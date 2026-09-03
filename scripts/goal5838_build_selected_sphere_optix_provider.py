#!/usr/bin/env python3
"""Build the Goal5838 OptiX provider and seal its exact provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = "scripts/goal5838_build_selected_sphere_optix_provider.py"
TRANSLATION_UNIT_PATHS = (
    "src/native/rtdl_optix.cpp",
    "src/native/optix/rtdl_optix_cuda_helpers.cu",
)
NATIVE_SOURCE_PATHS = (
    BUILDER_PATH,
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
REQUIRED_SYMBOLS = (
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
KEY_HEADER_NAMES = (
    "optix.h",
    "optix_device.h",
    "optix_function_table_definition.h",
    "optix_stack_size.h",
    "optix_stubs.h",
    "cuda.h",
    "cuda_runtime.h",
    "nvrtc.h",
)
RESULT_DOMAIN = "rtdl.goal5838.selected_sphere_optix_provider_build.v2"
OPTIX_RUNTIME_ABI_PROBE_SOURCE = """\
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


def _sealed_sha256(document: dict[str, object]) -> str:
    body = dict(document)
    body["result_sha256"] = ""
    return hashlib.sha256(
        RESULT_DOMAIN.encode("ascii") + b"\0" + _canonical_bytes(body)
    ).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _capture(command: list[str], *, required: bool = True) -> str:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = (completed.stdout + completed.stderr).strip()
    if required and completed.returncode:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {command!r}: {output}"
        )
    return output


def _probe(command: list[str]) -> dict[str, object]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        return {
            "returncode": completed.returncode,
            "output": completed.stdout,
        }
    except OSError as exc:
        return {
            "returncode": -1,
            "output": f"{type(exc).__name__}: {exc}",
        }


def probe_optix_runtime_abi(
    host_compiler: Path,
    optix_include: Path,
    cuda_include: Path,
) -> dict[str, object]:
    """Compile and execute optixInit without building or launching RT work."""

    with tempfile.TemporaryDirectory(prefix="rtdl-goal5838-optix-abi-") as name:
        directory = Path(name)
        source = directory / "probe.cpp"
        executable = directory / "probe"
        source.write_text(
            OPTIX_RUNTIME_ABI_PROBE_SOURCE,
            encoding="utf-8",
            newline="\n",
        )
        command = [
            str(host_compiler),
            "-std=c++17",
            f"-I{optix_include}",
            f"-I{cuda_include}",
            str(source),
            "-ldl",
            "-o",
            str(executable),
        ]
        compile_probe = _probe(command)
        executable_exists = executable.is_file() and executable.stat().st_size > 0
        runtime_probe = (
            _probe([str(executable)]) if executable_exists else None
        )
        runtime_output = (
            str(runtime_probe["output"]).strip()
            if runtime_probe is not None
            else ""
        )
        return {
            "source_sha256": hashlib.sha256(
                OPTIX_RUNTIME_ABI_PROBE_SOURCE.encode("ascii")
            ).hexdigest(),
            "compile_command_template": [
                "<temporary>/probe.cpp"
                if item == str(source)
                else "<temporary>/probe"
                if item == str(executable)
                else item
                for item in command
            ],
            "compile_returncode": compile_probe["returncode"],
            "compiler_output_sha256": hashlib.sha256(
                str(compile_probe["output"]).encode("utf-8")
            ).hexdigest(),
            "executable_bytes": (
                executable.stat().st_size if executable_exists else 0
            ),
            "executable_sha256": (
                _file_sha256(executable) if executable_exists else ""
            ),
            "runtime_returncode": (
                runtime_probe["returncode"] if runtime_probe is not None else None
            ),
            "runtime_output": runtime_output,
            "optix_launch_count": 0,
            "passed": (
                compile_probe["returncode"] == 0
                and executable_exists
                and runtime_probe is not None
                and runtime_probe["returncode"] == 0
                and runtime_output == "optixInit_result=0"
            ),
        }


def _git(*arguments: str) -> str:
    return _capture(["git", *arguments])


def _git_bytes(*arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", *arguments], cwd=ROOT, capture_output=True, check=False
    )
    if completed.returncode:
        raise RuntimeError(
            f"git {' '.join(arguments)} failed: "
            + completed.stderr.decode("utf-8", errors="replace").strip()
        )
    return completed.stdout


def _require_full_commit(value: str) -> str:
    if (
        len(value) != 40
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError("--expected-commit must be a full lowercase commit id")
    return value


def _source_rows(commit: str) -> list[dict[str, object]]:
    rows = []
    for relative in NATIVE_SOURCE_PATHS:
        path = ROOT / relative
        payload = path.read_bytes()
        committed = _git_bytes("show", f"{commit}:{relative}")
        if payload != committed:
            raise RuntimeError(f"native build source differs from Git: {relative}")
        rows.append(
            {
                "path": relative,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    return rows


def _repository_before(expected_commit: str) -> dict[str, object]:
    commit = _require_full_commit(expected_commit)
    head = _git("rev-parse", "HEAD")
    resolved = _git("rev-parse", "--verify", f"{commit}^{{commit}}")
    if head != commit or resolved != commit:
        raise RuntimeError(
            f"native build checkout differs from expected commit: {head} != {commit}"
        )
    dirty = _git("status", "--porcelain=v1", "--untracked-files=all")
    if dirty:
        raise RuntimeError(f"native build requires a clean Git tree: {dirty}")
    return {
        "expected_commit": commit,
        "head_before": head,
        "branch": _git("branch", "--show-current"),
        "origin_url": _git("remote", "get-url", "origin"),
        "clean_before": True,
        "source_files": _source_rows(commit),
    }


def _repository_after(before: dict[str, object]) -> dict[str, object]:
    head = _git("rev-parse", "HEAD")
    dirty = _git("status", "--porcelain=v1", "--untracked-files=all")
    if head != before["head_before"] or dirty:
        raise RuntimeError("Git identity changed during native build")
    if _source_rows(str(head)) != before["source_files"]:
        raise RuntimeError("native source identity changed during build")
    return {**before, "head_after": head, "clean_after": True}


def _parse_compute_capability(value: str) -> tuple[int, int]:
    match = re.fullmatch(
        r"([1-9][0-9]?)\.((?:0|[1-9][0-9]?))", value
    )
    if match is None:
        raise ValueError(f"invalid compute capability: {value!r}")
    major, minor = (int(item) for item in match.groups())
    if major == 0:
        raise ValueError(f"invalid compute capability: {value!r}")
    return major, minor


def _require_cuda_visibility() -> str:
    value = os.environ.get("CUDA_VISIBLE_DEVICES")
    if value != "0":
        raise RuntimeError(
            "Goal5838 requires CUDA_VISIBLE_DEVICES=0 so nvidia-smi and the "
            "native CUDA ordinal bind the same selected GPU"
        )
    return value


def _gpu_identity() -> dict[str, str]:
    fields = ("name", "uuid", "driver_version", "compute_capability")
    rows = _capture(
        [
            "nvidia-smi",
            "--id=0",
            "--query-gpu=name,uuid,driver_version,compute_cap",
            "--format=csv,noheader,nounits",
        ]
    ).splitlines()
    rows = [row.strip() for row in rows if row.strip()]
    if len(rows) != 1:
        raise RuntimeError(
            f"selected NVIDIA GPU query returned {len(rows)} rows"
        )
    values = tuple(part.strip() for part in rows[0].split(","))
    if len(values) != len(fields):
        raise RuntimeError("unexpected nvidia-smi GPU identity format")
    result = dict(zip(fields, values, strict=True))
    _parse_compute_capability(result["compute_capability"])
    return result


def _optix_version(path: Path) -> int:
    match = re.search(
        r"^\s*#\s*define\s+OPTIX_VERSION\s+([0-9]+)\s*$",
        path.read_text(encoding="utf-8", errors="strict"),
        re.MULTILINE,
    )
    if match is None:
        raise RuntimeError("OPTIX_VERSION is absent from optix.h")
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
    major, minor, patch = (int(item) for item in match.groups())
    if major == 0 or minor >= 100 or patch >= 100:
        raise ValueError(f"invalid OptiX SDK version: {value!r}")
    return major * 10000 + minor * 100 + patch


def _discover_host_compiler(requested: Path | None) -> Path:
    if requested is not None:
        result = requested.expanduser().resolve(strict=True)
    else:
        discovered = next(
            (
                shutil.which(name)
                for name in ("g++-13", "g++-12", "g++-11", "g++")
                if shutil.which(name) is not None
            ),
            None,
        )
        if discovered is None:
            raise RuntimeError("a supported g++ host compiler is required")
        result = Path(discovered).resolve(strict=True)
    if not result.is_file() or not os.access(result, os.X_OK):
        raise PermissionError(f"host compiler is not executable: {result}")
    return result


def _pkg_config_geos() -> tuple[list[str], list[str], str]:
    executable = shutil.which("pkg-config")
    if executable is not None:
        for package in ("geos-c", "geos"):
            cflags = subprocess.run(
                [executable, "--cflags", package],
                text=True,
                capture_output=True,
                check=False,
            )
            libraries = subprocess.run(
                [executable, "--libs", package],
                text=True,
                capture_output=True,
                check=False,
            )
            if cflags.returncode == 0 and libraries.returncode == 0:
                return (
                    shlex.split(cflags.stdout),
                    shlex.split(libraries.stdout),
                    f"pkg-config:{package}",
                )
    if Path("/usr/include/geos_c.h").is_file():
        return [], ["-lgeos_c"], "system-header-and-link-name"
    return [], [], "disabled-header-absent"


def _cuda_system_include(host_compiler: Path) -> str:
    multiarch = _capture(
        [str(host_compiler), "-print-multiarch"], required=False
    ).splitlines()
    if multiarch and multiarch[0].strip():
        candidate = Path("/usr/include") / multiarch[0].strip()
        if candidate.is_dir():
            return str(candidate)
    candidate = Path("/usr/include/x86_64-linux-gnu")
    return str(candidate) if candidate.is_dir() else ""


def _library_dirs(cuda_prefix: Path) -> list[Path]:
    result = []
    for candidate in (
        cuda_prefix / "lib64",
        cuda_prefix / "targets/x86_64-linux/lib",
        Path("/usr/lib/x86_64-linux-gnu"),
    ):
        if candidate.is_dir() and candidate not in result:
            result.append(candidate)
    return result


def _resolve_nvrtc_library(
    cuda_prefix: Path, requested: Path | None
) -> Path:
    if requested is not None:
        result = requested.expanduser().resolve(strict=True)
        if not result.is_file():
            raise FileNotFoundError(result)
        return result
    roots = _library_dirs(cuda_prefix)
    candidates = [
        root / name
        for root in roots
        for name in ("libnvrtc.so.12", "libnvrtc.so")
    ]
    candidates.extend(
        path
        for root in roots
        for path in sorted(root.glob("libnvrtc.so*"))
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve(strict=True)
    raise FileNotFoundError("no NVRTC shared library found; pass --nvrtc-library")


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


def _header_rows(optix_include: Path, cuda_include: Path) -> list[dict[str, object]]:
    rows = []
    for name in KEY_HEADER_NAMES:
        root = optix_include if name.startswith("optix") else cuda_include
        path = (root / name).resolve(strict=True)
        if not path.is_file():
            raise FileNotFoundError(path)
        rows.append(
            {
                "name": name,
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": _file_sha256(path),
            }
        )
    return rows


def _require_external_outputs(*paths: Path) -> None:
    root = ROOT.resolve()
    resolved = tuple(path.expanduser().resolve() for path in paths)
    for path in resolved:
        if path == root or root in path.parents:
            raise ValueError(f"evidence build output must be outside Git tree: {path}")
    for index, left in enumerate(resolved):
        for right in resolved[index + 1 :]:
            if left == right or left in right.parents or right in left.parents:
                raise ValueError(
                    f"build outputs must be distinct non-nested files: {left}, {right}"
                )


def _build_command(
    *,
    nvcc: Path,
    host_compiler: Path,
    optix_include: Path,
    cuda_include: Path,
    cuda_system_include: str,
    build_id: str,
    compute_capability: tuple[int, int],
    geos_cflags: list[str],
    geos_libraries: list[str],
    library_dirs: list[Path],
    nvrtc_library: Path,
    output: Path,
) -> list[str]:
    return [
        str(nvcc),
        "-ccbin",
        str(host_compiler),
        "-std=c++17",
        "-O3",
        "-shared",
        f"-I{optix_include}",
        f"-I{cuda_include}",
        *geos_cflags,
        f'-DRTDL_OPTIX_INCLUDE_DIR="{optix_include}"',
        f'-DRTDL_CUDA_INCLUDE_DIR="{cuda_include}"',
        f'-DRTDL_CUDA_SYSTEM_INCLUDE_DIR="{cuda_system_include}"',
        f'-DRTDL_OPTIX_BUILD_ID="{build_id}"',
        f"-arch=sm_{compute_capability[0]}{compute_capability[1]}",
        "-Xcompiler",
        "-fPIC",
        *(str(ROOT / relative) for relative in TRANSLATION_UNIT_PATHS),
        *(f"-L{path}" for path in library_dirs),
        "-lcuda",
        "-Xlinker",
        str(nvrtc_library),
        *geos_libraries,
        "-o",
        str(output),
    ]


def _publish_exclusive(source: Path, destination: Path) -> None:
    try:
        os.link(source, destination)
    except FileExistsError:
        raise FileExistsError(destination) from None
    source.unlink()


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
        _publish_exclusive(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def build(args: argparse.Namespace) -> dict[str, object]:
    output = args.output.expanduser().resolve()
    manifest = args.manifest.expanduser().resolve()
    log = args.log.expanduser().resolve()
    _require_external_outputs(output, manifest, log)
    for path in (output, manifest, log):
        if path.exists():
            raise FileExistsError(path)
        path.parent.mkdir(parents=True, exist_ok=True)

    repository_before = _repository_before(args.expected_commit)
    cuda_visible_devices = _require_cuda_visibility()
    cuda_prefix = args.cuda_prefix.expanduser().resolve(strict=True)
    optix_prefix = args.optix_prefix.expanduser().resolve(strict=True)
    cuda_include = (cuda_prefix / "include").resolve(strict=True)
    optix_include = (optix_prefix / "include").resolve(strict=True)
    nvcc = (cuda_prefix / "bin" / "nvcc").resolve(strict=True)
    host_compiler = _discover_host_compiler(args.host_compiler)
    if not nvcc.is_file() or not os.access(nvcc, os.X_OK):
        raise PermissionError(f"nvcc is not executable: {nvcc}")

    gpu = _gpu_identity()
    capability = _parse_compute_capability(gpu["compute_capability"])
    if args.compute_capability is not None:
        requested = _parse_compute_capability(args.compute_capability)
        if requested != capability:
            raise RuntimeError(
                "requested compute capability differs from visible GPU: "
                f"{requested} != {capability}"
            )
    optix_h = optix_include / "optix.h"
    optix_version = _optix_version(optix_h)
    expected_optix_version = _optix_sdk_number(args.expected_optix_sdk)
    if optix_version != expected_optix_version:
        raise RuntimeError(
            "OptiX header version differs from requested SDK: "
            f"{optix_version} != {expected_optix_version}"
        )
    headers = _header_rows(optix_include, cuda_include)
    optix_runtime_abi_probe = probe_optix_runtime_abi(
        host_compiler, optix_include, cuda_include
    )
    if optix_runtime_abi_probe["passed"] is not True:
        raise RuntimeError(
            "selected OptiX headers do not negotiate with the host driver: "
            f"{optix_runtime_abi_probe}"
        )
    geos_cflags, geos_libraries, geos_mode = _pkg_config_geos()
    library_dirs = _library_dirs(cuda_prefix)
    nvrtc_library = _resolve_nvrtc_library(
        cuda_prefix, args.nvrtc_library
    )
    system_include = _cuda_system_include(host_compiler)
    build_input = {
        "schema": "rtdl.goal5838.selected_sphere_optix_build_input.v2",
        "translation_units": list(TRANSLATION_UNIT_PATHS),
        "builder_path": BUILDER_PATH,
        "builder_sha256": next(
            row["sha256"]
            for row in repository_before["source_files"]
            if row["path"] == BUILDER_PATH
        ),
        "cuda_prefix": str(cuda_prefix),
        "cuda_include": str(cuda_include),
        "cuda_system_include": system_include,
        "nvcc_path": str(nvcc),
        "nvcc_sha256": _file_sha256(nvcc),
        "nvcc_version": _capture([str(nvcc), "--version"]),
        "nvrtc_library_path": str(nvrtc_library),
        "nvrtc_library_bytes": nvrtc_library.stat().st_size,
        "nvrtc_library_sha256": _file_sha256(nvrtc_library),
        "host_compiler_path": str(host_compiler),
        "host_compiler_sha256": _file_sha256(host_compiler),
        "host_compiler_version": _capture([str(host_compiler), "--version"]),
        "optix_prefix": str(optix_prefix),
        "optix_include": str(optix_include),
        "optix_version": optix_version,
        "expected_optix_sdk": args.expected_optix_sdk,
        "key_headers": headers,
        "compute_capability": gpu["compute_capability"],
        "gpu": gpu,
        "cuda_visible_devices": cuda_visible_devices,
        "optix_runtime_abi_probe": optix_runtime_abi_probe,
        "language_standard": "c++17",
        "optimization": "O3",
        "position_independent_code": True,
        "geos_mode": geos_mode,
        "geos_cflags": geos_cflags,
        "geos_libraries": geos_libraries,
        "library_dirs": [str(path) for path in library_dirs],
    }
    build_input_sha256 = _digest(build_input)

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", suffix=".partial", dir=output.parent
    )
    os.close(descriptor)
    temporary_output = Path(temporary_name)
    temporary_output.unlink()
    command = _build_command(
        nvcc=nvcc,
        host_compiler=host_compiler,
        optix_include=optix_include,
        cuda_include=cuda_include,
        cuda_system_include=system_include,
        build_id=build_input_sha256,
        compute_capability=capability,
        geos_cflags=geos_cflags,
        geos_libraries=geos_libraries,
        library_dirs=library_dirs,
        nvrtc_library=nvrtc_library,
        output=temporary_output,
    )
    try:
        with log.open("x", encoding="utf-8", newline="\n") as stream:
            process = subprocess.Popen(
                command,
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if process.stdout is None:
                raise RuntimeError("native build output pipe is unavailable")
            for line in process.stdout:
                stream.write(line)
                stream.flush()
                print(line, end="", flush=True)
            status = process.wait()
        if status:
            raise RuntimeError(f"native build failed ({status}); see {log}")
        if not temporary_output.is_file() or temporary_output.stat().st_size == 0:
            raise RuntimeError("native build produced no shared library")
        nm = shutil.which("nm")
        if nm is None:
            raise RuntimeError("nm is required for exported-symbol verification")
        exported_text = _capture(
            [nm, "-D", "--defined-only", str(temporary_output)]
        )
        exported_names = {
            line.split()[-1]
            for line in exported_text.splitlines()
            if line.split()
        }
        missing = [name for name in REQUIRED_SYMBOLS if name not in exported_names]
        if missing:
            raise RuntimeError(f"required Goal5838 symbols are missing: {missing}")
        native_bytes = temporary_output.stat().st_size
        native_sha256 = _file_sha256(temporary_output)
        dynamic_dependencies = _capture(["ldd", str(temporary_output)])
        dynamic_nvrtc = _resolve_ldd_dependency(
            dynamic_dependencies, "libnvrtc.so"
        )
        if dynamic_nvrtc != nvrtc_library:
            raise RuntimeError(
                "provider DSO resolves NVRTC from a different file: "
                f"{dynamic_nvrtc} != {nvrtc_library}"
            )
        dynamic_nvrtc_identity = {
            "path": str(dynamic_nvrtc),
            "bytes": dynamic_nvrtc.stat().st_size,
            "sha256": _file_sha256(dynamic_nvrtc),
        }
        _publish_exclusive(temporary_output, output)
    finally:
        temporary_output.unlink(missing_ok=True)

    repository = _repository_after(repository_before)
    if (
        _file_sha256(nvcc) != build_input["nvcc_sha256"]
        or _capture([str(nvcc), "--version"]) != build_input["nvcc_version"]
        or nvrtc_library.stat().st_size != build_input["nvrtc_library_bytes"]
        or _file_sha256(nvrtc_library) != build_input["nvrtc_library_sha256"]
        or _file_sha256(host_compiler) != build_input["host_compiler_sha256"]
        or _capture([str(host_compiler), "--version"])
        != build_input["host_compiler_version"]
        or _header_rows(optix_include, cuda_include) != headers
        or _gpu_identity() != gpu
    ):
        output.unlink(missing_ok=True)
        raise RuntimeError("toolchain identity changed during native build")

    reproduction_command = [
        str(output) if item == str(temporary_output) else item
        for item in command
    ]
    result = {
        "schema": RESULT_DOMAIN,
        "status": "PASS__FRESH_PROVIDER_DSO_AND_REQUIRED_ABI_EXPORTED",
        "repository": repository,
        "build_input": build_input,
        "build_input_sha256": build_input_sha256,
        "executed_command": command,
        "executed_command_display": shlex.join(command),
        "reproduction_command": reproduction_command,
        "reproduction_command_display": shlex.join(reproduction_command),
        "build_log": {
            "path": str(log),
            "bytes": log.stat().st_size,
            "sha256": _file_sha256(log),
        },
        "native_output": {
            "path": str(output),
            "bytes": native_bytes,
            "sha256": native_sha256,
        },
        "required_symbols": list(REQUIRED_SYMBOLS),
        "required_symbol_check": "exact_nm_dynamic_defined_name",
        "all_required_symbols_exported": True,
        "dynamic_dependencies": dynamic_dependencies,
        "dynamic_nvrtc": dynamic_nvrtc_identity,
        "result_sha256": "",
    }
    result["result_sha256"] = _sealed_sha256(result)
    try:
        _write_json_exclusive(manifest, result)
    except Exception:
        output.unlink(missing_ok=True)
        raise
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cuda-prefix", type=Path, required=True)
    parser.add_argument("--optix-prefix", type=Path, required=True)
    parser.add_argument("--expected-optix-sdk", required=True)
    parser.add_argument("--compute-capability")
    parser.add_argument("--host-compiler", type=Path)
    parser.add_argument("--nvrtc-library", type=Path)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    result = build(parser.parse_args())
    print(
        json.dumps(
            {
                "status": result["status"],
                "native_sha256": result["native_output"]["sha256"],
                "result_sha256": result["result_sha256"],
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
