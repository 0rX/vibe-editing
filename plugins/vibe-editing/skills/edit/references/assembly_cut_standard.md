# Speaker Q&A — ASSEMBLY-CUT standard (locked 2026-06-06)

THE visual setup for a Q&A assembly cut. Dialed over a long session against the reference editor's reels +
the Q&A Visual Guide; signed off by Operator on the Guest "ExampleClip" exemplar.
Tool: [`scripts/qa_assembly.py`](../scripts/qa_assembly.py) + [`scripts/qa_reframe_v2.py`](../scripts/qa_reframe_v2.py).
Pairs with selection rubric [`../QA_HOTLINE_SOP.md`](../QA_HOTLINE_SOP.md) + [`visual_guide.md`](visual_guide.md).

## The core idea
Cut between **CAMERAS** for variety; each camera holds **ONE consistent size — never zoom in/out
within a camera** (that reads as jarring "zooming"). Reframe is **Y-LOCKED** (only the X crop
keyframes; the eyeline stays fixed) and centers the **face BOX**, not the nose tip.

## The angles (EDL `cam` values)
| cam | source | framing | notes |
|---|---|---|---|
| `speaker` | C2092 (stage) | **3/4 head-to-thigh**, zoom 1.6, eye-y 0.18 | tracked, Y-lock, box-center; the dominant Speaker shot |
| `guest` | C2161 (mic cam) | **chest/waist-up**, zoom 1.4, eye-y 0.24 | tracked, Y-lock, box-center; roomy (not tight) |
| `guest_wide` | C2118 (**side cam**) | punched-in on the standing guest (~3× crop) | static; the room/side angle, used sparingly |
| `split` | C2092 + C2161 | Speaker top (zoom 1.4) / guest bottom + **soft seam drop-shadow** | the open / question |
| `wide` | C2118 | stage side | rarely used |

`speaker` field = who is TALKING (drives caption color later) — a reaction cutaway is `cam: guest, speaker: speaker`.

## Hard rules (from the SOP, enforced in the cut)
- **Speaker's voice/face within 5s** (15s max). Open on split + an early Speaker interjection.
- Contrast hook (activity→revenue), no greetings, ONE problem→solution, payoff at end, ~60-75s.
- Brand-safe: no exact prices / "I fired X".

## Locked visual details
- **Reframe Y-LOCK + box-center** (qa_reframe_v2.py `--lock-y --xcenter box`). This fixed the
  "Speaker too far right" + the vertical bob. ROI is widened so Speaker is tracked across the stage.
- **Split seam = a SOFT drop-shadow** (`assets/seam_shadow.png`, peak α≈0.7 fading down ~107px,
  content stays SHARP). NOT a blur, NOT a hard black bar. Restored after over-softening it once.
- **Side cam (C2118) must be punched IN** on the guest (he's far from it) — fills the frame.
- Format: 1080×1920 (review) — final delivery re-render at 4K. Captions are a SEPARATE later pass.

## Color grade + audio — house look (locked 2026-06-06, baked into qa_assembly)
**This footage is Rec709, NOT log.** The cameras are Sony XAVC recording **BT.709** (ffprobe: `color_transfer=bt709`,
range=tv, YMIN≈0, full contrast). The **"Buttery LUTs" are all log→Rec709 CONVERSION LUTs** (Sony S-Log2/3, BMPCC
Film) — they expect FLAT LOG input and **double-apply** the transform on already-baked 709 → crushed shadows + neon
oversaturation (verified on a frame: the "Natural Rec709" LUT turned Speaker magenta). **Never put a log→709 LUT on
baked footage.** That is why the Visual Guide's two grade presets are marked "missing" — the house grade is a
**curve grade, not a LUT**.
- **Per-cam grade (follows who's ON SCREEN, not the speaker):** Speaker / stage = **bright + saturated + slightly warm**;
  guest = **cool/blue, clean, slightly lower sat**. **Split-screen grades each half independently** (Speaker-top bright,
  guest-bottom cool). Moderate "Premiere-punch," never heavy. Values = qa_assembly globals `SPEAKER_GRADE` / `GUEST_GRADE`
  (eq + colortemperature); `grade_for(cam)` routes them; toggle with `GRADE=False`.
- **Audio = SF "Clean Audio Preset"** (DeNoise → presence/air EQ → compressor → hard limiter) on the spliced
  dialogue **before** the final −14 LUFS loudnorm. qa_assembly globals `CLEAN_AUDIO` / `CLEAN_AUDIO_AF`. The Premiere
  `.prfpset.xml` numeric values are base64-blobbed (unreadable) — the ffmpeg chain mirrors the same signal path.
- **ALWAYS verify the grade on the ACTUAL render** (an Speaker frame reads bright/saturated, a guest frame reads cooler,
  split halves differ) — same eyes-on rule as framing.
- Other SF presets (Music bed, Custom Reverb Fade, Hotline Flashback Vocal Reverb) are music/hotline-FX passes —
  see `references/audio_music_presets.md`; not used on a plain Q&A assembly cut.
- **MUSIC on Q&A = MANUAL — do NOT auto-add** (Operator, 2026-06-07: *"don't add music to the Q&A clips, I'll do that
  manually — it's too nuanced"*). qa_assembly HAS a `--music` engine (vibe track loudnorm'd UNDER the −14 voice,
  `amix normalize=0`, 0.12 s voice fade-in, HARD end, then re-loudnorm the mix back to −14) but it is **OFF by default**.
  Leave Q&A deliverables music-free. The Speaker music lane, IF ever asked, is **score-texture / instrumental trap, NEVER
  the Calm folder, never a melodic-identity song** (see `feedback_speaker_music_selection_logic`) and is high-rejection —
  confirm the lane on one proof before any batch.
- **Render robustness (2026-06-07):** mux + caption encode strip metadata (`-map_metadata -1 -dn` — kills any Sony
  XAVC timecode track); captions auto-trim a stray leading/trailing filler word ("so/and/yeah/um…", audio still plays);
  `qa_audit` now checks **A/V duration parity** (catches a frozen/short video tail).

## Build it
```bash
python scripts/qa_assembly.py --edl EDL.json --out clip.mp4 --sync SYNC.json --no-captions --keep-temp
```
Reframe masters are cached **content-addressed** (by cam+range+framing+reframer-version) in a SHARED
`_qa_mastercache/` next to the output — so they survive across output names AND revisions. A revision that
changes a few boundaries only re-tracks the merged range(s) that actually CHANGED; unchanged ranges reuse
instantly. **Measured: full cold render ~218s → unchanged re-render ~23s (9.5×)** on a 70s clip (per-frame
face detection is the cost; a source proxy does NOT help — see [[reference_qa_build_proxy_noop_2026-06-06]]).
Delete `_qa_mastercache/` to force a clean rebuild. (Was: per-output `_qabuild/` masters keyed by range
INDEX — unsafe to reuse across boundary changes, and a fresh output name rebuilt everything. Fixed 2026-06-07.)

## PER-GUEST override (each guest sits in a different seat)
The locked ZOOMS + drop-shadow + Y-lock logic never change. The guest **crops/ROIs** do, per guest:
`GUEST_HALF` (split bottom), `GUEST_WIDE_CROP` (C2118 side-cam crop+center-x), `GUEST_ROI`
(C2161 reframe ROI), and `SPEAKER_ROI`/`SPLIT_*` if Speaker moved. Set them per clip with a tiny job
wrapper that imports qa_assembly and monkeypatches those globals before `main()` (the proven
pattern — see `2026-06-05_QAWorkshopClips/10_WORK/_guest_build_proxy.py` for the shape), then
verify framing on STILLS first (pull a C2161/C2118 frame, eyeball the crop) before the full render.

## Lessons (paid for in iterations — don't repeat)
- ONE size per camera. Adding close+wide variants of the same cam = "zooming in/out" → Operator hates it.
- Don't over-engineer the seam: soft drop-shadow, sharp content. A blur or a hard band both got rejected.
- Punch the side cam IN (distant subject) but accept it's a touch soft (~3× upscale).
- Calibrate every guest's crops on stills before rendering — guests stand/sit in different spots.
- Reference exemplar clip: `2026-06-05_QAWorkshopClips/10_WORK/_guest_sop_v8.mp4`.

## Robustness (reframe hardening, 2026-06-06 — both verified on the 10-guest batch)
- **No-face fallback** — a guest range with ZERO face detections (a terse beat / glance-down) no
  longer aborts the build; it holds a static ROI-center crop. (Hit Guest A's "More ads / Manpower" beats.)
- **Crop-darkness hold** — the C2092 stage cam shoots OVER the audience, so an audience head can bob
  into the foreground out-of-focus and the tracker briefly grabs it → the CROP goes dark on an
  otherwise-bright frame. qa_reframe_v2 now checks the **crop** brightness (sampled luma), not the full
  frame, and holds the last good crop on a sudden drop (`cm < 50 < prev_cm`). KEY LESSON: a dark frame
  in the output was NOT a decode/encoder/seek bug — I chased those wrongly through 5 re-renders. It was
  the face-tracker grabbing a close foreground head; the full-frame brightness check never fires
  (frame is bright overall), you must check the CROP. Verify dark frames with `signalstats` YAVG, not
  the watch contact-sheet (its tile seek mis-renders near a glitch).
- **Per-guest worked examples:** Guest C (tall → raise split-crop top + widen guest ROI), Guest B (short
  → tighter/lower split crop + lower ROI + guest zoom 1.55). The C2118 side cam drifts over a 90-min
  session — verify its framing per clip or skip it (only Guest used it in this batch).

## Deliver — FINAL STEP (don't leave finished cuts in 10_WORK) — 2026-06-06
When a batch is finished, COPY each final into the project's `20_DELIVER/`, Brand-named per
[[engine-file-nomenclature-sop]]: **`SPEAKER_SF_WORKSHOP_<Title>_Operator_<FOOTAGE-YYYYMMDD>_AC.mp4`**
(SF = short-form deliverable; WORKSHOP = Tier1/L2/L3 Q&A source; AC = assembly cut, captions/grade pending;
date = when the FOOTAGE was SHOT, not today). 10_WORK keeps the work versions (copy, don't move).
**Don't-ship clips** (DO-NOT-USE guests, already-published dupes) → `20_DELIVER/_DONOTSHIP/` with a
README, never loose in the deliver root. Everything stays LOCAL — never push to Frame/Monday without
explicit per-file permission. (Operator, 2026-06-06: "put all these assembly cuts in the delivery folder.
Make sure to do this in the future.")

## Per-guest HEIGHT / reframe — tune for EVERY guest (Operator 2026-06-06: "everyone's a different height")
Framing is NOT one-size — guests sit at different heights in C2161, so TWO INDEPENDENT things must be tuned
per guest (fixing one does NOT fix the other — learned the hard way on Guest A: raised the split, the
full-screen close was still low):
1. **Split-bottom static crop (`GUEST_HALF`)** — a SHORT guest sits low with a big gap above; raise + tighten
   (higher y-offset, smaller height) so the head is ~0.10-0.13 of the panel, chest-up.
2. **Full-screen guest reframe (`GUEST_ROI` / `GUEST_ZOOM` / `GUEST_EYE`)** — a short guest's FACE can fall
   BELOW the default detection ROI (y 0.15-0.48), so the YuNet tracker never locks her -> framed low/loose
   with a huge gap. Fix: LOWER the ROI to cover her real eyeline (e.g. `0.25 0.30 0.60 0.72`) AND raise
   `GUEST_ZOOM` (1.4 -> ~1.9) so the close fills + rises (head ~0.13), `GUEST_EYE` ~0.28.
**ALWAYS verify BOTH framings on the ACTUAL render with vision** (extract the split frame AND a guest-close
frame and look); never trust the preview alone. Set per guest via a job wrapper (monkeypatch GUEST_HALF /
GUEST_ROI / GUEST_ZOOM / GUEST_EYE). Tall guests: defaults usually fine — still verify.
Worked values: **Guest A** (short) GUEST_HALF=`crop=iw*0.285:ih*0.45:iw*0.268:ih*0.374`, ROI=`0.25 0.30 0.60 0.72`,
ZOOM=`1.9`, EYE=`0.28` · **Guest B** (short) ZOOM=`1.55`, ROI lowered · **Guest C** (tall) raised split + widened ROI.

## Revision lessons — Operator's clip-by-clip review (2026-06-07, ACCUMULATING — apply to EVERY clip)
Each clip's review feeds back here so the batch self-corrects. Tool fixes auto-apply on re-render; editorial ones are
review criteria when building/auditing ANY EDL. `qa_assembly.py --dump-map` prints the clip-time→segment/cam/mic map to
translate review timecodes (HH:MM:SS:FF) into EDL edits.
1. **Start ON the hook — ZERO leading words.** No greeting/name ("Hi, my name is…"), no partial pre-hook word.
   Open on the first real hook word ("I own <Company>…"). TOOL: the first segment never snaps EARLIER than its EDL
   start (forward-only), so it can't grab a greeting tail.
2. **Never clip the last word at a cut.** TOOL: `END_TAIL_PAD` (0.12s) keeps the soft trailing consonant
   ("opportunity"→"-ty") past the post-word silence. Verify the word before every hard cut BY EAR, not the transcript.
3. **Cut Speaker's rambles + repeats — value-per-second.** If he meanders/fumbles before landing the point, OPEN him on
   the coherent line, not the lead-in (cut "And so I think that, like, what business are you really in?" → open on
   "You're actually in the training business."). Cut false-starts ("the core value, the core problem" → "the core
   problem"). Every repeat/incoherent beat is wasted seconds. (Matches the 1-pager SOP: fragment-after-trim, kill darlings.)
4. **End on a STRONG natural payoff.** If the last beat is weak, EXTEND past the current end to the real resolving
   insight / belief-breaker, then HARD-cut. Don't end on a soft trailing line.
5. **Guest framing: center the FACE, not the body.** Guests turn/sit off-center — shift the crop so the FACE (not the
   torso) centers; raise + zoom per guest. The split-bottom crop (`GUEST_HALF`) and the full guest reframe
   (`GUEST_ROI`/`GUEST_ZOOM`/`GUEST_EYE`) are tuned SEPARATELY — one can be perfect while the other is off. Verify BOTH.
6. **Prefer split-screen over a long full-guest cam** in some back-and-forth beats — keeps Speaker present, reads better.
7. **Keep brief guest reaction cutaways** (nodding while Speaker talks) — Operator likes them; keep them SHORT (Speaker is the star).
8. **Hook: cut the NAME and the LOCATION too, not just the greeting.** Lead with WHAT THEY DO + the revenue — never who they
   are or where ("I own <Company>… in <City/State>" → drop both; open on "We service residential and commercial clients.
   We do $1.3M…"). Contrast hook = activity → revenue, no identity/geography.
9. **Cut Speaker's "[pause] and so" lead-ins.** He habitually pauses, says "and so," then gets to the point — cut the pause +
   the "and so" and open on the actual content ("And so all of your focus…" → "all of your focus…"). Same for "um"s.
10. **Don't let the end-tail pad catch a trailing "um."** END_TAIL_PAD keeps the last WORD whole, but if a stray "um"/
    breath follows, set the segment end on the word and verify by ear that the pad didn't grab the filler.
11. **AUDIO — don't over-process a quiet-but-clean lav.** Speaker's lav is quiet (~−34 dB) and gets boosted ~+18 dB to hit
    −14 LUFS; an aggressive DeNoise (afftdn) + air-shelf + heavy compression then amplify the noise floor into a hazy,
    smeared "sounds completely shit" tone. Use the GENTLE chain (highpass + de-mud + gentle presence + gentle comp; NO
    afftdn, NO air boost) and a WEIGHTED conv-mix (active speaker mic 1.0, off mic 0.30). Diagnose with a spectrogram:
    the floor should stay DARK in the gaps. (Tool: `CLEAN_AUDIO_AF` + the weighted `amix`.)
12. **Payoff = an actionable to-do — KEEP SEARCHING past the current end for the best moment, don't just extend.** If the
    ending is soft, read further until Speaker lands a concrete framework/belief-breaker the viewer can DO, then hard-cut.
    Length up to ~1.5 min is fine when the payoff earns it (e.g. extended to Speaker's 3-step training system). Still
    precision-cut the path there — no fluff.
13. **Keep the PAYOFF on Speaker — never cut to a full guest cam at the punchline.** Use Speaker-main or split (Speaker-top) for
    variety through a long payoff; a guest full-cam at the resolving line steals the moment.

### From studying the reference editor's PUBLISHED cut of the same moment (2026-06-07, reel DX8BGoVBBpN = TrainingBusiness) — BIG recalibration
The single most useful reference is the reference editor's own published cut of a clip we also have. `yt-dlp` the reel, diarize BOTH
speakers (Groq on each mic), map his keep/cut to source time. What his cut taught (I'd been doing the OPPOSITE):
14. **Keep the REASONING chain, not just the conclusion.** Speaker's logic is what makes the payoff land — keep "how many
    techs? → 25 → you're in a narrow-pay market → you can't get 10× leverage on a cleaning tech → SO you're in the
    training business." Don't jump straight to "you're in the training business." The WHY is the value.
15. **Keep the Q&A DIALOGUE — the guest's answers ARE the content.** Keep the guest's replies ("25 techs," "we do
    one-on-one") that SET UP Speaker's points (her "we do one-on-one" is what makes "it's as costly to train one as five"
    land). It's a Q&A; the back-and-forth is the format. Do NOT compress it into an Speaker monologue.
16. **Cut the side-tangents, protect the spine.** Trim beats that don't advance the ONE through-line (here the reference editor cut
    "people problem / feature not the bug," "supply side," the whole "observable actions / smile-nod-yes-sir-my-pleasure"
    detour, "churn vs attraction," "amazing engineer"). KEEP the spine end-to-end. (I'd been keeping tangents + cutting
    the spine — invert it.)
17. **The payoff = the COMPLETE actionable method + a button.** Run the full system to its natural end (kudos → model →
    role-play → real-time feedback → "the mistake people make" → "lock it in") and close on the line that buttons it
    ("that's how we train anyone on anything"). Don't stop at step 1. **Length follows the payoff — the reference editor shipped 1:44.**
18. **Hook = revenue + the problem + market CONTEXT.** Cut only the NAME + specific location; KEEP context that sharpens
    the problem (e.g. "we're talking 5,000–10,000-town people" = the small labor pool). Don't strip all context.
19. **Don't over-compress.** The aggressive-trim instinct is for FILLER/tangents, NOT for reasoning or dialogue. Keep the
    texture; the clip can run long if every second earns it.
META: when the reference editor has published the same moment, his cut is the editorial ground truth — pull it and match the TRANSCRIPT
choices (not his visual choices: split/title-card are our call — title cards stay the other team's).
20. **WORKFLOW — transcribe the session ONCE, then SLICE; never re-transcribe (Operator 2026-06-07).** Build canonical
    word-level transcripts of each mic a single time → `_transcripts/<mic>.words.json` (Groq, chunked ~900s with offset,
    merged). For every clip/edit/boundary, SLICE the saved JSON by time (`_slice.py <json> <t0> <t1>`) — do NOT re-run
    Groq on overlapping sub-ranges (I'd been wastefully re-transcribing the same audio every round). One transcribe per
    session; reuse forever. (Groq has a ~7200s/hr cap — over-transcribing exhausts it; the cache avoids that. If rate-
    limited, finish the cache with LOCAL `whisper-cli -ml 1` + `ggml-large-v3.bin` — no quota.)
21. **When the reference editor published the SAME moment, make a LITERAL one-to-one — reproduce his exact lines, order (including his
    REORDERS), and trims. Do NOT improvise your own version (Operator 2026-06-07: "you analyzed how he cut it but didn't
    remake it — that's a waste").** Map each of his transcript lines to source time via the cache and build the EDL to
    HIS transcript. e.g. TrainingBusiness: he trimmed the hook to "staffing" ONLY (not turnover/recruiting), cut the
    location, cut "economics matter," and REORDERED narrow-ranges BEFORE cleaning-tech. (Analyzing ≠ remaking.)
22. **Verify BEFORE rendering by RECONSTRUCTING the clip from the cache** — slice each EDL segment's [mic_start,mic_end]
    from `_transcripts/<mic>.words.json` and read the concatenation. It exposes leaks / clips / missing words / wrong
    order (and, for an the reference editor remake, whether it matches his transcript) WITHOUT a 6-8 min render. Then confirm the
    actual render's content with local `whisper-cli` (no Groq). Catch boundary errors on paper, not after rendering.
23. **Boundary precision caveat.** Groq word-level = accurate timing → use it for cut boundaries. `whisper-cli -ml 1` =
    content-OK but COARSE/scrambled timing → don't trust it for sub-second boundaries (good enough for reading content).
    The `END_TAIL_PAD` (+0.12s) RE-INCLUDES the next word at a tight mid-continuous trim (cutting "staffing" right before
    "turnover" with no pause) — set the segment end ~0.15s earlier to compensate, then verify by reconstruction.
24. **The cache you DERIVE boundaries from must be GROQ-accurate end-to-end — local whisper.cpp timing doesn't just blur a
    boundary, it MOVES it onto the wrong audio (2026-06-07, paid for with a full re-cut of a batch).** When a cache is built
    partly with Groq (accurate) and partly with local `whisper-cli` (the offline fallback, used because Groq rate-limited),
    the whisper.cpp half's word-times DRIFT by SECONDS over a long session — so an EDL boundary drawn there lands on
    entirely different words than intended: hooks opened mid-conversation, a guest's NAME leaked back into the hook, and a
    clip's whole TITLE payoff line got dropped. It passed the reconstruction check anyway (lesson 22) because the recon was
    sliced from the SAME coarse cache (right text, wrong times → the render grabbed other audio). FIX, in order:
      a. Build the WHOLE-session cache with Groq word-level timing BEFORE deriving any boundary. If Groq rate-limited
         mid-build, the back half is boundary-UNUSABLE until re-run with Groq once the ~7200 s/hr window recovers (a ~12 s
         test transcribe tells you if quota is back). Back up the old cache (`*.coarse.bak.json`) and fall back to coarse
         PER-CHUNK only on a hard Groq failure, so the cache is never worse than before.
      b. Verify-by-reconstruction (lesson 22) is ONLY trustworthy on the GROQ-accurate cache. A recon off a coarse cache is
         false confidence — content reads fine while the render plays the wrong seconds.
      c. To preserve already-reviewed editorial while fixing ONLY timing: a segment's intent = the WORDS its (coarse)
         boundaries selected; re-find those same words in the accurate cache for true times (pattern `_rederive_edl.py`:
         coarse-slice → anchor head/tail → match in accurate cache → write new boundaries), then let qa_assembly's acoustic
         snap clean the edges. Re-derive, don't re-improvise.
      d. Then RENDER and confirm hook + button by ear/whisper on the ACTUAL file (the snap can still shift a fused edge).
25. **Word-order scrambles in a Groq word-level reconstruction are DISPLAY artifacts, not audio.** Groq emits overlapping
    word timestamps; slicing+sorting by start interleaves them ("the first came thoughts that to mind"). The rendered audio
    plays correctly in real time — judge a reconstruction on CONTENT/COMPLETENESS, never literal token order, and don't
    "fix" a scramble by moving a boundary (you'll clip real audio). A phantom word whose timestamp falls INSIDE the adjacent
    real word is an ASR double-decode — ignore it; keep the segment end on the real word's true acoustic end.
26. **Dead guest mic on a beat → set that segment's `speaker=speaker`** so the audio pulls from Speaker's lav (mic bleed carries
    the guest's voice); `speaker=guest` on a dead mic renders SILENCE (the weighted conv-mix would weight a dead channel
    1.0). Caption color is a later pass — fix the audio first. When unsure which mic has a line, slice BOTH and use whichever
    actually has the words. (Hit on a guest whose lav cut out across the back half + on a guest's mic-dropped closing question.)
META (parallelism): a fan-out of design agents is only as good as the DATA you hand them — the first pass failed because the
agents drew boundaries from the coarse cache. With the Groq-accurate cache + a MANDATORY reconstruction self-verify written
into each agent's contract, a one-agent-per-clip fan-out nailed all of them. Fix the data first, THEN parallelize.
27. **The length cap is a HARD GATE — content importance NEVER overrides it (2026-06-07, paid for with a 2:32 clip).**
    The SOP is 60–75s, **90s HARD CAP**. A clip shipped at 2:32 because the cut brief said "this payoff line is mandatory,
    keep all the proof beats" — but "important" is not a license to blow the cap. If the payoff won't fit in 90s, CUT
    HARDER: keep hook → problem/question → the ONE core principle/method → button, and DROP proof points, supporting
    examples, elaborations, and second-order tangents (e.g. a guest's "we have an AI agent selling 200/mo" stat, a
    "war chest" aside, a churn sub-explanation). A long meaty principle can sit at ~80s; nothing routine should pass 90s.
    When briefing a sub-agent to cut, state 90s as a GATE IT MUST HIT, not a target — and re-check EVERY clip's duration
    before delivery (now enforced in `qa_audit`: it flags any clip > 90s). Over-cap is a fail, not a judgment call.
    EXCEPTION: a LITERAL one-to-one remake of a published reference cut matches the REFERENCE's length (e.g. The reference editor
    shipped TrainingBusiness at 1:44) — the cap governs OUR original cuts, not a faithful reproduction of a longer published one.
28. **EDL segments must be DISJOINT in source time — overlapping ranges REPLAY the same words via mic bleed (2026-06-07,
    found on a rapid-Q&A one-to-one).** Recreating a fast back-and-forth by interleaving speaker-cam and guest-cam segments
    over the SAME source seconds makes lines play TWICE ("what do you charge?" ×2, "one time" ×3) — because BOTH mics carry
    every line via bleed, so two segments covering one source span each replay it. The reconstruction check (lesson 22) does
    NOT catch this — the concatenated text looks like an intentional Q+echo. RULE: no two segments may share >0.1s of source
    time — run `scripts/qa_overlap_check.py EDL.json` before rendering (flags any pair whose [mic_start,mic_end] intersect),
    AND always whisper the actual RENDER to HEAR duplications (the recon can't). For GENUINE crosstalk (two people
    truly talk over each other — e.g. Speaker's "pick one" landing over the guest's "tell me what to do"), you CANNOT make both
    disjoint; segment cuts can't replicate a published editor's frame-level audio ducking, so pick the more important line and
    drop/trim the other. (A fully faithful rapid-volley one-to-one has limits at the segment-cut level — get close, stay clean.)
29. **From the reference editor's PUBLISHED offer-teardown cut (reel DY79):** (a) SNAP-DIAGNOSIS HOOK — open on the guest's setup PLUS the
    expert's instant read ("…consultants. This is going to be an offer issue. I feel it."). The authority's snap judgment right
    after the setup is a strong hook; don't open on the guest alone. (b) KEEP THE RAPID Q&A VOLLEY — he kept the full "what do
    you charge? / 497–997 / one time? / one time" back-and-forth. The volley IS the watchable format and packs more story per
    second than a summarized monologue (I'd compressed it to a summary — wrong). (c) A DEBATE CAN BE THE BUTTON — he ended on
    the live $97-vs-$1000 pricing disagreement + the guest's own reframe ("it's a pitch event — get the price as low as possible
    to get the most people"), NOT a tidy Speaker conclusion. The guest's hard-won realization / an unresolved-but-juicy exchange
    can be the richer ending.
