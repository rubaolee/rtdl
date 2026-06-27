from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import v3_phoenix_rayjoin_point_location_runner_pod_ab as runner


def _legacy_payload(*, elapsed: float = 0.020, row_count: int = 47262) -> dict[str, object]:
    return {
        "row_count": row_count,
        "summary": {
            "output_contract": runner.OUTPUT_CONTRACT,
            "validation_exact_count": row_count,
            "point_order_mode": "y_then_x",
        },
        "phases_sec": {
            "prepared_query_sec": elapsed,
            "prepared_query_sec_total_sec": elapsed * 50.0,
            "prepared_query_sec_repeat": 50,
            "prepared_query_sec_warmup": 5,
        },
        "native_phase_timings": {
            "row_stream_materialized": False,
            "boundary_candidate_row_stream_materialized": False,
            "candidate_download": 0.0,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
        },
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "full_all_app_rerun_authorized_by_this_packet": False,
    }


def _runner_payload(*, elapsed: float = 0.010, row_count: int = 47262) -> dict[str, object]:
    metadata = {
        "schema": "rtdl.v3.phoenix.prepared_execution_session_runner.m3_3",
        "productized_execution_path": "prepared_execution_session_runner",
        "runtime_executed": True,
        "measured_repeat_count": 50,
        "measured_median_sec": elapsed,
        "measured_total_sec": elapsed * 50.0,
        "measured_repeat_seconds": [elapsed] * 50,
        "output_finalize_sec": 0.0,
        "prepared_execution_report": {"phase_timings": []},
        "prepared_execution_report_validation": {"status": "accept"},
        "runtime_trunk_executes_end_to_end": True,
        "internal_device_residency_between_rtdl_phases": True,
        "hot_path_host_materialization": False,
        "external_device_buffer_interop_authorized": False,
        "v4_embedding_or_external_zero_copy_authorized": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "full_all_app_rerun_authorized_by_this_packet": False,
    }
    return {
        "row_count": row_count,
        "summary": {
            "output_contract": runner.OUTPUT_CONTRACT,
            "validation_exact_count": row_count,
            "point_order_mode": "y_then_x",
        },
        "phases_sec": {
            "prepared_query_sec": elapsed,
        },
        "native_phase_timings": {
            "row_stream_materialized": False,
            "boundary_candidate_row_stream_materialized": False,
            "candidate_download": 0.0,
        },
        "prepared_execution_session_runner": metadata,
        "runtime_trunk_executes_end_to_end": True,
        "internal_device_residency_between_rtdl_phases": True,
        "hot_path_host_materialization": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "v4_embedding_or_external_zero_copy_authorized": False,
        "full_all_app_rerun_authorized_by_this_packet": False,
    }


class V3PhoenixRayJoinPointLocationRunnerPodAbTest(unittest.TestCase):
    def test_run_packet_marks_material_only_for_same_contract_runtime_win(self) -> None:
        args = runner.parse_args(
            [
                "--output-dir",
                "unused",
                "--dataset",
                "data/rayjoin_public_cdb/br_county.cdb",
                "--samples",
                "2",
                "--query-repeat",
                "50",
                "--warmup",
                "5",
                "--point-order-mode",
                "y_then_x",
            ]
        )
        with (
            mock.patch.object(runner.rayjoin_app, "run_rayjoin_prepared_optix_workload", return_value=_legacy_payload()),
            mock.patch.object(
                runner.rayjoin_app,
                "run_rayjoin_prepared_execution_point_location_topology_stream_workload",
                return_value=_runner_payload(),
            ),
            mock.patch.object(runner, "_command_output", return_value=None),
        ):
            payload = runner.run_packet(args)

        self.assertEqual(payload["status"], runner.STATUS_NOT_RELEASE)
        self.assertEqual(payload["failed_checks"], [])
        summary = payload["summary"]
        self.assertEqual(summary["row_count"], 47262)
        self.assertAlmostEqual(summary["speedups"]["median_per_call_speedup_legacy_over_runner"], 2.0)
        self.assertAlmostEqual(summary["speedups"]["median_total_repeat_speedup_legacy_over_runner"], 2.0)
        self.assertTrue(summary["runner_step3_residency_default_ready"])
        self.assertEqual(summary["runner_step3_audit_rows"][0]["status"], "accept_step3_ready")
        self.assertEqual(summary["runner_step3_audit_rows"][0]["missing_step3_fields"], [])
        self.assertTrue(payload["checks"]["runner_step3_residency_default_ready_all_samples"])
        self.assertTrue(summary["material_set_a_candidate"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["full_all_app_rerun_authorized_by_this_packet"])
        self.assertEqual(
            payload["goal_level_decision_audit"]["foolish_actions"],
            "The foolish move would be to compare runner vs Embree or toy data, then call it a V3 win.",
        )

    def test_run_packet_keeps_structural_only_when_speedup_is_small(self) -> None:
        args = runner.parse_args(["--output-dir", "unused", "--samples", "1"])
        with (
            mock.patch.object(runner.rayjoin_app, "run_rayjoin_prepared_optix_workload", return_value=_legacy_payload(elapsed=0.0101)),
            mock.patch.object(
                runner.rayjoin_app,
                "run_rayjoin_prepared_execution_point_location_topology_stream_workload",
                return_value=_runner_payload(elapsed=0.0100),
            ),
            mock.patch.object(runner, "_command_output", return_value=None),
        ):
            payload = runner.run_packet(args)

        self.assertEqual(payload["failed_checks"], [])
        self.assertFalse(payload["summary"]["material_set_a_candidate"])
        self.assertLess(
            payload["summary"]["speedups"]["median_per_call_speedup_legacy_over_runner"],
            1.20,
        )

    def test_main_writes_summary_and_readme(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            with (
                mock.patch.object(runner.rayjoin_app, "run_rayjoin_prepared_optix_workload", return_value=_legacy_payload()),
                mock.patch.object(
                    runner.rayjoin_app,
                    "run_rayjoin_prepared_execution_point_location_topology_stream_workload",
                    return_value=_runner_payload(),
                ),
                mock.patch.object(runner, "_command_output", return_value=None),
            ):
                status = runner.main(["--output-dir", str(output_dir), "--samples", "1"])

            self.assertEqual(status, 0)
            payload = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], runner.SCHEMA)
            readme = (output_dir / "README.md").read_text(encoding="utf-8")
            self.assertIn("not against Embree", readme)
            self.assertIn("runner Step-3 residency audit ready", readme)
            self.assertIn("authorizes no release", readme)


if __name__ == "__main__":
    unittest.main()
