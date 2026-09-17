# SharePoint and portal boundary (P0-03–P0-05, P0-09)

This is a boundary contract and test plan, not evidence that a tenant has been
configured. WBS-05 requires a security/tenant administrator to provide the
non-production identities, test sites/libraries, Selected grants, and approved
records profile before any external observation can be recorded.

## Containers

| Container | Intended content | Access boundary |
| --- | --- | --- |
| Client-content library | Client submissions, PBC receipts, approved responses | Client assignment plus firm staff assignment; no internal review fields. |
| Internal-workpaper library | Planning, workpapers, review points, conclusions | Firm roles only; never a client export or direct client link. |
| Issued-record library | Final released artifacts, manifests, delivery/archive evidence | Authorized records/signatory roles; release and protection checkpoints apply. |

The browser portal projects only the records permitted by the current
firm/client/engagement/period assignment. Direct Office links remain bounded by
the repository permissions; a portal screen is not an authorization layer.
Search, metadata, counts, exports, attachments, and version reads use the same
scope decision. Item-specific permissions are a last resort; inherited
site/library/group boundaries are preferred.

## Required observations

The live test must use named staff, invited client, unrelated tenant, reused
email, and disabled-user fixtures. It must show wrong-tenant, wrong-client,
revoked-access, and unrelated-repository denials for both content and
metadata. Deterministic bytes must retain distinct original, stored, submitted,
and approved identities; an ETag is never a SHA-256 substitute.

Records tests must distinguish an ordinary editor, records custodian, and
privileged administrator, and must record residual privileged-admin risk. A
retention label name alone is not proof of immutable bytes, retention, or
legal compliance.

## Current disposition

`docs/production/microsoft-capabilities.json` intentionally reports every
operation as `NOT_RUN_EXTERNAL_PREREQUISITE`. The mock tests prove only local
fail-closed helpers and deterministic snapshot behavior. No tenant, consent,
license, retention setting, provider success, or denial is claimed here.
