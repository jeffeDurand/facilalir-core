#!/usr/bin/env python3
"""
Copy a built Core ML package into the Xcode synchronized folder so it ships in the app.

Usage (use repo-root venv — see README / setup_python_env.sh):
  .venv/bin/python prepare_mlpackage_for_xcode.py --from-assets
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
# Default drop location at repo root (see assets/README.md)
ASSETS_PACKAGE = REPO_ROOT / "assets" / "ComicBubbleDetector.mlpackage"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Copy ComicBubbleDetector.mlpackage into the Facilalir Xcode tree. "
            "The string /path/to/... in examples is NOT a real path — use your actual file "
            "(type `open .` in Downloads, or drag the folder into Terminal)."
        ),
    )
    parser.add_argument(
        "--show-default-dest",
        action="store_true",
        help="Print the default Xcode Resources path and exit (no --source needed).",
    )
    parser.add_argument(
        "--show-assets-path",
        action="store_true",
        help=f"Print expected repo-root assets path ({ASSETS_PACKAGE.name}) and exit.",
    )
    parser.add_argument(
        "--from-assets",
        action="store_true",
        help=f"Use {ASSETS_PACKAGE.relative_to(REPO_ROOT)} (create assets/ and drop the .mlpackage there).",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Path to your real ComicBubbleDetector.mlpackage (not the literal text /path/to/...).",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=DEFAULT_DEST,
        help=f"Destination (default: {DEFAULT_DEST})",
    )
    args = parser.parse_args()
    dest: Path = args.dest.expanduser().resolve()

    if args.show_default_dest:
        print(dest)
        return 0

    if args.show_assets_path:
        print(ASSETS_PACKAGE.resolve())
        return 0

    if args.from_assets and args.source is not None:
        parser.error("use either --from-assets or --source, not both")

    if args.from_assets:
        src = ASSETS_PACKAGE.resolve()
    elif args.source is not None:
        src = args.source.expanduser().resolve()
    else:
        parser.error(
            "pass --from-assets, or --source PATH, or --show-default-dest / --show-assets-path"
        )
    if not src.exists():
        print(f"Source not found: {src}", file=sys.stderr)
        if "/path/to/" in str(src).replace("\\", "/").lower():
            print(
                "\nTip: `/path/to/...` in the docs is a placeholder — it is not a folder on your Mac. "
                "Use the real path to your .mlpackage, e.g. ~/Downloads/ComicBubbleDetector.mlpackage\n"
                "To see where this script copies into the repo, run:  "
                f"{Path(sys.argv[0]).name} --show-default-dest",
                file=sys.stderr,
            )
        else:
            print(
                "\nThat path does not exist yet. The repo does not ship ComicBubbleDetector.mlpackage — you must "
                "create it yourself (bubble-detection model exported to Core ML), then run this script again.\n"
                "  • Put the bundle in the repo:  mkdir -p assets && cp -R …/ComicBubbleDetector.mlpackage assets/\n"
                "    then:  " + f"{Path(sys.argv[0]).name} --from-assets\n"
                "  • Or check Downloads:  ls ~/Downloads/*.mlpackage 2>/dev/null\n"
                "  • How to export: read the docstring in export_comic_detection_to_coreml.py (YOLO → Core ML, etc.).\n"
                "  • The iOS app still works without it: on-device OCR uses Apple Vision only.\n"
                "  • Install location in repo:  " + f"{Path(sys.argv[0]).name} --show-default-dest",
                file=sys.stderr,
            )
        return 1
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    print(f"Copied to {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
