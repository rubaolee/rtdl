from pathlib import Path
import runpy
from types import SimpleNamespace
import unittest

import numpy as np

from rtdsl.v4_triangle_reduction_device_runtime import (
    VerifiedTriangleDeviceColumnCountExecutor,
)


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp"
API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
RUNTIME = ROOT / "src/rtdsl/v4_triangle_reduction_device_runtime.py"
CHECKED_REDUCTION = ROOT / "src/rtdsl/v4_checked_u64_device_reduction.py"
APP = ROOT / "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py"


class Goal5776V4TriangleDeviceColumnsTest(unittest.TestCase):
    def test_v4_triangle_gas_requires_single_any_hit_delivery(self):
        source = NATIVE.read_text(encoding="utf-8")
        self.assertGreaterEqual(
            source.count("OPTIX_GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL"),
            2,
        )
        self.assertNotIn(
            "uint32_t flags = OPTIX_GEOMETRY_FLAG_NONE;\n"
            "    triangles.flags = &flags;",
            source,
        )

    def test_particle_frontdoor_uses_column_output_without_array_truthiness(self):
        text = (ROOT / "Paper-reproduction-apps" /
                "goal5753-held-out-particle-tracking" /
                "v4_whole_app.py").read_text(encoding="utf-8")
        self.assertIn("partner_column_output=hasattr(query_values, \"dtype\")", text)
        self.assertIn("matched = bool(np.array_equal(", text)

    def test_particle_column_output_returns_scalar_exact_match(self):
        module = runpy.run_path(str(
            ROOT / "Paper-reproduction-apps" /
            "goal5753-held-out-particle-tracking" / "v4_whole_app.py"))
        expected = np.asarray(((1, 2, 3), (4, 5, 6)), dtype=np.uint32)

        class FakeOwner:
            lifecycle_receipt = {"kind": "test"}

            def execute(self, queries, **kwargs):
                self.partner_column_output = kwargs["partner_column_output"]
                return SimpleNamespace(
                    output=expected.copy(), traversal_receipt={"kind": "test"},
                    native_library_sha256="a" * 64)

        owner = FakeOwner()
        prepared = module["PreparedParticleTrackingV4"](
            owner=owner,
            prepared_input={
                "queries": np.ones((2, 7), dtype=np.float32),
                "expected": expected,
            },
            total_prepare_seconds=0.0,
        )
        result = prepared.execute()
        self.assertIs(result["matched"], True)
        self.assertTrue(owner.partner_column_output)

    def test_native_route_is_generic_built_in_triangle_optix(self):
        native = NATIVE.read_text(encoding="utf-8")
        begin = native.index(
            "static uint64_t prepare_v4_triangle_reduction_device_columns_count_callback")
        end = native.index(
            "static std::shared_ptr<V4PreparedTriangleReduction>", begin)
        prepare = native[begin:end]
        execute_begin = native.index(
            "static void execute_v4_prepared_triangle_reduction_device_columns_count_callback")
        execute_end = native.index(
            "static void destroy_v4_prepared_triangle_reduction_callback", execute_begin)
        execute = native[execute_begin:execute_end]
        self.assertIn("build_v4_triangle_anyhit_accel_from_device_columns", prepare)
        self.assertIn("OPTIX_PRIMITIVE_TYPE_FLAGS_TRIANGLE", prepare)
        self.assertIn("optixLaunch", execute)
        self.assertIn("rtdl_optix_bind_traversal_audit_context", execute)
        self.assertNotIn("triangle_counting", prepare + execute)
        self.assertNotIn("RT-1A2", prepare + execute)
        self.assertNotIn("RT-2A1", prepare + execute)

    def test_c_abi_uses_device_pointers_and_keeps_host_route(self):
        api = API.read_text(encoding="utf-8")
        self.assertIn(
            "rtdl_optix_v4_prepare_triangle_reduction_device_columns_count_v1",
            api,
        )
        self.assertIn(
            "rtdl_optix_v4_execute_prepared_triangle_reduction_device_columns_count_v1",
            api,
        )
        self.assertIn("rtdl_optix_v4_prepare_triangle_reduction_callback_v1", api)
        self.assertIn("rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v1", api)

    def test_runtime_preserves_device_rows_and_checked_u64_bounds(self):
        source = RUNTIME.read_text(encoding="utf-8")
        reduction_source = CHECKED_REDUCTION.read_text(encoding="utf-8")
        self.assertIn("per_ray_host_materialized\": False", source)
        self.assertIn("checked_u64_weighted_sum_device", source)
        self.assertIn("maximum_value > value_upper_bound", reduction_source)
        self.assertIn("value_upper_bound > U64_MAX // weight_sum", reduction_source)
        self.assertIn("copied_summary.tolist()", reduction_source)
        self.assertIn("checked_summary.summary_copy_sync", reduction_source)
        self.assertIn("OptixTraversalAuditSession.open", source)
        self.assertIn("physical_executor_classification", source)
        self.assertNotIn("paper_algorithm", source)

    def test_executor_close_is_idempotent_and_use_after_close_fails_closed(self):
        executor = VerifiedTriangleDeviceColumnCountExecutor.__new__(
            VerifiedTriangleDeviceColumnCountExecutor)
        executor._closed = False
        executor.close()
        executor.close()
        with self.assertRaisesRegex(RuntimeError, "executor is closed"):
            executor.execute_segment(None, None)

    def test_application_owns_algorithm_and_uses_bounded_segments(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn("paper_algorithm=self.paper_algorithm", source)
        self.assertIn("iter_segmented_rt_graph_device_geometry", source)
        self.assertIn("default_selected_between_paper_algorithms\": False", source)
        self.assertIn("global_two_hop_materialized\": False", source)
        self.assertIn("run_v4_segmented_complete", source)


if __name__ == "__main__":
    unittest.main()
