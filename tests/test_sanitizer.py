import unittest

from hebrew_renamer.sanitizer import (
    sanitize_filename,
    is_valid_filename,
    is_path_too_long,
)
from pathlib import Path


class SanitizeTests(unittest.TestCase):
    def test_illegal_chars_replaced(self):
        self.assertEqual(sanitize_filename('a/b:c?.txt'), 'a_b_c_.txt')

    def test_trailing_dot_and_space_stripped(self):
        self.assertEqual(sanitize_filename('name. '), 'name')
        self.assertEqual(sanitize_filename('name...'), 'name')

    def test_reserved_name_prefixed(self):
        self.assertEqual(sanitize_filename('CON'), '_CON')
        self.assertEqual(sanitize_filename('con.txt'), '_con.txt')

    def test_empty_becomes_replacement(self):
        self.assertEqual(sanitize_filename(''), '_')

    def test_long_name_truncated_keeps_suffix(self):
        name = 'a' * 300 + '.txt'
        result = sanitize_filename(name)
        self.assertTrue(len(result) <= 255)
        self.assertTrue(result.endswith('.txt'))


class ValidateTests(unittest.TestCase):
    def test_valid_name(self):
        ok, reason = is_valid_filename('photo_01.jpg')
        self.assertTrue(ok)
        self.assertIsNone(reason)

    def test_illegal_char(self):
        ok, reason = is_valid_filename('a?b.txt')
        self.assertFalse(ok)
        self.assertIn('תו אסור', reason)

    def test_reserved(self):
        ok, reason = is_valid_filename('NUL')
        self.assertFalse(ok)
        self.assertIn('שמור', reason)

    def test_trailing_dot(self):
        ok, _ = is_valid_filename('name.')
        self.assertFalse(ok)

    def test_empty(self):
        ok, _ = is_valid_filename('   ')
        self.assertFalse(ok)


class PathLengthTests(unittest.TestCase):
    def test_short_path_ok(self):
        self.assertFalse(is_path_too_long(Path('C:/a/b.txt')))

    def test_long_path_flagged(self):
        self.assertTrue(is_path_too_long(Path('C:/' + 'a' * 300)))


if __name__ == '__main__':
    unittest.main()
