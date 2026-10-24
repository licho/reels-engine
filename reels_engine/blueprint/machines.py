"""Machines of the blueprint style that come back in many episodes: gears, a piston engine cut open, an electric
motor, a jet engine cut open and a wind turbine. They all animate with t (what turns, turns; what burns, glows) and
take `speed` to go faster or slower (0 stops them).

    piston_engine(img, 540, 900, 1.6, c.t)                    # piston up and down, crank turning, spark on top
    gear_pair(img, 380, 1000, 120, 70, c.t)                   # two meshing gears, the small one turns faster
"""
import math

from . import Plate, mix, NEON, WHITE, CYAN, GRAY, DIM, ACCENT, RISK, VOLT, LIME, MAGENTA, PANEL

STEEL = mix(PANEL, GRAY, .3)
COPPER = mix(PANEL, ACCENT, .6)

# ---------- gears ----------
def gear_points(cx, cy, r, teeth, angle=0.0):
    """Outline of a gear: r = pitch radius, teeth around it, turned by angle (radians)."""
    pitch = 2 * math.pi / teeth; h = 2 * math.pi * r / teeth * .55
    ro, rr = r + h / 2, r - h / 2; pts = []
    for i in range(teeth):
        a = angle + i * pitch
        for f, rad in ((0, rr), (.15, ro), (.45, ro), (.6, rr)):
            pts.append((cx + rad * math.cos(a + f * pitch), cy + rad * math.sin(a + f * pitch)))
    return pts

def draw_gear(p, cx, cy, r, teeth, angle=0.0, color=WHITE, fill=STEEL, hub=True):
    """Gear on a Plate, with spokes and hub."""
    p.poly(gear_points(cx, cy, r, teeth, angle), fill=fill, color=color, w=3)
    if hub:
        p.circle(cx, cy, r * .62, fill=PANEL, color=color, w=2)
        for k in range(4):
            a = angle + k * math.pi / 2
            p.line([(cx + r * .2 * math.cos(a), cy + r * .2 * math.sin(a)),
                    (cx + r * .62 * math.cos(a), cy + r * .62 * math.sin(a))], color, max(3, r * .1))
        p.circle(cx, cy, r * .2, fill=fill, color=color, w=2)

def gear(img, cx, cy, r=100, teeth=None, t=0.0, speed=1.0, color=WHITE):
    """One gear turning (teeth from the size when not given)."""
    teeth = teeth or max(8, round(r / 9))
    with Plate(img, (cx - r * 1.3, cy - r * 1.3, cx + r * 1.3, cy + r * 1.3)) as p:
        draw_gear(p, cx, cy, r, teeth, t * speed * .8, color)
    return {"center": (cx, cy)}

def gear_pair(img, cx, cy, r1=120, r2=70, t=0.0, speed=1.0, angle=0.0, color=WHITE, mark=CYAN):
    """Two meshing gears: the second sits beside the first at 'angle' (radians, 0 = right) and turns the other way,
    faster if it's smaller. A colored tooth on each shows the turns."""
    m = 9; n1, n2 = max(8, round(r1 / m)), max(8, round(r2 / m))
    r2 = r1 * n2 / n1
    d = r1 + r2; cx2, cy2 = cx + d * math.cos(angle), cy + d * math.sin(angle)
    p1, p2 = 2 * math.pi / n1, 2 * math.pi / n2
    a1 = t * speed * .8 + angle - .3 * p1
    a2 = angle + math.pi - .8 * p2 - (a1 - angle + .3 * p1) * n1 / n2
    pad = max(r1, r2) * 1.3
    with Plate(img, (min(cx, cx2) - pad, min(cy, cy2) - pad, max(cx, cx2) + pad, max(cy, cy2) + pad)) as p:
        draw_gear(p, cx, cy, r1, n1, a1, color)
        draw_gear(p, cx2, cy2, r2, n2, a2, color)
    with Plate(img, (min(cx, cx2) - pad, min(cy, cy2) - pad, max(cx, cx2) + pad, max(cy, cy2) + pad), glow=NEON) as p:
        for (gx, gy, r, a, pt) in ((cx, cy, r1, a1, p1), (cx2, cy2, r2, a2, p2)):
            c = a + .3 * pt
            p.circle(gx + (r + 2) * math.cos(c), gy + (r + 2) * math.sin(c), max(4, r * .06), fill=mark)
    return {"centers": [(cx, cy), (cx2, cy2)], "ratio": n1 / n2}

# ---------- engines ----------
def piston_engine(img, cx, cy, s=1.0, t=0.0, speed=1.0, glow=NEON):
    """One cylinder of a car engine cut open: the spark (yellow) and the burn (orange) push the piston down, the rod
    turns the crankshaft; valves open in turn. (cx, cy) = crankshaft center."""
    th = t * speed * 4.0                                              # crank angle
    R, L, pw, ph = 42 * s, 135 * s, 100 * s, 58 * s
    pin = (cx + R * math.sin(th), cy - R * math.cos(th))
    py = pin[1] - math.sqrt(L * L - (R * math.sin(th)) ** 2)        # piston pin height
    head = cy - R - L - ph / 2 - 26 * s                               # inside top of the cylinder
    burn = max(0.0, math.cos(th)) ** 6                                # right after top dead center
    with Plate(img, (cx - pw, head - 70 * s, cx + pw, cy + R * 1.9)) as p:
        p.circle(cx, cy, R * 1.75, fill=PANEL, color=DIM, w=2)            # crankcase
        p.rect(cx - pw / 2 - 18 * s, head - 22 * s, cx + pw / 2 + 18 * s, cy - R * 1.1, fill=STEEL, color=WHITE, w=3)
        p.rect(cx - pw / 2, head, cx + pw / 2, cy - R * 1.1, fill=PANEL)
        if burn > .02: p.rect(cx - pw / 2, head, cx + pw / 2, py - ph / 2, fill=mix(PANEL, ACCENT, .7 * burn))
        p.hatch([(cx - pw / 2 - 18 * s, head - 22 * s), (cx - pw / 2, head - 22 * s), (cx - pw / 2, cy - R * 1.1),
                 (cx - pw / 2 - 18 * s, cy - R * 1.1)], DIM, 10)
        p.hatch([(cx + pw / 2, head - 22 * s), (cx + pw / 2 + 18 * s, head - 22 * s), (cx + pw / 2 + 18 * s, cy - R * 1.1),
                 (cx + pw / 2, cy - R * 1.1)], DIM, 10)
        for k, side in enumerate((-1, 1)):                            # intake and exhaust valves
            phase = (th / (2 * math.pi) + k * .5) % 1
            lift = 10 * s * max(0.0, math.sin(phase * 2 * math.pi)) if phase < .5 else 0
            vx = cx + side * pw * .25
            p.line([(vx, head - 60 * s), (vx, head + lift)], WHITE, 4 * s)
            p.line([(vx - 14 * s, head + lift), (vx + 14 * s, head + lift)], WHITE, 5 * s)
        p.rect(cx - 6 * s, head - 50 * s, cx + 6 * s, head - 20 * s, fill=PANEL, color=WHITE, w=2)   # spark plug
        p.line([(cx, py), pin], GRAY, 14 * s)                          # connecting rod
        p.rect(cx - pw / 2 + 3, py - ph / 2, cx + pw / 2 - 3, py + ph / 2, fill=STEEL, color=WHITE, w=3)
        for k in (1, 2): p.line([(cx - pw / 2 + 3, py - ph / 2 + k * 9 * s), (cx + pw / 2 - 3, py - ph / 2 + k * 9 * s)], DIM, 2)
        cw = [(cx - R * 1.2 * math.sin(th + a), cy + R * 1.2 * math.cos(th + a)) for a in (-.9, -.45, 0, .45, .9)]
        p.poly([(cx, cy)] + cw, fill=STEEL, color=WHITE, w=3)         # counterweight
        p.line([(cx, cy), pin], WHITE, 18 * s)
        p.circle(cx, cy, 12 * s, fill=PANEL, color=WHITE, w=3); p.circle(*pin, 9 * s, fill=PANEL, color=WHITE, w=3)
        p.circle(cx, py, 7 * s, fill=PANEL, color=WHITE, w=2)
    if burn > .3:
        with Plate(img, (cx - 40 * s, head - 30 * s, cx + 40 * s, head + 30 * s), glow=glow) as p:
            for k in range(5):
                a = k * 1.256 + t * 7
                p.line([(cx, head - 2 * s), (cx + 22 * s * burn * math.cos(a), head + 10 * s + 14 * s * burn * math.sin(a))], VOLT, 3)
    with Plate(img, (cx - R * 2, cy - R * 2, cx + R * 2, cy + R * 2), glow=glow) as p:
        a = -th - math.pi / 2
        pts = [(cx + R * 1.55 * math.cos(a - k * .12), cy + R * 1.55 * math.sin(a - k * .12)) for k in range(10)]
        p.line(pts, CYAN, 3)
    return {"crank": (cx, cy), "piston": (cx, py), "head": (cx, head), "burn": burn}

def electric_motor(img, cx, cy, r=180, t=0.0, speed=1.0, glow=NEON):
    """Electric motor seen from the front: copper coils around the outside switch on in turn (yellow) and pull the
    magnets of the rotor (pink and cyan), which spins."""
    a = t * speed * 2.2; active = int((a % (2 * math.pi)) / (math.pi / 3)) % 6
    with Plate(img, (cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10)) as p:
        p.circle(cx, cy, r, fill=STEEL, color=WHITE, w=4)
        p.circle(cx, cy, r * .72, fill=PANEL, color=GRAY, w=2)
        for k in range(6):
            b = k * math.pi / 3; ca, sa = math.cos(b), math.sin(b)
            def at(rad, off): return (cx + rad * ca - off * sa, cy + rad * sa + off * ca)
            p.poly([at(r * .92, -r * .16), at(r * .92, r * .16), at(r * .72, r * .12), at(r * .72, -r * .12)],
                   fill=COPPER, color=WHITE, w=2)
            for j in range(1, 4):
                rad = r * (.72 + .05 * j)
                p.line([at(rad, -r * .13), at(rad, r * .13)], mix(COPPER, PANEL, .4), 2)
    with Plate(img, (cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10), glow=glow) as p:
        for k in (active, (active + 3) % 6):
            b = k * math.pi / 3; ca, sa = math.cos(b), math.sin(b)
            def at(rad, off): return (cx + rad * ca - off * sa, cy + rad * sa + off * ca)
            p.line([at(r * .92, -r * .16), at(r * .92, r * .16), at(r * .72, r * .12), at(r * .72, -r * .12),
                    at(r * .92, -r * .16)], VOLT, 4)
        for k in range(4):                                            # rotor magnets
            b0 = a + k * math.pi / 2
            pts = [(cx, cy)] + [(cx + r * .6 * math.cos(b0 + u * math.pi / 2), cy + r * .6 * math.sin(b0 + u * math.pi / 2))
                                for u in [i / 10 for i in range(11)]]
            p.poly(pts, fill=mix(PANEL, MAGENTA if k % 2 else CYAN, .55), color=MAGENTA if k % 2 else CYAN, w=2)
        p.circle(cx, cy, r * .12, fill=PANEL, color=WHITE, w=3)
    return {"center": (cx, cy), "active": active}

def jet_engine(img, x0, cy, length=700, r=150, t=0.0, speed=1.0, glow=NEON):
    """Jet engine cut open, air in on the left: fan, compressor, burner and turbine; cold air in cyan, hot gas out in
    orange."""
    x1 = x0 + length; spin = t * speed * 9
    def shell(x):
        u = (x - x0) / length
        return r * (1.0 - .1 * u - .25 * max(0, u - .75) / .25)
    core_r = lambda x: r * (.18 + .22 * math.sin(math.pi * min(1, max(0, (x - x0) / length * 1.15))))
    xs = [x0 + length * k / 40 for k in range(41)]
    with Plate(img, (x0 - 10, cy - r - 30, x1 + 10, cy + r + 30)) as p:
        top = [(x, cy - shell(x)) for x in xs]; bot = [(x, cy + shell(x)) for x in xs][::-1]
        p.poly([(x0, cy - r - 18)] + top + [(x1, cy - shell(x1) - 18)] + [(x1, cy - shell(x1))] +
               [(x1, cy + shell(x1))] + [(x1, cy + shell(x1) + 18)] + bot + [(x0, cy + r + 18)], fill=None)
        p.line([(x0, cy - r - 18)] + [(x, y - 18) for x, y in top], WHITE, 3); p.line(top, GRAY, 2)
        p.line([(x0, cy + r + 18)] + [(x, y + 18) for x, y in bot[::-1]], WHITE, 3); p.line(bot, GRAY, 2)
        core = [(x, cy - core_r(x)) for x in xs] + [(x, cy + core_r(x)) for x in xs][::-1]
        p.poly(core, fill=STEEL, color=WHITE, w=3)
        p.poly([(x0 - 4, cy), (x0 + 40, cy - r * .22), (x0 + 40, cy + r * .22)], fill=STEEL, color=WHITE, w=3)   # spinner
        bx0, bx1 = x0 + length * .5, x0 + length * .66                   # burner
        p.rect(bx0, cy - shell(bx0) * .8, bx1, cy - core_r(bx0) - 6, fill=mix(PANEL, ACCENT, .25), color=ACCENT, w=2)
        p.rect(bx0, cy + core_r(bx0) + 6, bx1, cy + shell(bx0) * .8, fill=mix(PANEL, ACCENT, .25), color=ACCENT, w=2)
        stages = [(x0 + 60, 1.0)] + [(x0 + length * (.2 + .055 * k), .85) for k in range(5)] + \
                 [(x0 + length * (.72 + .06 * k), .9) for k in range(3)]
        for i, (sx, f) in enumerate(stages):                          # blade rows: their tips wobble as they spin
            for side in (-1, 1):
                rr = shell(sx) * f - 4
                wob = 6 * math.sin(spin + i * 1.3) * (1 if i else 2)
                p.line([(sx, cy + side * core_r(sx)), (sx + wob, cy + side * rr)], WHITE if i == 0 else GRAY, 5 if i == 0 else 3)
    with Plate(img, (x0 - 60, cy - r - 30, x1 + 160, cy + r + 30), glow=glow) as p:
        for k, f in enumerate((.55, .8)):
            for side in (-1, 1):
                y = cy + side * r * f
                p.dashed([(x0 - 50, y), (x0 + length * .45, cy + side * (core_r(x0 + length * .45) + 20))], CYAN, 3, 20, 18,
                         phase=-t * 160 - k * 9)
        flame = .6 + .4 * math.sin(t * 13)
        for side in (-1, 1):
            p.line([(x0 + length * .53, cy + side * core_r(x0 + length * .55) * 1.6),
                    (x0 + length * .64, cy + side * core_r(x0 + length * .6) * (1.6 + .3 * flame))], VOLT, 4)
        for k in range(3):
            y = cy + (k - 1) * shell(x1) * .5
            p.dashed([(x0 + length * .8, y), (x1 + 150, y + (k - 1) * 20)], mix(ACCENT, RISK, .3), 4, 26, 16, phase=-t * 260 - k * 7)
    return {"intake": (x0, cy), "burner": (x0 + length * .58, cy - r * .55), "exhaust": (x1, cy)}

def wind_turbine(img, x, base, h=520, t=0.0, speed=1.0, wind=True, glow=NEON):
    """Wind turbine: tapered tower, nacelle and three turning blades; a yellow pulse goes down the tower (power out)
    and, with wind, lines of air come in from the left."""
    hub = (x, base - h); L = h * .52; a = t * speed * 1.4
    with Plate(img, (x - L - 10, base - h - L - 10, x + L + 10, base + 4)) as p:
        p.poly([(x - h * .035, base), (x - h * .014, hub[1] + 20), (x + h * .014, hub[1] + 20), (x + h * .035, base)],
               fill=PANEL, color=WHITE, w=3)
        p.rect(x - 16, hub[1] - 18, x + 56, hub[1] + 18, fill=STEEL, color=WHITE, w=3)
        for k in range(3):
            b = a + k * 2 * math.pi / 3; ca, sa = math.cos(b), math.sin(b)
            def at(rad, off): return (hub[0] + rad * ca - off * sa, hub[1] + rad * sa + off * ca)
            p.poly([at(10, -8), at(L * .25, -h * .03), at(L, -3), at(L, 2), at(L * .25, h * .012), at(10, 8)],
                   fill=PANEL, color=WHITE, w=3)
        p.circle(*hub, 14, fill=STEEL, color=WHITE, w=3)
    with Plate(img, (x - L - 200, base - h - L - 10, x + L + 10, base + 4), glow=glow) as p:
        p.dashed([(x, hub[1] + 30), (x, base - 4)], VOLT, 3, 10, 40, phase=-t * 140)
        if wind:
            for k in range(4):
                y = hub[1] - L * .6 + k * L * .4
                p.dashed([(x - L - 190, y), (x - 40, y)], LIME, 2, 40, 60, phase=-t * 120 - k * 30)
    return {"hub": hub, "top": hub[1] - L}
