# 27 — Approved artifact rendering and verified signature evidence

## Objective

Implement controlled document generation and signature evidence handling before quotations and engagement letters are issued.

## Context/Dependencies

**Milestone:** R2. **Requirement scope:** FR-PBC-009–012; FR-CL-006–007; FR-INT-008; DOC-01–08 and reusable output infrastructure.

**Dependencies:** [21 — Exact receipts, preserved snapshots, and canonical manifests](21-exact-snapshots-and-manifests.md); [26 — Scoped messages, notification outbox, and safe correspondence](26-portal-messaging-and-notification-services.md)

**Execution gate:** file 26 and all listed technical prerequisites must be ACCEPTED; read the shared execution contract in [01](01-execution-contract-and-baseline.md). Do not import or call a future task's unimplemented service.

**External prerequisites:** Professional owner supplies approved wording/templates and permitted manual/electronic signature policy; optional Documenso credentials are required only when enabled.

**Source grounding:** [Approved functional requirements and architecture, sections 1–27](https://docs.google.com/document/d/1W32RQd4pfetfNk8lANeM4NsdiZ1GW68aDBrBg4gdSxs); [v5 gates, document catalogue, and commercial fixture](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/v5Data.js); [Microsoft Purview records management](https://learn.microsoft.com/en-us/purview/records-management); [AT/ET/BT/VT scenarios and P0 experiments](https://github.com/nirzaf/steauditqts/blob/2898e44f6732c8b37c31ddfbeab0e322d7574ffe/src/domain/traceability.js).

## Target Files

- **Create:** `production/audit_practice/audit_practice/application/artifacts.py`
- **Create:** `production/audit_practice/audit_practice/application/signatures.py`
- **Create:** `production/audit_practice/audit_practice/integrations/signatures.py`
- **Create:** `production/audit_practice/audit_practice/templates/artifacts/base.html`
- **Create:** `production/audit_practice/audit_practice/templates/artifacts/onboarding.html`
- **Create:** `production/audit_practice/audit_practice/api/artifacts.py`
- **Create:** `production/audit_practice/audit_practice/tests/test_artifacts_and_signatures.py`
- **Modify:** `production/audit_practice/audit_practice/application/command_registry.py`
- **Modify:** `production/audit_practice/audit_practice/jobs/executors.py`
- **Modify:** `production/audit_practice/pyproject.toml`
- **Modify:** `infra/production/versions.json`

All paths above are repository-relative. Create parent/package directories as needed; never rename or relocate existing demo code to satisfy a proposed path. A verified existing equivalent may be reused with a recorded path mapping.

## Implementation Details

1. Use approved versioned Artifact Template contracts and Frappe Jinja/print/PDF utilities for server rendering. Escape untrusted content and reject missing required fields. Rendering uses a frozen manifest and never performs financial calculations or professional decisions in the template.

2. For an Office-editable document requirement, generate a Word working copy with a pinned python-docx dependency or an existing approved rendering facility; record the chosen dependency in versions.json before use. Office edits remain working content until a new exact snapshot is submitted. Do not promise pixel-identical PDF bytes across unpinned fonts/renderers.

3. Implement a narrow signature interface create_envelope, inspect_status and collect_signed_artifact. The default approved manual-signature route retains witnessed/verified scanned evidence and signatory authority. Enable Documenso only if the earlier decision register approves its endpoint/license/profile; verify webhook signatures and replay IDs before accepting callbacks.

4. Preserve approved input digest, signed output digest, signer identity, authority and provider/evidence record. A signature that alters bytes creates a derived snapshot, not a falsely identical checksum. No self-signed test certificate or mock callback counts as a real authorized signature.

5. Register DOC metadata and visibility for only the outputs implemented in this task; later modules supply their own templates. Disabled optional signature integration must provide a deliberate allowed manual flow, not a hidden failure or fabricated electronic signature.

## Acceptance Criteria

- [ ] Required-field failure blocks generation rather than inventing content.
- [ ] Untrusted HTML/script text is escaped in generated output.
- [ ] Signed output and approved input remain linked with distinct verified hashes.
- [ ] Forged/replayed signature callback and unauthorized client signatory are denied.
- [ ] Record the tested commit, actual results, evidence location and any external blocker in `docs/production/execution-status.json`; no unrun or skipped proof is marked ACCEPTED.
- [ ] After implementing the listed scripts/tests, run these commands from **REPO_ROOT** in the authorized environment:

```bash
./scripts/production/dev test audit_practice.tests.test_artifacts_and_signatures
```

Commands are required verification steps for the implementing agent, not results already obtained. `--validate-only`, `--dry-run` and mock runs do not replace required live/test-tenant observations or professional/operator approvals.
