"""Charts of the blueprint style, made to be read in three seconds on a phone: a digital readout, horizontal bars,
columns (with shaded bands and a moving cursor), a line that draws itself, a limit meter, a fill bar, an icon grid
(1 icon = X), a scale of magnitudes, a split bar, before/after and a timeline. Every one grows with k (0 to 1).

    hbar_chart(img, [("TORRE A", 828), ("TORRE B", 632), ("TORRE C", 541)], 80, 700, 900, k=tw(c.lt, 0, 1, 0, 1), unit="m")
    trend_line(img, [0, 4, 9, 15, 22], (80, 700, 1000, 1200), k=tw(c.lt, 0, 2, 0, 1), labels=["2020", "", "", "", "2024"])
"""
import math

from . import Plate, text, font, mix, trace, NEON, SERIES, WHITE, CYAN, GRAY, DIM, ACCENT, RISK, PANEL

def _num(v, decimals=0):
    return f"{v:,.{decimals}f}" if isinstance(v, (int, float)) else str(v)

def readout(img, value, x, y, label="", size=96, decimals=0, unit="", color=CYAN, anchor="l"):
    """Digital readout: a framed number with fixed-width digits (counts up when value is animated), label on top."""
    s = _num(value, decimals); f = font(size)
    digits = max(len(s), 1); cw = f.getlength("0"); w = cw * digits + size * .5
    if unit: w += font(size * .32).getlength(" " + unit)
    x0 = x - {"l": 0, "m": w / 2, "r": w}[anchor]; y0, y1 = y, y + size * 1.25
    with Plate(img, (x0 - 4, y0 - 4, x0 + w + 4, y1 + 4)) as p:
        p.rect(x0, y0, x0 + w, y1, fill=PANEL, color=DIM, w=2)
        p.line([(x0, y0), (x0 + 26, y0)], color, 4); p.line([(x0 + w - 26, y1), (x0 + w, y1)], color, 4)
    xr = x0 + size * .25 + cw * digits
    text(img, s, xr, (y0 + y1) / 2, size, color, anchor="rm")
    if unit: text(img, unit.upper(), xr + size * .12, y1 - size * .3, int(size * .32), GRAY, anchor="ls")
    if label: text(img, label.upper(), x0, y0 - 12, 22, GRAY, tracking=.25, anchor="lb")
    return (x0, y0, x0 + w, y1)

def hbar_chart(img, items, x, y, w, bar_h=44, gap=40, k=1.0, vmax=None, unit="", decimals=0, highlight=None, size=26):
    """Horizontal bars comparing 2 to 6 things in one measure: items = [(label, value), …]; highlight = index in cyan."""
    vmax = vmax or max(v for _, v in items) or 1
    for i, (label, v) in enumerate(items):
        yy = y + i * (bar_h + gap + size); u = max(0.0, min(1.0, k * 1.4 - i * .12))
        text(img, label.upper(), x, yy, size, WHITE if highlight in (None, i) else GRAY, anchor="lt")
        by = yy + size * 1.25; bw = w * v / vmax * u
        col = CYAN if highlight == i else (mix(DIM, CYAN, .55) if highlight is None else DIM)
        with Plate(img, (x - 4, by - 4, x + w + 4, by + bar_h + 4)) as p:
            p.rect(x, by, x + w, by + bar_h, color=mix(PANEL, DIM, .6), w=1)
            if bw > 1: p.rect(x, by, x + bw, by + bar_h, fill=col)
        if u > .05:
            s = _num(v * u, decimals) + (f" {unit}" if unit else "")
            inside = bw > font(size).getlength(s) + 30
            text(img, s, x + bw - 12 if inside else x + bw + 12, by + bar_h / 2, size, PANEL if inside else WHITE,
                 anchor="rm" if inside else "lm")
    return y + len(items) * (bar_h + gap + size)

def column_chart(img, values, x, base, w, h, k=1.0, vmax=None, labels=None, bands=(), cursor=None, highlight=None,
                 color=CYAN, size=22):
    """Vertical columns (hour by hour, year by year); bands = [(i0, i1, label)] shaded, cursor = position in columns."""
    n = len(values); vmax = vmax or max(values) or 1; cw = w / n
    with Plate(img, (x - 4, base - h - 40, x + w + 4, base + 6)) as p:
        for i0, i1, _ in bands:
            p.rect(x + i0 * cw, base - h, x + i1 * cw, base, fill=mix(PANEL, ACCENT, .08))
        for i, v in enumerate(values):
            shown = (i + 1) <= k * n + 1e-9 if cursor is None else i < cursor
            if not shown: continue
            vh = h * v / vmax
            c = color if highlight == i else mix(DIM, color, .3 + .7 * v / vmax)
            p.rect(x + i * cw + cw * .16, base - vh, x + (i + 1) * cw - cw * .16, base, fill=c)
        p.line([(x, base), (x + w, base)], WHITE, 3)
        if cursor is not None:
            p.dashed([(x + cursor * cw, base - h - 20), (x + cursor * cw, base + 4)], ACCENT, 2, 10, 8)
    for i0, i1, label in bands:
        if label: text(img, label.upper(), x + (i0 + i1) / 2 * cw, base - h - 10, size, ACCENT, tracking=.2, anchor="ms")
    for i, lb in enumerate(labels or ()):
        if lb: text(img, str(lb), x + i * cw, base + 14, size, GRAY, anchor="lt")

def trend_line(img, values, box, k=1.0, vmin=None, vmax=None, labels=None, unit="", decimals=0, color=CYAN, area=True,
               size=22):
    """Line that draws itself over time inside box, with its last value at the tip; labels under the x axis."""
    x0, y0, x1, y1 = box; n = len(values)
    lo = min(values) if vmin is None else vmin; hi = max(values) if vmax is None else vmax; hi = hi if hi != lo else lo + 1
    pts = [(x0 + (x1 - x0) * i / max(1, n - 1), y1 - (y1 - y0) * (v - lo) / (hi - lo)) for i, v in enumerate(values)]
    path = trace(pts, k)
    with Plate(img, (x0 - 10, y0 - 10, x1 + 10, y1 + 10)) as p:
        for j in range(1, 4): p.dashed([(x0, y1 - (y1 - y0) * j / 4), (x1, y1 - (y1 - y0) * j / 4)], mix(PANEL, DIM, .7), 1, 6, 8)
        p.line([(x0, y0), (x0, y1), (x1, y1)], GRAY, 2)
        if len(path) > 1 and area: p.poly(path + [(path[-1][0], y1), (x0, y1)], fill=mix(PANEL, color, .18))
    if len(path) > 1:
        with Plate(img, (x0 - 10, y0 - 10, x1 + 10, y1 + 10), glow=NEON) as p:
            p.line(path, color, 5)
            p.circle(*path[-1], 9, fill=color)
    if len(path) > 1:
        seg = min(n - 1, int(k * (n - 1) + 1e-9)); u = k * (n - 1) - seg
        v = values[seg] + (values[min(n - 1, seg + 1)] - values[seg]) * u
        text(img, _num(v, decimals) + (f" {unit}" if unit else ""), path[-1][0] + 16, path[-1][1] - 18, size + 6, WHITE, anchor="lb")
    for i, lb in enumerate(labels or ()):
        if lb: text(img, str(lb), pts[i][0], y1 + 14, size, GRAY, anchor="mt")

def _dial(p, cx, cy, r, a0, a1, ticks, color=GRAY):
    for k in range(ticks + 1):
        a = a0 + (a1 - a0) * k / ticks; L = 14 if k % 2 == 0 else 7
        p.line([(cx + math.cos(a) * (r - 6), cy + math.sin(a) * (r - 6)), (cx + math.cos(a) * (r - 6 - L), cy + math.sin(a) * (r - 6 - L))], color, 3)

def limit_meter(img, cx, cy, r, value, vmax, limit, label="", unit="", decimals=0):
    """Half-dial showing how close something is to its limit: the zone past 'limit' in red, needle on value."""
    a0, a1 = math.pi, 2 * math.pi; al = a0 + (a1 - a0) * min(1, limit / vmax)
    with Plate(img, (cx - r - 10, cy - r - 10, cx + r + 10, cy + 20)) as p:
        arc = lambda b0, b1: [(cx + math.cos(b0 + (b1 - b0) * i / 40) * r, cy + math.sin(b0 + (b1 - b0) * i / 40) * r) for i in range(41)]
        p.line(arc(a0, al), WHITE, 6); p.line(arc(al, a1), RISK, 10)
        _dial(p, cx, cy, r, a0, a1, 10)
        a = a0 + (a1 - a0) * max(0, min(1.02, value / vmax))
        over = value >= limit
        p.line([(cx, cy), (cx + math.cos(a) * (r - 20), cy + math.sin(a) * (r - 20))], RISK if over else ACCENT, 6)
        p.circle(cx, cy, 10, fill=RISK if over else ACCENT)
    text(img, _num(value, decimals) + (f" {unit}" if unit else ""), cx, cy + 40, int(r * .24), RISK if value >= limit else WHITE, anchor="mt")
    if label: text(img, label.upper(), cx, cy - r - 24, 22, GRAY, tracking=.25, anchor="mb")

def fill_bar(img, x0, y0, x1, y1, level, label="", color=CYAN, percent=True, ticks=4):
    """Fill or progress bar (a tank filling or emptying); vertical when taller than wide."""
    level = max(0.0, min(1.0, level)); vertical = (y1 - y0) > (x1 - x0)
    with Plate(img, (x0 - 20, y0 - 4, x1 + 20, y1 + 4)) as p:
        p.rect(x0, y0, x1, y1, fill=PANEL, color=WHITE, w=3)
        if vertical: p.rect(x0 + 5, y1 - 5 - (y1 - y0 - 10) * level, x1 - 5, y1 - 5, fill=color)
        else: p.rect(x0 + 5, y0 + 5, x0 + 5 + (x1 - x0 - 10) * level, y1 - 5, fill=color)
        for i in range(1, ticks):
            if vertical: yy = y0 + (y1 - y0) * i / ticks; p.line([(x1, yy), (x1 + 14, yy)], GRAY, 2)
            else: xx = x0 + (x1 - x0) * i / ticks; p.line([(xx, y1), (xx, y1 + 14)], GRAY, 2)
    if percent:
        s = f"{int(round(level * 100))} %"
        if vertical: text(img, s, (x0 + x1) / 2, y0 - 16, 26, WHITE, anchor="mb")
        else: text(img, s, x1 + 18, (y0 + y1) / 2, 26, WHITE, anchor="lm")
    if label: text(img, label.upper(), x0, y1 + 30, 22, GRAY, tracking=.2, anchor="lt")

def _icon(p, kind, x, y, s, color):
    if kind == "person":
        p.circle(x, y - s * .28, s * .16, fill=color)
        p.poly([(x - s * .24, y + s * .38), (x - s * .2, y - s * .06), (x + s * .2, y - s * .06), (x + s * .24, y + s * .38)], fill=color)
    elif kind == "drop":
        p.poly([(x, y - s * .42)] + [(x + s * .28 * math.cos(a), y + s * .1 + s * .28 * math.sin(a))
                                    for a in [math.radians(d) for d in range(-20, 201, 20)]], fill=color)
    elif kind == "box":
        p.rect(x - s * .34, y - s * .26, x + s * .34, y + s * .3, fill=color)
        p.line([(x - s * .34, y - s * .06), (x + s * .34, y - s * .06)], PANEL, 2)
    else:
        p.rect(x - s * .32, y - s * .32, x + s * .32, y + s * .32, fill=color)

def icon_grid(img, n, x, y, cols=10, cell=60, k=1.0, kind="square", color=CYAN, off=DIM, total=None, legend=""):
    """Grid of icons to make a big amount visible (1 icon = X): the first n of 'total' light up as k grows.
    kind = square, person, drop, box, or a function (p, x, y, size, color)."""
    total = total or n; rows = math.ceil(total / cols); lit = int(round(n * max(0.0, min(1.0, k))))
    with Plate(img, (x - 4, y - 4, x + cols * cell + 4, y + rows * cell + 4)) as p:
        for i in range(total):
            cx, cy = x + (i % cols + .5) * cell, y + (i // cols + .5) * cell
            c = color if i < lit else off
            kind(p, cx, cy, cell * .8, c) if callable(kind) else _icon(p, kind, cx, cy, cell * .8, c)
    if legend: text(img, legend.upper(), x, y + rows * cell + 20, 22, GRAY, tracking=.2, anchor="lt")

def magnitude_scale(img, refs, value, x0, y, x1, label="", unit="", log=True, k=1.0, size=22):
    """Scale from small to huge with known references (refs = [(label, value)]) and the value marked between them."""
    vals = [v for _, v in refs] + [value]; lo, hi = min(vals), max(vals)
    pos = (lambda v: x0 + (x1 - x0) * (math.log10(v) - math.log10(lo)) / ((math.log10(hi) - math.log10(lo)) or 1)) if log \
        else (lambda v: x0 + (x1 - x0) * (v - lo) / ((hi - lo) or 1))
    with Plate(img, (x0 - 10, y - 60, x1 + 10, y + 30)) as p:
        p.line([(x0, y), (x1, y)], GRAY, 3)
        for _, v in refs: p.line([(pos(v), y - 14), (pos(v), y + 14)], WHITE, 3)
        vx = pos(lo) + (pos(value) - pos(lo)) * k
        p.poly([(vx, y - 6), (vx - 16, y - 34), (vx + 16, y - 34)], fill=CYAN)
    for i, (lb, v) in enumerate(refs):
        text(img, lb.upper(), pos(v), y + 30 + (i % 2) * 32, size, GRAY, anchor="mt")
    if k >= 1 and label: text(img, label.upper() + (f" · {_num(value)} {unit}" if unit else ""), vx, y - 46, size + 4, CYAN, anchor="mb")

def split_bar(img, parts, x0, y, x1, h=64, k=1.0, colors=None, size=22):
    """One bar split in the parts of a total (parts = [(label, share)]); labels under each part."""
    total = sum(v for _, v in parts) or 1
    colors = colors or SERIES
    x, w = x0, (x1 - x0) * max(0.0, min(1.0, k))
    with Plate(img, (x0 - 4, y - 4, x1 + 4, y + h + 4)) as p:
        p.rect(x0, y, x1, y + h, color=DIM, w=2)
        for i, (_, v) in enumerate(parts):
            pw = w * v / total
            if pw > 1: p.rect(x, y, x + pw, y + h, fill=colors[i % len(colors)]); p.line([(x + pw, y), (x + pw, y + h)], PANEL, 3)
            x += pw
    if k >= 1:
        x = x0
        for i, (lb, v) in enumerate(parts):
            pw = (x1 - x0) * v / total
            text(img, f"{round(100 * v / total)}%", x + pw / 2, y + h / 2, size + 2, PANEL, anchor="mm")
            text(img, lb.upper(), x + pw / 2, y + h + 18 + (i % 2) * 30, size, GRAY, anchor="mt")
            x += pw

def before_after(img, before, after, box, k=0.5, labels=("ANTES", "DESPUÉS"), color=CYAN):
    """Before/after split: 'before' and 'after' are full-size images; the divider sits at fraction k of the box."""
    x0, y0, x1, y1 = [int(v) for v in box]; cut = int(x0 + (x1 - x0) * k)
    if cut > x0: img.paste(before.crop((x0, y0, cut, y1)), (x0, y0))
    if cut < x1: img.paste(after.crop((cut, y0, x1, y1)), (cut, y0))
    with Plate(img, (cut - 24, y0 - 4, cut + 24, y1 + 4)) as p:
        p.line([(cut, y0), (cut, y1)], color, 4)
        p.circle(cut, (y0 + y1) / 2, 18, fill=PANEL, color=color, w=3)
    if cut - x0 > 160: text(img, labels[0], x0 + 20, y0 + 20, 24, GRAY, tracking=.25, anchor="lt")
    if x1 - cut > 160: text(img, labels[1], x1 - 20, y0 + 20, 24, color, tracking=.25, anchor="rt")

def timeline(img, events, x0, y, x1, now, t0=None, t1=None, size=22, unit=""):
    """Horizontal timeline: events = [(time, label)] light up when 'now' passes them (hour by hour, year by year)."""
    t0 = events[0][0] if t0 is None else t0; t1 = events[-1][0] if t1 is None else t1
    pos = lambda tt: x0 + (x1 - x0) * (tt - t0) / ((t1 - t0) or 1)
    with Plate(img, (x0 - 20, y - 30, x1 + 20, y + 30)) as p:
        p.line([(x0, y), (x1, y)], DIM, 4)
        for tt, _ in events:
            on = now >= tt
            p.circle(pos(tt), y, 12 if on else 9, fill=CYAN if on else PANEL, color=CYAN if on else DIM, w=3)
    with Plate(img, (x0 - 20, y - 30, x1 + 20, y + 30), glow=NEON) as p:
        p.line([(x0, y), (pos(max(t0, min(t1, now))), y)], CYAN, 4)
        p.circle(pos(max(t0, min(t1, now))), y, 7, fill=WHITE)
    for i, (tt, lb) in enumerate(events):
        on = now >= tt; up = i % 2 == 0
        text(img, f"{tt:g}{unit}", pos(tt), y + (-26 if up else 26), size, WHITE if on else DIM, anchor="mb" if up else "mt")
        text(img, lb.upper(), pos(tt), y + (-58 if up else 58), size, CYAN if on else DIM, anchor="mb" if up else "mt")
