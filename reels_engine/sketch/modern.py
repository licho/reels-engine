"""Sketch-style 1800s and early 1900s: the doodle dressed as a sultan, a navy admiral, a sailor or a palace guard;
a seaside palace, a steam warship, a flagpole, fire, explosions and smoke, a map pin, and a seaside background;
quack medicine: the doodle as a doctor (top hat, frock coat, spectacles), an apothecary pill bottle, pills, a newspaper.
All take the image (img) and a 'seed'; nothing draws a floor shadow.

    bg = seaside_bg()                                            # shore on the left, sea from SEA_Y down
    palace(bg, 270, SEA_Y + 20, 450, burn=.6, t=c.t)              # scorched and burning
    warship(bg, 800, 1200, 420, flash=1)                         # bow gun firing to the left
    a = sultan(img, 300, FLOOR, .9, mood="smug")

Flags: kind="plain" (one color), "cross" (white with a red cross) or "tricolor" (three horizontal stripes, 'colors')."""
import math
from functools import lru_cache
from . import Pen, INK, WHITE, RED, RED_D, WOOD, WOOD_D, GLASS, ellipse, rrect, rotated, spline
from .everyday import bumpy
from .humans import doodle
from ..core import W, H, grad

PAPER = ((253, 248, 236), (247, 238, 218))           # warm paper
SEA, SEA_D = (196, 224, 238), (120, 170, 205)
SAND, SAND_D = (236, 214, 166), (196, 165, 110)
NAVY, NAVY_D = (40, 52, 90), (26, 34, 62)
GOLD = (240, 190, 60)
CREAM = (246, 238, 218)
STEEL, STEEL_D = (150, 156, 166), (102, 108, 120)
FIRE, FIRE_L = (245, 120, 30), (255, 205, 60)
SMOKE = (150, 148, 150)
BLACK_ROBE = (52, 46, 50)
TURBAN_STRIPE = (190, 50, 50)
SEA_Y = 1000                                         # horizon line of seaside_bg; the shore sits on it

class _Place:
    def __init__(self, x, y, s): self.x, self.y, self.s = x, y, s
    def __call__(self, dx, dy): return (self.x + dx * self.s, self.y + dy * self.s)

def _scale(a):
    x, y = a["feet"]; s = (y - a["chest"][1]) / 360
    return _Place(x, y, s), s

# ---------- characters ----------
def _robe(p, a, color=WHITE, cloak=None):
    P, s = _scale(a)
    p.shape([P(-46, -418), P(46, -418), P(58, -300), P(72, -40), P(-72, -40), P(-58, -300)], color, w=6 * s, amp=.8)
    for k in (-26, 0, 26): p.stroke([P(k, -230), P(k * 1.4, -60)], 2.5 * s, (205, 200, 190), amp=.8)
    if cloak:                                        # open cloak with gold trim, the robe shows in the middle
        for k in (-1, 1):
            p.shape([P(46 * k, -418), P(16 * k, -418), P(22 * k, -40), P(74 * k, -40), P(58 * k, -300)], cloak, w=5 * s, amp=.6)
            p.stroke([P(16 * k, -416), P(22 * k, -42)], 4 * s, GOLD, amp=.4)

def _turban(p, a, color=CREAM, stripe=TURBAN_STRIPE):
    (hx, hy), r = a["head"], a["head_r"]
    cap = ellipse(hx, hy - .72 * r, 1.04 * r, .5 * r, n=40)
    p.poly(p.wobble(cap, .3, True), color)
    with p.clip(ellipse(hx, hy - .72 * r, .98 * r, .45 * r, n=40)):          # stripes stay inside the turban
        for k in (-.3, 0, .3):
            p.stroke(spline([(hx - 1.1 * r, hy - .72 * r + k * r), (hx, hy - .8 * r + k * r * .7), (hx + 1.1 * r, hy - .64 * r + k * r)]),
                     .045 * r, stripe, amp=.4)
    p.stroke(cap, .06 * r, amp=.6, closed=True)

def _full_beard(p, a, color=(36, 30, 30)):
    (hx, hy), r = a["head"], a["head_r"]
    outer = [(hx + math.cos(math.radians(d)) * r * 1.04, hy + math.sin(math.radians(d)) * r * 1.04) for d in range(15, 166, 6)]
    inner = [(hx + math.cos(math.radians(d)) * r * .62, hy + .12 * r + math.sin(math.radians(d)) * r * .58) for d in range(160, 19, -7)]
    p.shape(outer + inner, color, w=.05 * r, amp=.5)

def sultan(img, x, y, s=1.0, mood="smug", arms=("hip", "hip"), look=0.0, robe=WHITE, cloak=BLACK_ROBE, seed=1):
    """Sultan: doodle in a long robe, an open cloak with gold trim, a striped turban and a full black beard."""
    return doodle(img, x, y, s, outfit="tshirt", color=robe, mood=mood, arms=arms, look=look, seed=seed, shadow=False,
                  dress=lambda p, a: _robe(p, a, robe, cloak), hat=_turban, extras=_full_beard)

def _coat(p, a):
    P, s = _scale(a)
    for k in (-1, 1):
        p.shape([P(46 * k, -418), P(12 * k, -418), P(14 * k, -300), P(6 * k, -205), P(56 * k, -205), P(56 * k, -330)], NAVY, w=5 * s, amp=.6)
        for yy in (-370, -330, -290, -250): p.poly(ellipse(*P(26 * k, yy), 4.5 * s, 4.5 * s, n=10), GOLD)

def _officer_cap(p, a):
    (hx, hy), r = a["head"], a["head_r"]
    p.shape([(hx - 1.08 * r, hy - .78 * r), (hx - .9 * r, hy - 1.12 * r), (hx + .9 * r, hy - 1.12 * r), (hx + 1.08 * r, hy - .78 * r)],
            WHITE, w=.06 * r, amp=.5)
    p.shape(rrect(hx - .98 * r, hy - .82 * r, hx + .98 * r, hy - .6 * r, .06 * r), NAVY, w=.05 * r, amp=.4)
    p.shape(ellipse(hx, hy - .71 * r, .14 * r, .1 * r, n=16), GOLD, w=.03 * r, amp=.2)
    p.shape([(hx - .7 * r, hy - .62 * r), (hx + .7 * r, hy - .62 * r), (hx + .45 * r, hy - .48 * r), (hx - .45 * r, hy - .48 * r)],
            NAVY_D, w=.04 * r, amp=.3)

def _moustache(p, a, color=(230, 230, 232)):
    r = a["head_r"]; mx, my = a["mouth"]
    for k in (-1, 1):
        p.shape(spline([(mx, my - .14 * r), (mx + k * .3 * r, my - .2 * r), (mx + k * .42 * r, my - .1 * r), (mx + k * .2 * r, my - .1 * r)],
                       closed=True), color, w=.03 * r, amp=.3)

def admiral(img, x, y, s=1.0, mood="angry", arms=("hip", "hip"), look=0.0, moustache=True, seed=1):
    """Navy admiral: white shirt and tie, navy coat with gold buttons, officer's cap and a white moustache."""
    def extras(p, a):
        _officer_cap(p, a)
        if moustache: _moustache(p, a)
    return doodle(img, x, y, s, outfit="tie", tie=NAVY_D, mood=mood, arms=arms, look=look, seed=seed, shadow=False,
                  dress=_coat, extras=extras)

def _collar(p, a):
    P, s = _scale(a)
    p.shape([P(-44, -420), P(44, -420), P(30, -372), P(0, -340), P(-30, -372)], NAVY, w=4 * s, amp=.4)

def _bandage(p, a):
    (hx, hy), r = a["head"], a["head_r"]
    p.shape([(hx - .98 * r, hy - .5 * r), (hx + .98 * r, hy - .38 * r), (hx + 1.0 * r, hy - .18 * r), (hx - 1.0 * r, hy - .3 * r)],
            WHITE, w=.04 * r, amp=.4)
    p.poly(ellipse(hx + .5 * r, hy - .34 * r, .1 * r, .07 * r, n=12), RED)

def _sailor_hat(p, a):
    (hx, hy), r = a["head"], a["head_r"]
    p.shape(ellipse(hx, hy - .82 * r, .78 * r, .28 * r, n=32), WHITE, w=.05 * r, amp=.4)
    p.stroke([(hx - .66 * r, hy - .74 * r), (hx + .66 * r, hy - .74 * r)], .07 * r, NAVY, amp=.3)

def sailor(img, x, y, s=1.0, mood="happy", arms=("down", "down"), look=0.0, hurt=False, seed=1):
    """Navy sailor: white top with a navy collar and a round white hat; hurt=True adds a head bandage."""
    def extras(p, a):
        if hurt: _bandage(p, a)
        _sailor_hat(p, a)
    return doodle(img, x, y, s, outfit="tshirt", color=WHITE, mood=mood, arms=arms, look=look, seed=seed, shadow=False,
                  dress=_collar, extras=extras)

def _fez(p, a):
    (hx, hy), r = a["head"], a["head_r"]
    p.shape([(hx - .62 * r, hy - .72 * r), (hx - .5 * r, hy - 1.2 * r), (hx + .5 * r, hy - 1.2 * r), (hx + .62 * r, hy - .72 * r)],
            RED, w=.05 * r, amp=.4)
    p.stroke([(hx + .1 * r, hy - 1.2 * r), (hx + .45 * r, hy - .95 * r)], .04 * r, INK, amp=.2)

def _rifle(p, a):
    hx, hy = a["hand_r"]; s = a["head_r"] / 92
    p.stroke([(hx - 30 * s, hy + 70 * s), (hx + 26 * s, hy - 190 * s)], 7 * s, STEEL_D, amp=.3)
    p.stroke([(hx - 40 * s, hy + 110 * s), (hx - 16 * s, hy + 4 * s)], 15 * s, WOOD, amp=.4)

def guard(img, x, y, s=1.0, mood="angry", arms=("down", "hold"), look=0.0, rifle=True, seed=1):
    """Palace guard: doodle in a long white robe and a red fez; rifle=True holds an old rifle in the right hand."""
    def extras(p, a):
        _fez(p, a)
        if rifle: _rifle(p, a)
    return doodle(img, x, y, s, outfit="tshirt", color=WHITE, mood=mood, arms=arms, look=look, seed=seed, shadow=False,
                  dress=_robe, extras=extras)

# ---------- fire, explosions, smoke ----------
def _flame(p, cx, base, h, t=0.0, k=0):
    f = 1 + .08 * math.sin(t * 13 + k * 1.7); sway = math.sin(t * 9 + k * 2.3) * h * .06
    outer = spline([(cx - h * .3, base), (cx - h * .36, base - h * .4 * f), (cx - h * .1 + sway, base - h * .7 * f),
                    (cx + sway * 1.6, base - h * f), (cx + h * .14 + sway, base - h * .6 * f), (cx + h * .34, base - h * .35 * f),
                    (cx + h * .28, base)], closed=True)
    p.shape(outer, FIRE, w=max(3, h * .03), amp=.6)
    inner = spline([(cx - h * .15, base), (cx - h * .14, base - h * .3 * f), (cx + sway, base - h * .55 * f), (cx + h * .14, base - h * .26 * f),
                    (cx + h * .12, base)], closed=True)
    p.poly(p.wobble(inner, .4, True), FIRE_L)

def flame(img, cx, base, h=160, t=0.0, seed=1):
    """A tongue of fire that flickers with t."""
    with Pen(img, (cx - h * .6, base - h * 1.2, cx + h * .6, base + 10), seed) as p: _flame(p, cx, base, h, t)

def blast(img, cx, cy, r=120, seed=1):
    """Explosion burst: a spiky yellow star with an orange core."""
    n = 11
    star = [(cx + math.cos(math.pi * k / n) * r * (1 if k % 2 == 0 else .55), cy + math.sin(math.pi * k / n) * r * (1 if k % 2 == 0 else .55))
            for k in range(2 * n)]
    core = [(cx + math.cos(math.pi * k / n + .2) * r * (.6 if k % 2 == 0 else .35), cy + math.sin(math.pi * k / n + .2) * r * (.6 if k % 2 == 0 else .35))
            for k in range(2 * n)]
    with Pen(img, (cx - r * 1.2, cy - r * 1.2, cx + r * 1.2, cy + r * 1.2), seed) as p:
        p.shape(star, FIRE_L, w=max(3, r * .05), amp=.6)
        p.shape(core, FIRE, w=0)

def smoke(img, cx, cy, r=100, color=SMOKE, seed=1):
    """Puff of grey smoke centered on (cx, cy)."""
    pts = bumpy([(cx - r * .55, cy + r * .1, r * .5), (cx, cy - r * .25, r * .62), (cx + r * .55, cy, r * .5), (cx, cy + r * .25, r * .5)])
    with Pen(img, (cx - r * 1.3, cy - r * 1.1, cx + r * 1.3, cy + r * .9), seed) as p:
        p.shape(pts, color, w=max(3, r * .045), amp=.8)

# ---------- flags, buildings, ships ----------
def _flag(p, fx, fy, fw, color=RED, t=0.0, kind="plain", colors=(INK, WHITE, RED)):
    wave = lambda u: math.sin(u * 3.2 + t * 6) * fw * .05
    pts = [(fx + fw * u, fy + wave(u)) for u in (0, .25, .5, .75, 1)] + [(fx + fw * u, fy + fw * .62 + wave(u)) for u in (1, .75, .5, .25, 0)]
    if kind == "plain":
        p.shape(pts, color, w=max(3, fw * .04), amp=.4); return
    p.poly(p.wobble(pts, .3, True), WHITE)
    with p.clip(pts):
        if kind == "cross":
            p.poly([(fx, fy + fw * .26), (fx + fw, fy + fw * .26), (fx + fw, fy + fw * .38), (fx, fy + fw * .38)], color)
            p.poly([(fx + fw * .44, fy - fw * .1), (fx + fw * .56, fy - fw * .1), (fx + fw * .56, fy + fw * .8), (fx + fw * .44, fy + fw * .8)], color)
        else:                                        # tricolor: three horizontal stripes
            for i, col in enumerate(colors):
                p.poly([(fx - 5, fy + fw * .207 * i - (8 if i == 0 else 0)), (fx + fw + 5, fy + fw * .207 * i - (8 if i == 0 else 0)),
                        (fx + fw + 5, fy + fw * .207 * (i + 1) + (8 if i == 2 else 0)), (fx - 5, fy + fw * .207 * (i + 1) + (8 if i == 2 else 0))], col)
    p.stroke(pts, max(3, fw * .04), amp=.4, closed=True)

def flagpole(img, x, base, h=420, flag=1.0, color=RED, kind="plain", colors=(INK, WHITE, RED), t=0.0, seed=1):
    """Flagpole with a flag waving with t; flag = how high it flies (1 = top, 0 = bottom, None = no flag).
    kind: plain (one 'color'), cross (white with a 'color' cross) or tricolor (three stripes, 'colors' top to bottom)."""
    fw = h * .38
    with Pen(img, (x - 20, base - h - 30, x + fw + 30, base + 10), seed) as p:
        p.stroke([(x, base), (x, base - h)], max(4, h * .016), WOOD_D, amp=.3, taper=False)
        p.poly(ellipse(x, base - h - 6, 8, 8, n=12), GOLD)
        if flag is not None: _flag(p, x, base - h + (h - fw * .62) * (1 - flag), fw, color, t, kind, colors)

def palace(img, cx, base, w=460, flag=1.0, color=RED, burn=0.0, t=0.0, seed=1):
    """Seaside palace: three-storey building with arched verandas and a flag ('flag' = how high it flies, None = none);
    burn (0..1) adds scorch marks and flames that flicker with t."""
    h = w * .72; x0, x1 = cx - w / 2, cx + w / 2; fh = h / 3
    with Pen(img, (x0 - w * .12, base - h - w * .7, x1 + w * .12, base + 10), seed) as p:
        p.shape([(x0, base), (x0, base - h), (x1, base - h), (x1, base)], CREAM, w=6, amp=.8)
        p.shape(rrect(x0 - w * .03, base - h - 14, x1 + w * .03, base - h + 4, 4), (226, 214, 190), w=5)
        for f in range(3):
            fy = base - fh * f
            for k in range(6):
                ax = x0 + w * (k + .5) / 6; aw = w / 6 * .32; top = fy - fh * .78
                arch = [(ax - aw, fy - fh * .12), (ax - aw, top + aw)] + [(ax + math.cos(a) * aw, top + aw + math.sin(a) * aw)
                                                                         for a in (math.pi + math.pi * j / 8 for j in range(9))] + [(ax + aw, fy - fh * .12)]
                p.shape(arch, (70, 64, 70) if f == 0 and k in (2, 3) else (120, 150, 165), w=3.5, amp=.4)
            if f:
                p.stroke([(x0 + 4, fy - fh * .12), (x1 - 4, fy - fh * .12)], 5, WOOD_D, amp=.5)
                for k in range(25): p.stroke([(x0 + 8 + k * (w - 16) / 24, fy - fh * .12), (x0 + 8 + k * (w - 16) / 24, fy - fh * .3)], 2.5, WOOD_D, amp=.2)
        if burn:
            sc = [(x0 + 6, base - h * .4), (x0 + w * .3, base - h * .9), (x0 + w * .7, base - h + 6), (x1 - 6, base - h * .7),
                  (x1 - 6, base - h * .2), (x0 + w * .5, base - h * .5)]
            p.hatch(sc, (80, 70, 70), gap=max(8, 22 - 12 * burn), ang=-.8, w=3)
            for k, (fx, fr) in enumerate(((.18, .9), (.42, 1.2), (.66, 1.0), (.86, .8))):
                if burn > k * .2: _flame(p, x0 + w * fx, base - h + 4, w * .26 * fr * min(1, burn * 2), t, k)
        if flag is not None:
            px = cx + w * .25; ph = w * .55; fw = ph * .45
            p.stroke([(px, base - h - 12), (px, base - h - ph)], 5, WOOD_D, amp=.3, taper=False)
            _flag(p, px, base - h - ph + (ph - fw * .62 - 12) * (1 - flag), fw, color, t)

def warship(img, cx, base, w=520, color=STEEL, funnels=2, flag="cross", flash=0.0, sink=0.0, t=0.0, seed=1):
    """Steam warship facing left, base = waterline. color=WHITE gives a white hull (a royal yacht); flag: cross, plain
    (red) or None. flash (0..1) = the bow gun firing; sink (0..1) = tilts and goes under the waterline."""
    h = w * .14; x0, x1 = cx - w / 2, cx + w / 2
    ang = -.3 * sink; dy = sink * h * 3.4
    ca, sa = math.cos(ang), math.sin(ang)
    T = lambda q: (cx + (q[0] - cx) * ca - (q[1] - base) * sa, base + dy + (q[0] - cx) * sa + (q[1] - base) * ca)
    Ts = lambda pts: [T(q) for q in pts]
    white = color == WHITE
    with Pen(img, (x0 - w * .35, base - w * .7, x1 + w * .1, base + h * 1.2), seed) as p:
        with p.clip([(x0 - w * .4, base - w), (x1 + w * .2, base - w), (x1 + w * .2, base + 2), (x0 - w * .4, base + 2)]):
            for k in range(funnels):                                     # masts and funnels behind the deck house
                mx = cx - w * .28 + k * w * .5 / max(1, funnels - 1) if funnels > 1 else cx + w * .05
                p.stroke(Ts([(mx - w * .1, base - h * 1.2), (mx - w * .1, base - w * .52)]), 4, WOOD_D, amp=.3)
                fx = cx - w * .1 + k * w * .16
                p.shape(Ts([(fx - w * .035, base - h * 1.6), (fx - w * .03, base - h * 3.2), (fx + w * .03, base - h * 3.2), (fx + w * .035, base - h * 1.6)]),
                        (230, 200, 150) if white else (205, 170, 110), w=5, amp=.4)
                p.poly(Ts([(fx - w * .031, base - h * 3.2), (fx + w * .031, base - h * 3.2), (fx + w * .032, base - h * 2.9), (fx - w * .032, base - h * 2.9)]), INK)
            p.shape(Ts([(cx - w * .24, base - h), (cx - w * .2, base - h * 1.7), (cx + w * .22, base - h * 1.7), (cx + w * .26, base - h)]), color, w=5, amp=.5)
            for k in range(5): p.shape(Ts(ellipse(cx - w * .15 + k * w * .085, base - h * 1.35, w * .012, w * .012, n=10)), GLASS, w=2.5, amp=.2)
            p.shape(Ts([(x0, base - h * 1.15), (x1 - w * .02, base - h * 1.05), (x1 - w * .06, base), (x0 + w * .08, base)]),
                    WHITE if white else (90, 96, 108), w=6, amp=.6)
            p.poly(Ts([(x0 + w * .065, base - h * .3), (x1 - w * .055, base - h * .3), (x1 - w * .06, base), (x0 + w * .08, base)]), RED_D)
            p.stroke(Ts([(x0 + w * .02, base - h * .7), (x1 - w * .04, base - h * .65)]), 3, (60, 60, 70) if white else (200, 200, 205), amp=.4)
            gx, gy = x0 + w * .18, base - h * 1.35                       # bow gun pointing left
            p.shape(Ts(rrect(gx - w * .04, gy - h * .25, gx + w * .04, gy + h * .25, 6)), STEEL_D, w=4, amp=.3)
            p.stroke(Ts([(gx, gy), (gx - w * .16, gy - h * .1)]), max(5, w * .016), INK, amp=.2, taper=False)
            if flag:
                fx_, fy_ = T((x1 - w * .06, base - h * 1.05))
                p.stroke([(fx_, fy_), (fx_, fy_ - w * .2)], 4, WOOD_D, amp=.2)
                _flag(p, fx_, fy_ - w * .2, w * .1, RED, t, flag)
        for k in range(6):
            wx = x0 - w * .05 + k * w * .21
            p.stroke(spline([(wx, base + h * .12), (wx + w * .05, base - h * .06), (wx + w * .1, base + h * .12)]), 4, SEA_D, amp=.3)
        if flash > 0 and sink == 0:
            mx, my = T((gx - w * .16, gy - h * .1)); r = w * .09 * flash
            p.shape([(mx - r * .6 + math.cos(math.pi * k / 8) * r * (1 if k % 2 == 0 else .5), my + math.sin(math.pi * k / 8) * r * (1 if k % 2 == 0 else .5))
                     for k in range(16)], FIRE_L, w=3, amp=.4)

def map_pin(img, cx, cy, h=120, color=RED, seed=1):
    """Map pin; (cx, cy) = the point it marks."""
    r = h * .32
    with Pen(img, (cx - r * 1.4, cy - h * 1.1, cx + r * 1.4, cy + 10), seed) as p:
        p.shape([(cx, cy)] + [(cx + math.cos(a) * r, cy - h + r + math.sin(a) * r) for a in (math.radians(d) for d in range(150, 391, 12))],
                color, w=5, amp=.4)
        p.shape(ellipse(cx, cy - h + r, r * .38, r * .38, n=16), WHITE, w=3, amp=.2)

# ---------- quack medicine ----------
COAT_BLACK = (48, 46, 52)
AMBER, AMBER_D = (196, 120, 50), (140, 80, 30)
NEWSPRINT = (238, 234, 222)

def _frock_coat(p, a):
    P, s = _scale(a)
    for k in (-1, 1):
        p.shape([P(46 * k, -418), P(12 * k, -418), P(14 * k, -300), P(8 * k, -150), P(60 * k, -150), P(56 * k, -330)],
                COAT_BLACK, w=5 * s, amp=.6)

def _top_hat(p, a, color=COAT_BLACK):
    (hx, hy), r = a["head"], a["head_r"]
    p.shape(rrect(hx - 1.1 * r, hy - .86 * r, hx + 1.1 * r, hy - .7 * r, .06 * r), color, w=.05 * r, amp=.4)
    p.shape([(hx - .66 * r, hy - .8 * r), (hx - .62 * r, hy - 1.75 * r), (hx + .62 * r, hy - 1.75 * r), (hx + .66 * r, hy - .8 * r)],
            color, w=.05 * r, amp=.4)
    p.poly([(hx - .64 * r, hy - 1.02 * r), (hx + .64 * r, hy - 1.02 * r), (hx + .65 * r, hy - .9 * r), (hx - .65 * r, hy - .9 * r)], RED_D)

def _spectacles(p, a):
    (hx, hy), r = a["head"], a["head_r"]
    fx = a["mouth"][0]                                   # the face shifts with 'look'; the mouth marks its center
    for side in (-1, 1):
        p.stroke(ellipse(fx + side * .27 * r, hy - .05 * r, .23 * r, .3 * r, n=28), .035 * r, GOLD, amp=.3, closed=True)
    p.stroke([(fx - .05 * r, hy - .1 * r), (fx + .05 * r, hy - .1 * r)], .035 * r, GOLD, amp=.2)

def doctor(img, x, y, s=1.0, mood="smug", arms=("hip", "offer"), look=0.0, glasses=True, seed=1):
    """1800s doctor (or quack): white shirt and tie, long black frock coat, top hat and round gold spectacles."""
    def extras(p, a):
        _top_hat(p, a)
        if glasses: _spectacles(p, a)
    return doodle(img, x, y, s, outfit="tie", tie=INK, mood=mood, arms=arms, look=look, seed=seed, shadow=False,
                  dress=_frock_coat, extras=extras)

def pill_bottle(img, cx, base, h=240, label="PILLS", color=AMBER, ang=0.0, seed=1):
    """Old apothecary bottle with a cork and a paper label (label = its text)."""
    w = h * .5
    body = [(cx - w / 2, base), (cx - w / 2, base - h * .62), (cx - w * .3, base - h * .74), (cx - w * .2, base - h * .78),
            (cx - w * .2, base - h * .88), (cx + w * .2, base - h * .88), (cx + w * .2, base - h * .78), (cx + w * .3, base - h * .74),
            (cx + w / 2, base - h * .62), (cx + w / 2, base)]
    R = lambda pts: rotated(pts, cx, base - h / 2, ang) if ang else pts
    with Pen(img, (cx - h * .7, base - h * 1.2, cx + h * .7, base + h * .2), seed) as p:
        p.shape(R(body), color, w=6, amp=.6)
        p.stroke(R([(cx - w * .36, base - h * .55), (cx - w * .36, base - h * .12)]), 6, (235, 190, 140), amp=.3)
        p.shape(R(rrect(cx - w * .24, base - h, cx + w * .24, base - h * .86, 6)), WOOD, w=5, amp=.4)
        lab = R(rrect(cx - w * .42, base - h * .5, cx + w * .42, base - h * .2, 5))
        p.shape(lab, NEWSPRINT, w=4, amp=.4)
        if label: p.text(label, cx, base - h * .35, min(h * .1, w * .8 / max(1, len(label)) * 1.6), warp=0)

def pills(img, cx, cy, w=200, n=7, color=WHITE, seed=1):
    """A little heap of round pills centered on (cx, cy)."""
    with Pen(img, (cx - w * .7, cy - w * .5, cx + w * .7, cy + w * .4), seed) as p:
        for k in range(n):
            px = cx + (k - (n - 1) / 2) * w * .14 + (k % 2) * w * .04; py = cy - (k % 3) * w * .07
            p.shape(ellipse(px, py, w * .09, w * .065, n=20), color, w=3.5, amp=.3)
            p.stroke([(px - w * .05, py), (px + w * .05, py)], 2.5, (170, 170, 175), amp=.1)

def newspaper(img, cx, cy, w=360, headline="NEWS", ang=0.0, seed=1):
    """Old newspaper page: masthead line, a headline (headline = its text) and columns of text lines."""
    h = w * 1.25; x0, y0 = cx - w / 2, cy - h / 2
    R = lambda pts: rotated(pts, cx, cy, ang) if ang else pts
    with Pen(img, (cx - h * .75, cy - h * .75, cx + h * .75, cy + h * .75), seed) as p:
        p.shape(R([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)]), NEWSPRINT, w=5, amp=.6)
        p.stroke(R([(x0 + w * .08, y0 + h * .1), (x0 + w * .92, y0 + h * .1)]), 7, amp=.3)
        p.stroke(R([(x0 + w * .08, y0 + h * .14), (x0 + w * .92, y0 + h * .14)]), 2.5, amp=.2)
        hx, hy = R([(cx, y0 + h * .22)])[0]
        if headline: p.text(headline, hx, hy, min(w * .13, w * .84 / max(1, len(headline)) * 1.7), warp=0)
        for col in range(3):
            for k in range(9):
                lx = x0 + w * (.08 + col * .3); ly = y0 + h * (.33 + k * .07)
                p.stroke(R([(lx, ly), (lx + w * (.24 if k % 4 != 3 else .14), ly)]), 3, (120, 116, 110), amp=.2)

# ---------- background ----------
@lru_cache(maxsize=2)
def _seaside():
    img = grad(*PAPER)
    with Pen(img, (0, 0, W, H), seed=15) as p:
        p.poly([(-20, SEA_Y), (W + 20, SEA_Y), (W + 20, H + 20), (-20, H + 20)], SEA)
        p.stroke([(-20, SEA_Y), (W + 20, SEA_Y)], 5, SEA_D, amp=1.5, taper=False)
        for k in range(26):
            wx = (k * 397) % W; wy = SEA_Y + 60 + (k * 181) % 760
            p.stroke(spline([(wx, wy), (wx + 22, wy - 10), (wx + 44, wy)]), 3.5, SEA_D, amp=.3)
        p.shape(spline([(-20, SEA_Y - 40), (260, SEA_Y - 44), (500, SEA_Y - 30), (590, SEA_Y + 30), (520, SEA_Y + 80), (-20, SEA_Y + 90)]),
                SAND, w=5, amp=1)
        for k in range(10): p.stroke([(30 + k * 48, SEA_Y + 20 + (k % 3) * 18), (50 + k * 48, SEA_Y + 20 + (k % 3) * 18)], 3, SAND_D, amp=.3)
    return img

def seaside_bg(t=0.0):
    """Seafront on warm paper: plain sky, a sandy shore on the left (put buildings at SEA_Y + 20) and the sea with waves."""
    return _seaside().copy()

from . import cache_pieces
cache_pieces(globals())
