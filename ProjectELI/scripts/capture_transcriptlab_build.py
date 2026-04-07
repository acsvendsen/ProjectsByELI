#!/usr/bin/env python3
import datetime as dt
import os
import pathlib
import subprocess


BASE = pathlib.Path(__file__).resolve().parents[1]
STATE_DIR = BASE / "state"
SUMMARY_PATH = STATE_DIR / "transcriptlab_xcode_build_summary.md"
LOG_PATH = STATE_DIR / "transcriptlab_xcodebuild.log"
PROJECT_PATH = pathlib.Path("/Users/acs/Development/SmartGlasses/app/ios/TranscriptLab/TranscriptLab.xcodeproj")
WORKDIR = PROJECT_PATH.parent


def collect_key_lines(output):
    lines = []
    for raw in output.splitlines():
        line = raw.strip()
        if not line:
            continue
        if (
            line.startswith("Command line invocation:")
            or line.startswith("Build settings from command line:")
            or line.startswith("note:")
            or "** BUILD " in line
            or " error:" in line
            or " warning:" in line
        ):
            lines.append(line)
    if not lines:
        lines = [line.strip() for line in output.splitlines() if line.strip()][-20:]
    return lines[-40:]


def main():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now()
    env = dict(os.environ)
    env.setdefault("DEVELOPER_DIR", "/Applications/Xcode.app/Contents/Developer")
    cmd = [
        "xcodebuild",
        "-project",
        str(PROJECT_PATH),
        "-scheme",
        "TranscriptLab",
        "-sdk",
        "iphonesimulator",
        "-destination",
        "generic/platform=iOS Simulator",
        "build",
        "CODE_SIGNING_ALLOWED=NO",
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(WORKDIR),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    finished = dt.datetime.now()
    duration_ms = int((finished - started).total_seconds() * 1000)
    combined = (proc.stdout or "") + ("\n" if proc.stdout and proc.stderr else "") + (proc.stderr or "")
    LOG_PATH.write_text(combined, encoding="utf-8")

    error_count = sum(1 for line in combined.splitlines() if " error: " in line)
    warning_count = sum(1 for line in combined.splitlines() if " warning: " in line)
    success = proc.returncode == 0 and "** BUILD SUCCEEDED **" in combined
    status = "succeeded" if success else "failed"
    key_lines = collect_key_lines(combined)

    lines = [
        "# TranscriptLab Xcode Build Summary",
        "",
        f"- status: {status}",
        f"- exit_code: {proc.returncode}",
        f"- started_at: {started.isoformat(timespec='seconds')}",
        f"- finished_at: {finished.isoformat(timespec='seconds')}",
        f"- duration_ms: {duration_ms}",
        f"- warnings: {warning_count}",
        f"- errors: {error_count}",
        f"- project: {PROJECT_PATH}",
        f"- log_path: {LOG_PATH}",
        "",
        "## Key Output",
        "",
    ]
    for line in key_lines:
        lines.append(f"- {line}")
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(SUMMARY_PATH)


if __name__ == "__main__":
    main()
