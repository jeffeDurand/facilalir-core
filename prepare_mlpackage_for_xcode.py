#!/usr/bin/env python3
"""
Copy a built Core ML package into the Xcode synchronized folder so it ships in the app.

Usage (use repo-root venv — see README / setup_python_env.sh):
  .venv/bin/python prepare_mlpackage_for_xcode.py --source ~/Downloads/ComicBubbleDetector.mlpackage

The Facilalir target loads `ComicBubbleDetector` from the app bundle (see ComicBubbleDetectionService.swift).
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_DEST = REPO_ROOT / "Facilalir" / "Facilalir" / "Resources" / "ComicBubbleDetector.mlpackage"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Path to ComicBubbleDetector.mlpackage (or directory to copy).",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=DEFAULT_DEST,
        help=f"Destination (default: {DEFAULT_DEST})",
    )
    args = parser.parse_args()
    src: Path = args.source.expanduser().resolve()
    dest: Path = args.dest.expanduser().resolve()
    if not src.exists():
        print(f"Source not found: {src}", file=sys.stderr)
        return 1
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    print(f"Copied to {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
