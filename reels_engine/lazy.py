"""Catálogos de piezas con carga perezosa: un diccionario MAP {alias: "modulo[:nombre_real]"} se convierte en un
módulo del que se puede importar cada pieza por su alias. Así el canal registra sus propias piezas.

    # lib/props.py del canal
    from reels_engine.lazy import make
    from reels_engine.registry import PROPS
    MAP = {**PROPS, "mi_pieza": "lib.objetos"}
    __getattr__ = make(MAP, __name__)
"""
import importlib

def make(MAP, modname, wrap=None):
    """wrap: envolver las piezas para la revisión de contraste (por defecto sí, salvo módulos de fondos)."""
    if wrap is None: wrap = not modname.endswith("fondos")
    def __getattr__(name):
        if name not in MAP: raise AttributeError(f"{modname}: no existe '{name}'. Disponibles: {', '.join(sorted(MAP))}")
        mod, _, real = MAP[name].partition(":")
        obj = getattr(importlib.import_module(mod), real or name)
        if callable(obj) and wrap:
            from .check import element_wrap
            obj = element_wrap(obj, name)
        return obj
    return __getattr__
