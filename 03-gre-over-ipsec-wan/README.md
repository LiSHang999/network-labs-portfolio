# 03 · GRE over IPsec 企业广域安全互联

在华为 eNSP 中搭建的 Hub-and-Spoke 企业广域互联：总部与两地分支机构通过 GRE 隧道承载内网路由，再由 IPsec 对 GRE 流量加密，实现跨公网的安全内网互通。属"广域互联技术"课程实训。

## 拓扑

```
        AR4 ──── AR5 ──── AR6          ← 模拟 ISP 骨干（OSPF 100）
         │        │        │
    AR2-SH     AR1-HQ    AR3-GZ
   （上海分支） （北京总部） （广州分支）
      Spoke       Hub        Spoke
```

| 设备 | 角色 | 隧道地址 |
|------|------|---------|
| AR1-HQ | 总部（Hub） | 10.255.12.1 / 10.255.13.1 |
| AR2-SH | 上海分支（Spoke） | 10.255.12.2 |
| AR3-GZ | 广州分支（Spoke） | 10.255.13.2 |
| AR4 / AR5 / AR6 | 模拟 ISP 骨干 | — |

业务网段：总部 192.168.10.0/24、上海 192.168.20.0/24、广州 192.168.30.0/24。

## 技术要点

### 1. GRE 隧道（Tunnel 接口）

总部到两个分支各建一条 GRE 隧道，手工指定隧道源/目的与 `gre key` 做隧道标识：

```
interface Tunnel0/0/0
 ip address 10.255.12.1 255.255.255.252
 tunnel-protocol gre
 source 203.0.113.1          # 总部公网地址
 destination 198.51.100.1    # 上海分支公网地址
 gre key 120
```

### 2. IPsec 保护 GRE（ESP 传输模式）

**设计要点**：GRE 先封装，IPsec 用 **传输模式**（transport）保护 GRE 报文本身（协议号 47），而不是再套一层隧道模式。ACL 只放行 GRE 流量，避免把非隧道流量误加密：

```
acl number 3100
 rule 5 permit gre source 203.0.113.1 0 destination 198.51.100.1 0

ipsec proposal GRE-TRANS
 encapsulation-mode transport          # 传输模式，保护 GRE
 esp authentication-algorithm sha1
 esp encryption-algorithm aes-128

ike proposal 10
 authentication-method pre-share
 encryption-algorithm aes-cbc-128
 dh group2
```

### 3. 企业 OSPF 跑在 GRE 之上

隧道建立后，在 OSPF 区域 0 中发布隧道网段与业务网段，实现三站点到点动态互通。外层 ISP 骨干用独立的 OSPF 100，做到内外路由分离。

## 验证过程

按"逐层验证"推进，确认每一层都通再上下一层：

1. **底层连通**：公网地址互 ping
2. **隧道连通**：Tunnel 接口地址互 ping
3. **路由邻居**：`display ospf peer brief`，确认 2 个邻居达到 Full
4. **加密状态**：`display ike sa`、`display ipsec sa`，确认 SA 已建立
5. **业务连通**：三站点业务网段互 ping
6. **封装对比**：抓包对比部署前后，从 `gre(47)` 变为 `esp(50)`

## 文件

| 文件 | 说明 |
|------|------|
| [`configs/all-devices-config.txt`](configs/all-devices-config.txt) | 6 台路由器完整配置 + PC 地址 + 验证命令 |
| [`topology/gre-over-ipsec.topo`](topology/gre-over-ipsec.topo) | eNSP 拓扑文件 |

> 注：配置中的预共享密钥已替换为 `__PSK_SH__` / `__PSK_GZ__` 占位符。
