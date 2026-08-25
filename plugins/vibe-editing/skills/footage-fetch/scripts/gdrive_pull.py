#!/usr/bin/env python
"""gdrive_pull.py <client> <drive-url-or-id> [slug]

Download ONE Google Drive folder OR single file into its OWN scaffolded project, verified.
  Folder link -> whole folder into one project.
  File link   -> that file into its own project.

For big pulls run it detached (the wrapper handles the Windows equivalent of
`nohup ... & disown`):
    gdrive_pull.py <client> <url> --detach

Requires rclone with a remote named `gdrive:` already configured (`rclone config`).
Exit codes:  0 ok · 3 not enough disk · 4 project scaffold failed · 5 rclone missing
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]                      # plugins/vibe-editing
sys.path.insert(0, str(ROOT / "lib" / "_shared"))
from winenv import DETACHED_FLAGS, PY, free_gb, output_root, which, work_dir  # noqa: E402

NEW_PROJECT = ROOT / "vault" / "scripts" / "new_project.py"
MIN_FREE_G = 15          # never start a download with less than this free
VIDEO_EXT = (".mp4", ".mov", ".wav", ".mxf", ".mp3")


def parse_target(url: str):
    """Return (type, id) from a Drive URL or a bare id."""
    if "/folders/" in url:
        return "folder", re.sub(r".*/folders/([^/?]+).*", r"\1", url)
    if "/file/d/" in url:
        return "file", re.sub(r".*/file/d/([^/?]+).*", r"\1", url)
    m = re.search(r"[?&]id=([^&]+)", url)
    if m:
        return "file", m.group(1)
    return "file", url       # bare id: copyid is the universal fetch


def folder_size_gb(drive_id: str) -> float:
    r = subprocess.run(["rclone", "size", "gdrive:", f"--drive-root-folder-id={drive_id}",
                        "--json"], capture_output=True, text=True)
    m = re.search(r'"bytes":\s*(\d+)', r.stdout or "")
    return int(m.group(1)) / (1024 ** 3) if m else 0.0


def scaffold(client: str, slug: str) -> Path | None:
    subprocess.run([PY, str(NEW_PROJECT), client, slug],
                   capture_output=True, text=True)
    matches = sorted((output_root() / client).glob(f"*_{slug}"))
    return matches[0] if matches else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("client")
    ap.add_argument("url")
    ap.add_argument("slug", nargs="?", default="")
    ap.add_argument("--detach", action="store_true",
                    help="run the pull in a detached background process and return immediately")
    a = ap.parse_args()

    if not which("rclone"):
        print("[gdrive_pull] ABORT: rclone not installed. "
              "Run: winget install Rclone.Rclone && rclone config")
        return 5

    if a.detach:
        # Windows has no nohup/disown; DETACHED_PROCESS|CREATE_NO_WINDOW is the equivalent.
        cmd = [PY, str(Path(__file__).resolve()), a.client, a.url] + ([a.slug] if a.slug else [])
        log = work_dir("fetch") / f"fetch_{a.slug or 'pull'}.log"
        with open(log, "w", encoding="utf-8") as fh:
            subprocess.Popen(cmd, stdout=fh, stderr=subprocess.STDOUT,
                             creationflags=DETACHED_FLAGS)
        print(f"[gdrive_pull] detached; log: {log}")
        return 0

    kind, drive_id = parse_target(a.url)
    print(f"[gdrive_pull] client={a.client} type={kind} id={drive_id}")

    # ---- disk gate ----
    free = free_gb(output_root())
    print(f"[gdrive_pull] free={free:.0f}G")
    if kind == "folder":
        need = folder_size_gb(drive_id) + 5
        print(f"[gdrive_pull] folder ~{need:.0f}G needed")
        if need > 5 and free < need:
            print(f"[gdrive_pull] ABORT: need ~{need:.0f}G, have {free:.0f}G - "
                  f"free space or use an external drive")
            return 3
    if free < MIN_FREE_G:
        print(f"[gdrive_pull] ABORT: only {free:.0f}G free (<{MIN_FREE_G}G) - free space first")
        return 3

    # ---- slug + its own project ----
    slug = a.slug or (f"Drive-{drive_id[:8]}" if kind == "folder" else f"Clip-{drive_id[:8]}")
    proj = scaffold(a.client, slug)
    if not proj:
        print(f"[gdrive_pull] ABORT: project scaffold failed for {slug}")
        return 4
    dest = proj / "00_SOURCE"
    log = work_dir("fetch") / f"fetch_{slug}.log"
    print(f"[gdrive_pull] project={proj}")

    # ---- download ----
    common = ["--drive-acknowledge-abuse", "--stats=10s", "--stats-one-line", "-v",
              f"--log-file={log}"]
    if kind == "folder":
        cmd = (["rclone", "copy", "gdrive:", str(dest), f"--drive-root-folder-id={drive_id}",
                "--transfers=8", "--multi-thread-streams=8", "--multi-thread-cutoff=100M"]
               + common)
    else:
        cmd = (["rclone", "backend", "copyid", "gdrive:", drive_id, str(dest) + "\\",
                "--multi-thread-streams=8"] + common)
    rc = subprocess.run(cmd).returncode
    print(f"[gdrive_pull] download rc={rc}")

    # ---- rename an auto Clip-<id> project to the real filename ----
    if kind == "file" and slug.startswith("Clip-"):
        real = next((f for f in sorted(dest.iterdir())
                     if f.suffix.lower() in VIDEO_EXT), None) if dest.is_dir() else None
        if real:
            new_proj = proj.with_name(proj.name[: -len(slug)] + real.stem)
            try:
                proj.rename(new_proj)
                proj, dest = new_proj, new_proj / "00_SOURCE"
                print(f"[gdrive_pull] renamed project -> {new_proj.name}")
            except OSError:
                pass

    # ---- verify ----
    if kind == "folder":
        print("[gdrive_pull] MD5 check:")
        r = subprocess.run(["rclone", "check", "gdrive:", str(dest),
                            f"--drive-root-folder-id={drive_id}", "--one-way"],
                           capture_output=True, text=True)
        print("\n".join((r.stderr or r.stdout or "").strip().splitlines()[-2:]))
    else:
        print("[gdrive_pull] landed:")
        for f in sorted(dest.iterdir()) if dest.is_dir() else []:
            print(f"  {f.name}  {f.stat().st_size / 1e6:.1f} MB")

    print(f"[gdrive_pull] DONE {slug} -> {proj}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
