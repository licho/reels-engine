"""Sketch-style objects: money (bill, stack, pile, jar, big amount), school desk, stool, wallet, block arrow,
curved arrow, hatched bar chart, calendar and dashed divider. All take the image (img) and a 'seed'.
money_jar draws no floor shadow unless shadow=True."""
import math
from . import (Pen, WHITE, SHADE, RED, GREEN, GREEN_D, GREEN_L, MONEY, MONEY_D, GLASS, GLASS_D, WOOD, WOOD_D,
               BAND, BLUE, ellipse, rrect, rotated, spline)

# ---------- money ----------
def _bill(p, cx, cy, w, ang=0.0, label=None, edge=4):
    h = w * .46
    box = lambda k, kh: rotated([(cx - w * k, cy - h * kh), (cx + w * k, cy - h * kh), (cx + w * k, cy + h * kh),
                                 (cx - w * k, cy + h * kh)], cx, cy, ang)
    rect = box(.5, .5)
    p.poly(p.wobble(rect, .5, True), GREEN_L if label else GREEN)
    p.stroke(box(.42, .36), max(1.5, w * .025), GREEN_D, amp=.4, closed=True)
    p.poly(ellipse(cx, cy, w * .16, h * .3, rot=ang, n=20), WHITE if label else GREEN_L)
    if label: p.text(label, cx, cy, h * .42, fill=GREEN_D, warp=0)
    p.stroke(rect, edge, amp=.6, closed=True)

def bill(img, cx, cy, w=150, ang=0.0, label=None, seed=1):
    """Banknote centered on (cx, cy), 'w' px wide, turned 'ang' radians; label = text in the middle ("$10")."""
    r = w * .6
    with Pen(img, (cx - r, cy - r, cx + r, cy + r), seed) as p:
        _bill(p, cx, cy, w, ang, label)

def _brick(p, x, y, w, t):
    dx, dy = w * .22, w * .28
    top = [(x, y), (x + w, y), (x + w + dx, y - dy), (x + dx, y - dy)]
    front = [(x, y), (x + w, y), (x + w, y + t), (x, y + t)]
    side = [(x + w, y), (x + w + dx, y - dy), (x + w + dx, y - dy + t), (x + w, y + t)]
    p.poly(front, GREEN); p.poly(side, GREEN_D); p.poly(top, GREEN)
    for k in range(1, 4):
        p.stroke([(x + 2, y + t * k / 4), (x + w - 2, y + t * k / 4)], 1.8, GREEN_D, amp=.3)
    m = .18
    p.stroke([(x + w * m + dx * m, y - dy * m), (x + w * (1 - m) + dx * m, y - dy * m),
              (x + w * (1 - m) + dx * (1 - m), y - dy * (1 - m)), (x + w * m + dx * (1 - m), y - dy * (1 - m))],
             2, GREEN_D, amp=.3, closed=True)
    bx, bw = x + w * .5, w * .07                              # paper band
    p.poly([(bx - bw, y), (bx + bw, y), (bx + bw + dx, y - dy), (bx - bw + dx, y - dy)], BAND)
    p.poly([(bx - bw, y), (bx + bw, y), (bx + bw, y + t), (bx - bw, y + t)], BAND)
    for face in (top, front, side): p.stroke(face, 3.5, amp=.5, closed=True)

def money_stack(img, x, y, w=120, seed=1):
    """Banded stack of bills seen from the front and above; (x, y) = front top left corner."""
    with Pen(img, (x - 10, y - w * .4, x + w * 1.35, y + w * .35), seed) as p:
        _brick(p, x, y, w, w * .24)

def money_pile(img, cx, base, w=100, rows=(4, 3, 2, 1), seed=1):
    """Pyramid of money stacks centered on cx, sitting on y=base. rows = stacks per row, bottom first."""
    t, rise = w * .24, w * .28 * .55 + w * .24
    half = max(rows) * w / 2
    with Pen(img, (cx - half - 20, base - len(rows) * rise - w * .4, cx + half + w * .4, base + 20), seed) as p:
        for r, n in enumerate(rows):
            x0, y = cx - n * w / 2 + (r % 2) * w * .05, base - t - r * rise
            for k in range(n):
                _brick(p, x0 + k * w + p.rng.uniform(-4, 4), y + p.rng.uniform(-3, 3), w * .96, t)

def money_jar(img, cx, base, w=200, h=280, fill=.8, label=None, seed=1, shadow=False):
    """Glass jar sitting on y=base, filled with bills up to 'fill' (0…1); label = text on a white tag."""
    x0, x1, y0 = cx - w / 2, cx + w / 2, base - h
    with Pen(img, (x0 - w * .2, y0 - 10, x1 + w * .2, base + w * .1), seed) as p:
        if shadow: p.blob(cx, base, w * .6, w * .07, SHADE)
        body = rrect(x0, y0 + h * .08, x1, base, w * .2)
        p.poly(p.wobble(body, .6, True), GLASS)
        if fill:
            top, bw = base - h * .92 * fill, w * .36
            with p.clip(body):
                y = base - bw * .15
                while y > top - bw * .1:
                    x = x0 - bw * .2
                    while x < x1 + bw * .2:
                        _bill(p, x + p.rng.uniform(-8, 8), y, bw, p.rng.uniform(-.9, .9), edge=2.5)
                        x += bw * .55
                    y -= bw * .3
        p.stroke([(x0 + w * .12, y0 + h * .25), (x0 + w * .12, base - h * .25)], w * .05, WHITE, amp=.8)   # glints
        p.stroke([(x0 + w * .22, y0 + h * .22), (x0 + w * .22, y0 + h * .35)], w * .035, WHITE, amp=.5)
        p.stroke(body, 6, amp=1, closed=True)
        p.shape(rrect(x0 + w * .06, y0, x1 - w * .06, y0 + h * .1, 8), GLASS_D, w=5, amp=.6)
        if label:
            p.shape(rrect(cx - w * .3, base - h * .45, cx + w * .3, base - h * .3, 6), WHITE, w=3.5, amp=.5)
            p.text(label, cx, base - h * .375, h * .08, warp=0)

def money_text(img, text, cx, cy, size=170, color=MONEY, edge=MONEY_D, seed=1):
    """Big amount in bold green letters, slightly warped ("$3,650"). Centered on (cx, cy)."""
    wd = size * .62 * len(text) + size
    with Pen(img, (cx - wd / 2, cy - size, cx + wd / 2, cy + size), seed) as p:
        p.text(text, cx, cy, size, fill=color, stroke=edge, sw=size * .02, warp=1.3)

def wallet(img, cx, cy, w=110, seed=1):
    """Open brown wallet centered on (cx, cy)."""
    h = w * .62
    with Pen(img, (cx - w * .6, cy - h * .6, cx + w * .6, cy + h * .6), seed) as p:
        p.shape(rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 8), WOOD, w=5)
        p.shape(rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy - h * .05, 8), WOOD_D, w=4)

# ---------- furniture ----------
def school_desk(img, x, y, w=400, depth=46, color=WOOD, legs=170, seed=1):
    """School desk seen from the front; (x, y) = front left corner of the top. color = top (WOOD, WHITE…)."""
    dark = WOOD_D if color == WOOD else SHADE
    sh = depth * .6
    with Pen(img, (x - 20, y - depth - 10, x + w + sh + 20, y + legs + 15), seed) as p:
        for lx in (x + sh + 14, x + w + sh - 14): p.stroke([(lx, y - depth + 4), (lx, y - depth + legs - 26)], 6, amp=.6)
        for lx in (x + 14, x + w - 14):
            p.stroke([(lx, y + 18), (lx, y + legs)], 7, amp=.6)
            p.stroke([(lx - 9, y + legs), (lx + 9, y + legs)], 7, amp=.3)
        p.stroke([(x + 14, y + legs * .55), (x + w - 14, y + legs * .55)], 5, amp=.6)
        p.shape([(x, y), (x + w, y), (x + w + sh, y - depth), (x + sh, y - depth)], color, w=6)
        p.shape([(x, y), (x + w, y), (x + w, y + 18), (x, y + 18)], dark, w=6, amp=1)

def stool(img, cx, y, w=120, seed=1):
    """Three-legged wooden stool; (cx, y) = center of the seat."""
    with Pen(img, (cx - w * .7, y - w * .25, cx + w * .7, y + w), seed) as p:
        for dx in (-.35, 0, .35): p.stroke([(cx + dx * w, y + w * .1), (cx + dx * w * 1.2, y + w * .9)], 7, amp=.5)
        p.shape(ellipse(cx, y, w / 2, w * .13), WOOD, w=5)

# ---------- charts and signs ----------
def arrow(img, cx, cy, size=120, up=True, color=None, seed=1):
    """Fat block arrow, up (green by default) or down (red by default)."""
    color = color or (GREEN if up else RED)
    s, d = size, -1 if up else 1
    pts = [(cx, cy + d * s * .5), (cx + s * .42, cy + d * s * .05), (cx + s * .17, cy + d * s * .05),
           (cx + s * .17, cy - d * s * .5), (cx - s * .17, cy - d * s * .5), (cx - s * .17, cy + d * s * .05),
           (cx - s * .42, cy + d * s * .05)]
    with Pen(img, (cx - s * .5, cy - s * .6, cx + s * .5, cy + s * .6), seed) as p:
        p.shape(pts, color, w=max(3, s * .05), amp=.8)

def curve_arrow(img, pts, w=10, color=GREEN, seed=1):
    """Hand-drawn curved arrow through the points, with the head at the last one."""
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    m = w * 5
    with Pen(img, (min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m), seed) as p:
        path = p.stroke(spline(pts), w, color, amp=1, taper=False)
        (ax, ay), (bx, by) = path[-6], path[-1]
        a, L = math.atan2(by - ay, bx - ax), w * 3.2
        for da in (2.6, -2.6):
            p.stroke([(bx + math.cos(a + da) * L, by + math.sin(a + da) * L), (bx, by)], w, color, amp=.4)

def hatched_chart(img, x, base, values, bar_w=70, gap=14, color=GREEN, hatch=GREEN_D, seed=1):
    """Bar chart with marker hatching; bars start at x and stand on y=base; values = bar heights in px."""
    right = x + len(values) * (bar_w + gap) + 10
    with Pen(img, (x - 30, base - max(values) - 15, right + 10, base + 15), seed) as p:
        p.stroke([(x - 20, base), (right, base)], 6, amp=1)
        for i, v in enumerate(values):
            bx = x + i * (bar_w + gap)
            pts = [(bx, base), (bx + bar_w, base), (bx + bar_w, base - v), (bx, base - v)]
            p.poly(p.wobble(pts, .6, True), color)
            p.hatch(pts, hatch, gap=16, ang=-1.0, w=3)
            p.stroke(pts, 5, amp=1, closed=True)

def wall_calendar(img, x, y, w=150, color=BLUE, label=None, seed=1):
    """Calendar with rings; (x, y) = top left corner. label = big text instead of the grid of days ("1 YEAR")."""
    h = w * .95
    with Pen(img, (x - 10, y - h * .12, x + w + 10, y + h + 10), seed) as p:
        p.shape(rrect(x, y, x + w, y + h, 10), WHITE, w=5)
        p.shape(rrect(x, y, x + w, y + h * .22, 8), color, w=5)
        for k in range(4):
            rx = x + w * (.2 + .2 * k)
            p.stroke([(rx, y - h * .07), (rx, y + h * .07)], 6, amp=.3)
        if label:
            p.text(label, x + w / 2, y + h * .6, w * .22, warp=0)
            return
        for r in range(4):
            for c in range(5):
                gx, gy = x + w * (.1 + .165 * c), y + h * (.3 + .16 * r)
                p.stroke([(gx, gy), (gx + w * .12, gy), (gx + w * .12, gy + h * .11), (gx, gy + h * .11)], 2.5, amp=.3, closed=True)

def dashed_line(img, x, y0, y1, dash=22, gap=16, color=(150, 150, 155), seed=1):
    """Vertical dashed divider from y0 to y1 (split screens)."""
    with Pen(img, (x - 6, y0 - 6, x + 6, y1 + 6), seed) as p:
        y = y0
        while y < y1:
            p.stroke([(x, y), (x, min(y1, y + dash))], 3, color, amp=.3)
            y += dash + gap
