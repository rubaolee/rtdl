import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts import v3_phoenix_rtnn_prepared_execution_runner_repeat50_pod_ab as pod_ab

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "current" / "research_benchmarks" / "rtnn" / "rtdl_rtnn_benchmark_app.py"
PREPARED_EXECUTION = ROOT / "src" / "rtdsl" / "prepared_execution.py"
POD_AB = ROOT / "scripts" / "v3_phoenix_rtnn_prepared_execution_runner_repeat50_pod_ab.py"


class V3PhoenixRtnnPreparedExecutionRunnerWiringTest(unittest.TestCase):
    def test_cli_exposes_prepared_execution_ranked_summary_mode(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src;."
        help_text = subprocess.check_output(
            [sys.executable, str(APP), "--help"],
            cwd=ROOT,
            env=env,
            text=True,
        )

        self.assertIn("prepared_execution_ranked_summary", help_text)
        self.assertIn("--repeat", help_text)
        self.assertIn("--query-batch-size", help_text)

    def test_rtnn_mode_routes_through_generic_prepared_execution_runner(self) -> None:
        text = APP.read_text(encoding="utf-8")
        section = text[
            text.index("def rtnn_prepared_execution_ranked_summary_payload"):
            text.index("def rtnn_prepared_ranked_summary_raw_payload")
        ]

        self.assertIn("rt.run_fixed_radius_ranked_summary_3d_prepared_session", section)
        self.assertIn("productized_execution_path", section)
        self.assertIn("prepared_execution_session_runner", section)
        self.assertIn("require_repeat50_material_probe=repeat >= 50", section)
        self.assertIn("full_all_app_rerun_authorized_by_this_packet", section)
        self.assertNotIn("run_rtdl_batched_3d_neighbors", section)
        self.assertNotIn("public_speedup_claim_authorized\": True", section)
        self.assertNotIn("broad_v3_faster_than_v2_claim_authorized\": True", section)

    def test_generic_helper_body_is_not_app_named(self) -> None:
        text = PREPARED_EXECUTION.read_text(encoding="utf-8")
        section = text[
            text.index("def run_fixed_radius_ranked_summary_3d_prepared_session"):
            text.index("def run_aabb_index_query_2d_range_intersection_prepared_session")
        ]

        self.assertNotIn("rtnn", section.lower())
        self.assertIn('primitive="fixed_radius_ranked_summary_3d"', section)
        self.assertIn("runtime_trunk_executes_end_to_end", section)
        self.assertIn("internal_device_residency_between_rtdl_phases", section)
        self.assertIn("v4_embedding_or_external_zero_copy_authorized", section)

    def test_pod_ab_runner_is_focused_repeat50_not_all_app(self) -> None:
        text = POD_AB.read_text(encoding="utf-8")

        self.assertIn("SERIOUS_POINT_COUNT_FLOOR = 1_048_576", text)
        self.assertIn("parser.add_argument(\"--repeat\", type=int, default=50)", text)
        self.assertIn("LEGACY = \"legacy_app_front_door_prepared_optix\"", text)
        self.assertIn("RUNNER = \"productized_prepared_execution_runner\"", text)
        self.assertIn("CUPY = \"cupy_grid_reference\"", text)
        self.assertIn("rtnn_prepared_execution_ranked_summary_payload", text)
        self.assertIn("audit_prepared_execution_session_metadata", text)
        self.assertIn("runner_step3_audit", text)
        self.assertIn("step3_residency_default_ready", text)
        self.assertIn("run_cupy_grid_3d_ranked_summary", text)
        self.assertIn("full_all_app_rerun_authorized_by_this_packet", text)
        self.assertIn("no_all_app_authorization", text)
        self.assertNotIn("run_all_app", text.lower())
        self.assertNotIn("paired_v2_v3_benchmark", text.lower())

    def test_pod_ab_summary_carries_m31_step3_audit_payload(self) -> None:
        def summary() -> dict[str, object]:
            return {
                "row_count": 3,
                "bounded_neighbor_count": 6,
                "nearest_id_checksum": 9,
                "kth_id_checksum": 12,
                "sum_distance": 1.5,
            }

        metadata = {
            "schema": "rtdl.v3.phoenix.prepared_execution_session_runner.m3_3",
            "productized_execution_path": "prepared_execution_session_runner",
            "runtime_executed": True,
            "runtime_trunk_executes_end_to_end": True,
            "internal_device_residency_between_rtdl_phases": True,
            "hot_path_host_materialization": False,
            "measured_repeat_seconds": (0.1, 0.1),
            "measured_median_sec": 0.1,
            "output_finalize_sec": 0.0,
            "repeat50_material_probe_candidate": True,
            "prepared_execution_report": {
                "summary_sec": {"setup": 0.2},
            },
            "prepared_execution_report_validation": {"status": "accept"},
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        }
        variant_payloads = {
            pod_ab.LEGACY: {
                "runner_payload": {
                    "ok": True,
                    "result_mode": "legacy",
                    "query_count": 3,
                    "search_count": 3,
                    "elapsed_median_sec": 0.2,
                    "input_load_sec": 0.01,
                    "input_pack_sec": 0.01,
                    "execution_prepare_sec": 0.01,
                    "ranked_aggregate_summary": summary(),
                },
                "phoenix_v3_outer_wall_sec": 0.4,
                "release_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
                "full_all_app_rerun_authorized_by_this_packet": False,
            },
            pod_ab.RUNNER: {
                "mode": "prepared_execution_ranked_summary",
                "point_count": 3,
                "runtime_trunk_executes_end_to_end": True,
                "runner_metadata": metadata,
                "runner_payload": summary(),
                "timing_sec": {
                    "input_load_pack": 0.01,
                    "runner_wall": 0.25,
                    "runner_after_input_load_pack": 0.24,
                },
                "release_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
                "full_all_app_rerun_authorized_by_this_packet": False,
            },
            pod_ab.CUPY: {
                "ok": True,
                "mode": "cupy_grid_reference",
                "query_count": 3,
                "search_count": 3,
                "elapsed_runs_sec": (0.5, 0.5),
                "input_load_sec": 0.01,
                "grid_prepare_sec": 0.01,
                "summary": summary(),
                "release_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
                "full_all_app_rerun_authorized_by_this_packet": False,
            },
        }
        scratch = ROOT / "scratch"
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as tmpdir:
            args = SimpleNamespace(
                output_dir=Path(tmpdir),
                point_file=None,
                point_count=pod_ab.SERIOUS_POINT_COUNT_FLOOR,
                distribution="uniform",
                seed=20260622,
                radius=0.02,
                k_max=50,
                repeat=50,
                warmups=3,
                skip_cupy=False,
                allow_non_serious_local_smoke=False,
            )
            payload = pod_ab.build_payload(
                args=args,
                point_manifest={"path": str(Path(tmpdir) / "points.csv")},
                environment={"hardware_gate": {"status": "pass"}},
                variant_payloads=variant_payloads,
                run_errors={},
            )

        self.assertEqual(payload["failed_checks"], [])
        audit = payload["summary"]["runner_step3_audit"]
        self.assertEqual(audit["status"], "accept_step3_ready")
        self.assertTrue(audit["step3_residency_default_ready"])
        runner_row = payload["summary"]["phase_rows"][pod_ab.RUNNER]
        self.assertTrue(runner_row["step3_residency_default_ready"])
        self.assertEqual(runner_row["step3_audit_missing_fields"], ())


if __name__ == "__main__":
    unittest.main()
