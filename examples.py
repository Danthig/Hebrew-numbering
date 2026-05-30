"""
דוגמאות שימוש בתוכנת שינוי שם קבצים
"""

from file_renamer import FileRenamer, HebrewNumbering
from pathlib import Path

def example_1_hebrew_numbering():
    """דוגמה 1: מספור בעברית עם גרש"""
    print("=" * 50)
    print("דוגמה 1: מספור בעברית עם גרש")
    print("=" * 50)
    
    # הדפסת מספרים בעברית
    for i in range(1, 11):
        print(f"{i}: {HebrewNumbering.number_to_hebrew(i, with_geresh=True)}")

def example_2_hebrew_no_geresh():
    """דוגמה 2: מספור בעברית ללא גרש"""
    print("\n" + "=" * 50)
    print("דוגמה 2: מספור בעברית ללא גרש")
    print("=" * 50)
    
    for i in range(1, 11):
        print(f"{i}: {HebrewNumbering.number_to_hebrew(i, with_geresh=False)}")

def example_3_numeric_numbering():
    """דוגמה 3: הדגמת מספור מספרים"""
    print("\n" + "=" * 50)
    print("דוגמה 3: מספור מספרים")
    print("=" * 50)

    for i in [1, 2, 3, 10, 11, 100]:
        print(f"רגיל: {FileRenamer.format_number(i, 'numeric_no_dot')}")
        print(f"עם אפס אחד: {FileRenamer.format_number(i, 'numeric_no_dot', numeric_padding=2)}")
        print(f"עם שני אפסים: {FileRenamer.format_number(i, 'numeric_no_dot', numeric_padding=3)}")

def example_4_simulate_rename():
    """דוגמה 4: הדמיית שינוי שם קבצים"""
    print("\n" + "=" * 50)
    print("דוגמה 4: הדמיית שינוי שם קבצים")
    print("=" * 50)
    
    # דוגמה עם קבצים דמה
    sample_files = [
        "photo1.jpg",
        "photo2.jpg",
        "photo3.jpg",
        "document.pdf",
        "video.mp4"
    ]
    
    print("\n▶ דוגמה א: עם מספור בעברית וגרש")
    for idx, filename in enumerate(sample_files, start=1):
        extension = Path(filename).suffix
        number = HebrewNumbering.number_to_hebrew(idx, with_geresh=True)
        new_name = f"קובץ_{number}{extension}"
        print(f"  {filename} → {new_name}")
    
    print("\n▶ דוגמה ב: עם מספור בעברית ללא גרש")
    for idx, filename in enumerate(sample_files, start=1):
        extension = Path(filename).suffix
        number = HebrewNumbering.number_to_hebrew(idx, with_geresh=False)
        new_name = f"מסמך_{number}{extension}"
        print(f"  {filename} → {new_name}")
    
    print("\n▶ דוגמה ג: עם מספור מספרים עם אפס מוביל")
    for idx, filename in enumerate(sample_files, start=1):
        extension = Path(filename).suffix
        number = FileRenamer.format_number(idx, 'numeric_no_dot', numeric_padding=2)
        new_name = f"file_{number}{extension}"
        print(f"  {filename} → {new_name}")

def example_5_hebrew_numbers():
    """דוגמה 5: מספרים בעברית מורכבים"""
    print("\n" + "=" * 50)
    print("דוגמה 5: מספרים בעברית מורכבים")
    print("=" * 50)
    
    numbers = [1, 5, 10, 15, 20, 100, 123, 500, 999, 1000, 1001, 2001, 5778]
    
    print("\nעם גרש/גרשיים:")
    for num in numbers:
        hebrew = HebrewNumbering.number_to_hebrew(num, with_geresh=True)
        print(f"  {num:>3} = {hebrew}")
    
    print("\nללא גרש/גרשיים:")
    for num in numbers:
        hebrew = HebrewNumbering.number_to_hebrew(num, with_geresh=False)
        print(f"  {num:>4} = {hebrew}")

    print("\nסגנון אלפים מילולי:")
    for num in [1000, 1001, 2001, 5778]:
        hebrew = HebrewNumbering.number_to_hebrew(num, with_geresh=True, thousands_style='words')
        print(f"  {num:>4} = {hebrew}")

def example_6_custom_separator():
    """דוגמה 6: תוי הפרדה שונים"""
    print("\n" + "=" * 50)
    print("דוגמה 6: תוי הפרדה שונים")
    print("=" * 50)
    
    filename = "photo.jpg"
    extension = Path(filename).suffix
    prefix = "תמונה"
    number = HebrewNumbering.number_to_hebrew(1, with_geresh=True)
    
    separators = ['_', '-', ' ', '_-_', '']
    
    for sep in separators:
        new_name = f"{prefix}{sep}{number}{extension}"
        print(f"  תו הפרדה '{sep}': {new_name}")

if __name__ == "__main__":
    # הרצת כל הדוגמאות
    example_1_hebrew_numbering()
    example_2_hebrew_no_geresh()
    example_3_numeric_numbering()
    example_4_simulate_rename()
    example_5_hebrew_numbers()
    example_6_custom_separator()
    
    print("\n" + "=" * 50)
    print("עבור שימוש עם קבצים בפועל:")
    print("1. הרץ את gui.py לממשק גרפי")
    print("2. או השתמש ב-FileRenamer class ישירות בקוד שלך")
    print("=" * 50)
