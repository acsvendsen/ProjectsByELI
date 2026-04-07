#!/bin/bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_SRC="$ROOT_DIR/scripts/com.projectcognition.smartglasses.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.projectcognition.smartglasses.plist"
mkdir -p "$HOME/Library/LaunchAgents"
python3 - <<PY
from pathlib import Path
root = Path(r"$ROOT_DIR")
plist = Path(r"$PLIST_SRC")
text = plist.read_text()
text = text.replace("__ROOT__", str(root))
Path(r"$PLIST_DST").write_text(text)
print("wrote", Path(r"$PLIST_DST"))
PY
chmod +x "$ROOT_DIR/scripts/run_once.sh" "$ROOT_DIR/scripts/load_agent.sh" "$ROOT_DIR/scripts/unload_agent.sh"
echo "LaunchAgent installed to $PLIST_DST"
