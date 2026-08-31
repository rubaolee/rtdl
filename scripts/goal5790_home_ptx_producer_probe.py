#!/usr/bin/env python3
"""Observe the exact lx1 PTX producers after real Numba and NVRTC compiles.

This fixed diagnostic compiles no application input and records no elapsed
value.  It exists only to prove that the Home functional candidate uses the
frozen CUDA 12.2 NVVM/libdevice and NVRTC/builtins producers.
"""

from __future__ import annotations

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
                raise RuntimeError("Goal5790 Numba probe PTX duplicate directive")
            found[key] = match.group(2)
    if set(found) != {"version", "target", "address_size"}:
        raise RuntimeError("Goal5790 Numba probe PTX directive set drift")
    return found


def _loaded_paths(prefix: str) -> list[str]:
    paths = set()
    for line in Path("/proc/self/maps").read_text(
            encoding="utf-8", errors="strict").splitlines():
        tail = line.rsplit(None, 1)[-1]
        if tail.startswith("/") and Path(tail).name.startswith(prefix):
            paths.add(str(Path(tail).resolve()))
    return sorted(paths)


def observe_ptx_producers() -> dict[str, object]:
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

    def goal5790_numba_probe(value):
        return value + 1

    ptx, _ = cuda.compile(
        goal5790_numba_probe,
        types.int32(types.int32),
        debug=False,
        lineinfo=True,
        device=True,
        fastmath=False,
        cc=(6, 1),
        opt=True,
        abi="c",
        abi_info={"abi_name": "goal5790_numba_probe"},
        output="ptx",
    )

    # A PID-bearing comment forces a fresh NVRTC compilation even if CuPy has
    # an ambient disk cache.  The source is diagnostic and is not an app input.
    raw_source = (
        f"// goal5790 forced producer probe pid={os.getpid()}\n"
        "extern \"C\" __global__ void goal5790_nvrtc_probe(int* output) {"
        " if (threadIdx.x == 0 && blockIdx.x == 0) output[0] = 5790; }"
    )
    kernel = cp.RawKernel(raw_source, "goal5790_nvrtc_probe")
    output = cp.zeros((1,), dtype=cp.int32)
    kernel((1,), (1,), (output,))
    cp.cuda.runtime.deviceSynchronize()
    probe_output = int(cp.asnumpy(output)[0])
    if probe_output != 5790:
        raise RuntimeError("Goal5790 NVRTC producer probe returned wrong value")

    return {
        "schema": "rtdl.goal5790.home_ptx_producer_observation.v1",
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
        "loaded_nvvm_paths": _loaded_paths("libnvvm"),
        "cupy_nvrtc_runtime_version": list(cp.cuda.nvrtc.getVersion()),
        "nvrtc_probe_source_sha256": hashlib.sha256(
            raw_source.encode()).hexdigest(),
        "nvrtc_probe_output": probe_output,
        "loaded_nvrtc_family_paths": _loaded_paths("libnvrtc"),
        "elapsed_values_recorded": False,
        "application_input_used": False,
        "registered_performance_timing_created": False,
    }


def main() -> None:
    print(json.dumps(observe_ptx_producers(), sort_keys=True))


if __name__ == "__main__":
    main()
