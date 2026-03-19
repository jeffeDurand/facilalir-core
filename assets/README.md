# Assets (repo root)

Drop **local, large, or machine-specific** files here so paths stay predictable. Nothing in this folder is required to build the app.

## Core ML bubble model (optional)

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
