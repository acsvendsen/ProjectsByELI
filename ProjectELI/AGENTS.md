# Project ELI Working Rules

## Mission
ELI is a field-based project cognition engine. Its job is to refine the active project instance continuously by tracking architectural intent, tensions, constraints, progress, and drift over time.

## Project-source rule
- Keep engine behavior generic where possible.
- Treat `config/config.yaml` and `projects/<project_name>/` as the source of project-instance truth.
- Keep project-specific interaction rules, hardware assumptions, and product constraints in project docs and project config rather than in engine-only docs.

## Cycle behavior
- `sleep` should consolidate signals, tensions, contradictions, and weakening trends.
- `dream` should generate a small number of project-specific, core-deepening possibilities with concrete next probes.
- `reality` should pressure-test current direction against real constraints and identify likely waste early.
- `scorecard` should compare current implementation progress against goals and limitations.
- Future `reflect` work should update the field itself: what is strengthening, weakening, resonating, or drifting.

## ELI vs product runtime
- ELI is project tooling first, not the shipped wearer-facing assistant.
- Keep operator controls and project steering in separate dev surfaces from any end-user runtime.

## Current priorities
- Build the persistent field layer around attractors, tensions, constraints, and modes.
- Keep existing cycles working while deepening reflection, resonance, and auditability.
- Prefer grounded implementation truth over generic prose whenever build/runtime evidence is available.
- Keep project-instance specifics in project docs, scorecard config, and linked project files.
