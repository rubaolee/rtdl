from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "robot_collision"
    / "rtdl_robot_collision_benchmark_app.py"
)
REPORT = ROOT / "docs" / "reports" / "goal2484_robot_collision_prepared_reuse_2026-05-21.md"
EXPECTED_TINY_FLAGS = [0, 0, 0, 1, 1, 1, 0, 0, 0, 1]


class Goal2484RobotCollisionPreparedReuseTest(unittest.TestCase):
    def test_probe_lowering_matches_tiny_exact_fixture(self) -> None:
        from examples.v2_0.research_benchmarks.robot_collision.rtdl_robot_collision_benchmark_app import (
            _probe_reference_flags,
            build_segment_probe_contract,
            make_tiny_case,
        )

        contract = build_segment_probe_contract(make_tiny_case())

        self.assertEqual(len(contract.groups), 10)
        self.assertEqual(len(contract.segment_start_xyz), 90)
        self.assertEqual(contract.probe_points_per_group, 9)
        self.assertIn("vertical_finite_segments_3d", contract.lowering_policy)
        self.assertEqual(_probe_reference_flags(contract), EXPECTED_TINY_FLAGS)

    def test_embree_prepared_reuse_probe_records_warmup_and_tail_medians(self) -> None:
        from examples.v2_0.research_benchmarks.robot_collision.rtdl_robot_collision_benchmark_app import (
            run_prepared_reuse_probe,
        )

        payload = run_prepared_reuse_probe(backend="embree", dataset="tiny", repeats=4, warmup=1)
        reuse = payload["reuse_metadata"]

        self.assertEqual(payload["contract"], "PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1")
        self.assertEqual(payload["probe_reference_compact_link_flags"], EXPECTED_TINY_FLAGS)
        self.assertEqual(reuse["warmup_rows_dropped"], 1)
        self.assertEqual(reuse["measured_run_count"], 3)
        self.assertEqual(reuse["prepared_run_indices"], [1, 2, 3, 4])
        self.assertTrue(reuse["prepared_run_indices_strictly_increase"])
        self.assertTrue(reuse["prepared_scene_reused"])
        self.assertTrue(reuse["query_input_sequences_reused"])
        self.assertFalse(reuse["native_query_output_buffers_reused"])
        self.assertTrue(reuse["all_measured_runs_match_probe_reference"])
        self.assertIn("query_pack", payload["tail_medians"]["phase_timing_seconds"])
        self.assertIn("traversal", payload["tail_medians"]["phase_timing_seconds"])

    def test_prepared_cli_emits_probe_payload(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(APP),
                "--mode",
                "embree_prepared",
                "--dataset",
                "tiny",
                "--repeats",
                "3",
                "--warmup",
                "1",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": "src:."},
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["goal"], "Goal2484")
        self.assertEqual(payload["mode"], "embree_prepared")
        self.assertEqual(payload["warmup_protocol"]["warmup_count"], 1)
        self.assertEqual(payload["reuse_metadata"]["prepared_run_indices"], [1, 2, 3])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["exact_solid_collision_claim_authorized"])

    def test_report_records_goal2484_scope_and_limits(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2484 is complete", report)
        self.assertIn("7 repeats with 2 warmup rows", report)
        self.assertIn("tail medians", report)
        self.assertIn("prepared_run_indices", report)
        self.assertIn("native query/output buffers are repacked per run", report)
        self.assertIn("not exact solid collision", report)
        self.assertIn("No native files were changed", report)


if __name__ == "__main__":
    unittest.main()
