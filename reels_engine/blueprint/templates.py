"""Scene templates of the blueprint style (the cross-section lives in `section`): size comparison, step by step,
question and answer, failure and consequences, exploded view and schematic map. Each one fills a box and animates
with k (0 to 1) or with the active step, so an episode is built from two or three of them.

    size_compare(img, ["person", "bus", ("plane", "AVIÓN")], (60, 600, 1020, 1300), k=tw(c.lt, 0, 2, 0, 1))
    steps(img, [("CAPTAR", "río o pozo"), ("LIMPIAR", "planta"), ("BOMBEAR", "al tanque")], (60, 600, 1020, 1300), active=1, t=c.t)
    failure_chain(img, ["BOMBA", "TANQUE", "PRESIÓN", "LLAVES"], (60, 600, 1020, 1300), fail=0, k=tw(c.lt, .5, 2, 0, 1), t=c.t)
"""
import math
import random

from . import (Plate, text, font, mix, appear, callout, dimension, NEON, WHITE, CYAN, GRAY, DIM, ACCENT, RISK, PANEL,
               SERIES)
from .marks import flow_path, path_arrow, alert, step_badge, trace_line
from .scale import DRAW, SIZES, LABELS

# ---------- size comparison ----------
def size_compare(img, items, box, k=1.0, unit="m", size=24, heights=True):
    """Things side by side on one ground line, all at the same scale: items are scale names ("person", "bus",
    "plane", "eiffel", "car", "field", "pool"), (name, label) or (draw, label, width_m, height_m) with
    draw(img, x, base, m). They come in one after another as k grows; each gets its height."""
    x0, y0, x1, y1 = box; norm = []
    for it in items:
        if isinstance(it, str): it = (it,)
        if callable(it[0]): fn, label, wm, hm = it[0], it[1], it[2], it[3]
        else: fn, label = DRAW[it[0]], (it[1] if len(it) > 1 else LABELS[it[0]]); wm, hm = SIZES[it[0]]
        norm.append((fn, label, wm, hm))
    gap = 60
    m = min((y1 - y0 - 90) / max(h for *_, h in norm), (x1 - x0 - gap * (len(norm) - 1) - 80) / sum(w for _, _, w, _ in norm))
    x, base = x0, y1 - 90; n = len(norm); last = -1e9; row = 0
    with Plate(img, (x0 - 10, base - 4, x1 + 10, base + 6)) as p:
        p.line([(x0 - 10, base), (x1 + 10, base)], GRAY, 3)
    for i, (fn, label, wm, hm) in enumerate(norm):
        u = appear(k * n, i, gap=1, dur=1)
        if u > 0:
            fn(img, x, base, m)
            lw = font(size).getlength(label) * 1.15
            lx = min(max(x + wm * m / 2, x0 + lw / 2), x1 - lw / 2)
            row = 1 - row if lx - lw / 2 < last + 16 else 0             # labels that would touch go one row down
            text(img, label.upper(), lx, base + 22 + row * (size + 14), size, WHITE, tracking=.15, anchor="mt")
            last = lx + lw / 2 if row == 0 else max(last, lx + lw / 2)
            if heights and u >= 1 and hm * m > 40:
                dimension(img, x + wm * m + 18, base, x + wm * m + 18, base - hm * m, f"{hm:g} {unit}", size=size - 2)
        x += wm * m + gap
    return m

# ---------- step by step ----------
def steps(img, items, box, active=0, t=0.0, vertical=True, size=34, color=CYAN):
    """Numbered steps that light up: items = [(title, note)] or titles; steps before 'active' are done, the active one
    is filled and the route between done steps flows."""
    x0, y0, x1, y1 = box; n = len(items)
    items = [it if isinstance(it, tuple) else (it, "") for it in items]
    if vertical:
        r = min(34, (y1 - y0) / n / 3); pos = [(x0 + r + 4, y0 + (y1 - y0) * (i + .5) / n) for i in range(n)]
    else:
        r = min(34, (x1 - x0) / n / 3); pos = [(x0 + (x1 - x0) * (i + .5) / n, y0 + r + 4) for i in range(n)]
    with Plate(img, (x0 - 10, y0 - 10, x1 + 10, y1 + 10)) as p:
        for i in range(n - 1): p.line([pos[i], pos[i + 1]], DIM, 3)
    for i in range(min(active, n - 1)): flow_path(img, [pos[i], pos[i + 1]], t, color, 4)
    for i, ((title, note), (px, py)) in enumerate(zip(items, pos)):
        state = "done" if i < active else ("active" if i == active else "off")
        step_badge(img, i + 1, px, py, r, state)
        tc = WHITE if i <= active else DIM
        if vertical:
            text(img, title.upper(), px + r + 28, py - (12 if note else 0), size, color if i == active else tc, anchor="lm")
            if note: text(img, note, px + r + 28, py + size * .7, int(size * .62), GRAY if i <= active else DIM, bold=False, anchor="lm")
        else:
            text(img, title.upper(), px, py + r + 26, int(size * .8), color if i == active else tc, anchor="mt")
            if note: text(img, note, px, py + r + 26 + size * 1.1, int(size * .55), GRAY if i <= active else DIM, bold=False, anchor="mt")
    return pos

# ---------- question and answer ----------
def question_card(img, s, x, y, appear_=1.0, size=88, mark=True):
    """Big question at the start of a video: a cyan question mark in a lens and the question typed beside it."""
    from . import headline
    if mark:
        r = size * .7
        with Plate(img, (x - 6, y - 6, x + 2 * r + 6, y + 2 * r + 6), glow=NEON) as p:
            p.circle(x + r, y + r, r, color=CYAN, w=4)
        text(img, "?", x + r, y + r, int(size * 1.05), CYAN, anchor="mm")
        x += 2 * r + 36
    return headline(img, s, x, y, size=size, appear=appear_)

def answer_card(img, s, x, y, w, k=1.0, size=48, label="RESPUESTA"):
    """Answer revealed at the end: a framed panel that scans in (k from 0 to 1) with the answer, *words* in cyan."""
    from .marks import plan_caption
    lines = max(1, math.ceil(font(size).getlength(s.replace("*", "")) / (w - 60)))
    h = lines * size * 1.3 + 80
    hk = h * max(0.0, min(1.0, k))
    if hk < 2: return
    with Plate(img, (x - 6, y - 6, x + w + 6, y + h + 6)) as p:
        p.rect(x, y, x + w, y + hk, fill=PANEL, color=CYAN, w=3)
    text(img, label, x + 24, y - 14, 22, CYAN, tracking=.3, anchor="lb")
    if k >= 1: plan_caption(img, s, 99, y=y + h / 2 + 6, size=size, maxw=w - 60, band=False)

# ---------- failure and consequences ----------
def failure_chain(img, nodes, box, fail=0, k=1.0, t=0.0, size=30, vertical=True):
    """A part fails (red, pulsing) and the effect travels down the chain: nodes after it turn red one by one as k
    grows. nodes = labels in order of cause to effect."""
    x0, y0, x1, y1 = box; n = len(nodes)
    reached = fail + int(max(0.0, min(1.0, k)) * (n - 1 - fail) + 1e-6)
    bw, bh = (x1 - x0) * .62, min(96, (y1 - y0) / n * .55)
    if vertical: ctr = [((x0 + x1) / 2, y0 + (y1 - y0) * (i + .5) / n) for i in range(n)]
    else:
        bw, bh = min(220, (x1 - x0) / n * .8), 90; ctr = [(x0 + (x1 - x0) * (i + .5) / n, (y0 + y1) / 2) for i in range(n)]
    for i in range(n - 1):
        a, b = ctr[i], ctr[i + 1]
        p0 = (a[0], a[1] + bh / 2 + 6) if vertical else (a[0] + bw / 2 + 6, a[1])
        p1 = (b[0], b[1] - bh / 2 - 8) if vertical else (b[0] - bw / 2 - 8, b[1])
        hot = fail <= i < reached
        path_arrow(img, [p0, p1], color=RISK if hot else DIM, w=4, head=18, curved=False, glow=NEON if hot else 0)
    for i, (label, (cx, cy)) in enumerate(zip(nodes, ctr)):
        bad = fail <= i <= reached
        col = RISK if bad else WHITE
        with Plate(img, (cx - bw / 2 - 4, cy - bh / 2 - 4, cx + bw / 2 + 4, cy + bh / 2 + 4), glow=NEON if i == fail else 0) as p:
            p.rect(cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2, fill=mix(PANEL, RISK, .18) if bad else PANEL, color=col, w=3)
        text(img, label.upper(), cx, cy, size, col, anchor="mm")
        if i == fail: alert(img, cx + bw / 2 + 44 if vertical else cx, cy if vertical else cy - bh / 2 - 50, t, r=20)

# ---------- exploded view ----------
def _shape(p, kind, x, y, w, h, color):
    if kind == "circle": p.circle(x, y, w / 2, fill=PANEL, color=color, w=3)
    elif kind == "rod": p.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill=mix(PANEL, GRAY, .3), color=color, w=3)
    elif kind == "spring":
        pts = [(x + (w / 2 if i % 2 else -w / 2), y - h / 2 + h * i / 10) for i in range(11)]
        p.line(pts, color, 3)
    else: p.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill=PANEL, color=color, w=3)

def exploded_view(img, parts, cx, cy, k=1.0, size=24, color=WHITE):
    """An object pulled apart into its parts (k 0 = assembled, 1 = apart) with a label for each part.
    parts = [dict(kind="rect"|"circle"|"rod"|"spring", w=, h=, at=(dx, dy), out=(dx, dy), label="")] or with
    draw=fn(img, x, y) instead of kind; 'at' is its place in the object and 'out' how far it moves."""
    for i, pt in enumerate(parts):
        ax, ay = pt.get("at", (0, 0)); ox, oy = pt.get("out", (0, 0))
        x, y = cx + ax + ox * k, cy + ay + oy * k
        if "draw" in pt: pt["draw"](img, x, y)
        else:
            w, h = pt.get("w", 80), pt.get("h", 40)
            with Plate(img, (x - w / 2 - 6, y - h / 2 - 6, x + w / 2 + 6, y + h / 2 + 6)) as p:
                _shape(p, pt.get("kind", "rect"), x, y, w, h, pt.get("color", color))
        if k > .9 and pt.get("label"):
            side = (1 if ox > 0 else -1) if ox else (1 if x < 540 else -1)
            callout(img, pt["label"], x + side * pt.get("w", 80) / 2, y, x + side * (pt.get("w", 80) / 2 + 120), y - 40, size=size)

# ---------- schematic map ----------
def schematic_map(img, box, t=0.0, network=(), nodes=(), seed=3, block=150, street=34, colors=None, k=1.0, size=22):
    """City seen from above: blocks between streets, and networks drawn on top as glowing flows (pipes, cables,
    lines). network = [points, …] or [(points, color), …]; nodes = [(x, y, label)]."""
    x0, y0, x1, y1 = box; R = random.Random(seed); colors = colors or SERIES
    with Plate(img, (x0 - 4, y0 - 4, x1 + 4, y1 + 4)) as p:
        p.rect(x0, y0, x1, y1, fill=PANEL, color=DIM, w=2)
        y = y0 + street
        while y + 40 < y1:
            bh = min(block * R.uniform(.8, 1.2), y1 - street - y); x = x0 + street
            while x + 40 < x1:
                bw = min(block * R.uniform(.8, 1.4), x1 - street - x)
                if bw > 30 and bh > 30:
                    p.rect(x, y, x + bw, y + bh, fill=mix(PANEL, GRAY, .1), color=mix(PANEL, GRAY, .45), w=2)
                x += bw + street
            y += bh + street
    for i, net in enumerate(network):
        pts, col = (net if isinstance(net, tuple) and len(net) == 2 and isinstance(net[1], tuple) and len(net[1]) == 3
                    else (net, colors[i % len(colors)]))
        trace_line(img, pts, k, mix(col, PANEL, .45), 6, tip=None)
        if k >= 1: flow_path(img, pts, t, col, 4)
    for x, y, label in nodes:
        with Plate(img, (x - 18, y - 18, x + 18, y + 18), glow=NEON) as p:
            p.circle(x, y, 12, fill=ACCENT, color=WHITE, w=3)
        if label: text(img, label.upper(), x + 22, y - 18, size, WHITE, anchor="lb")
