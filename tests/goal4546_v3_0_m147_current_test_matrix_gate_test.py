from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4546_v3_0_m147_current_test_matrix_gate_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4546_v3_0_m147_current_test_matrix_gate_2026-06-17.md"
PROCESS_DOC = ROOT / "docs/audit/process/development_reliability_process.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
M129_TEST = ROOT / "tests/goal4525_v3_0_m129_barnes_hut_rt_native_python_wrapper_gate_test.py"
M130_TEST = ROOT / "tests/goal4526_v3_0_m130_barnes_hut_rt_native_fail_closed_abi_test.py"


class Goal4546V30M147CurrentTestMatrixGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4546_m147_v3_current_test_matrix_gate")
        cls.packet = cls.module.build_packet(ROOT, run_suite=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_v3_current_group_is_registered(self) -> None:
        self.assertEqual("rtdl.v3_0.current_test_matrix.goal4546.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        self.assertEqual("v3_current", self.packet["group"])
        self.assertEqual(76, len(self.packet["modules"]))
        self.assertEqual(
            "tests.goal4508_v3_0_m112_rtnn_clean_target_closeout_test",
            self.packet["modules"][0],
        )
        self.assertEqual(
            "tests.goal4586_v3_0_m187_c_abi_pkg_config_relocatable_stage_test",
            self.packet["modules"][-1],
        )
        self.assertNotIn(
            "tests.goal4546_v3_0_m147_current_test_matrix_gate_test",
            self.packet["modules"],
        )

    def test_checked_in_run_passed_current_v3_suite(self) -> None:
        suite = self.checked_in["suite_run"]
        self.assertTrue(suite["ok"])
        self.assertEqual(76, suite["module_count"])
        self.assertIn("--group v3_current", PROCESS_DOC.read_text(encoding="utf-8"))
        self.assertGreaterEqual(self.checked_in["suite_summary"]["ran_tests"], 134)
        self.assertIn("OK", suite["output"])

    def test_stale_barnes_hut_assertions_follow_goal4541_closure(self) -> None:
        for path in (M129_TEST, M130_TEST):
            text = path.read_text(encoding="utf-8")
            self.assertIn('"closed_current_target"', text)
            self.assertIn("assertIsNone(queue[\"barnes_hut_priority\"])", text)
            self.assertNotIn('"design_blocker", queue["barnes_hut_work_class"]', text)

    def test_docs_report_and_boundary_are_wired(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4546 / V3 M147", report)
        self.assertIn("Goal4546 current V3 test matrix gate", index)
        self.assertIn("default unittest discovery", PROCESS_DOC.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
