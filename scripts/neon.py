"""Shared design system for the profile SVGs: palette, embedded fonts, 3D math, helpers.

Stdlib only, so the GitHub Action can import it without installing anything.
Fonts in scripts/fonts/ are OFL-licensed subsets of Orbitron and JetBrains Mono.
"""
import base64
import math
import os
import random
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))

BG0 = "#ffffff"   # GitHub page white, so images blend into the README
BG1 = "#ffffff"
CYAN = "#0891b2"
MAG = "#c026d3"
VIO = "#7c3aed"
LIME = "#16a34a"
RED = "#e11d48"
AMBER = "#d97706"
TXT = "#0f172a"
DIM = "#64748b"
HI = "#4338ca"                   # hot core of lasers / CORE label
SKY = "#fbf5ff"                  # faint horizon glow
SLAB = ("#c7d2fe", "#ddd6fe")    # 3D slab under panels (far, near)
PANEL = "#eef2ff"                # title bars, plates
TRACK = "#e2e8f0"                # empty meter track
SIDE = ("#c4b5fd", "#a78bfa")    # extruded text sides
FACE_MID = "#1e1b4b"
STAR = "#a5b4fc"
BLEND = "multiply"


def tone(c):
    """Darken a brand colour until it reads on a white page."""
    if c.lower() == "#ffffff":
        return TXT
    r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
    while 0.2126 * r + 0.7152 * g + 0.0722 * b > 135:
        r, g, b = int(r * .88), int(g * .88), int(b * .88)
    return f"#{r:02x}{g:02x}{b:02x}"


DISPLAY = "'NeonDisplay', 'Orbitron', 'Arial Black', sans-serif"
MONO = "'NeonMono', 'JetBrains Mono', 'Fira Code', Consolas, monospace"
MONO_BOLD = "'NeonMonoBold', 'JetBrains Mono', 'Fira Code', Consolas, monospace"


def _font(name, file):
    with open(os.path.join(HERE, "fonts", file), "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"@font-face{{font-family:'{name}';src:url(data:font/woff;base64,{data}) format('woff');}}"


def font_css():
    return (
        _font("NeonDisplay", "orbitron-900.woff")
        + _font("NeonMono", "jbmono-500.woff")
        + _font("NeonMonoBold", "jbmono-800.woff")
    )


BASE_CSS = f"""
.disp{{font-family:{DISPLAY};font-weight:900;}}
.mono{{font-family:{MONO};}}
.monob{{font-family:{MONO_BOLD};font-weight:800;}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
@keyframes flicker{{0%,100%{{opacity:1}}41%{{opacity:1}}42%{{opacity:.2}}43%{{opacity:1}}45%{{opacity:.4}}46%{{opacity:1}}88%{{opacity:1}}89%{{opacity:.3}}90%{{opacity:1}}}}
@keyframes twinkle{{0%,100%{{opacity:.15}}50%{{opacity:1}}}}
@keyframes jitterA{{0%,86%,100%{{transform:translate(0,0)}}87%{{transform:translate(-6px,2px)}}89%{{transform:translate(5px,-2px)}}91%{{transform:translate(-3px,0)}}93%{{transform:translate(0,0)}}}}
@keyframes jitterB{{0%,86%,100%{{transform:translate(0,0)}}87%{{transform:translate(6px,-2px)}}89%{{transform:translate(-5px,2px)}}91%{{transform:translate(3px,1px)}}93%{{transform:translate(0,0)}}}}
@keyframes slice{{0%,84%,100%{{opacity:0;transform:translateX(0)}}85%{{opacity:.9;transform:translateX(-40px)}}87%{{opacity:.9;transform:translateX(30px)}}89%{{opacity:0}}}}
@keyframes floaty{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}
@keyframes pulse{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}
.blink{{animation:blink 1s steps(1) infinite}}
.flicker{{animation:flicker 4s infinite}}
.glA{{animation:jitterA 3.2s infinite}}
.glB{{animation:jitterB 3.2s infinite}}
.float{{animation:floaty 6s ease-in-out infinite}}
"""


def svg(w, h, body, css="", title=""):
    style = font_css() + BASE_CSS + css
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{escape(title)}">'
        f"<title>{escape(title)}</title><style>{style}</style>{body}</svg>"
    )


def glow_defs(fid="glow", std=4):
    return (
        f'<filter id="{fid}" x="-30%" y="-30%" width="160%" height="160%">'
        f'<feGaussianBlur stdDeviation="{std}" result="b"/>'
        f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    )


def hud_corners(x, y, w, h, c=CYAN, s=18, sw=2):
    p = (
        f"M{x},{y+s}V{y}H{x+s} M{x+w-s},{y}H{x+w}V{y+s} "
        f"M{x+w},{y+h-s}V{y+h}H{x+w-s} M{x+s},{y+h}H{x}V{y+h-s}"
    )
    return f'<path d="{p}" fill="none" stroke="{c}" stroke-width="{sw}"/>'


def stars(w, h, n=70, seed=7, ymax=None):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, ymax or h)
        r = rnd.choice([0.6, 0.8, 1.0, 1.4])
        c = rnd.choice([STAR, CYAN, MAG, STAR])
        out.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{c}" '
            f'style="animation:twinkle {rnd.uniform(2,5):.1f}s {rnd.uniform(0,4):.1f}s infinite"/>'
        )
    return "".join(out)


def synth_floor(w, horizon, bottom, color=MAG, lines=14, dur=3, vlines=26, cx=None):
    """Perspective grid floor that scrolls toward the viewer."""
    cx = w / 2 if cx is None else cx
    depth = bottom - horizon
    parts = [f'<clipPath id="floorclip"><rect x="0" y="{horizon}" width="{w}" height="{depth}"/></clipPath>',
             f'<linearGradient id="floorfade" x1="0" y1="{horizon}" x2="0" y2="{bottom}" gradientUnits="userSpaceOnUse">'
             f'<stop offset="0" stop-color="{color}" stop-opacity="0"/>'
             f'<stop offset=".35" stop-color="{color}" stop-opacity=".55"/>'
             f'<stop offset="1" stop-color="{color}" stop-opacity="1"/></linearGradient>']
    g = [f'<g clip-path="url(#floorclip)" fill="none">']
    for i in range(-vlines, vlines + 1):
        g.append(f'<line x1="{cx + i*14:.1f}" y1="{horizon}" x2="{cx + i*190:.1f}" y2="{bottom + 40}" stroke-width="1.2" '
                 f'stroke="url(#floorfade)"/>')
    # horizontal lines: y = horizon + depth * z0 / z, z sweeps far -> near
    steps = 24
    vals, ops = [], []
    for k in range(steps + 1):
        t = k / steps
        z = 12 * (1 - t) + 1 * t
        y = horizon + depth * 1.0 / z
        vals.append(f"0,{y - horizon:.1f}")
        ops.append(f"{min(1, 0.08 + 1.2 / z):.2f}")
    for i in range(lines):
        # a gradient stroke would vanish on a zero-height bbox, so fade via opacity instead
        g.append(
            f'<line x1="-50" y1="{horizon}" x2="{w + 50}" y2="{horizon}" stroke="{color}" stroke-width="1.6">'
            f'<animateTransform attributeName="transform" type="translate" values="{";".join(vals)}" '
            f'dur="{dur}s" begin="-{i*dur/lines:.3f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="stroke-opacity" values="{";".join(ops)}" '
            f'dur="{dur}s" begin="-{i*dur/lines:.3f}s" repeatCount="indefinite"/></line>'
        )
    g.append("</g>")
    return "<defs>" + "".join(parts) + "</defs>" + "".join(g)


# ---------- 3D ----------

def rot(p, ax=0.0, ay=0.0, az=0.0):
    x, y, z = p
    if ax:
        c, s = math.cos(ax), math.sin(ax)
        y, z = y * c - z * s, y * s + z * c
    if ay:
        c, s = math.cos(ay), math.sin(ay)
        x, z = x * c + z * s, -x * s + z * c
    if az:
        c, s = math.cos(az), math.sin(az)
        x, y = x * c - y * s, x * s + y * c
    return (x, y, z)


def project(p, f=600.0):
    x, y, z = p
    k = f / (f + z)
    return (x * k, y * k, k)


def icosahedron():
    t = (1 + 5 ** 0.5) / 2
    v = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
         (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    n = math.sqrt(1 + t * t)
    v = [(a / n, b / n, c / n) for a, b, c in v]
    edges = [(i, j) for i in range(12) for j in range(i + 1, 12)
             if abs(math.dist(v[i], v[j]) - 2 / n) < 1e-6]
    return v, edges


def cube():
    v = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    edges = [(i, j) for i in range(8) for j in range(i + 1, 8)
             if sum(a != b for a, b in zip(v[i], v[j])) == 1]
    return v, edges


def wire_frames(verts, edges, scale, frames, spin, f=600.0):
    """Return a list of path strings, one per frame, for a rotating wireframe."""
    out = []
    for k in range(frames + 1):
        t = k / frames
        ax, ay, az = (s * 2 * math.pi * t for s in spin)
        pts = [project(rot((a * scale, b * scale, c * scale), ax, ay, az), f) for a, b, c in verts]
        out.append(" ".join(f"M{pts[i][0]:.1f},{pts[i][1]:.1f}L{pts[j][0]:.1f},{pts[j][1]:.1f}" for i, j in edges))
    return out


def spinning_wire(cx, cy, verts, edges, scale, color, dur=12, frames=48, spin=(1, 1, 0), sw=1.4, extra=""):
    fr = wire_frames(verts, edges, scale, frames, spin)
    return (
        f'<g transform="translate({cx},{cy})"><path d="{fr[0]}" fill="none" stroke="{color}" '
        f'stroke-width="{sw}" stroke-linecap="round" {extra}>'
        f'<animate attributeName="d" values="{";".join(fr)}" dur="{dur}s" repeatCount="indefinite"/></path></g>'
    )


def extruded_text(x, y, text, size, layers=10, dx=1.0, dy=1.0, face="url(#faceGrad)",
                  side=SIDE, cls="disp", anchor="start", spacing=0, extra=""):
    """Fake-3D extrusion: stacked copies offset back-to-front."""
    t = escape(text)
    out = []
    for i in range(layers, 0, -1):
        mix = i / layers
        col = side[0] if mix > 0.5 else side[1]
        out.append(
            f'<text x="{x + i*dx:.1f}" y="{y + i*dy:.1f}" class="{cls}" font-size="{size}" fill="{col}" '
            f'text-anchor="{anchor}" letter-spacing="{spacing}">{t}</text>'
        )
    out.append(
        f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{face}" text-anchor="{anchor}" '
        f'letter-spacing="{spacing}" {extra}>{t}</text>'
    )
    return "".join(out)


def mono_width(text, size):
    return len(text) * size * 0.6


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  {os.path.relpath(path)}  {len(content.encode())/1024:.0f} KB")
