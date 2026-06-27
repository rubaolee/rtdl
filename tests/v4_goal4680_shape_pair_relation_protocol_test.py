from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as v4


class _FakeExecutor:
    def __init__(self, active_count: int = 17, *, row_stream_materialized: bool = False) -> None:
        self.active_count = active_count
        self.row_stream_materialized = row_stream_materialized
        self.closed = False

    def run(self) -> int:
        return self.active_count

    def to_metadata(self) -> dict[str, object]:
        return {
            "schema": "rtdl.optix.shape_pair_relation_active_count_prepared_left_executor.v1",
            "reusable_native_executor": True,
            "row_stream_materialized": self.row_stream_materialized,
        }

    def close(self) -> None:
        self.closed = True


class _FakePreparedRelation:
    def __init__(self) -> None:
        self.closed = False

    def last_phase_timings(self) -> dict[str, object]:
        return {
            "mode": "active_count_device_continuation_prepared_left_executor",
            "left_upload": 0.0,
        }

    def close(self) -> None:
        self.closed = True


class _FakePreparedLeft:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class V4Goal4680ShapePairRelationProtocolTest(unittest.TestCase):
    def test_claim_boundary_is_local_static_gate_not_release_surface(self) -> None:
        boundary = v4.shape_pair_relation_active_count_2d_prepared_left_executor_claim_boundary_v4()

        self.assertEqual("goal4680_local_static_gate_not_pod_measured", boundary["status"])
        self.assertEqual(
            "v4_shape_pair_relation_active_count_2d_prepared_left_executor",
            boundary["v4_api_surface"],
        )
        self.assertEqual(
            "SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_PREPARED_LEFT_EXECUTOR",
            boundary["generic_primitive"],
        )
        self.assertTrue(boundary["v2_14_same_primitive_existed"])
        self.assertTrue(boundary["same_primitive_speed_credit_requires_material_improvement"])
        self.assertFalse(boundary["candidate_surface"])
        self.assertFalse(boundary["measured_v4_operator_surface"])
        self.assertFalse(boundary["pod_benchmark_authorized"])
        self.assertFalse(boundary["release_claim_authorized"])
        self.assertFalse(boundary["app_specific_native_kernel_authorized"])

    def test_wrapper_runs_fake_executor_and_preserves_no_row_stream_contract(self) -> None:
        relation = _FakePreparedRelation()
        left = _FakePreparedLeft()
        executor = _FakeExecutor(23)
        runner = v4.V4ShapePairRelationActiveCount2DPreparedLeftExecutor(
            prepared_relation=relation,
            prepared_left=left,
            executor=executor,
        )

        result = runner.run()

        self.assertEqual(23, result["active_count"])
        self.assertFalse(result["metadata"]["host_materialization_in_hot_path"])
        self.assertTrue(result["metadata"]["runtime_executed"])
        self.assertEqual(0.0, result["phase_timings"]["left_upload"])
        self.assertTrue(result["executor_metadata"]["reusable_native_executor"])
        runner.close()
        self.assertTrue(relation.closed)
        self.assertTrue(left.closed)
        self.assertTrue(executor.closed)

    def test_wrapper_rejects_row_stream_materialization(self) -> None:
        runner = v4.V4ShapePairRelationActiveCount2DPreparedLeftExecutor(
            prepared_relation=_FakePreparedRelation(),
            prepared_left=_FakePreparedLeft(),
            executor=_FakeExecutor(row_stream_materialized=True),
        )

        with self.assertRaises(RuntimeError):
            runner.run()

    def test_protocol_freezes_strong_v2_14_denominator_and_bars(self) -> None:
        protocol = v4.v4_goal4680_shape_pair_relation_protocol().as_dict()
        bars = protocol["pass_fail_bar"]

        self.assertEqual(
            "goal4680_shape_pair_relation_local_static_frontdoor_protocol_passed_not_pod_run",
            protocol["status"],
        )
        self.assertEqual(4096, protocol["left_shape_count"])
        self.assertEqual(4096, protocol["right_shape_count"])
        self.assertEqual(7, protocol["repeat"])
        self.assertIn(
            "prepared_optix_shape_pair_active_count_device_continuation_reuse",
            protocol["v2_14_denominator"],
        )
        self.assertIn("must not silently fall back", protocol["v2_14_denominator"])
        self.assertEqual(1.20, bars["v4_hot_over_v2_14_same_primitive_min_for_speed_credit"])
        self.assertEqual(1.10, bars["v4_wall_over_v2_14_same_primitive_min_for_speed_credit"])
        self.assertFalse(bars["host_row_stream_materialization_in_hot_path_allowed"])
        self.assertFalse(bars["partner_migration_counts_as_speed"])
        self.assertFalse(bars["app_identity_kernel_allowed"])
        self.assertTrue(all(value is False for value in protocol["non_authorization"].values()))

    def test_protocol_validation_passes_and_does_not_authorize_pod(self) -> None:
        validation = v4.validate_v4_goal4680_shape_pair_relation_protocol()

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertTrue(validation["local_static_frontdoor_protocol_gate_passed"])
        self.assertFalse(validation["pod_run_authorized"])
        self.assertFalse(validation["release_authorized"])

    def test_goal4680_does_not_reopen_current_candidate_catalog(self) -> None:
        boundary = v4.claim_boundary_v4()

        self.assertEqual((), boundary["candidate_surfaces"])
        self.assertEqual([], v4.candidate_operator_catalog_v4())


if __name__ == "__main__":
    unittest.main()
