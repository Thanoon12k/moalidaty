"""
Receipt image generator.

Produces a PNG image that looks like a real payment receipt, ready for
print or sharing. Uses Pillow for drawing and arabic_reshaper + python-bidi
for correct Arabic text rendering.

If the Cairo font files are not present in staticfiles/fonts/, the generator
falls back to Pillow's built-in font (Latin only — Arabic will look broken).
To fix: download Cairo-Regular.ttf and Cairo-Bold.ttf and place them in:
    moalidatna-server/staticfiles/fonts/
"""

from __future__ import annotations

import io
import os
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False


# ─── Colour palette ──────────────────────────────────────────────────────────
PRIMARY     = (22,  78, 160)   # deep blue   #164EA0
PRIMARY_L   = (235, 242, 255)  # light blue  #EBF2FF
ACCENT      = (34,  139,  34)  # green       #228B22
ACCENT_L    = (235, 255, 235)  # light green #EBFFEB
WHITE       = (255, 255, 255)
GREY_L      = (245, 245, 247)
TEXT_DARK   = (20,  20,  30)
TEXT_MID    = (90,  90, 100)
DIVIDER     = (210, 210, 220)

W, H = 640, 980   # canvas size in pixels


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _ar(text: str) -> str:
    """Reshape + bidi-reorder Arabic text for PIL rendering."""
    if ARABIC_SUPPORT:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    return text


def _load_fonts():
    fonts_dir = os.path.join(settings.BASE_DIR, 'staticfiles', 'fonts')
    reg  = os.path.join(fonts_dir, 'Cairo-Regular.ttf')
    bold = os.path.join(fonts_dir, 'Cairo-Bold.ttf')
    try:
        if os.path.exists(reg) and os.path.exists(bold):
            return {
                'sm':    ImageFont.truetype(reg,  16),
                'md':    ImageFont.truetype(reg,  20),
                'lg':    ImageFont.truetype(bold, 24),
                'xl':    ImageFont.truetype(bold, 30),
                'title': ImageFont.truetype(bold, 36),
            }
    except Exception:
        pass
    default = ImageFont.load_default()
    return {k: default for k in ('sm', 'md', 'lg', 'xl', 'title')}


def _center_text(draw, y, text, font, color, width=W):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) // 2, y), text, fill=color, font=font)


def _right_text(draw, x, y, text, font, color):
    """Draw text anchored to the right."""
    draw.text((x, y), text, fill=color, font=font, anchor='ra')


def _left_text(draw, x, y, text, font, color):
    draw.text((x, y), text, fill=color, font=font, anchor='la')


# ─── Month names in Arabic ────────────────────────────────────────────────────
MONTHS_AR = [
    '', 'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
    'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر',
]


# ─── Main generator ──────────────────────────────────────────────────────────

def generate_receipt_image(receipt) -> None:
    """
    Generate a PNG receipt image and save it to receipt.receipt_image.
    Modifies the Receipt instance in-place (saves the model).
    """
    fonts = _load_fonts()
    img = Image.new('RGB', (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    y = 0  # current vertical cursor

    # ── Header band ─────────────────────────────────────────────────────────
    draw.rectangle([0, 0, W, 130], fill=PRIMARY)
    _center_text(draw, 18, _ar('إيصال دفع اشتراك'), fonts['title'], WHITE)
    _center_text(draw, 70, _ar(receipt.generator.generator_name), fonts['xl'], (180, 210, 255))
    _center_text(draw, 105, _ar('نظام مولداتنا'), fonts['sm'], (150, 190, 245))
    y = 130

    # ── Receipt number strip ─────────────────────────────────────────────────
    draw.rectangle([0, y, W, y + 44], fill=PRIMARY_L)
    _center_text(
        draw, y + 10,
        _ar(f'رقم الإيصال:  #{receipt.id:05d}'),
        fonts['lg'], PRIMARY,
    )
    y += 44

    # ── Subscriber section ───────────────────────────────────────────────────
    pad = 36    # left/right padding
    lh  = 48    # row height

    def row(label: str, value: str, y_pos: int, highlight=False, value_color=TEXT_DARK):
        bg = GREY_L if not highlight else ACCENT_L
        draw.rectangle([pad - 8, y_pos, W - pad + 8, y_pos + lh - 4], fill=bg)
        _right_text(draw, W - pad, y_pos + 14, _ar(label), fonts['md'], TEXT_MID)
        _left_text(draw, pad, y_pos + 14, _ar(value), fonts['lg'], value_color)
        return y_pos + lh

    y += 14
    sub = receipt.subscriber
    y = row('المشترك:', sub.name, y)
    y = row('رقم الجوزة:', sub.circuit_number, y)
    y = row('رقم الهاتف:', sub.phone or '—', y)
    y = row('الأمبيرات:', f'{sub.ambers} أمبير', y)

    # ── Divider ──────────────────────────────────────────────────────────────
    y += 8
    draw.line([pad, y, W - pad, y], fill=DIVIDER, width=1)
    y += 14

    # ── Period / pricing ─────────────────────────────────────────────────────
    month_name = MONTHS_AR[receipt.month] if 1 <= receipt.month <= 12 else str(receipt.month)
    y = row('الشهر / السنة:', f'{month_name}  {receipt.year}', y)
    y = row('سعر الأمبير:', f'{float(receipt.amber_price):,.0f} د.ع', y)

    # ── Divider ──────────────────────────────────────────────────────────────
    y += 8
    draw.line([pad, y, W - pad, y], fill=DIVIDER, width=1)
    y += 14

    # ── Total paid — highlighted ─────────────────────────────────────────────
    draw.rectangle([0, y, W, y + lh + 8], fill=ACCENT)
    _right_text(draw, W - pad, y + 16, _ar('المبلغ المدفوع:'), fonts['lg'], WHITE)
    _left_text(draw, pad, y + 16, _ar(f'{float(receipt.amount_paid):,.0f} د.ع'), fonts['xl'], WHITE)
    y += lh + 8 + 14

    # ── Meta info ────────────────────────────────────────────────────────────
    if receipt.date_received:
        date_str = receipt.date_received.strftime('%Y/%m/%d   %H:%M')
    else:
        date_str = '—'
    y = row('تاريخ الدفع:', date_str, y)

    if receipt.worker:
        y = row('العامل:', receipt.worker.name, y)

    if receipt.notes:
        y = row('ملاحظات:', receipt.notes, y)

    # ── Footer ───────────────────────────────────────────────────────────────
    draw.rectangle([0, H - 72, W, H], fill=PRIMARY)
    _center_text(draw, H - 56, _ar('شكراً لاشتراككم — مولداتنا'), fonts['lg'], WHITE)
    _center_text(draw, H - 24, _ar(receipt.generator.generator_name), fonts['sm'], (180, 210, 255))

    # ── Save ─────────────────────────────────────────────────────────────────
    buf = BytesIO()
    img.save(buf, format='PNG', optimize=True)
    buf.seek(0)

    filename = (
        f"receipt_{receipt.generator_id}_{receipt.year}"
        f"_{receipt.month:02d}_{receipt.id}.png"
    )
    receipt.receipt_image.save(filename, ContentFile(buf.read()), save=True)
