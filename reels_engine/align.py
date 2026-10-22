"""Sincronización sin transcripción: detecta pausas en la voz (ffmpeg) y reparte
el tiempo de cada línea según su número de palabras, ajustando al inicio de habla más cercano."""
import re, subprocess

def speech_segments(path, db=-35, min_sil=0.18):
    err = subprocess.run(["ffmpeg", "-i", path, "-af", f"silencedetect=noise={db}dB:d={min_sil}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    dur = float(re.search(r"Duration: (\d+):(\d+):([\d.]+)", err).groups()[2]) + 60 * float(re.search(r"Duration: (\d+):(\d+)", err).groups()[1])
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    segs, cur = [], 0.0
    for s, e in zip(starts, ends + [dur] * (len(starts) - len(ends))):
        if s > cur + 0.05: segs.append((cur, s))
        cur = e
    if cur < dur - 0.05: segs.append((cur, dur))
    return segs, dur

def nwords(text):
    return max(1, len(re.findall(r"\w+", text)))

def line_starts(path, lines, snap=0.8):
    """lines: textos hablados. Devuelve (inicios_reales, duración_audio)."""
    segs, dur = speech_segments(path)
    total = sum(b - a for a, b in segs)
    w = [nwords(l) for l in lines]; W = sum(w)
    def time_at(frac):
        target = frac * total; acc = 0.0
        for a, b in segs:
            if acc + (b - a) >= target: return a + (target - acc)
            acc += b - a
        return segs[-1][1]
    seg_starts = [a for a, b in segs]
    out, cum = [], 0
    for i, wi in enumerate(w):
        t = time_at(cum / W) if i else segs[0][0]
        near = min(seg_starts, key=lambda s: abs(s - t))
        if abs(near - t) <= snap: t = near
        if out and t <= out[-1] + 0.3: t = out[-1] + 0.3
        out.append(t); cum += wi
    return out, dur
