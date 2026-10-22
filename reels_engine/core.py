"""Shared core: drawing, text, safe zones, speech bubbles and utilities."""
import os, sys, math, random
from functools import lru_cache
from PIL import Image, ImageDraw
from .config import current as _current
from .base import F, cl, lerp, ease, pop, lc, dk, rich_caption, chip, bigtext, check, xmark, W, H, YEL, RED, WHITE, BLK, SKIN, GREEN, BLUE, GRAY, ORANGE, PURPLE

_cfg = _current()
# ---------------- safe zones (from the channel's configuration) ----------------
CHIP1, CHIP2 = _cfg.chip1, _cfg.chip2           # labels at the top
ACTION_TOP, ACTION_BOT = _cfg.action_top, _cfg.action_bot   # action zone
FLOOR = _cfg.floor                              # default floor (characters' feet)
CAP_Y = _cfg.cap_y                              # captions (keep anything important out of _cfg.cap_free)
_BZ = _cfg.bubble_zone

@lru_cache(maxsize=64)
def _grad(top, bot):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    for y in range(H): d.line([(0, y), (W, y)], fill=lc(top, bot, y / H))
    return img

def grad(top, bot):
    """Gradient background (cached). Returns a copy ready to draw on."""
    return _grad(tuple(top), tuple(bot)).copy()

def canvas(bg):
    """bg can be an Image (copied) or a tuple of 2 colors (gradient)."""
    img = bg.copy() if isinstance(bg, Image.Image) else grad(*bg)
    return img, ImageDraw.Draw(img)

def _bubble_layout(d, text, size, maxw):
    f = F(size); words = text.split(); lines = []; cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if d.textlength(test, font=f) > maxw and cur: lines.append(cur); cur = w
        else: cur = test
    lines.append(cur)
    lw = max(d.textlength(l, font=f) for l in lines); lh = size * 1.18
    return f, lines, lh, lw + size * 1.5, lh * len(lines) + size * 1.0

def _qbez(p0, p1, p2, n=10):
    return [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0], (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]) for u in [k / n for k in range(n + 1)]]

def bubble(d, x, y, text, size=52, tail=None, maxw=760, fill=WHITE, fg=BLK, max_tail=None, shadow=True):
    """Speech bubble centered at (x,y): very round corners, thick outline, soft shadow and a curved comic-style tail.
    tail=(x,y) = where it points. The tail never stretches too far (max. max_tail). To place it automatically, use say()."""
    f, lines, lh, bw, bh = _bubble_layout(d, text, size, maxw)
    x0, y0, x1, y1 = x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2
    r = int(min(bh / 2, size * .9)); ow = max(5, int(size * .12))
    tail_poly = None
    if tail:
        tx, ty = tail
        if ty > y1 or ty < y0:
            ex = min(max(tx, x0 + r * .8 + size * .3), x1 - r * .8 - size * .3); ey = y1 - ow if ty > y1 else y0 + ow
        else:
            ey = min(max(ty, y0 + bh * .3), y1 - bh * .3); ex = x1 - ow if tx > x1 else x0 + ow
        dx, dy = tx - ex, ty - ey; L = math.hypot(dx, dy) or 1
        Lc = min(L, max_tail or size * 2.0); tip = (ex + dx / L * Lc, ey + dy / L * Lc)
        hw = size * .42; vertical = ty > y1 or ty < y0
        b1, b2 = ((ex - hw, ey), (ex + hw, ey)) if vertical else ((ex, ey - hw), (ex, ey + hw))
        nx, ny = -dy / L, dx / L; bend = Lc * .2                    # bends to one side (like a hand-drawn stroke)
        c1 = ((b1[0] + tip[0]) / 2 + nx * bend, (b1[1] + tip[1]) / 2 + ny * bend)
        c2 = ((b2[0] + tip[0]) / 2 + nx * bend * .6, (b2[1] + tip[1]) / 2 + ny * bend * .6)
        tail_poly = _qbez(b1, c1, tip) + _qbez(tip, c2, b2)[1:]
    img = getattr(d, "_image", None)
    if shadow and img is not None and img.mode == "RGB":           # sombra suave desplazada
        from PIL import Image as _I, ImageDraw as _D
        sh = _I.new("RGBA", img.size, (0, 0, 0, 0)); sd = _D.Draw(sh); off = size * .16
        sd.rounded_rectangle([x0 + off, y0 + off, x1 + off, y1 + off], r, fill=(0, 0, 0, 70))
        if tail_poly: sd.polygon([(px + off, py + off) for px, py in tail_poly], fill=(0, 0, 0, 70))
        img.paste(sh, (0, 0), sh); d = _D.Draw(img)
    if tail_poly:
        d.polygon(tail_poly, fill=fill); d.line(tail_poly, fill=BLK, width=ow, joint="curve")
    d.rounded_rectangle([x0, y0, x1, y1], r, fill=fill, outline=BLK, width=ow)
    if tail_poly:                                                   # hides the seam: tail and bubble are one piece
        cx_, cy_ = (tail_poly[0][0] + tail_poly[-1][0]) / 2, (tail_poly[0][1] + tail_poly[-1][1]) / 2
        k = .72; d.polygon([(cx_ + (px - cx_) * k, cy_ + (py - cy_) * k) for px, py in tail_poly], fill=fill)
    for i, l in enumerate(lines):
        d.text((x, y0 + size * .5 + lh * i + lh / 2), l, font=f, fill=fg, anchor="mm")
    return (x0, y0, x1, y1)

def say(d, text, mouth, head=110, size=52, maxw=520, fill=WHITE, fg=BLK, side=None, avoid=()):
    """Bubble that places ITSELF next to the speaker.
    mouth = (x, y) of the mouth; head = head radius (px); avoid = boxes (x0,y0,x1,y1) not to cover (other characters, labels).
    Tries several spots (above center, above each side, at the sides, higher up) and picks the one that
    doesn't cover the head or 'avoid', stays on screen (between labels and captions) and has the shortest tail."""
    reserve = [(a[0] + (a[2] - a[0]) * .2, a[1] - 200, a[2] - (a[2] - a[0]) * .2, a[1]) for a in avoid]  # room above the others (for THEIR bubble)
    mx, my = mouth
    if side: toward = side
    elif avoid:                                                  # moves away from the other characters
        ac = sum((a[0] + a[2]) / 2 for a in avoid) / len(avoid); toward = 1 if ac < mx else -1
    else: toward = 1 if mx < W / 2 else -1
    head_box = (mx - head * 1.15, my - head * 1.9, mx + head * 1.15, my + head * .5)
    def over(a, b): return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))
    best = None
    for wi, mw in enumerate((maxw, int(maxw * .72))):             # if it doesn't fit nearby, try a narrower bubble (more lines)
        _, _, _, bw, bh = _bubble_layout(d, text, size, mw)
        top_lim, bot_lim = _BZ[0] + bh / 2, _BZ[1] - bh / 2
        cands = []
        for lift in (0, 80, 170, 260):
            above = my - head * 1.9 - bh / 2 - 20 - lift
            for sx, bias in ((0, 0), (toward, 10), (-toward, 25)):
                cands.append((mx + sx * (head * .6 + bw * .32), above, bias + lift * .25))
        for sd, bias in ((toward, 40), (-toward, 70)):
            cands.append((mx + sd * (head * 1.15 + 40 + bw / 2), my - head * .9, bias))
        if side: cands = [c for c in cands if (c[0] - mx) * side > 0] or cands
        for bx, by, bias in cands:
            cx = min(max(bx, bw / 2 + 30), W - bw / 2 - 30); cy = min(max(by, top_lim), bot_lim)
            box = (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)
            tipx = mx + (1 if cx > mx else -1) * head * .8
            ex = min(max(tipx, box[0] + 40), box[2] - 40); ey = box[3] if cy < my else box[1]
            tail_len = math.hypot(tipx - ex, my - ey)
            score = (bias + wi * 35 + tail_len * 1.4 + abs(cx - bx) * .5 + abs(cy - by) * .8
                     + (over(box, head_box) * 8000 + sum(over(box, a) for a in avoid) * 2000
                        + sum(over(box, a) for a in reserve) * 500 + sum(over(box, a) for a in _SAID) * 20000) / (bw * bh))
            if best is None or score < best[0]: best = (score, cx, cy, mw)
    _, cx, cy, mw = best
    tip = (mx + (1 if cx > mx else -1) * head * .8, my - head * .2)
    box = bubble(d, cx, cy, text, size, tail=tip, maxw=mw, fill=fill, fg=fg, max_tail=size * 1.9)
    _SAID.append(box)
    return box

_SAID = []                                                       # bubbles already drawn in the current frame
def say_reset():
    """Call at the start of each frame (produce does it) so bubbles avoid each other."""
    _SAID.clear()

def calendar(d, cx, cy, day, label="DÍA", col=(240, 150, 40), sc=0.7):
    S = lambda v: v * sc
    d.rounded_rectangle([cx - S(190), cy - S(170), cx + S(190), cy + S(170)], int(S(26)), fill=WHITE, outline=BLK, width=6)
    d.rounded_rectangle([cx - S(190), cy - S(170), cx + S(190), cy - S(70)], int(S(26)), fill=col, outline=BLK, width=6)
    d.text((cx, cy - S(120)), label, font=fit_font(d, label, S(340), int(S(52))), fill=WHITE, anchor="mm")
    d.text((cx, cy + S(50)), str(day), font=fit_font(d, str(day), S(330), int(S(150))), fill=BLK, anchor="mm")   # fits the width

def gauge(d, cx, cy, r, val, vmax, label, fg=WHITE):
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=(30, 30, 40), outline=WHITE, width=6)
    for k in range(11):
        a = math.pi + k / 10 * math.pi
        d.line([(cx + math.cos(a) * r * .85, cy + math.sin(a) * r * .85), (cx + math.cos(a) * r * .97, cy + math.sin(a) * r * .97)], fill=WHITE, width=5)
    a = math.pi + cl(val / vmax) * math.pi
    d.line([(cx, cy), (cx + math.cos(a) * r * .8, cy + math.sin(a) * r * .8)], fill=RED, width=12)
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=RED)
    d.text((cx, cy + 50), label, font=F(56), fill=fg, anchor="mm", stroke_width=5, stroke_fill=BLK)

def confetti(d, t, n=60, seed=7):
    rng = random.Random(seed)
    for i in range(n):
        x = rng.uniform(0, W); sp = rng.uniform(200, 400); y = (rng.uniform(-H, 0) + t * sp) % H
        c = rng.choice([(255, 214, 0), (225, 35, 45), (60, 160, 230), (60, 180, 90), (240, 120, 200)])
        d.rectangle([x, y, x + 14, y + 24], fill=c)

def speedlines(d, t, n=26, col=WHITE, y0=250, y1=1350, seed=2):
    rng = random.Random(seed)
    for i in range(n):
        y = rng.uniform(y0, y1); ln = rng.uniform(80, 260); sp = rng.uniform(1600, 2600)
        x = (rng.uniform(0, W) + t * sp) % (W + 400) - 300
        d.line([(x, y), (x + ln, y)], fill=col, width=5)

def sparkles(d, t, n=24, box=(80, 300, 1000, 1250), col=YEL, seed=3):
    rng = random.Random(seed)
    for i in range(n):
        x, y = rng.uniform(box[0], box[2]), rng.uniform(box[1], box[3])
        if (int(t * 4) + i) % 3 == 0:
            d.polygon([(x, y - 18), (x + 6, y), (x, y + 18), (x - 6, y)], fill=col)
            d.polygon([(x - 18, y), (x, y - 6), (x + 18, y), (x, y + 6)], fill=col)

def follow_btn(d, lt, y=1250, delay=1.5, text=_cfg.follow_text):
    """Follow button (Channel.follow_text) that pops in with a bounce."""
    if lt <= delay: return
    sc = pop((lt - delay) / 0.35)
    d.rounded_rectangle([540 - 330 * sc, y - 80 * sc, 540 + 330 * sc, y + 80 * sc], int(26 * sc), fill=RED, outline=WHITE, width=6)
    d.text((540, y), text, font=F(max(8, 80 * sc)), fill=WHITE, anchor="mm")

def stamp(img, draw_fn, x, y, size=900, angle=0.0, flip=False, **kw):
    """Draws any character on a separate layer and pastes it rotated/flipped.
    draw_fn(d, cx, cy, **kw) is called with the layer center (size/2, size/2)."""
    tmp = Image.new("RGBA", (size, size), (0, 0, 0, 0)); td = ImageDraw.Draw(tmp)
    draw_fn(td, size / 2, size / 2, **kw)
    if flip: tmp = tmp.transpose(Image.FLIP_LEFT_RIGHT)
    if angle: tmp = tmp.rotate(angle, resample=Image.BICUBIC)
    img.paste(tmp, (int(x - size / 2), int(y - size / 2)), tmp)
    return ImageDraw.Draw(img)

def shake_arr(arr, t, amp):
    import numpy as np
    return np.roll(arr, int(math.sin(t * 60) * amp), axis=1) if amp else arr


def fit_font(d, text, maxw, size):
    """Largest font (<= size) so that 'text' fits in maxw px."""
    while size > 10 and d.textlength(text, font=F(size)) > maxw: size -= 2
    return F(size)
