"""Sketch style: hand-drawn marker look. Every line is a slightly wobbly, tapered ink stroke; shapes are flat colors
with a loose outline that overshoots where it closes; shading is done with loose hatching. Near-black ink
(`Channel.sketch_ink`) on light backgrounds. It's optional and lives apart: the other styles don't change.

Pieces in this style take the image (img), like the cartoon style, because they're painted on a separate layer:

    from reels_engine.sketch.humans import doodle
    a = doodle(img, 540, FLOOR, 1.0, outfit="hoodie", mood="shocked", arms=("up", "up"))
    say(ImageDraw.Draw(img), "What?!", a["mouth"], a["head_r"])

The wobble comes from `seed`: the same seed always draws the same lines. Pass a seed that changes a few times per
second (`seed=int(c.t * 8)`) for the "boiling lines" look of hand-drawn animation.

Pieces: `humans` (doodle), `props` (money, school, charts), `everyday` (coffee, car, house, phone…),
`history` (pyramid, temple, weapons, helmets, doodle dressed as Roman/viking/pharaoh/Greek/knight/Aztec/Maya),
`modern` (1800s: sultan, admiral, sailor, palace, warship, fire, smoke),
`sports` (balls, gear, trophy, podium, goal, hoop, doodle as soccer player, boxer, runner, referee…),
`finance` (bank, safe, ATM, charts, gauge, contract, debt ball and chain, goal thermometer…).

To draw your own pieces in this style: `with Pen(img, box, seed) as p: p.shape(...); p.stroke(...)`."""
import copy
import functools
import inspect
import math
import os
import random
import types
from collections import OrderedDict
from contextlib import contextmanager

from PIL import Image, ImageDraw, ImageFont
from ..config import current as _current

_cfg = _current()
INK = _cfg.sketch_ink
FONT = _cfg.sketch_font or _cfg.font_bold
SS = 2                                    # the layer is drawn at double size and scaled down (soft edges)

WHITE = (255, 255, 255)
SHADE = (226, 226, 229)                   # floor shadows
SKIN_SHADE = (222, 222, 226)              # shadow side of the heads
RED, RED_D = (214, 38, 38), (150, 20, 24)
GREEN, GREEN_D, GREEN_L = (92, 178, 80), (36, 112, 46), (170, 220, 150)
MONEY, MONEY_D = (38, 170, 60), (18, 105, 38)
GLASS, GLASS_D = (228, 240, 242), (190, 214, 220)
WOOD, WOOD_D = (180, 116, 64), (128, 78, 40)
BAND = (238, 228, 196)
BLUE = (70, 120, 200)
MOUTH = (110, 28, 30)

# ---------- shapes ----------
def resample(pts, step):
    """Same path with a point every 'step' px."""
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        out += [(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n) for k in range(1, n + 1)]
    return out

def spline(pts, closed=False, n=10):
    """Smooth curve through all the points (Catmull-Rom)."""
    p = list(pts)
    p = [p[-1]] + p + [p[0], p[1]] if closed else [p[0]] + p + [p[-1]]
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                   + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(p[-2])
    return out

def ellipse(cx, cy, rx, ry, rot=0.0, n=48):
    """Points of an ellipse, optionally rotated (radians)."""
    c, s = math.cos(rot), math.sin(rot)
    return [(cx + rx * math.cos(a) * c - ry * math.sin(a) * s, cy + rx * math.cos(a) * s + ry * math.sin(a) * c)
            for a in (2 * math.pi * k / n for k in range(n))]

def rrect(x0, y0, x1, y1, r, n=6):
    """Points of a rectangle with rounded corners."""
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    pts = []
    for cx, cy, a in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        pts += [(cx + r * math.cos(math.radians(a + 90 * k / n)), cy + r * math.sin(math.radians(a + 90 * k / n)))
                for k in range(n + 1)]
    return pts

def rotated(pts, cx, cy, ang):
    """Points turned 'ang' radians around (cx, cy)."""
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]

# ---------- pen ----------
class Pen:
    """Transparent layer with screen coordinates. On leaving the 'with' block it's scaled down and pasted on img.
    Widths (w) are in screen px. The automatic check gets the piece's real outline."""
    def __init__(self, img, box, seed=1, ss=SS):
        self.target = img
        self.ox, self.oy = int(math.floor(box[0])), int(math.floor(box[1]))
        self.w, self.h = max(1, int(math.ceil(box[2])) - self.ox), max(1, int(math.ceil(box[3])) - self.oy)
        self.ss = ss
        self.img = Image.new("RGBA", (self.w * ss, self.h * ss), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.rng = random.Random(seed)
    def __enter__(self): return self
    def __exit__(self, *exc):
        if exc[0] is None: self.paste()
    def _p(self, pts):
        return [((x - self.ox) * self.ss, (y - self.oy) * self.ss) for x, y in pts]

    def wobble(self, pts, amp=1.6, closed=False, overshoot=0.0):
        """The path resampled and pushed sideways with smooth noise (the hand's tremor)."""
        pts = list(pts)
        if closed:
            pts = pts + [pts[0]]
            if overshoot:                                           # keep drawing a bit past the start
                total, acc, extra = sum(math.dist(a, b) for a, b in zip(pts, pts[1:])), 0, []
                for a, b in zip(pts, pts[1:]):
                    extra.append(b); acc += math.dist(a, b)
                    if acc > total * overshoot: break
                pts += extra
        r = resample(pts, 3)
        if len(r) < 2 or not amp: return r
        R = self.rng
        l1, l2, f1, f2 = R.uniform(70, 120), R.uniform(22, 34), R.uniform(0, 6.3), R.uniform(0, 6.3)
        out, s = [], 0.0
        for i, (x, y) in enumerate(r):
            a, b = r[max(0, i - 1)], r[min(len(r) - 1, i + 1)]
            nx, ny = -(b[1] - a[1]), b[0] - a[0]; ln = math.hypot(nx, ny) or 1
            if i: s += math.dist(r[i - 1], r[i])
            o = amp * (.7 * math.sin(s / l1 * 6.283 + f1) + .3 * math.sin(s / l2 * 6.283 + f2))
            out.append((x + nx / ln * o, y + ny / ln * o))
        return out

    def ink(self, path, w, color=INK, taper=True):
        """Draws an already wobbled path as a round stroke whose pressure varies (thinner at the ends)."""
        if len(path) < 2: return
        total = sum(math.dist(a, b) for a, b in zip(path, path[1:])) or 1
        ph, s = self.rng.uniform(0, 6.3), 0.0
        for a, b in zip(path, path[1:]):
            s += math.dist(a, b)
            k = 1 + .13 * math.sin(s / 41 + ph)
            if taper: k *= min(1.0, .45 + .55 * min(s, total - s) / (2.5 * w + 1))
            ww = max(1.0, w * k * self.ss)
            (pa, pb) = self._p([a, b])
            self.d.line([pa, pb], fill=color, width=int(round(ww)))
            self.d.ellipse([pb[0] - ww / 2, pb[1] - ww / 2, pb[0] + ww / 2, pb[1] + ww / 2], fill=color)

    def poly(self, pts, color):
        """Plain fill, no outline."""
        self.d.polygon(self._p(pts), fill=color)

    def stroke(self, pts, w=6, color=INK, amp=1.6, closed=False, taper=True, smooth=False):
        """Hand-drawn line through the points. Returns the drawn path."""
        if smooth: pts = spline(pts, closed)
        p = self.wobble(pts, amp, closed, overshoot=.05 if closed else 0)
        self.ink(p, w, color, taper)
        return p

    def shape(self, pts, fill=None, w=6, color=INK, amp=1.6, smooth=False):
        """Flat fill plus a loose outline."""
        if smooth: pts = spline(pts, closed=True)
        if fill is not None: self.poly(self.wobble(pts, amp * .5, closed=True), fill)
        if w: self.stroke(pts, w, color, amp, closed=True)

    def limb(self, pts, w, fill, edge=5):
        """Outlined tube (sleeve, arm): an ink stroke with a narrower color stroke on top."""
        p = self.wobble(spline(pts), 1.2)
        self.ink(p, w + 2 * edge, INK, taper=False)
        self.ink(p, w, fill, taper=False)
        return p

    def blob(self, cx, cy, rx, ry, color=SHADE):
        """Plain ellipse (floor shadows)."""
        self.poly(ellipse(cx, cy, rx, ry), color)

    @contextmanager
    def clip(self, pts):
        """Everything drawn inside the block only shows inside the shape."""
        base, layer = self.img, self.img.copy()
        mask = Image.new("L", base.size, 0)
        ImageDraw.Draw(mask).polygon(self._p(pts), fill=255)
        self.img, self.d = layer, ImageDraw.Draw(layer)
        try:
            yield
        finally:
            base.paste(layer, (0, 0), mask)
            self.img, self.d = base, ImageDraw.Draw(base)

    def hatch(self, pts, color, gap=14, ang=-.9, w=3):
        """Loose parallel marker strokes inside a shape."""
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        R = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) / 2 + 5
        dx, dy = math.cos(ang), math.sin(ang)
        with self.clip(pts):
            t = -R
            while t < R:
                ox, oy = cx - dy * t, cy + dx * t
                self.stroke([(ox - dx * R, oy - dy * R), (ox + dx * R, oy + dy * R)], w, color, amp=.8)
                t += gap * self.rng.uniform(.8, 1.25)

    def text(self, s, cx, cy, size, fill=INK, stroke=None, sw=0, warp=1.3, font=None):
        """Bold lettering centered on (cx, cy), slightly warped so it doesn't look typed."""
        f = ImageFont.truetype(font or FONT, max(8, int(size * self.ss)))
        layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        (q,) = self._p([(cx, cy)])
        ImageDraw.Draw(layer).text(q, s, font=f, fill=fill, anchor="mm", stroke_width=int(sw * self.ss),
                                   stroke_fill=stroke or fill)
        if warp:
            import numpy as np
            a = np.asarray(layer); h, w = a.shape[:2]
            yy, xx = np.mgrid[0:h, 0:w]
            ph = self.rng.uniform(0, 6.3)
            sx = (xx + warp * self.ss * np.sin(yy / (37 * self.ss) + ph)).astype(int).clip(0, w - 1)
            sy = (yy + warp * self.ss * np.sin(xx / (53 * self.ss) + ph * 1.7)).astype(int).clip(0, h - 1)
            layer = Image.fromarray(a[sy, sx])
        self.img.alpha_composite(layer)
        self.d = ImageDraw.Draw(self.img)

    def paste(self):
        small = self.img.convert("RGBa").resize((self.w, self.h), Image.LANCZOS).convert("RGBA")
        _put(self.target, small, (self.ox, self.oy), small.getbbox())
        return ImageDraw.Draw(self.target)

def _put(target, small, pos, bb):
    """Pastes a finished layer on the image, reports it to the check and to the piece being recorded (if any)."""
    target.paste(small, pos, small)
    if bb:
        from ..check import register
        register((bb[0] + pos[0], bb[1] + pos[1], bb[2] + pos[0], bb[3] + pos[1]), target)
    if _REC: _REC[-1].append((target, small, pos, bb))

# ---------- piece cache ----------
# With a fixed seed a piece drawn twice with the same arguments gives the same layers, so they're kept and pasted
# again instead of drawn again (most of a frame repeats from the previous one). The result is pixel-identical.
# REELS_PIECE_CACHE=0 turns it off; REELS_PIECE_CACHE_MB sets the memory per process (default 300).
_ON = os.environ.get("REELS_PIECE_CACHE", "1") != "0"
_LIMIT = int(os.environ.get("REELS_PIECE_CACHE_MB", "300")) << 20
_CACHE, _SIZE, _REC = OrderedDict(), [0], []

def _freeze(v):
    """Hashable copy of an argument; TypeError for anything that could change behind our back."""
    if v is None or isinstance(v, (bool, int, float, str, bytes)): return v
    if isinstance(v, (tuple, list)): return (type(v).__name__,) + tuple(_freeze(x) for x in v)
    if isinstance(v, dict): return ("dict",) + tuple(sorted((k, _freeze(x)) for k, x in v.items()))
    if isinstance(v, (types.FunctionType, types.BuiltinFunctionType)) and not v.__closure__: return v
    raise TypeError(type(v).__name__)

def cached(fn):
    """Remembers what a piece pastes (it must only draw through Pen) and repeats it when called again with the same
    arguments. Every public sketch piece uses it; a channel can use it on its own sketch pieces too."""
    if getattr(fn, "_cached", False): return fn
    @functools.wraps(fn)
    def piece(img, *a, **kw):
        from ..check import _REC as checking
        if not _ON or checking[0] is not None: return fn(img, *a, **kw)
        try:
            key = (fn.__module__, fn.__qualname__, img.size, img.mode, _freeze(a), _freeze(kw)); hash(key)
        except TypeError:
            return fn(img, *a, **kw)
        hit = _CACHE.get(key)
        if hit is not None:
            _CACHE.move_to_end(key)
            for small, pos, bb in hit[0]: _put(img, small, pos, bb)
            return copy.deepcopy(hit[1])
        rec = []; _REC.append(rec)
        try: out = fn(img, *a, **kw)
        finally: _REC.pop()
        if _REC: _REC[-1].extend(rec)                         # a piece inside another piece: the outer one keeps it too
        if all(t is img for t, *_ in rec):
            try: ret = copy.deepcopy(out)
            except Exception: return out
            _CACHE[key] = ([(s, p, b) for _, s, p, b in rec], ret)
            _SIZE[0] += sum(s.width * s.height * 4 for _, s, _, _ in rec)
            while _SIZE[0] > _LIMIT and len(_CACHE) > 1:
                ops, _ = _CACHE.popitem(last=False)[1]
                _SIZE[0] -= sum(s.width * s.height * 4 for s, _, _ in ops)
        return out
    piece._cached = True
    return piece

def cache_pieces(ns):
    """Applies `cached` to every public piece (first argument `img`) defined in a module's namespace."""
    for k, v in list(ns.items()):
        if k.startswith("_") or not inspect.isfunction(v) or v.__module__ != ns["__name__"]: continue
        if next(iter(inspect.signature(v).parameters), "") == "img": ns[k] = cached(v)
