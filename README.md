# facilalir-core

This repository is **[facilalir-core](https://github.com/jeffeDurand/facilalir-core)** — the **root** project (Python tooling, docs, `.gitignore`). The **Xcode iOS / iPadOS / visionOS app** lives in the **`Facilalir/` [git submodule](https://github.com/jeffeDurand/facilalir)** ([`jeffeDurand/facilalir`](https://github.com/jeffeDurand/facilalir)).

### Clone

```bash
git clone --recurse-submodules https://github.com/jeffeDurand/facilalir-core.git
cd facilalir-core
```

If you already cloned without submodules:

```bash
git submodule update --init --recursive
```

---

**Facilalir** is an offline-first iOS / iPadOS / visionOS app for reading comics and cartoons with strong accessibility: vision-impairment **profiles** (color palettes, dyslexia-friendly font, icon style), on-device **OCR** via Apple Vision, and an always-visible **“100% offline”** message.

## Project layout

- **App** (submodule): [Facilalir/Facilalir.xcodeproj](Facilalir/Facilalir.xcodeproj) — SwiftUI, MVVM, `Info-additions.plist` merged with generated keys (no ATS exceptions; no networking code).
- **Python tooling** (repo root): `export_comic_detection_to_coreml.py`, `prepare_mlpackage_for_xcode.py`, `requirements.txt` — optional Core ML bubble-detection pipeline. **Use the root virtual env** (`.venv/`); see below.
- **Fonts**: OpenDyslexic (SIL-OFL) under `Facilalir/Facilalir/Resources/Fonts/`.

## Python environment (repo root)

Tooling is meant to run in a **virtual environment at the repository root** (`.venv/`), not the system Python.

One-time setup (from this directory):

```bash
chmod +x setup_python_env.sh   # first time only, if needed
./setup_python_env.sh
```

Then either activate the env for your shell session:

```bash
source .venv/bin/activate
python export_comic_detection_to_coreml.py --check
```

…or call the interpreter explicitly (no activation):

```bash
.venv/bin/python prepare_mlpackage_for_xcode.py --source /path/to/ComicBubbleDetector.mlpackage
```

`.venv/` is listed in `.gitignore` and is not committed.

## Optional bubble model

After exporting `ComicBubbleDetector.mlpackage`, run (with the venv as above):

```bash
.venv/bin/python prepare_mlpackage_for_xcode.py --source /path/to/ComicBubbleDetector.mlpackage
```

Rebuild the app; the Reader screen enables **Speech bubble detection** when the model is present.

## Build

Open the Xcode project and build for **iPhone**, **iPad**, or **Apple Vision** (supported destinations are configured in the target).
