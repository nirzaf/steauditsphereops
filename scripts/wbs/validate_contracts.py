#!/usr/bin/env python3
"""Validate the versioned business contracts for WBS task 02."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from graphlib import CycleError, TopologicalSorter
from pathlib import Path


PROFILES = {"ACCOUNTING_ONLY", "EXTERNAL_AUDIT_ONLY", "COMBINED", "INTERNAL_AUDIT"}
GATES = {f"G{i}" for i in range(11)}
OUTPUTS = {f"DOC-{i:02d}" for i in range(1, 27)}
PENDING = "BLOCKED_PENDING_OWNER"


def read_json(path: Path, errors: list[str]) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path}: cannot read JSON ({exc})")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path}: root must be an object")
        return {}
    return value


def ids(items: object, label: str, expected: set[str], errors: list[str]) -> set[str]:
    if not isinstance(items, list):
        errors.append(f"{label}: must be a list")
        return set()
    seen: list[str] = []
    for item in items:
        if isinstance(item, dict):
            item = item.get("id")
        if not isinstance(item, str):
            errors.append(f"{label}: every id must be a string")
        else:
            seen.append(item)
    if len(seen) != len(set(seen)):
        errors.append(f"{label}: duplicate ids")
    actual = set(seen)
    if actual != expected:
        errors.append(f"{label}: expected {sorted(expected)}, got {sorted(actual)}")
    return actual


def required(item: dict, fields: tuple[str, ...], label: str, errors: list[str]) -> None:
    for field in fields:
        if field not in item or item[field] == "":
            errors.append(f"{label}: missing {field}")


def check_root(data: dict, schema: str, label: str, errors: list[str]) -> None:
    if data.get("schema") != schema:
        errors.append(f"{label}: schema must be {schema}")
    if data.get("version") != "v5":
        errors.append(f"{label}: version must be v5")


def validate_profiles(data: dict, errors: list[str]) -> None:
    check_root(data, "steauditsphereops/service-profiles@1", "service profiles", errors)
    profiles = data.get("profiles")
    actual = ids(profiles, "service profiles", PROFILES, errors)
    if not data.get("scope_rule"):
        errors.append("service profiles: scope_rule is required")
    for profile in profiles if isinstance(profiles, list) else []:
        if not isinstance(profile, dict) or profile.get("id") not in actual:
            continue
        label = f"profile {profile.get('id')}"
        required(profile, ("id", "enabled", "capabilities", "required_gates", "audit_only_gates", "forbidden_approvals", "required_outputs", "notes"), label, errors)
        for field, expected in (("required_gates", GATES), ("audit_only_gates", GATES), ("required_outputs", OUTPUTS)):
            values = profile.get(field, [])
            if not isinstance(values, list) or any(value not in expected for value in values):
                errors.append(f"{label}: invalid {field}")
        if set(profile.get("audit_only_gates", [])) - set(profile.get("required_gates", [])):
            errors.append(f"{label}: audit-only gates must be required gates")
        if profile.get("id") == "ACCOUNTING_ONLY" and set(profile.get("required_gates", [])) & {"G5", "G6", "G7"}:
            errors.append("ACCOUNTING_ONLY: audit-only gate required")
        if profile.get("id") == "ACCOUNTING_ONLY" and "DOC-21" in profile.get("required_outputs", []):
            errors.append("ACCOUNTING_ONLY: auditor-opinion output required")


def validate_gates(data: dict, profiles: dict, errors: list[str]) -> None:
    check_root(data, "steauditsphereops/gate-contracts@1", "gate contracts", errors)
    gates = data.get("gates")
    actual = ids(gates, "gates", GATES, errors)
    if data.get("gate_order") != [f"G{i}" for i in range(11)]:
        errors.append("gate contracts: gate_order must be G0 through G10")
    by_id = {gate.get("id"): gate for gate in gates if isinstance(gate, dict)} if isinstance(gates, list) else {}
    for gate_id in actual:
        gate = by_id.get(gate_id, {})
        label = f"gate {gate_id}"
        required(gate, ("id", "title", "applicable_profiles", "prerequisites", "owner_roles", "authoritative_inputs", "blocker_codes", "invalidation_triggers"), label, errors)
        applicable = gate.get("applicable_profiles", [])
        if not isinstance(applicable, list) or not set(applicable) <= PROFILES or not applicable:
            errors.append(f"{label}: invalid applicable_profiles")
        prerequisites = gate.get("prerequisites", {})
        if not isinstance(prerequisites, dict):
            errors.append(f"{label}: prerequisites must be an object")
            continue
        if set(prerequisites) != set(applicable):
            errors.append(f"{label}: prerequisites must cover exactly applicable profiles")
        for profile, deps in prerequisites.items():
            if not isinstance(deps, list):
                errors.append(f"{label}/{profile}: prerequisites must be a list")
                continue
            if any(dep not in actual for dep in deps):
                errors.append(f"{label}/{profile}: unknown prerequisite")
            for dep in deps:
                if dep not in by_id or profile not in by_id[dep].get("applicable_profiles", []):
                    errors.append(f"{label}/{profile}: prerequisite {dep} is not applicable")
            if gate_id == "G8" and set(deps) & {"G9", "G10"}:
                errors.append(f"G8/{profile}: release gate cannot depend on G9 or G10")
        for profile in profiles:
            if profile in applicable:
                graph = {candidate: set(by_id[candidate].get("prerequisites", {}).get(profile, [])) for candidate in actual if profile in by_id[candidate].get("applicable_profiles", [])}
                try:
                    tuple(TopologicalSorter(graph).static_order())
                except CycleError as exc:
                    errors.append(f"{profile}: gate dependency cycle ({exc})")


def validate_outputs(data: dict, profiles: dict, errors: list[str]) -> None:
    check_root(data, "steauditsphereops/output-catalog@1", "output catalog", errors)
    outputs = data.get("outputs")
    actual = ids(outputs, "outputs", OUTPUTS, errors)
    by_id = {output.get("id"): output for output in outputs if isinstance(output, dict)} if isinstance(outputs, list) else {}
    for output_id in actual:
        output = by_id.get(output_id, {})
        label = f"output {output_id}"
        required(output, ("id", "title", "trigger", "owner", "applicable_profiles", "visibility", "required_fields", "template_version", "template_disposition", "producing_wbs"), label, errors)
        applicable = output.get("applicable_profiles", [])
        if not isinstance(applicable, list) or not applicable or not set(applicable) <= profiles:
            errors.append(f"{label}: invalid applicable_profiles")
        if not isinstance(output.get("required_fields"), list) or not output.get("required_fields"):
            errors.append(f"{label}: required_fields must be non-empty")
        if not isinstance(output.get("visibility"), list) or not output.get("visibility"):
            errors.append(f"{label}: visibility must be non-empty")
        if output.get("template_version") is None and output.get("template_disposition") != "BLOCKED_PENDING_OWNER_TEMPLATE":
            errors.append(f"{label}: unresolved template must be explicitly blocked")


def validate_nfr(data: dict, errors: list[str]) -> None:
    check_root(data, "steauditsphereops/nfr-targets@1", "NFR targets", errors)
    targets = data.get("targets")
    if not isinstance(targets, list) or not targets:
        errors.append("NFR targets: targets must be non-empty")
        return
    seen: set[str] = set()
    for target in targets:
        if not isinstance(target, dict):
            errors.append("NFR targets: every target must be an object")
            continue
        target_id = target.get("id")
        if target_id in seen:
            errors.append(f"NFR target {target_id}: duplicate id")
        seen.add(target_id)
        label = f"NFR target {target_id}"
        required(target, ("id", "category", "metric", "value", "unit", "status", "owner_role", "evidence", "blocks"), label, errors)
        if target.get("status") == "UNRESOLVED":
            errors.append(f"{label}: UNRESOLVED is not an allowed disposition")
        if target.get("value") is None and (target.get("status") != PENDING or not target.get("blocks")):
            errors.append(f"{label}: null value must be BLOCKED_PENDING_OWNER with blocks")


def decision_json(path: Path, errors: list[str]) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{path}: cannot read ({exc})")
        return {}
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not match:
        errors.append(f"{path}: missing fenced JSON decision register")
        return {}
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid fenced JSON ({exc})")
        return {}
    return value if isinstance(value, dict) else {}


def validate_decisions(data: dict, errors: list[str]) -> None:
    check_root(data, "steauditsphereops/decision-register@1", "decision register", errors)
    decisions = data.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        errors.append("decision register: decisions must be non-empty")
        return
    seen: set[str] = set()
    for decision in decisions:
        if not isinstance(decision, dict):
            errors.append("decision register: every decision must be an object")
            continue
        decision_id = decision.get("id")
        if decision_id in seen:
            errors.append(f"decision {decision_id}: duplicate id")
        seen.add(decision_id)
        label = f"decision {decision_id}"
        required(decision, ("id", "topic", "owner_role", "status", "decision", "evidence", "required_action", "blocks"), label, errors)
        if decision.get("status") == "UNRESOLVED":
            errors.append(f"{label}: UNRESOLVED is not an allowed disposition")
        if not decision.get("owner_role") or not decision.get("required_action") or not decision.get("blocks"):
            errors.append(f"{label}: owner, required action, and blocks are required")


def load_contracts(root: Path, errors: list[str]) -> dict:
    production = root / "docs" / "production"
    data = {name: read_json(production / filename, errors) for name, filename in {
        "profiles": "service-profiles.json", "gates": "gate-contracts.json", "outputs": "output-catalog.json", "nfr": "nfr-targets.json"}.items()}
    data["decisions"] = decision_json(production / "decision-register.md", errors)
    return data


def validate_data(data: dict) -> list[str]:
    errors: list[str] = []
    profile_list = data.get("profiles", {}).get("profiles", [])
    profile_ids = {p.get("id") for p in profile_list if isinstance(p, dict)}
    validate_profiles(data.get("profiles", {}), errors)
    validate_gates(data.get("gates", {}), profile_ids, errors)
    validate_outputs(data.get("outputs", {}), profile_ids, errors)
    validate_nfr(data.get("nfr", {}), errors)
    validate_decisions(data.get("decisions", {}), errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--negative-fixture", action="store_true", help="verify that G8 -> G10 is rejected")
    args = parser.parse_args()
    errors: list[str] = []
    data = load_contracts(args.root.resolve(), errors)
    errors.extend(validate_data(data))
    if args.negative_fixture:
        fixture = copy.deepcopy(data)
        for gate in fixture.get("gates", {}).get("gates", []):
            if gate.get("id") == "G8":
                gate["prerequisites"]["ACCOUNTING_ONLY"] = ["G10"]
        fixture_errors = validate_data(fixture)
        if not any("G8" in error and "G10" in error for error in fixture_errors):
            errors.append("negative fixture: validator did not reject G8 depending on G10")
    if errors:
        print("CONTRACT CHECK: FAIL")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("CONTRACT CHECK: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
