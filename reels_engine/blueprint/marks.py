"""Marks of the blueprint style: what shows movement and calls attention on top of a drawing. Flows along a path,
lines that draw themselves, curved and force arrows, a zoom lens, data-type stamps (fact / estimate / hypothetical),
step badges, critical-point alerts, waves, a scan reveal, a grid transition, captions in the style and a brand block.

    flow_path(img, [(100, 900), (500, 900), (500, 1200)], c.t)                    # water running through
    path_arrow(img, [(200, 700), (420, 620), (640, 700)], k=tw(c.lt, 0, .8, 0, 1))
    force_arrow(img, 540, 600, 540, 820, "PESO")
    fact_tag(img, "estimate", 60, 1240)
"""
import math

from PIL import Image, ImageDraw
from ..config import current as _current
from . import (Plate, text, font, mix, trace, smooth, bounds, W, H, SS, NEON, WHITE, CYAN, GRAY, DIM, ACCENT, RISK,
               PANEL, BG)

_cfg = _current()

# ---------- lines and flows ----------
def trace_line(img, pts, k=1.0, color=WHITE, w=3, tip=CYAN, curved=False, glow=NEON):
    """Line that draws itself as k goes from 0 to 1, with a glowing dot at the pen's tip."""
    path = trace(smooth(pts) if curved else pts, k)
    if len(path) < 2: return
    with Plate(img, bounds(path, w + 12)) as p:
        p.line(path, color, w)
    if tip and k < 1:
        with Plate(img, bounds(path[-1:], w + 6), glow=glow) as p:
            p.circle(*path[-1], w + 3, fill=tip)

def flow_path(img, pts, t, color=CYAN, w=5, speed=80, kind="dash", k=1.0, curved=False, glow=NEON):
    """Something moving along a path (water, current, air, parcels): glowing dashes or dots that travel at 'speed'
    px/s. Color by system: CYAN water, VOLT electricity, LIME air or gas, MAGENTA data."""
    path = trace(smooth(pts) if curved else pts, k)
    if len(path) < 2: return
    with Plate(img, bounds(path, w + 10), glow=glow) as p:
        if kind == "dash": p.dashed(path, color, w, 16, 14, phase=-t * speed)
        else:
            total = sum(math.dist(a, b) for a, b in zip(path, path[1:])); gap = w * 5
            s = (t * speed) % gap
            while s < total:
                (x, y), = trace(path, s / total)[-1:]
                p.circle(x, y, w * .8, fill=color); s += gap

def _head(p, tip, back, size, color):
    ang = math.atan2(tip[1] - back[1], tip[0] - back[0])
    a = (tip[0] - size * math.cos(ang - .45), tip[1] - size * math.sin(ang - .45))
    b = (tip[0] - size * math.cos(ang + .45), tip[1] - size * math.sin(ang + .45))
    p.poly([tip, a, b], fill=color)

def path_arrow(img, pts, k=1.0, color=CYAN, w=5, head=26, curved=True, dashed=False, glow=NEON):
    """Curved route arrow through the points, drawn as k goes from 0 to 1 (direction or order of things)."""
    path = trace(smooth(pts) if curved and len(pts) > 2 else pts, k)
    if len(path) < 2: return
    with Plate(img, bounds(path, head + w + 6), glow=glow) as p:
        end = path[-1]; back = trace(path[::-1], min(1.0, head * .6 / max(1, sum(math.dist(a, b) for a, b in zip(path, path[1:])))))[-1]
        body = path[:-1] + [((end[0] + back[0]) / 2, (end[1] + back[1]) / 2)]
        if dashed: p.dashed(body, color, w, 18, 12)
        else: p.line(body, color, w)
        _head(p, end, back, head, color)

def force_arrow(img, x0, y0, x1, y1, label="", color=ACCENT, w=14, appear=1.0, size=26, glow=NEON):
    """Thick force arrow from (x0, y0) to (x1, y1) (push, weight, wind, pressure) with its name at the tail."""
    x1, y1 = x0 + (x1 - x0) * appear, y0 + (y1 - y0) * appear
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 4: return
    ux, uy = (x1 - x0) / L, (y1 - y0) / L; hl = min(L * .45, w * 2.6)
    with Plate(img, bounds([(x0, y0), (x1, y1)], w * 2 + 4), glow=glow) as p:
        p.line([(x0, y0), (x1 - ux * hl * .8, y1 - uy * hl * .8)], color, w)
        nx, ny = -uy, ux
        p.poly([(x1, y1), (x1 - ux * hl + nx * w * 1.3, y1 - uy * hl + ny * w * 1.3),
                (x1 - ux * hl - nx * w * 1.3, y1 - uy * hl - ny * w * 1.3)], fill=color)
    if label and appear >= 1:
        text(img, label.upper(), x0 - ux * 18, y0 - uy * 18, size, color,
             anchor=("r" if ux > .3 else "l" if ux < -.3 else "m") + ("b" if uy > .3 else "t" if uy < -.3 else "m"))

# ---------- attention ----------
def zoom_lens(img, sx, sy, sr, cx, cy, r, color=CYAN, label=""):
    """Zoom to a detail: the circle (sx, sy, sr) of the picture shown enlarged in a lens at (cx, cy, r)."""
    src = img.crop((int(sx - sr), int(sy - sr), int(sx + sr), int(sy + sr))).resize((int(2 * r), int(2 * r)), Image.LANCZOS)
    big = Image.new("L", (int(2 * r) * SS, int(2 * r) * SS), 0)
    ImageDraw.Draw(big).ellipse([0, 0, big.width - 1, big.height - 1], fill=255)
    img.paste(src, (int(cx - r), int(cy - r)), big.resize(src.size, Image.LANCZOS))
    d = math.hypot(cx - sx, cy - sy) or 1; ux, uy = (cx - sx) / d, (cy - sy) / d; nx, ny = -uy, ux
    with Plate(img, bounds([(sx, sy), (cx, cy)], r + 30)) as p:
        p.circle(sx, sy, sr, color=color, w=3)
        for s in (1, -1):                                          # the two lines joining the circles
            p.line([(sx + nx * sr * s, sy + ny * sr * s), (cx + nx * r * s, cy + ny * r * s)], mix(color, PANEL, .5), 2)
        p.circle(cx, cy, r, color=color, w=4)
    if label: text(img, label.upper(), cx, cy + r + 30, 24, color, tracking=.25, anchor="mm")

FACT_LABELS = {"fact": "DATO", "estimate": "ESTIMACIÓN", "hypothetical": "HIPOTÉTICO"}

def fact_tag(img, kind, x, y, size=22, labels=None, anchor="l"):
    """Stamp that says what kind of figure is on screen: fact (white), estimate (amber) or hypothetical (dashed grey)."""
    s = (labels or FACT_LABELS)[kind]
    color = {"fact": WHITE, "estimate": ACCENT, "hypothetical": GRAY}[kind]
    f = font(size); tw_ = f.getlength(s) + size * .3 * (len(s) - 1); pad = size * .6
    x0 = x - {"l": 0, "m": (tw_ + 2 * pad) / 2, "r": tw_ + 2 * pad}[anchor]; y0, y1 = y - size * .9, y + size * .9
    with Plate(img, (x0 - 4, y0 - 4, x0 + tw_ + 2 * pad + 4, y1 + 4)) as p:
        pts = [(x0, y0), (x0 + tw_ + 2 * pad, y0), (x0 + tw_ + 2 * pad, y1), (x0, y1), (x0, y0)]
        p.rect(x0, y0, x0 + tw_ + 2 * pad, y1, fill=PANEL)
        if kind == "hypothetical": p.dashed(pts, color, 2, 8, 6)
        else: p.line(pts, color, 2)
    return text(img, s, x0 + pad, y, size, color, tracking=.3, anchor="lm")

def step_badge(img, n, x, y, r=30, state="on", glow=NEON):
    """Step number in a circle: 'active' (filled cyan), 'on' (cyan ring), 'done' (white ring) or 'off' (dim)."""
    ring = {"active": CYAN, "on": CYAN, "done": WHITE, "off": DIM}[state]
    with Plate(img, (x - r - 4, y - r - 4, x + r + 4, y + r + 4), glow=glow if state == "active" else 0) as p:
        p.circle(x, y, r, fill=CYAN if state == "active" else PANEL, color=ring, w=3)
    text(img, f"{n:02d}" if isinstance(n, int) else str(n), x, y, int(r * .85),
         PANEL if state == "active" else (WHITE if state != "off" else DIM), anchor="mm")

def alert(img, x, y, t, r=26, label="", color=RISK, glow=NEON):
    """Critical point: a glowing warning triangle with red rings pulsing out of it."""
    with Plate(img, (x - r * 3.2, y - r * 3.2, x + r * 3.2, y + r * 3.2), glow=glow) as p:
        for k in range(2):
            u = (t * .9 + k * .5) % 1
            p.circle(x, y, r * (1.1 + 1.9 * u), color=mix(color, PANEL, u), w=3)
        p.poly([(x, y - r), (x + r * 1.05, y + r * .75), (x - r * 1.05, y + r * .75)], fill=color)
    text(img, "!", x, y + r * .18, int(r * 1.1), PANEL, anchor="mm")
    if label: text(img, label.upper(), x + r * 1.6, y, 24, color, anchor="lm")

def wave_lines(img, x, y, t, kind="rings", size=160, color=CYAN, n=3, speed=1.0, amp=14, glow=NEON):
    """Invisible forces made visible: rings opening from (x, y) (sound, impact, quake) or a sine across 'size' px
    (vibration, sway)."""
    with Plate(img, (x - size - 6, y - size - 6, x + size + 6, y + size + 6), glow=glow) as p:
        if kind == "rings":
            for k in range(n):
                u = (t * speed + k / n) % 1
                p.circle(x, y, 8 + (size - 8) * u, color=mix(color, PANEL, u), w=3)
        else:
            for k in range(n):
                pts = [(x - size + i * 6, y + (k - (n - 1) / 2) * amp * 2.4
                        + amp * math.sin(i * 6 / 46 * 6.283 - t * 6 * speed + k)) for i in range(int(2 * size / 6) + 1)]
                p.line(pts, mix(color, PANEL, k / (n + 1)), 3)

# ---------- reveals and transitions ----------
def scan_reveal(img, before, box, k, color=CYAN, glow=NEON):
    """Scan from the top of the box: above the line the picture as it is now, below it 'before' (an image of the
    same size); a cyan line marks the scan."""
    x0, y0, x1, y1 = [int(v) for v in box]
    cut = int(y0 + (y1 - y0) * max(0.0, min(1.0, k)))
    if cut < y1: img.paste(before.crop((x0, cut, x1, y1)), (x0, cut))
    if 0 < k < 1:
        with Plate(img, (x0 - 2, cut - 8, x1 + 2, cut + 8), glow=glow) as p:
            p.line([(x0, cut), (x1, cut)], color, 3)

def grid_wipe(img, k, cell=120, color=CYAN):
    """Transition of the style: grid cells cover the frame diagonally (k from 0 to 1) and their cyan edges flash.
    Use k from 1 to 0 at the start of a scene and 0 to 1 at its end."""
    if k <= 0: return
    cols, rows = W // cell + 1, H // cell + 1
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for i in range(cols):
        for j in range(rows):
            u = max(0.0, min(1.0, k * 2.2 - (i + j) / (cols + rows) * 1.2))
            if u <= 0: continue
            s = cell * u / 2; cx, cy = i * cell + cell / 2, j * cell + cell / 2
            d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=BG + (255,), outline=color + (min(255, int(255 * (1 - u) + 60)),) if u < 1 else None)
    img.paste(layer, (0, 0), layer)

# ---------- captions and brand ----------
def plan_caption(img, s, lt, y=None, size=None, maxw=940, stagger=.11, band=True, color=WHITE, highlight=CYAN):
    """Captions in the style: monospaced words appear one by one on a dark band with corner marks, *words* in cyan.
    For specs with CAPTIONS = False that draw them in the scene: plan_caption(img, c.cap, c.cap_lt)."""
    if not s: return
    y, size = y or _cfg.cap_y, size or 58
    f = font(size); words, hl = [], False
    for w in s.split():
        parts = []
        for j, part in enumerate(w.split("*")):
            if j: hl = not hl
            if part: parts.append((part, hl))
        words.append(parts)
    sp = f.getlength(" "); lines, cur, cw = [], [], 0
    for parts in words:
        ww = sum(f.getlength(a) for a, _ in parts)
        if cur and cw + sp + ww > maxw: lines.append((cur, cw)); cur, cw = [], 0
        cw += (sp if cur else 0) + ww; cur.append((parts, ww))
    if cur: lines.append((cur, cw))
    lh = size * 1.3; top = y - lh * len(lines) / 2
    if band:
        bw = max(lw for _, lw in lines) + size * 1.2
        x0, x1, y0, y1 = W / 2 - bw / 2, W / 2 + bw / 2, top - size * .35, top + lh * len(lines) + size * .25
        layer = Image.new("RGBA", (int(x1 - x0), int(y1 - y0)), PANEL + (205,))
        img.paste(layer, (int(x0), int(y0)), layer)
        with Plate(img, (x0 - 4, y0 - 4, x1 + 4, y1 + 4)) as p:
            for cx, cy, dx, dy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
                p.line([(cx + dx * 22, cy), (cx, cy), (cx, cy + dy * 22)], CYAN, 3)
    k = 0
    for li, (ln, lw) in enumerate(lines):
        x = W / 2 - lw / 2
        for parts, ww in ln:
            if lt >= k * stagger:
                px = x
                for a, h in parts:
                    text(img, a, px, top + li * lh + lh / 2, size, highlight if h else color, anchor="lm")
                    px += f.getlength(a)
            k += 1; x += ww + sp

def brand_mark(img, name, slogan="", x=None, y=None, size=64, appear=1.0, t=0.0):
    """Channel brand block: the x-ray lens symbol, the channel name and its slogan (texts come from the channel)."""
    x = W / 2 if x is None else x; y = H / 2 if y is None else y
    r = size * 1.1
    with Plate(img, (x - r - 26, y - r * 2.6 - 26, x + r + 26, y - r * .6 + 26), glow=NEON) as p:
        cy = y - r * 1.6
        p.circle(x, cy, r * appear, color=CYAN, w=4)
        p.circle(x, cy, r * .42 * appear, fill=CYAN)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p.line([(x + dx * (r - 12) * appear, cy + dy * (r - 12) * appear), (x + dx * (r + 18) * appear, cy + dy * (r + 18) * appear)], CYAN, 4)
    if appear >= 1:
        text(img, name.upper(), x, y, size, WHITE, tracking=.12, anchor="mt")
        if slogan: text(img, slogan, x, y + size * 1.45, int(size * .42), CYAN, bold=False, anchor="mt")
