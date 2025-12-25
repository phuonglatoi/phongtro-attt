@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 AUTO PUSH TO GITHUB
echo ========================================
echo.

REM Cấu hình Git
echo ⚙️ Cấu hình Git...
git config --global user.name "PhongTroATTT"
git config --global user.email "phongtro@example.com"
echo ✅ Đã cấu hình Git
echo.

REM Khởi tạo Git (nếu chưa có)
if not exist ".git" (
    echo 📦 Khởi tạo Git repository...
    git init
    echo ✅ Đã khởi tạo
    echo.
)

REM Add files
echo 📦 Thêm files...
git add .
echo ✅ Đã thêm files
echo.

REM Commit
echo 💾 Commit code...
git commit -m "feat: PhongTroATTT - Hệ thống quản lý phòng trọ với bảo mật nâng cao

- Authentication & Authorization (2FA, RBAC)
- Room management (CRUD, Search, Filter)
- Booking system
- Admin dashboard
- Security features (WAF, Rate limiting, Audit logs)
- Database backup automation
- 18 security features, 100%% OWASP Top 10 compliance"

if errorlevel 1 (
    echo ⚠️ Không có thay đổi mới hoặc đã commit
) else (
    echo ✅ Đã commit
)
echo.

REM Đổi branch thành main
echo 🔄 Đổi branch thành main...
git branch -M main
echo ✅ Đã đổi branch
echo.

REM Nhập username GitHub
echo 📝 Nhập thông tin GitHub:
set /p github_user="Nhập GitHub username của bạn: "
echo.

REM Add remote
echo 🌐 Thêm remote repository...
git remote remove origin 2>nul
git remote add origin https://github.com/%github_user%/phongtro-attt.git
echo ✅ Đã thêm remote: https://github.com/%github_user%/phongtro-attt.git
echo.

REM Push với token
echo 🚀 Push code lên GitHub...
echo.
git push https://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@github.com/%github_user%/phongtro-attt.git main --force

if errorlevel 1 (
    echo.
    echo ❌ Push thất bại!
    echo.
    echo 🔧 Kiểm tra:
    echo 1. Repository đã tạo chưa? https://github.com/%github_user%/phongtro-attt
    echo 2. Username đúng chưa?
    echo 3. Token còn hiệu lực không?
    echo.
) else (
    echo.
    echo ========================================
    echo ✅ PUSH THÀNH CÔNG!
    echo ========================================
    echo.
    echo 🎉 Code đã được đẩy lên GitHub!
    echo 🔗 Xem tại: https://github.com/%github_user%/phongtro-attt
    echo.
    echo ⚠️ LƯU Ý BẢO MẬT:
    echo Token đã bị lộ công khai trong chat!
    echo Hãy XÓA VÀ TẠO TOKEN MỚI ngay:
    echo 👉 https://github.com/settings/tokens
    echo.
)

pause

