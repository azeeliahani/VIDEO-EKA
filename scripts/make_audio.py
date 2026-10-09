"""Synthesises the background music and sound effects for the EKA explainer.

Everything is generated from scratch with numpy (no samples), so it is royalty-free.
Timings mirror src/video.html (96 BPM, 1 bar = 2.5 s, scenes change on bar lines).

Outputs (output/):
  music.wav  - music bed only
  sfx.wav    - sound effects only
  mix.wav    - music + sfx, levelled to leave headroom for a voice-over
"""
import wave
from pathlib import Path

import numpy as np

SR = 44100
DUR = 60.0
N = int(SR * DUR)
BPM = 96
BEAT = 60 / BPM
BAR = BEAT * 4
EIGHTH = BEAT / 2
OUT = Path(__file__).resolve().parent.parent / "output"
rs = np.random.default_rng(42)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(d):
    return np.arange(int(d * SR)) / SR


def add(buf, sig, t0, gain=1.0, pan=0.0):
    """Mix a mono signal into a stereo buffer at time t0 (s) with equal-power pan (-1..1)."""
    i = int(round(t0 * SR))
    if i >= buf.shape[1] or i + len(sig) <= 0:
        return
    s = sig[max(0, -i):]
    i = max(0, i)
    s = s[: buf.shape[1] - i]
    a = (pan + 1) * np.pi / 4
    buf[0, i:i + len(s)] += s * gain * np.cos(a)
    buf[1, i:i + len(s)] += s * gain * np.sin(a)


def biquad_bp_sweep(x, f0, f1, q=2.0, curve=1.0):
    """Band-pass x with a centre frequency gliding f0 -> f1 (exponential)."""
    n = len(x)
    y = np.zeros(n)
    x1 = x2 = y1 = y2 = 0.0
    p = np.linspace(0, 1, n) ** curve
    fc = f0 * (f1 / f0) ** p
    for k in range(n):
        w = 2 * np.pi * fc[k] / SR
        al = np.sin(w) / (2 * q)
        b0, b2, a0, a1, a2 = al, -al, 1 + al, -2 * np.cos(w), 1 - al
        yk = (b0 * x[k] + b2 * x2 - a1 * y1 - a2 * y2) / a0
        x2, x1, y2, y1 = x1, x[k], y1, yk
        y[k] = yk
    return y


def hp_noise(d, cutoff):
    n = rs.standard_normal(int(d * SR))
    F = np.fft.rfft(n)
    f = np.fft.rfftfreq(len(n), 1 / SR)
    F[f < cutoff] = 0
    return np.fft.irfft(F, len(n))


def band_noise(d, lo, hi):
    n = rs.standard_normal(int(d * SR))
    F = np.fft.rfft(n)
    f = np.fft.rfftfreq(len(n), 1 / SR)
    F[(f < lo) | (f > hi)] = 0
    out = np.fft.irfft(F, len(n))
    return out / (np.abs(out).max() + 1e-9)


def fade(sig, a=0.005, r=0.02):
    n = len(sig)
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return sig * e


# ----------------------------------------------------------------------------- instruments
def kick():
    t = tt(0.4)
    f = 48 + 120 * np.exp(-t * 32)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8)
    s[:200] += np.linspace(0.6, 0, 200) * rs.standard_normal(200) * 0.3
    return fade(s, 0.0005)


def clap():
    s = np.zeros(int(0.3 * SR))
    for k, off in enumerate((0, 0.011, 0.022)):
        o = int(off * SR)
        b = band_noise((len(s) - o) / SR, 900, 5000)[: len(s) - o]
        b = b * np.exp(-np.arange(len(b)) / SR * (60 if k < 2 else 16))
        s[o:o + len(b)] += b * (0.6 if k < 2 else 1)
    t = tt(0.3)
    s += 0.25 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    return fade(s * 0.6, 0.0005)


def hat(open_=False):
    d = 0.25 if open_ else 0.06
    return fade(hp_noise(d, 7000) * np.exp(-tt(d) * (14 if open_ else 70)) * 0.35, 0.0005)


def bass(m, d):
    t = tt(d)
    f = mtof(m)
    s = sum(np.sin(2 * np.pi * f * h * t) / (h * h) * (1 if h == 1 else 0.8) for h in (1, 2, 3, 4))
    s += 0.5 * np.sin(2 * np.pi * f / 2 * t)
    env = np.minimum(1, t / 0.006) * (0.55 + 0.45 * np.exp(-t * 6))
    return fade(s * env * 0.5, 0.003, 0.03)


def marimba(m, d=0.5):
    t = tt(d)
    f = mtof(m)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 7)
    s += 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 25)
    s += 0.12 * np.sin(2 * np.pi * f * 9.8 * t) * np.exp(-t * 45)
    return fade(s, 0.001, 0.05)


def bell(m, d=1.2):
    t = tt(d)
    f = mtof(m)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 3.2)
    s += 0.45 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 5)
    s += 0.18 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t * 8)
    s += 0.08 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 14)
    return fade(s, 0.002, 0.1)


def pad(notes, d):
    t = tt(d)
    s = np.zeros(len(t))
    for m in notes:
        for det in (-0.12, 0.0, 0.11):
            f = mtof(m + det)
            for h in range(1, 7):
                s += np.sin(2 * np.pi * f * h * t + h) / h * (0.75 ** h)
    env = np.minimum(1, t / 0.35) * np.minimum(1, (d - t) / 0.35)
    return s * env / (len(notes) * 3)


# ----------------------------------------------------------------------------- music
CH = {"C": (48, [60, 64, 67]), "G": (43, [59, 62, 67]), "Am": (45, [57, 60, 64]), "F": (41, [57, 60, 65])}
#        intro      problem    blocks (4 x C G Am F)            recap     outro
PROG = ["C", "G", "Am", "F"] + ["C", "G", "Am", "F"] * 4 + ["F", "G", "C", "C"]
MELODY = {  # (slot in eighths, midi, length in eighths)
    "C": [(0, 76, 2), (2, 79, 2), (4, 81, 1), (5, 79, 1), (6, 76, 2)],
    "G": [(0, 74, 3), (3, 74, 1), (4, 76, 1), (5, 74, 1), (6, 71, 2)],
    "Am": [(0, 72, 2), (2, 76, 2), (4, 79, 2), (6, 76, 1), (7, 72, 1)],
    "F": [(0, 69, 2), (2, 72, 2), (4, 74, 2), (6, 72, 2)],
}


def make_music():
    mus = np.zeros((2, N + SR))
    K, CL, H, HO = kick(), clap(), hat(), hat(True)
    for b, name in enumerate(PROG):
        t0 = b * BAR
        root, tri = CH[name]
        final = b == 23
        intro, problem = b < 2, 2 <= b < 4
        recap = 20 <= b < 22
        # pad
        if not final:
            add(mus, pad(tri, BAR + 0.3), t0, 0.16 if not problem else 0.2)
        # marimba arpeggio (8ths)
        tones = tri + [tri[0] + 12]
        pat = [0, 1, 2, 3, 2, 1, 2, 3]
        if not final:
            for k, ix in enumerate(pat):
                if problem and k % 2:
                    continue
                add(mus, marimba(tones[ix] + (12 if recap and k % 2 else 0)), t0 + k * EIGHTH, 0.20, pan=-0.35 + 0.1 * (k % 3))
        # bass
        if b >= 1 and not final:
            for k in (0, 3, 6):
                add(mus, bass(root + (12 if k == 6 and not problem else 0), EIGHTH * (2 if k < 6 else 1.6)), t0 + k * EIGHTH, 0.42)
        # drums
        if b == 0:
            for k in range(4, 8):
                add(mus, H, t0 + k * EIGHTH, 0.35, 0.3)
        elif problem:
            for k in (0, 4):
                add(mus, K, t0 + k * EIGHTH, 0.7)
            for k in range(8):
                add(mus, H, t0 + k * EIGHTH, 0.3, 0.3)
        elif not final:
            for k in (0, 4) + ((7,) if b % 2 else ()):
                add(mus, K, t0 + k * EIGHTH, 0.8)
            for k in (2, 6):
                add(mus, CL, t0 + k * EIGHTH, 0.55, -0.1)
            steps = 16 if recap or b >= 12 else 8
            for k in range(steps):
                acc = (k % 2 == 1) if steps == 8 else (k % 4 == 2)
                add(mus, HO if (steps == 8 and k == 7) else H, t0 + k * BAR / steps, 0.42 if acc else 0.25, 0.3)
        # lead melody from block 03 onwards (bar 12) and through the recap
        if 12 <= b < 22:
            for slot, m, ln in MELODY[name]:
                add(mus, bell(m + (12 if recap else 0), max(0.5, ln * EIGHTH + 0.6)), t0 + slot * EIGHTH, 0.14, 0.25)
        # final hit: big C chord at the start of the last bar
        if final:
            add(mus, K, t0, 1.0)
            add(mus, CL, t0, 0.6)
            add(mus, HO, t0, 0.5)
            add(mus, bass(36, 2.4), t0, 0.6)
            add(mus, pad([60, 64, 67, 72], 2.4), t0, 0.3)
            for k, m in enumerate([72, 76, 79, 84]):
                add(mus, bell(m, 2.4), t0 + k * 0.04, 0.16)
    # crash-ish swells on scene changes
    for tc in (T_BLOCKS, T_RECAP):
        s = hp_noise(1.6, 3500) * np.exp(-tt(1.6) * 2.5) * 0.25
        add(mus, s, tc, 0.8)
    return mus


# ----------------------------------------------------------------------------- sound effects
def sfx_whoosh(d=0.55, f0=300, f1=3200, g=1.0):
    x = rs.standard_normal(int(d * SR))
    y = biquad_bp_sweep(x, f0, f1, q=1.6)
    t = tt(d)
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.6
    return fade(y * env / (np.abs(y).max() + 1e-9) * g)


def sfx_pop(f=700, d=0.12):
    t = tt(d)
    fr = f * (1 + 1.4 * np.exp(-t * 60))
    s = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 35)
    return fade(s, 0.0005, 0.01)


def sfx_tick(m=84):
    t = tt(0.09)
    f = mtof(m)
    return fade((np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t * 55), 0.0005)


def sfx_boing(f=210, d=0.5):
    t = tt(d)
    fr = f * (1 + 0.35 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 6)) * (1 + 0.6 * np.exp(-t * 18))
    return fade(np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 6), 0.002)


def sfx_thud(f=95):
    t = tt(0.35)
    fr = f * (1 + 1.2 * np.exp(-t * 40))
    s = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 14)
    s += band_noise(0.35, 100, 1500) * np.exp(-t * 50) * 0.4
    return fade(s, 0.0005)


def sfx_ding(m=88, d=1.2):
    return bell(m, d) * 0.9


def sfx_chime_up(base=79):
    s = np.zeros(int(0.9 * SR))
    for k, m in enumerate([base, base + 4, base + 7, base + 12]):
        b = bell(m, 0.9 - k * 0.07)
        s[int(k * 0.07 * SR):int(k * 0.07 * SR) + len(b)] += b * 0.5
    return s


def sfx_sparkle(n=9, base=96):
    s = np.zeros(int(0.9 * SR))
    for k in range(n):
        m = base + [0, 3, 7, 10, 12, 15, 19, 22, 24][k % 9]
        b = sfx_tick(m) * 0.6
        o = int(k * 0.045 * SR)
        s[o:o + len(b)] += b[: len(s) - o]
    return s


def sfx_beep(seq=((81, .07), (88, .07), (84, .1))):
    """Cute robot 'beep-boop' made from soft square-ish blips."""
    out = []
    for m, d in seq:
        t = tt(d)
        f = mtof(m)
        s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 3 * f * t) + 0.12 * np.sin(2 * np.pi * 5 * f * t)
        out.append(fade(s * 0.5, 0.004, 0.015))
        out.append(np.zeros(int(0.02 * SR)))
    return np.concatenate(out)


def sfx_uhoh():
    return sfx_beep(((76, .13), (71, .2)))


def sfx_fall(d=0.55):
    t = tt(d)
    f = 1500 * (300 / 1500) ** (t / d)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / 0.05) * 0.4
    return fade(s, 0.01, 0.05) + sfx_whoosh(d, 2500, 400, 0.5)


def sfx_suck(d=0.45):
    return sfx_whoosh(d, 3000, 250, 1.0)


def sfx_scribble(d=0.4):
    s = band_noise(d, 1500, 6000) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 9 * tt(d))))
    return fade(s * 0.4, 0.01, 0.05)


def sfx_zap():
    t = tt(0.35)
    f = 900 * np.exp(-t * 6) + 120
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.25 + band_noise(0.35, 2000, 8000) * 0.3
    return fade(s * np.exp(-t * 9), 0.001)


def sfx_clank():
    t = tt(0.3)
    s = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * dcy) for f, dcy in ((520, 18), (1340, 25), (2210, 30), (3600, 40)))
    return fade(s * 0.35 + band_noise(0.3, 2000, 9000) * np.exp(-t * 80) * 0.3, 0.0005)


def sfx_send():
    t = tt(0.18)
    f = 500 + 900 * t / 0.18
    return fade(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12), 0.002)


def sfx_receive():
    return sfx_beep(((84, .06), (91, .12)))


def sfx_rise(d=0.6):
    t = tt(d)
    f = 400 * (1600 / 400) ** (t / d)
    return fade(np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) * 0.4, 0.01, 0.05)


def sfx_tada():
    s = np.zeros(int(1.6 * SR))
    for k, m in enumerate([72, 76, 79]):
        b = marimba(m, 0.25)
        s[int(k * 0.08 * SR):int(k * 0.08 * SR) + len(b)] += b * 0.6
    for m in (72, 76, 79, 84):
        b = bell(m, 1.3)
        o = int(0.26 * SR)
        s[o:o + len(b)] += b * 0.35
    return s


T_PROBLEM, T_BLOCKS, T_RECAP, T_OUTRO = 5, 10, 50, 55


def cues():
    C = []  # (time, signal, gain, pan)

    def c(t, sig, g=1.0, pan=0.0):
        C.append((t, sig, g, pan))

    # --- intro
    c(0.05, sfx_sparkle(6, 91), 0.35, 0.2)
    c(0.22, sfx_fall(0.56), 0.55, -0.3)
    c(0.78, sfx_thud(80), 0.9, -0.3)
    c(0.80, sfx_boing(190), 0.45, -0.3)
    c(1.05, sfx_pop(650), 0.5, -0.1)
    c(1.12, sfx_beep(), 0.35, -0.2)
    for k in range(3):
        c(1.22 + k * 0.28, sfx_whoosh(0.32, 600, 3500, 0.35), 1.0, 0.3)
    c(2.2, sfx_scribble(0.45), 0.6, 0.3)
    c(2.6, sfx_pop(900, 0.1), 0.35, 0.3)
    for k in range(8):
        c(3.25 + k * 0.09, sfx_tick(72 + [0, 2, 4, 5, 7, 9, 11, 12][k]), 0.45, -0.2 + k * 0.08)
    c(3.82, sfx_boing(260, 0.35), 0.3, -0.3)
    c(4.5, sfx_whoosh(0.8, 250, 4000), 0.75)
    # --- problem
    c(5.3, sfx_pop(800, 0.1), 0.3, 0.2)
    c(5.42, sfx_whoosh(0.35, 500, 3000, 0.35), 1.0, 0.2)
    for k in range(7):
        c(5.62 + k * 0.16, sfx_pop(420 + 70 * k, 0.11), 0.45, -0.1 + 0.12 * k)
    c(5.9, sfx_pop(600), 0.4, -0.3)
    c(5.98, sfx_uhoh(), 0.4, -0.3)
    for k in range(3):
        c(6.02 + k * 0.15, sfx_boing(420 + 60 * k, 0.25), 0.25, -0.35)
    c(6.8, sfx_zap(), 0.18, 0.3)
    c(7.45, sfx_suck(0.5), 0.7, 0.3)
    c(7.75, sfx_boing(240, 0.4), 0.35, -0.3)
    c(7.9, sfx_pop(650), 0.45, -0.3)
    c(7.95, sfx_beep(((84, .06), (88, .06), (91, .1))), 0.3, -0.3)
    for k in range(8):
        c(7.98 + k * 0.11, sfx_pop(500 + 60 * k, 0.1), 0.42, -0.1 + 0.08 * k)
    c(9.0, sfx_sparkle(), 0.3, 0.3)
    c(9.5, sfx_whoosh(0.8, 250, 4000), 0.75)
    # --- building blocks
    for k in range(8):
        c(T_BLOCKS + 0.15 + k * 0.06, sfx_tick(79 + k), 0.18, -0.3 + 0.1 * k)
    for i in range(8):
        a = T_BLOCKS + i * 5
        c(a + 0.0, sfx_whoosh(0.5, 400, 3500, 0.5), 1.0, 0.35)
        c(a + 0.05, sfx_boing(260, 0.3), 0.18, -0.35)
        c(a + 0.25, sfx_pop(560, 0.12), 0.45, 0.0)
        c(a + 0.25, sfx_tick(84 + i), 0.3, -0.1 + 0.08 * i)
        c(a + 0.6, sfx_pop(820, 0.09), 0.3, 0.3)
        for k in range(3):
            c(a + 1.05 + k * 0.5, sfx_pop(700 + 120 * k, 0.1), 0.42, 0.3)
            c(a + 1.12 + k * 0.5, sfx_tick(88 + 2 * k), 0.18, 0.3)
        if i < 7:
            c(a + 4.6, sfx_whoosh(0.4, 3000, 600, 0.35), 1.0, -0.2)
        if i == 0:
            c(a + 0.5, sfx_whoosh(0.35, 800, 5000, 0.6), 1.0, 0.1)
            c(a + 0.85, sfx_thud(140), 0.6, 0.1)
            c(a + 0.87, sfx_boing(330, 0.35), 0.25, 0.1)
        if i == 1:
            for k, tt0 in enumerate((1.0, 1.3)):
                c(a + tt0, sfx_whoosh(0.4, 600, 2200, 0.5), 1.0, -0.1)
                c(a + tt0 + 0.42, sfx_clank(), 0.45, 0.1)
            c(a + 2.2, sfx_ding(91), 0.45, -0.1)
        if i == 2:
            for k in range(3):
                c(a + 0.6 + k * 0.35, sfx_boing(500 + 80 * k, 0.3), 0.25, -0.2 + 0.2 * k)
        if i == 3:
            c(a + 0.4, sfx_scribble(0.95), 0.45, 0.0)
            c(a + 1.5, sfx_pop(600), 0.4, 0.0)
        if i == 4:
            c(a + 0.7, sfx_scribble(0.35), 0.5, 0.0)
            c(a + 1.0, sfx_ding(88), 0.45, 0.0)
            for k in range(4):
                c(a + 1.12 + k * 0.15, sfx_tick(76 + 3 * k), 0.35, -0.3 + 0.2 * k)
        if i == 5:
            for k in range(6):
                c(a + 0.3 + k * 0.28, sfx_clank(), 0.22, -0.1)
            c(a + 0.9, sfx_zap(), 0.5, 0.2)
        if i == 6:
            c(a + 0.3, sfx_sparkle(), 0.45, -0.4)
            c(a + 0.35, sfx_pop(650), 0.45, -0.4)
            c(a + 0.42, sfx_beep(((79, .07), (86, .07), (91, .14))), 0.4, -0.4)
            c(a + 0.6, sfx_send(), 0.4, 0.2)
            for k in range(6):
                c(a + 1.15 + k * 0.12, sfx_tick(96), 0.12, 0.0)
            c(a + 1.9, sfx_receive(), 0.45, -0.1)
            c(a + 1.9, sfx_boing(280, 0.35), 0.25, -0.4)
            c(a + 2.5, sfx_boing(320, 0.35), 0.25, -0.4)
            c(a + 2.6, sfx_sparkle(9, 100), 0.3, -0.4)
        if i == 7:
            for k in range(4):
                c(a + 0.4 + k * 0.2, sfx_pop(400 + 120 * k, 0.12), 0.4, 0.0)
            c(a + 1.3, sfx_rise(0.6), 0.4, 0.1)
            c(a + 1.85, sfx_ding(93), 0.4, 0.1)
    c(49.5, sfx_whoosh(0.8, 250, 4000), 0.75)
    # --- recap
    c(50.2, sfx_whoosh(0.35, 500, 3000, 0.35), 1.0, -0.2)
    order = [4, 5, 6, 7, 0, 1, 2, 3]
    for k in range(8):
        c(50.35 + k * 0.14 + 0.15, sfx_thud(110 + 8 * k), 0.55, -0.4 + 0.1 * (order[k] % 4))
    c(51.65 + 0.15, sfx_thud(70), 0.9)
    c(51.9, sfx_tada(), 0.55)
    for tc in (52.0, 52.55, 53.1):
        c(tc, sfx_pop(500), 0.5, -0.3)
        c(tc, sfx_pop(900), 0.35, 0.4)
        c(tc + 0.03, sfx_sparkle(), 0.3, 0.0)
        c(tc, sfx_boing(260, 0.35), 0.25, 0.5)
    c(52.1, sfx_beep(((84, .07), (88, .07), (91, .07), (96, .14))), 0.35, 0.5)
    c(52.3, sfx_whoosh(0.35, 500, 3000, 0.3), 1.0, -0.2)
    c(54.5, sfx_whoosh(0.8, 250, 4000), 0.75)
    # --- outro
    c(55.0, sfx_whoosh(0.5, 3500, 500, 0.5), 1.0, 0.4)
    c(55.5, sfx_pop(800, 0.1), 0.35, -0.3)
    c(55.7, sfx_whoosh(0.4, 500, 3000, 0.4), 1.0, -0.3)
    c(56.6, sfx_pop(1000, 0.09), 0.25, -0.3)
    c(57.6, sfx_boing(260, 0.35), 0.3, 0.4)
    c(57.6, sfx_chime_up(84), 0.35, 0.2)
    return C


def reverb(x, secs=1.4, wet=0.18):
    ir = rs.standard_normal(int(secs * SR)) * np.exp(-np.arange(int(secs * SR)) / SR * 4.5)
    ir[: int(0.012 * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    n = x.shape[1] + len(ir)
    nfft = 1 << (n - 1).bit_length()
    IR = np.fft.rfft(ir, nfft)
    out = np.zeros_like(x)
    for ch in range(2):
        # decorrelate channels slightly
        irc = np.fft.rfft(np.roll(ir, ch * 37), nfft) if ch else IR
        y = np.fft.irfft(np.fft.rfft(x[ch], nfft) * irc, nfft)[: x.shape[1]]
        out[ch] = x[ch] + wet * y
    return out


def soft_limit(x, ceiling=0.89):
    return np.tanh(x / ceiling) * ceiling


def write_wav(path, x):
    x = np.clip(x[:, :N], -1, 1)
    pcm = (x.T * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def db(x):
    return 20 * np.log10(np.abs(x).max() + 1e-12)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    music = reverb(make_music(), 1.6, 0.22)
    # gentle fade-out of the final chord
    t = np.arange(music.shape[1]) / SR
    music *= np.clip((DUR - t) / 1.6, 0, 1)
    music *= 10 ** (-6 / 20) / (np.abs(music).max() + 1e-9)   # music bed: sits ~6 dB under the sfx, room for a voice-over

    sfx = np.zeros((2, N + 2 * SR))
    for t0, sig, g, pan in cues():
        add(sfx, sig, t0, g, pan)
    sfx = reverb(sfx, 0.8, 0.12)
    sfx *= 10 ** (-2.5 / 20) / (np.abs(sfx).max() + 1e-9)       # sfx peaks at -2.5 dBFS before limiting

    mix = soft_limit(music[:, :N] + sfx[:, :N])
    write_wav(OUT / "music.wav", music)
    write_wav(OUT / "sfx.wav", sfx)
    write_wav(OUT / "mix.wav", mix)
    print(f"music peak {db(music):.1f} dBFS, sfx peak {db(sfx):.1f} dBFS, mix peak {db(mix):.1f} dBFS")
