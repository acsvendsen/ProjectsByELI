#!/usr/bin/env python3
import argparse, ast, datetime as dt, hashlib, json, os, pathlib, re, sqlite3, subprocess, time, urllib.request

BASE = pathlib.Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE / "config" / "config.yaml"
DB_PATH = BASE / "state" / "memory.db"
STATE_DIR = BASE / "state"
RUNTIME_STATE_PATH = STATE_DIR / "runtime_state.json"
OPERATOR_GUIDANCE_PATH = STATE_DIR / "operator_guidance.json"
ACTION_INBOX_PATH = STATE_DIR / "action_inbox.json"
ACTION_MEMORY_PATH = STATE_DIR / "action_memory.json"
SCORECARD_STATE_PATH = STATE_DIR / "project_scorecard.json"
REFLECT_STATE_PATH = STATE_DIR / "reflect_state.json"
PROMPTS_DIR = BASE / "prompts"
DREAM_DOMAINS = [
    "subtitle placement",
    "confidence display",
    "memory/cache policy",
    "phone/cloud boundary",
    "visual hierarchy",
]
DECISION_VERBS = ("define", "choose", "set", "limit", "compare", "use", "keep", "route", "cache", "show", "hide", "prefer")
PHONE_CLOUD_TASK_PATTERNS = {
    "live subtitle processing": [r'live subtitle', r'subtitle processing', r'subtitle rendering'],
    "transcript cleanup": [r'transcript cleanup', r'clean up transcript', r'transcript post[- ]processing'],
    "face/name recall lookup": [r'face/?name recall', r'face and name recall', r'face/name lookup', r'name recall lookup'],
    "memory archive sync": [r'memory archive sync', r'archive sync', r'archive upload'],
    "conversation snapshot upload": [r'conversation snapshot upload', r'conversation snapshot', r'snapshot upload'],
}
EVIDENCE_SOURCE_WEIGHTS = {
    'reports': 1.0,
    'eli_docs': 1.0,
    'code_config': 1.25,
    'runtime_truth': 1.5,
}
FIELD_CONCEPT_PATTERNS = {
    'attractors': {
        'subtitle_clarity': [r'subtitle', r'caption', r'transcript', r'readable', r'placement'],
        'memory_trust': [r'memory', r'face/?name', r'name recall', r'lookup trust', r'entity-linking', r'person-memory'],
        'low_friction_assistance': [r'low-friction', r'one-line', r'assistive', r'discreet help', r'frame touch'],
    },
    'tensions': {
        'privacy_vs_usefulness': [r'privacy', r'retention', r'capture', r'usefulness', r'trustworthiness'],
        'latency_vs_richness': [r'latency', r'richness', r'phone/cloud', r'cloud', r'local', r'slower processing'],
        'discreet_ux_vs_visual_clarity': [r'discreet', r'visual clarity', r'readable', r'prominen', r'socially acceptable'],
    },
    'modes': {
        'core_deepening': [r'core deepening', r'subtitle quality', r'memory trust', r'confidence display', r'visual hierarchy'],
        'constraint_pressure': [r'battery', r'thermal', r'latency', r'privacy', r'usability', r'constraint'],
        'implementation_grounding': [r'build', r'runtime', r'xcode', r'implementation', r'code', r'config'],
    },
}
DORMANT_IDEA_TYPE_VALUES = (
    'low_value',
    'premature_but_promising',
    'constraint_blocked',
    'mode_suppressed',
)
REFLECT_EXPECTED_TOP_LEVEL_KEYS = (
    'reflection_summary',
    'resonance_signals',
    'strengthening_attractors',
    'intensifying_tensions',
    'under_attended_tensions',
    'possible_drift',
    'dormant_ideas_worth_reactivation',
    'contradiction_persistence',
    'over_dominant_attractors',
    'cooling_candidates',
    'under_attended_recurring_tensions',
    'neglected_persistent_tensions',
    'reinforcement_loops',
    'counterweight_awareness',
    'field_imbalance_patterns',
    'repo_change_candidates',
    'repo_alignment_observations',
    'field_diff_alignment_patterns',
    'specialist_consultation_decisions',
    'specialist_consultation_evaluations',
    'action_direction_judgments',
    'dormant_idea_returns',
    'suggested_mode_shifts',
    'field_deltas',
)
REPO_ALIGNMENT_CLASSIFICATIONS = (
    'aligned',
    'productive_resistance',
    'misaligned',
    'field_neglecting',
    'cosmetic_only',
)
SPECIALIST_EVALUATION_VALUES = (
    'accept',
    'partial_accept',
    'reject',
    'defer_for_competitive_review',
)
SPECIALIST_TEXT_PATTERNS = {
    'embedded_linux_specialist_v1': [
        r'embedded', r'linux', r'raspberry', r'systemd', r'camera', r'device', r'gpio', r'i2c', r'spi', r'uart',
    ],
    'controls_specialist_v1': [
        r'bldc', r'foc', r'pid', r'dq', r'encoder', r'telemetry', r'loop tuning', r'parameter estimation', r'fault logic',
    ],
    'visualization_specialist_v1': [
        r'visual', r'ui', r'ux', r'display', r'placement', r'layout', r'hierarchy', r'overlay', r'prominence', r'render',
    ],
    'report_specialist_v1': [
        r'report', r'pdf', r'document', r'chart', r'markdown', r'explanation', r'packaging',
    ],
    'code_architecture_specialist_v1': [
        r'architecture', r'orchestration', r'refactor', r'state', r'schema', r'policy', r'boundary', r'cache', r'workflow',
    ],
}
ACTION_SPECIALIST_HINTS = {
    'subtitle placement': {
        'visualization_specialist_v1': 0.74,
        'code_architecture_specialist_v1': 0.28,
    },
    'confidence display': {
        'visualization_specialist_v1': 0.78,
        'code_architecture_specialist_v1': 0.24,
    },
    'memory/cache policy': {
        'code_architecture_specialist_v1': 0.76,
        'embedded_linux_specialist_v1': 0.16,
    },
    'phone/cloud boundary': {
        'code_architecture_specialist_v1': 0.8,
        'embedded_linux_specialist_v1': 0.18,
    },
    'visual hierarchy': {
        'visualization_specialist_v1': 0.82,
        'code_architecture_specialist_v1': 0.2,
    },
}
DOMAIN_TARGET_PATTERNS = {
    "subtitle placement": {
        "subtitle position rule": [r'fixed position', r'position rule', r'bottom', r'top center', r'placement rule', r'placement mode'],
        "confidence-state placement rule": [r'confidence state', r'high confidence', r'medium confidence', r'low confidence'],
        "fallback placement rule": [r'fallback'],
    },
    "confidence display": {
        "confidence format": [r'confidence format', r'format candidate', r'label and a short reason', r'label \+ short reason', r'label plus reason'],
        "confidence label scale": [r'confidence label', r'label for v1', r'"high"', r'"low"', r'"uncertain"'],
        "numeric score usage": [r'numeric score', r'score [0-9]', r'0\.[0-9]+'],
        "short reason style": [r'short reason', r'weak match', r'seen recently'],
    },
    "memory/cache policy": {
        "cache size limit": [r'cache size limit', r'local cache size', r'[0-9]+ entries'],
        "eviction rule": [r'eviction rule', r'evict', r'lru'],
        "recency threshold": [r'recency threshold', r'last 24 hours', r'last 30 days', r'recent'],
        "lookup retention rule": [r'lookup retention', r'retention rule'],
        "entity-linking rule": [r'entity-linking rule', r'attach new evidence', r'existing person-memory object'],
    },
    "phone/cloud boundary": {
        "task boundary": [r'phone-local', r'cloud fallback', r'phone/cloud boundary', r'falls back to cloud', r'stays local'],
    },
    "visual hierarchy": {
        "priority rule": [r'priority rule', r'take precedence', r'higher precedence', r'priority'],
        "suppression rule": [r'suppress', r'suppressed'],
        "coexistence rule": [r'coexistence', r'non-overlapping', r'shown together'],
        "prominence rule": [r'prominent', r'prominence'],
    },
}
ACTION_DIRECTION_LINKS = {
    "subtitle placement": {
        "attractors": ["subtitle_clarity"],
        "tensions": ["latency_vs_richness", "discreet_ux_vs_visual_clarity"],
        "modes": ["core_deepening", "implementation_grounding"],
        "constraints": ["core_deepening_over_sprawl"],
    },
    "confidence display": {
        "attractors": ["subtitle_clarity", "memory_trust"],
        "tensions": ["discreet_ux_vs_visual_clarity", "latency_vs_richness"],
        "modes": ["core_deepening", "implementation_grounding"],
        "constraints": ["core_deepening_over_sprawl"],
    },
    "memory/cache policy": {
        "attractors": ["memory_trust"],
        "tensions": ["privacy_vs_usefulness", "latency_vs_richness"],
        "modes": ["core_deepening", "implementation_grounding"],
        "constraints": ["phone_first_runtime", "core_deepening_over_sprawl"],
    },
    "phone/cloud boundary": {
        "attractors": ["subtitle_clarity", "memory_trust"],
        "tensions": ["latency_vs_richness", "privacy_vs_usefulness"],
        "modes": ["constraint_pressure", "implementation_grounding"],
        "constraints": ["phone_first_runtime", "core_deepening_over_sprawl"],
    },
    "visual hierarchy": {
        "attractors": ["subtitle_clarity", "low_friction_assistance"],
        "tensions": ["discreet_ux_vs_visual_clarity"],
        "modes": ["core_deepening"],
        "constraints": ["core_deepening_over_sprawl"],
    },
}

DEFAULT_FIELD_SCAFFOLDS = {
    "attractors": {
        "field": "attractors",
        "version": "eli_v2_phase1",
        "updated_at": "2026-04-06T00:00:00",
        "items": [
            {
                "id": "subtitle_clarity",
                "label": "Real-time subtitle clarity",
                "summary": "Keep subtitles clear, fast, and stable enough that the wearer can trust them in live conversation.",
                "strength": "high",
                "score": 0.82,
            },
            {
                "id": "memory_trust",
                "label": "Trustworthy memory support",
                "summary": "Remember names, faces, and prior context without pretending certainty or creating corrupted recall.",
                "strength": "high",
                "score": 0.78,
            },
            {
                "id": "low_friction_assistance",
                "label": "Low-friction assistance",
                "summary": "Deliver one-line help and visible support without creating command overhead or social awkwardness.",
                "strength": "medium",
                "score": 0.68,
            },
        ],
    },
    "tensions": {
        "field": "tensions",
        "version": "eli_v2_phase1",
        "updated_at": "2026-04-06T00:00:00",
        "items": [
            {
                "id": "privacy_vs_usefulness",
                "label": "Privacy vs usefulness",
                "summary": "Helpful assistive behavior should not quietly slide into invasive capture or retention.",
                "pressure": "high",
                "score": 0.76,
            },
            {
                "id": "latency_vs_richness",
                "label": "Latency vs richness",
                "summary": "The system should provide timely help without overloading the runtime with richer but slower processing.",
                "pressure": "high",
                "score": 0.79,
            },
            {
                "id": "discreet_ux_vs_visual_clarity",
                "label": "Discreet UX vs visual clarity",
                "summary": "Display behavior should remain socially acceptable while still being readable in motion and noise.",
                "pressure": "medium",
                "score": 0.67,
            },
        ],
    },
    "constraints": {
        "field": "constraints",
        "version": "eli_v2_phase1",
        "updated_at": "2026-04-06T00:00:00",
        "items": [
            {
                "id": "frame_touch_only_v1",
                "label": "Frame-touch-only V1",
                "summary": "V1 explicit interaction should happen through frame touches, not voice commands.",
                "type": "hard",
            },
            {
                "id": "phone_first_runtime",
                "label": "Phone-first runtime",
                "summary": "Heavy processing should primarily happen on the phone, with cloud optional where clearly justified.",
                "type": "hard",
            },
            {
                "id": "core_deepening_over_sprawl",
                "label": "Core-deepening over sprawl",
                "summary": "Prefer work that improves subtitle quality, memory trust, and visual UX over broad feature expansion.",
                "type": "guiding",
            },
        ],
    },
    "modes": {
        "field": "modes",
        "version": "eli_v2_phase1",
        "updated_at": "2026-04-06T00:00:00",
        "current_mode": "core_deepening",
        "items": [
            {
                "id": "core_deepening",
                "label": "Core Deepening",
                "summary": "Bias toward subtitle, memory, confidence, and architecture improvements that increase daily-use value.",
                "score": 0.84,
            },
            {
                "id": "constraint_pressure",
                "label": "Constraint Pressure",
                "summary": "Surface battery, latency, privacy, and usability limits early so weak directions are killed quickly.",
                "score": 0.58,
            },
            {
                "id": "implementation_grounding",
                "label": "Implementation Grounding",
                "summary": "Reason from actual repo files, app docs, and build truth instead of generic ideation.",
                "score": 0.74,
            },
        ],
    },
}


def parse_yaml_like(path):
    text = path.read_text(encoding='utf-8')
    data = {}
    current = None
    for raw in text.splitlines():
        line = raw.rstrip('\n')
        if not line.strip() or line.strip().startswith('#'):
            continue
        if re.match(r'^\S[^:]+:\s*$', line):
            key = line.split(':', 1)[0].strip()
            data[key] = []
            current = key
        elif re.match(r'^\s*-\s+', line) and current:
            data[current].append(line.split('-',1)[1].strip())
        elif ':' in line and not line.startswith('  '):
            k, v = line.split(':', 1)
            k, v = k.strip(), v.strip()
            if v.lower() in ('true','false'):
                data[k] = v.lower() == 'true'
            else:
                try:
                    data[k] = int(v)
                except Exception:
                    data[k] = v
            current = None
    for section in ('ollama','cycles','notifications'):
        m = re.search(rf'{section}:\n((?:\s{{2,}}.+\n?)*)', text)
        if m:
            sec = {}
            for line in m.group(1).splitlines():
                s = line.strip()
                if not s or ':' not in s:
                    continue
                k, v = s.split(':', 1)
                v = v.strip()
                if v.lower() in ('true','false'):
                    sec[k] = v.lower() == 'true'
                else:
                    try:
                        sec[k] = int(v)
                    except Exception:
                        sec[k] = v
            data[section] = sec
    return data

CFG = parse_yaml_like(CONFIG_PATH)


def cfg_path_value(key, default):
    raw = CFG.get(key, default)
    if not raw:
        raw = default
    path = pathlib.Path(str(raw))
    if not path.is_absolute():
        path = BASE / path
    return path


def cfg_path_list(key, default_items):
    raw_items = CFG.get(key, default_items)
    if not isinstance(raw_items, list) or not raw_items:
        raw_items = default_items
    paths = []
    for raw in raw_items:
        path = pathlib.Path(str(raw))
        if not path.is_absolute():
            path = BASE / path
        paths.append(path)
    return paths


PROJECT_SLUG = str(CFG.get('project_name', 'smart_glasses'))
PROJECT_DISPLAY_NAME = str(CFG.get('project_display_name', PROJECT_SLUG.replace('_', ' ').title()))
project_runtime_root = CFG.get('project_runtime_root')
if project_runtime_root:
    PROJECT_DIR = pathlib.Path(str(project_runtime_root))
else:
    PROJECT_DIR = BASE / "projects" / PROJECT_SLUG
REPORTS_DIR = PROJECT_DIR / "reports"
CORE_DIR = PROJECT_DIR / "core"
FIELD_V2_DIR = CORE_DIR / "field_v2"
SCORECARD_CONFIG_PATH = CORE_DIR / "project_scorecard.json"
PROJECT_STATE_DIR = PROJECT_DIR / "state"
FIELD_DELTA_HISTORY_PATH = PROJECT_STATE_DIR / "field_delta_history.json"
ENGINE_STATE_DIR = BASE / "state"
STATE_DIR = PROJECT_STATE_DIR
RUNTIME_STATE_PATH = STATE_DIR / "runtime_state.json"
OPERATOR_GUIDANCE_PATH = STATE_DIR / "operator_guidance.json"
ACTION_INBOX_PATH = STATE_DIR / "action_inbox.json"
ACTION_MEMORY_PATH = STATE_DIR / "action_memory.json"
SCORECARD_STATE_PATH = STATE_DIR / "project_scorecard.json"
REFLECT_STATE_PATH = STATE_DIR / "reflect_state.json"
INBOX_DIR = PROJECT_DIR / "inbox"
LINKS_DIR = PROJECT_DIR / "links"
REPO_LINK_DIR = LINKS_DIR / "repo"
REPO_ELI_DIR = REPO_LINK_DIR / "ELI"
COGNITION_SCHEMA_PATH = CORE_DIR / "cognition_schema.yaml"
SPECIALIST_REGISTRY_PATH = CORE_DIR / "specialist_registry.yaml"
SPECIALIST_ROUTING_POLICY_PATH = CORE_DIR / "specialist_routing_policy.yaml"
BUILD_SUMMARY_PATH = ENGINE_STATE_DIR / str(CFG.get('build_summary_filename', 'transcriptlab_xcode_build_summary.md'))
BUILD_CAPTURE_SCRIPT_PATH = cfg_path_value('build_capture_script', 'scripts/capture_transcriptlab_build.py')
SPECIALIST_TRUST_MEMORY_PATH = PROJECT_STATE_DIR / "specialist_trust_memory.json"
SPECIALIST_CONSULTATION_HISTORY_PATH = PROJECT_STATE_DIR / "specialist_consultation_history.json"
PROJECT_ELI_CONTEXT_PATHS = cfg_path_list('persistent_eli_context_paths', [
    str(REPO_ELI_DIR / "attractors.md"),
    str(REPO_ELI_DIR / "tensions.md"),
    str(REPO_ELI_DIR / "constraints" / "v1_real_world_limits.md"),
    str(REPO_ELI_DIR / "decisions" / "v1_architecture_direction.md"),
    str(REPO_ELI_DIR / "inbox" / "current_unknowns.md"),
    str(REPO_ELI_DIR / "modes" / "current_mode.md"),
])
PERSISTENT_APP_CONTEXT_PATHS = cfg_path_list('persistent_app_context_paths', [
    str(REPO_LINK_DIR / "app" / "ios" / "TranscriptLab" / "README.md"),
    str(REPO_LINK_DIR / "app" / "shared" / "transcript" / "README.md"),
])
BUILD_WATCH_ROOTS = cfg_path_list('build_watch_roots', [
    str(REPO_LINK_DIR / "app" / "ios" / "TranscriptLab"),
    str(REPO_LINK_DIR / "app" / "shared" / "transcript"),
])
IGNORE_DIR_NAMES = set(CFG.get('ignore_dirs', [
    ".git",
    "build",
    "DerivedData",
    ".swiftpm",
    ".idea",
    ".vscode",
    "node_modules",
    "__pycache__",
]))
ALLOWED_SUFFIXES = set(CFG.get('scan_extensions', [".md", ".txt", ".swift", ".json", ".yaml", ".yml"]))
FIELD_V2_FILES = {
    "attractors": FIELD_V2_DIR / "attractors.json",
    "tensions": FIELD_V2_DIR / "tensions.json",
    "constraints": FIELD_V2_DIR / "constraints.json",
    "modes": FIELD_V2_DIR / "modes.json",
}

DEFAULT_COGNITION_SCHEMA = {
    'specialist_consultation': {
        'enabled': True,
        'authority': {
            'eli_remains_primary_judge': True,
            'specialist_outputs_advisory_by_default': True,
            'require_eli_evaluation_before_integration': True,
            'forbid_direct_specialist_state_mutation': True,
        },
        'selection': {
            'minimum_expected_gain': 0.12,
            'high_uncertainty_threshold': 0.65,
            'competitive_consultation_threshold': 0.46,
            'minimum_semantic_match': 0.45,
            'minimum_constraint_fidelity': 0.72,
            'max_hallucination_risk_for_primary_use': 0.45,
        },
        'modes': {
            'advisory': True,
            'delegated_drafting': True,
            'competitive': True,
            'instrumental': True,
        },
        'safeguards': {
            'do_not_override_field_logic': True,
            'do_not_override_reflect_authority': True,
            'do_not_override_action_judgment': True,
            'do_not_reframe_project_identity': True,
            'require_consultation_audit_trail': True,
            'require_partial_accept_or_reject_path': True,
        },
    },
    'control': {
        'attractor_saturation': {
            'soft_start_score': 0.82,
            'strong_start_score': 0.92,
            'soft_damping': 0.72,
            'strong_damping': 0.38,
            'floor_multiplier': 0.08,
            'min_source_types_above_soft_start': 2,
            'min_source_types_above_strong_start': 3,
            'high_score_missing_runtime_or_code_penalty': 0.6,
        },
        'diversity_gating': {
            'recent_history_window': 16,
            'same_pattern_penalty': 0.7,
            'low_source_type_penalty': 0.78,
            'low_semantic_variation_penalty': 0.82,
            'low_time_separation_penalty': 0.82,
            'minimum_minutes_between_reinforcement': 45,
            'minimum_distinct_reasons': 2,
        },
        'recurrence_thresholds': {
            'contradiction_resurfacing_min': 2,
            'overdominant_attractor_score': 0.9,
            'under_attended_recurring_tension_score': 3.0,
            'reinforcement_loop_support_min': 4,
            'reinforcement_loop_weighted_score_min': 4.0,
        },
        'counterweights': {
            'attention_tension_score': 0.72,
            'attention_resonance_score': 2.2,
            'persistence_levels': ['medium', 'high'],
            'links': {
                'subtitle_clarity': ['latency_vs_richness', 'discreet_ux_vs_visual_clarity'],
                'memory_trust': ['privacy_vs_usefulness', 'latency_vs_richness'],
                'low_friction_assistance': ['discreet_ux_vs_visual_clarity', 'privacy_vs_usefulness'],
            },
        },
        'controlled_decay': {
            'cooling_score_threshold': 0.92,
            'low_diversity_max_source_types': 1,
            'stale_reinforcement_support_min': 4,
            'stale_reason_variant_max': 1,
            'stale_source_pattern_max': 1,
            'healthy_reinforcement_min_source_types': 2,
            'healthy_reinforcement_min_weighted_score': 3.2,
            'cooling_delta': -0.012,
        },
        'rebalancing': {
            'neglected_tension_score_threshold': 0.72,
            'neglected_tension_weighted_score_min': 3.0,
            'neglected_tension_delta': 0.012,
            'neglected_update_cap': 1,
            'max_rebalancing_deltas_per_cycle': 2,
            'imbalance_attractor_score_threshold': 0.84,
            'imbalance_support_min': 4,
            'imbalance_persistence_levels': ['medium', 'high'],
        },
        'dormant_returns': {
            'promising_evidence_min': 0.72,
            'promising_pull_min': 0.58,
            'constraint_release_resistance_max': 0.62,
            'mode_return_modes': ['core_deepening'],
            'return_delta': 0.01,
            'max_target_score_for_return_delta': 0.78,
        },
        'grounding_hold': {
            'enabled': True,
            'meaningful_alignment_min': 0.58,
            'meaningful_pull_min': 0.42,
            'repeat_appearance_min': 2,
            'repeat_consecutive_min': 2,
            'weak_repo_grounding_max': 0.22,
            'weak_source_diversity_max': 1,
            'material_repo_grounding_delta': 0.16,
            'material_evidence_delta': 0.1,
            'material_pull_delta': 0.08,
            'material_resistance_drop': 0.08,
            'field_repeat_window': 12,
            'field_min_weighted_evidence_gain': 0.22,
            'field_min_added_source_types': 1,
        },
        'phase7_repo_alignment': {
            'enabled': True,
            'diff_alignment': {
                'align_weight': 1.0,
                'productive_resistance_weight': 0.75,
                'misalignment_weight': -0.85,
                'neglect_weight': -0.65,
                'cosmetic_only_weight': -0.3,
            },
            'action_coupling': {
                'reward_diff_backed_actions': True,
                'damp_talk_without_change': True,
                'enable_dormant_return_on_structural_progress': True,
            },
            'reflect_grounding': {
                'require_diff_summary': True,
                'require_alignment_observations': True,
                'require_resistance_observations': True,
            },
            'safeguards': {
                'do_not_equate_any_diff_with_progress': True,
                'do_not_penalize_valid_design_pause_too_early': True,
                'require_semantic_interpretation_of_diffs': True,
            },
        },
    }
}

DEFAULT_COGNITION_SCHEMA_TEXT = """specialist_consultation:
  enabled: true
  authority:
    eli_remains_primary_judge: true
    specialist_outputs_advisory_by_default: true
    require_eli_evaluation_before_integration: true
    forbid_direct_specialist_state_mutation: true
  selection:
    minimum_expected_gain: 0.12
    high_uncertainty_threshold: 0.65
    competitive_consultation_threshold: 0.46
    minimum_semantic_match: 0.45
    minimum_constraint_fidelity: 0.72
    max_hallucination_risk_for_primary_use: 0.45
  modes:
    advisory: true
    delegated_drafting: true
    competitive: true
    instrumental: true
  safeguards:
    do_not_override_field_logic: true
    do_not_override_reflect_authority: true
    do_not_override_action_judgment: true
    do_not_reframe_project_identity: true
    require_consultation_audit_trail: true
    require_partial_accept_or_reject_path: true
control:
  attractor_saturation:
    soft_start_score: 0.82
    strong_start_score: 0.92
    soft_damping: 0.72
    strong_damping: 0.38
    floor_multiplier: 0.08
    min_source_types_above_soft_start: 2
    min_source_types_above_strong_start: 3
    high_score_missing_runtime_or_code_penalty: 0.6
  diversity_gating:
    recent_history_window: 16
    same_pattern_penalty: 0.7
    low_source_type_penalty: 0.78
    low_semantic_variation_penalty: 0.82
    low_time_separation_penalty: 0.82
    minimum_minutes_between_reinforcement: 45
    minimum_distinct_reasons: 2
  recurrence_thresholds:
    contradiction_resurfacing_min: 2
    overdominant_attractor_score: 0.9
    under_attended_recurring_tension_score: 3.0
    reinforcement_loop_support_min: 4
    reinforcement_loop_weighted_score_min: 4.0
  counterweights:
    attention_tension_score: 0.72
    attention_resonance_score: 2.2
    persistence_levels:
      - medium
      - high
    links:
      subtitle_clarity:
        - latency_vs_richness
        - discreet_ux_vs_visual_clarity
      memory_trust:
        - privacy_vs_usefulness
        - latency_vs_richness
      low_friction_assistance:
        - discreet_ux_vs_visual_clarity
        - privacy_vs_usefulness
  controlled_decay:
    cooling_score_threshold: 0.92
    low_diversity_max_source_types: 1
    stale_reinforcement_support_min: 4
    stale_reason_variant_max: 1
    stale_source_pattern_max: 1
    healthy_reinforcement_min_source_types: 2
    healthy_reinforcement_min_weighted_score: 3.2
    cooling_delta: -0.012
  rebalancing:
    neglected_tension_score_threshold: 0.72
    neglected_tension_weighted_score_min: 3.0
    neglected_tension_delta: 0.012
    neglected_update_cap: 1
    max_rebalancing_deltas_per_cycle: 2
    imbalance_attractor_score_threshold: 0.84
    imbalance_support_min: 4
    imbalance_persistence_levels:
      - medium
      - high
  dormant_returns:
    promising_evidence_min: 0.72
    promising_pull_min: 0.58
    constraint_release_resistance_max: 0.62
    mode_return_modes:
      - core_deepening
    return_delta: 0.01
    max_target_score_for_return_delta: 0.78
  grounding_hold:
    enabled: true
    meaningful_alignment_min: 0.58
    meaningful_pull_min: 0.42
    repeat_appearance_min: 2
    repeat_consecutive_min: 2
    weak_repo_grounding_max: 0.22
    weak_source_diversity_max: 1
    material_repo_grounding_delta: 0.16
    material_evidence_delta: 0.1
    material_pull_delta: 0.08
    material_resistance_drop: 0.08
    field_repeat_window: 12
    field_min_weighted_evidence_gain: 0.22
    field_min_added_source_types: 1
  phase7_repo_alignment:
    enabled: true
    diff_alignment:
      align_weight: 1.0
      productive_resistance_weight: 0.75
      misalignment_weight: -0.85
      neglect_weight: -0.65
      cosmetic_only_weight: -0.3
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
"""


def deep_copy_data(value):
    return json.loads(json.dumps(value))


def parse_scalar_value(raw):
    text = raw.strip()
    if not text:
        return ''
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        return text[1:-1]
    lower = text.lower()
    if lower in ('true', 'false'):
        return lower == 'true'
    if lower in ('null', 'none', '~'):
        return None
    try:
        if re.match(r'^-?\d+$', text):
            return int(text)
        if re.match(r'^-?\d+\.\d+$', text):
            return float(text)
    except Exception:
        pass
    return text


def parse_simple_yaml_tree(text):
    lines = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        lines.append(line)
    root = {}
    stack = [(-1, root)]
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        indent = len(line) - len(line.lstrip(' '))
        stripped = line.strip()
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        container = stack[-1][1]
        if stripped.startswith('- '):
            if isinstance(container, list):
                container.append(parse_scalar_value(stripped[2:]))
            idx += 1
            continue
        if ':' not in stripped or not isinstance(container, dict):
            idx += 1
            continue
        key, rest = stripped.split(':', 1)
        key = key.strip()
        rest = rest.strip()
        if rest:
            container[key] = parse_scalar_value(rest)
            idx += 1
            continue
        next_indent = None
        next_stripped = ''
        look_ahead = idx + 1
        while look_ahead < len(lines):
            next_line = lines[look_ahead]
            next_indent = len(next_line) - len(next_line.lstrip(' '))
            next_stripped = next_line.strip()
            break
        if next_indent is not None and next_indent > indent and next_stripped.startswith('- '):
            new_container = []
        else:
            new_container = {}
        container[key] = new_container
        stack.append((indent, new_container))
        idx += 1
    return root


def deep_merge_dict(base, override):
    merged = deep_copy_data(base)
    if not isinstance(override, dict):
        return merged
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def ensure_cognition_schema():
    COGNITION_SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not COGNITION_SCHEMA_PATH.exists():
        COGNITION_SCHEMA_PATH.write_text(DEFAULT_COGNITION_SCHEMA_TEXT.strip() + '\n', encoding='utf-8')


def load_cognition_schema():
    ensure_cognition_schema()
    try:
        raw = parse_simple_yaml_tree(COGNITION_SCHEMA_PATH.read_text(encoding='utf-8'))
    except Exception:
        raw = {}
    return deep_merge_dict(DEFAULT_COGNITION_SCHEMA, raw)


def cognition_control_config(section):
    return load_cognition_schema().get('control', {}).get(section, {})


def specialist_consultation_config(schema):
    return schema.get('specialist_consultation', {})


def parse_specialist_registry(path):
    if not path.exists():
        return {'version': 1, 'specialists': []}
    version = 1
    specialists = []
    current = None
    current_section = ''
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        indent = len(line) - len(line.lstrip(' '))
        if indent == 0 and stripped.startswith('version:'):
            version = safe_int(parse_scalar_value(stripped.split(':', 1)[1]), 1)
            continue
        if indent == 0 and stripped == 'specialists:':
            continue
        if indent == 2 and stripped.startswith('- id:'):
            if current:
                specialists.append(current)
            current = {'id': parse_scalar_value(stripped.split(':', 1)[1])}
            current_section = ''
            continue
        if current is None:
            continue
        if indent == 4:
            if stripped.endswith(':'):
                key = stripped[:-1].strip()
                current[key] = {} if key == 'trust_defaults' else []
                current_section = key
            elif ':' in stripped:
                key, value = stripped.split(':', 1)
                current[key.strip()] = parse_scalar_value(value)
                current_section = ''
            continue
        if indent == 6 and current_section:
            bucket = current.get(current_section)
            if isinstance(bucket, list) and stripped.startswith('- '):
                bucket.append(parse_scalar_value(stripped[2:]))
            elif isinstance(bucket, dict) and ':' in stripped:
                key, value = stripped.split(':', 1)
                bucket[key.strip()] = parse_scalar_value(value)
    if current:
        specialists.append(current)
    for specialist in specialists:
        for key in ('domains', 'input_types', 'output_types', 'strengths', 'weaknesses', 'consultation_modes'):
            values = specialist.get(key, [])
            if not isinstance(values, list):
                specialist[key] = [values] if values else []
        if not isinstance(specialist.get('trust_defaults'), dict):
            specialist['trust_defaults'] = {}
        specialist['enabled'] = bool(specialist.get('enabled', True))
    return {'version': version, 'specialists': specialists}


def load_specialist_registry():
    return parse_specialist_registry(SPECIALIST_REGISTRY_PATH)


def load_specialist_routing_policy():
    default = {
        'version': 1,
        'selection_policy': {
            'preserve_eli_authority': True,
            'consultation_requires_positive_expected_gain': True,
            'default_mode': 'advisory',
            'allow_no_consultation': True,
            'reject_specialist_if_conflicts_with_project_constraints': True,
            'require_eli_post_consultation_evaluation': True,
            'specialist_outputs_are_advisory_by_default': True,
        },
        'signals': {
            'semantic_match_weight': 0.25,
            'trust_memory_weight': 0.2,
            'current_uncertainty_weight': 0.2,
            'artifact_requirement_weight': 0.15,
            'historical_success_weight': 0.1,
            'constraint_fidelity_weight': 0.1,
            'contradiction_risk_weight': -0.1,
            'hallucination_risk_weight': -0.1,
        },
        'thresholds': {
            'minimum_expected_gain': 0.12,
            'high_uncertainty': 0.65,
            'competitive_consultation': 0.46,
            'minimum_constraint_fidelity': 0.72,
            'max_hallucination_risk_for_primary_use': 0.45,
            'minimum_semantic_match': 0.45,
        },
        'consultation_mode_rules': {
            'advisory': {
                'allowed_for': [
                    'architecture_questions',
                    'design_tradeoffs',
                    'critique',
                    'sanity_check',
                    'domain_analysis',
                    'implementation_review',
                    'component_selection_review',
                    'architecture_fork',
                    'component_tradeoff',
                ],
            },
            'delegated_drafting': {
                'allowed_for': [
                    'code_scaffold',
                    'report_draft',
                    'diagram_draft',
                    'artifact_assembly',
                    'schematic_draft',
                    'interface_map',
                    'subsystem_breakdown',
                    'component_shortlist',
                    'diagram_packaging',
                    'report_packaging',
                ],
            },
            'competitive': {
                'allowed_for': [
                    'high_risk_decision',
                    'conflicting_options',
                    'persistent_uncertainty',
                    'unresolved_tradeoff',
                    'architecture_fork',
                    'component_tradeoff',
                ],
            },
            'instrumental': {
                'allowed_for': [
                    'plotting',
                    'rendering',
                    'format_conversion',
                    'simulation',
                    'pdf_packaging',
                    'diagram_packaging',
                    'report_packaging',
                ],
            },
        },
        'build_artifact_bias': {
            'diagrams': {
                'preferred_mode': 'delegated_drafting',
                'preferred_specialists': ['visualization_specialist_v1', 'report_specialist_v1'],
            },
            'schematics': {
                'preferred_mode': 'delegated_drafting',
                'preferred_specialists': ['hardware_implementation_specialist_v1', 'visualization_specialist_v1'],
            },
            'component_shortlists': {
                'preferred_mode': 'advisory',
                'preferred_specialists': ['hardware_implementation_specialist_v1', 'code_architecture_specialist_v1'],
            },
            'interface_maps': {
                'preferred_mode': 'delegated_drafting',
                'preferred_specialists': ['code_architecture_specialist_v1', 'visualization_specialist_v1'],
            },
            'subsystem_breakdowns': {
                'preferred_mode': 'delegated_drafting',
                'preferred_specialists': ['code_architecture_specialist_v1', 'hardware_implementation_specialist_v1'],
            },
            'report_packaging': {
                'preferred_mode': 'delegated_drafting',
                'preferred_specialists': ['report_specialist_v1', 'visualization_specialist_v1'],
            },
        },
        'safeguards': {
            'do_not_override_field_logic': True,
            'do_not_override_reflect_authority': True,
            'do_not_override_action_judgment': True,
            'do_not_reframe_project_identity': True,
            'require_auditable_consultation_history': True,
            'require_partial_accept_or_reject_path': True,
            'require_high_uncertainty_for_competitive': True,
            'require_runner_up_for_competitive': True,
            'minimum_expected_gain_margin_for_competitive': 0.06,
            'max_top_runner_gap_for_competitive': 0.12,
            'artifact_generation_not_authoritative_reasoning': True,
            'artifact_generation_requires_eli_evaluation': True,
        },
    }
    if not SPECIALIST_ROUTING_POLICY_PATH.exists():
        return default
    try:
        raw = parse_simple_yaml_tree(SPECIALIST_ROUTING_POLICY_PATH.read_text(encoding='utf-8'))
    except Exception:
        raw = {}
    return deep_merge_dict(default, raw)


def render_cognition_schema_context(schema):
    control = schema.get('control', {})
    lines = ['# Cognition Control Schema']
    specialist = schema.get('specialist_consultation', {})
    specialist_selection = specialist.get('selection', {})
    lines.append('## Specialist Consultation')
    lines.append(
        f"- enabled: {specialist.get('enabled')} | minimum_expected_gain: {specialist_selection.get('minimum_expected_gain')} | high_uncertainty_threshold: {specialist_selection.get('high_uncertainty_threshold')} | competitive_consultation_threshold: {specialist_selection.get('competitive_consultation_threshold')}"
    )
    saturation = control.get('attractor_saturation', {})
    lines.append('## Attractor Saturation')
    lines.append(
        f"- soft_start_score: {saturation.get('soft_start_score')} | strong_start_score: {saturation.get('strong_start_score')} | floor_multiplier: {saturation.get('floor_multiplier')}"
    )
    diversity = control.get('diversity_gating', {})
    lines.append('## Diversity Gating')
    lines.append(
        f"- recent_history_window: {diversity.get('recent_history_window')} | minimum_minutes_between_reinforcement: {diversity.get('minimum_minutes_between_reinforcement')} | minimum_distinct_reasons: {diversity.get('minimum_distinct_reasons')}"
    )
    counterweights = control.get('counterweights', {})
    lines.append('## Counterweights')
    for attractor_id, linked in counterweights.get('links', {}).items():
        lines.append(f"- {attractor_id}: {', '.join(linked)}")
    decay = control.get('controlled_decay', {})
    lines.append('## Controlled Decay')
    lines.append(
        f"- cooling_score_threshold: {decay.get('cooling_score_threshold')} | low_diversity_max_source_types: {decay.get('low_diversity_max_source_types')} | cooling_delta: {decay.get('cooling_delta')}"
    )
    rebalancing = control.get('rebalancing', {})
    lines.append('## Rebalancing')
    lines.append(
        f"- neglected_tension_score_threshold: {rebalancing.get('neglected_tension_score_threshold')} | neglected_tension_delta: {rebalancing.get('neglected_tension_delta')} | max_rebalancing_deltas_per_cycle: {rebalancing.get('max_rebalancing_deltas_per_cycle')}"
    )
    dormant_returns = control.get('dormant_returns', {})
    lines.append('## Dormant Returns')
    lines.append(
        f"- promising_pull_min: {dormant_returns.get('promising_pull_min')} | constraint_release_resistance_max: {dormant_returns.get('constraint_release_resistance_max')} | return_delta: {dormant_returns.get('return_delta')}"
    )
    grounding_hold = control.get('grounding_hold', {})
    lines.append('## Grounding Hold Discipline')
    lines.append(
        f"- enabled: {grounding_hold.get('enabled')} | meaningful_alignment_min: {grounding_hold.get('meaningful_alignment_min')} | meaningful_pull_min: {grounding_hold.get('meaningful_pull_min')} | material_repo_grounding_delta: {grounding_hold.get('material_repo_grounding_delta')}"
    )
    repo_alignment = schema.get('phase7_repo_alignment', control.get('phase7_repo_alignment', {}))
    diff_alignment = repo_alignment.get('diff_alignment', {})
    lines.append('## Phase 7 Repo Alignment')
    lines.append(
        f"- enabled: {repo_alignment.get('enabled')} | align_weight: {diff_alignment.get('align_weight')} | productive_resistance_weight: {diff_alignment.get('productive_resistance_weight')} | misalignment_weight: {diff_alignment.get('misalignment_weight')}"
    )
    return '\n'.join(lines) + '\n'


def render_specialist_consultation_context():
    registry = load_specialist_registry()
    policy = load_specialist_routing_policy()
    trust = load_specialist_trust_memory()
    history = load_specialist_consultation_history()
    thresholds = policy.get('thresholds', {})
    artifact_bias = policy.get('build_artifact_bias', {})
    recent_entries = history.get('entries', [])[-4:]
    lines = ['# Specialist Consultation Context']
    lines.append(f"- registry_path: {SPECIALIST_REGISTRY_PATH}")
    lines.append(f"- routing_policy_path: {SPECIALIST_ROUTING_POLICY_PATH}")
    lines.append(f"- trust_memory_path: {SPECIALIST_TRUST_MEMORY_PATH}")
    lines.append(f"- consultation_history_path: {SPECIALIST_CONSULTATION_HISTORY_PATH}")
    lines.append(
        f"- specialists_enabled: {len([item for item in registry.get('specialists', []) if item.get('enabled', True)])} | minimum_expected_gain: {thresholds.get('minimum_expected_gain')} | competitive_consultation: {thresholds.get('competitive_consultation')} | minimum_constraint_fidelity: {thresholds.get('minimum_constraint_fidelity')}"
    )
    if artifact_bias:
        lines.append('- build_artifact_bias:')
        for key, item in artifact_bias.items():
            if not isinstance(item, dict):
                continue
            lines.append(
                f"  - {key}: mode {item.get('preferred_mode', '')} | specialists {', '.join(item.get('preferred_specialists', [])) or 'none'}"
            )
    else:
        lines.append('- build_artifact_bias: none')
    if not recent_entries:
        lines.append('- recent_consultation_history: none')
    else:
        lines.append('- recent_consultation_history:')
        for entry in recent_entries:
            label = entry.get('specialist_label') or entry.get('specialist_id', 'specialist')
            decision = entry.get('decision') or entry.get('eli_evaluation') or entry.get('kind', 'entry')
            lines.append(
                f"  - {entry.get('action_domain', '') or entry.get('action_title', 'unknown')}: {label} | {decision} | mode {entry.get('consultation_mode', '') or 'n/a'}"
            )
    if trust.get('specialists'):
        lines.append('- trust_memory_snapshot:')
        for specialist_id, profile in list(trust.get('specialists', {}).items())[:4]:
            lines.append(
                f"  - {specialist_id}: trust_score {profile.get('trust_score', 0.0)} | historical_success {profile.get('historical_success', 0.5)} | constraint_fidelity {profile.get('constraint_fidelity', 0.0)}"
            )
    return '\n'.join(lines) + '\n'


def ensure_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY, sha256 TEXT, mtime REAL, last_seen TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS memories(id INTEGER PRIMARY KEY AUTOINCREMENT, cycle TEXT, title TEXT, body TEXT, priority INTEGER, confidence REAL, created_at TEXT)")
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS cycle_runs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cycle TEXT,
            started_at TEXT,
            finished_at TEXT,
            status TEXT,
            duration_ms INTEGER,
            changed_files INTEGER,
            report_path TEXT,
            error_text TEXT
        )
        """
    )
    con.commit(); con.close()


def watch_roots():
    roots = [CORE_DIR, INBOX_DIR]
    if REPO_ELI_DIR.exists():
        roots.append(REPO_ELI_DIR)
    if REPO_LINK_DIR.exists():
        roots.append(REPO_LINK_DIR)
    return roots


def should_scan_path(path):
    parts = set(path.parts)
    if parts & IGNORE_DIR_NAMES:
        return False
    if path.is_file() and path.suffix.lower() not in ALLOWED_SUFFIXES:
        return False
    return True


def iter_project_files(root=None):
    count = 0
    maxf = CFG.get('cycles', {}).get('max_files_per_scan', 80)
    files = []
    for watch_root in watch_roots():
        if not watch_root.exists():
            continue
        for p in watch_root.rglob('*'):
            if count >= maxf:
                break
            if not should_scan_path(p):
                continue
            if not p.is_file():
                continue
            files.append(p)
            count += 1
        if count >= maxf:
            break
    for p in sorted(files):
        yield p


def sha256_text(t):
    return hashlib.sha256(t.encode('utf-8', 'ignore')).hexdigest()


def read_file_excerpt(path):
    try:
        txt = path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return ''
    maxc = CFG.get('cycles', {}).get('max_chars_per_file', 10000)
    return txt[:maxc]


def changed_files(root):
    ensure_db()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    changed = []
    now = dt.datetime.now().isoformat(timespec='seconds')
    for p in iter_project_files(root):
        txt = read_file_excerpt(p)
        digest = sha256_text(txt)
        mtime = p.stat().st_mtime
        row = cur.execute('SELECT sha256 FROM files WHERE path=?', (str(p),)).fetchone()
        if not row or row[0] != digest:
            changed.append((p, txt))
            cur.execute('INSERT OR REPLACE INTO files(path, sha256, mtime, last_seen) VALUES(?,?,?,?)', (str(p), digest, mtime, now))
        else:
            cur.execute('UPDATE files SET last_seen=? WHERE path=?', (now, str(p)))
    con.commit(); con.close()
    return changed


def ollama_generate(system_prompt, user_prompt):
    url = CFG['ollama']['base_url'].rstrip('/') + '/api/generate'
    payload = json.dumps({
        'model': CFG['ollama']['model'],
        'system': system_prompt,
        'prompt': user_prompt,
        'stream': False,
    }).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    return data.get('response', '').strip()


def load_prompt(name):
    return (PROMPTS_DIR / f'{name}.txt').read_text(encoding='utf-8')


def core_text():
    return (CORE_DIR / 'core_field.md').read_text(encoding='utf-8')


def persistent_eli_context():
    items = []
    for path in PROJECT_ELI_CONTEXT_PATHS:
        if path.exists():
            items.append((path, read_file_excerpt(path)))
    for path in PERSISTENT_APP_CONTEXT_PATHS:
        if path.exists():
            items.append((path, read_file_excerpt(path)))
    if BUILD_SUMMARY_PATH.exists():
        items.append((BUILD_SUMMARY_PATH, read_file_excerpt(BUILD_SUMMARY_PATH)))
    return items


def default_field_scaffold(name):
    return json.loads(json.dumps(DEFAULT_FIELD_SCAFFOLDS[name]))


def ensure_field_scaffolds():
    FIELD_V2_DIR.mkdir(parents=True, exist_ok=True)
    for name, path in FIELD_V2_FILES.items():
        if path.exists():
            continue
        path.write_text(json.dumps(default_field_scaffold(name), indent=2) + "\n", encoding="utf-8")


def load_field_scaffold(name):
    path = FIELD_V2_FILES[name]
    fallback = default_field_scaffold(name)
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return fallback
    if not isinstance(data, dict):
        return fallback
    if not isinstance(data.get('items'), list):
        data['items'] = fallback['items']
    data.setdefault('field', fallback['field'])
    data.setdefault('version', fallback['version'])
    data.setdefault('updated_at', fallback['updated_at'])
    if name == 'modes':
        data.setdefault('current_mode', fallback.get('current_mode', 'core_deepening'))
    fallback_items = {item.get('id'): item for item in fallback.get('items', []) if item.get('id')}
    for item in data.get('items', []):
        item_id = item.get('id')
        if not item_id or item_id not in fallback_items:
            continue
        template = fallback_items[item_id]
        for key in ('label', 'summary', 'strength', 'pressure', 'type', 'score'):
            if key in template and key not in item:
                item[key] = template[key]
    return data


def save_field_scaffold(name, payload):
    path = FIELD_V2_FILES[name]
    path.parent.mkdir(parents=True, exist_ok=True)
    payload['updated_at'] = now_iso()
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding='utf-8')


def field_layer_snapshot():
    ensure_field_scaffolds()
    return {name: load_field_scaffold(name) for name in FIELD_V2_FILES}


def load_field_delta_history():
    fallback = {"entries": []}
    try:
        data = json.loads(FIELD_DELTA_HISTORY_PATH.read_text(encoding='utf-8'))
    except Exception:
        return fallback
    if not isinstance(data, dict):
        return fallback
    if not isinstance(data.get('entries'), list):
        data['entries'] = []
    return data


def save_field_delta_history(history):
    PROJECT_STATE_DIR.mkdir(parents=True, exist_ok=True)
    history['updated_at'] = now_iso()
    history['entries'] = history.get('entries', [])[-400:]
    FIELD_DELTA_HISTORY_PATH.write_text(json.dumps(history, indent=2) + "\n", encoding='utf-8')


def render_recent_field_delta_context(limit=12):
    history = load_field_delta_history().get('entries', [])
    if not history:
        return '# Recent Field Delta History\n- no prior field deltas recorded\n'
    lines = ['# Recent Field Delta History']
    for entry in history[-limit:]:
        reason = entry.get('reason', '')
        applied = entry.get('applied_delta', 0.0)
        field = entry.get('field', 'unknown')
        target = entry.get('target_id', 'unknown')
        confidence = entry.get('confidence', '')
        lines.append(f"- {field}/{target}: applied_delta={applied}, confidence={confidence}, reason={reason}")
    return '\n'.join(lines) + '\n'


def clamp_number(value, low, high):
    return max(low, min(high, value))


def round_delta(value):
    return round(value, 4)


def safe_float(value, fallback=0.0):
    try:
        return float(value)
    except Exception:
        return fallback


def field_item_index(payload):
    return {item.get('id'): item for item in payload.get('items', []) if item.get('id')}


def delta_support_count(history_entries, field, target_id, direction, limit=16):
    count = 0
    for entry in reversed(history_entries[-limit:]):
        if entry.get('field') != field or entry.get('target_id') != target_id:
            continue
        applied = float(entry.get('applied_delta', 0.0) or 0.0)
        if direction > 0 and applied > 0:
            count += 1
        elif direction < 0 and applied < 0:
            count += 1
    return count


def target_history_entries(history_entries, field, target_id, direction=None, limit=16):
    matches = []
    for entry in history_entries[-limit:]:
        if entry.get('field') != field or entry.get('target_id') != target_id:
            continue
        applied = safe_float(entry.get('applied_delta', 0.0), 0.0)
        if direction is None:
            matches.append(entry)
        elif direction > 0 and applied > 0:
            matches.append(entry)
        elif direction < 0 and applied < 0:
            matches.append(entry)
    return matches


def parse_iso_datetime(value):
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(str(value))
    except Exception:
        return None


def reason_signature(text):
    stopwords = {
        'the', 'and', 'for', 'with', 'from', 'that', 'this', 'into', 'more', 'less', 'than',
        'because', 'while', 'should', 'could', 'would', 'about', 'across', 'still', 'need',
        'keep', 'when', 'what', 'where', 'which', 'exactly', 'reason', 'reflect', 'cycle',
        'project', 'field', 'target', 'delta', 'update',
    }
    tokens = [token for token in re.findall(r'[a-z0-9]+', lower_text(text)) if len(token) > 3 and token not in stopwords]
    return ' '.join(tokens[:6])


def diversity_gate_state(history_entries, field, target_id, direction, current_reason, evidence_profile, schema):
    cfg = schema.get('control', {}).get('diversity_gating', {})
    window = int(cfg.get('recent_history_window', 16) or 16)
    recent = target_history_entries(history_entries, field, target_id, direction, limit=window)
    current_sources = set(evidence_profile.get('source_types', []))
    current_reason_signature = reason_signature(current_reason)
    distinct_source_patterns = set()
    total_source_types = set(current_sources)
    distinct_reasons = set()
    same_pattern_hits = 0
    latest_ts = None
    for entry in recent:
        sources = tuple(sorted(entry.get('evidence_sources', [])))
        if sources:
            distinct_source_patterns.add(sources)
            total_source_types.update(sources)
            if set(sources) == current_sources and current_sources:
                same_pattern_hits += 1
        signature = reason_signature(entry.get('reason', ''))
        if signature:
            distinct_reasons.add(signature)
        ts = parse_iso_datetime(entry.get('timestamp'))
        if ts and (latest_ts is None or ts > latest_ts):
            latest_ts = ts
    if current_reason_signature:
        distinct_reasons.add(current_reason_signature)
    multiplier = 1.0
    notes = []
    if same_pattern_hits >= 2:
        multiplier *= safe_float(cfg.get('same_pattern_penalty', 0.7), 0.7)
        notes.append(f'repeated same-pattern reinforcement ({same_pattern_hits} recent hits)')
    if len(current_sources) < 2 and len(total_source_types) < 2:
        multiplier *= safe_float(cfg.get('low_source_type_penalty', 0.78), 0.78)
        notes.append('source-type diversity is still narrow')
    if recent and len([value for value in distinct_reasons if value]) < int(cfg.get('minimum_distinct_reasons', 2) or 2):
        multiplier *= safe_float(cfg.get('low_semantic_variation_penalty', 0.82), 0.82)
        notes.append('semantic variation is still low')
    if latest_ts:
        minutes_since = (dt.datetime.now() - latest_ts).total_seconds() / 60.0
        if minutes_since < safe_float(cfg.get('minimum_minutes_between_reinforcement', 45), 45.0):
            multiplier *= safe_float(cfg.get('low_time_separation_penalty', 0.82), 0.82)
            notes.append(f'time separation is short ({round(minutes_since, 1)} min)')
    return {
        'multiplier': round(clamp_number(multiplier, 0.2, 1.0), 3),
        'same_pattern_hits': same_pattern_hits,
        'distinct_source_patterns': len(distinct_source_patterns or ({tuple(sorted(current_sources))} if current_sources else set())),
        'distinct_source_types': len(total_source_types),
        'distinct_reason_count': len([value for value in distinct_reasons if value]),
        'notes': notes,
    }


def attractor_saturation_state(previous_value, evidence_profile, schema):
    cfg = schema.get('control', {}).get('attractor_saturation', {})
    soft_start = safe_float(cfg.get('soft_start_score', 0.82), 0.82)
    strong_start = safe_float(cfg.get('strong_start_score', 0.92), 0.92)
    floor_multiplier = safe_float(cfg.get('floor_multiplier', 0.08), 0.08)
    current_sources = set(evidence_profile.get('source_types', []))
    multiplier = 1.0
    notes = []
    if previous_value >= strong_start:
        multiplier *= safe_float(cfg.get('strong_damping', 0.38), 0.38)
        minimum_sources = int(cfg.get('min_source_types_above_strong_start', 3) or 3)
        notes.append('attractor is in the strong saturation band')
    elif previous_value >= soft_start:
        multiplier *= safe_float(cfg.get('soft_damping', 0.72), 0.72)
        minimum_sources = int(cfg.get('min_source_types_above_soft_start', 2) or 2)
        notes.append('attractor is in the soft saturation band')
    else:
        minimum_sources = 0
    if previous_value >= soft_start:
        remaining_band = max(0.0, 1.0 - previous_value)
        normalization_band = max(0.01, 1.0 - soft_start)
        headroom_multiplier = max(floor_multiplier, remaining_band / normalization_band)
        multiplier *= headroom_multiplier
        notes.append(f'limited headroom remains ({round(remaining_band, 3)})')
        if minimum_sources and len(current_sources) < minimum_sources:
            shortage = minimum_sources - len(current_sources)
            multiplier *= max(floor_multiplier, 1.0 - (0.18 * shortage))
            notes.append(f'high score now requires more source-type diversity (need {minimum_sources})')
        if not current_sources & {'runtime_truth', 'code_config'}:
            multiplier *= safe_float(cfg.get('high_score_missing_runtime_or_code_penalty', 0.6), 0.6)
            notes.append('high-score reinforcement lacks runtime/code evidence')
    return {
        'multiplier': round(clamp_number(multiplier, floor_multiplier, 1.0), 3),
        'notes': notes,
    }


def conservative_applied_delta(field, requested_delta, confidence, support_count):
    requested_delta = clamp_number(requested_delta, -0.08, 0.08)
    confidence = clamp_number(confidence, 0.0, 1.0)
    if requested_delta == 0:
        return 0.0
    support_multiplier = 0.22 if support_count == 0 else min(0.82, 0.34 + (0.14 * support_count))
    applied = requested_delta * confidence * support_multiplier
    if support_count == 0 and confidence < 0.7:
        applied *= 0.4
    if field == 'tensions' and requested_delta < 0:
        applied *= 0.35
    if abs(applied) < 0.004:
        return 0.0
    return round_delta(applied)


def latest_report_path(name):
    path = REPORTS_DIR / f'latest_{name}.md'
    return path if path.exists() else None


def lower_text(text):
    return re.sub(r'\s+', ' ', (text or '').lower())


def reflection_source_bucket(path):
    if path_within(path, [FIELD_V2_DIR]):
        return 'field_state'
    if path == BUILD_SUMMARY_PATH or path == RUNTIME_STATE_PATH:
        return 'runtime_truth'
    try:
        if path.parent == REPORTS_DIR or path == latest_report_path('sleep') or path == latest_report_path('dream') or path == latest_report_path('reality') or path == latest_report_path('reflect'):
            return 'reports'
    except Exception:
        pass
    if path in PROJECT_ELI_CONTEXT_PATHS:
        return 'eli_docs'
    suffix = path.suffix.lower()
    if suffix in ('.swift', '.py', '.json', '.yaml', '.yml', '.plist'):
        return 'code_config'
    if suffix == '.md' and path_within(path, BUILD_WATCH_ROOTS):
        return 'code_config'
    return 'eli_docs' if suffix == '.md' else 'code_config'


def collect_reflection_sources(changes, prior_reports):
    sources = []
    seen_paths = set()

    def add_source(path, text=''):
        if not path or path in seen_paths:
            return
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)
        bucket = reflection_source_bucket(path)
        if bucket == 'field_state':
            return
        if not text:
            text = read_file_excerpt(path)
        if not text:
            return
        seen_paths.add(path)
        sources.append({
            'path': path,
            'bucket': bucket,
            'text': text,
        })

    for name in ('sleep', 'dream', 'reality', 'reflect'):
        report_path = prior_reports.get(name) if isinstance(prior_reports, dict) else None
        if report_path:
            add_source(report_path)

    for path in PROJECT_ELI_CONTEXT_PATHS:
        if path.exists():
            add_source(path)

    if RUNTIME_STATE_PATH.exists():
        add_source(RUNTIME_STATE_PATH)
    if BUILD_SUMMARY_PATH.exists():
        add_source(BUILD_SUMMARY_PATH)

    for path, text in changes:
        bucket = reflection_source_bucket(path)
        if bucket in ('code_config', 'runtime_truth'):
            add_source(path, text)

    return sources


def concept_profile_key(field, target_id):
    return f'{field}/{target_id}'


def build_resonance_analysis(sources):
    profiles = {}
    for field, targets in FIELD_CONCEPT_PATTERNS.items():
        for target_id, patterns in targets.items():
            source_hits = {}
            for source in sources:
                source_text = lower_text(source.get('text', ''))
                if not source_text or not matches_any_pattern(source_text, patterns):
                    continue
                bucket = source.get('bucket', 'reports')
                source_hits.setdefault(bucket, [])
                source_hits[bucket].append(str(source.get('path')))
            if not source_hits:
                continue
            weighted_score = 0.0
            for bucket, paths in source_hits.items():
                weighted_score += EVIDENCE_SOURCE_WEIGHTS.get(bucket, 1.0) * min(len(paths), 2)
            source_types = sorted(source_hits.keys())
            repetition_kind = 'cross_source_resonance' if len(source_types) >= 2 else 'single_source_repetition'
            profiles[concept_profile_key(field, target_id)] = {
                'field': field,
                'target_id': target_id,
                'source_types': source_types,
                'source_counts': {bucket: len(paths) for bucket, paths in source_hits.items()},
                'source_paths': {bucket: paths[:4] for bucket, paths in source_hits.items()},
                'weighted_score': round(weighted_score, 3),
                'repetition_kind': repetition_kind,
            }
    return profiles


def build_contradiction_persistence(snapshot, history_entries, resonance_profiles):
    items = []
    tensions = snapshot.get('tensions', {}).get('items', [])
    for tension in tensions:
        target_id = tension.get('id')
        if not target_id:
            continue
        key = concept_profile_key('tensions', target_id)
        resonance = resonance_profiles.get(key, {})
        recent_entries = [entry for entry in history_entries[-24:] if entry.get('field') == 'tensions' and entry.get('target_id') == target_id]
        resurfacing_count = len(recent_entries)
        net_delta = round(sum(safe_float(entry.get('applied_delta', 0.0), 0.0) for entry in recent_entries), 4)
        source_types = resonance.get('source_types', [])
        stable_score = abs(net_delta) < 0.02
        semantically_unresolved = stable_score and len(source_types) >= 2 and resonance.get('weighted_score', 0.0) >= 2.0
        if not semantically_unresolved and resurfacing_count < 2 and resonance.get('weighted_score', 0.0) < 2.5:
            continue
        level = 'high' if resurfacing_count >= 3 or resonance.get('weighted_score', 0.0) >= 3.0 else 'medium'
        reason_parts = []
        if source_types:
            reason_parts.append(f"recurs across {', '.join(source_types)}")
        if resurfacing_count:
            reason_parts.append(f"has {resurfacing_count} recent tension updates")
        if semantically_unresolved:
            reason_parts.append('score is numerically stable but the contradiction remains unresolved in meaning')
        items.append({
            'target_id': target_id,
            'label': tension.get('label', target_id),
            'reason': '; '.join(reason_parts) if reason_parts else 'keeps resurfacing without real resolution',
            'persistence_level': level,
            'confidence': 0.7 if semantically_unresolved else 0.62,
        })
    return items


def classify_dormant_idea_type(item, resonance_profiles):
    label = lower_text(item.get('label', ''))
    reason = lower_text(item.get('reason', ''))
    text = f'{label} {reason}'
    if any(token in text for token in ('constraint', 'battery', 'thermal', 'privacy', 'latency', 'blocked', 'phone-first', 'hardware', 'v1 limit')):
        return 'constraint_blocked'
    if any(token in text for token in ('mode', 'core deepening', 'deprioritized', 'suppressed', 'current focus', 'implementation grounding')):
        return 'mode_suppressed'
    if any(token in text for token in ('premature', 'not yet', 'later', 'after v1', 'foundation first', 'worth reactivating now')):
        return 'premature_but_promising'
    related_profiles = []
    if 'subtitle' in text:
        related_profiles.append(resonance_profiles.get('attractors/subtitle_clarity'))
    if any(token in text for token in ('memory', 'name', 'face', 'person-memory', 'entity-linking')):
        related_profiles.append(resonance_profiles.get('attractors/memory_trust'))
    if any(token in text for token in ('one-line', 'low-friction', 'assist')):
        related_profiles.append(resonance_profiles.get('attractors/low_friction_assistance'))
    for profile in related_profiles:
        if profile and len(profile.get('source_types', [])) >= 2:
            return 'premature_but_promising'
    return 'low_value'


def build_overdominant_attractors(snapshot, history_entries, resonance_profiles, schema):
    threshold = safe_float(schema.get('control', {}).get('recurrence_thresholds', {}).get('overdominant_attractor_score', 0.9), 0.9)
    items = []
    for attractor in snapshot.get('attractors', {}).get('items', []):
        target_id = attractor.get('id')
        if not target_id:
            continue
        score = safe_float(attractor.get('score', 0.0), 0.0)
        profile = resonance_profiles.get(concept_profile_key('attractors', target_id), {})
        support_count = delta_support_count(history_entries, 'attractors', target_id, 1)
        if score < threshold and support_count < 3:
            continue
        reason_parts = [f'current score is {round(score, 3)}']
        if support_count:
            reason_parts.append(f'has {support_count} recent reinforcing updates')
        if profile.get('source_types'):
            reason_parts.append(f"current evidence comes from {', '.join(profile.get('source_types', []))}")
        if len(profile.get('source_types', [])) <= 1:
            reason_parts.append('reinforcement diversity is still narrow')
        items.append({
            'target_id': target_id,
            'label': attractor.get('label', target_id),
            'reason': '; '.join(reason_parts),
            'confidence': 0.76 if score >= threshold else 0.64,
        })
    items.sort(key=lambda item: safe_float(field_item_index(snapshot.get('attractors', {})).get(item.get('target_id'), {}).get('score', 0.0), 0.0), reverse=True)
    return items[:3]


def build_under_attended_recurring_tensions(snapshot, history_entries, resonance_profiles, schema):
    cfg = schema.get('control', {}).get('recurrence_thresholds', {})
    weighted_threshold = safe_float(cfg.get('under_attended_recurring_tension_score', 3.0), 3.0)
    resurfacing_min = int(cfg.get('contradiction_resurfacing_min', 2) or 2)
    items = []
    for tension in snapshot.get('tensions', {}).get('items', []):
        target_id = tension.get('id')
        if not target_id:
            continue
        profile = resonance_profiles.get(concept_profile_key('tensions', target_id), {})
        recurring_count = len(target_history_entries(history_entries, 'tensions', target_id, direction=None, limit=24))
        if profile.get('weighted_score', 0.0) < weighted_threshold:
            continue
        if recurring_count >= resurfacing_min:
            continue
        reason_parts = [
            f"recurs with weighted evidence {profile.get('weighted_score', 0.0)}",
            f"but only has {recurring_count} recent field updates",
        ]
        if profile.get('source_types'):
            reason_parts.append(f"source spread: {', '.join(profile.get('source_types', []))}")
        items.append({
            'target_id': target_id,
            'label': tension.get('label', target_id),
            'reason': '; '.join(reason_parts),
            'confidence': 0.67,
        })
    return items[:3]


def build_reinforcement_loops(snapshot, history_entries, resonance_profiles, schema):
    cfg = schema.get('control', {}).get('recurrence_thresholds', {})
    support_min = int(cfg.get('reinforcement_loop_support_min', 4) or 4)
    weight_min = safe_float(cfg.get('reinforcement_loop_weighted_score_min', 4.0), 4.0)
    items = []
    for attractor in snapshot.get('attractors', {}).get('items', []):
        target_id = attractor.get('id')
        if not target_id:
            continue
        profile = resonance_profiles.get(concept_profile_key('attractors', target_id), {})
        support_count = delta_support_count(history_entries, 'attractors', target_id, 1)
        recent = target_history_entries(history_entries, 'attractors', target_id, direction=1, limit=16)
        if support_count < support_min:
            continue
        source_patterns = {tuple(sorted(entry.get('evidence_sources', []))) for entry in recent if entry.get('evidence_sources')}
        reason_signatures = {reason_signature(entry.get('reason', '')) for entry in recent if reason_signature(entry.get('reason', ''))}
        low_diversity = len(source_patterns) <= 1 or len(reason_signatures) <= 1
        if not low_diversity and profile.get('weighted_score', 0.0) < weight_min:
            continue
        reason_parts = [f'{support_count} recent reinforcements']
        if source_patterns:
            reason_parts.append(f'{len(source_patterns)} source-pattern variants')
        if reason_signatures:
            reason_parts.append(f'{len(reason_signatures)} reason variants')
        if len(profile.get('source_types', [])) <= 1:
            reason_parts.append('recurrence is still concentrated in one source type')
        items.append({
            'field': 'attractors',
            'target_id': target_id,
            'label': attractor.get('label', target_id),
            'reason': '; '.join(reason_parts),
            'confidence': 0.73 if low_diversity else 0.62,
        })
    return items[:3]


def build_counterweight_awareness(snapshot, resonance_profiles, contradiction_persistence, schema):
    cfg = schema.get('control', {}).get('counterweights', {})
    links = cfg.get('links', {})
    tension_score_threshold = safe_float(cfg.get('attention_tension_score', 0.72), 0.72)
    resonance_threshold = safe_float(cfg.get('attention_resonance_score', 2.2), 2.2)
    persistence_levels = set(cfg.get('persistence_levels', ['medium', 'high']))
    tensions_by_id = field_item_index(snapshot.get('tensions', {}))
    contradiction_by_id = {item.get('target_id'): item for item in contradiction_persistence if item.get('target_id')}
    items = []
    for attractor_id, tension_ids in links.items():
        attractor = field_item_index(snapshot.get('attractors', {})).get(attractor_id, {})
        attractor_profile = resonance_profiles.get(concept_profile_key('attractors', attractor_id), {})
        if not attractor:
            continue
        if safe_float(attractor.get('score', 0.0), 0.0) < 0.7 and attractor_profile.get('weighted_score', 0.0) < 1.5:
            continue
        flagged_ids = []
        flagged_labels = []
        for tension_id in tension_ids:
            tension = tensions_by_id.get(tension_id, {})
            if not tension:
                continue
            profile = resonance_profiles.get(concept_profile_key('tensions', tension_id), {})
            contradiction = contradiction_by_id.get(tension_id, {})
            if (
                safe_float(tension.get('score', 0.0), 0.0) >= tension_score_threshold
                or profile.get('weighted_score', 0.0) >= resonance_threshold
                or contradiction.get('persistence_level') in persistence_levels
            ):
                flagged_ids.append(tension_id)
                flagged_labels.append(tension.get('label', tension_id))
        if not flagged_ids:
            continue
        items.append({
            'target_id': attractor_id,
            'label': attractor.get('label', attractor_id),
            'counterweight_tensions': flagged_ids,
            'reason': f"Strengthening {attractor.get('label', attractor_id)} also keeps pressure on {', '.join(flagged_labels)}.",
            'confidence': 0.7,
        })
    return items[:4]


def build_cooling_candidates(snapshot, history_entries, resonance_profiles, schema):
    cfg = schema.get('control', {}).get('controlled_decay', {})
    cooling_score_threshold = safe_float(cfg.get('cooling_score_threshold', 0.92), 0.92)
    low_diversity_max_source_types = int(cfg.get('low_diversity_max_source_types', 1) or 1)
    support_min = int(cfg.get('stale_reinforcement_support_min', 4) or 4)
    stale_reason_variant_max = int(cfg.get('stale_reason_variant_max', 1) or 1)
    stale_source_pattern_max = int(cfg.get('stale_source_pattern_max', 1) or 1)
    healthy_min_source_types = int(cfg.get('healthy_reinforcement_min_source_types', 2) or 2)
    healthy_weighted_score = safe_float(cfg.get('healthy_reinforcement_min_weighted_score', 3.2), 3.2)
    cooling_delta = round(clamp_number(safe_float(cfg.get('cooling_delta', -0.012), -0.012), -0.03, -0.004), 4)
    items = []
    for attractor in snapshot.get('attractors', {}).get('items', []):
        target_id = attractor.get('id')
        if not target_id:
            continue
        score = safe_float(attractor.get('score', 0.0), 0.0)
        if score < cooling_score_threshold:
            continue
        support_count = delta_support_count(history_entries, 'attractors', target_id, 1)
        if support_count < support_min:
            continue
        profile = resonance_profiles.get(concept_profile_key('attractors', target_id), {})
        recent = target_history_entries(history_entries, 'attractors', target_id, direction=1, limit=16)
        source_patterns = {tuple(sorted(entry.get('evidence_sources', []))) for entry in recent if entry.get('evidence_sources')}
        reason_signatures = {reason_signature(entry.get('reason', '')) for entry in recent if reason_signature(entry.get('reason', ''))}
        source_type_count = len(profile.get('source_types', []))
        low_diversity = (
            source_type_count <= low_diversity_max_source_types
            or (
                len(source_patterns) <= stale_source_pattern_max
                and len(reason_signatures) <= stale_reason_variant_max
            )
        )
        healthy_reinforcement = source_type_count >= healthy_min_source_types and profile.get('weighted_score', 0.0) >= healthy_weighted_score
        if not low_diversity or healthy_reinforcement:
            continue
        reason_parts = [
            f"score remains high at {round(score, 3)}",
            f"recent reinforcements stayed narrow across {max(1, source_type_count)} source types",
        ]
        if len(source_patterns) <= stale_source_pattern_max:
            reason_parts.append(f"only {len(source_patterns)} recent source-pattern variants")
        if len(reason_signatures) <= stale_reason_variant_max:
            reason_parts.append(f"only {len(reason_signatures)} recent reason variants")
        items.append({
            'target_id': target_id,
            'label': attractor.get('label', target_id),
            'cooling_kind': 'low_diversity_decay',
            'suggested_delta': cooling_delta,
            'reason': '; '.join(reason_parts),
            'confidence': 0.69,
        })
    items.sort(key=lambda item: safe_float(field_item_index(snapshot.get('attractors', {})).get(item.get('target_id'), {}).get('score', 0.0), 0.0), reverse=True)
    return items[:2]


def build_neglected_persistent_tensions(snapshot, history_entries, resonance_profiles, contradiction_persistence, under_attended_recurring_tensions, schema):
    cfg = schema.get('control', {}).get('rebalancing', {})
    score_threshold = safe_float(cfg.get('neglected_tension_score_threshold', 0.72), 0.72)
    weighted_threshold = safe_float(cfg.get('neglected_tension_weighted_score_min', 3.0), 3.0)
    neglected_update_cap = int(cfg.get('neglected_update_cap', 1) or 1)
    suggested_delta = round(clamp_number(safe_float(cfg.get('neglected_tension_delta', 0.012), 0.012), 0.004, 0.03), 4)
    contradiction_by_id = {
        item.get('target_id'): item
        for item in contradiction_persistence
        if item.get('target_id')
    }
    under_attended_by_id = {
        item.get('target_id'): item
        for item in under_attended_recurring_tensions
        if item.get('target_id')
    }
    items = []
    for tension in snapshot.get('tensions', {}).get('items', []):
        target_id = tension.get('id')
        if not target_id:
            continue
        contradiction = contradiction_by_id.get(target_id)
        under_attended = under_attended_by_id.get(target_id)
        profile = resonance_profiles.get(concept_profile_key('tensions', target_id), {})
        recurring_updates = len(target_history_entries(history_entries, 'tensions', target_id, direction=None, limit=24))
        if recurring_updates > neglected_update_cap:
            continue
        if not contradiction and not under_attended:
            continue
        if safe_float(tension.get('score', 0.0), 0.0) < score_threshold and profile.get('weighted_score', 0.0) < weighted_threshold:
            continue
        reason_parts = []
        if contradiction:
            reason_parts.append(contradiction.get('reason', 'contradiction remains unresolved'))
        if under_attended:
            reason_parts.append(under_attended.get('reason', 'tension keeps recurring without enough attention'))
        items.append({
            'target_id': target_id,
            'label': tension.get('label', target_id),
            'suggested_delta': suggested_delta,
            'reason': '; '.join(part for part in reason_parts if part),
            'confidence': 0.72 if contradiction and under_attended else 0.66,
        })
    items.sort(
        key=lambda item: (
            -safe_float(resonance_profiles.get(concept_profile_key('tensions', item.get('target_id', '')), {}).get('weighted_score', 0.0), 0.0),
            -safe_float(field_item_index(snapshot.get('tensions', {})).get(item.get('target_id'), {}).get('score', 0.0), 0.0),
        )
    )
    return items


def build_field_imbalance_patterns(snapshot, history_entries, contradiction_persistence, under_attended_recurring_tensions, counterweight_awareness, schema):
    cfg = schema.get('control', {}).get('rebalancing', {})
    attractor_score_threshold = safe_float(cfg.get('imbalance_attractor_score_threshold', 0.84), 0.84)
    support_min = int(cfg.get('imbalance_support_min', 4) or 4)
    persistence_levels = set(cfg.get('imbalance_persistence_levels', ['medium', 'high']))
    contradiction_by_id = {
        item.get('target_id'): item
        for item in contradiction_persistence
        if item.get('target_id')
    }
    neglected_ids = {
        item.get('target_id')
        for item in under_attended_recurring_tensions
        if item.get('target_id')
    }
    attractors_by_id = field_item_index(snapshot.get('attractors', {}))
    tensions_by_id = field_item_index(snapshot.get('tensions', {}))
    items = []
    for item in counterweight_awareness:
        target_id = item.get('target_id')
        attractor = attractors_by_id.get(target_id, {})
        if not attractor:
            continue
        if safe_float(attractor.get('score', 0.0), 0.0) < attractor_score_threshold:
            continue
        support_count = delta_support_count(history_entries, 'attractors', target_id, 1)
        if support_count < support_min:
            continue
        linked_neglected = []
        for tension_id in item.get('counterweight_tensions', []):
            contradiction = contradiction_by_id.get(tension_id, {})
            if tension_id in neglected_ids or contradiction.get('persistence_level') in persistence_levels:
                linked_neglected.append(tension_id)
        if not linked_neglected:
            continue
        linked_labels = [tensions_by_id.get(tension_id, {}).get('label', tension_id) for tension_id in linked_neglected]
        items.append({
            'target_id': target_id,
            'label': attractor.get('label', target_id),
            'linked_tensions': linked_neglected,
            'reason': f"{attractor.get('label', target_id)} keeps strengthening while linked tensions stay neglected: {', '.join(linked_labels)}.",
            'confidence': 0.74,
        })
    return items[:3]


def repo_alignment_config(schema):
    if isinstance(schema.get('phase7_repo_alignment'), dict):
        return schema.get('phase7_repo_alignment', {})
    return schema.get('control', {}).get('phase7_repo_alignment', {})


def repo_change_relative_path(path):
    try:
        return pathlib.Path(path).relative_to(REPO_LINK_DIR).as_posix()
    except Exception:
        try:
            return pathlib.Path(path).relative_to(PROJECT_DIR).as_posix()
        except Exception:
            return str(path)


def repo_change_surface(path):
    rel = repo_change_relative_path(path).lower()
    suffix = pathlib.Path(path).suffix.lower()
    if rel.startswith('assets/') or suffix in ('.png', '.jpg', '.jpeg', '.gif', '.svg'):
        return 'asset'
    if rel.startswith('docs/') or rel in ('readme.md', 'license') or suffix in ('.md', '.txt', '.rtf'):
        return 'docs'
    if rel.startswith('hardware/'):
        return 'hardware'
    if rel.startswith('firmware/'):
        return 'firmware'
    if rel.startswith('app/') and suffix in ('.html', '.css'):
        return 'ui'
    if suffix in ('.json', '.yaml', '.yml', '.plist'):
        return 'config'
    if suffix in ('.swift', '.py', '.js', '.ts', '.html', '.css'):
        return 'code'
    return 'code'


def repo_semantic_text(path, text):
    return lower_text(f"{repo_change_relative_path(path)} {text or ''}")


def repo_change_domains(text):
    matches = []
    if re.search(r'(subtitle|caption)', text) and re.search(r'(placement|position|overlay|layout|render)', text):
        matches.append('subtitle placement')
    if re.search(r'(confidence|certainty|uncertain)', text) or (re.search(r'\bscore\b', text) and re.search(r'(label|reason|confidence)', text)):
        matches.append('confidence display')
    if re.search(r'(memory|cache|lookup|entity-link|retention|evict|recency|name recall|face/?name)', text):
        matches.append('memory/cache policy')
    if re.search(r'(phone/?cloud|on-device|local|cloud|fallback|route|upload|sync|server)', text):
        matches.append('phone/cloud boundary')
    if re.search(r'(visual hierarchy|priority|precedence|overlay|prominen|one-line|z-index)', text):
        matches.append('visual hierarchy')
    return matches


def repo_change_field_links(text, matched_domains):
    linked = {'attractors': set(), 'tensions': set(), 'modes': set()}
    for field in ('attractors', 'tensions', 'modes'):
        for target_id, patterns in FIELD_CONCEPT_PATTERNS.get(field, {}).items():
            if target_id.replace('_', ' ') in text or matches_any_pattern(text, patterns):
                linked[field].add(target_id)
    for domain in matched_domains:
        links = candidate_domain_links(domain)
        for field in linked:
            linked[field].update(links.get(field, []))
    return {field: sorted(values) for field, values in linked.items()}


def repo_change_target_labels(field_links, snapshot):
    labels = []
    for field in ('attractors', 'tensions', 'modes'):
        items_by_id = field_item_index(snapshot.get(field, {}))
        for target_id in field_links.get(field, []):
            label = items_by_id.get(target_id, {}).get('label', target_id)
            labels.append(f'{field}/{label}')
    return labels


def repo_candidate_confidence(classification, surface, matched_domains, field_links):
    signal_count = len(matched_domains) + sum(len(values) for values in field_links.values())
    confidence = 0.48 + min(0.2, signal_count * 0.03)
    if classification in ('productive_resistance', 'misaligned', 'field_neglecting'):
        confidence += 0.08
    if surface in ('code', 'config', 'hardware', 'firmware'):
        confidence += 0.05
    if surface == 'docs':
        confidence -= 0.05
    if classification == 'cosmetic_only':
        confidence -= 0.03
    return round(clamp_number(confidence, 0.45, 0.9), 3)


def classify_repo_change_candidate(path, text, matched_domains, field_links, snapshot, contradiction_ids, neglected_ids, counterweight_by_target, overdominant_ids):
    semantic_text = repo_semantic_text(path, text)
    surface = repo_change_surface(path)
    structural_surface = surface in ('code', 'config', 'hardware', 'firmware', 'ui')
    tension_focus_ids = set(field_links.get('tensions', [])) & (set(contradiction_ids) | set(neglected_ids))
    counterweight_tensions = set()
    for attractor_id in field_links.get('attractors', []):
        counterweight_tensions.update(counterweight_by_target.get(attractor_id, {}).get('counterweight_tensions', []))
    touches_counterweight_tensions = bool(counterweight_tensions & set(field_links.get('tensions', [])))

    misaligned_patterns = [
        r'voice activation',
        r'spoken command',
        r'wake word',
        r'always[- ]listening',
        r'hands[- ]free',
        r'social feed',
        r'gamification',
        r'avatar',
        r'virtual companion',
    ]
    productive_resistance_patterns = [
        r'privacy',
        r'latency',
        r'thermal',
        r'battery',
        r'on-device',
        r'local',
        r'fallback',
        r'cache limit',
        r'retention',
        r'phone[- ]first',
    ]
    cosmetic_patterns = [
        r'\bcolor\b',
        r'\bfont\b',
        r'\bspacing\b',
        r'\bpadding\b',
        r'\bmargin\b',
        r'\btypo\b',
        r'\bwhitespace\b',
        r'\bcomment\b',
        r'\bformat\b',
        r'\blint\b',
    ]

    strong_field_link = bool(matched_domains or any(field_links.values()))
    if matches_any_pattern(semantic_text, misaligned_patterns):
        classification = 'misaligned'
        reason = 'repo change introduces explicit signals that conflict with current SmartGlasses guardrails'
    elif (
        surface == 'asset'
        or (surface == 'docs' and not strong_field_link)
        or (surface in ('ui', 'code') and matches_any_pattern(semantic_text, cosmetic_patterns) and not strong_field_link)
    ):
        classification = 'cosmetic_only'
        reason = 'repo change stays mostly cosmetic or documentary without clear field-backed structural movement'
    elif tension_focus_ids or matches_any_pattern(semantic_text, productive_resistance_patterns):
        tension_labels = [
            field_item_index(snapshot.get('tensions', {})).get(target_id, {}).get('label', target_id)
            for target_id in sorted(tension_focus_ids)
        ]
        classification = 'productive_resistance'
        if tension_labels:
            reason = f"repo change productively addresses active tension pressure in {', '.join(tension_labels)}"
        else:
            reason = 'repo change pushes on active constraint or resistance pressure without expanding scope'
    else:
        overdominant_focus = any(target_id in overdominant_ids for target_id in field_links.get('attractors', []))
        if overdominant_focus and counterweight_tensions and not touches_counterweight_tensions:
            classification = 'field_neglecting'
            reason = 'repo change reinforces a currently dominant attractor without corresponding counterweight attention'
        elif strong_field_link:
            target_labels = repo_change_target_labels(field_links, snapshot)
            classification = 'aligned'
            reason = f"repo change structurally backs current field priorities in {', '.join(target_labels[:3])}"
        elif structural_surface:
            classification = 'field_neglecting'
            reason = 'repo change adds structural churn without clear linkage to current field priorities or live tensions'
        else:
            classification = 'cosmetic_only'
            reason = 'repo change does not yet provide clear field-grounded structural evidence'

    confidence = repo_candidate_confidence(classification, surface, matched_domains, field_links)
    return surface, classification, reason, confidence


def build_repo_change_candidates(changes, snapshot, contradiction_persistence, under_attended_recurring_tensions, counterweight_awareness, overdominant_attractors, schema):
    cfg = repo_alignment_config(schema)
    if not cfg.get('enabled', False):
        return []
    contradiction_ids = {
        item.get('target_id')
        for item in contradiction_persistence
        if item.get('target_id')
    }
    neglected_ids = {
        item.get('target_id')
        for item in under_attended_recurring_tensions
        if item.get('target_id')
    }
    counterweight_by_target = {
        item.get('target_id'): item
        for item in counterweight_awareness
        if item.get('target_id')
    }
    overdominant_ids = {
        item.get('target_id')
        for item in overdominant_attractors
        if item.get('target_id')
    }
    items = []
    for path, text in changes:
        if classify_input_path(path) != 'repo':
            continue
        if pathlib.Path(path).name.startswith('.'):
            continue
        semantic_text = repo_semantic_text(path, text)
        matched_domains = repo_change_domains(semantic_text)
        field_links = repo_change_field_links(semantic_text, matched_domains)
        surface, classification, reason, confidence = classify_repo_change_candidate(
            path,
            text,
            matched_domains,
            field_links,
            snapshot,
            contradiction_ids,
            neglected_ids,
            counterweight_by_target,
            overdominant_ids,
        )
        items.append({
            'path': str(path),
            'relative_path': repo_change_relative_path(path),
            'surface': surface,
            'classification': classification,
            'matched_domains': matched_domains,
            'matched_field_targets': repo_change_target_labels(field_links, snapshot),
            'field_links': field_links,
            'structural_progress': surface in ('code', 'config', 'hardware', 'firmware', 'ui') and classification in ('aligned', 'productive_resistance'),
            'reason': reason,
            'confidence': confidence,
        })
    priority = {
        'misaligned': 0,
        'field_neglecting': 1,
        'productive_resistance': 2,
        'aligned': 3,
        'cosmetic_only': 4,
    }
    items.sort(key=lambda item: (priority.get(item.get('classification', ''), 9), -safe_float(item.get('confidence', 0.0), 0.0), item.get('relative_path', '')))
    return items[:8]


def build_field_diff_alignment_patterns(repo_candidates, snapshot, contradiction_persistence, under_attended_recurring_tensions, counterweight_awareness, overdominant_attractors):
    if not repo_candidates:
        return []
    contradiction_ids = {
        item.get('target_id')
        for item in contradiction_persistence
        if item.get('target_id')
    }
    neglected_ids = {
        item.get('target_id')
        for item in under_attended_recurring_tensions
        if item.get('target_id')
    }
    active_tension_ids = contradiction_ids | neglected_ids
    counterweight_by_target = {
        item.get('target_id'): item
        for item in counterweight_awareness
        if item.get('target_id')
    }
    overdominant_ids = {
        item.get('target_id')
        for item in overdominant_attractors
        if item.get('target_id')
    }
    tensions_by_id = field_item_index(snapshot.get('tensions', {}))
    attractors_by_id = field_item_index(snapshot.get('attractors', {}))
    positive_candidates = [
        item for item in repo_candidates
        if item.get('classification') in ('aligned', 'productive_resistance')
    ]
    patterns = []

    if repo_candidates and all(item.get('classification') == 'cosmetic_only' for item in repo_candidates):
        patterns.append({
            'classification': 'cosmetic_only',
            'field': 'repo',
            'target_id': '',
            'label': 'Repo motion is mostly cosmetic',
            'related_paths': [item.get('relative_path', '') for item in repo_candidates[:3]],
            'reason': 'current repo changes do not yet show structural progress on active field priorities',
            'confidence': 0.62,
        })

    for tension_id in sorted(active_tension_ids):
        matching = [
            item for item in positive_candidates
            if tension_id in item.get('field_links', {}).get('tensions', [])
        ]
        if not matching:
            continue
        classification = 'productive_resistance' if any(item.get('classification') == 'productive_resistance' for item in matching) else 'aligned'
        patterns.append({
            'classification': classification,
            'field': 'tensions',
            'target_id': tension_id,
            'label': tensions_by_id.get(tension_id, {}).get('label', tension_id),
            'related_paths': [item.get('relative_path', '') for item in matching[:3]],
            'reason': f"repo changes now touch this recurring tension through {', '.join(item.get('relative_path', '') for item in matching[:2])}",
            'confidence': 0.72 if classification == 'productive_resistance' else 0.64,
        })

    for attractor_id in sorted(overdominant_ids):
        matching = [
            item for item in repo_candidates
            if attractor_id in item.get('field_links', {}).get('attractors', [])
        ]
        if not matching:
            continue
        linked_tensions = counterweight_by_target.get(attractor_id, {}).get('counterweight_tensions', [])
        if linked_tensions and not any(
            any(tension_id in item.get('field_links', {}).get('tensions', []) for tension_id in linked_tensions)
            for item in positive_candidates
        ):
            patterns.append({
                'classification': 'field_neglecting',
                'field': 'attractors',
                'target_id': attractor_id,
                'label': attractors_by_id.get(attractor_id, {}).get('label', attractor_id),
                'related_paths': [item.get('relative_path', '') for item in matching[:3]],
                'reason': f"repo changes keep backing {attractors_by_id.get(attractor_id, {}).get('label', attractor_id)} without diff-backed counterweight work",
                'confidence': 0.74,
            })

    for item in repo_candidates:
        if item.get('classification') != 'misaligned':
            continue
        patterns.append({
            'classification': 'misaligned',
            'field': 'repo',
            'target_id': '',
            'label': item.get('relative_path', 'repo change'),
            'related_paths': [item.get('relative_path', '')],
            'reason': item.get('reason', ''),
            'confidence': item.get('confidence', 0.5),
        })

    priority = {
        'misaligned': 0,
        'field_neglecting': 1,
        'productive_resistance': 2,
        'aligned': 3,
        'cosmetic_only': 4,
    }
    patterns.sort(key=lambda item: (priority.get(item.get('classification', ''), 9), -safe_float(item.get('confidence', 0.0), 0.0), item.get('label', '')))
    return patterns[:5]


def build_repo_alignment_observations(repo_candidates, field_diff_alignment_patterns):
    if not repo_candidates:
        return []
    observations = []
    counts = {}
    for item in repo_candidates:
        counts[item.get('classification', '')] = counts.get(item.get('classification', ''), 0) + 1
    templates = {
        'aligned': 'repo changes structurally back current field priorities',
        'productive_resistance': 'repo changes are productively engaging active tensions or constraints',
        'misaligned': 'repo changes include motion that conflicts with current SmartGlasses guardrails',
        'field_neglecting': 'repo changes are neglecting active field pressure or counterweights',
        'cosmetic_only': 'repo changes are mostly cosmetic and should not be treated as structural progress',
    }
    for classification in REPO_ALIGNMENT_CLASSIFICATIONS:
        matching = [item for item in repo_candidates if item.get('classification') == classification]
        if not matching:
            continue
        observations.append({
            'classification': classification,
            'label': classification.replace('_', ' ').title(),
            'related_paths': [item.get('relative_path', '') for item in matching[:3]],
            'reason': f"{templates.get(classification, classification)} ({counts.get(classification, 0)} candidate changes)",
            'confidence': round(clamp_number(0.56 + (0.04 * min(len(matching), 3)), 0.52, 0.84), 3),
        })
    for pattern in field_diff_alignment_patterns[:2]:
        observations.append({
            'classification': pattern.get('classification', ''),
            'label': pattern.get('label', ''),
            'related_paths': pattern.get('related_paths', [])[:3],
            'reason': pattern.get('reason', ''),
            'confidence': pattern.get('confidence', 0.5),
        })
    priority = {
        'misaligned': 0,
        'field_neglecting': 1,
        'productive_resistance': 2,
        'aligned': 3,
        'cosmetic_only': 4,
    }
    observations.sort(key=lambda item: (priority.get(item.get('classification', ''), 9), -safe_float(item.get('confidence', 0.0), 0.0), item.get('label', '')))
    return observations[:6]


def empty_action_repo_grounding():
    return {
        'repo_grounding_score': 0.0,
        'repo_alignment_classification': '',
        'repo_grounding_reason': '',
        'repo_change_count': 0,
        'repo_grounding_paths': [],
        'repo_structural_progress': False,
        'repo_alignment_adjustment': 0.0,
        'repo_resistance_adjustment': 0.0,
        'repo_pull_adjustment': 0.0,
    }


def build_action_repo_grounding(repo_candidates, schema):
    cfg = repo_alignment_config(schema)
    diff_weights = cfg.get('diff_alignment', {})
    action_coupling = cfg.get('action_coupling', {})
    weights = {
        'aligned': safe_float(diff_weights.get('align_weight', 1.0), 1.0),
        'productive_resistance': safe_float(diff_weights.get('productive_resistance_weight', 0.75), 0.75),
        'misaligned': safe_float(diff_weights.get('misalignment_weight', -0.85), -0.85),
        'field_neglecting': safe_float(diff_weights.get('neglect_weight', -0.65), -0.65),
        'cosmetic_only': safe_float(diff_weights.get('cosmetic_only_weight', -0.3), -0.3),
    }
    grounding = {domain: empty_action_repo_grounding() for domain in DREAM_DOMAINS}
    if not cfg.get('enabled', False):
        return grounding
    for domain in DREAM_DOMAINS:
        matching = [item for item in repo_candidates if domain in item.get('matched_domains', [])]
        if not matching:
            continue
        raw_score = sum(weights.get(item.get('classification', ''), 0.0) for item in matching) / max(1, len(matching))
        repo_grounding_score = round(clamp_number(raw_score, -1.0, 1.0), 3)
        counts = {}
        for item in matching:
            counts[item.get('classification', '')] = counts.get(item.get('classification', ''), 0) + 1
        if counts.get('misaligned') and repo_grounding_score <= 0.15:
            classification = 'misaligned'
        elif counts.get('field_neglecting') and repo_grounding_score <= 0.2:
            classification = 'field_neglecting'
        elif counts.get('productive_resistance'):
            classification = 'productive_resistance'
        elif counts.get('aligned'):
            classification = 'aligned'
        else:
            classification = 'cosmetic_only'
        structural_progress = any(item.get('structural_progress') for item in matching)
        alignment_adjustment = 0.0
        resistance_adjustment = 0.0
        pull_adjustment = 0.0
        if classification == 'aligned' and action_coupling.get('reward_diff_backed_actions', True):
            alignment_adjustment += 0.03 if structural_progress else 0.015
            pull_adjustment += 0.04 if structural_progress else 0.02
        elif classification == 'productive_resistance' and action_coupling.get('reward_diff_backed_actions', True):
            alignment_adjustment += 0.012
            resistance_adjustment -= 0.018
            pull_adjustment += 0.028
        elif classification == 'misaligned':
            alignment_adjustment -= 0.03
            resistance_adjustment += 0.05
            pull_adjustment -= 0.06
        elif classification == 'field_neglecting':
            resistance_adjustment += 0.035
            pull_adjustment -= 0.04
        elif classification == 'cosmetic_only' and action_coupling.get('damp_talk_without_change', True):
            pull_adjustment -= 0.012
        path_samples = [item.get('relative_path', '') for item in matching[:3]]
        if classification == 'aligned':
            reason = f"repo changes in {', '.join(path_samples[:2])} now back this direction"
        elif classification == 'productive_resistance':
            reason = f"repo changes in {', '.join(path_samples[:2])} are productively addressing resistance around this direction"
        elif classification == 'misaligned':
            reason = f"repo changes in {', '.join(path_samples[:2])} conflict with current SmartGlasses guardrails"
        elif classification == 'field_neglecting':
            reason = f"repo changes in {', '.join(path_samples[:2])} add motion without enough field-linked balance"
        else:
            reason = f"repo changes in {', '.join(path_samples[:2])} are mostly cosmetic for this direction"
        grounding[domain] = {
            'repo_grounding_score': repo_grounding_score,
            'repo_alignment_classification': classification,
            'repo_grounding_reason': reason,
            'repo_change_count': len(matching),
            'repo_grounding_paths': path_samples,
            'repo_structural_progress': structural_progress,
            'repo_alignment_adjustment': round(alignment_adjustment, 3),
            'repo_resistance_adjustment': round(resistance_adjustment, 3),
            'repo_pull_adjustment': round(pull_adjustment, 3),
        }
    return grounding


def build_reflection_analysis(changes, prior_reports):
    schema = load_cognition_schema()
    snapshot = field_layer_snapshot()
    history_entries = load_field_delta_history().get('entries', [])
    sources = collect_reflection_sources(changes, prior_reports)
    resonance_profiles = build_resonance_analysis(sources)
    resonance_signals = []
    for key, profile in resonance_profiles.items():
        if profile.get('weighted_score', 0.0) < 1.5:
            continue
        label = key
        field = profile.get('field')
        target_id = profile.get('target_id')
        item = field_item_index(snapshot.get(field, {})).get(target_id, {})
        label = item.get('label', target_id)
        source_types = profile.get('source_types', [])
        resonance_signals.append({
            'field': field,
            'target_id': target_id,
            'label': label,
            'repetition_kind': profile.get('repetition_kind', 'single_source_repetition'),
            'source_types': source_types,
            'weighted_score': profile.get('weighted_score', 0.0),
            'reason': f"recurs in {', '.join(source_types)} with weighted evidence {profile.get('weighted_score', 0.0)}",
            'confidence': 0.7 if len(source_types) >= 2 else 0.55,
        })
    resonance_signals.sort(key=lambda item: item.get('weighted_score', 0.0), reverse=True)
    contradiction_persistence = build_contradiction_persistence(snapshot, history_entries, resonance_profiles)
    overdominant_attractors = build_overdominant_attractors(snapshot, history_entries, resonance_profiles, schema)
    under_attended_recurring_tensions = build_under_attended_recurring_tensions(snapshot, history_entries, resonance_profiles, schema)
    reinforcement_loops = build_reinforcement_loops(snapshot, history_entries, resonance_profiles, schema)
    counterweight_awareness = build_counterweight_awareness(snapshot, resonance_profiles, contradiction_persistence, schema)
    cooling_candidates = build_cooling_candidates(snapshot, history_entries, resonance_profiles, schema)
    neglected_persistent_tensions = build_neglected_persistent_tensions(snapshot, history_entries, resonance_profiles, contradiction_persistence, under_attended_recurring_tensions, schema)
    field_imbalance_patterns = build_field_imbalance_patterns(snapshot, history_entries, contradiction_persistence, under_attended_recurring_tensions, counterweight_awareness, schema)
    repo_change_candidates = build_repo_change_candidates(
        changes,
        snapshot,
        contradiction_persistence,
        under_attended_recurring_tensions,
        counterweight_awareness,
        overdominant_attractors,
        schema,
    )
    field_diff_alignment_patterns = build_field_diff_alignment_patterns(
        repo_change_candidates,
        snapshot,
        contradiction_persistence,
        under_attended_recurring_tensions,
        counterweight_awareness,
        overdominant_attractors,
    )
    repo_alignment_observations = build_repo_alignment_observations(repo_change_candidates, field_diff_alignment_patterns)
    action_repo_grounding = build_action_repo_grounding(repo_change_candidates, schema)
    return {
        'schema': schema,
        'snapshot': snapshot,
        'history_entries': history_entries,
        'sources': sources,
        'resonance_profiles': resonance_profiles,
        'resonance_signals': resonance_signals[:6],
        'contradiction_persistence': contradiction_persistence[:4],
        'overdominant_attractors': overdominant_attractors,
        'under_attended_recurring_tensions': under_attended_recurring_tensions,
        'reinforcement_loops': reinforcement_loops,
        'counterweight_awareness': counterweight_awareness,
        'cooling_candidates': cooling_candidates,
        'neglected_persistent_tensions': neglected_persistent_tensions,
        'field_imbalance_patterns': field_imbalance_patterns,
        'repo_change_candidates': repo_change_candidates,
        'repo_alignment_observations': repo_alignment_observations,
        'field_diff_alignment_patterns': field_diff_alignment_patterns,
        'action_repo_grounding': action_repo_grounding,
        'source_weighting': EVIDENCE_SOURCE_WEIGHTS,
    }


def normalized_resonance_score(profile):
    return clamp_number(safe_float(profile.get('weighted_score', 0.0), 0.0) / 4.0, 0.0, 1.0)


def average_score(values):
    values = [safe_float(value, 0.0) for value in values]
    if not values:
        return 0.0
    return round(sum(values) / len(values), 4)


def safe_int(value, fallback=0):
    try:
        return int(value)
    except Exception:
        return fallback


def candidate_domain_links(domain):
    return ACTION_DIRECTION_LINKS.get(domain, {
        'attractors': [],
        'tensions': [],
        'modes': [],
        'constraints': [],
    })


def action_candidate_signature(item):
    text = f"{item.get('domain', '')}|{item.get('title', '')}|{item.get('probe', '')}|{item.get('summary', '')}"
    return sha256_text(lower_text(text))[:16]


def action_evidence_sources(links, analysis):
    source_types = set()
    weighted_scores = []
    for field in ('attractors', 'tensions', 'modes'):
        for target_id in links.get(field, []):
            profile = evidence_profile_for_target(analysis, field, target_id)
            source_types.update(profile.get('source_types', []))
            weighted_scores.append(safe_float(profile.get('weighted_score', 0.0), 0.0))
    return {
        'source_types': sorted(source_types),
        'source_diversity_count': len(source_types),
        'weighted_evidence_score': round(average_score(weighted_scores), 3),
    }


def build_grounding_hold_state(item, links, analysis, repo_grounding, resurfacing_state, base_alignment_score, base_resistance_score, base_pull_score):
    schema = analysis.get('schema', load_cognition_schema())
    cfg = schema.get('control', {}).get('grounding_hold', {})
    evidence_state = action_evidence_sources(links, analysis)
    source_types = set(evidence_state.get('source_types', []))
    previous_source_types = {
        str(value)
        for value in item.get('grounding_source_types', [])
        if value
    }
    added_source_types = sorted(source_types - previous_source_types)
    source_diversity_count = evidence_state.get('source_diversity_count', 0)
    previous_source_diversity_count = safe_int(item.get('source_diversity_count', source_diversity_count), source_diversity_count)
    source_diversity_delta = source_diversity_count - previous_source_diversity_count
    weighted_evidence_score = safe_float(evidence_state.get('weighted_evidence_score', 0.0), 0.0)
    previous_weighted_evidence_score = safe_float(item.get('weighted_evidence_score', weighted_evidence_score), weighted_evidence_score)
    weighted_evidence_delta = round(weighted_evidence_score - previous_weighted_evidence_score, 3)
    repo_grounding_score = safe_float(repo_grounding.get('repo_grounding_score', 0.0), 0.0)
    previous_repo_grounding_score = safe_float(item.get('repo_grounding_score', repo_grounding_score), repo_grounding_score)
    repo_grounding_delta = round(repo_grounding_score - previous_repo_grounding_score, 3)
    previous_base_resistance_score = safe_float(item.get('base_resistance_score', item.get('resistance_score', base_resistance_score)), base_resistance_score)
    resistance_drop = round(previous_base_resistance_score - base_resistance_score, 3)
    appearance_count = max(1, safe_int(item.get('appearance_count', 0), 0))
    consecutive_appearances = max(1, safe_int(item.get('consecutive_appearances', 0), 0))
    evidence_delta = safe_float(resurfacing_state.get('evidence_delta', 0.0), 0.0)
    previous_base_pull_score = safe_float(item.get('base_architectural_pull_score', item.get('architectural_pull_score', base_pull_score)), base_pull_score)
    base_pull_delta = round(base_pull_score - previous_base_pull_score, 3)
    meaningful_alignment_min = safe_float(cfg.get('meaningful_alignment_min', 0.58), 0.58)
    meaningful_pull_min = safe_float(cfg.get('meaningful_pull_min', 0.42), 0.42)
    repeat_appearance_min = int(cfg.get('repeat_appearance_min', 2) or 2)
    repeat_consecutive_min = int(cfg.get('repeat_consecutive_min', 2) or 2)
    weak_repo_grounding_max = safe_float(cfg.get('weak_repo_grounding_max', 0.22), 0.22)
    weak_source_diversity_max = int(cfg.get('weak_source_diversity_max', 1) or 1)
    material_repo_grounding_delta = safe_float(cfg.get('material_repo_grounding_delta', 0.16), 0.16)
    material_evidence_delta = safe_float(cfg.get('material_evidence_delta', 0.1), 0.1)
    material_pull_delta = safe_float(cfg.get('material_pull_delta', 0.08), 0.08)
    material_resistance_drop = safe_float(cfg.get('material_resistance_drop', 0.08), 0.08)

    meaningful = base_alignment_score >= meaningful_alignment_min or base_pull_score >= meaningful_pull_min
    repeated = appearance_count >= repeat_appearance_min or consecutive_appearances >= repeat_consecutive_min
    material_repo_change = (
        repo_grounding_delta >= material_repo_grounding_delta
        or (repo_grounding.get('repo_structural_progress', False) and repo_grounding_score > previous_repo_grounding_score)
    )
    material_new_sources = bool(added_source_types)
    material_field_shift = (
        evidence_delta >= material_evidence_delta
        or base_pull_delta >= material_pull_delta
        or resistance_drop >= material_resistance_drop
        or resurfacing_state.get('resurfacing_classification') == 'genuine_reemergence'
    )
    material_change = material_repo_change or material_new_sources or material_field_shift

    if material_change:
        grounding_novelty_classification = 'new_grounding'
    elif repo_grounding_score <= weak_repo_grounding_max and source_diversity_count <= weak_source_diversity_max:
        grounding_novelty_classification = 'weak_grounding'
    else:
        grounding_novelty_classification = 'unchanged_grounding'

    novelty_components = [
        clamp_number(repo_grounding_delta / max(material_repo_grounding_delta, 0.001), 0.0, 1.0),
        1.0 if added_source_types else 0.0,
        clamp_number(evidence_delta / max(material_evidence_delta, 0.001), 0.0, 1.0),
        clamp_number(base_pull_delta / max(material_pull_delta, 0.001), 0.0, 1.0),
        clamp_number(resistance_drop / max(material_resistance_drop, 0.001), 0.0, 1.0),
    ]
    grounding_novelty_score = round(max(novelty_components), 3)

    hold_applies = bool(
        cfg.get('enabled', True)
        and meaningful
        and repeated
        and not material_change
        and resurfacing_state.get('resurfacing_classification') != 'genuine_reemergence'
    )
    hold_reason_parts = []
    if hold_applies:
        hold_reason_parts.append('still meaningful, but not newly actionable yet')
        if grounding_novelty_classification == 'weak_grounding':
            hold_reason_parts.append('repo grounding and source diversity are still too weak')
        else:
            hold_reason_parts.append('repo grounding and field evidence have not materially improved')
        if resurfacing_state.get('resurfacing_classification') == 'noisy_repetition':
            hold_reason_parts.append('resurfacing is repeating without better conditions')

    release_signals = []
    if not material_repo_change:
        release_signals.append('real repo change or stronger repo grounding')
    if not material_new_sources:
        release_signals.append('a new source type such as runtime truth or code-config evidence')
    if base_pull_delta < material_pull_delta:
        release_signals.append('meaningfully stronger architectural pull')
    if resistance_drop < material_resistance_drop:
        release_signals.append('meaningfully lower resistance')

    return {
        'grounding_novelty_classification': grounding_novelty_classification,
        'grounding_novelty_score': grounding_novelty_score,
        'grounding_hold_active': hold_applies,
        'grounding_hold_reason': '; '.join(hold_reason_parts),
        'grounding_release_signals': release_signals[:4],
        'grounding_source_types': evidence_state.get('source_types', []),
        'source_diversity_count': source_diversity_count,
        'source_diversity_delta': source_diversity_delta,
        'weighted_evidence_score': weighted_evidence_score,
        'weighted_evidence_delta': weighted_evidence_delta,
        'added_source_types': added_source_types,
        'repo_grounding_delta': repo_grounding_delta,
        'resistance_drop': resistance_drop,
        'base_pull_delta': base_pull_delta,
        'material_change_detected': material_change,
    }


def consultation_decision_signature(decision):
    parts = [
        decision.get('action_id', ''),
        decision.get('action_domain', ''),
        decision.get('consultation_purpose', ''),
        decision.get('specialist_id', ''),
        decision.get('consultation_mode', ''),
        decision.get('decision', ''),
        reason_signature(decision.get('reason', '')),
        decision.get('grounding_novelty_classification', ''),
        'hold' if decision.get('grounding_hold_active') else 'open',
    ]
    return '|'.join(str(part) for part in parts)


def latest_specialist_decision_entry(history_entries, action_id, action_domain):
    for entry in reversed(history_entries):
        if entry.get('kind') != 'decision':
            continue
        if action_id and entry.get('action_id') == action_id:
            return entry
        if action_domain and entry.get('action_domain') == action_domain:
            return entry
    return {}


def field_delta_hold_state(history_entries, field, target_id, direction, evidence_profile, schema):
    cfg = schema.get('control', {}).get('grounding_hold', {})
    window = int(cfg.get('field_repeat_window', 12) or 12)
    recent = target_history_entries(history_entries, field, target_id, direction, limit=window)
    if not recent:
        return {
            'hold_applies': False,
            'hold_reason': '',
        }
    latest = recent[-1]
    current_sources = set(evidence_profile.get('source_types', []))
    previous_sources = set(latest.get('evidence_sources', []))
    added_source_types = sorted(current_sources - previous_sources)
    weighted_evidence_gain = round(
        safe_float(evidence_profile.get('weighted_score', 0.0), 0.0)
        - safe_float(latest.get('weighted_evidence_score', 0.0), 0.0),
        3,
    )
    if (
        not added_source_types
        and weighted_evidence_gain < safe_float(cfg.get('field_min_weighted_evidence_gain', 0.22), 0.22)
        and len(recent) >= 2
    ):
        return {
            'hold_applies': True,
            'hold_reason': 'same field target is being pressured again without materially improved grounding',
            'added_source_types': added_source_types,
            'weighted_evidence_gain': weighted_evidence_gain,
        }
    return {
        'hold_applies': False,
        'hold_reason': '',
        'added_source_types': added_source_types,
        'weighted_evidence_gain': weighted_evidence_gain,
    }


def classify_action_resurfacing(item, field_evidence_score, base_alignment_score, base_pull_score):
    previous_judgment = item.get('direction_judgment', '')
    appearance_count = max(1, safe_int(item.get('appearance_count', 0), 0))
    consecutive_appearances = max(1, safe_int(item.get('consecutive_appearances', 0), 0))
    previous_evidence_score = safe_float(item.get('field_evidence_score', field_evidence_score), field_evidence_score)
    previous_pull_score = safe_float(item.get('architectural_pull_score', base_pull_score), base_pull_score)
    evidence_delta = round(field_evidence_score - previous_evidence_score, 3)
    pull_delta = round(base_pull_score - previous_pull_score, 3)
    resurfacing_despite_resistance = previous_judgment in ('pause', 'kill', 'hold_until_new_grounding') and appearance_count >= 2

    if not previous_judgment or appearance_count <= 1:
        resurfacing_classification = 'first_seen'
        resurfacing_reason = 'First appearance in the current action memory window.'
    elif previous_judgment == 'continue':
        resurfacing_classification = 'steady_reinforcement'
        resurfacing_reason = 'Recurring with an existing continue judgment, so modest reinforcement is allowed.'
    elif resurfacing_despite_resistance:
        if evidence_delta >= 0.1 or pull_delta >= 0.09 or (base_alignment_score >= 0.85 and base_pull_score >= 0.6):
            resurfacing_classification = 'genuine_reemergence'
            resurfacing_reason = 'Resurfacing follows a meaningful increase in field evidence or pull.'
        else:
            resurfacing_classification = 'noisy_repetition'
            resurfacing_reason = 'Resurfacing repeats despite resistance without enough new field evidence.'
    else:
        resurfacing_classification = 'steady_signal'
        resurfacing_reason = 'Still visible, but not yet a resistant resurfacing pattern.'

    return {
        'appearance_count': appearance_count,
        'consecutive_appearances': consecutive_appearances,
        'previous_judgment': previous_judgment,
        'previous_evidence_score': round(previous_evidence_score, 3),
        'evidence_delta': evidence_delta,
        'pull_delta': pull_delta,
        'resurfacing_despite_resistance': resurfacing_despite_resistance,
        'resurfacing_classification': resurfacing_classification,
        'resurfacing_reason': resurfacing_reason,
    }


def historical_action_influence(item, resurfacing_state):
    previous_judgment = resurfacing_state.get('previous_judgment', '')
    resurfacing_classification = resurfacing_state.get('resurfacing_classification', 'steady_signal')
    pull_adjustment = 0.0
    resistance_adjustment = 0.0
    alignment_adjustment = 0.0
    influence_state = 'neutral'
    influence_reason = 'No historical action influence applied yet.'

    if previous_judgment == 'continue':
        pull_adjustment += 0.04
        alignment_adjustment += 0.02
        influence_state = 'reinforced'
        influence_reason = 'Prior continue judgment allows modest reinforcement.'
    elif previous_judgment == 'pause':
        if resurfacing_classification == 'noisy_repetition':
            pull_adjustment -= 0.04
            resistance_adjustment += 0.03
            influence_state = 'damped'
            influence_reason = 'Repeated pause without new evidence is softly damped.'
        elif resurfacing_classification == 'genuine_reemergence':
            influence_state = 'visible'
            influence_reason = 'Earlier pause is kept visible because field evidence improved.'
        else:
            influence_state = 'visible'
            influence_reason = 'Pause keeps the candidate visible without promotion.'
    elif previous_judgment == 'kill':
        if resurfacing_classification == 'genuine_reemergence':
            influence_state = 'visible'
            influence_reason = 'Earlier kill is not enforced because new field evidence supports re-emergence.'
        else:
            pull_adjustment -= 0.08
            resistance_adjustment += 0.06
            influence_state = 'damped'
            influence_reason = 'Earlier kill softly damps resurfacing until new evidence appears.'
    elif previous_judgment == 'hold_until_new_grounding':
        if resurfacing_classification == 'genuine_reemergence':
            influence_state = 'visible'
            influence_reason = 'Earlier hold is lifted because conditions now show genuine re-emergence.'
        else:
            pull_adjustment -= 0.05
            resistance_adjustment += 0.02
            influence_state = 'held'
            influence_reason = 'Prior hold keeps the candidate meaningful but out of repeated pseudo-motion until grounding improves.'

    return {
        'alignment_adjustment': round(alignment_adjustment, 3),
        'resistance_adjustment': round(resistance_adjustment, 3),
        'pull_adjustment': round(pull_adjustment, 3),
        'influence_state': influence_state,
        'influence_reason': influence_reason,
    }


def build_action_direction_judgment(item, analysis, specialist_signal=None):
    snapshot = analysis.get('snapshot') or field_layer_snapshot()
    links = candidate_domain_links(item.get('domain', ''))
    repo_grounding = analysis.get('action_repo_grounding', {}).get(item.get('domain', ''), empty_action_repo_grounding())
    specialist_signal = specialist_signal or empty_specialist_signal()
    attractors_by_id = field_item_index(snapshot.get('attractors', {}))
    tensions_by_id = field_item_index(snapshot.get('tensions', {}))
    modes_by_id = field_item_index(snapshot.get('modes', {}))
    contradiction_by_id = {
        entry.get('target_id'): entry
        for entry in analysis.get('contradiction_persistence', [])
        if entry.get('target_id')
    }
    under_attended_by_id = {
        entry.get('target_id'): entry
        for entry in analysis.get('under_attended_recurring_tensions', [])
        if entry.get('target_id')
    }
    overdominant_ids = {
        entry.get('target_id')
        for entry in analysis.get('overdominant_attractors', [])
        if entry.get('target_id')
    }
    counterweight_by_target = {
        entry.get('target_id'): entry
        for entry in analysis.get('counterweight_awareness', [])
        if entry.get('target_id')
    }
    resonance_profiles = analysis.get('resonance_profiles', {})

    attractor_scores = [safe_float(attractors_by_id.get(target_id, {}).get('score', 0.0), 0.0) for target_id in links.get('attractors', [])]
    mode_scores = [safe_float(modes_by_id.get(target_id, {}).get('score', 0.0), 0.0) for target_id in links.get('modes', [])]
    attractor_resonance = [
        normalized_resonance_score(evidence_profile_for_target(analysis, 'attractors', target_id))
        for target_id in links.get('attractors', [])
    ]
    mode_resonance = [
        normalized_resonance_score(evidence_profile_for_target(analysis, 'modes', target_id))
        for target_id in links.get('modes', [])
    ]
    tension_scores = [safe_float(tensions_by_id.get(target_id, {}).get('score', 0.0), 0.0) for target_id in links.get('tensions', [])]

    attractor_alignment = average_score(attractor_scores)
    mode_alignment = average_score(mode_scores)
    resonance_alignment = average_score(attractor_resonance + mode_resonance)
    tension_resistance = average_score(tension_scores)
    field_evidence_score = round(average_score([attractor_alignment, mode_alignment, resonance_alignment]), 3)

    contradiction_penalty = 0.0
    resisting_tensions = []
    pull_tensions = []
    for target_id in links.get('tensions', []):
        contradiction = contradiction_by_id.get(target_id)
        if contradiction:
            resisting_tensions.append(tensions_by_id.get(target_id, {}).get('label', target_id))
            if contradiction.get('persistence_level') == 'high':
                contradiction_penalty += 0.16
            else:
                contradiction_penalty += 0.1
        if target_id in under_attended_by_id:
            pull_tensions.append(tensions_by_id.get(target_id, {}).get('label', target_id))

    counterweight_penalty = 0.0
    overdominance_penalty = 0.0
    counterweight_labels = []
    for target_id in links.get('attractors', []):
        if target_id in overdominant_ids:
            overdominance_penalty += 0.16
        counterweight = counterweight_by_target.get(target_id)
        if not counterweight:
            continue
        overlap = [
            tension_id for tension_id in counterweight.get('counterweight_tensions', [])
            if tension_id in set(links.get('tensions', []))
        ]
        if not overlap:
            continue
        counterweight_penalty += 0.12
        counterweight_labels.extend(
            tensions_by_id.get(tension_id, {}).get('label', tension_id)
            for tension_id in overlap
        )

    under_attended_pull_boost = min(0.24, 0.12 * len(pull_tensions))

    base_alignment_score = round(clamp_number(
        (attractor_alignment * 0.5) + (mode_alignment * 0.2) + (resonance_alignment * 0.3),
        0.0,
        1.0,
    ), 3)
    base_resistance_score = round(clamp_number(
        (tension_resistance * 0.68) + contradiction_penalty + counterweight_penalty + overdominance_penalty,
        0.0,
        1.0,
    ), 3)
    base_pull_score = round(clamp_number(
        base_alignment_score + under_attended_pull_boost - (base_resistance_score * 0.55),
        0.0,
        1.0,
    ), 3)
    resurfacing_state = classify_action_resurfacing(item, field_evidence_score, base_alignment_score, base_pull_score)
    grounding_hold = build_grounding_hold_state(
        item,
        links,
        analysis,
        repo_grounding,
        resurfacing_state,
        base_alignment_score,
        base_resistance_score,
        base_pull_score,
    )
    influence = historical_action_influence(item, resurfacing_state)
    alignment_score = round(clamp_number(
        base_alignment_score
        + influence.get('alignment_adjustment', 0.0)
        + repo_grounding.get('repo_alignment_adjustment', 0.0),
        0.0,
        1.0,
    ), 3)
    resistance_score = round(clamp_number(
        base_resistance_score
        + influence.get('resistance_adjustment', 0.0)
        + repo_grounding.get('repo_resistance_adjustment', 0.0),
        0.0,
        1.0,
    ), 3)
    architectural_pull_score = round(clamp_number(
        base_pull_score
        + influence.get('pull_adjustment', 0.0)
        + repo_grounding.get('repo_pull_adjustment', 0.0),
        0.0,
        1.0,
    ), 3)
    alignment_score = round(clamp_number(
        alignment_score + safe_float(specialist_signal.get('specialist_alignment_adjustment', 0.0), 0.0),
        0.0,
        1.0,
    ), 3)
    resistance_score = round(clamp_number(
        resistance_score + safe_float(specialist_signal.get('specialist_resistance_adjustment', 0.0), 0.0),
        0.0,
        1.0,
    ), 3)
    architectural_pull_score = round(clamp_number(
        architectural_pull_score + safe_float(specialist_signal.get('specialist_pull_adjustment', 0.0), 0.0),
        0.0,
        1.0,
    ), 3)

    if grounding_hold.get('grounding_hold_active'):
        direction_judgment = 'hold_until_new_grounding'
    elif resistance_score >= 0.82 and architectural_pull_score <= 0.22:
        direction_judgment = 'kill'
    elif architectural_pull_score >= 0.62 and alignment_score >= 0.78:
        direction_judgment = 'continue'
    elif architectural_pull_score >= 0.52 and resistance_score <= 0.78:
        direction_judgment = 'continue'
    else:
        direction_judgment = 'pause'

    aligned_labels = [
        attractors_by_id.get(target_id, {}).get('label', target_id)
        for target_id in links.get('attractors', [])
        if target_id in attractors_by_id
    ]
    reason_parts = []
    if aligned_labels:
        reason_parts.append(f"aligns with {', '.join(aligned_labels)}")
    if pull_tensions:
        reason_parts.append(f"also addresses under-attended pressure in {', '.join(pull_tensions)}")
    if resisting_tensions:
        reason_parts.append(f"meets resistance from {', '.join(dict.fromkeys(resisting_tensions))}")
    if counterweight_labels:
        reason_parts.append(f"needs counterweight discipline on {', '.join(dict.fromkeys(counterweight_labels))}")
    if repo_grounding.get('repo_grounding_reason'):
        reason_parts.append(repo_grounding.get('repo_grounding_reason'))
    if specialist_signal.get('specialist_signal_reason'):
        reason_parts.append(specialist_signal.get('specialist_signal_reason'))
    elif specialist_signal.get('specialist_consultation_reason') and specialist_signal.get('specialist_consultation_decision') == 'recommend_consultation':
        reason_parts.append(specialist_signal.get('specialist_consultation_reason'))
    if grounding_hold.get('grounding_hold_reason'):
        reason_parts.append(grounding_hold.get('grounding_hold_reason'))
    if not reason_parts:
        reason_parts.append('has limited field evidence either for or against it')

    influence_state = influence.get('influence_state', 'neutral')
    influence_reason = influence.get('influence_reason', '')
    if grounding_hold.get('grounding_hold_active'):
        influence_state = 'held'
        influence_reason = grounding_hold.get('grounding_hold_reason', influence_reason) or influence_reason

    return {
        'alignment_score': alignment_score,
        'resistance_score': resistance_score,
        'architectural_pull_score': architectural_pull_score,
        'direction_judgment': direction_judgment,
        'judgment_reason': '; '.join(reason_parts),
        'field_evidence_score': field_evidence_score,
        'base_alignment_score': base_alignment_score,
        'base_resistance_score': base_resistance_score,
        'base_architectural_pull_score': base_pull_score,
        'influence_state': influence_state,
        'influence_reason': influence_reason,
        'alignment_adjustment': influence.get('alignment_adjustment', 0.0),
        'resistance_adjustment': influence.get('resistance_adjustment', 0.0),
        'pull_adjustment': influence.get('pull_adjustment', 0.0),
        'grounding_novelty_classification': grounding_hold.get('grounding_novelty_classification', ''),
        'grounding_novelty_score': grounding_hold.get('grounding_novelty_score', 0.0),
        'grounding_hold_active': grounding_hold.get('grounding_hold_active', False),
        'grounding_hold_reason': grounding_hold.get('grounding_hold_reason', ''),
        'grounding_release_signals': grounding_hold.get('grounding_release_signals', []),
        'grounding_source_types': grounding_hold.get('grounding_source_types', []),
        'source_diversity_count': grounding_hold.get('source_diversity_count', 0),
        'source_diversity_delta': grounding_hold.get('source_diversity_delta', 0),
        'weighted_evidence_score': grounding_hold.get('weighted_evidence_score', 0.0),
        'weighted_evidence_delta': grounding_hold.get('weighted_evidence_delta', 0.0),
        'added_source_types': grounding_hold.get('added_source_types', []),
        'repo_grounding_delta': grounding_hold.get('repo_grounding_delta', 0.0),
        'resistance_drop': grounding_hold.get('resistance_drop', 0.0),
        'material_change_detected': grounding_hold.get('material_change_detected', False),
        'repo_grounding_score': repo_grounding.get('repo_grounding_score', 0.0),
        'repo_alignment_classification': repo_grounding.get('repo_alignment_classification', ''),
        'repo_grounding_reason': repo_grounding.get('repo_grounding_reason', ''),
        'repo_change_count': repo_grounding.get('repo_change_count', 0),
        'repo_grounding_paths': repo_grounding.get('repo_grounding_paths', []),
        'repo_structural_progress': repo_grounding.get('repo_structural_progress', False),
        'repo_alignment_adjustment': repo_grounding.get('repo_alignment_adjustment', 0.0),
        'repo_resistance_adjustment': repo_grounding.get('repo_resistance_adjustment', 0.0),
        'repo_pull_adjustment': repo_grounding.get('repo_pull_adjustment', 0.0),
        'specialist_signal_score': specialist_signal.get('specialist_signal_score', 0.0),
        'specialist_alignment_adjustment': specialist_signal.get('specialist_alignment_adjustment', 0.0),
        'specialist_resistance_adjustment': specialist_signal.get('specialist_resistance_adjustment', 0.0),
        'specialist_pull_adjustment': specialist_signal.get('specialist_pull_adjustment', 0.0),
        'specialist_signal_reason': specialist_signal.get('specialist_signal_reason', ''),
        'specialist_consultation_decision': specialist_signal.get('specialist_consultation_decision', 'no_consultation'),
        'specialist_consultation_status': specialist_signal.get('specialist_consultation_status', 'not_invoked'),
        'specialist_evaluation': specialist_signal.get('specialist_evaluation', ''),
        'specialist_recommended_specialist_id': specialist_signal.get('specialist_recommended_specialist_id', ''),
        'specialist_recommended_specialist_label': specialist_signal.get('specialist_recommended_specialist_label', ''),
        'specialist_consultation_mode': specialist_signal.get('specialist_consultation_mode', ''),
        'specialist_expected_gain': specialist_signal.get('specialist_expected_gain', 0.0),
        'specialist_current_uncertainty': specialist_signal.get('specialist_current_uncertainty', 0.0),
        'specialist_consultation_reason': specialist_signal.get('specialist_consultation_reason', ''),
        'specialist_competitive_alternative_id': specialist_signal.get('specialist_competitive_alternative_id', ''),
        'specialist_competitive_alternative_label': specialist_signal.get('specialist_competitive_alternative_label', ''),
        'appearance_count': resurfacing_state.get('appearance_count', 1),
        'consecutive_appearances': resurfacing_state.get('consecutive_appearances', 1),
        'resurfacing_despite_resistance': resurfacing_state.get('resurfacing_despite_resistance', False),
        'resurfacing_classification': resurfacing_state.get('resurfacing_classification', 'steady_signal'),
        'resurfacing_reason': resurfacing_state.get('resurfacing_reason', ''),
        'evidence_delta': resurfacing_state.get('evidence_delta', 0.0),
        'pull_delta': resurfacing_state.get('pull_delta', 0.0),
        'judgment_inputs': {
            'attractors': links.get('attractors', []),
            'tensions': links.get('tensions', []),
            'modes': links.get('modes', []),
            'constraints': links.get('constraints', []),
        },
    }


def empty_specialist_signal():
    return {
        'specialist_signal_score': 0.0,
        'specialist_alignment_adjustment': 0.0,
        'specialist_resistance_adjustment': 0.0,
        'specialist_pull_adjustment': 0.0,
        'specialist_signal_reason': '',
        'specialist_consultation_decision': 'no_consultation',
        'specialist_consultation_status': 'not_invoked',
        'specialist_evaluation': '',
        'specialist_recommended_specialist_id': '',
        'specialist_recommended_specialist_label': '',
        'specialist_consultation_mode': '',
        'specialist_expected_gain': 0.0,
        'specialist_current_uncertainty': 0.0,
        'specialist_consultation_reason': '',
        'specialist_competitive_alternative_id': '',
        'specialist_competitive_alternative_label': '',
    }


def specialist_registry_by_id(registry):
    return {
        item.get('id'): item
        for item in registry.get('specialists', [])
        if isinstance(item, dict) and item.get('id')
    }


def default_specialist_trust_profile(specialist):
    defaults = specialist.get('trust_defaults', {})
    return {
        'specialist_id': specialist.get('id', ''),
        'label': specialist.get('label', specialist.get('id', '')),
        'domain_reasoning': clamp_number(safe_float(defaults.get('domain_reasoning', 0.6), 0.6), 0.0, 1.0),
        'implementation_specificity': clamp_number(safe_float(defaults.get('implementation_specificity', 0.6), 0.6), 0.0, 1.0),
        'constraint_fidelity': clamp_number(safe_float(defaults.get('constraint_fidelity', 0.6), 0.6), 0.0, 1.0),
        'hallucination_risk': clamp_number(safe_float(defaults.get('hallucination_risk', 0.3), 0.3), 0.0, 1.0),
        'artifact_quality': clamp_number(safe_float(defaults.get('artifact_quality', 0.6), 0.6), 0.0, 1.0),
        'consultation_count': 0,
        'evaluated_consultations': 0,
        'accepted_count': 0,
        'partial_accept_count': 0,
        'rejected_count': 0,
        'deferred_count': 0,
        'historical_success': 0.5,
        'trust_score': 0.0,
    }


def specialist_trust_score(profile):
    positive = average_score([
        profile.get('domain_reasoning', 0.0),
        profile.get('implementation_specificity', 0.0),
        profile.get('constraint_fidelity', 0.0),
        profile.get('artifact_quality', 0.0),
        profile.get('historical_success', 0.5),
    ])
    hallucination_risk = safe_float(profile.get('hallucination_risk', 0.3), 0.3)
    return round(clamp_number(positive - (hallucination_risk * 0.35), 0.0, 1.0), 3)


def rebuild_specialist_trust_memory(registry, history, prior_memory=None):
    prior_profiles = {}
    if isinstance(prior_memory, dict) and isinstance(prior_memory.get('specialists'), dict):
        prior_profiles = prior_memory.get('specialists', {})
    memory = {'specialists': {}}
    registry_map = specialist_registry_by_id(registry)
    for specialist_id, specialist in registry_map.items():
        profile = default_specialist_trust_profile(specialist)
        prior_profile = prior_profiles.get(specialist_id, {})
        if isinstance(prior_profile, dict):
            for key in ('domain_reasoning', 'implementation_specificity', 'constraint_fidelity', 'hallucination_risk', 'artifact_quality'):
                if key in prior_profile:
                    profile[key] = clamp_number(safe_float(prior_profile.get(key, profile[key]), profile[key]), 0.0, 1.0)
        memory['specialists'][specialist_id] = profile
    for entry in history.get('entries', []):
        specialist_id = entry.get('specialist_id', '')
        evaluation = entry.get('eli_evaluation', '')
        profile = memory['specialists'].get(specialist_id)
        if not profile or evaluation not in SPECIALIST_EVALUATION_VALUES:
            continue
        profile['consultation_count'] += 1
        profile['evaluated_consultations'] += 1
        if evaluation == 'accept':
            profile['accepted_count'] += 1
            profile['domain_reasoning'] = clamp_number(profile['domain_reasoning'] + 0.012, 0.0, 1.0)
            profile['implementation_specificity'] = clamp_number(profile['implementation_specificity'] + 0.01, 0.0, 1.0)
            profile['constraint_fidelity'] = clamp_number(profile['constraint_fidelity'] + 0.012, 0.0, 1.0)
            profile['artifact_quality'] = clamp_number(profile['artifact_quality'] + 0.008, 0.0, 1.0)
            profile['hallucination_risk'] = clamp_number(profile['hallucination_risk'] - 0.01, 0.0, 1.0)
        elif evaluation == 'partial_accept':
            profile['partial_accept_count'] += 1
            profile['domain_reasoning'] = clamp_number(profile['domain_reasoning'] + 0.004, 0.0, 1.0)
            profile['constraint_fidelity'] = clamp_number(profile['constraint_fidelity'] + 0.004, 0.0, 1.0)
            profile['hallucination_risk'] = clamp_number(profile['hallucination_risk'] - 0.003, 0.0, 1.0)
        elif evaluation == 'reject':
            profile['rejected_count'] += 1
            profile['domain_reasoning'] = clamp_number(profile['domain_reasoning'] - 0.014, 0.0, 1.0)
            profile['constraint_fidelity'] = clamp_number(profile['constraint_fidelity'] - 0.012, 0.0, 1.0)
            profile['hallucination_risk'] = clamp_number(profile['hallucination_risk'] + 0.014, 0.0, 1.0)
        elif evaluation == 'defer_for_competitive_review':
            profile['deferred_count'] += 1
        evaluated = max(1, safe_int(profile.get('evaluated_consultations', 0), 0))
        profile['historical_success'] = round(clamp_number(
            (profile.get('accepted_count', 0) + (profile.get('partial_accept_count', 0) * 0.6)) / evaluated,
            0.0,
            1.0,
        ), 3)
    for profile in memory.get('specialists', {}).values():
        if not profile.get('evaluated_consultations'):
            profile['historical_success'] = 0.5
        profile['trust_score'] = specialist_trust_score(profile)
    memory['updated_at'] = now_iso()
    return memory


def action_uncertainty_score(item):
    alignment_score = safe_float(item.get('alignment_score', 0.0), 0.0)
    resistance_score = safe_float(item.get('resistance_score', 0.0), 0.0)
    pull_score = safe_float(item.get('architectural_pull_score', 0.0), 0.0)
    uncertainty = (1.0 - abs(alignment_score - resistance_score)) * 0.45
    if item.get('direction_judgment') == 'pause':
        uncertainty += 0.2
    elif item.get('direction_judgment') == 'hold_until_new_grounding':
        uncertainty += 0.08
    if 0.35 <= pull_score <= 0.65:
        uncertainty += 0.14
    if item.get('repo_alignment_classification') == 'productive_resistance':
        uncertainty += 0.08
    if item.get('resurfacing_classification') in ('genuine_reemergence', 'noisy_repetition'):
        uncertainty += 0.08
    return round(clamp_number(uncertainty, 0.0, 1.0), 3)


def action_contradiction_risk(item):
    resistance_score = safe_float(item.get('resistance_score', 0.0), 0.0)
    risk = resistance_score * 0.7
    repo_classification = item.get('repo_alignment_classification', '')
    if repo_classification == 'misaligned':
        risk += 0.16
    elif repo_classification == 'field_neglecting':
        risk += 0.1
    elif repo_classification == 'productive_resistance':
        risk += 0.05
    return round(clamp_number(risk, 0.0, 1.0), 3)


def specialist_semantic_match(item, specialist):
    specialist_id = specialist.get('id', '')
    domain = item.get('domain', '')
    text = lower_text(' '.join([
        domain,
        item.get('title', ''),
        item.get('summary', ''),
        item.get('probe', ''),
        item.get('judgment_reason', ''),
        item.get('repo_grounding_reason', ''),
    ]))
    score = ACTION_SPECIALIST_HINTS.get(domain, {}).get(specialist_id, 0.0)
    for token in specialist.get('domains', []) + specialist.get('strengths', []):
        normalized = lower_text(str(token).replace('_', ' '))
        if normalized and normalized in text:
            score += 0.05
    pattern_hits = 0
    for pattern in SPECIALIST_TEXT_PATTERNS.get(specialist_id, []):
        if re.search(pattern, text):
            pattern_hits += 1
    score += min(0.24, pattern_hits * 0.06)
    repo_paths = item.get('repo_grounding_paths', [])
    repo_text = lower_text(' '.join(repo_paths))
    if specialist_id == 'code_architecture_specialist_v1' and any(path.endswith(('.py', '.swift', '.json', '.yaml', '.yml')) for path in repo_paths):
        score += 0.08
    if specialist_id == 'visualization_specialist_v1' and any(token in repo_text for token in ('view', 'display', 'visual', 'layout', 'confidence')):
        score += 0.08
    if specialist_id == 'report_specialist_v1' and any(path.endswith('.md') or '/docs/' in path for path in repo_paths):
        score += 0.06
    if specialist_id == 'embedded_linux_specialist_v1' and any(token in repo_text for token in ('linux', 'device', 'camera', 'systemd')):
        score += 0.08
    if specialist_id == 'controls_specialist_v1' and any(token in repo_text for token in ('bldc', 'foc', 'telemetry', 'encoder')):
        score += 0.1
    return round(clamp_number(score, 0.0, 1.0), 3)


def specialist_artifact_requirement(item, specialist_id):
    domain = item.get('domain', '')
    repo_paths = item.get('repo_grounding_paths', [])
    if specialist_id == 'visualization_specialist_v1' and domain in ('subtitle placement', 'confidence display', 'visual hierarchy'):
        return 0.76
    if specialist_id == 'code_architecture_specialist_v1' and domain in ('memory/cache policy', 'phone/cloud boundary'):
        return 0.78
    if specialist_id == 'report_specialist_v1' and any(path.endswith('.md') for path in repo_paths):
        return 0.66
    if specialist_id == 'embedded_linux_specialist_v1' and any(token in lower_text(' '.join(repo_paths)) for token in ('device', 'linux', 'camera')):
        return 0.62
    if specialist_id == 'controls_specialist_v1' and any(token in lower_text(' '.join(repo_paths)) for token in ('bldc', 'foc', 'telemetry', 'encoder')):
        return 0.68
    return 0.18


def consultation_artifact_key(item, purpose):
    repo_paths = item.get('repo_grounding_paths', [])
    repo_text = lower_text(' '.join(repo_paths) + ' ' + item.get('title', '') + ' ' + item.get('summary', ''))
    if any(token in repo_text for token in ('schematic', 'wiring', 'sensor', 'power', 'connector', 'signal')):
        return 'schematics'
    if purpose == 'component_selection_review':
        return 'component_shortlists'
    if purpose in ('implementation_review', 'architecture_fork'):
        return 'subsystem_breakdowns'
    if purpose == 'interface_map':
        return 'interface_maps'
    if purpose == 'diagram_packaging' or any(path.endswith('.md') or '/docs/' in path for path in repo_paths):
        return 'report_packaging'
    if item.get('domain') in ('subtitle placement', 'confidence display', 'visual hierarchy'):
        return 'diagrams'
    return ''


def specialist_artifact_requirement_with_policy(item, specialist_id, routing_policy, purpose):
    score = specialist_artifact_requirement(item, specialist_id)
    artifact_key = consultation_artifact_key(item, purpose)
    artifact_cfg = routing_policy.get('build_artifact_bias', {}).get(artifact_key, {})
    preferred = artifact_cfg.get('preferred_specialists', [])
    if specialist_id in preferred:
        score = max(score, 0.76 if artifact_key in ('schematics', 'component_shortlists', 'subsystem_breakdowns') else 0.72)
    elif artifact_key and preferred:
        score = max(score, 0.28)
    return round(clamp_number(score, 0.0, 1.0), 3), artifact_key


def consultation_purpose(item, uncertainty_score):
    repo_paths = item.get('repo_grounding_paths', [])
    repo_text = lower_text(' '.join(repo_paths) + ' ' + item.get('title', '') + ' ' + item.get('summary', ''))
    if any(token in repo_text for token in ('schematic', 'wiring', 'connector', 'sensor', 'power')):
        return 'schematic_draft'
    if any(token in repo_text for token in ('component', 'bom', 'shortlist', 'part number')):
        return 'component_selection_review'
    if item.get('domain') in ('memory/cache policy', 'phone/cloud boundary'):
        if uncertainty_score >= 0.72 and item.get('repo_change_count', 0):
            return 'architecture_fork'
        return 'implementation_review'
    if item.get('domain') in ('subtitle placement', 'confidence display', 'visual hierarchy'):
        if any(path.endswith('.md') or '/docs/' in path for path in repo_paths):
            return 'diagram_packaging'
        return 'interface_map'
    if uncertainty_score >= 0.7 and item.get('direction_judgment') == 'pause':
        return 'persistent_uncertainty'
    if item.get('repo_alignment_classification') == 'productive_resistance' or safe_float(item.get('resistance_score', 0.0), 0.0) >= 0.72:
        return 'component_tradeoff'
    if item.get('repo_change_count', 0):
        return 'sanity_check'
    return 'domain_analysis'


def consultation_mode_allowed(policy, mode, purpose):
    rules = policy.get('consultation_mode_rules', {}).get(mode, {})
    allowed = rules.get('allowed_for', [])
    if not allowed:
        return True
    return purpose in allowed


def build_specialist_consultation_decisions(judged_items, analysis, registry, routing_policy, trust_memory):
    schema = analysis.get('schema', load_cognition_schema())
    config = specialist_consultation_config(schema)
    if not config.get('enabled', True):
        return []
    signals_cfg = routing_policy.get('signals', {})
    thresholds = routing_policy.get('thresholds', {})
    selection_cfg = config.get('selection', {})
    min_expected_gain = max(
        safe_float(thresholds.get('minimum_expected_gain', 0.12), 0.12),
        safe_float(selection_cfg.get('minimum_expected_gain', 0.12), 0.12),
    )
    min_semantic_match = max(
        safe_float(thresholds.get('minimum_semantic_match', 0.45), 0.45),
        safe_float(selection_cfg.get('minimum_semantic_match', 0.45), 0.45),
    )
    min_constraint_fidelity = max(
        safe_float(thresholds.get('minimum_constraint_fidelity', 0.6), 0.6),
        safe_float(selection_cfg.get('minimum_constraint_fidelity', 0.72), 0.72),
    )
    max_hallucination_risk = min(
        safe_float(thresholds.get('max_hallucination_risk_for_primary_use', 0.45), 0.45),
        safe_float(selection_cfg.get('max_hallucination_risk_for_primary_use', 0.45), 0.45),
    )
    high_uncertainty = max(
        safe_float(thresholds.get('high_uncertainty', 0.65), 0.65),
        safe_float(selection_cfg.get('high_uncertainty_threshold', 0.65), 0.65),
    )
    competitive_threshold = max(
        safe_float(thresholds.get('competitive_consultation', 0.46), 0.46),
        safe_float(selection_cfg.get('competitive_consultation_threshold', 0.46), 0.46),
    )
    safeguards = routing_policy.get('safeguards', {})
    min_gain_margin_for_competitive = safe_float(safeguards.get('minimum_expected_gain_margin_for_competitive', 0.06), 0.06)
    max_top_runner_gap_for_competitive = safe_float(safeguards.get('max_top_runner_gap_for_competitive', 0.12), 0.12)
    registry_profiles = specialist_registry_by_id(registry)
    trust_profiles = trust_memory.get('specialists', {})
    decisions = []
    for item in judged_items:
        if not isinstance(item, dict):
            continue
        uncertainty_score = action_uncertainty_score(item)
        contradiction_risk = action_contradiction_risk(item)
        purpose = consultation_purpose(item, uncertainty_score)
        candidates = []
        for specialist in registry.get('specialists', []):
            if not isinstance(specialist, dict) or not specialist.get('enabled', True):
                continue
            specialist_id = specialist.get('id', '')
            trust_profile = trust_profiles.get(specialist_id, default_specialist_trust_profile(specialist))
            semantic_match = specialist_semantic_match(item, specialist)
            historical_success = safe_float(trust_profile.get('historical_success', 0.5), 0.5)
            trust_score = safe_float(trust_profile.get('trust_score', specialist_trust_score(trust_profile)), 0.5)
            constraint_fidelity = safe_float(trust_profile.get('constraint_fidelity', 0.6), 0.6)
            hallucination_risk = safe_float(trust_profile.get('hallucination_risk', 0.3), 0.3)
            artifact_requirement, artifact_key = specialist_artifact_requirement_with_policy(item, specialist_id, routing_policy, purpose)
            expected_gain = (
                semantic_match * safe_float(signals_cfg.get('semantic_match_weight', 0.25), 0.25)
                + trust_score * safe_float(signals_cfg.get('trust_memory_weight', 0.2), 0.2)
                + uncertainty_score * safe_float(signals_cfg.get('current_uncertainty_weight', 0.2), 0.2)
                + artifact_requirement * safe_float(signals_cfg.get('artifact_requirement_weight', 0.15), 0.15)
                + historical_success * safe_float(signals_cfg.get('historical_success_weight', 0.1), 0.1)
                + constraint_fidelity * safe_float(signals_cfg.get('constraint_fidelity_weight', 0.1), 0.1)
                + contradiction_risk * safe_float(signals_cfg.get('contradiction_risk_weight', -0.1), -0.1)
                + hallucination_risk * safe_float(signals_cfg.get('hallucination_risk_weight', -0.1), -0.1)
            )
            candidates.append({
                'specialist_id': specialist_id,
                'specialist_label': specialist.get('label', specialist_id),
                'consultation_modes': specialist.get('consultation_modes', []),
                'semantic_match': round(clamp_number(semantic_match, 0.0, 1.0), 3),
                'historical_success': round(clamp_number(historical_success, 0.0, 1.0), 3),
                'trust_score': round(clamp_number(trust_score, 0.0, 1.0), 3),
                'constraint_fidelity': round(clamp_number(constraint_fidelity, 0.0, 1.0), 3),
                'hallucination_risk': round(clamp_number(hallucination_risk, 0.0, 1.0), 3),
                'artifact_requirement': round(clamp_number(artifact_requirement, 0.0, 1.0), 3),
                'artifact_key': artifact_key,
                'expected_gain': round(clamp_number(expected_gain, -1.0, 1.0), 3),
            })
        candidates.sort(key=lambda entry: entry.get('expected_gain', 0.0), reverse=True)
        top = candidates[0] if candidates else None
        runner_up = candidates[1] if len(candidates) > 1 else None
        decision = {
            'decision_id': sha256_text(f"{item.get('id', '')}|{item.get('domain', '')}|{item.get('title', '')}|specialist")[:16],
            'action_id': item.get('id', ''),
            'action_domain': item.get('domain', ''),
            'action_title': item.get('title', item.get('domain', 'candidate')),
            'consultation_purpose': purpose,
            'current_uncertainty': uncertainty_score,
            'contradiction_risk': contradiction_risk,
            'decision': 'no_consultation',
            'status': 'not_invoked',
            'specialist_id': '',
            'specialist_label': '',
            'consultation_mode': '',
            'expected_gain': 0.0,
            'semantic_match': 0.0,
            'trust_score': 0.0,
            'historical_success': 0.0,
            'constraint_fidelity': 0.0,
            'hallucination_risk': 0.0,
            'related_repo_paths': item.get('repo_grounding_paths', [])[:4],
            'reason': 'No specialist cleared the minimum expected-gain and semantic-match thresholds.',
            'competitive_alternative_id': '',
            'competitive_alternative_label': '',
            'grounding_novelty_classification': item.get('grounding_novelty_classification', ''),
            'grounding_hold_active': bool(item.get('grounding_hold_active', False)),
            'confidence': 0.48,
        }
        if item.get('grounding_hold_active') and item.get('direction_judgment') == 'hold_until_new_grounding':
            decision['reason'] = (
                item.get('grounding_hold_reason', '')
                or 'Candidate remains meaningful, but consultation is held until new grounding appears.'
            )
            decision['confidence'] = round(clamp_number(0.58 + (safe_float(item.get('grounding_novelty_score', 0.0), 0.0) * 0.12), 0.52, 0.78), 3)
            decisions.append(decision)
            continue
        if top:
            recommend = (
                top.get('expected_gain', 0.0) >= min_expected_gain
                and top.get('semantic_match', 0.0) >= min_semantic_match
                and top.get('constraint_fidelity', 0.0) >= min_constraint_fidelity
                and top.get('hallucination_risk', 1.0) <= max_hallucination_risk
            )
            decision.update({
                'specialist_id': top.get('specialist_id', ''),
                'specialist_label': top.get('specialist_label', ''),
                'expected_gain': top.get('expected_gain', 0.0),
                'semantic_match': top.get('semantic_match', 0.0),
                'trust_score': top.get('trust_score', 0.0),
                'historical_success': top.get('historical_success', 0.0),
                'constraint_fidelity': top.get('constraint_fidelity', 0.0),
                'hallucination_risk': top.get('hallucination_risk', 0.0),
            })
            recommended_mode = routing_policy.get('selection_policy', {}).get('default_mode', 'advisory')
            artifact_cfg = routing_policy.get('build_artifact_bias', {}).get(top.get('artifact_key', ''), {})
            artifact_mode = artifact_cfg.get('preferred_mode', '')
            if artifact_mode and artifact_mode in top.get('consultation_modes', []) and consultation_mode_allowed(routing_policy, artifact_mode, purpose):
                recommended_mode = artifact_mode
            competitive_purpose = purpose if consultation_mode_allowed(routing_policy, 'competitive', purpose) else 'persistent_uncertainty'
            if (
                uncertainty_score >= high_uncertainty
                and runner_up
                and runner_up.get('expected_gain', 0.0) >= competitive_threshold
                and top.get('expected_gain', 0.0) >= (min_expected_gain + min_gain_margin_for_competitive)
                and abs(top.get('expected_gain', 0.0) - runner_up.get('expected_gain', 0.0)) <= max_top_runner_gap_for_competitive
                and (not safeguards.get('require_high_uncertainty_for_competitive', True) or uncertainty_score >= high_uncertainty)
                and (not safeguards.get('require_runner_up_for_competitive', True) or bool(runner_up))
            ):
                if 'competitive' in top.get('consultation_modes', []) and consultation_mode_allowed(routing_policy, 'competitive', competitive_purpose):
                    recommended_mode = 'competitive'
                    decision['competitive_alternative_id'] = runner_up.get('specialist_id', '')
                    decision['competitive_alternative_label'] = runner_up.get('specialist_label', '')
            elif recommended_mode not in top.get('consultation_modes', []) or not consultation_mode_allowed(routing_policy, recommended_mode, purpose):
                if 'advisory' in top.get('consultation_modes', []) and consultation_mode_allowed(routing_policy, 'advisory', purpose):
                    recommended_mode = 'advisory'
                elif top.get('consultation_modes'):
                    recommended_mode = top.get('consultation_modes', ['advisory'])[0]
            decision['consultation_mode'] = recommended_mode
            if recommend:
                decision['decision'] = 'recommend_consultation'
                if recommended_mode == 'competitive' and decision.get('competitive_alternative_id'):
                    decision['reason'] = (
                        f"{top.get('specialist_label', '')} is a strong fit, but uncertainty remains high enough to defer toward competitive review with "
                        f"{decision.get('competitive_alternative_label', '') or decision.get('competitive_alternative_id', '')}."
                    )
                else:
                    decision['reason'] = (
                        f"{top.get('specialist_label', '')} can advise on {purpose.replace('_', ' ')} without overriding ELI judgment."
                    )
                decision['confidence'] = round(clamp_number(0.5 + (top.get('expected_gain', 0.0) * 0.35), 0.45, 0.88), 3)
            else:
                decision['reason'] = (
                    f"{top.get('specialist_label', '')} is the closest match, but expected gain {top.get('expected_gain', 0.0)} is still too weak for consultation."
                )
                decision['confidence'] = round(clamp_number(0.42 + (top.get('semantic_match', 0.0) * 0.2), 0.38, 0.72), 3)
        decisions.append(decision)
    return decisions


def record_specialist_consultation_decisions(history, decisions, timestamp):
    entries = history.setdefault('entries', [])
    for decision in decisions:
        entry = {
            'kind': 'decision',
            'timestamp': timestamp,
            'decision_id': decision.get('decision_id', ''),
            'action_id': decision.get('action_id', ''),
            'action_domain': decision.get('action_domain', ''),
            'action_title': decision.get('action_title', ''),
            'consultation_purpose': decision.get('consultation_purpose', ''),
            'specialist_id': decision.get('specialist_id', ''),
            'specialist_label': decision.get('specialist_label', ''),
            'consultation_mode': decision.get('consultation_mode', ''),
            'decision': decision.get('decision', 'no_consultation'),
            'status': decision.get('status', 'not_invoked'),
            'expected_gain': decision.get('expected_gain', 0.0),
            'semantic_match': decision.get('semantic_match', 0.0),
            'trust_score': decision.get('trust_score', 0.0),
            'historical_success': decision.get('historical_success', 0.0),
            'constraint_fidelity': decision.get('constraint_fidelity', 0.0),
            'hallucination_risk': decision.get('hallucination_risk', 0.0),
            'reason': decision.get('reason', ''),
            'related_repo_paths': decision.get('related_repo_paths', []),
            'grounding_novelty_classification': decision.get('grounding_novelty_classification', ''),
            'grounding_hold_active': bool(decision.get('grounding_hold_active', False)),
            'confidence': decision.get('confidence', 0.5),
        }
        latest = latest_specialist_decision_entry(entries, entry.get('action_id', ''), entry.get('action_domain', ''))
        if latest and consultation_decision_signature(latest) == consultation_decision_signature(entry):
            continue
        entries.append(entry)
    return history


def infer_specialist_effect_direction(entry):
    effect = lower_text(entry.get('effect_direction', ''))
    if effect in ('support', 'caution', 'oppose', 'mixed'):
        return effect
    text = lower_text(' '.join([
        entry.get('output_summary', ''),
        entry.get('summary', ''),
        entry.get('reason', ''),
    ]))
    if any(token in text for token in ('avoid', 'oppose', 'conflict', 'reject', 'block')):
        return 'oppose'
    if any(token in text for token in ('risk', 'caution', 'limit', 'defer', 'careful')):
        return 'caution'
    if any(token in text for token in ('support', 'prefer', 'adopt', 'proceed', 'use', 'implement')):
        return 'support'
    return 'mixed'


def evaluate_specialist_consultations(history, judged_items, analysis, routing_policy, trust_memory):
    action_by_id = {item.get('id'): item for item in judged_items if item.get('id')}
    action_by_domain = {item.get('domain'): item for item in judged_items if item.get('domain')}
    thresholds = routing_policy.get('thresholds', {})
    safeguards = routing_policy.get('safeguards', {})
    high_uncertainty = safe_float(thresholds.get('high_uncertainty', 0.65), 0.65)
    min_constraint_fidelity = safe_float(thresholds.get('minimum_constraint_fidelity', 0.6), 0.6)
    max_hallucination_risk = safe_float(thresholds.get('max_hallucination_risk_for_primary_use', 0.45), 0.45)
    evaluations = []
    for entry in history.get('entries', []):
        kind = entry.get('kind', '')
        has_output = bool(entry.get('output_summary') or entry.get('artifact_paths') or entry.get('artifact_path'))
        if kind not in ('consultation', 'consultation_result') and entry.get('status') != 'consulted':
            continue
        if not has_output:
            continue
        action = action_by_id.get(entry.get('action_id', '')) or action_by_domain.get(entry.get('action_domain', ''))
        trust_profile = trust_memory.get('specialists', {}).get(entry.get('specialist_id', ''), {})
        effect_direction = infer_specialist_effect_direction(entry)
        constraint_conflict = bool(entry.get('constraint_conflict', False) or entry.get('project_guardrail_conflict', False))
        constraint_fidelity = safe_float(entry.get('constraint_fidelity', trust_profile.get('constraint_fidelity', 0.6)), trust_profile.get('constraint_fidelity', 0.6))
        implementation_specificity = safe_float(entry.get('implementation_specificity', trust_profile.get('implementation_specificity', 0.6)), trust_profile.get('implementation_specificity', 0.6))
        hallucination_risk = safe_float(entry.get('hallucination_risk', trust_profile.get('hallucination_risk', 0.3)), trust_profile.get('hallucination_risk', 0.3))
        artifact_mode = entry.get('consultation_mode', '') in ('delegated_drafting', 'instrumental')
        has_reasoning_output = bool(entry.get('reasoning_evidence', False) or entry.get('output_type') == 'analysis')
        support_signal = safe_float(entry.get('observed_gain', 0.0), 0.0)
        if action and support_signal <= 0.0:
            if effect_direction == 'support':
                support_signal = average_score([action.get('alignment_score', 0.0), action.get('architectural_pull_score', 0.0)])
            elif effect_direction in ('caution', 'oppose'):
                support_signal = safe_float(action.get('resistance_score', 0.0), 0.0)
            else:
                support_signal = average_score([action.get('alignment_score', 0.0), 1.0 - safe_float(action.get('resistance_score', 0.0), 0.0)])
        uncertainty_score = action_uncertainty_score(action or {})
        evaluation = entry.get('eli_evaluation', '')
        reason = entry.get('eli_evaluation_reason', '')
        if evaluation not in SPECIALIST_EVALUATION_VALUES:
            if constraint_conflict or constraint_fidelity < min_constraint_fidelity or hallucination_risk > max_hallucination_risk:
                evaluation = 'reject'
                reason = 'ELI rejected the consultation because it conflicts with project constraints or trust thresholds.'
            elif entry.get('consultation_mode') == 'competitive' and uncertainty_score >= high_uncertainty and effect_direction == 'mixed':
                evaluation = 'defer_for_competitive_review'
                reason = 'ELI deferred this result for competitive review because the consultation remains unresolved at high uncertainty.'
            elif effect_direction == 'support' and support_signal >= 0.66 and implementation_specificity >= 0.62:
                evaluation = 'accept'
                reason = 'ELI accepted the consultation as supportive, specific, and constraint-compatible.'
            elif support_signal >= 0.42 or implementation_specificity >= 0.7:
                evaluation = 'partial_accept'
                reason = 'ELI accepted only the usable portion of the consultation and kept it advisory.'
            else:
                evaluation = 'reject'
                reason = 'ELI rejected the consultation because it did not add enough trustworthy, specific value.'
            if safeguards.get('artifact_generation_not_authoritative_reasoning', True) and artifact_mode and not has_reasoning_output and evaluation == 'accept':
                evaluation = 'partial_accept'
                reason = 'ELI kept artifact-oriented output subordinate by downgrading it to partial acceptance pending explicit reasoning review.'
            entry['eli_evaluation'] = evaluation
            entry['eli_evaluation_reason'] = reason
            entry['eli_evaluated_at'] = now_iso()
            entry['effect_direction'] = effect_direction
        evaluations.append({
            'action_id': entry.get('action_id', ''),
            'action_domain': entry.get('action_domain', ''),
            'specialist_id': entry.get('specialist_id', ''),
            'specialist_label': entry.get('specialist_label', entry.get('specialist_id', '')),
            'consultation_mode': entry.get('consultation_mode', ''),
            'evaluation': entry.get('eli_evaluation', ''),
            'effect_direction': entry.get('effect_direction', effect_direction),
            'reason': entry.get('eli_evaluation_reason', reason),
            'confidence': round(clamp_number(0.48 + (support_signal * 0.28), 0.4, 0.86), 3),
        })
    return evaluations


def build_specialist_action_signals(judged_items, decisions, evaluations):
    decisions_by_action = {item.get('action_id'): item for item in decisions if item.get('action_id')}
    decisions_by_domain = {item.get('action_domain'): item for item in decisions if item.get('action_domain')}
    evaluations_by_action = {}
    evaluations_by_domain = {}
    for item in evaluations:
        if item.get('action_id'):
            evaluations_by_action[item.get('action_id')] = item
        elif item.get('action_domain'):
            evaluations_by_domain[item.get('action_domain')] = item
    signals = {}
    for item in judged_items:
        signal = empty_specialist_signal()
        decision = decisions_by_action.get(item.get('id', '')) or decisions_by_domain.get(item.get('domain', ''))
        evaluation = evaluations_by_action.get(item.get('id', '')) or evaluations_by_domain.get(item.get('domain', ''))
        if decision:
            signal.update({
                'specialist_consultation_decision': decision.get('decision', 'no_consultation'),
                'specialist_consultation_status': decision.get('status', 'not_invoked'),
                'specialist_consultation_reason': decision.get('reason', ''),
            })
            if decision.get('decision') == 'recommend_consultation':
                signal.update({
                    'specialist_recommended_specialist_id': decision.get('specialist_id', ''),
                    'specialist_recommended_specialist_label': decision.get('specialist_label', ''),
                    'specialist_consultation_mode': decision.get('consultation_mode', ''),
                    'specialist_expected_gain': decision.get('expected_gain', 0.0),
                    'specialist_current_uncertainty': decision.get('current_uncertainty', 0.0),
                    'specialist_competitive_alternative_id': decision.get('competitive_alternative_id', ''),
                    'specialist_competitive_alternative_label': decision.get('competitive_alternative_label', ''),
                })
        if evaluation:
            effect_direction = evaluation.get('effect_direction', '')
            evaluation_kind = evaluation.get('evaluation', '')
            signal['specialist_evaluation'] = evaluation_kind
            signal['specialist_signal_reason'] = evaluation.get('reason', '')
            signal['specialist_consultation_status'] = 'evaluated'
            if evaluation_kind == 'accept':
                signal['specialist_signal_score'] = 0.68
                if effect_direction == 'support':
                    signal['specialist_alignment_adjustment'] = 0.018
                    signal['specialist_pull_adjustment'] = 0.024
                elif effect_direction in ('caution', 'oppose'):
                    signal['specialist_resistance_adjustment'] = 0.02
                    signal['specialist_pull_adjustment'] = -0.014
            elif evaluation_kind == 'partial_accept':
                signal['specialist_signal_score'] = 0.42
                if effect_direction == 'support':
                    signal['specialist_alignment_adjustment'] = 0.008
                    signal['specialist_pull_adjustment'] = 0.012
                elif effect_direction in ('caution', 'oppose'):
                    signal['specialist_resistance_adjustment'] = 0.01
                    signal['specialist_pull_adjustment'] = -0.008
            elif evaluation_kind == 'defer_for_competitive_review':
                signal['specialist_signal_reason'] = evaluation.get('reason', '')
            else:
                signal['specialist_signal_reason'] = evaluation.get('reason', '')
        signals[item.get('id') or item.get('domain', '')] = signal
    return signals


def build_specialist_consultation_context(judged_items, analysis, timestamp):
    registry = load_specialist_registry()
    routing_policy = load_specialist_routing_policy()
    history = load_specialist_consultation_history()
    prior_memory = load_specialist_trust_memory()
    trust_memory = rebuild_specialist_trust_memory(registry, history, prior_memory)
    decisions = build_specialist_consultation_decisions(judged_items, analysis, registry, routing_policy, trust_memory)
    history = record_specialist_consultation_decisions(history, decisions, timestamp)
    evaluations = evaluate_specialist_consultations(history, judged_items, analysis, routing_policy, trust_memory)
    trust_memory = rebuild_specialist_trust_memory(registry, history, trust_memory)
    save_specialist_consultation_history(history)
    save_specialist_trust_memory(trust_memory)
    signals = build_specialist_action_signals(judged_items, decisions, evaluations)
    return {
        'registry': registry,
        'routing_policy': routing_policy,
        'trust_memory': trust_memory,
        'history': history,
        'decisions': decisions,
        'evaluations': evaluations,
        'signals': signals,
    }


def enrich_action_inbox_with_reflection(analysis):
    data = load_action_inbox()
    action_memory = load_action_memory()
    memory_items = {item.get('id'): item for item in action_memory.get('items', [])}
    items = []
    for item in data.get('items', []):
        if not isinstance(item, dict):
            continue
        merged = dict(memory_items.get(item.get('id'), {}))
        merged.update(item)
        items.append(merged)
    if not items:
        empty_context = {
            'registry': {'specialists': []},
            'routing_policy': {},
            'trust_memory': {'specialists': {}},
            'history': {'entries': []},
            'decisions': [],
            'evaluations': [],
            'signals': {},
        }
        return [], data, empty_context
    judged_at = now_iso()

    provisional_items = []
    for item in items:
        if not isinstance(item, dict):
            continue
        provisional = dict(item)
        provisional.update(build_action_direction_judgment(item, analysis))
        provisional['last_judged_at'] = judged_at
        provisional_items.append(provisional)

    specialist_context = build_specialist_consultation_context(provisional_items, analysis, judged_at)
    specialist_signals = specialist_context.get('signals', {})

    ranked_items = []
    for item in items:
        if not isinstance(item, dict):
            continue
        signal = specialist_signals.get(item.get('id', '')) or specialist_signals.get(item.get('domain', '')) or empty_specialist_signal()
        enriched = dict(item)
        enriched.update(build_action_direction_judgment(item, analysis, signal))
        enriched['last_judged_at'] = judged_at
        ranked_items.append(enriched)

    sorted_items = sorted(
        ranked_items,
        key=lambda entry: (
            {'continue': 0, 'pause': 1, 'hold_until_new_grounding': 2, 'kill': 3}.get(entry.get('direction_judgment', 'pause'), 4),
            -safe_float(entry.get('architectural_pull_score', 0.0), 0.0),
            safe_float(entry.get('resistance_score', 0.0), 0.0),
            entry.get('title', ''),
        ),
    )
    rank_by_id = {
        entry.get('id'): index + 1
        for index, entry in enumerate(sorted_items)
        if entry.get('id')
    }
    judgment_rows = []
    updated_items = []
    for entry in ranked_items:
        enriched = dict(entry)
        enriched['judgment_rank'] = rank_by_id.get(entry.get('id'), 0)
        updated_items.append(enriched)
        judgment_rows.append({
            'id': enriched.get('id', ''),
            'title': enriched.get('title', enriched.get('domain', 'candidate')),
            'domain': enriched.get('domain', ''),
            'alignment_score': enriched.get('alignment_score', 0.0),
            'resistance_score': enriched.get('resistance_score', 0.0),
            'architectural_pull_score': enriched.get('architectural_pull_score', 0.0),
            'direction_judgment': enriched.get('direction_judgment', 'pause'),
            'repo_grounding_score': enriched.get('repo_grounding_score', 0.0),
            'repo_grounding_delta': enriched.get('repo_grounding_delta', 0.0),
            'repo_alignment_classification': enriched.get('repo_alignment_classification', ''),
            'repo_change_count': enriched.get('repo_change_count', 0),
            'grounding_novelty_classification': enriched.get('grounding_novelty_classification', ''),
            'grounding_novelty_score': enriched.get('grounding_novelty_score', 0.0),
            'grounding_hold_active': enriched.get('grounding_hold_active', False),
            'grounding_hold_reason': enriched.get('grounding_hold_reason', ''),
            'grounding_release_signals': enriched.get('grounding_release_signals', []),
            'specialist_consultation_decision': enriched.get('specialist_consultation_decision', 'no_consultation'),
            'specialist_recommended_specialist_label': enriched.get('specialist_recommended_specialist_label', ''),
            'specialist_consultation_mode': enriched.get('specialist_consultation_mode', ''),
            'specialist_evaluation': enriched.get('specialist_evaluation', ''),
            'specialist_signal_score': enriched.get('specialist_signal_score', 0.0),
            'reason': '; '.join(part for part in [
                enriched.get('judgment_reason', ''),
                enriched.get('influence_reason', ''),
                enriched.get('grounding_hold_reason', '') if enriched.get('grounding_hold_active') else '',
                enriched.get('resurfacing_reason', '') if enriched.get('resurfacing_classification') in ('noisy_repetition', 'genuine_reemergence') else '',
            ] if part),
            'influence_state': enriched.get('influence_state', 'neutral'),
            'influence_reason': enriched.get('influence_reason', ''),
            'resurfacing_classification': enriched.get('resurfacing_classification', 'steady_signal'),
            'resurfacing_reason': enriched.get('resurfacing_reason', ''),
            'resurfacing_despite_resistance': enriched.get('resurfacing_despite_resistance', False),
            'appearance_count': enriched.get('appearance_count', 1),
            'rank': enriched.get('judgment_rank', 0),
            'confidence': round(clamp_number(
                0.45 + (safe_float(enriched.get('alignment_score', 0.0), 0.0) * 0.25) + (safe_float(enriched.get('architectural_pull_score', 0.0), 0.0) * 0.2),
                0.35,
                0.92,
            ), 3),
        })

    judgment_rows.sort(key=lambda entry: entry.get('rank', 0) or 999)
    data['items'] = updated_items
    data['judged_at'] = judged_at
    data['specialist_consultation'] = {
        'generated_at': judged_at,
        'decisions': specialist_context.get('decisions', []),
        'evaluations': specialist_context.get('evaluations', []),
    }
    save_action_inbox(data)
    save_action_memory({
        'source': 'reflect_action_memory',
        'judged_at': judged_at,
        'items': updated_items,
    })
    return judgment_rows, data, specialist_context


def render_reflection_analysis_context(analysis):
    lines = ['# Reflection Evidence Analysis', '## Source Weighting']
    for bucket, weight in analysis.get('source_weighting', {}).items():
        lines.append(f'- {bucket}: weight {weight}')
    lines.append('')
    lines.append('## Resonance Signals')
    resonance_signals = analysis.get('resonance_signals', [])
    if not resonance_signals:
        lines.append('- none')
    else:
        for item in resonance_signals:
            lines.append(
                f"- {item.get('field')}/{item.get('target_id')}: {item.get('repetition_kind')} across {', '.join(item.get('source_types', []))} | weighted_score {item.get('weighted_score')} | reason: {item.get('reason')}"
            )
    lines.append('')
    lines.append('## Contradiction Persistence Heuristics')
    contradiction_items = analysis.get('contradiction_persistence', [])
    if not contradiction_items:
        lines.append('- none')
    else:
        for item in contradiction_items:
            lines.append(
                f"- {item.get('target_id')}: level {item.get('persistence_level')} | reason: {item.get('reason')}"
            )
    lines.append('')
    lines.append('## Over-Dominant Attractors')
    dominant_items = analysis.get('overdominant_attractors', [])
    if not dominant_items:
        lines.append('- none')
    else:
        for item in dominant_items:
            lines.append(f"- {item.get('target_id')}: {item.get('reason')}")
    lines.append('')
    lines.append('## Under-Attended Recurring Tensions')
    recurring_items = analysis.get('under_attended_recurring_tensions', [])
    if not recurring_items:
        lines.append('- none')
    else:
        for item in recurring_items:
            lines.append(f"- {item.get('target_id')}: {item.get('reason')}")
    lines.append('')
    lines.append('## Reinforcement Loops')
    loop_items = analysis.get('reinforcement_loops', [])
    if not loop_items:
        lines.append('- none')
    else:
        for item in loop_items:
            lines.append(f"- {item.get('field')}/{item.get('target_id')}: {item.get('reason')}")
    lines.append('')
    lines.append('## Counterweight Awareness')
    counter_items = analysis.get('counterweight_awareness', [])
    if not counter_items:
        lines.append('- none')
    else:
        for item in counter_items:
            lines.append(f"- {item.get('target_id')}: {item.get('reason')}")
    lines.append('')
    lines.append('## Cooling Candidates')
    cooling_items = analysis.get('cooling_candidates', [])
    if not cooling_items:
        lines.append('- none')
    else:
        for item in cooling_items:
            lines.append(f"- {item.get('target_id')}: {item.get('reason')} | suggested_delta {item.get('suggested_delta')}")
    lines.append('')
    lines.append('## Neglected Persistent Tensions')
    neglected_items = analysis.get('neglected_persistent_tensions', [])
    if not neglected_items:
        lines.append('- none')
    else:
        for item in neglected_items:
            lines.append(f"- {item.get('target_id')}: {item.get('reason')} | suggested_delta {item.get('suggested_delta')}")
    lines.append('')
    lines.append('## Field Imbalance Patterns')
    imbalance_items = analysis.get('field_imbalance_patterns', [])
    if not imbalance_items:
        lines.append('- none')
    else:
        for item in imbalance_items:
            lines.append(f"- {item.get('target_id')}: {item.get('reason')}")
    lines.append('')
    lines.append('## Repo Change Candidates')
    repo_candidates = analysis.get('repo_change_candidates', [])
    if not repo_candidates:
        lines.append('- none')
    else:
        for item in repo_candidates:
            domains = ', '.join(item.get('matched_domains', [])) or 'none'
            targets = ', '.join(item.get('matched_field_targets', [])) or 'none'
            lines.append(
                f"- {item.get('relative_path')}: {item.get('classification')} | surface {item.get('surface')} | domains {domains} | targets {targets} | reason: {item.get('reason')}"
            )
    lines.append('')
    lines.append('## Repo Alignment Observations')
    repo_observations = analysis.get('repo_alignment_observations', [])
    if not repo_observations:
        lines.append('- none')
    else:
        for item in repo_observations:
            lines.append(
                f"- {item.get('classification')}: {item.get('reason')} | paths {', '.join(item.get('related_paths', [])) or 'none'}"
            )
    lines.append('')
    lines.append('## Field Diff Alignment Patterns')
    diff_patterns = analysis.get('field_diff_alignment_patterns', [])
    if not diff_patterns:
        lines.append('- none')
    else:
        for item in diff_patterns:
            target = item.get('target_id', '') or item.get('label', '')
            lines.append(
                f"- {item.get('classification')}: {item.get('field')}/{target} | {item.get('reason')} | paths {', '.join(item.get('related_paths', [])) or 'none'}"
            )
    return '\n'.join(lines) + '\n'


def evidence_profile_for_target(analysis, field, target_id):
    return analysis.get('resonance_profiles', {}).get(concept_profile_key(field, target_id), {
        'field': field,
        'target_id': target_id,
        'source_types': [],
        'source_counts': {},
        'source_paths': {},
        'weighted_score': 0.0,
        'repetition_kind': 'weak_signal',
    })


def evidence_weight_multiplier(profile):
    source_types = set(profile.get('source_types', []))
    weighted_score = safe_float(profile.get('weighted_score', 0.0), 0.0)
    multiplier = 0.9
    if source_types & {'runtime_truth', 'code_config'}:
        multiplier += 0.18
    if len(source_types) >= 2:
        multiplier += 0.08
    if source_types and source_types <= {'reports', 'eli_docs'}:
        multiplier -= 0.06
    if weighted_score >= 3.0:
        multiplier += 0.08
    elif weighted_score < 1.0:
        multiplier -= 0.08
    return round(clamp_number(multiplier, 0.7, 1.35), 3)


def render_field_layer_context():
    snapshot = field_layer_snapshot()
    lines = ['# ELI V2 Field Layer']
    for name in ('attractors', 'tensions', 'constraints', 'modes'):
        payload = snapshot.get(name, {})
        label = payload.get('field', name).replace('_', ' ').title()
        lines.append(f'\n## {label}')
        if name == 'modes' and payload.get('current_mode'):
            lines.append(f"- current mode: {payload.get('current_mode')}")
        items = payload.get('items', [])
        if not items:
            lines.append('- no items yet')
            continue
        for item in items:
            item_id = item.get('id', 'unknown')
            item_label = item.get('label') or item_id
            summary = item.get('summary') or ''
            extras = []
            for key in ('score', 'strength', 'pressure', 'type'):
                value = item.get(key)
                if value:
                    extras.append(f'{key}: {value}')
            suffix = f" ({'; '.join(extras)})" if extras else ''
            lines.append(f"- [{item_id}] {item_label}: {summary}{suffix}")
    return '\n'.join(lines) + '\n'


def path_within(path, roots):
    for root in roots:
        try:
            path.relative_to(root)
            return True
        except Exception:
            continue
    return False


def transcriptlab_watch_files():
    files = []
    for root in BUILD_WATCH_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob('*'):
            if not p.is_file():
                continue
            if IGNORE_DIR_NAMES & set(p.parts):
                continue
            files.append(p)
    return files


def transcriptlab_build_summary_is_stale(changes):
    if not BUILD_SUMMARY_PATH.exists():
        return True
    if any(path_within(p, BUILD_WATCH_ROOTS) for p, _ in changes):
        return True
    try:
        summary_mtime = BUILD_SUMMARY_PATH.stat().st_mtime
    except Exception:
        return True
    source_files = transcriptlab_watch_files()
    if not source_files:
        return False
    latest_source_mtime = max(p.stat().st_mtime for p in source_files)
    return latest_source_mtime > summary_mtime


def refresh_transcriptlab_build_summary_if_needed(changes):
    if not transcriptlab_build_summary_is_stale(changes):
        return {"ran": False, "status": "fresh", "summary_path": str(BUILD_SUMMARY_PATH)}
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    started_at = now_iso()
    try:
        result = subprocess.run(
            ["python3", str(BUILD_CAPTURE_SCRIPT_PATH)],
            cwd=str(BASE),
            capture_output=True,
            text=True,
            check=False,
        )
        status = "ok" if result.returncode == 0 else "error"
        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        return {
            "ran": True,
            "status": status,
            "started_at": started_at,
            "finished_at": now_iso(),
            "summary_path": stdout or str(BUILD_SUMMARY_PATH),
            "error_text": stderr,
        }
    except Exception as exc:
        return {
            "ran": True,
            "status": "error",
            "started_at": started_at,
            "finished_at": now_iso(),
            "summary_path": str(BUILD_SUMMARY_PATH),
            "error_text": str(exc),
        }


def now_iso():
    return dt.datetime.now().isoformat(timespec='seconds')


def write_runtime_state(**state):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    merged = {}
    if RUNTIME_STATE_PATH.exists():
        try:
            merged.update(json.loads(RUNTIME_STATE_PATH.read_text(encoding='utf-8')))
        except Exception:
            pass
    merged.update({
        'updated_at': now_iso(),
        'pid': os.getpid(),
    })
    merged.update(state)
    RUNTIME_STATE_PATH.write_text(json.dumps(merged, indent=2), encoding='utf-8')


def load_operator_guidance():
    if not OPERATOR_GUIDANCE_PATH.exists():
        return None
    try:
        data = json.loads(OPERATOR_GUIDANCE_PATH.read_text(encoding='utf-8'))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    return data


def load_action_inbox():
    if not ACTION_INBOX_PATH.exists():
        return {"items": []}
    try:
        data = json.loads(ACTION_INBOX_PATH.read_text(encoding='utf-8'))
    except Exception:
        return {"items": []}
    if not isinstance(data, dict):
        return {"items": []}
    if not isinstance(data.get('items'), list):
        data['items'] = []
    return data


def load_action_memory():
    if not ACTION_MEMORY_PATH.exists():
        return {"items": []}
    try:
        data = json.loads(ACTION_MEMORY_PATH.read_text(encoding='utf-8'))
    except Exception:
        return {"items": []}
    if not isinstance(data, dict):
        return {"items": []}
    if not isinstance(data.get('items'), list):
        data['items'] = []
    return data


def save_action_inbox(data):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    data['updated_at'] = now_iso()
    ACTION_INBOX_PATH.write_text(json.dumps(data, indent=2), encoding='utf-8')


def save_action_memory(data):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    data['updated_at'] = now_iso()
    ACTION_MEMORY_PATH.write_text(json.dumps(data, indent=2), encoding='utf-8')


def load_specialist_consultation_history():
    data = load_json_file(SPECIALIST_CONSULTATION_HISTORY_PATH, {'entries': []})
    if not isinstance(data, dict):
        data = {'entries': []}
    if not isinstance(data.get('entries'), list):
        data['entries'] = []
    return data


def save_specialist_consultation_history(data):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    data['updated_at'] = now_iso()
    data['entries'] = data.get('entries', [])[-600:]
    SPECIALIST_CONSULTATION_HISTORY_PATH.write_text(json.dumps(data, indent=2), encoding='utf-8')


def load_specialist_trust_memory():
    data = load_json_file(SPECIALIST_TRUST_MEMORY_PATH, {'specialists': {}})
    if not isinstance(data, dict):
        data = {'specialists': {}}
    specialists = data.get('specialists', {})
    if not isinstance(specialists, dict):
        specialists = {}
    data['specialists'] = specialists
    return data


def save_specialist_trust_memory(data):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    data['updated_at'] = now_iso()
    SPECIALIST_TRUST_MEMORY_PATH.write_text(json.dumps(data, indent=2), encoding='utf-8')


def load_json_file(path, fallback):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return fallback


def project_scorecard_config():
    data = load_json_file(SCORECARD_CONFIG_PATH, {"dimensions": []})
    if not isinstance(data, dict):
        return {"dimensions": []}
    if not isinstance(data.get('dimensions'), list):
        data['dimensions'] = []
    return data


SCORECARD_ALLOWED_STATUSES = {'on_track', 'needs_attention', 'blocked', 'unknown'}
SCORECARD_ALLOWED_GROUNDING_STATUSES = {'grounded', 'weakly_grounded', 'limited_evidence', 'unknown'}


def normalize_signal_key(value):
    return re.sub(r'[^a-z0-9]+', '_', str(value or '').strip().lower()).strip('_')


def normalize_scorecard_status(value):
    status = normalize_signal_key(value)
    if status in SCORECARD_ALLOWED_STATUSES:
        return status
    return 'unknown'


def normalize_scorecard_grounding_status(value):
    status = normalize_signal_key(value)
    if status in SCORECARD_ALLOWED_GROUNDING_STATUSES:
        return status
    return 'unknown'


REALITY_ASSESSMENT_ALIASES = {
    'subtitle_placement': 'subtitle_clarity',
    'subtitle_placement_feasibility': 'subtitle_clarity',
    'subtitle_clarity': 'subtitle_clarity',
    'confidence_display': 'confidence_display',
    'confidence_display_feasibility': 'confidence_display',
    'memory_caching': 'memory_trust',
    'memory_cache_policy': 'memory_trust',
    'memory_support': 'memory_trust',
    'memory_trust': 'memory_trust',
    'phone_cloud_boundary': 'phone_first_runtime',
    'phone_cloud_boundary_feasibility': 'phone_first_runtime',
    'phone_first_runtime': 'phone_first_runtime',
    'visual_hierarchy': 'discreet_ux_vs_visual_clarity',
    'visual_hierarchy_feasibility': 'discreet_ux_vs_visual_clarity',
    'privacy_vs_usefulness': 'privacy_vs_usefulness',
    'latency_vs_richness': 'latency_vs_richness',
    'discreet_ux_vs_visual_clarity': 'discreet_ux_vs_visual_clarity',
    'frame_touch_only_v1_interaction': 'frame_touch_only_v1_interaction',
    'implementation_grounding': 'implementation_grounding',
}


def store_reality_assessment(entries, label, target_id, judgment, detail):
    key = REALITY_ASSESSMENT_ALIASES.get(normalize_signal_key(target_id or label), normalize_signal_key(target_id or label))
    entry = {
        'label': label,
        'target_id': key,
        'judgment': normalize_signal_key(judgment),
        'detail': compact_text_excerpt(detail, 280),
    }
    for candidate in {
        key,
        normalize_signal_key(label),
        normalize_signal_key(target_id),
        REALITY_ASSESSMENT_ALIASES.get(normalize_signal_key(label), ''),
    }:
        if candidate:
            entries[candidate] = entry


def parse_reality_assessments(text):
    entries = {}
    if not text:
        return entries
    legacy_pattern = re.compile(r'^###\s+(.+?)(?:\s+\[([^\]]+)\])?\s*$([\s\S]*?)(?=^###\s+|\Z)', flags=re.MULTILINE)
    for match in legacy_pattern.finditer(text):
        label = (match.group(1) or '').strip()
        target_id = normalize_signal_key(match.group(2) or label)
        body = (match.group(3) or '').strip()
        judgment = ''
        detail = compact_text_excerpt(body, 280)
        bullet = re.search(r'-\s+\*\*(.+?)\*\*:\s*(.+)', body)
        if bullet:
            judgment = normalize_signal_key(bullet.group(1))
            detail = compact_text_excerpt(bullet.group(2), 280)
        store_reality_assessment(entries, label, target_id, judgment, detail)
    feasibility_pattern = re.compile(r'^###\s+(.+?)\s+Feasibility\s*$([\s\S]*?)(?=^###\s+|\Z)', flags=re.MULTILINE)
    for match in feasibility_pattern.finditer(text):
        heading = (match.group(1) or '').strip()
        body = (match.group(2) or '').strip()
        label_match = re.search(r'\*\*(.+?)\*\*:\s*(.+)', body, flags=re.DOTALL)
        label = label_match.group(1).strip() if label_match else heading
        detail = label_match.group(2).strip() if label_match else body
        judgment_match = re.search(r'\*\*(feasible now|feasible later|likely waste of time|assumptions needing evidence)\*\*', detail, flags=re.IGNORECASE)
        if not judgment_match:
            judgment_match = re.search(r'\b(feasible now|feasible later|likely waste of time|assumptions needing evidence)\b', detail, flags=re.IGNORECASE)
        judgment = judgment_match.group(1) if judgment_match else ''
        store_reality_assessment(entries, label, heading, judgment, detail)
    bullet_pattern = re.compile(r'^\s*(?:[-*]|\d+\.)\s+\*\*(.+?)(?:\s+\(([^)]+)\))?\*\*:\s*(.+)$', flags=re.MULTILINE)
    for match in bullet_pattern.finditer(text):
        label = (match.group(1) or '').strip()
        target_id = (match.group(2) or '').strip()
        detail = (match.group(3) or '').strip()
        judgment_match = re.search(r'\b(feasible now|feasible later|likely waste of time|assumptions needing evidence)\b', detail, flags=re.IGNORECASE)
        judgment = judgment_match.group(1) if judgment_match else ''
        store_reality_assessment(entries, label, target_id, judgment, detail)
    return entries


def scorecard_reflect_state():
    state = load_json_file(REFLECT_STATE_PATH, {})
    if not isinstance(state, dict):
        return {}, {}, {}
    reflect = state.get('reflect', {})
    evidence = state.get('evidence_analysis', {})
    snapshot = state.get('field_snapshot', {})
    if not isinstance(reflect, dict):
        reflect = {}
    if not isinstance(evidence, dict):
        evidence = {}
    if not isinstance(snapshot, dict):
        snapshot = {}
    return reflect, evidence, snapshot


def scorecard_action_index(items):
    index = {}
    for item in items or []:
        if not isinstance(item, dict):
            continue
        keys = {
            normalize_signal_key(item.get('domain', '')),
            normalize_signal_key(item.get('title', '')),
            normalize_signal_key(item.get('id', '')),
        }
        for key in keys:
            if key:
                index[key] = item
    return index


def scorecard_dimension_override(status, grounding_status, basis, progress, next_focus, confidence):
    return {
        'status': normalize_scorecard_status(status),
        'grounding_status': normalize_scorecard_grounding_status(grounding_status),
        'grounding_basis': compact_text_excerpt(basis, 320),
        'progress_summary': compact_text_excerpt(progress, 640),
        'next_focus': compact_text_excerpt(next_focus, 360),
        'confidence': clamp_report_confidence(confidence, 0.5),
    }


def build_scorecard_grounding(prior_reports):
    reflect_data, _, field_snapshot = scorecard_reflect_state()
    reality_path = prior_reports.get('reality') or latest_report_path('reality')
    reality_assessments = parse_reality_assessments(read_file_excerpt(reality_path) if reality_path else '')
    action_index = scorecard_action_index(reflect_data.get('action_direction_judgments', []))
    modes_payload = field_snapshot.get('modes', {}) if isinstance(field_snapshot.get('modes', {}), dict) else {}
    current_mode = modes_payload.get('current_mode', '')
    strengthening = {item.get('target_id') for item in reflect_data.get('strengthening_attractors', []) if isinstance(item, dict)}
    intensifying = {item.get('target_id') for item in reflect_data.get('intensifying_tensions', []) if isinstance(item, dict)}
    neglected = {item.get('target_id') for item in reflect_data.get('neglected_persistent_tensions', []) if isinstance(item, dict)}
    under_attended = {item.get('target_id') for item in reflect_data.get('under_attended_tensions', []) if isinstance(item, dict)}
    counterweights = {
        item.get('target_id'): item
        for item in reflect_data.get('counterweight_awareness', [])
        if isinstance(item, dict) and item.get('target_id')
    }

    subtitle_reality = reality_assessments.get('subtitle_clarity', {})
    memory_reality = reality_assessments.get('memory_trust', {})
    privacy_reality = reality_assessments.get('privacy_vs_usefulness', {})
    phone_runtime_reality = reality_assessments.get('phone_first_runtime', {})
    implementation_reality = reality_assessments.get('implementation_grounding', {})
    touch_reality = reality_assessments.get('frame_touch_only_v1_interaction', {})

    memory_action = action_index.get('memory_cache_policy', {})
    boundary_action = action_index.get('phone_cloud_boundary', {})
    subtitle_action = action_index.get('subtitle_placement', {})

    repo_grounded_actions = [
        item for item in action_index.values()
        if safe_float(item.get('repo_grounding_score', 0.0), 0.0) >= 0.2
    ]

    overrides = {
        'software_stack': scorecard_dimension_override(
            'on_track',
            'weakly_grounded',
            (
                f"Current mode is {current_mode or 'unspecified'}; Reality still marks Implementation Grounding and "
                "Phone-First Runtime as feasible now; repo-grounded action evidence remains thin in this run."
            ),
            (
                "The software stack is still pointed in the right direction: implementation grounding and phone-first "
                "constraints remain active, and the cycle is not drifting toward generic feature sprawl. What is still "
                "missing is stronger repo-grounded proof that the most important subtitle/trust decisions are moving in code rather than only in reports."
            ),
            (
                "Turn one core subtitle-or-trust question into concrete repo-grounded implementation evidence instead of another high-level reconsideration."
            ),
            0.74 if implementation_reality.get('judgment') == 'feasible_now' else 0.66,
        ),
        'wireless_interface': scorecard_dimension_override(
            'needs_attention',
            'limited_evidence',
            (
                "Reality still supports a phone-first runtime, but this run does not provide direct evidence about link stability, "
                "reconnection behavior, or measured latency on the glasses-phone path; the active phone/cloud boundary candidate remains resisted rather than newly grounded."
            ),
            (
                "The architecture still assumes the right boundary direction for V1, but wireless readiness is not strongly evidenced yet. "
                "This is not a blocked area; it is a lightly grounded subsystem whose main risk is pretending the link is solved before connection behavior is actually observed."
            ),
            (
                "Capture concrete link-latency or reconnect evidence from the phone-first path before reopening boundary changes."
            ),
            0.62 if phone_runtime_reality.get('judgment') == 'feasible_now' else 0.56,
        ),
        'firmware': scorecard_dimension_override(
            'needs_attention',
            'limited_evidence',
            (
                "Reality continues to reinforce frame-touch-only V1 interaction, but this run carries almost no direct firmware implementation evidence."
            ),
            (
                "Firmware direction is still appropriately conservative and touch-first, which fits the SmartGlasses V1 shape. "
                "The weakness is grounding, not intent: the scorecard can justify the subsystem direction, but it cannot claim strong firmware readiness from the current evidence."
            ),
            (
                "Ground firmware readiness in explicit touch-input and display-control behavior instead of inferring it from project intent."
            ),
            0.58 if touch_reality.get('judgment') == 'feasible_now' else 0.5,
        ),
        'subtitle_system': scorecard_dimension_override(
            'on_track',
            'grounded',
            (
                "Reality marks subtitle clarity as feasible now; reflect still treats subtitle_clarity as a strengthening attractor; "
                "counterweight awareness keeps latency_vs_richness and discreet_ux_vs_visual_clarity active."
            ),
            (
                "Subtitle readiness is the strongest grounded subsystem in this run. The real question is no longer whether subtitles belong in V1, "
                "but how to preserve clarity and trust without reopening the same placement debates when new grounding is absent."
            ),
            (
                "Use concrete readability, latency, and distraction evidence to refine subtitle behavior before reviving more placement variants."
            ),
            0.84 if subtitle_reality.get('judgment') == 'feasible_now' and 'subtitle_clarity' in strengthening else 0.76,
        ),
        'memory_system': scorecard_dimension_override(
            'needs_attention',
            'weakly_grounded',
            (
                "Reality marks memory trust as feasible later; reflect keeps memory_trust meaningful, but Memory/Cache Policy is currently "
                f"{memory_action.get('direction_judgment', 'unjudged')} under privacy and latency resistance."
            ),
            (
                "Memory support remains central to SmartGlasses, but this run does not justify treating it as newly ready. "
                "The subsystem is meaningful and aligned, yet still constrained by privacy perception, lookup speed, and trust calibration."
            ),
            (
                "Ground trust-preserving recall with confidence objects and reinforcement rules before expanding cache policy or retention scope."
            ),
            0.76 if memory_reality.get('judgment') in {'feasible_later', 'feasible_now'} else 0.67,
        ),
        'privacy_trust': scorecard_dimension_override(
            'needs_attention',
            'grounded',
            (
                "Reality still marks privacy_vs_usefulness as feasible now, but reflect continues to surface that same tension as intensifying and unresolved across sources."
            ),
            (
                "Privacy and trust are not background concerns in this run; they are active shaping forces on memory, boundary, and confidence decisions. "
                "That means trust needs explicit behavior and visible rules, not just a general promise to be careful."
            ),
            (
                "Tie confidence display, memory reinforcement, and boundary choices to explicit wearer-visible trust rules and consent handling."
            ),
            0.83 if privacy_reality.get('judgment') == 'feasible_now' and 'privacy_vs_usefulness' in intensifying else 0.74,
        ),
    }

    if not repo_grounded_actions:
        software = overrides.get('software_stack', {})
        if software:
            software['progress_summary'] = compact_text_excerpt(
                software.get('progress_summary', '') + ' No action in the current cycle carries meaningful repo grounding yet, so software readiness stays directional rather than strongly evidenced.',
                420,
            )

    if boundary_action.get('direction_judgment') in {'pause', 'kill', 'hold_until_new_grounding'}:
        wireless = overrides.get('wireless_interface', {})
        if wireless:
            wireless['progress_summary'] = compact_text_excerpt(
                wireless.get('progress_summary', '') + f" The latest Phone/Cloud Boundary judgment is {boundary_action.get('direction_judgment')}, which reinforces that this area should not be treated as freshly actionable without better grounding.",
                420,
            )

    if subtitle_action.get('direction_judgment') in {'pause', 'kill', 'hold_until_new_grounding'}:
        subtitle = overrides.get('subtitle_system', {})
        if subtitle:
            subtitle['next_focus'] = compact_text_excerpt(
                subtitle.get('next_focus', '') + f" Keep repeated subtitle-placement reconsideration suspended while the candidate remains {subtitle_action.get('direction_judgment')} without better grounding.",
                220,
            )

    if 'latency_vs_richness' in neglected or 'discreet_ux_vs_visual_clarity' in under_attended:
        subtitle = overrides.get('subtitle_system', {})
        if subtitle:
            subtitle['grounding_basis'] = compact_text_excerpt(
                subtitle.get('grounding_basis', '') + " The field still flags latency_vs_richness and discreet_ux_vs_visual_clarity as active counterweights.",
                320,
            )

    if 'subtitle_clarity' in counterweights:
        subtitle = overrides.get('subtitle_system', {})
        if subtitle:
            subtitle['progress_summary'] = compact_text_excerpt(
                subtitle.get('progress_summary', '') + " The dominant subtitle attractor is healthy, but it still has to respect latency and discreet-UX pressure rather than winning by default.",
                420,
            )

    return overrides


def apply_scorecard_grounding(scorecard, prior_reports):
    if not isinstance(scorecard, dict):
        scorecard = {'project_summary': '', 'dimensions': []}
    overrides = build_scorecard_grounding(prior_reports)
    for dim in scorecard.get('dimensions', []):
        if not isinstance(dim, dict):
            continue
        dim['status'] = normalize_scorecard_status(dim.get('status', 'unknown'))
        dim['grounding_status'] = normalize_scorecard_grounding_status(dim.get('grounding_status', 'unknown'))
        dim['grounding_basis'] = compact_text_excerpt(dim.get('grounding_basis', ''), 320)
        override = overrides.get(dim.get('id'))
        if override:
            dim.update(override)
        elif not dim.get('grounding_basis'):
            dim['grounding_basis'] = 'No bounded evidence basis was derived for this dimension in the current run.'
    dims_by_id = {dim.get('id'): dim for dim in scorecard.get('dimensions', []) if isinstance(dim, dict)}
    software = dims_by_id.get('software_stack', {})
    subtitle = dims_by_id.get('subtitle_system', {})
    memory = dims_by_id.get('memory_system', {})
    privacy = dims_by_id.get('privacy_trust', {})
    wireless = dims_by_id.get('wireless_interface', {})
    firmware = dims_by_id.get('firmware', {})
    scorecard['project_summary'] = (
        f"The current scorecard is strongest around {subtitle.get('label', 'Subtitle System').lower()}, where the cycle still has multi-source evidence that V1 subtitle work is real and central. "
        f"{software.get('label', 'Software Stack')} remains directionally solid but only {software.get('grounding_status', 'unknown').replace('_', ' ')} because repo-grounded movement is still thin. "
        f"{memory.get('label', 'Memory System')}, {privacy.get('label', 'Privacy And Trust')}, {wireless.get('label', 'Wireless Interface')}, and {firmware.get('label', 'Firmware')} are not empty unknowns; "
        f"they are active but constrained areas whose readiness is limited by trust, latency, and missing direct subsystem evidence."
    )
    return scorecard


def domain_action_choices(domain):
    choices = {
        "subtitle placement": [
            {"id": "stable_default", "label": "Stable Default", "description": "Prefer fixed conservative subtitle placement."},
            {"id": "more_prominent", "label": "More Prominent", "description": "Bias toward easier visibility over subtlety."},
        ],
        "confidence display": [
            {"id": "label_only", "label": "Label Only", "description": "Keep certainty display minimal and fast to parse."},
            {"id": "label_plus_reason", "label": "Label + Reason", "description": "Expose a short reason to improve trust."},
        ],
        "memory/cache policy": [
            {"id": "smaller_cache", "label": "Smaller Cache", "description": "Bias toward tighter local memory and lower load."},
            {"id": "recency_cache", "label": "Recency First", "description": "Bias toward recent names and conversations."},
        ],
        "phone/cloud boundary": [
            {"id": "phone_first", "label": "Phone First", "description": "Keep critical work local unless clearly necessary."},
            {"id": "balanced_fallback", "label": "Balanced Fallback", "description": "Allow cloud assist for slower or richer lookups."},
        ],
        "visual hierarchy": [
            {"id": "subtitles_dominate", "label": "Subtitles Dominate", "description": "Keep subtitles above all other overlays."},
            {"id": "balanced_overlay", "label": "Balanced Overlay", "description": "Allow prompts to share attention more evenly."},
        ],
    }
    return choices.get(domain, [])


def extract_numbered_section(text, section_number, section_title):
    lines = text.splitlines()
    capture = False
    collected = []
    heading = f"{section_number}. **{section_title}**"
    for line in lines:
        if heading in line:
            capture = True
            continue
        if capture and re.match(r'^\s*[1-9]\.\s+\*\*', line):
            break
        if capture and line.strip():
            collected.append(line.strip().lstrip('-').strip())
    return ' '.join(collected).strip()


def parse_dream_idea_entries(text):
    entries = []
    title_map = {dream_domain_title(domain).lower(): domain for domain in DREAM_DOMAINS}
    matches = list(re.finditer(r'^### Idea \d+: (.+)$', text, flags=re.MULTILINE))
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        title = match.group(1).strip()
        domain = title_map.get(title.lower())
        if not domain:
            continue
        block = text[start:end].strip()
        entries.append({
            'id': domain.replace('/', '-').replace(' ', '-'),
            'domain': domain,
            'title': title,
            'summary': extract_numbered_section(block, 3, 'Likely payoff'),
            'probe': extract_immediate_next_probe(block),
        })
    return entries


def extract_json_payload(text):
    fenced = re.search(r'```(?:json)?\s*(\{.*\})\s*```', text, flags=re.DOTALL)
    candidate = fenced.group(1) if fenced else text
    start = candidate.find('{')
    end = candidate.rfind('}')
    if start == -1 or end == -1 or end < start:
        raise ValueError('No JSON object found in model output')
    candidate = candidate[start:end + 1].strip()
    variants = []

    def add_variant(value):
        value = value.strip()
        if value and value not in variants:
            variants.append(value)

    add_variant(candidate)
    add_variant(re.sub(r',(\s*[}\]])', r'\1', candidate))
    add_variant(re.sub(r'([{\[,]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*:)', r'\1"\2"\3', candidate))
    add_variant(re.sub(r',(\s*[}\]])', r'\1', re.sub(r'([{\[,]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*:)', r'\1"\2"\3', candidate)))

    for variant in variants:
        try:
            return json.loads(variant)
        except Exception:
            pass

    for variant in variants:
        try:
            parsed = ast.literal_eval(variant)
        except Exception:
            continue
        if isinstance(parsed, (dict, list)):
            return json.loads(json.dumps(parsed))

    return json.loads(candidate)


def compact_text_excerpt(text, limit=280):
    collapsed = re.sub(r'\s+', ' ', str(text or '')).strip()
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[:max(0, limit - 3)].rstrip() + '...'


def extract_balanced_json_object(text):
    if not text:
        return ''
    for start, char in enumerate(text):
        if char != '{':
            continue
        depth = 0
        in_string = False
        escape = False
        for idx in range(start, len(text)):
            current = text[idx]
            if in_string:
                if escape:
                    escape = False
                elif current == '\\':
                    escape = True
                elif current == '"':
                    in_string = False
                continue
            if current == '"':
                in_string = True
            elif current == '{':
                depth += 1
            elif current == '}':
                depth -= 1
                if depth == 0:
                    return text[start:idx + 1].strip()
    return ''


def insert_missing_json_key_commas(text):
    lines = text.splitlines()
    if not lines:
        return text
    repaired = []
    for idx, raw in enumerate(lines):
        line = raw.rstrip()
        if idx < len(lines) - 1:
            next_line = lines[idx + 1].lstrip()
            if next_line.startswith('"'):
                stripped = line.rstrip()
                if stripped and not stripped.endswith(('{', '[', ':', ',')):
                    if re.search(r'("|\}|\]|\btrue\b|\bfalse\b|\bnull\b|[0-9])\s*$', stripped):
                        line = stripped + ','
        repaired.append(line)
    return '\n'.join(repaired)


def reflect_json_variants(candidate):
    variants = []

    def add_variant(name, value):
        value = value.strip()
        if value and all(existing_value != value for _, existing_value in variants):
            variants.append((name, value))

    trimmed = re.sub(r',(\s*[}\]])', r'\1', candidate)
    quoted = re.sub(r'([{\[,]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*:)', r'\1"\2"\3', candidate)
    comma_repaired = insert_missing_json_key_commas(candidate)
    add_variant('raw', candidate)
    add_variant('trim_trailing_commas', trimmed)
    add_variant('insert_missing_key_commas', comma_repaired)
    add_variant('insert_missing_key_commas_then_trim', re.sub(r',(\s*[}\]])', r'\1', comma_repaired))
    add_variant('quote_bare_keys', quoted)
    add_variant('quote_bare_keys_then_trim', re.sub(r',(\s*[}\]])', r'\1', quoted))
    quoted_comma = insert_missing_json_key_commas(quoted)
    add_variant('quote_bare_keys_and_insert_missing_key_commas', quoted_comma)
    add_variant('quote_bare_keys_insert_missing_key_commas_then_trim', re.sub(r',(\s*[}\]])', r'\1', quoted_comma))
    return variants


def validate_reflect_payload(payload):
    if not isinstance(payload, dict):
        return False, 'Reflect payload did not parse as a top-level JSON object.', []
    recognized = sorted(key for key in payload.keys() if key in REFLECT_EXPECTED_TOP_LEVEL_KEYS)
    if not recognized:
        return False, 'Parsed JSON object did not contain recognized reflect keys.', []
    return True, '', recognized


def build_reflect_fallback_payload(diagnostics):
    error_text = diagnostics.get('error') or 'Reflect output could not be parsed as valid JSON.'
    return {
        'reflection_summary': (
            'Reflect fallback activated because the model returned malformed or unusable JSON. '
            'ELI preserved grounded analysis and downstream action judgment, but trusted no model-proposed field deltas from this pass.'
        ),
        'possible_drift': [
            {
                'label': 'Reflect Output Reliability',
                'reason': error_text,
                'confidence': 0.86,
            }
        ],
        'field_deltas': [],
    }


def parse_reflect_output(raw):
    raw_text = str(raw or '').strip()
    fenced = re.search(r'```(?:json)?\s*(.*?)\s*```', raw_text, flags=re.DOTALL)
    source_text = fenced.group(1).strip() if fenced else raw_text
    candidate = extract_balanced_json_object(source_text)
    diagnostics = {
        'status': 'valid',
        'source': 'fenced_block' if fenced else 'raw_response',
        'repair_strategy': 'none',
        'error': '',
        'recognized_keys': [],
        'raw_excerpt': compact_text_excerpt(raw_text, 320),
        'candidate_excerpt': compact_text_excerpt(candidate or source_text, 320),
    }
    if not candidate:
        diagnostics.update({
            'status': 'fallback',
            'error': 'No balanced JSON object could be extracted from reflect output.',
        })
        return build_reflect_fallback_payload(diagnostics), diagnostics

    last_error = ''
    for strategy, variant in reflect_json_variants(candidate):
        try:
            payload = json.loads(variant)
        except json.JSONDecodeError as exc:
            last_error = f'{exc.msg}: line {exc.lineno} column {exc.colno} (char {exc.pos})'
            continue
        valid, issue, recognized = validate_reflect_payload(payload)
        if not valid:
            last_error = issue
            continue
        diagnostics['recognized_keys'] = recognized
        diagnostics['repair_strategy'] = strategy if strategy != 'raw' else 'none'
        if strategy != 'raw':
            diagnostics['status'] = 'repaired'
        return payload, diagnostics

    diagnostics.update({
        'status': 'fallback',
        'error': last_error or 'Reflect JSON remained invalid after deterministic repair attempts.',
    })
    return build_reflect_fallback_payload(diagnostics), diagnostics


def sync_action_inbox_from_dream(dream_body):
    existing = load_action_inbox()
    existing_items = {item.get('id'): item for item in existing.get('items', [])}
    action_memory = load_action_memory()
    memory_items = {item.get('id'): item for item in action_memory.get('items', [])}
    items = []
    for entry in parse_dream_idea_entries(dream_body):
        preserved = memory_items.get(entry['id']) or existing_items.get(entry['id'], {})
        signature = action_candidate_signature(entry)
        previous_signature = preserved.get('candidate_signature', '')
        choices = domain_action_choices(entry['domain'])
        valid_choice_ids = {choice['id'] for choice in choices}
        selected_choice_id = preserved.get('selected_choice_id')
        if selected_choice_id not in valid_choice_ids:
            selected_choice_id = None
        selected_choice = next((choice for choice in choices if choice['id'] == selected_choice_id), None)
        appearance_count = safe_int(preserved.get('appearance_count', 0), 0) + 1 if preserved else 1
        consecutive_appearances = safe_int(preserved.get('consecutive_appearances', 0), 0) + 1 if signature == previous_signature and preserved else 1
        items.append({
            'id': entry['id'],
            'domain': entry['domain'],
            'title': entry['title'],
            'summary': entry['summary'],
            'probe': entry['probe'],
            'choices': choices,
            'selected_choice_id': selected_choice_id,
            'selected_choice_label': selected_choice.get('label') if selected_choice else '',
            'status': 'selected' if selected_choice_id else 'pending',
            'selected_at': preserved.get('selected_at') if selected_choice_id else '',
            'candidate_signature': signature,
            'appearance_count': appearance_count,
            'consecutive_appearances': consecutive_appearances,
            'first_seen_at': preserved.get('first_seen_at', now_iso()),
            'last_seen_at': now_iso(),
            'last_judged_at': preserved.get('last_judged_at', ''),
            'alignment_score': preserved.get('alignment_score', 0.0),
            'resistance_score': preserved.get('resistance_score', 0.0),
            'architectural_pull_score': preserved.get('architectural_pull_score', 0.0),
            'direction_judgment': preserved.get('direction_judgment', ''),
            'judgment_reason': preserved.get('judgment_reason', ''),
            'judgment_rank': preserved.get('judgment_rank', 0),
            'field_evidence_score': preserved.get('field_evidence_score', 0.0),
            'repo_grounding_score': preserved.get('repo_grounding_score', 0.0),
            'repo_grounding_delta': preserved.get('repo_grounding_delta', 0.0),
            'repo_alignment_classification': preserved.get('repo_alignment_classification', ''),
            'grounding_novelty_classification': preserved.get('grounding_novelty_classification', ''),
            'grounding_novelty_score': preserved.get('grounding_novelty_score', 0.0),
            'grounding_hold_active': preserved.get('grounding_hold_active', False),
            'grounding_hold_reason': preserved.get('grounding_hold_reason', ''),
            'grounding_release_signals': preserved.get('grounding_release_signals', []),
            'grounding_source_types': preserved.get('grounding_source_types', []),
            'source_diversity_count': preserved.get('source_diversity_count', 0),
            'weighted_evidence_score': preserved.get('weighted_evidence_score', 0.0),
            'influence_state': preserved.get('influence_state', 'neutral'),
            'influence_reason': preserved.get('influence_reason', ''),
            'resurfacing_despite_resistance': preserved.get('resurfacing_despite_resistance', False),
            'resurfacing_classification': preserved.get('resurfacing_classification', 'first_seen'),
            'resurfacing_reason': preserved.get('resurfacing_reason', ''),
        })
    payload = {
        'source': 'latest_dream',
        'items': items,
    }
    save_action_inbox(payload)
    save_action_memory({
        'source': 'latest_dream_memory',
        'items': items,
    })
    return payload


def scorecard_context(changes, prior_reports):
    pieces = [context_with_inputs(changes)]
    pieces.append('\n# Project Scorecard Configuration\n')
    pieces.append(json.dumps(project_scorecard_config(), indent=2))
    pieces.append('\n# Recent Cycle Reports\n')
    for name in ('sleep', 'dream', 'reality', 'reflect'):
        path = prior_reports.get(name)
        if not path:
            continue
        pieces.append(f'\n## {name.title()} Report\n')
        pieces.append(read_file_excerpt(path))
        pieces.append('\n')
    return '\n'.join(pieces)


def render_scorecard_markdown(scorecard):
    lines = ['## Project Summary', scorecard.get('project_summary', 'No summary generated.'), '']
    for dim in scorecard.get('dimensions', []):
        lines.append(f"## {dim.get('label', dim.get('id', 'Dimension'))}")
        lines.append(f"- status: {dim.get('status', 'unknown')}")
        lines.append(f"- grounding: {dim.get('grounding_status', 'unknown')}")
        lines.append(f"- goal: {dim.get('goal', '')}")
        lines.append(f"- limitation pressure: {dim.get('limitation_pressure', '')}")
        lines.append(f"- evidence basis: {dim.get('grounding_basis', '')}")
        lines.append(f"- progress: {dim.get('progress_summary', '')}")
        lines.append(f"- next focus: {dim.get('next_focus', '')}")
        lines.append(f"- confidence: {dim.get('confidence', '')}")
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def normalize_scorecard(scorecard):
    config = project_scorecard_config()
    configured = config.get('dimensions', [])
    parsed_by_id = {}
    parsed_dimensions = scorecard.get('dimensions', [])
    if not isinstance(parsed_dimensions, list):
        parsed_dimensions = []
    for item in parsed_dimensions:
        if isinstance(item, dict) and item.get('id'):
            parsed_by_id[item['id']] = item
    normalized = {
        'project_summary': scorecard.get('project_summary', 'No project summary generated.'),
        'dimensions': [],
    }
    for cfg in configured:
        item = parsed_by_id.get(cfg.get('id'), {})
        limitations = cfg.get('limitations', [])
        normalized['dimensions'].append({
            'id': cfg.get('id', item.get('id', 'unknown')),
            'label': item.get('label') or cfg.get('label', cfg.get('id', 'Dimension')),
            'status': normalize_scorecard_status(item.get('status', 'unknown')),
            'grounding_status': normalize_scorecard_grounding_status(item.get('grounding_status', 'unknown')),
            'goal': item.get('goal') or cfg.get('goal', ''),
            'limitation_pressure': item.get('limitation_pressure') or ', '.join(limitations),
            'grounding_basis': item.get('grounding_basis', ''),
            'progress_summary': item.get('progress_summary', 'No grounded assessment generated in this run.'),
            'next_focus': item.get('next_focus', f"Review {cfg.get('label', cfg.get('id', 'this dimension')).lower()} against current goals and limitations."),
            'confidence': item.get('confidence', 0.25),
        })
    return normalized


def generate_scorecard_cycle(changes, prior_reports):
    system = load_prompt('scorecard')
    context = scorecard_context(changes, prior_reports)
    raw = ollama_generate(system, context)
    scorecard = extract_json_payload(raw)
    scorecard = normalize_scorecard(scorecard)
    scorecard = apply_scorecard_grounding(scorecard, prior_reports)
    scorecard['generated_at'] = now_iso()
    scorecard['project_name'] = PROJECT_SLUG
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    SCORECARD_STATE_PATH.write_text(json.dumps(scorecard, indent=2), encoding='utf-8')
    return render_scorecard_markdown(scorecard)


def reflect_context(changes, prior_reports, analysis):
    pieces = [context_with_inputs(changes)]
    pieces.append(render_recent_field_delta_context())
    pieces.append(render_cognition_schema_context(analysis.get('schema', {})))
    pieces.append(render_specialist_consultation_context())
    pieces.append(render_reflection_analysis_context(analysis))
    pieces.append('\n# Current Field Snapshot JSON\n')
    pieces.append(json.dumps(field_layer_snapshot(), indent=2))
    pieces.append('\n# Recent Cycle Reports For Reflection\n')
    for name in ('sleep', 'dream', 'reality'):
        path = prior_reports.get(name)
        if not path:
            continue
        pieces.append(f'\n## {name.title()} Report\n')
        pieces.append(read_file_excerpt(path))
        pieces.append('\n')
    previous_reflect = latest_report_path('reflect')
    if previous_reflect:
        pieces.append('\n## Previous Reflect Report\n')
        pieces.append(read_file_excerpt(previous_reflect))
        pieces.append('\n')
    return '\n'.join(pieces)


def clamp_report_confidence(value, fallback=0.5):
    try:
        return round(clamp_number(float(value), 0.0, 1.0), 3)
    except Exception:
        return fallback


def normalize_reflect_entries(items, key_names):
    if not isinstance(items, list):
        return []
    normalized = []
    for item in items:
        if not isinstance(item, dict):
            continue
        entry = {}
        for key, fallback in key_names.items():
            entry[key] = item.get(key, fallback)
        entry['confidence'] = clamp_report_confidence(entry.get('confidence', 0.5))
        normalized.append(entry)
    return normalized


def normalize_reflect_output(payload):
    if not isinstance(payload, dict):
        payload = {}
    normalized = {
        'reflection_summary': payload.get('reflection_summary', 'No reflection summary generated.'),
        'resonance_signals': normalize_reflect_entries(payload.get('resonance_signals'), {
            'field': '',
            'target_id': '',
            'label': '',
            'repetition_kind': '',
            'reason': '',
            'confidence': 0.5,
        }),
        'strengthening_attractors': normalize_reflect_entries(payload.get('strengthening_attractors'), {
            'target_id': '',
            'label': '',
            'reason': '',
            'confidence': 0.5,
        }),
        'intensifying_tensions': normalize_reflect_entries(payload.get('intensifying_tensions'), {
            'target_id': '',
            'label': '',
            'reason': '',
            'confidence': 0.5,
        }),
        'under_attended_tensions': normalize_reflect_entries(payload.get('under_attended_tensions'), {
            'target_id': '',
            'label': '',
            'reason': '',
            'confidence': 0.5,
        }),
        'possible_drift': normalize_reflect_entries(payload.get('possible_drift'), {
            'label': '',
            'reason': '',
            'confidence': 0.5,
        }),
        'dormant_ideas_worth_reactivation': normalize_reflect_entries(payload.get('dormant_ideas_worth_reactivation'), {
            'label': '',
            'reason': '',
            'type': '',
            'confidence': 0.5,
        }),
        'contradiction_persistence': normalize_reflect_entries(payload.get('contradiction_persistence'), {
            'target_id': '',
            'label': '',
            'reason': '',
            'persistence_level': '',
            'confidence': 0.5,
        }),
        'over_dominant_attractors': normalize_reflect_entries(payload.get('over_dominant_attractors'), {
            'target_id': '',
            'label': '',
            'reason': '',
            'confidence': 0.5,
        }),
        'cooling_candidates': normalize_reflect_entries(payload.get('cooling_candidates'), {
            'target_id': '',
            'label': '',
            'reason': '',
            'cooling_kind': '',
            'suggested_delta': 0.0,
            'confidence': 0.5,
        }),
        'under_attended_recurring_tensions': normalize_reflect_entries(payload.get('under_attended_recurring_tensions'), {
            'target_id': '',
            'label': '',
            'reason': '',
            'confidence': 0.5,
        }),
        'neglected_persistent_tensions': normalize_reflect_entries(payload.get('neglected_persistent_tensions'), {
            'target_id': '',
            'label': '',
            'reason': '',
            'suggested_delta': 0.0,
            'confidence': 0.5,
        }),
        'reinforcement_loops': normalize_reflect_entries(payload.get('reinforcement_loops'), {
            'field': '',
            'target_id': '',
            'label': '',
            'reason': '',
            'confidence': 0.5,
        }),
        'counterweight_awareness': normalize_reflect_entries(payload.get('counterweight_awareness'), {
            'target_id': '',
            'label': '',
            'reason': '',
            'counterweight_tensions': [],
            'confidence': 0.5,
        }),
        'field_imbalance_patterns': normalize_reflect_entries(payload.get('field_imbalance_patterns'), {
            'target_id': '',
            'label': '',
            'linked_tensions': [],
            'reason': '',
            'confidence': 0.5,
        }),
        'repo_change_candidates': normalize_reflect_entries(payload.get('repo_change_candidates'), {
            'relative_path': '',
            'surface': '',
            'classification': '',
            'matched_domains': [],
            'matched_field_targets': [],
            'reason': '',
            'confidence': 0.5,
        }),
        'repo_alignment_observations': normalize_reflect_entries(payload.get('repo_alignment_observations'), {
            'classification': '',
            'label': '',
            'related_paths': [],
            'reason': '',
            'confidence': 0.5,
        }),
        'field_diff_alignment_patterns': normalize_reflect_entries(payload.get('field_diff_alignment_patterns'), {
            'classification': '',
            'field': '',
            'target_id': '',
            'label': '',
            'related_paths': [],
            'reason': '',
            'confidence': 0.5,
        }),
        'specialist_consultation_decisions': normalize_reflect_entries(payload.get('specialist_consultation_decisions'), {
            'action_domain': '',
            'action_title': '',
            'specialist_id': '',
            'specialist_label': '',
            'consultation_mode': '',
            'decision': '',
            'reason': '',
            'confidence': 0.5,
        }),
        'specialist_consultation_evaluations': normalize_reflect_entries(payload.get('specialist_consultation_evaluations'), {
            'action_domain': '',
            'specialist_id': '',
            'specialist_label': '',
            'evaluation': '',
            'reason': '',
            'confidence': 0.5,
        }),
        'action_direction_judgments': normalize_reflect_entries(payload.get('action_direction_judgments'), {
            'id': '',
            'title': '',
            'domain': '',
            'alignment_score': 0.0,
            'resistance_score': 0.0,
            'architectural_pull_score': 0.0,
            'direction_judgment': 'pause',
            'repo_grounding_score': 0.0,
            'repo_grounding_delta': 0.0,
            'repo_alignment_classification': '',
            'repo_change_count': 0,
            'grounding_novelty_classification': '',
            'grounding_novelty_score': 0.0,
            'grounding_hold_active': False,
            'grounding_hold_reason': '',
            'grounding_release_signals': [],
            'reason': '',
            'influence_state': 'neutral',
            'influence_reason': '',
            'resurfacing_classification': 'steady_signal',
            'resurfacing_reason': '',
            'resurfacing_despite_resistance': False,
            'appearance_count': 1,
            'rank': 0,
            'confidence': 0.5,
        }),
        'dormant_idea_returns': normalize_reflect_entries(payload.get('dormant_idea_returns'), {
            'label': '',
            'type': '',
            'return_kind': '',
            'related_domain': '',
            'field': '',
            'target_id': '',
            'requested_delta': 0.0,
            'reason': '',
            'confidence': 0.5,
        }),
        'suggested_mode_shifts': normalize_reflect_entries(payload.get('suggested_mode_shifts'), {
            'target_mode': '',
            'reason': '',
            'confidence': 0.5,
            'requested_delta': 0.04,
        }),
        'field_deltas': [],
    }
    raw_deltas = payload.get('field_deltas')
    if isinstance(raw_deltas, list):
        for item in raw_deltas:
            if not isinstance(item, dict):
                continue
            delta = {
                'field': item.get('field', ''),
                'target_id': item.get('target_id', ''),
                'requested_delta': round(clamp_number(safe_float(item.get('requested_delta', 0.0), 0.0), -0.08, 0.08), 4),
                'reason': item.get('reason', ''),
                'confidence': clamp_report_confidence(item.get('confidence', 0.5)),
            }
            if delta['field'] in ('attractors', 'tensions', 'modes') and delta['target_id']:
                normalized['field_deltas'].append(delta)
    for item in normalized.get('counterweight_awareness', []):
        tensions = item.get('counterweight_tensions', [])
        if isinstance(tensions, str):
            item['counterweight_tensions'] = [tensions] if tensions else []
        elif not isinstance(tensions, list):
            item['counterweight_tensions'] = []
    for item in normalized.get('field_imbalance_patterns', []):
        tensions = item.get('linked_tensions', [])
        if isinstance(tensions, str):
            item['linked_tensions'] = [tensions] if tensions else []
        elif not isinstance(tensions, list):
            item['linked_tensions'] = []
    for item in normalized.get('repo_change_candidates', []):
        for key in ('matched_domains', 'matched_field_targets'):
            values = item.get(key, [])
            if isinstance(values, str):
                item[key] = [values] if values else []
            elif not isinstance(values, list):
                item[key] = []
    for item in normalized.get('repo_alignment_observations', []) + normalized.get('field_diff_alignment_patterns', []):
        values = item.get('related_paths', [])
        if isinstance(values, str):
            item['related_paths'] = [values] if values else []
        elif not isinstance(values, list):
            item['related_paths'] = []
    if not any(delta.get('field') == 'modes' for delta in normalized['field_deltas']):
        current_mode = field_layer_snapshot().get('modes', {}).get('current_mode', 'core_deepening')
        for shift in normalized['suggested_mode_shifts']:
            target_mode = shift.get('target_mode', '')
            if not target_mode:
                continue
            normalized['field_deltas'].append({
                'field': 'modes',
                'target_id': target_mode,
                'requested_delta': round(clamp_number(safe_float(shift.get('requested_delta', 0.04), 0.04), 0.01, 0.08), 4),
                'reason': shift.get('reason', ''),
                'confidence': shift.get('confidence', 0.5),
            })
            if current_mode and current_mode != target_mode:
                normalized['field_deltas'].append({
                    'field': 'modes',
                    'target_id': current_mode,
                    'requested_delta': -0.02,
                    'reason': f"Reflect suggested a shift away from {current_mode} toward {target_mode}.",
                    'confidence': shift.get('confidence', 0.5),
                })
    return normalized


def append_history_entry(history, entry):
    history.setdefault('entries', []).append(entry)


def enrich_reflect_output(reflect_data, analysis):
    counterweight_by_target = {
        item.get('target_id'): item
        for item in analysis.get('counterweight_awareness', [])
        if item.get('target_id')
    }
    if not reflect_data.get('resonance_signals'):
        reflect_data['resonance_signals'] = [
            {
                'field': item.get('field', ''),
                'target_id': item.get('target_id', ''),
                'label': item.get('label', ''),
                'repetition_kind': item.get('repetition_kind', ''),
                'reason': item.get('reason', ''),
                'confidence': item.get('confidence', 0.5),
            }
            for item in analysis.get('resonance_signals', [])[:4]
        ]
    if not reflect_data.get('contradiction_persistence'):
        reflect_data['contradiction_persistence'] = [
            {
                'target_id': item.get('target_id', ''),
                'label': item.get('label', ''),
                'reason': item.get('reason', ''),
                'persistence_level': item.get('persistence_level', ''),
                'confidence': item.get('confidence', 0.5),
            }
            for item in analysis.get('contradiction_persistence', [])[:3]
        ]
    if not reflect_data.get('over_dominant_attractors'):
        reflect_data['over_dominant_attractors'] = [
            {
                'target_id': item.get('target_id', ''),
                'label': item.get('label', ''),
                'reason': item.get('reason', ''),
                'confidence': item.get('confidence', 0.5),
            }
            for item in analysis.get('overdominant_attractors', [])[:3]
        ]
    if not reflect_data.get('under_attended_recurring_tensions'):
        reflect_data['under_attended_recurring_tensions'] = [
            {
                'target_id': item.get('target_id', ''),
                'label': item.get('label', ''),
                'reason': item.get('reason', ''),
                'confidence': item.get('confidence', 0.5),
            }
            for item in analysis.get('under_attended_recurring_tensions', [])[:3]
        ]
    if not reflect_data.get('reinforcement_loops'):
        reflect_data['reinforcement_loops'] = [
            {
                'field': item.get('field', ''),
                'target_id': item.get('target_id', ''),
                'label': item.get('label', ''),
                'reason': item.get('reason', ''),
                'confidence': item.get('confidence', 0.5),
            }
            for item in analysis.get('reinforcement_loops', [])[:3]
        ]
    if not reflect_data.get('counterweight_awareness'):
        reflect_data['counterweight_awareness'] = [
            {
                'target_id': item.get('target_id', ''),
                'label': item.get('label', ''),
                'counterweight_tensions': item.get('counterweight_tensions', []),
                'reason': item.get('reason', ''),
                'confidence': item.get('confidence', 0.5),
            }
            for item in analysis.get('counterweight_awareness', [])[:4]
        ]
    else:
        for item in reflect_data.get('counterweight_awareness', []):
            target_id = item.get('target_id', '')
            expected = counterweight_by_target.get(target_id)
            if not expected:
                continue
            current_tensions = item.get('counterweight_tensions', [])
            if not isinstance(current_tensions, list):
                current_tensions = []
            if not current_tensions or any(tension not in expected.get('counterweight_tensions', []) for tension in current_tensions):
                item['counterweight_tensions'] = expected.get('counterweight_tensions', [])
            if not item.get('reason'):
                item['reason'] = expected.get('reason', '')
            if not item.get('label'):
                item['label'] = expected.get('label', target_id)
    for item in reflect_data.get('dormant_ideas_worth_reactivation', []):
        dormant_type = item.get('type', '')
        if dormant_type not in DORMANT_IDEA_TYPE_VALUES:
            item['type'] = classify_dormant_idea_type(item, analysis.get('resonance_profiles', {}))
    return reflect_data


def existing_field_delta_targets(reflect_data):
    return {
        (item.get('field'), item.get('target_id'))
        for item in reflect_data.get('field_deltas', [])
        if item.get('field') and item.get('target_id')
    }


def append_field_delta_once(reflect_data, field, target_id, requested_delta, reason, confidence, control_kind=''):
    for item in reflect_data.get('field_deltas', []):
        if item.get('field') != field or item.get('target_id') != target_id:
            continue
        existing_delta = safe_float(item.get('requested_delta', 0.0), 0.0)
        if control_kind and (
            existing_delta == 0.0
            or requested_delta == 0.0
            or (existing_delta > 0 and requested_delta > 0)
            or (existing_delta < 0 and requested_delta < 0)
        ):
            item.setdefault('control_kind', control_kind)
        return False
    entry = {
        'field': field,
        'target_id': target_id,
        'requested_delta': round(clamp_number(safe_float(requested_delta, 0.0), -0.08, 0.08), 4),
        'reason': reason,
        'confidence': clamp_report_confidence(confidence, 0.5),
    }
    if control_kind:
        entry['control_kind'] = control_kind
    reflect_data.setdefault('field_deltas', []).append(entry)
    return True


def dormant_related_domain(item):
    text = lower_text(f"{item.get('label', '')} {item.get('reason', '')}")
    if 'subtitle' in text or 'caption' in text or 'placement' in text:
        return 'subtitle placement'
    if 'confidence' in text or 'certainty' in text:
        return 'confidence display'
    if any(token in text for token in ('memory', 'name', 'face', 'person-memory', 'entity-linking', 'cache', 'lookup')):
        return 'memory/cache policy'
    if any(token in text for token in ('phone/cloud', 'phone local', 'cloud fallback', 'cloud boundary', 'phone-first')):
        return 'phone/cloud boundary'
    if any(token in text for token in ('visual hierarchy', 'overlay', 'priority', 'prominence', 'readable')):
        return 'visual hierarchy'
    return ''


def dormant_related_target(item):
    text = lower_text(f"{item.get('label', '')} {item.get('reason', '')}")
    if 'subtitle' in text or 'caption' in text or 'placement' in text:
        return ('attractors', 'subtitle_clarity')
    if any(token in text for token in ('memory', 'name', 'face', 'person-memory', 'entity-linking', 'cache', 'lookup')):
        return ('attractors', 'memory_trust')
    if any(token in text for token in ('one-line', 'assist', 'discreet', 'low-friction', 'visual hierarchy', 'overlay')):
        return ('attractors', 'low_friction_assistance')
    return ('', '')


def build_dormant_idea_returns(dormant_items, analysis, action_inbox):
    schema = analysis.get('schema', load_cognition_schema())
    cfg = schema.get('control', {}).get('dormant_returns', {})
    promising_evidence_min = safe_float(cfg.get('promising_evidence_min', 0.72), 0.72)
    promising_pull_min = safe_float(cfg.get('promising_pull_min', 0.58), 0.58)
    constraint_release_resistance_max = safe_float(cfg.get('constraint_release_resistance_max', 0.62), 0.62)
    mode_return_modes = set(cfg.get('mode_return_modes', ['core_deepening']))
    return_delta = round(clamp_number(safe_float(cfg.get('return_delta', 0.01), 0.01), 0.004, 0.02), 4)
    max_target_score_for_return_delta = safe_float(cfg.get('max_target_score_for_return_delta', 0.78), 0.78)
    current_mode = analysis.get('snapshot', {}).get('modes', {}).get('current_mode', '')
    attractors_by_id = field_item_index(analysis.get('snapshot', {}).get('attractors', {}))
    actions_by_domain = {
        item.get('domain'): item
        for item in action_inbox.get('items', [])
        if item.get('domain')
    }
    items = []
    for item in dormant_items:
        if not isinstance(item, dict):
            continue
        dormant_type = item.get('type') or classify_dormant_idea_type(item, analysis.get('resonance_profiles', {}))
        related_domain = dormant_related_domain(item)
        related_action = actions_by_domain.get(related_domain, {})
        related_field, related_target_id = dormant_related_target(item)
        related_target = attractors_by_id.get(related_target_id, {}) if related_field == 'attractors' else {}
        field_evidence_score = safe_float(related_action.get('field_evidence_score', 0.0), 0.0)
        pull_score = safe_float(related_action.get('architectural_pull_score', 0.0), 0.0)
        resistance_score = safe_float(related_action.get('resistance_score', 1.0), 1.0)
        repo_grounding_score = safe_float(related_action.get('repo_grounding_score', 0.0), 0.0)
        repo_alignment_classification = related_action.get('repo_alignment_classification', '')
        repo_structural_progress = bool(related_action.get('repo_structural_progress', False))
        resurfacing_classification = related_action.get('resurfacing_classification', '')
        direction_judgment = related_action.get('direction_judgment', '')
        legitimate = False
        reason_parts = []
        if dormant_type == 'premature_but_promising':
            if (field_evidence_score >= promising_evidence_min and pull_score >= promising_pull_min) or direction_judgment == 'continue':
                legitimate = True
                reason_parts.append('related field evidence and architectural pull now support reactivation')
            elif repo_structural_progress and repo_alignment_classification in ('aligned', 'productive_resistance') and repo_grounding_score >= 0.35:
                legitimate = True
                reason_parts.append('repo changes now show structural progress toward this dormant direction')
        elif dormant_type == 'constraint_blocked':
            if resistance_score <= constraint_release_resistance_max and direction_judgment == 'continue':
                legitimate = True
                reason_parts.append('earlier blocking resistance has eased enough to revisit the idea')
            else:
                reason_parts.append('blocking resistance is still too high for meaningful return')
        elif dormant_type == 'mode_suppressed':
            if current_mode in mode_return_modes and pull_score >= promising_pull_min:
                legitimate = True
                reason_parts.append(f'current mode {current_mode} now allows this previously suppressed idea to re-enter consideration')
            else:
                reason_parts.append('current mode still does not justify meaningful return')
        else:
            reason_parts.append('current evidence still looks too weak or repetitive for meaningful return')
        if resurfacing_classification == 'genuine_reemergence':
            legitimate = True
            reason_parts.append('action-level resurfacing already shows genuine re-emergence')
        return_kind = 'legitimate_reemergence' if legitimate else 'noisy_resurfacing'
        requested_delta = 0.0
        if legitimate and related_field and related_target_id and safe_float(related_target.get('score', 0.0), 0.0) <= max_target_score_for_return_delta:
            requested_delta = return_delta
        items.append({
            'label': item.get('label', ''),
            'type': dormant_type,
            'return_kind': return_kind,
            'related_domain': related_domain,
            'field': related_field,
            'target_id': related_target_id,
            'requested_delta': requested_delta,
            'reason': '; '.join(reason_parts) if reason_parts else 'no clear changed condition for return',
            'confidence': 0.74 if legitimate else 0.58,
        })
    return items


def enrich_phase6_reflect_output(reflect_data, analysis, action_inbox):
    expected_dormant_returns = build_dormant_idea_returns(
        reflect_data.get('dormant_ideas_worth_reactivation', []),
        analysis,
        action_inbox,
    )
    reflect_data['cooling_candidates'] = [
        {
            'target_id': item.get('target_id', ''),
            'label': item.get('label', ''),
            'reason': item.get('reason', ''),
            'cooling_kind': item.get('cooling_kind', ''),
            'suggested_delta': item.get('suggested_delta', 0.0),
            'confidence': item.get('confidence', 0.5),
        }
        for item in analysis.get('cooling_candidates', [])[:2]
    ]
    reflect_data['neglected_persistent_tensions'] = [
        {
            'target_id': item.get('target_id', ''),
            'label': item.get('label', ''),
            'reason': item.get('reason', ''),
            'suggested_delta': item.get('suggested_delta', 0.0),
            'confidence': item.get('confidence', 0.5),
        }
        for item in analysis.get('neglected_persistent_tensions', [])[:3]
    ]
    reflect_data['field_imbalance_patterns'] = [
        {
            'target_id': item.get('target_id', ''),
            'label': item.get('label', ''),
            'linked_tensions': item.get('linked_tensions', []),
            'reason': item.get('reason', ''),
            'confidence': item.get('confidence', 0.5),
        }
        for item in analysis.get('field_imbalance_patterns', [])[:3]
    ]
    reflect_data['dormant_idea_returns'] = expected_dormant_returns

    rebalancing_cfg = analysis.get('schema', {}).get('control', {}).get('rebalancing', {})
    max_rebalancing_deltas = int(rebalancing_cfg.get('max_rebalancing_deltas_per_cycle', 2) or 2)

    for item in analysis.get('cooling_candidates', [])[:1]:
        append_field_delta_once(
            reflect_data,
            'attractors',
            item.get('target_id', ''),
            item.get('suggested_delta', -0.012),
            f"Controlled cooling: {item.get('reason', '')}",
            item.get('confidence', 0.5),
            control_kind='controlled_decay',
        )
    for item in analysis.get('neglected_persistent_tensions', [])[:max_rebalancing_deltas]:
        append_field_delta_once(
            reflect_data,
            'tensions',
            item.get('target_id', ''),
            item.get('suggested_delta', 0.012),
            f"Rebalancing pressure: {item.get('reason', '')}",
            item.get('confidence', 0.5),
            control_kind='rebalancing',
        )
    for item in reflect_data.get('dormant_idea_returns', [])[:1]:
        if item.get('return_kind') != 'legitimate_reemergence':
            continue
        if not item.get('field') or not item.get('target_id') or safe_float(item.get('requested_delta', 0.0), 0.0) <= 0.0:
            continue
        append_field_delta_once(
            reflect_data,
            item.get('field', ''),
            item.get('target_id', ''),
            item.get('requested_delta', 0.01),
            f"Dormant idea return: {item.get('reason', '')}",
            item.get('confidence', 0.5),
            control_kind='dormant_return',
        )
    return reflect_data


def enrich_phase7_reflect_output(reflect_data, analysis, action_inbox):
    reflect_data['repo_change_candidates'] = [
        {
            'relative_path': item.get('relative_path', ''),
            'surface': item.get('surface', ''),
            'classification': item.get('classification', ''),
            'matched_domains': item.get('matched_domains', []),
            'matched_field_targets': item.get('matched_field_targets', []),
            'reason': item.get('reason', ''),
            'confidence': item.get('confidence', 0.5),
        }
        for item in analysis.get('repo_change_candidates', [])[:6]
    ]
    reflect_data['repo_alignment_observations'] = [
        {
            'classification': item.get('classification', ''),
            'label': item.get('label', ''),
            'related_paths': item.get('related_paths', []),
            'reason': item.get('reason', ''),
            'confidence': item.get('confidence', 0.5),
        }
        for item in analysis.get('repo_alignment_observations', [])[:6]
    ]
    reflect_data['field_diff_alignment_patterns'] = [
        {
            'classification': item.get('classification', ''),
            'field': item.get('field', ''),
            'target_id': item.get('target_id', ''),
            'label': item.get('label', ''),
            'related_paths': item.get('related_paths', []),
            'reason': item.get('reason', ''),
            'confidence': item.get('confidence', 0.5),
        }
        for item in analysis.get('field_diff_alignment_patterns', [])[:5]
    ]
    return reflect_data


def enrich_specialist_reflect_output(reflect_data, specialist_context):
    reflect_data['specialist_consultation_decisions'] = [
        {
            'action_domain': item.get('action_domain', ''),
            'action_title': item.get('action_title', ''),
            'specialist_id': item.get('specialist_id', ''),
            'specialist_label': item.get('specialist_label', ''),
            'consultation_mode': item.get('consultation_mode', ''),
            'decision': item.get('decision', ''),
            'reason': item.get('reason', ''),
            'confidence': item.get('confidence', 0.5),
        }
        for item in specialist_context.get('decisions', [])
        if item.get('decision') == 'recommend_consultation' or item.get('grounding_hold_active')
    ][:5]
    reflect_data['specialist_consultation_evaluations'] = [
        {
            'action_domain': item.get('action_domain', ''),
            'specialist_id': item.get('specialist_id', ''),
            'specialist_label': item.get('specialist_label', ''),
            'evaluation': item.get('evaluation', ''),
            'reason': item.get('reason', ''),
            'confidence': item.get('confidence', 0.5),
        }
        for item in specialist_context.get('evaluations', [])
    ][:5]
    return reflect_data


def apply_reflect_field_deltas(reflect_data, source_report_paths, analysis):
    schema = analysis.get('schema', load_cognition_schema())
    snapshot = field_layer_snapshot()
    history = load_field_delta_history()
    history_entries = history.get('entries', [])
    applied_entries = []
    changed_fields = set()

    for delta in reflect_data.get('field_deltas', []):
        field = delta.get('field')
        target_id = delta.get('target_id')
        payload = snapshot.get(field)
        if field not in ('attractors', 'tensions', 'modes') or not isinstance(payload, dict):
            continue
        items_by_id = field_item_index(payload)
        item = items_by_id.get(target_id)
        if not item:
            continue
        previous_value = safe_float(item.get('score', 0.5), 0.5)
        requested_delta = round(clamp_number(safe_float(delta.get('requested_delta', 0.0), 0.0), -0.08, 0.08), 4)
        confidence = clamp_report_confidence(delta.get('confidence', 0.5))
        control_kind = delta.get('control_kind', '')
        direction = 1 if requested_delta > 0 else -1 if requested_delta < 0 else 0
        support_count = delta_support_count(history_entries, field, target_id, direction)
        effective_support_count = support_count
        if control_kind in {'controlled_decay', 'rebalancing', 'dormant_return'} and effective_support_count < 1:
            effective_support_count = 1
        evidence_profile = evidence_profile_for_target(analysis, field, target_id)
        evidence_weight = evidence_weight_multiplier(evidence_profile)
        diversity_state = {'multiplier': 1.0, 'notes': [], 'same_pattern_hits': 0, 'distinct_source_patterns': 0, 'distinct_source_types': 0, 'distinct_reason_count': 0}
        saturation_state = {'multiplier': 1.0, 'notes': []}
        if direction > 0:
            diversity_state = diversity_gate_state(history_entries, field, target_id, direction, delta.get('reason', ''), evidence_profile, schema)
            if field == 'attractors':
                saturation_state = attractor_saturation_state(previous_value, evidence_profile, schema)
        grounding_hold_state = field_delta_hold_state(history_entries, field, target_id, direction, evidence_profile, schema)
        if grounding_hold_state.get('hold_applies'):
            applied_entries.append({
                'timestamp': now_iso(),
                'cycle': 'reflect',
                'field': field,
                'target_id': target_id,
                'target_label': item.get('label', target_id),
                'previous_value': previous_value,
                'requested_delta': requested_delta,
                'applied_delta': 0.0,
                'new_value': previous_value,
                'reason': grounding_hold_state.get('hold_reason', ''),
                'confidence': confidence,
                'control_kind': delta.get('control_kind', ''),
                'linked_source_reports': source_report_paths,
                'support_count': support_count,
                'effective_support_count': effective_support_count,
                'evidence_weight': evidence_weight,
                'evidence_sources': evidence_profile.get('source_types', []),
                'weighted_evidence_score': evidence_profile.get('weighted_score', 0.0),
                'resonance_kind': evidence_profile.get('repetition_kind', 'weak_signal'),
                'diversity_multiplier': diversity_state.get('multiplier', 1.0),
                'diversity_notes': diversity_state.get('notes', []),
                'saturation_multiplier': saturation_state.get('multiplier', 1.0),
                'saturation_notes': saturation_state.get('notes', []),
                'change_type': 'held_until_new_grounding',
                'added_source_types': grounding_hold_state.get('added_source_types', []),
                'weighted_evidence_gain': grounding_hold_state.get('weighted_evidence_gain', 0.0),
            })
            continue
        applied_delta = conservative_applied_delta(field, requested_delta, confidence, effective_support_count)
        applied_delta = round_delta(applied_delta * evidence_weight)
        if direction > 0:
            applied_delta = round_delta(applied_delta * diversity_state.get('multiplier', 1.0))
            if field == 'attractors':
                applied_delta = round_delta(applied_delta * saturation_state.get('multiplier', 1.0))
        if field == 'tensions' and requested_delta < 0:
            applied_delta = round_delta(applied_delta * 0.8)
        if abs(applied_delta) < 0.004:
            continue
        if applied_delta == 0.0:
            continue
        new_value = round(clamp_number(previous_value + applied_delta, 0.0, 1.0), 4)
        item['score'] = new_value
        changed_fields.add(field)
        entry = {
            'timestamp': now_iso(),
            'cycle': 'reflect',
            'field': field,
            'target_id': target_id,
            'target_label': item.get('label', target_id),
            'previous_value': previous_value,
            'requested_delta': requested_delta,
            'applied_delta': applied_delta,
            'new_value': new_value,
            'reason': delta.get('reason', ''),
            'confidence': confidence,
            'control_kind': control_kind,
            'linked_source_reports': source_report_paths,
            'support_count': support_count,
            'effective_support_count': effective_support_count,
            'evidence_weight': evidence_weight,
            'evidence_sources': evidence_profile.get('source_types', []),
            'weighted_evidence_score': evidence_profile.get('weighted_score', 0.0),
            'resonance_kind': evidence_profile.get('repetition_kind', 'weak_signal'),
            'diversity_multiplier': diversity_state.get('multiplier', 1.0),
            'diversity_notes': diversity_state.get('notes', []),
            'saturation_multiplier': saturation_state.get('multiplier', 1.0),
            'saturation_notes': saturation_state.get('notes', []),
            'change_type': 'score_update',
        }
        if field == 'attractors':
            counterweights = analysis.get('counterweight_awareness', [])
            for item_info in counterweights:
                if item_info.get('target_id') == target_id:
                    entry['counterweight_tensions'] = item_info.get('counterweight_tensions', [])
                    entry['counterweight_reason'] = item_info.get('reason', '')
                    break
        append_history_entry(history, entry)
        applied_entries.append(entry)

    modes_payload = snapshot.get('modes', {})
    if isinstance(modes_payload, dict) and isinstance(modes_payload.get('items'), list):
        items_by_id = field_item_index(modes_payload)
        current_mode = modes_payload.get('current_mode', '')
        current_score = safe_float(items_by_id.get(current_mode, {}).get('score', 0.0), 0.0)
        top_mode = current_mode
        top_score = current_score
        for mode_id, item in items_by_id.items():
            score = safe_float(item.get('score', 0.0), 0.0)
            if score > top_score:
                top_mode = mode_id
                top_score = score
        if top_mode and current_mode and top_mode != current_mode:
            support_count = delta_support_count(history_entries, 'modes', top_mode, 1)
            if support_count >= 2 or (top_score - current_score) >= 0.18:
                modes_payload['current_mode'] = top_mode
                switch_entry = {
                    'timestamp': now_iso(),
                    'cycle': 'reflect',
                    'field': 'modes',
                    'target_id': top_mode,
                    'target_label': items_by_id.get(top_mode, {}).get('label', top_mode),
                    'previous_value': current_mode,
                    'requested_delta': round(top_score - current_score, 4),
                    'applied_delta': round(top_score - current_score, 4),
                    'new_value': top_mode,
                    'reason': f"Mode {top_mode} overtook {current_mode} with repeated reinforcement.",
                    'confidence': 0.78,
                    'linked_source_reports': source_report_paths,
                    'support_count': support_count,
                    'change_type': 'mode_switch',
                }
                append_history_entry(history, switch_entry)
                applied_entries.append(switch_entry)
                changed_fields.add('modes')

    for field in changed_fields:
        save_field_scaffold(field, snapshot[field])
    save_field_delta_history(history)
    return applied_entries, snapshot


def render_reflect_markdown(reflect_data, applied_entries):
    lines = ['## Reflection Summary', reflect_data.get('reflection_summary', 'No reflection summary generated.'), '']
    diagnostics = reflect_data.get('reflect_generation_diagnostics', {})
    if diagnostics:
        lines.append('## Reflect Diagnostics')
        lines.append(
            f"- status: {diagnostics.get('status', '')} | source: {diagnostics.get('source', '')} | repair_strategy: {diagnostics.get('repair_strategy', 'none')}"
        )
        if diagnostics.get('error'):
            lines.append(f"- note: {diagnostics.get('error')}")
        if diagnostics.get('recognized_keys'):
            lines.append(f"- recognized_keys: {', '.join(diagnostics.get('recognized_keys', []))}")
        if diagnostics.get('raw_excerpt'):
            lines.append(f"- raw_excerpt: {diagnostics.get('raw_excerpt')}")
        lines.append('')
    sections = [
        ('Resonance Signals', reflect_data.get('resonance_signals', []), 'target_id'),
        ('Strengthening Attractors', reflect_data.get('strengthening_attractors', []), 'target_id'),
        ('Intensifying Tensions', reflect_data.get('intensifying_tensions', []), 'target_id'),
        ('Under-Attended Tensions', reflect_data.get('under_attended_tensions', []), 'target_id'),
        ('Contradiction Persistence', reflect_data.get('contradiction_persistence', []), 'target_id'),
        ('Over-Dominant Attractors', reflect_data.get('over_dominant_attractors', []), 'target_id'),
        ('Cooling Candidates', reflect_data.get('cooling_candidates', []), 'target_id'),
        ('Under-Attended Recurring Tensions', reflect_data.get('under_attended_recurring_tensions', []), 'target_id'),
        ('Neglected Persistent Tensions', reflect_data.get('neglected_persistent_tensions', []), 'target_id'),
        ('Reinforcement Loops', reflect_data.get('reinforcement_loops', []), 'target_id'),
        ('Counterweight Awareness', reflect_data.get('counterweight_awareness', []), 'target_id'),
        ('Field Imbalance Patterns', reflect_data.get('field_imbalance_patterns', []), 'target_id'),
        ('Repo Change Candidates', reflect_data.get('repo_change_candidates', []), 'relative_path'),
        ('Repo Alignment Observations', reflect_data.get('repo_alignment_observations', []), 'label'),
        ('Field Diff Alignment Patterns', reflect_data.get('field_diff_alignment_patterns', []), 'label'),
        ('Specialist Consultation Decisions', reflect_data.get('specialist_consultation_decisions', []), 'specialist_label'),
        ('Specialist Consultation Evaluations', reflect_data.get('specialist_consultation_evaluations', []), 'specialist_label'),
        ('Action Direction Judgments', reflect_data.get('action_direction_judgments', []), 'title'),
        ('Possible Drift', reflect_data.get('possible_drift', []), None),
        ('Dormant Ideas Worth Reactivation', reflect_data.get('dormant_ideas_worth_reactivation', []), None),
        ('Dormant Idea Returns', reflect_data.get('dormant_idea_returns', []), 'label'),
        ('Suggested Mode Shifts', reflect_data.get('suggested_mode_shifts', []), 'target_mode'),
    ]
    for heading, items, key in sections:
        lines.append(f'## {heading}')
        if not items:
            lines.append('- none')
            lines.append('')
            continue
        for item in items:
            label = item.get('label') or item.get(key or '', '') or 'item'
            if heading == 'Specialist Consultation Decisions' and label == 'item':
                label = item.get('action_title') or item.get('action_domain') or 'consultation'
            detail = item.get('reason', '')
            confidence = item.get('confidence', '')
            extra = ''
            if heading == 'Resonance Signals':
                extra = f" | {item.get('repetition_kind', '')}"
            elif heading == 'Contradiction Persistence':
                extra = f" | persistence {item.get('persistence_level', '')}"
            elif heading == 'Cooling Candidates':
                extra = f" | kind {item.get('cooling_kind', '')}"
                if safe_float(item.get('suggested_delta', 0.0), 0.0):
                    extra += f" | suggested_delta {item.get('suggested_delta', 0.0)}"
            elif heading == 'Neglected Persistent Tensions':
                if safe_float(item.get('suggested_delta', 0.0), 0.0):
                    extra = f" | suggested_delta {item.get('suggested_delta', 0.0)}"
            elif heading == 'Counterweight Awareness':
                extra = f" | tensions {', '.join(item.get('counterweight_tensions', []))}"
            elif heading == 'Field Imbalance Patterns':
                extra = f" | tensions {', '.join(item.get('linked_tensions', []))}"
            elif heading == 'Repo Change Candidates':
                extra = (
                    f" | class {item.get('classification', '')}"
                    f" | surface {item.get('surface', '')}"
                    f" | domains {', '.join(item.get('matched_domains', [])) or 'none'}"
                )
                targets = ', '.join(item.get('matched_field_targets', []))
                if targets:
                    extra += f" | targets {targets}"
            elif heading == 'Repo Alignment Observations':
                extra = f" | class {item.get('classification', '')} | paths {', '.join(item.get('related_paths', [])) or 'none'}"
            elif heading == 'Field Diff Alignment Patterns':
                target = f"{item.get('field', '')}/{item.get('target_id', '')}" if item.get('field') or item.get('target_id') else item.get('label', '')
                extra = f" | class {item.get('classification', '')}"
                if target:
                    extra += f" | target {target}"
                if item.get('related_paths'):
                    extra += f" | paths {', '.join(item.get('related_paths', []))}"
            elif heading == 'Specialist Consultation Decisions':
                extra = (
                    f" | action {item.get('action_domain', '') or item.get('action_title', '')}"
                    f" | mode {item.get('consultation_mode', '')}"
                    f" | decision {item.get('decision', '')}"
                )
            elif heading == 'Specialist Consultation Evaluations':
                extra = (
                    f" | action {item.get('action_domain', '')}"
                    f" | evaluation {item.get('evaluation', '')}"
                )
            elif heading == 'Action Direction Judgments':
                extra = (
                    f" | rank {item.get('rank', '')}"
                    f" | alignment {item.get('alignment_score', '')}"
                    f" | resistance {item.get('resistance_score', '')}"
                    f" | pull {item.get('architectural_pull_score', '')}"
                    f" | judgment {item.get('direction_judgment', '')}"
                    f" | influence {item.get('influence_state', '')}"
                    f" | resurfacing {item.get('resurfacing_classification', '')}"
                )
                if item.get('repo_alignment_classification'):
                    extra += (
                        f" | repo {item.get('repo_alignment_classification', '')}"
                        f" | repo_score {item.get('repo_grounding_score', '')}"
                    )
                if item.get('grounding_novelty_classification'):
                    extra += (
                        f" | grounding {item.get('grounding_novelty_classification', '')}"
                        f" | grounding_score {item.get('grounding_novelty_score', '')}"
                    )
                if item.get('grounding_hold_active'):
                    extra += f" | hold_reason {item.get('grounding_hold_reason', '')}"
                    if item.get('grounding_release_signals'):
                        extra += f" | release_on {', '.join(item.get('grounding_release_signals', []))}"
                if item.get('specialist_recommended_specialist_label'):
                    extra += (
                        f" | specialist {item.get('specialist_recommended_specialist_label', '')}"
                        f" | consult {item.get('specialist_consultation_decision', '')}"
                    )
                    if item.get('specialist_consultation_mode'):
                        extra += f" | mode {item.get('specialist_consultation_mode', '')}"
                if item.get('specialist_evaluation'):
                    extra += f" | specialist_eval {item.get('specialist_evaluation', '')}"
            elif heading == 'Dormant Ideas Worth Reactivation':
                extra = f" | type {item.get('type', '')}"
            elif heading == 'Dormant Idea Returns':
                extra = (
                    f" | type {item.get('type', '')}"
                    f" | return {item.get('return_kind', '')}"
                    f" | domain {item.get('related_domain', '') or 'n/a'}"
                )
                if item.get('field') and item.get('target_id'):
                    extra += f" | target {item.get('field')}/{item.get('target_id')}"
                if safe_float(item.get('requested_delta', 0.0), 0.0):
                    extra += f" | requested_delta {item.get('requested_delta', 0.0)}"
            suffix = f" (confidence {confidence})" if confidence != '' else ''
            lines.append(f"- {label}: {detail}{extra}{suffix}")
        lines.append('')
    lines.append('## Proposed Field Deltas')
    if not reflect_data.get('field_deltas'):
        lines.append('- none')
    else:
        for delta in reflect_data.get('field_deltas', []):
            kind_suffix = f" | kind {delta.get('control_kind')}" if delta.get('control_kind') else ''
            lines.append(
                f"- {delta.get('field')}/{delta.get('target_id')}: requested_delta {delta.get('requested_delta')} | confidence {delta.get('confidence')}{kind_suffix} | reason: {delta.get('reason', '')}"
            )
    lines.append('')
    lines.append('## Applied Conservative Field Updates')
    if not applied_entries:
        lines.append('- none')
    else:
        for entry in applied_entries:
            if entry.get('change_type') == 'held_until_new_grounding':
                added_sources = ', '.join(entry.get('added_source_types', [])) or 'none'
                kind_suffix = f" | kind {entry.get('control_kind')}" if entry.get('control_kind') else ''
                lines.append(
                    f"- {entry.get('field')}/{entry.get('target_id')}: held_until_new_grounding | previous {entry.get('previous_value')} | requested_delta {entry.get('requested_delta')}{kind_suffix} | weighted_evidence_gain {entry.get('weighted_evidence_gain', 0.0)} | added_source_types {added_sources} | reason: {entry.get('reason')} | confidence {entry.get('confidence')}"
                )
            elif entry.get('change_type') == 'mode_switch':
                lines.append(
                    f"- modes/{entry.get('target_id')}: switched current mode from {entry.get('previous_value')} to {entry.get('new_value')} | reason: {entry.get('reason')} | confidence {entry.get('confidence')}"
                )
            else:
                kind_suffix = f" | kind {entry.get('control_kind')}" if entry.get('control_kind') else ''
                lines.append(
                    f"- {entry.get('field')}/{entry.get('target_id')}: previous {entry.get('previous_value')} -> new {entry.get('new_value')} | applied_delta {entry.get('applied_delta')} | support_count {entry.get('support_count')} | effective_support_count {entry.get('effective_support_count', entry.get('support_count'))} | evidence_weight {entry.get('evidence_weight')} | diversity_multiplier {entry.get('diversity_multiplier', 1.0)} | saturation_multiplier {entry.get('saturation_multiplier', 1.0)}{kind_suffix} | evidence_sources {', '.join(entry.get('evidence_sources', [])) or 'none'} | reason: {entry.get('reason')} | confidence {entry.get('confidence')}"
                )
    lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def generate_reflect_cycle(changes, prior_reports):
    system = load_prompt('reflect')
    analysis = build_reflection_analysis(changes, prior_reports)
    context = reflect_context(changes, prior_reports, analysis)
    raw = ollama_generate(system, context)
    parsed_payload, reflect_diagnostics = parse_reflect_output(raw)
    reflect_data = normalize_reflect_output(parsed_payload)
    if reflect_diagnostics.get('status') != 'valid':
        reflect_data['reflect_generation_diagnostics'] = reflect_diagnostics
    reflect_data = enrich_reflect_output(reflect_data, analysis)
    action_direction_judgments, action_inbox, specialist_context = enrich_action_inbox_with_reflection(analysis)
    reflect_data['action_direction_judgments'] = action_direction_judgments
    reflect_data = enrich_phase6_reflect_output(reflect_data, analysis, action_inbox)
    reflect_data = enrich_phase7_reflect_output(reflect_data, analysis, action_inbox)
    reflect_data = enrich_specialist_reflect_output(reflect_data, specialist_context)
    source_report_paths = [str(path) for name, path in prior_reports.items() if name in ('sleep', 'dream', 'reality') and path]
    applied_entries, updated_snapshot = apply_reflect_field_deltas(reflect_data, source_report_paths, analysis)
    reflect_state = {
        'generated_at': now_iso(),
        'project_name': PROJECT_SLUG,
        'reflect': reflect_data,
        'action_inbox': action_inbox,
        'applied_updates': applied_entries,
        'evidence_analysis': {
            'resonance_signals': analysis.get('resonance_signals', []),
            'contradiction_persistence': analysis.get('contradiction_persistence', []),
            'overdominant_attractors': analysis.get('overdominant_attractors', []),
            'under_attended_recurring_tensions': analysis.get('under_attended_recurring_tensions', []),
            'reinforcement_loops': analysis.get('reinforcement_loops', []),
            'counterweight_awareness': analysis.get('counterweight_awareness', []),
            'cooling_candidates': analysis.get('cooling_candidates', []),
            'neglected_persistent_tensions': analysis.get('neglected_persistent_tensions', []),
            'field_imbalance_patterns': analysis.get('field_imbalance_patterns', []),
            'repo_change_candidates': analysis.get('repo_change_candidates', []),
            'repo_alignment_observations': analysis.get('repo_alignment_observations', []),
            'field_diff_alignment_patterns': analysis.get('field_diff_alignment_patterns', []),
            'action_repo_grounding': analysis.get('action_repo_grounding', {}),
            'specialist_consultation_decisions': specialist_context.get('decisions', []),
            'specialist_consultation_evaluations': specialist_context.get('evaluations', []),
            'specialist_trust_memory': specialist_context.get('trust_memory', {}),
            'action_direction_judgments': action_direction_judgments,
            'dormant_idea_returns': reflect_data.get('dormant_idea_returns', []),
            'source_weighting': analysis.get('source_weighting', {}),
        },
        'field_snapshot': updated_snapshot,
    }
    if reflect_diagnostics.get('status') != 'valid':
        reflect_state['reflect_generation_diagnostics'] = reflect_diagnostics
    REFLECT_STATE_PATH.write_text(json.dumps(reflect_state, indent=2), encoding='utf-8')
    return render_reflect_markdown(reflect_data, applied_entries), reflect_diagnostics


def store_cycle_run(cycle, started_at, finished_at, status, duration_ms, changed_files, report_path='', error_text=''):
    con = sqlite3.connect(DB_PATH)
    con.execute(
        """
        INSERT INTO cycle_runs(cycle, started_at, finished_at, status, duration_ms, changed_files, report_path, error_text)
        VALUES(?,?,?,?,?,?,?,?)
        """,
        (cycle, started_at, finished_at, status, duration_ms, changed_files, report_path, error_text),
    )
    con.commit(); con.close()


def dream_domain_title(domain):
    titles = {
        "subtitle placement": "Subtitle Placement",
        "confidence display": "Confidence Display",
        "memory/cache policy": "Memory/Cache Policy",
        "phone/cloud boundary": "Phone/Cloud Boundary",
        "visual hierarchy": "Visual Hierarchy",
    }
    return titles.get(domain, domain.title())


def dream_domain_focus(domain):
    focuses = {
        "subtitle placement": "subtitle placement rules only: fixed position, placement mode, placement fallback, or placement by confidence state",
        "confidence display": "confidence display only: format, label style, short reason style, certainty wording, or confidence score presentation",
        "memory/cache policy": "memory/cache policy only: cache size, eviction rule, recency rule, lookup retention, or local memory threshold",
        "phone/cloud boundary": "phone/cloud boundary only: what stays phone-local, what falls back to cloud, and when that handoff happens for exactly one task boundary",
        "visual hierarchy": "visual hierarchy only: subtitle-vs-one-line priority, display precedence, prominence, suppression, or coexistence rule",
    }
    return focuses.get(domain, domain)


def dream_domain_exclusions(domain):
    exclusions = {
        "subtitle placement": [
            "Keep the decision target on subtitle position or placement only.",
            "Do not turn this idea into confidence format, cache policy, phone/cloud routing, or subtitle-vs-one-line priority.",
        ],
        "confidence display": [
            "Keep the decision target on confidence labels, confidence wording, or confidence format only.",
            "Do not turn this idea into subtitle placement, cache policy, phone/cloud routing, or visual hierarchy.",
        ],
        "memory/cache policy": [
            "Keep the decision target on local memory thresholds, cache size, recency, retention, eviction, or the entity-linking rule for attaching new evidence to an existing person-memory object.",
            "Do not turn this idea into subtitle placement, confidence format, phone/cloud routing, or visual hierarchy.",
        ],
        "phone/cloud boundary": [
            "Keep the decision target on what runs phone-local versus what falls back to cloud for exactly one task boundary.",
            "Allowed task boundaries are: live subtitle processing, transcript cleanup, face/name recall lookup, memory archive sync, conversation snapshot upload.",
            "Do not bundle two tasks in one probe.",
            "Do not turn this idea into cache size, cache eviction, subtitle placement, confidence format, or visual hierarchy.",
        ],
        "visual hierarchy": [
            "Keep the decision target on precedence, prominence, or coexistence between subtitles and one-line support.",
            "Do not turn this idea into subtitle placement modes, confidence format, cache policy, or phone/cloud routing.",
        ],
    }
    return exclusions.get(domain, [])


def dream_domain_fallback_probe(domain):
    fallbacks = {
        "subtitle placement": "Define one fixed subtitle position rule for V1: keep subtitles at the bottom center of the display.",
        "confidence display": "Choose one confidence display format for V1: label only or label plus short reason.",
        "memory/cache policy": "Set one local cache eviction rule for face/name memory in V1.",
        "phone/cloud boundary": "Choose one phone-local versus cloud fallback boundary for face/name recall lookup in V1.",
        "visual hierarchy": "Define one visual priority rule between subtitles and one-line support in V1.",
    }
    return fallbacks.get(domain, f"Define one {domain} rule for V1.")


def dream_domain_system_prompt(base_prompt, domain):
    parts = [
        base_prompt,
        "Single-domain override for this call:",
        f"- Ignore any earlier instruction to generate multiple ideas. Generate exactly one idea for the fixed domain: {domain}.",
        "- Return no title for the idea. The caller will add the idea heading.",
        "- Return exactly these four numbered sections and nothing else:",
        "  1. **Why it benefits the core**",
        "  2. **What small change unlocks it**",
        "  3. **Likely payoff**",
        "  4. **Immediate next probe**",
        f"- Stay only inside this domain: {dream_domain_focus(domain)}.",
        "- Do not switch to another domain anywhere in the idea.",
        "- The immediate next probe must stay in the same domain as the idea.",
        "- The immediate next probe must be a single decision statement for V1.",
        "- The immediate next probe must target exactly one decision target.",
        "- Do not include testing plans, validation plans, or feedback language in the immediate next probe.",
    ]
    for line in dream_domain_exclusions(domain):
        parts.append(f"- {line}")
    return "\n\n".join(parts)


def normalize_probe_text(text):
    return re.sub(r'\s+', ' ', text.strip().lstrip('-').strip()).lower()


def matches_any_pattern(text, patterns):
    return any(re.search(pattern, text) for pattern in patterns)


def probe_matches_domain(domain, probe):
    p = normalize_probe_text(probe)
    if not p:
        return False
    if domain == "subtitle placement":
        return "subtitle" in p and any(token in p for token in ("placement", "position", "location", "placement rule", "fixed"))
    if domain == "confidence display":
        return any(token in p for token in ("confidence", "certainty", "label", "score", "reason", "format"))
    if domain == "memory/cache policy":
        return any(token in p for token in ("cache", "memory", "eviction", "retention", "recency", "local-cache", "entity-linking"))
    if domain == "phone/cloud boundary":
        has_phone_side = any(token in p for token in ("phone", "local", "on-phone"))
        has_cloud_side = any(token in p for token in ("cloud", "fallback", "boundary", "route", "handoff"))
        return has_phone_side and has_cloud_side
    if domain == "visual hierarchy":
        has_priority = any(token in p for token in ("visual priority", "hierarchy", "priority rule", "display priority", "precedence", "priority"))
        has_one_line = any(token in p for token in ("one-line support", "one-line prompt", "prompt", "subtitle-vs-one-line"))
        return has_priority and has_one_line
    return False


def count_decision_targets(domain, probe):
    p = normalize_probe_text(probe)
    if domain == "phone/cloud boundary":
        return sum(1 for patterns in PHONE_CLOUD_TASK_PATTERNS.values() if matches_any_pattern(p, patterns))
    target_patterns = DOMAIN_TARGET_PATTERNS.get(domain, {})
    return sum(1 for patterns in target_patterns.values() if matches_any_pattern(p, patterns))


def probe_is_decision_shaped(probe):
    p = normalize_probe_text(probe)
    return any(p.startswith(verb + ' ') for verb in DECISION_VERBS)


def probe_has_single_target(domain, probe):
    p = normalize_probe_text(probe)
    target_count = count_decision_targets(domain, p)
    if target_count != 1:
        return False
    if domain == "phone/cloud boundary":
        return True
    if ' and ' in p and target_count > 1:
        return False
    return True


def probe_mentions_other_domain(domain, probe):
    for other in DREAM_DOMAINS:
        if other == domain:
            continue
        if probe_matches_domain(other, probe):
            return True
    return False


def extract_immediate_next_probe(text):
    lines = text.splitlines()
    capture = False
    probe_lines = []
    for line in lines:
        if 'Immediate next probe' in line:
            capture = True
            continue
        if capture:
            if re.match(r'^\s*[1-9]\.', line):
                break
            stripped = line.strip()
            if stripped:
                probe_lines.append(stripped.lstrip('-').strip())
    return ' '.join(probe_lines).strip()


def extract_single_idea_block(text):
    lines = text.strip().splitlines()
    start = None
    for idx, line in enumerate(lines):
        if re.match(r'^\s*1\.\s+\*\*Why it benefits the core\*\*', line):
            start = idx
            break
    if start is None:
        return text.strip()

    out = []
    section_numbers_seen = set()
    in_probe_section = False
    probe_content_seen = False
    for line in lines[start:]:
        if out and in_probe_section and probe_content_seen and re.match(r'^\s*[1-4]\.\s+\*\*', line):
            break
        if line.strip() == '---' and 4 in section_numbers_seen:
            break
        out.append(line)
        m = re.match(r'^\s*([1-4])\.\s+\*\*', line)
        if m:
            section_number = int(m.group(1))
            section_numbers_seen.add(section_number)
            in_probe_section = section_number == 4
            continue
        if in_probe_section and line.strip():
            probe_content_seen = True
    return '\n'.join(out).strip()


def replace_immediate_next_probe(text, new_probe):
    lines = text.splitlines()
    out = []
    i = 0
    replaced = False
    while i < len(lines):
        line = lines[i]
        out.append(line)
        if 'Immediate next probe' in line:
            i += 1
            while i < len(lines):
                stripped = lines[i].strip()
                if re.match(r'^\s*[1-9]\.', lines[i]):
                    break
                if stripped:
                    i += 1
                    continue
                i += 1
            out.append(f"   - {new_probe}")
            replaced = True
            continue
        i += 1
    if not replaced:
        trimmed = text.rstrip()
        if trimmed:
            trimmed += "\n"
        trimmed += "4. **Immediate next probe**\n"
        trimmed += f"   - {new_probe}\n"
        return trimmed
    return "\n".join(out).rstrip() + "\n"


def repair_dream_probe(domain, idea_text):
    system = "\n".join([
        "You repair exactly one line in a current-project dream idea.",
        f"The fixed decision domain is: {domain}.",
        f"The replacement must stay only in this domain: {dream_domain_focus(domain)}.",
        "Return exactly one sentence with no bullet prefix, no heading, and no explanation.",
        "The sentence must be a concrete V1 decision statement for the immediate next probe.",
        "The sentence must target exactly one decision target.",
        "Do not mention testing, evaluation, feedback, metrics, prototypes, or another decision domain.",
        "Do not use 'and' to join two different target tasks or decisions.",
    ])
    prompt = "\n".join([
        "# Idea Block",
        idea_text,
        "",
        "# Return",
        "Rewrite only the immediate next probe sentence so it stays in the fixed domain and names exactly one decision target.",
    ])
    repaired = ollama_generate(system, prompt).strip()
    repaired = repaired.splitlines()[0].strip().lstrip('-').strip() if repaired else ""
    if not probe_matches_domain(domain, repaired) or probe_mentions_other_domain(domain, repaired) or not probe_has_single_target(domain, repaired) or not probe_is_decision_shaped(repaired):
        repaired = dream_domain_fallback_probe(domain)
    return repaired


def generate_dream_idea_block(domain, context, base_prompt):
    system = dream_domain_system_prompt(base_prompt, domain)
    raw = ollama_generate(system, context).strip()
    raw = extract_single_idea_block(raw)
    probe = extract_immediate_next_probe(raw)
    if not probe_matches_domain(domain, probe) or probe_mentions_other_domain(domain, probe) or not probe_has_single_target(domain, probe) or not probe_is_decision_shaped(probe):
        repaired_probe = repair_dream_probe(domain, raw)
        raw = replace_immediate_next_probe(raw, repaired_probe)
    return raw.strip()


def generate_dream_cycle(changes):
    base_prompt = load_prompt('dream')
    context = context_with_inputs(changes)
    blocks = []
    for idx, domain in enumerate(DREAM_DOMAINS, start=1):
        block = generate_dream_idea_block(domain, context, base_prompt)
        blocks.append(f"### Idea {idx}: {dream_domain_title(domain)}\n\n{block}")
    return '\n\n'.join(blocks)


def build_context(changes):
    pieces = ["# Core Field\n", core_text(), "\n# Recent Signals\n"]
    if not changes:
        pieces.append('No changed files detected in the latest scan. Use current core and prior memory to reflect.\n')
    for p, txt in changes:
        pieces.append(f'\n## File: {p}\n')
        pieces.append(txt[:6000])
        pieces.append('\n')
    return '\n'.join(pieces)

def classify_input_path(path):
    try:
        rel = path.relative_to(PROJECT_DIR)
        rels = rel.as_posix()
        if rels.startswith('core/field_v2/'):
            return 'field_v2'
        if rels.startswith('core/'):
            return 'core'
        if rels.startswith('inbox/'):
            return 'inbox'
        if rels == 'links/repo/ELI/attractors.md':
            return 'attractors'
        if rels == 'links/repo/ELI/tensions.md':
            return 'tensions'
        if rels.startswith('links/repo/ELI/constraints/'):
            return 'constraints'
        if rels.startswith('links/repo/ELI/decisions/'):
            return 'decisions'
        if rels.startswith('links/repo/ELI/inbox/'):
            return 'eli_inbox'
        if rels.startswith('links/repo/ELI/modes/'):
            return 'modes'
        if rels.startswith('links/repo/ELI/'):
            return 'eli'
        if rels.startswith('links/repo/'):
            return 'repo'
    except Exception:
        pass
    return 'other'


def grouped_context(changes):
    groups = {
        'field_v2': [],
        'core': [],
        'inbox': [],
        'attractors': [],
        'tensions': [],
        'constraints': [],
        'decisions': [],
        'eli_inbox': [],
        'modes': [],
        'eli': [],
        'repo': [],
        'other': [],
    }
    for p, txt in changes:
        key = classify_input_path(p)
        if key not in groups:
            key = 'other'
        groups[key].append((p, txt))
    return groups


def context_with_inputs(changes):
    groups = grouped_context(changes)
    persistent_inputs = persistent_eli_context()
    operator_guidance = load_operator_guidance()
    action_inbox = load_action_inbox()
    pieces = ['# Core Field\n', core_text(), '\n']
    pieces.append(render_field_layer_context())
    pieces.append(f'# {PROJECT_DISPLAY_NAME} Project Guardrails\n')
    pieces.append('- Treat the provided core field, linked project docs, field layer, and scorecard configuration as the source of project-specific truth.\n')
    pieces.append('- Respect explicit interaction, architecture, privacy, battery, latency, trust, and usability constraints from the current project inputs.\n')
    pieces.append('- Prefer core-deepening work over broad feature expansion unless the project docs justify a broader move.\n')
    pieces.append('- Keep suggestions concrete, inspectable, and tied to the current project instance rather than generic product advice.\n')
    pieces.append('\n')
    pieces.append('# Operator Guidance\n')
    if operator_guidance and operator_guidance.get('mode') and operator_guidance.get('mode') != 'best_effort':
        pieces.append(f"- Active guidance mode: {operator_guidance.get('mode')}\n")
        note = operator_guidance.get('note', '').strip()
        if note:
            pieces.append(f"- Guidance note: {note}\n")
        updated_at = operator_guidance.get('updated_at')
        if updated_at:
            pieces.append(f"- Guidance updated at: {updated_at}\n")
    else:
        pieces.append('- No active operator guidance. Use best effort and choose the strongest project-specific direction.\n')
    pieces.append('\n')
    pieces.append('# Action Inbox\n')
    action_items = action_inbox.get('items', [])
    if not action_items:
        pieces.append('- No pending action items. Use best effort.\n')
    else:
        for item in action_items:
            domain = item.get('domain', 'unknown')
            title = item.get('title', domain)
            selected = item.get('selected_choice_label', '').strip()
            if selected:
                pieces.append(f"- {title}: operator selected `{selected}`.\n")
            else:
                pieces.append(f"- {title}: no operator choice selected; use best effort within `{domain}`.\n")
    pieces.append('\n')
    pieces.append('# Inputs Used This Cycle\n')
    if not changes:
        pieces.append('- No changed files detected in the latest scan.\n')
    else:
        for p, _ in changes:
            try:
                rel = p.relative_to(PROJECT_DIR)
                pieces.append(f'- {rel.as_posix()}\n')
            except Exception:
                pieces.append(f'- {p}\n')
    pieces.append('\n# Reality Rules\n')
    pieces.append('- Prefer project-specific insight over generic product advice.\n')
    pieces.append('- Use concrete repo signals when available.\n')
    pieces.append('- Distinguish feasible now, feasible later, and likely waste of time.\n')
    pieces.append('- Favor additions that deepen the core mission rather than broaden it superficially.\n')
    pieces.append('- Surface contradictions, drift risks, and real implementation constraints early.\n')
    pieces.append('- Avoid vague suggestions like generic user testing unless directly grounded by the current inputs.\n')
    pieces.append('- Prefer define/choose/set concrete candidates over generic evaluation plans.\n')
    pieces.append(f'\n# Persistent {PROJECT_DISPLAY_NAME} Project Inputs\n')
    for p, txt in persistent_inputs:
        pieces.append(f'\n## File: {p}\n')
        pieces.append(txt[:6000])
        pieces.append('\n')
    pieces.append('\n# Structured Recent Signals\n')
    ordered = ['field_v2', 'core', 'inbox', 'attractors', 'tensions', 'constraints', 'decisions', 'eli_inbox', 'modes', 'eli', 'repo', 'other']
    any_items = False
    for key in ordered:
        items = groups.get(key, [])
        if not items:
            continue
        any_items = True
        pieces.append(f'\n## {key.replace("_", " ").title()}\n')
        for p, txt in items:
            pieces.append(f'\n### File: {p}\n')
            pieces.append(txt[:6000])
            pieces.append('\n')
    if not any_items:
        pieces.append('No changed files detected in the latest scan. Use current core and prior memory to reflect.\n')
    return '\n'.join(pieces)

def render_inputs_used(changes):
    lines = ['## Inputs Used This Cycle']
    if not changes:
        lines.append('- No changed files detected in the latest scan.')
        return '\n'.join(lines)
    for p, _ in changes:
        try:
            rel = p.relative_to(PROJECT_DIR)
            lines.append(f'- {rel.as_posix()}')
        except Exception:
            lines.append(f'- {p}')
    return '\n'.join(lines)


def attach_cycle_metadata(name, changes, content):
    header = [f'# {name.title()} cycle', '', render_inputs_used(changes), '']
    return '\n'.join(header) + content

def store_memory(cycle, title, body, priority=7, confidence=0.7):
    con = sqlite3.connect(DB_PATH)
    con.execute('INSERT INTO memories(cycle, title, body, priority, confidence, created_at) VALUES(?,?,?,?,?,?)',
                (cycle, title, body, priority, confidence, dt.datetime.now().isoformat(timespec='seconds')))
    con.commit(); con.close()


def parse_priority(text):
    score = 7
    low = text.lower()
    if 'critical' in low or 'urgent' in low or 'high priority' in low:
        score = 9
    elif 'low priority' in low or 'minor' in low:
        score = 5
    return score


def notify(title, message):
    if not CFG.get('notifications', {}).get('enabled', True):
        return
    try:
        subprocess.run(['osascript', '-e', f'display notification {json.dumps(message)} with title {json.dumps(title)}'], check=False)
    except Exception:
        pass


def write_report(name, content):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    path = REPORTS_DIR / f'{stamp}_{name}.md'
    path.write_text(content, encoding='utf-8')
    latest = REPORTS_DIR / f'latest_{name}.md'
    latest.write_text(content, encoding='utf-8')
    return path


def run_cycle(name, changes):
    started = dt.datetime.now()
    started_at = started.isoformat(timespec='seconds')
    write_runtime_state(state='running', current_cycle=name, current_project=PROJECT_SLUG, cycle_started_at=started_at, changed_files=len(changes))
    try:
        if name == 'dream':
            output = generate_dream_cycle(changes)
            sync_action_inbox_from_dream(output)
        elif name == 'reflect':
            raise RuntimeError('reflect cycle requires prior reports')
        elif name == 'scorecard':
            raise RuntimeError('scorecard cycle requires prior reports')
        else:
            system = load_prompt(name)
            context = context_with_inputs(changes)
            output = ollama_generate(system, context)
        output = attach_cycle_metadata(name, changes, output)
        title = f'{name.capitalize()} cycle'
        prio = parse_priority(output)
        conf = 0.82 if name == 'reality' else 0.72
        store_memory(name, title, output, priority=prio, confidence=conf)
        path = write_report(name, output)
        duration_ms = int((dt.datetime.now() - started).total_seconds() * 1000)
        store_cycle_run(name, started_at, now_iso(), 'ok', duration_ms, len(changes), str(path), '')
        if prio >= CFG.get('notifications', {}).get('min_priority', 8):
            notify(f"{PROJECT_DISPLAY_NAME}: {name}", f'New {name} insight saved: {path.name}')
        write_runtime_state(state='running', current_cycle=None, current_project=PROJECT_SLUG, last_completed_cycle=name, last_cycle_status='ok', last_cycle_finished_at=now_iso(), last_report_path=str(path), last_error='')
        return path
    except Exception as exc:
        duration_ms = int((dt.datetime.now() - started).total_seconds() * 1000)
        store_cycle_run(name, started_at, now_iso(), 'error', duration_ms, len(changes), '', str(exc))
        write_runtime_state(state='error', current_cycle=name, current_project=PROJECT_SLUG, last_cycle_status='error', last_error=str(exc), last_cycle_finished_at=now_iso())
        raise


def daily_snapshot():
    started = dt.datetime.now()
    started_at = started.isoformat(timespec='seconds')
    con = sqlite3.connect(DB_PATH)
    rows = con.execute('SELECT cycle, title, body, priority, confidence, created_at FROM memories ORDER BY id DESC LIMIT 12').fetchall()
    con.close()
    body = ['# Daily Field Snapshot', '']
    for cycle, title, text, prio, conf, created in rows:
        body.append(f'## {title}')
        body.append(f'- cycle: {cycle}')
        body.append(f'- priority: {prio}')
        body.append(f'- confidence: {conf}')
        body.append(f'- created: {created}')
        body.append(text[:2800])
        body.append('')
    path = write_report('daily_snapshot', '\n'.join(body))
    duration_ms = int((dt.datetime.now() - started).total_seconds() * 1000)
    store_cycle_run('daily_snapshot', started_at, now_iso(), 'ok', duration_ms, 0, str(path), '')
    write_runtime_state(state='waiting', current_cycle=None, current_project=PROJECT_SLUG, last_completed_cycle='daily_snapshot', last_cycle_status='ok', last_cycle_finished_at=now_iso(), last_report_path=str(path), last_error='')
    return path


def run_scorecard_cycle(changes, prior_reports):
    started = dt.datetime.now()
    started_at = started.isoformat(timespec='seconds')
    write_runtime_state(state='running', current_cycle='scorecard', current_project=PROJECT_SLUG, cycle_started_at=started_at, changed_files=len(changes))
    try:
        output = generate_scorecard_cycle(changes, prior_reports)
        output = attach_cycle_metadata('scorecard', changes, output)
        title = 'Scorecard cycle'
        prio = parse_priority(output)
        conf = 0.78
        store_memory('scorecard', title, output, priority=prio, confidence=conf)
        path = write_report('scorecard', output)
        duration_ms = int((dt.datetime.now() - started).total_seconds() * 1000)
        store_cycle_run('scorecard', started_at, now_iso(), 'ok', duration_ms, len(changes), str(path), '')
        write_runtime_state(state='running', current_cycle=None, current_project=PROJECT_SLUG, last_completed_cycle='scorecard', last_cycle_status='ok', last_cycle_finished_at=now_iso(), last_report_path=str(path), last_error='')
        return path
    except Exception as exc:
        duration_ms = int((dt.datetime.now() - started).total_seconds() * 1000)
        store_cycle_run('scorecard', started_at, now_iso(), 'error', duration_ms, len(changes), '', str(exc))
        write_runtime_state(state='error', current_cycle='scorecard', current_project=PROJECT_SLUG, last_cycle_status='error', last_error=str(exc), last_cycle_finished_at=now_iso())
        error_path = write_report('scorecard_error', f'# scorecard error\n\n{exc}\n')
        return error_path


def run_reflect_cycle(changes, prior_reports):
    started = dt.datetime.now()
    started_at = started.isoformat(timespec='seconds')
    write_runtime_state(state='running', current_cycle='reflect', current_project=PROJECT_SLUG, cycle_started_at=started_at, changed_files=len(changes))
    try:
        output, reflect_diagnostics = generate_reflect_cycle(changes, prior_reports)
        output = attach_cycle_metadata('reflect', changes, output)
        title = 'Reflect cycle'
        prio = parse_priority(output)
        if reflect_diagnostics.get('status') == 'fallback':
            conf = 0.58
        elif reflect_diagnostics.get('status') == 'repaired':
            conf = 0.72
        else:
            conf = 0.8
        store_memory('reflect', title, output, priority=prio, confidence=conf)
        path = write_report('reflect', output)
        duration_ms = int((dt.datetime.now() - started).total_seconds() * 1000)
        store_cycle_run('reflect', started_at, now_iso(), 'ok', duration_ms, len(changes), str(path), '')
        write_runtime_state(
            state='running',
            current_cycle=None,
            current_project=PROJECT_SLUG,
            last_completed_cycle='reflect',
            last_cycle_status='ok',
            last_cycle_finished_at=now_iso(),
            last_report_path=str(path),
            last_error='',
            reflect_generation_status=reflect_diagnostics.get('status', 'valid'),
            reflect_generation_repair_strategy=reflect_diagnostics.get('repair_strategy', 'none'),
            reflect_generation_note=reflect_diagnostics.get('error', ''),
        )
        return path
    except Exception as exc:
        duration_ms = int((dt.datetime.now() - started).total_seconds() * 1000)
        store_cycle_run('reflect', started_at, now_iso(), 'error', duration_ms, len(changes), '', str(exc))
        write_runtime_state(state='error', current_cycle='reflect', current_project=PROJECT_SLUG, last_cycle_status='error', last_error=str(exc), last_cycle_finished_at=now_iso())
        error_path = write_report('reflect_error', f'# reflect error\n\n{exc}\n')
        return error_path


def run_once():
    ensure_field_scaffolds()
    write_runtime_state(state='scanning', current_cycle=None, current_project=PROJECT_SLUG)
    changes = changed_files(PROJECT_DIR)
    build_refresh = refresh_transcriptlab_build_summary_if_needed(changes)
    write_runtime_state(state='running', current_cycle='sleep', current_project=PROJECT_SLUG, changed_files=len(changes), watch_roots=[str(p) for p in watch_roots()])
    write_runtime_state(
        transcriptlab_build_refresh=build_refresh.get('status'),
        transcriptlab_build_refresh_ran=build_refresh.get('ran', False),
        transcriptlab_build_summary_path=build_refresh.get('summary_path', str(BUILD_SUMMARY_PATH)),
        transcriptlab_build_refresh_finished_at=build_refresh.get('finished_at', now_iso()),
        transcriptlab_build_refresh_error=build_refresh.get('error_text', ''),
    )
    paths = []
    cycle_paths = {}
    for name in ('sleep', 'dream', 'reality'):
        try:
            path = run_cycle(name, changes)
            paths.append(path)
            cycle_paths[name] = path
        except Exception as e:
            error_path = write_report(f'{name}_error', f'# {name} error\n\n{e}\n')
            paths.append(error_path)
            write_runtime_state(state='error', current_cycle=None, current_project=PROJECT_SLUG, last_cycle_status='error', last_error=str(e), last_report_path=str(error_path))
    reflect_path = run_reflect_cycle(changes, cycle_paths)
    paths.append(reflect_path)
    cycle_paths['reflect'] = reflect_path
    paths.append(run_scorecard_cycle(changes, cycle_paths))
    paths.append(daily_snapshot())
    write_runtime_state(state='waiting', current_cycle=None, current_project=PROJECT_SLUG, last_run_finished_at=now_iso(), changed_files=len(changes), last_error='')
    return paths


def daemon():
    cycles_cfg = CFG.get('cycles', {})
    continuous = cycles_cfg.get('continuous', True)
    pause_seconds = max(1, int(cycles_cfg.get('pause_seconds_between_runs', 5)))
    interval = max(5, int(cycles_cfg.get('interval_minutes', 60))) * 60
    while True:
        run_once()
        if continuous:
            next_cycle_at = (dt.datetime.now() + dt.timedelta(seconds=pause_seconds)).isoformat(timespec='seconds')
            write_runtime_state(state='waiting', current_cycle=None, current_project=PROJECT_SLUG, scheduler_mode='continuous', next_cycle_at=next_cycle_at, pause_seconds_between_runs=pause_seconds, last_error='')
            time.sleep(pause_seconds)
        else:
            next_cycle_at = (dt.datetime.now() + dt.timedelta(seconds=interval)).isoformat(timespec='seconds')
            write_runtime_state(state='waiting', current_cycle=None, current_project=PROJECT_SLUG, scheduler_mode='interval', next_cycle_at=next_cycle_at, interval_minutes=int(cycles_cfg.get('interval_minutes', 60)), last_error='')
            time.sleep(interval)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--once', action='store_true')
    ap.add_argument('--daemon', action='store_true')
    args = ap.parse_args()
    ensure_db()
    ensure_field_scaffolds()
    if args.daemon:
        daemon()
    else:
        for p in run_once():
            print(p)


if __name__ == '__main__':
    main()
