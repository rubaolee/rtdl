from __future__ import annotations

import json
from pathlib import Path
import unittest

from rtdsl.v2_9_benchmark_adequacy import (
    summarize_v2_9_benchmark_adequacy,
    validate_v2_9_benchmark_adequacy,
    v2_9_benchmark_adequacy,
)


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "docs" / "reports" / "goal3757_robot_collision_scale_probe_a5000" / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3757_robot_collision_scaled_prepared_perf_packet_2026-06-07.md"


def _mode_by_name(row: dict[str, object]) -> dict[str, dict[str, object]]:
    return {
        str(mode["mode"]): mode
        for mode in row["mode_results"]  # type: ignore[index]
    }


class Goal3757RobotCollisionScaledPreparedPerfPacketTest(unittest.TestCase):
    def test_summary_artifact_records_two_scaled_prepared_contracts(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal3757")
        rows = {int(row["pose_count"]): row for row in payload["rows"]}
        self.assertEqual(set(rows), {1024, 4096})

        row1024 = _mode_by_name(rows[1024])
        row4096 = _mode_by_name(rows[4096])
        self.assertGreater(row1024["optix_prepared_device_buffers"]["speedup_vs_embree_prepared_buffers"], 4.0)
        self.assertGreater(row4096["optix_prepared_device_buffers"]["speedup_vs_embree_prepared_buffers"], 3.5)
        self.assertGreater(row1024["optix_prepared_device_count"]["speedup_vs_embree_prepared_buffers"], 30.0)
        self.assertGreater(row4096["optix_prepared_device_count"]["speedup_vs_embree_prepared_buffers"], 60.0)

    def test_all_measured_rows_match_reference_and_keep_claims_blocked(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        for flag, value in payload["claim_boundary"].items():
            self.assertFalse(value, flag)
        for row in payload["rows"]:
            for mode in row["mode_results"]:
                self.assertTrue(mode["all_measured_runs_match_probe_reference"])
                self.assertTrue(mode["all_measured_counts_match_probe_reference"])

    def test_adequacy_matrix_no_longer_marks_robot_collision_near_parity(self) -> None:
        validation = validate_v2_9_benchmark_adequacy()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())
        rows = {row["app"]: row for row in v2_9_benchmark_adequacy()}
        robot = rows["robot_collision"]
        self.assertEqual(robot["adequacy"], "strong")
        self.assertIn("Goal3757", robot["evidence_refs"])
        self.assertIn("4.825x", robot["current_performance_reading"])
        self.assertIn("66.591x", robot["current_performance_reading"])
        summary = summarize_v2_9_benchmark_adequacy()
        self.assertEqual(summary["adequacy_counts"]["near_parity"], 0)

    def test_report_is_reader_facing_and_contract_bounded(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Robot Collision Scaled Prepared Performance Packet", text)
        self.assertIn("prepared repeated-query subpath", text)
        self.assertIn("robot-planning acceleration", text)
        self.assertIn("not claimed", text)
        self.assertIn("66.591x", text)


if __name__ == "__main__":
    unittest.main()
