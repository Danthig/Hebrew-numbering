# תוכנת שינוי שם קבצים - Hebrew File Renamer

תוכנה מוקדשת לשינוי שם של קבצים מרובים עם תמיכה מלאה בממספור עברי (א' ב' ג'... י"ג י"ד וכו').

**A dedicated tool for batch renaming files with full Hebrew numbering support (א' ב' ג'... י"ג י"ד etc.)**

---

## ✨ תכונות / Features

- 📁 **שינוי שם מרובים** / Batch file renaming
- 🇮🇱 **ממספור עברי** / Full Hebrew numbering (א' ב' ג'... עד 9999)
- 🔢 **מספור מספרי** / Numeric numbering with optional dots (1. 2. 3. or 1 2 3)
- 📊 **מיון נכון** / Smart numeric sorting (1, 2, 10, 20, 100 - not 1, 10, 100, 2)
- 👀 **תצוגה חיה** / Live preview before renaming
- 🎯 **קדימה מותאמת** / Customizable prefix and separator
- 🖥️ **ממשק גרפי** / Intuitive GUI with Hebrew RTL support
- 📦 **ניידות מלאה** / Fully portable - no installation required

---

## 🚀 התחלה מהירה / Quick Start

### אפליקציה ניידה (Windows)
פשוט הורד והרץ את `Hebrew-numbering.exe` - לא צריך התקנה!

```bash
Hebrew-numbering.exe
```

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
    separator="_",
    start_number=1
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
