from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4_operator_catalog as catalog


class V4OperatorCatalogTest(unittest.TestCase):
    def test_measured_tier2_operator_is_planned_as_fused_surface(self) -> None:
        plan = catalog.plan_v4_operator_request("fixed-radius", partner="torch")

        self.assertEqual("tier2_measured_ready", plan.status)
        self.assertEqual("tier2_fused_operator", plan.tier)
        self.assertEqual("v4_fixed_radius_count_threshold_2d_device_arrays", plan.api_surface)
        self.assertEqual("FIXED_RADIUS_COUNT_THRESHOLD_2D", plan.generic_primitive)
        self.assertTrue(plan.measured_partner)
        self.assertFalse(plan.release_claim_authorized)
        self.assertFalse(plan.tier3_callback_claim_authorized)
        self.assertFalse(plan.app_specific_native_kernel_authorized)

    def test_cupy_tier2_partner_is_declared_but_unmeasured(self) -> None:
        plan = catalog.plan_v4_operator_request("grouped_argmin", partner="cupy")

        self.assertEqual("tier2_declared_unmeasured_partner", plan.status)
        self.assertIsNone(plan.api_surface)
        self.assertFalse(plan.measured_partner)
        self.assertIn("measured for torch only", plan.guidance)
        self.assertIn("No V4.0 API surface", plan.guidance)
        self.assertFalse(plan.cupy_performance_claim_authorized)
        self.assertFalse(plan.non_python_host_binding_claim_authorized)
        self.assertFalse(plan.broad_v4_speedup_claim_authorized)

    def test_numba_scalar_callback_is_spike_only_not_supported_surface(self) -> None:
        plan = catalog.plan_v4_operator_request(
            "custom_force_score",
            callback_shape="custom_scalar_reduce",
            numba_device_function=True,
            partner="torch",
        )

        self.assertEqual("tier3_spike_only_not_v4_0_release_surface", plan.status)
        self.assertEqual("tier3_numba_ptx_spike", plan.tier)
        self.assertTrue(plan.tier3_spike_authorized)
        self.assertEqual(
            catalog.V4_TIER3_CALLBACK_SPIKE_PROTOCOL_STATUS,
            plan.tier3_protocol_status,
        )
        self.assertEqual(catalog.V4_TIER3_CALLBACK_SPIKE_PROTOCOL_DOC, plan.tier3_protocol_doc)
        self.assertIn("callback spike protocol", plan.guidance)
        self.assertIn("fixed overhead ceiling", plan.guidance)
        self.assertFalse(plan.tier3_callback_claim_authorized)
        self.assertFalse(plan.raw_optix_callback_claim_authorized)
        self.assertFalse(plan.release_claim_authorized)
        self.assertIsNone(plan.api_surface)

    def test_action_shaped_callback_is_rejected_not_wrapped_as_optix(self) -> None:
        plan = catalog.plan_v4_operator_request(
            "custom_collision_response",
            callback_shape="custom_action",
            mutates_shared_state=True,
            variable_length_output=True,
            dynamic_allocation=True,
            partner="torch",
        )

        self.assertEqual("rejected_action_shaped_callback_deferred", plan.status)
        self.assertEqual("unsupported_v4_0_deferred", plan.tier)
        self.assertIn("shared mutation", plan.guidance)
        self.assertIn("dynamic allocation", plan.guidance)
        self.assertIn("variable-length output", plan.guidance)
        self.assertIn("does not expose raw OptiX callbacks", plan.guidance)
        self.assertIn("Tier-3 spike protocol", plan.guidance)
        self.assertEqual(
            catalog.V4_TIER3_ACTION_CALLBACK_REJECTED_STATUS,
            plan.tier3_protocol_status,
        )
        self.assertEqual(catalog.V4_TIER3_CALLBACK_SPIKE_PROTOCOL_DOC, plan.tier3_protocol_doc)
        self.assertFalse(plan.tier3_spike_authorized)
        self.assertFalse(plan.tier3_callback_claim_authorized)
        self.assertFalse(plan.raw_optix_callback_claim_authorized)
        self.assertFalse(plan.app_specific_native_kernel_authorized)

    def test_catalog_rows_keep_release_and_app_kernel_claims_false(self) -> None:
        rows = catalog.measured_v4_tier2_operator_catalog()
        self.assertEqual(10, len(rows))
        surfaces = {row["api_surface"] for row in rows}
        self.assertIn("v4_ray_triangle_any_hit_flags_2d_device_arrays", surfaces)
        self.assertIn("v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays", surfaces)
        self.assertIn("v4_point_group_nearest_witness_2d_device_arrays", surfaces)
        self.assertIn("v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays", surfaces)
        self.assertIn("v4_fixed_radius_graph_component_union_3d_device_arrays", surfaces)
        self.assertIn("v4_aabb_index_query_2d_all_ops_count_prepared_runner", surfaces)
        self.assertIn("v4_aggregate_frontier_device_columns_2d_prepared_runner", surfaces)
        self.assertIn("v4_ray_triangle_custom_predicate_early_exit_3d_numba", surfaces)
        self.assertTrue(
            all(
                row["measured_partners"]
                in {("torch",), ("numba",), ("rtdl_native",), ("rtdl_native", "cupy")}
                for row in rows
            )
        )
        self.assertTrue(all(row["release_claim_authorized"] is False for row in rows))
        self.assertTrue(all(row["app_specific_native_kernel_authorized"] is False for row in rows))

    def test_catalog_rows_have_goal4621_hardened_status_fields(self) -> None:
        rows = [
            *catalog.measured_v4_tier2_operator_catalog(),
            *catalog.candidate_v4_tier2_operator_catalog(),
        ]
        self.assertEqual(10, len(rows))

        required_fields = {
            "catalog_class",
            "surface_status",
            "partner_claim_status",
            "direct_device_input_columns",
            "direct_device_output_columns",
            "direct_device_output_scalar",
            "host_materialization_in_hot_path",
            "true_zero_copy_authorized",
            "release_claim_authorized",
            "broad_v4_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "tier3_callback_claim_authorized",
            "raw_optix_callback_claim_authorized",
            "cupy_performance_claim_authorized",
            "embedding_c_abi_claim_authorized",
            "non_python_host_binding_claim_authorized",
            "app_specific_native_kernel_authorized",
        }
        for row in rows:
            self.assertTrue(required_fields.issubset(row), row["operator"])
            self.assertFalse(row["host_materialization_in_hot_path"], row["operator"])
            self.assertFalse(row["true_zero_copy_authorized"], row["operator"])
            self.assertFalse(row["release_claim_authorized"], row["operator"])
            self.assertFalse(row["broad_v4_speedup_claim_authorized"], row["operator"])
            self.assertFalse(row["whole_app_speedup_claim_authorized"], row["operator"])
            self.assertFalse(row["tier3_callback_claim_authorized"], row["operator"])
            self.assertFalse(row["raw_optix_callback_claim_authorized"], row["operator"])
            self.assertFalse(row["cupy_performance_claim_authorized"], row["operator"])
            self.assertFalse(row["embedding_c_abi_claim_authorized"], row["operator"])
            self.assertFalse(row["non_python_host_binding_claim_authorized"], row["operator"])
            self.assertFalse(row["app_specific_native_kernel_authorized"], row["operator"])

        measured = [row for row in rows if row["catalog_class"] == "measured"]
        candidates = [row for row in rows if row["catalog_class"] == "candidate"]
        self.assertEqual(10, len(measured))
        self.assertEqual(0, len(candidates))
        candidate_names = {row["operator"] for row in candidates}
        self.assertNotIn("fixed_radius_ranked_summary_3d", candidate_names)
        self.assertNotIn("aggregate_frontier_device_columns_2d", candidate_names)
        self.assertTrue(
            all(str(row["surface_status"]).startswith("tier2_measured") for row in measured)
        )

    def test_grouped_i64_reduction_is_measured_tier2_surface(self) -> None:
        plan = catalog.plan_v4_operator_request("primitive_grouped_i64", partner="torch")

        self.assertEqual("tier2_measured_ready", plan.status)
        self.assertEqual("tier2_fused_operator", plan.tier)
        self.assertEqual(
            "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays",
            plan.api_surface,
        )
        self.assertEqual("RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D", plan.generic_primitive)
        self.assertTrue(plan.measured_partner)
        self.assertFalse(plan.release_claim_authorized)
        self.assertFalse(plan.broad_v4_speedup_claim_authorized)

        rows = catalog.measured_v4_tier2_operator_catalog()
        rows_by_operator = {row["operator"]: row for row in rows}
        grouped = rows_by_operator["primitive_grouped_i64_reduction"]
        self.assertFalse(grouped["release_claim_authorized"])
        self.assertEqual(("torch",), grouped["measured_partners"])
        self.assertEqual(("cupy",), grouped["declared_unmeasured_partners"])
        self.assertEqual("8.0", grouped["validated_optix_abi"])
        self.assertFalse(grouped["optix_9_1_validated"])

    def test_point_group_nearest_witness_is_measured_tier2_surface(self) -> None:
        plan = catalog.plan_v4_operator_request("point_group_nearest", partner="torch")

        self.assertEqual("tier2_measured_ready", plan.status)
        self.assertEqual("tier2_fused_operator", plan.tier)
        self.assertEqual("v4_point_group_nearest_witness_2d_device_arrays", plan.api_surface)
        self.assertEqual("POINT_GROUP_NEAREST_WITNESS_2D", plan.generic_primitive)
        self.assertEqual("nearest_witness", plan.continuation_class)
        self.assertTrue(plan.measured_partner)
        self.assertFalse(plan.release_claim_authorized)
        self.assertFalse(plan.broad_v4_speedup_claim_authorized)
        candidates = catalog.candidate_v4_tier2_operator_catalog()
        self.assertEqual(0, len(candidates))
        candidate_names = {row["operator"] for row in candidates}
        self.assertNotIn("fixed_radius_ranked_summary_3d", candidate_names)
        self.assertNotIn("aggregate_frontier_device_columns_2d", candidate_names)
        rows = catalog.measured_v4_tier2_operator_catalog()
        rows_by_operator = {row["operator"]: row for row in rows}
        point_group = rows_by_operator["point_group_nearest_witness"]
        self.assertEqual(("torch",), point_group["measured_partners"])
        self.assertEqual(("cupy",), point_group["declared_unmeasured_partners"])
        self.assertEqual("8.0", point_group["validated_optix_abi"])
        self.assertEqual("float32_computed_float64_output", point_group["distance_precision"])
        self.assertFalse(point_group["optix_9_1_validated"])

    def test_ranked_summary_is_deferred_not_candidate_or_measured_surface(self) -> None:
        plan = catalog.plan_v4_operator_request("ranked_summary", partner="rtdl_native")

        self.assertEqual("deferred_serious_scale_not_v4_0_release_surface", plan.status)
        self.assertEqual("deferred_v4_x_or_research", plan.tier)
        self.assertIsNone(plan.api_surface)
        self.assertEqual("FIXED_RADIUS_RANKED_SUMMARY_3D", plan.generic_primitive)
        self.assertEqual("ranked_summary_topk", plan.continuation_class)
        self.assertFalse(plan.measured_partner)
        self.assertFalse(plan.release_claim_authorized)
        self.assertFalse(plan.whole_app_speedup_claim_authorized)

    def test_weighted_sum_is_measured_torch_surface_after_goal4633(self) -> None:
        plan = catalog.plan_v4_operator_request("any_hit_weighted_sum", partner="torch")

        self.assertEqual("tier2_measured_ready", plan.status)
        self.assertEqual("tier2_fused_operator", plan.tier)
        self.assertEqual("v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays", plan.api_surface)
        self.assertEqual("RAY_TRIANGLE_ANY_HIT_WEIGHTED_SUM_3D", plan.generic_primitive)
        self.assertTrue(plan.measured_partner)
        self.assertFalse(plan.release_claim_authorized)
        self.assertFalse(plan.broad_v4_speedup_claim_authorized)
        self.assertFalse(plan.tier3_callback_claim_authorized)

        cupy_plan = catalog.plan_v4_operator_request("ray_triangle_weighted_sum", partner="cupy")
        self.assertEqual("tier2_declared_unmeasured_partner", cupy_plan.status)
        self.assertIsNone(cupy_plan.api_surface)
        self.assertFalse(cupy_plan.measured_partner)
        self.assertIn("measured for torch only", cupy_plan.guidance)

        rows = catalog.measured_v4_tier2_operator_catalog()
        weighted = {row["operator"]: row for row in rows}["ray_triangle_any_hit_weighted_sum"]
        self.assertEqual(("torch",), weighted["measured_partners"])
        self.assertEqual(("cupy",), weighted["declared_unmeasured_partners"])
        self.assertFalse(weighted["direct_device_output_columns"])
        self.assertTrue(weighted["direct_device_output_scalar"])
        self.assertEqual("same_operator_comparable_route", weighted["comparison_class"])
        self.assertEqual("largest_shape_barely_clears_1_20x_floor_not_large_speedup", weighted["performance_caveat"])
        self.assertFalse(weighted["release_claim_authorized"])
        self.assertFalse(weighted["app_specific_native_kernel_authorized"])

    def test_component_union_is_measured_numba_surface_after_goal4635(self) -> None:
        plan = catalog.plan_v4_operator_request("component_union", partner="numba")

        self.assertEqual("tier2_measured_ready", plan.status)
        self.assertEqual("tier2_fused_operator", plan.tier)
        self.assertEqual("v4_fixed_radius_graph_component_union_3d_device_arrays", plan.api_surface)
        self.assertEqual("FIXED_RADIUS_GRAPH_COMPONENT_UNION_3D", plan.generic_primitive)
        self.assertEqual("component_union", plan.continuation_class)
        self.assertTrue(plan.measured_partner)
        self.assertFalse(plan.release_claim_authorized)
        self.assertFalse(plan.whole_app_speedup_claim_authorized)

        torch_plan = catalog.plan_v4_operator_request("fixed_radius_graph_component_union", partner="torch")
        self.assertEqual("tier2_declared_unmeasured_partner", torch_plan.status)
        self.assertIsNone(torch_plan.api_surface)
        self.assertFalse(torch_plan.measured_partner)
        self.assertIn("measured for numba only", torch_plan.guidance)

        rows = catalog.measured_v4_tier2_operator_catalog()
        component_union = {row["operator"]: row for row in rows}["fixed_radius_graph_component_union_3d"]
        self.assertEqual(("numba",), component_union["measured_partners"])
        self.assertEqual(("torch", "cupy"), component_union["declared_unmeasured_partners"])
        self.assertEqual("same_contract_embree_control_and_legacy_optix_control", component_union["comparison_class"])
        self.assertGreaterEqual(component_union["runner_vs_embree_hot_speedup"], 1.20)
        self.assertGreaterEqual(component_union["runner_vs_embree_wall_speedup"], 1.20)
        self.assertGreaterEqual(component_union["runner_vs_legacy_wall_speedup"], 0.98)
        self.assertFalse(component_union["release_claim_authorized"])
        self.assertFalse(component_union["app_specific_native_kernel_authorized"])

    def test_aabb_index_is_measured_native_surface_after_goal4637(self) -> None:
        plan = catalog.plan_v4_operator_request("aabb_index_query", partner="rtdl_native")

        self.assertEqual("tier2_measured_ready", plan.status)
        self.assertEqual("tier2_fused_operator", plan.tier)
        self.assertEqual("v4_aabb_index_query_2d_all_ops_count_prepared_runner", plan.api_surface)
        self.assertEqual("AABB_INDEX_QUERY_2D", plan.generic_primitive)
        self.assertEqual("aabb_index_all_ops_count", plan.continuation_class)
        self.assertTrue(plan.measured_partner)
        self.assertFalse(plan.release_claim_authorized)
        self.assertFalse(plan.whole_app_speedup_claim_authorized)

        torch_plan = catalog.plan_v4_operator_request("aabb_index", partner="torch")
        self.assertEqual("tier2_declared_unmeasured_partner", torch_plan.status)
        self.assertIsNone(torch_plan.api_surface)
        self.assertFalse(torch_plan.measured_partner)
        self.assertIn("measured for rtdl_native only", torch_plan.guidance)

        rows = catalog.measured_v4_tier2_operator_catalog()
        aabb = {row["operator"]: row for row in rows}["aabb_index_query_2d_all_ops_count"]
        self.assertEqual(("rtdl_native",), aabb["measured_partners"])
        self.assertEqual(("torch", "cupy", "numba"), aabb["declared_unmeasured_partners"])
        self.assertEqual("same_contract_family_embree_control", aabb["comparison_class"])
        self.assertGreaterEqual(aabb["runner_vs_embree_hot_speedup"], 10.0)
        self.assertGreaterEqual(aabb["runner_vs_embree_wall_speedup"], 10.0)
        self.assertFalse(aabb["release_claim_authorized"])
        self.assertFalse(aabb["app_specific_native_kernel_authorized"])

    def test_invalid_partner_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "partner must be one of"):
            catalog.plan_v4_operator_request("any_hit", partner="numpy")


if __name__ == "__main__":
    unittest.main()
