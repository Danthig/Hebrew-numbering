import tempfile
import unittest
from pathlib import Path

from hebrew_renamer.renamer import FileRenamer
from hebrew_renamer.transaction import HistoryJournal


class UndoTests(unittest.TestCase):
    def _renamer(self, directory):
        journal = HistoryJournal(Path(directory) / 'hist.json')
        return FileRenamer(directory, journal=journal)

    def test_undo_restores_names(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            for n in ['a.txt', 'b.txt', 'c.txt']:
                (base / n).write_text(n, encoding='utf-8')
            files = [base / 'a.txt', base / 'b.txt', base / 'c.txt']

            r = self._renamer(d)
            r.rename_files(files, numbering_type='numeric_no_dot', numeric_padding=2)
            self.assertTrue((base / '01.txt').exists())

            self.assertTrue(r.can_undo())
            r.undo_last()
            self.assertTrue((base / 'a.txt').exists())
            self.assertTrue((base / 'b.txt').exists())
            self.assertFalse((base / '01.txt').exists())

    def test_undo_when_nothing_to_undo(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._renamer(d)
            self.assertFalse(r.can_undo())
            self.assertIsNone(r.undo_last())

    def test_chain_rename_then_undo(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            (base / '1.txt').write_text('one', encoding='utf-8')
            (base / '2.txt').write_text('two', encoding='utf-8')
            files = [base / '1.txt', base / '2.txt']

            r = self._renamer(d)
            r.rename_files(files, numbering_type='numeric_no_dot', start_number=2)
            self.assertEqual((base / '2.txt').read_text(), 'one')

            r.undo_last()
            self.assertEqual((base / '1.txt').read_text(), 'one')
            self.assertEqual((base / '2.txt').read_text(), 'two')


if __name__ == '__main__':
    unittest.main()
