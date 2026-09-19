"""Read-only Entra subject-mapping subprobe for WBS-05 P0-02.

This probe verifies only delegated Microsoft Graph /me identity bindings. It
does not establish Frappe authorization, SharePoint isolation, disabled-user
revocation, UPN history, or wrong-tenant behavior; the aggregate P0-02 suite
therefore remains BLOCKED after a successful subprobe.
"""

from __future__ import annotations

import base64
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
CONFIG_PATH = ROOT / ".local" / "p0" / "identity-live.json"
GRAPH_ORIGIN = "https://graph.microsoft.com"
GRAPH_BASE = f"{GRAPH_ORIGIN}/v1.0"
GRAPH_RESOURCE_ID = "00000003-0000-0000-c000-000000000000"
STANDARD_OIDC_SCOPES = frozenset({"openid", "profile", "email"})
ALLOWED_DELEGATED_SCOPES = frozenset({"user.read", "sites.selected"})
REQUIRED_IDENTITY_SCOPE = "user.read"
MAX_CONFIG_BYTES = 16 * 1024
MAX_TOKEN_BYTES = 64 * 1024
MAX_RESPONSE_BYTES = 64 * 1024
REQUEST_TIMEOUT_SECONDS = 15
REQUIRED_FIXTURES = ("staff", "client_x", "client_y")
TOKEN_ENV = {
    "staff": "AUDIT_P0_IDENTITY_STAFF_TOKEN",
    "client_x": "AUDIT_P0_IDENTITY_CLIENT_X_TOKEN",
    "client_y": "AUDIT_P0_IDENTITY_CLIENT_Y_TOKEN",
}
GUID_RE = re.compile(r"^[0-9a-fA-F-]{36}$")


@dataclass(frozen=True)
class Fixture:
    key: str
    object_id: str
    user_principal_name: str


@dataclass(frozen=True)
class ProbeConfig:
    tenant_id: str
    client_id: str
    permission_names: tuple[str, ...]
    fixtures: tuple[Fixture, ...]


@dataclass(frozen=True)
class Response:
    status: int | None
    body: bytes
    error: str | None = None


Transport = Callable[[urllib.request.Request, float], Response]


class ConfigError(ValueError):
    """The ignored private identity fixture is absent or invalid."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


def _guid(value: object, field: str) -> str:
    if not isinstance(value, str) or not GUID_RE.fullmatch(value):
        raise ConfigError(f"{field} must be a GUID")
    try:
        return str(uuid.UUID(value))
    except ValueError as error:
        raise ConfigError(f"{field} must be a GUID") from error


def parse_config(value: object) -> ProbeConfig:
    if not isinstance(value, dict):
        raise ConfigError("configuration must be a JSON object")
    expected_keys = {
        "schema",
        "environment",
        "tenant_id",
        "client_id",
        "auth_mode",
        "permission_names",
        "fixtures",
    }
    if set(value) != expected_keys:
        raise ConfigError("configuration fields do not match the P0-02 contract")
    if value.get("schema") != "steauditsphereops/p0-identity-live@1":
        raise ConfigError("configuration schema is not supported")
    if value.get("environment") != "NONPRODUCTION":
        raise ConfigError("only an explicitly configured non-production tenant is allowed")
    tenant_id = _guid(value.get("tenant_id"), "tenant_id")
    client_id = _guid(value.get("client_id"), "client_id")
    if value.get("auth_mode") != "delegated":
        raise ConfigError("P0-02 subject checks require the owner-selected delegated identity")
    permission_names = value.get("permission_names")
    if (
        not isinstance(permission_names, list)
        or not permission_names
        or any(
            not isinstance(name, str)
            or name.casefold() not in ALLOWED_DELEGATED_SCOPES
            for name in permission_names
        )
        or len({name.casefold() for name in permission_names}) != len(permission_names)
        or REQUIRED_IDENTITY_SCOPE not in {name.casefold() for name in permission_names}
    ):
        raise ConfigError(
            "P0-02 subject checks require User.Read and only the approved delegated scope set"
        )

    bindings = value.get("fixtures")
    if not isinstance(bindings, dict) or set(bindings) != set(REQUIRED_FIXTURES):
        raise ConfigError("fixtures must contain exactly staff, client_x, and client_y")
    fixtures: list[Fixture] = []
    for key in REQUIRED_FIXTURES:
        item = bindings[key]
        if not isinstance(item, dict) or set(item) != {"object_id", "user_principal_name"}:
            raise ConfigError(f"{key} fixture must contain only object_id and user_principal_name")
        object_id = _guid(item.get("object_id"), f"{key}.object_id")
        user_principal_name = item.get("user_principal_name")
        if (
            not isinstance(user_principal_name, str)
            or not user_principal_name
            or len(user_principal_name) > 256
            or any(character.isspace() for character in user_principal_name)
            or "@" not in user_principal_name
        ):
            raise ConfigError(f"{key}.user_principal_name must be a valid fixture UPN")
        fixtures.append(Fixture(key, object_id, user_principal_name))
    if len({fixture.object_id for fixture in fixtures}) != len(fixtures):
        raise ConfigError("staff, Client X, and Client Y must use distinct Entra object IDs")
    if len({fixture.user_principal_name.casefold() for fixture in fixtures}) != len(fixtures):
        raise ConfigError("staff, Client X, and Client Y must use distinct current UPNs")

    return ProbeConfig(tenant_id, client_id, tuple(permission_names), tuple(fixtures))


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
        raise ConfigError("private identity configuration is missing or outside .local") from error
    if not resolved_path.is_file() or resolved_path.stat().st_size > MAX_CONFIG_BYTES:
        raise ConfigError("private identity configuration is missing or too large")
    try:
        value = json.loads(resolved_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ConfigError("private identity configuration is unreadable or invalid JSON") from error
    return parse_config(value)


def _token_claims(token: str) -> dict[str, object] | None:
    if len(token) > MAX_TOKEN_BYTES:
        return None
    parts = token.split(".")
    if len(parts) != 3 or not parts[1]:
        return None
    try:
        encoded = parts[1].encode("ascii")
        payload = base64.b64decode(encoded + b"=" * (-len(encoded) % 4), altchars=b"-_", validate=True)
        claims = json.loads(payload.decode("utf-8"))
    except (UnicodeEncodeError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return claims if isinstance(claims, dict) else None


def _token_matches_fixture(token: str, config: ProbeConfig, fixture: Fixture, now: int) -> bool:
    claims = _token_claims(token)
    if claims is None:
        return False
    try:
        token_tenant = _guid(claims.get("tid"), "token tid")
        token_subject = _guid(claims.get("oid"), "token oid")
    except ConfigError:
        return False
    audience = claims.get("aud")
    client_id = claims.get("appid", claims.get("azp"))
    issuer = claims.get("iss")
    scopes = claims.get("scp")
    scope_names = scopes.split() if isinstance(scopes, str) else []
    normalized_scopes = {name.casefold() for name in scope_names}
    graph_scopes = normalized_scopes - STANDARD_OIDC_SCOPES
    expiry = claims.get("exp")
    not_before = claims.get("nbf", 0)
    identity_type = claims.get("idtyp")
    return (
        token_tenant == config.tenant_id
        and token_subject == fixture.object_id
        and isinstance(audience, str)
        and audience.casefold() in {GRAPH_ORIGIN.casefold(), GRAPH_RESOURCE_ID.casefold()}
        and isinstance(client_id, str)
        and client_id.casefold() == config.client_id.casefold()
        and isinstance(issuer, str)
        and issuer.casefold() in {
            f"https://login.microsoftonline.com/{config.tenant_id}/v2.0".casefold(),
            f"https://sts.windows.net/{config.tenant_id}/".casefold(),
        }
        # Microsoft adds standard OIDC identity scopes to delegated tokens.
        # They do not grant additional Graph API permissions. The approved
        # identity fixture may carry Sites.Selected as well because the same
        # P0 app is used for the separately bounded isolation proof; reject
        # every other scope.
        and graph_scopes == {name.casefold() for name in config.permission_names}
        and not claims.get("roles")
        and (identity_type is None or identity_type == "user")
        and type(expiry) is int
        and expiry > now
        and type(not_before) is int
        and not_before <= now
    )


def _graph_get(request: urllib.request.Request, timeout: float) -> Response:
    opener = urllib.request.build_opener(_NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
            if len(body) > MAX_RESPONSE_BYTES:
                return Response(int(response.status), b"", "response_too_large")
            return Response(int(response.status), body)
    except urllib.error.HTTPError as error:
        return Response(int(error.code), b"")
    except (urllib.error.URLError, TimeoutError, socket.timeout, OSError) as error:
        return Response(None, b"", type(error).__name__)


def _me_request(token: str) -> urllib.request.Request:
    query = urllib.parse.urlencode({"$select": "id,userPrincipalName"})
    return urllib.request.Request(
        f"{GRAPH_BASE}/me?{query}",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "client-request-id": str(uuid.uuid4()),
            "return-client-request-id": "true",
        },
        method="GET",
    )


def _base_result(status: str, outcome: str, trace: list[str], **fields: object) -> dict[str, object]:
    return {
        "status": status,
        "outcome": outcome,
        "trace": trace,
        "entra_subject_mapping_status": "BLOCKED",
        "frappe_authorization_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
        "email_change_reuse_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
        "disabled_revoked_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
        "wrong_tenant_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
        "sharepoint_user_access_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
        **fields,
    }


def run_probe(
    *,
    config: ProbeConfig | None = None,
    tokens: Mapping[str, str] | None = None,
    transport: Transport = _graph_get,
    now: int | None = None,
) -> dict[str, object]:
    trace = ["executor:entra-identity-read-only-v1"]
    token_values = (
        {key: os.environ.pop(environment_name, None) for key, environment_name in TOKEN_ENV.items()}
        if tokens is None
        else {key: tokens.get(key) for key in REQUIRED_FIXTURES}
    )
    if config is None:
        try:
            config = load_local_config()
        except ConfigError:
            return _base_result(
                "BLOCKED",
                "P0-02 requires an approved identity fixture at .local/p0/identity-live.json; no Graph request was sent.",
                trace + ["provider-call:none"],
            )

    supplied_tokens: dict[str, str] = {}
    for fixture in config.fixtures:
        token = token_values.get(fixture.key)
        if isinstance(token, str):
            token = token.strip()
            if token.lower().startswith("bearer "):
                token = token[7:].strip()
        else:
            token = ""
        if not token or any(character.isspace() for character in token):
            return _base_result(
                "BLOCKED",
                "P0-02 requires a short-lived delegated token for each configured member fixture; no Graph request was sent.",
                trace + ["provider-call:none"],
            )
        supplied_tokens[fixture.key] = token

    timestamp = int(time.time()) if now is None else now
    for fixture in config.fixtures:
        if not _token_matches_fixture(supplied_tokens[fixture.key], config, fixture, timestamp):
            return _base_result(
                "BLOCKED",
                "A delegated token did not match the approved tenant, app, scope set, or configured subject; no Graph request was sent.",
                trace + ["provider-call:none"],
            )

    observed: dict[str, str] = {}
    for fixture in config.fixtures:
        response = transport(_me_request(supplied_tokens[fixture.key]), REQUEST_TIMEOUT_SECONDS)
        trace.append(f"provider-call:entra-me:{fixture.key}")
        if response.error is not None or response.status in {None, 401, 403, 404, 408, 429} or (response.status or 0) >= 500:
            return _base_result(
                "BLOCKED",
                "P0-02 Entra identity could not be observed for every configured fixture; review the private provider result without broadening consent.",
                trace,
                entra_http_statuses=observed | {fixture.key: response.status or 0},
            )
        if response.status != 200:
            return _base_result(
                "FAIL",
                "P0-02 Entra identity returned an unexpected HTTP status.",
                trace,
                entra_subject_mapping_status="FAIL",
                entra_http_statuses=observed | {fixture.key: response.status or 0},
            )
        try:
            payload = json.loads(response.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return _base_result(
                "FAIL",
                "P0-02 Entra identity response was not valid JSON.",
                trace,
                entra_subject_mapping_status="FAIL",
            )
        if not isinstance(payload, dict):
            return _base_result(
                "FAIL",
                "P0-02 Entra identity response had an invalid shape.",
                trace,
                entra_subject_mapping_status="FAIL",
            )
        try:
            actual_object_id = _guid(payload.get("id"), "Graph /me id")
        except ConfigError:
            return _base_result(
                "FAIL",
                "P0-02 Entra identity response omitted a valid object ID.",
                trace,
                entra_subject_mapping_status="FAIL",
            )
        actual_upn = payload.get("userPrincipalName")
        if (
            actual_object_id != fixture.object_id
            or not isinstance(actual_upn, str)
            or actual_upn.casefold() != fixture.user_principal_name.casefold()
        ):
            return _base_result(
                "FAIL",
                "P0-02 Entra /me identity did not match the private fixture binding.",
                trace,
                entra_subject_mapping_status="FAIL",
                entra_http_statuses=observed | {fixture.key: 200},
            )
        observed[fixture.key] = "MATCH"

    return _base_result(
        "BLOCKED",
        "P0-02 Entra /me subject bindings passed for staff, Client X, and Client Y; Frappe authorization, email change/reuse, disabled/revoked, wrong-tenant, and user-level SharePoint proofs remain incomplete.",
        trace,
        entra_subject_mapping_status="LIVE_PASS",
        entra_fixture_results=observed,
        entra_http_statuses={key: 200 for key in observed},
    )
