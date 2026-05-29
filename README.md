diff --git a/README.md b/README.md
index 36df9e236faa93651087b375cce92d61746a5a01..c426087b842735e1da37e8cf85deecd399fa0bab 100644
--- a/README.md
+++ b/README.md
@@ -1,113 +1,134 @@
 # תוכנת שינוי שם קבצים - Hebrew File Renamer
 
 תוכנה מוקדשת לשינוי שם של קבצים מרובים עם תמיכה מלאה בממספור עברי (א' ב' ג'... י"ג י"ד וכו').
 
 **A dedicated tool for batch renaming files with full Hebrew numbering support (א' ב' ג'... י"ג י"ד etc.)**
 
 ---
 
 ## ✨ תכונות / Features
 
 - 📁 **שינוי שם מרובים** / Batch file renaming
-- 🇮🇱 **ממספור עברי** / Full Hebrew numbering (א' ב' ג'... עד 9999)
-- 🔢 **מספור מספרי** / Numeric numbering with optional dots (1. 2. 3. or 1 2 3)
+- 🇮🇱 **ממספור עברי** / Full Hebrew numbering, כולל מספור מעל אלף בשתי צורות (א' א' או אלף א')
+- 🔢 **מספור מספרי** / Numeric numbering with optional dots and zero padding (1, 01, 001)
 - 📊 **מיון נכון** / Smart numeric sorting (1, 2, 10, 20, 100 - not 1, 10, 100, 2)
 - 👀 **תצוגה חיה** / Live preview before renaming
-- 🎯 **קדימה מותאמת** / Customizable prefix and separator
+- 🎯 **תחילית מותאמת** / Customizable prefix and separator
+- ➕ **הוספה או החלפה** / Replace the original name or add numbering before/after it
+- 📂 **בחירת קבצים ותיקיות** / Select folders, individual files, and optionally include subfolders
 - 🖥️ **ממשק גרפי** / Intuitive GUI with Hebrew RTL support
 - 📦 **ניידות מלאה** / Fully portable - no installation required
 
 ---
 
 ## 🚀 התחלה מהירה / Quick Start
 
 ### אפליקציה ניידה (Windows)
-פשוט הורד והרץ את `Hebrew-numbering.exe` - לא צריך התקנה!
+פשוט הורד והרץ את `שינוי_שם_קבצים.exe` - לא צריך התקנה!
 
 ```bash
-Hebrew-numbering.exe
+שינוי_שם_קבצים.exe
 ```
 
+
+### קובץ EXE / Windows executable
+קובץ ההפעלה נמצא בתיקיית הפרויקט הראשית בשם `שינוי_שם_קבצים.exe`. אם העתקת רק את `gui.py`, `file_renamer.py` ו-`README.md`, לא העתקת את קובץ ההפעלה.
+
+כדי לבנות EXE מעודכן ב-Windows אחרי שינוי בקוד, הרץ:
+
+```bat
+build_exe.bat
+```
+
+הסקריפט יתקין PyInstaller במידת הצורך, יבנה קובץ חדש, ויעתיק אותו בחזרה לתיקיית הפרויקט בשם `שינוי_שם_קבצים.exe`.
+
 ### או Python
 ```bash
 # התקנה / Install dependencies
 pip install -r requirements.txt
 
 # הרצה / Run
 python gui.py
 ```
 
 ## דוגמאות:
 
 ### דוגמה 1: מספור בעברית עם גרש
 - קובץ1.txt → קובץ_א'.txt
 - קובץ2.txt → קובץ_ב'.txt
 - קובץ3.txt → קובץ_ג'.txt
 
 ### דוגמה 2: מספור עם נקודה
 - תמונה1.jpg → תמונה_1.jpg
 - תמונה2.jpg → תמונה_2.jpg
 
 ### דוגמה 3: מספור בעברית ללא גרש
 - מסמך1.pdf → מסמך_א.pdf
 - מסמך2.pdf → מסמך_ב.pdf
 
 ## שימוש בקוד:
 
 ```python
 from file_renamer import FileRenamer, HebrewNumbering
 
 # יצירת renamer object
 renamer = FileRenamer("C:/my/folder")
 
 # קבלת רשימת קבצים
 files = renamer.get_files()
 
 # שינוי שם עם מספור בעברית
 results = renamer.rename_files(
     files,
     prefix="קובץ",
     numbering_type="hebrew",  # hebrew, numeric, numeric_no_dot
     with_geresh=True,  # True או False
+    thousands_style="letters",  # letters או words
+    numeric_padding=0,  # 0, 2 (01), או 3 (001)
     separator="_",
-    start_number=1
+    start_number=1,
+    rename_mode="replace"  # replace, prepend, append
 )
 
 # הדפסת תוצאות
 for old_name, new_name, success in results:
     status = "✓" if success else "✗"
     print(f"{status} {old_name} → {new_name}")
 ```
 
 ## מספור בעברית:
 
 המחלקה HebrewNumbering תומכת בהמרת מספרים לעברית:
 
 ```python
 from file_renamer import HebrewNumbering
 
 # עם גרש/גרשיים
 print(HebrewNumbering.number_to_hebrew(1, True))   # א'
 print(HebrewNumbering.number_to_hebrew(15, True))  # ט"ו
 
 # בלי גרש/גרשיים
 print(HebrewNumbering.number_to_hebrew(1, False))  # א
 print(HebrewNumbering.number_to_hebrew(15, False)) # טו
+
+# מעל אלף
+print(HebrewNumbering.number_to_hebrew(1001, True, "letters")) # א' א'
+print(HebrewNumbering.number_to_hebrew(1001, True, "words"))   # אלף א'
 ```
 
 ## הערות חשובות:
 
 1. **גיבוי** - מומלץ לגבות את הקבצים לפני ביצוע שינוי שם!
 2. **דוחק** - כל קובץ שיש לו כבר את השם החדש לא ישתנה.
 3. **הרשאות** - ודא שיש לך הרשאות לשינוי קבצים בתיקייה.
 
 ## תמיכה:
 
 במידה ויש בעיה, בדוק:
 - שהתיקייה קיימת ויש בה קבצים
 - שיש לך הרשאות כתיבה בתיקייה
 - שלא קיימים כבר קבצים עם אותו שם 
 
 ## רישיון:
 
 MIT License - משוחרר לשימוש חופשי.
