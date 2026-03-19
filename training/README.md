# Train a comic / manga speech-bubble detector (YOLOv8 → Core ML)

This folder holds **example configs** and docs. Large files (images, weights, `runs/`) stay **out of git** (see `.gitignore`).

## 1. Environment

Use a **dedicated venv** (recommended: `.venv-train`) so Ultralytics’ PyTorch version does not fight the slimmer `.venv` used for `coremltools --check`:

```bash
chmod +x setup_train_env.sh   # once
./setup_train_env.sh
source .venv-train/bin/activate
```

If you see `ModuleNotFoundError: huggingface_hub` (or other missing deps), your `.venv-train` was created before `requirements-train.txt` was updated. Reinstall:

```bash
.venv-train/bin/pip install -r requirements-train.txt
```

## 2. Optional credentials (`.env`)

If you use **gated Hugging Face** repos, **Roboflow**, or **W&B**, copy the example env file and fill in only what you need:

```bash
cp .env.example .env
# edit .env — never commit it (it is gitignored)
```

| Variable | When needed |
|----------|-------------|
| `HF_TOKEN` | Private/gated HF datasets, or to avoid anonymous rate limits |
| `ROBOFLOW_API_KEY` | Downloading via Roboflow API |
| `WANDB_API_KEY` | Only if you enable Weights & Biases in Ultralytics |

**You do not need any API keys** if you work entirely from local files (images + labels on disk).

Public **pretrained** weights on Hugging Face also work **without a token** (unless a repo is gated). Set `HF_TOKEN` only if needed.

## 3. Pretrained models (download — no training)

Curated presets (see each **model card** for license / citation before shipping an app):

| `--preset` | Source | Notes |
|------------|--------|--------|
| `comic-speech-yolov8-s` | [mnemic/comic_speechbubble_yolov8](https://huggingface.co/mnemic/comic_speechbubble_yolov8) | **Good default** — classic YOLOv8, `imgsz` 640 |
| `comic-speech-yolov8-m` | same | Larger / slower |
| `manga-bubble-yolo-n` | [Kiuyha/Manga-Bubble-YOLO](https://huggingface.co/Kiuyha/Manga-Bubble-YOLO) | YOLO26-n; use `imgsz` **1280** for small bubbles; needs **recent** `ultralytics` |
| `manga-bubble-yolo-s` | same | YOLO26-s variant |

**List presets:**

```bash
python3 train_comic_bubble_yolo.py list-pretrained
```

**Download `.pt` only** (copy saved under `training/pretrained/`, gitignored):

```bash
python3 train_comic_bubble_yolo.py download-pretrained --preset comic-speech-yolov8-s
```

**Download + export Core ML in one step** (writes `assets/ComicBubbleDetector.mlpackage` by default):

```bash
python3 train_comic_bubble_yolo.py export-pretrained-coreml --preset comic-speech-yolov8-s
python3 prepare_mlpackage_for_xcode.py --from-assets
```

Manga presets (YOLO26): if load/export fails, upgrade `ultralytics` (`pip install -U ultralytics`) or use a `comic-speech-yolov8-*` preset instead.

## 4. Get a dataset (your responsibility)

Examples people use for **bubble / text region** detection (verify **license** and **citation** yourself):

- Community **YOLO** / **Roboflow** “comic” or “speech bubble” datasets (export as YOLOv8).
- Research projects such as **Manga-Bubble-YOLO** / manga bubble detectors on [Hugging Face](https://huggingface.co/) — clone or `snapshot_download` if the repo provides images + labels in YOLO layout (or convert).

Put data under `training/data/` (see `training/data/README.md`) and create a **`data.yaml`** (start from `bubble_dataset.example.yaml`).

## 5. Train

```bash
python3 train_comic_bubble_yolo.py doctor
python3 train_comic_bubble_yolo.py train \
  --data training/bubble_dataset.example.yaml \
  --model yolov8n.pt \
  --epochs 50 \
  --imgsz 640
```

Weights default to `./runs/detect/train/weights/best.pt` (or `train2`, … if you repeat).

## 6. Export Core ML (for the iOS app)

```bash
python3 train_comic_bubble_yolo.py export-coreml \
  --weights runs/detect/train/weights/best.pt \
  --out assets/ComicBubbleDetector.mlpackage
```

Then install into the Xcode tree:

```bash
# from repo root, can use main .venv or system python:
python3 prepare_mlpackage_for_xcode.py --from-assets
```

(If you passed `--out` directly to `assets/`, you may only need to rebuild Xcode — `prepare_mlpackage_for_xcode.py` also copies into `Facilalir/.../Resources/`.)

## 7. Hugging Face download helper

If a repo ships files you need (configs, weights, sample data):

```bash
python3 train_comic_bubble_yolo.py download-hf --repo org/name --out training/data/hf_name
```

Uses `HF_TOKEN` from `.env` when set.

## Legal

You are responsible for **dataset licenses**, **model licenses**, and **attribution**. This repo does not redistribute third-party weights or datasets.
