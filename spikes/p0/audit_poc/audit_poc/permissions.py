"""Fail-closed scope helpers for the disposable audit_poc app."""

from __future__ import annotations


def subject_key(tenant_id: str, subject_id: str) -> str:
    if not tenant_id or not subject_id:
        raise ValueError("tenant_id and subject_id are required")
    return f"{tenant_id}:{subject_id}"


def scope_key(client_id: str, period: str) -> str:
    if not client_id or not period:
        raise ValueError("client_id and period are required")
    return f"{client_id}:{period}"


def access_decision(actor: dict[str, object], record: dict[str, object], action: str = "read") -> tuple[bool, str]:
    """Return a conservative decision for mock permission experiments."""
    if actor.get("disabled"):
        return False, "ACTOR_DISABLED"
    if actor.get("revoked"):
        return False, "ACTOR_REVOKED"
    actor_identity = (actor.get("tenant_id"), actor.get("client_id"), actor.get("subject_id"))
    if any(not isinstance(value, str) or not value.strip() for value in actor_identity):
        return False, "ACTOR_IDENTITY_INCOMPLETE"
    record_scope = (record.get("tenant_id"), record.get("client_id"))
    if any(not isinstance(value, str) or not value.strip() for value in record_scope):
        return False, "RECORD_SCOPE_INCOMPLETE"
    if actor.get("tenant_id") != record.get("tenant_id"):
        return False, "TENANT_MISMATCH"
    if actor.get("client_id") != record.get("client_id"):
        return False, "CLIENT_SCOPE_MISMATCH"
    if action in {"export", "share"} and actor.get("role") not in {"staff", "records_custodian"}:
        return False, "ACTION_NOT_ASSIGNED"
    return True, "ALLOW"


def validate_record(doc: object) -> None:
    if not getattr(doc, "client_id", None) or not getattr(doc, "period", None):
        raise ValueError("client_id and period are required for every scoped POC record")


def poc_record_query(user: str | None = None) -> str:
    """Do not turn a caller-supplied user into a scope predicate."""
    return "1=0"


def poc_record_has_permission(doc: object, user: str | None = None, ptype: str | None = None) -> bool:
    # No authenticated assignment context exists in the disposable POC yet.
    # Allowing access based only on record fields would bypass tenant/client
    # isolation through direct Desk or generic-API permission checks.
    return False
