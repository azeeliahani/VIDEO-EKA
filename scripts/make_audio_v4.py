"""Music, sound effects and voice-over mix for "Why many knowledge hubs fail" (v4).

    python3 scripts/make_audio_v4.py --vo assets/voiceover/eka_vo_v4.wav

Scene timings come from src/timeline_v4.js. Everything except the voice is synthesised with numpy
(instruments and effects from scripts/make_audio.py), so it is royalty-free.
With --vo, the music is ducked under the voice and src/vo_env_v4.js is written for EKA's lip-sync.

Outputs (output/v4/): music.wav, sfx.wav, mix.wav (and voice.wav + mix_vo.wav with --vo)
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_audio as A  # noqa: E402  (shared instruments + sound effects)
import make_audio_v2 as V2  # noqa: E402  (voice loading, ducking and lip-sync envelope)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "v4"
SR = A.SR
TL = json.loads((ROOT / "src/timeline_v4.js").read_text().split("window.TL =", 1)[1].strip().rstrip(";"))
DUR = TL["end"]
N = int(SR * DUR)
BAR, EIGHTH = A.BAR, A.EIGHTH
ST = TL["traps"]
NT = len(ST)
DODGE = 2.3  # seconds into each trap when the fix appears (src/eka_v4.html DODGE_U)
T_STEPS, T_RECAP, T_CLOSE = ST[0], TL["recap"], TL["closing"]
V2.N, V2.SR = N, SR

# 24 bars at 96 BPM: intro build (3) | 7 traps (14, minor-flavoured) | recap (4, lifts to major) | closing (3, final hit)
PROG = ["Am", "G", "F"] + ["Am", "F", "C", "G"] * 3 + ["Am", "G"] + ["F", "G", "C", "G"] + ["F", "G", "C"]
HOOK = {  # bright lead riff: (slot in eighths, midi)
    "F": [(0, 77), (2, 76), (3, 72), (5, 74), (6, 72)],
    "G": [(0, 79), (2, 77), (3, 74), (5, 76), (6, 74)],
    "Am": [(0, 76), (2, 79), (3, 81), (5, 79), (6, 76)],
    "C": [(0, 79), (1, 81), (2, 84), (4, 81), (6, 79)],
}


def make_music():
    mus = np.zeros((2, N + SR))
    K, CL, H, HO = A.kick(), A.clap(), A.hat(), A.hat(True)
    nb = len(PROG)
    for b, name in enumerate(PROG):
        t0 = b * BAR
        root, tri = A.CH[name]
        final = b == nb - 1
        intro = b < 3
        recap = T_RECAP <= t0 < T_CLOSE
        if not final:
            A.add(mus, A.pad(tri, BAR + 0.3), t0, 0.15)
            tones = tri + [tri[0] + 12]
            for k in range(16 if not intro or b == 2 else 8):
                step = BAR / (16 if not intro or b == 2 else 8)
                ix = [0, 2, 1, 3, 2, 1, 3, 2][k % 8]
                if k % 2 and (intro and b < 2):
                    continue
                A.add(mus, A.marimba(tones[ix] + (12 if (recap or b >= 11) and k % 4 == 3 else 0), 0.35), t0 + k * step, 0.15, pan=-0.4 + 0.1 * (k % 5))
        if b >= 1 and not final:
            for k in (0, 2, 3, 5, 6):
                A.add(mus, A.bass(root + (12 if k in (3, 6) else 0), EIGHTH * 0.9), t0 + k * EIGHTH, 0.4)
        if intro:
            for k in range(8 if b == 0 else 16):
                A.add(mus, A.hat(), t0 + k * BAR / (8 if b == 0 else 16), 0.18 + 0.1 * (k % 2), 0.3)
            if b >= 1:
                for k in (0, 4):
                    A.add(mus, K, t0 + k * EIGHTH, 0.75)
            if b == 2:
                for k in range(8):  # snare-roll style build into step 1
                    A.add(mus, CL, t0 + BAR / 2 + k * BAR / 16, 0.15 + 0.05 * k, -0.1)
        elif not final:
            for k in (0, 3, 4) + ((7,) if b % 2 else ()):
                A.add(mus, K, t0 + k * EIGHTH, 0.8 if k != 3 else 0.5)
            for k in (2, 6):
                A.add(mus, CL, t0 + k * EIGHTH, 0.55, -0.1)
            for k in range(16):
                A.add(mus, HO if k == 14 else H, t0 + k * BAR / 16, 0.36 if k % 4 == 2 else 0.2, 0.3)
        if not intro and not final and (b >= 9 or recap):
            for slot, m in HOOK[name]:
                A.add(mus, A.bell(m + (12 if recap else 0), 0.7), t0 + slot * EIGHTH, 0.12, 0.25)
        if final:
            A.add(mus, K, t0, 1.0); A.add(mus, CL, t0, 0.6); A.add(mus, HO, t0, 0.5)
            A.add(mus, A.bass(36, 2.4), t0, 0.6)
            A.add(mus, A.pad([60, 64, 67, 72], 2.4), t0, 0.3)
            for k, m in enumerate([72, 76, 79, 84, 88]):
                A.add(mus, A.bell(m, 2.4), t0 + k * 0.05, 0.15)
    for tc in (T_STEPS, T_RECAP, T_CLOSE):
        A.add(mus, A.hp_noise(1.6, 3500) * np.exp(-A.tt(1.6) * 2.5) * 0.25, tc, 0.8)
    A.add(mus, A.sfx_rise(1.2), T_STEPS - 1.25, 0.3)
    return mus


def cues():
    C = []

    def c(t, sig, g=1.0, pan=0.0):
        C.append((t, sig, g, pan))

    # intro: EKA drops in, title builds, the orbit of eight appears
    c(0.05, A.sfx_sparkle(6, 91), 0.35, -0.3)
    c(0.2, A.sfx_fall(0.55), 0.55, -0.4)
    c(0.75, A.sfx_thud(80), 0.9, -0.4)
    c(0.77, A.sfx_boing(190), 0.45, -0.4)
    c(0.95, A.sfx_pop(650), 0.5, -0.3)
    c(1.0, A.sfx_beep(), 0.35, -0.4)
    c(1.2, A.sfx_whoosh(0.35, 600, 3500, 0.35), 1.0, 0.3)
    for k in range(3):
        a = 1.5 + k * 0.45
        c(a, A.sfx_whoosh(0.3, 700, 3800, 0.35), 1.0, 0.3)
        c(a + 0.25, A.sfx_pop(500 + 150 * k, 0.1), 0.4, 0.3)
    c(2.3, A.sfx_scribble(0.45), 0.5, 0.3)
    c(3.2, A.sfx_whoosh(0.3, 900, 3000, 0.25), 1.0, 0.3)
    for k in range(4):
        c(3.9 + k * 0.2, A.sfx_pop(600 + 100 * k, 0.1), 0.4, 0.2 + 0.1 * k)
    c(3.4, A.sfx_boing(260, 0.35), 0.3, -0.4)
    for k in range(8):
        c(4.7 + k * 0.12, A.sfx_tick(72 + [0, 2, 4, 5, 7, 9, 11, 12][k]), 0.4, -0.4 + 0.05 * k)
    c(5.6, A.sfx_boing(300, 0.35), 0.3, -0.4)
    c(5.75, A.sfx_chime_up(79), 0.3, -0.3)
    for B in (T_STEPS, T_RECAP, T_CLOSE):
        c(B - 0.5, A.sfx_whoosh(0.8, 250, 4000), 0.75)
    # traps: uh-oh when each trap appears, a happy "dodged!" when its fix pops up
    for i, a in enumerate(ST):
        end = ST[i + 1] if i < NT - 1 else T_RECAP
        c(a + 0.04, A.sfx_boing(220, 0.3), 0.15, -0.4)
        c(a + 0.08, A.sfx_pop(520, 0.12), 0.5, 0.2)
        c(a + 0.15, A.sfx_whoosh(0.45, 400, 3500, 0.5), 1.0, 0.35)
        c(a + 0.35, A.sfx_uhoh(), 0.42, 0.1)
        c(a + 0.45, A.sfx_tick(76), 0.25, 0.3)
        for k in range(4):
            c(a + 0.55 + k * 0.18, A.sfx_tick(86 + 2 * k), 0.1, 0.2)
        if i == 0:
            c(a + 0.5, A.hp_noise(1.2, 900) * np.exp(-A.tt(1.2) * 2.0) * 0.5, 0.5, 0.1)  # sputtering rocket
        if i == 2:
            for k in range(3):
                c(a + 0.6 + k * 0.4, A.sfx_clank(), 0.25, 0.1)
        if i == 3:
            for k in range(4):
                c(a + 0.5 + k * 0.3, A.sfx_boing(380 + 50 * k, 0.25), 0.16, -0.2 + 0.15 * k)
        if i == 4:
            c(a + 0.5, A.sfx_whoosh(1.0, 800, 2000, 0.2), 0.6, 0.1)
        if i == 5:
            for k in range(3):
                c(a + 0.6 + k * 0.45, A.sfx_pop(900 + 120 * k, 0.08), 0.25, 0.2)
        if i == 6:
            for k in range(4):
                c(a + 0.5 + k * 0.32, A.sfx_beep(((76 + 3 * (k % 2), .06),)), 0.2, (-1) ** k * 0.3)
        d = a + DODGE
        c(d - 0.05, A.sfx_whoosh(0.35, 600, 3200, 0.4), 1.0, 0.3)
        c(d + 0.05, A.sfx_chime_up(84 + (i % 3)), 0.32, 0.2)
        c(d + 0.15, A.sfx_zap(), 0.18, -0.2)
        c(d + 0.45, A.sfx_thud(140), 0.45, 0.4)                # DODGED! stamp
        c(d + 0.47, A.sfx_pop(800, 0.1), 0.35, 0.4)
        c(d + 0.3, A.sfx_boing(320, 0.35), 0.22, -0.4)        # EKA hops
        c(end - 0.6, A.sfx_whoosh(0.5, 3000, 500, 0.4), 1.0, -0.2)
        c(end - 0.12, A.sfx_pop(900, 0.1), 0.45, -0.4)
        c(end - 0.1, A.sfx_tick(84 + i), 0.3, -0.4)
    # recap: a tick for every fix as it is spoken
    r = T_RECAP
    c(r + 0.1, A.sfx_whoosh(0.35, 500, 3000, 0.35), 1.0, 0.2)
    c(r + 0.3, A.sfx_sparkle(), 0.35, 0.2)
    for k, f in enumerate(TL.get("fixes", [1.6 + 0.9 * j for j in range(NT)])):
        c(r + f, A.sfx_pop(500 + 70 * k), 0.5, 0.3)
        c(r + f + 0.04, A.sfx_ding(79 + [0, 2, 4, 5, 7, 9, 12][k], 0.6), 0.25, 0.3)
    c(r + 7.6, A.sfx_tada(), 0.45)
    c(r + 8.6, A.sfx_boing(260, 0.35), 0.25, -0.3)
    # closing
    s = T_CLOSE
    for k in range(4):
        c(s + 0.4 + k * 0.4, A.sfx_whoosh(0.3, 500, 3000, 0.3), 0.8, -0.3)
    c(s + 1.9, A.sfx_scribble(0.45), 0.45, -0.3)
    for k in range(6):
        c(s + 1.9 + k * 0.12, A.sfx_pop(500 + 90 * k, 0.1), 0.35, -0.6 + 0.24 * k)
    c(s + 3.0, A.sfx_chime_up(84), 0.35, -0.2)
    c(DUR - 3.0, A.sfx_pop(800, 0.1), 0.4, 0.3)
    c(DUR - 2.95, A.sfx_sparkle(), 0.35, 0.3)
    c(DUR - 1.45, A.sfx_boing(300, 0.35), 0.3, 0.3)
    return C


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--vo", help="voice-over audio file (mp3/wav)")
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

    if args.vo:
        vo = V2.load_vo(args.vo, 0.0)
        A.write_wav(OUT / "voice.wav", np.vstack([vo, vo]))
        mix = A.soft_limit(V2.duck(music, vo) * 0.85 + sfx * 0.55 + np.vstack([vo, vo]))
        A.write_wav(OUT / "mix_vo.wav", mix)
        (ROOT / "src/vo_env_v4.js").write_text("// Generated by scripts/make_audio_v4.py from the voice-over (mouth-open amount per frame).\n"
                                              f"window.VO_ENV = {json.dumps({'fps': 30, 'v': V2.envelope(vo)})};\n")
        print(f"wrote {OUT}/voice.wav, mix_vo.wav and src/vo_env_v4.js")
