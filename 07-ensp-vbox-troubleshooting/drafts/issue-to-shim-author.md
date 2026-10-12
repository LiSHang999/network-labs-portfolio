# [BUG] Win11 25H2 build 26200.9168 上 VBox 加固层 CreateProcessW 失败（错误 40，设备启动失败）

> English one-liner: VirtualBox hardening loader fails at `CreateProcessW` (ERROR_ACCESS_DENIED) when spawning the VM process, on Windows 11 25H2 build 26200.9168 / ntdll 26100.8972. Reproduces on both VBox 7.2.8 and 7.2.18, with shim v0.1.4-beta. This build is newer than your tested 26200.8457.

## 环境

| 项 | 值 |
|---|---|
| 系统 | Windows 11 专业版 25H2，build **26200.9168** |
| ntdll / kernel32 / KernelBase | **10.0.26100.8972**（8 月更新后） |
| 相关 KB | KB5123304（8-12）+ KB5121003（8-20）Security Update |
| VirtualBox | 7.2.8r173730（也试过 **7.2.18r175117**，同样复现） |
| shim | ensp-vbox-shim **v0.1.4-beta** |
| Hyper-V / WSL | 均未启用 |
| 设备 | AR_Base（AR2220 类） |

## 现象

- eNSP 拖 AR 设备启动报「错误 40，设备启动失败」。
- **绕过 eNSP**，直接 `VBoxManage startvm AR_Base --type headless` 也失败，exit code 1。说明问题在 VBox 加固层本身，与 shim/eNSP 无关。

```
VBoxManage.exe: error: The virtual machine 'AR_Base' has terminated unexpectedly during startup with exit code 1 (0x1).
VBoxManage.exe: error: Details: code E_FAIL (0x80004005), component MachineWrap, interface IMachine
```

## 错误日志（VBoxHardening.log 末尾）

```
supR3HardenedWinReSpawn: Spawning ...
Error -104 in supR3HardenedWinReSpawn! (enmWhat=5)
Error relaunching VirtualBox VM process: 5
Command line: 'C:\Program Files\Oracle\VirtualBox\VBoxHeadless.exe ...-suplib-3rdchild --comment AR_Base --startvm ... --vrde config --sup-hardening-log=...'
```

（7.2.18 上失败点提前到 `-suplib-2ndchild`，但错误码一致。）

## 已定位的根因（查了 VBox 源码）

`src/VBox/HostDrivers/Support/win/SUPR3HardenedMain-win.cpp` 里：

```c
if (!CreateProcessW(g_wszSupLibHardenedExePath, pwszCmdLine, &ProcessSecAttrs, &ThreadSecAttrs,
                    TRUE, dwCreationFlags, NULL, NULL, &SiEx.StartupInfo, &ProcessInfoW32))
    supR3HardenedFatalMsg("supR3HardenedWinReSpawn", kSupInitOp_Misc, VERR_INVALID_NAME,
                          "Error relaunching VirtualBox VM process: %u\n"
                          "Command line: '%ls %ls'",
                          RtlGetLastWin32Error(), g_wszSupLibHardenedExePath, pwszCmdLine);
```

- 这里 `%u` 就是 `RtlGetLastWin32Error()` = **5 = ERROR_ACCESS_DENIED**。
- `VERR_INVALID_NAME(-104)` / `enmWhat=5`(=kSupInitOp_Misc) 只是写死的标签，**真实错误是加固加载器用自定义 DACL 调 `CreateProcessW` 生成 VM 子进程时被系统拒绝（ACCESS_DENIED）**。
- 对应 `supR3HardNtChildInitSecAttrs()` 构造的 DACL（Deny Everyone 的 PROCESS_CREATE_THREAD / PROCESS_SET_INFORMATION 等）。

## 已排除项（系统是干净的）

- Windows Defender 实时保护/行为监控：**已关闭**
- Exploit Protection（强制 ASLR / CFG / DEP）：全部 NOTSET，无 IFEO 覆盖
- Smart App Control / WDAC / HVCI 策略：**无**（`CI\Policy` 及 HVCI `Enabled=0`）
- AppInit_DLLs：空
- 第三方杀毒 / 注入 DLL：无（日志 `supR3HardenedWinFindAdversaries: 0x0`）
- Hyper-V / VBS / 内核隔离：未启用
- Windows Sandbox / WDAG：未使用（路径是正常的 `\Device\HarddiskVolume3`，非 `\Device\vmsmb`）

## 关键怀疑点

你测试过的最高 25H2 build 是 **26200.8457**；本机是 **26200.9168**（8 月 KB5123304/KB5121003 把 ntdll 提到 26100.8972）。两者差异仅在这两个安全更新。VBox 7.2.6 / 7.2.14 的 changelog 都出现过「修复近期 Windows 更新导致的 VM 启动崩溃」（7.2.14 修的是 KB5066793），但 **7.2.16 / 7.2.18 没有对应的 Windows host 端修复**，所以最新 VBox 也没解决。

## 想请教

1. 这个 build（26200.9168）你那边是否已复现 / 有计划支持？
2. 有没有临时 workaround（例如让 VBox 走非加固路径、或某个能绕过该 DACL 限制的配置）？
3. 是否建议先固定某个 VBox 版本配合 shim？

（附：本机无系统还原点，8 月 KB 为 composition/merged 包，单独回滚基本不可行。）
