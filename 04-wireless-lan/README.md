# 04 · 智能无线网络部署与安全配置

基于华为 eNSP 的两组 WLAN 实训：**办公区无线网络安全配置**（访客/办公 SSID 隔离 + MAC 白名单）与**酒店智能无线网络部署**（多楼层覆盖 + 隧道转发）。属"无线网络技术"课程实训。

## 一、办公区无线网络安全配置

### 拓扑与地址规划

| 设备 | 型号 | 说明 |
|------|------|------|
| AC | 无线控制器 | CAPWAP 源接口 LoopBack0 `1.1.1.1/32` |
| AP1 / AP2 | AP7050DN | 绑定真实 eNSP MAC 上线 |
| 接入交换机 | — | Trunk GE0/0/1-2，pvid 99 |

| VLAN | 名称 | 网段 |
|------|------|------|
| VLAN10 | guest | 192.168.10.0/24 |
| VLAN20 | office | 192.168.20.0/24 |
| VLAN99 | AP-Guanli（AP 管理） | 192.168.99.0/24 |

### 关键配置

**AP 自动发现**——通过 DHCP Option 43 下发 AC 地址：

```
dhcp server option 43 sub-option 3 ascii 1.1.1.1
```

**双 SSID 差异化策略**：

| SSID | 安全策略 | 说明 |
|------|---------|------|
| `guest` | Open（开放） | 访客网络，独立 VLAN 隔离 |
| `office` | WPA2-PSK AES + SSID 隐藏 | 办公网络，叠加 STA MAC 白名单 |

```
security wpa2 psk pass-phrase __WLAN_PSK__ aes
ssid-hide enable
sta-whitelist-profile name BGS-WL
 sta-mac 5489-981b-7b4a
```

**集中管理**：用 `ap-group` 与 VAP 模板统一管理两台 AP 的多个射频，guest 走 wlan1、office 走 wlan2。

### 验证

`display ap all`（AP 上线状态）、`display vap all`（VAP 生效）、`display station all`（终端接入）。

## 二、酒店智能无线网络部署

多楼层覆盖场景，接入交换机（S5700）上规划了更细的 VLAN 划分：

| VLAN | 用途 |
|------|------|
| VLAN10 | User-Wifi-1F（一层无线用户） |
| VLAN20 | User-Wifi-2F（二层无线用户） |
| VLAN30 | User-Wire（有线用户） |
| VLAN99 | AP-Guanli（AP 管理） |
| VLAN100 | SW-Guanli（交换机管理） |

连 AP 的端口配置 `port trunk pvid vlan 99`，管理流量与业务流量隔离；连 AC 的端口放行全部业务 VLAN。

## 文件

| 文件 | 说明 |
|------|------|
| [`configs/office-wlan-ac-config.txt`](configs/office-wlan-ac-config.txt) | 办公区 AC 完整配置（可直接粘贴） |
| [`configs/hotel-wlan-config.txt`](configs/hotel-wlan-config.txt) | 酒店 WLAN 完整配置（交换机 + AC + AP） |
| [`topology/office-wlan.topo`](topology/office-wlan.topo) | 办公区拓扑 |
| [`topology/hotel-wlan.topo`](topology/hotel-wlan.topo) | 酒店拓扑 |

> 注：WPA2 预共享密钥已替换为 `__WLAN_PSK__`，设备口令替换为 `__LAB_PASSWORD__`。
