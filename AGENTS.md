# AGENTS.md — Autonomous development contract for `steauditsphereops`

> Scope note: this repository (`nirzaf/steauditsphereops`, public, branch `main`) is a **build-plan archive, not application code**.
> It contains `docs/01`–`docs/72` — the execution contract, WBS index, and task specifications for STE AuditSphere Ops.
> Implementation described by those specs lands in the paths each spec names (`production/audit_practice/`, `scripts/wbs/`,
> `scripts/production/`, `infra/production/`, `docs/production/`) once their execution gates are ACCEPTED.
> Until then, the specs themselves are the normative source of truth — an agent must implement the specs, never silently rewrite them to fit its output.

Related repositories (do not confuse): `nirzaf/steauditqts` holds the Vue/Vite demonstrator and the source baseline
(`docs/requirements-manifest.md`, `src/v5Data.js`, `src/domain/traceability.js`, `docs/demo-shell-architecture.md`,
`package.json` at the pinned revision recorded in doc 01). The Merconiq/.NET ERP project is **out of scope** — never mix it in.

```text
Codex Agent
    │  writes code (Codex only — Cubic reviews, never writes)
    ▼
Pull Request (draft → ready)
    │
    ├──────────────► Deterministic CI (bench, WBS validators, security)
    │
    ├──────────────► Codex Review (read-only) ──────┐
    │                                               ├─► consolidated findings ─► Codex repair ─► new SHA ─► CI again ─► both reviews again
    └──────────────► Cubic Independent Review ──────┘
                            │
                            ▼
                    GitHub Ruleset (merge authority)
                            │
                            ▼
                       Merge Queue (integration proof)
                            │
                            ▼
                           main ─► Deployment (artifact already validated) ─► smoke tests ─► Done / Incident Issue ─► cycle
```

Fundamental rule: **AI may propose and modify code, but GitHub decides whether that code merges.**
Author (\u0043odex worker) ≠ Reviewers (Codex read-only + Cubic) ≠ Merge authority (Rulesets + Merge Queue).

---

## 1. Non-negotiable repository rules (from doc 01 — they outrank any agent preference)

1. **Ascending execution order.** Work `docs/01` → `docs/72` in order. Every task's Dependencies plus the immediately preceding
   execution gate are **acceptance gates**, not file-existence checks. A dependency is complete only when its acceptance criteria
   AND required external evidence are satisfied (`execution-status.json` state `ACCEPTED`).
2. **Do not parallelize spec tasks** without revalidating dependencies and path ownership. Shared-file changes are deliberately serialized.
3. **Never rename or relocate existing demo code** to satisfy a proposed path. A verified existing equivalent may be reused only with a
   recorded path mapping. Preserve the root npm package and demo entrypoint; keep the deployed Vue/Cloudflare demonstrator untouched.
4. **Never fabricate.** Do not invent questionnaire wording, methodology, template content, approvals, NFR values, licensing dispositions,
   or sign-offs. Record real references: Google Doc URL/revision, repo commit, source hashes, requirement IDs. The agent cannot manufacture
   owner/sponsor/professional-lead acceptance — unresolved decisions stay explicit and block dependent live proofs.
5. **Evidence hygiene.** Evidence must not contain passwords, tokens, real client data, or private source text beyond the authorized scope.
   Record tested commit, actual results, evidence location, and blockers in `docs/production/execution-status.json`
   (`NOT_STARTED / IN_PROGRESS / BLOCKED / ACCEPTED`). An unexecuted test definition is not evidence; mock-only, waived-without-owner,
   or stale proof for a required live experiment must fail validation (nonzero exit).
6. **One branch per Issue, minimal diff.** One numbered task at a time, one branch per task (`agent/<issue>-<slug>`), review the diff and
   relevant tests before moving on. No autonomous merge, deploy, tenant consent/retention change, or irreversible operation — those require the
   user-specified confirmation codeword. **Never invent a codeword.**
7. **Versioned vocabulary only.** Current v5 gates `G0`–`G10`, outputs `DOC-01`–`DOC-26`, service profiles
   (`ACCOUNTING_ONLY / EXTERNAL_AUDIT_ONLY / COMBINED / INTERNAL_AUDIT`). Never import older v3/v4 gate numbering.
8. **Pinned toolchain.** Exact Frappe/ERPNext tags AND commit hashes, Python, Node, package manager, MariaDB, Redis, Bench, and container-image
   digests live in `infra/production/versions.json`. No floating `latest`/`develop`. WBS validators use **Python standard library only**
   (`pathlib / json / graphlib`, `Decimal / csv / hashlib / unittest`); extra runtime deps only when the spec names them
   (`requests`, `msal`, `rfc8785`, `openpyxl`, `xlrd` only if XLS input is retained). Prefer built-in Frappe auth, PDF/Jinja, ORM/query
   builder, and Redis-backed workers over new services.
9. **Local conventions.** `REPO_ROOT` = repository root; production app at `$REPO_ROOT/production/audit_practice`;
   disposable benches under `$REPO_ROOT/.local/` (ignored — never commit a Bench, `sites/` secrets, vendor apps, or `node_modules`);
   test site `AUDIT_SITE=auditflow-test.localhost` (example only; real values in ignored local config, never in evidence).
   Final outputs must be reproducible from structured inputs and pinned templates — no cash-flow plugs or invented disclosures.

---

## 2. Separation of responsibilities

| Component | Responsibility | May write code? |
| --- | --- | --- |
| Codex Implementation Agent | Implement the Issue's scope | Yes (workspace only) |
| GitHub Actions CI | Build / test / static verification | No |
| Codex Reviewer | Intent, correctness, architecture (read-only) | No |
| Cubic | Independent second review (read-only) | No — never auto-modify branches |
| GitHub Rulesets | Policy enforcement | No |
| GitHub Merge Queue | Final integration verification | No |
| CD workflow | Deployment of the validated artifact | Deployment only |
| Incident workflow | Open a structured remediation Issue | Issue creation only |

Repair flow preserves independence: `Cubic finding → Codex repair task → new commit → CI → Codex re-review → Cubic re-review`.
No Ruleset bypass permission for any AI identity.

---

## 3. Repository control files (target state — doc 09 creates the CI side)

```text
/
├── AGENTS.md                  # this file — primary Codex instructions (AGENT.md is a pointer to it)
├── AGENT.md                   # pointer for humans/tools that look for the singular name
├── cubic.yaml                 # Cubic review rules as code
├── CODEOWNERS
├── CONTRIBUTING.md
├── docs/                      # 01–72 normative specs (this repo's core content) + docs/production/ outputs
├── .github/
│   ├── ISSUE_TEMPLATE/agent-task.yml
│   ├── pull_request_template.md
│   ├── agent/policy.yml  protected-paths.yml  review-schema.json  prompts/{planner,implementer,repair,reviewer}.md
│   └── workflows/  01-agent-plan  02-agent-dispatch  03-ci  04-ai-review  05-agent-repair  06-ai-review-gate  07-cd  08-incident-loop
└── scripts/
    ├── wbs/validate_*.py  check_*.py   # stdlib-only validators (baseline, contracts, versions, P0 exit, …)
    └── production/dev                # strict wrapper: doctor | bootstrap-test | migrate-test | test | test-all | build | serve-test
```

Nested `AGENTS.md` files may add tighter constraints for a module; they may never loosen this file.

---

## 4. Labels are the state machine (one principal state per Issue)

```text
agent:planning → agent:ready → agent:implementing → agent:pr-open → agent:verifying → agent:reviewing → agent:merge-ready → agent:merge-queue → agent:done
                                             ↘ failure → agent:repair ↘ (loops back; bounded — see §10)
Exceptions: agent:blocked  agent:conflict  agent:retry-exhausted  agent:policy-violation  agent:human-required
```

---

## 5. Issue-driven development contract

Every change begins with a structured GitHub Issue — never from an informal comment. The Issue is the machine-readable contract:

- WBS task (`docs/NN-*.md`), milestone (`R0`–`R4`), requirement scope (e.g. `FR-GATE-001–009`, `P0-01–12`)
- Execution gate: predecessor task(s) that must be ACCEPTED first (default: the immediately preceding doc)
- Source grounding: baseline links (Google Doc sections, `steauditqts` pinned paths, Frappe/Microsoft docs as the spec cites)
- Objective, Context, Scope (in/out), Target Files (create vs read/preserve), Architecture constraints
- Acceptance Criteria as checkboxes (copied from the spec, never weakened)
- Verification commands appropriate to the task, e.g.:
  `python scripts/wbs/validate_baseline.py`, `python scripts/wbs/check_versions.py`,
  `python scripts/wbs/validate_contracts.py`, `python scripts/wbs/check_p0_exit.py`,
  `scripts/production/dev doctor | bootstrap-test | migrate-test | test-all`,
  `bench --site "$AUDIT_SITE" run-tests --app audit_practice [--module <module>]`
- Risk (`low / medium / high`) — §11 controls what may auto-merge
- Evidence location (where proof outputs will be attached)

---

## 6. Planning, claiming, and parallel work

- Large features: Epic Issue → Codex Planner → dependency-ordered child Issues (schema → domain → services → API → UI → E2E),
  scheduler never runs a task whose predecessors are incomplete. R0 exit (doc 08) must be ACCEPTED before any production construction (doc 09+).
- Claim: branch `agent/<issue>-<slug>` (e.g. `agent/143-bootstrap-test-harness`) only if no open PR/branch exists for the Issue,
  dependencies are ACCEPTED, and state is `agent:ready`. Concurrency group `agent-issue-<number>`, `cancel-in-progress: false`.
- Parallelism: compare target paths against open autonomous PRs. Overlapping areas
  (`production/audit_practice/**`, `scripts/wbs/**`, `infra/production/**`, `docs/production/**`) → `agent:conflict`
  until the conflicting PR merges or safe coexistence is confirmed. Maximum parallelism without branch collisions.
- Bounded PRs: ~30 files / ~1000 lines. Oversized work goes back to the planner for splitting.

---

## 7. Implementation worker (Codex, least privilege)

Use the official Codex GitHub Action with a restricted permission profile; Codex edits its workspace while a trusted workflow does
Git/GitHub operations. Validate policy, then run the repo's documented commands — for WBS tasks the stdlib validators, for production
tasks the disposable-site lifecycle (fresh install → migrate → `run-tests` → build). Open a **Draft PR** first containing:
`Closes #<n>`, Objective, Acceptance Criteria (copied), Implementation summary, Files changed, Verification results (PASS/FAIL per command),
Architecture impact, Known risks, `AI Agent: Codex`.

---

## 8. Deterministic CI before any AI review (AI review never replaces it)

Formatting, lint, type checks, unit + integration tests, migration verification, dependency-pin validation, CodeQL, dependency review,
secret detection, protected-path policy. Draft → Ready-for-review only after baseline CI is green.
Required checks must handle both `pull_request` and `merge_group` events — PR-green ≠ merge-safe; PR + current-`main` green = merge-eligible.

---

## 9. Dual AI review

- **Codex Review** (first, read-only; `@codex review`, optionally focused: concurrency, regression risk, boundaries, security, acceptance criteria).
  An additional machine-readable gate may emit `codex-review-gate` (`pass` / `changes_required` + severity + findings) via a structured-output schema.
- **Cubic** (second, independent; `@cubic-dev-ai review this PR`, `ultrareview` for auth/isolation/races/migrations/compat on high-risk changes).
  `cubic.yaml` mirrors this file's invariants as review rules, e.g.: no raw SQL where the Frappe ORM/query builder suffices; flag missing
  tenant/company isolation filters; flag guest-role/permission relaxations; flag destructive schema operations outside the controlled-amendment
  workflow (doc 59); flag business logic in controllers/API layers; flag swallowed exceptions; flag new packages duplicating stdlib/Frappe
  functionality; flag secrets, live credentials, or real client data. Start Cubic auto-approval in **Shadow** mode; Live only for low-risk paths,
  never for `auth / security / migrations-destructive / .github / infra / billing / production-data`.

---

## 10. Self-healing with hard bounds (fix root causes, never weaken the gate)

CI/review failure → collect logs → Codex repair on the same PR (root-cause fix; smallest sufficient change; unrelated files untouched).
The repair prompt must forbid: disabling/skipping tests, weakening assertions or validation, suppressing warnings, changing acceptance criteria,
editing governance to pass. Bounds: CI repair 3 attempts, AI-review repair 3, merge-conflict repair 2, deployment auto-rollback 1 —
then `agent:retry-exhausted`, leaving full diagnostics on the PR. Spec changes to satisfy CI are forbidden (see §11) — a wrong spec needs a
governance Issue with owner sign-off, not a quiet edit.

---

## 11. Protected paths and risk lanes

Autonomous writers must not normally touch: `docs/01–72` (normative specs), `.github/**`, `AGENTS.md / AGENT.md`, `cubic.yaml`,
`CODEOWNERS`, `infra/production/versions.json`, `infra/production/poc-requirements.txt`, lockfiles, lint/security/coverage configuration.
Such changes need an explicit governance Issue (`risk:high` + `type:governance`) with human-owner approval.

- **Low** (docs fixes, isolated bugs, UI corrections, extra tests): may auto-merge when all gates pass.
- **Medium** (migrations, public API, dependencies, background jobs, cross-module refactors): full gates + merge queue; auto-merge only if every required policy passes.
- **High** (auth/authz, crypto, secrets, workflow permissions, production infra, destructive DB changes, billing, production-data mutation,
  any R0/R-exit sign-off claim): never merge on AI agreement alone → `agent:human-required`.

---

## 12. Ruleset, merge queue, and execution safety for `main`

Protect `main`: require PR + conversation resolution, dismiss stale approvals, block force pushes/deletions, require linear history,
require checks (build, unit, integration, architecture, CodeQL, dependency review, protected-paths, `codex-review-gate`), require Merge Queue
(which revalidates each PR against latest `main` — mandatory with parallel agents). Never run untrusted PR code under `pull_request_target`
with secrets (pwn-request risk); privileged mutation workflows must confirm the PR is intra-repo, carries `agent:managed`, matches the branch
convention, and came from the expected actor.

---

## 13. Deployment, verification, incidents

Deploy only the exact validated artifact: build immutable artifact → staging → smoke tests (health probe, critical APIs, DB connectivity,
auth smoke, worker health, critical journey) → production via GitHub Environments + OIDC (no long-lived credentials). An Issue with deployment
scope closes only after smoke tests pass. On failure: **roll back to last-known-healthy first**, verify, then auto-open an Incident Issue
(SHA, workflow run, failed probe with expected/actual, logs, last healthy SHA) that re-enters the lifecycle as `agent:plan`.

---

## 14. Status and audit trail (no comment spam)

One control comment per Issue (`<!-- autonomous-agent-status -->`: state, branch, PR, attempt counters, CI/AI-review checklist, last action —
updated in place). Leave evidence in GitHub: requirement → Issue; implementation → commits; reasoning → PR summary; verification → checks;
findings → PR reviews; repairs → commits; merge decision → Ruleset; integration proof → Merge Queue; deployment → environment history;
failure → Incident Issue.

---

## 15. Definition of done

An autonomous Issue is complete only when: acceptance criteria satisfied · branch from correct base · only relevant files changed ·
build/unit/integration/architecture/security checks green · Codex + Cubic reviews clean · conversations resolved · latest SHA reviewed ·
Merge Queue verification passed · PR merged · deployment + smoke tests passed (where in scope) · `execution-status.json` updated
(`ACCEPTED` with tested commit, results, evidence location) · Issue auto-closed · no follow-up failure. Anything less is IN PROGRESS.

Control hierarchy (higher overrides lower): **1. GitHub Rulesets · 2. deterministic tests/security policies · 3. architecture constraints ·
4. Issue acceptance criteria · 5. Cubic review · 6. Codex review · 7. implementation decisions.** Agents are replaceable; policies are not.
