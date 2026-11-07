"""Example spec with the sketch coffee shop pieces. Try it with:
  python3 -m channel.produce specs/s07_cafe.py preview 1 4 7
  python3 -m channel.produce specs/s07_cafe.py check"""
from reels_engine.core import *
from reels_engine.motion import tw, back_out
from channel.backgrounds import cafe_bg
from channel.characters import doodle, doodle_marks, doodle_barista
from channel.props import cafe_counter, takeaway_cup, cup_meter, cup_grid, espresso_machine

NAME = "s07_cafe"
LINES = [
    ("calm", "Same coffee, same cup. In twenty fifteen it cost two dollars.", "Same coffee: *$2* in 2015"),
    ("excited", "Today it costs three fifty. That's inflation.", "Today: *$3.50*. That's *inflation*"),
    ("calm", "With the same money you now get fewer cups.", "Same money, *fewer* cups"),
]
PAPER = ((252, 252, 250), (244, 244, 242))

def boil(c): return int(c.t * 6)

def then(c):
    img = cafe_bg()
    doodle_barista(img, 820, FLOOR - 110, 1.0, arms=("down", "offer"), held=None, look=-.4, seed=boil(c))
    cafe_counter(img, 540, FLOOR, 1000)                  # in front of the barista: hides the legs
    espresso_machine(img, 250, FLOOR - 300, 320, pressure=.3)
    takeaway_cup(img, 560, FLOOR - 300, "M", label="$2", steam=True, seed=boil(c))
    return img

def now(c):
    img = cafe_bg()
    a = doodle(img, 820, FLOOR - 110, 1.0, outfit="hoodie", mood="shocked" if c.lt > .8 else "smile",
               arms=("up", "up") if c.lt > .8 else "down", look=-.4, seed=boil(c))
    if c.lt > .8: doodle_marks(img, a["head"], a["head_r"], "excited", seed=boil(c))
    cafe_counter(img, 540, FLOOR, 1000)
    espresso_machine(img, 250, FLOOR - 300, 320, pressure=tw(c.lt, .2, 1.2, .3, .95))
    takeaway_cup(img, 560, FLOOR - 300, "M", label="$3.50" if c.lt > .8 else "$2", steam=True, seed=boil(c))
    return img

def fewer(c):
    img, d = canvas(PAPER)
    cup_meter(img, 290, 980, 380, fill=1.0, label="2015")
    cup_meter(img, 790, 980, 380, fill=tw(c.lt, .2, 1.4, 1.0, .57, back_out), label="TODAY")
    cup_grid(img, 120, 1080, 5, 2, 120, filled=round(tw(c.lt, .2, 1.4, 10, 6)))
    return img

SCENES = [(0, then), (1, now), (2, fewer)]
SFX = [(1, .8, "pop"), (2, 1.4, "ding")]
MUSIC = ("pad", [], None)
