"""Narration for the v2 video: Kokoro neural TTS (voice af_bella), one line per scene.

The ElevenLabs "Allison - Energetic, Clear and Bubbly" recording in assets/source/ is the voice reference.
af_bella with a slight pitch lift is the closest offline match. Each line is fitted into its 5 s
scene slot (src/timeline_v2.js), so the voice lands on the music's bar lines.

Setup (offline model, ~160 MB, from npm):
    pip install sherpa-onnx soundfile
    (cd /tmp && npm pack n8n-nodes-ttsbro && tar xzf n8n-nodes-ttsbro-*.tgz)
    KOKORO=/tmp/package/kokoro-int8-en-v0_19 python3 scripts/make_voiceover_v2.py

Writes assets/voiceover/eka_vo_v2.wav. Then:
    python3 scripts/make_audio_v2.py --vo assets/voiceover/eka_vo_v2.wav
    MIX=mix_vo.wav VIDEO=v2 node scripts/render.js
"""
import os
import subprocess
from pathlib import Path

import numpy as np
import sherpa_onnx
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
M = os.environ.get("KOKORO", "/tmp/package/kokoro-int8-en-v0_19")
tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
    kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=f"{M}/model.int8.onnx", voices=f"{M}/voices.bin", tokens=f"{M}/tokens.txt", data_dir=f"{M}/espeak-ng-data"), num_threads=4)))
SID = 1  # af_bella
# (slot start, slot length, lead-in, text)
L = [
 (0, 5, 0.9, "Hi, I'm Eka! Let's build an Enterprise Knowledge Hub in eight simple steps!"),
 (5, 5, 0.2, "One: Understand. Know your users, their questions, and trusted sources."),
 (10, 5, 0.2, "Two: Content. Keep it accurate and current. Good content means good answers!"),
 (15, 5, 0.2, "Three: Metadata. Tags, owners and review dates help Copilot know what to trust."),
 (20, 5, 0.2, "Four: Format. Clear headings and simple language mean better answers."),
 (25, 5, 0.2, "Five: Governance. Owners and access rules keep information secure and reliable."),
 (30, 5, 0.2, "Six: Automation. Let workflows handle reviews, approvals and updates."),
 (35, 5, 0.2, "Seven: Copilot Agent. That's me! Connect me to trusted content, with a clear purpose."),
 (40, 5, 0.2, "Eight: Analytics. Track usage, feedback and unanswered questions to keep improving."),
 (45, 7.5, 0.6, "A successful knowledge hub starts with trusted content, clear governance, and continuous improvement."),
 (52.5, 7.5, 0.5, "Get these foundations right, and Copilot delivers accurate knowledge, so everyone works smarter!"),
]
SR = 24000; P = 1.05  # gentle pitch lift towards the reference voice (~228 Hz)
out = np.zeros(int(60 * SR)); report = []
def trim(a):
    idx = np.where(np.abs(a) > 0.01)[0]; return a[max(0, idx[0] - 240): idx[-1] + 2400]
for t0, slot, lead, text in L:
    room = slot - lead - 0.35
    speed = 1.12
    for _ in range(6):
        a = trim(np.array(tts.generate(text, sid=SID, speed=speed).samples))
        if len(a) / SR <= room: break
        speed *= (len(a) / SR) / room * 1.01
    i = int((t0 + lead) * SR); out[i:i + len(a)] += a[: len(out) - i]
    report.append((t0, round(speed, 2), round(len(a) / SR, 2), text[:40]))
for r in report: print(r)
raw = ROOT / "output/v2/vo_raw.wav"
raw.parent.mkdir(parents=True, exist_ok=True)
sf.write(raw, out, SR)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af",
  f"asetrate={int(SR*P)},aresample={SR},atempo={1/P:.6f},equalizer=f=3500:t=q:w=1:g=3,equalizer=f=200:t=q:w=1:g=-2",
  "-ar", "44100", str(ROOT / "assets/voiceover/eka_vo_v2.wav")], check=True)
raw.unlink()
print("wrote assets/voiceover/eka_vo_v2.wav")
