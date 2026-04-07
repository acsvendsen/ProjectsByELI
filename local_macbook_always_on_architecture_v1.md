# Local MacBook Always-On Architecture v1

## Objective
Run an always-on project cognition system locally on a MacBook, using background processes and local models where practical.

## Recommended V1 Stack
- macOS LaunchAgent via launchd
- Python orchestrator
- SQLite state store
- Markdown project files
- Ollama local model runtime
- optional Open WebUI for manual interaction

## Why Local First
- lower latency
- private project state
- always-on background availability
- easy file watching on the Mac
- can still escalate selected jobs to cloud models later

## System Services
### 1. Ingest Service
Watches project folders and ingests new notes, transcripts, markdown files, and logs.

### 2. Memory Service
Extracts structured memory objects, constraints, tensions, and candidate suggestions.

### 3. Sleep Service
Runs on a timer to consolidate new information into the memory field.

### 4. Dream Service
Runs on a timer to generate upward-evolution possibilities for the core idea.

### 5. Reality Service
Scores dream outputs against feasibility and constraint signals.

### 6. Snapshot Service
Writes a readable project field report for the user.

## Apple Silicon Fit
An Apple Silicon MacBook can comfortably handle file watching, orchestration, SQLite, local summarization, tagging, and periodic project synthesis. Heavier deep synthesis can remain optional.

## Deployment Notes
- use launchd to keep the main loop alive
- store logs in a dedicated local folder
- keep reports human-readable in markdown
- keep prompts editable in plain files
- start with one project, then scale to multiple projects
