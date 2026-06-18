from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4572_v3_0_m173_c_abi_doctor_docs_surface_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4572_v3_0_m173_c_abi_doctor_docs_surface_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
DOCTOR_DOC = ROOT / "docs/learn/source_tree_doctor.md"


class Goal4572V30M173CAbiDoctorDocsSurfaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4572_m173_v3_c_abi_doctor_docs_surface")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_doctor_docs_surface_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_doctor_docs_surface.goal4572.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_doctor_payload_contains_required_docs_surface_check(self) -> None:
        checks = {row["name"]: row for row in self.packet["doctor_payload"]["checks"]}
        self.assertEqual("pass", checks["V3 C ABI docs surface"]["status"])
        self.assertEqual([], self.packet["doctor_payload"]["required_failures"])
        self.assertTrue(all(self.packet["required_docs"].values()))

    def test_report_docs_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4572 / V3 M173", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4572 C ABI doctor docs surface", INDEX.read_text(encoding="utf-8"))
        self.assertIn("V3 C ABI docs surface", DOCTOR_DOC.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
