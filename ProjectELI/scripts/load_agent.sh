#!/bin/bash
set -euo pipefail
launchctl unload "$HOME/Library/LaunchAgents/com.projectcognition.smartglasses.plist" >/dev/null 2>&1 || true
launchctl load "$HOME/Library/LaunchAgents/com.projectcognition.smartglasses.plist"
launchctl start com.projectcognition.smartglasses || true
echo "Agent loaded"
