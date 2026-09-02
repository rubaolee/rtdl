#!/usr/bin/env python3
"""Fail-fast toolchain preflight for successor owner-grouped GPU validation."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
for import_root in (ROOT / "src", ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from rtdsl.v4_callback_ir import CallbackRole
from rtdsl.v4_curve_owner_grouped_any_hit_optix_compiler import (
    compile_verified_curve_owner_grouped_any_hit_executable,
)
from rtdsl.v4_curve_owner_grouped_any_hit_standard_library import (
    build_curve_owner_grouped_any_hit_authority,
)
from rtdsl.v4_curve_physical_schema import CurveTargetProfile
from rtdsl.v4_owner_grouped_any_hit import compile_owner_grouped_any_hit_abi
from scripts.build_v4_optix_native_snapshot import (
    _header_inventory,
    _compute_capability,
    _gpu_identity,
    _optix_sdk_number,
    _optix_version,
    _sha,
    _write_json,
)

_ENV_MARKER = "RTDL_SUCCESSOR_OWNER_GROUPED_TOOLCHAIN_ENV_V1"
_PREFLIGHT_SCHEMA = (
    "rtdl.successor_owner_grouped_any_hit.pod_preflight.v2"
)
_FORMAL_CACHE_ENV = (
    "RTDL_V4_FORMAL_LEAF_CACHE",
    "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST",
    "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256",
)
_CLEARED_AMBIENT_ENV = _FORMAL_CACHE_ENV + (
    "LD_PRELOAD",
    "NUMBA_ENABLE_CUDASIM",
    "NUMBA_FORCE_CUDA_CC",
    "NUMBA_CUDA_DEFAULT_PTX_CC",
    "NUMBA_CUDA_DRIVER",
    "RTDL_OPTIX_LIB",
    "RTDL_OPTIX_LIBRARY",
)
_ROLES = (
    CallbackRole.MAKE_RAY,
    CallbackRole.ANY_HIT,
    CallbackRole.MISS,
    CallbackRole.FINALIZE,
)
_OPTIX_RUNTIME_ABI_PROBE_SOURCE = """\
#include <cstdio>
#include <optix.h>
#include <optix_function_table_definition.h>
#include <optix_stubs.h>

int main() {
    const OptixResult result = optixInit();
    if (result != OPTIX_SUCCESS) {
        std::fprintf(stderr, "optixInit_result=%d\\n", static_cast<int>(result));
        return 1;
    }
    std::printf("optixInit_result=%d\\n", static_cast<int>(result));
    return 0;
}
"""


def _capture(command: list[str]) -> str:
    completed = subprocess.run(
        command, cwd=ROOT, text=True, capture_output=True, check=False)
    output = (completed.stdout + completed.stderr).strip()
    if completed.returncode:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {command!r}: {output}")
    return output


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
                path.resolve(strict=True) for path in sorted(root.glob(pattern))
                if path.is_file())
    unique = tuple(dict.fromkeys(observed))
    if not unique:
        raise FileNotFoundError(f"{label} was not found; pass its exact path")
    return unique[0]


def resolve_cuda_runtime_files(
    cuda_prefix: Path,
    *,
    nvrtc_library: Path | None = None,
    nvvm_library: Path | None = None,
    libdevice: Path | None = None,
) -> dict[str, Path]:
    """Resolve the exact CUDA compiler libraries used by preflight and run."""

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
            tuple(root / name for root in library_roots
                  for name in ("libnvrtc.so.12", "libnvrtc.so")),
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


def configured_runtime_environment(
    cuda_prefix: Path,
    optix_prefix: Path,
    runtime_files: dict[str, Path],
    *,
    base: dict[str, str] | None = None,
) -> tuple[dict[str, str], dict[str, object]]:
    cuda = cuda_prefix.expanduser().resolve(strict=True)
    optix = optix_prefix.expanduser().resolve(strict=True)
    environment = dict(os.environ if base is None else base)
    library_dirs = tuple(dict.fromkeys(
        str(path) for path in (
            runtime_files["nvrtc_library"].parent,
            runtime_files["nvvm_library"].parent,
            cuda / "lib64",
            cuda / "targets/x86_64-linux/lib",
            Path("/usr/lib/x86_64-linux-gnu"),
        ) if path.is_dir()
    ))
    path_dirs = (str(cuda / "bin"),)
    old_library_path = tuple(filter(None,
        environment.get("LD_LIBRARY_PATH", "").split(os.pathsep)))
    old_path = tuple(filter(None, environment.get("PATH", "").split(os.pathsep)))
    environment["LD_LIBRARY_PATH"] = os.pathsep.join(
        tuple(dict.fromkeys(library_dirs + old_library_path)))
    environment["PATH"] = os.pathsep.join(
        tuple(dict.fromkeys(path_dirs + old_path)))
    environment["NUMBA_CUDA_NVVM"] = str(runtime_files["nvvm_library"])
    environment["NUMBA_CUDA_LIBDEVICE"] = str(runtime_files["libdevice"])
    environment["CUDA_HOME"] = str(cuda)
    environment["CUDA_PATH"] = str(cuda)
    environment["RTDL_V4_CUDA_PREFIX"] = str(cuda)
    environment["RTDL_V4_OPTIX_PREFIX"] = str(optix)
    for name in _CLEARED_AMBIENT_ENV:
        environment.pop(name, None)
    identity = {
        "cuda_prefix": str(cuda),
        "optix_prefix": str(optix),
        "nvrtc_library": str(runtime_files["nvrtc_library"]),
        "nvrtc_sha256": _sha(runtime_files["nvrtc_library"]),
        "nvvm_library": str(runtime_files["nvvm_library"]),
        "nvvm_sha256": _sha(runtime_files["nvvm_library"]),
        "libdevice": str(runtime_files["libdevice"]),
        "libdevice_sha256": _sha(runtime_files["libdevice"]),
        "ld_library_path_prefix": list(library_dirs),
        "path_prefix": list(path_dirs),
        "formal_numba_cache_disabled": True,
        "cleared_ambient_environment": list(_CLEARED_AMBIENT_ENV),
    }
    marker = hashlib.sha256(json.dumps(
        identity, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode("utf-8")).hexdigest()
    environment[_ENV_MARKER] = marker
    return environment, {**identity, "environment_marker": marker}


def ensure_runtime_environment(
    cuda_prefix: Path,
    optix_prefix: Path,
    runtime_files: dict[str, Path],
    *,
    argv: list[str],
) -> dict[str, object]:
    environment, identity = configured_runtime_environment(
        cuda_prefix, optix_prefix, runtime_files)
    if os.environ.get(_ENV_MARKER) != identity["environment_marker"]:
        os.execve(sys.executable, argv, environment)
        raise AssertionError("os.execve returned unexpectedly")
    for name in (
        "NUMBA_CUDA_NVVM", "NUMBA_CUDA_LIBDEVICE",
        "CUDA_HOME", "CUDA_PATH",
        "RTDL_V4_CUDA_PREFIX", "RTDL_V4_OPTIX_PREFIX",
    ):
        if os.environ.get(name) != environment[name]:
            raise RuntimeError(f"configured CUDA environment drifted: {name}")
    if tuple(os.environ["LD_LIBRARY_PATH"].split(os.pathsep)[
            :len(identity["ld_library_path_prefix"])]) != \
            tuple(identity["ld_library_path_prefix"]):
        raise RuntimeError("configured CUDA loader path drifted")
    if os.environ["PATH"].split(os.pathsep)[0] != \
            identity["path_prefix"][0]:
        raise RuntimeError("configured CUDA executable path drifted")
    if any(os.environ.get(name) for name in _CLEARED_AMBIENT_ENV):
        raise RuntimeError("ambient CUDA/loader overrides were not cleared")
    return identity


def _compile_callback_stack(
    *,
    optix_sdk: str,
    compute_capability: tuple[int, int],
    optix_include: Path,
    cuda_include: Path,
) -> dict[str, object]:
    synthetic_native = hashlib.sha256(
        b"successor pod preflight; no native library or GPU launch"
    ).hexdigest()
    target = CurveTargetProfile(
        "optix", optix_sdk,
        f"{compute_capability[0]}.{compute_capability[1]}",
        synthetic_native,
    )
    authority, _ = build_curve_owner_grouped_any_hit_authority(target)
    abi = compile_owner_grouped_any_hit_abi(authority.behavior)
    executable, compiler_log = \
        compile_verified_curve_owner_grouped_any_hit_executable(
            authority,
            abi,
            compute_capability=compute_capability,
            optix_include=optix_include,
            cuda_include=cuda_include,
            expected_python_version=platform.python_version(),
            expected_numba_version=importlib.metadata.version("numba"),
            expected_numpy_version=importlib.metadata.version("numpy"),
            python_executable=sys.executable,
        )
    if tuple(leaf.role for leaf in executable.generated_leaves) != _ROLES \
            or tuple(leaf.role for leaf in executable.compiled_leaves) != \
                tuple(role.value for role in _ROLES):
        raise RuntimeError("preflight compiled callback role topology differs")
    return {
        "executable_sha256": executable.executable_sha256,
        "wrapper_ptx_sha256": executable.wrapper_ptx_sha256,
        "composed_ptx_sha256": executable.composed.ptx_sha256,
        "compiled_leaf_ptx_sha256": [
            leaf.ptx_sha256 for leaf in executable.compiled_leaves],
        "compiled_roles": [role.value for role in _ROLES],
        "nvrtc_log_sha256": hashlib.sha256(
            compiler_log.encode("utf-8")).hexdigest(),
    }


def _compile_nvcc_host_probe(
    nvcc: Path,
    host_compiler: Path,
    compute_capability: tuple[int, int],
) -> dict[str, object]:
    with tempfile.TemporaryDirectory(
            prefix="rtdl-successor-nvcc-preflight-") as directory:
        root = Path(directory)
        source = root / "probe.cu"
        output = root / "probe.o"
        source_body = (
            'extern "C" __global__ void rtdl_preflight_kernel('
            'unsigned int* value) { if (threadIdx.x == 0) *value = 1u; }\n'
        )
        source.write_text(
            source_body,
            encoding="utf-8",
            newline="\n",
        )
        command = [
            str(nvcc), "-ccbin", str(host_compiler), "-std=c++17",
            f"-arch=sm_{compute_capability[0]}{compute_capability[1]}",
            "-c", str(source), "-o", str(output),
        ]
        compiler_output = _capture(command)
        if not output.is_file() or output.stat().st_size == 0:
            raise RuntimeError("nvcc host-compiler probe produced no object")
        return {
            "command_template": [
                "<temporary>/probe.cu" if item == str(source) else
                "<temporary>/probe.o" if item == str(output) else item
                for item in command
            ],
            "source_sha256": hashlib.sha256(
                source_body.encode("utf-8")).hexdigest(),
            "object_bytes": output.stat().st_size,
            "object_sha256": _sha(output),
            "compiler_output_sha256": hashlib.sha256(
                compiler_output.encode("utf-8")).hexdigest(),
        }


def _run_optix_runtime_abi_probe(
    host_compiler: Path,
    optix_include: Path,
    cuda_include: Path,
) -> dict[str, object]:
    """Require the selected headers to negotiate with the host OptiX driver."""

    with tempfile.TemporaryDirectory(
            prefix="rtdl-successor-optix-abi-preflight-") as directory:
        root = Path(directory)
        source = root / "probe.cpp"
        executable = root / "probe"
        source.write_text(
            _OPTIX_RUNTIME_ABI_PROBE_SOURCE,
            encoding="utf-8",
            newline="\n",
        )
        command = [
            str(host_compiler), "-std=c++17",
            f"-I{optix_include}", f"-I{cuda_include}",
            str(source), "-ldl", "-o", str(executable),
        ]
        compiler_output = _capture(command)
        if not executable.is_file() or executable.stat().st_size == 0:
            raise RuntimeError("OptiX runtime ABI probe produced no executable")
        runtime_output = _capture([str(executable)])
        if runtime_output != "optixInit_result=0":
            raise RuntimeError(
                f"unexpected OptiX runtime ABI probe output: {runtime_output!r}")
        return {
            "command_template": [
                "<temporary>/probe.cpp" if item == str(source) else
                "<temporary>/probe" if item == str(executable) else item
                for item in command
            ],
            "source_sha256": hashlib.sha256(
                _OPTIX_RUNTIME_ABI_PROBE_SOURCE.encode("utf-8")).hexdigest(),
            "executable_bytes": executable.stat().st_size,
            "executable_sha256": _sha(executable),
            "compiler_output_sha256": hashlib.sha256(
                compiler_output.encode("utf-8")).hexdigest(),
            "runtime_output": runtime_output,
            "optix_launch_count": 0,
        }


def run_preflight(args) -> dict[str, object]:
    if platform.system() != "Linux" \
            or platform.machine().lower() not in {"x86_64", "amd64"}:
        raise RuntimeError("successor pod requires Linux x86_64")
    output = args.output.expanduser().resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError("pod preflight output must be outside the Git tree")
    if output.exists():
        raise FileExistsError(output)
    cuda = args.cuda_prefix.expanduser().resolve(strict=True)
    optix = args.optix_prefix.expanduser().resolve(strict=True)
    cuda_include = cuda / "include"
    optix_include = optix / "include"
    for path in (
        cuda / "bin/nvcc", cuda_include / "cuda.h", cuda_include / "nvrtc.h",
        optix_include / "optix.h",
    ):
        if not path.is_file():
            raise FileNotFoundError(path)
    for executable in ("git", "nm", "nvidia-smi"):
        if shutil.which(executable) is None:
            raise RuntimeError(f"required executable is unavailable: {executable}")
    if args.host_compiler is None:
        discovered_host_compiler = shutil.which("g++")
        if discovered_host_compiler is None:
            raise RuntimeError("g++ is required as the explicit nvcc host compiler")
        host_compiler = Path(discovered_host_compiler)
    else:
        host_compiler = args.host_compiler
    host_compiler = host_compiler.expanduser().resolve(strict=True)
    if not host_compiler.is_file() or not os.access(host_compiler, os.X_OK):
        raise PermissionError(
            f"nvcc host compiler is not executable: {host_compiler}")
    git_commit = _capture(["git", "rev-parse", "HEAD"])
    git_status = _capture(["git", "status", "--porcelain"])
    if git_status and not args.allow_dirty:
        raise RuntimeError("pod preflight requires a clean Git tree")
    expected_optix = _optix_sdk_number(args.expected_optix_sdk)
    observed_optix = _optix_version(optix_include / "optix.h")
    if observed_optix != expected_optix:
        raise RuntimeError(
            f"OptiX SDK mismatch: observed={observed_optix}, "
            f"expected={expected_optix}")
    gpu_identity, capability = _gpu_identity()
    requested = _compute_capability(args.compute_capability)
    if capability != requested:
        raise RuntimeError(
            f"GPU compute capability mismatch: observed={capability}, "
            f"requested={requested}")
    runtime_files = resolve_cuda_runtime_files(
        cuda,
        nvrtc_library=args.nvrtc_library,
        nvvm_library=args.nvvm_library,
        libdevice=args.libdevice,
    )
    environment_identity = ensure_runtime_environment(
        cuda, optix, runtime_files,
        argv=[sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
    )
    optix_headers_before = _header_inventory(optix_include)
    cuda_headers_before = _header_inventory(cuda_include)
    host_compile_probe = _compile_nvcc_host_probe(
        (cuda / "bin/nvcc").resolve(strict=True),
        host_compiler,
        capability,
    )
    optix_runtime_abi_probe = _run_optix_runtime_abi_probe(
        host_compiler,
        optix_include,
        cuda_include,
    )
    callback_stack = _compile_callback_stack(
        optix_sdk=args.expected_optix_sdk,
        compute_capability=capability,
        optix_include=optix_include,
        cuda_include=cuda_include,
    )
    post_commit = _capture(["git", "rev-parse", "HEAD"])
    post_status = _capture(["git", "status", "--porcelain"])
    if post_commit != git_commit or post_status != git_status \
            or _header_inventory(optix_include) != optix_headers_before \
            or _header_inventory(cuda_include) != cuda_headers_before:
        raise RuntimeError("preflight input identity changed during compilation")
    result = {
        "schema": _PREFLIGHT_SCHEMA,
        "status": "PASS__COMPILER_AND_OPTIX_RUNTIME_ABI_READY_FOR_NATIVE_BUILD",
        "git_commit": git_commit,
        "git_status_before": git_status.splitlines(),
        "git_status_after": post_status.splitlines(),
        "dirty_preflight_authorized": bool(args.allow_dirty),
        "host": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "numba": importlib.metadata.version("numba"),
            "numpy": importlib.metadata.version("numpy"),
            "gpu": gpu_identity,
        },
        "target": {
            "optix_sdk": args.expected_optix_sdk,
            "optix_version": observed_optix,
            "compute_capability": list(capability),
            "cuda_prefix": str(cuda),
            "optix_prefix": str(optix),
            "nvcc_path": str((cuda / "bin/nvcc").resolve(strict=True)),
            "nvcc_sha256": _sha((cuda / "bin/nvcc").resolve(strict=True)),
            "nvcc_version": _capture([str(cuda / "bin/nvcc"), "--version"]),
            "host_compiler_path": str(host_compiler),
            "host_compiler_sha256": _sha(host_compiler),
            "host_compiler_version": _capture(
                [str(host_compiler), "--version"]),
            "optix_header_inventory": optix_headers_before,
            "cuda_header_inventory": cuda_headers_before,
            "runtime_environment": environment_identity,
        },
        "compiler_probe": callback_stack,
        "nvcc_host_compiler_probe": host_compile_probe,
        "optix_runtime_abi_probe": optix_runtime_abi_probe,
        "optix_runtime_abi_checked": True,
        "native_library_built": False,
        "optix_launch_count": 0,
        "gpu_correctness_evidence_count": 0,
        "performance_claimed": False,
        "external_review_count": 0,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    _write_json(output, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cuda-prefix", required=True, type=Path)
    parser.add_argument("--optix-prefix", required=True, type=Path)
    parser.add_argument("--expected-optix-sdk", default="9.0.0")
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--host-compiler", type=Path)
    parser.add_argument("--nvrtc-library", type=Path)
    parser.add_argument("--nvvm-library", type=Path)
    parser.add_argument("--libdevice", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--allow-dirty", action="store_true")
    args = parser.parse_args()
    result = run_preflight(args)
    print(json.dumps({
        "status": result["status"],
        "gpu": result["host"]["gpu"],
        "compiled_roles": result["compiler_probe"]["compiled_roles"],
        "optix_launch_count": result["optix_launch_count"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
