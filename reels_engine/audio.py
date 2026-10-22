"""Mezclador único: voz + efectos + música. Reemplaza los audioNN.py."""
import subprocess, wave
import numpy as np
from .config import current as _current
SR = 44100
try:
    from scipy.signal import lfilter
    def lp(x, a): return lfilter([a], [1, -(1 - a)], x)
except Exception:
    def lp(x, a):
        y = np.empty_like(x); acc = 0.0
        for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
        return y

class Mix:
    def __init__(self, dur, T_of_v=lambda v: v, seed=11):
        self.N = int(SR * dur); self.out = np.zeros(self.N); self.M = T_of_v; self.dur = dur
        self.rng = np.random.default_rng(seed)
    # -- primitivas
    def env(self, n, a=0.005, r=None):
        e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
        if r: e *= np.exp(-np.arange(n) / SR / r)
        return e
    def tone(self, f, d, w='sin'):
        n = int(d * SR); ff = np.broadcast_to(f, (n,)) if np.ndim(f) else np.full(n, f)
        ph = 2 * np.pi * np.cumsum(ff) / SR
        return {'sin': np.sin(ph), 'saw': 2 * ((ph / (2 * np.pi)) % 1) - 1, 'sq': np.sign(np.sin(ph))}[w]
    def noise(self, d): return self.rng.standard_normal(int(d * SR))
    def add(self, st, sig, g=1.0, raw=False):
        i = int((st if raw else self.M(st)) * SR); j = min(self.N, i + len(sig))
        if 0 <= i < self.N: self.out[i:j] += sig[:j - i] * g
    # -- efectos (st en tiempo nominal v)
    def pop(self, st, g=0.3, f0=300, f1=900, d=0.1): self.add(st, self.tone(np.linspace(f0, f1, int(d * SR)), d) * self.env(int(d * SR), .002, d / 2), g)
    def ding(self, st, g=0.2, f=1568): self.add(st, (self.tone(f, .4) + .5 * self.tone(f * 1.335, .4)) * self.env(int(.4 * SR), .002, .12), g)
    def whoosh(self, st, g=0.35): self.add(st - .15, lp(self.noise(.35), .08) * np.sin(np.linspace(0, np.pi, int(.35 * SR))), g)
    def buzzer(self, st, g=0.3): self.add(st, lp(self.tone(140, .35, 'sq'), .3) * self.env(int(.35 * SR), .005, .2), g)
    def boing(self, st, g=0.3):
        d = .5; f = 180 + 60 * np.sin(np.linspace(0, 25, int(d * SR))) * np.exp(-np.linspace(0, 4, int(d * SR)))
        self.add(st, self.tone(f, d) * self.env(int(d * SR), .002, .2), g)
    def thud(self, st, g=0.9): self.add(st, self.tone(np.linspace(140, 45, int(.4 * SR)), .4) * self.env(int(.4 * SR), .002, .1), g)
    def sting(self, st, g=0.4, d=2.0):
        s = sum(self.tone(f, d, 'saw') for f in (55, 58.3, 110.4, 116.7)); self.add(st, lp(s, .07) * self.env(int(d * SR), .01, .8), g)
    def jingle(self, st, g=0.12, notes=(523, 659, 784, 1047), gap=0.12):
        for k, f in enumerate(notes): self.add(self.M(st) + k * gap, self.tone(f, .22, 'sq') * self.env(int(.22 * SR), .005, .1), g, raw=True)
    def sadtrom(self, st, g=0.12):
        for k, f in enumerate((392, 370, 349, 330, 262)): self.add(self.M(st) + k * .25, self.tone(f, .24, 'sq') * self.env(int(.24 * SR), .005, .15), g, raw=True)
    def rumble(self, st, d=2.0, g=0.8): self.add(st, lp(self.noise(d), .02) * np.linspace(1, 0, int(d * SR)), g)
    def splat(self, st, g=0.6): self.add(st, lp(self.noise(.25), .2) * self.env(int(.25 * SR), .001, .06), g)
    def skid(self, st, g=0.5):
        n = int(SR); self.add(st, lp(self.noise(1.0), .3) * np.linspace(1, 0, n) * (.6 + .4 * np.sin(np.arange(n) / SR * 2 * np.pi * 30)), g)
    def alarm(self, st, n=10, g=0.07):
        for k in range(n): self.add(self.M(st) + k * .18, self.tone(2200, .09, 'sq') * self.env(int(.09 * SR), .002, .05), g, raw=True)
    def buzz(self, a, b, g=0.06, f0=220):
        t0, t1 = self.M(a), self.M(b); n = int((t1 - t0) * SR); tt = np.arange(n) / SR
        f = f0 + 30 * np.sin(2 * np.pi * 7 * tt); s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (.6 + .4 * np.sin(2 * np.pi * 3 * tt))
        self.add(t0, lp(s, .25), g, raw=True)
    def whine(self, st, dur=1.5, g=0.07, f0=620):
        """Zumbido de mosquito (agudo con vibrato), dur en segundos reales."""
        n = int(dur * SR); tt = np.arange(n) / SR
        f = f0 + 40 * np.sin(2 * np.pi * 9 * tt) + 25 * np.sin(2 * np.pi * 1.3 * tt)
        ph = 2 * np.pi * np.cumsum(f) / SR
        sig = (np.sin(ph) + .5 * np.sin(2 * ph) + .25 * np.sin(3 * ph)) * np.minimum(1, np.minimum(tt / .15, (dur - tt) / .3))
        self.add(st, sig, g)
    def fx(self, name, st, **kw): getattr(self, name)(st, **kw)
    # -- música
    def music(self, style="bass", quiet=(), loud_from=None):
        """style: bass | chiptune | pad | waltz. quiet=[(v0,v1)] silencios; loud_from=v sube volumen al final."""
        v_of_T = None
        sty = {
            "bass": dict(bpm=110, bass=[73.4, 0, 73.4, 87.3, 98, 0, 87.3, 73.4], mel=None, wave='saw'),
            "chiptune": dict(bpm=128, bass=[55, 55, 65.4, 65.4, 49, 49, 61.7, 61.7], mel=[220, 0, 261.6, 0, 329.6, 293.7, 261.6, 0, 196, 0, 246.9, 0, 293.7, 261.6, 246.9, 0], wave='sq'),
            "waltz": dict(bpm=100, bass=[98, 98, 130.8, 130.8, 87.3, 87.3, 98, 98], mel=[392, 0, 440, 392, 349.2, 0, 329.6, 0, 293.7, 0, 329.6, 349.2, 392, 0, 0, 0], wave='sq'),
        }
        sty.update(_current().music_styles)
        if style == "pad":
            chords = [(110, 164.8, 220, 261.6), (98, 146.8, 196, 246.9), (87.3, 130.8, 174.6, 220), (98, 146.8, 196, 233.1)]
            for k, st in enumerate(np.arange(0, self.dur, 4.0)):
                n = int(5.5 * SR); tt = np.arange(n) / SR; e = np.minimum(1, tt / 1.2) * np.minimum(1, (5.5 - tt) / 1.5)
                sig = sum(np.sin(2 * np.pi * f * tt) * (.5 if i == 0 else .3) for i, f in enumerate(chords[k % 4]))
                self.add(st, sig * e, .09, raw=True)
            return
        s = sty[style]; step = 60 / s["bpm"] / 2
        inv = getattr(self, "v_of_T", None)
        for k, st in enumerate(np.arange(0, self.dur - 1, step)):
            v = inv(st) if inv else st
            if any(a <= v < b for a, b in quiet): continue
            g = .8 if (loud_from is not None and v >= loud_from) else .5
            f = s["bass"][k % 8]
            if f and k % 2 == 0: self.add(st, lp(self.tone(f, step * 1.8, s["wave"]), .15) * self.env(int(step * 1.8 * SR), .005, .15), .10 * g, raw=True)
            if s["mel"]:
                m = s["mel"][k % 16]
                if m and k % 32 < 28: self.add(st, self.tone(m * 2, step * .8, 'sq') * self.env(int(step * .8 * SR), .002, step * .6), .045 * g, raw=True)
            if k % 4 == 0: self.add(st, np.sin(2 * np.pi * np.cumsum(np.linspace(140, 45, int(.1 * SR))) / SR) * np.exp(-np.arange(int(.1 * SR)) / SR / .04), .25 * g, raw=True)
            if k % 4 == 2: self.add(st, lp(self.noise(.04), .6) * np.exp(-np.arange(int(.04 * SR)) / SR / .01), .10 * g, raw=True)
    # -- salida
    def render(self, out_wav, voice_path=None):
        sfx = self.out / (np.max(np.abs(self.out)) or 1)
        if voice_path:
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", voice_path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
            vo = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
            voice = np.zeros(self.N); voice[:min(self.N, len(vo))] = vo[:self.N]; voice /= (np.max(np.abs(voice)) or 1); voice *= .95
            w = int(.05 * SR); e = np.sqrt(np.convolve(voice ** 2, np.ones(w) / w, mode="same"))
            on = (e > .02).astype(float); k = int(.25 * SR); on = np.clip(np.convolve(on, np.ones(k) / k, mode="same") * 1.5, 0, 1)
            mix = voice + sfx * .42 * (1 - .6 * on)
        else:
            mix = sfx * .6
        mix = mix / (np.max(np.abs(mix)) or 1) * .95
        fade = np.ones(self.N); fade[-int(.5 * SR):] = np.linspace(1, 0, int(.5 * SR)); mix *= fade
        with wave.open(out_wav, 'wb') as wv:
            wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((mix * 32767).astype(np.int16).tobytes())
