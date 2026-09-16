# 09 — Scaffold the production app and executable test harness

## Objective

Create the additive production Frappe app and the repeatable local/CI test commands used by all following tasks. Keep the deployed Vue/Cloudflare demonstrator untouched.

## Context/Dependencies

**Milestone:** R1. **Requirement scope:** FR-INT-001–003; FR-TRACE-003–005; P0-01 production recheck.

**Dependencies:** [03 — Pin the toolchain and command conventions](03-toolchain-and-version-contract.md); [08 — R0 evidence reconciliation and feasibility exit](08-r0-feasibility-exit.md)

**Execution gate:** file 08 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Frappe app scaffolding](https://docs.frappe.io/framework/user/en/tutorial/create-an-app); [Frappe testing](https://docs.frappe.io/framework/user/en/testing); [Frappe background jobs](https://docs.frappe.io/framework/user/en/api/background_jobs).

## Target Files

- **Create:** `production/audit_practice/pyproject.toml`
- **Create:** `production/audit_practice/audit_practice/__init__.py`
- **Create:** `production/audit_practice/audit_practice/hooks.py`
- **Create:** `production/audit_practice/audit_practice/modules.txt`
- **Create:** `production/audit_practice/audit_practice/patches.txt`
- **Create:** `production/audit_practice/audit_practice/audit_operations/__init__.py`
- **Create:** `production/audit_practice/audit_practice/tests/__init__.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_bootstrap.py`
- **Create:** `scripts/production/dev`
- **Create:** `scripts/production/bootstrap.py`
- **Create:** `infra/production/dev.compose.yml`
- **Create:** `.github/workflows/production-ci.yml`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Generate a Frappe application named audit_practice with module Audit Operations using the pinned scaffold; retain generated license/packaging metadata. Its package root is production/audit_practice/audit_practice, distinct from the repository root. Add __init__.py files for Python packages as introduced; never check a whole Bench, sites/ secrets, vendor apps or node_modules into this repository.

2. Implement scripts/production/dev as a strict shell/Python wrapper callable from REPO_ROOT. doctor verifies binaries, versions, disposable site, DB and mounted app. bootstrap-test creates only the allowlisted local test site and installs ERPNext then audit_practice. migrate-test performs bench --site "$AUDIT_SITE" migrate; test <module> executes bench --site "$AUDIT_SITE" run-tests --app audit_practice --module <module>; test-all, build and serve-test use the corresponding pinned Bench commands. Reject production hosts, arbitrary shell evaluation and missing environment configuration.

3. Mount or install the nested app into the ignored disposable Bench using the mechanism proven in R0. Make the install idempotent and validate package import, sites/apps.txt and installed-app registration. Set tests enabled only on the disposable test site. Preserve the root npm package and demo entrypoint.

4. Add production-ci.yml with isolated MariaDB/Redis, dependency caches keyed by exact pins, fresh site install, app tests and build. Run no tenant mutations, production migrations or deployment on pull requests. Untrusted forks receive no live credentials.

5. Implement a bootstrap test proving custom app/module availability and a clean install/migrate/re-run lifecycle. R0 proved the platform spike; this task now proves the actual production app skeleton. All later test modules must be collected by this runner, not merely compile successfully.

## Acceptance Criteria

- [ ] A clean checkout boots the disposable site and imports audit_practice.
- [ ] Running bootstrap/migrate twice does not duplicate setup records or modify demo state.
- [ ] The focused bootstrap test and production build pass; root npm test/build remain independently runnable.
- [ ] The wrapper rejects a production site and unsupported subcommand.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev doctor
./scripts/production/dev bootstrap-test
./scripts/production/dev migrate-test
./scripts/production/dev test audit_practice.tests.test_bootstrap
./scripts/production/dev build
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.
