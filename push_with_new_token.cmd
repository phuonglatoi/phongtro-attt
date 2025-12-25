@echo off
chcp 65001 >nul
echo ========================================
echo PUSH TO GITHUB
echo ========================================
echo.
echo Repository: https://github.com/phuonglatoi/phongtro-attt
echo.
echo.
echo TAO TOKEN MOI TAI:
echo https://github.com/settings/tokens/new
echo.
echo Chon scopes: repo (tat ca)
echo.
set /p TOKEN="Nhap token vua tao: "
echo.

echo [1/5] Cau hinh Git...
git config --global user.name "phuonglatoi"
git config --global user.email "phuonglatoi@github.com"
echo OK
echo.

echo [2/5] Add files...
git add .
echo OK
echo.

echo [3/5] Commit...
git commit -m "feat: PhongTroATTT - He thong quan ly phong tro voi bao mat nang cao"
if %errorlevel% equ 0 (
    echo OK - Da commit
) else (
    echo OK - Khong co thay doi moi
)
echo.

echo [4/5] Doi branch thanh main...
git branch -M main
echo OK
echo.

echo [5/5] Push len GitHub...
echo Dang push...
echo.
git push https://%TOKEN%@github.com/phuonglatoi/phongtro-attt.git main --force

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo THANH CONG!
    echo ========================================
    echo.
    echo Code da duoc push len:
    echo https://github.com/phuonglatoi/phongtro-attt
    echo.
) else (
    echo.
    echo ========================================
    echo THAT BAI!
    echo ========================================
    echo.
    echo Kiem tra:
    echo 1. Token co quyen "repo" chua?
    echo 2. Token con hieu luc khong?
    echo 3. Repository da duoc tao chua?
    echo.
)

pause

