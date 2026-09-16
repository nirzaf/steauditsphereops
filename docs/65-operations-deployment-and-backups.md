# 65 — Production deployment packaging, telemetry, backups, and runbooks

## Objective

Make the approved application operable and recoverable with reproducible deployment artifacts and measurable health controls.

## Context/Dependencies

**Milestone:** R5. **Requirement scope:** Section 26.2; FR-REC-004–008; FR-INT-001–007,012; ET-44.

**Dependencies:** [10 — Runtime configuration, secrets boundary, and diagnostic primitives](10-runtime-settings-and-telemetry.md); [64 — Next-period continuance, non-renewal, and controlled roll-forward](64-continuance-and-controlled-rollover.md)

**Execution gate:** file 64 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Frappe database API and transaction lifecycle](https://docs.frappe.io/framework/user/en/api/database); [Frappe background jobs](https://docs.frappe.io/framework/user/en/api/background_jobs); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `infra/production/Dockerfile`
- **Create:** `infra/production/compose.yml`
- **Create:** `infra/production/proxy.conf`
- **Create:** `infra/production/monitoring-rules.yml`
- **Create:** `scripts/production/deploy_plan.py`
- **Create:** `scripts/production/backup.py`
- **Create:** `docs/production/operations-runbook.md`
- **Create:** `docs/production/upgrade-runbook.md`
- **Create:** `production/audit_practice/audit_practice/tests/test_operations_configuration.py`
- **Modify:** `.github/workflows/production-ci.yml`
- **Modify:** `production/audit_practice/audit_practice/runtime/logging.py`
- **Modify:** `production/audit_practice/audit_practice/runtime/settings.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Build immutable images from exact Frappe/ERPNext/audit_practice pins and locked asset dependencies; do not bake secrets. Define app/websocket/scheduler/worker roles and appropriate private DB/Redis connectivity. Keep staging/demo/production secret stores, databases, buckets and egress targets disjoint.

2. Implement the availability topology actually required by approved NFRs. A single-host Compose deployment is not HA; if targets require redundant app/DB tiers, specify/test those resources and fail readiness until provisioned. Do not add Kubernetes or a service mesh without that need.

3. Monitor command latency/errors, scope conflicts, queue depth/outbox age, worker leases, provider throttling/unknown outcomes, permission drift, stale approvals, checkpoint lag and backup verification. Export redacted correlation-aware metrics/logs through the chosen existing monitoring system.

4. Back up MariaDB, required site config/encryption material and custom app/version metadata using approved secrets handling; verify SharePoint retention/export/reconstructability separately. Independent checkpoint/epoch authority must not be rolled back with the application backup. Test backup restoration, not just successful file creation.

5. Provide reviewed expand/migrate/verify deployment and rollback/forward-fix runbooks. MariaDB DDL and external effects are not undone by an application image rollback. Provide plan/validate commands with explicit human approval for deploy, consent, record policy and production data mutation.

## Acceptance Criteria

- [ ] Built image digest and migrations are traceable to the reviewed commit.
- [ ] Secrets/data isolation and private networking checks pass.
- [ ] Alerts trigger on controlled stalled-outbox/checkpoint/backup failures.
- [ ] Availability and recovery readiness reflect tested topology, not unsupported HA claims.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
python3 scripts/production/deploy_plan.py --environment staging --validate-only
python3 scripts/production/backup.py --environment staging --validate-only
./scripts/production/dev test audit_practice.tests.test_operations_configuration
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.
