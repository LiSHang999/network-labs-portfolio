$vmrun = 'G:\VMware\VMware\vmrun.exe'
$user = 'root'
$pass = '__VM_ROOT_PASSWORD__'
$local = 'E:\Claude Code\virt-storage-lab'

$map = @{
  'database.vmx' = 'db-raid.sh'
  'file.vmx'     = 'file-lvm.sh'
}

$vmxs = Get-ChildItem 'G:\VMware\LC' -Recurse -Filter *.vmx | Where-Object { $_.Name -in @('database.vmx','file.vmx') }

foreach ($vmx in $vmxs) {
  $script = $map[$vmx.Name]
  Write-Output ("===== " + $vmx.Name + " =====")
  & $vmrun -T ws -gu $user -gp $pass CopyFileFromHostToGuest $vmx.FullName ($local + '\' + $script) '/root/cfg.sh' 2>&1 | Out-Null
  & $vmrun -T ws -gu $user -gp $pass runProgramInGuest $vmx.FullName '/bin/bash' '/root/cfg.sh' 2>&1 | Out-Null
  Start-Sleep -Seconds 12
  if ($vmx.Name -eq 'database.vmx') { $remote = '/root/raid.txt' } else { $remote = '/root/lvm.txt' }
  $out = ($local + '\' + $(if ($vmx.Name -eq 'database.vmx') {'raid'} else {'lvm'}) + '-result.txt')
  & $vmrun -T ws -gu $user -gp $pass CopyFileFromGuestToHost $vmx.FullName $remote $out 2>&1 | Out-Null
  if (Test-Path $out) { Get-Content $out } else { Write-Output '  (no output)' }
  Write-Output ''
}
