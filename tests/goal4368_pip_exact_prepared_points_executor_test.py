from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4368_pip_exact_prepared_points_executor_2026-06-13.md"
SUMMARY = (
    ROOT
    / "docs"
    / "reports"
    / "goal4368_pip_exact_prepared_points_executor_2026-06-13"
    / "summary.json"
)


class Goal4368PipExactPreparedPointsExecutorTest(unittest.TestCase):
    def test_native_exact_executor_symbols_are_exported(self) -> None:
        prelude = (ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp").read_text(encoding="utf-8")
        workloads = (ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp").read_text(encoding="utf-8")

        for symbol in (
            "rtdl_optix_prepare_point_closed_shape_membership_exact_prepared_points_scalar_count_executor_2d",
            "rtdl_optix_run_point_closed_shape_membership_exact_prepared_points_scalar_count_executor_2d",
            "rtdl_optix_destroy_point_closed_shape_membership_exact_prepared_points_scalar_count_executor_2d",
        ):
            self.assertIn(symbol, prelude)
            self.assertIn(symbol, api)

        self.assertIn("PreparedPointClosedShapeExactPreparedPointsScalarCountExecutor2D", workloads)
        self.assertIn("reset_closed_shape_membership_phase_timings(13u)", workloads)
        self.assertIn("output overflowed fixed candidate capacity", workloads)
        self.assertIn("prepared->right_geos->covers", workloads)

    def test_python_runtime_exposes_exact_executor_without_changing_old_count(self) -> None:
        runtime = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")
        self.assertIn("PreparedOptixExactPreparedPointsScalarCountExecutor2D", runtime)
        self.assertIn("prepare_exact_prepared_points_scalar_count_executor", runtime)
        self.assertIn("count_prepared_points_exact", runtime)
        self.assertIn("prepared_points_exact_count_executor_run", runtime)
        self.assertIn("exact_host_refined_scalar_count", runtime)
        self.assertIn("row_stream_materialized", runtime)

    def test_rayjoin_runner_has_executor_count_mode(self) -> None:
        runner = (
            ROOT / "scripts" / "goal4354_rayjoin_original_vs_rtdl_same_stream_scalar_count.py"
        ).read_text(encoding="utf-8")
        self.assertIn("exact_prepared_points_executor", runner)
        self.assertIn("prepare_exact_scalar_count_executor_sec", runner)
        self.assertIn("exact_scalar_count_executor_reused", runner)
        self.assertIn("prepared_exact_closed_shape_membership_prepared_points_scalar_count_executor", runner)

    def test_pod_evidence_records_exact_count_improvement_and_rayjoin_gap(self) -> None:
        data = json.loads(SUMMARY.read_text(encoding="utf-8"))
        optix = data["rtdl"]["pip"]["backends"]["optix"]
        embree = data["rtdl"]["pip"]["backends"]["embree"]
        self.assertEqual("prepared_exact_closed_shape_membership_prepared_points_scalar_count_executor", optix["execution_route"])
        self.assertEqual(8686, optix["row_count"])
        self.assertEqual(8686, embree["row_count"])

        optix_ms = optix["hot_median_sec"] * 1000.0
        embree_ms = embree["hot_median_sec"] * 1000.0
        self.assertLess(optix_ms, 7.0)
        self.assertGreater(embree_ms / optix_ms, 2.5)

        v2_12 = json.loads(
            (
                ROOT
                / "docs"
                / "reports"
                / "goal4358_rtx_a4000_v2_12_rayjoin_same_stream_2026-06-13"
                / "summary.json"
            ).read_text(encoding="utf-8")
        )
        old_ms = v2_12["rtdl"]["pip"]["backends"]["optix"]["hot_median_sec"] * 1000.0
        self.assertGreater(old_ms / optix_ms, 1.7)

        comparison = next(row for row in data["comparisons"] if row["backend"] == "optix")
        self.assertLess(comparison["rayjoin_rt_over_rtdl"], 1.0)
        self.assertGreater(1.0 / comparison["rayjoin_rt_over_rtdl"], 7.0)

        phases = [
            row["native_phase_timings"]
            for row in optix["timing"]["runs"]
            if not row["is_warmup"]
        ]
        self.assertTrue(all(row["mode"] == "prepared_points_exact_count_executor_run" for row in phases))

        rejected = optix["diagnostics"]["rejected_fast_route"]
        self.assertEqual(8798, rejected["device_filtered_prepared_points_count"])
        self.assertEqual(8603, rejected["relation_status_corrected_row_count"])
        self.assertEqual(8686, rejected["exact_row_count"])

    def test_report_keeps_public_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("internal v2.13 optimization evidence", report)
        self.assertIn("does not make RTDL faster than RayJoin RT", report)
        self.assertIn("New OptiX executor vs v2.12 OptiX exact prepared-points", report)
        self.assertIn("RayJoin RT faster than new RTDL OptiX executor", report)
        self.assertIn("does not authorize public RTDL-beats-RayJoin", report)


if __name__ == "__main__":
    unittest.main()
