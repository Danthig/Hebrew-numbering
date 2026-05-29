import re
from pathlib import Path
from typing import List, Tuple


def natural_sort_key(value):
    """מפתח מיון טבעי ללא תלות בספריות חיצוניות."""
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r'(\d+)', str(value))
    ]


def natsorted(values, key=None):
    """תחליף קטן ל-natsort כדי שהקובץ יעבוד גם בלי התקנות נוספות."""
    if key is None:
        return sorted(values, key=natural_sort_key)
    return sorted(values, key=lambda item: natural_sort_key(key(item)))


class HebrewNumbering:
    """מחלקה לעיבוד מספור בעברית"""

    HEBREW_ONES = ['', 'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט']
    HEBREW_TENS = ['', 'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ']
    HEBREW_HUNDREDS = ['', 'ק', 'ר', 'ש', 'ת', 'תק', 'תר', 'תש', 'תת', 'תתק']

    @staticmethod
    def number_to_hebrew(
        num: int,
        with_geresh: bool = True,
        thousands_style: str = 'letters',
    ) -> str:
        """המרת מספר לעברית"""

        if num < 1 or num > 999999:
            raise ValueError("המספר חייב להיות בין 1 ל-999999")

        if num >= 1000:
            thousands = num // 1000
            remainder = num % 1000

            if thousands_style == 'words':
                parts = [HebrewNumbering._thousands_to_words(thousands, with_geresh)]
            else:
                parts = [HebrewNumbering._under_1000_to_hebrew(thousands, with_geresh)]

            if remainder:
                parts.append(HebrewNumbering._under_1000_to_hebrew(remainder, with_geresh))

            return ' '.join(part for part in parts if part)

        return HebrewNumbering._under_1000_to_hebrew(num, with_geresh)

    @staticmethod
    def _under_1000_to_hebrew(num: int, with_geresh: bool = True) -> str:
        """המרת מספר בין 1 ל-999 לעברית"""

        if num < 1 or num > 999:
            raise ValueError("המספר חייב להיות בין 1 ל-999")

        result = ''

        # מאות
        if num >= 100:
            hundreds = num // 100
            result += HebrewNumbering.HEBREW_HUNDREDS[hundreds]
            num %= 100

        # עשרות ויחידות
        if num >= 10:
            tens = num // 10
            ones = num % 10

            if tens == 1:
                result += HebrewNumbering._get_teen(ones)
            else:
                result += HebrewNumbering.HEBREW_TENS[tens]
                if ones > 0:
                    result += HebrewNumbering.HEBREW_ONES[ones]
        elif num > 0:
            result += HebrewNumbering.HEBREW_ONES[num]

        return HebrewNumbering._apply_geresh(result) if with_geresh else result

    @staticmethod
    def _thousands_to_words(thousands: int, with_geresh: bool) -> str:
        """ייצוג מילולי של אלפים"""

        if thousands == 1:
            return 'אלף'

        if thousands == 2:
            return 'אלפיים'

        return f"{HebrewNumbering.number_to_hebrew(thousands, with_geresh, 'letters')} אלפים"

    @staticmethod
    def _apply_geresh(text: str) -> str:
        """הוספת גרש/גרשיים"""

        if not text:
            return text

        if len(text) == 1:
            return text + "'"

        return text[:-1] + '"' + text[-1]

    @staticmethod
    def _get_teen(ones: int) -> str:
        """המרת מספר בין 10-19"""

        teens = ['י', 'יא', 'יב', 'יג', 'יד', 'טו', 'טז', 'יז', 'יח', 'יט']
        return teens[ones]


class FileRenamer:
    """מחלקה לניהול שינוי שמות קבצים"""

    def __init__(self, directory: str):
        self.directory = Path(directory)

        if not self.directory.exists():
            raise ValueError(f"הנתיב '{directory}' לא קיים")

    def get_files(self, extensions: List[str] = None, recursive: bool = False) -> List[Path]:
        """קבלת רשימת קבצים"""

        if self.directory.is_file():
            return [self.directory]

        files = []
        glob_method = self.directory.rglob if recursive else self.directory.glob

        if extensions is None:
            files = [f for f in glob_method('*') if f.is_file()]
        else:
            for ext in extensions:
                pattern = f"*.{ext.lstrip('.')}"
                files.extend(f for f in glob_method(pattern) if f.is_file())

        return natsorted(files, key=lambda x: str(x.relative_to(self.directory)))

    @staticmethod
    def get_selected_files(paths: List[str], recursive: bool = False) -> List[Path]:
        """קבלת קבצים מרשימת נתיבים"""

        files = []

        for selected_path in paths:
            path = Path(selected_path)

            if path.is_file():
                files.append(path)
            elif path.is_dir():
                files.extend(FileRenamer(str(path)).get_files(recursive=recursive))

        return natsorted(files, key=lambda x: str(x))

    @staticmethod
    def format_number(
        number: int,
        numbering_type: str = 'hebrew',
        with_geresh: bool = True,
        thousands_style: str = 'letters',
        numeric_padding: int = 0,
    ) -> str:
        """יצירת מחרוזת המספור"""

        if numbering_type == 'hebrew':
            return HebrewNumbering.number_to_hebrew(number, with_geresh, thousands_style)

        number_str = str(number).zfill(numeric_padding) if numeric_padding else str(number)

        if numbering_type == 'numeric':
            return number_str + '.'

        if numbering_type == 'numeric_no_dot':
            return number_str

        return number_str

    @staticmethod
    def build_new_name(
        file_path: Path,
        number_str: str,
        prefix: str = '',
        separator: str = '_',
        rename_mode: str = 'replace',
    ) -> str:
        """בניית שם קובץ חדש"""

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
    ) -> List[Tuple[str, str, bool]]:
        """שינוי שמות קבצים"""

        results = []

        for idx, file_path in enumerate(files, start=start_number):
            file_path = Path(file_path)
            original_name = file_path.name

            number_str = self.format_number(
                idx,
                numbering_type=numbering_type,
                with_geresh=with_geresh,
                thousands_style=thousands_style,
                numeric_padding=numeric_padding,
            )

            new_name = self.build_new_name(
                file_path,
                number_str,
                prefix=prefix,
                separator=separator,
                rename_mode=rename_mode,
            )

            new_path = file_path.with_name(new_name)

            if new_path.exists() and new_path != file_path:
                results.append((original_name, new_name, False))
                continue

            try:
                file_path.rename(new_path)
                results.append((original_name, new_name, True))
            except Exception as e:
                results.append((original_name, f"שגיאה: {str(e)}", False))

        return results


def main():
    import sys

    if len(sys.argv) < 2:
        print("שימוש: python file_renamer.py <תיקייה>")
        return

    directory = sys.argv[1]

    try:
        renamer = FileRenamer(directory)
        files = renamer.get_files()

        if not files:
            print("לא נמצאו קבצים בתיקייה")
            return

        print(f"\nנמצאו {len(files)} קבצים")

        results = renamer.rename_files(
            files,
            prefix='קובץ',
            numbering_type='hebrew',
            with_geresh=True,
        )

        print("\nתוצאות השינוי:")

        for old_name, new_name, success in results:
            status = '✓' if success else '✗'
            print(f"  {status} {old_name} → {new_name}")

    except Exception as e:
        print(f"שגיאה: {e}")


if __name__ == '__main__':
    main()

