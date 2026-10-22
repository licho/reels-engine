"""Example spec: one video = one file. Try it with:
  python3 -m channel.produce specs/s01_savings.py text
  python3 -m channel.produce specs/s01_savings.py preview 2 6 10
  python3 -m channel.produce specs/s01_savings.py check"""
from channel import ROOT
from reels_engine.core import *
from reels_engine.motion import tw, yoyo, back_out, radial_bg
from channel.characters import guy, anchors
from channel.props import coin, bar_chart, piggy_bank

NAME = "s01_savings"
LINES = [
    ("excited", "If you save ten dollars a day, in a year you'll have three thousand six hundred fifty.", "Ten dollars a day = *$3,650* a year"),
    ("confident", "And if you invest it, it grows even more.", "If you invest it, *it grows more*"),
]

def intro(c):
    img = radial_bg(((0, (40, 70, 60)), (1, (10, 20, 18)))); d = ImageDraw.Draw(img)
    chip(d, "SAVINGS CHALLENGE", CHIP1, appear=c.lt / .4)
    a = anchors(380, FLOOR, .8)
    guy(d, 380, FLOOR, .8, mood="neutral", t=c.t)
    piggy_bank(d, 760, FLOOR, 1.0, t=c.t)
    coin(d, 760, tw(c.lt, .3, .6, 900, 1150, back_out), .6)   # the coin drops into the piggy bank
    say(d, "$10 a day!", a["mouth"], a["head_r"], avoid=[(660, 780, 860, 1300)])
    return img

def chart(c):
    img = radial_bg(((0, (40, 50, 80)), (1, (8, 10, 25)))); d = ImageDraw.Draw(img)
    chip(d, "IN ONE YEAR", CHIP1)
    bar_chart(d, 120, 760, 900, [("Saved", 3650, (80, 200, 120)), ("Invested", 3900, (250, 200, 50))], frac=tw(c.lt, 0, 1.2, 0, 1))
    return img

SCENES = [(0, intro), (1, chart)]
SFX = [(0, .3, "pop"), (1, .2, "ding")]
MUSIC = ("bass", [], None)
