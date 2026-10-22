"""Personaje base de caricatura ('guy') y utilidades para colocar cosas sobre él."""
import math
from .base import dk, WHITE, BLK, SKIN

def guy(d, x, y, s=1.0, mood="neutral", arms="down", look=0.0, t=0.0, hoodie=(240, 120, 40)):
    S = lambda v: v * s
    d.ellipse([x-S(130), y-S(16), x+S(130), y+S(16)], fill=(70, 72, 75))
    jeans = (45, 65, 120)
    bob = math.sin(t * 8) * S(3) if mood == "scared" else 0
    for sx in (-1, 1):
        d.rounded_rectangle([x + sx*S(10) - (S(65) if sx < 0 else 0), y-S(180), x + sx*S(10) + (S(65) if sx > 0 else 0), y-S(10)], S(20), fill=jeans)
        d.ellipse([x + sx*S(50) - S(48), y-S(42), x + sx*S(50) + S(48), y+S(4)], fill=(30, 30, 30))
    y = y + bob
    sh = dk(hoodie, 0.8)
    # arms (behind body for some poses)
    def arm(sx, hx, hy):
        d.line([(x + sx*S(95), y-S(365)), (hx, hy)], fill=sh, width=int(S(46)), joint="curve")
        d.ellipse([hx-S(26), hy-S(26), hx+S(26), hy+S(26)], fill=SKIN)
    if arms == "up":
        arm(-1, x-S(185), y-S(560)); arm(1, x+S(185), y-S(560))
    d.rounded_rectangle([x-S(110), y-S(415), x+S(110), y-S(150)], S(60), fill=hoodie)
    d.rounded_rectangle([x-S(62), y-S(265), x+S(62), y-S(195)], S(22), fill=sh)
    d.line([(x-S(22), y-S(400)), (x-S(26), y-S(330))], fill=WHITE, width=int(S(7)))
    d.line([(x+S(22), y-S(400)), (x+S(26), y-S(330))], fill=WHITE, width=int(S(7)))
    if arms == "down":
        arm(-1, x-S(135), y-S(205)); arm(1, x+S(135), y-S(205))
    elif arms == "push":
        arm(-1, x+S(150), y-S(300)); arm(1, x+S(200), y-S(285))
    elif arms == "mop":
        arm(-1, x+S(110), y-S(290)); arm(1, x+S(170), y-S(320))
    elif arms == "switch":
        arm(-1, x-S(135), y-S(205)); arm(1, x+S(190), y-S(470))
    hx, hy = x, y - S(505)
    d.ellipse([hx-S(100), hy-S(100), hx+S(100), hy+S(100)], fill=SKIN)
    d.chord([hx-S(106), hy-S(114), hx+S(106), hy+S(72)], 180, 360, fill=(55, 38, 28))
    d.polygon([(hx-S(100), hy-S(20)), (hx-S(60), hy-S(60)), (hx-S(105), hy-S(70))], fill=(55, 38, 28))
    lx = look * S(10)
    if mood == "relief":
        for sx in (-1, 1):
            d.arc([hx+sx*S(38)-S(24), hy-S(10), hx+sx*S(38)+S(24), hy+S(25)], 200, 340, fill=BLK, width=int(S(7)))
        d.arc([hx-S(40), hy+S(20), hx+S(40), hy+S(70)], 20, 160, fill=(120, 40, 30), width=int(S(8)))
    else:
        er = S(34) if mood == "scared" else S(25)
        for sx in (-1, 1):
            ex, ey = hx + sx*S(38), hy + S(5)
            d.ellipse([ex-er, ey-er, ex+er, ey+er], fill=WHITE, outline=BLK, width=int(S(4)))
            pr = S(11) if mood == "scared" else S(12)
            d.ellipse([ex+lx-pr, ey-pr, ex+lx+pr, ey+pr], fill=BLK)
            if mood == "scared":
                d.line([(ex-S(26), ey-S(52)-sx*S(6)), (ex+S(26), ey-S(52)+sx*S(6))], fill=(55, 38, 28), width=int(S(8)))
        if mood == "scared":
            d.ellipse([hx-S(20), hy+S(45), hx+S(20), hy+S(85)], fill=(70, 20, 20))
            dy = (t * 120) % 60
            d.polygon([(hx+S(105), hy-S(40)+S(dy)), (hx+S(92), hy-S(10)+S(dy)), (hx+S(118), hy-S(10)+S(dy))], fill=(120, 190, 255))
            d.ellipse([hx+S(92), hy-S(22)+S(dy), hx+S(118), hy+S(4)+S(dy)], fill=(120, 190, 255))
        else:
            d.arc([hx-S(30), hy+S(30), hx+S(30), hy+S(65)], 20, 160, fill=(120, 40, 30), width=int(S(7)))

def anchors(x, y, s=1.0):
    """Puntos del cuerpo de 'guy' (y de don_tono) para poner objetos encima sin que floten.
    Uso: a = anchors(540, 1290, .7); medal(d, *a['chest'], ...)"""
    S = lambda v: v * s
    return {
        "head": (x, y - S(520)), "head_r": S(125), "box": (x - S(150), y - S(660), x + S(150), y), "head_top": (x, y - S(640)), "eyes": (x, y - S(530)), "mouth": (x, y - S(470)),
        "neck": (x, y - S(415)), "chest": (x - S(30), y - S(320)), "belly": (x, y - S(230)), "feet": (x, y),
        "hand_r_down": (x + S(135), y - S(205)), "hand_l_down": (x - S(135), y - S(205)),
        "hand_r_up": (x + S(185), y - S(560)), "hand_l_up": (x - S(185), y - S(560)),
        "hand_r_push": (x + S(200), y - S(285)), "hand_l_push": (x + S(150), y - S(300)),
    }

def medal(d, x, y, s=1.0, text="1º", ribbon=(40, 120, 220), neck=None):
    """Medalla colgada; (x, y) = centro de la medalla. neck=(x, y) dibuja el listón desde el cuello."""
    from .core import F, YEL, BLK
    S = lambda v: v * s
    if neck:
        d.line([(neck[0] - S(30), neck[1]), (x, y - S(30))], fill=ribbon, width=int(S(16))); d.line([(neck[0] + S(30), neck[1]), (x, y - S(30))], fill=ribbon, width=int(S(16)))
    d.ellipse([x - S(40), y - S(40), x + S(40), y + S(40)], fill=YEL, outline=BLK, width=4)
    d.text((x, y), text, font=F(S(34)), fill=BLK, anchor="mm")

