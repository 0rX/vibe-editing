#!/usr/bin/env python
"""new_project.py - scaffold a dated job folder (00_SOURCE / 10_WORK / 20_DELIVER).

    new_project.py <group> <slug> [YYYY-MM-DD]  ->  <OUTPUT>/<group>/<date>_<slug>/
    new_project.py <slug>                       ->  <OUTPUT>/_PROJECTS/<date>_<slug>/

"group" is any top-level folder used to organise jobs (client / channel / brand).
Output root comes from winenv.output_root() (%USERPROFILE%\\Videos\\vibe-editing);
override with VIBE_OUTPUT_ROOT, or OUTPUT_DIR for compatibility with the old bash script.

Prints the created directory on stdout (and a status line on stderr) so callers can
capture the path, exactly like the bash version it replaces.
"""
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib" / "_shared"))
from winenv import output_root  # noqa: E402


def resolve_root() -> Path:
    # OUTPUT_DIR is honoured for parity with the bash script's interface.
    override = os.environ.get("OUTPUT_DIR")
    return Path(override) if override else output_root()


def match_existing_group(root: Path, group: str) -> str:
    """Reuse an existing folder that differs only by case.

    Windows filesystems are case-insensitive, so "Speaker" and "speaker" are the same
    directory; this keeps the behaviour explicit rather than accidental, and matches what
    the bash version did with `find -iname` on macOS.
    """
    if (root / group).is_dir():
        return group
    try:
        for child in root.iterdir():
            if child.is_dir() and child.name.lower() == group.lower():
                return child.name
    except OSError:
        pass
    return group


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(f"usage: {Path(__file__).name} <group> <slug> [YYYY-MM-DD]", file=sys.stderr)
        return 1

    root = resolve_root()
    if len(args) == 1:
        group, slug, date_str = "", args[0], date.today().isoformat()
        base = root / "_PROJECTS"
    else:
        group, slug = args[0], args[1]
        date_str = args[2] if len(args) > 2 else date.today().isoformat()
        group = match_existing_group(root, group)
        base = root / group

    job = f"{date_str}_{slug}"
    target = base / job

    if target.is_dir():
        print(f"exists: {target}", file=sys.stderr)
        print(target)
        return 0

    for sub in ("00_SOURCE", "10_WORK", "20_DELIVER"):
        (target / sub).mkdir(parents=True, exist_ok=True)
    (target / "_project.md").write_text(
        f"# {job}\n\n- group: {group or '_PROJECTS'}\n- created: {date_str}\n- status: intake\n",
        encoding="utf-8")

    print(f"created: {target}", file=sys.stderr)
    print(target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
