from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4564_v3_0_m165_c_abi_source_tree_doctor_surface_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4564_v3_0_m165_c_abi_source_tree_doctor_surface_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
DOCTOR_DOC = ROOT / "docs/learn/source_tree_doctor.md"


class Goal4564V30M165CAbiSourceTreeDoctorSurfaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4564_m165_v3_c_abi_source_tree_doctor_surface")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_c_abi_surface_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_source_tree_doctor_surface.goal4564.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_doctor_payload_contains_required_surface_check(self) -> None:
        checks = {row["name"]: row for row in self.packet["doctor_payload"]["checks"]}
        self.assertEqual("pass", checks["V3 C ABI embedding surface"]["status"])
        self.assertIn("include/rtdl/rtdl.h", checks["V3 C ABI embedding surface"]["detail"])
        self.assertIn("make build-c-api", checks["V3 C ABI embedding surface"]["detail"])
        self.assertEqual([], self.packet["doctor_payload"]["required_failures"])

    def test_report_docs_and_index_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4564 / V3 M165", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4564 C ABI source-tree doctor surface", INDEX.read_text(encoding="utf-8"))
        self.assertIn("V3 C ABI embedding surface", DOCTOR_DOC.read_text(encoding="utf-8"))

    def test_claim_boundary_remains_blocked(self) -> None:
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
