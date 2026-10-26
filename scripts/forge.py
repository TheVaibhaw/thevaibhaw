#!/usr/bin/env python3
"""Forge every static animated SVG used by the profile README.

    python3 scripts/forge.py          # writes into assets/

The contribution skyline is data-driven and built separately by scripts/skyline.py
(run by the GitHub Action), everything here is static content.
"""
import math
import os
import random
from xml.sax.saxutils import escape

from neon import (AMBER, BG0, BG1, CYAN, DIM, FACE_MID, HI, LIME, MAG, PANEL, RED, SKY, SLAB, TRACK,
                  TXT, VIO, cube, extruded_text, glow_defs,
                  hud_corners, icosahedron, mono_width, project, rot, spinning_wire, stars, svg,
                  synth_floor, tone, write)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")

FACE_GRAD = (
    '<linearGradient id="faceGrad" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox">'
    f'<stop offset="0" stop-color="{CYAN}"/><stop offset=".45" stop-color="{FACE_MID}"/>'
    f'<stop offset=".55" stop-color="{FACE_MID}"/><stop offset="1" stop-color="{MAG}"/>'
    '<animateTransform attributeName="gradientTransform" type="translate" values="-1 0;1 0;-1 0" '
    'dur="6s" repeatCount="indefinite"/></linearGradient>'
)


# --------------------------------------------------------------------------- hero

def typing_roles(x, y, phrases, size=21, slot=3.2):
    total = slot * len(phrases)
    cw = size * 0.6
    out = []
    for k, ph in enumerate(phrases):
        s0 = k * slot
        type_t = min(1.4, 0.045 * len(ph))
        times, widths = [0.0], [0.0]
        if s0 > 0:
            times.append(s0 / total)
            widths.append(0)
        for i in range(1, len(ph) + 1):
            times.append((s0 + type_t * i / len(ph)) / total)
            widths.append(i * cw)
        hold_end = s0 + slot - 0.45
        times.append(hold_end / total)
        widths.append(len(ph) * cw)
        times.append((hold_end + 0.25) / total)
        widths.append(0)
        times.append(1.0)
        widths.append(0)
        kt = ";".join(f"{t:.4f}" for t in times)
        wv = ";".join(f"{w:.1f}" for w in widths)
        xv = ";".join(f"{x + w + 2:.1f}" for w in widths)
        out.append(
            f'<clipPath id="tp{k}"><rect x="{x}" y="{y - size}" width="0" height="{size * 1.5}">'
            f'<animate attributeName="width" values="{wv}" keyTimes="{kt}" dur="{total}s" calcMode="discrete" '
            f'repeatCount="indefinite"/></rect></clipPath>'
            f'<text x="{x}" y="{y}" class="monob" font-size="{size}" fill="{LIME}" clip-path="url(#tp{k})">'
            f"{escape(ph)}</text>"
            f'<rect x="{x}" y="{y - size + 3}" width="{cw * .9:.1f}" height="{size + 2}" fill="{LIME}" opacity="0">'
            f'<animate attributeName="x" values="{xv}" keyTimes="{kt}" dur="{total}s" calcMode="discrete" '
            f'repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;{s0/total:.4f};'
            f'{(hold_end + .25)/total:.4f};{(hold_end + .26)/total:.4f};1" dur="{total}s" calcMode="discrete" '
            f'repeatCount="indefinite"/></rect>'
        )
    return "".join(out)


def mountains(w, horizon, seed=3):
    rnd = random.Random(seed)
    pts, x = [], -10
    while x < w + 20:
        pts.append((x, horizon - rnd.uniform(4, 46) * (0.4 + 0.6 * abs(math.sin(x / 170)))))
        x += rnd.uniform(18, 46)
    d = f"M-10,{horizon} " + " ".join(f"L{x:.0f},{y:.0f}" for x, y in pts) + f" L{w + 20},{horizon}Z"
    return (
        f'<path d="{d}" fill="{BG0}" stroke="{VIO}" stroke-width="1.2" stroke-opacity=".8"/>'
        f'<line x1="0" y1="{horizon}" x2="{w}" y2="{horizon}" stroke="{MAG}" stroke-width="2.5" filter="url(#glow)"/>'
    )


def hero():
    W, H = 1200, 700
    horizon = 548
    css = """
@keyframes popin{0%{transform:translateY(16px)}100%{transform:translateY(0)}}
@keyframes ghost{0%,100%{opacity:0}92%{opacity:0}93%{opacity:.8}95%{opacity:0}97%{opacity:.6}98%{opacity:0}}
.pop{animation:popin .7s cubic-bezier(.2,.9,.3,1.3) both}
.ghost{opacity:0;animation:ghost 5s infinite}
"""
    defs = (
        "<defs>" + glow_defs("glow", 4) + glow_defs("glowS", 2) + FACE_GRAD +
        f'<radialGradient id="sky" cx="50%" cy="78%" r="75%"><stop offset="0" stop-color="{SKY}"/>'
        f'<stop offset=".45" stop-color="{BG1}"/><stop offset="1" stop-color="{BG0}"/></radialGradient>'
        f'<linearGradient id="melt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG0}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{BG0}"/></linearGradient>'
        "</defs>"
    )
    b = [defs, f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', stars(W, horizon, 90)]
    b.append(synth_floor(W, horizon, H, MAG, lines=14, dur=2.6, cx=600))
    b.append(mountains(W, horizon))

    # top HUD
    b.append(f'<text x="30" y="40" class="monob" font-size="13" fill="{CYAN}">[ GITHUB PROFILE ]'
             f'<tspan fill="{DIM}">  ::  </tspan><tspan fill="{LIME}">OPEN TO NEW PROJECTS</tspan></text>')
    b.append(f'<g transform="translate(1170,40)"><circle cx="-74" cy="-5" r="5" fill="{RED}" class="blink"/>'
             f'<text x="0" y="0" class="monob" font-size="13" fill="{RED}" text-anchor="end">ONLINE</text></g>')
    b.append(f'<line x1="30" y1="52" x2="1170" y2="52" stroke="{CYAN}" stroke-opacity=".25"/>')

    # spinning polyhedra
    iv, ie = icosahedron()
    cv, ce = cube()
    for px, c1, c2, sgn in ((110, CYAN, MAG, -1), (1090, MAG, CYAN, 1)):
        b.append(spinning_wire(px, 200, iv, ie, 56, c1, dur=14, spin=(1, 2 * sgn, 0), sw=1.6, extra='filter="url(#glowS)"'))
        b.append(spinning_wire(px, 200, cv, ce, 22, c2, dur=9, spin=(-2, sgn, 1), sw=1.4))

    # name block, centered
    X = W / 2
    b.append(f'<g class="pop" style="animation-delay:.1s"><text x="{X}" y="104" class="monob" font-size="18" '
             f'fill="{AMBER}" text-anchor="middle">HELLO, I AM</text></g>')
    for i, (word, y) in enumerate((("VAIBHAW", 206), ("KUMAR", 302))):
        b.append(f'<g class="pop" style="animation-delay:{.3 + i*.2:.1f}s">')
        for col, cls in ((RED, "glA"), (CYAN, "glB")):
            b.append(f'<text x="{X}" y="{y}" class="disp" font-size="92" fill="{col}" opacity=".75" '
                     f'letter-spacing="4" text-anchor="middle"><tspan class="{cls}">{word}</tspan></text>')
        b.append(extruded_text(X, y, word, 92, layers=12, dx=1.1, dy=1.3, spacing=4, anchor="middle"))
        b.append("</g>")
    # glitch slices across the name
    for i, (yy, c, dl) in enumerate(((146, CYAN, 0), (192, MAG, 1.3), (262, LIME, 2.1), (290, CYAN, 3.4))):
        b.append(f'<rect class="ghost" style="animation-delay:{dl}s" x="230" y="{yy}" width="740" '
                 f'height="{3 + i % 2 * 4}" fill="{c}"/>')

    phrases = [
        "FULL STACK DEVELOPER",
        "WORDPRESS & WOOCOMMERCE EXPERT",
        "BIGCOMMERCE DEVELOPER",
        "PAYMENT GATEWAY INTEGRATION",
        "4 PLUGINS ON WORDPRESS.ORG",
        "REACT / NEXT.JS / NODE.JS / PHP",
    ]
    tx = X - (40 + mono_width(max(phrases, key=len), 25)) / 2
    b.append(f'<text x="{tx:.0f}" y="352" class="monob" font-size="25" fill="{MAG}">//</text>')
    b.append(typing_roles(round(tx + 40), 352, phrases, size=25))

    chips = [("4.6+", "YEARS EXP.", CYAN), ("4", "WP PLUGINS", LIME), ("15+", "THEMES", MAG),
             ("10+", "STORES", AMBER), ("8+", "PAYMENTS", VIO)]
    cx0 = X - (len(chips) * 140 - 10) / 2
    for i, (num, lab, c) in enumerate(chips):
        x0 = cx0 + i * 140
        b.append(
            f'<g class="pop" style="animation-delay:{1 + i*.15:.2f}s"><g transform="translate({x0:.0f},384)">'
            f'<g class="float" style="animation-delay:{i*.5:.1f}s;animation-duration:4s">'
            f'<path d="M0,0H118L130,12V66H12L0,54Z" fill="{BG0}" fill-opacity=".8" stroke="{c}" stroke-width="1.5"/>'
            f'<path d="M0,0H118L130,12V66H12L0,54Z" fill="none" stroke="{c}" stroke-width="3" '
            f'stroke-dasharray="40 400" filter="url(#glowS)">'
            f'<animate attributeName="stroke-dashoffset" values="0;-440" dur="{2.4 + i*.3:.1f}s" '
            f'repeatCount="indefinite"/></path>'
            f'<text x="65" y="36" class="disp" font-size="28" fill="{c}" text-anchor="middle">{num}</text>'
            f'<text x="65" y="56" class="monob" font-size="11.5" fill="{TXT}" text-anchor="middle">'
            f'{lab}</text></g></g></g>'
        )

    b.append(f'<rect y="{horizon + 40}" width="{W}" height="{H - horizon - 40}" fill="url(#melt)" pointer-events="none"/>')
    return svg(W, H, "".join(b), css, "Vaibhaw Kumar — Full Stack Developer: WordPress, WooCommerce, BigCommerce, React, Node")


# --------------------------------------------------------------------------- section headers

def section(num, title, comment, color):
    W, H = 1200, 120
    css = """
@keyframes sweep{0%{transform:translateX(-300px)}100%{transform:translateX(1300px)}}
.sweep{animation:sweep 2.8s cubic-bezier(.6,0,.4,1) infinite}
"""
    defs = "<defs>" + glow_defs("glow", 3) + FACE_GRAD + (
        f'<linearGradient id="laser" x1="0" x2="1"><stop offset="0" stop-color="{color}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{HI}"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient>'
    ) + "</defs>"
    b = [defs, f'<rect width="{W}" height="{H}" rx="10" fill="{BG0}"/>']
    b.append(f'<text x="40" y="34" class="monob" font-size="14" fill="{color}">[ 0x{num:02X} ]'
             f'<tspan fill="{DIM}"> ── SECTOR_{num:02d} ── </tspan><tspan class="blink" fill="{color}">█</tspan></text>')
    b.append(f'<text x="1160" y="34" class="mono" font-size="14" fill="{DIM}" text-anchor="end">{escape(comment)}</text>')
    b.append(f'<g class="glA"><text x="40" y="92" class="disp" font-size="50" fill="{color}" opacity=".55" '
             f'letter-spacing="4">{escape(title)}</text></g>')
    b.append(extruded_text(40, 92, title, 50, layers=8, dx=1, dy=1.2, spacing=4))
    b.append(f'<line x1="40" y1="108" x2="1160" y2="108" stroke="{color}" stroke-opacity=".35" stroke-width="2"/>')
    b.append(f'<rect class="sweep" x="0" y="105" width="300" height="6" fill="url(#laser)" filter="url(#glow)"/>')
    for i in range(14):
        b.append(f'<rect x="{1160 - i*12}" y="{70 + (i % 3) * 4}" width="7" height="14" fill="{color}" '
                 f'style="animation:pulse {0.6 + (i*37 % 9)/10:.1f}s {i*0.11:.2f}s infinite"/>')
    return svg(W, H, "".join(b), css, f"Section {num}: {title}")


# --------------------------------------------------------------------------- whoami terminal

def whoami():
    W, H = 1200, 470
    css = """
@keyframes reveal{0%{opacity:0;transform:translateX(-12px)}100%{opacity:1;transform:translateX(0)}}
.ln{opacity:0;animation:reveal .35s ease-out forwards}
"""
    defs = "<defs>" + glow_defs("glow", 3) + "</defs>"
    b = [defs, f'<rect width="{W}" height="{H}" rx="14" fill="{BG0}"/>', stars(W, H, 40, seed=11)]

    # 3D slab terminal
    tx, ty, tw, th = 30, 26, 760, 410
    b.append('<g class="float">')
    for i in range(10, 0, -1):
        b.append(f'<rect x="{tx + i*1.6:.1f}" y="{ty + i*1.6:.1f}" width="{tw}" height="{th}" rx="12" '
                 f'fill="{SLAB[0] if i > 5 else SLAB[1]}"/>')
    b.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="12" fill="{BG1}" stroke="{CYAN}" stroke-width="1.5"/>')
    b.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="34" rx="12" fill="{PANEL}"/>')
    for i, c in enumerate((RED, AMBER, LIME)):
        b.append(f'<circle cx="{tx + 22 + i*20}" cy="{ty + 17}" r="6" fill="{c}"/>')
    b.append(f'<text x="{tx + tw/2}" y="{ty + 22}" class="mono" font-size="12" fill="{DIM}" text-anchor="middle">'
             f'vaibhaw@mohali: ~/profile — zsh — 120x40</text>')

    prompt = f'<tspan fill="{LIME}">root@vaibhaw</tspan><tspan fill="{TXT}">:</tspan><tspan fill="{CYAN}">~</tspan><tspan fill="{TXT}">$ </tspan>'
    rows = [
        ("ORIGIN", "Born & raised in Bihar → building from Mohali, Punjab"),
        ("ROLE", "Full Stack Developer @ Tech Prastish Software Solutions"),
        ("XP", "4.6+ years  //  B.Tech CSE"),
        ("MAIN", "WordPress · WooCommerce · PHP · BigCommerce"),
        ("ALSO", "React · Next.js · TypeScript · Node.js · Laravel"),
        ("SHIPPED", "4 WP.org plugins · 15+ themes · 10+ BC stores"),
        ("SITE", "vaibhawkumar.in"),
        ("MOTTO", '"clean code, fast sites — sab smooth chalega!"'),
    ]
    y = ty + 68
    b.append(f'<text x="{tx + 24}" y="{y}" class="monob" font-size="15">{prompt}'
             f'<tspan fill="{AMBER}">whoami --verbose --flex</tspan></text>')
    for i, (k, v) in enumerate(rows):
        y += 32
        b.append(
            f'<g class="ln" style="animation-delay:{.5 + i*.28:.2f}s"><text x="{tx + 24}" y="{y}" class="mono" font-size="15">'
            f'<tspan fill="{MAG}">▸ </tspan><tspan fill="{CYAN}" class="monob">{k}</tspan>'
            f'<tspan x="{tx + 140}" fill="{TXT}">{escape(v)}</tspan></text></g>'
        )
    y += 34
    b.append(f'<g class="ln" style="animation-delay:{.5 + len(rows)*.28:.2f}s"><text x="{tx + 24}" y="{y}" '
             f'class="monob" font-size="15">{prompt}<tspan fill="{LIME}" class="blink">█</tspan></text></g>')
    b.append("</g>")

    # power levels
    px = 830
    b.append(hud_corners(px - 10, 26, 350, 410, MAG, 16, 2))
    b.append(f'<text x="{px + 6}" y="62" class="disp" font-size="20" fill="{MAG}" letter-spacing="2">POWER LEVELS</text>')
    b.append(f'<text x="{px + 6}" y="82" class="mono" font-size="11" fill="{DIM}">// self-reported. emotionally accurate.</text>')
    skills = [("WORDPRESS", 96, tone("#4fc3ff")), ("WOOCOMMERCE", 94, tone("#c084fc")), ("PHP / MYSQL", 92, tone("#8892ff")),
              ("BIGCOMMERCE", 90, tone("#ffffff")), ("PAYMENTS / APIS", 88, LIME), ("JS / REACT", 80, tone("#61dafb")),
              ("NODE / LARAVEL", 72, tone("#7ee787"))]
    bw = 300
    for i, (name, pct, c) in enumerate(skills):
        yy = 112 + i * 44
        d = 1.2 + i * .18
        b.append(f'<text x="{px + 6}" y="{yy}" class="monob" font-size="12" fill="{TXT}">{name}</text>')
        b.append(f'<rect x="{px + 6}" y="{yy + 8}" width="{bw}" height="12" fill="{TRACK}" stroke="{c}" stroke-opacity=".3"/>')
        b.append(f'<rect x="{px + 6}" y="{yy + 8}" width="0" height="12" fill="{c}" filter="url(#glow)">'
                 f'<animate attributeName="width" from="0" to="{bw*pct/100:.0f}" begin="{d:.2f}s" dur="1.1s" '
                 f'fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/></rect>')
        # segment gaps for a meter look
        b.append(f'<path d="{" ".join(f"M{px + 6 + s*12},{yy + 8}v12" for s in range(1, bw // 12))}" '
                 f'stroke="{BG0}" stroke-width="3"/>')
    b.append(f'<text x="{px + 6}" y="{H - 44}" class="disp" font-size="17" fill="{LIME}">'
             f'<tspan class="flicker">OVERALL: BEAST MODE</tspan></text>')
    return svg(W, H, "".join(b), css, "whoami — Vaibhaw Kumar")


# --------------------------------------------------------------------------- arsenal orbit

def ring_node(label, color, R, phase, tilt, roll, dur, frames, cx, cy, direction=1):
    tr, op, sc = [], [], []
    for k in range(frames + 1):
        a = phase + direction * 2 * math.pi * k / frames
        p = rot((R * math.cos(a), 0, R * math.sin(a)), tilt, 0, roll)
        x, y, s = project(p, 2200)
        depth = (p[2] + R) / (2 * R)  # 0 front .. 1 back
        tr.append(f"{cx + x:.1f},{cy + y:.1f}")
        sc.append(f"{s * (1.1 - .35*depth):.3f}")
        op.append(f"{1 - .7*depth:.2f}")
    w = mono_width(label, 13) + 30
    return (
        f'<g><animateTransform attributeName="transform" type="translate" values="{";".join(tr)}" dur="{dur}s" '
        f'repeatCount="indefinite"/><animate attributeName="opacity" values="{";".join(op)}" dur="{dur}s" '
        f'repeatCount="indefinite"/><g><animateTransform attributeName="transform" type="scale" '
        f'values="{";".join(sc)}" dur="{dur}s" repeatCount="indefinite"/>'
        f'<rect x="{-w/2:.1f}" y="-15" width="{w:.1f}" height="30" rx="15" fill="{BG1}" stroke="{color}" stroke-width="1.8"/>'
        f'<circle cx="{-w/2 + 14:.1f}" cy="0" r="4" fill="{color}"/>'
        f'<text x="{8}" y="5" class="monob" font-size="13" fill="{color}" text-anchor="middle">{escape(label)}</text>'
        f"</g></g>"
    )


def ring_path(R, tilt, roll, cx, cy, n=90):
    pts = []
    for k in range(n + 1):
        a = 2 * math.pi * k / n
        x, y, _ = project(rot((R * math.cos(a), 0, R * math.sin(a)), tilt, 0, roll), 2200)
        pts.append(f"{cx + x:.1f},{cy + y:.1f}")
    return "M" + " L".join(pts)


def globe(cx, cy, R, frames=40, dur=16, tilt=0.35):
    out = []
    # parallels are invariant under spin, only meridians move
    for lat in (-60, -30, 0, 30, 60):
        phi = math.radians(lat)
        pts = []
        for k in range(49):
            a = 2 * math.pi * k / 48
            p = rot((R * math.cos(phi) * math.cos(a), -R * math.sin(phi), R * math.cos(phi) * math.sin(a)), tilt)
            x, y, _ = project(p, 900)
            pts.append(f"{cx + x:.1f},{cy + y:.1f}")
        out.append(f'<path d="M{" L".join(pts)}" fill="none" stroke="{VIO}" stroke-width="1.2" stroke-opacity=".7"/>')
    for m in range(6):
        seq = []
        for k in range(frames + 1):
            lon = math.pi * m / 6 + 2 * math.pi * k / frames
            pts = []
            for j in range(29):
                phi = -math.pi / 2 + math.pi * j / 28
                p = (R * math.cos(phi) * math.cos(lon), -R * math.sin(phi), R * math.cos(phi) * math.sin(lon))
                x, y, _ = project(rot(p, tilt), 900)
                pts.append(f"{cx + x:.1f},{cy + y:.1f}")
            seq.append("M" + " L".join(pts))
        out.append(f'<path d="{seq[0]}" fill="none" stroke="{CYAN}" stroke-width="1.3" stroke-opacity=".85">'
                   f'<animate attributeName="d" values="{";".join(seq)}" dur="{dur}s" repeatCount="indefinite"/></path>')
    return "".join(out)


def arsenal():
    W, H = 1200, 600
    cx, cy = 600, 300
    defs = "<defs>" + glow_defs("glow", 6) + glow_defs("glowS", 2) + (
        f'<radialGradient id="core" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{MAG}" stop-opacity=".16"/>'
        f'<stop offset=".5" stop-color="{VIO}" stop-opacity=".06"/><stop offset="1" stop-color="{BG0}" stop-opacity="0"/>'
        "</radialGradient>"
    ) + "</defs>"
    b = [defs, f'<rect width="{W}" height="{H}" rx="14" fill="{BG0}"/>', stars(W, H, 80, seed=21)]
    b.append(f'<circle cx="{cx}" cy="{cy}" r="230" fill="url(#core)"><animate attributeName="r" values="210;250;210" '
             f'dur="4s" repeatCount="indefinite"/></circle>')

    inner = [("WORDPRESS", tone("#4fc3ff")), ("WOOCOMMERCE", tone("#c084fc")), ("PHP", tone("#8892ff")), ("BIGCOMMERCE", tone("#ffffff")),
             ("MYSQL", tone("#ffa94d")), ("REST API", LIME)]
    outer = [(lab, tone(col)) for lab, col in (
        ("REACT", "#61dafb"), ("NEXT.JS", "#ffffff"), ("TYPESCRIPT", "#5a9cff"), ("NODE.JS", "#7ee787"),
        ("LARAVEL", "#ff5a4f"), ("MONGODB", "#5fd068"), ("STRIPE", "#8a84ff"), ("OPENAI", "#3ee0b0"),
        ("GRAPHQL", "#ff4fc3"), ("JAVASCRIPT", "#f7df1e"))]
    rings = [(inner, 230, 0.3, 0.16, 22, 1, CYAN), (outer, 450, 0.36, -0.1, 34, -1, MAG)]
    for items, R, tilt, roll, dur, dirn, c in rings:
        b.append(f'<path d="{ring_path(R, tilt, roll, cx, cy)}" fill="none" stroke="{c}" stroke-opacity=".45" '
                 f'stroke-width="1.5" stroke-dasharray="6 8"><animate attributeName="stroke-dashoffset" '
                 f'values="0;{-140*dirn}" dur="3s" repeatCount="indefinite"/></path>')
    b.append(globe(cx, cy, 120))
    iv, ie = icosahedron()
    b.append(spinning_wire(cx, cy, iv, ie, 46, MAG, dur=8, spin=(2, -1, 1), sw=2, extra='filter="url(#glowS)"'))
    b.append(f'<text x="{cx}" y="{cy + 6}" class="disp" font-size="16" fill="{HI}" text-anchor="middle" '
             f'filter="url(#glow)">CORE</text>')
    for items, R, tilt, roll, dur, dirn, c in rings:
        for i, (lab, col) in enumerate(items):
            b.append(ring_node(lab, col, R, 2 * math.pi * i / len(items), tilt, roll, dur, 72, cx, cy, dirn))

    b.append(hud_corners(16, 16, W - 32, H - 32, CYAN, 26, 2))
    b.append(f'<text x="40" y="52" class="disp" font-size="18" fill="{CYAN}" letter-spacing="2">ARSENAL.MAP</text>')
    b.append(f'<text x="40" y="74" class="mono" font-size="12" fill="{DIM}">'
             f'<tspan fill="{CYAN}">●</tspan> ORBIT-1  CORE STACK   '
             f'<tspan fill="{MAG}">●</tspan> ORBIT-2  EXTENDED STACK</text>')
    b.append(f'<text x="1160" y="52" class="monob" font-size="12" fill="{LIME}" text-anchor="end">'
             f'<tspan class="blink">●</tspan> 16 SYSTEMS ONLINE</text>')
    b.append(f'<text x="40" y="{H - 34}" class="mono" font-size="12" fill="{DIM}">'
             f'// payments: Stripe · PayPal · Binance Pay · Twilio   // ai: OpenAI · Gemini · Grok</text>')
    b.append(f'<text x="1160" y="{H - 34}" class="mono" font-size="12" fill="{DIM}" text-anchor="end">'
             f'security · core web vitals · caching</text>')
    return svg(W, H, "".join(b), "", "Tech stack orbit: WordPress, WooCommerce, PHP, BigCommerce and more")


# --------------------------------------------------------------------------- buttons

BUTTONS = [
    ("linkedin", "LINKEDIN", "/in/itsvaibhaw", tone("#3b9cff")),
    ("portfolio", "PORTFOLIO", "vaibhawkumar.in", CYAN),
    ("wporg", "WORDPRESS.ORG", "profiles/thevaibhaw", LIME),
    ("email", "EMAIL", "imvaibhaw@gmail.com", MAG),
    ("instagram", "INSTAGRAM", "@itsvaibhaw", VIO),
]


def button(label, sub, c, i):
    W, H = 380, 92
    css = """
@keyframes shine{0%{transform:translateX(-150px) skewX(-25deg)}55%,100%{transform:translateX(520px) skewX(-25deg)}}
.shine{animation:shine 3.4s ease-in-out infinite}
"""
    shape = f"M14,6H{W-6}V{H-22}L{W-22},{H-6}H6V22Z"
    perim = 2 * (W + H) - 40
    b = ["<defs>" + glow_defs("glow", 3) + f'<clipPath id="bc"><path d="{shape}"/></clipPath>' +
         '<linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
         '<stop offset=".5" stop-color="#fff" stop-opacity=".2"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
         "</linearGradient></defs>"]
    b.append(f'<path d="{shape}" fill="{BG1}" stroke="{c}" stroke-opacity=".4" stroke-width="1.5"/>')
    b.append(f'<path d="{shape}" fill="none" stroke="{c}" stroke-width="3" stroke-dasharray="90 {perim}" '
             f'filter="url(#glow)"><animate attributeName="stroke-dashoffset" values="0;{-(perim + 90)}" '
             f'dur="{2.6 + i*.25:.2f}s" repeatCount="indefinite"/></path>')
    b.append(f'<g clip-path="url(#bc)"><rect class="shine" style="animation-delay:{i*.4:.1f}s" x="0" y="0" '
             f'width="90" height="{H}" fill="url(#sh)"/></g>')
    b.append(f'<rect x="22" y="26" width="6" height="40" fill="{c}" filter="url(#glow)"/>')
    b.append(f'<text x="44" y="50" class="disp" font-size="20" fill="{c}" letter-spacing="2">{label}</text>')
    b.append(f'<text x="44" y="70" class="mono" font-size="12" fill="{TXT}" opacity=".8">{escape(sub)}</text>')
    b.append(f'<text x="{W - 30}" y="56" class="monob" font-size="22" fill="{c}" text-anchor="end">'
             f'<tspan>▸</tspan><animate attributeName="x" values="{W-34};{W-24};{W-34}" dur="1.2s" '
             f'repeatCount="indefinite"/></text>')
    return svg(W, H, "".join(b), css, f"{label.title()} — {sub}")


def main():
    print("forging assets/ ...")
    write(os.path.join(OUT, "hero.svg"), hero())
    for n, (slug, title, comment, c) in enumerate([
        ("whoami", "WHOAMI", "// the human behind the commits", CYAN),
        ("arsenal", "ARSENAL", "// weapons of mass deployment", MAG),
        ("telemetry", "TELEMETRY", "// numbers don't lie (much)", AMBER),
        ("uplink", "UPLINK", "// open a channel", VIO),
    ], start=1):
        write(os.path.join(OUT, f"sec-{slug}.svg"), section(n, title, comment, c))
    write(os.path.join(OUT, "whoami.svg"), whoami())
    write(os.path.join(OUT, "arsenal.svg"), arsenal())
    for i, (slug, label, sub, c) in enumerate(BUTTONS):
        write(os.path.join(OUT, f"btn-{slug}.svg"), button(label, sub, c, i))


if __name__ == "__main__":
    main()
