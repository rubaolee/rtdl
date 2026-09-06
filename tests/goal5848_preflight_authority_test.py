from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from experiments.goal5848_strong_baseline import contracts, preflight_worker, worker
from scripts import goal5848_finalize_preflight as finalizer
from scripts import goal5848_probe_aot_cache_hits as aot_probe
from scripts import goal5848_run_timer_free_preflight as preflight
from tests.goal5848_instrumentation_fixture import (
    write_instrumentation_fixture,
)


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


class Goal5848PreflightAuthorityTest(unittest.TestCase):
    def test_direct_triangle_preflight_rejects_no_output_contract(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            direct = root / "direct"
            direct.write_bytes(b"binary")
            ptx = root / "device.ptx"
            ptx.write_bytes(b"ptx")
            receipt = {
                "schema": "rtdl.goal5802.direct_scalar.worker.v1",
                "status": "PASS",
                "task": contracts.direct_worker_task(contracts.TRIANGLE_TASK),
                "regime": "LOCAL_UNTIMED",
                "registered_performance_timing_count": 0,
                "execute_or_regime_durations_ns": [],
                "correctness": {
                    "oracle_exact": True,
                    "reduced_u64": 65530,
                },
                "operation_ledger": {
                    "optix_launch_count": 1,
                    "application_output_d2h_bytes": 8,
                    "per_ray_d2h_bytes": 0,
                },
            }
            completed = subprocess.CompletedProcess(
                args=[str(direct)],
                returncode=0,
                stdout=json.dumps(receipt).encode(),
                stderr=b"",
            )
            args = argparse.Namespace(
                direct_worker=direct,
                precompiled_ptx=ptx,
                compaction_cubin=None,
                task=contracts.TRIANGLE_TASK,
            )
            with mock.patch.object(
                preflight_worker.subprocess, "run", return_value=completed
            ) as run:
                result = preflight_worker._direct(args)
            self.assertEqual(
                run.call_args.args[0][run.call_args.args[0].index("--task") + 1],
                contracts.direct_worker_task(contracts.TRIANGLE_TASK),
            )
            self.assertEqual(result["output_sha256"], contracts.TASK_CONTRACTS[
                contracts.TRIANGLE_TASK
            ]["public_output_sha256"])
            receipt["operation_ledger"]["per_ray_d2h_bytes"] = 1
            completed.stdout = json.dumps(receipt).encode()
            with (
                mock.patch.object(
                    preflight_worker.subprocess, "run", return_value=completed
                ),
                self.assertRaisesRegex(RuntimeError, "contract"),
            ):
                preflight_worker._direct(args)

    def test_timer_free_worker_validator_rejects_timing_mutation(self):
        value = {
            "schema": "rtdl.goal5848.timer_free_preflight_worker.v1",
            "status": "PASS__UNTIMED_EXACT_PHYSICAL_WITNESS",
            "arm": contracts.RTDL_ARM,
            "task": contracts.RELATION_TASK,
            "hardware": {},
            "details": {
                "execution_count": 2,
                "output_sha256": contracts.TASK_CONTRACTS[
                    contracts.RELATION_TASK
                ]["public_output_sha256"],
            },
            "clock_read_count": 0,
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0,
            "external_review_complete": False,
            "public_or_manuscript_claim_authorized": False,
        }
        value["receipt_sha256"] = contracts.digest(value)
        preflight._validate_worker(
            value, arm=contracts.RTDL_ARM, task=contracts.RELATION_TASK
        )
        value["registered_performance_timing_count"] = 1
        value["receipt_sha256"] = contracts.digest({
            key: item for key, item in value.items() if key != "receipt_sha256"
        })
        with self.assertRaisesRegex(RuntimeError, "preflight worker"):
            preflight._validate_worker(
                value, arm=contracts.RTDL_ARM, task=contracts.RELATION_TASK
            )

    def test_rtdl_program_bundle_selection_is_always_a_singleton_tuple(self):
        self.assertEqual(
            contracts.rtdl_program_bundles(contracts.RELATION_TASK),
            ("v4_custom_aabb_bounded_relation_composed",),
        )
        self.assertEqual(
            contracts.rtdl_program_bundles(contracts.TRIANGLE_TASK),
            ("v4_builtin_triangle_checked_reduction_composed",),
        )
        with self.assertRaisesRegex(ValueError, "no RTDL program bundle"):
            contracts.rtdl_program_bundles("unknown")

    def test_direct_worker_task_selection_is_explicit_and_fail_closed(self):
        self.assertEqual(
            contracts.direct_worker_task(contracts.RELATION_TASK),
            "CUSTOM_AABB_CLOSED_RELATION_COUNT_V2_MATCHED",
        )
        self.assertEqual(
            contracts.direct_worker_task(contracts.TRIANGLE_TASK),
            "BUILTIN_TRIANGLE_WEIGHTED_SCALAR_V2_MATCHED",
        )
        with self.assertRaisesRegex(ValueError, "no Direct worker mapping"):
            contracts.direct_worker_task("unknown")

    def test_strong_preflight_uses_two_untimed_operation_guards(self):
        guard = {"scope": "test"}
        results = [
            {
                "weighted_sum": 65530,
                "dynamic_input_receipt": {
                    "prepared_input_reused": reused,
                    "dynamic_input_generation": 1,
                },
                "independent_execute_guard": guard,
                "execute_operation_counts": {"launches": 1},
                "operation_order": ["launch"],
                "prepare_operation_counts": {"allocations": 1},
                "live_execute_guard_inside_timer": True,
            }
            for reused in (False, True)
        ]
        adapter = mock.Mock()
        adapter.execute_with_operation_guard.side_effect = results
        lifecycle, evidence = preflight_worker._strong_untimed_witness(
            adapter,
            task=contracts.TRIANGLE_TASK,
            expected=65530,
        )
        self.assertEqual(adapter.execute_with_operation_guard.call_count, 2)
        self.assertEqual(
            [row["prepared_input_reused"] for row in lifecycle],
            [False, True],
        )
        self.assertEqual(
            evidence["reused_execute"]["independent_execute_guard"], guard
        )

    def test_triangle_guarded_result_uses_reduced_u64_public_output(self):
        self.assertEqual(
            worker._public_output(
                contracts.TRIANGLE_TASK,
                {"reduced_u64": 65530},
            ),
            65530,
        )
        with self.assertRaisesRegex(RuntimeError, "outputs disagree"):
            worker._public_output(
                contracts.TRIANGLE_TASK,
                {"weighted_sum": 65530, "reduced_u64": 1},
            )

    def test_process_streams_are_preserved_byte_exact_without_overwrite(self):
        completed = subprocess.CompletedProcess(
            args=["worker"],
            returncode=1,
            stdout=b"partial-output\n",
            stderr=b"diagnostic\x00bytes\n",
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            preflight._preserve_process_streams(root, "G5848_TEST", completed)
            self.assertEqual(
                (root / "G5848_TEST.stdout").read_bytes(), completed.stdout
            )
            self.assertEqual(
                (root / "G5848_TEST.stderr").read_bytes(), completed.stderr
            )
            with self.assertRaises(FileExistsError):
                preflight._preserve_process_streams(root, "G5848_TEST", completed)

    def test_finalizer_binds_all_three_authorities_and_preregistration(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = "a" * 40
            predecessor = "b" * 40
            prereg = {
                "schema": contracts.PREREGISTRATION_SCHEMA,
                "status": "FROZEN__BEFORE_FORMAL_WORKER_ZERO",
                "source_commit": source,
                "predecessor_commit": predecessor,
                "expected_optix_sdk": "8.0.0",
                "artifacts": {
                    "device_artifact_build_receipt": {"path": "/tmp/receipt"},
                    "precompiled_ptx": {"path": "/tmp/device.ptx"},
                    "compaction_cubin": {"path": "/tmp/compaction.cubin"},
                    "aot_cache_authority": {"path": "/tmp/aot.json"},
                    "candidate_manifest": {"path": "/tmp/candidates.json"},
                },
            }
            prereg["preregistration_sha256"] = contracts.digest(prereg)
            prereg_path = root / "prereg.json"
            _write(prereg_path, prereg)
            hardware = {"gpu_uuid": "GPU-test", "compute_capability": "8.9"}
            witness = {
                "schema": "rtdl.goal5848.timer_free_witness_authority.v1",
                "status": "PASS__ALL_EIGHT_PRIMARY_ARM_TASK_WITNESSES",
                "source_commit": source,
                "predecessor_commit": predecessor,
                "preregistration_sha256": prereg["preregistration_sha256"],
                "registered_performance_timing_count": 0,
                "formal_worker_count": 0,
                "worker_count": 8,
                "process_count": 8,
                "hardware": hardware,
                "retry_count": 0,
                "discard_count": 0,
            }
            witness["authority_sha256"] = contracts.digest(witness)
            witness_path = root / "witness.json"
            _write(witness_path, witness)
            competence = {
                "schema": "rtdl.goal5848.baseline_competence.v1",
                "status": "PASS__STRONG_PYOPTIX_COMPETENT_FOR_BOTH_TASKS",
                "source_commit": source,
                "predecessor_commit": predecessor,
                "preregistration_sha256": prereg["preregistration_sha256"],
                "registered_performance_timing_count": 0,
                "formal_worker_count": 0,
                "worker_count": 4,
                "process_count": 4,
                "hardware": hardware,
                "tasks": {task: {"pass": True} for task in contracts.TASKS},
                "retry_count": 0,
                "discard_count": 0,
                "included_in_formal_estimators": False,
            }
            competence["authority_sha256"] = contracts.digest(competence)
            competence_path = root / "competence.json"
            _write(competence_path, competence)
            instrumentation_path, instrumentation = (
                write_instrumentation_fixture(
                    root,
                    source_commit=source,
                    predecessor_commit=predecessor,
                    preregistration_sha256=prereg["preregistration_sha256"],
                    hardware=hardware,
                    python_path=root / "python",
                    candidate_manifest=Path("/tmp/candidates.json"),
                )
            )
            output = root / "preflight.json"
            argv = [
                "goal5848_finalize_preflight.py",
                "--expected-source-commit",
                source,
                "--expected-predecessor-commit",
                predecessor,
                "--preregistration",
                str(prereg_path),
                "--timer-free-witness",
                str(witness_path),
                "--baseline-competence",
                str(competence_path),
                "--instrumentation-overhead",
                str(instrumentation_path),
                "--output",
                str(output),
            ]
            with (
                mock.patch.object(sys, "argv", argv),
                mock.patch.object(finalizer, "load_device_artifact_receipt"),
                mock.patch.object(finalizer, "load_aot_cache_authority"),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                finalizer.main()
            result = json.loads(output.read_text())
            self.assertEqual(result["schema"], contracts.PREFLIGHT_SCHEMA)
            self.assertEqual(result["untimed_witness_worker_count"], 8)
            self.assertEqual(result["nonformal_competence_worker_count"], 4)
            self.assertEqual(
                result["nonformal_instrumentation_worker_count"],
                contracts.instrumentation_protocol()["worker_count"],
            )
            instrumentation["tasks"][contracts.RELATION_TASK][
                "instrumentation_overhead_ppm"
            ] = contracts.INSTRUMENTATION_OVERHEAD_LIMIT_PPM + 1
            instrumentation["authority_sha256"] = contracts.digest({
                key: item
                for key, item in instrumentation.items()
                if key != "authority_sha256"
            })
            _write(instrumentation_path, instrumentation)
            argv[-1] = str(root / "rejected-preflight.json")
            with (
                mock.patch.object(sys, "argv", argv),
                mock.patch.object(finalizer, "load_device_artifact_receipt"),
                mock.patch.object(finalizer, "load_aot_cache_authority"),
                contextlib.redirect_stdout(io.StringIO()),
                self.assertRaisesRegex(RuntimeError, "summary differs"),
            ):
                finalizer.main()

    def test_aot_hit_worker_authority_rejects_compiler_module(self):
        value = {
            "schema": "rtdl.goal5848.aot_fresh_process_hit.v1",
            "status": "PASS__EXACT_VERIFIED_HIT__NO_PRODUCER_NO_COMPILER",
            "worker_id": "worker",
            "task": contracts.RELATION_TASK,
            "pid": 10,
            "python": "3.12",
            "source_commit": "a" * 40,
            "request_identity_sha256": "b" * 64,
            "entry_path": "/tmp/entry",
            "duration_ns": 10,
            "cache_hit": True,
            "producer_invoked": False,
            "producer_call_count": 0,
            "compiler_modules_before": [],
            "compiler_modules_after": [],
            "nvrtc_mappings_before": [],
            "nvrtc_mappings_after": [],
            "verification": {},
            "public_or_manuscript_claim_authorized": False,
        }
        value["receipt_sha256"] = contracts.digest(value)
        aot_probe._validate_worker(
            value,
            worker_id="worker",
            task=contracts.RELATION_TASK,
            source_commit="a" * 40,
            request_identity="b" * 64,
        )
        value["compiler_modules_after"] = ["numba"]
        value["receipt_sha256"] = contracts.digest({
            key: item for key, item in value.items() if key != "receipt_sha256"
        })
        with self.assertRaisesRegex(RuntimeError, "receipt"):
            aot_probe._validate_worker(
                value,
                worker_id="worker",
                task=contracts.RELATION_TASK,
                source_commit="a" * 40,
                request_identity="b" * 64,
            )


if __name__ == "__main__":
    unittest.main()
