from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4582_v3_0_m183_c_abi_python_ctypes_aabb2_query_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4582_v3_0_m183_c_abi_python_ctypes_aabb2_query_2026-06-17.md"
EXAMPLE = ROOT / "examples/current/embedding/python_ctypes_aabb2_query_client.py"
STAGING_DOC = ROOT / "docs/learn/v3_0_c_abi_staging_contract.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4582V30M183CAbiPythonCtypesAabb2QueryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4582_m183_v3_c_abi_python_ctypes_aabb2_query")
        cls.packet = cls.module.build_packet(ROOT, run_smoke=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_python_ctypes_query_example_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_python_ctypes_aabb2_query.goal4582.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_stage_smoke_runs_python_ctypes_query(self) -> None:
        smoke = self.checked_in["python_ctypes_query_smoke"]
        self.assertTrue(smoke["ok"])
        self.assertTrue(smoke["stage_result"]["ok"])
        self.assertTrue(smoke["run_result"]["ok"])
        self.assertEqual("python_ctypes_hit_count=1 first_pair=(0,0)", smoke["run_result"]["stdout"])

    def test_example_report_index_and_boundaries_are_wired(self) -> None:
        source = EXAMPLE.read_text(encoding="utf-8")
        self.assertIn("class RtdlBufferView", source)
        self.assertIn("rtdl_query_execute", source)
        self.assertIn("python_ctypes_aabb2_query_client.py", STAGING_DOC.read_text(encoding="utf-8"))
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4582 / V3 M183", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4582 C ABI Python ctypes AABB2 query", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
