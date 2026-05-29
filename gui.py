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

# main_gui.py


import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from file_renamer import FileRenamer


class FileRenamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("תוכנת שינוי שם קבצים")
        self.root.geometry("950x900")
        self.root.resizable(True, True)

        try:
            self.root.iconbitmap("שינוי השם.ico")
        except Exception:
            pass

        root.tk.call('tk', 'scaling', 2)

        self.selected_path_text = tk.StringVar()
        self.selected_paths = []
        self.files_list = []
        self.renamer = None

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        self.setup_ui()

    def setup_ui(self):
        main_content = ttk.Frame(self.root)
        main_content.grid(row=0, column=0, sticky="nsew")
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_rowconfigure(5, weight=1)

        # בחירת תיקייה
        frame_dir = ttk.LabelFrame(main_content, text="בחירת תיקייה או קבצים", padding=10)
        frame_dir.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        frame_dir.grid_columnconfigure(0, weight=1)

        ttk.Button(frame_dir, text="בחר תיקייה", command=self.select_directory).grid(row=0, column=2, padx=5)
        ttk.Button(frame_dir, text="בחר קבצים", command=self.select_files).grid(row=0, column=1, padx=5)

        self.include_subfolders = tk.BooleanVar(value=False)

        ttk.Checkbutton(
            frame_dir,
            text="כלול תתי-תיקיות",
            variable=self.include_subfolders,
            command=self.reload_files,
        ).grid(row=1, column=2, padx=5, pady=5)

        lbl_dir = ttk.Label(
            frame_dir,
            textvariable=self.selected_path_text,
            foreground="blue",
            cursor="hand2",
            wraplength=600,
        )

        lbl_dir.grid(row=0, column=0, rowspan=2, sticky="ew")
        lbl_dir.bind("<Button-1>", lambda _event: self.open_selected_location())

        # אפשרויות מספור
        frame_numbering = ttk.LabelFrame(main_content, text="אפשרויות מספור", padding=10)
        frame_numbering.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        self.numbering_type = tk.StringVar(value="hebrew")

        ttk.Radiobutton(frame_numbering, text="עברית", variable=self.numbering_type, value="hebrew", command=self.update_preview).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(frame_numbering, text="1.", variable=self.numbering_type, value="numeric", command=self.update_preview).grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(frame_numbering, text="1", variable=self.numbering_type, value="numeric_no_dot", command=self.update_preview).grid(row=0, column=2, sticky=tk.W)

        self.with_geresh = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            frame_numbering,
            text="עם גרש/גרשיים",
            variable=self.with_geresh,
            command=self.update_preview,
        ).grid(row=1, column=0, sticky=tk.W, pady=5)

        self.thousands_style = tk.StringVar(value="letters")
        self.numeric_padding = tk.IntVar(value=0)

        # מצב שינוי
        frame_mode = ttk.LabelFrame(main_content, text="אופן שינוי השם", padding=10)
        frame_mode.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        self.rename_mode = tk.StringVar(value="replace")

        ttk.Radiobutton(frame_mode, text="החלף שם", variable=self.rename_mode, value="replace", command=self.update_preview).grid(row=0, column=0)
        ttk.Radiobutton(frame_mode, text="הוסף בתחילה", variable=self.rename_mode, value="prepend", command=self.update_preview).grid(row=0, column=1)
        ttk.Radiobutton(frame_mode, text="הוסף בסוף", variable=self.rename_mode, value="append", command=self.update_preview).grid(row=0, column=2)

        # תחילית
        frame_prefix = ttk.LabelFrame(main_content, text="תחילית", padding=10)
        frame_prefix.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

        ttk.Label(frame_prefix, text="תחילית:").grid(row=0, column=0, padx=5)

        self.prefix_var = tk.StringVar(value="קובץ")
        entry_prefix = ttk.Entry(frame_prefix, textvariable=self.prefix_var, width=30)
        entry_prefix.grid(row=0, column=1, padx=5)
        entry_prefix.bind('<KeyRelease>', lambda _event: self.update_preview())

        ttk.Label(frame_prefix, text="תו הפרדה:").grid(row=1, column=0, padx=5)

        self.separator_var = tk.StringVar(value="_")
        entry_sep = ttk.Entry(frame_prefix, textvariable=self.separator_var, width=5)
        entry_sep.grid(row=1, column=1, padx=5)
        entry_sep.bind('<KeyRelease>', lambda _event: self.update_preview())

        ttk.Label(frame_prefix, text="התחלה מהמספר:").grid(row=2, column=0, padx=5)

        self.start_number = tk.IntVar(value=1)

        spinbox_start = ttk.Spinbox(
            frame_prefix,
            from_=1,
            to=999999,
            textvariable=self.start_number,
            width=10,
        )

        spinbox_start.grid(row=2, column=1, padx=5)
        spinbox_start.bind('<KeyRelease>', lambda _event: self.update_preview())

        # תצוגה מקדימה
        frame_preview = ttk.LabelFrame(main_content, text="תצוגה מקדימה", padding=10)
        frame_preview.grid(row=5, column=0, sticky="nsew", padx=10, pady=5)
        frame_preview.grid_columnconfigure(0, weight=1)
        frame_preview.grid_rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(frame_preview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.preview_text = tk.Text(
            frame_preview,
            height=20,
            yscrollcommand=scrollbar.set,
            state=tk.DISABLED,
            font=("Arial", 10),
        )

        self.preview_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.preview_text.yview)

        # כפתורים
        frame_buttons = ttk.Frame(self.root)
        frame_buttons.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        ttk.Button(frame_buttons, text="רענן תצוגה", command=self.reload_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_buttons, text="בצע שינוי שם!", command=self.perform_rename).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_buttons, text="יציאה", command=self.root.quit).pack(side=tk.LEFT, padx=5)

    def select_directory(self):
        directory = filedialog.askdirectory(title="בחר תיקייה")

        if directory:
            self.selected_paths = [Path(directory)]
            self.selected_path_text.set(directory)
            self.reload_files()

    def select_files(self):
        files = filedialog.askopenfilenames(title="בחר קבצים")

        if files:
            self.selected_paths = [Path(file_path) for file_path in files]
            self.selected_path_text.set(self._format_selected_paths())
            self.reload_files()

    def _format_selected_paths(self):
        if not self.selected_paths:
            return ""

        if len(self.selected_paths) == 1:
            return str(self.selected_paths[0])

        first_path = self.selected_paths[0]
        return f"{first_path.parent} ({len(self.selected_paths)} קבצים נבחרו)"

    def reload_files(self):
        if not self.selected_paths:
            self.files_list = []
            self.update_preview()
            return

        try:
            self.files_list = FileRenamer.get_selected_files(
                [str(path) for path in self.selected_paths],
                recursive=self.include_subfolders.get(),
            )

            base_path = self.selected_paths[0]

            self.renamer = FileRenamer(
                str(base_path if base_path.is_dir() else base_path.parent)
            )

            self.update_preview()

        except Exception as e:
            messagebox.showerror("שגיאה", f"לא ניתן לפתוח את הנתיב: {e}")

    def open_selected_location(self):
        if not self.selected_paths:
            return

        path = self.selected_paths[0]
        folder = path if path.is_dir() else path.parent

        try:
            if sys.platform.startswith('win'):
                os.startfile(folder)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', str(folder)])
            else:
                subprocess.Popen(['xdg-open', str(folder)])
        except Exception as e:
            messagebox.showerror("שגיאה", f"לא ניתן לפתוח את התיקייה: {e}")

    def get_start_number(self):
        try:
            return self.start_number.get()
        except tk.TclError:
            return 1

    def build_preview_name(self, file_path, idx):
        number_str = FileRenamer.format_number(
            idx,
            numbering_type=self.numbering_type.get(),
            with_geresh=self.with_geresh.get(),
            thousands_style=self.thousands_style.get(),
            numeric_padding=self.numeric_padding.get(),
        )

        return FileRenamer.build_new_name(
            file_path,
            number_str,
            prefix=self.prefix_var.get(),
            separator=self.separator_var.get(),
            rename_mode=self.rename_mode.get(),
        )

    def update_preview(self):
        if not self.files_list:
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, "אנא בחר תיקייה או קבצים")
            self.preview_text.config(state=tk.DISABLED)
            return

        preview_lines = []
        start_number = self.get_start_number()

        for idx, file_path in enumerate(self.files_list, start=start_number):
            try:
                new_name = self.build_preview_name(file_path, idx)
            except Exception:
                new_name = file_path.name

            preview_lines.append(f"{file_path.name} → {new_name}")

        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, "\n".join(preview_lines))
        self.preview_text.config(state=tk.DISABLED)

    def perform_rename(self):
        if not self.files_list:
            messagebox.showwarning("אזהרה", "אנא בחר תיקייה או קבצים")
            return

        subfolders_note = " כולל תתי-תיקיות" if self.include_subfolders.get() else ""

        result = messagebox.askyesno(
            "אישור",
            f"האם בטוח? הפעולה תחול על {len(self.files_list)} קבצים{subfolders_note}",
        )

        if not result:
            return

        try:
            results = self.renamer.rename_files(
                self.files_list,
                prefix=self.prefix_var.get(),
                numbering_type=self.numbering_type.get(),
                with_geresh=self.with_geresh.get(),
                separator=self.separator_var.get(),
                start_number=self.get_start_number(),
                thousands_style=self.thousands_style.get(),
                numeric_padding=self.numeric_padding.get(),
                rename_mode=self.rename_mode.get(),
            )

            successes = sum(1 for _, _, success in results if success)
            failures = len(results) - successes

            message = f"בוצע בהצלחה: {successes}/{len(results)}"

            if failures > 0:
                message += f"\n\nשגיאות: {failures}\n\n"

                for old, new, success in results:
                    if not success:
                        message += f"✗ {old} → {new}\n"

            messagebox.showinfo("תוצאה", message)
            self.reload_files()

        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בשינוי השם: {e}")


def main():
    root = tk.Tk()
    FileRenamerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()


