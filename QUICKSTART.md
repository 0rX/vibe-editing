# Quickstart — 3 steps

```
1.  powershell -ExecutionPolicy Bypass -File .\setup.ps1
    # installs Python/ffmpeg/deps, then runs a health check
2.  (optional) paste a free Groq key in plugins/vibe-editing/config/keys.env
3.  In Claude Code:   /edit <your youtube link>
    or in a terminal: .\bin\vibe-editing.ps1 "<your youtube link>"
```

Finished clips land in the project's `20_DELIVER/` folder — already run through the
6-gate quality audit.

- **No Groq key?** Skip step 2 and `pip install faster-whisper` for free local transcription.
- **Check readiness any time:** `python plugins/vibe-editing/doctor.py`
- **Make it yours** (font, caption style, hook taste): see `Vibe-Editing-Playbook.pdf` → "Your turn".
