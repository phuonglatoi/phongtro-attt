git add -A
git commit -m "chore: Final cleanup - remove all temporary scripts"
git push https://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@github.com/phuonglatoi/phongtro-attt.git main
Remove-Item "last_push.ps1" -Force
Write-Host "All cleaned up!" -ForegroundColor Green

