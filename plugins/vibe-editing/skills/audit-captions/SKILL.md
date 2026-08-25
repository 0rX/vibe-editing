---
name: audit-captions
description: >
  Dedicated caption auditor. Receives a rendered clip and checks ONLY caption quality:
  accuracy vs spoken audio, speaker color attribution, timing sync, formatting, emphasis,
  and positioning. Runs in fresh context with NO knowledge of how the clip was made.
  Returns structured pass/fail per check with specific timestamps for failures.
  Part of the post-render audit fan-out at edit step 9.
---

# audit-captions — caption-only quality gate

> Fresh-context agent. Receives ONLY the rendered mp4. Does NOT know the transcript,
> the editing decisions, or the source footage. Tests what a VIEWER would see.

## How to run

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/audit-captions/scripts/check.py \
    --clip 20_DELIVER/v1/clip.mp4 \
    --out 10_WORK/audit_captions.json
```

If the clip has a corresponding `.ass` subtitle file in `10_WORK/`, pass it:
```bash
python ... --ass 10_WORK/captions.ass
```

## What it checks

### 1. ACCURACY — do captions match spoken words?
Burnt captions are CHUNK-displayed stylized text: punctuation stripped by design,
case folded, numbers digit-formed, verbal fillers and false starts dropped. The
comparison is therefore NORMALIZED and WER-gated, not word-exact:
- Layered .ass events (shadow + main) are deduplicated to unique display chunks
- Both sides are normalized (case/punctuation folded, digit ↔ number-word
  equivalence, safe contraction expansion) and sequence-aligned
- Missing runs of ≤4 consecutive words are stylistic trims (dropped fillers /
  false starts — by design); runs of ≥5 words are content loss
- **FAIL** if WER >6% (substitutions + content-loss missing + extra, over spoken
  words) or any 3+ consecutive-word substitution run (wrong text on screen)
- Token diffs within the threshold are reported as `sample_diffs` (ASR noise)

### 2. SPEAKER ATTRIBUTION — right color on right speaker?
- Speaker count comes from the render metadata (`clip.contract.json` via
  `_shared/clip_meta.py`); 1 declared speaker → uniform color is CORRECT (pass)
- 2+ declared speakers → the dialogue events must use ≥2 distinct primary colors
- **FAIL** if 2+ speakers all render in one color

### 3. TIMING SYNC — do captions appear/disappear with speech?
Chunk-display engines legitimately show a sentence-final word in the NEXT chunk
(isolated 0.5–0.8s per-word lag at chunk boundaries is by-design), and captions
lead by 3–5 frames per SOP. The blocking tests are SYSTEMIC, against each chunk's
ALIGNED first word (not nearest-same-word anywhere):
- **FAIL** if the track median lags speech >350ms or runs >600ms ahead (track-level
  desync — shifted captions), or >25% of chunks lag their words by >450ms
- **FAIL** any single chunk >1.2s late or >1.2s early; **WARN** >450ms late

### 4. FORMATTING — correct style applied?
- Font: Montserrat (or the brand's canonical font)
- Size: base size appropriate for resolution, emphasis bumps correct
- Position: within safe zone, not overlapping face
- Width: ≤80% of frame width
- No punctuation (per Speaker/SF standard, unless brand override)
- Single-line ≤18 chars or ≤3 words per line
- **FAIL** if any formatting rule is violated

### 5. EMPHASIS — are bold/size bumps on the right words?
- Money amounts, key nouns, emotional peaks should have emphasis
- Filler words should NEVER be emphasized
- Check that emphasis matches the speaker's vocal stress (louder = emphasis)
- **WARN** if emphasis seems misplaced (not a hard fail)

### 6. GAPS — any uncaptioned speech?
- Caption chunk intervals are merged into a proper interval union (display tolerance
  −0.2s/+0.3s); a spoken word is uncovered if its midpoint falls outside the union
- **FAIL** on any uncovered span ≥0.8s containing ≥2 words

## Output format

```json
{
  "clip": "clip.mp4",
  "verdict": "PASS",
  "transcript_words": 182,
  "caption_chunks": 64,
  "checks": {
    "accuracy": {"pass": true, "wer": 0.0, "substitutions": 0,
                 "missing_content_words": 0, "extra_words": 0,
                 "stylistic_trims": 4, "issues": []},
    "timing": {"pass": true, "median_offset_ms": 0, "late_chunk_fraction": 0.03,
               "chunks_timed": 64, "issues": []},
    "gaps": {"pass": true, "issues": []},
    "speaker_color": {"pass": true, "note": "single speaker — uniform caption color is correct"},
    "formatting": {"pass": true, "issues": []}
  },
  "metadata": {"ass": "10_WORK/captions_work/subs.ass", "speakers": 1,
               "resolved_from": "contract/manifest"},
  "summary": "All caption checks passed"
}
```

The `.ass` source auto-resolves from the clip's project (`captions_work/subs.ass`)
when `--ass` isn't passed.

Calibration (2026-06-12): thresholds set against a 22-clip human-reviewed known-good
batch (all PASS, including clips whose captions intentionally drop "you know" /
false-start fillers) and proven against constructed defects — another clip's .ass
FAILs accuracy+timing+gaps; a +1.5s-shifted .ass FAILs as "caption track lags speech
by 1500ms (median) — track-level desync".

## Integration with edit pipeline

Called at edit step 9 alongside audit-audio, audit-visual, audit-script.
On FAIL: return specific fix instructions to the editing session.
- Accuracy error → fix in `captions.ass`, re-render with `--bump` (~30s)
- Color error → fix speaker tag in `captions.ass`, re-render
- Timing error → adjust timestamps in `captions.ass`, re-render

The fix is always in `captions.ass` — the render cache means only caption stage + downstream re-runs.
