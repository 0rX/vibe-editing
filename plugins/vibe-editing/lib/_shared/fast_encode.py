"""Vibe Editing FAST-RENDER STANDARD — single source of truth for video encoder args.

Windows machines vary enormously in what video hardware they have, so this module probes
the actual ffmpeg build at runtime and picks the best available encoder. NEVER hardcode
`-c:v` anywhere else; call encoder_args() and you get the right thing on every machine.

The ladder, best first:

    h264_nvenc   NVIDIA GPU        — fastest, best quality-per-bit of the hardware options
    h264_qsv     Intel Quick Sync  — on basically every Intel iGPU since Skylake
    h264_amf     AMD GPU           — works, but weakest quality per bit (see BITRATE_MULT)
    libx264      software          — always available, slow, pins every core

Any video skill should call encoder_args() instead of hand-writing '-c:v libx264 ...':

    import sys, os; sys.path.insert(0, VIBE_SHARED)
    from fast_encode import encoder_args
    cmd = [ffmpeg, ..., *encoder_args(width, height, ffmpeg, tier="delivery"), "-c:a","aac", out]

Env overrides (flip behaviour without code edits):
    VIBE_ENCODER=nvenc|qsv|amf|x264   force one encoder everywhere
    VIBE_FAST=0                       alias for VIBE_ENCODER=x264
    VIBE_ENCODER_STRICT=1             fail loudly if the forced encoder is unavailable,
                                      instead of silently falling back to libx264
"""
# ── vibe-editing portable path bootstrap (auto-inserted) ──
import os as _os, sys as _sys
def _acq_root():
    r = _os.environ.get("VIBE_PIPELINE_ROOT") or _os.environ.get("CLAUDE_PLUGIN_ROOT")
    if r and _os.path.isdir(_os.path.join(r, ".claude-plugin")):
        return r
    d = _os.path.dirname(_os.path.abspath(__file__))
    while d != _os.path.dirname(d):
        if _os.path.isdir(_os.path.join(d, ".claude-plugin")):
            return d
        d = _os.path.dirname(d)
    return _os.path.dirname(_os.path.abspath(__file__))
VIBE_ROOT = _acq_root()
VIBE_SHARED = _os.path.join(VIBE_ROOT, "lib", "_shared")
VIBE_SKILLS = _os.path.join(VIBE_ROOT, "skills")
VIBE_VAULT  = _os.path.join(VIBE_ROOT, "vault")
VIBE_ASSETS = _os.environ.get("VIBE_ASSETS") or _os.path.join(VIBE_ROOT, "assets")
if VIBE_SHARED not in _sys.path:
    _sys.path.insert(0, VIBE_SHARED)
# ── end bootstrap ──
import os
import subprocess
from functools import lru_cache

# Preference order. First one the ffmpeg build actually supports wins.
LADDER = ("h264_nvenc", "h264_qsv", "h264_amf")

# Short names accepted by VIBE_ENCODER.
ALIASES = {
    "nvenc": "h264_nvenc", "nvidia": "h264_nvenc", "cuda": "h264_nvenc",
    "qsv": "h264_qsv", "intel": "h264_qsv", "quicksync": "h264_qsv",
    "amf": "h264_amf", "amd": "h264_amf",
    "x264": "libx264", "libx264": "libx264", "sw": "libx264", "software": "libx264",
}

# Hardware encoders are NOT interchangeable at equal bitrate. The Mac original's numbers
# were tuned for VideoToolbox; carrying them over unadjusted would ship visibly worse
# files on AMD. Multipliers are applied to the resolution-aware base bitrate below.
BITRATE_MULT = {
    "h264_nvenc": 1.0,   # roughly at parity with VideoToolbox
    "h264_qsv":   1.15,  # slightly softer, especially on older iGPUs
    "h264_amf":   1.35,  # weakest rate-distortion of the three; needs the headroom
}

# Decode-side hardware acceleration that pairs with each encoder. Used by bench.py.
HWACCEL = {
    "h264_nvenc": "cuda",
    "h264_qsv":   "qsv",
    "h264_amf":   "d3d11va",
    "libx264":    None,
}


@lru_cache(maxsize=8)
def available_encoders(ffmpeg: str = "ffmpeg") -> frozenset:
    """Which of our candidate encoders this ffmpeg build exposes.

    Note this reflects the BUILD, not the hardware — a build can list h264_qsv on a
    machine with no Intel GPU. See detect() for why that is handled separately.
    """
    try:
        out = subprocess.run([ffmpeg, "-hide_banner", "-encoders"],
                             capture_output=True, text=True, timeout=15).stdout
    except Exception:
        return frozenset()
    return frozenset(e for e in (*LADDER, "libx264") if e in out)


@lru_cache(maxsize=8)
def _really_works(encoder: str, ffmpeg: str = "ffmpeg") -> bool:
    """Encode two frames of colour bars to null and see if it actually runs.

    This matters: ffmpeg lists every encoder compiled in, whether or not the machine has
    the silicon or driver for it. Listing h264_nvenc on a laptop with no NVIDIA GPU is
    normal, and using it fails at runtime — halfway through a render, after the pipeline
    has already spent minutes on transcription and cutting. A ~1s probe up front turns a
    late, confusing failure into an early, correct choice.
    """
    try:
        r = subprocess.run(
            [ffmpeg, "-hide_banner", "-loglevel", "error",
             "-f", "lavfi", "-i", "testsrc=size=320x240:rate=30",
             "-frames:v", "2", "-c:v", encoder, "-f", "null", "-"],
            capture_output=True, text=True, timeout=60)
        return r.returncode == 0
    except Exception:
        return False


@lru_cache(maxsize=8)
def detect(ffmpeg: str = "ffmpeg") -> str:
    """The best encoder that this machine can actually run. Cached."""
    have = available_encoders(ffmpeg)
    for enc in LADDER:
        if enc in have and _really_works(enc, ffmpeg):
            return enc
    return "libx264"


def _forced() -> str:
    """Resolve VIBE_ENCODER / VIBE_FAST to a concrete encoder name, or "" if unset."""
    if os.environ.get("VIBE_FAST") == "0":
        return "libx264"
    raw = os.environ.get("VIBE_ENCODER", "").strip().lower()
    if not raw:
        return ""
    return ALIASES.get(raw, raw)


def _bitrate_for(width: int, height: int) -> int:
    """Resolution-aware VBR target in Mbps. Generous on purpose — most of these are
    intermediates that get re-encoded downstream, so we protect against generational loss."""
    px = int(width) * int(height)
    if px >= 7_000_000:   # 4K (2160x3840 / 3840x2160)
        return 50
    if px >= 3_000_000:   # ~1440
        return 24
    if px >= 1_500_000:   # 1080x1920 / 1920x1080
        return 14
    return 8


@lru_cache(maxsize=64)
def probe_size(path: str, ffmpeg: str = "ffmpeg") -> tuple[int, int]:
    """Return (width, height) of the first video stream in path, or (1080, 1920) as a
    sensible 9:16 short-form fallback if probing fails. Cached per path."""
    # Derive ffprobe from the BASENAME only. A global str-replace would corrupt a parent
    # dir like ".../ffmpeg-full/.../bin/ffmpeg" into a bogus ".../ffprobe-full/...",
    # silently breaking the probe -> falling back to 1080p bitrate even for 4K sources.
    _b = os.path.basename(ffmpeg)
    if "ffmpeg" in _b:
        ffprobe = os.path.join(os.path.dirname(ffmpeg), _b.replace("ffmpeg", "ffprobe"))
    else:
        ffprobe = "ffprobe"
    try:
        out = subprocess.run([ffprobe, "-v", "error", "-select_streams", "v:0",
                              "-show_entries", "stream=width,height",
                              "-of", "csv=s=x:p=0", path],
                             capture_output=True, text=True, timeout=15).stdout.strip()
        w, h = out.split("x")[:2]
        return int(w), int(h)
    except Exception:
        return (1080, 1920)


def encoder_args_for(input_path: str, ffmpeg: str = "ffmpeg", *, tier="delivery",
                     crf=18, bitrate=None):
    """encoder_args() but auto-probe width/height from input_path. Convenience for callers
    that don't already know the output dimensions (most common case)."""
    w, h = probe_size(input_path, ffmpeg)
    return encoder_args(w, h, ffmpeg, tier=tier, crf=crf, bitrate=bitrate)


def _quality_args(encoder: str, br_mbps: int) -> list:
    """Per-encoder tuning. Each vendor spells its rate control differently."""
    br = f"{br_mbps}M"
    if encoder == "h264_nvenc":
        # p4 = balanced preset; vbr with a maxrate ceiling keeps peaks sane.
        return ["-c:v", "h264_nvenc", "-preset", "p4", "-rc", "vbr",
                "-b:v", br, "-maxrate", f"{int(br_mbps * 1.5)}M",
                "-tag:v", "avc1", "-pix_fmt", "yuv420p"]
    if encoder == "h264_qsv":
        return ["-c:v", "h264_qsv", "-preset", "medium", "-b:v", br,
                "-maxrate", f"{int(br_mbps * 1.5)}M",
                "-tag:v", "avc1", "-pix_fmt", "yuv420p"]
    if encoder == "h264_amf":
        return ["-c:v", "h264_amf", "-quality", "balanced", "-rc", "vbr_peak",
                "-b:v", br, "-maxrate", f"{int(br_mbps * 1.5)}M",
                "-tag:v", "avc1", "-pix_fmt", "yuv420p"]
    return []


def encoder_args(width, height, ffmpeg, *, tier="delivery", crf=18, bitrate=None):
    """ffmpeg video-codec args for an output.

    tier: 'delivery' | 'intermediate' | 'proxy'  -> best available hardware encoder
          'master'                                -> libx264 (slow, max quality-per-bit)

    Honors VIBE_ENCODER / VIBE_FAST. Falls back to libx264 whenever the preferred encoder
    is unavailable, unless VIBE_ENCODER_STRICT=1, in which case an explicitly forced but
    unusable encoder raises instead of quietly producing a slow software render.
    """
    force = _forced()
    strict = os.environ.get("VIBE_ENCODER_STRICT") == "1"

    if force == "libx264" or (tier == "master" and not force):
        encoder = "libx264"
    elif force:
        if _really_works(force, ffmpeg):
            encoder = force
        elif strict:
            have = sorted(available_encoders(ffmpeg))
            raise RuntimeError(
                f"VIBE_ENCODER={force} is not usable with this ffmpeg/hardware. "
                f"Build exposes: {have or 'nothing recognised'}. "
                f"Unset VIBE_ENCODER_STRICT to fall back to libx264.")
        else:
            encoder = "libx264"
    else:
        encoder = detect(ffmpeg)

    if encoder == "libx264":
        preset = "slow" if tier == "master" else "medium"
        return ["-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p"]

    if bitrate is not None:
        # Caller-supplied override, e.g. "20M" from a legacy call site. Honour the number
        # but still scale it for the encoder's rate-distortion behaviour.
        base = int(str(bitrate).rstrip("Mm") or _bitrate_for(width, height))
    else:
        base = _bitrate_for(width, height)
    br_mbps = max(1, round(base * BITRATE_MULT.get(encoder, 1.0)))
    return _quality_args(encoder, br_mbps)


def encoder_args_bitrate(bitrate, ffmpeg: str = "ffmpeg", *, tier="delivery", crf=18):
    """Encoder args at an explicitly chosen bitrate.

    For call sites that already hand-tuned a number for their particular stage (the
    render stages each pick their own: 25M for the cut, 14M for the mix, and so on).
    The dimensions only ever feed the default bitrate table, which an explicit bitrate
    replaces, so there is nothing meaningful to pass for them here.
    """
    return encoder_args(1920, 1080, ffmpeg, tier=tier, crf=crf, bitrate=bitrate)


def describe(ffmpeg: str = "ffmpeg") -> str:
    """One-line human summary for doctor.py and logs."""
    names = {"h264_nvenc": "NVIDIA NVENC", "h264_qsv": "Intel Quick Sync",
             "h264_amf": "AMD AMF", "libx264": "software (libx264)"}
    force = _forced()
    have = sorted(available_encoders(ffmpeg))
    if force and force != "libx264" and not _really_works(force, ffmpeg):
        # Say so plainly rather than reporting the fallback as if it were the choice.
        chosen, suffix = detect(ffmpeg), f"  [VIBE_ENCODER={force} UNAVAILABLE, fell back]"
    elif force:
        chosen, suffix = force, "  [forced via VIBE_ENCODER]"
    else:
        chosen, suffix = detect(ffmpeg), ""
    return f"{names.get(chosen, chosen)}{suffix}   build offers: {', '.join(have) or 'none detected'}"


if __name__ == "__main__":
    import sys
    ff = sys.argv[1] if len(sys.argv) > 1 else "ffmpeg"
    print(f"  ffmpeg        {ff}")
    print(f"  encoder       {describe(ff)}")
    for w, h, t in ((1080, 1920, "delivery"), (2160, 3840, "delivery"), (1080, 1920, "master")):
        try:
            args = " ".join(encoder_args(w, h, ff, tier=t))
        except RuntimeError as e:
            args = f"ERROR: {e}"
        print(f"  {w}x{h} {t:<12} {args}")
