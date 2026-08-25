# FFmpeg recipes

## Detect black frames

```bash
ffmpeg -hide_banner -nostats -i INPUT \
  -vf "blackdetect=d=0.4:pix_th=0.10" \
  -an -f null - 2>&1 | grep blackdetect
```

- `d=0.4` — gap must be ≥0.4 seconds to register.
- `pix_th=0.10` — pixels below 10% luminance count as black.
- Output lines look like: `[blackdetect @ 0x...] black_start:23.48 black_end:24.91 black_duration:1.43`

## Detect silence

```bash
ffmpeg -hide_banner -nostats -i INPUT \
  -af "silencedetect=n=-35dB:d=0.4" \
  -vn -f null - 2>&1 | grep silence
```

- `n=-35dB` — below -35dB counts as silent. Loosen to -40 if your clips have noise floors.
- Output lines: `[silencedetect @ 0x...] silence_start: 23.48` and `silence_end: 24.91 | silence_duration: 1.43`

## Trim and burn captions in one pass

```bash
ffmpeg -y -i INPUT \
  -ss START -to END \
  -vf "subtitles=SUBS.ass:fontsdir=FONTS_DIR" \
  -c:v the hardware encoder chosen by fast_encode -b:v 14M -tag:v avc1 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  OUTPUT
```

- `-ss` before `-i` is faster but less accurate; after `-i` is frame-accurate. We put it after because clip boundaries need to be precise.
- `fontsdir` makes FFmpeg load the fonts in that folder without them needing to be installed system-wide — critical for making the skill shippable.
- `-c:v the hardware encoder chosen by fast_encode` — Brand fast-render standard: hardware H.264 (NVENC / Quick Sync / AMF), ~4x faster than libx264 and off-CPU. `-b:v` is the resolution-aware bitrate (14M for 1080p, 50M for 4K); Python callers should use `_shared/fast_encode.py` `encoder_args()` so it's picked automatically. libx264 `-crf` is reserved for archival masters (`tier='master'`).
- `-movflags +faststart` — moves MOOV atom to the front so the file streams/seeks instantly when uploaded.

## Fontconfig gotcha

On macOS, if you see `[Parsed_subtitles ... Fontconfig error: Cannot load default config file`, FFmpeg is trying to resolve fonts via the system. Two fixes:

1. Point it at our bundled fonts with `fontsdir=` in the subtitles filter (preferred).
2. Set `FC_CONFIG_FILE` to a minimal fontconfig XML that just points at our fonts folder.

The `burn_captions.py` script sets `fontsdir` automatically.

## Probe video resolution

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,duration \
  -of json INPUT
```
