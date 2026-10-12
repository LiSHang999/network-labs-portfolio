# 06 · Open vSwitch 源码编译与 SDN 环境搭建

在 Ubuntu 虚拟机上**从源码编译安装 Open vSwitch 2.14.1**，加载内核模块并拉起 OVS 三大守护进程，完成 SDN 交换机环境搭建。属"SDN 实验 3.1"课程实训。

## 环境

| 项 | 值 |
|----|----|
| 系统 | Ubuntu（hostname `ubuntu-C241`） |
| 内核 | 5.4.0-150-generic |
| OVS 版本 | 2.14.1（源码编译） |
| 已有 SDN 工具链 | Mininet、POX、OpenFlow reference switch、oftest、oflops |

## 执行步骤

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

## 验证

```bash
ovs-vsctl --version     # → ovs-vsctl (Open vSwitch) 2.14.1
ovs-vsctl show          # → DB Schema 8.2.0
ovs-vsctl list-br       # → 网桥列表
```

安装产物：`/usr/local/bin/ovs-vsctl`、`/usr/local/sbin/ovsdb-server`、`/usr/local/sbin/ovs-vswitchd`。

## 文件

| 文件 | 说明 |
|------|------|
| [`scripts/labshot.sh`](scripts/labshot.sh) | 实验全流程重放 + 逐步截图脚本 |

> 打包说明：源码压缩包（约 5MB）与 40+ 张过程截图未纳入仓库；如需可自行从 openvswitch.org 下载对应版本。
