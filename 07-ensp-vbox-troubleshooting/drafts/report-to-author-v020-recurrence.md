# 错误 40 复发报告（build 26200.9457，最新累积更新已装）

## 现象

eNSP 拖 AR 设备启动报「错误 40」，`VBoxManage startvm AR_Base --type headless` 直接失败 exit 1。`VBoxHardening.log` 末尾：

```
Error -104 in supR3HardenedWinReSpawn! (enmWhat=5)
Error relaunching VirtualBox VM process: 5   (ERROR_ACCESS_DENIED)
```

判别三条全部命中「根因 E」：绕开 eNSP 直接 startvm 也失败；锚点是 `-104` 而非 `-5657`；日志/报告里没有被拒模块。

## 时间线

- 2026-09-17：装 KB5129195 + KB5124007（build 26200.9168 → 9457，ntdll 8972 → 9278）后问题自愈，端到端跑通（含 AR/WLAN 设备克隆启动）。
- 2026-09-18：仅 Store/app 更新（OpenAI.Codex、WindowsAppRuntime、Edge/Copilot）。
- 2026-09-20：**同 build 9457 上错误 40 复发**，重启后依旧，连续 6 次稳定失败。

即：9 月累积更新只能「暂时压住」，本质偶发/复发，不是版本决定性的。

## 已排除的成因（本机逐项核查）

| 假设 | 结果 |
|---|---|
| 安全软件拦截 | 本机仅火绒（`HipsDaemon`+`sysdiag`/`hrwfpdrv`/`hrdevmon` 三驱动在跑）。hipsdaemon.log **无任何 VBox 拦截记录**；且 9/17 修复态下火绒同样在场。SecurityCenter 里的「360/腾讯」是卸载残留注册项。 |
| 智能应用控制 / VBS / 内存完整性 | 均关闭（`VerifiedAndReputablePolicyState=0`、`VirtualizationBasedSecurityStatus=0`）。 |
| 文件权限 / ACL | VBoxHeadless.exe `Everyone` 有 ReadAndExecute；owner SYSTEM（VBox 安装器默认）。 |
| ntdll 被悄悄更新 | 文件未变（Size 0x267BE0、LastWrite 9/17）。版本显示 9278 vs 9444 是「FileVersion 字符串」与「数值 FilePrivatePart」的微软系统 DLL 常见不一致，非更新。 |
| 权限 / token 不够 | **提权（管理员）运行 startvm 同样失败**，非 token 问题。 |
| Windows / VBox 更新 | 均最新（build 9457 / VBox 7.2.18r175117，`LATEST-STABLE.TXT` 仍 7.2.18）。 |

## 附带发现：还有一个独立的 host-only 绑定失效（D1）

诊断报告第 [3]/[9] 节另检出：`VBoxNetLwf` 服务 Stopped、`oracle_VBoxNetLwf` 未绑定到 host-only 网卡（`VERR_INTNET_FLT_IF_NOT_FOUND` 型）。这个 -104 解决后仍会卡设备联网，`环境检查.bat -Fix hostonly-bind` 可修。

## 附：诊断报告

`C:\ProgramData\ensp-vbox-shim\diag-20260920-092213.txt`（v0.2.0-beta `环境检查.bat` 生成，10 节完整，第 [8] 节确认 `rc=-104 supR3HardenedWinReSpawn Misc(5)`）。

## 诉求

-104 在最新累积更新上仍复发，是否有垫片侧可绕过的路径（比如拦截 CreateProcessW 失败后的重试/回退），或有可定向验证的修复层？如需更多环境信息请告知。
