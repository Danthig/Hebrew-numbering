@echo off
chcp 65001 >nul
REM תוכנת שינוי שם קבצים - מפעיל ל-Windows

REM 1) אם קובץ ההרצה כבר נבנה - הפעל אותו ישירות
if exist "שינוי_שם_קבצים.exe" (
    start "" "שינוי_שם_קבצים.exe"
    exit /b 0
)
if exist "dist\שינוי_שם_קבצים.exe" (
    start "" "dist\שינוי_שם_קבצים.exe"
    exit /b 0
)

REM 2) אחרת - הרצה דרך Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo שגיאה: Python לא מותקן או לא נמצא ב-PATH
    echo אנא הורד Python מ- https://www.python.org
    pause
    exit /b 1
)

REM התקנת הממשק המודרני (pywebview) אם חסר - לא חובה, יש נפילה ל-tkinter
python -c "import webview" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo מתקין את הממשק המודרני ^(pywebview^)...
    python -m pip install --quiet pywebview
)

echo הפעלת תוכנת שינוי שם קבצים...
python gui.py

if %ERRORLEVEL% NEQ 0 (
    echo שגיאה בהרצת התוכנה
    pause
)
