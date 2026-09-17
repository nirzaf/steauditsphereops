#!/usr/bin/env python3
"""Safely validate or provision the disposable WBS-04 POC substrate."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COMPOSE = ROOT / "infra/production/poc.compose.yml"
SCHEMA = ROOT / "spikes/p0/schema.sql"
APP = ROOT / "spikes/p0/audit_poc"


def result(status: str, reason: str, **extra: object) -> dict[str, object]:
    return {"status": status, "reason": reason, **extra}


def safety() -> tuple[dict[str, str] | None, dict[str, object] | None]:
    required = {
        "AUDIT_POC_ENV": os.environ.get("AUDIT_POC_ENV", ""),
        "AUDIT_SITE": os.environ.get("AUDIT_SITE", ""),
        "POC_DB_NAME": os.environ.get("POC_DB_NAME", ""),
        "POC_DB_PASSWORD": os.environ.get("POC_DB_PASSWORD", ""),
    }
    if required["AUDIT_POC_ENV"] != "POC":
        return None, result("BLOCKED", "AUDIT_POC_ENV must be exactly POC")
    site = required["AUDIT_SITE"]
    if not site.endswith(".localhost") or any(token in site.casefold() for token in ("prod", "production", "live")):
        return None, result("BLOCKED", "AUDIT_SITE must be an allowlisted local .localhost site")
    if required["POC_DB_NAME"] != "audit_poc":
        return None, result("BLOCKED", "POC_DB_NAME must be exactly audit_poc")
    if not required["POC_DB_PASSWORD"]:
        return None, result("BLOCKED", "POC_DB_PASSWORD is required for live disposable provisioning")
    if shutil.which("docker") is None:
        return None, result("BLOCKED", "docker is not installed")
    runtime_env = os.environ.copy()
    runtime_env.update(required)
    return runtime_env, None


def run_fixed(args: list[str], *, env: dict[str, str], input_bytes: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(args, cwd=ROOT, env=env, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def validate_only() -> dict[str, object]:
    if not COMPOSE.is_file() or not SCHEMA.is_file() or not APP.is_dir():
        return result("FAIL", "POC compose, schema, or app skeleton is missing")
    env = os.environ.copy()
    env.update({"POC_DB_PASSWORD": "validation-only", "AUDIT_POC_ENV": "POC", "AUDIT_SITE": "auditflow-poc.localhost", "POC_DB_NAME": "audit_poc"})
    check = run_fixed(["docker", "compose", "-f", str(COMPOSE), "config", "--quiet"], env=env)
    if check.returncode:
        return result("FAIL", "docker compose config rejected the pinned POC definition", returncode=check.returncode)
    schema_text = SCHEMA.read_text(encoding="utf-8")
    required_tables = ("scope_guard", "poc_package", "command_receipt", "poc_outbox", "checkpoint_reference", "poc_audit_event")
    missing = [table for table in required_tables if f"CREATE TABLE IF NOT EXISTS {table}" not in schema_text]
    if missing:
        return result("FAIL", "schema is missing required proof tables", missing=missing)
    return result("VALIDATED", "local safety checks, compose syntax, app skeleton, and schema markers pass")


def live() -> dict[str, object]:
    env, blocked = safety()
    if blocked:
        return blocked
    assert env is not None
    info = run_fixed(["docker", "info", "--format", "{{.ServerVersion}}"], env=env)
    if info.returncode:
        return result("BLOCKED", "docker daemon is unavailable")
    down = run_fixed(["docker", "compose", "-f", str(COMPOSE), "down", "--volumes", "--remove-orphans"], env=env)
    if down.returncode:
        return result("FAIL", "clean disposable resources could not be removed", returncode=down.returncode)
    up = run_fixed(["docker", "compose", "-f", str(COMPOSE), "up", "--detach", "--wait", "mariadb", "redis", "frappe"], env=env)
    if up.returncode:
        return result("FAIL", "pinned disposable services did not become healthy", returncode=up.returncode)

    credential_file: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", prefix="audit-poc-", suffix=".cnf", delete=False) as handle:
            credential_file = Path(handle.name)
            handle.write(f"[client]\nuser=root\npassword={env['POC_DB_PASSWORD']}\n")
        copy = run_fixed(["docker", "compose", "-f", str(COMPOSE), "cp", str(credential_file), "mariadb:/tmp/poc.cnf"], env=env)
        if copy.returncode:
            return result("FAIL", "database credential handoff failed", returncode=copy.returncode)
        apply_schema = run_fixed(["docker", "compose", "-f", str(COMPOSE), "exec", "--no-TTY", "mariadb", "mariadb", "--defaults-extra-file=/tmp/poc.cnf", "audit_poc"], env=env, input_bytes=SCHEMA.read_bytes())
        if apply_schema.returncode:
            return result("FAIL", "POC schema migration failed", returncode=apply_schema.returncode)
        compile_app = run_fixed(["docker", "compose", "-f", str(COMPOSE), "exec", "--no-TTY", "frappe", "python3", "-m", "compileall", "-q", "/workspace/audit_poc"], env=env)
        if compile_app.returncode:
            return result("FAIL", "pinned Frappe image could not compile the mounted audit_poc app", returncode=compile_app.returncode)
        versions = run_fixed(["docker", "compose", "-f", str(COMPOSE), "exec", "--no-TTY", "frappe", "bench", "version", "--format", "plain"], env=env)
        if versions.returncode:
            return result("FAIL", "pinned Frappe image did not expose the expected Bench version command", returncode=versions.returncode)
        return result("PASS", "clean disposable services, proof schema, mounted app, and Bench version command passed", dependency_output=versions.stdout.decode(errors="replace").strip())
    finally:
        if credential_file:
            credential_file.unlink(missing_ok=True)
        run_fixed(["docker", "compose", "-f", str(COMPOSE), "exec", "--no-TTY", "mariadb", "rm", "-f", "/tmp/poc.cnf"], env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-only", action="store_true")
    mode.add_argument("--live", action="store_true")
    args = parser.parse_args()
    outcome = validate_only() if args.validate_only else live()
    print(json.dumps(outcome, sort_keys=True))
    return 0 if outcome["status"] in {"VALIDATED", "PASS"} else (2 if outcome["status"] == "BLOCKED" else 1)


if __name__ == "__main__":
    sys.exit(main())
