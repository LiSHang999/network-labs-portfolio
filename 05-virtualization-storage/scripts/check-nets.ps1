Write-Output '===== NetAdapters (VMware) ====='
Get-NetAdapter -ErrorAction SilentlyContinue | Where-Object { $_.Name -like '*VMware*' -or $_.InterfaceDescription -like '*VMware*' } | Format-Table Name, InterfaceDescription, Status -AutoSize | Out-String -Width 200

Write-Output '===== IPv4 on VMware adapters ====='
Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue | Where-Object { $_.InterfaceAlias -like '*VMnet*' } | Format-Table InterfaceAlias, IPAddress, PrefixLength -AutoSize | Out-String -Width 200

Write-Output '===== vmnetcfg / Virtual Network Editor present? ====='
$paths = @('C:\Program Files (x86)\VMware\VMware Workstation\vmnetcfg.exe','C:\Program Files\VMware\VMware Workstation\vmnetcfg.exe','G:\VMware\VMware\vmnetcfg.exe')
foreach ($p in $paths) { if (Test-Path $p) { Write-Output ("FOUND: " + $p) } }
