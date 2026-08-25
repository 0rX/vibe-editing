---
name: audit-script
description: >
  Dedicated editorial/script auditor. Receives ONLY the transcript text of a rendered clip
  (no video, no audio). Checks logical flow, context-before-payoff, cold viewer comprehension,
  one-arc structure, hook quality, brand safety, and SOP compliance. Uses all editorial SOPs
  (post bible, scorecard, Q&A SOP, hooks taxonomy). Runs in fresh context with NO knowledge
  of how the clip was made or what footage it came from.
  Returns structured pass/fail per check with specific line references.
  Part of the post-render audit fan-out at edit step 9.
---

# audit-script — editorial-only quality gate

> Fresh-context agent. Receives ONLY the transcript text of the rendered clip.
> No video, no audio, no editing context. Tests whether the WORDS make sense
> to a cold viewer who just opened this video.

## How to run

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/audit-script/scripts/check.py \
    --clip 20_DELIVER/v1/clip.mp4 \
    --out 10_WORK/audit_script.json
```

The script transcribes the clip independently (Groq), then runs all editorial checks
on the text. It does NOT read any prior transcript or mining results.

## What it checks

### 1. COLD VIEWER TEST — does every line make sense with zero context?
- Read the transcript as if you just opened this video with no prior knowledge
- For each line, ask: "Does this make complete sense given ONLY the lines before it?"
- Flag: dangling references ("that focus", "what he said", "the same thing", "her ex")
  where the referent was never stated in this clip
- Flag: jargon or terms used without definition ("one avatar", "grand slam offer",
  "the funnel") that a cold viewer wouldn't understand
- Flag: mid-conversation continuations ("...and that's why", "so basically", "the point is")
  that assume the viewer heard something they didn't
- **FAIL** if any line requires context the clip doesn't provide

### 2. CONTEXT BEFORE PAYOFF — is the setup present?
- If this is a Q&A/commentary clip: does the QUESTION appear before the ANSWER?
- If this is a story clip: is there a setup before the punchline?
- If this is advice: is the PROBLEM stated before the SOLUTION?
- The viewer should understand WHY the speaker is saying what they're saying
- **FAIL** if payoff arrives without setup

### 3. ONE-ARC RULE — one topic, one story, one payoff?
- The clip should cover ONE thing. Not two half-stories stitched together.
- Flag: topic changes mid-clip ("...anyway, on a different note", or an abrupt shift
  from pricing to hiring to marketing)
- Flag: two separate Q&A pairs merged into one clip
- **FAIL** if the clip contains more than one distinct topic/arc

### 4. HOOK QUALITY — would a stranger stop scrolling?
- The first sentence must be compelling on its own
- Rate the hook: would a stranger who doesn't know the speaker stop scrolling?
- Check against hooks taxonomy (contrarian, story, stat, confession, stakes, question, list, reveal)
- Flag: hooks that are generic ("today we're going to talk about...")
- Flag: hooks that require insider knowledge to be interesting
- **WARN** if hook is weak (not a hard fail — subjective)

### 5. PAYOFF LANDS — does the ending resolve the setup?
- The last sentence should deliver a clear conclusion, lesson, or punchline
- Flag: trails off ("so yeah, that's kind of the thing...")
- Flag: introduces a new idea in the last line (no resolution)
- Flag: ends on a question without an answer (unless that's the hook structure)
- **FAIL** if the ending doesn't resolve the setup

### 6. LOGICAL FLOW — are there jumps in logic?
- Between each sentence, check: does this follow from the previous one?
- Flag: missing connecting logic where a cut removed a bridging sentence
- Flag: pronouns with no clear antecedent
- Flag: cause-and-effect claims where the cause was cut
- **WARN** if flow feels choppy (some choppiness is intentional for pacing)

### 7. BRAND SAFETY — does this comply with SOPs?
- No specific dollar amounts (unless the content type allows it)
- No competitor names
- No profanity (unless the brand allows it)
- No claims that could create legal liability
- Respects the brand's content guardrails (loaded from vocab/brand config if available)
- **FAIL** if any brand safety rule is violated

### 8. LENGTH APPROPRIATENESS
- Shorts: 25–40s of speech
- Mids: 60–75s of speech
- Hard cap: 90s
- Flag: clip is >90s of speech
- Flag: clip feels padded (could deliver the same point in half the time)
- **WARN** if over-length or padded

## Output format

```json
{
  "clip": "clip.mp4",
  "verdict": "FAIL",
  "transcript_word_count": 187,
  "estimated_duration_s": 52,
  "checks": {
    "cold_viewer": {"pass": false, "issues": [
      {"line": 3, "text": "that's why I always say focus on the avatar", "problem": "dangling reference: 'the avatar' never defined in this clip"}
    ]},
    "context_payoff": {"pass": true},
    "one_arc": {"pass": true},
    "hook_quality": {"pass": true, "hook_type": "contrarian", "hook_text": "Most people think revenue is the goal"},
    "payoff_lands": {"pass": true},
    "logical_flow": {"pass": true},
    "brand_safety": {"pass": true},
    "length": {"pass": true, "category": "short"}
  },
  "summary": "FAIL: cold viewer test — 'the avatar' referenced at line 3 but never defined in this clip"
}
```

## Fix instructions on failure

- Cold viewer issue → either add the missing context line to `cuts.json` (extend the clip)
  or rewrite/remove the line that references it
- Missing context/setup → extend the clip start in `cuts.json` to include the question/setup
- Multiple arcs → split into two clips, or trim one arc out in `cuts.json`
- Weak hook → consider starting the clip later at a stronger opening line
- Trailing payoff → trim the end in `cuts.json` to end on the strongest beat
- Brand safety → remove the offending line in `cuts.json`

## SOPs this agent should have loaded

When running as a sub-agent, load these references for the editorial checks:
- `${CLAUDE_PLUGIN_ROOT}/vault/CLIP_CUTTING_PLAYBOOK.md` — global cutting rules
- `edit/references/hooks_taxonomy.md` — hook classification
- `edit/QA_HOTLINE_SOP.md` — Q&A/Hotline specific rules (if Q&A content)
- The brand's `vocab.txt` if available (for jargon validation)
