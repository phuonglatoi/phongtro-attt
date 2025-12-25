git add -A
git commit -m "chore: Remove push_cleanup script"
git push https://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@github.com/phuonglatoi/phongtro-attt.git main
Remove-Item "final.ps1" -Force
Write-Host "Repository is now clean!" -ForegroundColor Green
Write-Host "Check: https://github.com/phuonglatoi/phongtro-attt" -ForegroundColor Cyan

