# reels-engine

Engine to produce vertical reels (1080x1920) with code: scenes drawn with Pillow, GSAP-style animation,
word-by-word captions, speech bubbles that place themselves, audio (voice + effects + generated music),
voice sync and an automatic check of every frame (covered captions, cut or overlapping texts, contrast).

A **channel** (for example `licho/datos-asustan-videos`) is a separate repo that installs this engine, sets its
configuration (colors, zones, output folder…) and adds its own pieces and videos.

## Install

System requirements: Python 3.9+, `ffmpeg` and the DejaVu Sans font (`/usr/share/fonts/truetype/dejavu/`).

```
pip install "reels-engine[audio] @ git+https://github.com/licho/reels-engine@v0.4.0"
```

The channel pins the version in `requirements.txt` (always a tag, never `main`):

```
reels-engine[audio] @ git+https://github.com/licho/reels-engine@v0.4.0
```

`[audio]` adds `scipy` (faster audio filters). It works without it, just slower when mixing.

## Create a new channel from scratch

The [`channel_template/`](channel_template/) folder is a minimal channel that works as is. To start a new one:

1. **Create the channel repo** and copy the contents of `channel_template/` into it (the `channel/` and `specs/` folders).
   Add a `requirements.txt` with the line above and install: `pip install -r requirements.txt`.
2. **Configure the channel** in `channel/__init__.py`. Everything is optional; whatever you leave out takes the default:
   ```python
   configure(Channel(
       name="finance",
       root=ROOT,
       outdir="/tmp/finance_out",            # where previews and videos go
       font_bold="/path/to/MyFont-Bold.ttf",
       caption_highlight=(80, 220, 120),     # color of *highlighted* words
       chip_bg=(30, 110, 210),               # label color
       vignette=0,                           # no vignette
       wps=2.6,                              # reading speed (words per second)
       music=("pad", [], None),              # default music
   ))
   ```
   The full list (safe zones, captions, check thresholds, catalog, extra music styles…) is commented in
   [`reels_engine/config.py`](reels_engine/config.py). `configure()` must run **before** importing the rest of the
   engine; that's why it lives in the channel package's `__init__.py` and every channel command imports that package first.
3. **Your own pieces**: draw them in `channel/pieces.py` (or several modules) and register them in `channel/props.py`,
   `channel/characters.py` or `channel/backgrounds.py`, in the `MAP` dict (`alias -> "module[:name]"`). The MAPs start
   with the engine's pieces (`registry.PROPS`, `registry.CHARACTERS`, `registry.BACKGROUNDS`) plus the channel's.
4. **First video**: copy `specs/s01_savings.py` and change `NAME`, `LINES`, the scene functions, `SCENES`, `SFX` and `MUSIC`.
5. **Commands** (from the channel root):
   ```
   python3 -m channel.produce specs/s01.py text           # text for the voice + estimated duration
   python3 -m channel.produce specs/s01.py sheet          # frame sheet to review the composition
   python3 -m channel.produce specs/s01.py preview 2 6 10 # single frames (seconds)
   python3 -m channel.produce specs/s01.py check          # automatic check
   python3 -m channel.produce specs/s01.py silent         # video without voice (music + effects)
   python3 -m channel.produce specs/s01.py final voice.mp3  # final video synced to the voice
   python3 -m channel.catalog                             # regenerates the channel's piece catalog
   ```

## What the engine includes

| Module | What it is |
|---|---|
| `config` | `Channel` (channel configuration) and `configure()` |
| `base` | font `F`, colors, `lerp`/`ease`/`pop`, `chip` (label), `bigtext`, `rich_caption`, `xmark`, `check` |
| `core` | safe zones, `canvas`, `grad`, bubbles `bubble`/`say`, `fit_font`, `calendar`, `gauge`, `confetti`, `speedlines`, `sparkles`, `follow_btn`, `stamp` |
| `motion` | easing curves (`back_out`, `elastic_out`…), `tw`, `yoyo`, `shake`, `layer`, `glow`, `radial_bg`, `space_bg`, `vignette`, `sphere_shade`, word-by-word captions |
| `camera` | camera moves over any image: `Shot`, `film`, `path`, `pan`, `zoom_in`, `zoom_out`, `ken_burns`, `whip`, `handheld`, `impact` (see "Camera") |
| `produce` | commands text/sheet/preview/check/silent/final, parallel rendering, check cache |
| `check` | automatic frame check and per-piece contrast |
| `audio`, `align` | mixes voice + effects + music; syncs the voice by its pauses |
| `humans` | base character `guy`, `anchors` (head, mouth, hands…), `medal` |
| `furniture`, `exterior`, `screens` | neutral pieces: furniture, clock, window, house, tree, clouds, lightning, documents, phone chat, monitor, `bar_chart`, `people_grid`… |
| `cartoon` | cartoon style (separate, see "Styles"): `Brush`, shapes (`jagged`, `spiky_blob`, `blob`, `teardrop`, `strokes`), `humans.buddy`, `exterior.campfire` |
| `registry` | the engine's pieces, ready to merge into the channel's `MAP`s |
| `lazy`, `catalog` | lazy-loading catalogs and the catalog generator |

Spec format, safe zones and animation tips: see the `CLAUDE.md` of the Datos que Asustan channel, which is still the
most complete reference.

Default on-screen texts (`Channel.follow_text`, and piece defaults such as `calendar(label=…)` or `wanted(title=…)`)
are in Spanish because the current channels are; pass your own text to change them.

## Styles

The engine has two styles that can be mixed in the same video; neither changes the other:

- **Basic** (`humans`, `furniture`, `exterior`, `screens`): flat shapes with a black outline. Pieces take the
  `ImageDraw` (`d`). It's the one Datos que Asustan uses.
- **Cartoon** (`reels_engine.cartoon`): soft edges (drawn at double size and scaled down), very dark brown ink
  (`Channel.ink`), rough edges and stroke textures. Pieces take the image (`img`) because they're painted on a separate
  layer, and they report their outline to the automatic check.

```python
from channel.characters import buddy
from channel.props import campfire
campfire(img, 540, FLOOR - 40, .8, t=c.t)
a = buddy(img, 300, FLOOR, .8, arms="wave", mood="laugh", hair="bangs", shirt=(80, 150, 220), t=c.t)
say(ImageDraw.Draw(img), "Hi!", a["mouth"], a["head_r"])
```

`buddy` is the base to build characters on: `pose` (standing, sitting), `arms` (down, up, hips, wave, point, think,
behind, or `(left, right)`), `mood` (happy, neutral, sad, surprised, angry, laugh, asleep), `hair` (none, bangs, short),
skin/shirt/hair colors, and two hooks to dress it without redrawing the body: `dress(p, a)` (over the torso, under the
arms) and `extras(p, a)` (at the end). `p` is the `Brush` and `a` the body points (head, mouth, hands, chest, hip…).
Full example: `channel_template/specs/s02_cartoon.py`.

Your own pieces in this style: `with Brush(img, (x0, y0, x1, y1)) as p: p.polygon(...); p.polyline(...)`.
Careful with very dark backgrounds: the ink is almost black (the contrast check warns about it).

## Camera

`reels_engine.camera` films a "world" image (a scene drawn bigger than the screen, an illustration, or the frame
itself) and paints the view on the screen or on a box of it. Moves are sub-pixel smooth (no jitter on slow pans).

```python
from reels_engine.camera import Shot, film, path, pan, zoom_in, zoom_out, ken_burns, whip, handheld, impact

img = Image.new("RGB", (W, H))
shot = path(c.lt, [(0, Shot(1400, 1300, 1.0)), (1.5, Shot(1750, 1290, 2.5))])   # glide to a face
view = film(img, world, shot)                    # dst=(x0, y0, x1, y1) to film inside a box
say(ImageDraw.Draw(img), "Hi!", view.to_screen(mouth), head_r * view.scale)
```

- `Shot(x, y, zoom=1, angle=0)`: where the camera looks (world px). `zoom=1` is the biggest view that fits inside the
  world; `2` is twice as close; below 1 shows the world smaller with `fill` around it. `angle` tilts the camera (degrees).
- Moves (each returns the Shot for time `t`): `path` (keyframes, any mix of pan/zoom/tilt), `pan`, `zoom_in`,
  `zoom_out`, `ken_burns` (slow, steady), `whip` (very fast, with motion blur).
- On top of any move: `handheld(shot, t)` (gentle wobble), `impact(shot, t, t0)` (hit or scare shake).
- `film` returns a `View`: `to_screen(p)` / `to_world(p)` and `scale`, so bubbles and labels follow the camera.
- Example with every move: `channel_template/specs/s03_camera.py`.

## Drawing backend

Everything is drawn with Pillow today (`brush="pil"`). The configuration already has the `brush` field to add a vector
backend (cairo) later without breaking channels that use Pillow: the current pieces will keep working the same.

## Old Spanish names

Up to v0.2.0 the engine used Spanish names. They still work, so channels pinned to older versions can upgrade without
changing their code:

| Old name | New name |
|---|---|
| `reels_engine.muebles`, `pantallas`, `humanos`, `catalogo` | `reels_engine.furniture`, `screens`, `humans`, `catalog` |
| `registry.PERSONAJES`, `registry.FONDOS` | `registry.CHARACTERS`, `registry.BACKGROUNDS` |
| commands `texto`, `hoja`, `check-contraste`, `sinvoz` | `text`, `sheet`, `check-contrast`, `silent` (the old names keep their old file names: `_hoja.png`, `_SINVOZ.mp4`) |
| `chair(kind="silla" / "oficina")` | `chair(kind="chair" / "office")` |

The v0.2.0 cartoon style (`caricatura`, `monito`, `fogata`, `Pincel`) was renamed without aliases (`cartoon`, `buddy`,
`campfire`, `Brush`): no channel used it yet.

## Publishing a new engine version

1. Change the code and test it with the template (`cd channel_template && python3 -m channel.produce specs/s01_savings.py check`)
   and with at least one real channel (preview + check of all its specs, comparing against the previous frames).
2. Bump `version` in `pyproject.toml` and `reels_engine/__init__.py`, and note the change below.
3. Commit, tag and push: `git tag v0.4.0 && git push origin main v0.4.0` (or create a GitHub release with tag `v0.4.0`;
   the `v` matters).
4. In each channel, change the tag in `requirements.txt` and reinstall (`pip install -r requirements.txt`).

Versions are never rewritten: if something goes wrong, publish another one.

## Versions

- **v0.4.0** — Camera (`reels_engine.camera`): pan, zoom in/out, Ken Burns, whip pan with motion blur, tilt,
  hand-held and impact shake, keyframed paths, and a `View` to place bubbles on the filmed scene. New example
  `s03_camera.py`. Nothing else changes: existing frames are identical.
- **v0.3.0** — Everything in English: code, comments, docs, check messages and commands (`text`, `sheet`, `silent`,
  `check-contrast`). Modules renamed (`furniture`, `screens`, `humans`, `catalog`, `cartoon`) and the template is now
  `channel_template/`. The old Spanish names still work (see "Old Spanish names"). No frame changes: the template and
  every Datos que Asustan spec render pixel-identical to v0.1.0.
- **v0.2.0** — Cartoon style (then `reels_engine.caricatura`): brush, shapes, base character (poses, faces, hair and
  hooks to dress it) and campfire. `Channel.ink`. The automatic check sees pieces painted on a separate layer.
  Nothing in the basic style changes: frames from v0.1.0 come out identical.
- **v0.1.0** — First version, split from `licho/datos-asustan-videos` (`lib/`) without changing any frame of its videos.
