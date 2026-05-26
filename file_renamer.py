import os
import re
from pathlib import Path
from typing import List, Tuple
from natsort import natsorted

class HebrewNumbering:
    """מחלקה לעיבוד מספור בעברית"""
    
    HEBREW_ONES = ['', 'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט']
    HEBREW_TENS = ['', 'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ']
    HEBREW_HUNDREDS = ['', 'ק', 'ר', 'ש', 'ת', 'תק', 'תר', 'תש', 'תת', 'תתק']
    
    @staticmethod
    def number_to_hebrew(num: int, with_geresh: bool = True) -> str:
        """
        המרת מספר לעברית
        num: המספר להמרה (1-9999)
        with_geresh: האם להוסיף גרש/גרשיים
        """
        if num < 1 or num > 9999:
            raise ValueError("המספר חייב להיות בין 1 ל-9999")
        
        result = ''
        
        # אלפים
        if num >= 1000:
            thousands = num // 1000
            result += HebrewNumbering.HEBREW_ONES[thousands] + " אלף"
            num = num % 1000
            if num > 0:
                result += " "
        
        # מאות
        if num >= 100:
            hundreds = num // 100
            if hundreds < len(HebrewNumbering.HEBREW_HUNDREDS):
                result += HebrewNumbering.HEBREW_HUNDREDS[hundreds]
            num = num % 100
        
        # עשרות ויחידות
        if num >= 10:
            tens = num // 10
            ones = num % 10
            
            if tens == 1:  # 10-19
                result += HebrewNumbering._get_teen(ones)
            else:
                result += HebrewNumbering.HEBREW_TENS[tens]
                if ones > 0:
                    result += HebrewNumbering.HEBREW_ONES[ones]
        else:  # 1-9
            if num > 0:
                result += HebrewNumbering.HEBREW_ONES[num]
        
        # הוספת גרש/גרשיים
        if with_geresh and result:
            if len(result) > 1:
                result = result[:-1] + '"' + result[-1]
            else:
                result += "'"
        
        return result
    
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
            raise ValueError(f"התיקייה '{directory}' לא קיימת")
    
    def get_files(self, extensions: List[str] = None) -> List[Path]:
        """
        קבלת רשימת קבצים מהתיקייה
        extensions: רשימת סיומות (ללא נקודה), None = כל הקבצים
        """
        files = []
        
        if extensions is None:
            # כל הקבצים
            files = [f for f in self.directory.iterdir() if f.is_file()]
        else:
            # קבצים עם סיומות מסוימות
            for ext in extensions:
                pattern = f"*.{ext.lstrip('.')}"
                files.extend(self.directory.glob(pattern))
        
        # מיון טבעי (numeric sort) - 1,2,3... 10,11... לא 1,10,100...
        return natsorted(files, key=lambda x: x.name)
    
    def rename_files(self, files: List[Path], prefix: str = '', 
                     numbering_type: str = 'hebrew',
                     with_geresh: bool = True,
                     separator: str = '_',
                     start_number: int = 1) -> List[Tuple[str, str, bool]]:
        """
        שינוי שם קבצים
        
        numbering_type: 'hebrew', 'numeric', 'arabic'
        separator: התו המפריד בין התחילית למספר
        
        מחזיר רשימה של tuples: (שם ישן, שם חדש, הצליח)
        """
        results = []
        
        for idx, file_path in enumerate(files, start=start_number):
            original_name = file_path.name
            extension = file_path.suffix
            
            # יצירת המספור
            if numbering_type == 'hebrew':
                number_str = HebrewNumbering.number_to_hebrew(idx, with_geresh)
            elif numbering_type == 'numeric':
                number_str = str(idx) + '.'
            elif numbering_type == 'numeric_no_dot':
                number_str = str(idx)
            else:
                number_str = str(idx)
            
            # יצירת השם החדש
            if prefix:
                new_name = f"{prefix}{separator}{number_str}{extension}"
            else:
                new_name = f"{number_str}{extension}"
            
            new_path = self.directory / new_name
            
            # בדיקה אם הקובץ כבר קיים
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
    """דוגמה לשימוש"""
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
        print("\nשמות הקבצים:")
        for f in files:
            print(f"  - {f.name}")
        
        # דוגמה: שינוי שם עם מספור בעברית
        results = renamer.rename_files(files, prefix='קובץ', 
                                      numbering_type='hebrew',
                                      with_geresh=True)
        
        print("\nתוצאות השינוי:")
        for old_name, new_name, success in results:
            status = "✓" if success else "✗"
            print(f"  {status} {old_name} → {new_name}")
    
    except Exception as e:
        print(f"שגיאה: {e}")

if __name__ == "__main__":
    main()
