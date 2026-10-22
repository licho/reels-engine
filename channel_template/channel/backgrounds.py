"""Full backgrounds (an image the size of the canvas)."""
from reels_engine.lazy import make
from reels_engine.registry import BACKGROUNDS
MAP = {**BACKGROUNDS}
__getattr__ = make(MAP, __name__)
