# EKA explainer: voice-over script (60 s)

The video's scenes change on fixed beats, so each line below has a time window.
Read at a relaxed pace of about 2.5 words a second. Every line fits its window with some room to spare.

| Time | On screen | EKA says |
|---|---|---|
| 0:00–0:05 | EKA drops in and waves. Title: *Let's build an AI-powered Knowledge Hub* | "Hi, I'm EKA! Let's build an AI-powered Knowledge Hub in eight simple blocks." |
| 0:05–0:10 | Messy files, question marks, then 8 coloured blocks appear | "Too many files, and no idea which one is right? Let's fix that, block by block!" |
| 0:10–0:15 | **01 Understand**: target and arrow | "One: Understand. Who is it for, what do they ask, and where's the truth?" |
| 0:15–0:20 | **02 Content**: old files go in the bin | "Two: Content. Clear out old and duplicate files, and give every document an owner." |
| 0:20–0:25 | **03 Metadata**: tags swing onto a document | "Three: Metadata. Label everything with an owner, a status and a review date." |
| 0:25–0:30 | **04 Format**: a template builds itself | "Four: Format. Clear templates, one topic per document, and no facts hidden in pictures." |
| 0:30–0:35 | **05 Governance**: shield, tick and RACI | "Five: Governance. Agree who does what, and review content on a regular cycle." |
| 0:35–0:40 | **06 Automation**: spinning gears and a lightning bolt | "Six: Automation. Let Power Automate check tags, send reminders and flag old content." |
| 0:40–0:45 | **07 Agent**: EKA glows and a chat demo plays | "Seven: the Agent. That's me! I only answer from curated, trusted libraries." |
| 0:45–0:50 | **08 Analytics**: bars grow and a trend line rises | "Eight: Analytics. Track what people ask, fix the gaps, and keep improving." |
| 0:50–0:55 | The blocks stack into a house with confetti | "Eight blocks, one smart hub. Good content in, great answers out!" |
| 0:55–1:00 | *Your turn! Start with Block 01: Understand* | "Your turn! Start with block one: Understand. See you soon!" |

## Adding the voice-over

Record one continuous WAV file, then run:

```bash
scripts/add_voiceover.sh my_voiceover.wav        # add a second argument such as 0.3 to delay the voice
```

The script levels the voice to -16 LUFS and lowers the music automatically while EKA speaks.
The sound effects stay audible. The result is `output/eka_knowledge_hub_60s_with_vo.mp4`.
