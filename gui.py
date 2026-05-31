"""
נקודת כניסה לממשק הגרפי (תאימות לאחור עבור run.bat / run.sh).

מעדיף את הממשק המודרני (HTML/CSS דרך pywebview); אם pywebview אינו זמין —
נופל בחזרה לממשק ה-tkinter הקלאסי (ללא תלויות).
"""

import sys


def main():
    try:
        import webview  # noqa: F401
        from hebrew_renamer.webapp import main as web_main
        return web_main()
    except Exception as exc:
        print(f"(ממשק מודרני לא זמין: {exc} — עובר ל-tkinter)", file=sys.stderr)
        from hebrew_renamer.gui import main as tk_main
        return tk_main()


if __name__ == '__main__':
    main()
