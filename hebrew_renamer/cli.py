"""
ממשק שורת-פקודה לשינוי שמות קבצים עם מספור עברי.

דוגמאות:
    python -m hebrew_renamer ./photos --prefix תמונה --type hebrew
    python -m hebrew_renamer ./docs --type numeric --padding 3 --dry-run
    python -m hebrew_renamer ./photos --clean-language
    python -m hebrew_renamer --undo
"""

import argparse
import sys
from pathlib import Path

from .renamer import FileRenamer
from .gematria import HebrewNumbering


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='hebrew_renamer',
        description='שינוי שמות קבצים מרובים עם מספור עברי / מספרי',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument('directory', nargs='?', help='התיקייה לעיבוד')

    parser.add_argument('--prefix', default='', help='תחילית לשם הקובץ')
    parser.add_argument('--separator', default='_', help='תו הפרדה (ברירת מחדל: _)')
    parser.add_argument(
        '--type', dest='numbering_type', default='hebrew',
        choices=['hebrew', 'numeric', 'numeric_no_dot'],
        help='סוג המספור',
    )
    parser.add_argument('--start', type=int, default=1, help='מספר התחלה')
    parser.add_argument('--padding', type=int, default=0, help='אפסים מובילים (0/2/3)')
    parser.add_argument(
        '--no-geresh', action='store_true', help='ללא גרש/גרשיים (עברית)',
    )
    parser.add_argument(
        '--thousands', default='letters', choices=['letters', 'words'],
        help='סגנון אלפים בעברית',
    )
    parser.add_argument(
        '--mode', dest='rename_mode', default='replace',
        choices=['replace', 'prepend', 'append'],
        help='אופן השינוי',
    )
    parser.add_argument(
        '--clean-language', action='store_true',
        help='מספור בלשון נקייה (שד→דש)',
    )
    parser.add_argument(
        '--clean-extra', action='store_true',
        help='לשון נקייה מורחבת (כולל רע→ער, שמד→דמש)',
    )
    parser.add_argument(
        '--recursive', '-r', action='store_true', help='כלול תתי-תיקיות',
    )
    parser.add_argument(
        '--sort', default='natural',
        choices=['natural', 'name', 'date', 'size', 'type'],
        help='אסטרטגיית מיון',
    )
    parser.add_argument(
        '--dry-run', '-n', action='store_true',
        help='הצגת תצוגה מקדימה בלבד, ללא ביצוע',
    )
    parser.add_argument(
        '--undo', action='store_true', help='ביטול הריצה האחרונה',
    )
    parser.add_argument(
        '--yes', '-y', action='store_true', help='ביצוע ללא בקשת אישור',
    )
    return parser


def _clean_substitutions(args):
    if not args.clean_language:
        return None
    if args.clean_extra:
        return dict(HebrewNumbering.OPTIONAL_CLEAN_SUBSTITUTIONS)
    return None


def run(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Undo
    if args.undo:
        return _run_undo()

    if not args.directory:
        parser.error('יש לציין תיקייה (או --undo)')

    directory = Path(args.directory)
    if not directory.exists():
        print(f"שגיאה: הנתיב '{directory}' לא קיים", file=sys.stderr)
        return 1

    renamer = FileRenamer(str(directory))
    files = renamer.get_files(recursive=args.recursive, sort_strategy=args.sort)

    if not files:
        print('לא נמצאו קבצים בתיקייה')
        return 0

    kwargs = dict(
        prefix=args.prefix,
        numbering_type=args.numbering_type,
        with_geresh=not args.no_geresh,
        separator=args.separator,
        start_number=args.start,
        thousands_style=args.thousands,
        numeric_padding=args.padding,
        rename_mode=args.rename_mode,
        clean_language=args.clean_language,
        clean_substitutions=_clean_substitutions(args),
    )

    plan = renamer.build_plan(files, **kwargs)

    print(f"\nנמצאו {len(files)} קבצים:\n")
    for item in plan.items:
        arrow = '→'
        marker = '  '
        print(f"{marker}{item.source.name} {arrow} {item.target_name}")

    if plan.has_conflicts:
        print(f"\n⚠ זוהו {len(plan.conflicts)} התנגשויות:")
        for conflict in plan.conflicts:
            print(f"  ✗ {conflict.item.source.name}: {conflict.reason}")

    if args.dry_run:
        print('\n(dry-run — לא בוצע שינוי)')
        return 0

    if not args.yes:
        answer = input(f"\nלבצע שינוי שם ל-{len(plan.actionable_items)} קבצים? [y/N] ")
        if answer.strip().lower() not in ('y', 'yes', 'כ', 'כן'):
            print('בוטל.')
            return 0

    results = renamer.rename_files(files, **kwargs)
    return _report(results)


def _run_undo() -> int:
    renamer = FileRenamer(str(Path.cwd()))
    if not renamer.can_undo():
        print('אין פעולה לביטול.')
        return 0

    results = renamer.undo_last()
    print('בוטלה הריצה האחרונה:')
    return _report(results or [])


def _report(results) -> int:
    successes = sum(1 for _, _, ok in results if ok)
    failures = len(results) - successes

    for old, new, ok in results:
        status = '✓' if ok else '✗'
        print(f"  {status} {old} → {new}")

    print(f"\nבוצע: {successes}/{len(results)}")
    return 0 if failures == 0 else 2


if __name__ == '__main__':
    sys.exit(run())
