#!/usr/bin/env python3
"""Audit a pod before the frozen Goal5838 GPU exam.

This script performs no native build and no GPU launch.  A failed check is a
repairable environment/readiness result, never a scientific Goal5838 failure.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from scripts.goal5838_build_selected_sphere_optix_provider import (
    OPTIX_RUNTIME_ABI_PROBE_SOURCE as _OPTIX_RUNTIME_ABI_PROBE_SOURCE,
)
from scripts.goal5838_build_selected_sphere_optix_provider import (
    probe_optix_runtime_abi,
)

OPTIX_RUNTIME_ABI_PROBE_SOURCE = _OPTIX_RUNTIME_ABI_PROBE_SOURCE

ROOT = Path(__file__).resolve().parents[1]
BASELINE_COMMIT = "0f5c9d4297f73e412732e5a8ab133423fe4cfd21"
KNOWN_OPTIX_DEV_RELEASES = {
    "7.7.0": "7b5c4e8608b8b4b601729f6240fc3fd53cb36d23",
    "8.0.0": "f60c1e44f18426f426a2ed948f28515b3cf67b8a",
    "8.1.0": "50021ea0af6d41609a97777ceebbdf1e1d34efe7",
    "9.0.0": "fff65c2a7c592f1ea5f1661ad7d2381cf965f9bd",
    "9.1.0": "f1f6dd803f3159992d248178f6e09421c6eb8b6d",
}
EXPECTED_PACKAGE_VERSIONS = {"numba": "0.65.1", "numpy": "2.4.4"}
FOCUSED_TEST_MODULES = (
    "tests.goal5838_preregistration_test",
    "tests.goal5838_generic_family_lifecycle_test",
    "tests.goal5838_core_seal_and_selection_test",
    "tests.goal5838_family_route_migration_test",
    "tests.goal5838_selected_sphere_any_hit_count_test",
    "tests.goal5838_pod_preflight_test",
)
OPTIX_HEADERS = (
    "optix.h",
    "optix_device.h",
    "optix_function_table_definition.h",
    "optix_stack_size.h",
    "optix_stubs.h",
)
CUDA_HEADERS = ("cuda.h", "cuda_runtime.h", "nvrtc.h")
CALLBACK_ROLES = ("make_ray", "any_hit", "miss", "finalize")
FORMAL_CACHE_ENV = (
    "RTDL_V4_FORMAL_LEAF_CACHE",
    "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST",
    "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256",
)
CLEARED_AMBIENT_ENV = FORMAL_CACHE_ENV + (
    "LD_PRELOAD",
    "NUMBA_ENABLE_CUDASIM",
    "NUMBA_FORCE_CUDA_CC",
    "NUMBA_CUDA_DEFAULT_PTX_CC",
    "NUMBA_CUDA_DRIVER",
    "RTDL_V4_NVRTC_LIBRARY",
    "RTDL_OPTIX_LIB",
    "RTDL_OPTIX_LIBRARY",
)
INTERNAL_CALLBACK_PROBE = "--internal-callback-compile-probe"
RESULT_DOMAIN = "rtdl.goal5838.pod_preflight.v2"
PASS_STATUS = (
    "PASS__GOAL5838_POD_READY_FOR_FROZEN_GPU_EXAM"
    "__NO_GPU_EXECUTION_CLAIM"
)
REPAIR_STATUS = (
    "REPAIR_REQUIRED__GOAL5838_POD_ENVIRONMENT_NOT_READY"
    "__NOT_SCIENTIFIC_FAILURE"
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
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _first_file(
    explicit: Path | None,
    candidates: tuple[Path, ...],
    globs: tuple[tuple[Path, str], ...],
    *,
    label: str,
) -> Path:
    if explicit is not None:
        resolved = explicit.expanduser().resolve(strict=True)
        if not resolved.is_file():
            raise FileNotFoundError(resolved)
        return resolved
    observed: list[Path] = []
    for candidate in candidates:
        if candidate.is_file():
            observed.append(candidate.resolve(strict=True))
    for root, pattern in globs:
        if root.is_dir():
            observed.extend(
                path.resolve(strict=True)
                for path in sorted(root.glob(pattern))
                if path.is_file()
            )
    unique = tuple(dict.fromkeys(observed))
    if not unique:
        raise FileNotFoundError(f"{label} was not found; pass its exact path")
    return unique[0]


def resolve_cuda_compiler_files(
    cuda_prefix: Path,
    *,
    nvrtc_library: Path | None = None,
    nvvm_library: Path | None = None,
    libdevice: Path | None = None,
) -> dict[str, Path]:
    """Resolve the exact offline CUDA compiler inputs used by Callback IR."""

    cuda = cuda_prefix.expanduser().resolve(strict=True)
    if not cuda.is_dir():
        raise NotADirectoryError(cuda)
    library_roots = (
        cuda / "lib64",
        cuda / "targets/x86_64-linux/lib",
        Path("/usr/lib/x86_64-linux-gnu"),
    )
    nvvm_roots = (
        cuda / "nvvm/lib64",
        Path("/usr/lib/x86_64-linux-gnu"),
    )
    return {
        "nvrtc_library": _first_file(
            nvrtc_library,
            tuple(
                root / name
                for root in library_roots
                for name in ("libnvrtc.so.12", "libnvrtc.so")
            ),
            tuple((root, "libnvrtc.so*") for root in library_roots),
            label="NVRTC shared library",
        ),
        "nvvm_library": _first_file(
            nvvm_library,
            tuple(root / "libnvvm.so" for root in nvvm_roots),
            tuple((root, "libnvvm.so*") for root in nvvm_roots),
            label="NVVM shared library",
        ),
        "libdevice": _first_file(
            libdevice,
            (cuda / "nvvm/libdevice/libdevice.10.bc",),
            ((cuda / "nvvm/libdevice", "libdevice*.bc"),),
            label="CUDA libdevice bitcode",
        ),
    }


def configured_cuda_environment(
    cuda_prefix: Path,
    optix_prefix: Path,
    compiler_files: dict[str, Path],
    *,
    base: dict[str, str] | None = None,
) -> tuple[dict[str, str], dict[str, object]]:
    """Build a clean, reproducible compiler environment for child processes."""

    cuda = cuda_prefix.expanduser().resolve(strict=True)
    optix = optix_prefix.expanduser().resolve(strict=True)
    environment = dict(os.environ if base is None else base)
    library_dirs = tuple(
        dict.fromkeys(
            str(path)
            for path in (
                compiler_files["nvrtc_library"].parent,
                compiler_files["nvvm_library"].parent,
                cuda / "lib64",
                cuda / "targets/x86_64-linux/lib",
                Path("/usr/lib/x86_64-linux-gnu"),
            )
            if path.is_dir()
        )
    )
    path_dirs = (str(cuda / "bin"),)
    old_library_path = tuple(
        filter(None, environment.get("LD_LIBRARY_PATH", "").split(os.pathsep))
    )
    old_path = tuple(filter(None, environment.get("PATH", "").split(os.pathsep)))
    for name in CLEARED_AMBIENT_ENV:
        environment.pop(name, None)
    environment.update(
        {
            "CUDA_VISIBLE_DEVICES": "0",
            "LD_LIBRARY_PATH": os.pathsep.join(
                tuple(dict.fromkeys(library_dirs + old_library_path))
            ),
            "PATH": os.pathsep.join(tuple(dict.fromkeys(path_dirs + old_path))),
            "NUMBA_CUDA_NVVM": str(compiler_files["nvvm_library"]),
            "NUMBA_CUDA_LIBDEVICE": str(compiler_files["libdevice"]),
            "CUDA_HOME": str(cuda),
            "CUDA_PATH": str(cuda),
            "RTDL_V4_CUDA_PREFIX": str(cuda),
            "RTDL_V4_OPTIX_PREFIX": str(optix),
            "RTDL_V4_NVRTC_LIBRARY": str(
                compiler_files["nvrtc_library"]
            ),
            "PYTHONPATH": "src:.",
        }
    )
    identity = {
        "cuda_prefix": str(cuda),
        "optix_prefix": str(optix),
        "nvrtc_library": str(compiler_files["nvrtc_library"]),
        "nvrtc_sha256": _file_sha256(compiler_files["nvrtc_library"]),
        "nvvm_library": str(compiler_files["nvvm_library"]),
        "nvvm_sha256": _file_sha256(compiler_files["nvvm_library"]),
        "libdevice": str(compiler_files["libdevice"]),
        "libdevice_sha256": _file_sha256(compiler_files["libdevice"]),
        "ld_library_path_prefix": list(library_dirs),
        "path_prefix": list(path_dirs),
        "formal_numba_cache_disabled": True,
        "cleared_ambient_environment": list(CLEARED_AMBIENT_ENV),
    }
    identity["environment_sha256"] = _digest(identity)
    return environment, identity


def _require_full_commit(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("--expected-commit must be a full lowercase commit id")
    return value


def _parse_driver_major(value: str) -> int:
    match = re.fullmatch(r"([0-9]+)(?:\.[0-9]+)+", value.strip())
    if match is None:
        raise ValueError(f"invalid NVIDIA driver version: {value!r}")
    return int(match.group(1))


def _parse_compute_capability(value: str) -> tuple[int, int]:
    match = re.fullmatch(
        r"([1-9][0-9]?)\.((?:0|[1-9][0-9]?))", value.strip()
    )
    if match is None:
        raise ValueError(f"invalid compute capability: {value!r}")
    major, minor = (int(part) for part in match.groups())
    if major == 0:
        raise ValueError(f"invalid compute capability: {value!r}")
    return major, minor


def _normalize_compute_capability_row(value: object) -> tuple[int, int]:
    if (
        not isinstance(value, list)
        or len(value) != 2
        or any(type(item) is not int for item in value)
        or value[0] <= 0
        or value[1] < 0
        or any(item > 99 for item in value)
    ):
        raise ValueError("internal callback compute capability differs")
    return value[0], value[1]


def _parse_gpu_rows(output: str) -> list[dict[str, str]]:
    fields = ("name", "uuid", "driver_version", "compute_capability")
    result = []
    for raw_row in output.splitlines():
        if not raw_row.strip():
            continue
        values = tuple(part.strip() for part in raw_row.split(","))
        if len(values) != len(fields) or any(not value for value in values):
            raise ValueError(f"unexpected nvidia-smi row: {raw_row!r}")
        row = dict(zip(fields, values, strict=True))
        _parse_driver_major(row["driver_version"])
        _parse_compute_capability(row["compute_capability"])
        result.append(row)
    return result


def _parse_optix_version(path: Path) -> int:
    match = re.search(
        r"^\s*#\s*define\s+OPTIX_VERSION\s+([0-9]+)\s*$",
        path.read_text(encoding="utf-8", errors="strict"),
        re.MULTILINE,
    )
    if match is None:
        raise ValueError(f"OPTIX_VERSION is absent from {path}")
    return int(match.group(1))


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
    major, minor, patch = (int(part) for part in match.groups())
    if major == 0 or minor >= 100 or patch >= 100:
        raise ValueError(f"invalid OptiX SDK version: {value!r}")
    return major * 10000 + minor * 100 + patch


def _capture(
    command: list[str],
    *,
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
) -> dict[str, object]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        return {
            "command": command,
            "command_display": shlex.join(command),
            "returncode": completed.returncode,
            "output_tail": completed.stdout[-12000:],
        }
    except OSError as exc:
        return {
            "command": command,
            "command_display": shlex.join(command),
            "returncode": -1,
            "output_tail": f"{type(exc).__name__}: {exc}",
        }


def _check(
    rows: list[dict[str, object]],
    name: str,
    passed: bool,
    *,
    requirement: str,
    observed: object,
    repair: str,
    required: bool = True,
) -> None:
    rows.append(
        {
            "name": name,
            "required": required,
            "passed": bool(passed),
            "requirement": requirement,
            "observed": observed,
            "repair": "" if passed else repair,
        }
    )


def _external_path(path: Path, *, root: Path = ROOT) -> Path:
    result = path.expanduser().resolve()
    repository = root.resolve()
    if result == repository or repository in result.parents:
        raise ValueError(f"preflight/evidence path must be outside Git tree: {result}")
    return result


def _write_json_exclusive(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


def _compile_selected_callback_stack(request: dict[str, object]) -> dict[str, object]:
    """Compile the selected route without loading native code or launching OptiX."""

    expected_keys = {
        "compute_capability",
        "cuda_include",
        "expected_numba_version",
        "expected_numpy_version",
        "expected_python_version",
        "optix_include",
        "optix_sdk",
    }
    if set(request) != expected_keys:
        raise ValueError("internal callback compile request differs")
    capability = _normalize_compute_capability_row(request["compute_capability"])
    optix_sdk = str(request["optix_sdk"])
    _optix_sdk_number(optix_sdk)
    optix_include = Path(str(request["optix_include"])).resolve(strict=True)
    cuda_include = Path(str(request["cuda_include"])).resolve(strict=True)

    for import_root in (ROOT / "src", ROOT):
        if str(import_root) not in sys.path:
            sys.path.insert(0, str(import_root))
    from rtdsl.v4_callback_lifecycle import V4Toolchain
    from rtdsl.v4_public_builtin_sphere import V4SphereTarget
    from rtdsl.v4_sphere_any_hit_count_family_route import (
        sphere_any_hit_count_family_route,
    )

    with tempfile.TemporaryDirectory(
        prefix="rtdl-goal5838-callback-preflight-"
    ) as name:
        native = Path(name) / "not_loaded_native_identity.bin"
        native.write_bytes(
            b"Goal5838 callback compiler preflight; never loaded or executed\n"
        )
        target = V4SphereTarget.from_native(
            native,
            optix_sdk=optix_sdk,
            compute_capability=f"{capability[0]}.{capability[1]}",
        )
        toolchain = V4Toolchain(
            capability,
            optix_include,
            cuda_include,
            str(request["expected_python_version"]),
            str(request["expected_numba_version"]),
            str(request["expected_numpy_version"]),
        )
        route = sphere_any_hit_count_family_route()
        program = route.compile()
        shape = route.plan.to_dict()["family_shape"]
        roles = tuple(row["role"] for row in shape["callback"]["roles"])
        if roles != CALLBACK_ROLES:
            raise RuntimeError("selected callback role topology differs")
        materialized = program.materialize(target=target, toolchain=toolchain)
        identity = materialized.identity.to_dict()
        if materialized.state != "materialized":
            raise RuntimeError("callback preflight crossed the prepare boundary")
    return {
        "schema": "rtdl.goal5838.selected_callback_compile_probe.v1",
        "classification": route.classification,
        "provider_id": route.provider.descriptor.provider_id,
        "callback_roles": list(roles),
        "plan_sha256": route.plan.plan_sha256,
        "provider_descriptor_sha256": (
            route.provider.descriptor.descriptor_sha256
        ),
        "provider_projection_sha256": (
            program.provider_projection.projection_sha256
        ),
        "executable_identity": identity,
        "optix_sdk": optix_sdk,
        "compute_capability": list(capability),
        "compiled_through_generic_family_front_door": True,
        "native_prepare_called": False,
        "native_library_loaded": False,
        "gpu_execution_performed": False,
        "optix_launch_count": 0,
    }


def _callback_probe_receipt_passes(
    receipt: object,
    *,
    optix_sdk: str,
    compute_capability: tuple[int, int],
) -> bool:
    if not isinstance(receipt, dict):
        return False
    identity = receipt.get("executable_identity")
    hashes = (
        "identity_sha256",
        "provider_descriptor_sha256",
        "provider_projection_sha256",
        "plan_sha256",
        "target_sha256",
        "executable_sha256",
        "provider_artifact_sha256",
        "generated_artifact_sha256",
    )
    return (
        receipt.get("schema")
        == "rtdl.goal5838.selected_callback_compile_probe.v1"
        and receipt.get("classification") == "prospective_selected_extension"
        and receipt.get("provider_id")
        == "rtdl.optix.builtin_sphere_any_hit_count"
        and receipt.get("callback_roles") == list(CALLBACK_ROLES)
        and receipt.get("optix_sdk") == optix_sdk
        and receipt.get("compute_capability") == list(compute_capability)
        and receipt.get("compiled_through_generic_family_front_door") is True
        and receipt.get("native_prepare_called") is False
        and receipt.get("native_library_loaded") is False
        and receipt.get("gpu_execution_performed") is False
        and receipt.get("optix_launch_count") == 0
        and isinstance(identity, dict)
        and all(
            isinstance(identity.get(name), str)
            and re.fullmatch(r"[0-9a-f]{64}", identity[name]) is not None
            for name in hashes
        )
        and receipt.get("plan_sha256") == identity.get("plan_sha256")
        and receipt.get("provider_descriptor_sha256")
        == identity.get("provider_descriptor_sha256")
        and receipt.get("provider_projection_sha256")
        == identity.get("provider_projection_sha256")
    )


def _probe_selected_callback_compiler(
    *,
    python: Path,
    environment: dict[str, str],
    optix_sdk: str,
    compute_capability: tuple[int, int],
    optix_include: Path,
    cuda_include: Path,
    package_versions: dict[str, str | None],
) -> dict[str, object]:
    request = {
        "compute_capability": list(compute_capability),
        "cuda_include": str(cuda_include),
        "expected_numba_version": package_versions["numba"],
        "expected_numpy_version": package_versions["numpy"],
        "expected_python_version": platform.python_version(),
        "optix_include": str(optix_include),
        "optix_sdk": optix_sdk,
    }
    with tempfile.TemporaryDirectory(
        prefix="rtdl-goal5838-callback-probe-parent-"
    ) as name:
        directory = Path(name)
        request_path = directory / "request.json"
        output_path = directory / "result.json"
        request_path.write_text(
            json.dumps(request, sort_keys=True), encoding="utf-8", newline="\n"
        )
        command = [
            str(python),
            str(Path(__file__).resolve()),
            INTERNAL_CALLBACK_PROBE,
            str(request_path),
            str(output_path),
        ]
        process = _capture(command, env=environment)
        receipt = None
        parse_error = None
        if process["returncode"] == 0 and output_path.is_file():
            try:
                receipt = json.loads(output_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                parse_error = f"{type(exc).__name__}: {exc}"
        passed = (
            process["returncode"] == 0
            and _callback_probe_receipt_passes(
                receipt,
                optix_sdk=optix_sdk,
                compute_capability=compute_capability,
            )
        )
        command_template = [
            "<temporary>/request.json" if item == str(request_path) else
            "<temporary>/result.json" if item == str(output_path) else item
            for item in command
        ]
        return {
            "passed": passed,
            "command_template": command_template,
            "returncode": process["returncode"],
            "output_tail": process["output_tail"],
            "parse_error": parse_error,
            "request": request,
            "request_sha256": _digest(request),
            "receipt": receipt,
            "receipt_sha256": None if receipt is None else _digest(receipt),
            "native_prepare_called": False,
            "gpu_execution_performed": False,
            "optix_launch_count": 0,
        }


def _discover_host_compiler(requested: Path | None) -> Path | None:
    if requested is not None:
        candidate = requested.expanduser().resolve()
        return candidate if candidate.is_file() and os.access(candidate, os.X_OK) else None
    for name in ("g++-13", "g++-12", "g++-11", "g++"):
        candidate = shutil.which(name)
        if candidate is not None:
            return Path(candidate).resolve()
    return None


def _header_inventory(
    include: Path, names: tuple[str, ...]
) -> list[dict[str, object]]:
    rows = []
    for name in names:
        path = include / name
        if path.is_file():
            rows.append(
                {
                    "name": name,
                    "path": str(path.resolve()),
                    "bytes": path.stat().st_size,
                    "sha256": _file_sha256(path),
                }
            )
    return rows


def _artifact_paths(directory: Path) -> dict[str, Path]:
    return {
        "native": directory / "librtdl_optix_goal5838.so",
        "native_build_manifest": directory / "goal5838_native_build.json",
        "native_build_log": directory / "goal5838_native_build.log",
        "gpu_exam": directory / "goal5838_gpu_exam.json",
        "verification": directory / "goal5838_gpu_exam_verification.json",
    }


def _require_distinct_receipt(
    output: Path, artifacts: dict[str, Path]
) -> None:
    if output in artifacts.values():
        raise ValueError("preflight receipt must differ from generated artifacts")


def _command_plan(
    *,
    python: Path,
    cuda_prefix: Path,
    optix_prefix: Path,
    host_compiler: Path,
    optix_sdk: str,
    compute_capability: str,
    expected_commit: str,
    artifacts: dict[str, Path],
    compiler_environment: dict[str, str],
) -> dict[str, dict[str, object]]:
    environment_names = (
        "CUDA_VISIBLE_DEVICES",
        "LD_LIBRARY_PATH",
        "PATH",
        "NUMBA_CUDA_NVVM",
        "NUMBA_CUDA_LIBDEVICE",
        "CUDA_HOME",
        "CUDA_PATH",
        "RTDL_V4_CUDA_PREFIX",
        "RTDL_V4_OPTIX_PREFIX",
        "RTDL_V4_NVRTC_LIBRARY",
        "PYTHONPATH",
    )
    prefix = [
        "env",
        *(
            item
            for name in CLEARED_AMBIENT_ENV
            for item in ("-u", name)
        ),
        *(f"{name}={compiler_environment[name]}" for name in environment_names),
        str(python),
    ]
    build = [
        *prefix,
        "scripts/goal5838_build_selected_sphere_optix_provider.py",
        "--cuda-prefix",
        str(cuda_prefix),
        "--optix-prefix",
        str(optix_prefix),
        "--expected-optix-sdk",
        optix_sdk,
        "--compute-capability",
        compute_capability,
        "--host-compiler",
        str(host_compiler),
        "--nvrtc-library",
        compiler_environment["RTDL_V4_NVRTC_LIBRARY"],
        "--expected-commit",
        expected_commit,
        "--output",
        str(artifacts["native"]),
        "--manifest",
        str(artifacts["native_build_manifest"]),
        "--log",
        str(artifacts["native_build_log"]),
    ]
    run = [
        *prefix,
        "scripts/goal5838_run_selected_sphere_gpu_exam.py",
        "--native",
        str(artifacts["native"]),
        "--native-build-manifest",
        str(artifacts["native_build_manifest"]),
        "--optix-include",
        str(optix_prefix / "include"),
        "--cuda-include",
        str(cuda_prefix / "include"),
        "--optix-sdk",
        optix_sdk,
        "--compute-capability",
        compute_capability,
        "--expected-commit",
        expected_commit,
        "--output",
        str(artifacts["gpu_exam"]),
    ]
    verify = [
        str(python),
        "scripts/goal5838_verify_selected_sphere_gpu_exam.py",
        "--artifact",
        str(artifacts["gpu_exam"]),
        "--native",
        str(artifacts["native"]),
        "--output",
        str(artifacts["verification"]),
    ]
    return {
        name: {"argv": command, "display": shlex.join(command)}
        for name, command in (("build", build), ("run", run), ("verify", verify))
    }


def _git_probe(*arguments: str) -> dict[str, object]:
    return _capture(["git", *arguments])


def _package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def run_preflight(args: argparse.Namespace) -> dict[str, object]:
    expected_commit = _require_full_commit(args.expected_commit)
    expected_optix_version = _optix_sdk_number(args.expected_optix_sdk)
    output = _external_path(args.output)
    artifact_dir = _external_path(args.artifact_dir)
    if output.exists():
        raise FileExistsError(output)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifacts = _artifact_paths(artifact_dir)
    _require_distinct_receipt(output, artifacts)

    checks: list[dict[str, object]] = []
    probes: dict[str, object] = {}

    head_probe = _git_probe("rev-parse", "HEAD")
    head = str(head_probe["output_tail"]).strip()
    probes["git_head"] = head_probe
    _check(
        checks,
        "exact_expected_commit",
        head_probe["returncode"] == 0 and head == expected_commit,
        requirement=expected_commit,
        observed=head,
        repair="fetch and checkout the exact pushed Goal5838 commit",
    )

    status_probe = _git_probe("status", "--porcelain=v1", "--untracked-files=all")
    dirty = str(status_probe["output_tail"]).strip()
    probes["git_status"] = status_probe
    _check(
        checks,
        "clean_worktree",
        status_probe["returncode"] == 0 and not dirty,
        requirement="no tracked or untracked changes",
        observed=dirty,
        repair="use a fresh checkout; do not discard unreviewed work",
    )

    baseline_probe = _git_probe("cat-file", "-e", f"{BASELINE_COMMIT}^{{commit}}")
    probes["baseline_commit"] = baseline_probe
    _check(
        checks,
        "preregistered_baseline_object_present",
        baseline_probe["returncode"] == 0,
        requirement=BASELINE_COMMIT,
        observed=baseline_probe["returncode"],
        repair=f"git fetch --depth=1 origin {BASELINE_COMMIT}",
    )

    python_path = Path(os.path.abspath(sys.executable))
    _check(
        checks,
        "python_3_12",
        sys.version_info[:2] == (3, 12),
        requirement="Python 3.12.x",
        observed=platform.python_version(),
        repair="create and activate a Python 3.12 environment",
    )
    package_versions = {
        name: _package_version(name) for name in EXPECTED_PACKAGE_VERSIONS
    }
    for name, expected in EXPECTED_PACKAGE_VERSIONS.items():
        _check(
            checks,
            f"python_package_{name}",
            package_versions[name] == expected,
            requirement=expected,
            observed=package_versions[name],
            repair=f"install {name}=={expected} into {python_path}",
        )

    nvidia_smi = shutil.which("nvidia-smi")
    gpu_probe = (
        _capture(
            [
                nvidia_smi,
                "--id=0",
                "--query-gpu=name,uuid,driver_version,compute_cap",
                "--format=csv,noheader,nounits",
            ]
        )
        if nvidia_smi is not None
        else {
            "command": ["nvidia-smi"],
            "command_display": "nvidia-smi",
            "returncode": -1,
            "output_tail": "nvidia-smi not found",
        }
    )
    probes["gpu_identity"] = gpu_probe
    try:
        gpu_rows = (
            _parse_gpu_rows(str(gpu_probe["output_tail"]))
            if gpu_probe["returncode"] == 0
            else []
        )
    except ValueError as exc:
        gpu_rows = []
        probes["gpu_parse_error"] = str(exc)
    _check(
        checks,
        "selected_nvidia_gpu_zero",
        len(gpu_rows) == 1,
        requirement="nvidia-smi GPU index 0 resolves to exactly one GPU",
        observed=gpu_rows,
        repair="repair NVIDIA container visibility; multiple GPUs are allowed",
    )
    gpu = gpu_rows[0] if len(gpu_rows) == 1 else None
    compute_capability = None if gpu is None else gpu["compute_capability"]
    requested_capability = args.compute_capability
    capability_matches = compute_capability is not None and (
        requested_capability is None or compute_capability == requested_capability
    )
    _check(
        checks,
        "compute_capability_identified",
        capability_matches,
        requirement=(
            "a parseable visible-GPU capability"
            if requested_capability is None
            else requested_capability
        ),
        observed=compute_capability,
        repair="query the visible GPU and pass its exact compute capability",
    )

    cuda_prefix = args.cuda_prefix.expanduser().resolve()
    optix_prefix = args.optix_prefix.expanduser().resolve()
    nvcc = cuda_prefix / "bin" / "nvcc"
    cuda_include = cuda_prefix / "include"
    optix_include = optix_prefix / "include"
    _check(
        checks,
        "nvcc_executable",
        nvcc.is_file() and os.access(nvcc, os.X_OK),
        requirement=str(nvcc),
        observed=nvcc.exists(),
        repair="install a CUDA toolkit compatible with the visible GPU",
    )
    if nvcc.is_file() and os.access(nvcc, os.X_OK):
        probes["nvcc_version"] = _capture([str(nvcc), "--version"])
        _check(
            checks,
            "nvcc_version_probe",
            probes["nvcc_version"]["returncode"] == 0,
            requirement="nvcc --version succeeds",
            observed=probes["nvcc_version"],
            repair="repair the CUDA toolkit installation",
        )

    missing_cuda_headers = [
        name for name in CUDA_HEADERS if not (cuda_include / name).is_file()
    ]
    _check(
        checks,
        "cuda_build_headers",
        not missing_cuda_headers,
        requirement=list(CUDA_HEADERS),
        observed={"include": str(cuda_include), "missing": missing_cuda_headers},
        repair="point --cuda-prefix at a complete CUDA toolkit",
    )
    compiler_files = None
    compiler_environment = None
    compiler_environment_identity = None
    compiler_resolution_error = None
    try:
        compiler_files = resolve_cuda_compiler_files(
            cuda_prefix,
            nvrtc_library=getattr(args, "nvrtc_library", None),
            nvvm_library=getattr(args, "nvvm_library", None),
            libdevice=getattr(args, "libdevice", None),
        )
        compiler_environment, compiler_environment_identity = (
            configured_cuda_environment(
                cuda_prefix, optix_prefix, compiler_files
            )
        )
    except (FileNotFoundError, NotADirectoryError, OSError) as exc:
        compiler_resolution_error = f"{type(exc).__name__}: {exc}"
    _check(
        checks,
        "cuda_offline_compiler_inputs",
        compiler_files is not None,
        requirement="exact libnvrtc, libnvvm, and libdevice inputs",
        observed=(
            compiler_resolution_error
            if compiler_files is None
            else {name: str(path) for name, path in compiler_files.items()}
        ),
        repair=(
            "complete the pod-local CUDA compiler toolkit or pass exact "
            "--nvrtc-library, --nvvm-library, and --libdevice paths"
        ),
    )

    missing_optix_headers = [
        name for name in OPTIX_HEADERS if not (optix_include / name).is_file()
    ]
    _check(
        checks,
        "optix_build_headers",
        not missing_optix_headers,
        requirement=list(OPTIX_HEADERS),
        observed={"include": str(optix_include), "missing": missing_optix_headers},
        repair=(
            "acquire a complete OptiX header set compatible with this pod, "
            "then pass its exact version"
        ),
    )
    optix_h = optix_include / "optix.h"
    try:
        optix_version = _parse_optix_version(optix_h) if optix_h.is_file() else None
    except ValueError as exc:
        optix_version = None
        probes["optix_version_parse_error"] = str(exc)
    _check(
        checks,
        "optix_header_version",
        optix_version == expected_optix_version,
        requirement=expected_optix_version,
        observed=optix_version,
        repair=(
            "make --expected-optix-sdk match the selected headers, or select "
            "another exact SDK candidate"
        ),
    )
    optix_header_inventory = _header_inventory(optix_include, OPTIX_HEADERS)
    cuda_header_inventory = _header_inventory(cuda_include, CUDA_HEADERS)
    optix_git_probe = (
        _capture(["git", "-C", str(optix_prefix), "rev-parse", "HEAD"])
        if (optix_prefix / ".git").exists()
        else None
    )
    probes["optix_git_head"] = optix_git_probe
    if optix_git_probe is not None:
        optix_git_head = str(optix_git_probe["output_tail"]).strip()
        known_commit = KNOWN_OPTIX_DEV_RELEASES.get(args.expected_optix_sdk)
        _check(
            checks,
            "known_optix_dev_commit",
            known_commit is None
            or (
                optix_git_probe["returncode"] == 0
                and optix_git_head == known_commit
            ),
            requirement=(
                "exact header hashes"
                if known_commit is None
                else known_commit
            ),
            observed=optix_git_head,
            repair="checkout the recorded exact optix-dev release commit",
            required=False,
        )
    else:
        _check(
            checks,
            "known_optix_dev_commit",
            True,
            requirement="Git identity when available; otherwise exact header hashes",
            observed="non-Git SDK/header distribution",
            repair="",
            required=False,
        )

    host_compiler = _discover_host_compiler(args.host_compiler)
    _check(
        checks,
        "host_compiler",
        host_compiler is not None,
        requirement="an executable g++-13/g++-12/g++-11/g++",
        observed=None if host_compiler is None else str(host_compiler),
        repair="install g++ and pass --host-compiler if discovery is ambiguous",
    )
    abi_probe = None
    if (
        host_compiler is not None
        and not missing_optix_headers
        and not missing_cuda_headers
    ):
        abi_probe = probe_optix_runtime_abi(
            host_compiler, optix_include, cuda_include
        )
    probes["optix_runtime_abi"] = abi_probe
    _check(
        checks,
        "optix_runtime_abi",
        abi_probe is not None and abi_probe["passed"] is True,
        requirement=(
            "a zero-launch optixInit() probe succeeds for the exact selected "
            "headers and host driver"
        ),
        observed=abi_probe,
        repair=(
            "select another compatible OptiX SDK/header release and rerun; "
            "do not classify an ABI mismatch as scientific failure"
        ),
    )
    probes["cuda_compiler_environment"] = compiler_environment_identity
    callback_probe = None
    callback_probe_error = None
    package_stack_matches = all(
        package_versions[name] == expected
        for name, expected in EXPECTED_PACKAGE_VERSIONS.items()
    )
    if (
        compiler_environment is not None
        and compute_capability is not None
        and sys.version_info[:2] == (3, 12)
        and package_stack_matches
        and not missing_cuda_headers
        and not missing_optix_headers
        and optix_version == expected_optix_version
    ):
        try:
            callback_probe = _probe_selected_callback_compiler(
                python=python_path,
                environment=compiler_environment,
                optix_sdk=args.expected_optix_sdk,
                compute_capability=_parse_compute_capability(
                    compute_capability
                ),
                optix_include=optix_include,
                cuda_include=cuda_include,
                package_versions=package_versions,
            )
        except Exception as exc:  # noqa: BLE001 - convert probe failures to evidence
            callback_probe_error = f"{type(exc).__name__}: {exc}"
    probes["selected_callback_compiler"] = (
        callback_probe if callback_probe is not None else callback_probe_error
    )
    _check(
        checks,
        "selected_callback_compiler",
        callback_probe is not None and callback_probe["passed"] is True,
        requirement=(
            "the selected make_ray/any_hit/miss/finalize stack compiles via "
            "the generic family front door with real Numba/NVVM and NVRTC"
        ),
        observed=(
            callback_probe_error
            if callback_probe is None
            else callback_probe
        ),
        repair=(
            "repair the pod-local CUDA compiler environment or select a "
            "compatible CUDA toolkit; do not change the frozen family core"
        ),
    )
    required_tools = {name: shutil.which(name) for name in ("nm", "ldd")}
    for name, path in required_tools.items():
        _check(
            checks,
            f"tool_{name}",
            path is not None,
            requirement=name,
            observed=path,
            repair=f"install the package that provides {name}",
        )

    python_env = dict(os.environ)
    python_env["PYTHONPATH"] = "src:."
    gate_commands = {
        "freeze": [
            str(python_path),
            "scripts/goal5838_freeze_generic_core.py",
            "--verify-stored",
        ],
        "selection": [
            str(python_path),
            "scripts/goal5838_select_challenge.py",
            "--verify-stored",
        ],
        "focused_tests": [
            str(python_path),
            "-m",
            "unittest",
            *FOCUSED_TEST_MODULES,
        ],
    }
    for name, command in gate_commands.items():
        probe = _capture(command, env=python_env)
        probes[f"gate_{name}"] = probe
        _check(
            checks,
            f"local_gate_{name}",
            probe["returncode"] == 0,
            requirement=f"{name} gate exits zero",
            observed=probe,
            repair=f"diagnose and repair the mutable Goal5838 {name} gate",
        )

    for name, path in artifacts.items():
        _check(
            checks,
            f"fresh_artifact_path_{name}",
            not path.exists(),
            requirement=f"nonexistent exclusive output {path}",
            observed=path.exists(),
            repair="choose a fresh external artifact directory",
        )

    required_failures = [
        str(row["name"])
        for row in checks
        if row["required"] and not row["passed"]
    ]
    ready = not required_failures
    command_plan = None
    if (
        compute_capability is not None
        and host_compiler is not None
        and compiler_environment is not None
    ):
        command_plan = _command_plan(
            python=python_path,
            cuda_prefix=cuda_prefix,
            optix_prefix=optix_prefix,
            host_compiler=host_compiler,
            optix_sdk=args.expected_optix_sdk,
            compute_capability=compute_capability,
            expected_commit=expected_commit,
            artifacts=artifacts,
            compiler_environment=compiler_environment,
        )
    result = {
        "schema": RESULT_DOMAIN,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "status": PASS_STATUS if ready else REPAIR_STATUS,
        "ready_for_gpu_exam": ready,
        "scientific_failure_claimed": False,
        "gpu_execution_performed": False,
        "performance_claim_authorized": False,
        "expected_commit": expected_commit,
        "baseline_commit": BASELINE_COMMIT,
        "expected_optix_sdk": args.expected_optix_sdk,
        "expected_optix_version": expected_optix_version,
        "python": {
            "executable": str(python_path),
            "version": platform.python_version(),
            "packages": package_versions,
        },
        "gpu": gpu,
        "paths": {
            "repository": str(ROOT),
            "cuda_prefix": str(cuda_prefix),
            "optix_prefix": str(optix_prefix),
            "optix_header_inventory": optix_header_inventory,
            "cuda_header_inventory": cuda_header_inventory,
            "cuda_compiler_environment": compiler_environment_identity,
            "artifact_dir": str(artifact_dir),
            "artifacts": {name: str(path) for name, path in artifacts.items()},
        },
        "checks": checks,
        "repair_required_checks": required_failures,
        "probes": probes,
        "command_plan": command_plan,
        "boundary": (
            "This receipt establishes pod readiness only. A non-ready result is "
            "repairable engineering, not scientific failure. A ready result is "
            "not a native build, GPU execution, performance result, Paper App, "
            "external review, consensus, or Goal5838 completion claim."
        ),
        "result_sha256": "",
    }
    result["result_sha256"] = _digest(result)
    _write_json_exclusive(output, result)
    return result


def _internal_callback_compile_main(arguments: list[str]) -> int:
    if len(arguments) != 2:
        raise ValueError(
            f"{INTERNAL_CALLBACK_PROBE} requires request and output paths"
        )
    request_path = Path(arguments[0]).expanduser().resolve(strict=True)
    output_path = Path(arguments[1]).expanduser().resolve()
    if output_path.exists():
        raise FileExistsError(output_path)
    request = json.loads(request_path.read_text(encoding="utf-8"))
    if not isinstance(request, dict):
        raise TypeError("internal callback compile request must be an object")
    result = _compile_selected_callback_stack(request)
    _write_json_exclusive(output_path, result)
    return 0


def main() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] == INTERNAL_CALLBACK_PROBE:
        return _internal_callback_compile_main(sys.argv[2:])
    parser = argparse.ArgumentParser()
    parser.add_argument("--cuda-prefix", type=Path, required=True)
    parser.add_argument("--optix-prefix", type=Path, required=True)
    parser.add_argument("--expected-optix-sdk", required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--compute-capability")
    parser.add_argument("--host-compiler", type=Path)
    parser.add_argument("--nvrtc-library", type=Path)
    parser.add_argument("--nvvm-library", type=Path)
    parser.add_argument("--libdevice", type=Path)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_preflight(args)
    print(
        json.dumps(
            {
                "status": result["status"],
                "ready_for_gpu_exam": result["ready_for_gpu_exam"],
                "repair_required_checks": result["repair_required_checks"],
                "result_sha256": result["result_sha256"],
            },
            sort_keys=True,
        )
    )
    plan = result["command_plan"]
    if result["ready_for_gpu_exam"] and isinstance(plan, dict):
        for name in ("build", "run", "verify"):
            print(f"{name}: {plan[name]['display']}")
    print(f"output={args.output.expanduser().resolve()}")
    return 0 if result["ready_for_gpu_exam"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
