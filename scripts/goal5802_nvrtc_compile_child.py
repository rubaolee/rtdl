#!/usr/bin/env python3
"""Fresh-process, untimed NVRTC compiler child for Goal5802.

The parent preserves the exact argv, stdout/stderr, product and this receipt.
This child deliberately has no benchmarking clock and never launches GPU work.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

# The parent intentionally launches this script by absolute path from an
# arbitrary qualification directory. Anchor project imports to the script's
# checked-out source tree instead of relying on the caller's current directory
# or PYTHONPATH.
_SOURCE_ROOT = Path(__file__).resolve(strict=True).parents[1]
sys.path.insert(0, str(_SOURCE_ROOT))

from experiments.goal5802_premeasurement.runtime_manifest import digest
from scripts.goal5802_prepare_matched_ptx_untimed import architecture_contract


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_create_only(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _loaded_nvrtc_identity(nvrtc: object) -> dict[str, object]:
    result = nvrtc.nvrtcVersion()
    if not isinstance(result, tuple) or len(result) != 3 \
            or getattr(result[0], "value", result[0]) != 0:
        raise RuntimeError("fresh NVRTC child version query failed")
    libraries: set[Path] = set()
    builtins: set[Path] = set()
    for line in Path("/proc/self/maps").read_text(
            encoding="utf-8").splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) == 6 and fields[5].startswith("/"):
            candidate = Path(fields[5]).resolve(strict=True)
            if candidate.name.startswith("libnvrtc-builtins.so"):
                builtins.add(candidate)
            elif candidate.name.startswith("libnvrtc.so"):
                libraries.add(candidate)
    if len(libraries) != 1 or len(builtins) != 1:
        raise RuntimeError(
            "fresh NVRTC child loaded DSO set ambiguous: "
            f"library={sorted(map(str, libraries))}, "
            f"builtins={sorted(map(str, builtins))}")

    def record(path: Path) -> dict[str, object]:
        metadata = path.lstat()
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
            raise RuntimeError(
                "fresh NVRTC child DSO is not canonical regular file")
        return {
            "path": str(path), "bytes": metadata.st_size,
            "sha256": _sha(path), "canonical_regular_file": True,
            "symlink": False,
        }

    return {
        "library": record(next(iter(libraries))),
        "builtins": record(next(iter(builtins))),
        "version": [int(result[1]), int(result[2])],
    }


def _check_nvrtc(nvrtc: object, result: tuple[object, ...],
                 program: object | None = None) -> object:
    """Check one NVRTC result without importing either measured Python arm."""

    if not isinstance(result, tuple) or not result:
        raise RuntimeError("fresh NVRTC child result envelope differs")
    status = getattr(result[0], "value", result[0])
    if status:
        log = ""
        if program is not None:
            log_result = nvrtc.nvrtcGetProgramLogSize(program)
            if isinstance(log_result, tuple) and len(log_result) == 2 \
                    and getattr(log_result[0], "value", log_result[0]) == 0:
                buffer = b" " * int(log_result[1])
                nvrtc.nvrtcGetProgramLog(program, buffer)
                log = buffer.decode(errors="replace")
        error = nvrtc.nvrtcGetErrorString(result[0])
        message = error[1] if isinstance(error, tuple) and len(error) == 2 \
            else "unknown NVRTC error"
        raise RuntimeError(f"NVRTC {status}: {message}\n{log}")
    if len(result) == 1:
        return None
    if len(result) == 2:
        return result[1]
    return result[1:]


def _compile(
        *, mode: str, source: Path, optix_include: Path | None,
        cuda_include: Path | None, compute_capability: str,
        ) -> tuple[bytes, list[str], str]:
    from cuda.bindings import nvrtc

    canonical, compute_arch, sm_arch = architecture_contract(
        compute_capability)
    if mode == "ptx":
        if optix_include is None or cuda_include is None:
            raise RuntimeError("PTX child requires both include roots")
        options = [
            "--std=c++17", "--device-as-default-execution-space",
            "--relocatable-device-code=true",
            f"--gpu-architecture={compute_arch}",
            f"-I{optix_include}", f"-I{cuda_include}",
            f"-I{cuda_include / 'nv'}",
        ]
    else:
        options = [
            "--std=c++17", "--device-as-default-execution-space",
            f"--gpu-architecture={sm_arch}",
        ]
    source_bytes = source.read_bytes()
    program = _check_nvrtc(nvrtc, nvrtc.nvrtcCreateProgram(
        source_bytes, source.name.encode(), 0, [], []))
    encoded = [item.encode() for item in options]
    _check_nvrtc(
        nvrtc, nvrtc.nvrtcCompileProgram(program, len(encoded), encoded),
        program)
    if mode == "ptx":
        size = _check_nvrtc(nvrtc, nvrtc.nvrtcGetPTXSize(program))
        product = b" " * size
        _check_nvrtc(nvrtc, nvrtc.nvrtcGetPTX(program, product))
        targets = [item.decode("ascii") for item in re.findall(
            rb"(?m)^\.target[ \t]+(sm_[0-9]+)(?:[ \t,\r\n]|$)",
            product)]
        if targets != [sm_arch]:
            raise RuntimeError(
                f"fresh NVRTC child PTX target differs: {targets}")
    else:
        size = _check_nvrtc(nvrtc, nvrtc.nvrtcGetCUBINSize(program))
        product = b" " * size
        _check_nvrtc(nvrtc, nvrtc.nvrtcGetCUBIN(program, product))
        if product[:4] != b"\x7fELF":
            raise RuntimeError("fresh NVRTC child cubin is not ELF")
    if canonical != compute_capability:
        raise RuntimeError("fresh NVRTC child canonical CC differs")
    return product, options, sm_arch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("ptx", "cubin"), required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path)
    parser.add_argument("--cuda-include", type=Path)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--nvrtc-library", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    if not source.is_file():
        raise RuntimeError("fresh NVRTC child source is not a file")
    optix = args.optix_include.resolve(strict=True) \
        if args.optix_include is not None else None
    cuda = args.cuda_include.resolve(strict=True) \
        if args.cuda_include is not None else None
    nvrtc_library = args.nvrtc_library.resolve(strict=True) \
        if args.nvrtc_library is not None else None
    if nvrtc_library is not None:
        metadata = nvrtc_library.lstat()
        if not stat.S_ISREG(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
            raise RuntimeError("pinned NVRTC library is not a regular file")
    try:
        # cuda-python's pathfinder may prefer an independently installed
        # nvidia-cuda-nvrtc wheel even when LD_LIBRARY_PATH names the frozen
        # toolkit.  Preload the manifest-bound DSO into RTLD_GLOBAL so the
        # binding's RTLD_DEFAULT probe uses the exact cross-arm library.
        pinned_nvrtc_handle = ctypes.CDLL(
            str(nvrtc_library), mode=os.RTLD_NOW | os.RTLD_GLOBAL) \
            if nvrtc_library is not None else None
        product, options, target = _compile(
            mode=args.mode, source=source, optix_include=optix,
            cuda_include=cuda, compute_capability=args.compute_capability)
        if nvrtc_library is not None and pinned_nvrtc_handle is None:
            raise RuntimeError("pinned NVRTC library handle was not retained")
    except Exception as error:
        from cuda.bindings import nvrtc
        try:
            loaded_nvrtc: object = _loaded_nvrtc_identity(nvrtc)
        except Exception as identity_error:
            loaded_nvrtc = {
                "identity_capture_failed": type(identity_error).__name__,
                "identity_capture_error": str(identity_error),
            }
        failure: dict[str, object] = {
            "schema": "rtdl.goal5802.fresh_nvrtc_compile_failure.v2",
            "status": "FAIL__FRESH_PROCESS_NVRTC_COMPILE__NO_PRODUCT",
            "pid": os.getpid(), "parent_pid": os.getppid(),
            "argv": sys.argv,
            "cwd": str(Path.cwd().resolve(strict=True)),
            "mode": args.mode,
            "source": {
                "path": str(source), "bytes": source.stat().st_size,
                "sha256": _sha(source)},
            "include_roots": {
                "optix": str(optix) if optix is not None else None,
                "cuda": str(cuda) if cuda is not None else None,
            },
            "compute_capability": args.compute_capability,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "loaded_nvrtc": loaded_nvrtc,
            "product_created": False,
            "clock_read_count": 0, "gpu_kernel_launch_count": 0,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
        }
        failure["receipt_sha256"] = digest(failure)
        _write_create_only(
            args.receipt,
            json.dumps(failure, indent=2, sort_keys=True).encode("utf-8")
            + b"\n")
        print(json.dumps({
            "status": failure["status"], "pid": failure["pid"],
            "error_type": failure["error_type"],
            "error_message": failure["error_message"],
            "receipt_sha256": failure["receipt_sha256"],
        }, sort_keys=True), file=sys.stderr)
        return 17
    from cuda.bindings import nvrtc
    _write_create_only(args.output, product)
    value: dict[str, object] = {
        "schema": "rtdl.goal5802.fresh_nvrtc_compile_child.v2",
        "status": "PASS__FRESH_PROCESS_UNTIMED_NVRTC_COMPILE",
        "pid": os.getpid(),
        "parent_pid": os.getppid(),
        "argv": sys.argv,
        "cwd": str(Path.cwd().resolve(strict=True)),
        "mode": args.mode,
        "source": {
            "path": str(source), "bytes": source.stat().st_size,
            "sha256": _sha(source)},
        "include_roots": {
            "optix": str(optix) if optix is not None else None,
            "cuda": str(cuda) if cuda is not None else None,
        },
        "compute_capability": args.compute_capability,
        "compile_options": options,
        "target": target,
        "product": {
            "path": str(args.output.resolve(strict=True)),
            "bytes": len(product),
            "sha256": hashlib.sha256(product).hexdigest()},
        "loaded_nvrtc": _loaded_nvrtc_identity(nvrtc),
        "clock_read_count": 0,
        "gpu_kernel_launch_count": 0,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    value["receipt_sha256"] = digest(value)
    _write_create_only(
        args.receipt,
        json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": value["status"], "pid": value["pid"],
        "product_sha256": value["product"]["sha256"],
        "receipt_sha256": value["receipt_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
