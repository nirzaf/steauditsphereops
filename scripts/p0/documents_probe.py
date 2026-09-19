"""Bounded live SharePoint upload and saved-version proof for WBS-05 P0-05.

The probe accepts only ignored local bindings, uses a short-lived token from
the process environment, and writes one small synthetic file to the prebound
Client A library. It never retries an uncertain write or deletes the artifact.
"""

from __future__ import annotations

import hashlib
import base64
import binascii
import json
import os
import re
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / ".local" / "p0" / "sharepoint-documents.json"
TOKEN_ENV = "AUDIT_P0_GRAPH_ACCESS_TOKEN"
GRAPH_ORIGIN = "https://graph.microsoft.com"
GRAPH_BASE = f"{GRAPH_ORIGIN}/v1.0"
GRAPH_RESOURCE_ID = "00000003-0000-0000-c000-000000000000"
MAX_CONFIG_BYTES = 16 * 1024
MAX_RESPONSE_BYTES = 16 * 1024
MAX_DELTA_RESPONSE_BYTES = 64 * 1024
MAX_DELTA_PAGES = 8
MAX_FILE_BYTES = 256
MAX_VERSION_CANDIDATES = 8
REQUEST_TIMEOUT_SECONDS = 20
SITE_ID_RE = re.compile(r"^([A-Za-z0-9.-]+),([^,]+),([^,]+)$")
GRAPH_ID_RE = re.compile(r"^[A-Za-z0-9!._~-]{1,512}$")
LIST_ITEM_ID_RE = re.compile(r"^[1-9][0-9]{0,19}$")
DOWNLOAD_HOST_SUFFIXES = (
    "sharepoint.com",
    "sharepoint-df.com",
    "sharepointonline.com",
    "onedrive.com",
    "1drv.com",
    "1drv.ms",
)

ORIGINAL_BYTES = b"STE AuditSphere P0-05 synthetic original v1\n"
UPDATED_BYTES = b"STE AuditSphere P0-05 synthetic working copy v2\n"
FINAL_BYTES = b"STE AuditSphere P0-05 synthetic working copy v3\n"


@dataclass(frozen=True)
class DocumentConfig:
    tenant_id: str
    client_id: str
    allowed_site_id: str
    client_b_site_id: str
    unrelated_site_id: str
    document_drive_id: str


@dataclass(frozen=True)
class Response:
    status: int | None
    body: bytes
    headers: Mapping[str, str]
    error: str | None = None


Transport = Callable[[urllib.request.Request, float, int], Response]


class ConfigError(ValueError):
    """The ignored private document fixture is absent or invalid."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


def _validate_site_id(value: object, field_name: str) -> tuple[str, str]:
    if not isinstance(value, str) or not value or len(value) > 512:
        raise ConfigError(f"{field_name} must be a stable Graph site ID")
    match = SITE_ID_RE.fullmatch(value)
    if match is None:
        raise ConfigError(f"{field_name} must use hostname,site-guid,web-guid form")
    host, site_guid, web_guid = match.groups()
    if not host.casefold().endswith(".sharepoint.com"):
        raise ConfigError(f"{field_name} must bind to SharePoint Online")
    for value_part in (site_guid, web_guid):
        try:
            if str(uuid.UUID(value_part)) != value_part.casefold():
                raise ValueError
        except (ValueError, AttributeError):
            raise ConfigError(f"{field_name} contains an invalid site identifier")
    return value, host.casefold()


def parse_config(value: object) -> DocumentConfig:
    if not isinstance(value, dict):
        raise ConfigError("configuration must be a JSON object")
    expected_keys = {
        "schema",
        "environment",
        "tenant_id",
        "client_id",
        "auth_mode",
        "permission_names",
        "site_bindings",
        "site_exists_verified",
        "drive_bindings",
    }
    if set(value) != expected_keys:
        raise ConfigError("configuration fields do not match the P0-05 contract")
    if value.get("schema") != "steauditsphereops/p0-sharepoint-documents@1":
        raise ConfigError("configuration schema is not supported")
    if value.get("environment") != "NONPRODUCTION":
        raise ConfigError("only an explicitly configured non-production tenant is allowed")
    try:
        tenant_id = str(uuid.UUID(value["tenant_id"]))
    except (TypeError, ValueError, KeyError) as error:
        raise ConfigError("tenant_id must be a GUID") from error
    try:
        client_id = str(uuid.UUID(value["client_id"]))
    except (TypeError, ValueError, KeyError) as error:
        raise ConfigError("client_id must be a GUID") from error
    if value.get("auth_mode") != "application":
        raise ConfigError("P0-05 requires the owner-selected application identity")
    if value.get("permission_names") != ["Sites.Selected"]:
        raise ConfigError("P0-05 requires the exact owner-approved Sites.Selected grant")

    bindings = value.get("site_bindings")
    if not isinstance(bindings, dict) or set(bindings) != {
        "allowed",
        "client_b",
        "unrelated",
    }:
        raise ConfigError("site_bindings must contain allowed, client_b, and unrelated IDs")
    parsed_sites = {
        key: _validate_site_id(bindings[key], f"{key} site")
        for key in ("allowed", "client_b", "unrelated")
    }
    if len({value[0] for value in parsed_sites.values()}) != 3:
        raise ConfigError("allowed, Client B, and unrelated sites must be distinct")
    if len({value[1] for value in parsed_sites.values()}) != 1:
        raise ConfigError("all test site bindings must belong to the same SharePoint host")

    verified = value.get("site_exists_verified")
    if not isinstance(verified, dict) or set(verified) != {"client_b", "unrelated"}:
        raise ConfigError("site_exists_verified must confirm Client B and unrelated site existence")
    if any(verified.get(name) is not True for name in ("client_b", "unrelated")):
        raise ConfigError("denial tests require independently verified existing sites")

    drives = value.get("drive_bindings")
    if not isinstance(drives, dict) or set(drives) != {"client_a_content"}:
        raise ConfigError("drive_bindings must contain the Client A content library")
    drive_id = drives["client_a_content"]
    if not isinstance(drive_id, str) or not GRAPH_ID_RE.fullmatch(drive_id):
        raise ConfigError("Client A content drive ID is invalid")

    return DocumentConfig(
        tenant_id=tenant_id,
        client_id=client_id,
        allowed_site_id=parsed_sites["allowed"][0],
        client_b_site_id=parsed_sites["client_b"][0],
        unrelated_site_id=parsed_sites["unrelated"][0],
        document_drive_id=drive_id,
    )


def load_local_config(path: Path = CONFIG_PATH) -> DocumentConfig:
    local_root = ROOT / ".local"
    parent = ROOT / ".local" / "p0"
    if any(candidate.is_symlink() for candidate in (local_root, parent, path)):
        raise ConfigError("private fixture configuration cannot use symlinked paths")
    try:
        resolved_root = local_root.resolve(strict=True)
        resolved_path = path.resolve(strict=True)
        resolved_path.relative_to(resolved_root)
    except (OSError, ValueError) as error:
        raise ConfigError("private local fixture configuration is missing or outside .local") from error
    if not resolved_path.is_file() or resolved_path.stat().st_size > MAX_CONFIG_BYTES:
        raise ConfigError("private local fixture configuration is missing or too large")
    try:
        value = json.loads(resolved_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ConfigError("private local fixture configuration is unreadable or invalid JSON") from error
    return parse_config(value)


def _send(request: urllib.request.Request, timeout: float, limit: int) -> Response:
    opener = urllib.request.build_opener(_NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            body = response.read(limit + 1) if limit else b""
            if len(body) > limit:
                return Response(int(response.status), b"", {}, "response_too_large")
            return Response(
                int(response.status),
                body,
                {key.casefold(): value for key, value in response.headers.items()},
            )
    except urllib.error.HTTPError as error:
        return Response(
            int(error.code),
            b"",
            {key.casefold(): value for key, value in (error.headers or {}).items()},
        )
    except (urllib.error.URLError, TimeoutError, socket.timeout, OSError) as error:
        return Response(None, b"", {}, type(error).__name__)


def _graph_request(
    path: str,
    token: str,
    *,
    method: str = "GET",
    body: bytes | None = None,
    content_type: str | None = None,
    accept: str = "application/json",
    if_match: str | None = None,
) -> urllib.request.Request:
    headers = {
        "Accept": accept,
        "Authorization": f"Bearer {token}",
        "client-request-id": str(uuid.uuid4()),
        "return-client-request-id": "true",
    }
    if content_type is not None:
        headers["Content-Type"] = content_type
    if if_match is not None:
        headers["If-Match"] = if_match
    return urllib.request.Request(
        f"{GRAPH_BASE}{path}",
        data=body,
        headers=headers,
        method=method,
    )


def _parse_json(response: Response) -> object | None:
    try:
        return json.loads(response.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _access_token_claims(token: str) -> dict[str, object] | None:
    parts = token.split(".")
    if len(parts) != 3 or not parts[1] or not re.fullmatch(r"[A-Za-z0-9_-]+", parts[1]):
        return None
    try:
        payload = base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4))
        claims = json.loads(payload.decode("utf-8"))
    except (binascii.Error, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return claims if isinstance(claims, dict) else None


def _token_matches_binding(token: str, config: DocumentConfig) -> bool:
    claims = _access_token_claims(token)
    if claims is None:
        return False
    tenant_id = config.tenant_id.casefold()
    issuer = claims.get("iss")
    allowed_issuers = {
        f"https://sts.windows.net/{tenant_id}/",
        f"https://login.microsoftonline.com/{tenant_id}/v2.0",
    }
    now = int(time.time())
    token_tenant_id = claims.get("tid")
    audience = claims.get("aud")
    exp = claims.get("exp")
    nbf = claims.get("nbf")
    roles = claims.get("roles")
    app_id = claims.get("appid", claims.get("azp"))
    return (
        isinstance(token_tenant_id, str)
        and token_tenant_id.casefold() == tenant_id
        and isinstance(issuer, str)
        and issuer.casefold() in allowed_issuers
        and isinstance(audience, str)
        and audience in {GRAPH_RESOURCE_ID, GRAPH_ORIGIN}
        and app_id == config.client_id
        and isinstance(roles, list)
        and roles == ["Sites.Selected"]
        and not claims.get("scp")
        and claims.get("idtyp", "app") == "app"
        and type(exp) is int
        and type(nbf) is int
        and exp > now
        and nbf <= now + 300
    )


def _blocked(outcome: str, trace: list[str], **fields: object) -> dict[str, object]:
    return {
        "status": "BLOCKED",
        "outcome": outcome,
        "trace": trace,
        "p0_05_status": "BLOCKED",
        "p0_09_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
        "metadata_update_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
        "delta_reconciliation_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
        **fields,
    }


def _failed(outcome: str, trace: list[str], **fields: object) -> dict[str, object]:
    return {
        "status": "FAIL",
        "outcome": outcome,
        "trace": trace,
        "p0_05_status": "FAIL",
        "p0_09_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
        "metadata_update_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
        "delta_reconciliation_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
        **fields,
    }


def _success(trace: list[str], **fields: object) -> dict[str, object]:
    return {
        "status": "BLOCKED",
        "outcome": (
            "P0-05 upload, repeated edits, preserved exact snapshot readback, writable Title metadata update, and bounded delta reconciliation passed; "
            "other P0-05 capabilities and P0-09 records protection remain unobserved."
        ),
        "trace": trace,
        "p0_05_status": "LIVE_PASS",
        "p0_09_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
        "metadata_update_status": fields.get("metadata_update_status"),
        "p0_05_observation": {
            "auth_mode": "application",
            "permission_names": ["Sites.Selected"],
            "tenant_id_configured": True,
            "tenant_verification": "GRAPH_ACCEPTED_TOKEN_MATCHING_CONFIGURED_TENANT_CLIENT_AND_ROLE",
            "target_ids": "redacted",
            "client_b_site_metadata": "DENIED",
            "unrelated_site_metadata": "DENIED",
            "original_sha256": hashlib.sha256(ORIGINAL_BYTES).hexdigest(),
            "updated_sha256": hashlib.sha256(UPDATED_BYTES).hexdigest(),
            "snapshot_sha256": fields["snapshot_sha256"],
            "current_sha256": fields["current_sha256"],
            "original_size": len(ORIGINAL_BYTES),
            "updated_size": len(UPDATED_BYTES),
            "current_size": len(FINAL_BYTES),
            "version_id": "redacted",
            "drive_item_id": "redacted",
            "file_name": "redacted synthetic unique name",
            "metadata_update_status": fields.get("metadata_update_status"),
            "delta_reconciliation_status": fields.get("delta_reconciliation_status"),
        },
        **fields,
    }


def _site_request(site_id: str, token: str) -> urllib.request.Request:
    site_segment = urllib.parse.quote(site_id, safe=",")
    return _graph_request(f"/sites/{site_segment}?%24select=id", token)


def _valid_delta_link(value: object, drive_id: str) -> bool:
    if not isinstance(value, str) or not value or len(value) > MAX_DELTA_RESPONSE_BYTES:
        return False
    try:
        parsed = urllib.parse.urlsplit(value)
        port = parsed.port
    except ValueError:
        return False
    expected_path = f"/v1.0/drives/{drive_id}/root/delta"
    try:
        query = urllib.parse.parse_qs(
            parsed.query,
            keep_blank_values=True,
            strict_parsing=True,
            max_num_fields=8,
        )
    except ValueError:
        return False
    return (
        parsed.scheme == "https"
        and (parsed.hostname or "").casefold() == "graph.microsoft.com"
        and port in {None, 443}
        and parsed.username is None
        and parsed.password is None
        and not parsed.fragment
        and urllib.parse.unquote(parsed.path) == expected_path
        and bool(query)
        and set(query).issubset({"token", "$deltatoken", "$skiptoken", "$select", "$top"})
        and len(set(query) & {"token", "$deltatoken", "$skiptoken"}) == 1
        and all(len(values) == 1 and values[0] for values in query.values())
    )


def _delta_link_request(url: str, token: str) -> urllib.request.Request:
    return urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "client-request-id": str(uuid.uuid4()),
            "return-client-request-id": "true",
        },
        method="GET",
    )


def _reconcile_delta(
    *,
    delta_link: str,
    drive_id: str,
    item_id: str,
    item_name: str,
    item_size: int,
    token: str,
    transport: Transport,
) -> tuple[str, str, list[str]]:
    if not _valid_delta_link(delta_link, drive_id):
        return "FAIL", "Graph returned an invalid delta cursor; no cursor request was sent.", []

    trace: list[str] = []
    current_link = delta_link
    latest_target_state: str | None = None
    for _page_number in range(MAX_DELTA_PAGES):
        response = transport(
            _delta_link_request(current_link, token),
            REQUEST_TIMEOUT_SECONDS,
            MAX_DELTA_RESPONSE_BYTES,
        )
        trace.append("provider-call:delta-page")
        if _is_provider_unavailable(response):
            return "BLOCKED", "Delta reconciliation could not be observed; no broader consent was requested.", trace
        if response.status != 200:
            return "FAIL", "Delta reconciliation returned an unexpected status.", trace
        payload = _parse_json(response)
        if not isinstance(payload, dict) or not isinstance(payload.get("value"), list):
            return "FAIL", "Delta reconciliation returned an invalid page.", trace

        for item in payload["value"]:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                return "FAIL", "Delta reconciliation returned an invalid item entry.", trace
            if item["id"] != item_id:
                continue
            if item.get("deleted") is not None:
                latest_target_state = "DELETED"
            elif item.get("name") == item_name and type(item.get("size")) is int and item["size"] == item_size:
                latest_target_state = "MATCH"
            else:
                latest_target_state = "MISMATCH"

        next_link = payload.get("@odata.nextLink")
        new_delta_link = payload.get("@odata.deltaLink")
        if isinstance(next_link, str) and new_delta_link is None:
            if not _valid_delta_link(next_link, drive_id):
                return "FAIL", "Delta pagination returned a link outside the bound Graph drive.", trace
            current_link = next_link
            continue
        if next_link is not None or not isinstance(new_delta_link, str):
            return "BLOCKED", "Delta reconciliation did not return a bounded continuation cursor.", trace
        if not _valid_delta_link(new_delta_link, drive_id):
            return "FAIL", "Delta reconciliation returned a cursor outside the bound Graph drive.", trace
        if latest_target_state == "MATCH":
            return "LIVE_PASS", "The synthetic file change was present in the incremental delta feed.", trace
        if latest_target_state in {"DELETED", "MISMATCH"}:
            return "FAIL", "The latest delta state for the synthetic file did not match its saved working copy.", trace
        return "BLOCKED", "The incremental delta feed did not contain the synthetic file change.", trace

    return "BLOCKED", "Delta pagination exceeded the bounded P0 page limit.", trace


def _is_provider_unavailable(response: Response) -> bool:
    return (
        response.error is not None
        or response.status is None
        or response.status in {401, 403, 404, 429}
        or response.status >= 500
    )


def _allowed_download_location(value: str | None) -> bool:
    if not isinstance(value, str) or not value or len(value) > 16 * 1024:
        return False
    try:
        parsed = urllib.parse.urlsplit(value)
        hostname = (parsed.hostname or "").casefold().rstrip(".")
        port = parsed.port
    except ValueError:
        return False
    if (
        parsed.scheme != "https"
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or (port is not None and port != 443)
    ):
        return False
    return any(
        hostname == suffix or hostname.endswith("." + suffix)
        for suffix in DOWNLOAD_HOST_SUFFIXES
    )


def _read_content(
    path: str,
    token: str,
    transport: Transport,
) -> tuple[bytes | None, str | None]:
    response = transport(
        _graph_request(path, token, accept="application/octet-stream"),
        REQUEST_TIMEOUT_SECONDS,
        MAX_FILE_BYTES,
    )
    if response.error is not None:
        return None, "Graph content request outcome is unknown."
    if response.status == 200:
        return response.body, None
    if response.status != 302:
        return None, "Graph did not return content or a preauthenticated download URL."

    location = response.headers.get("location")
    if not _allowed_download_location(location):
        return None, "Graph returned a download URL outside the allowed Microsoft file hosts."
    download_request = urllib.request.Request(
        location,
        headers={"Accept": "application/octet-stream"},
        method="GET",
    )
    download = transport(download_request, REQUEST_TIMEOUT_SECONDS, MAX_FILE_BYTES)
    if download.error is not None or download.status != 200:
        return None, "The preauthenticated version content could not be read."
    return download.body, None


def _update_synthetic_title_metadata(
    *,
    site_id: str,
    drive_id: str,
    item_id: str,
    title_value: str,
    token: str,
    transport: Transport,
) -> tuple[str, str, list[str]]:
    """Update and read back the built-in Title field on one synthetic file."""
    trace: list[str] = []
    site_match = SITE_ID_RE.fullmatch(site_id)
    if site_match is None or not title_value or len(title_value) > 128:
        return "FAIL", "The synthetic metadata binding or value was invalid.", trace

    drive_segment = urllib.parse.quote(drive_id, safe="")
    item_binding_response = transport(
        _graph_request(
            f"/drives/{drive_segment}/items/{urllib.parse.quote(item_id, safe='')}?%24select=id,sharepointIds",
            token,
        ),
        REQUEST_TIMEOUT_SECONDS,
        MAX_RESPONSE_BYTES,
    )
    trace.append("provider-call:read-synthetic-metadata-binding")
    if _is_provider_unavailable(item_binding_response):
        return "BLOCKED", "The synthetic file's SharePoint list binding could not be observed.", trace
    if item_binding_response.status != 200:
        return "FAIL", "The synthetic file's SharePoint list binding returned an unexpected status.", trace

    item_binding = _parse_json(item_binding_response)
    sharepoint_ids = item_binding.get("sharepointIds") if isinstance(item_binding, dict) else None
    if (
        not isinstance(item_binding, dict)
        or item_binding.get("id") != item_id
        or not isinstance(sharepoint_ids, dict)
        or not isinstance(sharepoint_ids.get("siteId"), str)
        or sharepoint_ids["siteId"].casefold() != site_match.group(2).casefold()
        or not isinstance(sharepoint_ids.get("webId"), str)
        or sharepoint_ids["webId"].casefold() != site_match.group(3).casefold()
    ):
        return "FAIL", "The returned SharePoint list binding did not match the configured site and file.", trace

    list_id = sharepoint_ids.get("listId")
    list_item_id = sharepoint_ids.get("listItemId")
    try:
        if not isinstance(list_id, str) or str(uuid.UUID(list_id)) != list_id.casefold():
            raise ValueError
    except (ValueError, AttributeError):
        return "FAIL", "The synthetic file returned an invalid SharePoint list identifier.", trace
    if not isinstance(list_item_id, str) or not LIST_ITEM_ID_RE.fullmatch(list_item_id):
        return "FAIL", "The synthetic file returned an invalid SharePoint list-item identifier.", trace

    site_segment = urllib.parse.quote(site_id, safe=",")
    list_segment = urllib.parse.quote(list_id, safe="")
    list_root = f"/sites/{site_segment}/lists/{list_segment}"
    columns_response = transport(
        _graph_request(
            f"{list_root}/columns?%24select=name,readOnly,hidden",
            token,
        ),
        REQUEST_TIMEOUT_SECONDS,
        MAX_RESPONSE_BYTES,
    )
    trace.append("provider-call:read-synthetic-list-columns")
    if _is_provider_unavailable(columns_response):
        return "BLOCKED", "The synthetic list's existing metadata columns could not be observed.", trace
    if columns_response.status != 200:
        return "FAIL", "The synthetic list's metadata columns returned an unexpected status.", trace
    columns_payload = _parse_json(columns_response)
    columns = columns_payload.get("value") if isinstance(columns_payload, dict) else None
    if (
        not isinstance(columns, list)
        or columns_payload.get("@odata.nextLink") is not None
    ):
        return "BLOCKED", "The synthetic list's metadata-column response was invalid or paged beyond the bounded probe.", trace
    title_columns = [
        column
        for column in columns
        if isinstance(column, dict) and column.get("name") == "Title"
    ]
    if len(title_columns) != 1 or title_columns[0].get("readOnly") is not False:
        return "BLOCKED", "The existing Title column was absent, ambiguous, or not writable; no metadata write was sent.", trace

    list_item_path = f"{list_root}/items/{urllib.parse.quote(list_item_id, safe='')}"
    existing_item_response = transport(
        _graph_request(
            f"{list_item_path}?%24select=id,eTag&%24expand=fields(%24select=Title)",
            token,
        ),
        REQUEST_TIMEOUT_SECONDS,
        MAX_RESPONSE_BYTES,
    )
    trace.append("provider-call:read-synthetic-list-item-before-metadata-update")
    if _is_provider_unavailable(existing_item_response):
        return "BLOCKED", "The synthetic list item could not be read before its metadata update.", trace
    if existing_item_response.status != 200:
        return "FAIL", "The synthetic list item returned an unexpected pre-update status.", trace
    existing_item = _parse_json(existing_item_response)
    existing_fields = existing_item.get("fields") if isinstance(existing_item, dict) else None
    etag = existing_item.get("eTag") if isinstance(existing_item, dict) else None
    if (
        not isinstance(existing_item, dict)
        or existing_item.get("id") != list_item_id
        or not isinstance(existing_fields, dict)
        or "Title" not in existing_fields
        or not isinstance(etag, str)
        or not etag
        or len(etag) > 1024
        or "\r" in etag
        or "\n" in etag
    ):
        return "FAIL", "The synthetic list-item identity, Title field, or ETag was invalid.", trace

    update_response = transport(
        _graph_request(
            f"{list_item_path}/fields",
            token,
            method="PATCH",
            body=json.dumps({"Title": title_value}).encode("utf-8"),
            content_type="application/json",
            if_match=etag,
        ),
        REQUEST_TIMEOUT_SECONDS,
        MAX_RESPONSE_BYTES,
    )
    trace.append("provider-call:update-synthetic-title-metadata")
    if update_response.error is not None or update_response.status is None:
        return "BLOCKED", "Synthetic metadata update outcome is unknown; no automatic retry was attempted.", trace + ["metadata-write-retry:none"]
    if update_response.status != 200:
        if update_response.status in {401, 403, 404, 409, 412, 429} or update_response.status >= 500:
            return "BLOCKED", "Synthetic metadata update was not confirmed; inspect the provider before retrying.", trace + ["metadata-write-retry:none"]
        return "FAIL", "Synthetic metadata update returned an unexpected status.", trace
    updated_fields = _parse_json(update_response)
    if not isinstance(updated_fields, dict) or updated_fields.get("Title") != title_value:
        return "FAIL", "The metadata-update receipt did not match the synthetic Title value.", trace

    readback_response = transport(
        _graph_request(
            f"{list_item_path}?%24select=id&%24expand=fields(%24select=Title)",
            token,
        ),
        REQUEST_TIMEOUT_SECONDS,
        MAX_RESPONSE_BYTES,
    )
    trace.append("provider-call:verify-synthetic-title-metadata")
    if _is_provider_unavailable(readback_response):
        return "BLOCKED", "Synthetic metadata could not be independently read back.", trace
    if readback_response.status != 200:
        return "FAIL", "Synthetic metadata readback returned an unexpected status.", trace
    readback = _parse_json(readback_response)
    readback_fields = readback.get("fields") if isinstance(readback, dict) else None
    if (
        not isinstance(readback, dict)
        or readback.get("id") != list_item_id
        or not isinstance(readback_fields, dict)
        or readback_fields.get("Title") != title_value
    ):
        return "FAIL", "Synthetic Title metadata readback did not match the requested value.", trace
    return "LIVE_PASS", "The existing writable Title field was updated and independently read back.", trace


def run_probe(
    *,
    config: DocumentConfig | None = None,
    token: str | None = None,
    transport: Transport = _send,
) -> dict[str, object]:
    trace = ["executor:sharepoint-documents-v1"]
    if token is None:
        token = os.environ.pop(TOKEN_ENV, None)
    if config is None:
        try:
            config = load_local_config()
        except ConfigError:
            return _blocked(
                "P0-05 requires approved ignored bindings at .local/p0/sharepoint-documents.json; no Graph request was sent.",
                trace + ["provider-call:none"],
            )
    token = token.strip() if isinstance(token, str) else ""
    if (
        not token
        or len(token) > 64 * 1024
        or any(character.isspace() for character in token)
    ):
        return _blocked(
            f"P0-05 requires a short-lived {TOKEN_ENV} value; no Graph request was sent.",
            trace + ["provider-call:none"],
        )

    if not _token_matches_binding(token, config):
        return _blocked(
            "P0-05 requires an unexpired Graph app-only token matching the configured tenant, client app, and exact Sites.Selected role; no Graph request was sent.",
            trace + ["provider-call:none"],
        )

    common = {
        "api_version": "v1.0",
        "auth_context": {
            "mode": "application",
            "permission_names": ["Sites.Selected"],
            "source": "private local fixture metadata; requires owner evidence review",
        },
        "tenant_id_configured": True,
        "tenant_verification": "TOKEN_CLAIMS_MATCH_CONFIGURED_TENANT_AND_CLIENT; GRAPH_ACCEPTANCE_PENDING",
        "target_ids": "redacted",
    }

    allowed_site = transport(
        _site_request(config.allowed_site_id, token),
        REQUEST_TIMEOUT_SECONDS,
        MAX_RESPONSE_BYTES,
    )
    trace.append("provider-call:authorized-site-metadata")
    if allowed_site.error is not None or allowed_site.status is None:
        return _blocked("Allowed-site metadata outcome is unknown.", trace, **common)
    if allowed_site.status != 200:
        if _is_provider_unavailable(allowed_site):
            return _blocked("Allowed-site metadata was not readable; grant or tenant binding needs review.", trace, **common)
        return _failed("Allowed-site metadata returned an unexpected HTTP status.", trace, **common)
    allowed_metadata = _parse_json(allowed_site)
    if not isinstance(allowed_metadata, dict) or allowed_metadata.get("id") != config.allowed_site_id:
        return _failed("Graph did not confirm the exact allowed-site binding.", trace, **common)

    for site_id, label in (
        (config.client_b_site_id, "client-b"),
        (config.unrelated_site_id, "unrelated"),
    ):
        response = transport(
            _site_request(site_id, token),
            REQUEST_TIMEOUT_SECONDS,
            0,
        )
        trace.append(f"provider-call:{label}-site-metadata-denial")
        if _is_provider_unavailable(response) and response.status not in {403, 404}:
            return _blocked(f"{label} site denial could not be observed.", trace, **common)
        if response.status == 404:
            # The ignored fixture separately records that the site was verified to exist.
            pass
        elif response.status == 403:
            pass
        elif response.status == 200:
            return _failed(f"{label} site returned success outside the allowed boundary.", trace, **common)
        else:
            return _failed(f"{label} site returned an unexpected denial status.", trace, **common)

    drive_segment = urllib.parse.quote(config.document_drive_id, safe="")
    site_segment = urllib.parse.quote(config.allowed_site_id, safe=",")
    drive_request = _graph_request(
        f"/sites/{site_segment}/drives?%24select=id,driveType",
        token,
    )
    drive_response = transport(drive_request, REQUEST_TIMEOUT_SECONDS, MAX_RESPONSE_BYTES)
    trace.append("provider-call:allowed-site-document-libraries")
    if _is_provider_unavailable(drive_response):
        return _blocked("Allowed-site document library binding could not be verified.", trace, **common)
    if drive_response.status != 200:
        return _failed("Allowed-site document library lookup returned an unexpected status.", trace, **common)
    drives_payload = _parse_json(drive_response)
    drives = drives_payload.get("value") if isinstance(drives_payload, dict) else None
    if (
        not isinstance(drives, list)
        or drives_payload.get("@odata.nextLink") is not None
        or not any(
            isinstance(item, dict)
            and item.get("id") == config.document_drive_id
            and item.get("driveType") == "documentLibrary"
            for item in drives
        )
    ):
        return _blocked("The bound Client A drive was not verified inside the allowed site.", trace, **common)

    delta_query = urllib.parse.urlencode(
        {"token": "latest", "$select": "id,name,size,deleted"}
    )
    initial_delta = transport(
        _graph_request(
            f"/drives/{drive_segment}/root/delta?{delta_query}",
            token,
        ),
        REQUEST_TIMEOUT_SECONDS,
        MAX_DELTA_RESPONSE_BYTES,
    )
    trace.append("provider-call:delta-initial-cursor")
    if _is_provider_unavailable(initial_delta):
        return _blocked(
            "The initial SharePoint delta cursor could not be observed.",
            trace,
            delta_reconciliation_status="BLOCKED",
            **common,
        )
    if initial_delta.status != 200:
        return _failed(
            "The initial SharePoint delta cursor returned an unexpected status.",
            trace,
            delta_reconciliation_status="FAIL",
            **common,
        )
    initial_payload = _parse_json(initial_delta)
    delta_link = initial_payload.get("@odata.deltaLink") if isinstance(initial_payload, dict) else None
    if (
        not isinstance(initial_payload, dict)
        or initial_payload.get("value") != []
        or initial_payload.get("@odata.nextLink") is not None
        or not _valid_delta_link(delta_link, config.document_drive_id)
    ):
        return _failed(
            "The initial SharePoint delta response did not provide the expected empty baseline cursor.",
            trace,
            delta_reconciliation_status="FAIL",
            **common,
        )

    unique_name = f"p0-05-{uuid.uuid4().hex}.txt"
    encoded_name = urllib.parse.quote(unique_name, safe="")
    conflict_query = urllib.parse.urlencode(
        {"@microsoft.graph.conflictBehavior": "fail"}
    )
    upload_path = (
        f"/drives/{drive_segment}/root:/{encoded_name}:/content?{conflict_query}"
    )
    create_response = transport(
        _graph_request(
            upload_path,
            token,
            method="PUT",
            body=ORIGINAL_BYTES,
            content_type="text/plain",
        ),
        REQUEST_TIMEOUT_SECONDS,
        MAX_RESPONSE_BYTES,
    )
    trace.append("provider-call:create-synthetic-file")
    if create_response.error is not None or create_response.status is None:
        return _blocked(
            "Synthetic file creation outcome is unknown; no automatic retry was attempted.",
            trace + ["write-retry:none"],
            **common,
        )
    if create_response.status != 201:
        if create_response.status in {401, 403, 404, 409, 429} or create_response.status >= 500:
            return _blocked(
                "Synthetic file creation was not confirmed; inspect the provider before retrying.",
                trace + ["write-retry:none"],
                **common,
            )
        return _failed("Synthetic file creation returned an unexpected status.", trace, **common)
    created = _parse_json(create_response)
    item_id = created.get("id") if isinstance(created, dict) else None
    if (
        not isinstance(item_id, str)
        or not GRAPH_ID_RE.fullmatch(item_id)
        or created.get("name") != unique_name
        or created.get("size") != len(ORIGINAL_BYTES)
    ):
        return _blocked(
            "Graph accepted the upload but did not return the expected item receipt; do not retry.",
            trace + ["write-retry:none"],
            **common,
        )
    item_segment = urllib.parse.quote(item_id, safe="")
    item_path = f"/drives/{drive_segment}/items/{item_segment}"
    content_path = f"{item_path}/content"

    original_readback, read_error = _read_content(content_path, token, transport)
    trace.append("provider-call:verify-original-bytes")
    if read_error is not None:
        return _blocked(read_error, trace, **common)
    if original_readback != ORIGINAL_BYTES:
        return _failed("Provider readback differs from the deterministic original bytes.", trace, **common)

    update_response = transport(
        _graph_request(
            content_path,
            token,
            method="PUT",
            body=UPDATED_BYTES,
            content_type="text/plain",
        ),
        REQUEST_TIMEOUT_SECONDS,
        MAX_RESPONSE_BYTES,
    )
    trace.append("provider-call:edit-working-file")
    if update_response.error is not None or update_response.status is None:
        return _blocked(
            "Working-file edit outcome is unknown; no automatic retry was attempted.",
            trace + ["write-retry:none"],
            **common,
        )
    if update_response.status not in {200, 201}:
        if update_response.status in {401, 403, 404, 409, 429} or update_response.status >= 500:
            return _blocked(
                "Working-file edit was not confirmed; inspect the provider before retrying.",
                trace + ["write-retry:none"],
                **common,
            )
        return _failed("Working-file edit returned an unexpected status.", trace, **common)
    updated_item = _parse_json(update_response)
    if not isinstance(updated_item, dict) or updated_item.get("id") != item_id:
        return _blocked(
            "Graph accepted the edit but did not confirm the same item identity.",
            trace + ["write-retry:none"],
            **common,
        )

    current_readback, read_error = _read_content(content_path, token, transport)
    trace.append("provider-call:verify-updated-bytes")
    if read_error is not None:
        return _blocked(read_error, trace, **common)
    if current_readback != UPDATED_BYTES:
        return _failed("Provider current-file readback differs from the edited bytes.", trace, **common)

    versions_request = _graph_request(
        f"{item_path}/versions?%24select=id,size",
        token,
    )
    versions_response = transport(versions_request, REQUEST_TIMEOUT_SECONDS, MAX_RESPONSE_BYTES)
    trace.append("provider-call:list-saved-versions")
    if _is_provider_unavailable(versions_response):
        return _blocked("Saved-version metadata could not be observed.", trace, **common)
    if versions_response.status != 200:
        return _failed("Saved-version metadata returned an unexpected status.", trace, **common)
    versions_payload = _parse_json(versions_response)
    versions = versions_payload.get("value") if isinstance(versions_payload, dict) else None
    if (
        not isinstance(versions, list)
        or versions_payload.get("@odata.nextLink") is not None
    ):
        return _blocked("Saved-version list was invalid or exceeded the bounded P0 page.", trace, **common)
    candidates = [
        item
        for item in versions
        if isinstance(item, dict)
        and item.get("size") == len(ORIGINAL_BYTES)
        and isinstance(item.get("id"), str)
        and GRAPH_ID_RE.fullmatch(item["id"])
    ]
    if not candidates:
        return _blocked(
            "The library did not expose a saved version matching the original bytes; versioning remains unverified.",
            trace,
            **common,
        )
    if len(candidates) > MAX_VERSION_CANDIDATES:
        return _blocked("Saved-version candidates exceeded the bounded P0 limit.", trace, **common)

    original_digest = hashlib.sha256(ORIGINAL_BYTES).hexdigest()
    snapshot_digest: str | None = None
    snapshot_version_id: str | None = None
    for version in candidates:
        version_segment = urllib.parse.quote(version["id"], safe="")
        version_content_path = f"{item_path}/versions/{version_segment}/content"
        snapshot_readback, read_error = _read_content(
            version_content_path,
            token,
            transport,
        )
        trace.append("provider-call:read-saved-version")
        if read_error is not None:
            return _blocked(read_error, trace, **common)
        assert snapshot_readback is not None
        candidate_digest = hashlib.sha256(snapshot_readback).hexdigest()
        if candidate_digest == original_digest and snapshot_readback == ORIGINAL_BYTES:
            snapshot_digest = candidate_digest
            snapshot_version_id = version["id"]
            break

    if snapshot_digest is None or snapshot_version_id is None:
        return _failed("No saved provider version reconstructed the exact original bytes.", trace, **common)

    snapshot_version_segment = urllib.parse.quote(snapshot_version_id, safe="")
    snapshot_version_path = f"{item_path}/versions/{snapshot_version_segment}/content"
    second_update = transport(
        _graph_request(
            content_path,
            token,
            method="PUT",
            body=FINAL_BYTES,
            content_type="text/plain",
        ),
        REQUEST_TIMEOUT_SECONDS,
        MAX_RESPONSE_BYTES,
    )
    trace.append("provider-call:edit-after-snapshot")
    if second_update.error is not None or second_update.status is None:
        return _blocked(
            "Post-snapshot working-file edit outcome is unknown; no automatic retry was attempted.",
            trace + ["write-retry:none"],
            **common,
        )
    if second_update.status not in {200, 201}:
        if second_update.status in {401, 403, 404, 409, 429} or second_update.status >= 500:
            return _blocked(
                "Post-snapshot working-file edit was not confirmed; inspect the provider before retrying.",
                trace + ["write-retry:none"],
                **common,
            )
        return _failed("Post-snapshot working-file edit returned an unexpected status.", trace, **common)
    second_updated_item = _parse_json(second_update)
    if not isinstance(second_updated_item, dict) or second_updated_item.get("id") != item_id:
        return _blocked(
            "Graph accepted the post-snapshot edit but did not confirm the same item identity.",
            trace + ["write-retry:none"],
            **common,
        )

    final_readback, read_error = _read_content(content_path, token, transport)
    trace.append("provider-call:verify-final-working-bytes")
    if read_error is not None:
        return _blocked(read_error, trace, **common)
    if final_readback != FINAL_BYTES:
        return _failed("Provider current-file readback differs from the post-snapshot working bytes.", trace, **common)

    preserved_snapshot, read_error = _read_content(snapshot_version_path, token, transport)
    trace.append("provider-call:reverify-saved-version-after-edit")
    if read_error is not None:
        return _blocked(read_error, trace, **common)
    if preserved_snapshot != ORIGINAL_BYTES:
        return _failed("The saved snapshot changed after the working file was edited again.", trace, **common)

    metadata_status, metadata_outcome, metadata_trace = _update_synthetic_title_metadata(
        site_id=config.allowed_site_id,
        drive_id=config.document_drive_id,
        item_id=item_id,
        title_value=f"STE AuditSphere P0-05 {uuid.uuid4().hex[:16]}",
        token=token,
        transport=transport,
    )
    trace.extend(metadata_trace)
    if metadata_status == "BLOCKED":
        return _blocked(
            metadata_outcome,
            trace,
            metadata_update_status=metadata_status,
            **common,
        )
    if metadata_status == "FAIL":
        return _failed(
            metadata_outcome,
            trace,
            metadata_update_status=metadata_status,
            **common,
        )
    if metadata_status != "LIVE_PASS":
        return _failed(
            "Synthetic metadata update returned an unsupported result state.",
            trace,
            metadata_update_status="FAIL",
            **common,
        )

    preserved_snapshot, read_error = _read_content(snapshot_version_path, token, transport)
    trace.append("provider-call:reverify-saved-version-after-metadata-update")
    if read_error is not None:
        return _blocked(read_error, trace, metadata_update_status=metadata_status, **common)
    if preserved_snapshot != ORIGINAL_BYTES:
        return _failed(
            "The saved snapshot changed after synthetic metadata was updated.",
            trace,
            metadata_update_status=metadata_status,
            **common,
        )

    synthetic_stem = unique_name[:-4]
    destination_folder_name = f"{synthetic_stem}-destination"
    renamed_file_name = f"{synthetic_stem}-renamed.txt"
    folder_response = transport(
        _graph_request(
            f"/drives/{drive_segment}/root/children",
            token,
            method="POST",
            body=json.dumps(
                {
                    "name": destination_folder_name,
                    "folder": {},
                    "@microsoft.graph.conflictBehavior": "fail",
                }
            ).encode("utf-8"),
            content_type="application/json",
        ),
        REQUEST_TIMEOUT_SECONDS,
        MAX_RESPONSE_BYTES,
    )
    trace.append("provider-call:create-synthetic-destination-folder")
    if folder_response.error is not None or folder_response.status is None:
        return _blocked(
            "Synthetic destination-folder creation outcome is unknown; no automatic retry was attempted.",
            trace + ["write-retry:none"],
            metadata_update_status=metadata_status,
            **common,
        )
    if folder_response.status != 201:
        if folder_response.status in {401, 403, 404, 409, 429} or folder_response.status >= 500:
            return _blocked(
                "Synthetic destination-folder creation was not confirmed; inspect the provider before retrying.",
                trace + ["write-retry:none"],
                metadata_update_status=metadata_status,
                **common,
            )
        return _failed("Synthetic destination-folder creation returned an unexpected status.", trace, metadata_update_status=metadata_status, **common)
    folder = _parse_json(folder_response)
    folder_id = folder.get("id") if isinstance(folder, dict) else None
    if (
        not isinstance(folder_id, str)
        or not GRAPH_ID_RE.fullmatch(folder_id)
        or folder.get("name") != destination_folder_name
        or not isinstance(folder.get("folder"), dict)
    ):
        return _blocked(
            "Graph accepted destination-folder creation but did not return the expected receipt; do not retry.",
            trace + ["write-retry:none"],
            metadata_update_status=metadata_status,
            **common,
        )

    move_response = transport(
        _graph_request(
            item_path,
            token,
            method="PATCH",
            body=json.dumps(
                {
                    "name": renamed_file_name,
                    "parentReference": {"id": folder_id},
                }
            ).encode("utf-8"),
            content_type="application/json",
        ),
        REQUEST_TIMEOUT_SECONDS,
        MAX_RESPONSE_BYTES,
    )
    trace.append("provider-call:rename-and-move-synthetic-file")
    if move_response.error is not None or move_response.status is None:
        return _blocked(
            "Synthetic-file rename/move outcome is unknown; no automatic retry was attempted.",
            trace + ["write-retry:none"],
            metadata_update_status=metadata_status,
            **common,
        )
    if move_response.status != 200:
        if move_response.status in {401, 403, 404, 409, 429} or move_response.status >= 500:
            return _blocked(
                "Synthetic-file rename/move was not confirmed; inspect the provider before retrying.",
                trace + ["write-retry:none"],
                metadata_update_status=metadata_status,
                **common,
            )
        return _failed("Synthetic-file rename/move returned an unexpected status.", trace, metadata_update_status=metadata_status, **common)
    moved_item = _parse_json(move_response)
    moved_parent = moved_item.get("parentReference") if isinstance(moved_item, dict) else None
    if (
        not isinstance(moved_item, dict)
        or moved_item.get("id") != item_id
        or moved_item.get("name") != renamed_file_name
        or not isinstance(moved_parent, dict)
        or moved_parent.get("id") != folder_id
    ):
        return _blocked(
            "Graph accepted the rename/move but did not confirm the expected item identity and parent.",
            trace + ["write-retry:none"],
            metadata_update_status=metadata_status,
            **common,
        )

    metadata_response = transport(
        _graph_request(
            f"{item_path}?%24select=id,name,parentReference",
            token,
        ),
        REQUEST_TIMEOUT_SECONDS,
        MAX_RESPONSE_BYTES,
    )
    trace.append("provider-call:verify-renamed-moved-metadata")
    if _is_provider_unavailable(metadata_response):
        return _blocked("Renamed/moved item metadata could not be independently read back.", trace, metadata_update_status=metadata_status, **common)
    if metadata_response.status != 200:
        return _failed("Renamed/moved item metadata returned an unexpected status.", trace, metadata_update_status=metadata_status, **common)
    current_metadata = _parse_json(metadata_response)
    current_parent = current_metadata.get("parentReference") if isinstance(current_metadata, dict) else None
    if (
        not isinstance(current_metadata, dict)
        or current_metadata.get("id") != item_id
        or current_metadata.get("name") != renamed_file_name
        or not isinstance(current_parent, dict)
        or current_parent.get("id") != folder_id
    ):
        return _failed("Renamed/moved item metadata did not match the synthetic target and destination.", trace, metadata_update_status=metadata_status, **common)

    moved_content, read_error = _read_content(content_path, token, transport)
    trace.append("provider-call:verify-content-after-move")
    if read_error is not None:
        return _blocked(read_error, trace, metadata_update_status=metadata_status, **common)
    if moved_content != FINAL_BYTES:
        return _failed("The final working bytes changed during the rename/move operation.", trace, metadata_update_status=metadata_status, **common)

    delta_status, delta_outcome, delta_trace = _reconcile_delta(
        delta_link=delta_link,
        drive_id=config.document_drive_id,
        item_id=item_id,
        item_name=renamed_file_name,
        item_size=len(FINAL_BYTES),
        token=token,
        transport=transport,
    )
    trace.extend(delta_trace)
    if delta_status == "BLOCKED":
        return _blocked(
            delta_outcome,
            trace,
            metadata_update_status=metadata_status,
            delta_reconciliation_status=delta_status,
            **common,
        )
    if delta_status == "FAIL":
        return _failed(
            delta_outcome,
            trace,
            metadata_update_status=metadata_status,
            delta_reconciliation_status=delta_status,
            **common,
        )
    if delta_status != "LIVE_PASS":
        return _failed(
            "Delta reconciliation returned an unsupported result state.",
            trace,
            metadata_update_status=metadata_status,
            delta_reconciliation_status="FAIL",
            **common,
        )

    return _success(
        trace,
        current_sha256=hashlib.sha256(FINAL_BYTES).hexdigest(),
        snapshot_sha256=snapshot_digest,
        metadata_update_status=metadata_status,
        delta_reconciliation_status=delta_status,
    )


if __name__ == "__main__":
    result = run_probe()
    print(json.dumps(result, indent=2, sort_keys=True))
