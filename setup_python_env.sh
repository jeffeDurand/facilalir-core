#!/usr/bin/env bash
# Create and populate a Python virtual environment at the repo root (./.venv).
# Run from the repository root: ./setup_python_env.sh

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ ! -f "requirements.txt" ]]; then
  echo "requirements.txt not found in $ROOT" >&2
  exit 1
fi

if [[ ! -d ".venv" ]]; then
  echo "Creating .venv …"
  python3 -m venv .venv
fi

# shellcheck source=/dev/null
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo ""
echo "Done. Activate with:"
echo "  source .venv/bin/activate"
echo "Or run scripts explicitly (one line at a time):"
echo "  .venv/bin/python export_comic_detection_to_coreml.py --check"
echo "  .venv/bin/python prepare_mlpackage_for_xcode.py --show-default-dest"
echo "  .venv/bin/python prepare_mlpackage_for_xcode.py --show-assets-path"
echo "  # after placing ComicBubbleDetector.mlpackage in assets/:"
echo "  .venv/bin/python prepare_mlpackage_for_xcode.py --from-assets"
