from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts import v3_phoenix_hausdorff_threshold_runner_pod_ab as runner
from rtdsl.prepared_execution import PREPARED_EXECUTION_SESSION_RUNNER_STATUS
from rtdsl.prepared_execution import PREPARED_EXECUTION_SESSION_RUNNER_VERSION


def _ready_directed_runner_metadata() -> dict[str, object]:
    return {
        "schema": PREPARED_EXECUTION_SESSION_RUNNER_VERSION,
        "status": PREPARED_EXECUTION_SESSION_RUNNER_STATUS,
        "productized_execution_path": "prepared_execution_session_runner",
        "runtime_executed": True,
        "runtime_trunk_executes_end_to_end": True,
        "prepared_execution_report": {"summary_sec": {"setup": 0.001}},
        "prepared_execution_report_validation": {"status": "accept"},
        "internal_device_residency_between_rtdl_phases": True,
        "hot_path_host_materialization": False,
        "measured_repeat_seconds": (0.002, 0.002, 0.002, 0.002, 0.002),
        "output_finalize_sec": 0.0,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
    }


class V3PhoenixHausdorffThresholdRunnerPodAbTest(unittest.TestCase):
    def test_dry_run_builds_three_route_packet_without_release_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            args = runner.parse_args(
                [
                    "--output-dir",
                    tmpdir,
                    "--copies",
                    "1",
                    "--repeat",
                    "5",
                    "--warmup",
                    "1",
                    "--allow-non-serious-local-smoke",
                    "--dry-run",
                ]
            )
            args.output_dir = Path(tmpdir)
            payload = runner.run_packet(args)

        self.assertEqual(payload["summary"]["status"], runner.STATUS_NOT_RELEASE)
        self.assertEqual(payload["failed_checks"], [])
        self.assertEqual(set(payload["variants"]), {runner.EMBREE, runner.LEGACY, runner.RUNNER})
        self.assertFalse(payload["summary"]["release_authorized"])
        self.assertFalse(payload["summary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["summary"]["all_app_rerun_authorized"])
        runner_command = payload["variants"][runner.RUNNER]["command"]
        legacy_command = payload["variants"][runner.LEGACY]["command"]
        embree_command = payload["variants"][runner.EMBREE]["command"]
        self.assertIn("directed_threshold_prepared_runner", runner_command)
        self.assertIn("directed_threshold_prepared", legacy_command)
        self.assertIn("directed_threshold_prepared", embree_command)
        self.assertIn("--require-rt-core", runner_command)
        self.assertIn("--require-rt-core", legacy_command)
        self.assertNotIn("--require-rt-core", embree_command)

    def test_serious_scale_gate_rejects_toy_without_explicit_smoke_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            args = runner.parse_args(
                [
                    "--output-dir",
                    tmpdir,
                    "--copies",
                    "1",
                    "--dry-run",
                ]
            )
            args.output_dir = Path(tmpdir)
            with self.assertRaises(SystemExit):
                runner.run_packet(args)

    def test_build_command_keeps_legacy_and_runner_modes_distinct(self) -> None:
        args = runner.parse_args(
            [
                "--copies",
                "262144",
                "--repeat",
                "5",
                "--warmup",
                "1",
                "--dry-run",
            ]
        )

        self.assertIn("directed_threshold_prepared", runner.build_command(args, variant=runner.LEGACY))
        self.assertIn("directed_threshold_prepared_runner", runner.build_command(args, variant=runner.RUNNER))
        self.assertIn("embree", runner.build_command(args, variant=runner.EMBREE))

    def test_directed_runner_step3_audit_requires_both_legs_ready(self) -> None:
        ready_leg = _ready_directed_runner_metadata()
        audit = runner.audit_hausdorff_directed_runner(
            {
                "directed_a_to_b": dict(ready_leg),
                "directed_b_to_a": dict(ready_leg),
            }
        )

        self.assertEqual(audit["status"], "accept_step3_ready")
        self.assertTrue(audit["all_directed_legs_step3_ready"])
        self.assertEqual(audit["missing_step3_fields_by_leg"]["directed_a_to_b"], ())

        incomplete_audit = runner.audit_hausdorff_directed_runner(
            {
                "directed_a_to_b": dict(ready_leg),
                "directed_b_to_a": {},
            }
        )

        self.assertEqual(incomplete_audit["status"], "incomplete_step3_audit")
        self.assertFalse(incomplete_audit["all_directed_legs_step3_ready"])
        self.assertIn(
            "accepted_phase_accounting",
            incomplete_audit["missing_step3_fields_by_leg"]["directed_b_to_a"],
        )

    def test_failed_checks_enforce_embree_material_floor_for_goal4636(self) -> None:
        args = runner.parse_args(
            [
                "--copies",
                "262144",
                "--repeat",
                "5",
                "--warmup",
                "1",
                "--require-rt-hardware",
            ]
        )
        environment = {"hardware_gate": {"status": "pass"}}
        ready_runner = {
            "used": True,
            "both_directed_legs_runtime_executed": True,
            "both_directed_legs_runtime_trunk_end_to_end": True,
            "both_directed_legs_no_threshold_rows_materialized_on_host": True,
            "both_directed_legs_internal_device_residency_between_rtdl_phases": True,
        }
        ready_step3 = {"all_directed_legs_step3_ready": True}
        variants = {
            runner.EMBREE: {"status": "ok", "matches_oracle": True},
            runner.LEGACY: {"status": "ok", "matches_oracle": True},
            runner.RUNNER: {
                "status": "ok",
                "matches_oracle": True,
                "prepared_execution_session_runner": ready_runner,
                "step3_audit": ready_step3,
            },
        }
        comparisons = {
            "runner_vs_legacy": {
                "phase_total_speedup": 1.0,
                "wrapper_wall_speedup": 1.0,
            },
            "runner_vs_embree": {
                "phase_total_speedup": 1.19,
                "wrapper_wall_speedup": 1.19,
            },
        }

        failed = runner.failed_checks_for(args, environment, variants, {}, comparisons)

        self.assertIn("runner_below_embree_phase_total_material_floor", failed)
        self.assertIn("runner_below_embree_wrapper_wall_material_floor", failed)


if __name__ == "__main__":
    unittest.main()
