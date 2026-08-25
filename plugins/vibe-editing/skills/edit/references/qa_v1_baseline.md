# Q&A V1 BASELINE — LOCKED 2026-06-04 (build on this)

**This is the known-good V1.** It produced `%USERPROFILE%/Videos/vibe-editing/ExampleQA_QA_v6_1080.mp4` (the Ricky
"never stop a flow" clip) — found, cut, synced, diarized, reframed, switched, captioned, graded,
clean-audio, end-to-end from raw 3-cam + iso-mic footage. User signed off: "much better, make this our new v1."
Reproduce/extend from here. Do NOT regress these settings.

## Pipeline (one workflow; Q&A is an input mode — see shortform/CLIP_DELIVERY_CHECKLIST.md)
`ingest 3 iso cams + iso mics → FIND moment (transcribe full session, mine vs SOP) → CUT (hook→payoff)
 → SYNC cams + recorder (envelope xcorr) → DIARIZE (by content + iso-mic energy) → REFRAME (speaker-locked
 → canonical reframe_h2v) → SWITCH (beat-aligned, payoff held) → CAPTIONS (spice) → GRADE → DYNAMICS
 → AUDIO (iso-mic gated mix + loudnorm) → GATE (checklist + vision-MCP) → deliver`

## Scripts (qa-clipper/scripts/)
- `qa_detect_speaker.py` — YuNet + ROI + nearest-previous → speaker-locked `face.json` (NOT largest-face)
- `reframe_h2v.py` (horizontal-to-vertical skill) — the CANONICAL reframer (X-smooth 51, **Y-LOCKED**). Use this; only the detection is custom.
- `qa_switch_plan.py` — beat-aligned (`--words`), payoff-protected (`--protect`) shot plan + reaction cutaways
- `qa_captions.py` — thin adapter → `generate_spice.py` (the ONE caption style; voice-colored)
- `qa_colorgrade.py` — per-speaker grade + `--inversion-guard`
- `qa_assemble.py` — reframe-passthrough + grade + push-in on holds + concat + caption burn
- audio: `qa_audio_sync.py` (identify mics + offset), `qa_audio_v2.py` (gated mix + loudnorm + remux)

## 🔒 LOCKED PARAMS (this is what "framed right" means)
**Speaker STAGE cam** (largest-face grabs audience → must speaker-lock; render from 4K for sharpness):
```
qa_detect_speaker.py speaker.mp4 speaker_faces.json --roi 0.05 0.08 0.50 0.45
reframe_h2v.py --video speaker_4K.mp4 --face-json speaker_faces_4K.json --out-w 1080 --out-h 1920 \
               --zoom 1.9 --smooth 51 --nose-y-1080 430   # head-to-mid-thigh medium, head HIGH (SOP "Speaker Main Angle")
```
**Guest cam** (mic area; exclude foreground audience):
```
qa_detect_speaker.py guest.mp4 guest_faces.json --roi 0.30 0.10 0.62 0.45
reframe_h2v.py ... --zoom 1.25 --smooth 51                 # chest-up medium, centered
```
**Switcher:** `--words words.json --protect "<payoff a-b>"` → cuts on pauses, speaker HELD on the payoff.
**Grade:** `--inversion-guard` when Speaker is on a cool stage + guest in a warm room.
**Audio:** Speaker = LAV1, audience = MIC4 (MIC3/LAV2 unused); recorder offset +833.86s; gated crossfade mix + loudnorm.
**Assemble:** `--simple-reframe` (pass pre-reframed verticals) `--inversion-guard`; push-in (zoompan) on `_main` holds >6s.

## Hard-won lessons (the QC loop that was missing)
1. **Detection, not the reframer, was the glitch.** Canonical detector grabs the LARGEST face = nearby audience → jumps + centers the wrong person. Fix = ROI + nearest-previous lock. Keep the canonical Y-locked smoother.
2. **Calibrate framing against the SOP reference image + the reference editor's finished clips — THEN watch with the vision MCP — BEFORE delivering.** "Speaker Main" = head-to-mid-thigh medium (head high, body to thighs, table visible), NOT chest-up.
3. The gate (`QA_V1_DELIVERY_CHECKLIST.md` / `shortform/CLIP_DELIVERY_CHECKLIST.md`) runs on EVERY clip, EVERY format.

## Open (build-on-this list)
- [ ] Caption-director emphasis (last checklist box, vs the manual word list)
- [ ] 4K master render (this baseline is a 1080 proxy)
- [ ] Profile look-room (bias crop toward facing direction)
- [ ] Consolidate Q&A + podcast + hotline under the ONE clip workflow (front-ends differ, back-half shared)
- [ ] Self-audit built INTO the assembler (auto frame-checks + vision-MCP before staging)
