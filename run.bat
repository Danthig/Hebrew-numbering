@echo off
chcp 65001 >nul
REM תוכנת שינוי שם קבצים - Windows Batch Script

REM בדיקה אם Python מותקן
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo שגיאה: Python לא מותקן או לא נמצא ב-PATH
    echo אנא הורד Python מ- https://www.python.org
    pause
    exit /b 1
)

REM הרצת הממשק הגרפי
echo הפעלת תוכנת שינוי שם קבצים...
python gui.py

if %ERRORLEVEL% NEQ 0 (
    echo שגיאה בהרצת התוכנה
    pause
)
