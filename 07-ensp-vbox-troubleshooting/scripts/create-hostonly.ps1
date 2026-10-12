$ErrorActionPreference = 'Continue'
$log = 'E:\Claude Code\ensp-fix-vb\create-hostonly.log'
$vbm = 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
"=== create hostonly ===" | Out-File $log -Encoding utf8

"--- hostonlyif create ---" | Out-File $log -Append -Encoding utf8
& $vbm hostonlyif create 2>&1 | Out-File $log -Append -Encoding utf8

"--- list hostonlyifs ---" | Out-File $log -Append -Encoding utf8
& $vbm list hostonlyifs 2>&1 | Out-File $log -Append -Encoding utf8

"--- list dhcpservers ---" | Out-File $log -Append -Encoding utf8
& $vbm list dhcpservers 2>&1 | Out-File $log -Append -Encoding utf8

"=== done ===" | Out-File $log -Append -Encoding utf8
