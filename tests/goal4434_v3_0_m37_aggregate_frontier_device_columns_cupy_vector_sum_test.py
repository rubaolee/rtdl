from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/rtdsl/app_reference/aggregate_force_math.py"
INIT = ROOT / "src/rtdsl/__init__.py"
REPORT = ROOT / "docs/reports/goal4434_v3_0_m37_aggregate_frontier_device_columns_cupy_vector_sum_2026-06-16.md"

sys.path.insert(0, str(ROOT / "src"))


def _has_cupy() -> bool:
    try:
        import cupy  # noqa: F401
    except Exception:
        return False
    return True


class Goal4434V30M37AggregateFrontierDeviceColumnsCupyVectorSumTest(unittest.TestCase):
    def test_cupy_partner_function_is_exported(self) -> None:
        import rtdsl as rt

        self.assertTrue(hasattr(rt, "sum_aggregate_frontier_device_columns_weighted_vectors_2d_cupy"))
        self.assertEqual(
            rt.AGGREGATE_FRONTIER_DEVICE_COLUMNS_WEIGHTED_VECTOR_SUM_2D_CONTRACT,
            "generic_aggregate_frontier_device_columns_weighted_vector_sum_2d_v1",
        )
        source = SOURCE.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        for phrase in (
            "sum_aggregate_frontier_device_columns_weighted_vectors_2d_cupy",
            "AGGREGATE_FRONTIER_DEVICE_COLUMNS_WEIGHTED_VECTOR_SUM_2D_CONTRACT",
        ):
            self.assertIn(phrase, source)
            self.assertIn(phrase, init)
        for phrase in (
            "frontier_columns_materialized_on_host",
            "rt_core_speedup_claim_authorized",
            "False",
        ):
            self.assertIn(phrase, source)

    def test_partner_source_keeps_engine_boundary(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        start = source.index("def sum_aggregate_frontier_device_columns_weighted_vectors_2d_cupy")
        body = source[start:]
        self.assertIn("app-scoped partner math", body)
        self.assertIn("frontier_device_columns.as_cupy_columns()", body)
        self.assertIn("cp.bincount", body)
        self.assertNotIn("rtdl_optix_collect_aggregate_frontier_2d", body)

    @unittest.skipUnless(_has_cupy(), "CuPy is required for device-column partner parity")
    def test_cupy_partner_matches_fused_reference_when_optix_is_available(self) -> None:
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
            prepared = rt.prepare_aggregate_frontier_device_columns_2d_optix(
                tree["nodes"],
                theta=0.5,
            )
        except Exception as exc:
            self.skipTest(f"OptiX aggregate-frontier device-column backend unavailable: {exc}")

        with prepared:
            frontier = prepared.run_cupy(
                points,
                row_capacity=expected["summary"]["contribution_row_count"] + 32,
            )
            actual = rt.sum_aggregate_frontier_device_columns_weighted_vectors_2d_cupy(
                frontier,
                points,
                points,
                tree["nodes"],
                softening=0.01,
            )
            self.assertFalse(actual["metadata"]["frontier_columns_materialized_on_host"])
            self.assertFalse(actual["metadata"]["contribution_rows_materialized_on_host"])
            self.assertEqual(
                actual["metadata"]["frontier_row_count"],
                expected["summary"]["contribution_row_count"],
            )
            actual_x = cp.asnumpy(actual["columns"]["vector_x"])
            actual_y = cp.asnumpy(actual["columns"]["vector_y"])
            expected_x = [float(row["vector_x"]) for row in expected["vector_sum_rows"]]
            expected_y = [float(row["vector_y"]) for row in expected["vector_sum_rows"]]
            max_x = max(abs(float(a) - float(b)) for a, b in zip(actual_x, expected_x))
            max_y = max(abs(float(a) - float(b)) for a, b in zip(actual_y, expected_y))
            self.assertLess(max_x, 1.0e-7)
            self.assertLess(max_y, 1.0e-7)

    def test_report_records_m37_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "CuPy partner continuation",
            "frontier rows are not materialized on host",
            "app-scoped inverse-square math",
            "whole-app speedup claim remains unauthorized",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
