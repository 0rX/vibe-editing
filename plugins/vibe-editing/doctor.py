#!/usr/bin/env python
"""Vibe Editing — machine check + install planner (Windows).

Checks what's already on this machine and prints the EXACT commands to install ONLY
what's missing (check-then-install). Run it, install the gaps it lists, run it again,
repeat until it says READY. Exit 0 = ready, 1 = something to install.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "lib" / "_shared"))

from winenv import PY, enable_ansi, enable_utf8, free_gb, has_key, output_root, which, work_dir  # noqa: E402

enable_utf8()
_COLOR = enable_ansi()

G = "\033[92m" if _COLOR else ""
R = "\033[91m" if _COLOR else ""
Y = "\033[93m" if _COLOR else ""
X = "\033[0m" if _COLOR else ""


def mark(b):
    return f"{G}OK{X}" if b else f"{R}MISSING{X}"


def has(c):
    return which(c) is not None


def pyimp(m):
    try:
        __import__(m)
        return True
    except Exception:
        return False


# winget package IDs for each command we need.
WINGET = {
    "ffmpeg": "Gyan.FFmpeg",
    "yt-dlp": "yt-dlp.yt-dlp",
    "tesseract": "UB-Mannheim.TesseractOCR",
    "rclone": "Rclone.Rclone",
    "node": "OpenJS.NodeJS.LTS",
}

winget_need, pip_need, notes = [], [], []
crit_ok = True

print("\n  Vibe Editing — machine check (Windows)\n  " + "-" * 44)

# ── system tools ──
ffmpeg, ffprobe = has("ffmpeg"), has("ffprobe")
libass = False
if ffmpeg:
    try:
        out = subprocess.run([which("ffmpeg"), "-hide_banner", "-filters"],
                             capture_output=True, text=True).stdout
        libass = "subtitles" in out
    except Exception:
        pass
print(f"  ffmpeg + libass    {mark(ffmpeg and ffprobe and libass)}")
if not (ffmpeg and ffprobe and libass):
    winget_need.append("ffmpeg")
    crit_ok = False
    if ffmpeg and not libass:
        # A minimal ffmpeg build cannot burn captions, which is core to this product.
        notes.append("ffmpeg found but built WITHOUT libass — captions cannot be burned. "
                     "Install the full build: winget install Gyan.FFmpeg")

ytd = has("yt-dlp")
print(f"  yt-dlp (URL in)    {mark(ytd)}")
if not ytd:
    winget_need.append("yt-dlp")
    crit_ok = False

tess = has("tesseract")
print(f"  tesseract (audit)  {mark(tess)}  {Y}(optional){X}")
if not tess:
    winget_need.append("tesseract")

rcl = has("rclone")
print(f"  rclone (drive in)  {mark(rcl)}  {Y}(optional){X}")
if not rcl:
    winget_need.append("rclone")

node = has("node")
print(f"  node (promo skill) {mark(node)}  {Y}(optional){X}")
if not node:
    winget_need.append("node")

# ── encoder ──
print("  " + "-" * 44)
if ffmpeg:
    try:
        from fast_encode import describe
        print(f"  video encoder      {G}{describe(which('ffmpeg'))}{X}")
    except Exception as e:
        print(f"  video encoder      {R}probe failed{X}  {Y}({e}){X}")
else:
    print(f"  video encoder      {Y}unknown until ffmpeg is installed{X}")

# ── python deps ──
print("  " + "-" * 44)
deps_missing = False
for mod in ["numpy", "cv2", "PIL", "scipy", "librosa", "soundfile", "requests"]:
    ok = pyimp(mod)
    print(f"  py:{mod:<15} {mark(ok)}")
    if not ok:
        deps_missing = True
        crit_ok = False
anth = pyimp("anthropic")
print(f"  py:anthropic      {mark(anth)}  {Y}(captions){X}")
if not anth:
    deps_missing = True
if deps_missing:
    pip_need.append("-r requirements.txt")

# ── assets ──
print("  " + "-" * 44)
font = any((ROOT / "skills/caption-clips/fonts").glob("*.ttf")) or \
       any((ROOT / "skills/caption-clips/fonts/free_font").glob("*.otf"))
yunet = (ROOT / "skills/horizontal-to-vertical/scripts/yunet.onnx").exists()
print(f"  caption fonts      {mark(font)}")
print(f"  face model (yunet) {mark(yunet)}")
crit_ok &= font and yunet
if not font:
    notes.append("caption fonts missing — re-download the kit")
if not yunet:
    notes.append("face model yunet.onnx missing — re-download the kit")

# ── transcription (key-free by default via local whisper) ──
print("  " + "-" * 44)
groq = has_key("GROQ_API_KEY")
fw = pyimp("faster_whisper")
anth_key = has_key("ANTHROPIC_API_KEY")
transcribe_ok = groq or fw
why = ("Groq — fast" if groq else
       "local whisper — SLOW on CPU; add a free Groq key for ~10x faster" if fw else
       "add a free Groq key (console.groq.com) — or pip install faster-whisper")
print(f"  transcription      {mark(transcribe_ok)}   {Y}({why}){X}")
if not transcribe_ok:
    pip_need.append("faster-whisper")
    crit_ok = False
cap = "Anthropic key" if anth_key else "claude CLI / built-in fallback"
print(f"  caption styling    {mark(True)}   {Y}({cap}){X}")

# ── environment ──
print("  " + "-" * 44)
in_venv = sys.prefix != sys.base_prefix
print(f"  interpreter        {PY}")
print(f"  virtualenv         {mark(in_venv)}  {Y}({'active' if in_venv else 'running system Python'}){X}")
if not in_venv:
    notes.append(r"not running inside the project venv — use .venv\Scripts\python.exe")
utf8 = (sys.stdout.encoding or "").lower().replace("-", "") == "utf8"
print(f"  console encoding   {mark(utf8)}  {Y}({sys.stdout.encoding}){X}")
if not utf8:
    notes.append("console is not UTF-8 — set PYTHONUTF8=1 (setup.ps1 does this) or "
                 "scripts printing arrows/checkmarks will crash")
free = free_gb(output_root())
low = free < 20
print(f"  free disk          {'' if low else G}{free:.0f} GiB{X}  {Y}({output_root()}){X}")
if low:
    notes.append(f"only {free:.0f} GiB free — video work needs headroom")
print(f"  scratch dir        {work_dir()}")

# ── verdict + install plan ──
print("  " + "-" * 44)
if crit_ok:
    print(f"  {G}READY{X} — run:  /edit <your link>   (or .\\bin\\vibe-editing.ps1 \"<link>\")\n")
    for n in notes:
        print(f"    {Y}note:{X} {n}")
    if notes:
        print()
    sys.exit(0)

print(f"  {R}NOT READY{X} — install ONLY what's missing:\n")
if winget_need:
    ids = [WINGET[c] for c in dict.fromkeys(winget_need)]
    print("    winget install --accept-package-agreements --accept-source-agreements \\")
    print("        " + " ".join(f"--id {i}" for i in ids))
    print(f"    {Y}# then open a NEW terminal so PATH picks them up{X}")
if pip_need:
    print(f"    cd {ROOT}")
    print(r"    python -m venv .venv && .venv\Scripts\python.exe -m pip install "
          + " ".join(dict.fromkeys(pip_need)))
    if "faster-whisper" in pip_need:
        print("    # ↑ FASTER alternative: skip whisper and paste a free GROQ_API_KEY into")
        print("    #   config/keys.env (console.groq.com) — ~10x faster, better quality, no install.")
for n in notes:
    print(f"    ! {n}")
print(f"\n  Then re-check:  python {Path(__file__).name}\n")
sys.exit(1)
