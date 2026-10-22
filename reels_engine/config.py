"""Configuración del canal: todo lo que cambia de un canal a otro (fuentes, colores, zonas seguras,
subtítulos, viñeta, velocidad de lectura, carpeta de salida, música, umbrales de la revisión y catálogo).

El canal la registra UNA vez, antes de importar cualquier otra parte del motor:

    from reels_engine import Channel, configure
    configure(Channel(name="mi_canal", root="/ruta/al/repo", outdir="/tmp/mi_canal_out"))

Lo normal es hacerlo en el `__init__.py` del paquete del canal (por ejemplo `lib/__init__.py`)."""
from dataclasses import dataclass, field, replace, fields

DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def _palette():
    return {"YEL": (255, 214, 0), "RED": (225, 35, 45), "WHITE": (255, 255, 255), "BLK": (0, 0, 0), "SKIN": (241, 194, 150),
            "GREEN": (30, 140, 80), "BLUE": (40, 120, 220), "GRAY": (90, 90, 100), "ORANGE": (230, 130, 30), "PURPLE": (140, 60, 170)}

@dataclass(frozen=True)
class Channel:
    name: str = "canal"
    root: str = "."                       # raíz del repo del canal (catálogo, huella del check)
    # lienzo y video
    size: tuple = (1080, 1920)
    fps: int = 30
    workers: int = 4                      # procesos para dibujar en paralelo (máximo)
    brush: str = "pil"                    # pincel de dibujo; hoy solo "pil" (más adelante: "cairo")
    # tipografía y colores
    font_bold: str = DEJAVU_BOLD          # fuente de letreros, subtítulos y globos
    palette: dict = field(default_factory=_palette)   # colores con nombre (YEL, RED, WHITE, BLK, SKIN, GREEN, …)
    caption_fill: tuple = (255, 255, 255)
    caption_highlight: tuple = (255, 214, 0)          # palabras entre *asteriscos*
    caption_stroke: tuple = (0, 0, 0)
    chip_bg: tuple = (225, 35, 45)
    chip_fg: tuple = (255, 255, 255)
    # zonas seguras (y en px)
    chip1: int = 300                      # letrero principal
    chip2: int = 420                      # segundo letrero
    action_top: int = 480
    action_bot: int = 1320
    floor: int = 1300                     # piso por defecto (pies de personajes)
    cap_y: int = 1500                     # centro de los subtítulos
    cap_free: tuple = (1380, 1640)        # franja reservada a subtítulos (no poner nada)
    bubble_zone: tuple = (380, 1330)      # límites verticales de los globos de diálogo
    # subtítulos, viñeta y ritmo
    caption_style: str = "words"          # "words" (palabra por palabra) o "static"
    caption_size: int = 70
    captions: bool = True
    vignette: float = .35                 # 0 = sin viñeta
    wps: float = 2.75                     # palabras por segundo (duración estimada)
    gap: float = .35                      # pausa entre líneas (s)
    end: float = 4.0                      # segundos extra al final
    follow_text: str = "SÍGUEME"
    # salida y audio
    outdir: str = "/tmp/reels_out"
    music: tuple = ("bass", [], None)     # música por defecto si el spec no define MUSIC
    music_styles: dict = field(default_factory=dict)  # estilos extra: nombre -> dict(bpm, bass, mel, wave)
    # revisión automática
    check_margin: int = 18                # px alrededor de los subtítulos
    contrast_limit: float = .30           # fracción de orilla que se confunde a partir de la cual se avisa
    contrast_ratio: float = 1.35          # relación de luz por debajo de la cual dos colores se confunden
    contrast_dist: float = 70             # …y distancia de color
    contrast_skip: tuple = ()             # piezas que no se revisan por contraste (además de las del motor)
    code_dirs: tuple = ()                 # carpetas extra cuyo código invalida el check guardado (p. ej. "lib")
    # catálogo
    catalog_out: str = "CATALOGO.md"      # relativo a root
    catalog_header: tuple = ()            # líneas de introducción
    catalog_api: tuple = ()               # (título, módulo del motor) a documentar, p. ej. ("lib.core", "reels_engine.core")
    catalog_maps: tuple = ()              # módulos con MAP de piezas, p. ej. "lib.personajes"
    catalog_paths: dict = field(default_factory=dict)   # prefijo de módulo -> carpeta, para módulos fuera de sys.path

    @property
    def W(self): return self.size[0]
    @property
    def H(self): return self.size[1]

_current = Channel()
_used = False

def configure(channel=None, **kw):
    """Registra la configuración del canal. Debe llamarse antes de importar el resto del motor."""
    global _current
    new = replace(channel or _current, **kw)
    if _used and new != _current:
        raise RuntimeError("reels_engine: configure() llegó tarde; el motor ya se importó con otra configuración. "
                           "Llama configure() antes de importar reels_engine.core / motion / produce.")
    _current = new
    return _current

def current():
    """Configuración vigente (la primera lectura la deja fija)."""
    global _used
    _used = True
    return _current
