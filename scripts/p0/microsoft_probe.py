"""Read-only Microsoft Graph probe for the WBS-05 P0-04 capability row.

This is a proof helper, not a production integration. It only reads the stable
site identifiers supplied in ignored local configuration and never discovers
or accepts a caller-supplied Graph URL.
"""

from __future__ import annotations

import json
import os
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / ".local" / "p0" / "microsoft-live.json"
TOKEN_ENV = "AUDIT_P0_GRAPH_ACCESS_TOKEN"
GRAPH_API_VERSION = "v1.0"
GRAPH_ORIGIN = "https://graph.microsoft.com"
GRAPH_BASE = f"{GRAPH_ORIGIN}/{GRAPH_API_VERSION}"
MAX_CONFIG_BYTES = 16 * 1024
MAX_RESPONSE_BYTES = 64 * 1024
REQUEST_TIMEOUT_SECONDS = 15
SITE_ID_RE = re.compile(r"^([A-Za-z0-9.-]+),([^,]+),([^,]+)$")
PERMISSION_NAME_RE = re.compile(r"^(?:[A-Za-z][A-Za-z0-9._-]{0,99}|https://graph\.microsoft\.com/\.default)$")


@dataclass(frozen=True)
class ProbeConfig:
    tenant_id: str
    auth_mode: str
    permission_names: tuple[str, ...]
    allowed_site_id: str
    unrelated_site_id: str


Transport = Callable[[urllib.request.Request, float, bool], tuple[int | None, bytes, str | None]]


class ConfigError(ValueError):
    """The private local fixture configuration is absent or invalid."""


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
        raise ConfigError(f"{field_name} must bind to a SharePoint Online host")
    try:
        uuid.UUID(site_guid)
        uuid.UUID(web_guid)
    except ValueError as error:
        raise ConfigError(f"{field_name} contains an invalid site identifier") from error
    return value, host.casefold()


def parse_config(value: object) -> ProbeConfig:
    if not isinstance(value, dict):
        raise ConfigError("configuration must be a JSON object")

    expected_keys = {
        "schema",
        "environment",
        "tenant_id",
        "auth_mode",
        "permission_names",
        "unrelated_site_exists_verified",
        "site_bindings",
    }
    if set(value) != expected_keys:
        raise ConfigError("configuration fields do not match the P0-04 contract")
    if value.get("schema") != "steauditsphereops/p0-microsoft-live@1":
        raise ConfigError("configuration schema is not supported")
    if value.get("environment") != "NONPRODUCTION":
        raise ConfigError("only an explicitly configured non-production tenant is allowed")
    try:
        tenant_id = str(uuid.UUID(value["tenant_id"]))
    except (TypeError, ValueError, KeyError) as error:
        raise ConfigError("tenant_id must be a GUID") from error

    auth_mode = value.get("auth_mode")
    if not isinstance(auth_mode, str) or auth_mode not in {"application", "delegated"}:
        raise ConfigError("auth_mode must be explicitly selected as application or delegated")
    permission_names = value.get("permission_names")
    if (
        not isinstance(permission_names, list)
        or not permission_names
        or any(
            not isinstance(item, str)
            or not PERMISSION_NAME_RE.fullmatch(item)
            for item in permission_names
        )
    ):
        raise ConfigError("permission_names must list the owner-approved permission names")
    if len(set(permission_names)) != len(permission_names):
        raise ConfigError("permission_names cannot contain duplicates")
    if value.get("unrelated_site_exists_verified") is not True:
        raise ConfigError("the unrelated-site existence must be verified before a 404 can count as denial")

    bindings = value.get("site_bindings")
    if not isinstance(bindings, dict) or set(bindings) != {"allowed", "unrelated"}:
        raise ConfigError("site_bindings must contain exactly allowed and unrelated IDs")
    allowed_site_id, allowed_host = _validate_site_id(bindings["allowed"], "allowed site")
    unrelated_site_id, unrelated_host = _validate_site_id(bindings["unrelated"], "unrelated site")
    if allowed_site_id == unrelated_site_id:
        raise ConfigError("allowed and unrelated sites must be different")
    if allowed_host != unrelated_host:
        raise ConfigError("the denial fixture must be an unrelated site in the configured tenant")

    return ProbeConfig(
        tenant_id=tenant_id,
        auth_mode=auth_mode,
        permission_names=tuple(permission_names),
        allowed_site_id=allowed_site_id,
        unrelated_site_id=unrelated_site_id,
    )


def load_local_config(path: Path = CONFIG_PATH) -> ProbeConfig:
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


def _graph_get(request: urllib.request.Request, timeout: float, read_body: bool) -> tuple[int | None, bytes, str | None]:
    opener = urllib.request.build_opener(_NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            status = int(response.status)
            body = response.read(MAX_RESPONSE_BYTES + 1) if read_body else b""
            if len(body) > MAX_RESPONSE_BYTES:
                return status, b"", "response_too_large"
            return status, body, None
    except urllib.error.HTTPError as error:
        return int(error.code), b"", None
    except (urllib.error.URLError, TimeoutError, socket.timeout, OSError) as error:
        return None, b"", type(error).__name__


def _site_metadata_request(site_id: str, token: str) -> urllib.request.Request:
    site_segment = urllib.parse.quote(site_id, safe=",")
    request_id = str(uuid.uuid4())
    return urllib.request.Request(
        f"{GRAPH_BASE}/sites/{site_segment}?%24select=id",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "client-request-id": request_id,
            "return-client-request-id": "true",
        },
        method="GET",
    )


def _blocked(outcome: str, trace: list[str], **fields: object) -> dict[str, object]:
    return {"status": "BLOCKED", "outcome": outcome, "trace": trace, **fields}


def run_probe(
    *,
    config: ProbeConfig | None = None,
    token: str | None = None,
    transport: Transport = _graph_get,
) -> dict[str, object]:
    trace: list[str] = ["executor:microsoft-read-only-v1"]
    if token is None:
        token = os.environ.pop(TOKEN_ENV, None)
    if config is None:
        try:
            config = load_local_config()
        except ConfigError:
            return _blocked(
                "P0-04 requires an approved non-production binding file at .local/p0/microsoft-live.json; no Graph request was sent.",
                trace + ["provider-call:none"],
            )
    token = token.strip() if isinstance(token, str) else ""
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    if not token or len(token) > 64 * 1024 or any(character.isspace() for character in token):
        return _blocked(
            f"P0-04 requires a short-lived {TOKEN_ENV} value; no Graph request was sent.",
            trace + ["provider-call:none"],
        )

    common = {
        "api_version": GRAPH_API_VERSION,
        "auth_context": {
            "mode": config.auth_mode,
            "permission_names": list(config.permission_names),
            "source": "private local fixture metadata; requires owner evidence review",
        },
        "tenant_id_configured": True,
        "tenant_verification": "NOT_PROVEN_BY_THIS_PROBE",
        "target_ids": "redacted",
    }

    allowed_request = _site_metadata_request(config.allowed_site_id, token)
    status, body, transport_error = transport(allowed_request, REQUEST_TIMEOUT_SECONDS, True)
    trace.append("provider-call:authorized-site-metadata")
    if transport_error is not None:
        return _blocked("P0-04 Graph metadata request could not be observed; provider outcome is unknown.", trace, **common)
    if status != 200:
        if status in {401, 403, 404, 429} or status is None or status >= 500:
            return _blocked("P0-04 authorized-site metadata was not readable; tenant binding or grant needs review.", trace, **common)
        return {"status": "FAIL", "outcome": "P0-04 authorized-site metadata returned an unexpected HTTP status.", "trace": trace, **common}
    try:
        metadata = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"status": "FAIL", "outcome": "P0-04 authorized-site metadata was not valid JSON.", "trace": trace, **common}
    if not isinstance(metadata, dict) or metadata.get("id") != config.allowed_site_id:
        return {"status": "FAIL", "outcome": "P0-04 Graph returned a different site identity than the trusted binding.", "trace": trace, **common}

    unrelated_request = _site_metadata_request(config.unrelated_site_id, token)
    unrelated_status, _body, transport_error = transport(unrelated_request, REQUEST_TIMEOUT_SECONDS, False)
    trace.append("provider-call:unrelated-site-metadata-denial")
    if transport_error is not None or unrelated_status is None or unrelated_status == 401 or unrelated_status == 429 or unrelated_status >= 500:
        return _blocked("P0-04 unrelated-site denial could not be observed; provider outcome is unknown.", trace, **common)
    if unrelated_status not in {403, 404}:
        if unrelated_status == 200:
            return {
                "status": "FAIL",
                "outcome": "P0-04 unrelated site returned success; the application boundary is broader than expected.",
                "trace": trace,
                "unrelated_http_status": unrelated_status,
                **common,
            }
        return {"status": "FAIL", "outcome": "P0-04 unrelated-site request returned an unexpected HTTP status.", "trace": trace, **common}

    return {
        "status": "LIVE_PASS",
        "outcome": "P0-04 observed selected-site metadata access and unrelated-site metadata denial; this does not prove identity, file, or records behavior.",
        "trace": trace,
        "request_shape": "GET /v1.0/sites/{site-id}?$select=id",
        "authorized_http_status": status,
        "authorized_site_metadata": "READABLE",
        "unrelated_http_status": unrelated_status,
        "unrelated_site_metadata": "DENIED",
        **common,
    }
