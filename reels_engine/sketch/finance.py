"""Sketch-style economy and personal finance: bank, safe, ATM, cash register, calculator, gold bars, money bag,
money tree, salary envelope, price tag, percent badge, balance scale, hourglass, line chart, candlestick chart, pie
chart, score gauge, contract, ball and chain (debt), umbrella (emergency fund), goal thermometer, padlock,
magnifier, rocket and balloon. All take the image (img) and a 'seed'. Things that stand on the floor draw no floor
shadow unless shadow=True.

    bank(img, 540, FLOOR, 460)
    line_chart(img, 120, 900, 840, 420, [3, 4, 3.5, 6, 5.5, 8])

The money pieces from props (bill, money_stack, money_pile, money_jar, money_text, wallet) and everyday (coin,
credit_card, piggy_bank, receipt, shopping_bag, shopping_cart) work together with these."""
import math
from . import (Pen, INK, WHITE, SHADE, RED, RED_D, GREEN, GREEN_D, GREEN_L, MONEY, MONEY_D, GLASS, GLASS_D, WOOD,
               WOOD_D, BLUE, ellipse, rrect, rotated, spline)
from .everyday import YELLOW, GOLD, GOLD_D, GRAY, GRAY_L, DARK, PAPER_BAG, bumpy
from .props import _bill

MARBLE, MARBLE_D = (240, 236, 226), (196, 190, 178)
STEEL, STEEL_D = (190, 196, 206), (130, 136, 150)
SACK, SACK_D = (214, 180, 120), (160, 124, 70)
PAPER, PAPER_D = (250, 248, 240), (200, 196, 186)
SAND = (236, 196, 110)
ORANGE = (236, 130, 50)
PURPLE = (140, 100, 200)
PIE_COLORS = (MONEY, BLUE, YELLOW, RED, PURPLE, GRAY)

# ---------- places and machines ----------
def bank(img, cx, base, w=460, label="BANK", seed=1, shadow=False):
    """Bank building with columns and a '$' on the pediment; label = text on the frieze."""
    h = w * .82
    with Pen(img, (cx - w * .6, base - h * 1.08, cx + w * .6, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .6, w * .04, SHADE)
        top = base - h
        for k in range(3):                                         # steps
            y = base - k * h * .045
            p.shape([(cx - w * (.5 - k * .03), y), (cx + w * (.5 - k * .03), y), (cx + w * (.5 - k * .03), y - h * .045),
                     (cx - w * (.5 - k * .03), y - h * .045)], MARBLE, w=4, amp=.4)
        y_col_b, y_col_t = base - h * .135, top + h * .43
        p.poly([(cx - w * .4, y_col_b), (cx + w * .4, y_col_b), (cx + w * .4, y_col_t), (cx - w * .4, y_col_t)], MARBLE_D)
        n = 5
        for k in range(n):
            x = cx - w * .36 + k * w * .72 / (n - 1)
            cw = w * .05
            p.shape([(x - cw, y_col_t), (x + cw, y_col_t), (x + cw, y_col_b), (x - cw, y_col_b)], MARBLE, w=4, amp=.4)
            for f in (-.4, .4): p.stroke([(x + cw * f, y_col_t + 8), (x + cw * f, y_col_b - 8)], 2, MARBLE_D, amp=.3)
            p.shape(rrect(x - cw * 1.4, y_col_t - h * .025, x + cw * 1.4, y_col_t + h * .01, 3), MARBLE, w=3.5, amp=.3)
            p.shape(rrect(x - cw * 1.4, y_col_b - h * .015, x + cw * 1.4, y_col_b + h * .01, 3), MARBLE, w=3.5, amp=.3)
        frieze_b = y_col_t - h * .025
        p.shape([(cx - w * .46, frieze_b), (cx + w * .46, frieze_b), (cx + w * .46, frieze_b - h * .12), (cx - w * .46, frieze_b - h * .12)],
                MARBLE, w=5, amp=.5)
        if label: p.text(label, cx, frieze_b - h * .06, h * .085, warp=.5)
        ped_b = frieze_b - h * .12
        p.shape([(cx - w * .5, ped_b), (cx + w * .5, ped_b), (cx, top)], MARBLE, w=6, amp=.6)
        p.shape(ellipse(cx, ped_b - (ped_b - top) * .38, h * .075, h * .075, n=28), GOLD, w=4, amp=.3)
        p.text("$", cx, ped_b - (ped_b - top) * .38, h * .1, fill=GOLD_D, warp=0)

def safe(img, cx, base, h=300, open=False, seed=1, shadow=False):
    """Steel safe with a dial and handle; open=True shows the door swung open and money inside."""
    w = h * .9
    x0, x1, y0 = cx - w / 2, cx + w / 2, base - h
    with Pen(img, (x0 - w * .55, y0 - 10, x1 + w * .2, base + h * .06), seed) as p:
        if shadow: p.blob(cx, base, w * .6, h * .04, SHADE)
        for x in (x0 + w * .15, x1 - w * .15):
            p.shape(rrect(x - w * .07, base - h * .06, x + w * .07, base, 4), DARK, w=4, amp=.3)
        p.shape(rrect(x0, y0, x1, base - h * .05, w * .05), STEEL, w=7)
        ix0, iy0, ix1, iy1 = x0 + w * .1, y0 + h * .1, x1 - w * .1, base - h * .15
        if open:
            p.shape(rrect(ix0, iy0, ix1, iy1, 6), DARK, w=5, amp=.4)
            p.stroke([(ix0 + 6, (iy0 + iy1) / 2), (ix1 - 6, (iy0 + iy1) / 2)], 5, STEEL_D, amp=.3)
            bw = (ix1 - ix0) * .34
            for row, yy in enumerate(((iy0 + iy1) / 2 - bw * .22, iy1 - bw * .22)):
                for k in range(3 if row else 2):
                    x = ix0 + bw * .6 + k * bw * .9
                    for j in range(3): _bill(p, x, yy - j * bw * .1, bw, 0, edge=2.5)
            door = [(x0, y0 + h * .02), (x0 - w * .45, y0 + h * .1), (x0 - w * .45, base - h * .12), (x0, base - h * .07)]
            p.shape(door, STEEL_D, w=6, amp=.5)
            p.shape(ellipse(x0 - w * .25, (y0 + base) / 2, w * .07, w * .1, n=24), STEEL, w=4, amp=.3)
        else:
            p.shape(rrect(ix0, iy0, ix1, iy1, 6), STEEL, w=5, amp=.4)
            dx, dy = cx - w * .05, (iy0 + iy1) / 2
            p.shape(ellipse(dx, dy, w * .15, w * .15, n=36), STEEL_D, w=5, amp=.4)
            p.shape(ellipse(dx, dy, w * .1, w * .1, n=28), GRAY_L, w=4, amp=.3)
            for k in range(12):
                a = 2 * math.pi * k / 12
                p.stroke([(dx + math.cos(a) * w * .1, dy + math.sin(a) * w * .1), (dx + math.cos(a) * w * .13, dy + math.sin(a) * w * .13)], 2.5, amp=0)
            p.stroke([(dx, dy), (dx, dy - w * .08)], 4, RED, amp=0)
            hx = ix1 - w * .1
            p.limb([(hx, dy - h * .12), (hx, dy + h * .12)], w * .04, STEEL_D, 4)
            for yy in (iy0 + h * .06, iy1 - h * .06):
                p.shape(rrect(ix0 - w * .06, yy - h * .04, ix0 + w * .02, yy + h * .04, 3), STEEL_D, w=3.5, amp=.2)

def atm(img, cx, base, h=420, cash=True, seed=1, shadow=False):
    """Cash machine (ATM) with screen and keypad; cash=True shows bills coming out of the slot."""
    w = h * .55
    x0, x1, y0 = cx - w / 2, cx + w / 2, base - h
    with Pen(img, (x0 - w * .3, y0 - 10, x1 + w * .3, base + h * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .7, h * .03, SHADE)
        p.shape(rrect(x0, y0, x1, base, w * .06), BLUE, w=7)
        p.shape(rrect(x0 + w * .08, y0 + h * .05, x1 - w * .08, y0 + h * .13, 6), WHITE, w=4, amp=.3)
        p.text("ATM", cx, y0 + h * .09, h * .055, fill=BLUE, warp=0)
        p.shape(rrect(x0 + w * .12, y0 + h * .17, x1 - w * .12, y0 + h * .4, 8), GLASS, w=5, amp=.4)
        p.text("$", cx, y0 + h * .285, h * .1, fill=GLASS_D, warp=0)
        p.shape(rrect(x0 + w * .05, y0 + h * .45, x1 - w * .05, y0 + h * .5, 4), DARK, w=4, amp=.3)
        for r in range(4):
            for c in range(3):
                kx, ky = cx - w * .2 + c * w * .14, y0 + h * .56 + r * h * .05
                p.shape(rrect(kx - w * .05, ky - h * .018, kx + w * .05, ky + h * .018, 3), WHITE, w=2.5, amp=.2)
            col = (RED, YELLOW, GREEN, WHITE)[r]
            p.shape(rrect(cx + w * .22 - w * .06, y0 + h * .56 + r * h * .05 - h * .018, cx + w * .22 + w * .06,
                          y0 + h * .56 + r * h * .05 + h * .018, 3), col, w=2.5, amp=.2)
        sy = y0 + h * .8
        if cash:
            for k in range(3): _bill(p, cx + (k - 1) * 6, sy + h * .045 - k * 5, w * .5, (k - 1) * .06, edge=3)
        p.shape(rrect(x0 + w * .15, sy - h * .015, x1 - w * .15, sy + h * .015, 3), DARK, w=4, amp=.3)

def cash_register(img, cx, base, w=300, display="$25.00", open=True, seed=1, shadow=False):
    """Shop cash register with a display; open=True slides the drawer out with money."""
    h = w * .8
    with Pen(img, (cx - w * .65, base - h * 1.1, cx + w * .65, base + w * .06), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .04, SHADE)
        dy0 = base - h * .28
        if open:
            p.shape([(cx - w * .48, dy0 + h * .05), (cx + w * .48, dy0 + h * .05), (cx + w * .56, base), (cx - w * .56, base)],
                    GRAY_L, w=5)
            for k in range(3):
                x = cx - w * .36 + k * w * .24
                p.stroke([(x + w * .12, dy0 + h * .08), (x + w * .13, base - 4)], 3, GRAY, amp=.2)
                _bill(p, x + w * .02, dy0 + h * .15, w * .2, .1, edge=2.5)
        p.shape(rrect(cx - w * .48, dy0 - h * .05, cx + w * .48, dy0 + h * .1 if open else base, 6), GRAY_L if not open else GRAY, w=6)
        body = [(cx - w * .46, dy0 - h * .05), (cx - w * .4, base - h * .78), (cx + w * .4, base - h * .78), (cx + w * .46, dy0 - h * .05)]
        p.shape(body, RED, w=6)
        for r in range(3):
            for c in range(5):
                kx, ky = cx - w * .3 + c * w * .15, base - h * .66 + r * h * .1
                p.shape(rrect(kx - w * .05, ky - h * .03, kx + w * .05, ky + h * .03, 3), WHITE, w=2.5, amp=.2)
        p.shape([(cx - w * .1, base - h * .78), (cx + w * .1, base - h * .78), (cx + w * .08, base - h * .86), (cx - w * .08, base - h * .86)],
                DARK, w=4, amp=.3)
        p.shape(rrect(cx - w * .3, base - h * 1.04, cx + w * .3, base - h * .86, 6), DARK, w=5, amp=.4)
        if display: p.text(display, cx, base - h * .95, h * .1, fill=(120, 230, 120), warp=0)

def calculator(img, cx, cy, h=260, display="1,250", ang=0.0, seed=1):
    """Pocket calculator with a display; ang = tilt."""
    w = h * .64
    R = lambda pts: rotated(pts, cx, cy, ang)
    with Pen(img, (cx - h * .7, cy - h * .7, cx + h * .7, cy + h * .7), seed) as p:
        p.shape(R(rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, w * .1)), DARK, w=6)
        p.shape(R(rrect(cx - w * .38, cy - h * .4, cx + w * .38, cy - h * .2, 6)), (196, 214, 180), w=4, amp=.3)
        if display:
            p.text(str(display), *R([(cx + w * .05, cy - h * .3)])[0], h * .1, fill=DARK, warp=0)
        for r in range(4):
            for c in range(4):
                kx, ky = cx - w * .3 + c * w * .2, cy - h * .08 + r * h * .13
                col = ORANGE if c == 3 else (GRAY if r == 0 else GRAY_L)
                p.shape(R(rrect(kx - w * .07, ky - h * .045, kx + w * .07, ky + h * .045, 4)), col, w=2.5, amp=.2)

# ---------- money things ----------
def gold_bars(img, cx, base, w=110, rows=(3, 2, 1), seed=1, shadow=False):
    """Stack of gold bars (pyramid); w = width of one bar, rows = bars per row, bottom first."""
    t = w * .32
    half = max(rows) * w / 2
    with Pen(img, (cx - half - 20, base - len(rows) * t - w * .3, cx + half + 20, base + 15), seed) as p:
        if shadow: p.blob(cx, base, half * 1.05, w * .1, SHADE)
        for r, n in enumerate(rows):
            for k in range(n):
                x = cx - n * w / 2 + k * w
                y = base - r * t
                bar = [(x + 3, y), (x + w - 3, y), (x + w * .86, y - t), (x + w * .14, y - t)]
                p.shape(bar, GOLD, w=4, amp=.4)
                p.stroke([(x + w * .22, y - t * .3), (x + w * .5, y - t * .3)], 3, WHITE, amp=.2)
                p.stroke([(x + w * .14, y - t), (x + w * .86, y - t)], 3, GOLD_D, amp=.2)

def money_bag(img, cx, base, h=240, label="$", seed=1, shadow=False):
    """Tied money sack with a '$' on it."""
    w = h * .85
    with Pen(img, (cx - w * .65, base - h * 1.08, cx + w * .65, base + h * .06), seed) as p:
        if shadow: p.blob(cx, base, w * .5, h * .04, SHADE)
        neck = base - h * .72
        body = spline([(cx - w * .14, neck), (cx - w * .4, base - h * .5), (cx - w * .5, base - h * .2), (cx - w * .3, base),
                       (cx + w * .3, base), (cx + w * .5, base - h * .2), (cx + w * .4, base - h * .5), (cx + w * .14, neck)], closed=True)
        p.shape(body, SACK, w=6)
        p.shape([(cx - w * .14, neck), (cx - w * .3, base - h * 1.0), (cx - w * .1, base - h * .9), (cx, base - h * 1.02),
                 (cx + w * .1, base - h * .9), (cx + w * .3, base - h * 1.0), (cx + w * .14, neck)], SACK, w=5, amp=.6)
        p.limb([(cx - w * .17, neck + 2), (cx + w * .17, neck + 2)], h * .035, SACK_D, 3)
        p.stroke([(cx + w * .2, base - h * .45), (cx + w * .32, base - h * .2)], 3, SACK_D, amp=.3)
        if label: p.text(label, cx, base - h * .33, h * .32, fill=MONEY_D, warp=.8)

def money_tree(img, cx, base, h=420, seed=1, shadow=False):
    """Tree whose leaves are banknotes (growth, passive income)."""
    r = h * .3
    cy = base - h * .66
    with Pen(img, (cx - r * 1.6, base - h * 1.05, cx + r * 1.6, base + h * .05), seed) as p:
        if shadow: p.blob(cx, base, r * .9, h * .03, SHADE)
        p.shape([(cx - h * .05, base), (cx - h * .035, cy), (cx + h * .035, cy), (cx + h * .05, base)], WOOD, w=6)
        for sd in (-1, 1): p.stroke([(cx, cy + h * .12), (cx + sd * r * .5, cy - r * .1)], h * .025, WOOD_D, amp=.4)
        crown = bumpy([(cx - r * .6, cy, r * .55), (cx + r * .6, cy, r * .55), (cx, cy - r * .45, r * .65), (cx, cy + r * .1, r * .6)])
        p.shape(crown, GREEN_L, w=6)
        R = p.rng
        for k in range(14):
            a, d = R.uniform(0, 6.28), R.uniform(.1, .95)
            _bill(p, cx + math.cos(a) * r * d * 1.05, cy - r * .1 + math.sin(a) * r * d * .75, r * .38, R.uniform(-.7, .7), edge=2.5)

def salary_envelope(img, cx, cy, w=240, label="$", bills=True, seed=1):
    """Paper envelope (salary, savings) with bills peeking out of the top."""
    h = w * .62
    with Pen(img, (cx - w * .6, cy - h * 1.1, cx + w * .6, cy + h * .6), seed) as p:
        if bills:
            for k in range(3): _bill(p, cx - w * .12 + k * w * .12, cy - h * .45 - k * 4, w * .55, -.15 + k * .15, edge=3)
        p.shape(rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 6), PAPER_BAG, w=6)
        p.stroke([(cx - w / 2, cy + h / 2), (cx, cy + h * .02), (cx + w / 2, cy + h / 2)], 4, (170, 130, 80), amp=.4)
        if label:
            p.shape(ellipse(cx, cy - h * .08, h * .17, h * .17, n=24), RED, w=3, amp=.3)
            p.text(label, cx, cy - h * .08, h * .2, fill=WHITE, warp=0)

def price_tag(img, cx, cy, w=200, text="$9.99", color=YELLOW, ang=-0.2, seed=1):
    """Price tag with a hole and string; ang = tilt."""
    h = w * .5
    R = lambda pts: rotated(pts, cx, cy, ang)
    with Pen(img, (cx - w * .9, cy - w * .9, cx + w * .9, cy + w * .9), seed) as p:
        hx, hy = R([(cx - w * .32, cy)])[0]
        p.stroke(spline([(hx, hy), (hx - w * .2, hy - h * .6), (hx - w * .35, hy - h * .9)]), 3, amp=.6)
        p.shape(R([(cx - w * .5, cy), (cx - w * .3, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w * .3, cy + h / 2)]),
                color, w=5)
        p.shape(ellipse(hx, hy, h * .08, h * .08, n=14), WHITE, w=3, amp=.2)
        if text:
            tx, ty = R([(cx + w * .1, cy)])[0]
            p.text(text, tx, ty, h * .42, warp=.5)

def percent_badge(img, cx, cy, r=80, text="%", color=RED, seed=1):
    """Starburst badge with a percent sign (interest, discounts, inflation)."""
    with Pen(img, (cx - r * 1.3, cy - r * 1.3, cx + r * 1.3, cy + r * 1.3), seed) as p:
        n = 16
        pts = [(cx + math.cos(math.pi * k / n) * r * (1 if k % 2 == 0 else .82), cy + math.sin(math.pi * k / n) * r * (1 if k % 2 == 0 else .82))
               for k in range(2 * n)]
        p.shape(pts, color, w=max(3, r * .06), amp=.5)
        p.text(text, cx, cy, r * (.9 if len(text) <= 2 else .6), fill=WHITE, stroke=INK, sw=max(1, r * .02), warp=.6)

# ---------- ideas ----------
def balance_scale(img, cx, base, h=360, tilt=0.0, seed=1, shadow=False):
    """Balance scale; tilt > 0 lowers the right pan (-1…1). Returns the centers of the (left, right) pans."""
    w = h * .9
    top = base - h * .82
    a = tilt * .3
    dx, dy = math.cos(a) * w * .42, math.sin(a) * w * .42
    pans = ((cx - dx, top - dy + h * .32), (cx + dx, top + dy + h * .32))
    with Pen(img, (cx - w * .75, base - h * 1.0, cx + w * .75, base + h * .06), seed) as p:
        if shadow: p.blob(cx, base, w * .3, h * .03, SHADE)
        p.shape([(cx - w * .2, base), (cx - w * .12, base - h * .06), (cx + w * .12, base - h * .06), (cx + w * .2, base)], GOLD, w=5, amp=.4)
        p.limb([(cx, base - h * .06), (cx, top)], h * .03, GOLD, 4)
        p.limb([(cx - dx, top - dy), (cx + dx, top + dy)], h * .025, GOLD, 4)
        p.shape(ellipse(cx, top, h * .035, h * .035, n=16), GOLD_D, w=3, amp=.2)
        for (px, py), (ex, ey) in zip(pans, ((cx - dx, top - dy), (cx + dx, top + dy))):
            for sd in (-1, 1): p.stroke([(ex, ey), (px + sd * w * .18, py)], 2.5, GOLD_D, amp=.3)
            p.shape([(px - w * .2, py), (px + w * .2, py), (px + w * .13, py + h * .06), (px - w * .13, py + h * .06)], GOLD, w=4, amp=.4)
    return pans

def hourglass(img, cx, cy, h=240, t=0.5, seed=1):
    """Hourglass; t = 0…1 how much sand has fallen (time is money)."""
    w = h * .6
    with Pen(img, (cx - w * .7, cy - h * .6, cx + w * .7, cy + h * .6), seed) as p:
        up = [(cx - w * .38, cy - h * .42), (cx + w * .38, cy - h * .42), (cx + w * .06, cy - h * .02), (cx - w * .06, cy - h * .02)]
        dn = [(cx - w * .06, cy + h * .02), (cx + w * .06, cy + h * .02), (cx + w * .38, cy + h * .42), (cx - w * .38, cy + h * .42)]
        glass = up[:2] + [up[2], dn[2], dn[3], up[3]]
        p.poly(p.wobble(glass, .4, True), GLASS)
        t = max(0.0, min(1.0, t))
        with p.clip(up):
            ys = cy - h * .02 - (h * .4) * (1 - t) * .85
            if t < 1: p.poly([(cx - w, ys), (cx + w, ys), (cx + w, cy), (cx - w, cy)], SAND)
        with p.clip(dn):
            yb = cy + h * .42 - h * .4 * t * .85
            if t > 0: p.poly([(cx - w, cy + h * .42), (cx + w, cy + h * .42), (cx, yb - h * .05)], SAND)
        if 0 < t < 1: p.stroke([(cx, cy - h * .02), (cx, cy + h * .4)], 2.5, SAND, amp=.2)
        p.stroke(glass, 5, amp=.5, closed=True)
        for yy in (cy - h * .42, cy + h * .42):
            p.shape(rrect(cx - w * .48, yy - h * .05, cx + w * .48, yy + h * .05, 5), WOOD, w=5, amp=.3)

def line_chart(img, x, y, w=600, h=360, values=(3, 4, 3.5, 6, 5.5, 8), color=MONEY, area=True, dots=True, seed=1):
    """Line chart with axes; (x, y) = bottom left corner (origin). The line goes up or down with 'values'."""
    lo, hi = min(values + (0,)), max(values)
    pts = [(x + w * .06 + w * .9 * k / max(1, len(values) - 1), y - h * .05 - h * .85 * (v - lo) / ((hi - lo) or 1))
           for k, v in enumerate(values)]
    with Pen(img, (x - 20, y - h - 20, x + w + 30, y + 20), seed) as p:
        if area:
            poly = pts + [(pts[-1][0], y), (pts[0][0], y)]
            p.poly(p.wobble(poly, .4, True), tuple(min(255, int(c * .35 + 255 * .65)) for c in color))
            p.hatch(poly, tuple(int(c * .8 + 255 * .2) for c in color), gap=16, w=2.5)
        for k in range(1, 4): p.stroke([(x, y - h * k / 4), (x + w, y - h * k / 4)], 2, GRAY_L, amp=.3)
        p.stroke(pts, 8, color, amp=.8)
        if dots:
            for px, py in pts: p.shape(ellipse(px, py, 9, 9, n=14), WHITE, w=4, color=color, amp=.2)
        p.stroke([(x, y - h), (x, y), (x + w, y)], 6, amp=.6)

def candle_chart(img, x, y, w=600, h=360, candles=None, trend=1.0, n=10, seed=1):
    """Stock-market candlestick chart; (x, y) = bottom left corner. candles = [(open, close, high, low)…] or
    None for a random walk going up (trend > 0) or down (trend < 0)."""
    if candles is None:
        import random
        R, v, candles = random.Random(seed), 5.0, []
        for _ in range(n):
            o = v; v = max(.5, v + trend * .5 + R.uniform(-1, 1)); c = v
            candles.append((o, c, max(o, c) + R.uniform(.1, .6), min(o, c) - R.uniform(.1, .6)))
    lo, hi = min(c[3] for c in candles), max(c[2] for c in candles)
    Y = lambda v: y - h * .06 - h * .88 * (v - lo) / ((hi - lo) or 1)
    step = w * .92 / len(candles)
    with Pen(img, (x - 20, y - h - 20, x + w + 30, y + 20), seed) as p:
        for k in range(1, 4): p.stroke([(x, y - h * k / 4), (x + w, y - h * k / 4)], 2, GRAY_L, amp=.3)
        for k, (o, c, hgh, low) in enumerate(candles):
            cx = x + w * .06 + step * (k + .5)
            col = MONEY if c >= o else RED
            p.stroke([(cx, Y(hgh)), (cx, Y(low))], 3, amp=.2)
            top, bot = Y(max(o, c)), Y(min(o, c))
            if bot - top < 4: bot = top + 4
            p.shape([(cx - step * .3, top), (cx + step * .3, top), (cx + step * .3, bot), (cx - step * .3, bot)], col, w=3, amp=.3)
        p.stroke([(x, y - h), (x, y), (x + w, y)], 6, amp=.6)

def pie_chart(img, cx, cy, r=160, parts=(.5, .3, .2), colors=None, labels=None, seed=1):
    """Pie chart (budget split); parts are fractions or amounts; labels = text on each slice ("50%")."""
    colors = colors or PIE_COLORS
    total = sum(parts) or 1
    with Pen(img, (cx - r * 1.25, cy - r * 1.25, cx + r * 1.25, cy + r * 1.25), seed) as p:
        a = -math.pi / 2
        for k, v in enumerate(parts):
            b = a + 2 * math.pi * v / total
            n = max(3, int(40 * v / total))
            sl = [(cx, cy)] + [(cx + math.cos(a + (b - a) * j / n) * r, cy + math.sin(a + (b - a) * j / n) * r) for j in range(n + 1)]
            p.poly(p.wobble(sl, .4, True), colors[k % len(colors)])
            p.stroke([(cx, cy), sl[1]], 4, amp=.3)
            if labels and k < len(labels) and labels[k]:
                m = (a + b) / 2
                p.text(str(labels[k]), cx + math.cos(m) * r * .6, cy + math.sin(m) * r * .6, r * .2, fill=WHITE, stroke=INK,
                       sw=max(1, r * .012), warp=0)
            a = b
        p.stroke(ellipse(cx, cy, r, r, n=64), 6, amp=.8, closed=True)

def gauge(img, cx, cy, r=150, value=0.7, label=None, seed=1):
    """Half-circle meter from red to green with a needle (credit score, risk); value = 0…1."""
    cols = (RED, ORANGE, YELLOW, (170, 210, 80), MONEY)
    with Pen(img, (cx - r * 1.2, cy - r * 1.2, cx + r * 1.2, cy + r * .45), seed) as p:
        for k, col in enumerate(cols):
            a0, a1 = math.pi + math.pi * k / 5, math.pi + math.pi * (k + 1) / 5
            seg = [(cx + math.cos(a0 + (a1 - a0) * j / 8) * r, cy + math.sin(a0 + (a1 - a0) * j / 8) * r) for j in range(9)] + \
                  [(cx + math.cos(a1 - (a1 - a0) * j / 8) * r * .62, cy + math.sin(a1 - (a1 - a0) * j / 8) * r * .62) for j in range(9)]
            p.shape(seg, col, w=4, amp=.3)
        a = math.pi + math.pi * max(0.0, min(1.0, value))
        p.stroke([(cx, cy), (cx + math.cos(a) * r * .9, cy + math.sin(a) * r * .9)], r * .05, amp=.3)
        p.shape(ellipse(cx, cy, r * .09, r * .09, n=16), DARK, w=3, amp=.2)
        if label: p.text(str(label), cx, cy + r * .25, r * .22, warp=0)

def contract(img, cx, cy, h=300, title="CONTRACT", signed=True, stamp=None, ang=0.0, seed=1):
    """Paper document with text lines and a signature (loan, contract, tax form); stamp = text in a red stamp."""
    w = h * .74
    R = lambda pts: rotated(pts, cx, cy, ang)
    with Pen(img, (cx - h * .65, cy - h * .65, cx + h * .65, cy + h * .65), seed) as p:
        x0, y0 = cx - w / 2, cy - h / 2
        p.shape(R([(x0, y0), (cx + w / 2 - w * .14, y0), (cx + w / 2, y0 + w * .14), (cx + w / 2, cy + h / 2), (x0, cy + h / 2)]), PAPER, w=5)
        p.shape(R([(cx + w / 2 - w * .14, y0), (cx + w / 2 - w * .14, y0 + w * .14), (cx + w / 2, y0 + w * .14)]), PAPER_D, w=3, amp=.2)
        if title: p.text(title, *R([(cx - w * .04, y0 + h * .11)])[0], h * .065, warp=.4)
        for k in range(6):
            yy = y0 + h * (.24 + k * .08)
            p.stroke(R([(x0 + w * .12, yy), (x0 + w * (.88 if k % 3 != 2 else .6), yy)]), 3, GRAY, amp=.4)
        sy = cy + h * .34
        p.stroke(R([(cx + w * .02, sy), (cx + w * .4, sy)]), 2.5, amp=.2)
        if signed:
            p.stroke(R(spline([(cx + w * .04, sy - 6), (cx + w * .1, sy - 30), (cx + w * .13, sy - 4), (cx + w * .19, sy - 26),
                               (cx + w * .23, sy - 2), (cx + w * .3, sy - 22), (cx + w * .38, sy - 8)])), 3, BLUE, amp=.4)
        if stamp:
            sx, sy2 = R([(cx - w * .22, cy + h * .3)])[0]
            p.stroke(ellipse(sx, sy2, w * .17, w * .17, n=30), 4, RED, amp=.4, closed=True)
            p.text(str(stamp), sx, sy2, w * .07, fill=RED, warp=.3)

def ball_and_chain(img, cx, base, r=70, to=None, label="DEBT", seed=1, shadow=False):
    """Heavy iron ball with a chain (debt); to = (x, y) where the chain ends, e.g. a doodle's foot."""
    by = base - r
    tx, ty = to or (cx - r * 3, base - r * .2)
    with Pen(img, (min(cx, tx) - r * 1.3, min(by, ty) - r * 1.2, max(cx, tx) + r * 1.3, base + r * .3), seed) as p:
        if shadow: p.blob(cx, base, r * .9, r * .12, SHADE)
        L = math.hypot(cx - tx, by - ty) or 1
        n = max(3, int(L / (r * .32)))
        for k in range(n + 1):
            f = k / n
            x = tx + (cx - tx) * f
            y = ty + (by - ty) * f + math.sin(f * math.pi) * r * .35
            p.stroke(ellipse(x, y, r * .2 if k % 2 == 0 else r * .08, r * .12, rot=math.atan2(by - ty, cx - tx), n=16), r * .06,
                     DARK, amp=.2, closed=True)
        p.shape(ellipse(tx, ty, r * .25, r * .25, n=20), STEEL, w=r * .07, amp=.2)
        p.shape(ellipse(cx, by, r, r, n=48), DARK, w=r * .09)
        p.stroke(spline([(cx - r * .55, by - r * .2), (cx - r * .4, by - r * .55), (cx - r * .1, by - r * .7)]), r * .1, GRAY, amp=.3)
        if label: p.text(label, cx, by + r * .1, r * .36, fill=WHITE, warp=.4)

def umbrella(img, cx, cy, w=320, color=RED, seed=1):
    """Open umbrella (protection, emergency fund); (cx, cy) = tip of the canopy."""
    r = w / 2
    with Pen(img, (cx - r * 1.15, cy - r * .2, cx + r * 1.15, cy + r * 1.6), seed) as p:
        base = cy + r * .55
        p.limb([(cx, cy + r * .1), (cx, base + r * .8)], r * .04, DARK, 3)
        p.stroke(spline([(cx, base + r * .8), (cx + r * .02, base + r * .95), (cx + r * .14, base + r * .95), (cx + r * .15, base + r * .82)]),
                 r * .06, DARK, amp=.3)
        top = [(cx + math.cos(t) * r, base + math.sin(t) * r * .55) for t in (math.pi + math.pi * k / 30 for k in range(31))]
        scal = []
        for k in range(4):
            x0, x1 = cx - r + k * r / 2, cx - r + (k + 1) * r / 2
            scal += [(x0 + (x1 - x0) * j / 8, base - math.sin(math.pi * j / 8) * r * .1) for j in range(9)]
        canopy = top + scal[::-1]
        dark = tuple(int(v * .78) for v in color)
        p.poly(p.wobble(canopy, .5, True), color)
        for k in (1, 3):
            seg = [(cx - r + k * r / 2, base), (cx - r + (k + 1) * r / 2, base), (cx, base - r * .55)]
            with p.clip(canopy): p.poly(seg, dark)
        for k in range(1, 4): p.stroke([(cx, base - r * .55), (cx - r + k * r / 2, base)], 3, amp=.3)
        p.stroke(canopy, 6, amp=.6, closed=True)
        p.shape(ellipse(cx, base - r * .58, r * .04, r * .06, n=12), DARK, w=3, amp=.2)

def goal_thermometer(img, cx, base, h=480, fill=0.6, label=None, color=RED, seed=1, shadow=False):
    """Savings goal thermometer with tick marks; fill = 0…1; label = text above (the goal)."""
    w = h * .14
    with Pen(img, (cx - w * 2.6, base - h * 1.12, cx + w * 2.6, base + h * .05), seed) as p:
        if shadow: p.blob(cx, base, w * 1.2, h * .02, SHADE)
        br = w * .95
        by = base - br
        tube = rrect(cx - w / 2, base - h, cx + w / 2, by, w / 2)
        p.poly(p.wobble(tube, .4, True), WHITE)
        top = by - (by - (base - h) - w * .3) * max(0.0, min(1.0, fill))
        with p.clip(tube): p.poly([(cx - w, by + 2), (cx + w, by + 2), (cx + w, top), (cx - w, top)], color)
        p.stroke(tube, 5, amp=.4, closed=True)
        p.shape(ellipse(cx, by, br, br, n=32), color, w=5, amp=.4)
        for k in range(1, 6):
            yy = by - (by - (base - h) - w * .3) * k / 5
            p.stroke([(cx + w * .65, yy), (cx + w * (1.1 if k % 5 == 0 else .95), yy)], 3, amp=.1)
        if label: p.text(str(label), cx, base - h * 1.06, w * .9, fill=color, stroke=INK, sw=1.5, warp=.5)

def padlock(img, cx, cy, h=200, locked=True, color=GOLD, seed=1):
    """Padlock (security, locked savings); locked=False lifts the shackle."""
    w = h * .74
    with Pen(img, (cx - w * .7, cy - h * .9, cx + w * .7, cy + h * .55), seed) as p:
        lift = 0 if locked else h * .16
        body_t = cy - h * .1
        p.stroke(spline([(cx - w * .3, body_t - lift + (lift and h * .02)), (cx - w * .3, body_t - h * .35 - lift), (cx, body_t - h * .55 - lift),
                         (cx + w * .3, body_t - h * .35 - lift), (cx + w * .3, body_t - (lift and h * .2))]), h * .09, GRAY, amp=.4)
        p.shape(rrect(cx - w / 2, body_t, cx + w / 2, cy + h * .45, w * .12), color, w=6)
        p.shape(ellipse(cx, cy + h * .12, w * .09, w * .09, n=16), DARK, w=2, amp=.2)
        p.poly([(cx - w * .04, cy + h * .14), (cx + w * .04, cy + h * .14), (cx + w * .05, cy + h * .3), (cx - w * .05, cy + h * .3)], DARK)

def magnifier(img, cx, cy, r=80, ang=0.7, seed=1):
    """Magnifying glass (analysis, looking for hidden fees); (cx, cy) = center of the lens, ang = handle direction."""
    with Pen(img, (cx - r * 3, cy - r * 3, cx + r * 3, cy + r * 3), seed) as p:
        dx, dy = math.sin(ang), math.cos(ang)
        p.limb([(cx + dx * r * 1.05, cy + dy * r * 1.05), (cx + dx * r * 2.3, cy + dy * r * 2.3)], r * .22, WOOD_D, r * .06)
        p.shape(ellipse(cx, cy, r, r, n=44), GLASS, w=r * .14, color=DARK)
        p.stroke(spline([(cx - r * .6, cy - r * .1), (cx - r * .5, cy - r * .45), (cx - r * .15, cy - r * .62)]), r * .1, WHITE, amp=.2)

def rocket(img, cx, cy, h=300, ang=0.5, flame=True, color=RED, seed=1):
    """Rocket taking off (growth, 'to the moon'); ang = tilt from straight up."""
    w = h * .36
    R = lambda pts: rotated(pts, cx, cy, ang)
    with Pen(img, (cx - h * .8, cy - h * .8, cx + h * .8, cy + h * .8), seed) as p:
        bot = cy + h * .35
        if flame:
            p.shape(R(spline([(cx - w * .3, bot), (cx - w * .2, bot + h * .25), (cx, bot + h * .45), (cx + w * .2, bot + h * .25),
                              (cx + w * .3, bot)], closed=True)), ORANGE, w=4, amp=.5)
            p.shape(R(spline([(cx - w * .15, bot), (cx, bot + h * .26), (cx + w * .15, bot)], closed=True)), YELLOW, w=0, amp=.4)
        for sd in (-1, 1):
            p.shape(R([(cx + sd * w * .4, bot - h * .25), (cx + sd * w * .8, bot + h * .05), (cx + sd * w * .4, bot)]), color, w=5, amp=.4)
        body = spline([(cx, cy - h * .5), (cx + w * .45, cy - h * .15), (cx + w * .45, bot), (cx - w * .45, bot), (cx - w * .45, cy - h * .15)],
                      closed=True)
        p.shape(R(body), WHITE, w=6)
        p.shape(R(ellipse(cx, cy - h * .08, w * .2, w * .2, n=24)), GLASS, w=5, amp=.3)
        p.shape(R([(cx - w * .45, bot - h * .08), (cx + w * .45, bot - h * .08), (cx + w * .45, bot), (cx - w * .45, bot)]), color, w=4, amp=.3)

def balloon(img, cx, cy, r=110, label="%", color=RED, string=True, seed=1):
    """Balloon with a label (inflation, a bubble); string=True hangs a string below."""
    with Pen(img, (cx - r * 1.2, cy - r * 1.3, cx + r * 1.2, cy + r * 2.6), seed) as p:
        if string:
            p.stroke(spline([(cx, cy + r * 1.2), (cx + r * .15, cy + r * 1.6), (cx - r * .1, cy + r * 2.0), (cx + r * .05, cy + r * 2.4)]), 3, amp=.4)
        p.shape([(cx - r * .12, cy + r * 1.24), (cx + r * .12, cy + r * 1.24), (cx, cy + r * 1.08)], color, w=3, amp=.2)
        p.shape(spline([(cx, cy - r), (cx + r * .9, cy - r * .3), (cx + r * .55, cy + r * .75), (cx, cy + r * 1.1),
                        (cx - r * .55, cy + r * .75), (cx - r * .9, cy - r * .3)], closed=True), color, w=max(3, r * .05))
        p.stroke(spline([(cx - r * .55, cy - r * .3), (cx - r * .45, cy - r * .6), (cx - r * .2, cy - r * .78)]), r * .08, WHITE, amp=.2)
        if label: p.text(str(label), cx, cy + r * .1, r * (.7 if len(str(label)) <= 2 else .4), fill=WHITE, stroke=INK, sw=max(1, r * .015), warp=.6)

from . import cache_pieces
cache_pieces(globals())
