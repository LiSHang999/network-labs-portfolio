# 02 · 基于 eNSP 的企业级网络综合组网（旗舰项目）

在华为 eNSP 中搭建的 **13 设备企业级网络**综合实训，覆盖交换、路由、运营商 MPLS、安全、IPv6、无线与接入安全。总部（Site A）与分支机构（Site B）通过运营商 MPLS L3VPN 互通，并以 IPsec VPN 作为备份链路。属"职业技能等级证书类综合实训"项目。

## 拓扑与设备清单

| 设备 | 型号 | 角色 |
|------|------|------|
| A_FW1 | USG6000V | 总部出口防火墙 / Site A CE |
| B_FW2 | USG6000V | 分支出口防火墙 / Site B CE / PPPoE 客户端 |
| A_SW1 / A_SW2 | S5700 | 总部核心交换机（MSTP 双根、VRRP 网关） |
| A_SW3 / A_SW4 | S3700 | 总部接入交换机 |
| B_SW1 | S3700 | 分支接入交换机 |
| PE1 / P / PE2 | AR2240 | 运营商 MPLS 骨干（P 兼 VPNv4 路由反射器） |
| ISP | AR2220 | 模拟互联网 / PPPoE 服务端 |
| B_R1 | AR2220 | 分支路由器 / DHCP 服务器 |
| AC1 | AC6005 | 无线控制器 |

## 技术要点（按域拆分）

### 交换部分

- **链路聚合**：A_SW1↔A_SW2 部署 Eth-Trunk（手动模式），提升核心间带宽与可靠性
- **MSTP 负载分担**：`instance 1 → VLAN10`、`instance 2 → VLAN20`，两台核心互为不同实例的根桥，实现流量负载分担
- **VRRP 网关冗余**：虚拟网关 `10.1.X.254`（X 为 VLAN ID），与 MSTP 实例配合实现网关侧负载分担
- **Trunk/VLAN**：VLAN10、VLAN20、VLAN254 贯穿四台交换机

### 路由部分（Site A）

- OSPF **区域 0 + 区域 1**；区域 0 启用 **MD5 认证**（接口方式），并启用 **BFD** 快速检测链路故障
- A_SW1/A_SW2 的 VLANIF254 部署 **Virtual-Link** 作为区域间备份
- A_FW1、A_SW1、A_SW2 加入区域 0；下行接口（VLANIF10/20）不建立 OSPF 邻居

### 运营商网络（MPLS）

- PE1/P/PE2 部署 **IS-IS Level-2**（区域 49.0000）+ **LDP**
- **MPLS L3VPN**：VRF `SiteA`（RD 100:1）/ `SiteB`（RD 100:2），VPNv4 路由由 **P 节点作路由反射器**
- A_FW1、B_FW2 作为 **CE** 与 PE 建立 **eBGP** 邻居（运营商 AS 100，总部与分支同属 AS 65000）

### 安全部分

- **IPsec VPN**（总部↔分支）作为 MPLS VPN 的**备份链路**：MPLS 故障时 IPsec 生效
  - IKE：3DES + 预共享密钥 + SHA1 + DH Group2
  - IPsec：**隧道模式**，3DES + SHA1，保护源目 `10.1.x.x/24`
- **NAT**：总部用户访问外网用地址池 `119.1.1.11–119.1.1.20`；分支用 **Easy-IP**；总部访问内网服务器用公网地址 `119.1.1.100`；外网用户可访问内网 WEB 服务（NAT Server）
- **NQA**：检测 `151.1.4.1` 不可达则停止向 内网下发缺省路由

### IPv6 部分

- 运营商 AS100 内互联地址用 **Link-Local**；PE1/P/PE2 的 Lo0 为 `2001:100:1:x::x/128`，启用 **IS-ISv6** 并实现 v4/v6 拓扑分离
- A_FW1、A_SW1、A_SW2 部署 **OSPFv3** 区域 0（互联用 Link-Local，加载 Loopback0）
- A_FW1↔B_FW2 经 MPLS VPN 建立 **6to4 隧道**，在其上部署 **BGP4+** 实现总部与分支 IPv6 互通
- B_R1 用**有状态 DHCPv6** 下发地址与 DNS（`2001:10:1:9::9`）

### 无线部分（AC6005）

- SSID `HUAWEI`，安全策略 **WPA2-PSK AES**，**直接转发**模式
- 业务 VLAN10；AP 与 STA 地址由**防火墙上的 DHCP 地址池**动态分配

### 接入安全与运维

- **DHCP Snooping**：防止 DHCP 欺骗与饥饿攻击
- **端口安全**：接口自动学习 MAC（sticky），限制最大 MAC 数
- **端口隔离**：同 VLAN 内 PC 之间不能互访
- **PPPoE**：B_FW2 作客户端（Dialer1，CHAP），ISP 作服务端（Virtual-Template）
- **SNMPv2c**：A_SW1 配置 MIB 查看范围，接口 up/down 主动发送 trap
- **SSH**：ISP 支持远程 SSH 登录
- **DHCP Relay**：核心交换机上部署

## 文件

| 文件 | 说明 |
|------|------|
| [`configs/all-devices-config.txt`](configs/all-devices-config.txt) | 13 台设备完整配置命令（1400+ 行） |
| [`topology/project6.topo`](topology/project6.topo) | eNSP 拓扑文件 |
| [`topology/topology.png`](topology/topology.png) | 拓扑示意图 |

> 注：设备口令已替换为 `__LAB_PASSWORD__`，IPsec 预共享密钥同理已脱敏。
