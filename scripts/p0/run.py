#!/usr/bin/env python3
"""Run the explicit, bounded P0 suite registry."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
P0_BY_SUITE = {
    "build": ["P0-01"],
    "identity": ["P0-02"],
    "isolation": ["P0-03"],
    "microsoft": ["P0-04"],
    "documents": ["P0-05", "P0-09"],
    "transactions": ["P0-06"],
    "accounting": ["P0-07"],
    "privileged": ["P0-08"],
    "recovery": ["P0-10", "P0-11"],
    "human": ["P0-12"],
}
SUITES = set(P0_BY_SUITE)
LIVE_PREREQUISITES = {
    "isolation": "P0-03 requires pre-authorized cross-client and revocation fixtures plus a live SharePoint executor; no tenant request was issued.",
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


def live(suite: str) -> tuple[str, str, list[str], dict[str, object] | None]:
    trace = [f"registry:{suite}", f"manifest:{manifest_digest()}"]
    if suite == "identity":
        probe_path = ROOT / "scripts/p0/identity_probe.py"
        spec = importlib.util.spec_from_file_location("p0_identity_probe", probe_path)
        if spec is None or spec.loader is None:
            return "FAIL", "P0-02 identity probe module could not be loaded.", trace + ["executor-load:failed"], None
        probe = importlib.util.module_from_spec(spec)
        try:
            sys.modules[spec.name] = probe
            spec.loader.exec_module(probe)
            result = probe.run_probe()
        except Exception as error:
            return (
                "FAIL",
                "P0-02 identity probe raised an internal error; details are withheld from evidence.",
                trace + [f"executor-error:{type(error).__name__}"],
                None,
            )
        if not isinstance(result, dict):
            return "FAIL", "P0-02 identity probe returned an invalid result.", trace + ["executor-result:invalid"], None
        status = result.get("status")
        outcome = result.get("outcome")
        probe_trace = result.get("trace", [])
        subject_status = result.get("entra_subject_mapping_status")
        external_status_fields = (
            "frappe_authorization_status",
            "email_change_reuse_status",
            "disabled_revoked_status",
            "wrong_tenant_status",
            "sharepoint_user_access_status",
        )
        if (
            not isinstance(status, str)
            or status not in {"BLOCKED", "FAIL"}
            or not isinstance(outcome, str)
            or not isinstance(probe_trace, list)
            or any(not isinstance(item, str) for item in probe_trace)
            or not probe_trace
            or probe_trace[0] != "executor:entra-identity-read-only-v1"
            or any(
                item != "provider-call:none"
                and item not in {f"provider-call:entra-me:{key}" for key in ("staff", "client_x", "client_y")}
                for item in probe_trace[1:]
            )
            or not isinstance(subject_status, str)
            or subject_status not in {"BLOCKED", "LIVE_PASS", "FAIL"}
            or (status == "FAIL") != (subject_status == "FAIL")
            or any(result.get(field) != "NOT_RUN_EXTERNAL_PREREQUISITE" for field in external_status_fields)
        ):
            return "FAIL", "P0-02 identity probe returned an invalid or unsupported result.", trace + ["executor-result:invalid"], None
        fixture_results = result.get("entra_fixture_results", {})
        http_statuses = result.get("entra_http_statuses", {})
        if (
            not isinstance(fixture_results, dict)
            or set(fixture_results) - {"staff", "client_x", "client_y"}
            or any(value != "MATCH" for value in fixture_results.values())
            or not isinstance(http_statuses, dict)
            or set(http_statuses) - {"staff", "client_x", "client_y"}
            or any(type(value) is not int or value < 0 or value > 599 for value in http_statuses.values())
            or (subject_status == "LIVE_PASS" and fixture_results != {key: "MATCH" for key in ("staff", "client_x", "client_y")})
            or (subject_status == "LIVE_PASS" and http_statuses != {key: 200 for key in ("staff", "client_x", "client_y")})
            or (subject_status != "LIVE_PASS" and bool(fixture_results))
        ):
            return "FAIL", "P0-02 identity probe returned invalid fixture observations.", trace + ["executor-result:invalid"], None
        safe_outcome = (
            "P0-02 Entra /me subject mapping matched all configured member fixtures; remaining identity checks are not run."
            if subject_status == "LIVE_PASS"
            else "P0-02 Entra subject mapping is blocked or failed; inspect private fixture/provider details without broadening consent."
        )
        observation = {
            "entra_subject_mapping_status": subject_status,
            **{field: "NOT_RUN_EXTERNAL_PREREQUISITE" for field in external_status_fields},
        }
        if fixture_results:
            observation["entra_fixture_results"] = fixture_results
        if http_statuses:
            observation["entra_http_statuses"] = http_statuses
        # Entra subject matching is a partial P0-02 subproof; WBS-05 needs
        # Frappe authorization and the remaining identity/isolation cases too.
        return status, safe_outcome, trace + probe_trace, observation
    if suite == "isolation":
        probe_path = ROOT / "scripts/p0/isolation_probe.py"
        spec = importlib.util.spec_from_file_location("p0_isolation_probe", probe_path)
        if spec is None or spec.loader is None:
            return "FAIL", "P0-03 isolation probe module could not be loaded.", trace + ["executor-load:failed"], None
        probe = importlib.util.module_from_spec(spec)
        try:
            sys.modules[spec.name] = probe
            spec.loader.exec_module(probe)
            result = probe.run_probe()
        except Exception as error:
            return (
                "FAIL",
                "P0-03 isolation probe raised an internal error; details are withheld from evidence.",
                trace + [f"executor-error:{type(error).__name__}"],
                None,
            )
        if not isinstance(result, dict):
            return "FAIL", "P0-03 isolation probe returned an invalid result.", trace + ["executor-result:invalid"], None
        status = result.get("status")
        outcome = result.get("outcome")
        probe_trace = result.get("trace", [])
        sharepoint_status = result.get("sharepoint_isolation_status")
        identity_status = result.get("identity_context_status", "NOT_RUN_EXTERNAL_PREREQUISITE")
        frappe_status = result.get("frappe_authorization_status")
        revocation_status = result.get("revocation_status")
        allowed_trace = {
            "executor:sharepoint-isolation-read-only-v1",
            "provider-call:none",
        }
        operation_trace = {
            f"provider-call:{fixture}:{site}:{operation}"
            for fixture in ("staff", "client_x", "client_y")
            for site in ("client_x", "client_y", "unrelated")
            for operation in ("site-metadata", "item-metadata", "content", "search")
        }
        safe_keys = {
            "api_version",
            "auth_context",
            "tenant_id_configured",
            "tenant_verification",
            "identity_context_status",
            "sharepoint_isolation_status",
            "frappe_authorization_status",
            "revocation_status",
        }
        if (
            status not in {"BLOCKED", "FAIL"}
            or not isinstance(outcome, str)
            or not outcome.startswith("P0-03")
            or not isinstance(probe_trace, list)
            or any(not isinstance(item, str) or item not in allowed_trace | operation_trace for item in probe_trace)
            or not probe_trace
            or probe_trace[0] != "executor:sharepoint-isolation-read-only-v1"
            or sharepoint_status not in {"BLOCKED", "LIVE_PASS", "FAIL"}
            or identity_status not in {"NOT_RUN_EXTERNAL_PREREQUISITE", "LIVE_PASS", "BLOCKED"}
            or frappe_status != "NOT_RUN_EXTERNAL_PREREQUISITE"
            or revocation_status != "NOT_RUN_EXTERNAL_PREREQUISITE"
            or set(result) - {"status", "outcome", "trace"} - safe_keys
            or (status == "FAIL") != (sharepoint_status == "FAIL")
            or (sharepoint_status == "LIVE_PASS" and status != "BLOCKED")
        ):
            return "FAIL", "P0-03 isolation probe returned an invalid or unsupported result.", trace + ["executor-result:invalid"], None
        # A missing private fixture is a valid fail-closed preflight outcome;
        # it has no tenant metadata to expose and must not be upgraded to a
        # provider observation.
        if (
            status == "BLOCKED"
            and sharepoint_status == "BLOCKED"
            and probe_trace == ["executor:sharepoint-isolation-read-only-v1", "provider-call:none"]
            and not (set(result) - {"status", "outcome", "trace", "sharepoint_isolation_status", "frappe_authorization_status", "revocation_status"})
        ):
            return status, outcome, trace + probe_trace, None
        if result.get("api_version") != "v1.0" or result.get("tenant_id_configured") is not True or result.get("tenant_verification") != "NOT_PROVEN_BY_THIS_PROBE":
            return "FAIL", "P0-03 isolation probe returned invalid tenant metadata.", trace + ["executor-result:invalid"], None
        auth_context = result.get("auth_context")
        if (
            not isinstance(auth_context, dict)
            or set(auth_context) != {"mode", "permission_names", "source"}
            or auth_context.get("mode") not in {"application", "delegated"}
            or auth_context.get("permission_names") != ["Sites.Selected"]
            or auth_context.get("source") != "private local fixture metadata; requires owner evidence review"
        ):
            return "FAIL", "P0-03 isolation probe returned invalid authorization metadata.", trace + ["executor-result:invalid"], None
        observation = {key: result[key] for key in safe_keys if key in result}
        return status, outcome, trace + probe_trace, observation
    if suite == "microsoft":
        probe_path = ROOT / "scripts/p0/microsoft_probe.py"
        spec = importlib.util.spec_from_file_location("p0_microsoft_probe", probe_path)
        if spec is None or spec.loader is None:
            return "FAIL", "P0-04 Graph probe module could not be loaded.", trace + ["executor-load:failed"], None
        probe = importlib.util.module_from_spec(spec)
        try:
            sys.modules[spec.name] = probe
            spec.loader.exec_module(probe)
            result = probe.run_probe()
        except Exception as error:
            return (
                "FAIL",
                "P0-04 Graph probe raised an internal error; details are withheld from evidence.",
                trace + [f"executor-error:{type(error).__name__}"],
                None,
            )
        status = result.get("status")
        if status not in {"LIVE_PASS", "BLOCKED", "FAIL"}:
            return "FAIL", "P0-04 Graph probe returned an invalid status.", trace + ["executor-result:invalid"], None
        outcome = result.get("outcome")
        if not isinstance(outcome, str):
            return "FAIL", "P0-04 Graph probe returned no outcome.", trace + ["executor-result:invalid"], None
        probe_trace = result.get("trace", [])
        if not isinstance(probe_trace, list) or any(not isinstance(item, str) for item in probe_trace):
            return "FAIL", "P0-04 Graph probe returned an invalid trace.", trace + ["executor-result:invalid"], None
        observation = {key: value for key, value in result.items() if key not in {"status", "outcome", "trace"}}
        return status, outcome, trace + probe_trace, observation
    if suite == "documents":
        probe_path = ROOT / "scripts/p0/documents_probe.py"
        spec = importlib.util.spec_from_file_location("p0_documents_probe", probe_path)
        if spec is None or spec.loader is None:
            return "FAIL", "P0-05 SharePoint document probe module could not be loaded.", trace + ["executor-load:failed"], None
        probe = importlib.util.module_from_spec(spec)
        try:
            sys.modules[spec.name] = probe
            spec.loader.exec_module(probe)
            result = probe.run_probe()
        except Exception as error:
            return (
                "FAIL",
                "P0-05 SharePoint document probe raised an internal error; details are withheld from evidence.",
                trace + [f"executor-error:{type(error).__name__}"],
                None,
            )
        status = result.get("status")
        outcome = result.get("outcome")
        probe_trace = result.get("trace", [])
        p0_05_status = result.get("p0_05_status")
        p0_09_status = result.get("p0_09_status")
        delta_status = result.get("delta_reconciliation_status")
        safe_result_fields = {
            "api_version",
            "auth_context",
            "tenant_id_configured",
            "tenant_verification",
            "target_ids",
            "p0_05_status",
            "p0_09_status",
            "metadata_update_status",
            "delta_reconciliation_status",
            "p0_05_observation",
            "current_sha256",
            "snapshot_sha256",
        }
        safe_observation_fields = {
            "auth_mode",
            "permission_names",
            "tenant_id_configured",
            "tenant_verification",
            "target_ids",
            "client_b_site_metadata",
            "unrelated_site_metadata",
            "original_sha256",
            "updated_sha256",
            "snapshot_sha256",
            "current_sha256",
            "original_size",
            "updated_size",
            "current_size",
            "version_id",
            "drive_item_id",
            "file_name",
            "metadata_update_status",
            "delta_reconciliation_status",
        }
        p0_05_observation = result.get("p0_05_observation")
        if (
            status not in {"BLOCKED", "FAIL"}
            or not isinstance(outcome, str)
            or not isinstance(probe_trace, list)
            or any(not isinstance(item, str) for item in probe_trace)
            or any("://" in item or "token=" in item.casefold() for item in probe_trace)
            or p0_05_status not in {"BLOCKED", "LIVE_PASS", "FAIL"}
            or p0_09_status != "NOT_RUN_EXTERNAL_PREREQUISITE"
            or result.get("metadata_update_status") not in {
                "NOT_RUN_EXTERNAL_PREREQUISITE",
                "BLOCKED",
                "LIVE_PASS",
                "FAIL",
            }
            or delta_status not in {"NOT_RUN_EXTERNAL_PREREQUISITE", "BLOCKED", "LIVE_PASS", "FAIL"}
            or set(result) - {"status", "outcome", "trace"} - safe_result_fields
            or (p0_05_status == "LIVE_PASS")
            != (
                delta_status == "LIVE_PASS"
                and result.get("metadata_update_status") == "LIVE_PASS"
            )
            or (result.get("metadata_update_status") == "FAIL" and p0_05_status != "FAIL")
            or (delta_status == "FAIL" and p0_05_status != "FAIL")
            or (
                p0_05_observation is not None
                and (
                    not isinstance(p0_05_observation, dict)
                    or set(p0_05_observation) != safe_observation_fields
                    or p0_05_observation.get("metadata_update_status") != result.get("metadata_update_status")
                    or p0_05_observation.get("delta_reconciliation_status") != delta_status
                )
            )
        ):
            return "FAIL", "P0-05/P0-09 probe returned an invalid or unsupported result.", trace + ["executor-result:invalid"], None
        if (status == "FAIL") != (p0_05_status == "FAIL"):
            return "FAIL", "P0-05 probe status was inconsistent with the suite result.", trace + ["executor-result:inconsistent"], None
        observation = {
            key: value
            for key, value in result.items()
            if key in safe_result_fields
        }
        # P0-09 is independently required, so P0-05 cannot pass the suite alone.
        return status, f"P0-05/P0-09: {outcome}", trace + probe_trace, observation
    if suite in LIVE_PREREQUISITES:
        trace.extend((f"live-dispatch:{suite}:blocked-no-executor", "provider-call:none"))
        return "BLOCKED", LIVE_PREREQUISITES[suite], trace, None
    if suite != "build":
        return "BLOCKED", "This suite is owned by WBS-05/06/07 and no future service is called by WBS-04.", trace, None
    env = os.environ.copy()
    provision = subprocess.run([sys.executable, str(ROOT / "scripts/p0/provision_local.py"), "--live"], cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    trace.append(f"provision:returncode={provision.returncode}")
    try:
        outcome = json.loads(provision.stdout.decode(errors="replace"))
    except json.JSONDecodeError:
        return "FAIL", "provisioner returned non-JSON output", trace
    status = outcome.get("status")
    if status == "PASS":
        return "LIVE_PASS", str(outcome.get("reason")), trace, None
    if status == "BLOCKED":
        return "BLOCKED", str(outcome.get("reason")), trace, None
    return "FAIL", str(outcome.get("reason")), trace, None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=sorted(SUITES), required=True)
    parser.add_argument("--mode", choices=("mock", "live"), required=True)
    args = parser.parse_args()
    provider_observation = None
    if args.mode == "mock":
        status, outcome, trace = mock(args.suite)
    else:
        status, outcome, trace, provider_observation = live(args.suite)
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
    if provider_observation:
        evidence["provider_observation"] = provider_observation
    evidence_dir = ROOT / ".local/p0-evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / f"{args.suite}-{args.mode}-{time.time_ns()}.json"
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    evidence["evidence_path"] = evidence_path.relative_to(ROOT).as_posix()
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0 if status in {"MOCK_PASS", "LIVE_PASS"} else (2 if status == "BLOCKED" else 1)


if __name__ == "__main__":
    sys.exit(main())
