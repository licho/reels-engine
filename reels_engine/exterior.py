"""Outdoors: houses, trees, lamp posts, sun, moon, clouds, fence, road. (x, y) = bottom center (floor) unless noted."""
import math, random
from .core import F, BLK, WHITE, RED, YEL, dk, lc

def house(d, x, y, s=1.0, wall=(240, 220, 180), roof=(190, 70, 50), lights=False, door_col=(140, 90, 50)):
    """One-story house with a gabled roof."""
    S = lambda v: v * s
    d.rectangle([x - S(230), y - S(330), x + S(230), y], fill=wall, outline=BLK, width=6)
    d.polygon([(x - S(270), y - S(320)), (x, y - S(540)), (x + S(270), y - S(320))], fill=roof, outline=BLK)
    d.rectangle([x + S(110), y - S(520), x + S(170), y - S(410)], fill=dk(roof, .8), outline=BLK, width=4)
    d.rectangle([x - S(50), y - S(200), x + S(50), y], fill=door_col, outline=BLK, width=5)
    d.ellipse([x + S(22), y - S(110), x + S(38), y - S(94)], fill=(230, 190, 60))
    win = (255, 230, 120) if lights else (160, 210, 240)
    for wx in (-150, 150):
        d.rectangle([x + S(wx) - S(55), y - S(250), x + S(wx) + S(55), y - S(150)], fill=win, outline=BLK, width=5)
        d.line([(x + S(wx), y - S(250)), (x + S(wx), y - S(150))], fill=BLK, width=4); d.line([(x + S(wx) - S(55), y - S(200)), (x + S(wx) + S(55), y - S(200))], fill=BLK, width=4)

def building(d, x, y, w=220, h=600, col=(180, 150, 120), lit=0.0, seed=1, face=None):
    """Building (x = center). lit = fraction of windows lit (night)."""
    rnd = random.Random(seed)
    d.rectangle([x - w / 2, y - h, x + w / 2, y], fill=col, outline=BLK, width=5)
    # windows scaled to the building size: they never leave the facade
    pad = max(8, min(w, h) * .08)
    cols = max(1, int((w - pad) // 60)); rows = max(1, int((h - pad) // 80))
    cw, rh = (w - 2 * pad) / cols, (h - 2 * pad) / rows
    ww, wh = min(32, cw * .55), min(42, rh * .6)
    for r in range(rows):
        for c in range(cols):
            wx = x - w / 2 + pad + (c + .5) * cw; wy = y - h + pad + (r + .5) * rh
            on = rnd.random() < lit
            d.rectangle([wx - ww / 2, wy - wh / 2, wx + ww / 2, wy + wh / 2], fill=(255, 220, 110) if on else (150, 200, 230) if lit == 0 else (50, 60, 80), outline=BLK, width=2)

def tree(d, x, y, s=1.0, kind="round", t=0.0, col=(70, 160, 80)):
    """Tree. kind: round | pine | palm."""
    S = lambda v: v * s; sw = math.sin(t * 1.5) * S(6)
    if kind == "palm":
        pts = [(x, y), (x + S(20), y - S(250)), (x + S(50) + sw, y - S(480))]
        d.line(pts, fill=BLK, width=int(S(42)), joint="curve"); d.line(pts, fill=(160, 110, 60), width=int(S(34)), joint="curve")
        tx, ty = x + S(50) + sw, y - S(480)
        for a in (-2.6, -2.0, -1.2, -.5, .1):
            ex, ey = tx + math.cos(a) * S(200), ty + math.sin(a) * S(120) + S(60)
            d.polygon([(tx, ty), ((tx + ex) / 2, (ty + ey) / 2 - S(40)), (ex, ey), ((tx + ex) / 2, (ty + ey) / 2 + S(10))], fill=col, outline=BLK)
        return
    d.rectangle([x - S(22), y - S(220), x + S(22), y], fill=(130, 85, 50), outline=BLK, width=4)
    if kind == "pine":
        for k in range(3):
            w = S(170 - k * 40); top = y - S(180 + k * 120)
            d.polygon([(x - w + sw, top), (x + sw * .5, top - S(210)), (x + w + sw, top)], fill=lc(col, (40, 100, 60), .5), outline=BLK)
    else:
        for (dx, dy, r) in ((-70, -300, 110), (70, -300, 110), (0, -400, 130)):
            d.ellipse([x + S(dx) - S(r) + sw, y + S(dy) - S(r), x + S(dx) + S(r) + sw, y + S(dy) + S(r)], fill=col, outline=BLK, width=4)

def bush(d, x, y, s=1.0, col=(80, 160, 80)):
    S = lambda v: v * s
    for dx, r in ((-60, 60), (60, 60), (0, 80)):
        d.ellipse([x + S(dx) - S(r), y - S(r) * 1.6, x + S(dx) + S(r), y], fill=col, outline=BLK, width=4)

def cactus(d, x, y, s=1.0, col=(70, 150, 80)):
    """Saguaro-style cactus (cartoon)."""
    S = lambda v: v * s
    for (x0, y0, x1, y1) in ((-35, -420, 35, 0), (-130, -300, -80, -170), (80, -360, 130, -230)):
        d.rounded_rectangle([x + S(x0), y + S(y0), x + S(x1), y + S(y1)], int(S(25)), fill=col, outline=BLK, width=4)
    d.rectangle([x - S(105), y - S(195), x - S(30), y - S(150)], fill=col); d.rectangle([x + S(30), y - S(255), x + S(105), y - S(210)], fill=col)
    d.line([(x - S(105), y - S(150)), (x - S(35), y - S(150))], fill=BLK, width=4); d.line([(x + S(35), y - S(210)), (x + S(105), y - S(210))], fill=BLK, width=4)

def street_lamp(d, x, y, s=1.0, on=True):
    """Street lamp; y = floor."""
    S = lambda v: v * s
    if on: d.polygon([(x + S(80), y - S(640)), (x + S(140), y - S(640)), (x + S(300), y), (x - S(80), y)], fill=(255, 245, 190))
    d.rectangle([x - S(12), y - S(680), x + S(12), y], fill=(70, 70, 80), outline=BLK, width=3)
    d.line([(x, y - S(680)), (x + S(110), y - S(680))], fill=(70, 70, 80), width=int(S(16)))
    d.chord([x + S(60), y - S(700), x + S(160), y - S(620)], 0, 180, fill=(255, 230, 120) if on else (150, 150, 150), outline=BLK, width=3)

def sun(d, x, y, r=90, t=0.0, rays=True):
    if rays:
        for k in range(12):
            a = k / 12 * 2 * math.pi + t * .3
            d.line([(x + math.cos(a) * r * 1.2, y + math.sin(a) * r * 1.2), (x + math.cos(a) * r * 1.5, y + math.sin(a) * r * 1.5)], fill=(255, 210, 60), width=max(4, r // 10))
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 220, 70), outline=(240, 170, 40), width=max(3, r // 15))

def moon(d, x, y, r=80, bg=(20, 25, 55), crescent=False):
    if crescent:                                   # real crescent (without "covering" with the background color)
        from PIL import Image as _I, ImageDraw as _D
        n = int(2 * r) + 2; m = _I.new("1", (n, n), 0); md = _D.Draw(m)
        md.ellipse([0, 0, 2 * r, 2 * r], fill=1); md.ellipse([r * .55, -r * .05, r * 2.5, r * 1.9], fill=0)
        d.bitmap((int(x - r), int(y - r)), m, fill=(245, 240, 200)); return
    d.ellipse([x - r, y - r, x + r, y + r], fill=(245, 240, 200))
    for (dx, dy, rr) in ((-.3, -.2, .18), (.25, .2, .12), (.1, -.4, .1)): d.ellipse([x + dx * r - rr * r, y + dy * r - rr * r, x + dx * r + rr * r, y + dy * r + rr * r], fill=(225, 220, 180))
    if r >= 30:
        from .motion import sphere_shade
        sphere_shade(d._image, x, y, r, .25, .3)                      # sphere volume

def clouds(d, x, y, s=1.0, col=WHITE, t=0.0, rain=False):
    """Cloud (x, y = center). rain=True draws rain."""
    S = lambda v: v * s
    for dx, dy, r in ((-90, 10, 60), (0, -20, 85), (90, 10, 60)):
        d.ellipse([x + S(dx) - S(r), y + S(dy) - S(r), x + S(dx) + S(r), y + S(dy) + S(r)], fill=col)
    d.rectangle([x - S(90), y, x + S(90), y + S(70)], fill=col)
    if rain:
        for k in range(8):
            px = x - S(120) + k * S(34); ph = (t * 2 + k * .37) % 1
            d.line([(px, y + S(90) + ph * S(200)), (px - S(10), y + S(120) + ph * S(200))], fill=(90, 150, 230), width=4)

def fence(d, x0, x1, y, h=160, col=(240, 240, 235)):
    for x in range(int(x0), int(x1), 60):
        d.polygon([(x, y), (x, y - h), (x + 20, y - h - 25), (x + 40, y - h), (x + 40, y)], fill=col, outline=BLK)
    d.rectangle([x0, y - h * .75, x1, y - h * .62], fill=col, outline=BLK, width=3)

def road(d, y0, y1, t=0.0, speed=0.0, col=(70, 70, 75)):
    """Horizontal road with lane lines (speed>0 makes them move)."""
    d.rectangle([0, y0, 1080, y1], fill=col)
    off = (t * speed) % 200
    for x in range(-200, 1280, 200):
        d.rectangle([x - off, (y0 + y1) / 2 - 8, x - off + 110, (y0 + y1) / 2 + 8], fill=(240, 240, 240))

def booth(d, x, y, s=1.0, label="SEGURIDAD", col=(200, 205, 210)):
    """Booth (security, toll)."""
    S = lambda v: v * s
    d.rectangle([x - S(130), y - S(470), x + S(130), y], fill=col, outline=BLK, width=6)
    d.rectangle([x - S(150), y - S(500), x + S(150), y - S(460)], fill=dk(col, .8), outline=BLK, width=5)
    d.rectangle([x - S(95), y - S(420), x + S(95), y - S(280)], fill=(150, 200, 235), outline=BLK, width=5)
    d.text((x, y - S(200)), label, font=F(S(36)), fill=BLK, anchor="mm")

def bolt(d, x0, y0, x1, y1, seed=1, width=14, col=(255, 245, 140), glow=True, branches=2):
    """Zigzag lightning bolt from (x0,y0) to (x1,y1) with branches and glow."""
    rnd = random.Random(seed); n = 9; pts = [(x0, y0)]
    for k in range(1, n):
        u = k / n; pts.append((x0 + (x1 - x0) * u + rnd.uniform(-1, 1) * 60, y0 + (y1 - y0) * u))
    pts.append((x1, y1))
    if glow: d.line(pts, fill=(160, 170, 255), width=width * 3, joint="curve")
    d.line(pts, fill=col, width=width, joint="curve"); d.line(pts, fill=WHITE, width=max(2, width // 3))
    for b in range(branches):
        i = rnd.randint(2, n - 3); bx, by = pts[i]; ex, ey = bx + rnd.uniform(-160, 160), by + rnd.uniform(80, 200)
        d.line([(bx, by), ((bx + ex) / 2 + rnd.uniform(-30, 30), (by + ey) / 2), (ex, ey)], fill=col, width=max(3, width // 2))

def ground_current(d, x, y, t, r=300, col=(255, 230, 80)):
    """Electric current spreading over the ground from (x, y)."""
    for k in range(3):
        rr = (t * 300 + k * r / 3) % r
        d.arc([x - rr, y - rr * .18, x + rr, y + rr * .18], 0, 360, fill=col, width=5)
