from pathlib import Path
import tempfile
import unittest

from file_renamer import FileRenamer, HebrewNumbering


class HebrewNumberingTests(unittest.TestCase):
    def test_hebrew_numbering_above_thousand_letters(self):
        self.assertEqual(HebrewNumbering.number_to_hebrew(1000, True, 'letters'), "א'")
        self.assertEqual(HebrewNumbering.number_to_hebrew(1001, True, 'letters'), "א' א'")
        self.assertEqual(HebrewNumbering.number_to_hebrew(1015, True, 'letters'), "א' ט\"ו")
        self.assertEqual(HebrewNumbering.number_to_hebrew(5778, True, 'letters'), "ה' תשע\"ח")

    def test_hebrew_numbering_above_thousand_words(self):
        self.assertEqual(HebrewNumbering.number_to_hebrew(1000, True, 'words'), "אלף")
        self.assertEqual(HebrewNumbering.number_to_hebrew(1001, True, 'words'), "אלף א'")
        self.assertEqual(HebrewNumbering.number_to_hebrew(2001, True, 'words'), "אלפיים א'")
        self.assertEqual(HebrewNumbering.number_to_hebrew(3001, True, 'words'), "ג' אלפים א'")


class FileRenamerNumberFormattingTests(unittest.TestCase):
    def test_numeric_padding_without_dot(self):
        self.assertEqual(
            FileRenamer.format_number(1, numbering_type='numeric_no_dot', numeric_padding=2),
            '01',
        )
        self.assertEqual(
            FileRenamer.format_number(10, numbering_type='numeric_no_dot', numeric_padding=2),
            '10',
        )
        self.assertEqual(
            FileRenamer.format_number(1, numbering_type='numeric_no_dot', numeric_padding=3),
            '001',
        )
        self.assertEqual(
            FileRenamer.format_number(10, numbering_type='numeric_no_dot', numeric_padding=3),
            '010',
        )
        self.assertEqual(
            FileRenamer.format_number(100, numbering_type='numeric_no_dot', numeric_padding=3),
            '100',
        )

    def test_numeric_padding_with_dot(self):
        self.assertEqual(
            FileRenamer.format_number(3, numbering_type='numeric', numeric_padding=2),
            '03.',
        )
        self.assertEqual(
            FileRenamer.format_number(12, numbering_type='numeric', numeric_padding=3),
            '012.',
        )

    def test_rename_files_uses_numeric_padding(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            files = []
            for name in ['a.txt', 'b.txt', 'c.txt']:
                path = base / name
                path.write_text('x', encoding='utf-8')
                files.append(path)

            results = FileRenamer(temp_dir).rename_files(
                files,
                numbering_type='numeric_no_dot',
                numeric_padding=2,
                prefix='',
                separator='_',
            )

            self.assertEqual(
                results,
                [('a.txt', '01.txt', True), ('b.txt', '02.txt', True), ('c.txt', '03.txt', True)],
            )
            self.assertTrue((base / '01.txt').exists())
            self.assertTrue((base / '02.txt').exists())
            self.assertTrue((base / '03.txt').exists())


if __name__ == '__main__':
    unittest.main()
