"""Render a neofetch-style card of what PileUp Digital has actually shipped.

Only the live numbers come from the GitHub API (public repo count, stars, the
Java line count across the plugin repos). Everything else is authored here,
because the things worth saying about shipped software are not in an API.

Set STATIC=1 to emit a frozen frame for local preview.
"""

import json
import os
import urllib.request

USER = "PileUpDigital"
PLUGINS = [
    "LegendaryWeapons",
    "TemporalGear",
    "TagsPlugin",
    "WeeklyChallenges",
    "PlayerMarket",
    "MinesPlugin",
]

W, H = 560, 470
PAD = 22
LINE = 21
FONT = 13

BG = "#0d1117"
INK = "#e6edf3"
DIM = "#7d8590"
KEY = "#39d353"
ALT = "#58a6ff"
WARN = "#d29922"

STEP = 0.09
DUR = 0.34


def api(path):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "pileup-profile"},
    )
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def stats():
    try:
        repos = api(f"/users/{USER}/repos?per_page=100&type=public")
    except Exception as e:  # keep the card renderable when the API is unreachable
        print(f"  warning: API unreachable ({e}), falling back to committed values")
        return {"public": 10, "stars": 0}
    return {
        "public": len(repos),
        "stars": sum(r.get("stargazers_count", 0) for r in repos),
    }


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(s, static=False):
    rows = [
        ("title", "pileup@github", ""),
        ("rule", "", ""),
        ("kv", "Studio", "PileUp Digital LLC, Wyoming"),
        ("kv", "Does", "Ships small software end to end"),
        ("gap", "", ""),
        ("head", "Shipped", ""),
        ("item", "BugMe", "iOS reminder app, live on the App Store"),
        ("sub", "", "12 tier escalation, built for ADHD brains"),
        ("sub", "", "trybugme.com"),
        ("gap", "", ""),
        ("item", "Minecraft plugins", "6 public, Paper 1.21"),
        ("sub", "", "45,402 lines of Java"),
        ("sub", "", "economies, custom items, progression"),
        ("gap", "", ""),
        ("head", "Stack", ""),
        ("kv", "Mobile", "Swift, SwiftUI, StoreKit"),
        ("kv", "Server", "Java, Node, TypeScript"),
        ("kv", "Data", "SQLite, MySQL, Postgres"),
        ("gap", "", ""),
        ("kv", "Public repos", str(s["public"])),
        ("kv", "Stars", str(s["stars"])),
    ]

    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" '
        'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>',
        "<style><![CDATA[",
    ]
    if static:
        o.append(".l{opacity:1}")
    else:
        o.append(".l{opacity:0}")
        o.append(
            "@keyframes in{from{opacity:0;transform:translateX(-6px)}"
            "to{opacity:1;transform:translateX(0)}}"
        )
        for i in range(len(rows)):
            o.append(f".l{i}{{animation:in {DUR}s ease-out {round(i * STEP, 3)}s forwards}}")
    o.append("]]></style>")

    y = PAD + FONT
    for i, (kind, k, v) in enumerate(rows):
        cls = "l" if static else f"l l{i}"
        if kind == "gap":
            y += LINE // 2
            continue
        if kind == "rule":
            o.append(
                f'<text class="{cls}" x="{PAD}" y="{y:.0f}" fill="{DIM}" '
                f'font-size="{FONT}">{"-" * 34}</text>'
            )
        elif kind == "title":
            o.append(
                f'<text class="{cls}" x="{PAD}" y="{y:.0f}" font-size="{FONT}">'
                f'<tspan fill="{KEY}" font-weight="bold">pileup</tspan>'
                f'<tspan fill="{DIM}">@</tspan>'
                f'<tspan fill="{ALT}" font-weight="bold">github</tspan></text>'
            )
        elif kind == "head":
            o.append(
                f'<text class="{cls}" x="{PAD}" y="{y:.0f}" fill="{WARN}" '
                f'font-size="{FONT}" font-weight="bold">{esc(k)}</text>'
            )
        elif kind == "item":
            o.append(
                f'<text class="{cls}" x="{PAD + 12}" y="{y:.0f}" font-size="{FONT}">'
                f'<tspan fill="{KEY}">- </tspan>'
                f'<tspan fill="{INK}" font-weight="bold">{esc(k)}</tspan>'
                f'<tspan fill="{DIM}">  {esc(v)}</tspan></text>'
            )
        elif kind == "sub":
            o.append(
                f'<text class="{cls}" x="{PAD + 26}" y="{y:.0f}" fill="{DIM}" '
                f'font-size="{FONT - 1}">{esc(v)}</text>'
            )
        else:
            o.append(
                f'<text class="{cls}" x="{PAD}" y="{y:.0f}" font-size="{FONT}">'
                f'<tspan fill="{ALT}">{esc(k)}</tspan>'
                f'<tspan fill="{DIM}">{" " * max(1, 15 - len(k))}</tspan>'
                f'<tspan fill="{INK}">{esc(v)}</tspan></text>'
            )
        y += LINE

    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    svg = build(stats(), static=bool(os.environ.get("STATIC")))
    with open("shipped.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote shipped.svg  {len(svg)} bytes")
