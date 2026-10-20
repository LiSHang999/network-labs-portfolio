# 09 · 仓储中心无线网络性能优化

基于双 AC 热备的仓储无线网络，从**信道与带宽、发射功率、速率集、用户限速**四个方面做性能优化。属"无线网络技术"项目 7，拓扑与高可用配置沿用项目 6（医院双 AC 热备）。

## 拓扑

```
   AP1 GX-AP7050DN-1 (G0/0/0) ──┐
                                 ├── L2SW (S5700) ── G0/0/24 ══ G0/0/1 L3SW (S5700)
   AP2 GX-AP7050DN-2 (G0/0/0) ──┘                        │
                                                          ├── G0/0/24 ── AC1 (AC6005)
                                                          └── G0/0/23 ── AC2 (AC6005)
```

- AP 通过 trunk 接入 L2SW，管理 VLAN 99 由 L3SW 的 DHCP 下发；
- L3SW 同时是无线用户网关（VLAN 10）和 AP 管理网关（VLAN 99）；
- AC1/AC2 通过 VLAN 100 互联，运行 `ac protect` + HSB，AC1 为主（priority 0）、AC2 为备；
- 业务转发为 **tunnel 模式**，VAP 直接引用流量模板。

## VLAN / IP 规划

| VLAN | 名称 | 网段 | 说明 |
|------|------|------|------|
| 10 | User-Wifi | `192.168.10.0/24` | 无线用户，SSID `Warehouse`，网关 `.254` |
| 99 | AP-Guanli | `192.168.99.0/24` | AP 管理 / CAPWAP 源，AC1 `.1`、AC2 `.2` |
| 100 | Link-AC | `192.168.100.0/24` | L3SW 与双 AC 互联、HSB 通道 |
| 200 | SW-Guanli | `192.168.200.0/24` | 交换机管理，L3SW `.254`、L2SW `.2` |

## 优化内容

| 任务 | 项目 | 关键配置 |
|------|------|----------|
| 7-1 | 关闭自动调优，手工固定信道与带宽 | `calibrate auto-channel-select disable`；AP1 `channel 40mhz-minus 1` / `channel 80mhz 36`，AP2 `channel 40mhz-minus 11` / `channel 80mhz 52` |
| 7-2 | 关闭功率自动调优，固定发射功率 | `calibrate auto-txpower-select disable`；四张射频卡 `eirp 20`（20 dBm） |
| 7-3 | 裁剪低速率集，提升频谱效率 | 2.4G `dot11bg supported-rate 6 9 11`；5G `dot11a supported-rate 12 18` |
| 7-4 | 按终端限速，防止单用户占满空口 | `traffic-profile Warehouse-traffic`：`rate-limit client down 8000`、`up 8000`（kbit/s） |

设计要点：

- **信道错开**：2.4G 使用 1 / 11 两个非重叠信道；5G 使用 36 / 52，覆盖不同的 UNII 频段，降低同频干扰。
- **带宽分层**：2.4G 用 40 MHz 兼顾覆盖与兼容性，5G 用 80 MHz 提升峰值速率。
- **速率集**：关闭 1/2/5.5/11 Mbps 等低速率的"拖尾效应"，避免低速终端拉低整张射频卡的 airtime 效率。
- **限速位置**：限速模板挂在 VAP 上，对每个无线终端分别生效，而不是对整条 CAPWAP 隧道限速。

## 验证命令

```bash
# 信道与带宽（4 张射频卡应分别为 1/40M、36/80M、11/40M、52/80M）
display radio all

# AP 功率（Config EIRP 应为 20）
display ap config-info ap-id 1

# 速率集
display radio-2g-profile name Warehouse-2g     # 802.11bg support rate: 6 9 11
display radio-5g-profile name Warehouse-5g     # 802.11a  support rate: 12 18

# 用户限速（上下行均 8000 Kbps）
display traffic-profile name Warehouse-traffic

# 整体 WLAN 配置
display current-configuration configuration wlan-view
```

## 文件

| 文件 | 说明 |
|------|------|
| `configs/L2SW.txt` | 接入交换机：VLAN、trunk、管理地址 |
| `configs/L3SW.txt` | 核心交换机：VLANIF、DHCP、AC 互联路由 |
| `configs/AC1.txt` | AC1 全量配置：WLAN 模板、AP 组、双机热备 |
| `configs/AC2.txt` | AC2 全量配置（与 AC1 对称） |
| `configs/AC1-increment.txt` | AC1 上项目 7 的增量优化命令 |
| `configs/AC2-increment.txt` | AC2 上项目 7 的增量优化命令 |
| `configs/all-devices-full.txt` | 从空配置开始的全部设备命令 + 规划表 + 避坑说明 |

> **说明**
> 1. 仓库中的 Telnet 口令统一替换为 `__TELNET_PASSWORD__`，粘贴前请自行替换。
> 2. AP 的 MAC（`c4b8-b469-3a40` / `c4b8-b469-33e0`）取自规划表；eNSP 每次新建或重启 AP 后 MAC 可能变化，粘贴前需用 `display ap all` 核对并替换。
> 3. 报告 DOCX/PDF、PPT 与过程截图未纳入仓库。
