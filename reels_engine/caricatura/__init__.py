"""Estilo caricatura: orillas suaves (cada pieza se dibuja al doble y se reduce), tinta café muy oscuro, bordes
irregulares y texturas de rayitas. Es opcional y vive aparte: las piezas del estilo básico (humanos, muebles,
exterior, pantallas) no cambian.

Las piezas de este estilo reciben la imagen (img), no el ImageDraw, porque se pintan en una capa aparte:

    from reels_engine.caricatura.humanos import monito
    a = monito(img, 540, FLOOR, .9, mood="feliz", pelo="fleco")
    say(ImageDraw.Draw(img), "¡Hola!", a["mouth"], a["head_r"])

Para dibujar piezas propias en este estilo: `with Pincel(img, caja) as p: p.polygon(...)`."""
import math
from PIL import Image, ImageDraw
from ..config import current as _current

_cfg = _current()
INK = _cfg.ink
SS = 2                                    # la capa se dibuja al doble de tamaño y se reduce (orillas suaves)

def semilla(seed):
    """Números aleatorios reproducibles (mulberry32): la misma semilla da siempre la misma forma."""
    a = seed & 0xFFFFFFFF
    def imul(x, y): return (x * y) & 0xFFFFFFFF
    def rng():
        nonlocal a
        a = (a + 0x6D2B79F5) & 0xFFFFFFFF
        t = imul(a ^ (a >> 15), a | 1)
        t = ((t + imul(t ^ (t >> 7), t | 61)) & 0xFFFFFFFF) ^ t
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    return rng

# ---------- formas ----------
def quad(p0, p1, p2, n=24):
    """Curva suave de p0 a p2 que se inclina hacia p1."""
    return [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0],
             (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]) for u in (i / n for i in range(n + 1))]

def jagged(points, step, amp, rng):
    """Borde "peludo": subdivide cada arista y empuja un pico hacia fuera en cada tramo (pelaje, paja, pasto)."""
    n_ = len(points)
    area = sum(points[i][0] * points[(i + 1) % n_][1] - points[(i + 1) % n_][0] * points[i][1] for i in range(n_))
    sign = 1 if area > 0 else -1
    out = []
    for i, a in enumerate(points):
        b = points[(i + 1) % n_]
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1
        nx, ny = sign * dy / L, -sign * dx / L
        n = max(1, round(L / step))
        for j in range(n):
            out.append((a[0] + dx * j / n, a[1] + dy * j / n))
            f = (j + .5) / n; k = amp * (.5 + .5 * rng())
            out.append((a[0] + dx * f + nx * k, a[1] + dy * f + ny * k))
    return out

def spiky_blob(cx, cy, rx, ry_top, ry_bot, n, rng):
    """Mancha con picos irregulares (melena, arbusto, explosión)."""
    pts = []
    for i in range(n * 2):
        tip = i % 2 == 0
        a = math.pi * (i + (rng() - .5) * .7) / n
        k = 1.0 + .14 * rng() if tip else .86 + .05 * rng()
        ry = ry_bot if math.sin(a) > 0 else ry_top
        bend = (rng() - .5) * .12 if tip else 0
        pts.append((cx + math.cos(a + bend) * rx * k, cy + math.sin(a + bend) * ry * k))
    return pts

def blob(cx, cy, rx, ry, rng, n=18):
    """Óvalo un poco chueco (piedras, nubes, manchas)."""
    return [(cx + math.cos(2 * math.pi * i / n) * rx * (1 + .08 * (rng() - .5)),
             cy + math.sin(2 * math.pi * i / n) * ry * (1 + .08 * (rng() - .5))) for i in range(n)]

def teardrop(cx, by, w, h, lean, n=40):
    """Gota con base en (cx, by) y punta hacia arriba inclinada 'lean' px (lenguas de fuego, gotas)."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n; u = (1 - math.cos(t)) / 2
        pts.append((cx + w * math.sin(t) * math.sin(t / 2) ** 1.2 + lean * (1 - u) ** 2, by - h * (1 - u)))
    return pts

def inside_poly(x, y, poly):
    inside = False; j = len(poly) - 1
    for i in range(len(poly)):
        (xi, yi), (xj, yj) = poly[i], poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi: inside = not inside
        j = i
    return inside

def strokes(p, poly, n, rng, cols, ln=(14, 32), sw=3.5, angle=math.pi / 2, spread=.9, curve=5):
    """Textura de rayitas dentro de un polígono (pelaje, paja). cols = colores a sortear."""
    xs = [q[0] for q in poly]; ys = [q[1] for q in poly]
    for _ in range(n):
        x, y = min(xs) + rng() * (max(xs) - min(xs)), min(ys) + rng() * (max(ys) - min(ys))
        a, L = angle + (rng() - .5) * spread, ln[0] + rng() * (ln[1] - ln[0])
        col = cols[math.floor(rng() * len(cols))]
        if not (inside_poly(x, y, poly) and inside_poly(x + math.cos(a) * L, y + math.sin(a) * L, poly)): continue
        p.polyline(quad((x, y), (x + math.cos(a) * L * .5 + curve, y + math.sin(a) * L * .5), (x + math.cos(a) * L, y + math.sin(a) * L), 6), col, sw)

# ---------- pincel ----------
class Pincel:
    """Capa transparente con coordenadas de pantalla. Al salir del 'with' se reduce y se pega en img.
    Los anchos (sw) están en px de pantalla. La revisión automática recibe la silueta real de la pieza."""
    def __init__(self, img, box, ss=SS):
        self.target = img
        self.ox, self.oy = int(math.floor(box[0])), int(math.floor(box[1]))
        self.w, self.h = max(1, int(math.ceil(box[2])) - self.ox), max(1, int(math.ceil(box[3])) - self.oy)
        self.ss = ss
        self.img = Image.new("RGBA", (self.w * ss, self.h * ss), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
    def __enter__(self): return self
    def __exit__(self, *exc):
        if exc[0] is None: self.pegar()
    def _p(self, pts):
        return [((x - self.ox) * self.ss, (y - self.oy) * self.ss) for x, y in pts]
    def polygon(self, pts, fill, stroke=INK, sw=5):
        q = self._p(pts)
        if fill: self.d.polygon(q, fill=fill)
        if stroke and sw: self.d.line(q + [q[0]], fill=stroke, width=max(1, round(sw * self.ss)), joint="curve")
    def polyline(self, pts, stroke=INK, sw=6):
        q = self._p(pts); w = max(1, sw * self.ss)
        self.d.line(q, fill=stroke, width=round(w), joint="curve")
        for x, y in (q[0], q[-1]):                                  # puntas redondas
            self.d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=stroke)
    def ellipse(self, cx, cy, rx, ry, fill, stroke=None, sw=0):
        (cx, cy), = self._p([(cx, cy)]); rx, ry, h = rx * self.ss, ry * self.ss, sw * self.ss / 2
        if stroke and sw:
            self.d.ellipse([cx - rx - h, cy - ry - h, cx + rx + h, cy + ry + h], fill=stroke); rx, ry = rx - h, ry - h
        self.d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill)
    def circle(self, cx, cy, r, fill, stroke=INK, sw=5):
        self.ellipse(cx, cy, r, r, fill, stroke, sw)
    def pegar(self):
        small = self.img.convert("RGBa").resize((self.w, self.h), Image.LANCZOS).convert("RGBA")
        self.target.paste(small, (self.ox, self.oy), small)
        bb = small.getbbox()
        if bb:
            from ..check import registrar
            registrar((bb[0] + self.ox, bb[1] + self.oy, bb[2] + self.ox, bb[3] + self.oy), self.target)
        return ImageDraw.Draw(self.target)
