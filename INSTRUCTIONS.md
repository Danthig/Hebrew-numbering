diff --git a/INSTRUCTIONS.md b/INSTRUCTIONS.md
index 0ba90157c57cd0f95a7ec1024ccd4fdb2e1cf507..8f60bc4ab9fb7090f56dd7bf5d1a8032cdf80ea9 100644
--- a/INSTRUCTIONS.md
+++ b/INSTRUCTIONS.md
@@ -1,36 +1,59 @@
 תוכנת שינוי שם קבצים - הוראות שימוש
 ========================================
 
 ## מהי התוכנה?
 
 תוכנה זו מאפשרת לשנות שם של קבצים מרובים בבת-אחת בדרכים שונות:
 - מספור בעברית (א' ב' ג' וכו')
 - מספור רגיל (1 2 3 וכו')
 - הוספת התחילית משותפת
 - בחירה בתו הפרדה
 
+
+## איפה קובץ ה-EXE?
+
+קובץ ההפעלה נמצא בתיקיית הפרויקט הראשית בשם:
+
+```text
+שינוי_שם_קבצים.exe
+```
+
+אם העתקת רק את שלושת קובצי הקוד (`gui.py`, `file_renamer.py`, `README.md`) ל-VS Code, לא העתקת את קובץ ה-EXE.
+
+כדי להריץ מהקוד ב-CMD, פתח את התיקייה שבה נמצאים `gui.py` ו-`file_renamer.py` והריץ:
+
+```bat
+python gui.py
+```
+
+כדי לבנות EXE מעודכן ב-Windows, הרץ:
+
+```bat
+build_exe.bat
+```
+
 ## דרישות מוקדמות:
 - Python 3.7 ומעלה
 - tkinter (בדרך כלל כלול ב-Python)
 
 ## התקנה ראשונה:
 
 ### Windows:
 1. הורד Python מ- https://www.python.org
    * בחשוב: בחר "Add Python to PATH" במהלך ההתקנה
 2. פתח Command Prompt או PowerShell בתיקייה של התוכנה
 3. הרץ: `python gui.py` או לחץ על `run.bat`
 
 ### Linux/macOS:
 1. בדוק אם Python 3 מותקן: `python3 --version`
 2. בדוק אם tkinter מותקן:
    - Ubuntu/Debian: `sudo apt-get install python3-tk`
    - macOS: `brew install python-tk`
 3. הרץ: `python3 gui.py` או `bash run.sh`
 
 ## שימוש בממשק הגרפי:
 
 ### שלב 1: בחירת תיקייה
 - לחץ על "בחר תיקייה"
 - בחר את התיקייה שמכילה את הקבצים שברצונך להינם
 
