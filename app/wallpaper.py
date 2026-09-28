"""Render a desktop wallpaper with month calendar + today's todos."""

from __future__ import annotations

import calendar
import subprocess
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.db import DATA_DIR

WALLPAPER_PATH = DATA_DIR / "dayboard-wallpaper.png"
W, H = 2560, 1600
BG = (12, 16, 24)
CARD = (22, 28, 40)
ACCENT = (59, 130, 246)
TEXT = (236, 242, 254)
MUTED = (148, 163, 184)
TODAY_BG = (29, 78, 216)


def _font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def render(todos, events, out=None):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out = out or WALLPAPER_PATH
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    title_f = _font(54, True)
    head_f = _font(28, True)
    body_f = _font(22)
    small_f = _font(18)
    today = date.today()
    draw.text((80, 70), today.strftime("%A"), font=head_f, fill=MUTED)
    draw.text((80, 110), today.strftime("%B %d, %Y"), font=title_f, fill=TEXT)
    _calendar_card(draw, today, 80, 230, 980, 980, head_f, body_f, small_f)
    _list_card(draw, "TODAY TO DO", todos or ["No open tasks"], 1140, 230, 1340, 560, head_f, body_f)
    _list_card(draw, "TODAY SCHEDULE", events or ["Nothing on the calendar"], 1140, 830, 1340, 560, head_f, body_f)
    draw.text((80, H - 80), "Dayboard  ·  local widgets", font=small_f, fill=MUTED)
    img.save(out, "PNG")
    return out


def _rounded(draw, box, fill):
    draw.rounded_rectangle(box, radius=28, fill=fill)


def _calendar_card(draw, today, x, y, w, h, head_f, body_f, small_f):
    _rounded(draw, (x, y, x + w, y + h), CARD)
    draw.text((x + 40, y + 28), today.strftime("%B %Y"), font=head_f, fill=TEXT)
    names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cell_w, cell_h = 120, 110
    ox, oy = x + 50, y + 110
    for i, name in enumerate(names):
        draw.text((ox + i * cell_w + 28, oy), name, font=small_f, fill=MUTED)
    cal = calendar.Calendar(firstweekday=0)
    weeks = cal.monthdatescalendar(today.year, today.month)
    for r, week in enumerate(weeks):
        for c, d in enumerate(week):
            cx = ox + c * cell_w
            cy = oy + 40 + r * cell_h
            if d == today:
                draw.rounded_rectangle((cx + 8, cy + 8, cx + 100, cy + 92), radius=16, fill=TODAY_BG)
                fill = TEXT
            elif d.month != today.month:
                fill = (71, 85, 105)
            else:
                fill = TEXT
            draw.text((cx + 40, cy + 32), str(d.day), font=body_f, fill=fill)


def _list_card(draw, title, items, x, y, w, h, head_f, body_f):
    _rounded(draw, (x, y, x + w, y + h), CARD)
    draw.rectangle((x, y, x + 10, y + h), fill=ACCENT)
    draw.text((x + 36, y + 28), title, font=head_f, fill=TEXT)
    yy = y + 90
    for item in items[:8]:
        text = item if len(item) < 52 else item[:49] + "..."
        draw.ellipse((x + 36, yy + 8, x + 48, yy + 20), fill=ACCENT)
        draw.text((x + 64, yy), text, font=body_f, fill=TEXT)
        yy += 48


def set_macos_wallpaper(path):
    if sys.platform != "darwin":
        return f"Wallpaper saved to {path}. Set it manually on this OS."
    script = f'tell application "System Events" to tell every desktop to set picture to POSIX file "{path}"'
    subprocess.run(["osascript", "-e", script], check=False)
    return f"Wallpaper set: {path}"
