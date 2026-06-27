from __future__ import annotations

import argparse
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import v3_phoenix_barnes_hut_runner_parity_pod_ab as script


def _payload_for_mode(mode: str, *, seconds: float) -> dict[str, object]:
    if mode == "prepared_aggregate_frontier_weighted_vector_optix":
        medians = {
            "wall_seconds": seconds,
            "hot_seconds_native_plus_partner": seconds * 0.9,
        }
        vector_summary = {
            "frontier_row_count": 120,
            "aggregate_contribution_row_count": 70,
            "exact_contribution_row_count": 50,
            "checksum_force_x": 1.25,
            "checksum_force_y": -2.5,
        }
        claim_flags = {
            "frontier_columns_materialized_on_host": False,
            "contribution_rows_materialized_on_host": False,
            "native_engine_app_specific": False,
            "rt_core_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        }
    else:
        medians = {
            "fused_numba_cuda_call_wall_seconds": seconds,
            "fused_numba_cuda_kernel_event_seconds": seconds * 0.8,
        }
        if mode == "prepared_execution_fused_vector_sum_numba_cuda":
            medians["prepared_execution_runner_measured_seconds"] = seconds
        vector_summary = {
            "tree_node_count": 31,
            "contribution_row_count": 120,
            "aggregate_contribution_row_count": 70,
            "exact_contribution_row_count": 50,
            "checksum_force_x": 1.25,
            "checksum_force_y": -2.5,
            "frontier_rows_materialized_on_host": False,
            "contribution_rows_materialized_on_host": False,
            "internal_device_residency_between_rtdl_phases": mode == "prepared_execution_fused_vector_sum_numba_cuda",
            "hot_path_host_materialization": False,
            "runtime_trunk_executes_end_to_end": mode == "prepared_execution_fused_vector_sum_numba_cuda",
        }
        claim_flags = {
            "frontier_rows_materialized_on_host": False,
            "contribution_rows_materialized_on_host": False,
            "hot_path_host_materialization": False,
            "native_engine_app_specific": False,
            "automatic_partner_selection_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "v4_embedding_or_external_zero_copy_authorized": False,
            "full_all_app_rerun_authorized_by_this_packet": False,
        }
    return {
        "mode": mode,
        "medians": medians,
        "vector_sum_summary": vector_summary,
        "tree_summary": {"node_count": 31},
        "validation": {"skipped": True, "reason": "unit_fake"},
        "claim_flags": claim_flags,
        "phoenix_v3_m72": (
            {
                "target": "barnes_hut_aggregate_tree_set_a_blocker",
                "scorecard_blocker_bound": True,
                "scorecard_blocker_app": "barnes_hut",
                "scorecard_blocker_current_value": 0.844,
                "scorecard_blocker_route_kind": "trunk_fix_candidate",
                "scorecard_blocker_target": "move_toward_or_above_parity",
                "win_source": "partner_continuation",
                "m43_reuse_scope": (
                    "reuse prepared-runner explicit-partner continuation discipline; "
                    "this aggregate-tree path uses numba_cuda, not the M43 CuPy "
                    "grouped-reduction kernel"
                ),
            }
            if mode == "prepared_execution_fused_vector_sum_numba_cuda"
            else {}
        ),
        "prepared_execution_session_runner": (
            {
                "schema": "rtdl.v3.phoenix.prepared_execution_session_runner.v1",
                "productized_execution_path": "prepared_execution_session_runner",
                "runtime_executed": True,
                "runtime_trunk_executes_end_to_end": True,
                "internal_device_residency_between_rtdl_phases": True,
                "hot_path_host_materialization": False,
                "prepared_execution_report": {"phase_timings": []},
                "prepared_execution_report_validation": {"status": "accept"},
                "measured_repeat_seconds": (seconds,),
                "output_finalize_sec": 0.0,
                "release_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
                "automatic_partner_selection_authorized": False,
                "v4_embedding_or_external_zero_copy_authorized": False,
                "full_all_app_rerun_authorized_by_this_packet": False,
                "scorecard_blocker_bound": True,
                "scorecard_binding": {
                    "id": "set_a_barnes_hut_app_geomean_0_844x",
                    "set": "A",
                    "app": "barnes_hut",
                    "metric": "set_a_app_geomean_v3_vs_v2_14",
                    "current_value": 0.844,
                    "source": "docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md",
                    "route_kind": "trunk_fix_candidate",
                },
                "m72_target_blocker": "set_a_barnes_hut_app_geomean_0_844x",
                "scorecard_blocker_app": "barnes_hut",
                "scorecard_blocker_current_value": 0.844,
                "scorecard_blocker_route_kind": "trunk_fix_candidate",
                "win_source": "partner_continuation",
                "m43_reuse_scope": (
                    "reuse prepared-runner explicit-partner continuation discipline; "
                    "this aggregate-tree path uses numba_cuda, not the M43 CuPy "
                    "grouped-reduction kernel"
                ),
            }
            if mode == "prepared_execution_fused_vector_sum_numba_cuda"
            else {}
        ),
    }


class V3PhoenixBarnesHutRunnerParityPodAbTest(unittest.TestCase):
    def test_packet_uses_dual_comparison_and_keeps_claims_closed(self) -> None:
        seconds_by_mode = {
            "prepared_aggregate_frontier_weighted_vector_optix": 0.12,
            "fused_frontier_force_sum_bucketized_numba_cuda": 0.011,
            "prepared_execution_fused_vector_sum_numba_cuda": 0.0105,
        }

        def fake_run_benchmark(mode: str, **_: object) -> dict[str, object]:
            return _payload_for_mode(mode, seconds=seconds_by_mode[mode])

        with tempfile.TemporaryDirectory() as tmp, patch.object(
            script.barnes_app,
            "run_benchmark",
            side_effect=fake_run_benchmark,
        ):
            args = argparse.Namespace(
                output_dir=Path(tmp),
                body_counts=[32768],
                query_repeat=11,
                warmup=3,
                samples=2,
                theta=0.5,
                bucket_size=32,
                max_depth=32,
                frontier_capacity_multiplier=700,
                skip_historical_optix=False,
            )
            payload = script.run_packet(args)

        summary = payload["summary"]
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))
        self.assertTrue(payload["checks"]["runner_control_output_equivalence_all_sizes"])
        self.assertTrue(summary["runner_control_equivalence_rows"][0]["equivalence_pass"])
        self.assertTrue(summary["runner_parity_with_existing_fused_partner"])
        self.assertTrue(summary["historical_reference_material"])
        self.assertTrue(summary["runner_step3_residency_default_ready"])
        self.assertEqual(summary["runner_step3_audit_rows"][0]["status"], "accept_step3_ready")
        self.assertEqual(summary["runner_step3_audit_rows"][0]["missing_step3_fields"], [])
        self.assertTrue(payload["checks"]["runner_step3_residency_default_ready_all_samples"])
        self.assertTrue(payload["checks"]["runner_scorecard_blocker_bound_all_samples"])
        self.assertTrue(payload["checks"]["runner_scorecard_blocker_id_all_samples"])
        self.assertTrue(payload["checks"]["runner_scorecard_blocker_app_all_samples"])
        self.assertTrue(payload["checks"]["runner_win_source_partner_continuation_all_samples"])
        self.assertTrue(payload["checks"]["runner_m43_reuse_scope_present_all_samples"])
        self.assertTrue(payload["checks"]["control_not_scorecard_bound"])
        self.assertTrue(summary["m72_blocker_metadata_ready"])
        self.assertEqual(summary["scorecard_blocker"]["id"], "set_a_barnes_hut_app_geomean_0_844x")
        self.assertEqual(
            summary["incumbent_route_declaration"]["baseline_mode"],
            "fused_frontier_force_sum_bucketized_numba_cuda",
        )
        self.assertTrue(summary["step1_replacement_candidate"])
        self.assertFalse(summary["wrapper_itself_faster_than_existing_fused_partner_claim_authorized"])
        self.assertFalse(summary["historical_optix_reference_is_primary_claim"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(summary["true_zero_copy_claim_authorized"])
        self.assertFalse(summary["full_all_app_rerun_authorized_by_this_packet"])
        self.assertAlmostEqual(
            summary["parity_rows"][0]["runner_vs_existing_fused_control_speedup"],
            0.011 / 0.0105,
        )
        self.assertAlmostEqual(
            summary["historical_reference_rows"][0]["historical_optix_over_runner_speedup"],
            0.12 / 0.0105,
        )
        self.assertIn("was_i_foolish", payload["goal_level_decision_audit"])
        self.assertIn("foolish_actions", payload["goal_level_decision_audit"])

    def test_skip_historical_mode_is_smoke_only_not_candidate(self) -> None:
        seconds_by_mode = {
            "fused_frontier_force_sum_bucketized_numba_cuda": 0.011,
            "prepared_execution_fused_vector_sum_numba_cuda": 0.0105,
        }

        def fake_run_benchmark(mode: str, **_: object) -> dict[str, object]:
            return _payload_for_mode(mode, seconds=seconds_by_mode[mode])

        with tempfile.TemporaryDirectory() as tmp, patch.object(
            script.barnes_app,
            "run_benchmark",
            side_effect=fake_run_benchmark,
        ):
            args = argparse.Namespace(
                output_dir=Path(tmp),
                body_counts=[32768],
                query_repeat=11,
                warmup=3,
                samples=1,
                theta=0.5,
                bucket_size=32,
                max_depth=32,
                frontier_capacity_multiplier=700,
                skip_historical_optix=True,
            )
            payload = script.run_packet(args)

        summary = payload["summary"]
        self.assertTrue(summary["skip_historical_optix_smoke_only"])
        self.assertTrue(summary["runner_parity_with_existing_fused_partner"])
        self.assertFalse(summary["historical_reference_material"])
        self.assertFalse(summary["step1_replacement_candidate"])
        self.assertFalse(summary["runtime_sourced_material_gain"])
        self.assertTrue(summary["m72_blocker_metadata_ready"])

    def test_runner_control_checksum_mismatch_blocks_packet(self) -> None:
        def fake_run_benchmark(mode: str, **_: object) -> dict[str, object]:
            payload = _payload_for_mode(
                mode,
                seconds={
                    "prepared_aggregate_frontier_weighted_vector_optix": 0.12,
                    "fused_frontier_force_sum_bucketized_numba_cuda": 0.011,
                    "prepared_execution_fused_vector_sum_numba_cuda": 0.0105,
                }[mode],
            )
            if mode == "prepared_execution_fused_vector_sum_numba_cuda":
                payload["vector_sum_summary"]["checksum_force_x"] = 9.0
            return payload

        with tempfile.TemporaryDirectory() as tmp, patch.object(
            script.barnes_app,
            "run_benchmark",
            side_effect=fake_run_benchmark,
        ):
            args = argparse.Namespace(
                output_dir=Path(tmp),
                body_counts=[32768],
                query_repeat=11,
                warmup=3,
                samples=1,
                theta=0.5,
                bucket_size=32,
                max_depth=32,
                frontier_capacity_multiplier=700,
                skip_historical_optix=False,
            )
            payload = script.run_packet(args)

        self.assertIn("runner_control_output_equivalence_all_sizes", payload["failed_checks"])
        self.assertFalse(payload["checks"]["runner_control_output_equivalence_all_sizes"])
        self.assertFalse(payload["summary"]["runner_control_equivalence_rows"][0]["equivalence_pass"])
        self.assertFalse(payload["summary"]["step1_replacement_candidate"])

    def test_readme_states_historical_route_is_not_primary_claim(self) -> None:
        payload = {
            "status": "ok",
            "summary": {
                "body_counts": [32768],
                "query_repeat": 11,
                "warmup": 3,
                "samples": 1,
                "runner_vs_existing_fused_control_geomean": 1.01,
                "historical_optix_over_runner_geomean": 10.0,
                "runner_parity_with_existing_fused_partner": True,
                "step1_replacement_candidate": True,
            },
        }
        text = script._readme(payload)

        self.assertIn("existing app-front-door fused Numba CUDA route", text)
        self.assertIn("historical no-go reference", text)
        self.assertIn("wrapper-is-faster wording", text)
        self.assertIn("authorizes no release", text)


if __name__ == "__main__":
    unittest.main()
