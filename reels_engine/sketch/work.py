"""Sketch-style jobs, trades and office: the doodle dressed as a medic, nurse, chef, police officer, firefighter,
builder, scientist, teacher, farmer, mechanic or pilot; work hats; trade tools (hammer, wrench, screwdriver, shovel,
paint roller, frying pan, toolbox, ladder, flask, microscope, scissors, book); and office things (desk, office chair,
monitor, filing cabinet, printer, briefcase, mug, stapler, sticky note, clipboard, folder, whiteboard, potted plant,
water cooler, desk lamp, pencil cup, ID badge). All take the image (img) and a 'seed'. Nothing draws a floor shadow
unless shadow=True.

    a = chef(img, 300, FLOOR, .9, held="pan")
    office_desk(img, 760, FLOOR, 420, monitor=True)

Hand tools take the grip point (where the hand holds them) and 'ang' = tilt from straight up, in radians
(0 = up, .5 = leaning right, math.pi = down)."""
import math
from . import Pen, INK, WHITE, RED, RED_D, GREEN, GREEN_L, GLASS, GLASS_D, WOOD, WOOD_D, BLUE, ellipse, rrect, rotated, spline
from .everyday import YELLOW, GOLD, GOLD_D, GRAY, GRAY_L, DARK, LEAF, LEAF_D, bumpy
from .humans import doodle

STEEL, STEEL_D = (196, 202, 212), (130, 136, 150)
NAVY, NAVY_D = (44, 62, 112), (28, 40, 76)
TEAL, TEAL_D = (70, 170, 170), (40, 120, 120)
DENIM, DENIM_D = (80, 112, 170), (52, 76, 124)
ORANGE, ORANGE_D = (240, 128, 40), (180, 84, 20)
KHAKI = (196, 168, 110)
STRAW, STRAW_D = (236, 206, 130), (190, 156, 80)
FIRE_RED = (200, 46, 36)
REFLECT = (236, 236, 120)
PURPLE = (130, 100, 170)
CREAM = (248, 244, 232)
TERRACOTTA = (200, 110, 70)
BEIGE, BEIGE_D = (226, 220, 204), (180, 172, 152)

def _dir(ang):
    return math.sin(ang), -math.cos(ang)

def _axis(gx, gy, L, ang):
    """Point along a tool: a = along its length (in L), b = sideways (in L)."""
    dx, dy = _dir(ang)
    return lambda a, b: (gx + dx * a * L - dy * b * L, gy + dy * a * L + dx * b * L)

# ---------- hand tools ----------
def _hammer(p, gx, gy, L, ang):
    P = _axis(gx, gy, L, ang)
    p.shape([P(-.18, -.035), P(.72, -.03), P(.72, .03), P(-.18, .035)], WOOD, w=max(3, L * .016), amp=.4)
    head = [P(.68, -.24), P(.86, -.24), P(.86, .1), P(.8, .2), P(.75, .26), P(.74, .1), P(.68, .1)]
    p.shape(head, STEEL, w=max(3, L * .018), amp=.4)
    p.stroke([P(.7, -.22), P(.84, -.22)], max(2, L * .01), WHITE, amp=.1)

def _wrench(p, gx, gy, L, ang):
    P = _axis(gx, gy, L, ang)
    p.shape([P(-.12, -.05), P(.72, -.045), P(.72, .045), P(-.12, .05)], STEEL, w=max(3, L * .016), amp=.4)
    p.shape([P(.68, -.13), P(.9, -.16), P(.94, -.06), P(.8, -.05), P(.8, .05), P(.94, .06), P(.9, .16), P(.68, .13)],
            STEEL, w=max(3, L * .018), amp=.4)
    p.shape(ellipse(*P(-.16, 0), L * .1, L * .1, n=24), STEEL, w=max(3, L * .016), amp=.3)
    p.poly(ellipse(*P(-.16, 0), L * .045, L * .045, n=16), WHITE)
    p.stroke([P(.1, -.02), P(.55, -.02)], max(2, L * .01), WHITE, amp=.1)

def _screwdriver(p, gx, gy, L, ang, color=RED):
    P = _axis(gx, gy, L, ang)
    p.shape([P(.3, -.018), P(.88, -.014), P(.92, 0), P(.88, .014), P(.3, .018)], STEEL, w=max(2.5, L * .012), amp=.2)
    p.shape(spline([P(-.18, 0), P(-.15, -.07), P(.0, -.08), P(.3, -.06), P(.34, 0), P(.3, .06), P(.0, .08), P(-.15, .07)], closed=True),
            color, w=max(3, L * .016), amp=.3)
    for b in (-.035, .035): p.stroke([P(-.1, b), P(.25, b)], max(2, L * .008), tuple(int(v * .7) for v in color), amp=.1)

def _shovel(p, gx, gy, L, ang):
    P = _axis(gx, gy, L, ang)
    p.limb([P(-.45, 0), P(.55, 0)], L * .04, WOOD, max(2, L * .012))
    p.limb([P(-.45, -.1), P(-.45, .1)], L * .04, WOOD_D, max(2, L * .012))
    blade = spline([P(.55, -.05), P(.6, -.16), P(.95, -.14), P(1.08, 0), P(.95, .14), P(.6, .16), P(.55, .05)], closed=True)
    p.shape(blade, STEEL, w=max(3, L * .016), amp=.4)
    p.stroke([P(.65, -.08), P(.92, -.06)], max(2, L * .01), WHITE, amp=.1)

def _pan(p, gx, gy, L, ang):
    P = _axis(gx, gy, L, ang)
    p.limb([P(-.12, 0), P(.36, 0)], L * .06, DARK, max(2, L * .012))
    cx, cy = P(.64, 0)
    p.shape(ellipse(cx, cy, L * .3, L * .3, n=40), DARK, w=max(3, L * .02), amp=.4)
    p.poly(ellipse(cx, cy, L * .23, L * .23, n=36), (90, 90, 98))
    p.stroke(spline([(cx - L * .14, cy - L * .1), (cx - L * .06, cy - L * .17), (cx + L * .06, cy - L * .18)]), max(2, L * .014), GRAY_L, amp=.2)

def _roller(p, gx, gy, L, ang, color=BLUE):
    P = _axis(gx, gy, L, ang)
    p.limb([P(-.15, 0), P(.3, 0)], L * .07, YELLOW, max(2, L * .012))
    p.stroke([P(.3, 0), P(.55, 0), P(.62, .12), P(.75, .12)], max(3, L * .022), STEEL_D, amp=.2)
    p.shape([P(.68, -.2), P(.68, .44), P(.88, .44), P(.88, -.2)], color, w=max(3, L * .018), amp=.4)
    p.stroke([P(.72, -.15), P(.72, .38)], max(2, L * .012), WHITE, amp=.1)

def _book(p, cx, cy, h, color=RED, ang=0.0, title=None):
    w = h * .74
    R = lambda pts: rotated(pts, cx, cy, ang)
    p.shape(R(rrect(cx - w / 2 + 6, cy - h / 2 + 6, cx + w / 2 + 6, cy + h / 2 + 6, 4)), WHITE, w=4, amp=.3)
    p.shape(R(rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 5)), color, w=5, amp=.4)
    p.stroke(R([(cx - w / 2 + w * .12, cy - h / 2 + 3), (cx - w / 2 + w * .12, cy + h / 2 - 3)]), 3, tuple(int(v * .7) for v in color), amp=.2)
    if title: p.text(title, *R([(cx + w * .05, cy - h * .15)])[0], h * .14, fill=WHITE, warp=0)

def _flask(p, cx, cy, h, liquid=GREEN):
    w = h * .7
    base, top = cy + h / 2, cy - h / 2
    body = [(cx - w * .12, top + h * .12), (cx - w * .12, top + h * .4), (cx - w / 2, base - h * .04), (cx - w * .46, base),
            (cx + w * .46, base), (cx + w / 2, base - h * .04), (cx + w * .12, top + h * .4), (cx + w * .12, top + h * .12)]
    p.poly(p.wobble(body, .4, True), GLASS)
    with p.clip(body):
        ly = base - h * .32
        p.poly([(cx - w, ly), (cx + w, ly), (cx + w, base + 4), (cx - w, base + 4)], liquid)
    for k, (bx, by, br) in enumerate(((-.1, .2, .05), (.08, .1, .035), (0, .3, .03))):
        p.stroke(ellipse(cx + bx * w, ly - by * h + h * .25, br * h, br * h, n=12), 2, WHITE, amp=0, closed=True)
    p.stroke(body, max(3, h * .025), amp=.4, closed=True)
    p.shape(rrect(cx - w * .18, top + h * .06, cx + w * .18, top + h * .14, 3), GLASS_D, w=max(3, h * .02), amp=.2)

def _clipboard(p, cx, cy, h, ang=0.0, checks=True):
    w = h * .74
    R = lambda pts: rotated(pts, cx, cy, ang)
    p.shape(R(rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 6)), WOOD, w=5, amp=.4)
    p.shape(R(rrect(cx - w * .4, cy - h * .38, cx + w * .4, cy + h * .44, 3)), WHITE, w=3, amp=.3)
    p.shape(R(rrect(cx - w * .2, cy - h * .53, cx + w * .2, cy - h * .38, 4)), STEEL, w=4, amp=.3)
    for k in range(4):
        yy = cy - h * .22 + k * h * .16
        if checks:
            p.stroke(R([(cx - w * .3, yy), (cx - w * .25, yy + h * .04), (cx - w * .16, yy - h * .05)]), max(2, h * .018), GREEN, amp=.1)
        p.stroke(R([(cx - w * .08, yy), (cx + w * .3, yy)]), max(2, h * .012), GRAY, amp=.3)

def hammer(img, gx, gy, L=220, ang=0.0, seed=1):
    """Claw hammer held at (gx, gy); ang = tilt from straight up."""
    with Pen(img, (gx - L * 1.1, gy - L * 1.1, gx + L * 1.1, gy + L * 1.1), seed) as p: _hammer(p, gx, gy, L, ang)

def wrench(img, gx, gy, L=220, ang=0.0, seed=1):
    """Open-end wrench held at (gx, gy)."""
    with Pen(img, (gx - L * 1.2, gy - L * 1.2, gx + L * 1.2, gy + L * 1.2), seed) as p: _wrench(p, gx, gy, L, ang)

def screwdriver(img, gx, gy, L=200, ang=0.0, color=RED, seed=1):
    """Screwdriver held at (gx, gy); color = handle."""
    with Pen(img, (gx - L * 1.1, gy - L * 1.1, gx + L * 1.1, gy + L * 1.1), seed) as p: _screwdriver(p, gx, gy, L, ang, color)

def shovel(img, gx, gy, L=300, ang=0.0, seed=1):
    """Shovel held at (gx, gy), the middle of the shaft."""
    with Pen(img, (gx - L * 1.2, gy - L * 1.2, gx + L * 1.2, gy + L * 1.2), seed) as p: _shovel(p, gx, gy, L, ang)

def frying_pan(img, gx, gy, L=240, ang=0.0, seed=1):
    """Frying pan held by the handle at (gx, gy)."""
    with Pen(img, (gx - L * 1.1, gy - L * 1.1, gx + L * 1.1, gy + L * 1.1), seed) as p: _pan(p, gx, gy, L, ang)

def paint_roller(img, gx, gy, L=220, ang=0.0, color=BLUE, seed=1):
    """Paint roller held at (gx, gy); color = paint."""
    with Pen(img, (gx - L * 1.1, gy - L * 1.1, gx + L * 1.1, gy + L * 1.1), seed) as p: _roller(p, gx, gy, L, ang, color)

def book(img, cx, cy, h=180, color=RED, ang=0.0, title=None, seed=1):
    """Closed hardcover book; title = text on the cover."""
    with Pen(img, (cx - h * .7, cy - h * .7, cx + h * .7, cy + h * .7), seed) as p: _book(p, cx, cy, h, color, ang, title)

def flask(img, cx, cy, h=200, liquid=GREEN, seed=1):
    """Lab flask (Erlenmeyer) with bubbling liquid."""
    with Pen(img, (cx - h * .5, cy - h * .6, cx + h * .5, cy + h * .6), seed) as p: _flask(p, cx, cy, h, liquid)

def clipboard(img, cx, cy, h=220, ang=0.0, checks=True, seed=1):
    """Clipboard with a checklist (checks=False leaves the boxes unticked)."""
    with Pen(img, (cx - h * .7, cy - h * .7, cx + h * .7, cy + h * .7), seed) as p: _clipboard(p, cx, cy, h, ang, checks)

def toolbox(img, cx, base, w=260, color=RED, seed=1, shadow=False):
    """Metal toolbox with a handle, tools peeking out."""
    h = w * .5
    with Pen(img, (cx - w * .6, base - h * 1.5, cx + w * .6, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .04)
        top = base - h
        _wrench(p, cx + w * .1, top + h * .1, w * .5, -.5)
        _screwdriver(p, cx - w * .2, top + h * .15, w * .45, .35, YELLOW)
        p.stroke(spline([(cx - w * .25, top), (cx - w * .25, top - h * .35), (cx + w * .25, top - h * .35), (cx + w * .25, top)]), w * .035, DARK, amp=.3)
        p.shape([(cx - w / 2, top), (cx + w / 2, top), (cx + w * .48, base), (cx - w * .48, base)], color, w=6)
        p.stroke([(cx - w / 2, top + h * .28), (cx + w / 2, top + h * .28)], 4, tuple(int(v * .7) for v in color), amp=.3)
        p.shape(rrect(cx - w * .08, top + h * .18, cx + w * .08, top + h * .38, 3), STEEL, w=3, amp=.2)

def ladder(img, cx, base, h=460, seed=1, shadow=False):
    """Wooden step ladder seen from the front."""
    with Pen(img, (cx - h * .35, base - h * 1.05, cx + h * .35, base + h * .04), seed) as p:
        if shadow: p.blob(cx, base, h * .25, h * .025)
        top = base - h
        for sd in (-1, 1): p.limb([(cx + sd * h * .1, top), (cx + sd * h * .2, base)], h * .03, WOOD, 4)
        for k in range(1, 6):
            f = k / 6
            hw = h * (.1 + .1 * f)
            p.limb([(cx - hw, top + h * f), (cx + hw, top + h * f)], h * .022, WOOD, 3.5)
        p.shape(rrect(cx - h * .13, top - h * .03, cx + h * .13, top + h * .02, 4), WOOD_D, w=4, amp=.3)

def microscope(img, cx, base, h=300, seed=1, shadow=False):
    """Lab microscope standing on the table."""
    w = h * .7
    with Pen(img, (cx - w * .7, base - h * 1.05, cx + w * .7, base + h * .04), seed) as p:
        if shadow: p.blob(cx, base, w * .5, h * .03)
        p.shape(rrect(cx - w * .45, base - h * .08, cx + w * .35, base, 6), DARK, w=5, amp=.3)
        arm = spline([(cx + w * .2, base - h * .08), (cx + w * .28, base - h * .45), (cx + w * .12, base - h * .78)])
        p.stroke(arm, h * .09, DARK, amp=.3)
        p.stroke(arm, h * .05, GRAY, amp=.3, taper=False)
        p.shape(rrect(cx - w * .3, base - h * .36, cx + w * .2, base - h * .31, 3), DARK, w=4, amp=.2)
        p.shape(rrect(cx - w * .1, base - h * .345, cx + w * .02, base - h * .325, 2), GLASS, w=2, amp=.1)
        tube = rotated(rrect(cx - w * .1, base - h * 1.0, cx + w * .06, base - h * .42, 6), cx - w * .02, base - h * .7, -.35)
        p.shape(tube, WHITE, w=5, amp=.3)
        p.shape(rotated(rrect(cx - w * .13, base - h * 1.04, cx + w * .09, base - h * .97, 4), cx - w * .02, base - h * .7, -.35), DARK, w=3, amp=.2)
        p.shape(ellipse(cx + w * .3, base - h * .55, w * .07, w * .07, n=16), GRAY, w=3, amp=.2)

def scissors(img, cx, cy, w=200, ang=0.0, open=0.4, color=RED, seed=1):
    """Office scissors; open = how far the blades are open (0…1)."""
    with Pen(img, (cx - w * .8, cy - w * .8, cx + w * .8, cy + w * .8), seed) as p:
        for sd in (-1, 1):
            a = ang + sd * open * .35
            P = _axis(cx, cy, w, a + math.pi / 2)
            p.shape([P(0, -.02 * sd), P(.55, -.005 * sd), P(.6, .015 * sd), P(0, .05 * sd)], STEEL, w=4, amp=.2)
            hx, hy = P(-.28, .1 * sd)
            p.stroke(ellipse(hx, hy, w * .14, w * .1, rot=a, n=24), w * .05, color, amp=.3, closed=True)
            p.stroke([P(-.15, .07 * sd), P(0, .02 * sd)], w * .05, color, amp=.2)
        p.poly(ellipse(cx, cy, w * .025, w * .025, n=10), DARK)

# ---------- office ----------
def computer_monitor(img, cx, base, w=300, screen=GLASS, text=None, chart=False, seed=1):
    """Desktop monitor on its stand; base = the desk top. text = words on screen, chart = a little rising chart."""
    h = w * .62
    top = base - h * 1.25
    with Pen(img, (cx - w * .6, top - 10, cx + w * .6, base + 8), seed) as p:
        p.shape([(cx - w * .05, base - h * .3), (cx + w * .05, base - h * .3), (cx + w * .07, base - 6), (cx - w * .07, base - 6)], GRAY, w=4, amp=.3)
        p.shape(rrect(cx - w * .22, base - 10, cx + w * .22, base, 4), DARK, w=4, amp=.3)
        p.shape(rrect(cx - w / 2, top, cx + w / 2, top + h, w * .03), DARK, w=6)
        scr = rrect(cx - w * .45, top + h * .08, cx + w * .45, top + h * .9, w * .015)
        p.shape(scr, screen, w=3, amp=.3)
        if chart:
            x0, y0, x1, y1 = cx - w * .35, top + h * .8, cx + w * .35, top + h * .2
            pts = [(x0 + (x1 - x0) * k / 5, y0 + (y1 - y0) * v) for k, v in enumerate((.1, .3, .2, .55, .5, .9))]
            p.stroke(pts, max(3, w * .015), GREEN, amp=.3)
        if text: p.text(text, cx, top + h * (.3 if chart else .49), h * .15, warp=0)

def office_desk(img, cx, base, w=440, color=WOOD, monitor=True, seed=1, shadow=False):
    """Office desk with a drawer pedestal; monitor=True puts a monitor, keyboard and mug on it. Returns the top y."""
    h = w * .48
    top = base - h
    with Pen(img, (cx - w * .58, top - w * .5, cx + w * .58, base + w * .04), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .03)
        dark = WOOD_D if color == WOOD else tuple(int(v * .75) for v in color)
        p.shape([(cx - w * .44, top), (cx - w * .4, top), (cx - w * .4, base), (cx - w * .44, base)], dark, w=5, amp=.3)
        ped = (cx + w * .12, top, cx + w * .46, base)
        p.shape(rrect(*ped, 4), color, w=5, amp=.4)
        for k in range(3):
            y0 = top + h * (.1 + k * .3)
            p.shape(rrect(cx + w * .15, y0, cx + w * .43, y0 + h * .26, 3), color, w=3.5, amp=.3)
            p.stroke([(cx + w * .25, y0 + h * .13), (cx + w * .33, y0 + h * .13)], 4, dark, amp=.1)
        p.shape(rrect(cx - w / 2, top - w * .04, cx + w / 2, top + w * .015, 5), color, w=6)
        if monitor:
            p.shape(rrect(cx - w * .2, top - w * .06, cx + w * .12, top - w * .035, 3), GRAY_L, w=3, amp=.2)
            mx, my = cx + w * .28, top - w * .04
            p.shape(rrect(mx - w * .04, my - w * .1, mx + w * .04, my, 4), WHITE, w=4, amp=.2)
            p.stroke(spline([(mx + w * .04, my - w * .08), (mx + w * .065, my - w * .06), (mx + w * .04, my - w * .025)]), 4, amp=.2)
    if monitor: computer_monitor(img, cx - w * .04, top - w * .06, w * .5, seed=seed)
    return top - w * .04

def office_chair(img, cx, base, h=360, color=DARK, look=1, seed=1, shadow=False):
    """Swivel office chair seen from the side; look = 1 faces right, -1 left."""
    d = 1 if look >= 0 else -1
    with Pen(img, (cx - h * .5, base - h * 1.05, cx + h * .5, base + h * .04), seed) as p:
        if shadow: p.blob(cx, base, h * .3, h * .025)
        seat_y = base - h * .45
        for k in (-1, 0, 1):
            fx = cx + k * h * .28
            p.stroke([(cx, base - h * .08), (fx, base - h * .05)], h * .03, DARK, amp=.2)
            p.shape(ellipse(fx, base - h * .03, h * .03, h * .03, n=12), DARK, w=3, amp=.1)
        p.limb([(cx, base - h * .08), (cx, seat_y)], h * .035, GRAY, 3)
        p.shape(rrect(cx - h * .26, seat_y - h * .07, cx + h * .26, seat_y + h * .02, h * .03), color, w=5, amp=.4)
        bx = cx - d * h * .24
        p.stroke([(cx - d * h * .1, seat_y), (bx, seat_y - h * .15)], h * .03, GRAY, amp=.2)
        back = rrect(bx - h * .06, base - h * 1.0, bx + h * .06, seat_y - h * .12, h * .05)
        p.shape(rotated(back, bx, seat_y - h * .3, -d * .08), color, w=5, amp=.4)

def filing_cabinet(img, cx, base, h=360, drawers=3, open=None, color=STEEL, seed=1, shadow=False):
    """Metal filing cabinet; open = index of a drawer pulled out with folders (0 = top) or None."""
    w = h * .5
    top = base - h
    with Pen(img, (cx - w * .6, top - 10, cx + w * 1.0, base + h * .04), seed) as p:
        if shadow: p.blob(cx, base, w * .6, h * .025)
        p.shape(rrect(cx - w / 2, top, cx + w / 2, base, 6), color, w=6)
        dh = (h - 16) / drawers
        for k in range(drawers):
            y0 = top + 8 + k * dh
            if open == k:
                p.shape([(cx - w * .45, y0 + 4), (cx + w * .75, y0 + dh * .3), (cx + w * .75, y0 + dh - 4), (cx - w * .45, y0 + dh - 4)],
                        color, w=4, amp=.3)
                for j, col in enumerate((YELLOW, BLUE, GREEN, RED)):
                    fx = cx - w * .2 + j * w * .22
                    p.shape([(fx, y0 + dh * .15), (fx + w * .12, y0 + dh * .2), (fx + w * .12, y0 + dh * .5), (fx, y0 + dh * .5)], col, w=3, amp=.2)
                p.shape(rrect(cx + w * .55, y0 + dh * .3, cx + w * .75, y0 + dh - 4, 3), color, w=4, amp=.3)
            else:
                p.shape(rrect(cx - w * .42, y0 + 4, cx + w * .42, y0 + dh - 4, 4), color, w=4, amp=.3)
                p.shape(rrect(cx - w * .12, y0 + dh * .25, cx + w * .12, y0 + dh * .38, 3), STEEL_D, w=3, amp=.2)
                p.shape(rrect(cx - w * .1, y0 + dh * .48, cx + w * .1, y0 + dh * .6, 2), WHITE, w=2.5, amp=.1)

def printer(img, cx, base, w=280, paper=True, seed=1, shadow=False):
    """Office printer; paper=True shows a printed page coming out."""
    h = w * .55
    top = base - h
    with Pen(img, (cx - w * .6, top - h * .55, cx + w * .6, base + w * .04), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .03)
        p.shape([(cx - w * .3, top), (cx - w * .2, top - h * .45), (cx + w * .25, top - h * .45), (cx + w * .32, top)], WHITE, w=4, amp=.3)
        p.shape(rrect(cx - w / 2, top, cx + w / 2, base, w * .05), BEIGE, w=6)
        p.shape(rrect(cx - w * .38, top + h * .45, cx + w * .38, top + h * .55, 3), DARK, w=3, amp=.2)
        if paper:
            pg = [(cx - w * .3, top + h * .5), (cx + w * .3, top + h * .5), (cx + w * .34, base + h * .05), (cx - w * .34, base + h * .05)]
            p.shape(pg, WHITE, w=4, amp=.3)
            for k in range(3): p.stroke([(cx - w * .22, top + h * (.68 + k * .12)), (cx + w * .2, top + h * (.68 + k * .12))], 3, GRAY, amp=.3)
        p.shape(rrect(cx + w * .28, top + h * .14, cx + w * .42, top + h * .3, 3), GLASS_D, w=3, amp=.2)
        p.poly(ellipse(cx + w * .2, top + h * .22, w * .02, w * .02, n=10), GREEN)

def briefcase(img, cx, base, w=240, color=WOOD_D, seed=1, shadow=False):
    """Leather briefcase standing on its side; (cx, base) = bottom center (or the hand when carried)."""
    h = w * .7
    top = base - h
    with Pen(img, (cx - w * .6, top - h * .3, cx + w * .6, base + w * .04), seed) as p:
        if shadow: p.blob(cx, base, w * .5, w * .03)
        p.stroke(spline([(cx - w * .16, top), (cx - w * .14, top - h * .22), (cx + w * .14, top - h * .22), (cx + w * .16, top)]), w * .04, DARK, amp=.3)
        p.shape(rrect(cx - w / 2, top, cx + w / 2, base, w * .06), color, w=6)
        p.stroke([(cx - w / 2 + 4, top + h * .35), (cx + w / 2 - 4, top + h * .35)], 4, tuple(int(v * .7) for v in color), amp=.3)
        for sd in (-1, 1): p.shape(rrect(cx + sd * w * .28 - w * .05, top + h * .28, cx + sd * w * .28 + w * .05, top + h * .44, 3), GOLD, w=3, amp=.2)

def mug(img, cx, base, h=150, color=WHITE, label=None, steam=True, seed=1):
    """Coffee mug with a handle; label = text on it."""
    w = h * .8
    top = base - h
    with Pen(img, (cx - w * .8, top - h * .6, cx + w * .8, base + 6), seed) as p:
        if steam:
            for k in (-1, 1):
                x = cx + k * w * .15
                p.stroke(spline([(x, top - h * .05), (x - w * .06, top - h * .2), (x + w * .06, top - h * .35), (x, top - h * .5)]), 3.5, GRAY, amp=.3)
        p.stroke(spline([(cx + w * .45, top + h * .25), (cx + w * .72, top + h * .3), (cx + w * .7, top + h * .65), (cx + w * .45, top + h * .7)]),
                 h * .08, INK, amp=.3)
        p.stroke(spline([(cx + w * .45, top + h * .25), (cx + w * .72, top + h * .3), (cx + w * .7, top + h * .65), (cx + w * .45, top + h * .7)]),
                 h * .04, color, amp=.3, taper=False)
        p.shape(rrect(cx - w / 2, top, cx + w / 2, base, w * .1), color, w=5)
        p.shape(ellipse(cx, top + 4, w * .44, h * .06, n=24), WOOD_D, w=3, amp=.2)
        if label: p.text(label, cx, top + h * .55, h * .2, fill=RED if color == WHITE else WHITE, warp=.3)

def stapler(img, cx, base, w=220, color=RED, seed=1):
    """Desk stapler seen from the side."""
    h = w * .3
    with Pen(img, (cx - w * .6, base - h * 1.4, cx + w * .6, base + 6), seed) as p:
        p.shape(rrect(cx - w / 2, base - h * .25, cx + w / 2, base, 4), DARK, w=4, amp=.3)
        p.shape(rrect(cx - w * .46, base - h * .55, cx + w * .4, base - h * .25, 4), GRAY, w=4, amp=.3)
        p.shape(spline([(cx - w * .5, base - h * .5), (cx - w * .45, base - h * 1.1), (cx + w * .3, base - h * 1.05),
                        (cx + w * .48, base - h * .7), (cx + w * .45, base - h * .5)], closed=True), color, w=5)
        p.stroke([(cx - w * .3, base - h * .85), (cx + w * .2, base - h * .82)], 3, WHITE, amp=.2)

def sticky_note(img, cx, cy, w=160, text=None, color=YELLOW, ang=-0.06, seed=1):
    """Square sticky note with handwritten text (use \\n for more lines)."""
    R = lambda pts: rotated(pts, cx, cy, ang)
    with Pen(img, (cx - w * .75, cy - w * .75, cx + w * .75, cy + w * .75), seed) as p:
        h = w
        p.shape(R([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h * .32), (cx + w * .32, cy + h / 2), (cx - w / 2, cy + h / 2)]),
                color, w=4, amp=.4)
        p.poly(R([(cx - w / 2 + 2, cy - h / 2 + 2), (cx + w / 2 - 2, cy - h / 2 + 2), (cx + w / 2 - 2, cy - h * .36), (cx - w / 2 + 2, cy - h * .36)]),
               tuple(int(v * .9) for v in color))
        p.shape(R([(cx + w / 2, cy + h * .32), (cx + w * .32, cy + h * .32), (cx + w * .32, cy + h / 2)]), tuple(int(v * .82) for v in color), w=3, amp=.2)
        if text:
            lines = str(text).split("\n")
            for k, ln in enumerate(lines):
                tx, ty = R([(cx, cy + (k - (len(lines) - 1) / 2) * w * .2)])[0]
                p.text(ln, tx, ty + w * .05, w * .16, warp=1)

def folder(img, cx, cy, w=240, color=YELLOW, label=None, ang=0.0, seed=1):
    """Paper file folder with a tab and a paper peeking out; label = text on it."""
    h = w * .72
    R = lambda pts: rotated(pts, cx, cy, ang)
    dark = tuple(int(v * .82) for v in color)
    with Pen(img, (cx - w * .7, cy - w * .7, cx + w * .7, cy + w * .7), seed) as p:
        x0, y0 = cx - w / 2, cy - h / 2
        p.shape(R([(x0, y0), (x0 + w * .35, y0), (x0 + w * .42, y0 + h * .08), (x0 + w, y0 + h * .08), (x0 + w, cy + h / 2), (x0, cy + h / 2)]),
                dark, w=4, amp=.4)
        p.shape(R(rrect(x0 + w * .08, y0 + h * .02, x0 + w * .92, cy + h * .3, 3)), WHITE, w=3, amp=.3)
        p.shape(R([(x0, y0 + h * .2), (x0 + w, y0 + h * .2), (x0 + w, cy + h / 2), (x0, cy + h / 2)]), color, w=5, amp=.4)
        if label: p.text(label, *R([(cx, cy + h * .15)])[0], h * .16, warp=.5)

def whiteboard(img, cx, cy, w=520, text=None, chart=True, seed=1):
    """Wall whiteboard with a marker tray; chart = a hand-drawn rising chart, text = a title written on it."""
    h = w * .6
    with Pen(img, (cx - w * .55, cy - h * .58, cx + w * .55, cy + h * .62), seed) as p:
        p.shape(rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 6), GRAY_L, w=6)
        p.shape(rrect(cx - w * .47, cy - h * .45, cx + w * .47, cy + h * .45, 4), WHITE, w=3, amp=.3)
        p.shape(rrect(cx - w * .3, cy + h * .5, cx + w * .3, cy + h * .56, 3), GRAY, w=4, amp=.3)
        for k, col in enumerate((RED, BLUE, GREEN)):
            p.shape(rrect(cx - w * .2 + k * w * .09, cy + h * .47, cx - w * .14 + k * w * .09, cy + h * .51, 2), col, w=2.5, amp=.1)
        if text: p.text(text, cx, cy - h * .3, h * .12, fill=BLUE, warp=1.2)
        if chart:
            x0, y0 = cx - w * .35, cy + h * .35
            p.stroke([(x0, cy - h * (.1 if text else .35)), (x0, y0), (cx + w * .38, y0)], 4, amp=.6)
            pts = [(x0 + w * .7 * k / 5, y0 - h * v) for k, v in enumerate((.08, .2, .14, .3, .26, .5 if text else .62))]
            p.stroke(pts, 6, RED, amp=.8)
            ex, ey = pts[-1]
            p.stroke([(ex - w * .04, ey + h * .01), (ex, ey), (ex - w * .01, ey + h * .07)], 6, RED, amp=.3)

def potted_plant(img, cx, base, h=280, pot=TERRACOTTA, seed=1, shadow=False):
    """Office plant in a pot."""
    with Pen(img, (cx - h * .55, base - h * 1.05, cx + h * .55, base + h * .04), seed) as p:
        if shadow: p.blob(cx, base, h * .2, h * .025)
        R = p.rng
        for k in range(9):
            a = -math.pi / 2 + (k - 4) * .28 + R.uniform(-.08, .08)
            L = h * R.uniform(.5, .72)
            bx, by = cx, base - h * .34
            tx, ty = bx + math.cos(a) * L, by + math.sin(a) * L
            mx, my = (bx + tx) / 2, (by + ty) / 2
            nx, ny = -math.sin(a), math.cos(a)
            leaf = spline([(bx, by), (mx + nx * h * .07, my + ny * h * .07), (tx, ty), (mx - nx * h * .07, my - ny * h * .07)], closed=True)
            p.shape(leaf, LEAF if k % 2 else LEAF_D, w=4, amp=.3)
            p.stroke([(bx, by), (tx, ty)], 2, LEAF_D if k % 2 else LEAF, amp=.2)
        p.shape([(cx - h * .2, base - h * .36), (cx + h * .2, base - h * .36), (cx + h * .15, base), (cx - h * .15, base)], pot, w=5)
        p.shape(rrect(cx - h * .23, base - h * .4, cx + h * .23, base - h * .32, 4), pot, w=5, amp=.3)

def water_cooler(img, cx, base, h=440, seed=1, shadow=False):
    """Office water cooler with a big blue bottle."""
    w = h * .38
    with Pen(img, (cx - w * .7, base - h * 1.04, cx + w * .7, base + h * .04), seed) as p:
        if shadow: p.blob(cx, base, w * .6, h * .02)
        body_t = base - h * .62
        bottle = spline([(cx - w * .1, body_t), (cx - w * .12, body_t - h * .05), (cx - w * .45, body_t - h * .1), (cx - w * .46, base - h * .98),
                         (cx + w * .46, base - h * .98), (cx + w * .45, body_t - h * .1), (cx + w * .12, body_t - h * .05), (cx + w * .1, body_t)], closed=True)
        p.poly(p.wobble(bottle, .4, True), (190, 220, 245))
        with p.clip(bottle): p.poly([(cx - w, base - h * .85), (cx + w, base - h * .85), (cx + w, body_t), (cx - w, body_t)], (120, 180, 230))
        p.stroke(bottle, 5, amp=.4, closed=True)
        p.stroke([(cx - w * .3, base - h * .93), (cx - w * .3, base - h * .78)], 5, WHITE, amp=.2)
        p.shape(rrect(cx - w / 2, body_t, cx + w / 2, base, w * .08), WHITE, w=6)
        p.shape(rrect(cx - w * .32, body_t + h * .1, cx + w * .32, body_t + h * .22, 4), GRAY_L, w=3.5, amp=.2)
        for sd, col in ((-1, BLUE), (1, RED)):
            p.shape(rrect(cx + sd * w * .17 - w * .06, body_t + h * .2, cx + sd * w * .17 + w * .06, body_t + h * .26, 3), col, w=3, amp=.2)

def desk_lamp(img, cx, base, h=280, on=True, color=GREEN, seed=1):
    """Bendy desk lamp facing left; on=True draws a soft light cone."""
    with Pen(img, (cx - h * .9, base - h * 1.05, cx + h * .4, base + 6), seed) as p:
        ex, ey = cx + h * .12, base - h * .55
        hx, hy = cx - h * .2, base - h * .92
        if on:
            p.poly([(hx - h * .12, hy + h * .1), (hx - h * .02, hy + h * .16), (hx - h * .1, base), (hx - h * .62, base)], (255, 246, 200))
        p.shape(ellipse(cx, base - h * .03, h * .2, h * .045, n=24), color, w=4, amp=.3)
        p.stroke([(cx, base - h * .05), (ex, ey), (hx, hy)], h * .04, DARK, amp=.3)
        p.shape(ellipse(ex, ey, h * .035, h * .035, n=12), GRAY, w=3, amp=.1)
        shade = rotated([(hx - h * .05, hy - h * .08), (hx + h * .06, hy - h * .04), (hx + h * .02, hy + h * .14), (hx - h * .2, hy + h * .1)], hx, hy, 0)
        p.shape(shade, color, w=5, amp=.3)
        if on: p.shape(ellipse(hx - h * .07, hy + h * .13, h * .05, h * .03, rot=.4, n=14), YELLOW, w=3, amp=.1)

def pencil_cup(img, cx, base, h=170, color=BLUE, seed=1):
    """Cup with pencils and pens."""
    w = h * .55
    top = base - h * .6
    with Pen(img, (cx - w, base - h * 1.1, cx + w, base + 6), seed) as p:
        for k, (a, col) in enumerate(((-.3, YELLOW), (-.1, RED), (.1, BLUE), (.3, YELLOW))):
            bx, by = cx + (k - 1.5) * w * .18, top + h * .1
            tx, ty = bx + math.sin(a) * h * .5, by - math.cos(a) * h * .5
            p.stroke([(bx, by), (tx, ty)], h * .06, INK, amp=.2)
            p.stroke([(bx, by), (tx, ty)], h * .035, col, amp=.2, taper=False)
            if col == YELLOW:
                p.shape([(tx - math.cos(a) * h * .03, ty - math.sin(a) * h * .03), (tx + math.cos(a) * h * .03, ty + math.sin(a) * h * .03),
                         (tx + math.sin(a) * h * .07, ty - math.cos(a) * h * .07)], (240, 210, 170), w=2, amp=.1)
        p.shape([(cx - w / 2, top), (cx + w / 2, top), (cx + w * .44, base), (cx - w * .44, base)], color, w=5)

def id_badge(img, cx, cy, w=140, name="NAME", color=BLUE, lanyard=True, seed=1):
    """ID badge on a lanyard; (cx, cy) = center of the card, name = text on it."""
    h = w * 1.3
    with Pen(img, (cx - w * .9, cy - h * 1.6, cx + w * .9, cy + h * .6), seed) as p:
        if lanyard:
            for sd in (-1, 1):
                p.stroke([(cx + sd * w * .12, cy - h * .48), (cx + sd * w * .7, cy - h * 1.5)], w * .07, color, amp=.4)
        p.shape(rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, w * .08), WHITE, w=5)
        p.poly(rrect(cx - w / 2 + 3, cy - h / 2 + 3, cx + w / 2 - 3, cy - h * .28, w * .06), color)
        p.shape(rrect(cx - w * .09, cy - h * .55, cx + w * .09, cy - h * .42, 3), GRAY, w=3, amp=.1)
        p.shape(ellipse(cx, cy - h * .05, w * .2, w * .2, n=24), GRAY_L, w=3, amp=.2)
        p.poly(ellipse(cx, cy - h * .09, w * .07, w * .07, n=12), GRAY)
        p.poly([(cx - w * .13, cy + h * .08), (cx - w * .1, cy + h * .01), (cx + w * .1, cy + h * .01), (cx + w * .13, cy + h * .08)], GRAY)
        if name: p.text(str(name), cx, cy + h * .3, min(w * .2, w * 1.4 / max(1, len(str(name)))), warp=0)

# ---------- hats ----------
def _hard_hat(p, hx, hy, r, look, color=YELLOW):
    R, a0 = r * 1.06, math.asin(.42)
    dome = [(hx + R * math.cos(t), hy + R * math.sin(t)) for t in (math.pi + a0 + (math.pi - 2 * a0) * k / 24 for k in range(25))]
    p.shape(dome, color, w=r * .08, amp=.5)
    p.stroke([(hx + look * r * .2, hy - R), (hx + look * r * .3, hy - R * .45)], r * .1, tuple(int(v * .82) for v in color), amp=.2)
    p.shape(rrect(hx - r * 1.25 + look * r * .1, hy - R * .5, hx + r * 1.25 + look * r * .1, hy - R * .34, r * .06), color, w=r * .07, amp=.4)

def _chef_hat(p, hx, hy, r, look):
    p.shape(bumpy([(hx - r * .45, hy - r * 1.35, r * .42), (hx + r * .45, hy - r * 1.35, r * .42), (hx, hy - r * 1.6, r * .5)]), WHITE, w=r * .07, amp=.5)
    p.shape(rrect(hx - r * .72, hy - r * 1.28, hx + r * .72, hy - r * .66, r * .08), WHITE, w=r * .07, amp=.4)
    for k in (-.35, 0, .35): p.stroke([(hx + k * r, hy - r * 1.2), (hx + k * r * 1.1, hy - r * .75)], r * .03, GRAY_L, amp=.2)

def _peaked_cap(p, hx, hy, r, look, color=NAVY, band=None, badge=GOLD, crown_w=1.2):
    p.shape(spline([(hx - r * .95, hy - r * .66), (hx - r * crown_w, hy - r * 1.12), (hx, hy - r * 1.28), (hx + r * crown_w, hy - r * 1.12),
                    (hx + r * .95, hy - r * .66)]) + [(hx - r * .95, hy - r * .66)], color, w=r * .07, amp=.4)
    p.shape(rrect(hx - r * .97, hy - r * .82, hx + r * .97, hy - r * .62, r * .05), band or tuple(int(v * .6) for v in color), w=r * .06, amp=.3)
    vx = hx + look * r * .4
    p.shape([(vx - r * .75, hy - r * .64), (vx + r * .75, hy - r * .64), (vx + r * .55, hy - r * .48), (vx - r * .55, hy - r * .48)], DARK, w=r * .06, amp=.3)
    if badge: p.shape(ellipse(hx + look * r * .15, hy - r * .98, r * .14, r * .12, n=16), badge, w=r * .04, amp=.2)

def _fire_helmet(p, hx, hy, r, look, color=FIRE_RED):
    p.shape(ellipse(hx - look * r * .3, hy - r * .55, r * 1.45, r * .28, n=40), color, w=r * .07, amp=.4)
    R, a0 = r * 1.04, math.asin(.5)
    dome = [(hx + R * math.cos(t), hy + R * math.sin(t)) for t in (math.pi + a0 + (math.pi - 2 * a0) * k / 24 for k in range(25))]
    p.shape(dome, color, w=r * .08, amp=.5)
    p.stroke([(hx - r * .02, hy - R), (hx, hy - R * .5)], r * .12, tuple(int(v * .78) for v in color), amp=.2)
    sx = hx + look * r * .25
    p.shape([(sx - r * .3, hy - r * .58), (sx - r * .34, hy - r * .95), (sx, hy - r * 1.08), (sx + r * .34, hy - r * .95), (sx + r * .3, hy - r * .58)],
            GOLD, w=r * .05, amp=.3)

def _straw_hat(p, hx, hy, r, look):
    p.shape(ellipse(hx, hy - r * .66, r * 1.7, r * .3, n=48), STRAW, w=r * .06, amp=.6)
    crown = spline([(hx - r * .72, hy - r * .7), (hx - r * .68, hy - r * 1.2), (hx, hy - r * 1.32), (hx + r * .68, hy - r * 1.2), (hx + r * .72, hy - r * .7)])
    p.shape(crown + [(hx - r * .72, hy - r * .7)], STRAW, w=r * .06, amp=.5)
    p.poly([(hx - r * .71, hy - r * .9), (hx + r * .71, hy - r * .9), (hx + r * .72, hy - r * .76), (hx - r * .72, hy - r * .76)], RED)
    for k in range(-3, 4): p.stroke([(hx + k * r * .4, hy - r * .55), (hx + k * r * .45, hy - r * .8)], r * .02, STRAW_D, amp=.2)

def _nurse_cap(p, hx, hy, r, look):
    p.shape([(hx - r * .62, hy - r * .78), (hx - r * .5, hy - r * 1.22), (hx + r * .5, hy - r * 1.22), (hx + r * .62, hy - r * .78)], WHITE, w=r * .06, amp=.4)
    cx_, cy_ = hx + look * r * .1, hy - r * 1.0
    p.poly([(cx_ - r * .05, cy_ - r * .14), (cx_ + r * .05, cy_ - r * .14), (cx_ + r * .05, cy_ + r * .14), (cx_ - r * .05, cy_ + r * .14)], RED)
    p.poly([(cx_ - r * .14, cy_ - r * .05), (cx_ + r * .14, cy_ - r * .05), (cx_ + r * .14, cy_ + r * .05), (cx_ - r * .14, cy_ + r * .05)], RED)

def _work_cap(p, hx, hy, r, look, color=DENIM):
    R, a0 = r * 1.05, math.asin(.55)
    crown = [(hx + R * math.cos(t), hy + R * math.sin(t)) for t in (math.pi + a0 + (math.pi - 2 * a0) * k / 24 for k in range(25))]
    p.shape(crown, color, w=r * .08, amp=.5)
    vx = hx + look * r * .55
    visor = [(vx + r * .8 * math.cos(t), hy - R * .55 + r * .2 * math.sin(t)) for t in (math.pi * k / 16 for k in range(17))]
    p.shape(visor + [(vx - r * .8, hy - R * .55)], color, w=r * .07, amp=.4)

def _goggles(p, hx, hy, r, look):
    y = hy - r * .62
    head = ellipse(hx, hy, r * 1.01, r * 1.03, n=64)
    with p.clip(head): p.poly([(hx - r * 1.2, y - r * .07), (hx + r * 1.2, y - r * .07), (hx + r * 1.2, y + r * .07), (hx - r * 1.2, y + r * .07)], DARK)
    for sd in (-1, 1): p.shape(ellipse(hx + look * r * .16 + sd * r * .3, y, r * .24, r * .18, n=24), (190, 230, 240), w=r * .06, amp=.2)

WORK_HATS = {"hard_hat": _hard_hat, "chef": _chef_hat, "police": lambda p, x, y, r, l: _peaked_cap(p, x, y, r, l),
             "pilot": lambda p, x, y, r, l: _peaked_cap(p, x, y, r, l, NAVY, GOLD, (220, 220, 230)),
             "firefighter": _fire_helmet, "straw": _straw_hat, "nurse": _nurse_cap, "cap": _work_cap, "goggles": _goggles}

def work_hat(img, cx, cy, r=80, kind="hard_hat", look=0.0, seed=1):
    """A work hat on its own, sized for a head of radius r centered on (cx, cy): hard_hat, chef, police, pilot,
    firefighter, straw, nurse, cap or goggles."""
    with Pen(img, (cx - r * 1.8, cy - r * 1.9, cx + r * 1.8, cy + r * .2), seed) as p:
        WORK_HATS[kind](p, cx, cy, r, look)

# ---------- jobs ----------
class _Place:
    def __init__(self, x, y, s): self.x, self.y, self.s = x, y, s
    def __call__(self, dx, dy): return (self.x + dx * self.s, self.y + dy * self.s)

def _pants(p, P, s, look, color):
    for side in (-1, 1):
        p.limb([P(18 * side, -248), P(25 * side + look * 6, -125), P(29 * side, -26)], 24 * s, color, 4 * s)
    p.shape([P(-50, -262), P(50, -262), P(52, -226), P(-52, -226)], color, w=5 * s, amp=.4)

def _coat(p, P, s, color=WHITE, bottom=-150):
    for k in (-1, 1):
        p.shape([P(46 * k, -418), P(14 * k, -418), P(16 * k, -300), P(12 * k, bottom), P(60 * k, bottom), P(58 * k, -330)], color, w=5 * s, amp=.6)
        p.shape([P(14 * k, -418), P(30 * k, -414), P(22 * k, -350), P(16 * k, -330)], color, w=4 * s, amp=.3)
    p.shape(rrect(*P(22, -310), *P(48, -280), 3 * s), color, w=3.5 * s, amp=.2)

def _job(img, x, y, s, job, mood, arms, look, color, held, seed, shadow, **kw):
    P = _Place(x, y, s)
    torso = [P(-44, -418), P(44, -418), P(54, -330), P(50, -238), P(-50, -238), P(-54, -330)]
    outfit, shirt = {"medic": ("tie", WHITE), "scientist": ("tie", WHITE), "teacher": ("tie", WHITE), "pilot": ("tie", WHITE),
                     "nurse": ("tshirt", color or TEAL), "chef": ("tshirt", WHITE), "police": ("tshirt", color or NAVY),
                     "firefighter": ("tshirt", color or KHAKI), "builder": ("tshirt", color or BLUE),
                     "farmer": ("tshirt", color or RED), "mechanic": ("tshirt", color or DENIM)}[job]
    tie = {"medic": BLUE, "scientist": (120, 120, 130), "teacher": RED_D, "pilot": DARK}[job] if outfit == "tie" else INK

    def dress(p, a):
        if job in ("medic", "scientist"):
            _coat(p, P, s)
            p.stroke([P(30, -312), P(32, -290)], 3 * s, BLUE, amp=.1)
            p.stroke([P(38, -312), P(39, -295)], 3 * s, RED, amp=.1)
            if job == "medic":
                p.stroke(spline([P(-34, -416), P(-30, -360), P(-12, -320), P(0, -312)]), 5 * s, DARK, amp=.3)
                p.stroke(spline([P(34, -416), P(30, -360), P(12, -320), P(0, -312)]), 5 * s, DARK, amp=.3)
                p.stroke([P(0, -312), P(4, -288)], 5 * s, DARK, amp=.2)
                p.shape(ellipse(*P(4, -280), 11 * s, 11 * s, n=16), STEEL, w=3.5 * s, amp=.2)
        elif job == "nurse":
            _pants(p, P, s, look, shirt)
            p.shape(torso, shirt, w=7.5 * s, amp=.8)
            p.stroke([P(-22, -418), P(0, -380), P(22, -418)], 5 * s, tuple(int(v * .7) for v in shirt), amp=.3)
            p.shape(rrect(*P(-44, -320), *P(-18, -290), 3 * s), shirt, w=3.5 * s, amp=.2)
        elif job == "chef":
            _pants(p, P, s, look, (60, 60, 66))
            p.shape(torso, WHITE, w=7.5 * s, amp=.8)
            for col_x in (-14, 14):
                for yy in (-380, -340, -300): p.poly(ellipse(*P(col_x, yy), 4 * s, 4 * s, n=10), INK)
            p.shape([P(-30, -420), P(30, -420), P(0, -384)], RED, w=4 * s, amp=.3)
            p.shape([P(-48, -258), P(48, -258), P(56, -150), P(-56, -150)], WHITE, w=5 * s, amp=.5)
        elif job == "police":
            _pants(p, P, s, look, NAVY_D)
            p.shape(torso, shirt, w=7.5 * s, amp=.8)
            for k in (-1, 1): p.shape(rrect(*P(k * 28 - 14, -370), *P(k * 28 + 14, -345), 3 * s), shirt, w=3 * s, amp=.2)
            bx, by = P(-28, -330)
            star = [(bx + math.cos(-math.pi / 2 + k * math.pi / 5) * (14 if k % 2 == 0 else 6) * s,
                     by + math.sin(-math.pi / 2 + k * math.pi / 5) * (14 if k % 2 == 0 else 6) * s) for k in range(10)]
            p.shape(star, GOLD, w=2.5 * s, amp=.1)
            p.stroke([P(0, -414), P(0, -250)], 3 * s, tuple(int(v * .7) for v in shirt), amp=.2)
            p.limb([P(-52, -250), P(52, -250)], 12 * s, DARK, 3 * s)
            p.shape(rrect(*P(-8, -258), *P(8, -242), 2 * s), STEEL, w=2.5 * s, amp=.1)
        elif job == "firefighter":
            _pants(p, P, s, look, shirt)
            coat = [P(-50, -420), P(50, -420), P(60, -330), P(62, -180), P(-62, -180), P(-60, -330)]
            p.shape(coat, shirt, w=7.5 * s, amp=.8)
            for yy in (-300, -200):
                p.poly([P(-60, yy), P(60, yy), P(60, yy + 14), P(-60, yy + 14)], REFLECT)
            for side in (-1, 1): p.poly([P(26 * side - 6, -110), P(26 * side + 6, -110), P(26 * side + 6, -96), P(26 * side - 6, -96)], REFLECT)
            p.stroke([P(0, -418), P(0, -182)], 4 * s, amp=.3)
            p.stroke(coat, 7.5 * s, amp=.8, closed=True)
        elif job == "builder":
            _pants(p, P, s, look, DENIM)
            p.shape(torso, shirt, w=7.5 * s, amp=.8)
            vest = [P(-46, -414), P(-18, -414), P(-12, -330), P(12, -330), P(18, -414), P(46, -414), P(56, -330), P(52, -238), P(-52, -238), P(-56, -330)]
            p.shape(vest, ORANGE, w=6 * s, amp=.6)
            with p.clip(vest):
                for yy in (-310, -270): p.poly([P(-70, yy), P(70, yy), P(70, yy + 12), P(-70, yy + 12)], REFLECT)
            p.stroke(vest, 6 * s, amp=.6, closed=True)
        elif job == "teacher":
            for k in (-1, 1):
                p.shape([P(46 * k, -418), P(14 * k, -418), P(10 * k, -240), P(52 * k, -240), P(56 * k, -330)], color or PURPLE, w=5 * s, amp=.6)
                for yy in (-370, -320, -270): p.poly(ellipse(*P(16 * k, yy), 3.5 * s, 3.5 * s, n=10), INK)
        elif job == "farmer":
            with p.clip(spline(torso, closed=True)):
                for k in range(-4, 5): p.stroke([P(k * 16, -430), P(k * 16, -230)], 3 * s, RED_D, amp=.3)
                for k in range(12): p.stroke([P(-60, -420 + k * 16), P(60, -420 + k * 16)], 3 * s, RED_D, amp=.3)
            p.stroke(spline(torso, closed=True), 7.5 * s, amp=.8, closed=True)
            _pants(p, P, s, look, DENIM)
            p.shape([P(-30, -340), P(30, -340), P(34, -240), P(-34, -240)], DENIM, w=5 * s, amp=.4)
            for k in (-1, 1):
                p.stroke([P(24 * k, -342), P(34 * k, -414)], 8 * s, DENIM_D, amp=.2)
                p.poly(ellipse(*P(24 * k, -334), 4 * s, 4 * s, n=10), GOLD)
            p.shape(rrect(*P(-16, -320), *P(16, -290), 3 * s), DENIM, w=3 * s, amp=.2)
        elif job == "mechanic":
            _pants(p, P, s, look, shirt)
            p.shape(torso, shirt, w=7.5 * s, amp=.8)
            p.stroke([P(0, -414), P(0, -250)], 4 * s, tuple(int(v * .7) for v in shirt), amp=.2)
            p.shape(rrect(*P(-46, -360), *P(-12, -336), 3 * s), WHITE, w=3 * s, amp=.2)
            if kw.get("name"): p.text(kw["name"], *P(-29, -348), min(14, 48 / len(kw["name"])) * s, fill=RED, warp=0)
            p.limb([P(-52, -250), P(52, -250)], 10 * s, tuple(int(v * .7) for v in shirt), 3 * s)
            p.stroke([P(30, -300), P(40, -280)], 5 * s, (60, 60, 60), amp=.4)
        elif job == "pilot":
            _pants(p, P, s, look, NAVY_D)
            p.shape([P(-20, -360), P(-6, -366), P(-20, -350)], GOLD, w=2 * s, amp=.1)
            p.shape(ellipse(*P(-26, -362), 10 * s, 6 * s, n=14), GOLD, w=2 * s, amp=.1)
            p.shape([P(-46, -360), P(-26, -364), P(-6, -360), P(-26, -356)], GOLD, w=2.5 * s, amp=.1)

    def hat(p, a):
        (hx, hy), r = a["head"], a["head_r"]
        kind = kw.get("hat_kind", {"chef": "chef", "police": "police", "pilot": "pilot", "firefighter": "firefighter",
                                   "builder": "hard_hat", "farmer": "straw", "nurse": "nurse", "mechanic": "cap",
                                   "scientist": "goggles"}.get(job))
        if kind: WORK_HATS[kind](p, hx, hy, r, look)
        if job == "teacher" and kw.get("glasses", True):
            fx = a["mouth"][0]
            for sd in (-1, 1): p.stroke(rrect(fx + sd * .27 * r - .22 * r, hy - .25 * r, fx + sd * .27 * r + .22 * r, hy + .15 * r, .06 * r),
                                        .04 * r, DARK, amp=.2, closed=True)
            p.stroke([(fx - .05 * r, hy - .08 * r), (fx + .05 * r, hy - .08 * r)], .04 * r, DARK, amp=.1)

    def extras(p, a):
        if job == "pilot":
            for sh in a["shoulders"]:
                p.shape(rrect(sh[0] - 18 * s, sh[1] - 6 * s, sh[0] + 18 * s, sh[1] + 6 * s, 2 * s), NAVY, w=3 * s, amp=.2)
                for k in (-8, 0, 8): p.stroke([(sh[0] + k * s, sh[1] - 4 * s), (sh[0] + k * s, sh[1] + 4 * s)], 2.5 * s, GOLD, amp=0)
        if job in ("firefighter", "police", "builder", "mechanic", "farmer", "chef", "pilot", "nurse"):
            shoe = {"nurse": WHITE, "builder": WOOD_D, "farmer": WOOD_D}.get(job, DARK)
            for side in (-1, 1):
                d = look or side
                p.shape(spline([P(30 * side - 18 * d, -2), P(30 * side - 16 * d, -24), P(30 * side + 8 * d, -26),
                                P(30 * side + 34 * d, -12), P(30 * side + 36 * d, -2)], closed=True), shoe, w=4.5 * s, amp=.4)
        if job == "firefighter":
            for hd in (a["hand_l"], a["hand_r"]): p.shape(ellipse(hd[0], hd[1], 17 * s, 17 * s, n=20), DARK, w=4 * s, amp=.4)

    a = doodle(img, x, y, s, outfit=outfit, color=shirt, tie=tie, mood=mood, arms=arms, look=look, dress=dress, hat=hat,
               extras=extras, shadow=shadow, seed=seed)
    if held:
        gx, gy = a["hand_r"]
        right = arms if isinstance(arms, str) else arms[1]
        ang = kw.get("ang")
        if ang is None: ang = {"up": .25, "down": math.pi - .5}.get(right, .55)
        L = 220 * s
        with Pen(img, (gx - L * 1.4, gy - L * 1.4, gx + L * 1.4, gy + L * 1.4), seed + 3) as p:
            if held == "hammer": _hammer(p, gx, gy, L, ang)
            elif held == "wrench": _wrench(p, gx, gy, L, ang)
            elif held == "screwdriver": _screwdriver(p, gx, gy, L * .9, ang)
            elif held == "shovel": _shovel(p, gx, gy, L * 1.3, min(ang, .2))
            elif held == "pan": _pan(p, gx, gy, L, ang)
            elif held == "roller": _roller(p, gx, gy, L, ang)
            elif held == "book": _book(p, gx + 30 * s, gy - 30 * s, 110 * s, kw.get("book_color") or BLUE, .15)
            elif held == "flask": _flask(p, gx + 10 * s, gy - 50 * s, 110 * s, kw.get("liquid") or GREEN)
            elif held == "clipboard": _clipboard(p, gx + 20 * s, gy - 30 * s, 130 * s, .12)
            hc = DARK if job == "firefighter" else WHITE
            p.shape(ellipse(gx, gy, (17 if job == "firefighter" else 14) * s, (17 if job == "firefighter" else 14) * s, n=20), hc, w=5 * s, amp=.6)
    return a

def medic(img, x, y, s=1.0, mood="smile", arms=("down", "offer"), look=0.0, held="clipboard", shadow=False, seed=1):
    """doodle as a modern doctor: white coat over shirt and tie, stethoscope; held = clipboard/flask/book/None."""
    return _job(img, x, y, s, "medic", mood, arms, look, None, held, seed, shadow)

def nurse(img, x, y, s=1.0, mood="smile", arms=("down", "offer"), look=0.0, color=TEAL, held=None, shadow=False, seed=1):
    """doodle as a nurse: teal scrubs and a white cap with a red cross; held = clipboard/None."""
    return _job(img, x, y, s, "nurse", mood, arms, look, color, held, seed, shadow)

def chef(img, x, y, s=1.0, mood="happy", arms=("hip", "up"), look=0.0, held="pan", shadow=False, seed=1):
    """doodle as a chef: tall white hat, double-breasted jacket, red neckerchief, apron; held = pan/None."""
    return _job(img, x, y, s, "chef", mood, arms, look, None, held, seed, shadow)

def police(img, x, y, s=1.0, mood="angry", arms=("hip", "point"), look=0.0, color=NAVY, held=None, shadow=False, seed=1):
    """doodle as a police officer: peaked cap, navy uniform with a gold star badge and belt."""
    return _job(img, x, y, s, "police", mood, arms, look, color, held, seed, shadow)

def firefighter(img, x, y, s=1.0, mood="happy", arms=("hip", "up"), look=0.0, color=KHAKI, held=None, shadow=False, seed=1):
    """doodle as a firefighter: red helmet, tan coat and trousers with reflective stripes, gloves; color = coat."""
    return _job(img, x, y, s, "firefighter", mood, arms, look, color, held, seed, shadow)

def builder(img, x, y, s=1.0, mood="happy", arms=("down", "up"), look=0.0, color=BLUE, held="hammer", shadow=False, seed=1):
    """doodle as a construction worker: yellow hard hat, orange hi-vis vest, jeans; held = hammer/shovel/wrench/roller/None."""
    return _job(img, x, y, s, "builder", mood, arms, look, color, held, seed, shadow)

def scientist(img, x, y, s=1.0, mood="happy", arms=("down", "up"), look=0.0, held="flask", liquid=GREEN, shadow=False, seed=1):
    """doodle as a scientist: white lab coat, goggles on the forehead; held = flask/clipboard/None."""
    return _job(img, x, y, s, "scientist", mood, arms, look, None, held, seed, shadow, liquid=liquid)

def teacher(img, x, y, s=1.0, mood="smile", arms=("down", "offer"), look=0.0, color=PURPLE, held="book", glasses=True,
            shadow=False, seed=1):
    """doodle as a teacher: cardigan over shirt and tie, glasses; held = book/clipboard/None; color = cardigan."""
    return _job(img, x, y, s, "teacher", mood, arms, look, color, held, seed, shadow, glasses=glasses)

def farmer(img, x, y, s=1.0, mood="happy", arms=("down", "up"), look=0.0, color=RED, held="shovel", shadow=False, seed=1):
    """doodle as a farmer: straw hat, plaid shirt, denim overalls; held = shovel/None."""
    return _job(img, x, y, s, "farmer", mood, arms, look, color, held, seed, shadow)

def mechanic(img, x, y, s=1.0, mood="smile", arms=("down", "up"), look=0.0, color=DENIM, held="wrench", name=None,
             shadow=False, seed=1):
    """doodle as a mechanic: cap and blue coveralls with a name patch; held = wrench/screwdriver/hammer/None."""
    return _job(img, x, y, s, "mechanic", mood, arms, look, color, held, seed, shadow, name=name)

def pilot(img, x, y, s=1.0, mood="smug", arms=("hip", "down"), look=0.0, held=None, shadow=False, seed=1):
    """doodle as an airline pilot: captain's cap, white shirt with gold epaulettes and wings, black tie."""
    return _job(img, x, y, s, "pilot", mood, arms, look, None, held, seed, shadow)

from . import cache_pieces
cache_pieces(globals())
