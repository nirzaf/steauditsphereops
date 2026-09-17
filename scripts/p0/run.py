#!/usr/bin/env python3
"""Run the explicit, bounded P0 suite registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SUITES = {"build", "identity", "documents", "transactions", "recovery", "accounting", "privileged"}
P0_BY_SUITE = {
    "build": ["P0-01"],
    "identity": ["P0-02"],
    "documents": ["P0-05", "P0-09"],
    "transactions": ["P0-06"],
    "recovery": ["P0-10", "P0-11"],
    "accounting": ["P0-07"],
    "privileged": ["P0-08"],
}


def manifest_digest() -> str:
    paths = [ROOT / "infra/production/versions.json", ROOT / "spikes/p0/schema.sql", ROOT / "docs/production/p0-index.json"]
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.relative_to(ROOT).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def mock(suite: str) -> tuple[str, str, list[str]]:
    trace = [f"registry:{suite}", "deterministic-fixture:seed=p0-v1", f"manifest:{manifest_digest()}"]
    if suite == "build":
        check = subprocess.run([sys.executable, str(ROOT / "scripts/wbs/check_versions.py"), str(ROOT / "infra/production/versions.json")], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        trace.append(f"version-check:returncode={check.returncode}")
        if check.returncode:
            return "FAIL", "pinned version contract rejected", trace
    return "MOCK_PASS", "Synthetic runner self-test only; this is not LIVE_PASS.", trace


def live(suite: str) -> tuple[str, str, list[str]]:
    trace = [f"registry:{suite}", f"manifest:{manifest_digest()}"]
    if suite != "build":
        return "BLOCKED", "This suite is owned by WBS-05/06/07 and no future service is called by WBS-04.", trace
    env = os.environ.copy()
    provision = subprocess.run([sys.executable, str(ROOT / "scripts/p0/provision_local.py"), "--live"], cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    trace.append(f"provision:returncode={provision.returncode}")
    try:
        outcome = json.loads(provision.stdout.decode(errors="replace"))
    except json.JSONDecodeError:
        return "FAIL", "provisioner returned non-JSON output", trace
    status = outcome.get("status")
    if status == "PASS":
        return "LIVE_PASS", str(outcome.get("reason")), trace
    if status == "BLOCKED":
        return "BLOCKED", str(outcome.get("reason")), trace
    return "FAIL", str(outcome.get("reason")), trace


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=sorted(SUITES), required=True)
    parser.add_argument("--mode", choices=("mock", "live"), required=True)
    args = parser.parse_args()
    status, outcome, trace = mock(args.suite) if args.mode == "mock" else live(args.suite)
    evidence = {
        "schema": "steauditsphereops/p0-evidence@1",
        "source_experiment_ids": P0_BY_SUITE.get(args.suite, []),
        "suite": args.suite,
        "mode": args.mode,
        "status": status,
        "outcome": outcome,
        "declared_dependency_manifest": manifest_digest(),
        "targets": ["POC_TARGET_REDACTED"],
        "trace": trace,
        "monotonic_started_ns": time.monotonic_ns(),
    }
    evidence_dir = ROOT / ".local/p0-evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / f"{args.suite}-{args.mode}-{time.time_ns()}.json"
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    evidence["evidence_path"] = evidence_path.relative_to(ROOT).as_posix()
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0 if status in {"MOCK_PASS", "LIVE_PASS"} else (2 if status == "BLOCKED" else 1)


if __name__ == "__main__":
    sys.exit(main())
