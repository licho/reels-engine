"""python3 -m channel.catalog  -> channel/CATALOG.md"""
from . import characters, props, backgrounds
from reels_engine.catalog import generate
if __name__ == "__main__":
    generate()
