"""Objects: the engine's + the channel's (alias -> "module[:name]")."""
from reels_engine.lazy import make
from reels_engine.registry import PROPS
MAP = {**PROPS, "coin": "channel.pieces"}
__getattr__ = make(MAP, __name__)
