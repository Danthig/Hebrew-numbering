"""
ניקוי ואימות שמות קבצים — מניעת תווים אסורים, שמות שמורים ואורך נתיב חורג.
מטפל בכללי Windows (המחמירים ביותר) כדי שהתוצאה תקפה בכל מערכת.
"""

import re
from pathlib import Path
from typing import Optional, Tuple

# תווים אסורים בשמות קבצים ב-Windows
ILLEGAL_CHARS = '<>:"/\\|?*'
ILLEGAL_PATTERN = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

# שמות שמורים ב-Windows (ללא תלות בסיומת)
RESERVED_NAMES = {
    'CON', 'PRN', 'AUX', 'NUL',
    *(f'COM{i}' for i in range(1, 10)),
    *(f'LPT{i}' for i in range(1, 10)),
}

MAX_FILENAME_LENGTH = 255   # אורך מרכיב בודד
MAX_PATH_LENGTH = 259       # אורך נתיב מלא ב-Windows (ללא \\?\)


def sanitize_filename(name: str, replacement: str = '_') -> str:
    """החזרת שם קובץ תקין: החלפת תווים אסורים, טיפול בשמות שמורים
    והסרת רווחים/נקודות בסוף (אסורים ב-Windows)."""
    if not name:
        return replacement

    # החלפת תווים אסורים ותווי בקרה
    sanitized = ILLEGAL_PATTERN.sub(replacement, name)

    # הסרת רווחים ונקודות בסוף השם (Windows חותך אותם בשקט)
    sanitized = sanitized.rstrip(' .')

    if not sanitized:
        sanitized = replacement

    # טיפול בשמות שמורים — מוסיפים קו תחתון
    stem = sanitized.split('.')[0]
    if stem.upper() in RESERVED_NAMES:
        sanitized = '_' + sanitized

    # קיצור אם ארוך מדי, תוך שמירת הסיומת
    if len(sanitized) > MAX_FILENAME_LENGTH:
        path = Path(sanitized)
        suffix = path.suffix
        stem = path.stem[: MAX_FILENAME_LENGTH - len(suffix)]
        sanitized = stem + suffix

    return sanitized


def is_valid_filename(name: str) -> Tuple[bool, Optional[str]]:
    """בדיקה אם שם הקובץ תקין. מחזיר (תקין, סיבת פסילה)."""
    if not name or not name.strip():
        return False, "שם קובץ ריק"

    match = ILLEGAL_PATTERN.search(name)
    if match:
        char = match.group()
        readable = repr(char) if char.isprintable() else f"תו בקרה ({ord(char)})"
        return False, f"תו אסור בשם הקובץ: {readable}"

    if name != name.rstrip(' .'):
        return False, "שם קובץ אינו יכול להסתיים ברווח או בנקודה"

    stem = name.split('.')[0]
    if stem.upper() in RESERVED_NAMES:
        return False, f"'{stem}' הוא שם שמור במערכת"

    if len(name) > MAX_FILENAME_LENGTH:
        return False, f"שם הקובץ ארוך מדי (מעל {MAX_FILENAME_LENGTH} תווים)"

    return True, None


def is_path_too_long(path: Path) -> bool:
    """בדיקה אם הנתיב המלא חורג ממגבלת Windows."""
    return len(str(path)) > MAX_PATH_LENGTH
