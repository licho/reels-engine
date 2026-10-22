"""Spec de ejemplo: un video = un archivo. Probar con:
  python3 -m canal.produce specs/s01_ahorro.py texto
  python3 -m canal.produce specs/s01_ahorro.py preview 2 6 10
  python3 -m canal.produce specs/s01_ahorro.py check"""
from canal import ROOT
from reels_engine.core import *
from reels_engine.motion import tw, yoyo, back_out, radial_bg
from canal.personajes import guy, anchors
from canal.props import coin, bar_chart, piggy_bank

NAME = "s01_ahorro"
LINES = [
    ("excited", "Si guardas diez pesos diarios, en un año juntas tres mil seiscientos cincuenta.", "Diez pesos diarios = *$3,650* al año"),
    ("confident", "Y si los inviertes, crecen todavía más.", "Si los inviertes, *crecen más*"),
]

def intro(c):
    img = radial_bg(((0, (40, 70, 60)), (1, (10, 20, 18)))); d = ImageDraw.Draw(img)
    chip(d, "RETO DEL AHORRO", CHIP1, appear=c.lt / .4)
    a = anchors(380, FLOOR, .8)
    guy(d, 380, FLOOR, .8, mood="neutral", t=c.t)
    piggy_bank(d, 760, FLOOR, 1.0, t=c.t)
    coin(d, 760, tw(c.lt, .3, .6, 900, 1150, back_out), .6)   # la moneda cae en el cochinito
    say(d, "¡10 al día!", a["mouth"], a["head_r"], avoid=[(660, 780, 860, 1300)])
    return img

def grafica(c):
    img = radial_bg(((0, (40, 50, 80)), (1, (8, 10, 25)))); d = ImageDraw.Draw(img)
    chip(d, "EN UN AÑO", CHIP1)
    bar_chart(d, 120, 760, 900, [("Guardado", 3650, (80, 200, 120)), ("Invertido", 3900, (250, 200, 50))], frac=tw(c.lt, 0, 1.2, 0, 1))
    return img

SCENES = [(0, intro), (1, grafica)]
SFX = [(0, .3, "pop"), (1, .2, "ding")]
MUSIC = ("bass", [], None)
