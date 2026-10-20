# 08 · VMware ESXi 企业级虚拟化平台

在 VMware Workstation 中嵌套部署 **两台 ESXi 8.0 主机 + VCSA 8.0**，配合独立的 iSCSI 存储服务器，完成虚拟网络、共享存储、vCenter 集中管理与 vMotion 热迁移。属"虚拟化技术"综合实训项目 2。

## 环境架构

| 节点 | 地址 | 角色 |
|------|------|------|
| ESXi1 | `192.168.61.143` | 虚拟化主机 1（管理 `vmk0`，存储 `vmk1=192.168.50.10`） |
| ESXi2 | `192.168.61.20` | 虚拟化主机 2（管理 `vmk0`，存储 `vmk1=192.168.50.20`） |
| VCSA | `192.168.61.60` | vCenter Server 8.0（tiny 规格，SSO 域 `vsphere.local`） |
| store | `192.168.61.50` / `192.168.50.50` | iSCSI target（CentOS 8 + targetcli） |
| centos6.5 | `192.168.61.30` / `192.168.100.30` | 业务虚拟机（CentOS 6.5） |
| file | `192.168.61.40` / `192.168.100.40` | 由 centos6.5 克隆的业务虚拟机 |

**三张网络**：

```
管理网  192.168.61.0/24   VMnet8(NAT)，网关 .2        —— ESXi/vCenter 管理
数据网  192.168.100.0/24  VMnet1(仅主机)              —— 跨主机业务虚拟机互通
存储网  192.168.50.0/24   VMnet2(仅主机，关闭 DHCP)   —— ESXi vmk1 ↔ store
```

> 指导书使用 `192.168.200.0/24` 作为管理网。本机 VMnet8 实际为 `192.168.61.0/24`，因此只替换网段、保留各节点主机位（`.20/.30/.40/.50/.60`），ESXi1 因已有环境占用而使用 `.143`。

## 实验内容

### 1. 部署 ESXi 8.0

在 Workstation 中开启 VT-x/EPT 后安装 ESXi，DCUI 配置管理地址，浏览器登录 Host Client。两台主机均使用静态管理地址。

### 2. 虚拟化网络

每台 ESXi 建立两组标准交换机：

| vSwitch | 上行链路 | 端口组 | 用途 |
|---------|----------|--------|------|
| `sw-data` | `vmnic1` | `data` | 业务虚拟机跨主机通信（192.168.100.0/24） |
| `sw-store` | `vmnic2` | `store` | iSCSI 存储流量，承载 `vmk1` |

`vmk1` 在各自主机上配置为 `192.168.50.10 / .20`，与 store 的存储网卡同网段。`scripts/esxi/net_setup.py` 以幂等方式创建 vSwitch、端口组和 vmk1。

### 3. iSCSI 共享存储

store 上使用 targetcli 创建后端块设备、LUN 与 ACL；两台 ESXi 添加软件 iSCSI 适配器并发现目标。LUN 先用 `partedUtil` 将分区类型改为 `0xfb`，再用 `vmkfstools` 创建 VMFS6，最终两台主机同时挂载同一个 `iscsi-datastore`——这是 vMotion 的前提。

### 4. vCenter 与 vMotion

VCSA 8.0 以 tiny 规格部署在 ESXi1，创建 Datacenter 后添加两台主机，在 `vmk0` 上启用 vMotion。`file` 虚拟机在开机状态下从 ESXi1 热迁移到 ESXi2，实测约 4 秒，迁移后业务仍可 ping 通。

## 遇到的问题

**克隆 ESXi 主机带来的身份冲突。** 为节省时间，ESXi2 由已装好的 ESXi1 克隆而来，结果继承了相同的 `vmk0` MAC 地址和相同的本地 VMFS UUID。vCenter 添加 ESXi2 时报 `NoHost` / `ConflictingDatastoreFound`。处理方式：

1. 用 pyVmomi 的 `UpdateVirtualNic` 将 ESXi2 的 `vmk0` MAC 改为 `00:50:56:61:20:01`；
2. 把虚拟机迁到共享的 `iscsi-datastore`，移除虚拟机对本地数据存储的引用，并从 ESXi1 清单移除冲突的本地数据存储；
3. 之后 `AddStandaloneHost_Task` 成功，两台主机均为 connected。

> 复盘结论：克隆 ESXi 前应先隔离 system UUID、管理网卡 MAC、VMFS UUID 三类身份字段；该故障排查耗时已超过重装一台 ESXi 的时间。

**CentOS 6.5 自动化安装。** 自制的 kickstart ISO 中，anaconda 从 `cdrom:`/`file:` 读取 `ks.cfg` 时静默解析到 0 条指令；改为在 ESXi 上用自带 python3 起 HTTP 服务、以 `ks=http://…/ks.cfg` 引导后成功。另有 ESXi 拒绝 VMX 中 `guestOS = "otherLinuxGuest"` 的虚拟机开机，改为 `centos6_64Guest` 后正常。

## 验证

```bash
# 主机连通性
ping 192.168.61.143     # ESXi1
ping 192.168.61.20      # ESXi2
ping 192.168.61.60      # vCenter

# 共享存储（ESXi 上）
esxcli storage filesystem list          # 两台主机均可见 iscsi-datastore
esxcli iscsi session list
```

vCenter 中两台主机 `connectionState = connected`，`file` 虚拟机迁移后运行于 ESXi2。

## 文件

| 文件 | 说明 |
|------|------|
| `scripts/esxi/p2.py` | pyVmomi 公共工具：连接、对象查找、任务等待、电源/设备操作 |
| `scripts/esxi/esh.py` | ESXi SSH 命令执行封装 |
| `scripts/esxi/net_setup.py` | 幂等创建 `sw-data` / `sw-store`、端口组与 `vmk1` |
| `scripts/esxi/create_db.py` | 在 ESXi2 上创建 database 虚拟机（含串口） |
| `scripts/esxi/clone_file.py` | 克隆 centos6.5 → file，改串口、移除光驱 |
| `scripts/esxi/prep_store.py` | 为 store 虚拟机添加存储网卡、VNC 与 100G 数据盘 |
| `scripts/esxi/vc_addhost.py` | 带证书指纹把 ESXi 主机加入 vCenter 并巡检 |
| `scripts/centos65/build_auto_iso.py` | 用 pycdlib 把 ks.cfg 写入 CentOS 6.5 ISO |
| `scripts/centos65/create_vm.py` | 在 ESXi 上手工生成 VMX、注册并开机 |
| `scripts/centos65/ks_esxi_server.py` | ESXi 上的最小 HTTP 服务，供 anaconda 拉取 ks.cfg |
| `scripts/centos65/add_serial.py` | 用 SOAP 直接调用 ReconfigVM_Task 添加网络串口 |
| `configs/ks.cfg` | CentOS 6.5 kickstart 模板 |
| `configs/isolinux-http.cfg` | 从 HTTP 拉取 kickstart 的 isolinux 配置 |
| `configs/vcsa_install.template.json` | VCSA 8.0 静默部署模板 |

> **凭据说明**：仓库中的密码一律改为环境变量或占位符（`ESXI_PASS`、`VCSA_SSO_PASS`、`ESXI_THUMBPRINT`、`KS_ROOT_PASSWORD`、`VNC_PASS`），不含任何真实口令。
> 报告 DOCX/PDF 与过程截图未纳入仓库。
