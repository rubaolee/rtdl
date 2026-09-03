#!/usr/bin/env python3
"""Run the prospective Goal5838 selected topology on a true OptiX target."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from rtdsl.v4_callback_lifecycle import V4Toolchain
from rtdsl.v4_sphere_any_hit_count import (
    MotionSegmentBatch,
    SphereAnyHitCountStaticInput,
    V4SphereTarget,
    sphere_any_hit_count_family_route,
)

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
SELECTED_CANDIDATE_ID = (
    "builtin_sphere::any_hit_count_continue_u64_per_query"
)
SELECTION_RESULT_SHA256 = (
    "9f543f52cd9453e0410766aa79c3f302a6a0e39314487279842fa5ad5e57ed61"
)
GENERIC_CORE_SEAL_SHA256 = (
    "c2a461c8a4a61650044b724d103a80d25241b44b7b486c071b601946292e5dae"
)
CHALLENGE_TABLE_SHA256 = (
    "0a2b2c01aed75ad08fad44f7fbc2509ef632d786545e0202b9a4b27425a30345"
)
TARGET_LOCAL_RANDOM_VALUE = (
    "aa62c239c5079ed89cf0ad70c1b44245552bf2dd519d6d4871518746fac2efca"
    "5a64bb5a21956e897e36a5bc7cc0f0bd53d1f9ae585045a3c762656f852eefa7"
)
EXAM_SOURCE_PATHS = (
    "case_studies/goal5838_selected_sphere_any_hit_count/README.md",
    (
        "history/internal_docs/goal5838_generic_core_exam_20260902/"
        "POD_COMPATIBILITY_CORRECTION.md"
    ),
    (
        "history/internal_docs/goal5838_generic_core_exam_20260902/"
        "UNKNOWN_POD_COMPLETION_PLAN.md"
    ),
    (
        "history/internal_docs/goal5838_generic_core_exam_20260902/"
        "FIRST_POD_EXECUTION_REPAIR_LOG.md"
    ),
    "case_studies/goal5838_selected_sphere_any_hit_count/fixture.py",
    (
        "case_studies/goal5838_selected_sphere_any_hit_count/"
        "sphere_any_hit_count_oracle.py"
    ),
    "scripts/goal5838_build_selected_sphere_optix_provider.py",
    "scripts/goal5838_pod_preflight.py",
    "scripts/goal5838_run_selected_sphere_gpu_exam.py",
    "scripts/goal5838_verify_selected_sphere_gpu_exam.py",
    "src/native/rtdl_optix.cpp",
    "src/native/optix/rtdl_optix_api.cpp",
    "src/native/optix/rtdl_optix_core.cpp",
    "src/native/optix/rtdl_optix_cuda_helpers.cu",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/native/optix/rtdl_optix_v4_particle_template.h",
    "src/native/optix/rtdl_optix_v4_product_status.h",
    "src/native/optix/rtdl_optix_prelude.h",
    "src/native/optix/rtdl_optix_workloads.cpp",
    "src/rtdsl/physical_execution_provenance.py",
    "src/rtdsl/v4_family_route_adapters.py",
    "src/rtdsl/v4_public_sphere_any_hit_count.py",
    "src/rtdsl/v4_sphere_any_hit_count.py",
    "src/rtdsl/v4_sphere_any_hit_count_contract.py",
    "src/rtdsl/v4_sphere_any_hit_count_family_route.py",
    "src/rtdsl/v4_sphere_any_hit_count_numba_codegen.py",
    "src/rtdsl/v4_sphere_any_hit_count_optix_compiler.py",
    "src/rtdsl/v4_sphere_any_hit_count_prepared_runtime.py",
    "src/rtdsl/v4_sphere_any_hit_count_wrapper_codegen.py",
    "src/rtdsl/v4_sphere_optix_compiler.py",
    "src/rtdsl/v4_sphere_physical_schema.py",
    "src/rtdsl/v4_sphere_prepared_runtime.py",
    "tests/goal5838_selected_sphere_any_hit_count_test.py",
    "tests/goal5838_pod_preflight_test.py",
)
NATIVE_BUILD_RESULT_DOMAIN = (
    "rtdl.goal5838.selected_sphere_optix_provider_build.v2"
)
NATIVE_BUILD_SOURCE_PATHS = (
    "scripts/goal5838_build_selected_sphere_optix_provider.py",
    "src/native/rtdl_optix.cpp",
    "src/native/optix/rtdl_optix_prelude.h",
    "src/native/optix/rtdl_optix_core.cpp",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/native/optix/rtdl_optix_api.cpp",
    "src/native/optix/rtdl_optix_v4_particle_template.h",
    "src/native/optix/rtdl_optix_v4_product_status.h",
    "src/native/optix/rtdl_optix_workloads.cpp",
    "src/native/optix/rtdl_optix_cuda_helpers.cu",
)
NATIVE_BUILD_TRANSLATION_UNITS = (
    "src/native/rtdl_optix.cpp",
    "src/native/optix/rtdl_optix_cuda_helpers.cu",
)
NATIVE_BUILD_REQUIRED_SYMBOLS = (
    "rtdl_optix_get_version",
    "rtdl_optix_v4_runtime_compiler_attempt_count_v1",
    "rtdl_optix_v4_rtdlexe_producer_descriptor_v1",
    "rtdl_optix_traversal_audit_begin",
    "rtdl_optix_traversal_audit_finish",
    "rtdl_optix_traversal_audit_abort",
    "rtdl_optix_v4_prepare_builtin_sphere_callback_v1",
    "rtdl_optix_v4_execute_prepared_builtin_sphere_callback_v1",
    "rtdl_optix_v4_describe_prepared_builtin_sphere_callback_v1",
    "rtdl_optix_v4_destroy_prepared_builtin_sphere_callback_v1",
)
COMPILER_ENVIRONMENT_SCHEMA = "rtdl.goal5838.cuda_compiler_environment.v1"
COMPILER_FILE_ENVIRONMENT = (
    ("nvrtc", "RTDL_V4_NVRTC_LIBRARY"),
    ("nvvm", "NUMBA_CUDA_NVVM"),
    ("libdevice", "NUMBA_CUDA_LIBDEVICE"),
)
COMPILER_PREFIX_ENVIRONMENT = (
    ("CUDA_HOME", "cuda_prefix"),
    ("CUDA_PATH", "cuda_prefix"),
    ("RTDL_V4_CUDA_PREFIX", "cuda_prefix"),
    ("RTDL_V4_OPTIX_PREFIX", "optix_prefix"),
)
FORBIDDEN_COMPILER_ENVIRONMENT = (
    "RTDL_V4_FORMAL_LEAF_CACHE",
    "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST",
    "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256",
    "LD_PRELOAD",
    "NUMBA_ENABLE_CUDASIM",
    "NUMBA_FORCE_CUDA_CC",
    "NUMBA_CUDA_DEFAULT_PTX_CC",
    "NUMBA_CUDA_DRIVER",
)
NATIVE_LIBRARY_OVERRIDE_ENVIRONMENT = (
    "RTDL_OPTIX_LIB",
    "RTDL_OPTIX_LIBRARY",
)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_ldd_dependency(output: str, stem: str) -> Path:
    matches = []
    for line in output.splitlines():
        if "=>" not in line:
            continue
        name, resolution = (part.strip() for part in line.split("=>", 1))
        if name != stem and not name.startswith(stem + "."):
            continue
        path_text = resolution.split(maxsplit=1)[0]
        if path_text == "not":
            raise RuntimeError(f"dynamic dependency is unresolved: {line.strip()}")
        path = Path(path_text).resolve(strict=True)
        if not path.is_file():
            raise RuntimeError(f"dynamic dependency is not a file: {path}")
        matches.append(path)
    unique = tuple(dict.fromkeys(matches))
    if len(unique) != 1:
        raise RuntimeError(
            f"expected one resolved {stem} dependency, observed {unique!r}"
        )
    return unique[0]


def _resolved_environment_path(name: str, *, file: bool) -> Path:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"required compiler environment variable is absent: {name}")
    try:
        path = Path(value).expanduser().resolve(strict=True)
    except OSError as exc:
        raise RuntimeError(
            f"compiler environment path is unavailable: {name}={value}"
        ) from exc
    if file and not path.is_file():
        raise RuntimeError(f"compiler environment path is not a file: {name}={path}")
    if not file and not path.is_dir():
        raise RuntimeError(
            f"compiler environment path is not a directory: {name}={path}"
        )
    return path


def _capture_compiler_environment(
    native_build: dict[str, object],
    *,
    optix_include: Path,
    cuda_include: Path,
    native_override: Path | None,
) -> dict[str, object]:
    build_input = native_build.get("build_input")
    if not isinstance(build_input, dict):
        raise TypeError("native build input is absent from compiler custody")
    expected_optix_include = Path(str(build_input["optix_include"])).resolve(
        strict=True
    )
    expected_cuda_include = Path(str(build_input["cuda_include"])).resolve(
        strict=True
    )
    if (
        optix_include.resolve(strict=True) != expected_optix_include
        or cuda_include.resolve(strict=True) != expected_cuda_include
    ):
        raise RuntimeError("runtime include roots differ from the native build")

    prefixes: dict[str, str] = {}
    for environment_name, build_key in COMPILER_PREFIX_ENVIRONMENT:
        observed = _resolved_environment_path(environment_name, file=False)
        expected = Path(str(build_input[build_key])).resolve(strict=True)
        if observed != expected:
            raise RuntimeError(
                f"compiler prefix differs: {environment_name}={observed} != {expected}"
            )
        prefixes[environment_name] = str(observed)

    contaminated = [
        name for name in FORBIDDEN_COMPILER_ENVIRONMENT if name in os.environ
    ]
    if contaminated:
        raise RuntimeError(
            f"forbidden compiler environment is present: {contaminated}"
        )
    expected_native = None if native_override is None else native_override.resolve(
        strict=True
    )
    for name in NATIVE_LIBRARY_OVERRIDE_ENVIRONMENT:
        value = os.environ.get(name)
        if expected_native is None:
            if name in os.environ:
                raise RuntimeError(
                    f"native library override was present before runner setup: {name}"
                )
        elif not value or Path(value).expanduser().resolve(strict=True) != expected_native:
            raise RuntimeError(f"runner-owned native library override differs: {name}")

    files = []
    for label, environment_name in COMPILER_FILE_ENVIRONMENT:
        path = _resolved_environment_path(environment_name, file=True)
        row = {
            "label": label,
            "environment_variable": environment_name,
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": _file_sha256(path),
        }
        if label == "nvrtc" and (
            path
            != Path(str(build_input["nvrtc_library_path"])).resolve(strict=True)
            or row["bytes"] != build_input["nvrtc_library_bytes"]
            or row["sha256"] != build_input["nvrtc_library_sha256"]
        ):
            raise RuntimeError("runtime NVRTC differs from the native build input")
        files.append(row)
    result = {
        "schema": COMPILER_ENVIRONMENT_SCHEMA,
        "prefixes": prefixes,
        "compiler_files": files,
        "forbidden_environment_absent": list(FORBIDDEN_COMPILER_ENVIRONMENT),
    }
    result["identity_sha256"] = _digest(result)
    return result


def _sealed_document_sha256(
    document: dict[str, object], field: str, domain: str
) -> str:
    payload = dict(document)
    payload[field] = ""
    return hashlib.sha256(
        domain.encode("ascii") + b"\0" + _canonical_bytes(payload)
    ).hexdigest()


def _native_build_seal(document: dict[str, object]) -> str:
    payload = dict(document)
    payload["result_sha256"] = ""
    return hashlib.sha256(
        NATIVE_BUILD_RESULT_DOMAIN.encode("ascii")
        + b"\0"
        + _canonical_bytes(payload)
    ).hexdigest()


def _require_cuda_visibility() -> str:
    value = os.environ.get("CUDA_VISIBLE_DEVICES")
    if value != "0":
        raise RuntimeError(
            "Goal5838 requires CUDA_VISIBLE_DEVICES=0 so nvidia-smi and the "
            "native CUDA ordinal bind the same selected GPU"
        )
    return value


def _optix_sdk_number(value: str) -> int:
    match = re.fullmatch(
        (
            r"([1-9][0-9]?)\.((?:0|[1-9][0-9]?))\."
            r"((?:0|[1-9][0-9]?))"
        ),
        value,
    )
    if match is None:
        raise ValueError(f"invalid OptiX SDK version: {value!r}")
    major, minor, patch = (int(item) for item in match.groups())
    if major == 0 or minor >= 100 or patch >= 100:
        raise ValueError(f"invalid OptiX SDK version: {value!r}")
    return major * 10000 + minor * 100 + patch


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load independent module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _thaw(value):
    if isinstance(value, dict) or hasattr(value, "items"):
        return {str(key): _thaw(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_thaw(item) for item in value]
    return value


def _git(*arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            f"git {' '.join(arguments)} failed: {completed.stderr.strip()}"
        )
    return completed.stdout.strip()


def _git_bytes(*arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            f"git {' '.join(arguments)} failed: "
            f"{completed.stderr.decode('utf-8', errors='replace').strip()}"
        )
    return completed.stdout


def _repository_custody(expected_commit: str) -> dict[str, object]:
    if (
        len(expected_commit) != 40
        or any(char not in "0123456789abcdef" for char in expected_commit)
    ):
        raise RuntimeError("--expected-commit must be a full lowercase commit id")
    head = _git("rev-parse", "HEAD")
    resolved = _git("rev-parse", "--verify", f"{expected_commit}^{{commit}}")
    if head != expected_commit or resolved != expected_commit:
        raise RuntimeError(
            f"exam checkout differs from expected commit: {head} != {expected_commit}"
        )
    dirty = _git("status", "--porcelain=v1", "--untracked-files=all")
    if dirty:
        raise RuntimeError(f"exam requires a clean worktree before execution: {dirty}")
    rows = []
    for relative in EXAM_SOURCE_PATHS:
        working = (ROOT / relative).read_bytes()
        committed = _git_bytes("show", f"{head}:{relative}")
        if working != committed:
            raise RuntimeError(f"exam source differs from commit: {relative}")
        rows.append(
            {
                "path": relative,
                "bytes": len(working),
                "sha256": hashlib.sha256(working).hexdigest(),
            }
        )
    return {
        "expected_commit": expected_commit,
        "head_commit": head,
        "branch": _git("branch", "--show-current"),
        "origin_url": _git("remote", "get-url", "origin"),
        "clean_before_execution": True,
        "tracked_source_files": rows,
    }


def _finalize_repository_custody(
    repository: dict[str, object],
) -> dict[str, object]:
    expected_commit = str(repository["expected_commit"])
    head = _git("rev-parse", "HEAD")
    dirty = _git("status", "--porcelain=v1", "--untracked-files=all")
    if head != expected_commit or dirty:
        raise RuntimeError("exam Git identity changed during execution")
    expected_rows = repository["tracked_source_files"]
    observed_rows = []
    for relative in EXAM_SOURCE_PATHS:
        payload = (ROOT / relative).read_bytes()
        committed = _git_bytes("show", f"{head}:{relative}")
        if payload != committed:
            raise RuntimeError(f"exam source changed during execution: {relative}")
        observed_rows.append(
            {
                "path": relative,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    if observed_rows != expected_rows:
        raise RuntimeError("exam source inventory changed during execution")
    return {
        **repository,
        "head_after_execution": head,
        "clean_after_execution": True,
    }


def _require_external_output(path: Path) -> Path:
    output = path.expanduser().resolve()
    root = ROOT.resolve()
    if output == root or root in output.parents:
        raise ValueError(f"GPU exam output must be outside Git tree: {output}")
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def _write_json_exclusive(path: Path, value: object) -> None:
    descriptor, name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".partial", dir=path.parent
    )
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            raise FileExistsError(path) from None
    finally:
        temporary.unlink(missing_ok=True)


def _verify_native_build_manifest(
    path: Path,
    *,
    native: Path,
    expected_commit: str,
    compute_capability: str,
    optix_sdk: str,
    visible_gpu: dict[str, object],
) -> dict[str, object]:
    manifest_path = path.expanduser().resolve(strict=True)
    try:
        manifest = json.loads(manifest_path.read_text("utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError("native build manifest is invalid JSON") from exc
    if not isinstance(manifest, dict):
        raise TypeError("native build manifest root must be an object")
    if (
        manifest.get("schema") != NATIVE_BUILD_RESULT_DOMAIN
        or manifest.get("status")
        != "PASS__FRESH_PROVIDER_DSO_AND_REQUIRED_ABI_EXPORTED"
        or manifest.get("result_sha256") != _native_build_seal(manifest)
        or manifest.get("all_required_symbols_exported") is not True
        or manifest.get("required_symbols") != list(NATIVE_BUILD_REQUIRED_SYMBOLS)
        or manifest.get("required_symbol_check")
        != "exact_nm_dynamic_defined_name"
    ):
        raise RuntimeError("native build manifest envelope differs")
    repository = manifest.get("repository")
    if not isinstance(repository, dict):
        raise TypeError("native build manifest lacks repository custody")
    if (
        repository.get("expected_commit") != expected_commit
        or repository.get("head_before") != expected_commit
        or repository.get("head_after") != expected_commit
        or repository.get("clean_before") is not True
        or repository.get("clean_after") is not True
    ):
        raise RuntimeError("native build repository identity differs")
    source_rows = repository.get("source_files")
    if (
        not isinstance(source_rows, list)
        or [row.get("path") for row in source_rows if isinstance(row, dict)]
        != list(NATIVE_BUILD_SOURCE_PATHS)
    ):
        raise RuntimeError("native build source inventory differs")
    for row, relative in zip(
        source_rows, NATIVE_BUILD_SOURCE_PATHS, strict=True
    ):
        committed = _git_bytes("show", f"{expected_commit}:{relative}")
        if (
            not isinstance(row, dict)
            or row.get("path") != relative
            or row.get("bytes") != len(committed)
            or row.get("sha256")
            != hashlib.sha256(committed).hexdigest()
        ):
            raise RuntimeError(f"native build source row differs: {relative}")
    build_input = manifest.get("build_input")
    if not isinstance(build_input, dict):
        raise TypeError("native build input is absent")
    abi_probe = build_input.get("optix_runtime_abi_probe")
    if (
        manifest.get("build_input_sha256") != _digest(build_input)
        or build_input.get("translation_units")
        != list(NATIVE_BUILD_TRANSLATION_UNITS)
        or build_input.get("builder_path") != NATIVE_BUILD_SOURCE_PATHS[0]
        or build_input.get("expected_optix_sdk") != optix_sdk
        or build_input.get("optix_version") != _optix_sdk_number(optix_sdk)
        or build_input.get("compute_capability") != compute_capability
        or build_input.get("cuda_visible_devices") != "0"
        or build_input.get("language_standard") != "c++17"
        or build_input.get("optimization") != "O3"
        or build_input.get("position_independent_code") is not True
        or not isinstance(build_input.get("nvrtc_library_path"), str)
        or not build_input.get("nvrtc_library_path")
        or type(build_input.get("nvrtc_library_bytes")) is not int
        or build_input.get("nvrtc_library_bytes") <= 0
        or not isinstance(build_input.get("nvrtc_library_sha256"), str)
        or re.fullmatch(
            r"[0-9a-f]{64}", build_input["nvrtc_library_sha256"]
        )
        is None
        or not isinstance(abi_probe, dict)
        or abi_probe.get("passed") is not True
        or abi_probe.get("runtime_returncode") != 0
        or abi_probe.get("runtime_output") != "optixInit_result=0"
        or abi_probe.get("optix_launch_count") != 0
    ):
        raise RuntimeError("native build input identity differs")
    dynamic_dependencies = manifest.get("dynamic_dependencies")
    dynamic_nvrtc = manifest.get("dynamic_nvrtc")
    if (
        not isinstance(dynamic_dependencies, str)
        or not isinstance(dynamic_nvrtc, dict)
        or set(dynamic_nvrtc) != {"path", "bytes", "sha256"}
        or dynamic_nvrtc.get("path") != build_input.get("nvrtc_library_path")
        or dynamic_nvrtc.get("bytes") != build_input.get("nvrtc_library_bytes")
        or dynamic_nvrtc.get("sha256")
        != build_input.get("nvrtc_library_sha256")
    ):
        raise RuntimeError("native build dynamic NVRTC identity differs")
    ldd = subprocess.run(
        ["ldd", str(native)],
        text=True,
        capture_output=True,
        check=False,
    )
    if ldd.returncode:
        raise RuntimeError(f"ldd failed for execution DSO: {ldd.stderr.strip()}")
    resolved_nvrtc = _resolve_ldd_dependency(
        ldd.stdout + ldd.stderr, "libnvrtc.so"
    )
    if (
        resolved_nvrtc
        != Path(str(build_input["nvrtc_library_path"])).resolve(strict=True)
        or resolved_nvrtc.stat().st_size != build_input["nvrtc_library_bytes"]
        or _file_sha256(resolved_nvrtc) != build_input["nvrtc_library_sha256"]
    ):
        raise RuntimeError("execution DSO resolves a different NVRTC file")
    build_gpu = build_input.get("gpu")
    if not isinstance(build_gpu, dict) or any(
        build_gpu.get(field) != visible_gpu.get(field)
        for field in ("name", "uuid", "driver_version", "compute_capability")
    ):
        raise RuntimeError("native build GPU differs from execution GPU")
    native_output = manifest.get("native_output")
    native_bytes = native.read_bytes()
    if (
        not isinstance(native_output, dict)
        or Path(str(native_output.get("path"))).resolve() != native
        or native_output.get("bytes") != len(native_bytes)
        or native_output.get("sha256")
        != hashlib.sha256(native_bytes).hexdigest()
    ):
        raise RuntimeError("native build output differs from execution DSO")
    return manifest


def _verify_selection() -> dict[str, object]:
    selection = json.loads(SELECTION.read_text("utf-8"))
    if (
        selection.get("selection_result_sha256") != SELECTION_RESULT_SHA256
        or _sealed_document_sha256(
            selection,
            "selection_result_sha256",
            "rtdl.goal5838.challenge_selection_result.v1",
        )
        != SELECTION_RESULT_SHA256
        or selection.get("challenge_table_sha256") != CHALLENGE_TABLE_SHA256
        or selection.get("generic_core_seal_sha256")
        != GENERIC_CORE_SEAL_SHA256
        or selection.get("target_pulse", {}).get("local_random_value")
        != TARGET_LOCAL_RANDOM_VALUE
        or selection.get("mapping", {}).get("selected_index") != 3
        or selection.get("selected_candidate", {}).get("candidate_id")
        != SELECTED_CANDIDATE_ID
        or selection.get("selected_candidate", {}).get("metadata_channels") != []
        or selection.get("selected_candidate", {}).get(
            "true_gpu_receipt_required"
        )
        is not True
        or selection.get("activity_at_selection")
        != {
            "candidate_execution_count": 0,
            "candidate_implementation_count": 0,
            "gpu_receipt_count": 0,
            "prospective_success_count": 0,
        }
    ):
        raise RuntimeError("stored Goal5838 selection authority differs")
    return selection


def _nvidia_smi() -> dict[str, object]:
    query = (
        "name,uuid,driver_version,pci.bus_id,compute_cap,"
        "memory.total"
    )
    completed = subprocess.run(
        [
            "nvidia-smi",
            "--id=0",
            f"--query-gpu={query}",
            "--format=csv,noheader,nounits",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(f"nvidia-smi failed: {completed.stderr.strip()}")
    rows = [
        [part.strip() for part in line.split(",")]
        for line in completed.stdout.splitlines()
        if line.strip()
    ]
    if len(rows) != 1 or len(rows[0]) != 6:
        raise RuntimeError(f"selected NVIDIA GPU query differs: {rows!r}")
    fields = (
        "name",
        "uuid",
        "driver_version",
        "pci_bus_id",
        "compute_capability",
        "memory_mib",
    )
    return dict(zip(fields, rows[0], strict=True))


def _verify_frozen_core() -> dict[str, object]:
    seal = json.loads(SEAL.read_text("utf-8"))
    if (
        seal.get("seal_sha256") != GENERIC_CORE_SEAL_SHA256
        or _sealed_document_sha256(
            seal,
            "seal_sha256",
            "rtdl.goal5838.generic_core_seal.v1",
        )
        != GENERIC_CORE_SEAL_SHA256
        or seal.get("challenge_table", {}).get("authority_sha256")
        != CHALLENGE_TABLE_SHA256
    ):
        raise RuntimeError("stored Goal5838 generic-core seal differs")
    observed = []
    for row in seal["frozen_core_files"]:
        path = ROOT / row["path"]
        digest = _file_sha256(path)
        if digest != row["sha256"]:
            raise RuntimeError(f"frozen core changed: {row['path']}")
        observed.append(
            {
                "path": row["path"],
                "bytes": path.stat().st_size,
                "sha256": digest,
            }
        )
    return {
        "generic_core_seal_sha256": seal["seal_sha256"],
        "files": observed,
        "changed_file_count": 0,
    }


def _require_true_optix(receipt: dict[str, object]) -> None:
    if receipt.get("physical_executor_classification") != (
        "optix_traversal_observed"
    ):
        raise RuntimeError("execution receipt is not true OptiX traversal")
    if receipt.get("selected_topology") != (
        "builtin_sphere::any_hit_count_continue_u64_per_query"
    ):
        raise RuntimeError("execution receipt selected topology differs")
    physical = receipt.get("physical_receipt")
    if not isinstance(physical, dict):
        raise TypeError("execution receipt lacks physical receipt")
    descriptor = physical.get("native_descriptor")
    if (
        physical.get("build_input_type_name")
        != "OPTIX_BUILD_INPUT_TYPE_SPHERES"
        or physical.get("continuation_name") != "optixIgnoreIntersection"
        or not isinstance(descriptor, dict)
        or descriptor.get("builtin_is_module") is not True
        or descriptor.get("user_intersection_program") is not False
        or descriptor.get("gas_count") != 1
        or descriptor.get("sbt_record_count") != 1
    ):
        raise RuntimeError("execution physical sphere contract differs")


def run(args: argparse.Namespace) -> dict[str, object]:
    cuda_visible_devices = _require_cuda_visibility()
    repository = _repository_custody(args.expected_commit)
    frozen = _verify_frozen_core()
    selection = _verify_selection()
    selected_id = selection["selected_candidate"]["candidate_id"]
    if selected_id != SELECTED_CANDIDATE_ID:
        raise RuntimeError(f"unexpected selected candidate: {selected_id}")
    oracle = _load_module(
        "goal5838_independent_sphere_count_oracle",
        CASE_ROOT / "sphere_any_hit_count_oracle.py",
    )
    fixture_module = _load_module(
        "goal5838_selected_sphere_count_fixture", CASE_ROOT / "fixture.py"
    )
    fixture = fixture_module.selected_exam_fixture()
    expected = oracle.count_batch(
        fixture["queries"], fixture["centers"], fixture["radii"]
    )
    reverse_queries = tuple(reversed(fixture["queries"]))
    reverse_expected = tuple(reversed(expected))

    native = args.native.resolve(strict=True)
    visible_gpu = _nvidia_smi()
    native_build = _verify_native_build_manifest(
        args.native_build_manifest,
        native=native,
        expected_commit=args.expected_commit,
        compute_capability=args.compute_capability,
        optix_sdk=args.optix_sdk,
        visible_gpu=visible_gpu,
    )
    compiler_environment = _capture_compiler_environment(
        native_build,
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
        native_override=None,
    )
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    target = V4SphereTarget.from_native(
        native,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
    )
    capability = tuple(
        int(item) for item in args.compute_capability.split(".")
    )
    if len(capability) != 2:
        raise RuntimeError("compute capability must have two components")
    toolchain = V4Toolchain.current(
        compute_capability=capability,
        optix_include=args.optix_include.resolve(strict=True),
        cuda_include=args.cuda_include.resolve(strict=True),
    )
    route = sphere_any_hit_count_family_route()
    program = route.compile()
    materialized = program.materialize(target=target, toolchain=toolchain)
    identity = materialized.identity.to_dict()
    prepared = materialized.prepare(
        SphereAnyHitCountStaticInput(fixture["centers"], fixture["radii"])
    )
    try:
        lifecycle_before = _thaw(prepared.lifecycle_receipt)
        primary = prepared.execute(MotionSegmentBatch(fixture["queries"]))
        primary_output = tuple(int(item) for item in primary.output["counts"])
        if primary_output != expected:
            raise RuntimeError(
                f"primary oracle mismatch: {primary_output} != {expected}"
            )
        primary_receipt = _thaw(primary.traversal_receipt)
        _require_true_optix(primary_receipt)
        lifecycle_middle = _thaw(prepared.lifecycle_receipt)
        reverse = prepared.execute(MotionSegmentBatch(reverse_queries))
        reverse_output = tuple(int(item) for item in reverse.output["counts"])
        if reverse_output != reverse_expected:
            raise RuntimeError(
                f"reverse oracle mismatch: {reverse_output} != {reverse_expected}"
            )
        reverse_receipt = _thaw(reverse.traversal_receipt)
        _require_true_optix(reverse_receipt)
        lifecycle_after = _thaw(prepared.lifecycle_receipt)
    finally:
        prepared.close()
        prepared.close()

    compiler_environment_after = _capture_compiler_environment(
        native_build,
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
        native_override=native,
    )
    if compiler_environment_after != compiler_environment:
        raise RuntimeError("compiler environment changed during GPU execution")

    repository = _finalize_repository_custody(repository)

    result = {
        "schema": "rtdl.goal5838.selected_sphere_gpu_exam.v1",
        "status": "PASS__BOUNDED_PROSPECTIVE_FROZEN_CORE_TOPOLOGY",
        "claim_boundary": {
            "one_bounded_prospective_result": True,
            "arbitrary_callback_ir_gpu_execution": False,
            "universal_provider_portability": False,
            "performance_or_speedup": False,
            "external_review_or_consensus": False,
        },
        "selection": {
            "candidate_id": selected_id,
            "selection_result_sha256": selection["selection_result_sha256"],
            "selection_file_sha256": _file_sha256(SELECTION),
            "selected_index": selection["mapping"]["selected_index"],
            "target_pulse_index": selection["target_pulse"]["pulse_index"],
            "target_local_random_value": selection["target_pulse"][
                "local_random_value"
            ],
        },
        "repository": repository,
        "frozen_core": frozen,
        "native_build": native_build,
        "target": {
            "profile_sha256": target.profile.target_sha256,
            "native_library_path": str(native),
            "native_library_sha256": _file_sha256(native),
            "native_library_bytes": native.stat().st_size,
            "optix_sdk": args.optix_sdk,
            "compute_capability": args.compute_capability,
            "gpu": visible_gpu,
        },
        "toolchain": {
            "python": platform.python_version(),
            "python_executable": os.path.abspath(sys.executable),
            "numba": importlib.metadata.version("numba"),
            "numpy": importlib.metadata.version("numpy"),
            "optix_include": str(args.optix_include.resolve()),
            "cuda_include": str(args.cuda_include.resolve()),
            "cuda_visible_devices": cuda_visible_devices,
            "compiler_environment": compiler_environment,
            "native_library_overrides": {
                name: str(native) for name in NATIVE_LIBRARY_OVERRIDE_ENVIRONMENT
            },
        },
        "generic_family": {
            "classification": route.classification,
            "plan_sha256": route.plan.plan_sha256,
            "provider_descriptor_sha256": (
                route.provider.descriptor.descriptor_sha256
            ),
            "provider_projection_sha256": (
                program.provider_projection.projection_sha256
            ),
            "executable_identity": identity,
        },
        "fixture": {
            "case_names": list(fixture["case_names"]),
            "primitive_count": len(fixture["centers"]),
            "query_count": len(fixture["queries"]),
            "expected_counts": list(expected),
            "fixture_sha256": _digest(fixture),
            "oracle_sha256": _file_sha256(
                CASE_ROOT / "sphere_any_hit_count_oracle.py"
            ),
        },
        "executions": [
            {
                "label": "primary",
                "observed_counts": list(primary_output),
                "output_sha256": primary.output_sha256,
                "oracle_exact_match": True,
                "traversal_receipt": primary_receipt,
            },
            {
                "label": "reverse_query_order",
                "observed_counts": list(reverse_output),
                "output_sha256": reverse.output_sha256,
                "oracle_exact_match": True,
                "traversal_receipt": reverse_receipt,
            },
        ],
        "lifecycle": {
            "before": lifecycle_before,
            "after_primary": lifecycle_middle,
            "after_reverse": lifecycle_after,
            "execution_count": 2,
            "closed_idempotently": True,
        },
        "summary": {
            "true_optix_launch_count": 2,
            "oracle_case_count": len(expected) * 2,
            "oracle_exact_match_count": len(expected) * 2,
            "frozen_core_changed_file_count": 0,
        },
    }
    result["result_sha256"] = _digest(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--native-build-manifest", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = _require_external_output(args.output)
    result = run(args)
    _write_json_exclusive(output, result)
    print(json.dumps(result["summary"], sort_keys=True))
    print(f"result_sha256={result['result_sha256']}")
    print(f"output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
