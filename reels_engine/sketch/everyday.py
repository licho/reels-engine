"""Sketch-style everyday objects: coffee to go, car, motorbike, bicycle, house, building, tree, cloud, sun, phone,
laptop, TV, shopping bag and cart, credit card, coin, piggy bank, light bulb, clock, gift, burger, pizza slice and
receipt. All take the image (img) and a 'seed'.

Things that stand on the floor take (cx, base) = bottom center; floating things take their center (cx, cy)."""
import math
from . import (Pen, INK, WHITE, SHADE, RED, GREEN, GREEN_D, GLASS, GLASS_D, WOOD, WOOD_D, BLUE, ellipse, rrect,
               rotated, spline)

YELLOW = (250, 205, 60)
GOLD, GOLD_D = (240, 190, 50), (190, 135, 20)
GRAY, GRAY_L, DARK = (150, 150, 155), (215, 215, 220), (62, 62, 68)
TIRE, HUB = (58, 58, 64), (200, 200, 206)
PAPER_BAG = (214, 170, 110)
BRICK = (196, 86, 64)
WALL = (244, 226, 190)
LEAF, LEAF_D = (110, 180, 80), (60, 125, 50)
PINK, PINK_D = (244, 170, 185), (200, 110, 130)
BUN, BUN_D = (232, 165, 80), (190, 120, 50)
MEAT = (120, 70, 45)

def bumpy(circles, n=96):
    """Outline of a group of overlapping circles [(x, y, r)…], seen from their middle (clouds, tree tops, bushes)."""
    cx = sum(c[0] for c in circles) / len(circles); cy = sum(c[1] for c in circles) / len(circles)
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n; dx, dy = math.cos(a), math.sin(a); best = 0
        for x, y, r in circles:
            ox, oy = x - cx, y - cy
            proj = ox * dx + oy * dy; disc = r * r - (ox * ox + oy * oy - proj * proj)
            if disc >= 0: best = max(best, proj + math.sqrt(disc))
        pts.append((cx + dx * best, cy + dy * best))
    return pts

def _wheel(p, cx, cy, r, w=5):
    p.shape(ellipse(cx, cy, r, r, n=40), TIRE, w=w, amp=.8)
    p.shape(ellipse(cx, cy, r * .5, r * .5, n=28), HUB, w=w * .7, amp=.5)
    p.poly(ellipse(cx, cy, r * .14, r * .14, n=12), DARK)

# ---------- food and drink ----------
def coffee_cup(img, cx, base, h=170, sleeve=WOOD, steam=True, seed=1):
    """Coffee to go: paper cup with lid, cardboard sleeve and optional steam."""
    wt, wb, top = h * .31, h * .23, base - h * .82
    with Pen(img, (cx - h * .45, base - h * 1.45, cx + h * .45, base + h * .1), seed) as p:
        p.blob(cx, base, h * .32, h * .04, SHADE)
        at = lambda f: (wb + (wt - wb) * f)                  # half width at a height fraction (0 = base)
        p.shape([(cx - wt, top), (cx + wt, top), (cx + wb, base), (cx - wb, base)], WHITE, w=5)
        f0, f1 = .3, .68
        y0, y1 = base - h * .82 * f1, base - h * .82 * f0
        band = [(cx - at(f1), y0), (cx + at(f1), y0), (cx + at(f0), y1), (cx - at(f0), y1)]
        p.shape(band, sleeve, w=4.5)
        p.shape(ellipse(cx, (y0 + y1) / 2, h * .07, h * .07, n=20), WHITE, w=3, amp=.4)
        p.shape(rrect(cx - wt * 1.12, top - h * .09, cx + wt * 1.12, top + h * .01, h * .03), GRAY_L, w=5, amp=.8)
        p.shape(rrect(cx - wt * .8, top - h * .16, cx + wt * .8, top - h * .08, h * .03), GRAY_L, w=4.5, amp=.6)
        if steam:
            for dx in (-.12, .1):
                x = cx + dx * h
                p.stroke(spline([(x, top - h * .2), (x + h * .05, top - h * .3), (x - h * .04, top - h * .42),
                                 (x + h * .03, top - h * .55)]), 4, GRAY, amp=.6)

def burger(img, cx, base, w=200, seed=1):
    """Burger: buns with sesame, lettuce, cheese and meat."""
    h = w * .7
    with Pen(img, (cx - w * .65, base - h * 1.1, cx + w * .65, base + w * .08), seed) as p:
        p.blob(cx, base, w * .55, w * .06, SHADE)
        p.shape(rrect(cx - w * .48, base - h * .2, cx + w * .48, base, h * .08), BUN, w=5)
        p.shape(rrect(cx - w * .52, base - h * .38, cx + w * .52, base - h * .18, h * .1), MEAT, w=5)
        p.shape([(cx - w * .5, base - h * .4), (cx + w * .5, base - h * .4), (cx + w * .38, base - h * .28),
                 (cx + w * .25, base - h * .4), (cx - w * .1, base - h * .4), (cx - w * .2, base - h * .26),
                 (cx - w * .32, base - h * .4)], YELLOW, w=4)
        lettuce = [(cx - w * .54 + w * .108 * k, base - h * (.46 if k % 2 else .38)) for k in range(11)]
        p.shape(lettuce + [(cx + w * .5, base - h * .5), (cx - w * .5, base - h * .5)], LEAF, w=4, smooth=True)
        dome = spline([(cx - w * .5, base - h * .5), (cx - w * .42, base - h * .85), (cx, base - h), (cx + w * .42, base - h * .85),
                       (cx + w * .5, base - h * .5)])
        p.shape(dome, BUN, w=5)
        for k in range(6):
            sx, sy = cx + w * (-.3 + .12 * k), base - h * (.75 + .1 * math.sin(k * 1.7))
            p.shape(ellipse(sx, sy, w * .025, w * .014, rot=.4 * (k % 3 - 1), n=10), WHITE, w=2, amp=.2)

def pizza_slice(img, cx, cy, h=200, ang=0.0, seed=1):
    """Pizza slice pointing down, with crust and pepperoni; ang = turn in radians."""
    w = h * .8
    tri = rotated([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx, cy + h / 2)], cx, cy, ang)
    crust = rotated(rrect(cx - w * .56, cy - h * .62, cx + w * .56, cy - h * .45, h * .07), cx, cy, ang)
    r = h * .7
    with Pen(img, (cx - r, cy - r, cx + r, cy + r), seed) as p:
        p.shape(tri, YELLOW, w=5)
        for fx, fy in ((-.18, -.3), (.15, -.25), (0, -.02), (-.05, .22)):
            (px, py), = rotated([(cx + fx * w, cy + fy * h)], cx, cy, ang)
            p.shape(ellipse(px, py, h * .07, h * .07, n=20), RED, w=3, amp=.4)
        p.shape(crust, BUN, w=5)

# ---------- vehicles ----------
def car(img, cx, base, w=420, color=BLUE, seed=1):
    """Small car seen from the side, facing right."""
    r = w * .11
    yb, yt = base - r * .9, base - r - w * .17
    with Pen(img, (cx - w * .6, base - w * .5, cx + w * .6, base + w * .08), seed) as p:
        p.blob(cx, base, w * .52, w * .04, SHADE)
        cab = [(cx - w * .32, yt + 4), (cx - w * .22, yt - w * .15), (cx + w * .12, yt - w * .15), (cx + w * .24, yt + 4)]
        p.shape(cab, color, w=6)
        p.shape([(cx - w * .27, yt), (cx - w * .2, yt - w * .12), (cx - w * .06, yt - w * .12), (cx - w * .06, yt)], GLASS, w=4, amp=.6)
        p.shape([(cx - w * .02, yt), (cx - w * .02, yt - w * .12), (cx + w * .1, yt - w * .12), (cx + w * .19, yt)], GLASS, w=4, amp=.6)
        body = [(cx - w * .5, yb), (cx - w * .5, yt + w * .03), (cx - w * .44, yt), (cx + w * .38, yt + w * .01),
                (cx + w * .5, yt + w * .06), (cx + w * .5, yb)]
        p.shape(body, color, w=6, smooth=False)
        p.stroke([(cx - w * .04, yt + 4), (cx - w * .04, yb - 4)], 4, amp=.5)
        p.stroke([(cx + w * .02, yt + w * .05), (cx + w * .08, yt + w * .05)], 5, amp=.3)
        p.shape(ellipse(cx + w * .47, yt + w * .06, w * .03, w * .022, n=14), YELLOW, w=3, amp=.3)
        p.shape(ellipse(cx - w * .48, yt + w * .05, w * .018, w * .025, n=14), RED, w=3, amp=.3)
        for wx in (cx - w * .3, cx + w * .3): _wheel(p, wx, base - r, r)

def motorbike(img, cx, base, w=360, color=RED, seed=1):
    """Motorbike seen from the side, facing right."""
    r = w * .15
    bx, fx, cyw = cx - w * .34, cx + w * .34, base - r
    arc = lambda x, a0, a1: [(x + math.cos(math.radians(a)) * r * 1.2, cyw + math.sin(math.radians(a)) * r * 1.2)
                             for a in range(a0, a1 + 1, 10)]
    with Pen(img, (cx - w * .6, base - w * .65, cx + w * .6, base + w * .08), seed) as p:
        p.blob(cx, base, w * .52, w * .05, SHADE)
        for x in (bx, fx): _wheel(p, x, cyw, r)
        p.limb([(bx, cyw), (cx - w * .05, cyw - r * .45)], 9, DARK, 3)                          # swingarm
        p.limb([(cx, cyw - r * .2), (cx - w * .2, cyw - r * .3), (bx + r * .1, cyw - r * .55)], 12, GRAY, 3.5)   # exhaust
        p.shape(rrect(cx - w * .1, cyw - r * 1.0, cx + w * .12, cyw - r * .1, 8), GRAY, w=4.5)   # engine
        p.shape([(cx - w * .42, cyw - r * 1.25), (cx - w * .1, cyw - r * 1.35), (cx + w * .04, cyw - r * 1.8),
                 (cx + w * .2, cyw - r * 1.75), (cx + w * .18, cyw - r * 1.0), (cx - w * .05, cyw - r * .95),
                 (cx - w * .3, cyw - r * .98)], color, w=5, smooth=True)                         # body and tank
        p.shape([(cx - w * .38, cyw - r * 1.32), (cx - w * .06, cyw - r * 1.45), (cx - w * .03, cyw - r * 1.25),
                 (cx - w * .35, cyw - r * 1.15)], DARK, w=4)                                       # seat
        p.stroke(arc(fx, -165, -30), 7, color, amp=.4, taper=False)                               # fender
        p.limb([(fx, cyw), (cx + w * .22, cyw - r * 2.15)], 9, GRAY, 3)                           # fork
        p.stroke([(cx + w * .15, cyw - r * 2.3), (cx + w * .23, cyw - r * 2.15), (cx + w * .3, cyw - r * 2.2)], 8, amp=.4)
        p.shape(ellipse(cx + w * .27, cyw - r * 1.75, w * .035, w * .045, n=16), YELLOW, w=3.5, amp=.3)

def bicycle(img, cx, base, w=320, color=GREEN, seed=1):
    """Bicycle seen from the side, facing right."""
    r = w * .2
    bx, fx, cyw = cx - w * .3, cx + w * .3, base - r
    with Pen(img, (cx - w * .58, base - w * .62, cx + w * .58, base + w * .08), seed) as p:
        p.blob(cx, base, w * .5, w * .05, SHADE)
        for x in (bx, fx):
            p.shape(ellipse(x, cyw, r, r, n=40), None, w=7, amp=.8)
            p.poly(ellipse(x, cyw, r * .12, r * .12, n=12), DARK)
        crank, seat_t, head = (cx - w * .02, cyw), (cx - w * .1, cyw - r * 1.25), (cx + w * .2, cyw - r * 1.15)
        for a, b in ((bx, crank), (crank, seat_t), (seat_t, (bx, cyw)), (seat_t, head), (head, crank)):
            p.stroke([a if isinstance(a, tuple) else (a, cyw), b], 9, color, amp=.5)
        p.stroke([head, (fx, cyw)], 9, color, amp=.5)
        p.stroke([head, (head[0] - w * .02, head[1] - r * .3), (head[0] + w * .08, head[1] - r * .35)], 6, amp=.4)
        p.shape(rrect(seat_t[0] - w * .08, seat_t[1] - r * .25, seat_t[0] + w * .06, seat_t[1] - r * .1, 6), DARK, w=4)
        p.stroke([seat_t, (seat_t[0] - w * .01, seat_t[1] - r * .15)], 6, amp=.3)
        p.shape(ellipse(crank[0], crank[1], r * .18, r * .18, n=16), GRAY, w=4, amp=.3)

# ---------- places and nature ----------
def house(img, cx, base, w=360, wall=WALL, roof=BRICK, seed=1):
    """Little house with pitched roof, chimney, door and two windows."""
    h = w * .6
    top = base - h
    with Pen(img, (cx - w * .65, base - w * 1.15, cx + w * .65, base + w * .08), seed) as p:
        p.blob(cx, base, w * .6, w * .05, SHADE)
        p.shape(rrect(cx + w * .2, top - w * .42, cx + w * .32, top - w * .1, 4), BRICK, w=5)
        p.shape([(cx - w / 2, base), (cx - w / 2, top), (cx + w / 2, top), (cx + w / 2, base)], wall, w=6)
        roof_pts = [(cx - w * .6, top + w * .02), (cx, top - w * .45), (cx + w * .6, top + w * .02)]
        p.shape(roof_pts, roof, w=6)
        p.hatch(roof_pts, tuple(int(v * .78) for v in roof), gap=20, ang=-.6, w=3)
        p.stroke(roof_pts, 6, amp=1, closed=True)
        p.shape(rrect(cx - w * .08, base - h * .62, cx + w * .08, base, 6), WOOD, w=5)
        p.poly(ellipse(cx + w * .045, base - h * .3, w * .012, w * .012, n=10), INK)
        for wx in (cx - w * .3, cx + w * .3):
            p.shape(rrect(wx - w * .1, top + h * .22, wx + w * .1, top + h * .55, 4), GLASS, w=5)
            p.stroke([(wx, top + h * .22), (wx, top + h * .55)], 4, amp=.3)
            p.stroke([(wx - w * .1, top + h * .385), (wx + w * .1, top + h * .385)], 4, amp=.3)

def building(img, cx, base, w=240, h=520, color=(205, 210, 220), seed=1):
    """Office/apartment building with a grid of windows and a door."""
    top = base - h
    cols, rows = 3, max(2, int(h / (w * .3)))
    with Pen(img, (cx - w * .65, top - 20, cx + w * .65, base + w * .08), seed) as p:
        p.blob(cx, base, w * .6, w * .05, SHADE)
        p.shape([(cx - w / 2, base), (cx - w / 2, top), (cx + w / 2, top), (cx + w / 2, base)], color, w=6)
        p.shape(rrect(cx - w * .54, top - 14, cx + w * .54, top + 4, 4), tuple(int(v * .8) for v in color), w=5)
        ww, wh = w * .18, h / rows * .45
        for r in range(rows - 1):
            for c in range(cols):
                x = cx - w * .32 + c * w * .32; y = top + h / rows * (r + .4)
                p.shape(rrect(x - ww / 2, y, x + ww / 2, y + wh, 3), GLASS, w=4, amp=.5)
        p.shape(rrect(cx - w * .12, base - h / rows * .8, cx + w * .12, base, 4), GLASS_D, w=5)
        p.stroke([(cx, base - h / rows * .8), (cx, base)], 4, amp=.3)

def tree(img, cx, base, h=420, leaves=LEAF, seed=1):
    """Round tree: brown trunk and a bumpy hatched top."""
    r = h * .22
    with Pen(img, (cx - h * .5, base - h * 1.05, cx + h * .5, base + h * .06), seed) as p:
        p.blob(cx, base, h * .3, h * .035, SHADE)
        p.shape([(cx - h * .05, base), (cx - h * .035, base - h * .5), (cx + h * .035, base - h * .5), (cx + h * .05, base)], WOOD, w=6)
        cy = base - h + r * 1.3
        top = bumpy([(cx, cy - r * .3, r), (cx - r * .8, cy + r * .2, r * .8), (cx + r * .8, cy + r * .15, r * .85),
                     (cx - r * .3, cy + r * .6, r * .75), (cx + r * .35, cy + r * .6, r * .7)])
        p.poly(p.wobble(top, .8, True), leaves)
        p.hatch(top, tuple(int(v * .75) for v in leaves), gap=26, ang=-1.1, w=3)
        p.stroke(top, 6, amp=1.2, closed=True)

def cloud(img, cx, cy, w=260, color=WHITE, seed=1):
    """Fluffy cloud centered on (cx, cy)."""
    r = w * .2
    with Pen(img, (cx - w * .65, cy - w * .5, cx + w * .65, cy + w * .35), seed) as p:
        pts = bumpy([(cx - r * 1.3, cy + r * .2, r * .8), (cx - r * .3, cy - r * .3, r * 1.1), (cx + r * .8, cy - r * .1, r * .95),
                     (cx + r * 1.5, cy + r * .3, r * .7), (cx, cy + r * .4, r * .9)])
        p.shape(pts, color, w=5, amp=1)

def sun(img, cx, cy, r=70, seed=1):
    """Sun: yellow disc with short rays."""
    with Pen(img, (cx - r * 1.8, cy - r * 1.8, cx + r * 1.8, cy + r * 1.8), seed) as p:
        for k in range(10):
            a = 2 * math.pi * k / 10
            p.stroke([(cx + math.cos(a) * r * 1.25, cy + math.sin(a) * r * 1.25),
                      (cx + math.cos(a) * r * 1.6, cy + math.sin(a) * r * 1.6)], 6, GOLD_D, amp=.4)
        p.shape(ellipse(cx, cy, r, r, n=48), YELLOW, w=6)

# ---------- gadgets ----------
def phone(img, cx, cy, h=260, screen=GLASS, ang=0.0, seed=1):
    """Smartphone seen from the front; screen = screen color; ang = tilt in radians."""
    w = h * .5
    R = lambda pts: rotated(pts, cx, cy, ang)
    with Pen(img, (cx - h * .6, cy - h * .6, cx + h * .6, cy + h * .6), seed) as p:
        p.shape(R(rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, w * .16)), DARK, w=5)
        p.shape(R(rrect(cx - w * .42, cy - h * .43, cx + w * .42, cy + h * .43, w * .08)), screen, w=0)
        p.stroke(R([(cx - w * .12, cy - h * .465), (cx + w * .12, cy - h * .465)]), 4, GRAY, amp=.2)
        p.stroke(R([(cx - w * .14, cy + h * .465), (cx + w * .14, cy + h * .465)]), 4, GRAY, amp=.2)

def laptop(img, cx, base, w=320, screen=GLASS, seed=1):
    """Open laptop seen from the front, sitting on y=base."""
    sh = w * .62
    with Pen(img, (cx - w * .65, base - sh - w * .2, cx + w * .65, base + w * .06), seed) as p:
        p.shape(rrect(cx - w * .45, base - sh - w * .08, cx + w * .45, base - w * .08, 10), DARK, w=5)
        p.shape(rrect(cx - w * .4, base - sh - w * .04, cx + w * .4, base - w * .12, 4), screen, w=3, amp=.5)
        p.shape([(cx - w * .45, base - w * .08), (cx + w * .45, base - w * .08), (cx + w * .55, base), (cx - w * .55, base)], GRAY_L, w=5)
        p.stroke([(cx - w * .1, base - w * .03), (cx + w * .1, base - w * .03)], 4, GRAY, amp=.2)

def tv(img, cx, base, w=320, screen=GLASS, seed=1):
    """Flat TV on a small stand, sitting on y=base."""
    h = w * .6
    top = base - h - w * .12
    with Pen(img, (cx - w * .6, top - 20, cx + w * .6, base + w * .06), seed) as p:
        p.shape([(cx - w * .04, top + h), (cx + w * .04, top + h), (cx + w * .05, base - w * .03), (cx - w * .05, base - w * .03)], DARK, w=4)
        p.shape(rrect(cx - w * .22, base - w * .04, cx + w * .22, base, 6), DARK, w=4)
        p.shape(rrect(cx - w / 2, top, cx + w / 2, top + h, 8), DARK, w=5)
        p.shape(rrect(cx - w * .46, top + w * .04, cx + w * .46, top + h - w * .04, 4), screen, w=3, amp=.5)
        p.stroke([(cx - w * .35, top + h * .25), (cx - w * .25, top + h * .15)], 6, WHITE, amp=.3)   # glint

def light_bulb(img, cx, cy, h=200, on=True, seed=1):
    """Light bulb (an idea!); on = yellow glass with rays."""
    r = h * .3
    gy = cy - h * .12
    with Pen(img, (cx - h * .75, cy - h * .9, cx + h * .75, cy + h * .6), seed) as p:
        if on:
            for k in range(7):
                a = math.pi * (1.05 + .9 * k / 6)
                p.stroke([(cx + math.cos(a) * r * 1.35, gy + math.sin(a) * r * 1.35),
                          (cx + math.cos(a) * r * 1.8, gy + math.sin(a) * r * 1.8)], 6, GOLD_D, amp=.3)
        glass = spline([(cx - r * .45, cy + h * .22), (cx - r * .55, cy + h * .08), (cx - r, gy), (cx - r * .7, gy - r * .75),
                        (cx, gy - r), (cx + r * .7, gy - r * .75), (cx + r, gy), (cx + r * .55, cy + h * .08), (cx + r * .45, cy + h * .22)])
        p.shape(glass, YELLOW if on else WHITE, w=6)
        p.stroke(spline([(cx - r * .25, cy + h * .2), (cx - r * .25, gy + r * .2), (cx - r * .1, gy), (cx + r * .1, gy),
                         (cx + r * .25, gy + r * .2), (cx + r * .25, cy + h * .2)]), 3.5, GOLD_D if on else GRAY, amp=.3)
        p.shape(rrect(cx - r * .5, cy + h * .22, cx + r * .5, cy + h * .42, 6), GRAY, w=5)
        for k in (1, 2): p.stroke([(cx - r * .5, cy + h * (.22 + .065 * k)), (cx + r * .5, cy + h * (.22 + .065 * k))], 3, amp=.2)
        p.shape(ellipse(cx, cy + h * .45, r * .2, r * .12, n=16), DARK, w=3, amp=.2)

def clock(img, cx, cy, r=90, hour=3, minute=0, seed=1):
    """Wall clock showing hour:minute."""
    with Pen(img, (cx - r * 1.2, cy - r * 1.2, cx + r * 1.2, cy + r * 1.2), seed) as p:
        p.shape(ellipse(cx, cy, r, r, n=56), WHITE, w=8)
        for k in range(12):
            a = 2 * math.pi * k / 12; L = .16 if k % 3 == 0 else .08
            p.stroke([(cx + math.sin(a) * r * .82, cy - math.cos(a) * r * .82),
                      (cx + math.sin(a) * r * (.82 - L), cy - math.cos(a) * r * (.82 - L))], 4, amp=.2)
        ah = 2 * math.pi * ((hour % 12) + minute / 60) / 12; am = 2 * math.pi * minute / 60
        p.stroke([(cx, cy), (cx + math.sin(ah) * r * .45, cy - math.cos(ah) * r * .45)], 8, amp=.3)
        p.stroke([(cx, cy), (cx + math.sin(am) * r * .68, cy - math.cos(am) * r * .68)], 5, amp=.3)
        p.poly(ellipse(cx, cy, r * .07, r * .07, n=12), INK)

# ---------- shopping and money ----------
def shopping_bag(img, cx, base, h=200, color=PAPER_BAG, seed=1):
    """Paper shopping bag with handles."""
    w = h * .8
    top = base - h * .78
    with Pen(img, (cx - w * .65, base - h * 1.05, cx + w * .65, base + h * .06), seed) as p:
        p.blob(cx, base, w * .55, h * .04, SHADE)
        p.stroke(spline([(cx - w * .2, top + 4), (cx - w * .18, top - h * .2), (cx + w * .18, top - h * .2), (cx + w * .2, top + 4)]), 6, amp=.6)
        p.shape([(cx - w * .45, top), (cx + w * .45, top), (cx + w * .5, base), (cx - w * .5, base)], color, w=5)
        p.stroke([(cx - w * .45, top + h * .08), (cx + w * .45, top + h * .08)], 3, tuple(int(v * .78) for v in color), amp=.4)

def shopping_cart(img, cx, base, w=260, color=GRAY_L, seed=1):
    """Supermarket cart seen from the side, handle on the left."""
    r = w * .06
    top, low = base - w * .62, base - w * .2
    with Pen(img, (cx - w * .65, base - w * .8, cx + w * .65, base + w * .06), seed) as p:
        basket = [(cx - w * .38, top), (cx + w * .48, top), (cx + w * .36, low), (cx - w * .3, low)]
        p.poly(p.wobble(basket, .6, True), color)
        p.hatch(basket, GRAY, gap=22, ang=0, w=2.5); p.hatch(basket, GRAY, gap=22, ang=1.57, w=2.5)
        p.stroke(basket, 6, amp=.8, closed=True)
        p.stroke([(cx - w * .52, top - w * .1), (cx - w * .4, top - w * .1), (cx - w * .3, low), (cx - w * .3, low + w * .08),
                  (cx + w * .36, low + w * .08)], 6, amp=.6)
        for x in (cx - w * .25, cx + w * .3): _wheel(p, x, base - r, r, w=4)

def credit_card(img, cx, cy, w=220, color=BLUE, ang=0.0, seed=1):
    """Bank card with a gold chip; ang = tilt in radians."""
    h = w * .63
    R = lambda pts: rotated(pts, cx, cy, ang)
    with Pen(img, (cx - w * .65, cy - w * .65, cx + w * .65, cy + w * .65), seed) as p:
        p.shape(R(rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, w * .07)), color, w=5)
        p.shape(R(rrect(cx - w * .38, cy - h * .2, cx - w * .2, cy + h * .02, 4)), GOLD, w=3, amp=.3)
        for k in range(4):
            x = cx - w * .38 + k * w * .19
            p.stroke(R([(x, cy + h * .25), (x + w * .14, cy + h * .25)]), 4, WHITE, amp=.2)

def coin(img, cx, cy, r=50, label="$", seed=1):
    """Gold coin with a symbol in the middle."""
    with Pen(img, (cx - r * 1.2, cy - r * 1.2, cx + r * 1.2, cy + r * 1.2), seed) as p:
        p.shape(ellipse(cx, cy, r, r, n=40), GOLD, w=max(3, r * .08), amp=.6)
        p.stroke(ellipse(cx, cy, r * .75, r * .75, n=36), max(2, r * .05), GOLD_D, amp=.4, closed=True)
        if label: p.text(label, cx, cy, r * .9, fill=GOLD_D, warp=0)

def piggy_bank(img, cx, base, w=240, color=PINK, seed=1):
    """Piggy bank facing right, with a coin slot."""
    h = w * .62
    cy = base - h * .55
    dark = tuple(int(v * .8) for v in color)
    with Pen(img, (cx - w * .65, base - h * 1.2, cx + w * .65, base + w * .06), seed) as p:
        p.blob(cx, base, w * .45, w * .05, SHADE)
        for lx in (-.28, -.12, .14, .3):
            p.shape(rrect(cx + w * lx - w * .05, cy + h * .2, cx + w * lx + w * .05, base, 5), dark, w=4)
        p.stroke(spline([(cx - w * .44, cy - h * .05), (cx - w * .5, cy - h * .14), (cx - w * .46, cy - h * .2),
                         (cx - w * .52, cy - h * .22)]), 4, amp=.3)
        p.shape(ellipse(cx, cy, w * .45, h * .45, n=48), color, w=6)
        p.shape([(cx + w * .1, cy - h * .38), (cx + w * .2, cy - h * .62), (cx + w * .27, cy - h * .32)], dark, w=4)
        p.shape(ellipse(cx + w * .45, cy + h * .02, w * .07, h * .13, n=20), dark, w=4, amp=.4)
        for dy in (-.04, .08): p.poly(ellipse(cx + w * .45, cy + h * dy, w * .012, h * .03, n=8), INK)
        p.poly(ellipse(cx + w * .26, cy - h * .12, w * .02, w * .025, n=10), INK)
        p.stroke([(cx - w * .1, cy - h * .38), (cx + w * .06, cy - h * .4)], 6, amp=.2)

def gift_box(img, cx, base, w=180, color=RED, ribbon=YELLOW, seed=1):
    """Wrapped present with a ribbon and a bow."""
    h = w * .7
    top = base - h
    with Pen(img, (cx - w * .65, top - w * .4, cx + w * .65, base + w * .06), seed) as p:
        p.blob(cx, base, w * .55, w * .05, SHADE)
        p.shape(rrect(cx - w * .45, top + h * .2, cx + w * .45, base, 4), color, w=5)
        p.shape(rrect(cx - w * .5, top, cx + w * .5, top + h * .22, 4), color, w=5)
        p.shape([(cx - w * .07, top), (cx + w * .07, top), (cx + w * .07, base), (cx - w * .07, base)], ribbon, w=4)
        for side in (-1, 1):
            p.shape([(cx, top), (cx + side * w * .3, top - w * .25), (cx + side * w * .32, top - w * .02)], ribbon, w=4, smooth=True)
        p.shape(ellipse(cx, top - w * .02, w * .06, w * .05, n=16), ribbon, w=4, amp=.3)

def receipt(img, cx, cy, h=260, lines=5, total=None, seed=1):
    """Shop receipt with a torn zigzag bottom; total = text at the end ("$25")."""
    w = h * .55
    with Pen(img, (cx - w * .7, cy - h * .6, cx + w * .7, cy + h * .6), seed) as p:
        teeth = 8
        zig = [(cx + w / 2 - w * k / (2 * teeth), cy + h / 2 - (h * .04 if k % 2 else 0)) for k in range(2 * teeth + 1)]
        p.shape([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2)] + zig, WHITE, w=4.5, amp=.6)
        for k in range(lines):
            y = cy - h * .36 + k * h * .1
            p.stroke([(cx - w * .36, y), (cx + w * (.05 if k % 2 else .15), y)], 4, GRAY, amp=.3)
            p.stroke([(cx + w * .22, y), (cx + w * .36, y)], 4, GRAY, amp=.3)
        if total:
            y = cy - h * .36 + lines * h * .1 + h * .04
            p.stroke([(cx - w * .36, y - h * .05), (cx + w * .36, y - h * .05)], 3, amp=.3)
            p.text(total, cx + w * .12, y + h * .03, h * .09, warp=0)
