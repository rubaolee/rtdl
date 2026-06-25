from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.aabb_index import Aabb2D
from rtdsl.aabb_index import Point2DLike
from rtdsl.v4_aabb_index import V4_AABB_INDEX_ALL_OPS_COUNT_PREPARED_RUNNER_SURFACE
from rtdsl.v4_aabb_index import aabb_index_query_2d_all_ops_count_claim_boundary_v4
from rtdsl.v4_aabb_index import prepare_aabb_index_query_2d_all_ops_count_prepared_runner_v4


class V4AabbIndexFrontDoorTest(unittest.TestCase):
    def test_claim_boundary_preserves_release_and_whole_app_non_claims(self) -> None:
        boundary = aabb_index_query_2d_all_ops_count_claim_boundary_v4(backend="optix")

        self.assertEqual(V4_AABB_INDEX_ALL_OPS_COUNT_PREPARED_RUNNER_SURFACE, boundary["v4_api_surface"])
        self.assertEqual("rtdl_native", boundary["partner"])
        self.assertEqual(("rtdl_native",), boundary["measured_partners"])
        self.assertEqual(("optix", "embree"), boundary["validated_backends"])
        self.assertTrue(boundary["measured_backend"])
        self.assertFalse(boundary["release_claim_authorized"])
        self.assertFalse(boundary["broad_v4_speedup_claim_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(boundary["all_benchmark_speedup_claim_authorized"])
        self.assertFalse(boundary["app_specific_native_kernel_authorized"])

    def test_cpu_correctness_path_runs_without_cuda_but_makes_no_performance_claim(self) -> None:
        boxes = (
            Aabb2D(0.0, 0.0, 1.0, 1.0),
            Aabb2D(0.2, 0.2, 0.8, 0.8),
        )
        point_queries = (Point2DLike(0.5, 0.5), Point2DLike(2.0, 2.0))
        box_queries = (
            Aabb2D(0.25, 0.25, 0.75, 0.75),
            Aabb2D(0.9, 0.9, 1.1, 1.1),
        )

        with prepare_aabb_index_query_2d_all_ops_count_prepared_runner_v4(
            boxes,
            point_queries_for_bounds=point_queries,
            box_queries_for_bounds=box_queries,
            backend="cpu",
        ) as session:
            result = session.run(point_queries=point_queries, box_queries=box_queries)

        self.assertEqual(
            {"point_contains": 2, "range_contains": 2, "range_intersects": 3},
            result["counts"],
        )
        metadata = result["metadata"]
        self.assertEqual(V4_AABB_INDEX_ALL_OPS_COUNT_PREPARED_RUNNER_SURFACE, metadata["adapter"])
        self.assertEqual("AABB_INDEX_QUERY_2D", metadata["generic_primitive"])
        self.assertEqual("cpu_or_unvalidated_backend_correctness_only", metadata["partner_claim_status"])
        self.assertFalse(metadata["measured_backend"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["release_claim_authorized"])
        self.assertFalse(metadata["whole_app_speedup_claim_authorized"])

    def test_invalid_partner_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "partner must be one of"):
            aabb_index_query_2d_all_ops_count_claim_boundary_v4(partner="torch")


if __name__ == "__main__":
    unittest.main()
