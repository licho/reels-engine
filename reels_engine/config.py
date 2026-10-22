"""Channel configuration: everything that changes from one channel to another (fonts, colors, safe zones,
captions, vignette, reading speed, output folder, music, check thresholds and catalog).

The channel registers it ONCE, before importing any other part of the engine:

    from reels_engine import Channel, configure
    configure(Channel(name="my_channel", root="/path/to/repo", outdir="/tmp/my_channel_out"))

The usual place is the `__init__.py` of the channel's package (for example `lib/__init__.py`)."""
from dataclasses import dataclass, field, replace, fields

DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def _palette():
    return {"YEL": (255, 214, 0), "RED": (225, 35, 45), "WHITE": (255, 255, 255), "BLK": (0, 0, 0), "SKIN": (241, 194, 150),
            "GREEN": (30, 140, 80), "BLUE": (40, 120, 220), "GRAY": (90, 90, 100), "ORANGE": (230, 130, 30), "PURPLE": (140, 60, 170)}

@dataclass(frozen=True)
class Channel:
    name: str = "channel"
    root: str = "."                       # channel repo root (catalog, check fingerprint)
    # canvas and video
    size: tuple = (1080, 1920)
    fps: int = 30
    workers: int = 4                      # max processes drawing in parallel
    brush: str = "pil"                    # drawing backend; only "pil" for now (later: "cairo")
    # type and colors
    font_bold: str = DEJAVU_BOLD          # font for labels, captions and speech bubbles
    palette: dict = field(default_factory=_palette)   # named colors (YEL, RED, WHITE, BLK, SKIN, GREEN, …)
    caption_fill: tuple = (255, 255, 255)
    caption_highlight: tuple = (255, 214, 0)          # words between *asterisks*
    caption_stroke: tuple = (0, 0, 0)
    chip_bg: tuple = (225, 35, 45)
    chip_fg: tuple = (255, 255, 255)
    ink: tuple = (43, 36, 32)                         # ink (outlines) of the cartoon style
    # safe zones (y in px)
    chip1: int = 300                      # main label
    chip2: int = 420                      # second label
    action_top: int = 480
    action_bot: int = 1320
    floor: int = 1300                     # default floor (characters' feet)
    cap_y: int = 1500                     # captions center
    cap_free: tuple = (1380, 1640)        # band reserved for captions (keep it clear)
    bubble_zone: tuple = (380, 1330)      # vertical limits for speech bubbles
    # captions, vignette and pacing
    caption_style: str = "words"          # "words" (word by word) or "static"
    caption_size: int = 70
    captions: bool = True
    vignette: float = .35                 # 0 = no vignette
    wps: float = 2.75                     # words per second (estimated duration)
    gap: float = .35                      # pause between lines (s)
    end: float = 4.0                      # extra seconds at the end
    follow_text: str = "SÍGUEME"               # on-screen text of follow_btn
    # output and audio
    outdir: str = "/tmp/reels_out"
    music: tuple = ("bass", [], None)     # default music when the spec doesn't define MUSIC
    music_styles: dict = field(default_factory=dict)  # extra styles: name -> dict(bpm, bass, mel, wave)
    # automatic check
    check_margin: int = 18                # px around the captions
    contrast_limit: float = .30           # fraction of the outline that blends in before warning
    contrast_ratio: float = 1.35          # luminance ratio below which two colors blend in
    contrast_dist: float = 70             # …and color distance
    contrast_skip: tuple = ()             # pieces skipped by the contrast check (besides the engine's)
    code_dirs: tuple = ()                 # extra folders whose code invalidates the saved check (e.g. "lib")
    # catalog
    catalog_out: str = "CATALOGO.md"      # relative to root
    catalog_header: tuple = ()            # intro lines
    catalog_api: tuple = ()               # (title, engine module) to document, e.g. ("lib.core", "reels_engine.core")
    catalog_maps: tuple = ()              # modules with a MAP of pieces, e.g. "lib.characters"
    catalog_paths: dict = field(default_factory=dict)   # module prefix -> folder, for modules outside sys.path

    @property
    def W(self): return self.size[0]
    @property
    def H(self): return self.size[1]

_current = Channel()
_used = False

def configure(channel=None, **kw):
    """Registers the channel configuration. Must be called before importing the rest of the engine."""
    global _current
    new = replace(channel or _current, **kw)
    if _used and new != _current:
        raise RuntimeError("reels_engine: configure() came too late; the engine was already imported with another configuration. "
                           "Call configure() before importing reels_engine.core / motion / produce.")
    _current = new
    return _current

def current():
    """Current configuration (the first read locks it)."""
    global _used
    _used = True
    return _current
