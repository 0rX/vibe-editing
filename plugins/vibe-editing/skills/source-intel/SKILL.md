---
name: source-intel
description: >
  Footage intelligence agent. Analyzes raw source footage BEFORE any editing begins.
  Produces a structured report: face positions/sizes, camera angles, scene changes,
  audio quality, speaker count, movement patterns. Feeds into edit step 1 (DETECT)
  and informs every downstream decision (reframe zoom, caption height, mic routing,
  filter requirements). Run this ONCE per source file at the start of every project.
---

# source-intel — know your footage before you touch it

> Run at edit step 0.5, after scaffold, before transcribe.
> Output: `10_WORK/source_intel.json` — every downstream step reads this.

## What it produces

```json
{
  "source": "00_SOURCE/video.mp4",
  "duration_s": 1847.3,
  "resolution": "3840x2160",
  "fps": 29.97,
  "codec": "h264",

  "faces": {
    "count": 2,
    "primary": {
      "avg_x_pct": 0.52,
      "avg_y_pct": 0.35,
      "avg_size_pct": 0.08,
      "movement_range_x_pct": 0.15,
      "movement_range_y_pct": 0.04,
      "classification": "tight"
    },
    "secondary": {
      "avg_x_pct": 0.28,
      "avg_y_pct": 0.38,
      "avg_size_pct": 0.05,
      "classification": "medium"
    },
    "classifications": "tight = face>5% | medium = 2-5% | wide = 0.5-2% | extreme_wide = <0.5%"
  },

  "scenes": {
    "count": 14,
    "avg_duration_s": 131.9,
    "changes_at_s": [0, 45.2, 89.1, ...],
    "is_multicam": true,
    "dominant_angles": ["tight_host", "tight_guest", "wide_two_shot"]
  },

  "audio": {
    "channels": 2,
    "mean_volume_db": -22.4,
    "max_volume_db": -3.1,
    "noise_floor_db": -48.2,
    "has_hum_60hz": false,
    "has_clipping": false,
    "speech_ratio": 0.74,
    "silence_ratio": 0.26,
    "quality": "clean"
  },

  "recommendations": {
    "reframe_preset": "stage",
    "reframe_zoom": 1.6,
    "caption_height": 0.50,
    "needs_notch_filter": false,
    "needs_denoise": false,
    "mic_routing": "mix_both",
    "notes": ["Face is 8% of frame — default zoom is fine", "2 speakers detected — use dual-color captions"]
  }
}
```

## How to run

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/source-intel/scripts/analyze.py \
    --source 00_SOURCE/video.mp4 \
    --out 10_WORK/source_intel.json
```

Optional flags:
- `--sample-interval 10` — extract a frame every N seconds (default: 10)
- `--audio-only` — skip video analysis, just probe audio
- `--faces-only` — skip audio analysis, just detect faces

## What downstream steps use it for

| Step | Reads from source_intel | Decision |
|---|---|---|
| 1 DETECT | `faces.count`, `scenes.is_multicam` | Speaker count + camera count |
| 4PRE-b FRAMING | `faces.primary.avg_size_pct` | Reframe zoom level |
| 6a MIC ROUTING | `audio.channels`, `recommendations.mic_routing` | Mix vs switch |
| 8 RENDER | `recommendations.reframe_preset`, `caption_height` | Preset + positioning |
| Pre-transcribe | `audio.has_hum_60hz`, `audio.noise_floor_db` | Apply notch filter first |

## Face classification thresholds

| Classification | Face area % of frame | Typical content | Reframe zoom |
|---|---|---|---|
| tight | >5% | Close-up, webcam, chest-up | 1.2–1.6 |
| medium | 2–5% | Seated interview, desk | 1.6–2.0 |
| wide | 0.5–2% | Standing stage, full body | 2.0–2.5 |
| extreme_wide | <0.5% | Auditorium, far stage | 2.5–3.0 (quality degrades) |

## Scene change detection

Uses ffmpeg scene filter. A multicam shoot typically has 10+ scene changes per 10 minutes
with consistent alternating patterns (A→B→A→B = two-camera setup). A single-cam shoot
has 0 scene changes (or very few from zoom adjustments).

The `dominant_angles` field classifies each scene segment by face position and size:
- `tight_host` — primary face, tight framing
- `tight_guest` — secondary face, tight framing
- `wide_two_shot` — both faces visible, wider framing
- `broll` — no faces detected (cutaway footage)

## Audio quality assessment

| Quality | Condition |
|---|---|
| clean | noise floor < -40dB, no hum, no clipping |
| needs_filter | 60Hz hum detected (harmonics at 120/180/240Hz) |
| needs_denoise | noise floor > -35dB |
| clipping | max volume > -0.5dB |
| poor | multiple issues — flag to user before proceeding |
