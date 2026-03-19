#!/usr/bin/env bash
# Virtualenv for YOLO training / Core ML export (.venv-train).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ ! -f "requirements-train.txt" ]]; then
  echo "requirements-train.txt not found in $ROOT" >&2
  exit 1
fi

if [[ ! -d ".venv-train" ]]; then
  echo "Creating .venv-train …"
  python3 -m venv .venv-train
fi

# shellcheck source=/dev/null
source .venv-train/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-train.txt

echo ""
echo "Done. Examples (one line at a time):"
echo "  source .venv-train/bin/activate"
echo "  python3 train_comic_bubble_yolo.py doctor"
echo "  python3 train_comic_bubble_yolo.py list-pretrained"
echo "  python3 train_comic_bubble_yolo.py export-pretrained-coreml --preset comic-speech-yolov8-s"
echo "  python3 train_comic_bubble_yolo.py train --data training/bubble_dataset.example.yaml --epochs 30"
echo "  python3 train_comic_bubble_yolo.py export-coreml --weights runs/detect/train/weights/best.pt"
echo ""
echo "Optional: cp .env.example .env   # then add HF_TOKEN etc. if needed"
