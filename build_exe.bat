@echo off
chcp 65001 >nul
REM בניית קובץ הרצה (.exe) עם אייקון התוכנה
REM דורש: pip install pyinstaller pywebview

echo בונה את שינוי_שם_קבצים.exe ...

pyinstaller --noconfirm --onefile --windowed ^
  --name "שינוי_שם_קבצים" ^
  --icon "app.ico" ^
  --add-data "hebrew_renamer/webui;hebrew_renamer/webui" ^
  gui.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo שגיאה בבנייה. ודא ש-pyinstaller מותקן: pip install pyinstaller
    pause
    exit /b 1
)

echo.
echo הקובץ נבנה בתיקיית dist\
pause
