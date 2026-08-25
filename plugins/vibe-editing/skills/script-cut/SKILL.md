---
name: script-cut
description: >
  Text-based / script-driven precision cutter for talking-head clips. Use this whenever you need to
  cut a clip from a transcript and the recurring problems are clipped words, leftover "uh"/"um", false
  starts or restarts, dead air, scrambled word order, or a payoff that gets chopped. Instead of trusting
  the editor's rough in/out times or the ASR timestamps, it takes the exact words you want the clip to
  SAY, forced-aligns them to the audio, keeps those word-spans, and cuts everything in between (silence
  AND stumbles). Pairs with a renderer (e.g. listicle-short/build_short.py) that consumes the cut spec.
  Trigger phrases: "script cut", "text-based cut", "align the words and cut between them", "Descript-style cut".
---

# script-cut — text-based editing with forced alignment

## The idea (say it back to yourself before using it)
You edit in Premiere by looking at the **audio track** and the **words**. This automates exactly that:

1. **Script** — the exact clean words you want the clip to say.
2. **Find** — forced-align that script to the audio so you know where every word physically is.
3. **Cut** — keep the word-spans, cut *everything in between*.

"Everything in between" is **silence AND junk** (fillers, false starts, restarts). Junk is never in
the script, so it lives in the gaps between kept words and gets cut automatically. You never surgically
remove errors after the fact — you only keep the words you chose, so errors can't leak through.

This is text-based editing (how Descript works), done with a real forced aligner so it's frame-honest.

## Why align the FULL transcript, not just the clean script
A forced aligner **cannot skip** unscripted audio — it absorbs a stumble into a neighbouring word's
boundary, inflating that word's span so the stumble rides along in the cut. So: align the *faithful*
transcript (every word, incl. fillers/restarts), then KEEP only the curated subset and cut the rest.
The kept words land on their true positions; the junk stays in the cut gaps.

## Run it
```bash
# 1) one-time: install the toolchain (MFA + a python venv with numpy + num2words)
bash ${CLAUDE_PLUGIN_ROOT}/skills/script-cut/scripts/setup_toolchain.ps1

# 2) cut: produces <out>/cut_spec.json  (precise, in SOURCE seconds)
"$VENV/bin/python" ${CLAUDE_PLUGIN_ROOT}/skills/script-cut/scripts/script_cut.py \
    --source  SOURCE.mp4 \
    --transcript words.json \      # word-level transcript: {"segments":[{"words":[{word,start,end}]}]} etc
    --spec    structure.json \     # {"segments":[{"in":sec,"out":sec, "n":1?, "cat":"LABEL"?}]} = rough marks
    --out     OUTDIR \
    --gap     0.20                 # cut any inter-kept-word gap >= this; bigger = keep longer pauses

# 3) render cut_spec.json with whatever renderer you use, e.g. for a numbered listicle short:
python ${CLAUDE_PLUGIN_ROOT}/skills/listicle-short/scripts/build_short.py \
    --source SOURCE.mp4 --spec OUTDIR/cut_spec.json --music TRACK.mp3 \
    --res 1080 --grade --per-seg --eye-lock --out RENDERDIR/

# 4) EAR-TEST IT YOURSELF (never hand QC to the user):
"$VENV/bin/python" ${CLAUDE_PLUGIN_ROOT}/skills/script-cut/scripts/qc_ears.py  --clip RENDER.mp4 --spec OUTDIR/cut_spec.json
"$VENV/bin/python" ${CLAUDE_PLUGIN_ROOT}/skills/script-cut/scripts/qc_clips.py --clip RENDER.mp4 --spec OUTDIR/cut_spec.json \
    --transcript RENDER_words.json    # the render's OWN transcript = ground truth of what it actually says
```

`--spec` `in/out` are only the editor's **rough** marks that choose which words belong to each chunk;
the actual cut is defined by the script. `n`/`cat` pass through (e.g. listicle numbered category tabs).

## Verify by EAR, with ground truth — not by guessing
- **Ground truth** of what the render says = the render's OWN word transcript (the captions transcript).
  Read it and compare to intent. An external ASR (e.g. a quick vision-model pass) **hallucinates** fillers
  across tight jumpcuts — don't trust it over the render's own transcript.
- **Clipping** can't be heard in a transcript (ASR re-reads a clipped word as whole). Detect it by ENERGY:
  a clean cut tapers into silence; a clipped cut ends while the word is still loud (`qc_clips.py`).
- `qc_ears.py` scans residual dead air and draws a spectrogram of every seam.

## The lessons baked in (each was a real bug — keep them)
- **Never sort the transcript by timestamp.** Glitchy ASR timestamps reorder words ("just learned" →
  "learned just"). Transcript **file order is the spoken order**.
- **Numbers are real words.** A digit-cleaner that treats "250"/"2024" as empty will drop them. Keep them;
  spell them for the aligner's dictionary (num2words, year-aware: 2024 → "twenty twenty-four").
- **MFA edge-pull.** If the wav has unscripted lead audio, MFA glues the first word to t=0 and drifts the
  whole chunk ~0.3s early, dragging in pre-roll ("Because the thing is, is that…"). Fix: start the wav
  right at the first context word (minimal pre-roll) and select from the editor mark *forward*.
- **A stretched function word hides a stumble.** A 1.18s "it" in the transcript is the ASR smearing a
  restart ("it is the hardest **thing**— … the hardest **part**…") into one token; the aligner then locks
  onto the false start. Tell a **stumble from a pause by LISTENING**: if the long word's interior stays as
  loud as its onset it's a stumble (drop it); if it goes quiet it's just a breath (keep the word). =`hides_speech()`.
- **true_end / no clipped tails.** Aligners label soft endings (-ing / -s / -ve) early. End every cut at the
  word's RELEASE-INTO-SILENCE (energy drops and stays down), not at the label + a fixed pad — otherwise tails
  get shaved and the final payoff word clips. =`true_end()`.
- **true_start / no ghost alignments in silence.** Symmetric problem at the *front*: when Whisper smears
  a false-start + restart into one stretched function word (e.g. a 2.18s "you" that's actually `[false-start]
  [silence] [restart]`), MFA can place a script word **inside** the silent gap. Caught one in the
  EndurePainLonger clip: MFA put "can" at 2121.046–2121.256 in a **−60 dB** dead zone (waveform was
  unambiguous — see [Lesson: silence-validate kept word onsets]). The aligner has no acoustic-gate on the
  label, so the cut spec includes 210ms of silence. **Fix:** validate every kept word's first ~50ms — if
  its mean dB is below `word_body_dB − 16`, treat it as a ghost and drop that span. Until that lands in
  code, manually scan the cut_spec for any sub-300ms segment whose `_frames_db()` mean is < −45.
- **Trim editorial slop** at chunk edges: leading connectors / "because" / "is is" stutters; trailing
  orphan fragments after the last complete sentence (use the transcript's own sentence punctuation).
- **Leading-orphan = early sentence boundary.** If your rough window pulls in the *tail* of the previous
  sentence ("…you might be dead. **And so if you're like, the fact that you are alive…**"), the cleanup
  loop won't catch it — "not", "dead" aren't in LEAD_DROP / CONN / STRETCH_FN, so they survive and the
  clip opens with "**not dead. And so…**". Heuristic: if the **first** sentence-ending word lands within
  the first ≤3 real words of the chunk, those words are an orphan tail — trim through that period.
- **Trailing-orphan = next-sentence leak.** Symmetric to leading-orphan but at the END: if your rough
  `out=` extends past the last complete sentence in the chunk, the opening words of the NEXT sentence leak
  in. The script then ends with "…this season. **And so it hasn't just been me**" instead of "…this season."
  The cleanup loop won't catch it — "And", "so", "it" are valid words from a valid sentence that just
  shouldn't be in this clip. Heuristic: if the LAST sentence-start in the chunk lands after the last
  period/question mark, those trailing words are an orphan head — tighten `out=` back to just after the
  period. (Caught on MoveTheMountain 2026-06-08.)
- **Mid-chunk tangents pass through.** Cleanup only fires at chunk *edges*. A tangent in the middle
  ("looking a lot more into Buddhism **lately weirdly enough**") survives because it's not at a boundary
  and not a single-word stutter. Fix at the *window* layer: split the rough chunk in two so the tangent
  falls in the cut gap, OR tighten the in/out to exclude it.
- **READ THE PRINTED CURATED SCRIPT BEFORE YOU RENDER.** script_cut.py prints every curated script line
  as `[CAT] says: …`. **Eyeball each one** — if the first words don't form a clean sentence opener, or if
  there's a tangent / orphan tail mid-line, **STOP, tighten the window, re-run.** Rendering a clip with a
  busted opening word is the most common avoidable failure of this pipeline (Operator caught "not dead",
  "weirdly enough", and "And so it hasn't just been me" leaking through on 2026-06-08 — none of which
  the cleanup catches automatically, all of which the printed script showed plainly).
- **Also read the END of every script.** Same scan in reverse — if the line ends on a connector / mid-clause
  ("…losing **when**", "…cash my chips in **somebody**", "…I'm like **is**"), the payoff is being chopped.
  Push the `out=` of that chunk further until the final word is a real terminal (period / question mark / a
  fully-resolved noun phrase). Verify the LAST word in `says: …` is the word you want the viewer to hear last.
- **Don't overlap chunk windows.** Two chunks with overlapping `in`/`out` (e.g. chunk_n out=1888.5, chunk_n+1
  in=1886.5) produce TWO span sets that include the same words — and the renderer plays both, so the audio
  repeats a phrase. ("…and to me that gives the hardship | and to me that gives the hardship memory dividends…")
  Always make chunk ranges disjoint, or merge them into one chunk if they belong together.
- **Validator: drop SILENT, never just TINY.** A post-cut "drop any seg <0.30s" rule looks defensive but
  it murders real short words like "is" (0.22s, −20dB). Drop a segment only when its mean dB is < −40
  (true silence/ghost) OR (sub-0.20s AND sub-−30dB). Tiny-but-loud spans are real syllables — keep them.
- **Final-word clipped tail = `out` set too low.** If qc-tail scan shows the last seg's edge dB > −30
  (still loud) AND the dB post-cut > edge − 6 (jumps into next-segment audio rather than tapering), the
  chunk's `out=` cut the final word mid-syllable. Bump `out=` past the word's full release into silence —
  use the next sentence-end's start time as a safe upper bound.
- **Fallback, don't crash.** If a chunk's alignment fails (token-count mismatch / no TextGrid), fall back to
  the curated auto-timestamps for that chunk and keep going.

## Pre-cut validation gate (shared — run BEFORE cutting)
```bash
# Validate rough windows (pre-script-cut):
python ${CLAUDE_PLUGIN_ROOT}/lib/_shared/window_validator.py \
    --transcript words.json --spec structure.json --rough [--source VIDEO.mp4]

# Validate cut_spec (post-script-cut, before rendering):
python ${CLAUDE_PLUGIN_ROOT}/lib/_shared/window_validator.py \
    --transcript words.json --spec cut_spec.json --rough [--source VIDEO.mp4]
```
`--rough` = multi-segment-per-clip (rough windows OR cut_specs). Checks opener on first chunk,
payoff on last, downgrades overlap to WARN. Omit for a flat list of independent single-clip entries.
`--source` = enables energy-based rules (clipped-tail, ghost-silence). Slower but catches more.
All 9 lessons from this skill are coded into that validator as automated rules. Use it in ANY
pipeline (script-cut, clip-miner, precision_cut) — it's in `_shared/` so everyone can call it.

## Tuning knob
`--gap` (default 0.20s): the only dial. Smaller = tighter (cuts shorter pauses too, can feel rushed);
bigger = keeps Speaker's natural beats. Stumbles are removed regardless (they're not in the script).

## Toolchain (what setup installs)
- **Montreal Forced Aligner** (MFA, english_us_arpa acoustic + dictionary) via **micromamba**.
- A **python venv** with `numpy`, `num2words`, `soundfile`, `matplotlib` (for QC), run the scripts with it.
- `ffmpeg` on PATH.
Paths are overridable by env: `MFA_MAMBA`, `MFA_ENV`, `MFA_ACOUSTIC`, `MFA_DICT`.

> Generic skill — no brand baked in. "Speaker" is just the canonical example. Per-brand vocab / music /
> reframe presets live in that brand's own folder and are passed by path, never hardcoded here.
