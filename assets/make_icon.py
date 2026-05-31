"""
מחולל אייקון התוכנה — אריח בגרדיאנט המותג עם האות "א".
יוצר icon.png (512) ו-icon.ico (רב-גודל) באמצעות Pillow בלבד.

הרצה:
    python assets/make_icon.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = Path(__file__).parent
SS = 1024  # supersampling — נרנדר בגדול ונקטין לחדות מקסימלית

# צבעי המותג (תואם ל-CSS של הממשק) — גוון עשיר עם עומק
TOP = (91, 79, 224)        # #5b4fe0 אינדיגו עמוק
BOTTOM = (146, 96, 248)    # #9260f8 סגול
GLYPH = "א"


def _lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _gradient(size, top, bottom):
    """גרדיאנט אנכי חלק."""
    img = Image.new("RGB", (size, size), top)
    draw = ImageDraw.Draw(img)
    for y in range(size):
        draw.line([(0, y), (size, y)], fill=_lerp(top, bottom, y / (size - 1)))
    return img


def _rounded_mask(size, radius):
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return mask


def _highlight(size):
    """הילה לבנה עדינה בחלק העליון לתחושת עומק."""
    h = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(h)
    d.ellipse([-size * 0.25, -size * 0.55, size * 1.25, size * 0.55], fill=48)
    return h.filter(ImageFilter.GaussianBlur(size * 0.06))


def _load_font(px):
    for name in ("segoeuib.ttf", "arialbd.ttf", "ariblk.ttf"):
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            continue
    return ImageFont.load_default()


def build():
    # רקע גרדיאנט עם פינות מעוגלות
    base = _gradient(SS, TOP, BOTTOM).convert("RGBA")
    base.putalpha(_rounded_mask(SS, radius=int(SS * 0.225)))

    # הילה עליונה
    glow = Image.new("RGBA", (SS, SS), (255, 255, 255, 0))
    glow.putalpha(_highlight(SS))
    glow.putalpha(Image.composite(glow.getchannel("A"), Image.new("L", (SS, SS), 0), _rounded_mask(SS, int(SS * 0.225))))
    base = Image.alpha_composite(base, glow)

    # האות "א"
    font = _load_font(int(SS * 0.62))
    draw = ImageDraw.Draw(base)
    bbox = draw.textbbox((0, 0), GLYPH, font=font)
    gw, gh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (SS - gw) / 2 - bbox[0]
    y = (SS - gh) / 2 - bbox[1] - SS * 0.01

    # צל רך מתחת לאות
    shadow = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((x, y + SS * 0.015), GLYPH, font=font, fill=(40, 20, 90, 130))
    shadow = shadow.filter(ImageFilter.GaussianBlur(SS * 0.02))
    base = Image.alpha_composite(base, shadow)

    # האות הלבנה
    draw = ImageDraw.Draw(base)
    draw.text((x, y), GLYPH, font=font, fill=(255, 255, 255, 255))

    # שמירה
    png = base.resize((512, 512), Image.LANCZOS)
    png.save(OUT / "icon.png")

    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_master = base.resize((256, 256), Image.LANCZOS)
    ico_master.save(OUT / "icon.ico", format="ICO", sizes=ico_sizes)

    # עותק בשורש לשימוש ב-build וב-tkinter
    ico_master.save(OUT.parent / "app.ico", format="ICO", sizes=ico_sizes)

    # עותקים בתוך החבילה (ל-favicon, ל-pywebview ולהפצת pip)
    webui = OUT.parent / "hebrew_renamer" / "webui"
    png.save(webui / "icon.png")
    ico_master.save(webui / "icon.ico", format="ICO", sizes=ico_sizes)

    print("נוצרו: assets/icon.png, assets/icon.ico, app.ico, hebrew_renamer/webui/icon.{png,ico}")


if __name__ == "__main__":
    build()
