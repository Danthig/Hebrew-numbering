"""
מנוע מספור עברי (גימטריה).

תומך ב:
- מספור 1 עד 999,999
- גרש/גרשיים
- אלפים בסגנון אותיות ("א' א'") או מילים ("אלף א'")
- הימנעות משם ה' (טו/טז במקום יה/יו) — תמיד פעיל
- "לשון נקייה" — החלפת צירופי אותיות שיוצרים מילים לא רצויות (שד→דש)
- ניתוח הפוך: מחרוזת עברית → מספר
"""

from typing import Dict, Optional


class HebrewNumbering:
    """המרת מספרים לעברית ובחזרה, בהתאם למוסכמות הגימטריה."""

    HEBREW_ONES = ['', 'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט']
    HEBREW_TENS = ['', 'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ']
    HEBREW_HUNDREDS = ['', 'ק', 'ר', 'ש', 'ת', 'תק', 'תר', 'תש', 'תת', 'תתק']

    # 10-19: טו/טז במקום יה/יו (הימנעות משם ה') — חלק אינטגרלי מהגימטריה, תמיד פעיל
    TEENS = ['י', 'יא', 'יב', 'יג', 'יד', 'טו', 'טז', 'יז', 'יח', 'יט']

    # "לשון נקייה": החלפת צירוף אותיות שיוצר מילה לא רצויה.
    # ההחלפה מתבצעת על "חלק" שלם (פחות מאלף) לפני הוספת הגרש.
    DEFAULT_CLEAN_SUBSTITUTIONS: Dict[str, str] = {
        'שד': 'דש',   # 304 — שֵׁד (מקובל בכל מקום)
    }
    # אופציונליים — המשתמש מפעיל לפי מנהג
    OPTIONAL_CLEAN_SUBSTITUTIONS: Dict[str, str] = {
        'רע': 'ער',    # 270 — רַע
        'שמד': 'דמש',  # 344 — שְׁמד
    }

    MIN_VALUE = 1
    MAX_VALUE = 999999

    # ------------------------------------------------------------------ #
    # המרה: מספר -> עברית
    # ------------------------------------------------------------------ #
    @staticmethod
    def number_to_hebrew(
        num: int,
        with_geresh: bool = True,
        thousands_style: str = 'letters',
        clean_language: bool = False,
        clean_substitutions: Optional[Dict[str, str]] = None,
    ) -> str:
        """המרת מספר שלם (1..999999) למחרוזת עברית.

        :param with_geresh: הוספת גרש/גרשיים
        :param thousands_style: 'letters' (א' א') או 'words' (אלף א')
        :param clean_language: הפעלת לשון נקייה (שד→דש)
        :param clean_substitutions: החלפות נוספות מעבר לברירת המחדל
        """
        if num < HebrewNumbering.MIN_VALUE or num > HebrewNumbering.MAX_VALUE:
            raise ValueError(
                f"המספר חייב להיות בין {HebrewNumbering.MIN_VALUE} "
                f"ל-{HebrewNumbering.MAX_VALUE}"
            )

        subs = HebrewNumbering._resolve_substitutions(clean_language, clean_substitutions)

        if num >= 1000:
            thousands, remainder = divmod(num, 1000)

            if thousands_style == 'words':
                parts = [HebrewNumbering._thousands_to_words(thousands, with_geresh, subs)]
            else:
                parts = [HebrewNumbering._format_chunk(thousands, with_geresh, subs)]

            if remainder:
                parts.append(HebrewNumbering._format_chunk(remainder, with_geresh, subs))

            return ' '.join(part for part in parts if part)

        return HebrewNumbering._format_chunk(num, with_geresh, subs)

    @staticmethod
    def _resolve_substitutions(
        clean_language: bool,
        clean_substitutions: Optional[Dict[str, str]],
    ) -> Dict[str, str]:
        if not clean_language:
            return {}

        subs = dict(HebrewNumbering.DEFAULT_CLEAN_SUBSTITUTIONS)
        if clean_substitutions:
            subs.update(clean_substitutions)
        return subs

    @staticmethod
    def _chunk_to_raw(num: int) -> str:
        """המרת מספר 1..999 לאותיות עבריות, ללא גרש וללא לשון נקייה."""
        if num < 1 or num > 999:
            raise ValueError("חלק המספר חייב להיות בין 1 ל-999")

        result = ''

        if num >= 100:
            result += HebrewNumbering.HEBREW_HUNDREDS[num // 100]
            num %= 100

        if num >= 10:
            tens, ones = divmod(num, 10)
            if tens == 1:
                result += HebrewNumbering.TEENS[ones]
            else:
                result += HebrewNumbering.HEBREW_TENS[tens]
                if ones > 0:
                    result += HebrewNumbering.HEBREW_ONES[ones]
        elif num > 0:
            result += HebrewNumbering.HEBREW_ONES[num]

        return result

    @staticmethod
    def _format_chunk(num: int, with_geresh: bool, subs: Dict[str, str]) -> str:
        """המרת חלק (1..999) עם לשון נקייה וגרש."""
        raw = HebrewNumbering._chunk_to_raw(num)

        # לשון נקייה: רק כשהחלק כולו שווה למילה הנמנעת (למשל 304 == 'שד')
        if raw in subs:
            raw = subs[raw]

        return HebrewNumbering._apply_geresh(raw) if with_geresh else raw

    @staticmethod
    def _thousands_to_words(thousands: int, with_geresh: bool, subs: Dict[str, str]) -> str:
        """ייצוג מילולי של האלפים."""
        if thousands == 1:
            return 'אלף'
        if thousands == 2:
            return 'אלפיים'
        return f"{HebrewNumbering._format_chunk(thousands, with_geresh, subs)} אלפים"

    @staticmethod
    def _apply_geresh(text: str) -> str:
        """הוספת גרש (אות אחת) או גרשיים (לפני האות האחרונה)."""
        if not text:
            return text
        if len(text) == 1:
            return text + "'"
        return text[:-1] + '"' + text[-1]

    # ------------------------------------------------------------------ #
    # ניתוח הפוך: עברית -> מספר (best-effort, לזיהוי ומיון)
    # ------------------------------------------------------------------ #
    _LETTER_VALUES = {
        'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
        'י': 10, 'כ': 20, 'ך': 20, 'ל': 30, 'מ': 40, 'ם': 40, 'נ': 50, 'ן': 50,
        'ס': 60, 'ע': 70, 'פ': 80, 'ף': 80, 'צ': 90, 'ץ': 90,
        'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400,
    }

    @staticmethod
    def hebrew_to_number(text: str) -> Optional[int]:
        """המרת מחרוזת עברית בחזרה למספר. מחזיר None אם לא ניתן לפענח.

        מטפל בגרש/גרשיים, בטו/טז, בלשון נקייה ובאלפים (אותיות/מילים).
        """
        if not text:
            return None

        cleaned = text.replace('"', '').replace("'", '').replace('׳', '').replace('״', '')
        cleaned = cleaned.strip()
        if not cleaned:
            return None

        # אלפים בסגנון מילים
        if 'אלפים' in cleaned or 'אלפיים' in cleaned or 'אלף' in cleaned:
            return HebrewNumbering._parse_words_thousands(cleaned)

        tokens = cleaned.split()

        if len(tokens) == 2:
            high = HebrewNumbering._gematria_value(tokens[0])
            low = HebrewNumbering._gematria_value(tokens[1])
            if high is not None and low is not None:
                return high * 1000 + low
            return None

        if len(tokens) == 1:
            return HebrewNumbering._gematria_value(tokens[0])

        return None

    @staticmethod
    def _parse_words_thousands(cleaned: str) -> Optional[int]:
        remainder = 0
        thousands = 0

        if 'אלפיים' in cleaned:
            thousands = 2
            rest = cleaned.replace('אלפיים', '').strip()
        elif 'אלפים' in cleaned:
            before, _, after = cleaned.partition('אלפים')
            count = HebrewNumbering._gematria_value(before.strip())
            if count is None:
                return None
            thousands = count
            rest = after.strip()
        elif 'אלף' in cleaned:
            thousands = 1
            rest = cleaned.replace('אלף', '').strip()
        else:
            return None

        if rest:
            remainder = HebrewNumbering._gematria_value(rest) or 0

        return thousands * 1000 + remainder

    @staticmethod
    def _gematria_value(token: str) -> Optional[int]:
        """ערך גימטרי של מחרוזת אותיות (כולל טו/טז ולשון נקייה הפוכה)."""
        if not token:
            return None

        # הפיכת לשון נקייה בחזרה (דש→שד וכו') כדי שהערך הגימטרי יישמר ממילא —
        # הסכום הגימטרי זהה בלי קשר לסדר, אז אין צורך בהיפוך מפורש.
        total = 0
        for char in token:
            value = HebrewNumbering._LETTER_VALUES.get(char)
            if value is None:
                return None
            total += value

        return total if total > 0 else None
