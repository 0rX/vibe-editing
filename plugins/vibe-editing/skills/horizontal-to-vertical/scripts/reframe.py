#!/usr/bin/env python
"""LEGACY - kept only because listicle-short/build_short.py still calls it.
NEW CODE: use qa_reframe_v2.py --preset <name> (Y-LOCK + xcenter box). This is NOT the
canonical face-tracker.

horizontal-to-vertical - 16:9 -> 9:16 reframe + face tracking.
  per-frame multi-cascade Haar detect -> box-car smooth 51 -> crop's X follows the nose
  to a fixed center (540 in 1080-ref), Y locked at the eye line; zoom 1.15 (86% crop).
Reframe + facetrack ONLY -- captions / color grade / music are SEPARATE workflow steps.

Usage: reframe.py INPUT [OUTPUT] [--res auto|1080|4k] [--zoom 1.15]
  INPUT   horizontal clip (any res, single angle)
  OUTPUT  defaults to <input>_9x16.mp4
  --res   auto (default): 4K source -> 2160x3840, else 1080x1920
  --zoom  1.15 locked default (= 86% crop height)
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "lib" / "_shared"))
from winenv import PY, which  # noqa: E402


def ffprobe_height(path: str) -> int:
    out = subprocess.run(
        [which("ffprobe") or "ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=height", "-of", "csv=p=0", path],
        capture_output=True, text=True).stdout.strip()
    try:
        return int(out.splitlines()[0])
    except (ValueError, IndexError):
        return 0


def count_hard_cuts(path: str) -> int:
    """Scene-change count, used only to warn about multi-angle sources.

    A single-median X track loses the subject across angle switches, so this is a heads-up,
    never a failure.
    """
    r = subprocess.run(
        [which("ffmpeg") or "ffmpeg", "-i", path, "-vf", "select='gt(scene,0.3)',showinfo",
         "-an", "-f", "null", "-"],
        capture_output=True, text=True)
    times = [float(m) for m in re.findall(r"pts_time:([0-9.]+)", r.stderr or "")]
    return sum(1 for t in times if t > 0.5)


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("input")
    ap.add_argument("output", nargs="?", default=None)
    ap.add_argument("--res", default="auto", choices=["auto", "1080", "4k"])
    ap.add_argument("--zoom", default="1.15")
    ap.add_argument("--nose-y", default="719",
                    help="nose Y in the 1080x1920 ref (lower value = subject higher)")
    ap.add_argument("--smooth", default="51")
    ap.add_argument("--lock-x", action="store_true")
    ap.add_argument("--eye-y-src")
    ap.add_argument("--eye-y-out")
    a = ap.parse_args()

    inp = a.input
    out = a.output or str(Path(inp).with_suffix("")) + "_9x16.mp4"

    if a.res == "4k":
        ow, oh = 2160, 3840
    elif a.res == "1080":
        ow, oh = 1080, 1920
    else:
        ow, oh = (2160, 3840) if ffprobe_height(inp) >= 2160 else (1080, 1920)

    ncuts = count_hard_cuts(inp)
    if ncuts:
        print(f"WARN: {ncuts} hard cut(s) detected -- looks multi-angle. Single-median "
              f"X-track may lose the subject on angle switches; handle per-segment "
              f"(see SKILL.md multi-angle note).", file=sys.stderr)

    work = Path(tempfile.mkdtemp(prefix="reframe_"))
    try:
        face = work / "face.json"
        print("> [1/2] dense face detect (per-frame multi-cascade Haar)")
        subprocess.run([PY, str(HERE / "detect_face_dense.py"), inp, str(face)], check=True)

        print(f"> [2/2] reframe {ow}x{oh}  zoom {a.zoom}  smooth {a.smooth}  "
              f"(X->nose@540,{a.nose_y}  Y-locked)")
        cmd = [PY, str(HERE / "reframe_h2v.py"), "--video", inp, "--face-json", str(face),
               "--output", out, "--out-w", str(ow), "--out-h", str(oh),
               "--zoom", str(a.zoom), "--smooth", str(a.smooth),
               "--nose-x-1080", "540", "--nose-y-1080", str(a.nose_y)]
        if a.lock_x:
            cmd.append("--lock-x")
        if a.eye_y_src:
            cmd += ["--eye-y-src", a.eye_y_src]
        if a.eye_y_out:
            cmd += ["--eye-y-out", a.eye_y_out]
        subprocess.run(cmd, check=True)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    print(f"OK {out}")
    print("   verify framing by EYE (extract frames) -- the audit centering flag "
          "false-negatives on weak detection.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
