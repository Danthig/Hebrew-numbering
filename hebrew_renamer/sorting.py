"""
מיון קבצים — מיון טבעי (1, 2, 10 ולא 1, 10, 2) ואסטרטגיות מיון נוספות:
שם, תאריך שינוי, גודל, סוג (סיומת). ללא תלות בספריות חיצוניות.
"""

import re
from pathlib import Path
from typing import Callable, Iterable, List, Optional

_NUM_SPLIT = re.compile(r'(\d+)')


def natural_sort_key(value) -> list:
    """מפתח מיון טבעי — מספרים מושווים כמספרים, לא כטקסט."""
    return [
        int(part) if part.isdigit() else part.lower()
        for part in _NUM_SPLIT.split(str(value))
    ]


def natsorted(values: Iterable, key: Optional[Callable] = None) -> list:
    """מיון טבעי, תחליף קל ל-natsort."""
    if key is None:
        return sorted(values, key=natural_sort_key)
    return sorted(values, key=lambda item: natural_sort_key(key(item)))


# אסטרטגיות מיון נתמכות
SORT_STRATEGIES = ('name', 'natural', 'date', 'size', 'type')


def sort_files(
    files: List[Path],
    strategy: str = 'natural',
    reverse: bool = False,
) -> List[Path]:
    """מיון רשימת קבצים לפי אסטרטגיה נבחרת.

    :param strategy: name | natural | date | size | type
    :param reverse: סדר יורד
    """
    if strategy == 'natural':
        result = natsorted(files, key=lambda p: p.name)
    elif strategy == 'name':
        result = sorted(files, key=lambda p: p.name.lower())
    elif strategy == 'date':
        result = sorted(files, key=_safe_mtime)
    elif strategy == 'size':
        result = sorted(files, key=_safe_size)
    elif strategy == 'type':
        # מיון לפי סיומת, ובתוך אותה סיומת — מיון טבעי
        result = sorted(
            files,
            key=lambda p: (p.suffix.lower(), natural_sort_key(p.name)),
        )
    else:
        raise ValueError(f"אסטרטגיית מיון לא מוכרת: {strategy}")

    return list(reversed(result)) if reverse else result


def _safe_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def _safe_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0
