---
name: audit-audio
description: >
  Dedicated audio auditor. Receives a rendered clip and checks ONLY audio quality:
  word clipping, pops/clicks at splice points, level consistency, buzz/hum, music bed
  balance, clean open/close. Runs in fresh context — audio only, no video.
  Returns structured pass/fail per check with timestamps for failures.
  Part of the post-render audit fan-out at edit step 9.
---

# audit-audio — audio-only quality gate

> Fresh-context agent. Receives ONLY the audio track (video stripped).
> Cannot be biased by seeing the visuals. Tests what a LISTENER would hear.

## How to run

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/audit-audio/scripts/check.py \
    --clip 20_DELIVER/v1/clip.mp4 \
    --out 10_WORK/audit_audio.json
```

## What it checks

### 1. WORD CLIPPING — any words cut off?
- Transcribe the audio independently; ASR word durations are HYPOTHESES, not verdicts
- The forced aligner glitches at clip start: the FIRST word routinely reports a tiny
  duration on clips whose waveform attack is clean — first-word ASR flags are
  suppressed (reported as `suppressed_aligner_glitches`), never failed
- Zero-gap opens / hard-ends legitimately put near-full voice level at the literal
  clip edges, so a hot edge alone is not evidence either
- **FAIL** only when the LAST word is ASR-short AND the waveform confirms the audio
  ends at full voice level (cut mid-decay) — corroboration on both channels
- Head/tail edge levels are always reported (`head/tail_edge_db_below_speech`) for
  the reviewing agent to eyeball

### 2. POPS AND CLICKS — any splice artifacts?
- At every edit point (detected via waveform discontinuity), check for:
  - Click/pop: sudden amplitude spike >6dB above surrounding 50ms
  - DC offset jump at splice boundary
- Extract the waveform around each detected splice, measure peak-to-surrounding ratio
- **FAIL** if any pop/click detected

### 3. LEVEL CONSISTENCY — voice volume steady throughout?
- Measure LUFS per segment (between splice points)
- All speech segments should be within ±3 LUFS of each other
- No segment should be >6 LUFS different from the average
- **FAIL** if any segment is >6 LUFS off, **WARN** if >3 LUFS off

### 4. MUSIC BED BALANCE — music sitting correctly under voice?
- The declared music bed is read from the render metadata (`clip.contract.json` /
  `manifest.json` via `_shared/clip_meta.py`); no music declared → check passes with note
- Bed level is measured in isolatable speech gaps (≥0.4s), compared against voiced level
- Target separation is 10–13dB; **FAIL** if the bed is within 6dB of voice,
  **WARN** within 9dB. No gap long enough to isolate the bed → pass with note (ear check)

### 5. BUZZ AND HUM — any electrical noise?
- Real mains hum must be TONAL (narrowband prominence ≥10dB over its spectral
  neighborhood), PERSISTENT (≥75% of 2s windows), and GRID-LOCKED (within ±0.7Hz of
  an exact 50/60Hz harmonic — equal-temperament musical notes all miss this window)
- A single grid tone also needs harmonic-family evidence (≥2 family members) or to be
  very loud and steady (≥18dB prominent, ≥90% persistent)
- A music bed's harmonic content (e.g. 300Hz piano partials, sustained drones at
  47–49Hz) fails these criteria and can no longer fail the gate
- **FAIL** if a confirmed hum sits within 25dB of the speech band, **WARN** within 35dB
- `top_candidates` in the output always shows the 3 most hum-like frequencies with
  their measurements, for transparency

### 6. CLEAN OPEN AND CLOSE
- Measured on the VOICE-BAND (300–3400Hz) envelope, anchored at t=0 and t=end —
  a sparse music bed cannot register as either voice or "dead air"
- **Open:** first sustained voice onset. Known-good clips open at 20–70ms.
  **WARN** >120ms, **FAIL** >250ms before first voice
- **Close:** trailing time after the last sustained voice. A declared music fade-out
  doesn't count (voice-band). **WARN** >0.5s, **FAIL** >0.9s after last voice

## Output format

```json
{
  "clip": "clip.mp4",
  "verdict": "PASS",
  "speech_level_db": -21.4,
  "checks": {
    "word_clipping": {"pass": true, "issues": [],
      "head_edge_db_below_speech": 22.6, "tail_edge_db_below_speech": 35.3,
      "total_words": 182},
    "pops_clicks": {"pass": true, "issues": []},
    "level_consistency": {"pass": true, "avg_voice_db": -23.2, "range_db": 3.4},
    "buzz_hum": {"pass": true, "music_declared": true, "top_candidates": [
      {"freq_hz": 102.5, "prominence_db": 7.2, "persistence": 0.65, "below_speech_db": 18.9}
    ]},
    "clean_open_close": {"pass": true, "open_onset_ms": 70, "close_tail_ms": 195},
    "music_balance": {"pass": true, "voice_over_bed_db": 19.1, "music": "track.mp3"}
  },
  "metadata": {"music_declared": true, "segments": 7, "resolved_from": "contract/manifest"},
  "summary": "All audio checks passed"
}
```

Calibration (2026-06-12): thresholds were set against a 22-clip human-reviewed
known-good batch (all PASS) and proven against constructed defects — injected 60Hz
mains hum FAILs at 28.5dB prominence; 1.5s of prepended dead air FAILs at 1580ms.

## Fix instructions on failure

- Word clipping → adjust end time in `cuts.json` to include full word + true-end silence, re-render
- Pop/click → a seam was hand-rolled without fade; re-cut with `precision_cut.py` (it fades seams)
- Level inconsistency → add per-segment loudnorm in the mix stage config
- Music too loud → lower `music_lufs` in `manifest.json` → `stages.mix`, re-render (~30s)
- Buzz/hum → apply notch filter (120/180/240/300/360/480/600Hz) to source before re-cut
- Dirty open/close → trim head/tail in `cuts.json`, re-render
