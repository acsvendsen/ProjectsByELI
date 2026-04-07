import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "config.yaml"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def now_local_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


@dataclass
class Config:
    ollama_base_url: str
    ollama_model: str
    scheduler_poll_seconds: int
    sleep_minutes: int
    dream_minutes: int
    reality_minutes: int
    snapshot_minutes: int
    notify_min_priority: float
    notify_top_n: int
    projects_dir: Path
    data_dir: Path
    logs_dir: Path


class ProjectCognition:
    def __init__(self, root: Path = ROOT):
        self.root = root
        self.config = self.load_config()
        self.projects_dir = self.root / self.config.projects_dir
        self.data_dir = self.root / self.config.data_dir
        self.logs_dir = self.root / self.config.logs_dir
        self.db_path = self.data_dir / "memory.db"
        self.ensure_dirs()
        self.conn = self.connect_db()

    def load_config(self) -> Config:
        raw = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
        return Config(
            ollama_base_url=raw["ollama"]["base_url"].rstrip("/"),
            ollama_model=raw["ollama"]["model"],
            scheduler_poll_seconds=int(raw["scheduler"].get("poll_seconds", 60)),
            sleep_minutes=int(raw["scheduler"].get("sleep_minutes", 60)),
            dream_minutes=int(raw["scheduler"].get("dream_minutes", 180)),
            reality_minutes=int(raw["scheduler"].get("reality_minutes", 240)),
            snapshot_minutes=int(raw["scheduler"].get("snapshot_minutes", 360)),
            notify_min_priority=float(raw["notifications"].get("min_priority", 0.72)),
            notify_top_n=int(raw["notifications"].get("top_n", 3)),
            projects_dir=Path(raw["paths"]["projects_dir"]),
            data_dir=Path(raw["paths"]["data_dir"]),
            logs_dir=Path(raw["paths"]["logs_dir"]),
        )

    def ensure_dirs(self):
        for p in [self.projects_dir, self.data_dir, self.logs_dir]:
            p.mkdir(parents=True, exist_ok=True)

    def connect_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memory_objects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT NOT NULL,
                cycle_type TEXT NOT NULL,
                kind TEXT NOT NULL,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                source_hash TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                relevance REAL DEFAULT 0.5,
                freshness REAL DEFAULT 0.5,
                recurrence REAL DEFAULT 0.0,
                feasibility REAL DEFAULT 0.5,
                novelty REAL DEFAULT 0.5,
                priority REAL DEFAULT 0.5,
                status TEXT DEFAULT 'active',
                notified INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(project, source_hash)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cycle_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT NOT NULL,
                cycle_type TEXT NOT NULL,
                report_path TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS file_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT NOT NULL,
                path TEXT NOT NULL,
                mtime REAL NOT NULL,
                sha1 TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(project, path)
            )
            """
        )
        conn.commit()
        return conn

    def close(self):
        self.conn.close()

    def read_text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            return ""

    def project_files(self, project_dir: Path) -> List[Path]:
        files = []
        for folder in [project_dir / "core", project_dir / "inbox"]:
            if folder.exists():
                files.extend(sorted(folder.glob("*.md")))
        return files

    def collect_project_state(self, project_dir: Path) -> Dict[str, Any]:
        core_dir = project_dir / "core"
        inbox_dir = project_dir / "inbox"
        core_files = sorted(core_dir.glob("*.md")) if core_dir.exists() else []
        inbox_files = sorted(inbox_dir.glob("*.md")) if inbox_dir.exists() else []
        core_text = "\n\n".join(self.read_text(p) for p in core_files)
        inbox_text = "\n\n".join(self.read_text(p) for p in inbox_files)
        memory_summary = self.fetch_recent_memory(project_dir.name, limit=20)
        return {
            "project": project_dir.name,
            "core_text": core_text,
            "inbox_text": inbox_text,
            "core_files": [str(p.relative_to(self.root)) for p in core_files],
            "inbox_files": [str(p.relative_to(self.root)) for p in inbox_files],
            "recent_memory": memory_summary,
        }

    def fetch_recent_memory(self, project_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT kind, title, priority, confidence, relevance, feasibility, created_at, status
            FROM memory_objects
            WHERE project = ?
            ORDER BY updated_at DESC, id DESC
            LIMIT ?
            """,
            (project_name, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def ollama_generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.4) -> str:
        payload = {
            "model": self.config.ollama_model,
            "format": "json",
            "stream": False,
            "options": {"temperature": temperature},
            "prompt": f"SYSTEM:\n{system_prompt}\n\nUSER:\n{user_prompt}",
        }
        response = requests.post(
            f"{self.config.ollama_base_url}/api/generate",
            json=payload,
            timeout=240,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "{}").strip()

    def prompt_template(self, name: str) -> str:
        return (self.root / "prompts" / name).read_text(encoding="utf-8")

    def parse_json_response(self, raw: str) -> Dict[str, Any]:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise

    def build_prompt_context(self, state: Dict[str, Any], cycle_type: str) -> str:
        return json.dumps(
            {
                "cycle_type": cycle_type,
                "project": state["project"],
                "core_files": state["core_files"],
                "inbox_files": state["inbox_files"],
                "core_text": state["core_text"][:18000],
                "inbox_text": state["inbox_text"][:18000],
                "recent_memory": state["recent_memory"][:20],
                "instructions": {
                    "return_json_only": True,
                    "max_memory_objects": 10,
                    "require_grounding": True,
                },
            },
            ensure_ascii=False,
            indent=2,
        )

    def compute_priority(
        self,
        confidence: float,
        relevance: float,
        freshness: float,
        recurrence: float,
        feasibility: float,
        novelty: float,
        kind: str,
    ) -> float:
        base = (
            confidence * 0.20
            + relevance * 0.24
            + freshness * 0.12
            + recurrence * 0.16
            + feasibility * 0.18
            + novelty * 0.10
        )
        bonus = 0.0
        if kind in {"contradiction", "drift_risk", "core_shift", "high_value_suggestion"}:
            bonus += 0.08
        return max(0.0, min(1.0, round(base + bonus, 4)))

    def recurrence_for_title(self, project: str, title: str) -> float:
        row = self.conn.execute(
            "SELECT COUNT(*) AS c FROM memory_objects WHERE project = ? AND lower(title) = lower(?)",
            (project, title.strip()),
        ).fetchone()
        count = int(row["c"]) if row else 0
        return min(1.0, count / 5.0)

    def upsert_memory(self, project: str, cycle_type: str, item: Dict[str, Any]):
        title = item.get("title", "Untitled").strip()
        body = item.get("body", "").strip()
        kind = item.get("kind", cycle_type).strip() or cycle_type
        confidence = float(item.get("confidence", 0.5))
        relevance = float(item.get("relevance", 0.5))
        freshness = float(item.get("freshness", 0.7))
        feasibility = float(item.get("feasibility", 0.5))
        novelty = float(item.get("novelty", 0.5))
        recurrence = float(item.get("recurrence", self.recurrence_for_title(project, title)))
        priority = self.compute_priority(
            confidence, relevance, freshness, recurrence, feasibility, novelty, kind
        )
        status = item.get("status", "active")
        source_hash = sha1_text(f"{project}|{kind}|{title}|{body}")
        ts = utc_now().isoformat()
        self.conn.execute(
            """
            INSERT INTO memory_objects (
                project, cycle_type, kind, title, body, source_hash,
                confidence, relevance, freshness, recurrence, feasibility, novelty,
                priority, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project, source_hash) DO UPDATE SET
                cycle_type = excluded.cycle_type,
                confidence = excluded.confidence,
                relevance = excluded.relevance,
                freshness = excluded.freshness,
                recurrence = excluded.recurrence,
                feasibility = excluded.feasibility,
                novelty = excluded.novelty,
                priority = excluded.priority,
                status = excluded.status,
                updated_at = excluded.updated_at
            """,
            (
                project,
                cycle_type,
                kind,
                title,
                body,
                source_hash,
                confidence,
                relevance,
                freshness,
                recurrence,
                feasibility,
                novelty,
                priority,
                status,
                ts,
                ts,
            ),
        )
        self.conn.commit()

    def write_report(self, project_dir: Path, name: str, content: str) -> Path:
        reports = project_dir / "reports"
        reports.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = reports / f"{timestamp}_{name}.md"
        path.write_text(content, encoding="utf-8")
        return path

    def record_cycle(self, project_name: str, cycle_type: str, report_path: Path):
        self.conn.execute(
            "INSERT INTO cycle_runs (project, cycle_type, report_path, created_at) VALUES (?, ?, ?, ?)",
            (project_name, cycle_type, str(report_path.relative_to(self.root)), utc_now().isoformat()),
        )
        self.conn.commit()

    def markdown_report(self, cycle_title: str, project_name: str, result: Dict[str, Any]) -> str:
        lines = [f"# {cycle_title}", "", f"**Project:** {project_name}", ""]
        if result.get("summary"):
            lines += ["## Summary", result["summary"], ""]
        for section_title, key in [
            ("Key Findings", "findings"),
            ("Suggestions", "suggestions"),
            ("Constraints", "constraints"),
            ("Questions", "questions"),
        ]:
            items = result.get(key, [])
            if items:
                lines += [f"## {section_title}"]
                for item in items:
                    if isinstance(item, dict):
                        title = item.get("title") or item.get("label") or "Item"
                        body = item.get("body") or item.get("reason") or item.get("details") or ""
                        lines.append(f"- **{title}** — {body}")
                    else:
                        lines.append(f"- {item}")
                lines.append("")
        mem = result.get("memory_objects", [])
        if mem:
            lines += ["## Memory Objects"]
            for item in mem:
                priority = self.compute_priority(
                    float(item.get('confidence', 0.5)),
                    float(item.get('relevance', 0.5)),
                    float(item.get('freshness', 0.7)),
                    float(item.get('recurrence', 0.0)),
                    float(item.get('feasibility', 0.5)),
                    float(item.get('novelty', 0.5)),
                    item.get('kind', 'item'),
                )
                lines.append(
                    f"- **{item.get('kind','item')}** | {item.get('title','Untitled')} | priority≈{priority:.2f}"
                )
            lines.append("")
        return "\n".join(lines).strip() + "\n"

    def run_llm_cycle(self, project_dir: Path, cycle_type: str, prompt_file: str, report_name: str) -> Optional[Path]:
        state = self.collect_project_state(project_dir)
        system_prompt = self.prompt_template(prompt_file)
        user_prompt = self.build_prompt_context(state, cycle_type)
        try:
            raw = self.ollama_generate(system_prompt, user_prompt)
            result = self.parse_json_response(raw)
        except Exception as exc:
            error_report = self.write_report(
                project_dir,
                f"{report_name}_error",
                f"# {cycle_type.title()} Error\n\n{type(exc).__name__}: {exc}\n",
            )
            self.record_cycle(project_dir.name, f"{cycle_type}_error", error_report)
            return error_report

        for item in result.get("memory_objects", []):
            self.upsert_memory(project_dir.name, cycle_type, item)

        report = self.markdown_report(cycle_type.replace("_", " ").title(), project_dir.name, result)
        report_path = self.write_report(project_dir, report_name, report)
        self.record_cycle(project_dir.name, cycle_type, report_path)
        return report_path

    def snapshot_cycle(self, project_dir: Path) -> Path:
        project_name = project_dir.name
        rows = self.conn.execute(
            """
            SELECT kind, title, priority, confidence, relevance, feasibility, novelty, status, updated_at
            FROM memory_objects
            WHERE project = ?
            ORDER BY priority DESC, updated_at DESC
            LIMIT 15
            """,
            (project_name,),
        ).fetchall()
        lines = ["# Daily Field Snapshot", "", f"**Project:** {project_name}", "", "## Top Active Memory"]
        for row in rows:
            lines.append(
                f"- **{row['title']}** ({row['kind']}) — priority {row['priority']:.2f}, confidence {row['confidence']:.2f}, feasibility {row['feasibility']:.2f}, status {row['status']}"
            )
        lines += ["", f"Generated: {now_local_str()}"]
        path = self.write_report(project_dir, "field_snapshot", "\n".join(lines) + "\n")
        self.record_cycle(project_name, "snapshot", path)
        return path

    def changed_files(self, project_dir: Path) -> List[str]:
        changed: List[str] = []
        project = project_dir.name
        for file_path in self.project_files(project_dir):
            stat = file_path.stat()
            text = self.read_text(file_path)
            digest = sha1_text(text)
            rel = str(file_path.relative_to(self.root))
            row = self.conn.execute(
                "SELECT mtime, sha1 FROM file_state WHERE project = ? AND path = ?",
                (project, rel),
            ).fetchone()
            if row is None or float(row["mtime"]) != stat.st_mtime or row["sha1"] != digest:
                changed.append(rel)
                self.conn.execute(
                    """
                    INSERT INTO file_state(project, path, mtime, sha1, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(project, path) DO UPDATE SET
                        mtime = excluded.mtime,
                        sha1 = excluded.sha1,
                        updated_at = excluded.updated_at
                    """,
                    (project, rel, stat.st_mtime, digest, utc_now().isoformat()),
                )
        self.conn.commit()
        return changed

    def should_run_cycle(self, project_name: str, cycle_type: str, every_minutes: int) -> bool:
        row = self.conn.execute(
            "SELECT created_at FROM cycle_runs WHERE project = ? AND cycle_type = ? ORDER BY id DESC LIMIT 1",
            (project_name, cycle_type),
        ).fetchone()
        if row is None:
            return True
        last = datetime.fromisoformat(row["created_at"])
        return (utc_now() - last).total_seconds() >= every_minutes * 60

    def send_notifications(self, project_name: str):
        rows = self.conn.execute(
            """
            SELECT id, title, body, priority, kind
            FROM memory_objects
            WHERE project = ? AND notified = 0 AND priority >= ? AND status = 'active'
            ORDER BY priority DESC, updated_at DESC
            LIMIT ?
            """,
            (project_name, self.config.notify_min_priority, self.config.notify_top_n),
        ).fetchall()
        for row in rows:
            title = f"{project_name}: {row['title']}"
            body = (row["body"] or row["kind"])[:180]
            script = f'display notification {json.dumps(body)} with title {json.dumps(title)}'
            try:
                subprocess.run(["osascript", "-e", script], check=False, capture_output=True)
            except Exception:
                pass
            self.conn.execute("UPDATE memory_objects SET notified = 1 WHERE id = ?", (row["id"],))
        self.conn.commit()

    def run_project(self, project_dir: Path, force: bool = False, changed_hint: Optional[List[str]] = None):
        project_name = project_dir.name
        changed = changed_hint if changed_hint is not None else self.changed_files(project_dir)
        if changed:
            notes = "\n".join(f"- {c}" for c in changed)
            self.upsert_memory(
                project_name,
                "ingest",
                {
                    "kind": "ingest",
                    "title": "Project files changed",
                    "body": f"Changed files detected:\n{notes}",
                    "confidence": 1.0,
                    "relevance": 0.85,
                    "freshness": 1.0,
                    "feasibility": 1.0,
                    "novelty": 0.2,
                    "status": "active",
                },
            )

        if force or changed or self.should_run_cycle(project_name, "sleep", self.config.sleep_minutes):
            self.run_llm_cycle(project_dir, "sleep", "sleep_prompt.txt", "sleep_report")
        if force or changed or self.should_run_cycle(project_name, "dream", self.config.dream_minutes):
            self.run_llm_cycle(project_dir, "dream", "dream_prompt.txt", "dream_report")
        if force or changed or self.should_run_cycle(project_name, "reality", self.config.reality_minutes):
            self.run_llm_cycle(project_dir, "reality", "reality_prompt.txt", "reality_report")
        if force or changed or self.should_run_cycle(project_name, "snapshot", self.config.snapshot_minutes):
            self.snapshot_cycle(project_dir)
        self.send_notifications(project_name)

    def run_once(self, force: bool = False):
        for project_dir in sorted(self.projects_dir.iterdir()):
            if project_dir.is_dir():
                self.run_project(project_dir, force=force)

    def daemon_loop(self):
        while True:
            try:
                self.run_once(force=False)
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                error_path = self.logs_dir / "orchestrator_runtime_error.log"
                with error_path.open("a", encoding="utf-8") as f:
                    f.write(f"[{now_local_str()}] {type(exc).__name__}: {exc}\n")
            time.sleep(self.config.scheduler_poll_seconds)


def main(argv: List[str]):
    mode = argv[1] if len(argv) > 1 else "run-once"
    app = ProjectCognition()
    try:
        if mode == "run-once":
            app.run_once(force=True)
        elif mode == "daemon":
            app.daemon_loop()
        else:
            print("Usage: python src/orchestrator.py [run-once|daemon]")
            sys.exit(1)
    finally:
        app.close()


if __name__ == "__main__":
    main(sys.argv)
