# 网络工程实践集 · Network Labs

> 李承 · 求职意向：网络工程师 · 广东工商职业技术大学（信息工程技术，本科在读）

本仓库汇总我在课程实训中完成的网络工程项目，覆盖 **园区网规划、路由交换、广域互联、无线网络、虚拟化与存储、SDN** 等方向。所有拓扑均在华为 eNSP / VMware / Linux 环境中实际搭建并验证通过，配置均为可复现的真实设备命令。

## 项目索引

| # | 项目 | 技术关键词 | 实验环境 |
|---|------|-----------|---------|
| 01 | [企业园区网络规划与设计方案](01-campus-network-design/) | 三层架构、双核心冗余、双出口、VLAN 规划、国标综合布线 | 方案设计 |
| 02 | [基于 eNSP 的企业级网络综合组网](02-ensp-enterprise-network/) | OSPF/BFD、MSTP、VRRP、MPLS L3VPN、IPSec、IPv6、WLAN | eNSP，13 台设备 |
| 03 | [GRE over IPsec 企业广域安全互联](03-gre-over-ipsec-wan/) | GRE 隧道、IPsec ESP、IKE、OSPF over GRE | eNSP，6 台路由器 |
| 04 | [智能无线网络部署与安全配置](04-wireless-lan/) | AC+AP、CAPWAP、WPA2、MAC 白名单、SSID 隔离 | eNSP |
| 05 | [VMware 虚拟化与 RAID/LVM 存储实验](05-virtualization-storage/) | RAID10、LVM+XFS、LAMP、kodbox、LAN Segment | VMware，3 台 VM |
| 06 | [Open vSwitch 源码编译（SDN）](06-sdn-openvswitch/) | SDN、OpenFlow、源码编译、内核模块加载 | Ubuntu |
| 07 | [eNSP + VirtualBox 兼容性排障](07-ensp-vbox-troubleshooting/) | Windows 加固层、根因分析、开源协作 | Windows 11 |

## 关于本仓库

- **凭据已脱敏**：配置中的设备口令、IPsec 预共享密钥、虚拟机口令等均替换为 `__LAB_PASSWORD__`、`__PSK_xx__` 等占位符，不包含任何真实凭据。
- **`.topo` 文件**可用华为 eNSP 直接打开（需自行准备对应设备镜像）。
- 各项目目录下的 `README.md` 说明了项目背景、拓扑、用到的技术与关键配置片段。

## 技能覆盖

`VLAN` `STP/MSTP` `链路聚合` `OSPF` `BGP` `VRRP` `策略路由` `ACL` `NAT/PAT` `PPPoE` `GRE` `IPsec VPN` `MPLS L3VPN` `IS-IS` `IPv6/OSPFv3` `WLAN AC+AP` `CAPWAP` `DHCP Snooping` `端口安全` `SNMP` `SSH` `NQA` `Linux` `Windows Server` `VMware ESXi` `RAID10` `LVM` `Open vSwitch`
