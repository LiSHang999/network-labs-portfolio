$ErrorActionPreference = 'Continue'
$log = 'E:\Claude Code\ensp-fix-vb\start-drivers.log'
"=== start drivers ===" | Out-File $log -Encoding utf8

"--- sc start vboxsup ---" | Out-File $log -Append -Encoding utf8
sc.exe start vboxsup 2>&1 | Out-File $log -Append -Encoding utf8

"--- sc start vboxsds ---" | Out-File $log -Append -Encoding utf8
sc.exe start vboxsds 2>&1 | Out-File $log -Append -Encoding utf8

"--- sc query vboxsup ---" | Out-File $log -Append -Encoding utf8
sc.exe query vboxsup 2>&1 | Out-File $log -Append -Encoding utf8

"--- sc query vboxsds ---" | Out-File $log -Append -Encoding utf8
sc.exe query vboxsds 2>&1 | Out-File $log -Append -Encoding utf8

"=== done ===" | Out-File $log -Append -Encoding utf8
