"""Engine base: canvas, font, colors, interpolation and text (label, big text, caption).
It used to live in src/reel.py of the Datos que Asustan channel."""
import math
from PIL import ImageFont
from .config import current

_cfg = current()
W, H = _cfg.size
FB = _cfg.font_bold
_fc = {}
def F(s):
    s = max(8, int(s))
    if s not in _fc: _fc[s] = ImageFont.truetype(FB, s)
    return _fc[s]

def cl(v, a=0.0, b=1.0): return max(a, min(b, v))
def lerp(a, b, t): return a + (b - a) * t
def ease(t): t = cl(t); return t * t * (3 - 2 * t)
def pop(t):
    t = cl(t); c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
def lc(c1, c2, t): return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))
def dk(c, f): return tuple(int(v * f) for v in c)

_P = _cfg.palette
YEL, RED, WHITE, BLK, SKIN = _P["YEL"], _P["RED"], _P["WHITE"], _P["BLK"], _P["SKIN"]
GREEN, BLUE, GRAY, ORANGE, PURPLE = _P["GREEN"], _P["BLUE"], _P["GRAY"], _P["ORANGE"], _P["PURPLE"]
CAP_Y = _cfg.cap_y
_CF, _CH, _CS = _cfg.caption_fill, _cfg.caption_highlight, _cfg.caption_stroke

# ---------------- text helpers ----------------
def rich_caption(d, text, y=CAP_Y, size=_cfg.caption_size, maxw=960, appear=1.0):
    size = int(size * (0.8 + 0.2 * pop(appear)))
    f = F(size)
    hl = False; words = []
    for w in text.split():
        pieces = []
        for j, part in enumerate(w.split("*")):
            if j > 0: hl = not hl
            if part: pieces.append((part, hl))
        words.append(pieces)
    sp = d.textlength(" ", font=f)
    lines, cur, cw = [], [], 0
    for pcs in words:
        ww = sum(d.textlength(p, font=f) for p, _ in pcs)
        if cur and cw + sp + ww > maxw:
            lines.append((cur, cw)); cur, cw = [], 0
        cw = cw + (sp if cur else 0) + ww; cur.append((pcs, ww))
    if cur: lines.append((cur, cw))
    lh = size * 1.22
    y0 = y - lh * (len(lines) - 1) / 2
    for li, (ln, lw) in enumerate(lines):
        x = W / 2 - lw / 2
        for pcs, ww in ln:
            for p, h in pcs:
                d.text((x, y0 + li * lh), p, font=f, fill=_CH if h else _CF, anchor="lm",
                       stroke_width=max(4, int(size * 0.14)), stroke_fill=_CS)
                x += d.textlength(p, font=f)
            x += sp

def chip(d, text, y=_cfg.chip1, bg=_cfg.chip_bg, fg=_cfg.chip_fg, size=56, appear=1.0):
    size = int(size * (0.6 + 0.4 * pop(appear)))
    f = F(size); w = d.textlength(text, font=f); pad = size * 0.65
    d.rounded_rectangle([W/2 - w/2 - pad, y - size*0.8, W/2 + w/2 + pad, y + size*0.8],
                        radius=int(size*0.6), fill=bg, outline=BLK, width=6)
    d.text((W/2, y), text, font=f, fill=fg, anchor="mm")

def bigtext(d, s, x, y, size, fill=YEL, stroke=BLK, sw=None):
    d.text((x, y), s, font=F(size), fill=fill, anchor="mm",
           stroke_width=sw if sw is not None else max(4, int(size*0.12)), stroke_fill=stroke)


def xmark(d, cx, cy, s):
    for col, wd in ((BLK, 54), (RED, 36)):
        d.line([(cx-170*s, cy-170*s), (cx+170*s, cy+170*s)], fill=col, width=int(wd*s))
        d.line([(cx-170*s, cy+170*s), (cx+170*s, cy-170*s)], fill=col, width=int(wd*s))

def check(d, cx, cy, s):
    d.ellipse([cx-42*s, cy-42*s, cx+42*s, cy+42*s], fill=(40, 180, 80), outline=BLK, width=5)
    d.line([(cx-20*s, cy), (cx-5*s, cy+18*s), (cx+22*s, cy-16*s)], fill=WHITE, width=int(11*s), joint="curve")

