# 03 — Pin the toolchain and command conventions

## Objective

Choose a compatible, supported Frappe/ERPNext runtime and freeze exact dependencies. Establish one repeatable local/CI command interface before proof code or production code is introduced.

## Context/Dependencies

**Milestone:** R0. **Requirement scope:** FR-INT-001–003; FR-TRACE-003; ET-44; P0-01.

**Dependencies:** [02 — Service contracts, gates, outputs, and operating targets](02-business-contracts-and-operating-targets.md)

**Execution gate:** file 02 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Frappe app scaffolding](https://docs.frappe.io/framework/user/en/tutorial/create-an-app); [Frappe testing](https://docs.frappe.io/framework/user/en/testing); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database); [MSAL Python token acquisition](https://learn.microsoft.com/en-us/entra/msal/python/getting-started/acquiring-tokens); [RFC 8785 Python implementation](https://github.com/trailofbits/rfc8785.py).

## Target Files

- **Create:** `infra/production/versions.json`
- **Create:** `infra/production/poc-requirements.txt`
- **Create:** `docs/production/developer-environment.md`
- **Create:** `scripts/wbs/check_versions.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Verify the current official compatibility/support matrix and select matching Frappe/ERPNext supported releases; record exact tags AND commit hashes, Python, Node, package-manager, MariaDB, Redis, Bench and container-image digests. Do not use floating latest/develop or change the existing demo package-lock.json for this task. The WBS deliberately does not invent current patch versions.

2. Use Frappe/ERPNext, Python standard-library Decimal/csv/hashlib/unittest, Frappe ORM/query builder and Redis-backed Frappe workers. Plan explicit runtime dependencies only when needed: requests for one HTTP transport, msal for Microsoft application tokens, rfc8785 for manifest bytes, openpyxl for XLSX, and xlrd only when XLS input is explicitly retained in the approved profile. Prefer built-in Frappe authentication and PDF/Jinja utilities over new services.

3. Define REPO_ROOT as the current repository root; production app source at $REPO_ROOT/production/audit_practice; ignored disposable benches under $REPO_ROOT/.local/. Use AUDIT_SITE=auditflow-test.localhost for test commands, and a different allowlisted POC site for proof work. Keep these environment values in ignored local configuration; examples contain no credentials.

4. Document future command interfaces: python3 scripts/p0/run.py --suite <name> --mode mock|live; ./scripts/production/dev doctor|bootstrap-test|migrate-test|test <module>|test-all|build|serve-test. Task [04 — Disposable feasibility environment, spike schema, and proof runner](04-poc-harness-and-schema.md) creates the proof runner; task [09 — Scaffold the production app and executable test harness](09-production-app-and-test-harness.md) creates the production wrapper. Do not run nonexistent commands now.

5. Verify Bench command help for the pinned version and document installing a locally sourced nested app without relocating the demo. Use a generated app skeleton and a Bench-side app mount/symlink plus editable install; sites/apps.txt registration and install-app must be proven in the bootstrap task. No custom dependency resolver or general configuration framework.

## Acceptance Criteria

- [ ] Exact versions and image digests are recorded, compatible and reproducible; unresolved runtime mismatches prevent P0 completion.
- [ ] check_versions.py rejects floating refs and missing pin fields without downloading or executing arbitrary code.
- [ ] The developer guide defines working directories, all environment variables and command ownership.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
python3 scripts/wbs/check_versions.py infra/production/versions.json
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.
