import unittest

from examples.current.research_benchmarks.librts_spatial_index import (
    rtdl_librts_spatial_index_benchmark_app as app,
)
from scripts import v3_phoenix_aabb_cpu_reference_oracle as oracle


class V3PhoenixAABBCpuReferenceOracleTest(unittest.TestCase):
    def test_tiny_fixture_matches_existing_python_reference(self):
        fixture = app.make_tiny_fixture()
        arrays = oracle._fixture_arrays(fixture)
        counts = {
            "point_contains": oracle.count_point_contains(arrays["boxes"], arrays["points"], chunk_size=2),
            "range_contains": oracle.count_range_contains(arrays["boxes"], arrays["query_boxes"], chunk_size=2),
            "range_intersects": oracle.count_range_intersects(arrays["boxes"], arrays["query_boxes"], chunk_size=2),
        }
        self.assertEqual(counts, app.run_counts(fixture, "all")["counts"])

    def test_small_uniform_fixture_expected_comparison_passes(self):
        fixture = app.make_uniform_fixture(box_count=64, query_count=32, seed=2025)
        expected = app.run_counts(fixture, "all")["counts"]
        payload = oracle.run_oracle(
            box_count=64,
            query_count=32,
            seed=2025,
            chunk_size=8,
            dtype_name="float64",
            expected_counts=expected,
        )
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["counts"], expected)
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertIn("not a product runtime path", payload["oracle_boundary"])


if __name__ == "__main__":
    unittest.main()
