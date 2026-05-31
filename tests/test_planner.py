import tempfile
import unittest
from pathlib import Path

from hebrew_renamer.planner import build_plan, execute_plan


def _make_files(base, names):
    paths = []
    for name in names:
        p = base / name
        p.write_text(name, encoding='utf-8')
        paths.append(p)
    return paths


class ConflictDetectionTests(unittest.TestCase):
    def test_duplicate_target_is_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            a, b = _make_files(base, ['a.txt', 'b.txt'])
            plan = build_plan([(a, 'same.txt'), (b, 'same.txt')])
            self.assertTrue(plan.has_conflicts)
            self.assertEqual(len(plan.conflicts), 2)

    def test_existing_file_target_is_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            a, existing = _make_files(base, ['a.txt', 'taken.txt'])
            plan = build_plan([(a, 'taken.txt')])
            self.assertTrue(plan.has_conflicts)

    def test_illegal_target_is_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            (a,) = _make_files(base, ['a.txt'])
            plan = build_plan([(a, 'bad?name.txt')])
            self.assertTrue(plan.has_conflicts)

    def test_clean_plan_no_conflicts(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            a, b = _make_files(base, ['a.txt', 'b.txt'])
            plan = build_plan([(a, '1.txt'), (b, '2.txt')])
            self.assertFalse(plan.has_conflicts)


class AtomicRenameTests(unittest.TestCase):
    def test_chain_rename_preserves_content(self):
        # 1.txt -> 2.txt, 2.txt -> 3.txt  (target of one == source of another)
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            f1, f2 = _make_files(base, ['1.txt', '2.txt'])
            plan = build_plan([(f1, '2.txt'), (f2, '3.txt')])
            self.assertFalse(plan.has_conflicts)
            results = execute_plan(plan)
            self.assertTrue(all(ok for *_, ok in results))
            self.assertEqual((base / '2.txt').read_text(), '1.txt')
            self.assertEqual((base / '3.txt').read_text(), '2.txt')

    def test_swap_rename(self):
        # a <-> b  (full cycle)
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            a, b = _make_files(base, ['a.txt', 'b.txt'])
            plan = build_plan([(a, 'b.txt'), (b, 'a.txt')])
            self.assertFalse(plan.has_conflicts)
            execute_plan(plan)
            self.assertEqual((base / 'a.txt').read_text(), 'b.txt')
            self.assertEqual((base / 'b.txt').read_text(), 'a.txt')

    def test_cancel_stops_execution(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            files = _make_files(base, [f'{i}.txt' for i in range(5)])
            pairs = [(f, f'new_{i}.txt') for i, f in enumerate(files)]
            plan = build_plan(pairs)
            results = execute_plan(plan, cancel_check=lambda: True)
            # ביטול מיידי -> אף קובץ לא שונה
            self.assertTrue(all(not (base / f'new_{i}.txt').exists() for i in range(5)))

    def test_progress_callback_called(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            files = _make_files(base, ['a.txt', 'b.txt'])
            plan = build_plan([(files[0], 'x.txt'), (files[1], 'y.txt')])
            calls = []
            execute_plan(plan, progress_cb=lambda *a: calls.append(a))
            self.assertEqual(len(calls), 2)


if __name__ == '__main__':
    unittest.main()
