#!/usr/bin/env python3
"""
Generate the animated terminal-style hero banner (assets/hero-dark.svg, assets/hero-light.svg).

Left panel: the panther silhouette rebuilt from particles that fly in and assemble.
Right panel: a "./profile.sh --live" readout whose lines type out one by one.

Run locally when the details change:  pip install resvg-py pillow && python scripts/generate_hero.py
Panther silhouette: "Vintage Heraldic Panther Silhouette", Wikimedia Commons, CC0.
"""
import html
import io
import os
import random
import re

import resvg_py
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
PANTHER = os.path.join(ASSETS, "panther.svg")

W, H = 1180, 610
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

TITLE = "surendar@ai-lab ~ % ./profile.sh --live"
INFO = [
    ("Subject", "Surendar G K"),
    ("Role", "AI/ML Developer"),
    ("Origin", "Bengaluru, India"),
    ("Education", "B.E. AI & ML · Final Year"),
    ("Status", "Building + Learning + Shipping"),
    ("ToolChain", "VS Code, Git, Jupyter, Colab"),
    None,
    ("Core.Lang", "Python, JavaScript, C, C++"),
    ("Core.ML", "PyTorch, scikit-learn, OpenCV"),
    ("Core.AI", "LLMs, RAG, Hugging Face, Ollama"),
    ("Core.Web", "React, Node.js, Flask"),
    ("Core.Infra", "AWS, Docker, CI/CD"),
    "Contact",
    ("Grid.Mail", "arosurendar@gmail.com"),
    ("Grid.LinkedIn", "surendar-gk"),
    ("Grid.GitHub", "@surendar-77"),
    ("Grid.Portfolio", "my-portfolio-eta-tawny-13.vercel.app"),
]
LINE_CHARS = 66  # key + dotted leader + value, fixed width

THEMES = {
    "dark": {
        "BG": "#0b0613", "PANEL": "#100819", "BAR": "#0d0616", "BARLINE": "rgba(255,255,255,0.07)",
        "ACCENT": "#c084fc", "KEY": "#a855f7", "TEXT": "#f5f3ff", "MUTED": "#a1a1aa", "DIM": "#52525b",
        "LIVE": "#f0abfc", "FRAME": "rgba(192,132,252,0.55)",
        "DOTS": ["#f5d0fe", "#d8b4fe", "#c084fc", "#a855f7", "#7e22ce"],
        "BORDER": ["#7e22ce", "#c084fc", "#f0abfc"],
    },
    "light": {
        "BG": "#faf5ff", "PANEL": "#ffffff", "BAR": "#f3e8ff", "BARLINE": "rgba(0,0,0,0.07)",
        "ACCENT": "#7e22ce", "KEY": "#9333ea", "TEXT": "#1e1033", "MUTED": "#52525b", "DIM": "#a1a1aa",
        "LIVE": "#c026d3", "FRAME": "rgba(126,34,206,0.45)",
        "DOTS": ["#3b0764", "#581c87", "#6b21a8", "#7e22ce", "#9333ea"],
        "BORDER": ["#6b21a8", "#a855f7", "#c026d3"],
    },
}

# particle map area (left panel)
MAP_X, MAP_Y, MAP_W, MAP_H = 36, 84, 400, 492
STEP = 8


def panther_points():
    """Sample the silhouette on a grid; return (x, y) centres of filled cells."""
    src = open(PANTHER, encoding="utf-8").read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', src).group(1).split()]
    vw, vh = vb[2], vb[3]
    scale = min((MAP_W - 40) / vw, (MAP_H - 40) / vh)
    rw, rh = int(vw * scale), int(vh * scale)
    png = bytes(resvg_py.svg_to_bytes(svg_string=src, width=rw, height=rh))
    img = Image.open(io.BytesIO(png)).convert("RGBA")
    w, h = img.size
    alpha = img.getchannel("A")
    ox = MAP_X + (MAP_W - w) / 2
    oy = MAP_Y + (MAP_H - h) / 2
    pts = []
    for y in range(STEP // 2, h, STEP):
        for x in range(STEP // 2, w, STEP):
            if alpha.getpixel((x, y)) > 100:
                pts.append((ox + x, oy + y))
    return pts


def esc(s):
    return html.escape(s, quote=True)


def build(theme):
    t = THEMES[theme]
    rnd = random.Random(77)
    out = []
    a = out.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'font-family="{FONT}" role="img" aria-label="Surendar G K - profile.sh --live">')
    a('<!-- Panther silhouette: "Vintage Heraldic Panther Silhouette", Wikimedia Commons, CC0 -->')
    b0, b1, b2 = t["BORDER"]
    a('<defs>')
    a(f'<linearGradient id="border" x1="0" y1="0" x2="1" y2="1">'
      f'<stop offset="0" stop-color="{b0}"><animate attributeName="stop-color" values="{b0};{b1};{b2};{b0}" dur="9s" repeatCount="indefinite"/></stop>'
      f'<stop offset="0.5" stop-color="{b1}"><animate attributeName="stop-color" values="{b1};{b2};{b0};{b1}" dur="9s" repeatCount="indefinite"/></stop>'
      f'<stop offset="1" stop-color="{b2}"><animate attributeName="stop-color" values="{b2};{b0};{b1};{b2}" dur="9s" repeatCount="indefinite"/></stop>'
      '</linearGradient>')
    a('<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/>'
      '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    a('<clipPath id="win"><rect x="2" y="2" width="1176" height="606" rx="16"/></clipPath>')
    a('</defs>')

    # window
    a(f'<rect x="2" y="2" width="1176" height="606" rx="16" fill="{t["BG"]}"/>')
    a('<g clip-path="url(#win)">')
    a(f'<rect x="2" y="2" width="1176" height="46" fill="{t["BAR"]}"/>')
    a(f'<line x1="2" y1="48" x2="1178" y2="48" stroke="{t["BARLINE"]}"/>')
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        a(f'<circle cx="{30 + i * 20}" cy="25" r="6" fill="{c}"/>')
    a(f'<text x="590" y="29" text-anchor="middle" font-size="12" fill="{t["MUTED"]}">{esc(TITLE)}</text>')
    a(f'<rect x="446" y="60" width="716" height="530" rx="10" fill="{t["PANEL"]}" opacity="0.6"/>')
    a('</g>')
    a('<rect x="2" y="2" width="1176" height="606" rx="16" fill="none" stroke="url(#border)" stroke-width="2.5"/>')

    # left: particle panther
    a(f'<text x="38" y="74" font-size="10" letter-spacing="3" fill="{t["DIM"]}">VISUAL.MAP</text>')
    fx0, fy0, fx1, fy1 = MAP_X, MAP_Y, MAP_X + MAP_W, MAP_Y + MAP_H
    L = 14
    for (x, y, dx, dy) in [(fx0, fy0, 1, 1), (fx1, fy0, -1, 1), (fx0, fy1, 1, -1), (fx1, fy1, -1, -1)]:
        a(f'<path d="M{x} {y + dy * L}V{y}H{x + dx * L}" fill="none" stroke="{t["ACCENT"]}" stroke-width="2"/>')
    a(f'<rect x="{fx0}" y="{fy0}" width="{MAP_W}" height="{MAP_H}" fill="none" stroke="{t["FRAME"]}" stroke-opacity="0.35"/>')
    # scan line
    a(f'<rect x="{fx0 + 1}" y="{fy0}" width="{MAP_W - 2}" height="2" fill="{t["ACCENT"]}" opacity="0.35">'
      f'<animate attributeName="y" values="{fy0};{fy1 - 2};{fy0}" dur="6s" repeatCount="indefinite"/></rect>')

    pts = panther_points()
    ys = [p[1] for p in pts]
    ymin, ymax = min(ys), max(ys)
    a('<g filter="url(#glow)">')
    for (x, y) in pts:
        shade = t["DOTS"][min(4, int((y - ymin) / (ymax - ymin + 1) * 5))]
        sx = rnd.uniform(fx0, fx1)
        sy = rnd.uniform(fy0, fy1)
        delay = 0.2 + rnd.uniform(0, 1.2)
        r = 2.9 if rnd.random() > 0.15 else 2.0
        tw = rnd.uniform(2.5, 5)
        a(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{r}" fill="{shade}" opacity="0">'
          f'<animate attributeName="cx" from="{sx:.1f}" to="{x:.1f}" begin="{delay:.2f}s" dur="1.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/>'
          f'<animate attributeName="cy" from="{sy:.1f}" to="{y:.1f}" begin="{delay:.2f}s" dur="1.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/>'
          f'<animate attributeName="opacity" values="0;1;0.55;1" keyTimes="0;0.3;0.65;1" begin="{delay:.2f}s" dur="{tw:.1f}s" fill="freeze"/>'
          '</circle>')
    a('</g>')

    # right: system info
    a(f'<text x="470" y="106" font-size="13" letter-spacing="2" fill="{t["ACCENT"]}" filter="url(#glow)">SYSTEM.INFO</text>')
    a(f'<line x1="580" y1="102" x2="1060" y2="102" stroke="{t["DIM"]}" stroke-opacity="0.5"/>')
    a(f'<g fill="{t["LIVE"]}" font-size="12" font-weight="700"><circle cx="1080" cy="102" r="3.5">'
      '<animate attributeName="opacity" values="1;0.2;1" dur="1.4s" repeatCount="indefinite"/></circle>'
      '<text x="1125" y="106" text-anchor="end">LIVE</text></g>')

    y = 140
    begin = 1.0
    for idx, item in enumerate(INFO):
        if item is None:
            y += 8
            continue
        cid = f"l{idx}"
        if isinstance(item, str):
            dashes = "-" * (LINE_CHARS - len(item) - 3)
            body = (f'<tspan fill="{t["ACCENT"]}" font-weight="700">- {esc(item)} </tspan>'
                    f'<tspan fill="{t["DIM"]}">{dashes}</tspan>')
            y += 8
        else:
            k, v = item
            dots = "." * max(3, LINE_CHARS - len(k) - len(v) - 2)
            body = (f'<tspan fill="{t["KEY"]}">{esc(k)}</tspan><tspan fill="{t["DIM"]}"> {dots} </tspan>'
                    f'<tspan fill="{t["TEXT"]}">{esc(v)}</tspan>')
        a(f'<clipPath id="{cid}"><rect x="466" y="{y - 16}" width="0" height="22">'
          f'<animate attributeName="width" from="0" to="680" begin="{begin:.2f}s" dur="0.45s" fill="freeze"/></rect></clipPath>')
        a(f'<text x="470" y="{y}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" '
          f'xml:space="preserve" clip-path="url(#{cid})">{body}</text>')
        y += 23
        begin += 0.18

    a(f'<text x="470" y="{y + 12}" font-size="14" fill="{t["MUTED"]}">&#9656; More about me &amp; my projects below &#8595;'
      f'<tspan fill="{t["ACCENT"]}"> &#9608;<animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan></text>')
    a('</svg>')
    return "\n".join(out)


if __name__ == "__main__":
    for theme in THEMES:
        path = os.path.join(ASSETS, f"hero-{theme}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(build(theme))
        print("wrote", path, os.path.getsize(path), "bytes")
