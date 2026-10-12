$ErrorActionPreference = 'Continue'
$log = 'E:\Claude Code\ensp-fix-vb\phase1-log.txt'
"=== phase1 start $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File -FilePath $log -Encoding utf8

function Log($m) { $m | Out-File -FilePath $log -Append -Encoding utf8 }

# 1) Stop VirtualBox kernel drivers to release file locks (non-fatal)
foreach ($d in @('VBoxNetLwf','VBoxNetAdp','VBoxUSBMon','VBoxSup','VBoxDrv')) {
    $o = & sc.exe stop $d 2>&1
    Log "[stop $d] $o"
}
Start-Sleep -Seconds 3

# 2) Uninstall VirtualBox 5.2.44
Log "--- uninstall 5.2.44 ---"
$p = Start-Process -FilePath 'msiexec.exe' -ArgumentList '/x {A94E6C96-FE0C-4E97-9372-C83B28C03D6D} /qn /norestart' -Wait -PassThru
Log "UNINSTALL_EXIT=$($p.ExitCode)"

Start-Sleep -Seconds 3

# 3) Install VirtualBox 7.2.8
Log "--- install 7.2.8 ---"
$msi = 'E:\Claude Code\ensp-fix-vb\vbox-msi\VirtualBox-7.2.8-r173730-MultiArch_amd64.msi'
$p2 = Start-Process -FilePath 'msiexec.exe' -ArgumentList "/i `"$msi`" /qn /norestart" -Wait -PassThru
Log "INSTALL_EXIT=$($p2.ExitCode)"

# 4) Verify install result
Log "--- verify ---"
$v = & 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe' --version 2>&1
Log "VBoxManage --version => $v"

"=== phase1 end $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File -FilePath $log -Append -Encoding utf8
