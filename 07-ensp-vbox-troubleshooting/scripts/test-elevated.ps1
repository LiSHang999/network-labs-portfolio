$log = 'E:\Claude Code\ensp-fix-vb\test-elevated-result.log'
"=== start (elevated=$([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) ===" | Out-File $log -Encoding ascii
$vbm = 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
& $vbm startvm AR_Base --type headless *>> $log
"=== exit=$LASTEXITCODE ===" | Out-File $log -Append -Encoding ascii
& $vbm list runningvms *>> $log
