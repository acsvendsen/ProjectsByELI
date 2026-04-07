# Project ELI V2 Architecture

## Summary
Project ELI V2 adds a persistent field layer underneath the existing cycle engine. The current `sleep`, `dream`, `reality`, `reflect`, and `scorecard` flows remain intact, but they now run with explicit field structures for attractors, tensions, constraints, and modes.

## Module map
- `src/orchestrator.py`
  - watches the configured project inputs
  - refreshes configured build/runtime truth when available
  - loads field scaffolds and persistent ELI docs
  - assembles context for `sleep`, `dream`, `reality`, `reflect`, and `scorecard`
  - enriches dream-derived action candidates with field judgment after `reflect`
- `projects/<project_name>/core/field_v2/*.json`
  - minimal persistent field scaffolds
  - internal field objects for Phase 1
- `links/repo/ELI/*.md`
  - project-facing field docs
  - persistent grounding for attractors, tensions, mode, constraints, architecture direction, and unknowns
- `state/<configured build summary>`
  - current build or runtime truth for the active project instance
- `<project runtime root>/reports/*.md`
  - cycle outputs written under the active runtime tree
- `<project runtime root>/state/action_inbox.json`
  - dream-derived candidate actions plus operator choices and field-ranked judgment
- `<project runtime root>/state/reflect_state.json`
  - reflect output, evidence analysis, action judgments, and current field snapshot

## Data flow
1. Watch repo-linked files and internal cognition files.
2. Refresh configured build/runtime truth when watched implementation inputs change, or when the summary is stale.
3. Load the internal V2 field scaffolds from JSON.
4. Load persistent ELI docs from the linked project repo when present.
5. Combine:
   - core field
   - V2 field scaffolds
   - persistent project docs
   - current repo changes
   - operator guidance
   - action inbox state
6. Feed that context into the `sleep`, `dream`, `reality`, `reflect`, and `scorecard` cycle prompts.
7. Use `reflect` to write conservative field deltas and derive action-level alignment, resistance, architectural pull, and continue/pause/kill judgment for dream-derived candidates.
8. Write reports, memories, runtime state, scorecard state, reflect state, and enriched action inbox state.

## Current architectural maturity
Project ELI is no longer only a reflective reporting engine. It now performs field-informed action steering.

The current engine can:
- maintain persistent field structures for attractors, tensions, constraints, and modes
- update field state conservatively through `reflect`
- detect resonance, contradiction persistence, counterweight pressure, and reinforcement loops
- enrich dream-derived action candidates with field judgment:
  - alignment
  - resistance
  - architectural pull
  - continue / pause / kill guidance

This means the architecture has moved from:
- cycle output only
to:
- field-informed direction judgment

The next architectural step is not broader output generation, but rebalancing:
- controlled decay
- cooling of over-dominant attractors
- neglected-tension pressure
- dormant-idea return under changed conditions

## Why the early V2 structure matters
- The field objects exist persistently.
- The linked field docs exist and are always loaded.
- The cycles still behave the same externally.
- Reflection and resonance are already active in the engine.
- Action ranking can now use the field layer instead of relying only on prompt output.
- Self-updating field logic can extend the engine without replacing the cycle structure.
