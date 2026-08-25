---
name: audit-visual
description: >
  Dedicated visual auditor. Receives a rendered clip with audio STRIPPED and checks ONLY
  visual quality: face tracking stability, framing consistency, jump cuts, frozen frames,
  black frames, rendering artifacts. Cannot see captions (they're burnt in — use audit-captions
  for that). Runs in fresh context with NO editing knowledge.
  Returns structured pass/fail per check with frame numbers for failures.
  Part of the post-render audit fan-out at edit step 9.
---

# audit-visual — visual-only quality gate

> Fresh-context agent. Receives ONLY the video frames (audio stripped).
> Checks what a VIEWER would see, ignoring what they'd hear.

## How to run

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/audit-visual/scripts/check.py \
    --clip 20_DELIVER/v1/clip.mp4 \
    --project 10_WORK/clips/<Slug> \
    --out 10_WORK/audit_visual.json
```

**ALWAYS pass `--project`** (the clip's work dir) — it reads the real cut seams so the within-shot
**pan gate** fires hard. Without it, seams are self-detected (loose) and panning only warns.
Optional: `--contact-sheet` to generate a visual grid for manual review.

## What it checks

### 1. CROP STABILITY — the authoritative check (background phase-correlation)
The defect a viewer sees is the CROP WINDOW jumping, not the subject moving. The
crop is rigid: if it jumps, the static background moves with it. So the gate
phase-correlates the static top band of the frame (top 22%) and reads the clip's
REAL cut boundaries from the render pipeline (`10_WORK/stages/cut/<hash>.meta.json`
via `_shared/clip_meta.py`) — same-angle jump cuts are content seams, never
"tracking failures". Without metadata, seams are self-detected from frame-diff spikes.
- **Within a shot:** vertical crop step ≥1.2% of height, step-confirmed (neighbors
  stay shifted) = **FAIL**. Unconfirmed transients are reported, not failed.
- **Across seams:** the Y-axis must hold (Y-lock / global-Y). Background dY ≥1.5%
  across a cut = **FAIL**, ≥0.9% = **WARN**. X may legitimately re-center.
  (Known-good seams measure 0.0–0.08% dY; one accepted outlier at 0.73%.)
- **Zoom exemption:** punch-in zooms read as band motion but are intentional — a
  zoom is detected (left/right band halves move horizontally in opposite directions)
  and exempted, counted in `zoom_moves_within_shots` / `zoom_seams`.
- **Horizontal PAN within a shot = FAIL** (2026-06-12, Guest159 regression): >8% within-shot
  horizontal crop drift (when seams are known via `--project`, bg static) = the frame is FOLLOWING
  the subject instead of holding — the "terrible keyframe" defect. Fix = reframe with `--lock-x`
  (auto-on for the `podcast` preset). Small dx for true re-centering at a content cut is exempt;
  in self-detected (loose) mode it warns rather than fails.
- **OVER-ZOOM = FAIL** (2026-06-12): face AREA >20% of frame = head cropped / too tight. A chest-up
  podcast/talking-head reframe sits ~8-14% (measured: known-good L3 clips 7.9-8.2%; the over-zoom
  batch 20.7-23.5%). 16-20% = warn. Cause = applying source-intel's zoom (1.4-2.2) on already-chest-up
  footage; fix = `--preset podcast` (zoom 1.0) from the 4K master.
- Moving-content footage (handheld, b-roll) is detected via baseline band motion and
  the stability checks are skipped with a note rather than false-failing.

### 2. FACE TRACKING — advisory + corroboration
- Face detection (YuNet, continuity-tracked, median-smoothed — detector flicker
  cannot fail a clip)
- **FAIL** if the subject drifts outside the center band (cx beyond 0.22–0.78) for
  >1.5s sustained — tracker lost the subject
- **WARN** if face detected in <60% of samples (coverage too low to audit)
- **WARN** if the subject's eyeline shifts >6% across a seam (pose change at a jump
  cut is normal); escalates to **FAIL** only when crop_stability proved the
  background also moved at that same seam

### 3. FRAMING — advisory only
- Face-size variation per segment (median-smoothed); punch-in zooms and leaning
  toward camera are intentional style devices, so face size never blocks a clip
- **WARN** >40% sustained deviation within a shot — eyeball it
- Stability gating lives in crop_stability

### 4. FROZEN FRAMES — any held/repeated frames?
- Compare consecutive frames for exact or near-exact duplicates
- A single duplicate = normal (frame timing). 3+ consecutive identical frames = frozen
- Especially check at scene cut boundaries (reframer "holding" when face lost)
- **FAIL** if >3 consecutive identical frames found

### 5. BLACK FRAMES — any rendering gaps?
- Scan for frames that are all-black (or near-black, mean pixel value <5)
- A single black frame at a cut point is suspicious
- Multiple black frames = rendering failure
- **FAIL** if any black frames found

### 6. FIRST AND LAST FRAME — clean open and close?
- First frame: should show the speaker, not black, not a title card, not a random frame
- Last frame: should be a live frame of the speaker, not frozen, not fading to black
- **FAIL** if first or last frame is black/frozen/artifact

### 7. ASPECT RATIO — correct 9:16 vertical?
- Final clip should be 1080x1920 (or 2160x3840 for 4K vertical)
- No letterboxing, no pillarboxing, no black bars
- **FAIL** if aspect ratio is wrong

## Output format

```json
{
  "clip": "clip.mp4",
  "verdict": "PASS",
  "resolution": "2160x3840",
  "fps": 23.94,
  "duration_s": 53.2,
  "total_frames": 1272,
  "checks": {
    "aspect_ratio": {"pass": true, "ratio": "9:16"},
    "crop_stability": {"pass": true, "seams_checked": 6, "max_seam_dy_pct": 0.01,
                       "zoom_seams": 0, "zoom_moves_within_shots": 0,
                       "max_within_shot_dy_pct": 0.4, "baseline_dy_pct": 0.009},
    "face_tracking": {"pass": true, "faces_detected_pct": 100.0, "avg_center_x": 0.5},
    "framing": {"pass": true, "avg_face_size_pct": 7.4, "max_sustained_deviation_pct": 13.6},
    "frozen_frames": {"pass": true, "detected": 0},
    "black_frames": {"pass": true, "detected": 0},
    "first_last_frame": {"pass": true},
    "jump_cuts": {"pass": true, "detected": 6, "note": "6 cut seams (render metadata)"}
  },
  "metadata": {"segments": 7, "seam_source": "render metadata", "resolved_from": "contract/manifest"},
  "summary": "All visual checks passed"
}
```

Calibration (2026-06-12): thresholds set against a 22-clip human-reviewed known-good
batch (all PASS, including punch-in-zoom listicles) and proven against a constructed
defect — a 2.5% mid-segment vertical crop jump FAILs as "crop shifted 2.4% vertically
WITHIN a shot (sustained step)".

## Fix instructions on failure

- Seam dY bump (Y-lock broken) → re-run `qa_reframe_v2.py --global-y` (auto for
  single/listicle via reframe stage ≥v2.2.0), re-render from reframe
- Within-shot crop step → inspect reframe keyframes around the flagged time; re-run
  reframe with smoothing
- Subject off-center sustained → tracker lost the subject; re-run reframe (check preset)
- Frozen frames at cut → re-run reframe with `--scene-split` per-segment
- Black frames → investigate the cut stage; likely a gap in `cuts.json` segments
- Wrong aspect ratio → check reframe preset (should be 9:16)
