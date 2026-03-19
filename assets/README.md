# Assets (repo root)

Drop **local, large, or machine-specific** files here so paths stay predictable. Nothing in this folder is required to build the app.

To **train** a bubble YOLO and export Core ML into this folder, see [`../training/README.md`](../training/README.md) and run `train_comic_bubble_yolo.py export-coreml --out assets/ComicBubbleDetector.mlpackage`.

## Core ML bubble model (optional)

### You only have a `.pt` file (e.g. under `training/pretrained/`)?

`prepare_mlpackage_for_xcode.py` copies **`.mlpackage`** only, not PyTorch weights. Convert first with **`.venv-train`**:

```bash
source .venv-train/bin/activate
python3 train_comic_bubble_yolo.py export-coreml \
  --weights training/pretrained/comic_speechbubble_s_yolov8_v1.pt \
  --out assets/ComicBubbleDetector.mlpackage
python3 prepare_mlpackage_for_xcode.py --from-assets
```

Or in one shot from Hugging Face: `export-pretrained-coreml --preset comic-speech-yolov8-s` (see [`training/README.md`](../training/README.md)).

### You already have a `.mlpackage`

1. Export your bubble-detection model as **`ComicBubbleDetector.mlpackage`** (Core ML package bundle).
2. Place it here:

   `assets/ComicBubbleDetector.mlpackage`

3. Install into the Xcode app tree:

   ```bash
   .venv/bin/python prepare_mlpackage_for_xcode.py --from-assets
   ```

   Or equivalently:

   ```bash
   .venv/bin/python prepare_mlpackage_for_xcode.py --source assets/ComicBubbleDetector.mlpackage
   ```

`.mlpackage` bundles are **gitignored** here so they are not committed by mistake (they are often large). This `README.md` is tracked.

## Other files

You can add other subfolders (e.g. reference images) as needed; prefer documenting them in this file if others should know about them.
