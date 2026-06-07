from __future__ import annotations

from pathlib import Path
import unittest

from rtdsl.engine_feature_matrix import NATIVE
from rtdsl.engine_feature_matrix import engine_feature_support
from rtdsl.v2_10_amd_hiprt_benchmark_parity import (
    V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION,
    summarize_v2_10_amd_hiprt_benchmark_parity,
    validate_v2_10_amd_hiprt_benchmark_parity,
    v2_10_amd_hiprt_benchmark_parity,
)
from rtdsl.v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3753_amd_hiprt_benchmark_parity_plan_2026-06-07.md"


class Goal3753AmdHiprtBenchmarkParityPlanTest(unittest.TestCase):
    def test_engine_feature_matrix_includes_point_nearest_segment_for_hiprt(self) -> None:
        support = engine_feature_support("point_nearest_segment_2d", "hiprt")
        self.assertEqual(support.status, NATIVE)
        self.assertIn("HIPRT", support.note)

    def test_parity_matrix_covers_all_ten_benchmark_apps(self) -> None:
        rows = v2_10_amd_hiprt_benchmark_parity()
        self.assertEqual({row["app"] for row in rows}, set(V2_8_PROMOTED_BENCHMARK_APPS))
        validation = validate_v2_10_amd_hiprt_benchmark_parity()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())

    def test_summary_is_honest_about_amd_extension_work(self) -> None:
        self.assertEqual(
            V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION,
            "rtdl.v2_10.amd_hiprt_benchmark_parity_after_goal3765.v1",
        )
        summary = summarize_v2_10_amd_hiprt_benchmark_parity()
        self.assertEqual(summary["app_count"], 10)
        self.assertEqual(summary["stage_counts"]["ready_for_amd_functional_pod"], 1)
        self.assertEqual(summary["stage_counts"]["compatibility_only_not_amd_perf_ready"], 2)
        self.assertEqual(summary["stage_counts"]["needs_generic_hiprt_extension"], 7)
        self.assertEqual(summary["ready_for_amd_functional_pod_apps"], ("robot_collision",))
        self.assertIn("spatial_rayjoin", summary["needs_generic_hiprt_extension_apps"])
        self.assertIn("raydb_style", summary["compatibility_only_not_amd_perf_ready_apps"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["amd_perf_claim_authorized"])

    def test_each_row_keeps_claim_boundary_false(self) -> None:
        for row in v2_10_amd_hiprt_benchmark_parity():
            for key in (
                "release_authorized",
                "amd_perf_claim_authorized",
                "whole_app_speedup_claim_authorized",
                "broad_rt_core_claim_authorized",
                "paper_reproduction_claim_authorized",
                "app_specific_native_engine_logic_allowed",
            ):
                self.assertFalse(row[key], (row["app"], key))

    def test_report_records_next_amd_lane(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3753", text)
        self.assertIn("AMD/HIPRT", text)
        self.assertIn("robot_collision", text)
        self.assertIn("raydb_style", text)
        self.assertIn("does not authorize", text)


if __name__ == "__main__":
    unittest.main()
