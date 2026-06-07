import json
import pathlib
import unittest

import rtdsl as rt
from rtdsl import hiprt_runtime
from rtdsl.engine_feature_matrix import NATIVE
from rtdsl.point_nearest_witness_typed_stream import make_v2_8_point_group_nearest_witness_typed_producer_metadata
from rtdsl.point_nearest_witness_typed_stream import make_v2_8_point_group_nearest_witness_typed_stream_contract
from rtdsl.v2_10_amd_hiprt_benchmark_parity import summarize_v2_10_amd_hiprt_benchmark_parity
from rtdsl.v2_10_amd_hiprt_benchmark_parity import v2_10_amd_hiprt_benchmark_parity


ROOT = pathlib.Path(__file__).resolve().parents[1]
HIPRT_API = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_api.cpp"
HIPRT_CORE = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_core.cpp"
HIPRT_KERNELS = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_kernels.cpp"
HIPRT_RUNTIME = ROOT / "src" / "rtdsl" / "hiprt_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal3774_hiprt_point_group_nearest_device_columns_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3774_hiprt_point_group_nearest_device_columns_a5000.json"


def _native_point_group_columns_available() -> bool:
    try:
        rt.hiprt_context_probe()
        lib = hiprt_runtime._hiprt_lib()
    except Exception:
        return False
    return (
        getattr(lib, "rtdl_hiprt_prepare_point_group_nearest_witness_2d", None) is not None
        and getattr(lib, "rtdl_hiprt_write_prepared_point_group_nearest_witness_2d_device_columns", None) is not None
        and getattr(lib, "rtdl_hiprt_destroy_prepared_point_group_nearest_witness_2d", None) is not None
    )


def _cupy_available() -> bool:
    try:
        import cupy as cp

        cp.cuda.runtime.getDevice()
    except Exception:
        return False
    return True


def _p(point_id: int, x: float, y: float) -> rt.Point:
    return rt.Point(id=point_id, x=x, y=y)


class Goal3774HiprtPointGroupNearestDeviceColumnsPortableTest(unittest.TestCase):
    def test_native_symbols_and_kernel_are_generic(self) -> None:
        api = HIPRT_API.read_text(encoding="utf-8")
        core = HIPRT_CORE.read_text(encoding="utf-8")
        kernels = HIPRT_KERNELS.read_text(encoding="utf-8")
        self.assertIn("rtdl_hiprt_write_prepared_point_group_nearest_witness_2d_device_columns", api)
        self.assertIn("write_prepared_point_group_nearest_witness_device_columns_2d_hiprt", core)
        self.assertIn("RtdlPointGroupNearestWitness2DSplitColumnsKernel", kernels)
        self.assertIn("oroCtxGetCurrent", (ROOT / "src/native/hiprt/rtdl_hiprt_prelude.h").read_text(encoding="utf-8"))
        for source in (api, core, kernels):
            self.assertNotIn("hausdorff", source.lower())
            self.assertNotIn("xhd", source.lower())

    def test_python_runtime_exposes_device_column_method_and_binding(self) -> None:
        runtime = HIPRT_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("def write_device_nearest_witness_columns", runtime)
        self.assertIn("_require_hiprt_partner_device_vector_output_layout", runtime)
        self.assertIn("rtdl_hiprt_write_prepared_point_group_nearest_witness_2d_device_columns", runtime)

    def test_typed_producer_metadata_accepts_hiprt_device_columns(self) -> None:
        stream = make_v2_8_point_group_nearest_witness_typed_stream_contract(
            2,
            stream_id="hiprt_point_group_nearest_witness_2d_device_columns",
            device_type="cuda",
            device_id=0,
            data_ptrs={"query_id": 11, "neighbor_id": 22, "distance": 33},
        )
        metadata = make_v2_8_point_group_nearest_witness_typed_producer_metadata(
            stream,
            backend="hiprt",
            native_symbol="rtdl_hiprt_write_prepared_point_group_nearest_witness_2d_device_columns",
            native_execution_path="prepared_hiprt_point_group_nearest_witness_2d_device_columns",
            query_count=2,
            search_count=3,
            group_count=2,
            radius=5.0,
            transfer_mode="host_query_points_to_device_witness_columns",
        )
        self.assertTrue(metadata["device_resident_output_columns_proven"])
        self.assertTrue(metadata["device_resident_output_stream_proven"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])
        self.assertFalse(metadata["release_authorized"])

    def test_feature_matrix_and_parity_move_hausdorff_to_amd_functional_ready(self) -> None:
        self.assertEqual(
            rt.engine_feature_support("point_group_nearest_witness_output_columns_2d", "hiprt").status,
            NATIVE,
        )
        rows = {row["app"]: row for row in v2_10_amd_hiprt_benchmark_parity()}
        hausdorff = rows["hausdorff_xhd"]
        self.assertIn("point_group_nearest_witness_output_columns_2d", hausdorff["required_engine_features"])
        self.assertEqual(hausdorff["missing_generic_contracts"], ())
        self.assertEqual(hausdorff["parity_stage"], "ready_for_amd_functional_pod")
        summary = summarize_v2_10_amd_hiprt_benchmark_parity()
        self.assertEqual(summary["stage_counts"]["ready_for_amd_functional_pod"], 8)
        self.assertEqual(summary["stage_counts"]["needs_generic_hiprt_extension"], 0)
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["amd_perf_claim_authorized"])

    def test_report_and_artifact_record_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertIn("Goal3774", report)
        self.assertIn("device-column", report)
        self.assertIn("not AMD hardware evidence", report)
        self.assertTrue(artifact["sample"]["device_columns_match_reference"])
        self.assertEqual(artifact["hausdorff_xhd_missing_generic_contracts"], [])
        self.assertEqual(artifact["hausdorff_xhd_parity_stage"], "ready_for_amd_functional_pod")
        self.assertIn("not AMD hardware evidence", artifact["backend_route"])
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)


@unittest.skipUnless(
    _native_point_group_columns_available() and _cupy_available(),
    "requires HIPRT point-group device-column symbols and CuPy",
)
class Goal3774HiprtPointGroupNearestDeviceColumnsNativeTest(unittest.TestCase):
    def test_device_columns_match_reference_rows(self) -> None:
        import cupy as cp

        search = (
            _p(10, 0.0, 0.0),
            _p(11, 1.0, 0.0),
            _p(12, 10.0, 0.0),
        )
        groups = (
            {
                "id": 1,
                "point_offset": 0,
                "point_count": 2,
                "min_x": 0.0,
                "min_y": 0.0,
                "max_x": 1.0,
                "max_y": 0.0,
            },
            {
                "id": 2,
                "point_offset": 2,
                "point_count": 1,
                "min_x": 10.0,
                "min_y": 0.0,
                "max_x": 10.0,
                "max_y": 0.0,
            },
        )
        queries = (
            _p(100, 0.5, 0.0),
            _p(101, 8.0, 0.0),
        )
        query_ids = cp.empty(2, dtype=cp.uint32)
        neighbor_ids = cp.empty(2, dtype=cp.uint32)
        distances = cp.empty(2, dtype=cp.float64)

        with rt.prepare_hiprt_point_group_nearest_witness_2d(search, groups, max_radius=5.0) as prepared:
            reference = prepared.nearest_witness_rows(queries, radius=5.0)
            result = prepared.write_device_nearest_witness_columns(
                queries,
                radius=5.0,
                query_ids_out=query_ids,
                neighbor_ids_out=neighbor_ids,
                distances_out=distances,
            )
        cp.cuda.Stream.null.synchronize()

        self.assertEqual(query_ids.get().tolist(), [row["query_id"] for row in reference])
        self.assertEqual(neighbor_ids.get().tolist(), [row["neighbor_id"] for row in reference])
        self.assertEqual([round(float(value), 6) for value in distances.get().tolist()], [0.5, 2.0])
        metadata = result["metadata"]
        self.assertEqual(metadata["backend"], "hiprt")
        self.assertFalse(metadata["materializes_neighbor_rows"])
        self.assertTrue(metadata["v2_8_typed_producer_metadata"]["device_resident_output_columns_proven"])
        self.assertFalse(metadata["true_zero_copy_authorized"])
        self.assertFalse(metadata["v2_10_release_authorized"])


if __name__ == "__main__":
    unittest.main()
