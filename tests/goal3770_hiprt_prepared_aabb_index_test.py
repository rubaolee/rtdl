import pathlib
import unittest
import json

import rtdsl as rt
from rtdsl import hiprt_runtime


ROOT = pathlib.Path(__file__).resolve().parents[1]
HIPRT_CORE = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_core.cpp"
HIPRT_API = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal3770_hiprt_prepared_aabb_index_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3770_hiprt_prepared_aabb_index_a5000.json"


def _native_prepared_aabb_index_available() -> bool:
    try:
        rt.hiprt_context_probe()
        lib = hiprt_runtime._hiprt_lib()
    except Exception:
        return False
    return (
        getattr(lib, "rtdl_hiprt_prepare_aabb_index_2d", None) is not None
        and getattr(lib, "rtdl_hiprt_count_prepared_aabb_index_2d", None) is not None
        and getattr(lib, "rtdl_hiprt_destroy_prepared_aabb_index_2d", None) is not None
    )


class Goal3770HiprtPreparedAabbIndexPortableTest(unittest.TestCase):
    def test_new_symbols_are_generic_prepared_aabb_index_counts(self) -> None:
        api = HIPRT_API.read_text(encoding="utf-8")
        core = HIPRT_CORE.read_text(encoding="utf-8")
        self.assertIn("rtdl_hiprt_prepare_aabb_index_2d", api)
        self.assertIn("rtdl_hiprt_count_prepared_aabb_index_2d", api)
        self.assertIn("rtdl_hiprt_destroy_prepared_aabb_index_2d", api)
        self.assertIn("RtdlAabbIndexCount2DKernel", core)
        self.assertIn("PreparedAabbIndex2D", core)
        self.assertIn("RtdlHiprtAabb2DDevice", core)
        self.assertNotIn("librts", api.lower())
        self.assertNotIn("librts", core.lower())

    def test_python_exports_and_contract_include_hiprt(self) -> None:
        self.assertIn("prepare_hiprt_aabb_index_2d", rt.__all__)
        self.assertIn("PreparedHiprtAabbIndex2D", rt.__all__)
        self.assertIn("HiprtAabbIndex2D", rt.__all__)
        self.assertEqual(
            rt.AABB_INDEX_2D_CONTRACT["backend_status"]["hiprt"],
            "native_count_point_contains_range_contains_range_intersects",
        )

    def test_backend_aliases_validate_without_native_library(self) -> None:
        from rtdsl.aabb_index import _validate_backend

        self.assertEqual(_validate_backend("hiprt"), "hiprt")
        self.assertEqual(_validate_backend("amd_hiprt"), "hiprt")
        self.assertEqual(_validate_backend("hiprt_cuda_orochi"), "hiprt")

    def test_parity_matrix_moves_librts_to_amd_functional_ready(self) -> None:
        from rtdsl.v2_10_amd_hiprt_benchmark_parity import v2_10_amd_hiprt_benchmark_parity

        rows = {row["app"]: row for row in v2_10_amd_hiprt_benchmark_parity()}
        librts = rows["librts_spatial_index"]
        self.assertIn("prepared_aabb_query_2d", librts["required_engine_features"])
        self.assertEqual(librts["missing_generic_contracts"], ())
        self.assertEqual(librts["parity_stage"], "ready_for_amd_functional_pod")

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3770", report)
        self.assertIn("AABB_INDEX_QUERY_2D", report)
        self.assertIn("count-only", report)
        self.assertIn("not AMD hardware evidence", report)
        self.assertIn("does not authorize", report)

    def test_artifact_records_clean_pod_evidence_and_boundaries(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["source_commit"], "75d19c76")
        self.assertFalse(artifact["scoped_source_dirty"])
        self.assertTrue(artifact["sample"]["direct_matches_cpu"])
        self.assertTrue(artifact["sample"]["generic_matches_cpu"])
        self.assertEqual(
            artifact["sample"]["hiprt_generic_counts"],
            {"point_contains": 3, "range_contains": 1, "range_intersects": 5},
        )
        self.assertEqual(artifact["librts_spatial_index_parity_stage"], "ready_for_amd_functional_pod")
        self.assertEqual(artifact["librts_spatial_index_missing_generic_contracts"], [])
        self.assertEqual(artifact["parity_summary"]["stage_counts"]["ready_for_amd_functional_pod"], 4)
        self.assertIn("not AMD hardware evidence", artifact["backend_route"])
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)


@unittest.skipUnless(_native_prepared_aabb_index_available(), "HIPRT prepared AABB index symbols unavailable")
class Goal3770HiprtPreparedAabbIndexNativeTest(unittest.TestCase):
    def test_prepared_counts_match_cpu_reference(self) -> None:
        boxes = (
            rt.Aabb2D(0.0, 0.0, 2.0, 2.0),
            rt.Aabb2D(1.0, 1.0, 3.0, 3.0),
            rt.Aabb2D(5.0, 5.0, 6.0, 6.0),
        )
        point_queries = ((0.5, 0.5), (1.5, 1.5), (4.0, 4.0))
        box_queries = (
            rt.Aabb2D(0.25, 0.25, 1.0, 1.0),
            rt.Aabb2D(1.5, 1.5, 5.5, 5.5),
            rt.Aabb2D(10.0, 10.0, 11.0, 11.0),
        )
        cpu = rt.query_aabb_index_2d(
            boxes,
            point_queries=point_queries,
            box_queries=box_queries,
            operation="all",
            backend="cpu",
        )["counts"]
        with rt.prepare_hiprt_aabb_index_2d(boxes) as prepared:
            self.assertEqual(prepared.count(point_queries=point_queries, operation="point_contains"), cpu["point_contains"])
            self.assertEqual(prepared.count(box_queries=box_queries, operation="range_contains"), cpu["range_contains"])
            self.assertEqual(prepared.count(box_queries=box_queries, operation="range_intersects"), cpu["range_intersects"])

        hiprt = rt.query_aabb_index_2d(
            boxes,
            point_queries=point_queries,
            box_queries=box_queries,
            operation="all",
            backend="hiprt",
        )
        self.assertEqual(hiprt["contract"], "generic_prepared_aabb_index_query_2d")
        self.assertEqual(hiprt["counts"], cpu)


if __name__ == "__main__":
    unittest.main()
