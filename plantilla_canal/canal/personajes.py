"""Personajes: los del motor + los del canal."""
from reels_engine.lazy import make
from reels_engine.registry import PERSONAJES
MAP = {**PERSONAJES}
__getattr__ = make(MAP, __name__)
