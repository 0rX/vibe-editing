---
name: horizontal-to-vertical
description: THE single face-tracking + 16:9→9:16 reframe skill (locked house style, 2026-06-10). Two cases — that's it. (1) SINGLE FACE → `scripts/qa_reframe_v2.py --preset {talking-head | stage | split-top | guest | podcast}` — Y-LOCK (eyeline fixed at clip median, only X keyframes) + face-BOX center (steadier than nose tip). Named presets fire the locked template automatically. (2) SPLIT-SCREEN → reframe each angle with qa_reframe_v2 (use `split-top` + `guest` presets) then stack with `scripts/make_splitscreen.py` (gaussian seam shadow; `--width 2160` for a 4K-chain 2160x3840 output, default 1080); the full Q&A multicam pipeline is `edit/scripts/qa_assembly.py` which calls these tools. Supersedes vertical-reframer (archived), shortform/reframe.py (keyframe-linear, jerky), qa_reframe_stage.py (no Y-lock / nose-only — the failed canonical from earlier in 2026-06-08), and reframe_yunet.py (no Y-lock / no presets). Use whenever a horizontal clip needs to become a vertical 9:16 short — talking-head, stage Q&A, hotline, podcast single-cam, podcast multicam, listicle, any of it. Trigger keywords reframe, reframe to 9:16, vertical reframe, 16:9 to 9:16, format vertical, make this vertical, reformat to portrait, crop to vertical, face track, face tracking, follow the speaker, keep the face centered, speaker reframe, split screen, split-screen reframe, two-up vertical, stacked angles, listicle reframe.
---

# horizontal-to-vertical — THE face-tracking skill (2 cases, locked house style)

**Locked 2026-06-08, updated 2026-06-10.** One tool for face-tracking. One tool for split-screen stacking. Five locked presets. That's it.

The locked house style: **Y is FIXED at the clip's median eyeline (no Y bob), X tracks the face-BOX center (not the nose tip — steadier on a moving subject).** Per-frame X keyframes follow the subject so the face stays pinned at one output X coordinate while Y never moves. This is what makes the AC clips look the way they do, and what every prior attempt was missing.

## 🛑 SHAKY, MULTI-PERSON footage (testimonial ADS) → 2D FACE-PIN, NOT these presets (2026-06-16)
The locked presets above assume a STABLE camera (Y-LOCK to median can't cancel a shaking camera) and
a SINGLE clear face. For handheld testimonial-ad footage (camera shakes, background attendees in frame),
qa_reframe_v2 locks onto the wrong/background face and the Y-lock leaves the vertical shake in. **Use
`_shared/testimonial_reframe.py`** instead: per-frame LARGEST-face detection (= foreground guest), crop
follows the face on X AND Y every frame → guest pinned dead-centre, shake cancelled. 🛑 NEVER vidstab
these (it rubber-bands/"swims" the frame). Verify by extracting CONSECUTIVE frames — the face must hold
the same screen position. (NOTE: YuNet's detector threshold is `--score`, not `--face-conf`.) Full SOP:
`edit/references/testimonial_ads.md`.

## 🔒 HARD RULE — Reframe BEFORE merge, NEVER after (2026-06-11)

**For assembly cuts (multi-segment clips built from separate sources), ALWAYS reframe each
segment individually FIRST, then concatenate the reframed segments.** Never concatenate raw
segments into one file and then try to reframe the whole thing.

**Why:** Each segment may come from a different camera, a different angle, a different speaker.
The face tracker needs to lock onto the correct face in each segment independently — with its
own Y-LOCK median, its own X smoothing window, its own zoom. If you reframe after merging:
- The tracker sees a camera switch as the face jumping across the frame and tries to
  smoothly pan to the new position (visible slide instead of a clean cut)
- Y-LOCK uses a single median across all segments (wrong eyeline for at least one speaker)
- Smoothing bleeds across segment boundaries (first frames after a cut show the old
  speaker's position fading out)

**The correct order for assembly cuts:**
```
1. Extract each segment as its own horizontal clip (from 4K source)
2. Reframe EACH segment individually:
   qa_reframe_v2.py seg_00.mp4 seg_00_vert.mp4 --preset <per-camera> --no-scene-split --smooth 30
3. Concatenate the reframed vertical segments
4. Mux with audio
```

This is different from the scene-split mode below (which handles camera switches within ONE
source file in a single pass). Assembly cuts = separate source files = reframe each, then merge.

---

## 🏆 THE HIGHEST UNLOCK — Segment-aware single-pass architecture (2026-06-10)

**The single biggest improvement to the entire clip pipeline.** For ANY multi-angle footage
**within a single source file** (podcasts, interviews, Q&A with camera switches), the architecture is:

1. **DETECT boundaries first** — find every camera hard-cut as a frame number
2. **Track each segment independently** — reset the face detector at each boundary so it locks onto whoever is on screen in THAT segment, with its own Y-lock and its own X smoothing window
3. **Render in ONE pass** — no splitting into files, no re-encoding, no concat. One read of the source, one write of the output. The tracker just resets its state at boundary frames.

**Why this matters:** Without this, camera switches cause:
- The X tracker smoothly pans from speaker A to speaker B (a visible slide instead of a clean cut)
- Y-lock uses a single median across both speakers (wrong eyeline for at least one of them)
- Smoothing bleeds across the boundary (the first few frames after a cut show the old speaker's position)

**Why single-pass, not split-concat:** The v1 approach (detect → split into N files → reframe each → concat) had THREE encodes per clip (source → split segments → reframe each → concat final). This produced:
- Glitch frames at concat boundaries (encoder cold-start artifacts)
- 3× encode time
- Quality loss from triple generation loss

The v2 single-pass approach has ONE encode. The tracker state (last detected face position) resets to `None` at boundary frames — that's it. Everything else (per-segment Y-lock, per-segment X smoothing, per-segment interpolation) is just array math on the tracking data, partitioned by a segment-ID array.

> 🛑 **`--global-y` is REQUIRED for same-angle assembled cuts (2026-06-12).** Per-segment Y-lock is
> for TRUE multicam (each angle has its own eyeline). On a SINGLE locked camera with content seams
> (`--cut-frames` from an assembled cut), per-segment Y medians differ by a few px per segment, so
> EVERY cut visibly bumps the subject up/down — "the cuts are super jumpy... he moves up when he
> shouldn't" (caught by the user across a full 22-clip batch). `--global-y` keeps ONE clip-wide
> eyeline median (the original Y-LOCK doctrine) while X still resets per cut. The render stage
> (`render/stages/reframe.py` v2.2.0) passes it automatically for `single`/`listicle` pipelines;
> multicam (`qa`/`podcast`) keeps per-segment Y. Override per clip: manifest
> `stages.reframe.y_scope: "clip" | "segment"`.

**This same boundary-detection → per-segment-independent-processing → single-pass-render pattern applies to ANY per-segment operation:**
- **Caption color switching** — detect who's speaking in each segment, assign host=white / guest=yellow per segment
- **Audio mixing** — per-segment gain/EQ when mic sources differ per angle
- **Grade/LUT** — per-segment color if different cameras have different white balance

The pattern: `scene_boundaries[] → segment_ids[] → process each segment independently → render once`.

## Case 1 — SINGLE FACE

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/horizontal-to-vertical/scripts/qa_reframe_v2.py INPUT OUTPUT \
    --preset {talking-head | stage | split-top | guest | podcast} [--res 1080|4k]
```

| `--preset` | Use for | zoom | eye-y | ROI |
|---|---|---|---|---|
| **`talking-head`** | Speaker talking-head from a desk (4K master source). **PROVED 2026-06-08 on StayInAGreatMood batch.** | 1.6 | 0.25 | `0.20 0.05 0.80 0.70` |
| **`stage`** | Speaker on Q&A stage with audience in foreground. Tight upper-left ROI excludes audience. Used by `qa_assembly.py` for Speaker's cam (C2092). | 1.6 | 0.18 | `0.05 0.05 0.82 0.55` |
| **`split-top`** | Speaker in the TOP half of a split-screen stack. Slightly looser. | 1.4 | 0.22 | `0.05 0.05 0.82 0.55` |
| **`guest`** | Guest cam, single-face full-frame (NOT the static split-bottom crop). | 1.4 | 0.24 | `0.25 0.15 0.58 0.48` |
| **`podcast`** | YouTube/podcast source already tightly framed (chest-up). No zoom — subjects already fill the frame, any zoom crops too aggressively. **Auto-enables `--scene-split`.** **PROVED 2026-06-10 on George Guest x the creator (PeaceOrPower).** | 1.0 | 0.28 | `0.10 0.05 0.80 0.70` |

All presets bake `--lock-y --xcenter box`. Smoothing window 41. Explicit `--zoom / --eye-y / --roi / --lock-y / --xcenter` override individual preset values.

**`--lock-x` (added 2026-06-12, Speaker PeaceOrPower) — lock X per segment like Y.** By default X is the
SMOOTHED face-box center (follows the speaker). On a **seated talking-head who shifts/gestures**, that
following reads as an unwanted slow **horizontal pan** within a single shot. `--lock-x` pins X to the
per-segment MEDIAN (static frame per camera angle), mirroring the Y-lock — pair it with `--scene-split`
so each angle still gets its own locked X. Use it for podcast/talking-head clips where the frame should
hold still; leave it off when the subject genuinely moves and you want the camera to follow.

### Scene-split reframe (auto for podcast, opt-in for others)

Multi-angle source footage (podcasts, interviews, any video with camera switches between speakers) **must not** be reframed as one continuous piece. When the camera hard-cuts from speaker A to speaker B, the face tracker would smoothly keyframe the X position across — producing a sliding pan instead of a clean cut.

`--scene-split` (auto-enabled for `--preset podcast`) fixes this via **single-pass scene-aware tracking** (no splitting/concat):

1. **Detect** camera angle switches via ffmpeg scene scoring (threshold `--scene-threshold 0.20`) → frame numbers stored in `_scene_frames: set[int]`
2. **Track** in one pass — the tracking loop checks `if n in _scene_frames: last = None` to reset the face tracker state at each boundary. The detector picks up the new speaker fresh instead of following from the previous one.
3. **Segment ID array** — `seg_ids[frame]` maps every frame to its segment index (0, 1, 2...). This array drives ALL per-segment operations.
4. **Per-segment interpolation** — NaN frames (no detection) are interpolated WITHIN their segment only, never across a boundary. Without this, a missed detection near a cut would interpolate between two different speakers.
5. **Per-segment smoothing** — the X median pre-filter + box-car smoothing window operates on each segment's frames independently. This is what prevents the slide — smoothing can't pull X toward the previous segment's speaker.
6. **Per-segment Y-lock** — each segment gets `np.median(y_values_in_that_segment)` as its locked Y. Different speakers sit at different heights; a single global median would be wrong for at least one of them.
7. **Single encode** — the render loop reads `y_lock_per_seg[seg_ids[i]]` to get the correct Y for each frame. One ffmpeg pipe, one encode pass, zero quality loss.

If no scene changes are detected, falls through to the normal single-piece reframe (segment count = 1, all arrays are whole-clip).

```bash
# Auto for podcast preset:
python qa_reframe_v2.py input.mp4 output.mp4 --preset podcast --res 1080

# Explicit on any preset:
python qa_reframe_v2.py input.mp4 output.mp4 --preset guest --scene-split --res 1080

# Disable for podcast if source is genuinely single-angle:
python qa_reframe_v2.py input.mp4 output.mp4 --preset podcast --no-scene-split --res 1080
```

**PROVED 2026-06-10:** 6/15 clips from PeaceOrPower had camera switches (3–5 segments each). Without scene-split, the X tracker slid between speakers on every cut. With scene-split, each segment locks independently = clean hard cuts between angles. **Architecture note:** v1 split-then-concat (triple encode) produced glitch frames at boundaries; v2 single-pass (reset tracker at boundary frames) eliminated them.

### ⚠️ VERIFY scene-split caught EVERY cut — never ship a cross-angle pan (hard rule 2026-06-11)
A MISSED camera cut is the #1 reframe defect: two angles end up in ONE segment, so the X-track
**interpolates between the two speakers' face positions → a visible horizontal pan/slide across what
should be a hard cut.** Operator flagged exactly this ("it keyframes across horizontally instead of
individual camera angles"). The default `--scene-threshold` can be too high for a *subtle* angle change
(same set, similar framing, small head-position delta). So, every multi-angle reframe:
1. Read the printed `scene-split: N segments, cuts at frames [...]` and sanity-check N against the
   number of camera cuts you can see in the source (contact-sheet or eyeball).
2. If the output shows the face **panning/sliding across a hard cut**, a cut was MISSED — **lower
   `--scene-threshold`** (try 12 → 8) and/or `--min-seg`, and re-run. Never ship X interpolating between
   two camera angles.
3. **Last-frame check:** the FINAL frame must be the correct speaker (the brand person), not a hanging
   interviewer/guest frame or a reaction cutaway. If the clip ends on the wrong face, trim the last
   1–2 frames (the cut belongs to the editor, not the source's camera timing). Operator: "on the very last
   frame it shows the interviewer — that can't happen."

### How the tracking works (locked, do not change)

YuNet DNN face detect → ROI gate (rejects audience / off-camera people) → NEAREST-to-previous selection (locks onto the speaker across frames) → track the face BOX center for X, median Y across the whole clip → median pre-filter + box-car smoothing window 41 → 9:16 crop where X follows the smoothed nose-x and Y is FIXED at clip median. Velocity-continuous, no Y bob, no keyframe jerk.

Graceful fallback: if no face found in ROI for the whole clip, holds a static crop centered on the ROI midpoint. Keeps the build robust across guests/source quality.

## Case 2 — SPLIT-SCREEN (two speakers stacked) — ONE SHOT

For ANY 2-person split-screen (podcast, interview, debate, reaction — anything that isn't a Q&A workshop stage):

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/horizontal-to-vertical/scripts/split_facetracked.py \
    --top host.mp4 --bottom guest.mp4 --out split.mp4
```

That's it. The wrapper reframes each angle with the locked `talking-head` template, bakes asymmetric eye-y values (top=0.15 face-high, bottom=0.65 face-low) so the face lands at the upper-third of EACH 960-tall tile, then stacks via `make_splitscreen.py` with the gaussian seam shadow. Symmetric, clean.

Override knobs (when defaults don't match the footage):
- `--top-preset` / `--bottom-preset` — swap presets per side (e.g. `stage` for a wide stage cam)
- `--top-eye-y` / `--bottom-eye-y` — re-tune the face position in each tile
- `--start` / `--end` — clip the stack to a sub-range

### Q&A workshop multicam — use `qa_assembly.py` instead

For the full Q&A pipeline (per-segment fast-seek cuts, per-cam reframe with asymmetric ROIs for stage-with-audience geometry, 4-mic audio mix, transcribe, SPICE captions, house grade, HW H.264), use `edit/scripts/qa_assembly.py` directly — it calls into THIS skill's tools and adds the workflow chrome. `split_facetracked.py` is for SIMPLE two-cam stacks where each cam has a centered subject; `qa_assembly.py` is for the full Q&A multicam build.

### Podcast multicam — use `edit --type podcast`

For lav-mic podcasts with sync, diarization, jumpcut, and dual-color captions, the `edit` skill's podcast path (`edit/scripts/multicut.py`) runs the full build — by default it uses STATIC crop per speaker (because podcast subjects don't usually move enough to need tracking, and static is jitter-free). If you want face-tracking instead of static crop on a podcast, the per-side step inside `multicut.py` would be the swap target — small change, do it when you have podcast footage to verify against.

## Where things live

All in **THIS folder** (`${CLAUDE_PLUGIN_ROOT}/skills/horizontal-to-vertical/`) as of 2026-06-08:

- **Face-tracking engine:** `scripts/qa_reframe_v2.py` (the only single-face tool you should call)
- **Split-screen stacker:** `scripts/make_splitscreen.py`
- **YuNet model:** `scripts/yunet.onnx`
- **Seam shadow:** `assets/seam_shadow.png`
- **Hardware encode:** auto via `_shared/fast_encode.py` (VideoToolbox, ~4× libx264)

All callers (`edit/scripts/qa_assembly.py`, `edit/scripts/qa_build.py`, per-guest wrappers in brand job folders) point directly to THIS folder — no symlinks needed.

## Source-resolution discipline (learned the hard way 2026-06-08)

A 720p source CANNOT produce a sharp 1080p vertical no matter what tool/zoom you use — the crop region is too few pixels, upscale is too aggressive. Always reframe from the **highest-resolution master available** (4K HEVC if recorded that way). If the input is a downscaled "horizontal" deliverable from a prior listicle/short pipeline, find the 4K original in `<project>/00_SOURCE/` and reframe from THAT using the same `cut_spec.json` timestamps. The proxy and master share a timeline.

## Archived 2026-06-08

| What | Where | Why |
|---|---|---|
| `vertical-reframer` | `_archive/2026-06-08_facetracking_consolidation/` | Step-function crop, snaps every 1–4s. Deprecated 2026-06-04. |
| `qa_reframe_stage.py` | (in scripts/, deprecation note added — its callers still work via the symlink) | Earlier "canonical" mistake. No Y-lock, nose-only tracking. Produces visible micro-jitter on stationary subjects. `qa_reframe_v2.py` supersedes it. |
| Old Haar `reframe.py` + `detect_face_dense.py` + `reframe_h2v.py` + `reframe_yunet.py` | (in scripts/, legacy fallback) | All predate the Y-lock + xcenter-box discovery. qa_reframe_v2 is strictly better. |

## Verification rule

Always pull a contact sheet on a render before declaring it good. The sf-audit centering check has weak detection and false-negatives on hats/beards/mics. EYEBALL it. Stat output from qa_reframe_v2 (`hits 100% | x 0.50-0.52 | y LOCKED@0.33`) confirms the tracker found the face every frame and Y is genuinely locked — but you still need to watch the playback.
