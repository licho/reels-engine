"""Piezas de exterior del estilo caricatura."""
import math
from . import Pincel, INK, quad, blob, teardrop, semilla

STONE, STONE_LIGHT, ASH, STICK = (167, 169, 174), (198, 200, 204), (110, 82, 54), (74, 52, 36)
FLAME = ((240, 128, 42), (249, 169, 58), (255, 216, 107))

def fogata(img, x, y, s=1.0, t=0.0, piedras=12, seed=7):
    """Fogata con llama animada (t en segundos) y anillo de piedras; (x, y) = centro de la ceniza."""
    rng = semilla(seed); S = lambda dx, dy: (x + dx * s, y + dy * s)
    back, front = [], []
    for i in range(piedras):
        a = 2 * math.pi * i / piedras + (rng() - .5) * .2
        cx, cy = S(math.cos(a) * 178, math.sin(a) * 58)
        rx, ry = (40 + rng() * 10) * s, (26 + rng() * 7) * s
        stone = (blob(cx, cy, rx, ry, rng), quad((cx - rx * .5, cy - ry * .35), (cx - rx * .1, cy - ry * .7), (cx + rx * .35, cy - ry * .45), 8))
        (back if math.sin(a) < 0 else front).append((cy, stone))
    with Pincel(img, (x - 240 * s, y - 270 * s, x + 240 * s, y + 110 * s)) as p:
        def draw(stones):
            for _, (shape, shine) in sorted(stones, key=lambda q: q[0]):
                p.polygon(shape, STONE, INK, 4.5 * s); p.polyline(shine, STONE_LIGHT, 5 * s)
        p.ellipse(x, y, 150 * s, 44 * s, ASH, INK, 4 * s)
        p.polyline([S(-90, 8), S(60, -16)], STICK, 9 * s)
        p.polyline([S(-60, -18), S(95, 10)], STICK, 9 * s)
        draw(back)
        bx, by = S(5, -8)
        wob = lambda ph, sp=1: math.sin(2 * math.pi * t * 1.6 * sp + ph)
        layer = lambda drops, dy: [teardrop(bx + dx * s, by - dy * s, w * s, h * s * (1 + .07 * wob(ph, 1.3)), (lean + 10 * wob(ph + 1)) * s)
                                   for dx, w, h, lean, ph in drops]
        outer = layer([(0, 70, 215, -10, 0), (-48, 44, 130, -26, 1.3), (48, 46, 150, 22, 2.1), (-18, 58, 175, -6, .7)], 0)
        for q in outer: p.polygon(q, INK, INK, 10 * s)                    # contorno de la unión de todas las lenguas
        for q in outer: p.polygon(q, FLAME[0], None, 0)
        for q in layer([(2, 50, 150, -8, .4), (-30, 32, 95, -18, 1.7), (30, 32, 105, 14, 2.6)], 8): p.polygon(q, FLAME[1], None, 0)
        for q in layer([(2, 30, 92, -5, .9), (-12, 22, 62, -8, 2.2)], 14): p.polygon(q, FLAME[2], None, 0)
        draw(front)
    return (x, y - 230 * s)
