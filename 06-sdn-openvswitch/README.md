# 06 · Open vSwitch 源码编译与 SDN 实验

在 Ubuntu 虚拟机上**从源码编译安装 Open vSwitch 2.14.1**，加载内核模块并拉起 OVS 三大守护进程，完成 SDN 交换机环境搭建；并在此基础上完成 **QoS 入口限速**与**端口镜像**实验。属"SDN 技术"课程实验 3.1 / 3.4。

## 环境

| 项 | 值 |
|----|----|
| 系统 | Ubuntu 18.04（hostname `ubuntu-C241`） |
| 内核 | 5.4.0-150-generic |
| OVS 版本 | 2.14.1（源码编译） |
| 已有 SDN 工具链 | Mininet、POX、OpenFlow reference switch、oftest、oflops |

实验 3.4 使用三台虚拟机：交换机 1（OVS，`192.168.61.142`）、主机 1（`192.168.61.141`）、主机 2（跳板）。

## 一、源码编译与守护进程

全程用 Bash 脚本驱动，**每一步自动截图留证**（ImageMagick `import`），共产出 19+ 张过程截图。

```bash
# 1. 获取源码
wget http://openvswitch.org/releases/openvswitch-2.14.1.tar.gz
tar -zxvf openvswitch-2.14.1.tar.gz

# 2. 配置（指定本机内核头文件）
./configure --with-linux=/lib/modules/$(uname -r)/build

# 3. 编译安装
make -j2
make install

# 4. 加载内核模块
insmod ./datapath/linux/openvswitch.ko

# 5. 初始化数据库
ovsdb-tool create conf.db vswitchd/vswitch.ovsschema

# 6. 拉起守护进程
ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock \
             --remote=db:Open_vSwitch,Open_vSwitch,manager_options \
             --private-key=db:Open_vSwitch,SSL,private_key \
             --certificate=db:Open_vSwitch,SSL,certificate \
             --bootstrap-ca-cert=db:Open_vSwitch,SSL,ca_cert \
             --pidfile --detach
ovs-vsctl --no-wait init
ovs-vswitchd --pidfile --detach
```

验证：

```bash
ovs-vsctl --version     # → ovs-vsctl (Open vSwitch) 2.14.1
ovs-vsctl show          # → DB Schema 8.2.0
ovs-vsctl list-br       # → 网桥列表
```

安装产物：`/usr/local/bin/ovs-vsctl`、`/usr/local/sbin/ovsdb-server`、`/usr/local/sbin/ovs-vswitchd`。

## 二、实验 3.4：QoS 设置

把交换机 1 的唯一物理网卡 `ens33` 挂到 `br0`，由 `br0` 承载 IP：

```bash
ovs-vsctl add-br br0
ovs-vsctl add-port br0 ens33
ifconfig ens33 0 up
ifconfig br0 192.168.61.142/24 up

# 交换机 1 作为 netperf 服务端
netserver -p 9991

# 主机 1 发起 UDP_STREAM 测试
netperf -t UDP_STREAM -H 192.168.61.142 -p 9991
```

在 `ens33` 上配置入口 policer，承诺速率 100 Mbit/s、突发 50 kbit：

```bash
ovs-vsctl set interface ens33 ingress_policing_rate=100000
ovs-vsctl set interface ens33 ingress_policing_burst=50000
```

实测结果：

| 场景 | 服务端接收速率 |
|------|----------------|
| 未设置 QoS | 682 / 673 Mbit/s |
| 设置 QoS 后 | 5.55 / 0 Mbit/s |

客户端仍按原速率发送，服务端实际接收速率骤降，说明超出承诺速率的报文已被 OVS 入口 policer 丢弃。

> **netperf 2.6.0 的坑**：`-P` 是"是否显示表头"的开关，不是端口；端口是小写 `-p`。指导书中的 `-P 9991` 并不会把测试发到 9991，服务端与客户端应统一使用 `-p`。

## 三、实验 3.4：端口镜像

```bash
BR=$(ovs-vsctl get port br0 _uuid)
EN=$(ovs-vsctl get port ens33 _uuid)

ovs-vsctl -- set bridge br0 mirrors=@m -- \
  --id=@m create mirror name=mymirror \
  select-dst-port=$EN select-src-port=$EN output-port=$BR

ovs-vsctl list mirror
```

镜像把 `ens33` 收发的全部报文复制到 `br0` 端口。命令正常返回 mirror UUID，`ovs-vsctl show` 中可见 `mirrors` 配置。

> **重要**：管理流量本身也经过 `ens33`，镜像生效后主机的管理连通性会立即消失（对端 ARP 全 INCOMPLETE），`clear bridge br0 mirrors` 也无法从远端救回。因此镜像与截图必须放在 **guest 本地的 `systemd-run` 脚本**里一次性完成；恢复用 `del-port br0 ens33` + `del-br br0` + `dhclient ens33`，或直接重启。

## 四、截图流水线

`scripts/lab34/` 是实验 3.4 的完整驱动代码：

1. `prep34.sh`：在 guest 的 `:0` 桌面关闭熄屏/锁屏，创建 `shot34` 截图命令并启动中文 xterm；
2. `drive34.py`：通过 SSH（可经跳板）向 xterm 注入命令、逐步 `import -window root` 截图，按 `env / enslave / qos / mirror` 分阶段执行；
3. `build_docx34.py`：把截图按模板的空段落槽位填成报告 DOCX，自动编号图题。

关键设计：

- 会断网的操作（`add-port`、`mirror`）全部封装为 guest 本地脚本，用 `systemd-run` 脱离 SSH 会话执行；
- 密码只从 `VMPASS` 环境变量读取，不落盘；
- 截图取回宿主机后逐张 `PIL.Image.open().load()` 校验，防止传输截断的 PNG 混入报告。

## 文件

| 文件 | 说明 |
|------|------|
| [`scripts/labshot.sh`](scripts/labshot.sh) | 实验 3.1 全流程重放 + 逐步截图脚本 |
| [`scripts/lab34/prep34.sh`](scripts/lab34/prep34.sh) | 实验 3.4 截图环境准备（X 授权、熄屏、xterm） |
| [`scripts/lab34/drive34.py`](scripts/lab34/drive34.py) | 实验 3.4 分阶段命令注入与截图驱动 |
| [`scripts/lab34/build_docx34.py`](scripts/lab34/build_docx34.py) | 把截图填入模板生成报告（身份信息已置空） |

> 打包说明：源码压缩包（约 5MB）、过程截图与报告文件未纳入仓库；如需可自行从 openvswitch.org 下载对应版本。
