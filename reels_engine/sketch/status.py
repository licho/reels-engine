"""Sketch-style status pieces, like the hand-drawn interface of a game or a planning sheet: a time card (clock +
time + day), an inventory sheet with rows, a stat bar (hunger, health…), an alert box, a status panel with
lights, and a camera monitor with several feeds. All take the image (img) and a 'seed'; texts are the caller's.

    time_card(img, 540, 300, 460, "06:42 AM", day="DAY 0")
    inventory_sheet(img, 760, 900, 420, title="INVENTORY", rows=[("MONEY", "$50,000"), ("FOOD", "3 DAYS")])
    stat_bar(img, 120, 1500, 400, .35, label="HUNGER")
    status_panel(img, 540, 1200, 520, rows=[("WATER", "ok"), ("POWER", "bad")])"""
import math
import random
from . import Pen, INK, WHITE, RED, GREEN, GREEN_D, ellipse, rrect, rotated, spline
from .everyday import YELLOW, GRAY, GRAY_L, DARK
from .survival import PAPER, PAPER_D, NIGHT, _ltext, _fit, _shade

STATES = {"ok": GREEN, "warn": YELLOW, "bad": RED, "off": GRAY}
SCREEN = (34, 52, 44)

def _level_color(v):
    return RED if v < .34 else (YELLOW if v < .67 else GREEN)

def time_card(img, cx, cy, w=460, time="06:42 AM", day=None, color=PAPER, seed=1):
    """Paper card with a small clock (hands set to 'time') and the time in big letters; day = second line."""
    h = w * (.42 if day else .3)
    with Pen(img, (cx - w * .6, cy - h * .7, cx + w * .6, cy + h * .7), seed) as p:
        p.shape(rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, w * .04), color, w=6, amp=.5)
        r = min(h * .32, w * .12)
        ox, oy = cx - w / 2 + r + w * .06, cy
        p.shape(ellipse(ox, oy, r, r, n=36), WHITE, w=5, amp=.4)
        try:
            hh, mm = (int(v) for v in str(time).split()[0].split(":")[:2])
        except ValueError:
            hh, mm = 3, 0
        for ang_, L, ww in (((hh % 12 + mm / 60) / 12 * 2 * math.pi, .5, 5), (mm / 60 * 2 * math.pi, .78, 3.5)):
            p.stroke([(ox, oy), (ox + math.sin(ang_) * r * L, oy - math.cos(ang_) * r * L)], ww, amp=.1)
        p.poly(ellipse(ox, oy, r * .08, r * .08, n=10), INK)
        tx0, tx1 = ox + r + w * .05, cx + w / 2 - w * .05
        if day:
            size = _fit(time, h * .38, tx1 - tx0)
            p.text(time, (tx0 + tx1) / 2, cy - h * .16, size, warp=1)
            p.stroke([(tx0, cy + h * .04), (tx1, cy + h * .04)], 3, PAPER_D, amp=.4)
            p.text(day, (tx0 + tx1) / 2, cy + h * .24, _fit(day, h * .24, tx1 - tx0), fill=RED, warp=1)
        else:
            p.text(time, (tx0 + tx1) / 2, cy, _fit(time, h * .5, tx1 - tx0), warp=1)

def inventory_sheet(img, cx, cy, w=440, title=None, rows=(), checks=False, ang=-.02, seed=1):
    """Planning sheet on lined paper: a title and rows of (label, value) in hand lettering; checks=True ticks each
    row. Height grows with the rows."""
    n = max(1, len(rows))
    lh = w * .13
    h = lh * n + (w * .2 if title else w * .06) + w * .06
    with Pen(img, (cx - w * .65, cy - h * .65, cx + w * .65, cy + h * .65), seed) as p:
        R = lambda pts: rotated(pts, cx, cy, ang)
        x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
        p.shape(R([(x0 + 8, y0 + 8), (x1 + 8, y0 + 8), (x1 + 8, y1 + 8), (x0 + 8, y1 + 8)]), PAPER_D, w=0)
        p.shape(R([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), PAPER, w=5, amp=.5)
        p.stroke(R([(x0 + w * .1, y0 + 4), (x0 + w * .1, y1 - 4)]), 2.5, (230, 140, 140), amp=.3)
        ty = y0 + w * .03
        if title:
            p.text(title, cx, ty + w * .07, _fit(title, w * .08, w * .8), warp=1)
            p.stroke(R([(x0 + w * .15, ty + w * .14), (x1 - w * .15, ty + w * .14)]), 4, RED, amp=.5)
            ty += w * .17
        lx = x0 + w * (.2 if checks else .14)
        size = lh * .55
        for row in rows:
            label, value = (row if isinstance(row, (tuple, list)) else (row, ""))
            size = min(size, _fit(f"{label}: {value}" if value != "" else str(label), lh * .55, x1 - lx - w * .05))
        for k, row in enumerate(rows):
            label, value = (row if isinstance(row, (tuple, list)) else (row, ""))
            yy = ty + lh * (k + .5)
            p.stroke(R([(x0 + 6, yy + lh * .45), (x1 - 6, yy + lh * .45)]), 2, (180, 200, 230), amp=.3)
            if checks:
                q = R([(x0 + w * .14, yy)])[0]
                p.stroke([(q[0] - w * .03, q[1]), (q[0] - w * .01, q[1] + w * .025), (q[0] + w * .03, q[1] - w * .03)], 5, GREEN_D, amp=.1)
            text = f"{label}: {value}" if value != "" else str(label)
            if value != "":
                lt = f"{label}:"
                from PIL import ImageFont
                from . import FONT
                lw = ImageFont.truetype(FONT, int(size)).getlength(lt + " ")
                (ax, ay), (bx, by) = R([(lx, yy), (lx + lw, yy)])
                _ltext(p, lt, ax, ay, size, DARK)
                _ltext(p, str(value), bx, by, size, INK)
            else:
                ax, ay = R([(lx, yy)])[0]
                _ltext(p, text, ax, ay, size, DARK)

def stat_bar(img, x, y, w=420, value=.5, label=None, color=None, seed=1):
    """Hand-drawn meter bar from (x, y) (top left of the bar), filled to value = 0…1 with hatching; the color goes
    red → yellow → green with the value unless 'color' is given. label above it, the percent at the right."""
    h = w * .12
    col = color or _level_color(value)
    with Pen(img, (x - 20, y - (h * 1.4 if label else 20), x + w + 20, y + h + 20), seed) as p:
        if label:
            size = _fit(label, h * .8, w * .7)
            _ltext(p, label, x, y - h * .6, size)
            pc = f"{round(value * 100)} %"
            from PIL import ImageFont
            from . import FONT
            pw = ImageFont.truetype(FONT, int(size)).getlength(pc)
            _ltext(p, pc, x + w - pw, y - h * .6, size, _shade(col, .8))
        box = rrect(x, y, x + w, y + h, h * .3)
        p.shape(box, WHITE, w=0)
        v = max(0.0, min(1.0, value))
        if v > 0:
            fill = rrect(x + 4, y + 4, x + 4 + (w - 8) * v, y + h - 4, h * .25)
            p.poly(p.wobble(fill, .4, True), col)
            p.hatch(fill, _shade(col, .78), gap=12, w=2.5)
        p.stroke(box, 5, amp=.5, closed=True)

def alert_box(img, cx, cy, w=620, text="!", color=RED, t=None, seed=1):
    """Warning box with a double border, a warning triangle and the text; t (optional) makes the border blink."""
    h = w * .2
    on = True if t is None else (int(t * 3) % 2 == 0)
    with Pen(img, (cx - w * .6, cy - h * .8, cx + w * .6, cy + h * .8), seed) as p:
        p.shape(rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 6), WHITE, w=6, color=color if on else DARK, amp=.6)
        p.stroke(rrect(cx - w / 2 + 10, cy - h / 2 + 10, cx + w / 2 - 10, cy + h / 2 - 10, 4), 3, color, amp=.5, closed=True)
        tx, r = cx - w / 2 + h * .55, h * .3
        tri = [(tx, cy - r), (tx + r * 1.1, cy + r * .8), (tx - r * 1.1, cy + r * .8)]
        p.shape(tri, YELLOW, w=4, amp=.3)
        p.text("!", tx, cy + r * .2, r * 1.1, warp=0)
        x0 = tx + r * 1.4
        p.text(text, (x0 + cx + w / 2 - 18) / 2, cy, _fit(text, h * .36, cx + w / 2 - 18 - x0), fill=color, warp=1)

def status_panel(img, cx, cy, w=520, rows=(), title=None, seed=1):
    """Dark control panel with one row per system: a light and the label; rows = [(label, state)] with state ok
    (green), warn (yellow), bad (red) or off (grey), or [(label, state, "text")] to print a value at the right."""
    n = max(1, len(rows))
    lh = w * .13
    h = lh * n + w * (.16 if title else .06)
    with Pen(img, (cx - w * .6, cy - h * .65, cx + w * .6, cy + h * .65), seed) as p:
        x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
        p.shape(rrect(x0, y0, x1, y1, w * .04), (70, 74, 84), w=6, amp=.5)
        for q in ((x0 + 12, y0 + 12), (x1 - 12, y0 + 12), (x0 + 12, y1 - 12), (x1 - 12, y1 - 12)): p.poly(ellipse(*q, 4, 4, n=8), GRAY)
        ty = y0 + w * .03
        if title:
            p.text(title, cx, ty + w * .045, _fit(title, w * .055, w * .8), fill=GRAY_L, warp=0)
            ty += w * .1
        for k, row in enumerate(rows):
            label, state = row[0], row[1]
            yy = ty + lh * (k + .5)
            p.shape(rrect(x0 + w * .04, yy - lh * .4, x1 - w * .04, yy + lh * .4, 5), (44, 48, 56), w=3, amp=.2)
            col = STATES.get(state, state if isinstance(state, tuple) else GRAY)
            lx = x0 + w * .11
            if state != "off": p.poly(ellipse(lx, yy, lh * .26, lh * .26, n=20), tuple((a + b) // 2 for a, b in zip(col, (44, 48, 56))))
            p.shape(ellipse(lx, yy, lh * .17, lh * .17, n=20), col, w=3, amp=.2)
            p.poly(ellipse(lx - lh * .05, yy - lh * .05, lh * .05, lh * .05, n=8), WHITE)
            extra = row[2] if len(row) > 2 else None
            tx1 = x1 - w * (.3 if extra else .07)
            _ltext(p, str(label), lx + lh * .4, yy, _fit(str(label), lh * .45, tx1 - lx - lh * .4), WHITE)
            if extra:
                size = _fit(str(extra), lh * .42, w * .22)
                from PIL import ImageFont
                from . import FONT
                ew = ImageFont.truetype(FONT, int(size)).getlength(str(extra))
                _ltext(p, str(extra), x1 - w * .07 - ew, yy, size, col)

def _figure(p, x, base, s, color):
    r = 14 * s
    p.poly(ellipse(x, base - 62 * s, r, r, n=14), color)
    p.poly([(x - 12 * s, base - 48 * s), (x + 12 * s, base - 48 * s), (x + 10 * s, base - 18 * s), (x - 10 * s, base - 18 * s)], color)
    for sd in (-1, 1):
        p.stroke([(x + 5 * sd * s, base - 20 * s), (x + 9 * sd * s, base)], 4 * s, color, amp=.1)
    p.stroke([(x + 10 * s, base - 44 * s), (x + 30 * s, base - 46 * s)], 4 * s, color, amp=.1)

def camera_monitor(img, cx, cy, w=560, feeds=(0, 2, 0, 5), night=True, rec=True, labels=True, t=0.0, seed=1):
    """Security monitor split into 2×2 camera feeds (or 1 / 3×3, by len(feeds)); each number in feeds is how many
    figures that camera sees. night=True uses green night-vision tint. rec=True blinks a red REC dot with t."""
    n = len(feeds)
    cols = 1 if n == 1 else (2 if n <= 4 else 3)
    rws = math.ceil(n / cols)
    h = w * .72
    rng = random.Random(seed)
    bg = (60, 92, 70) if night else (190, 210, 220)
    fg = (24, 40, 30) if night else NIGHT
    with Pen(img, (cx - w * .6, cy - h * .7, cx + w * .6, cy + h * .75), seed) as p:
        p.shape(rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, w * .04), DARK, w=6, amp=.4)
        p.shape(rrect(cx - w * .1, cy + h / 2, cx + w * .1, cy + h * .6, 3), GRAY, w=4, amp=.2)
        ix0, iy0, ix1, iy1 = cx - w * .45, cy - h * .42, cx + w * .45, cy + h * .42
        cw, ch = (ix1 - ix0) / cols, (iy1 - iy0) / rws
        for i, count in enumerate(feeds):
            fx0, fy0 = ix0 + cw * (i % cols), iy0 + ch * (i // cols)
            cell = [(fx0 + 3, fy0 + 3), (fx0 + cw - 3, fy0 + 3), (fx0 + cw - 3, fy0 + ch - 3), (fx0 + 3, fy0 + ch - 3)]
            p.poly(cell, bg)
            with p.clip(cell):
                hy = fy0 + ch * (.45 + .1 * rng.random())
                p.poly([(fx0, hy), (fx0 + cw, hy - ch * .05), (fx0 + cw, fy0 + ch), (fx0, fy0 + ch)], _shade(bg, .8))
                for k in range(int(cw / 30)):
                    px = fx0 + k * 30 + 10
                    p.stroke([(px, hy + ch * .1), (px, hy - ch * .05)], 2.5, fg, amp=0)
                p.stroke([(fx0, hy - ch * .02), (fx0 + cw, hy - ch * .07)], 2, fg, amp=.2)
                for k in range(count):
                    s = ch / 170 * rng.uniform(.7, 1.2)
                    _figure(p, fx0 + cw * rng.uniform(.12, .88) + math.sin(t + k) * 4, hy + ch * rng.uniform(.15, .4), s, fg)
                for k in range(0, int(ch), 12): p.stroke([(fx0, fy0 + k), (fx0 + cw, fy0 + k)], 1, _shade(bg, 1.08), amp=0, taper=False)
            if labels: p.text(f"CAM {i + 1}", fx0 + cw * .2, fy0 + ch * .1, min(ch * .09, 22), fill=WHITE, warp=0)
        for k in range(1, cols): p.stroke([(ix0 + cw * k, iy0), (ix0 + cw * k, iy1)], 4, DARK, amp=0)
        for k in range(1, rws): p.stroke([(ix0, iy0 + ch * k), (ix1, iy0 + ch * k)], 4, DARK, amp=0)
        if rec and int(t * 2) % 2 == 0:
            p.poly(ellipse(ix1 - w * .1, cy - h * .46, w * .013, w * .013, n=12), RED)
            p.text("REC", ix1 - w * .05, cy - h * .46, w * .028, fill=RED, warp=0)

from . import cache_pieces
cache_pieces(globals())
