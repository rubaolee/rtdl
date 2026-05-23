from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCAL_ARTIFACT = ROOT / "docs" / "reports" / "goal2485_robot_collision_perf_matrix_local_2026-05-21.json"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal2485_robot_collision_perf_matrix_pod" / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal2485_robot_collision_performance_matrix_2026-05-21.md"
SCRIPT = ROOT / "scripts" / "goal2485_robot_collision_matrix_pod_runner.py"


def _row_by_mode(rows: list[dict[str, object]], mode: str) -> dict[str, object]:
    return next(row for row in rows if row.get("mode") == mode)


class Goal2485RobotCollisionPerformanceMatrixTest(unittest.TestCase):
    def test_matrix_helper_collects_cpu_and_embree_rows_locally(self) -> None:
        from examples.v2_0.research_benchmarks.robot_collision.rtdl_robot_collision_benchmark_app import (
            run_performance_matrix,
        )

        payload = run_performance_matrix(
            dataset="scaled",
            pose_count=12,
            obstacle_count=5,
            link_count=3,
            repeats=3,
            warmup=1,
            include_optix=False,
        )
        rows = payload["rows"]
        cpu = _row_by_mode(rows, "cpu_reference")
        embree = _row_by_mode(rows, "embree_prepared")
        optix = _row_by_mode(rows, "optix_prepared")

        self.assertEqual(payload["goal"], "Goal2485")
        self.assertEqual(cpu["status"], "ok")
        self.assertEqual(embree["status"], "ok")
        self.assertEqual(optix["status"], "skipped")
        self.assertTrue(embree["all_measured_runs_match_probe_reference"])
        self.assertTrue(embree["reuse_metadata"]["prepared_scene_reused"])
        self.assertLess(0.0, embree["tail_median_total_run_seconds"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])

    def test_local_artifact_records_internal_embree_matrix(self) -> None:
        payload = json.loads(LOCAL_ARTIFACT.read_text(encoding="utf-8"))
        rows = payload["rows"]
        cpu = _row_by_mode(rows, "cpu_reference")
        embree = _row_by_mode(rows, "embree_prepared")

        self.assertEqual(payload["case_shape"]["pose_count"], 64)
        self.assertEqual(payload["warmup_protocol"]["warmup_count"], 2)
        self.assertEqual(cpu["status"], "ok")
        self.assertEqual(embree["status"], "ok")
        self.assertEqual(embree["reuse_metadata"]["measured_run_count"], 5)
        self.assertTrue(embree["all_measured_runs_match_probe_reference"])

    def test_pod_runner_and_pod_artifact_record_optix_matrix(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        summary = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        matrix = summary["matrix"]
        optix = _row_by_mode(matrix["rows"], "optix_prepared")

        self.assertIn("make", script)
        self.assertIn("build-optix", script)
        self.assertIn("nvidia-smi", script)
        self.assertIn("run_performance_matrix", script)
        self.assertIn("NVIDIA", summary["gpu"])
        self.assertEqual(optix["status"], "ok")
        self.assertTrue(optix["all_measured_runs_match_probe_reference"])
        self.assertTrue(optix["reuse_metadata"]["prepared_scene_reused"])
        self.assertFalse(summary["claim_boundary"]["public_speedup_claim_authorized"])

    def test_report_records_bounded_internal_claims(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2485 is complete", report)
        self.assertIn("internal evidence only", report)
        self.assertIn("CPU reference", report)
        self.assertIn("Embree prepared", report)
        self.assertIn("OptiX prepared", report)
        self.assertIn("public speedup claim is not authorized", report)
        self.assertIn("authors-code comparison is not authorized", report)


if __name__ == "__main__":
    unittest.main()
