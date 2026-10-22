"""Example spec in the cartoon style (buddy + campfire). Try it with:
  python3 -m channel.produce specs/s02_cartoon.py preview 1 4
  python3 -m channel.produce specs/s02_cartoon.py check"""
from reels_engine.core import *
from reels_engine.motion import tw, back_out, glow
from channel.characters import buddy
from channel.props import campfire

NAME = "s02_cartoon"
LINES = [
    ("excited", "Before alarm clocks, the sun woke us up.", "Before the *alarm clock*, *the sun* woke us up"),
    ("calm", "And at night, everyone gathered around the fire.", "And at night, around the *fire*"),
]
SKY = ((240, 185, 155), (200, 155, 103))

def morning(c):
    img, d = canvas(SKY)
    chip(d, "BEFORE ALARM CLOCKS", CHIP1, appear=c.lt / .4)
    sun_y = tw(c.lt, 0, 1.2, 760, 560, back_out)
    d.ellipse([820 - 90, sun_y - 90, 820 + 90, sun_y + 90], fill=YEL, outline=BLK, width=6)
    a = buddy(img, 380, FLOOR, .85, arms="up" if c.lt > 1 else "down", mood="happy" if c.lt > 1 else "asleep", hair="bangs", t=c.t)
    if c.lt > 1.2: say(ImageDraw.Draw(img), "Good morning!", a["mouth"], a["head_r"])
    return img

def night(c):
    img, d = canvas(((95, 90, 150), (190, 140, 100)))
    chip(d, "AND AT NIGHT…", CHIP1)
    glow(img, 540, FLOOR - 200, 300, (255, 190, 90), .35)
    campfire(img, 540, FLOOR - 40, .8, t=c.t)
    buddy(img, 200, FLOOR, .75, pose="sitting", mood="happy", hair="short", shirt=(80, 150, 220), t=c.t)
    buddy(img, 900, FLOOR, .75, arms="wave", mood="laugh", shirt=(230, 120, 60), t=c.t)
    return img

SCENES = [(0, morning), (1, night)]
SFX = [(0, .3, "pop"), (0, 1.0, "ding")]
MUSIC = ("pad", [], None)
