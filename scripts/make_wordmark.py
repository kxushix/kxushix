#!/usr/bin/env python3
"""Draw a word — the GitHub handle — as ascii.svg, in place of the portrait.

Same ramp, same grid, same self-typing SMIL wipe as scripts/make_portrait.py;
only the source pixels differ. The word is set in JetBrains Mono ExtraBold,
rasterised large, then downscaled onto the character grid, so the letterforms
land as shading rather than as blocky stamps.

    python3 scripts/make_wordmark.py kxu/shix
    python3 scripts/embed_portrait_font.py      # inline the font, as always

Split the word with "/" to stack it over several lines. Stacking is what makes
it read as a graphic rather than a caption: the height comes back, so the
letters are drawn with enough cells to shade their curves, and the row-by-row
wipe has something to build. --cols sets the grid width and the height follows
from the block's aspect.
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

from make_portrait import build_svg, to_lines

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "fonts", "jbmono-600.woff2")
RASTER = 120                # px per em before the downscale — plenty of detail
TRACKING = -0.04            # em, tightens the default monospace advance a touch
LEADING = 0.95              # em between stacked lines — tight, so the block reads as one


def render(word, font_path=FONT):
    """Rasterise the word — "/" starts a new line — black on white, cropped."""
    rows = word.split("/")
    font = ImageFont.truetype(font_path, RASTER)
    adv = font.getlength("M") + TRACKING * RASTER
    pad = RASTER
    img = Image.new("L", (int(adv * max(map(len, rows)) + pad * 2),
                          int(RASTER * (LEADING * len(rows) + 2))), 255)
    draw = ImageDraw.Draw(img)
    for r, row in enumerate(rows):
        for i, ch in enumerate(row):
            draw.text((pad + i * adv, RASTER * (1 + LEADING * r)), ch,
                      font=font, fill=0, anchor="ls")

    box = Image.eval(img, lambda v: 255 - v).getbbox()
    if not box:
        raise SystemExit(f"{font_path}: none of {word!r} is in this font subset")
    return img.crop(box)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("word", help='"/" splits the word onto a new line')
    ap.add_argument("out", nargs="?", default="ascii.svg")
    ap.add_argument("--cols", type=int, default=90)
    ap.add_argument("--font", default=FONT)
    ap.add_argument("--preview", action="store_true")
    args = ap.parse_args()

    lines = to_lines(render(args.word, args.font), cols=args.cols)
    if args.preview:
        print("\n".join(lines))
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(build_svg(lines, cols=args.cols))
    print(f"wrote {args.out} — {len(lines)} rows, {args.cols} columns")
    print("next: python3 scripts/embed_portrait_font.py")


if __name__ == "__main__":
    main()
