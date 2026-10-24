"""Example spec in the blueprint style (technical infographic on a dark screen). Try it with:
  python3 -m channel.produce specs/s05_blueprint.py preview 1 4 7 10
  python3 -m channel.produce specs/s05_blueprint.py check"""
from reels_engine.core import *
from reels_engine.motion import tw
from reels_engine.blueprint import blueprint_bg, kicker, headline, big_number, callout, plan_stamp, ACCENT
from reels_engine.blueprint.section import cross_section

NAME = "s05_blueprint"
LINES = [
    ("curious", "This city sinks up to fifteen centimeters every year.", "It sinks *15 cm* a year"),
    ("calm", "Under the streets there is soft clay full of water.", "Under it: *soft clay* full of water"),
    ("serious", "When the wells pump that water out, the clay shrinks and the ground goes down with it.",
     "Pump the water out… and the ground *goes down*"),
]
CAPTION_STYLE = "static"
LAYERS = [("fill", 30, "FILL"), ("wet_clay", 190, "SOFT CLAY"), ("gravel", 110, "GRAVEL"), ("rock", 0)]
BOX = (40, 790, 1040, 1320)

def titles(img, c, sink_cm):
    kicker(img, "GROUND MECHANICS", 60, 236)
    plan_stamp(img, [("sheet", f"0{c.line + 1}/03"), ("scale", "1:500")], 1020, 160)
    headline(img, "THE CITY\nTHAT *SINKS*", 60, 286, size=96, appear=tw(c.v, 0, 1.4, 0, 1))
    big_number(img, sink_cm, 60, 530, size=160, unit="cm a year · highest measured")

def hook(c):
    img, d = canvas(blueprint_bg(c.t))
    titles(img, c, tw(c.lt, .6, 2.2, 0, 15))
    cross_section(img, BOX, LAYERS, water=40, t=c.t,
                  xray=(tw(c.lt, .3, 2.6, 180, 760), 1130, 150), xray_label="x-ray")      # what you don't see
    return img

def clay(c):
    img, d = canvas(blueprint_bg(c.t))
    titles(img, c, 15)
    a = cross_section(img, BOX, LAYERS, water=40, ruler=(4, 10), t=c.t)
    (top, bot) = a["layers"][1]
    if c.lt > .4: callout(img, "water in the pores", 300, (top + bot) / 2 + 30, 420, top + 80, size=26)
    return img

def pumping(c):
    img, d = canvas(blueprint_bg(c.t))
    titles(img, c, 15)
    k = tw(c.lt, .5, 4, 0, 1)
    a = cross_section(img, BOX, LAYERS, water=40 + 120 * k, sink=60 * k, ruler=(4, 10), t=c.t)
    if k > .3: callout(img, "ground level now", 525, a["surface"], 600, 752, size=26, dot=ACCENT)
    return img

SCENES = [(0, hook), (1, clay), (2, pumping)]
SFX = [(0, .6, "pop")]
MUSIC = ("pad", [], None)
