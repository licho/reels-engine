"""Cartoon style: soft edges (each piece is drawn at double size and scaled down), very dark brown ink, rough
edges and stroke textures. It's optional and lives apart: the basic-style pieces (humans, furniture, exterior,
screens) don't change.

Pieces in this style take the image (img), not the ImageDraw, because they're painted on a separate layer:

    from reels_engine.cartoon.humans import buddy
    a = buddy(img, 540, FLOOR, .9, mood="happy", hair="bangs")
    say(ImageDraw.Draw(img), "Hi!", a["mouth"], a["head_r"])

To draw your own pieces in this style: `with Brush(img, box) as p: p.polygon(...)`."""
import math
from PIL import Image, ImageDraw
from ..config import current as _current

_cfg = _current()
INK = _cfg.ink
SS = 2                                    # the layer is drawn at double size and scaled down (soft edges)

def seeded(seed):
    """Reproducible random numbers (mulberry32): the same seed always gives the same shape."""
    a = seed & 0xFFFFFFFF
    def imul(x, y): return (x * y) & 0xFFFFFFFF
    def rng():
        nonlocal a
        a = (a + 0x6D2B79F5) & 0xFFFFFFFF
        t = imul(a ^ (a >> 15), a | 1)
        t = ((t + imul(t ^ (t >> 7), t | 61)) & 0xFFFFFFFF) ^ t
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    return rng

# ---------- shapes ----------
def quad(p0, p1, p2, n=24):
    """Smooth curve from p0 to p2 bending toward p1."""
    return [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0],
             (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]) for u in (i / n for i in range(n + 1))]

def jagged(points, step, amp, rng):
    """"Furry" edge: splits each side and pushes a spike outward on each stretch (fur, straw, grass)."""
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
    """Blob with irregular spikes (mane, bush, explosion)."""
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
    """Slightly wobbly oval (stones, clouds, spots)."""
    return [(cx + math.cos(2 * math.pi * i / n) * rx * (1 + .08 * (rng() - .5)),
             cy + math.sin(2 * math.pi * i / n) * ry * (1 + .08 * (rng() - .5))) for i in range(n)]

def teardrop(cx, by, w, h, lean, n=40):
    """Drop with its base at (cx, by) and the tip pointing up, leaning 'lean' px (flame tongues, drops)."""
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
    """Texture of little strokes inside a polygon (fur, straw). cols = colors to pick from."""
    xs = [q[0] for q in poly]; ys = [q[1] for q in poly]
    for _ in range(n):
        x, y = min(xs) + rng() * (max(xs) - min(xs)), min(ys) + rng() * (max(ys) - min(ys))
        a, L = angle + (rng() - .5) * spread, ln[0] + rng() * (ln[1] - ln[0])
        col = cols[math.floor(rng() * len(cols))]
        if not (inside_poly(x, y, poly) and inside_poly(x + math.cos(a) * L, y + math.sin(a) * L, poly)): continue
        p.polyline(quad((x, y), (x + math.cos(a) * L * .5 + curve, y + math.sin(a) * L * .5), (x + math.cos(a) * L, y + math.sin(a) * L), 6), col, sw)

# ---------- brush ----------
class Brush:
    """Transparent layer with screen coordinates. On leaving the 'with' block it's scaled down and pasted on img.
    Widths (sw) are in screen px. The automatic check gets the piece's real outline."""
    def __init__(self, img, box, ss=SS):
        self.target = img
        self.ox, self.oy = int(math.floor(box[0])), int(math.floor(box[1]))
        self.w, self.h = max(1, int(math.ceil(box[2])) - self.ox), max(1, int(math.ceil(box[3])) - self.oy)
        self.ss = ss
        self.img = Image.new("RGBA", (self.w * ss, self.h * ss), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
    def __enter__(self): return self
    def __exit__(self, *exc):
        if exc[0] is None: self.paste()
    def _p(self, pts):
        return [((x - self.ox) * self.ss, (y - self.oy) * self.ss) for x, y in pts]
    def polygon(self, pts, fill, stroke=INK, sw=5):
        q = self._p(pts)
        if fill: self.d.polygon(q, fill=fill)
        if stroke and sw: self.d.line(q + [q[0]], fill=stroke, width=max(1, round(sw * self.ss)), joint="curve")
    def polyline(self, pts, stroke=INK, sw=6):
        q = self._p(pts); w = max(1, sw * self.ss)
        self.d.line(q, fill=stroke, width=round(w), joint="curve")
        for x, y in (q[0], q[-1]):                                  # round ends
            self.d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=stroke)
    def ellipse(self, cx, cy, rx, ry, fill, stroke=None, sw=0):
        (cx, cy), = self._p([(cx, cy)]); rx, ry, h = rx * self.ss, ry * self.ss, sw * self.ss / 2
        if stroke and sw:
            self.d.ellipse([cx - rx - h, cy - ry - h, cx + rx + h, cy + ry + h], fill=stroke); rx, ry = rx - h, ry - h
        self.d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill)
    def circle(self, cx, cy, r, fill, stroke=INK, sw=5):
        self.ellipse(cx, cy, r, r, fill, stroke, sw)
    def paste(self):
        small = self.img.convert("RGBa").resize((self.w, self.h), Image.LANCZOS).convert("RGBA")
        self.target.paste(small, (self.ox, self.oy), small)
        bb = small.getbbox()
        if bb:
            from ..check import register
            register((bb[0] + self.ox, bb[1] + self.oy, bb[2] + self.ox, bb[3] + self.oy), self.target)
        return ImageDraw.Draw(self.target)
