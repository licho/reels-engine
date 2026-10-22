"""Documents, screens and icons: checklists, resume, chat, monitors, charts, people."""
import math
from .core import F, fit_font, BLK, WHITE, RED, YEL, dk, lc, cl, pop, check

def checklist(d, x, y, w, title, items, done=None, size=36, appear=1.0):
    """Card with a list. (x, y) = top-left corner. done = how many are already checked (None = all)."""
    n = len(items); h = 110 + n * (size + 26)
    d.rounded_rectangle([x, y, x + w, y + h], 24, fill=WHITE, outline=BLK, width=6)
    d.text((x + w / 2, y + 55), title, font=F(size + 8), fill=BLK, anchor="mm")
    for i, it in enumerate(items):
        if i >= n * cl(appear) + .001: break
        yy = y + 115 + i * (size + 26)
        ok = done is None or i < done
        d.rounded_rectangle([x + 30, yy - 18, x + 66, yy + 18], 8, fill=(40, 170, 80) if ok else WHITE, outline=BLK, width=3)
        if ok: d.line([(x + 38, yy), (x + 46, yy + 9), (x + 60, yy - 10)], fill=WHITE, width=5)
        d.text((x + 86, yy), it, font=F(size), fill=BLK, anchor="lm")
    return h

def document(d, x, y, w, h, title="CURRÍCULUM", lines=(), size=30, stamp=None):
    """Document sheet (resume, contract). stamp=('REJECTED', color) draws a stamp on top (use core.stamp to rotate it)."""
    d.rectangle([x, y, x + w, y + h], fill=WHITE, outline=BLK, width=6)
    d.text((x + w / 2, y + 55), title, font=F(size + 12), fill=BLK, anchor="mm")
    yy = y + 110
    for ln in lines:
        d.text((x + 30, yy), ln, font=F(size), fill=(60, 60, 60), anchor="lm"); yy += size + 20
    while yy < y + h - 40:
        d.line([(x + 30, yy), (x + w - 30, yy)], fill=(210, 210, 210), width=6); yy += 44
    if stamp:
        txt, col = stamp
        d.rounded_rectangle([x + w * .15, y + h * .55, x + w * .85, y + h * .55 + size * 2.4], 10, outline=col, width=8)
        d.text((x + w / 2, y + h * .55 + size * 1.2), txt, font=fit_font(d, txt, w * .62, int(size * 1.4)), fill=col, anchor="mm")

def phone_chat(d, x, y, w, h, title, msgs, shown=None, size=32):
    """Phone with a chat. msgs = [(side 'l'|'r', text, time)]. shown = how many messages are visible."""
    d.rounded_rectangle([x, y, x + w, y + h], 40, fill=(30, 30, 35), outline=BLK, width=6)
    d.rounded_rectangle([x + 16, y + 16, x + w - 16, y + h - 16], 28, fill=(240, 242, 245))
    d.rectangle([x + 16, y + 40, x + w - 16, y + 110], fill=(90, 80, 160)); d.text((x + 40, y + 75), title, font=F(size), fill=WHITE, anchor="lm")
    yy = y + 140
    for i, (side, txt, clock) in enumerate(msgs[: (len(msgs) if shown is None else shown)]):
        tw = d.textlength(txt, font=F(size)) + 40
        bx = x + 36 if side == "l" else x + w - 36 - tw
        d.rounded_rectangle([bx, yy, bx + tw, yy + size + 30], 18, fill=WHITE if side == "l" else (200, 230, 255), outline=(180, 180, 190), width=2)
        d.text((bx + 20, yy + (size + 30) / 2), txt, font=F(size), fill=BLK, anchor="lm")
        if clock: d.text((bx + tw - 6, yy + size + 40), clock, font=F(size * .6), fill=(120, 120, 130), anchor="rm")
        yy += size + 70

def monitor(d, x0, y0, x1, y1, content="chart", t=0.0, trend=1.0, col=(80, 220, 120), stand=True):
    """Monitor/screen. content: chart (trend>0 goes up) | wave | blank | text:<text>."""
    d.rounded_rectangle([x0, y0, x1, y1], 18, fill=(20, 25, 30), outline=BLK, width=6)
    i0, j0, i1, j1 = x0 + 20, y0 + 20, x1 - 20, y1 - 20
    if content == "chart":
        pts = []
        for k in range(25):
            u = k / 24; v = .5 - trend * (u - .5) * .8 + .08 * math.sin(k * 1.7 + t)
            pts.append((i0 + u * (i1 - i0), j0 + cl(v) * (j1 - j0)))
        d.line(pts, fill=col, width=7)
    elif content == "wave":
        mid = (j0 + j1) / 2
        d.line([(i0 + k * (i1 - i0) / 80, mid + math.sin(k * .9 + t * 8) * (j1 - j0) * .35 * abs(math.sin(k * .21 + t))) for k in range(81)], fill=col, width=5)
    elif content.startswith("text:"):
        d.text(((i0 + i1) / 2, (j0 + j1) / 2), content[5:], font=fit_font(d, content[5:], i1 - i0 - 20, 60), fill=col, anchor="mm")
    if stand:
        cx = (x0 + x1) / 2
        d.rectangle([cx - 15, y1, cx + 15, y1 + 50], fill=(60, 60, 65)); d.rectangle([cx - 80, y1 + 45, cx + 80, y1 + 60], fill=(60, 60, 65), outline=BLK, width=3)

def people_grid(d, x, y, n=10, cols=5, highlight=(), gap=95, size=1.0, col=(150, 155, 165), hcol=RED):
    """People icons ('1 in 10'). (x, y) = center of the grid."""
    rows = math.ceil(n / cols)
    for i in range(n):
        cx = x + (i % cols - (cols - 1) / 2) * gap * size; cy = y + (i // cols - (rows - 1) / 2) * gap * 1.4 * size
        c = hcol if i in highlight else col
        d.ellipse([cx - 22 * size, cy - 60 * size, cx + 22 * size, cy - 16 * size], fill=c)
        d.rounded_rectangle([cx - 34 * size, cy - 10 * size, cx + 34 * size, cy + 60 * size], int(18 * size), fill=c)

def thought(d, x, y, w, h, tail_to=None, fill=WHITE):
    """Thought cloud (x, y = center) with little bubbles toward tail_to. Returns the inner box."""
    for k in range(10):
        a = k / 10 * 2 * math.pi
        cx, cy = x + math.cos(a) * w * .42, y + math.sin(a) * h * .38
        d.ellipse([cx - w * .17, cy - h * .2, cx + w * .17, cy + h * .2], fill=fill, outline=BLK, width=4)
    d.ellipse([x - w * .45, y - h * .4, x + w * .45, y + h * .4], fill=fill)
    if tail_to:
        tx, ty = tail_to
        for k, r in enumerate((22, 15, 9)):
            u = .55 + k * .17; px, py = x + (tx - x) * u, y + h * .4 + (ty - y - h * .4) * u
            d.ellipse([px - r, py - r, px + r, py + r], fill=fill, outline=BLK, width=3)
    return (x - w * .35, y - h * .3, x + w * .35, y + h * .3)

def sign_board(d, x, y, text, size=48, bg=(110, 70, 40), fg=WHITE, post=True, post_h=260):
    """Wooden sign with a post; (x, y) = base of the post (floor)."""
    tw = d.textlength(text, font=F(size)) + 60; top = y - post_h - size * 2
    if post: d.rectangle([x - 14, top + size, x + 14, y], fill=dk(bg, .85), outline=BLK, width=4)
    d.rounded_rectangle([x - tw / 2, top, x + tw / 2, top + size * 1.8], 12, fill=bg, outline=BLK, width=5)
    d.text((x, top + size * .9), text, font=F(size), fill=fg, anchor="mm")

def heart(d, x, y, r=40, col=RED):
    d.ellipse([x - r, y - r * .6, x, y + r * .3], fill=col); d.ellipse([x, y - r * .6, x + r, y + r * .3], fill=col)
    d.polygon([(x - r * .97, y), (x + r * .97, y), (x, y + r)], fill=col)

def arrow(d, x0, y0, x1, y1, col=RED, w=14):
    d.line([(x0, y0), (x1, y1)], fill=col, width=w)
    a = math.atan2(y1 - y0, x1 - x0); L = w * 2.6
    d.polygon([(x1 + math.cos(a) * L * .5, y1 + math.sin(a) * L * .5), (x1 + math.cos(a + 2.5) * L, y1 + math.sin(a + 2.5) * L), (x1 + math.cos(a - 2.5) * L, y1 + math.sin(a - 2.5) * L)], fill=col)

def ruler(d, x, y0, y1, marks, current=None, appear=1.0, w=60, col=(250, 210, 60)):
    """Vertical size ruler. marks=[(fraction 0=bottom..1=top, text)]; current = highlighted index."""
    d.rounded_rectangle([x, y0, x + w, y1], 14, fill=col, outline=BLK, width=5)
    for k in range(1, 20):
        yy = y1 - (y1 - y0) * k / 20
        d.line([(x + w - (26 if k % 5 == 0 else 14), yy), (x + w, yy)], fill=BLK, width=3)
    for i, (f, txt) in enumerate(marks):
        if i >= len(marks) * appear + .001: break
        yy = y1 - (y1 - y0) * f; on = i == current
        d.line([(x + w, yy), (x + w + 30, yy)], fill=RED if on else BLK, width=6 if on else 3)
        d.text((x + w + 40, yy), txt, font=F(46 if on else 32), fill=RED if on else (60, 60, 60), anchor="lm", stroke_width=4, stroke_fill=WHITE)
        if on: d.polygon([(x - 10, yy), (x - 40, yy - 20), (x - 40, yy + 20)], fill=RED, outline=BLK)

def wanted(d, x, y, w, h, title="SE BUSCA", subtitle="", paper=(240, 225, 185)):
    """WANTED poster. Returns the box to draw the 'suspect' in. (x, y) = top-left corner."""
    d.rectangle([x, y, x + w, y + h], fill=paper, outline=(120, 90, 50), width=8)
    d.text((x + w / 2, y + 70), title, font=fit_font(d, title, w - 60, 80), fill=(110, 50, 30), anchor="mm")
    box = (x + 40, y + 130, x + w - 40, y + h - (110 if subtitle else 40))
    d.rectangle(box, fill=(250, 240, 215), outline=(120, 90, 50), width=4)
    if subtitle: d.text((x + w / 2, y + h - 60), subtitle, font=fit_font(d, subtitle, w - 60, 46), fill=(110, 50, 30), anchor="mm")
    return box

def blob_map(d, cx, cy, r, seed=3, fill=(170, 175, 185), outline=BLK, label=None, size=40, bumps=7):
    """Irregular map-like outline (city, region). Area ≈ π·r²."""
    import random; rnd = random.Random(seed); n = 48
    amps = [(rnd.uniform(.05, .14), rnd.uniform(0, 6.28), k) for k in range(2, 2 + bumps // 2)]
    pts = []
    for i in range(n):
        a = i / n * 2 * math.pi; rr = r * (1 + sum(A * math.sin(k * a + ph) for A, ph, k in amps))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    d.polygon(pts, fill=fill, outline=outline, width=5)
    if label: d.text((cx, cy), label, font=F(size), fill=BLK, anchor="mm", stroke_width=4, stroke_fill=WHITE)

def cracks(d, box, seed=1, n=6, col=WHITE, width=4):
    """Glass cracks inside box (broken windows)."""
    import random; rnd = random.Random(seed); x0, y0, x1, y1 = box
    for _ in range(n):
        cx, cy = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        for k in range(5):
            a = rnd.uniform(0, 6.28); L = rnd.uniform(.3, .7) * min(x1 - x0, y1 - y0)
            d.line([(cx, cy), (max(x0, min(x1, cx + math.cos(a) * L)), max(y0, min(y1, cy + math.sin(a) * L)))], fill=col, width=width)

def bar_chart(d, x0, y0, x1, items, vmax=None, frac=1.0, size=40, gap=30, bar_h=70, fmt=None):
    """Horizontal bars: items=[(label, value, color)]. frac (0..1) animates the growth. Returns the final y.
    The value is written at the end of each bar (fmt(value) or with thousands separators)."""
    vmax = vmax or max(v for _, v, _ in items); y = y0; lw = 0
    f = F(size)
    for lab, _, _ in items: lw = max(lw, d.textlength(lab, font=f))
    bx = x0 + lw + 20
    for i, (lab, v, col) in enumerate(items):
        k = max(0.0, min(1.0, frac * len(items) - i))
        d.text((x0 + lw, y + bar_h / 2), lab, font=f, fill=WHITE, anchor="rm", stroke_width=max(3, size // 9), stroke_fill=BLK)
        wpx = max(6, (x1 - bx - 10) * v / vmax * k)
        d.rounded_rectangle([bx, y, bx + wpx, y + bar_h], 12, fill=col, outline=BLK, width=4)
        if k > .95:
            txt = fmt(v) if fmt else f"{v:,.0f}"
            tw_ = d.textlength(txt, font=F(int(size * .9)))
            tx = bx + wpx + 12 if bx + wpx + 12 + tw_ < x1 + 60 else bx + wpx - 12 - tw_
            d.text((tx, y + bar_h / 2), txt, font=F(int(size * .9)), fill=WHITE, anchor="lm", stroke_width=max(3, size // 9), stroke_fill=BLK)
        y += bar_h + gap
    return y
