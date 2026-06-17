from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = (
    ROOT / "docs/reports/goal4543_v3_0_m144_major_performance_target_refresh_2026-06-17.json"
)
REPORT = (
    ROOT / "docs/reports/goal4543_v3_0_m144_major_performance_target_refresh_2026-06-17.md"
)
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4543V30M144MajorPerformanceTargetRefreshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module(
            "scripts.goal4543_m144_v3_major_performance_target_refresh"
        )
        cls.packet = cls.module.build_packet()
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_target_refresh_checks_all_pass(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.major_performance_target_refresh.goal4543.v1",
            self.packet["version"],
        )
        self.assertEqual((), self.packet["failed_checks"])
        self.assertEqual("accept", rt.validate_current_major_performance_targets()["status"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_no_immediate_pod_targets_after_app_closure(self) -> None:
        summary = self.packet["target_summary"]
        rows = {row["target_id"]: row for row in self.packet["target_rows"]}
        self.assertEqual(
            "rtdl.v3_0.current_major_performance_targets.goal4543.v1",
            summary["version"],
        )
        self.assertEqual((), tuple(summary["pod_needed_next_targets"]))
        self.assertIn("Goal4542", rows["ten_app_current_route_health"]["evidence_refs"])
        self.assertIn("Goal4542", rows["release_grade_long_run_packet"]["evidence_refs"])
        self.assertIn("Goal4542", rows["major_release_candidate_packet"]["evidence_refs"])
        self.assertFalse(rows["release_grade_long_run_packet"]["pod_needed_next"])
        self.assertFalse(rows["amd_hiprt_functional_parity"]["pod_needed_next"])
        self.assertTrue(rows["amd_hiprt_functional_parity"]["amd_hardware_needed"])

    def test_release_and_public_claims_remain_blocked(self) -> None:
        boundary = self.packet["claim_boundary"]
        for key, value in boundary.items():
            if key in {"runtime_executed", "current_route_changed"}:
                self.assertFalse(value, key)
            else:
                self.assertFalse(value, key)

    def test_report_index_and_checked_in_packet_are_wired(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4543 / V3 M144", report)
        self.assertIn("Immediate pod-needed targets: ``", report)
        self.assertIn("Goal4543 major performance target refresh", index)


if __name__ == "__main__":
    unittest.main()
