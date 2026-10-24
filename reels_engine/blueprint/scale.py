"""Scale silhouettes of the blueprint style, drawn at their real proportions so sizes can be compared honestly:
a person, a car, a bus, an airliner, the Eiffel Tower, and a soccer field and an Olympic pool seen from above.

Every one takes (img, x, base, m): x = left side, base = the ground (bottom of the drawing) and m = pixels per meter.
They return their size in px. SIZES has the real size (width, height in meters) of each one.

    m = 300 / 12                                        # a 12 m bus 300 px long
    scale_bus(img, 100, 1200, m); scale_person(img, 420, 1200, m)
"""
from . import Plate, mix, WHITE, CYAN, GRAY, DIM, PANEL

FILL = mix(PANEL, GRAY, .12)
SIZES = {                                   # (width, height) in meters
    "person": (.5, 1.75), "car": (4.5, 1.5), "bus": (12.0, 3.2), "plane": (37.6, 11.8),
    "eiffel": (125.0, 330.0), "field": (105.0, 68.0), "pool": (50.0, 25.0),
}

LABELS = {"person": "PERSONA", "car": "COCHE", "bus": "AUTOBÚS", "plane": "AVIÓN", "eiffel": "TORRE EIFFEL",
          "field": "CAMPO DE FÚTBOL", "pool": "PISCINA OLÍMPICA"}  # default names on screen (pass your own)

def _w(m, k=1.0): return max(2, min(4, m * .5 * k))

def scale_person(img, x, base, m, color=WHITE, fill=FILL):
    """Person 1.75 m tall seen from the front."""
    h = 1.75 * m; w = .5 * m; cx = x + w / 2; lw = _w(m, .4)
    with Plate(img, (x - 4, base - h - 4, x + w + 4, base + 4)) as p:
        p.circle(cx, base - h + .12 * m, .12 * m, fill=fill, color=color, w=lw)
        p.poly([(cx - .22 * m, base - h + .27 * m), (cx + .22 * m, base - h + .27 * m), (cx + .2 * m, base - .8 * m),
                (cx + .12 * m, base), (cx - .12 * m, base), (cx - .2 * m, base - .8 * m)], fill=fill, color=color, w=lw)
    return w, h

def scale_car(img, x, base, m, color=WHITE, fill=FILL):
    """Car 4.5 m long and 1.5 m tall seen from the side."""
    L, h = 4.5 * m, 1.5 * m; r = .33 * m; lw = _w(m, .3)
    with Plate(img, (x - 4, base - h - 4, x + L + 4, base + 4)) as p:
        p.poly([(x, base - r), (x, base - .85 * m), (x + .9 * m, base - .95 * m), (x + 1.4 * m, base - h), (x + 3.1 * m, base - h),
                (x + 3.7 * m, base - .95 * m), (x + L, base - .85 * m), (x + L, base - r)], fill=fill, color=color, w=lw)
        for wx in (x + .95 * m, x + 3.55 * m): p.circle(wx, base - r, r, fill=PANEL, color=color, w=lw)
    return L, h

def scale_bus(img, x, base, m, color=WHITE, fill=FILL):
    """City bus 12 m long and 3.2 m tall seen from the side."""
    L, h = 12 * m, 3.2 * m; r = .5 * m; lw = _w(m, .25)
    with Plate(img, (x - 4, base - h - 4, x + L + 4, base + 4)) as p:
        p.rect(x, base - h, x + L, base - r, fill=fill, color=color, w=lw)
        for i in range(6):
            wx = x + .8 * m + i * 1.75 * m
            p.rect(wx, base - h + .5 * m, wx + 1.4 * m, base - h + 1.5 * m, fill=PANEL, color=DIM, w=max(1, lw * .6))
        for wx in (x + 2.3 * m, x + 9.4 * m): p.circle(wx, base - r, r, fill=PANEL, color=color, w=lw)
    return L, h

def scale_plane(img, x, base, m, color=WHITE, fill=FILL):
    """Airliner about 37.6 m long and 11.8 m tall to the tail, seen from the side, nose to the right."""
    L, h = 37.6 * m, 11.8 * m; lw = _w(m, .1)
    b = base - 1.2 * m; fh = 4 * m                                  # fuselage bottom and height
    with Plate(img, (x - 4, base - h - 4, x + L + 4, base + 4)) as p:
        body = [(x + 1 * m, b - fh * .55), (x + 6 * m, b - fh), (x + L - 4 * m, b - fh), (x + L, b - fh * .45),
                (x + L - 1.5 * m, b), (x + 7 * m, b)]
        tail = [(x + 1.5 * m, b - fh * .6), (x, base - h), (x + 3 * m, base - h), (x + 8 * m, b - fh)]
        p.poly(tail, fill=fill, color=color, w=lw); p.poly(body, fill=fill, color=color, w=lw)
        p.poly([(x + 14 * m, b - fh * .35), (x + 22 * m, b - fh * .35), (x + 16 * m, b + .8 * m)], fill=mix(fill, WHITE, .15), color=color, w=lw)
        for gx in (x + 15 * m, x + L - 5 * m):
            p.line([(gx, b), (gx, base - .4 * m)], color, lw); p.circle(gx, base - .4 * m, .4 * m, fill=PANEL, color=color, w=lw)
    return L, h

def scale_eiffel(img, x, base, m, color=WHITE, fill=None):
    """Eiffel Tower, 330 m tall to the antenna and 125 m wide at the base, drawn in outline."""
    H_, B = 330 * m, 125 * m; cx = x + B / 2; lw = _w(m, 4)
    lvl = [(0, B / 2), (57, B * .33), (116, B * .17), (276, B * .05), (300, B * .02)]
    with Plate(img, (x - 4, base - H_ - 4, x + B + 4, base + 4)) as p:
        left = [(cx - hw, base - y * m) for y, hw in lvl] + [(cx, base - H_)]
        right = [(cx + hw, base - y * m) for y, hw in lvl][::-1]
        p.line(left + right, color, lw)
        p.line([(cx - B * .26, base), (cx, base - 40 * m), (cx + B * .26, base)], color, lw)   # the big arch
        for y, hw in lvl[1:3]: p.line([(cx - hw - 4 * m, base - y * m), (cx + hw + 4 * m, base - y * m)], color, lw * 1.5)
        for i in range(8):                                                    # lattice
            y0, y1 = 57 + i * 28, 57 + (i + 1) * 28
            if y1 > 276: break
            hw0 = B * .33 - (B * .28) * (y0 - 57) / 219; hw1 = B * .33 - (B * .28) * (y1 - 57) / 219
            p.line([(cx - hw0, base - y0 * m), (cx + hw1, base - y1 * m)], DIM, max(1, lw * .5))
            p.line([(cx + hw0, base - y0 * m), (cx - hw1, base - y1 * m)], DIM, max(1, lw * .5))
    return B, H_

def scale_field(img, x, base, m, color=WHITE, fill=None):
    """Soccer field seen from above, 105 x 68 m, with its markings."""
    L, Wd = 105 * m, 68 * m; top = base - Wd; lw = _w(m, 3)
    with Plate(img, (x - 4, top - 4, x + L + 4, base + 4)) as p:
        p.rect(x, top, x + L, base, fill=fill if fill is not None else mix(PANEL, (60, 160, 90), .25), color=color, w=lw)
        p.line([(x + L / 2, top), (x + L / 2, base)], color, lw)
        p.circle(x + L / 2, top + Wd / 2, 9.15 * m, color=color, w=lw)
        for sx, d in ((x, 1), (x + L, -1)):
            p.rect(min(sx, sx + d * 16.5 * m), top + Wd / 2 - 20.15 * m, max(sx, sx + d * 16.5 * m), top + Wd / 2 + 20.15 * m, color=color, w=lw)
    return L, Wd

def scale_pool(img, x, base, m, color=WHITE, fill=None):
    """Olympic pool seen from above, 50 x 25 m, with its 10 lanes."""
    L, Wd = 50 * m, 25 * m; top = base - Wd; lw = _w(m, 3)
    with Plate(img, (x - 4, top - 4, x + L + 4, base + 4)) as p:
        p.rect(x, top, x + L, base, fill=fill if fill is not None else mix(PANEL, CYAN, .25), color=color, w=lw)
        for i in range(1, 10): p.dashed([(x + 2 * m, top + i * 2.5 * m), (x + L - 2 * m, top + i * 2.5 * m)], mix(CYAN, WHITE, .4), max(1, lw * .6), 2 * m, m)
    return L, Wd

DRAW = {"person": scale_person, "car": scale_car, "bus": scale_bus, "plane": scale_plane, "eiffel": scale_eiffel,
        "field": scale_field, "pool": scale_pool}

def silhouette(img, kind, x, base, m, **kw):
    """Any scale silhouette by name (person, car, bus, plane, eiffel, field, pool)."""
    return DRAW[kind](img, x, base, m, **kw)
