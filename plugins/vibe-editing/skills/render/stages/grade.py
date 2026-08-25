"""grade — apply a color grade filter chain. Default = locked Speaker/SF grade.

Config:
    {
      "filter": "eq=contrast=1.06:saturation=1.08:gamma=0.98,colorbalance=..."
    }
"""
from __future__ import annotations
# ── winenv bootstrap: locate the plugin's shared lib ──
import os as _os2, sys as _sys2
_d2 = _os2.path.dirname(_os2.path.abspath(__file__))
while _d2 != _os2.path.dirname(_d2) and not _os2.path.isdir(_os2.path.join(_d2, '.claude-plugin')):
    _d2 = _os2.path.dirname(_d2)
_sys2.path.insert(0, _os2.path.join(_d2, 'lib', '_shared'))
from fast_encode import encoder_args_bitrate  # noqa: E402
# ── end winenv bootstrap ──

from _util import run as ff

VERSION = "1.0.0"

DEFAULT_GRADE = "eq=contrast=1.06:saturation=1.08:gamma=0.98,colorbalance=rm=0.015:gm=-0.022:bm=-0.035"


def run(work_dir, config, inputs, inputs_meta, project, manifest, out_path):
    prior = inputs[list(inputs.keys())[-1]]  # last upstream output
    filt = config.get("filter", DEFAULT_GRADE)
    ff(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", prior,
        "-vf", filt,
        *encoder_args_bitrate("20M"),
        "-c:a", "copy", "-movflags", "+faststart", str(out_path)])

    upstream_meta = inputs_meta.get(list(inputs_meta.keys())[-1], {}) if inputs_meta else {}
    return {"out": str(out_path), "meta": {
        "filter": filt,
        "fps": upstream_meta.get("fps"),
        "total_duration_s": upstream_meta.get("total_duration_s"),
        "segments": upstream_meta.get("segments"),
    }}
