"""Sketch-style survival and shelters: zombies (one or a whole horde), the doodle as a survivor with a backpack;
ground cut in layers, a partly buried bunker in cross-section, a temporary shelter built in stages, perimeter fence,
floodlight, security camera, heavy door and hatch, log cabin, pine tree, rocks and hills; utilities (solar panel,
battery bank, battery, generator, electrical panel, cable, water tank, water filter, rain, bottle, jerrycan, tap,
vent fan, duct, vent pipe, air flow arrows, air monitor); supplies (backpack, canned food, crate, pantry shelf,
first aid kit, flashlight, camp bed, trash bin and pile, flies, garden bed); and plans (paper map, plan sheet,
floor plan with zones, site plan seen from above). All take the image (img) and a 'seed'. Nothing draws a floor
shadow unless shadow=True.

    bunker_section(img, 540, 900, 900, buried=.7)
    a = zombie(img, 300, FLOOR, .8, look=1, t=c.t)
    fence(img, 60, 1020, FLOOR, 230, kind="metal")

Things on the floor take (cx, base) = bottom center; floating things take their center (cx, cy). Hand-held things
take the grip point and 'ang' = tilt from straight up, in radians."""
import math
import random
from PIL import ImageFont
from . import Pen, INK, WHITE, RED, RED_D, GREEN, GREEN_D, GREEN_L, GLASS, GLASS_D, WOOD, WOOD_D, BLUE, FONT, \
    ellipse, rrect, rotated, spline
from .everyday import YELLOW, GOLD, GRAY, GRAY_L, DARK, LEAF, LEAF_D, bumpy
from .work import STEEL, STEEL_D, ORANGE, ORANGE_D, KHAKI, CREAM, BEIGE, BEIGE_D, DENIM, _shovel
from .humans import doodle

ZOMBIE, ZOMBIE_D = (172, 196, 150), (128, 152, 108)
RAGS = ((150, 140, 118), (112, 124, 150), (160, 104, 96), (120, 140, 110), (196, 190, 176))
STAIN = (128, 44, 40)
NIGHT = (92, 96, 108)
SOIL, SOIL_D = (168, 124, 84), (122, 86, 54)
TOPSOIL = (110, 78, 50)
ROCK, ROCK_D = (168, 168, 166), (118, 118, 118)
CONCRETE, CONCRETE_D = (206, 204, 198), (150, 148, 142)
ROOM = (250, 244, 226)
WATER, WATER_D = (150, 200, 236), (80, 140, 200)
GRAVEL = (190, 182, 160)
TAR = (40, 44, 58)
OLIVE, OLIVE_D = (122, 132, 74), (84, 92, 48)
LIGHT = (255, 238, 150, 120)
TIN, TIN_D = (214, 216, 222), (156, 160, 170)
PANEL, PANEL_D = (54, 84, 150), (30, 50, 100)
PAPER, PAPER_D = (252, 248, 234), (226, 218, 196)
PINE, PINE_D = (70, 140, 80), (40, 96, 54)
SPROUT = (120, 200, 90)

def _dir(ang):
    return math.sin(ang), -math.cos(ang)

def _shade(c, k=.7):
    return tuple(int(v * k) for v in c[:3])

def _ltext(p, s, x, cy, size, fill=INK, warp=0):
    """Text that starts at x (Pen.text centers it)."""
    w = ImageFont.truetype(FONT, max(8, int(size))).getlength(s)
    p.text(s, x + w / 2, cy, size, fill=fill, warp=warp)

def _fit(s, size, maxw):
    """Font size so that s fits in maxw px."""
    while size > 8 and ImageFont.truetype(FONT, int(size)).getlength(s) > maxw: size *= .92
    return size

# ---------- characters ----------
def zombie_anchors(x, y, s=1.0, look=1.0):
    """Body points of zombie (head, mouth, hands…) to place bubbles and objects on it."""
    d = 1 if look >= 0 else -1
    hx, hy, r = x + d * 58 * s, y - 478 * s, 86 * s
    return {"head": (hx, hy), "head_r": r, "mouth": (hx + d * .22 * r, hy + .45 * r), "chest": (x + d * 14 * s, y - 350 * s),
            "hand_l": (x + d * 196 * s, y - 318 * s), "hand_r": (x + d * 182 * s, y - 270 * s), "feet": (x, y),
            "box": (x - 280 * s, y - 760 * s, x + 300 * s, y + 20 * s)}

def zombie(img, x, y, s=1.0, look=1.0, color=None, mood="hungry", stains=True, silhouette=False, t=0.0, shadow=False, seed=1):
    """Hunched, shambling zombie in the doodle's proportions: grey-green skin, sunken glowing eyes, gaping jaw with
    jagged teeth, torn clothes and both arms reaching, limp hands, towards 'look' (1 right, -1 left). mood: hungry (jaw
    wide open), groan (half open) or blank (shut). t makes it sway and drag its feet. silhouette=True draws a flat
    dark figure with only the eyes glowing (far away, at night). Returns the body points."""
    d = 1 if look >= 0 else -1
    a = zombie_anchors(x, y, s, look)
    sway = math.sin(t * 2.2) * 8 * s
    P = lambda dx, dy: (x + dx * s + sway * (-dy / 500), y + dy * s)      # dx already includes the direction
    F = lambda dx, dy: P(dx * d, dy)                                       # dx measured forward
    rng = random.Random(seed * 7 + 3)
    skin = NIGHT if silhouette else ZOMBIE
    dark = _shade(NIGHT, .8) if silhouette else ZOMBIE_D
    shirt = NIGHT if silhouette else (color or RAGS[seed % len(RAGS)])
    pants = _shade(NIGHT, .9) if silhouette else _shade(DENIM, .8)
    hx, hy = a["head"]; hx += sway; r = a["head_r"]
    with Pen(img, a["box"], seed) as p:
        if shadow: p.blob(*P(0, 2), 95 * s, 14 * s)
        step = math.sin(t * 2.2)
        for side, k in ((-1, step), (1, -step)):                           # legs, one dragging behind
            fx = 30 * side + d * 14 * k - (12 * d if side == -d else 0)
            p.limb([P(18 * side, -250), F(4 * side * d + 10 + 8 * k, -130), P(fx, -8)], 22 * s, pants, 4 * s)
            p.shape(spline([P(fx - 14 * d, -2), P(fx - 12 * d, -20), P(fx + 10 * d, -22), P(fx + 34 * d, -10), P(fx + 36 * d, -2)],
                           closed=True), _shade(DARK, .9), w=4 * s, amp=.4)

        def arm(sh, el, hd, w):
            hd = (hd[0] + sway, hd[1])
            p.limb([sh, el], w * s, shirt, 4.5 * s)                            # torn sleeve
            p.limb([el, hd], (w - 9) * s, skin, 4 * s)                          # bony forearm
            if not silhouette:
                p.stroke([(el[0] + d * 6 * s, el[1] - 2 * s), (el[0] + d * 22 * s, el[1] + 4 * s)], 2.5 * s, dark, amp=.2)
            for k in range(3):                                                 # limp hand: short fingers hanging down
                fx0 = hd[0] + d * (6 + k * 7) * s
                p.limb([(fx0, hd[1] + 2 * s), (fx0 + d * 6 * s, hd[1] + 14 * s), (fx0 + d * 4 * s, hd[1] + 24 * s)], 6 * s, skin, 2.5 * s)
            p.limb([(hd[0] - d * 2 * s, hd[1] - 6 * s), (hd[0] + d * 12 * s, hd[1] - 12 * s)], 6 * s, skin, 2.5 * s)   # thumb
            p.shape(ellipse(hd[0] + d * 6 * s, hd[1], 17 * s, 12 * s, n=18), skin, w=4.5 * s, amp=.4)

        arm(F(16, -366), F(104, -334), a["hand_l"], 24)                    # far arm, behind the body
        T = 26                                                             # hunch: the shoulders lean forward
        body = [F(-46 + T, -418), F(46 + T, -416), F(58 + T * .4, -330), F(54, -232)]
        for k in range(7): body.append(F(54 - k * 18, -232 + (16 if k % 2 else 0) + rng.uniform(-4, 4)))
        body += [F(-58 + T * .3, -330)]
        p.shape(body, shirt, w=7 * s, amp=.8)
        if not silhouette:
            hole = ellipse(*F(-6, -312), 20 * s, 26 * s, n=12)
            p.shape(hole, dark, w=3 * s, amp=.9)
            for k in range(3):                                             # ribs through the tear
                yy = -326 + k * 13
                p.stroke(spline([F(-20, yy), F(-6, yy - 4), F(8, yy)]), 3 * s, (230, 226, 200), amp=.1)
            if stains:
                for (bx, by, br) in ((30, -372, 13), (-30, -268, 10), (20, -250, 8), (40, -405, 8)):
                    p.poly(p.wobble(ellipse(*F(bx, by), br * s, br * s * .8, n=12), 1.5, True), STAIN)
        p.limb([F(T, -420), (hx - d * .3 * r, hy + .7 * r)], 26 * s, skin, 4 * s)   # neck stretched forward
        head = rotated(ellipse(hx, hy, r, r * 1.06, n=64), hx, hy, d * .18)
        p.poly(p.wobble(head, .8, True), skin)
        if not silhouette:
            with p.clip(head):
                p.poly(ellipse(hx - d * .55 * r, hy + .45 * r, r * .95, r * .9), dark)
                p.poly(ellipse(hx - d * .3 * r, hy + .2 * r, r * .95, r * .95), skin)
                for k in range(3):                                         # veins and cracks
                    vx = hx - d * (.2 + .25 * k) * r
                    p.stroke([(vx, hy - .95 * r), (vx + d * .06 * r, hy - .7 * r), (vx - d * .04 * r, hy - .55 * r)], .025 * r, dark, amp=.3)
        p.stroke(head, .1 * r, amp=1.2, closed=True)
        for k in range(5):                                                 # thin, messy hair
            bx = hx - .55 * r + k * .24 * r
            p.stroke(spline([(bx, hy - .98 * r), (bx - d * .1 * r, hy - 1.2 * r), (bx + d * .05 * r * (k % 2 * 2 - 1), hy - 1.32 * r)]), .045 * r, amp=.4)
        fx = hx + d * .24 * r
        glow = (250, 236, 120)
        for side in (-1, 1):
            big = side == d
            ex, ey = fx + side * .28 * r, hy - .1 * r + (0 if big else .05 * r)
            if silhouette:
                p.poly(ellipse(ex, ey, .07 * r, .05 * r, n=10), glow)
                continue
            p.poly(ellipse(ex, ey + .02 * r, .25 * r, .24 * r, n=20), (60, 70, 52))   # sunken socket
            p.shape(ellipse(ex, ey, (.16 if big else .12) * r, (.15 if big else .09) * r, n=24), glow, w=.04 * r, amp=.4)
            p.poly(ellipse(ex + d * .03 * r, ey + .01 * r, .035 * r, .035 * r, n=10), (150, 20, 20))
            inner = ex - side * .18 * r                                    # heavy angry brow, low over the eye
            p.stroke([(ex + side * .22 * r, ey - .26 * r), (inner, ey - .14 * r)], .07 * r, amp=.3)
        near = (F(36 + T * .4, -360), F(108, -296), a["hand_r"])
        if silhouette:
            arm(*near, 26)
            a["head"] = (hx, hy)
            return a
        mx, my = fx, hy + .45 * r
        o = {"hungry": .36, "groan": .2}.get(mood, 0)
        if o:
            jaw = spline([(mx - .3 * r, my - .1 * r), (mx, my - .14 * r), (mx + .3 * r, my - .08 * r),
                          (mx + .24 * r, my + o * r), (mx - .02 * r, my + (o + .08) * r), (mx - .26 * r, my + o * r)], closed=True)
            p.poly(jaw, (60, 18, 22))
            with p.clip(jaw):
                for k in range(-3, 4):                                     # jagged teeth, top and bottom
                    tx = mx + k * .085 * r
                    p.poly([(tx - .04 * r, my - .16 * r), (tx + .04 * r, my - .16 * r), (tx + (k % 2) * .01 * r, my - .02 * r - (k % 2) * .03 * r)], (236, 228, 190))
                    p.poly([(tx - .035 * r, my + (o + .12) * r), (tx + .035 * r, my + (o + .12) * r), (tx, my + (o - .06) * r + (k % 2) * .03 * r)], (236, 228, 190))
            p.stroke(jaw, .05 * r, amp=.5, closed=True)
            p.stroke([(mx + .12 * r, my + (o + .04) * r), (mx + .13 * r, my + (o + .26) * r)], .03 * r, (200, 220, 200), amp=.2)   # drool
        else:
            p.stroke([(mx - .22 * r, my + .02 * r), (mx - .05 * r, my - .03 * r), (mx + .1 * r, my + .03 * r), (mx + .22 * r, my - .02 * r)], .05 * r, amp=.4)
            for k in range(3): p.stroke([(mx - .12 * r + k * .12 * r, my - .07 * r), (mx - .12 * r + k * .12 * r, my + .07 * r)], .03 * r, amp=0)
        sx = hx - d * .5 * r                                               # stitched scar
        p.stroke([(sx, hy - .62 * r), (sx + d * .22 * r, hy - .28 * r)], .035 * r, STAIN, amp=.2)
        for k in range(3):
            q = (sx + d * .22 * r * (k + .5) / 3, hy - .62 * r + .34 * r * (k + .5) / 3)
            p.stroke([(q[0] - .05 * r, q[1] + .03 * r), (q[0] + .05 * r, q[1] - .03 * r)], .025 * r, STAIN, amp=.1)
        arm(*near, 26)                                                     # near arm, in front
    a["head"] = (hx, hy)
    return a

def horde(img, x0, x1, base, n=12, s=.5, depth=160, look=1.0, silhouette=False, t=0.0, seed=1):
    """A crowd of n zombies walking towards 'look', spread from x0 to x1; the back rows sit up to 'depth' px higher
    and smaller. silhouette=True for far away or night."""
    rng = random.Random(seed)
    spots = []
    for k in range(n):
        f = rng.random()
        spots.append((f, x0 + (x1 - x0) * (k + rng.uniform(.1, .9)) / n))
    spots.sort()
    for k, (f, xx) in enumerate(spots):
        ss = s * (.6 + .4 * f)
        zombie(img, xx, base - depth * (1 - f), ss, look=look, silhouette=silhouette or f < .3, t=t + k * .7,
               mood=("hungry", "groan", "blank")[k % 3], seed=seed * 31 + k)

def survivor(img, x, y, s=1.0, mood="worried", arms=("down", "hold"), look=0.0, color=OLIVE, pack=(196, 100, 50), held=None,
             on=True, shadow=False, seed=1):
    """doodle as a survivor: hoodie with a big backpack and straps; held = flashlight (on/off), shovel, map or None."""
    P = lambda dx, dy: (x + dx * s, y + dy * s)
    with Pen(img, (x - 120 * s, y - 470 * s, x + 120 * s, y - 220 * s), seed + 5) as p:
        p.shape(rrect(*P(-82, -450), *P(82, -240), 26 * s), pack, w=7 * s, amp=.6)
        p.shape(rrect(*P(-90, -470), *P(90, -420), 18 * s), _shade(pack, .8), w=6 * s, amp=.5)

    def dress(p, a):
        for k in (-1, 1):
            p.limb([P(34 * k, -418), P(30 * k, -330), P(36 * k, -262)], 9 * s, _shade(pack, .75), 3 * s)
        p.limb([P(-34, -340), P(34, -340)], 7 * s, _shade(pack, .75), 2.5 * s)
        p.shape(rrect(*P(-12, -346), *P(12, -334), 2 * s), GRAY, w=2 * s, amp=.1)

    a = doodle(img, x, y, s, outfit="hoodie", color=color, mood=mood, arms=arms, look=look, dress=dress, shadow=shadow, seed=seed)
    if held:
        gx, gy = a["hand_r"]
        L = 200 * s
        with Pen(img, (gx - L * 3.2, gy - L * 3.2, gx + L * 3.2, gy + L * 3.2), seed + 3) as p:
            if held == "flashlight": _flashlight(p, gx, gy, L * .7, math.pi / 2 if look >= 0 else -math.pi / 2, on)
            elif held == "shovel": _shovel(p, gx, gy, L * 1.4, .15)
            elif held == "map": _paper_map(p, gx + 60 * s, gy - 40 * s, 190 * s, 140 * s, (), None, None, .12)
            p.shape(ellipse(gx, gy, 14 * s, 14 * s, n=20), WHITE, w=5 * s, amp=.6)
    return a

# ---------- ground and landscape ----------
def soil_section(img, x0, top, x1, bottom, grass=True, rocks=.5, water=None, seed=1):
    """Side cut of the ground: grass, dark topsoil, earth and a rocky layer at the bottom. rocks = 0…1 how much rock;
    water = 0…1 height of the water table (None = no water). Returns the y of each layer."""
    h = bottom - top
    y_top, y_earth, y_rock = top + h * .08, top + h * .2, top + h * (.75 - .4 * rocks)
    rng = random.Random(seed)
    with Pen(img, (x0 - 10, top - 40, x1 + 10, bottom + 10), seed) as p:
        box = [(x0, top), (x1, top), (x1, bottom), (x0, bottom)]
        with p.clip(box):
            p.poly(box, SOIL)
            for k in range(int((x1 - x0) * h / 1800)):
                q = (rng.uniform(x0, x1), rng.uniform(y_earth, y_rock))
                p.poly(ellipse(*q, 3, 2.4, n=8), SOIL_D)
            p.poly([(x0, top), (x1, top), (x1, y_earth), (x0, y_earth)], TOPSOIL)
            p.poly([(x0 - 5, y_rock)] + [(x0 + (x1 - x0) * k / 12, y_rock + rng.uniform(-14, 14)) for k in range(13)]
                   + [(x1 + 5, y_rock), (x1 + 5, bottom + 5), (x0 - 5, bottom + 5)], ROCK)
            p.hatch([(x0, y_rock), (x1, y_rock), (x1, bottom), (x0, bottom)], ROCK_D, gap=22, w=2.5)
            if water is not None:
                wy = bottom - h * water
                p.poly([(x0 - 5, wy), (x1 + 5, wy), (x1 + 5, bottom + 5), (x0 - 5, bottom + 5)], (150, 186, 214))
                for k in range(int((x1 - x0) / 60)):
                    q = (x0 + 30 + k * 60, wy + (bottom - wy) * (.35 + .3 * (k % 2)))
                    p.stroke([(q[0] - 14, q[1]), (q[0] - 5, q[1] - 5), (q[0] + 5, q[1]), (q[0] + 14, q[1] - 5)], 2.5, WATER_D, amp=0)
                p.stroke([(x0, wy), (x1, wy)], 4, WATER_D, amp=1.2, taper=False)
            for k in range(int(3 + 9 * rocks * (x1 - x0) / 800)):
                bx, by = rng.uniform(x0, x1), rng.uniform(y_earth + h * .1, bottom)
                br = rng.uniform(.04, .09) * h
                p.shape(bumpy([(bx, by, br), (bx + br * .6, by + br * .2, br * .7), (bx - br * .5, by + br * .3, br * .6)], n=30), ROCK, w=4, amp=.6)
                p.stroke([(bx - br * .3, by - br * .2), (bx, by + br * .1), (bx + br * .2, by + br * .05)], 2.5, ROCK_D, amp=.3)
            for y_ in (y_earth, y_rock): p.stroke([(x0, y_), (x1, y_)], 2.5, _shade(SOIL_D), amp=1.6, taper=False)
        if grass:
            p.poly([(x0, top - 4), (x1, top - 4), (x1, y_top), (x0, y_top)], GREEN)
            for k in range(int((x1 - x0) / 14)):
                gx = x0 + k * 14 + rng.uniform(-4, 4)
                p.stroke([(gx, top + 2), (gx + rng.uniform(-6, 6), top - rng.uniform(10, 22))], 3, GREEN_D, amp=.2)
        p.stroke([(x0, top), (x1, top)], 5, amp=1.2, taper=False)
        p.stroke(box, 4, amp=.8, closed=True)
    return {"surface": top, "topsoil": y_top, "earth": y_earth, "rock": y_rock}

def rock(img, cx, base, w=200, color=ROCK, seed=1, shadow=False):
    """Boulder with a couple of cracks."""
    h = w * .62
    with Pen(img, (cx - w * .7, base - h * 1.2, cx + w * .7, base + w * .06), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .05)
        pts = bumpy([(cx - w * .22, base - h * .4, h * .42), (cx + w * .12, base - h * .55, h * .55), (cx + w * .32, base - h * .3, h * .32)], n=40)
        pts = [(x_, min(y_, base)) for x_, y_ in pts]
        p.shape(pts, color, w=6, amp=.8)
        with p.clip(pts): p.hatch([(cx, base - h * 1.2), (cx + w, base - h * 1.2), (cx + w, base), (cx, base)], _shade(color, .82), gap=16, w=3)
        p.stroke([(cx - w * .1, base - h * .8), (cx - w * .02, base - h * .55), (cx + w * .08, base - h * .5)], 3.5, _shade(color, .6), amp=.4)
        p.stroke([(cx - w * .3, base - h * .3), (cx - w * .2, base - h * .18)], 3, _shade(color, .6), amp=.3)

def hills(img, x0, x1, base, h=260, color=(176, 206, 128), rocks=True, seed=1):
    """Rolling hills from x0 to x1 that rise up to h above base (backgrounds); rocks=True scatters stones."""
    rng = random.Random(seed)
    n = 5
    pts = [(x0, base)] + [(x0 + (x1 - x0) * k / n, base - h * rng.uniform(.45, 1)) for k in range(n + 1)] + [(x1, base)]
    with Pen(img, (x0 - 10, base - h * 1.1, x1 + 10, base + 6), seed) as p:
        top = spline(pts[1:-1], n=16)
        shape = [(x0, base)] + top + [(x1, base)]
        p.poly(p.wobble(shape, .5, True), color)
        with p.clip(shape): p.hatch(shape, _shade(color, .85), gap=34, ang=-.6, w=3)
        p.stroke(top, 6, amp=1.2)
        if rocks:
            for k in range(int((x1 - x0) / 140)):
                i = rng.randrange(len(top)); rx, ry = top[i]
                ry += rng.uniform(.15, .6) * (base - ry)
                rr = rng.uniform(10, 22)
                p.shape(bumpy([(rx, ry, rr), (rx + rr * .7, ry + rr * .2, rr * .7)], n=24), ROCK, w=3.5, amp=.4)

def pine_tree(img, cx, base, h=400, color=PINE, seed=1, shadow=False):
    """Pine tree: three stacked green triangles on a short trunk."""
    w = h * .5
    with Pen(img, (cx - w * .7, base - h * 1.05, cx + w * .7, base + h * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .5, h * .03)
        p.shape([(cx - h * .04, base), (cx - h * .03, base - h * .25), (cx + h * .03, base - h * .25), (cx + h * .04, base)], WOOD, w=5)
        for k, (top, bot, hw) in enumerate(((.0, .42, .26), (.2, .66, .36), (.42, .86, .48))):
            tri = [(cx, base - h + top * h), (cx + w * hw * 1.0, base - h + bot * h), (cx + w * hw * .4, base - h + bot * h - h * .03),
                   (cx, base - h + bot * h + h * .01), (cx - w * hw * .4, base - h + bot * h - h * .03), (cx - w * hw, base - h + bot * h)]
            p.poly(p.wobble(tri, .5, True), color)
            p.hatch(tri, _shade(color, .8), gap=18, ang=-1.2, w=3)
            p.stroke(tri, 5, amp=.8, closed=True)

def cabin(img, cx, base, w=380, seed=1, shadow=False):
    """Log cabin in the woods: log walls, dark roof, chimney, door and a window."""
    h = w * .48
    with Pen(img, (cx - w * .65, base - h * 2.1, cx + w * .65, base + w * .06), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .04)
        top = base - h
        p.shape(rrect(cx + w * .2, top - h * .9, cx + w * .32, top - h * .2, 3), (160, 90, 70), w=5, amp=.4)
        wall = [(cx - w * .45, base), (cx - w * .45, top), (cx + w * .45, top), (cx + w * .45, base)]
        p.shape(wall, WOOD, w=6)
        for k in range(1, 7):
            yy = top + h * k / 7
            p.stroke([(cx - w * .47, yy), (cx + w * .47, yy)], 3.5, WOOD_D, amp=.8)
        for sd in (-1, 1):
            for k in range(7): p.shape(ellipse(cx + sd * w * .47, top + h * (k + .5) / 7, h * .06, h * .065, n=12), (214, 160, 100), w=2.5, amp=.2)
        roof = [(cx - w * .58, top + h * .05), (cx, top - h * .75), (cx + w * .58, top + h * .05)]
        p.shape(roof, (92, 60, 46), w=6)
        p.hatch(roof, (70, 46, 36), gap=18, ang=-.5, w=3)
        p.stroke(roof, 6, amp=.6, closed=True)
        p.shape(rrect(cx - w * .32, base - h * .78, cx - w * .1, base, 3), WOOD_D, w=5, amp=.4)
        p.poly(ellipse(cx - w * .14, base - h * .38, 5, 5, n=8), GOLD)
        win = rrect(cx + w * .06, top + h * .25, cx + w * .32, top + h * .62, 3)
        p.shape(win, GLASS, w=5, amp=.4)
        p.stroke([(cx + w * .19, top + h * .25), (cx + w * .19, top + h * .62)], 3, amp=.2)
        p.stroke([(cx + w * .06, top + h * .43), (cx + w * .32, top + h * .43)], 3, amp=.2)

# ---------- shelters and perimeter ----------
def shelter(img, cx, base, w=420, stage=4, door=True, seed=1, shadow=False):
    """Temporary shelter (small shed) built in stages: 1 foundation slab, 2 frame and walls, 3 roof, 4 door and
    window (finished). Animate 'stage' to show it being built."""
    h = w * .55
    top = base - h
    with Pen(img, (cx - w * .65, base - h * 1.7, cx + w * .65, base + w * .08), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .04)
        p.shape(rrect(cx - w * .52, base - w * .04, cx + w * .52, base + w * .03, 3), CONCRETE, w=5, amp=.4)
        if stage < 2: return
        wall = [(cx - w * .45, base - w * .04), (cx - w * .45, top), (cx + w * .45, top), (cx + w * .45, base - w * .04)]
        p.shape(wall, (222, 200, 160), w=6)
        for k in range(1, 9):
            xx = cx - w * .45 + w * .9 * k / 9
            p.stroke([(xx, top + 4), (xx, base - w * .045)], 2.5, _shade((222, 200, 160), .75), amp=.6)
        for xx in (cx - w * .45, cx + w * .45): p.limb([(xx, top), (xx, base - w * .04)], w * .03, WOOD, 3)
        if stage < 3: return
        roof = [(cx - w * .55, top + h * .06), (cx - w * .5, top - h * .3), (cx + w * .55, top - h * .14), (cx + w * .58, top + h * .1)]
        p.shape(roof, STEEL, w=6)
        for k in range(1, 12):
            f = k / 12
            p.stroke([(cx - w * .52 + w * 1.08 * f, top - h * .3 + h * .16 * f), (cx - w * .55 + w * 1.13 * f, top + h * .06 + h * .04 * f)], 3, STEEL_D, amp=.3)
        if stage < 4: return
        if door:
            p.shape(rrect(cx - w * .32, base - h * .78, cx - w * .08, base - w * .04, 3), WOOD_D, w=5, amp=.4)
            p.stroke([(cx - w * .32, base - h * .6), (cx - w * .08, base - h * .2)], 4, _shade(WOOD_D), amp=.3)
            p.poly(ellipse(cx - w * .12, base - h * .4, 5, 5, n=8), GOLD)
        win = rrect(cx + w * .08, top + h * .22, cx + w * .32, top + h * .52, 3)
        p.shape(win, GLASS, w=5, amp=.4)
        p.stroke([(cx + w * .2, top + h * .22), (cx + w * .2, top + h * .52)], 3, amp=.2)

def fence(img, x0, x1, base, h=220, kind="chain", gap=None, gate=False, damage=0.0, seed=1):
    """Perimeter fence from x0 to x1 standing on base: kind = chain (chain-link with barbed wire on top), wood
    (planks), barbed (wire strands) or metal (reinforced corrugated panels). gap = distance between posts;
    gate=True leaves a gate in the middle; damage = 0…1 bends and breaks a few sections."""
    gap = gap or h * 1.1
    n = max(1, round((x1 - x0) / gap))
    xs = [x0 + (x1 - x0) * k / n for k in range(n + 1)]
    rng = random.Random(seed)
    top = base - h
    with Pen(img, (x0 - 30, top - h * .3, x1 + 30, base + 10), seed) as p:
        for i, (a, b) in enumerate(zip(xs, xs[1:])):
            broken = rng.random() < damage
            lean = rng.uniform(-.12, .12) * h if broken else 0
            if gate and i == n // 2:
                g = [(a + 10, top + h * .1), (b - 10, top + h * .1), (b - 10, base - 8), (a + 10, base - 8)]
                p.stroke(g, 6, STEEL_D, amp=.4, closed=True)
                p.stroke([(a + 10, base - 8), (b - 10, top + h * .1)], 5, STEEL_D, amp=.3)
                continue
            panel = [(a, top + (h * .15 if broken else 0)), (b + lean, top), (b, base - (h * .1 if kind == "metal" else 0)), (a, base - (h * .1 if kind == "metal" else 0))]
            if kind == "chain":
                with p.clip(panel):
                    for k in range(-12, int((b - a) / 18) + 12):
                        xx = a + k * 18
                        p.stroke([(xx, top), (xx + h, base)], 2, STEEL_D, amp=.3, taper=False)
                        p.stroke([(xx + h, top), (xx, base)], 2, STEEL_D, amp=.3, taper=False)
                p.stroke([panel[0], panel[1]], 4, STEEL_D, amp=.3)
                for k in range(3):
                    yy = top - h * .06 - k * h * .06
                    p.stroke([(a, yy), (b, yy)], 2.5, DARK, amp=.6)
                    for j in range(1, 4):
                        bx = a + (b - a) * j / 4
                        p.stroke([(bx - 6, yy - 6), (bx + 6, yy + 6)], 2.5, DARK, amp=0)
                        p.stroke([(bx + 6, yy - 6), (bx - 6, yy + 6)], 2.5, DARK, amp=0)
            elif kind == "wood":
                m = max(2, int((b - a) / 34))
                for k in range(m):
                    pa, pb = a + (b - a) * k / m + 3, a + (b - a) * (k + 1) / m - 3
                    pk = [(pa, top + 16 + (lean if k == m - 1 else 0)), ((pa + pb) / 2, top), (pb, top + 16), (pb, base - 4), (pa, base - 4)]
                    p.shape(pk, WOOD, w=4, amp=.5)
                for yy in (top + h * .25, base - h * .25): p.limb([(a, yy), (b, yy + lean * .3)], h * .05, WOOD_D, 3)
            elif kind == "barbed":
                for k in range(4):
                    yy = top + h * .1 + k * h * .24
                    p.stroke([(a, yy), (b, yy + (lean if broken else 0))], 2.5, DARK, amp=.6)
                    for j in range(1, 4):
                        bx = a + (b - a) * j / 4
                        p.stroke([(bx - 6, yy - 6), (bx + 6, yy + 6)], 2.5, DARK, amp=0)
            else:                                            # metal
                p.shape(panel, STEEL, w=5, amp=.4)
                with p.clip(panel):
                    for k in range(int((b - a) / 16) + 1):
                        p.stroke([(a + k * 16, top - 5), (a + k * 16, base + 5)], 2.5, STEEL_D, amp=.3)
                    for yy in (top + h * .2, base - h * .3):
                        p.limb([(a, yy), (b, yy)], h * .05, STEEL_D, 2.5)
                    p.stroke([(a + 6, base - h * .3), (b - 6, top + h * .2)], h * .035, STEEL_D, amp=.3)
                p.stroke(panel, 5, amp=.4, closed=True)
        for k, xx in enumerate(xs):
            post = rrect(xx - h * .035, top - h * (.2 if kind == "chain" else .06), xx + h * .035, base, 3)
            p.shape(post, WOOD_D if kind == "wood" else STEEL_D, w=4.5, amp=.3)

def floodlight(img, x, base, h=420, on=True, ang=.6, beam=380, seed=1):
    """Floodlight on a pole lighting towards ang (radians from straight down: + = right); on=False switches it off."""
    hx, hy = x, base - h
    dx, dy = math.sin(ang), math.cos(ang)
    with Pen(img, (x - beam * 1.1, hy - 60, x + beam * 1.1, max(base, hy + beam) + 10), seed) as p:
        if on:
            nx, ny = dy, -dx
            far = (hx + dx * beam, hy + dy * beam)
            p.poly([(hx + nx * 18, hy + ny * 18), (far[0] + nx * beam * .45, far[1] + ny * beam * .45),
                    (far[0] - nx * beam * .45, far[1] - ny * beam * .45), (hx - nx * 18, hy - ny * 18)], LIGHT)
        p.limb([(x, base), (x, hy + 10)], h * .03, STEEL_D, 3)
        head = rotated(rrect(hx - 22, hy - 30, hx + 22, hy + 30, 6), hx, hy, -ang)
        p.shape(head, DARK, w=5, amp=.3)
        lens = rotated([(hx - 18, hy + 22), (hx + 18, hy + 22), (hx + 18, hy + 30), (hx - 18, hy + 30)], hx, hy, -ang)
        p.shape(lens, YELLOW if on else GRAY_L, w=3, amp=.2)

def security_camera(img, cx, cy, w=160, look=1.0, on=True, seed=1):
    """Wall security camera on a bracket, pointing towards look (1 right, -1 left); on = red light."""
    d = 1 if look >= 0 else -1
    with Pen(img, (cx - w * .9, cy - w * .6, cx + w * .9, cy + w * .5), seed) as p:
        p.shape(rrect(cx - d * w * .5 - w * .06, cy - w * .2, cx - d * w * .5 + w * .06, cy + w * .2, 3), GRAY, w=4, amp=.2)
        p.limb([(cx - d * w * .5, cy), (cx - d * w * .2, cy - w * .02), (cx - d * w * .05, cy - w * .12)], w * .05, GRAY, 3)
        body = rotated(rrect(cx - w * .32, cy - w * .32, cx + w * .32, cy - w * .08, w * .05), cx, cy - w * .2, d * .18)
        p.shape(body, WHITE, w=5, amp=.4)
        lx, ly = rotated([(cx + d * w * .32, cy - w * .2)], cx, cy - w * .2, d * .18)[0]
        p.shape(ellipse(lx, ly, w * .06, w * .09, n=16), DARK, w=3, amp=.2)
        p.poly(ellipse(cx - d * w * .1, cy - w * .26, w * .025, w * .025, n=10), RED if on else GRAY)

def bunker_door(img, cx, base, h=420, open=0.0, kind="door", seed=1, shadow=False):
    """Heavy steel door in a concrete frame with a wheel lock and rivets. kind="hatch" draws a round escape hatch in
    the ground seen at an angle (base = ground line). open = 0…1."""
    with Pen(img, (cx - h * .75, base - h * 1.15, cx + h * .75, base + h * .2), seed) as p:
        if kind == "hatch":
            rx, ry = h * .4, h * .14
            if open:
                ly = base - ry * .4 - h * .32 * open
                p.shape(ellipse(cx, ly, rx * .96, h * .32 * open + ry * .2, n=48), STEEL, w=6, amp=.4)
                p.stroke(ellipse(cx, ly, rx * .75, (h * .32 * open + ry * .2) * .78, n=40), 3, STEEL_D, amp=.2, closed=True)
                wy = ly
            p.shape(ellipse(cx, base, rx * 1.25, ry * 1.25, n=48), CONCRETE, w=6, amp=.5)
            p.shape(ellipse(cx, base, rx, ry, n=48), DARK, w=5, amp=.4)
            if not open:
                p.shape(ellipse(cx, base - h * .02, rx * .98, ry * .98, n=48), STEEL, w=6, amp=.4)
                wy = base - h * .02
            p.stroke(ellipse(cx, wy, h * .12, h * .12 * (.4 if not open else 1), n=28), h * .022, DARK, amp=.2, closed=True)
            p.stroke([(cx - h * .12, wy), (cx + h * .12, wy)], h * .018, DARK, amp=.1)
            return
        w = h * .62
        if shadow: p.blob(cx, base, w * .7, h * .03)
        p.shape(rrect(cx - w * .62, base - h * 1.08, cx + w * .62, base, 6), CONCRETE, w=6, amp=.5)
        p.hatch(rrect(cx - w * .62, base - h * 1.08, cx + w * .62, base, 6), CONCRETE_D, gap=26, w=2.5)
        frame = rrect(cx - w * .5, base - h, cx + w * .5, base, 8)
        p.shape(frame, DARK, w=6, amp=.4)
        dw = w * (1 - .78 * open)
        door = [(cx - w * .5, base - h), (cx - w * .5 + dw, base - h - h * .06 * open), (cx - w * .5 + dw, base + h * .06 * open), (cx - w * .5, base)]
        p.shape(door, STEEL, w=6, amp=.4)
        k = dw / w
        for fy in (.08, .5, .92):
            for fx in (.1, .9):
                p.poly(ellipse(cx - w * .5 + dw * fx, base - h + h * fy, 5, 5, n=8), STEEL_D)
        wx, wy = cx - w * .5 + dw * .5, base - h * .5
        rr = w * .2 * k
        if rr > 6:
            p.stroke(ellipse(wx, wy, rr, rr, n=28), max(3, w * .04), DARK, amp=.2, closed=True)
            for a_ in (0, math.pi / 3, 2 * math.pi / 3):
                p.stroke([(wx - math.cos(a_) * rr, wy - math.sin(a_) * rr), (wx + math.cos(a_) * rr, wy + math.sin(a_) * rr)], max(2, w * .025), DARK, amp=.1)
            p.poly(ellipse(wx, wy, rr * .2, rr * .2, n=12), DARK)

def bunker_section(img, cx, ground, w=900, buried=.7, soil=True, vents=True, drain=True, exit=True, stairs=True,
                   rooms=2, lights=True, seed=1):
    """Partly buried bunker in cross-section: earth around it, thick concrete shell with a waterproof skin, earth
    berm over the roof, stairs down to the entrance on the left, an escape shaft with a ladder and hatch on the right,
    a vent pipe through the roof, gravel and a drain pipe under the floor. buried = 0…1 how much of the shell is
    under the ground line. Returns the interior box: {"left", "right", "ceiling", "floor", "ground"}."""
    h = w * .36
    t = w * .035                                          # wall thickness
    top, bot = ground - h * (1 - buried), ground + h * buried
    L, R = cx - w * .36, cx + w * .36
    inside = {"left": L + t, "right": R - t, "ceiling": top + t, "floor": bot - t, "ground": ground}
    rng = random.Random(seed)
    with Pen(img, (cx - w * .55, top - h * .7, cx + w * .55, bot + h * .4), seed) as p:
        X0, X1, B = cx - w * .52, cx + w * .52, bot + h * .35
        if soil:
            box = [(X0, ground), (X1, ground), (X1, B), (X0, B)]
            p.poly(box, SOIL)
            with p.clip(box):
                for k in range(int(w * h / 900)):
                    p.poly(ellipse(rng.uniform(X0, X1), rng.uniform(ground, B), 3, 2.4, n=8), SOIL_D)
                for k in range(6):
                    bx, by = rng.uniform(X0, X1), rng.uniform(bot, B)
                    br = rng.uniform(.06, .1) * h
                    p.shape(bumpy([(bx, by, br), (bx + br * .6, by + br * .2, br * .7)], n=24), ROCK, w=3.5, amp=.5)
            # earth berm over the part above ground
            if buried < 1:
                berm = spline([(L - w * .1, ground), (L - t, top - t * .6), (cx, top - t * 1.6), (R + t, top - t * .6), (R + w * .1, ground)])
                p.shape(berm + [(L - w * .1, ground)], SOIL, w=0)
                p.poly([(q[0], q[1] - 8) for q in berm] + list(reversed(berm)), GREEN)
                p.stroke([(q[0], q[1] - 6) for q in berm], 5, GREEN_D, amp=.8)
            p.poly([(X0, ground - 6), (L - w * .1, ground - 6), (L - w * .1, ground + 6), (X0, ground + 6)], GREEN)
            p.poly([(R + w * .1, ground - 6), (X1, ground - 6), (X1, ground + 6), (R + w * .1, ground + 6)], GREEN)
            p.stroke([(X0, ground), (L - w * .1, ground)], 5, amp=.8)
            p.stroke([(R + w * .1, ground), (X1, ground)], 5, amp=.8)
        if drain:
            gr = [(L - t * 1.4, bot - h * .25), (R + t * 1.4, bot - h * .25), (R + t * 1.4, bot + t * 1.4), (L - t * 1.4, bot + t * 1.4)]
            p.poly(gr, GRAVEL)
            with p.clip(gr):
                for k in range(int(w / 6)):
                    p.stroke(ellipse(rng.uniform(L - t * 2, R + t * 2), rng.uniform(bot - h * .25, bot + t * 1.6), 3.5, 3, n=8), 1.5, _shade(GRAVEL, .7), amp=0, closed=True)
            for sx in (L - t * .7, R + t * .7):
                p.shape(ellipse(sx, bot + t * .4, t * .55, t * .55, n=20), WHITE, w=3, amp=.2)
                for k in range(4): p.poly(ellipse(sx + math.cos(k * 1.57) * t * .3, bot + t * .4 + math.sin(k * 1.57) * t * .3, 2, 2, n=6), INK)
        shell = [(L, top), (R, top), (R, bot), (L, bot)]
        wy = max(top + t, ground - h * .1)
        p.stroke([(L - 6, wy), (L - 6, bot + 6), (R + 6, bot + 6), (R + 6, wy)], 6, TAR, amp=.3)
        p.shape(shell, CONCRETE, w=6, amp=.5)
        p.hatch(shell, CONCRETE_D, gap=20, w=2.5, ang=-.8)
        room = [(L + t, top + t), (R - t, top + t), (R - t, bot - t), (L + t, bot - t)]
        p.shape(room, ROOM, w=4, amp=.4)
        fl = bot - t
        p.stroke([(L + t, fl - 4), (R - t, fl - 4)], 4, WOOD_D, amp=.3)
        if rooms > 1:
            for k in range(1, rooms):
                xx = L + t + (R - L - 2 * t) * k / rooms
                p.poly([(xx - t * .25, top + t), (xx + t * .25, top + t), (xx + t * .25, fl - h * .38), (xx - t * .25, fl - h * .38)], CONCRETE)
                p.stroke([(xx - t * .25, top + t), (xx - t * .25, fl - h * .38), (xx + t * .25, fl - h * .38), (xx + t * .25, top + t)], 3, amp=.2)
        if lights:
            for k in range(rooms):
                lx = L + t + (R - L - 2 * t) * (k + .5) / rooms
                p.poly([(lx - 20, top + t), (lx + 20, top + t), (lx + 70, fl - 4), (lx - 70, fl - 4)], (255, 246, 204))
                p.shape([(lx - 16, top + t), (lx + 16, top + t), (lx + 10, top + t + 12), (lx - 10, top + t + 12)], YELLOW, w=3, amp=.2)
        if stairs:                                       # stairs down to the door on the left
            sx0, sx1 = L - w * .14, L
            p.poly([(sx0, ground), (sx1, ground), (sx1, fl), (sx0, fl)], ROOM)
            n, steps = 6, []
            for k in range(n + 1):
                xx = sx0 + (sx1 - sx0) * k / n
                yy = ground + (fl - ground) * k / n
                steps += [(xx, yy), (xx + (sx1 - sx0) / n, yy)]
            p.stroke(steps[:-1], 4, amp=.3)
            p.stroke([(sx0, ground), (sx0, fl), (sx1, fl)], 4, amp=.3)
            p.poly([(L - 3, fl - h * .5), (L + t + 3, fl - h * .5), (L + t + 3, fl), (L - 3, fl)], STEEL)
            p.stroke([(L, fl - h * .5), (L + t, fl - h * .5)], 4, amp=.2)
        surf = ground if buried >= 1 or not soil else top - t * 1.1     # surface over the roof (berm)
        if exit:                                         # escape shaft with a ladder up to a hatch on the surface
            ex = R - t - w * .05
            p.poly([(ex - w * .035, surf), (ex + w * .035, surf), (ex + w * .035, top + t), (ex - w * .035, top + t)], (226, 220, 204))
            p.stroke([(ex - w * .035, surf), (ex - w * .035, top + t)], 3, amp=.2)
            p.stroke([(ex + w * .035, surf), (ex + w * .035, top + t)], 3, amp=.2)
            for xx in (ex - w * .02, ex + w * .02): p.stroke([(xx, surf), (xx, fl)], 3, STEEL_D, amp=.2)
            yy = fl - 14
            while yy > surf + 6:
                p.stroke([(ex - w * .02, yy), (ex + w * .02, yy)], 3, STEEL_D, amp=.1); yy -= 22
            p.shape(ellipse(ex, surf, w * .05, w * .015, n=24), STEEL, w=4, amp=.2)
        if vents:
            vx = cx - (R - L) * .12
            vt = surf - h * .2
            p.limb([(vx, top + t), (vx, vt)], w * .028, STEEL, 3)
            p.shape(spline([(vx - w * .05, vt), (vx, vt - h * .1), (vx + w * .05, vt)]) + [(vx - w * .05, vt)], STEEL, w=4, amp=.3)
            p.shape(ellipse(vx, top + t + 16, 16, 16, n=16), WHITE, w=3, amp=.2)
            for k in range(3): p.stroke([(vx, top + t + 16), (vx + math.cos(k * 2.1) * 13, top + t + 16 + math.sin(k * 2.1) * 13)], 3, GRAY, amp=0)
    return inside

# ---------- power ----------
def solar_panel(img, cx, base, w=320, tilt=.35, glint=True, seed=1, shadow=False):
    """Solar panel on a tilted stand: blue cells in a grid; glint=True adds white shine strokes."""
    h = w * .62
    with Pen(img, (cx - w * .65, base - h * 1.25, cx + w * .65, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .5, w * .04)
        y0, y1 = base - h * 1.05, base - h * (1.05 - .55)
        lift = h * tilt * .6
        tl, tr, br, bl = (cx - w * .42, y0), (cx + w * .5, y0 + lift * .2), (cx + w * .42, y1 + lift), (cx - w * .5, y1)
        for (fx, fy) in ((cx - w * .3, y1), (cx + w * .3, y1 + lift)):
            p.limb([(fx, fy - 4), (fx + (8 if fx > cx else -8), base)], w * .03, STEEL_D, 3)
        p.limb([(cx - w * .3, base - h * .2), (cx + w * .3, base - h * .2)], w * .02, STEEL_D, 2.5)
        quad = [tl, tr, br, bl]
        p.shape(quad, PANEL, w=6, amp=.4)
        L = lambda a, b, f: (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        for k in range(1, 6): p.stroke([L(tl, tr, k / 6), L(bl, br, k / 6)], 2.5, (150, 180, 230), amp=.2)
        for k in range(1, 4): p.stroke([L(tl, bl, k / 4), L(tr, br, k / 4)], 2.5, (150, 180, 230), amp=.2)
        if glint:
            for f in (.2, .3):
                p.stroke([L(L(tl, tr, f), L(bl, br, f), .15), L(L(tl, tr, f + .1), L(bl, br, f + .1), .05)], 4, WHITE, amp=.1)
        p.stroke(quad, 6, amp=.4, closed=True)

def battery_bank(img, cx, base, w=320, charge=.7, n=3, seed=1, shadow=False):
    """Row of n big batteries on a rack, each with a charge bar (charge = 0…1; red when low, green when full)."""
    h = w * .55
    col = RED if charge < .25 else (YELLOW if charge < .6 else GREEN)
    with Pen(img, (cx - w * .6, base - h * 1.25, cx + w * .6, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .04)
        p.shape(rrect(cx - w * .52, base - w * .05, cx + w * .52, base, 3), DARK, w=4, amp=.3)
        bw = w * .96 / n
        for k in range(n):
            x0 = cx - w * .48 + k * bw + bw * .06
            x1 = x0 + bw * .88
            top = base - h - w * .05
            for tx, c in ((x0 + bw * .2, RED), (x1 - bw * .2, DARK)):
                p.shape(rrect(tx - bw * .08, top - h * .1, tx + bw * .08, top + 4, 2), c, w=3, amp=.2)
            p.shape(rrect(x0, top, x1, base - w * .05, 6), (70, 74, 84), w=5, amp=.4)
            p.shape(rrect(x0 + bw * .2, top + h * .25, x1 - bw * .2, base - w * .05 - h * .12, 3), WHITE, w=3, amp=.2)
            iy0, iy1 = top + h * .25, base - w * .05 - h * .12
            fy = iy1 - (iy1 - iy0) * max(0, min(1, charge))
            if charge > 0: p.poly([(x0 + bw * .2 + 3, fy), (x1 - bw * .2 - 3, fy), (x1 - bw * .2 - 3, iy1 - 3), (x0 + bw * .2 + 3, iy1 - 3)], col)
            p.text("+", x0 + bw * .2, top + h * .12, h * .12, fill=WHITE, warp=0)

def battery(img, cx, cy, h=140, ang=0.0, charge=1.0, seed=1):
    """Single AA-style battery; charge = 0…1 draws the level band."""
    w = h * .38
    R = lambda pts: rotated(pts, cx, cy, ang)
    with Pen(img, (cx - h * .7, cy - h * .7, cx + h * .7, cy + h * .7), seed) as p:
        p.shape(R(rrect(cx - w * .2, cy - h * .56, cx + w * .2, cy - h * .46, 2)), GRAY, w=3, amp=.2)
        p.shape(R(rrect(cx - w / 2, cy - h * .48, cx + w / 2, cy + h * .5, w * .15)), DARK, w=5, amp=.3)
        p.poly(R([(cx - w / 2 + 3, cy - h * .48 + 3), (cx + w / 2 - 3, cy - h * .48 + 3), (cx + w / 2 - 3, cy - h * .2), (cx - w / 2 + 3, cy - h * .2)]), GOLD)
        col = RED if charge < .25 else (YELLOW if charge < .6 else GREEN)
        fy = cy + h * .4 - h * .55 * max(0, min(1, charge))
        if charge > 0: p.poly(R([(cx - w * .25, fy), (cx + w * .25, fy), (cx + w * .25, cy + h * .4), (cx - w * .25, cy + h * .4)]), col)
        p.stroke(R(rrect(cx - w / 2, cy - h * .48, cx + w / 2, cy + h * .5, w * .15)), 5, amp=.3, closed=True)

def generator(img, cx, base, w=320, running=False, color=ORANGE, t=0.0, seed=1, shadow=False):
    """Portable backup generator in a tube frame; running=True puffs exhaust and shakes a little with t."""
    h = w * .62
    j = math.sin(t * 40) * 2 if running else 0
    with Pen(img, (cx - w * .65, base - h * 1.8, cx + w * .65, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .04)
        top = base - h + j
        body = rrect(cx - w * .4, top + h * .12, cx + w * .4, base - h * .1, w * .06)
        p.shape(body, color, w=6, amp=.4)
        p.shape(rrect(cx - w * .34, top + h * .08, cx + w * .02, top + h * .36, 8), _shade(color, .8), w=4, amp=.3)
        p.shape(rrect(cx + w * .08, top + h * .3, cx + w * .34, top + h * .62, 6), DARK, w=4, amp=.3)
        for k in range(3): p.stroke([(cx + w * .12, top + h * (.38 + k * .08)), (cx + w * .3, top + h * (.38 + k * .08))], 3, GRAY, amp=.1)
        for k in range(2): p.poly(ellipse(cx - w * (.24 - k * .12), top + h * .58, w * .03, w * .03, n=12), DARK)
        frame = [(cx - w * .48, base), (cx - w * .48, top + h * .05), (cx + w * .48, top + h * .05), (cx + w * .48, base)]
        p.stroke(frame, w * .03, DARK, amp=.3)
        p.stroke([(cx - w * .48, base - h * .05), (cx + w * .48, base - h * .05)], w * .03, DARK, amp=.3)
        p.limb([(cx + w * .3, top + h * .12), (cx + w * .3, top - h * .08)], w * .03, STEEL_D, 2.5)
        if running:
            for k in range(3):
                f = (t * 1.3 + k / 3) % 1
                r = w * (.05 + .08 * f)
                sx, sy = cx + w * (.32 + .1 * f), top - h * (.15 + .7 * f)
                p.shape(bumpy([(sx, sy, r), (sx + r * .6, sy - r * .2, r * .7)], n=24), (200, 200, 204), w=3, amp=.4)

def electrical_panel(img, cx, cy, h=320, tripped=(), open=True, seed=1):
    """Wall breaker box with its door open: two columns of switches; tripped = indices (0…9) that are off (red)."""
    w = h * .72
    with Pen(img, (cx - w * 1.1, cy - h * .6, cx + w * .7, cy + h * .6), seed) as p:
        box = rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 6)
        p.shape(box, GRAY_L, w=6, amp=.4)
        if open:
            p.shape([(cx - w / 2, cy - h / 2), (cx - w * 1.0, cy - h * .44), (cx - w * 1.0, cy + h * .44), (cx - w / 2, cy + h / 2)], GRAY, w=5, amp=.4)
        p.shape(rrect(cx - w * .38, cy - h * .38, cx + w * .38, cy + h * .4, 4), DARK, w=4, amp=.3)
        for i in range(10):
            col, row = i % 2, i // 2
            bx, by = cx + (-.17 if col == 0 else .17) * w, cy - h * .3 + row * h * .15
            off = i in tripped
            p.shape(rrect(bx - w * .12, by - h * .05, bx + w * .12, by + h * .05, 3), WHITE, w=3, amp=.2)
            sx = bx + (-w * .05 if off else w * .05)
            p.poly(rrect(sx - w * .035, by - h * .035, sx + w * .035, by + h * .035, 2), RED if off else GREEN)
        p.poly(ellipse(cx + w * .3, cy - h * .44, w * .025, w * .025, n=10), RED if tripped else GREEN)

def wire(img, pts, color=DARK, w=6, sag=.0, seed=1):
    """Cable through the points; sag = how much it hangs between points (0…1)."""
    pts = list(pts)
    if sag and len(pts) >= 2:
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            out += [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + sag * math.dist(a, b) * .25), b]
        pts = out
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    with Pen(img, (min(xs) - w * 3, min(ys) - w * 3, max(xs) + w * 3, max(ys) + w * 3), seed) as p:
        p.stroke(spline(pts) if len(pts) > 2 else pts, w, color, amp=.6, taper=False)

# ---------- water ----------
def water_tank(img, cx, base, h=360, level=.6, color=(70, 110, 170), label=None, seed=1, shadow=False):
    """Plastic water tank on a base: level strip that shows the water (level = 0…1), lid and outlet tap."""
    w = h * .7
    with Pen(img, (cx - w * .7, base - h * 1.1, cx + w * .7, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .04)
        top, bot = base - h * .95, base - h * .06
        p.shape(rrect(cx - w * .46, base - h * .06, cx + w * .46, base, 3), CONCRETE, w=4, amp=.3)
        body = spline([(cx - w * .42, bot), (cx - w * .44, top + h * .2), (cx - w * .3, top + h * .05), (cx, top), (cx + w * .3, top + h * .05),
                       (cx + w * .44, top + h * .2), (cx + w * .42, bot)]) + [(cx - w * .42, bot)]
        p.shape(body, color, w=6, amp=.5)
        for k in (.35, .6): p.stroke([(cx - w * .43, top + h * k), (cx + w * .43, top + h * k)], 3, _shade(color, .75), amp=.6)
        p.shape(rrect(cx - w * .12, top - h * .04, cx + w * .12, top + h * .04, 4), _shade(color, .7), w=4, amp=.2)
        sx0, sx1, sy0, sy1 = cx + w * .14, cx + w * .26, top + h * .14, bot - h * .06
        p.shape(rrect(sx0, sy0, sx1, sy1, 4), WHITE, w=3.5, amp=.2)
        fy = sy1 - (sy1 - sy0) * max(0, min(1, level))
        if level > 0: p.poly([(sx0 + 3, fy), (sx1 - 3, fy), (sx1 - 3, sy1 - 3), (sx0 + 3, sy1 - 3)], WATER)
        for k in range(1, 4): p.stroke([(sx0 - 6, sy0 + (sy1 - sy0) * k / 4), (sx0 + 2, sy0 + (sy1 - sy0) * k / 4)], 2.5, amp=0)
        p.limb([(cx - w * .42, bot - h * .1), (cx - w * .56, bot - h * .1)], h * .03, STEEL, 2.5)
        p.shape(rrect(cx - w * .6, bot - h * .14, cx - w * .54, bot - h * .02, 2), RED, w=2.5, amp=.1)
        if label: p.text(label, cx - w * .1, top + h * .48, _fit(label, h * .08, w * .45), fill=WHITE, warp=0)

def water_filter(img, cx, base, h=320, seed=1, shadow=False):
    """Gravity water filter: top tank cut open to show sand, charcoal and gravel layers over a bottom tank with tap."""
    w = h * .5
    with Pen(img, (cx - w * .8, base - h * 1.05, cx + w * .8, base + w * .06), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .05)
        t0, mid = base - h, base - h * .48
        top = rrect(cx - w * .45, t0 + h * .04, cx + w * .45, mid, 6)
        p.shape(top, GLASS, w=5, amp=.4)
        with p.clip(top):
            for k, (c, f) in enumerate(((WATER, .0), ((236, 220, 170), .3), ((60, 60, 66), .52), (GRAVEL, .76))):
                yy = t0 + h * .04 + (mid - t0 - h * .04) * f
                p.poly([(cx - w, yy), (cx + w, yy), (cx + w, mid + 4), (cx - w, mid + 4)], c)
            for k in range(14):
                gx, gy = cx - w * .4 + (k % 7) * w * .13, mid - h * .05 - (k // 7) * h * .04
                p.stroke(ellipse(gx, gy, 6, 5, n=8), 1.5, _shade(GRAVEL), amp=0, closed=True)
        p.stroke(top, 5, amp=.4, closed=True)
        p.shape(rrect(cx - w * .5, t0, cx + w * .5, t0 + h * .06, 4), GRAY, w=4, amp=.3)
        bottom = rrect(cx - w * .45, mid + h * .02, cx + w * .45, base, 6)
        p.shape(bottom, (220, 236, 246), w=5, amp=.4)
        with p.clip(bottom): p.poly([(cx - w, base - h * .25), (cx + w, base - h * .25), (cx + w, base), (cx - w, base)], WATER)
        p.stroke(bottom, 5, amp=.4, closed=True)
        p.limb([(cx + w * .45, base - h * .12), (cx + w * .6, base - h * .12)], h * .03, STEEL, 2.5)
        p.shape(rrect(cx + w * .56, base - h * .17, cx + w * .66, base - h * .07, 2), BLUE, w=2.5, amp=.1)
        for k in range(3): p.shape(ellipse(cx - w * .2 + k * w * .2, mid + h * .06, 4, 6, n=10), WATER, w=2, amp=0)

def rain(img, x0, y0, x1, y1, t=0.0, density=1.0, color=(110, 150, 200), seed=1):
    """Slanted rain streaks filling the box; t makes them fall."""
    rng = random.Random(seed)
    n = int((x1 - x0) * (y1 - y0) / 4000 * density)
    with Pen(img, (x0, y0, x1, y1), seed) as p:
        for k in range(n):
            x, y = rng.uniform(x0 - 60, x1), rng.uniform(0, 1)
            y = y0 + ((y + t * 1.6) % 1) * (y1 - y0 + 60) - 30
            L = rng.uniform(26, 44)
            p.stroke([(x, y), (x + L * .3, y + L)], 3, color, amp=0)

def water_bottle(img, cx, base, h=240, level=.7, seed=1, shadow=False):
    """Plastic water bottle with a blue cap, label band and water level (0…1)."""
    w = h * .36
    with Pen(img, (cx - w * .8, base - h * 1.05, cx + w * .8, base + w * .1), seed) as p:
        if shadow: p.blob(cx, base, w * .6, w * .08)
        body = spline([(cx - w * .5, base), (cx - w * .5, base - h * .62), (cx - w * .2, base - h * .8), (cx - w * .17, base - h * .9),
                       (cx + w * .17, base - h * .9), (cx + w * .2, base - h * .8), (cx + w * .5, base - h * .62), (cx + w * .5, base)], n=6) + [(cx - w * .5, base)]
        p.poly(p.wobble(body, .4, True), (232, 244, 250))
        with p.clip(body):
            ly = base - h * .85 * max(0, min(1, level))
            p.poly([(cx - w, ly), (cx + w, ly), (cx + w, base), (cx - w, base)], WATER)
            p.poly([(cx - w, base - h * .5), (cx + w, base - h * .5), (cx + w, base - h * .3), (cx - w, base - h * .3)], BLUE)
            for yy in (.15, .2, .55): p.stroke([(cx - w * .5, base - h * yy), (cx + w * .5, base - h * yy)], 2, (140, 180, 210), amp=.3)
        p.stroke(body, 5, amp=.4, closed=True)
        p.shape(rrect(cx - w * .2, base - h, cx + w * .2, base - h * .9, 3), BLUE, w=4, amp=.2)
        p.stroke([(cx - w * .3, base - h * .65), (cx - w * .3, base - h * .55)], 3, WHITE, amp=0)

def jerrycan(img, cx, base, h=260, color=BLUE, seed=1, shadow=False):
    """Jerrycan for water or fuel: boxy can with a handle and a spout cap."""
    w = h * .75
    with Pen(img, (cx - w * .7, base - h * 1.1, cx + w * .7, base + w * .06), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .05)
        body = [(cx - w * .45, base), (cx - w * .45, base - h * .82), (cx + w * .2, base - h * .82), (cx + w * .45, base - h * .65), (cx + w * .45, base)]
        p.shape(body, color, w=6, amp=.4)
        p.stroke([(cx - w * .3, base - h * .15), (cx - w * .1, base - h * .6)], 4, _shade(color), amp=.3)
        p.stroke([(cx + w * .1, base - h * .15), (cx - w * .1, base - h * .6)], 4, _shade(color), amp=.3)
        p.stroke([(cx + w * .3, base - h * .15), (cx + w * .1, base - h * .6)], 4, _shade(color), amp=.3)
        p.shape(rrect(cx - w * .4, base - h * 1.0, cx - w * .02, base - h * .82, 6), color, w=5, amp=.3)
        p.poly(rrect(cx - w * .32, base - h * .96, cx - w * .1, base - h * .86, 4), WHITE)
        p.shape(rrect(cx + w * .2, base - h * .95, cx + w * .36, base - h * .75, 3), DARK, w=4, amp=.2)

def tap(img, cx, cy, size=160, flow=0.0, drip=False, t=0.0, seed=1):
    """Wall tap; flow = 0…1 water pouring out; drip=True lets a single drop fall (with t)."""
    s = size
    with Pen(img, (cx - s * .7, cy - s * .5, cx + s * .7, cy + s * 1.6), seed) as p:
        p.shape(rrect(cx - s * .6, cy - s * .12, cx - s * .45, cy + s * .12, 3), STEEL, w=4, amp=.2)
        spout = [(cx - s * .45, cy - s * .08), (cx + s * .2, cy - s * .08), (cx + s * .32, cy + s * .02), (cx + s * .32, cy + s * .2),
                 (cx + s * .18, cy + s * .2), (cx + s * .18, cy + s * .08), (cx - s * .45, cy + s * .08)]
        p.shape(spout, STEEL, w=5, amp=.3)
        p.shape(rrect(cx - s * .08, cy - s * .3, cx + s * .02, cy - s * .08, 2), STEEL, w=4, amp=.2)
        p.shape(rrect(cx - s * .24, cy - s * .38, cx + s * .18, cy - s * .28, 4), RED, w=4, amp=.2)
        ox, oy = cx + s * .25, cy + s * .2
        if flow > 0:
            fw = s * .1 * flow
            p.poly([(ox - fw / 2, oy), (ox + fw / 2, oy), (ox + fw * .6, oy + s * 1.3), (ox - fw * .6, oy + s * 1.3)], WATER)
            for k in range(3):
                yy = oy + s * ((t * 2 + k / 3) % 1) * 1.2
                p.stroke([(ox - fw * .2, yy), (ox - fw * .2, yy + s * .12)], 2.5, WHITE, amp=0)
        elif drip:
            f = (t * .8) % 1
            dy = oy + s * .12 + s * 1.1 * f * f
            p.shape(spline([(ox, dy - s * .1), (ox + s * .05, dy), (ox, dy + s * .04), (ox - s * .05, dy)], closed=True), WATER, w=3, amp=.1)

# ---------- air ----------
def vent_fan(img, cx, cy, r=110, on=True, t=0.0, seed=1):
    """Square wall fan with a grille; the blades turn with t when on."""
    with Pen(img, (cx - r * 1.2, cy - r * 1.2, cx + r * 1.2, cy + r * 1.2), seed) as p:
        p.shape(rrect(cx - r, cy - r, cx + r, cy + r, r * .12), GRAY_L, w=6, amp=.4)
        p.shape(ellipse(cx, cy, r * .85, r * .85, n=40), (70, 74, 84), w=4, amp=.3)
        a0 = t * 9 if on else .3
        for k in range(4):
            a = a0 + k * math.pi / 2
            blade = [(cx, cy)] + [(cx + math.cos(a + u) * r * .78 * (1 - abs(u - .35) * .6), cy + math.sin(a + u) * r * .78 * (1 - abs(u - .35) * .6)) for u in (0, .2, .45, .7)]
            p.shape(blade, STEEL, w=3, amp=.2)
        p.shape(ellipse(cx, cy, r * .14, r * .14, n=16), DARK, w=3, amp=.2)
        for k in range(1, 4): p.stroke(ellipse(cx, cy, r * .85 * k / 4, r * .85 * k / 4, n=32), 2, DARK, amp=.1, closed=True)
        if on:
            for k in (-1, 1): p.stroke([(cx + k * r * 1.08, cy - r * .3), (cx + k * r * 1.14, cy), (cx + k * r * 1.08, cy + r * .3)], 3, GRAY, amp=.2)

def air_duct(img, pts, w=60, color=STEEL, seed=1):
    """Square air duct along the points (corners where the path turns), with joint bands."""
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    with Pen(img, (min(xs) - w * 2, min(ys) - w * 2, max(xs) + w * 2, max(ys) + w * 2), seed) as p:
        path = p.wobble(pts, .4)
        p.ink(path, w + 10, INK, taper=False)
        p.ink(path, w, color, taper=False)
        for a, b in zip(pts, pts[1:]):
            L = math.dist(a, b); n = max(1, int(L / (w * 2.5)))
            ux, uy = (b[0] - a[0]) / (L or 1), (b[1] - a[1]) / (L or 1)
            for k in range(1, n):
                m = (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
                p.stroke([(m[0] - uy * w * .55, m[1] + ux * w * .55), (m[0] + uy * w * .55, m[1] - ux * w * .55)], 4, STEEL_D, amp=.1)
            p.stroke([(a[0] - uy * w * .3 + ux * 6, a[1] + ux * w * .3 + uy * 6), (b[0] - uy * w * .3 - ux * 6, b[1] + ux * w * .3 - uy * 6)], 3, WHITE, amp=.2)

def vent_pipe(img, cx, base, h=260, seed=1):
    """Air intake pipe sticking out of the ground with a mushroom cap and a mesh."""
    w = h * .2
    with Pen(img, (cx - w * 2, base - h * 1.1, cx + w * 2, base + 10), seed) as p:
        p.limb([(cx, base), (cx, base - h * .78)], w, STEEL, 4)
        p.shape(rrect(cx - w * .9, base - h * .9, cx + w * .9, base - h * .76, 4), (220, 224, 230), w=4, amp=.2)
        for k in range(-3, 4): p.stroke([(cx + k * w * .24, base - h * .9), (cx + k * w * .24, base - h * .76)], 1.5, DARK, amp=0)
        cap = spline([(cx - w * 1.6, base - h * .88), (cx - w, base - h * 1.02), (cx + w, base - h * 1.02), (cx + w * 1.6, base - h * .88)])
        p.shape(cap + [(cx - w * 1.6, base - h * .88)], STEEL, w=5, amp=.3)

def air_flow(img, pts, color=(90, 170, 220), w=8, t=0.0, gap=70, seed=1):
    """Moving dashed arrows along a path (air or water flow); t slides them forward."""
    path = spline(pts) if len(pts) > 2 else list(pts)
    from . import resample
    r = resample(path, 4)
    xs, ys = [q[0] for q in r], [q[1] for q in r]
    total = len(r) * 4
    with Pen(img, (min(xs) - 40, min(ys) - 40, max(xs) + 40, max(ys) + 40), seed) as p:
        off = (t * 120) % gap
        s = off
        while s < total - 12:
            i, j = int(s / 4), min(len(r) - 1, int((s + gap * .55) / 4))
            seg = r[i:j + 1]
            if len(seg) >= 2:
                p.stroke(seg, w, color, amp=.2)
                (ax, ay), (bx, by) = seg[-2], seg[-1]
                L = math.hypot(bx - ax, by - ay) or 1; ux, uy = (bx - ax) / L, (by - ay) / L
                p.stroke([(bx - ux * w * 2 - uy * w * 1.6, by - uy * w * 2 + ux * w * 1.6), (bx, by), (bx - ux * w * 2 + uy * w * 1.6, by - uy * w * 2 - ux * w * 1.6)], w * .8, color, amp=.1)
            s += gap

def air_monitor(img, cx, cy, w=200, status="ok", text=None, seed=1):
    """Wall air-quality monitor: screen with a short text and a light (status = ok green, warn yellow, bad red)."""
    h = w * .7
    col = {"ok": GREEN, "warn": YELLOW, "bad": RED}.get(status, GRAY)
    with Pen(img, (cx - w * .65, cy - h * .7, cx + w * .65, cy + h * .7), seed) as p:
        p.shape(rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, w * .1), WHITE, w=6, amp=.4)
        p.shape(rrect(cx - w * .38, cy - h * .34, cx + w * .38, cy + h * .1, 4), (210, 236, 214) if status == "ok" else (240, 230, 200), w=4, amp=.2)
        if text: p.text(text, cx, cy - h * .12, _fit(text, h * .2, w * .7), fill=DARK, warp=0)
        p.shape(ellipse(cx - w * .25, cy + h * .3, w * .06, w * .06, n=16), col, w=3, amp=.2)
        for k in range(3): p.stroke([(cx - w * .05 + k * w * .12, cy + h * .24), (cx - w * .05 + k * w * .12, cy + h * .36)], 3, GRAY, amp=0)

# ---------- supplies ----------
def backpack(img, cx, base, h=260, color=(196, 100, 50), open=False, seed=1, shadow=False):
    """Hiking backpack with a front pocket and straps; open=True shows cans and a bottle peeking out."""
    w = h * .72
    with Pen(img, (cx - w * .7, base - h * 1.2, cx + w * .7, base + w * .06), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .05)
        top = base - h * .88
        p.stroke(spline([(cx - w * .2, top + h * .04), (cx, top - h * .12), (cx + w * .2, top + h * .04)]), 7, _shade(color, .6), amp=.3)
        if open:
            for k, (dx, c) in enumerate(((-.2, TIN), (.18, WATER))):
                p.shape(rrect(cx + w * dx - w * .12, top - h * .16, cx + w * dx + w * .12, top + h * .2, 6), c, w=4, amp=.3)
        body = spline([(cx - w * .45, base), (cx - w * .48, top + h * .3), (cx - w * .36, top), (cx + w * .36, top), (cx + w * .48, top + h * .3), (cx + w * .45, base)], n=8) + [(cx - w * .45, base)]
        p.shape(body, color, w=6, amp=.5)
        if not open:
            p.shape(spline([(cx - w * .44, top + h * .3), (cx - w * .3, top - h * .02), (cx + w * .3, top - h * .02), (cx + w * .44, top + h * .3), (cx, top + h * .38)], closed=True), _shade(color, .82), w=5, amp=.4)
        p.shape(rrect(cx - w * .3, base - h * .42, cx + w * .3, base - h * .06, w * .08), _shade(color, .85), w=5, amp=.4)
        p.stroke([(cx - w * .26, base - h * .32), (cx + w * .26, base - h * .32)], 3, _shade(color, .55), amp=.2)
        for k in (-1, 1): p.stroke([(cx + k * w * .2, top + h * .3), (cx + k * w * .2, base - h * .42)], 5, _shade(color, .6), amp=.2)
        p.shape(rrect(cx - w * .06, top + h * .32, cx + w * .06, top + h * .42, 2), GRAY, w=2.5, amp=.1)

def canned_food(img, cx, base, h=140, label=None, color=RED, open=False, seed=1, shadow=False):
    """Tin can with a paper label (text 'label'); open=True peels the lid back."""
    w = h * .74
    with Pen(img, (cx - w * .7, base - h * 1.4, cx + w * .7, base + w * .08), seed) as p:
        if shadow: p.blob(cx, base, w * .6, w * .07)
        top = base - h
        body = [(cx - w / 2, top), (cx + w / 2, top), (cx + w / 2, base - w * .08)] + \
               [(cx + w / 2 * math.cos(a), base - w * .08 + w * .08 * math.sin(a)) for a in (math.pi * k / 12 for k in range(13))]
        p.shape(body, TIN, w=5, amp=.4)
        band = [(cx - w / 2, top + h * .2), (cx + w / 2, top + h * .2), (cx + w / 2, base - h * .18), (cx - w / 2, base - h * .18)]
        p.poly(band, color)
        p.stroke([(cx - w / 2, top + h * .2), (cx + w / 2, top + h * .2)], 3, amp=.2)
        p.stroke([(cx - w / 2, base - h * .18), (cx + w / 2, base - h * .18)], 3, amp=.2)
        if label: p.text(label, cx, top + h * .5, _fit(label, h * .2, w * .85), fill=WHITE, warp=0)
        p.stroke([(cx - w * .36, top + h * .26), (cx - w * .36, base - h * .26)], 3, WHITE, amp=.1)
        p.shape(ellipse(cx, top, w / 2, w * .1, n=32), TIN_D if open else TIN, w=4.5, amp=.3)
        if open:
            p.shape(rotated(ellipse(cx + w * .1, top - h * .3, w * .45, w * .09, n=32), cx - w * .4, top, -1.0), TIN, w=4, amp=.3)
        else:
            p.stroke(ellipse(cx, top, w * .4, w * .07, n=28), 2, TIN_D, amp=.1, closed=True)

def supply_crate(img, cx, base, w=240, label=None, color=WOOD, seed=1, shadow=False):
    """Wooden supply crate with planks, a diagonal brace and a stenciled label."""
    h = w * .7
    with Pen(img, (cx - w * .6, base - h * 1.1, cx + w * .6, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .04)
        box = [(cx - w / 2, base - h), (cx + w / 2, base - h), (cx + w / 2, base), (cx - w / 2, base)]
        p.shape(box, color, w=6)
        for k in range(1, 4): p.stroke([(cx - w / 2, base - h * k / 4), (cx + w / 2, base - h * k / 4)], 3, _shade(color), amp=.6)
        for sd in (-1, 1): p.shape([(cx + sd * w / 2, base - h), (cx + sd * (w / 2 - w * .1), base - h), (cx + sd * (w / 2 - w * .1), base), (cx + sd * w / 2, base)], _shade(color, .85), w=4, amp=.3)
        p.limb([(cx - w * .38, base - h * .06), (cx + w * .38, base - h * .94)], w * .05, _shade(color, .85), 3)
        if label:
            p.poly(rrect(cx - w * .3, base - h * .62, cx + w * .3, base - h * .38, 3), (240, 230, 200))
            p.text(label, cx, base - h * .5, _fit(label, h * .18, w * .55), fill=DARK, warp=0)

def pantry_shelf(img, cx, base, w=420, h=560, fill=1.0, seed=1, shadow=False):
    """Wooden pantry shelf with 4 shelves of cans, jars, sacks of rice and beans, boxes and oil bottles;
    fill = 0…1 how full it is (items disappear one by one)."""
    rng = random.Random(seed)
    with Pen(img, (cx - w * .6, base - h * 1.05, cx + w * .6, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .04)
        x0, x1, top = cx - w / 2, cx + w / 2, base - h
        p.shape([(x0, top), (x1, top), (x1, base), (x0, base)], (238, 222, 192), w=6)
        rows = 4
        slots = []
        for r in range(rows):
            sy = top + h * (r + 1) / rows - h * .02
            for k in range(5): slots.append((r, k, sy))
        order = list(range(len(slots))); rng.shuffle(order)
        keep = set(order[:round(len(slots) * max(0, min(1, fill)))])
        for i, (r, k, sy) in enumerate(slots):
            if i not in keep: continue
            sx = x0 + w * (k + .5) / 5
            kind = (r * 5 + k * 3 + seed) % 5
            sw = w / 5 * .75
            vs = max(1.0, min(1.6, h / rows * .7 / sw))
            if kind == 0:
                for j in (-1, 1):
                    p.shape(rrect(sx + j * sw * .25 - sw * .22, sy - sw * vs * .6, sx + j * sw * .25 + sw * .22, sy, 3), TIN, w=3, amp=.2)
                    p.poly([(sx + j * sw * .25 - sw * .22, sy - sw * vs * .45), (sx + j * sw * .25 + sw * .22, sy - sw * vs * .45), (sx + j * sw * .25 + sw * .22, sy - sw * vs * .2), (sx + j * sw * .25 - sw * .22, sy - sw * vs * .2)], (RED, GREEN, ORANGE)[(k + r) % 3])
            elif kind == 1:
                p.shape(rrect(sx - sw * .3, sy - sw * vs * .8, sx + sw * .3, sy, 6), (240, 200, 120), w=3.5, amp=.2)
                p.shape(rrect(sx - sw * .32, sy - sw * vs * .92, sx + sw * .32, sy - sw * vs * .78, 3), RED, w=3, amp=.1)
            elif kind == 2:
                p.shape(spline([(sx - sw * .45, sy), (sx - sw * .42, sy - sw * vs * .55), (sx - sw * .25, sy - sw * vs * .8), (sx + sw * .25, sy - sw * vs * .8), (sx + sw * .42, sy - sw * vs * .55), (sx + sw * .45, sy)], n=6) + [(sx - sw * .45, sy)], BEIGE, w=3.5, amp=.4)
                p.stroke([(sx - sw * .2, sy - sw * vs * .78), (sx + sw * .2, sy - sw * vs * .78)], 3, BEIGE_D, amp=.2)
            elif kind == 3:
                p.shape(rrect(sx - sw * .4, sy - sw * vs * .9, sx + sw * .4, sy, 3), (ORANGE, BLUE, YELLOW)[(k + r) % 3], w=3.5, amp=.2)
                p.poly(rrect(sx - sw * .25, sy - sw * vs * .65, sx + sw * .25, sy - sw * vs * .4, 2), WHITE)
            else:
                p.shape(spline([(sx - sw * .2, sy), (sx - sw * .2, sy - sw * vs * .7), (sx - sw * .08, sy - sw * vs * .85), (sx - sw * .08, sy - sw * vs * 1.05), (sx + sw * .08, sy - sw * vs * 1.05), (sx + sw * .08, sy - sw * vs * .85), (sx + sw * .2, sy - sw * vs * .7), (sx + sw * .2, sy)], n=4) + [(sx - sw * .2, sy)], GOLD, w=3.5, amp=.2)
        for r in range(rows):
            sy = top + h * (r + 1) / rows - h * .02
            p.limb([(x0, sy + 6), (x1, sy + 6)], h * .02, WOOD, 3)
        for xx in (x0, x1): p.limb([(xx, top), (xx, base)], w * .03, WOOD_D, 3)
        p.limb([(x0, top), (x1, top)], w * .03, WOOD_D, 3)

def first_aid_kit(img, cx, base, w=240, open=False, seed=1, shadow=False):
    """First aid kit: white box with a red cross and handle; open=True shows bandages, a pill bottle, plasters and
    scissors in compartments."""
    h = w * .62
    with Pen(img, (cx - w * .6, base - h * 2, cx + w * .6, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .04)
        top = base - h
        if open:
            lid = [(cx - w / 2, top), (cx + w / 2, top), (cx + w * .46, top - h * .9), (cx - w * .46, top - h * .9)]
            p.shape(lid, WHITE, w=5, amp=.4)
            ly = top - h * .45
            p.poly([(cx - h * .06, ly - h * .2), (cx + h * .06, ly - h * .2), (cx + h * .06, ly + h * .2), (cx - h * .06, ly + h * .2)], RED)
            p.poly([(cx - h * .2, ly - h * .06), (cx + h * .2, ly - h * .06), (cx + h * .2, ly + h * .06), (cx - h * .2, ly + h * .06)], RED)
        box = rrect(cx - w / 2, top, cx + w / 2, base, w * .05)
        p.shape(box, WHITE, w=6, amp=.4)
        if open:
            p.shape(rrect(cx - w * .46, top + h * .08, cx + w * .46, base - h * .1, 3), (236, 236, 240), w=3, amp=.2)
            for k in (-1, 1): p.stroke([(cx + k * w * .15, top + h * .08), (cx + k * w * .15, base - h * .1)], 3, GRAY, amp=.1)
            for k in range(2): p.shape(ellipse(cx - w * .3, top + h * (.3 + k * .32), w * .1, h * .13, n=20), (250, 244, 230), w=3, amp=.2)
            p.shape(rrect(cx - w * .08, top + h * .2, cx + w * .08, base - h * .2, 4), (220, 140, 50), w=3, amp=.2)
            p.poly(rrect(cx - w * .08, top + h * .2, cx + w * .08, top + h * .3, 3), WHITE)
            for k in range(3): p.shape(rotated(rrect(cx + w * .2, top + h * (.22 + k * .18), cx + w * .42, top + h * (.32 + k * .18), 6), cx + w * .31, top + h * (.27 + k * .18), .2), (240, 200, 160), w=2.5, amp=.1)
        else:
            p.stroke(spline([(cx - w * .16, top), (cx - w * .14, top - h * .2), (cx + w * .14, top - h * .2), (cx + w * .16, top)]), w * .04, DARK, amp=.2)
            p.stroke([(cx - w / 2, top + h * .2), (cx + w / 2, top + h * .2)], 3, GRAY, amp=.2)
            ly = top + h * .58
            p.poly([(cx - h * .09, ly - h * .28), (cx + h * .09, ly - h * .28), (cx + h * .09, ly + h * .28), (cx - h * .09, ly + h * .28)], RED)
            p.poly([(cx - h * .28, ly - h * .09), (cx + h * .28, ly - h * .09), (cx + h * .28, ly + h * .09), (cx - h * .28, ly + h * .09)], RED)

def _flashlight(p, gx, gy, L, ang, on=True):
    dx, dy = _dir(ang)
    P = lambda a, b: (gx + dx * a * L - dy * b * L, gy + dy * a * L + dx * b * L)
    if on:
        p.poly([P(.6, -.14), P(2.6, -.75), P(2.6, .75), P(.6, .14)], LIGHT)
    p.shape([P(-.35, -.09), P(.35, -.09), P(.42, -.16), P(.62, -.17), P(.62, .17), P(.42, .16), P(.35, .09), P(-.35, .09)], (60, 64, 74), w=max(3, L * .03), amp=.3)
    p.shape([P(.6, -.15), P(.66, -.15), P(.66, .15), P(.6, .15)], YELLOW if on else GRAY_L, w=max(2, L * .02), amp=.1)
    p.shape([P(.05, -.12), P(.17, -.12), P(.17, -.08), P(.05, -.08)], RED, w=2, amp=0)
    for k in range(3): p.stroke([P(-.3 + k * .08, -.09), P(-.3 + k * .08, .09)], max(2, L * .012), GRAY, amp=0)

def flashlight(img, gx, gy, L=200, ang=math.pi / 2, on=True, seed=1):
    """Flashlight held at (gx, gy) pointing towards ang (π/2 = right); on=True draws the light beam."""
    with Pen(img, (gx - L * 3, gy - L * 3, gx + L * 3, gy + L * 3), seed) as p: _flashlight(p, gx, gy, L, ang, on)

def cot(img, cx, base, w=420, blanket=OLIVE, seed=1, shadow=False):
    """Folding camp bed with a pillow and a blanket."""
    h = w * .3
    with Pen(img, (cx - w * .6, base - h * 1.2, cx + w * .6, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .5, w * .03)
        top = base - h * .6
        for xx in (cx - w * .35, cx + w * .35):
            p.stroke([(xx - w * .08, base), (xx + w * .08, top)], 5, STEEL_D, amp=.2)
            p.stroke([(xx + w * .08, base), (xx - w * .08, top)], 5, STEEL_D, amp=.2)
        p.shape(rrect(cx - w * .48, top - h * .14, cx + w * .48, top + h * .06, 6), (160, 150, 120), w=5, amp=.4)
        p.shape(spline([(cx - w * .46, top - h * .14), (cx - w * .46, top - h * .42), (cx - w * .26, top - h * .48), (cx - w * .26, top - h * .14)], closed=True), WHITE, w=4, amp=.3)
        bl = [(cx - w * .2, top - h * .12), (cx - w * .18, top - h * .38), (cx + w * .46, top - h * .32), (cx + w * .5, top + h * .12), (cx - w * .22, top + h * .1)]
        p.shape(bl, blanket, w=5, amp=.5)
        for k in range(1, 4): p.stroke([(cx - w * .19 + w * .16 * k, top - h * .33), (cx - w * .2 + w * .16 * k, top + h * .1)], 3, _shade(blanket), amp=.3)

def trash_bin(img, cx, base, h=240, lid=True, color=GRAY, seed=1, shadow=False):
    """Trash bin with a lid (lid=False leaves it open with a bag sticking out)."""
    w = h * .7
    with Pen(img, (cx - w * .7, base - h * 1.25, cx + w * .7, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .05)
        top = base - h * .88
        if not lid: p.shape(bumpy([(cx - w * .2, top - h * .02, w * .2), (cx + w * .15, top - h * .04, w * .22)], n=30), DARK, w=4, amp=.5)
        body = [(cx - w * .45, top), (cx + w * .45, top), (cx + w * .38, base), (cx - w * .38, base)]
        p.shape(body, color, w=6)
        for k in (-.2, 0, .2): p.stroke([(cx + w * k, top + h * .1), (cx + w * k * .9, base - h * .08)], 3, _shade(color), amp=.2)
        if lid:
            p.shape(rrect(cx - w * .5, top - h * .1, cx + w * .5, top + h * .02, 5), _shade(color, .85), w=5, amp=.3)
            p.shape(rrect(cx - w * .12, top - h * .16, cx + w * .12, top - h * .1, 3), DARK, w=3, amp=.1)

def flies(img, cx, cy, r=80, n=4, t=0.0, seed=1):
    """A few flies buzzing around (cx, cy) inside radius r; they move with t."""
    rng = random.Random(seed)
    with Pen(img, (cx - r * 1.3, cy - r * 1.3, cx + r * 1.3, cy + r * 1.3), seed) as p:
        for k in range(n):
            ph, sp, rr = rng.uniform(0, 6.3), rng.uniform(1.5, 3), rng.uniform(.4, 1) * r
            a = ph + t * sp
            fx, fy = cx + math.cos(a) * rr, cy + math.sin(a * 1.7) * rr * .6
            trail = [(cx + math.cos(a - u) * rr, cy + math.sin((a - u) * 1.7) * rr * .6) for u in (.15, .3, .45, .6)]
            for j in range(0, 3, 2): p.stroke(trail[j:j + 2], 2, GRAY, amp=0)
            for sd in (-1, 1): p.shape(ellipse(fx + sd * 5, fy - 6, 6, 4, rot=sd * .6, n=10), (230, 240, 250), w=1.5, amp=0)
            p.poly(ellipse(fx, fy, 5, 4, n=10), INK)

def trash_pile(img, cx, base, w=260, flies_=True, t=0.0, seed=1):
    """Pile of trash bags, empty cans and wrappers in a corner; flies_=True adds flies buzzing over it."""
    rng = random.Random(seed)
    with Pen(img, (cx - w * .6, base - w * .7, cx + w * .6, base + 8), seed) as p:
        for k, (dx, r, c) in enumerate(((-.25, .2, DARK), (.18, .24, (70, 80, 70)), (-.02, .17, DARK))):
            bx, by = cx + w * dx, base - w * r * .8 - (w * .12 if k == 2 else 0)
            bag = bumpy([(bx, by, w * r), (bx, by - w * r * .7, w * r * .45)], n=30)
            bag = [(x_, min(y_, base)) for x_, y_ in bag]
            p.shape(bag, c, w=4.5, amp=.6)
            p.stroke([(bx - w * .04, by - w * r * 1.1), (bx + w * .04, by - w * r * 1.25)], 3, GRAY, amp=.2)
        for k in range(3):
            x_ = cx + w * rng.uniform(-.45, .45)
            p.shape(rotated(rrect(x_ - w * .04, base - w * .1, x_ + w * .04, base, 2), x_, base - w * .05, 1.4), TIN, w=3, amp=.2)
        p.shape([(cx + w * .3, base), (cx + w * .38, base - w * .05), (cx + w * .46, base - w * .01)], YELLOW, w=3, amp=.3)
    if flies_: flies(img, cx, base - w * .65, w * .35, 4, t, seed)

def garden_bed(img, cx, base, w=420, growth=1.0, seed=1, shadow=False):
    """Raised wooden garden bed; growth = 0 seeds, .3 sprouts, .6 leafy plants, 1 plants with tomatoes."""
    h = w * .18
    with Pen(img, (cx - w * .6, base - w * .7, cx + w * .6, base + w * .05), seed) as p:
        if shadow: p.blob(cx, base, w * .55, w * .03)
        top = base - h
        n = 5
        for k in range(n):
            px = cx - w * .4 + w * .8 * k / (n - 1)
            g = max(0.0, min(1.0, growth))
            if g < .15:
                p.poly(ellipse(px, top - 4, 5, 3, n=8), (110, 80, 50))
                continue
            ph = w * (.06 + .32 * g)
            p.stroke(spline([(px, top), (px + 3, top - ph * .5), (px, top - ph)]), 4, LEAF_D, amp=.3)
            for j in range(1 + int(g * 3)):
                ly = top - ph * (.3 + .6 * j / max(1, int(g * 3)))
                sd = 1 if j % 2 else -1
                leaf = ellipse(px + sd * ph * .12, ly, ph * .11 + 6, ph * .05 + 3, rot=sd * -.5, n=14)
                p.shape(leaf, SPROUT if g < .5 else LEAF, w=2.5, amp=.2)
            if g >= .9:
                for j in (-1, 1): p.shape(ellipse(px + j * ph * .12, top - ph * .45, w * .025, w * .025, n=14), RED, w=2.5, amp=.2)
        p.shape([(cx - w * .5, top), (cx + w * .5, top), (cx + w * .5, base), (cx - w * .5, base)], WOOD, w=6)
        p.poly([(cx - w * .48, top - 6), (cx + w * .48, top - 6), (cx + w * .48, top + 4), (cx - w * .48, top + 4)], TOPSOIL)
        p.stroke([(cx - w * .5, top + h * .5), (cx + w * .5, top + h * .5)], 3, WOOD_D, amp=.5)

# ---------- maps and plans ----------
def _paper(p, x0, y0, x1, y1, color=PAPER, folds=0, ang=0.0):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = lambda pts: rotated(pts, cx, cy, ang)
    p.shape(R([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), color, w=5, amp=.5)
    for k in range(1, folds + 1):
        xx = x0 + (x1 - x0) * k / (folds + 1)
        p.stroke(R([(xx, y0 + 3), (xx, y1 - 3)]), 2, PAPER_D, amp=.4)
    return R

def _paper_map(p, cx, cy, w, h, spots, route, mark, ang):
    rng = random.Random(int(w + h))
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    R = _paper(p, x0, y0, x1, y1, (246, 240, 214), folds=2, ang=ang)
    M = lambda fx, fy: (x0 + w * fx, y0 + h * fy)
    p.stroke(R(spline([M(.05, .1), M(.3, .3), M(.25, .6), M(.4, .95)])), max(3, w * .02), WATER_D, amp=.4)
    p.stroke(R(spline([M(0, .7), M(.4, .55), M(.7, .6), M(1, .4)])), max(3, w * .015), (200, 120, 60), amp=.4)
    for k in range(int(w / 40)):
        q = M(rng.uniform(.55, .95), rng.uniform(.08, .35))
        p.shape(R(ellipse(*q, w * .025, w * .025, n=10)), LEAF, w=2, amp=.1)
    for k in range(3):
        q = M(.12 + k * .08, .82)
        p.stroke(R([(q[0] - w * .04, q[1]), (q[0], q[1] - h * .08), (q[0] + w * .04, q[1])]), 3, WOOD_D, amp=.2)
    if route:
        pts = [M(*f) for f in route]
        for a, b in zip(pts, pts[1:]):
            L = math.dist(a, b); n = max(1, int(L / 16))
            for k in range(0, n, 2):
                p.stroke(R([(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n), (a[0] + (b[0] - a[0]) * (k + 1) / n, a[1] + (b[1] - a[1]) * (k + 1) / n)]), 4, RED, amp=0)
    for fx, fy, *lab in spots:
        q = R([M(fx, fy)])[0]
        pin = spline([(q[0], q[1]), (q[0] - w * .03, q[1] - w * .05), (q[0], q[1] - w * .08), (q[0] + w * .03, q[1] - w * .05)], closed=True)
        p.shape(pin, RED, w=3, amp=.2)
        p.poly(ellipse(q[0], q[1] - w * .055, w * .01, w * .01, n=8), WHITE)
        if lab: p.text(str(lab[0]), q[0], q[1] - w * .12, _fit(str(lab[0]), w * .06, w * .3), warp=0)
    if mark:
        q = R([M(*mark)])[0]; r = w * .04
        p.stroke([(q[0] - r, q[1] - r), (q[0] + r, q[1] + r)], 6, RED, amp=.2)
        p.stroke([(q[0] + r, q[1] - r), (q[0] - r, q[1] + r)], 6, RED, amp=.2)

def paper_map(img, cx, cy, w=520, h=380, spots=(), route=None, mark=None, ang=0.0, seed=1):
    """Hand-drawn folded paper map with a river, a road, woods and hills. spots = [(fx, fy, "label"), …] red pins
    at fractions of the map; route = [(fx, fy), …] dashed red path; mark = (fx, fy) for a big red X."""
    with Pen(img, (cx - w * .75, cy - h * .9, cx + w * .75, cy + h * .9), seed) as p:
        _paper_map(p, cx, cy, w, h, spots, route, mark, ang)

def plan_sheet(img, cx, cy, w=480, title=None, ang=-.04, seed=1):
    """Blueprint sheet unrolled on a table: rooms drawn in white lines with dimension marks, rolled ends, title."""
    h = w * .66
    with Pen(img, (cx - w * .7, cy - h * .8, cx + w * .7, cy + h * .8), seed) as p:
        x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
        R = _paper(p, x0, y0, x1, y1, (70, 120, 190), ang=ang)
        for xx in (x0, x1): p.shape(R(rrect(xx - w * .035, y0 - h * .03, xx + w * .035, y1 + h * .03, w * .03)), (90, 140, 205), w=4, amp=.3)
        M = lambda fx, fy: (x0 + w * fx, y0 + h * fy)
        L = (230, 240, 255)
        p.stroke(R([M(.15, .2), M(.85, .2), M(.85, .8), M(.15, .8)]), 5, L, amp=.3, closed=True)
        p.stroke(R([M(.5, .2), M(.5, .55)]), 3.5, L, amp=.2)
        p.stroke(R([M(.15, .55), M(.38, .55)]), 3.5, L, amp=.2)
        p.stroke(R([M(.62, .55), M(.85, .55)]), 3.5, L, amp=.2)
        p.stroke(R([M(.15, .9), M(.85, .9)]), 2.5, L, amp=.1)
        for fx in (.15, .85): p.stroke(R([M(fx, .87), M(fx, .93)]), 2.5, L, amp=0)
        p.stroke(R([M(.9, .2), M(.9, .8)]), 2.5, L, amp=.1)
        for fy in (.2, .8): p.stroke(R([M(.88, fy), M(.92, fy)]), 2.5, L, amp=0)
        p.stroke(R(ellipse(*M(.3, .38), w * .04, w * .04, n=16)), 2.5, L, amp=.1, closed=True)
        if title: p.text(title, *R([M(.5, .1)])[0], _fit(title, h * .08, w * .6), fill=WHITE, warp=0)

def floor_plan(img, x0, y0, x1, y1, zones=(), wall=10, seed=1):
    """Room seen from above with zones: zones = [("label", (fx0, fy0, fx1, fy1), color), …] in fractions of the
    room; each zone is filled with its color, outlined with a dashed line and labelled. Thick outer walls."""
    w, h = x1 - x0, y1 - y0
    with Pen(img, (x0 - wall * 2, y0 - wall * 2, x1 + wall * 2, y1 + wall * 2), seed) as p:
        p.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], ROOM)
        boxes, size = [], 44.0
        for label, (fx0, fy0, fx1, fy1), *col in zones:
            zx0, zy0, zx1, zy1 = x0 + w * fx0, y0 + h * fy0, x0 + w * fx1, y0 + h * fy1
            words = str(label).split()
            lines = [" ".join(words[:(len(words) + 1) // 2]), " ".join(words[(len(words) + 1) // 2:])] if len(label) > 10 and len(words) > 1 else [str(label)]
            size = min(size, _fit(max(lines, key=len), 44, (zx1 - zx0) * .82), (zy1 - zy0) * .7 / len(lines))
            boxes.append((zx0, zy0, zx1, zy1, lines, col[0] if col else GREEN_L))
        for zx0, zy0, zx1, zy1, lines, col in boxes:
            zone = [(zx0 + 6, zy0 + 6), (zx1 - 6, zy0 + 6), (zx1 - 6, zy1 - 6), (zx0 + 6, zy1 - 6)]
            p.poly(p.wobble(zone, .6, True), col)
            for a, b in zip(zone, zone[1:] + zone[:1]):
                L = math.dist(a, b); n = max(1, int(L / 18))
                for k in range(0, n, 2):
                    p.stroke([(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n), (a[0] + (b[0] - a[0]) * (k + 1) / n, a[1] + (b[1] - a[1]) * (k + 1) / n)], 3, DARK, amp=0)
            for k, ln in enumerate(lines):
                p.text(ln, (zx0 + zx1) / 2, (zy0 + zy1) / 2 + (k - (len(lines) - 1) / 2) * size * 1.15, size, warp=0)
        p.stroke([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], wall, DARK, amp=.6, closed=True, taper=False)

def site_plan(img, x0, y0, x1, y1, fence=True, clear=True, bunker=True, trees=True, road=True, garden=False, panels=False, seed=1):
    """Plot of land seen from above, like a hand-drawn plan: dashed boundary, fence ring with posts, cleared zone
    around a bunker in the middle, trees outside, access road; garden=True and panels=True add a garden patch and
    solar panels."""
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rng = random.Random(seed)
    with Pen(img, (x0 - 20, y0 - 20, x1 + 20, y1 + 20), seed) as p:
        p.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], (214, 230, 176))
        if road:
            p.limb([(cx + w * .08, y1 - 14), (cx + w * .06, cy + h * .3), (cx, cy + h * .18)], w * .07, (220, 205, 170), 3)
        if trees:
            for k in range(int(w * h / 14000)):
                tx, ty = rng.uniform(x0 + 20, x1 - 20), rng.uniform(y0 + 20, y1 - 20)
                if abs(tx - cx) < w * .36 and abs(ty - cy) < h * .36: continue
                r = rng.uniform(14, 24)
                p.shape(bumpy([(tx, ty, r), (tx + r * .5, ty + r * .3, r * .7), (tx - r * .5, ty + r * .2, r * .7)], n=24), LEAF, w=3, amp=.3)
        if clear:
            cz = rrect(cx - w * .3, cy - h * .3, cx + w * .3, cy + h * .3, 20)
            p.poly(p.wobble(cz, .6, True), (236, 228, 196))
        if fence:
            fr = [(cx - w * .34, cy - h * .34), (cx + w * .34, cy - h * .34), (cx + w * .34, cy + h * .34), (cx - w * .34, cy + h * .34)]
            p.stroke(fr, 5, STEEL_D, amp=.6, closed=True, taper=False)
            for a, b in zip(fr, fr[1:] + fr[:1]):
                for k in range(8):
                    q = (a[0] + (b[0] - a[0]) * k / 8, a[1] + (b[1] - a[1]) * k / 8)
                    p.shape(rrect(q[0] - 6, q[1] - 6, q[0] + 6, q[1] + 6, 2), DARK, w=2, amp=0)
        if bunker:
            p.shape(rrect(cx - w * .13, cy - h * .1, cx + w * .13, cy + h * .1, 6), CONCRETE, w=5, amp=.4)
            p.hatch(rrect(cx - w * .13, cy - h * .1, cx + w * .13, cy + h * .1, 6), CONCRETE_D, gap=14, w=2)
            p.shape(ellipse(cx + w * .09, cy - h * .06, w * .018, w * .018, n=14), STEEL, w=3, amp=.1)
        if garden:
            g = [(cx - w * .27, cy + h * .14), (cx - w * .16, cy + h * .14), (cx - w * .16, cy + h * .26), (cx - w * .27, cy + h * .26)]
            p.shape(g, TOPSOIL, w=3, amp=.3)
            for k in range(3): p.stroke([(cx - w * .26, cy + h * (.17 + k * .035)), (cx - w * .17, cy + h * (.17 + k * .035))], 3, SPROUT, amp=.2)
        if panels:
            for k in range(3):
                px = cx + w * (.12 + k * .055)
                p.shape([(px, cy + h * .16), (px + w * .045, cy + h * .16), (px + w * .045, cy + h * .26), (px, cy + h * .26)], PANEL, w=3, amp=.2)
        p.stroke([(x0 + 10, y0 + 10), (x1 - 10, y0 + 10), (x1 - 10, y1 - 10), (x0 + 10, y1 - 10)], 3, RED_D, amp=.4, closed=True, taper=False)

from . import cache_pieces
cache_pieces(globals())
