# Review Lanes

## Purpose

ELI should not treat all surfaced items as the same kind of thing.

Different kinds of project movement need different review lanes so that:
- readiness remains honest
- continuity remains visible
- held items do not look active
- artifact candidates do not look like final commitments

---

## Lane overview

### 1. Pending decision review
This lane contains bounded choices that are mature enough for explicit inspection.

Examples:
- default subtitle position
- confidence display format
- phone/cloud boundary
- visual hierarchy

These should:
- be bounded
- carry current direction
- remain revisable
- show what could still change them

---

### 2. Held pending new grounding
This lane contains items that are still meaningful, but not newly actionable.

Typical properties:
- still aligned with project goals
- currently resisted, under-grounded, or stalled
- should not be re-chewed as if they are fresh
- should reactivate only when grounding changes

This lane protects against pseudo-motion.

---

### 3. Implementation-artifact review
This lane contains implementation-oriented review objects.

Examples:
- subsystem_breakdown
- interface_map
- component_shortlist
- schematic_direction
- implementation_sketch
- visual_layout_rule
- confidence_object_spec

These are:
- provisional
- review-oriented
- not final design truth
- candidates for stronger draft forms only when grounding improves

---

### 4. User-facing readiness review
This lane surfaces what is:
- ready_to_review
- almost_ready
- emerging
- too_early

These are user-facing labels; internal ranking or scoring may exist, but should not be exposed as fake precision.

This lane is meant to expose maturity honestly without fake precision.

---

### 5. Draft artifact emission readiness
This lane should appear only when the system can conservatively distinguish:
- still only a review artifact
- mature enough for a draft artifact candidate
- not yet honest to emit

This lane should stay secondary to artifact review itself.

---

## Transition principles

A surfaced item may move between lanes, but the move should be explainable.

Examples:
- pending decision -> held pending new grounding
- implementation artifact -> draft artifact candidate
- current review item -> recently changed / superseded
- active candidate -> no_longer_qualified

Transitions should not feel like silent disappearance.

---

## Review lane rules

- keep current items primary
- keep recently changed items secondary
- do not let held items masquerade as ready
- do not let draft-candidate status masquerade as final commitment
- continuity should explain change, not freeze it
- practical usefulness should stay visible; structural maturity alone should not make a lane look more valuable than it is
- review lanes should clarify project movement, not create workflow theater

---

## Working test

A good review-lane system should help answer:
- what kind of thing is this?
- why is it surfaced here?
- what can the user do with it now?
- what changed since last cycle?
- what is still blocked or missing?
