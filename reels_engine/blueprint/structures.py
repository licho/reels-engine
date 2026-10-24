"""Structures of the blueprint style that come back in many episodes: houses (front and cut open with their hidden
pipes and wires), an apartment block with lit windows, a factory, power lines and five kinds of bridge (beam, truss,
arch, suspension and cable-stayed) with optional water underneath and traffic crossing.

They all take the image and stand on a ground line (base). Moving things (water, current, traffic lights, smoke) glow.
They return where their key points ended up, to place callouts:

    home_section(img, 120, 1250, t=c.t)                       # house cut open: water in cyan, power in yellow
    b = suspension_bridge(img, 40, 1040, 1000, 1250, t=c.t, traffic=True, forces=True)
    callout(img, "main cable", *b["cable_mid"], 700, 760)
"""
import math
import random

from . import Plate, mix, NEON, WHITE, CYAN, GRAY, DIM, VOLT, PANEL, GROUND

WATER = GROUND["water"]
LIT = mix(PANEL, VOLT, .55)                 # a window with the light on
DARK = mix(PANEL, GRAY, .18)                # a window with the light off

# ---------- houses and buildings ----------
def home_front(img, x, base, w=320, h=170, roof="gable", t=0.0, lights=0.0, chimney=True):
    """House seen from the front with door, windows and chimney (roof "gable" or "flat"); lights 0→1 turns them on."""
    rh = w * .38 if roof == "gable" else 16
    with Plate(img, (x - 14, base - h - rh - 50, x + w + 14, base + 4)) as p:
        if chimney: p.rect(x + w * .68, base - h - rh * .55 - 40, x + w * .78, base - h - rh * .25, fill=PANEL, color=WHITE, w=3)
        p.rect(x, base - h, x + w, base, fill=PANEL, color=WHITE, w=4)
        if roof == "gable":
            p.poly([(x - 12, base - h), (x + w / 2, base - h - rh), (x + w + 12, base - h)], fill=PANEL, color=WHITE, w=4)
        else:
            p.rect(x - 8, base - h - rh, x + w + 8, base - h, fill=PANEL, color=WHITE, w=4)
        dw = w * .2
        p.rect(x + w / 2 - dw / 2, base - h * .6, x + w / 2 + dw / 2, base, fill=mix(PANEL, GRAY, .12), color=WHITE, w=3)
        p.circle(x + w / 2 + dw * .3, base - h * .3, 3, fill=WHITE)
        for wx in (x + w * .1, x + w * .7):
            fill = mix(DARK, LIT, max(0.0, min(1.0, lights)))
            p.rect(wx, base - h * .7, wx + w * .2, base - h * .35, fill=fill, color=WHITE, w=3)
            p.line([(wx + w * .1, base - h * .7), (wx + w * .1, base - h * .35)], WHITE, 2)
    if chimney:                                                     # smoke rises from the chimney
        _smoke(img, x + w * .73, base - h - rh * .55 - 42, t)
    return {"door": (x + w / 2, base), "roof": (x + w / 2, base - h - rh), "top": base - h - rh}

def _smoke(img, x, y, t, n=3, size=1.0):
    with Plate(img, (x - 40 * size, y - 120 * size, x + 40 * size, y)) as p:
        for i in range(n):
            u = (t * .5 + i / n) % 1
            r = (6 + 16 * u) * size
            p.circle(x + 10 * size * math.sin(u * 5 + i), y - 10 * size - 90 * size * u, r,
                     color=mix(GRAY, PANEL, u), w=2)

def home_section(img, x, base, w=520, floors=2, floor_h=150, t=0.0, water=True, power=True, foundation=60, glow=NEON):
    """House cut open: floors, rooms, stairs and foundation, with the hidden pipe (cyan) and wiring (yellow) running."""
    top = base - floors * floor_h; rh = w * .3
    with Plate(img, (x - 16, top - rh - 6, x + w + 16, base + foundation + 6)) as p:
        p.rect(x - 10, base, x + w + 10, base + foundation, fill=mix(PANEL, GRAY, .25))
        p.hatch([(x - 10, base), (x + w + 10, base), (x + w + 10, base + foundation), (x - 10, base + foundation)],
                DIM, 14)
        p.rect(x - 10, base, x + w + 10, base + foundation, color=WHITE, w=3)
        p.rect(x, top, x + w, base, fill=PANEL, color=WHITE, w=5)
        p.poly([(x - 14, top), (x + w / 2, top - rh), (x + w + 14, top)], fill=PANEL, color=WHITE, w=5)
        for i in range(1, floors):
            y = base - i * floor_h
            p.rect(x, y - 6, x + w, y + 6, fill=mix(PANEL, GRAY, .3), color=WHITE, w=2)
        for i in range(floors):                                     # inner walls with a door gap
            y0, y1 = base - (i + 1) * floor_h, base - i * floor_h
            p.line([(x + w * .62, y0 + 6), (x + w * .62, y1 - floor_h * .6)], GRAY, 4)
        for i in range(floors - 1):                                 # stairs
            y0, y1 = base - i * floor_h, base - (i + 1) * floor_h
            n = 7; sx, sw = x + w * .08, w * .3
            pts = []
            for k in range(n + 1):
                pts += [(sx + sw * k / n, y0 - (y0 - y1) * k / n), (sx + sw * (k + 1) / n, y0 - (y0 - y1) * k / n)]
            p.line(pts[:-1], GRAY, 2)
    pipe = [(x + w * .82, base + foundation + 6), (x + w * .82, top + 40), (x + w * .9, top + 40)]
    wire = [(x + w * .5, top - rh * .55), (x + w * .5, top + 14), (x + w * .74, top + 14), (x + w * .74, base - 40),
            (x + w * .7, base - 40)]
    lamp = (x + w * .4, top + 54)
    branch = [(x + w * .5, top + 14), (lamp[0], top + 14), (lamp[0], lamp[1] - 14)]
    with Plate(img, (x - 4, top - rh, x + w + 4, base + foundation + 8)) as p:
        if water:
            p.line(pipe, DIM, 14); p.line(pipe, PANEL, 8)
        if power:
            p.rect(x + w * .7 - 10, base - 52, x + w * .7, base - 28, fill=PANEL, color=WHITE, w=2)
    with Plate(img, (x - 4, top - rh, x + w + 4, base + foundation + 8), glow=glow) as p:
        if water: p.dashed(pipe, CYAN, 3, 14, 12, phase=-t * 70)
        if power:
            p.dashed(wire, VOLT, 3, 8, 10, phase=-t * 90); p.dashed(branch, VOLT, 3, 8, 10, phase=-t * 90)
            p.poly([(lamp[0] - 22, lamp[1] + 6), (lamp[0] + 22, lamp[1] + 6), (lamp[0] + 10, lamp[1] - 14),
                    (lamp[0] - 10, lamp[1] - 14)], fill=VOLT)
    return {"top": top - rh, "floor": lambda i: base - i * floor_h, "pipe": pipe[1], "wire": wire[1], "lamp": lamp,
            "foundation": (x + w / 2, base + foundation / 2)}

def apartment_block(img, x, base, w=300, floors=10, floor_h=48, t=0.0, lit=.4, seed=1, roof_tank=True):
    """Apartment building seen from the front: rows of windows (a share 'lit' with the light on, a few change over
    time), balconies, entrance and a water tank on the roof."""
    rnd = random.Random(f"apartment:{seed}"); top = base - floors * floor_h
    cols = max(2, int(w // 60))
    with Plate(img, (x - 10, top - 70, x + w + 10, base + 4)) as p:
        if roof_tank:
            p.rect(x + w * .62, top - 50, x + w * .86, top - 22, fill=PANEL, color=WHITE, w=3)
            for lx in (x + w * .65, x + w * .83): p.line([(lx, top - 22), (lx, top)], WHITE, 3)
        p.rect(x, top, x + w, base, fill=PANEL, color=WHITE, w=4)
        cw = w / cols
        for f in range(floors):
            y0 = top + f * floor_h
            if f < floors - 1: p.line([(x, y0 + floor_h), (x + w, y0 + floor_h)], DIM, 2)
            for c_ in range(cols):
                wx = x + c_ * cw + cw * .2
                if f == floors - 1 and c_ == cols // 2:              # entrance
                    p.rect(wx, y0 + floor_h * .2, wx + cw * .6, base, fill=mix(PANEL, GRAY, .2), color=WHITE, w=2)
                    continue
                on = rnd.random() < lit
                if rnd.random() < .12: on = (math.sin(t * 1.3 + f * 3.1 + c_ * 1.7) > 0)
                p.rect(wx, y0 + floor_h * .22, wx + cw * .6, y0 + floor_h * .72, fill=LIT if on else DARK)
            if f % 2 and f < floors - 1:
                p.line([(x + cw * .1, y0 + floor_h * .8), (x + cw * .9, y0 + floor_h * .8)], GRAY, 3)
    return {"top": top, "floor": lambda i: base - i * floor_h, "roof": (x + w / 2, top)}

def factory(img, x, base, w=440, h=150, t=0.0, smoke=True):
    """Factory with a sawtooth roof, windows and a chimney (smoke rises when 'smoke')."""
    n = 4; tw_ = w * .7 / n; ch = h * 1.9
    with Plate(img, (x - 10, base - ch - 6, x + w + 10, base + 4)) as p:
        p.rect(x + w * .8, base - ch, x + w * .9, base - h, fill=PANEL, color=WHITE, w=3)
        for k in range(1, 4): p.line([(x + w * .8, base - ch + k * 26), (x + w * .9, base - ch + k * 26)], DIM, 2)
        p.rect(x, base - h, x + w, base, fill=PANEL, color=WHITE, w=4)
        saw = [(x, base - h)]
        for i in range(n):
            saw += [(x + i * tw_, base - h - h * .35), (x + (i + 1) * tw_, base - h)]
        p.poly(saw + [(x + n * tw_, base - h)], fill=PANEL, color=WHITE, w=4)
        for i in range(n): p.line([(x + i * tw_ + 4, base - h - h * .3), (x + i * tw_ + 4, base - h - 4)], CYAN, 3)
        for i in range(5):
            wx = x + 20 + i * (w - 40) / 5
            p.rect(wx, base - h * .7, wx + (w - 40) / 5 - 16, base - h * .45, fill=DARK, color=GRAY, w=2)
        p.rect(x + w * .12, base - h * .32, x + w * .32, base, fill=mix(PANEL, GRAY, .15), color=WHITE, w=3)
    if smoke: _smoke(img, x + w * .85, base - ch, t, size=1.5)
    return {"chimney": (x + w * .85, base - ch), "top": base - ch}

def power_line(img, xs, base, h=300, t=0.0, sag=40, glow=NEON):
    """Lattice pylons at the given x positions joined by sagging cables with current (yellow pulses) running."""
    arms = [(base - h + 30, h * .2), (base - h + 90, h * .26)]
    with Plate(img, (min(xs) - h * .3, base - h - 10, max(xs) + h * .3, base + 4)) as p:
        for x in xs:
            hw = h * .14
            L = [(x - hw, base), (x - hw * .25, base - h * .8), (x, base - h)]
            R = [(x + hw, base), (x + hw * .25, base - h * .8), (x, base - h)]
            p.line(L, WHITE, 3); p.line(R, WHITE, 3)
            for k in range(6):                                       # lattice
                ya, yb = base - h * .8 * k / 6, base - h * .8 * (k + 1) / 6
                wa, wb = hw - (hw * .75) * k / 6, hw - (hw * .75) * (k + 1) / 6
                p.line([(x - wa, ya), (x + wb, yb)], DIM, 2); p.line([(x + wa, ya), (x - wb, yb)], DIM, 2)
            for y, aw in arms: p.line([(x - aw, y), (x + aw, y)], WHITE, 3)
    cables = []
    for y, aw in arms:
        for s in (-1, 1):
            for a, b in zip(xs, xs[1:]):
                pts = [(a + s * aw + (b - a) * k / 16, y + 6 + sag * 4 * (k / 16) * (1 - k / 16)) for k in range(17)]
                cables.append(pts)
    with Plate(img, (min(xs) - h * .3, base - h - 10, max(xs) + h * .3, base), glow=glow) as p:
        for pts in cables:
            p.line(pts, mix(GRAY, VOLT, .25), 2)
            p.dashed(pts, VOLT, 3, 6, 40, phase=-t * 160)
    return {"tops": [(x, base - h) for x in xs]}

# ---------- bridges ----------
def _bridge_ground(p, x0, x1, deck, base, water):
    """Banks at both ends and, between them, water (or ground) under the bridge."""
    if water:
        p.rect(x0 + 40, base - 26, x1 - 40, base + 30, fill=WATER)
    for a, d in ((x0, 1), (x1, -1)):
        bank = [(a, deck + 18), (a + d * 60, deck + 18), (a + d * 130, base), (a + d * 130, base + 30), (a, base + 30)]
        p.poly(bank, fill=mix(PANEL, GRAY, .2))
        p.hatch(bank, DIM, 16)
        p.line(bank[:3] + [(a + d * 130, base + 30)], WHITE, 3)

def _bridge_life(img, x0, x1, deck, base, t, water, traffic, glow):
    """What moves on a bridge: ripples on the water and cars crossing with their lights on."""
    with Plate(img, (x0, deck - 30, x1, base + 30), glow=glow) as p:
        if water:
            for k in range(3):
                y = base - 16 + k * 14
                p.dashed([(x0 + 150, y), (x1 - 150, y)], mix(WATER, CYAN, .6 - k * .15), 2, 30, 50, phase=-t * (30 + 10 * k))
        if traffic:
            L = x1 - x0
            for i in range(3):
                for direction in (1, -1):
                    u = (t * .12 * (1 + i * .15) + i / 3 + (.5 if direction < 0 else 0)) % 1
                    cx = x0 + (u if direction > 0 else 1 - u) * L
                    p.rect(cx - 18, deck - 14, cx + 18, deck - 2, fill=PANEL, color=WHITE, w=2)
                    p.circle(cx + direction * 18, deck - 8, 3, fill=VOLT)

def _deck(p, x0, x1, deck):
    p.rect(x0, deck, x1, deck + 18, fill=mix(PANEL, GRAY, .3), color=WHITE, w=3)

def beam_bridge(img, x0, x1, deck, base, piers=3, t=0.0, water=True, traffic=False, glow=NEON):
    """Beam bridge: a straight deck resting on piers (the simplest kind)."""
    xs = [x0 + 130 + (x1 - x0 - 260) * (i + 1) / (piers + 1) for i in range(piers)]
    with Plate(img, (x0 - 4, deck - 6, x1 + 4, base + 34)) as p:
        _bridge_ground(p, x0, x1, deck, base, water)
        for x in xs:
            p.rect(x - 14, deck + 18, x + 14, base, fill=PANEL, color=WHITE, w=3)
            p.rect(x - 30, base, x + 30, base + 20, fill=mix(PANEL, GRAY, .3), color=WHITE, w=3)
        _deck(p, x0, x1, deck)
    _bridge_life(img, x0, x1, deck, base, t, water, traffic, glow)
    return {"deck": deck, "piers": [(x, (deck + base) / 2) for x in xs]}

def truss_bridge(img, x0, x1, deck, base, height=140, panels=8, t=0.0, water=True, traffic=False, glow=NEON):
    """Truss bridge: a frame of triangles above the deck carries the load to the banks."""
    a, b = x0 + 60, x1 - 60; seg = (b - a) / panels; top = deck - height
    with Plate(img, (x0 - 4, top - 6, x1 + 4, base + 34)) as p:
        _bridge_ground(p, x0, x1, deck, base, water)
        _deck(p, x0, x1, deck)
        p.line([(a, deck), (a + seg, top), (b - seg, top), (b, deck)], WHITE, 5)
        for i in range(1, panels):
            xx = a + i * seg
            p.line([(xx, deck), (xx, top)], WHITE, 3)
        for i in range(1, panels - 1):                               # diagonals lean toward the middle (Pratt)
            xx = a + i * seg
            if xx < (a + b) / 2: p.line([(xx, top), (xx + seg, deck)], GRAY, 3)
            else: p.line([(xx + seg, top), (xx, deck)], GRAY, 3)
    _bridge_life(img, x0, x1, deck, base, t, water, traffic, glow)
    return {"deck": deck, "top": top, "mid": ((a + b) / 2, top)}

def arch_bridge(img, x0, x1, deck, base, t=0.0, water=True, traffic=False, glow=NEON, columns=9):
    """Arch bridge: an arch under the deck pushes the load into the banks; columns hold the deck on the arch."""
    a, b = x0 + 120, x1 - 120; crown = deck + 26
    arch = lambda u: (a + (b - a) * u, base - (base - crown) * 4 * u * (1 - u))
    with Plate(img, (x0 - 4, deck - 6, x1 + 4, base + 34)) as p:
        _bridge_ground(p, x0, x1, deck, base, water)
        pts = [arch(k / 40) for k in range(41)]
        p.line(pts, WHITE, 10); p.line(pts, mix(PANEL, GRAY, .3), 4)
        for i in range(1, columns + 1):
            x, y = arch(i / (columns + 1))
            if y - deck > 30: p.line([(x, deck + 18), (x, y - 5)], GRAY, 4)
        _deck(p, x0, x1, deck)
    _bridge_life(img, x0, x1, deck, base, t, water, traffic, glow)
    return {"deck": deck, "crown": arch(.5), "springs": (arch(0), arch(1))}

def suspension_bridge(img, x0, x1, deck, base, tower_h=260, t=0.0, water=True, traffic=False, forces=False, glow=NEON):
    """Suspension bridge: two towers, the main cable hanging between them and hangers holding the deck;
    forces=True sends cyan pulses along the cable toward the anchors (the pull it carries)."""
    ta, tb = x0 + (x1 - x0) * .24, x1 - (x1 - x0) * .24; ttop = deck - tower_h; low = deck - 24
    def cable_y(x):
        if x < ta: u = (x - x0) / (ta - x0); return deck - (deck - ttop) * u ** 1.6
        if x > tb: u = (x1 - x) / (x1 - tb); return deck - (deck - ttop) * u ** 1.6
        u = (x - ta) / (tb - ta); return ttop + (low - ttop) * 4 * u * (1 - u) * 1.0
    xs = [x0 + 10 + (x1 - x0 - 20) * k / 120 for k in range(121)]
    cable = [(x, cable_y(x)) for x in xs]
    with Plate(img, (x0 - 4, ttop - 30, x1 + 4, base + 34)) as p:
        _bridge_ground(p, x0, x1, deck, base, water)
        for k in range(1, 40):
            x = x0 + (x1 - x0) * k / 40
            if abs(x - ta) > 10 and abs(x - tb) > 10 and cable_y(x) < deck - 8: p.line([(x, cable_y(x)), (x, deck)], DIM, 2)
        p.line(cable, WHITE, 4)
        for x in (ta, tb):
            p.rect(x - 12, ttop - 20, x + 12, base, fill=PANEL, color=WHITE, w=3)
            for y in (ttop + 20, deck - tower_h * .45): p.line([(x - 12, y), (x + 12, y)], WHITE, 3)
            p.rect(x - 30, base, x + 30, base + 22, fill=mix(PANEL, GRAY, .3), color=WHITE, w=3)
        for a in (x0 + 10, x1 - 10): p.rect(a - 14, deck - 10, a + 14, deck + 18, fill=mix(PANEL, GRAY, .4), color=WHITE, w=3)
        _deck(p, x0, x1, deck)
    if forces:
        with Plate(img, (x0 - 4, ttop - 30, x1 + 4, deck + 4), glow=glow) as p:
            mid = len(cable) // 2
            p.dashed(cable[mid::-1], CYAN, 4, 18, 22, phase=-t * 80)
            p.dashed(cable[mid:], CYAN, 4, 18, 22, phase=-t * 80)
    _bridge_life(img, x0, x1, deck, base, t, water, traffic, glow)
    return {"deck": deck, "towers": [(ta, ttop), (tb, ttop)], "cable_mid": ((x0 + x1) / 2, cable_y((x0 + x1) / 2)),
            "anchors": [(x0 + 10, deck), (x1 - 10, deck)]}

def cable_stayed_bridge(img, x0, x1, deck, base, tower_h=300, towers=2, cables=8, t=0.0, water=True, traffic=False,
                        forces=False, glow=NEON):
    """Cable-stayed bridge: one or two tall towers with straight cables fanning down to the deck."""
    if towers == 1: txs = [(x0 + x1) / 2]
    else: txs = [x0 + (x1 - x0) * .3, x1 - (x1 - x0) * .3]
    reach = (x1 - x0) * (.42 if towers == 1 else .19)
    stays = []
    for tx in txs:
        for s in (-1, 1):
            for k in range(cables):
                stays.append([(tx, deck - tower_h + 20 + k * (tower_h * .35) / cables),
                              (tx + s * reach * (cables - k) / cables, deck)])
    with Plate(img, (x0 - 4, deck - tower_h - 30, x1 + 4, base + 34)) as p:
        _bridge_ground(p, x0, x1, deck, base, water)
        for st in stays: p.line(st, GRAY, 2)
        for tx in txs:
            p.poly([(tx - 26, base), (tx - 6, deck - tower_h), (tx + 6, deck - tower_h), (tx + 26, base)],
                   fill=PANEL, color=WHITE, w=3)
            p.rect(tx - 34, base, tx + 34, base + 22, fill=mix(PANEL, GRAY, .3), color=WHITE, w=3)
        _deck(p, x0, x1, deck)
    if forces:
        with Plate(img, (x0 - 4, deck - tower_h - 30, x1 + 4, deck + 4), glow=glow) as p:
            for st in stays: p.dashed(st[::-1], CYAN, 3, 12, 30, phase=-t * 70)
    _bridge_life(img, x0, x1, deck, base, t, water, traffic, glow)
    return {"deck": deck, "towers": [(tx, deck - tower_h) for tx in txs]}

def bridge(img, kind, x0, x1, deck, base, **kw):
    """Any bridge by kind: "beam", "truss", "arch", "suspension" or "cable_stayed"."""
    return {"beam": beam_bridge, "truss": truss_bridge, "arch": arch_bridge, "suspension": suspension_bridge,
            "cable_stayed": cable_stayed_bridge}[kind](img, x0, x1, deck, base, **kw)
