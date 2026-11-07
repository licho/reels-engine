"""Sketch-style coffee shop: takeaway cup in sizes S/M/L, cup meter (a clear cup that fills like a bar), espresso cup
with saucer, cup grid and cup stack (to count in cups), coffee bean and bean heap, coffee sack, espresso machine with
a pressure gauge, chalkboard menu, shop counter, the doodle as a barista and a coffee shop background. All take the
image (img) and a 'seed'. Things on the floor draw no floor shadow unless shadow=True.

    bg = cafe_bg()
    cafe_counter(bg, 540, FLOOR, 1000)
    takeaway_cup(img, 300, 900, "L", label="$4.50")
    cup_meter(img, 760, FLOOR - 40, 420, fill=.65, label="65%")
    barista(img, 540, FLOOR, .9, held="cup")

Things that stand on the floor take (cx, base) = bottom center; floating things take their center (cx, cy)."""
import math
from functools import lru_cache
from . import Pen, INK, WHITE, SHADE, RED, GREEN, GLASS, GLASS_D, WOOD, WOOD_D, ellipse, rrect, rotated, spline
from .everyday import GRAY, GRAY_L, DARK
from .humans import doodle
from ..core import W, H, FLOOR, grad

COFFEE, COFFEE_D = (120, 72, 42), (76, 44, 24)       # brewed coffee
CREMA = (214, 168, 110)                              # the foam on top
BEAN, BEAN_D = (110, 64, 36), (64, 36, 18)
CUP_PAPER = (252, 250, 244)
BURLAP, BURLAP_D = (206, 172, 116), (156, 122, 72)
CHALK, CHALK_D = (52, 60, 56), (34, 40, 37)
CHROME, CHROME_D = (206, 212, 220), (140, 146, 158)
CERAMIC = (250, 250, 248)
APRON, APRON_D = (96, 62, 40), (62, 38, 22)
CAFE_WALL = ((250, 242, 226), (242, 230, 206))       # warm cream wall (top, bottom)
TILE = (236, 226, 204)
CAFE_FLOOR, CAFE_FLOOR_D = (214, 182, 140), (176, 140, 98)
SIZES = {"S": .78, "M": 1.0, "L": 1.24}

# ---------- cups ----------
def _paper_cup(p, cx, base, h, sleeve, label, lid=True, steam=True):
    """Takeaway cup drawn on an open Pen; returns the y of the rim."""
    wt, wb, top = h * .31, h * .23, base - h * .82
    at = lambda f: wb + (wt - wb) * f
    p.shape([(cx - wt, top), (cx + wt, top), (cx + wb, base), (cx - wb, base)], CUP_PAPER, w=5)
    if sleeve:
        f0, f1 = .28, .7
        y0, y1 = base - h * .82 * f1, base - h * .82 * f0
        p.shape([(cx - at(f1), y0), (cx + at(f1), y0), (cx + at(f0), y1), (cx - at(f0), y1)], sleeve, w=4.5)
        if label:
            p.text(str(label), cx, (y0 + y1) / 2, min(h * .13, at(f0) * 3.2 / max(1, len(str(label)))), fill=WHITE,
                   stroke=INK, sw=max(1, h * .008), warp=.5)
    if lid:
        p.shape(rrect(cx - wt * 1.12, top - h * .09, cx + wt * 1.12, top + h * .01, h * .03), GRAY_L, w=5, amp=.8)
        p.shape(rrect(cx - wt * .8, top - h * .16, cx + wt * .8, top - h * .08, h * .03), GRAY_L, w=4.5, amp=.6)
        p.shape(ellipse(cx + wt * .45, top - h * .12, h * .025, h * .015, n=12), DARK, w=0)
    if steam:
        for dx in (-.12, .1):
            x = cx + dx * h
            p.stroke(spline([(x, top - h * .22), (x + h * .05, top - h * .32), (x - h * .04, top - h * .44),
                             (x + h * .03, top - h * .57)]), max(2.5, h * .018), GRAY, amp=.6)
    return top

def takeaway_cup(img, cx, base, size="M", h=220, label=None, sleeve=WOOD, lid=True, steam=False, seed=1, shadow=False):
    """Coffee to go in size S, M or L (h = height of the M); label = text on the sleeve (a price, a size)."""
    h = h * SIZES.get(str(size).upper(), 1.0)
    with Pen(img, (cx - h * .45, base - h * 1.45, cx + h * .45, base + h * .1), seed) as p:
        if shadow: p.blob(cx, base, h * .32, h * .04, SHADE)
        _paper_cup(p, cx, base, h, sleeve, label, lid, steam)

def cup_meter(img, cx, base, h=420, fill=0.5, color=COFFEE, label=None, ticks=5, crema=True, seed=1, shadow=False):
    """Clear plastic cup that fills with coffee like a bar chart; fill = 0…1, label = text above, ticks = marks (0 = none)."""
    wt, wb, top = h * .34, h * .25, base - h
    cup = [(cx - wt, top), (cx + wt, top), (cx + wb, base), (cx - wb, base)]
    f = max(0.0, min(1.0, fill))
    with Pen(img, (cx - h * .5, base - h * 1.25, cx + h * .5, base + h * .06), seed) as p:
        if shadow: p.blob(cx, base, h * .32, h * .03, SHADE)
        p.poly(p.wobble(cup, .4, True), GLASS)
        if f > 0:
            ly = base - (h * .94) * f
            with p.clip(cup):
                p.poly([(cx - h, base + 4), (cx + h, base + 4), (cx + h, ly), (cx - h, ly)], color)
                if crema and f > .04:
                    p.poly([(cx - h, ly), (cx + h, ly), (cx + h, ly + h * .035), (cx - h, ly + h * .035)], CREMA)
                p.stroke([(cx - wb * .62, base - h * .06), (cx - wt * .62, max(ly + h * .05, top + h * .1))], h * .02,
                         (255, 255, 255), amp=.3)
        with p.clip(cup):
            p.stroke([(cx + wb * .55, base - h * .08), (cx + wt * .55, top + h * .1)], h * .025, GLASS_D, amp=.3)
        p.stroke(cup, 5.5, amp=.5, closed=True)
        p.stroke([(cx - wt * 1.06, top), (cx + wt * 1.06, top)], 7, amp=.3)
        for k in range(1, ticks + 1 if ticks else 0):
            yy = base - h * .94 * k / (ticks + 1)
            xr = cx - (wb + (wt - wb) * (base - yy) / h)
            p.stroke([(xr + 6, yy), (xr + h * (.08 if k % 2 else .05), yy)], 3, amp=.1)
        if label: p.text(str(label), cx, top - h * .11, h * .12, fill=color, stroke=INK, sw=max(1.5, h * .004), warp=.5)

def espresso_cup(img, cx, base, h=150, color=CERAMIC, steam=True, seed=1, shadow=False):
    """Small ceramic coffee cup on its saucer (a cup at a table, the classic 'taza')."""
    w = h * 1.1
    with Pen(img, (cx - w * .9, base - h * 1.6, cx + w * .9, base + h * .1), seed) as p:
        if shadow: p.blob(cx, base, w * .7, h * .06, SHADE)
        p.shape(ellipse(cx, base - h * .08, w * .72, h * .1, n=40), color, w=5, amp=.4)
        top = base - h * .9
        body = spline([(cx - w * .42, top), (cx - w * .38, base - h * .45), (cx - w * .22, base - h * .14), (cx, base - h * .1),
                       (cx + w * .22, base - h * .14), (cx + w * .38, base - h * .45), (cx + w * .42, top)])
        p.stroke(spline([(cx + w * .38, top + h * .18), (cx + w * .66, top + h * .16), (cx + w * .66, top + h * .46),
                         (cx + w * .34, top + h * .52)]), h * .07, amp=.3)
        p.shape(body, color, w=5.5, amp=.5)
        p.shape(ellipse(cx, top, w * .42, h * .1, n=36), COFFEE, w=4.5, amp=.3)
        p.poly(ellipse(cx - w * .08, top - h * .005, w * .2, h * .04, n=24), CREMA)
        if steam:
            for dx in (-.14, .1):
                x = cx + dx * w
                p.stroke(spline([(x, top - h * .2), (x + h * .07, top - h * .36), (x - h * .05, top - h * .52),
                                 (x + h * .04, top - h * .68)]), max(2.5, h * .025), GRAY, amp=.5)

def cup_grid(img, x, y, cols=5, rows=2, size=110, filled=None, color=COFFEE, empty=GRAY_L, seed=1):
    """Grid of little cups to count with (pictogram); filled = how many are full of coffee (None = all); (x, y) = top left."""
    n = cols * rows
    filled = n if filled is None else max(0, min(n, int(filled)))
    gap = size * 1.15
    with Pen(img, (x - size * .2, y - size * .3, x + cols * gap + size * .2, y + rows * gap * 1.1 + size * .2), seed) as p:
        for k in range(n):
            cx = x + (k % cols) * gap + size * .5; base = y + (k // cols) * gap * 1.1 + size
            wt, wb, top = size * .34, size * .25, base - size * .82
            cup = [(cx - wt, top), (cx + wt, top), (cx + wb, base), (cx - wb, base)]
            p.shape(cup, color if k < filled else empty, w=4, amp=.4)
            p.shape(rrect(cx - wt * 1.12, top - size * .1, cx + wt * 1.12, top + size * .01, size * .03),
                    WHITE if k < filled else empty, w=4, amp=.3)

def cup_stack(img, cx, base, n=5, h=110, color=CERAMIC, seed=1, shadow=False):
    """Tower of n cups on saucers stacked one on top of the other (a lot of coffees)."""
    step = h * .82
    with Pen(img, (cx - h * .9, base - step * n - h * .5, cx + h * .9, base + h * .1), seed) as p:
        if shadow: p.blob(cx, base, h * .7, h * .05, SHADE)
        for k in range(n):
            b = base - k * step
            dx = math.sin(k * 1.7) * h * .04
            p.shape(ellipse(cx + dx, b - h * .06, h * .62, h * .08, n=32), color, w=4, amp=.3)
            p.stroke(spline([(cx + dx + h * .32, b - h * .62), (cx + dx + h * .56, b - h * .62), (cx + dx + h * .54, b - h * .36),
                             (cx + dx + h * .3, b - h * .3)]), h * .06, amp=.2)
            p.shape([(cx + dx - h * .38, b - h * .76), (cx + dx + h * .38, b - h * .76), (cx + dx + h * .26, b - h * .12),
                     (cx + dx - h * .26, b - h * .12)], color, w=4.5, amp=.4)

# ---------- beans and sacks ----------
def _bean(p, cx, cy, r, ang, w=4):
    pts = rotated(ellipse(cx, cy, r * .72, r, n=28), cx, cy, ang)
    p.shape(pts, BEAN, w=w, amp=.3)
    crease = rotated(spline([(cx, cy - r * .82), (cx + r * .16, cy - r * .3), (cx - r * .16, cy + r * .3), (cx, cy + r * .82)]),
                     cx, cy, ang)
    p.stroke(crease, max(2, w * .8), BEAN_D, amp=.2)

def coffee_bean(img, cx, cy, r=60, ang=0.4, seed=1):
    """One big coffee bean with its crease (for a mascot or a close-up); ang = tilt in radians."""
    with Pen(img, (cx - r * 1.3, cy - r * 1.3, cx + r * 1.3, cy + r * 1.3), seed) as p:
        _bean(p, cx, cy, r, ang, w=max(4, r * .08))

def coffee_beans(img, cx, base, w=260, n=14, seed=1):
    """Little heap of coffee beans sitting on (cx, base)."""
    r = w * .07
    with Pen(img, (cx - w * .7, base - w * .6, cx + w * .7, base + r * 1.5), seed) as p:
        k, row, placed = 0, 0, 0
        while placed < n:
            per = max(1, int(w / (r * 1.9)) - row * 2)
            for j in range(per):
                if placed >= n: break
                bx = cx + (j - (per - 1) / 2) * r * 1.8 + (row % 2) * r * .3
                by = base - r * .9 - row * r * 1.25
                _bean(p, bx, by, r, (k * 1.3) % math.pi - .8, w=3)
                k += 1; placed += 1
            row += 1

def coffee_sack(img, cx, base, h=300, label="COFFEE", beans=True, seed=1, shadow=False):
    """Open burlap sack full of coffee beans; label = text stamped on it."""
    w = h * .8
    with Pen(img, (cx - w * .75, base - h * 1.12, cx + w * .75, base + h * .06), seed) as p:
        if shadow: p.blob(cx, base, w * .6, h * .04, SHADE)
        mouth = base - h * .86
        body = spline([(cx - w * .44, mouth), (cx - w * .52, base - h * .5), (cx - w * .5, base - h * .1), (cx - w * .3, base),
                       (cx + w * .3, base), (cx + w * .5, base - h * .1), (cx + w * .52, base - h * .5), (cx + w * .44, mouth)])
        p.shape(body, BURLAP, w=6, amp=.6)
        with p.clip(body):
            for k in range(-6, 7): p.stroke([(cx + k * w * .09, mouth), (cx + k * w * .09, base)], 2, BURLAP_D, amp=.4)
        p.stroke(body, 6, amp=.6)
        if beans:
            p.shape(ellipse(cx, mouth, w * .44, h * .07, n=32), BEAN_D, w=4, amp=.3)
            for j in range(9):
                _bean(p, cx + (j - 4) * w * .085, mouth - h * .03 - (j % 2) * h * .03, h * .035, j * .7, w=2.5)
        p.stroke(spline([(cx - w * .5, mouth + h * .06), (cx, mouth + h * .1), (cx + w * .5, mouth + h * .06)]), 3, BURLAP_D, amp=.3)
        if label:
            p.text(str(label), cx, base - h * .42, min(h * .13, w * 1.3 / max(1, len(str(label)))), fill=APRON_D, warp=1.2)

# ---------- machines and furniture ----------
def espresso_machine(img, cx, base, w=420, color=RED, pressure=0.5, cup=True, steam=False, band=None, seed=1, shadow=False):
    """Espresso machine with a pressure gauge (pressure = 0…1 moves the needle), group head and an optional cup;
    band = (low, high) in 0…1 paints that stretch of the dial green (a target zone)."""
    h = w * .9
    x0, x1, top = cx - w / 2, cx + w / 2, base - h
    with Pen(img, (x0 - w * .12, top - h * .4, x1 + w * .12, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .04, SHADE)
        p.shape(rrect(x0, top, x1, base, w * .05), color, w=6, amp=.6)
        dark = tuple(int(v * .72) for v in color)
        p.shape(rrect(x0 + w * .04, top + h * .62, x1 - w * .04, base - h * .04, w * .03), CHROME, w=4.5, amp=.4)
        for k in range(6): p.stroke([(x0 + w * (.1 + k * .16), top + h * .68), (x0 + w * (.1 + k * .16), base - h * .1)], 2.5,
                                    CHROME_D, amp=.2)
        p.shape(rrect(x0 + w * .02, top - h * .06, x1 - w * .02, top + h * .02, w * .02), CHROME, w=4.5, amp=.4)
        for k in range(4):                                         # cups warming on top
            ux = x0 + w * (.2 + k * .2); ub = top - h * .06
            p.shape([(ux - w * .05, ub - h * .12), (ux + w * .05, ub - h * .12), (ux + w * .035, ub), (ux - w * .035, ub)],
                    CERAMIC, w=3.5, amp=.3)
        gx, gy, gr = cx, top + h * .22, h * .14
        p.shape(ellipse(gx, gy, gr * 1.15, gr * 1.15, n=36), CHROME, w=5, amp=.3)
        p.shape(ellipse(gx, gy, gr, gr, n=36), WHITE, w=3.5, amp=.2)
        if band:
            lo, hi = sorted(max(0.0, min(1.0, v)) for v in band)
            arc = [math.pi * (1.15 - 1.3 * (lo + (hi - lo) * k / 12)) for k in range(13)]
            p.poly([(gx + math.cos(a) * gr * .95, gy - math.sin(a) * gr * .95) for a in arc] +
                   [(gx + math.cos(a) * gr * .62, gy - math.sin(a) * gr * .55) for a in reversed(arc)], GREEN)
        for k in range(7):
            a = math.pi * (1.15 - 1.3 * k / 6)
            p.stroke([(gx + math.cos(a) * gr * .74, gy - math.sin(a) * gr * .74), (gx + math.cos(a) * gr * .9, gy - math.sin(a) * gr * .9)],
                     2.5, amp=0)
        p.poly([(gx + math.cos(math.pi * (1.15 - 1.3 * f)) * gr * .9, gy - math.sin(math.pi * (1.15 - 1.3 * f)) * gr * .9)
                for f in (.8, .9, 1.0)] + [(gx, gy)], RED if color != RED else (250, 200, 60))
        a = math.pi * (1.15 - 1.3 * max(0.0, min(1.0, pressure)))
        p.stroke([(gx, gy), (gx + math.cos(a) * gr * .78, gy - math.sin(a) * gr * .78)], max(3, gr * .08), amp=0)
        p.poly(ellipse(gx, gy, gr * .1, gr * .1, n=12), INK)
        for side in (-1, 1):
            hx = cx + side * w * .3
            p.shape(rrect(hx - w * .07, top + h * .36, hx + w * .07, top + h * .44, w * .02), CHROME, w=4, amp=.3)
            p.limb([(hx + side * w * .02, top + h * .4), (hx + side * w * .2, top + h * .37)], w * .025, DARK, 3)
            p.shape([(hx - w * .04, top + h * .44), (hx + w * .04, top + h * .44), (hx + w * .025, top + h * .5), (hx - w * .025, top + h * .5)],
                    CHROME_D, w=3.5, amp=.2)
        p.shape(rrect(x0 + w * .08, top + h * .06, x0 + w * .2, top + h * .1, 3), dark, w=0)
        p.shape(rrect(x1 - w * .2, top + h * .06, x1 - w * .08, top + h * .1, 3), dark, w=0)
        if cup:
            for side in (-1, 1):
                hx = cx + side * w * .3; cb = top + h * .62
                p.shape([(hx - w * .07, cb - h * .1), (hx + w * .07, cb - h * .1), (hx + w * .055, cb), (hx - w * .055, cb)],
                        CERAMIC, w=4, amp=.3)
                p.stroke([(hx, top + h * .5), (hx, cb - h * .1)], 3, COFFEE, amp=.2)
        if steam:
            for k in (-1, 1):
                x = cx + k * w * .46
                p.stroke(spline([(x, top - h * .05), (x + h * .06, top - h * .16), (x - h * .04, top - h * .28),
                                 (x + h * .03, top - h * .38)]), 5, GRAY, amp=.6)

def menu_board(img, cx, cy, w=460, title="MENU", items=(("ESPRESSO", "$2"), ("LATTE", "$3"), ("TO GO", "$4")),
               seed=1):
    """Chalkboard menu in a wooden frame; items = (name, price) pairs written in chalk."""
    rows = max(1, len(items))
    h = w * (.32 + .14 * rows)
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    with Pen(img, (x0 - 20, y0 - 20, x1 + 20, y1 + 20), seed) as p:
        p.shape(rrect(x0, y0, x1, y1, w * .02), WOOD, w=6, amp=.5)
        p.shape(rrect(x0 + w * .05, y0 + w * .05, x1 - w * .05, y1 - w * .05, 4), CHALK, w=4, amp=.3)
        for k in range(4):
            p.stroke([(x0 + w * (.12 + k * .21), y0 + w * .09), (x0 + w * (.22 + k * .21), y0 + w * .08)], 2, CHALK_D, amp=.4)
        if title: p.text(str(title), cx, y0 + w * .16, w * .085, fill=(250, 246, 230), warp=1)
        p.stroke([(cx - w * .2, y0 + w * .23), (cx + w * .2, y0 + w * .23)], 3, (240, 220, 160), amp=.5)
        for k, (name, price) in enumerate(items):
            yy = y0 + w * (.33 + .14 * k)
            fs = min(w * .055, w * .55 / max(1, len(str(name))) * 1.6)
            p.text(str(name), x0 + w * .34, yy, fs, fill=(244, 244, 236), warp=.8)
            p.stroke([(x0 + w * .58, yy + fs * .3), (x0 + w * .7, yy + fs * .3)], 2, (180, 186, 180), amp=.3)
            p.text(str(price), x0 + w * .8, yy, w * .06, fill=(250, 214, 110), warp=.8)

def cafe_counter(img, cx, base, w=900, h=300, color=WOOD, top=CERAMIC, seed=1):
    """Coffee shop counter: light top and a wooden front with planks (put cups and machines at base - h)."""
    x0, x1, ty = cx - w / 2, cx + w / 2, base - h
    with Pen(img, (x0 - 30, ty - 40, x1 + 30, base + 10), seed) as p:
        front = [(x0, ty + h * .1), (x1, ty + h * .1), (x1, base), (x0, base)]
        p.shape(front, color, w=6, amp=.6)
        with p.clip(front):
            k = 1
            while x0 + k * w * .12 < x1:
                xx = x0 + k * w * .12
                p.stroke([(xx, ty + h * .12), (xx, base)], 3, WOOD_D, amp=.3); k += 1
        p.stroke(front, 6, amp=.6, closed=True)
        p.shape(rrect(x0 - 24, ty - 6, x1 + 24, ty + h * .1, 6), top, w=6, amp=.5)

def barista(img, x, y, s=1.0, mood="smile", arms=("down", "offer"), look=0.0, color=GREEN, apron=APRON, held="cup",
            cap=True, shadow=False, seed=1):
    """doodle as a barista: t-shirt (color), long apron with a pocket and a cap; held = cup/espresso/None (right hand)."""
    P = lambda dx, dy: (x + dx * s, y + dy * s)

    def dress(p, a):
        for side in (-1, 1):
            p.limb([P(18 * side, -248), P(25 * side + look * 6, -125), P(29 * side, -26)], 24 * s, (60, 60, 66), 4 * s)
        bib = [P(-30, -400), P(30, -400), P(34, -262), P(58, -250), P(64, -110), P(-64, -110), P(-58, -250), P(-34, -262)]
        p.shape(bib, apron, w=6 * s, amp=.6)
        for side in (-1, 1): p.stroke([P(30 * side, -400), P(40 * side, -418)], 4 * s, APRON_D, amp=.2)
        p.stroke([P(-56, -262), P(56, -262)], 4 * s, APRON_D, amp=.3)
        p.shape(rrect(*P(-26, -228), *P(26, -180), 3 * s), apron, w=3.5 * s, amp=.2)
        p.stroke([P(10, -236), P(12, -206)], 3 * s, (230, 230, 230), amp=.1)

    def hat(p, a):
        if not cap: return
        (hx, hy), r = a["head"], a["head_r"]
        dome = spline([(hx - r * 1.0, hy - r * .3), (hx - r * .8, hy - r * .9), (hx, hy - r * 1.08), (hx + r * .8, hy - r * .9),
                       (hx + r * 1.0, hy - r * .3)])
        p.shape(dome, apron, w=5 * s, amp=.4)
        d = 1 if look >= 0 else -1
        p.shape(spline([(hx + d * r * .2, hy - r * .36), (hx + d * r * 1.45, hy - r * .4), (hx + d * r * 1.4, hy - r * .26),
                        (hx + d * r * .2, hy - r * .22)], closed=True), APRON_D, w=4 * s, amp=.3)

    def extras(p, a):
        for side in (-1, 1):
            d = look or side
            p.shape(spline([P(30 * side - 18 * d, -2), P(30 * side - 16 * d, -24), P(30 * side + 8 * d, -26),
                            P(30 * side + 34 * d, -12), P(30 * side + 36 * d, -2)], closed=True), DARK, w=4.5 * s, amp=.4)

    a = doodle(img, x, y, s, outfit="tshirt", color=color, mood=mood, arms=arms, look=look, dress=dress, hat=hat,
               extras=extras, shadow=shadow, seed=seed)
    if held:
        gx, gy = a["hand_r"]
        ch = 130 * s
        with Pen(img, (gx - ch, gy - ch * 1.6, gx + ch, gy + ch * .6), seed + 3) as p:
            if held == "espresso":
                p.shape(ellipse(gx, gy - ch * .05, ch * .5, ch * .07, n=28), CERAMIC, w=4 * s, amp=.3)
                p.shape([(gx - ch * .3, gy - ch * .5), (gx + ch * .3, gy - ch * .5), (gx + ch * .2, gy - ch * .1), (gx - ch * .2, gy - ch * .1)],
                        CERAMIC, w=4.5 * s, amp=.3)
            else:
                _paper_cup(p, gx, gy + ch * .25, ch, WOOD, None, steam=False)
            p.shape(ellipse(gx, gy, 14 * s, 14 * s, n=20), WHITE, w=5 * s, amp=.6)
    return a

# ---------- background ----------
@lru_cache(maxsize=2)
def _cafe():
    img = grad(*CAFE_WALL)
    with Pen(img, (0, 0, W, H), seed=21) as p:
        band_t, band_b = H * .5, H * .64
        p.poly([(-10, band_t), (W + 10, band_t), (W + 10, band_b), (-10, band_b)], TILE)
        for r in range(4):
            yy = band_t + (band_b - band_t) * r / 4
            p.stroke([(-10, yy), (W + 10, yy)], 2.5, (214, 200, 172), amp=.4, taper=False)
            off = 45 if r % 2 else 0
            for k in range(13):
                xx = off + k * 90
                p.stroke([(xx, yy + 4), (xx, yy + (band_b - band_t) / 4 - 4)], 2, (214, 200, 172), amp=.2)
        p.stroke([(-10, band_b), (W + 10, band_b)], 4, (190, 170, 140), amp=.8, taper=False)
        fy = FLOOR - 40                                             # wooden floor
        p.poly([(-10, fy), (W + 10, fy), (W + 10, H + 10), (-10, H + 10)], CAFE_FLOOR)
        for k in range(1, 12):
            yy = fy + k * k * 7
            if yy < H: p.stroke([(-10, yy), (W + 10, yy)], 2.5, CAFE_FLOOR_D, amp=.5, taper=False)
        p.stroke([(-10, fy), (W + 10, fy)], 5, CAFE_FLOOR_D, amp=.8, taper=False)
        sy = H * .2
        for sx in (W * .08, W * .62):
            p.shape(rrect(sx, sy, sx + W * .3, sy + 18, 4), WOOD, w=4, amp=.4)
            for k in range(3):
                jx = sx + W * (.05 + k * .1); jb = sy
                p.shape(rrect(jx - 26, jb - 86, jx + 26, jb, 8), GLASS, w=3.5, amp=.3)
                p.poly(rrect(jx - 22, jb - 50, jx + 22, jb - 4, 6), BEAN if k != 1 else CREMA)
                p.shape(rrect(jx - 20, jb - 100, jx + 20, jb - 84, 4), WOOD_D, w=3, amp=.2)
        for lx in (W * .3, W * .7):
            p.stroke([(lx, -10), (lx, H * .07)], 3, (90, 80, 70), amp=.2)
            p.shape([(lx - 50, H * .1), (lx - 16, H * .07), (lx + 16, H * .07), (lx + 50, H * .1)], (60, 70, 66), w=4, amp=.3)
            p.poly(ellipse(lx, H * .1 + 6, 22, 9, n=16), (255, 230, 150))
    return img

def cafe_bg(t=0.0):
    """Coffee shop on warm cream paper: tiled band, two shelves with coffee jars, pendant lamps and a wooden floor from
    FLOOR - 40 down. Put cafe_counter at FLOOR in front of it."""
    return _cafe().copy()

from . import cache_pieces
cache_pieces(globals())
