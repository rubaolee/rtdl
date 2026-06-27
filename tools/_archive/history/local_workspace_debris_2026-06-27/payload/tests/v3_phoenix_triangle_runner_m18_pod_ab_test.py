from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts import v3_phoenix_triangle_runner_m18_pod_ab as runner


class V3PhoenixTriangleRunnerM18PodAbTest(unittest.TestCase):
    def test_dry_run_builds_three_variant_harness_without_pod_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            args = runner.parse_args(
                [
                    "--output-dir",
                    tmpdir,
                    "--edge-file",
                    str(Path(tmpdir) / "k4.edge"),
                    "--cliques",
                    "80000",
                    "--repeat",
                    "5",
                    "--warmup",
                    "1",
                    "--dry-run",
                ]
            )
            args.output_dir = Path(tmpdir)
            args.edge_file = Path(tmpdir) / "k4.edge"
            payload = runner.run_packet(args)

        self.assertEqual(payload["summary"]["status"], runner.STATUS_NOT_RELEASE)
        self.assertFalse(payload["summary"]["release_authorized"])
        self.assertFalse(payload["summary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["summary"]["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["summary"]["focused_pod_spend_authorized_now"])
        self.assertFalse(payload["summary"]["all_app_pod_spend_authorized"])
        self.assertFalse(payload["summary"]["third_strict_set_a_material_probe_closed"])
        self.assertEqual(set(payload["variants"]), {runner.EMBREE, runner.LEGACY, runner.RUNNER})
        self.assertEqual(payload["comparisons"]["status"], "dry_run_no_performance_interpretation")

    def test_serious_scale_and_repeat_gates_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            args = runner.parse_args(
                [
                    "--output-dir",
                    tmpdir,
                    "--edge-file",
                    str(Path(tmpdir) / "tiny.edge"),
                    "--cliques",
                    "10",
                    "--dry-run",
                ]
            )
            args.output_dir = Path(tmpdir)
            args.edge_file = Path(tmpdir) / "tiny.edge"
            with self.assertRaises(SystemExit):
                runner.run_packet(args)

            args = runner.parse_args(
                [
                    "--output-dir",
                    tmpdir,
                    "--edge-file",
                    str(Path(tmpdir) / "k4.edge"),
                    "--cliques",
                    "80000",
                    "--repeat",
                    "1",
                    "--dry-run",
                ]
            )
            args.output_dir = Path(tmpdir)
            args.edge_file = Path(tmpdir) / "k4.edge"
            with self.assertRaises(SystemExit):
                runner.run_packet(args)

    def test_runner_command_and_source_use_m16_device_output_helper(self) -> None:
        args = runner.parse_args(["--dry-run", "--require-rt-hardware"])
        command = runner.build_command(args, variant=runner.RUNNER)
        self.assertIn("scripts/v3_phoenix_triangle_runner_m18_pod_ab.py", command)
        self.assertIn("--require-rt-hardware", command)

        source = Path(runner.__file__).read_text(encoding="utf-8")
        self.assertIn("run_ray_triangle_weighted_summary_device_output_stream_prepared_session", source)
        self.assertIn("prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor", source)
        self.assertIn("caller_owned_device_output_scalar", source)
        self.assertIn("hot_path_host_materialization", source)
        self.assertIn("audit_prepared_execution_session_metadata", source)
        self.assertIn("step3_residency_default_ready", source)
        self.assertIn("runner_step3_audit", source)
        self.assertIn("focused_pod_spend_authorized_now", source)

    def test_host_scalar_read_is_finalize_only_not_measured_launch_body(self) -> None:
        source = Path(runner.__file__).read_text(encoding="utf-8")
        launch_body = source.split("def launch_weighted_summary_device_output_stream", 1)[1].split(
            "def finalize_weighted_summary_device_output_stream",
            1,
        )[0]
        finalize_body = source.split("def finalize_weighted_summary_device_output_stream", 1)[1].split(
            "def close",
            1,
        )[0]

        self.assertNotIn("weighted_hit_sum_out.get", launch_body)
        self.assertIn("weighted_hit_sum_out.get", finalize_body)
        self.assertIn("host_scalar_materialized_during_hot_path", launch_body)
        self.assertIn("finalize_weighted_summary=", source)

    def test_failure_checks_fail_closed_on_control_oracle_mismatch(self) -> None:
        edge_file = {
            "exists": True,
            "file_size_multiple_of_edge_record": True,
            "actual_edge_count_matches_expected": True,
            "actual_bytes_matches_expected": True,
            "checksum_matches_expected": True,
            "expected_oracle_triangle_count": 320000,
        }
        variant_payloads = {
            runner.EMBREE: {
                "status": "ok",
                "wrapper_wall_sec": 10.0,
                "payload": {
                    "oracle_triangle_count": 320000,
                    "generic_rt_weighted_triangle_count": 319999,
                    "triangle_count_matches_oracle": False,
                    "timing_ms": {"query_median_ms": 1000.0},
                },
            },
            runner.LEGACY: {
                "status": "ok",
                "wrapper_wall_sec": 1.0,
                "payload": {
                    "oracle_triangle_count": 320000,
                    "generic_rt_weighted_triangle_count": 320000,
                    "triangle_count_matches_oracle": True,
                    "timing_ms": {"query_median_ms": 100.0},
                },
            },
            runner.RUNNER: {
                "status": "ok",
                "runtime_trunk_executes_end_to_end": True,
                "step3_residency_default_ready": True,
                "triangle_count_matches_oracle": True,
                "oracle_triangle_count": 320000,
                "weighted_hit_sum": 320000,
                "timing_sec": {
                    "runner_measured_median": 0.1,
                    "outer_wall": 1.0,
                },
            },
        }
        oracle_checks = runner.oracle_check_payload(
            variant_payloads,
            expected_oracle_triangle_count=320000,
            dry_run=False,
        )
        failed = runner.failure_checks(
            variant_payloads,
            {},
            {
                "runner_vs_embree_hot_speedup": 10.0,
                "runner_vs_embree_wall_speedup": 10.0,
                "runner_vs_legacy_wall_speedup": 1.0,
            },
            edge_file=edge_file,
            oracle_checks=oracle_checks,
            dry_run=False,
        )

        self.assertIn(f"{runner.EMBREE}_oracle_mismatch", failed)
        self.assertFalse(oracle_checks["all_passed"])

    def test_edge_file_metadata_checksums_exact_k4_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            wrong_path = Path(tmpdir) / "wrong.edge"
            wrong_path.write_bytes(b"\0" * (6 * 8))

            wrong = runner.edge_file_metadata(
                wrong_path,
                cliques=1,
                generated_now=False,
                dry_run=False,
            )

            self.assertTrue(wrong["actual_edge_count_matches_expected"])
            self.assertFalse(wrong["checksum_matches_expected"])
            self.assertFalse(wrong["usable_for_m18"])

            args = runner.parse_args(
                [
                    "--output-dir",
                    tmpdir,
                    "--edge-file",
                    str(Path(tmpdir) / "correct.edge"),
                    "--cliques",
                    "1",
                    "--repeat",
                    "5",
                    "--allow-non-serious-local-smoke",
                    "--generate-edge-file",
                ]
            )
            args.output_dir = Path(tmpdir)
            args.edge_file = Path(tmpdir) / "correct.edge"
            correct = runner.prepare_edge_file(args)

            self.assertTrue(correct["generated_now"])
            self.assertTrue(correct["checksum_matches_expected"])
            self.assertTrue(correct["usable_for_m18"])


if __name__ == "__main__":
    unittest.main()
