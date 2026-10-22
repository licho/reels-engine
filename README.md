# reels-engine

Motor para producir reels verticales (1080x1920) con código: escenas dibujadas con Pillow, animación tipo GSAP,
subtítulos palabra por palabra, globos de diálogo que se acomodan solos, audio (voz + efectos + música generada),
sincronización con la voz y revisión automática de cada cuadro (subtítulos tapados, textos cortados o encimados, contraste).

Un **canal** (por ejemplo `licho/datos-asustan-videos`) es un repo aparte que instala este motor, pone su configuración
(colores, zonas, carpeta de salida…) y agrega sus propias piezas y videos.

## Instalar

Requisitos del sistema: Python 3.9+, `ffmpeg` y la fuente DejaVu Sans (`/usr/share/fonts/truetype/dejavu/`).

```
pip install "reels-engine[audio] @ git+https://github.com/licho/reels-engine@v0.1.0"
```

En el canal se fija la versión en `requirements.txt` (siempre con etiqueta, nunca `main`):

```
reels-engine[audio] @ git+https://github.com/licho/reels-engine@v0.1.0
```

`[audio]` agrega `scipy` (filtros de audio más rápidos). Sin él funciona igual, solo más lento al mezclar.

## Crear un canal nuevo desde cero

La carpeta [`plantilla_canal/`](plantilla_canal/) es un canal mínimo que funciona tal cual. Para empezar uno nuevo:

1. **Crea el repo del canal** y copia ahí el contenido de `plantilla_canal/` (la carpeta `canal/` y `specs/`).
   Agrega un `requirements.txt` con la línea de arriba e instala: `pip install -r requirements.txt`.
2. **Configura el canal** en `canal/__init__.py`. Todo es opcional; lo que no pongas toma el valor por defecto:
   ```python
   configure(Channel(
       name="finanzas",
       root=ROOT,
       outdir="/tmp/finanzas_out",           # dónde salen previews y videos
       font_bold="/ruta/a/MiFuente-Bold.ttf",
       caption_highlight=(80, 220, 120),     # color de las palabras *resaltadas*
       chip_bg=(30, 110, 210),               # color de los letreros
       vignette=0,                           # sin viñeta
       wps=2.6,                              # velocidad de lectura (palabras por segundo)
       music=("pad", [], None),              # música por defecto
   ))
   ```
   La lista completa (zonas seguras, subtítulos, umbrales de la revisión, catálogo, estilos de música extra…) está
   comentada en [`reels_engine/config.py`](reels_engine/config.py). `configure()` debe correr **antes** de importar el
   resto del motor; por eso va en el `__init__.py` del paquete del canal y cada comando del canal importa ese paquete primero.
3. **Piezas propias**: dibújalas en `canal/piezas.py` (o en varios módulos) y regístralas en `canal/props.py`,
   `canal/personajes.py` o `canal/fondos.py`, en el diccionario `MAP` (`alias -> "modulo[:nombre]"`). Los MAP empiezan
   con las piezas del motor (`registry.PROPS`, `registry.PERSONAJES`, `registry.FONDOS`) y se les suman las del canal.
4. **Primer video**: copia `specs/s01_ahorro.py`, cambia `NAME`, `LINES`, las funciones de escena, `SCENES`, `SFX` y `MUSIC`.
5. **Comandos** (desde la raíz del canal):
   ```
   python3 -m canal.produce specs/s01.py texto          # texto para la voz + duración estimada
   python3 -m canal.produce specs/s01.py hoja           # hoja de cuadros para revisar composición
   python3 -m canal.produce specs/s01.py preview 2 6 10 # cuadros sueltos (segundos)
   python3 -m canal.produce specs/s01.py check          # revisión automática
   python3 -m canal.produce specs/s01.py sinvoz         # video sin voz (música + efectos)
   python3 -m canal.produce specs/s01.py final voz.mp3  # video final sincronizado con la voz
   python3 -m canal.catalogo                            # regenera el catálogo de piezas del canal
   ```

## Qué trae el motor

| Módulo | Qué es |
|---|---|
| `config` | `Channel` (configuración del canal) y `configure()` |
| `base` | fuente `F`, colores, `lerp`/`ease`/`pop`, `chip` (letrero), `bigtext`, `rich_caption`, `xmark`, `check` |
| `core` | zonas seguras, `canvas`, `grad`, globos `bubble`/`say`, `fit_font`, `calendar`, `gauge`, `confetti`, `speedlines`, `sparkles`, `follow_btn`, `stamp` |
| `motion` | curvas (`back_out`, `elastic_out`…), `tw`, `yoyo`, `shake`, `layer`, `glow`, `radial_bg`, `space_bg`, `vignette`, `sphere_shade`, subtítulos palabra por palabra |
| `produce` | comandos texto/hoja/preview/check/sinvoz/final, render en paralelo, caché de revisión |
| `check` | revisión automática de cuadros y contraste por pieza |
| `audio`, `align` | mezcla voz + efectos + música; sincroniza la voz por silencios |
| `humanos` | personaje base `guy`, `anchors` (cabeza, boca, manos…), `medal` |
| `muebles`, `exterior`, `pantallas` | piezas neutras: muebles, reloj, ventana, casa, árbol, nubes, rayo, documentos, chat de celular, monitor, `bar_chart`, `people_grid`… |
| `registry` | las piezas del motor listas para mezclar en los `MAP` del canal |
| `lazy`, `catalogo` | catálogos con carga perezosa y generador de `CATALOGO.md` |

Formato del spec, zonas seguras y consejos de animación: ver el `CLAUDE.md` del canal Datos que Asustan, que sigue
siendo la referencia más completa.

## Dibujo (pincel)

Hoy todo se dibuja con Pillow (`brush="pil"`). La configuración ya tiene el campo `brush` para agregar más adelante un
pincel vectorial (cairo) sin romper los canales que usan Pillow: las piezas actuales seguirán funcionando igual.

## Publicar una versión nueva del motor

1. Cambia el código y prueba con la plantilla (`cd plantilla_canal && python3 -m canal.produce specs/s01_ahorro.py check`)
   y con al menos un canal real (preview + check de todos sus specs, comparando contra los cuadros de antes).
2. Sube `version` en `pyproject.toml` y `reels_engine/__init__.py`, y anota el cambio abajo.
3. Commit, etiqueta y push: `git tag v0.2.0 && git push origin main v0.2.0`.
4. En cada canal, cambia la etiqueta en `requirements.txt` y reinstala (`pip install -r requirements.txt`).

Las versiones nunca se reescriben: si algo sale mal, se publica otra.

## Versiones

- **v0.1.0** — Primera versión, separada de `licho/datos-asustan-videos` (`lib/`) sin cambiar ningún cuadro de sus videos.
