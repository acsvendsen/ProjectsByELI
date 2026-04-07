# macOS Install Guide

## What this version adds
- real Ollama API calls
- weighted memory scoring
- macOS notifications for high-priority findings
- launchd daemon mode for always-on behavior
- file-change detection for core and inbox markdown files

## 1. Install Ollama
Install Ollama on your Mac and pull the model configured in `config/config.yaml`.

Example:
```bash
ollama pull qwen2.5:7b-instruct
```

Start Ollama if it is not already running.

## 2. Prepare the project scaffold
Unzip the folder wherever you want it to live.

Edit:
- `projects/example_project/core/core_field.md`
- `projects/example_project/inbox/notes.md`

## 3. Install the Python environment and LaunchAgent
From the project root:
```bash
bash scripts/install_macos.sh
```

This creates:
- a local Python virtual environment
- a user LaunchAgent at `~/Library/LaunchAgents/com.example.projectcognition.plist`

## 4. Test one full cycle
```bash
bash scripts/run_once.sh
```

Then inspect:
- `projects/example_project/reports/`
- `data/memory.db`
- `logs/launchd.out`
- `logs/launchd.err`

## 5. Load the always-on daemon
```bash
bash scripts/load_agent.sh
```

The daemon will:
- keep running in the background
- poll every 60 seconds
- notice markdown changes
- run sleep / dream / reality cycles on schedule or when files change
- send macOS notifications for high-priority outputs

## 6. Unload it later
```bash
bash scripts/unload_agent.sh
```

## Notes
- The current system only watches markdown files in `core/` and `inbox/`.
- Notifications are sent with AppleScript `display notification`.
- The database is SQLite, so it is easy to inspect or migrate later.
- You can tune cadence and thresholds in `config/config.yaml`.
