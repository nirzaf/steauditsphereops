#!/usr/bin/env python3
"""Validate the WBS-01 source baseline and execution-status ledger."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


EXPECTED_TASK_IDS = [f"{number:02d}" for number in range(1, 73)]
LEGAL_STATES = {"NOT_STARTED", "IN_PROGRESS", "BLOCKED", "ACCEPTED"}
REQUIRED_BASELINE_MARKERS = (
    "nirzaf/steauditsphereops",
    "nirzaf/steauditqts",
    "2898e44f6732c8b37c31ddfbeab0e322d7574ffe",
    "ANLCKQmu2G_lj5urAbbPvWKjY81cbKLwI_hulbiCl-vh367JYEms9Jcaq5Y9kM-iL4CUE9FkPfmtnXVhku8UHNGRwblC9TWu9u20eVplsnU",
    "docs/requirements-manifest.md",
    "cc20087acee6813b43c7d72edc123402e25316ed",
    "src/v5Data.js",
    "2b9270e806ad83871e481d24e49b9533592d371f",
    "src/domain/traceability.js",
    "1e65880eb3809dc3caf7bc0b0994510f4951718f",
    "docs/demo-shell-architecture.md",
    "80412d3aef032d8ea05143acd067fdabe38e5524",
    "package.json",
    "62de2d105a7b43228a84ff9373c02ef66d5d9d4c",
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
        approval = re.search(r"(?m)^owner_approval:\s*(\S+)\s*$", baseline_text)
        reference = re.search(r"(?m)^approval_reference:\s*(\S+)\s*$", baseline_text)
        if not approval or approval.group(1) != "APPROVED":
            errors.append("owner-approved baseline disposition is required")
        elif not reference or reference.group(1).lower() in {"none", "null", "missing"}:
            errors.append("approved baseline disposition needs a non-empty approval reference")

    if not status_path.is_file():
        errors.append(f"missing {status_path}")
        return errors

    try:
        status = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot parse execution status: {exc}")
        return errors

    if not isinstance(status, dict):
        errors.append("execution status root must be an object")
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
            commit = task.get("commit")
            if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{7,64}", commit):
                errors.append(f"accepted task {task_id} needs a hexadecimal tested commit")
            tests = task.get("tests")
            if not tests or any(not isinstance(test, str) or not test.strip() for test in tests):
                errors.append(f"accepted task {task_id} needs observable test results")
            evidence_path = task.get("evidence_path")
            evidence_is_url = isinstance(evidence_path, str) and evidence_path.startswith(("https://", "http://"))
            evidence_file = root / evidence_path if isinstance(evidence_path, str) and not Path(evidence_path).is_absolute() else None
            evidence_exists = evidence_is_url or (evidence_file is not None and evidence_file.is_file())
            if not isinstance(evidence_path, str) or not evidence_path.strip() or not evidence_exists:
                errors.append(f"accepted task {task_id} needs a verifiable evidence path or URL")

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
