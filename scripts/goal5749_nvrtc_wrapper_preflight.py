#!/usr/bin/env python3
"""Compile the exact embedded Goal5749 trusted-wrapper template with NVRTC.

This is a no-GPU preflight.  It catches device-source and OptiX-intrinsic
errors before a Home/RTX functional lane is requested.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NATIVE_SOURCE = ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_nvrtc() -> ctypes.CDLL:
    for name in ("libnvrtc.so.12", "libnvrtc.so"):
        try:
            return ctypes.CDLL(name)
        except OSError:
            pass
    raise RuntimeError("libnvrtc.so is unavailable")


def _check(status: int, label: str) -> None:
    if status:
        raise RuntimeError(f"NVRTC {label} failed with status {status}")


def _compile(source: str, options: list[str]) -> tuple[str, str]:
    library = _load_nvrtc()
    program = ctypes.c_void_p()
    create = library.nvrtcCreateProgram
    create.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_char_p, ctypes.c_char_p,
                       ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]
    create.restype = ctypes.c_int
    _check(create(ctypes.byref(program), source.encode(), b"rtdl_v4_callback_wrapper.cu",
                  0, None, None), "create")
    encoded = [item.encode() for item in options]
    option_array = (ctypes.c_char_p * len(encoded))(*encoded)
    compile_program = library.nvrtcCompileProgram
    compile_program.argtypes = [ctypes.c_void_p, ctypes.c_int,
                                ctypes.POINTER(ctypes.c_char_p)]
    compile_program.restype = ctypes.c_int
    status = int(compile_program(program, len(encoded), option_array))
    log_size = ctypes.c_size_t()
    library.nvrtcGetProgramLogSize(program, ctypes.byref(log_size))
    log = ctypes.create_string_buffer(max(1, log_size.value))
    library.nvrtcGetProgramLog(program, log)
    if status:
        raise RuntimeError("NVRTC wrapper compile failed:\n" + log.value.decode(errors="replace"))
    ptx_size = ctypes.c_size_t()
    _check(library.nvrtcGetPTXSize(program, ctypes.byref(ptx_size)), "get PTX size")
    ptx = ctypes.create_string_buffer(ptx_size.value)
    _check(library.nvrtcGetPTX(program, ptx), "get PTX")
    library.nvrtcDestroyProgram(ctypes.byref(program))
    return ptx.value.decode(), log.value.decode(errors="replace")


def _template() -> str:
    source = NATIVE_SOURCE.read_text(encoding="utf-8")
    match = re.search(
        r"static std::string v4_callback_wrapper_source\(.*?R\"CUDA\((.*?)\)CUDA\";",
        source, flags=re.DOTALL)
    if not match:
        raise RuntimeError("embedded V4 wrapper template not found")
    return match.group(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--leaf-result", required=True)
    parser.add_argument("--optix-include", required=True)
    parser.add_argument("--cuda-include", required=True)
    parser.add_argument("--cc", required=True, choices=("61", "89"))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = json.loads(Path(args.leaf_result).read_text(encoding="utf-8"))
    strict = {row["role"]: row for row in result["numba_artifacts"]
              if row["numeric_mode"] == "strict"}
    required = {"intersection", "any_hit", "miss", "scalar_probe"}
    if set(strict) != required:
        raise RuntimeError(f"leaf result lacks exact strict artifact set: {set(strict)!r}")
    source = _template()
    replacements = {
        "@INTERSECTION_SYMBOL@": strict["intersection"]["abi_name"],
        "@ANY_HIT_SYMBOL@": strict["any_hit"]["abi_name"],
        "@MISS_SYMBOL@": strict["miss"]["abi_name"],
        "@SCALAR_SYMBOL@": strict["scalar_probe"]["abi_name"],
        "@INTERSECTION_NONCE@": str(strict["intersection"]["nonce_word"]),
        "@ANY_HIT_NONCE@": str(strict["any_hit"]["nonce_word"]),
        "@MISS_NONCE@": str(strict["miss"]["nonce_word"]),
    }
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    for direct in (False, True):
        for numeric_mode in ("strict", "fast"):
            candidate = source.replace("@DIRECT_ROUTE@", "1" if direct else "0")
            for old, new in replacements.items():
                candidate = candidate.replace(old, new)
            options = [
                f"-I{Path(args.optix_include).resolve()}",
                f"-I{Path(args.cuda_include).resolve()}",
                "-I/usr/include", "-I/usr/include/x86_64-linux-gnu",
                "--std=c++14", f"--gpu-architecture=compute_{args.cc}",
                "--relocatable-device-code=true", "-D__x86_64__=1", "-D__LP64__=1",
            ]
            if numeric_mode == "fast":
                options.append("--use_fast_math")
            ptx, log = _compile(candidate, options)
            stem = f"{'direct' if direct else 'ordinary_composed'}__{numeric_mode}"
            (output / f"{stem}.ptx").write_text(ptx, encoding="utf-8")
            (output / f"{stem}.log").write_text(log, encoding="utf-8")
            rows.append({
                "route": "direct_callable" if direct else "ordinary_composed",
                "wrapper_numeric_mode": numeric_mode,
                "cc": args.cc,
                "ptx_version": re.search(r"(?m)^\s*\.version\s+(\S+)", ptx).group(1),
                "ptx_target": re.search(r"(?m)^\s*\.target\s+(\S+)", ptx).group(1),
                "unresolved_leaf_symbols_present": all(
                    item["abi_name"] in ptx for item in strict.values()),
                "scalar_return_abi_present": strict["scalar_probe"]["abi_name"] in ptx,
                "direct_call_opcode_present": "_optix_call_direct_callable" in ptx
                    if direct else None,
            })
    (output / "RESULT.json").write_text(json.dumps({
        "schema": "rtdl.goal5749.nvrtc_wrapper_preflight.v1",
        "functional_gpu_execution_performed": False,
        "registered_performance_timing_count": 0,
        "rows": rows,
    }, indent=2, sort_keys=True) + "\n")
    manifest = []
    for path in sorted(item for item in output.iterdir() if item.is_file()):
        manifest.append({
            "path": path.name,
            "size": path.stat().st_size,
            "sha256": _sha256(path),
        })
    (output / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(rows, sort_keys=True))


if __name__ == "__main__":
    main()
