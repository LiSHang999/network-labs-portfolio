$ErrorActionPreference = 'Continue'
$log = 'E:\Claude Code\ensp-fix-vb\fix-netadp-hostonly.log'
$vbdir = 'C:\Program Files\Oracle\VirtualBox'
$drv = Join-Path $vbdir 'VBoxDrvInst.exe'
$vbm = Join-Path $vbdir 'VBoxManage.exe'
"=== fix netadp + hostonly ===" | Out-File $log -Encoding utf8

"--- install VBoxNetAdp6.inf ---" | Out-File $log -Append -Encoding utf8
& $drv install --inf-file (Join-Path $vbdir 'drivers\network\netadp6\VBoxNetAdp6.inf') 2>&1 | Out-File $log -Append -Encoding utf8
"exit=$LASTEXITCODE" | Out-File $log -Append -Encoding utf8

"--- hostonlyif create ---" | Out-File $log -Append -Encoding utf8
& $vbm hostonlyif create 2>&1 | Out-File $log -Append -Encoding utf8

"--- list hostonlyifs ---" | Out-File $log -Append -Encoding utf8
& $vbm list hostonlyifs 2>&1 | Out-File $log -Append -Encoding utf8

"=== done ===" | Out-File $log -Append -Encoding utf8
