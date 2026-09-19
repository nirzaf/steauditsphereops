# Entra identity, SharePoint, and portal boundaries (P0-02–P0-05, P0-09)

This records the boundary contract, test plan, and observed provisioning state.
It incorporates the owner-supplied Microsoft 365 / SharePoint integration
guideline. P0-04 metadata and P0-05 saved-version behavior now have bounded
app-only observations. A bounded Entra subject-mapping subprobe now exists;
identity isolation and records protection remain blocked pending the fixtures
and role-based proof recorded below.

## Tenant connection and identity lanes

An organization administrator connects the tenant once through OAuth admin
consent. The system records the verified Entra tenant ID as the trusted
organization key, together with the organization name, primary domain,
connection and consent status, and who/when connected it. Email domains do not
establish tenant identity.

The administrator selects the allowed SharePoint sites and libraries. Store
their stable tenant, site, and library identifiers as trusted bindings; names
and URLs are for discovery and display. Resolve every operation through those
bindings and reject caller-supplied URLs, site IDs, drive IDs, folder IDs, and
Graph paths.

Use the lifecycle `CONNECTED → VERIFIED → ACTIVE`. Verification checks tenant
identity, OAuth consent, selected site/library existence, required permissions,
file read/write behavior in disposable test data, and denial for an
unauthorized location. Merely selecting a development tenant or observing a
site does not satisfy this gate.

Interactive document operations use the signed-in user's delegated Microsoft
identity. Application role, client/engagement assignment, permitted operation,
and the user's actual SharePoint permission must all allow access. Opening an
Office link does not bypass either authorization layer, and the application
does not impersonate a broadly privileged service account for user activity.

Background operations use a separate application/service identity with
least-privilege access to the approved repositories. The exact grant and
per-operation authentication mode remain owner-selected and must be tested.
Tenant admin consent does not add users to SharePoint or grant site membership.
Preserve existing membership, reconcile desired and actual access, and verify
application and SharePoint revocation independently. Use separate identities
and repository boundaries where records or compliance data require them.

## Containers

| Container | Intended content | Access boundary |
| --- | --- | --- |
| Client-content library | Client submissions, PBC receipts, approved responses | Client assignment plus firm staff assignment; no internal review fields. |
| Internal-workpaper library | Planning, workpapers, review points, conclusions | Firm roles only; never a client export or direct client link. |
| Issued-record library | Final released artifacts, manifests, delivery/archive evidence | Authorized records/signatory roles; release and protection checkpoints apply. |

## Observed developer-tenant test layout (2026-09-18)

The designated Microsoft 365 developer tenant now has separate private team
sites for Client A, Client B, internal workpapers, issued records, and an
unrelated repository. The issued-records site was provisioned after delayed
feedback, so a second site with the same display name was also created; both
remain in place. The current tenant administrator is the owner. No additional owners or
members were added during site setup. The P0-05 probe later uploaded one small
synthetic file to Client A; it remains in that test library. The admin center
reports external sharing enabled on each created site; that setting was not
changed. Tenant, user, site, library, and group identifiers are intentionally
kept out of this repository.

The browser portal projects only the records permitted by the current
firm/client/engagement/period assignment. Direct Office links remain bounded by
the repository permissions; a portal screen is not an authorization layer.
Search, metadata, counts, exports, attachments, and version reads use the same
scope decision. Item-specific permissions are a last resort; inherited
site/library/group boundaries are preferred.

## Required observations

The WBS baseline requests named staff, invited-client, unrelated-tenant,
reused-email, and disabled-user fixtures. The owner approved member identities
for this POC and deferred the guest/invite model to production; this scoped
disposition is recorded in the decision register and does not establish the
production guest model. Live identity and isolation observations still need
real member sessions and must show wrong-tenant, wrong-client, revoked-access,
and unrelated-repository denials for content and metadata. Deterministic bytes
must retain distinct original, stored, submitted, and approved identities; an
ETag is never a SHA-256 substitute.

Records tests must distinguish an ordinary editor, records custodian, and
privileged administrator, and must record residual privileged-admin risk. A
retention label name alone is not proof of immutable bytes, retention, or
legal compliance.

## P0-02 read-only Entra subject-mapping subprobe

`scripts/p0/identity_probe.py` performs only
`GET /v1.0/me?$select=id,userPrincipalName` for the configured staff, Client X,
and Client Y member fixtures. Its private configuration belongs at the ignored
path `.local/p0/identity-live.json` and must identify the non-production
tenant, AuditSphere P0 client application, delegated authentication, exactly
the `User.Read` permission, and distinct fixture object IDs and current UPNs.
The schema identifier is `steauditsphereops/p0-identity-live@1`; each fixture
contains only `object_id` and `user_principal_name`.
Supply one short-lived delegated Graph token for each fixture through
`AUDIT_P0_IDENTITY_STAFF_TOKEN`, `AUDIT_P0_IDENTITY_CLIENT_X_TOKEN`, and
`AUDIT_P0_IDENTITY_CLIENT_Y_TOKEN`. Tokens are consumed from the process
environment and are never written to evidence or printed.

Before any request, the probe checks token claims against the configured
tenant, application, Graph audience, exact delegated scope, and fixture
subject. This local claim check is only a request guard; Microsoft Graph
validates the bearer token. The probe never follows redirects, retries a
denial, or changes consent or access. Evidence contains fixture keys and
bounded HTTP statuses only, not tokens, UPNs, object IDs, or response bodies.
Matching all three `/me` responses records only the Entra subject-mapping
subproof as `LIVE_PASS`; the aggregate P0-02 suite remains `BLOCKED` until the
Frappe authorization, email change/reuse, disabled/revoked, wrong-tenant, and
user-level SharePoint cases are independently proven.

## P0-04 read-only Graph probe

`scripts/p0/microsoft_probe.py` implements only the bounded P0-04 metadata
check. It issues `GET /v1.0/sites/{site-id}?$select=id` for the prebound
authorized site and then the verified unrelated site. It does not enumerate
sites, accept caller-supplied URLs, upload or modify files, or change consent,
membership, grants, or retention. A 403/404 for the unrelated site counts as a
denial only when the private fixture records that the site was independently
verified to exist; a successful unrelated response fails the probe without
capturing its response body.

The private fixture belongs at the ignored path
`.local/p0/microsoft-live.json`; the short-lived bearer token is supplied only
through `AUDIT_P0_GRAPH_ACCESS_TOKEN` and is never written to the evidence file
or printed. The fixture must explicitly name the non-production tenant, the
owner-selected authentication mode and exact permission names, stable site
IDs, and the unrelated site's prior existence verification. Missing or
invalid configuration returns BLOCKED before a provider request. On
2026-09-18 the app-only P0-04 probe returned HTTP 200 for Client A metadata
and HTTP 403 for the independently verified unrelated site. Evidence is in
.local/p0-evidence/microsoft-live-1789735940536556300.json (ignored local
evidence). The separate Graph Explorer permission setup and permission-list
reads recorded below are not P0-04 capability evidence. This probe covers only
site metadata; it does not establish identity mapping, file snapshots, records protection, or production readiness.

The local fixture schema is:

```json
{
  "schema": "steauditsphereops/p0-microsoft-live@1",
  "environment": "NONPRODUCTION",
  "tenant_id": "<tenant-guid>",
  "auth_mode": "<owner-selected: application or delegated>",
  "permission_names": ["<exact owner-approved permissions>"],
  "unrelated_site_exists_verified": true,
  "site_bindings": {
    "allowed": "<hostname,site-guid,web-guid>",
    "unrelated": "<hostname,site-guid,web-guid>"
  }
}
```

## P0-05 bounded file, saved-version, and delta probe

`scripts/p0/documents_probe.py` implements one non-production synthetic file
cycle using the exact `Sites.Selected` app-only grant and prebound Client A
library. Before writing, it confirms the allowed site, checks Client B and an
independently verified unrelated site are denied, and verifies the configured
document library belongs to Client A. It creates one unique file, reads the
original bytes, edits the working copy twice, and verifies each current byte
set. It lists bounded saved versions, reconstructs the exact original bytes,
then reads that same saved version again after the second edit. It creates one
unique destination folder, renames and moves the synthetic file within the
bound drive, then verifies the item ID, name, parent, and bytes. Graph v1.0
supports creating a child folder and moving an item by updating its
`parentReference` ([create folder](https://learn.microsoft.com/en-us/graph/api/driveitem-post-children?view=graph-rest-1.0), [move item](https://learn.microsoft.com/en-us/graph/api/driveitem-move?view=graph-rest-1.0)). An uncertain write is never retried and the probe never deletes its artifacts. An untrusted
preauthenticated download host is rejected and the Graph bearer token is never
forwarded to the download host.

The probe establishes a delta cursor with `token=latest` before creating the
synthetic file, then follows the returned cursor after the edits and
rename/move. It checks the last occurrence of the same item in the bounded
delta pages against the final synthetic name and working-copy size. Only HTTPS
Graph links for the configured drive are followed; evidence records the status
and never copies cursor URLs or tokens. Microsoft Graph documents `token=latest`
as returning an empty result with a current delta link and uses
`@odata.nextLink` / `@odata.deltaLink` for paging and continuation
([driveItem delta API](https://learn.microsoft.com/en-us/graph/api/driveitem-delta?view=graph-rest-1.0)).
This extension is covered by mocked tests; it has not yet been run against the
developer tenant, so it is not a live delta observation.

The probe now includes a bounded metadata subprobe for the same synthetic file.
It derives the SharePoint list and item identifiers from that bound drive item,
checks that the existing `Title` column is writable, uses the item's ETag for a
conditional field update, and reads the value back. It does not create columns
or change site schema. It follows the Graph list-columns, listItem field-update,
and listItem readback APIs ([list columns](https://learn.microsoft.com/en-us/graph/api/list-list-columns?view=graph-rest-1.0),
[update fields](https://learn.microsoft.com/en-us/graph/api/listitem-update?view=graph-rest-1.0),
[read fields](https://learn.microsoft.com/en-us/graph/api/listitem-get?view=graph-rest-1.0)).
This new path currently has mock coverage only; no live metadata-update
observation is claimed. The probe still does not verify tenant
identity, Office unsaved-change behavior, version pruning, concurrent snapshot
creation, protected files, or records policy. Even a successful P0-05
observation leaves the `documents` suite `BLOCKED` until P0-09 has independent
records-protection evidence. Its private bindings belong at
`.local/p0/sharepoint-documents.json`; the short-lived bearer token uses
`AUDIT_P0_GRAPH_ACCESS_TOKEN` and is consumed from the process environment.
Before sending a request, the probe checks the token payload for the configured
tenant and client IDs, Microsoft Graph audience, exact `Sites.Selected` app
role, app-only context, and a current validity window. This local check does
not verify the JWT signature; Microsoft Graph validates the actual token and
enforces the grant on each request. IDs, claims, and bearer material are not
copied to the evidence file.

The ignored private fixture has this shape:

```json
{
  "schema": "steauditsphereops/p0-sharepoint-documents@1",
  "environment": "NONPRODUCTION",
  "tenant_id": "<tenant-guid>",
  "client_id": "<app-registration-guid>",
  "auth_mode": "application",
  "permission_names": ["Sites.Selected"],
  "site_bindings": {
    "allowed": "<hostname,site-guid,web-guid>",
    "client_b": "<hostname,site-guid,web-guid>",
    "unrelated": "<hostname,site-guid,web-guid>"
  },
  "site_exists_verified": {"client_b": true, "unrelated": true},
  "drive_bindings": {"client_a_content": "<drive-id>"}
}
```

## Current disposition

The current capability matrix distinguishes completed observations from
operations still awaiting proof. P0-04 metadata access and the bounded P0-05
file/saved-version cycle are observed with the app-only `Sites.Selected`
grant. P0-09 record protection remains `NOT_RUN_EXTERNAL_PREREQUISITE`; the
other operations retain their individual status in
`docs/production/microsoft-capabilities.json`.

The EasyGuide tenant contains the single-tenant `AuditSphere P0` app
registration with Microsoft Graph delegated `User.Read` and application
`Sites.Selected` consent. A Graph Explorer signed-in administrator consented
to delegated `Sites.FullControl.All` for permission setup and read-only
verification. That consent is separate from the AuditSphere P0 application
permission and remains active. No additional Graph permissions were granted.

AuditSphere P0 received one `write` site permission on the separate Client A
site. Microsoft Graph returned HTTP 201 when creating it and HTTP 200 when
reading it back; the response showed the AuditSphere P0 application and the
`write` role. Read-only permission listings returned an empty permission list
for Client B, the unrelated site, the internal-workpaper site, the separate
development site, and both issued-records sites with the same display name.
No grant was added on those sites. These permission-list checks verify the
configured site grants; the live P0-04 and P0-05 results below provide the
bounded app-only observations.

P0-04 and P0-05 now have genuine app-only observations using the
AuditSphere P0 Sites.Selected application permission and its single Client A
write grant. The P0-04 live probe returned HTTP 200 for Client A metadata and
HTTP 403 for the verified unrelated site. The P0-05 live probe returned HTTP
403 for both Client B and the unrelated site, uploaded one synthetic file to
Client A, verified the original and edited bytes, and reconstructed the exact
original saved version after the edit. The original and saved-version
SHA-256 values match. The probe intentionally left the unique synthetic file
in the test library and did not retry or delete it. Detailed redacted results
are in .local/p0-evidence/microsoft-live-1789735940536556300.json and
.local/p0-evidence/documents-live-1789735950375315400.json; these paths are
ignored local evidence. The app credential and short-lived access token were
not written to the repository or evidence.

The documents suite remains `BLOCKED` because P0-09 is independently
required. The owner approved member identities for the POC and deferred the
guest/invite model to production. The P0-02 Entra subprobe is implemented but
has not run: `.local/p0/identity-live.json` and the three per-user delegated
tokens are not configured. P0-02 and P0-03 remain blocked; wrong-tenant,
revoked-access, changed/reused-email, Frappe authorization, and cross-client
user-access observations have not been run.

Purview Records Management is accessible in the EasyGuide developer tenant,
and its File Plan showed zero labels. The owner-approved synthetic profile is
30-day retention followed by disposition review on disposable artifacts. The
label wizard required a named disposition reviewer; none was designated,
so the draft was canceled before saving. No label or retention setting was
applied. P0-09 has no edit/delete/unlock evidence for an ordinary editor,
records custodian, or privileged administrator. The protected-role model and
verification method remain pending. The separate Graph Explorer
`Sites.FullControl.All` delegated consent remains active; it is not part of
the AuditSphere P0 app permission.
