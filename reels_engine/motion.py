"""Movimiento estilo GSAP en Python: curvas (ease), interpolación por tiempo, capas con escala/rotación/transparencia,
subtítulos palabra por palabra y resplandor. Curvas de Robert Penner (las mismas que usan GSAP, CSS y After Effects)."""
import math
from functools import lru_cache
from PIL import Image, ImageDraw
from .core import W, H, F, WHITE, YEL, BLK, CAP_Y
from .config import current as _current
_cfg = _current()
_CF, _CH, _CS = _cfg.caption_fill, _cfg.caption_highlight, _cfg.caption_stroke

# ---------- curvas (u de 0 a 1 -> progreso) ----------
def linear(u): return u
def sine_in_out(u): return -(math.cos(math.pi * u) - 1) / 2
def quad_out(u): return 1 - (1 - u) ** 2
def cubic_out(u): return 1 - (1 - u) ** 3
def expo_out(u): return 1 if u >= 1 else 1 - 2 ** (-10 * u)
def power_in(u, p=3): return u ** p
def back_out(u, s=1.70158):
    u -= 1; return u * u * ((s + 1) * u + s) + 1
def back_in(u, s=1.70158): return u * u * ((s + 1) * u - s)
def elastic_out(u, amp=1.0, period=.35):
    if u <= 0 or u >= 1: return max(0, min(1, u))
    return amp * 2 ** (-10 * u) * math.sin((u - period / 4) * (2 * math.pi) / period) + 1
def bounce_out(u):
    n, dd = 7.5625, 2.75
    if u < 1 / dd: return n * u * u
    if u < 2 / dd: u -= 1.5 / dd; return n * u * u + .75
    if u < 2.5 / dd: u -= 2.25 / dd; return n * u * u + .9375
    u -= 2.625 / dd; return n * u * u + .984375

def tw(t, t0, dur, a, b, ease=cubic_out):
    """Valor que va de a a b entre t0 y t0+dur con la curva 'ease' (antes: a, después: b)."""
    u = 0 if dur <= 0 else max(0.0, min(1.0, (t - t0) / dur))
    return a + (b - a) * ease(u)

def yoyo(t, t0, period, a, b, ease=sine_in_out):
    """Va y viene entre a y b (flotar, respirar). Determinista: depende solo de t."""
    if t < t0: return a
    k = ((t - t0) / period) % 2
    return a + (b - a) * ease(k if k < 1 else 2 - k)

def shake(t, t0, dur, amp=10, freq=40):
    if not (t0 <= t < t0 + dur): return 0.0
    return amp * math.sin((t - t0) * freq) * (1 - (t - t0) / dur)

# ---------- capas ----------
def layer(img, draw_fn, x, y, size=600, sx=1.0, sy=1.0, rot=0.0, alpha=1.0, **kw):
    """Dibuja draw_fn(d, cx, cy, **kw) en una capa y la pega centrada en (x, y) con escala (sx, sy), giro y transparencia.
    Sirve para aplastar/estirar (squash & stretch), girar o desvanecer cualquier personaje."""
    if alpha <= .01 or sx <= .01 or sy <= .01: return ImageDraw.Draw(img)
    L = Image.new("RGBA", (size, size), (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(L), size / 2, size / 2, **kw)
    if sx != 1 or sy != 1: L = L.resize((max(1, int(size * sx)), max(1, int(size * sy))), Image.BICUBIC)
    if rot: L = L.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1: L.putalpha(L.getchannel("A").point(lambda v: int(v * alpha)))
    img.paste(L, (int(x - L.width / 2), int(y - L.height / 2)), L)
    return ImageDraw.Draw(img)

@lru_cache(maxsize=32)
def _glow(r, col):
    g = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0)); px = g.load()
    for yy in range(2 * r):
        for xx in range(2 * r):
            dd = math.hypot(xx - r, yy - r) / r
            if dd < 1: px[xx, yy] = (*col, int(255 * (1 - dd) ** 2))
    return g

def glow(img, x, y, r, col=(255, 250, 210), alpha=.5):
    """Resplandor suave (radial) centrado en (x, y)."""
    if alpha <= .01 or r < 4: return ImageDraw.Draw(img)
    g = _glow(int(r), tuple(col))
    if alpha < 1: g = g.copy(); g.putalpha(g.getchannel("A").point(lambda v: int(v * alpha)))
    img.paste(g, (int(x - r), int(y - r)), g)
    return ImageDraw.Draw(img)

# ---------- subtítulos palabra por palabra ----------
def caption_words(d, text, lt, y=CAP_Y, size=_cfg.caption_size, maxw=960, stagger=.12, dur=.3):
    """Como rich_caption, pero cada palabra salta con 'back_out' una tras otra. *resaltado* en amarillo."""
    f = F(size); hl = False; words = []
    for w in text.split():
        pieces = []
        for j, part in enumerate(w.split("*")):
            if j > 0: hl = not hl
            if part: pieces.append((part, hl))
        words.append(pieces)
    sp = d.textlength(" ", font=f); lines, cur, cw = [], [], 0
    for pcs in words:
        ww = sum(d.textlength(p, font=f) for p, _ in pcs)
        if cur and cw + sp + ww > maxw: lines.append((cur, cw)); cur, cw = [], 0
        cw = cw + (sp if cur else 0) + ww; cur.append((pcs, ww))
    if cur: lines.append((cur, cw))
    lh = size * 1.22; y0 = y - lh * (len(lines) - 1) / 2; k = 0
    for li, (ln, lw) in enumerate(lines):
        x = W / 2 - lw / 2
        for pcs, ww in ln:
            t0 = k * stagger; k += 1
            if lt >= t0:
                sc = tw(lt, t0, dur, .55, 1.0, back_out); dy = tw(lt, t0, dur, 30, 0, cubic_out)
                fs = F(max(8, int(size * sc))); cx = x + ww / 2; px = cx - sum(d.textlength(p, font=fs) for p, _ in pcs) / 2
                for p, h in pcs:
                    d.text((px, y0 + li * lh + dy), p, font=fs, fill=_CH if h else _CF, anchor="lm", stroke_width=max(4, int(size * sc * .14)), stroke_fill=_CS)
                    px += d.textlength(p, font=fs)
            x += ww + sp

# ---------- fondos con profundidad (degradado radial, viñeta, espacio) ----------
import numpy as _np

@lru_cache(maxsize=16)
def _radial(stops, cx, cy, rx, ry):
    yy, xx = _np.mgrid[0:H, 0:W].astype(_np.float32)
    dist = _np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    pos = _np.array([p for p, _ in stops], _np.float32); cols = _np.array([c for _, c in stops], _np.float32)
    out = _np.stack([_np.interp(dist, pos, cols[:, k]) for k in range(3)], axis=2)
    return Image.fromarray(out.clip(0, 255).astype(_np.uint8))

def radial_bg(stops=((0, (27, 21, 80)), (.55, (10, 10, 42)), (1, (5, 5, 21))), cx=540, cy=670, rx=760, ry=1250):
    """Fondo con degradado radial (centro iluminado, orillas oscuras). stops=((posición 0..1, color), ...). Cacheado."""
    return _radial(tuple((p, tuple(c)) for p, c in stops), cx, cy, rx, ry).copy()

@lru_cache(maxsize=8)
def _vig(strength):
    yy, xx = _np.mgrid[0:H, 0:W].astype(_np.float32)
    dist = _np.sqrt(((xx - W / 2) / (W * .75)) ** 2 + ((yy - H / 2) / (H * .7)) ** 2)
    a = (dist.clip(0, 1) ** 2 * 255 * strength).astype(_np.uint8)
    v = Image.new("RGBA", (W, H), (0, 0, 0, 0)); v.putalpha(Image.fromarray(a)); return v

def vignette(img, strength=.55):
    """Oscurece suavemente las orillas (da profundidad a cualquier fondo)."""
    img.paste(_vig(strength), (0, 0), _vig(strength)); return ImageDraw.Draw(img)

_SPACE_STARS = None
def space_bg(t=0.0, n=170, seed=7, stops=((0, (27, 21, 80)), (.55, (10, 10, 42)), (1, (5, 5, 21)))):
    """Espacio con degradado radial y estrellas que titilan (distinto brillo y tamaño)."""
    global _SPACE_STARS
    import random as _r
    if _SPACE_STARS is None or _SPACE_STARS[0] != (n, seed):
        rnd = _r.Random(seed); _SPACE_STARS = ((n, seed), [(rnd.uniform(0, W), rnd.uniform(0, 1450), rnd.uniform(1, 3.2), rnd.uniform(0, 6.28), rnd.uniform(.4, 1)) for _ in range(n)])
    img = radial_bg(stops); d = ImageDraw.Draw(img)
    for x, y, r, ph, b in _SPACE_STARS[1]:
        a = b * (.55 + .45 * math.sin(t * 2.5 + ph)); c = int(110 + 140 * a)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(c, c, min(255, c + 25)))
    return img

@lru_cache(maxsize=32)
def _sphere(r, light, dark):
    n = 2 * r; yy, xx = _np.mgrid[0:n, 0:n].astype(_np.float32)
    inside = ((xx - r) ** 2 + (yy - r) ** 2) <= (r - 2) ** 2
    lx, ly = xx - r * .62, yy - r * .55                      # luz arriba a la izquierda
    hl = (1 - _np.sqrt(lx ** 2 + ly ** 2) / (r * 1.1)).clip(0, 1) ** 1.6
    sh = (_np.sqrt((xx - r * .62) ** 2 + (yy - r * .55) ** 2) / (r * 1.5)).clip(0, 1) ** 2.2
    a_hl = (hl * 255 * light) * inside; a_sh = (sh * 255 * dark) * inside
    L = _np.zeros((n, n, 4), _np.uint8); L[..., :3] = 255; L[..., 3] = a_hl.clip(0, 255)
    D = _np.zeros((n, n, 4), _np.uint8); D[..., :3] = (10, 10, 40); D[..., 3] = a_sh.clip(0, 255)
    return Image.fromarray(D), Image.fromarray(L)

def sphere_shade(img, cx, cy, r, light=.35, dark=.28):
    """Luz y sombra de esfera sobre algo redondo ya dibujado (planetas, luna, pelotas): le da volumen."""
    D, L = _sphere(int(r), light, dark); pos = (int(cx - r), int(cy - r))
    if img.mode == "RGBA":                                   # en capas transparentes: mezclar sin perforar el alfa
        for X in (D, L): img.alpha_composite(X, dest=pos)
    else:
        img.paste(D, pos, D); img.paste(L, pos, L)
    return ImageDraw.Draw(img)
