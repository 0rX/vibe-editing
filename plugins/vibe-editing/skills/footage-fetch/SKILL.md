---
name: footage-fetch
description: Download raw footage FAST from Google Drive (folders OR single-file links) into properly-scaffolded per-download projects, with integrity verification. Use whenever Operator drops a Google Drive link and wants the footage pulled to disk — "download this footage", "grab this drive folder", "pull these clips", "add this to the download queue", "digest this footage", "ingest this". Uses rclone (never the browser): parallel multi-thread transfers, by-ID single-file downloads, detached so the session can't kill them, disk-space guards, per-download project scaffolding, and MD5 verification. NOT for transcribing (that's long-form-ingest) or editing.
---

# Footage Fetch — fast, verified Google Drive downloads

THE way to get footage off Google Drive onto this Mac. Crushes the browser and survives long unattended pulls. Built from the 2026-06-06 Speaker ingest session — see [[reference_rclone_drive_downloads_2026-06-05]].

## 🔑 Golden rules (do not skip)
1. **rclone, NEVER the browser.** Browser = one slow stream + a server-side zip that fails on 100GB+. rclone = parallel multi-thread, resumable, verifiable. ~40–50 MB/s sustained on Wi-Fi; 100 GB ≈ ~45 min.
2. **EVERY separate download = its OWN project.** One `/folders/` link = ONE project (it's one shoot). EACH `/file/d/` link = its OWN project. NEVER lump separate downloads into one project. Scaffold via `new_project.py <brand> <slug>` → `%USERPROFILE%/Videos/vibe-editing/<brand>/<YYYY-MM-DD>_<slug>/00_SOURCE/` (default brand `speaker`). (Learned the hard way — don't dump single-file pulls into a folder's project.)
3. **Check disk FIRST.** Get total size, compare to `free_gb()` (winenv) free, flag BEFORE pulling. Never fill the boot drive. 400GB+ won't fit internal → route to an external SSD.
4. **Run DETACHED for anything big.** The harness reaps `run_in_background` tasks ~every 20–25 min mid-download. Launch with `nohup … & disown` so they survive the session.
5. **Always MD5-verify** after (`rclone check … --one-way`). rclone stamps finished files with the SOURCE mtime — a *today* mtime on a "done" file means it's a browser copy or an unfinished partial.

## Setup (one-time, already done)
rclone v1.74+ (brew). Remote `gdrive:` = **read-only** Google OAuth (`scope=drive.readonly`), token in `~/.config/rclone/rclone.conf`. Re-auth if it ever breaks: `rclone config reconnect gdrive:`.

## Get the ID from a link
- Folder: `https://drive.google.com/drive/folders/<FOLDER_ID>`
- File:   `https://drive.google.com/file/d/<FILE_ID>/view`

## Before committing — reachability, size, disk
```bash
# reachable?  "[]" (empty array, exit 0) = rclone can fetch it.  An error = not shared to this account.
rclone lsjson gdrive: --drive-root-folder-id=<ID>
rclone size  gdrive: --drive-root-folder-id=<FOLDER_ID>            # folder size
python -c "import sys; sys.path.insert(0,'lib/_shared'); from winenv import free_gb; print(f'{free_gb():.0f} GiB free')"              # free space
```
Single-file size: the folder-by-ID trick returns `[]` for files, so use the **Google Drive MCP `get_file_metadata`** (if that account can see it), otherwise read the total off the first `--stats` line once the download starts.

## Download a FOLDER (whole folder → one project)
```bash
python ${CLAUDE_PLUGIN_ROOT}/vault/scripts/new_project.py <brand> <slug>
DEST=%USERPROFILE%/Videos/vibe-editing/<brand>/<YYYY-MM-DD>_<slug>/00_SOURCE
nohup rclone copy gdrive: "$DEST" --drive-root-folder-id=<FOLDER_ID> \
  --transfers=8 --multi-thread-streams=8 --multi-thread-cutoff=100M \
  --drive-acknowledge-abuse --stats=10s --stats-one-line -v \
  --log-file=/tmp/fetch_<slug>.log >/dev/null 2>&1 & disown
```

## Download a SINGLE FILE (→ its own project) — by ID
```bash
python ${CLAUDE_PLUGIN_ROOT}/vault/scripts/new_project.py <brand> <slug>
DEST=%USERPROFILE%/Videos/vibe-editing/<brand>/<YYYY-MM-DD>_<slug>/00_SOURCE
nohup rclone backend copyid gdrive: <FILE_ID> "$DEST/" --multi-thread-streams=8 \
  --drive-acknowledge-abuse --stats=10s --stats-one-line -v \
  --log-file=/tmp/fetch_<slug>.log >/dev/null 2>&1 & disown
```
`rclone backend copyid` is THE way to fetch a single shared file by ID — `--drive-root-folder-id` only works for folders.

## One-shot helper (preferred)
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/footage-fetch/scripts/gdrive_pull.py <brand> <drive-url-or-id> [slug]
```
Detects folder vs file, runs reachability + disk checks, scaffolds **its own** project, downloads, MD5-verifies, and (for unknown-name single files) renames the project folder to the real filename. Logs to `/tmp/fetch_<slug>.log`. For big pulls, run IT detached: `python …/gdrive_pull.py … --detach`. For a queue of files, call it once per file (each gets its own project) and chain with a `free_gb()` (winenv) guard between them.

## Verify (always)
```bash
rclone check gdrive: "$DEST" --drive-root-folder-id=<ID> --one-way      # 0 differences = good
```

## Monitor detached downloads
```bash
grep -a ETA /tmp/fetch_<slug>.log | tail -1          # live speed / ETA
ps -Ao command | grep "[r]clone"                      # what's REALLY running
```
⚠️ Never put a file ID inline in a `pgrep`/`grep` status command — it matches your OWN command and gives false "running" hits. Use the `[r]clone` bracket trick (the `[r]` keeps grep from matching itself).

## Hard-won gotchas
- **Flags in a shell var don't word-split under zsh** → rclone sees one giant `--transfers` arg and dies silently (exit 0, downloads nothing). INLINE the flags, or only rely on `$VAR` splitting inside a real `#!/bin/bash` script.
- **`--drive-acknowledge-abuse`** is required or Google blocks big-file downloads ("can't scan for viruses").
- **Resume**: re-running `rclone copy` skips already-complete files (size + source-mtime); multi-thread `.partial` files restart from 0, not mid-file; rclone cleans its partials on success/SIGTERM.
- **Google throttles single-file pulls** — even a fast pipe tops out ~hundreds of Mbps per file; `--multi-thread-streams` mitigates.
- **Trash** — files "deleted" in Finder still occupy disk until the Trash is emptied (`du -sh ~/.Trash`).
- **Finder tags** — never move/delete a tagged item without per-item OK; read tags via xattr (Spotlight is off). 🟣 purple = frozen.
- **Disk full mid-queue** — guard with `free_gb()` (winenv) before each file; skip (don't overflow) and report what was skipped.

## Default flow when Operator drops a link
1. Default the brand to `speaker` (only use another Brand brand — creator / creator / creator — when the footage is clearly that brand). 2. Reachability + size + disk check (flag if it won't fit). 3. Scaffold its OWN project (folder→one project; each file→its own). 4. Detached download. 5. MD5-verify. 6. Report; rename any `Clip-<id>` project to the real filename. 7. After meaningful skill/vault changes, `backup_brain.sh`.
