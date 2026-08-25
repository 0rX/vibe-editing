# Windows port — what changed and why

This fork of [maddexritter-rgb/vibe-editing](https://github.com/maddexritter-rgb/vibe-editing)
(MIT) makes the kit run on Windows. Upstream targets macOS on Apple Silicon exclusively and has
had no commits since 2026-06-29.

The port is **Windows-only by choice** — the macOS branches were removed rather than kept behind
platform checks, so this fork does not merge back upstream.

## The platform layer

All OS-specific behaviour lives in one file: **`plugins/vibe-editing/lib/_shared/winenv.py`**.
When something behaves oddly on a new machine, that is the file to read.

| Helper | Replaces |
|---|---|
| `PY` | the literal `"python3"` (a Microsoft Store stub on Windows) |
| `work_dir()` / `work_file()` | hardcoded `/tmp/...` |
| `tool_dir()` | persistent installs for optional toolchains (MFA, whisper models) |
| `output_root()` | `~/Downloads` defaults |
| `free_gb()` | the BSD-only `df -g` |
| `read_key()` | scraping `~/.zshrc` for API keys |
| `ffmpeg_bin()` | globbing `/opt/homebrew/Cellar/ffmpeg-full/*/bin/` |
| `whisper_model()` / `whisper_cli()` | `~/.claude-video-vision/models/` + `/opt/homebrew/bin/whisper-cli` |
| `enable_utf8()` | (new — see below) |

## What was actually broken

Measured across 149 Python files:

| Issue | Files | Sites |
|---|---|---|
| `"python3"` in `subprocess` | 17 | 63 |
| `h264_videotoolbox` hardcoded | 9 | 18 |
| Non-ASCII `print()` on a cp1252 console | 82 | 222 |
| Hardcoded `/tmp` | 7 | 10 |
| `~/.zshrc` key scraping | 11 | 11 |
| Homebrew ffmpeg globs | 14 | 16 |
| `fcntl.flock` encode gate | 1 | 4 |
| Bash scripts | 5 | — |

### Three that deserve explanation

**The console encoding crash.** Windows Python reports `sys.stdout.encoding == 'cp1252'`, which
cannot encode the arrows and check marks this codebase prints in 82 files. Printing one raises
`UnicodeEncodeError` and kills the script mid-pipeline. This was not in the original port plan —
it surfaced while testing, and it would have caused failures deep inside a render with a
confusing traceback. Fixed in two layers: `winenv.enable_utf8()` runs on import, and `setup.ps1`
sets `PYTHONUTF8=1` for the files that never import the platform layer.

**The encode gate.** Upstream uses POSIX `fcntl.flock` on N lockfiles as a machine-wide semaphore
so parallel Claude sessions don't stampede the GPU. Rewritten with `msvcrt.locking`. The failure
mode of a broken lock is silent — every worker runs at once and renders thrash — so
`plugins/vibe-editing/tests/test_encode_gate.py` asserts the invariant directly: 8 concurrent
workers against 3 slots, peak concurrency must never exceed the cap.

**Encoder detection is a runtime probe, not a capability list.** `ffmpeg -encoders` lists
everything the *build* was compiled with, not what the *machine* can run. The winget
`Gyan.FFmpeg` build advertises `h264_nvenc` and `h264_amf` on a laptop with neither. Picking the
first listed encoder would fail mid-render, after transcription and cutting had already spent
minutes. So `fast_encode.detect()` encodes two frames of colour bars to null with each candidate
and takes the first that actually runs — a ~1s probe that turns a late, confusing failure into an
early, correct choice.

## Encoder behaviour

`fast_encode.encoder_args()` is the single source of truth; 25 files already called it upstream
and needed no change. Ladder: `h264_nvenc` → `h264_qsv` → `h264_amf` → `libx264`.

Bitrates are scaled per vendor (`BITRATE_MULT`) rather than reusing VideoToolbox's numbers —
AMD's AMF is meaningfully weaker at the same bitrate, so it gets 1.35x headroom, Quick Sync 1.15x.

Overrides:

```
VIBE_ENCODER=nvenc|qsv|amf|x264   force one encoder
VIBE_FAST=0                       alias for x264
VIBE_ENCODER_STRICT=1             raise instead of silently falling back to libx264
```

`tier="master"` stays pinned to libx264 for archival quality.

**Note:** encoder args feed the render engine's stage content-hashes, so this port invalidates any
pre-existing `10_WORK/stages/` cache. That is correct, not a bug — the stages genuinely changed.

## Scripts converted

| Was | Now |
|---|---|
| `setup.sh` | `setup.ps1` (winget + venv + PATH refresh + health check) |
| `bin/vibe-editing` | `bin/vibe-editing.ps1` |
| `vault/scripts/new_project.sh` | `new_project.py` |
| `skills/footage-fetch/scripts/gdrive_pull.sh` | `gdrive_pull.py` (`--detach` replaces `nohup … & disown`) |
| `skills/horizontal-to-vertical/scripts/reframe.sh` | `reframe.py` |
| `skills/script-cut/scripts/setup_toolchain.sh` | `setup_toolchain.ps1` (micromamba `win-64`) |
| `lib/_shared/encode_args.sh` | deleted — superseded by `fast_encode.py` |

PowerShell files are deliberately **ASCII-only**: Windows PowerShell 5.1 reads a BOM-less UTF-8
script as ANSI, so an em dash renders as mojibake.

## Verifying

```powershell
.\setup.ps1                                          # must end in READY
$py = ".\plugins\vibe-editing\.venv\Scripts\python.exe"
& $py .\plugins\vibe-editing\tests\test_encode_gate.py          # lock invariant
& $py .\plugins\vibe-editing\skills\edit\scripts\_selftest.py   # upstream logic tests
```

## Known issues inherited from upstream

Neither was introduced by this port; both reproduce on upstream `main`.

- **`test_spice_format.py` fails 6 of 171 cases** — number-normalisation rules R4/R5 don't convert
  "one" to "1" in several contexts. `spice_format.py` and its test are untouched by the port. The
  test also exits 0 despite failures, so it does not gate anything.
- **Dangling references to scripts that were never shipped** — `backup_brain.sh`, `sync.sh`,
  `recut_clip.sh`, `render_v27.sh` are cited in the docs but do not exist in the repo.

## Not yet verified

An end-to-end run (a real link through `/edit` to a delivered clip, all audit gates) has not been
done. It needs real footage and, realistically, a Groq API key — local `faster-whisper` on a CPU
makes the transcription step dominate the wall clock. The NVENC and AMF encoder paths cannot be
verified on Intel-only hardware; they are written to fail loudly rather than emit a broken file.
