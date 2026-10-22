"""Sketch-style ancient history: monuments (pyramid, obelisk, column, temple, colosseum, castle), viking longship,
amphora, scroll, torch, crown, weapons and shields, helmets, and the doodle character dressed as a Roman soldier,
viking, pharaoh, Greek, knight, Aztec warrior or Maya noble, plus Mexican pieces (step pyramid, Sun Stone,
Olmec head, stela, macuahuitl, chimalli, maize, cacao). All take the image (img) and a 'seed'. Monuments and objects that stand on the
floor draw no floor shadow unless shadow=True (the dressed doodle keeps its own).

    a = roman(img, 300, FLOOR, .9, mood="angry")                 # helmet, armor, gladius and shield
    viking(img, 780, FLOOR, .9, mood="happy", weapon="axe")

Weapons take the grip point (where the hand holds them) and 'ang' = tilt from straight up, in radians
(0 = up, .5 = leaning right, math.pi = down)."""
import math
from . import Pen, INK, WHITE, SHADE, RED, WOOD, WOOD_D, BLUE, ellipse, rrect, rotated, spline
from .everyday import YELLOW, GOLD, GOLD_D, GRAY, GRAY_L, DARK, bumpy
from .humans import doodle

SAND, SAND_D = (226, 196, 140), (186, 150, 96)
MARBLE, MARBLE_D = (242, 238, 228), (200, 196, 186)
STONE, STONE_D = (222, 200, 162), (170, 140, 100)
STEEL, STEEL_D = (208, 212, 222), (150, 156, 168)
BRONZE = (205, 150, 70)
FUR = (150, 122, 92)
CREAM = (238, 228, 200)
CLAY, CLAY_D = (204, 112, 62), (150, 72, 36)
PARCH = (240, 226, 186)
FLAME, FLAME_L = (245, 130, 40), (255, 210, 80)
CRIMSON = (190, 40, 40)
TUNIC_GREEN = (105, 125, 80)
LEAF = (110, 160, 70)
JADE, JADE_D = (60, 170, 130), (30, 110, 85)
TURQ = (60, 170, 190)
QUETZAL = (40, 150, 80)
FEATHERS = (QUETZAL, (220, 60, 50), TURQ, (245, 190, 50))
MESO, MESO_D = (210, 196, 168), (160, 144, 116)
CORN, CORN_D = (250, 205, 70), (210, 150, 30)
CACAO, CACAO_D = (214, 120, 50), (150, 70, 30)

def _dir(ang):
    return math.sin(ang), -math.cos(ang)

# ---------- weapons and shields (drawn with a Pen) ----------
def _sword(p, gx, gy, L, ang, kind="long"):
    dx, dy = _dir(ang); nx, ny = -dy, dx
    at = lambda t, o=0: (gx + dx * L * t + nx * o, gy + dy * L * t + ny * o)
    bw = L * (.06 if kind == "gladius" else .04)
    tipf = .8 if kind == "gladius" else .9
    blade = [at(.12, -bw), at(tipf, -bw), at(1), at(tipf, bw), at(.12, bw)]
    p.shape(blade, STEEL, w=max(3, L * .015), amp=.4)
    p.stroke([at(.15), at(tipf - .02)], max(2, L * .008), STEEL_D, amp=.2)
    p.shape([at(.09, -L * .14), at(.09, L * .14), at(.13, L * .14), at(.13, -L * .14)], GOLD if kind == "long" else BRONZE,
            w=max(3, L * .013), amp=.3)
    p.limb([at(-.12), at(.09)], L * .045, WOOD_D, max(2, L * .01))
    pm = at(-.14)
    p.shape(ellipse(pm[0], pm[1], L * .035, L * .035, n=16), GOLD if kind == "long" else BRONZE, w=max(3, L * .012), amp=.3)

def _axe(p, gx, gy, L, ang):
    dx, dy = _dir(ang); nx, ny = -dy, dx
    at = lambda t, o=0: (gx + dx * L * t + nx * o, gy + dy * L * t + ny * o)
    p.limb([at(-.25), at(.78)], L * .045, WOOD, max(2, L * .012))
    edge = spline([at(.46, L * .3), at(.62, L * .4), at(.8, L * .38), at(.92, L * .26)])
    head = [at(.62, L * .02), at(.58, L * .12)] + edge + [at(.84, L * .12), at(.8, L * .02)]
    p.shape(head, STEEL, w=max(3, L * .015), amp=.5)
    p.stroke(spline([at(.52, L * .3), at(.64, L * .36), at(.8, L * .34), at(.88, L * .26)]), max(2, L * .012), WHITE, amp=.3)

def _spear(p, gx, gy, L, ang):
    dx, dy = _dir(ang); nx, ny = -dy, dx
    at = lambda t, o=0: (gx + dx * L * t + nx * o, gy + dy * L * t + ny * o)
    p.limb([at(-.5), at(.38)], L * .025, WOOD, max(2, L * .008))
    p.shape([at(.36, -L * .012), at(.41, -L * .04), at(.5), at(.41, L * .04), at(.36, L * .012)], STEEL, w=max(3, L * .01),
            smooth=True, amp=.3)

def _round_shield(p, cx, cy, r, color=CRIMSON, color2=CREAM):
    pts = ellipse(cx, cy, r, r, n=56)
    p.poly(p.wobble(pts, .6, True), color)
    with p.clip(pts):
        for k in (0, 2):
            a0 = math.pi / 2 * k + .3
            p.poly([(cx, cy)] + [(cx + math.cos(a0 + i * .1) * r * 1.1, cy + math.sin(a0 + i * .1) * r * 1.1) for i in range(17)], color2)
        for k in range(-3, 4):
            p.stroke([(cx + k * r * .28, cy - r), (cx + k * r * .28, cy + r)], max(2, r * .025), WOOD_D, amp=.4)
    p.stroke(pts, max(4, r * .07), amp=.8, closed=True)
    p.stroke(ellipse(cx, cy, r * .93, r * .93, n=56), max(3, r * .05), STEEL_D, amp=.5, closed=True)
    p.shape(ellipse(cx, cy, r * .22, r * .22, n=24), STEEL, w=max(3, r * .05), amp=.4)

def _scutum(p, cx, cy, h, color=CRIMSON):
    w = h * .62
    body = rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, w * .12)
    p.shape(body, color, w=max(4, h * .022))
    p.stroke(rrect(cx - w * .42, cy - h * .44, cx + w * .42, cy + h * .44, w * .08), max(3, h * .015), GOLD, amp=.5, closed=True)
    for sx in (-1, 1):                                        # stylized wings and bolts
        p.stroke(spline([(cx + sx * w * .1, cy), (cx + sx * w * .22, cy - h * .12), (cx + sx * w * .34, cy - h * .2)]), max(3, h * .014), GOLD, amp=.4)
        p.stroke([(cx + sx * w * .1, cy + h * .05), (cx + sx * w * .2, cy + h * .2), (cx + sx * w * .12, cy + h * .22),
                  (cx + sx * w * .25, cy + h * .38)], max(3, h * .014), GOLD, amp=.4)
    p.shape(ellipse(cx, cy, w * .14, w * .14, n=24), BRONZE, w=max(3, h * .014), amp=.4)

def _heater_shield(p, cx, cy, h, color=WHITE, cross=RED):
    w = h * .8
    body = [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2)] + spline([(cx + w / 2, cy - h / 2), (cx + w * .44, cy + h * .05),
                                                                            (cx, cy + h / 2)])[1:] + \
           spline([(cx, cy + h / 2), (cx - w * .44, cy + h * .05), (cx - w / 2, cy - h / 2)])[1:-1]
    p.poly(p.wobble(body, .6, True), color)
    with p.clip(body):
        p.poly([(cx - w * .08, cy - h), (cx + w * .08, cy - h), (cx + w * .08, cy + h), (cx - w * .08, cy + h)], cross)
        p.poly([(cx - w, cy - h * .2), (cx + w, cy - h * .2), (cx + w, cy - h * .05), (cx - w, cy - h * .05)], cross)
    p.stroke(body, max(4, h * .025), amp=.8, closed=True)

# ---------- headgear (fits a head of radius r centered on hx, hy) ----------
def _viking_helmet(p, hx, hy, r, look=0.0, horns=True):
    band = hy - r * .2
    dome = [(hx - r * 1.04, band)] + [(hx + math.cos(a) * r * 1.04, band + math.sin(a) * r * .95)
                                      for a in (math.pi + math.pi * k / 24 for k in range(1, 24))] + [(hx + r * 1.04, band)]
    if horns:
        for sd in (-1, 1):
            base_ = (hx + sd * r * .82, hy - r * .55)
            horn = spline([(base_[0], base_[1] + r * .12), (hx + sd * r * 1.3, hy - r * .6), (hx + sd * r * 1.48, hy - r * 1.05),
                           (hx + sd * r * 1.36, hy - r * 1.32)]) + \
                   spline([(hx + sd * r * 1.36, hy - r * 1.32), (hx + sd * r * 1.3, hy - r * 1.02), (hx + sd * r * 1.1, hy - r * .78),
                           (base_[0], base_[1] - r * .14)])[1:]
            p.shape(horn, CREAM, w=r * .06, amp=.5)
    p.shape(dome, STEEL, w=r * .08, amp=.7)
    p.shape(rrect(hx - r * 1.06, band - r * .08, hx + r * 1.06, band + r * .1, r * .05), BRONZE, w=r * .06, amp=.5)
    p.stroke([(hx, band - r * .9), (hx, band - r * .08)], r * .07, BRONZE, amp=.3)
    fx = hx + look * .16 * r
    p.shape([(fx - r * .05, band + r * .08), (fx + r * .05, band + r * .08), (fx + r * .04, hy + r * .2), (fx - r * .04, hy + r * .2)],
            BRONZE, w=r * .045, amp=.3)

def _roman_helmet(p, hx, hy, r, look=0.0, crest=CRIMSON):
    band = hy - r * .3
    crest_pts = [(hx - r * .72, hy - r * 1.0)] + [(hx + math.cos(a) * r * .75, hy - r * 1.0 + math.sin(a) * r * .6)
                                                 for a in (math.pi + math.pi * k / 20 for k in range(1, 20))] + [(hx + r * .72, hy - r * 1.0)]
    p.poly(p.wobble(crest_pts, .6, True), crest)
    p.hatch(crest_pts, tuple(int(v * .7) for v in crest), gap=r * .1, ang=0, w=r * .025)
    p.stroke(crest_pts, r * .06, amp=.6, closed=True)
    for sd in (-1, 1):                                        # cheek guards
        p.shape([(hx + sd * r * .98, band), (hx + sd * r * .7, band + r * .05), (hx + sd * r * .66, hy + r * .42),
                 (hx + sd * r * .9, hy + r * .38)], GOLD, w=r * .05, amp=.4)
    dome = [(hx - r * 1.04, band)] + [(hx + math.cos(a) * r * 1.04, band + math.sin(a) * r * .8)
                                      for a in (math.pi + math.pi * k / 24 for k in range(1, 24))] + [(hx + r * 1.04, band)]
    p.shape(dome, GOLD, w=r * .08, amp=.7)
    p.shape(rrect(hx - r * 1.12, band - r * .02, hx + r * 1.12, band + r * .1, r * .04), GOLD_D, w=r * .05, amp=.4)

def _knight_helmet(p, hx, hy, r, look=0.0):
    band = hy - r * .25
    cone = [(hx - r * 1.03, band)] + spline([(hx - r * 1.03, band), (hx - r * .75, hy - r * 1.05), (hx, hy - r * 1.5)])[1:] + \
           spline([(hx, hy - r * 1.5), (hx + r * .75, hy - r * 1.05), (hx + r * 1.03, band)])[1:]
    p.shape(cone, STEEL, w=r * .08, amp=.6)
    p.stroke([(hx - r * .5, band - r * .5), (hx - r * .3, band - r * .85)], r * .06, WHITE, amp=.3)
    p.shape(rrect(hx - r * 1.05, band - r * .06, hx + r * 1.05, band + r * .1, r * .04), STEEL_D, w=r * .06, amp=.4)
    fx = hx + look * .16 * r
    p.shape([(fx - r * .06, band + r * .08), (fx + r * .06, band + r * .08), (fx + r * .05, hy + r * .22), (fx - r * .05, hy + r * .22)],
            STEEL_D, w=r * .045, amp=.3)

def _nemes(p, hx, hy, r, look=0.0):
    top = hy - r * .4
    for sd in (-1, 1):                                        # lappets hanging beside the face
        lap = [(hx + sd * r * .78, top), (hx + sd * r * 1.12, top + r * .1), (hx + sd * r * 1.05, hy + r * 1.15),
               (hx + sd * r * .7, hy + r * 1.15), (hx + sd * r * .72, hy + r * .35)]
        p.poly(p.wobble(lap, .5, True), YELLOW)
        p.hatch(lap, BLUE, gap=r * .16, ang=0, w=r * .06)
        p.stroke(lap, r * .06, amp=.5, closed=True)
    cap = [(hx - r * 1.12, top + r * .12)] + [(hx + math.cos(a) * r * 1.08, top + math.sin(a) * r * .75)
                                             for a in (math.pi + math.pi * k / 24 for k in range(1, 24))] + [(hx + r * 1.12, top + r * .12)]
    p.poly(p.wobble(cap, .5, True), YELLOW)
    p.hatch(cap, BLUE, gap=r * .16, ang=1.57, w=r * .06)
    p.stroke(cap, r * .07, amp=.6, closed=True)
    p.shape(rrect(hx - r * 1.0, top - r * .02, hx + r * 1.0, top + r * .12, r * .04), GOLD, w=r * .05, amp=.4)
    p.shape([(hx - r * .06, top - r * .02), (hx + r * .06, top - r * .02), (hx + r * .03, top - r * .22), (hx - r * .03, top - r * .22)],
            GOLD, w=r * .04, amp=.2)

def _laurel(p, hx, hy, r, look=0.0):
    cy = hy - r * .45
    for sd in (-1, 1):
        for k in range(6):
            a = math.pi * (1.5 + sd * (.18 + .1 * k))
            lx, ly = hx + math.cos(a) * r * 1.0, cy + math.sin(a) * r * .5 + r * .1
            p.shape(ellipse(lx, ly, r * .13, r * .06, rot=a + sd * 1.2, n=14), LEAF, w=r * .035, amp=.2)

def _beard(p, hx, hy, r, look=0.0, color=(206, 118, 50)):
    fx = hx + look * .1 * r
    chin = spline([(fx - r * .85, hy + r * .55), (fx - r * .45, hy + r * 1.3), (fx, hy + r * 1.45), (fx + r * .45, hy + r * 1.3),
                   (fx + r * .85, hy + r * .55)])
    inner = spline([(fx + r * .6, hy + r * .35), (fx + r * .3, hy + r * .75), (fx, hy + r * .8), (fx - r * .3, hy + r * .75),
                    (fx - r * .6, hy + r * .35)])
    shape = [(fx + r * .98, hy + r * .17)] + list(reversed(chin)) + [(fx - r * .98, hy + r * .17)] + list(reversed(inner))
    p.shape(shape, color, w=r * .06, amp=.6)
    for k in (-1, 0, 1):
        p.stroke([(fx + k * r * .3, hy + r * .9), (fx + k * r * .25, hy + r * 1.2)], r * .03, tuple(int(v * .7) for v in color), amp=.3)

HELMETS = {"viking": _viking_helmet, "roman": _roman_helmet, "knight": _knight_helmet, "nemes": _nemes, "laurel": _laurel,
           "penacho": lambda *a: _penacho(*a), "maya": lambda *a: _maya_headdress(*a)}

def helmet(img, cx, cy, r=80, kind="viking", seed=1):
    """Headgear on its own, as an object: viking, roman, knight, nemes (pharaoh), laurel, penacho (Aztec feather
    headdress) or maya. (cx, cy) = head center."""
    with Pen(img, (cx - r * 2.1, cy - r * 2.3, cx + r * 2.1, cy + r * 1.4), seed) as p:
        HELMETS[kind](p, cx, cy, r)

# ---------- public weapons ----------
def sword(img, gx, gy, L=300, ang=0.0, kind="long", seed=1):
    """Sword gripped at (gx, gy): kind 'long' (knight/viking) or 'gladius' (short, Roman)."""
    with Pen(img, (gx - L * 1.2, gy - L * 1.2, gx + L * 1.2, gy + L * 1.2), seed) as p: _sword(p, gx, gy, L, ang, kind)

def axe(img, gx, gy, L=280, ang=0.0, seed=1):
    """Viking axe gripped at (gx, gy)."""
    with Pen(img, (gx - L * 1.2, gy - L * 1.2, gx + L * 1.2, gy + L * 1.2), seed) as p: _axe(p, gx, gy, L, ang)

def spear(img, gx, gy, L=520, ang=0.0, seed=1):
    """Spear gripped at (gx, gy), L = total length."""
    with Pen(img, (gx - L * .7, gy - L * .7, gx + L * .7, gy + L * .7), seed) as p: _spear(p, gx, gy, L, ang)

def round_shield(img, cx, cy, r=110, color=CRIMSON, color2=CREAM, seed=1):
    """Viking round shield, painted in quarters, with an iron boss."""
    with Pen(img, (cx - r * 1.15, cy - r * 1.15, cx + r * 1.15, cy + r * 1.15), seed) as p: _round_shield(p, cx, cy, r, color, color2)

def scutum(img, cx, cy, h=280, color=CRIMSON, seed=1):
    """Roman legionary shield (tall rectangle with gold wings)."""
    with Pen(img, (cx - h * .45, cy - h * .6, cx + h * .45, cy + h * .6), seed) as p: _scutum(p, cx, cy, h, color)

def heater_shield(img, cx, cy, h=220, color=WHITE, cross=RED, seed=1):
    """Knight's shield with a cross."""
    with Pen(img, (cx - h * .55, cy - h * .6, cx + h * .55, cy + h * .6), seed) as p: _heater_shield(p, cx, cy, h, color, cross)

# ---------- costumes for doodle ----------
def _skirt(p, P, color, bottom=-180):
    p.shape([P(-52, -252), P(52, -252), P(60, bottom), P(-60, bottom)], color, w=6 * P.s)

def _belt(p, P, color=WOOD_D, buckle=GOLD, y=-258):
    p.limb([P(-52, y), P(52, y)], 10 * P.s, color, 3 * P.s)
    if buckle: p.shape(rrect(*P(-9, y - 8), *P(9, y + 8), 3), buckle, w=3 * P.s, amp=.3)

class _Place:
    def __init__(self, x, y, s): self.x, self.y, self.s = x, y, s
    def __call__(self, dx, dy): return (self.x + dx * self.s, self.y + dy * self.s)

def _costume(img, x, y, s, era, mood, arms, look, weapon, shield, ang, seed, color=None):
    P = _Place(x, y, s)
    torso = [P(-44, -418), P(44, -418), P(54, -330), P(50, -238), P(-50, -238), P(-54, -330)]

    def dress(p, a):
        if era == "roman":
            _skirt(p, P, color or CRIMSON)
            for k in range(-3, 4):
                p.shape(rrect(*P(k * 14 - 5, -255), *P(k * 14 + 5, -198), 2), WOOD, w=3 * s, amp=.3)
            p.shape(rrect(*P(-52, -408), *P(52, -262), 12 * s), STEEL, w=6 * s)
            for yy in (-378, -350, -322, -294): p.stroke([P(-50, yy), P(50, yy)], 4 * s, STEEL_D, amp=.5)
            _belt(p, P, WOOD_D, GOLD, -262)
        elif era == "viking":
            _skirt(p, P, color or TUNIC_GREEN, -175)
            p.stroke([P(-56, -195), P(56, -195)], 4 * s, GOLD_D, amp=.4)
            _belt(p, P)
        elif era == "pharaoh":
            p.shape([P(-50, -254), P(50, -254), P(60, -165), P(-60, -165)], WHITE, w=6 * s)
            panel = [P(-14, -250), P(14, -250), P(24, -168), P(-24, -168)]
            p.poly(p.wobble(panel, .4, True), GOLD); p.hatch(panel, BLUE, gap=14 * s, ang=0, w=3 * s); p.stroke(panel, 4 * s, amp=.4, closed=True)
            p.limb([P(-52, -256), P(52, -256)], 10 * s, GOLD, 3 * s)
        elif era == "greek":
            robe = [P(-50, -252), P(50, -252), P(66, -40), P(-66, -40)]
            p.shape(robe, WHITE, w=6 * s)
            for k in (-30, -8, 16, 38): p.stroke([P(k, -230), P(k * 1.25, -60)], 3 * s, GRAY_L, amp=.8)
            drape = [P(-48, -414), P(-22, -420), P(54, -296), P(56, -238), P(28, -240)]
            p.shape(drape, CREAM, w=5 * s, smooth=True)
            for k in (0, 1, 2): p.stroke([P(-30 + k * 12, -395 + k * 6), P(30 + k * 6, -270 + k * 4)], 3 * s, GOLD_D, amp=.6)
        elif era == "knight":
            p.hatch(torso, STEEL_D, gap=11 * s, ang=.8, w=2 * s); p.hatch(torso, STEEL_D, gap=11 * s, ang=-.8, w=2 * s)
            p.shape([P(-36, -410), P(36, -410), P(42, -252), P(50, -178), P(-50, -178), P(-42, -252)], WHITE, w=6 * s)
            p.poly([P(-7, -392), P(7, -392), P(7, -280), P(-7, -280)], RED)
            p.poly([P(-30, -356), P(30, -356), P(30, -342), P(-30, -342)], RED)
            _belt(p, P, WOOD_D, STEEL_D, -258)
        elif era == "aztec":
            p.hatch(torso, GRAY_L, gap=16 * s, ang=0, w=2.5 * s); p.hatch(torso, GRAY_L, gap=16 * s, ang=1.57, w=2.5 * s)
            p.stroke(torso, 7.5 * s, amp=.8, closed=True)
            p.shape([P(-50, -252), P(50, -252), P(56, -200), P(-56, -200)], WHITE, w=5 * s)
            p.shape([P(-16, -250), P(16, -250), P(20, -168), P(0, -158), P(-20, -168)], color or CRIMSON, w=4 * s)
            p.limb([P(-52, -254), P(52, -254)], 10 * s, color or CRIMSON, 3 * s)
        elif era == "maya":
            p.limb([P(-52, -256), P(52, -256)], 12 * s, color or JADE, 3 * s)
            flap = [P(-18, -250), P(18, -250), P(22, -150), P(-22, -150)]
            p.poly(p.wobble(flap, .4, True), CRIMSON); p.hatch(flap, GOLD, gap=18 * s, ang=0, w=4 * s); p.stroke(flap, 4 * s, amp=.4, closed=True)

    def hat(p, a):
        (hx, hy), r = a["head"], a["head_r"]
        if era == "viking":
            _beard(p, hx, hy, r, look); _viking_helmet(p, hx, hy, r, look)
        elif era == "roman": _roman_helmet(p, hx, hy, r, look)
        elif era == "knight": _knight_helmet(p, hx, hy, r, look)
        elif era == "pharaoh": _nemes(p, hx, hy, r, look)
        elif era == "greek": _laurel(p, hx, hy, r, look)
        elif era == "aztec": _penacho(p, hx, hy, r, look)
        elif era == "maya": _maya_headdress(p, hx, hy, r, look)

    def extras(p, a):
        if era == "roman":
            for sh in a["shoulders"]: p.shape(ellipse(sh[0], sh[1] + 6 * s, 30 * s, 20 * s, n=24), STEEL, w=5 * s, amp=.4)
        elif era == "viking":
            p.shape(bumpy([(*P(k * 20, -412 + abs(k) * 2), 22 * s) for k in range(-3, 4)]), FUR, w=5 * s, amp=.6)
        elif era == "pharaoh":
            cx_, cy_ = P(0, -418)
            ring = [(cx_ + math.cos(t) * 64 * s, cy_ + math.sin(t) * 44 * s) for t in (math.pi * k / 16 for k in range(17))] + \
                   [(cx_ + math.cos(t) * 26 * s, cy_ + math.sin(t) * 12 * s) for t in (math.pi * (16 - k) / 16 for k in range(17))]
            p.shape(ring, GOLD, w=5 * s, amp=.4)
            p.stroke([(cx_ + math.cos(t) * 46 * s, cy_ + math.sin(t) * 28 * s) for t in (math.pi * k / 16 for k in range(1, 16))],
                     7 * s, BLUE, amp=.3)
        elif era in ("aztec", "maya"):
            cx_, cy_ = P(0, -414)
            n = 9 if era == "aztec" else 11
            for k in range(n):                                    # jade bead necklace
                t = math.pi * (.1 + .8 * k / (n - 1))
                rr = (9 if era == "aztec" else 11) * s
                p.shape(ellipse(cx_ + math.cos(t) * 42 * s, cy_ + math.sin(t) * 30 * s, rr, rr, n=12), JADE, w=3 * s, amp=.2)
            if era == "maya":
                for sh, hd in zip(a["elbows"], (a["hand_l"], a["hand_r"])):
                    mx, my = (sh[0] * .3 + hd[0] * .7), (sh[1] * .3 + hd[1] * .7)
                    p.shape(ellipse(mx, my, 15 * s, 15 * s, n=14), JADE, w=3.5 * s, amp=.2)

    color_arms = {"roman": color or CRIMSON, "viking": color or TUNIC_GREEN, "pharaoh": WHITE, "greek": WHITE,
                  "knight": STEEL, "aztec": WHITE, "maya": WHITE}[era]
    a = doodle(img, x, y, s, outfit="tshirt", mood=mood, arms=arms, look=look, color=color_arms,
               dress=dress, hat=hat, extras=extras, seed=seed)
    gx, gy = a["hand_r"]
    if weapon:
        right = arms if isinstance(arms, str) else arms[1]
        if ang is None: ang = {"up": .15, "down": math.pi - .35}.get(right, .45)
        L = 300 * s
        with Pen(img, (gx - L * 1.2, gy - L * 1.2, gx + L * 1.2, gy + L * 1.2), seed) as p:
            if weapon in ("sword", "gladius"): _sword(p, gx, gy, L * (.75 if weapon == "gladius" else 1), ang, "gladius" if weapon == "gladius" else "long")
            elif weapon == "axe": _axe(p, gx, gy, L * .95, ang)
            elif weapon == "spear": _spear(p, gx, gy, L * 2, min(ang, .1))
            elif weapon == "scroll": _scroll(p, gx + 55 * s, gy - 10 * s, 150 * s, None)
            elif weapon == "torch": _torch(p, gx, gy, 200 * s, 0.0)
            elif weapon == "macuahuitl": _macuahuitl(p, gx, gy, L * .95, ang)
            elif weapon == "corn": _corn(p, gx + 20 * s, gy - 30 * s, 150 * s, .5)
            elif weapon == "cacao": _cacao(p, gx + 25 * s, gy - 20 * s, 120 * s, .4)
            p.shape(ellipse(gx, gy, 14 * s, 14 * s, n=20), WHITE, w=5 * s, amp=.6)
    if shield:
        sx, sy = a["hand_l"]
        r = 120 * s
        with Pen(img, (sx - r * 1.6, sy - r * 1.6, sx + r * 1.6, sy + r * 1.6), seed + 7) as p:
            if era == "roman": _scutum(p, sx, sy + 75 * s, 240 * s)
            elif era == "knight": _heater_shield(p, sx, sy + 55 * s, 210 * s)
            elif era in ("aztec", "maya"): _chimalli(p, sx, sy + 40 * s, 95 * s)
            else: _round_shield(p, sx, sy + 45 * s, 100 * s)
    return a

def roman(img, x, y, s=1.0, mood="angry", arms=("show", "up"), look=0.0, weapon="gladius", shield=True, ang=None,
          color=None, seed=1):
    """doodle as a Roman legionary: plumed helmet, segmented armor, red tunic; weapon gladius/sword/spear/None, scutum."""
    return _costume(img, x, y, s, "roman", mood, arms, look, weapon, shield, ang, seed, color)

def viking(img, x, y, s=1.0, mood="happy", arms=("show", "up"), look=0.0, weapon="axe", shield=True, ang=None,
           color=None, seed=1):
    """doodle as a viking: horned helmet, red beard, fur collar, tunic; weapon axe/sword/spear/None, round shield."""
    return _costume(img, x, y, s, "viking", mood, arms, look, weapon, shield, ang, seed, color)

def pharaoh(img, x, y, s=1.0, mood="smug", arms=("hip", "down"), look=0.0, weapon=None, ang=None, seed=1):
    """doodle as a pharaoh: striped nemes headdress, gold collar and kilt."""
    return _costume(img, x, y, s, "pharaoh", mood, arms, look, weapon, False, ang, seed)

def greek(img, x, y, s=1.0, mood="smile", arms=("down", "offer"), look=0.0, weapon="scroll", ang=None, seed=1):
    """doodle as an ancient Greek/Roman citizen: toga, laurel wreath; weapon scroll/torch/spear/None."""
    return _costume(img, x, y, s, "greek", mood, arms, look, weapon, False, ang, seed)

def knight(img, x, y, s=1.0, mood="angry", arms=("show", "up"), look=0.0, weapon="sword", shield=True, ang=None, seed=1):
    """doodle as a medieval knight: nasal helmet, chainmail, white surcoat with a red cross, sword and shield."""
    return _costume(img, x, y, s, "knight", mood, arms, look, weapon, shield, ang, seed)

def aztec(img, x, y, s=1.0, mood="angry", arms=("show", "up"), look=0.0, weapon="macuahuitl", shield=True, ang=None,
          color=None, seed=1):
    """doodle as an Aztec warrior: feather headdress, quilted cotton armor, jade necklace; weapon macuahuitl/spear/None,
    chimalli shield; color = loincloth and sash."""
    return _costume(img, x, y, s, "aztec", mood, arms, look, weapon, shield, ang, seed, color)

def maya(img, x, y, s=1.0, mood="smile", arms=("hip", "offer"), look=0.0, weapon="cacao", shield=False, ang=None,
         color=None, seed=1):
    """doodle as a Maya noble: tall headdress with quetzal plumes, jade collar and cuffs, patterned loincloth;
    weapon cacao/corn/spear/macuahuitl/None; color = sash."""
    return _costume(img, x, y, s, "maya", mood, arms, look, weapon, shield, ang, seed, color)

# ---------- small objects ----------
def _scroll(p, cx, cy, w, text):
    h = w * .62
    p.shape([(cx - w * .42, cy - h / 2), (cx + w * .42, cy - h / 2), (cx + w * .42, cy + h / 2), (cx - w * .42, cy + h / 2)], PARCH, w=max(3, w * .025))
    for sd in (-1, 1):
        p.shape(rrect(cx + sd * w * .42 - w * .06, cy - h * .58, cx + sd * w * .42 + w * .06, cy + h * .58, w * .05), CREAM, w=max(3, w * .025), amp=.4)
    if text: p.text(text, cx, cy, h * .22, warp=0)
    else:
        for k in range(4): p.stroke([(cx - w * .3, cy - h * .28 + k * h * .19), (cx + w * (.3 - .08 * (k % 2)), cy - h * .28 + k * h * .19)], max(2, w * .018), STEEL_D, amp=.4)

def scroll(img, cx, cy, w=240, text=None, seed=1):
    """Open parchment scroll with its two rolls; text = what's written on it (else squiggly lines)."""
    with Pen(img, (cx - w * .6, cy - w * .5, cx + w * .6, cy + w * .5), seed) as p: _scroll(p, cx, cy, w, text)

def _torch(p, gx, gy, h, t):
    p.limb([(gx, gy + h * .3), (gx, gy - h * .25)], h * .07, WOOD, max(2, h * .015))
    p.shape(rrect(gx - h * .07, gy - h * .32, gx + h * .07, gy - h * .2, 3), DARK, w=max(2, h * .015), amp=.3)
    fl = math.sin(t * 9) * h * .04
    outer = spline([(gx - h * .11, gy - h * .33), (gx - h * .14, gy - h * .5), (gx + fl, gy - h * .78), (gx + h * .14, gy - h * .5),
                    (gx + h * .11, gy - h * .33)])
    p.shape(outer, FLAME, w=max(3, h * .02), amp=.5)
    p.shape(spline([(gx - h * .05, gy - h * .34), (gx - h * .06, gy - h * .45), (gx + fl * .6, gy - h * .62), (gx + h * .06, gy - h * .45),
                    (gx + h * .05, gy - h * .34)]), FLAME_L, w=0)

def torch(img, gx, gy, h=220, t=0.0, seed=1):
    """Burning torch held at (gx, gy); pass t (seconds) to make the flame flicker."""
    with Pen(img, (gx - h * .3, gy - h * .85, gx + h * .3, gy + h * .4), seed) as p: _torch(p, gx, gy, h, t)

def amphora(img, cx, base, h=220, color=CLAY, seed=1, shadow=False):
    """Greek/Roman amphora (clay jar with two handles and a black band)."""
    w = h * .5
    with Pen(img, (cx - w, base - h * 1.05, cx + w, base + h * .06), seed) as p:
        if shadow: p.blob(cx, base, w * .5, h * .03, SHADE)
        for sd in (-1, 1):
            p.stroke(spline([(cx + sd * w * .14, base - h * .9), (cx + sd * w * .5, base - h * .92), (cx + sd * w * .45, base - h * .68)]), h * .035)
        body = spline([(cx - w * .12, base - h), (cx - w * .14, base - h * .82), (cx - w * .5, base - h * .55), (cx - w * .35, base - h * .18),
                       (cx - w * .14, base - h * .03)]) + \
               spline([(cx + w * .14, base - h * .03), (cx + w * .35, base - h * .18), (cx + w * .5, base - h * .55), (cx + w * .14, base - h * .82),
                       (cx + w * .12, base - h)])
        p.shape(body, color, w=max(4, h * .025))
        with p.clip(body):
            p.poly([(cx - w, base - h * .62), (cx + w, base - h * .62), (cx + w, base - h * .5), (cx - w, base - h * .5)], INK)
            for k in range(6):
                bx = cx - w * .4 + k * w * .16
                p.stroke([(bx, base - h * .47), (bx + w * .06, base - h * .4)], max(2, h * .012), INK, amp=.2)
        p.stroke(body, max(4, h * .025), amp=.6, closed=True)
        p.shape(rrect(cx - w * .2, base - h * 1.04, cx + w * .2, base - h * .98, 3), color, w=max(3, h * .02), amp=.3)
        p.shape(rrect(cx - w * .2, base - h * .05, cx + w * .2, base, 3), color, w=max(3, h * .02), amp=.3)

def crown(img, cx, cy, w=160, seed=1):
    """Gold crown with five points and gems; (cx, cy) = center of the band."""
    h = w * .5
    with Pen(img, (cx - w * .6, cy - h * 1.1, cx + w * .6, cy + h * .5), seed) as p:
        pts = [(cx - w / 2, cy + h * .3), (cx - w / 2, cy - h * .6)]
        for k in range(1, 9):
            pts.append((cx - w / 2 + w * k / 8, cy - (h * .1 if k % 2 else h * .6 + (h * .15 if k == 4 else 0))))
        pts.append((cx + w / 2, cy + h * .3))
        p.shape(pts, GOLD, w=max(3, w * .03))
        p.shape(rrect(cx - w / 2, cy, cx + w / 2, cy + h * .3, 3), GOLD_D, w=max(3, w * .025), amp=.3)
        for k, col in zip((-1, 0, 1), (BLUE, RED, BLUE)):
            p.shape(ellipse(cx + k * w * .28, cy + h * .15, w * .045, w * .045, n=12), col, w=max(2, w * .015), amp=.2)

def laurel_wreath(img, cx, cy, r=80, seed=1):
    """Laurel wreath (victory, emperors); (cx, cy) = center of the head it would crown."""
    with Pen(img, (cx - r * 1.4, cy - r * 1.4, cx + r * 1.4, cy + r * 1.4), seed) as p:
        for sd in (-1, 1):
            p.stroke([(cx + sd * r * math.cos(math.radians(d)), cy + r * math.sin(math.radians(d))) for d in range(-60, 91, 10)],
                     max(2, r * .04), (90, 120, 50), amp=.3)
            for k in range(8):
                a = math.radians(-55 + k * 19)
                lx, ly = cx + sd * r * math.cos(a), cy + r * math.sin(a)
                for o in (-1, 1):
                    p.shape(ellipse(lx + sd * o * r * .1 * math.sin(a), ly - o * r * .1 * math.cos(a), r * .14, r * .06,
                                    rot=sd * (a + math.pi / 2) + o * .5, n=14), LEAF, w=max(2, r * .03), amp=.2)

# ---------- monuments ----------
def pyramid(img, cx, base, w=440, seed=1, shadow=False):
    """Egyptian pyramid with a lit face, a shaded face and stone courses."""
    h = w * .62
    apex, ridge = (cx, base - h), (cx + w * .14, base)
    left = [(cx - w / 2, base), apex, ridge]
    right = [ridge, apex, (cx + w / 2, base)]
    with Pen(img, (cx - w * .6, base - h - 20, cx + w * .6, base + w * .06), seed) as p:
        if shadow: p.blob(cx + w * .1, base, w * .6, w * .04, SHADE)
        p.poly(p.wobble(left, .6, True), SAND); p.poly(p.wobble(right, .6, True), SAND_D)
        for face, col in ((left, SAND_D), (right, STONE_D)):
            with p.clip(face):
                n = 9
                for k in range(1, n):
                    yy = base - h * k / n
                    p.stroke([(cx - w / 2, yy), (cx + w / 2, yy)], 2.5, col, amp=.5)
                    for j in range(-6, 7):
                        xx = cx + (j + (k % 2) * .5) * w / 12
                        p.stroke([(xx, yy), (xx, yy + h / n)], 2, col, amp=.2)
        p.hatch(right, STONE_D, gap=18, ang=-.5, w=2.5)
        p.stroke(left, 6, amp=1, closed=True); p.stroke(right, 6, amp=1, closed=True)

def obelisk(img, cx, base, h=420, seed=1, shadow=False):
    """Egyptian obelisk with a few carved signs."""
    w = h * .14
    with Pen(img, (cx - w * 1.5, base - h - 20, cx + w * 1.5, base + 20), seed) as p:
        if shadow: p.blob(cx, base, w * 1.2, w * .2, SHADE)
        p.shape([(cx - w / 2, base), (cx - w * .36, base - h * .88), (cx + w * .36, base - h * .88), (cx + w / 2, base)], SAND, w=6)
        p.shape([(cx - w * .36, base - h * .88), (cx, base - h), (cx + w * .36, base - h * .88)], GOLD, w=5)
        for k in range(5):
            yy = base - h * (.75 - k * .13)
            p.stroke([(cx - w * .15, yy), (cx + w * .15, yy)], 3, SAND_D, amp=.3)
            p.shape(ellipse(cx, yy + h * .045, w * .1, w * .1, n=12), None, w=3, color=SAND_D, amp=.2)

def _column(p, cx, base, h, w, broken=False):
    p.shape(rrect(cx - w * .75, base - h * .06, cx + w * .75, base, 3), MARBLE, w=5)
    top = base - h * (.78 if broken else .9)
    shaft = [(cx - w / 2, base - h * .06), (cx - w * .44, top), (cx + w * .44, top), (cx + w / 2, base - h * .06)]
    if broken:
        shaft = shaft[:1] + [(cx - w * .44, top), (cx - w * .15, top - h * .06), (cx, top + h * .02), (cx + w * .2, top - h * .08),
                             (cx + w * .44, top - h * .03)] + shaft[3:]
    p.shape(shaft, MARBLE, w=5)
    for k in (-1, 0, 1):
        p.stroke([(cx + k * w * .22, base - h * .08), (cx + k * w * .2, top + h * .03)], 3, MARBLE_D, amp=.4)
    if not broken:
        p.shape(rrect(cx - w * .65, top - h * .03, cx + w * .65, top + h * .01, 3), MARBLE, w=5, amp=.4)
        p.shape(rrect(cx - w * .8, top - h * .1, cx + w * .8, top - h * .03, 3), MARBLE, w=5, amp=.4)

def column(img, cx, base, h=420, broken=False, seed=1, shadow=False):
    """Greek column (marble, fluted); broken = ruin with a cracked top."""
    w = h * .16
    with Pen(img, (cx - w, base - h - 20, cx + w, base + 15), seed) as p:
        if shadow: p.blob(cx, base, w * .9, w * .15, SHADE)
        _column(p, cx, base, h, w, broken)

def temple(img, cx, base, w=520, seed=1, shadow=False):
    """Greek temple: steps, six columns and a triangular pediment."""
    h = w * .72
    with Pen(img, (cx - w * .6, base - h - 20, cx + w * .6, base + 20), seed) as p:
        if shadow: p.blob(cx, base, w * .58, w * .04, SHADE)
        for k in range(3):
            p.shape(rrect(cx - w * (.5 - k * .03), base - h * .04 * (k + 1), cx + w * (.5 - k * .03), base - h * .04 * k, 2), MARBLE, w=5, amp=.4)
        col_base, col_h = base - h * .12, h * .6
        for k in range(6):
            _column(p, cx - w * .38 + k * w * .152, col_base, col_h, w * .065)
        top = col_base - col_h * .97
        p.shape(rrect(cx - w * .47, top - h * .08, cx + w * .47, top + 2, 2), MARBLE, w=5)
        ped = [(cx - w * .5, top - h * .08), (cx, top - h * .27), (cx + w * .5, top - h * .08)]
        p.shape(ped, MARBLE, w=6)
        p.stroke([(cx - w * .38, top - h * .1), (cx, top - h * .23), (cx + w * .38, top - h * .1)], 3, MARBLE_D, amp=.4)

def colosseum(img, cx, base, w=560, seed=1, shadow=False):
    """Roman Colosseum seen from the front: three tiers of arches, the right end in ruins."""
    h = w * .52
    x0, x1 = cx - w / 2, cx + w / 2
    body = [(x0, base), (x0, base - h), (cx + w * .1, base - h), (cx + w * .18, base - h * .86), (cx + w * .3, base - h * .8),
            (cx + w * .36, base - h * .6), (x1, base - h * .52), (x1, base)]
    with Pen(img, (x0 - 20, base - h - 20, x1 + 20, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .035, SHADE)
        p.poly(p.wobble(body, .6, True), STONE)
        with p.clip(body):
            tiers = 3
            for t in range(tiers):
                yb, yt = base - h * t / tiers, base - h * (t + 1) / tiers
                p.stroke([(x0, yt), (x1, yt)], 5, amp=.6)
                n = 8
                for k in range(n):
                    ax = x0 + w * (k + .5) / n
                    aw, ah = w / n * .3, (yb - yt) * .62
                    arch = [(ax - aw, yb - (yb - yt) * .12)] + \
                           [(ax + math.cos(a) * aw, yb - (yb - yt) * .12 - ah + math.sin(a) * aw) for a in (math.pi + math.pi * j / 10 for j in range(11))] + \
                           [(ax + aw, yb - (yb - yt) * .12)]
                    p.shape(arch, STONE_D, w=3.5, amp=.4)
            p.hatch([(cx + w * .1, base - h), (x1, base - h), (x1, base)], STONE_D, gap=20, ang=-.4, w=2)
        p.stroke(body, 6, amp=1, closed=True)

def castle(img, cx, base, w=440, flag=RED, seed=1, shadow=False):
    """Stone castle: wall with battlements, two towers with pointed roofs, gate and a flag."""
    h = w * .45
    tw_, th = w * .2, h * 1.45
    with Pen(img, (cx - w * .6, base - th - w * .4, cx + w * .6, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .58, w * .04, SHADE)
        wall_top, xa, xb, m = base - h, cx - w * .4, cx + w * .4, 11
        pts = [(xa, base)]
        for k in range(m):
            yk = wall_top - (h * .12 if k % 2 == 0 else 0)
            pts += [(xa + (xb - xa) * k / m, yk), (xa + (xb - xa) * (k + 1) / m, yk)]
        pts.append((xb, base))
        p.shape(pts, STONE, w=6, amp=.6)
        gate = [(cx - w * .08, base)] + [(cx + math.cos(a) * w * .08, base - h * .45 + math.sin(a) * w * .08) for a in (math.pi + math.pi * j / 10 for j in range(11))] + [(cx + w * .08, base)]
        p.shape(gate, WOOD_D, w=5)
        for k in range(-2, 3): p.stroke([(cx + k * w * .03, base - h * .5), (cx + k * w * .03, base)], 3, DARK, amp=.2)
        for sd in (-1, 1):
            tx = cx + sd * w * .4
            tower = [(tx - tw_ / 2, base), (tx - tw_ / 2, base - th), (tx + tw_ / 2, base - th), (tx + tw_ / 2, base)]
            p.shape(tower, STONE, w=6)
            p.shape([(tx - tw_ * .6, base - th), (tx, base - th - tw_ * 1.1), (tx + tw_ * .6, base - th)], RED, w=6)
            p.shape(rrect(tx - tw_ * .07, base - th * .7, tx + tw_ * .07, base - th * .5, 3), DARK, w=3, amp=.3)
            for k in range(3): p.stroke([(tx - tw_ / 2 + 6, base - th * (.2 + .25 * k)), (tx - tw_ * .1, base - th * (.2 + .25 * k))], 2.5, STONE_D, amp=.3)
        fx, fy = cx + w * .4, base - th - tw_ * 1.1
        p.stroke([(fx, fy), (fx, fy - w * .16)], 4, amp=.3)
        p.shape([(fx, fy - w * .16), (fx + w * .12, fy - w * .13), (fx, fy - w * .1)], flag, w=4, amp=.4)

def longship(img, cx, base, w=560, sail=RED, seed=1):
    """Viking longship on the water: dragon prow, shields along the side, striped square sail. base = waterline."""
    h = w * .16
    x0, x1 = cx - w / 2, cx + w / 2
    with Pen(img, (x0 - w * .08, base - w * .85, x1 + w * .08, base + h * .7), seed) as p:
        p.stroke([(cx, base - h * .5), (cx, base - w * .78)], 9, WOOD_D, amp=.4)
        sx0, sx1, sy0, sy1 = cx - w * .22, cx + w * .22, base - w * .72, base - h * 1.4
        sail_pts = [(sx0, sy0), (sx1, sy0), (sx1 + w * .02, sy1), (sx0 - w * .02, sy1)]
        p.poly(p.wobble(sail_pts, .6, True), WHITE)
        with p.clip(sail_pts):
            for k in range(-3, 4, 2):
                p.poly([(cx + k * w * .055, sy0), (cx + (k + 1) * w * .055, sy0), (cx + (k + 1) * w * .06, sy1), (cx + k * w * .06, sy1)], sail)
        p.stroke(sail_pts, 6, amp=.8, closed=True)
        p.stroke([(sx0 - w * .03, sy0), (sx1 + w * .03, sy0)], 8, WOOD_D, amp=.3)
        hull = spline([(x0 + w * .02, base - h * 1.6), (x0 + w * .12, base - h * .2), (cx, base + h * .5), (x1 - w * .12, base - h * .2),
                       (x1 - w * .02, base - h * 1.6)]) + [(x1 - w * .1, base - h * 1.05), (x0 + w * .1, base - h * 1.05)]
        p.shape(hull, WOOD, w=6)
        with p.clip(hull):
            for k in (1, 2): p.stroke(spline([(x0, base - h * (1.05 - .35 * k)), (cx, base - h * (.6 - .35 * k) + h * .3), (x1, base - h * (1.05 - .35 * k))]), 3, WOOD_D, amp=.5)
        for k in range(7):
            sxk = cx - w * .3 + k * w * .1
            _round_shield(p, sxk, base - h * 1.05, h * .3, (CRIMSON, BLUE, GOLD)[k % 3], CREAM)
        head = spline([(x1 - w * .02, base - h * 1.6), (x1 + w * .02, base - h * 2.6), (x1 - w * .04, base - h * 3.1), (x1 - w * .09, base - h * 2.75)])
        p.stroke(head, w * .035, WOOD, amp=.4); p.stroke(head, 4, WOOD_D, amp=.4)
        p.poly(ellipse(x1 - w * .035, base - h * 2.9, 4, 4, n=8), INK)
        tail = spline([(x0 + w * .02, base - h * 1.6), (x0 - w * .02, base - h * 2.4), (x0 + w * .03, base - h * 2.7), (x0 + w * .05, base - h * 2.4)])
        p.stroke(tail, w * .03, WOOD, amp=.4)
        for k in range(5):
            wx = x0 + w * .05 + k * w * .22
            p.stroke(spline([(wx, base + h * .55), (wx + w * .05, base + h * .4), (wx + w * .1, base + h * .55)]), 4, BLUE, amp=.3)

# ---------- Mexico: Aztecs, Maya, Olmecs ----------
def _feather(p, x, y, ang, L, wd, color):
    dx, dy = math.sin(ang), -math.cos(ang)
    cx, cy = x + dx * L / 2, y + dy * L / 2
    p.shape(ellipse(cx, cy, wd, L / 2, rot=ang, n=24), color, w=max(2, wd * .25), amp=.4)
    p.stroke([(x + dx * L * .1, y + dy * L * .1), (x + dx * L * .92, y + dy * L * .92)], max(1.5, wd * .15),
             tuple(int(v * .6) for v in color), amp=.2)

def _penacho(p, hx, hy, r, look=0.0):
    """Aztec feather headdress: a wide fan of long plumes over a gold band with jade studs."""
    n = 13
    for k in range(n):
        a = -1.25 + 2.5 * k / (n - 1)
        bx, by = hx + math.sin(a) * r * .75, hy - r * .35 - math.cos(a) * r * .55
        _feather(p, bx, by, a, r * (.95 if k % 2 else 1.1), r * .13, FEATHERS[k % 4])
    p.shape(rrect(hx - r * .98, hy - r * .58, hx + r * .98, hy - r * .36, r * .06), GOLD, w=r * .06, amp=.4)
    for k in (-2, -1, 0, 1, 2):
        p.shape(ellipse(hx + k * r * .36, hy - r * .47, r * .07, r * .07, n=12), JADE, w=r * .03, amp=.2)

def _maya_headdress(p, hx, hy, r, look=0.0):
    """Maya headdress: tall jade-and-gold crown topped with long green quetzal plumes."""
    for k in range(7):
        a = -.55 + 1.1 * k / 6
        _feather(p, hx + math.sin(a) * r * .3, hy - r * 1.15, a * 1.2, r * (.8 if k % 2 else .95), r * .11,
                 QUETZAL if k % 3 else TURQ)
    crown = [(hx - r * .95, hy - r * .4), (hx - r * .7, hy - r * 1.2), (hx + r * .7, hy - r * 1.2), (hx + r * .95, hy - r * .4)]
    p.poly(p.wobble(crown, .5, True), JADE)
    p.hatch(crown, JADE_D, gap=r * .2, ang=0, w=r * .04)
    p.stroke(crown, r * .07, amp=.6, closed=True)
    p.shape(ellipse(hx, hy - r * .8, r * .2, r * .2, n=20), GOLD, w=r * .05, amp=.3)
    p.shape(ellipse(hx, hy - r * .8, r * .08, r * .08, n=12), CRIMSON, w=r * .03, amp=.2)
    p.shape(rrect(hx - r * 1.0, hy - r * .5, hx + r * 1.0, hy - r * .34, r * .05), GOLD, w=r * .06, amp=.4)

def _macuahuitl(p, gx, gy, L, ang):
    dx, dy = _dir(ang); nx, ny = -dy, dx
    at = lambda t, o=0: (gx + dx * L * t + nx * o, gy + dy * L * t + ny * o)
    p.limb([at(-.15), at(.15)], L * .05, WOOD_D, max(2, L * .01))
    paddle = [at(.12, -L * .055), at(.95, -L * .065), at(1.0), at(.95, L * .065), at(.12, L * .055)]
    p.shape(paddle, WOOD, w=max(3, L * .014), amp=.4)
    for k in range(7):
        t = .22 + k * .11
        for sd in (-1, 1):
            p.shape([at(t - .035, sd * L * .055), at(t, sd * L * .1), at(t + .035, sd * L * .057)], DARK, w=max(2, L * .006), amp=.2)

def _chimalli(p, cx, cy, r, color=TURQ):
    for k in range(9):                                        # feather fringe hanging below
        a = math.pi * (.2 + .6 * k / 8)
        _feather(p, cx + math.cos(a) * r * .8, cy + math.sin(a) * r * .8, math.pi - (a - math.pi / 2) * .7, r * .8, r * .11,
                 FEATHERS[k % 4])
    p.shape(ellipse(cx, cy, r, r, n=56), color, w=max(4, r * .07), amp=.7)
    pts = ellipse(cx, cy, r * .97, r * .97, n=56)
    with p.clip(pts):                                         # step-fret band
        p.poly([(cx - r, cy - r * .18), (cx + r, cy - r * .18), (cx + r, cy + r * .18), (cx - r, cy + r * .18)], WHITE)
        u, fret = r * .12, []
        for k in range(-9, 9):
            x = cx + k * 2 * u
            fret += [(x, cy + r * .1), (x, cy - r * .1), (x + u, cy - r * .1), (x + u, cy + r * .1)]
        p.stroke(fret, max(3, r * .05), CRIMSON, amp=.2, taper=False)
        for yy in (-.18, .18): p.stroke([(cx - r, cy + yy * r), (cx + r, cy + yy * r)], max(2, r * .03), amp=.2)
    p.stroke(ellipse(cx, cy, r * .97, r * .97, n=56), max(3, r * .05), GOLD, amp=.4, closed=True)
    p.stroke(ellipse(cx, cy, r, r, n=56), max(4, r * .07), amp=.7, closed=True)

def _corn(p, cx, cy, h, ang=0.0):
    w = h * .32
    R_ = lambda pts: rotated(pts, cx, cy, ang)
    for sd in (-1, 1):
        p.shape(R_([(cx, cy + h * .45), (cx + sd * w * .9, cy + h * .1), (cx + sd * w * .7, cy - h * .2), (cx + sd * w * .25, cy + h * .2)]),
                LEAF, w=max(3, h * .02), smooth=True, amp=.4)
    cob = R_(spline([(cx, cy - h * .5), (cx + w * .5, cy - h * .2), (cx + w * .45, cy + h * .3), (cx, cy + h * .38), (cx - w * .45, cy + h * .3),
                     (cx - w * .5, cy - h * .2)], closed=True))
    p.poly(p.wobble(cob, .4, True), CORN)
    with p.clip(cob):
        for k in range(-3, 4): p.stroke(R_([(cx + k * w * .14, cy - h * .5), (cx + k * w * .14, cy + h * .4)]), max(2, h * .01), CORN_D, amp=.2)
        for k in range(12): p.stroke(R_([(cx - w, cy - h * .45 + k * h * .075), (cx + w, cy - h * .45 + k * h * .075)]), max(2, h * .01), CORN_D, amp=.2)
    p.stroke(cob, max(3, h * .02), amp=.5, closed=True)
    p.shape(R_([(cx, cy + h * .52), (cx - w * .3, cy + h * .2), (cx, cy + h * .3), (cx + w * .3, cy + h * .2)]), LEAF, w=max(3, h * .02), amp=.3)

def _cacao(p, cx, cy, h, ang=0.0):
    w = h * .5
    R_ = lambda pts: rotated(pts, cx, cy, ang)
    pod = R_(spline([(cx, cy - h * .5), (cx + w * .5, cy - h * .15), (cx + w * .45, cy + h * .25), (cx, cy + h * .5), (cx - w * .45, cy + h * .25),
                     (cx - w * .5, cy - h * .15)], closed=True))
    p.shape(pod, CACAO, w=max(3, h * .025), amp=.5)
    for k in (-.25, 0, .25):
        p.stroke(R_(spline([(cx + k * w * .6, cy - h * .45), (cx + k * w * 1.6, cy), (cx + k * w * .6, cy + h * .45)])), max(2, h * .015), CACAO_D, amp=.3)
    p.stroke(R_([(cx, cy - h * .5), (cx + h * .04, cy - h * .62)]), max(3, h * .03), WOOD_D, amp=.2)

def macuahuitl(img, gx, gy, L=300, ang=0.0, seed=1):
    """Aztec wooden sword edged with obsidian blades, gripped at (gx, gy)."""
    with Pen(img, (gx - L * 1.2, gy - L * 1.2, gx + L * 1.2, gy + L * 1.2), seed) as p: _macuahuitl(p, gx, gy, L, ang)

def chimalli(img, cx, cy, r=100, color=TURQ, seed=1):
    """Aztec round shield with a step-fret band and a fringe of feathers."""
    with Pen(img, (cx - r * 1.3, cy - r * 1.2, cx + r * 1.3, cy + r * 1.6), seed) as p: _chimalli(p, cx, cy, r, color)

def corn(img, cx, cy, h=180, ang=0.0, seed=1):
    """Ear of maize with its husk; ang = tilt in radians."""
    with Pen(img, (cx - h * .7, cy - h * .7, cx + h * .7, cy + h * .7), seed) as p: _corn(p, cx, cy, h, ang)

def cacao_pod(img, cx, cy, h=150, ang=0.0, seed=1):
    """Cacao pod (chocolate fruit); ang = tilt in radians."""
    with Pen(img, (cx - h * .7, cy - h * .7, cx + h * .7, cy + h * .7), seed) as p: _cacao(p, cx, cy, h, ang)

def step_pyramid(img, cx, base, w=480, tiers=5, color=MESO, seed=1, shadow=False):
    """Mesoamerican stepped pyramid (Chichén Itzá, Teotihuacan) with a central stairway and a temple on top."""
    h = w * .62
    th = h * .8 / tiers
    dark = tuple(int(v * .78) for v in color)
    with Pen(img, (cx - w * .6, base - h - 20, cx + w * .6, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .58, w * .04, SHADE)
        for k in range(tiers):
            hw0, hw1 = w / 2 * (1 - .75 * k / tiers), w / 2 * (1 - .75 * (k + 1) / tiers) + w * .02
            y0, y1 = base - k * th, base - (k + 1) * th
            tier = [(cx - hw0, y0), (cx - hw1, y1), (cx + hw1, y1), (cx + hw0, y0)]
            p.shape(tier, color, w=5, amp=.6)
            p.stroke([(cx - hw0 * .97, y0 - th * .45), (cx + hw0 * .97, y0 - th * .45)], 2.5, dark, amp=.3)
        top = base - tiers * th
        sw0, sw1 = w * .12, w * .07
        stair = [(cx - sw0, base), (cx - sw1, top), (cx + sw1, top), (cx + sw0, base)]
        p.poly(p.wobble(stair, .4, True), dark)
        n = tiers * 5
        for k in range(1, n):
            yy = base - (base - top) * k / n
            hw = sw0 + (sw1 - sw0) * k / n
            p.stroke([(cx - hw, yy), (cx + hw, yy)], 2.5, INK, amp=.2)
        p.stroke(stair, 5, amp=.5, closed=True)
        tw_, tt = w * .2, h * .2
        p.shape([(cx - tw_ / 2, top), (cx - tw_ / 2, top - tt), (cx + tw_ / 2, top - tt), (cx + tw_ / 2, top)], color, w=5)
        p.shape(rrect(cx - tw_ * .17, top - tt * .62, cx + tw_ * .17, top, 3), DARK, w=4, amp=.3)
        p.shape(rrect(cx - tw_ * .58, top - tt * 1.18, cx + tw_ * .58, top - tt * .95, 3), dark, w=5, amp=.4)

def sun_stone(img, cx, cy, r=170, seed=1):
    """Aztec Sun Stone (calendar stone): central face, ring of day signs and sun rays."""
    with Pen(img, (cx - r * 1.1, cy - r * 1.1, cx + r * 1.1, cy + r * 1.1), seed) as p:
        p.shape(ellipse(cx, cy, r, r, n=72), MESO, w=max(4, r * .04), amp=.8)
        p.stroke(ellipse(cx, cy, r * .86, r * .86, n=72), max(3, r * .02), MESO_D, amp=.5, closed=True)
        for k in range(20):                                   # day signs
            a = 2 * math.pi * k / 20
            bx, by = cx + math.cos(a) * r * .74, cy + math.sin(a) * r * .74
            p.shape(rotated(rrect(bx - r * .07, by - r * .07, bx + r * .07, by + r * .07, 3), bx, by, a), MESO, w=max(2, r * .015), amp=.2)
            p.poly(ellipse(bx, by, r * .025, r * .025, n=8), MESO_D)
        p.stroke(ellipse(cx, cy, r * .62, r * .62, n=64), max(3, r * .02), MESO_D, amp=.5, closed=True)
        for k in range(8):                                    # rays
            a = 2 * math.pi * k / 8 + math.pi / 8
            tip = (cx + math.cos(a) * r * .6, cy + math.sin(a) * r * .6)
            l_ = (cx + math.cos(a - .2) * r * .36, cy + math.sin(a - .2) * r * .36)
            r_ = (cx + math.cos(a + .2) * r * .36, cy + math.sin(a + .2) * r * .36)
            p.shape([l_, tip, r_], MESO, w=max(2, r * .015), amp=.2)
        p.shape(ellipse(cx, cy, r * .34, r * .34, n=48), MESO, w=max(3, r * .02), amp=.4)
        for sd in (-1, 1):                                    # the face in the middle
            p.shape(ellipse(cx + sd * r * .12, cy - r * .07, r * .06, r * .04, n=12), WHITE, w=max(2, r * .015), amp=.2)
            p.poly(ellipse(cx + sd * r * .12, cy - r * .07, r * .025, r * .025, n=8), INK)
        p.stroke([(cx, cy - r * .02), (cx - r * .03, cy + r * .06), (cx + r * .03, cy + r * .06)], max(2, r * .015), amp=.2)
        p.shape([(cx - r * .05, cy + r * .12), (cx + r * .05, cy + r * .12), (cx + r * .03, cy + r * .26), (cx, cy + r * .3),
                 (cx - r * .03, cy + r * .26)], CRIMSON, w=max(2, r * .015), amp=.2)

def olmec_head(img, cx, base, h=280, seed=1, shadow=False):
    """Colossal Olmec stone head: helmet, wide nose and full lips."""
    w = h * .85
    with Pen(img, (cx - w * .7, base - h - 10, cx + w * .7, base + h * .06), seed) as p:
        if shadow: p.blob(cx, base, w * .6, h * .04, SHADE)
        face = rrect(cx - w / 2, base - h, cx + w / 2, base, w * .32)
        p.shape(face, MESO, w=6)
        with p.clip(face):
            p.poly([(cx - w, base - h), (cx + w, base - h), (cx + w, base - h * .7), (cx - w, base - h * .7)], MESO_D)
            for k in range(-4, 5): p.stroke([(cx + k * w * .11, base - h), (cx + k * w * .11, base - h * .72)], 2.5, MESO, amp=.3)
        p.stroke([(cx - w / 2, base - h * .7), (cx + w / 2, base - h * .7)], 5, amp=.5)
        p.stroke(face, 6, amp=.8, closed=True)
        for sd in (-1, 1):
            p.shape(ellipse(cx + sd * w * .2, base - h * .55, w * .11, h * .045, n=20), MESO_D, w=4, amp=.3)
            p.shape(ellipse(cx + sd * w * .52, base - h * .45, w * .07, h * .12, n=18), MESO, w=4, amp=.3)
            p.stroke(spline([(cx + sd * w * .32, base - h * .64), (cx + sd * w * .2, base - h * .66), (cx + sd * w * .08, base - h * .63)]), 4, amp=.3)
        p.shape(spline([(cx - w * .14, base - h * .32), (cx - w * .06, base - h * .52), (cx + w * .06, base - h * .52), (cx + w * .14, base - h * .32),
                        (cx, base - h * .3)], closed=True), MESO, w=4, amp=.3)
        p.shape(spline([(cx - w * .2, base - h * .2), (cx, base - h * .25), (cx + w * .2, base - h * .2), (cx, base - h * .12)], closed=True),
                MESO_D, w=4, amp=.3)

def stela(img, cx, base, h=380, seed=1, shadow=False):
    """Maya stela: tall carved stone with a column of glyph blocks."""
    w = h * .42
    with Pen(img, (cx - w * .7, base - h - 10, cx + w * .7, base + h * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .7, h * .03, SHADE)
        slab = [(cx - w / 2, base)] + [(cx + math.cos(a) * w / 2, base - h + w / 2 + math.sin(a) * w / 2) for a in
                                       (math.pi + math.pi * k / 16 for k in range(17))] + [(cx + w / 2, base)]
        p.shape(slab, MESO, w=6)
        for r_ in range(5):
            for c in (-1, 1):
                gx, gy = cx + c * w * .2, base - h + w * .55 + r_ * h * .15
                p.shape(rrect(gx - w * .17, gy - h * .06, gx + w * .17, gy + h * .06, w * .06), MESO, w=3, amp=.3)
                p.shape(ellipse(gx - w * .05, gy - h * .015, w * .045, w * .045, n=10), None, w=2.5, color=MESO_D, amp=.2)
                p.stroke([(gx - w * .1, gy + h * .03), (gx + w * .1, gy + h * .03)], 2.5, MESO_D, amp=.2)
                p.stroke([(gx + w * .05, gy - h * .04), (gx + w * .08, gy + h * .01)], 2.5, MESO_D, amp=.2)

from . import cache_pieces
cache_pieces(globals())
