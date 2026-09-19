# Developer environment and command ownership

This guide describes the pinned v16.34.0 Frappe / v16.35.0 ERPNext candidate
toolchain in
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

## POC dependency lock

`infra/production/poc-requirements.txt` lists direct POC dependencies, and
`infra/production/poc-requirements.constraints.txt` records framework
compatibility constraints for their transitive dependencies.
`infra/production/poc-requirements.lock.txt` pins the transitive dependency
versions and hashes for CPython 3.14 on Linux x86_64. Install them in the
disposable POC environment with:

```bash
python3 -m pip install --require-hashes -r infra/production/poc-requirements.lock.txt
```

Requests 2.33.0 matches Frappe 16.34.0's `requests~=2.33.0` constraint. The
constraints file pins MSAL's transitive PyJWT dependency to 2.13.0, inside
Frappe's `PyJWT~=2.13.0` range, without adding another direct dependency.

This lock covers the POC transport/artifact packages only. The custom app's
transitive lock must be generated with its WBS-09 package manifest and verified
in the pinned Linux build environment.

## Environment variables

| Variable | Example | Owner | Rule |
| --- | --- | --- | --- |
| `REPO_ROOT` | `/work/STEAuditSphereOps` | developer/CI | Must resolve to this repository root. |
| `AUDIT_SITE` | `auditflow-test.localhost` | WBS-09 wrapper | Disposable test site only; reject production hosts. |
| `POC_SITE` | `auditflow-poc.localhost` | WBS-04 runner | Separate allowlisted POC site; no real-client data. |
| `BENCH_ROOT` | `$REPO_ROOT/.local/bench` | WBS-04/WBS-09 | Ignored disposable Bench directory. |
| `FRAPPE_REF` | `v16.34.0` | WBS-03 pins | Must match the exact repository ref and commit in `versions.json`. |
| `ERPNEXT_REF` | `v16.35.0` | WBS-03 pins | Must match the exact repository ref and commit in `versions.json`. |

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

The [official v16 installation matrix](https://docs.frappe.io/framework/user/en/installation)
lists Python 3.14, Node 24, MariaDB 11.8, Redis/Valkey 6+, Yarn 1.22+, and pip
25.3+. Frappe v16.34.0 metadata requires
Python `>=3.14,<3.15`; ERPNext v16.35.0 declares Frappe `>=16.21.0,<17.0.0`,
which includes v16.34.0. The [official Frappe Docker quick-start](https://github.com/frappe/frappe_docker/blob/main/pwd.yml)
uses MariaDB 11.8 and Redis 6.2. Exact source tags, commits, runtime patches,
and image digests are recorded in `versions.json`.

These checks establish a release-metadata-compatible candidate. After the
2026-09-19 restart, WSL 2.7.14.0 with kernel 6.18.33.2-2 and default WSL
version 2 was verified. Ubuntu 24.04 is running and its Docker integration is
verified through the production wrapper. Docker Desktop 4.91.0.239619,
Engine 29.8.0, and Compose 5.5.1 were verified. Bench 5.31.0 runs from the
pinned Linux environment; it cannot start on native Windows because its CLI
imports the POSIX-only `pwd` module. The selected Windows Python 3.14.7
reports pip 26.2.1, while the wrapper uses the pinned Linux runtime.

The 2026-09-19 disposable prototype run passed `doctor`, `bootstrap-test`,
`migrate-test`, the focused Frappe bootstrap test (2/2), the structural
Frappe harness test (30/30), and `build`. These runs use ignored local state
under `.local`; they do not by themselves reaccept WBS-03 because a clean
Linux install and independent review still need to be recorded. The existing
WBS-04 POC compose file remains pinned to the earlier v15 runtime; its separate
revalidation is required before v16 P0 evidence can be claimed. The WBS-04
spike package metadata also still declares Python `>=3.10,<3.14` and must be
revalidated against the v16 runtime.

## Revalidation checks

On 2026-09-18, the recorded Frappe v16.34.0, ERPNext v16.35.0, and Bench
v5.31.0 tags resolved to their pinned commit hashes. The version validator,
floating-reference negative fixture, and baseline validator passed. The
WBS-09 scaffold suite passed all 17 tests under uv-managed CPython 3.14.7.
The WBS-09 shell wrapper was executable from a read-only checkout mount in the
pinned Python 3.14.7 Linux image and rejected unsupported commands and a
production `AUDIT_SITE`; this does not prove a live Bench runtime.
The POC dependency lock resolved 13 packages and passed a hash-required
Linux-targeted install into an ignored directory; pip 25.3 also hash-checked
and downloaded the compatible Windows wheels.

The source checks and scaffold suite are now supplemented by the disposable
Linux Frappe run above. The system Python launcher still cannot select the
pinned 3.12 compatibility helper, so the standalone P0 validators ran with
the installed pinned CPython 3.12.11 executable and the structural suite also
passed inside Bench's pinned CPython 3.14.7 environment.

Prototype command results from Ubuntu 24.04 under WSL 2 on 2026-09-19:

```text
python3 scripts/wbs/check_versions.py infra/production/versions.json => PASS
python3 scripts/wbs/validate_baseline.py --root . => PASS
python3 scripts/wbs/validate_contracts.py --root . => PASS
./scripts/production/dev doctor => PASS
./scripts/production/dev bootstrap-test => PASS
./scripts/production/dev migrate-test => PASS
./scripts/production/dev test audit_practice.tests.test_bootstrap => 2/2 PASS
./scripts/production/dev test audit_practice.tests.test_skeleton => 30/30 PASS
./scripts/production/dev build => PASS
```
