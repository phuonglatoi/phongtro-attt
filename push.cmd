@echo off
echo ========================================
echo PUSH TO GITHUB
echo ========================================
echo.

set /p GITHUB_USER="Nhap GitHub username cua ban: "
echo.

set TOKEN=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

echo Cau hinh Git...
git config --global user.name "PhongTroATTT"
git config --global user.email "phongtro@example.com"
echo.

if not exist ".git" (
    echo Khoi tao Git...
    git init
    echo.
)

echo Them files...
git add .
echo.

echo Commit code...
git commit -m "feat: PhongTroATTT - He thong quan ly phong tro"
echo.

echo Doi branch thanh main...
git branch -M main
echo.

echo Cau hinh remote...
git remote remove origin 2>nul
git remote add origin https://github.com/%GITHUB_USER%/phongtro-attt.git
echo.

echo Push len GitHub...
git push https://%TOKEN%@github.com/%GITHUB_USER%/phongtro-attt.git main --force

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo PUSH THANH CONG!
    echo ========================================
    echo.
    echo Xem tai: https://github.com/%GITHUB_USER%/phongtro-attt
    echo.
    echo LUU Y: Hay xoa va tao token moi tai:
    echo https://github.com/settings/tokens
) else (
    echo.
    echo PUSH THAT BAI!
    echo.
    echo Kiem tra:
    echo 1. Da tao repository chua? https://github.com/new
    echo 2. Repository name: phongtro-attt
    echo 3. Username dung chua?
)

echo.
pause

