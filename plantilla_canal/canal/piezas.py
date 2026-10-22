"""Piezas propias del canal. Toda pieza: (d, x, y, s=1.0, ...), contorno negro, (x, y) = centro abajo."""
from reels_engine.core import BLK, F

def coin(d, x, y, s=1.0, label="$"):
    """Moneda dorada con símbolo."""
    r = 60 * s
    d.ellipse([x - r, y - 2 * r, x + r, y], fill=(250, 200, 50), outline=BLK, width=max(3, int(6 * s)))
    d.text((x, y - r), label, font=F(70 * s), fill=BLK, anchor="mm")
