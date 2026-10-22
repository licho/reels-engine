"""Pieces that come with the engine, ready to merge with the channel's own:

    MAP = {**registry.CHARACTERS, "my_monster": "channel.creatures"}

Format: alias -> "module[:real_name]"."""
CHARACTERS = {
    "guy": "reels_engine.humans", "anchors": "reels_engine.humans", "medal": "reels_engine.humans",
    # cartoon style
    "buddy": "reels_engine.cartoon.humans", "buddy_anchors": "reels_engine.cartoon.humans",
}
PROPS = {
    # furniture and indoor things
    **{k: f"reels_engine.furniture:{k}" for k in ("chair", "table", "counter", "wall_clock", "alarm_clock", "window", "picture",
                                                    "floor_lamp", "door", "shelf", "light_switch", "laptop", "piggy_bank")},
    # outdoors
    **{k: f"reels_engine.exterior:{k}" for k in ("house", "building", "tree", "bush", "cactus", "street_lamp", "clouds", "fence",
                                                   "road", "booth", "bolt", "ground_current")},
    "sun_simple": "reels_engine.exterior:sun", "moon_disc": "reels_engine.exterior:moon",
    # documents, screens and charts
    **{k: f"reels_engine.screens:{k}" for k in ("checklist", "document", "phone_chat", "monitor", "people_grid", "thought", "sign_board",
                                                  "heart", "arrow", "ruler", "wanted", "blob_map", "cracks", "bar_chart")},
    # cartoon style
    "campfire": "reels_engine.cartoon.exterior",
}
BACKGROUNDS = {
    "make_space": "reels_engine.motion:space_bg", "radial_bg": "reels_engine.motion",
}

# old Spanish names, kept so existing channels keep working
PERSONAJES, FONDOS = CHARACTERS, BACKGROUNDS
