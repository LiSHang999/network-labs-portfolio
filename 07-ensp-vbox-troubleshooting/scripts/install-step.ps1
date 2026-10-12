$log = 'E:\Claude Code\ensp-fix-vb\install-log.txt'
"=== start (correct -s flag) ===" | Out-File -FilePath $log -Encoding utf8

# wait for any pending driver stop to settle
Start-Sleep -Seconds 5

$args = '-s -msiparams "REBOOT=ReallySuppress"'
$p = Start-Process -FilePath 'E:\Claude Code\ensp-fix-vb\VirtualBox-5.2.44-139111-Win.exe' -ArgumentList $args -Wait -PassThru
"INSTALL_EXIT=$($p.ExitCode)" | Out-File -FilePath $log -Append -Encoding utf8

"=== end ===" | Out-File -FilePath $log -Append -Encoding utf8
