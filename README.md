# EKA explainer: Building an AI-Powered Knowledge Hub

A 60-second motion graphic explainer for beginners, presented by **EKA** the robot.
It turns the *"Eight building blocks of an AI-powered knowledge hub"* slide into an animated story.

**Final video:** `output/eka_knowledge_hub_60s.mp4` (1920×1080, 30 fps, with music and sound effects)

## Storyboard

| Time | Scene |
|---|---|
| 0–5 s | EKA drops in, lands with a bounce and waves: "Hi, I'm EKA!" The title builds and the 8 blocks bounce in |
| 5–10 s | The problem: messy, duplicated files and confused question marks. The files get sucked away and turn into 8 building blocks |
| 10–50 s | One card per block, 5 s each, each with its own animated icon. A progress tracker at the bottom ticks off each block as EKA presents it |
| 40–45 s | Block 07, Agent: EKA's moment. EKA grows and glows, sparkles appear, and a live chat demo plays |
| 50–55 s | Recap: the blocks stack into a house with an "AI Knowledge Hub" roof, then confetti |
| 55–60 s | Call to action: *Start with Block 01: Understand* |

## Audio

The music and sound effects are synthesised from scratch in `scripts/make_audio.py`, so they are royalty-free.
The music is an upbeat 96 BPM marimba, bell and drum groove, and the scenes change on its bar lines.
There are about 150 sound-effect cues: pops, whooshes, boings, robot beeps, dings, clanks, zaps, sparkles and a ta-da.

| File | Contents |
|---|---|
| `output/mix.wav` | Music and SFX together (used in the final video) |
| `output/music.wav` | Music bed only |
| `output/sfx.wav` | Sound effects only |
| `output/eka_knowledge_hub_60s_noaudio.mp4` | Picture only, for editing in another tool |

To add the voice-over, see [VOICEOVER_SCRIPT.md](VOICEOVER_SCRIPT.md).
It has a line-by-line script timed to each scene, and `scripts/add_voiceover.sh` mixes in your recording and ducks the music under it automatically.

## Rebuilding

Requires Node 18+, Python 3 with numpy and Pillow, ffmpeg, and Playwright's Chromium.

```bash
npm install
npm run cutout     # cut EKA out of the white background and split off the waving arm
npm run audio      # synthesise music.wav, sfx.wav and mix.wav
npm run frames     # render 1800 frames with Playwright and encode them with ffmpeg
```

To preview in a browser, open `src/video.html#play`.
For quick stills, run `node scripts/render.js --stills 12.5,42`.
The text, colours and timings are all in `src/video.html`. The `BLOCKS` array holds each card's wording.
