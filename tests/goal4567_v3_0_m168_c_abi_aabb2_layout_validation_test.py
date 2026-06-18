from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4567_v3_0_m168_c_abi_aabb2_layout_validation_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4567_v3_0_m168_c_abi_aabb2_layout_validation_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4567V30M168CAbiAabb2LayoutValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4567_m168_v3_c_abi_aabb2_layout_validation")
        cls.packet = cls.module.build_packet(ROOT, run_compile=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_static_layout_contract_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_aabb2_layout_validation.goal4567.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_c_runtime_validated_layout_cases(self) -> None:
        self.assertTrue(self.checked_in["checks"]["shared_library_build_ok"])
        self.assertTrue(self.checked_in["checks"]["c_client_compile_ok"])
        self.assertTrue(self.checked_in["checks"]["c_client_run_ok"])
        self.assertTrue(self.checked_in["checks"]["runtime_validated_layout_cases"])
        for name, passed in self.checked_in["validated_cases"].items():
            self.assertTrue(passed, name)
        stdout = self.checked_in["client_result"]["client_run"]["stdout"]
        self.assertIn("validated_layout_cases=3", stdout)

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4567 / V3 M168", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4567 C ABI AABB2 layout validation", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
