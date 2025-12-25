@echo off
chcp 65001 >nul
echo ========================================
echo PUSH TO GITHUB - phuonglatoi/phongtro-attt
echo ========================================
echo.

set GITHUB_USER=phuonglatoi
set TOKEN=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

echo [1/7] Cau hinh Git...
git config --global user.name "phuonglatoi" 2>nul
git config --global user.email "phuonglatoi@github.com" 2>nul
echo OK
echo.

if not exist ".git" (
    echo [2/7] Khoi tao Git repository...
    git init
    echo OK
    echo.
) else (
    echo [2/7] Git repository da ton tai
    echo.
)

echo [3/7] Them files vao Git...
git add .
echo OK
echo.

echo [4/7] Commit code...
git commit -m "feat: PhongTroATTT - He thong quan ly phong tro voi bao mat nang cao" 2>nul
if %errorlevel% equ 0 (
    echo OK - Da commit
) else (
    echo OK - Khong co thay doi moi
)
echo.

echo [5/7] Doi branch thanh main...
git branch -M main 2>nul
echo OK
echo.

echo [6/7] Cau hinh remote repository...
git remote remove origin 2>nul
git remote add origin https://github.com/%GITHUB_USER%/phongtro-attt.git
echo OK - https://github.com/%GITHUB_USER%/phongtro-attt.git
echo.

echo [7/7] Push code len GitHub...
echo Dang push... Vui long cho...
echo.
git push https://%TOKEN%@github.com/%GITHUB_USER%/phongtro-attt.git main --force

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo THANH CONG!
    echo ========================================
    echo.
    echo Code da duoc push len GitHub!
    echo.
    echo Xem tai: https://github.com/%GITHUB_USER%/phongtro-attt
    echo.
    echo.
    echo LUU Y BAO MAT:
    echo Token da bi lo cong khai!
    echo Hay XOA VA TAO TOKEN MOI ngay tai:
    echo https://github.com/settings/tokens
    echo.
) else (
    echo.
    echo ========================================
    echo THAT BAI!
    echo ========================================
    echo.
    echo Nguyen nhan co the:
    echo 1. Repository chua duoc tao
    echo 2. Token het han hoac khong hop le
    echo 3. Khong co quyen truy cap
    echo.
    echo Tao repository tai: https://github.com/new
    echo - Repository name: phongtro-attt
    echo - KHONG chon "Initialize with README"
    echo.
)

pause

