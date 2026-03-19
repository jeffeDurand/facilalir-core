#!/usr/bin/env python3
"""
Export a comic / manga speech-bubble detection model to Core ML (.mlpackage).

For an end-to-end path (YOLOv8 train → Core ML → Xcode), use **train_comic_bubble_yolo.py**
with **./setup_train_env.sh** (see `training/README.md`).

If you already downloaded a **`.pt`** to `training/pretrained/` (e.g. `comic_speechbubble_s_yolov8_v1.pt`),
that is **not** Core ML yet — run **`export-coreml`** in `.venv-train`, then **`prepare_mlpackage_for_xcode.py --from-assets`** (see `assets/README.md`).

This file is a shorter reference / `coremltools --check` helper for the **./.venv** env:
run `./setup_python_env.sh`, then `.venv/bin/python export_comic_detection_to_coreml.py`.
The iOS app expects a bundled model named ComicBubbleDetector.mlpackage (or compiled mlmodelc).

Typical sources (you must satisfy each model's license):
  - YOLOv8 family fine-tuned on comic bubbles (e.g. Hugging Face / community repos)
  - Manga-Bubble-YOLO or similar object-detection checkpoints

Steps (high level):
  1. Obtain a trained PyTorch or ONNX detection model that outputs bounding boxes.
  2. Trace / export to a Core ML–compatible graph (coremltools).
  3. Save as ComicBubbleDetector.mlpackage.

Example skeleton using ultralytics (uncomment and adapt paths after you have weights):

    from ultralytics import YOLO
    import coremltools as ct

    model = YOLO("path/to/best.pt")
    # Ultralytics can export Core ML directly in many versions:
    model.export(format="coreml", nms=True, imgsz=640)

Then rename the output bundle to ComicBubbleDetector.mlpackage and run:

    python3 prepare_mlpackage_for_xcode.py

For manual coremltools conversion from PyTorch, see:
  https://apple.github.io/coremltools/

Compute units: after conversion, prefer MLProgram with compute_precision FLOAT16
for a good balance of speed (Metal / Neural Engine) on iPad and visionOS.
"""

from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Comic bubble detector → Core ML (documentation + hook).")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Print whether coremltools is importable.",
    )
    args = parser.parse_args()
    if args.check:
        try:
            import coremltools  # noqa: F401

            print("coremltools OK:", coremltools.__version__)  # type: ignore[name-defined]
        except ImportError:
            print("coremltools not installed. Run: pip install -r requirements.txt", file=sys.stderr)
            return 1
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
