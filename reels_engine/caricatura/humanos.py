"""Monito base del estilo caricatura (el que está debajo del cavernícola): cabeza redonda, torso y extremidades de
palito. Se viste con 'vestir' y 'accesorios' para armar otros personajes sin redibujar el cuerpo.

    def tunica(p, a): p.polygon(..., (123, 86, 56))      # p = Pincel, a = puntos del cuerpo
    a = monito(img, 540, FLOOR, 1.0, pose="sentado", pelo="fleco", vestir=tunica)

(x, y) = punto en el piso entre los pies. A escala 1 mide unos 770 px de alto parado."""
import math
from ..base import WHITE
from . import Pincel, INK, quad, semilla

HAIR = (91, 63, 44)
POSES = ("parado", "sentado")
BRAZOS = ("abajo", "arriba", "jarra", "saluda", "señala", "pensando", "atras")
MOODS = ("feliz", "neutral", "triste", "sorpresa", "enojado", "risa", "dormido")
PELOS = ("ninguno", "fleco", "corto")

def _arm(side, kind, sh, t, s):
    """Puntos de un brazo (side=-1 izquierdo en pantalla, 1 derecho) desde el hombro sh."""
    x, y = sh; S = lambda dx, dy: (x + side * dx * s, y + dy * s)
    if kind == "arriba": return quad(sh, S(85, -50), S(105, -190), 12)
    if kind == "jarra": return [sh, S(85, 100), S(12, 190)]
    if kind == "saluda":
        a = math.radians(-65 + 18 * math.sin(t * 9))
        el = S(90, -40); return [sh, el, (el[0] + side * math.cos(a) * 120 * s, el[1] + math.sin(a) * 120 * s)]
    if kind == "señala": return [sh, S(110, -10), S(225, -25)]
    if kind == "pensando": return [sh, S(55, 85), S(-40, -22)]
    if kind == "atras": return quad(sh, S(-10, 110), S(-55, 205), 12)
    return quad(sh, S(55, 100), S(60, 215), 12)                        # abajo

def monito_anchors(x, y, s=1.0, pose="parado", brazos="abajo", t=0.0):
    """Puntos del cuerpo del monito (cabeza, boca, manos, pecho…) para poner globos y objetos encima."""
    S = lambda dx, dy: (x + dx * s, y + dy * s)
    sit = pose == "sentado"
    hip = S(0, -60) if sit else S(0, -290)
    top = hip[1] - 270 * s
    hx, hy = x, top - 85 * s
    R = 100 * s
    torso = [(x - 22 * s, top), (x + 22 * s, top), (x + 52 * s, top + 45 * s), (x + 58 * s, hip[1]),
             (x - 58 * s, hip[1]), (x - 52 * s, top + 45 * s)]
    if isinstance(brazos, str): bl, br = ("abajo", brazos) if brazos in ("saluda", "señala", "pensando") else (brazos, brazos)
    else: bl, br = brazos                                                 # los gestos de una mano van con la derecha
    arms = [_arm(-1, bl, (x - 46 * s, top + 35 * s), t, s), _arm(1, br, (x + 46 * s, top + 35 * s), t, s)]
    if sit:
        legs = [[S(-28, -70), S(60, -235), S(140, -12), S(172, -12)], [S(28, -70), S(150, -95), S(265, -8), S(297, -8)]]
    else:
        legs = [[S(-28, -295), S(-42, -150), S(-55, -4), S(-88, -4)], [S(28, -295), S(42, -150), S(55, -4), S(88, -4)]]
    pts = [q for part in [torso] + arms + legs for q in part] + [(hx - R * 1.15, hy - R * 1.15), (hx + R * 1.15, hy + R)]
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    return {
        "head": (hx, hy), "head_r": R, "head_top": (hx, hy - R), "eyes": (hx, hy - 15 * s), "mouth": (hx, hy + 30 * s),
        "neck": (x, top), "chest": (x, top + 80 * s), "belly": (x, top + 180 * s), "hip": hip, "feet": (x, y),
        "hand_l": arms[0][-1], "hand_r": arms[1][-1], "box": (min(xs), min(ys), max(xs), max(ys)),
        "torso": torso, "arms": arms, "legs": legs,
    }

def _face(p, a, s, mood, look, t):
    hx, hy = a["head"]; S = lambda dx, dy: (hx + dx * s, hy + dy * s); ex = look * 8 * s
    blink = t and mood != "dormido" and (t % 3.2) < .12
    for side in (-1, 1):
        cx, cy = hx + side * 30 * s + ex, hy - 15 * s
        if mood == "dormido" or blink:
            p.polyline(quad((cx - 9 * s, cy), (cx, cy + (7 if mood == "dormido" else 0) * s), (cx + 9 * s, cy), 8), INK, 4 * s)
        elif mood == "sorpresa":
            p.ellipse(cx, cy - 3 * s, 9 * s, 13 * s, INK)
        else:
            p.ellipse(cx, cy, 7.5 * s, 10.5 * s, INK)
        if mood == "enojado":                                             # cejas: punta de adentro abajo (enojo) o arriba (tristeza)
            p.polyline([(cx - side * 14 * s, cy - 16 * s), (cx + side * 12 * s, cy - 26 * s)], INK, 4.5 * s)
        if mood == "triste":
            p.polyline([(cx - side * 12 * s, cy - 26 * s), (cx + side * 12 * s, cy - 18 * s)], INK, 4 * s)
    if mood == "feliz": p.polyline(quad(S(-18, 24), S(0, 39), S(18, 24)), INK, 4.5 * s)
    elif mood == "triste": p.polyline(quad(S(-16, 38), S(0, 25), S(16, 38)), INK, 4.5 * s)
    elif mood == "sorpresa": p.ellipse(*S(0, 35), 9 * s, 12 * s, INK)
    elif mood == "risa": p.polygon(quad(S(-22, 22), S(0, 58), S(22, 22), 12), INK, INK, 3 * s)
    elif mood == "enojado": p.polyline([S(-14, 34), S(14, 31)], INK, 4.5 * s)
    elif mood == "dormido": p.ellipse(*S(4, 34), 5 * s, 6 * s, INK)
    else: p.polyline([S(-14, 32), S(14, 32)], INK, 4.5 * s)

def _hair(p, a, s, pelo, color, seed):
    if pelo == "ninguno": return
    hx, hy = a["head"]; R = a["head_r"]; rng = semilla(seed)
    arc = [(hx + math.cos(math.radians(160 + 220 * i / 30)) * (R + 10 * s), hy + math.sin(math.radians(160 + 220 * i / 30)) * (R + 10 * s))
           for i in range(31)]
    x0, x1 = arc[-1][0], arc[0][0]
    if pelo == "corto":                                                   # casquete liso
        k = 1.0 / R
        bottom = [(x0 + (x1 - x0) * i / 12, hy - .55 * R + .55 * R * ((x0 + (x1 - x0) * i / 12 - hx) * k) ** 2) for i in range(1, 12)]
        p.polygon(arc + bottom, color, INK, 4.5 * s); return
    teeth, bangs = 13, list(arc)                                          # fleco en zigzag
    for i in range(1, teeth * 2):
        bx = x0 + (x1 - x0) * i / (teeth * 2); dx = (bx - hx) / R
        bangs.append((bx, hy - .76 * R + 1.13 * R * dx * dx + ((.15 + rng() * .09) * R if i % 2 else -.02 * R)))
    p.polygon(bangs, color, INK, 4.5 * s)
    dark = tuple(int(v * .7) for v in color)
    for i in range(6):
        sx = hx - .56 * R + i * .2 * R + rng() * .07 * R
        p.polyline([(sx, hy - .86 * R + rng() * .09 * R), (sx - .05 * R + rng() * .11 * R, hy - .61 * R + rng() * .09 * R)], dark, 3.5 * s)

def monito(img, x, y, s=1.0, pose="parado", brazos="abajo", mood="feliz", pelo="ninguno", look=0.0, t=0.0,
           piel=WHITE, ropa=WHITE, pelo_color=HAIR, vestir=None, accesorios=None, seed=7):
    """Monito caricatura con contorno de tinta. pose: parado|sentado; brazos: abajo|arriba|jarra|saluda|señala|pensando|atras
    (o (izq, der)); mood: feliz|neutral|triste|sorpresa|enojado|risa|dormido; pelo: ninguno|fleco|corto; look -1..1 = mira a un lado;
    t = tiempo (parpadeo y saludo). vestir(p, a) se dibuja sobre el torso y bajo los brazos; accesorios(p, a) al final.
    Devuelve los puntos del cuerpo (ver monito_anchors)."""
    a = monito_anchors(x, y, s, pose, brazos, t)
    bx0, by0, bx1, by1 = a["box"]; m = 40 * s
    with Pincel(img, (bx0 - m, by0 - m, bx1 + m, by1 + m)) as p:
        for leg in a["legs"]: p.polyline(leg, INK, 6 * s)
        p.polygon(a["torso"], ropa, INK, 5 * s)
        if vestir: vestir(p, a)
        for arm in a["arms"]: p.polyline(arm, INK, 6 * s)
        p.circle(*a["head"], a["head_r"], piel, INK, 5 * s)
        _face(p, a, s, mood, look, t)
        _hair(p, a, s, pelo, pelo_color, seed)
        if accesorios: accesorios(p, a)
    return a
