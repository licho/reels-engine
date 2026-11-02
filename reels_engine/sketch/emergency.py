"""Sketch-style city in an emergency: ambulance, police car, helicopter, bus stop and a city skyline that can burn.
All take the image (img) and a 'seed'; nothing draws a floor shadow unless shadow=True. Light bars and rotors
move with t.

    skyline(img, 0, 1080, 900, 360, fires=3, t=c.t)
    ambulance(img, 300, FLOOR, 440, t=c.t)
    helicopter(img, 760, 400, 380, t=c.t)"""
import math
import random
from . import Pen, INK, WHITE, RED, RED_D, GLASS, GLASS_D, BLUE, ellipse, rrect, rotated, spline
from .everyday import YELLOW, GRAY, GRAY_L, DARK, _wheel, bumpy
from .modern import _flame
from .survival import CONCRETE, NIGHT, _shade

NAVY = (44, 62, 112)
SMOKE = (150, 148, 150)

def _lightbar(p, x0, x1, y, t, colors=(RED, BLUE)):
    on = int(t * 4) % 2
    mid = (x0 + x1) / 2
    for k, (a, b) in enumerate(((x0, mid), (mid, x1))):
        c = colors[k] if (k == on) else _shade(colors[k], .55)
        p.shape(rrect(a, y - (x1 - x0) * .14, b, y, 4), c, w=3.5, amp=.2)
        if k == on:
            cx = (a + b) / 2
            for ang in (-2.4, -1.57, -.7):
                p.stroke([(cx + math.cos(ang) * (x1 - x0) * .3, y - (x1 - x0) * .1 + math.sin(ang) * (x1 - x0) * .3),
                          (cx + math.cos(ang) * (x1 - x0) * .45, y - (x1 - x0) * .1 + math.sin(ang) * (x1 - x0) * .45)], 3, c, amp=0)

def ambulance(img, cx, base, w=440, t=0.0, seed=1, shadow=False):
    """Box ambulance seen from the side, facing right: red stripe, red cross, flashing light bar (with t)."""
    r = w * .1
    with Pen(img, (cx - w * .6, base - w * .7, cx + w * .6, base + w * .06), seed) as p:
        if shadow: p.blob(cx, base, w * .52, w * .04)
        yb = base - r * .9
        box = [(cx - w * .5, yb), (cx - w * .5, base - w * .52), (cx + w * .16, base - w * .52), (cx + w * .16, yb)]
        cab = [(cx + w * .16, yb), (cx + w * .16, base - w * .42), (cx + w * .32, base - w * .42), (cx + w * .48, base - w * .26), (cx + w * .5, yb)]
        p.shape(cab, WHITE, w=6)
        p.shape([(cx + w * .2, base - w * .38), (cx + w * .31, base - w * .38), (cx + w * .43, base - w * .26), (cx + w * .2, base - w * .26)], GLASS, w=4, amp=.4)
        p.shape(box, WHITE, w=6)
        p.poly([(cx - w * .5 + 4, base - w * .24), (cx + w * .5 - 4, base - w * .24), (cx + w * .5 - 4, base - w * .2), (cx - w * .5 + 4, base - w * .2)], RED)
        qx, qy, q = cx - w * .18, base - w * .37, w * .07
        p.poly([(qx - q * .35, qy - q), (qx + q * .35, qy - q), (qx + q * .35, qy + q), (qx - q * .35, qy + q)], RED)
        p.poly([(qx - q, qy - q * .35), (qx + q, qy - q * .35), (qx + q, qy + q * .35), (qx - q, qy + q * .35)], RED)
        p.stroke([(cx + w * .02, base - w * .48), (cx + w * .02, yb - 4)], 3, GRAY, amp=.3)
        p.shape(ellipse(cx + w * .48, base - w * .2, w * .02, w * .015, n=12), YELLOW, w=3, amp=.2)
        _lightbar(p, cx + w * .18, cx + w * .32, base - w * .42, t)
        for wx in (cx - w * .3, cx + w * .32): _wheel(p, wx, base - r, r)

def police_car(img, cx, base, w=420, color=NAVY, t=0.0, seed=1, shadow=False):
    """Patrol car seen from the side, facing right: two-tone body (white doors) and a flashing light bar (with t)."""
    r = w * .11
    yb, yt = base - r * .9, base - r - w * .17
    with Pen(img, (cx - w * .6, base - w * .55, cx + w * .6, base + w * .06), seed) as p:
        if shadow: p.blob(cx, base, w * .52, w * .04)
        cab = [(cx - w * .32, yt + 4), (cx - w * .22, yt - w * .15), (cx + w * .12, yt - w * .15), (cx + w * .24, yt + 4)]
        p.shape(cab, color, w=6)
        p.shape([(cx - w * .27, yt), (cx - w * .2, yt - w * .12), (cx - w * .06, yt - w * .12), (cx - w * .06, yt)], GLASS, w=4, amp=.6)
        p.shape([(cx - w * .02, yt), (cx - w * .02, yt - w * .12), (cx + w * .1, yt - w * .12), (cx + w * .19, yt)], GLASS, w=4, amp=.6)
        body = [(cx - w * .5, yb), (cx - w * .5, yt + w * .03), (cx - w * .44, yt), (cx + w * .38, yt + w * .01), (cx + w * .5, yt + w * .06), (cx + w * .5, yb)]
        p.shape(body, color, w=6)
        p.poly([(cx - w * .3, yt + 6), (cx + w * .22, yt + 6), (cx + w * .22, yb - 6), (cx - w * .3, yb - 6)], WHITE)
        p.stroke(body, 6, amp=1.6, closed=True)
        p.stroke([(cx - w * .04, yt + 4), (cx - w * .04, yb - 4)], 4, amp=.5)
        p.shape(ellipse(cx + w * .47, yt + w * .06, w * .03, w * .022, n=14), YELLOW, w=3, amp=.3)
        _lightbar(p, cx - w * .12, cx + w * .06, yt - w * .15, t)
        for wx in (cx - w * .3, cx + w * .3): _wheel(p, wx, base - r, r)

def helicopter(img, cx, cy, w=380, color=(220, 60, 50), t=0.0, light=False, look=1.0, seed=1):
    """Helicopter in the air seen from the side, facing 'look' (1 right, -1 left): bubble cabin, tail boom, skids
    and a blurred main rotor that turns with t; light=True shines a searchlight down."""
    d = 1 if look >= 0 else -1
    X = lambda dx: cx + d * dx * w
    with Pen(img, (cx - w * .75, cy - w * .4, cx + w * .75, cy + (w * 1.5 if light else w * .4)), seed) as p:
        if light: p.poly([(X(.12), cy + w * .16), (X(.45), cy + w * 1.4), (X(-.2), cy + w * 1.4), (X(.06), cy + w * .16)], (255, 238, 150, 110))
        p.limb([(X(-.1), cy - w * .02), (X(-.6), cy - w * .08)], w * .05, color, w * .012)
        p.shape([(X(-.62), cy - w * .2), (X(-.55), cy - w * .2), (X(-.52), cy - w * .06), (X(-.64), cy - w * .04)], color, w=4, amp=.3)
        tr = (X(-.6), cy - w * .1)
        a = t * 30
        p.stroke([(tr[0] + math.cos(a) * w * .08, tr[1] + math.sin(a) * w * .08), (tr[0] - math.cos(a) * w * .08, tr[1] - math.sin(a) * w * .08)], 4, DARK, amp=0)
        body = spline([(X(-.2), cy - w * .05), (X(-.12), cy - w * .17), (X(.12), cy - w * .18), (X(.3), cy - w * .08), (X(.32), cy + w * .05),
                       (X(.18), cy + w * .14), (X(-.12), cy + w * .14), (X(-.22), cy + w * .05)], closed=True)
        p.shape(body, color, w=6, amp=.5)
        win = spline([(X(.08), cy - w * .14), (X(.2), cy - w * .11), (X(.29), cy - w * .02), (X(.27), cy + w * .04), (X(.08), cy + w * .04)], closed=True)
        p.shape(win, GLASS, w=4, amp=.3)
        p.shape(rrect(min(X(-.1), X(.02)), cy - w * .12, max(X(-.1), X(.02)), cy + w * .04, 4), GLASS, w=3.5, amp=.2)
        for sx in (-.08, .16): p.stroke([(X(sx), cy + w * .14), (X(sx - .02), cy + w * .22)], 4, DARK, amp=.1)
        p.stroke([(X(-.22), cy + w * .22), (X(.26), cy + w * .22), (X(.3), cy + w * .19)], 5, DARK, amp=.2)
        p.limb([(cx, cy - w * .18), (cx, cy - w * .24)], w * .025, DARK, 2)
        k = .5 + .5 * math.sin(t * 25)
        p.stroke([(cx - w * .62, cy - w * .25), (cx + w * .62, cy - w * .25)], 4, DARK, amp=.2)
        p.poly(ellipse(cx, cy - w * .25, w * .62, w * .03, n=40), (60, 60, 68, 60))
        p.stroke([(cx - w * .5 * k, cy - w * .26), (cx + w * .5 * k, cy - w * .24)], 5, DARK, amp=0)

def bus_stop(img, cx, base, w=380, damage=0.0, seed=1, shadow=False):
    """Bus stop shelter: roof, glass panel, bench and a sign pole. damage = 0…1 cracks the glass and bends the roof."""
    h = w * .75
    with Pen(img, (cx - w * .7, base - h * 1.25, cx + w * .7, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .04)
        top = base - h
        bend = damage * h * .12
        glass = [(cx - w * .4, top + h * .08), (cx + w * .3, top + h * .08 + bend * .6), (cx + w * .3, base - h * .1), (cx - w * .4, base - h * .1)]
        p.shape(glass, GLASS + (190,), w=4, amp=.4)
        if damage:
            rng = random.Random(seed)
            ox, oy = cx - w * .05, top + h * .45
            for k in range(int(4 + 6 * damage)):
                a = rng.uniform(0, 6.28); L = rng.uniform(.15, .35) * w
                p.stroke([(ox, oy), (ox + math.cos(a) * L * .5 + rng.uniform(-10, 10), oy + math.sin(a) * L * .5), (ox + math.cos(a) * L, oy + math.sin(a) * L)], 2.5, WHITE, amp=.3)
                p.stroke([(ox, oy), (ox + math.cos(a) * L * .5, oy + math.sin(a) * L * .5)], 1.5, DARK, amp=.3)
        for xx in (cx - w * .4, cx + w * .3): p.limb([(xx, base), (xx, top + (bend if xx > cx else 0))], w * .025, GRAY, 3)
        p.shape([(cx - w * .48, top), (cx + w * .4, top + bend), (cx + w * .4, top + bend + h * .08), (cx - w * .48, top + h * .08)], DARK, w=5, amp=.4)
        p.shape(rrect(cx - w * .32, base - h * .35, cx + w * .2, base - h * .3, 3), (180, 116, 64), w=4, amp=.2)
        for xx in (cx - w * .28, cx + w * .16): p.stroke([(xx, base - h * .3), (xx, base)], 4, DARK, amp=.1)
        sx = cx + w * .5
        p.limb([(sx, base), (sx, top - h * .1)], w * .02, GRAY, 2.5)
        p.shape(ellipse(sx, top - h * .18, w * .09, w * .09, n=24), (60, 130, 200), w=4, amp=.2)
        p.shape(rrect(sx - w * .05, top - h * .23, sx + w * .05, top - h * .13, 3), WHITE, w=2.5, amp=.1)

def skyline(img, x0, x1, base, h=360, fires=0, smoke=True, night=False, t=0.0, seed=1):
    """City skyline from x0 to x1 standing on base, buildings up to h tall with windows. fires = how many rooftops
    burn (smoke columns rise from them when smoke=True); night=True turns the buildings dark with a few lit windows.
    Flames flicker with t."""
    rng = random.Random(seed)
    blds, x = [], x0
    while x < x1:
        bw = rng.uniform(.18, .32) * h
        blds.append((x, min(x1, x + bw), base - h * rng.uniform(.35, 1)))
        x += bw + rng.uniform(-.04, .02) * h
    burning = set(rng.sample(range(len(blds)), min(fires, len(blds))))
    wall = (70, 74, 90) if night else None
    with Pen(img, (x0 - 10, base - h * 1.9, x1 + 10, base + 6), seed) as p:
        if smoke:
            for i in sorted(burning):
                a, b, top = blds[i]
                mx = (a + b) / 2
                for k in range(5):
                    f = k / 5 + (t * .15) % .2
                    rr = h * (.07 + .08 * f)
                    sx, sy = mx + h * .2 * f * f, top - h * .08 - h * .7 * f
                    p.shape(bumpy([(sx, sy, rr), (sx + rr * .6, sy + rr * .2, rr * .7), (sx - rr * .5, sy + rr * .3, rr * .6)], n=28),
                            (110, 108, 112) if night else SMOKE, w=3, amp=.5)
        for i, (a, b, top) in enumerate(blds):
            col = wall or rng.choice(((205, 210, 220), (226, 214, 196), (190, 200, 214), (214, 206, 214)))
            p.shape([(a, base), (a, top), (b, top), (b, base)], col, w=4.5, amp=.5)
            cols = max(1, int((b - a) / 26))
            for r in range(int((base - top) / 34) - 1):
                for c in range(cols):
                    wx = a + (b - a) * (c + .5) / cols
                    wy = top + 18 + r * 34
                    lit = (rng.random() < .25) if night else True
                    p.poly(rrect(wx - 7, wy, wx + 7, wy + 16, 2), (250, 220, 120) if night and lit else (_shade(col, .8) if night else GLASS_D))
            if i in burning:
                for k in range(2): _flame(p, a + (b - a) * (.3 + .4 * k), top + 4, h * .14, t, k)
        p.stroke([(x0, base), (x1, base)], 5, amp=.8)

from . import cache_pieces
cache_pieces(globals())
