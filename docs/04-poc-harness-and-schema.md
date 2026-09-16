# 04 — Disposable feasibility environment, spike schema, and proof runner

## Objective

Create the isolated test substrate required by all Phase 0 experiments. Provide a minimal real database schema and evidence runner without depending on future production APIs.

## Context/Dependencies

**Milestone:** R0. **Requirement scope:** FR-TRACE-002–006; P0-01; sections 25–27.

**Dependencies:** [03 — Pin the toolchain and command conventions](03-toolchain-and-version-contract.md)

**Execution gate:** file 03 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database); [Frappe app scaffolding](https://docs.frappe.io/framework/user/en/tutorial/create-an-app); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `infra/production/poc.compose.yml`
- **Create:** `spikes/p0/schema.sql`
- **Create:** `spikes/p0/__init__.py`
- **Create:** `spikes/p0/test_build.py`
- **Create:** `scripts/p0/run.py`
- **Create:** `scripts/p0/provision_local.py`
- **Create:** `docs/production/p0-index.json`
- **Create:** `spikes/p0/audit_poc/pyproject.toml`
- **Create:** `spikes/p0/audit_poc/audit_poc/__init__.py`
- **Create:** `spikes/p0/audit_poc/audit_poc/hooks.py`
- **Create:** `spikes/p0/audit_poc/audit_poc/modules.txt`
- **Create:** `spikes/p0/audit_poc/audit_poc/poc/__init__.py`
- **Create:** `spikes/p0/audit_poc/audit_poc/poc/doctype/__init__.py`
- **Create:** `spikes/p0/audit_poc/audit_poc/poc/doctype/poc_record/__init__.py`
- **Create:** `spikes/p0/audit_poc/audit_poc/poc/doctype/poc_record/poc_record.json`
- **Create:** `spikes/p0/audit_poc/audit_poc/poc/doctype/poc_record/poc_record.py`
- **Modify:** `.gitignore`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Provision only disposable MariaDB/Redis/Frappe/ERPNext proof instances using the pinned runtime; mount no production volumes and inherit no production tenant secrets. A tiny audit_poc app may exercise permission hooks; keep it outside production/audit_practice and label it non-reusable spike code. P0-01 tests a clean build and migration; do not claim the future audit_practice application was already built.

2. Create schema.sql before any spike mutations: scope_guard(client_id, period, generation, revision), package(id, scope, evaluated_generation), command_receipt(scope, actor, key, payload_digest), outbox(id, scope, state, attempt, fence), checkpoint_reference and local audit events. Use MariaDB unique indexes and transactions. These are proof tables, not production DocTypes or a substitute for tasks later in R1.

3. Implement run.py with explicit suite registry build/identity/documents/transactions/recovery/accounting/privileged, a monotonic clock, deterministic test data and JSON evidence output. Include source experiment ID, mode, exact revisions, target IDs with sensitive fields redacted, test outcome and trace. MOCK_PASS is not LIVE_PASS; missing live credentials returns BLOCKED/nonzero rather than a skipped success.

4. Index the actual twelve P0 IDs from src/domain/traceability.js. Map each to a task and a specific test; preserve the source meaning and expected result. Keep professional/scope-economics P0-12 as a human-evidence gate, not an automated assertion.

5. Create local-only safety checks before running schema changes: require explicit environment=POC, allowlisted local host/site and database names. No remote D1 migrations, automatic tenant provisioning or retention changes. Root proof runner may use subprocess only with fixed argument arrays and fail on unexpected targets.

6. Scaffold the declared audit_poc package and a minimal scoped POC Record DocType for real generic-API/permission experiments. Build suite live mode creates the actual disposable container/site/app; mock mode is runner self-test only. The documents suite includes test_records.py. P0-01 at R0 proves platform/custom-app build feasibility; task 09 repeats it on the real audit_practice app and subsequent release changes require revalidation.

## Acceptance Criteria

- [ ] The build suite runs twice from clean disposable resources and records the same declared dependency versions.
- [ ] Proof schema exists before test inserts; malformed target names and production-like configurations fail closed.
- [ ] All twelve P0 IDs are indexed once; missing live environment is visibly BLOCKED.
- [ ] Existing demo source and deployment settings remain unchanged except additive ignore entries.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
python3 scripts/p0/provision_local.py --validate-only
python3 scripts/p0/run.py --suite build --mode mock
python3 scripts/p0/run.py --suite build --mode live
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.
