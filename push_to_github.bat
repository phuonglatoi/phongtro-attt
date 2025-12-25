@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 PUSH CODE LÊN GITHUB
echo ========================================
echo.

REM Kiểm tra Git đã cài chưa
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git chưa được cài đặt!
    echo 📥 Tải Git tại: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo ✅ Git đã được cài đặt
echo.

REM Kiểm tra đã có .git chưa
if not exist ".git" (
    echo 📦 Khởi tạo Git repository...
    git init
    echo ✅ Đã khởi tạo Git repository
    echo.
)

REM Kiểm tra cấu hình Git
git config user.name >nul 2>&1
if errorlevel 1 (
    echo ⚙️ Cấu hình Git...
    set /p username="Nhập tên của bạn: "
    set /p email="Nhập email của bạn: "
    git config --global user.name "%username%"
    git config --global user.email "%email%"
    echo ✅ Đã cấu hình Git
    echo.
)

REM Tạo .gitignore nếu chưa có
if not exist ".gitignore" (
    echo 📝 Tạo file .gitignore...
    (
        echo # Python
        echo *.pyc
        echo __pycache__/
        echo *.py[cod]
        echo *$py.class
        echo *.so
        echo .Python
        echo env/
        echo venv/
        echo ENV/
        echo.
        echo # Django
        echo *.log
        echo db.sqlite3
        echo db.sqlite3-journal
        echo /media
        echo /staticfiles
        echo .env
        echo .env.local
        echo.
        echo # IDE
        echo .vscode/
        echo .idea/
        echo *.swp
        echo *.swo
        echo.
        echo # OS
        echo .DS_Store
        echo Thumbs.db
        echo.
        echo # Backup
        echo *.bak
        echo *.backup
    ) > .gitignore
    echo ✅ Đã tạo .gitignore
    echo.
)

REM Add files
echo 📦 Thêm files vào Git...
git add .
echo ✅ Đã thêm files
echo.

REM Commit
echo 💾 Commit code...
git commit -m "Initial commit: PhongTroATTT - Hệ thống quản lý phòng trọ với bảo mật nâng cao"
if errorlevel 1 (
    echo ⚠️ Không có thay đổi để commit hoặc đã commit rồi
) else (
    echo ✅ Đã commit code
)
echo.

REM Kiểm tra remote
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo 🌐 Chưa có remote repository
    echo.
    echo 📋 HƯỚNG DẪN:
    echo 1. Vào https://github.com/new
    echo 2. Tạo repository mới tên: phongtro-attt
    echo 3. KHÔNG chọn "Initialize with README"
    echo 4. Copy URL repository (ví dụ: https://github.com/username/phongtro-attt.git^)
    echo.
    set /p repo_url="Nhập URL repository: "
    
    git remote add origin %repo_url%
    echo ✅ Đã thêm remote origin
    echo.
)

REM Đổi branch thành main
echo 🔄 Đổi branch thành main...
git branch -M main
echo ✅ Đã đổi branch thành main
echo.

REM Push
echo 🚀 Push code lên GitHub...
echo.
echo ⚠️ Nếu bị lỗi authentication:
echo    - Username: Nhập username GitHub của bạn
echo    - Password: Nhập Personal Access Token (KHÔNG phải password)
echo    - Tạo token tại: https://github.com/settings/tokens
echo.
git push -u origin main

if errorlevel 1 (
    echo.
    echo ❌ Push thất bại!
    echo.
    echo 🔧 Thử lại với force push? (y/n^)
    set /p force="Nhập lựa chọn: "
    if /i "%force%"=="y" (
        git push -u origin main --force
    )
) else (
    echo.
    echo ========================================
    echo ✅ PUSH THÀNH CÔNG!
    echo ========================================
    echo.
    echo 🎉 Code đã được đẩy lên GitHub!
    echo 🔗 Kiểm tra tại repository của bạn
    echo.
)

pause

