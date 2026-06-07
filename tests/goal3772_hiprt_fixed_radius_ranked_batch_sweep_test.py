import json
import pathlib
import unittest

import rtdsl as rt
from rtdsl import hiprt_runtime
from rtdsl.engine_feature_matrix import NATIVE


ROOT = pathlib.Path(__file__).resolve().parents[1]
HIPRT_CORE = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_core.cpp"
HIPRT_API = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal3772_hiprt_fixed_radius_ranked_batch_sweep_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3772_hiprt_fixed_radius_ranked_batch_sweep_a5000.json"


def _native_batch_available() -> bool:
    try:
        rt.hiprt_context_probe()
        lib = hiprt_runtime._hiprt_lib()
    except Exception:
        return False
    return getattr(lib, "rtdl_hiprt_aggregate_prepared_fixed_radius_ranked_summary_batch_3d", None) is not None


def _p(point_id: int, x: float, y: float, z: float):
    return rt.Point3D(id=point_id, x=x, y=y, z=z)


class Goal3772HiprtFixedRadiusRankedBatchSweepPortableTest(unittest.TestCase):
    def test_new_symbol_is_generic_batch_sweep(self) -> None:
        api = HIPRT_API.read_text(encoding="utf-8")
        core = HIPRT_CORE.read_text(encoding="utf-8")
        self.assertIn("rtdl_hiprt_aggregate_prepared_fixed_radius_ranked_summary_batch_3d", api)
        self.assertIn("aggregate_prepared_fixed_radius_ranked_summary_batch_3d", core)
        self.assertIn("write_prepared_fixed_radius_params_3d", core)
        self.assertNotIn("rtnn", api.lower())
        self.assertNotIn("rtnn", core.lower())

    def test_python_handle_exposes_batch_sweep_and_empty_path(self) -> None:
        self.assertTrue(hasattr(hiprt_runtime.PreparedHiprtFixedRadiusNeighbors3D, "aggregate_ranked_summary_batch"))
        with rt.prepare_hiprt_fixed_radius_neighbors_3d((), radius=1.0) as prepared:
            batch = prepared.aggregate_ranked_summary_batch(
                (_p(1, 0.0, 0.0, 0.0),),
                ({"radius": 0.5, "k_max": 2}, {"radius": 1.0, "k_max": 4}),
            )
        self.assertEqual(len(batch), 2)
        self.assertEqual(batch[0]["query_count"], 1)
        self.assertEqual(batch[0]["bounded_neighbor_count"], 0)
        self.assertEqual(batch[0]["request_index"], 0)
        self.assertEqual(batch[1]["k_max"], 4)

    def test_single_prepared_aggregate_rejects_silent_radius_override(self) -> None:
        with rt.prepare_hiprt_fixed_radius_neighbors_3d((), radius=1.0) as prepared:
            with self.assertRaisesRegex(ValueError, "use aggregate_ranked_summary_batch"):
                prepared.aggregate_ranked_summary((_p(1, 0.0, 0.0, 0.0),), k_max=2, radius=0.5)

    def test_parity_matrix_moves_rtnn_to_ready_for_amd_functional_pod(self) -> None:
        from rtdsl.v2_10_amd_hiprt_benchmark_parity import summarize_v2_10_amd_hiprt_benchmark_parity
        from rtdsl.v2_10_amd_hiprt_benchmark_parity import v2_10_amd_hiprt_benchmark_parity

        rows = {row["app"]: row for row in v2_10_amd_hiprt_benchmark_parity()}
        rtnn = rows["rtnn"]
        self.assertIn("fixed_radius_ranked_summary_batched_sweep_3d", rtnn["required_engine_features"])
        self.assertEqual(rtnn["hiprt_feature_statuses"]["fixed_radius_ranked_summary_batched_sweep_3d"], NATIVE)
        self.assertEqual(rtnn["missing_generic_contracts"], ())
        self.assertEqual(rtnn["parity_stage"], "ready_for_amd_functional_pod")
        summary = summarize_v2_10_amd_hiprt_benchmark_parity()
        self.assertEqual(summary["stage_counts"]["ready_for_amd_functional_pod"], 5)
        self.assertIn("rtnn", summary["ready_for_amd_functional_pod_apps"])

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3772", report)
        self.assertIn("batched prepared-query sweep", report)
        self.assertIn("not AMD hardware evidence", report)
        self.assertIn("does not authorize", report)

    def test_artifact_records_clean_pod_evidence_and_boundary(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertFalse(artifact["scoped_source_dirty"])
        self.assertTrue(artifact["sample"]["batch_matches_repeated_single_aggregate"])
        self.assertEqual(artifact["rtnn_missing_generic_contracts"], [])
        self.assertEqual(artifact["rtnn_parity_stage"], "ready_for_amd_functional_pod")
        self.assertIn("not AMD hardware evidence", artifact["backend_route"])
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)


@unittest.skipUnless(_native_batch_available(), "HIPRT ranked-summary batch-sweep symbol unavailable")
class Goal3772HiprtFixedRadiusRankedBatchSweepNativeTest(unittest.TestCase):
    def test_batch_sweep_matches_repeated_single_aggregate_and_smaller_radius_reference(self) -> None:
        points = (
            _p(1, 0.0, 0.0, 0.0),
            _p(2, 0.2, 0.0, 0.0),
            _p(3, 0.4, 0.0, 0.0),
            _p(4, 10.0, 10.0, 10.0),
        )
        with rt.prepare_hiprt_fixed_radius_neighbors_3d(points, radius=0.5) as prepared:
            batch = prepared.aggregate_ranked_summary_batch(
                points,
                ({"radius": 0.5, "k_max": 3}, {"radius": 0.5, "k_max": 2}, {"radius": 0.25, "k_max": 2}),
            )
            expected_k3 = prepared.aggregate_ranked_summary(points, k_max=3)
            expected_k2 = prepared.aggregate_ranked_summary(points, k_max=2)
        with rt.prepare_hiprt_fixed_radius_neighbors_3d(points, radius=0.25) as smaller:
            expected_smaller = smaller.aggregate_ranked_summary(points, k_max=2)

        for got, expected in ((batch[0], expected_k3), (batch[1], expected_k2), (batch[2], expected_smaller)):
            for key in ("query_count", "bounded_neighbor_count", "nearest_id_checksum", "kth_id_checksum"):
                self.assertEqual(got[key], expected[key], key)
            self.assertAlmostEqual(got["sum_distance"], expected["sum_distance"], places=6)


if __name__ == "__main__":
    unittest.main()
