"""
תכנון וביצוע שינוי שמות בצורה בטוחה.

עקרונות:
- זיהוי התנגשויות *לפני* הביצוע (שמות יעד כפולים, דריסת קבצים קיימים).
- ביצוע אטומי דו-שלבי: כשיש מעגל/שרשרת (היעד של קובץ אחד הוא המקור של אחר),
  כל הקבצים עוברים תחילה לשמות זמניים ייחודיים ואז לשמות הסופיים —
  כך לא נאבד אף קובץ.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from .sanitizer import is_valid_filename


@dataclass
class RenameItem:
    """פריט בודד בתוכנית שינוי השם."""
    source: Path
    target_name: str
    result: Optional[bool] = None   # None=טרם בוצע, True=הצליח, False=נכשל
    error: Optional[str] = None

    @property
    def target(self) -> Path:
        return self.source.with_name(self.target_name)

    @property
    def is_noop(self) -> bool:
        return self.source.name == self.target_name


@dataclass
class Conflict:
    """תיאור התנגשות שמונעת ביצוע בטוח."""
    item: RenameItem
    reason: str


@dataclass
class RenamePlan:
    """תוכנית שינוי שם מלאה, כולל ההתנגשויות שזוהו."""
    items: List[RenameItem] = field(default_factory=list)
    conflicts: List[Conflict] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    @property
    def actionable_items(self) -> List[RenameItem]:
        """פריטים שאינם no-op ושאינם מעורבים בהתנגשות."""
        conflicting = {id(c.item) for c in self.conflicts}
        return [
            item for item in self.items
            if not item.is_noop and id(item) not in conflicting
        ]


def build_plan(pairs: List[Tuple[Path, str]]) -> RenamePlan:
    """בניית תוכנית מתוך זוגות (מקור, שם-יעד) וזיהוי כל ההתנגשויות.

    התנגשויות שמזוהות:
    - שם יעד לא תקין (תווים אסורים / שם שמור)
    - שני קבצים שונים שממופים לאותו שם יעד
    - שם יעד שכבר תפוס ע"י קובץ קיים שאינו חלק מהתוכנית
    """
    items = [RenameItem(Path(src), name) for src, name in pairs]
    conflicts: List[Conflict] = []

    sources = {item.source.resolve() for item in items}
    target_counts: dict = {}

    for item in items:
        target_counts.setdefault(item.target.resolve(), []).append(item)

    for item in items:
        if item.is_noop:
            continue

        valid, reason = is_valid_filename(item.target_name)
        if not valid:
            conflicts.append(Conflict(item, f"שם יעד לא תקין: {reason}"))
            continue

        resolved_target = item.target.resolve()

        # שני מקורות -> אותו יעד
        if len(target_counts.get(resolved_target, [])) > 1:
            conflicts.append(Conflict(item, "שם היעד משותף ליותר מקובץ אחד"))
            continue

        # היעד כבר קיים בדיסק ואינו אחד מהמקורות שעומדים להשתנות
        if item.target.exists() and resolved_target not in sources:
            conflicts.append(Conflict(item, "כבר קיים קובץ בשם היעד"))
            continue

    return RenamePlan(items=items, conflicts=conflicts)


def _needs_two_phase(items: List[RenameItem]) -> bool:
    """האם יש חפיפה בין קבוצת היעדים לקבוצת המקורות (שרשרת/מעגל)."""
    sources = {item.source.resolve() for item in items}
    targets = {item.target.resolve() for item in items}
    return bool(sources & targets)


def _unique_temp_path(source: Path, index: int) -> Path:
    """יצירת נתיב זמני ייחודי בתוך אותה תיקייה."""
    counter = 0
    while True:
        candidate = source.with_name(f".__hrn_tmp_{index}_{counter}__")
        if not candidate.exists():
            return candidate
        counter += 1


def results_from_plan(plan: RenamePlan) -> List[Tuple[str, str, bool]]:
    """בניית רשימת תוצאות (שם-מקורי, שם-חדש/שגיאה, הצלחה) בסדר הקלט."""
    results = []
    for item in plan.items:
        if item.is_noop or item.result is None:
            continue
        if item.result:
            results.append((item.source.name, item.target_name, True))
        else:
            results.append((item.source.name, item.error or "שגיאה", False))
    return results


def execute_plan(
    plan: RenamePlan,
    progress_cb: Optional[Callable[[int, int, str], None]] = None,
    cancel_check: Optional[Callable[[], bool]] = None,
) -> List[Tuple[str, str, bool]]:
    """ביצוע התוכנית. מתייג כל פריט בתוצאה ומחזיר רשימת תוצאות בסדר הקלט.

    :param progress_cb: פונקציית התקדמות (done, total, current_name)
    :param cancel_check: פונקציה שמחזירה True כדי לעצור באמצע
    """
    # תיוג ההתנגשויות ככישלון מנומק
    for conflict in plan.conflicts:
        conflict.item.result = False
        conflict.item.error = conflict.reason

    items = plan.actionable_items

    if items:
        if _needs_two_phase(items):
            _execute_two_phase(items, progress_cb, cancel_check)
        else:
            _execute_direct(items, progress_cb, cancel_check)

    return results_from_plan(plan)


def _execute_direct(items, progress_cb, cancel_check) -> None:
    total = len(items)
    for done, item in enumerate(items, start=1):
        if cancel_check and cancel_check():
            break
        if progress_cb:
            progress_cb(done, total, item.source.name)
        try:
            item.source.rename(item.target)
            item.result = True
        except Exception as exc:
            item.result = False
            item.error = f"שגיאה: {exc}"


def _execute_two_phase(items, progress_cb, cancel_check) -> None:
    """שלב א': כל המקורות -> שמות זמניים. שלב ב': זמניים -> שמות סופיים."""
    total = len(items)
    staged: List[Tuple[RenameItem, Path]] = []

    # שלב א'
    for index, item in enumerate(items):
        if cancel_check and cancel_check():
            _rollback_staging(staged)
            return
        temp = _unique_temp_path(item.source, index)
        try:
            item.source.rename(temp)
            staged.append((item, temp))
        except Exception as exc:
            item.result = False
            item.error = f"שגיאה (שלב א'): {exc}"

    # שלב ב'
    for done, (item, temp) in enumerate(staged, start=1):
        if progress_cb:
            progress_cb(done, total, item.source.name)
        try:
            temp.rename(item.target)
            item.result = True
        except Exception as exc:
            try:
                temp.rename(item.source)
            except Exception:
                pass
            item.result = False
            item.error = f"שגיאה (שלב ב'): {exc}"


def _rollback_staging(staged: List[Tuple[RenameItem, Path]]) -> None:
    for item, temp in staged:
        try:
            temp.rename(item.source)
        except Exception:
            pass
