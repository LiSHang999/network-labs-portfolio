# 07 · eNSP + VirtualBox 兼容性排障（开源协作）

针对开源项目 [`LBXaaa/ensp-vbox-shim`](https://github.com/LBXaaa/ensp-vbox-shim) 的一个兼容性缺陷，独立完成复现、根因定位、持续跟进，并与维护者协作。**排错结论被维护者采纳，纳入项目官方排错文档。**

> 相关 issue：https://github.com/LBXaaa/ensp-vbox-shim/issues/8

## 问题背景

eNSP 依赖 VirtualBox 运行设备镜像。在 **Windows 11 25H2（build 26200.9168 及之后的 9457）** 上，拖动 AR 设备启动时持续报 **「错误 40，设备启动失败」**。

## 定位过程

### 1. 隔离变量：问题不在 eNSP，也不在 shim

**关键一步**是绕过 eNSP 与打补丁层，直接用 VirtualBox 命令启动同一下层虚拟机：

```powershell
VBoxManage.exe startvm AR_Base --type headless
# → exit code 1，报错一致
```

这说明问题出在 **VirtualBox 加固层（hardening）本身**，与 eNSP 和 shim 无关。

### 2. 读日志锚定根因

`VBoxHardening.log` 末尾：

```
Error -104 in supR3HardenedWinReSpawn! (enmWhat=5)
Error relaunching VirtualBox VM process: 5   (ERROR_ACCESS_DENIED)
```

用三条判别规则锁定根因（绕开 eNSP 也失败 / 锚点是 `-104` 而非 `-5657` / 日志里没有被拒模块），判定为加固层在自己的重生成链里被拒绝访问。

### 3. 完整复现数据

提交了含**环境矩阵**的结构化报告：Windows build 号、`ntdll/kernel32/KernelBase` 文件版本、KB 补丁清单、VirtualBox 版本（7.2.8 与 7.2.18 均复现）、shim 版本，以及复现步骤与日志。

### 4. 跟进复发 + 逐项排除

问题在 9 月累积更新后一度"自愈"，但**同一 build 上再次复发**。据此提交复发报告，逐项排除下列假设：

| 假设 | 核查结果 |
|------|---------|
| 安全软件（火绒）拦截 | 驱动日志中**无任何 VBox 拦截记录**，且修复态下火绒同样在场 → 排除 |
| 智能应用控制 / VBS / 内存完整性 | 均处于关闭状态 → 排除 |
| 360 / 腾讯安全 | 实为卸载残留注册项，无驱动在跑 → 排除 |

结论：该故障**不是版本决定性的**，而是偶发/复发型。

### 5. 附带成果：降级后遗症的修复方法

排查中还定位并修复了三个由 VirtualBox 降级操作遗留的问题，一并记录（对遇到同类报错的人有用）：

| 报错 | 原因 | 修复 |
|------|------|------|
| `NtCreateFile(\Device\VBoxDrvStub) → STATUS_OBJECT_NAME_NOT_FOUND` | VBoxSup 内核驱动服务注册项被删 | `VBoxDrvInst.exe install --inf-file drivers\vboxsup\VBoxSup.inf` + `sc start vboxsup` |
| `Could not find Host Interface Networking driver!` | VBoxNetAdp6 的 PnP INF 丢失 | `VBoxDrvInst.exe install --inf-file drivers\network\netadp6\VBoxNetAdp6.inf` |
| `Nonexistent host networking interface 'VirtualBox Host-Only Ethernet Adapter'` | 宿主机 host-only 网卡缺失 | `VBoxManage hostonlyif create` |

## 结果

维护者公开回复：

> 感谢把环境数据和后续验证都记录得这么完整 —— 那三个降级后遗症的报错与修法一并留下了，**对后来遇到同样问题的人很有用，我会总结归纳进排错文档的**

## 文件

| 文件 | 说明 |
|------|------|
| [`drafts/issue-to-shim-author.md`](drafts/issue-to-shim-author.md) | 首次提交的缺陷报告 |
| [`drafts/report-to-author-v020-recurrence.md`](drafts/report-to-author-v020-recurrence.md) | 复发报告（含逐项排除） |
| [`scripts/`](scripts/) | 诊断与修复用 PowerShell / Python 脚本 |
| [`scripts/SUPR3HardenedMain-win.cpp`](scripts/SUPR3HardenedMain-win.cpp) | VirtualBox 加固层入口源码（比对分析用） |

> 注：诊断脚本中的系统口令等已脱敏；VirtualBox 安装包等大文件未纳入仓库。
