"""Concurrency test for the Windows encode_gate rewrite.

The gate replaced POSIX fcntl.flock with msvcrt byte-range locking. A broken lock does
not raise — it silently lets every worker through at once, and the only symptom is
thrashed renders under load. So this test asserts the invariant directly: spawn far more
workers than there are slots and prove the machine-wide cap actually holds.

Run:  python tests/test_encode_gate.py
Exit 0 = pass.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "lib" / "_shared"
sys.path.insert(0, str(SHARED))

from winenv import enable_utf8  # noqa: E402

enable_utf8()  # this file prints non-ASCII; cp1252 would mangle or crash on it

WORKERS = 8
SLOTS = 3
HOLD = 0.4  # seconds each worker holds its slot

# Child process: acquire a slot, record enter/exit timestamps as JSON, release.
CHILD = r"""
import json, sys, time
sys.path.insert(0, r"{shared}")
from encode_gate import gate
with gate(timeout=60):
    t0 = time.time()
    time.sleep({hold})
    t1 = time.time()
print(json.dumps([t0, t1]))
"""


def main():
    slot_dir = Path(os.environ["VIBE_ENCODE_SLOT_DIR"])
    print(f"  slots={SLOTS} workers={WORKERS} hold={HOLD}s")
    print(f"  slot dir: {slot_dir}")

    src = CHILD.format(shared=str(SHARED), hold=HOLD)
    procs = [
        subprocess.Popen([sys.executable, "-c", src],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for _ in range(WORKERS)
    ]

    spans = []
    failed = False
    for i, p in enumerate(procs):
        out, err = p.communicate(timeout=180)
        if p.returncode != 0:
            print(f"  FAIL worker {i} exited {p.returncode}: {err.strip()[:400]}")
            failed = True
            continue
        try:
            spans.append(tuple(json.loads(out.strip().splitlines()[-1])))
        except Exception as e:
            print(f"  FAIL worker {i} unparseable output {out!r}: {e}")
            failed = True

    if failed or len(spans) != WORKERS:
        print(f"\n  FAILED — {len(spans)}/{WORKERS} workers reported cleanly")
        return 1

    # Sweep the timeline: at every enter event, count how many spans overlap it.
    peak = 0
    for t0, _ in spans:
        n = sum(1 for a, b in spans if a <= t0 < b)
        peak = max(peak, n)

    total = max(b for _, b in spans) - min(a for a, _ in spans)
    print(f"  peak concurrent holders: {peak}  (cap {SLOTS})")
    print(f"  wall clock: {total:.2f}s")

    if peak > SLOTS:
        print(f"\n  FAILED — {peak} workers held slots at once, cap is {SLOTS}.")
        print("  The lock is not excluding anything.")
        return 1

    # Serialization sanity: 8 workers x 0.4s through 3 slots cannot finish in one hold
    # window. If it did, the workers never actually queued.
    floor = (WORKERS / SLOTS) * HOLD * 0.5
    if total < floor:
        print(f"\n  FAILED — finished in {total:.2f}s, too fast to have queued "
              f"(expected at least ~{floor:.2f}s).")
        return 1

    print("\n  PASSED — cap held and work serialized.")
    return 0


if __name__ == "__main__":
    # Use a dedicated slot dir + cap so a real encode running on this machine can't
    # perturb the test, and the test can't steal that encode's slots.
    import tempfile
    os.environ["VIBE_ENCODE_SLOTS"] = str(SLOTS)
    with tempfile.TemporaryDirectory(prefix="gate_test_") as td:
        os.environ["VIBE_ENCODE_SLOT_DIR"] = td
        sys.exit(main())
