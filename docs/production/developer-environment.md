# Developer environment and command ownership

This guide describes the reproducible v15.99.0 toolchain in
[`infra/production/versions.json`](../../infra/production/versions.json). The
versions file is authoritative for exact refs, commits, package versions, and
image digests; a local machine must not substitute `latest`, `develop`, a
branch, or a dependency range.

## Working directories

```text
REPO_ROOT=/path/to/STEAuditSphereOps
production/audit_practice/       # production app (created by WBS-09)
.local/                          # ignored disposable benches and POC sites
```

`REPO_ROOT` is the checked-out repository root. Disposable Bench/source
checkouts stay below `$REPO_ROOT/.local/`; they are never committed and never
point at a production host. Do not move or copy the read-only `steauditqts`
demo into this repository.

## Environment variables

| Variable | Example | Owner | Rule |
| --- | --- | --- | --- |
| `REPO_ROOT` | `/work/STEAuditSphereOps` | developer/CI | Must resolve to this repository root. |
| `AUDIT_SITE` | `auditflow-test.localhost` | WBS-09 wrapper | Disposable test site only; reject production hosts. |
| `POC_SITE` | `auditflow-poc.localhost` | WBS-04 runner | Separate allowlisted POC site; no real-client data. |
| `BENCH_ROOT` | `$REPO_ROOT/.local/bench` | WBS-04/WBS-09 | Ignored disposable Bench directory. |
| `FRAPPE_REF` | `v15.99.0` | WBS-03 pins | Must match the exact repository ref and commit in `versions.json`. |
| `ERPNEXT_REF` | `v15.99.0` | WBS-03 pins | Must match the exact repository ref and commit in `versions.json`. |

Credentials, tenant identifiers, cookies, and client records never belong in
these variables or in source control. Provider access is configured only in
the approved local/CI secret store by the authorized operator.

## Command ownership

The commands below are contracts, not commands available in this task. Do not
run them until their owning task creates and verifies them.

| Command | Owner | Purpose |
| --- | --- | --- |
| `python3 scripts/p0/run.py --suite <name> --mode mock|live` | WBS-04 | Bounded POC proof runner. |
| `./scripts/production/dev doctor` | WBS-09 | Disposable production-wrapper diagnostics. |
| `./scripts/production/dev bootstrap-test` | WBS-09 | Create the allowlisted test site and app registration. |
| `./scripts/production/dev migrate-test` | WBS-09 | Apply and verify additive migrations in the test site. |
| `./scripts/production/dev test <module>` | WBS-09 | Run one actual Frappe test module. |
| `./scripts/production/dev test-all` | WBS-09 | Run the complete configured suite. |
| `./scripts/production/dev build` | WBS-09 | Build the pinned app artifact. |
| `./scripts/production/dev serve-test` | WBS-09 | Serve only the disposable test site. |

The wrapper must reject production hosts, unsafe paths, unsupported
subcommands, shell evaluation, and unconfigured sites. Until WBS-04/09 are
accepted, a missing command is not a passing check.

## Bench and app layout contract

WBS-04 owns the disposable POC Bench and proof runner. WBS-09 owns the
production app at `production/audit_practice`, its test wrapper, and CI. A
locally sourced app is mounted from that path into the Bench and installed
with Bench's supported app command; an ignored Bench-side symlink/editable
install is acceptable. `sites/apps.txt` registration and `install-app` are
acceptance evidence for WBS-04/09, not assumptions made here.

## Compatibility and change control

The official Frappe v15 installation matrix requires Python 3.10+, Node 18+,
MariaDB 10.6.6+, Redis 6, and Yarn 1.12+; the selected pins stay inside that
envelope. Frappe v15.99.0's project metadata also constrains Python to
`>=3.10,<3.14`. Re-run `check_versions.py` and record a new reviewed commit
before changing a pin. A toolchain mismatch blocks feasibility work; it is not
resolved by an unreviewed upgrade or by changing the demo package lockfile.
