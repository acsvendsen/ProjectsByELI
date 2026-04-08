# Codex Phase Prompt Patterns


## Purpose

This file stores reusable prompt patterns that help keep Codex work narrow, auditable, canonically targeted, and aligned with ELI principles.

## When to use which pattern

Use this file as a practical prompt toolbox, not as a rigid script.

- use `Standard preamble` for most SmartGlasses-era Codex passes that should anchor to the canonical project path and handoff
- use `Standard operating constraints` when the pass could drift into overreach, fake precision, premature commitment, or SmartGlasses-specific hardcoding
- use `Standard inspection block` when you want Codex to explicitly declare what it is reading and modifying before editing
- use `Standard closeout block` when you want a concise, auditable summary of what changed and why
- use `Narrow pass pattern` for most implementation phases where one sharply defined improvement is the goal
- use `Correction prompt pattern` when Codex solved the wrong problem, targeted the wrong lane, or repeated a previous pass instead of doing the requested one
- use `Review-lane pass pattern` when a surfaced lane exists but is too compact, unstable, hard to inspect, or missing continuity
- use `Readiness-band pass pattern` when a user-facing maturity/readiness surface is needed and exact displayed percentages would be misleading
- use `Artifact-maturation pass pattern` when implementation artifacts exist structurally but still need better typing, detail, or semantic honesty
- use `Draft artifact emission readiness pattern` when the goal is to decide whether a review artifact is mature enough for draft emission, not to generate final artifacts yet

---

## Standard preamble

Use this at the top of most Codex prompts:

This is the SmartGlasses-era canonical preamble. If you later generalize beyond SmartGlasses, create a project-agnostic variant rather than weakening this one.

```text
Before making any changes, read and follow:

/Users/acs/Development/ProjectsByELI/ProjectELI-State/SmartGlasses/core/Codex_handoff.md

Use this as the canonical SmartGlasses project path for this pass:

/Users/acs/Development/ProjectsByELI/ProjectELI-State/SmartGlasses

Do not write parallel copies under:
- /Users/acs/Development/ProjectsByELI/ProjectELI/projects/smart_glasses
- /Users/acs/Development/ProjectsByELI/SmartGlasses
```

---

## Standard operating constraints

Use when relevant:

```text
Important intent:
ELI should remain general-purpose and trust-preserving.
Do not hard-specialize the engine around SmartGlasses unless the pass explicitly requires project-shaped config only.

Requirements:
- preserve ELI as the authoritative synthesizer and judge
- do not broaden architecture unnecessarily
- do not auto-apply final commitments
- do not expose fake precision
- prefer conservative, review-oriented shaping over loose optimism
```

---

## Standard inspection block

Use near the top of implementation prompts:

```text
Before editing, print:
1. current working directory
2. exact canonical SmartGlasses path you will use
3. exact files you expect to read
4. exact files you expect to modify
```

---

## Standard closeout block

Use at the end of implementation prompts:

```text
At the end, briefly explain:
- what structure was added or changed
- how it works
- how ELI authority remains preserved
- exactly which files you changed
```

---

## Narrow pass pattern

Use for most phase prompts:

```text
This pass is for [single narrow purpose] only.

Goals for this pass:
1. ...
2. ...
3. ...

Please make only the minimal coherent changes needed so that:
- ...
- ...
- ...
```

---

## Correction prompt pattern

Use when Codex implements the wrong lane:

```text
Your previous response implemented the wrong pass.

Please correct course and target only:
- [correct lane / file / structure]

Do not spend this pass modifying:
- [wrongly targeted files or structures]
unless strictly required as a small compatibility adjustment.

At the end, explicitly state:
1. the exact target file or structure name
2. whether it now contains the requested content
3. whether continuity or transitions were added
4. exactly which files you changed
```

---

## Review-lane pass pattern

Use for review surfaces:

```text
This pass is for [review lane name] continuity and inspectability.

Context:
- the lane exists but is too compact / unstable / hard to inspect
- I want a dedicated review surface
- this should remain review-oriented and not become a workflow engine

A good result would allow the system to say:
- these are the current items
- these recently changed
- here is why they changed
- here is what is still revisable
```

---

## Readiness-band pass pattern

Use for user-facing readiness work:

```text
This pass is for a user-facing option surfacing and readiness layer.

Readiness should use coarse bands, not exact displayed percentages.

Recommended bands:
- ready_to_review
- almost_ready
- emerging
- too_early
```

---

## Artifact-maturation pass pattern

Use for implementation artifact work:

```text
This pass is for semantic maturation of the implementation-artifact review lane.

Do not invent fake technical detail.
Do not collapse UX/policy questions into hardware/component language unless justified.
Add optional bounded detail only when it is honest to do so.
```
```

---

## Draft artifact emission readiness pattern

Use before actual draft outputs:

```text
This pass is for artifact promotion readiness only.

Do not generate final PDFs, final KiCad files, or final engineering commitments.
This pass is only for deciding when a review artifact is mature enough to become a draft artifact candidate.
```

---

## Branch and commit naming pattern

Use branch and commit names that preserve phase intent and make later review easier.

### Branch naming

Preferred pattern:
- `features/phaseNN_shortDescription`

Examples:
- `features/phase21_optionReadinessUI`
- `features/phase22_artifactPromotionReadiness`
- `features/phase20_artifactSemanticMaturation`

Guidelines:
- keep the phase number if the work is part of the staged Codex progression
- keep the short description narrow and specific
- prefer capability names over vague labels like `misc_updates`

### Commit naming

Preferred style:
- imperative, narrow, and outcome-oriented

Examples:
- `Add user-facing option surfacing with coarse readiness bands`
- `Refine implementation artifact typing and add bounded review detail`
- `Add dedicated review surface and continuity for implementation artifacts`


Guidelines:
- describe what was added, hardened, refined, or preserved
- avoid generic commit messages like `updates` or `fix stuff`
- let the commit message reflect the actual pass purpose, not just the file touched

---

## Working reminder

Good Codex prompts should:
- target one narrow pass
- preserve canonical paths
- keep changes inspectable
- protect ELI’s authority
- avoid fake certainty
- avoid architecture drift
