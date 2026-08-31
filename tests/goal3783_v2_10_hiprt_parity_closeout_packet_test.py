from __future__ import annotations

import json
from pathlib import Path
import unittest

from rtdsl.v2_10_amd_hiprt_benchmark_parity import V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION
from rtdsl.v2_10_amd_hiprt_benchmark_parity import summarize_v2_10_amd_hiprt_benchmark_parity
from rtdsl.v2_10_amd_hiprt_benchmark_parity import validate_v2_10_amd_hiprt_benchmark_parity
from rtdsl.v2_10_amd_hiprt_benchmark_parity import v2_10_amd_hiprt_benchmark_parity


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3783_v2_10_hiprt_parity_closeout_packet_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3783_v2_10_hiprt_parity_closeout_a5000.json"

REQUIRED_A5000_ARTIFACTS = (
    "goal3763_hiprt_context_probe_tail_repair_and_cuda_path_smoke_a5000.json",
    "goal3764_robot_collision_hiprt_cuda_path_app_smoke_a5000.json",
    "goal3765_robot_collision_hiprt_prepared_group_flags_a5000.json",
    "goal3766_hiprt_prepared_segment_pair_exact_count_a5000.json",
    "goal3767_hiprt_prepared_shape_pair_active_count_a5000.json",
    "goal3768_hiprt_fixed_radius_threshold_count_a5000.json",
    "goal3769_hiprt_fixed_radius_threshold_flags_a5000.json",
    "goal3770_hiprt_prepared_aabb_index_a5000.json",
    "goal3771_hiprt_fixed_radius_ranked_aggregate_a5000.json",
    "goal3772_hiprt_fixed_radius_ranked_batch_sweep_a5000.json",
    "goal3773_hiprt_point_group_nearest_witness_a5000.json",
    "goal3774_hiprt_point_group_nearest_device_columns_a5000.json",
    "goal3775_hiprt_ray_triangle_closest_hit_3d_a5000.json",
    "goal3776_hiprt_collect_k_bounded_i64_a5000.json",
    "goal3777_hiprt_aggregate_frontier_collect_2d_a5000.json",
    "goal3779_hiprt_grouped_i64_count_sum_a5000.json",
    "goal3780_hiprt_grouped_vector_sum_f64x2_a5000.json",
    "goal3781_hiprt_columnar_i64_predicate_scan_a5000.json",
    "goal3782_hiprt_graph_cycle_count_a5000.json",
)


class Goal3783V210HiprtParityCloseoutPacketTest(unittest.TestCase):
    def test_current_parity_map_is_all_ready_without_authorizing_claims(self) -> None:
        self.assertEqual(
            V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION,
            "rtdl.v2_10.amd_hiprt_benchmark_parity_after_goal3782.v1",
        )
        validation = validate_v2_10_amd_hiprt_benchmark_parity()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())

        summary = summarize_v2_10_amd_hiprt_benchmark_parity()
        self.assertEqual(summary["app_count"], 10)
        self.assertEqual(summary["stage_counts"]["ready_for_amd_functional_pod"], 10)
        self.assertEqual(summary["stage_counts"]["needs_generic_hiprt_extension"], 0)
        self.assertEqual(summary["stage_counts"]["compatibility_only_not_amd_perf_ready"], 0)
        self.assertEqual(summary["needs_generic_hiprt_extension_apps"], ())
        self.assertEqual(summary["compatibility_only_not_amd_perf_ready_apps"], ())
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["amd_perf_claim_authorized"])

        for row in v2_10_amd_hiprt_benchmark_parity():
            self.assertEqual(row["parity_stage"], "ready_for_amd_functional_pod")
            self.assertEqual(row["missing_generic_contracts"], ())
            for flag in (
                "release_authorized",
                "amd_perf_claim_authorized",
                "whole_app_speedup_claim_authorized",
                "broad_rt_core_claim_authorized",
                "paper_reproduction_claim_authorized",
                "app_specific_native_engine_logic_allowed",
            ):
                self.assertFalse(row[flag], (row["app"], flag))

    def test_required_a5000_artifacts_exist_and_do_not_authorize_claims(self) -> None:
        missing = [name for name in REQUIRED_A5000_ARTIFACTS if not (ROOT / "docs" / "reports" / name).exists()]
        self.assertEqual(missing, [])
        for name in REQUIRED_A5000_ARTIFACTS:
            path = ROOT / "docs" / "reports" / name
            data = json.loads(path.read_text(encoding="utf-8"))
            boundary = data.get("claim_boundary", {})
            self.assertIsInstance(boundary, dict, name)
            for key, value in boundary.items():
                self.assertFalse(value, (name, key))
            text = path.read_text(encoding="utf-8").lower()
            self.assertTrue("nvidia" in text or "not amd" in text, name)

    def test_closeout_report_records_boundary_and_all_apps(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3783", report)
        self.assertIn("10 / 10", report)
        self.assertIn("not AMD hardware evidence", report)
        self.assertIn("does not authorize", report)
        for app in (
            "hausdorff_xhd",
            "spatial_rayjoin",
            "rt_dbscan",
            "robot_collision",
            "contact_manifold",
            "raydb_style",
            "barnes_hut",
            "librts_spatial_index",
            "rtnn",
            "triangle_counting",
        ):
            self.assertIn(app, report)

    def test_closeout_artifact_records_pod_sweep_when_present(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal3783 pod closeout artifact not generated yet")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["goal"], "Goal3783")
        self.assertEqual(artifact["stage_counts"]["ready_for_amd_functional_pod"], 10)
        self.assertEqual(artifact["stage_counts"]["needs_generic_hiprt_extension"], 0)
        self.assertEqual(artifact["stage_counts"]["compatibility_only_not_amd_perf_ready"], 0)
        self.assertTrue(artifact["focused_tests_passed"])
        self.assertFalse(artifact["scoped_source_dirty"])
        self.assertIn("not AMD hardware evidence", artifact["backend_route"])
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
