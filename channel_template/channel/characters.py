"""Characters: the engine's + the channel's."""
from reels_engine.lazy import make
from reels_engine.registry import CHARACTERS
MAP = {**CHARACTERS}
__getattr__ = make(MAP, __name__)
