# THE PERFECT Q&A PLAYBOOK — one-shot, AI-executable (2026-06-14)

> **📖 READ FIRST: [`QA_MASTER_SOP.md`](QA_MASTER_SOP.md)** — the consolidated single-source-of-truth for
> the EDITORIAL + visual cut (The reference editor's master-editor framework + the 250-pair data + visual guide + every
> session lesson, in one human-readable file). It is the WHAT-makes-a-good-Q&A spine; this playbook is the
> HOW-to-execute procedure. Same file lives at `${CLAUDE_PLUGIN_ROOT}/vault/SOPs/QA_MASTER_SOP.md` for drag-drop.

> **What this is.** The complete, deterministic procedure for turning raw Tier1 Q&A footage (a
> business owner asks the creator about their business; he advises) into a finished, posted-quality
> Q&A short — with **no prior context**. If you are an AI (Claude Code, Codex, anything) handed raw
> Q&A footage, follow these steps in order and you will produce a correct Q&A. Every rule here is
> backed by data from **1,110 highlight→short pairs + 71 visually-classified Q&A shorts** (see the
> evidence + frequencies in [`qa_clip_patterns.md`](qa_clip_patterns.md)).
>
> **The bar (Turing test).** A fresh session runs `/edit` on Q&A footage → a perfect Q&A comes out.
> Each step below ends with a **DONE-WHEN** gate; do not advance until it passes.
>
> **Golden rule of Q&A:** one guest = one clip = ONE self-contained problem→fix arc that a cold
> viewer understands with zero context, opening on the guest's number and ending on Speaker's payoff.
>
> ## 🔒 SIX NON-NEGOTIABLES — read FIRST (each cost a re-render on a real build with Operator)
> `qa_assembly.py` AUTO-CHECKS #1, #2, #6 and prints `[audio][check]` / `[split][check]` lines; #3-#5 require the AUDITS listed below.
> 1. **AUDIO — every speaker on their OWN lav, ALWAYS BOTH MICS MIXED AT 1.0 the entire time.** `qa_sync.json` MUST include
>    `speaker_mics{"speaker":<host lav>,"guest":<guest lav>}`. Without it the mix uses ONE mic for everyone, so the other
>    speaker is faint room bleed amplified ~+18–30 dB into hiss ("terrible audio"). The log must read **"2-mic conv mix"**
>    with `[audio][check]` mapping each speaker to THEIR mic and NO `[audio][WARN]`; voice dynamic range ≳35 dB.
>    **2026-06-16 Frame review on Guest**: previous behavior ducked the OFF mic to 0.30 weight. When the active speaker was QUIET on their own mic (e.g. wireless held loosely), the ducked off-mic contributed too little to fill in — output sounded like a mic cut. **NEW behavior (qa_assembly committed)**: BOTH mics at weight 1.0 always, regardless of segment speaker. The `speaker` field is for caption COLOR routing only; audio is always both-mics-1.0. Don't revert.
> 2. **SPLIT — GUEST PANEL = DYNAMIC TARGET-FRAMING (locked 2026-06-17). NEVER a fixed zoom, NEVER a static crop.**
>    **THE METHOD:** `qa_sync.json` → `guest_split: {"mode":"target", "target_face_h":0.34, "target_face_y":0.34, "roi":"0.05 0.00 0.55 0.60"}`. `qa_assembly` (default `mode=target`) calls `horizontal-to-vertical/scripts/guest_panel_render.py`, which detects the guest's face PER-FRAME and SOLVES the crop so the face is always **34% of panel height, centered 34% from the panel top** — crops the raw CCAM at the PANEL aspect (2160:1920, wider than 9:16 → no letterbox), size constant per camera-segment (median face height → no breathing), position tracked per-frame (camera pan/tilt just moves the framed crop). **This auto-adapts to every guest — tall/short/near/far — with ZERO per-guest tuning.**
>    **WHY (the bug it kills):** the OLD fixed-`zoom`+`eye` approach landed differently on every guest (each stands at a different distance/height in the wide CCAM), and `cropH=min(H,H/zoom)` clamped at zoom≤1 so 0.70/0.95/1.0 all rendered identical (eye_y dead too). Result: ~10 Guest re-renders of "too big/too low/too high." There is NO universal zoom — STOP guessing zoom entirely; the target-framer solves it.
>    **VALIDATED:** all 9 Tier1 guests through the target-framer with one spec → face_y locked 31–33%, uniformly chest-up (contact sheet confirmed). The target (34%/34%) was MEASURED from Operator's reference IG reel, not eyeballed.
>    **VERIFY each build:** `measure_guest_panel_face.py <clip>` reports face_h%/face_y%. To pick/adjust the target visually, `10_WORK/_orchestrate/panel_preview.py` makes a 9-cell zoom×position grid from ONE still (then `open` it for the user — Read only shows it to the AI). The legacy fixed-zoom path is still reachable via `guest_split.mode="zoom"` but should not be used.
> 3. **Q&A INTRO = BUSINESS + PROBLEM, not just business.** Drop the name. Open ON the business + revenue/number, BUT also state the actual constraint/problem CONCRETELY before Speaker's diagnosis. "I sell golf carts to families" alone = NOT an intro; "I sell golf carts… everything's been organic but now we have inventory" = correct intro. **A cold viewer must know WHAT THE GUEST'S PROBLEM IS before Speaker starts solving it.** If the source has the guest stuttering through the problem mid-exchange (e.g. Q&A back-and-forth), EXTRACT the concrete problem statement and place it in the intro phase. Optionally include Speaker's diagnostic callback ("you're sitting on product") as a clarifying beat. **AUDIT:** read your designed intro segments aloud as a cold viewer — does it answer "what does this guest do AND what's wrong"?
> 4. **CAPTIONS — money renders `$100K`, never "100 grand" or "a hundred thousand".** The qa path normalizes with **`spice_normalize.py`** (NOT `spice_format.py` — two normalizers exist by design). `caption_lint` must show **0 spelled-number errors**. If Whisper transcribes a number as words and spice_normalize doesn't catch it, ADD a `corrections.json` entry mapping the spoken form → the compact form (e.g. `{"a hundred thousand": "$100K"}`). Pass via `--corrections <path.json>`.
> 5. **CUT WORD-PERFECT, NO CLIPPED TAILS, LET THE GUEST FINISH.** Whisper's `word.end` labels are 0.10–0.25s EARLY — soft consonants (-s, -t, -th, -m, -ng, -ful, -al, -tion) and even hard stops (-d, -t after a vowel) extend PAST the label. **EVERY segment boundary must be checked**, not just the closing payoff. AND: when a cam-switch (split→speaker or split→guest) happens mid-conversation, EXTEND the previous segment past the speaker's natural completion point before cutting. If the guest is mid-sentence when cam cuts to Speaker, the source-time skip reads as "guest mic got cut." **AUDIT:** run the boundary-tail scan (see Step 8) — flags any seg-end within +0.10s of the labeled word-end with a soft-tail consonant. Fix by either extending end +0.15–0.25s OR including the next word.
> 6. **CLOSE ON THE REAL PAYOFF — extend 1–3s past the designed end to find the natural button.** TAM picks the conceptual payoff (e.g. "Give the sickest one away") but the source often has the actual punchy line 0.5–2s LATER than the EDL's designed end. **AUDIT:** after designing the closing seg, transcribe the next 3s of source — if the next 1–2 words are the real button line (a one-liner / number-reframe / story-button), EXTEND the seg to include them. Never end on a mid-thought beat where Speaker is still building toward a point.
>
> **NEW AUDITS that run BEFORE rebuild** (see Step 4-AUDIT below): boundary-tail scan, intro-business-plus-problem cold-viewer check, music-intro buildup profile (`--music-ss <N>` when track has a slow buildup), closing-payoff-extension scan.
>
> Full failure stories + fixes: the **FIELD-TESTED FIXES** section at the bottom.

---

## INPUTS & GLOBAL TARGETS

- **Input:** raw multicam Tier1 Q&A session (Speaker on stage + an audience questioner at a mic; cameras A/B/C + lav/mic audio), OR a single Highlights-style highlight (one guest's full Q&A). Either works.
- **Output per clip:** a 9:16 vertical short. **Sweet spot 17–60s (median 35s); hard cap ~90s.** ⚠️ Do NOT target a compression ratio — winners are LIGHTLY trimmed (top10 median **1.17x**, band ~1.2–1.5x); heavy compression (>5x) is a bottom-25 signal. **Cut for ONE CLEAN ARC + PORTABILITY, let length fall where it lands** (see Step 4 + qa_clip_patterns "TRANSCRIPT EDITORIAL TRANSFORM"). The old "~9:1" rule is retired for Q&A.
- **One session → ~8–10 candidate clips** (one per guest). Default to the Speaker brand (switch to another Brand brand — creator / creator / creator — only when the footage is clearly that brand). Honor any "DO NOT USE <guest>" notes.

---

## STEP 1 — INGEST

**Do:** scaffold the project, transcribe word-level, detect speakers + cameras.
```
python ${CLAUDE_PLUGIN_ROOT}/vault/scripts/new_project.py speaker <ShortName>      # → speaker/<date>_<ShortName>/{00_SOURCE,10_WORK,20_DELIVER}
# copy raw into 00_SOURCE (never edit originals)
python ${CLAUDE_PLUGIN_ROOT}/skills/edit/scripts/transcribe_groq.py <src> <boundaries.json> --out 10_WORK/transcripts   # word-level
# 2-mic stereo (host/guest split) → transcribe_isolated.py for clean per-speaker attribution
```
**Why:** word-level timestamps are required for frame-precise cutting; speaker/camera detection drives reframe + caption color.
**DONE-WHEN:** you have a word-timestamped transcript and know which mic/camera is Speaker vs guest.

---

## STEP 2 — SEGMENT INTO Q&A UNITS

**Do:** split the session into one unit per guest. A unit = the guest's intro → Speaker's full answer. Use the editor marker sheet if present (timecodes + "DO NOT USE" notes).
**DONE-WHEN:** a list of guest units, each with rough in/out and a one-line business descriptor.

---

## STEP 3 — SELECT (per unit) — does this become a clip?

Keep a unit only if it has **ONE self-contained cause→effect arc** that survives the **cold-viewer test** (a stranger with zero context gets it). Score each unit; cut the rest.
- ✅ keep: a clear business + number + constraint, then a clean diagnosis → **portable PRINCIPLE** payoff.
- ❌ drop: multi-thread sprawls with no single arc; units that need prior context; pure logistics; **units whose only payoff is a caller-specific tactic with no portable principle behind it** (these land bottom-25 — see below).
- **🎯 PREFER THE PORTABLE-PRINCIPLE MOMENT.** Data (250 perf-tiered pairs, 2026-06-17): motivation/mindset/wealth/relationship answers WIN; niche tactical-business diagnostics (pricing/scaling/how-to) skew bottom-25. When choosing which exchange to clip, favor the one that resolves to a universal takeaway, not just a niche fix.
**WHY:** the near-universal editorial move is "isolate the one arc, drop everything situational" (see qa_clip_patterns).
**DONE-WHEN:** a shortlist of clip-worthy units, each with a one-sentence arc that ENDS ON A PORTABLE PRINCIPLE.

---

## STEP 4 — DEFINE THE CUT (build `10_WORK/cuts.json` keep-spans)

This is the editorial heart. For each clip, choose keep-spans (by word index) per these rules.

> **🎯 THE MASTER GATE — PORTABILITY (the #1 predictor, 2.89x lift; 250 perf-tiered pairs 2026-06-17).** Read ONLY your chosen first line + last line, as a cold viewer with zero context. The hook must intrigue AND the payoff must resolve it, standalone. 94% of winners pass this vs 33% of bottom-25. **If it fails, the clip fails — fix the boundaries before anything else.** Full ruleset: `qa_clip_patterns.md` → "TRANSCRIPT EDITORIAL TRANSFORM".

- **OPENER — open on a WINNING hook class, NEVER a plain statement.** Highest lift: **confession (∞)** · **vivid_image (4.76x)** · **contrarian_claim (3.52x)**. A flat **plain_statement is the DEATH hook (0.23x, 49% of all bottom-25)** — if your candidate opener is flat, SCAN THE WHOLE ANSWER for a contrarian/confession/image line and lift it to the front. ⚠️ A bare number/stat hook is only neutral (0.68x) and wins ONLY when shocking AND it's Speaker's — for the **Tier1 diagnostic format** still open on the guest's business+problem (non-negotiable #3) so the cold viewer knows whose problem it is, but make the FIRST line the most gripping available, not a flat "I sell X."
- **BODY = the single arc.** Keep Speaker's first real move (diagnostic **question** or **reframe**) → the one principle. **Kill competing threads** (cut in 57% of clips). Cut host interjections (75%), tangents/celebrity digressions (59%), redundant examples (54% — keep the most visceral ONE), hedges (20%). Keep Speaker's crisp one-word beats for pace. **Preserve numbers exactly.** Speaker's confessions + tough-love stay verbatim.
- **EXTRACT-AND-WELD** is normal and tier-neutral (~30% reach-back in every tier). Lift the best hook to the front, weld to a clean principle button. Constraint = grammatical continuity at the weld (sentence boundaries, no orphaned pronouns), NOT adjacency. Welding a cleaner span from elsewhere BEATS faithfully cutting a rambly supplied span.
- **EXIT = a portable PRINCIPLE. End HARD on it.** 74% of winners end on a principle. **NEVER end on:** a **wind_down (0.06x — THE deadliest ending, 22% of bottom-25)**, a **bare TACTIC (0.11x)**, a CTA (0.0x), or a guest reaction. If the natural end is a tactic/wind-down, **EXTEND one more sentence to the principle behind it.** ⚠️ Tier1 LESSON 2026-06-17: my Surgeon clip ended on "$25K + $5K/yr" and golf-cart on "give the sickest one away" — both bare tactics = the bottom-25 signature. Extend to the principle.
- **⚠️ LENGTH — there is a SUBSTANCE FLOOR. The finished Q&A is ~130–160 words ≈ 50–65s (winner median 148 words / 57s; p25≈100 words / 38s).** Do NOT ship a hook→verdict→principle SKELETON. **KEEP SPEAKER'S FULL REASONING CHAIN** — the diagnosis AND the *why* behind the prescription (the in-person reframe, the recurring-model logic, the proof, the texture). The bookends alone (hook + one-line principle) = a hollow ~30s clip that has NEVER shipped. ⚠️ Tier1 LESSON 2026-06-17: my "ideal" Surgeon recut was 79 words / 30s — I stripped the meat and kept only the hook + "charge more." That's the OPPOSITE error from ending-on-tactic; both are wrong. The winning cut was ~150 words: it keeps the whole "fly them out → in-person is worth more → 25K + 5K/yr recurring + the meetup → people want to be in the room" REASONING, then buttons on the principle.
- **⚠️ COMPRESSION — RETIRE "9:1", but DON'T over-trim either.** The Highlights pairs compress only ~1.2–1.5x because the raw is ALREADY a curated ~60–90s highlight. A raw Tier1 BACK-AND-FORTH exchange (~150–250s) compresses to the ~50–65s final at ~3–4x. **>5x is the bottom-25 over-compression signal — it severs the substance.** Cut for ONE CLEAN ARC + the FULL reasoning, not for a ratio and not for minimum length. If your cut is under ~100 words / ~38s, you almost certainly gutted Speaker's reasoning — add it back.

> **🔒 EDITORIAL GATE (run BEFORE render — `qa_editorial_score.py`):** After designing each clip's keep-spans, score the resulting spoken transcript:
> ```
> python ${CLAUDE_PLUGIN_ROOT}/skills/edit/scripts/qa_editorial_score.py --text "<the clip's spoken words>"
> # or batch: --transcript-json {name:{title,transcript}}
> ```
> It scores hook class / payoff class / portability / one-arc / opener cleanliness against the 250-pair winner-vs-loser data and **exits 1 (BLOCK) on the bottom-25 patterns**: plain_statement opener, wind_down/tactic/cta ending, failed cold portability, or a mid-fragment open. Fix the EDL until it PASSES. (Validated 2026-06-17: it correctly FAILED all 9 Tier1 Q&A clips — flat business-description openers + bare-tactic endings — the exact editorial weakness this batch shipped.)
- **CUT the CTA outro** ("company.com/roadmap", "free gift", "link in bio") — 96%. Discard the back ~22% of the source.
- Cut word-precise; remove dead air + filler.
```
python ${CLAUDE_PLUGIN_ROOT}/lib/_shared/precision_cut.py --src 00_SOURCE/<raw> --transcript 10_WORK/transcripts/<t>.json \
        --keep '[[a,b],[c,d],...]' --out 10_WORK/cuts/<clip>.mp4     # spans END on the true acoustic word-end
```
Validate boundaries: `python ${CLAUDE_PLUGIN_ROOT}/lib/_shared/window_validator.py` (9-rule gate).
**DONE-WHEN:** the clip reads as ONE arc, opens on the number, ends on the payoff, no CTA, no fragment/clipped word.

---

## STEP 5 — REFRAME (camera grammar → vertical 9:16)

Measured grammar (71 Q&A shorts): **open on split-screen, then cut to the speaker.**
- **OPEN on the SPLIT-SCREEN over the question/hook — Speaker (host) TOP / guest (questioner) BOTTOM**, stacked, gaussian seam (82% of Q&A shorts open this way; it often bookends the clip).
- **Then cut to the SINGLE angle of whoever is speaking** — guest-single for their question, Speaker-single for his answer. **Switch on the SPEAKER, not a scene detector.** Re-trigger the split at exchange beats.

**SWITCH LOGIC (measured, 39 two-person Q&A clips) — build the angle sequence like this:**
1. **OPEN on the split** (Speaker top / guest bottom) over the question/hook — 60–67% do; or open on the guest-single asking. (Some cold-open the split ~0.5s just to establish both faces, then collapse to a single.)
2. **Primary hard cut = the question→answer handoff** (33/39): the instant the speaker role flips, hard-cut to that speaker's single. **Cut ON a clause/breath boundary, never mid-word.**
3. **Hold the speaker's single through their whole turn** — do NOT cut every sentence. The answerer owns the frame until the payoff.
4. **Reopen the split** at exchange beats / when Speaker asks a follow-up (34/39); **reaction cut** to the listener on a reaction beat (35/39).
5. **Punch-in / punch-out reframes on the held single for variety** during a long answer (87% — 2–3 gentle beats, tighter on key nouns, looser before a list). These are reframes, NOT angle switches.
6. **Hard-cut the ending on the payoff word, on a live frame** — no fade, no freeze, no cut back to the guest.
(The simplest valid grammar is the floor: guest-single question → ONE cut at the handoff → Speaker-single answer held to the payoff, no split at all. Use it when only two clean angles exist.)
```
# single angles (Y-LOCK + face-box center):
python ${CLAUDE_PLUGIN_ROOT}/skills/horizontal-to-vertical/scripts/qa_reframe_v2.py IN OUT --preset stage   # Speaker on stage
python ${CLAUDE_PLUGIN_ROOT}/skills/horizontal-to-vertical/scripts/qa_reframe_v2.py IN OUT --preset guest        # questioner
# split-screen: reframe each angle (split-top + guest) then stack:
python ${CLAUDE_PLUGIN_ROOT}/skills/horizontal-to-vertical/scripts/make_splitscreen.py TOP BOTTOM OUT   # gaussian seam
# OR the whole multicam Q&A in one pass from an EDL:
python ${CLAUDE_PLUGIN_ROOT}/skills/edit/scripts/qa_assembly.py --edl 10_WORK/edl.json --sync 10_WORK/sync.json --out 10_WORK/<clip>_reframed.mp4
```
**🔒 `qa_sync.json` REQUIRED KEYS (NON-NEGOTIABLE #1 + #2):**
```json
{ "cam_dir": "...", "roles": {"BCAM/<stem>":"speaker","CCAM/<stem>":"guest"},
  "offsets": {"BCAM/<stem>": <s>, "CCAM/<stem>": <s>},
  "mics": ["<host lav>","<guest lav>"],
  "speaker_mics": {"speaker":"<host lav>","guest":"<guest lav>"},   // ← each speaker on THEIR OWN lav (or audio = bleed/hiss)
  "guest_split": {"zoom": 1.1, "eye": 0.22} }                    // ← tune zoom so guest face ≈ host (~20-35% of panel)
```
- **Both split panels are face-tracked reframe masters** (zoom + Y-lock), never a static crop. Guest zoom default 1.1;
  the `roi` in `guest_split` GUARDS against locking onto a seated AUDIENCE face (pre-scan with `detect_face_dense.py`).
- After the render, the build prints `[audio][check]` (mic per speaker), `[split][check]` (host vs guest panel face%),
  and a voice dynamic-range line. **Any `[WARN]` = fix before delivery** (set/repair speaker_mics; lower guest zoom).
- **4K = `VIBE_QA_RES=2160`** (default is a 1080p proxy; reqc blocks on resolution).
**WHY:** opening on the split shows BOTH people so a cold viewer instantly reads "someone is asking Speaker"; cutting to the speaker keeps energy. Per-speaker mics + matched panel scale are what make it read PRO not amateur.
**DONE-WHEN:** opens on the Speaker-top/guest-bottom split over the question; single angles track the active speaker; face Y-locked (no per-seam bob); `[audio][check]` shows each speaker on their own mic (no WARN); `[split][check]` host & guest face% comparable (~20-35%, no WARN).

---

## STEP 6 — CAPTIONS

```
python ${CLAUDE_PLUGIN_ROOT}/skills/caption-clips/scripts/spice_caption.py 10_WORK/<clip>_reframed.mp4 10_WORK/<clip>_capped.mp4 --context "<hook hint>"
```
- **Color = speaker: white = host (Speaker), yellow = guest — 99%. EYEBALL it; diarization mis-tags.**
- **Position rides the SEAM / center** (NOT lower-third). On a split, captions sit on the seam between panels.
- The reference editor style: bold, word-by-word, size emphasis on the key word/number.
- Consider a **caption = generalized principle** treatment if a hook card is used (the takeaway abstracted above the specific case).

**Measured the reference editor caption rules (40 Q&A clips, 2026-06-14) — the spice engine should apply these:**
- **Active-word (karaoke) emphasis (40/40):** the word being spoken pops/brightens/enlarges; word-by-word reveal, pop/snap-on.
- **Italics are COMMON (72%)** — quoted/role-played/reflective/guest-emphasis words (not the old ~10%).
- **Per-word size tiers** emph 1.25 / strong 1.5 / peak 1.85 (~27% of words bumped); numbers/money get a bump + the speaker's color.
- **Spoken "and" → "&"** (75%); **profanity self-censored with `*`** (`B*TCH`) for brand safety (33%).
- **Yellow highlight BOX behind the single peak hook word** (~18%) — a peak device beyond size/weight.
- **Parentheses ~20%** for asides; **never brackets**; no emoji/stickers.
- **Word-synced timing — NEVER show a word before it's spoken** (the align-to-silence + pause-split fix; verify no pre-reveal).
- **🔒 MONEY/NUMBERS render compact (NON-NEGOTIABLE #3):** `$100K` / `$3.5M` / `85%` / `10X`, never "100 grand", "three
  and a half mil", "85 percent". ⚠️ The qa-assembly caption path normalizes with **`spice_normalize.py`** (lowercase SOP),
  NOT `spice_format.py` — they're two separate normalizers (keep money rules in sync). After the render `caption_lint`
  runs; it MUST report **0 spelled-number errors**. If you fix a money rule, fix it in `spice_normalize.py` for this path.
→ Full measured detail: `references/qa_clip_patterns.md` (CAPTIONS section) + `caption-clips` spec.

**DONE-WHEN:** every line is the right speaker color, sits on the seam/center, matches the spoken words exactly, money/numbers are compact (**caption_lint = 0 spelled-number errors**), and **no word appears before it's spoken**.

**`--corrections` for Whisper mishearings (2026-06-15):** when Whisper consistently mishears a word/phrase on the rendered audio that isn't fixable by adjusting the cut (e.g. burns "founder's problem" instead of "the founder. I fulfill,", or hallucinates "when like" instead of "when"), pass a per-clip JSON of `{heard: burned}` substitutions to `qa_assembly.py --corrections <path>`. Multi-token phrase pass runs first, then single-token (case-insensitive on bare word, punctuation preserved). Verify via: `[captions] corrections applied: N word/phrase fix(es)` in the build log + visually extracting a frame from the rendered file. If N=0 your `heard` text doesn't match what `transcribe_lv3.py` (qa_assembly's internal transcriber) actually output — verify against the burned pixels, NOT a Groq re-transcribe (Groq variance differs).

---

## STEP 7 — MUSIC

```
python ${CLAUDE_PLUGIN_ROOT}/lib/_shared/pick_music.py --folder "<vibe>" --used "<batch picks>"   # distinct track per clip
```
Loudnorm the bed ~10–13 dB under the −16 LUFS voice; gentle fades. Never reuse a track within a batch.

**🔒 PROFILE EVERY TRACK FOR SLOW INTRO (2026-06-16, Operator review on Guest).** Many TikTok/atmosphere tracks have 5–30s of build-up before the beat actually drops. Shipping the build-up under a hook is a defect. **REQUIRED:** for every picked track, run an RMS curve on the first 30s. If the track's RMS doesn't cross −25dB until t=N seconds, pass `--music-ss N` to skip to the beat-drop. Examples from Tier1: `øfdream - thelema` drops at 27s, `Gods creation` at 25s, `øneheart - this feeling` at 17s. Quick profile:
```
ffmpeg -hide_banner -i "<track>" -t 30 -af "astats=metadata=1:reset=1:length=1,ametadata=print:key=lavfi.astats.Overall.RMS_level" -f null - 2>&1 | grep RMS_level | awk -F= 'NR>=1{printf "  t=%2ds  %s\n", NR-1, $NF}'
```
Find the first second where RMS > −25dB → that's your `--music-ss`. **NEVER skip this profile step** — Operator calls it out the moment he hears a build-up.

**Two music knobs** (don't confuse them):
- `--music-ss <N>` — **SEEK INTO THE TRACK** (skip the boring intro, start at the cool part). Music still begins at clip-time 0. THIS is what you want for slow-intro tracks.
- `--music-delay <N>` — **DELAY in the OUTPUT timeline** (silence at the clip start, music kicks in later). Only use when you genuinely want no music over the split-screen Q opener, not as a workaround for #1.

**DONE-WHEN:** a distinct, vibe-matched bed sits under the voice without masking it AND the track's beat-drop is within ~1s of clip-time 0 (no slow build-up bleeding under the hook).

---

## STEP 8 — QC + AUDIT (the gate)

### 8a — PRE-BUILD AUDITS (run on the EDL + source transcript, BEFORE any 4K encode)
These catch the defect classes Operator reviewed Guest for. Failures here = re-design EDL, not re-render.

1. **BOUNDARY-TAIL SCAN.** For every segment's `mic_end`, check: does it fall within +0.10s of a soft-tail consonant word (-s, -t, -th, -m, -ng, -tion, -al, -ful, -d, -ce, -ze, -x, -f, -sh, -ch)? If yes AND the next word starts within 0.15s, **the soft consonant gets clipped**. Fix: extend `mic_end` past `word.end + 0.20` (cap at next_word.start − 0.01), OR include the next word in the segment.
   ```python
   for seg in edl: check end against words.json — flag if word.end is within +0.10s of seg.mic_end
   ```
2. **GUEST-COMPLETION SCAN.** For every cam-transition (`split` → `speaker` or `speaker` → `split`), check the source-time gap between prev seg's end and next seg's start. If the prev seg ends WITH GUEST TALKING and the next seg starts with SPEAKER (or vice versa) AND the source between them still has the prev speaker talking → **EXTEND the prev seg through the speaker's natural completion point.** Operator's literal note on Guest v2: *"when it cuts to Speaker while the guest is still talking, you can't hear the guest, so you cut the guest's mic. Which you shouldn't have done."* The source-time jump reads as a muted mic.
3. **PAYOFF-EXTENSION SCAN.** Read the source transcript for 3s past the LAST segment's `mic_end`. If the next 1–2 words form a punchier closing button (a one-liner, a number-reframe, a story-button, a callback), **EXTEND the closing seg to include them.** TAM names the conceptual payoff but often the actual quotable button is 0.5–2s later. Operator on Guest: *"You ended it on Speaker still talking. Find a better natural payoff."* — the real payoff `"So give the sickest one away"` was 1.5s past my designed end.
4. **INTRO BUSINESS + PROBLEM SCAN.** Read the first 3 segments of the EDL aloud as a cold viewer. Can you answer BOTH: (a) what does the guest do, and (b) what's their specific problem? If only (a), the intro fails non-negotiable #3. Solution: either extract the concrete problem statement from later in the source and include it in the intro phase, OR weld in Speaker's diagnostic callback as a clarifying beat.
5. **MUSIC INTRO PROFILE.** Per Step 7, profile the picked track's first 30s. If beat-drop > 1s in, MUST pass `--music-ss <beat-drop>`.
6. **GUEST-EYE POSITION.** `qa_sync.guest_split.eye` — render a single test frame, measure where the standing guest's face center lands in the panel. If face_y > 0.35 of panel_height (below the upper third) → lower `eye` value (the Tier1 session needed 0.15, not the default 0.22).

### 8b — BUILD via qa_assembly OR the manifest engine
```
python ${CLAUDE_PLUGIN_ROOT}/skills/render/scripts/init_manifest.py <project> --pipeline qa
python ${CLAUDE_PLUGIN_ROOT}/skills/render/engine.py <project>
# OR direct: qa_assembly.py --edl ... --sync ... --music ... --music-ss <N> --corrections <path> --out ...
```

### 8c — POST-BUILD audit fan-out (edit step 9)
**sf-audit** (mechanics) + **scorecard-audit** (narrative; N4 "payoff is the final line") + audit-visual/audio/captions/script.

**Acceptance checklist (all must pass):**
1. Opens on the guest's number; name dropped.
2. ONE arc; cold-viewer-safe. 
3. **Intro = business + problem** (per non-negotiable #3). 
4. Ends ON the REAL payoff (not mid-thought); no CTA outro; no trailing question. 
5. Opens on the Speaker-top/guest-bottom split; cuts to the speaker. 
6. Guest doesn't get audio-cut mid-completion at cam-transitions. 
7. Captions: white=Speaker / yellow=guest, on the seam, accurate, no clipped soft-tail consonants. 
8. video==audio length; opens clean (<0.10s lead silence); ends on a LIVE frame (no freeze/fade). 
9. 17–60s (≤90 cap).

**🔒 THE SIX NON-NEGOTIABLES (hard gates — verify by MEASUREMENT on the delivered file, not by eye):**
10. **AUDIO:** each speaker mixed on THEIR OWN lav — build log says "2-mic conv mix", `[audio][check]` mapping correct, NO `[audio][WARN]`, voice dynamic range ≳35 dB.
11. **SPLIT BALANCE + EYE:** guest panel face% ~20–35%, NO `[split][WARN]`, face center in upper third (not lower-middle); confirm with `detect_face_dense.py` on the delivered guest panel.
12. **INTRO:** business + problem both established before Speaker's diagnosis (cold-viewer test on transcript).
13. **CAPTION MONEY:** `caption_lint` = **0 spelled-number errors**.
14. **BOUNDARY TAILS:** the pre-build boundary-tail scan returned 0 flagged seg-ends.
15. **PAYOFF:** the pre-build payoff-extension scan confirmed the closing seg includes the natural button line.

**DONE-WHEN:** every checklist item (1–15) passes and both audit gates are green.

---

## STEP 9 — DELIVER

- Output to the project's **`20_DELIVER/`**, Brand-named (`SPEAKER_<TYPE>_<SOURCE>_<Title>_Operator_<YYYYMMDD>_V#`).
- **your review tool = SPEAKER clips only, and only after an explicit per-file "push" in this conversation.** Default: deliver locally, show Operator, WAIT. Never auto-push.

---

## POINTERS (this playbook orchestrates; it does not duplicate)
- Editorial rules + frequencies + anti-patterns + non-obvious findings → [`qa_clip_patterns.md`](qa_clip_patterns.md)
- Reframe → `horizontal-to-vertical` · Captions → `caption-clips` · Cut → `_shared/precision_cut.py` · Build → `render` · Audits → `sf-audit` + `scorecard-audit`
- SOP context → `references/editorial_sop.md`, `references/assembly_cut_standard.md`, `QA_HOTLINE_SOP.md`
- Provenance: `the source-map` (a local database) — 1,110 short↔Highlights-highlight pairs.

---

## FIELD-TESTED FIXES — first real-footage one-shot (2026-06-14, Tier1 0507 / Rebecca)

Three failures caught on the first real two-cam build. All are fixed in code; these are the RULES so they
don't recur. Verify each on the DELIVERED file (measure, don't eyeball — Three Laws).

1. **AUDIO — `qa_sync.json` MUST set `speaker_mics`.** `{"speaker_mics":{"speaker":"<host lav>","guest":"<guest lav>"}}`.
   Without it the conv-mix silently uses `mics[0]` for EVERY speaker, so the guest's question plays off the
   HOST's lav as faint room bleed, then loudnorm amplifies it ~+18–30 dB into hiss ("terrible audio"). qa_assembly
   now infers per-speaker lavs from filenames (SPEAKER/HOST, GUEST/CALLER/ATTENDEE) and WARNS if a multi-speaker EDL
   lacks them — but set it explicitly. VERIFY: per-speaker noise floor in a quiet gap (astats RMS trough) should be
   ≤ ~−55 dB; the wrong-mic bug reads ~−32 dB. Log must say "**2-mic** conv mix/run", not 1-mic.
2. **SPLIT panels are FACE-TRACKED reframe masters — never static crops.** Both halves are reframed (Y-locked,
   box-centered) and cropped to the panel identically. **MEASURE the zoom, don't guess:** a guest who looks "small"
   in a WIDE room cam is still LARGE once the ROI punches in — zoom 2.0 made the guest's face **57%** of the panel (a
   giant close-up) vs the host's ~21%. Default `guest_split` zoom is now **1.1** (≈32% face = head-and-shoulders
   comparable to the host). Pick zoom per camera (`sync["guest_split"]={"zoom","eye","roi"}`) so the guest's face%
   ≈ the host's (~20-35%) — VERIFY with `detect_face_dense.py` on BOTH delivered panels (face_h / panel_h). The `roi`
   GUARDS against locking onto a seated AUDIENCE face — pre-scan and EYEBALL the panel to confirm it locked on the GUEST.
3. **CAPTION money lives in `spice_normalize.py` for the qa path (NOT `spice_format.py`).** Two normalizers exist;
   the qa assembly uses `spice_normalize` (lowercase-first SOP), the standalone caption-clips path uses `spice_format`.
   Money rules (`$`, `K/M/B`, `grand`, slang `k/mil/m`, word-fractions "three and a half mil"→`$3.5M`) are now in
   BOTH — keep them in sync (⚠️ tech-debt: unify). VERIFY: `caption_lint` must show **0 spelled-number errors**.
4. **4K is `VIBE_QA_RES=2160`.** The assembler defaults to a 1080p proxy; reqc BLOCKS on resolution. Set the env var
   for any delivery render (masters are reframed at 4K either way; the cache key includes the output size).
