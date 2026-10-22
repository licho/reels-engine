"""Furniture and indoor things (cartoon, black outline). (x, y) = bottom center (where it touches the floor) unless noted."""
import math
from .core import F, fit_font, BLK, WHITE, RED, YEL, dk, lc

WOOD = (140, 95, 55)

def chair(d, x, y, s=1.0, col=WOOD, facing=1, kind="chair"):
    """Chair seen from the side. facing=1 backrest on the left. kind: chair | office (old names: silla | oficina)."""
    S = lambda v: v * s; f = facing
    if kind in ("office", "oficina"):
        d.line([(x, y - S(20)), (x, y - S(170))], fill=(60, 60, 65), width=int(S(16)))
        for dx in (-70, 0, 70): d.line([(x, y - S(30)), (x + S(dx), y - S(5))], fill=(60, 60, 65), width=int(S(10))); d.ellipse([x + S(dx) - S(12), y - S(14), x + S(dx) + S(12), y + S(4)], fill=BLK)
        d.rounded_rectangle([x - S(110), y - S(200), x + S(110), y - S(160)], int(S(18)), fill=col, outline=BLK, width=5)
        bx = x - f * S(100)
        d.rounded_rectangle([min(bx, bx + f * S(50)), y - S(430), max(bx, bx + f * S(50)), y - S(170)], int(S(20)), fill=col, outline=BLK, width=5)
        return
    for dx in (-90, 90): d.rectangle([x + S(dx) - S(10), y - S(190), x + S(dx) + S(10), y], fill=dk(col, .85), outline=BLK, width=4)
    d.rectangle([x - S(115), y - S(215), x + S(115), y - S(185)], fill=col, outline=BLK, width=5)
    bx = x - f * S(105)
    d.rectangle([min(bx - S(10), bx + S(10)), y - S(450), max(bx - S(10), bx + S(10)), y - S(200)], fill=col, outline=BLK, width=4)
    d.rectangle([min(bx, bx + f * S(14)) - S(12), y - S(440), max(bx, bx + f * S(14)) + S(12), y - S(330)], fill=dk(col, .9), outline=BLK, width=4)

def table(d, x, y, s=1.0, w=520, col=WOOD, cloth=None):
    """Table (~330·s tall). cloth = tablecloth color."""
    S = lambda v: v * s; hw = S(w) / 2
    for dx in (-hw + S(40), hw - S(40)): d.rectangle([x + dx - S(14), y - S(300), x + dx + S(14), y], fill=dk(col, .85), outline=BLK, width=4)
    d.rectangle([x - hw, y - S(335), x + hw, y - S(295)], fill=col, outline=BLK, width=5)
    if cloth:
        d.polygon([(x - hw - S(10), y - S(340)), (x + hw + S(10), y - S(340)), (x + hw + S(30), y - S(220)), (x - hw - S(30), y - S(220))], fill=cloth, outline=BLK)
    return y - S(335)          # height of the surface

def counter(d, x, y, s=1.0, w=700, col=(120, 90, 70), top=(210, 210, 215)):
    """Counter / checkout (~380·s tall). Returns the y of the surface."""
    S = lambda v: v * s; hw = S(w) / 2
    d.rectangle([x - hw, y - S(360), x + hw, y], fill=col, outline=BLK, width=6)
    for k in range(1, 4): d.line([(x - hw + k * S(w) / 4, y - S(340)), (x - hw + k * S(w) / 4, y - S(20))], fill=dk(col, .8), width=4)
    d.rectangle([x - hw - S(20), y - S(385), x + hw + S(20), y - S(355)], fill=top, outline=BLK, width=5)
    return y - S(385)

def wall_clock(d, x, y, r=70, t=0.0, hour=None, minute=None, spin=0.0):
    """Wall clock centered at (x, y). spin>0 turns the hands (time passing)."""
    d.ellipse([x - r, y - r, x + r, y + r], fill=WHITE, outline=BLK, width=max(4, r // 12))
    for k in range(12):
        a = k / 12 * 2 * math.pi
        d.line([(x + math.cos(a) * r * .78, y + math.sin(a) * r * .78), (x + math.cos(a) * r * .9, y + math.sin(a) * r * .9)], fill=BLK, width=max(2, r // 25))
    h = (hour if hour is not None else 3) + spin * t / 12; m = (minute if minute is not None else 0) + spin * t * 5
    for ang, L, wd in ((h / 12 * 2 * math.pi, .5, r // 9), (m / 60 * 2 * math.pi, .75, r // 14)):
        d.line([(x, y), (x + math.sin(ang) * r * L, y - math.cos(ang) * r * L)], fill=BLK, width=max(3, wd))
    d.ellipse([x - r * .08, y - r * .08, x + r * .08, y + r * .08], fill=RED)

def alarm_clock(d, x, y, s=1.0, t=0.0, ring=False, text="7:00"):
    """Alarm clock; y = base."""
    S = lambda v: v * s; sh = math.sin(t * 50) * S(6) if ring else 0
    x += sh
    for dx in (-55, 55): d.ellipse([x + S(dx) - S(30), y - S(190), x + S(dx) + S(30), y - S(140)], fill=(220, 60, 60), outline=BLK, width=4)
    d.line([(x - S(50), y), (x - S(35), y - S(30))], fill=BLK, width=int(S(10))); d.line([(x + S(50), y), (x + S(35), y - S(30))], fill=BLK, width=int(S(10)))
    d.ellipse([x - S(80), y - S(170), x + S(80), y - S(10)], fill=(220, 60, 60), outline=BLK, width=5)
    d.ellipse([x - S(62), y - S(152), x + S(62), y - S(28)], fill=WHITE, outline=BLK, width=3)
    d.text((x, y - S(90)), text, font=F(S(40)), fill=BLK, anchor="mm")
    if ring:
        for side in (-1, 1): d.arc([x + side * S(110) - S(30), y - S(200), x + side * S(110) + S(30), y - S(120)], 270 if side > 0 else 90, 90 if side > 0 else 270, fill=BLK, width=4)

def window(d, x0, y0, x1, y1, kind="day", t=0.0, frame=(240, 240, 240)):
    """Window in a box. kind: day | night (with moon) | blinds | storm."""
    sky = {"day": (150, 205, 240), "night": (20, 25, 55), "blinds": (150, 200, 235), "storm": (60, 65, 85)}[kind]
    d.rectangle([x0, y0, x1, y1], fill=sky, outline=frame, width=12)
    if kind == "night":
        r = (x1 - x0) * .12; cx, cy = x1 - (x1 - x0) * .28, y0 + (y1 - y0) * .28
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(245, 240, 200))
    if kind == "blinds":
        for k in range(1, 4): d.line([(x0 + k * (x1 - x0) / 4, y0), (x0 + k * (x1 - x0) / 4, y1)], fill=frame, width=5)
    else:
        d.line([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)], fill=frame, width=8)
        if kind == "day":
            d.line([(x0 + 20, y0 + 30), (x0 + 60, y0 + 70)], fill=WHITE, width=6)
    if kind == "storm" and int(t * 2) % 5 == 0:
        mx = (x0 + x1) / 2
        d.line([(mx - 20, y0 + 20), (mx + 10, (y0 + y1) / 2), (mx - 10, (y0 + y1) / 2), (mx + 20, y1 - 20)], fill=YEL, width=6)

def picture(d, x0, y0, x1, y1, kind="landscape", frame=(120, 80, 50), label=None):
    """Hanging picture. kind: landscape | sea | portrait | blank. label = plaque at the bottom (e.g. EMPLOYEE OF THE MONTH)."""
    d.rectangle([x0, y0, x1, y1], fill=frame, outline=BLK, width=6)
    i0, j0, i1, j1 = x0 + 16, y0 + 16, x1 - 16, y1 - 16 - (50 if label else 0)
    if kind == "landscape":
        d.rectangle([i0, j0, i1, j1], fill=(250, 240, 210))
        d.polygon([(i0, j1), (i0 + (i1 - i0) * .35, j0 + (j1 - j0) * .35), (i0 + (i1 - i0) * .6, j1 - (j1 - j0) * .25), (i0 + (i1 - i0) * .8, j0 + (j1 - j0) * .5), (i1, j1)], fill=(80, 160, 90))
    elif kind == "sea":
        d.rectangle([i0, j0, i1, j1], fill=(160, 210, 240)); d.rectangle([i0, (j0 + j1) / 2, i1, j1], fill=(50, 120, 190))
        r = (i1 - i0) * .1; d.ellipse([i1 - 3 * r, j0 + r, i1 - r, j0 + 3 * r], fill=YEL)
    elif kind == "portrait":
        d.rectangle([i0, j0, i1, j1], fill=(230, 220, 190))
        cx, w = (i0 + i1) / 2, i1 - i0
        d.chord([cx - w * .35, j1 - (j1 - j0) * .35, cx + w * .35, j1 + (j1 - j0) * .25], 180, 360, fill=(90, 100, 130))
        d.ellipse([cx - w * .2, j0 + (j1 - j0) * .2, cx + w * .2, j0 + (j1 - j0) * .62], fill=(241, 194, 150), outline=BLK, width=3)
    else:
        d.rectangle([i0, j0, i1, j1], fill=(235, 235, 230))
    if label:
        d.rectangle([x0 + 16, y1 - 62, x1 - 16, y1 - 16], fill=(200, 160, 60), outline=BLK, width=3)
        d.text(((x0 + x1) / 2, y1 - 39), label, font=fit_font(d, label, x1 - x0 - 50, 30), fill=BLK, anchor="mm")
    return (i0, j0, i1, j1)

def floor_lamp(d, x, y, s=1.0, on=True):
    """Floor lamp; y = floor."""
    S = lambda v: v * s
    if on: d.polygon([(x - S(70), y - S(560)), (x + S(70), y - S(560)), (x + S(200), y - S(150)), (x - S(200), y - S(150))], fill=(255, 245, 190))
    d.ellipse([x - S(60), y - S(16), x + S(60), y + S(8)], fill=(60, 60, 60))
    d.line([(x, y), (x, y - S(560))], fill=(70, 70, 70), width=int(S(10)))
    d.polygon([(x - S(55), y - S(660)), (x + S(55), y - S(660)), (x + S(80), y - S(560)), (x - S(80), y - S(560))], fill=(240, 220, 150) if on else (200, 190, 160), outline=BLK)

def door(d, x0, y0, x1, y1, col=(150, 100, 60), opened=0.0, inside=(40, 40, 50), knob=True):
    """Door in a box; opened 0..1 (opens inward showing 'inside')."""
    d.rectangle([x0 - 12, y0 - 12, x1 + 12, y1], fill=(230, 225, 215), outline=BLK, width=5)
    d.rectangle([x0, y0, x1, y1], fill=inside)
    w = (x1 - x0) * (1 - .8 * opened)
    d.rectangle([x0, y0, x0 + w, y1], fill=col, outline=BLK, width=5)
    if w > 60:
        for yy in (y0 + 30, (y0 + y1) / 2 + 20): d.rectangle([x0 + 22, yy, x0 + w - 22, yy + (y1 - y0) * .35], outline=dk(col, .8), width=4)
        if knob: d.ellipse([x0 + w - 45, (y0 + y1) / 2 - 12, x0 + w - 21, (y0 + y1) / 2 + 12], fill=(230, 190, 60), outline=BLK, width=3)

def shelf(d, x0, y0, x1, y1, rows=4, seed=1, items=True):
    """Shelf with colorful products (store, pantry)."""
    import random; rnd = random.Random(seed)
    d.rectangle([x0, y0, x1, y1], fill=(120, 120, 130), outline=BLK, width=5)
    rh = (y1 - y0) / rows
    for r in range(rows):
        by = y0 + (r + 1) * rh
        d.rectangle([x0, by - 14, x1, by], fill=(200, 200, 205))
        if items:
            x = x0 + 12
            while x < x1 - 50:
                w = rnd.randint(30, 60); h = rnd.uniform(.45, .8) * rh
                c = rnd.choice([(220, 60, 60), (60, 140, 220), (240, 200, 50), (70, 170, 90), (240, 240, 240), (230, 130, 40)])
                d.rectangle([x, by - 14 - h, x + w, by - 14], fill=c, outline=BLK, width=2); x += w + 8

def light_switch(d, x, y, s=1.0, on=False):
    S = lambda v: v * s
    d.rounded_rectangle([x - S(35), y - S(55), x + S(35), y + S(55)], int(S(10)), fill=(245, 245, 240), outline=BLK, width=4)
    d.rounded_rectangle([x - S(12), y - S(30) + (0 if on else S(25)), x + S(12), y + (S(-5) if on else S(30))], int(S(5)), fill=(220, 220, 215), outline=BLK, width=3)

def laptop(d, x, y, s=1.0, screen=(40, 120, 220), back=False):
    """Laptop on a surface at y. back=True shows it from behind."""
    S = lambda v: v * s
    d.polygon([(x - S(150), y), (x + S(150), y), (x + S(130), y - S(16)), (x - S(130), y - S(16))], fill=(170, 170, 180), outline=BLK)
    d.rounded_rectangle([x - S(125), y - S(190), x + S(125), y - S(16)], int(S(10)), fill=(70, 70, 80) if back else (40, 40, 45), outline=BLK, width=4)
    if not back: d.rectangle([x - S(110), y - S(175), x + S(110), y - S(30)], fill=screen)
    else: d.ellipse([x - S(18), y - S(120), x + S(18), y - S(84)], fill=(200, 200, 210))

def piggy_bank(d, x, y, s=1.0, coin=True, t=0.0):
    """Piggy bank; y = base."""
    S = lambda v: v * s; P = (245, 160, 180)
    for dx in (-60, 50): d.rectangle([x + S(dx) - S(16), y - S(60), x + S(dx) + S(16), y], fill=dk(P, .85), outline=BLK, width=3)
    d.ellipse([x - S(130), y - S(220), x + S(120), y - S(30)], fill=P, outline=BLK, width=5)
    d.polygon([(x + S(30), y - S(205)), (x + S(60), y - S(260)), (x + S(80), y - S(195))], fill=P, outline=BLK)
    d.ellipse([x + S(95), y - S(150), x + S(165), y - S(90)], fill=dk(P, .9), outline=BLK, width=4)
    for dx in (115, 140): d.ellipse([x + S(dx) - S(6), y - S(126), x + S(dx) + S(6), y - S(114)], fill=BLK)
    d.ellipse([x + S(55), y - S(160), x + S(75), y - S(140)], fill=BLK)
    d.rectangle([x - S(40), y - S(222), x + S(20), y - S(212)], fill=BLK)
    if coin:
        cy = y - S(300) + (t * S(200)) % S(90)
        d.ellipse([x - S(32), cy - S(30), x + S(12), cy + S(30)], fill=(240, 200, 50), outline=BLK, width=4)
