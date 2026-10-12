$log = 'E:\Claude Code\ensp-fix-vb\fix-hostonly-d2-result.log'
$vbox = 'C:\Program Files\Oracle\VirtualBox'
"=== D2 fix start ===" | Out-File $log -Encoding ascii

# 1. Recreate the oracle_VBoxNetLwf NetService component (NDIS LWF filter)
$netcfg = 'C:\Windows\System32\netcfg.exe'
$inf = "$vbox\drivers\network\netlwf\VBoxNetLwf.inf"
"--- netcfg install oracle_VBoxNetLwf ---" | Out-File $log -Append -Encoding ascii
& $netcfg -v -l $inf -c s -i oracle_VBoxNetLwf *>> $log
"--- netcfg exit=$LASTEXITCODE ---" | Out-File $log -Append -Encoding ascii

# 2. Bounce the host-only adapter to rebind
Start-Sleep -Seconds 2
"--- bounce adapter ---" | Out-File $log -Append -Encoding ascii
Disable-NetAdapter -Name '以太网 2' -Confirm:$false *>> $log
Start-Sleep -Seconds 3
Enable-NetAdapter -Name '以太网 2' -Confirm:$false *>> $log
"--- bounce done ---" | Out-File $log -Append -Encoding ascii

# 3. Verify
"--- verify binding ---" | Out-File $log -Append -Encoding ascii
$adapter = Get-NetAdapter | Where-Object { $_.InterfaceDescription -like '*VirtualBox Host-Only*' }
$b = Get-NetAdapterBinding -Name $adapter.Name | Where-Object { $_.ComponentID -match 'VBox|NetLwf' }
if ($b) { $b | Out-String | Out-File $log -Append -Encoding ascii } else { '(!) still no VBoxNetLwf binding' | Out-File $log -Append -Encoding ascii }
sc.exe query VBoxNetLwf *>> $log
"=== D2 fix end ===" | Out-File $log -Append -Encoding ascii
