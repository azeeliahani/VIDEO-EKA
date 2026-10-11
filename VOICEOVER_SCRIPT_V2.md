# EKA: Enterprise Knowledge Hub, voice-over script (60 s)

For the video `output/v2/eka_enterprise_knowledge_hub_60s.mp4`.
The voice is modelled on ElevenLabs' **Allison (Energetic, Clear and Bubbly)**. The reference clip is `assets/source/voice_reference_allison_energetic.mp3`.
Each line fits its 5-second scene, so the voice lands on the music's bar lines.

| Time | On screen | EKA says |
|---|---|---|
| 0:00–0:05 | EKA drops in: *Building an Enterprise Knowledge Hub* | "Hi, I'm EKA! Let's build an Enterprise Knowledge Hub in eight simple steps!" |
| 0:05–0:10 | **01 Understand** | "One: Understand. Know your users, their questions, and trusted sources." |
| 0:10–0:15 | **02 Content** | "Two: Content. Keep it accurate and current. Good content means good answers!" |
| 0:15–0:20 | **03 Metadata** | "Three: Metadata. Tags, owners and review dates help Copilot know what to trust." |
| 0:20–0:25 | **04 Format** | "Four: Format. Clear headings and simple language mean better answers." |
| 0:25–0:30 | **05 Governance** | "Five: Governance. Owners and access rules keep information secure and reliable." |
| 0:30–0:35 | **06 Automation** | "Six: Automation. Let workflows handle reviews, approvals and updates." |
| 0:35–0:40 | **07 Copilot Agent** (EKA: "That's me!") | "Seven: Copilot Agent. That's me! Connect me to trusted content, with a clear purpose." |
| 0:40–0:45 | **08 Analytics** | "Eight: Analytics. Track usage, feedback and unanswered questions to keep improving." |
| 0:45–0:52 | The blocks stack into the hub. *Trusted content · Clear governance · Continuous improvement* | "A successful knowledge hub starts with trusted content, clear governance, and continuous improvement." |
| 0:52–1:00 | *Copilot delivers accurate knowledge & helps people work smarter* | "Get these foundations right, and Copilot delivers accurate knowledge, so everyone works smarter!" |

## Plain text for ElevenLabs

Paste this as one block. The blank lines give natural pauses between scenes.

```
Hi, I'm EKA! Let's build an Enterprise Knowledge Hub in eight simple steps!

One: Understand. Know your users, their questions, and trusted sources.

Two: Content. Keep it accurate and current. Good content means good answers!

Three: Metadata. Tags, owners and review dates help Copilot know what to trust.

Four: Format. Clear headings and simple language mean better answers.

Five: Governance. Owners and access rules keep information secure and reliable.

Six: Automation. Let workflows handle reviews, approvals and updates.

Seven: Copilot Agent. That's me! Connect me to trusted content, with a clear purpose.

Eight: Analytics. Track usage, feedback and unanswered questions to keep improving.

A successful knowledge hub starts with trusted content, clear governance, and continuous improvement.

Get these foundations right, and Copilot delivers accurate knowledge, so everyone works smarter!
```

## The voice-over in the current video

`assets/voiceover/eka_vo_v2.wav` is generated offline by `scripts/make_voiceover_v2.py` with Kokoro TTS (voice `af_bella`, pitch lifted slightly towards Allison).
There was no ElevenLabs API access when it was built.

## Swapping in an ElevenLabs recording

Generate the plain text above with Allison and export one MP3.
Then run:

```bash
python3 scripts/make_audio_v2.py --vo my_voiceover.mp3      # ducks the music and writes EKA's lip-sync data
MIX=mix_vo.wav VIDEO=v2 node scripts/render.js              # re-renders so EKA's mouth moves with the voice
```

If a scene's line runs long or short, adjust the start times in `src/timeline_v2.js`, then re-run both commands.
Everything, including the music and sound effects, re-times itself to match.
