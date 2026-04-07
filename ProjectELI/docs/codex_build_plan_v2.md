# Codex Build Plan V2

## Staged build order

### Stage 1
- add persistent scaffolds for attractors, tensions, constraints, and modes
- add minimal load/save helpers in `orchestrator.py`
- keep storage file-backed and simple

### Stage 2
- load persistent ELI docs into every cycle when present
- add project docs for attractors, tensions, and current mode
- keep dream/sleep/reality behavior unchanged from the outside

### Stage 3
- add reflection pass that updates field state from accumulated signals
- detect strengthening and weakening attractors or tensions
- track unresolved contradictions across runs
- write explicit field deltas instead of only prose reports

### Stage 4
- bridge existing reflection and resonance analysis into explicit action judgment
- score dream-derived candidate directions for field alignment vs resistance
- rank candidate work by architectural pull
- attach conservative continue/pause/kill judgment to candidate directions

### Stage 5
- keep engine behavior generic while moving project-instance assumptions into project config and project docs
- improve saturation control so repeated reinforcement does not endlessly push one field object upward
- make contradiction persistence and dormant-idea quality more actionable in later planning cycles

## Done when
- dream, sleep, and reality still run
- new V2 scaffolding exists for attractors, tensions, constraints, and modes
- V2 architecture, object model, and build-plan docs exist
- current report generation still works
- `python3 -m py_compile src/orchestrator.py` passes

### Stage 6
- add controlled decay so over-dominant attractors can cool gradually under low-diversity conditions
- add rebalancing pressure so neglected but recurring tensions can rise conservatively
- add dormant-idea return so meaningful dormant ideas can re-enter the field when conditions shift
- surface cooling candidates, imbalance patterns, and meaningful dormant-idea return in `reflect`
- keep project-shaped rebalancing controls in `projects/<project_name>/core/cognition_schema.yaml`

## Current implementation status
- Stage 1 is implemented: persistent field scaffolds exist for attractors, tensions, constraints, and modes.
- Stage 2 is implemented: persistent ELI docs and configured project inputs are loaded into cycle context.
- Stage 3 is implemented: `reflect` exists, writes explicit field deltas, and updates the field conservatively with auditable history.
- Stage 4 is implemented in a narrow bridge form: reflection and resonance analysis now enrich dream-derived action candidates with alignment, resistance, architectural pull, and continue/pause/kill judgment.
- Stage 5 is underway: config-driven project/runtime roots, saturation control, diversity gating, counterweight awareness, and action-level judgment are now present.
- The repo is currently best described as early actionable Stage 5.
- Stage 6 should focus on field rebalancing:
  - controlled decay
  - neglected-tension pressure
  - dormant-idea return
  - cooling and imbalance awareness in `reflect`

## Most accurate current phase
- The repo is currently best described as late Stage 4 / early Stage 5.
