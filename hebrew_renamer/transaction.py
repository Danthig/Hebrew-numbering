"""
יומן פעולות ו-Undo/Redo.

כל ריצת שינוי-שם נשמרת כטרנזקציה ביומן קבוע (JSON) בתיקיית הבית של המשתמש,
כך שאפשר לבטל גם לאחר סגירת התוכנה. כל טרנזקציה מכילה את כל זוגות
(שם-מקורי -> שם-חדש) שבוצעו בהצלחה.
"""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable, List, Optional, Tuple

HISTORY_DIR = Path.home() / '.hebrew_renamer'
HISTORY_FILE = HISTORY_DIR / 'history.json'
MAX_HISTORY = 100


@dataclass
class Operation:
    """פעולת שינוי-שם בודדת שהצליחה."""
    original_path: str
    new_path: str


@dataclass
class Transaction:
    """אוסף פעולות מריצה אחת."""
    transaction_id: str
    timestamp: str
    directory: str
    operations: List[Operation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'transaction_id': self.transaction_id,
            'timestamp': self.timestamp,
            'directory': self.directory,
            'operations': [asdict(op) for op in self.operations],
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        return cls(
            transaction_id=data['transaction_id'],
            timestamp=data['timestamp'],
            directory=data['directory'],
            operations=[Operation(**op) for op in data.get('operations', [])],
        )


class HistoryJournal:
    """ניהול יומן הטרנזקציות הקבוע."""

    def __init__(self, history_file: Path = HISTORY_FILE):
        self.history_file = Path(history_file)

    def _load(self) -> List[dict]:
        if not self.history_file.exists():
            return []
        try:
            with open(self.history_file, 'r', encoding='utf-8') as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self, data: List[dict]) -> None:
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as fh:
            json.dump(data[-MAX_HISTORY:], fh, ensure_ascii=False, indent=2)

    def record(self, transaction: Transaction) -> None:
        """הוספת טרנזקציה ליומן."""
        if not transaction.operations:
            return
        data = self._load()
        data.append(transaction.to_dict())
        self._save(data)

    def all_transactions(self) -> List[Transaction]:
        return [Transaction.from_dict(item) for item in self._load()]

    def last_transaction(self) -> Optional[Transaction]:
        data = self._load()
        if not data:
            return None
        return Transaction.from_dict(data[-1])

    def pop_last(self) -> Optional[Transaction]:
        """הוצאת הטרנזקציה האחרונה מהיומן והחזרתה."""
        data = self._load()
        if not data:
            return None
        last = data.pop()
        self._save(data)
        return Transaction.from_dict(last)


def undo_transaction(
    transaction: Transaction,
    progress_cb: Optional[Callable[[int, int, str], None]] = None,
) -> List[Tuple[str, str, bool]]:
    """ביטול טרנזקציה — החזרת כל קובץ לשמו המקורי, בצורה אטומית דו-שלבית."""
    # ייבוא מקומי כדי להימנע מתלות מעגלית
    from .planner import RenamePlan, RenameItem, execute_plan

    items = []
    for op in transaction.operations:
        new_path = Path(op.new_path)
        original_path = Path(op.original_path)
        if new_path.exists():
            items.append(RenameItem(new_path, original_path.name))

    plan = RenamePlan(items=items, conflicts=[])
    return execute_plan(plan, progress_cb=progress_cb)
