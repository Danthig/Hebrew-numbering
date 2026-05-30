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
        ttk.Label(frame_numbering, text="אלפים בעברית:").grid(row=1, column=1, sticky=tk.W, padx=(15, 5))
        ttk.Radiobutton(
            frame_numbering,
            text="אותיות (א' א')",
            variable=self.thousands_style,
            value="letters",
            command=self.update_preview,
        ).grid(row=1, column=2, sticky=tk.W, pady=5)
        ttk.Radiobutton(
            frame_numbering,
            text="מילים (אלף א')",
            variable=self.thousands_style,
            value="words",
            command=self.update_preview,
        ).grid(row=1, column=3, sticky=tk.W, pady=5)

        self.numeric_padding = tk.IntVar(value=0)
        ttk.Label(frame_numbering, text="אפסים לפני מספר:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(
            frame_numbering,
            text="ללא (1, 2, 3)",
            variable=self.numeric_padding,
            value=0,
            command=self.update_preview,
        ).grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(
            frame_numbering,
            text="0 אחד (01, 02)",
            variable=self.numeric_padding,
            value=2,
            command=self.update_preview,
        ).grid(row=2, column=2, sticky=tk.W, pady=5)
        ttk.Radiobutton(
            frame_numbering,
            text="00 שניים (001, 002)",
            variable=self.numeric_padding,
            value=3,
            command=self.update_preview,
        ).grid(row=2, column=3, sticky=tk.W, pady=5)

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
            command=self.update_preview,
        )

        spinbox_start.grid(row=2, column=1, padx=5)
        spinbox_start.bind('<KeyRelease>', lambda _event: self.update_preview())
        spinbox_start.bind('<FocusOut>', lambda _event: self.update_preview())

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


