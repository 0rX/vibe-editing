# The reference editor caption deep-dive — measured refresh (40 Q&A clips, 2026-06-14)

> Builds on the 2026-06-03 19-clip study (`spice_caption_spec.md`). Source: 40 finished Q&A shorts,
> high-res frames + word-accurate transcripts. Raw: `%USERPROFILE%/Videos/vibe-editing/speaker/2026-06-14_QAPatternAnalysis/10_WORK/caption_deepdive.json`.

## Confirmed / refined — ALREADY in the engine
- **Color = voice:** white = Speaker, yellow = guest/quoted — **40/40 use yellow** (~10% run all-white = simpler/older edits; DEFAULT to the white/yellow split).
- **Per-word SIZE emphasis 39/40** — tiers emph 1.25 / strong 1.5 / peak 1.85, ~27% of words bumped.
- **ITALICS are COMMON — 72%** (was treated as ~10%). `caption_director.py` prompt updated 2026-06-14 to italicize quoted/reflective/guest-emphasis words liberally.
- **Active-word (karaoke) emphasis 40/40** — the spoken word pops/enlarges; word-by-word pop/snap reveal (fade on ~⅔). Keep the size bump on the load-bearing word as it lands.
- **2–4 words per cue**, centered / on the seam, ALL-CAPS common (mixed with title-case).
- **TIMING word-synced — NO pre-reveal.** FIXED 2026-06-14: `align_to_silence` wired into the spice GEN chain + a PAUSE_SPLIT (0.35s) cue-break + merge-guard in `generate_spice.py`, so a word can never display before it's spoken.

## NEW rules (measured here; the first three are concrete TO-WIRE code adds)
1. **Spoken "and" → "&"** — 75% (30/40). Stylize a standalone "and" as "&".
   *TO WIRE in `spice_format.py`:* it's ~75% (not 100%), so scope it (e.g. sentence/cue-initial or standalone "and") and re-run `test_spice_format.py` to confirm no regressions before locking.
2. **Profanity self-censored with `*`** — 33% (`b*tch`, `sh*t`, `f*ck`) — CAPTION ONLY, audio untouched, brand-safe.
   *TO WIRE in `spice_format.py`:* deterministic profanity→asterisk map; safe to default-on (over-censoring a caption is harmless for the brand).
3. **Yellow highlight BOX behind the single PEAK word** (~18%; e.g. `CONTROVERSIAL?` on solid yellow) — a peak-emphasis device beyond size/weight.
   *TO WIRE:* a new style key in the `generate_spice` renderer + the director emitting it on the one peak word (cap one per clip).
4. **Parentheses ~20%** for short asides/clarifiers; **brackets essentially never (1/40) — do NOT use brackets**; no emoji/stickers as a rule.

## Status
- Wired now: white/yellow, size tiers, **italics-liberal + active-word + peak (director prompt)**, word-synced timing fix.
- Queued (small, testable; wire as caption feedback lands): the "&" rule, profanity-censor, the peak highlight-box.
