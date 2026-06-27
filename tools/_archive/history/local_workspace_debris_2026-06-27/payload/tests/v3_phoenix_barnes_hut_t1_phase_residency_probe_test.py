from __future__ import annotations

import argparse
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import v3_phoenix_barnes_hut_t1_phase_residency_probe as script


def _payload_for_mode(mode: str, seconds: float) -> dict[str, object]:
    if mode == "prepared_aggregate_frontier_weighted_vector_optix":
        return {
            "mode": mode,
            "medians": {
                "wall_seconds": seconds,
                "hot_seconds_native_plus_partner": seconds * 0.9,
                "frontier_traversal_seconds": seconds * 0.6,
                "partner_seconds": seconds * 0.3,
            },
            "run_phases": {
                "frontier_prepare_wall_sec": 0.02,
                "vector_prepare_wall_sec": 0.01,
                "partner_prepare_seconds": 0.005,
            },
            "vector_sum_summary": {
                "frontier_row_count": 120,
                "aggregate_contribution_row_count": 70,
                "exact_contribution_row_count": 50,
                "checksum_force_x": 1.25,
                "checksum_force_y": -2.5,
            },
            "tree_summary": {"node_count": 31},
            "claim_flags": {
                "frontier_columns_materialized_on_host": False,
                "contribution_rows_materialized_on_host": False,
            },
        }
    medians = {
        "fused_numba_cuda_call_wall_seconds": seconds,
        "fused_numba_cuda_kernel_event_seconds": seconds * 0.8,
    }
    if mode == "prepared_execution_fused_vector_sum_numba_cuda":
        medians["prepared_execution_runner_measured_seconds"] = seconds
    runner = mode == "prepared_execution_fused_vector_sum_numba_cuda"
    return {
        "mode": mode,
        "medians": medians,
        "run_phases": {
            "vector_prepare_sec": 0.02,
            "runner_prepare_or_cache_sec": 0.021,
            "vector_copy_to_host_sec": 0.001,
        },
        "vector_sum_summary": {
            "tree_node_count": 31,
            "contribution_row_count": 120,
            "aggregate_contribution_row_count": 70,
            "exact_contribution_row_count": 50,
            "checksum_force_x": 1.25,
            "checksum_force_y": -2.5,
            "frontier_rows_materialized_on_host": False,
            "contribution_rows_materialized_on_host": False,
            "prepared_lookup_columns_resident": True,
            "aggregate_tree_columns_resident": True,
            "source_columns_reused": True,
            "target_columns_reused": True,
            "runtime_trunk_executes_end_to_end": runner,
            "internal_device_residency_between_rtdl_phases": runner,
            "hot_path_host_materialization": False,
            "scorecard_blocker_bound": runner,
            "win_source": "partner_continuation" if runner else "",
        },
        "tree_summary": {"node_count": 31},
        "claim_flags": {
            "frontier_rows_materialized_on_host": False,
            "contribution_rows_materialized_on_host": False,
            "hot_path_host_materialization": False,
        },
        "prepared_execution_session_runner": (
            {
                "runtime_executed": True,
                "runtime_trunk_executes_end_to_end": True,
                "internal_device_residency_between_rtdl_phases": True,
                "hot_path_host_materialization": False,
                "scorecard_blocker_bound": True,
                "win_source": "partner_continuation",
            }
            if runner
            else {}
        ),
    }


class V3PhoenixBarnesHutT1PhaseResidencyProbeTest(unittest.TestCase):
    def test_probe_records_no_movement_and_native_fail_closed(self) -> None:
        seconds_by_mode = {
            "prepared_aggregate_frontier_weighted_vector_optix": 0.12,
            "fused_frontier_force_sum_bucketized_numba_cuda": 0.0100,
            "prepared_execution_fused_vector_sum_numba_cuda": 0.0101,
        }

        def fake_run_benchmark(mode: str, **_: object) -> dict[str, object]:
            return _payload_for_mode(mode, seconds_by_mode[mode])

        with tempfile.TemporaryDirectory() as tmp, patch.object(
            script.barnes_app,
            "run_benchmark",
            side_effect=fake_run_benchmark,
        ), patch.object(
            script.rt,
            "prepare_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_optix",
            side_effect=RuntimeError(
                "AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE native OptiX traversal is not implemented yet"
            ),
        ):
            args = argparse.Namespace(
                output_dir=Path(tmp),
                body_counts=[64],
                query_repeat=1,
                warmup=0,
                samples=1,
                theta=0.5,
                bucket_size=32,
                max_depth=32,
                frontier_capacity_multiplier=700,
                skip_native_rt_attempt=False,
            )
            payload = script.run_packet(args)

        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(payload["checks"]["runner_runtime_executed_all_samples"])
        self.assertTrue(payload["checks"]["runner_internal_residency_all_samples"])
        self.assertTrue(payload["checks"]["runner_hot_materialization_absent"])
        diagnosis = payload["summary"]["diagnosis"]
        self.assertLess(diagnosis["projected_scorecard_value_geomean"], script.SCORECARD_CURRENT_VALUE)
        self.assertFalse(diagnosis["moves_0_844_blocker_toward_parity"])
        self.assertTrue(diagnosis["native_rt_fused_symbol_available"])
        self.assertFalse(diagnosis["native_rt_fused_runtime_implemented"])
        self.assertEqual(
            diagnosis["next_t2_action"],
            "native_rt_fused_required_before_rt_traversal_claim",
        )
        self.assertFalse(payload["summary"]["release_authorized"])
        self.assertFalse(payload["summary"]["broad_v3_faster_than_v2_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
