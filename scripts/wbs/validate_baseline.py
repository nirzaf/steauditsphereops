#!/usr/bin/env python3
"""Validate the WBS-01 source baseline and execution-status ledger."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


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
    "repository_mapping:",
    "controlled_v5_source:",
    "owner_approval:",
)


def resolves_to_commit(root: Path, commit: str) -> bool:
    """Return whether commit names a commit object in the repository."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "cat-file", "-e", f"{commit}^{{commit}}"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return False
    return result.returncode == 0


def is_integrated_commit(root: Path, commit: str) -> bool:
    """Return whether commit is an ancestor of the protected main branch."""
    try:
        for ref in ("refs/remotes/origin/main", "refs/heads/main"):
            result = subprocess.run(
                ["git", "-C", str(root), "merge-base", "--is-ancestor", commit, ref],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if result.returncode == 0:
                return True
    except OSError:
        return False
    return False


def is_verifiable_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def resolve_contained(root: Path, relative_path: str) -> Path | None:
    try:
        candidate = (root / relative_path).resolve()
        candidate.relative_to(root)
    except (OSError, RuntimeError, ValueError):
        return None
    return candidate


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    baseline_relative = "docs/production/source-baseline.md"
    status_relative = "docs/production/execution-status.json"
    baseline_path = resolve_contained(root, baseline_relative)
    status_path = resolve_contained(root, status_relative)

    if baseline_path is None or not baseline_path.is_file():
        errors.append(f"missing {root / baseline_relative}")
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
        else:
            if not reference or reference.group(1).lower() in {"none", "null", "missing"}:
                errors.append("approved baseline disposition needs a non-empty approval reference")
            mapping = re.search(r"(?m)^repository_mapping:\s*(\S+)\s*$", baseline_text)
            if not mapping or mapping.group(1) not in {"APPROVED", "CONFIRMED"}:
                errors.append("approved baseline disposition needs a resolved repository mapping")
            v5_source = re.search(r"(?m)^controlled_v5_source:\s*(\S+)\s*$", baseline_text)
            if not v5_source or v5_source.group(1) not in {"PROVIDED", "CONFIRMED"}:
                errors.append("approved baseline disposition needs a resolved controlled v5 source")

    if status_path is None or not status_path.is_file():
        errors.append(f"missing {root / status_relative}")
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
        string_fields = {
            "task_id",
            "wbs",
            "issue_url",
            "github_label",
            "milestone",
            "risk",
            "state",
        }
        for field in string_fields:
            value = task.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"task {task_id} field {field} must be a non-empty string")
        issue = task.get("issue")
        if isinstance(issue, bool) or not isinstance(issue, int) or issue < 1:
            errors.append(f"task {task_id} field issue must be a positive integer")
        if isinstance(task.get("issue_url"), str) and not is_verifiable_url(task["issue_url"]):
            errors.append(f"task {task_id} field issue_url must be an absolute HTTP(S) URL")
        for field in ("commit", "evidence_path", "blocker"):
            value = task.get(field)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                errors.append(f"task {task_id} field {field} must be a non-empty string or null")
        if task.get("state") not in LEGAL_STATES:
            errors.append(f"task {task_id} has illegal state: {task.get('state')!r}")
        if index and task.get("state") in {"IN_PROGRESS", "ACCEPTED"}:
            previous_task = tasks[index - 1]
            previous_state = previous_task.get("state") if isinstance(previous_task, dict) else None
            previous_id = previous_task.get("task_id", "previous") if isinstance(previous_task, dict) else "previous"
            if previous_state != "ACCEPTED":
                errors.append(
                    f"task {task_id} cannot be {task.get('state')} until task "
                    f"{previous_id} is ACCEPTED"
                )
        if not isinstance(task.get("tests"), list):
            errors.append(f"task {task_id} tests must be a list")
        elif any(not isinstance(test, str) or not test.strip() for test in task["tests"]):
            errors.append(f"task {task_id} tests must contain non-empty strings")
        if task.get("state") == "ACCEPTED":
            commit = task.get("commit")
            if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}(?:[0-9a-f]{24})?", commit):
                errors.append(f"accepted task {task_id} needs a full hexadecimal tested commit")
            elif not resolves_to_commit(root, commit):
                errors.append(f"accepted task {task_id} commit does not resolve to a repository commit")
            elif not is_integrated_commit(root, commit):
                errors.append(f"accepted task {task_id} commit is not integrated into main")
            tests = task.get("tests")
            if not tests or any(not isinstance(test, str) or not test.strip() for test in tests):
                errors.append(f"accepted task {task_id} needs observable test results")
            evidence_path = task.get("evidence_path")
            evidence_is_url = is_verifiable_url(evidence_path)
            evidence_file = None
            if isinstance(evidence_path, str) and not evidence_path.startswith(("https://", "http://")):
                evidence_file = resolve_contained(root, evidence_path)
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
