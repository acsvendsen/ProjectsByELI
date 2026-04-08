# Artifact Progression

## Purpose

Artifacts should emerge in a staged, trust-preserving way.

ELI should not jump directly from vague idea to concrete emitted file.
Instead, artifacts should mature through review, readiness, and grounding.

---

## Progression model

### 1. Concept or pressure
A project tension, question, or repeated need begins to suggest that a more concrete artifact may eventually be useful.

Examples:
- unclear system boundary
- unresolved interface question
- repeated hardware uncertainty
- recurring UX decision pressure

At this stage:
- artifact need may be implicit
- no draft artifact should be emitted yet

---

### 2. Implementation-artifact candidate
The system surfaces a review-oriented implementation artifact candidate.

Examples:
- `subsystem_breakdown`
- `interface_map`
- `schematic_direction`
- `component_shortlist`
- `visual_layout_rule`
- `confidence_object_spec`

At this stage:
- the artifact is provisional
- it is still a review surface
- it is not yet a file-emission candidate by default

---

### 3. Semantically typed artifact review
The candidate becomes more clearly classified and begins carrying bounded useful detail.

Examples of useful bounded detail:
- candidate directions
- open constraints
- relevant interfaces
- candidate components
- escalation signals

At this stage:
- the artifact becomes easier to inspect
- continuity and transitions should remain visible
- weak grounding should remain visible

---

### 4. Option readiness / review readiness
The artifact or linked decision becomes visible in readiness terms.

Possible readiness bands:
- `ready_to_review`
- `almost_ready`
- `emerging`
- `too_early`

At this stage:
- the artifact may be mature enough for user inspection
- but not necessarily mature enough for draft emission

---

### 5. Draft artifact emission candidate
The system determines that an artifact may now justify a draft-oriented output.

Possible draft forms:
- `pdf_summary`
- `structured_design_brief`
- `bom_draft`
- `interface_map_draft`
- `schematic_direction_draft`
- `kicad_related_scaffold`

At this stage:
- draft emission remains provisional
- final design truth is still not claimed
- missing evidence should remain visible

---

### 6. Draft artifact emission
A draft artifact is surfaced.

This should happen only when grounding is strong enough.

Examples:
- draft PDF summary
- draft BOM-like output
- draft interface map
- draft schematic direction
- KiCad-related scaffold

At this stage:
- the artifact is still review-oriented unless stronger logic supports more commitment
- it should remain revisable

---

### 7. Stronger commitment
Only later, and only when justified, an artifact may begin to support stronger project commitment.

This may include:
- sharper engineering direction
- tighter component narrowing
- stronger implementation planning
- more concrete build preparation

This stage must not be reached through weak grounding or artifact theater.

---

## Promotion rules

Artifact progression should depend on:
- grounding strength
- bounded framing quality
- repo/runtime evidence when relevant
- constraint visibility
- review readiness
- whether the artifact materially helps the project move forward
- whether stronger concreteness would preserve architecture rather than simulate progress

---

## Anti-patterns

Do not:
- jump directly from abstract question to concrete file
- emit draft artifacts because they “look useful” without grounding
- let weakly grounded artifacts appear more mature than they are
- confuse review artifacts with final commitments
- sacrifice truth for artifact richness

---

## Working test

A good artifact progression should help answer:
- what stage is this artifact in?
- what is it ready for now?
- what is missing before stronger emission or commitment is justified?
- is this becoming more buildable without sacrificing architectural integrity?
