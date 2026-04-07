# Project ELI Cognition Engine

Local always-on project cognition engine for a configured project instance.

The current instance is configured for:

`/Users/acs/Development/SmartGlasses`

This service watches the configured project, maintains weighted memory in SQLite, runs sleep/dream/reality/reflect cycles through Ollama, and writes suggestions plus daily field snapshots.

ELI in this repo is a project-refinement system: it critiques architecture, tracks progress against goals and limits, and helps steer implementation. It is not the shipped wearer-facing assistant UI.

## Dashboard

Run the local project dashboard:

```bash
./scripts/run_dashboard.sh
```

Then open:

`http://127.0.0.1:8421`

The dashboard shows:
- module health for sleep, dream, reality, and daily snapshot
- a project scorecard that compares progress against project-specific dimensions, goals, and limitations
- recent durations and freshness
- live CPU and RAM telemetry for ELI Brain and the dashboard server
- tracked-file and database load
- valuable recent output messages
- optional operator guidance buttons; if nothing is selected, the system uses best effort
- an action inbox populated from the latest dream cycle, with decision buttons per domain
- the currently active project and the current execution mode
- a dev/operator surface that stays separate from the wearer-facing iPhone app

## ELI V2 Field Layer

ELI V2 now keeps a persistent field layer for:
- attractors
- tensions
- constraints
- modes

Phase 3 adds a `reflect` cycle that proposes conservative field deltas and writes an auditable update history at:

- `/Users/acs/Development/ProjectsByELI/ProjectELI-State/SmartGlasses/state/field_delta_history.json`
- `/Users/acs/Development/ProjectsByELI/ProjectELI-State/SmartGlasses/state/reflect_state.json`

## Current Instance Grounding

For the current SmartGlasses instance, ELI auto-refreshes the TranscriptLab Xcode build summary before each cognition pass whenever:
- the stored build summary is missing
- TranscriptLab files changed since the last stored summary
- the shared transcript layer changed since the last stored summary

The auto-refresh writes:
- `state/transcriptlab_xcode_build_summary.md`
- `state/transcriptlab_xcodebuild.log`

Those are included in every cycle alongside the key ELI docs and the app docs configured for this project instance.

You can still refresh the build summary manually if needed:

```bash
python3 scripts/capture_transcriptlab_build.py
```
