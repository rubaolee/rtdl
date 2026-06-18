from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4545_v3_0_m146_source_tree_doctor_refresh_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4545_v3_0_m146_source_tree_doctor_refresh_2026-06-17.md"
DOCTOR_DOC = ROOT / "docs/learn/source_tree_doctor.md"


class Goal4545V30M146SourceTreeDoctorRefreshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4545_m146_source_tree_doctor_v3_refresh")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_doctor_refresh_checks_all_pass(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.source_tree_doctor_refresh.goal4545.v1",
            self.packet["version"],
        )
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_doctor_payload_uses_current_version_and_v3_doc(self) -> None:
        payload = self.packet["doctor_payload"]
        checks = {row["name"]: row for row in payload["checks"]}
        self.assertEqual("v2.14", payload["version"])
        self.assertEqual("pass", checks["version marker"]["status"])
        self.assertIn("v2.14 release package", checks)
        self.assertIn("V3 app-author strategy", checks)
        self.assertIn("V3 current test matrix", checks)
        self.assertIn("V3 C ABI embedding surface", checks)
        self.assertEqual([], payload["required_failures"])

    def test_report_and_doc_are_wired(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        doc = DOCTOR_DOC.read_text(encoding="utf-8")
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4545 / V3 M146", report)
        self.assertIn("V3 development", doc)
        self.assertIn("V3 C ABI embedding surface", doc)
        self.assertIn("not a benchmark", doc)

    def test_claim_boundary_remains_blocked(self) -> None:
        for key, value in self.packet["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
