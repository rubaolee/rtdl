from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts import run_test_matrix
from scripts import v4_0_m1_linux_gpu_release_gate as gate
from scripts.v4_0_source_tree_runtime_preflight import build_payload as build_runtime_preflight


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _base_claims() -> dict[str, bool]:
    return {
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "v4_true_zero_copy_claim_authorized": False,
        "async_claim_authorized": False,
    }


def _write_synthetic_probe_outputs(artifact_dir: Path) -> None:
    _write_json(
        artifact_dir / "cupy_stream_smoke.json",
        {
            "status": "pass-with-boundary",
            "route_id": "fixed_radius_count_threshold_2d",
            "caller_stream_handle_nonzero": True,
            "pointer_identity": {"query.x": True, "output.query_ids": True},
            "pointer_echo_identity": {"query.x": True, "output.query_ids": True},
            "claim_boundaries": _base_claims(),
        },
    )
    _write_json(
        artifact_dir / "cupy_no_host_stage.json",
        {
            "status": "pass-with-boundary",
            "point_count": 4096,
            "metadata_subset": {"v4_true_zero_copy_claim_authorized": False},
            "transfer_counter_classification": {"no_host_stage_ready": True},
            "claim_boundaries": _base_claims(),
        },
    )
    _write_json(
        artifact_dir / "cupy_stream_ordering.json",
        {
            "status": "pass-with-boundary",
            "ordering_scope": "same_stream_and_cross_stream_prepare_query_event_wait",
            "validation": {
                "device_consumer_checksum_match": True,
                "cross_stream_device_consumer_checksum_match": True,
            },
            "cross_stream_prepare_query_contract": {"cross_stream_event_wait_validated": True},
            "metadata_subset": {"native_async_ready": False},
            "claim_boundaries": _base_claims(),
        },
    )
    _write_json(
        artifact_dir / "numba_partner_surface.json",
        {
            "status": "pass-with-boundary",
            "case_count": 4,
            "pass_count": 4,
            "claim_boundaries": {
                "numba_m1_devicearray_partner_surface_claim_authorized": True,
                "numba_full_partner_surface_claim_authorized": False,
            },
        },
    )
    _write_json(
        artifact_dir / "dlpack_capsule.json",
        {
            "status": "pass-with-boundary",
            "protocol": "legacy_dlpack_capsule",
            "validation": {"output_match": True},
            "dlpack_stream_contract": {"all_requested_streams_match_caller_stream": True},
            "claim_boundaries": {
                "fixed_radius_m1_dlpack_capsule_route_claim_authorized": True,
                "framework_neutral_dlpack_route_claim_authorized": False,
            },
        },
    )
    _write_json(
        artifact_dir / "pytorch_cuda_tensor.json",
        {
            "status": "pass-with-boundary",
            "validation": {
                "compatibility_matrix_all_expected": True,
                "accepted_case_count": 3,
                "rejected_case_count": 10,
            },
            "stream_contract": {"cross_stream_event_wait_validated": True},
            "claim_boundaries": {
                "pytorch_fixed_radius_m1_cuda_tensor_route_claim_authorized": True,
                "pytorch_full_partner_surface_claim_authorized": False,
            },
        },
    )
    _write_json(
        artifact_dir / "cupy_benchmark.json",
        {
            "status": "pass-with-boundary",
            "parameters": {"count": gate.DEFAULT_BENCHMARK_COUNT},
            "validation": {"output_match": True},
            "median_seconds": {"v4_prepared_query_only": 0.006},
            "claim_boundaries": _base_claims(),
        },
    )


class V40M1LinuxGpuReleaseGateTest(unittest.TestCase):
    def test_command_plan_runs_live_gpu_route_probes_and_guards(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plan = gate.build_command_plan(Path(tmp), python_executable="python3")
        names = [command.name for command in plan]

        self.assertEqual(names[0], "build_optix")
        for required in (
            "source_tree_runtime_preflight",
            "cupy_stream_smoke",
            "cupy_no_host_stage",
            "cupy_stream_ordering",
            "numba_partner_surface",
            "dlpack_capsule",
            "pytorch_cuda_tensor",
            "cupy_benchmark",
            "v4_release_candidate",
            "claim_boundary_scan",
            "git_diff_check",
            "clean_worktree",
        ):
            self.assertIn(required, names)

        by_name = {command.name: command for command in plan}
        self.assertIn("--output", by_name["cupy_stream_smoke"].command)
        self.assertIn("--output", by_name["pytorch_cuda_tensor"].command)
        self.assertIn(str(gate.DEFAULT_BENCHMARK_COUNT), by_name["cupy_benchmark"].command)

    def test_live_gate_uses_serious_default_benchmark_scale(self) -> None:
        self.assertGreaterEqual(gate.DEFAULT_BENCHMARK_COUNT, 262_144)
        self.assertGreaterEqual(gate.DEFAULT_BENCHMARK_REPEATS, 3)
        self.assertGreaterEqual(gate.DEFAULT_COMMAND_TIMEOUT_SEC, 600)

    def test_summarizer_accepts_bounded_current_m1_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = Path(tmp)
            _write_synthetic_probe_outputs(artifact_dir)

            summaries, failures = gate.summarize_probe_outputs(
                artifact_dir,
                include_benchmark=True,
                min_benchmark_count=gate.DEFAULT_BENCHMARK_COUNT,
            )

        self.assertEqual([], failures)
        self.assertEqual("pass-with-boundary", summaries["cupy_stream_smoke"]["status"])
        self.assertTrue(summaries["cupy_no_host_stage"]["no_host_stage_ready"])
        self.assertEqual(gate.DEFAULT_BENCHMARK_COUNT, summaries["cupy_benchmark"]["count"])

    def test_summarizer_rejects_public_true_zero_copy_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = Path(tmp)
            _write_synthetic_probe_outputs(artifact_dir)
            no_host = json.loads((artifact_dir / "cupy_no_host_stage.json").read_text(encoding="utf-8"))
            no_host["metadata_subset"]["v4_true_zero_copy_claim_authorized"] = True
            _write_json(artifact_dir / "cupy_no_host_stage.json", no_host)

            _summaries, failures = gate.summarize_probe_outputs(
                artifact_dir,
                include_benchmark=True,
                min_benchmark_count=gate.DEFAULT_BENCHMARK_COUNT,
            )

        self.assertIn(
            {
                "probe": "cupy_no_host_stage",
                "check": "public_true_zero_copy_blocked",
                "detail": None,
            },
            failures,
        )

    def test_build_report_keeps_release_action_separate_from_m1_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = Path(tmp)
            _write_synthetic_probe_outputs(artifact_dir)
            report = gate.build_report(
                artifact_dir=artifact_dir,
                command_results=[{"name": "v4_release_candidate", "ok": True, "status": "pass", "returncode": 0}],
                include_benchmark=True,
                min_benchmark_count=gate.DEFAULT_BENCHMARK_COUNT,
                initial_git_status_short="",
            )

        self.assertTrue(report["ok"])
        self.assertTrue(report["release_reading"]["m1_route_release_evidence_ready"])
        self.assertFalse(report["release_reading"]["front_door_switch_authorized"])
        self.assertFalse(report["release_reading"]["current_user_release_may_change"])
        self.assertTrue(report["release_reading"]["release_action_required"])
        self.assertTrue(report["claim_boundaries"]["fixed_radius_m1_python_gpu_operator_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["public_true_zero_copy_claim_authorized"])
        self.assertFalse(report["claim_boundaries"]["public_speedup_claim_authorized"])

    def test_source_tree_runtime_preflight_points_to_live_linux_gate(self) -> None:
        payload = build_runtime_preflight()
        commands = "\n".join(payload["supported_source_tree_commands"])

        self.assertIn("scripts/v4_0_m1_linux_gpu_release_gate.py", commands)
        self.assertIn("--benchmark-count 262144", commands)

    def test_v4_matrices_include_the_live_gate_static_guard(self) -> None:
        for group in ("v4_active", "v4_release_candidate"):
            modules = run_test_matrix.group_modules(group)
            self.assertIn("tests.v4_0_m1_linux_gpu_release_gate_test", modules)


if __name__ == "__main__":
    unittest.main()
