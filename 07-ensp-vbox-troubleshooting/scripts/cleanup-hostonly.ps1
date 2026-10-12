$ErrorActionPreference = 'Continue'
$log = 'E:\Claude Code\ensp-fix-vb\cleanup-hostonly.log'
$vbm = 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
"=== cleanup hostonly #2 ===" | Out-File $log -Encoding utf8

"--- remove dhcp #2 ---" | Out-File $log -Append -Encoding utf8
& $vbm dhcpserver remove --netname 'HostInterfaceNetworking-VirtualBox Host-Only Ethernet Adapter #2' 2>&1 | Out-File $log -Append -Encoding utf8

"--- hostonlyif remove #2 ---" | Out-File $log -Append -Encoding utf8
& $vbm hostonlyif remove 'VirtualBox Host-Only Ethernet Adapter #2' 2>&1 | Out-File $log -Append -Encoding utf8

"--- list hostonlyifs ---" | Out-File $log -Append -Encoding utf8
& $vbm list hostonlyifs 2>&1 | Out-File $log -Append -Encoding utf8

"--- list dhcpservers ---" | Out-File $log -Append -Encoding utf8
& $vbm list dhcpservers 2>&1 | Out-File $log -Append -Encoding utf8

"=== done ===" | Out-File $log -Append -Encoding utf8
