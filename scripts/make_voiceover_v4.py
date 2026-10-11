"""Excited narration for the v4 video ("Why many knowledge hubs fail"): Kokoro v1.0 TTS, one line per scene.

The voice is a blend of Kokoro's most expressive US voices (af_heart, af_jessica, af_sarah),
pitched up towards the ElevenLabs "Allison - Energetic, Clear and Bubbly" reference in
assets/source/. Each line is fitted into its scene (src/timeline_v4.js).

Setup (all offline, from npm + PyPI):
    pip install kokoro-onnx soundfile
    mkdir -p /tmp/kokoro && cd /tmp/kokoro && npm pack kokoro-q8-shards kokoro-js && for f in *.tgz; do tar xzf $f --one-top-level; done
    KOKORO_DIR=/tmp/kokoro python3 scripts/make_voiceover_v4.py

Writes assets/voiceover/eka_vo_v4.wav (+ output/v4/vo_lines.json with each line's timing).
"""
import glob
import json
import os
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parent.parent
KD = Path(os.environ.get("KOKORO_DIR", "/tmp/kokoro"))
TL = json.loads((ROOT / "src/timeline_v4.js").read_text().split("window.TL =", 1)[1].strip().rstrip(";"))

model = KD / "kokoro_v1_q8.onnx"
if not model.exists():
    model.write_bytes(b"".join(Path(p).read_bytes() for p in sorted(glob.glob(str(KD / "kokoro-q8-shards*/package/kokoro-q8.part*.bin")))))
voices = KD / "voices_v1.npz"
if not voices.exists():
    vd = glob.glob(str(KD / "kokoro-js*/package/voices"))[0]
    np.savez(voices, **{Path(f).stem: np.fromfile(f, np.float32).reshape(-1, 1, 256) for f in glob.glob(vd + "/*.bin")})
k = Kokoro(str(model), str(voices))
V = np.load(voices)
VOICE = 0.5 * V["af_heart"] + 0.3 * V["af_jessica"] + 0.2 * V["af_sarah"]

S = TL["traps"]
# (scene start, scene end, lead-in, text)
LINES = [
    (0, S[0], 0.8, "Uh-oh! Why do so many knowledge hubs fail? Let's spot the seven sneaky traps, so yours won't!"),
    (S[0], S[1], 0.2, "Trap one: Technology first! The agent launches too early, and answers disappoint."),
    (S[1], S[2], 0.2, "Trap two: No owners! Documents get old, and nobody updates them."),
    (S[2], S[3], 0.2, "Trap three: Garbage in, garbage out! Duplicates compete, so answers conflict."),
    (S[3], S[4], 0.2, "Trap four: Metadata as an afterthought! Messy tags make content hard to trust."),
    (S[4], S[5], 0.2, "Trap five: Governance only on paper! Rules exist, but nobody follows them."),
    (S[5], S[6], 0.2, "Trap six: No feedback loop! Unanswered questions pile up, and gaps stay open."),
    (S[6], TL["recap"], 0.2, "Trap seven: Weak change management! People still ask colleagues instead."),
    (TL["recap"], TL["closing"], 0.3, "So, how do you dodge them? Content first! Clear owners! Clean sources! Required tags! Automated rules! A feedback loop! And show the value!"),
    (TL["closing"], TL["end"], 0.4, "Dodge these traps, and your hub becomes the place everyone trusts! Let's build it right!"),
]
SR = 24000
PITCH = 1.10   # lift towards the bubbly reference (~225 Hz)


def trim(a):
    idx = np.where(np.abs(a) > 0.01)[0]
    return a[max(0, idx[0] - 240): idx[-1] + 2400]


out = np.zeros(int(TL["end"] * SR))
info = []
for t0, t1, lead, text in LINES:
    room = t1 - t0 - lead - 0.3
    speed = 1.15
    for _ in range(6):
        a, sr = k.create(text, voice=VOICE, speed=speed, lang="en-us")
        a = trim(a)
        if len(a) / SR <= room or speed > 1.5:
            break
        speed = min(1.5, speed * (len(a) / SR) / room * 1.01)
    i = int((t0 + lead) * SR)
    out[i:i + len(a)] += a[: len(out) - i]
    info.append({"start": round(t0 + lead, 2), "dur": round(len(a) / SR, 2), "speed": round(speed, 2), "text": text})
    print(info[-1])

(ROOT / "output/v4").mkdir(parents=True, exist_ok=True)
(ROOT / "output/v4/vo_lines.json").write_text(json.dumps(info, indent=1))
raw = ROOT / "output/v4/vo_raw.wav"
sf.write(raw, out, SR)
(ROOT / "assets/voiceover").mkdir(parents=True, exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af",
                f"asetrate={int(SR * PITCH)},aresample={SR},atempo={1 / PITCH:.6f},"
                "equalizer=f=3200:t=q:w=1:g=4,equalizer=f=8000:t=q:w=1:g=2,equalizer=f=220:t=q:w=1:g=-2,"
                "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2",
                "-ar", "44100", str(ROOT / "assets/voiceover/eka_vo_v4.wav")], check=True)
raw.unlink()
print("wrote assets/voiceover/eka_vo_v4.wav")
