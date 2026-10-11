"""Music, sound effects and (optional) voice-over mix for the Enterprise Knowledge Hub video (v2).

    python3 scripts/make_audio_v2.py                         # music + sfx only
    python3 scripts/make_audio_v2.py --vo voice.mp3 [--offset 0.2]

Scene timings come from src/timeline_v2.js. With --vo, the music is ducked under the voice,
and src/vo_env_v2.js is written so EKA's mouth moves in sync with the voice-over.

Outputs (output/v2/): music.wav, sfx.wav, mix.wav (and voice.wav + mix_vo.wav with --vo)
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_audio as A  # noqa: E402  (shared instruments + sound effects)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "v2"
SR = A.SR
TL = json.loads((ROOT / "src/timeline_v2.js").read_text().split("window.TL =", 1)[1].strip().rstrip(";"))
DUR = TL["end"]
N = int(SR * DUR)
BAR, EIGHTH = A.BAR, A.EIGHTH
BS = TL["blocks"]
T_BLOCKS, T_RECAP, T_CLOSE = BS[0], TL["recap"], TL["closing"]

# 24 bars at 96 BPM: intro (2) | 8 blocks (16) | recap (3) | closing (3, final hit on the last bar)
PROG = ["C", "G"] + ["C", "G", "Am", "F"] * 4 + ["F", "G", "Am"] + ["F", "G", "C"]


def make_music():
    mus = np.zeros((2, N + SR))
    K, CL, H, HO = A.kick(), A.clap(), A.hat(), A.hat(True)
    nb = len(PROG)
    for b, name in enumerate(PROG):
        t0 = b * BAR
        root, tri = A.CH[name]
        final = b == nb - 1
        recap = T_RECAP <= t0 < T_CLOSE
        if not final:
            A.add(mus, A.pad(tri, BAR + 0.3), t0, 0.16)
            tones = tri + [tri[0] + 12]
            for k, ix in enumerate([0, 1, 2, 3, 2, 1, 2, 3]):
                A.add(mus, A.marimba(tones[ix] + (12 if recap and k % 2 else 0)), t0 + k * EIGHTH, 0.19, pan=-0.35 + 0.1 * (k % 3))
        if b >= 1 and not final:
            for k in (0, 3, 6):
                A.add(mus, A.bass(root + (12 if k == 6 else 0), EIGHTH * (2 if k < 6 else 1.6)), t0 + k * EIGHTH, 0.42)
        if b == 0:
            for k in range(4, 8):
                A.add(mus, H, t0 + k * EIGHTH, 0.35, 0.3)
        elif not final:
            for k in (0, 4) + ((7,) if b % 2 else ()):
                A.add(mus, K, t0 + k * EIGHTH, 0.8)
            for k in (2, 6):
                A.add(mus, CL, t0 + k * EIGHTH, 0.5, -0.1)
            steps = 16 if recap or b >= 10 else 8
            for k in range(steps):
                acc = (k % 2 == 1) if steps == 8 else (k % 4 == 2)
                A.add(mus, HO if (steps == 8 and k == 7) else H, t0 + k * BAR / steps, 0.4 if acc else 0.24, 0.3)
        if 10 <= b < nb - 1:
            for slot, m, ln in A.MELODY[name]:
                A.add(mus, A.bell(m + (12 if recap else 0), max(0.5, ln * EIGHTH + 0.6)), t0 + slot * EIGHTH, 0.12, 0.25)
        if final:
            A.add(mus, K, t0, 1.0); A.add(mus, CL, t0, 0.6); A.add(mus, HO, t0, 0.5)
            A.add(mus, A.bass(36, 2.4), t0, 0.6)
            A.add(mus, A.pad([60, 64, 67, 72], 2.4), t0, 0.3)
            for k, m in enumerate([72, 76, 79, 84]):
                A.add(mus, A.bell(m, 2.4), t0 + k * 0.04, 0.16)
    for tc in (T_BLOCKS, T_RECAP, T_CLOSE):
        A.add(mus, A.hp_noise(1.6, 3500) * np.exp(-A.tt(1.6) * 2.5) * 0.25, tc, 0.8)
    return mus


def cues():
    C = []

    def c(t, sig, g=1.0, pan=0.0):
        C.append((t, sig, g, pan))

    # intro
    c(0.05, A.sfx_sparkle(6, 91), 0.35, 0.2)
    c(0.22, A.sfx_fall(0.56), 0.55, -0.3)
    c(0.78, A.sfx_thud(80), 0.9, -0.3)
    c(0.80, A.sfx_boing(190), 0.45, -0.3)
    c(1.05, A.sfx_pop(650), 0.5, -0.1)
    c(1.12, A.sfx_beep(), 0.35, -0.2)
    for k in range(3):
        c(1.22 + k * 0.28, A.sfx_whoosh(0.32, 600, 3500, 0.35), 1.0, 0.3)
    c(1.8, A.sfx_scribble(0.45), 0.55, 0.3)
    c(2.5, A.sfx_pop(900, 0.1), 0.35, 0.3)
    for k in range(8):
        c(3.25 + k * 0.09, A.sfx_tick(72 + [0, 2, 4, 5, 7, 9, 11, 12][k]), 0.45, -0.2 + 0.08 * k)
    c(3.82, A.sfx_boing(260, 0.35), 0.3, -0.3)
    # wipes
    for B in (T_BLOCKS, T_RECAP, T_CLOSE):
        c(B - 0.5, A.sfx_whoosh(0.8, 250, 4000), 0.75)
    # blocks
    for k in range(8):
        c(T_BLOCKS + 0.15 + k * 0.06, A.sfx_tick(79 + k), 0.18, -0.3 + 0.1 * k)
    for i, a in enumerate(BS):
        end = BS[i + 1] if i < 7 else T_RECAP
        c(a + 0.0, A.sfx_whoosh(0.5, 400, 3500, 0.5), 1.0, 0.35)
        c(a + 0.05, A.sfx_boing(260, 0.3), 0.15, -0.35)
        c(a + 0.25, A.sfx_pop(560, 0.12), 0.45)
        c(a + 0.25, A.sfx_tick(84 + i), 0.3, -0.1 + 0.08 * i)
        c(a + 0.7, A.sfx_whoosh(0.3, 900, 3000, 0.25), 1.0, 0.3)
        c(a + 0.72, A.sfx_tick(82), 0.18, -0.4)       # EKA points
        c(a + 2.0, A.sfx_whoosh(0.35, 600, 2800, 0.35), 1.0, 0.3)  # "why it matters" panel
        c(a + 2.25, A.sfx_ding(91 if i % 2 else 88, 0.9), 0.32, 0.3)
        c(a + 2.27, A.sfx_tick(80), 0.15, -0.4)
        if i < 7:
            c(end - 0.45, A.sfx_whoosh(0.4, 3000, 600, 0.35), 1.0, -0.2)
        if i == 0:
            for k in range(3):
                c(a + 0.5 + k * 0.2, A.sfx_boing(480 + 70 * k, 0.25), 0.22, 0.1)
            c(a + 1.35, A.sfx_whoosh(0.35, 800, 5000, 0.6), 1.0, 0.1)
            c(a + 1.7, A.sfx_thud(140), 0.6, 0.1)
        if i == 1:
            for t0 in (1.0, 1.3):
                c(a + t0, A.sfx_whoosh(0.4, 600, 2200, 0.5), 1.0, -0.1)
                c(a + t0 + 0.42, A.sfx_clank(), 0.42, 0.1)
            c(a + 2.4, A.sfx_pop(700), 0.35, -0.2)
        if i == 2:
            for k in range(4):
                c(a + 0.5 + k * 0.3, A.sfx_boing(480 + 60 * k, 0.3), 0.24, -0.2 + 0.15 * k)
        if i == 3:
            c(a + 0.4, A.sfx_scribble(1.2), 0.42)
            c(a + 1.8, A.sfx_pop(650), 0.4)
        if i == 4:
            c(a + 0.7, A.sfx_scribble(0.35), 0.5)
            c(a + 1.0, A.sfx_ding(84, 0.9), 0.35)
            for k in range(3):
                c(a + 1.12 + k * 0.2, A.sfx_tick(76 + 4 * k), 0.35, -0.3 + 0.3 * k)
        if i == 5:
            for k in range(6):
                c(a + 0.3 + k * 0.28, A.sfx_clank(), 0.2, -0.1)
            c(a + 0.9, A.sfx_zap(), 0.45, 0.2)
        if i == 6:
            c(a + 0.3, A.sfx_sparkle(), 0.45, -0.4)
            c(a + 0.35, A.sfx_pop(650), 0.45, -0.4)
            c(a + 0.42, A.sfx_beep(((79, .07), (86, .07), (91, .14))), 0.4, -0.4)
            c(a + 0.6, A.sfx_send(), 0.4, 0.2)
            for k in range(6):
                c(a + 1.15 + k * 0.12, A.sfx_tick(96), 0.12)
            c(a + 1.9, A.sfx_receive(), 0.45, -0.1)
            c(a + 1.9, A.sfx_boing(280, 0.35), 0.25, -0.4)
            c(a + 2.45, A.sfx_boing(320, 0.35), 0.25, -0.4)
            c(a + 2.6, A.sfx_pop(800, 0.1), 0.3, 0.1)
        if i == 7:
            for k in range(4):
                c(a + 0.4 + k * 0.2, A.sfx_pop(400 + 120 * k, 0.12), 0.4)
            c(a + 1.3, A.sfx_rise(0.6), 0.4, 0.1)
            c(a + 2.1, A.sfx_boing(500, 0.3), 0.25, -0.2)
    # recap
    r = T_RECAP
    c(r + 0.2, A.sfx_whoosh(0.35, 500, 3000, 0.35), 1.0, -0.2)
    order = [4, 5, 6, 7, 0, 1, 2, 3]
    for k in range(8):
        c(r + 0.35 + k * 0.14 + 0.15, A.sfx_thud(110 + 8 * k), 0.55, -0.4 + 0.1 * (order[k] % 4))
    c(r + 1.8, A.sfx_thud(70), 0.9)
    c(r + 1.9, A.sfx_tada(), 0.55)
    for tc in (r + 2.0, r + 2.55, r + 3.1):
        c(tc, A.sfx_pop(500), 0.5, -0.3)
        c(tc, A.sfx_pop(900), 0.35, 0.4)
        c(tc + 0.03, A.sfx_sparkle(), 0.3)
        c(tc + 0.1, A.sfx_boing(260, 0.35), 0.22, 0.5)
    c(r + 2.2, A.sfx_beep(((84, .07), (88, .07), (91, .07), (96, .14))), 0.35, 0.5)
    for k in range(3):
        c(r + 3.6 + k * 0.55, A.sfx_pop(700 + 120 * k, 0.11), 0.42, -0.3 + 0.3 * k)
        c(r + 3.65 + k * 0.55, A.sfx_ding(84 + 4 * k, 0.7), 0.22, -0.3 + 0.3 * k)
    # closing
    s = T_CLOSE
    c(s + 0.0, A.sfx_whoosh(0.5, 3500, 500, 0.5), 1.0, 0.4)
    c(s + 0.45, A.sfx_pop(800, 0.1), 0.35, -0.3)
    c(s + 1.0, A.sfx_whoosh(0.4, 500, 3000, 0.4), 1.0, -0.3)
    c(s + 2.6, A.sfx_scribble(0.45), 0.5, -0.3)
    for k in range(3):
        c(s + 3.4 + k * 0.3, A.sfx_tick(84 + 3 * k), 0.35, -0.4 + 0.2 * k)
    c(s + 4.6, A.sfx_boing(260, 0.35), 0.3, 0.4)
    c(s + 5.0, A.sfx_chime_up(84), 0.35, 0.2)
    return C


def load_vo(path, offset):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    v = np.frombuffer(raw, np.float32).astype(np.float64)
    # Level: speech RMS (above a noise gate) to about -18 dBFS, peaks safely below 0.
    frame = int(0.05 * SR)
    rms = np.sqrt(np.convolve(v ** 2, np.ones(frame) / frame, mode="same"))
    speech = rms > rms.max() * 0.1
    v *= 10 ** (-18 / 20) / (np.sqrt(np.mean(v[speech] ** 2)) + 1e-9)
    v = np.tanh(v / 0.9) * 0.9
    out = np.zeros(N)
    i = int(offset * SR)
    n = min(len(v), N - i)
    out[i:i + n] = v[:n]
    return out


def envelope(v, fps=30):
    """Per-frame mouth-open amount (0..1) from the voice signal."""
    hop = SR // fps
    frames = len(v) // hop
    e = np.array([np.sqrt(np.mean(v[k * hop:(k + 1) * hop] ** 2)) for k in range(frames)])
    e = e / (np.percentile(e[e > 1e-4], 95) + 1e-9) if np.any(e > 1e-4) else e
    e = np.clip((e - 0.12) / 0.88, 0, 1)
    # smooth a touch so the mouth doesn't flicker
    e = np.convolve(e, [0.25, 0.5, 0.25], mode="same")
    return [round(float(x), 3) for x in e]


def duck(music, vo):
    """Lower the music by ~9 dB while the voice is speaking (with smooth attack/release)."""
    frame = int(0.03 * SR)
    rms = np.sqrt(np.convolve(vo ** 2, np.ones(frame) / frame, mode="same"))
    on = (rms > 0.01).astype(np.float64)
    # attack 60 ms / release 400 ms one-pole smoothing, computed at a coarse rate then upsampled
    step = 441
    coarse = on[::step]
    g = np.zeros_like(coarse)
    a_att, a_rel = np.exp(-step / (0.06 * SR)), np.exp(-step / (0.4 * SR))
    for k in range(1, len(coarse)):
        a = a_att if coarse[k] > g[k - 1] else a_rel
        g[k] = a * g[k - 1] + (1 - a) * coarse[k]
    g = np.interp(np.arange(len(on)), np.arange(len(coarse)) * step, g)
    gain = 10 ** (-9 * g / 20)
    return music * gain


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--vo", help="voice-over audio file (mp3/wav)")
    ap.add_argument("--offset", type=float, default=0.0, help="seconds to delay the voice-over")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    music = A.reverb(make_music(), 1.6, 0.22)[:, :N]
    t = np.arange(N) / SR
    music *= np.clip((DUR - t) / 1.6, 0, 1)
    music *= 10 ** (-6 / 20) / (np.abs(music).max() + 1e-9)

    sfx = np.zeros((2, N + 2 * SR))
    for t0, sig, g, pan in cues():
        A.add(sfx, sig, t0, g, pan)
    sfx = A.reverb(sfx, 0.8, 0.12)[:, :N]
    sfx *= 10 ** (-2.5 / 20) / (np.abs(sfx).max() + 1e-9)

    A.N = N
    A.write_wav(OUT / "music.wav", music)
    A.write_wav(OUT / "sfx.wav", sfx)
    A.write_wav(OUT / "mix.wav", A.soft_limit(music + sfx))
    print(f"wrote {OUT}/music.wav, sfx.wav, mix.wav")

    env_js = ROOT / "src/vo_env_v2.js"
    if args.vo:
        vo = load_vo(args.vo, args.offset)
        A.write_wav(OUT / "voice.wav", np.vstack([vo, vo]))
        mix = A.soft_limit(duck(music, vo) * 0.85 + sfx * 0.6 + np.vstack([vo, vo]))
        A.write_wav(OUT / "mix_vo.wav", mix)
        env_js.write_text("// Generated by scripts/make_audio_v2.py from the voice-over (mouth-open amount per frame).\n"
                          f"window.VO_ENV = {json.dumps({'fps': 30, 'v': envelope(vo)})};\n")
        print(f"wrote {OUT}/voice.wav, mix_vo.wav and {env_js.relative_to(ROOT)}")
    elif env_js.exists():
        env_js.unlink()
