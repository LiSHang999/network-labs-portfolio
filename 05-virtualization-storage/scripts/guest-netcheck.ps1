$vmrun = 'G:\VMware\VMware\vmrun.exe'
$user = 'root'
$pass = '__VM_ROOT_PASSWORD__'
$local = 'E:\Claude Code\virt-storage-lab'

$vmxs = Get-ChildItem 'G:\VMware\LC' -Recurse -Filter *.vmx | Where-Object { $_.Name -in @('web.vmx','file.vmx','database.vmx') }

foreach ($vmx in $vmxs) {
  Write-Output ("===== " + $vmx.Name + " =====")
  # push script
  & $vmrun -T ws -gu $user -gp $pass CopyFileFromHostToGuest $vmx.FullName ($local + '\netcheck.sh') '/root/netcheck.sh' 2>&1 | Out-Null
  # run it
  & $vmrun -T ws -gu $user -gp $pass runProgramInGuest $vmx.FullName '/bin/bash' '/root/netcheck.sh' 2>&1 | Out-Null
  Start-Sleep -Seconds 2
  # pull result
  $out = ($local + '\netcheck-' + $vmx.Name + '.txt')
  & $vmrun -T ws -gu $user -gp $pass CopyFileFromGuestToHost $vmx.FullName '/root/netcheck.txt' $out 2>&1 | Out-Null
  if (Test-Path $out) {
    Get-Content $out
  } else {
    Write-Output '  (no output pulled)'
  }
  Write-Output ''
}
