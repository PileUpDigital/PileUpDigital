"""Render the PileUp Digital mark as a self-typing ASCII SVG.

The mark is light line art on a near-black square, so the density ramp runs the
opposite way to a normal photo pipeline: bright pixels are the logo and get the
dense glyphs, dark pixels are background and get a space.

Set STATIC=1 to emit a frozen frame for local preview.
"""

import os
import sys

from PIL import Image

COLS = 68
ROWS = 32
CELL_W = 8.0
CELL_H = 14.0
PAD = 20
FONT_SIZE = 13

# background -> ink
RAMP = " .:-=+*#%@"

INK = "#e6edf3"
DIM = "#7d8590"
ACCENT = "#39d353"
BG = "#0d1117"

ROW_DELAY = 0.06
ROW_DUR = 0.34


# anything at or below this stays blank, anything at or above is full ink
BLACK_POINT = 0.22
WHITE_POINT = 0.75


def load_rows(path):
    im = Image.open(path).convert("L")

    # crop to the mark itself so it fills the canvas instead of floating in padding
    bbox = im.point(lambda v: 255 if v > 90 else 0).getbbox()
    if bbox:
        m = int(max(im.size) * 0.02)
        im = im.crop(
            (
                max(bbox[0] - m, 0),
                max(bbox[1] - m, 0),
                min(bbox[2] + m, im.width),
                min(bbox[3] + m, im.height),
            )
        )

    im = im.resize((COLS, ROWS), Image.LANCZOS)
    px = im.load()
    span = WHITE_POINT - BLACK_POINT
    rows = []
    for y in range(ROWS):
        line = []
        for x in range(COLS):
            v = (px[x, y] / 255.0 - BLACK_POINT) / span
            v = 0.0 if v < 0 else (1.0 if v > 1 else v)
            line.append(RAMP[int(v * (len(RAMP) - 1) + 0.5)])
        rows.append("".join(line).rstrip())
    return rows


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(rows, static=False):
    w = int(COLS * CELL_W + PAD * 2)
    h = int(ROWS * CELL_H + PAD * 2 + 30)
    o = []
    o.append(
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">'
    )
    o.append(f'<rect width="{w}" height="{h}" rx="10" fill="{BG}"/>')

    o.append("<style><![CDATA[")
    if static:
        o.append(".row{opacity:1}")
    else:
        o.append(".row{opacity:0}")
        o.append(
            "@keyframes wipe{"
            "from{opacity:1;clip-path:inset(0 100% 0 0)}"
            "to{opacity:1;clip-path:inset(0 0 0 0)}}"
        )
        for i in range(len(rows)):
            o.append(
                f".w{i}{{animation:wipe {ROW_DUR}s "
                f"steps({COLS},end) {round(i * ROW_DELAY, 3)}s forwards}}"
            )
    o.append("@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}")
    o.append(".cur{animation:blink 1.05s step-end infinite}")
    o.append("]]></style>")

    y0 = PAD + FONT_SIZE
    for i, line in enumerate(rows):
        cls = "row" if static else f"row w{i}"
        o.append(
            f'<text class="{cls}" x="{PAD}" y="{y0 + i * CELL_H:.1f}" fill="{INK}" '
            f'font-size="{FONT_SIZE}" letter-spacing="{CELL_W - 7.82:.2f}" '
            f'xml:space="preserve">{esc(line)}</text>'
        )

    o.append(
        f'<text x="{PAD}" y="{h - PAD + 4}" font-size="12">'
        f'<tspan fill="{ACCENT}">pileup</tspan>'
        f'<tspan fill="{DIM}">@github ~ $</tspan> '
        f'<tspan fill="{INK}">whoami</tspan>'
        f'<tspan class="cur" fill="{ACCENT}"> _</tspan></text>'
    )
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "assets/mark.png"
    svg = build(load_rows(src), static=bool(os.environ.get("STATIC")))
    with open("logo-ascii.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote logo-ascii.svg  {COLS}x{ROWS}  {len(svg)} bytes")
