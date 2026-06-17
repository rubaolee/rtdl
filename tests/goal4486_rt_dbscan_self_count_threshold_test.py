from pathlib import Path
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


class Goal4486RtDbscanSelfCountThresholdTest(unittest.TestCase):
    def test_native_and_python_exports_are_present(self) -> None:
        symbol = "rtdl_optix_write_prepared_fixed_radius_count_threshold_3d_self_device_outputs"
        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        runtime = (ROOT / "src/rtdsl/optix_runtime.py").read_text(encoding="utf-8")
        init = (ROOT / "src/rtdsl/__init__.py").read_text(encoding="utf-8")

        self.assertIn(symbol, prelude)
        self.assertIn(symbol, api)
        self.assertIn("write_prepared_fixed_radius_count_threshold_3d_self_device_outputs_optix", workloads)
        self.assertIn("_OPTIX_PREPARED_FIXED_RADIUS_COUNT_THRESHOLD_3D_SELF_DEVICE_OUTPUT_SYMBOL", runtime)
        self.assertIn("def write_device_count_threshold_self_columns", runtime)
        self.assertIn("prepared_search_points_self_query_device", runtime)
        self.assertIn("host_query_point_upload_avoided", runtime)
        self.assertIn("fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns", init)

    def test_rt_dbscan_predicate_route_uses_self_query_adapter(self) -> None:
        app = (
            ROOT
            / "examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py"
        ).read_text(encoding="utf-8")

        self.assertIn("fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns", app)
        self.assertIn("generic_prepared_fixed_radius_count_threshold_3d_self_device_columns_plus_predicate_direct_status_union", app)
        self.assertIn("prepared_rt_core_count_threshold_3d_self_query_then_partner_predicate_direct_status_union_preview", app)
        self.assertIn("prepared_optix_count_threshold_self_query_device", app)

    def test_partner_adapter_metadata_marks_self_query_without_gpu(self) -> None:
        from rtdsl import partner_adapters as pa

        class FakePrepared:
            search_count = 3

            def write_device_count_threshold_self_columns(self, **kwargs):
                return {
                    "metadata": {
                        "direct_device_handoff_authorized": True,
                        "true_zero_copy_authorized": False,
                        "rt_core_accelerated": True,
                        "host_query_point_repack_avoided": True,
                        "host_query_point_upload_avoided": True,
                    }
                }

        fake_runtime = {"name": "fake", "sync": lambda: None}
        output_columns = {
            "query_ids": [0, 1, 2],
            "neighbor_counts": [0, 0, 0],
            "threshold_flags": [0, 0, 0],
        }
        with patch.object(pa, "_partner_module", return_value=fake_runtime):
            result = pa.fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns(
                FakePrepared(),
                radius=1.0,
                threshold=4,
                partner="fake",
                output_columns=output_columns,
                return_metadata=True,
            )

        metadata = result["metadata"]
        self.assertEqual(
            metadata["adapter"],
            "fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns",
        )
        self.assertEqual(metadata["input_contract"], "prepared_native_self_query_device_search_scene")
        self.assertTrue(metadata["self_query_prepared_search_buffer_reused"])
        self.assertTrue(metadata["host_query_point_repack_avoided"])
        self.assertTrue(metadata["host_query_point_upload_avoided"])


if __name__ == "__main__":
    unittest.main()
