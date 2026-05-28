from pathlib import Path
import inspect
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.raydb_style import (
    rtdl_raydb_style_benchmark_app as raydb_app,
)


ROOT = Path(__file__).resolve().parents[1]


class Goal2676V25TritonPartnerPivotTest(unittest.TestCase):
    def test_planner_marks_triton_count_sum_as_executable_preview(self):
        for operation in ("segmented_count_i64", "segmented_sum_f64"):
            spec = rt.plan_v2_5_partner_continuation(
                operation,
                available_partners=("triton", "numba"),
            )
            self.assertEqual(spec.partner, "triton")
            self.assertEqual(spec.status, "preview_not_promoted")
            self.assertFalse(spec.promoted_performance_path)
            self.assertFalse(spec.replaces_rt_traversal)

    def test_triton_describes_all_generic_operations_without_cupy_or_pytorch_partner(self):
        for operation in rt.V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
            descriptor = rt.describe_triton_partner_continuation(operation)
            self.assertEqual(descriptor["partner"], "triton")
            self.assertFalse(descriptor["raw_kernel_required"])
            self.assertFalse(descriptor["replaces_rt_traversal"])
            self.assertFalse(descriptor["promoted_performance_path"])
            self.assertFalse(descriptor["cupy_required"])
            self.assertFalse(descriptor["pytorch_partner_required"])
            self.assertEqual(descriptor["tensor_carrier"], rt.TRITON_TENSOR_CARRIER)
            self.assertFalse(descriptor["tensor_carrier_is_partner"])

        self.assertTrue(rt.describe_triton_partner_continuation("segmented_count_i64")["triton_kernel_available"])
        self.assertTrue(rt.describe_triton_partner_continuation("segmented_sum_f64")["triton_kernel_available"])
        self.assertTrue(rt.describe_triton_partner_continuation("segmented_min_f64")["triton_kernel_available"])
        self.assertTrue(rt.describe_triton_partner_continuation("segmented_max_f64")["triton_kernel_available"])
        self.assertTrue(rt.describe_triton_partner_continuation("compact_mask_i64")["triton_kernel_available"])
        self.assertTrue(rt.describe_triton_partner_continuation("grouped_argmin_f64")["triton_kernel_available"])
        self.assertTrue(rt.describe_triton_partner_continuation("bounded_collect_finalize_i64")["triton_kernel_available"])

    def test_triton_dispatcher_rejects_unknown_operations(self):
        with self.assertRaisesRegex(ValueError, "unsupported"):
            rt.run_triton_partner_continuation(
                "app_specific_magic",
                {},
            )

    def test_raydb_v2_5_surface_prefers_triton_and_not_cupy_or_pytorch_partner(self):
        plan = raydb_app.describe_raydb_v2_5_partner_continuation("count")

        self.assertEqual(plan["preferred_partner"], "triton")
        self.assertEqual(plan["fallback_partner"], "numba")
        self.assertTrue(plan["triton_executable_preview_available"])
        self.assertFalse(plan["uses_cupy_partner"])
        self.assertFalse(plan["uses_pytorch_partner"])
        self.assertEqual(
            inspect.signature(raydb_app._make_paper_rt_partner_ray_columns).parameters["partner"].default,
            "triton",
        )

    def test_raydb_v2_5_preview_runner_uses_generic_triton_dispatch(self):
        result = raydb_app.run_raydb_v2_5_partner_continuation_preview(
            "count",
            {"group_ids": [0, 2, 2, 0], "group_count": 3},
            allow_reference_fallback=True,
        )

        self.assertEqual(result["partner"], "triton")
        self.assertEqual(result["operations"], ("segmented_count_i64",))
        self.assertEqual(result["outputs"]["counts"], [2, 0, 2])
        self.assertFalse(result["metadata"]["uses_cupy_partner"])
        self.assertFalse(result["metadata"]["uses_pytorch_partner"])
        self.assertFalse(result["metadata"]["replaces_rt_traversal"])

    def test_primitive_hierarchy_records_triton_first_continuation(self):
        node = rt.find_primitive_hierarchy_node("continuation.partner_resident")
        self.assertIsNotNone(node)
        assert node is not None
        self.assertIn("Triton-first", node.title)
        self.assertIn("Triton-first", node.summary)
        self.assertNotIn("NumPy/CuPy/PyTorch-style", node.summary)

    def test_benchmark_app_migration_plan_covers_ten_promoted_apps(self):
        plan = rt.v2_5_triton_benchmark_app_migration_plan()
        validation = rt.validate_v2_5_triton_benchmark_app_migration_plan()

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(plan["primary_partner"], "triton")
        self.assertEqual(plan["benchmark_app_count"], 10)
        app_ids = {app["app_id"] for app in plan["apps"]}
        preview_ops = set(plan["preview_kernel_operations"])
        self.assertEqual(
            app_ids,
            {
                "raydb_style",
                "spatial_rayjoin",
                "librts_spatial_index",
                "hausdorff_xhd",
                "rt_dbscan",
                "rtnn",
                "triangle_counting",
                "barnes_hut",
                "robot_collision",
                "contact_manifold",
            },
        )
        for app in plan["apps"]:
            self.assertTrue(set(app["v2_5_required_operations"]).issubset(preview_ops))
        raydb = next(app for app in plan["apps"] if app["app_id"] == "raydb_style")
        self.assertEqual(raydb["v2_5_status"], "first_executable_preview_for_count_sum_min_max")
        self.assertIn("segmented_count_i64", raydb["v2_5_required_operations"])
        self.assertIn("V2_5_TRITON_BENCHMARK_APP_PLANS", rt.__all__)

    def test_docs_record_goal2676_cross_layer_slice(self):
        report = ROOT / "docs/reports/goal2676_v2_5_triton_partner_pivot_2026-05-27.md"
        self.assertTrue(report.exists())
        text = report.read_text()
        self.assertIn("Triton is the primary v2.5 partner", text)
        self.assertIn("Torch is a tensor carrier", text)
        self.assertIn("CuPy and PyTorch are not benchmark-path partners", text)


if __name__ == "__main__":
    unittest.main()
