# תוכנת שינוי שם קבצים - Hebrew File Renamer

תוכנה לשינוי שם של קבצים מרובים עם תמיכה במספור עברי, במספור מספרי רגיל, ובמספור מספרי עם אפסים מובילים.

**A batch file renamer with Hebrew numbering, regular numeric numbering, and zero-padded numeric numbering.**

---

## ✨ תכונות / Features

- 📁 **שינוי שם מרובים** / Batch file renaming
- 🇮🇱 **מספור עברי מעל אלף** / Hebrew numbering above 1,000 up to 999,999
  - סגנון אותיות: `א' א'`, `ה' תשע"ח`
  - סגנון מילים: `אלף א'`, `אלפיים א'`
- 🔢 **מספור מספרי עם אפסים מובילים** / Numeric zero padding
  - ללא אפסים: `1`, `2`, `3`, `10`, `11`
  - אפס אחד: `01`, `02`, `03`, `10`, `11`
  - שני אפסים: `001`, `002`, `003`, `010`, `011`, `100`, `101`
- 📊 **מיון טבעי נכון** / Smart numeric sorting (`1, 2, 10` instead of `1, 10, 2`)
- 👀 **תצוגה חיה** / Live preview before renaming
- 🎯 **תחילית ותו הפרדה מותאמים** / Customizable prefix and separator
- ➕ **החלפה או הוספה** / Replace the original name or add numbering before/after it
- 📂 **בחירת תיקייה או קבצים** / Select folders, individual files, and optionally include subfolders
- 🖥️ **ממשק גרפי** / Tkinter GUI with Hebrew labels

---

## 🚀 התחלה מהירה / Quick Start

### הרצה עם Python

```bash
python gui.py
```

### Windows

אפשר להריץ גם דרך:

```bat
run.bat
```

או לפתוח את קובץ ההפעלה אם הוא קיים בתיקיית הפרויקט:

```text
שינוי_שם_קבצים.exe
```

---

## שימוש בממשק הגרפי

1. בחר תיקייה או קבצים.
2. בחר סוג מספור:
   - `עברית`
   - `1.`
   - `1`
3. למספור עברי מעל אלף, בחר סגנון אלפים:
   - `אותיות (א' א')`
   - `מילים (אלף א')`
4. למספור מספרי עם אפסים מובילים, בחר:
   - `ללא (1, 2, 3)`
   - `0 אחד (01, 02)`
   - `00 שניים (001, 002)`
5. בדוק את התצוגה המקדימה ולחץ על **בצע שינוי שם!**.

---

## שימוש בקוד

```python
from file_renamer import FileRenamer, HebrewNumbering

renamer = FileRenamer("C:/my/folder")
files = renamer.get_files()

results = renamer.rename_files(
    files,
    prefix="קובץ",
    numbering_type="hebrew",      # hebrew, numeric, numeric_no_dot
    with_geresh=True,
    thousands_style="letters",    # letters או words
    numeric_padding=0,             # 0, 2 עבור 01, או 3 עבור 001
    separator="_",
    start_number=1,
    rename_mode="replace",        # replace, prepend, append
)

for old_name, new_name, success in results:
    status = "✓" if success else "✗"
    print(f"{status} {old_name} → {new_name}")
```

---

## דוגמאות מספור

```python
from file_renamer import FileRenamer, HebrewNumbering

print(HebrewNumbering.number_to_hebrew(1001, True, "letters"))  # א' א'
print(HebrewNumbering.number_to_hebrew(1001, True, "words"))    # אלף א'
print(HebrewNumbering.number_to_hebrew(5778, True, "letters"))  # ה' תשע"ח

print(FileRenamer.format_number(1, "numeric_no_dot", numeric_padding=2))   # 01
print(FileRenamer.format_number(10, "numeric_no_dot", numeric_padding=2))  # 10
print(FileRenamer.format_number(1, "numeric_no_dot", numeric_padding=3))   # 001
print(FileRenamer.format_number(10, "numeric_no_dot", numeric_padding=3))  # 010
print(FileRenamer.format_number(100, "numeric_no_dot", numeric_padding=3)) # 100
```

---

## הערות חשובות

1. מומלץ לגבות את הקבצים לפני שינוי שם מרובה.
2. קובץ לא ישונה אם כבר קיים קובץ אחר בשם החדש.
3. ודא שיש הרשאות כתיבה בתיקייה.

## רישיון

MIT License
