from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
C_ABI_DOC = ROOT / "docs/learn/v3_0_c_abi_draft.md"
EXAMPLE_README = ROOT / "examples/current/embedding/README.md"
PACKET = ROOT / "docs/reports/goal4561_v3_0_m162_c_abi_aabb2_contract_doc_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4561_v3_0_m162_c_abi_aabb2_contract_doc_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4561V30M162CAbiAabb2ContractDocTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4561_m162_v3_c_abi_aabb2_contract_doc")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_contract_doc_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_aabb2_contract_doc.goal4561.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_layout_and_boundary_are_visible(self) -> None:
        combined = C_ABI_DOC.read_text(encoding="utf-8") + "\n" + EXAMPLE_README.read_text(encoding="utf-8")
        self.assertIn("RTDL_DTYPE_F32", combined)
        self.assertIn("RTDL_DTYPE_U64", combined)
        self.assertIn("(query_id, primitive_id)", combined)
        self.assertIn("Unsupported primitive kinds", combined)

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4561 / V3 M162", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4561 C ABI AABB2 contract doc", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
