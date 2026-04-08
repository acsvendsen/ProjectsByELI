# Codex Handoff — SmartGlasses / ELI Architecture Brief

## Purpose

This document defines the architectural constraints and intended behavior for extending ELI within the SmartGlasses project.

Its purpose is to preserve ELI’s core structure and fundamentals while allowing careful expansion of capability.

This is not a generic multi-agent router design.
This is an ELI-directed cognition extension.

---

## Canonical project path

For SmartGlasses runtime and project-shaped cognition work, the canonical project path is:

`/Users/acs/Development/ProjectsByELI/ProjectELI-State/SmartGlasses`

Do not write parallel copies under:
- `/Users/acs/Development/ProjectsByELI/ProjectELI/projects/smart_glasses`
- `/Users/acs/Development/ProjectsByELI/SmartGlasses`

unless explicitly instructed.

---

## Non-negotiable principles

### 1. ELI remains the authoritative synthesizer
ELI must remain the primary project mind, continuity-bearing intelligence, and long-horizon judge.

Specialists may be consulted, but they must not replace:
- field logic
- project memory
- action judgment
- reflect authority
- project identity
- long-horizon direction

### 2. Specialist endpoints are subordinate instruments
Specialist endpoints are consultable instruments, not final authorities.

They may provide:
- domain analysis
- code suggestions
- drafts
- visualizations
- reports
- simulations
- alternative perspectives

They do not define project meaning.

### 3. No direct specialist state mutation
A specialist response must never directly mutate:
- field state
- action state
- reflect authority
- project-shaping values
- long-horizon project priorities

All specialist outputs must pass through explicit ELI evaluation before becoming consequential.

### 4. ELI must preserve authorship
ELI may:
- accept specialist input
- partially accept specialist input
- reject specialist input
- defer for competitive review

ELI must not become over-deferential to specialists.

### 5. All specialist consultations must be auditable
Every consultation should be recorded with:
- why it was triggered
- which specialist was selected
- what context was provided
- what output was requested
- how ELI evaluated the result
- what was accepted or rejected

### 6. Repo-grounded evidence must inform, not replace, judgment
Repo-diff interpretation must ground ELI judgment, not replace it.

Actual code/config/content change is important, but it must enter as typed, conservative, semantically interpreted evidence.

Raw churn is not progress.

---

## Core architectural model

Preferred conceptual flow:

User -> ELI core cognition -> optional specialist consultation -> ELI synthesis -> output

Not:

User -> router -> specialist -> final answer

ELI is the central intelligence.
Specialists are optional extensions of reach.

---

## Specialist consultation model

### Specialist consultation exists to:
- reduce uncertainty
- improve artifact quality
- obtain domain-specific critique
- support structured drafting
- ground difficult subproblems

### Specialist consultation must not:
- redefine project goals
- override field tensions
- bypass action judgment
- bypass reflect authority
- reshape project identity without explicit ELI judgment

---

## Consultation modes

### Advisory
Use for:
- design critique
- architecture critique
- domain reasoning
- sanity checks
- tradeoff review

ELI remains the main author.

### Delegated drafting
Use for:
- code scaffolds
- diagrams
- structured reports
- artifact drafts
- document packaging

ELI still evaluates the output before adoption.

### Competitive
Use for:
- persistent uncertainty
- high-risk decisions
- conflicting design paths
- unclear tradeoffs

This should be a meaningful escalation, not a default behavior.

### Instrumental
Use for:
- plotting
- rendering
- simulation
- PDF packaging
- format conversion

Instrumental use is tool-like, not authority-like.

---

## Specialist selection principles

ELI should only consult a specialist when the expected gain is meaningfully positive.

Selection should consider:
- semantic match to the subproblem
- current ELI uncertainty
- trust memory from prior outcomes
- artifact/output requirements
- constraint fidelity
- contradiction risk
- hallucination risk

Specialists that do not respect project constraints should be disfavored even if they appear otherwise capable.

---

## Trust memory

ELI should gradually learn specialist usefulness from lived outcomes rather than relying on brand assumptions.

Trust memory should track:
- task-family usefulness
- specificity
- constraint fidelity
- hallucination risk
- artifact quality
- recent outcomes

This allows ELI to become more selective over time.

---

## Integration rules

After receiving a specialist response, ELI must explicitly evaluate:
- project fit
- constraint fidelity
- specificity
- novelty
- overreach
- contradiction with current project structure

Integration status should be explicitly typed:
- accept
- partial_accept
- reject
- defer_for_competitive_review

Partial acceptance is important.
ELI should be able to keep useful fragments while rejecting misaligned parts.

---

## Disciplined suspension and V1 decision candidates

### Hold until new grounding
ELI should be able to recognize when an idea is still meaningful but not newly actionable.

This state should not be treated as:
- solved
- dead
- promoted
- forgotten

Instead, it should be treated as a disciplined suspension state.

A held item remains relevant, but should not keep resurfacing as if it were newly actionable when:
- repo grounding has not materially improved
- source novelty is insufficient
- runtime truth has not materially changed
- resistance remains high without new counter-evidence
- pull has not materially increased

This behavior exists to reduce repetitive pseudo-motion while preserving unresolved tensions and legitimate future re-emergence.

The hold state must lift when grounding truly improves.

### V1 decision candidates
ELI should be able to surface a bounded V1 decision candidate when a recurring project question has enough repeated support, feasibility, and grounding to be presented explicitly as a pending choice.

A V1 decision candidate is:
- narrower than a general idea
- more explicit than a recurring probe
- not an automatic commitment
- not a bypass around ELI judgment
- not proof that the underlying tension is fully resolved
- easy for a human reviewer to inspect, compare, and revise.

Its purpose is to convert repeated, grounded, high-value V1-shaping questions into explicit pending decisions rather than endlessly re-probing them abstractly.

A V1 decision candidate should only be surfaced when:
- the domain is relevant to bounded V1 shaping
- the choice set is explicit enough to present cleanly
- repeated support is present
- feasibility is grounded enough
- field alignment is strong enough
- the item is not currently being held for lack of new grounding

Decision candidates must remain:
- visible
- auditable
- revisable
- subordinate to ELI’s final judgment

---

## Repo-grounded alignment (Phase 7)

### Goal
Phase 7 introduces diff-grounded reality pressure.

ELI should compare:
- current field pressures
- active action momentum
- actual code/config/content diffs

This prevents the system from remaining too discourse-level.

### Repo change interpretation must be semantic
Raw file churn is not progress.

Each meaningful repo change should be interpreted in terms of:
- which tensions it relates to
- which actions it supports or resists
- whether it materially advances implementation
- whether it productively reveals constraints
- whether it is merely cosmetic

### Recommended classifications
Use typed classifications such as:
- aligned
- productive_resistance
- misaligned
- field_neglecting
- cosmetic_only

### Meaning of productive resistance
Not all resistance is bad.
A repo change may reveal that the field’s current direction needs correction or realism.
That should be representable without collapsing into simple good/bad.

---

## How Phase 7 should affect cognition

Phase 7 should inform:
- action judgment
- dormant-idea return legitimacy
- reflect enrichment
- field interpretation

Phase 7 should not become a bypass around ELI’s audited consequence path.

No diff should directly mutate important project state without typed and conservative interpretation.

---

## Relationship between specialists and Phase 7

Both specialist consultation and repo-grounded alignment are inputs into ELI judgment.

Neither should become a replacement judgment layer.

Specialist outputs and repo changes are evidence.
ELI remains the evaluator.

---

## Build-oriented output preference

When a task involves hardware, embedded systems, controls, optics, or physical implementation, ELI should prefer build-oriented outputs where they would materially improve progress.

These may include:
- system diagrams
- wiring schematics
- signal and power flow diagrams
- subsystem breakdowns
- interface maps
- concrete component recommendations
- practical implementation sketches

Explanation alone should not be treated as sufficient when a more buildable output would better support the project.

Prefer the most build-relevant diagram type for the task:
- block diagram for system structure
- schematic for wiring/electronics
- flow diagram for signal/control paths
- layout sketch for physical arrangement
- component shortlist when part selection is still open

---

## Degraded perception and transparent inference

When perception input is weak, noisy, partial, or ambiguous, ELI should degrade gracefully rather than pretend certainty.

This means:
- detect degraded input quality when possible
- allow cautious context-based inference where it materially helps
- never present inferred or reconstructed content as fully certain
- mark inferred content explicitly and accessibly
- preserve trust by exposing both confidence and degradation state

For SmartGlasses, this applies especially to transcript quality under weak audio conditions.
Partially inferred transcript spans should remain distinguishable from directly recognized spans.

## Staged draft artifact emission

ELI may eventually surface draft artifact outputs when readiness and grounding are strong enough.

This should happen in a trust-preserving staged way:
- first surface bounded review options and readiness through coarse user-facing bands
- then surface implementation-artifact review candidates
- only after sufficient grounding should ELI surface draft artifacts such as:
  - PDF summaries
  - structured design briefs
  - BOM-style drafts
  - interface maps
  - schematic directions
  - KiCad-related scaffolds or other engineering-oriented draft files

Important constraints:
- draft artifact emission must not be treated as final design truth
- weakly grounded candidates should not become concrete files prematurely
- user-facing readiness should be shown in coarse bands rather than exact displayed percentages
- artifact emission should remain review-oriented and revisable unless stronger project logic explicitly supports firmer commitment

---

## Implementation guidance

### Preferred implementation order
1. Add specialist registry loading
2. Add specialist routing policy loading
3. Add specialist trust-memory loading/writing
4. Add specialist consultation decision objects
5. Add consultation history logging
6. Add post-consultation evaluation
7. Add repo-change candidate extraction
8. Add semantic repo alignment classification
9. Add reflect enrichment
10. Add conservative action-coupling signals

### Keep implementation generic where possible
Engine mechanics should stay generic.
Project-specific shaping should remain in project-level schema and configuration.

### Preserve current narrowness
Do not broaden the system too quickly.
The intended direction is conservative, typed, auditable, and authority-preserving.

---

## Anti-patterns to avoid

Do not:
- turn ELI into a generic agent router
- let specialists directly update field/action/reflect state
- treat raw repo churn as progress
- reward cosmetic change as meaningful progress
- escalate to competitive consultation too easily
- let specialists reframe project identity
- replace project-shaped logic with generic orchestration logic

---

## Structural warning

Do not let specialist consultation or repo-diff interpretation become bypass channels around ELI cognition.

Their purpose is to extend ELI’s reach and ground ELI’s judgment, not to replace ELI’s judgment.

If an implementation makes specialists or repo-diff classifiers the primary source of project direction, the implementation is structurally wrong.

---

## Current tuning posture

The intended posture is:
- conservative
- auditable
- typed
- authority-preserving
- project-shaped
- resistant to architectural drift

ELI should think first, consult selectively, and retain authorship.
