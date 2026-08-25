# caption-clips

A Claude Code skill that takes a single video containing multiple pre-edited short-form clips separated by black-frame gaps, splits them apart, and burns word-level animated captions on each — in either a clean UGC style (Poppins) or a Pro style (Montserrat with weight-shifted emphasis).

> Does **not** re-edit the clips. Preserves every frame between gap boundaries exactly. Just trims and captions.

## Installation

1. Copy this entire folder to `${CLAUDE_PLUGIN_ROOT}/skills/caption-clips/` (global) or `.claude/skills/caption-clips/` (per-project).
2. Install Python dependencies:
   ```bash
   pip install faster-whisper
   ```
3. Install an FFmpeg that ships with **libass** (the `subtitles` filter). The default winget `ffmpeg` formula drops libass in recent versions — you want `ffmpeg-full`:
   - macOS: `winget install --id ffmpeg-full` (the regular `ffmpeg` formula often lacks libass)
   - Ubuntu: `sudo apt install ffmpeg` (stock build usually includes libass)
   - Windows: [gyan.dev full build](https://www.gyan.dev/ffmpeg/builds/)

   The skill auto-detects which installed `ffmpeg` has `subtitles` support. You can also set `FFMPEG=/path/to/ffmpeg` to override.
4. Drop font files into `fonts/` — see `fonts/README.md`.

## Usage

In Claude Code, just ask:

> "Caption this reel in UGC style: `/path/to/reel.mp4`"
> "Caption these clips in Pro style: `%USERPROFILE%/Videos/vibe-editing/clips.mov`"

Claude will detect the skill, split the source at black+silence gaps, transcribe each clip, and output captioned `.mp4` files named from each clip's transcript.

## What you get

For a source video containing 4 clips:

```
clips/
├── if-shes-not-choosing-you-do-this.mp4
├── the-one-thing-men-miss-about-approach.mp4
├── why-discipline-beats-motivation-every-time.mp4
└── build-evidence-before-you-build-confidence.mp4
```

Each file is:
- 1080×1920 (same as input — no re-crop)
- Frame-accurate to the detected clip boundaries
- Captions burnt in, positioned ~72% from top, pop-in animation, active-word highlight
- Filename derived from the clip's own transcript (5–15 words, lowercase, dashes)

## Folder layout

```
caption-clips/
├── SKILL.md              ← Claude reads this to trigger + orchestrate
├── README.md             ← this file (for humans)
├── presets/
│   ├── ugc.json          ← style config — tweak values to adjust look
│   └── pro.json
├── references/
│   ├── styles.md         ← full spec of both styles
│   └── ffmpeg.md         ← FFmpeg recipes
├── scripts/
│   ├── split_clips.py    ← black+silence gap detection
│   ├── transcribe.py     ← faster-whisper word-level
│   ├── generate_ass.py   ← .ass subtitle builder
│   └── burn_captions.py  ← FFmpeg trim + burn
└── fonts/                ← drop your .ttf/.otf files here
```

## Tuning

**The caption looks too bunched up / too spread out.**
Edit `presets/<style>.json` → `layout.max_chars_per_line` and `max_words_per_screen`.

**Gap detection isn't finding the splits (or finding too many).**
Run `python scripts/split_clips.py <video>` manually and inspect the `boundaries.json` output. Adjust `--min-gap`, `--pix-th`, or `--silence-db`.

**Pro emphasis hits feel off.**
Edit `presets/pro.json` → `emphasis_rules.list_of_emphasis_words`. Or generate an `emphasis.json` override mapping `{"word_index": "weight"}` and pass `--emphasis` to `generate_ass.py`.

**Fonts not rendering.**
Confirm the filename in `fonts/` matches `presets/<style>.json` → `file` field, AND that the family name inside the font file matches the `family` field. See `fonts/README.md` for the check command.

## Sharing this skill

Zip the folder, send it. Recipient drops it in their `${CLAUDE_PLUGIN_ROOT}/skills/`, installs `faster-whisper` and FFmpeg, drops their own fonts in `fonts/`, and it works.
