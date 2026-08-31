from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts import goal5813_home_loaded_capsule_ab_controller as controller


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Goal5813HomeLoadedCapsuleABControllerTest(unittest.TestCase):

    def test_fake_matrix_selects_and_verifies_each_exact_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            worker = root / "goal5810_worker.py"
            target = root / "target.json"
            worker.write_text("# exact fake worker\n", encoding="utf-8")
            target.write_text("{}\n", encoding="utf-8")
            arms: dict[str, tuple[Path, str]] = {}
            for name in controller.ARMS:
                source_root = root / name
                implementation = (
                    source_root / controller.IMPLEMENTATION_RELATIVE_PATH)
                implementation.parent.mkdir(parents=True)
                implementation.write_text(
                    f"# {name} implementation\n", encoding="utf-8")
                arms[name] = (source_root, _sha(implementation))

            output_root = root / "workers"
            output = output_root / "matrix.json"
            calls: list[tuple[str, str, str]] = []
            next_pid = 9000

            def fake_run(command: list[str], **kwargs: object) \
                    -> subprocess.CompletedProcess[str]:
                nonlocal next_pid
                self.assertEqual(command[command.index("--arm") + 1], "rtdl")
                first_app = command[command.index("--first-app") + 1]
                result_path = Path(command[command.index("--output") + 1])
                child_cwd = Path(str(kwargs["cwd"])).resolve(strict=True)
                arm_name = child_cwd.name
                source_root, implementation_sha = arms[arm_name]
                expected_pythonpath = os.pathsep.join((
                    str((source_root / "src").resolve(strict=True)),
                    str(source_root.resolve(strict=True)),
                ))
                environment = kwargs["env"]
                self.assertIsInstance(environment, dict)
                self.assertEqual(environment["PYTHONPATH"], expected_pythonpath)
                calls.append((first_app, arm_name, environment["PYTHONPATH"]))

                cursor = 1_000_000
                phases: dict[str, dict[str, int | float]] = {}
                arm_delta = 100 if arm_name == "predecessor" else 80
                for ordinal, phase in enumerate(controller.PHASES):
                    duration = arm_delta + ordinal + 1
                    phases[phase] = {
                        "ordinal": ordinal,
                        "start_perf_counter_ns": cursor,
                        "end_perf_counter_ns": cursor + duration,
                        "duration_ns": duration,
                        "duration_ms": duration / 1_000_000.0,
                    }
                    cursor += duration + 7
                body = {
                    "schema": "rtdl.goal5810.home_two_app_phase_diagnostic.v1",
                    "status": (
                        "COMPLETE__HOME_PASCAL_NONFORMAL_TWO_APP_PHASE_"
                        "DIAGNOSTIC"),
                    "process_pid": next_pid,
                    "cuda": {
                        "gpu_name": "NVIDIA GeForce GTX 1070",
                        "compute_capability": [6, 1],
                    },
                    "scope": {"arm": "RTDL_SHARED_RUNTIME_SESSION"},
                    "app_order": [
                        first_app,
                        "triangle" if first_app == "relation" else "relation",
                    ],
                    "applications": {
                        task: {
                            "exact_oracle_passed": True,
                            "device_status_ok": True,
                        }
                        for task in controller.FIRST_APPS
                    },
                    "phase_times_absolute": {
                        "phase_order": list(controller.PHASES),
                        "phases": phases,
                    },
                    "runtime": {
                        "implementation_module": {
                            "path": str((
                                source_root
                                / controller.IMPLEMENTATION_RELATIVE_PATH
                            ).resolve(strict=True)),
                            "bytes": (
                                source_root
                                / controller.IMPLEMENTATION_RELATIVE_PATH
                            ).stat().st_size,
                            "sha256": implementation_sha,
                        },
                    },
                    "formal_worker_count": 0,
                    "registered_performance_timing_count": 0,
                }
                sealed = {
                    **body,
                    "diagnostic_sha256": controller._digest(body),
                }
                result_path.write_bytes(controller._canonical(sealed) + b"\n")
                next_pid += 1
                return subprocess.CompletedProcess(
                    command, 0, stdout="fake pass\n", stderr="")

            argv = [
                str(controller.__file__),
                "--worker", str(worker),
                "--target-manifest", str(target),
                "--expected-target-manifest-sha256", _sha(target),
                "--predecessor-source-root", str(arms["predecessor"][0]),
                "--expected-predecessor-implementation-sha256",
                arms["predecessor"][1],
                "--successor-source-root", str(arms["successor"][0]),
                "--expected-successor-implementation-sha256",
                arms["successor"][1],
                "--output-root", str(output_root),
                "--output", str(output),
                "--blocks", "1",
            ]
            with mock.patch.object(sys, "argv", argv), mock.patch.object(
                    controller.subprocess, "run", side_effect=fake_run):
                self.assertEqual(controller.main(), 0)

            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["design"]["worker_count"], 8)
            self.assertEqual(len(result["journal"]), 8)
            self.assertEqual(
                [(first, arm) for first, arm, _path in calls],
                [
                    ("relation", "predecessor"),
                    ("relation", "successor"),
                    ("relation", "predecessor"),
                    ("relation", "successor"),
                    ("triangle", "predecessor"),
                    ("triangle", "successor"),
                    ("triangle", "predecessor"),
                    ("triangle", "successor"),
                ],
            )
            for condition in result["conditions"].values():
                self.assertEqual(condition["sample_count"], 2)
                self.assertEqual(
                    set(condition["phase_median_ns"]),
                    set(controller.PHASES))
                self.assertEqual(
                    set(condition["continuous_median_ns"]),
                    {
                        "input_admission_start_to_second_exact_output",
                        "first_session_admission_start_to_second_exact_output",
                        "first_app_prepare_start_to_second_exact_output",
                    },
                )
            self.assertFalse(result["scope"]["claim_authorized"])
            self.assertFalse(
                result["scope"]["threshold_or_pass_fail_gate_present"])
            self.assertEqual(result["registered_performance_timing_count"], 0)

    def test_source_arm_hash_mismatch_fails_before_workers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_root = Path(temporary)
            implementation = (
                source_root / controller.IMPLEMENTATION_RELATIVE_PATH)
            implementation.parent.mkdir(parents=True)
            implementation.write_text("# implementation\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "sha256_differs"):
                controller._admit_source_arm(
                    name="predecessor", root=source_root,
                    expected_implementation_sha256="0" * 64)


if __name__ == "__main__":
    unittest.main()
