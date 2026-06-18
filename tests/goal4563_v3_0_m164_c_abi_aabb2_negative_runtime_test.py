from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4563_v3_0_m164_c_abi_aabb2_negative_runtime_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4563_v3_0_m164_c_abi_aabb2_negative_runtime_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4563V30M164CAbiAabb2NegativeRuntimeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4563_m164_v3_c_abi_aabb2_negative_runtime")
        cls.packet = cls.module.build_packet(ROOT, run_compile=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_static_negative_runtime_contract_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_aabb2_negative_runtime.goal4563.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_c_runtime_validated_all_cases(self) -> None:
        self.assertTrue(self.checked_in["checks"]["shared_library_build_ok"])
        self.assertTrue(self.checked_in["checks"]["c_client_compile_ok"])
        self.assertTrue(self.checked_in["checks"]["c_client_run_ok"])
        self.assertTrue(self.checked_in["checks"]["runtime_validated_all_cases"])
        for name, passed in self.checked_in["validated_cases"].items():
            self.assertTrue(passed, name)
        stdout = self.checked_in["client_result"]["client_run"]["stdout"]
        self.assertIn("validated_cases=7", stdout)

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4563 / V3 M164", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4563 C ABI AABB2 negative runtime", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
