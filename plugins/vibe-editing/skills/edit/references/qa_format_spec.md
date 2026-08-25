# Speaker Q&A SF — Format Spec (LOCKED 2026-06-04)
**Source of truth** for the Q&A short-form pipeline. From the two official docs:
`ExampleQA_SF_Editing_Structure.pdf` (SOP) + `ExampleQA_SF_Visual_Guide.pdf` (visual guide + presets).
Items marked **⬚** are gaps the docs leave open → filled by reverse-engineering the reference editor's 24 finished Q&A clips.

---

## 1. Picking the moment
Great Q&A moment = **clear introduction · clear problem · tension · widely applicable · clear payoff.**
Filters: *Is this too niche? Is the problem clear? Is there clear tension?* **One issue only.**

## 2. Structure — Hook → Problem/Tension → Solution/Payoff
**HOOK**
- *Visual:* text hook **title card** → **splitscreen (Speaker on top)** → switch to Speaker / guest full-screen. (Or full-screen → full-screen.)
- *Audible:* "we make Y, our business is X" **or** straight into the problem ("I sell X, can't figure out Y even after 3 yrs…"). **Don't** include "hi, my name is…" or Speaker's "hey, what can I help with?" unless truly necessary.
- *Good-hook filter (≥1 of 2):* a short **preface ≤15s** (dentist 12s / time-study 13s / no-sales 11s) **or** an **attention-grabber** ($10M).

**PROBLEM / TENSION** — establish context, lead to the solution, Speaker confronts the tension.
- Speaker prompts a question → guest says something that prompts Speaker's reaction → Speaker digs for **only the necessary** context. Not solving multiple issues — **solving 1.**

**SOLUTION / PAYOFF** — **ONE** solution (actionable advice · belief-breaker · Speaker's professional opinion). Widely applicable, easy to understand, clearly related. *Did we solve the issue? Does this give the audience value?*

**BRAND ALIGNMENT** — protect authenticity; any restructuring stays **PARALLEL** to Speaker's actual point, never perpendicular. Make Speaker look good; represent both Speaker and the guest accurately.

**CUT WORKFLOW (pro tips)** — color-code cuts: **Stage 1 = segment** (hook / profit / AI / growth / money / tension), **Stage 2 = camera angle** (Speaker / guest / wide). Write out segments + potential structures. Experiment with multiple structures. Kill darlings (1 issue; cut off-structure moments).

## 3. Camera angles (5)
- **Split-screen (50/50):** Speaker **top**, guest **bottom**, same proportions, **drop shadow on Speaker's angle.**
- **Speaker Main**, **Guest Main** (medium shots)
- **Speaker Wide**, **Guest Wide**
- Switch angle by who's speaking + emphasis. ⬚ *exact cut rhythm / avg shot length / when to use split vs full vs wide — from clip analysis.*

## 4. Colorgrade
- **Speaker:** bright, saturated.  ⬚ *preset missing in doc → derive ffmpeg curve/LUT from clips.*
- **Guest:** cool, blue tones.  ⬚ *preset missing → derive.*

## 5. Captions / subtitles
Both speakers: **Montserrat, size 80**, text box **150** (avoid UI cutoff), **centered**, **single line** default, **lowercase** (except proper nouns + I/I'm/I'll/I'd/I've), `$`/`%` **symbols** (never "dollars"/"percent"), money **abbreviated** ($600K, $1.2M, $3B; under $100K can be $10K/$75K/$1,600), **no dead gaps**, spelling double-checked. Animation preset = Premiere "Text Down" style.
- **GUEST → yellow `#FED90F` (or `#FECB00`), *ITALIC*** — default Medium Italic, highlights **Black Italic**.
- **SPEAKER → white `#FFFFFF`, non-italic** — default Medium, highlights **Black**.
- **Highlights** (Black weight) land on the key/number/payoff words.
- ⬚ *validate these colors hold across all 24 clips; note any per-angle exceptions.*

## 6. Title card
**SF Pro, weight Black, ALL CAPS, ~160px**, leading **-40**, tracking **-30**. Colors: white `#FFFFFF` + black `#000000` + yellow `#FECB00` highlights (subtle black stroke on white bg). Background: **dark-grey `#1A1A1A` box, opacity 100%, size 60, corner radius 50.** Animated (preset). Example: **"YOU HAVEN'T NAILED THE MODEL"** (MODEL in yellow).

## 7. Premiere presets (human editors / reference; our pipeline replicates these in libass/ffmpeg)
- Q&A subtitle font: `<source-footage-link>`
- Q&A subtitle animation: `<source-footage-link>`
- Title-card font: `<source-footage-link>`
- Title-card animation: `<source-footage-link>`

## Gaps being filled from the 24 the reference editor Q&A clips (the analysis pass)
1. **Cut rhythm** — avg shot length, angle-switch cadence, split-screen vs full-screen frequency.
2. **Colorgrade** — concrete Speaker (bright/saturated) + Guest (cool/blue) values → ffmpeg.
3. **Caption validation** — confirm guest-yellow-italic / Speaker-white across clips; note exceptions.
4. **Per-angle examples** + title-card frequency/placement.

Source PDFs: `%USERPROFILE%/Videos/vibe-editing/...ExampleQA_SF_Editing_Structure.pdf`, `%USERPROFILE%/Videos/vibe-editing/...ExampleQA_SF_Visual_Guide.pdf`.
Existing engine: `scripts/make_qa_captions.py` (dual guest/Speaker styles — align to §5).

---

## ✅ VALIDATED FROM 24 SHIPPED SPICE CLIPS (2026-06-04) — these override the docs above

**Source:** frame analysis of all 24 Team Speaker Q&A shorts (The reference editor, 2024-11→2026-04), ~9 frames each → `QA_ANALYSIS_SYNTHESIS.md`. Where these contradict §1–7 (doc-derived), **these win** — they're what actually ships.

### TITLE CARD — ❌ OFF BY DEFAULT (overrides §6)
**0/24** shipped clips have an opening title card. The SF Pro / #1A1A1A box / yellow-keyword card is in the Visual Guide but **another team owns that step** (matches the locked "no title-card hooks for Speaker/SF" rule). **Do not generate one by default.** The hook is the audible question + captions. `qa_title_card.py` exists but stays OFF unless explicitly requested.

### SPLIT-SCREEN — MID-CLIP, not the hook (corrects §2/§3)
Used in **19/24 (79%)**, but it's a **reaction/exchange device in the tension/back-half** — 18/19 place it AFTER the hook, only 1 in the hook. Layout: Speaker-TOP / guest-BOTTOM, hard center seam, triggered when the audience member is active/reacting. **Drop shadow optional** (only ~3/19) — not required. 5 clips use no split at all.

### CUT RHYTHM (fills §3 ⬚)
**Avg shot ~14.3s** (median ~13s, range 8.6–27.7s). **~7 shot states/clip** regardless of length (longer clips hold angles longer, don't add cuts). **Speaker-driven:** ~1 angle change every 10–15s, holding the active speaker's MAIN angle for their beat. No montage; locked-off cameras; energy from angle switches + word captions.

### ANGLE USAGE (fills §3 ⬚)
Default = each speaker's **MAIN** (medium) while they talk (Speaker→speaker_main, guest→guest_main). Split-screen overlays exchanges. **Wides are rare punctuation** (guest_wide rarest). Most clips use only **3–4 of 5** angles. **⚠ Caption color follows the VOICE, not the on-screen face** (Speaker VO over a guest cutaway is still white).

### COLORGRADE (fills §4 ⬚) — gentle nudge + inversion guard
Holds in 12/24, **INVERTS in 4/24** (Speaker on a cool blue stage + guest in a warm room). Apply per-speaker as a **gentle nudge respecting native lighting, never a hard teal/orange LUT.**
- **Speaker:** `eq=brightness=0.03:saturation=1.12:contrast=1.05` (+ optional warm `colortemperature=6300`)
- **Guest:** `eq=brightness=-0.02:saturation=0.93:contrast=0.98` + `colortemperature=7200` (~700–900K cooler)
- **Inversion guard:** sample shot luminance/WB; if Speaker's source is already cooler/darker than the guest's, skip/soften the push.

### CAPTIONS (confirms §5) — yellow has TWO jobs
- **SPEAKER = white #FFFFFF — 24/24 (universal, the most reliable rule in the set).**
- **GUEST = yellow #FED90F — 19/24; italic — 20/24.** 5 edge cases (number-yellow vs speaker-yellow, solo monologue, silent guest) — not contradictions.
- **Yellow dual-role:** (1) guest-speaker color; (2) number/money highlight on Speaker's WHITE lines (#FECB00 digits — matches speaker-canon). Emphasis = **Black weight** on key+number+payoff words.
- ~4 clips show a slight italic slant on Speaker lines — tolerated minor; weight + color are load-bearing.

### Build outputs — FULL PIPELINE (2026-06-04)
- `scripts/qa_captions.py` — **thin adapter to the unified `generate_spice.py` engine** — the SAME caption style as podcast + hotline (user directive 2026-06-04: "it's all the same style"). Feeds the diarization timeline in as spice `voice_spans` → **guest = a different VOICE rendered yellow #FECB00, Speaker = white**; full Montserrat weight palette + Text-Down animation + size axis. Reconciled to canon: **numbers = white + weight/size emphasis (voice-colored, NOT forced yellow)**; **italic = quotes/reflection only (NOT per-speaker)** — the guest is distinguished by COLOR, not italics. ✅ visually validated. *(Flip numbers to always-yellow with `--number-color FECB00` if ever wanted — but it would apply to every format.)*
- `scripts/qa_colorgrade.py` — per-speaker grade nudge + inversion guard. ✅ A/B validated.
- `scripts/qa_switch_plan.py` — **switcher decision engine** (speaker timeline → shot plan: cold-open hook, ~14s shots, split-screen for mid-clip exchanges, wide relief). ✅ self-test.
- `scripts/qa_assemble.py` — **assembler** (shot plan + 3 iso cams → reframe/grade/composite/concat/audio/captions → final 9:16). ✅ proven end-to-end on synthetic 3-cam.
- `scripts/qa_title_card.py` — OFF by default (0/24).
- `scripts/make_splitscreen.py` — Speaker-top/guest-bottom compositor (expects 9:16 inputs).

**Input contract (your footage):** 3 synced iso cams — `--speaker` (speaker_main + split top), `--guest1` (guest_main + split bottom), `--guest2` (guest_wide).

**Remaining to run for real:** `qa_diarize.py` — speaker timeline from the iso-cam audio (energy-based across mics if iso, else whisperx/pyannote) + a `faster_whisper` transcript. Then the one-shot flow: **transcribe → diarize → qa_switch_plan → qa_captions → qa_assemble → QC → deliver.**
