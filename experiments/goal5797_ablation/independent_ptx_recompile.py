#!/usr/bin/env python3
"""Recompile Goal5797 CUDA sources without importing PyOptiX or RTDL."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from cuda.bindings import nvrtc


def check(result, program=None):
    if result[0].value:
        log = b""
        if program is not None:
            status, size = nvrtc.nvrtcGetProgramLogSize(program)
            if not status.value:
                log = b" " * size
                nvrtc.nvrtcGetProgramLog(program, log)
        raise RuntimeError(
            f"NVRTC {result[0].value}: {log.decode(errors='replace')}")
    return None if len(result) == 1 else result[1]


def compile_ptx(source: bytes, name: str, optix: Path, cuda: Path) -> bytes:
    program = check(nvrtc.nvrtcCreateProgram(
        source, name.encode(), 0, [], []))
    options = [
        b"--std=c++17", b"--device-as-default-execution-space",
        b"--relocatable-device-code=true",
        f"-I{optix}".encode(), f"-I{cuda}".encode(),
    ]
    check(nvrtc.nvrtcCompileProgram(program, len(options), options), program)
    size = check(nvrtc.nvrtcGetPTXSize(program))
    ptx = b" " * size
    check(nvrtc.nvrtcGetPTX(program, ptx))
    return ptx


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--expected-result", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    expected = json.loads(args.expected_result.read_bytes())
    rows = []
    for name, identity in sorted(expected["identities"].items()):
        source_path = args.source_dir / f"{name}.cu"
        source = source_path.read_bytes()
        ptx = compile_ptx(
            source, source_path.name, args.optix_include, args.cuda_include)
        row = {
            "name": name,
            "source_sha256": sha(source),
            "expected_source_sha256": identity["device_source_sha256"],
            "recompiled_ptx_sha256": sha(ptx),
            "expected_loaded_ptx_sha256": identity["loaded_ptx_sha256"],
        }
        row["passed"] = (
            row["source_sha256"] == row["expected_source_sha256"]
            and row["recompiled_ptx_sha256"]
            == row["expected_loaded_ptx_sha256"])
        rows.append(row)
    result = {
        "schema": "rtdl.goal5797.independent_ptx_recompile.v1",
        "status": "PASS" if all(row["passed"] for row in rows) else "FAIL",
        "imports_pyoptix": False,
        "imports_rtdl": False,
        "source_count": len(rows),
        "byte_identical_ptx_count": sum(row["passed"] for row in rows),
        "rows": rows,
        "registered_performance_timing_count": 0,
    }
    args.output.write_bytes(json.dumps(
        result, indent=2, sort_keys=True).encode() + b"\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
