"""Cartoon-style base character ('buddy', the one under the caveman): round head, torso and stick limbs.
Dress it with 'dress' and 'extras' to build other characters without redrawing the body.

    def tunic(p, a): p.polygon(..., (123, 86, 56))       # p = Brush, a = body points
    a = buddy(img, 540, FLOOR, 1.0, pose="sitting", hair="bangs", dress=tunic)

(x, y) = point on the floor between the feet. At scale 1 it's about 770 px tall standing."""
import math
from ..base import WHITE
from . import Brush, INK, quad, seeded

HAIR = (91, 63, 44)
POSES = ("standing", "sitting")
ARMS = ("down", "up", "hips", "wave", "point", "think", "behind")
MOODS = ("happy", "neutral", "sad", "surprised", "angry", "laugh", "asleep")
HAIRS = ("none", "bangs", "short")
ONE_HAND = ("wave", "point", "think")

def _arm(side, kind, sh, t, s):
    """Points of one arm (side=-1 left on screen, 1 right) from the shoulder sh."""
    x, y = sh; S = lambda dx, dy: (x + side * dx * s, y + dy * s)
    if kind == "up": return quad(sh, S(85, -50), S(105, -190), 12)
    if kind == "hips": return [sh, S(85, 100), S(12, 190)]
    if kind == "wave":
        a = math.radians(-65 + 18 * math.sin(t * 9))
        el = S(90, -40); return [sh, el, (el[0] + side * math.cos(a) * 120 * s, el[1] + math.sin(a) * 120 * s)]
    if kind == "point": return [sh, S(110, -10), S(225, -25)]
    if kind == "think": return [sh, S(55, 85), S(-40, -22)]
    if kind == "behind": return quad(sh, S(-10, 110), S(-55, 205), 12)
    return quad(sh, S(55, 100), S(60, 215), 12)                        # down

def buddy_anchors(x, y, s=1.0, pose="standing", arms="down", t=0.0):
    """Body points of buddy (head, mouth, hands, chest…) to place bubbles and objects on it."""
    S = lambda dx, dy: (x + dx * s, y + dy * s)
    sit = pose == "sitting"
    hip = S(0, -60) if sit else S(0, -290)
    top = hip[1] - 270 * s
    hx, hy = x, top - 85 * s
    R = 100 * s
    torso = [(x - 22 * s, top), (x + 22 * s, top), (x + 52 * s, top + 45 * s), (x + 58 * s, hip[1]),
             (x - 58 * s, hip[1]), (x - 52 * s, top + 45 * s)]
    if isinstance(arms, str): al, ar = ("down", arms) if arms in ONE_HAND else (arms, arms)
    else: al, ar = arms                                                   # one-hand gestures use the right hand
    limbs = [_arm(-1, al, (x - 46 * s, top + 35 * s), t, s), _arm(1, ar, (x + 46 * s, top + 35 * s), t, s)]
    if sit:
        legs = [[S(-28, -70), S(60, -235), S(140, -12), S(172, -12)], [S(28, -70), S(150, -95), S(265, -8), S(297, -8)]]
    else:
        legs = [[S(-28, -295), S(-42, -150), S(-55, -4), S(-88, -4)], [S(28, -295), S(42, -150), S(55, -4), S(88, -4)]]
    pts = [q for part in [torso] + limbs + legs for q in part] + [(hx - R * 1.15, hy - R * 1.15), (hx + R * 1.15, hy + R)]
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    return {
        "head": (hx, hy), "head_r": R, "head_top": (hx, hy - R), "eyes": (hx, hy - 15 * s), "mouth": (hx, hy + 30 * s),
        "neck": (x, top), "chest": (x, top + 80 * s), "belly": (x, top + 180 * s), "hip": hip, "feet": (x, y),
        "hand_l": limbs[0][-1], "hand_r": limbs[1][-1], "box": (min(xs), min(ys), max(xs), max(ys)),
        "torso": torso, "arms": limbs, "legs": legs,
    }

def _face(p, a, s, mood, look, t):
    hx, hy = a["head"]; S = lambda dx, dy: (hx + dx * s, hy + dy * s); ex = look * 8 * s
    blink = t and mood != "asleep" and (t % 3.2) < .12
    for side in (-1, 1):
        cx, cy = hx + side * 30 * s + ex, hy - 15 * s
        if mood == "asleep" or blink:
            p.polyline(quad((cx - 9 * s, cy), (cx, cy + (7 if mood == "asleep" else 0) * s), (cx + 9 * s, cy), 8), INK, 4 * s)
        elif mood == "surprised":
            p.ellipse(cx, cy - 3 * s, 9 * s, 13 * s, INK)
        else:
            p.ellipse(cx, cy, 7.5 * s, 10.5 * s, INK)
        if mood == "angry":                                               # brows: inner end down (angry) or up (sad)
            p.polyline([(cx - side * 14 * s, cy - 16 * s), (cx + side * 12 * s, cy - 26 * s)], INK, 4.5 * s)
        if mood == "sad":
            p.polyline([(cx - side * 12 * s, cy - 26 * s), (cx + side * 12 * s, cy - 18 * s)], INK, 4 * s)
    if mood == "happy": p.polyline(quad(S(-18, 24), S(0, 39), S(18, 24)), INK, 4.5 * s)
    elif mood == "sad": p.polyline(quad(S(-16, 38), S(0, 25), S(16, 38)), INK, 4.5 * s)
    elif mood == "surprised": p.ellipse(*S(0, 35), 9 * s, 12 * s, INK)
    elif mood == "laugh": p.polygon(quad(S(-22, 22), S(0, 58), S(22, 22), 12), INK, INK, 3 * s)
    elif mood == "angry": p.polyline([S(-14, 34), S(14, 31)], INK, 4.5 * s)
    elif mood == "asleep": p.ellipse(*S(4, 34), 5 * s, 6 * s, INK)
    else: p.polyline([S(-14, 32), S(14, 32)], INK, 4.5 * s)

def _hair(p, a, s, hair, color, seed):
    if hair == "none": return
    hx, hy = a["head"]; R = a["head_r"]; rng = seeded(seed)
    arc = [(hx + math.cos(math.radians(160 + 220 * i / 30)) * (R + 10 * s), hy + math.sin(math.radians(160 + 220 * i / 30)) * (R + 10 * s))
           for i in range(31)]
    x0, x1 = arc[-1][0], arc[0][0]
    if hair == "short":                                                   # smooth cap
        k = 1.0 / R
        bottom = [(x0 + (x1 - x0) * i / 12, hy - .55 * R + .55 * R * ((x0 + (x1 - x0) * i / 12 - hx) * k) ** 2) for i in range(1, 12)]
        p.polygon(arc + bottom, color, INK, 4.5 * s); return
    teeth, bangs = 13, list(arc)                                          # zigzag bangs
    for i in range(1, teeth * 2):
        bx = x0 + (x1 - x0) * i / (teeth * 2); dx = (bx - hx) / R
        bangs.append((bx, hy - .76 * R + 1.13 * R * dx * dx + ((.15 + rng() * .09) * R if i % 2 else -.02 * R)))
    p.polygon(bangs, color, INK, 4.5 * s)
    dark = tuple(int(v * .7) for v in color)
    for i in range(6):
        sx = hx - .56 * R + i * .2 * R + rng() * .07 * R
        p.polyline([(sx, hy - .86 * R + rng() * .09 * R), (sx - .05 * R + rng() * .11 * R, hy - .61 * R + rng() * .09 * R)], dark, 3.5 * s)

def buddy(img, x, y, s=1.0, pose="standing", arms="down", mood="happy", hair="none", look=0.0, t=0.0,
          skin=WHITE, shirt=WHITE, hair_color=HAIR, dress=None, extras=None, seed=7):
    """Cartoon buddy with ink outline. pose: standing|sitting; arms: down|up|hips|wave|point|think|behind (or (left, right));
    mood: happy|neutral|sad|surprised|angry|laugh|asleep; hair: none|bangs|short; look -1..1 = looks to one side;
    t = time (blinking and waving). dress(p, a) is drawn over the torso and under the arms; extras(p, a) at the end.
    Returns the body points (see buddy_anchors)."""
    a = buddy_anchors(x, y, s, pose, arms, t)
    bx0, by0, bx1, by1 = a["box"]; m = 40 * s
    with Brush(img, (bx0 - m, by0 - m, bx1 + m, by1 + m)) as p:
        for leg in a["legs"]: p.polyline(leg, INK, 6 * s)
        p.polygon(a["torso"], shirt, INK, 5 * s)
        if dress: dress(p, a)
        for arm in a["arms"]: p.polyline(arm, INK, 6 * s)
        p.circle(*a["head"], a["head_r"], skin, INK, 5 * s)
        _face(p, a, s, mood, look, t)
        _hair(p, a, s, hair, hair_color, seed)
        if extras: extras(p, a)
    return a
