#!/bin/bash
# תוכנת שינוי שם קבצים - Linux/Mac Shell Script

# בדיקה אם Python מותקן
if ! command -v python3 &> /dev/null
then
    echo "שגיאה: Python 3 לא מותקן"
    echo "התקן ב-Ubuntu/Debian: sudo apt-get install python3"
    echo "התקן ב-macOS: brew install python3"
    exit 1
fi

# התקנת הממשק המודרני (pywebview) אם חסר — יש נפילה אוטומטית ל-tkinter
if ! python3 -c "import webview" 2>/dev/null
then
    echo "מתקין את הממשק המודרני (pywebview)..."
    python3 -m pip install --quiet pywebview 2>/dev/null
fi

# גיבוי: ודא ש-tkinter זמין למקרה שאין pywebview
if ! python3 -c "import webview" 2>/dev/null && ! python3 -c "import tkinter" 2>/dev/null
then
    echo "שגיאה: לא נמצאו pywebview או tkinter"
    echo "התקן ב-Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "התקן ב-macOS: brew install python-tk"
    exit 1
fi

# הרצת הממשק הגרפי
echo "הפעלת תוכנת שינוי שם קבצים..."
python3 gui.py
