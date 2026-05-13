from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1898_v2_package_install_gate_audit_2026-05-13.md"


class Goal1898V2PackageInstallGateAuditTest(unittest.TestCase):
    def test_repo_still_has_no_packaging_metadata(self) -> None:
        self.assertFalse((ROOT / "pyproject.toml").exists())
        self.assertFalse((ROOT / "setup.py").exists())
        self.assertFalse((ROOT / "setup.cfg").exists())
        self.assertTrue((ROOT / "requirements.txt").exists())

    def test_report_blocks_package_install_claims_until_dedicated_decision(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: blocked-source-tree-only-until-consensus", text)
        self.assertIn("no `pyproject.toml`", text)
        self.assertIn("no `setup.py`", text)
        self.assertIn("PYTHONPATH=src:.", text)
        self.assertIn("Goal1814 allows two ways", text)
        self.assertIn("Do not add packaging metadata as an incidental change", text)
        self.assertIn("package-install claims blocked", text)


if __name__ == "__main__":
    unittest.main()
