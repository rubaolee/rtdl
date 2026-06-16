from __future__ import annotations

import inspect
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/rtdsl/app_reference/aggregate_force_math.py"
INIT = ROOT / "src/rtdsl/__init__.py"
REPORT = ROOT / "docs/reports/goal4436_v3_0_m39_prepared_aggregate_frontier_numba_pipeline_2026-06-16.md"

sys.path.insert(0, str(ROOT / "src"))


def _has_cupy_numba_cuda() -> bool:
    try:
        import cupy  # noqa: F401
        from numba import cuda
    except Exception:
        return False
    try:
        return bool(cuda.is_available())
    except Exception:
        return False


class Goal4436V30M39PreparedAggregateFrontierNumbaPipelineTest(unittest.TestCase):
    def test_prepared_numba_continuation_is_exported(self) -> None:
        import rtdsl as rt

        self.assertTrue(
            hasattr(rt, "PreparedAggregateFrontierDeviceColumnsWeightedVectorSum2DNumba")
        )
        self.assertTrue(
            hasattr(rt, "prepare_aggregate_frontier_device_columns_weighted_vectors_2d_numba")
        )
        self.assertEqual(
            rt.AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_NUMBA_CONTRACT,
            "generic_aggregate_frontier_device_columns_prepared_weighted_vector_sum_2d_numba_v1",
        )
        source = SOURCE.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        for phrase in (
            "PreparedAggregateFrontierDeviceColumnsWeightedVectorSum2DNumba",
            "prepare_aggregate_frontier_device_columns_weighted_vectors_2d_numba",
            "AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_NUMBA_CONTRACT",
        ):
            self.assertIn(phrase, source)
            self.assertIn(phrase, init)

    def test_numba_continuation_declares_no_cpp_partner_boundary(self) -> None:
        import rtdsl as rt

        source = inspect.getsource(rt.PreparedAggregateFrontierDeviceColumnsWeightedVectorSum2DNumba)
        for phrase in (
            "frontier_source_device_args",
            "source_ids_device_ptr",
            "requires_cupy_frontier_adapter",
            "numba_cuda_jit_used",
            "raw_cuda_kernel_required",
            "global_atomic_add_used",
            "frontier_columns_materialized_on_host",
            "contribution_rows_materialized_on_host",
            "public_speedup_claim_authorized",
            "False",
        ):
            self.assertIn(phrase, source)
        full_source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("@cuda.jit", full_source)
        self.assertIn("cuda.atomic.add", full_source)

    @unittest.skipUnless(_has_cupy_numba_cuda(), "CuPy and Numba CUDA are required for live M39 parity")
    def test_prepared_numba_pipeline_matches_fused_reference_when_optix_is_available(self) -> None:
        import rtdsl as rt

        points = rt.make_v3_m8_weighted_point_grid(256)
        tree = rt.build_bucketized_aggregate_tree_2d(points, bucket_size=16)
        expected = rt.sum_aggregate_frontier_weighted_vectors_2d(
            points,
            points,
            tree["nodes"],
            theta=0.5,
            softening=0.01,
        )
        try:
            prepared_frontier = rt.prepare_aggregate_frontier_device_columns_2d_optix(
                tree["nodes"],
                theta=0.5,
            )
        except Exception as exc:
            self.skipTest(f"OptiX aggregate-frontier device-column backend unavailable: {exc}")

        prepared_vector = rt.prepare_aggregate_frontier_device_columns_weighted_vectors_2d_numba(
            points,
            points,
            tree["nodes"],
        )
        with prepared_frontier:
            actual = prepared_vector.run_with_prepared_frontier(
                prepared_frontier,
                row_capacity=expected["summary"]["contribution_row_count"] + 32,
                softening=0.01,
            )
            self.assertFalse(actual["frontier"].overflow)
            self.assertFalse(actual["metadata"]["frontier_columns_materialized_on_host"])
            self.assertFalse(actual["metadata"]["contribution_rows_materialized_on_host"])
            self.assertTrue(actual["metadata"]["requires_cupy_frontier_adapter"])
            self.assertTrue(actual["metadata"]["numba_cuda_jit_used"])
            self.assertEqual(
                actual["vector_sum"]["metadata"]["frontier_row_count"],
                expected["summary"]["contribution_row_count"],
            )
            actual_x = actual["vector_sum"]["columns"]["vector_x"].copy_to_host()
            actual_y = actual["vector_sum"]["columns"]["vector_y"].copy_to_host()

        expected_x = [float(row["vector_x"]) for row in expected["vector_sum_rows"]]
        expected_y = [float(row["vector_y"]) for row in expected["vector_sum_rows"]]
        max_x = max(abs(float(a) - float(b)) for a, b in zip(actual_x, expected_x))
        max_y = max(abs(float(a) - float(b)) for a, b in zip(actual_y, expected_y))
        self.assertLess(max_x, 1.0e-7)
        self.assertLess(max_y, 1.0e-7)

    def test_report_records_m39_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "prepared Numba continuation",
            "no-C++ partner route",
            "CuPy is only the current device-column carrier",
            "frontier rows are not materialized on host",
            "not a public speedup claim",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
