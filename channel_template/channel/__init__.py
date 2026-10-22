"""The channel's package. Registers the configuration BEFORE any part of the engine is used."""
import os
from reels_engine import Channel, configure

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

configure(Channel(
    name="my-channel",
    root=ROOT,
    outdir="/tmp/my_channel_out",
    # timezone="America/Mexico_City",      # zone for scheduled dates (default: the machine's)
    caption_highlight=(80, 220, 120),        # *highlighted* words in green
    chip_bg=(30, 110, 210),                  # blue labels
    code_dirs=("channel",),
    catalog_out="channel/CATALOG.md",
    catalog_header=("# My channel's catalog\n", "Generated with `python3 -m channel.catalog`.\n"),
    catalog_api=(("reels_engine.core", "reels_engine.core"), ("reels_engine.motion", "reels_engine.motion"), ("reels_engine.camera", "reels_engine.camera")),
    catalog_maps=("channel.characters", "channel.props", "channel.backgrounds"),
))
