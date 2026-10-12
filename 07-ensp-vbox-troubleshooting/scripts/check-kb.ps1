$log = 'E:\Claude Code\ensp-fix-vb\dism-packages.txt'
dism /online /get-packages /format:table 2>&1 | Out-File $log -Encoding ascii
"=== PACKAGE INFO for 9168 ===" | Out-File $log -Append -Encoding ascii
dism /online /get-packageinfo /packagename:"Composition-Core-Package~31bf3856ad364e35~amd64~~10.0.26100.9168" 2>&1 | Out-File $log -Append -Encoding ascii
