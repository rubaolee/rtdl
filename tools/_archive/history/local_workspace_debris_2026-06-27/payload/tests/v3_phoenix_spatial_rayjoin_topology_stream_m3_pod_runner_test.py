import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner as runner


def _sample_payload(row_count: int = 7):
    return {
        "row_count": row_count,
        "summary": {
            "output_contract": "point_to_shape_positive_hit_count_exact_prepared_points",
            "validation_exact_count": row_count,
        },
        "phases_sec": {
            "prepared_query_sec": 0.010,
            "prepared_query_sec_total_sec": 0.050,
        },
        "native_phase_timings": {
            "mode": "prepared_points_exact_count",
        },
        "topology_stream_m3_phase_table": {
            "contract": "topology_stream_m3_phase_table_v1",
            "full_m3_phase_table_complete": True,
            "missing_m3_phases_for_public_row": (),
            "phase_seconds": {
                "static_scene_prepare_sec": 0.003,
                "query_stream_prepare_sec": 0.004,
                "device_transfer_or_residency_sec": 0.0,
                "rt_traversal_sec": 0.005,
                "topology_continuation_sec": 0.001,
                "host_return_or_scalar_materialization_sec": 0.0002,
            },
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "row_scoped_public_speedup_claim_authorized": False,
            "m7_promotion_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
        "topology_stream_prepared_handle": {
            "contract": "topology_stream_prepared_handle_v1",
            "generic_capability": "point_location_topology_stream",
            "query_stream_prepared": True,
            "query_stream_residency": "device_resident_prepared_point_probe_columns",
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "row_scoped_public_speedup_claim_authorized": False,
            "m7_promotion_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
        "claim_boundary": {
            "rtdl_beats_rayjoin_claim_authorized": False,
        },
        "device_resident_continuation_status": "partial_exact_prepared_points",
    }


class V3PhoenixSpatialRayJoinTopologyStreamM3PodRunnerTest(unittest.TestCase):
    def test_run_packet_is_not_m7_and_summarizes_m3_table(self):
        args = runner.parse_args(
            [
                "--output",
                "unused.json",
                "--sample-repeat",
                "2",
                "--query-repeat",
                "5",
                "--warmup",
                "1",
            ]
        )
        with (
            mock.patch.object(runner.rayjoin_app, "run_rayjoin_prepared_optix_workload", return_value=_sample_payload()),
            mock.patch.object(runner, "_command_output", return_value=None),
        ):
            payload = runner.run_packet(args)

        self.assertEqual(payload["status"], runner.STATUS_NOT_M7)
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertEqual(payload["failed_checks"], [])
        self.assertEqual(payload["summary"]["row_count"], 7)
        self.assertTrue(payload["summary"]["full_m3_phase_table_complete_all_samples"])
        self.assertEqual(
            payload["summary"]["query_stream_residency"],
            "device_resident_prepared_point_probe_columns",
        )
        self.assertEqual(
            payload["summary"]["m3_phase_sec_medians"]["rt_traversal_sec"],
            0.005,
        )

    def test_main_defaults_to_dry_run_without_calling_workload(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "packet.json"
            with mock.patch.object(runner.rayjoin_app, "run_rayjoin_prepared_optix_workload") as mocked:
                status = runner.main(["--output", str(output)])

            self.assertEqual(status, 0)
            mocked.assert_not_called()
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], runner.STATUS_DRY_RUN)
            self.assertFalse(payload["execute"])
            self.assertTrue(payload["summary"]["requires_explicit_authorization"])
            self.assertFalse(payload["summary"]["focused_pod_spend_authorized_now"])
            self.assertEqual(
                payload["planned_execution_requires_token"],
                runner.AUTHORIZATION_TOKEN,
            )
            self.assertIn("current_topology_stream_source_signature", payload["preflight"])

    def test_main_preflight_only_runs_no_samples(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "packet.json"
            preflight = {"current_topology_stream_source_signature": {"returncode": 0}}
            with (
                mock.patch.object(runner, "execute_preflight", return_value=(preflight, {})) as preflight_mock,
                mock.patch.object(runner.rayjoin_app, "run_rayjoin_prepared_optix_workload") as workload_mock,
            ):
                status = runner.main(["--output", str(output), "--run-preflight"])

            self.assertEqual(status, 0)
            preflight_mock.assert_called_once()
            workload_mock.assert_not_called()
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], runner.STATUS_PREFLIGHT_ONLY)
            self.assertEqual(payload["preflight"], preflight)
            self.assertEqual(payload["failed_checks"], [])

    def test_main_execute_requires_authorization_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "packet.json"
            with self.assertRaisesRegex(SystemExit, "explicit external authorization token"):
                runner.main(["--output", str(output), "--execute"])

    def test_execute_aborts_before_samples_when_preflight_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "packet.json"
            preflight = {"current_topology_stream_source_signature": {"returncode": 1}}
            preflight_errors = {"current_topology_stream_source_signature": "exit_code=1"}
            with (
                mock.patch.object(
                    runner,
                    "execute_preflight",
                    return_value=(preflight, preflight_errors),
                ),
                mock.patch.object(runner.rayjoin_app, "run_rayjoin_prepared_optix_workload") as workload_mock,
            ):
                status = runner.main(
                    [
                        "--output",
                        str(output),
                        "--execute",
                        "--authorization-token",
                        runner.AUTHORIZATION_TOKEN,
                    ]
                )

            self.assertEqual(status, 2)
            workload_mock.assert_not_called()
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], runner.STATUS_FAILED)
            self.assertIn(
                "preflight_current_topology_stream_source_signature",
                payload["failed_checks"],
            )

    def test_validate_sample_rejects_authorized_claims(self):
        payload = _sample_payload()
        payload["topology_stream_prepared_handle"]["public_speedup_claim_authorized"] = True
        with self.assertRaisesRegex(RuntimeError, "public_speedup_claim_authorized"):
            runner.validate_sample(payload, require_full_m3=True)

    def test_main_writes_json_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "packet.json"
            with (
                mock.patch.object(
                    runner,
                    "execute_preflight",
                    return_value=({"current_topology_stream_source_signature": {"returncode": 0}}, {}),
                ),
                mock.patch.object(runner.rayjoin_app, "run_rayjoin_prepared_optix_workload", return_value=_sample_payload()),
                mock.patch.object(runner, "_command_output", return_value=None),
            ):
                status = runner.main(
                    [
                        "--output",
                        str(output),
                        "--execute",
                        "--authorization-token",
                        runner.AUTHORIZATION_TOKEN,
                        "--sample-repeat",
                        "1",
                        "--query-repeat",
                        "2",
                        "--warmup",
                        "0",
                    ]
                )

            self.assertEqual(status, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], runner.SCHEMA)
            self.assertEqual(payload["status"], runner.STATUS_NOT_M7)


if __name__ == "__main__":
    unittest.main()
