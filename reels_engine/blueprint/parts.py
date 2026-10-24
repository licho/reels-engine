"""Parts of the blueprint style: white-line drawings of infrastructure and mechanisms that come back across episodes.
Pipes with water running through, valve, pump, open tank, water tower, faucet and falling water, pressure gauge,
water meter, house, building, a skyscraper cut open (floors, core, columns, piles) and terrain.

Every piece has an img version (draws its own layer). Pipes, tanks and the rest also have a Plate version (the same
name starting with `draw_`) to combine several in one layer:

    plan_pipe(img, [(40, 1200), (500, 1200), (500, 800)], c.t)
    pump(img, 220, 1200, 54, c.t)
    water_tower(img, 840, 900, 160, 200, level=.7, t=c.t)
"""
import math

from . import Plate, text, mix, bounds, NEON, WHITE, CYAN, GRAY, DIM, ACCENT, VOLT, PANEL, GROUND
from .section import building

WATER = GROUND["water"]

# ---------- pipes and water ----------
def draw_pipe(p, pts, t=0.0, w=18, flow=True, speed=70, color=DIM, water=CYAN):
    """Pipe seen from the side on a Plate: grey walls, dark inside, cyan dashes travelling along (speed px/s)."""
    p.line(pts, color, w)
    p.line(pts, PANEL, max(2, w - 6))
    if flow: p.dashed(pts, water, max(2, w * .22), 16, 14, phase=-t * speed)

def plan_pipe(img, pts, t=0.0, w=18, flow=True, speed=70, color=DIM, water=CYAN, glow=NEON):
    """Pipe through the points with glowing water running inside (stops when flow=False); corners are elbows.
    water = color of what runs: CYAN water, VOLT electricity (a cable), LIME air or gas, MAGENTA data."""
    with Plate(img, bounds(pts, w + 4)) as p:
        draw_pipe(p, pts, t, w, False, speed, color, water)
    if flow:
        with Plate(img, bounds(pts, w + 4), glow=glow) as p:
            p.dashed(pts, water, max(2, w * .22), 16, 14, phase=-t * speed)

def pipe_cut(img, cx, cy, r, t=0.0, flow=True, fill=WATER, color=WHITE, glow=NEON):
    """A pipe cut across (it comes toward you): a full circle with glowing rings opening while water runs."""
    with Plate(img, (cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6)) as p:
        p.circle(cx, cy, r, fill=fill, color=color, w=5)
    with Plate(img, (cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6), glow=glow) as p:
        if flow:
            for k in range(3):
                rr = 6 + ((t * 40 + k * r / 3.4) % (r - 6))
                p.circle(cx, cy, rr, color=mix(fill, CYAN, 1 - rr / r), w=3)

def draw_stream(p, x, y0, y1, t, w=16):
    """Falling water on a Plate: three cyan dashed threads running down."""
    for k, dx in enumerate((-w / 3, 0, w / 3)):
        p.dashed([(x + dx, y0), (x + dx, y1)], CYAN, 3, 22, 10, phase=-t * 300 - k * 9)

def water_stream(img, x, y0, y1, t, w=16, glow=NEON):
    """Glowing water falling from (x, y0) to (x, y1)."""
    with Plate(img, (x - w - 4, y0 - 4, x + w + 4, y1 + 4), glow=glow) as p:
        draw_stream(p, x, y0, y1, t, w)

def water_drop(img, cx, cy, r, color=CYAN, outline=None):
    """A drop of water centered on (cx, cy)."""
    pts = [(cx, cy - r * 1.5)] + [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(-25, 206, 15)]
    with Plate(img, (cx - r - 4, cy - r * 1.6, cx + r + 4, cy + r + 4)) as p:
        p.poly(pts, fill=color, color=outline, w=3)

# ---------- machines ----------
def draw_valve(p, x, y, s=1.0, open=1.0, vertical=False, color=WHITE):
    """Valve symbol on a Plate: two triangles tip to tip (cyan inside when open) and a handle that turns a quarter
    turn from shut (0, across the pipe) to open (1, along it)."""
    L, h = 30 * s, 22 * s
    tri = [[(-L, -h), (-L, h), (0, 0)], [(L, -h), (L, h), (0, 0)]]
    fill = mix(PANEL, CYAN, .75 * open)
    for t_ in tri:
        p.poly([(x + (b if vertical else a), y + (a if vertical else b)) for a, b in t_], fill=fill, color=color, w=3)
    sx, sy = (x - 40 * s, y) if vertical else (x, y - 40 * s)
    p.line([(x, y), (sx, sy)], color, 4)
    ang = (1 - open) * math.pi / 2 + (math.pi / 2 if vertical else 0)
    dx, dy = 20 * s * math.cos(ang), 20 * s * math.sin(ang)
    p.line([(sx - dx, sy - dy), (sx + dx, sy + dy)], color, 6)

def valve(img, x, y, s=1.0, open=1.0, vertical=False):
    """Valve on a pipe at (x, y): open (cyan inside) or shut (dark), with its handle."""
    with Plate(img, (x - 60 * s, y - 60 * s, x + 60 * s, y + 60 * s)) as p:
        draw_valve(p, x, y, s, open, vertical)

def draw_pump(p, x, y, r, t=0.0, on=True, color=WHITE):
    """Pump on a Plate: a casing with a three-blade impeller that turns while on."""
    p.circle(x, y, r, fill=PANEL, color=color, w=4)
    for k in range(3):
        a = (t * 7 if on else 0) + k * 2.094
        p.line([(x, y), (x + r * .8 * math.cos(a), y + r * .8 * math.sin(a))], CYAN if on else DIM, max(3, r * .11))
    p.circle(x, y, r * .14, fill=color)

def pump(img, x, y, r=54, t=0.0, on=True, color=VOLT, glow=NEON):
    """Pump centered at (x, y) whose impeller turns and glows (in the electricity color) while on."""
    with Plate(img, (x - r - 6, y - r - 6, x + r + 6, y + r + 6)) as p:
        p.circle(x, y, r, fill=PANEL, color=WHITE, w=4)
    with Plate(img, (x - r - 6, y - r - 6, x + r + 6, y + r + 6), glow=glow if on else 0) as p:
        for k in range(3):
            a = (t * 7 if on else 0) + k * 2.094
            p.line([(x, y), (x + r * .8 * math.cos(a), y + r * .8 * math.sin(a))], color if on else DIM, max(3, r * .11))
        p.circle(x, y, r * .14, fill=WHITE)

def draw_tank(p, x0, y0, x1, y1, level, t=0.0, fill=WATER, color=WHITE, lid=False):
    """Open tank cut in section on a Plate, water up to 'level' (0 to 1) with a rippling cyan surface;
    returns the water line y."""
    wy = y1 - (y1 - y0) * max(0.0, min(1.0, level))
    if level > .01:
        surf = [(x, wy + 3 * math.sin(x / 26 + t * 4)) for x in range(int(x0), int(x1) + 1, 8)] + [(x1, wy + 3 * math.sin(x1 / 26 + t * 4))]
        p.poly(surf + [(x1, y1), (x0, y1)], fill=fill)
        p.line(surf, CYAN, 3)
    p.line([(x0, y0), (x0, y1), (x1, y1), (x1, y0)], color, 4)
    if lid: p.line([(x0 - 10, y0), (x1 + 10, y0)], color, 4)
    return wy

def plan_tank(img, x0, y0, x1, y1, level, t=0.0, label="", percent=False, lid=False):
    """Tank seen in section, filled to 'level' (0 to 1), with an optional label and percentage."""
    with Plate(img, (x0 - 14, y0 - 10, x1 + 14, y1 + 6)) as p:
        draw_tank(p, x0, y0, x1, y1, level, t, lid=lid)
    if percent: text(img, f"{int(round(level * 100))} %", (x0 + x1) / 2, y1 + 30, 26, CYAN, anchor="mm")
    if label: text(img, label.upper(), (x0 + x1) / 2, y0 - 22, 22, GRAY, tracking=.2, anchor="mb")

def water_tower(img, x, base, w=160, h=200, level=.7, t=0.0, legs=.45, label=""):
    """Elevated water tank on braced legs, standing on (x, base) (x = center); h is the whole height."""
    top, tb = base - h, base - h * legs
    with Plate(img, (x - w / 2 - 16, top - 10, x + w / 2 + 16, base + 4)) as p:
        lx = (x - w * .38, x + w * .38)
        for xx in lx: p.line([(xx, tb), (xx, base)], WHITE, 4)
        n = 3; step = (base - tb) / n
        for i in range(n):
            ya, yb = tb + i * step, tb + (i + 1) * step
            p.line([(lx[0], ya), (lx[1], yb)], DIM, 2); p.line([(lx[1], ya), (lx[0], yb)], DIM, 2)
        draw_tank(p, x - w / 2, top, x + w / 2, tb, level, t, lid=True)
    if label: text(img, label.upper(), x, top - 22, 22, GRAY, tracking=.2, anchor="mb")
    return {"top": top, "bottom": tb, "water": tb - (tb - top) * level}

def draw_faucet(p, x, y, s=1.0, color=WHITE):
    """Wall faucet on a Plate: body at (x, y), spout to the right; returns the nozzle point."""
    p.rect(x - 30 * s, y - 24 * s, x + 30 * s, y + 24 * s, fill=PANEL, color=color, w=4)
    p.rect(x - 8 * s, y - 62 * s, x + 8 * s, y - 24 * s, fill=PANEL, color=color, w=4)
    p.line([(x - 34 * s, y - 66 * s), (x + 34 * s, y - 66 * s)], color, max(3, 8 * s))
    spout = [(x + 30 * s, y - 6 * s), (x + 120 * s, y - 6 * s), (x + 140 * s, y + 14 * s), (x + 140 * s, y + 46 * s)]
    p.line(spout, color, max(5, 12 * s)); p.line(spout, PANEL, max(2, 4 * s))
    return (x + 140 * s, y + 50 * s)

def faucet(img, x, y, s=1.0, t=0.0, running=False, fall=200):
    """Wall faucet with its body at (x, y); running=True pours water 'fall' px down. Returns the nozzle point."""
    with Plate(img, (x - 40 * s, y - 72 * s, x + 160 * s, y + 56 * s)) as p:
        nx, ny = draw_faucet(p, x, y, s)
    if running: water_stream(img, nx, ny, ny + fall, t, w=16 * s)
    return (nx, ny)

def pressure_gauge(img, cx, cy, r, value, vmax=4, label="bar", color=WHITE):
    """Round pressure gauge from 0 to vmax with its needle on value."""
    a0, a1 = math.radians(140), math.radians(400)
    with Plate(img, (cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8)) as p:
        p.circle(cx, cy, r, fill=PANEL, color=color, w=4)
        for k in range(vmax * 2 + 1):
            a = a0 + (a1 - a0) * k / (vmax * 2); L = 14 if k % 2 == 0 else 7
            p.line([(cx + math.cos(a) * (r - 6), cy + math.sin(a) * (r - 6)), (cx + math.cos(a) * (r - 6 - L), cy + math.sin(a) * (r - 6 - L))], GRAY, 3)
        a = a0 + (a1 - a0) * max(0, min(value, vmax)) / vmax
        p.line([(cx, cy), (cx + math.cos(a) * (r - 16), cy + math.sin(a) * (r - 16))], ACCENT, 5)
        p.circle(cx, cy, 7, fill=ACCENT)
    if label: text(img, label, cx, cy + r * .5, int(r * .3), GRAY, anchor="mm")

def water_meter(img, x, y, t=0.0, s=1.0, running=True):
    """Water meter box with a dial that spins while water passes."""
    with Plate(img, (x - 34 * s, y - 30 * s, x + 34 * s, y + 30 * s)) as p:
        p.rect(x - 30 * s, y - 26 * s, x + 30 * s, y + 26 * s, fill=PANEL, color=WHITE, w=3)
        p.circle(x, y, 14 * s, color=CYAN, w=3)
        a = t * 6 if running else 0
        p.line([(x, y), (x + 10 * s * math.cos(a), y + 10 * s * math.sin(a))], ACCENT, 3)

# ---------- buildings and terrain ----------
def plan_house(img, x0, base, w=300, h=130, fill=PANEL):
    """House outline with a gable roof standing on (x0, base) (x0 = left side)."""
    with Plate(img, (x0 - 6, base - h - w * .38 - 6, x0 + w + 6, base + 4)) as p:
        p.poly([(x0, base), (x0, base - h), (x0 + w / 2, base - h - w * .38), (x0 + w, base - h), (x0 + w, base)],
               fill=fill, color=WHITE, w=4)

def plan_building(img, x0, base, w, h):
    """Building outline with a grid of windows standing on (x0, base) (x0 = left side)."""
    with Plate(img, (x0 - 6, base - h - 6, x0 + w + 6, base + 4)) as p:
        building(p, x0, base, w, h)

def tower_section(img, x, base, w=260, floors=20, floor_h=24, piles=160, t=0.0, highlight=None, core=True, label_every=0):
    """Skyscraper cut open: floor slabs, central core, columns and foundation piles; highlight = floor in cyan."""
    top = base - floors * floor_h
    with Plate(img, (x - w / 2 - 10, top - 10, x + w / 2 + 10, base + piles + 10)) as p:
        p.rect(x - w / 2, top, x + w / 2, base, fill=PANEL, color=WHITE, w=4)
        for i in range(1, floors):
            yy = base - i * floor_h
            p.line([(x - w / 2, yy), (x + w / 2, yy)], CYAN if highlight == i else DIM, 3 if highlight == i else 2)
        for k in (-.5, -.17, .17, .5):
            p.line([(x + w * k, top), (x + w * k, base)], mix(PANEL, WHITE, .35), 2)
        if core: p.rect(x - w * .12, top, x + w * .12, base, fill=mix(PANEL, GRAY, .22), color=GRAY, w=2)
        if highlight is not None:
            yy = base - highlight * floor_h
            p.rect(x - w / 2 + 3, yy - floor_h + 2, x + w / 2 - 3, yy - 2, fill=mix(PANEL, CYAN, .25))
        if piles:
            p.rect(x - w / 2 - 20, base, x + w / 2 + 20, base + 26, fill=mix(PANEL, GRAY, .3), color=WHITE, w=3)
            for k in range(5):
                px = x - w / 2 + 10 + (w - 20) * k / 4
                p.rect(px - 7, base + 26, px + 7, base + piles, fill=mix(PANEL, GRAY, .3), color=WHITE, w=2)
    if label_every:
        for i in range(label_every, floors + 1, label_every):
            text(img, f"{i}", x + w / 2 + 16, base - i * floor_h + floor_h / 2, 20, GRAY, anchor="lm")
    return {"top": top, "floor": lambda i: base - i * floor_h}

def plan_terrain(img, pts, fill=None, color=WHITE):
    """Terrain profile (a hill, a valley, a slope): the outline through the points, filled down to the lowest one."""
    fill = fill if fill is not None else mix(PANEL, GRAY, .1)
    with Plate(img, bounds(pts, 6)) as p:
        p.poly(pts, fill=fill, color=color, w=3)
