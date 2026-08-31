import pathlib
import unittest
import json

import rtdsl as rt
from rtdsl import hiprt_runtime


ROOT = pathlib.Path(__file__).resolve().parents[1]
HIPRT_CORE = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_core.cpp"
HIPRT_API = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal3771_hiprt_fixed_radius_ranked_aggregate_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3771_hiprt_fixed_radius_ranked_aggregate_a5000.json"


def _native_ranked_aggregate_available() -> bool:
    try:
        rt.hiprt_context_probe()
        lib = hiprt_runtime._hiprt_lib()
    except Exception:
        return False
    return getattr(lib, "rtdl_hiprt_aggregate_prepared_fixed_radius_ranked_summary_3d", None) is not None


def _p(point_id: int, x: float, y: float, z: float):
    return rt.Point3D(id=point_id, x=x, y=y, z=z)


def _aggregate_from_rows(rows, queries):
    by_query: dict[int, list[tuple[int, float]]] = {int(point.id): [] for point in queries}
    for row in rows:
        by_query[int(row["query_id"])].append((int(row["neighbor_id"]), float(row["distance"])))
    bounded_neighbor_count = 0
    nearest_id_checksum = 0
    kth_id_checksum = 0
    sum_distance = 0.0
    for point in queries:
        ranked = sorted(by_query[int(point.id)], key=lambda item: (item[1], item[0]))
        bounded_neighbor_count += len(ranked)
        if not ranked:
            nearest_id_checksum += 0xFFFFFFFF
            kth_id_checksum += 0xFFFFFFFF
            continue
        nearest_id_checksum += ranked[0][0]
        kth_id_checksum += ranked[-1][0]
        sum_distance += sum(distance for _neighbor_id, distance in ranked)
    return {
        "query_count": len(tuple(queries)),
        "bounded_neighbor_count": bounded_neighbor_count,
        "nearest_id_checksum": nearest_id_checksum,
        "kth_id_checksum": kth_id_checksum,
        "sum_distance": sum_distance,
    }


class Goal3771HiprtFixedRadiusRankedAggregatePortableTest(unittest.TestCase):
    def test_new_symbol_is_generic_ranked_aggregate(self) -> None:
        api = HIPRT_API.read_text(encoding="utf-8")
        core = HIPRT_CORE.read_text(encoding="utf-8")
        self.assertIn("rtdl_hiprt_aggregate_prepared_fixed_radius_ranked_summary_3d", api)
        self.assertIn("RtdlFixedRadiusRankedSummaryAggregate3DKernel", core)
        self.assertIn("fixed_radius_ranked_summary_aggregate_3d", core)
        self.assertNotIn("rtnn", api.lower())
        self.assertNotIn("rtnn", core.lower())

    def test_python_handle_exposes_aggregate_method(self) -> None:
        self.assertTrue(hasattr(hiprt_runtime.PreparedHiprtFixedRadiusNeighbors3D, "aggregate_ranked_summary"))
        with rt.prepare_hiprt_fixed_radius_neighbors_3d((), radius=1.0) as prepared:
            aggregate = prepared.aggregate_ranked_summary((_p(1, 0.0, 0.0, 0.0),), k_max=3)
        self.assertEqual(aggregate["query_count"], 1)
        self.assertEqual(aggregate["bounded_neighbor_count"], 0)
        self.assertEqual(aggregate["nearest_id_checksum"], 0)
        self.assertEqual(aggregate["kth_id_checksum"], 0)

    def test_parity_matrix_removes_ranked_aggregate_from_rtnn_missing_contracts(self) -> None:
        from rtdsl.v2_10_amd_hiprt_benchmark_parity import v2_10_amd_hiprt_benchmark_parity

        rows = {row["app"]: row for row in v2_10_amd_hiprt_benchmark_parity()}
        rtnn = rows["rtnn"]
        self.assertIn("fixed_radius_ranked_summary_aggregate_3d", rtnn["required_engine_features"])
        self.assertNotIn("ranked_summary_aggregate", rtnn["missing_generic_contracts"])
        self.assertEqual(rtnn["missing_generic_contracts"], ())
        self.assertEqual(rtnn["parity_stage"], "ready_for_amd_functional_pod")

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3771", report)
        self.assertIn("ranked-summary aggregate", report)
        self.assertIn("batched prepared-query sweep", report)
        self.assertIn("not AMD hardware evidence", report)
        self.assertIn("does not authorize", report)

    def test_artifact_records_clean_pod_evidence_and_boundary(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["source_commit"], "38fa119c")
        self.assertFalse(artifact["scoped_source_dirty"])
        self.assertTrue(artifact["sample"]["integer_fields_match_row_path"])
        self.assertEqual(artifact["sample"]["sum_distance_abs_error"], 0.0)
        self.assertEqual(artifact["sample"]["hiprt_ranked_aggregate"]["bounded_neighbor_count"], 10)
        self.assertEqual(artifact["rtnn_missing_generic_contracts"], ["batched_prepared_query_sweep"])
        self.assertEqual(artifact["rtnn_parity_stage"], "needs_generic_hiprt_extension")
        self.assertIn("not AMD hardware evidence", artifact["backend_route"])
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)


@unittest.skipUnless(_native_ranked_aggregate_available(), "HIPRT ranked-summary aggregate symbol unavailable")
class Goal3771HiprtFixedRadiusRankedAggregateNativeTest(unittest.TestCase):
    def test_ranked_aggregate_matches_prepared_row_path(self) -> None:
        points = (
            _p(1, 0.0, 0.0, 0.0),
            _p(2, 0.2, 0.0, 0.0),
            _p(3, 0.4, 0.0, 0.0),
            _p(4, 10.0, 10.0, 10.0),
        )
        k_max = 3
        with rt.prepare_hiprt_fixed_radius_neighbors_3d(points, radius=0.5) as prepared:
            rows = prepared.run(points, k_max=k_max)
            expected = _aggregate_from_rows(rows, points)
            aggregate = prepared.aggregate_ranked_summary(points, k_max=k_max)
        for key in ("query_count", "bounded_neighbor_count", "nearest_id_checksum", "kth_id_checksum"):
            self.assertEqual(aggregate[key], expected[key], key)
        self.assertAlmostEqual(aggregate["sum_distance"], expected["sum_distance"], places=6)


if __name__ == "__main__":
    unittest.main()
