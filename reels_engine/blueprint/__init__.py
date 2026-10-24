"""Blueprint style: minimal technical infographic, like an engineering drawing on a dark screen. Dark blue-black
background with a faint grid, "+" marks and a few dim stars; thin white lines for structures, electric cyan for what
moves (water, flows, mechanisms), grey for secondary things and one accent color (yellow by default) for the key
number. All the lettering is monospaced and uppercase. It's optional and lives apart: the other styles don't change.

Pieces in this style take the image (img). Lines are drawn on a separate layer at double size and scaled down
(soft edges); texts are drawn straight on the image so the automatic check sees them:

    from reels_engine.blueprint import blueprint_bg, kicker, headline, big_number
    from reels_engine.blueprint.section import cross_section
    img, d = canvas(blueprint_bg(c.t))
    kicker(img, "GROUND MECHANICS", 60, 250)
    headline(img, "THE CITY\\nTHAT SINKS", 60, 290, appear=c.lt / 1.2)
    big_number(img, 15, 60, 520, unit="cm a year")
    cross_section(img, (40, 800, 1040, 1320), [("clay", 230), ("gravel", 150), ("rock", 0)], water=40, t=c.t)

Colors are tokens (BG, GRID, WHITE, CYAN, GRAY, DIM, ACCENT, RISK, PANEL and the ground colors); a channel changes
any of them with `Channel.blueprint_palette` and the type with `Channel.blueprint_font` / `blueprint_font_light`.

Pieces: this module (background, titles, big number, callout, dimension line, ruler, frame, markers) and `section`
(cross-section of the ground with buildings, layers, water table and sinking).

To draw your own pieces in this style: `with Plate(img, box) as p: p.line(...); p.dashed(...); p.rect(...)`."""
import math
import random
from contextlib import contextmanager
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont
from ..config import current as _current

_cfg = _current()
W, H = _cfg.size
SS = 2                                    # the layer is drawn at double size and scaled down (soft edges)
FONT = _cfg.blueprint_font or "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FONT_LIGHT = _cfg.blueprint_font_light or "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

_P = {
    "BG": (10, 14, 22), "BG2": (5, 8, 14),             # background (top, bottom)
    "GRID": (21, 29, 42), "CROSS": (52, 64, 82), "STAR": (120, 134, 154),
    "WHITE": (236, 240, 245), "CYAN": (60, 222, 232), "GRAY": (132, 144, 160), "DIM": (74, 86, 104),
    "ACCENT": (246, 206, 52), "RISK": (240, 88, 64),   # key number / failures, risks, critical points
    "PANEL": (13, 17, 25),                             # inside of diagrams (sky of a cross-section)
    # ground layers
    "FILL": (104, 90, 74), "CLAY": (84, 70, 56), "SAND": (122, 104, 74), "GRAVEL": (54, 70, 68),
    "ROCK": (42, 43, 48), "WATER": (24, 60, 78),
    **_cfg.blueprint_palette,
}
BG, BG2, GRID, CROSS, STAR = _P["BG"], _P["BG2"], _P["GRID"], _P["CROSS"], _P["STAR"]
WHITE, CYAN, GRAY, DIM, ACCENT, RISK, PANEL = (_P[k] for k in ("WHITE", "CYAN", "GRAY", "DIM", "ACCENT", "RISK", "PANEL"))
GROUND = {k.lower(): _P[k] for k in ("FILL", "CLAY", "SAND", "GRAVEL", "ROCK", "WATER")}

@lru_cache(maxsize=64)
def font(size, bold=True):
    """Monospaced font of the style (cached)."""
    return ImageFont.truetype(FONT if bold else FONT_LIGHT, max(8, int(size)))

def mix(c1, c2, t):
    """Color between c1 and c2 (t from 0 to 1)."""
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

# ---------- plate ----------
class Plate:
    """Transparent layer with screen coordinates. On leaving the 'with' block it's scaled down and pasted on img.
    Widths (w) are in screen px. The automatic check gets the piece's real outline."""
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
    def _w(self, w): return max(1, int(round(w * self.ss)))

    def line(self, pts, color=WHITE, w=3):
        """Straight segments through the points, round joints."""
        q = self._p(pts); ww = self._w(w)
        self.d.line(q, fill=color, width=ww, joint="curve")
        for x, y in (q[0], q[-1]):
            self.d.ellipse([x - ww / 2 + .5, y - ww / 2 + .5, x + ww / 2 - .5, y + ww / 2 - .5], fill=color)

    def dashed(self, pts, color=WHITE, w=3, dash=18, gap=12, phase=0.0):
        """Dashed line through the points; a phase that grows makes the dashes travel."""
        period = dash + gap; s = -(phase % period)
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            L = math.hypot(x1 - x0, y1 - y0)
            if not L: continue
            ux, uy = (x1 - x0) / L, (y1 - y0) / L
            while s < L:
                a, b = max(0, s), min(L, s + dash)
                if b > a: self.d.line(self._p([(x0 + ux * a, y0 + uy * a), (x0 + ux * b, y0 + uy * b)]), fill=color, width=self._w(w))
                s += period
            s -= L

    def poly(self, pts, fill=None, color=None, w=3):
        """Polygon with an optional fill and outline."""
        q = self._p(pts)
        if fill is not None: self.d.polygon(q, fill=fill)
        if color is not None: self.line(list(pts) + [pts[0], pts[1]], color, w)

    def rect(self, x0, y0, x1, y1, fill=None, color=None, w=3):
        """Rectangle with an optional fill and outline."""
        if fill is not None: self.d.rectangle(self._p([(x0, y0), (x1, y1)]), fill=fill)
        if color is not None:
            hw = w / 2
            self.d.rectangle(self._p([(x0 - hw, y0 - hw), (x1 + hw, y1 + hw)]), outline=color, width=self._w(w))

    def circle(self, cx, cy, r, fill=None, color=None, w=2):
        """Circle with an optional fill and outline."""
        self.d.ellipse(self._p([(cx - r, cy - r), (cx + r, cy + r)]), fill=fill, outline=color,
                       width=self._w(w) if color is not None else 0)

    @contextmanager
    def clip(self, pts):
        """Everything drawn inside the block only shows inside the shape."""
        base, layer = self.img, Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        mask = Image.new("L", base.size, 0)
        ImageDraw.Draw(mask).polygon(self._p(pts), fill=255)
        self.img, self.d = layer, ImageDraw.Draw(layer)
        try:
            yield
        finally:
            empty = Image.new("RGBA", layer.size, (0, 0, 0, 0))
            base.alpha_composite(Image.composite(layer, empty, mask))
            self.img, self.d = base, ImageDraw.Draw(base)

    def hatch(self, pts, color=DIM, gap=18, ang=-math.pi / 4, w=2):
        """Parallel lines inside a shape (the drawing convention for rock or a cut solid)."""
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        R = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) / 2 + 5
        dx, dy = math.cos(ang), math.sin(ang)
        with self.clip(pts):
            t = -R
            while t < R:
                ox, oy = cx - dy * t, cy + dx * t
                self.d.line(self._p([(ox - dx * R, oy - dy * R), (ox + dx * R, oy + dy * R)]), fill=color, width=self._w(w))
                t += gap

    def paste(self):
        small = self.img.convert("RGBa").resize((self.w, self.h), Image.LANCZOS).convert("RGBA")
        bb = small.getbbox()
        self.target.paste(small, (self.ox, self.oy), small)
        if bb:
            from ..check import register
            register((bb[0] + self.ox, bb[1] + self.oy, bb[2] + self.ox, bb[3] + self.oy), self.target)
        return ImageDraw.Draw(self.target)

# ---------- background ----------
@lru_cache(maxsize=8)
def _grid(cell, top, bot, grid, cross):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    for y in range(H): d.line([(0, y), (W, y)], fill=mix(top, bot, y / H))
    ox, oy = (W % cell) // 2, (H % cell) // 2
    for x in range(ox, W, cell): d.line([(x, 0), (x, H)], fill=grid)
    for y in range(oy, H, cell): d.line([(0, y), (W, y)], fill=grid)
    for x in range(ox, W + 1, cell * 2):
        for y in range(oy, H + 1, cell * 2):
            d.line([(x - 9, y), (x + 9, y)], fill=cross, width=2); d.line([(x, y - 9), (x, y + 9)], fill=cross, width=2)
    return img

@lru_cache(maxsize=8)
def _stars(n, seed):
    R = random.Random(seed)
    return [(R.uniform(0, W), R.uniform(0, H), R.choice((1, 1, 1.5, 2, 2.5)), R.uniform(0, 6.3), R.uniform(.25, 1)) for _ in range(n)]

def blueprint_bg(t=0.0, cell=120, stars=90, seed=3):
    """Dark blue-black background with a faint grid, "+" marks and dim twinkling dots."""
    img = _grid(cell, BG, BG2, GRID, CROSS).copy(); d = ImageDraw.Draw(img)
    for x, y, r, ph, b in _stars(stars, seed):
        c = mix(BG, STAR, b * (.6 + .4 * math.sin(t * 1.7 + ph)))
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    return img

# ---------- text ----------
def text(img, s, x, y, size, fill=WHITE, bold=True, tracking=0.0, anchor="ls"):
    """Monospaced text; tracking = extra space between letters (fraction of the size); anchor like Pillow's.
    Returns its box."""
    f, d = font(size, bold), ImageDraw.Draw(img)
    if not tracking or len(s) < 2:
        d.text((x, y), s, font=f, fill=fill, anchor=anchor)
        return d.textbbox((x, y), s, font=f, anchor=anchor)
    gap = tracking * size; ws = [f.getlength(ch) for ch in s]
    total = sum(ws) + gap * (len(s) - 1)
    x0 = x - {"l": 0, "m": total / 2, "r": total}[anchor[0]]
    bb = d.textbbox((x0, y), s[0], font=f, anchor="l" + anchor[1])
    for ch, w in zip(s, ws):
        if ch.strip(): d.text((x0, y), ch, font=f, fill=fill, anchor="l" + anchor[1])
        x0 += w + gap
    return (bb[0], bb[1], bb[0] + total, bb[3])

def kicker(img, s, x, y, size=34, color=GRAY, anchor="lt"):
    """Small label with wide letter spacing (series or section name) above a title."""
    return text(img, s.upper(), x, y, size, color, tracking=.42, anchor=anchor)

def headline(img, s, x, y, size=100, color=WHITE, appear=1.0, leading=1.0, cursor=CYAN):
    """Big uppercase title ("\\n" splits lines) typed letter by letter while appear goes from 0 to 1."""
    lines = s.upper().split("\n")
    total = sum(len(l) for l in lines); shown = int(round(max(0.0, min(1.0, appear)) * total))
    f = font(size); lh = size * leading; box = None
    for i, ln in enumerate(lines):
        part = ln[:max(0, shown)]; shown -= len(ln)
        ly = y + i * lh
        if part.strip():
            bb = text(img, part, x, ly, size, color, anchor="lt")
            box = bb if box is None else (min(box[0], bb[0]), min(box[1], bb[1]), max(box[2], bb[2]), max(box[3], bb[3]))
        if 0 > shown > -len(ln) - 1 and appear < 1 and cursor:            # blinking block where the typing is
            cx = x + f.getlength(part)
            ImageDraw.Draw(img).rectangle([cx + 4, ly + size * .12, cx + 4 + size * .5, ly + size * .95], fill=cursor)
            break
    return box

def big_number(img, value, x, y, size=220, unit="", color=ACCENT, unit_color=WHITE, decimals=0, underline=True,
               anchor="l"):
    """Key figure in the accent color, underlined, with its unit below; value can be a number (count it up with tw)."""
    s = f"{value:,.{decimals}f}" if isinstance(value, (int, float)) else str(value)
    f = font(size); w = f.getlength(s)
    x0 = x - {"l": 0, "m": w / 2, "r": w}[anchor]
    bb = text(img, s, x0, y, size, color, anchor="lt")
    top, bot = bb[1], bb[3]
    if underline:
        uy = bot + size * .1
        with Plate(img, (x0 - 10, uy - 10, x0 + w + 10, uy + 10)) as p:
            p.line([(x0, uy), (x0 + w * .92, uy)], color, max(3, size * .025))
        bot = uy
    if unit:
        ub = text(img, unit, x0, bot + size * .1, size * .2, unit_color, bold=False, anchor="lt")
        bot = ub[3]
    return (x0, top, max(x0 + w, bb[2]), bot)

def callout(img, s, x, y, tx, ty, size=30, color=WHITE, line=GRAY, dot=CYAN):
    """Technical label: a dot on the point (x, y) and a leader line to the text at (tx, ty)."""
    k = 1 if tx >= x else -1
    knee = (tx - k * 60, ty)
    with Plate(img, (min(x, tx, knee[0]) - 12, min(y, ty) - 12, max(x, tx, knee[0]) + 12, max(y, ty) + 12)) as p:
        p.line([(x, y), knee, (tx - k * 12, ty)], line, 2)
        p.circle(x, y, 6, fill=dot)
    return text(img, s.upper(), tx, ty, size, color, anchor="lm" if k > 0 else "rm")

def dimension(img, x0, y0, x1, y1, s="", size=28, color=GRAY, text_color=WHITE, offset=0):
    """Dimension line between two points with end ticks and its measure beside the middle (sizes and distances)."""
    L = math.hypot(x1 - x0, y1 - y0) or 1
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    a, b = (x0 + nx * offset, y0 + ny * offset), (x1 + nx * offset, y1 + ny * offset)
    with Plate(img, (min(x0, x1, a[0], b[0]) - 20, min(y0, y1, a[1], b[1]) - 20,
                     max(x0, x1, a[0], b[0]) + 20, max(y0, y1, a[1], b[1]) + 20)) as p:
        p.line([a, b], color, 2)
        for (px, py), (ex, ey) in ((a, (x0, y0)), (b, (x1, y1))):
            p.line([(px - nx * 14, py - ny * 14), (px + nx * 14, py + ny * 14)], color, 2)
            if offset: p.line([(ex, ey), (px, py)], color, 1)
    if s:
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        if abs(y1 - y0) > abs(x1 - x0): return text(img, s, mx + 22, my, size, text_color, anchor="lm")
        return text(img, s, mx, my - 18, size, text_color, anchor="ms")

def scale_ruler(img, x, y0, y1, step=12, major=5, labels=(), size=26, color=GRAY, side="left", label_color=None):
    """Vertical measuring ruler from y0 to y1: a tick every 'step' px, a long one every 'major';
    labels = [(y, "40"), …] written beside it."""
    s = -1 if side == "left" else 1
    with Plate(img, (x - 34, y0 - 4, x + 34, y1 + 4)) as p:
        p.line([(x, y0), (x, y1)], color, 2)
        k, y = 0, y0
        while y <= y1 + .5:
            n = 22 if k % major == 0 else 11
            p.line([(x, y), (x + s * n, y)], color, 2)
            k += 1; y += step
    for ly, s_ in labels:
        text(img, str(s_), x + s * 30, ly, size, label_color or color, anchor="rm" if side == "left" else "lm")

def plan_frame(img, x0, y0, x1, y1, color=DIM, w=2, cross=16):
    """Thin box with "+" marks sticking out of its corners (frame of a diagram)."""
    with Plate(img, (x0 - cross - 4, y0 - cross - 4, x1 + cross + 4, y1 + cross + 4)) as p:
        p.rect(x0, y0, x1, y1, color=color, w=w)
        for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
            p.line([(cx - cross, cy), (cx + cross, cy)], color, w); p.line([(cx, cy - cross), (cx, cy + cross)], color, w)

def pointer(img, x, y, size=22, color=ACCENT, facing="left"):
    """Small solid triangle pointing at (x, y) (marks a level on a ruler)."""
    s = {"left": (1, 0), "right": (-1, 0), "up": (0, 1), "down": (0, -1)}[facing]
    a, b = (x + s[0] * size - s[1] * size * .6, y + s[1] * size - s[0] * size * .6), \
           (x + s[0] * size + s[1] * size * .6, y + s[1] * size + s[0] * size * .6)
    with Plate(img, (x - size - 2, y - size - 2, x + size + 2, y + size + 2)) as p:
        p.poly([(x, y), a, b], fill=color)

def level_mark(img, x, y, size=26, color=CYAN):
    """Water level symbol: an open triangle standing on the line with two short lines under it."""
    with Plate(img, (x - size - 4, y - size * 1.1, x + size + 4, y + size * .9)) as p:
        p.poly([(x - size * .6, y - size * .95), (x + size * .6, y - size * .95), (x, y)], color=color, w=3)
        p.line([(x - size * .45, y + size * .3), (x + size * .45, y + size * .3)], color, 3)
        p.line([(x - size * .25, y + size * .6), (x + size * .25, y + size * .6)], color, 3)
