from __future__ import annotations

import base64
import importlib.machinery
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

from scripts.p0 import isolation_probe


TENANT_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
CLIENT_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
SITE_IDS = {
    "client_x": "easyguide.sharepoint.com,11111111-1111-4111-8111-111111111111,22222222-2222-4222-8222-222222222222",
    "client_y": "easyguide.sharepoint.com,33333333-3333-4333-8333-333333333333,44444444-4444-4444-8444-444444444444",
    "unrelated": "easyguide.sharepoint.com,55555555-5555-4555-8555-555555555555,66666666-6666-4666-8666-666666666666",
}
RESOURCES = {
    "client_x": {"drive_id": "drive-x", "item_id": "item-x", "search_term": "p0-isolation-client-x"},
    "client_y": {"drive_id": "drive-y", "item_id": "item-y", "search_term": "p0-isolation-client-y"},
    "unrelated": {"drive_id": "drive-u", "item_id": "item-u", "search_term": "p0-isolation-unrelated"},
}
FIXTURES = {
    "staff": {
        "object_id": "11111111-1111-4111-8111-111111111111",
        "user_principal_name": "staff@example.invalid",
        "allowed_site_keys": ["client_x", "client_y"],
    },
    "client_x": {
        "object_id": "22222222-2222-4222-8222-222222222222",
        "user_principal_name": "client-x@example.invalid",
        "allowed_site_keys": ["client_x"],
    },
    "client_y": {
        "object_id": "33333333-3333-4333-8333-333333333333",
        "user_principal_name": "client-y@example.invalid",
        "allowed_site_keys": ["client_y"],
    },
}
TOKEN_MARKER = "fixture-token-never-output"


def private_config(*, auth_mode: str = "delegated") -> dict[str, object]:
    return {
        "schema": "steauditsphereops/p0-isolation-live@1",
        "environment": "NONPRODUCTION",
        "tenant_id": TENANT_ID,
        "client_id": CLIENT_ID,
        "auth_mode": auth_mode,
        "permission_names": ["Sites.Selected"],
        "site_bindings": {
            key: {"site_id": site_id, "exists_verified": True}
            for key, site_id in SITE_IDS.items()
        },
        "resources": RESOURCES,
        "fixtures": FIXTURES,
    }


def valid_config(*, auth_mode: str = "delegated") -> isolation_probe.ProbeConfig:
    return isolation_probe.parse_config(private_config(auth_mode=auth_mode))


def make_token(fixture_key: str, *, auth_mode: str = "delegated", **overrides: object) -> str:
    claims: dict[str, object] = {
        "tid": TENANT_ID,
        "aud": isolation_probe.GRAPH_RESOURCE_ID,
        "azp": CLIENT_ID,
        "iss": f"https://login.microsoftonline.com/{TENANT_ID}/v2.0",
        "exp": 5000,
        "nbf": 900,
        "idtyp": "user" if auth_mode == "delegated" else "app",
    }
    if auth_mode == "delegated":
        claims.update({"oid": FIXTURES[fixture_key]["object_id"], "scp": "Sites.Selected"})
    else:
        claims["roles"] = ["Sites.Selected"]
    claims.update(overrides)
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
    return f"e30.{payload}.test-signature"


def valid_tokens(*, auth_mode: str = "delegated") -> dict[str, str]:
    return {
        key: make_token(key, auth_mode=auth_mode)
        for key in isolation_probe.REQUIRED_FIXTURES
    }


def _site_key_from_id(site_id: str) -> str:
    return next(key for key, value in SITE_IDS.items() if value == site_id)


def boundary_transport(request, _timeout: float, read_body: bool):
    config = valid_config()
    fixture_key = next(
        key for key, token_name in isolation_probe.TOKEN_ENV.items()
        if request.headers["Authorization"] == f"Bearer {make_token(key)}"
    )
    path = unquote(urlsplit(request.full_url).path)
    if "/sites/" in path:
        site_id = path.split("/sites/", 1)[1]
        site_key = _site_key_from_id(site_id)
        if site_key in next(item.allowed_site_keys for item in config.fixtures if item.key == fixture_key):
            return isolation_probe.Response(200, json.dumps({"id": site_id}).encode())
        return isolation_probe.Response(403)
    if path.endswith("/content"):
        drive_id = path.split("/drives/", 1)[1].split("/items/", 1)[0]
        resource_key = next(key for key, resource in RESOURCES.items() if resource["drive_id"] == drive_id)
        allowed = resource_key in next(item.allowed_site_keys for item in config.fixtures if item.key == fixture_key)
        return isolation_probe.Response(200 if allowed else 403, b"" if not read_body else b"unexpected")
    if "/drives/" in path:
        drive_id = path.split("/drives/", 1)[1].split("/items/", 1)[0]
        item_id = path.split("/items/", 1)[1]
        resource_key = next(key for key, resource in RESOURCES.items() if resource["drive_id"] == drive_id)
        allowed = resource_key in next(item.allowed_site_keys for item in config.fixtures if item.key == fixture_key)
        if allowed:
            return isolation_probe.Response(200, json.dumps({"id": item_id}).encode())
        return isolation_probe.Response(403)
    if path.endswith("/search/query"):
        payload = json.loads(request.data.decode())
        search_term = payload["requests"][0]["query"]["queryString"]
        resource_key = next(key for key, resource in RESOURCES.items() if resource["search_term"] == search_term)
        allowed = resource_key in next(item.allowed_site_keys for item in config.fixtures if item.key == fixture_key)
        body = {"value": []}
        if allowed:
            body = {"value": [{"hitsContainers": [{"hits": [{"resource": {"id": RESOURCES[resource_key]["item_id"]}}]}]}]}
        return isolation_probe.Response(200, json.dumps(body).encode())
    raise AssertionError(f"unexpected request path: {path}")


class IsolationProbeTests(unittest.TestCase):
    def test_exact_contract_rejects_broad_permission_and_wrong_boundary(self) -> None:
        self.assertEqual(valid_config().permission_names, ("Sites.Selected",))
        invalid_permission = private_config()
        invalid_permission["permission_names"] = ["Sites.Read.All"]
        with self.assertRaises(isolation_probe.ConfigError):
            isolation_probe.parse_config(invalid_permission)

        invalid_fixture = private_config()
        invalid_fixture["fixtures"] = dict(FIXTURES)
        invalid_fixture["fixtures"]["client_x"] = dict(FIXTURES["client_x"])
        invalid_fixture["fixtures"]["client_x"]["allowed_site_keys"] = ["client_y"]
        with self.assertRaises(isolation_probe.ConfigError):
            isolation_probe.parse_config(invalid_fixture)

    def test_missing_config_consumes_all_tokens_without_provider_call(self) -> None:
        calls: list[object] = []
        environment_tokens = {
            environment_name: make_token(fixture_key)
            for fixture_key, environment_name in isolation_probe.TOKEN_ENV.items()
        }
        with patch.dict(os.environ, environment_tokens):
            with patch.object(isolation_probe, "load_local_config", side_effect=isolation_probe.ConfigError("missing")):
                result = isolation_probe.run_probe(transport=lambda *args: calls.append(args))
            self.assertTrue(all(name not in os.environ for name in environment_tokens))
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(calls, [])
        serialized = json.dumps(result, sort_keys=True)
        self.assertNotIn(TOKEN_MARKER, serialized)

    def test_missing_or_invalid_token_blocks_before_provider_call(self) -> None:
        calls: list[object] = []
        result = isolation_probe.run_probe(
            config=valid_config(),
            tokens={"staff": make_token("staff")},
            transport=lambda *args: calls.append(args),
        )
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(calls, [])
        invalid_tokens = valid_tokens()
        invalid_tokens["client_x"] = make_token("client_x", tid="dddddddd-dddd-4ddd-8ddd-dddddddddddd")
        result = isolation_probe.run_probe(
            config=valid_config(),
            tokens=invalid_tokens,
            transport=lambda *args: calls.append(args),
            now=1000,
        )
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(calls, [])

    def test_all_read_only_boundaries_pass_but_aggregate_remains_blocked(self) -> None:
        result = isolation_probe.run_probe(
            config=valid_config(),
            tokens=valid_tokens(),
            transport=boundary_transport,
            now=1000,
        )
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["sharepoint_isolation_status"], "LIVE_PASS")
        self.assertEqual(result["identity_context_status"], "LIVE_PASS")
        self.assertEqual(result["frappe_authorization_status"], "NOT_RUN_EXTERNAL_PREREQUISITE")
        self.assertEqual(result["revocation_status"], "NOT_RUN_EXTERNAL_PREREQUISITE")
        serialized = json.dumps(result, sort_keys=True)
        for token in valid_tokens().values():
            self.assertNotIn(token, serialized)
        for private_value in [TENANT_ID, CLIENT_ID, *SITE_IDS.values(), *(item["item_id"] for item in RESOURCES.values())]:
            self.assertNotIn(private_value, serialized)

    def test_unauthorized_site_success_is_a_fail_closed_failure(self) -> None:
        def leaked_site(request, _timeout: float, _read_body: bool):
            path = unquote(urlsplit(request.full_url).path)
            if "/sites/" in path:
                site_id = path.split("/sites/", 1)[1]
                site_key = _site_key_from_id(site_id)
                fixture_key = next(
                    key for key in isolation_probe.REQUIRED_FIXTURES
                    if request.headers["Authorization"] == f"Bearer {make_token(key)}"
                )
                allowed = site_key in next(item["allowed_site_keys"] for key, item in FIXTURES.items() if key == fixture_key)
                if not allowed:
                    return isolation_probe.Response(200, json.dumps({"id": site_id}).encode())
            return boundary_transport(request, _timeout, _read_body)

        result = isolation_probe.run_probe(
            config=valid_config(),
            tokens=valid_tokens(),
            transport=leaked_site,
            now=1000,
        )
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["sharepoint_isolation_status"], "FAIL")
        self.assertIn("broader than expected", result["outcome"])

    def test_unknown_provider_result_is_blocked(self) -> None:
        result = isolation_probe.run_probe(
            config=valid_config(),
            tokens=valid_tokens(),
            transport=lambda *_args: isolation_probe.Response(503),
            now=1000,
        )
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["sharepoint_isolation_status"], "BLOCKED")
        self.assertNotIn("503", result["outcome"])

    def test_runner_whitelists_only_safe_observations(self) -> None:
        from scripts.p0 import run as p0_run

        safe_result = {
            "status": "BLOCKED",
            "outcome": "P0-03 direct subprobe passed; aggregate remains blocked.",
            "trace": [
                "executor:sharepoint-isolation-read-only-v1",
                "provider-call:staff:client_x:site-metadata",
            ],
            "api_version": "v1.0",
            "auth_context": {
                "mode": "delegated",
                "permission_names": ["Sites.Selected"],
                "source": "private local fixture metadata; requires owner evidence review",
            },
            "tenant_id_configured": True,
            "tenant_verification": "NOT_PROVEN_BY_THIS_PROBE",
            "identity_context_status": "LIVE_PASS",
            "sharepoint_isolation_status": "LIVE_PASS",
            "frappe_authorization_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
            "revocation_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
            "private_secret": TOKEN_MARKER,
        }

        class Loader:
            def create_module(self, spec):
                return None

            def exec_module(self, module) -> None:
                module.run_probe = lambda: safe_result

        module_name = "p0_isolation_probe_runner_test"
        spec = importlib.machinery.ModuleSpec(module_name, Loader())
        try:
            with patch.object(p0_run.importlib.util, "spec_from_file_location", return_value=spec):
                status, outcome, trace, observation = p0_run.live("isolation")
        finally:
            sys.modules.pop(module_name, None)
        self.assertEqual(status, "FAIL")
        self.assertIn("invalid", outcome)
        self.assertEqual(trace[-1], "executor-result:invalid")
        self.assertIsNone(observation)


if __name__ == "__main__":
    unittest.main()
