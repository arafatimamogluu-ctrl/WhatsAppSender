@echo off
title GitHub Kurulum Sihirbazi
color 0f
echo ========================================================
echo          GITHUB ENTEGRASYON SIHIRBAZI
echo ========================================================
echo.

:: 1. GitHub CLI Kontrol
gh --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] GitHub CLI (gh) yuklu degil veya henuz yola eklenmedi.
    echo Lutfen terminali kapatip acin veya yuklemenin bitmesini bekleyin.
    pause
    exit
)

:: 2. Giris Kontrol
echo [1/3] GitHub Giris Kontrolu yapiliyor...
gh auth status >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo GitHub'a giris yapmaniz gerekiyor.
    echo [BILGI] Tarayici acilacak, lutfen onay verin.
    echo.
    gh auth login -w -p HTTPS
    if %errorlevel% neq 0 (
        echo [HATA] Giris basarisiz oldu.
        pause
        exit
    )
) else (
    echo [OK] Zaten giris yapilmis.
)

:: 3. Repo Olusturma
echo.
echo [2/3] GitHub deposu olusturuluyor...
set /p REPO_NAME="Repository ismi ne olsun? (Bos birakirsaniz 'WhatsAppSender' olur): "
if "%REPO_NAME%"=="" set REPO_NAME=WhatsAppSender

gh repo create %REPO_NAME% --public --source=. --remote=origin --push

if %errorlevel% neq 0 (
    echo.
    echo [BILGI] Repo olusturulamadi (belki zaten var?). Push deniyoruz...
    git push -u origin main
)

echo.
echo [3/3] Islem Tamamlandi!
echo.
echo Repo linkiniz: https://github.com/%USERNAME%/%REPO_NAME%
echo.
pause
