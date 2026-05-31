"""
ממשק גרפי (Tkinter) לשינוי שמות קבצים עם מספור עברי.

תכונות:
- מספור עברי / מספרי, גרש, אלפים, אפסים מובילים
- מספור בלשון נקייה (שד→דש, ובאופציה רע/שמד)
- תצוגה מקדימה חיה עם סימון התנגשויות
- שינוי שם בטוח (אטומי) ברקע, עם פס התקדמות וביטול
- Undo לריצה האחרונה
- שמירת הגדרות בין הפעלות
- בחירת אסטרטגיית מיון
"""

import json
import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from hebrew_renamer.renamer import FileRenamer
from hebrew_renamer.gematria import HebrewNumbering
from hebrew_renamer.transaction import HISTORY_DIR

SETTINGS_FILE = HISTORY_DIR / 'settings.json'

SORT_LABELS = {
    'natural': 'טבעי (1, 2, 10)',
    'name': 'שם',
    'date': 'תאריך שינוי',
    'size': 'גודל',
    'type': 'סוג (סיומת)',
}
SORT_VALUES = {label: value for value, label in SORT_LABELS.items()}


class FileRenamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("תוכנת שינוי שם קבצים")
        self.root.geometry("950x950")
        self.root.resizable(True, True)

        self._set_icon()

        root.tk.call('tk', 'scaling', 2)

        self.selected_path_text = tk.StringVar()
        self.selected_paths = []
        self.files_list = []
        self.renamer = None

        # מצב ריצה ברקע
        self.work_queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.is_running = False

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        self._init_vars()
        self.setup_ui()
        self._load_settings()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _set_icon(self):
        """הגדרת אייקון החלון (.ico ב-Windows, .png כגיבוי חוצה-פלטפורמות)."""
        if getattr(sys, 'frozen', False):
            base = Path(getattr(sys, '_MEIPASS', Path(__file__).parent.parent))
            webui = base / 'hebrew_renamer' / 'webui'
        else:
            webui = Path(__file__).parent / 'webui'
        try:
            self.root.iconbitmap(str(webui / 'icon.ico'))
            return
        except Exception:
            pass
        try:
            self._icon_img = tk.PhotoImage(file=str(webui / 'icon.png'))
            self.root.iconphoto(True, self._icon_img)
        except Exception:
            pass

    def _init_vars(self):
        self.include_subfolders = tk.BooleanVar(value=False)
        self.sort_label = tk.StringVar(value=SORT_LABELS['natural'])
        self.numbering_type = tk.StringVar(value="hebrew")
        self.with_geresh = tk.BooleanVar(value=True)
        self.thousands_style = tk.StringVar(value="letters")
        self.numeric_padding = tk.IntVar(value=0)
        self.clean_language = tk.BooleanVar(value=False)
        self.clean_extra = tk.BooleanVar(value=False)
        self.rename_mode = tk.StringVar(value="replace")
        self.prefix_var = tk.StringVar(value="קובץ")
        self.separator_var = tk.StringVar(value="_")
        self.start_number = tk.IntVar(value=1)
        self.status_text = tk.StringVar(value="מוכן")

    # ------------------------------------------------------------------ #
    # בניית הממשק
    # ------------------------------------------------------------------ #
    def setup_ui(self):
        main_content = ttk.Frame(self.root)
        main_content.grid(row=0, column=0, sticky="nsew")
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_rowconfigure(5, weight=1)

        self._build_dir_frame(main_content)
        self._build_numbering_frame(main_content)
        self._build_mode_frame(main_content)
        self._build_prefix_frame(main_content)
        self._build_preview_frame(main_content)
        self._build_bottom_bar()

    def _build_dir_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="בחירת תיקייה או קבצים", padding=10)
        frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        frame.grid_columnconfigure(0, weight=1)

        ttk.Button(frame, text="בחר תיקייה", command=self.select_directory).grid(row=0, column=2, padx=5)
        ttk.Button(frame, text="בחר קבצים", command=self.select_files).grid(row=0, column=1, padx=5)

        ttk.Checkbutton(
            frame, text="כלול תתי-תיקיות",
            variable=self.include_subfolders, command=self.reload_files,
        ).grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(frame, text="מיון:").grid(row=1, column=1, sticky=tk.E)
        sort_combo = ttk.Combobox(
            frame, textvariable=self.sort_label,
            values=list(SORT_LABELS.values()), state="readonly", width=16,
        )
        sort_combo.grid(row=1, column=0, sticky=tk.W, padx=5)
        sort_combo.bind("<<ComboboxSelected>>", lambda _e: self.reload_files())

        lbl_dir = ttk.Label(
            frame, textvariable=self.selected_path_text,
            foreground="blue", cursor="hand2", wraplength=600,
        )
        lbl_dir.grid(row=0, column=0, sticky="ew")
        lbl_dir.bind("<Button-1>", lambda _e: self.open_selected_location())

    def _build_numbering_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="אפשרויות מספור", padding=10)
        frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        ttk.Radiobutton(frame, text="עברית", variable=self.numbering_type, value="hebrew", command=self.update_preview).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(frame, text="1.", variable=self.numbering_type, value="numeric", command=self.update_preview).grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(frame, text="1", variable=self.numbering_type, value="numeric_no_dot", command=self.update_preview).grid(row=0, column=2, sticky=tk.W)

        ttk.Checkbutton(frame, text="עם גרש/גרשיים", variable=self.with_geresh, command=self.update_preview).grid(row=1, column=0, sticky=tk.W, pady=5)

        ttk.Label(frame, text="אלפים בעברית:").grid(row=1, column=1, sticky=tk.W, padx=(15, 5))
        ttk.Radiobutton(frame, text="אותיות (א' א')", variable=self.thousands_style, value="letters", command=self.update_preview).grid(row=1, column=2, sticky=tk.W, pady=5)
        ttk.Radiobutton(frame, text="מילים (אלף א')", variable=self.thousands_style, value="words", command=self.update_preview).grid(row=1, column=3, sticky=tk.W, pady=5)

        # לשון נקייה
        ttk.Checkbutton(
            frame, text="מספור בלשון נקייה (שד→דש)",
            variable=self.clean_language, command=self._on_clean_toggle,
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        self.clean_extra_cb = ttk.Checkbutton(
            frame, text="כולל רע→ער, שמד→דמש",
            variable=self.clean_extra, command=self.update_preview, state=tk.DISABLED,
        )
        self.clean_extra_cb.grid(row=2, column=2, columnspan=2, sticky=tk.W, pady=5)

        ttk.Label(frame, text="אפסים לפני מספר:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(frame, text="ללא (1, 2, 3)", variable=self.numeric_padding, value=0, command=self.update_preview).grid(row=3, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(frame, text="0 אחד (01, 02)", variable=self.numeric_padding, value=2, command=self.update_preview).grid(row=3, column=2, sticky=tk.W, pady=5)
        ttk.Radiobutton(frame, text="00 שניים (001, 002)", variable=self.numeric_padding, value=3, command=self.update_preview).grid(row=3, column=3, sticky=tk.W, pady=5)

    def _build_mode_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="אופן שינוי השם", padding=10)
        frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        ttk.Radiobutton(frame, text="החלף שם", variable=self.rename_mode, value="replace", command=self.update_preview).grid(row=0, column=0)
        ttk.Radiobutton(frame, text="הוסף בתחילה", variable=self.rename_mode, value="prepend", command=self.update_preview).grid(row=0, column=1)
        ttk.Radiobutton(frame, text="הוסף בסוף", variable=self.rename_mode, value="append", command=self.update_preview).grid(row=0, column=2)

    def _build_prefix_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="תחילית", padding=10)
        frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

        ttk.Label(frame, text="תחילית:").grid(row=0, column=0, padx=5)
        entry_prefix = ttk.Entry(frame, textvariable=self.prefix_var, width=30)
        entry_prefix.grid(row=0, column=1, padx=5)
        entry_prefix.bind('<KeyRelease>', lambda _e: self.update_preview())

        ttk.Label(frame, text="תו הפרדה:").grid(row=1, column=0, padx=5)
        entry_sep = ttk.Entry(frame, textvariable=self.separator_var, width=5)
        entry_sep.grid(row=1, column=1, padx=5)
        entry_sep.bind('<KeyRelease>', lambda _e: self.update_preview())

        ttk.Label(frame, text="התחלה מהמספר:").grid(row=2, column=0, padx=5)
        spinbox = ttk.Spinbox(frame, from_=1, to=999999, textvariable=self.start_number, width=10, command=self.update_preview)
        spinbox.grid(row=2, column=1, padx=5)
        spinbox.bind('<KeyRelease>', lambda _e: self.update_preview())
        spinbox.bind('<FocusOut>', lambda _e: self.update_preview())

    def _build_preview_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="תצוגה מקדימה", padding=10)
        frame.grid(row=5, column=0, sticky="nsew", padx=10, pady=5)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.preview_text = tk.Text(frame, height=18, yscrollcommand=scrollbar.set, state=tk.DISABLED, font=("Arial", 10))
        self.preview_text.grid(row=0, column=0, sticky="nsew")
        self.preview_text.tag_config("conflict", foreground="red")
        scrollbar.config(command=self.preview_text.yview)

    def _build_bottom_bar(self):
        bar = ttk.Frame(self.root)
        bar.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        bar.grid_columnconfigure(5, weight=1)

        self.btn_refresh = ttk.Button(bar, text="רענן תצוגה", command=self.reload_files)
        self.btn_refresh.grid(row=0, column=0, padx=5)
        self.btn_rename = ttk.Button(bar, text="בצע שינוי שם!", command=self.perform_rename)
        self.btn_rename.grid(row=0, column=1, padx=5)
        self.btn_undo = ttk.Button(bar, text="בטל שינוי אחרון", command=self.undo_last)
        self.btn_undo.grid(row=0, column=2, padx=5)
        self.btn_cancel = ttk.Button(bar, text="עצור", command=self._request_cancel, state=tk.DISABLED)
        self.btn_cancel.grid(row=0, column=3, padx=5)
        ttk.Button(bar, text="יציאה", command=self._on_close).grid(row=0, column=4, padx=5)

        self.progress = ttk.Progressbar(bar, mode='determinate', length=200)
        self.progress.grid(row=0, column=6, padx=5, sticky=tk.E)
        ttk.Label(bar, textvariable=self.status_text, foreground="gray").grid(row=0, column=7, padx=5)

        self._refresh_undo_state()

    # ------------------------------------------------------------------ #
    # בחירת קבצים
    # ------------------------------------------------------------------ #
    def select_directory(self):
        directory = filedialog.askdirectory(title="בחר תיקייה")
        if directory:
            self.selected_paths = [Path(directory)]
            self.selected_path_text.set(directory)
            self.reload_files()

    def select_files(self):
        files = filedialog.askopenfilenames(title="בחר קבצים")
        if files:
            self.selected_paths = [Path(p) for p in files]
            self.selected_path_text.set(self._format_selected_paths())
            self.reload_files()

    def _format_selected_paths(self):
        if not self.selected_paths:
            return ""
        if len(self.selected_paths) == 1:
            return str(self.selected_paths[0])
        return f"{self.selected_paths[0].parent} ({len(self.selected_paths)} קבצים נבחרו)"

    def _current_sort(self):
        return SORT_VALUES.get(self.sort_label.get(), 'natural')

    def reload_files(self):
        if not self.selected_paths:
            self.files_list = []
            self.update_preview()
            return
        try:
            self.files_list = FileRenamer.get_selected_files(
                [str(p) for p in self.selected_paths],
                recursive=self.include_subfolders.get(),
                sort_strategy=self._current_sort(),
            )
            base = self.selected_paths[0]
            self.renamer = FileRenamer(str(base if base.is_dir() else base.parent))
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

    # ------------------------------------------------------------------ #
    # אפשרויות וחישוב
    # ------------------------------------------------------------------ #
    def _on_clean_toggle(self):
        state = tk.NORMAL if self.clean_language.get() else tk.DISABLED
        self.clean_extra_cb.config(state=state)
        self.update_preview()

    def get_start_number(self):
        try:
            return self.start_number.get()
        except tk.TclError:
            return 1

    def _clean_substitutions(self):
        if self.clean_language.get() and self.clean_extra.get():
            return dict(HebrewNumbering.OPTIONAL_CLEAN_SUBSTITUTIONS)
        return None

    def _rename_kwargs(self):
        return dict(
            prefix=self.prefix_var.get(),
            numbering_type=self.numbering_type.get(),
            with_geresh=self.with_geresh.get(),
            separator=self.separator_var.get(),
            start_number=self.get_start_number(),
            thousands_style=self.thousands_style.get(),
            numeric_padding=self.numeric_padding.get(),
            rename_mode=self.rename_mode.get(),
            clean_language=self.clean_language.get(),
            clean_substitutions=self._clean_substitutions(),
        )

    def update_preview(self):
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)

        if not self.files_list or not self.renamer:
            self.preview_text.insert(tk.END, "אנא בחר תיקייה או קבצים")
            self.preview_text.config(state=tk.DISABLED)
            return

        try:
            plan = self.renamer.build_plan(self.files_list, **self._rename_kwargs())
        except Exception:
            self.preview_text.insert(tk.END, "שגיאה בחישוב התצוגה המקדימה")
            self.preview_text.config(state=tk.DISABLED)
            return

        conflict_ids = {id(c.item): c.reason for c in plan.conflicts}
        for item in plan.items:
            reason = conflict_ids.get(id(item))
            if reason:
                self.preview_text.insert(tk.END, f"⚠ {item.source.name} → {item.target_name}  ({reason})\n", "conflict")
            else:
                self.preview_text.insert(tk.END, f"{item.source.name} → {item.target_name}\n")

        if plan.has_conflicts:
            self.status_text.set(f"⚠ {len(plan.conflicts)} התנגשויות")
        else:
            self.status_text.set(f"{len(plan.items)} קבצים מוכנים")

        self.preview_text.config(state=tk.DISABLED)

    # ------------------------------------------------------------------ #
    # ביצוע ברקע
    # ------------------------------------------------------------------ #
    def perform_rename(self):
        if self.is_running:
            return
        if not self.files_list:
            messagebox.showwarning("אזהרה", "אנא בחר תיקייה או קבצים")
            return

        note = " כולל תתי-תיקיות" if self.include_subfolders.get() else ""
        if not messagebox.askyesno("אישור", f"האם בטוח? הפעולה תחול על {len(self.files_list)} קבצים{note}"):
            return

        self._set_running(True)
        self.cancel_event.clear()
        self.progress.config(maximum=len(self.files_list), value=0)

        files = list(self.files_list)
        kwargs = self._rename_kwargs()
        thread = threading.Thread(target=self._worker_rename, args=(files, kwargs), daemon=True)
        thread.start()
        self.root.after(50, self._poll_queue)

    def _worker_rename(self, files, kwargs):
        def progress_cb(done, total, name):
            self.work_queue.put(('progress', done, total, name))
        try:
            results = self.renamer.rename_files(
                files, progress_cb=progress_cb,
                cancel_check=self.cancel_event.is_set, **kwargs,
            )
            self.work_queue.put(('done', results))
        except Exception as exc:
            self.work_queue.put(('error', exc))

    def undo_last(self):
        if self.is_running:
            return
        if not self.renamer:
            # אפשר לבטל גם בלי תיקייה נבחרת — נשתמש בתיקייה הנוכחית
            self.renamer = FileRenamer(str(Path.cwd()))
        if not self.renamer.can_undo():
            messagebox.showinfo("ביטול", "אין פעולה לביטול")
            return
        if not messagebox.askyesno("ביטול", "לבטל את הריצה האחרונה?"):
            return

        self._set_running(True)
        self.progress.config(mode='indeterminate')
        self.progress.start(10)

        def worker():
            try:
                results = self.renamer.undo_last()
                self.work_queue.put(('done', results))
            except Exception as exc:
                self.work_queue.put(('error', exc))

        threading.Thread(target=worker, daemon=True).start()
        self.root.after(50, self._poll_queue)

    def _poll_queue(self):
        try:
            while True:
                msg = self.work_queue.get_nowait()
                kind = msg[0]
                if kind == 'progress':
                    _, done, total, name = msg
                    self.progress.config(value=done)
                    self.status_text.set(f"{done}/{total}: {name}")
                elif kind == 'done':
                    self._finish_run(msg[1])
                    return
                elif kind == 'error':
                    self._finish_run(None, error=msg[1])
                    return
        except queue.Empty:
            pass
        if self.is_running:
            self.root.after(50, self._poll_queue)

    def _finish_run(self, results, error=None):
        self.progress.stop()
        self.progress.config(mode='determinate', value=0)
        self._set_running(False)

        if error is not None:
            messagebox.showerror("שגיאה", f"שגיאה בשינוי השם: {error}")
            return

        results = results or []
        successes = sum(1 for _, _, ok in results if ok)
        failures = len(results) - successes
        message = f"בוצע בהצלחה: {successes}/{len(results)}"
        if failures > 0:
            message += f"\n\nשגיאות/התנגשויות: {failures}\n\n"
            for old, new, ok in results:
                if not ok:
                    message += f"✗ {old} → {new}\n"
        messagebox.showinfo("תוצאה", message)

        self._refresh_undo_state()
        self.reload_files()

    def _request_cancel(self):
        self.cancel_event.set()
        self.status_text.set("עוצר...")

    def _set_running(self, running):
        self.is_running = running
        state = tk.DISABLED if running else tk.NORMAL
        self.btn_rename.config(state=state)
        self.btn_refresh.config(state=state)
        self.btn_undo.config(state=state)
        self.btn_cancel.config(state=tk.NORMAL if running else tk.DISABLED)
        if not running:
            self._refresh_undo_state()

    def _refresh_undo_state(self):
        try:
            renamer = self.renamer or FileRenamer(str(Path.cwd()))
            self.btn_undo.config(state=tk.NORMAL if renamer.can_undo() else tk.DISABLED)
        except Exception:
            self.btn_undo.config(state=tk.DISABLED)

    # ------------------------------------------------------------------ #
    # הגדרות
    # ------------------------------------------------------------------ #
    def _settings_snapshot(self):
        return {
            'sort_label': self.sort_label.get(),
            'numbering_type': self.numbering_type.get(),
            'with_geresh': self.with_geresh.get(),
            'thousands_style': self.thousands_style.get(),
            'numeric_padding': self.numeric_padding.get(),
            'clean_language': self.clean_language.get(),
            'clean_extra': self.clean_extra.get(),
            'rename_mode': self.rename_mode.get(),
            'prefix': self.prefix_var.get(),
            'separator': self.separator_var.get(),
            'include_subfolders': self.include_subfolders.get(),
        }

    def _load_settings(self):
        try:
            if not SETTINGS_FILE.exists():
                return
            data = json.loads(SETTINGS_FILE.read_text(encoding='utf-8'))
        except Exception:
            return
        mapping = {
            'sort_label': self.sort_label, 'numbering_type': self.numbering_type,
            'with_geresh': self.with_geresh, 'thousands_style': self.thousands_style,
            'numeric_padding': self.numeric_padding, 'clean_language': self.clean_language,
            'clean_extra': self.clean_extra, 'rename_mode': self.rename_mode,
            'prefix': self.prefix_var, 'separator': self.separator_var,
            'include_subfolders': self.include_subfolders,
        }
        for key, var in mapping.items():
            if key in data:
                try:
                    var.set(data[key])
                except Exception:
                    pass
        self._on_clean_toggle()

    def _save_settings(self):
        try:
            SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            SETTINGS_FILE.write_text(
                json.dumps(self._settings_snapshot(), ensure_ascii=False, indent=2),
                encoding='utf-8',
            )
        except Exception:
            pass

    def _on_close(self):
        if self.is_running:
            if not messagebox.askyesno("יציאה", "פעולה רצה כעת. לצאת בכל זאת?"):
                return
        self._save_settings()
        self.root.quit()


def main():
    root = tk.Tk()
    FileRenamerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
