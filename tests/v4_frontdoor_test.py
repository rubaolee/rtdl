from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as v4


README = ROOT / "README.md"
QUICKSTART = ROOT / "future" / "v4" / "examples" / "v4_frontdoor_quickstart.py"


class V4FrontDoorTest(unittest.TestCase):
    def test_claim_boundary_lists_measured_surfaces_without_release_claims(self) -> None:
        boundary = v4.claim_boundary_v4()

        self.assertEqual("v4_python_edsl_operator_pushdown_front_door_complete_rt_core_matrix", boundary["status"])
        self.assertEqual("mixed_torch_numba_cupy_and_rtdl_native", boundary["measured_partner"])
        self.assertEqual(("cupy", "numba", "rtdl_native", "torch"), boundary["measured_partners"])
        self.assertEqual(10, len(boundary["measured_surfaces"]))
        self.assertEqual(10, boundary["measured_surface_count"])
        self.assertIn("v4_fixed_radius_count_threshold_2d_device_arrays", boundary["measured_surfaces"])
        self.assertIn("v4_closest_hit_grouped_argmin_3d_device_arrays", boundary["measured_surfaces"])
        self.assertIn("v4_ray_triangle_any_hit_flags_2d_device_arrays", boundary["measured_surfaces"])
        self.assertIn(
            "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
            boundary["measured_surfaces"],
        )
        self.assertIn(
            "v4_point_group_nearest_witness_2d_device_arrays",
            boundary["measured_surfaces"],
        )
        self.assertIn(
            "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
            boundary["measured_surfaces"],
        )
        self.assertIn(
            "v4_fixed_radius_graph_component_union_3d_device_arrays",
            boundary["measured_surfaces"],
        )
        self.assertIn(
            "v4_aabb_index_query_2d_all_ops_count_prepared_runner",
            boundary["measured_surfaces"],
        )
        self.assertIn(
            "v4_aggregate_frontier_device_columns_2d_prepared_runner",
            boundary["measured_surfaces"],
        )
        self.assertIn(
            "v4_ray_triangle_custom_predicate_early_exit_3d_numba",
            boundary["measured_surfaces"],
        )
        self.assertTrue(boundary["v4_python_edsl_release_candidate_supported"])
        self.assertTrue(boundary["operator_pushdown_workflow_high_performance_supported"])
        self.assertEqual(
            "v4_ray_triangle_custom_predicate_early_exit_3d_numba",
            boundary["custom_predicate_early_exit_surface"],
        )
        self.assertGreaterEqual(boundary["custom_predicate_early_exit_serious_scale_v3_geomean"], 1.50)
        self.assertEqual(0, len(boundary["candidate_surfaces"]))
        self.assertEqual("published", boundary["public_release_status"])
        self.assertEqual("v4.0.0", boundary["public_release_tag"])
        self.assertEqual(
            "1c8f63cbadbb1edfc994c1c2477a94a7f00a8639",
            boundary["public_release_commit"],
        )
        self.assertTrue(boundary["v4_0_0_public_tag_created"])
        self.assertTrue(boundary["bounded_public_release_authorized"])
        self.assertEqual(
            v4.V4_AUTHORIZED_RELEASE_LABEL,
            boundary["authorized_release_label"],
        )
        self.assertTrue(boundary["bounded_operator_surface_available"])
        self.assertFalse(boundary["app_level_high_performance_authorized"])
        self.assertEqual(
            "complete_rt_core_app_matrix__bounded_material_wins__no_broad_all_app_speedup_claim",
            boundary["current_app_level_decision_label"],
        )
        self.assertTrue(boundary["complete_rt_core_app_matrix_available"])
        self.assertEqual(10, boundary["complete_rt_core_app_matrix_app_count"])
        self.assertEqual(30, boundary["complete_rt_core_app_matrix_row_count"])
        self.assertEqual(0, boundary["app_matrix_hot_path_regression_count"])
        self.assertFalse(boundary["all_historical_benchmark_apps_faster_claim_authorized"])
        self.assertFalse(boundary["broad_v4_over_v2_14_speedup_claim_authorized"])
        self.assertFalse(boundary["release_claim_authorized"])
        self.assertFalse(boundary["broad_v4_speedup_claim_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(boundary["true_zero_copy_authorized"])
        self.assertFalse(boundary["tier3_callback_claim_authorized"])
        self.assertFalse(boundary["raw_optix_callback_claim_authorized"])
        self.assertFalse(boundary["cupy_performance_claim_authorized"])
        self.assertFalse(boundary["non_python_host_binding_claim_authorized"])
        self.assertFalse(boundary["app_specific_native_kernel_authorized"])

    def test_frontdoor_catalog_and_planner_are_reachable(self) -> None:
        rows = v4.measured_operator_catalog_v4()
        self.assertEqual(10, len(rows))
        candidates = v4.candidate_operator_catalog_v4()
        self.assertEqual(0, len(candidates))
        candidate_names = {row["operator"] for row in candidates}
        self.assertNotIn("fixed_radius_ranked_summary_3d", candidate_names)
        self.assertNotIn("aggregate_frontier_device_columns_2d", candidate_names)

        plan = v4.plan_operator_request_v4("any-hit", partner="torch")
        self.assertEqual("tier2_measured_ready", plan.status)
        self.assertEqual("v4_ray_triangle_any_hit_flags_2d_device_arrays", plan.api_surface)
        grouped_plan = v4.plan_operator_request_v4("grouped_i64", partner="torch")
        self.assertEqual("tier2_measured_ready", grouped_plan.status)
        self.assertEqual("tier2_fused_operator", grouped_plan.tier)
        self.assertFalse(grouped_plan.release_claim_authorized)
        point_group_plan = v4.plan_operator_request_v4("point_group_nearest", partner="torch")
        self.assertEqual("tier2_measured_ready", point_group_plan.status)
        self.assertEqual("tier2_fused_operator", point_group_plan.tier)
        self.assertEqual(
            "v4_point_group_nearest_witness_2d_device_arrays",
            point_group_plan.api_surface,
        )
        component_union_plan = v4.plan_operator_request_v4("component_union", partner="numba")
        self.assertEqual("tier2_measured_ready", component_union_plan.status)
        self.assertEqual("v4_fixed_radius_graph_component_union_3d_device_arrays", component_union_plan.api_surface)
        aabb_plan = v4.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
        self.assertEqual("tier2_measured_ready", aabb_plan.status)
        self.assertEqual("v4_aabb_index_query_2d_all_ops_count_prepared_runner", aabb_plan.api_surface)
        ranked_plan = v4.plan_operator_request_v4("ranked_summary", partner="rtdl_native")
        self.assertEqual("deferred_serious_scale_not_v4_0_release_surface", ranked_plan.status)
        self.assertEqual("deferred_v4_x_or_research", ranked_plan.tier)
        self.assertIsNone(ranked_plan.api_surface)
        self.assertFalse(ranked_plan.release_claim_authorized)

    def test_readme_points_users_at_unified_frontdoor(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn("import rtdsl.v4 as rtdl_v4", text)
        self.assertIn("V4 is a V2/V3 superset", text)
        self.assertIn("complete 10-app RT-core matrix", text)
        self.assertIn("broad V4-over-V2.14 speedup wording", text)
        self.assertIn("embedding, C ABI, or non-Python host binding claims", text)
        self.assertIn("non-Python host binding claims", text)
        self.assertIn("docs/learn/operator_catalog.md", text)
        self.assertIn("tutorials/current/README.md", text)
        self.assertIn("examples/README.md", text)
        self.assertNotIn("Current candidate packet", text)
        self.assertNotIn("still needs\nPOD validation and completion review", text)

    def test_quickstart_runs_without_cuda(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(QUICKSTART)],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        payload = json.loads(proc.stdout)
        self.assertEqual("ok", payload["status"])
        self.assertEqual(
            "v4_python_edsl_operator_pushdown_front_door_complete_rt_core_matrix",
            payload["front_door_status"],
        )
        self.assertEqual(10, payload["measured_surface_count"])
        self.assertEqual(10, payload["catalog_operator_count"])
        self.assertEqual(["cupy", "numba", "rtdl_native", "torch"], payload["measured_partners"])
        self.assertEqual(0, payload["candidate_surface_count"])
        self.assertEqual("tier2_measured_ready", payload["tier2_plan_status"])
        self.assertEqual("tier2_measured_ready", payload["aabb_plan_status"])
        self.assertEqual("published", payload["public_release_status"])
        self.assertEqual("v4.0.0", payload["public_release_tag"])
        self.assertEqual(
            "1c8f63cbadbb1edfc994c1c2477a94a7f00a8639",
            payload["public_release_commit"],
        )
        self.assertTrue(payload["v4_0_0_public_tag_created"])
        self.assertTrue(payload["bounded_public_release_authorized"])
        self.assertEqual(
            v4.V4_AUTHORIZED_RELEASE_LABEL,
            payload["authorized_release_label"],
        )
        self.assertTrue(payload["bounded_operator_surface_available"])
        self.assertFalse(payload["app_level_high_performance_authorized"])
        self.assertEqual(
            "complete_rt_core_app_matrix__bounded_material_wins__no_broad_all_app_speedup_claim",
            payload["current_app_level_decision_label"],
        )
        self.assertTrue(payload["complete_rt_core_app_matrix_available"])
        self.assertEqual(10, payload["complete_rt_core_app_matrix_app_count"])
        self.assertEqual(30, payload["complete_rt_core_app_matrix_row_count"])
        self.assertEqual(0, payload["app_matrix_hot_path_regression_count"])
        self.assertFalse(payload["all_historical_benchmark_apps_faster_claim_authorized"])
        self.assertFalse(payload["broad_v4_over_v2_14_speedup_claim_authorized"])
        self.assertEqual(
            "v4_aabb_index_query_2d_all_ops_count_prepared_runner",
            payload["aabb_plan_surface"],
        )
        self.assertEqual("rejected_action_shaped_callback_deferred", payload["complex_callback_status"])
        self.assertFalse(payload["release_claim_authorized"])
        self.assertFalse(payload["broad_v4_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertFalse(payload["tier3_callback_claim_authorized"])
        self.assertFalse(payload["raw_optix_callback_claim_authorized"])
        self.assertFalse(payload["cupy_performance_claim_authorized"])
        self.assertFalse(payload["embedding_c_abi_claim_authorized"])
        self.assertFalse(payload["non_python_host_binding_claim_authorized"])
        self.assertFalse(payload["app_specific_native_kernel_authorized"])


if __name__ == "__main__":
    unittest.main()
