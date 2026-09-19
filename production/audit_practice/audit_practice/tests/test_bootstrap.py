"""Integration checks for an installed audit_practice app in a disposable site."""

import importlib
from pathlib import Path

import frappe
from frappe.tests.utils import FrappeTestCase


class TestAuditPracticeBootstrap(FrappeTestCase):
    def test_app_is_installed_and_importable(self) -> None:
        installed_apps = frappe.get_installed_apps()
        self.assertEqual(installed_apps.count("audit_practice"), 1)

        module = importlib.import_module("audit_practice")
        self.assertTrue(Path(module.__file__).resolve().is_file())

    def test_audit_operations_module_is_registered(self) -> None:
        app_root = Path(importlib.import_module("audit_practice").__file__).resolve().parent
        registered_modules = (app_root / "modules.txt").read_text("utf-8").splitlines()
        self.assertIn("Audit Operations", registered_modules)

        module = importlib.import_module("audit_practice.audit_operations")
        self.assertEqual(module.__name__, "audit_practice.audit_operations")

        module_definitions = frappe.get_all(
            "Module Def",
            filters={"app_name": "audit_practice"},
            pluck="name",
        )
        self.assertEqual(module_definitions.count("Audit Operations"), 1)
