---
name: scorecard-audit
description: >
  Runs the company.com 51-rule scorecard against a finished short. Three format variants
  auto-selected: qa (151 max / pass=121), hotline (121 max / pass=97), story (~145 max).
  Catches what sf-audit can't — narrative coherence (N1-N10 including the most-failed
  rule N4 "payoff is the final line"), hook structure (H1 contrast formula, H4 hook bloat),
  editing discipline (E1-E5 incl. fragment-after-trim, redundant examples), and brand
  authority advisories. Auto-translates each failed rule into a tracker.py lesson so the
  precedent retrieval loop sees the lesson on the next similar clip. Final pre-handoff gate
  before sf-audit's classical CV + vision checks. Triggers: invoked as final step of
  shortform / qa-clipper / caption-clips. Manual: "score this clip", "run the scorecard
  audit", "is this clip ready to ship".
---

# scorecard-audit

The narrative + structural QC layer the editing pipeline was missing. SF-sf-audit checks
subtitles/audio/video mechanics; the scorecard checks whether the clip is actually a good
piece of content. Together they form the full pre-handoff gate.

Sourced from the company.com editing team's scorecard (Q&A, Hotline, Story format
variants — `prompts/qa.md`, `hotline.md`, `story.md`). Schema matches theirs exactly so
the JSON is interoperable with their internal Electron scoring app.

---

## What gets checked (Q&A = 51 rules, 151 max points)

| Category | Rules | Max | Most-failed |
|----------|-------|----:|-------------|
| Hook & Retention | H1-H5 | 25 | H1 (contrast hook formula) |
| Pacing & Timing | P1-P8 | 27 | P3 (runtime under 90s) |
| **Narrative Focus** | **N1-N10** | **37** | **N4 — payoff is the final line (THE most-failed rule)** |
| Subtitles & Text | S1-S11 | 26 | S5 (number/$ format), S4 (lowercase) |
| Brand & Framing | B1-B7 | 18 | B2 (Speaker authority maintained) |
| Editing Discipline | E1-E5 | 10 | E3 (fragment-after-trim), E4 (redundant examples) |
| Brand Risk | R1-R4 | 8 | R3 (no trigger words <15s) |

Pass threshold: 80% = 121 / 151. Hotline = 97 / 121. Story varies (see prompts/story.md).

Visual-only rules (S1, S2, S3, S7, B5, B6, B7, HH5) return `null` here — they're handed
off to sf-audit's classical-CV + vision-MCP checks.

---

## Usage

```bash
# Minimum (auto-detects format from transcript density + duration)
python ${CLAUDE_PLUGIN_ROOT}/skills/scorecard-audit/scripts/scorecard.py \
  --transcript /tmp/shortform-work/transcript.json \
  --clip %USERPROFILE%/Videos/vibe-editing/speaker-clip-v1.mp4

# Full — wired with profile fields + autolog into clip-review-tracker
python ${CLAUDE_PLUGIN_ROOT}/skills/scorecard-audit/scripts/scorecard.py \
  --transcript transcript.json --clip clip-v1.mp4 \
  --format qa \
  --client speaker --clip-slug pricing-rant \
  --clip-type q\&a --gesture-profile speaker_hand_enters_upper_frame \
  --caption-style pro --hook-type revenue-first \
  --exit-on-fail
```

Flags:
- `--transcript` (required) — our standard transcript.json schema (post-align + correct)
- `--clip` — optional, only used for path/report co-location
- `--format` — `qa`, `hotline`, `story`. Auto-detected if omitted
- `--client`, `--clip-slug` — required for failure-→-lesson autolog (skip with `--no-autolog`)
- `--clip-type`, `--gesture-profile`, `--caption-style`, `--hook-type` — feed into the
  WHEN clause of auto-logged lessons so they generalize to similar clips
- `--exit-on-fail` — non-zero exit if total_score < pass threshold (use as ship gate)
- `--model` — default `claude-sonnet-4-5`

---

## Outputs

Two files written next to the clip (or transcript if no `--clip`):

1. **`<clip>.scorecard.json`** — schema matches their Electron app exactly, every rule with
   `score / max / pass / flag / timestamp`. Categories + total + pass + brand_advisory.

2. **`<clip>.scorecard.md`** — human-readable report. Total at top, category breakdown table,
   failed-rules section with timestamps + flags, visual-check-required list.

---

## Auto-log to clip-review-tracker

When `--client` + `--clip-slug` are provided, every failed rule (excluding visual-only)
becomes a `tracker.py lesson` entry. The WHEN clause is built from the profile flags so the
lesson generalizes — `WHEN: client=speaker AND clip_type=q&a AND gesture_profile=X AND
caption_style=pro AND hook_type=revenue-first`. The THEN clause is pulled from a canonical
"what to do next time" map for each rule (e.g., N4 → "Payoff is the FINAL audible line. Cut
everything after the payoff lands.").

This closes the feedback loop with `find-precedents` — failures on this clip surface as
precedents on the next similar one.

---

## Auth

Uses `ANTHROPIC_API_KEY` from `config/keys.env` via the Anthropic Python SDK (preferred). Falls
back to `claude -p` if no key. Same setup as `correct_transcript.py`.

---

## Integration

This is **step 11** of the shortform pipeline (after all mechanics + captions + render +
classical audit). Wired automatically — see `shortform/SKILL.md`, `qa-clipper/SKILL.md`,
`caption-clips/SKILL.md` for the call sites.

The full QC stack at handoff time:
1. `sf-audit --client <slug> --safe-zones doac.json` — 16-point mechanics + CV checks
2. **`scorecard-audit --client <slug> --clip-slug <slug> ...`** — 51-rule narrative + structural
3. Both must pass before `tracker.py transition <slug> audited-v1-pass`

## ⭐ CONTEXT rule — NARRATIVE gate (added 2026-06-07, Operator's #1 note)
**Any commentary / reaction / answer / Q&A clip MUST include the QUESTION or STORY it responds to.** A bare answer where the speaker references a scenario the viewer never heard ("her ex had surgery and went back to him", "after 16 years of being lied to") = an automatic narrative FAIL — the viewer is lost. Score it like the most-failed coherence rules (sits next to N4 "payoff is the final line"):
- **CONTEXT present?** The setup the commentary references is in the clip (ideally the clip OPENS on the submitted question/story, then the answer). FAIL if the answer floats without its question.
- Fix = prepend the submission (multi-segment cut, question span + commentary span); see [[CLIP_CUTTING_PLAYBOOK]] step 0 + the `multicam-podcast-clipper` / `recut.py` pattern. This applies to ALL footage (Speaker hotline, podcasts, everything) — not just multicam.
