$log = 'E:\Claude Code\ensp-fix-vb\fix-hostonly-result.log'
"=== fix hostonly-bind start ===" | Out-File $log -Encoding ascii
Set-Location 'E:\Claude Code\ensp-fix-vb\shim-v020'
powershell -NoProfile -ExecutionPolicy Bypass -File 'E:\Claude Code\ensp-fix-vb\shim-v020\diag.ps1' -Fix hostonly-bind *>> $log
"=== fix exit=$LASTEXITCODE ===" | Out-File $log -Append -Encoding ascii
