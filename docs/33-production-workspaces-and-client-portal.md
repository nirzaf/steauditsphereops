# 33 — Production staff workspace and restricted client portal

## Objective

Deliver usable staff/client workflow surfaces backed only by the implemented authoritative APIs.

## Context/Dependencies

**Milestone:** R2. **Requirement scope:** FR-AUTH-010; FR-COM-001–005; FR-STATE-001–003; FR-NAV-001,004–007; FR-UX-001–002.

**Dependencies:** [23 — Service-specific gate evaluation and progress projections](23-gate-engine-and-projection-contract.md); [32 — PBC requests, bounded uploads, replacements, and review](32-pbc-commands-and-evidence-review.md)

**Execution gate:** file 32 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Demo shell responsibility boundaries](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/docs/demo-shell-architecture.md); [Existing prototype scripts and dependencies](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/package.json); [Frappe hooks](https://docs.frappe.io/framework/user/en/python-api/hooks).

## Target Files

- **Create:** `production/audit_practice/audit_practice/www/__init__.py`
- **Create:** `production/audit_practice/audit_practice/www/audit_portal.html`
- **Create:** `production/audit_practice/audit_practice/www/audit_portal.py`
- **Create:** `production/audit_practice/audit_practice/public/js/portal.js`
- **Create:** `production/audit_practice/audit_practice/public/css/portal.css`
- **Create:** `production/audit_practice/audit_practice/audit_operations/page/audit_workspace/audit_workspace.json`
- **Create:** `production/audit_practice/audit_practice/audit_operations/page/audit_workspace/audit_workspace.js`
- **Create:** `production/audit_practice/audit_practice/audit_operations/page/audit_workspace/audit_workspace.py`
- **Create:** `production/audit_practice/audit_practice/ui/__init__.py`
- **Create:** `production/audit_practice/audit_practice/ui/routes.py`
- **Create:** `tests/production/portal.spec.js`
- **Create:** `playwright.production.config.js`
- **Create:** `production/audit_practice/audit_practice/tests/test_portal_routes.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/page/__init__.py`
- **Create:** `production/audit_practice/audit_practice/audit_operations/page/audit_workspace/__init__.py`
- **Modify:** `production/audit_practice/audit_practice/hooks.py`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Use Frappe Desk for internal forms/tasks and an explicitly scoped custom portal for clients; reuse the existing Vue demo interaction patterns, not its local auth/state. Keep the production portal separate from root demo src/. Avoid an unrequested SPA rewrite or new frontend state framework.

2. Implement visible client/engagement/service/period, role assignments, task queues, breadcrumbs and exact next actions. Server routes and payload allowlists decide visibility. Switching selection clears old scoped data before loading; failed authoritative reads do not fall back to demo fixtures.

3. Wire client profile, quotation/EL review, setup, PBC request/upload/clarification, thread messages and permitted artifact center. Future accounting/audit/release routes remain disabled/unregistered until their APIs exist. Clients never see professional review notes, internal costs or admin diagnostics.

4. Add loading/error/empty/conflict feedback, unsaved-draft warning, keyboard focus/labels, responsive tables and server-sourced notification counts. Do not cache production workflow truth or bearer tokens in localStorage. Any local draft is clearly labeled and never automatically replayed.

5. Create separate Playwright config targeting the disposable Frappe site and a synthetic authenticated test setup. Use the existing pinned @playwright/test dependency, not the demo server config. Tests must navigate actual paths and perform one client-to-staff PBC handoff.

## Acceptance Criteria

- [ ] Client and staff can complete the R2 handoff without developer tools.
- [ ] Direct unauthorized routes and cross-client deep links deny data, not just hide navigation.
- [ ] Context selection, notification destination and PBC revision stay consistent after refresh.
- [ ] The existing root demo build/tests remain unaffected.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
npx playwright test --config playwright.production.config.js tests/production/portal.spec.js
./scripts/production/dev test audit_practice.tests.test_portal_routes
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.
