"""python3 -m canal.catalogo  -> canal/CATALOGO.md"""
from . import personajes, props, fondos
from reels_engine.catalogo import generate
if __name__ == "__main__":
    generate()
