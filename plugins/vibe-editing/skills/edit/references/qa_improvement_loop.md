# Q&A IMPROVEMENT LOOP — the standing routine for making Q&As more perfect over time

> "Perfect" isn't a state, it's a flywheel. Run this loop every batch/review. The one rule that makes it
> real: **measure before and after every change** — improvement we can't see in the cold-start number is
> hope, not progress. Our unfair advantage: we have the RAW footage + the reference editor's published cut + real views,
> so we can improve against a master editor AND the audience, not by guessing.

## The 6 mechanisms (each turn of the flywheel)
1. **Grow the answer key.** Whenever the reference editor posts clips from footage we have, link them back (scrape→match
   method, see [`qa_calibration/README.md`](qa_calibration/README.md)) → new raw→the reference editor pairs. Bigger corpus = better calibration.
2. **Capture every review as a durable artifact.** A cut you APPROVE → add to [`qa_worked_examples.md`](qa_worked_examples.md)
   (gold to pattern-match). A cut you REJECT → its reason becomes a GATE rule or a counter-example. Never
   leave a lesson as prose only ([[feedback_compounding_standard_default_plus_gate_2026-06-12]]).
3. **Run the regression harness on EVERY skill change (keystone).** A cold agent reads only the skill files,
   cuts held-out raws blind, scores on FUNDAMENTALS (not the reference editor-similarity). Baseline 2026-06-17: 58 cold /
   ~89–93 carefully-applied. Re-run after any edit → did the number go UP? If not, revert. (Harness =
   `qa-coldstart-validation` workflow; held-out raws in `_spice_calibration/_coldstart_test/`.)
4. **Gate, don't warn.** Every failure mode found → a BLOCKING check in `qa_editorial_score.py` /
   `qa_prebuild_audit.py`. The floor only rises; a mistake caught once can't ship again.
5. **Self-correct at design time.** `cut_design.py` generates → scores → repairs until it PASSES the gate.
   This is what converts "knows the rules" into "applies them every time." Use it as the cut step.
6. **Validate the rubric against real views (periodic).** Our fundamentals rubric is a hypothesis of "good";
   your analytics has the actual views/tiers. Periodically check: do our high-scoring cuts actually outperform?
   If a fundamental doesn't correlate with views, reweight it. Tune what "good" MEANS, not just apply it.

## The bar
**85%+ on fundamentals + "is it a genuinely good clip"** — NOT transcript-match to the reference editor (he's inconsistent;
every guest is nuanced). Fundamentals: contrast hook · one clean arc · reasoning ladder kept · ends on
portable principle/quantified result · compressed (no detour after the answer) · portable · brand-safe · postable.

## Run it (a cycle)
```
# 1. cut with the self-correcting designer (won't emit until it passes the gate)
python ${CLAUDE_PLUGIN_ROOT}/skills/edit/scripts/cut_design.py --raw <guest_raw.txt> --precontext "<earlier intro>"
# 2. human review → approve or reject
#    approve → paste the cut into qa_worked_examples.md with a beat-by-beat why + score
#    reject  → add the reason as a rule in qa_editorial_score.py RULESET (or a gate in qa_prebuild_audit)
# 3. prove the change helped — re-run the regression harness, confirm the cold score went UP
# 4. sync the 4 SOP copies + backup_brain.sh
```
Each cycle: corpus grows → your taste becomes examples + gates → harness proves it helped → generation
self-corrects → views keep the rubric honest. The skill gets measurably better every review.
