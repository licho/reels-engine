"""Spec de ejemplo con el estilo caricatura (monito + fogata). Probar con:
  python3 -m canal.produce specs/s02_caricatura.py preview 1 4
  python3 -m canal.produce specs/s02_caricatura.py check"""
from reels_engine.core import *
from reels_engine.motion import tw, back_out, glow
from canal.personajes import monito
from canal.props import fogata

NAME = "s02_caricatura"
LINES = [
    ("excited", "Antes del despertador, nos despertaba el sol.", "Antes del *despertador*, nos despertaba *el sol*"),
    ("calm", "Y en la noche, todos junto al fuego.", "Y en la noche, junto al *fuego*"),
]
CIELO = ((240, 185, 155), (200, 155, 103))

def manana(c):
    img, d = canvas(CIELO)
    chip(d, "ANTES DEL DESPERTADOR", CHIP1, appear=c.lt / .4)
    sol = tw(c.lt, 0, 1.2, 760, 560, back_out)
    d.ellipse([820 - 90, sol - 90, 820 + 90, sol + 90], fill=YEL, outline=BLK, width=6)
    a = monito(img, 380, FLOOR, .85, brazos="arriba" if c.lt > 1 else "abajo", mood="feliz" if c.lt > 1 else "dormido", pelo="fleco", t=c.t)
    if c.lt > 1.2: say(ImageDraw.Draw(img), "¡Buenos días!", a["mouth"], a["head_r"])
    return img

def noche(c):
    img, d = canvas(((95, 90, 150), (190, 140, 100)))
    chip(d, "Y EN LA NOCHE…", CHIP1)
    glow(img, 540, FLOOR - 200, 300, (255, 190, 90), .35)
    fogata(img, 540, FLOOR - 40, .8, t=c.t)
    monito(img, 200, FLOOR, .75, pose="sentado", mood="feliz", pelo="corto", ropa=(80, 150, 220), t=c.t)
    monito(img, 900, FLOOR, .75, brazos="saluda", mood="risa", ropa=(230, 120, 60), t=c.t)
    return img

SCENES = [(0, manana), (1, noche)]
SFX = [(0, .3, "pop"), (0, 1.0, "ding")]
MUSIC = ("pad", [], None)
