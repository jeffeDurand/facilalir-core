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
- **YOLO / Core ML** (optional): [`train_comic_bubble_yolo.py`](train_comic_bubble_yolo.py) — **pretrained Hugging Face presets** (`list-pretrained`, `download-pretrained`, `export-pretrained-coreml`) or train your own; see [`training/README.md`](training/README.md). Use [`setup_train_env.sh`](setup_train_env.sh) + [`requirements-train.txt`](requirements-train.txt) and **`.venv-train`**. Optional **`.env`** for `HF_TOKEN` etc. ([`.env.example`](.env.example)).
- **Assets** (repo root): [`assets/`](assets/) — drop optional **`ComicBubbleDetector.mlpackage`** here, then run `prepare_mlpackage_for_xcode.py --from-assets` (see [`assets/README.md`](assets/README.md)). Large bundles are gitignored.
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
.venv/bin/python prepare_mlpackage_for_xcode.py --source ~/Downloads/ComicBubbleDetector.mlpackage
```

`.venv/` is listed in `.gitignore` and is not committed.

## Optional bubble model

After you have a real `ComicBubbleDetector.mlpackage` on disk (from your own export — there is no bundled model in the repo), either:

**A — Repo-root `assets/` folder (recommended)**

```bash
# put the bundle at assets/ComicBubbleDetector.mlpackage, then:
.venv/bin/python prepare_mlpackage_for_xcode.py --from-assets
```

**B — Any path**

```bash
.venv/bin/python prepare_mlpackage_for_xcode.py --source ~/Downloads/ComicBubbleDetector.mlpackage
```

Replace the `--source` path with your actual `.mlpackage` location (the string `/path/to/...` in older docs was only a placeholder — **do not paste it literally**).

To print the default install folder inside the repo (no model file needed):

```bash
.venv/bin/python prepare_mlpackage_for_xcode.py --show-default-dest
```

Rebuild the app; the Reader screen enables **Speech bubble detection** when the model is present.

**`Source not found` for `~/Downloads/ComicBubbleDetector.mlpackage`?** That only works after you actually export a model to that path. The name in the README is an example; nothing is downloaded automatically. Use `ls ~/Downloads/*.mlpackage` to see what you have, or skip bubble detection until you export one (the app’s text recognition still works via Vision).

## Build

Open the Xcode project and build for **iPhone**, **iPad**, or **Apple Vision** (supported destinations are configured in the target).
