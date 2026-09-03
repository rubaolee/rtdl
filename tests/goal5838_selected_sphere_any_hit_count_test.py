from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import os
import random
import shlex
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

from rtdsl.v4_callback_frontend import parse_callback_source
from rtdsl.v4_callback_ir import (
    CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
    CallbackRole,
)
from rtdsl.v4_callback_lifecycle import V4Toolchain
from rtdsl.v4_public_builtin_sphere import MotionSegmentBatch, V4SphereTarget
from rtdsl.v4_public_sphere_any_hit_count import (
    SphereAnyHitCountStaticInput,
)
from rtdsl.v4_sphere_any_hit_count_contract import (
    SPHERE_ANY_HIT_COUNT_SOURCE,
    SphereAnyHitCountContractError,
    build_sphere_any_hit_count_authority,
    derive_sphere_any_hit_count_proof,
    sphere_any_hit_count_manifest,
    verify_sphere_any_hit_count_callback_program,
    verify_sphere_any_hit_count_physical_schema,
)
from rtdsl.v4_sphere_any_hit_count_family_route import (
    sphere_any_hit_count_family_route,
)
from rtdsl.v4_sphere_any_hit_count_numba_codegen import (
    generate_formal_sphere_any_hit_count_numba_leaf,
)
from rtdsl.v4_sphere_any_hit_count_prepared_runtime import (
    sphere_any_hit_count_output,
)
from rtdsl.v4_sphere_any_hit_count_wrapper_codegen import (
    generate_trusted_optix_sphere_any_hit_count_wrapper_v1,
)
from rtdsl.v4_sphere_physical_schema import SphereTargetProfile

ROOT = Path(__file__).resolve().parents[1]
CASE_ROOT = (
    ROOT / "case_studies" / "goal5838_selected_sphere_any_hit_count"
)
SELECTION = (
    ROOT
    / "history"
    / "internal_docs"
    / "goal5838_generic_core_exam_20260902"
    / "CHALLENGE_SELECTION_RESULT.json"
)
SEAL = SELECTION.with_name("GENERIC_CORE_SEAL.json")


def _target(native_sha256: str = "1" * 64) -> SphereTargetProfile:
    return SphereTargetProfile("optix", "9.0.0", "8.9", native_sha256)


def _load_case_module(name: str):
    spec = importlib.util.spec_from_file_location(name, CASE_ROOT / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_script_module(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
    ).hexdigest()


class _FakePrepared:
    def __init__(self) -> None:
        self.closed = False

    @property
    def lifecycle_receipt(self):
        return {"schema": "goal5838.fake_prepared.v1"}

    def execute(self, batch):
        output = sphere_any_hit_count_output((4, 1, 1))
        return SimpleNamespace(
            output=output,
            output_sha256=_canonical_sha256(output),
            traversal_receipt={"schema": "goal5838.fake_traversal.v1"},
            counters=(0, 3, 0, 5, 0, 3, 3),
            physical_receipt={"schema": "goal5838.fake_physical.v1"},
        )

    def close(self) -> None:
        self.closed = True


class _FakeMaterialized:
    def __init__(self, program) -> None:
        self.program = program
        self.executable = SimpleNamespace(
            executable_sha256="2" * 64,
            composed=SimpleNamespace(ptx_sha256="3" * 64),
        )

    def prepare(self, static_input):
        return _FakePrepared()


class Goal5838SelectedSphereAnyHitCountTest(unittest.TestCase):
    def test_selection_binds_exact_candidate_before_implementation(self):
        result = json.loads(SELECTION.read_text("utf-8"))
        self.assertEqual(
            result["selected_candidate"]["candidate_id"],
            "builtin_sphere::any_hit_count_continue_u64_per_query",
        )
        self.assertEqual(result["mapping"]["selected_index"], 3)
        self.assertEqual(result["activity_at_selection"], {
            "candidate_execution_count": 0,
            "candidate_implementation_count": 0,
            "gpu_receipt_count": 0,
            "prospective_success_count": 0,
        })

    def test_callback_authority_proof_and_abi_rederive(self):
        authority, proof, abi, behavior = (
            build_sphere_any_hit_count_authority(_target())
        )
        self.assertEqual(
            tuple(item.role for item in abi.roles),
            (
                CallbackRole.MAKE_RAY,
                CallbackRole.ANY_HIT,
                CallbackRole.MISS,
                CallbackRole.FINALIZE,
            ),
        )
        self.assertEqual(proof, derive_sphere_any_hit_count_proof(authority.callback))
        self.assertEqual(behavior.result_operator, "rtdl.result.per_query_u64.v1")
        self.assertEqual(authority.schema.semantic_dict()["metadata_channels"], [])
        self.assertEqual(authority.schema.geometry_flags,
                         "require_single_anyhit_call")

    def test_altered_increment_is_not_given_order_proof(self):
        altered = SPHERE_ANY_HIT_COUNT_SOURCE.replace(
            "payload.count + 1", "payload.count + 2", 1
        )
        parsed = parse_callback_source(
            altered,
            sphere_any_hit_count_manifest(),
            schema_version=CALLBACK_IR_TYPED_PHYSICAL_SCHEMA_VERSION,
        )
        verified = verify_sphere_any_hit_count_callback_program(parsed)
        with self.assertRaisesRegex(
            SphereAnyHitCountContractError, "proof_normal_form"
        ):
            derive_sphere_any_hit_count_proof(verified)

    def test_physical_schema_mutation_fails_closed(self):
        authority, _, _, _ = build_sphere_any_hit_count_authority(_target())
        for field, value in (
            ("geometry_family", "builtin_triangle"),
            ("motion_blur", True),
            ("sbt_record_count", 2),
            ("geometry_flags", "none"),
            ("provider_primitive_id_field_id", "public_application_ids"),
        ):
            with self.subTest(field=field), self.assertRaises(
                SphereAnyHitCountContractError
            ):
                verify_sphere_any_hit_count_physical_schema(
                    authority.callback,
                    replace(authority.schema, **{field: value}),
                    target=authority.target,
                )

    def test_checked_u64_leaf_increments_and_rejects_overflow(self):
        authority, _, abi, _ = build_sphere_any_hit_count_authority(_target())
        leaf = generate_formal_sphere_any_hit_count_numba_leaf(
            authority, abi, CallbackRole.ANY_HIT
        )
        namespace = {
            "__builtins__": {},
            "math": math,
            "_f32": np.float32,
            "range": range,
            "abs": abs,
        }
        exec(  # noqa: S102 - execute the generated restricted callback in isolation
            compile(leaf.generated_source, "<goal5838-any-hit>", "exec"),
            namespace,
            namespace,
        )

        def run(count: int):
            values = {
                "in.context.launch_index": 0,
                "in.hit.t": 0.5,
                "in.hit.hit_kind": 0,
                "in.payload.count": count,
            }
            pointers = {}
            arguments = []
            for path, kind in zip(leaf.parameter_order, leaf.parameter_types):
                if kind.startswith("ptr<"):
                    pointers[path] = [0]
                    arguments.append(pointers[path])
                else:
                    arguments.append(values[path])
            namespace[leaf.abi_name](*arguments)
            return pointers

        normal = run(41)
        self.assertEqual(normal["status.ok"], [1])
        self.assertEqual(normal["out.accept_continue.payload.count"], [42])
        overflow = run((1 << 64) - 1)
        self.assertEqual(overflow["status.ok"], [0])
        self.assertEqual(overflow["status.error_code"], [4])
        self.assertEqual(overflow["out.effect_tag"], [0])

    def test_wrapper_uses_real_any_hit_continuation_and_every_leaf_output(self):
        authority, _, abi, _ = build_sphere_any_hit_count_authority(_target())
        wrapper = generate_trusted_optix_sphere_any_hit_count_wrapper_v1(
            authority, authority.canonical_plan, abi
        )
        source = wrapper.source
        self.assertEqual(source.count("optixTrace("), 1)
        self.assertEqual(source.count("optixIgnoreIntersection();"), 1)
        self.assertIn("__int_as_float(0x7fffffffu)", source)
        self.assertIn("OPTIX_RAY_FLAG_DISABLE_CLOSESTHIT", source)
        self.assertIn("__anyhit__rtdl_v4_sphere_canonical", source)
        self.assertIn("__miss__rtdl_v4_sphere", source)
        self.assertNotIn("__closesthit__", source)
        self.assertEqual(source.count("params.application_ids"), 0)
        prefixes = {
            CallbackRole.MAKE_RAY: "mr",
            CallbackRole.ANY_HIT: "ah",
            CallbackRole.MISS: "ms",
            CallbackRole.FINALIZE: "fin",
        }
        for role in abi.roles:
            output_paths = role.parameter_order[
                len(role.inputs) + len(role.status):
            ]
            for path in output_paths:
                local = prefixes[role.role] + "_" + "".join(
                    char if char.isalnum() else "_" for char in path
                )
                self.assertGreaterEqual(
                    source.count(local), 3, f"inert leaf output: {role.role}:{path}"
                )

    def test_native_builder_uses_generic_provider_and_seals_required_abi(self):
        builder = _load_script_module(
            "goal5838_build_selected_sphere_optix_provider"
        )
        runner = _load_script_module("goal5838_run_selected_sphere_gpu_exam")
        verifier = _load_script_module(
            "goal5838_verify_selected_sphere_gpu_exam"
        )
        self.assertEqual(
            builder.TRANSLATION_UNIT_PATHS,
            (
                "src/native/rtdl_optix.cpp",
                "src/native/optix/rtdl_optix_cuda_helpers.cu",
            ),
        )
        self.assertNotIn(
            "src/native/rtdl_optix_v4_product.cpp",
            builder.TRANSLATION_UNIT_PATHS,
        )
        self.assertEqual(builder.REQUIRED_SYMBOLS, runner.NATIVE_BUILD_REQUIRED_SYMBOLS)
        self.assertEqual(builder.REQUIRED_SYMBOLS, verifier.NATIVE_BUILD_REQUIRED_SYMBOLS)
        self.assertEqual(builder.NATIVE_SOURCE_PATHS, runner.NATIVE_BUILD_SOURCE_PATHS)
        self.assertEqual(builder.NATIVE_SOURCE_PATHS, verifier.NATIVE_BUILD_SOURCE_PATHS)
        self.assertEqual(runner.EXAM_SOURCE_PATHS, verifier.EXAM_SOURCE_PATHS)
        self.assertTrue(all((ROOT / path).is_file() for path in runner.EXAM_SOURCE_PATHS))
        self.assertEqual(
            builder.TRANSLATION_UNIT_PATHS,
            runner.NATIVE_BUILD_TRANSLATION_UNITS,
        )
        self.assertEqual(
            builder.TRANSLATION_UNIT_PATHS,
            verifier.NATIVE_BUILD_TRANSLATION_UNITS,
        )
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text("utf-8")
        for symbol in builder.REQUIRED_SYMBOLS:
            self.assertIn(symbol, api)
        guard_start = api.index("#ifndef RTDL_V4_PRODUCT_ONLY")
        guard_end = api.index("#endif  // RTDL_V4_PRODUCT_ONLY")
        sphere_prepare = api.index(
            "rtdl_optix_v4_prepare_builtin_sphere_callback_v1"
        )
        self.assertLess(guard_start, sphere_prepare)
        self.assertLess(sphere_prepare, guard_end)

    def test_native_builder_command_and_output_boundaries_are_deterministic(self):
        builder = _load_script_module(
            "goal5838_build_selected_sphere_optix_provider"
        )
        runner = _load_script_module("goal5838_run_selected_sphere_gpu_exam")
        command = builder._build_command(
            nvcc=Path("/cuda/bin/nvcc"),
            host_compiler=Path("/usr/bin/g++-13"),
            optix_include=Path("/optix/include"),
            cuda_include=Path("/cuda/include"),
            cuda_system_include="/usr/include/x86_64-linux-gnu",
            build_id="a" * 64,
            compute_capability=(8, 9),
            geos_cflags=["-I/geos/include"],
            geos_libraries=["-lgeos_c"],
            library_dirs=[Path("/cuda/lib64")],
            nvrtc_library=Path("/cuda/lib64/libnvrtc.so.12"),
            output=Path("/tmp/goal5838.so"),
        )
        self.assertEqual(command[0:3], ["/cuda/bin/nvcc", "-ccbin", "/usr/bin/g++-13"])
        self.assertIn("-arch=sm_89", command)
        self.assertIn(str(ROOT / "src/native/rtdl_optix.cpp"), command)
        self.assertIn("-lcuda", command)
        self.assertIn("/cuda/lib64/libnvrtc.so.12", command)
        nvrtc_index = command.index("/cuda/lib64/libnvrtc.so.12")
        self.assertEqual(command[nvrtc_index - 1], "-Xlinker")
        self.assertNotIn("-lnvrtc", command)
        self.assertEqual(command[-2:], ["-o", "/tmp/goal5838.so"])
        with tempfile.TemporaryDirectory() as temporary:
            real_nvrtc = Path(temporary) / "libnvrtc.so.12.8.93"
            linked_nvrtc = Path(temporary) / "libnvrtc.so.12"
            real_nvrtc.write_bytes(b"nvrtc")
            linked_nvrtc.symlink_to(real_nvrtc.name)
            ldd_output = (
                f"libnvrtc.so.12 => {linked_nvrtc} (0x0000000000000000)\n"
            )
            self.assertEqual(
                builder._resolve_ldd_dependency(ldd_output, "libnvrtc.so"),
                real_nvrtc.resolve(),
            )
            self.assertEqual(
                runner._resolve_ldd_dependency(ldd_output, "libnvrtc.so"),
                real_nvrtc.resolve(),
            )
            with self.assertRaisesRegex(RuntimeError, "expected one resolved"):
                builder._resolve_ldd_dependency("linux-vdso.so.1\n", "libnvrtc.so")
        self.assertEqual(builder._parse_compute_capability("8.9"), (8, 9))
        self.assertEqual(builder._optix_sdk_number("8.0.0"), 80000)
        self.assertEqual(runner._optix_sdk_number("8.0.0"), 80000)
        with self.assertRaises(ValueError):
            builder._optix_sdk_number("08.0.0")
        with patch.dict(os.environ, {"CUDA_VISIBLE_DEVICES": "0"}):
            self.assertEqual(builder._require_cuda_visibility(), "0")
            self.assertEqual(runner._require_cuda_visibility(), "0")
        with (
            patch.dict(os.environ, {}, clear=True),
            self.assertRaisesRegex(RuntimeError, "CUDA_VISIBLE_DEVICES=0"),
        ):
            builder._require_cuda_visibility()
        with self.assertRaises(ValueError):
            builder._parse_compute_capability("sm_89")
        with self.assertRaisesRegex(ValueError, "outside Git tree"):
            builder._require_external_outputs(ROOT / "build/goal5838.so")
        with self.assertRaisesRegex(ValueError, "outside Git tree"):
            runner._require_external_output(ROOT / "goal5838-result.json")
        with self.assertRaisesRegex(ValueError, "outside Git tree"):
            verifier = _load_script_module(
                "goal5838_verify_selected_sphere_gpu_exam"
            )
            verifier._require_external_output(
                ROOT / "goal5838-verification.json",
                artifact_path=Path("/tmp/goal5838-artifact.json"),
            )
        with self.assertRaisesRegex(ValueError, "differ from the exam artifact"):
            verifier._require_external_output(
                Path("/tmp/goal5838-artifact.json"),
                artifact_path=Path("/tmp/goal5838-artifact.json"),
            )

    def test_target_compiler_prefers_exact_configured_nvrtc_file(self):
        from rtdsl import v4_sphere_optix_compiler as compiler

        with tempfile.TemporaryDirectory() as temporary:
            nvrtc = Path(temporary) / "libnvrtc.so.13"
            nvrtc.write_bytes(b"synthetic-nvrtc")
            sentinel = object()
            with (
                patch.dict(
                    os.environ,
                    {compiler.NVRTC_LIBRARY_ENV: str(nvrtc)},
                    clear=False,
                ),
                patch.object(compiler.ctypes, "CDLL", return_value=sentinel) as load,
            ):
                self.assertIs(compiler._load_nvrtc(), sentinel)
            load.assert_called_once_with(str(nvrtc.resolve()))
        with (
            patch.dict(
                os.environ,
                {compiler.NVRTC_LIBRARY_ENV: "/absent/libnvrtc.so"},
                clear=False,
            ),
            self.assertRaisesRegex(RuntimeError, "configured NVRTC"),
        ):
            compiler._load_nvrtc()

    def test_runner_and_verifier_bind_exact_compiler_environment(self):
        runner = _load_script_module(
            "goal5838_run_selected_sphere_gpu_exam"
        )
        verifier = _load_script_module(
            "goal5838_verify_selected_sphere_gpu_exam"
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cuda = root / "cuda"
            optix = root / "optix"
            cuda_include = cuda / "include"
            optix_include = optix / "include"
            for directory in (
                cuda_include,
                optix_include,
                cuda / "lib64",
                cuda / "nvvm" / "lib64",
                cuda / "nvvm" / "libdevice",
            ):
                directory.mkdir(parents=True, exist_ok=True)
            nvrtc = cuda / "lib64" / "libnvrtc.so.12"
            nvvm = cuda / "nvvm" / "lib64" / "libnvvm.so"
            libdevice = cuda / "nvvm" / "libdevice" / "libdevice.10.bc"
            native = root / "librtdl_optix.so"
            for path, payload in (
                (nvrtc, b"nvrtc"),
                (nvvm, b"nvvm"),
                (libdevice, b"libdevice"),
                (native, b"native"),
            ):
                path.write_bytes(payload)
            build_input = {
                "cuda_prefix": str(cuda.resolve()),
                "cuda_include": str(cuda_include.resolve()),
                "optix_prefix": str(optix.resolve()),
                "optix_include": str(optix_include.resolve()),
                "nvrtc_library_path": str(nvrtc.resolve()),
                "nvrtc_library_bytes": nvrtc.stat().st_size,
                "nvrtc_library_sha256": hashlib.sha256(
                    nvrtc.read_bytes()
                ).hexdigest(),
            }
            environment = {
                "CUDA_HOME": str(cuda),
                "CUDA_PATH": str(cuda),
                "RTDL_V4_CUDA_PREFIX": str(cuda),
                "RTDL_V4_OPTIX_PREFIX": str(optix),
                "RTDL_V4_NVRTC_LIBRARY": str(nvrtc),
                "NUMBA_CUDA_NVVM": str(nvvm),
                "NUMBA_CUDA_LIBDEVICE": str(libdevice),
            }
            with patch.dict(os.environ, environment, clear=True):
                identity = runner._capture_compiler_environment(
                    {"build_input": build_input},
                    optix_include=optix_include,
                    cuda_include=cuda_include,
                    native_override=None,
                )
                os.environ.update(
                    {
                        name: str(native)
                        for name in runner.NATIVE_LIBRARY_OVERRIDE_ENVIRONMENT
                    }
                )
                after = runner._capture_compiler_environment(
                    {"build_input": build_input},
                    optix_include=optix_include,
                    cuda_include=cuda_include,
                    native_override=native,
                )
                os.environ["NUMBA_ENABLE_CUDASIM"] = "1"
                with self.assertRaisesRegex(
                    RuntimeError, "forbidden compiler environment"
                ):
                    runner._capture_compiler_environment(
                        {"build_input": build_input},
                        optix_include=optix_include,
                        cuda_include=cuda_include,
                        native_override=native,
                    )
            self.assertEqual(identity, after)
            verifier._verify_compiler_environment(
                identity, build_input=build_input
            )
            tampered = copy.deepcopy(identity)
            tampered["compiler_files"][0]["sha256"] = "f" * 64
            body = dict(tampered)
            body.pop("identity_sha256")
            tampered["identity_sha256"] = verifier._digest(body)
            with self.assertRaisesRegex(
                verifier.Goal5838ExamVerificationError,
                "NVRTC differs",
            ):
                verifier._verify_compiler_environment(
                    tampered, build_input=build_input
                )

    def test_independent_verifier_rejects_resealed_native_build_tampering(self):
        builder = _load_script_module(
            "goal5838_build_selected_sphere_optix_provider"
        )
        verifier = _load_script_module(
            "goal5838_verify_selected_sphere_gpu_exam"
        )
        source_rows = [
            {
                "path": relative,
                "bytes": (ROOT / relative).stat().st_size,
                "sha256": hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
            }
            for relative in verifier.NATIVE_BUILD_SOURCE_PATHS
        ]
        gpu = {
            "name": "Synthetic GPU",
            "uuid": "GPU-synthetic",
            "driver_version": "999.1",
            "compute_capability": "8.9",
        }
        headers = [
            {
                "name": name,
                "path": f"/sdk/include/{name}",
                "bytes": index + 1,
                "sha256": f"{index + 1:064x}",
            }
            for index, name in enumerate(builder.KEY_HEADER_NAMES)
        ]
        abi_probe = {
            "source_sha256": verifier.OPTIX_RUNTIME_ABI_PROBE_SOURCE_SHA256,
            "compile_command_template": [
                "/usr/bin/g++-13",
                "-std=c++17",
                "-I/optix/include",
                "-I/cuda/include",
                "<temporary>/probe.cpp",
                "-ldl",
                "-o",
                "<temporary>/probe",
            ],
            "compile_returncode": 0,
            "compiler_output_sha256": hashlib.sha256(b"").hexdigest(),
            "executable_bytes": 1234,
            "executable_sha256": "d" * 64,
            "runtime_returncode": 0,
            "runtime_output": "optixInit_result=0",
            "optix_launch_count": 0,
            "passed": True,
        }
        build_input = {
            "schema": "rtdl.goal5838.selected_sphere_optix_build_input.v2",
            "translation_units": list(verifier.NATIVE_BUILD_TRANSLATION_UNITS),
            "builder_path": verifier.NATIVE_BUILD_SOURCE_PATHS[0],
            "builder_sha256": source_rows[0]["sha256"],
            "cuda_prefix": "/cuda",
            "cuda_include": "/cuda/include",
            "cuda_system_include": "/usr/include/x86_64-linux-gnu",
            "nvcc_path": "/cuda/bin/nvcc",
            "nvcc_sha256": "a" * 64,
            "nvcc_version": "Cuda compilation tools, release 12.8",
            "nvrtc_library_path": "/cuda/lib64/libnvrtc.so.12",
            "nvrtc_library_bytes": 123456,
            "nvrtc_library_sha256": "e" * 64,
            "host_compiler_path": "/usr/bin/g++-13",
            "host_compiler_sha256": "b" * 64,
            "host_compiler_version": "g++ 13",
            "optix_prefix": "/optix",
            "optix_include": "/optix/include",
            "optix_version": 80000,
            "expected_optix_sdk": "8.0.0",
            "key_headers": headers,
            "compute_capability": "8.9",
            "gpu": gpu,
            "cuda_visible_devices": "0",
            "optix_runtime_abi_probe": abi_probe,
            "language_standard": "c++17",
            "optimization": "O3",
            "position_independent_code": True,
            "geos_mode": "disabled-header-absent",
            "geos_cflags": [],
            "geos_libraries": [],
            "library_dirs": ["/cuda/lib64"],
        }
        build_input_sha256 = verifier._digest(build_input)
        verifier._verify_optix_runtime_abi_probe(build_input)
        tampered_probe_input = copy.deepcopy(build_input)
        tampered_probe_input["optix_runtime_abi_probe"][
            "runtime_output"
        ] = "optixInit_result=7801"
        with self.assertRaisesRegex(
            verifier.Goal5838ExamVerificationError,
            "runtime ABI probe differs",
        ):
            verifier._verify_optix_runtime_abi_probe(tampered_probe_input)
        command = builder._build_command(
            nvcc=Path(build_input["nvcc_path"]),
            host_compiler=Path(build_input["host_compiler_path"]),
            optix_include=Path(build_input["optix_include"]),
            cuda_include=Path(build_input["cuda_include"]),
            cuda_system_include=build_input["cuda_system_include"],
            build_id=build_input_sha256,
            compute_capability=(8, 9),
            geos_cflags=[],
            geos_libraries=[],
            library_dirs=[Path("/cuda/lib64")],
            nvrtc_library=Path(build_input["nvrtc_library_path"]),
            output=Path("/tmp/.goal5838.partial"),
        )
        target = {
            "native_library_path": "/tmp/goal5838.so",
            "native_library_bytes": 123,
            "native_library_sha256": "c" * 64,
            "optix_sdk": "8.0.0",
            "compute_capability": "8.9",
            "gpu": {
                **gpu,
                "pci_bus_id": "0000:01:00.0",
                "memory_mib": "24576",
            },
        }
        reproduction = [*command[:-1], target["native_library_path"]]
        manifest = {
            "schema": verifier.NATIVE_BUILD_RESULT_DOMAIN,
            "status": "PASS__FRESH_PROVIDER_DSO_AND_REQUIRED_ABI_EXPORTED",
            "repository": {
                "expected_commit": "f" * 40,
                "head_before": "f" * 40,
                "branch": "synthetic",
                "origin_url": "https://example.invalid/rtdl",
                "clean_before": True,
                "source_files": source_rows,
                "head_after": "f" * 40,
                "clean_after": True,
            },
            "build_input": build_input,
            "build_input_sha256": build_input_sha256,
            "executed_command": command,
            "executed_command_display": shlex.join(command),
            "reproduction_command": reproduction,
            "reproduction_command_display": shlex.join(reproduction),
            "build_log": {
                "path": "/tmp/goal5838.log",
                "bytes": 0,
                "sha256": hashlib.sha256(b"").hexdigest(),
            },
            "native_output": {
                "path": target["native_library_path"],
                "bytes": target["native_library_bytes"],
                "sha256": target["native_library_sha256"],
            },
            "required_symbols": list(verifier.NATIVE_BUILD_REQUIRED_SYMBOLS),
            "required_symbol_check": "exact_nm_dynamic_defined_name",
            "all_required_symbols_exported": True,
            "dynamic_dependencies": "synthetic",
            "dynamic_nvrtc": {
                "path": build_input["nvrtc_library_path"],
                "bytes": build_input["nvrtc_library_bytes"],
                "sha256": build_input["nvrtc_library_sha256"],
            },
            "result_sha256": "",
        }
        manifest["result_sha256"] = verifier._native_build_seal(manifest)
        def local_blob(_commit, relative, *, root):
            return (root / relative).read_bytes()

        with patch.object(verifier, "_git_blob", side_effect=local_blob):
            verifier._verify_native_build(
                manifest, commit="f" * 40, target=target, root=ROOT
            )
            tampered = copy.deepcopy(manifest)
            tampered["all_required_symbols_exported"] = False
            tampered["result_sha256"] = verifier._native_build_seal(tampered)
            with self.assertRaisesRegex(
                verifier.Goal5838ExamVerificationError,
                "manifest envelope differs",
            ):
                verifier._verify_native_build(
                    tampered, commit="f" * 40, target=target, root=ROOT
                )

    def test_optix_runtime_abi_probe_records_zero_launch_success(self):
        builder = _load_script_module(
            "goal5838_build_selected_sphere_optix_provider"
        )
        verifier = _load_script_module(
            "goal5838_verify_selected_sphere_gpu_exam"
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            compiler = root / "fake-cxx"
            compiler.write_text(
                "#!/bin/sh\n"
                "output=''\n"
                "while [ \"$#\" -gt 0 ]; do\n"
                "  if [ \"$1\" = '-o' ]; then shift; output=$1; fi\n"
                "  shift\n"
                "done\n"
                "printf '%s\\n' '#!/bin/sh' "
                "'printf \"optixInit_result=0\\\\n\"' > \"$output\"\n"
                "chmod +x \"$output\"\n",
                encoding="ascii",
            )
            compiler.chmod(0o755)
            result = builder.probe_optix_runtime_abi(
                compiler,
                root / "optix" / "include",
                root / "cuda" / "include",
            )
        self.assertTrue(result["passed"])
        self.assertEqual(result["runtime_output"], "optixInit_result=0")
        self.assertEqual(result["optix_launch_count"], 0)
        self.assertEqual(
            result["source_sha256"],
            verifier.OPTIX_RUNTIME_ABI_PROBE_SOURCE_SHA256,
        )
        self.assertEqual(
            result["compile_command_template"][-3:],
            ["-ldl", "-o", "<temporary>/probe"],
        )

    def test_family_route_is_admitted_without_metadata_or_core_dispatch(self):
        route = sphere_any_hit_count_family_route()
        program = route.compile()
        shape = route.plan.to_dict()["family_shape"]
        self.assertEqual(route.classification, "prospective_selected_extension")
        self.assertEqual(shape["graph_nodes"][0]["primitive_kind"], "builtin_sphere")
        self.assertEqual(shape["channels"], [])
        self.assertEqual(shape["views"], [])
        self.assertEqual(
            shape["physical"]["sbt"]["record_count_relation"], "constant_one"
        )
        self.assertEqual(
            shape["capabilities"],
            [
                "any_hit_accept_continue",
                "builtin_sphere_intersection",
                "callback_ir",
                "fail_closed_status",
                "per_query_u64_output",
            ],
        )
        self.assertEqual(
            shape["result_pipeline"][0]["operator_id"],
            "rtdl.result.per_query_u64.v1",
        )
        self.assertEqual(
            program.provider_projection.plan_sha256, route.plan.plan_sha256
        )
        provider_module = (
            ROOT / "src" / "rtdsl" / "v4_sphere_any_hit_count_family_route.py"
        )
        self.assertEqual(
            route.provider.descriptor.implementation_sha256,
            hashlib.sha256(provider_module.read_bytes()).hexdigest(),
        )
        seal = json.loads(SEAL.read_text("utf-8"))
        adapter_row = next(
            row
            for row in seal["stage_b_evidence_files_at_seal"]
            if row["path"] == "src/rtdsl/v4_family_route_adapters.py"
        )
        adapter = ROOT / adapter_row["path"]
        self.assertEqual(adapter.stat().st_size, adapter_row["bytes"])
        self.assertEqual(
            hashlib.sha256(adapter.read_bytes()).hexdigest(),
            adapter_row["sha256"],
        )
        verifier = _load_script_module(
            "goal5838_verify_selected_sphere_gpu_exam"
        )
        self.assertEqual(verifier.PLAN_SHA256, route.plan.plan_sha256)
        self.assertEqual(
            verifier.PROVIDER_DESCRIPTOR_SHA256,
            route.provider.descriptor.descriptor_sha256,
        )
        self.assertEqual(
            verifier.PROVIDER_PROJECTION_SHA256,
            program.provider_projection.projection_sha256,
        )

    def test_generic_public_lifecycle_wires_selected_route(self):
        fixture = _load_case_module("fixture").selected_exam_fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            native = root / "librtdl_optix.so"
            native.write_bytes(b"goal5838-native-placeholder")
            target = V4SphereTarget.from_native(
                native, optix_sdk="9.0.0", compute_capability="8.9"
            )
            optix_include = root / "optix"
            cuda_include = root / "cuda"
            optix_include.mkdir()
            cuda_include.mkdir()
            toolchain = V4Toolchain(
                (8, 9),
                optix_include,
                cuda_include,
                "3.12.14",
                "0.65.1",
                "2.4.4",
            )
            route = sphere_any_hit_count_family_route()
            program = route.compile()
            with patch(
                "rtdsl.v4_public_sphere_any_hit_count."
                "materialize_sphere_any_hit_count_program",
                side_effect=lambda concrete, *, toolchain: _FakeMaterialized(
                    concrete
                ),
            ):
                materialized = program.materialize(
                    target=target, toolchain=toolchain
                )
                prepared = materialized.prepare(
                    SphereAnyHitCountStaticInput(
                        fixture["centers"], fixture["radii"]
                    )
                )
                result = prepared.execute(
                    MotionSegmentBatch(fixture["queries"][:3])
                )
                self.assertEqual(tuple(result.output["counts"]), (4, 1, 1))
                prepared.close()
                prepared.close()

    def test_independent_oracle_and_conditioned_fixture(self):
        verifier = _load_script_module(
            "goal5838_verify_selected_sphere_gpu_exam"
        )
        oracle_path = CASE_ROOT / "sphere_any_hit_count_oracle.py"
        oracle_source = (CASE_ROOT / "sphere_any_hit_count_oracle.py").read_text(
            "utf-8"
        )
        self.assertNotIn("import rtdsl", oracle_source)
        self.assertNotIn("from rtdsl", oracle_source)
        self.assertEqual(
            verifier.ORACLE_SHA256,
            hashlib.sha256(oracle_path.read_bytes()).hexdigest(),
        )
        fixture = _load_case_module("fixture").selected_exam_fixture()
        oracle = _load_case_module("sphere_any_hit_count_oracle")
        self.assertEqual(
            oracle.count_batch(
                fixture["queries"], fixture["centers"], fixture["radii"]
            ),
            (4, 1, 1, 0, 4, 0),
        )
        self.assertEqual(
            oracle.count_batch(
                fixture["queries"],
                tuple(reversed(fixture["centers"])),
                tuple(reversed(fixture["radii"])),
            ),
            (4, 1, 1, 0, 4, 0),
        )
        with self.assertRaisesRegex(ValueError, "exact tangent"):
            oracle.count_intersections(
                (0.0, 1.0, 0.0),
                (6.0, 1.0, 0.0),
                ((3.0, 0.0, 0.0),),
                (1.0,),
            )

    def test_exact_oracle_matches_separate_root_formula_away_from_boundaries(self):
        oracle = _load_case_module("sphere_any_hit_count_oracle")
        generator = random.Random(5838)
        checked = 0
        for _ in range(2_000):
            start = tuple(generator.uniform(-10.0, 10.0) for _ in range(3))
            end = tuple(generator.uniform(-10.0, 10.0) for _ in range(3))
            center = tuple(generator.uniform(-10.0, 10.0) for _ in range(3))
            radius = generator.uniform(0.1, 3.0)
            projected_start = tuple(oracle.f32(value) for value in start)
            projected_end = tuple(oracle.f32(value) for value in end)
            projected_center = tuple(oracle.f32(value) for value in center)
            projected_radius = oracle.f32(radius)
            direction = tuple(
                oracle.f32(projected_end[axis] - projected_start[axis])
                for axis in range(3)
            )
            if direction == (0.0, 0.0, 0.0):
                continue
            offset = tuple(
                projected_start[axis] - projected_center[axis]
                for axis in range(3)
            )
            a = sum(value * value for value in direction)
            half_b = sum(
                offset[axis] * direction[axis] for axis in range(3)
            )
            c = sum(value * value for value in offset) - projected_radius**2
            if c <= 0.0:
                continue
            discriminant = half_b * half_b - a * c
            scale = max(1.0, abs(half_b * half_b), abs(a * c))
            if abs(discriminant) <= 1e-7 * scale:
                continue
            expected = False
            if discriminant > 0.0:
                entry = (-half_b - math.sqrt(discriminant)) / a
                if min(abs(entry), abs(entry - 1.0)) <= 1e-7:
                    continue
                expected = 0.0 <= entry <= 1.0
            observed = oracle.count_intersections(
                start, end, (center,), (radius,)
            )
            self.assertEqual(observed, int(expected))
            checked += 1
        self.assertGreater(checked, 1_900)

    def test_static_input_materializes_single_pass_columns(self):
        static_input = SphereAnyHitCountStaticInput(
            (center for center in ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0))),
            (radius for radius in (0.5, 1.25)),
        )
        self.assertEqual(
            static_input.centers,
            ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0)),
        )
        self.assertEqual(static_input.radii, (0.5, 1.25))

    def test_independent_receipt_verifier_rejects_resealed_tampering(self):
        verifier = _load_script_module(
            "goal5838_verify_selected_sphere_gpu_exam"
        )
        counts = (4, 1, 1, 0, 4, 0)
        output = {
            "schema": "rtdl.v4.sphere_any_hit_count_output.v1",
            "counts": list(counts),
        }
        output_sha256 = verifier._digest(output)
        native_sha256 = "a" * 64
        generated_sha256 = "b" * 64
        target = {
            "native_library_path": "/tmp/librtdl_optix.so",
            "native_library_sha256": native_sha256,
            "optix_sdk": "8.1.0",
            "compute_capability": "8.9",
        }
        target["profile_sha256"] = verifier._digest(
            {
                "provider": "optix",
                "optix_sdk": "8.1.0",
                "compute_capability": "8.9",
                "native_sha256": native_sha256,
                "supports_builtin_sphere": True,
                "max_graph_depth": 1,
            }
        )
        identity = {"generated_artifact_sha256": generated_sha256}
        bundle_id = verifier._physical_program_bundle_id(
            verifier.PROGRAM_BUNDLE
        )
        traversable = 12345
        snapshot = {name: 1 for name in verifier.SNAPSHOT_FIELDS}
        snapshot.update(
            {
                "nonce_hi": 7,
                "nonce_lo": 11,
                "attempted_launch_count": 1,
                "successful_launch_count": 1,
                "failed_launch_count": 0,
                "complete_context_launch_count": 1,
                "incomplete_context_launch_count": 0,
                "context_bind_count": 1,
                "raygen_invocation_count": 6,
                "program_bundle_mix": verifier._native_audit_mix_u64(
                    0, bundle_id
                ),
                "traversable_mix": verifier._native_audit_mix_u64(
                    0, traversable
                ),
                "first_program_bundle_id": bundle_id,
                "last_program_bundle_id": bundle_id,
                "first_traversable": traversable,
                "last_traversable": traversable,
                "pending_context_at_finish": 0,
                "session_error": 0,
                "incomplete_callsite_record_count": 0,
                "incomplete_callsite_lines": [0] * 32,
            }
        )
        fingerprints = verifier._execution_native_fingerprints(
            counts, verifier.FIXTURE_QUERIES
        )
        self.assertEqual(
            verifier._static_commitment(),
            "7b327720385b1983e88a96427a3aa8d211958bc3156896bb1039116024e461be",
        )
        self.assertEqual(
            verifier._static_native_fingerprint(),
            "66f985e50aee67aa89bd7ada954a1c7e810b7b36518dbeb0603a579f4d0e66b9",
        )
        self.assertEqual(
            verifier._query_commitment(verifier.FIXTURE_QUERIES),
            "b1019bae740e9757947e26c36bbaed67171ddf53b8aa9affec3312657b964b60",
        )
        self.assertEqual(
            fingerprints,
            {
                "query": (
                    "9cccb84fe13acf14a7207741324b612731714dd54359929293313bd9b2bea9c2"
                ),
            "output": (
                "7202e52c1ad750bafcff6f74c162cf84717de278a0c82934c6c3aa469bf76cbd"
                ),
                "status": (
                    "121e786cbe5c0ea2b0f1d4abd120a8648151a73cf6466cda9cb68170cdbeb9c3"
                ),
                "counter": (
                    "de221d177a58fe9561257e16d3095e732fe43384cbd8fd931b87bee1aa964164"
                ),
                "raw_output_commitment": (
                    "85f9e013d5418962388558d25af213ecea83b1907cfc4a601a20f3e6f2301152"
                ),
            },
        )
        reverse_queries = tuple(reversed(verifier.FIXTURE_QUERIES))
        reverse_fingerprints = verifier._execution_native_fingerprints(
            tuple(reversed(counts)), reverse_queries
        )
        self.assertEqual(
            verifier._query_commitment(reverse_queries),
            "eae117c1a3078d0f6354446b934b3f4f4b6eddbcec31db559ddd6d1e8d77ef5e",
        )
        self.assertEqual(
            reverse_fingerprints["query"],
            "9e40208456752bf4c141b2e2cee8f93709cdc3c1e0defdd23eba675bcd072d82",
        )
        self.assertEqual(
            reverse_fingerprints["output"],
            "1532be98ad0430ba8425811b1843fa84fec8e746bce722b464c32fdca50f653d",
        )
        authority_nonce, physical_plan_sha256 = verifier._physical_authority(
            target["profile_sha256"]
        )
        query_commitment = verifier._query_commitment(verifier.FIXTURE_QUERIES)
        descriptor = {
            "schema": "rtdl.v4.native_builtin_sphere_descriptor.v2",
            "build_input_type": 0x2146,
            "primitive_type": 0x2506,
            "primitive_type_flags": 1 << 6,
            "builtin_is_build_flags": 1 << 2,
            "build_flags": 1 << 2,
            "geometry_flags": 1 << 1,
            "builtin_is_module": True,
            "user_intersection_program": False,
            "uses_motion_blur": False,
            "center_stride_bytes": 12,
            "radius_stride_bytes": 4,
            "single_radius": False,
            "primitive_index_offset": 0,
            "sbt_record_count": 1,
            "gas_count": 1,
            "primitive_count": 6,
            "motion_key_count": 0,
            "traversable_graph_flags": 1,
            "max_payload_values": 8,
            "max_attribute_values": 0,
            "max_trace_depth": 1,
            "program_group_count": 3,
            "compiled_optix_version": 80100,
            "compiled_optix_major": 8,
            "compiled_optix_minor": 1,
            "compiled_optix_patch": 0,
            "cuda_device_ordinal": 0,
            "cuda_compute_capability_major": 8,
            "cuda_compute_capability_minor": 9,
            "cuda_driver_version": 12080,
            "static_input_fingerprint": verifier._static_native_fingerprint(),
            "device_static_input_fingerprint": (
                verifier._static_native_fingerprint()
            ),
            "center_device_pointer": 1,
            "radius_device_pointer": 2,
            "application_id_device_pointer": 3,
            "traversable_identity": traversable,
            "last_execution_present": True,
            "last_status_failed": False,
            "last_query_count": 6,
            "last_status_d2h_call_count": 1,
            "last_application_output_d2h_call_count": 6,
            "last_output_after_status_failure_count": 0,
            "last_query_device_pointer_nonzero_count": 6,
            "last_output_device_pointer_nonzero_count": 8,
            "last_query_fingerprint": fingerprints["query"],
            "last_device_query_fingerprint": fingerprints["query"],
            "last_output_fingerprint": fingerprints["output"],
            "last_status_fingerprint": fingerprints["status"],
            "last_counter_fingerprint": fingerprints["counter"],
            "last_query_device_pointer_fingerprint": "3" * 64,
            "last_output_device_pointer_fingerprint": "4" * 64,
        }
        semantic_digest = verifier._digest(
            {
                "authority": authority_nonce,
                "plan": physical_plan_sha256,
                "abi": verifier.CALLBACK_ABI_SHA256,
                "ptx": generated_sha256,
                "native": native_sha256,
                "descriptor": descriptor,
                "query": query_commitment,
            }
        )
        physical_receipt = {
            "schema": "rtdl.v4.sphere_any_hit_count_physical_receipt.v1",
            "native_descriptor": descriptor,
            "build_input_type_name": "OPTIX_BUILD_INPUT_TYPE_SPHERES",
            "primitive_type_name": "OPTIX_PRIMITIVE_TYPE_SPHERE",
            "builtin_is_api_name": "optixBuiltinISModuleGet",
            "geometry_flags_name": (
                "OPTIX_GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL"
            ),
            "continuation_name": "optixIgnoreIntersection",
            "result_semantics": "per_query_u64_intersected_primitive_count",
            "provider_private_primitive_ids": True,
            "metadata_channels": [],
            "native_library_sha256": native_sha256,
            "loaded_native_library_path": target["native_library_path"],
            "composed_ptx_sha256": generated_sha256,
            "authority_nonce": authority_nonce,
            "field_mapping_commitment_sha256": (
                verifier._field_mapping_commitment()
            ),
            "static_input_commitment_sha256": verifier._static_commitment(),
            "status_before_output": True,
            "numeric_policy": (
                "binary32_projection__disc_ratio_ge_2^-12__"
                "exact_tangent_prelaunch_reject__"
                "front_entry_endpoint_margin_2^-12__"
                "nonexact_toi_ulp_le_4_v3"
            ),
            "discriminant_guard_binary32_unit_roundoffs": 4096,
            "nonexact_toi_ulp_bound": 4,
            "query_commitment_sha256": query_commitment,
            "output_commitment_sha256": output_sha256,
            "raw_output_commitment_sha256": fingerprints[
                "raw_output_commitment"
            ],
            "role_counters": [0, 6, 0, 10, 0, 6, 6],
        }
        base = {
            "schema": "rtdl.physical_execution.traversal_receipt.v1",
            "provider_library": "librtdl_optix",
            "provider_library_path": target["native_library_path"],
            "provider_library_sha256": native_sha256,
            "route_identity": verifier.ROUTE_IDENTITY,
            "semantic_digest": semantic_digest,
            "output_digest": output_sha256,
            "nonce": {"hi": 7, "lo": 11},
            "physical_executor_classification": "optix_traversal_observed",
            "expected_program_bundles": [verifier.PROGRAM_BUNDLE],
            "expected_program_bundle_ids": [bundle_id],
            "expected_program_observed_at_receipt_edge": True,
            "native_snapshot": snapshot,
            "claim_rules": {
                "provider_name_alone_proves_traversal": False,
                "selected_template_alone_proves_traversal": False,
                "successful_optix_launch_required": True,
                "nonzero_traversable_binding_required": True,
                "program_bundle_binding_required": True,
                "output_digest_bound": True,
            },
        }
        base["receipt_sha256"] = verifier._digest(base)
        receipt = {
            **base,
            "selected_topology": verifier.SELECTED_CANDIDATE_ID,
            "role_counters": [0, 6, 0, 10, 0, 6, 6],
            "physical_receipt": physical_receipt,
        }
        verifier._verify_traversal_receipt(
            receipt,
            counts=counts,
            queries=verifier.FIXTURE_QUERIES,
            output_sha256=output_sha256,
            target=target,
            identity=identity,
        )
        tampered = copy.deepcopy(receipt)
        tampered["native_snapshot"]["successful_launch_count"] = 0
        body = {
            key: value
            for key, value in tampered.items()
            if key
            not in {
                "receipt_sha256",
                "selected_topology",
                "role_counters",
                "physical_receipt",
            }
        }
        tampered["receipt_sha256"] = verifier._digest(body)
        with self.assertRaisesRegex(
            verifier.Goal5838ExamVerificationError,
            "native traversal observation differs",
        ):
            verifier._verify_traversal_receipt(
                tampered,
                counts=counts,
                queries=verifier.FIXTURE_QUERIES,
                output_sha256=output_sha256,
                target=target,
                identity=identity,
            )

    def test_frozen_core_bytes_remain_at_preselection_seal(self):
        seal = json.loads(SEAL.read_text("utf-8"))
        for row in seal["frozen_core_files"]:
            path = ROOT / row["path"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                             row["sha256"], row["path"])


if __name__ == "__main__":
    unittest.main()
