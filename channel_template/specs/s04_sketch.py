"""Example spec in the sketch style (hand-drawn marker look). Try it with:
  python3 -m channel.produce specs/s04_sketch.py preview 1 4 7
  python3 -m channel.produce specs/s04_sketch.py check"""
from reels_engine.core import *
from reels_engine.motion import tw, back_out
from channel.characters import doodle, doodle_marks
from channel.props import (bill, money_jar, money_pile, money_text, wallet, block_arrow, curve_arrow, hatched_chart,
                           wall_calendar, dashed_line)

NAME = "s04_sketch"
LINES = [
    ("excited", "Ten dollars a day becomes three thousand six hundred and fifty in a year.", "$10 a day = *$3,650* a year"),
    ("calm", "One spends them, the other saves them.", "One *spends*, the other *saves*"),
    ("excited", "In five years the difference is huge.", "In 5 years: *huge* difference"),
]
PAPER = ((252, 252, 250), (244, 244, 242))

def boil(c): return int(c.t * 6)                # new wobble 6 times a second: lines "breathe" like drawn by hand

def year(c):
    img, d = canvas(PAPER)
    wall_calendar(img, 60, 470, 140, label="1 YEAR")
    if c.lt > .3: money_text(img, "$3,650", 610, 545, tw(c.lt, .3, .5, 60, 160, back_out), seed=boil(c))
    money_jar(img, 540, FLOOR, 330, 520, fill=tw(c.lt, .2, 2.5, 0, .88), seed=3)
    doodle(img, 170, FLOOR, .85, outfit="tie", mood="smug", arms=("hip", "offer"), look=.5, seed=boil(c))
    a = doodle(img, 910, FLOOR, .85, outfit="hoodie", mood="shocked" if c.lt > 1.5 else "smile",
               arms=("up", "up") if c.lt > 1.5 else "down", look=-.5, seed=boil(c) + 1)
    if c.lt > 1.5: doodle_marks(img, a["head"], a["head_r"], "excited", seed=boil(c))
    return img

def split(c):
    img, d = canvas(PAPER)
    dashed_line(img, 540, 480, FLOOR + 20)
    for x, up in ((270, False), (810, True)):
        bill(img, x, 520, 140, label="$10")
        block_arrow(img, x, tw(c.lt, 0, .6, 760, 680, back_out), 120 if up else 80, up=up, seed=boil(c))
    a = doodle(img, 270, FLOOR, .8, outfit="hoodie", mood="sad", arms=("show", "show"), seed=boil(c))
    (x0, y0), (x1, y1) = a["hand_l"], a["hand_r"]
    wallet(img, (x0 + x1) / 2, (y0 + y1) / 2 + 8, 90, seed=boil(c))
    doodle_marks(img, a["head"], a["head_r"], "sweat")
    doodle(img, 880, FLOOR, .8, outfit="tie", mood="smile", arms=("down", "hip"), look=-.3, seed=boil(c) + 1)
    money_jar(img, 690, FLOOR, 160, 230, fill=.75, seed=3)
    money_pile(img, 720, FLOOR + 40, 80, rows=(2, 1))
    return img

def growth(c):
    img, d = canvas(PAPER)
    money_text(img, "$18,250", 540, 560, 140, seed=boil(c))
    grow = tw(c.lt, .2, 1.6, 0, 1)
    hatched_chart(img, 80, FLOOR - 40, [max(2, v * grow) for v in (90, 150, 230, 330, 450)], bar_w=70, seed=2)
    if grow >= 1: curve_arrow(img, [(70, FLOOR - 180), (220, FLOOR - 230), (360, FLOOR - 350), (450, FLOOR - 560)], w=11, seed=boil(c))
    a = doodle(img, 800, FLOOR, .9, outfit="tie", mood="happy" if grow >= 1 else "smile", arms=("point", "up"), look=-.4,
               seed=boil(c))
    if grow >= 1: doodle_marks(img, a["head"], a["head_r"], "excited", seed=boil(c))
    return img

SCENES = [(0, year), (1, split), (2, growth)]
SFX = [(0, .3, "pop"), (2, 1.8, "ding")]
MUSIC = ("pad", [], None)
