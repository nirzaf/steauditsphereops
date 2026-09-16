#!/usr/bin/env python3
"""Validate the WBS-01 source baseline and execution-status ledger."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


EXPECTED_TASK_IDS = [f"{number:02d}" for number in range(1, 73)]
LEGAL_STATES = {"NOT_STARTED", "IN_PROGRESS", "BLOCKED", "ACCEPTED"}
REQUIRED_BASELINE_MARKERS = (
    "nirzaf/steauditsphereops",
    "nirzaf/steauditqts",
    "2898e44f6732c8b37c31ddfbeab0e322d7574ffe",
    "ANLCKQmu2G_lj5urAbbPvWKjY81cbKLwI_hulbiCl-vh367JYEms9Jcaq5Y9kM-iL4CUE9FkPfmtnXVhku8UHNGRwblC9TWu9u20eVplsnU",
    "owner_approval:",
)


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    baseline_path = root / "docs/production/source-baseline.md"
    status_path = root / "docs/production/execution-status.json"

    if not baseline_path.is_file():
        errors.append(f"missing {baseline_path}")
        baseline_text = ""
    else:
        baseline_text = baseline_path.read_text(encoding="utf-8")
        for marker in REQUIRED_BASELINE_MARKERS:
            if marker not in baseline_text:
                errors.append(f"source baseline is missing reference: {marker}")
        if "owner_approval: APPROVED" not in baseline_text:
            errors.append("owner-approved baseline disposition is required")

    if not status_path.is_file():
        errors.append(f"missing {status_path}")
        return errors

    try:
        status = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot parse execution status: {exc}")
        return errors

    if status.get("schema") != "steauditsphereops/execution-status@1":
        errors.append("execution status schema must be steauditsphereops/execution-status@1")
    if status.get("repo") != "nirzaf/steauditsphereops":
        errors.append("execution status repo must be nirzaf/steauditsphereops")
    tasks = status.get("tasks")
    if not isinstance(tasks, list):
        errors.append("execution status tasks must be a list")
        return errors

    task_ids = [task.get("task_id") for task in tasks if isinstance(task, dict)]
    if task_ids != EXPECTED_TASK_IDS:
        errors.append("execution status task IDs must be the ordered sequence 01 through 72")

    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append(f"task entry {index} must be an object")
            continue
        task_id = task.get("task_id", f"entry {index}")
        missing = {
            "task_id",
            "wbs",
            "issue",
            "issue_url",
            "github_label",
            "milestone",
            "risk",
            "state",
            "commit",
            "tests",
            "evidence_path",
            "blocker",
        } - task.keys()
        if missing:
            errors.append(f"task {task_id} is missing fields: {', '.join(sorted(missing))}")
        if task.get("state") not in LEGAL_STATES:
            errors.append(f"task {task_id} has illegal state: {task.get('state')!r}")
        if not isinstance(task.get("tests"), list):
            errors.append(f"task {task_id} tests must be a list")
        if task.get("state") == "ACCEPTED":
            for field in ("commit", "evidence_path"):
                if not task.get(field):
                    errors.append(f"accepted task {task_id} needs {field}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("BASELINE CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("BASELINE CHECK: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
