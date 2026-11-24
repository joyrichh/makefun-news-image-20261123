#!/usr/bin/env python3
"""Render the 23 November 2026 world-news image (1024x1024 PNG).

Fresh, deterministic renderer for the make.fun news-image-20261123 entry.
Reads news.json next to this file, draws a newspaper-style infographic with
Pillow and system DejaVu fonts. No network, no timestamps, no randomness:
running it twice produces byte-identical output.

Layout (1024x1024):
  header band (0..120)      date + title
  2x3 story panels (132..856) tag chip, pictogram, headline, summary, source
  "Also today" strip (868..956)
  footer (964..1024)        source credits
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
W = H = 1024

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

PAPER = (247, 243, 234)
PANEL = (255, 255, 255)
INK = (20, 28, 43)
NAVY = (20, 33, 61)
NAVY_LIGHT = (31, 46, 80)
MUTED = (96, 103, 116)
FAINT = (214, 210, 198)
ACCENT = (244, 162, 89)
SUBTITLE = (201, 209, 217)

TAG_COLORS = {
    "TECH": (37, 99, 235),
    "WAR": (185, 28, 28),
    "CLIMATE": (21, 128, 61),
    "ASIA": (194, 65, 12),
    "TRADE": (124, 58, 237),
    "DIPLOMACY": (14, 116, 144),
}


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, fnt, max_w, max_lines):
    """Greedy word wrap by pixel width; fails loudly on overflow."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        raise ValueError(f"text overflows {max_lines} lines: {text!r} -> {lines}")
    return lines


def draw_lines(d, lines, x, y, fnt, fill, leading):
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- pictograms
# Each draws a small flat icon centred on (cx, cy) inside a ~64px box.

def pic_chip(d, cx, cy, color):
    # computer chip: dark body, pins, green up-arrow
    d.rounded_rectangle([cx - 20, cy - 20, cx + 20, cy + 20], radius=5,
                        fill=(17, 24, 39))
    d.rectangle([cx - 11, cy - 11, cx + 11, cy + 11], outline=(118, 185, 0), width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(118, 185, 0))
    for i in (-1, 0, 1):
        off = i * 11
        d.rectangle([cx + off - 2, cy - 27, cx + off + 2, cy - 20], fill=(17, 24, 39))
        d.rectangle([cx + off - 2, cy + 20, cx + off + 2, cy + 27], fill=(17, 24, 39))
        d.rectangle([cx - 27, cy + off - 2, cx - 20, cy + off + 2], fill=(17, 24, 39))
        d.rectangle([cx + 20, cy + off - 2, cx + 27, cy + off + 2], fill=(17, 24, 39))
    d.line([(cx + 26, cy + 18), (cx + 32, cy + 8), (cx + 37, cy + 13), (cx + 42, cy - 2)],
           fill=(22, 163, 74), width=3)
    d.polygon([(cx + 42, cy - 2), (cx + 35, cy - 2), (cx + 42, cy + 5)], fill=(22, 163, 74))


def pic_warship(d, cx, cy, color):
    # hull + mast + explosion + waves
    d.polygon([(cx - 28, cy + 2), (cx + 28, cy + 2), (cx + 20, cy + 14), (cx - 20, cy + 14)],
              fill=(51, 65, 85))
    d.rectangle([cx - 8, cy - 10, cx + 6, cy + 2], fill=(71, 85, 105))
    d.line([(cx + 2, cy - 10), (cx + 2, cy - 24)], fill=(51, 65, 85), width=3)
    # explosion burst
    bx, by = cx - 2, cy - 30
    for ang in range(0, 360, 45):
        import math
        r2 = 10
        a = math.radians(ang)
        d.line([(bx, by), (bx + r2 * math.cos(a), by + r2 * math.sin(a))],
               fill=(234, 88, 12), width=3)
    d.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=(250, 204, 21))
    # waves
    for k, wy in enumerate((cy + 20, cy + 26)):
        d.arc([cx - 30 + k * 6, wy - 5, cx - 6 + k * 6, wy + 5], 0, 180,
              fill=(37, 99, 235), width=3)
        d.arc([cx + 2 + k * 6, wy - 5, cx + 26 + k * 6, wy + 5], 0, 180,
              fill=(37, 99, 235), width=3)


def pic_globe(d, cx, cy, color):
    # globe + sun
    d.ellipse([cx - 24, cy - 22, cx + 24, cy + 26], fill=(59, 130, 246),
              outline=(30, 64, 175), width=2)
    d.ellipse([cx - 18, cy - 12, cx - 2, cy + 2], fill=(34, 197, 94))
    d.ellipse([cx + 2, cy + 4, cx + 16, cy + 18], fill=(34, 197, 94))
    d.arc([cx - 24, cy - 22, cx + 24, cy + 26], 200, 340, fill=(255, 255, 255), width=2)
    # sun top-right
    sx, sy = cx + 26, cy - 26
    d.ellipse([sx - 7, sy - 7, sx + 7, sy + 7], fill=(249, 115, 22))
    for ang in range(0, 360, 45):
        import math
        a = math.radians(ang)
        d.line([(sx + 10 * math.cos(a), sy + 10 * math.sin(a)),
                (sx + 15 * math.cos(a), sy + 15 * math.sin(a))],
               fill=(249, 115, 22), width=2)


def pic_fire(d, cx, cy, color):
    # factory + flame
    d.rectangle([cx - 26, cy - 2, cx + 26, cy + 24], fill=(100, 116, 139))
    d.polygon([(cx - 26, cy - 2), (cx - 13, cy - 12), (cx, cy - 2), (cx + 13, cy - 12),
               (cx + 26, cy - 2)], fill=(71, 85, 105))
    d.rectangle([cx + 16, cy - 22, cx + 24, cy - 2], fill=(71, 85, 105))
    for wx in (-18, -4, 10):
        d.rectangle([cx + wx, cy + 8, cx + wx + 8, cy + 16], fill=(226, 232, 240))
    # flame above the roof
    fx, fy = cx - 2, cy - 14
    d.polygon([(fx - 12, fy + 8), (fx - 8, fy - 8), (fx - 2, fy - 16), (fx + 4, fy - 6),
               (fx + 10, fy - 12), (fx + 12, fy + 8)], fill=(234, 88, 12))
    d.polygon([(fx - 6, fy + 8), (fx - 3, fy - 4), (fx + 1, fy - 10), (fx + 5, fy - 2),
               (fx + 7, fy + 8)], fill=(250, 204, 21))


def pic_ban_chip(d, cx, cy, color):
    # chip with a red ban circle over it
    d.rounded_rectangle([cx - 18, cy - 18, cx + 18, cy + 18], radius=4,
                        fill=(17, 24, 39))
    d.rectangle([cx - 10, cy - 10, cx + 10, cy + 10], outline=(148, 163, 184), width=2)
    for i in (-1, 0, 1):
        off = i * 10
        d.rectangle([cx + off - 2, cy - 24, cx + off + 2, cy - 18], fill=(17, 24, 39))
        d.rectangle([cx + off - 2, cy + 18, cx + off + 2, cy + 24], fill=(17, 24, 39))
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], outline=(220, 38, 38), width=5)
    d.line([(cx - 18, cy + 18), (cx + 18, cy - 18)], fill=(220, 38, 38), width=5)


def pic_eu_bank(d, cx, cy, color):
    # bank building in EU blue, gold stars above
    d.polygon([(cx - 24, cy - 2), (cx, cy - 14), (cx + 24, cy - 2)], fill=(30, 58, 138))
    for i, off in enumerate((-16, 0, 16)):
        d.rectangle([cx + off - 3, cy + 2, cx + off + 3, cy + 18], fill=(30, 58, 138))
    d.rectangle([cx - 26, cy + 18, cx + 26, cy + 22], fill=(30, 58, 138))
    for k, sx in enumerate((-20, -10, 0, 10, 20)):
        d.ellipse([cx + sx - 2, cy - 26, cx + sx + 2, cy - 22], fill=(250, 204, 21))


PICTOGRAMS = {
    "nvidia-huang": pic_chip,
    "libya-warship": pic_warship,
    "cop31": pic_globe,
    "indonesia-fire": pic_fire,
    "megaspeed": pic_ban_chip,
    "eu-sanctions": pic_eu_bank,
}


# ------------------------------------------------------------------- drawing

def draw_panel(d, story, x0, y0, pw, ph):
    tag = story["tag"]
    color = TAG_COLORS[tag]
    d.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], radius=12,
                        fill=PANEL, outline=color, width=2)
    # tag chip
    f_tag = font(FONT_BOLD, 16)
    tw = f_tag.getlength(tag)
    chip_w = int(tw) + 22
    d.rounded_rectangle([x0 + 14, y0 + 12, x0 + 14 + chip_w, y0 + 38], radius=13, fill=color)
    d.text((x0 + 25, y0 + 16), tag, font=f_tag, fill=(255, 255, 255))
    # pictogram, top-right (dedicated zone; text wraps clear of it)
    pic = PICTOGRAMS[story["id"]]
    pic(d, x0 + pw - 62, y0 + 58, color)
    # headline (up to 2 lines, kept clear of the pictogram zone)
    text_w = pw - 32 - 104
    f_head = font(FONT_BOLD, 25)
    lines = wrap(story["headline"], f_head, text_w, 2)
    y = draw_lines(d, lines, x0 + 16, y0 + 52, f_head, INK, 31)
    # summary (up to 3 lines)
    f_sum = font(FONT_REG, 18)
    slines = wrap(story["summary"], f_sum, text_w, 3)
    draw_lines(d, slines, x0 + 16, y + 8, f_sum, (55, 65, 81), 23)
    # source line at the bottom
    d.line([(x0 + 16, y0 + ph - 30), (x0 + pw - 16, y0 + ph - 30)], fill=FAINT, width=1)
    d.text((x0 + 16, y0 + ph - 24), "Source: " + story["source"],
           font=font(FONT_REG, 13), fill=MUTED)


def render(news, out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- header band
    d.rectangle([0, 0, W, 120], fill=NAVY)
    d.text((24, 14), "THE WORLD IN ONE IMAGE", font=font(FONT_BOLD, 15), fill=ACCENT)
    d.text((24, 36), "MONDAY 23 NOVEMBER 2026", font=font(FONT_BOLD, 46), fill=(255, 255, 255))
    d.text((24, 92), "Six stories that defined the day — from Nvidia's boardroom to a warship off Libya",
           font=font(FONT_REG, 18), fill=SUBTITLE)

    # ---- story grid: 2 cols x 3 rows
    stories = news["stories"]
    pw, ph = 490, 232
    gx, gy, gap = 16, 132, 12
    for i, story in enumerate(stories):
        col, row = i % 2, i // 2
        x0 = gx + col * (pw + gap)
        y0 = gy + row * (ph + gap)
        draw_panel(d, story, x0, y0, pw, ph)

    # ---- "Also today" strip
    sy0, sy1 = 868, 956
    d.rounded_rectangle([16, sy0, W - 16, sy1], radius=12, fill=PANEL,
                        outline=NAVY, width=2)
    f_chip = font(FONT_BOLD, 15)
    d.rounded_rectangle([30, sy0 + 12, 30 + 118, sy0 + 36], radius=12, fill=NAVY)
    d.text((41, sy0 + 15), "ALSO TODAY", font=f_chip, fill=(255, 255, 255))
    f_item = font(FONT_REG, 15)
    # items start right of the chip (ends x=148); content ends at panel edge - 16
    col_w = (992 - 170 - 2 * 16) // 3
    for i, item in enumerate(news["also_today"]):
        lines = wrap(item["headline"], f_item, col_w, 2)
        draw_lines(d, lines, 170 + i * (col_w + 16), sy0 + 44, f_item, INK, 19)

    # ---- footer
    f_foot = font(FONT_REG, 13)
    line1 = "Sources: Reuters · CNN · AP · Al Jazeera · US Treasury (OFAC) · UN News"
    line2 = "All six stories verified 24 November 2026 · Drawn with code, no photographs · make.fun — news-image-20261123"
    for j, line in enumerate((line1, line2)):
        lw = f_foot.getlength(line)
        d.text(((W - lw) / 2, 968 + j * 20), line, font=f_foot, fill=MUTED)

    img.save(out_path, format="PNG")
    return out_path


def main():
    data = json.loads((HERE / "news.json").read_text(encoding="utf-8"))
    out = HERE / "entry.png"
    if len(sys.argv) > 1:
        out = Path(sys.argv[1])
    render(data, out)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
