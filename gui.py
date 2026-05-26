import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from typing import List
import sys
from file_renamer import FileRenamer, HebrewNumbering

class FileRenamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("תוכנת שינוי שם קבצים")
        self.root.geometry("900x1100")
        self.root.resizable(True, True)
        
        # הוספת icon
        try:
            self.root.iconbitmap("שינוי השם.ico")
        except:
            pass  # אם לא קיים, המשך בלי icon
        
        # לשון עברית - RTL
        root.tk.call('tk', 'scaling', 2)
        
        # משתנים
        self.selected_directory = tk.StringVar()
        self.files_list = []
        self.renamer = None
        
        # הגדרת grid weights - חשוב מאוד!
        self.root.grid_rowconfigure(0, weight=1)  # main content - expandable
        self.root.grid_rowconfigure(1, weight=0)  # buttons - fixed size
        self.root.grid_columnconfigure(0, weight=1)
        
        self.setup_ui()
        
    def setup_ui(self):
        """בניית ממשק המשתמש"""
        
        # === MAIN CONTENT FRAME - יתרחב עם החלון ===
        main_content = ttk.Frame(self.root)
        main_content.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_rowconfigure(4, weight=1)  # preview expands
        
        # === קטע בחירת תיקייה ===
        frame_dir = ttk.LabelFrame(main_content, text="בחירת תיקייה", padding=10)
        frame_dir.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        frame_dir.grid_columnconfigure(1, weight=1)
        
        btn_browse = ttk.Button(frame_dir, text="בחר תיקייה", command=self.select_directory)
        btn_browse.pack(side=tk.RIGHT, padx=5)
        
        lbl_dir = ttk.Label(frame_dir, textvariable=self.selected_directory, 
                           foreground="blue", wraplength=500)
        lbl_dir.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
        # === קטע אפשרויות מספור ===
        frame_numbering = ttk.LabelFrame(main_content, text="אפשרויות מספור", padding=10)
        frame_numbering.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        frame_numbering.grid_columnconfigure(0, weight=1)
        
        # סוג המספור
        lbl_type = ttk.Label(frame_numbering, text="סוג מספור:")
        lbl_type.grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.numbering_type = tk.StringVar(value="hebrew")
        options_frame = ttk.Frame(frame_numbering)
        options_frame.grid(row=0, column=1, sticky=tk.W, columnspan=2, padx=5)
        
        ttk.Radiobutton(options_frame, text="עברית (א' ב' ג')", 
                       variable=self.numbering_type, value="hebrew",
                       command=self.update_preview).pack(anchor=tk.W)
        ttk.Radiobutton(options_frame, text="מספרים עם נקודה (1. 2. 3.)", 
                       variable=self.numbering_type, value="numeric",
                       command=self.update_preview).pack(anchor=tk.W)
        ttk.Radiobutton(options_frame, text="מספרים בלי נקודה (1 2 3)", 
                       variable=self.numbering_type, value="numeric_no_dot",
                       command=self.update_preview).pack(anchor=tk.W)
        
        # אפשרויות עברית
        self.with_geresh = tk.BooleanVar(value=True)
        self.geresh_check = ttk.Checkbutton(frame_numbering, text="עם גרש/גרשיים (א' בדל מ א)", 
                                           variable=self.with_geresh,
                                           command=self.update_preview)
        self.geresh_check.grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        # === קטע התחילית ===
        frame_prefix = ttk.LabelFrame(main_content, text="התחילית והפרדה", padding=10)
        frame_prefix.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        frame_prefix.grid_columnconfigure(1, weight=1)
        
        lbl_prefix = ttk.Label(frame_prefix, text="התחילית:")
        lbl_prefix.grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.prefix_var = tk.StringVar(value="קובץ")
        entry_prefix = ttk.Entry(frame_prefix, textvariable=self.prefix_var, width=30)
        entry_prefix.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        entry_prefix.bind('<KeyRelease>', lambda e: self.update_preview())
        
        lbl_sep = ttk.Label(frame_prefix, text="תו הפרדה:")
        lbl_sep.grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.separator_var = tk.StringVar(value="_")
        entry_sep = ttk.Entry(frame_prefix, textvariable=self.separator_var, width=5)
        entry_sep.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        entry_sep.bind('<KeyRelease>', lambda e: self.update_preview())
        
        # === קטע התחלת המספור ===
        lbl_start = ttk.Label(frame_prefix, text="התחלה מהמספר:")
        lbl_start.grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.start_number = tk.IntVar(value=1)
        spinbox_start = ttk.Spinbox(frame_prefix, from_=1, to=9999, 
                                   textvariable=self.start_number, width=10)
        spinbox_start.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        spinbox_start.bind('<KeyRelease>', lambda e: self.update_preview())
        
        # === קטע תצוגה מקדימה - זה חייב להתרחב! ===
        frame_preview = ttk.LabelFrame(main_content, text="תצוגה מקדימה", padding=10)
        frame_preview.grid(row=4, column=0, sticky="nsew", padx=10, pady=5)
        frame_preview.grid_columnconfigure(1, weight=1)
        frame_preview.grid_rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(frame_preview)
        scrollbar.grid(row=0, column=0, sticky="ns")
        
        self.preview_text = tk.Text(frame_preview, height=20, width=60, 
                                   yscrollcommand=scrollbar.set,
                                   state=tk.DISABLED, font=("Arial", 10))
        self.preview_text.grid(row=0, column=1, sticky="nsew")
        scrollbar.config(command=self.preview_text.yview)
        
        # === BUTTONS FRAME - בשורה שניה ותמיד נראה ===
        frame_buttons = ttk.Frame(self.root)
        frame_buttons.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        frame_buttons.grid_columnconfigure(0, weight=1)
        
        btn_preview = ttk.Button(frame_buttons, text="רענן תצוגה", command=self.update_preview)
        btn_preview.pack(side=tk.LEFT, padx=5)
        
        btn_rename = ttk.Button(frame_buttons, text="בצע שינוי שם!", 
                               command=self.perform_rename)
        btn_rename.pack(side=tk.LEFT, padx=5)
        
        btn_exit = ttk.Button(frame_buttons, text="יציאה", command=self.root.quit)
        btn_exit.pack(side=tk.LEFT, padx=5)
    
    def select_directory(self):
        """בחירת תיקייה"""
        directory = filedialog.askdirectory(title="בחר תיקייה")
        if directory:
            self.selected_directory.set(directory)
            try:
                self.renamer = FileRenamer(directory)
                self.files_list = self.renamer.get_files()
                self.update_preview()
            except Exception as e:
                messagebox.showerror("שגיאה", f"לא ניתן לפתוח את התיקייה: {e}")
    
    def update_preview(self):
        """עדכון תצוגה מקדימה"""
        if not self.files_list:
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, "אנא בחר תיקייה עם קבצים")
            self.preview_text.config(state=tk.DISABLED)
            return
        
        # יצירת התצוגה המקדימה
        preview_lines = []
        
        for idx, file_path in enumerate(self.files_list, start=self.start_number.get()):
            original_name = file_path.name
            extension = file_path.suffix
            
            # יצירת המספור
            if self.numbering_type.get() == "hebrew":
                try:
                    number_str = HebrewNumbering.number_to_hebrew(idx, self.with_geresh.get())
                except:
                    number_str = str(idx)
            elif self.numbering_type.get() == "numeric":
                number_str = str(idx) + '.'
            else:
                number_str = str(idx)
            
            # יצירת השם החדש
            prefix = self.prefix_var.get()
            separator = self.separator_var.get()
            
            if prefix:
                new_name = f"{prefix}{separator}{number_str}{extension}"
            else:
                new_name = f"{number_str}{extension}"
            
            preview_lines.append(f"{original_name} → {new_name}")
        
        # עדכון התצוגה
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, "\n".join(preview_lines))
        self.preview_text.config(state=tk.DISABLED)
    
    def perform_rename(self):
        """ביצוע שינוי השם"""
        if not self.files_list:
            messagebox.showwarning("אזהרה", "אנא בחר תיקייה עם קבצים")
            return
        
        # אישור מהמשתמש
        result = messagebox.askyesno("אישור", 
                                    f"האם בטוח? על סך הכל {len(self.files_list)} קבצים")
        if not result:
            return
        
        try:
            results = self.renamer.rename_files(
                self.files_list,
                prefix=self.prefix_var.get(),
                numbering_type=self.numbering_type.get(),
                with_geresh=self.with_geresh.get(),
                separator=self.separator_var.get(),
                start_number=self.start_number.get()
            )
            
            # ספירת ההצלחות
            successes = sum(1 for _, _, success in results if success)
            failures = len(results) - successes
            
            message = f"בוצע בהצלחה: {successes}/{len(results)}"
            if failures > 0:
                message += f"\n\nשגיאות: {failures}"
                message += "\n\n"
                for old, new, success in results:
                    if not success:
                        message += f"✗ {old} → {new}\n"
            
            messagebox.showinfo("תוצאה", message)
            self.update_preview()
        
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בשינוי השם: {e}")

def main():
    root = tk.Tk()
    app = FileRenamerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
