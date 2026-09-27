#!/usr/bin/env python3
"""
Generate the animated projects panel (projects-dark.svg, projects-light.svg).

Reads projects.json. Entries with a "repo" get live data from the GitHub API
(description fallback, stars, language, last push). Standard library only, so
the workflow needs no installs.

Usage: python scripts/generate_projects.py projects.json OUT_DIR
"""
import html
import json
import os
import sys
import textwrap
import urllib.request
from datetime import datetime, timezone

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
W = 1180
MARGIN = 4
GAP = 16
COLS = 2
CARD_W = (W - 2 * MARGIN - GAP * (COLS - 1)) // COLS
CARD_H = 192
HEAD_H = 44
WRAP = 64

LANG_COLORS = {
    "Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "C++": "#f34b7d",
    "C": "#555555", "Jupyter Notebook": "#DA5B0B", "HTML": "#e34c26", "CSS": "#563d7c",
}

THEMES = {
    "dark": {
        "BG": "#0b0613", "CARD": "#100819", "BAR": "#0d0616", "LINE": "rgba(255,255,255,0.07)",
        "STROKE": "rgba(192,132,252,0.35)", "ACCENT": "#c084fc", "ACCENT2": "#a855f7",
        "TEXT": "#f5f3ff", "MUTED": "#a1a1aa", "DIM": "#52525b",
        "PILL": "rgba(168,85,247,0.18)", "PILL_STROKE": "rgba(192,132,252,0.45)", "PILL_TEXT": "#e9d5ff",
        "MONO_BG": "#7e22ce", "MONO_TEXT": "#faf5ff",
    },
    "light": {
        "BG": "#faf5ff", "CARD": "#ffffff", "BAR": "#f3e8ff", "LINE": "rgba(0,0,0,0.07)",
        "STROKE": "rgba(126,34,206,0.30)", "ACCENT": "#7e22ce", "ACCENT2": "#9333ea",
        "TEXT": "#1e1033", "MUTED": "#52525b", "DIM": "#a1a1aa",
        "PILL": "rgba(147,51,234,0.10)", "PILL_STROKE": "rgba(126,34,206,0.35)", "PILL_TEXT": "#6b21a8",
        "MONO_BG": "#7e22ce", "MONO_TEXT": "#ffffff",
    },
}


def esc(s):
    return html.escape(str(s), quote=True)


def fetch(repo):
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}",
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-projects"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except Exception as e:  # keep the panel rendering even if the API is unavailable
        print(f"warning: could not fetch {repo}: {e}", file=sys.stderr)
        return {}


def ago(iso):
    if not iso:
        return ""
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    days = (datetime.now(timezone.utc) - dt).days
    if days < 1:
        return "updated today"
    if days < 30:
        return f"updated {days}d ago"
    if days < 365:
        return f"updated {days // 30}mo ago"
    return f"updated {days // 365}y ago"


def card(p, i, x, y, t):
    live = p.get("_live", {})
    desc = p.get("description") or live.get("description") or ""
    lines = textwrap.wrap(desc, WRAP)[:3]
    path = p["repo"] if p.get("repo") else f"~/projects/{p['name'].lower().replace(' ', '-').replace('&', 'and')}"
    delay = 0.25 + i * 0.18
    o = []
    a = o.append
    a(f'<g opacity="0" transform="translate({x},{y + 12})">')
    a(f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.6s" fill="freeze"/>')
    a(f'<animateTransform attributeName="transform" type="translate" from="{x} {y + 12}" to="{x} {y}" '
      f'begin="{delay:.2f}s" dur="0.6s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/>')
    a(f'<rect width="{CARD_W}" height="{CARD_H}" rx="12" fill="{t["CARD"]}" stroke="{t["STROKE"]}"/>')
    a(f'<path d="M0 12a12 12 0 0 1 12-12h{CARD_W - 24}a12 12 0 0 1 12 12v16H0z" fill="{t["BAR"]}"/>')
    a(f'<line x1="0" y1="28" x2="{CARD_W}" y2="28" stroke="{t["LINE"]}"/>')
    for k, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        a(f'<circle cx="{16 + k * 14}" cy="14" r="4" fill="{c}"/>')
    a(f'<text x="{CARD_W / 2}" y="18" text-anchor="middle" font-size="10.5" fill="{t["MUTED"]}">{esc(path)}</text>')

    # monogram
    initials = "".join(w[0] for w in p["name"].replace("&", "").split()[:2]).upper()
    a(f'<rect x="18" y="44" width="40" height="40" rx="10" fill="{t["MONO_BG"]}"/>')
    a(f'<text x="38" y="69.5" text-anchor="middle" font-size="15" font-weight="700" fill="{t["MONO_TEXT"]}">{esc(initials)}</text>')
    a(f'<text x="72" y="60" font-size="16" font-weight="700" fill="{t["TEXT"]}">{esc(p["name"])}</text>')
    sub = p.get("subtitle") or (live.get("language") and f"{live['language']} repository") or ""
    a(f'<text x="72" y="79" font-size="11.5" fill="{t["ACCENT"]}">{esc(sub)}</text>')

    for j, ln in enumerate(lines):
        a(f'<text x="18" y="{106 + j * 17}" font-size="12" fill="{t["MUTED"]}">{esc(ln)}</text>')

    # tags
    tx = 18
    for tag in p.get("tags", [])[:5]:
        tw = len(tag) * 6.9 + 16
        a(f'<rect x="{tx}" y="{CARD_H - 30}" width="{tw:.0f}" height="19" rx="9.5" fill="{t["PILL"]}" stroke="{t["PILL_STROKE"]}"/>')
        a(f'<text x="{tx + tw / 2:.1f}" y="{CARD_H - 16.5}" text-anchor="middle" font-size="11" fill="{t["PILL_TEXT"]}">{esc(tag)}</text>')
        tx += tw + 6

    # right-bottom meta
    if p.get("repo"):
        lang = live.get("language") or ""
        meta = f'&#9733; {live.get("stargazers_count", 0)}'
        if lang:
            meta += f'  <tspan fill="{LANG_COLORS.get(lang, t["ACCENT2"])}">&#9679;</tspan> {esc(lang)}'
        up = ago(live.get("pushed_at"))
        if up:
            meta += f'  &#183; {up}'
    else:
        meta = f'<tspan fill="{t["ACCENT"]}">&#9679;</tspan> academic project'
    a(f'<text x="{CARD_W - 16}" y="{CARD_H - 16.5}" text-anchor="end" font-size="11" fill="{t["DIM"]}" xml:space="preserve">{meta}</text>')
    a('</g>')
    return "".join(o)


def build(projects, theme):
    t = THEMES[theme]
    rows = (len(projects) + COLS - 1) // COLS
    h = HEAD_H + rows * CARD_H + (rows - 1) * GAP + MARGIN * 2
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
         f'font-family="{FONT}" role="img" aria-label="Projects">']
    o.append(f'<text x="{MARGIN + 4}" y="22" font-size="12" letter-spacing="3" fill="{t["ACCENT"]}">PROJECTS.LIST</text>')
    o.append(f'<text x="{MARGIN + 136}" y="22" font-size="11" fill="{t["DIM"]}">./projects.sh --all</text>')
    o.append(f'<line x1="{MARGIN + 280}" y1="18" x2="{W - MARGIN - 4}" y2="18" stroke="{t["STROKE"]}" stroke-opacity="0.6"/>')
    for i, p in enumerate(projects):
        r, c = divmod(i, COLS)
        # centre a lone card on the last row
        x = MARGIN + c * (CARD_W + GAP)
        if i == len(projects) - 1 and len(projects) % COLS == 1:
            x = (W - CARD_W) // 2
        y = MARGIN + HEAD_H - 10 + r * (CARD_H + GAP)
        o.append(card(p, i, x, y, t))
    o.append('</svg>')
    return "\n".join(o)


def main():
    src, out = sys.argv[1], sys.argv[2]
    projects = json.load(open(src, encoding="utf-8"))
    for p in projects:
        if p.get("repo"):
            p["_live"] = fetch(p["repo"])
    os.makedirs(out, exist_ok=True)
    for theme in THEMES:
        path = os.path.join(out, f"projects-{theme}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(build(projects, theme))
        print("wrote", path)


if __name__ == "__main__":
    main()
