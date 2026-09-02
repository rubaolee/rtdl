import copy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import scripts.build_v4_optix_native_snapshot as native_builder
from scripts.build_v4_optix_native_snapshot import (
    REQUIRED_SYMBOLS,
    _build_input_id,
    _compute_capability,
    _header_inventory,
    _optix_sdk_number,
    _optix_version,
    _source_inventory,
    _validate_output_paths,
)
from scripts.successor_linear_rtccd_owner_grouped_pod_runner import (
    _parse_compute_capability,
    _parse_scale,
    _validate_native_build_manifest,
    _validated_include_from_prefix,
    _validate_result_paths,
    _workloads,
)
from scripts.successor_owner_grouped_pod_preflight import (
    _OPTIX_RUNTIME_ABI_PROBE_SOURCE,
    _PREFLIGHT_SCHEMA,
    configured_runtime_environment,
    resolve_cuda_runtime_files,
)


ROOT = Path(__file__).resolve().parents[1]


class SuccessorOwnerGroupedGpuToolingTest(unittest.TestCase):
    def test_successor_entrypoints_bootstrap_repo_imports(self):
        environment = dict(os.environ)
        environment.pop("PYTHONPATH", None)
        for relative_path in (
            "case_studies/linear_rtccd_owner_grouped/run_local_validation.py",
            "scripts/successor_owner_grouped_pod_preflight.py",
            "scripts/successor_linear_rtccd_owner_grouped_pod_runner.py",
        ):
            completed = subprocess.run(
                [sys.executable, relative_path, "--help"],
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(
                completed.returncode,
                0,
                msg=f"{relative_path}: {completed.stdout}{completed.stderr}",
            )

    def test_builder_parses_exact_target_and_optix_version(self):
        self.assertEqual(_compute_capability("8.9"), (8, 9))
        self.assertEqual(_parse_compute_capability("8.9"), (8, 9))
        self.assertEqual(_optix_sdk_number("9.0.0"), 90000)
        with self.assertRaises(ValueError):
            _compute_capability("sm_89")
        with self.assertRaises(ValueError):
            _parse_compute_capability("8.9.0")
        with self.assertRaises(ValueError):
            _optix_sdk_number("9.0")
        with tempfile.TemporaryDirectory() as directory:
            header = Path(directory) / "optix.h"
            header.write_text(
                "#pragma once\n#define OPTIX_VERSION 90000\n",
                encoding="utf-8")
            self.assertEqual(_optix_version(header), 90000)

    def test_builder_observes_exactly_one_gpu_and_its_compute_target(self):
        identity = "NVIDIA L4, GPU-test, 580.1, 8.9"
        with patch.object(native_builder, "_capture", return_value=identity):
            self.assertEqual(native_builder._gpu_identity(), (identity, (8, 9)))
        with patch.object(
                native_builder, "_capture", return_value=identity + "\n" + identity):
            with self.assertRaisesRegex(RuntimeError, "exactly one"):
                native_builder._gpu_identity()

    def test_evidence_paths_must_be_distinct_and_non_nested(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _validate_output_paths(
                root / "native.so", root / "manifest.json", root / "build.log")
            _validate_result_paths(root / "result.json", root / "artifacts")
            with self.assertRaises(ValueError):
                _validate_output_paths(
                    root / "same", root / "same", root / "build.log")
            with self.assertRaises(ValueError):
                _validate_output_paths(
                    root / "native", root / "native/manifest.json",
                    root / "build.log")
            with self.assertRaises(ValueError):
                _validate_result_paths(
                    root / "artifacts/result.json", root / "artifacts")

    def test_runner_preserves_logical_prefix_across_include_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cuda = root / "cuda"
            physical_include = cuda / "targets/x86_64-linux/include"
            physical_include.mkdir(parents=True)
            (cuda / "include").symlink_to(physical_include, target_is_directory=True)
            prefix, logical_include = _validated_include_from_prefix(
                cuda, cuda / "include", label="cuda")
            self.assertEqual(prefix, cuda.resolve())
            self.assertEqual(logical_include, cuda.resolve() / "include")
            self.assertNotEqual(logical_include, physical_include)
            unrelated = root / "unrelated/include"
            unrelated.mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, "does not belong"):
                _validated_include_from_prefix(
                    cuda, unrelated, label="cuda")

    def test_runner_requires_manifest_bound_to_native_and_current_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            native = root / "librtdl_optix.so"
            native.write_bytes(b"native-owner-grouped-test")
            optix_include = root / "optix/include"
            cuda_include = root / "cuda/include"
            optix_include.mkdir(parents=True)
            cuda_include.mkdir(parents=True)
            nvcc = root / "cuda/bin/nvcc"
            nvcc.parent.mkdir(parents=True)
            nvcc.write_text(
                "#!/bin/sh\necho 'fake nvcc 12.9'\n", encoding="utf-8")
            nvcc.chmod(0o755)
            host_compiler = root / "toolchain/g++"
            host_compiler.parent.mkdir(parents=True)
            host_compiler.write_text(
                "#!/bin/sh\necho 'fake g++ 12.3'\n", encoding="utf-8")
            host_compiler.chmod(0o755)
            (optix_include / "optix.h").write_text(
                "#define OPTIX_VERSION 90000\n", encoding="utf-8")
            (cuda_include / "cuda.h").write_text(
                "#pragma once\n", encoding="utf-8")
            (cuda_include / "nvrtc.h").write_text(
                "#pragma once\n", encoding="utf-8")
            commit = "a" * 40
            gpu_identity = "Fake GPU, GPU-fake, 1.0, 8.9"
            manifest_path = root / "native.json"
            manifest = {
                "schema": "rtdl.v4.optix_native_snapshot_build.v1",
                "status":
                    "PASS__FRESH_NATIVE_BUILT_AND_REQUIRED_SYMBOLS_EXPORTED",
                "git_commit": commit,
                "git_commit_after_build": commit,
                "git_status_before_build": [],
                "git_status_after_build": [],
                "dirty_build_authorized": False,
                "build_id": None,
                "optix_version": 90000,
                "gpu": gpu_identity,
                "build_input": {
                    "git_commit": commit,
                    "builder_sha256": hashlib.sha256((ROOT / (
                        "scripts/build_v4_optix_native_snapshot.py"
                    )).read_bytes()).hexdigest(),
                    "source_inventory": _source_inventory(),
                    "optix_version": 90000,
                    "expected_optix_sdk": "9.0.0",
                    "compute_capability": [8, 9],
                    "gpu": gpu_identity,
                    "nvcc_path": str(nvcc.resolve()),
                    "nvcc_sha256": hashlib.sha256(
                        nvcc.read_bytes()).hexdigest(),
                    "nvcc_version": "fake nvcc 12.9",
                    "host_compiler_path": str(host_compiler.resolve()),
                    "host_compiler_sha256": hashlib.sha256(
                        host_compiler.read_bytes()).hexdigest(),
                    "host_compiler_version": "fake g++ 12.3",
                    "optix_include": str(optix_include.resolve()),
                    "cuda_include": str(cuda_include.resolve()),
                    "optix_header_inventory":
                        _header_inventory(optix_include),
                    "cuda_header_inventory":
                        _header_inventory(cuda_include),
                },
                "native_path": str(native),
                "native_bytes": native.stat().st_size,
                "native_sha256": hashlib.sha256(native.read_bytes()).hexdigest(),
                "nvcc_path": str(nvcc.resolve()),
                "nvcc_sha256": hashlib.sha256(nvcc.read_bytes()).hexdigest(),
                "nvcc_version": "fake nvcc 12.9",
                "host_compiler_path": str(host_compiler.resolve()),
                "host_compiler_sha256": hashlib.sha256(
                    host_compiler.read_bytes()).hexdigest(),
                "host_compiler_version": "fake g++ 12.3",
                "required_symbols": list(REQUIRED_SYMBOLS),
                "exported_symbol_match_mode":
                    "exact_nm_dynamic_defined_name",
                "all_required_symbols_exported": True,
            }
            manifest["build_id"] = _build_input_id(manifest["build_input"])
            manifest_path.write_text(
                json.dumps(manifest), encoding="utf-8", newline="\n")
            observed = _validate_native_build_manifest(
                manifest_path, native, git_commit=commit,
                optix_sdk="9.0.0", compute_capability=(8, 9),
                gpu_identity=gpu_identity,
                optix_include=optix_include, cuda_include=cuda_include,
                optix_prefix=root / "optix",
                cuda_prefix=root / "cuda",
                allow_dirty=False)
            self.assertEqual(
                observed["build_id"], _build_input_id(manifest["build_input"]))
            baseline = copy.deepcopy(manifest)
            manifest["native_sha256"] = "c" * 64
            manifest_path.write_text(
                json.dumps(manifest), encoding="utf-8", newline="\n")
            with self.assertRaisesRegex(RuntimeError, "selected library"):
                _validate_native_build_manifest(
                    manifest_path, native, git_commit=commit,
                    optix_sdk="9.0.0", compute_capability=(8, 9),
                    gpu_identity=gpu_identity,
                    optix_include=optix_include, cuda_include=cuda_include,
                    optix_prefix=root / "optix",
                    cuda_prefix=root / "cuda",
                    allow_dirty=False)
            manifest = copy.deepcopy(baseline)
            manifest["build_id"] = "b" * 64
            manifest_path.write_text(
                json.dumps(manifest), encoding="utf-8", newline="\n")
            with self.assertRaisesRegex(RuntimeError, "build-input digest"):
                _validate_native_build_manifest(
                    manifest_path, native, git_commit=commit,
                    optix_sdk="9.0.0", compute_capability=(8, 9),
                    gpu_identity=gpu_identity,
                    optix_include=optix_include, cuda_include=cuda_include,
                    optix_prefix=root / "optix",
                    cuda_prefix=root / "cuda",
                    allow_dirty=False)
            manifest = copy.deepcopy(baseline)
            manifest["build_input"]["compute_capability"] = [9, 0]
            manifest_path.write_text(
                json.dumps(manifest), encoding="utf-8", newline="\n")
            with self.assertRaisesRegex(RuntimeError, "source identity"):
                _validate_native_build_manifest(
                    manifest_path, native, git_commit=commit,
                    optix_sdk="9.0.0", compute_capability=(8, 9),
                    gpu_identity=gpu_identity,
                    optix_include=optix_include, cuda_include=cuda_include,
                    optix_prefix=root / "optix",
                    cuda_prefix=root / "cuda",
                    allow_dirty=False)
            manifest = copy.deepcopy(baseline)
            manifest["git_status_after_build"] = [" M changed"]
            manifest_path.write_text(
                json.dumps(manifest), encoding="utf-8", newline="\n")
            with self.assertRaisesRegex(RuntimeError, "build-time source drift"):
                _validate_native_build_manifest(
                    manifest_path, native, git_commit=commit,
                    optix_sdk="9.0.0", compute_capability=(8, 9),
                    gpu_identity=gpu_identity,
                    optix_include=optix_include, cuda_include=cuda_include,
                    optix_prefix=root / "optix",
                    cuda_prefix=root / "cuda",
                    allow_dirty=False)
            manifest = copy.deepcopy(baseline)
            manifest_path.write_text(
                json.dumps(manifest), encoding="utf-8", newline="\n")
            (cuda_include / "cuda.h").write_text(
                "#pragma once\n// drift\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "source identity"):
                _validate_native_build_manifest(
                    manifest_path, native, git_commit=commit,
                    optix_sdk="9.0.0", compute_capability=(8, 9),
                    gpu_identity=gpu_identity,
                    optix_include=optix_include, cuda_include=cuda_include,
                    optix_prefix=root / "optix",
                    cuda_prefix=root / "cuda",
                    allow_dirty=False)

    def test_preflight_resolves_and_pins_cuda_runtime_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cuda = root / "cuda"
            optix = root / "optix"
            (cuda / "lib64").mkdir(parents=True)
            (cuda / "nvvm/lib64").mkdir(parents=True)
            (cuda / "nvvm/libdevice").mkdir(parents=True)
            (cuda / "bin").mkdir(parents=True)
            optix.mkdir()
            (cuda / "lib64/libnvrtc.so.12").write_bytes(b"nvrtc")
            (cuda / "nvvm/lib64/libnvvm.so").write_bytes(b"nvvm")
            (cuda / "nvvm/libdevice/libdevice.10.bc").write_bytes(b"libdevice")
            files = resolve_cuda_runtime_files(cuda)
            environment, identity = configured_runtime_environment(
                cuda,
                optix,
                files,
                base={
                    "PATH": "/usr/bin",
                    "LD_LIBRARY_PATH": "/ambient",
                    "LD_PRELOAD": "/forbidden.so",
                    "RTDL_V4_FORMAL_LEAF_CACHE": "/forbidden",
                },
            )
            self.assertEqual(
                environment["NUMBA_CUDA_NVVM"], str(files["nvvm_library"]))
            self.assertEqual(
                environment["NUMBA_CUDA_LIBDEVICE"], str(files["libdevice"]))
            self.assertEqual(
                environment["PATH"].split(os.pathsep)[0],
                str(cuda.resolve() / "bin"),
            )
            self.assertNotIn("RTDL_V4_FORMAL_LEAF_CACHE", environment)
            self.assertNotIn("LD_PRELOAD", environment)
            self.assertEqual(environment["CUDA_HOME"], str(cuda.resolve()))
            self.assertEqual(len(identity["nvrtc_sha256"]), 64)
            self.assertTrue(identity["formal_numba_cache_disabled"])

    def test_preflight_runtime_abi_probe_is_zero_launch(self):
        self.assertEqual(
            _PREFLIGHT_SCHEMA,
            "rtdl.successor_owner_grouped_any_hit.pod_preflight.v2",
        )
        self.assertIn(
            "#include <optix_function_table_definition.h>",
            _OPTIX_RUNTIME_ABI_PROBE_SOURCE,
        )
        self.assertIn(
            "#include <optix_stubs.h>",
            _OPTIX_RUNTIME_ABI_PROBE_SOURCE,
        )
        self.assertIn("optixInit()", _OPTIX_RUNTIME_ABI_PROBE_SOURCE)
        self.assertNotIn("optixLaunch", _OPTIX_RUNTIME_ABI_PROBE_SOURCE)

    def test_native_builder_inventories_complete_optix_snapshot(self):
        inventory = _source_inventory()
        paths = [row["path"] for row in inventory]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertIn("src/native/rtdl_optix.cpp", paths)
        self.assertIn(
            "src/native/optix/rtdl_optix_v4_callback_poc.cpp", paths)
        self.assertIn("src/native/optix/rtdl_optix_api.cpp", paths)
        self.assertTrue(all(len(row["sha256"]) == 64 for row in inventory))

    def test_all_required_c_symbols_align_with_python_runtime(self):
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(
            encoding="utf-8")
        runtime = (ROOT / (
            "src/rtdsl/v4_curve_owner_grouped_any_hit_prepared_runtime.py"
        )).read_text(encoding="utf-8")
        self.assertEqual(len(REQUIRED_SYMBOLS), 4)
        for symbol in REQUIRED_SYMBOLS:
            self.assertEqual(api.count(f'extern "C" int {symbol}('), 1)
            self.assertEqual(runtime.count(f'"{symbol}"'), 1)

    def test_host_and_generated_device_launch_layouts_are_locked(self):
        native = (ROOT / (
            "src/native/optix/rtdl_optix_v4_callback_poc.cpp"
        )).read_text(encoding="utf-8")
        wrapper = (ROOT / (
            "src/rtdsl/v4_curve_owner_grouped_any_hit_optix_wrapper_codegen.py"
        )).read_text(encoding="utf-8")
        for field in (
            "traversable", "query_sx", "query_sy", "query_sz",
            "query_ex", "query_ey", "query_ez", "owner_ids",
            "primitive_count", "query_count", "owner_count",
            "owner_hit_bits", "query_completion_tokens", "status",
            "role_counters",
        ):
            self.assertIn(field, native)
            self.assertIn(field, wrapper)
        self.assertIn(
            "static_assert(sizeof(V4CurveOwnerGroupedParams) == 112u", native)
        self.assertIn(
            "static_assert(offsetof(V4CurveOwnerGroupedParams, owner_ids) == 56u",
            native,
        )
        self.assertIn(
            "static_assert(offsetof(V4CurveOwnerGroupedParams, owner_hit_bits) == 80u",
            native,
        )

    def test_native_route_is_real_optix_and_status_first(self):
        native = (ROOT / (
            "src/native/optix/rtdl_optix_v4_callback_poc.cpp"
        )).read_text(encoding="utf-8")
        wrapper = (ROOT / (
            "src/rtdsl/v4_curve_owner_grouped_any_hit_optix_wrapper_codegen.py"
        )).read_text(encoding="utf-8")
        self.assertIn("OPTIX_PRIMITIVE_TYPE_ROUND_LINEAR", native)
        self.assertIn("optixLaunch(", native)
        self.assertIn("optixTrace(params.traversable", wrapper)
        self.assertIn("atomicOr(params.owner_hit_bits + owner, 1u)", wrapper)
        self.assertIn("optixIgnoreIntersection()", wrapper)
        status_download = native.index(
            "download(output_status, status.ptr, query_count)",
            native.index("static void execute_v4_curve_owner_grouped_any_hit"),
        )
        owner_download = native.index(
            "download(output_owner_hit_bits, owner_bits.ptr",
            status_download,
        )
        self.assertLess(status_download, owner_download)

    def test_gpu_runner_uses_only_public_app_lifecycle_and_no_claim(self):
        source = (ROOT / (
            "scripts/successor_linear_rtccd_owner_grouped_pod_runner.py"
        )).read_text(encoding="utf-8")
        self.assertIn("prepare_problem", source)
        self.assertNotIn("_configure(", source)
        self.assertNotIn("ctypes", source)
        self.assertRegex(source, r'"registered_performance_timing_count":\s*0')
        self.assertRegex(source, r'"performance_claimed":\s*False')
        self.assertIn("flush=True", source)
        self.assertIn('parser.add_argument("--native-manifest", required=True', source)
        self.assertIn("RUN_INCOMPLETE.json", source)
        self.assertIn("source identity changed during GPU validation", source)

    def test_scale_parser_and_workload_registration_are_deterministic(self):
        scale = _parse_scale("8:2:3:2")
        self.assertEqual(scale, (8, 2, 3, 2))
        with self.assertRaises(Exception):
            _parse_scale("8:2:3")
        first = _workloads((scale,))
        second = _workloads((scale,))
        self.assertEqual(first, second)
        self.assertEqual(len(first), 7)
        self.assertEqual(len({row.case_id for row in first}), 7)
        with self.assertRaisesRegex(ValueError, "at most 16"):
            _workloads((scale,) * 17)

    def test_builder_does_not_claim_omitted_makefile(self):
        source = (ROOT / "scripts/build_v4_optix_native_snapshot.py").read_text(
            encoding="utf-8")
        self.assertNotIn("make build-optix", source)
        self.assertIn("rtdl_optix_cuda_helpers.cu", source)
        self.assertIn('"-lcuda", "-lnvrtc"', source)
        self.assertIn('"builder_sha256"', source)
        self.assertIn('"executed_command"', source)
        self.assertIn('"reproduction_command"', source)
        self.assertIn('"exact_nm_dynamic_defined_name"', source)
        self.assertIsNone(re.search(r"\b(collision|trajectory|robot|rtccd)\b",
                                    source.lower()))


if __name__ == "__main__":
    unittest.main()
