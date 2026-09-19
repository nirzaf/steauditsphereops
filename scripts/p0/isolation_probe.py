"""Read-only SharePoint isolation subprobe for WBS-05 P0-03.

The probe is deliberately narrower than the aggregate P0-03 exit.  It checks
site metadata, item metadata, content access, and search visibility for three
configured actor fixtures against client-X, client-Y, and unrelated sites.  A
successful provider pass still reports the aggregate result as ``BLOCKED``
until the Frappe assignment, revocation, and records paths have independently
been observed.

The ignored ``.local/p0/isolation-live.json`` contract is intentionally exact:
it binds a non-production tenant, one app, the ``Sites.Selected`` permission,
three stable site IDs, one deterministic item per site, and the staff/client-X/
client-Y actor mapping.  Tokens are short-lived JWTs supplied through the three
fixture-specific environment variables below.  No request mutates the tenant,
and no response body or identifier is copied to evidence.
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
from typing import Callable


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / ".local" / "p0" / "isolation-live.json"
GRAPH_ORIGIN = "https://graph.microsoft.com"
GRAPH_BASE = f"{GRAPH_ORIGIN}/v1.0"
GRAPH_RESOURCE_ID = "00000003-0000-0000-c000-000000000000"
MAX_CONFIG_BYTES = 24 * 1024
MAX_TOKEN_BYTES = 64 * 1024
MAX_RESPONSE_BYTES = 64 * 1024
REQUEST_TIMEOUT_SECONDS = 15
REQUIRED_FIXTURES = ("staff", "client_x", "client_y")
SITE_KEYS = ("client_x", "client_y", "unrelated")
TOKEN_ENV = {
    "staff": "AUDIT_P0_ISOLATION_STAFF_TOKEN",
    "client_x": "AUDIT_P0_ISOLATION_CLIENT_X_TOKEN",
    "client_y": "AUDIT_P0_ISOLATION_CLIENT_Y_TOKEN",
}
SITE_ID_RE = re.compile(r"^([A-Za-z0-9.-]+),([^,]+),([^,]+)$")
GUID_RE = re.compile(r"^[0-9a-fA-F-]{36}$")
GRAPH_ID_RE = re.compile(r"^[A-Za-z0-9._!~()\-]{1,512}$")
PERMISSION_NAMES = ("Sites.Selected",)
STANDARD_OIDC_SCOPES = frozenset({"openid", "profile", "email"})
# The app requests User.Read to establish the delegated subject. Microsoft
# includes that grant, and the standard OIDC scopes, in the same token as
# Sites.Selected. Keep this allowlist explicit so broader Graph permissions
# still fail closed.
DELEGATED_AUXILIARY_SCOPES = frozenset({"user.read"})


@dataclass(frozen=True)
class SiteBinding:
    key: str
    site_id: str
    exists_verified: bool


@dataclass(frozen=True)
class Resource:
    key: str
    drive_id: str
    item_id: str
    search_term: str


@dataclass(frozen=True)
class Fixture:
    key: str
    object_id: str
    user_principal_name: str
    allowed_site_keys: tuple[str, ...]


@dataclass(frozen=True)
class ProbeConfig:
    tenant_id: str
    client_id: str
    auth_mode: str
    permission_names: tuple[str, ...]
    sites: tuple[SiteBinding, ...]
    resources: tuple[Resource, ...]
    fixtures: tuple[Fixture, ...]


@dataclass(frozen=True)
class Response:
    status: int | None
    body: bytes = b""
    error: str | None = None


Transport = Callable[[urllib.request.Request, float, bool], Response]


class ConfigError(ValueError):
    """The private local isolation fixture is absent or invalid."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


def _guid(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not GUID_RE.fullmatch(value):
        raise ConfigError(f"{field_name} must be a GUID")
    try:
        return str(uuid.UUID(value))
    except ValueError as error:
        raise ConfigError(f"{field_name} must be a GUID") from error


def _site_id(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 512:
        raise ConfigError(f"{field_name} must be a stable Graph site ID")
    match = SITE_ID_RE.fullmatch(value)
    if match is None:
        raise ConfigError(f"{field_name} must use hostname,site-guid,web-guid form")
    host, site_guid, web_guid = match.groups()
    if not host.casefold().endswith(".sharepoint.com"):
        raise ConfigError(f"{field_name} must bind to SharePoint Online")
    try:
        uuid.UUID(site_guid)
        uuid.UUID(web_guid)
    except ValueError as error:
        raise ConfigError(f"{field_name} contains an invalid site identifier") from error
    return value


def _graph_id(value: object, field_name: str) -> str:
    if not isinstance(value, str) or GRAPH_ID_RE.fullmatch(value) is None:
        raise ConfigError(f"{field_name} must be a bounded Graph resource ID")
    return value


def _search_term(value: object, field_name: str) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or len(value) > 256
        or any(ord(character) < 0x20 for character in value)
    ):
        raise ConfigError(f"{field_name} must be a bounded search term")
    return value


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
        "site_bindings",
        "resources",
        "fixtures",
    }
    if set(value) != expected_keys:
        raise ConfigError("configuration fields do not match the P0-03 contract")
    if value.get("schema") != "steauditsphereops/p0-isolation-live@1":
        raise ConfigError("configuration schema is not supported")
    if value.get("environment") != "NONPRODUCTION":
        raise ConfigError("only an explicitly configured non-production tenant is allowed")
    tenant_id = _guid(value.get("tenant_id"), "tenant_id")
    client_id = _guid(value.get("client_id"), "client_id")
    auth_mode = value.get("auth_mode")
    if auth_mode not in {"application", "delegated"}:
        raise ConfigError("auth_mode must be explicitly selected as application or delegated")
    if value.get("permission_names") != list(PERMISSION_NAMES):
        raise ConfigError("P0-03 requires the exact owner-approved Sites.Selected permission")

    raw_sites = value.get("site_bindings")
    if not isinstance(raw_sites, dict) or set(raw_sites) != set(SITE_KEYS):
        raise ConfigError("site_bindings must contain client_x, client_y, and unrelated")
    sites: list[SiteBinding] = []
    site_ids: set[str] = set()
    for key in SITE_KEYS:
        binding = raw_sites[key]
        if not isinstance(binding, dict) or set(binding) != {"site_id", "exists_verified"}:
            raise ConfigError(f"{key} site binding must contain site_id and exists_verified")
        site_id = _site_id(binding.get("site_id"), f"{key}.site_id")
        if binding.get("exists_verified") is not True:
            raise ConfigError(f"{key} site existence must be verified before denial is inferred")
        if site_id in site_ids:
            raise ConfigError("site bindings must identify three distinct sites")
        site_ids.add(site_id)
        sites.append(SiteBinding(key, site_id, True))
    hosts = {SITE_ID_RE.fullmatch(site.site_id).group(1).casefold() for site in sites}
    if len(hosts) != 1:
        raise ConfigError("all site bindings must belong to one SharePoint host")

    raw_resources = value.get("resources")
    if not isinstance(raw_resources, dict) or set(raw_resources) != set(SITE_KEYS):
        raise ConfigError("resources must contain one deterministic item for each site")
    resources: list[Resource] = []
    resource_ids: set[tuple[str, str]] = set()
    for key in SITE_KEYS:
        resource = raw_resources[key]
        if not isinstance(resource, dict) or set(resource) != {"drive_id", "item_id", "search_term"}:
            raise ConfigError(f"{key} resource must contain drive_id, item_id, and search_term")
        drive_id = _graph_id(resource.get("drive_id"), f"{key}.drive_id")
        item_id = _graph_id(resource.get("item_id"), f"{key}.item_id")
        term = _search_term(resource.get("search_term"), f"{key}.search_term")
        if (drive_id, item_id) in resource_ids:
            raise ConfigError("resources must identify three distinct drive items")
        resource_ids.add((drive_id, item_id))
        resources.append(Resource(key, drive_id, item_id, term))

    raw_fixtures = value.get("fixtures")
    if not isinstance(raw_fixtures, dict) or set(raw_fixtures) != set(REQUIRED_FIXTURES):
        raise ConfigError("fixtures must contain exactly staff, client_x, and client_y")
    expected_allowed = {
        "staff": {"client_x", "client_y"},
        "client_x": {"client_x"},
        "client_y": {"client_y"},
    }
    fixtures: list[Fixture] = []
    object_ids: set[str] = set()
    upns: set[str] = set()
    for key in REQUIRED_FIXTURES:
        fixture = raw_fixtures[key]
        if not isinstance(fixture, dict) or set(fixture) != {"object_id", "user_principal_name", "allowed_site_keys"}:
            raise ConfigError(f"{key} fixture fields do not match the P0-03 contract")
        object_id = _guid(fixture.get("object_id"), f"{key}.object_id")
        upn = fixture.get("user_principal_name")
        if (
            not isinstance(upn, str)
            or not upn
            or len(upn) > 256
            or any(character.isspace() for character in upn)
            or "@" not in upn
        ):
            raise ConfigError(f"{key}.user_principal_name must be a valid fixture UPN")
        allowed = fixture.get("allowed_site_keys")
        if not isinstance(allowed, list) or set(allowed) != expected_allowed[key] or len(allowed) != len(set(allowed)):
            raise ConfigError(f"{key}.allowed_site_keys does not match the approved boundary")
        if object_id in object_ids or upn.casefold() in upns:
            raise ConfigError("fixture object IDs and UPNs must be distinct")
        object_ids.add(object_id)
        upns.add(upn.casefold())
        fixtures.append(Fixture(key, object_id, upn, tuple(allowed)))

    return ProbeConfig(
        tenant_id=tenant_id,
        client_id=client_id,
        auth_mode=auth_mode,
        permission_names=PERMISSION_NAMES,
        sites=tuple(sites),
        resources=tuple(resources),
        fixtures=tuple(fixtures),
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


def _token_claims(token: str) -> dict[str, object] | None:
    if len(token) > MAX_TOKEN_BYTES:
        return None
    parts = token.split(".")
    if len(parts) != 3 or not parts[1]:
        return None
    try:
        encoded = parts[1].encode("ascii")
        payload = base64.urlsafe_b64decode(encoded + b"=" * (-len(encoded) % 4))
        claims = json.loads(payload.decode("utf-8"))
    except (UnicodeEncodeError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return claims if isinstance(claims, dict) else None


def _delegated_scope_name(value: str) -> str:
    """Normalize Microsoft Graph scope spellings without widening the proof."""

    normalized = value.casefold()
    graph_prefix = f"{GRAPH_ORIGIN}/".casefold()
    if normalized.startswith(graph_prefix):
        return normalized[len(graph_prefix) :]
    return normalized


def _claims_match(token: str, config: ProbeConfig, fixture: Fixture, now: int) -> bool:
    claims = _token_claims(token)
    if claims is None:
        return False
    try:
        token_tenant = _guid(claims.get("tid"), "token tid")
        expiry = int(claims.get("exp"))
        not_before = int(claims.get("nbf", 0))
    except (ConfigError, TypeError, ValueError):
        return False
    audience = claims.get("aud")
    client_id = claims.get("appid", claims.get("azp"))
    issuer = claims.get("iss")
    common = (
        token_tenant == config.tenant_id
        and isinstance(audience, str)
        and audience.casefold() in {GRAPH_ORIGIN.casefold(), GRAPH_RESOURCE_ID.casefold()}
        and isinstance(client_id, str)
        and client_id.casefold() == config.client_id.casefold()
        and isinstance(issuer, str)
        and issuer.casefold()
        in {
            f"https://login.microsoftonline.com/{config.tenant_id}/v2.0".casefold(),
            f"https://sts.windows.net/{config.tenant_id}/".casefold(),
        }
        and expiry > now
        and not_before <= now
    )
    if not common:
        return False
    if config.auth_mode == "delegated":
        try:
            token_subject = _guid(claims.get("oid"), "token oid")
        except ConfigError:
            return False
        scopes = claims.get("scp")
        scope_names = scopes.split() if isinstance(scopes, str) else []
        normalized_scopes = {
            _delegated_scope_name(scope) for scope in scope_names
        }
        graph_scopes = normalized_scopes - STANDARD_OIDC_SCOPES
        required_scopes = {name.casefold() for name in config.permission_names}
        allowed_scopes = required_scopes | DELEGATED_AUXILIARY_SCOPES
        return (
            token_subject == fixture.object_id
            and required_scopes <= graph_scopes <= allowed_scopes
            and claims.get("idtyp") == "user"
            and "roles" not in claims
        )
    roles = claims.get("roles")
    return (
        set(roles) == set(config.permission_names)
        if isinstance(roles, list) and all(isinstance(role, str) for role in roles)
        else False
    ) and claims.get("idtyp") == "app" and "scp" not in claims


def _graph_request(request: urllib.request.Request, timeout: float, read_body: bool) -> Response:
    opener = urllib.request.build_opener(_NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            status = int(response.status)
            body = response.read(MAX_RESPONSE_BYTES + 1) if read_body else b""
            if len(body) > MAX_RESPONSE_BYTES:
                return Response(status, error="response_too_large")
            return Response(status, body)
    except urllib.error.HTTPError as error:
        return Response(int(error.code))
    except (urllib.error.URLError, TimeoutError, socket.timeout, OSError) as error:
        return Response(None, error=type(error).__name__)


def _headers(token: str, *, content_type: bool = False) -> dict[str, str]:
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "client-request-id": str(uuid.uuid4()),
        "return-client-request-id": "true",
    }
    if content_type:
        headers["Content-Type"] = "application/json"
    return headers


def _site_request(site_id: str, token: str) -> urllib.request.Request:
    site_segment = urllib.parse.quote(site_id, safe=",")
    return urllib.request.Request(
        f"{GRAPH_BASE}/sites/{site_segment}?%24select=id",
        headers=_headers(token),
        method="GET",
    )


def _item_request(resource: Resource, token: str) -> urllib.request.Request:
    drive_segment = urllib.parse.quote(resource.drive_id, safe="")
    item_segment = urllib.parse.quote(resource.item_id, safe="")
    return urllib.request.Request(
        f"{GRAPH_BASE}/drives/{drive_segment}/items/{item_segment}?%24select=id,name,parentReference",
        headers=_headers(token),
        method="GET",
    )


def _content_request(resource: Resource, token: str) -> urllib.request.Request:
    drive_segment = urllib.parse.quote(resource.drive_id, safe="")
    item_segment = urllib.parse.quote(resource.item_id, safe="")
    return urllib.request.Request(
        f"{GRAPH_BASE}/drives/{drive_segment}/items/{item_segment}/content",
        headers=_headers(token),
        method="GET",
    )


def _search_request(resource: Resource, token: str) -> urllib.request.Request:
    body = json.dumps(
        {
            "requests": [
                {
                    "entityTypes": ["driveItem"],
                    "query": {"queryString": resource.search_term},
                    "from": 0,
                    "size": 25,
                }
            ]
        },
        separators=(",", ":"),
    ).encode("utf-8")
    return urllib.request.Request(
        f"{GRAPH_BASE}/search/query",
        data=body,
        headers=_headers(token, content_type=True),
        method="POST",
    )


def _base_fields(config: ProbeConfig, identity_status: str) -> dict[str, object]:
    return {
        "api_version": "v1.0",
        "auth_context": {
            "mode": config.auth_mode,
            "permission_names": list(config.permission_names),
            "source": "private local fixture metadata; requires owner evidence review",
        },
        "tenant_id_configured": True,
        "tenant_verification": "NOT_PROVEN_BY_THIS_PROBE",
        "identity_context_status": identity_status,
        "frappe_authorization_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
        "revocation_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
    }


def _result(
    status: str,
    outcome: str,
    trace: list[str],
    *,
    config: ProbeConfig | None = None,
    identity_status: str = "NOT_RUN_EXTERNAL_PREREQUISITE",
    sharepoint_status: str = "BLOCKED",
) -> dict[str, object]:
    fields: dict[str, object] = {
        "status": status,
        "outcome": outcome,
        "trace": trace,
        "sharepoint_isolation_status": sharepoint_status,
        "frappe_authorization_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
        "revocation_status": "NOT_RUN_EXTERNAL_PREREQUISITE",
    }
    if config is not None:
        fields.update(_base_fields(config, identity_status))
    return fields


def _unknown(response: Response) -> bool:
    return response.error is not None or response.status is None or response.status in {401, 408, 429} or response.status >= 500


def _json_object(response: Response) -> dict[str, object] | None:
    if response.error is not None:
        return None
    try:
        value = json.loads(response.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _contains_id(value: object, item_id: str) -> bool:
    if isinstance(value, dict):
        if value.get("id") == item_id:
            return True
        return any(_contains_id(child, item_id) for child in value.values())
    if isinstance(value, list):
        return any(_contains_id(child, item_id) for child in value)
    return False


def run_probe(
    *,
    config: ProbeConfig | None = None,
    tokens: dict[str, str] | None = None,
    transport: Transport = _graph_request,
    now: int | None = None,
) -> dict[str, object]:
    trace: list[str] = ["executor:sharepoint-isolation-read-only-v1"]
    if tokens is None:
        tokens = {key: os.environ.pop(environment_name, "") for key, environment_name in TOKEN_ENV.items()}
    else:
        tokens = dict(tokens)
    if config is None:
        try:
            config = load_local_config()
        except ConfigError:
            return _result(
                "BLOCKED",
                "P0-03 requires an approved non-production isolation fixture at .local/p0/isolation-live.json; no Graph request was sent.",
                trace + ["provider-call:none"],
            )
    missing = [key for key in REQUIRED_FIXTURES if not isinstance(tokens.get(key), str) or not tokens[key].strip()]
    if missing:
        return _result(
            "BLOCKED",
            "P0-03 requires one short-lived fixture token per configured actor; no Graph request was sent.",
            trace + ["provider-call:none"],
            config=config,
        )
    cleaned_tokens = {key: value.strip() for key, value in tokens.items() if key in REQUIRED_FIXTURES and isinstance(value, str)}
    if any(len(token) > MAX_TOKEN_BYTES or any(character.isspace() for character in token) for token in cleaned_tokens.values()):
        return _result(
            "BLOCKED",
            "P0-03 received an invalid short-lived fixture token; no Graph request was sent.",
            trace + ["provider-call:none"],
            config=config,
        )
    clock = int(time.time()) if now is None else now
    fixtures = {fixture.key: fixture for fixture in config.fixtures}
    for key in REQUIRED_FIXTURES:
        if not _claims_match(cleaned_tokens[key], config, fixtures[key], clock):
            return _result(
                "BLOCKED",
                "P0-03 fixture token claims did not match the configured tenant, app, permission, or actor; no Graph request was sent.",
                trace + ["provider-call:none"],
                config=config,
            )

    identity_status = "LIVE_PASS" if config.auth_mode == "delegated" else "NOT_RUN_EXTERNAL_PREREQUISITE"
    sites = {site.key: site for site in config.sites}
    resources = {resource.key: resource for resource in config.resources}
    for fixture_key in REQUIRED_FIXTURES:
        fixture = fixtures[fixture_key]
        token = cleaned_tokens[fixture_key]
        for site_key in SITE_KEYS:
            allowed = site_key in fixture.allowed_site_keys
            site_response = transport(_site_request(sites[site_key].site_id, token), REQUEST_TIMEOUT_SECONDS, True)
            trace.append(f"provider-call:{fixture_key}:{site_key}:site-metadata")
            if _unknown(site_response):
                return _result(
                    "BLOCKED",
                    "P0-03 site metadata outcome was unknown; no denial or boundary claim was recorded.",
                    trace,
                    config=config,
                    identity_status=identity_status,
                    sharepoint_status="BLOCKED",
                )
            if allowed:
                if site_response.status != 200:
                    return _result("BLOCKED", "P0-03 an allowed site was not readable; grant or fixture binding needs review.", trace, config=config, identity_status=identity_status, sharepoint_status="BLOCKED")
                metadata = _json_object(site_response)
                if metadata is None or metadata.get("id") != sites[site_key].site_id:
                    return _result("FAIL", "P0-03 allowed site metadata did not match the trusted binding.", trace, config=config, identity_status=identity_status, sharepoint_status="FAIL")
            elif site_response.status not in {403, 404}:
                if site_response.status == 200:
                    return _result("FAIL", "P0-03 unauthorized site metadata was readable; the boundary is broader than expected.", trace, config=config, identity_status=identity_status, sharepoint_status="FAIL")
                return _result("FAIL", "P0-03 unauthorized site metadata returned an unexpected HTTP status.", trace, config=config, identity_status=identity_status, sharepoint_status="FAIL")

            resource = resources[site_key]
            item_response = transport(_item_request(resource, token), REQUEST_TIMEOUT_SECONDS, allowed)
            trace.append(f"provider-call:{fixture_key}:{site_key}:item-metadata")
            if _unknown(item_response):
                return _result("BLOCKED", "P0-03 item metadata outcome was unknown; no leakage claim was recorded.", trace, config=config, identity_status=identity_status, sharepoint_status="BLOCKED")
            if allowed:
                if item_response.status != 200:
                    return _result("BLOCKED", "P0-03 an allowed item was not readable; grant or fixture binding needs review.", trace, config=config, identity_status=identity_status, sharepoint_status="BLOCKED")
                metadata = _json_object(item_response)
                if metadata is None or metadata.get("id") != resource.item_id:
                    return _result("FAIL", "P0-03 allowed item metadata did not match the trusted binding.", trace, config=config, identity_status=identity_status, sharepoint_status="FAIL")
            elif item_response.status not in {403, 404}:
                if item_response.status == 200:
                    return _result("FAIL", "P0-03 unauthorized item metadata was readable; cross-client metadata leaked.", trace, config=config, identity_status=identity_status, sharepoint_status="FAIL")
                return _result("FAIL", "P0-03 unauthorized item metadata returned an unexpected HTTP status.", trace, config=config, identity_status=identity_status, sharepoint_status="FAIL")

            content_response = transport(_content_request(resource, token), REQUEST_TIMEOUT_SECONDS, False)
            trace.append(f"provider-call:{fixture_key}:{site_key}:content")
            if _unknown(content_response):
                return _result("BLOCKED", "P0-03 content outcome was unknown; no leakage claim was recorded.", trace, config=config, identity_status=identity_status, sharepoint_status="BLOCKED")
            if allowed:
                if content_response.status not in {200, 302}:
                    return _result("BLOCKED", "P0-03 an allowed file was not readable; grant or fixture binding needs review.", trace, config=config, identity_status=identity_status, sharepoint_status="BLOCKED")
            elif content_response.status not in {403, 404}:
                if content_response.status in {200, 302}:
                    return _result("FAIL", "P0-03 unauthorized file content was readable; cross-client data leaked.", trace, config=config, identity_status=identity_status, sharepoint_status="FAIL")
                return _result("FAIL", "P0-03 unauthorized content returned an unexpected HTTP status.", trace, config=config, identity_status=identity_status, sharepoint_status="FAIL")

            search_response = transport(_search_request(resource, token), REQUEST_TIMEOUT_SECONDS, allowed)
            trace.append(f"provider-call:{fixture_key}:{site_key}:search")
            if _unknown(search_response):
                return _result("BLOCKED", "P0-03 search outcome was unknown; no leakage claim was recorded.", trace, config=config, identity_status=identity_status, sharepoint_status="BLOCKED")
            if search_response.status in {403, 404} and not allowed:
                continue
            if search_response.status != 200:
                return _result("FAIL", "P0-03 search returned an unexpected HTTP status.", trace, config=config, identity_status=identity_status, sharepoint_status="FAIL")
            search_body = _json_object(search_response)
            if search_body is None:
                return _result("FAIL", "P0-03 search response was not valid JSON.", trace, config=config, identity_status=identity_status, sharepoint_status="FAIL")
            leaked = _contains_id(search_body, resource.item_id)
            if allowed and not leaked:
                return _result("FAIL", "P0-03 allowed search did not return the trusted item identity.", trace, config=config, identity_status=identity_status, sharepoint_status="FAIL")
            if not allowed and leaked:
                return _result("FAIL", "P0-03 unauthorized search exposed the trusted item identity.", trace, config=config, identity_status=identity_status, sharepoint_status="FAIL")

    return _result(
        "BLOCKED",
        "P0-03 SharePoint site, item, content, and search boundaries passed the direct read-only subprobe; Frappe assignment and revocation evidence remain required.",
        trace,
        config=config,
        identity_status=identity_status,
        sharepoint_status="LIVE_PASS",
    )
