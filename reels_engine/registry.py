"""Piezas que trae el motor, listas para mezclar con las del canal:

    MAP = {**registry.PERSONAJES, "mi_monstruo": "lib.criaturas"}

Formato: alias -> "modulo[:nombre_real]"."""
PERSONAJES = {
    "guy": "reels_engine.humanos", "anchors": "reels_engine.humanos", "medal": "reels_engine.humanos",
}
PROPS = {
    # muebles e interiores
    **{k: f"reels_engine.muebles:{k}" for k in ("chair", "table", "counter", "wall_clock", "alarm_clock", "window", "picture",
                                                  "floor_lamp", "door", "shelf", "light_switch", "laptop", "piggy_bank")},
    # exteriores
    **{k: f"reels_engine.exterior:{k}" for k in ("house", "building", "tree", "bush", "cactus", "street_lamp", "clouds", "fence",
                                                   "road", "booth", "bolt", "ground_current")},
    "sun_simple": "reels_engine.exterior:sun", "moon_disc": "reels_engine.exterior:moon",
    # documentos, pantallas y gráficas
    **{k: f"reels_engine.pantallas:{k}" for k in ("checklist", "document", "phone_chat", "monitor", "people_grid", "thought", "sign_board",
                                                    "heart", "arrow", "ruler", "wanted", "blob_map", "cracks", "bar_chart")},
}
FONDOS = {
    "make_space": "reels_engine.motion:space_bg", "radial_bg": "reels_engine.motion",
}
