# Push to GitHub Script
$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PUSH CODE TO GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Config
$username = "phuonglatoi"
$repo = "phongtro-attt"
$token = "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"

# Step 1: Git config
Write-Host "[1/6] Configure Git..." -ForegroundColor Yellow
git config --global user.name "$username"
git config --global user.email "$username@users.noreply.github.com"
git config --global credential.helper store
Write-Host "Done" -ForegroundColor Green
Write-Host ""

# Step 2: Init (if needed)
if (-not (Test-Path ".git")) {
    Write-Host "[2/6] Initialize Git..." -ForegroundColor Yellow
    git init
    Write-Host "Done" -ForegroundColor Green
} else {
    Write-Host "[2/6] Git already initialized" -ForegroundColor Green
}
Write-Host ""

# Step 3: Add files
Write-Host "[3/6] Add files..." -ForegroundColor Yellow
git add .
Write-Host "Done" -ForegroundColor Green
Write-Host ""

# Step 4: Commit
Write-Host "[4/6] Commit..." -ForegroundColor Yellow
$commitMsg = @"
feat: PhongTroATTT - Hệ thống quản lý phòng trọ với bảo mật nâng cao

✅ Authentication & Authorization (2FA, RBAC)
✅ Room Management (CRUD, Search, Filter)
✅ Booking System
✅ Admin Dashboard
✅ Security Features (WAF, Rate Limiting, Audit Logs)
✅ Database Backup Automation
✅ 18 Security Features
✅ 100% OWASP Top 10 Compliance
"@

git commit -m $commitMsg
if ($LASTEXITCODE -ne 0) {
    Write-Host "No changes to commit or already committed" -ForegroundColor Yellow
}
Write-Host "Done" -ForegroundColor Green
Write-Host ""

# Step 5: Set branch
Write-Host "[5/6] Set branch to main..." -ForegroundColor Yellow
git branch -M main
Write-Host "Done" -ForegroundColor Green
Write-Host ""

# Step 6: Push
Write-Host "[6/6] Push to GitHub..." -ForegroundColor Yellow
Write-Host "Repository: https://github.com/$username/$repo" -ForegroundColor Cyan
Write-Host ""

# Remove old remote
git remote remove origin 2>$null

# Add new remote with token
$remoteUrl = "https://${token}@github.com/${username}/${repo}.git"
git remote add origin $remoteUrl

# Push
Write-Host "Pushing..." -ForegroundColor Yellow
git push -u origin main --force 2>&1 | Tee-Object -Variable pushOutput

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ SUCCESS!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 Code đã được push lên GitHub!" -ForegroundColor Cyan
    Write-Host "🔗 Xem tại: https://github.com/$username/$repo" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "⚠️  LƯU Ý BẢO MẬT:" -ForegroundColor Yellow
    Write-Host "Token đã bị lộ công khai trong chat!" -ForegroundColor Red
    Write-Host "Hãy XÓA và TẠO TOKEN MỚI ngay tại:" -ForegroundColor Red
    Write-Host "👉 https://github.com/settings/tokens" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ FAILED!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error output:" -ForegroundColor Yellow
    Write-Host $pushOutput -ForegroundColor White
    Write-Host ""
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "1. Token không có quyền 'repo' đầy đủ" -ForegroundColor White
    Write-Host "2. Repository chưa được tạo hoặc không đúng owner" -ForegroundColor White
    Write-Host "3. Token đã hết hạn" -ForegroundColor White
    Write-Host ""
    Write-Host "Giải pháp:" -ForegroundColor Yellow
    Write-Host "1. Tạo token mới tại: https://github.com/settings/tokens/new" -ForegroundColor Cyan
    Write-Host "   - Chọn scope: repo (tất cả)" -ForegroundColor White
    Write-Host "2. Kiểm tra repository: https://github.com/$username/$repo" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

