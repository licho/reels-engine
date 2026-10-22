"""Sketch-style sports: balls (soccer, basketball, tennis, baseball, volleyball, American football), gear (racket, bat,
boxing glove, dumbbell, kettlebell, sneaker, whistle, stopwatch, cone, skateboard, jersey), awards (trophy, medal,
podium), places (soccer goal, basketball hoop, scoreboard, finish flag) and the doodle character as a soccer player,
basketball player, boxer, runner, tennis player, baseball player or referee. All take the image (img) and a 'seed'.
Pieces that stand on the floor draw no floor shadow unless shadow=True (the athletes keep their own).

    a = soccer_player(img, 300, FLOOR, .9, number=10, ball=True)
    trophy(img, 780, FLOOR, 260)

Held gear (racket, bat) takes the grip point and 'ang' = tilt from straight up, in radians (0 = up, .5 = leaning
right, math.pi = down)."""
import math
from . import Pen, INK, WHITE, RED, GREEN, BLUE, WOOD, WOOD_D, ellipse, rrect, rotated, spline
from .everyday import YELLOW, GOLD, GOLD_D, GRAY, GRAY_L, DARK
from .humans import doodle

ORANGE, ORANGE_D = (236, 120, 40), (170, 70, 20)
OPTIC, OPTIC_D = (214, 232, 70), (150, 170, 30)
LEATHER, LEATHER_D = (150, 82, 44), (100, 50, 24)
SILVER, SILVER_D = (210, 214, 222), (150, 156, 168)
BRONZE_M, BRONZE_MD = (205, 130, 70), (150, 85, 40)
NAVY = (40, 60, 120)
SKY = (110, 170, 230)
NET = (150, 150, 155)

def _dir(ang):
    return math.sin(ang), -math.cos(ang)

# ---------- balls ----------
BALLS = ("soccer", "basketball", "tennis", "baseball", "volleyball", "football")

def _ball(p, cx, cy, r, kind="soccer", ang=0.0):
    w = max(2.5, r * .07)
    if kind == "football":                                         # American football: pointy leather egg
        pts = rotated(spline([(cx - r * 1.35, cy), (cx - r * .7, cy - r * .78), (cx + r * .7, cy - r * .78), (cx + r * 1.35, cy),
                              (cx + r * .7, cy + r * .78), (cx - r * .7, cy + r * .78)], closed=True), cx, cy, ang)
        p.shape(pts, LEATHER, w=w)
        with p.clip(pts):
            for sd in (-1, 1):
                p.stroke(rotated([(cx + sd * r * .78, cy - r), (cx + sd * r * .82, cy + r)], cx, cy, ang), r * .1, WHITE, amp=.3)
        p.stroke(rotated([(cx - r * .42, cy - r * .02), (cx + r * .42, cy - r * .02)], cx, cy, ang), max(2, r * .06), WHITE, amp=.2)
        for k in range(5):
            x = cx - r * .32 + k * r * .16
            p.stroke(rotated([(x, cy - r * .14), (x, cy + r * .1)], cx, cy, ang), max(2, r * .05), WHITE, amp=.1)
        return
    disc = ellipse(cx, cy, r, r, n=56)
    fill = {"soccer": WHITE, "basketball": ORANGE, "tennis": OPTIC, "baseball": WHITE, "volleyball": WHITE}[kind]
    p.poly(p.wobble(disc, .5, True), fill)
    with p.clip(disc):
        if kind == "soccer":
            def pent(x, y, rr, rot):
                return [(x + rr * math.cos(rot + 2 * math.pi * k / 5), y + rr * math.sin(rot + 2 * math.pi * k / 5)) for k in range(5)]
            core = pent(cx, cy, r * .3, -math.pi / 2 + ang)
            p.poly(p.wobble(core, .3, True), DARK)
            for k in range(5):
                a = -math.pi / 2 + ang + math.pi / 5 + 2 * math.pi * k / 5
                ox, oy = cx + math.cos(a) * r * .95, cy + math.sin(a) * r * .95
                p.poly(p.wobble(pent(ox, oy, r * .4, a), .3, True), DARK)
                vx, vy = core[k]
                va = math.atan2(vy - cy, vx - cx)
                p.stroke([(vx, vy), (cx + math.cos(va) * r * 1.05, cy + math.sin(va) * r * 1.05)], w * .6, amp=.2)
        elif kind == "basketball":
            p.stroke(rotated([(cx, cy - r), (cx, cy + r)], cx, cy, ang), w * .9, amp=.3)
            p.stroke(rotated([(cx - r, cy), (cx + r, cy)], cx, cy, ang), w * .9, amp=.3)
            for sd in (-1, 1):
                p.stroke(rotated(spline([(cx + sd * r * .35, cy - r), (cx + sd * r * .62, cy), (cx + sd * r * .35, cy + r)]),
                                 cx, cy, ang), w * .9, amp=.3)
        elif kind == "tennis":
            for sd in (-1, 1):
                p.stroke(rotated(spline([(cx + sd * r * 1.05, cy - r * .75), (cx + sd * r * .5, cy), (cx + sd * r * 1.05, cy + r * .75)]),
                                 cx, cy, ang), r * .1, WHITE, amp=.2)
        elif kind == "baseball":
            for sd in (-1, 1):
                seam = rotated(spline([(cx + sd * r * .95, cy - r * .7), (cx + sd * r * .55, cy), (cx + sd * r * .95, cy + r * .7)]),
                               cx, cy, ang)
                p.stroke(seam, max(2, r * .05), RED, amp=.1)
                for k in range(2, len(seam) - 2, 3):
                    (x0, y0), (x1, y1) = seam[k - 1], seam[k + 1]
                    nx, ny = -(y1 - y0), x1 - x0; ln = math.hypot(nx, ny) or 1
                    nx, ny = nx / ln * r * .09, ny / ln * r * .09
                    x, y = seam[k]
                    p.stroke([(x - nx, y - ny), (x + nx, y + ny)], max(1.5, r * .035), RED, amp=0)
        elif kind == "volleyball":
            for k in range(3):
                a = ang + 2 * math.pi * k / 3
                band = [(cx + math.cos(a + t) * r * f, cy + math.sin(a + t) * r * f) for t, f in
                        ((0, 0), (.3, .5), (.55, 1.1), (1.2, 1.1), (.9, .6), (.6, .15))]
                if k == 0: p.poly(p.wobble(spline(band, closed=True), .3, True), YELLOW)
                if k == 1: p.poly(p.wobble(spline(band, closed=True), .3, True), SKY)
            for k in range(3):
                a = ang + 2 * math.pi * k / 3
                p.stroke(spline([(cx, cy), (cx + math.cos(a + .3) * r * .5, cy + math.sin(a + .3) * r * .5),
                                 (cx + math.cos(a + .55) * r * 1.1, cy + math.sin(a + .55) * r * 1.1)]), w * .8, amp=.2)
    p.stroke(disc, w, amp=.8, closed=True)

def ball(img, cx, cy, r=60, kind="soccer", ang=0.0, seed=1):
    """Sports ball: kind = soccer, basketball, tennis, baseball, volleyball or football (American); ang = spin."""
    with Pen(img, (cx - r * 1.6, cy - r * 1.6, cx + r * 1.6, cy + r * 1.6), seed) as p:
        _ball(p, cx, cy, r, kind, ang)

def soccer_ball(img, cx, cy, r=60, ang=0.0, seed=1):
    """Soccer ball with black pentagons."""
    ball(img, cx, cy, r, "soccer", ang, seed)

def basketball(img, cx, cy, r=60, ang=0.0, seed=1):
    """Orange basketball with black lines."""
    ball(img, cx, cy, r, "basketball", ang, seed)

def tennis_ball(img, cx, cy, r=36, ang=0.0, seed=1):
    """Yellow-green tennis ball."""
    ball(img, cx, cy, r, "tennis", ang, seed)

def baseball(img, cx, cy, r=40, ang=0.0, seed=1):
    """White baseball with red stitches."""
    ball(img, cx, cy, r, "baseball", ang, seed)

def volleyball(img, cx, cy, r=60, ang=0.0, seed=1):
    """Volleyball with yellow and blue panels."""
    ball(img, cx, cy, r, "volleyball", ang, seed)

def football(img, cx, cy, r=50, ang=-0.4, seed=1):
    """American football (leather, white laces); ang = tilt."""
    ball(img, cx, cy, r, "football", ang, seed)

# ---------- gear ----------
def _racket(p, gx, gy, L, ang, color=RED):
    dx, dy = _dir(ang)
    nx, ny = -dy, dx
    P = lambda a, b: (gx + dx * a * L + nx * b * L, gy + dy * a * L + ny * b * L)
    p.limb([P(-.14, 0), P(.3, 0)], .055 * L, DARK, .012 * L)                     # grip
    p.stroke([P(.3, 0), P(.5, -.1)], .03 * L, color, amp=.2)                     # throat
    p.stroke([P(.3, 0), P(.5, .1)], .03 * L, color, amp=.2)
    hx, hy = P(.72, 0)
    head = ellipse(hx, hy, .22 * L, .3 * L, rot=ang, n=40)
    with p.clip(head):
        p.hatch(head, GRAY, gap=.045 * L, ang=ang, w=max(1.5, .006 * L))
        p.hatch(head, GRAY, gap=.045 * L, ang=ang + math.pi / 2, w=max(1.5, .006 * L))
    p.stroke(head, .045 * L, color, amp=.4, closed=True)
    p.stroke(ellipse(hx, hy, .245 * L, .325 * L, rot=ang, n=40), .012 * L, amp=.4, closed=True)

def tennis_racket(img, gx, gy, L=300, ang=0.0, color=RED, seed=1):
    """Tennis racket held at (gx, gy); ang = tilt from straight up."""
    with Pen(img, (gx - L * 1.15, gy - L * 1.15, gx + L * 1.15, gy + L * 1.15), seed) as p:
        _racket(p, gx, gy, L, ang, color)

def _bat(p, gx, gy, L, ang):
    dx, dy = _dir(ang)
    nx, ny = -dy, dx
    P = lambda a, b: (gx + dx * a * L + nx * b * L, gy + dy * a * L + ny * b * L)
    pts = [P(-.16, -.03), P(.2, -.02), P(.55, -.045), P(.84, -.06), P(.86, 0), P(.84, .06), P(.55, .045), P(.2, .02),
           P(-.16, .03)]
    p.shape(spline(pts, closed=True), WOOD, w=max(3, .018 * L))
    p.shape(ellipse(*P(-.17, 0), .045 * L, .02 * L, rot=ang + math.pi / 2, n=16), WOOD_D, w=max(2, .012 * L), amp=.2)
    p.stroke([P(.4, .015), P(.78, .03)], max(2, .01 * L), WOOD_D, amp=.3)

def baseball_bat(img, gx, gy, L=320, ang=0.0, seed=1):
    """Wooden baseball bat held at (gx, gy); ang = tilt from straight up."""
    with Pen(img, (gx - L * 1.1, gy - L * 1.1, gx + L * 1.1, gy + L * 1.1), seed) as p:
        _bat(p, gx, gy, L, ang)

def _glove(p, cx, cy, r, color=RED, ex=None, ey=None):
    ux, uy = (0.0, 1.0)
    if ex is not None:
        ux, uy = ex - cx, ey - cy; ln = math.hypot(ux, uy) or 1; ux, uy = ux / ln, uy / ln
    p.limb([(cx + ux * r * .7, cy + uy * r * .7), (cx + ux * r * 1.35, cy + uy * r * 1.35)], r * .95, WHITE, r * .14)
    a = math.atan2(uy, ux)
    p.shape(ellipse(cx - ux * r * .1, cy - uy * r * .1, r * 1.05, r * .9, rot=a, n=36), color, w=r * .16, amp=.5)
    tx, ty = cx + ux * r * .3 - uy * r * .7, cy + uy * r * .3 + ux * r * .7
    p.shape(ellipse(tx, ty, r * .42, r * .3, rot=a + .6, n=20), color, w=r * .13, amp=.3)
    p.stroke([(cx - ux * r * .7 + uy * r * .25, cy - uy * r * .7 - ux * r * .25), (cx - ux * r * .2 + uy * r * .55, cy - uy * r * .2 - ux * r * .55)],
             r * .08, tuple(int(v * .8) for v in color), amp=.2)

def boxing_glove(img, cx, cy, r=60, color=RED, ang=0.0, seed=1):
    """Boxing glove with a white cuff; ang = which way the cuff points (0 = down)."""
    ex, ey = cx - math.sin(ang) * r * 3, cy + math.cos(ang) * r * 3
    with Pen(img, (cx - r * 2.2, cy - r * 2.2, cx + r * 2.2, cy + r * 2.2), seed) as p:
        _glove(p, cx, cy, r, color, ex, ey)

def dumbbell(img, cx, cy, w=240, color=DARK, seed=1):
    """Gym dumbbell lying sideways."""
    with Pen(img, (cx - w * .65, cy - w * .4, cx + w * .65, cy + w * .4), seed) as p:
        p.limb([(cx - w * .4, cy), (cx + w * .4, cy)], w * .05, SILVER, max(2, w * .015))
        p.shape(rrect(cx - w * .15, cy - w * .045, cx + w * .15, cy + w * .045, w * .02), GRAY, w=max(2, w * .015), amp=.3)
        for sd in (-1, 1):
            for k, (h, t) in enumerate(((.32, .08), (.24, .06))):
                x = cx + sd * (w * .38 + k * w * .085)
                p.shape(rrect(x - w * t / 2, cy - w * h / 2, x + w * t / 2, cy + w * h / 2, w * .02), color, w=max(3, w * .02), amp=.4)

def kettlebell(img, cx, base, h=180, color=DARK, seed=1, shadow=False):
    """Kettlebell standing on the floor."""
    r = h * .38
    cy = base - r
    with Pen(img, (cx - h * .6, base - h * 1.1, cx + h * .6, base + h * .06), seed) as p:
        if shadow: p.blob(cx, base, r * 1.1, h * .05)
        p.stroke(spline([(cx - r * .55, cy - r * .7), (cx - r * .65, base - h * 1.0), (cx + r * .65, base - h * 1.0),
                         (cx + r * .55, cy - r * .7)]), h * .09, color, amp=.5)
        p.stroke(spline([(cx - r * .55, cy - r * .7), (cx - r * .65, base - h * 1.0), (cx + r * .65, base - h * 1.0),
                         (cx + r * .55, cy - r * .7)]), h * .03, GRAY, amp=.3)
        body = spline([(cx - r * .7, base), (cx - r, cy), (cx - r * .6, cy - r * .85), (cx + r * .6, cy - r * .85), (cx + r, cy),
                       (cx + r * .7, base)], closed=True)
        p.shape(body, color, w=max(3, h * .03))
        p.stroke(spline([(cx - r * .55, cy - r * .3), (cx - r * .3, cy - r * .6), (cx, cy - r * .65)]), h * .03, GRAY, amp=.3)

def sneaker(img, cx, base, w=220, color=RED, seed=1, shadow=False):
    """Running shoe seen from the side, toe on the right."""
    h = w * .42
    with Pen(img, (cx - w * .65, base - h * 1.25, cx + w * .65, base + w * .06), seed) as p:
        if shadow: p.blob(cx, base, w * .5, w * .04)
        upper = spline([(cx - w * .46, base - h * .25), (cx - w * .44, base - h * .95), (cx - w * .2, base - h * 1.0),
                        (cx - w * .02, base - h * .7), (cx + w * .3, base - h * .5), (cx + w * .48, base - h * .25)], closed=False)
        p.shape(upper + [(cx + w * .48, base - h * .2), (cx - w * .46, base - h * .2)], color, w=max(3, w * .025))
        p.shape(rrect(cx - w * .5, base - h * .3, cx + w * .52, base, h * .14), WHITE, w=max(3, w * .025), amp=.6)
        p.stroke([(cx - w * .45, base - h * .12), (cx + w * .45, base - h * .12)], max(2, w * .01), GRAY, amp=.3)
        for k in range(4):
            x = cx - w * .14 + k * w * .07
            p.stroke([(x - w * .04, base - h * (.82 - k * .06)), (x + w * .05, base - h * (.72 - k * .06))], max(2, w * .016), WHITE, amp=.1)
        p.stroke(spline([(cx - w * .3, base - h * .5), (cx, base - h * .45), (cx + w * .2, base - h * .35)]), max(3, w * .03), WHITE, amp=.3)

def whistle(img, cx, cy, w=120, color=SILVER, seed=1):
    """Referee whistle with a cord; mouthpiece on the left."""
    with Pen(img, (cx - w * .9, cy - w * .9, cx + w * .9, cy + w * .6), seed) as p:
        p.stroke(spline([(cx + w * .1, cy - w * .3), (cx + w * .3, cy - w * .75), (cx + w * .7, cy - w * .6), (cx + w * .5, cy - w * .2)]),
                 max(2, w * .03), RED, amp=.4)
        p.shape(ellipse(cx + w * .12, cy, w * .3, w * .27, n=32), color, w=max(3, w * .04), amp=.4)
        p.shape([(cx - w * .62, cy - w * .2), (cx + w * .05, cy - w * .27), (cx + w * .05, cy - w * .02), (cx - w * .62, cy - w * .05)],
                color, w=max(3, w * .04), amp=.3)
        p.poly(ellipse(cx + w * .2, cy - w * .02, w * .07, w * .07, n=12), DARK)

def stopwatch(img, cx, cy, r=90, seconds=15, seed=1):
    """Stopwatch; 'seconds' places the hand."""
    with Pen(img, (cx - r * 1.3, cy - r * 1.6, cx + r * 1.3, cy + r * 1.2), seed) as p:
        p.shape(rrect(cx - r * .14, cy - r * 1.3, cx + r * .14, cy - r * .95, r * .05), GRAY, w=max(3, r * .05), amp=.3)
        p.shape(rrect(cx - r * .3, cy - r * 1.45, cx + r * .3, cy - r * 1.28, r * .06), RED, w=max(3, r * .05), amp=.3)
        p.shape(rotated(rrect(cx - r * .1, cy - r * 1.18, cx + r * .1, cy - r * .98, r * .04), cx, cy, .8), GRAY, w=max(3, r * .04), amp=.2)
        p.shape(ellipse(cx, cy, r, r, n=56), SILVER, w=max(4, r * .08))
        p.shape(ellipse(cx, cy, r * .82, r * .82, n=48), WHITE, w=max(3, r * .04), amp=.4)
        for k in range(12):
            a = 2 * math.pi * k / 12; L = .14 if k % 3 == 0 else .07
            p.stroke([(cx + math.sin(a) * r * .74, cy - math.cos(a) * r * .74),
                      (cx + math.sin(a) * r * (.74 - L), cy - math.cos(a) * r * (.74 - L))], max(2, r * .035), amp=.1)
        a = 2 * math.pi * (seconds % 60) / 60
        p.stroke([(cx, cy), (cx + math.sin(a) * r * .65, cy - math.cos(a) * r * .65)], max(3, r * .05), RED, amp=.2)
        p.poly(ellipse(cx, cy, r * .07, r * .07, n=12), INK)

def cone(img, cx, base, h=160, color=ORANGE, seed=1, shadow=False):
    """Training cone with white stripes."""
    w = h * .7
    with Pen(img, (cx - w * .75, base - h * 1.1, cx + w * .75, base + h * .06), seed) as p:
        if shadow: p.blob(cx, base, w * .6, h * .05)
        p.shape(rrect(cx - w * .55, base - h * .1, cx + w * .55, base, h * .03), color, w=max(3, h * .025), amp=.4)
        body = [(cx - w * .08, base - h), (cx + w * .08, base - h), (cx + w * .42, base - h * .1), (cx - w * .42, base - h * .1)]
        p.poly(p.wobble(body, .4, True), color)
        with p.clip(body):
            for y0, y1 in ((.55, .68), (.28, .4)):
                p.poly([(cx - w, base - h * y1), (cx + w, base - h * y1), (cx + w, base - h * y0), (cx - w, base - h * y0)], WHITE)
        p.stroke(body, max(3, h * .03), amp=.5, closed=True)

def skateboard(img, cx, base, w=320, color=RED, seed=1, shadow=False):
    """Skateboard seen from the side."""
    r = w * .055
    with Pen(img, (cx - w * .6, base - w * .25, cx + w * .6, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .5, w * .03)
        deck = spline([(cx - w * .5, base - w * .2), (cx - w * .4, base - w * .14), (cx + w * .4, base - w * .14),
                       (cx + w * .5, base - w * .2), (cx + w * .4, base - w * .11), (cx - w * .4, base - w * .11)], closed=True)
        for x in (cx - w * .3, cx + w * .3):
            p.shape([(x - w * .05, base - w * .11), (x + w * .05, base - w * .11), (x + w * .03, base - r * 1.6), (x - w * .03, base - r * 1.6)],
                    GRAY, w=max(2, w * .012), amp=.2)
            for dx in (-w * .03, w * .03):
                p.shape(ellipse(x + dx, base - r, r, r, n=20), YELLOW, w=max(2, w * .012), amp=.3)
        p.shape(deck, color, w=max(3, w * .016), amp=.6)

def jersey(img, cx, cy, w=220, color=BLUE, number=10, name=None, seed=1):
    """Team shirt seen from the back, with number (and name)."""
    h = w * 1.05
    with Pen(img, (cx - w * .75, cy - h * .6, cx + w * .75, cy + h * .6), seed) as p:
        top, bot = cy - h * .45, cy + h * .5
        pts = [(cx - w * .18, top), (cx - w * .5, top + h * .08), (cx - w * .68, top + h * .32), (cx - w * .46, top + h * .42),
               (cx - w * .38, top + h * .3), (cx - w * .38, bot), (cx + w * .38, bot), (cx + w * .38, top + h * .3),
               (cx + w * .46, top + h * .42), (cx + w * .68, top + h * .32), (cx + w * .5, top + h * .08), (cx + w * .18, top)]
        p.shape(pts, color, w=max(3, w * .028))
        p.stroke(spline([(cx - w * .18, top), (cx, top + h * .06), (cx + w * .18, top)]), max(3, w * .03), WHITE, amp=.3)
        if name: p.text(str(name).upper(), cx, top + h * .2, w * .13, fill=WHITE, stroke=INK, sw=max(1, w * .006), warp=.6)
        if number is not None:
            p.text(str(number), cx, cy + h * .14, w * .42, fill=WHITE, stroke=INK, sw=max(2, w * .012), warp=1)

# ---------- awards ----------
def trophy(img, cx, base, h=260, color=GOLD, label=None, seed=1, shadow=False):
    """Trophy cup with two handles on a base; label = text on the plate."""
    w = h * .7
    dark = GOLD_D if color == GOLD else tuple(int(v * .72) for v in color)
    with Pen(img, (cx - w * .8, base - h * 1.1, cx + w * .8, base + h * .06), seed) as p:
        if shadow: p.blob(cx, base, w * .5, h * .04)
        cup_top, cup_bot = base - h, base - h * .5
        for sd in (-1, 1):
            p.stroke(spline([(cx + sd * w * .36, cup_top + h * .08), (cx + sd * w * .62, cup_top + h * .1),
                             (cx + sd * w * .58, cup_top + h * .3), (cx + sd * w * .22, cup_bot - h * .02)]), h * .045, dark, amp=.4)
        p.shape(rrect(cx - w * .42, base - h * .14, cx + w * .42, base, h * .02), DARK, w=max(3, h * .02), amp=.4)
        p.shape(rrect(cx - w * .3, base - h * .2, cx + w * .3, base - h * .13, h * .02), dark, w=max(3, h * .018), amp=.3)
        p.shape([(cx - w * .07, cup_bot), (cx + w * .07, cup_bot), (cx + w * .12, base - h * .2), (cx - w * .12, base - h * .2)],
                color, w=max(3, h * .02), amp=.3)
        cup = spline([(cx - w * .42, cup_top), (cx - w * .38, cup_top + h * .28), (cx - w * .1, cup_bot), (cx + w * .1, cup_bot),
                      (cx + w * .38, cup_top + h * .28), (cx + w * .42, cup_top)])
        p.shape(cup, color, w=max(3, h * .025))
        p.stroke([(cx - w * .26, cup_top + h * .06), (cx - w * .22, cup_top + h * .26)], h * .03, WHITE, amp=.2)
        p.stroke(ellipse(cx, cup_top, w * .42, h * .03, n=28), max(2, h * .015), dark, amp=.3, closed=True)
        star = [(cx + math.cos(-math.pi / 2 + k * math.pi / 5) * h * (.07 if k % 2 == 0 else .03),
                 cup_top + h * .2 + math.sin(-math.pi / 2 + k * math.pi / 5) * h * (.07 if k % 2 == 0 else .03)) for k in range(10)]
        p.shape(star, WHITE, w=max(2, h * .012), amp=.2)
        if label: p.text(str(label), cx, base - h * .07, h * .075, fill=GOLD, warp=0)

MEDAL_COLORS = {1: (GOLD, GOLD_D), 2: (SILVER, SILVER_D), 3: (BRONZE_M, BRONZE_MD)}

def medal(img, cx, cy, r=60, place=1, ribbon=(RED, BLUE), seed=1):
    """Medal on a V ribbon: place 1 gold, 2 silver, 3 bronze; (cx, cy) = center of the disc."""
    color, dark = MEDAL_COLORS.get(place, MEDAL_COLORS[1])
    with Pen(img, (cx - r * 1.6, cy - r * 3.6, cx + r * 1.6, cy + r * 1.3), seed) as p:
        for sd, col in zip((-1, 1), ribbon):
            p.shape([(cx + sd * r * 1.1, cy - r * 3.3), (cx + sd * r * .45, cy - r * 3.3), (cx - sd * r * .1, cy - r * .7),
                     (cx + sd * r * .45, cy - r * .7)], col, w=max(3, r * .07), amp=.4)
        p.shape(ellipse(cx, cy, r, r, n=44), color, w=max(3, r * .08), amp=.5)
        p.stroke(ellipse(cx, cy, r * .75, r * .75, n=36), max(2, r * .05), dark, amp=.3, closed=True)
        p.text(str(place), cx, cy + r * .02, r * .9, fill=dark, warp=0)

def podium(img, cx, base, w=520, colors=(GOLD, SILVER, BRONZE_M), seed=1, shadow=False):
    """Winners' podium: 1 in the middle (tallest), 2 on the left, 3 on the right. Returns the top-center of each step."""
    bw = w / 3
    hs = {1: w * .42, 2: w * .3, 3: w * .22}
    xs = {2: cx - bw, 1: cx, 3: cx + bw}
    with Pen(img, (cx - w * .6, base - w * .5, cx + w * .6, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .03)
        for k in (2, 3, 1):
            x, h = xs[k], hs[k]
            p.shape([(x - bw / 2, base - h), (x + bw / 2, base - h), (x + bw / 2, base), (x - bw / 2, base)], WHITE, w=max(3, w * .012))
            p.poly(p.wobble([(x - bw / 2 + 4, base - h + 4), (x + bw / 2 - 4, base - h + 4), (x + bw / 2 - 4, base - h + w * .03),
                             (x - bw / 2 + 4, base - h + w * .03)], .3, True), colors[k - 1])
            p.text(str(k), x, base - h * .5, bw * .5, fill=colors[k - 1], stroke=INK, sw=max(2, w * .005), warp=.8)
    return {k: (xs[k], base - hs[k]) for k in (1, 2, 3)}

# ---------- places ----------
def soccer_goal(img, cx, base, w=520, seed=1, shadow=False):
    """Soccer goal with net, seen from the front."""
    h = w * .4
    with Pen(img, (cx - w * .58, base - h * 1.15, cx + w * .58, base + w * .04), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .025)
        net = [(cx - w * .5, base - h), (cx + w * .5, base - h), (cx + w * .5, base), (cx - w * .5, base)]
        p.hatch(net, NET, gap=w * .04, ang=.75, w=max(1.5, w * .004))
        p.hatch(net, NET, gap=w * .04, ang=-.75, w=max(1.5, w * .004))
        p.stroke([(cx - w * .42, base - h * .88), (cx + w * .42, base - h * .88), (cx + w * .42, base), ], max(2, w * .005), GRAY, amp=.4)
        p.stroke([(cx - w * .42, base - h * .88), (cx - w * .42, base)], max(2, w * .005), GRAY, amp=.4)
        frame = [(cx - w * .5, base), (cx - w * .5, base - h), (cx + w * .5, base - h), (cx + w * .5, base)]
        p.stroke(frame, w * .028, INK, amp=.8)
        p.stroke(frame, w * .016, WHITE, amp=.8, taper=False)

def basketball_hoop(img, cx, base, h=640, seed=1, shadow=False):
    """Basketball hoop on a pole: backboard, orange rim, net. Returns the rim center."""
    bw = h * .5
    top = base - h
    rim = (cx, top + bw * .62)
    with Pen(img, (cx - bw * .7, top - 10, cx + bw * .7, base + h * .03), seed) as p:
        if shadow: p.blob(cx, base, bw * .3, h * .02)
        p.shape(rrect(cx - h * .025, top + bw * .5, cx + h * .025, base, 4), GRAY, w=max(3, h * .008), amp=.4)
        p.shape(rrect(cx - bw * .2, base - h * .03, cx + bw * .2, base, 4), DARK, w=max(3, h * .008), amp=.3)
        board = rrect(cx - bw / 2, top, cx + bw / 2, top + bw * .6, h * .012)
        p.shape(board, WHITE, w=max(4, h * .01))
        p.stroke([(cx - bw * .16, top + bw * .52), (cx - bw * .16, top + bw * .3), (cx + bw * .16, top + bw * .3),
                  (cx + bw * .16, top + bw * .52)], max(3, h * .008), RED, amp=.3)
        rx, ry = rim
        for k in range(6):
            t = k / 5
            x0 = rx - bw * .2 + bw * .4 * t
            x1 = rx - bw * .13 + bw * .26 * t
            p.stroke([(x0, ry), (x1, ry + bw * .35)], max(2, h * .004), GRAY, amp=.3)
        for k in (1, 2):
            f = k / 3
            p.stroke([(rx - bw * (.2 - .07 * f), ry + bw * .35 * f), (rx + bw * (.2 - .07 * f), ry + bw * .35 * f)], max(2, h * .004), GRAY, amp=.4)
        p.stroke(ellipse(rx, ry, bw * .21, bw * .05, n=32), max(4, h * .012), ORANGE, amp=.3, closed=True)
    return rim

def scoreboard(img, cx, cy, w=420, home="2", away="1", labels=("HOME", "AWAY"), seed=1):
    """Scoreboard with two scores and their labels."""
    h = w * .5
    with Pen(img, (cx - w * .58, cy - h * .65, cx + w * .58, cy + h * .62), seed) as p:
        p.shape(rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, w * .03), DARK, w=max(4, w * .015))
        for sd, val, lab in ((-1, home, labels[0]), (1, away, labels[1])):
            x = cx + sd * w * .24
            p.shape(rrect(x - w * .18, cy - h * .2, x + w * .18, cy + h * .38, w * .02), INK, w=max(2, w * .008), amp=.3)
            p.text(str(val), x, cy + h * .09, h * .48, fill=YELLOW, warp=0)
            if lab: p.text(str(lab), x, cy - h * .33, h * .14, fill=WHITE, warp=0)
        p.text(":", cx, cy + h * .06, h * .3, fill=YELLOW, warp=0)

def finish_flag(img, cx, base, h=420, wave=0.0, seed=1, shadow=False):
    """Checkered finish flag on a pole; wave = 0…1 phase of the flutter (animate with t)."""
    fw, fh = h * .55, h * .36
    top = base - h
    with Pen(img, (cx - h * .1, top - h * .08, cx + fw * 1.25, base + h * .03), seed) as p:
        if shadow: p.blob(cx, base, h * .08, h * .02)
        p.limb([(cx, base), (cx, top)], max(4, h * .018), GRAY_L, max(2, h * .006))
        p.shape(ellipse(cx, top - h * .015, h * .025, h * .025, n=14), GOLD, w=max(2, h * .006), amp=.2)
        def F(u, v):
            return (cx + u * fw, top + v * fh + math.sin((u * 2.2 + wave) * math.pi * 2) * fh * .1 * u)
        n, m = 6, 4
        for i in range(n):
            for j in range(m):
                cell = [F(i / n, j / m), F((i + 1) / n, j / m), F((i + 1) / n, (j + 1) / m), F(i / n, (j + 1) / m)]
                p.poly(cell, INK if (i + j) % 2 else WHITE)
        p.stroke([F(k / 24, 0) for k in range(25)] + [F(1, k / 8) for k in range(9)] + [F(1 - k / 24, 1) for k in range(25)],
                 max(3, h * .009), amp=.5)

# ---------- athletes ----------
class _Place:
    def __init__(self, x, y, s): self.x, self.y, self.s = x, y, s
    def __call__(self, dx, dy): return (self.x + dx * self.s, self.y + dy * self.s)

def _headband(p, hx, hy, r, color):
    head = ellipse(hx, hy, r * 1.01, r * 1.03, n=64)
    with p.clip(head):
        band = [(hx - r * 1.2, hy - r * .82), (hx + r * 1.2, hy - r * .82), (hx + r * 1.2, hy - r * .62), (hx - r * 1.2, hy - r * .62)]
        p.poly(band, color)
        p.stroke([(hx - r * 1.1, hy - r * .82), (hx + r * 1.1, hy - r * .82)], r * .05, amp=.4)
        p.stroke([(hx - r * 1.1, hy - r * .62), (hx + r * 1.1, hy - r * .62)], r * .05, amp=.4)
    p.stroke(head, r * .1, amp=.8, closed=True)

def _cap(p, hx, hy, r, look, color):
    R, a0 = r * 1.06, math.asin(.55)
    crown = [(hx + R * math.cos(t), hy + R * math.sin(t)) for t in
             (math.pi + a0 + (math.pi - 2 * a0) * k / 24 for k in range(25))]
    p.shape(crown, color, w=r * .09, amp=.6)
    p.stroke([(hx + look * r * .2, hy - R), (hx + look * r * .35, hy - R * .58)], r * .04, tuple(int(v * .7) for v in color), amp=.3)
    p.shape(ellipse(hx + look * r * .2, hy - R * .99, r * .1, r * .06, n=12), color, w=r * .04, amp=.2)
    vx = hx + look * r * .55
    visor = [(vx + r * .8 * math.cos(t), hy - R * .55 + r * .2 * math.sin(t)) for t in (math.pi * k / 16 for k in range(17))]
    p.shape(visor + [(vx - r * .8, hy - R * .55)], color, w=r * .08, amp=.4)

def _kit(img, x, y, s, sport, mood, arms, look, color, number, seed, **kw):
    P = _Place(x, y, s)
    torso = [P(-44, -418), P(44, -418), P(54, -330), P(50, -238), P(-50, -238), P(-54, -330)]
    tank = [P(-40, -418), P(-24, -418), P(0, -392), P(24, -418), P(40, -418), P(44, -372), P(54, -330), P(50, -238), P(-50, -238),
            P(-54, -330), P(-44, -372)]
    shorts_c = kw.get("shorts") or {"soccer": WHITE, "basketball": color, "boxer": color, "runner": DARK, "tennis": WHITE,
                                    "baseball": WHITE, "referee": DARK}[sport]
    shorts_low = {"basketball": -150, "boxer": -175, "runner": -205, "baseball": -120}.get(sport, -190)

    def shorts(p):
        gap = 4 if shorts_low > -160 else 8
        p.shape([P(-52, -256), P(52, -256), P(60, shorts_low), P(gap, shorts_low), P(0, shorts_low - 22), P(-gap, shorts_low),
                 P(-60, shorts_low)], shorts_c, w=6 * s)

    def number_on(p, yy, size=56, fill=WHITE):
        if number is not None: p.text(str(number), *P(0, yy), size * s, fill=fill, stroke=INK, sw=2.5 * s, warp=.8)

    def dress(p, a):
        if sport in ("soccer", "tennis", "baseball"):
            p.shape(torso, color, w=7.5 * s, smooth=True)
            shorts(p)
            if sport == "soccer":
                p.stroke(spline([P(-22, -418), P(0, -398), P(22, -418)]), 5 * s, WHITE, amp=.3)
                number_on(p, -330)
            elif sport == "tennis":
                for sd in (-1, 1): p.shape([P(0, -400), P(sd * 30, -420), P(sd * 26, -396)], WHITE, w=4 * s, amp=.3)
                p.stroke([P(0, -400), P(0, -360)], 3 * s, amp=.2)
            else:
                p.stroke([P(0, -406), P(0, -246)], 3 * s, tuple(int(v * .7) for v in color), amp=.3)
                for yy in (-380, -340, -300, -265): p.poly(ellipse(*P(5, yy), 3 * s, 3 * s, n=8), INK)
                p.text(str(kw.get("team") or ""), *P(-20, -360), 24 * s, fill=WHITE, warp=.5)
                p.stroke(spline([P(-22, -418), P(0, -404), P(22, -418)]), 5 * s, amp=.3)
        elif sport in ("basketball", "runner"):
            p.shape(tank, color, w=7 * s)
            shorts(p)
            if sport == "basketball":
                for side in (-1, 1): p.stroke([P(60 * side, shorts_low + 4), P(56 * side, -250)], 5 * s, WHITE, amp=.3)
                number_on(p, -322, 62)
            else:
                bib = rrect(*P(-30, -372), *P(30, -312), 4 * s)
                p.shape(bib, WHITE, w=4 * s, amp=.3)
                for bx in (-22, 22): p.poly(ellipse(*P(bx, -364), 2.5 * s, 2.5 * s, n=8), INK)
                if number is not None: p.text(str(number), *P(0, -340), 34 * s, warp=.4)
        elif sport == "boxer":
            for sd in (-1, 1):
                p.stroke(spline([P(sd * 38, -385), P(sd * 18, -372), P(sd * 4, -380)]), 3.5 * s, GRAY, amp=.3)
            p.poly(ellipse(*P(0, -292), 3 * s, 4 * s, n=10), GRAY)
            shorts(p)
            p.limb([P(-54, -258), P(54, -258)], 14 * s, WHITE, 3.5 * s)
        elif sport == "referee":
            p.shape(torso, WHITE, w=0, smooth=True)
            with p.clip(spline(torso, closed=True)):
                for k in range(-3, 4):
                    p.poly(p.wobble([P(k * 22 - 5, -430), P(k * 22 + 5, -430), P(k * 22 + 5, -230), P(k * 22 - 5, -230)], .3, True), INK)
            p.stroke(spline(torso, closed=True), 7.5 * s, amp=1, closed=True)
            p.stroke(spline([P(-22, -418), P(0, -400), P(22, -418)]), 8 * s, amp=.3)
            shorts(p)
            p.stroke(spline([P(-20, -414), P(-6, -360), P(6, -360), P(20, -414)]), 2.5 * s, RED, amp=.2)
            wx, wy = P(8, -352)
            p.shape(ellipse(wx, wy, 11 * s, 10 * s, n=16), SILVER, w=3 * s, amp=.2)
            p.shape([(wx - 26 * s, wy - 8 * s), (wx, wy - 9 * s), (wx, wy), (wx - 26 * s, wy - 2 * s)], SILVER, w=3 * s, amp=.2)

    def hat(p, a):
        (hx, hy), r = a["head"], a["head_r"]
        if sport in ("runner", "tennis") and kw.get("headband", True):
            _headband(p, hx, hy, r, kw.get("band") or (RED if sport == "runner" else color))
        elif sport == "baseball":
            _cap(p, hx, hy, r, look, kw.get("cap") or color)

    def extras(p, a):
        sleeve = {"soccer": color, "tennis": color, "baseball": color, "referee": INK}.get(sport)
        if sleeve:
            for sh, el in zip(a["shoulders"], a["elbows"]):
                p.limb([sh, (sh[0] + (el[0] - sh[0]) * .6, sh[1] + (el[1] - sh[1]) * .6)], 26 * s, sleeve, 4.5 * s)
        sock = {"soccer": color, "basketball": WHITE, "tennis": WHITE, "baseball": color, "referee": INK, "runner": WHITE,
                "boxer": WHITE}[sport]
        low = {"soccer": -110, "baseball": -112, "referee": -100}.get(sport, -55)
        shoe = {"soccer": INK, "baseball": INK, "referee": INK, "boxer": color, "basketball": RED if color != RED else WHITE,
                "runner": BLUE, "tennis": WHITE}[sport]
        for side in (-1, 1):
            p.limb([P(27 * side + look * 5, low), P(30 * side, -14)], 15 * s, sock, 3 * s)
            if sport == "soccer": p.stroke([P(26 * side + look * 5, low + 14), P(34 * side + look * 5, low + 14)], 4 * s, WHITE, amp=.2)
            d = look or side
            p.shape(spline([P(30 * side - 18 * d, -2), P(30 * side - 16 * d, -22), P(30 * side + 8 * d, -24),
                            P(30 * side + 34 * d, -12), P(30 * side + 36 * d, -2)], closed=True), shoe, w=4.5 * s, amp=.4)
        if sport == "boxer":
            for hd, el in zip((a["hand_l"], a["hand_r"]), a["elbows"]):
                _glove(p, hd[0], hd[1], 30 * s, color if color != WHITE else RED, *el)
        if sport == "referee" and kw.get("card"):
            hx, hy = a["hand_r"]
            col = {"yellow": YELLOW, "red": RED}.get(kw["card"], kw["card"])
            p.shape(rotated(rrect(hx - 22 * s, hy - 84 * s, hx + 22 * s, hy - 12 * s, 4 * s), hx, hy, .12), col, w=4 * s, amp=.3)
            p.shape(ellipse(hx, hy, 14 * s, 14 * s, n=20), WHITE, w=5 * s, amp=.6)

    a = doodle(img, x, y, s, outfit="tshirt", mood=mood, arms=arms, look=look, color=WHITE, dress=dress, hat=hat,
               extras=extras, seed=seed)
    gx, gy = a["hand_r"]
    right = arms if isinstance(arms, str) else arms[1]
    held = kw.get("held")
    if held:
        ang = kw.get("ang")
        if ang is None: ang = {"up": .2, "down": math.pi - .5}.get(right, .6)
        L = 300 * s
        with Pen(img, (gx - L * 1.2, gy - L * 1.2, gx + L * 1.2, gy + L * 1.2), seed + 3) as p:
            if held == "racket": _racket(p, gx, gy, L * .95, ang, kw.get("gear") or RED)
            elif held == "bat": _bat(p, gx, gy, L * 1.05, ang)
            elif held in BALLS: _ball(p, gx, gy - 40 * s, 42 * s if held != "tennis" else 22 * s, held, .3)
            p.shape(ellipse(gx, gy, 14 * s, 14 * s, n=20), WHITE, w=5 * s, amp=.6)
    if kw.get("mitt"):
        hx, hy = a["hand_l"]
        with Pen(img, (hx - 80 * s, hy - 80 * s, hx + 80 * s, hy + 80 * s), seed + 5) as p:
            mitt = spline([(hx - 34 * s, hy + 20 * s), (hx - 40 * s, hy - 26 * s), (hx - 16 * s, hy - 46 * s), (hx + 16 * s, hy - 44 * s),
                           (hx + 36 * s, hy - 16 * s), (hx + 30 * s, hy + 24 * s)], closed=True)
            p.shape(mitt, LEATHER, w=5 * s)
            for k in (-1, 0, 1): p.stroke([(hx + k * 12 * s, hy - 36 * s), (hx + k * 10 * s, hy - 4 * s)], 3 * s, LEATHER_D, amp=.2)
            p.limb([(hx - 30 * s, hy + 18 * s), (hx + 28 * s, hy + 20 * s)], 10 * s, LEATHER_D, 3 * s)
    foot_ball = kw.get("ball")
    if foot_ball:
        kind = foot_ball if isinstance(foot_ball, str) else {"basketball": "basketball", "tennis": "tennis"}.get(sport, "soccer")
        r = (22 if kind in ("tennis", "baseball") else 46) * s
        bx = x + (95 if look >= 0 else -95) * s
        with Pen(img, (bx - r * 1.6, y - r * 3.2, bx + r * 1.6, y + r * .6), seed + 9) as p:
            _ball(p, bx, y - r, r, kind, .2)
    return a

def soccer_player(img, x, y, s=1.0, mood="happy", arms=("down", "up"), look=0.0, color=BLUE, number=10, shorts=None,
                  ball=False, held=None, seed=1):
    """doodle as a soccer player: team shirt with number, shorts, long socks, boots; ball=True puts a ball at the feet,
    held="soccer" puts it in the right hand."""
    return _kit(img, x, y, s, "soccer", mood, arms, look, color, number, seed, shorts=shorts, ball=ball, held=held)

def basketball_player(img, x, y, s=1.0, mood="smug", arms=("hip", "offer"), look=0.0, color=ORANGE, number=23,
                      held="basketball", ball=False, seed=1):
    """doodle as a basketball player: tank top with number, long shorts, sneakers; held = basketball/None."""
    return _kit(img, x, y, s, "basketball", mood, arms, look, color, number, seed, held=held, ball=ball)

def boxer(img, x, y, s=1.0, mood="angry", arms=("show", "show"), look=0.0, color=RED, seed=1):
    """doodle as a boxer: bare chest, boxing shorts with a white waistband, big gloves; color = gloves and shorts."""
    return _kit(img, x, y, s, "boxer", mood, arms, look, color, None, seed)

def runner(img, x, y, s=1.0, mood="happy", arms=("up", "up"), look=0.0, color=GREEN, number=7, band=None, seed=1):
    """doodle as a runner: tank top with a race bib, short shorts, headband, sneakers."""
    return _kit(img, x, y, s, "runner", mood, arms, look, color, number, seed, band=band)

def tennis_player(img, x, y, s=1.0, mood="happy", arms=("down", "up"), look=0.0, color=GREEN, racket=RED, ang=None,
                  headband=True, ball=False, seed=1):
    """doodle as a tennis player: polo shirt, white shorts, headband and racket; ball=True drops a ball at the feet."""
    return _kit(img, x, y, s, "tennis", mood, arms, look, color, None, seed, held="racket", gear=racket, ang=ang,
                headband=headband, ball="tennis" if ball else False)

def baseball_player(img, x, y, s=1.0, mood="smug", arms=("down", "up"), look=0.0, color=NAVY, cap=None, team="",
                    bat=True, mitt=False, ang=None, seed=1):
    """doodle as a baseball player: cap, buttoned jersey, knickers, socks; bat=True swings a bat, mitt=True on the left hand."""
    return _kit(img, x, y, s, "baseball", mood, arms, look, color, None, seed, cap=cap, team=team,
                held="bat" if bat else None, mitt=mitt, ang=ang)

def referee(img, x, y, s=1.0, mood="angry", arms=("hip", "up"), look=0.0, card="yellow", seed=1):
    """doodle as a referee: black-and-white striped shirt, whistle, black shorts; card = yellow/red/None in the raised hand."""
    return _kit(img, x, y, s, "referee", mood, arms, look, WHITE, None, seed, card=card)
