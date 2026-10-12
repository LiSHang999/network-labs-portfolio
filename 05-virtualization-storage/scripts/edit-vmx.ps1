$enc = New-Object System.Text.UTF8Encoding($false)  # UTF-8 no BOM
$pvnID = '52 4c 5e 98 70 6a 82 1b-0f eb 97 5d 76 2e 8a 85'
$CRLF = "`r`n"

$vmxs = Get-ChildItem 'G:\VMware\LC' -Recurse -Filter *.vmx | Where-Object { $_.Name -in @('web.vmx','file.vmx','database.vmx') }

foreach ($vmx in $vmxs) {
  $path = $vmx.FullName
  $c = [System.IO.File]::ReadAllText($path, $enc)
  $orig = $c

  if ($vmx.Name -eq 'web.vmx') {
    # ethernet0 missing connectionType -> make it NAT
    $c = $c.Replace('ethernet0.virtualDev = "vmxnet3"', 'ethernet0.virtualDev = "vmxnet3"' + $CRLF + 'ethernet0.connectionType = "nat"' + $CRLF + 'ethernet0.startConnected = "TRUE"')
    # add ethernet1 = pvn (LAN segment)
    $eth1 = @(
      'ethernet1.present = "TRUE"',
      'ethernet1.virtualDev = "vmxnet3"',
      'ethernet1.connectionType = "pvn"',
      'ethernet1.pvnID = "' + $pvnID + '"',
      'ethernet1.startConnected = "TRUE"',
      'ethernet1.addressType = "generated"',
      'ethernet1.pciSlotNumber = "224"',
      'ethernet1.allowguestconnectioncontrol = "false"',
      'ethernet1.generatedAddress = "00:0c:29:79:6c:15"',
      'ethernet1.generatedAddressOffset = "10"'
    ) -join $CRLF
    $c = $c.TrimEnd() + $CRLF + $CRLF + $eth1 + $CRLF
  }
  elseif ($vmx.Name -eq 'file.vmx') {
    # add ethernet1 = pvn
    $eth1 = @(
      'ethernet1.present = "TRUE"',
      'ethernet1.virtualDev = "vmxnet3"',
      'ethernet1.connectionType = "pvn"',
      'ethernet1.pvnID = "' + $pvnID + '"',
      'ethernet1.startConnected = "TRUE"',
      'ethernet1.addressType = "generated"',
      'ethernet1.pciSlotNumber = "224"',
      'ethernet1.allowguestconnectioncontrol = "false"',
      'ethernet1.generatedAddress = "00:0c:29:4f:a3:47"',
      'ethernet1.generatedAddressOffset = "10"'
    ) -join $CRLF
    $c = $c.TrimEnd() + $CRLF + $CRLF + $eth1 + $CRLF
  }
  elseif ($vmx.Name -eq 'database.vmx') {
    # ethernet0 NAT -> pvn (isolated, no internet)
    $c = $c.Replace('ethernet0.connectionType = "nat"', 'ethernet0.connectionType = "pvn"' + $CRLF + 'ethernet0.pvnID = "' + $pvnID + '"')
  }

  if ($c -ne $orig) {
    [System.IO.File]::WriteAllText($path, $c, $enc)
    Write-Output ("EDITED: " + $vmx.Name)
  } else {
    Write-Output ("NO-CHANGE (unexpected): " + $vmx.Name)
  }
}

Write-Output ''
Write-Output '===== verify ethernet lines ====='
foreach ($vmx in $vmxs) {
  Write-Output ("--- " + $vmx.Name + " ---")
  [System.IO.File]::ReadAllText($vmx.FullName, $enc) -split "`r?`n" | Where-Object { $_ -match 'ethernet' }
}
