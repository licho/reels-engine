"""Lazy-loading catalogs of pieces: a dict MAP {alias: "module[:real_name]"} becomes a
module you can import each piece from by its alias. This is how the channel registers its own pieces.

    # the channel's channel/props.py
    from reels_engine.lazy import make
    from reels_engine.registry import PROPS
    MAP = {**PROPS, "my_piece": "channel.objects"}
    __getattr__ = make(MAP, __name__)
"""
import importlib

def make(MAP, modname, wrap=None):
    """wrap: wrap the pieces for the contrast check (yes by default, except background modules)."""
    if wrap is None: wrap = not modname.endswith(("backgrounds", "fondos"))
    def __getattr__(name):
        if name not in MAP: raise AttributeError(f"{modname}: there is no '{name}'. Available: {', '.join(sorted(MAP))}")
        mod, _, real = MAP[name].partition(":")
        obj = getattr(importlib.import_module(mod), real or name)
        if callable(obj) and wrap:
            from .check import element_wrap
            obj = element_wrap(obj, name)
        return obj
    return __getattr__
