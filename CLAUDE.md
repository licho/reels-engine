# reels-engine — guía para sesiones

Motor compartido por varios canales de reels de Luis (Datos que Asustan `licho/datos-asustan-videos`, pixel art y otros).
Dueño: Luis. **Respóndele en español, con explicaciones sencillas (sin jerga técnica).**

## Reglas
- **No romper canales.** Los canales fijan una versión (`@vX.Y.Z`). Cualquier cambio que altere cómo se ve un cuadro
  existente es un cambio de versión mayor y hay que avisarle a Luis. Antes de etiquetar, compara cuadros de los specs de
  Datos que Asustan contra la versión anterior (preview + check de todos los specs; diferencia de píxeles ≈ 0).
- **Nada propio de un canal aquí**: ni terror, ni marcas, ni textos o piezas de un solo canal. Lo que cambia entre
  canales va en `Channel` (`reels_engine/config.py`); las piezas de un canal viven en el repo del canal.
- Las piezas nuevas genéricas van en `muebles.py`, `exterior.py`, `pantallas.py` o `humanos.py` (estilo básico: reciben
  `d`, contorno negro) o en `caricatura/` (estilo caricatura: reciben `img`, dibujan con `Pincel` y tinta `INK`). Siempre
  con docstring de una línea y registradas en `registry.py`. Los estilos no se mezclan dentro de una pieza.
- Todo módulo que lea la configuración lo hace al importarse (`_cfg = current()`), por eso `configure()` va primero.
- Commits en español. Versiones: ver "Publicar una versión nueva" en `README.md`.

## Probar
```
pip install -e ".[audio]"
cd plantilla_canal && python3 -m canal.produce specs/s01_ahorro.py check && python3 -m canal.produce specs/s01_ahorro.py preview 1 4 7 9
```
