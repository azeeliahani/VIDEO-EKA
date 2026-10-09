#!/usr/bin/env bash
# Adds a voice-over to the finished video and automatically ducks the music under the voice.
#
#   scripts/add_voiceover.sh path/to/voiceover.wav [offset_seconds]
#
# Uses the separate stems (music.wav, sfx.wav) so the voice stays clear while the
# sound effects keep their punch. Writes output/eka_knowledge_hub_60s_with_vo.mp4
set -euo pipefail
cd "$(dirname "$0")/.."
VO="${1:?usage: scripts/add_voiceover.sh voiceover.wav [offset_seconds]}"
OFFSET_MS=$(awk "BEGIN{printf \"%d\", ${2:-0}*1000}")
ffmpeg -y -i output/eka_knowledge_hub_60s_noaudio.mp4 -i "$VO" -i output/music.wav -i output/sfx.wav -filter_complex "
  [1:a]aresample=44100,aformat=channel_layouts=stereo,adelay=${OFFSET_MS}|${OFFSET_MS},apad,loudnorm=I=-16:TP=-1.5:LRA=7,asplit=2[vo][key];
  [2:a][key]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350[bed];
  [3:a]volume=-3dB[fx];
  [bed][fx][vo]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.9[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 256k -t 60 -movflags +faststart output/eka_knowledge_hub_60s_with_vo.mp4
echo "wrote output/eka_knowledge_hub_60s_with_vo.mp4"
