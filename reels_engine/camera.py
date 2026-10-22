"""Camera: films a "world" image (a scene bigger than the screen, an illustration, or the frame itself) with
pans, zoom in/out, tilt, shake and whip pans. Moves are smooth (sub-pixel) and return a View that maps world
points to the screen, so bubbles and labels stay on the right spot.

    world = draw_world(c.t)                                   # any PIL image, any size
    shot = path(c.lt, [(0, wide(world)), (1.5, Shot(1336, 410, 2.2))])   # glide from the whole scene to a face
    view = film(img, world, shot)                             # paints the view on img (full screen or dst box)
    say(ImageDraw.Draw(img), "Hi!", view.to_screen((1336, 440)), 108 * view.scale)

A Shot is where the camera looks: world point (x, y), zoom (1 = the biggest view that fits inside the world) and
angle (degrees, tilt). Helpers return a Shot for time t: path, pan, zoom_in, zoom_out, ken_burns, whip, plus
handheld and impact to add shake on top of any of them."""
import math
from dataclasses import dataclass, replace
import numpy as np
from PIL import Image
from .core import W, H
from .motion import tw, sine_in_out, cubic_out, shake

@dataclass(frozen=True)
class Shot:
    x: float                      # world point at the center of the view
    y: float
    zoom: float = 1.0             # 1 = biggest view that fits inside the world; 2 = twice as close
    angle: float = 0.0            # tilt in degrees (dutch angle)
    streak: tuple = (0.0, 0.0)    # motion blur (px on screen) along a direction, used by whip

def wide(world, zoom=1.0):
    """Shot of the whole world (centered)."""
    w, h = world if isinstance(world, tuple) else world.size
    return Shot(w / 2, h / 2, zoom)

def mix(a, b, u):
    """Shot between a (u=0) and b (u=1). Zoom changes geometrically so it feels even."""
    za, zb = max(a.zoom, 1e-3), max(b.zoom, 1e-3)
    return Shot(a.x + (b.x - a.x) * u, a.y + (b.y - a.y) * u, za * (zb / za) ** u, a.angle + (b.angle - a.angle) * u)

def path(t, keys, ease=sine_in_out):
    """Camera path through keyframes [(time, Shot) or (time, Shot, ease), ...] (times ascending).
    Holds the first shot before the first key and the last one after the last key."""
    if t <= keys[0][0]: return keys[0][1]
    for k0, k1 in zip(keys, keys[1:]):
        if t < k1[0]:
            e = k1[2] if len(k1) > 2 else ease
            return mix(k0[1], k1[1], tw(t, k0[0], k1[0] - k0[0], 0, 1, e))
    return keys[-1][1]

def pan(t, t0, dur, a, b, ease=sine_in_out):
    """Pan (and/or zoom) from shot a to shot b between t0 and t0+dur."""
    return path(t, [(t0, a), (t0 + dur, b, ease)])

def zoom_in(t, t0, dur, at, z0=1.0, z1=2.0, ease=cubic_out, start=None):
    """Zoom in toward world point at=(x, y). start = Shot to begin from (default: zoom z0 centered on at)."""
    a = start or Shot(at[0], at[1], z0)
    return pan(t, t0, dur, a, Shot(at[0], at[1], z1), ease)

def zoom_out(t, t0, dur, at, z0=2.0, z1=1.0, ease=cubic_out, end=None):
    """Zoom out from world point at=(x, y). end = Shot to finish on (default: zoom z1 centered on at)."""
    return pan(t, t0, dur, Shot(at[0], at[1], z0), end or Shot(at[0], at[1], z1), ease)

def ken_burns(t, dur, a, b):
    """Slow, steady pan + zoom across the whole scene (documentary style): from a to b over dur seconds."""
    return pan(t, 0, dur, a, b, lambda u: u)

def _snap(u):
    """Exponential in-out: almost still at both ends, very fast in the middle."""
    if u <= 0 or u >= 1: return max(0.0, min(1.0, u))
    return 2 ** (20 * u - 10) / 2 if u < .5 else (2 - 2 ** (-20 * u + 10)) / 2

def whip(t, t0, dur, a, b, blur=60):
    """Whip pan: very fast move from a to b with motion blur in the middle."""
    s = pan(t, t0, dur, a, b, _snap)
    u = 0 if dur <= 0 else max(0.0, min(1.0, (t - t0) / dur))
    k = math.sin(math.pi * u) * blur                                    # strongest blur halfway
    dx, dy = b.x - a.x, b.y - a.y; L = math.hypot(dx, dy) or 1
    return replace(s, streak=(dx / L * k, dy / L * k))

def handheld(shot, t, amp=6.0, seed=1):
    """Adds a gentle hand-held wobble (amp in world px, a little tilt too). Deterministic: depends only on t."""
    p = [seed * 1.7 + k * 2.3 for k in range(3)]
    nx = math.sin(t * 1.3 + p[0]) * .6 + math.sin(t * 2.9 + p[1]) * .4
    ny = math.sin(t * 1.1 + p[1]) * .6 + math.sin(t * 3.3 + p[2]) * .4
    return replace(shot, x=shot.x + nx * amp, y=shot.y + ny * amp, angle=shot.angle + math.sin(t * .9 + p[2]) * amp * .05)

def impact(shot, t, t0, dur=.4, amp=18):
    """Shake for a hit or a scare between t0 and t0+dur (amp in world px)."""
    return replace(shot, x=shot.x + shake(t, t0, dur, amp, 47), y=shot.y + shake(t, t0, dur, amp * .6, 61))

class View:
    """What the camera sees: world box and scale. to_screen / to_world convert points."""
    def __init__(self, world_size, shot, dst, clamp=True):
        ww, wh = world_size; X0, Y0, X1, Y1 = dst; dw, dh = X1 - X0, Y1 - Y0
        base = min(ww / dw, wh / dh)                                    # world px per screen px at zoom 1
        self.scale = max(shot.zoom, 1e-3) / base                        # screen px per world px
        vw, vh = dw / self.scale, dh / self.scale
        x, y = shot.x, shot.y
        if clamp and not shot.angle:                                    # keep the view inside the world (no empty edges)
            x = min(max(x, vw / 2), ww - vw / 2) if vw <= ww else ww / 2
            y = min(max(y, vh / 2), wh - vh / 2) if vh <= wh else wh / 2
        self.cx, self.cy, self.angle, self.dst = x, y, math.radians(shot.angle), dst
        self.box = (x - vw / 2, y - vh / 2, x + vw / 2, y + vh / 2)
    def to_screen(self, p):
        """World point -> screen point."""
        dx, dy = p[0] - self.cx, p[1] - self.cy; c, s = math.cos(self.angle), math.sin(self.angle)
        X0, Y0, X1, Y1 = self.dst
        return ((X0 + X1) / 2 - .5 + (dx * c + dy * s) * self.scale, (Y0 + Y1) / 2 - .5 + (-dx * s + dy * c) * self.scale)
    def to_world(self, p):
        """Screen point -> world point."""
        X0, Y0, X1, Y1 = self.dst
        u, v = (p[0] + .5 - (X0 + X1) / 2) / self.scale, (p[1] + .5 - (Y0 + Y1) / 2) / self.scale
        c, s = math.cos(self.angle), math.sin(self.angle)
        return (self.cx + u * c - v * s, self.cy + u * s + v * c)

def _streak(im, dx, dy, n=9):
    """Directional motion blur: average of copies shifted along (dx, dy)."""
    a = np.asarray(im).astype(np.float32); acc = np.zeros_like(a)
    for k in range(n):
        f = k / (n - 1) - .5
        acc += np.roll(a, (int(round(dy * f)), int(round(dx * f))), axis=(0, 1))
    return Image.fromarray((acc / n).astype(np.uint8))

def film(img, world, shot, dst=None, clamp=True, fill=(0, 0, 0)):
    """Paints what the camera sees of 'world' (PIL image) on img, inside dst=(x0, y0, x1, y1) (default: whole screen).
    clamp keeps the view inside the world (ignored when tilted). Returns the View (to_screen, scale, box)."""
    dst = dst or (0, 0, W, H)
    X0, Y0, X1, Y1 = [int(round(v)) for v in dst]; dw, dh = X1 - X0, Y1 - Y0
    view = View(world.size, shot, (X0, Y0, X1, Y1), clamp)
    src, k = world.convert("RGB"), 1
    if view.scale < .5:                                                 # shrinking a lot: pre-reduce to avoid aliasing
        k = int(1 / view.scale); src = src.reduce(k)
    c, s = math.cos(view.angle), math.sin(view.angle); inv = 1 / (view.scale * k)
    # output pixel (u, v) -> source pixel: world = center + R(angle) * ((u, v) - dst center) / scale
    # (points use Pillow's convention: pixel i has its center at i + .5; this keeps zooms free of half-pixel drift)
    ox, oy = dw / 2, dh / 2
    a, b, d, e = c * inv, -s * inv, s * inv, c * inv
    cx, cy = (view.cx + .5) / k, (view.cy + .5) / k
    data = (a, b, cx - a * ox - b * oy, d, e, cy - d * ox - e * oy)
    out = src.transform((dw, dh), Image.AFFINE, data, resample=Image.BICUBIC, fillcolor=fill)
    if any(abs(v) >= 1 for v in shot.streak): out = _streak(out, *shot.streak)
    img.paste(out, (X0, Y0))
    return view
