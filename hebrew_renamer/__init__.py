"""
Hebrew File Renamer — שינוי שמות קבצים מרובים עם מספור עברי.

ארכיטקטורת שכבות:
- gematria   : מנוע מספור עברי (כולל לשון נקייה והימנעות משם ה')
- sanitizer  : ניקוי ואימות שמות קבצים
- sorting    : מיון טבעי ואסטרטגיות מיון
- planner    : תכנון וביצוע אטומי בטוח עם זיהוי התנגשויות
- transaction: יומן פעולות ו-Undo/Redo
- renamer    : ה-API הראשי המחבר את הכל
"""

from .gematria import HebrewNumbering
from .renamer import FileRenamer
from .sorting import natsorted, natural_sort_key, sort_files, SORT_STRATEGIES
from .sanitizer import sanitize_filename, is_valid_filename
from .planner import RenamePlan, RenameItem, build_plan, execute_plan
from .transaction import HistoryJournal, Transaction, undo_transaction

__version__ = '2.0.0'

__all__ = [
    'HebrewNumbering',
    'FileRenamer',
    'natsorted',
    'natural_sort_key',
    'sort_files',
    'SORT_STRATEGIES',
    'sanitize_filename',
    'is_valid_filename',
    'RenamePlan',
    'RenameItem',
    'build_plan',
    'execute_plan',
    'HistoryJournal',
    'Transaction',
    'undo_transaction',
    '__version__',
]
