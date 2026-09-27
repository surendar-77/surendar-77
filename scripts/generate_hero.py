#!/usr/bin/env python3
"""
Generate the animated terminal-style hero banner (assets/hero-dark.svg, assets/hero-light.svg).

Left panel: particles that hold the panther silhouette, then morph through stack logos
(Python, PyTorch, </>, OpenCV) every few seconds and back, on a loop.
Right panel: a "./profile.sh --live" readout whose lines type out one by one.

Run locally when the details change:  pip install resvg-py pillow && python scripts/generate_hero.py
Panther silhouette: "Vintage Heraldic Panther Silhouette", Wikimedia Commons, CC0.
Logos in assets/morph: Simple Icons (CC0).
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
N_PARTICLES = 720

# Morph cycle: panther -> stack logos -> panther. Logos: Simple Icons (CC0), code glyph drawn here.
MORPH = os.path.join(ASSETS, "morph")
SHAPES = [
    (PANTHER, MAP_W - 40, MAP_H - 40),
    (os.path.join(MORPH, "python.svg"), 290, 290),
    (os.path.join(MORPH, "pytorch.svg"), 290, 290),
    (os.path.join(MORPH, "code.svg"), 320, 320),
    (os.path.join(MORPH, "opencv.svg"), 290, 290),
]
MOVE, HOLD = 0.9, 2.1  # seconds per transition / per pose


def shape_pixels(path, box_w, box_h):
    """Render an SVG into the map area and return every filled pixel (x, y)."""
    src = open(path, encoding="utf-8").read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', src).group(1).split()]
    scale = min(box_w / vb[2], box_h / vb[3])
    rw, rh = int(vb[2] * scale), int(vb[3] * scale)
    png = bytes(resvg_py.svg_to_bytes(svg_string=src, width=rw, height=rh))
    alpha = Image.open(io.BytesIO(png)).convert("RGBA").getchannel("A")
    ox = MAP_X + (MAP_W - rw) / 2
    oy = MAP_Y + (MAP_H - rh) / 2
    filled = {(x, y) for y in range(rh) for x in range(rw) if alpha.getpixel((x, y)) > 128}
    edge = [p for p in filled if any((p[0] + dx, p[1] + dy) not in filled for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)))]
    to_map = lambda pts: [(ox + x, oy + y) for x, y in pts]
    return to_map(sorted(filled)), to_map(sorted(edge))


def shape_targets(rnd):
    """N_PARTICLES target points per shape, ordered top-to-bottom so morphs flow instead of scrambling."""
    targets = []
    for path, bw, bh in SHAPES:
        fill, edge = shape_pixels(path, bw, bh)
        # half the particles trace the outline so logos stay recognisable, half fill the body
        n_edge = N_PARTICLES // 2
        pts = rnd.sample(edge, min(n_edge, len(edge)))
        pts += rnd.sample(fill, N_PARTICLES - len(pts))
        pts.sort(key=lambda p: (round(p[1] / 12), p[0]))
        targets.append(pts)
    return targets


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

    n = len(SHAPES)
    cycle = n * (MOVE + HOLD)
    times, splines = [0.0], []
    for k in range(n):
        base = k * (MOVE + HOLD)
        times += [base + HOLD, base + HOLD + MOVE]
        splines += ["0 0 1 1", "0.45 0 0.2 1"]
    kt = ";".join(f"{x / cycle:.4f}" for x in times)
    ks = ";".join(splines)
    targets = shape_targets(rnd)
    # crisp panther underlay, visible while the particles hold the panther pose
    fade_out = HOLD / cycle
    fade_in = (cycle - 0.25) / cycle
    a(f'<g opacity="0.55"><g opacity="1">'
      f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;{fade_out:.4f};{(HOLD + 0.35) / cycle:.4f};{fade_in:.4f};1" '
      f'dur="{cycle:.1f}s" begin="0.6s" repeatCount="indefinite"/>')
    src = open(PANTHER, encoding="utf-8").read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', src).group(1).split()]
    ps = min((MAP_W - 40) / vb[2], (MAP_H - 40) / vb[3])
    px0 = MAP_X + (MAP_W - vb[2] * ps) / 2
    py0 = MAP_Y + (MAP_H - vb[3] * ps) / 2
    body = "".join(f'<path d="{d}"/>' for d in re.findall(r'<path[^>]*\sd="([^"]+)"', src))
    a(f'<g transform="translate({px0:.1f},{py0:.1f}) scale({ps:.5f})" fill="{t["DOTS"][3]}">{body}</g></g></g>')

    a('<defs>' + "".join(f'<circle id="p{c}" r="1.7" fill="{col}"/>' for c, col in enumerate(t["DOTS"])) + '</defs>')
    a('<g filter="url(#glow)" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="0.2s" dur="1s" fill="freeze"/>')
    for i in range(N_PARTICLES):
        seq = [targets[k][i] for k in range(n)]
        vals = [seq[0]]
        for k in range(n):
            nxt = seq[(k + 1) % n]
            vals += [seq[k], nxt]
        vals = ";".join(f"{x:.0f} {y:.0f}" for x, y in vals)
        sx, sy = rnd.uniform(MAP_X, MAP_X + MAP_W), rnd.uniform(MAP_Y, MAP_Y + MAP_H)
        shade = min(4, int((seq[0][1] - MAP_Y) / MAP_H * 5))
        a(f'<use href="#p{shade}" transform="translate({sx:.0f} {sy:.0f})">'
          f'<animateTransform attributeName="transform" type="translate" values="{vals}" keyTimes="{kt}" '
          f'calcMode="spline" keySplines="{ks}" dur="{cycle:.1f}s" begin="0.6s" repeatCount="indefinite"/></use>')
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
