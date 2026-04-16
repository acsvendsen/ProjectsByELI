#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import pathlib
import re
import sqlite3
import subprocess
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from orchestrator import (
    ACTION_INBOX_PATH,
    BASE,
    CFG,
    COMPONENT_PACKAGE_REVIEW_PATH,
    BUDGET_TIER_REVIEW_PATH,
    COST_VIABILITY_REVIEW_PATH,
    DB_PATH,
    EXECUTION_RESUME_PATH,
    EXECUTION_BOUNDARIES_PATH,
    EXPLORATORY_IDEAS_REVIEW_PATH,
    EXTENSION_DEPLOYMENT_REVIEW_PATH,
    EXTENSIONS_CAPABILITY_REVIEW_PATH,
    HARDWARE_AWARE_RENDERING_BRIEF_REVIEW_PATH,
    OPERATOR_PROPOSAL_REVIEW_PATH,
    OPERATOR_GUIDANCE_PATH,
    PARTS_READINESS_REVIEW_PATH,
    PRICING_ALTERNATIVES_REVIEW_PATH,
    PROJECT_DIR,
    PROJECT_DIRECTION_REVIEW_PATH,
    PROJECT_EXPECTATIONS_PATH,
    PROJECT_MILESTONES_PATH,
    PROJECT_STATE_DIR,
    SIMILAR_PRODUCTS_REVIEW_PATH,
    REUSE_RECOMMENDATION_REVIEW_PATH,
    PROJECT_TOPOLOGY_VIEW_PATH,
    PRODUCT_REALISM_REVIEW_PATH,
    REPORTS_DIR,
    RUNTIME_STATE_PATH,
    SCORECARD_STATE_PATH,
    STATE_DIR,
    UI_SURFACE_PLAN_PATH,
    VERIFICATION_SUMMARY_PATH,
    ensure_db,
    runtime_review_surface_path,
    state_write_config,
    state_write_mode_status,
    watch_roots,
)

UI_DIR = BASE / "ui"
HTML_PATH = UI_DIR / "dashboard.html"
ENGINE_STATE_DIR = BASE / "state"
SCORECARD_REPORT_RE = re.compile(r"^(?P<stamp>\d{8}_\d{6})_scorecard\.md$")
SCORECARD_META_SECTIONS = {
    "Inputs Used This Cycle",
    "Project Summary",
    "Transcript Quality & Transparent Inference",
}
SCORECARD_HISTORY_WINDOW = 12
SCORECARD_HISTORY_LOOKBACK = 24


def read_json(path, fallback):
    path = resolve_dashboard_json_path(path)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def resolve_dashboard_json_path(path):
    path = pathlib.Path(path)
    cfg = state_write_config()
    if not cfg.get("dashboard_prefer_runtime_review_surfaces", True):
        return path
    try:
        path.relative_to(PROJECT_STATE_DIR)
    except Exception:
        return path
    runtime_path = runtime_review_surface_path(path)
    if runtime_path.exists():
        return runtime_path
    return path


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def safe_stat(path):
    try:
        return path.stat()
    except Exception:
        return None


def iso_to_dt(value):
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value)
    except Exception:
        return None


def minutes_since(value):
    stamp = iso_to_dt(value)
    if not stamp:
        return None
    delta = dt.datetime.now() - stamp
    return round(delta.total_seconds() / 60, 1)


def read_text_excerpt(path, limit=420):
    try:
        text = pathlib.Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    text = " ".join(text.split())
    return text[:limit]


def normalize_token(value):
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")


def parse_scorecard_report_stamp(path):
    match = SCORECARD_REPORT_RE.match(path.name)
    if not match:
        return None
    try:
        return dt.datetime.strptime(match.group("stamp"), "%Y%m%d_%H%M%S")
    except Exception:
        return None


def parse_scorecard_report_dimensions(path):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {}

    headings = list(re.finditer(r"^## (.+)$", text, re.MULTILINE))
    parsed = {}
    for idx, match in enumerate(headings):
        heading = match.group(1).strip()
        if heading in SCORECARD_META_SECTIONS:
            continue
        start = match.end()
        end = headings[idx + 1].start() if idx + 1 < len(headings) else len(text)
        body = text[start:end]
        status_match = re.search(r"^- status:\s*([a-z_]+)", body, re.MULTILINE)
        grounding_match = re.search(r"^- grounding:\s*([a-z_]+)", body, re.MULTILINE)
        confidence_match = re.search(r"^- confidence:\s*([0-9]+(?:\.[0-9]+)?)", body, re.MULTILINE)
        parsed[normalize_token(heading)] = {
            "label": heading,
            "status": status_match.group(1) if status_match else "unknown",
            "grounding_status": grounding_match.group(1) if grounding_match else "unknown",
            "confidence": round(float(confidence_match.group(1)), 3) if confidence_match else None,
        }
    return parsed


def classify_confidence_trend(values):
    usable = [float(value) for value in values if isinstance(value, (int, float))]
    if len(usable) < 4:
        return ""
    delta = usable[-1] - usable[0]
    span = max(usable) - min(usable)
    if delta >= 0.08:
        return "rising"
    if delta <= -0.08:
        return "falling"
    if abs(delta) < 0.04 and span < 0.08:
        return "flat"
    return ""


def build_scorecard_history(scorecard):
    dimensions = scorecard.get("dimensions", []) if isinstance(scorecard, dict) else []
    if not isinstance(dimensions, list) or not dimensions:
        return scorecard

    aliases = {}
    for dim in dimensions:
        dim_id = str(dim.get("id") or normalize_token(dim.get("label", "")))
        aliases[normalize_token(dim_id)] = dim_id
        aliases[normalize_token(dim.get("label", ""))] = dim_id

    report_paths = []
    for path in sorted(REPORTS_DIR.glob("*_scorecard.md")):
        if not SCORECARD_REPORT_RE.match(path.name):
            continue
        stamp = parse_scorecard_report_stamp(path)
        if not stamp:
            continue
        report_paths.append((stamp, path))
    report_paths = report_paths[-SCORECARD_HISTORY_LOOKBACK:]

    history_by_dimension = {str(dim.get("id") or normalize_token(dim.get("label", ""))): [] for dim in dimensions}
    for stamp, path in report_paths:
        parsed = parse_scorecard_report_dimensions(path)
        if not parsed:
            continue
        for parsed_key, payload in parsed.items():
            dim_id = aliases.get(parsed_key)
            if not dim_id:
                continue
            history_by_dimension.setdefault(dim_id, []).append({
                "timestamp": stamp.isoformat(timespec="seconds"),
                "report_name": path.name,
                "status": payload.get("status", "unknown"),
                "grounding_status": payload.get("grounding_status", "unknown"),
                "confidence": payload.get("confidence"),
            })

    for dim in dimensions:
        dim_id = str(dim.get("id") or normalize_token(dim.get("label", "")))
        points = history_by_dimension.get(dim_id, [])
        if not points and isinstance(dim.get("confidence"), (int, float)):
            points = [{
                "timestamp": scorecard.get("generated_at", ""),
                "report_name": "",
                "status": dim.get("status", "unknown"),
                "grounding_status": dim.get("grounding_status", "unknown"),
                "confidence": round(float(dim.get("confidence", 0.0)), 3),
            }]
        points = points[-SCORECARD_HISTORY_WINDOW:]
        dim["history"] = {
            "sample_count": len(points),
            "window_label": f"Recent {len(points)} scorecards" if points else "No retained scorecard history",
            "trend_label": classify_confidence_trend([point.get("confidence") for point in points]),
            "points": points,
        }
    return scorecard


def module_state(last_run, runtime_state, interval_minutes):
    current_cycle = runtime_state.get("current_cycle")
    state = runtime_state.get("state")
    if current_cycle == last_run["cycle"] and state == "running":
        return "running"
    freshness = minutes_since(last_run.get("finished_at"))
    if last_run.get("status") == "error":
        return "error"
    if freshness is None:
        return "unknown"
    if freshness <= interval_minutes * 1.5:
        return "healthy"
    if freshness <= interval_minutes * 3:
        return "stale"
    return "late"


def launch_agent_status():
    label = CFG.get("launch_agent_label", "com.projectcognition.smartglasses")
    try:
        result = subprocess.run(
            ["launchctl", "list"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and label in result.stdout:
            return "loaded"
        if result.returncode == 0:
            return "not_loaded"
    except Exception:
        pass
    return "unknown"


def collect_process_telemetry():
    groups = {
        "orchestrator": [],
        "dashboard": [],
    }
    try:
        result = subprocess.run(
            ["ps", "-axo", "pid=,ppid=,pcpu=,rss=,etime=,command="],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception:
        return {key: {"count": 0, "cpu_pct": 0.0, "rss_mb": 0.0, "processes": []} for key in groups}

    for raw in result.stdout.splitlines():
        parts = raw.strip().split(None, 5)
        if len(parts) < 6:
            continue
        pid, ppid, pcpu, rss, etime, command = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
        entry = {
            "pid": int(pid),
            "ppid": int(ppid),
            "cpu_pct": round(float(pcpu), 1),
            "rss_mb": round(int(rss) / 1024, 1),
            "etime": etime,
            "command": command,
        }
        if "src/orchestrator.py" in command and "dashboard.py" not in command:
            groups["orchestrator"].append(entry)
        if "src/dashboard.py" in command:
            groups["dashboard"].append(entry)

    telemetry = {}
    for key, processes in groups.items():
        telemetry[key] = {
            "count": len(processes),
            "cpu_pct": round(sum(p["cpu_pct"] for p in processes), 1),
            "rss_mb": round(sum(p["rss_mb"] for p in processes), 1),
            "processes": processes[:4],
        }
    return telemetry


def load_action_inbox_data():
    data = read_json(ACTION_INBOX_PATH, {"items": []})
    if not isinstance(data, dict):
        return {"items": []}
    if not isinstance(data.get("items"), list):
        data["items"] = []
    return data


def update_action_choice(action_id, choice_id=None):
    data = load_action_inbox_data()
    updated = None
    for item in data.get("items", []):
        if item.get("id") != action_id:
            continue
        if choice_id:
            selected = next((choice for choice in item.get("choices", []) if choice.get("id") == choice_id), None)
            if not selected:
                raise ValueError("unknown choice")
            item["selected_choice_id"] = selected["id"]
            item["selected_choice_label"] = selected.get("label", "")
            item["status"] = "selected"
            item["selected_at"] = dt.datetime.now().isoformat(timespec="seconds")
        else:
            item["selected_choice_id"] = ""
            item["selected_choice_label"] = ""
            item["status"] = "pending"
            item["selected_at"] = ""
        updated = item
        break
    if updated is None:
        raise ValueError("unknown action")
    data["updated_at"] = dt.datetime.now().isoformat(timespec="seconds")
    write_json(ACTION_INBOX_PATH, data)
    return updated


def load_dashboard_data():
    ensure_db()
    runtime_state = read_json(RUNTIME_STATE_PATH, {})
    if not isinstance(runtime_state, dict):
        runtime_state = {}
    runtime_state_defaults = state_write_mode_status()
    for key, value in runtime_state_defaults.items():
        runtime_state.setdefault(key, value)
    operator_guidance = read_json(OPERATOR_GUIDANCE_PATH, {"mode": "best_effort"})
    action_inbox = load_action_inbox_data()
    project_expectations = read_json(PROJECT_EXPECTATIONS_PATH, {
        "project_intent": "",
        "target_outcome_type": "functional_prototype",
        "quality_bar": "credible",
        "intended_seriousness": "exploratory",
        "intended_value_posture": "assistive_prototype_learning",
        "target_product_tier": "discreet_consumer_assistive_wearable",
        "acceptable_cost_posture": "prototype_only_until_costs_grounded",
        "reviewed_by_operator": False,
        "defaults_are_tentative": True,
        "product_candidate_goal": "",
    })
    project_milestones = read_json(PROJECT_MILESTONES_PATH, {
        "generated_at": "",
        "milestones": [],
        "counts": {},
    })
    product_realism_review = read_json(PRODUCT_REALISM_REVIEW_PATH, {
        "generated_at": "",
        "current_realism_band": "concept_only",
        "why_this_band": "",
        "anti_gimmick_strengths": [],
        "gimmick_risks": [],
        "missing_for_product_candidate": [],
        "missing_for_real_product_path": [],
        "quality_bar_alignment": {},
    })
    execution_resume = read_json(EXECUTION_RESUME_PATH, {
        "generated_at": "",
        "execution_boundaries": {},
        "project_intent": {},
        "product_realism": {},
        "component_package": {},
        "cost_viability": {},
        "project_direction": {},
        "budget_tier": {},
        "exploratory_ideas": {},
        "operator_proposals": {},
        "similar_products": {},
        "reuse_recommendations": {},
        "extension_actions": {},
        "unblocked_next": {},
        "needs_human_review": [],
        "resume_notes": [],
    })
    execution_boundaries = read_json(EXECUTION_BOUNDARIES_PATH, {
        "generated_at": "",
        "working_mode": "until_next_reviewable_milestone",
        "target_milestone_id": "",
        "target_milestone_title": "",
        "current_milestone_target_id": "",
        "current_milestone_target_title": "",
        "deadline_posture": "no_explicit_deadline",
        "review_cadence": "at_next_reviewable_milestone_or_operator_decision",
        "default_stop_conditions": [],
        "pause_conditions": [],
        "stop_conditions": [],
        "operator_review_required_when": [],
        "staleness_stop_condition": "",
        "no_new_grounding_stop_condition": "",
        "cost_stop_condition": "",
        "current_boundary_summary": "",
        "why_this_target_now": "",
        "current_target_posture": "",
        "what_unlocks_if_reviewed": [],
        "what_blocks_progress": [],
        "when_to_escalate_to_operator": "",
        "when_to_stop_working_this_front": "",
        "prototype_vs_product_interpretation": "",
        "competing_milestones_deferred": [],
        "current_reason_to_continue": "",
        "current_reason_to_pause": "",
        "current_reason_to_stop": "",
        "current_reason_to_escalate": "",
        "prototype_vs_product_boundary_note": "",
        "trust_posture": {},
    })
    project_direction_review = read_json(PROJECT_DIRECTION_REVIEW_PATH, {
        "generated_at": "",
        "current_direction_summary": "",
        "hardware_direction": "",
        "software_direction": "",
        "interaction_direction": "",
        "product_shaping_direction": "",
        "favored_choices": [],
        "deferred_or_weaker_choices": [],
        "why_current_direction_is_winning": [],
        "what_is_still_provisional": [],
        "what_is_blocking_stronger_direction_lock": [],
        "what_could_change_direction_next": [],
        "prototype_vs_product_interpretation": "",
        "budget_pressure_note": "",
        "trust_posture": {},
    })
    exploratory_ideas_review = read_json(EXPLORATORY_IDEAS_REVIEW_PATH, {
        "generated_at": "",
        "ideas_summary": "",
        "ideas_being_explored": [],
        "why_these_ideas_are_visible_now": [],
        "ideas_gaining_strength": [],
        "ideas_fading_or_blocked": [],
        "what_changed_recently": [],
        "what_would_promote_an_idea": [],
        "what_keeps_ideas_non_authoritative": [],
        "prototype_vs_product_interpretation": "",
        "trust_posture": {},
    })
    operator_proposal_review = read_json(OPERATOR_PROPOSAL_REVIEW_PATH, {
        "generated_at": "",
        "proposal_summary": "",
        "proposal_lifecycle_summary": "",
        "operator_proposals": [],
        "live_proposals": [],
        "promoted_proposals": [],
        "held_proposals": [],
        "rejected_proposals": [],
        "why_proposals_are_visible_now": [],
        "proposals_fitting_current_direction": [],
        "proposals_challenging_current_direction": [],
        "proposals_blocked_or_too_weak": [],
        "why_a_proposal_was_promoted": [],
        "why_a_proposal_was_held": [],
        "why_a_proposal_was_rejected": [],
        "what_would_promote_a_proposal": [],
        "what_would_reopen_a_held_or_rejected_proposal": [],
        "what_keeps_proposals_non_authoritative": [],
        "proposal_lifecycle_note": "",
        "prototype_vs_product_interpretation": "",
        "trust_posture": {},
    })
    similar_products_review = read_json(SIMILAR_PRODUCTS_REVIEW_PATH, {
        "generated_at": "",
        "similarity_review_summary": "",
        "similar_products": [],
        "adjacent_products": [],
        "already_solved_subproblems": [],
        "inspiration_not_substitute": [],
        "do_not_reinvent_signals": [],
        "real_differentiation_opportunities": [],
        "why_these_products_are_visible_now": [],
        "how_this_should_change_project_judgment": [],
        "what_this_does_not_change": [],
        "trust_posture": {},
    })
    reuse_recommendation_review = read_json(REUSE_RECOMMENDATION_REVIEW_PATH, {
        "generated_at": "",
        "reuse_recommendation_summary": "",
        "recommended_reuse_rows": [],
        "recommended_adaptation_rows": [],
        "recommended_integration_rows": [],
        "recommended_buy_or_source_rows": [],
        "inspiration_only_rows": [],
        "true_invention_focus_rows": [],
        "do_not_reinvent_recommendations": [],
        "why_these_recommendations_are_current": [],
        "what_this_should_change_in_project_judgment": [],
        "what_this_does_not_change": [],
        "prototype_vs_product_reuse_note": "",
        "trust_posture": {},
    })
    project_topology_view = read_json(PROJECT_TOPOLOGY_VIEW_PATH, {
        "generated_at": "",
        "overview_summary": "",
        "nodes": [],
        "edges": [],
        "active_node_ids": [],
        "blocked_node_ids": [],
        "held_node_ids": [],
        "reviewable_node_ids": [],
        "operator_input_needed_node_ids": [],
        "current_focus_node_id": "",
        "trust_posture": {},
    })
    component_package_review = read_json(COMPONENT_PACKAGE_REVIEW_PATH, {
        "generated_at": "",
        "bom_readiness_band": "not_warranted",
        "component_package_kind": "",
        "target_subsystems": [],
        "required_now": [],
        "recommended_for_quality": [],
        "optional_or_later": [],
        "blocked_by_unresolved_choices": [],
        "missing_for_stronger_bom": [],
        "why_bom_is_or_is_not_warranted": "",
        "milestone_link": {},
        "realism_link": {},
        "trust_posture": {},
    })
    parts_readiness_review = read_json(PARTS_READINESS_REVIEW_PATH, {
        "generated_at": "",
        "parts_readiness_band": "not_ready_for_suggestions",
        "current_shortlist_posture": "not_yet_warranted",
        "suggested_now": [],
        "suggested_packages_now": [],
        "blocked_for_stronger_shortlist": [],
        "why_not_stronger_yet": "",
        "next_evidence_needed": [],
        "operator_waiting_for": [],
        "trust_posture": {},
    })
    pricing_alternatives_review = read_json(PRICING_ALTERNATIVES_REVIEW_PATH, {
        "generated_at": "",
        "pricing_confidence_posture": "too_early_for_directional_pricing",
        "current_candidate_rows": [],
        "alternative_rows": [],
        "cost_direction_view": "",
        "fit_for_target_tier": "unknown",
        "why_current_choice_may_fail": [],
        "why_alternative_may_help": [],
        "operator_warning": "",
        "trust_posture": {},
    })
    budget_tier_review = read_json(BUDGET_TIER_REVIEW_PATH, {
        "generated_at": "",
        "budget_tier_summary": "",
        "supported_budget_tiers": [],
        "current_project_budget_posture": "unknown",
        "intended_budget_posture": "unknown",
        "budget_alignment_status": "unknown",
        "where_current_direction_sits": [],
        "where_current_ideas_sit": [],
        "where_current_packages_sit": [],
        "mixed_tier_compromise_paths": [],
        "tier_pressure_points": [],
        "what_is_pushing_cost_up": [],
        "what_is_keeping_cost_down": [],
        "what_would_realign_the_project": [],
        "prototype_vs_product_budget_note": "",
        "trust_posture": {},
    })
    cost_viability_review = read_json(COST_VIABILITY_REVIEW_PATH, {
        "generated_at": "",
        "cost_realism_band": "too_early_for_exact_cost",
        "intended_value_posture": "",
        "target_product_tier": "",
        "acceptable_cost_posture": "",
        "likely_cost_risk_level": "moderate",
        "economic_viability_posture": "unknown",
        "why_this_posture": "",
        "major_cost_risk_factors": [],
        "cost_unknowns": [],
        "what_would_improve_cost_confidence": [],
        "current_evidence_strength": "thin",
        "prototype_only_vs_product_viable_view": "",
        "kill_pause_reframe_signal": "proceed_with_caution",
        "operator_cost_warning": "",
        "trust_posture": {},
    })
    hardware_aware_rendering_brief_review = read_json(HARDWARE_AWARE_RENDERING_BRIEF_REVIEW_PATH, {
        "generated_at": "",
        "summary": "",
        "eli_authority_note": "",
        "informational_extension_posture": "informational_only",
        "trust_posture": {},
        "source_authority": {},
        "rendering_briefs": [],
    })
    extensions_capability_review = read_json(EXTENSIONS_CAPABILITY_REVIEW_PATH, {
        "generated_at": "",
        "summary": "",
        "eli_authority_note": "",
        "ui_enablement_status": "informational_only",
        "available_capabilities": [],
        "project_recommended_extensions": [],
        "missing_but_useful_capabilities": [],
        "representation_risks": [],
    })
    extension_deployment_review = read_json(EXTENSION_DEPLOYMENT_REVIEW_PATH, {
        "generated_at": "",
        "extensions_summary": "",
        "eli_authority_note": "",
        "deployment_execution_posture": "state_model_only",
        "trust_posture": {},
        "source_authority": {},
        "top_level_operator_actions_needed": [],
        "active_extensions": [],
        "recommended_waiting_for_opt_in": [],
        "available_but_not_requested": [],
        "deferred_or_not_yet_justified": [],
        "why_this_state_is_current": [],
        "what_operator_can_do_now": [],
    })
    ui_surface_plan = read_json(UI_SURFACE_PLAN_PATH, {
        "generated_at": "",
        "summary": "",
        "project_pages": [],
        "section_emergence_rules": [],
        "representation_risks": [],
        "operator_goals": [],
    })
    scorecard = read_json(SCORECARD_STATE_PATH, {"project_summary": "", "dimensions": []})
    scorecard = build_scorecard_history(scorecard if isinstance(scorecard, dict) else {"project_summary": "", "dimensions": []})
    verification_summary = read_json(VERIFICATION_SUMMARY_PATH, {
        "summary": "",
        "subsystem_card_source": {},
        "current_truth_sources": [],
        "supporting_context_sources": [],
        "recent_transitions": [],
        "lane_explanations": {"active": [], "held": [], "blocked": []},
        "recent_source_wins": [],
        "surfaces_with_caution": [],
        "representation_risks": [],
        "operator_checks": [],
    })
    telemetry = collect_process_telemetry()
    interval_minutes = int(CFG.get("cycles", {}).get("interval_minutes", 60))
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    tracked_files = con.execute("SELECT COUNT(*) AS count FROM files").fetchone()["count"]
    memories_total = con.execute("SELECT COUNT(*) AS count FROM memories").fetchone()["count"]
    recent_outputs = con.execute(
        """
        SELECT cycle, priority, confidence, created_at, body
        FROM memories
        ORDER BY id DESC
        LIMIT 8
        """
    ).fetchall()
    latest_runs = con.execute(
        """
        SELECT cycle, status, started_at, finished_at, duration_ms, changed_files, report_path, error_text
        FROM cycle_runs
        WHERE id IN (
            SELECT MAX(id)
            FROM cycle_runs
            GROUP BY cycle
        )
        """
    ).fetchall()
    avg_durations = {
        row["cycle"]: row["avg_duration_ms"]
        for row in con.execute(
            """
            SELECT cycle, ROUND(AVG(duration_ms)) AS avg_duration_ms
            FROM (
                SELECT cycle, duration_ms
                FROM cycle_runs
                WHERE status = 'ok'
                ORDER BY id DESC
            )
            GROUP BY cycle
            """
        )
    }
    counts_24h = {}
    cutoff = dt.datetime.now() - dt.timedelta(days=1)
    for row in con.execute("SELECT cycle, started_at FROM cycle_runs"):
        started = iso_to_dt(row["started_at"])
        if started and started >= cutoff:
            counts_24h[row["cycle"]] = counts_24h.get(row["cycle"], 0) + 1
    con.close()

    cycle_order = ["sleep", "dream", "reality", "reflect", "scorecard", "daily_snapshot"]
    runs_by_cycle = {row["cycle"]: dict(row) for row in latest_runs}
    modules = []
    for cycle in cycle_order:
        last_run = runs_by_cycle.get(cycle, {
            "cycle": cycle,
            "status": "unknown",
            "started_at": None,
            "finished_at": None,
            "duration_ms": None,
            "changed_files": None,
            "report_path": "",
            "error_text": "",
        })
        modules.append({
            **last_run,
            "state": module_state(last_run, runtime_state, interval_minutes),
            "freshness_minutes": minutes_since(last_run.get("finished_at")),
            "avg_duration_ms": avg_durations.get(cycle),
            "runs_24h": counts_24h.get(cycle, 0),
        })

    report_files = sorted(REPORTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    recent_reports = [
        {
            "name": path.name,
            "updated_at": dt.datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
            "size_kb": round(path.stat().st_size / 1024, 1),
        }
        for path in report_files[:10]
    ]

    db_stat = safe_stat(DB_PATH)
    stdout_stat = safe_stat(ENGINE_STATE_DIR / "agent_stdout.log")
    stderr_stat = safe_stat(ENGINE_STATE_DIR / "agent_stderr.log")

    tweak_notes = []
    dream_mod = next((m for m in modules if m["cycle"] == "dream"), None)
    if dream_mod and dream_mod.get("avg_duration_ms") and dream_mod["avg_duration_ms"] > 20000:
        tweak_notes.append("Dream is the heaviest module now; per-domain generation is increasing latency.")
    if tracked_files >= int(CFG.get("cycles", {}).get("max_files_per_scan", 80)) * 0.9:
        tweak_notes.append("File scan count is near the configured cap; module awareness may be truncated.")
    if operator_guidance.get("mode") in (None, "", "best_effort"):
        tweak_notes.append("No operator guidance is set. ELI Brain is using best effort.")
    tweak_notes.append("ELI Brain is project tooling only; keep operator controls out of the project's end-user runtime surfaces.")
    if not tweak_notes:
        tweak_notes.append("Current settings look stable. The clearest tweak levers are prompt strictness, scan cap, and cycle interval.")

    return {
        "project": {
            "name": CFG.get("project_display_name", CFG.get("project_name", "smart_glasses")),
            "project_root": CFG.get("project_root", ""),
            "watch_roots": [str(p) for p in watch_roots()],
            "agent_status": launch_agent_status(),
            "cycle_interval_minutes": interval_minutes,
            "current_project": runtime_state.get("current_project") or CFG.get("project_name", "smart_glasses"),
            "execution_mode": "single_project",
            "scheduler_mode": "continuous" if CFG.get("cycles", {}).get("continuous", True) else "interval",
            "pause_seconds_between_runs": int(CFG.get("cycles", {}).get("pause_seconds_between_runs", 5)),
            "eli_role": "project refinement, architecture critique, and task guidance",
            "state_write_mode": runtime_state.get("runtime_mode", "unknown"),
            "state_write_summary": runtime_state.get("summary", ""),
        },
        "runtime_state": runtime_state,
        "operator_guidance": operator_guidance,
        "action_inbox": action_inbox,
        "project_expectations": project_expectations,
        "project_milestones": project_milestones,
        "product_realism_review": product_realism_review,
        "execution_resume": execution_resume,
        "execution_boundaries": execution_boundaries,
        "project_direction_review": project_direction_review,
        "exploratory_ideas_review": exploratory_ideas_review,
        "operator_proposal_review": operator_proposal_review,
        "similar_products_review": similar_products_review,
        "reuse_recommendation_review": reuse_recommendation_review,
        "project_topology_view": project_topology_view,
        "component_package_review": component_package_review,
        "parts_readiness_review": parts_readiness_review,
        "pricing_alternatives_review": pricing_alternatives_review,
        "budget_tier_review": budget_tier_review,
        "cost_viability_review": cost_viability_review,
        "hardware_aware_rendering_brief_review": hardware_aware_rendering_brief_review,
        "extensions_capability_review": extensions_capability_review,
        "extension_deployment_review": extension_deployment_review,
        "ui_surface_plan": ui_surface_plan,
        "scorecard": scorecard,
        "verification_summary": verification_summary,
        "telemetry": telemetry,
        "modules": modules,
        "load": {
            "tracked_files": tracked_files,
            "memories_total": memories_total,
            "report_count": len(report_files),
            "db_size_kb": round((db_stat.st_size if db_stat else 0) / 1024, 1),
            "stdout_kb": round((stdout_stat.st_size if stdout_stat else 0) / 1024, 1),
            "stderr_kb": round((stderr_stat.st_size if stderr_stat else 0) / 1024, 1),
            "tweak_notes": tweak_notes,
        },
        "valuable_outputs": [
            {
                "cycle": row["cycle"],
                "priority": row["priority"],
                "confidence": row["confidence"],
                "created_at": row["created_at"],
                "excerpt": " ".join((row["body"] or "").split())[:320],
            }
            for row in recent_outputs
        ],
        "recent_reports": recent_reports,
    }


def save_guidance(mode, note=""):
    payload = {
        "mode": mode or "best_effort",
        "note": note.strip(),
        "updated_at": dt.datetime.now().isoformat(timespec="seconds"),
    }
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    OPERATOR_GUIDANCE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


class DashboardHandler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            html = HTML_PATH.read_text(encoding="utf-8")
            self._send(HTTPStatus.OK, html, "text/html; charset=utf-8")
            return
        if parsed.path == "/api/status":
            self._send(HTTPStatus.OK, json.dumps(load_dashboard_data()).encode("utf-8"))
            return
        self._send(HTTPStatus.NOT_FOUND, json.dumps({"error": "not found"}).encode("utf-8"))

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else ""
        try:
            payload = json.loads(raw) if raw else {}
        except Exception:
            payload = parse_qs(raw)
        if parsed.path == "/api/guidance":
            if isinstance(payload, dict) and "mode" in payload:
                mode = payload.get("mode")
                if isinstance(mode, list):
                    mode = mode[0]
                note = payload.get("note", "")
                if isinstance(note, list):
                    note = note[0]
                saved = save_guidance(mode, note)
                self._send(HTTPStatus.OK, json.dumps(saved).encode("utf-8"))
                return
            self._send(HTTPStatus.BAD_REQUEST, json.dumps({"error": "mode is required"}).encode("utf-8"))
            return
        if parsed.path == "/api/action-choice":
            action_id = payload.get("action_id") if isinstance(payload, dict) else None
            choice_id = payload.get("choice_id") if isinstance(payload, dict) else None
            if isinstance(action_id, list):
                action_id = action_id[0]
            if isinstance(choice_id, list):
                choice_id = choice_id[0]
            if not action_id or not choice_id:
                self._send(HTTPStatus.BAD_REQUEST, json.dumps({"error": "action_id and choice_id are required"}).encode("utf-8"))
                return
            try:
                updated = update_action_choice(action_id, choice_id)
            except ValueError as exc:
                self._send(HTTPStatus.BAD_REQUEST, json.dumps({"error": str(exc)}).encode("utf-8"))
                return
            self._send(HTTPStatus.OK, json.dumps(updated).encode("utf-8"))
            return
        self._send(HTTPStatus.NOT_FOUND, json.dumps({"error": "not found"}).encode("utf-8"))

    def do_DELETE(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/guidance":
            saved = save_guidance("best_effort", "")
            self._send(HTTPStatus.OK, json.dumps(saved).encode("utf-8"))
            return
        if parsed.path == "/api/action-choice":
            query = parse_qs(parsed.query)
            action_id = (query.get("action_id") or [""])[0]
            if not action_id:
                self._send(HTTPStatus.BAD_REQUEST, json.dumps({"error": "action_id is required"}).encode("utf-8"))
                return
            try:
                updated = update_action_choice(action_id, None)
            except ValueError as exc:
                self._send(HTTPStatus.BAD_REQUEST, json.dumps({"error": str(exc)}).encode("utf-8"))
                return
            self._send(HTTPStatus.OK, json.dumps(updated).encode("utf-8"))
            return
        self._send(HTTPStatus.NOT_FOUND, json.dumps({"error": "not found"}).encode("utf-8"))

    def log_message(self, format, *args):
        return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8421, type=int)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    print(f"Dashboard running on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
