from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.p0 import microsoft_probe


ALLOWED_SITE = "easyguide.sharepoint.com,11111111-1111-4111-8111-111111111111,22222222-2222-4222-8222-222222222222"
UNRELATED_SITE = "easyguide.sharepoint.com,33333333-3333-4333-8333-333333333333,44444444-4444-4444-8444-444444444444"
TOKEN = "test-access-token-never-output"
PRIVATE_CONFIG = {
    "schema": "steauditsphereops/p0-microsoft-live@1",
    "environment": "NONPRODUCTION",
    "tenant_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    "auth_mode": "application",
    "permission_names": ["Sites.Selected"],
    "unrelated_site_exists_verified": True,
    "site_bindings": {"allowed": ALLOWED_SITE, "unrelated": UNRELATED_SITE},
}


def valid_config() -> microsoft_probe.ProbeConfig:
    return microsoft_probe.ProbeConfig(
        tenant_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        auth_mode="application",
        permission_names=("Sites.Selected",),
        allowed_site_id=ALLOWED_SITE,
        unrelated_site_id=UNRELATED_SITE,
    )


class MicrosoftProbeTests(unittest.TestCase):
    def test_missing_private_bindings_fail_closed_without_provider_call(self) -> None:
        with patch.object(microsoft_probe, "load_local_config", side_effect=microsoft_probe.ConfigError("missing")):
            result = microsoft_probe.run_probe(token=TOKEN)

        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("P0-04", result["outcome"])
        self.assertIn("provider-call:none", result["trace"])

    def test_missing_bindings_consume_an_injected_token_before_blocking(self) -> None:
        with patch.dict(os.environ, {microsoft_probe.TOKEN_ENV: TOKEN}):
            with patch.object(microsoft_probe, "load_local_config", side_effect=microsoft_probe.ConfigError("missing")):
                result = microsoft_probe.run_probe()
            self.assertNotIn(microsoft_probe.TOKEN_ENV, os.environ)

        self.assertEqual(result["status"], "BLOCKED")
        self.assertNotIn(TOKEN, json.dumps(result, sort_keys=True))

    def test_missing_token_fails_closed_without_provider_call(self) -> None:
        calls: list[object] = []
        result = microsoft_probe.run_probe(config=valid_config(), token="", transport=lambda *args: calls.append(args))

        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(calls, [])
        self.assertIn("provider-call:none", result["trace"])

    def test_environment_token_is_consumed_and_never_returned(self) -> None:
        outcomes = [(200, json.dumps({"id": ALLOWED_SITE}).encode(), None), (403, b"", None)]
        calls = 0

        def transport(request, _timeout: float, _read_body: bool):
            nonlocal calls
            self.assertEqual(request.headers["Authorization"], f"Bearer {TOKEN}")
            result = outcomes[calls]
            calls += 1
            return result

        with patch.dict(os.environ, {microsoft_probe.TOKEN_ENV: TOKEN}):
            result = microsoft_probe.run_probe(config=valid_config(), transport=transport)
            self.assertNotIn(microsoft_probe.TOKEN_ENV, os.environ)

        self.assertEqual(result["status"], "LIVE_PASS")
        self.assertNotIn(TOKEN, json.dumps(result, sort_keys=True))

    def test_selected_site_read_and_unrelated_site_denial(self) -> None:
        calls: list[tuple[str, str, bool]] = []
        outcomes = [(200, json.dumps({"id": ALLOWED_SITE, "displayName": "Client X"}).encode(), None), (403, b"private body", None)]

        def transport(request, timeout: float, read_body: bool):
            calls.append((request.full_url, request.get_method(), read_body))
            self.assertEqual(request.headers["Authorization"], f"Bearer {TOKEN}")
            self.assertEqual(request.get_header("Accept"), "application/json")
            return outcomes[len(calls) - 1]

        result = microsoft_probe.run_probe(config=valid_config(), token=TOKEN, transport=transport)
        serialized = json.dumps(result, sort_keys=True)

        self.assertEqual(result["status"], "LIVE_PASS")
        self.assertEqual(result["api_version"], "v1.0")
        self.assertEqual(result["auth_context"]["mode"], "application")
        self.assertEqual(result["authorized_site_metadata"], "READABLE")
        self.assertEqual(result["unrelated_site_metadata"], "DENIED")
        self.assertEqual(result["unrelated_http_status"], 403)
        self.assertEqual([call[2] for call in calls], [True, False])
        self.assertTrue(all(call[0].startswith("https://graph.microsoft.com/v1.0/sites/") for call in calls))
        self.assertTrue(all(call[1] == "GET" for call in calls))
        self.assertNotIn(TOKEN, serialized)
        self.assertNotIn(ALLOWED_SITE, serialized)
        self.assertNotIn(UNRELATED_SITE, serialized)
        self.assertNotIn("Client X", serialized)

    def test_unrelated_success_fails_without_reading_its_body(self) -> None:
        calls: list[bool] = []
        outcomes = [(200, json.dumps({"id": ALLOWED_SITE}).encode(), None), (200, b"must not be captured", None)]

        def transport(_request, _timeout: float, read_body: bool):
            calls.append(read_body)
            return outcomes[len(calls) - 1]

        result = microsoft_probe.run_probe(config=valid_config(), token=TOKEN, transport=transport)

        self.assertEqual(result["status"], "FAIL")
        self.assertIn("broader than expected", result["outcome"])
        self.assertEqual(calls, [True, False])

    def test_verified_unrelated_site_404_is_a_denial_observation(self) -> None:
        outcomes = [(200, json.dumps({"id": ALLOWED_SITE}).encode(), None), (404, b"", None)]
        calls = 0

        def transport(_request, _timeout: float, _read_body: bool):
            nonlocal calls
            result = outcomes[calls]
            calls += 1
            return result

        result = microsoft_probe.run_probe(config=valid_config(), token=TOKEN, transport=transport)

        self.assertEqual(result["status"], "LIVE_PASS")
        self.assertEqual(result["unrelated_http_status"], 404)

    def test_network_failure_is_blocked_not_passed(self) -> None:
        result = microsoft_probe.run_probe(
            config=valid_config(),
            token=TOKEN,
            transport=lambda *_args: (None, b"", "TimeoutError"),
        )

        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("unknown", result["outcome"])

    def test_private_config_rejects_production_and_cross_host_targets(self) -> None:
        self.assertEqual(microsoft_probe.parse_config(PRIVATE_CONFIG).allowed_site_id, ALLOWED_SITE)

        value = dict(PRIVATE_CONFIG)
        value["environment"] = "PRODUCTION"
        with self.assertRaises(microsoft_probe.ConfigError):
            microsoft_probe.parse_config(value)

        value["environment"] = "NONPRODUCTION"
        value["site_bindings"] = {"allowed": ALLOWED_SITE, "unrelated": UNRELATED_SITE.replace("easyguide.sharepoint.com", "other.sharepoint.com")}
        with self.assertRaises(microsoft_probe.ConfigError):
            microsoft_probe.parse_config(value)

    def test_unverified_unrelated_site_cannot_turn_a_404_into_expected_denial(self) -> None:
        value = dict(PRIVATE_CONFIG)
        value["unrelated_site_exists_verified"] = False
        with self.assertRaises(microsoft_probe.ConfigError):
            microsoft_probe.parse_config(value)

    def test_malformed_auth_context_fails_closed(self) -> None:
        value = dict(PRIVATE_CONFIG)
        value["auth_mode"] = ["application"]
        with self.assertRaises(microsoft_probe.ConfigError):
            microsoft_probe.parse_config(value)

        value = dict(PRIVATE_CONFIG)
        value["permission_names"] = ["Bearer test-secret"]
        with self.assertRaises(microsoft_probe.ConfigError):
            microsoft_probe.parse_config(value)

    def test_local_loader_rejects_config_outside_ignored_local_root(self) -> None:
        outside = Path(__file__).resolve()
        with self.assertRaises(microsoft_probe.ConfigError):
            microsoft_probe.load_local_config(outside)

    def test_private_fixture_path_is_ignored_by_git(self) -> None:
        root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            ["git", "check-ignore", "--quiet", "--no-index", "--", ".local/p0/microsoft-live.json"],
            cwd=root,
            check=False,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0)

    def test_capability_matrix_matches_bounded_live_observations(self) -> None:
        root = Path(__file__).resolve().parents[2]
        matrix = json.loads((root / "docs/production/microsoft-capabilities.json").read_text("utf-8"))
        operations = matrix["operations"]
        ids = [operation["id"] for operation in operations]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            set(ids),
            {
                "GRAPH-METADATA-READ",
                "GRAPH-METADATA-UPDATE",
                "GRAPH-UPLOAD",
                "GRAPH-SAVED-VERSION",
                "GRAPH-DELTA",
                "GRAPH-SNAPSHOT-READBACK",
                "GRAPH-UNRELATED-DENY",
                "GRAPH-RENAME-MOVE",
                "GRAPH-VERSION-PRUNE",
                "PURVIEW-RECORD-PROFILE",
            },
        )
        self.assertEqual(
            {operation["classification"] for operation in operations},
            {"SUPPORTED_IF_AUTHORIZED", "DENIED_EXPECTED", "UNSUPPORTED_AS_PROOF"},
        )
        expected_statuses = {
            "GRAPH-METADATA-READ": "OBSERVED_SUPPORTED",
            "GRAPH-METADATA-UPDATE": "NOT_RUN_EXTERNAL_PREREQUISITE",
            "GRAPH-UPLOAD": "OBSERVED_SUPPORTED",
            "GRAPH-SAVED-VERSION": "OBSERVED_SUPPORTED",
            "GRAPH-DELTA": "NOT_RUN_EXTERNAL_PREREQUISITE",
            "GRAPH-SNAPSHOT-READBACK": "OBSERVED_SUPPORTED",
            "GRAPH-UNRELATED-DENY": "OBSERVED_DENIED",
            "GRAPH-RENAME-MOVE": "NOT_RUN_EXTERNAL_PREREQUISITE",
            "GRAPH-VERSION-PRUNE": "NOT_RUN_EXTERNAL_PREREQUISITE",
            "PURVIEW-RECORD-PROFILE": "NOT_RUN_EXTERNAL_PREREQUISITE",
        }
        self.assertEqual(
            {operation["id"]: operation["status"] for operation in operations},
            expected_statuses,
        )
        for operation in operations:
            with self.subTest(operation=operation["id"]):
                status = operation["status"]
                outcome = operation["observed_outcome"]
                self.assertIsInstance(operation["scope_disposition"], str)
                self.assertTrue(operation["scope_disposition"])
                if status in {"OBSERVED_SUPPORTED", "OBSERVED_DENIED"}:
                    self.assertIsInstance(outcome, str)
                    self.assertIn("2026-09-18", outcome)
                    self.assertIn(".local/p0-evidence/", outcome)
                    self.assertNotIn("BLOCKED_PENDING_", operation["scope_disposition"])
                elif operation["id"] == "PURVIEW-RECORD-PROFILE":
                    self.assertIsInstance(outcome, str)
                    self.assertIn("canceled before save", outcome)
                    self.assertIn("REVIEWER", operation["scope_disposition"])
                else:
                    self.assertIsNone(outcome)
                    self.assertTrue(operation["scope_disposition"].startswith("BLOCKED_PENDING_"))
        contract = matrix["integration_contract"]
        self.assertEqual(contract["status"], "IMPLEMENTED_WITH_LIMITED_LIVE_OBSERVATIONS")
        self.assertEqual(contract["p0_proof_runner"]["status"], "IMPLEMENTED_AND_LIVE_RUN")
        self.assertEqual(contract["p0_document_runner"]["status"], "IMPLEMENTED_AND_LIVE_RUN")


if __name__ == "__main__":
    unittest.main()
