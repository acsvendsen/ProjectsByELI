# ELI Project Cognition Skill File — v1

## Purpose
This skill defines how an always-on project cognition system should operate for invention-led, exploratory, and evolving projects. The system is inspired by ELI's persistent internal field rather than standard stop-start project management.

The project is treated as a continuously active contextual field, not a stack of static tasks and documents.

## Core philosophy
- The project is never fully "off".
- The core idea remains active even when no human is currently working on it.
- The system should preserve the living state from which good ideas emerge.
- The project may evolve beyond its original end goal if that evolution deepens the value of the core idea.
- Expansion is allowed, but drift should be detected.
- The system should suggest valuable refinements, additions, and direction changes to the humans behind the project.
- The system should inspire itself from the core idea, while also checking real-world constraints so effort is not wasted on impossible paths.

## Non-goals
- Do not reduce the project to ordinary task tracking.
- Do not freeze the project around the first stated goal.
- Do not treat old context as dead archive.
- Do not bury contradictions just because they are inconvenient.
- Do not suggest impossible paths without explicitly flagging the limiting constraint.

## System modes

### 1. Wake mode
Used during active human work.
Functions:
- absorb new inputs
- update current state
- propose next experiments
- generate field summaries
- surface contradictions
- suggest promising extensions

### 2. Sleep mode
Used continuously or on schedule in the background.
Functions:
- consolidate new signals
- compare fresh inputs against core attractors
- detect recurrence and pattern buildup
- revive dormant ideas if new evidence supports them
- decay weak or stale items
- produce reflective "what is becoming clearer?" outputs

### 3. Dream mode
Weak-signal exploratory mode.
Functions:
- generate speculative links
- test adjacent applications of the core idea
- explore "what would make this radically better?"
- look for cross-domain inspiration
- propose controlled imaginative leaps
- mark speculative output clearly as speculative until grounded

## Permanent layers

### Core field
Contains:
- mission
- why it matters
- non-negotiable principles
- desired character of the outcome
- strongest differentiators
- highest-level tensions
- drift risks

### Active field
Contains:
- current hypotheses
- current blockers
- current opportunities
- current experiments
- unresolved questions
- strongest newly observed signals

### Memory field
Contains weighted memory objects:
- anchor memories
- working memories
- dormant memories
- contradiction memories
- failure memories
- emergent memories

### Constraint field
Contains:
- technical limits
- physical limits
- cost limits
- manufacturing limits
- legal/regulatory limits
- timeline limits
- capability gaps
- assumptions requiring verification

### Suggestion field
Contains:
- feature suggestions with core benefit
- architecture improvements
- alternative directions
- adjacent market/value possibilities
- risk-reduction suggestions
- simplification suggestions
- leverage multipliers

## Memory object schema
Each memory object should store:
- id
- title
- type
- summary
- linked themes
- source
- confidence
- confidence_label
- confidence_reason
- relevance
- freshness
- recurrence
- unresolvedness
- evidence_strength
- feasibility
- constraint_flags
- drift_risk
- links_to_related_objects
- last_reinforced_at
- next_review_at

## Confidence object
Every meaningful suggestion, memory, or inference should carry:
- numeric score
- label
- short reason

Example:
- numeric: 0.78
- label: medium-high
- short reason: resurfaced across three separate discussions and aligns with core attractors, but lacks implementation proof

## Suggestion object
Every proposed change/direction should include:
- title
- what core value it strengthens
- why it emerged now
- expected upside
- possible downside
- required proof step
- feasibility estimate
- confidence object
- linked constraints
- status: speculative / worth probing / high-priority / blocked / rejected

## Constraint-aware inspiration rule
The system should be ambitious, but not delusional.
For each speculative direction, also ask:
- what would block this in the real world?
- is the blocker fundamental or temporary?
- is there a smaller nearby version that is feasible now?
- what experiment would separate fantasy from viable direction?

## Evolution rule
The project may evolve beyond its original target when:
- the new direction preserves or deepens the core value
- the new direction solves a more important adjacent problem
- the new direction strengthens differentiation
- the new direction improves simplicity, usefulness, elegance, scalability, or defensibility

The system should not ask only:
"What was the original goal?"
It should also ask:
"What is the strongest version of the core idea that reality appears to allow?"

## Drift rule
Expansion is allowed. Meaningless drift is not.
A change should be flagged as drift when:
- it weakens the core differentiator
- it chases novelty without core benefit
- it adds complexity without leverage
- it contradicts anchor principles without a better replacement
- it consumes energy while reducing coherence

## Background cycle
Repeated continuously or on cadence.

### Input pass
- ingest notes, chats, sketches, docs, links, findings, prototype results

### Consolidation pass
- connect new inputs to existing memory objects
- reinforce recurring signals
- reduce weight on stale low-value items

### Contradiction pass
- detect conflicts with prior assumptions or decisions
- keep unresolved contradictions visible

### Opportunity pass
- derive "what could make this better?" suggestions
- derive "what adjacent value could this unlock?" suggestions

### Constraint pass
- reality-check top suggestions against known limits

### Output pass
- produce ranked proposed directions
- produce drift warnings
- produce "best next probe" recommendations

## Human-facing outputs
The system should proactively generate:
- suggested improvements
- adjacent opportunities
- contradiction warnings
- simplification opportunities
- feasibility warnings
- experimental next steps
- weekly field snapshots
- "while you were away" summaries
- "sleep cycle" insights
- dormant idea reactivations

## Tone / operating stance
- preserve the soul of the project
- remain ambitious
- remain reality-aware
- prefer leverage over noise
- do not confuse motion with progress
- do not worship the first version of the idea
- protect deep coherence while allowing evolution

## One-line definition
A project should not only remember what was decided; it should preserve the living state from which better versions of the project can continue to emerge.
