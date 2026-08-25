# Install — Vibe Editing (Windows)

> ## Just want it working?
>
> ```powershell
> winget install --id Git.Git      # then open a NEW terminal
> git clone https://github.com/0rX/vibe-editing.git
> cd vibe-editing
> powershell -ExecutionPolicy Bypass -File .\setup.ps1
> ```
>
> That installs Python, ffmpeg, yt-dlp and every Python dependency, then runs the health
> check. **The rest of this file is the manual path** — read it only if setup fails or you
> want to know what it did.
>
> **Two things that bite everyone on a fresh Windows:**
> - `-ExecutionPolicy Bypass` is required. Windows refuses to run `.ps1` files by default
>   (*"running scripts is disabled on this system"*). This flag applies to that one command
>   and changes nothing permanently.
> - **Open a new terminal after installing anything.** PATH does not refresh in a window
>   that is already open, so freshly-installed tools look missing until you do.

## Prerequisites

| Need | Get it | Notes |
|---|---|---|
| Windows 10 (1809+) or 11 | — | `winget` ships with it |
| Claude Code + a paid plan | claude.com/claude-code | Pro or Max |
| Git | `winget install --id Git.Git` | to clone the repo |
| Python 3.10+ | `setup.ps1` installs it | see the warning below |

> ⚠️ **Do not rely on typing `python` on a fresh Windows.** There is a stub in `WindowsApps`
> that opens the Microsoft Store instead of running Python. It looks installed to
> `Get-Command` and to `Test-Path`, but `python -m venv` silently does nothing. `setup.ps1`
> detects and skips that stub. If you install Python yourself, use
> `winget install --id Python.Python.3.12`.

A portable Claude Code plugin. It does **not** need to live in `~/.claude/skills/` — it runs
from wherever Claude Code installs it.

## 1. Add the marketplace + install the plugin

This folder is both the marketplace and the plugin. In Claude Code:

```text
/plugin marketplace add /absolute/path/to/vibe-editing-starter
/plugin install vibe-editing@vibe-editing-marketplace
```

Verify it loaded:

```text
/plugin        # shows vibe-editing as enabled
/edit          # the orchestrator entry point
```

(To iterate without the marketplace step, drop `plugins/vibe-editing/` into a skills directory;
it carries its own `.claude-plugin/plugin.json` and self-loads. Run `/reload-plugins` after edits.)

## 2. System tools

winget package IDs are exact strings — `winget install --id ffmpeg` does **not** work.

| Tool | Command | Why |
|---|---|---|
| **FFmpeg** | `winget install --id Gyan.FFmpeg` | **REQUIRED.** Every render shells out to `ffmpeg`/`ffprobe`. Use this full build — it includes **libass**, which burns the captions. A minimal ffmpeg cannot, and `doctor.py` checks specifically for it. |
| **yt-dlp** | `winget install --id yt-dlp.yt-dlp` | URL ingest |
| **tesseract** | `winget install --id UB-Mannheim.TesseractOCR` | caption OCR for the audit gates |
| **rclone** | `winget install --id Rclone.Rclone` then `rclone config` | cloud-drive ingest (`footage-fetch`) |
| **Node** | `winget install --id OpenJS.NodeJS.LTS` | optional — only the `promo` skill |

Montreal Forced Aligner (`script-cut`, optional) has its own installer:
`powershell -ExecutionPolicy Bypass -File .\plugins\vibe-editing\skills\script-cut\scripts\setup_toolchain.ps1`

## 3. Python dependencies (3.10+)

```powershell
cd plugins\vibe-editing
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Call `.venv\Scripts\python.exe` directly rather than activating — it works the same from any
shell and avoids the execution-policy problem `activate.ps1` runs into.

Heavy / optional (only if you use these paths):

```powershell
.venv\Scripts\python.exe -m pip install faster-whisper   # local transcription, no API key
.venv\Scripts\python.exe -m pip install torch            # diarization / alignment
.venv\Scripts\python.exe -m pip install mediapipe        # face-mesh reframe path
```

### Set PYTHONUTF8=1

```powershell
[Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', 'User')
```

Not cosmetic. Windows Python defaults stdout to cp1252, which cannot encode the arrows and
check marks this codebase prints in 82 files — printing one raises `UnicodeEncodeError` and
kills the script mid-render. `setup.ps1` sets this for you.

## 4. API keys — bring your own

Edit `plugins/vibe-editing/config/keys.env`. **Nothing ships with a key.** The file auto-loads
at runtime; paste yours once:

```bash
GROQ_API_KEY=          # free tier at console.groq.com — optional, falls back to local whisper
ANTHROPIC_API_KEY=     # optional — captions fall back to the `claude` CLI if installed
ELEVENLABS_API_KEY=    # optional — audio cleanup / SFX / voice isolation
```

## 5. Your assets

| Asset | Default | How to change |
|---|---|---|
| Caption font | free **Montserrat** bundled in `skills/caption-clips/fonts/` | swap your own — see `fonts_README.md` |
| Music library | none bundled | put royalty-free tracks in a folder, set `VIBE_MUSIC=C:\Users\you\Music\vibe` |
| Editorial taste | placeholder SOPs / prompts | fill in `skills/*/references/` and `skills/*/prompts/` |

## 6. Paths — how the plugin finds its own files

Everything resolves from **`${CLAUDE_PLUGIN_ROOT}`** (the install dir). Python scripts also
self-locate by walking up to the `.claude-plugin/` marker, and honor `VIBE_PIPELINE_ROOT` /
`CLAUDE_PLUGIN_ROOT`. **No absolute path or env var is required for scripts.**

## 7. Run it

`/edit` accepts a **local file, a URL, or a cloud-drive link**, then runs the spine
(ingest → scaffold → source-intel → detect → transcribe → mine → pick → validate → cut → QC →
render → re-QC → audit → deliver). Or drive the render engine directly once a project +
`manifest.json` exist:

```powershell
$py = ".\plugins\vibe-editing\.venv\Scripts\python.exe"
& $py .\plugins\vibe-editing\skills\render\engine.py <project_dir>          # build
& $py .\plugins\vibe-editing\skills\render\engine.py <project_dir> --bump   # revise (changed stages only)
```

## 8. First run

Test one short clip end-to-end and confirm: ffmpeg + libass present, your keys pasted (or local
whisper installed), a font in `fonts/`, and a music folder set. After that, batches just work.

## 9. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `running scripts is disabled on this system` | Windows blocks `.ps1` by default | Run it as `powershell -ExecutionPolicy Bypass -File .\setup.ps1` |
| `doctor.py` says a tool is MISSING right after you installed it | PATH does not refresh in an open terminal | Close it, open a new one, re-run. `setup.ps1` refreshes PATH itself, so this only hits manual installs |
| The Microsoft Store opens instead of Python | You invoked the `WindowsApps` stub | Use `plugins\vibe-editing\.venv\Scripts\python.exe`, or install real Python: `winget install --id Python.Python.3.12` |
| `UnicodeEncodeError: 'charmap' codec can't encode character` | Console is cp1252, not UTF-8 | `[Environment]::SetEnvironmentVariable('PYTHONUTF8','1','User')`, then open a new terminal |
| `winget: No package found matching input criteria` | Wrong package ID | IDs are exact — see the table in §2. `winget install --id ffmpeg` is not valid; `Gyan.FFmpeg` is |
| Captions never appear on the render | ffmpeg built without libass | `winget install --id Gyan.FFmpeg` (the full build). `doctor.py` reports this specifically |
| Renders are very slow and pin every core | No hardware encoder found, using libx264 | Check the `video encoder` line in `doctor.py`. Software encoding is the expected fallback when no NVIDIA/Intel/AMD encoder is usable |
| Transcription takes longer than everything else | Running local whisper on CPU | Put a free `GROQ_API_KEY` in `config/keys.env` — roughly 10x faster |
| `rclone` errors on a Drive link | Remote not configured | `rclone config` and create a remote **named `gdrive`** |

Re-check readiness at any time:

```powershell
.\plugins\vibe-editing\.venv\Scripts\python.exe .\plugins\vibe-editing\doctor.py
```
