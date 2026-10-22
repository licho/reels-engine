"""Example spec: camera moves over a scene bigger than the screen. Try it with:
  python3 -m channel.produce specs/s03_camera.py sheet
  python3 -m channel.produce specs/s03_camera.py silent"""
from reels_engine.core import *
from reels_engine.camera import Shot, film, path, pan, zoom_in, zoom_out, ken_burns, whip, handheld, impact
from channel.characters import buddy
from channel.props import campfire, house, tree, clouds, sun_simple

NAME = "s03_camera"
LINES = [
    ("calm", "A wide shot shows the whole place.", "*Wide shot*: the whole place"),
    ("calm", "A pan moves across the scene.", "A *pan* moves across the scene"),
    ("excited", "Zoom in to see who is talking.", "*Zoom in* to the one talking"),
    ("excited", "Zoom out to reveal everything else.", "*Zoom out* to reveal the rest"),
    ("excited", "And a whip pan jumps to the action!", "A *whip pan* jumps to the action!"),
]
WORLD = (3000, 2400)
FACE = (1750, 1290)            # head of the sitting buddy (see world())
FIRE = (2250, 1850)

def world(t):
    """The whole scene, drawn bigger than the screen. Returns (image, anchors of the sitting buddy)."""
    img, d = canvas(((150, 200, 240), (250, 225, 190)))
    img = img.resize(WORLD); d = ImageDraw.Draw(img)
    d.rectangle([0, 1500, WORLD[0], WORLD[1]], fill=(120, 170, 90))
    sun_simple(d, 2500, 450, 140, t=t)
    clouds(d, 700 + 20 * t, 450, 1.6); clouds(d, 1900 + 12 * t, 300, 1.2)
    house(d, 600, 1750, 1.6)
    tree(d, 1250, 1760, 1.5, t=t)
    campfire(img, *FIRE, 1.3, t=t)
    a = buddy(img, 1750, 1900, 1.5, pose="sitting", mood="happy", hair="bangs", shirt=(80, 150, 220), t=t)
    buddy(img, 2700, 1950, 1.4, arms="wave", mood="laugh", hair="short", shirt=(230, 120, 60), t=t)
    return img, a

def shot1(c):                                   # wide shot with a gentle hand-held wobble
    w, a = world(c.t); img = Image.new("RGB", (W, H))
    film(img, w, handheld(ken_burns(c.lt, c.dur, Shot(1400, 1300, 1.0), Shot(1700, 1350, 1.12)), c.t, 8))
    d = ImageDraw.Draw(img); chip(d, "WIDE SHOT", CHIP1, appear=c.lt / .4)
    return img

def shot2(c):                                   # pan from the house to the campfire
    w, a = world(c.t); img = Image.new("RGB", (W, H))
    film(img, w, pan(c.lt, .2, c.dur - .4, Shot(500, 1500, 1.3), Shot(2500, 1500, 1.3)))
    chip(ImageDraw.Draw(img), "PAN", CHIP1)
    return img

def shot3(c):                                   # zoom in to the face, then the bubble follows the camera
    w, a = world(c.t); img = Image.new("RGB", (W, H))
    v = film(img, w, zoom_in(c.lt, 0, 1.2, (FACE[0] + 60, FACE[1] + 150), 1.0, 2.6, start=Shot(2000, 1500, 1.0)))
    d = ImageDraw.Draw(img); chip(d, "ZOOM IN", CHIP1)
    if c.lt > 1.2: say(d, "Hi there!", v.to_screen(a["mouth"]), a["head_r"] * v.scale)
    return img

def shot4(c):                                   # zoom out with a small tilt that straightens
    w, a = world(c.t); img = Image.new("RGB", (W, H))
    s = path(c.lt, [(0, Shot(1750, 1400, 2.6, -8)), (1.6, Shot(1500, 1300, .95, 0))])
    film(img, w, s, fill=(150, 200, 240))
    chip(ImageDraw.Draw(img), "ZOOM OUT", CHIP1)
    return img

def shot5(c):                                   # whip pan to the fire, then a hit of shake
    w, a = world(c.t); img = Image.new("RGB", (W, H))
    s = whip(c.lt, .3, .5, Shot(600, 1500, 1.4), Shot(FIRE[0], FIRE[1] - 250, 1.9))
    film(img, w, impact(s, c.lt, .8, .5, 30))
    chip(ImageDraw.Draw(img), "WHIP PAN", CHIP1, appear=(c.lt - .8) / .3)
    return img

SCENES = [(0, shot1), (1, shot2), (2, shot3), (3, shot4), (4, shot5)]
SFX = [(2, 1.2, "pop"), (4, .55, "thud")]
MUSIC = ("pad", [], None)
