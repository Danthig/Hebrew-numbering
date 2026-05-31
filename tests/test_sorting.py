import tempfile
import unittest
from pathlib import Path

from hebrew_renamer.sorting import natsorted, sort_files


class NaturalSortTests(unittest.TestCase):
    def test_natural_order(self):
        names = ['file10', 'file2', 'file1']
        self.assertEqual(natsorted(names), ['file1', 'file2', 'file10'])

    def test_natural_beats_lexical(self):
        names = ['1', '10', '2', '20', '3']
        self.assertEqual(natsorted(names), ['1', '2', '3', '10', '20'])


class SortStrategyTests(unittest.TestCase):
    def test_sort_by_name(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            files = []
            for n in ['b.txt', 'a.txt', 'c.txt']:
                p = base / n
                p.write_text('x')
                files.append(p)
            result = sort_files(files, strategy='name')
            self.assertEqual([p.name for p in result], ['a.txt', 'b.txt', 'c.txt'])

    def test_sort_by_type(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            files = []
            for n in ['z.jpg', 'a.txt', 'b.jpg']:
                p = base / n
                p.write_text('x')
                files.append(p)
            result = sort_files(files, strategy='type')
            # קבצי .jpg לפני .txt
            self.assertEqual([p.suffix for p in result], ['.jpg', '.jpg', '.txt'])

    def test_reverse(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            files = []
            for n in ['a.txt', 'b.txt', 'c.txt']:
                p = base / n
                p.write_text('x')
                files.append(p)
            result = sort_files(files, strategy='name', reverse=True)
            self.assertEqual([p.name for p in result], ['c.txt', 'b.txt', 'a.txt'])

    def test_invalid_strategy(self):
        with self.assertRaises(ValueError):
            sort_files([], strategy='nope')


if __name__ == '__main__':
    unittest.main()
