import pathlib
import unittest
import json

import rtdsl as rt
from rtdsl import hiprt_runtime


ROOT = pathlib.Path(__file__).resolve().parents[1]
HIPRT_CORE = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_core.cpp"
HIPRT_API = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal3769_hiprt_fixed_radius_threshold_flags_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3769_hiprt_fixed_radius_threshold_flags_a5000.json"


def _native_threshold_flags_available() -> bool:
    try:
        rt.hiprt_context_probe()
        lib = hiprt_runtime._hiprt_lib()
    except Exception:
        return False
    return getattr(lib, "rtdl_hiprt_write_prepared_fixed_radius_threshold_flags_3d", None) is not None


def _p(point_id: int, x: float, y: float, z: float):
    return rt.Point3D(id=point_id, x=x, y=y, z=z)


class Goal3769HiprtFixedRadiusThresholdFlagsPortableTest(unittest.TestCase):
    def test_new_symbol_is_generic_fixed_radius_threshold_flags(self) -> None:
        api = HIPRT_API.read_text(encoding="utf-8")
        core = HIPRT_CORE.read_text(encoding="utf-8")
        self.assertIn("rtdl_hiprt_write_prepared_fixed_radius_threshold_flags_3d", api)
        self.assertIn("RtdlFixedRadiusThresholdFlags3DKernel", core)
        self.assertIn("fixed_radius_threshold_flags_3d", core)
        self.assertNotIn("dbscan", api.lower())
        self.assertNotIn("dbscan", core.lower())

    def test_empty_prepared_search_returns_false_flags_without_native_symbols(self) -> None:
        queries = (_p(1, 0.0, 0.0, 0.0), _p(2, 1.0, 1.0, 1.0))
        with rt.prepare_hiprt_fixed_radius_neighbors_3d((), radius=1.0) as prepared:
            self.assertEqual(prepared.threshold_flags(queries, threshold=1), (False, False))
            self.assertEqual(prepared.threshold_reached_flags(queries, threshold=1), (False, False))

    def test_parity_matrix_moves_rt_dbscan_to_amd_functional_ready(self) -> None:
        from rtdsl.v2_10_amd_hiprt_benchmark_parity import v2_10_amd_hiprt_benchmark_parity

        rows = {row["app"]: row for row in v2_10_amd_hiprt_benchmark_parity()}
        dbscan = rows["rt_dbscan"]
        self.assertIn("fixed_radius_grouped_stream_flags_3d", dbscan["required_engine_features"])
        self.assertEqual(dbscan["missing_generic_contracts"], ())
        self.assertEqual(dbscan["parity_stage"], "ready_for_amd_functional_pod")

    def test_report_and_artifact_record_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3769", report)
        self.assertIn("ready_for_amd_functional_pod", report)
        self.assertIn("not AMD hardware evidence", report)
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["source_commit"], "a7264d39")
        self.assertFalse(artifact["scoped_source_dirty"])
        self.assertTrue(artifact["sample_flags_match_prepared_rows"])
        self.assertTrue(artifact["sample_flags_sum_matches_scalar_count"])
        self.assertEqual(artifact["rt_dbscan_parity_stage"], "ready_for_amd_functional_pod")
        self.assertEqual(artifact["rt_dbscan_missing_generic_contracts"], [])
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)


@unittest.skipUnless(_native_threshold_flags_available(), "HIPRT prepared fixed-radius threshold flags unavailable")
class Goal3769HiprtFixedRadiusThresholdFlagsNativeTest(unittest.TestCase):
    def test_threshold_flags_match_prepared_row_path(self) -> None:
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
            expected = tuple(counts.get(point.id, 0) >= threshold for point in points)
            self.assertEqual(prepared.threshold_flags(points, threshold=threshold), expected)
            self.assertEqual(prepared.threshold_reached_flags(points, threshold=threshold), expected)
            self.assertEqual(sum(prepared.threshold_flags(points, threshold=threshold)), prepared.count_threshold_reached(points, threshold=threshold))


if __name__ == "__main__":
    unittest.main()
