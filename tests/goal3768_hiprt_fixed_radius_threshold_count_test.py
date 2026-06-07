import pathlib
import unittest
import json

import rtdsl as rt
from rtdsl import hiprt_runtime


ROOT = pathlib.Path(__file__).resolve().parents[1]
HIPRT_CORE = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_core.cpp"
HIPRT_API = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal3768_hiprt_fixed_radius_threshold_count_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3768_hiprt_fixed_radius_threshold_count_a5000.json"


def _native_threshold_count_available() -> bool:
    try:
        rt.hiprt_context_probe()
        lib = hiprt_runtime._hiprt_lib()
    except Exception:
        return False
    return getattr(lib, "rtdl_hiprt_count_prepared_fixed_radius_threshold_reached_3d", None) is not None


def _p(point_id: int, x: float, y: float, z: float):
    return rt.Point3D(id=point_id, x=x, y=y, z=z)


class Goal3768HiprtFixedRadiusThresholdCountPortableTest(unittest.TestCase):
    def test_new_symbol_is_generic_fixed_radius_threshold_count(self) -> None:
        api = HIPRT_API.read_text(encoding="utf-8")
        core = HIPRT_CORE.read_text(encoding="utf-8")
        self.assertIn("rtdl_hiprt_count_prepared_fixed_radius_threshold_reached_3d", api)
        self.assertIn("RtdlFixedRadiusThresholdReachedCount3DKernel", core)
        self.assertIn("fixed_radius_threshold_count_3d", core)
        self.assertNotIn("dbscan", api.lower())
        self.assertNotIn("dbscan", core.lower())

    def test_empty_prepared_search_returns_zero_without_native_symbols(self) -> None:
        with rt.prepare_hiprt_fixed_radius_neighbors_3d((), radius=1.0) as prepared:
            self.assertEqual(prepared.count_threshold_reached((_p(1, 0.0, 0.0, 0.0),), threshold=1), 0)

    def test_parity_matrix_still_records_goal3768_scalar_threshold_count(self) -> None:
        from rtdsl.v2_10_amd_hiprt_benchmark_parity import v2_10_amd_hiprt_benchmark_parity

        rows = {row["app"]: row for row in v2_10_amd_hiprt_benchmark_parity()}
        dbscan = rows["rt_dbscan"]
        self.assertIn("fixed_radius_threshold_reached_count_3d", dbscan["required_engine_features"])
        self.assertIn(dbscan["parity_stage"], {"needs_generic_hiprt_extension", "ready_for_amd_functional_pod"})

    def test_report_and_artifact_record_scalar_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3768", report)
        self.assertIn("not full RT-DBSCAN acceleration", report)
        self.assertIn("fixed_radius_grouped_stream_flags", report)
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["source_commit"], "522d3e2a")
        self.assertFalse(artifact["scoped_source_dirty"])
        self.assertTrue(artifact["sample_matches_prepared_rows"])
        self.assertEqual(artifact["rt_dbscan_missing_generic_contracts"], ["fixed_radius_grouped_stream_flags"])
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)


@unittest.skipUnless(_native_threshold_count_available(), "HIPRT prepared fixed-radius threshold count unavailable")
class Goal3768HiprtFixedRadiusThresholdCountNativeTest(unittest.TestCase):
    def test_threshold_count_matches_prepared_row_path(self) -> None:
        points = (
            _p(1, 0.0, 0.0, 0.0),
            _p(2, 0.2, 0.0, 0.0),
            _p(3, 0.4, 0.0, 0.0),
            _p(4, 10.0, 10.0, 10.0),
        )
        threshold = 3
        with rt.prepare_hiprt_fixed_radius_neighbors_3d(points, radius=0.5) as prepared:
            rows = prepared.run(points, k_max=threshold)
            counts: dict[int, int] = {}
            for row in rows:
                counts[int(row["query_id"])] = counts.get(int(row["query_id"]), 0) + 1
            expected = sum(1 for point in points if counts.get(point.id, 0) >= threshold)
            self.assertEqual(prepared.count_threshold_reached(points, threshold=threshold), expected)


if __name__ == "__main__":
    unittest.main()
