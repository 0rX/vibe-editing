# Segment → Select → Tighten (Julian IP integration)

New additive layer that upgrades the clip-miner front of house: **split** a long-form Q&A/Hotline into
clean exchanges, **select** what to clip per-exchange, and **tighten** each cut — all ported from
Julian's SEGMENTER-X and CLIPPER_X. Nothing here replaces `tam_select.py`; it wraps and feeds it.
**This is the basis for the upcoming Hotline (call-in) pipeline** — the stereo diarizer and the
host/caller-aware prompts are built for that next.

## The flow

```
long-form transcript ({segments:[{start,end,text[,words]}]} or .txt)
   │
   ├─(optional, Hotline/Q&A) transcribe_isolated.py  ── clean host/caller attribution
   │
   ▼
tam_segment.py  ── split into EXCHANGES + carve FILLER          → <out>.segments.json/.md
   │   (windows ~28 min so 90-min sessions don't blow the token ceiling, then merges)
   ▼
tam_pipeline.py ── for each NON-filler exchange, slice its window → tam_select.py
   │                                                                → <out>.picks.json/.md (ranked)
   ▼
(build candidates.json from the MINE picks — existing step 4 in SKILL.md)
   │
   ▼
tam_tighten.py  ── HOOK→MEAT→PAYOFF keep/remove/trim per exchange → cuts JSON (merge w/ detect_fillers)
   ▼
tam_coherence.md ── (prompt) incomplete-thought check before render
```

`tam_pipeline.py` is the one-command orchestrator for the first two boxes:

```bash
python scripts/tam_pipeline.py --transcript session.json --format hotline \
        --top-per 3 --top 20 --out %USERPROFILE%/Videos/vibe-editing/<brand>/<job>/10_WORK/session
# → session.segments.json/.md  (exchanges, filler flagged)
# → session.picks.json/.md     (combined ranked MINE/MAYBE across all exchanges)
```

## New files

| File | Purpose |
|------|---------|
| `prompts/tam_segment.md` | Q&A/Hotline segmentation system prompt (ported from SEGMENTER-X `segment-system.ts`). Splits into exchanges, carves filler into `Filler – …` segments, word-level start/end. |
| `scripts/tam_segment.py` | Headless segmenter. Formats transcript as `[LINE N] / [WORDS N] word@ts`, clamps Claude's startSec/endSec to the line range, **windows ~28 min + merges with offset-corrected indices** (fixes SEGMENTER-X's single-pass token limit). Out: `{exchanges:[{start,end,title,summary,is_filler,speaker_lead}]}`. |
| `scripts/tam_pipeline.py` | Thin orchestrator: transcript → `tam_segment` → per non-filler exchange → `tam_select` → combined `<out>.picks.json/.md`, globally re-ranked. |
| `scripts/transcribe_isolated.py` | Stereo host/caller diarization (ported from CLIPPER_X `transcribe.py`): detect channel-isolated stereo via per-50ms RMS-envelope Pearson correlation (corr<0.65 ⇒ isolated), transcribe **each channel separately with Groq large-v3** (whisper-cli fallback), emit `{segments:[{start,end,text,speaker}]}` with speaker = host/caller. Mono/cross-talk → mono mix, speaker="unknown". **No Deepgram.** Built for Hotline. |
| `prompts/tam_tighten.md` | Within-clip HOOK→MEAT→PAYOFF keep/remove/trim editor (ported from CLIPPER_X `default-edit.ts`). |
| `scripts/tam_tighten.py` | Optional runner: runs the tighten prompt (uses the `submit_edit_decisions` tool, CLI line-parse fallback), converts KEEP/REMOVE/TRIM → cut intervals `{cuts:[{start,end,reason}]}` (mergeable with `detect_fillers.py` for `cut_clip.py --fillers`). Needs per-utterance word timing. |
| `prompts/tam_coherence.md` | Incomplete-thought / contextless-reference coherence validator (ported from CLIPPER_X `validate-assembly.ts`). Use after tighten, before render. |
| `scripts/_selftest.py` | Offline self-test of the pure helpers on a synthetic transcript (no API/ffmpeg). `python _selftest.py`. |

## What was ported from each repo

**SEGMENTER-X**
- `segment-system.ts` → `tam_segment.md` (adapted to Speaker Q&A/Hotline; filler list made concrete:
  pump-up, calling next guest, "can you hear me", ad reads, sign-off banter).
- `/api/segment` route → `tam_segment.py`: the `[LINE N]` + `[WORDS N] word@ts` formatting and the
  **timestamp clamp** (trust word-level start/end only inside the claimed line's range).
- Its single-pass `max_tokens` failure mode (route returns "split the source video") → **fixed** here
  with windowing + offset-corrected merge.

**CLIPPER_X**
- `scripts/transcribe.py` channel-isolation (`_read_stereo_pcm`, `is_channel_isolated`,
  `extract_channel`) → `transcribe_isolated.py` (logic verbatim; backend swapped Deepgram→Groq).
- `prompts/default-edit.ts` → `tam_tighten.md` + the `submit_edit_decisions` schema in `tam_tighten.py`.
- `validate-assembly.ts` → `tam_coherence.md` (+ `submit_validation` shape).

## What was changed / dropped

- **DROPPED the word budget.** CLIPPER_X's `<word_budget>300–400 words / ~60s</word_budget>` is gone.
  Our clips are **content-driven 25–150s** — `tam_tighten.md` explicitly forbids padding to or capping
  at any length.
- **DROPPED "cut everything after the last payoff" / "nothing trails."** Kept the editorial logic
  (lead on caller's problem+numbers, never open on host, protect revenue/lead numbers, kill
  filler/false-starts, strongest-example-only) but the clip may keep a second payoff / clean button
  and must simply end on a complete thought.
- **No Deepgram.** Stereo transcription uses Groq whisper-large-v3 (whisper-cli offline fallback).
- **Hotline-first additions** (not in either repo): `speaker_lead` per segment; `is_filler` flag;
  per-50ms isolation detect wired to host/caller labels; filler list tuned to live Hotline patterns.

## How to run it on the next Q&A

```bash
# 1) transcribe (Groq large-v3). For a STEREO call-in, get host/caller labels in one shot:
GROQ_API_KEY=… python scripts/transcribe_isolated.py call.mp4 --out 10_WORK/call.transcript.json
# (mono Q&A: use the existing transcribe_groq.py → {segments:[{start,end,text}]})

# 2) segment → select in one command (writes .segments.* and .picks.*):
python scripts/tam_pipeline.py --transcript 10_WORK/call.transcript.json --format hotline \
        --top-per 3 --out 10_WORK/call
# Then cut the MINE picks (SKILL.md step 4+), and per clip run tam_tighten.py and merge its cuts
# with detect_fillers.py before cut_clip.py --fillers.
```
