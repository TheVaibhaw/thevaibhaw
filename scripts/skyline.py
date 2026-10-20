#!/usr/bin/env python3
"""Render the last year of GitHub contributions as an animated 3D isometric neon city.

    python3 scripts/skyline.py <github-user> <out.svg>

Reads the public contributions calendar, so no token is needed. On any fetch/parse
failure it still writes a "signal lost" card instead of breaking the README.
"""
import datetime as dt
import html
import math
import re
import sys
import urllib.request

from neon import AMBER, BG0, CYAN, DIM, LIME, MAG, TXT, VIO, glow_defs, hud_corners, scanlines, stars, svg, write

LEVELS = [  # top, right side, front side
    ("#1a0d33", "#120826", "#0e061e"),
    ("#6d28d9", "#4c1d95", "#36126e"),
    ("#a78bfa", "#7c3aed", "#5b21b6"),
    (CYAN, "#0891b2", "#0e5f75"),
    (MAG, "#c0179f", "#86106f"),
]


def fetch(user):
    req = urllib.request.Request(
        f"https://github.com/users/{user}/contributions",
        headers={"User-Agent": "profile-skyline"},
    )
    page = urllib.request.urlopen(req, timeout=30).read().decode()
    cells = {}
    for tag in re.findall(r"<td[^>]*data-date[^>]*>", page):
        date = re.search(r'data-date="([\d-]+)"', tag).group(1)
        cid = re.search(r'id="([^"]+)"', tag).group(1)
        level = int(re.search(r'data-level="(\d)"', tag).group(1))
        cells[cid] = [dt.date.fromisoformat(date), level, 0]
    for cid, text in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)', page):
        m = re.match(r"\s*([\d,]+) contribution", html.unescape(text))
        if cid in cells and m:
            cells[cid][2] = int(m.group(1).replace(",", ""))
    days = sorted(cells.values())
    if len(days) < 300:
        raise ValueError(f"only {len(days)} days parsed")
    return days


def streaks(days):
    longest = run = 0
    for _, _, n in days:
        run = run + 1 if n else 0
        longest = max(longest, run)
    current = 0
    tail = days[:-1] if days and days[-1][2] == 0 else days  # today may simply not have started yet
    for _, _, n in reversed(tail):
        if not n:
            break
        current += 1
    return current, longest


def render(user, days):
    W, H = 1200, 640
    u = (17.4, 5.0)    # one week step
    v = (-11.0, 6.4)   # one weekday step
    x0, y0 = 172, 262
    maxc = max(n for _, _, n in days) or 1
    start = days[0][0] - dt.timedelta(days=(days[0][0].weekday() + 1) % 7)

    def at(w, d, h=0.0):
        return (x0 + w * u[0] + d * v[0], y0 + w * u[1] + d * v[1] - h)

    def quad(*pts):
        return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z"

    bars = []
    for date, level, n in days:
        w, d = (date - start).days // 7, (date - start).days % 7
        bars.append((w, d, level, n, date))
    bars.sort(key=lambda b: (b[0] + b[1], b[0]))  # painter's order: back to front

    css = """
@keyframes sweep{0%{transform:translate(-60px,-18px)}100%{transform:translate(1000px,280px)}}
.sweep{animation:sweep 5s linear infinite}
"""
    b = ["<defs>" + glow_defs("glow", 3) + glow_defs("glowS", 1.5) +
         f'<linearGradient id="lz" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>'
         f'<stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>'
         f'</linearGradient><radialGradient id="bgG" cx="50%" cy="70%" r="70%"><stop offset="0" stop-color="#22093f"/>'
         f'<stop offset="1" stop-color="{BG0}"/></radialGradient></defs>',
         f'<rect width="{W}" height="{H}" rx="14" fill="url(#bgG)"/>', stars(W, H, 60, seed=5, ymax=260)]

    weeks = max(x[0] for x in bars) + 1
    m = 0.6
    plate = quad(at(-m, -m), at(weeks + m, -m), at(weeks + m, 7 + m), at(-m, 7 + m))
    b.append(f'<path d="{plate}" fill="#0b0420" stroke="{CYAN}" stroke-opacity=".5" stroke-width="1.5"/>')
    sx, sy = at(-m, 7 + m)
    ex, ey = at(weeks + m, 7 + m)
    b.append(f'<path d="M{sx:.1f},{sy:.1f}L{ex:.1f},{ey:.1f}L{ex:.1f},{ey + 14:.1f}L{sx:.1f},{sy + 14:.1f}Z" '
             f'fill="{MAG}" fill-opacity=".25" stroke="{MAG}" stroke-opacity=".6"/>')

    g = 0.14
    for w, d, level, n, date in bars:
        top, side, front = LEVELS[level]
        if not n:
            b.append(f'<path d="{quad(at(w+g, d+g), at(w+1-g, d+g), at(w+1-g, d+1-g), at(w+g, d+1-g))}" fill="{top}"/>')
            continue
        h = 6 + 150 * math.sqrt(n / maxc)

        def faces(hh):
            t = [at(w + g, d + g, hh), at(w + 1 - g, d + g, hh), at(w + 1 - g, d + 1 - g, hh), at(w + g, d + 1 - g, hh)]
            right = quad(t[1], t[2], at(w + 1 - g, d + 1 - g), at(w + 1 - g, d + g))
            fr = quad(t[3], t[2], at(w + 1 - g, d + 1 - g), at(w + g, d + 1 - g))
            return quad(*t), right, fr

        flat, full = faces(0.5), faces(h)
        begin = 0.4 + w * 0.045 + d * 0.02
        anim = ('<animate attributeName="d" values="{a};{b}" begin="{s:.2f}s" dur=".9s" fill="freeze" '
                'calcMode="spline" keyTimes="0;1" keySplines=".2 .9 .25 1"/>')
        for k, col in ((1, side), (2, front), (0, top)):
            extra = ' filter="url(#glowS)"' if k == 0 and level == 4 else ""
            b.append(f'<path d="{flat[k]}" fill="{col}"{extra}><title>{n} on {date}</title>'
                     + anim.format(a=flat[k], b=full[k], s=begin) + "</path>")

    # laser sweeping across the city along the week axis
    lx, ly = at(0, -1.2)
    lx2, ly2 = at(0, 8.2)
    b.append(f'<g class="sweep" style="mix-blend-mode:screen"><path d="M{lx:.0f},{ly:.0f}L{lx2:.0f},{ly2:.0f}" '
             f'stroke="url(#lz)" stroke-width="5" filter="url(#glow)" transform="translate(0,-40)"/></g>')

    # month labels along the front edge
    seen = set()
    for w, d, _, _, date in sorted(bars):
        if date.day <= 7 and date.month not in seen and d == 0:
            seen.add(date.month)
            x, y = at(w, 7 + m)
            b.append(f'<text x="{x + 4:.0f}" y="{y + 30:.0f}" class="mono" font-size="11" fill="{DIM}">'
                     f'{date.strftime("%b").upper()}</text>')

    total = sum(n for _, _, n in days)
    best = max(days, key=lambda x: x[2])
    cur, longest = streaks(days)
    b.append(f'<text x="40" y="54" class="disp" font-size="24" fill="{CYAN}" letter-spacing="2">CONTRIBUTION SKYLINE</text>')
    b.append(f'<text x="40" y="78" class="mono" font-size="12" fill="{DIM}">@{user} // last 365 days // rebuilt '
             f'{dt.date.today().isoformat()} by github actions</text>')
    tiles = [(f"{total:,}", "TOTAL", CYAN), (str(best[2]), "BEST DAY", MAG),
             (f"{cur}d", "CURRENT STREAK", LIME), (f"{longest}d", "LONGEST STREAK", AMBER)]
    for i, (num, lab, c) in enumerate(tiles):
        x = 640 + i * 132
        b.append(f'<g transform="translate({x},30)"><path d="M0,0H112L122,10V62H10L0,52Z" fill="{BG0}" '
                 f'fill-opacity=".85" stroke="{c}" stroke-width="1.5"/>'
                 f'<text x="61" y="34" class="disp" font-size="22" fill="{c}" text-anchor="middle">{num}</text>'
                 f'<text x="61" y="51" class="mono" font-size="9.5" fill="{TXT}" text-anchor="middle" letter-spacing="1">'
                 f'{lab}</text></g>')
    b.append(f'<text x="40" y="{H - 26}" class="mono" font-size="11" fill="{DIM}">'
             f'<tspan fill="{VIO}">■</tspan> low  <tspan fill="{CYAN}">■</tspan> high  '
             f'<tspan fill="{MAG}">■</tspan> beast   // height = sqrt(contributions)</text>')
    b.append(hud_corners(14, 14, W - 28, H - 28, CYAN, 24, 2))
    b.append(scanlines(W, H, opacity=.05))
    return svg(W, H, "".join(b), css, f"{user}'s contributions over the last year as a 3D city")


def signal_lost(user, err):
    W, H = 1200, 200
    body = (f'<rect width="{W}" height="{H}" rx="14" fill="{BG0}"/>'
            f'<text x="{W/2}" y="96" class="disp" font-size="34" fill="{MAG}" text-anchor="middle">'
            f'<tspan class="flicker">SIGNAL LOST</tspan></text>'
            f'<text x="{W/2}" y="132" class="mono" font-size="13" fill="{DIM}" text-anchor="middle">'
            f'skyline for @{user} will rebuild on the next run // {html.escape(str(err))[:90]}</text>')
    return svg(W, H, body, "", "Contribution skyline unavailable")


def main():
    user, out = sys.argv[1], sys.argv[2]
    try:
        content = render(user, fetch(user))
    except Exception as e:  # never leave the README with a broken image
        print(f"skyline failed: {e}", file=sys.stderr)
        content = signal_lost(user, e)
    write(out, content)


if __name__ == "__main__":
    main()
