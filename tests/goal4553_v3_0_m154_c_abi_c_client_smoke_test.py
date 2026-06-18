from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4553_v3_0_m154_c_abi_c_client_smoke_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4553_v3_0_m154_c_abi_c_client_smoke_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4553V30M154CAbiCClientSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4553_m154_v3_c_abi_c_client_smoke")
        cls.packet = cls.module.build_packet(ROOT, run_compile=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_static_c_client_contract_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_c_client_smoke.goal4553.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_c_client_build_and_run_passed(self) -> None:
        client_result = self.checked_in["client_result"]
        self.assertTrue(client_result["shared_library"]["ok"])
        self.assertTrue(client_result["client_compile"]["ok"])
        self.assertTrue(client_result["client_run"]["ok"])
        self.assertTrue(self.checked_in["checks"]["c_client_run_ok"])
        self.assertTrue(self.checked_in["validated_capabilities"]["non_python_c11_dynamic_client_validated"])

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4553 / V3 M154", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4553 C ABI C client smoke", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
