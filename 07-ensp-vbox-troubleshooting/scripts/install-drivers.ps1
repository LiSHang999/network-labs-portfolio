$ErrorActionPreference = 'Continue'
$log = 'E:\Claude Code\ensp-fix-vb\install-drivers.log'
$vbdir = 'C:\Program Files\Oracle\VirtualBox'
$drv = Join-Path $vbdir 'VBoxDrvInst.exe'

"=== driver install start ===" | Out-File $log -Encoding utf8

$infs = @(
  'drivers\vboxsup\VBoxSup.inf',
  'drivers\network\netlwf\VBoxNetLwf.inf',
  'drivers\USB\device\VBoxUSB.inf',
  'drivers\USB\filter\VBoxUSBMon.inf'
)

foreach ($rel in $infs) {
  $inf = Join-Path $vbdir $rel
  "--- installing $rel ---" | Out-File $log -Append -Encoding utf8
  & $drv install --inf-file $inf 2>&1 | Out-File $log -Append -Encoding utf8
  "exit=$LASTEXITCODE" | Out-File $log -Append -Encoding utf8
}

"--- status ---" | Out-File $log -Append -Encoding utf8
& $drv status 2>&1 | Out-File $log -Append -Encoding utf8

"=== done ===" | Out-File $log -Append -Encoding utf8
