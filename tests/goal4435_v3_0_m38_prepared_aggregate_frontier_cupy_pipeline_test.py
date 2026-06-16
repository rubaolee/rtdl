from __future__ import annotations

import inspect
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/rtdsl/app_reference/aggregate_force_math.py"
INIT = ROOT / "src/rtdsl/__init__.py"
REPORT = ROOT / "docs/reports/goal4435_v3_0_m38_prepared_aggregate_frontier_cupy_pipeline_2026-06-16.md"

sys.path.insert(0, str(ROOT / "src"))


def _has_cupy() -> bool:
    try:
        import cupy  # noqa: F401
    except Exception:
        return False
    return True


class Goal4435V30M38PreparedAggregateFrontierCupyPipelineTest(unittest.TestCase):
    def test_prepared_cupy_continuation_is_exported(self) -> None:
        import rtdsl as rt

        self.assertTrue(
            hasattr(rt, "PreparedAggregateFrontierDeviceColumnsWeightedVectorSum2DCupy")
        )
        self.assertTrue(
            hasattr(rt, "prepare_aggregate_frontier_device_columns_weighted_vectors_2d_cupy")
        )
        self.assertEqual(
            rt.AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_CONTRACT,
            "generic_aggregate_frontier_device_columns_prepared_weighted_vector_sum_2d_v1",
        )
        source = SOURCE.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        for phrase in (
            "PreparedAggregateFrontierDeviceColumnsWeightedVectorSum2DCupy",
            "prepare_aggregate_frontier_device_columns_weighted_vectors_2d_cupy",
            "AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_CONTRACT",
        ):
            self.assertIn(phrase, source)
            self.assertIn(phrase, init)

    def test_prepared_continuation_declares_resident_hot_path(self) -> None:
        import rtdsl as rt

        source = inspect.getsource(rt.PreparedAggregateFrontierDeviceColumnsWeightedVectorSum2DCupy)
        for phrase in (
            "frontier_source_device_args",
            "source_ids_device_ptr",
            "source_x_device_ptr",
            "source_y_device_ptr",
            "prepared_lookup_columns_resident",
            "setup_seconds_excluded_from_hot_path",
            "frontier_columns_materialized_on_host",
            "contribution_rows_materialized_on_host",
            "public_speedup_claim_authorized",
            "False",
        ):
            self.assertIn(phrase, source)
        self.assertIn("run_device_columns", source)
        self.assertIn("cp.bincount", source)

    @unittest.skipUnless(_has_cupy(), "CuPy is required for prepared device-column pipeline parity")
    def test_prepared_pipeline_matches_fused_reference_when_optix_is_available(self) -> None:
        import cupy as cp
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

        prepared_vector = rt.prepare_aggregate_frontier_device_columns_weighted_vectors_2d_cupy(
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
            self.assertTrue(actual["metadata"]["prepared_lookup_columns_resident"])
            self.assertEqual(
                actual["vector_sum"]["metadata"]["frontier_row_count"],
                expected["summary"]["contribution_row_count"],
            )
            actual_x = cp.asnumpy(actual["vector_sum"]["columns"]["vector_x"])
            actual_y = cp.asnumpy(actual["vector_sum"]["columns"]["vector_y"])

        expected_x = [float(row["vector_x"]) for row in expected["vector_sum_rows"]]
        expected_y = [float(row["vector_y"]) for row in expected["vector_sum_rows"]]
        max_x = max(abs(float(a) - float(b)) for a, b in zip(actual_x, expected_x))
        max_y = max(abs(float(a) - float(b)) for a, b in zip(actual_y, expected_y))
        self.assertLess(max_x, 1.0e-7)
        self.assertLess(max_y, 1.0e-7)

    def test_report_records_m38_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "prepared CuPy continuation",
            "source columns are passed into M36 by device pointer",
            "frontier rows are not materialized on host",
            "not a whole-application speedup claim",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
