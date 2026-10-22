"""Objetos: los del motor + los del canal (alias -> "modulo[:nombre]")."""
from reels_engine.lazy import make
from reels_engine.registry import PROPS
MAP = {**PROPS, "coin": "canal.piezas"}
__getattr__ = make(MAP, __name__)
