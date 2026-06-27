#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from importlib import metadata
from pathlib import Path
import sys
import traceback
from typing import Any


PACKAGE_REQUIREMENTS = {
    "cupy-cuda12x": "14.1.1",
    "torch": "2.6.0+cu124",
    "numba": "0.65.1",
    "nvidia-cuda-nvcc-cu12": "12.4.131",
    "nvidia-cuda-nvrtc-cu12": "12.9.86",
    "nvidia-cuda-runtime-cu12": "12.9.79",
}

ENV_KEYS = (
    "NUMBA_CUDA_PREFIX",
    "CUDA_HOME",
    "CUDA_PATH",
    "RTDL_OPTIX_LIBRARY",
    "RTDL_EMBREE_LIBRARY",
)


def package_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in ("cupy", *PACKAGE_REQUIREMENTS):
        try:
            versions[name] = metadata.version(name)
        except Exception as exc:
            versions[name] = f"missing: {exc}"
    return versions


def env_snapshot() -> dict[str, str | None]:
    return {key: os.environ.get(key) for key in ENV_KEYS}


def cupy_rawkernel_check() -> dict[str, Any]:
    try:
        import cupy as cp

        code = r"""
        extern "C" __global__ void add_one(const float* x, float* y) {
            int i = blockDim.x * blockIdx.x + threadIdx.x;
            if (i < 8) y[i] = x[i] + 1.0f;
        }
        """
        kernel = cp.RawKernel(code, "add_one")
        x = cp.arange(8, dtype=cp.float32)
        y = cp.zeros_like(x)
        kernel((1,), (32,), (x, y))
        cp.cuda.Stream.null.synchronize()
        return {
            "status": "pass",
            "cupy_version": cp.__version__,
            "runtime_version": cp.cuda.runtime.runtimeGetVersion(),
            "local_runtime_version": cp.cuda.get_local_runtime_version(),
            "driver_version": cp.cuda.runtime.driverGetVersion(),
            "result": y.get().tolist(),
        }
    except Exception as exc:  # pragma: no cover - requires CUDA stack
        return {"status": "fail", "error": repr(exc), "traceback": traceback.format_exc()[-2000:]}


def torch_cuda_check() -> dict[str, Any]:
    try:
        import torch

        available = torch.cuda.is_available()
        payload: dict[str, Any] = {
            "status": "pass" if available else "fail",
            "torch_version": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "cuda_available": available,
        }
        if available:
            tensor = torch.arange(8, device="cuda", dtype=torch.float32) + 2
            torch.cuda.synchronize()
            payload["result"] = tensor.cpu().tolist()
        return payload
    except Exception as exc:  # pragma: no cover - requires CUDA stack
        return {"status": "fail", "error": repr(exc), "traceback": traceback.format_exc()[-2000:]}


def numba_cuda_jit_check() -> dict[str, Any]:
    try:
        from rtdsl.numba_partner_continuation import configure_numba_cuda_toolchain_environment

        configure_numba_cuda_toolchain_environment()
        import numpy as np
        from numba import cuda

        @cuda.jit
        def add_three(x, y):  # pragma: no cover - compiled on GPU
            i = cuda.grid(1)
            if i < x.size:
                y[i] = x[i] + 3.0

        xh = np.arange(8, dtype=np.float32)
        yh = np.zeros_like(xh)
        xd = cuda.to_device(xh)
        yd = cuda.to_device(yh)
        add_three[1, 32](xd, yd)
        cuda.synchronize()
        return {"status": "pass", "result": yd.copy_to_host().tolist()}
    except Exception as exc:  # pragma: no cover - requires CUDA stack
        return {"status": "fail", "error": repr(exc), "traceback": traceback.format_exc()[-2000:]}


def build_payload(*, dry_run: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "tool": "v3_gpu_python_env_gate",
        "status": "dry_run" if dry_run else "unknown",
        "python": sys.version,
        "required_packages": PACKAGE_REQUIREMENTS,
        "packages": package_versions(),
        "env": env_snapshot(),
        "checks": {},
    }
    if dry_run:
        payload["note"] = "Dry run records package requirements and environment keys without importing GPU libraries."
        return payload

    payload["checks"] = {
        "cupy_rawkernel": cupy_rawkernel_check(),
        "torch_cuda": torch_cuda_check(),
        "numba_cuda_jit": numba_cuda_jit_check(),
    }
    payload["status"] = "pass" if all(check.get("status") == "pass" for check in payload["checks"].values()) else "fail"
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the V3 GPU Python environment gate.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(dry_run=args.dry_run)
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] in {"pass", "dry_run"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
