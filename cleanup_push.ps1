Write-Host "Cleaning up and pushing..." -ForegroundColor Cyan
Write-Host ""

$token = "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"

Write-Host "[1/3] Adding changes..." -ForegroundColor Yellow
git add -A
Write-Host "OK" -ForegroundColor Green
Write-Host ""

Write-Host "[2/3] Committing..." -ForegroundColor Yellow
git commit -m "chore: Remove unnecessary files (push scripts, shortcuts, temp files)"
Write-Host "OK" -ForegroundColor Green
Write-Host ""

Write-Host "[3/3] Pushing to GitHub..." -ForegroundColor Yellow
git push https://${token}@github.com/phuonglatoi/phongtro-attt.git main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS! Files cleaned up and pushed." -ForegroundColor Green
    Write-Host "Check: https://github.com/phuonglatoi/phongtro-attt" -ForegroundColor Cyan
} else {
    Write-Host "FAILED!" -ForegroundColor Red
}

Write-Host ""

