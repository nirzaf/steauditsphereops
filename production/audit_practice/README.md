# STE AuditSphere Ops Frappe app

This package is the production app boundary for STE AuditSphere Ops.

The current scaffold registers the Audit Operations module. It does not yet
implement business records, workflows, identity integrations, or document
delivery. Those capabilities are introduced by their accepted WBS tasks.

## License

MIT. See [license.txt](license.txt).

## Microsoft 365 and SharePoint connection contract

The production integration follows the organization-level connection model in
the approved Microsoft 365 integration guideline. This section records the
required boundary; it does not mean that OAuth, Graph access, or a tenant
connection is configured.

- An authorized organization administrator connects the tenant once and
  approves only the permissions selected for the integration. The verified
  Entra tenant ID is the organization key; an email domain is not an identity
  boundary. Keep consent state and its actor/time as auditable metadata, never
  client secrets or access tokens in source or ordinary application records.
- The administrator selects the permitted SharePoint sites and libraries.
  Bind them by verified stable site/library IDs; treat names and URLs as display
  or navigation data, not as authority. Resolve document references from
  server-controlled bindings instead of accepting caller-supplied URLs, IDs, or
  Graph paths.
- Keep site discovery and Selected-grant provisioning in a separately
  authorized administrator control-plane step. The Graph all-sites listing
  endpoint uses broad application permissions, and creating a site permission
  requires full-control authority. Do not give those tenant-wide permissions to
  a long-lived document worker just to populate a picker or create grants. The
  worker receives only the pre-approved Selected scope and resource assignment
  needed for its job; connection activation verifies that scope and assignment
  together.
- Keep the connection inactive until tenant identity, consent, selected
  libraries, required access, and denial outside the selected boundary have
  been verified. Exercise the authorized read/write and saved-version
  operations before marking the connection `ACTIVE`.
- Interactive document work uses the signed-in user's delegated Microsoft
  identity. The application checks the actor's account, role, client and
  engagement assignments, operation, and any hold; SharePoint independently
  evaluates that user's existing permissions. A tenant connection does not
  grant site membership, and the integration must not add users implicitly.
- Background synchronization, snapshot, reconciliation, and records jobs use
  a separate application identity restricted to their approved repositories
  and operations. Do not reuse an elevated human account or one broad identity
  across working, compliance, and issued-record repositories. Keep any exact
  Graph permission and Selected-grant decision with the authorized
  tenant/security owner; never broaden consent automatically after a denial.
- Provisioning, removal, and periodic access reconciliation evaluate local
  application access and SharePoint membership independently. A denial or
  revocation in either system denies the document operation.

The scaffold has not requested tenant consent, changed SharePoint membership,
or verified provider access. WBS-05 still owns the live identity/document
capability proof and the selected grants and records profile; creating a test
site alone is not evidence that the integration is connected or authorized.

The Selected-permission consent, resource assignment, and token scope are all
required for access. See Microsoft's [Selected permissions overview](https://learn.microsoft.com/en-us/graph/permissions-selected-overview),
[List sites permissions](https://learn.microsoft.com/en-us/graph/api/site-list?view=graph-rest-1.0),
and [Create site permission requirements](https://learn.microsoft.com/en-us/graph/api/site-post-permissions?view=graph-rest-1.0).

The local harness defaults `BENCH_ROOT` to `.local/bench` and accepts only
paths below the ignored `.local/` directory. A disposable site's generated
Administrator password is stored in the ignored
`.local/production/site-admin-password` file so the local `serve-test` site can
be accessed after bootstrap. Keep that file private and do not add it to source
control.
