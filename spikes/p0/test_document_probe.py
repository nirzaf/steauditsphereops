from __future__ import annotations

import json
import base64
from importlib.machinery import ModuleSpec
import hashlib
import os
import subprocess
import unittest
from pathlib import Path
import time
from unittest.mock import patch
from urllib.parse import quote, unquote, urlencode, urlsplit

from scripts.p0 import documents_probe, run as p0_runner


ALLOWED_SITE = "easyguide.sharepoint.com,11111111-1111-4111-8111-111111111111,22222222-2222-4222-8222-222222222222"
CLIENT_B_SITE = "easyguide.sharepoint.com,33333333-3333-4333-8333-333333333333,44444444-4444-4444-8444-444444444444"
UNRELATED_SITE = "easyguide.sharepoint.com,55555555-5555-4555-8555-555555555555,66666666-6666-4666-8666-666666666666"
DRIVE_ID = "b!client-a-document-library"
CLIENT_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
ITEM_ID = "p0-05-item"
FOLDER_ID = "p0-05-destination"
LIST_ID = "77777777-7777-4777-8777-777777777777"
LIST_ITEM_ID = "17"
PREAUTH_URL = "https://download.sharepoint.com/file?auth=one-time-token"
DELTA_PATH = f"{documents_probe.GRAPH_BASE}/drives/{quote(DRIVE_ID, safe='')}/root/delta"


def delta_link(token: str) -> str:
    return f"{DELTA_PATH}?{urlencode({'token': token, '$select': 'id,name,size,deleted'})}"


BASELINE_DELTA_LINK = delta_link("baseline-cursor")
NEXT_DELTA_LINK = delta_link("next-cursor")
INITIAL_DELTA_REQUEST = f"{DELTA_PATH}?token=latest&%24select=id%2Cname%2Csize%2Cdeleted"


def make_token(**overrides: object) -> str:
    now = int(time.time())
    claims: dict[str, object] = {
        "tid": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        "iss": "https://login.microsoftonline.com/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa/v2.0",
        "aud": documents_probe.GRAPH_RESOURCE_ID,
        "appid": CLIENT_ID,
        "roles": ["Sites.Selected"],
        "exp": now + 3600,
        "nbf": now - 30,
        "idtyp": "app",
    }
    claims.update(overrides)
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
    return f"e30.{payload}.test-signature"


TOKEN = make_token()


def valid_config() -> documents_probe.DocumentConfig:
    return documents_probe.DocumentConfig(
        tenant_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        client_id=CLIENT_ID,
        allowed_site_id=ALLOWED_SITE,
        client_b_site_id=CLIENT_B_SITE,
        unrelated_site_id=UNRELATED_SITE,
        document_drive_id=DRIVE_ID,
    )


def response(
    status: int | None,
    body: bytes = b"",
    headers: dict[str, str] | None = None,
    error: str | None = None,
) -> documents_probe.Response:
    return documents_probe.Response(status, body, headers or {}, error)


class DocumentProbeTests(unittest.TestCase):
    def test_missing_private_bindings_fail_closed_without_provider_call(self) -> None:
        calls: list[object] = []
        with patch.object(documents_probe, "load_local_config", side_effect=documents_probe.ConfigError("missing")):
            result = documents_probe.run_probe(token=TOKEN, transport=lambda *args: calls.append(args))

        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("provider-call:none", result["trace"])
        self.assertEqual(calls, [])

    def test_config_rejects_production_wrong_grant_duplicate_sites_and_bad_guid(self) -> None:
        base = {
            "schema": "steauditsphereops/p0-sharepoint-documents@1",
            "environment": "NONPRODUCTION",
            "tenant_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "client_id": CLIENT_ID,
            "auth_mode": "application",
            "permission_names": ["Sites.Selected"],
            "site_bindings": {
                "allowed": ALLOWED_SITE,
                "client_b": CLIENT_B_SITE,
                "unrelated": UNRELATED_SITE,
            },
            "site_exists_verified": {"client_b": True, "unrelated": True},
            "drive_bindings": {"client_a_content": DRIVE_ID},
        }
        invalid_cases = [
            dict(base, environment="PRODUCTION"),
            dict(base, permission_names=["Sites.ReadWrite.All"]),
            dict(base, site_bindings=dict(base["site_bindings"], unrelated=CLIENT_B_SITE)),
            dict(
                base,
                site_bindings=dict(
                    base["site_bindings"],
                    client_b=CLIENT_B_SITE.replace(
                        "33333333-3333-4333-8333-333333333333",
                        "not-a-guid-3333-4333-8333-333333333333",
                    ),
                ),
            ),
        ]
        for value in invalid_cases:
            with self.subTest(value=value):
                with self.assertRaises(documents_probe.ConfigError):
                    documents_probe.parse_config(value)

    def test_token_must_match_tenant_client_graph_audience_and_app_role(self) -> None:
        invalid_tokens = [
            make_token(tid="cccccccc-cccc-4ccc-8ccc-cccccccccccc"),
            make_token(appid="dddddddd-dddd-4ddd-8ddd-dddddddddddd"),
            make_token(aud="https://graph.microsoft.us"),
            make_token(roles=["Sites.ReadWrite.All"]),
            make_token(scp="Sites.Selected"),
            make_token(exp=int(time.time()) - 1),
            "not-a-jwt",
        ]
        for token in invalid_tokens:
            with self.subTest(token=token[:12]):
                calls: list[object] = []
                result = documents_probe.run_probe(
                    config=valid_config(),
                    token=token,
                    transport=lambda *args: calls.append(args),
                )
                self.assertEqual(result["status"], "BLOCKED")
                self.assertIn("provider-call:none", result["trace"])
                self.assertEqual(calls, [])
                self.assertNotIn(token, json.dumps(result, sort_keys=True))

    def test_live_document_cycle_verifies_denials_bytes_metadata_saved_version_and_redirection(self) -> None:
        calls: list[tuple[str, str, bytes | None, str | None]] = []
        content_reads = 0
        content_updates = 0
        created_names: list[str] = []
        destination_names: list[str] = []
        renamed_names: list[str] = []
        metadata_values: list[str] = []

        def transport(request, _timeout: float, _limit: int):
            nonlocal content_reads, content_updates
            path = request.full_url
            method = request.get_method()
            body = request.data
            auth = request.get_header("Authorization")
            calls.append((method, path, body, auth))
            if method == "GET" and path.startswith(f"https://graph.microsoft.com/v1.0/sites/{ALLOWED_SITE}?"):
                return response(200, json.dumps({"id": ALLOWED_SITE}).encode())
            if method == "GET" and f"/sites/{CLIENT_B_SITE}?" in path:
                return response(403)
            if method == "GET" and f"/sites/{UNRELATED_SITE}?" in path:
                return response(404)
            if method == "GET" and path.endswith("/drives?%24select=id,driveType"):
                return response(200, json.dumps({"value": [{"id": DRIVE_ID, "driveType": "documentLibrary"}]}).encode())
            if method == "GET" and path == INITIAL_DELTA_REQUEST:
                return response(200, json.dumps({"value": [], "@odata.deltaLink": BASELINE_DELTA_LINK}).encode())
            if method == "GET" and path == BASELINE_DELTA_LINK:
                return response(
                    200,
                    json.dumps(
                        {
                            "value": [
                                {
                                    "id": ITEM_ID,
                                    "name": renamed_names[0],
                                    "size": len(documents_probe.FINAL_BYTES),
                                }
                            ],
                            "@odata.deltaLink": NEXT_DELTA_LINK,
                        }
                    ).encode(),
                )
            if method == "PUT" and f"/drives/{quote(DRIVE_ID, safe='')}/root:/" in path:
                self.assertEqual(body, documents_probe.ORIGINAL_BYTES)
                file_name = unquote(urlsplit(path).path.split("/root:/", 1)[1].split(":/content", 1)[0])
                created_names.append(file_name)
                return response(201, json.dumps({"id": ITEM_ID, "name": file_name, "size": len(body or b"")}).encode())
            if method == "GET" and path.endswith(f"/items/{ITEM_ID}/versions/v1/content"):
                return response(302, headers={"location": PREAUTH_URL})
            if method == "GET" and path == PREAUTH_URL:
                return response(200, documents_probe.ORIGINAL_BYTES)
            if method == "GET" and path.endswith(
                f"/drives/{quote(DRIVE_ID, safe='')}/items/{ITEM_ID}?%24select=id,sharepointIds"
            ):
                return response(
                    200,
                    json.dumps(
                        {
                            "id": ITEM_ID,
                            "sharepointIds": {
                                "siteId": "11111111-1111-4111-8111-111111111111",
                                "webId": "22222222-2222-4222-8222-222222222222",
                                "listId": LIST_ID,
                                "listItemId": LIST_ITEM_ID,
                            },
                        }
                    ).encode(),
                )
            if method == "GET" and path.endswith(f"/lists/{LIST_ID}/columns?%24select=name,readOnly,hidden"):
                return response(
                    200,
                    json.dumps({"value": [{"name": "Title", "readOnly": False, "hidden": False}]}).encode(),
                )
            if method == "GET" and path.endswith(
                f"/items/{LIST_ITEM_ID}?%24select=id,eTag&%24expand=fields(%24select=Title)"
            ):
                return response(
                    200,
                    json.dumps({"id": LIST_ITEM_ID, "eTag": 'W/"synthetic-etag"', "fields": {"Title": ""}}).encode(),
                )
            if method == "PATCH" and path.endswith(f"/items/{LIST_ITEM_ID}/fields"):
                self.assertEqual(request.get_header("If-match"), 'W/"synthetic-etag"')
                field_update = json.loads(body or b"{}")
                self.assertEqual(set(field_update), {"Title"})
                metadata_values.append(field_update["Title"])
                return response(200, json.dumps(field_update).encode())
            if method == "GET" and path.endswith(
                f"/items/{LIST_ITEM_ID}?%24select=id&%24expand=fields(%24select=Title)"
            ):
                return response(
                    200,
                    json.dumps({"id": LIST_ITEM_ID, "fields": {"Title": metadata_values[-1]}}).encode(),
                )
            if method == "POST" and path.endswith(f"/drives/{quote(DRIVE_ID, safe='')}/root/children"):
                folder_request = json.loads(body or b"{}")
                self.assertEqual(folder_request["@microsoft.graph.conflictBehavior"], "fail")
                destination_names.append(folder_request["name"])
                return response(
                    201,
                    json.dumps({"id": FOLDER_ID, "name": folder_request["name"], "folder": {}}).encode(),
                )
            if method == "PATCH" and path.endswith(f"/drives/{quote(DRIVE_ID, safe='')}/items/{ITEM_ID}"):
                move_request = json.loads(body or b"{}")
                renamed_names.append(move_request["name"])
                self.assertEqual(move_request["parentReference"], {"id": FOLDER_ID})
                return response(
                    200,
                    json.dumps(
                        {
                            "id": ITEM_ID,
                            "name": move_request["name"],
                            "parentReference": {"id": FOLDER_ID},
                        }
                    ).encode(),
                )
            if method == "GET" and path.endswith(f"/items/{ITEM_ID}?%24select=id,name,parentReference"):
                return response(
                    200,
                    json.dumps(
                        {
                            "id": ITEM_ID,
                            "name": renamed_names[0],
                            "parentReference": {"id": FOLDER_ID},
                        }
                    ).encode(),
                )
            if method == "GET" and path.endswith(f"/items/{ITEM_ID}/content"):
                content_reads += 1
                content = {
                    1: documents_probe.ORIGINAL_BYTES,
                    2: documents_probe.UPDATED_BYTES,
                    3: documents_probe.FINAL_BYTES,
                    4: documents_probe.FINAL_BYTES,
                }[content_reads]
                return response(200, content)
            if method == "PUT" and path.endswith(f"/items/{ITEM_ID}/content"):
                content_updates += 1
                expected_body = documents_probe.UPDATED_BYTES if content_updates == 1 else documents_probe.FINAL_BYTES
                self.assertEqual(body, expected_body)
                return response(200, json.dumps({"id": ITEM_ID}).encode())
            if method == "GET" and path.endswith(f"/items/{ITEM_ID}/versions?%24select=id,size"):
                return response(200, json.dumps({"value": [{"id": "v1", "size": len(documents_probe.ORIGINAL_BYTES)}]}).encode())
            self.fail(f"Unexpected request in synthetic transport: {method} {path}")

        result = documents_probe.run_probe(config=valid_config(), token=TOKEN, transport=transport)
        serialized = json.dumps(result, sort_keys=True)

        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["p0_05_status"], "LIVE_PASS")
        self.assertEqual(result["p0_09_status"], "NOT_RUN_EXTERNAL_PREREQUISITE")
        self.assertEqual(result["delta_reconciliation_status"], "LIVE_PASS")
        self.assertEqual(result["p0_05_observation"]["delta_reconciliation_status"], "LIVE_PASS")
        self.assertEqual(result["metadata_update_status"], "LIVE_PASS")
        self.assertEqual(result["p0_05_observation"]["metadata_update_status"], "LIVE_PASS")
        self.assertEqual(result["p0_05_observation"]["snapshot_sha256"], result["p0_05_observation"]["original_sha256"])
        self.assertEqual(
            result["p0_05_observation"]["current_sha256"],
            hashlib.sha256(documents_probe.FINAL_BYTES).hexdigest(),
        )
        self.assertNotIn(TOKEN, serialized)
        self.assertNotIn(PREAUTH_URL, serialized)
        self.assertNotIn(ALLOWED_SITE, serialized)
        self.assertNotIn(BASELINE_DELTA_LINK, serialized)
        self.assertNotIn(NEXT_DELTA_LINK, serialized)
        self.assertNotIn(LIST_ID, serialized)
        self.assertEqual(len(metadata_values), 1)
        self.assertTrue(metadata_values[0].startswith("STE AuditSphere P0-05 "))
        self.assertEqual(len(destination_names), 1)
        self.assertEqual(len(renamed_names), 1)
        self.assertEqual(
            destination_names[0],
            created_names[0].removesuffix(".txt") + "-destination",
        )
        self.assertEqual(
            renamed_names[0],
            created_names[0].removesuffix(".txt") + "-renamed.txt",
        )
        self.assertTrue(all(call[3] == f"Bearer {TOKEN}" for call in calls if call[1].startswith("https://graph.microsoft.com/")))
        download_call = next(call for call in calls if call[1] == PREAUTH_URL)
        self.assertIsNone(download_call[3])
        self.assertEqual([call[0] for call in calls].count("PUT"), 3)
        self.assertEqual([call[0] for call in calls].count("POST"), 1)
        self.assertEqual([call[0] for call in calls].count("PATCH"), 2)
        self.assertEqual([call[0] for call in calls].count("DELETE"), 0)

    def test_metadata_update_writes_only_an_existing_writable_title_column(self) -> None:
        for column_value, paged in (
            ({"name": "Title", "readOnly": True, "hidden": False}, False),
            ({"name": "Other", "readOnly": False, "hidden": False}, False),
            ({"name": "Title", "readOnly": False, "hidden": False}, True),
        ):
            with self.subTest(column=column_value, paged=paged):
                requests: list[str] = []

                def transport(request, _timeout: float, _limit: int):
                    requests.append(request.full_url)
                    if request.full_url.endswith(
                        f"/drives/{quote(DRIVE_ID, safe='')}/items/{ITEM_ID}?%24select=id,sharepointIds"
                    ):
                        return response(
                            200,
                            json.dumps(
                                {
                                    "id": ITEM_ID,
                                    "sharepointIds": {
                                        "siteId": "11111111-1111-4111-8111-111111111111",
                                        "webId": "22222222-2222-4222-8222-222222222222",
                                        "listId": LIST_ID,
                                        "listItemId": LIST_ITEM_ID,
                                    },
                                }
                            ).encode(),
                        )
                    if request.full_url.endswith(f"/lists/{LIST_ID}/columns?%24select=name,readOnly,hidden"):
                        payload = {"value": [column_value]}
                        if paged:
                            payload["@odata.nextLink"] = "https://graph.microsoft.com/v1.0/next"
                        return response(200, json.dumps(payload).encode())
                    self.fail("No list-item read or write is allowed when Title is not safely writable")

                status, _outcome, _trace = documents_probe._update_synthetic_title_metadata(
                    site_id=ALLOWED_SITE,
                    drive_id=DRIVE_ID,
                    item_id=ITEM_ID,
                    title_value="STE AuditSphere P0-05 synthetic metadata",
                    token=TOKEN,
                    transport=transport,
                )

                self.assertEqual(status, "BLOCKED")
                self.assertEqual(len(requests), 2)

    def test_metadata_write_uses_bound_etag_and_never_retries_unknown_outcome(self) -> None:
        calls: list[tuple[str, str | None]] = []

        def transport(request, _timeout: float, _limit: int):
            method = request.get_method()
            calls.append((method, request.full_url))
            if method == "GET" and request.full_url.endswith(
                f"/drives/{quote(DRIVE_ID, safe='')}/items/{ITEM_ID}?%24select=id,sharepointIds"
            ):
                return response(
                    200,
                    json.dumps(
                        {
                            "id": ITEM_ID,
                            "sharepointIds": {
                                "siteId": "11111111-1111-4111-8111-111111111111",
                                "webId": "22222222-2222-4222-8222-222222222222",
                                "listId": LIST_ID,
                                "listItemId": LIST_ITEM_ID,
                            },
                        }
                    ).encode(),
                )
            if method == "GET" and request.full_url.endswith(
                f"/lists/{LIST_ID}/columns?%24select=name,readOnly,hidden"
            ):
                return response(200, json.dumps({"value": [{"name": "Title", "readOnly": False}]}).encode())
            if method == "GET" and request.full_url.endswith(
                f"/items/{LIST_ITEM_ID}?%24select=id,eTag&%24expand=fields(%24select=Title)"
            ):
                return response(
                    200,
                    json.dumps({"id": LIST_ITEM_ID, "eTag": 'W/"etag-before-patch"', "fields": {"Title": ""}}).encode(),
                )
            if method == "PATCH" and request.full_url.endswith(f"/items/{LIST_ITEM_ID}/fields"):
                self.assertEqual(request.get_header("If-match"), 'W/"etag-before-patch"')
                return response(None, error="TimeoutError")
            self.fail("No retry or readback is allowed after an unknown metadata-write outcome")

        status, _outcome, trace = documents_probe._update_synthetic_title_metadata(
            site_id=ALLOWED_SITE,
            drive_id=DRIVE_ID,
            item_id=ITEM_ID,
            title_value="STE AuditSphere P0-05 synthetic metadata",
            token=TOKEN,
            transport=transport,
        )

        self.assertEqual(status, "BLOCKED")
        self.assertIn("metadata-write-retry:none", trace)
        self.assertEqual([method for method, _path in calls].count("PATCH"), 1)
        self.assertEqual(len(calls), 4)

    def test_delta_link_is_bound_to_graph_drive_and_one_opaque_cursor(self) -> None:
        self.assertTrue(documents_probe._valid_delta_link(BASELINE_DELTA_LINK, DRIVE_ID))
        invalid_links = [
            BASELINE_DELTA_LINK.replace("https://graph.microsoft.com", "http://graph.microsoft.com"),
            BASELINE_DELTA_LINK.replace("graph.microsoft.com", "graph.microsoft.com.attacker.invalid"),
            BASELINE_DELTA_LINK.replace(quote(DRIVE_ID, safe=""), "another-drive"),
            BASELINE_DELTA_LINK + "&extra=1",
            f"{DELTA_PATH}?$select=id,name,size",
            f"{DELTA_PATH}?token=one&token=two",
            BASELINE_DELTA_LINK + "#fragment",
        ]
        for link in invalid_links:
            with self.subTest(link=link):
                self.assertFalse(documents_probe._valid_delta_link(link, DRIVE_ID))

    def test_delta_reconciliation_uses_last_target_change_and_keeps_cursor_private(self) -> None:
        second_page = delta_link("second-page")
        final_link = delta_link("final-cursor")
        calls: list[str] = []

        def transport(request, _timeout: float, _limit: int):
            calls.append(request.full_url)
            if request.full_url == BASELINE_DELTA_LINK:
                payload = {
                    "value": [{"id": ITEM_ID, "name": "prior.txt", "size": len(documents_probe.ORIGINAL_BYTES)}],
                    "@odata.nextLink": second_page,
                }
            elif request.full_url == second_page:
                payload = {
                    "value": [{"id": ITEM_ID, "name": "target.txt", "size": len(documents_probe.UPDATED_BYTES)}],
                    "@odata.deltaLink": final_link,
                }
            else:
                self.fail("The delta probe requested a URL outside the supplied cursor pages")
            return response(200, json.dumps(payload).encode())

        status, outcome, trace = documents_probe._reconcile_delta(
            delta_link=BASELINE_DELTA_LINK,
            drive_id=DRIVE_ID,
            item_id=ITEM_ID,
            item_name="target.txt",
            item_size=len(documents_probe.UPDATED_BYTES),
            token=TOKEN,
            transport=transport,
        )

        self.assertEqual(status, "LIVE_PASS")
        self.assertIn("present in the incremental delta feed", outcome)
        self.assertEqual(calls, [BASELINE_DELTA_LINK, second_page])
        self.assertTrue(all("cursor" not in entry for entry in trace))
        self.assertTrue(all("token=" not in entry for entry in trace))

    def test_delta_reconciliation_blocks_missing_target_and_fails_mismatched_target(self) -> None:
        cases = (
            ({"value": [{"id": "another-item", "name": "other.txt", "size": 4}], "@odata.deltaLink": NEXT_DELTA_LINK}, "BLOCKED"),
            ({"value": [{"id": ITEM_ID, "name": "wrong.txt", "size": len(documents_probe.UPDATED_BYTES)}], "@odata.deltaLink": NEXT_DELTA_LINK}, "FAIL"),
            ({"value": [{"id": ITEM_ID, "deleted": {}}], "@odata.deltaLink": NEXT_DELTA_LINK}, "FAIL"),
        )
        for payload, expected_status in cases:
            with self.subTest(expected_status=expected_status, payload=payload):
                status, _outcome, trace = documents_probe._reconcile_delta(
                    delta_link=BASELINE_DELTA_LINK,
                    drive_id=DRIVE_ID,
                    item_id=ITEM_ID,
                    item_name="target.txt",
                    item_size=len(documents_probe.UPDATED_BYTES),
                    token=TOKEN,
                    transport=lambda *_args: response(200, json.dumps(payload).encode()),
                )
                self.assertEqual(status, expected_status)
                self.assertEqual(trace, ["provider-call:delta-page"])

    def test_delta_reconciliation_rejects_hostile_link_and_stops_at_page_limit(self) -> None:
        hostile_calls: list[str] = []
        hostile_link = f"https://graph.microsoft.com.attacker.invalid/v1.0/drives/{DRIVE_ID}/root/delta?token=next"
        hostile_status, _outcome, hostile_trace = documents_probe._reconcile_delta(
            delta_link=BASELINE_DELTA_LINK,
            drive_id=DRIVE_ID,
            item_id=ITEM_ID,
            item_name="target.txt",
            item_size=len(documents_probe.UPDATED_BYTES),
            token=TOKEN,
            transport=lambda request, *_args: (
                hostile_calls.append(request.full_url)
                or response(200, json.dumps({"value": [], "@odata.nextLink": hostile_link}).encode())
            ),
        )
        self.assertEqual(hostile_status, "FAIL")
        self.assertEqual(hostile_calls, [BASELINE_DELTA_LINK])
        self.assertEqual(hostile_trace, ["provider-call:delta-page"])

        page_calls: list[str] = []

        def paged_transport(request, _timeout: float, _limit: int):
            page_calls.append(request.full_url)
            return response(
                200,
                json.dumps({"value": [], "@odata.nextLink": delta_link(f"page-{len(page_calls)}")}).encode(),
            )

        page_status, _outcome, page_trace = documents_probe._reconcile_delta(
            delta_link=BASELINE_DELTA_LINK,
            drive_id=DRIVE_ID,
            item_id=ITEM_ID,
            item_name="target.txt",
            item_size=len(documents_probe.UPDATED_BYTES),
            token=TOKEN,
            transport=paged_transport,
        )
        self.assertEqual(page_status, "BLOCKED")
        self.assertEqual(len(page_calls), documents_probe.MAX_DELTA_PAGES)
        self.assertEqual(len(page_trace), documents_probe.MAX_DELTA_PAGES)

    def test_documents_runner_rejects_provider_cursors_in_evidence_fields(self) -> None:
        probe_result = {
            "status": "BLOCKED",
            "outcome": "P0-05 delta observation is blocked.",
            "trace": [],
            "p0_05_status": "BLOCKED",
            "p0_09_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
            "delta_reconciliation_status": "BLOCKED",
            "delta_cursor": BASELINE_DELTA_LINK,
        }

        class Loader:
            def create_module(self, _spec):
                return None

            def exec_module(self, module) -> None:
                module.run_probe = lambda: probe_result

        fake_spec = ModuleSpec("p0_documents_probe", Loader())
        with patch.object(p0_runner.importlib.util, "spec_from_file_location", return_value=fake_spec):
            status, _outcome, _trace, observation = p0_runner.live("documents")
            self.assertEqual(status, "FAIL")
            self.assertIsNone(observation)

            probe_result = documents_probe._success(
                ["provider-call:delta-page"],
                current_sha256=hashlib.sha256(documents_probe.FINAL_BYTES).hexdigest(),
                snapshot_sha256=hashlib.sha256(documents_probe.ORIGINAL_BYTES).hexdigest(),
                metadata_update_status="LIVE_PASS",
                delta_reconciliation_status="LIVE_PASS",
            )
            status, _outcome, _trace, observation = p0_runner.live("documents")

        self.assertEqual(status, "BLOCKED")
        self.assertEqual(observation["delta_reconciliation_status"], "LIVE_PASS")
        self.assertNotIn("token=", json.dumps(observation))

    def test_untrusted_preauth_host_is_rejected_before_followup_call(self) -> None:
        calls: list[str] = []

        def transport(request, _timeout: float, _limit: int):
            calls.append(request.full_url)
            if request.get_method() == "GET" and request.full_url.endswith("/content"):
                return response(302, headers={"location": "https://sharepoint.com.attacker.invalid/file"})
            self.fail("An untrusted redirect target must not be requested")

        result, error = documents_probe._read_content("/items/x/content", TOKEN, transport)

        self.assertIsNone(result)
        self.assertIn("outside the allowed Microsoft file hosts", error or "")
        self.assertEqual(len(calls), 1)

    def test_unknown_upload_outcome_is_not_retried(self) -> None:
        requests: list[str] = []

        def transport(request, _timeout: float, _limit: int):
            requests.append(request.full_url)
            if request.full_url.startswith(f"https://graph.microsoft.com/v1.0/sites/{ALLOWED_SITE}?"):
                return response(200, json.dumps({"id": ALLOWED_SITE}).encode())
            if f"/sites/{CLIENT_B_SITE}?" in request.full_url:
                return response(403)
            if f"/sites/{UNRELATED_SITE}?" in request.full_url:
                return response(403)
            if request.full_url.endswith("/drives?%24select=id,driveType"):
                return response(200, json.dumps({"value": [{"id": DRIVE_ID, "driveType": "documentLibrary"}]}).encode())
            if request.full_url == INITIAL_DELTA_REQUEST:
                return response(200, json.dumps({"value": [], "@odata.deltaLink": BASELINE_DELTA_LINK}).encode())
            if request.get_method() == "PUT":
                return response(None, error="TimeoutError")
            self.fail("No provider request is allowed after an uncertain upload")

        result = documents_probe.run_probe(config=valid_config(), token=TOKEN, transport=transport)

        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("write-retry:none", result["trace"])
        self.assertEqual(len([url for url in requests if "/root:/" in url]), 1)
        self.assertEqual(len(requests), 6)

    def test_private_config_and_token_are_not_checked_in_or_returned(self) -> None:
        root = Path(__file__).resolve().parents[2]
        checked = subprocess.run(
            ["git", "check-ignore", "--quiet", "--no-index", "--", ".local/p0/sharepoint-documents.json"],
            cwd=root,
            check=False,
            timeout=10,
        )
        self.assertEqual(checked.returncode, 0)
        with patch.dict(os.environ, {documents_probe.TOKEN_ENV: TOKEN}):
            with patch.object(documents_probe, "load_local_config", side_effect=documents_probe.ConfigError("missing")):
                outcome = documents_probe.run_probe()
            self.assertNotIn(documents_probe.TOKEN_ENV, os.environ)
        self.assertNotIn(TOKEN, json.dumps(outcome, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
