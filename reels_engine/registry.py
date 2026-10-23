"""Pieces that come with the engine, ready to merge with the channel's own:

    MAP = {**registry.CHARACTERS, "my_monster": "channel.creatures"}

Format: alias -> "module[:real_name]"."""
CHARACTERS = {
    "guy": "reels_engine.humans", "anchors": "reels_engine.humans", "medal": "reels_engine.humans",
    # cartoon style
    "buddy": "reels_engine.cartoon.humans", "buddy_anchors": "reels_engine.cartoon.humans",
    # sketch style
    "doodle": "reels_engine.sketch.humans", "doodle_anchors": "reels_engine.sketch.humans",
    "doodle_marks": "reels_engine.sketch.humans:marks",
    **{f"doodle_{k}": f"reels_engine.sketch.modern:{k}" for k in ("sultan", "admiral", "sailor", "guard", "doctor")},
    **{f"doodle_{k}": f"reels_engine.sketch.history:{k}" for k in ("roman", "viking", "pharaoh", "greek", "knight",
                                                                     "aztec", "maya")},
    **{f"doodle_{k}": f"reels_engine.sketch.work:{k}" for k in ("medic", "nurse", "chef", "police", "firefighter", "builder",
                                                                  "scientist", "teacher", "farmer", "mechanic", "pilot")},
    **{f"doodle_{k}": f"reels_engine.sketch.sports:{k}" for k in ("soccer_player", "basketball_player", "boxer", "runner",
                                                                    "tennis_player", "baseball_player", "referee")},
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
    # sketch style
    **{k: f"reels_engine.sketch.props:{k}" for k in ("bill", "money_stack", "money_pile", "money_jar", "money_text", "wallet",
                                                       "school_desk", "stool", "curve_arrow", "hatched_chart",
                                                       "wall_calendar", "dashed_line")},
    "block_arrow": "reels_engine.sketch.props:arrow",
    **{k: f"reels_engine.sketch.everyday:{k}" for k in ("coffee_cup", "burger", "pizza_slice", "car", "motorbike", "bicycle",
                                                          "cloud", "sun", "phone", "tv", "light_bulb", "clock", "shopping_bag",
                                                          "shopping_cart", "credit_card", "coin", "gift_box", "receipt",
                                                          "tomato", "ketchup_bottle")},
    **{f"sketch_{k}": f"reels_engine.sketch.everyday:{k}" for k in ("house", "building", "tree", "laptop", "piggy_bank")},
    **{k: f"reels_engine.sketch.history:{k}" for k in ("pyramid", "obelisk", "temple", "colosseum", "castle", "longship", "amphora",
                                                         "scroll", "torch", "crown", "laurel_wreath", "helmet", "sword", "axe",
                                                         "spear", "round_shield", "scutum", "heater_shield", "step_pyramid",
                                                         "sun_stone", "olmec_head", "stela", "macuahuitl", "chimalli", "corn",
                                                         "cacao_pod")},
    "greek_column": "reels_engine.sketch.history:column",
    **{k: f"reels_engine.sketch.sports:{k}" for k in ("soccer_ball", "basketball", "tennis_ball", "baseball", "volleyball",
                                                        "football", "tennis_racket", "baseball_bat", "boxing_glove", "dumbbell",
                                                        "kettlebell", "sneaker", "whistle", "stopwatch", "cone", "skateboard",
                                                        "jersey", "trophy", "podium", "soccer_goal", "basketball_hoop",
                                                        "scoreboard", "finish_flag")},
    **{k: f"reels_engine.sketch.finance:{k}" for k in ("bank", "safe", "atm", "cash_register", "calculator", "gold_bars",
                                                         "money_bag", "money_tree", "salary_envelope", "price_tag",
                                                         "percent_badge", "balance_scale", "hourglass", "line_chart",
                                                         "candle_chart", "pie_chart", "gauge", "contract", "ball_and_chain",
                                                         "umbrella", "goal_thermometer", "padlock", "magnifier", "rocket",
                                                         "balloon")},
    **{k: f"reels_engine.sketch.work:{k}" for k in ("hammer", "wrench", "screwdriver", "shovel", "frying_pan", "paint_roller",
                                                      "book", "flask", "clipboard", "toolbox", "ladder", "microscope", "scissors",
                                                      "computer_monitor", "office_desk", "office_chair", "filing_cabinet", "printer",
                                                      "briefcase", "mug", "stapler", "sticky_note", "folder", "whiteboard",
                                                      "potted_plant", "water_cooler", "desk_lamp", "pencil_cup", "id_badge", "work_hat")},
    "sport_ball": "reels_engine.sketch.sports:ball", "sport_medal": "reels_engine.sketch.sports:medal",
    **{k: f"reels_engine.sketch.modern:{k}" for k in ("flame", "blast", "smoke", "flagpole", "palace", "warship", "map_pin",
                                                        "pill_bottle", "pills", "newspaper")},
}
BACKGROUNDS = {
    "make_space": "reels_engine.motion:space_bg", "radial_bg": "reels_engine.motion",
    "seaside_bg": "reels_engine.sketch.modern",
}

# old Spanish names, kept so existing channels keep working
PERSONAJES, FONDOS = CHARACTERS, BACKGROUNDS
