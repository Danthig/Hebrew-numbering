"""
שכבת תאימות לאחור.

הלוגיקה עברה לחבילה המודולרית ``hebrew_renamer``. קובץ זה נשאר כדי
לשמור על תאימות עם ``import`` קיימים (gui.py, בדיקות, סקריפטים של משתמשים).

מומלץ לעבור לייבוא ישיר:
    from hebrew_renamer import FileRenamer, HebrewNumbering
"""

from hebrew_renamer.gematria import HebrewNumbering
from hebrew_renamer.renamer import FileRenamer
from hebrew_renamer.sorting import natural_sort_key, natsorted

__all__ = ['HebrewNumbering', 'FileRenamer', 'natural_sort_key', 'natsorted']


def main():
    import sys
    from hebrew_renamer.cli import run

    # תאימות לאחור: שימוש פשוט "python file_renamer.py <dir>"
    if len(sys.argv) == 2 and not sys.argv[1].startswith('-'):
        return run([sys.argv[1], '--prefix', 'קובץ', '--type', 'hebrew', '--yes'])
    return run(sys.argv[1:])


if __name__ == '__main__':
    main()
