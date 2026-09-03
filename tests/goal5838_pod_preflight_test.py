import argparse
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5838_pod_preflight.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5838_pod_preflight", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Goal5838 pod preflight")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5838PodPreflightTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = _load_module()

    def test_driver_parser_records_but_does_not_impose_a_floor(self):
        self.assertEqual(self.module._parse_driver_major("550.127.05"), 550)
        self.assertEqual(self.module._parse_driver_major("570.124.06"), 570)
        self.assertEqual(self.module._parse_driver_major("580.126.09"), 580)
        self.assertFalse(hasattr(self.module, "MINIMUM_DRIVER_MAJOR"))

    def test_driver_parser_rejects_non_driver_text(self):
        with self.assertRaises(ValueError):
            self.module._parse_driver_major("not-available")

    def test_gpu_parser_requires_complete_rows(self):
        rows = self.module._parse_gpu_rows(
            "NVIDIA L4, GPU-0123, 570.124.06, 8.9\n"
        )
        self.assertEqual(
            rows,
            [
                {
                    "name": "NVIDIA L4",
                    "uuid": "GPU-0123",
                    "driver_version": "570.124.06",
                    "compute_capability": "8.9",
                }
            ],
        )
        with self.assertRaises(ValueError):
            self.module._parse_gpu_rows("NVIDIA L4, GPU-0123, 570.124.06\n")

    def test_optix_version_parser_is_exact(self):
        with tempfile.TemporaryDirectory() as temporary:
            header = Path(temporary) / "optix.h"
            header.write_text("#define OPTIX_VERSION 90000\n", encoding="utf-8")
            self.assertEqual(self.module._parse_optix_version(header), 90000)
        self.assertEqual(self.module._optix_sdk_number("7.7.0"), 70700)
        self.assertEqual(self.module._optix_sdk_number("8.0.0"), 80000)
        self.assertEqual(self.module._optix_sdk_number("9.0.0"), 90000)
        self.assertEqual(self.module._optix_sdk_number("9.1.0"), 90100)
        with self.assertRaises(ValueError):
            self.module._optix_sdk_number("08.0.0")

    def test_repository_paths_cannot_receive_preflight_receipt(self):
        with self.assertRaises(ValueError):
            self.module._external_path(ROOT / "forbidden.json")

    def test_command_plan_binds_exact_commit_and_detected_capability(self):
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            artifacts = self.module._artifact_paths(temp / "evidence")
            commit = "a" * 40
            plan = self.module._command_plan(
                python=Path("/venv/bin/python"),
                cuda_prefix=Path("/usr/local/cuda"),
                optix_prefix=Path("/tmp/optix-dev-v8.0.0"),
                host_compiler=Path("/usr/bin/g++-12"),
                optix_sdk="8.0.0",
                compute_capability="8.9",
                expected_commit=commit,
                artifacts=artifacts,
            )
        build = plan["build"]["argv"]
        run = plan["run"]["argv"]
        verify = plan["verify"]["argv"]
        self.assertIn(commit, build)
        self.assertIn(commit, run)
        self.assertIn("8.9", build)
        self.assertIn("8.9", run)
        self.assertIn("8.0.0", build)
        self.assertIn("8.0.0", run)
        self.assertIn("CUDA_VISIBLE_DEVICES=0", build)
        self.assertIn("CUDA_VISIBLE_DEVICES=0", run)
        self.assertIn("PYTHONPATH=src:.", build)
        self.assertNotIn("PYTHONPATH=src:.", verify)

    def test_status_vocabulary_never_calls_readiness_failure_scientific(self):
        self.assertIn("NOT_SCIENTIFIC_FAILURE", self.module.REPAIR_STATUS)
        self.assertIn("NO_GPU_EXECUTION_CLAIM", self.module.PASS_STATUS)

    def test_argument_namespace_shape_for_run_preflight_is_explicit(self):
        namespace = argparse.Namespace(
            cuda_prefix=Path("/cuda"),
            optix_prefix=Path("/optix"),
            expected_optix_sdk="8.0.0",
            expected_commit="b" * 40,
            compute_capability=None,
            host_compiler=None,
            artifact_dir=Path("/tmp/goal5838-artifacts"),
            output=Path("/tmp/goal5838-preflight.json"),
        )
        self.assertEqual(namespace.expected_optix_sdk, "8.0.0")
        self.assertEqual(len(namespace.expected_commit), 40)

    def test_runtime_probe_is_zero_launch_and_version_neutral(self):
        source = self.module.OPTIX_RUNTIME_ABI_PROBE_SOURCE
        self.assertIn("optixInit()", source)
        self.assertNotIn("optixLaunch", source)
        self.assertNotIn("OPTIX_VERSION", source)

    def test_r550_with_compatible_optix8_is_ready(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cuda = root / "cuda"
            optix = root / "optix"
            for directory in (
                cuda / "bin",
                cuda / "include",
                cuda / "lib64",
                optix / "include",
            ):
                directory.mkdir(parents=True, exist_ok=True)
            nvcc = cuda / "bin" / "nvcc"
            nvcc.write_text("#!/bin/sh\n", encoding="ascii")
            nvcc.chmod(0o755)
            for name in self.module.CUDA_HEADERS:
                (cuda / "include" / name).write_text("/* cuda */\n", encoding="ascii")
            (cuda / "lib64" / "libnvrtc.so").write_bytes(b"nvrtc")
            for name in self.module.OPTIX_HEADERS:
                body = "#define OPTIX_VERSION 80000\n" if name == "optix.h" else ""
                (optix / "include" / name).write_text(body, encoding="ascii")

            commit = "c" * 40
            args = argparse.Namespace(
                cuda_prefix=cuda,
                optix_prefix=optix,
                expected_optix_sdk="8.0.0",
                expected_commit=commit,
                compute_capability=None,
                host_compiler=None,
                artifact_dir=root / "artifacts",
                output=root / "preflight.json",
            )

            def fake_git(*arguments):
                if arguments == ("rev-parse", "HEAD"):
                    output = commit
                else:
                    output = ""
                return {
                    "command": ["git", *arguments],
                    "command_display": "git",
                    "returncode": 0,
                    "output_tail": output,
                }

            def fake_capture(command, **_kwargs):
                if "nvidia-smi" in command[0]:
                    output = "NVIDIA RTX 4000 Ada, GPU-test, 550.127.05, 8.9\n"
                else:
                    output = "pass\n"
                return {
                    "command": command,
                    "command_display": "synthetic",
                    "returncode": 0,
                    "output_tail": output,
                }

            abi = {
                "source_sha256": "a" * 64,
                "compile_command_template": [],
                "compile_returncode": 0,
                "compiler_output_sha256": "b" * 64,
                "executable_bytes": 1,
                "executable_sha256": "c" * 64,
                "runtime_returncode": 0,
                "runtime_output": "optixInit_result=0",
                "passed": True,
                "optix_launch_count": 0,
            }
            with (
                patch.object(self.module, "_git_probe", side_effect=fake_git),
                patch.object(self.module, "_capture", side_effect=fake_capture),
                patch.object(
                    self.module,
                    "_discover_host_compiler",
                    return_value=Path("/usr/bin/g++"),
                ),
                patch.object(
                    self.module,
                    "probe_optix_runtime_abi",
                    return_value=abi,
                ),
                patch.object(
                    self.module,
                    "_package_version",
                    side_effect=self.module.EXPECTED_PACKAGE_VERSIONS.get,
                ),
                patch.object(
                    self.module.shutil,
                    "which",
                    side_effect=lambda name: f"/usr/bin/{name}",
                ),
            ):
                result = self.module.run_preflight(args)

        self.assertTrue(result["ready_for_gpu_exam"])
        self.assertEqual(result["status"], self.module.PASS_STATUS)
        self.assertEqual(result["gpu"]["driver_version"], "550.127.05")
        self.assertEqual(result["expected_optix_sdk"], "8.0.0")
        self.assertNotIn("minimum_driver_major", result)

    def test_preflight_receipt_cannot_overwrite_exam_artifact(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            artifacts = self.module._artifact_paths(directory)
            with self.assertRaisesRegex(ValueError, "must differ"):
                self.module._require_distinct_receipt(
                    directory / "goal5838_gpu_exam.json", artifacts
                )


if __name__ == "__main__":
    unittest.main()
