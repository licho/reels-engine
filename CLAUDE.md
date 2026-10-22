# reels-engine — guide for sessions

Engine shared by several of Luis's reel channels (Datos que Asustan `licho/datos-asustan-videos`, pixel art and others).
Owner: Luis. **Reply to him in Spanish, with simple explanations (no technical jargon).** The repo itself (code,
comments, docs, commits) is in English.

## Rules
- **Don't break channels.** Channels pin a version (`@vX.Y.Z`). Any change that alters how an existing frame looks is a
  major version change and Luis must be told. Before tagging, compare frames of the Datos que Asustan specs against the
  previous version (preview + check of every spec; pixel difference ≈ 0).
- **Old Spanish names stay working** (`muebles`, `pantallas`, `humanos`, `catalogo`, `PERSONAJES`, `FONDOS`, the
  `texto`/`hoja`/`sinvoz`/`check-contraste` commands, `chair(kind="silla"|"oficina")`): channels still use them.
  Remove them only in a major version, after updating the channels.
- **Nothing channel-specific here**: no horror, no brands, no texts or pieces for a single channel. What changes between
  channels goes in `Channel` (`reels_engine/config.py`); a channel's pieces live in the channel's repo.
- New generic pieces go in `furniture.py`, `exterior.py`, `screens.py` or `humans.py` (basic style: they take `d`, black
  outline) or in `cartoon/` (cartoon style: they take `img`, draw with `Brush` and `INK`). Always with a one-line
  docstring and registered in `registry.py`. Styles don't mix inside a piece.
- Every module that reads the configuration does it on import (`_cfg = current()`), so `configure()` goes first.
- Commits in English. Versions: see "Publishing a new engine version" in `README.md`.

## Test
```
pip install -e ".[audio]"
cd channel_template && python3 -m channel.produce specs/s01_savings.py check && python3 -m channel.produce specs/s01_savings.py preview 1 4 7 9
```
