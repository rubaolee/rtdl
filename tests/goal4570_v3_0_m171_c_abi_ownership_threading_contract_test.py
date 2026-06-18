from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4570_v3_0_m171_c_abi_ownership_threading_contract_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4570_v3_0_m171_c_abi_ownership_threading_contract_2026-06-17.md"
CONTRACT = ROOT / "docs/learn/v3_0_c_abi_ownership_threading_contract.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4570V30M171CAbiOwnershipThreadingContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4570_m171_v3_c_abi_ownership_threading_contract")
        cls.packet = cls.module.build_packet(ROOT, run_compile=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_static_contract_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_ownership_threading_contract.goal4570.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_runtime_validated_ownership_cases(self) -> None:
        self.assertTrue(self.checked_in["checks"]["shared_library_build_ok"])
        self.assertTrue(self.checked_in["checks"]["c_client_compile_ok"])
        self.assertTrue(self.checked_in["checks"]["c_client_run_ok"])
        self.assertTrue(self.checked_in["checks"]["runtime_validated_all_cases"])
        for name, passed in self.checked_in["validated_cases"].items():
            self.assertTrue(passed, name)
        stdout = self.checked_in["client_result"]["client_run"]["stdout"]
        self.assertIn("validated_ownership_cases=3", stdout)

    def test_doc_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4570 / V3 M171", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4570 C ABI ownership/threading contract", INDEX.read_text(encoding="utf-8"))
        contract = CONTRACT.read_text(encoding="utf-8")
        self.assertIn("release-callback", contract)
        self.assertIn("external synchronization", contract)
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
