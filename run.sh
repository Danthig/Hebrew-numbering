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

# בדיקה אם tkinter מותקן
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]
then
    echo "שגיאה: tkinter לא מותקן"
    echo "התקן ב-Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "התקן ב-macOS: brew install python-tk"
    exit 1
fi

# הרצת הממשק הגרפי
echo "הפעלת תוכנת שינוי שם קבצים..."
python3 gui.py
