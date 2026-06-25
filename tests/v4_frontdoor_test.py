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


README = ROOT / "future" / "v4" / "README.md"
QUICKSTART = ROOT / "future" / "v4" / "examples" / "v4_frontdoor_quickstart.py"


class V4FrontDoorTest(unittest.TestCase):
    def test_claim_boundary_lists_measured_surfaces_without_release_claims(self) -> None:
        boundary = v4.claim_boundary_v4()

        self.assertEqual("v4_scorecard_passed_front_door_pending_final_authorization", boundary["status"])
        self.assertEqual("mixed_torch_numba_and_rtdl_native", boundary["measured_partner"])
        self.assertEqual(("numba", "rtdl_native", "torch"), boundary["measured_partners"])
        self.assertEqual(8, len(boundary["measured_surfaces"]))
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
        self.assertEqual(0, len(boundary["candidate_surfaces"]))
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
        self.assertEqual(8, len(rows))
        candidates = v4.candidate_operator_catalog_v4()
        self.assertEqual(0, len(candidates))

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

    def test_readme_points_users_at_unified_frontdoor(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn("import rtdsl.v4 as rtdl_v4", text)
        self.assertIn("V4.0 does not expose raw OptiX callbacks", text)
        self.assertIn("final release authorization pending", text)
        self.assertIn("CuPy performance claims", text)
        self.assertIn("embedding/C-ABI claims", text)
        self.assertIn("non-Python host binding claims", text)
        self.assertIn("measured Tier-2 surfaces: `8`", text)
        self.assertIn("measured partners: `numba`, `rtdl_native`, `torch`", text)
        self.assertIn("candidate Tier-2 surfaces: `0`", text)
        self.assertIn("Ray/triangle any-hit weighted sum", text)
        self.assertIn("Fixed-radius graph component union", text)
        self.assertIn("AABB all-ops count", text)
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
        self.assertEqual("v4_scorecard_passed_front_door_pending_final_authorization", payload["front_door_status"])
        self.assertEqual(8, payload["measured_surface_count"])
        self.assertEqual(8, payload["catalog_operator_count"])
        self.assertEqual(["numba", "rtdl_native", "torch"], payload["measured_partners"])
        self.assertEqual(0, payload["candidate_surface_count"])
        self.assertEqual("tier2_measured_ready", payload["tier2_plan_status"])
        self.assertEqual("tier2_measured_ready", payload["aabb_plan_status"])
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
