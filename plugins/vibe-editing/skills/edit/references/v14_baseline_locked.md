# Q&A V1 BASELINE — v14 LOCKED 2026-06-04 (user: "lock this in as the v1 baseline")

Master = `%USERPROFILE%/Videos/vibe-editing/ExampleQA_QA_v14_4K.mp4`. Reproduce via `/tmp/render_v14.sh`.

## LOCKED PARAMS (new defaults)
- **Captions:** caption-DIRECTOR authored (`qa_captions.py --style <director.json>`; run `caption_director.py` first) — yellow-italic guest voice, weight emphasis, single-word size payoffs. **VIBRANT shadow** (spice.json: alpha 0 / offset_y 16 / blur 18 / **stroke_px 14** / both 000000). Two heights by CAMERA via `qa_caption_layout.py`: speaker 0.47, guest 0.674; cues clipped at switches.
- **Reframe:** speaker-locked detect (`qa_detect_speaker.py` ROI, NOT largest-face) → canonical `reframe_h2v.py`. Speaker zoom **1.9** nose-y **430** (head-to-thigh per SOP, from 4K); guest zoom 1.25.
- **Grade:** richer speaker (`eq sat 1.20 contrast 1.10 gamma 0.98`) + `--inversion-guard`. **Push-in 0.09** over `_main` holds.
- **Finish (MASTER only):** vignette+gblur (`apply_vignette.py`) → 4K caption burn (crf 12).
- **Audio:** ElevenLabs `isolate_audio` on the active-speaker mic mix (LAV1 Speaker / MIC4 guest, sidechain bleed-duck base).

## FAST ITERATION MODE (for cut/split experiments)
Skip vignette + 4K (use the 1080 reframes `editorial_sop4k.mp4`/`guest_canon.mp4`, `--res 1080`, no `apply_vignette`). Add the full finish ONLY on the final master.

## KNOWN ISSUE — Speaker blur
Speaker stage cam is a WIDE shot → tight crop (zoom 1.9) → big upscale → SOFT. Guest is sharp (wider crop). FIX on the master: run an **AI upscaler (Real-ESRGAN)** on the Speaker crop before the final scale.

## SPLIT-SCREEN (LOCKED rules — Q&As need these regularly)
- **Layout:** Speaker TOP / guest BOTTOM, 50/50 (Visual Guide p2).
- **Seam — GROUNDED in the reference editor's actual clips (2026-06-04).** Downloaded his finished Q&A clips
  from your review tool (2026 TEAM SPEAKER › 02_Social/01_Short Form/<month>/03_EXPORTS, `Speaker_Q&A_*_Spice_V1.mp4`)
  and zoomed the seam. His treatment = a ONE-SIDED DROP shadow: Speaker's panel has a CRISP top edge
  ("the hard line"), and a defined shadow falls DOWNWARD onto the GUEST only, darkest right at the
  edge (~0.6 alpha), fading ~50px down. NOT symmetric, NOT drawbox bars.
  Implementation: `assets/seam_shadow.png` = half-gaussian (hard top / soft bottom), **peak alpha 0.60,
  sigma 34**, overlaid with its top ON the 50% seam (`overlay y=main_h/2`). The crisp "hard line"
  reads strongest where Speaker's bg is bright (The reference editor's blue stage); on dark content it's naturally subtler.
- **Caption position RULE (user 2026-06-04):** during a split, captions go DEAD-CENTER on the seam —
  `qa_caption_layout.py --split-y 0.50`. Color still follows voice (white Speaker / yellow guest).
- **Tiles = dedicated 1080x960 reframes straight from the 4K cams** (NOT a crop of the pre-zoomed
  verticals — that grabbed torsos / face-filled the guest). `reframe_h2v --out-w 1080 --out-h 960`:
  - Speaker tile: zoom ~2.3, nose-x 540 (centered), **smooth 21** (heavy smooth lags his stage pacing →
    right-shift), nose-y-1080 ~580. Fills the tile (head+chest+arms).
  - Guest tile: zoom ~1.35 (head+shoulders; tighter reads "too zoomed", looser shows seated audience),
    nose-x 540, nose-y-1080 ~600.
  - Wired: `qa_assemble.py --split-tile --guest-split-tile` (seg_split uses them at crop-y 0).
- **Uses so far:** establishing split on the opening question (0-4s); split HELD across a payoff line
  through its last word ("...a flow", to 24.6s), then hard cut back to full-screen.

## DONE (v15/v16)
- "new[s]" caption (~33s) renders with brackets intact. Tail trimmed to 54.60 (cut the guest "uh-huh").
- Fast iteration mode: `qa_assemble --no-grade --res 1080` + no vignette (skip the slow 4K finish).

## STILL TODO (master pass, once cuts locked)
- Speaker AI-upscale (Real-ESRGAN) for his soft stage-cam crop; full 4K + grade + vignette finish.
