$log = 'E:\Claude Code\virt-storage-lab\vmnet8-fix.log'
"=== fix vmnet8 started ===" | Out-File $log -Encoding ascii
try {
  $adapter = Get-NetAdapter -Name 'VMware Network Adapter VMnet8' -ErrorAction Stop
  ("adapter: " + $adapter.Name + " index=" + $adapter.ifIndex) | Out-File $log -Append -Encoding ascii
  Remove-NetIPAddress -InterfaceIndex $adapter.ifIndex -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
  New-NetIPAddress -InterfaceIndex $adapter.ifIndex -IPAddress 192.168.61.1 -PrefixLength 24 -AddressFamily IPv4 -ErrorAction SilentlyContinue
  Set-NetIPInterface -InterfaceIndex $adapter.ifIndex -AddressFamily IPv4 -Dhcp Disabled -ErrorAction SilentlyContinue
  "--- result ---" | Out-File $log -Append -Encoding ascii
  Get-NetIPAddress -InterfaceIndex $adapter.ifIndex -AddressFamily IPv4 | ForEach-Object { ($_.InterfaceAlias + " " + $_.IPAddress + "/" + $_.PrefixLength) } | Out-File $log -Append -Encoding ascii
} catch {
  ("ERROR: " + $_.Exception.Message) | Out-File $log -Append -Encoding ascii
}
"=== done ===" | Out-File $log -Append -Encoding ascii
