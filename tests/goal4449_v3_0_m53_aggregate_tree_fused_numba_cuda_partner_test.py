from __future__ import annotations

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "app_reference" / "aggregate_force_math.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
REPORT = ROOT / "docs" / "reports" / "goal4449_v3_0_m53_aggregate_tree_fused_numba_cuda_partner_2026-06-16.md"
SMOKE = ROOT / "docs" / "reports" / "goal4449_v3_0_m53_aggregate_tree_fused_numba_cuda_partner_smoke_2026-06-16.json"


def _has_numba_cuda() -> bool:
    try:
        from rtdsl.numba_partner_continuation import configure_numba_cuda_toolchain_environment

        configure_numba_cuda_toolchain_environment()
        from numba import cuda
    except Exception:
        return False
    return bool(cuda.is_available())


class Goal4449V30M53AggregateTreeFusedNumbaCudaPartnerTest(unittest.TestCase):
    def test_reusable_fused_numba_cuda_partner_contract_is_exported(self) -> None:
        import rtdsl as rt

        self.assertTrue(hasattr(rt, "prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda"))
        self.assertTrue(hasattr(rt, "sum_aggregate_tree_fused_weighted_vectors_2d_numba_cuda"))
        self.assertTrue(hasattr(rt, "PreparedAggregateTreeFusedWeightedVectorSum2DNumbaCuda"))
        self.assertEqual(
            rt.AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_NUMBA_CUDA_CONTRACT,
            "generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1",
        )

    def test_source_keeps_app_agnostic_claim_boundary(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")

        for phrase in (
            "PreparedAggregateTreeFusedWeightedVectorSum2DNumbaCuda",
            "_numba_aggregate_tree_fused_weighted_vector_sum_kernel",
            "generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1",
            "frontier_rows_emitted",
            "native_engine_app_specific",
            "rt_core_speedup_claim_authorized",
            "raw_cuda_kernel_required",
        ):
            self.assertIn(phrase, source)
        for phrase in (
            "prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda",
            "sum_aggregate_tree_fused_weighted_vectors_2d_numba_cuda",
            "AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_NUMBA_CUDA_CONTRACT",
        ):
            self.assertIn(phrase, init)
        m53_block = source[source.index("class PreparedAggregateTreeFusedWeightedVectorSum2DNumbaCuda") :]
        self.assertNotIn("Barnes-Hut", m53_block)
        self.assertNotIn("barnes_hut", m53_block)

    def test_report_and_smoke_record_reusable_api_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        smoke = json.loads(SMOKE.read_text(encoding="utf-8"))
        metadata = smoke["hot_run_metadata"]

        self.assertIn("Goal4449", report)
        self.assertIn("prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda", report)
        self.assertTrue(smoke["validation"]["passed"])
        self.assertEqual(metadata["contract"], "generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1")
        self.assertEqual(metadata["contribution_row_count"], smoke["validation"]["reference_frontier_row_count"])
        self.assertFalse(metadata["frontier_rows_emitted"])
        self.assertFalse(metadata["contribution_rows_materialized_on_host"])
        self.assertFalse(metadata["native_engine_app_specific"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])

    @unittest.skipUnless(_has_numba_cuda(), "Numba CUDA is required for live fused partner smoke")
    def test_live_fused_numba_cuda_partner_matches_cpu_reference(self) -> None:
        import rtdsl as rt

        points = tuple(
            {"id": index, "x": (index % 8) / 8.0, "y": (index // 8) / 8.0, "mass": 1.0 + (index % 5) * 0.1}
            for index in range(64)
        )
        tree = rt.build_bucketized_aggregate_tree_2d(points, bucket_size=8, max_depth=32)
        prepared = rt.prepare_aggregate_tree_fused_weighted_vectors_2d_numba_cuda(
            points,
            points,
            tree["nodes"],
            block_size=64,
        )
        actual = prepared.sum(theta=0.5, softening=0.05, use_cuda_events=True)
        columns = actual["columns"]
        vector_x = columns["vector_x"].copy_to_host()
        vector_y = columns["vector_y"].copy_to_host()
        reference = rt.sum_aggregate_frontier_weighted_vectors_2d(
            points,
            points,
            tree["nodes"],
            theta=0.5,
            softening=0.05,
        )
        expected_by_id = {
            int(row["source_id"]): (float(row["vector_x"]), float(row["vector_y"]))
            for row in reference["vector_sum_rows"]
        }
        max_abs_diff_x = max(abs(float(vector_x[index]) - expected_by_id[index][0]) for index in range(64))
        max_abs_diff_y = max(abs(float(vector_y[index]) - expected_by_id[index][1]) for index in range(64))
        metadata = actual["metadata"]

        self.assertLessEqual(max_abs_diff_x, 1.0e-7)
        self.assertLessEqual(max_abs_diff_y, 1.0e-7)
        self.assertEqual(metadata["contribution_row_count"], reference["summary"]["contribution_row_count"])
        self.assertFalse(metadata["frontier_rows_emitted"])
        self.assertFalse(metadata["frontier_rows_materialized_on_host"])
        self.assertFalse(metadata["contribution_rows_materialized_on_host"])
        self.assertFalse(metadata["native_engine_app_specific"])
        self.assertFalse(metadata["rt_cores_used"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertIsNotNone(metadata["kernel_event_ms"])


if __name__ == "__main__":
    unittest.main()
