import argparse
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5838_pod_preflight.py"
UNKNOWN_POD_PLAN = (
    ROOT
    / "history"
    / "internal_docs"
    / "goal5838_generic_core_exam_20260902"
    / "UNKNOWN_POD_COMPLETION_PLAN.md"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("goal5838_pod_preflight", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Goal5838 pod preflight")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _compiler_environment():
    return {
        "CUDA_VISIBLE_DEVICES": "0",
        "LD_LIBRARY_PATH": "/cuda/lib64",
        "PATH": "/cuda/bin:/usr/bin",
        "NUMBA_CUDA_NVVM": "/cuda/nvvm/lib64/libnvvm.so",
        "NUMBA_CUDA_LIBDEVICE": "/cuda/nvvm/libdevice/libdevice.10.bc",
        "CUDA_HOME": "/cuda",
        "CUDA_PATH": "/cuda",
        "RTDL_V4_CUDA_PREFIX": "/cuda",
        "RTDL_V4_OPTIX_PREFIX": "/optix",
        "RTDL_V4_NVRTC_LIBRARY": "/cuda/lib64/libnvrtc.so.12",
        "PYTHONPATH": "src:.",
    }


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

    def test_compute_capability_minor_zero_is_valid(self):
        self.assertEqual(self.module._parse_compute_capability("9.0"), (9, 0))
        self.assertEqual(
            self.module._normalize_compute_capability_row([9, 0]), (9, 0)
        )
        with self.assertRaises(ValueError):
            self.module._normalize_compute_capability_row([0, 9])

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
                compiler_environment=_compiler_environment(),
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
        self.assertIn("NUMBA_CUDA_NVVM=/cuda/nvvm/lib64/libnvvm.so", run)
        self.assertIn(
            "NUMBA_CUDA_LIBDEVICE=/cuda/nvvm/libdevice/libdevice.10.bc",
            run,
        )
        self.assertIn("RTDL_V4_NVRTC_LIBRARY=/cuda/lib64/libnvrtc.so.12", run)
        for name in self.module.CLEARED_AMBIENT_ENV:
            occurrences = [
                index
                for index, item in enumerate(run[:-1])
                if item == "-u" and run[index + 1] == name
            ]
            self.assertEqual(len(occurrences), 1, name)
        self.assertIn("--nvrtc-library", build)
        self.assertIn("/cuda/lib64/libnvrtc.so.12", build)
        self.assertNotIn("PYTHONPATH=src:.", verify)

    def test_cuda_compiler_inputs_and_clean_environment_are_exact(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cuda = root / "cuda"
            optix = root / "optix"
            for directory in (
                cuda / "bin",
                cuda / "lib64",
                cuda / "nvvm" / "lib64",
                cuda / "nvvm" / "libdevice",
                optix,
            ):
                directory.mkdir(parents=True, exist_ok=True)
            (cuda / "lib64" / "libnvrtc.so.12").write_bytes(b"nvrtc")
            (cuda / "nvvm" / "lib64" / "libnvvm.so").write_bytes(b"nvvm")
            (cuda / "nvvm" / "libdevice" / "libdevice.10.bc").write_bytes(
                b"libdevice"
            )
            files = self.module.resolve_cuda_compiler_files(cuda)
            environment, identity = self.module.configured_cuda_environment(
                cuda,
                optix,
                files,
                base={
                    "PATH": "/usr/bin",
                    "LD_LIBRARY_PATH": "/old/lib",
                    "RTDL_V4_FORMAL_LEAF_CACHE": "/forbidden/cache",
                    "NUMBA_ENABLE_CUDASIM": "1",
                    "RTDL_V4_NVRTC_LIBRARY": "/wrong/libnvrtc.so",
                },
            )
        self.assertEqual(environment["CUDA_VISIBLE_DEVICES"], "0")
        self.assertEqual(environment["NUMBA_CUDA_NVVM"], str(files["nvvm_library"]))
        self.assertEqual(
            environment["NUMBA_CUDA_LIBDEVICE"], str(files["libdevice"])
        )
        self.assertNotIn("RTDL_V4_FORMAL_LEAF_CACHE", environment)
        self.assertNotIn("NUMBA_ENABLE_CUDASIM", environment)
        self.assertEqual(
            environment["RTDL_V4_NVRTC_LIBRARY"],
            str(files["nvrtc_library"]),
        )
        self.assertTrue(identity["formal_numba_cache_disabled"])
        self.assertRegex(identity["environment_sha256"], r"^[0-9a-f]{64}$")

    def test_callback_compile_receipt_requires_front_door_and_zero_launch(self):
        hashes = {
            name: str(index) * 64
            for index, name in enumerate(
                (
                    "identity_sha256",
                    "provider_descriptor_sha256",
                    "provider_projection_sha256",
                    "plan_sha256",
                    "target_sha256",
                    "executable_sha256",
                    "provider_artifact_sha256",
                    "generated_artifact_sha256",
                ),
                start=1,
            )
        }
        receipt = {
            "schema": "rtdl.goal5838.selected_callback_compile_probe.v1",
            "classification": "prospective_selected_extension",
            "provider_id": "rtdl.optix.builtin_sphere_any_hit_count",
            "callback_roles": list(self.module.CALLBACK_ROLES),
            "plan_sha256": hashes["plan_sha256"],
            "provider_descriptor_sha256": hashes[
                "provider_descriptor_sha256"
            ],
            "provider_projection_sha256": hashes[
                "provider_projection_sha256"
            ],
            "executable_identity": hashes,
            "optix_sdk": "8.0.0",
            "compute_capability": [8, 9],
            "compiled_through_generic_family_front_door": True,
            "native_prepare_called": False,
            "native_library_loaded": False,
            "gpu_execution_performed": False,
            "optix_launch_count": 0,
        }
        self.assertTrue(
            self.module._callback_probe_receipt_passes(
                receipt, optix_sdk="8.0.0", compute_capability=(8, 9)
            )
        )
        receipt["native_prepare_called"] = True
        self.assertFalse(
            self.module._callback_probe_receipt_passes(
                receipt, optix_sdk="8.0.0", compute_capability=(8, 9)
            )
        )

    def test_status_vocabulary_never_calls_readiness_failure_scientific(self):
        self.assertIn("NOT_SCIENTIFIC_FAILURE", self.module.REPAIR_STATUS)
        self.assertIn("NO_GPU_EXECUTION_CLAIM", self.module.PASS_STATUS)

    def test_unknown_pod_plan_assigns_software_adaptation_to_agent(self):
        text = " ".join(UNKNOWN_POD_PLAN.read_text(encoding="utf-8").split())
        self.assertIn("The owner supplies one reachable SSH command", text)
        self.assertIn("The RTDL agent owns discovery", text)
        self.assertIn("There is no R570 driver floor", text)
        self.assertIn("reject a pod merely because", text)
        self.assertIn("toolkit, compiler, Python version", text)
        self.assertIn("two true OptiX executions", text)

    def test_argument_namespace_shape_for_run_preflight_is_explicit(self):
        namespace = argparse.Namespace(
            cuda_prefix=Path("/cuda"),
            optix_prefix=Path("/optix"),
            expected_optix_sdk="8.0.0",
            expected_commit="b" * 40,
            compute_capability=None,
            host_compiler=None,
            nvrtc_library=None,
            nvvm_library=None,
            libdevice=None,
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
                cuda / "nvvm" / "lib64",
                cuda / "nvvm" / "libdevice",
                optix / "include",
            ):
                directory.mkdir(parents=True, exist_ok=True)
            nvcc = cuda / "bin" / "nvcc"
            nvcc.write_text("#!/bin/sh\n", encoding="ascii")
            nvcc.chmod(0o755)
            for name in self.module.CUDA_HEADERS:
                (cuda / "include" / name).write_text("/* cuda */\n", encoding="ascii")
            (cuda / "lib64" / "libnvrtc.so").write_bytes(b"nvrtc")
            (cuda / "nvvm" / "lib64" / "libnvvm.so").write_bytes(b"nvvm")
            (cuda / "nvvm" / "libdevice" / "libdevice.10.bc").write_bytes(
                b"libdevice"
            )
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
                nvrtc_library=None,
                nvvm_library=None,
                libdevice=None,
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
                    "_probe_selected_callback_compiler",
                    return_value={"passed": True, "optix_launch_count": 0},
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
