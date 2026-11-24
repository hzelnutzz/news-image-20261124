#!/usr/bin/env python3
"""Draw the make.fun news-image entry: a 1024x1024 broadsheet front page.

Fully deterministic: fixed layout, fixed fonts, no randomness, no clock reads.
Output: entry.png (RGB, 1024x1024) in the repository root.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 44
CONTENT_W = W - 2 * M

PAPER = (250, 247, 239)
INK = (27, 25, 23)
GREY = (90, 86, 79)
LIGHT = (168, 162, 151)
HAIR = (196, 190, 178)
RED = (155, 29, 37)
TINT = (242, 237, 226)

SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

_fonts = {}


def F(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def tracked_w(draw, text, fnt, tracking):
    if not text:
        return 0
    return sum(text_w(draw, ch, fnt) for ch in text) + tracking * (len(text) - 1)


def draw_tracked(draw, x, y, text, fnt, fill, tracking):
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=fnt, fill=fill)
        cx += text_w(draw, ch, fnt) + tracking


def draw_tracked_center(draw, y, text, fnt, fill, tracking):
    x = (W - tracked_w(draw, text, fnt, tracking)) / 2
    draw_tracked(draw, x, y, text, fnt, fill, tracking)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_headline(draw, text, path, max_w, max_lines, hi, lo):
    """Largest size whose wrapped headline fits the width in max_lines."""
    size = lo
    for candidate in range(hi, lo - 1, -2):
        fnt = F(path, candidate)
        lines = wrap(draw, text, fnt, max_w)
        if len(lines) <= max_lines and all(text_w(draw, ln, fnt) <= max_w for ln in lines):
            size = candidate
            break
    else:
        fnt = F(path, size)
        lines = wrap(draw, text, fnt, max_w)
        while len(lines) > max_lines and size > 8:
            size -= 2
            fnt = F(path, size)
            lines = wrap(draw, text, fnt, max_w)
    return fnt, lines, size


def rule(draw, x0, y, x1, fill=HAIR, width=1):
    draw.rectangle([x0, y, x1, y + width - 1], fill=fill)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Page frame ------------------------------------------------------------
    d.rectangle([19, 19, W - 20, H - 20], outline=HAIR, width=1)

    # Masthead --------------------------------------------------------------
    kicker_f = F(SANS_BOLD, 13)
    draw_tracked_center(d, 38, "THE GLOBAL EDITION  ·  SIX REGIONS, ONE PAGE", kicker_f, RED, 2.4)

    mast_f, mast_lines, mast_size = fit_headline(
        d, "WORLD NEWS IN ONE IMAGE", SERIF_BOLD, CONTENT_W - 20, 1, 62, 40
    )
    mast_y = 60
    for line in mast_lines:
        d.text(((W - text_w(d, line, mast_f)) / 2, mast_y), line, font=mast_f, fill=INK)

    rule(d, M, 138, W - M, INK, 2)

    # Dateline strip --------------------------------------------------------
    d.rectangle([M, 145, W - M, 184], fill=TINT)
    date_f = F(SANS_BOLD, 25)
    d.text((M + 10, 152), "TUESDAY 24 NOVEMBER 2026", font=date_f, fill=INK)

    meta_f = F(SANS, 12)
    meta = "VOL. 1  ·  NO. 328  ·  EVENING FINAL"
    meta_x = W - M - 10 - tracked_w(d, meta, meta_f, 1.0)
    draw_tracked(d, meta_x, 160, meta, meta_f, GREY, 1.0)

    rule(d, M, 184, W - M, INK, 3)
    rule(d, M, 189, W - M, HAIR, 1)

    # Lead story ------------------------------------------------------------
    y = 206
    lab_f = F(SANS_BOLD, 12)
    draw_tracked(d, M + 1, y, "LEAD STORY  ·  STRAIT OF HORMUZ", lab_f, RED, 1.8)
    y = 228

    lead_f, lead_lines, lead_size = fit_headline(
        d, "THREE TANKERS ABLAZE AS IRAN SHUTS THE STRAIT OF HORMUZ",
        SERIF_BOLD, CONTENT_W, 3, 54, 38
    )
    lead_lh = int(lead_size * 1.06)
    for line in lead_lines:
        d.text(((W - text_w(d, line, lead_f)) / 2, y), line, font=lead_f, fill=INK)
        y += lead_lh

    y += 4
    deck_f = F(SERIF_IT, 18)
    deck_text = (
        "Mines hit three escorted tankers in the Gulf; Iran's army chief orders the "
        "waterway closed until Tehran's terms are met. Brent crude near $99."
    )
    deck_cols_w = 624
    for line in wrap(d, deck_text, deck_f, deck_cols_w - 8):
        d.text(((W - text_w(d, line, deck_f)) / 2, y), line, font=deck_f, fill=GREY)
        y += 23
    y += 8

    # Lead body: two columns, plus a fact box at right.
    body_f = F(SERIF, 14)
    body_lh = 18
    col_w = 292
    col_x = [M, M + col_w + 26]
    body_cols = [
        "Three oil tankers struck naval mines and caught fire in the Strait of "
        "Hormuz despite a US escort, Iran's Revolutionary Guard Navy said on "
        "Tuesday, in an attack on shipping inside the world's busiest oil chokepoint.",
        "Iran's army chief ordered the strait to stay closed until Iran's "
        "conditions are met, leaving the Gulf waterway shut to commercial traffic "
        "and exposing global energy supplies to a prolonged interruption.",
    ]
    body_top = y
    for cx, text in zip(col_x, body_cols):
        ly = body_top
        for line in wrap(d, text, body_f, col_w):
            d.text((cx, ly), line, font=body_f, fill=INK)
            ly += body_lh
    body_bottom = max(
        body_top + len(wrap(d, t, body_f, col_w)) * body_lh for t in body_cols
    )

    # Fact box
    box_x0, box_x1 = 700, W - M
    box_y0, box_y1 = body_top - 6, body_bottom + 2
    d.rectangle([box_x0, box_y0, box_x1, box_y1], fill=TINT)
    d.rectangle([box_x0, box_y0, box_x1, box_y1], outline=LIGHT, width=1)
    d.rectangle([box_x0, box_y0, box_x0 + 4, box_y1], fill=RED)
    bh_f = F(SANS_BOLD, 10)
    draw_tracked(d, box_x0 + 16, box_y0 + 10, "AT A GLANCE", bh_f, RED, 1.6)
    items = [
        ("3", "tankers mined and ablaze in the strait"),
        ("SHUT", "until Iran's conditions are met"),
        ("$99", "Brent crude, trading near"),
    ]
    num_f = F(SERIF_BOLD, 17)
    label_w = max(text_w(d, num, num_f) for num, _ in items)
    tx = box_x0 + 16 + label_w + 10
    t_f = F(SANS, 11)
    iy = box_y0 + 28
    for num, txt in items:
        d.text((box_x0 + 16, iy - 2), num, font=num_f, fill=INK)
        for line in wrap(d, txt, t_f, box_x1 - 12 - tx):
            d.text((tx, iy), line, font=t_f, fill=INK)
            iy += 13
        iy += 9

    # Close the lead block
    lead_bottom = max(body_bottom, iy) + 12
    rule(d, M, lead_bottom, W - M, INK, 3)

    # Secondary stories -----------------------------------------------------
    stories = [
        ("RUSSIA–UKRAINE",
         "RUSSIA AND UKRAINE CLASH AT UN OVER BLACK SEA ATTACKS",
         "Zelenskyy presses allies for more air-defence missiles as the EU rolls out a new sanctions package."),
        ("MIDDLE EAST",
         "GAZA POLICE POST STRIKE KILLS THREE",
         "Israeli drone strike hits Khan Younis; rain floods 70,000 tents as senators urge winter supplies. Vance and Rubio meet Qatar's PM on Iran talks."),
        ("ASIA",
         "PAKISTANI ASTRONAUT JOINS SHENZHOU-24",
         "Muhammad Zeeshan Ali becomes the first foreign astronaut on the Tiangong station; launch set for Nov 25."),
        ("AMERICAS",
         "CAR BOMB ROCKS COLOMBIAN CITY",
         "Blast near Meta government headquarters in Villavicencio injures dozens, with no deaths. Trump says China may buy 250 more Boeing jets."),
        ("TECH / BUSINESS",
         "NVIDIA REINSTATES JENSEN HUANG AS CEO",
         "Gold holds above $4,600; FIFA awards the 2031 Women's World Cup to the US, Mexico, Costa Rica and Jamaica, and 2035 to the UK."),
        ("EUROPE",
         "SPAIN SETS SNAP ELECTION FOR NOV 29",
         "Sanchez proposes a tax on fortunes above €100m as voters head to the polls."),
    ]

    sec_top = lead_bottom + 16
    sec_bottom = 962
    col_gap = 36
    s_col_w = (CONTENT_W - col_gap) // 2
    s_x = [M, M + s_col_w + col_gap]

    d.rectangle([M + s_col_w + col_gap // 2 - 1, sec_top, M + s_col_w + col_gap // 2, sec_bottom], fill=HAIR)

    rows = 3
    row_h = (sec_bottom - sec_top) // rows
    s_lab_f = F(SANS_BOLD, 11)
    s_head_f = F(SERIF_BOLD, 18)
    s_deck_f = F(SERIF, 14)
    s_head_lh = 22
    s_deck_lh = 17

    for idx, (label, headline, deck) in enumerate(stories):
        col = idx % 2
        row = idx // 2
        x = s_x[col]
        y = sec_top + row * row_h

        draw_tracked(d, x, y, label, s_lab_f, RED, 1.5)
        y += 18

        lines = wrap(d, headline, s_head_f, s_col_w)
        if len(lines) > 2:
            hf, lines, _ = fit_headline(d, headline, SERIF_BOLD, s_col_w, 2, 18, 13)
        else:
            hf = s_head_f
        for line in lines:
            d.text((x, y), line, font=hf, fill=INK)
            y += s_head_lh
        y += 5

        df = s_deck_f
        dlines = wrap(d, deck, df, s_col_w)
        if len(dlines) > 3:
            df = F(SERIF, 13)
            dlines = wrap(d, deck, df, s_col_w)
        for line in dlines:
            d.text((x, y), line, font=df, fill=GREY)
            y += s_deck_lh

        if row > 0:
            rule(d, x, sec_top + row * row_h - 10, x + s_col_w, HAIR, 1)

    # Footer ----------------------------------------------------------------
    rule(d, M, 972, W - M, INK, 2)
    foot_f = F(SANS_BOLD, 9)
    draw_tracked_center(d, 980, "WORLD NEWS IN ONE IMAGE  ·  TUESDAY 24 NOVEMBER 2026  ·  PAGE 1",
                        foot_f, GREY, 1.6)

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, img.mode, img.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
