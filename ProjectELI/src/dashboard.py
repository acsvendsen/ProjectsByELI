#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import pathlib
import sqlite3
import subprocess
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from orchestrator import (
    ACTION_INBOX_PATH,
    BASE,
    CFG,
    DB_PATH,
    OPERATOR_GUIDANCE_PATH,
    PROJECT_DIR,
    REPORTS_DIR,
    RUNTIME_STATE_PATH,
    SCORECARD_STATE_PATH,
    STATE_DIR,
    ensure_db,
    watch_roots,
)

UI_DIR = BASE / "ui"
HTML_PATH = UI_DIR / "dashboard.html"
ENGINE_STATE_DIR = BASE / "state"


def read_json(path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


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
    operator_guidance = read_json(OPERATOR_GUIDANCE_PATH, {"mode": "best_effort"})
    action_inbox = load_action_inbox_data()
    scorecard = read_json(SCORECARD_STATE_PATH, {"project_summary": "", "dimensions": []})
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
        },
        "runtime_state": runtime_state,
        "operator_guidance": operator_guidance,
        "action_inbox": action_inbox,
        "scorecard": scorecard,
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
