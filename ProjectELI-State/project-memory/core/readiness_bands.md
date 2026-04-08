# Readiness Bands

This file is an operational rule file, not a broad philosophy file. Keep it narrow, reusable, and tied to readiness communication.

## Purpose

Readiness should be communicated in a way that is useful and honest without implying fake precision.

User-facing readiness should therefore use coarse bands rather than exact displayed percentages.

---

## User-facing readiness bands

- `ready_to_review`
- `almost_ready`
- `emerging`
- `too_early`

These labels should be preferred over exact percentages in user-facing interfaces.

They are meant to preserve honesty and usability, not to hide missing evidence or overstate maturity.

---

## Recommended internal mapping

Internal numeric scoring may exist for ranking or transition logic, but it should not be the primary user-facing surface.

Recommended mapping:

- `85–100` → `ready_to_review`
- `60–84` → `almost_ready`
- `35–59` → `emerging`
- `0–34` → `too_early`

---

## Meaning of each band

### `ready_to_review`
The option or artifact is grounded enough to be surfaced for explicit human review now.

Typical properties:
- bounded enough to inspect
- materially relevant
- grounding is strong enough
- blockers are not dominant
- review is useful now

### `almost_ready`
The option or artifact is close, but still missing one or more important forms of grounding or clarification.

Typical properties:
- promising and increasingly shaped
- useful to watch
- not yet strong enough for full review
- likely to mature with limited additional evidence

### `emerging`
The option or artifact is taking shape, but remains under-grounded, blocked, or too early for strong review.

Typical properties:
- meaningful but not mature
- still forming
- should not be over-read as a near-term decision
- often still needs repo/runtime/user evidence

### `too_early`
The option or artifact is not yet mature enough to surface as a serious review item.

Typical properties:
- weak grounding
- unclear framing
- speculative or premature
- likely to create noise if surfaced too strongly

---

## Important constraints

- user-facing output should prefer readiness bands over exact displayed percentages
- exact percentages should not be used to imply false certainty
- held or blocked items must not be made to look review-ready
- readiness should reflect grounding, not just repetition
- readiness should be revisable when new evidence appears

---

## Working test

A good readiness label should help answer:

- should this be reviewed now?
- is it close but not ready?
- is it still only emerging?
- is it too early to surface strongly?
