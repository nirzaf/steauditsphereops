"""Structural diagnostics for the source skeleton, without Frappe."""

import ast
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest import mock
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = PACKAGE_ROOT.parent
REPO_ROOT = APP_ROOT.parents[1]
BOOTSTRAP_SCRIPT = REPO_ROOT / "scripts" / "production" / "bootstrap.py"


class SkeletonTests(unittest.TestCase):
    @staticmethod
    def _local_tempdir(
        prefix: str, repo_root: Path = REPO_ROOT
    ) -> tempfile.TemporaryDirectory[str]:
        local_root = repo_root / ".local"
        junction_check = getattr(local_root, "is_junction", None)
        if local_root.is_symlink() or (junction_check is not None and junction_check()):
            raise RuntimeError(f"Refusing linked test state directory: {local_root}")
        resolved_repo = repo_root.resolve()
        if not local_root.resolve().is_relative_to(resolved_repo):
            raise RuntimeError(f"Test state directory resolves outside repository: {local_root}")
        local_root.mkdir(parents=True, exist_ok=True)
        if not local_root.resolve().is_relative_to(resolved_repo):
            raise RuntimeError(f"Test state directory resolves outside repository: {local_root}")
        return tempfile.TemporaryDirectory(prefix=prefix, dir=local_root)

    def test_local_tempdir_rejects_links_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory(prefix="test-state-link-") as temp_root:
            temp_path = Path(temp_root)
            repo_root = temp_path / "repo"
            repo_root.mkdir()
            local_root = repo_root / ".local"
            with mock.patch.object(
                Path,
                "is_symlink",
                autospec=True,
                side_effect=lambda path: path == local_root,
            ):
                with self.assertRaisesRegex(
                    RuntimeError, "Refusing linked test state directory"
                ):
                    self._local_tempdir("must-not-be-created-", repo_root=repo_root)
            self.assertFalse(local_root.exists())

    def test_imports_resolve_to_checkout(self) -> None:
        names = (
            "audit_practice",
            "audit_practice.hooks",
            "audit_practice.audit_operations",
            "audit_practice.tests",
        )
        script = (
            "import importlib, json, sys\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "modules = [importlib.import_module(n) for n in sys.argv[2:]]\n"
            "print(json.dumps({'version': modules[0].__version__, "
            "'files': [m.__file__ for m in modules]}))\n"
        )
        result = subprocess.run(
            [sys.executable, "-I", "-B", "-c", script, str(APP_ROOT), *names],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
        observed = json.loads(result.stdout)
        expected = (
            PACKAGE_ROOT / "__init__.py",
            PACKAGE_ROOT / "hooks.py",
            PACKAGE_ROOT / "audit_operations" / "__init__.py",
            PACKAGE_ROOT / "tests" / "__init__.py",
        )
        self.assertEqual(
            [Path(path).resolve() for path in observed["files"]],
            [path.resolve() for path in expected],
        )
        with (APP_ROOT / "pyproject.toml").open("rb") as stream:
            project = tomllib.load(stream)["project"]
        self.assertEqual(project["dynamic"], ["version"])
        self.assertEqual(observed["version"], "0.1.0.dev0")

    def test_project_metadata_matches_contract(self) -> None:
        with (APP_ROOT / "pyproject.toml").open("rb") as stream:
            metadata = tomllib.load(stream)
        pins = json.loads(
            (REPO_ROOT / "infra/production/versions.json").read_text("utf-8")
        )
        project = metadata["project"]
        self.assertEqual(project["name"], "audit-practice")
        self.assertEqual(
            project["authors"],
            [{"name": "STE AuditSphere Ops", "email": "info@quadrate.lk"}],
        )
        self.assertEqual(project["dynamic"], ["version"])
        self.assertEqual(
            project["requires-python"], pins["runtime"]["python"]["support"]
        )
        self.assertEqual(project["dependencies"], [])
        self.assertEqual(
            metadata["build-system"],
            {
                "requires": ["flit_core==3.12.0"],
                "build-backend": "flit_core.buildapi",
            },
        )
        self.assertEqual(
            metadata["tool"]["bench"]["frappe-dependencies"],
            {"frappe": "==16.34.0", "erpnext": "==16.35.0"},
        )

    def test_poc_python_constraint_matches_pinned_runtime(self) -> None:
        pins = json.loads(
            (REPO_ROOT / "infra/production/versions.json").read_text("utf-8")
        )
        poc_manifest = REPO_ROOT / "spikes/p0/audit_poc/pyproject.toml"
        with poc_manifest.open("rb") as stream:
            project = tomllib.load(stream)["project"]
        self.assertEqual(
            project["requires-python"], pins["runtime"]["python"]["support"]
        )

    def test_ci_runtime_matches_toolchain_pins(self) -> None:
        pins = json.loads(
            (REPO_ROOT / "infra/production/versions.json").read_text("utf-8")
        )["runtime"]
        workflow = (REPO_ROOT / ".github/workflows/production-ci.yml").read_text(
            "utf-8"
        )
        self.assertIn(f'python-version: "{pins["python"]["version"]}"', workflow)
        self.assertIn(f'node-version: "{pins["node"]["version"]}"', workflow)
        self.assertIn(f'pip=={pins["pip"]["version"]}', workflow)
        self.assertIn(f'yarn@{pins["yarn"]["version"]}', workflow)

    def test_module_and_migration_registrations(self) -> None:
        modules = (PACKAGE_ROOT / "modules.txt").read_text("utf-8")
        self.assertEqual(modules.splitlines(), ["Audit Operations"])
        patches = (PACKAGE_ROOT / "patches.txt").read_text("utf-8")
        self.assertEqual(patches.strip(), "")

    def test_bench_apps_file_registers_the_production_app_once(self) -> None:
        spec = importlib.util.spec_from_file_location("production_bootstrap", BOOTSTRAP_SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        with self._local_tempdir("bench-apps-test-") as temporary:
            apps_txt = Path(temporary) / "apps.txt"
            apps_txt.write_text("frappe\nerpnext\n", encoding="utf-8")
            with self.assertRaisesRegex(harness.HarnessError, "exactly once"):
                harness._validate_apps_registration(apps_txt)

            apps_txt.write_text("frappe\nerpnext\naudit_practice\n", encoding="utf-8")
            harness._validate_apps_registration(apps_txt)

            apps_txt.write_text(
                "frappe\nerpnext\naudit_practice\naudit_practice\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(harness.HarnessError, "exactly once"):
                harness._validate_apps_registration(apps_txt)

    def test_importable_modules_contain_only_literal_metadata(self) -> None:
        paths = [PACKAGE_ROOT / "hooks.py", *PACKAGE_ROOT.rglob("__init__.py")]
        for path in paths:
            with self.subTest(path=path):
                tree = ast.parse(path.read_text("utf-8"), filename=str(path))
                for node in tree.body:
                    if isinstance(node, ast.Expr):
                        self.assertIsInstance(ast.literal_eval(node.value), str)
                    else:
                        self.assertIsInstance(node, ast.Assign)
                        self.assertTrue(
                            all(isinstance(target, ast.Name) for target in node.targets)
                        )
                        ast.literal_eval(node.value)

    def test_hooks_are_metadata_only(self) -> None:
        tree = ast.parse((PACKAGE_ROOT / "hooks.py").read_text("utf-8"))
        assignments = {
            node.targets[0].id: ast.literal_eval(node.value)
            for node in tree.body
            if isinstance(node, ast.Assign)
        }
        self.assertEqual(
            assignments,
            {
                "app_name": "audit_practice",
                "app_title": "STE AuditSphere Ops",
                "app_publisher": "STE AuditSphere Ops",
                "app_description": (
                    "Source skeleton only; no production workflows implemented."
                ),
                "app_email": "info@quadrate.lk",
                "app_license": "mit",
                "required_apps": ["erpnext"],
            },
        )
        license_text = (APP_ROOT / "license.txt").read_text("utf-8")
        self.assertIn("MIT License", license_text)
        self.assertIn("Copyright (c) 2026 STE AuditSphere Ops", license_text)
        self.assertIn("Permission is hereby granted, free of charge", license_text)

    def test_shell_wrapper_checkout_is_executable_and_lf(self) -> None:
        wrapper = REPO_ROOT / "scripts" / "production" / "dev"
        source = wrapper.read_bytes()
        self.assertTrue(source.startswith(b"#!/usr/bin/env sh\n"))
        self.assertNotIn(b"\r", source)
        entry = self._git(REPO_ROOT, "ls-files", "--stage", "--", "scripts/production/dev")
        self.assertEqual(entry.stdout.split()[0], "100755")

        if os.name == "posix":
            self.assertTrue(os.access(wrapper, os.X_OK))
            environment = os.environ.copy()
            environment["PYTHON"] = sys.executable
            result = subprocess.run(
                [str(wrapper), "not-a-command"],
                cwd=REPO_ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("invalid choice", result.stderr)

    def test_wrapper_rejects_unsupported_subcommand(self) -> None:
        result = subprocess.run(
            [sys.executable, str(BOOTSTRAP_SCRIPT), "not-a-command"],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr)

    def test_wrapper_rejects_non_disposable_site(self) -> None:
        environment = os.environ.copy()
        environment["AUDIT_SITE"] = "production.example.com"
        result = subprocess.run(
            [sys.executable, str(BOOTSTRAP_SCRIPT), "doctor"],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
            timeout=15,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing any other site", result.stderr)

    def test_test_module_allowlist_rejects_traversal(self) -> None:
        spec = importlib.util.spec_from_file_location("production_bootstrap", BOOTSTRAP_SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        harness._validate_test_module("audit_practice.tests.test_bootstrap")
        with self.assertRaises(harness.HarnessError):
            harness._validate_test_module("audit_practice.tests..production")

    def test_bench_init_uses_the_containerized_redis_service(self) -> None:
        spec = importlib.util.spec_from_file_location("production_bootstrap", BOOTSTRAP_SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        command = harness._bench_init_command(
            "bench", Path(".local/sources/frappe"), "v16.34.0"
        )

        self.assertIn("--skip-redis-config-generation", command)
        self.assertEqual(command[command.index("--frappe-branch") + 1], "v16.34.0")

    def test_bootstrap_materializes_pinned_node_dependencies(self) -> None:
        spec = importlib.util.spec_from_file_location("production_bootstrap", BOOTSTRAP_SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        plan = harness._node_requirements_commands(Path(".local/bench"))
        self.assertEqual(
            plan,
            (
                (
                    Path(".local/bench/apps/frappe"),
                    ("yarn", "install", "--check-files", "--frozen-lockfile"),
                ),
                (
                    Path(".local/bench/apps/erpnext"),
                    (
                        "yarn",
                        "install",
                        "--check-files",
                        "--frozen-lockfile",
                        "--ignore-scripts",
                    ),
                ),
                (
                    Path(".local/bench/apps/erpnext/banking"),
                    (
                        "yarn",
                        "install",
                        "--check-files",
                        "--frozen-lockfile",
                        "--ignore-scripts",
                    ),
                ),
            ),
        )

    def test_frappe_retry_uses_pinned_bench_python(self) -> None:
        spec = importlib.util.spec_from_file_location("production_bootstrap", BOOTSTRAP_SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        with mock.patch.object(harness, "_run") as run:
            harness._install_frappe_app(Path(".local/bench/apps/frappe"), Path(".local/bench/env/bin/python"))
        command = run.call_args.args[0]
        self.assertEqual(
            command,
            [
                str(Path(".local/bench/env/bin/python")),
                "-m",
                "pip",
                "install",
                "--quiet",
                "--editable",
                str(Path(".local/bench/apps/frappe")),
            ],
        )
        self.assertNotIn("uv", command)

    def test_node_dependency_marker_is_pinned_and_complete(self) -> None:
        spec = importlib.util.spec_from_file_location("production_bootstrap", BOOTSTRAP_SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        with self._local_tempdir("node-marker-test-") as temporary:
            bench_root = Path(temporary) / "bench"
            for path in (
                bench_root / "apps" / "frappe" / "node_modules" / "fast-glob",
                bench_root / "apps" / "erpnext" / "node_modules",
                bench_root / "apps" / "erpnext" / "banking" / "node_modules",
            ):
                path.mkdir(parents=True)
            marker = bench_root / ".audit-node-dependencies.ready"
            with (
                mock.patch.object(harness, "BENCH_ROOT", bench_root),
                mock.patch.object(harness, "NODE_DEPENDENCIES_MARKER", marker),
                mock.patch.object(
                    harness,
                    "_node_dependencies_marker_payload",
                    return_value={"frappe": "f", "erpnext": "e"},
                ),
            ):
                self.assertFalse(harness._node_dependencies_are_ready())
                marker.write_text('{"erpnext":"e","frappe":"f"}\n', encoding="utf-8")
                self.assertTrue(harness._node_dependencies_are_ready())
                marker.write_text('{"erpnext":"wrong","frappe":"f"}\n', encoding="utf-8")
                self.assertFalse(harness._node_dependencies_are_ready())

    def test_site_commands_reassert_disposable_services(self) -> None:
        spec = importlib.util.spec_from_file_location("production_bootstrap", BOOTSTRAP_SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        with (
            mock.patch.object(harness, "_assert_state_is_ignored_and_contained"),
            mock.patch.object(harness, "_assert_bench_layout"),
            mock.patch.object(harness, "_ensure_disposable_services") as ensure_services,
            mock.patch.object(harness, "_validate_site_routes"),
            mock.patch.object(harness, "_assert_app_link"),
        ):
            harness._require_site("auditflow-test.localhost")
        ensure_services.assert_called_once_with()

    def test_serve_test_binds_the_disposable_port_without_host_flag(self) -> None:
        spec = importlib.util.spec_from_file_location("production_bootstrap", BOOTSTRAP_SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        with (
            mock.patch.object(harness, "_require_site"),
            mock.patch.object(harness, "_site_admin_password", return_value="x" * 40),
            mock.patch.object(harness, "_bench_command") as bench_command,
        ):
            harness.serve_test("auditflow-test.localhost")
        argv = bench_command.call_args.args[0]
        self.assertEqual(
            argv,
            ["--site", "auditflow-test.localhost", "serve", "--port", "8000"],
        )
        self.assertNotIn("--host", argv)

    def test_bench_apps_file_is_materialized_for_local_sources(self) -> None:
        spec = importlib.util.spec_from_file_location("production_bootstrap", BOOTSTRAP_SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        with self._local_tempdir("apps-file-test-") as temporary:
            bench_root = Path(temporary)
            (bench_root / "apps").mkdir()
            (bench_root / "sites").mkdir()
            (bench_root / "env").mkdir()
            with mock.patch.object(harness, "BENCH_ROOT", bench_root):
                harness._ensure_bench_apps_file(("frappe", "erpnext"))
            self.assertEqual(
                (bench_root / "sites" / "apps.txt").read_text("utf-8"),
                "frappe\nerpnext\n",
            )

    def test_site_allowlist_accepts_only_the_test_site(self) -> None:
        spec = importlib.util.spec_from_file_location("production_bootstrap", BOOTSTRAP_SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        with mock.patch.dict(os.environ, {"AUDIT_SITE": "auditflow-test.localhost"}):
            self.assertEqual(harness._site_from_environment(), "auditflow-test.localhost")

    def test_site_routes_reject_unsafe_database_and_redis_targets(self) -> None:
        spec = importlib.util.spec_from_file_location("production_bootstrap", BOOTSTRAP_SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        site = "auditflow-test.localhost"
        redis_routes = {
            "redis_cache": "redis://127.0.0.1:16379/0",
            "redis_queue": "redis://127.0.0.1:16379/1",
            "redis_socketio": "redis://127.0.0.1:16379/2",
        }
        common_config = {"db_host": "127.0.0.1", "db_port": 3307, **redis_routes}
        site_config = {
            "db_host": "127.0.0.1",
            "db_port": 3307,
            "db_type": "mariadb",
            "allow_tests": True,
            **redis_routes,
        }

        with self._local_tempdir("site-routes-test-") as temporary:
            bench_root = Path(temporary)
            sites_root = bench_root / "sites"
            site_root = sites_root / site
            site_root.mkdir(parents=True)
            common_path = sites_root / "common_site_config.json"
            site_path = site_root / "site_config.json"
            with mock.patch.object(harness, "BENCH_ROOT", bench_root):
                common_path.write_text(json.dumps(common_config), encoding="utf-8")
                site_path.write_text(json.dumps(site_config), encoding="utf-8")
                harness._validate_site_routes(site, require_tests=True)

                cases = (
                    ("remote common DB host", "common", "db_host", "db.example.com", "database routing"),
                    ("wrong common DB port", "common", "db_port", 3308, "database routing"),
                    ("fractional DB port", "common", "db_port", 3307.5, "database routing"),
                    ("text DB port", "site", "db_port", "3307", "database routing"),
                    ("DB socket", "site", "db_socket", "/var/run/mysql.sock", "database routing"),
                    ("non-MariaDB backend", "site", "db_type", "postgres", "database routing"),
                    ("remote common Redis", "common", "redis_queue", "redis://cache:6379/1", "Bench Redis routing"),
                    ("remote site Redis", "site", "redis_cache", "redis://10.0.0.5:6379/0", "Test site Redis routing"),
                    ("tests disabled", "site", "allow_tests", False, "Tests are not enabled"),
                )
                for label, target, key, value, error in cases:
                    with self.subTest(route=label):
                        current_common = common_config.copy()
                        current_site = site_config.copy()
                        selected = current_common if target == "common" else current_site
                        selected[key] = value
                        common_path.write_text(json.dumps(current_common), encoding="utf-8")
                        site_path.write_text(json.dumps(current_site), encoding="utf-8")
                        with self.assertRaisesRegex(harness.HarnessError, error):
                            harness._validate_site_routes(site, require_tests=True)

    def test_bench_root_follows_task03_ignored_local_contract(self) -> None:
        spec = importlib.util.spec_from_file_location("production_bootstrap", BOOTSTRAP_SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        expected = REPO_ROOT / ".local" / "bench"
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(harness._bench_root_from_environment(), expected)
        with mock.patch.dict(os.environ, {"BENCH_ROOT": "$REPO_ROOT/.local/bench"}):
            self.assertEqual(harness._bench_root_from_environment(), expected)
        with mock.patch.dict(os.environ, {"BENCH_ROOT": str(expected)}):
            self.assertEqual(harness._bench_root_from_environment(), expected)
        for unsafe in (REPO_ROOT / "production" / "bench", REPO_ROOT.parent / "bench"):
            with self.subTest(path=unsafe), mock.patch.dict(
                os.environ, {"BENCH_ROOT": str(unsafe)}
            ):
                with self.assertRaises(harness.HarnessError):
                    harness._bench_root_from_environment()

    def test_subprocess_environment_excludes_caller_secrets(self) -> None:
        spec = importlib.util.spec_from_file_location("production_bootstrap", BOOTSTRAP_SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        with mock.patch.dict(
            os.environ,
            {"PATH": "safe-path", "AUDIT_TEST_SECRET": "must-not-propagate"},
            clear=True,
        ):
            environment = harness._subprocess_environment()
        self.assertEqual(environment.get("PATH"), "safe-path")
        self.assertNotIn("AUDIT_TEST_SECRET", environment)
        self.assertEqual(environment["GIT_CONFIG_GLOBAL"], os.devnull)
        self.assertEqual(environment["GIT_CONFIG_NOSYSTEM"], "1")

    def test_subprocess_environment_preserves_docker_plugin_system_paths(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "production_bootstrap_env_paths", BOOTSTRAP_SCRIPT
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        expected = {
            "PROGRAMDATA": r"C:\\ProgramData",
            "PROGRAMFILES": r"C:\\Program Files",
            "PROGRAMFILES(X86)": r"C:\\Program Files (x86)",
            "COMMONPROGRAMFILES": r"C:\\Program Files\\Common Files",
            "COMMONPROGRAMFILES(X86)": r"C:\\Program Files (x86)\\Common Files",
        }
        with mock.patch.dict(
            os.environ,
            expected,
            clear=True,
        ):
            observed = harness._subprocess_environment()

        for key, value in expected.items():
            self.assertEqual(observed[key], value)

    def test_runtime_env_accepts_equivalent_wsl_path_on_windows(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "production_bootstrap_runtime_path", BOOTSTRAP_SCRIPT
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        # Forward slashes preserve the expected spelling on both test hosts.
        windows_path = Path("C:/Users/DELL/repos/steauditsphereops/.local/production/mariadb")
        wsl_path = "/mnt/c/Users/DELL/repos/steauditsphereops/.local/production/mariadb"
        self.assertEqual(
            harness._resolve_runtime_data_path(wsl_path, host_os="nt"),
            windows_path.resolve(),
        )

    def test_runtime_env_accepts_equivalent_windows_paths_on_wsl(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "production_bootstrap_runtime_path", BOOTSTRAP_SCRIPT
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        wsl_path = Path("/mnt/c/Users/DELL/repos/steauditsphereops/.local/production/mariadb")
        for windows_path in (
            r"C:\Users\DELL\repos\steauditsphereops\.local\production\mariadb",
            "C:/Users/DELL/repos/steauditsphereops/.local/production/mariadb",
        ):
            with self.subTest(path=windows_path):
                self.assertEqual(
                    harness._resolve_runtime_data_path(windows_path, host_os="posix"),
                    wsl_path.resolve(),
                )

    def test_compose_project_identity_is_stable_across_windows_and_wsl_paths(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "production_bootstrap_compose_identity", BOOTSTRAP_SCRIPT
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        windows_path = r"C:\Users\DELL\repos\steauditsphereops"
        wsl_path = "/mnt/c/Users/DELL/repos/steauditsphereops"
        self.assertEqual(
            harness._canonical_path_alias(windows_path),
            harness._canonical_path_alias(wsl_path),
        )

    def test_bench_commands_require_the_pinned_cli_version(self) -> None:
        spec = importlib.util.spec_from_file_location("production_bootstrap", BOOTSTRAP_SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        pinned = harness._read_versions()["runtime"]["bench"]["version"]
        with (
            mock.patch.object(harness.shutil, "which", return_value="bench"),
            mock.patch.object(
                harness,
                "_run",
                return_value=subprocess.CompletedProcess(
                    ["bench", "--version"], 0, f"{pinned}\n", ""
                ),
            ),
        ):
            self.assertEqual(harness._bench_executable(), "bench")

        with (
            mock.patch.object(harness.shutil, "which", return_value="bench"),
            mock.patch.object(
                harness,
                "_run",
                return_value=subprocess.CompletedProcess(
                    ["bench", "--version"], 0, "5.23.0\n", ""
                ),
            ),
        ):
            with self.assertRaisesRegex(harness.HarnessError, "Bench CLI mismatch"):
                harness._bench_executable()

    def test_pinned_source_ref_must_match_before_use(self) -> None:
        spec = importlib.util.spec_from_file_location("production_bootstrap", BOOTSTRAP_SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        with self._local_tempdir("pinned-source-test-") as temporary:
            root = Path(temporary)
            origin_work = root / "origin-work"
            origin_work.mkdir()
            origin_git = root / "origin.git"
            self._git(origin_work, "init")
            (origin_work / "source.txt").write_text("pinned content\n", encoding="utf-8")
            self._git(origin_work, "add", "source.txt")
            self._git(
                origin_work,
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.invalid",
                "commit",
                "-m",
                "pinned source",
            )
            commit = self._git(origin_work, "rev-parse", "HEAD").stdout.strip()
            self._git(origin_work, "tag", "v15.99.0")
            self._git(root, "clone", "--bare", str(origin_work), str(origin_git))

            pin = {"url": str(origin_git), "ref": "v15.99.0", "commit": "0" * 40}
            with self.assertRaisesRegex(harness.HarnessError, "does not resolve"):
                harness._prepare_pinned_source(root / "wrong-pin", pin, "test source")

            pin["commit"] = commit
            prepared = harness._prepare_pinned_source(
                root / "correct-pin", pin, "test source"
            )
            self.assertEqual(self._git(prepared, "rev-parse", "HEAD").stdout.strip(), commit)

    def test_local_test_site_admin_password_is_persisted_for_serve(self) -> None:
        spec = importlib.util.spec_from_file_location("production_bootstrap", BOOTSTRAP_SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        harness = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(harness)

        with self._local_tempdir("site-password-test-") as temporary:
            password_file = Path(temporary) / "site-admin-password"
            with mock.patch.object(harness, "SITE_ADMIN_PASSWORD_FILE", password_file):
                generated = harness._site_admin_password(create=True)
                reused = harness._site_admin_password(create=False)
            self.assertRegex(generated, r"^[A-Za-z0-9_-]{40}$")
            self.assertEqual(reused, generated)
            self.assertEqual(password_file.read_text(encoding="utf-8"), generated)

    @staticmethod
    def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(cwd), *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )


if __name__ == "__main__":
    unittest.main()
