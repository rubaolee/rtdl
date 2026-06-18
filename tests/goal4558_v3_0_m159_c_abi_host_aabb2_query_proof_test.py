from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4558_v3_0_m159_c_abi_host_aabb2_query_proof_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4558_v3_0_m159_c_abi_host_aabb2_query_proof_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4558V30M159CAbiHostAabb2QueryProofTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4558_m159_v3_c_abi_host_aabb2_query_proof")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_host_aabb2_query_proof_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_host_aabb2_query_proof.goal4558.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_c_client_validated_query_capability(self) -> None:
        self.assertTrue(self.checked_in["checks"]["c_client_validated_host_aabb2_query"])
        self.assertFalse(self.checked_in["claim_boundary"]["optix_backend_query_implemented"])
        self.assertFalse(self.checked_in["claim_boundary"]["embree_backend_query_implemented"])

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4558 / V3 M159", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4558 C ABI host AABB2 query proof", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
