import tempfile
import unittest
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

from scripts import v3_phoenix_m47_librts_stability_protocol as m47


class V3PhoenixM47LibRtsStabilityProtocolTest(unittest.TestCase):
    def test_dry_run_builds_two_scenario_alternating_schedule_without_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = m47.parse_args(["--output-dir", tmp])
            payload = m47.build_or_run_packet(args)

        self.assertEqual(payload["status"], m47.STATUS_DRY_RUN)
        self.assertEqual(payload["summary"]["failed_check_count"], 0)
        self.assertFalse(payload["summary"]["execute"])
        self.assertFalse(payload["summary"]["paid_pod_authorized_by_this_packet"])
        self.assertFalse(payload["summary"]["release_authorized"])
        self.assertFalse(payload["summary"]["all_app_pod_spend_authorized"])
        self.assertFalse(payload["summary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["summary"]["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["summary"]["v4_work_authorized"])
        self.assertEqual(payload["summary"]["scenario_count"], 2)
        self.assertEqual(payload["summary"]["sample_count_per_scenario"], 8)
        self.assertEqual(payload["summary"]["schedule_row_count"], 32)

        first_two = payload["schedule"][:2]
        self.assertEqual([row["tree"] for row in first_two], ["v2_14", "current"])
        self.assertIn("<v2-root-required-on-execute>", first_two[0]["command"][1])
        self.assertNotIn("<v2-root-required-on-execute>", first_two[1]["command"][1])
        next_two = payload["schedule"][2:4]
        self.assertEqual([row["tree"] for row in next_two], ["current", "v2_14"])

    def test_dry_run_commands_match_protocol_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = m47.parse_args(["--output-dir", tmp])
            schedule = m47.build_schedule(args)

        optix = next(row for row in schedule if row["scenario_id"] == "optix_cold_single_shot")
        optix_command = optix["command"]
        self.assertIn("--mode", optix_command)
        self.assertIn("optix_aabb_index", optix_command)
        self.assertIn("--box-count", optix_command)
        self.assertIn("2048", optix_command)
        self.assertIn("--repeat", optix_command)
        self.assertIn("1", optix_command)
        self.assertNotIn("--skip-counts", optix_command)

        embree = next(row for row in schedule if row["scenario_id"] == "embree_32768_stress")
        embree_command = embree["command"]
        self.assertIn("embree_aabb_index", embree_command)
        self.assertIn("32768", embree_command)
        self.assertIn("20", embree_command)
        self.assertIn("5", embree_command)
        self.assertIn("--skip-counts", embree_command)

    def test_dry_run_includes_preflight_plan_without_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            v2_root = Path(tmp) / "v2_14"
            args = m47.parse_args(["--output-dir", tmp, "--v2-root", str(v2_root)])
            payload = m47.build_or_run_packet(args)

        preflight = payload["preflight"]
        self.assertIn("nvidia_smi", preflight)
        self.assertIn("current_librts_set_b_source_signature", preflight)
        self.assertIn("current_preflight_tests", preflight)
        self.assertIn("v2_python_version", preflight)
        self.assertTrue(preflight["current_librts_set_b_source_signature"]["required"])
        self.assertFalse(payload["summary"]["execute"])
        self.assertIn("tests.v3_phoenix_librts_aabb_count_runner_test", preflight["current_preflight_tests"]["command"])

    def test_dry_run_can_execute_preflight_without_samples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = m47.parse_args(["--output-dir", tmp, "--v2-root", str(Path(tmp) / "v2_14"), "--run-preflight"])
            preflight = {
                "current_librts_set_b_source_signature": {
                    "required": True,
                    "returncode": 0,
                }
            }
            with patch.object(
                m47,
                "execute_preflight",
                return_value=(preflight, {}),
            ), patch.object(m47, "execute_schedule") as execute_schedule:
                payload = m47.build_or_run_packet(args)

        execute_schedule.assert_not_called()
        self.assertEqual(payload["status"], m47.STATUS_PREFLIGHT_ONLY)
        self.assertFalse(payload["summary"]["execute"])
        self.assertTrue(payload["summary"]["run_preflight"])
        self.assertEqual(payload["preflight"], preflight)
        self.assertEqual(payload["scenario_results"], {})
        self.assertEqual(payload["run_errors"], {})

    def test_preflight_only_failure_aborts_without_samples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = m47.parse_args(["--output-dir", tmp, "--v2-root", str(Path(tmp) / "v2_14"), "--run-preflight"])
            preflight = {
                "current_librts_set_b_source_signature": {
                    "required": True,
                    "returncode": 1,
                }
            }
            preflight_errors = {
                "preflight_current_librts_set_b_source_signature": "exit_code=1"
            }
            with patch.object(
                m47,
                "execute_preflight",
                return_value=(preflight, preflight_errors),
            ), patch.object(m47, "execute_schedule") as execute_schedule:
                payload = m47.build_or_run_packet(args)

        execute_schedule.assert_not_called()
        self.assertEqual(payload["status"], m47.STATUS_FAILED)
        self.assertEqual(payload["run_errors"], preflight_errors)
        self.assertEqual(payload["scenario_results"], {})
        self.assertIn("run_errors_present", payload["failed_checks"])

    def test_current_set_b_source_signature_preflight_passes_for_local_tree(self) -> None:
        command = [
            sys.executable,
            "-c",
            m47.CURRENT_SOURCE_SIGNATURE_SCRIPT,
            str(m47.ROOT),
        ]

        completed = subprocess.run(command, capture_output=True, text=True, check=False)

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn('"failed": []', completed.stdout)

    def test_schedule_executes_each_tree_from_its_own_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            current_root = Path(tmp) / "current"
            v2_root = Path(tmp) / "v2_14"
            args = m47.parse_args(
                [
                    "--output-dir",
                    tmp,
                    "--current-root",
                    str(current_root),
                    "--v2-root",
                    str(v2_root),
                ]
            )

        self.assertEqual(m47.cwd_for(args, tree="current"), current_root)
        self.assertEqual(m47.cwd_for(args, tree="v2_14"), v2_root)

    def test_env_for_root_includes_root_and_src_for_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = m47.env_for_root(root)

        entries = env["PYTHONPATH"].split(m47.os.pathsep)
        self.assertEqual(entries[0], str(root / "src"))
        self.assertEqual(entries[1], str(root))

    def test_execute_requires_external_authorization_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = m47.parse_args(
                [
                    "--output-dir",
                    tmp,
                    "--execute",
                    "--v2-root",
                    str(Path(tmp) / "v2_14"),
                ]
            )
            with self.assertRaisesRegex(SystemExit, "explicit external authorization token"):
                m47.build_or_run_packet(args)

    def test_m57_rerun_token_is_explicit_but_does_not_execute_in_dry_run(self) -> None:
        self.assertIn(m47.AUTHORIZATION_TOKEN, m47.AUTHORIZED_EXECUTION_TOKENS)
        self.assertIn(m47.M57_AUTHORIZATION_TOKEN, m47.AUTHORIZED_EXECUTION_TOKENS)
        self.assertEqual(
            "M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED",
            m47.M57_AUTHORIZATION_TOKEN,
        )

    def test_execute_aborts_before_samples_when_preflight_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = m47.parse_args(
                [
                    "--output-dir",
                    tmp,
                    "--execute",
                    "--v2-root",
                    str(Path(tmp) / "v2_14"),
                    "--authorization-token",
                    m47.M57_AUTHORIZATION_TOKEN,
                ]
            )
            preflight = {
                "current_librts_set_b_source_signature": {
                    "required": True,
                    "returncode": 1,
                }
            }
            preflight_errors = {
                "preflight_current_librts_set_b_source_signature": "exit_code=1"
            }
            with patch.object(
                m47,
                "execute_preflight",
                return_value=(preflight, preflight_errors),
            ), patch.object(m47, "execute_schedule") as execute_schedule:
                payload = m47.build_or_run_packet(args)

        execute_schedule.assert_not_called()
        self.assertEqual(payload["status"], m47.STATUS_FAILED)
        self.assertEqual(payload["run_errors"], preflight_errors)
        self.assertEqual(payload["scenario_results"], {})
        self.assertIn("run_errors_present", payload["failed_checks"])

    def test_classification_green_yellow_red(self) -> None:
        paired_ok = [
            {"current_stderr_empty": True, "v2_14_stderr_empty": True}
            for _ in range(8)
        ]
        green_ratios = [1.01, 0.99, 0.98, 1.02, 1.03, 1.00, 0.97, 1.01]
        self.assertEqual(
            m47.classify_ratios(green_ratios, green_ratios[1:], paired_ok),
            "green_closure_candidate_requires_external_review",
        )

        yellow_ratios = [1.30, 1.10, 1.08, 0.88, 1.06, 1.04, 1.02, 1.01]
        self.assertEqual(
            m47.classify_ratios(yellow_ratios, yellow_ratios[1:], paired_ok),
            "yellow_stability_boundary_watch_row_open",
        )

        red_ratios = [0.80, 0.90, 0.93, 0.94, 0.96, 0.92, 0.91, 0.90]
        self.assertEqual(
            m47.classify_ratios(red_ratios, red_ratios[1:], paired_ok),
            "red_failure_watch_row_open",
        )

    def test_missing_current_metadata_or_fixture_mismatch_forces_red(self) -> None:
        base_fixture = {
            "dataset": "uniform",
            "box_count": 2048,
            "point_query_count": 1024,
            "box_query_count": 1024,
            "seed": 2025,
        }
        rows = [
            {
                "scenario_id": "optix_cold_single_shot",
                "tree": "current",
                "sample": 1,
                "query_sec": 1.0,
                "stderr_empty": True,
                "payload": {
                    "mode": "optix_aabb_index",
                    "operation": "all",
                    "fixture": dict(base_fixture),
                    "primitive_contract": "generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count",
                    "prepared_execution_session_runner_used": True,
                    "productized_execution_path": "prepared_execution_session_runner",
                    "prepared_execution_session_runner_metadata": {
                        "set_b_control_candidate": True,
                    },
                },
            },
            {
                "scenario_id": "optix_cold_single_shot",
                "tree": "v2_14",
                "sample": 1,
                "query_sec": 2.0,
                "stderr_empty": True,
                "payload": {
                    "mode": "optix_aabb_index",
                    "operation": "all",
                    "fixture": {**base_fixture, "seed": 2026},
                },
            },
        ]

        result = m47.analyze_scenario(rows)

        self.assertEqual(result["m47_status_label"], "red_failure_watch_row_open")
        self.assertIn("fixture_mismatch_seed", result["paired_samples"][0]["fixture_contract_failures"])
        self.assertIn("prepared_query_mode_missing", result["paired_samples"][0]["current_metadata_failures"])

    def test_exactly_eight_samples_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = m47.parse_args(["--output-dir", tmp, "--samples", "7"])
            with self.assertRaisesRegex(SystemExit, "exactly 8"):
                m47.build_or_run_packet(args)


if __name__ == "__main__":
    unittest.main()
