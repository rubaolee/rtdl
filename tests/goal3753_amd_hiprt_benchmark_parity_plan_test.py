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
            "rtdl.v2_10.amd_hiprt_benchmark_parity_after_goal3774.v1",
        )
        summary = summarize_v2_10_amd_hiprt_benchmark_parity()
        self.assertEqual(summary["app_count"], 10)
        self.assertEqual(summary["stage_counts"]["ready_for_amd_functional_pod"], 6)
        self.assertEqual(summary["stage_counts"]["compatibility_only_not_amd_perf_ready"], 2)
        self.assertEqual(summary["stage_counts"]["needs_generic_hiprt_extension"], 2)
        self.assertEqual(
            summary["ready_for_amd_functional_pod_apps"],
            ("hausdorff_xhd", "spatial_rayjoin", "rt_dbscan", "robot_collision", "librts_spatial_index", "rtnn"),
        )
        self.assertIn("raydb_style", summary["compatibility_only_not_amd_perf_ready_apps"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["amd_perf_claim_authorized"])

    def test_hausdorff_records_goal3774_device_column_contract_closure(self) -> None:
        rows = {row["app"]: row for row in v2_10_amd_hiprt_benchmark_parity()}
        hausdorff = rows["hausdorff_xhd"]
        self.assertIn("point_group_nearest_witness_2d", hausdorff["required_engine_features"])
        self.assertIn("point_group_nearest_witness_output_columns_2d", hausdorff["required_engine_features"])
        self.assertIn("point_group_nearest_max_distance_2d", hausdorff["required_engine_features"])
        self.assertEqual(hausdorff["hiprt_feature_statuses"]["point_group_nearest_witness_2d"], NATIVE)
        self.assertEqual(hausdorff["hiprt_feature_statuses"]["point_group_nearest_witness_output_columns_2d"], NATIVE)
        self.assertEqual(hausdorff["hiprt_feature_statuses"]["point_group_nearest_max_distance_2d"], NATIVE)
        self.assertNotIn("grouped_max_distance_reduction", hausdorff["missing_generic_contracts"])
        self.assertNotIn("nearest_witness_output_columns", hausdorff["missing_generic_contracts"])
        self.assertEqual(hausdorff["missing_generic_contracts"], ())
        self.assertEqual(hausdorff["parity_stage"], "ready_for_amd_functional_pod")

    def test_spatial_rayjoin_records_goal3766_and_goal3767_contract_closure(self) -> None:
        rows = {row["app"]: row for row in v2_10_amd_hiprt_benchmark_parity()}
        spatial = rows["spatial_rayjoin"]
        self.assertIn("prepared_segment_pair_exact_count_2d", spatial["required_engine_features"])
        self.assertIn("prepared_shape_pair_active_count_2d", spatial["required_engine_features"])
        self.assertNotIn("prepared_segment_pair_exact_count", spatial["missing_generic_contracts"])
        self.assertEqual(spatial["missing_generic_contracts"], ())
        self.assertEqual(spatial["parity_stage"], "ready_for_amd_functional_pod")

    def test_rt_dbscan_records_goal3768_and_goal3769_contract_closure(self) -> None:
        rows = {row["app"]: row for row in v2_10_amd_hiprt_benchmark_parity()}
        dbscan = rows["rt_dbscan"]
        self.assertIn("fixed_radius_threshold_reached_count_3d", dbscan["required_engine_features"])
        self.assertIn("fixed_radius_grouped_stream_flags_3d", dbscan["required_engine_features"])
        self.assertEqual(dbscan["missing_generic_contracts"], ())
        self.assertEqual(dbscan["parity_stage"], "ready_for_amd_functional_pod")

    def test_librts_records_goal3770_aabb_query_contract_closure(self) -> None:
        rows = {row["app"]: row for row in v2_10_amd_hiprt_benchmark_parity()}
        librts = rows["librts_spatial_index"]
        self.assertIn("prepared_aabb_query_2d", librts["required_engine_features"])
        self.assertEqual(librts["hiprt_feature_statuses"]["prepared_aabb_query_2d"], NATIVE)
        self.assertEqual(librts["missing_generic_contracts"], ())
        self.assertEqual(librts["parity_stage"], "ready_for_amd_functional_pod")

    def test_rtnn_records_goal3772_batched_sweep_closure(self) -> None:
        rows = {row["app"]: row for row in v2_10_amd_hiprt_benchmark_parity()}
        rtnn = rows["rtnn"]
        self.assertIn("fixed_radius_ranked_summary_aggregate_3d", rtnn["required_engine_features"])
        self.assertIn("fixed_radius_ranked_summary_batched_sweep_3d", rtnn["required_engine_features"])
        self.assertEqual(rtnn["hiprt_feature_statuses"]["fixed_radius_ranked_summary_aggregate_3d"], NATIVE)
        self.assertEqual(rtnn["hiprt_feature_statuses"]["fixed_radius_ranked_summary_batched_sweep_3d"], NATIVE)
        self.assertNotIn("ranked_summary_aggregate", rtnn["missing_generic_contracts"])
        self.assertNotIn("batched_prepared_query_sweep", rtnn["missing_generic_contracts"])
        self.assertEqual(rtnn["missing_generic_contracts"], ())
        self.assertEqual(rtnn["parity_stage"], "ready_for_amd_functional_pod")

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
