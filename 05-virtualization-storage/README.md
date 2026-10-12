# 05 · VMware 虚拟化与 RAID/LVM 存储实验

在 VMware Workstation 上搭建的 3 台 Linux 虚拟机环境，完成**虚拟网络规划、软件 RAID、LVM 逻辑卷、LAMP 应用栈与私有网盘部署**，全程由宿主机通过 `vmrun` 与 PowerShell/Python 脚本自动化驱动。属"虚拟化与存储技术"课程实训。

## 环境架构

| 虚拟机 | 系统 | 网络 | 角色 |
|--------|------|------|------|
| web | Rocky/CentOS 8 | NAT + 私网 | LAMP + kodbox 网盘 |
| file | Rocky/CentOS 8 | NAT + 私网 | 文件服务（LVM） |
| database | Rocky/CentOS 8 | 仅私网 | 数据库（RAID10） |

**双网络设计**：

- **VMnet8 (NAT)** `192.168.61.0/24` —— 提供外网访问（需要联网的 VM 使用）
- **私有 LAN Segment (pvn)** `192.168.56.0/24` —— 三台 VM 的隔离内网，database 仅接此网，**故意不给外网**

> database 不接外网是有意设计：验证内网隔离 + 存储节点无需公网。

## 存储部分（核心）

### 数据库节点：软件 RAID10 → LVM → XFS

```
4 × 5GB NVMe 物理盘
   └─ mdadm RAID10 (metadata 1.2, near=2, chunk 512K)
        └─ LVM: vg_data / lv_data (9GB)
             └─ XFS 文件系统，挂载 /data
```

阵列可用容量 9.99 GiB，实测容量与预期一致（4 盘 RAID10 取一半）。

### 文件节点：LVM → XFS

```
1 × 20GB NVMe 盘
   └─ LVM: vg_file / lv_file (20GB, 100%FREE)
        └─ XFS，挂载 /file
```

两处均用 `mdadm -D`、`lsblk`、`df -hT` 核验，并做了实际写入测试。

## 应用部分

在 web 节点部署 **LAMP** 与私有网盘：

| 组件 | 版本 |
|------|------|
| Apache httpd | 2.4.37 |
| PHP | 7.2.24（php-fpm 模式） |
| MariaDB | 10.3.28 |
| kodbox | 1.69 |

kodbox 依赖的 PHP 扩展（curl / gd / json / mbstring / mysqli / pdo_mysql / SimpleXML / xml / zip）逐项核验，建库（utf8mb4）并完成部署。

## 网络连通性验证

- 三台 VM 私网 `192.168.56.x` 互 ping 全部通过
- database 无法访问外网（符合设计），web / file 可访问外网
- 三台 VM 的 sshd 均监听 `0.0.0.0:22`

## 自动化方式

从 Windows 宿主机通过 `vmrun` 驱动 Guest 操作（PowerShell + Python），包括：创建虚拟磁盘、编辑 `.vmx` 添加网卡、配置 Guest 内存储与网络、部署应用、回传验证结果。

## 文件

| 文件 | 说明 |
|------|------|
| [`scripts/db-raid.sh`](scripts/db-raid.sh) | database 节点 RAID10 + LVM + XFS 配置 |
| [`scripts/file-lvm.sh`](scripts/file-lvm.sh) | file 节点 LVM + XFS 配置 |
| [`scripts/create-disks.ps1`](scripts/create-disks.ps1) | 宿主机创建虚拟磁盘 |
| [`scripts/edit-vmx.ps1`](scripts/edit-vmx.ps1) | 编辑 `.vmx` 添加网卡（vmxnet3 / NAT / pvn） |
| [`scripts/web-lamp.sh`](scripts/web-lamp.sh) | LAMP 环境部署 |
| [`scripts/kod-deploy.sh`](scripts/kod-deploy.sh) | kodbox 网盘部署 |
| [`scripts/guest-netcheck.ps1`](scripts/guest-netcheck.ps1) | 跨 VM 连通性验证 |

> 注：脚本中的虚拟机口令已替换为 `__VM_ROOT_PASSWORD__`，运行时需自行注入。
