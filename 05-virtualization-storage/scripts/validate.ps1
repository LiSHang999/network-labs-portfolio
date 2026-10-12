$vmrun = 'G:\VMware\VMware\vmrun.exe'
$user = 'root'
$pass = '__VM_ROOT_PASSWORD__'

# admin?
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
Write-Output ("Admin: " + $isAdmin)

# resolve vmx paths
$targets = @('Web\web.vmx','file\file.vmx','database\database.vmx')
$vmxs = Get-ChildItem 'G:\VMware\LC' -Recurse -Filter *.vmx | Where-Object { $_.Name -in @('web.vmx','file.vmx','database.vmx') }

foreach ($vmx in $vmxs) {
  Write-Output ("===== " + $vmx.FullName + " =====")
  # test VMware Tools + creds via fileExistsInGuest
  $r = & $vmrun -T ws -gu $user -gp $pass fileExistsInGuest $vmx.FullName '/etc/hostname' 2>&1
  Write-Output ("  /etc/hostname exists -> " + $r)
  # check power state
  $s = & $vmrun -T ws list 2>&1
  Write-Output ("  running? " + ($s -match [regex]::Escape($vmx.FullName)))
}
