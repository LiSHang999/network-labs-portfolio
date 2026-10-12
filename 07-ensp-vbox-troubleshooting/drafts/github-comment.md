感谢回复，你要的三项环境信息如下，同时带来一个**决定性结论**：

## ✅ 结论：升级到 build 26200.9457 后，问题已自愈

2026-09-17 安装 KB5129195 + KB5124007 后，build 从 **26200.9168 → 26200.9457**，ntdll/kernel32/KernelBase 从 **10.0.26100.8972 → 10.0.26100.9278**。升级后 `CreateProcessW` 的 ERROR_ACCESS_DENIED **不再出现**，VBox 加固层能正常生成 VM 子进程了。

所以根因确认就是你判断的方向：**8 月的 KB5123304/KB5121003（build 26200.9168）引入的硬化层 CreateProcessW 被拒问题，被 9 月的 KB 更新（26200.9457）修复了。** 不需要 shim 绕过、不需要 Oracle 出新版。

---

## 你要的三项环境信息

### 1. winver 完整版本号
- Windows 11 专业版 25H2，内部版本 **26200.9168**（升级前）→ **26200.9457**（升级后）
- 注册表 ProductName 显示 "Windows 10 Pro"，是升级遗留，实际为 Win11 25H2

### 2. ntdll / kernel32 / KernelBase 文件版本
| 文件 | 升级前 | 升级后 |
|---|---|---|
| ntdll.dll | 10.0.26100.8972 | **10.0.26100.9278** |
| kernel32.dll | 10.0.26100.8972 | **10.0.26100.9278** |
| KernelBase.dll | 10.0.26100.8972 | **10.0.26100.9278** |

### 3. Get-HotFix（最近几条）
| HotFixID | InstalledOn | Description |
|---|---|---|
| KB5129195 | 2026-09-17 | Security Update |
| KB5124007 | 2026-09-17 | Security Update |
| KB5123304 | 2026-08-12 | Security Update |
| KB5100998 | 2026-07-19 | Update |
| KB5054156 | 2026-07-19 | Update |
| KB5126052 | — | Update (.NET) |

---

## 附：升级后还踩了三个「我自己搞出来的」坑（与 shim/硬化无关，供他人参考）

升级后 VM 启动确实通了，但中间还报了三个错，全是我之前折腾降级（7.2.18→7.2.8 失败）留下的后遗症，已逐一修好：

1. **`NtCreateFile(\Device\VBoxDrvStub) → STATUS_OBJECT_NAME_NOT_FOUND`** → VBoxSup 内核驱动服务丢失（降级卸载时被删了注册项）。
   修法：`VBoxDrvInst.exe install --inf-file drivers\vboxsup\VBoxSup.inf` + `sc start vboxsup`。
2. **`Could not find Host Interface Networking driver! Please reinstall`** → VBoxNetAdp6 的 PnP INF 丢了。
   修法：`VBoxDrvInst.exe install --inf-file drivers\network\netadp6\VBoxNetAdp6.inf`。
3. **`Nonexistent host networking interface 'VirtualBox Host-Only Ethernet Adapter'`** → 宿主机 host-only 网卡没了。
   修法：`VBoxManage hostonlyif create`。

修完这仨后 `VBoxManage startvm AR_Base --type headless` 直接成功，eNSP 拖设备启动也已跑通。**顺带确认：shim v0.1.4-beta 与 VBox 7.2.18 兼容，无需降回 7.2.8。**

---

再次感谢你的排查和 shim 工作。结论：问题已随 9 月系统更新自愈，无需 shim 侧改动。
