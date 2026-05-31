import unittest

from hebrew_renamer.gematria import HebrewNumbering as H


class BasicNumberingTests(unittest.TestCase):
    def test_ones(self):
        self.assertEqual(H.number_to_hebrew(1), "א'")
        self.assertEqual(H.number_to_hebrew(9), "ט'")

    def test_divine_name_avoidance(self):
        # טו/טז במקום יה/יו
        self.assertEqual(H.number_to_hebrew(15), 'ט"ו')
        self.assertEqual(H.number_to_hebrew(16), 'ט"ז')
        self.assertEqual(H.number_to_hebrew(115), 'קט"ו')
        self.assertEqual(H.number_to_hebrew(116), 'קט"ז')

    def test_hundreds(self):
        self.assertEqual(H.number_to_hebrew(100), "ק'")
        self.assertEqual(H.number_to_hebrew(500), 'ת"ק')
        self.assertEqual(H.number_to_hebrew(900), 'תת"ק')

    def test_without_geresh(self):
        self.assertEqual(H.number_to_hebrew(15, with_geresh=False), 'טו')
        self.assertEqual(H.number_to_hebrew(304, with_geresh=False), 'שד')

    def test_bounds(self):
        with self.assertRaises(ValueError):
            H.number_to_hebrew(0)
        with self.assertRaises(ValueError):
            H.number_to_hebrew(1000000)


class ThousandsTests(unittest.TestCase):
    def test_letters_style(self):
        self.assertEqual(H.number_to_hebrew(1000, thousands_style='letters'), "א'")
        self.assertEqual(H.number_to_hebrew(1001, thousands_style='letters'), "א' א'")
        self.assertEqual(H.number_to_hebrew(5778, thousands_style='letters'), 'ה\' תשע"ח')

    def test_words_style(self):
        self.assertEqual(H.number_to_hebrew(1000, thousands_style='words'), 'אלף')
        self.assertEqual(H.number_to_hebrew(1001, thousands_style='words'), "אלף א'")
        self.assertEqual(H.number_to_hebrew(2001, thousands_style='words'), "אלפיים א'")
        self.assertEqual(H.number_to_hebrew(3001, thousands_style='words'), "ג' אלפים א'")


class CleanLanguageTests(unittest.TestCase):
    def test_default_off(self):
        self.assertEqual(H.number_to_hebrew(304), 'ש"ד')

    def test_shad_to_dash(self):
        self.assertEqual(H.number_to_hebrew(304, clean_language=True), 'ד"ש')
        self.assertEqual(
            H.number_to_hebrew(304, clean_language=True, with_geresh=False), 'דש'
        )

    def test_clean_inside_large_number(self):
        # 1304 -> "א' ד\"ש"
        self.assertEqual(H.number_to_hebrew(1304, clean_language=True), "א' ד\"ש")

    def test_clean_does_not_overtrigger(self):
        # 704 = תשד מכיל "שד" אך אינו 304 — לא אמור להשתנות
        self.assertEqual(H.number_to_hebrew(704, clean_language=True), 'תש"ד')

    def test_optional_substitutions(self):
        opt = H.OPTIONAL_CLEAN_SUBSTITUTIONS
        self.assertEqual(
            H.number_to_hebrew(270, clean_language=True, clean_substitutions=opt), 'ע"ר'
        )
        self.assertEqual(
            H.number_to_hebrew(344, clean_language=True, clean_substitutions=opt), 'דמ"ש'
        )

    def test_optional_off_by_default(self):
        # רע לא משתנה ללא ההחלפות המורחבות
        self.assertEqual(H.number_to_hebrew(270, clean_language=True), 'ר"ע')


class ReverseParsingTests(unittest.TestCase):
    def test_round_trip_under_thousand(self):
        for n in range(1, 1000):
            text = H.number_to_hebrew(n)
            self.assertEqual(H.hebrew_to_number(text), n, f"failed at {n}")

    def test_reverse_clean_language(self):
        # ד"ש (304 בלשון נקייה) חוזר ל-304 (הסכום הגימטרי זהה)
        self.assertEqual(H.hebrew_to_number('ד"ש'), 304)

    def test_reverse_thousands(self):
        self.assertEqual(H.hebrew_to_number("א' א'"), 1001)
        self.assertEqual(H.hebrew_to_number("אלף א'"), 1001)
        self.assertEqual(H.hebrew_to_number("אלפיים א'"), 2001)

    def test_reverse_invalid(self):
        self.assertIsNone(H.hebrew_to_number(''))
        self.assertIsNone(H.hebrew_to_number('hello'))


if __name__ == '__main__':
    unittest.main()
