#!/usr/bin/env python3
from __future__ import annotations

import filecmp
import hashlib
import os
from pathlib import Path
from typing import Iterable

OLD = Path("/Users/acs/Development/ProjectsByELI/SmartGlasses/smartglasses_project_cognition")
NEW = Path("/Users/acs/Development/ProjectsByELI/ProjectELI")

IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "reports",
    "state",
    ".idea",
    ".vscode",
}

IGNORE_FILES = {
    ".DS_Store",
}

TEXT_SUFFIXES = {
    ".py", ".txt", ".md", ".yaml", ".yml", ".json", ".sh", ".html", ".css"
}


def should_skip(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return True
    if path.name in IGNORE_FILES:
        return True
    if path.suffix == ".pyc":
        return True
    return False


def walk_files(root: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirpath_p = Path(dirpath)

        dirnames[:] = [d for d in dirnames if not should_skip(dirpath_p / d)]

        for filename in filenames:
            p = dirpath_p / filename
            if should_skip(p):
                continue
            rel = str(p.relative_to(root))
            files[rel] = p
    return files


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    old_files = walk_files(OLD)
    new_files = walk_files(NEW)

    old_set = set(old_files)
    new_set = set(new_files)

    only_old = sorted(old_set - new_set)
    only_new = sorted(new_set - old_set)
    common = sorted(old_set & new_set)

    changed: list[str] = []
    same: list[str] = []

    for rel in common:
        old_hash = sha256(old_files[rel])
        new_hash = sha256(new_files[rel])
        if old_hash == new_hash:
            same.append(rel)
        else:
            changed.append(rel)

    print("=== SUMMARY ===")
    print(f"Only in OLD: {len(only_old)}")
    print(f"Only in NEW: {len(only_new)}")
    print(f"Changed:     {len(changed)}")
    print(f"Same:        {len(same)}")
    print()

    if only_old:
        print("=== ONLY IN OLD ===")
        for rel in only_old:
            print(rel)
        print()

    if only_new:
        print("=== ONLY IN NEW ===")
        for rel in only_new:
            print(rel)
        print()

    if changed:
        print("=== CHANGED ===")
        for rel in changed:
            print(rel)
        print()

    # highlight the files you care about most
    priority = [
        "src/orchestrator.py",
        "src/dashboard.py",
        "prompts/dream.txt",
        "prompts/reflect.txt",
        "prompts/sleep.txt",
        "prompts/reality.txt",
        "prompts/scorecard.txt",
        "AGENTS.md",
        "README.md",
        "projects/smart_glasses/core/cognition_schema.yaml",
    ]

    print("=== PRIORITY FILE STATUS ===")
    for rel in priority:
        if rel in only_old:
            status = "ONLY_IN_OLD"
        elif rel in only_new:
            status = "ONLY_IN_NEW"
        elif rel in changed:
            status = "CHANGED"
        elif rel in same:
            status = "SAME"
        else:
            status = "MISSING_BOTH"
        print(f"{status:12} {rel}")


if __name__ == "__main__":
    main()
