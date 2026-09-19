"""Guarded local developer harness for the disposable production test site."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = REPO_ROOT / "production" / "audit_practice"
LOCAL_ROOT = REPO_ROOT / ".local"
STATE_ROOT = LOCAL_ROOT / "production"
SITE_NAME = "auditflow-test.localhost"
SITE_NAME_RE = re.compile(r"[a-z0-9](?:[a-z0-9_.-]*[a-z0-9])?")
WINDOWS_PATH_RE = re.compile(r"^([A-Za-z]):[\\/](.*)$")
WSL_PATH_RE = re.compile(r"^/mnt/([A-Za-z])(?:/(.*))?$")
ENV_FILE = STATE_ROOT / "runtime.env"
SITE_ADMIN_PASSWORD_FILE = STATE_ROOT / "site-admin-password"
MARIADB_DATA = STATE_ROOT / "mariadb"
COMPOSE_FILE = REPO_ROOT / "infra" / "production" / "dev.compose.yml"
VERSIONS_FILE = REPO_ROOT / "infra" / "production" / "versions.json"
FRAPPE_LOCAL_SOURCE = LOCAL_ROOT / "sources" / "frappe"
ERP_LOCAL_SOURCE = LOCAL_ROOT / "sources" / "erpnext"
SAFE_SUBPROCESS_ENV = frozenset(
    {
        "APPDATA",
        "COMMONPROGRAMFILES",
        "COMMONPROGRAMFILES(X86)",
        "COMSPEC",
        "HOMEDRIVE",
        "HOMEPATH",
        "HOME",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "LOCALAPPDATA",
        "PATH",
        "PATHEXT",
        "PROGRAMDATA",
        "PROGRAMFILES",
        "PROGRAMFILES(X86)",
        "SYSTEMDRIVE",
        "SYSTEMROOT",
        "TEMP",
        "TMP",
        "TZ",
        "USERPROFILE",
        "WINDIR",
    }
)


class HarnessError(RuntimeError):
    """A local precondition or command failed safely."""


def _is_link_like(path: Path) -> bool:
    junction_check = getattr(path, "is_junction", None)
    return path.is_symlink() or (junction_check is not None and junction_check())


def _bench_root_from_environment() -> Path:
    configured = os.environ.get("BENCH_ROOT", str(LOCAL_ROOT / "bench")).strip()
    if not configured:
        raise HarnessError("BENCH_ROOT must name an ignored disposable Bench directory.")
    if configured == "$REPO_ROOT" or configured.startswith(("$REPO_ROOT/", "$REPO_ROOT\\")):
        configured = str(REPO_ROOT) + configured[len("$REPO_ROOT") :]

    candidate = Path(configured)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    candidate = Path(os.path.abspath(candidate))
    local_root = Path(os.path.abspath(LOCAL_ROOT))
    if candidate == local_root or not candidate.is_relative_to(local_root):
        raise HarnessError("BENCH_ROOT must be a child of this repository's .local directory.")

    current = candidate
    while current != local_root:
        if _is_link_like(current):
            raise HarnessError(f"Refusing linked disposable Bench path: {current}")
        current = current.parent
    return candidate


BENCH_ROOT = _bench_root_from_environment()
NODE_DEPENDENCIES_MARKER = BENCH_ROOT / ".audit-node-dependencies.ready"


def _subprocess_environment() -> dict[str, str]:
    """Pass only OS/runtime essentials to children that may execute app code."""
    environment = {
        key: value
        for key, value in os.environ.items()
        if key.upper() in SAFE_SUBPROCESS_ENV
    }
    environment.update(
        {
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    return environment


def _assert_path_below_local(path: Path, label: str) -> None:
    local_root = Path(os.path.abspath(LOCAL_ROOT))
    candidate = Path(os.path.abspath(path))
    if candidate == local_root or not candidate.is_relative_to(local_root):
        raise HarnessError(f"{label} path must stay below .local: {path}")
    current = candidate
    while current != local_root:
        if _is_link_like(current):
            raise HarnessError(f"Refusing linked {label} path: {current}")
        current = current.parent
    if not path.resolve().is_relative_to(LOCAL_ROOT.resolve()):
        raise HarnessError(f"{label} path resolves outside .local: {path}")


def _read_versions() -> dict:
    return json.loads(VERSIONS_FILE.read_text(encoding="utf-8"))


def _pins() -> tuple[dict[str, dict], dict[str, dict]]:
    manifest = _read_versions()
    repositories = {item["name"]: item for item in manifest["repositories"]}
    images = {item["name"]: item for item in manifest["images"]}
    return repositories, images


def _run(
    argv: Sequence[str],
    *,
    cwd: Path = REPO_ROOT,
    capture: bool = False,
    timeout: int = 1800,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(argv),
        cwd=cwd,
        check=False,
        capture_output=capture,
        env=_subprocess_environment(),
        text=True,
        timeout=timeout,
    )
    if result.returncode:
        if capture and result.stderr:
            sys.stderr.write(result.stderr)
        raise HarnessError(f"Command failed with exit code {result.returncode}: {argv[0]}")
    return result


def _probe(argv: Sequence[str], *, cwd: Path = REPO_ROOT) -> bool:
    try:
        result = subprocess.run(
            list(argv),
            cwd=cwd,
            check=False,
            capture_output=True,
            env=_subprocess_environment(),
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def _bench_platform_failure(os_name: str) -> str | None:
    if os_name == "nt":
        return (
            "the pinned Bench CLI requires a POSIX/Linux runtime; native Windows "
            "Python does not provide the Unix pwd module. Run this harness from Linux or WSL."
        )
    return None


def _site_from_environment() -> str:
    site = os.environ.get("AUDIT_SITE", SITE_NAME)
    if not SITE_NAME_RE.fullmatch(site) or site != SITE_NAME:
        raise HarnessError(
            f"AUDIT_SITE must be exactly {SITE_NAME}; refusing any other site."
        )
    return site


def _assert_state_is_ignored_and_contained() -> None:
    if _is_link_like(LOCAL_ROOT):
        raise HarnessError(f"Refusing symlinked local state root: {LOCAL_ROOT}")
    local_resolved = LOCAL_ROOT.resolve()
    repo_resolved = REPO_ROOT.resolve()
    if not local_resolved.is_relative_to(repo_resolved):
        raise HarnessError("The .local state directory resolves outside the repository.")
    for path in (
        STATE_ROOT,
        BENCH_ROOT,
        ENV_FILE,
        SITE_ADMIN_PASSWORD_FILE,
        MARIADB_DATA,
        FRAPPE_LOCAL_SOURCE,
        ERP_LOCAL_SOURCE,
    ):
        _assert_path_below_local(path, "disposable")
    for relative in (
        BENCH_ROOT.relative_to(REPO_ROOT).as_posix(),
        FRAPPE_LOCAL_SOURCE.relative_to(REPO_ROOT).as_posix(),
        ERP_LOCAL_SOURCE.relative_to(REPO_ROOT).as_posix(),
        SITE_ADMIN_PASSWORD_FILE.relative_to(REPO_ROOT).as_posix(),
        ".local/production/runtime.env",
        ".local/production/mariadb",
    ):
        ignored = subprocess.run(
            ["git", "check-ignore", "--quiet", "--no-index", "--", relative],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            env=_subprocess_environment(),
            text=True,
        )
        if ignored.returncode != 0:
            raise HarnessError(f"Disposable state is not ignored by Git: {relative}")


def _tool_version(name: str, argv: Sequence[str], pattern: str) -> str | None:
    executable = shutil.which(name)
    if executable is None:
        return None
    try:
        result = subprocess.run(
            [executable, *argv],
            check=False,
            capture_output=True,
            env=_subprocess_environment(),
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    match = re.search(pattern, result.stdout + "\n" + result.stderr)
    return match.group(1) if match else None


def _check_runtime(*, require_docker: bool = True) -> list[str]:
    runtime = _read_versions()["runtime"]
    expected = {
        "python": runtime["python"]["version"],
        "node": runtime["node"]["version"],
        "npm": runtime["npm"]["version"],
        "yarn": runtime["yarn"]["version"],
        "pip": runtime["pip"]["version"],
        "bench": runtime["bench"]["version"],
    }
    commands = {
        "node": ("node", ["--version"], r"v?([0-9]+\.[0-9]+\.[0-9]+)"),
        "npm": ("npm", ["--version"], r"([0-9]+\.[0-9]+\.[0-9]+)"),
        "yarn": ("yarn", ["--version"], r"([0-9]+\.[0-9]+\.[0-9]+)"),
    }
    failures: list[str] = []
    observed_python = ".".join(str(part) for part in sys.version_info[:3])
    if observed_python != expected["python"]:
        failures.append(f"python: expected {expected['python']}, found {observed_python}")
    else:
        print(f"python: {observed_python}")
    try:
        pip_result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            check=False,
            capture_output=True,
            env=_subprocess_environment(),
            text=True,
            timeout=20,
        )
        pip_match = re.search(
            r"\bpip\s+([0-9]+\.[0-9]+(?:\.[0-9]+)?)",
            pip_result.stdout + "\n" + pip_result.stderr,
        )
        observed_pip = pip_match.group(1) if pip_result.returncode == 0 and pip_match else None
    except (OSError, subprocess.TimeoutExpired):
        observed_pip = None
    if observed_pip != expected["pip"]:
        failures.append(f"pip: expected {expected['pip']}, found {observed_pip or 'unavailable'}")
    else:
        print(f"pip: {observed_pip}")
    for key, (name, argv, pattern) in commands.items():
        observed = _tool_version(name, argv, pattern)
        if observed != expected[key]:
            failures.append(
                f"{key}: expected {expected[key]}, found {observed or 'unavailable'}"
            )
        else:
            print(f"{key}: {observed}")
    bench_platform_failure = _bench_platform_failure(os.name)
    if bench_platform_failure is not None:
        failures.append(f"bench: {bench_platform_failure}")
    else:
        observed_bench = _tool_version(
            "bench", ["--version"], r"\b([0-9]+\.[0-9]+\.[0-9]+)\b"
        )
        if observed_bench != expected["bench"]:
            failures.append(
                f"bench: expected {expected['bench']}, found {observed_bench or 'unavailable'}"
            )
        else:
            print(f"bench: {observed_bench}")
    if require_docker:
        docker_version = _tool_version(
            "docker", ["compose", "version", "--short"], r"v?([0-9]+\.[0-9]+\.[0-9]+)"
        )
        if docker_version is None:
            failures.append("docker compose: unavailable")
        else:
            print(f"docker compose: {docker_version}")
    return failures


def _bench_executable() -> str:
    executable = shutil.which("bench")
    if executable is None:
        raise HarnessError("Pinned Bench CLI is unavailable on PATH.")
    expected = _read_versions()["runtime"]["bench"]["version"]
    result = _run([executable, "--version"], capture=True)
    observed = re.search(r"\b([0-9]+\.[0-9]+\.[0-9]+)\b", result.stdout + result.stderr)
    found = observed.group(1) if observed else "unavailable"
    if found != expected:
        raise HarnessError(f"Bench CLI mismatch: expected {expected}, found {found}.")
    return executable


def _bench_python() -> Path:
    candidates = (
        BENCH_ROOT / "env" / "bin" / "python",
        BENCH_ROOT / "env" / "Scripts" / "python.exe",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise HarnessError("The disposable Bench Python environment is missing.")


def _verify_bench_python() -> None:
    expected = _read_versions()["runtime"]["python"]["version"]
    result = _run([str(_bench_python()), "--version"], capture=True)
    observed = re.search(r"Python\s+([0-9]+\.[0-9]+\.[0-9]+)", result.stdout + result.stderr)
    if observed is None or observed.group(1) != expected:
        found = observed.group(1) if observed else "unavailable"
        raise HarnessError(f"Bench Python mismatch: expected {expected}, found {found}.")
    pip_expected = _read_versions()["runtime"]["pip"]["version"]
    result = _run(
        [str(_bench_python()), "-m", "pip", "--version"],
        capture=True,
    )
    pip_match = re.search(r"\bpip\s+([0-9]+\.[0-9]+(?:\.[0-9]+)?)", result.stdout)
    pip_found = pip_match.group(1) if pip_match else "unavailable"
    if pip_found != pip_expected:
        raise HarnessError(
            f"Bench pip mismatch: expected {pip_expected}, found {pip_found}."
        )


def _bench_command(
    args: Sequence[str], *, capture: bool = False
) -> subprocess.CompletedProcess[str]:
    _assert_state_is_ignored_and_contained()
    if not BENCH_ROOT.is_dir():
        raise HarnessError("Disposable Bench is not initialized; run bootstrap-test.")
    _assert_bench_layout()
    executable = _bench_executable()
    _verify_bench_python()
    return _run([executable, *args], cwd=BENCH_ROOT, capture=capture)


def _assert_bench_layout() -> None:
    root = BENCH_ROOT.resolve()
    for name in ("apps", "sites", "env"):
        path = BENCH_ROOT / name
        if _is_link_like(path) or not path.resolve().is_relative_to(root):
            raise HarnessError(f"Disposable Bench {name} path is linked or escapes the Bench.")


def _bench_app(name: str) -> Path:
    _assert_bench_layout()
    path = BENCH_ROOT / "apps" / name
    if _is_link_like(path):
        raise HarnessError(f"Refusing linked Bench application directory: {name}")
    if not path.resolve().is_relative_to((BENCH_ROOT / "apps").resolve()):
        raise HarnessError(f"Bench application path escapes the disposable Bench: {name}")
    return path


def _compose_prefix() -> list[str]:
    project_key = _canonical_path_alias(REPO_ROOT.resolve().as_posix())
    return [
        "docker",
        "compose",
        "--project-name",
        "steauditsphere-" + hashlib.sha256(project_key.encode()).hexdigest()[:10],
        "--env-file",
        str(ENV_FILE),
        "--file",
        str(COMPOSE_FILE),
    ]


def _canonical_path_alias(value: str) -> str:
    """Canonicalize Windows and WSL spellings for stable local identities."""
    candidate = value.replace("\\", "/")
    windows_match = WINDOWS_PATH_RE.fullmatch(candidate)
    if windows_match:
        drive, remainder = windows_match.groups()
        candidate = f"/mnt/{drive.lower()}/{remainder}"
    else:
        wsl_match = WSL_PATH_RE.fullmatch(candidate)
        if wsl_match:
            drive, remainder = wsl_match.groups()
            candidate = f"/mnt/{drive.lower()}/{remainder or ''}"
    return candidate.rstrip("/").casefold()


def _resolve_runtime_data_path(value: str, *, host_os: str | None = None) -> Path:
    """Resolve a runtime.env path while allowing the two local host spellings."""
    if not isinstance(value, str) or not value.strip():
        return Path("").resolve()
    platform = os.name if host_os is None else host_os
    candidate = value.strip()
    if platform == "nt":
        match = WSL_PATH_RE.fullmatch(candidate)
        if match:
            drive, remainder = match.groups()
            candidate = f"{drive.upper()}:/{remainder or ''}"
    else:
        match = WINDOWS_PATH_RE.fullmatch(candidate)
        if match:
            drive, remainder = match.groups()
            remainder = remainder.replace("\\", "/")
            candidate = f"/mnt/{drive.lower()}/{remainder}"
    return Path(candidate).resolve()


def _write_runtime_env(*, create: bool = True) -> dict[str, str]:
    _assert_state_is_ignored_and_contained()
    if MARIADB_DATA.is_symlink():
        raise HarnessError(f"Refusing symlinked MariaDB data directory: {MARIADB_DATA}")
    data_path = MARIADB_DATA.resolve()
    values: dict[str, str]
    runtime_env_needs_rewrite = False
    if _is_link_like(ENV_FILE):
        raise HarnessError(f"Refusing symlinked runtime config: {ENV_FILE}")
    if ENV_FILE.exists():
        values = {}
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key] = value
        password = values.get("MARIADB_ROOT_PASSWORD", "")
        if not re.fullmatch(r"[0-9a-f]{48}", password):
            raise HarnessError("Existing runtime.env has an invalid local DB password.")
        configured_data_path = _resolve_runtime_data_path(
            values.get("AUDIT_DB_DATA_PATH", "")
        )
        if configured_data_path != data_path:
            raise HarnessError("Existing runtime.env points outside this disposable state path.")
        # The ignored state file may have been created from the other local
        # host (Windows or WSL). Rewrite only the equivalent path spelling so
        # Docker Compose receives a path valid for the current host.
        runtime_env_needs_rewrite = values.get("AUDIT_DB_DATA_PATH") != data_path.as_posix()
        values["AUDIT_DB_DATA_PATH"] = data_path.as_posix()
    else:
        if not create:
            raise HarnessError("Local runtime.env is missing; run bootstrap-test first.")
        STATE_ROOT.mkdir(parents=True, exist_ok=True)
        _, images = _pins()
        values = {
            "MARIADB_ROOT_PASSWORD": secrets.token_hex(24),
            "AUDIT_DB_DATA_PATH": data_path.as_posix(),
            "AUDIT_MARIADB_IMAGE": images["mariadb"]["reference"],
            "AUDIT_REDIS_IMAGE": images["redis"]["reference"],
        }
        lines = [f"{key}={value}" for key, value in values.items()]
        file_descriptor = os.open(
            ENV_FILE,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
        with os.fdopen(file_descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write("\n".join(lines) + "\n")
    _, images = _pins()
    expected_values = {
        "AUDIT_DB_DATA_PATH": data_path.as_posix(),
        "AUDIT_MARIADB_IMAGE": images["mariadb"]["reference"],
        "AUDIT_REDIS_IMAGE": images["redis"]["reference"],
    }
    if set(values) != {
        "MARIADB_ROOT_PASSWORD",
        "AUDIT_DB_DATA_PATH",
        "AUDIT_MARIADB_IMAGE",
        "AUDIT_REDIS_IMAGE",
    }:
        raise HarnessError("Local runtime.env is missing required pinned values.")
    if not re.fullmatch(r"[0-9a-f]{48}", values["MARIADB_ROOT_PASSWORD"]):
        raise HarnessError("Existing runtime.env has an invalid local DB password.")
    for key, expected in expected_values.items():
        if values.get(key) != expected:
            raise HarnessError(f"Existing runtime.env has an unexpected value for {key}.")
    if runtime_env_needs_rewrite:
        ENV_FILE.write_text(
            "\n".join(f"{key}={value}" for key, value in values.items()) + "\n",
            encoding="utf-8",
        )
    if create:
        data_path.mkdir(parents=True, exist_ok=True)
    elif not data_path.is_dir():
        raise HarnessError("Disposable MariaDB data directory is missing.")
    return values


def _wait_for_services() -> None:
    deadline = time.monotonic() + 150
    maria_ok = redis_ok = False
    while time.monotonic() < deadline:
        maria_ok = _probe(
            [
                *_compose_prefix(),
                "exec",
                "-T",
                "mariadb",
                "healthcheck.sh",
                "--connect",
                "--innodb_initialized",
            ]
        )
        redis_ok = _probe(
            [*_compose_prefix(), "exec", "-T", "redis", "redis-cli", "ping"]
        )
        if maria_ok and redis_ok:
            print("MariaDB and Redis are healthy.")
            return
        time.sleep(2)
    raise HarnessError(
        f"Local services did not become healthy (MariaDB={maria_ok}, Redis={redis_ok})."
    )


def _ensure_disposable_services() -> None:
    """Start the allowlisted database and Redis services before site commands."""
    _write_runtime_env(create=False)
    _run([*_compose_prefix(), "up", "-d", "mariadb", "redis"], cwd=REPO_ROOT)
    _wait_for_services()


def _verify_git_commit(path: Path, expected: str, label: str) -> None:
    actual = _run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture=True,
    ).stdout.strip()
    if actual != expected:
        raise HarnessError(f"{label} source commit mismatch: expected {expected}, found {actual}.")
    status = _run(
        ["git", "-C", str(path), "status", "--porcelain", "--untracked-files=all"],
        cwd=REPO_ROOT,
        capture=True,
    ).stdout
    if status:
        raise HarnessError(f"{label} source checkout is not clean; refusing to process it.")


def _prepare_pinned_source(path: Path, pin: dict, label: str) -> Path:
    """Materialize the pinned tag locally and verify its commit before Bench uses it."""
    _assert_state_is_ignored_and_contained()
    _assert_path_below_local(path, f"{label} source")

    created = not path.exists()
    if created:
        path.parent.mkdir(parents=True, exist_ok=True)
        _run(["git", "init", str(path)], cwd=REPO_ROOT)
        _run(["git", "-C", str(path), "remote", "add", "origin", pin["url"]])
    elif not (path / ".git").exists():
        raise HarnessError(f"Existing {label} source is not a Git checkout: {path}")
    elif _is_link_like(path / ".git"):
        raise HarnessError(f"Refusing linked Git metadata for {label}: {path}")

    origin = _run(
        ["git", "-C", str(path), "remote", "get-url", "origin"],
        capture=True,
    ).stdout.strip()
    if origin != pin["url"]:
        raise HarnessError(f"{label} source origin does not match the pinned repository URL.")

    tag_ref = f"refs/tags/{pin['ref']}"
    has_tag = _probe(
        ["git", "-C", str(path), "show-ref", "--verify", "--quiet", tag_ref]
    )
    if not has_tag:
        _run(
            [
                "git",
                "-C",
                str(path),
                "fetch",
                "--depth=1",
                "--filter=blob:none",
                "origin",
                f"{tag_ref}:{tag_ref}",
            ],
            cwd=REPO_ROOT,
            timeout=1800,
        )
    tag_commit = _run(
        ["git", "-C", str(path), "rev-parse", "--verify", f"{tag_ref}^{{commit}}"],
        capture=True,
    ).stdout.strip()
    if tag_commit != pin["commit"]:
        raise HarnessError(
            f"{label} ref {pin['ref']} does not resolve to its pinned commit "
            f"{pin['commit']} (found {tag_commit})."
        )

    if created:
        _run(["git", "-C", str(path), "checkout", "--detach", pin["commit"]])
    _verify_git_commit(path, pin["commit"], label)
    return path


def _configure_bench() -> None:
    _assert_bench_layout()
    config_path = BENCH_ROOT / "sites" / "common_site_config.json"
    if _is_link_like(config_path) or not config_path.is_file():
        raise HarnessError("Bench common_site_config.json is missing or symlinked.")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise HarnessError("Bench common site config is not a JSON object.")
    config.update(
        {
            "db_host": "127.0.0.1",
            "db_port": 3307,
            "redis_cache": "redis://127.0.0.1:16379/0",
            "redis_queue": "redis://127.0.0.1:16379/1",
            "redis_socketio": "redis://127.0.0.1:16379/2",
        }
    )
    config_path.write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _bench_init_command(bench: str, frappe_source: Path, frappe_ref: str) -> list[str]:
    """Build a Bench without local Redis processes; this harness uses its Redis container."""
    return [
        bench,
        "init",
        str(BENCH_ROOT),
        "--frappe-path",
        str(frappe_source),
        "--frappe-branch",
        frappe_ref,
        "--skip-redis-config-generation",
        "--python",
        sys.executable,
    ]


def _node_requirements_commands(
    bench_root: Path,
) -> tuple[tuple[Path, tuple[str, ...]], ...]:
    """Build frozen Yarn commands for the pinned app dependency trees."""
    return (
        (
            bench_root / "apps" / "frappe",
            ("yarn", "install", "--check-files", "--frozen-lockfile"),
        ),
        (
            bench_root / "apps" / "erpnext",
            (
                "yarn",
                "install",
                "--check-files",
                "--frozen-lockfile",
                "--ignore-scripts",
            ),
        ),
        (
            bench_root / "apps" / "erpnext" / "banking",
            (
                "yarn",
                "install",
                "--check-files",
                "--frozen-lockfile",
                "--ignore-scripts",
            ),
        ),
    )


def _node_dependencies_marker_payload() -> dict[str, str]:
    repositories, _ = _pins()
    return {
        "frappe": repositories["frappe"]["commit"],
        "erpnext": repositories["erpnext"]["commit"],
    }


def _node_dependencies_are_ready() -> bool:
    if _is_link_like(NODE_DEPENDENCIES_MARKER) or not NODE_DEPENDENCIES_MARKER.is_file():
        return False
    try:
        observed = json.loads(NODE_DEPENDENCIES_MARKER.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if observed != _node_dependencies_marker_payload():
        return False
    required = (
        BENCH_ROOT / "apps" / "frappe" / "node_modules" / "fast-glob",
        BENCH_ROOT / "apps" / "erpnext" / "node_modules",
        BENCH_ROOT / "apps" / "erpnext" / "banking" / "node_modules",
    )
    return all(path.is_dir() and not _is_link_like(path) for path in required)


def _install_node_dependencies() -> None:
    if _node_dependencies_are_ready():
        return
    for cwd, command in _node_requirements_commands(BENCH_ROOT):
        if _is_link_like(cwd) or not cwd.is_dir() or not (cwd / "package.json").is_file():
            raise HarnessError(f"Pinned Node dependency source is missing: {cwd}")
        _run(list(command), cwd=cwd, timeout=3600)
    if _is_link_like(NODE_DEPENDENCIES_MARKER):
        raise HarnessError("Refusing linked Node dependency marker.")
    NODE_DEPENDENCIES_MARKER.write_text(
        json.dumps(_node_dependencies_marker_payload(), sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _install_frappe_app(frappe_app: Path, bench_python: Path) -> None:
    """Ensure a retry after partial Bench setup installs Frappe's dependencies."""
    _run(
        [
            str(bench_python),
            "-m",
            "pip",
            "install",
            "--quiet",
            "--editable",
            str(frappe_app),
        ],
        cwd=BENCH_ROOT,
        timeout=3600,
    )


def _ensure_bench_apps_file(app_names: Sequence[str]) -> None:
    """Materialize Bench's legacy app registry when local app installs omit it."""
    _assert_bench_layout()
    apps_txt = BENCH_ROOT / "sites" / "apps.txt"
    if _is_link_like(apps_txt):
        raise HarnessError("Bench sites/apps.txt is missing or symlinked.")
    if apps_txt.exists() and not apps_txt.is_file():
        raise HarnessError("Bench sites/apps.txt is not a regular file.")
    entries = apps_txt.read_text(encoding="utf-8").splitlines() if apps_txt.exists() else []
    for app_name in app_names:
        if app_name not in entries:
            entries.append(app_name)
    apps_txt.write_text("\n".join(entries) + "\n", encoding="utf-8")


def _ensure_app_link() -> None:
    _assert_bench_layout()
    apps_path = BENCH_ROOT / "apps" / "audit_practice"
    source = APP_ROOT.resolve(strict=True)
    if apps_path.is_symlink():
        if apps_path.resolve() != source:
            raise HarnessError("Existing audit_practice app link points to a different source.")
    elif apps_path.exists():
        raise HarnessError("Existing audit_practice path is not the expected source link.")
    else:
        apps_path.symlink_to(source, target_is_directory=True)

    apps_txt = BENCH_ROOT / "sites" / "apps.txt"
    if _is_link_like(apps_txt) or not apps_txt.is_file():
        raise HarnessError("Bench sites/apps.txt is missing or symlinked.")
    entries = apps_txt.read_text(encoding="utf-8").splitlines()
    if "audit_practice" not in entries:
        apps_txt.write_text("\n".join([*entries, "audit_practice"]) + "\n", encoding="utf-8")
    _validate_apps_registration(apps_txt)

    _run(
        [
            str(_bench_python()),
            "-m",
            "pip",
            "install",
            "--editable",
            str(APP_ROOT.resolve()),
        ],
        cwd=BENCH_ROOT,
        timeout=900,
    )
    script = (
        "import audit_practice, pathlib, sys; "
        "expected = pathlib.Path(sys.argv[1]).resolve(); "
        "actual = pathlib.Path(audit_practice.__file__).resolve(); "
        "assert actual.is_relative_to(expected), (actual, expected); "
        "print(actual)"
    )
    _run(
        [str(_bench_python()), "-c", script, str(APP_ROOT.resolve())],
        cwd=BENCH_ROOT,
        capture=True,
    )


def _assert_app_link() -> Path:
    app_path = BENCH_ROOT / "apps" / "audit_practice"
    if not app_path.is_symlink():
        raise HarnessError("Nested audit_practice source is not mounted into Bench.")
    expected_app = APP_ROOT.resolve(strict=True)
    if _is_link_like(APP_ROOT) or not expected_app.is_relative_to(REPO_ROOT.resolve()):
        raise HarnessError("The nested app source resolves outside this repository.")
    if app_path.resolve(strict=True) != expected_app:
        raise HarnessError("Nested audit_practice source link points outside this checkout.")
    _validate_apps_registration(BENCH_ROOT / "sites" / "apps.txt")
    return app_path


def _validate_apps_registration(apps_txt: Path) -> None:
    if _is_link_like(apps_txt) or not apps_txt.is_file():
        raise HarnessError("Bench sites/apps.txt is missing or symlinked.")
    entries = apps_txt.read_text(encoding="utf-8").splitlines()
    if entries.count("audit_practice") != 1:
        raise HarnessError(
            "Bench sites/apps.txt must register audit_practice exactly once."
        )


def _list_installed_apps(site: str) -> set[str]:
    result = _bench_command(["--site", site, "list-apps"], capture=True)
    installed: set[str] = set()
    for line in result.stdout.splitlines():
        words = line.strip().split()
        if words and re.fullmatch(r"[a-z][a-z0-9_]*", words[0]):
            installed.add(words[0])
    return installed


def _site_admin_password(*, create: bool) -> str:
    _assert_state_is_ignored_and_contained()
    if _is_link_like(SITE_ADMIN_PASSWORD_FILE):
        raise HarnessError("Refusing a linked local test-site administrator credential file.")
    if SITE_ADMIN_PASSWORD_FILE.is_file():
        password = SITE_ADMIN_PASSWORD_FILE.read_text(encoding="utf-8")
        if not re.fullmatch(r"[A-Za-z0-9_-]{40}", password):
            raise HarnessError("Local test-site administrator credential file is malformed.")
        return password
    if not create:
        raise HarnessError(
            "The local test-site administrator credential is unavailable. Restore "
            f"{SITE_ADMIN_PASSWORD_FILE} from your private local backup before serving the site."
        )

    SITE_ADMIN_PASSWORD_FILE.parent.mkdir(parents=True, exist_ok=True)
    password = secrets.token_urlsafe(30)
    try:
        descriptor = os.open(
            SITE_ADMIN_PASSWORD_FILE,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            0o600,
        )
    except FileExistsError:
        return _site_admin_password(create=False)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        stream.write(password)
    return password


def _ensure_site_and_apps(site: str, db_password: str) -> None:
    _assert_bench_layout()
    _ensure_disposable_services()
    site_root = BENCH_ROOT / "sites" / site
    site_config = site_root / "site_config.json"
    if _is_link_like(site_root):
        raise HarnessError("Refusing a symlinked test-site directory.")
    if _is_link_like(site_config):
        raise HarnessError("Refusing a symlinked test-site config.")
    if not site_config.exists():
        if site_root.exists():
            raise HarnessError("A partial test-site directory exists; refusing to overwrite it.")
        _bench_command(
            [
                "new-site",
                site,
                "--db-host",
                "127.0.0.1",
                "--db-port",
                "3307",
                "--mariadb-root-password",
                db_password,
                "--admin-password",
                _site_admin_password(create=True),
            ]
        )
    else:
        _site_admin_password(create=False)
    _validate_site_routes(site, require_tests=False)
    if "erpnext" not in _list_installed_apps(site):
        _bench_command(["--site", site, "install-app", "erpnext"])
    if "audit_practice" not in _list_installed_apps(site):
        _bench_command(["--site", site, "install-app", "audit_practice"])
    # Frappe's ``--parse`` path uses ``ast.literal_eval``.  Python literals
    # require ``True`` here; JSON's lowercase ``true`` is rejected by the
    # pinned Frappe v16 command implementation.
    _bench_command(["--site", site, "set-config", "allow_tests", "True", "--parse"])
    _validate_site_routes(site, require_tests=True)


def bootstrap_test(site: str) -> None:
    failures = _check_runtime()
    if failures:
        raise HarnessError("Runtime prerequisites failed:\n- " + "\n- ".join(failures))
    _assert_state_is_ignored_and_contained()
    if not APP_ROOT.is_dir() or not (APP_ROOT / "pyproject.toml").is_file():
        raise HarnessError("The nested audit_practice app source is missing.")
    app_source = APP_ROOT.resolve()
    if _is_link_like(APP_ROOT) or not app_source.is_relative_to(REPO_ROOT.resolve()):
        raise HarnessError("The nested app source resolves outside this repository.")
    repositories, _ = _pins()
    frappe_pin = repositories["frappe"]
    erpnext_pin = repositories["erpnext"]
    frappe_source = _prepare_pinned_source(FRAPPE_LOCAL_SOURCE, frappe_pin, "Frappe")
    erpnext_source = _prepare_pinned_source(ERP_LOCAL_SOURCE, erpnext_pin, "ERPNext")
    bench = _bench_executable()
    runtime_env = _write_runtime_env()
    _run([*_compose_prefix(), "up", "-d", "mariadb", "redis"], cwd=REPO_ROOT)
    _wait_for_services()

    if BENCH_ROOT.exists():
        _assert_bench_layout()
    if not BENCH_ROOT.exists():
        _run(
            _bench_init_command(bench, frappe_source, frappe_pin["ref"]),
            cwd=REPO_ROOT,
            timeout=3600,
        )
    elif not (BENCH_ROOT / "apps" / "frappe").is_dir():
        raise HarnessError("Existing disposable Bench is incomplete; refusing to replace it.")
    _assert_bench_layout()
    frappe_app = _bench_app("frappe")
    bench_python = _bench_python()
    runtime = _read_versions()["runtime"]
    _run(
        [
            str(bench_python),
            "-m",
            "pip",
            "install",
            "--upgrade",
            f"pip=={runtime['pip']['version']}",
        ],
        cwd=BENCH_ROOT,
        timeout=600,
    )
    _verify_bench_python()
    _verify_git_commit(frappe_app, frappe_pin["commit"], "Frappe")
    _install_frappe_app(frappe_app, bench_python)

    erpnext_app = _bench_app("erpnext")
    if not erpnext_app.exists():
        _run(
            [
                bench,
                "get-app",
                "--branch",
                erpnext_pin["ref"],
                "erpnext",
                str(erpnext_source),
            ],
            cwd=BENCH_ROOT,
        )
    _verify_git_commit(erpnext_app, erpnext_pin["commit"], "ERPNext")

    _configure_bench()
    _ensure_bench_apps_file(("frappe", "erpnext"))
    _ensure_app_link()
    _install_node_dependencies()
    _ensure_site_and_apps(site, runtime_env["MARIADB_ROOT_PASSWORD"])
    print(f"Disposable test site is ready: {site}")


def _require_site(site: str) -> None:
    _assert_state_is_ignored_and_contained()
    _assert_bench_layout()
    _ensure_disposable_services()
    _validate_site_routes(site, require_tests=True)
    _assert_app_link()


def _validate_site_routes(site: str, *, require_tests: bool) -> None:
    site_root = BENCH_ROOT / "sites" / site
    site_path = site_root / "site_config.json"
    if _is_link_like(site_root) or _is_link_like(site_path) or not site_path.is_file():
        raise HarnessError(f"Disposable test site is not bootstrapped: {site}")
    common_path = BENCH_ROOT / "sites" / "common_site_config.json"
    if _is_link_like(common_path) or not common_path.is_file():
        raise HarnessError("Bench common site config is missing or symlinked.")
    common = json.loads(
        common_path.read_text(encoding="utf-8")
    )
    site_config = json.loads(site_path.read_text(encoding="utf-8"))
    common_db_port = common.get("db_port")
    site_db_port = site_config.get("db_port", 3307)
    if (
        common.get("db_host") != "127.0.0.1"
        or type(common_db_port) is not int
        or common_db_port != 3307
        or site_config.get("db_host", "127.0.0.1") != "127.0.0.1"
        or type(site_db_port) is not int
        or site_db_port != 3307
        or common.get("db_socket") not in (None, "")
        or site_config.get("db_socket") not in (None, "")
        or common.get("db_type") not in (None, "mariadb")
        or site_config.get("db_type") not in (None, "mariadb")
    ):
        raise HarnessError("Test site database routing is not restricted to local port 3307.")
    redis_routes = (
        ("redis_cache", "redis://127.0.0.1:16379/0"),
        ("redis_queue", "redis://127.0.0.1:16379/1"),
        ("redis_socketio", "redis://127.0.0.1:16379/2"),
    )
    if any(common.get(key) != expected for key, expected in redis_routes):
        raise HarnessError("Bench Redis routing is not restricted to loopback.")
    if any(
        site_config.get(key, expected) != expected
        for key, expected in redis_routes
    ):
        raise HarnessError("Test site Redis routing is not restricted to loopback.")
    if require_tests and site_config.get("allow_tests") is not True:
        raise HarnessError("Tests are not enabled on the allowlisted disposable site.")


def doctor(site: str) -> None:
    failures = _check_runtime()
    try:
        _require_site(site)
        _verify_local_runtime(site)
        print(f"site: {site} (allow_tests=true)")
        print("app: audit_practice is mounted and importable")
        print("services: MariaDB and Redis healthy")
    except HarnessError as exc:
        failures.append(str(exc))
    if failures:
        raise HarnessError("Doctor found unmet prerequisites:\n- " + "\n- ".join(failures))
    print("DOCTOR: PASS")


def _verify_local_runtime(site: str) -> None:
    _verify_bench_python()
    _verify_git_commit(
        _bench_app("frappe"),
        _pins()[0]["frappe"]["commit"],
        "Frappe",
    )
    _verify_git_commit(
        _bench_app("erpnext"),
        _pins()[0]["erpnext"]["commit"],
        "ERPNext",
    )
    apps = _list_installed_apps(site)
    if not {"frappe", "erpnext", "audit_practice"}.issubset(apps):
        raise HarnessError("The allowlisted test site is missing an installed app.")
    expected_source = APP_ROOT.resolve()
    script = (
        "import audit_practice, pathlib, sys; "
        "expected = pathlib.Path(sys.argv[1]).resolve(); "
        "actual = pathlib.Path(audit_practice.__file__).resolve(); "
        "assert actual.is_relative_to(expected), (actual, expected)"
    )
    _run(
        [str(_bench_python()), "-c", script, str(expected_source)],
        cwd=BENCH_ROOT,
        capture=True,
    )
    _write_runtime_env(create=False)
    if not all(
        _probe(
            [
                *_compose_prefix(),
                "exec",
                "-T",
                service,
                *command,
            ]
        )
        for service, command in (
            ("mariadb", ["healthcheck.sh", "--connect", "--innodb_initialized"]),
            ("redis", ["redis-cli", "ping"]),
        )
    ):
        raise HarnessError("A disposable database or Redis health check failed.")


def _validate_test_module(module: str) -> None:
    prefix = "audit_practice.tests."
    if not module.startswith(prefix):
        raise HarnessError(f"Tests must be in the {prefix} package.")
    parts = module.split(".")
    if any(not part.isidentifier() for part in parts):
        raise HarnessError("Test module contains an invalid Python identifier.")
    app_root = APP_ROOT.resolve()
    test_root = APP_ROOT / "audit_practice" / "tests"
    if (
        _is_link_like(APP_ROOT)
        or _is_link_like(test_root)
        or not app_root.is_relative_to(REPO_ROOT.resolve())
        or not test_root.resolve().is_relative_to(app_root)
    ):
        raise HarnessError("The app test package resolves outside this repository.")
    test_path = APP_ROOT.joinpath(*parts).with_suffix(".py")
    resolved = test_path.resolve(strict=True)
    if not resolved.is_relative_to(test_root.resolve()):
        raise HarnessError("Test module resolves outside the app test package.")
    if not test_path.is_file() or not test_path.name.startswith("test_"):
        raise HarnessError("Test module must identify an existing test_*.py file.")


def migrate_test(site: str) -> None:
    _require_site(site)
    _bench_command(["--site", site, "migrate"])


def run_test(site: str, module: str | None = None) -> None:
    _require_site(site)
    args = ["--site", site, "run-tests", "--app", "audit_practice"]
    if module is not None:
        _validate_test_module(module)
        args.extend(["--module", module])
    _bench_command(args)


def build() -> None:
    failures = _check_runtime(require_docker=False)
    if failures:
        raise HarnessError("Runtime prerequisites failed:\n- " + "\n- ".join(failures))
    _assert_state_is_ignored_and_contained()
    _assert_bench_layout()
    _assert_app_link()
    _bench_command(["build", "--app", "audit_practice"])


def serve_test(site: str) -> None:
    _require_site(site)
    _site_admin_password(create=False)
    _bench_command(["--site", site, "serve", "--host", "127.0.0.1", "--port", "8000"])


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run only allowlisted commands against the disposable test site.",
        allow_abbrev=False,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("doctor", "bootstrap-test", "migrate-test", "test-all", "build", "serve-test"):
        subparsers.add_parser(command, allow_abbrev=False)
    test_parser = subparsers.add_parser("test", allow_abbrev=False)
    test_parser.add_argument("module")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        site = _site_from_environment()
        if args.command == "doctor":
            doctor(site)
        elif args.command == "bootstrap-test":
            bootstrap_test(site)
        elif args.command == "migrate-test":
            migrate_test(site)
        elif args.command == "test":
            run_test(site, args.module)
        elif args.command == "test-all":
            run_test(site)
        elif args.command == "build":
            build()
        elif args.command == "serve-test":
            serve_test(site)
        else:
            raise HarnessError("Unsupported command.")
    except (
        HarnessError,
        OSError,
        ValueError,
        json.JSONDecodeError,
        subprocess.TimeoutExpired,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
