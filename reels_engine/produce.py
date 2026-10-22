"""Produces a video from a specification file (spec).

Usage:
  python3 -m channel.produce SPEC.py text             -> text for the voice (ElevenLabs)
  python3 -m channel.produce SPEC.py preview 1.5 8 20 -> sheet with those frames (nominal times)
  python3 -m channel.produce SPEC.py sheet            -> review sheet (1 frame every 2 s) BEFORE rendering the video (~3 s)
  python3 -m channel.produce SPEC.py check            -> quick check (captions, edges, texts)
  python3 -m channel.produce SPEC.py check-contrast   -> check + contrast (slow, only on request)
  python3 -m channel.produce SPEC.py silent           -> video without voice (music + effects)
  python3 -m channel.produce SPEC.py final VOICE.mp3  -> final video synced to the voice
  python3 -m channel.produce SPEC.py draft [VOICE.mp3] -> quick review video: 15 frames/s, half size (~3x faster)
Every render also writes a verification sheet (1 frame every 2 s).
Videos are drawn in parts of 4 s that are kept in OUTDIR/.parts/: the next render of the same spec only redraws the
parts whose scene (or the shared code, or the timing) changed. Add --fresh to draw everything again.
The old Spanish command names (texto, hoja, check-contraste, sinvoz) still work and keep their old file names."""
import importlib.util, os, sys, subprocess, math
import numpy as np
from PIL import Image, ImageDraw
from .core import W, H, rich_caption, CAP_Y
from .config import current as _current
from .audio import Mix
from . import align, check

_cfg = _current()
FPS = _cfg.fps; WPS = _cfg.wps; GAP = _cfg.gap

class Ctx:
    pass

def load(spec_path):
    spec_path = os.path.abspath(spec_path)
    sp = importlib.util.spec_from_file_location("spec", spec_path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    lines = [L if len(L) == 3 else (L[0], L[1], L[1]) for L in m.LINES]
    m.LINES = lines
    st, t = [], 0.0
    for tag, spoken, cap in lines:
        st.append(t); t += align.nwords(spoken) / WPS + GAP
    m.NSTART = st; m.NEND = t + getattr(m, "END", _cfg.end)
    import inspect
    scenes = {fn for _, fn in m.SCENES}
    for k, v in list(vars(m).items()):
        if inspect.isfunction(v) and v not in scenes and not k.startswith("_"):
            try: first = next(iter(inspect.signature(v).parameters), "")
            except (TypeError, ValueError): continue
            if first in ("d", "img", "dd"): setattr(m, k, check.element_wrap(v, k))
    return m

def voice_text(m):
    return " ".join((f"[{tag}] " if tag else "") + spoken for tag, spoken, cap in m.LINES)

def make_warp(m, voice=None):
    if not voice:
        return (lambda T: T), (lambda v: v), m.NEND
    real, dur = align.line_starts(voice, [s for _, s, _ in m.LINES])
    end_real = dur + getattr(m, "END", _cfg.end)
    TK = np.array([0.0] + real[1:] + [dur, end_real]); VK = np.array([0.0] + m.NSTART[1:] + [m.NSTART[-1] + (dur - real[-1]), m.NEND])
    order = np.argsort(TK); TK, VK = TK[order], VK[order]
    return (lambda T: float(np.interp(T, TK, VK))), (lambda v: float(np.interp(v, VK, TK))), end_real

def scene_at(m, v):
    cur = None
    for i, (li, fn) in enumerate(m.SCENES):
        start = m.NSTART[li]
        if v >= start: cur = (fn, start, (m.NSTART[m.SCENES[i + 1][0]] if i + 1 < len(m.SCENES) else m.NEND))
    return cur

def render_frame(m, v, t, rec=None):
    fn, s0, s1 = scene_at(m, v)
    c = Ctx(); c.v = v; c.t = t; c.lt = v - s0; c.dur = s1 - s0; c.shake = 0
    c.at = lambda i: m.NSTART[i] - s0          # start of line i relative to the scene
    c.line, c.cap, c.cap_lt = 0, "", 0.0         # current line (for scenes that draw their own caption, e.g. pixel art)
    for i, (tag, spoken, cap) in enumerate(m.LINES):
        e = m.NSTART[i + 1] if i + 1 < len(m.LINES) else m.NEND
        if m.NSTART[i] <= v < e: c.line, c.cap, c.cap_lt = i, cap, v - m.NSTART[i]
    from .core import say_reset
    say_reset()
    img = fn(c)
    d = ImageDraw.Draw(img)
    if rec: rec.tag = "caption"
    if getattr(m, "VIGNETTE", _cfg.vignette) and getattr(m, "CAPTIONS", _cfg.captions):        # standard vignette (not in pixel art)
        from .motion import vignette
        d = vignette(img, getattr(m, "VIGNETTE", _cfg.vignette))
    if getattr(m, "CAPTIONS", _cfg.captions) and c.cap:
        if getattr(m, "CAPTION_STYLE", _cfg.caption_style) == "words":                  # standard: word by word
            from .motion import caption_words
            caption_words(d, c.cap, c.cap_lt)
        else:
            rich_caption(d, c.cap, y=CAP_Y, appear=c.cap_lt / 0.25)
    arr = np.asarray(img)
    if c.shake: arr = np.roll(arr, int(math.sin(t * 60) * c.shake), axis=1)
    return arr

def build_audio(m, out_wav, T_of_v, v_of_T, dur, voice=None):
    mx = Mix(dur, T_of_v); mx.v_of_T = v_of_T
    mus = getattr(m, "MUSIC", _cfg.music)
    quiet = [(m.NSTART[a], m.NSTART[b] if b < len(m.LINES) else m.NEND) for a, b in mus[1]]
    mx.music(mus[0], quiet=quiet, loud_from=(m.NSTART[mus[2]] if mus[2] is not None else None))
    for li, off, name, *kw in getattr(m, "SFX", []):
        mx.fx(name, m.NSTART[li] + off, **(kw[0] if kw else {}))
    for (li, fn) in m.SCENES[1:]:
        mx.whoosh(m.NSTART[li])
    mx.render(out_wav, voice)

_JOB = {}
CHUNK = 120                                      # frames per part (4 s): the unit that is drawn in parallel and reused

def _render_part(args):
    """Child process: draws a range of frames and encodes it into its own file."""
    i0, i1, path, preset, fps, size = args
    m, v_of_T = _JOB["m"], _JOB["v_of_T"]
    scale = ["-vf", f"scale={size[0]}:{size[1]}:flags=area"] if size != (W, H) else []
    tmp = path + ".tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                          *scale, "-c:v", "libx264", "-preset", preset, "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(i0, i1):
        T = i / fps
        p.stdin.write(render_frame(m, v_of_T(T), T).tobytes())
    p.stdin.close(); p.wait()
    os.replace(tmp, path)                        # only finished parts land in the cache
    return path

def _code_hash(m):
    """Hash of the code a frame can depend on: the whole engine plus every module loaded from the channel's repo or
    the spec's folder (the spec itself is hashed scene by scene in _scene_keys)."""
    import hashlib, glob
    from dataclasses import replace
    h = hashlib.sha1(repr(replace(_cfg, root="", outdir="", workers=0, catalog_paths={})).encode())   # paths don't change frames
    real = os.path.realpath
    eng = real(os.path.dirname(__file__))
    files = {real(f) for f in glob.glob(os.path.join(eng, "**", "*.py"), recursive=True)}
    roots = [real(_cfg.root), real(os.path.dirname(m.__file__))]
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if f and f.endswith(".py") and any(real(f).startswith(r + os.sep) for r in roots): files.add(real(f))
    files.discard(real(m.__file__))
    for f in sorted(files): h.update(open(f, "rb").read())
    return h.hexdigest()

def _scene_keys(m):
    """One fingerprint per scene: the scene function's own code plus everything else in the spec (helpers, LINES…),
    so editing one scene only invalidates that scene."""
    import ast, hashlib
    tree = ast.parse(open(m.__file__, encoding="utf-8").read())
    names = {fn.__name__ for _, fn in m.SCENES if getattr(fn, "__module__", None) == m.__name__}
    own = {n.name: ast.dump(n) for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names}
    tree.body = [n for n in tree.body if not (isinstance(n, ast.FunctionDef) and n.name in own)]
    rest = ast.dump(tree)
    return [hashlib.sha1((rest + own.get(fn.__name__, fn.__name__)).encode()).hexdigest() for _, fn in m.SCENES]

def _parts(m, v_of_T, n, fps):
    """Frame ranges [(scene index, i0, i1)]: never across two scenes and at most CHUNK frames long."""
    starts = [m.NSTART[li] for li, _ in m.SCENES]
    def scene(i):
        v = v_of_T(i / fps); k = 0
        while k + 1 < len(starts) and v >= starts[k + 1]: k += 1
        return k
    out, i0 = [], 0
    ks = [scene(i) for i in range(n)]
    for i in range(1, n + 1):
        if i == n or ks[i] != ks[i0] or i - i0 >= CHUNK: out.append((ks[i0], i0, i)); i0 = i
    return out

def encode(m, out_mp4, v_of_T, dur, wav, preset="medium", fps=None, size=None, cache=None):
    """Draws and encodes using every core (parts of up to CHUNK frames), then joins the parts.
    cache = folder where finished parts are kept: a part whose scene, timing and code didn't change is reused."""
    import multiprocessing as mp, hashlib
    fps = fps or FPS; size = tuple(size or (W, H))
    n = int(dur * fps); k = max(1, min(os.cpu_count() or 1, _cfg.workers))
    _JOB.update(m=m, v_of_T=v_of_T)
    parts = _parts(m, v_of_T, n, fps)
    folder = cache or os.path.dirname(os.path.abspath(out_mp4))
    os.makedirs(folder, exist_ok=True)
    if cache:
        code, keys = _code_hash(m), _scene_keys(m)
        def path(sc, i0, i1):
            frames = np.array([(i / fps, v_of_T(i / fps)) for i in range(i0, i1)], dtype=np.float64).tobytes()
            h = hashlib.sha1(f"{code}{keys[sc]}{preset}{fps}{size}".encode() + frames).hexdigest()[:20]
            return os.path.join(folder, f"{h}.mp4")
    else:
        path = lambda sc, i0, i1: f"{out_mp4}.part{i0}.mp4"
    jobs = [(i0, i1, path(sc, i0, i1), preset, fps, size) for sc, i0, i1 in parts]
    todo = [j for j in jobs if not (cache and os.path.exists(j[2]))]
    if cache: print(f"Parts: {len(jobs) - len(todo)} of {len(jobs)} reused, {len(todo)} to draw")
    todo.sort(key=lambda j: j[0] - j[1])                                # longest first: better use of the cores
    if todo:
        with mp.get_context("fork").Pool(min(k, len(todo))) as pool: pool.map(_render_part, todo, chunksize=1)
    paths = [j[2] for j in jobs]
    lst = out_mp4 + ".list.txt"
    open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in paths))
    tmp = out_mp4 + ".v.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", tmp], check=True)
    os.remove(lst)
    if cache:                                                           # keep only what this video uses
        for f in os.listdir(folder):
            if os.path.join(folder, f) not in paths: os.remove(os.path.join(folder, f))
    else:
        for p in paths: os.remove(p)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_mp4], check=True)
    os.remove(tmp)
    sheet = out_mp4.replace(".mp4", "_tile.png")
    cols = int(math.ceil(dur / 2 / 3))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", out_mp4, "-vf", f"fps=1/2,scale=180:320,tile={cols}x3", "-frames:v", "1", sheet])
    return sheet

def sheet_quick(m, path, step=2.0):
    """Review sheet BEFORE rendering the video: one frame every 'step' seconds (nominal time)."""
    ts = [x * step + step / 2 for x in range(int(m.NEND / step))]
    cols = math.ceil(len(ts) / 3)
    sh = Image.new("RGB", (180 * cols, 320 * 3))
    for i, t in enumerate(ts): sh.paste(Image.fromarray(render_frame(m, t, t)).resize((180, 320)), ((i % cols) * 180, (i // cols) * 320))
    sh.save(path); return path

def _fingerprint(spec_path):
    import hashlib, glob
    h = hashlib.sha1(open(spec_path, "rb").read())
    dirs = [os.path.dirname(os.path.abspath(__file__))] + [os.path.join(_cfg.root, p) for p in _cfg.code_dirs]
    for dd in dirs:
        for f in sorted(glob.glob(os.path.join(dd, "*.py"))): h.update(open(f, "rb").read())
    return h.hexdigest()

def run_check(m, per_scene=6, contrast=False):
    """Checks several frames of each scene (contrast only on request). Returns True when there are no problems."""
    total = 0
    bounds = [m.NSTART[li] for li, _ in m.SCENES] + [m.NEND]
    for k, (li, fn) in enumerate(m.SCENES):
        a, b = bounds[k], bounds[k + 1]; seen = {}; worst = {}; full = {}
        for j in range(per_scene):
            v = a + (b - a) * (j + .5) / per_scene
            rec = check.Rec(); check.ACTIVE = rec if contrast else None
            try:
                with check.recording(rec): render_frame(m, v, v, rec)
            finally: check.ACTIVE = None
            for p, bb in check.contrast_issues(rec):
                key = p.split(" blends into")[0] if "' blends into" in p else p      # one line per piece and scene
                if key not in seen: seen[key] = v; worst[key] = 0; full[key] = p
                pct = int(p.split("(")[1].split("%")[0]) if "% of its outline" in p else 0
                if pct > worst[key]: worst[key] = pct; full[key] = p
            for p, px in check.analyze(rec.items):
                seen.setdefault(p, v); worst[p] = max(worst.get(p, 0), px)
        for p, v in seen.items():
            if p in full: print(f"  [{fn.__name__} from {v:.1f}s] {full[p]}"); total += 1; continue
            print(f"  [{fn.__name__} from {v:.1f}s] {p}" + (f" (up to {worst[p]} px)" if worst[p] else "")); total += 1
    print("Automatic check:", "no problems ✔" if not total else f"{total} problem(s)")
    return total == 0

_ALIASES = {"texto": "text", "hoja": "sheet", "check-contraste": "check-contrast", "sinvoz": "silent"}   # old Spanish names

def main():
    fresh = "--fresh" in sys.argv; sys.argv = [a for a in sys.argv if a != "--fresh"]
    spec, cmd = sys.argv[1], sys.argv[2]
    old = cmd in _ALIASES; cmd = _ALIASES.get(cmd, cmd)
    m = load(spec)
    name = getattr(m, "NAME", os.path.splitext(os.path.basename(spec))[0])
    outdir = getattr(m, "OUTDIR", _cfg.outdir); os.makedirs(outdir, exist_ok=True)
    if cmd == "text":
        print(voice_text(m)); print(f"\n# words: {sum(align.nwords(s) for _, s, _ in m.LINES)}  estimated duration: {m.NEND:.0f} s"); return
    if cmd == "preview":
        ts = [float(x) for x in sys.argv[3:]]
        ims = [Image.fromarray(render_frame(m, x, x)).resize((270, 480)) for x in ts]
        sh = Image.new("RGB", (270 * min(6, len(ims)), 480 * ((len(ims) + 5) // 6)))
        for i, im in enumerate(ims): sh.paste(im, ((i % 6) * 270, (i // 6) * 480))
        p = os.path.join(outdir, f"{name}_preview.png"); sh.save(p); print(p); return
    if cmd == "sheet":
        print(sheet_quick(m, os.path.join(outdir, f"{name}_{'hoja' if old else 'sheet'}.png"))); return
    stamp_f = os.path.join(outdir, f".checked_{name}")
    if cmd in ("check", "check-contrast"):
        ok = run_check(m, contrast=cmd == "check-contrast")
        if ok and cmd == "check": open(stamp_f, "w").write(_fingerprint(spec))
        return
    voice = sys.argv[3] if cmd == "final" or (cmd == "draft" and len(sys.argv) > 3) else None
    if not (os.path.exists(stamp_f) and open(stamp_f).read() == _fingerprint(spec)):
        if run_check(m): open(stamp_f, "w").write(_fingerprint(spec))
    else:
        print("Automatic check: already checked, nothing changed since ✔")
    v_of_T, T_of_v, dur = make_warp(m, voice)
    wav = os.path.join(outdir, f"{name}.wav"); build_audio(m, wav, T_of_v, v_of_T, dur, voice)
    suffix = {"silent": "_SINVOZ" if old else "_SILENT", "draft": "_DRAFT"}.get(cmd, "")
    out = os.path.join(outdir, f"{name}{suffix}.mp4")
    parts = os.path.join(outdir, ".parts", f"{name}_{cmd}")
    if fresh and os.path.isdir(parts): import shutil; shutil.rmtree(parts)
    if cmd == "draft":
        sheet = encode(m, out, v_of_T, dur, wav, preset="ultrafast", fps=15, size=(W // 2, H // 2), cache=parts)
    else:
        sheet = encode(m, out, v_of_T, dur, wav, preset="veryfast" if cmd == "silent" else "medium", cache=parts)
    print(out); print(sheet); print(f"duration: {dur:.1f} s")

if __name__ == "__main__":
    main()
