#!/usr/bin/env bash
# Step 1 dev runner — hotkey + capture only.
# Run from the repository root; equivalent to: python -m src.main
set -euo pipefail
cd "$(dirname "$0")/.."
exec python -m src.main
