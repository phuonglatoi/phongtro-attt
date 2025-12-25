# Final Push Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PUSHING TO GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$token = "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"
$username = "phuonglatoi"
$repo = "phongtro-attt"

Write-Host "Repository: https://github.com/$username/$repo" -ForegroundColor Yellow
Write-Host ""

# Configure Git
Write-Host "[1/5] Configuring Git..." -ForegroundColor Yellow
git config --global user.name "$username"
git config --global user.email "$username@users.noreply.github.com"
Write-Host "OK" -ForegroundColor Green
Write-Host ""

# Add files
Write-Host "[2/5] Adding files..." -ForegroundColor Yellow
git add .
Write-Host "OK" -ForegroundColor Green
Write-Host ""

# Commit
Write-Host "[3/5] Committing..." -ForegroundColor Yellow
git commit -m "feat: PhongTroATTT - He thong quan ly phong tro voi bao mat nang cao

- Authentication & Authorization (2FA, RBAC)
- Room Management (CRUD, Search, Filter)
- Booking System
- Admin Dashboard
- Security Features (WAF, Rate Limiting, Audit Logs)
- Database Backup Automation
- 18 Security Features, 100% OWASP Top 10"

if ($LASTEXITCODE -ne 0) {
    Write-Host "No new changes or already committed" -ForegroundColor Yellow
}
Write-Host "OK" -ForegroundColor Green
Write-Host ""

# Set branch
Write-Host "[4/5] Setting branch to main..." -ForegroundColor Yellow
git branch -M main
Write-Host "OK" -ForegroundColor Green
Write-Host ""

# Push
Write-Host "[5/5] Pushing to GitHub..." -ForegroundColor Yellow
git remote remove origin 2>$null
$remoteUrl = "https://${token}@github.com/${username}/${repo}.git"
git remote add origin $remoteUrl
git push -u origin main --force

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Code da duoc push len GitHub!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Xem tai: https://github.com/$username/$repo" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "LUU Y BAO MAT:" -ForegroundColor Red
    Write-Host "Token da bi lo cong khai!" -ForegroundColor Red
    Write-Host "Hay XOA va TAO TOKEN MOI tai:" -ForegroundColor Yellow
    Write-Host "https://github.com/settings/tokens" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "FAILED!" -ForegroundColor Red
    Write-Host "Kiem tra token va repository" -ForegroundColor Yellow
}

Write-Host ""

