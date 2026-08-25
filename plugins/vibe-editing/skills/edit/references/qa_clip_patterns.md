# Q&A clip patterns (data-backed, 2026-06-14)

> How a full Q&A (a business owner asks Speaker about their business; he advises) becomes a
> short. Reverse-engineered from the **Highlights highlight channel as the raw source** vs the
> published shorts, mined through your analytics across all platforms and years.
>
> Evidence base:
> - **805 verbatim pairs** — quantitative cut-diff (short text is an exact subset of the highlight)
> - **51 business-Q&A pairs** — qualitative cut-diff (LLM reverse-engineered each editor decision)
> - **48 finished IG Q&A clips** — editorial-structure pass
> - **1,110 short↔source pairs total**, stored in a local database `the source-map` (451 distinct sources)
>
> These apply to the Q&A / hotline branch of `edit`. Monologue/long-form clips → `longform_clip_patterns.md`.

---

## Pipeline shape (805 pairs)

- Source highlight ≈ **250s median** (p90 ~10 min) → short ≈ **35s median** (17–60s typical). ~**9:1 compression**; roughly 1/7 of the runtime survives.
- The short is carved from the **front of the highlight**: it opens at the head (median start **0.6%**, 84% start within the first 10%) and exits around **78%** through. The back ~22% — wind-down + CTA — is discarded.

---

## ENTRY — open the short HERE

| Rule | Detail | Freq |
|------|--------|------|
| **Open at the highlight's head** | Start where the Q&A starts: the guest's intro | 63–84% |
| **Keep the revenue/number** | The credential IS the hook ("$4.3M, 70% margin"; "I did a million three") | 65% |
| **Drop the name/company** | Anonymize — the takeaway must generalize | 92–100% |
| **Use the business-intro template** | `[what I sell] + [revenue] + [goal/constraint]` carried verbatim as the hook | 92% of finished openers |

**Cut the pre-amble:** greetings ("What's up Speaker"), the messy goal-setting ("I thought I wrote 25, now 35…"), disfluencies, and redundant re-phrasings of the question. Drop the viewer straight onto the number.

---

## INTERIOR / SELECTION — keep THIS, cut THAT

1. **Isolate ONE self-contained arc** (near-universal). From a sprawling 4–10 min consult, keep the single cleanest `problem → fix` loop that survives cold with **zero outside context**. Everything situational/niche is cut.
2. **Kill competing threads** even when substantive. (One pair: the editor dropped the more-concrete *sponsorship-revenue* thread to keep the *hiring/leverage* thread, because the latter generalized.)
3. **Extract-and-weld, don't just trim.** Editors keep the intro, **jump across minutes of middle**, and **relocate a later payoff line** to weld on as the closing button. Re-sequencing is normal.
4. **First Speaker move kept** = a diagnostic **question** (~43%) or a **reframe** (~39%); long interrogation chains get cut when a direct prescription is the point.
5. **Compress turns, keep the rhythm.** Strip filler + ASR noise; keep Speaker's crisp one-word beats ("Sure", "Love it", "Good call") for pace. **Numbers are preserved exactly.**

---

## EXIT — end the short HERE

- **Always end on the payoff — 100%.** Never ride into the next sub-question or the wind-down.
- **Payoff type:** **principle 53%** (a portable maxim), then tactic, tough-love, number-reframe.
- **Cut the CTA outro** ("company.com/roadmap", "free gift", "link in bio") — **96%**.
- **Ending forms:** resolved one-liner / hard statement **56%**, on the tactic **21%**, the guest's "thank you" button **19%**, mid-thought cliffhanger **4%**.

---

## STRUCTURE

**`problem → diagnosis → (reframe) → tactic → payoff`** — the dominant arc.
The short = guest states business + number + constraint → Speaker's first probe or reframe → the one tactic/principle → the payoff button. Nothing else.

---

## VISUAL grammar (MEASURED — 71 two-person Q&A shorts, 2026-06-14)

- **OPEN on the split-screen — 82%.** Speaker (host) **top** / guest (questioner at the mic) **bottom**, stacked two-angle with a gaussian seam, held over the hook/question. It appears at the OPENING (often "bookends" the clip) then drops to single. Re-trigger the split at exchange beats.
- **Then cut to the SINGLE angle of whoever is speaking** — guest-single for the question, Speaker-single for the answer. **Switch on the SPEAKER, not on a scene detector** (matched static talking-heads defeat scdet — cut-count under-reads).
- **Captions ride the SEAM / center, never the lower-third** (seam-on-split, else frame-center).
- **Caption color = speaker: white = host (Speaker), yellow = guest — 99%.** EYEBALL it; diarization mis-tags. The reference editor style: bold, word-by-word, size emphasis on key words.
- **Cadence ~one cut / 5s.** Hard-cut on the payoff; never fade or freeze.
- *(Monologue / aphorism shorts differ: single static angle, center captions, single color — that's the listicle look, NOT Q&A. Don't apply Q&A split-screen to a monologue.)*

---

## ANTI-PATTERNS

1. Never keep the name/company intro (drop it; lead with the number).
2. Never keep the CTA outro.
3. Never end on the wind-down or the next question — end on the payoff.
4. Never keep two threads — one self-contained arc only.
5. Never keep situational detail that needs prior context (fails the cold-viewer test).
6. Never leave the payoff where it sat if a better button lives later — relocate it.

---

## NON-OBVIOUS findings (ranked)

1. **Extract-and-weld** — editors re-sequence, relocating a later payoff line to land as the button. The clip's order ≠ the conversation's order.
2. **Caption = generalized principle**, not a line from the clip. The takeaway is abstracted ABOVE the specific case so it reads as universal advice.
3. **Drop the name, keep the number** — the revenue figure is the credential/hook; the name is noise.
4. **Cut the CTA near-universally (96%)** — the roadmap pitch never survives.
5. **The back ~22% is almost always discarded** — it holds the wind-down + CTA; mine the front.

---

## Provenance

- `the source-map` (a local database, brand `your-brand`): 1,110 short↔source pairs, 806 verbatim + 304 semantic, 451 distinct Highlights sources. Source = Highlights highlight channel (1,646 transcribed Q&A highlights).
- Build scripts + raw analysis: `%USERPROFILE%/Videos/vibe-editing/speaker/2026-06-14_Tier1-QA-PatternAnalysis/` (10_WORK: the source-map.json, editorial_learnings.json, business_cutdiff.json, finished_editorial.json).

---

# MEASURED DEEPENING (2026-06-14) — cut performance · camera switches · the reference editor captions

## CUT — which moments WIN (performance-weighted; business-Q&A pairs joined to view counts)
Payoff type → **median views**: **story-button 365K · tough-love 325K · principle 303K (n=28) · number-reframe 296K · TACTIC-only 166K.**
- **End on a PRINCIPLE, a tough-love line, a story button, or a number-reframe — NOT a bare tactic** (tactic-only ≈ halves views).
- **Every top performer (up to 3.3M views) isolates ONE self-contained arc** and drops everything situational — the universal selection rule, performance-confirmed.
- **Keep the guest's revenue number in the opener** (308K vs 283K without it).
- Speaker's first kept move on the winners = a **diagnostic question or a reframe**, never a cold prescription.

## CAMERA-SWITCH grammar (measured, 39 two-person Q&A clips)
- **OPEN on the split** (Speaker top / guest bottom) over the question — 60–67%; **90% use the split somewhere**. (Some cold-open the split ~0.5s only to establish both faces, then collapse to a single.)
- **Primary hard cut = the question→answer handoff** (33/39): cut to the speaker the instant their turn starts, **ON a clause/breath boundary, never mid-word**.
- **Hold the speaker's single through their whole turn** — do NOT cut every sentence; the answerer owns the frame until the payoff.
- **Reopen the split** at exchange beats / Speaker follow-ups (34/39); **reaction-cut** to the listener on a beat (35/39).
- **Punch-in / punch-out reframes on the held single for variety** during long answers (**87%** — 2–3 gentle beats; tighter on key nouns, looser before a list) — these are REFRAMES, not angle switches.
- **Hard-cut the ending on the payoff word, on a live frame** — no fade/freeze.
- Floor case (only two clean angles): guest-single question → ONE cut at the handoff → Speaker-single answer held to the payoff, no split.

## CAPTIONS — the reference editor styling (measured, 40 Q&A clips; builds on the 2026-06-03 19-clip study)
**Confirmed + refined:**
- **Color = voice: white = Speaker, yellow = guest/quoted — 40/40 use yellow** (≈10% run all-white = simpler/older edits; DEFAULT to the white/yellow split).
- **Per-word SIZE emphasis near-universal (39/40)** — tiers emph 1.25 / strong 1.5 / peak 1.85, ≈27% of words bumped.
- **ITALICS are COMMON — 72% (29/40)**, not the old ~10%: quoted/role-played/reflective/guest-emphasis words. Use liberally on the "other voice" + reflective payoff lines.
- **Active-word (karaoke) emphasis — 40/40**: the word being spoken pops/brightens/enlarges as it's said. Word-by-word pop/snap-on reveal (fade on ~⅔).
- **2–4 words per cue**, centered / on the seam, ALL-CAPS common (mixed with title-case).

**NEW conventions (were NOT in the engine — add them):**
- **Spoken "and" → "&" ampersand — 75% (30/40).** Stylize standalone "and" as "&".
- **Profanity self-censored with an asterisk in-caption — 33%** (`B*TCH`, etc.) even when said in full → brand-safe captions.
- **Yellow highlight BOX behind the peak hook word** (e.g. `CONTROVERSIAL?` on solid yellow) — a peak-emphasis device beyond size/weight (~18%).
- **Parentheses ~20%** (asides/clarifiers); **brackets essentially never (1/40) — don't use brackets.**
- **No emoji/stickers as a rule** (~18% have a B-roll overlay or the highlight box; emoji absent).

**TIMING (the fix):** The reference editor's captions are **word-synced — a word never displays before it's spoken**; the cue clears on the pause. Our engine now matches this via `align_to_silence` + pause-split in the spice chain (2026-06-14). → see `caption-clips`.

---

# 🎯 TRANSCRIPT EDITORIAL TRANSFORM — winner-vs-loser ruleset (250 raw→final pairs, perf-tiered, 2026-06-17)

> **What this is.** 250 Highlights raw-highlight→published-short pairs, each tagged with the published short's performance tier (33 top10 · 39 top25 · 129 median · 49 bottom25). For every pair an agent reverse-engineered the editorial transform (entry / cuts / hook / Speaker move / payoff / reorder), then synthesized winner-vs-loser contrasts. This is the SHARPEST signal we have for the EDITORIAL cut — it CORRECTS three rules above. Source: `clip_sources` table; analysis in `speaker/2026-06-14_QAPatternAnalysis/`.
>
> **⚠️ FORMAT NOTE.** These pairs are PODCAST/highlight Q&As (Speaker is the speaker). The Tier1-WORKSHOP diagnostic format (a caller's specific business → Speaker diagnoses) still needs the **business+problem intro** (non-negotiable #3) so a cold viewer knows whose problem it is. BUT every rule below — especially PORTABILITY and "never end on a bare tactic" — applies to BOTH formats and is exactly where the Tier1 batch was weakest.

## THE MASTER GATE — PORTABILITY (the #1 predictor, 2.89x lift)
**94% of winners are fully self-contained (hook + payoff understandable with ZERO prior context) vs only 33% of bottom25.** This is the single strongest signal in the dataset — stronger than hook, payoff, or compression alone. **THE TEST:** read ONLY the first line + the last line, as a cold viewer who knows nothing. Does the hook intrigue AND does the payoff resolve it, standalone? If no → fix the boundaries until yes. Most bottom25 failures reduce to "payoff needs the story/case that got cut" or "opens mid-thought."

## HOOK — open on a WINNING class, never a plain statement
Lift = winner-rate ÷ bottom25-rate:
- **confession ∞** (10 winners, 0 losers) — a raw personal admission. Open cold on it whenever Speaker makes one.
- **vivid_image 4.76x** — one concrete metaphor/image (ocean of fear, shot glass of milk). Beats abstraction.
- **contrarian_claim 3.52x** — a sharp claim that inverts conventional wisdom. THE dominant winning hook (43% of winners).
- number_or_stat / direct_question — **only 0.68x (neutral-negative)**. A bare number wins ONLY when it's shocking AND it's Speaker's. ⚠️ This NUANCES the old "open on the guest's number": opening on a guest's stat a cold viewer can't track is a named bottom25 cause.
- **plain_statement 0.23x — THE DEATH HOOK** (49% of all bottom25). A flat declarative with no contrast/image/number/confession. **If your candidate opener is a plain statement, KEEP HUNTING** the whole answer for a contrarian/confession/image line and lift it to the front. Highest-ROI single fix.
- **none** (no hook function) appears ONLY in bottom25.

## PAYOFF — end on a PRINCIPLE, NEVER a wind-down/tactic/CTA
- **principle 74% of winners** (vs 43% bottom25, 1.72x) — last line = a portable universal maxim ("volume negates luck", "you don't have to feel confident to do it").
- **story_button 2.04x** — if you keep a story, end on its punchline/moral as the literal last line.
- **wind_down 0.06x — THE DEADLIEST ENDING** (22% of bottom25, ~1% of winners): trailing off, guest reaction, polite thank-you, "land the plane." **The defining loser move is STOPPING at the wind-down instead of extending one more sentence to the principle.**
- **tactic 0.11x** — a bare how-to step / acronym-walk. Extend to the principle BEHIND the tactic. (⚠️ THIS is why Tier1 "$25K + $5K/yr" and "give the sickest one away" endings were weak — bare tactics, not principles.)
- **cta 0.0x / cliffhanger 0.68x** — never end on a pitch or unresolved tease.
- The payoff must PAY the hook's setup (resolve the tension the first line opened). Hard-end on the payoff word — no trailing connective ("So,", "or").

## COMPRESSION — ⚠️ RETIRE the "9:1" rule for Q&A
- **Winners are LIGHTLY compressed: top10 median 1.17x; 48% are near-verbatim (<1.15x). Winning band ≈ 1.2–1.5x.**
- **Heavy compression (>5x) is a LOSER signal** (27% of bottom25 vs 6% of top10) — aggressive welding to hit a length target severs the stakes/setup → context-dependent fragment.
- **CUT FOR ONE CLEAN ARC, NOT FOR LENGTH.** Duration does not separate tiers (top10 median ≈151 words ≈ all tiers). Do NOT chase 60s or 9:1. When the source moment is already a clean self-contained arc, leave it nearly intact — just trim front + tail.

## ENTRY & CUTS (frequencies over 250)
- **Always trim the front** (82% skip ≥1 front element). Near-verbatim front = bottom25 tell. Skip, in order: host_question (26%), backstory (10%), disfluency (5%), name/company (4%), goal-setting preamble (3%), greeting (1%). Never open lowercase/mid-fragment.
- **Cut, ranked:** host_interjection 75% · tangent/celebrity-digression 59% · competing_thread 57% (keep ONE of two ideas) · filler_disfluency 55% · redundant_example 54% (keep the most visceral one) · backstory 36% (only if payoff still lands) · restatement_of_question 24% · name_company 24% · wind_down 23% · hedge 20% · cta_outro ~96% when present.

## STRUCTURE
- **ONE ARC ONLY** — single hook→support→principle thread; delete everything that doesn't serve it. Two competing threads = named bottom25 cause.
- **Reorder/weld is fine & tier-neutral** (~30% reach-back in every tier incl. top10): lift the best hook to the front, weld to a clean principle button. Constraint = grammatical continuity at the weld (sentence boundaries, no orphaned pronouns), NOT adjacency. Welding a cleaner span from elsewhere BEATS faithfully cutting a rambly supplied span.
- **Speaker carries the payoff** — hook/button on Speaker's voice, not the guest's. His confessions + tough-love stay verbatim/uncut (highest-lift moments).

## TOPIC as a SELECTION filter (real lift)
Motivation / mindset / wealth / relationships → winners (Motivation 41% of winners vs 13% bottom25). Tactical-business (Pricing, Scaling, how-to, generic advice) → skews bottom25. Portable life-principle answers travel; niche tactical diagnostics don't. **Prefer the portable-principle moment when choosing which exchange to clip.**

## THE ONE-SHOT EDITORIAL CHECKLIST (follow in order, cutting from a raw transcript)
1. Read the full answer; find the ONE self-contained idea. If the obvious moment rambles, scan the whole source for a cleaner span and use THAT.
2. PICK HOOK: punchiest line → must be contrarian / confession / vivid_image. REJECT a plain-statement opener — keep hunting.
3. PICK PAYOFF: the portable PRINCIPLE that ends the arc. If the natural end is a wind-down / bare tactic / CTA / guest reaction, EXTEND to the next principle line.
4. **PORTABILITY GATE:** read hook+payoff only, cold. Intrigue + resolution with zero context? If not, fix boundaries.
5. TRIM FRONT to the hook (first word starts a complete sentence; never lowercase/mid-fragment).
6. ENFORCE ONE ARC: cut host interjections, tangents, the competing thread, redundant examples, restatements, hedges.
7. CUT TAIL: wind-down, sign-off, the whole CTA. Hard-end on the payoff word.
8. COMPRESSION CHECK: cut for arc, not length. >5x → you severed setup, re-add minimum context. Clean source moment → near-verbatim is ideal.
9. VERIFY WELDS: sentence-boundary joins, no orphaned references.
10. COLD-VIEWER READ-THROUGH: winning hook class · one arc · Speaker carries payoff · ends hard on a portable principle.
