Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
Write-Host ""

$token = "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"
$repo = "https://github.com/phuonglatoi/phongtro-attt.git"

Write-Host "[1/5] Add files..." -ForegroundColor Yellow
git add .
Write-Host "OK" -ForegroundColor Green
Write-Host ""

Write-Host "[2/5] Commit..." -ForegroundColor Yellow
git commit -m "feat: PhongTroATTT - He thong quan ly phong tro voi bao mat nang cao"
Write-Host "OK" -ForegroundColor Green
Write-Host ""

Write-Host "[3/5] Set branch to main..." -ForegroundColor Yellow
git branch -M main
Write-Host "OK" -ForegroundColor Green
Write-Host ""

Write-Host "[4/5] Remove old remote..." -ForegroundColor Yellow
git remote remove origin 2>$null
Write-Host "OK" -ForegroundColor Green
Write-Host ""

Write-Host "[5/5] Pushing to GitHub..." -ForegroundColor Yellow
$pushUrl = "https://${token}@github.com/phuonglatoi/phongtro-attt.git"
git push $pushUrl main --force

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository: https://github.com/phuonglatoi/phongtro-attt" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "FAILED!" -ForegroundColor Red
    Write-Host ""
}

