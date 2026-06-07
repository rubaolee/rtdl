import json
import math
import pathlib
import unittest

import rtdsl as rt
from rtdsl import hiprt_runtime
from rtdsl.engine_feature_matrix import NATIVE
from rtdsl.v2_10_amd_hiprt_benchmark_parity import summarize_v2_10_amd_hiprt_benchmark_parity
from rtdsl.v2_10_amd_hiprt_benchmark_parity import v2_10_amd_hiprt_benchmark_parity


ROOT = pathlib.Path(__file__).resolve().parents[1]
HIPRT_API = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_api.cpp"
HIPRT_CORE = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_core.cpp"
HIPRT_KERNELS = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_kernels.cpp"
REPORT = ROOT / "docs" / "reports" / "goal3773_hiprt_point_group_nearest_witness_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3773_hiprt_point_group_nearest_witness_a5000.json"


def _native_point_group_available() -> bool:
    try:
        rt.hiprt_context_probe()
        lib = hiprt_runtime._hiprt_lib()
    except Exception:
        return False
    return (
        getattr(lib, "rtdl_hiprt_prepare_point_group_nearest_witness_2d", None) is not None
        and getattr(lib, "rtdl_hiprt_run_prepared_point_group_nearest_witness_2d", None) is not None
        and getattr(lib, "rtdl_hiprt_reduce_prepared_point_group_nearest_max_distance_2d", None) is not None
    )


def _p(point_id: int, x: float, y: float) -> rt.Point:
    return rt.Point(id=point_id, x=x, y=y)


class Goal3773HiprtPointGroupNearestWitnessPortableTest(unittest.TestCase):
    def test_new_symbols_are_generic_point_group_contracts(self) -> None:
        api = HIPRT_API.read_text(encoding="utf-8")
        core = HIPRT_CORE.read_text(encoding="utf-8")
        kernels = HIPRT_KERNELS.read_text(encoding="utf-8")
        for symbol in (
            "rtdl_hiprt_prepare_point_group_nearest_witness_2d",
            "rtdl_hiprt_run_prepared_point_group_nearest_witness_2d",
            "rtdl_hiprt_reduce_prepared_point_group_nearest_max_distance_2d",
        ):
            self.assertIn(symbol, api)
        self.assertIn("prepare_point_group_nearest_witness_2d_hiprt", core)
        self.assertIn("RtdlPointGroupNearestWitness2DKernel", kernels)
        self.assertIn("RtdlPointGroupNearestMaxDistance2DKernel", kernels)
        self.assertNotIn("hausdorff", api.lower())
        self.assertNotIn("hausdorff", core.lower())
        self.assertNotIn("hausdorff", kernels.lower())

    def test_python_handle_exposes_empty_path_and_radius_guard(self) -> None:
        self.assertTrue(hasattr(rt, "prepare_hiprt_point_group_nearest_witness_2d"))
        with rt.prepare_hiprt_point_group_nearest_witness_2d((), (), max_radius=1.0) as prepared:
            rows = prepared.nearest_witness_rows((_p(7, 0.0, 0.0),), radius=1.0)
            row = prepared.nearest_max_distance_row((_p(7, 0.0, 0.0),), radius=1.0)
            with self.assertRaisesRegex(ValueError, "must not exceed"):
                prepared.nearest_witness_rows((_p(7, 0.0, 0.0),), radius=2.0)
        self.assertEqual(rows, ({"query_id": 7, "neighbor_id": 0xFFFFFFFF, "distance": math.inf},))
        self.assertEqual(row["query_id"], 7)
        self.assertEqual(row["neighbor_id"], 0xFFFFFFFF)
        self.assertTrue(math.isinf(row["distance"]))

    def test_engine_feature_matrix_records_goal3773_contracts(self) -> None:
        self.assertEqual(rt.engine_feature_support("point_group_nearest_witness_2d", "hiprt").status, NATIVE)
        self.assertEqual(rt.engine_feature_support("point_group_nearest_max_distance_2d", "hiprt").status, NATIVE)

    def test_parity_matrix_keeps_goal3773_contracts_current_after_device_columns(self) -> None:
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
        summary = summarize_v2_10_amd_hiprt_benchmark_parity()
        self.assertEqual(summary["stage_counts"]["ready_for_amd_functional_pod"], 8)
        self.assertIn("hausdorff_xhd", summary["ready_for_amd_functional_pod_apps"])

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3773", report)
        self.assertIn("point-group nearest witness", report)
        self.assertIn("device-column", report)
        self.assertIn("does not authorize", report)

    def test_artifact_records_clean_pod_evidence_and_boundary(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertFalse(artifact["scoped_source_dirty"])
        self.assertTrue(artifact["sample"]["rows_match_reference"])
        self.assertTrue(artifact["sample"]["max_row_matches_reference"])
        self.assertEqual(artifact["hausdorff_xhd_missing_generic_contracts"], ["nearest_witness_output_columns"])
        self.assertEqual(artifact["hausdorff_xhd_parity_stage"], "needs_generic_hiprt_extension")
        self.assertIn("not AMD hardware evidence", artifact["backend_route"])
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)


@unittest.skipUnless(_native_point_group_available(), "HIPRT point-group nearest witness symbols unavailable")
class Goal3773HiprtPointGroupNearestWitnessNativeTest(unittest.TestCase):
    def test_nearest_rows_tie_break_and_max_distance_reduction(self) -> None:
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
        with rt.prepare_hiprt_point_group_nearest_witness_2d(search, groups, max_radius=5.0) as prepared:
            rows = prepared.nearest_witness_rows(queries, radius=5.0)
            max_row = prepared.nearest_max_distance_row(queries, radius=5.0)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["query_id"], 100)
        self.assertEqual(rows[0]["neighbor_id"], 10)
        self.assertAlmostEqual(rows[0]["distance"], 0.5, places=6)
        self.assertEqual(rows[1]["query_id"], 101)
        self.assertEqual(rows[1]["neighbor_id"], 12)
        self.assertAlmostEqual(rows[1]["distance"], 2.0, places=6)
        self.assertEqual(max_row["query_id"], 101)
        self.assertEqual(max_row["neighbor_id"], 12)
        self.assertAlmostEqual(max_row["distance"], 2.0, places=6)


if __name__ == "__main__":
    unittest.main()
