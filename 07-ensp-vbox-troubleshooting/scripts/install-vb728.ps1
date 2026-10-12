$ErrorActionPreference = 'Continue'
$log = 'E:\Claude Code\ensp-fix-vb\install-vb728.log'
"=== install-vb728 start $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File $log -Encoding ascii

foreach ($p in 'eNSP_VBoxServer.exe','VBoxSVC.exe','VBoxSDS.exe','VBoxManage.exe','VBoxHeadless.exe') {
    taskkill /F /IM $p 2>$null | Out-Null
}
net stop VBoxSDS 2>$null | Out-Null
net stop VBoxSVC 2>$null | Out-Null
Start-Sleep -Seconds 2

$exe = 'E:\Claude Code\ensp-fix-vb\VirtualBox-7.2.8-173730-Win.exe'
"Running: $exe" | Out-File $log -Append -Encoding ascii

$p = Start-Process -FilePath $exe -ArgumentList '--silent' -Wait -PassThru
"Installer exit code: $($p.ExitCode)" | Out-File $log -Append -Encoding ascii

& 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe' --version 2>&1 | Out-File $log -Append -Encoding ascii
"=== done ===" | Out-File $log -Append -Encoding ascii
