"""
ממשק גרפי מודרני מבוסס HTML/CSS דרך pywebview, מחובר למנוע ה-Python האמיתי.

הפעלה:
    python -m hebrew_renamer.webapp
"""

import os
import sys
import subprocess
from pathlib import Path

try:
    import webview
except ImportError:  # pragma: no cover
    webview = None

from .renamer import FileRenamer
from .gematria import HebrewNumbering


def _webui_dir() -> Path:
    """נתיב תיקיית ה-webui — תומך גם בהרצה רגילה וגם בתוך חבילת PyInstaller."""
    if getattr(sys, 'frozen', False):
        base = Path(getattr(sys, '_MEIPASS', Path(__file__).parent.parent))
        return base / 'hebrew_renamer' / 'webui'
    return Path(__file__).parent / 'webui'


WEBUI_DIR = _webui_dir()


class Api:
    """הגשר בין ה-JavaScript למנוע ה-Python."""

    def __init__(self):
        self.selected_paths = []     # נתיבי הבחירה המקוריים (str)
        self.files = []              # רשימת Path ממוינת, בסדר שבו ישונו
        self.directory = None        # תיקיית הבסיס
        self.mode = None             # 'folder' | 'files'

    # ------------------------- כלי עזר ------------------------- #
    @property
    def _window(self):
        return webview.windows[0] if webview and webview.windows else None

    def _renamer(self):
        base = self.directory or Path.cwd()
        return FileRenamer(str(base))

    @staticmethod
    def _kwargs(opts):
        clean = bool(opts.get('clean_language'))
        subs = None
        if clean and opts.get('clean_extra'):
            subs = dict(HebrewNumbering.OPTIONAL_CLEAN_SUBSTITUTIONS)
        return dict(
            prefix=opts.get('prefix', ''),
            separator=opts.get('separator', '_'),
            start_number=int(opts.get('start_number', 1) or 1),
            numbering_type=opts.get('numbering_type', 'hebrew'),
            with_geresh=bool(opts.get('with_geresh', True)),
            thousands_style=opts.get('thousands_style', 'letters'),
            numeric_padding=int(opts.get('numeric_padding', 0) or 0),
            rename_mode=opts.get('rename_mode', 'replace'),
            clean_language=clean,
            clean_substitutions=subs,
        )

    def _relist(self, opts):
        self.files = FileRenamer.get_selected_files(
            self.selected_paths,
            recursive=bool(opts.get('recursive')),
            sort_strategy=opts.get('sort', 'natural'),
        )

    def _payload(self):
        return {
            'ok': True,
            'label': str(self.directory) + (
                f"  ({len(self.files)} קבצים)" if self.mode == 'folder' else
                f"  ({len(self.files)} נבחרו)"
            ),
            'files': [p.name for p in self.files],
        }

    # ------------------------- בחירה ------------------------- #
    def pick_folder(self, opts):
        win = self._window
        if not win:
            return {'ok': False, 'error': 'חלון לא זמין'}
        result = win.create_file_dialog(webview.FOLDER_DIALOG)
        if not result:
            return {'ok': False}
        folder = Path(result[0])
        self.selected_paths = [str(folder)]
        self.directory = folder
        self.mode = 'folder'
        self._relist(opts)
        return self._payload()

    def pick_files(self, opts):
        win = self._window
        if not win:
            return {'ok': False, 'error': 'חלון לא זמין'}
        result = win.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=True)
        if not result:
            return {'ok': False}
        self.selected_paths = [str(p) for p in result]
        self.directory = Path(result[0]).parent
        self.mode = 'files'
        self._relist(opts)
        return self._payload()

    def relist(self, opts):
        if not self.selected_paths:
            return {'ok': False}
        self._relist(opts)
        return self._payload()

    # ------------------------- ביצוע ------------------------- #
    def rename(self, opts):
        if not self.files:
            return {'error': 'לא נבחרו קבצים'}
        try:
            renamer = self._renamer()
            results = renamer.rename_files(self.files, **self._kwargs(opts))
        except Exception as exc:  # pragma: no cover
            return {'error': str(exc)}

        success = sum(1 for *_, ok in results if ok)
        fail = len(results) - success

        # רענון רשימת הקבצים לאחר השינוי
        if self.mode == 'folder' and self.directory and self.directory.is_dir():
            self._relist(opts)
        else:
            new_files = []
            for old_name, new_name, ok in results:
                src = next((f for f in self.files if f.name == old_name), None)
                if src is not None:
                    new_files.append(src.with_name(new_name) if ok else src)
            self.files = new_files

        return {
            'success': success, 'fail': fail, 'total': len(results),
            'files': [p.name for p in self.files],
        }

    def undo(self):
        renamer = FileRenamer(str(self.directory or Path.cwd()))
        if not renamer.can_undo():
            return {'ok': False}
        results = renamer.undo_last() or []
        count = sum(1 for *_, ok in results if ok)
        if self.mode == 'folder' and self.directory and self.directory.is_dir():
            self.files = FileRenamer.get_selected_files([str(self.directory)])
        return {'ok': True, 'count': count, 'files': [p.name for p in self.files]}

    def can_undo(self):
        try:
            return FileRenamer(str(self.directory or Path.cwd())).can_undo()
        except Exception:
            return False

    # ------------------------- שונות ------------------------- #
    def open_location(self):
        if not self.directory:
            return
        try:
            if sys.platform.startswith('win'):
                os.startfile(self.directory)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', str(self.directory)])
            else:
                subprocess.Popen(['xdg-open', str(self.directory)])
        except Exception:
            pass

    def exit_app(self):
        win = self._window
        if win:
            win.destroy()


def main():
    if webview is None:
        print("pywebview אינו מותקן. התקן עם: pip install pywebview", file=sys.stderr)
        return 1

    api = Api()
    webview.create_window(
        'תוכנת שינוי שם קבצים',
        url=str(WEBUI_DIR / 'index.html'),
        js_api=api,
        width=1180,
        height=900,
        min_size=(900, 680),
        background_color='#eef1ff',
    )

    icon = WEBUI_DIR / 'icon.ico'
    try:
        webview.start(icon=str(icon))
    except TypeError:
        # גרסאות/backends שאינם תומכים בפרמטר icon
        webview.start()
    return 0


if __name__ == '__main__':
    sys.exit(main())
