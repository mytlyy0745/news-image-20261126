#!/usr/bin/env python3
"""Draw entry.png: one 1024x1024 image summing up Thursday 26 November 2026's
world news. Deterministic: fixed layout, fixed colours, fixed text; no random
input, no network, no clock. Running it twice produces byte-identical PNGs
(Pillow writes no timestamps into PNG chunks).

Layout (1024x1024):
  masthead 0-120, lead tariff panel 132-336, 2x3 story grid 348-916,
  "ALSO TODAY" footer 928-1000.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

# --- palette ---
NAVY = (13, 27, 46)        # page background
NAVY2 = (10, 20, 34)       # masthead band
CARD = (22, 48, 76)        # story card
LEAD = (18, 40, 64)        # lead panel
GOLD = (242, 183, 5)
RED = (228, 87, 46)
TEAL = (46, 196, 182)
WHITE = (245, 247, 250)
MUTED = (178, 196, 214)
LINE = (58, 96, 138)
CHIP = (242, 183, 5)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)

F_TITLE = font("DejaVuSans-Bold.ttf", 52)
F_DATE = font("DejaVuSans-Bold.ttf", 30)
F_KICKER = font("DejaVuSans-Bold.ttf", 20)
F_LEAD_H = font("DejaVuSans-Bold.ttf", 33)
F_LEAD_B = font("DejaVuSans.ttf", 21)
F_TAG = font("DejaVuSans-Bold.ttf", 18)
F_CARD_H = font("DejaVuSans-Bold.ttf", 23)
F_CARD_B = font("DejaVuSans.ttf", 19)
F_FOOT = font("DejaVuSans.ttf", 18)
F_FOOT_B = font("DejaVuSans-Bold.ttf", 18)
F_BIG = font("DejaVuSans-Bold.ttf", 30)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines. Raises if a word alone is too wide."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            if draw.textlength(word, font=fnt) > max_w:
                raise ValueError("word too wide for box: %r" % word)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, fnt, max_w, max_lines, fill, leading=None):
    """Draw wrapped text; returns bottom y. Raises on overflow."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) > max_lines:
        raise ValueError("text overflows box (%d > %d lines): %r"
                         % (len(lines), max_lines, text))
    lh = leading or int(fnt.size * 1.28)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def draw_bar_chart(draw, x, y, w, h, bars):
    """Simple horizontal bar chart: bars = [(label, value, colour)]."""
    max_v = max(v for _, v, _ in bars)
    row_h = h // len(bars)
    lab_f = font("DejaVuSans-Bold.ttf", 17)
    val_f = font("DejaVuSans-Bold.ttf", 17)
    for i, (label, value, colour) in enumerate(bars):
        ry = y + i * row_h
        draw.text((x, ry + 2), label, font=lab_f, fill=WHITE)
        bx = x + 132
        bw = int((w - 132 - 52) * value / max_v)
        draw.rectangle([bx, ry + 4, bx + bw, ry + row_h - 10], fill=colour)
        draw.text((bx + bw + 6, ry + 2), "%d%%" % value, font=val_f, fill=GOLD)


def glyph_oil(draw, x, y, s):
    """Oil barrel with a flame above it."""
    # flame
    fx, fy = x + s // 2, y + int(s * 0.08)
    draw.polygon([(fx, fy), (fx + int(s * 0.22), fy + int(s * 0.30)),
                  (fx + int(s * 0.10), fy + int(s * 0.26)),
                  (fx + int(s * 0.16), fy + int(s * 0.42)),
                  (fx - int(s * 0.16), fy + int(s * 0.42)),
                  (fx - int(s * 0.10), fy + int(s * 0.26)),
                  (fx - int(s * 0.22), fy + int(s * 0.30))], fill=RED)
    # barrel
    bx, by = x + int(s * 0.18), y + int(s * 0.48)
    bw, bh = int(s * 0.64), int(s * 0.46)
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=TEAL)
    draw.line([bx, by + bh // 3, bx + bw, by + bh // 3], fill=NAVY, width=3)
    draw.line([bx, by + 2 * bh // 3, bx + bw, by + 2 * bh // 3], fill=NAVY, width=3)


def glyph_chip(draw, x, y, s):
    """Microchip: square body, inner die, pins on four sides."""
    m = int(s * 0.22)
    draw.rectangle([x + m, y + m, x + s - m, y + s - m], fill=GOLD)
    im = int(s * 0.36)
    draw.rectangle([x + im, y + im, x + s - im, y + s - im], fill=NAVY2)
    for i in range(3):
        off = m + int((s - 2 * m) * (i + 1) / 4)
        draw.line([x + off, y + 4, x + off, y + m], fill=GOLD, width=4)
        draw.line([x + off, y + s - m, x + off, y + s - 4], fill=GOLD, width=4)
        draw.line([x + 4, y + off, x + m, y + off], fill=GOLD, width=4)
        draw.line([x + s - m, y + off, x + s - 4, y + off], fill=GOLD, width=4)


def glyph_cross(draw, x, y, s):
    """Memorial cross over a low mound."""
    cx = x + int(s * 0.30)
    draw.rectangle([cx - 6, y + int(s * 0.10), cx + 6, y + int(s * 0.78)],
                   fill=WHITE)
    draw.rectangle([cx - int(s * 0.20), y + int(s * 0.24),
                    cx + int(s * 0.20), y + int(s * 0.24) + 12], fill=WHITE)
    draw.ellipse([x + int(s * 0.05), y + int(s * 0.78),
                  x + int(s * 0.55), y + int(s * 0.94)], fill=MUTED)


def glyph_tanker(draw, x, y, s):
    """Fuel tanker truck with flames behind the tank."""
    # flames
    draw.polygon([(x + int(s * 0.55), y + int(s * 0.05)),
                  (x + int(s * 0.72), y + int(s * 0.35)),
                  (x + int(s * 0.62), y + int(s * 0.30)),
                  (x + int(s * 0.66), y + int(s * 0.48)),
                  (x + int(s * 0.48), y + int(s * 0.48)),
                  (x + int(s * 0.52), y + int(s * 0.30)),
                  (x + int(s * 0.42), y + int(s * 0.35))], fill=RED)
    # tank
    draw.rounded_rectangle([x + int(s * 0.06), y + int(s * 0.48),
                            x + int(s * 0.70), y + int(s * 0.74)],
                           radius=10, fill=TEAL)
    # cab
    draw.rectangle([x + int(s * 0.72), y + int(s * 0.54),
                    x + int(s * 0.92), y + int(s * 0.74)], fill=GOLD)
    # wheels
    for wx in (int(s * 0.20), int(s * 0.55), int(s * 0.82)):
        draw.ellipse([x + wx - 9, y + int(s * 0.74) - 4,
                      x + wx + 9, y + int(s * 0.74) + 14], fill=NAVY2,
                     outline=WHITE, width=2)


def glyph_shield(draw, x, y, s):
    """Police shield with a star."""
    cx, top = x + s // 2, y + int(s * 0.08)
    pts = [(cx, top),
           (cx + int(s * 0.32), top + int(s * 0.12)),
           (cx + int(s * 0.32), top + int(s * 0.48)),
           (cx, top + int(s * 0.86)),
           (cx - int(s * 0.32), top + int(s * 0.48)),
           (cx - int(s * 0.32), top + int(s * 0.12))]
    draw.polygon(pts, fill=TEAL)
    # five-point star, approximated with a small polygon
    sx, sy, r = cx, top + int(s * 0.38), int(s * 0.13)
    star = [(sx, sy - r), (sx + int(r * 0.29), sy - int(r * 0.40)),
            (sx + int(r * 0.95), sy - int(r * 0.31)),
            (sx + int(r * 0.47), sy + int(r * 0.15)),
            (sx + int(r * 0.59), sy + int(r * 0.81)),
            (sx, sy + int(r * 0.42)),
            (sx - int(r * 0.59), sy + int(r * 0.81)),
            (sx - int(r * 0.47), sy + int(r * 0.15)),
            (sx - int(r * 0.95), sy - int(r * 0.31)),
            (sx - int(r * 0.29), sy - int(r * 0.40))]
    draw.polygon(star, fill=WHITE)


def glyph_probe(draw, x, y, s):
    """Document under a magnifier, ringed by a red stamp circle."""
    # document
    draw.rectangle([x + int(s * 0.12), y + int(s * 0.16),
                    x + int(s * 0.62), y + int(s * 0.84)], fill=WHITE)
    for i in range(4):
        ly = y + int(s * 0.28) + i * int(s * 0.14)
        draw.line([x + int(s * 0.20), ly, x + int(s * 0.54), ly],
                  fill=NAVY, width=3)
    # magnifier
    mx, my, mr = x + int(s * 0.66), y + int(s * 0.30), int(s * 0.20)
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], outline=RED, width=6)
    draw.line([mx + int(mr * 0.7), my + int(mr * 0.7),
               mx + int(mr * 1.35), my + int(mr * 1.35)], fill=RED, width=6)
    # red stamp ring
    draw.ellipse([x + 4, y + 4, x + s - 4, y + s - 4], outline=RED, width=4)


def main():
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.rectangle([0, 0, W, 120], fill=NAVY2)
    d.text((24, 14), "THE WORLD IN ONE PICTURE", font=F_KICKER, fill=GOLD)
    d.text((24, 44), "THURSDAY 26 NOVEMBER 2026", font=F_TITLE, fill=WHITE)
    d.text((24, 98), "Seven stories that defined the day",
           font=font("DejaVuSans.ttf", 19), fill=MUTED)
    d.rectangle([0, 120, W, 124], fill=GOLD)

    # ---- lead: tariffs ----
    lx, ly, lw, lh = 24, 132, 976, 204
    d.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=10, fill=LEAD)
    d.rectangle([lx, ly + 8, lx + 6, ly + lh - 8], fill=GOLD)
    d.text((lx + 20, ly + 12), "LEAD  ·  TRADE", font=F_TAG, fill=GOLD)
    text_block(d, lx + 20, ly + 40, "TRUMP'S TARIFF SALVO",
               F_LEAD_H, 520, 1, WHITE)
    text_block(d, lx + 20, ly + 88,
               "US proposes 20-40% duties on 14 trading partners to fight "
               "\"excess capacity\". China faces +20%; the EU, Japan, South "
               "Korea and Taiwan are capped at 15%.",
               F_LEAD_B, 520, 4, MUTED)
    # right: bar chart of proposed caps
    cx = lx + 560
    d.text((cx, ly + 12), "PROPOSED CAPS", font=F_TAG, fill=MUTED)
    draw_bar_chart(d, cx, ly + 44, 396, 148, [
        ("China", 20, RED),
        ("Vietnam", 20, RED),
        ("Malaysia", 19, GOLD),
        ("India", 17, GOLD),
        ("EU/JP/KR/TW", 15, TEAL),
    ])

    # ---- story grid ----
    stories = [
        ("OIL", "HOUTHIS CLAIM RAS TANURA STRIKE",
         "Brent jumps 3.5% to $94.61 a barrel; Saudi Arabia says it shot "
         "down four drones over the refinery.", glyph_oil),
        ("TECH", "HUANG BACK AT NVIDIA \u2014 AFTER NO PROBE",
         "Trump pushed the CEO's return; the Justice Dept. never probed "
         "him. Congress is furious.",
         glyph_chip),
        ("WAR", "RUSSIA'S OWN DATA: ~500,000 DEAD",
         "Leaked Rosstat records show 490,334 soldiers killed; over "
         "720,000 including the missing.", glyph_cross),
        ("EGYPT", "31 KILLED IN CAIRO TANKER FIRE",
         "A fuel tanker overturned on the Ring Road in Giza; flames "
         "engulfed 27 vehicles.", glyph_tanker),
        ("COLOMBIA", "20 HOSTAGES FREED IN CARTAGENA",
         "Police storm an \u00c9xito supermarket after a 17-hour siege; "
         "one gunman killed.", glyph_shield),
        ("CHINA", "XI'S PURGE HITS SHANGHAI CHIEF",
         "Politburo member Chen Jining probed for graft \u2014 the fourth "
         "top leader investigated in a year.", glyph_probe),
    ]
    gx, gy = 24, 348
    cw, ch, gap = 482, 182, 12
    for i, (tag, head, body, glyph) in enumerate(stories):
        x = gx + (i % 2) * (cw + gap)
        y = gy + (i // 2) * (ch + gap)
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=10, fill=CARD)
        # number chip
        d.ellipse([x + 14, y + 14, x + 44, y + 44], fill=CHIP)
        num = str(i + 2)
        tw = d.textlength(num, font=F_TAG)
        d.text((x + 29 - tw / 2, y + 18), num, font=F_TAG, fill=NAVY2)
        d.text((x + 54, y + 18), tag, font=F_TAG, fill=GOLD)
        # glyph panel
        g = 96
        glyph(d, x + 14, y + 62, g)
        tx = x + 122
        text_block(d, tx, y + 58, head, F_CARD_H, cw - 136, 2, WHITE)
        text_block(d, tx, y + 112, body, F_CARD_B, cw - 136, 3, MUTED)

    # ---- footer: also today ----
    fy = 928
    d.rectangle([0, fy, W, H], fill=NAVY2)
    d.rectangle([0, fy, W, fy + 3], fill=GOLD)
    text_block(d, 24, fy + 14, "ALSO TODAY:  Hera probe's first close-ups "
               "of the Dimorphos asteroid due  \u00b7  Kenya discharges its "
               "last Ebola patient as the DRC toll passes 5,300  \u00b7  "
               "Taiwan stocks plunge 1,927 points  \u00b7  Fed: modest "
               "growth, price pressure persists",
               F_FOOT, 976, 3, MUTED)

    img.save(OUT, format="PNG", optimize=True)
    print("wrote %s (%d bytes)" % (OUT, os.path.getsize(OUT)))


if __name__ == "__main__":
    main()
