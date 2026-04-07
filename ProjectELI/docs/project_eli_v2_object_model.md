# Project ELI V2 Object Model

## Purpose
The V2 object model keeps the field simple for now. It is designed to be easy to inspect, edit, and extend later without forcing an early database rewrite.

## Object types

### Attractor
- Stored in `field_v2/attractors.json`
- Fields:
  - `id`
  - `label`
  - `summary`
  - `strength`
- Meaning:
  - a persistent pull the project should move toward

### Tension
- Stored in `field_v2/tensions.json`
- Fields:
  - `id`
  - `label`
  - `summary`
  - `pressure`
- Meaning:
  - a balance the project must continuously manage

### Constraint
- Stored in `field_v2/constraints.json`
- Fields:
  - `id`
  - `label`
  - `summary`
  - `type`
- Meaning:
  - a hard rule or guiding limitation that should resist drift

### Mode
- Stored in `field_v2/modes.json`
- Fields:
  - `current_mode`
  - `items[]`
  - each item has `id`, `label`, `summary`
- Meaning:
  - the current cognitive stance or bias ELI should operate under

## Supporting persistent docs
- `ELI/attractors.md`
- `ELI/tensions.md`
- `ELI/constraints/v1_real_world_limits.md`
- `ELI/decisions/v1_architecture_direction.md`
- `ELI/inbox/current_unknowns.md`
- `ELI/modes/current_mode.md`

These docs are human-facing grounding documents for the current project instance. The JSON field objects are machine-friendly scaffolds. Together they form the early V2 field layer.

## Non-goals in V2 Phase 1 and 2
- no reflection graph yet
- no resonance scoring yet
- no automatic field mutation from reports yet
- no database normalization of field objects yet
