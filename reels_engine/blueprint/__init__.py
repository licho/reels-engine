"""Blueprint style: minimal technical infographic, like an engineering plan on a dark screen. Dark blueprint-blue
sheet with a fine grid, a major grid with "+" marks and sheet coordinates on the margins; thin white lines for
structures, electric cyan for what moves (water, flows, mechanisms) and for the key number, grey for secondary things,
amber for critical points and red for failures. All the lettering is monospaced and uppercase. Its signature is the
x-ray lens that shows what's hidden inside things. It's optional and lives apart: the other styles don't change.

Pieces in this style take the image (img). Lines are drawn on a separate layer at double size and scaled down
(soft edges); texts are drawn straight on the image so the automatic check sees them:

    from reels_engine.blueprint import blueprint_bg, kicker, headline, big_number
    from reels_engine.blueprint.section import cross_section
    img, d = canvas(blueprint_bg(c.t))
    kicker(img, "GROUND MECHANICS", 60, 250)
    headline(img, "THE CITY\\nTHAT *SINKS*", 60, 290, appear=c.lt / 1.2)
    big_number(img, 15, 60, 520, unit="cm a year")
    cross_section(img, (40, 800, 1040, 1320), [("clay", 230), ("gravel", 150), ("rock", 0)], water=40, t=c.t)

Colors are tokens (BG, GRID, WHITE, CYAN, GRAY, DIM, ACCENT, RISK, PANEL and the ground colors); a channel changes
any of them with `Channel.blueprint_palette` and the type with `Channel.blueprint_font` / `blueprint_font_light`.

Modules: this one (background, text, titles, big number, callout, dimension line, ruler, frame, markers, title block,
x-ray lens), `marks` (flows, arrows, forces, zoom lens, data stamps, alerts, waves, reveals, captions, brand),
`charts` (readout, bars, columns, line, limit meter, fill bar, icon grid, magnitudes, split bar, before/after,
timeline), `parts` (pipes, valve, pump, tanks, faucet, gauge, meter, house, building, tower section, terrain),
`scale` (silhouettes at real size), `section` (cross-section of the ground) and `templates` (size comparison, steps,
question and answer, failure chain, exploded view, schematic map).

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
NEON = 12                                 # default halo (px) of the things that move; glow=0 turns it off
FONT = _cfg.blueprint_font or "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FONT_LIGHT = _cfg.blueprint_font_light or "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

_P = {
    "BG": (12, 27, 50), "BG2": (6, 15, 31),            # background (top, bottom): dark blueprint blue
    "GRID": (17, 35, 61), "GRID2": (27, 50, 82),       # minor / major grid
    "CROSS": (62, 94, 132), "STAR": (120, 146, 178),
    "WHITE": (234, 242, 252), "CYAN": (72, 228, 242), "GRAY": (130, 152, 180), "DIM": (70, 96, 128),
    "ACCENT": (255, 166, 40), "RISK": (255, 84, 72),   # critical points, "now" markers / failures and risks
    # one color per kind of system, so a scene isn't only blue: water and the main flow are CYAN, electricity and
    # energy VOLT, air, gas and "it works" LIME, data, signals and sensors MAGENTA, a second flow or heat VIOLET
    "VOLT": (255, 214, 64), "LIME": (128, 242, 120), "MAGENTA": (255, 86, 200), "VIOLET": (160, 128, 255),
    "PANEL": (9, 21, 40),                              # inside of diagrams (sky of a cross-section)
    # ground layers: blue-grey tones told apart by their drawing pattern, like a real technical section
    "FILL": (46, 64, 90), "CLAY": (35, 53, 80), "SAND": (54, 72, 98), "GRAVEL": (27, 45, 70),
    "ROCK": (20, 33, 54), "WATER": (14, 52, 86),
    **_cfg.blueprint_palette,
}
BG, BG2, GRID, GRID2, CROSS, STAR = (_P[k] for k in ("BG", "BG2", "GRID", "GRID2", "CROSS", "STAR"))
WHITE, CYAN, GRAY, DIM, ACCENT, RISK, PANEL = (_P[k] for k in ("WHITE", "CYAN", "GRAY", "DIM", "ACCENT", "RISK", "PANEL"))
VOLT, LIME, MAGENTA, VIOLET = (_P[k] for k in ("VOLT", "LIME", "MAGENTA", "VIOLET"))
SERIES = (CYAN, MAGENTA, VOLT, LIME, VIOLET, ACCENT)   # colors in order for charts with several series
GROUND = {k.lower(): _P[k] for k in ("FILL", "CLAY", "SAND", "GRAVEL", "ROCK", "WATER")}

@lru_cache(maxsize=64)
def font(size, bold=True):
    """Monospaced font of the style (cached)."""
    return ImageFont.truetype(FONT if bold else FONT_LIGHT, max(8, int(size)))

def mix(c1, c2, t):
    """Color between c1 and c2 (t from 0 to 1)."""
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def trace(pts, k):
    """The first fraction k (0 to 1) of a path, to draw lines that draw themselves."""
    pts = list(pts)
    if k >= 1 or len(pts) < 2: return pts
    total = sum(math.dist(a, b) for a, b in zip(pts, pts[1:])); want, out = total * max(0.0, k), [pts[0]]
    for a, b in zip(pts, pts[1:]):
        L = math.dist(a, b)
        if want >= L: out.append(b); want -= L
        else:
            if L: out.append((a[0] + (b[0] - a[0]) * want / L, a[1] + (b[1] - a[1]) * want / L))
            break
    return out

def appear(t, i, gap=.25, dur=.4, start=0.0):
    """How far item i of a list has appeared (0 to 1) when they come in one after another."""
    return max(0.0, min(1.0, (t - start - i * gap) / dur)) if dur > 0 else float(t >= start + i * gap)

def smooth(pts, n=12):
    """Rounded path through the points (Catmull-Rom), for curved arrows and flows."""
    p = [pts[0]] + list(pts) + [pts[-1]]; out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                   + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(p[-2])
    return out

def bounds(pts, pad=0):
    """Box around some points, with a margin."""
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)

# ---------- plate ----------
class Plate:
    """Transparent layer with screen coordinates. On leaving the 'with' block it's scaled down and pasted on img.
    Widths (w) are in screen px. The automatic check gets the piece's real outline.
    glow = radius in px of a neon halo around everything drawn in it (for things that move: flows, arrows, pulses)."""
    def __init__(self, img, box, ss=SS, glow=0, glow_alpha=1.0):
        self.target, self.glow, self.glow_alpha = img, glow, glow_alpha
        if glow: box = (box[0] - 2 * glow, box[1] - 2 * glow, box[2] + 2 * glow, box[3] + 2 * glow)
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
        if self.glow and bb: _neon(self.target, small, (self.ox, self.oy), self.glow, self.glow_alpha)
        self.target.paste(small, (self.ox, self.oy), small)
        if bb:
            from ..check import register
            register((bb[0] + self.ox, bb[1] + self.oy, bb[2] + self.ox, bb[3] + self.oy), self.target)
        return ImageDraw.Draw(self.target)

def _neon(target, small, pos, radius, strength):
    """Adds a blurred, brightened copy of the layer under it: light, not paint, so it glows on the dark sheet."""
    import numpy as np
    from PIL import ImageFilter
    add = 0
    for r, g in ((radius * .35, 1.8), (radius, 2.2)):   # a tight bright core plus a wide soft halo
        a = np.asarray(small.filter(ImageFilter.GaussianBlur(max(1, r)))).astype(np.float32)
        add = add + a[..., :3] * (a[..., 3:4] / 255.0) * (g * strength)
    x, y = pos; w, h = small.size
    X0, Y0, X1, Y1 = max(0, x), max(0, y), min(target.width, x + w), min(target.height, y + h)
    if X1 <= X0 or Y1 <= Y0: return
    add = add[Y0 - y:Y1 - y, X0 - x:X1 - x]
    if target.mode == "RGB":
        base = np.asarray(target.crop((X0, Y0, X1, Y1))).astype(np.float32)
        target.paste(Image.fromarray(np.clip(base + add, 0, 255).astype(np.uint8)), (X0, Y0))
    else:                                             # a transparent layer: keep the halo as soft light on it
        al = np.clip(add.max(axis=2), 0, 255)
        rgb = np.clip(add * 255.0 / np.maximum(al[..., None], 1), 0, 255)
        layer = Image.fromarray(np.dstack([rgb, al]).astype(np.uint8), "RGBA")
        target.alpha_composite(layer, (X0, Y0))

# ---------- background ----------
@lru_cache(maxsize=8)
def _grid(cell, top, bot):
    # drawn one px taller and cropped: the check ignores canvases of another size, so the sheet marks don't count
    img = Image.new("RGB", (W, H + 1)); d = ImageDraw.Draw(img)
    for y in range(H): d.line([(0, y), (W, y)], fill=mix(top, bot, y / H))
    minor = cell // 5
    ox, oy = (W % cell) // 2, (H % cell) // 2
    for x in range(ox % minor, W, minor): d.line([(x, 0), (x, H)], fill=GRID)
    for y in range(oy % minor, H, minor): d.line([(0, y), (W, y)], fill=GRID)
    for x in range(ox, W, cell): d.line([(x, 0), (x, H)], fill=GRID2, width=2)
    for y in range(oy, H, cell): d.line([(0, y), (W, y)], fill=GRID2, width=2)
    for x in range(ox, W + 1, cell):
        for y in range(oy, H + 1, cell):
            d.line([(x - 8, y), (x + 8, y)], fill=CROSS, width=2); d.line([(x, y - 8), (x, y + 8)], fill=CROSS, width=2)
    f = font(18)                                      # sheet coordinates, like the margins of a plan
    for i, x in enumerate(range(ox, W - cell // 2, cell)):
        d.text((x + cell / 2, 22), "ABCDEFGHIJ"[i % 10], font=f, fill=CROSS, anchor="mm")
    for j, y in enumerate(range(oy, H - cell // 2, cell)):
        d.text((16, y + cell / 2), f"{j + 1:02d}", font=f, fill=CROSS, anchor="lm")
    return img.crop((0, 0, W, H))

@lru_cache(maxsize=8)
def _stars(n, seed):
    R = random.Random(seed)
    return [(R.uniform(0, W), R.uniform(0, H), R.choice((1, 1, 1.5, 2)), R.uniform(0, 6.3), R.uniform(.25, 1)) for _ in range(n)]

def blueprint_bg(t=0.0, cell=200, stars=0, seed=3):
    """Dark blueprint-blue sheet: fine grid, major grid with "+" marks and sheet coordinates on the margins."""
    img = _grid(cell, BG, BG2).copy()
    if stars:
        d = ImageDraw.Draw(img)
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
    bb = d.textbbox((x0, y), s, font=f, anchor="l" + anchor[1])
    base = y + d.textbbox((0, 0), s, font=f, anchor="l" + anchor[1])[1] - d.textbbox((0, 0), s, font=f, anchor="ls")[1]
    for ch, w in zip(s, ws):                          # letter by letter on one baseline (accents don't shift them)
        if ch.strip(): d.text((x0, base), ch, font=f, fill=fill, anchor="ls")
        x0 += w + gap
    return (bb[0], bb[1], bb[0] + total, bb[3])

def kicker(img, s, x, y, size=34, color=GRAY, mark=CYAN, anchor="lt"):
    """Small label with wide letter spacing after a cyan square (series or section name) above a title."""
    if mark:
        ImageDraw.Draw(img).rectangle([x, y + size * .18, x + size * .62, y + size * .8], fill=mark)
        x += size * 1.15
    return text(img, s.upper(), x, y, size, color, tracking=.42, anchor=anchor)

def headline(img, s, x, y, size=100, color=WHITE, appear=1.0, leading=1.2, cursor=CYAN, highlight=CYAN):
    """Big uppercase title ("\n" splits lines, *words* in cyan) typed letter by letter while appear goes 0 to 1."""
    lines, hl = [], False
    for ln in s.upper().split("\n"):
        chars = []
        for ch in ln:
            if ch == "*": hl = not hl
            else: chars.append((ch, hl))
        lines.append(chars)
    total = sum(len(l) for l in lines); shown = int(round(max(0.0, min(1.0, appear)) * total))
    f = font(size); lh = size * leading; box = None
    for i, ln in enumerate(lines):
        part = ln[:max(0, shown)]; shown -= len(ln)
        ly, cx = y + i * lh, x
        k = 0
        while k < len(part):                          # runs of the same color
            j = k
            while j < len(part) and part[j][1] == part[k][1]: j += 1
            run = "".join(ch for ch, _ in part[k:j])
            if run.strip():
                bb = text(img, run, cx, ly, size, highlight if part[k][1] else color, anchor="la")
                box = bb if box is None else (min(box[0], bb[0]), min(box[1], bb[1]), max(box[2], bb[2]), max(box[3], bb[3]))
            cx += f.getlength(run); k = j
        if 0 > shown > -len(ln) - 1 and appear < 1 and cursor:            # block where the typing is
            ImageDraw.Draw(img).rectangle([cx + 4, ly + size * .12, cx + 4 + size * .5, ly + size * .95], fill=cursor)
            break
    return box

def _glow(img, s, x, y, f, color, radius):
    from PIL import ImageFilter
    bb = ImageDraw.Draw(img).textbbox((x, y), s, font=f, anchor="lt")
    m = int(radius * 3)
    layer = Image.new("L", (int(bb[2] - bb[0]) + 2 * m, int(bb[3] - bb[1]) + 2 * m), 0)
    ImageDraw.Draw(layer).text((x - bb[0] + m, y - bb[1] + m), s, font=f, fill=110, anchor="lt")
    layer = layer.filter(ImageFilter.GaussianBlur(radius))
    img.paste(Image.new("RGB", layer.size, color), (int(bb[0]) - m, int(bb[1]) - m), layer)

def big_number(img, value, x, y, size=220, unit="", color=CYAN, unit_color=WHITE, decimals=0, underline=True,
               anchor="l", glow=True):
    """Key figure in cyan with a soft screen glow, measured by a dimension line under it, and its unit below;
    value can be a number (count it up with tw)."""
    s = f"{value:,.{decimals}f}" if isinstance(value, (int, float)) else str(value)
    f = font(size); w = f.getlength(s)
    x0 = x - {"l": 0, "m": w / 2, "r": w}[anchor]
    if glow: _glow(img, s, x0, y, f, color, size * .09)
    bb = text(img, s, x0, y, size, color, anchor="lt")
    top, bot = bb[1], bb[3]
    if underline:                                     # a dimension line: the number is "measured"
        uy, tk = bot + size * .12, size * .07
        with Plate(img, (x0 - 10, uy - tk - 4, x0 + w + 10, uy + tk + 4)) as p:
            p.line([(x0, uy), (x0 + w, uy)], color, max(3, size * .018))
            for ex in (x0, x0 + w): p.line([(ex, uy - tk), (ex, uy + tk)], color, max(3, size * .018))
        bot = uy + tk
    if unit:
        ub = text(img, unit, x0, bot + size * .08, size * .2, unit_color, bold=False, anchor="lt")
        bot = ub[3]
    return (x0, top, max(x0 + w, bb[2]), bot)

def plan_stamp(img, rows, x1, y0, size=22, color=GRAY, value_color=WHITE, line=DIM):
    """Title block of a plan in a corner: rows of (label, value), right edge at x1 (sheet 2/5, scale, step…)."""
    f, fv = font(size, False), font(size)
    lw = max(f.getlength(a.upper()) for a, _ in rows); vw = max(fv.getlength(str(b)) for _, b in rows)
    pad, rh = size * .6, size * 1.7
    x0, y1 = x1 - (lw + vw + pad * 4), y0 + rh * len(rows)
    with Plate(img, (x0 - 4, y0 - 4, x1 + 4, y1 + 4)) as p:
        p.rect(x0, y0, x1, y1, fill=PANEL, color=line, w=2)
        p.line([(x0 + lw + pad * 2, y0), (x0 + lw + pad * 2, y1)], line, 2)
        for i in range(1, len(rows)): p.line([(x0, y0 + rh * i), (x1, y0 + rh * i)], line, 2)
    for i, (a, b) in enumerate(rows):
        cy = y0 + rh * (i + .5)
        text(img, a.upper(), x0 + pad, cy, size, color, bold=False, anchor="lm")
        text(img, str(b), x1 - pad, cy, size, value_color, anchor="rm")
    return (x0, y0, x1, y1)

def xray(img, hidden, cx, cy, r, color=CYAN, label="", ring=True):
    """X-ray lens: inside the circle shows 'hidden' (an image of the same size with what's inside), ringed in cyan."""
    m = Image.new("L", img.size, 0)
    box = (int(cx - r - 2), int(cy - r - 2), int(cx + r + 3), int(cy + r + 3))
    big = Image.new("L", ((box[2] - box[0]) * SS, (box[3] - box[1]) * SS), 0)
    ImageDraw.Draw(big).ellipse([(cx - r - box[0]) * SS, (cy - r - box[1]) * SS, (cx + r - box[0]) * SS, (cy + r - box[1]) * SS], fill=255)
    m.paste(big.resize((box[2] - box[0], box[3] - box[1]), Image.LANCZOS), box[:2])
    img.paste(hidden, (0, 0), Image.composite(hidden.getchannel("A"), Image.new("L", m.size, 0), m) if hidden.mode == "RGBA" else m)
    if ring: lens_ring(img, cx, cy, r, color, label)

def lens_ring(img, cx, cy, r, color=CYAN, label=""):
    """Ring of the x-ray lens: cyan circle with four ticks and an optional label on top."""
    with Plate(img, (cx - r - 24, cy - r - 24, cx + r + 24, cy + r + 24)) as p:
        p.circle(cx, cy, r, color=color, w=3)
        p.circle(cx, cy, r + 9, color=mix(color, PANEL, .6), w=1.5)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p.line([(cx + dx * (r - 10), cy + dy * (r - 10)), (cx + dx * (r + 18), cy + dy * (r + 18))], color, 3)
    if label: text(img, label.upper(), cx + r * .72 + 10, cy - r * .72 - 10, 22, color, tracking=.25, anchor="lb")

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
