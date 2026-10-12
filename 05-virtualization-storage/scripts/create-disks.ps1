$vdm = 'G:\VMware\VMware\vmware-vdiskmanager.exe'

function Resolve-VMDir($name) {
  $vmx = Get-ChildItem 'G:\VMware\LC' -Recurse -Filter *.vmx | Where-Object { $_.Name -eq $name } | Select-Object -First 1
  return $vmx.Directory.FullName
}

$dbDir = Resolve-VMDir 'database.vmx'
$fileDir = Resolve-VMDir 'file.vmx'

Write-Output ("database dir: " + $dbDir)
Write-Output ("file dir: " + $fileDir)

# database: 4 x 5GB for RAID10
foreach ($i in 2..5) {
  $disk = Join-Path $dbDir ("database-disk" + $i + ".vmdk")
  Write-Output ("create " + $disk)
  & $vdm -c -s 5GB -a lsilogic -t 0 $disk 2>&1
}
# file: 1 x 20GB for LVM
$disk = Join-Path $fileDir 'file-disk2.vmdk'
Write-Output ("create " + $disk)
& $vdm -c -s 20GB -a lsilogic -t 0 $disk 2>&1

Write-Output '--- verify created ---'
Get-ChildItem $dbDir, $fileDir -Filter '*.vmdk' | Where-Object { $_.Name -match 'disk[2-5]' } | Select-Object Name, @{n='KB';e={[math]::Round($_.Length/1KB)}} | Format-Table -AutoSize | Out-String -Width 200
