# reels-engine

Engine to produce vertical reels (1080x1920) with code: scenes drawn with Pillow, GSAP-style animation,
word-by-word captions, speech bubbles that place themselves, audio (voice + effects + generated music),
voice sync and an automatic check of every frame (covered captions, cut or overlapping texts, contrast).

A **channel** (for example `licho/datos-asustan-videos`) is a separate repo that installs this engine, sets its
configuration (colors, zones, output folder…) and adds its own pieces and videos.

## Install

System requirements: Python 3.9+, `ffmpeg` and the DejaVu Sans font (`/usr/share/fonts/truetype/dejavu/`).

```
pip install "reels-engine[audio] @ git+https://github.com/licho/reels-engine@v0.5.0"
```

The channel pins the version in `requirements.txt` (always a tag, never `main`):

```
reels-engine[audio] @ git+https://github.com/licho/reels-engine@v0.5.0
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
   python3 -m channel.produce specs/s01.py draft          # quick review video (15 frames/s, half size)
   python3 -m channel.catalog                             # regenerates the channel's piece catalog
   python3 -m channel.publish out/s01.mp4 "2026-10-25 19:00" --title "..."   # schedules it on YouTube/Facebook
   ```

## What the engine includes

| Module | What it is |
|---|---|
| `config` | `Channel` (channel configuration) and `configure()` |
| `base` | font `F`, colors, `lerp`/`ease`/`pop`, `chip` (label), `bigtext`, `rich_caption`, `xmark`, `check` |
| `core` | safe zones, `canvas`, `grad`, bubbles `bubble`/`say`, `fit_font`, `calendar`, `gauge`, `confetti`, `speedlines`, `sparkles`, `follow_btn`, `stamp` |
| `motion` | easing curves (`back_out`, `elastic_out`…), `tw`, `yoyo`, `shake`, `layer`, `glow`, `radial_bg`, `space_bg`, `vignette`, `sphere_shade`, word-by-word captions |
| `camera` | camera moves over any image: `Shot`, `film`, `path`, `pan`, `zoom_in`, `zoom_out`, `ken_burns`, `whip`, `handheld`, `impact` (see "Camera") |
| `produce` | commands text/sheet/preview/check/silent/final/draft, parallel rendering, reused parts, check cache |
| `check` | automatic frame check and per-piece contrast |
| `publish` | schedules a finished video on YouTube and a Facebook Page at a date and time (see "Scheduling videos") |
| `audio`, `align` | mixes voice + effects + music; syncs the voice by its pauses |
| `humans` | base character `guy`, `anchors` (head, mouth, hands…), `medal` |
| `furniture`, `exterior`, `screens` | neutral pieces: furniture, clock, window, house, tree, clouds, lightning, documents, phone chat, monitor, `bar_chart`, `people_grid`… |
| `cartoon` | cartoon style (separate, see "Styles"): `Brush`, shapes (`jagged`, `spiky_blob`, `blob`, `teardrop`, `strokes`), `humans.buddy`, `exterior.campfire` |
| `sketch` | sketch style (separate, see "Styles"): `Pen`, `humans.doodle`, money pieces (`bill`, `money_stack`, `money_pile`, `money_jar`, `money_text`), `school_desk`, `hatched_chart`, arrows, `wall_calendar`…; `everyday`: coffee cup, car, motorbike, house, phone and other everyday objects; `history`: monuments, weapons, helmets and doodle in Roman/viking/pharaoh/Greek/knight/Aztec/Maya costume; `sports`: balls, gear, awards and doodle as athletes; `finance`: bank, safe, ATM, charts, gauge, debt and savings pieces |
| `registry` | the engine's pieces, ready to merge into the channel's `MAP`s |
| `lazy`, `catalog` | lazy-loading catalogs and the catalog generator |

Spec format, safe zones and animation tips: see the `CLAUDE.md` of the Datos que Asustan channel, which is still the
most complete reference.

Default on-screen texts (`Channel.follow_text`, and piece defaults such as `calendar(label=…)` or `wanted(title=…)`)
are in Spanish because the current channels are; pass your own text to change them.

## Styles

The engine has three styles that can be mixed in the same video; none changes the others:

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

- **Sketch** (`reels_engine.sketch`): hand-drawn marker look on light backgrounds. Every line wobbles a little and
  gets thinner at the ends, outlines overshoot where they close, colors are flat and shading is loose hatching.
  Near-black ink (`Channel.sketch_ink`); big amounts use `Channel.sketch_font` (empty = `font_bold`). Pieces take the
  image (`img`) and a `seed`.

```python
from channel.characters import doodle, doodle_marks
from channel.props import money_jar, money_text
money_text(img, "$3,650", 540, 560, 160)
money_jar(img, 540, FLOOR, 330, 520, fill=.8)
a = doodle(img, 900, FLOOR, .85, outfit="hoodie", mood="shocked", arms=("up", "up"), look=-.5, seed=int(c.t * 6))
doodle_marks(img, a["head"], a["head_r"], "excited")
```

`doodle` is the base character: big round head, stick legs, `outfit` (hoodie, tie, tshirt) with `color`, `arms`
(down, hip, up, hold, show, offer, shrug, head, point, chin, or `(left, right)`), `mood` (happy, smile, smug, shocked,
worried, angry, sad, doubt), `look` (-1 left … 1 right) and an `extras(p, a)` hook. It returns the body points (head,
mouth, hands…) to put bubbles or objects in its hands. `doodle_marks` adds excited ticks, `?`, `!` or a sweat drop.

The same `seed` always draws the same lines. A seed that changes a few times per second (`seed=int(c.t * 6)`) makes
the lines "boil" like hand-drawn animation; keep a fixed seed for things that should stay still. Full example:
`channel_template/specs/s04_sketch.py`. Your own pieces: `with Pen(img, box, seed) as p: p.shape(...); p.stroke(...)`
(also `p.limb`, `p.hatch`, `p.clip`, `p.text`).

Everyday objects (`reels_engine.sketch.everyday`): `coffee_cup`, `burger`, `pizza_slice`, `car`, `motorbike`,
`bicycle`, `sketch_house`, `sketch_building`, `sketch_tree`, `cloud`, `sun`, `phone`, `sketch_laptop`, `tv`,
`light_bulb`, `clock`, `shopping_bag`, `shopping_cart`, `credit_card`, `coin`, `sketch_piggy_bank`, `gift_box` and
`receipt` (registry names; the `sketch_` ones avoid clashing with basic-style pieces of the same name). Things that
stand on the floor take the bottom center `(cx, base)`; floating things take their center `(cx, cy)`. Objects draw
no floor shadow; pass `shadow=True` to get the soft grey one (characters keep theirs: `doodle(..., shadow=False)` hides it).
Most take a size and a main color:

```python
from channel.props import coffee_cup, car, sketch_house, phone
sketch_house(img, 760, FLOOR, 340)
car(img, 330, FLOOR, 400, color=(214, 38, 38))
coffee_cup(img, 900, FLOOR - 200, 150)
phone(img, 540, 700, 240, ang=.1)
```

Ancient history (`reels_engine.sketch.history`): `doodle_roman`, `doodle_viking`, `doodle_pharaoh`, `doodle_greek` and
`doodle_knight`, `doodle_aztec` and `doodle_maya` dress the doodle (helmet or headdress, armor or robe, and a weapon and shield where it fits: `weapon`
= gladius, sword, axe, spear, scroll, torch, macuahuitl, corn, cacao or None; `shield=False` to drop it; same `mood`, `arms`, `look` as
`doodle`). Objects: `pyramid`, `obelisk`, `greek_column` (`broken=True` for a ruin), `temple`, `colosseum`, `castle`,
`longship`, `amphora`, `scroll`, `torch` (flickers with `t`), `crown`, `laurel_wreath`, `helmet` (viking, roman,
knight, nemes, laurel, penacho, maya), `sword` (long or gladius), `axe`, `spear`, `round_shield`, `scutum` and `heater_shield`; from Mexico: `step_pyramid`,
`sun_stone`, `olmec_head`, `stela`, `macuahuitl`, `chimalli`, `corn` and `cacao_pod` (`helmet` also has penacho and
maya).
Weapons take the grip point and `ang`, the tilt from straight up in radians. Like the other sketch objects, the
monuments draw no floor shadow unless `shadow=True`.

```python
from channel.characters import doodle_roman, doodle_viking
from channel.props import pyramid, longship
pyramid(img, 760, FLOOR - 60, 420)
doodle_roman(img, 260, FLOOR, .9, mood="angry")
doodle_viking(img, 820, FLOOR, .9, mood="happy", weapon="sword", look=-.4)
```

Sports (`reels_engine.sketch.sports`): `doodle_soccer_player` (`number`, `ball=True` for a ball at the feet),
`doodle_basketball_player`, `doodle_boxer`, `doodle_runner` (race bib, headband), `doodle_tennis_player` (racket),
`doodle_baseball_player` (cap, bat, `mitt=True`) and `doodle_referee` (`card` = yellow, red or None). Same `mood`,
`arms`, `look` as `doodle`; `color` = team color. Objects: `soccer_ball`, `basketball`, `tennis_ball`, `baseball`,
`volleyball`, `football` (or `sport_ball(kind=…)`), `tennis_racket`, `baseball_bat`, `boxing_glove`, `dumbbell`,
`kettlebell`, `sneaker`, `whistle`, `stopwatch`, `cone`, `skateboard`, `jersey` (number and name), `trophy`,
`sport_medal` (`place` 1, 2 or 3), `podium` (returns where each winner stands), `soccer_goal`, `basketball_hoop`
(returns the rim center), `scoreboard` and `finish_flag` (flutters with `wave`). No floor shadows unless `shadow=True`.

```python
from channel.characters import doodle_runner
from channel.props import podium
tops = podium(img, 540, FLOOR, 720)
doodle_runner(img, *tops[1], .6, arms=("up", "up"), number=1)
```

1800s and early 1900s (`reels_engine.sketch.modern`): the doodle as `doodle_sultan` (robe, cloak, turban, beard),
`doodle_admiral` (navy coat, officer's cap), `doodle_sailor` (`hurt=True` adds a bandage) and `doodle_guard` (robe,
fez, `rifle`); `palace` (seaside, `flag` = how high it flies, `burn` 0…1 = scorch and flames), `warship` (facing left,
`flash` = gun firing, `sink` 0…1, `color=WHITE` = royal yacht), `flagpole` (`flag` height, kinds plain / cross /
tricolor), `flame`, `blast`, `smoke` and `map_pin`; background `seaside_bg` (shore on the left, sea from `SEA_Y`).

```python
from reels_engine.sketch.modern import seaside_bg, palace, warship, SEA_Y
bg = seaside_bg()
palace(bg, 270, SEA_Y + 20, 450, burn=.6, t=c.t)
warship(bg, 800, 1200, 420, flash=1, t=c.t)
```

Economy and personal finance (`reels_engine.sketch.finance`): `bank`, `safe` (`open=True` shows the money), `atm`,
`cash_register`, `calculator`, `gold_bars`, `money_bag`, `money_tree`, `salary_envelope`, `price_tag`,
`percent_badge`, `balance_scale` (`tilt`, returns the pans), `hourglass` (`t` = sand fallen), `line_chart` and
`candle_chart` (up or down with `values` / `trend`), `pie_chart` (`parts`, `labels`), `gauge` (credit score, `value`
0…1), `contract` (`title`, `stamp`), `ball_and_chain` (debt; `to` = where the chain ends, e.g. a foot),
`umbrella` (emergency fund), `goal_thermometer` (`fill`, `label`), `padlock`, `magnifier`, `rocket` and `balloon`
(inflation, bubbles). They go well with the money props and the everyday `coin`, `credit_card`, `piggy_bank` and
`receipt`.

```python
from channel.characters import doodle
from channel.props import pie_chart, goal_thermometer, calculator
pie_chart(img, 300, 300, 190, (50, 30, 20), labels=("50%", "30%", "20%"))
goal_thermometer(img, 870, FLOOR - 40, 520, fill=.7, label="$5,000")
a = doodle(img, 560, FLOOR, .85, outfit="tie", mood="smug", arms=("hip", "point"))
calculator(img, *a["hand_l"], 140)
```

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

## Scheduling videos

`python3 -m channel.publish` uploads a finished video to YouTube and/or a Facebook Page with a publish date. The
network keeps it and publishes it on its own at that time (nothing has to stay running), like scheduling it by hand.

```
python3 -m channel.publish /tmp/my_channel_out/s01_savings.mp4 "2026-10-25 19:00" \
    --title "How much you really save" --description "#savings #money" [--to youtube,facebook] [--tz America/Lima]
python3 -m channel.publish status        # which networks are connected
```

- The time is in `Channel.timezone` (for example `"America/Lima"`), or the machine's zone when it's empty.
- Without `--to` it goes to every connected network. It prints the link of each video, or why one failed.
- YouTube: uploaded as private with a publish date; it shows as "Scheduled" in YouTube Studio. Vertical videos up to
  3 minutes become Shorts. Default limit: about 6 uploads a day per Google project.
- Facebook: published as a **reel** (3 to 90 seconds) between 15 minutes and 29 days ahead; up to 30 a day per Page.
  The title and description go together as the reel's text.
- Only the Python standard library is used (no extra packages). Hosts it needs: `oauth2.googleapis.com`,
  `www.googleapis.com`, `graph.facebook.com`, `rupload.facebook.com`.

### Connecting the accounts (once per channel)

Credentials never go into the repo. `setup` saves them in `~/.config/reels-engine/<channel>/` and prints a JSON value;
to use them on another machine or in a cloud session, store that value in the environment variable (secret)
`REELS_<CHANNEL>_YOUTUBE` / `REELS_<CHANNEL>_FACEBOOK` (channel name in capitals, e.g. `REELS_MY_CHANNEL_YOUTUBE`), or
`REELS_YOUTUBE` / `REELS_FACEBOOK` for all channels.

**YouTube** (one Google project can serve every channel):
1. In [Google Cloud Console](https://console.cloud.google.com/) create a project and enable **YouTube Data API v3**.
2. *Google Auth Platform → Branding*: fill in the app name and your email. *Audience*: External, then
   **Publish app** (in "Testing" the access expires every 7 days). Google will warn "unverified app" when you
   connect: that's expected for personal use.
3. *Clients → Create client → TVs and Limited Input devices*. Copy the client id and secret.
4. `python3 -m channel.publish setup youtube CLIENT_ID CLIENT_SECRET`, open the link it shows, type the code and
   choose the Google account of the YouTube channel.
5. **Important:** Google keeps every video uploaded by a new, unaudited project private (it never goes public, even on
   its date). Request the free audit once with the
   [YouTube API Services audit form](https://support.google.com/youtube/contact/yt_api_form) ("personal use, I
   upload my own channel's videos"). Until it's approved, use a test channel or schedule by hand.

**Facebook Page:**
1. In [Meta for Developers](https://developers.facebook.com/apps/) create an app (type *Business*), with yourself as
   admin. It can stay in development mode: it's only used with your own Pages, so no app review is needed.
2. In *Graph API Explorer* choose the app, *Get User Access Token* with the permissions `pages_show_list`,
   `pages_read_engagement` and `pages_manage_posts`, and copy the token. The app id and secret are in
   *App settings → Basic*.
3. `python3 -m channel.publish setup facebook APP_ID APP_SECRET USER_TOKEN ["Page name"]`. It turns the token into a
   Page token that doesn't expire (it stops working if you change your Facebook password or remove the app).

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

## Rendering speed

- **Parts are reused.** Videos are drawn in parts of up to 4 s (never across two scenes) that are kept in
  `OUTDIR/.parts/<name>_<command>/`. The next render of the same spec only redraws the parts whose scene function,
  timing or shared code (the rest of the spec, the channel's modules, the engine, the `Channel` settings) changed;
  editing one scene redraws only that scene. Add `--fresh` to draw everything again (for example after changing an
  image file a spec loads).
- **Sketch pieces are remembered.** With a fixed seed a sketch piece called again with the same arguments pastes the
  layers it drew the first time instead of drawing them again (pixel-identical). Every public piece in
  `reels_engine.sketch` does it; wrap a channel's own sketch pieces with `@cached` (from `reels_engine.sketch`) to get
  the same, as long as they only draw through `Pen`. `REELS_PIECE_CACHE=0` turns it off and
  `REELS_PIECE_CACHE_MB` sets its memory per process (default 300).
- **`draft`** renders a review video at 15 frames/s and half size, about half the drawing work.

## Publishing a new engine version

1. Change the code and test it with the template (`cd channel_template && python3 -m channel.produce specs/s01_savings.py check`)
   and with at least one real channel (preview + check of all its specs, comparing against the previous frames).
2. Bump `version` in `pyproject.toml` and `reels_engine/__init__.py`, and note the change below.
3. Commit, tag and push: `git tag v0.5.0 && git push origin main v0.5.0` (or create a GitHub release with tag `v0.5.0`;
   the `v` matters).
4. In each channel, change the tag in `requirements.txt` and reinstall (`pip install -r requirements.txt`).

Versions are never rewritten: if something goes wrong, publish another one.

## Versions

- **v0.12.0** — 1800s and early 1900s pieces in the sketch style (`reels_engine.sketch.modern`): sultan, admiral,
  sailor and palace guard, seaside palace (can burn), steam warship (fires, sinks), flagpole, fire, explosion, smoke,
  map pin and a seaside background. Nothing else changes: existing frames are identical.
- **v0.11.0** — Faster renders: parts of the video are reused between renders when their scene didn't change, sketch
  pieces are remembered instead of redrawn (about 2x faster drawing on sketch videos), and a new `draft` command.
  Nothing else changes: existing frames are identical.
- **v0.10.0** — Economy and personal finance pieces in the sketch style (`reels_engine.sketch.finance`): bank,
  safe, ATM, cash register, calculator, gold bars, money bag and tree, charts (line, candlestick, pie), score gauge,
  contract, debt ball and chain, goal thermometer and more. Nothing else changes: existing frames are identical.
- **v0.9.0** — Ancient history in the sketch style (`reels_engine.sketch.history`): monuments, longship, weapons,
  shields, helmets and the doodle dressed as a Roman, viking, pharaoh, Greek or knight; Aztecs and Maya (step pyramid,
  Sun Stone, Olmec head, stela, macuahuitl, chimalli, maize, cacao, Aztec warrior and Maya noble). Sports
  (`reels_engine.sketch.sports`): balls, gear, trophy, medals, podium, goal, hoop, scoreboard and the doodle as soccer
  player, basketball player, boxer, runner, tennis player, baseball player or referee. `doodle` gets two new hooks,
  `dress` and `hat`. Nothing else changes: existing frames are identical.
- **v0.8.0** — Sketch-style objects no longer draw a floor shadow by default; `shadow=True` brings it back
  (`money_jar` and the everyday objects that stand on the floor). Frames with those objects change (the grey ellipse
  under them is gone); the basic and cartoon styles and the `doodle` character are unchanged.
- **v0.7.0** — Everyday objects in the sketch style (`reels_engine.sketch.everyday`): food, vehicles, house,
  building, tree, cloud, sun, gadgets, shopping and money things (see "Styles"). Nothing else changes: existing
  frames are identical.
- **v0.6.0** — Sketch style (`reels_engine.sketch`): `Pen` (wobbly tapered strokes, loose outlines, hatching),
  base character `doodle` (outfits, moods, arm poses, `doodle_marks`) and money/school pieces. New `Channel.sketch_ink`
  and `Channel.sketch_font`, new example `s04_sketch.py`. Nothing else changes: existing frames are identical.
- **v0.5.0** — `reels_engine.publish` / `python3 -m channel.publish`: schedules a finished video on YouTube and a
  Facebook Page at a date and time (see "Scheduling videos"). New `Channel.timezone`. Nothing else changes: existing
  frames are identical.
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
