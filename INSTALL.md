# Install — Vibe Editing

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

- **FFmpeg with libass** — REQUIRED. Every render shells out to `ffmpeg`/`ffprobe`; libass burns
  the captions. `winget install --id ffmpeg`
- **tesseract** — caption OCR used by the audit gates. `winget install --id tesseract`
- **yt-dlp** — URL ingest (installed by `requirements.txt`, or `winget install --id yt-dlp`).
- **rclone** — cloud-drive ingest (`footage-fetch`). `winget install --id rclone && rclone config`.
- Optional: **Node + npm** (only the `promo` end-card), **Montreal Forced Aligner** (`script-cut`).

## 3. Python dependencies (3.10+)

```bash
cd plugins/vibe-editing
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
```

Heavy / optional (only if you use these paths):

```bash
pip install faster-whisper   # local transcription, no API key needed
pip install torch            # diarization / alignment
pip install mediapipe        # face-mesh reframe path
```

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
| Music library | none bundled | put royalty-free tracks in a folder, set `VIBE_MUSIC=/your/music` |
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

```bash
python "$CLAUDE_PLUGIN_ROOT/skills/render/engine.py" <project_dir>          # build
python "$CLAUDE_PLUGIN_ROOT/skills/render/engine.py" <project_dir> --bump   # revise (changed stages only)
```

## 8. First run

Test one short clip end-to-end and confirm: ffmpeg + libass present, your keys pasted (or local
whisper installed), a font in `fonts/`, and a music folder set. After that, batches just work.
