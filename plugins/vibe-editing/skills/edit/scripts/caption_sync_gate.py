#!/usr/bin/env python3
"""caption_sync_gate.py — does the BURNED caption text match the DELIVERED audio? Catches the
'captions don't line up because we cut' defect: the caption track was built from a transcript that no
longer matches the final cut audio, so it shows words the audio dropped (or misses words the audio has).

Origin: an example clip V7 (2026-06-22) — caption said 'different' (the cut removed it) and missed 'right'
(the audio had it). Operator: "captions are not lining up because we did the cuts."

Re-transcribes the DELIVERED clip's audio (whisper large-v3) and diffs it against the caption text, after
normalizing away pure tokenization noise (contraction splits we've/we 've, number-word<->digit, hyphen
splits day-to-day/day to day, punctuation). Real residual mismatches = caption-only words (on screen, not
spoken) or audio-only words (spoken, not captioned).

Usage:
  caption_sync_gate.py --cc cc_text.ass --clip CLIP.mp4 [--audio-words fresh_lv3.json] [--max-mismatch 1]
Exit 0 = in sync (<= max-mismatch real diffs) · 1 = caption/audio mismatch.
"""
# ── winenv bootstrap: locate the plugin's shared lib ──
import os as _os6, sys as _sys6
_d6 = _os6.path.dirname(_os6.path.abspath(__file__))
while _d6 != _os6.path.dirname(_d6) and not _os6.path.isdir(_os6.path.join(_d6, '.claude-plugin')):
    _d6 = _os6.path.dirname(_d6)
_sys6.path.insert(0, _os6.path.join(_d6, 'lib', '_shared'))
from winenv import whisper_cli, whisper_model  # noqa: E402
# ── end winenv bootstrap ──
import argparse, re, json, subprocess, difflib, sys, os, tempfile
from pathlib import Path

NUMWORD = set(("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety "
    "hundred thousand million billion first second third fourth fifth sixth seventh eighth ninth tenth").split())

def canon(words):
    """Reduce to canonical ALPHA content words so pure tokenization noise (money/number splits,
    hyphen splits day-to-day, contraction splits we've/we 've) does NOT count as a mismatch — only
    real content-word differences survive. Steps: split hyphens/slashes, merge contraction suffixes
    into the prior token, drop punctuation + all numbers/money/ordinals + number-words."""
    flat = []
    for w in words:
        for part in re.split(r"[-/]", w.strip().lower()):
            flat.append(part)
    out = []
    for t in flat:
        if t.startswith("'") and t.lstrip("'") in ("s", "ll", "re", "ve", "t", "d", "m"):
            if out: out[-1] = out[-1] + t.replace("'", "")
            continue
        t = re.sub(r"[^a-z0-9']", "", t).replace("'", "")
        if not t: continue
        if re.fullmatch(r"\$?\d[\d.,]*(k|m|b|st|nd|rd|th)?", t): continue   # 20, $20m, 3rd...
        if t in NUMWORD: continue
        out.append(t)
    return out

def cc_words(ass):
    txt = Path(ass).read_text(encoding="utf-8", errors="ignore")
    w = []
    for ln in txt.splitlines():
        if ln.startswith("Dialogue:") and ",the reference editor," in ln:
            for grp in re.findall(r"\}([^{]+)", ln.split(",", 9)[9]):
                w += [tok for tok in grp.split() if tok.strip()]   # split multi-word style groups on whitespace
    return w

def transcribe(clip):
    wav = tempfile.mktemp(suffix=".wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", clip, "-ac", "1", "-ar", "16000", wav], capture_output=True)
    base = tempfile.mktemp()
    model = whisper_model()
    exe = whisper_cli()
    if not exe or not model.exists():
        # Optional backend. Returning empty lets the gate SKIP rather than fail a clip
        # over a tool the user was never required to install.
        print("[caption_sync_gate] whisper.cpp not available - skipping", file=sys.stderr)
        return []
    subprocess.run([exe, "-m", str(model), "-f", wav, "-oj", "-of", base, "-ml", "1"], capture_output=True)
    j = base + ".json"
    if not os.path.exists(j): return []
    return [s.get("text", "") for s in json.loads(open(j).read()).get("transcription", [])]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cc", required=True)
    ap.add_argument("--clip")
    ap.add_argument("--audio-words")
    ap.add_argument("--max-mismatch", type=int, default=1)
    a = ap.parse_args()
    cap = canon(cc_words(a.cc))
    if a.audio_words and Path(a.audio_words).exists():
        aw = json.loads(Path(a.audio_words).read_text())
        aud_raw = [s.get("text", "") for s in aw.get("transcription", aw.get("words", []))] if isinstance(aw, dict) else aw
    elif a.clip:
        aud_raw = transcribe(a.clip)
    else:
        print("need --clip or --audio-words"); return 2
    aud = canon(aud_raw)
    print(f"=== caption_sync_gate ({Path(a.cc).name}) ===")
    print(f"  caption {len(cap)} content-words · audio {len(aud)} content-words")
    caponly, audonly = [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, cap, aud).get_opcodes():
        if op in ("delete", "replace"): caponly += cap[i1:i2]
        if op in ("insert", "replace"): audonly += aud[j1:j2]
    # a 'replace' of equal-length differing only by ASR mishear (roles/goals) is softer; report all but count content
    real = [w for w in caponly if len(w) > 2] + [w for w in audonly if len(w) > 2]
    if caponly: print(f"  ✗ ON SCREEN but NOT in audio: {caponly}")
    if audonly: print(f"  ✗ IN AUDIO but NOT captioned: {audonly}")
    if not caponly and not audonly:
        print("  ✓ captions match the delivered audio")
    n = len(set(caponly) | set(audonly))
    if n > a.max_mismatch:
        print(f"\n  BLOCK — {n} caption/audio mismatches. Regenerate captions from the FINAL cut audio "
              f"(force-align), and ear-verify any ASR mishears (e.g. roles/goals).")
        return 1
    print(f"\n  PASS ({n} mismatch(es) within tolerance {a.max_mismatch})")
    return 0

if __name__ == "__main__":
    sys.exit(main())
