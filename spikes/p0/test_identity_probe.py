from __future__ import annotations

import base64
import importlib.machinery
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from unittest.mock import patch

from scripts.p0 import identity_probe, run as p0_run


TENANT_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
CLIENT_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
OTHER_TENANT_ID = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
FIXTURE_VALUES = {
    "staff": {
        "object_id": "11111111-1111-4111-8111-111111111111",
        "user_principal_name": "staff@example.invalid",
    },
    "client_x": {
        "object_id": "22222222-2222-4222-8222-222222222222",
        "user_principal_name": "client-x@example.invalid",
    },
    "client_y": {
        "object_id": "33333333-3333-4333-8333-333333333333",
        "user_principal_name": "client-y@example.invalid",
    },
}


def private_config() -> dict[str, object]:
    return {
        "schema": "steauditsphereops/p0-identity-live@1",
        "environment": "NONPRODUCTION",
        "tenant_id": TENANT_ID,
        "client_id": CLIENT_ID,
        "auth_mode": "delegated",
        "permission_names": ["User.Read"],
        "fixtures": FIXTURE_VALUES,
    }


def valid_config() -> identity_probe.ProbeConfig:
    return identity_probe.parse_config(private_config())


def make_token(fixture_key: str, **overrides: object) -> str:
    fixture = FIXTURE_VALUES[fixture_key]
    claims: dict[str, object] = {
        "tid": TENANT_ID,
        "oid": fixture["object_id"],
        "aud": identity_probe.GRAPH_RESOURCE_ID,
        "azp": CLIENT_ID,
        "iss": f"https://login.microsoftonline.com/{TENANT_ID}/v2.0",
        "scp": "User.Read",
        "exp": 5000,
        "nbf": 900,
        "idtyp": "user",
    }
    claims.update(overrides)
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
    return f"e30.{payload}.test-signature"


def valid_tokens() -> dict[str, str]:
    return {key: make_token(key) for key in identity_probe.REQUIRED_FIXTURES}


class IdentityProbeTests(unittest.TestCase):
    def test_runner_keeps_partial_identity_observation_blocked_and_whitelists_evidence(self) -> None:
        private_marker = "fixture-user-and-token-must-not-be-copied"
        probe_result = {
            "status": "BLOCKED",
            "outcome": private_marker,
            "trace": [
                "executor:entra-identity-read-only-v1",
                "provider-call:entra-me:staff",
                "provider-call:entra-me:client_x",
                "provider-call:entra-me:client_y",
            ],
            "entra_subject_mapping_status": "LIVE_PASS",
            "frappe_authorization_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
            "email_change_reuse_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
            "disabled_revoked_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
            "wrong_tenant_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
            "sharepoint_user_access_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
            "entra_fixture_results": {key: "MATCH" for key in FIXTURE_VALUES},
            "entra_http_statuses": {key: 200 for key in FIXTURE_VALUES},
            "debug": private_marker,
        }

        class Loader:
            def create_module(self, spec):
                return None

            def exec_module(self, module) -> None:
                module.run_probe = lambda: probe_result

        module_name = "p0_identity_probe_runner_test"
        spec = importlib.machinery.ModuleSpec(module_name, Loader())
        try:
            with patch.object(p0_run.importlib.util, "spec_from_file_location", return_value=spec):
                status, outcome, trace, observation = p0_run.live("identity")
        finally:
            sys.modules.pop(module_name, None)

        self.assertEqual(status, "BLOCKED")
        self.assertNotIn(private_marker, outcome)
        self.assertNotIn(private_marker, json.dumps(observation, sort_keys=True))
        self.assertEqual(observation["entra_subject_mapping_status"], "LIVE_PASS")
        self.assertEqual(observation["frappe_authorization_status"], "NOT_RUN_EXTERNAL_PREREQUISITE")
        self.assertTrue(any(item == "provider-call:entra-me:staff" for item in trace))

        probe_result["status"] = "LIVE_PASS"
        with patch.object(p0_run.importlib.util, "spec_from_file_location", return_value=spec):
            invalid_status, _, _, _ = p0_run.live("identity")
        self.assertEqual(invalid_status, "FAIL")

    def test_missing_config_consumes_all_environment_tokens_without_provider_call(self) -> None:
        environment_tokens = {
            environment_name: make_token(fixture_key)
            for fixture_key, environment_name in identity_probe.TOKEN_ENV.items()
        }
        calls: list[object] = []
        with patch.dict(os.environ, environment_tokens):
            with patch.object(identity_probe, "load_local_config", side_effect=identity_probe.ConfigError("missing")):
                result = identity_probe.run_probe(transport=lambda *args: calls.append(args))
            self.assertTrue(all(name not in os.environ for name in environment_tokens))

        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("provider-call:none", result["trace"])
        self.assertEqual(calls, [])
        self.assertNotIn(json.dumps(environment_tokens), json.dumps(result, sort_keys=True))

    def test_exact_private_config_contract_rejects_wrong_mode_scope_and_fixture_set(self) -> None:
        value = private_config()
        self.assertEqual(identity_probe.parse_config(value).tenant_id, TENANT_ID)

        invalid_cases = [
            dict(value, environment="PRODUCTION"),
            dict(value, auth_mode="application"),
            dict(value, permission_names=["User.Read", "Mail.Read"]),
            dict(value, fixtures={"staff": FIXTURE_VALUES["staff"]}),
        ]
        for invalid in invalid_cases:
            with self.subTest(invalid=invalid):
                with self.assertRaises(identity_probe.ConfigError):
                    identity_probe.parse_config(invalid)

        duplicate = private_config()
        duplicate_fixtures = dict(FIXTURE_VALUES)
        duplicate_fixtures["client_y"] = dict(FIXTURE_VALUES["client_x"])
        duplicate["fixtures"] = duplicate_fixtures
        with self.assertRaises(identity_probe.ConfigError):
            identity_probe.parse_config(duplicate)

    def test_approved_isolation_scope_can_be_carried_by_identity_fixture(self) -> None:
        value = private_config()
        value["permission_names"] = ["User.Read", "Sites.Selected"]
        config = identity_probe.parse_config(value)
        token = make_token("staff", scp="Sites.Selected User.Read openid profile email")
        self.assertTrue(
            identity_probe._token_matches_fixture(
                token, config, config.fixtures[0], now=1000
            )
        )

    def test_missing_fixture_token_fails_before_provider_call(self) -> None:
        calls: list[object] = []
        result = identity_probe.run_probe(
            config=valid_config(),
            tokens={},
            transport=lambda *args: calls.append(args),
            now=1000,
        )

        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("provider-call:none", result["trace"])
        self.assertEqual(calls, [])

    def test_wrong_tenant_client_audience_scope_or_expiry_blocks_before_provider_call(self) -> None:
        invalid_tokens = [
            make_token("staff", tid=OTHER_TENANT_ID),
            make_token("staff", azp="dddddddd-dddd-4ddd-8ddd-dddddddddddd"),
            make_token("staff", aud="https://graph.microsoft.us"),
            make_token("staff", scp="User.Read Mail.Read"),
            make_token("staff", exp=999),
            make_token("staff", roles=["Directory.Read.All"]),
            make_token("staff", idtyp="app"),
        ]
        for token in invalid_tokens:
            with self.subTest(token=token[:24]):
                tokens = valid_tokens()
                tokens["staff"] = token
                calls: list[object] = []
                result = identity_probe.run_probe(
                    config=valid_config(),
                    tokens=tokens,
                    transport=lambda *args: calls.append(args),
                    now=1000,
                )
                self.assertEqual(result["status"], "BLOCKED")
                self.assertIn("provider-call:none", result["trace"])
                self.assertEqual(calls, [])
                self.assertNotIn(token, json.dumps(result, sort_keys=True))

    def test_standard_oidc_scopes_added_by_microsoft_are_allowed(self) -> None:
        tokens = valid_tokens()
        tokens["staff"] = make_token("staff", scp="User.Read openid profile email")
        self.assertTrue(
            identity_probe._token_matches_fixture(
                tokens["staff"], valid_config(), valid_config().fixtures[0], now=1000
            )
        )

        for extra_scope in ("offline_access", "Sites.ReadWrite.All"):
            with self.subTest(extra_scope=extra_scope):
                token = make_token("staff", scp=f"User.Read {extra_scope}")
                self.assertFalse(
                    identity_probe._token_matches_fixture(
                        token, valid_config(), valid_config().fixtures[0], now=1000
                    )
                )

    def test_all_three_graph_me_bindings_are_a_partial_pass_only_and_are_redacted(self) -> None:
        tokens = valid_tokens()
        calls: list[tuple[str, str, str | None]] = []

        def transport(request, timeout: float):
            self.assertEqual(timeout, identity_probe.REQUEST_TIMEOUT_SECONDS)
            calls.append((request.full_url, request.get_method(), request.get_header("Authorization")))
            fixture_key = identity_probe.REQUIRED_FIXTURES[len(calls) - 1]
            fixture = FIXTURE_VALUES[fixture_key]
            return identity_probe.Response(
                200,
                json.dumps(
                    {
                        "id": fixture["object_id"],
                        "userPrincipalName": fixture["user_principal_name"],
                    }
                ).encode(),
            )

        result = identity_probe.run_probe(
            config=valid_config(), tokens=tokens, transport=transport, now=1000
        )
        serialized = json.dumps(result, sort_keys=True)

        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["entra_subject_mapping_status"], "LIVE_PASS")
        self.assertEqual(result["frappe_authorization_status"], "NOT_RUN_EXTERNAL_PREREQUISITE")
        self.assertEqual(result["disabled_revoked_status"], "NOT_RUN_EXTERNAL_PREREQUISITE")
        self.assertEqual(result["entra_fixture_results"], {key: "MATCH" for key in FIXTURE_VALUES})
        self.assertEqual(result["entra_http_statuses"], {key: 200 for key in FIXTURE_VALUES})
        self.assertEqual(len(calls), 3)
        for index, (url, method, authorization) in enumerate(calls):
            self.assertEqual(method, "GET")
            self.assertTrue(url.startswith(f"{identity_probe.GRAPH_BASE}/me?"))
            self.assertEqual(parse_qs(urlsplit(url).query), {"$select": ["id,userPrincipalName"]})
            self.assertEqual(authorization, f"Bearer {tokens[identity_probe.REQUIRED_FIXTURES[index]]}")
        for token in tokens.values():
            self.assertNotIn(token, serialized)
        for fixture in FIXTURE_VALUES.values():
            self.assertNotIn(fixture["object_id"], serialized)
            self.assertNotIn(fixture["user_principal_name"], serialized)

    def test_graph_subject_mismatch_fails_and_stops_after_first_fixture(self) -> None:
        calls = 0

        def transport(_request, _timeout: float):
            nonlocal calls
            calls += 1
            return identity_probe.Response(
                200,
                json.dumps(
                    {
                        "id": "99999999-9999-4999-8999-999999999999",
                        "userPrincipalName": "wrong@example.invalid",
                    }
                ).encode(),
            )

        result = identity_probe.run_probe(
            config=valid_config(), tokens=valid_tokens(), transport=transport, now=1000
        )

        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["entra_subject_mapping_status"], "FAIL")
        self.assertEqual(calls, 1)
        self.assertNotIn("wrong@example.invalid", json.dumps(result, sort_keys=True))

    def test_provider_denial_is_blocked_without_retries_or_consent_expansion(self) -> None:
        calls: list[str] = []

        def transport(request, _timeout: float):
            calls.append(request.full_url)
            return identity_probe.Response(403, b"private provider body")

        result = identity_probe.run_probe(
            config=valid_config(), tokens=valid_tokens(), transport=transport, now=1000
        )

        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(len(calls), 1)
        self.assertNotIn("private provider body", json.dumps(result, sort_keys=True))
        self.assertNotIn("Mail.Read", json.dumps(result, sort_keys=True))

    def test_private_fixture_path_cannot_escape_ignored_local_root(self) -> None:
        with self.assertRaises(identity_probe.ConfigError):
            identity_probe.load_local_config(Path(__file__).resolve())

        root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            ["git", "check-ignore", "--quiet", "--no-index", "--", ".local/p0/identity-live.json"],
            cwd=root,
            check=False,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
