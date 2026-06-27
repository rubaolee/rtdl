from __future__ import annotations

from unittest.mock import patch
import unittest

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as v4
import rtdsl.v4_aggregate_frontier as aggregate_frontier
import rtdsl.v4_operator_catalog as catalog


class FakeFrontierOutput:
    def __init__(
        self,
        *,
        frontier_columns_materialized_on_host: bool = False,
        row_offsets_materialized_on_host: bool = False,
    ) -> None:
        self.frontier_columns_materialized_on_host = frontier_columns_materialized_on_host
        self.row_offsets_materialized_on_host = row_offsets_materialized_on_host

    def to_metadata(self) -> dict[str, object]:
        return {
            "primitive": "AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D",
            "contract": "generic_aggregate_frontier_device_columns_2d_v1",
            "native_symbol": "rtdl_optix_run_aggregate_frontier_device_columns_2d",
            "device_resident": True,
            "frontier_columns_materialized_on_host": self.frontier_columns_materialized_on_host,
            "row_offsets_materialized_on_host": self.row_offsets_materialized_on_host,
            "traversal_seconds": 0.0125,
            "source_count": 4,
            "capacity": 64,
        }


class FakePreparedFrontier:
    def __init__(self, frontier_output: FakeFrontierOutput | None = None) -> None:
        self.closed = False
        self.calls: list[dict[str, object]] = []
        self.frontier_output = frontier_output or FakeFrontierOutput()

    def run_device_columns(self, **kwargs):
        self.calls.append(dict(kwargs))
        return self.frontier_output

    def run_cupy(self, source_points, *, row_capacity=None):
        self.calls.append({"source_points": tuple(source_points), "row_capacity": row_capacity})
        return self.frontier_output

    def close(self) -> None:
        self.closed = True


class V4Goal4675AggregateFrontierPreparedRunnerTest(unittest.TestCase):
    def test_claim_boundary_is_measured_after_goal4677_but_not_release(self) -> None:
        boundary = aggregate_frontier.aggregate_frontier_device_columns_2d_prepared_runner_claim_boundary_v4(
            downstream_partner="cupy"
        )

        self.assertEqual(
            "tier2_measured_goal4677_v2_14_host_frontier_bottleneck_no_release",
            boundary["status"],
        )
        self.assertEqual(
            "v4_aggregate_frontier_device_columns_2d_prepared_runner",
            boundary["v4_api_surface"],
        )
        self.assertEqual("AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D", boundary["generic_primitive"])
        self.assertTrue(boundary["device_resident_frontier_columns_required"])
        self.assertTrue(boundary["host_frontier_materialization_before_partner_forbidden"])
        self.assertFalse(boundary["candidate_surface"])
        self.assertTrue(boundary["measured_v4_operator_surface"])
        self.assertTrue(boundary["goal4676_pod_measured"])
        self.assertFalse(boundary["pod_benchmark_authorized"])
        self.assertFalse(boundary["release_claim_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(boundary["rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["old_fused_weighted_vector_sum_promoted"])

    def test_runner_wraps_native_device_columns_and_adds_v4_metadata(self) -> None:
        prepared = FakePreparedFrontier()
        runner = aggregate_frontier.V4AggregateFrontierDeviceColumns2DPreparedRunner(
            prepared,
            downstream_partner="numba",
        )

        result = runner.run_device_columns(
            source_ids_device_ptr=11,
            source_x_device_ptr=22,
            source_y_device_ptr=33,
            source_count=4,
            row_capacity=64,
        )

        self.assertIsInstance(result["frontier"], FakeFrontierOutput)
        self.assertEqual(1, len(prepared.calls))
        metadata = result["metadata"]
        self.assertEqual(
            "v4_aggregate_frontier_device_columns_2d_prepared_runner",
            metadata["adapter"],
        )
        self.assertEqual("numba", metadata["downstream_partner"])
        self.assertEqual("AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D", metadata["generic_primitive"])
        self.assertEqual(0.0125, metadata["phase_accounting"]["aggregate_frontier_traversal_seconds"])
        self.assertEqual(0.0, metadata["phase_accounting"]["host_frontier_materialization_seconds"])
        self.assertFalse(metadata["frontier_columns_materialized_on_host"])
        self.assertFalse(metadata["row_offsets_materialized_on_host"])
        self.assertFalse(metadata["host_materialization_in_hot_path"])
        self.assertTrue(metadata["device_resident"])
        self.assertFalse(metadata["release_claim_authorized"])
        self.assertFalse(metadata["pod_benchmark_authorized"])

    def test_prepare_function_delegates_to_optix_prepare_and_returns_runner(self) -> None:
        fake_prepared = FakePreparedFrontier()
        with patch.object(
            aggregate_frontier,
            "prepare_aggregate_frontier_device_columns_2d_optix",
            return_value=fake_prepared,
        ) as prepare:
            runner = aggregate_frontier.prepare_aggregate_frontier_device_columns_2d_prepared_runner_v4(
                [{"id": 1}],
                theta=0.5,
                downstream_partner="cupy",
            )

        prepare.assert_called_once()
        self.assertIsInstance(runner, aggregate_frontier.V4AggregateFrontierDeviceColumns2DPreparedRunner)
        self.assertEqual("cupy", runner.downstream_partner)
        runner.close()
        self.assertTrue(fake_prepared.closed)

    def test_frontdoor_and_planner_expose_measured_surface_after_goal4677(self) -> None:
        boundary = v4.claim_boundary_v4()
        self.assertIn(
            "v4_aggregate_frontier_device_columns_2d_prepared_runner",
            boundary["measured_surfaces"],
        )
        self.assertNotIn(
            "v4_aggregate_frontier_device_columns_2d_prepared_runner",
            boundary["candidate_surfaces"],
        )

        plan = catalog.plan_v4_operator_request("aggregate_frontier_device_columns", partner="cupy")
        self.assertEqual("tier2_measured_ready", plan.status)
        self.assertEqual("tier2_fused_operator", plan.tier)
        self.assertEqual(
            "v4_aggregate_frontier_device_columns_2d_prepared_runner",
            plan.api_surface,
        )
        self.assertTrue(plan.measured_partner)
        self.assertFalse(plan.release_claim_authorized)
        self.assertFalse(plan.whole_app_speedup_claim_authorized)

        recognition = catalog.recognize_v4_pushdown_request(
            {"operator": "aggregate_frontier_device_columns"},
            partner="cupy",
        )
        self.assertEqual("pushdown_recognized_measured_tier2", recognition.status)
        self.assertFalse(recognition.release_claim_authorized)
        self.assertFalse(recognition.measured_catalog_claim_authorized)

    def test_invalid_backend_and_partner_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "backend must be one of"):
            aggregate_frontier.aggregate_frontier_device_columns_2d_prepared_runner_claim_boundary_v4(
                backend="embree"
            )
        with self.assertRaisesRegex(ValueError, "downstream_partner must be one of"):
            aggregate_frontier.aggregate_frontier_device_columns_2d_prepared_runner_claim_boundary_v4(
                downstream_partner="torch"
            )

    def test_host_materialized_frontier_fails_closed(self) -> None:
        runner = aggregate_frontier.V4AggregateFrontierDeviceColumns2DPreparedRunner(
            FakePreparedFrontier(
                FakeFrontierOutput(frontier_columns_materialized_on_host=True)
            )
        )

        with self.assertRaisesRegex(RuntimeError, "requires no host frontier"):
            runner.run_device_columns(
                source_ids_device_ptr=11,
                source_x_device_ptr=22,
                source_y_device_ptr=33,
                source_count=4,
                row_capacity=64,
            )

    def test_closed_runner_rejects_execution(self) -> None:
        runner = aggregate_frontier.V4AggregateFrontierDeviceColumns2DPreparedRunner(FakePreparedFrontier())
        runner.close()
        with self.assertRaisesRegex(RuntimeError, "runner is closed"):
            runner.run_device_columns(
                source_ids_device_ptr=11,
                source_x_device_ptr=22,
                source_y_device_ptr=33,
                source_count=4,
                row_capacity=64,
            )


if __name__ == "__main__":
    unittest.main()
