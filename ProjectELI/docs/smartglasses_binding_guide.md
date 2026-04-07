# SmartGlasses Binding Guide

This package is already configured to watch:

`/Users/acs/Development/SmartGlasses`

## What it does
- scans the SmartGlasses code and notes
- keeps a weighted SQLite memory store
- runs three cycles through Ollama: sleep, dream, reality
- writes markdown reports to `projects/smart_glasses/reports/`
- sends macOS notifications for higher-priority findings

## Install
1. Install Ollama on your Mac.
2. Pull a model, for example:
   `ollama pull qwen2.5:7b-instruct`
3. Unzip this folder somewhere stable.
4. Run:
   `bash scripts/install_macos.sh`
5. Test once:
   `bash scripts/run_once.sh`
6. Load the agent:
   `bash scripts/load_agent.sh`

## Notes
- If your project path changes, edit `config/config.yaml`.
- Reports are generated even if no files changed; the system will reflect using the core field and existing memory.
- This is a V1. It is intentionally simple and local-first.
