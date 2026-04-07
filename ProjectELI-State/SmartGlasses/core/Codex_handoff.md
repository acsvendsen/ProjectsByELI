
Before making changes, read and follow `Codex_handoff.md` as the authoritative architectural brief for this work.

Important constraints:
- ELI must remain the authoritative synthesizer and long-horizon judge.
- Specialist endpoints are subordinate consultable instruments.
- Specialist outputs must not directly mutate field logic, action judgment, project memory, or reflect authority.
- Repo-diff interpretation must ground ELI judgment, not replace it.
- Preserve the current narrow, conservative, typed, and auditable structure.

For this pass, please implement the next conservative step for:
1. specialist consultation support
2. Phase 7 repo-grounded alignment

Scope:
- load and use the project specialist registry
- load and use the specialist routing policy
- load and update specialist trust memory
- create consultation decision objects and history logging
- add post-consultation evaluation with accept / partial_accept / reject / defer_for_competitive_review
- add repo-change candidate extraction
- add semantic repo alignment classification
- enrich reflect with specialist and repo-grounded signals
- keep all new consequences conservative and explicitly typed

Please do not let specialist outputs or diff interpretations become direct state-mutation bypasses.

Please keep implementation generic where possible, project-shaped where necessary, and do not modify the Phase 6 bridge except where needed to attach conservative typed inputs into existing audited flows.

phase7_repo_alignment:
  enabled: true

  diff_alignment:
    align_weight: 1.0
    productive_resistance_weight: 0.75
    misalignment_weight: -0.85
    neglect_weight: -0.65
    cosmetic_only_weight: -0.30

  action_coupling:
    reward_diff_backed_actions: true
    damp_talk_without_change: true
    enable_dormant_return_on_structural_progress: true

  reflect_grounding:
    require_diff_summary: true
    require_alignment_observations: true
    require_resistance_observations: true

  safeguards:
    do_not_equate_any_diff_with_progress: true
    do_not_penalize_valid_design_pause_too_early: true
    require_semantic_interpretation_of_diffs: true
    
At the end, briefly explain:
- which parts of `Codex_handoff.md` you followed most directly
- how your implementation preserves ELI authority
- where specialist and repo-alignment signals enter the flow
