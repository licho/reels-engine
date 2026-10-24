"""Cross-section template of the blueprint style: a cut of the ground seen from the side, with a skyline in white
line, textured layers (fill, clay, wet clay, sand, gravel, rock, water), the water table in dashed cyan, a measuring
ruler and the ground sinking against its original level.

    a = cross_section(img, (40, 800, 1040, 1320), [("clay", 230, "CLAY"), ("gravel", 150), ("rock", 0)],
                      water=40, sink=tw(c.lt, 1, 4, 0, 30), ruler=(2, 20), t=c.t)
    callout(img, "AQUIFER", 600, a["layers"][1][0] + 60, 760, 1000)

Layers go from the surface down: (kind, height_px[, label]) or dict(kind=, h=, label=, color=); the last one fills
down to the bottom. The function returns where things ended up (ground, surface, water, layers) to place labels."""
import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw
from . import Plate, text, mix, WHITE, CYAN, GRAY, DIM, ACCENT, PANEL, GROUND, SS

_WET = ("wet_clay", "sand_wet")

def _layer(spec):
    if isinstance(spec, dict): return spec["kind"], spec.get("h", 0), spec.get("label", ""), spec.get("color")
    kind, h, *rest = spec
    return kind, h, (rest[0] if rest else ""), None

def _base(kind, color):
    if color: return tuple(color)
    return GROUND.get({"wet_clay": "clay", "sand_wet": "sand"}.get(kind, kind), GROUND["fill"])

@lru_cache(maxsize=48)
def _texture(kind, w, h, color, seed):
    """Fill pattern of a ground layer, drawn at double size once and reused."""
    R = random.Random(f"{kind}:{seed}")
    big = Image.new("RGBA", (w * SS, h * SS), color + (255,)); d = ImageDraw.Draw(big)
    line = mix(color, WHITE, .16); speck = mix(color, WHITE, .1)
    def wavy(gap, amp):
        y = gap * R.uniform(.3, 1)
        while y < h:
            ph, per = R.uniform(0, 6.3), R.uniform(140, 260)
            d.line([(x * SS, (y + amp * math.sin(x / per * 6.283 + ph)) * SS) for x in range(0, w + 8, 8)], fill=line, width=SS)
            y += gap * R.uniform(.75, 1.25)
    if kind in ("clay", "wet_clay", "fill"):
        wavy(24 if kind != "fill" else 40, 3)
        for _ in range(w * h // 900):
            x, y = R.uniform(0, w), R.uniform(0, h); r = R.uniform(.8, 1.6)
            d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=speck)
    elif kind in ("sand", "sand_wet"):
        for _ in range(w * h // 160):
            x, y = R.uniform(0, w), R.uniform(0, h); r = R.uniform(.7, 1.5)
            d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=mix(color, WHITE, R.uniform(.12, .3)))
    elif kind == "gravel":
        ring = mix(color, WHITE, .22)
        for _ in range(w * h // 500):
            x, y = R.uniform(0, w), R.uniform(0, h); r = R.choice((3, 4, 5, 6, 8, 10))
            d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], outline=ring, width=SS + (r > 6))
    elif kind == "rock":
        for t in range(-h, w, 20):
            d.line([(t * SS, h * SS), ((t + h) * SS, 0)], fill=mix(color, WHITE, .12), width=SS)
    elif kind == "water":
        for _ in range(w * h // 1400):
            x, y = R.uniform(0, w), R.uniform(0, h)
            d.line([(x * SS, y * SS), ((x + R.uniform(14, 30)) * SS, y * SS)], fill=mix(color, CYAN, .45), width=SS)
    return big.resize((w, h), Image.LANCZOS)

@lru_cache(maxsize=48)
def _dots(w, h, seed):
    """Water droplets inside a wet layer (x, y, phase)."""
    R = random.Random(seed * 7 + 1)
    return [(R.uniform(6, w - 6), R.uniform(6, h - 6), R.uniform(0, 6.3)) for _ in range(w * h // 1600)]

def _wave(x, k, seed): return 3 * math.sin(x / (160 + 23 * k) * 6.283 + seed + k * 1.9)

def _skyline(w, top, seed):
    R = random.Random(seed); out, x = [], R.uniform(10, 30)
    while x < w - 150:
        bw = R.choice((60, 70, 80, 90, 110)); bh = R.choice((60, 70, 90, 110, 150, 190))
        out.append((x, bw, min(bh, top))); x += bw + R.choice((12, 16, 40, 80))
    return out

def building(p, x, base, w, h, color=WHITE, fill=PANEL, window=None, lw=3):
    """Outline of a building with a grid of windows, standing on (x, base) (x = left side); draws on a Plate."""
    p.rect(x, base - h, x + w, base, fill=fill, color=color, w=lw)
    win = window or mix(fill, color, .45)
    cols = max(1, int((w - 14) // 16)); rows = max(1, int((h - 14) // 18))
    gx = (w - cols * 16 + 6) / 2
    for i in range(cols):
        for j in range(rows):
            wx, wy = x + gx + i * 16, base - h + 10 + j * 18
            if wy + 9 < base - 6: p.rect(wx, wy, wx + 9, wy + 9, fill=win)

def cross_section(img, box, layers, ground=.28, buildings=None, sink=0.0, water=None, water_x=.8, ruler=None,
                  labels=True, reveal=1.0, t=0.0, seed=1, frame=DIM):
    """Cross-section of the ground with buildings, textured layers, water table, ruler and sinking."""
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = x1 - x0, y1 - y0
    gy = y0 + (ground * h if ground < 1 else ground)              # original ground level
    sy = gy + sink                                                 # surface now
    # where each layer ends: the layers above the soft one (the first wet one) go down with the surface and the soft
    # one gets thinner, like clay that loses its water
    specs, bounds, acc = [_layer(L) for L in layers], [], gy
    soft = next((i for i, (kind, *_) in enumerate(specs) if kind in _WET), 0)
    for i, (kind, lh, label, color) in enumerate(specs):
        a = acc + (sink if i <= soft else 0)
        acc = acc + lh if lh and i < len(specs) - 1 else y1
        bounds.append((a, max(a, acc + (sink if i < soft else 0))))
    sec = Image.new("RGBA", (w, h), PANEL + (255,))
    for i, ((kind, lh, label, color), (a, b)) in enumerate(zip(specs, bounds)):
        if b <= a: continue
        tex = _texture(kind, w, int(math.ceil(y1 - gy)) + 4, _base(kind, color), seed + i)
        mask = Image.new("L", (w, h), 0); md = ImageDraw.Draw(mask)
        top_edge = [(x, a - y0 + (_wave(x, i, seed) if i else 0)) for x in range(0, w + 10, 10)]
        bot_edge = [(x, b - y0 + 2 + _wave(x, i + 1, seed)) for x in range(w + 10, -10, -10)] if i < len(specs) - 1 else [(w, h), (0, h)]
        md.polygon(top_edge + bot_edge, fill=255)
        sec.paste(tex.crop((0, 0, w, h)), (0, int(round(a - y0))), mask.crop((0, int(round(a - y0)), w, h + int(round(a - y0)))))
    # lines on top: boundaries, wet dots, water table, buildings, ground, original level
    full = Image.new("RGBA", img.size, (0, 0, 0, 0))
    full.paste(sec, (x0, y0))
    with Plate(full, (x0, y0, x1, y1)) as p:
        for i, ((kind, *_), (a, b)) in enumerate(zip(specs, bounds)):
            if i < len(specs) - 1 and b > a:
                p.line([(x0 + x, b + _wave(x, i + 1, seed)) for x in range(0, w + 10, 10)], mix(_base(kind, None), WHITE, .35), 2)
            if kind in _WET:
                wy = gy + water if water is not None else a
                for dx, dy, ph in _dots(w, int(y1 - gy) + 4, seed + i):
                    yy = a + dy
                    if yy < max(a + 6, wy + 6) or yy > b - 6: continue
                    r = 2.2 + .8 * math.sin(t * 2 + ph)
                    p.circle(x0 + dx, yy, r, fill=mix(_base(kind, None), CYAN, .55 + .3 * math.sin(t * 1.3 + ph)))
        if water is not None:
            wy = gy + water
            p.dashed([(x0 + 4, wy), (x1 - (70 if ruler else 4), wy)], CYAN, 3, 22, 12, phase=t * 30)
            mx = x0 + w * water_x
            p.poly([(mx - 16, wy - 30), (mx + 16, wy - 30), (mx, wy - 2)], fill=PANEL, color=CYAN, w=3)
            p.line([(mx - 12, wy + 9), (mx + 12, wy + 9)], CYAN, 3); p.line([(mx - 6, wy + 17), (mx + 6, wy + 17)], CYAN, 3)
        for bx, bw, bh in (buildings if buildings is not None else _skyline(w, int(gy - y0 - 16), seed)):
            building(p, x0 + bx, sy, bw, bh)
        if sink > 1:
            p.dashed([(x0 + 4, gy), (x1 - 4, gy)], GRAY, 2, 12, 9)
        p.line([(x0, sy), (x1, sy)], WHITE, 5)
        if ruler:                                                  # 0 at the original level, a tick every unit
            px_unit, every = ruler
            rx = x1 - 30; top_r, bot_r = gy - px_unit * every * .5, gy + px_unit * every * 2
            p.line([(rx, top_r), (rx, bot_r)], GRAY, 2)
            k = math.ceil((top_r - gy) / px_unit)
            while gy + k * px_unit <= bot_r:
                p.line([(rx, gy + k * px_unit), (rx - (18 if k % every == 0 else 9 if k % 5 == 0 else 5), gy + k * px_unit)], GRAY, 2)
                k += 1
            if sink > 1:
                p.poly([(rx + 2, sy), (rx + 22, sy - 11), (rx + 22, sy + 11)], fill=ACCENT)
    if reveal < 1:                                                 # scan from the top: only what the line has passed
        cut = int(y0 + h * max(0.0, reveal))
        clear = Image.new("RGBA", (w, max(0, y1 - cut) + 2), (0, 0, 0, 0))
        full.paste(clear, (x0, cut))
    img.paste(full, (0, 0), full)
    out = dict(box=(x0, y0, x1, y1), ground=gy, surface=sy, water=(gy + water if water is not None else None),
               layers=bounds)
    with Plate(img, (x0 - 20, y0 - 20, x1 + 20, y1 + 20)) as p:
        if frame:
            p.rect(x0, y0, x1, y1, color=frame, w=2)
            for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
                p.line([(cx - 16, cy), (cx + 16, cy)], frame, 2); p.line([(cx, cy - 16), (cx, cy + 16)], frame, 2)
        if reveal < 1:
            cut = y0 + h * max(0.0, reveal)
            p.line([(x0, cut), (x1, cut)], CYAN, 3)
    vis = y0 + h * min(1.0, reveal)
    if ruler:
        px_unit, every = ruler
        for k in range(3):
            ly = gy + k * px_unit * every
            if ly < vis - 10: text(img, str(k * every), x1 - 56, ly, 26, GRAY, anchor="rm")
    if labels:
        for (kind, lh, label, color), (a, b) in zip(specs, bounds):
            if label and b - a > 40 and (a + b) / 2 < vis - 10:
                text(img, label.upper(), x0 + 24, a + 26, 24, mix(_base(kind, color), WHITE, .7), tracking=.3, anchor="lm")
    return out
