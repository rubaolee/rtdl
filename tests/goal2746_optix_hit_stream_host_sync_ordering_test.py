from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
OPTIX_WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal2746OptixHitStreamHostSyncOrderingTest(unittest.TestCase):
    def test_native_device_column_source_synchronizes_before_returning_owner(self) -> None:
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        function_start = workloads.index(
            "run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns_impl_optix"
        )
        function_end = workloads.index(
            "run_prepared_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns_optix",
            function_start,
        )
        function = workloads[function_start:function_end]

        self.assertIn("cuStreamSynchronize(stream)", function)
        self.assertIn("columns_out->owner_handle = owner.release();", function)
        self.assertLess(
            function.index("cuStreamSynchronize(stream)"),
            function.index("columns_out->owner_handle = owner.release();"),
        )

    def test_python_runtime_records_host_synchronized_ordering_for_optix_device_columns(self) -> None:
        source = OPTIX_RUNTIME.read_text(encoding="utf-8")
        method_start = source.index("def ray_triangle_hit_stream_device_columns(")
        method_end = source.index("def ray_triangle_prepared_primitive_grouped_i64_reduction", method_start)
        method = source[method_start:method_end]

        self.assertIn('producer_consumer_stream_ordering="host_synchronized_before_consumer"', method)
        self.assertIn("native_device_column_output_proven_on_hardware=True", method)
        self.assertIn("true_zero_copy_authorized", source)

    def test_no_public_zero_copy_claim_is_added_by_host_sync_ordering(self) -> None:
        source = OPTIX_RUNTIME.read_text(encoding="utf-8")
        method_start = source.index("def ray_triangle_hit_stream_device_columns(")
        method_end = source.index("def ray_triangle_prepared_primitive_grouped_i64_reduction", method_start)
        method = source[method_start:method_end]

        self.assertNotIn("true_zero_copy_authorized=True", method)
        self.assertNotIn("public_speedup_claim_authorized=True", method)


if __name__ == "__main__":
    unittest.main()
