# Field-Driven Project Cognition v1

## Definition
Field-Driven Project Cognition is a project architecture in which the project is treated as a persistent contextual field rather than a disconnected sequence of tasks, documents, and meetings.

## Thesis
A project should not only remember what was decided. It should preserve the living state from which good decisions emerge.

## Design Goals
- Preserve continuity between work sessions.
- Allow upward evolution of the project core.
- Detect when the project is becoming stronger than originally imagined.
- Prevent waste by checking promising directions against real-world constraints.
- Support human judgment with timely, valuable suggestions.

## Layers
### 1. Core Field
Persistent identity of the project:
- mission
- why it matters
- non-negotiables
- core differentiators
- desired character
- fundamental tensions

### 2. Active Field
Current state:
- live questions
- current evidence
- strong directions
- uncertainties
- contradictions
- active experiments

### 3. Memory Field
Weighted project memory:
- anchor memories
- dormant ideas
- rejected paths
- lessons learned
- repeated patterns
- resurfacing opportunities

### 4. Dream Layer
Weak-signal synthesis:
- adjacent value possibilities
- elegant expansions
- recombination of old and new ideas
- “this may belong near the center” hypotheses

### 5. Reality Layer
Pressure test:
- physics
- cost
- tooling
- manufacturability
- regulation
- timelines
- dependencies
- implementation load

### 6. Output Layer
Human-facing outputs:
- snapshots
- alerts
- drift warnings
- opportunity suggestions
- next probes

## Core Rule
The project may evolve beyond the original end goal if the evolution produces a better final system while remaining meaningfully linked to the core value.

## Three Operating Rhythms
### Wake
Direct work and explicit updates.

### Sleep
Consolidation and reinterpretation.

### Dream
Speculative upward exploration.

## Why This Matters
Most projects repeatedly reconstruct context from scratch. That destroys subtle progress, hides contradictions, and weakens invention. A persistent field architecture reduces reconstruction cost and increases coherent emergence.

## V1 Implementation Pattern
- local project files as source inputs
- always-on watcher/orchestrator
- weighted memory store
- local LLM for synthesis and idea generation
- scheduled sleep and dream cycles
- reality-check cycle before surfacing high-energy suggestions
