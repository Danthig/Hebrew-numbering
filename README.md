# תוכנת שינוי שם קבצים - Hebrew File Renamer

תוכנה לשינוי שם של קבצים מרובים עם תמיכה במספור עברי (גימטריה), במספור מספרי, ובמספור עם אפסים מובילים — כולל **לשון נקייה**, **Undo**, ושינוי שם **אטומי ובטוח**.

**A batch file renamer with Hebrew (gematria) numbering, "clean language" substitutions, full undo, and atomic-safe renaming.**

---

## ✨ תכונות / Features

- 📁 **שינוי שם מרובים** / Batch file renaming
- 🇮🇱 **מספור עברי עד 999,999** / Hebrew numbering up to 999,999
  - סגנון אותיות: `א' א'`, `ה' תשע"ח`
  - סגנון מילים: `אלף א'`, `אלפיים א'`
- 🕊️ **לשון נקייה** / "Clean language" — החלפת צירופים לא רצויים:
  - `שד` → `דש` (304, פעיל כברירת מחדל)
  - אופציונלי: `רע` → `ער` (270), `שמד` → `דמש` (344)
  - משלים את ההימנעות הקיימת משם ה': `15 → טו`, `16 → טז`
- 🔢 **מספור מספרי עם אפסים מובילים** / Numeric zero padding (`01`, `001`)
- ↩️ **Undo מלא** / Full undo — ביטול הריצה האחרונה, גם אחרי סגירת התוכנה
- 🛡️ **שינוי אטומי בטוח** / Atomic two-phase rename — פותר שרשראות/מעגלים (`1→2, 2→3`) בלי לאבד קבצים
- 🚫 **זיהוי התנגשויות** / Conflict detection — שמות כפולים, קבצים קיימים, תווים אסורים
- 📊 **מיון חכם** / Smart sorting — טבעי, שם, תאריך, גודל, סוג
- 👀 **תצוגה חיה** / Live preview עם סימון התנגשויות באדום
- ⏳ **התקדמות וביטול** / Progress bar + cancel — ה-GUI לא קופא
- 💾 **שמירת הגדרות** / Settings persisted between runs
- 🖥️ **ממשק גרפי + CLI** / Both Tkinter GUI and full command-line interface

---

## 🚀 התחלה מהירה / Quick Start

### ממשק גרפי / GUI

```bash
python gui.py
```

ב-Windows אפשר גם דרך `run.bat`.

### שורת פקודה / CLI

```bash
# תצוגה מקדימה בלבד (לא משנה כלום)
python -m hebrew_renamer ./photos --prefix תמונה --type hebrew --dry-run

# מספור עברי בלשון נקייה
python -m hebrew_renamer ./photos --type hebrew --clean-language

# מספור מספרי עם אפסים מובילים, ללא אישור אינטראקטיבי
python -m hebrew_renamer ./docs --type numeric --padding 3 --yes

# ביטול הריצה האחרונה
python -m hebrew_renamer --undo
```

אפשרויות עיקריות: `--prefix`, `--separator`, `--type {hebrew,numeric,numeric_no_dot}`,
`--start`, `--padding`, `--no-geresh`, `--thousands {letters,words}`,
`--mode {replace,prepend,append}`, `--clean-language`, `--clean-extra`,
`--recursive`, `--sort`, `--dry-run`, `--undo`, `--yes`.

---

## 🧩 ארכיטקטורה / Architecture

הקוד מאורגן בשכבות תחת החבילה `hebrew_renamer`:

| מודול | תפקיד |
|-------|-------|
| `gematria.py` | מנוע מספור עברי (לשון נקייה, הימנעות משם ה', ניתוח הפוך) |
| `sanitizer.py` | ניקוי ואימות שמות קבצים (תווים אסורים, שמות שמורים, אורך) |
| `sorting.py` | מיון טבעי ואסטרטגיות מיון |
| `planner.py` | תכנון וביצוע אטומי בטוח + זיהוי התנגשויות |
| `transaction.py` | יומן פעולות ו-Undo |
| `renamer.py` | ה-API הראשי |
| `cli.py` / `gui.py` | חזיתות שורת-פקודה וגרפית |

`file_renamer.py` נשאר כשכבת תאימות לאחור.

---

## שימוש בקוד / Library usage

```python
from hebrew_renamer import FileRenamer, HebrewNumbering

# מספור בלשון נקייה
print(HebrewNumbering.number_to_hebrew(304, clean_language=True))  # ד"ש
print(HebrewNumbering.number_to_hebrew(304))                       # ש"ד

renamer = FileRenamer("C:/my/folder")
files = renamer.get_files(sort_strategy="natural")

results = renamer.rename_files(
    files,
    prefix="קובץ",
    numbering_type="hebrew",      # hebrew, numeric, numeric_no_dot
    with_geresh=True,
    thousands_style="letters",    # letters / words
    clean_language=True,          # שד→דש
    rename_mode="replace",        # replace, prepend, append
)

renamer.undo_last()  # ביטול
```

---

## הערות חשובות / Notes

1. השינוי בטוח (אטומי) ומתועד — אפשר תמיד לבטל עם **Undo**.
2. קובץ לא יידרס: שם יעד שכבר תפוס מסומן כהתנגשות ולא מבוצע.
3. תווים אסורים בשמות (`< > : " / \ | ? *`) ושמות שמורים מזוהים מראש.

## בדיקות / Tests

```bash
python -m unittest discover -s tests
```

## רישיון / License

MIT License
