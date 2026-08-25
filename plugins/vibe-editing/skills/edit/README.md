# edit

THE master clip-creation orchestrator. Raw footage in, finished short-form clips out.

## What it does

One universal 13-step spine for ALL footage types — monologue, Q&A, hotline, podcast, multicam:

```
scaffold → detect → transcribe → mine → pick → validate → cut + clean →
QC → reframe → caption → music → hard end → audit → deliver
```

Two branch points: **speaker count** (1 vs 2) and **camera count** (1 vs multi). Everything else is the same.

## Inputs

- Raw footage (MP4/MOV, any resolution)
- Optional: separate lav/mic WAVs, EDL, sync config

## Outputs

Finished clips in `%USERPROFILE%/Videos/vibe-editing/<brand>/YYYY-MM-DD_<slug>/20_DELIVER/`, Brand-named.

## Downstream skills (this skill orchestrates, they own their capability)

| Skill | Capability |
|---|---|
| `horizontal-to-vertical` | Face-tracking + 16:9→9:16 reframe |
| `caption-clips` | SPICE captions (Montserrat, per-word emphasis) |
| `script-cut` | MFA forced-alignment precision cutting |
| `sf-audit` | Mechanics audit gate |
| `scorecard-audit` | Narrative audit gate |
| `_shared/` | Shared engines (precision_cut, fast_encode, window_validator, parallel) |

## Key rule

This skill ORCHESTRATES. It owns mining, boundary-picking, filler surgery, and the delivery handoff. For each downstream step it says "use skill: X" — it never duplicates their instructions.

## Usage

In Claude Code: `/edit` or ask for clips.

## Dependencies

- FFmpeg (with libass)
- Python 3.10+
- Groq API key (for transcription) or faster-whisper (local fallback)

## Note on `assets/`

The `assets/` directory (overlay / transition / text media packs, ~11GB) is **gitignored** —
it's binary media, not skill logic, and exceeds GitHub's file-size limits. Those packs live
locally only. Everything that defines the skill's behavior (SKILL.md, `references/`, `config/`,
`presets/`, `prompts/`, `scripts/`, `luts/`) is tracked.
