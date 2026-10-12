try {
    $a = '-NoProfile -ExecutionPolicy Bypass -File "E:\Claude Code\ensp-fix-vb\phase1-uninstall-install.ps1"'
    $p = Start-Process powershell.exe -ArgumentList $a -Verb RunAs -Wait -PassThru -ErrorAction Stop
    Write-Output "RESULT=OK EXITCODE=$($p.ExitCode)"
} catch {
    Write-Output "RESULT=FAIL MSG=$($_.Exception.Message)"
}
