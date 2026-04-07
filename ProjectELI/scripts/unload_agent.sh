#!/bin/bash
set -euo pipefail
launchctl unload "$HOME/Library/LaunchAgents/com.projectcognition.smartglasses.plist" || true
echo "Agent unloaded"
