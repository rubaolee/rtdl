#!/usr/bin/env python3
"""Fresh target-local Numba/NVRTC producer observation for Goal5791.

This helper compiles no application input and records no elapsed value.  It
forces one Numba device PTX compile for sm_89 and one unique CuPy RawKernel
compile/launch in an initially empty private recipe cache, then records the
actual NVVM, libdevice, NVRTC, and NVRTC-builtins paths and bytes used by the
process.  The enclosing create-only target prepare traces file opens and
rejects foreign producer binaries before formal worker zero.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _directives(ptx: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for line in ptx.splitlines():
        match = re.match(
            r"^\s*\.(version|target|address_size)\s+(.+?)\s*$", line)
        if match:
            key = match.group(1)
            if key in found:
                raise RuntimeError(
                    "Goal5791 target Numba probe has a duplicate PTX directive")
            found[key] = match.group(2)
    if set(found) != {"version", "target", "address_size"}:
        raise RuntimeError("Goal5791 target Numba probe PTX directives drifted")
    return found


def _loaded_paths(prefix: str) -> list[str]:
    result: set[str] = set()
    for line in Path("/proc/self/maps").read_text(
        encoding="utf-8", errors="strict",
    ).splitlines():
        tail = line.rsplit(None, 1)[-1]
        if tail.startswith("/") and Path(tail).name.startswith(prefix):
            result.add(str(Path(tail).resolve()))
    return sorted(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    cache_spelling = os.environ.get("CUPY_CACHE_DIR")
    if not cache_spelling:
        raise RuntimeError("Goal5791 target producer cache is not isolated")
    cache = Path(cache_spelling)
    if cache.is_symlink() or not cache.is_dir() or any(cache.iterdir()):
        raise RuntimeError(
            "Goal5791 target producer cache is not initially empty")

    import cupy as cp
    import llvmlite
    import numba
    from numba import cuda, types
    from numba.cuda.cuda_paths import get_cuda_paths
    import numpy as np
    import platform

    selected = get_cuda_paths()
    nvvm = selected["nvvm"]
    libdevice = selected["libdevice"]
    nvvm_path = Path(str(nvvm.info)).resolve()
    libdevice_path = Path(str(libdevice.info)).resolve()

    def goal5791_numba_target_probe(value):
        return value + 1

    ptx, _ = cuda.compile(
        goal5791_numba_target_probe,
        types.int32(types.int32),
        debug=False,
        lineinfo=True,
        device=True,
        fastmath=False,
        cc=(8, 9),
        opt=True,
        abi="c",
        abi_info={"abi_name": "goal5791_numba_target_probe"},
        output="ptx",
    )

    # PID-bearing source plus an initially empty private cache forces the
    # producer path without making the resulting cache a scientific payload.
    raw_source = (
        f"// goal5791 forced target producer probe pid={os.getpid()}\n"
        "extern \"C\" __global__ void goal5791_nvrtc_target_probe(int* out) {"
        " if (threadIdx.x == 0 && blockIdx.x == 0) out[0] = 5791; }"
    )
    kernel = cp.RawKernel(raw_source, "goal5791_nvrtc_target_probe")
    output = cp.zeros((1,), dtype=cp.int32)
    kernel((1,), (1,), (output,))
    cp.cuda.runtime.deviceSynchronize()
    probe_output = int(cp.asnumpy(output)[0])
    if probe_output != 5791:
        raise RuntimeError("Goal5791 target NVRTC producer probe output drifted")

    nvvm_paths = _loaded_paths("libnvvm")
    nvrtc_paths = _loaded_paths("libnvrtc")
    observation = {
        "schema": "rtdl.goal5791.target_ptx_producer_observation.v1",
        "python": platform.python_version(),
        "numba": numba.__version__,
        "numpy": np.__version__,
        "llvmlite": llvmlite.__version__,
        "cupy": cp.__version__,
        "cuda_home": os.environ.get("CUDA_HOME"),
        "cuda_path": os.environ.get("CUDA_PATH"),
        "numba_selected_nvvm_by": nvvm.by,
        "numba_selected_nvvm_path": str(nvvm_path),
        "numba_selected_nvvm_sha256": _sha(nvvm_path),
        "numba_selected_libdevice_by": libdevice.by,
        "numba_selected_libdevice_path": str(libdevice_path),
        "numba_selected_libdevice_sha256": _sha(libdevice_path),
        "numba_probe_ptx_sha256": hashlib.sha256(ptx.encode()).hexdigest(),
        "numba_probe_ptx_directives": _directives(ptx),
        "loaded_nvvm_paths": nvvm_paths,
        "loaded_nvvm_sha256": {
            path: _sha(Path(path)) for path in nvvm_paths
        },
        "cupy_nvrtc_runtime_version": list(cp.cuda.nvrtc.getVersion()),
        "nvrtc_probe_source_sha256": hashlib.sha256(
            raw_source.encode()).hexdigest(),
        "nvrtc_probe_output": probe_output,
        "loaded_nvrtc_family_paths": nvrtc_paths,
        "loaded_nvrtc_family_sha256": {
            path: _sha(Path(path)) for path in nvrtc_paths
        },
        "private_cupy_cache_initially_empty": True,
        "unique_pid_bearing_nvrtc_source": True,
        "cache_payload_is_not_authoritative_evidence": True,
        "application_input_used": False,
        "elapsed_values_recorded": False,
        "registered_performance_timing_created": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(observation, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps(observation, sort_keys=True))


if __name__ == "__main__":
    main()
