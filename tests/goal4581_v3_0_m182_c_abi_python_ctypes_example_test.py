from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4581_v3_0_m182_c_abi_python_ctypes_example_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4581_v3_0_m182_c_abi_python_ctypes_example_2026-06-17.md"
EXAMPLE = ROOT / "docs/history/v4_preparatory_embedding/examples/embedding/python_ctypes_client.py"
STAGING_DOC = ROOT / "docs/history/v4_preparatory_embedding/v3_0_c_abi_staging_contract.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4581V30M182CAbiPythonCtypesExampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4581_m182_v3_c_abi_python_ctypes_example")
        cls.packet = cls.module.build_packet(ROOT, run_smoke=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_python_ctypes_example_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_python_ctypes_example.goal4581.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_stage_smoke_runs_python_ctypes_example(self) -> None:
        smoke = self.checked_in["python_ctypes_smoke"]
        self.assertTrue(smoke["ok"])
        self.assertTrue(smoke["stage_result"]["ok"])
        self.assertTrue(smoke["run_result"]["ok"])
        self.assertEqual("python_ctypes_ok 0.1.3 ok", smoke["run_result"]["stdout"])

    def test_example_report_index_and_boundaries_are_wired(self) -> None:
        source = EXAMPLE.read_text(encoding="utf-8")
        self.assertIn("ctypes.CDLL", source)
        self.assertIn("RtdlContextDesc", source)
        self.assertIn("python_ctypes_client.py", STAGING_DOC.read_text(encoding="utf-8"))
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4581 / V3 M182", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4581 C ABI Python ctypes example", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
