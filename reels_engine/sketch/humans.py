"""Sketch-style base character ('doodle'): big round head, stick legs and a simple outfit (hoodie, shirt and tie,
or t-shirt). Dress it with 'extras' to build other characters without redrawing the body.

    a = doodle(img, 540, FLOOR, 1.0, outfit="tie", mood="smug", arms=("hip", "offer"), look=.5)
    bill(img, *a["hand_r"], 120)

(x, y) = point on the floor between the feet. At scale 1 it's about 610 px tall."""
from . import Pen, INK, WHITE, SHADE, SKIN_SHADE, RED, MOUTH, ellipse, spline

OUTFITS = ("hoodie", "tie", "tshirt")
# arm poses for the arm on the right of the screen, as (elbow, hand) offsets from the shoulder; mirrored for the left
ARMS = {
    "down": ((14, 95), (20, 185)),
    "hip": ((66, 70), (24, 150)),
    "up": ((48, -70), (40, -170)),
    "hold": ((26, 100), (-28, 120)),
    "show": ((40, 105), (-5, 45)),
    "offer": ((40, 95), (120, 70)),
    "shrug": ((60, 90), (125, 40)),
    "head": ((95, -30), (40, -110)),
    "point": ((70, 15), (165, -25)),
    "chin": ((40, 105), (-30, 0)),
}
# brows: (inner, outer) height of each brow (left, right on screen); mouth; how low the pupils look
MOODS = {
    "happy": (((-.04, 0), (-.04, 0)), "grin", 0),
    "smile": (((-.02, 0), (-.02, 0)), "smile", 0),
    "smug": (((.06, -.02), (-.06, -.12)), "smirk", 0),
    "shocked": (((-.14, -.08), (-.14, -.08)), "O", -.02),
    "worried": (((-.12, .03), (-.12, .03)), "wavy", .04),
    "angry": (((.09, -.05), (.09, -.05)), "frown", 0),
    "sad": (((-.1, .04), (-.1, .04)), "frown", .06),
    "doubt": (((.07, -.02), (-.04, -.1)), "flat", 0),
}
MARKS = ("excited", "?", "!", "sweat")

def doodle_anchors(x, y, s=1.0, arms=("down", "down"), look=0.0):
    """Body points of doodle (head, mouth, hands…) to place bubbles and objects on it."""
    if isinstance(arms, str): arms = (arms, arms)
    hx, hy, r = x + look * 8 * s, y - 512 * s, 92 * s
    shoulders, elbows, hands = [], [], []
    for side, kind in zip((-1, 1), arms):
        (ex, ey), (px, py) = ARMS[kind]
        sh = (x + 44 * side * s, y - 402 * s)
        shoulders.append(sh)
        elbows.append((sh[0] + ex * side * s, sh[1] + ey * s))
        hands.append((sh[0] + px * side * s, sh[1] + py * s))
    return {"head": (hx, hy), "head_r": r, "head_top": (hx, hy - r), "mouth": (hx + look * .16 * r, hy + .4 * r),
            "chest": (x, y - 360 * s), "hip": (x, y - 245 * s), "feet": (x, y), "hand_l": hands[0], "hand_r": hands[1],
            "shoulders": shoulders, "elbows": elbows,
            "box": (x - 270 * s, y - 760 * s, x + 270 * s, y + 20 * s)}

def _face(p, cx, cy, r, mood, look):
    brows, mouth, pdy = MOODS[mood]
    fx = cx + look * .16 * r
    for i, side in enumerate((-1, 1)):
        ex, ey, rx, ry = fx + side * .27 * r, cy - .05 * r, .17 * r, .24 * r
        p.shape(ellipse(ex, ey, rx, ry, n=28), WHITE, w=.05 * r, amp=.6)
        pr = .05 * r if mood == "shocked" else .085 * r
        p.poly(ellipse(ex + look * .06 * r, ey + (pdy + .03) * r, pr, pr * 1.35, n=16), INK)
        if (mood in ("smug", "doubt") and side == -1) or mood == "angry":          # heavy eyelid
            p.stroke([(ex - rx * 1.1, ey - ry * .25), (ex + rx * 1.1, ey - ry * .15)], .045 * r, amp=.4)
        inner, outer = brows[i]
        by = ey - .4 * r
        bi, bo = (ex - side * .06 * r, by + inner * r), (ex + side * .2 * r, by + outer * r)
        p.stroke(spline([bi, ((bi[0] + bo[0]) / 2, min(bi[1], bo[1]) - .035 * r), bo]), .07 * r, amp=.5)
    mx, my = fx, cy + .4 * r
    M = lambda pts: spline([(mx + dx * r, my + dy * r) for dx, dy in pts])
    if mouth == "grin":
        pts = M([(-.33, -.06), (0, -.02), (.33, -.06)])[:-1] + M([(.33, -.06), (.18, .2), (0, .26), (-.18, .2), (-.33, -.06)])
        p.poly(pts, MOUTH)
        with p.clip(pts):
            p.poly([(mx - .4 * r, my - .2 * r), (mx + .4 * r, my - .2 * r), (mx + .4 * r, my + .06 * r), (mx - .4 * r, my + .06 * r)], WHITE)
        p.stroke(pts, .05 * r, amp=.6, closed=True)
    elif mouth == "O":
        p.shape(ellipse(mx, my + .06 * r, .12 * r, .16 * r, n=24), MOUTH, w=.05 * r, amp=.6)
    else:
        pts = {"smile": [(-.22, -.02), (0, .1), (.22, -.02)], "smirk": [(-.2, .04), (.05, .06), (.25, -.06)],
               "frown": [(-.18, .08), (0, -.02), (.18, .08)], "flat": [(-.15, .04), (.15, .02)],
               "wavy": [(-.2, .05), (-.1, 0), (0, .05), (.1, 0), (.2, .05)]}[mouth]
        p.stroke(M(pts), .055 * r, amp=.4)

def _head(p, cx, cy, r, mood, look):
    pts = ellipse(cx, cy, r, r * 1.02, n=64)
    p.poly(p.wobble(pts, .8, True), WHITE)
    with p.clip(pts):                                         # soft grey crescent on the shadow side
        p.poly(ellipse(cx + .5 * r, cy + .45 * r, r * .95, r * .9), SKIN_SHADE)
        p.poly(ellipse(cx + .28 * r, cy + .2 * r, r * .95, r * .95), WHITE)
    p.stroke(pts, .1 * r, amp=1.2, closed=True)
    _face(p, cx, cy, r, mood, look)

def doodle(img, x, y, s=1.0, outfit="hoodie", mood="happy", arms=("down", "down"), look=0.0, color=RED, tie=INK,
           legs=True, shadow=True, dress=None, hat=None, extras=None, seed=1):
    """Sketch-style character. outfit: hoodie, tie (white shirt + tie) or tshirt; 'color' = hoodie/t-shirt color.
    arms = one pose or (left, right): down, hip, up, hold, show, offer, shrug, head, point, chin.
    mood: happy, smile, smug, shocked, worried, angry, sad, doubt. look: -1 (left) … 1 (right).
    Hooks (p = Pen, a = body points): dress(p, a) over the torso and under the head and arms (armor, robes, belts),
    hat(p, a) right after the head (helmets, beards, wreaths), extras(p, a) at the very end. Returns the body points."""
    a = doodle_anchors(x, y, s, arms, look)
    P = lambda dx, dy: (x + dx * s, y + dy * s)
    with Pen(img, a["box"], seed) as p:
        if shadow and legs: p.blob(*P(0, 2), 95 * s, 14 * s, SHADE)
        if legs:
            for side in (-1, 1):
                foot = P(30 * side, -6)
                p.stroke(spline([P(18 * side, -250), P(25 * side + look * 6, -125), foot]), 12 * s, amp=1.2)
                p.stroke([foot, P(30 * side + 30 * (look or side), -4)], 13 * s, amp=.6)
        shirt = WHITE if outfit == "tie" else color
        if outfit == "hoodie":
            body = [P(-52, -418), P(52, -418), P(66, -330), P(62, -232), P(-62, -232), P(-66, -330)]
            p.shape(body, color, w=8 * s, smooth=True)
            dark = tuple(int(v * .7) for v in color)
            p.stroke([P(-58, -258), P(58, -258)], 4 * s, dark, amp=1)
            p.stroke([P(-36, -312), P(-30, -268), P(30, -268), P(36, -312)], 4 * s, dark, amp=1)
        else:
            body = [P(-44, -418), P(44, -418), P(54, -330), P(50, -238), P(-50, -238), P(-54, -330)]
            p.shape(body, shirt, w=7.5 * s, smooth=True)
            p.stroke([P(-50, -246), P(50, -246)], 8 * s, amp=.8)
            if outfit == "tie":
                p.shape([P(-8, -404), P(8, -404), P(14, -300), P(0, -280), P(-14, -300)], tie, w=3 * s, amp=.6)
                p.shape([P(-26, -420), P(0, -398), P(-10, -386)], WHITE, w=4 * s, amp=.5)
                p.shape([P(26, -420), P(0, -398), P(10, -386)], WHITE, w=4 * s, amp=.5)
                p.shape([P(-9, -408), P(9, -408), P(6, -394), P(-6, -394)], tie, w=3 * s, amp=.3)
            else:
                p.stroke(spline([P(-22, -418), P(0, -400), P(22, -418)]), 5 * s, amp=.5)
        if dress: dress(p, a)
        (hx, hy), r = a["head"], a["head_r"]
        if outfit == "hoodie":                                 # the hood, behind the head
            p.shape(ellipse(hx - look * 10 * s, y - 432 * s, 70 * s, 38 * s, n=36), color, w=7 * s)
        _head(p, hx, hy, r, mood, look)
        if hat: hat(p, a)
        if outfit == "hoodie":
            for side in (-1, 1): p.stroke([P(14 * side, -414), P(16 * side, -372)], 4 * s, amp=.5)
        for sh, el, hd in zip(a["shoulders"], a["elbows"], (a["hand_l"], a["hand_r"])):
            if outfit == "hoodie": p.limb([sh, el, hd], 30 * s, color, 5 * s)
            else: p.limb([sh, el, hd], 20 * s, shirt, 4.5 * s)
            p.shape(ellipse(hd[0], hd[1], 14 * s, 14 * s, n=20), WHITE, w=5 * s, amp=.6)
        if extras: extras(p, a)
    return a

def marks(img, head, r, kind="excited", seed=1):
    """Little extras around a head: excited ticks, '?', '!' or a sweat drop. head = a["head"], r = a["head_r"]."""
    import math
    cx, cy = head
    s = r / 92
    with Pen(img, (cx - r * 1.7, cy - r * 1.9, cx + r * 1.9, cy + r * .3), seed) as p:
        if kind == "excited":
            for ang in (-2.4, -2.0, -1.6, -1.15, -.75):
                c, sn = math.cos(ang), math.sin(ang)
                p.stroke([(cx + c * r * 1.2, cy + sn * r * 1.2), (cx + c * r * 1.45, cy + sn * r * 1.45)], 5 * s, amp=.4)
        elif kind in ("?", "!"):
            p.text(kind, cx + r * 1.15, cy - r * .9, 70 * s, warp=1)
        elif kind == "sweat":
            px, py = cx + r * .95, cy - r * .45
            p.shape([(px, py - 22 * s), (px + 12 * s, py + 4 * s), (px, py + 14 * s), (px - 12 * s, py + 4 * s)],
                    (150, 200, 240), w=4 * s, smooth=True, amp=.4)

from . import cache_pieces
cache_pieces(globals())
