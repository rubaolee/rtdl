from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4571_v3_0_m172_c_abi_aabb2_result_ordering_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4571_v3_0_m172_c_abi_aabb2_result_ordering_2026-06-17.md"
C_ABI_DOC = ROOT / "docs/history/v4_preparatory_embedding/v3_0_c_abi_draft.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4571V30M172CAbiAabb2ResultOrderingContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4571_m172_v3_c_abi_aabb2_result_ordering_contract")
        cls.packet = cls.module.build_packet(ROOT, run_compile=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_static_ordering_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_aabb2_result_ordering.goal4571.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_runtime_validated_ordering_cases(self) -> None:
        self.assertTrue(self.checked_in["checks"]["shared_library_build_ok"])
        self.assertTrue(self.checked_in["checks"]["c_client_compile_ok"])
        self.assertTrue(self.checked_in["checks"]["c_client_run_ok"])
        self.assertTrue(self.checked_in["checks"]["runtime_validated_all_cases"])
        for name, passed in self.checked_in["validated_cases"].items():
            self.assertTrue(passed, name)
        stdout = self.checked_in["client_result"]["client_run"]["stdout"]
        self.assertIn("validated_ordering_cases=2", stdout)

    def test_doc_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4571 / V3 M172", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4571 C ABI AABB2 result ordering", INDEX.read_text(encoding="utf-8"))
        doc = C_ABI_DOC.read_text(encoding="utf-8")
        self.assertIn("ascending `query_id`", doc)
        self.assertIn("ascending `primitive_id`", doc)
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
