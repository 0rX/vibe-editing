"""Vibe Editing — Windows platform layer. THE single place OS-specific behaviour lives.

This kit was originally macOS-only. Every POSIX assumption it made (`/tmp`, `flock`,
`python3`, `~/.zshrc`, `df -g`, `~/Downloads`) is replaced by one helper here, so the
rest of the codebase stays plain portable Python and there is exactly one file to audit
when something behaves oddly on a new machine.

Usage — the shared lib is already on sys.path via the bootstrap block every script carries:

    from winenv import PY, work_dir, output_root, free_gb, read_key

    subprocess.run([PY, str(SCRIPTS / "burn_captions.py"), ...])   # never "python3"
    scratch = work_dir("tighten_scan")                            # never Path("/tmp/...")
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
if VIBE_SHARED not in _sys.path:
    _sys.path.insert(0, VIBE_SHARED)
# ── end bootstrap ──
import os
import shutil
import sys
import time
from pathlib import Path

# ── the interpreter ───────────────────────────────────────────────────────────
# On Windows `python3` is a Microsoft Store *stub* that opens the Store instead of
# running anything, so a bare "python3" in a subprocess call is always a bug here.
# sys.executable is also what keeps child processes inside the project's .venv.
PY = sys.executable


# ── scratch space ─────────────────────────────────────────────────────────────
def _local_appdata() -> Path:
    p = os.environ.get("LOCALAPPDATA")
    if p:
        return Path(p)
    return Path.home() / "AppData" / "Local"


def work_root() -> Path:
    """Base scratch directory. Override with VIBE_WORK_DIR."""
    override = os.environ.get("VIBE_WORK_DIR")
    return Path(override) if override else _local_appdata() / "vibe-editing" / "work"


def work_dir(name: str = "") -> Path:
    """A scratch directory, created if missing. Replaces every hardcoded /tmp path.

    Unlike /tmp, Windows does NOT clear this on reboot — call prune_work() to reclaim
    space rather than assuming the OS does it for you.
    """
    p = work_root() / name if name else work_root()
    p.mkdir(parents=True, exist_ok=True)
    return p


def work_file(name: str, *, pid: bool = True) -> Path:
    """A uniquely-named scratch FILE path (not created). `pid=True` keeps concurrent
    runs of the same script from clobbering each other, matching the original
    `/tmp/_foo_{os.getpid()}.png` convention."""
    stem, dot, ext = name.partition(".")
    if pid:
        stem = f"{stem}_{os.getpid()}"
    return work_dir() / (stem + dot + ext)


def prune_work(days: float = 7.0) -> int:
    """Delete scratch files older than `days`. Returns how many were removed.

    Video intermediates are large; without this the scratch dir grows without bound.
    """
    cutoff = time.time() - days * 86400
    removed = 0
    root = work_root()
    if not root.exists():
        return 0
    for p in sorted(root.rglob("*"), key=lambda x: len(x.parts), reverse=True):
        try:
            if p.is_file() and p.stat().st_mtime < cutoff:
                p.unlink()
                removed += 1
            elif p.is_dir() and not any(p.iterdir()):
                p.rmdir()
        except OSError:
            pass  # locked by a running encode — skip it, next prune gets it
    return removed


def tool_dir(name: str = "") -> Path:
    """Persistent install location for an optional toolchain (MFA, whisper.cpp models).

    Deliberately NOT under work_dir(): scratch is prunable by age, and silently deleting a
    multi-gigabyte conda env that took ten minutes to build would be a nasty surprise.
    Keep this in step with the -Root default in skills/script-cut/scripts/setup_toolchain.ps1.
    """
    p = _local_appdata() / "vibe-editing"
    return p / name if name else p


# ── where finished work lands ─────────────────────────────────────────────────
def output_root() -> Path:
    """Project/delivery root. The Mac original scattered these into ~/Downloads;
    on Windows the Videos folder is the honest home for rendered video.
    Override with VIBE_OUTPUT_ROOT."""
    override = os.environ.get("VIBE_OUTPUT_ROOT")
    p = Path(override) if override else Path.home() / "Videos" / "vibe-editing"
    p.mkdir(parents=True, exist_ok=True)
    return p


# ── disk ──────────────────────────────────────────────────────────────────────
def free_gb(path=None) -> float:
    """Free space in GiB. Replaces the BSD-only `df -g` calls.

    Walks up to the nearest existing parent, so it works for a path that is about to
    be created (which is exactly when a disk check is wanted).
    """
    p = Path(path) if path else output_root()
    p = p.resolve()
    while not p.exists() and p != p.parent:
        p = p.parent
    try:
        return shutil.disk_usage(str(p)).free / (1024 ** 3)
    except OSError:
        return 0.0


# ── API keys ──────────────────────────────────────────────────────────────────
def keys_path() -> Path:
    return Path(VIBE_ROOT) / "config" / "keys.env"


def read_key(name: str, default: str = "") -> str:
    """Look up an API key: real environment first, then config/keys.env.

    Replaces the original's habit of grepping ~/.zshrc, which has no Windows analogue.
    Placeholder values ("PASTE...") are treated as unset so doctor.py reports honestly.
    """
    val = os.environ.get(name)
    if val and val.strip():
        return val.strip()
    kf = keys_path()
    if kf.exists():
        try:
            for line in kf.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                if k.strip() == name:
                    v = v.strip().strip('"').strip("'")
                    if v and "PASTE" not in v.upper():
                        return v
        except OSError:
            pass
    return default


def has_key(name: str) -> bool:
    return bool(read_key(name))


# ── ffmpeg ────────────────────────────────────────────────────────────────────
def ffmpeg_bin(name: str = "ffmpeg") -> str:
    """Resolve ffmpeg / ffprobe.

    The Mac original globbed /opt/homebrew/Cellar/ffmpeg-full/*/bin/ to find a build with
    libass. On Windows the winget `Gyan.FFmpeg` full build is on PATH and already has it,
    so PATH is the answer; VIBE_FFMPEG_DIR covers a hand-placed build.

    Returns the bare name as a last resort so the caller's own error handling still runs.
    """
    d = os.environ.get("VIBE_FFMPEG_DIR")
    if d:
        for ext in (".exe", ""):
            cand = Path(d) / (name + ext)
            if cand.exists():
                return str(cand)
    return which(name) or name


FFMPEG_INSTALL_HINT = "ffmpeg not found - run: winget install --id Gyan.FFmpeg"


# ── whisper.cpp (optional offline transcription backend) ──────────────────────
def whisper_model() -> Path:
    """Path to the ggml whisper model.

    The Mac original kept this under ~/.claude-video-vision/models/. Models are large
    binary caches, so on Windows they belong in LOCALAPPDATA alongside the other
    machine-local state. Override with VIBE_WHISPER_MODEL.
    """
    override = os.environ.get("VIBE_WHISPER_MODEL")
    if override:
        return Path(override)
    return tool_dir("models") / "ggml-large-v3.bin"


def whisper_cli():
    """Path to the whisper.cpp executable, or None if it isn't installed.

    The Mac original hardcoded /opt/homebrew/bin/whisper-cli, which obviously cannot
    resolve here. whisper.cpp ships prebuilt Windows binaries; put the folder on PATH or
    point VIBE_WHISPER_CLI at the exe.
    """
    override = os.environ.get("VIBE_WHISPER_CLI")
    if override and Path(override).exists():
        return override
    return which("whisper-cli") or which("whisper")


def whisper_ready() -> bool:
    return bool(whisper_cli()) and whisper_model().exists()


# ── console ───────────────────────────────────────────────────────────────────
def enable_utf8() -> None:
    """Force UTF-8 on stdout/stderr.

    NOT cosmetic — this prevents hard crashes. A stock Windows Python reports
    `sys.stdout.encoding == 'cp1252'`, which cannot represent the arrows, check marks
    and box-drawing characters this codebase prints in 82 files. Printing one raises
    `UnicodeEncodeError: 'charmap' codec can't encode character '\\u2192'` and kills the
    script mid-pipeline. macOS never hit this because its default is UTF-8.

    Called on import (below) so anything reaching the platform layer is protected;
    `setup.ps1` also sets PYTHONUTF8=1 so the files that never import winenv are covered.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            if stream and getattr(stream, "encoding", "").lower() not in ("utf-8", "utf8"):
                stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass  # redirected to a pipe that can't be reconfigured — not worth dying over


def enable_ansi() -> bool:
    """Turn on ANSI colour handling in the Windows console.

    Windows Terminal handles escapes natively; the legacy conhost used by some
    shells does not, and prints raw `\\033[92m` garbage unless VT mode is enabled.
    Returns True if colour should be used.
    """
    if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
        return False
    try:
        import ctypes
        k = ctypes.windll.kernel32
        # -11 = STD_OUTPUT_HANDLE, 0x4 = ENABLE_VIRTUAL_TERMINAL_PROCESSING
        h = k.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if k.GetConsoleMode(h, ctypes.byref(mode)):
            k.SetConsoleMode(h, mode.value | 0x4)
        return True
    except Exception:
        return False


# ── background processes ──────────────────────────────────────────────────────
# Flags for detaching a long download/encode so it survives and stays quiet.
# Replaces the `nohup ... & disown` pattern from the bash scripts.
DETACHED_FLAGS = 0
if os.name == "nt":
    DETACHED_FLAGS = 0x00000008 | 0x08000000  # DETACHED_PROCESS | CREATE_NO_WINDOW


def which(cmd: str):
    """shutil.which, but also finds .exe/.cmd/.bat without the caller spelling it out."""
    found = shutil.which(cmd)
    if found:
        return found
    for ext in (".exe", ".cmd", ".bat"):
        found = shutil.which(cmd + ext)
        if found:
            return found
    return None


# Applied at import: every module that touches the platform layer gets a console that
# can print the characters this codebase already uses. See enable_utf8() for why.
enable_utf8()


if __name__ == "__main__":
    enable_ansi()
    print(f"  interpreter   {PY}")
    print(f"  work dir      {work_dir()}")
    print(f"  output root   {output_root()}")
    print(f"  keys.env      {keys_path()}  {'found' if keys_path().exists() else 'MISSING'}")
    print(f"  free space    {free_gb():.1f} GiB")
    for k in ("GROQ_API_KEY", "ANTHROPIC_API_KEY", "ELEVENLABS_API_KEY"):
        print(f"  {k:<20} {'set' if has_key(k) else '-'}")
