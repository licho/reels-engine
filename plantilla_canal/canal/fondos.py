"""Fondos completos (imagen del tamaño del lienzo)."""
from reels_engine.lazy import make
from reels_engine.registry import FONDOS
MAP = {**FONDOS}
__getattr__ = make(MAP, __name__)
