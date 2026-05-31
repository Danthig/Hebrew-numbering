"""
ה-API הראשי לשינוי שמות קבצים — מחבר בין מנוע הגימטריה, המיון,
המתכנן הבטוח ויומן ה-Undo.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .gematria import HebrewNumbering
from .sorting import natsorted, sort_files
from .planner import RenameItem, RenamePlan, build_plan, execute_plan
from .transaction import (
    HistoryJournal,
    Operation,
    Transaction,
    undo_transaction,
)


class FileRenamer:
    """ניהול שינוי שמות קבצים עם מספור עברי/מספרי, בטיחות ו-Undo."""

    def __init__(self, directory: str, journal: Optional[HistoryJournal] = None):
        self.directory = Path(directory)
        if not self.directory.exists():
            raise ValueError(f"הנתיב '{directory}' לא קיים")
        self.journal = journal or HistoryJournal()

    # ------------------------------------------------------------------ #
    # איסוף קבצים
    # ------------------------------------------------------------------ #
    def get_files(
        self,
        extensions: Optional[List[str]] = None,
        recursive: bool = False,
        sort_strategy: str = 'natural',
    ) -> List[Path]:
        """קבלת רשימת קבצים מהתיקייה, ממוינת."""
        if self.directory.is_file():
            return [self.directory]

        glob_method = self.directory.rglob if recursive else self.directory.glob

        if extensions is None:
            files = [f for f in glob_method('*') if f.is_file()]
        else:
            files = []
            for ext in extensions:
                pattern = f"*.{ext.lstrip('.')}"
                files.extend(f for f in glob_method(pattern) if f.is_file())

        return sort_files(files, strategy=sort_strategy)

    @staticmethod
    def get_selected_files(
        paths: List[str],
        recursive: bool = False,
        sort_strategy: str = 'natural',
    ) -> List[Path]:
        """קבלת קבצים מרשימת נתיבים (קבצים ו/או תיקיות)."""
        files: List[Path] = []
        for selected_path in paths:
            path = Path(selected_path)
            if path.is_file():
                files.append(path)
            elif path.is_dir():
                files.extend(
                    FileRenamer(str(path)).get_files(recursive=recursive)
                )
        return sort_files(files, strategy=sort_strategy)

    # ------------------------------------------------------------------ #
    # בניית שמות
    # ------------------------------------------------------------------ #
    @staticmethod
    def format_number(
        number: int,
        numbering_type: str = 'hebrew',
        with_geresh: bool = True,
        thousands_style: str = 'letters',
        numeric_padding: int = 0,
        clean_language: bool = False,
        clean_substitutions: Optional[Dict[str, str]] = None,
    ) -> str:
        """יצירת מחרוזת המספור לפי הסוג הנבחר."""
        if numbering_type == 'hebrew':
            return HebrewNumbering.number_to_hebrew(
                number,
                with_geresh=with_geresh,
                thousands_style=thousands_style,
                clean_language=clean_language,
                clean_substitutions=clean_substitutions,
            )

        number_str = str(number).zfill(numeric_padding) if numeric_padding else str(number)

        if numbering_type == 'numeric':
            return number_str + '.'
        return number_str

    @staticmethod
    def build_new_name(
        file_path: Path,
        number_str: str,
        prefix: str = '',
        separator: str = '_',
        rename_mode: str = 'replace',
    ) -> str:
        """בניית שם קובץ חדש מתחילית, מספר ומצב השינוי."""
        file_path = Path(file_path)
        extension = file_path.suffix
        stem = file_path.stem

        label = f"{prefix}{separator}{number_str}" if prefix else number_str

        if rename_mode == 'prepend':
            new_stem = f"{label}{separator}{stem}"
        elif rename_mode == 'append':
            new_stem = f"{stem}{separator}{label}"
        else:
            new_stem = label

        return f"{new_stem}{extension}"

    # ------------------------------------------------------------------ #
    # תכנון ותצוגה מקדימה
    # ------------------------------------------------------------------ #
    def build_plan(
        self,
        files: List[Path],
        prefix: str = '',
        numbering_type: str = 'hebrew',
        with_geresh: bool = True,
        separator: str = '_',
        start_number: int = 1,
        thousands_style: str = 'letters',
        numeric_padding: int = 0,
        rename_mode: str = 'replace',
        clean_language: bool = False,
        clean_substitutions: Optional[Dict[str, str]] = None,
    ) -> RenamePlan:
        """בניית תוכנית שינוי שם (כולל זיהוי התנגשויות) ללא ביצוע."""
        pairs: List[Tuple[Path, str]] = []
        for idx, file_path in enumerate(files, start=start_number):
            file_path = Path(file_path)
            number_str = self.format_number(
                idx,
                numbering_type=numbering_type,
                with_geresh=with_geresh,
                thousands_style=thousands_style,
                numeric_padding=numeric_padding,
                clean_language=clean_language,
                clean_substitutions=clean_substitutions,
            )
            new_name = self.build_new_name(
                file_path,
                number_str,
                prefix=prefix,
                separator=separator,
                rename_mode=rename_mode,
            )
            pairs.append((file_path, new_name))

        return build_plan(pairs)

    def preview(self, files: List[Path], **kwargs) -> List[Tuple[str, str]]:
        """תצוגה מקדימה — רשימת (שם-ישן, שם-חדש)."""
        plan = self.build_plan(files, **kwargs)
        return [(item.source.name, item.target_name) for item in plan.items]

    # ------------------------------------------------------------------ #
    # ביצוע
    # ------------------------------------------------------------------ #
    def rename_files(
        self,
        files: List[Path],
        prefix: str = '',
        numbering_type: str = 'hebrew',
        with_geresh: bool = True,
        separator: str = '_',
        start_number: int = 1,
        thousands_style: str = 'letters',
        numeric_padding: int = 0,
        rename_mode: str = 'replace',
        clean_language: bool = False,
        clean_substitutions: Optional[Dict[str, str]] = None,
        progress_cb=None,
        cancel_check=None,
        record: bool = True,
    ) -> List[Tuple[str, str, bool]]:
        """שינוי שמות קבצים בצורה בטוחה. מחזיר (שם-מקורי, שם-חדש/שגיאה, הצלחה)."""
        plan = self.build_plan(
            files,
            prefix=prefix,
            numbering_type=numbering_type,
            with_geresh=with_geresh,
            separator=separator,
            start_number=start_number,
            thousands_style=thousands_style,
            numeric_padding=numeric_padding,
            rename_mode=rename_mode,
            clean_language=clean_language,
            clean_substitutions=clean_substitutions,
        )

        results = execute_plan(plan, progress_cb=progress_cb, cancel_check=cancel_check)

        if record:
            self._record(plan)

        return results

    def _record(self, plan: RenamePlan) -> None:
        operations = [
            Operation(
                original_path=str(item.source),
                new_path=str(item.target),
            )
            for item in plan.items
            if item.result
        ]
        if not operations:
            return

        now = datetime.now()
        transaction = Transaction(
            transaction_id=now.strftime('%Y%m%d%H%M%S%f'),
            timestamp=now.isoformat(timespec='seconds'),
            directory=str(self.directory),
            operations=operations,
        )
        self.journal.record(transaction)

    # ------------------------------------------------------------------ #
    # Undo
    # ------------------------------------------------------------------ #
    def can_undo(self) -> bool:
        return self.journal.last_transaction() is not None

    def undo_last(self, progress_cb=None) -> Optional[List[Tuple[str, str, bool]]]:
        """ביטול הריצה האחרונה. מחזיר None אם אין מה לבטל."""
        transaction = self.journal.pop_last()
        if transaction is None:
            return None
        return undo_transaction(transaction, progress_cb=progress_cb)
