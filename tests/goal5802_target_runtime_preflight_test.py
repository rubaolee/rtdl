from __future__ import annotations

import copy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from experiments.goal5802_premeasurement import controller
from experiments.goal5802_premeasurement.runtime_manifest import (
    digest,
    direct_nvrtc_identity_stdout_bytes,
    validate_direct_nvrtc_identity_document,
    validate_target_observation_receipt,
)


def _file(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    return {
        "path": str(path.resolve()), "path_kind": "REGULAR_FILE",
        "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _command(command: list[str], stdout: str) -> dict[str, object]:
    return {
        "command": command, "exit_code": 0,
        "stdout_utf8": stdout,
        "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
        "stderr_utf8": "", "stderr_sha256": hashlib.sha256(b"").hexdigest(),
    }


def _reseal(value: dict[str, object], field: str) -> None:
    value.pop(field, None)
    value[field] = digest(value)


class Goal5802TargetRuntimePreflightTest(unittest.TestCase):
    def test_target_v2_reconstructs_raw_commands_and_rejects_hostile_fields(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            nvidia_smi = root / "nvidia-smi"
            nvcc = root / "nvcc"
            nvidia_smi.write_bytes(b"smi")
            nvcc.write_bytes(b"nvcc")
            files = {"nvidia_smi": _file(nvidia_smi), "nvcc": _file(nvcc)}
            smi_command = [
                str(nvidia_smi),
                "--query-gpu=name,compute_cap,driver_version",
                "--format=csv,noheader,nounits",
            ]
            nvcc_command = [str(nvcc), "--version"]
            value: dict[str, object] = {
                "schema": "rtdl.goal5802.target_observation.v2",
                "status": "PASS__UNTIMED_EXACT_TARGET_OBSERVATION",
                "tools": copy.deepcopy(files),
                "command_receipts": {
                    "nvidia_smi": _command(
                        smi_command, "NVIDIA RTX Synthetic, 8.9, 555.42\n"),
                    "nvcc": _command(
                        nvcc_command,
                        "nvcc: NVIDIA compiler\nCuda compilation tools, release 12.6\n"),
                },
                "gpu_name": "NVIDIA RTX Synthetic",
                "compute_capability": "8.9",
                "driver_version": "555.42",
                "cuda_driver_version": "12060",
                "cuda_toolkit_version": "Cuda compilation tools, release 12.6",
                "optix_version": "9.0.0",
                "loader_environment": {
                    "LD_LIBRARY_PATH": None, "LD_PRELOAD": None},
                "clock_read_count": 0,
                "registered_performance_timing_count": 0,
                "gpu_kernel_launch_count": 0,
                "formal_worker_count": 0,
            }
            _reseal(value, "observation_sha256")
            projection = validate_target_observation_receipt(
                value, files, require_current_loader_environment=False)
            self.assertEqual(projection["compute_capability"], "8.9")

            for mutate in (
                    lambda row: row.__setitem__("gpu_name", "different"),
                    lambda row: row["loader_environment"].__setitem__(
                        "LD_LIBRARY_PATH", "relative"),
                    lambda row: row["loader_environment"].__setitem__(
                        "LD_PRELOAD", ""),
                    lambda row: row.__setitem__("formal_worker_count", False),
                    lambda row: row["tools"]["nvcc"].__setitem__(
                        "sha256", "0" * 64),
            ):
                hostile = copy.deepcopy(value)
                mutate(hostile)
                _reseal(hostile, "observation_sha256")
                with self.assertRaises(RuntimeError):
                    validate_target_observation_receipt(
                        hostile, files,
                        require_current_loader_environment=False)

    def test_direct_v2_binds_both_dsos_fixed_source_and_exact_stdout(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            library = root / "libnvrtc.so.12"
            builtins = root / "libnvrtc-builtins.so.12"
            library.write_bytes(b"nvrtc-library")
            builtins.write_bytes(b"nvrtc-builtins")
            files = {
                "nvrtc_library": {
                    "path": str(library), "bytes": library.stat().st_size,
                    "sha256": hashlib.sha256(library.read_bytes()).hexdigest()},
                "nvrtc_builtins": {
                    "path": str(builtins), "bytes": builtins.stat().st_size,
                    "sha256": hashlib.sha256(builtins.read_bytes()).hexdigest()},
            }
            source = (
                'extern "C" __global__ void goal5802_nvrtc_identity_probe() {}\n')
            value: dict[str, object] = {
                "schema": "rtdl.goal5802.direct_loaded_nvrtc_identity.v2",
                "status": "PASS__UNTIMED_NO_GPU",
                "discovery": (
                    "MINIMAL_NVRTC_COMPILE_THEN_DLADDR_NVRTCVERSION_AND_"
                    "PROC_SELF_MAPS_UNIQUE_BUILTINS_REALPATH_OPEN_NOFOLLOW_FSTAT"),
                "loaded_library_path": str(library),
                "loaded_library_bytes": library.stat().st_size,
                "loaded_library_sha256": files["nvrtc_library"]["sha256"],
                "loaded_builtins_path": str(builtins),
                "loaded_builtins_bytes": builtins.stat().st_size,
                "loaded_builtins_sha256": files["nvrtc_builtins"]["sha256"],
                "nvrtc_version": {"major": 12, "minor": 6},
                "nvrtc_compile_kat": {
                    "source_utf8": source,
                    "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                    "compile_options": ["--std=c++11"],
                    "product_bytes": 128,
                    "product_sha256": "a" * 64,
                    "compile_success": True, "program_destroyed": True,
                },
                "clock_read_count": 0,
                "registered_performance_timing_count": 0,
                "gpu_kernel_launch_count": 0,
                "formal_worker_count": 0,
            }
            validate_direct_nvrtc_identity_document(value, files)
            stdout = direct_nvrtc_identity_stdout_bytes(value)
            self.assertEqual(json.loads(stdout), value)
            self.assertTrue(stdout.endswith(b"\n"))

            for path, replacement in (
                    (("loaded_builtins_sha256",), "0" * 64),
                    (("nvrtc_version", "major"), 0),
                    (("nvrtc_compile_kat", "source_utf8"), "alternate\n"),
                    (("nvrtc_compile_kat", "product_sha256"), "A" * 64),
                    (("gpu_kernel_launch_count",), False),
            ):
                hostile = copy.deepcopy(value)
                cursor = hostile
                for key in path[:-1]:
                    cursor = cursor[key]
                cursor[path[-1]] = replacement
                with self.assertRaises(RuntimeError):
                    validate_direct_nvrtc_identity_document(hostile, files)

    def test_preflight_failure_is_sealed_and_preserves_zero_worker_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            runtime = root / "runtime.json"
            runtime.write_text("{}", encoding="utf-8")
            environment = {
                "PATH": str(root), "LD_LIBRARY_PATH": None,
                "LD_PRELOAD": None}
            cases = (
                ("TARGET_REOBSERVATION_VALIDATE", "target_process.json",
                 '{"changed_gpu_field":true}\n', "live target differs"),
                ("DIRECT_NVRTC_IDENTITY_VALIDATE", "direct_process.json",
                 '{"changed_loaded_builtins":true}\n',
                 "loaded Direct DSO differs"),
            )
            for ordinal, (stage, name, payload, message) in enumerate(cases):
                with self.subTest(stage=stage):
                    output = root / f"output_{ordinal}"
                    output.mkdir()

                    def fail(**kwargs):
                        kwargs["stage_state"]["stage"] = stage
                        (kwargs["preflight_root"] / name).write_text(
                            payload, encoding="utf-8")
                        raise RuntimeError(message)

                    with mock.patch.object(
                            controller, "_formal_runtime_preflight_impl",
                            side_effect=fail):
                        with self.assertRaises(RuntimeError):
                            controller._formal_runtime_preflight(
                                root=root, output_directory=output,
                                host_code_snapshot_root=root,
                                runtime_path=runtime, runtime={},
                                environment=environment, timeout_seconds=1)
                    receipt = json.loads((output / (
                        "runtime_preflight/failure_receipt.json")).read_text())
                    unsigned = dict(receipt)
                    seal = unsigned.pop("failure_sha256")
                    self.assertEqual(seal, digest(unsigned))
                    self.assertEqual(receipt["failed_stage"], stage)
                    self.assertEqual(receipt["formal_worker_count"], 0)
                    self.assertIs(type(receipt["formal_worker_count"]), int)
                    self.assertEqual(
                        receipt["registered_performance_timing_count"], 0)
                    self.assertEqual(
                        [row["name"] for row in receipt[
                            "preserved_preflight_payloads"]], [name])

    def test_controller_runs_runtime_preflight_before_first_worker_loop(self):
        source = Path(controller.__file__).read_text(encoding="utf-8")
        call = source.index("runtime_preflight = _formal_runtime_preflight(")
        comparative = source.index('for row in freeze["schedule"]:', call)
        build = source.index(
            'for row in freeze["build_cold_absolute_schedule"]:', call)
        self.assertLess(call, comparative)
        self.assertLess(call, build)
        self.assertIn('"PATH", "LD_LIBRARY_PATH", "LD_PRELOAD"', source)
        self.assertIn(
            'str(clean_python), "-I", "-S", "-B", "-P", "-c", bootstrap,',
            source)
        self.assertIn("pyoptix_initializer.parent.parent != site_packages", source)
        child = (Path(controller.__file__).parents[2] / "scripts" /
                 "goal5802_capture_rtdsl_package_import_untimed.py").read_text(
                     encoding="utf-8")
        self.assertIn("observed_count, observed_tree = _package_identity(root)",
                      child)

    def test_exact_success_receipt_and_live_pipe_block_direct_or_stale_entry(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            runtime_sha = "1" * 64

            def write_document(path: Path, value: object) -> None:
                path.write_bytes(
                    json.dumps(value, indent=2, sort_keys=True).encode() + b"\n")

            def plain_file(path: Path) -> dict[str, object]:
                payload = path.read_bytes()
                return {
                    "path": str(path.resolve()), "bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                }

            def process(document: object) -> dict[str, object]:
                stdout = json.dumps(document, sort_keys=True) + "\n"
                return {
                    "command": ["/synthetic/preflight"], "exit_code": 0,
                    "stdout_utf8": stdout,
                    "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
                    "stderr_utf8": "",
                    "stderr_sha256": hashlib.sha256(b"").hexdigest(),
                }

            target_document: dict[str, object] = {}
            target_document["observation_sha256"] = digest(target_document)
            direct_document: dict[str, object] = {"exact": "direct"}
            product = root / "fresh.ptx"
            product.write_bytes(b".version 8.7\n.target sm_89\n")
            python_document: dict[str, object] = {
                "status": "PASS", "pid": 17,
                "product": {"sha256": plain_file(product)["sha256"]},
            }
            python_document["receipt_sha256"] = digest(python_document)
            python_summary = {
                "status": python_document["status"],
                "pid": python_document["pid"],
                "product_sha256": python_document["product"]["sha256"],
                "receipt_sha256": python_document["receipt_sha256"],
            }
            package_document: dict[str, object] = {
                "schema": "rtdl.goal5802.rtdsl_package_import_preflight.v1",
                "status": "PASS__CLEAN_PYTHON_IMPORTED_SEALED_RTDSL_PACKAGE",
            }
            package_document["receipt_sha256"] = digest(package_document)
            rows = {
                "target": (target_document, process(target_document)),
                "direct": (direct_document, process(direct_document)),
                "python": (python_document, process(python_summary)),
                "package": (package_document, process(package_document)),
            }
            for name, (document, process_row) in rows.items():
                write_document(root / f"{name}.json", document)
                write_document(root / f"{name}_process.json", process_row)

            preflight: dict[str, object] = {
                "schema": "rtdl.goal5802.formal_runtime_preflight.v1",
                "status": (
                    "PASS__LIVE_TARGET_AND_CROSS_ARM_NVRTC_BEFORE_WORKER_ZERO"),
                "runtime_manifest_file_sha256": runtime_sha,
                "loader_environment": {
                    "PATH": str(root), "LD_LIBRARY_PATH": None,
                    "LD_PRELOAD": None},
                "target_reobservation": {
                    "process": rows["target"][1],
                    "process_evidence": plain_file(root / "target_process.json"),
                    "receipt": plain_file(root / "target.json"),
                    "document": target_document,
                    "all_frozen_fields_equal": True,
                },
                "direct_nvrtc_compile_identity": {
                    "process": rows["direct"][1],
                    "process_evidence": plain_file(root / "direct_process.json"),
                    "document": direct_document,
                    "prepare_document_byte_projection_equal": True,
                },
                "python_nvrtc_compile_identity": {
                    "process": rows["python"][1],
                    "process_evidence": plain_file(root / "python_process.json"),
                    "receipt": plain_file(root / "python.json"),
                    "document": python_document,
                    "product": plain_file(product),
                    "matched_ptx_byte_identical": True,
                },
                "rtdsl_package_import_identity": {
                    "process": rows["package"][1],
                    "process_evidence": plain_file(
                        root / "package_process.json"),
                    "document": package_document,
                    "all_modules_match_sealed_package": True,
                },
                "cross_arm_libnvrtc_builtins_version_equal": True,
                "clock_read_count": 0,
                "registered_performance_timing_count": 0,
                "gpu_kernel_launch_count": 0,
                "formal_worker_count": 0,
            }
            preflight["preflight_sha256"] = digest(preflight)
            receipt_path = root / "receipt.json"
            write_document(receipt_path, preflight)
            environment = {
                controller.PREFLIGHT_PATH_ENV: str(receipt_path),
                controller.PREFLIGHT_FILE_SHA_ENV: hashlib.sha256(
                    receipt_path.read_bytes()).hexdigest(),
                controller.PREFLIGHT_SELF_SHA_ENV: preflight["preflight_sha256"],
                "GOAL5802_FORMAL_CONTROLLER_PID": str(os.getppid()),
            }
            accepted = controller.validate_formal_worker_preflight_gate(
                runtime_manifest_sha256=runtime_sha, environment=environment)
            self.assertEqual(accepted["path"], str(receipt_path))

            for key in (
                    controller.PREFLIGHT_PATH_ENV,
                    controller.PREFLIGHT_FILE_SHA_ENV,
                    controller.PREFLIGHT_SELF_SHA_ENV):
                hostile = dict(environment)
                hostile.pop(key)
                with self.subTest(absent=key), self.assertRaises(RuntimeError):
                    controller.validate_formal_worker_preflight_gate(
                        runtime_manifest_sha256=runtime_sha,
                        environment=hostile)
            with self.assertRaises(RuntimeError):
                controller.validate_formal_worker_preflight_gate(
                    runtime_manifest_sha256="2" * 64,
                    environment=environment)

            for mutate in (
                    lambda row: row.__setitem__("formal_worker_count", 1),
                    lambda row: row.__setitem__(
                        "schema", "rtdl.goal5802.formal_runtime_preflight.v0")):
                hostile_document = copy.deepcopy(preflight)
                mutate(hostile_document)
                hostile_document.pop("preflight_sha256", None)
                hostile_document["preflight_sha256"] = digest(hostile_document)
                write_document(receipt_path, hostile_document)
                hostile_environment = dict(environment)
                hostile_environment[controller.PREFLIGHT_FILE_SHA_ENV] = \
                    hashlib.sha256(receipt_path.read_bytes()).hexdigest()
                hostile_environment[controller.PREFLIGHT_SELF_SHA_ENV] = \
                    hostile_document["preflight_sha256"]
                with self.assertRaises(RuntimeError):
                    controller.validate_formal_worker_preflight_gate(
                        runtime_manifest_sha256=runtime_sha,
                        environment=hostile_environment)
            write_document(receipt_path, preflight)

            capability_environment = {
                **environment,
                "GOAL5802_RUNTIME_MANIFEST_SHA256": runtime_sha,
            }
            capability = {
                "schema": controller.LIVE_CAPABILITY_SCHEMA,
                "controller_pid": os.getppid(),
                "worker_id": "G5802_HOSTILE_DIRECT_SPAWN",
                "runtime_manifest_sha256": runtime_sha,
                "preflight_receipt_file_sha256": environment[
                    controller.PREFLIGHT_FILE_SHA_ENV],
                "preflight_sha256": environment[
                    controller.PREFLIGHT_SELF_SHA_ENV],
                "nonce": "a" * 64,
            }
            frame = controller.canonical(capability) + b"\n"
            trace = controller.consume_formal_worker_live_capability(
                worker_id=capability["worker_id"],
                runtime_manifest_sha256=runtime_sha,
                environment=capability_environment,
                stream=io.BytesIO(frame))
            self.assertEqual(trace, hashlib.sha256(frame).hexdigest())
            for hostile_frame in (
                    b"", frame.replace(b"G5802_HOSTILE", b"G5802_STALE__"),
                    frame + frame):
                with self.assertRaises(RuntimeError):
                    controller.consume_formal_worker_live_capability(
                        worker_id=capability["worker_id"],
                        runtime_manifest_sha256=runtime_sha,
                        environment=capability_environment,
                        stream=io.BytesIO(hostile_frame))

    def test_all_formal_entrypoints_consume_fresh_capability_before_work(self):
        controller_source = Path(controller.__file__).read_text(encoding="utf-8")
        spawn = controller_source.index("process = subprocess.Popen(")
        nonce = controller_source.index("nonce=secrets.token_hex(32)", spawn)
        send = controller_source.index("process.communicate(", nonce)
        self.assertLess(spawn, nonce)
        self.assertLess(nonce, send)
        self.assertIn("stdin=subprocess.PIPE", controller_source[spawn:send])

        python_source = (Path(controller.__file__).parent / "python_worker.py").read_text()
        python_main = python_source.index("def main()")
        self.assertLess(
            python_source.index(
                "consume_formal_worker_live_capability(", python_main),
            python_source.index("preload_pyoptix_runtime()", python_main))
        build_source = (Path(controller.__file__).parent / "build_cold_worker.py").read_text()
        build_main = build_source.index("def main()")
        self.assertLess(
            build_source.index(
                "consume_formal_worker_live_capability(", build_main),
            build_source.index(
                'if args.arm.startswith("B_NVIDIA_PYOPTIX")', build_main))
        direct_source = (Path(controller.__file__).parent /
                         "direct_scalar_worker.cpp").read_text()
        self.assertEqual(
            direct_source.count("consume_live_controller_capability("), 2)
        self.assertIn("std::getline(std::cin, frame)", direct_source)
        self.assertIn("formal Direct live controller capability is absent",
                      direct_source)

    def test_direct_spawn_with_copied_receipt_environment_but_no_pipe_fails(self):
        runtime_sha = "1" * 64
        worker_id = "G5802_HOSTILE_DIRECT_SPAWN"
        environment = {
            **os.environ,
            "GOAL5802_FORMAL_CONTROLLER_PID": str(os.getpid()),
            "GOAL5802_RUNTIME_PREFLIGHT_RECEIPT_FILE_SHA256": "2" * 64,
            "GOAL5802_RUNTIME_PREFLIGHT_SHA256": "3" * 64,
            "PYTHONPATH": str(Path.cwd()),
        }
        program = (
            "from experiments.goal5802_premeasurement.controller import "
            "consume_formal_worker_live_capability as consume;"
            f"consume(worker_id={worker_id!r},"
            f"runtime_manifest_sha256={runtime_sha!r});print('ACCEPT')")
        direct = subprocess.run(
            [sys.executable, "-P", "-c", program], cwd=Path.cwd(),
            env=environment, input=b"", capture_output=True, check=False)
        self.assertNotEqual(direct.returncode, 0)
        self.assertNotIn(b"ACCEPT", direct.stdout)

        capability = {
            "schema": controller.LIVE_CAPABILITY_SCHEMA,
            "controller_pid": os.getpid(), "worker_id": worker_id,
            "runtime_manifest_sha256": runtime_sha,
            "preflight_receipt_file_sha256": "2" * 64,
            "preflight_sha256": "3" * 64, "nonce": "4" * 64,
        }
        through_fresh_pipe = subprocess.run(
            [sys.executable, "-P", "-c", program], cwd=Path.cwd(),
            env=environment, input=controller.canonical(capability) + b"\n",
            capture_output=True, check=False)
        self.assertEqual(through_fresh_pipe.returncode, 0)
        self.assertEqual(through_fresh_pipe.stdout.splitlines(), [b"ACCEPT"])


if __name__ == "__main__":
    unittest.main()
