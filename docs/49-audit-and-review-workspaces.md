# 49 — Planning, fieldwork, reviewer, partner, and EQR workspaces

## Objective

Expose the audit lifecycle through task-focused role workspaces with exact evidence and review targets.

## Context/Dependencies

**Milestone:** R3. **Requirement scope:** FR-AUTH-010; FR-AUD; FR-REV; FR-NAV-006–007; FR-UX-001.

**Dependencies:** [33 — Production staff workspace and restricted client portal](33-production-workspaces-and-client-portal.md); [48 — Internal-audit engagements and continuing remediation](48-internal-audit-service-profile.md)

**Execution gate:** file 48 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** None beyond the accepted predecessor tasks.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [Demo shell responsibility boundaries](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/docs/demo-shell-architecture.md); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/public/js/audit_workspace.js`
- **Create:** `production/audit_practice/audit_practice/public/js/review_workspace.js`
- **Create:** `tests/production/audit.spec.js`
- **Create:** `production/audit_practice/audit_practice/tests/test_audit_routes.py`
- **Modify:** `production/audit_practice/audit_practice/public/js/portal.js`
- **Modify:** `production/audit_practice/audit_practice/ui/routes.py`
- **Modify:** `production/audit_practice/audit_practice/public/css/portal.css`
- **Modify:** `production/audit_practice/audit_practice/audit_operations/page/audit_workspace/audit_workspace.js`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Implement approved plan/risk/sample/workpaper forms and assigned procedure queue; show method/version, evidence identity, blockers and next reviewer. Use paginated data APIs and existing shared widgets, not a second business-rule store.

2. Reviewer UI displays the exact submitted snapshot and expected revision/generation used by approve/return/clear actions. Prevent mutable-working-preview versus immutable-command mismatch. A stale conflict prompts refresh and preserves unsent response text explicitly.

3. Partner/EQR UI separates manager recommendation, independent EQR, representations, opinion and final discussion. Technical admins and client users cannot access these action surfaces or underlying payloads.

4. Client management sees only permitted FS/MIR responses and management-action fields. Internal-audit views honor their service-specific output/approval profile. Disable release actions until R4 APIs exist.

5. Automate the preparer -> reviewer -> response -> independent clearance -> manager -> partner/EQR sequence with multiple test sessions, retaining exact assignment and scope across navigation. No production impersonation shortcut is added for testing.

## Acceptance Criteria

- [ ] Each actor completes only its assigned action in the same engagement.
- [ ] UI and command target the same frozen workpaper revision.
- [ ] Self-review, stale response and unauthorized deep link fail visibly.
- [ ] Cross-role state updates reflect authoritative data after reload.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
npx playwright test --config playwright.production.config.js tests/production/audit.spec.js
./scripts/production/dev test audit_practice.tests.test_audit_routes
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.
