#!/usr/bin/env python3
"""
Train / export a YOLO-style bubble detector to Core ML for Facilalir.

Full setup: see training/README.md and .env.example (optional API keys).

Pretrained (Hugging Face, no training):
  python3 train_comic_bubble_yolo.py list-pretrained
  python3 train_comic_bubble_yolo.py download-pretrained --preset comic-speech-yolov8-s
  python3 train_comic_bubble_yolo.py export-pretrained-coreml --preset comic-speech-yolov8-s
  python3 prepare_mlpackage_for_xcode.py --from-assets

Train your own:
  python3 train_comic_bubble_yolo.py train --data training/bubble_dataset.example.yaml --epochs 50
  python3 train_comic_bubble_yolo.py export-coreml --weights runs/detect/train/weights/best.pt
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# Curated public Hugging Face checkpoints (verify license on each model card before shipping an app).
PRETRAINED_MODELS: dict[str, dict] = {
    "comic-speech-yolov8-s": {
        "repo_id": "mnemic/comic_speechbubble_yolov8",
        "filename": "comic_speechbubble_s_yolov8_v1.pt",
        "description": "Comic speech bubbles (YOLOv8 small, ~22MB). Good default for Core ML export.",
        "default_export_imgsz": 640,
        "hf_url": "https://huggingface.co/mnemic/comic_speechbubble_yolov8",
    },
    "comic-speech-yolov8-m": {
        "repo_id": "mnemic/comic_speechbubble_yolov8",
        "filename": "comic_speechbubble_m_yolov8_v1.pt",
        "description": "Comic speech bubbles (YOLOv8 medium, ~50MB). Heavier / may be slower on device.",
        "default_export_imgsz": 640,
        "hf_url": "https://huggingface.co/mnemic/comic_speechbubble_yolov8",
    },
    "manga-bubble-yolo-n": {
        "repo_id": "Kiuyha/Manga-Bubble-YOLO",
        "filename": "weights/yolo26n.pt",
        "description": "Manga bubbles (YOLO26-n). Use imgsz 1280 for small bubbles; needs recent ultralytics.",
        "default_export_imgsz": 1280,
        "hf_url": "https://huggingface.co/Kiuyha/Manga-Bubble-YOLO",
    },
    "manga-bubble-yolo-s": {
        "repo_id": "Kiuyha/Manga-Bubble-YOLO",
        "filename": "weights/yolo26s.pt",
        "description": "Manga bubbles (YOLO26-s). Larger variant; imgsz 1280 recommended.",
        "default_export_imgsz": 1280,
        "hf_url": "https://huggingface.co/Kiuyha/Manga-Bubble-YOLO",
    },
}


def _load_dotenv() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        print(
            "Note: python-dotenv not installed; skipping .env. Install with: pip install python-dotenv",
            file=sys.stderr,
        )
        return
    load_dotenv(env_path)


def _import_hf_hub_download():
    """Lazy import with a clear message if .venv-train is missing huggingface_hub."""
    try:
        from huggingface_hub import hf_hub_download

        return hf_hub_download
    except ImportError:
        print(
            "Missing package: huggingface_hub\n\n"
            "Install it into the same Python you are using (e.g. .venv-train):\n"
            f"  {sys.executable} -m pip install -r requirements-train.txt\n"
            "or re-run from the repo root:\n"
            "  ./setup_train_env.sh\n",
            file=sys.stderr,
        )
        raise SystemExit(1) from None


def _hf_download_file(repo_id: str, filename: str) -> Path:
    hf_hub_download = _import_hf_hub_download()
    token = os.environ.get("HF_TOKEN")
    path = hf_hub_download(repo_id=repo_id, filename=filename, token=token)
    return Path(path).resolve()


def _export_coreml_bundle(
    weights: str | Path,
    out: Path,
    imgsz: int,
    *,
    nms: bool,
) -> int:
    from ultralytics import YOLO

    out = out.expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    w = Path(weights)
    if not w.is_file():
        print(f"Weights not found: {w}", file=sys.stderr)
        return 1

    model = YOLO(str(w))
    exported = model.export(
        format="coreml",
        imgsz=imgsz,
        nms=nms,
        half=False,
    )
    exported_path = Path(exported).resolve()
    if not exported_path.exists():
        print(f"Export failed — expected output missing: {exported_path}", file=sys.stderr)
        return 1

    if out.exists():
        if out.is_dir():
            shutil.rmtree(out)
        else:
            out.unlink()
    if exported_path.is_dir():
        shutil.copytree(exported_path, out)
    else:
        shutil.copy2(exported_path, out)

    print(f"Core ML bundle ready:\n  {out}")
    print("\nThen:")
    print(f"  python3 prepare_mlpackage_for_xcode.py --source {out}")
    print("  # or if you used default assets path:")
    print("  python3 prepare_mlpackage_for_xcode.py --from-assets")
    return 0


def cmd_doctor(_args: argparse.Namespace) -> int:
    print("Repo root:", REPO_ROOT)
    print(".env present:", (REPO_ROOT / ".env").is_file())
    if (REPO_ROOT / ".env").is_file():
        print("  (HF_TOKEN set:", bool(os.environ.get("HF_TOKEN")), ")")

    try:
        import torch

        print("torch:", torch.__version__)
        print("MPS (Apple GPU) available:", torch.backends.mps.is_available())
    except ImportError:
        print("torch: not installed (use requirements-train.txt)")

    try:
        import ultralytics

        print("ultralytics:", ultralytics.__version__)
    except ImportError:
        print("ultralytics: not installed — run ./setup_train_env.sh")

    try:
        import huggingface_hub

        print("huggingface_hub:", huggingface_hub.__version__)
    except ImportError:
        print("huggingface_hub: not installed (optional; for download-hf)")

    return 0


def cmd_list_pretrained(_args: argparse.Namespace) -> int:
    print("Available --preset values (public HF weights; check each model card for license):\n")
    for preset, meta in PRETRAINED_MODELS.items():
        print(f"  {preset}")
        print(textwrap.indent(meta["description"], "    "))
        print(f"    {meta['repo_id']}  /  {meta['filename']}")
        print(f"    default export imgsz: {meta['default_export_imgsz']}")
        print(f"    {meta['hf_url']}\n")
    print("Commands:")
    print("  download-pretrained --preset <name>   # save .pt under training/pretrained/")
    print("  export-pretrained-coreml --preset <name>  # HF cache → Core ML → default assets path")
    return 0


def cmd_download_pretrained(args: argparse.Namespace) -> int:
    meta = PRETRAINED_MODELS[args.preset]
    path = _hf_download_file(meta["repo_id"], meta["filename"])

    if args.out:
        dest = Path(args.out).expanduser().resolve()
    else:
        dest_dir = REPO_ROOT / "training" / "pretrained"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / Path(meta["filename"]).name

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)
    print(f"Saved weights:\n  {dest}")
    print("\nExport to Core ML:")
    print(f"  python3 {Path(__file__).name} export-coreml --weights {dest}")
    return 0


def cmd_export_pretrained(args: argparse.Namespace) -> int:
    meta = PRETRAINED_MODELS[args.preset]
    print(f"Downloading {meta['repo_id']} / {meta['filename']} …")
    pt_path = _hf_download_file(meta["repo_id"], meta["filename"])
    imgsz = args.imgsz if args.imgsz is not None else meta["default_export_imgsz"]
    out = Path(args.out).expanduser().resolve()
    return _export_coreml_bundle(pt_path, out, imgsz, nms=args.nms)


def cmd_train(args: argparse.Namespace) -> int:
    from ultralytics import YOLO

    data = Path(args.data).expanduser().resolve()
    if not data.is_file():
        print(f"data yaml not found: {data}", file=sys.stderr)
        return 1

    model = YOLO(args.model)
    model.train(
        data=str(data),
        epochs=args.epochs,
        imgsz=args.imgsz,
        project=args.project,
        name=args.name,
        device=args.device,
        exist_ok=args.exist_ok,
    )
    print("\nNext: export Core ML from best weights, e.g.")
    print(f"  python3 {Path(__file__).name} export-coreml \\")
    print(f"    --weights {Path(args.project) / args.name / 'weights' / 'best.pt'}")
    return 0


def cmd_export_coreml(args: argparse.Namespace) -> int:
    return _export_coreml_bundle(
        Path(args.weights).expanduser().resolve(),
        Path(args.out).expanduser().resolve(),
        args.imgsz,
        nms=args.nms,
    )


def cmd_download_hf(args: argparse.Namespace) -> int:
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        _import_hf_hub_download()

    out = Path(args.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("HF_TOKEN")
    snapshot_download(
        repo_id=args.repo,
        local_dir=str(out),
        repo_type=args.repo_type,
        revision=args.revision,
        token=token,
    )
    print(f"Downloaded to:\n  {out}")
    if not token:
        print("\nTip: For private/gated repos set HF_TOKEN in .env (see .env.example).")
    return 0


def main() -> int:
    _load_dotenv()

    parser = argparse.ArgumentParser(
        description="Train or download pretrained bubble YOLO and export Core ML for Facilalir.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    preset_help = "One of: " + ", ".join(sorted(PRETRAINED_MODELS))

    p_doc = sub.add_parser("doctor", help="Print versions and environment hints.")
    p_doc.set_defaults(func=cmd_doctor)

    p_list = sub.add_parser("list-pretrained", help="List Hugging Face presets you can download.")
    p_list.set_defaults(func=cmd_list_pretrained)

    p_dl = sub.add_parser(
        "download-pretrained",
        help="Download a curated .pt from Hugging Face (saves copy under training/pretrained/).",
    )
    p_dl.add_argument("--preset", required=True, choices=sorted(PRETRAINED_MODELS), metavar="PRESET", help=preset_help)
    p_dl.add_argument(
        "--out",
        default=None,
        help="Destination .pt path (default: training/pretrained/<original filename>)",
    )
    p_dl.set_defaults(func=cmd_download_pretrained)

    p_ep = sub.add_parser(
        "export-pretrained-coreml",
        help="Download a preset .pt from HF and export Core ML in one step (no local training).",
    )
    p_ep.add_argument("--preset", required=True, choices=sorted(PRETRAINED_MODELS), metavar="PRESET", help=preset_help)
    p_ep.add_argument(
        "--out",
        default=str(REPO_ROOT / "assets" / "ComicBubbleDetector.mlpackage"),
        help="Output .mlpackage path (default: assets/ComicBubbleDetector.mlpackage)",
    )
    p_ep.add_argument(
        "--imgsz",
        type=int,
        default=None,
        help="Export image size (default: preset-specific, e.g. 640 or 1280)",
    )
    p_ep.add_argument("--nms", action="store_true", default=True, help="Embed NMS (default on)")
    p_ep.add_argument("--no-nms", dest="nms", action="store_false")
    p_ep.set_defaults(func=cmd_export_pretrained)

    p_tr = sub.add_parser("train", help="Run Ultralytics training.")
    p_tr.add_argument("--data", required=True, help="Path to data.yaml")
    p_tr.add_argument("--model", default="yolov8n.pt", help="Base checkpoint (default yolov8n.pt)")
    p_tr.add_argument("--epochs", type=int, default=50)
    p_tr.add_argument("--imgsz", type=int, default=640)
    p_tr.add_argument("--project", default="runs/detect", help="Ultralytics project dir")
    p_tr.add_argument("--name", default="train", help="Run name under project")
    p_tr.add_argument("--device", default=None, help="e.g. mps, cpu, 0 — default: auto")
    p_tr.add_argument(
        "--exist-ok",
        dest="exist_ok",
        action="store_true",
        help="Overwrite existing run name",
    )
    p_tr.set_defaults(func=cmd_train)

    p_ex = sub.add_parser("export-coreml", help="Export a local .pt to Core ML .mlpackage")
    p_ex.add_argument("--weights", required=True, help="Path to best.pt (or last.pt)")
    p_ex.add_argument(
        "--out",
        default=str(REPO_ROOT / "assets" / "ComicBubbleDetector.mlpackage"),
        help="Output .mlpackage bundle path",
    )
    p_ex.add_argument("--imgsz", type=int, default=640)
    p_ex.add_argument("--nms", action="store_true", default=True, help="Embed NMS (default on)")
    p_ex.add_argument("--no-nms", dest="nms", action="store_false")
    p_ex.set_defaults(func=cmd_export_coreml)

    p_hf = sub.add_parser("download-hf", help="snapshot_download any Hugging Face repo (dataset/model)")
    p_hf.add_argument("--repo", required=True, help="e.g. org/model-name")
    p_hf.add_argument("--out", required=True, help="Local directory")
    p_hf.add_argument("--repo-type", default="model", choices=("model", "dataset", "space"))
    p_hf.add_argument("--revision", default=None)
    p_hf.set_defaults(func=cmd_download_hf)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
