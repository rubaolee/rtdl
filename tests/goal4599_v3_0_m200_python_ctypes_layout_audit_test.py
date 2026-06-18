from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4599_v3_0_m200_python_ctypes_layout_audit_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4599_v3_0_m200_python_ctypes_layout_audit_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
POLICY = ROOT / "docs/learn/v3_0_c_abi_stability_policy.md"


class Goal4599V30M200PythonCtypesLayoutAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4599_m200_v3_python_ctypes_layout_audit")
        cls.packet = cls.module.build_packet(ROOT, run_probe=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_layout_audit_static_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.python_ctypes_layout_audit.goal4599.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_c_probe_matches_python_ctypes_layout(self) -> None:
        probe = self.checked_in["c_layout_probe"]
        self.assertTrue(probe["ok"])
        self.assertTrue(probe["compile_result"]["ok"])
        self.assertTrue(probe["run_result"]["ok"])
        c_layout = probe["c_layout"]
        py_layout = self.checked_in["python_ctypes_layout"]
        for c_name in (
            "rtdl_external_runtime",
            "rtdl_buffer_view",
            "rtdl_context_desc",
            "rtdl_index_desc",
            "rtdl_query_desc",
        ):
            self.assertEqual(c_layout[c_name], py_layout[c_name], c_name)
        self.assertEqual(py_layout["rtdl_buffer_view"], py_layout["python_cuda_example_rtdl_buffer_view"])

    def test_policy_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("C/Python `ctypes` layout audit", POLICY.read_text(encoding="utf-8"))
        self.assertIn("Goal4599 / V3 M200", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4599 Python ctypes layout audit", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
