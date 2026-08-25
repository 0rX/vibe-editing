# /highlight MODE C — fill your queue with finished shorts

Auto-fill your social queue with finished **9:16 short videos**: scan a folder of shorts,
filter them, and queue each one to **your** YouTube channel on a schedule via the Buffer
API. Buffer needs a public media URL, so each clip is uploaded to **your own** storage
bucket first. Never-post-twice, daily cap, dry-run.

Nothing here is tied to any account. You bring three things — a Buffer token, your channel
id, and a storage bucket — all read from env or `~/.config/`. No ids, urls, or keys are
hardcoded.

## What you connect (one-time)

1. **Buffer account + API token**
   - Create a token: https://publish.buffer.com/settings/api
   - `export BUFFER_TOKEN='your-token'` (or `echo … > ~/.config/buffer/api_key`)

2. **Your channel id** (the YouTube channel/profile you post to)
   - `python fill_queue.py discover` → copy the id of the channel you want
   - `export BUFFER_CHANNEL_ID='<id>'` (or `echo … > ~/.config/buffer/channel_id`)

3. **Storage for public URLs** (Supabase Storage, or any S3-style public bucket)
   - `export SUPABASE_URL='https://YOUR-PROJECT.supabase.co'`
   - `export SUPABASE_KEY='your-service-role-key'`
   - `export SUPABASE_BUCKET='your-bucket'` (default: `vibe-media`)
   - …or write each to `~/.config/supabase/{url,service_key,bucket}`
   - Skip uploads entirely for a pre-hosted clip with `--video-url`.

Install deps: `pip install -r requirements.txt` (plus `ffmpeg` on PATH for `ffprobe`).

## Usage

```bash
python fill_queue.py discover                 # find YOUR channel id
python fill_queue.py slots                    # preview scheduling slots
python fill_queue.py fill --dry-run           # preview what WOULD be queued
python fill_queue.py fill --total 10          # queue up to 10 shorts
python fill_queue.py fill --dir ~/clips       # scan a specific folder
python fill_queue.py fill --order name        # filename order instead of newest-first
python fill_queue.py fill --video-url URL --total 1   # queue a pre-hosted clip
```

## How it picks clips

- **Source:** a local folder of `*.mp4` (also `.mov/.webm/.m4v`).
  Order: `--dir`, else `VIBE_SHORTS_DIR`, else the kit's deliver folder.
- **Filter:** must have an audio stream and be **10–180s** long.
- **Title:** from a sidecar `clip.txt` (or `clip.mp4.txt`) next to the video if present,
  else the cleaned filename. Add hashtags with `export VIBE_HASHTAGS="#shorts #you"`.
- **Never twice:** a JSON ledger (`posted_log.json`) records every clip ever queued;
  uploads are cached in `url_cache.json` so a clip uploads at most once.
- **Daily cap:** `VIBE_BUFFER_DAILY_CAP` (default **10**), tracked in `api_calls.json`
  and printed loudly on every run.

## Files

```
fill_queue.py   ← entry point (discover / slots / fill)
config.py       ← creds + paths (env or ~/.config/) — no hardcoded ids
buffer_api.py   ← Buffer GraphQL client (post creation + channel discovery)
storage.py      ← video -> your bucket -> public URL
captions.py     ← title/description from sidecar .txt or filename
slots.py        ← scheduling slot generator
```
