"""Automatic frame check: records the box (bbox) of everything drawn and warns about
  1) elements over the captions, 2) texts cut by the edge, 3) texts overlapping each other,
  4) large pieces or texts with low contrast against their surroundings (and no outline to save them).
Usage:  python3 -m channel.produce SPEC check"""
from contextlib import contextmanager
from PIL import ImageDraw
from .core import W, H
from .config import current as _current
_cfg = _current()

_OPS = ("ellipse", "rectangle", "rounded_rectangle", "polygon", "line", "arc", "chord", "pieslice", "text")
_orig = {k: getattr(ImageDraw.ImageDraw, k) for k in _OPS}

def _bbox_pts(xy):
    if hasattr(xy, "__len__") and len(xy) == 4 and all(isinstance(v, (int, float)) for v in xy):
        return [xy[0], xy[1], xy[2], xy[3]]
    pts = list(xy)
    if pts and isinstance(pts[0], (int, float)): pts = list(zip(pts[0::2], pts[1::2]))
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return [min(xs), min(ys), max(xs), max(ys)]

class Rec:
    def __init__(self): self.items = []; self.tag = "scene"; self.contrast = []; self.texts = []

# ---------- contrast ----------
def _rgb(c, im):
    if c is None: return None
    if isinstance(c, str):
        from PIL import ImageColor
        try: return ImageColor.getrgb(c)[:3]
        except Exception: return None
    if isinstance(c, int): return None
    return tuple(c[:3])

def _lum(c):
    def ch(v):
        v /= 255; return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    r, g, b = c; return .2126 * ch(r) + .7152 * ch(g) + .0722 * ch(b)

def similar(a, b):
    """True when two colors blend in: low luminance contrast AND small color difference."""
    la, lb = _lum(a), _lum(b); ratio = (max(la, lb) + .05) / (min(la, lb) + .05)
    dist = sum((x - y) ** 2 for x, y in zip(a, b)) ** .5
    return ratio < _cfg.contrast_ratio and dist < _cfg.contrast_dist

def _ring(im, bb, gap):
    """Colors just outside the box (what was already drawn around it)."""
    x0, y0, x1, y1 = [int(v) for v in bb]; w, h = im.size; px = im.load(); out = []
    n = 24
    for k in range(n):
        u = (k + .5) / n
        for (x, y) in ((x0 + (x1 - x0) * u, y0 - gap), (x0 + (x1 - x0) * u, y1 + gap), (x0 - gap, y0 + (y1 - y0) * u), (x1 + gap, y0 + (y1 - y0) * u)):
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h: out.append(px[x, y][:3])
    return out

def _contrast_probe(self, name, xy, a, kw, rec, scale):
    im = getattr(self, "_image", None)
    if im is None or im.mode != "RGB": return
    if name == "text":
        txt = a[0] if a else kw.get("text", "")
        if not str(txt).strip(): return
        sw = kw.get("stroke_width", 0) or 0
        fill = _rgb(kw.get("fill", a[1] if len(a) > 1 else None), im)
        stroke = _rgb(kw.get("stroke_fill"), im) if sw >= max(1, 2 * scale) else None
        bb = list(self.textbbox(xy, txt, font=kw.get("font"), anchor=kw.get("anchor"), stroke_width=sw))
        minsz = 14 * scale; label = f"text {str(txt)[:24]!r}"
        rec.texts.append((str(txt), bb, None))
    else:
        return                                  # shapes are checked as whole pieces (see element_wrap)
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    if fill is None or bw < minsz or bh < minsz * (.5 if name == "text" else 1): return
    if name != "text" and (bw >= .9 * im.size[0] or bh >= .6 * im.size[1]): return
    ring = _ring(im, bb, max(2, int(3 * scale)))
    if len(ring) < 20: return
    low = sum(similar(fill, r) for r in ring) / len(ring)
    if low < .5: return
    if stroke is not None and sum(similar(stroke, r) for r in ring) / len(ring) < .5: return   # the text's outline saves it
    k = W / im.size[0]
    msg = f"low contrast [SERIOUS]: {label} color {fill} blends into the background ({int(low * 100)}% of the edge)"
    if name == "text": rec.texts[-1] = (rec.texts[-1][0], rec.texts[-1][1], msg)
    else: rec.contrast.append((msg, [v * k for v in bb]))

def contrast_issues(rec):
    """Collects the contrast warnings. For texts with a shadow (two layers almost in the same place) only the top one counts."""
    out = list(rec.contrast); n = len(rec.texts)
    for i, (txt, bb, msg) in enumerate(rec.texts):
        if not msg: continue
        tol = max(4, (bb[3] - bb[1]) * .25)
        if any(rec.texts[j][0] == txt and abs(rec.texts[j][1][0] - bb[0]) <= tol and abs(rec.texts[j][1][1] - bb[1]) <= tol for j in range(i + 1, n)): continue
        out.append((msg, bb))
    return out

_REC = [None]                                   # active record (for pieces painted on a separate layer)

def register(bb, img=None, kind="piece", label=""):
    """Pieces painted on a separate layer (cartoon style) report their box here for the check."""
    rec = _REC[0]
    if rec is None or (img is not None and img.size != (W, H)): return
    rec.items.append((rec.tag, kind, label, list(bb)))

@contextmanager
def recording(rec):
    def wrap(name):
        f = _orig[name]
        def g(self, xy, *a, **kw):
            try:
                im = getattr(self, "_image", None)
                if rec.tag == "scene" and im is not None:
                    _contrast_probe(self, name, xy, a, kw, rec, im.size[0] / W)
            except Exception:
                pass
            try:
                if getattr(self, "_image", None) is not None and self._image.size != (W, H): raise StopIteration   # small canvases (pixel art) aren't checked here
                if name == "text":
                    txt = a[0] if a else kw.get("text", "")
                    bb = list(self.textbbox(xy, txt, font=kw.get("font"), anchor=kw.get("anchor"), stroke_width=kw.get("stroke_width", 0)))
                    rec.items.append((rec.tag, "text", str(txt), bb))
                else:
                    bb = _bbox_pts(xy); w = kw.get("width", 0) or 0
                    bb = [bb[0] - w / 2, bb[1] - w / 2, bb[2] + w / 2, bb[3] + w / 2]
                    rec.items.append((rec.tag, name, "", bb))
            except Exception:
                pass
            return f(self, xy, *a, **kw)
        return g
    for k in _OPS: setattr(ImageDraw.ImageDraw, k, wrap(k))
    _REC[0] = rec
    try: yield rec
    finally:
        _REC[0] = None
        for k in _OPS: setattr(ImageDraw.ImageDraw, k, _orig[k])

def _inter(a, b):
    return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))
def _area(a): return max(1, (a[2] - a[0]) * (a[3] - a[1]))

def analyze(items, margin=_cfg.check_margin):
    """Returns the list of problems (text) for one frame."""
    probs = []
    cap = [b for tg, k, s, b in items if tg == "caption"]
    capbox = [min(b[0] for b in cap) - margin, min(b[1] for b in cap) - margin, max(b[2] for b in cap) + margin, max(b[3] for b in cap) + margin] if cap else None
    scene = [(k, s, b) for tg, k, s, b in items if tg == "scene"]
    for k, s, b in scene:
        bw, bh = b[2] - b[0], b[3] - b[1]
        if k != "text" and (bw >= .9 * W or bh >= .6 * H): continue   # background / floor bands (texts are always checked)
        if capbox and _inter(b, capbox) > 0 and (k == "text" or bw * bh > 45 * 45):
            lvl = "minor (thin line)" if k in ("line", "arc") else "SERIOUS"
            probs.append((f"over the captions [{lvl}]: {k} {s!r}".replace(" ''", ""), int(b[3]) - int(capbox[1])))
        if k == "text" and (b[0] < 8 or b[2] > W - 8 or b[1] < 0):
            probs.append((f"text cut by the edge [SERIOUS]: {s!r}", int(max(-b[0], b[2] - W, -b[1]))))
    texts = [(s, b) for k, s, b in scene if k == "text" and s.strip()]
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            (s1, b1), (s2, b2) = texts[i], texts[j]
            if _inter(b1, b2) > .15 * min(_area(b1), _area(b2)) and s1 != s2:
                probs.append((f"overlapping texts [SERIOUS]: {s1!r} / {s2!r}", 0))
    return probs


# ---------- contrast per whole piece ----------
import numpy as np, random
_LUT = np.array([(v / 255 / 12.92 if v / 255 <= .03928 else ((v / 255 + .055) / 1.055) ** 2.4) for v in range(256)])
ACTIVE = None          # Rec active during the check
LOW_LIMIT = _cfg.contrast_limit        # fraction of the outline blending into the background before warning
_depth = [0]

def _lum_arr(a):
    return .2126 * _LUT[a[..., 0]] + .7152 * _LUT[a[..., 1]] + .0722 * _LUT[a[..., 2]]

def _target_image(args):
    if not args: return None
    x = args[0]
    from PIL import Image as _I
    if isinstance(x, ImageDraw.ImageDraw): return getattr(x, "_image", None)
    if isinstance(x, _I.Image): return x
    return None

SENTINEL = (255, 0, 255)

def true_mask(fn, args, kw, im):
    """Real silhouette: draws the piece on a magenta canvas (so parts the same color as the background show up too)."""
    from PIL import Image as _I
    probe = _I.new("RGB", im.size, SENTINEL)
    x = args[0]
    a2 = (ImageDraw.Draw(probe),) + tuple(args[1:]) if isinstance(x, ImageDraw.ImageDraw) else (probe,) + tuple(args[1:])
    st = random.getstate()
    try: fn(*a2, **kw)
    finally: random.setstate(st)
    return np.any(np.asarray(probe) != np.array(SENTINEL, dtype=np.uint8), axis=2)

def silhouette_low(before, after, scale, mask=None):
    """Fraction of the piece's outline that blends into what was behind it. None if it doesn't apply."""
    if mask is None: mask = np.any(before != after, axis=2)
    area = int(mask.sum()); total = mask.size
    if area < 3000 * scale * scale or area > .6 * total: return None
    ys_, xs_ = np.nonzero(mask)
    if xs_.max() - xs_.min() >= .9 * mask.shape[1] or ys_.max() - ys_.min() >= .6 * mask.shape[0]: return None   # background bands
    lb, la = _lum_arr(before.astype(int)), _lum_arr(after.astype(int))
    sims = []
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        nb = np.roll(mask, (dy, dx), axis=(0, 1))
        edge = mask & ~nb                       # piece pixel whose neighbor (−dy,−dx)… is outside
        ys, xs = np.nonzero(edge)
        oy, ox = ys - dy, xs - dx
        ok = (oy >= 0) & (oy < mask.shape[0]) & (ox >= 0) & (ox < mask.shape[1])
        ys, xs, oy, ox = ys[ok], xs[ok], oy[ok], ox[ok]
        if len(ys) == 0: continue
        if len(ys) > 4000:
            idx = np.random.default_rng(0).choice(len(ys), 4000, replace=False); ys, xs, oy, ox = ys[idx], xs[idx], oy[idx], ox[idx]
        outc, l2 = before[oy, ox].astype(int), lb[oy, ox]
        sim = np.ones(len(ys), dtype=bool)
        for j in (0, 3, 6, 9, 12, 15, 18):               # outline and nearby fill: enough if something stands out
            j = int(round(j * scale)) if j else 0
            iy, ix = np.clip(ys + dy * j, 0, mask.shape[0] - 1), np.clip(xs + dx * j, 0, mask.shape[1] - 1)
            inside = mask[iy, ix]
            l1 = la[iy, ix]
            ratio = (np.maximum(l1, l2) + .05) / (np.minimum(l1, l2) + .05)
            dist = np.sqrt(((after[iy, ix].astype(int) - outc) ** 2).sum(axis=1))
            sim &= ~inside | ((ratio < _cfg.contrast_ratio) & (dist < _cfg.contrast_dist))
        sims.append(sim)
    if not sims: return None
    allp = np.concatenate(sims)
    if len(allp) < 40: return None
    return float(allp.mean()), np.argwhere(mask)

_SKIP = ("rect", "text", "chip", "rich_caption", "bigtext") + tuple(_cfg.contrast_skip)

def element_wrap(fn, name):
    """Wraps a function that draws a piece: during a check, measures the contrast of its silhouette."""
    if getattr(fn, "_dqa_wrapped", False) or name in _SKIP: return fn
    def g(*args, **kw):
        rec = ACTIVE
        if rec is None or _depth[0] > 0: return fn(*args, **kw)
        im = _target_image(args)
        if im is None or im.mode != "RGB": return fn(*args, **kw)
        before = np.asarray(im).copy()
        _depth[0] += 1
        try:
            try: mask = true_mask(fn, args, kw, im)
            except Exception: mask = None
            out = fn(*args, **kw)
        finally: _depth[0] -= 1
        im2 = _target_image(args) or im
        after = np.asarray(im2 if not hasattr(out, "size") or out is None else im2)
        try:
            r = silhouette_low(before, np.asarray(im), im.size[0] / W, mask)
            if r and r[0] >= LOW_LIMIT:
                ys, xs = r[1][:, 0], r[1][:, 1]; k = W / im.size[0]
                bb = [xs.min() * k, ys.min() * k, xs.max() * k, ys.max() * k]
                lvl = "SERIOUS" if r[0] >= .5 else "review"
                rec.contrast.append((f"low contrast [{lvl}]: '{name}' blends into the background ({int(r[0] * 100)}% of its outline) near x={int((bb[0] + bb[2]) / 2)}, y={int((bb[1] + bb[3]) / 2)}", bb))
        except Exception:
            pass
        return out
    g._dqa_wrapped = True; g.__name__ = getattr(fn, "__name__", name); g.__wrapped__ = fn
    return g
