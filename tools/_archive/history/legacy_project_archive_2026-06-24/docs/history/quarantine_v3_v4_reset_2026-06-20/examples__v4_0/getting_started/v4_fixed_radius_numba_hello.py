#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def _stream_ptr(stream) -> int:
    handle = getattr(stream, "handle", None)
    value = getattr(handle, "value", handle)
    return int(value or 0)


def _device_columns(cuda, stream, *, ids, x, y) -> dict[str, object]:
    return {
        "ids": cuda.to_device(np.asarray(ids, dtype=np.uint32), stream=stream),
        "x": cuda.to_device(np.asarray(x, dtype=np.float64), stream=stream),
        "y": cuda.to_device(np.asarray(y, dtype=np.float64), stream=stream),
    }


def run() -> dict[str, object]:
    try:
        from numba import cuda
        import rtdsl
    except Exception as exc:  # pragma: no cover - depends on local GPU env
        raise RuntimeError(
            "V4 Numba hello requires Numba CUDA, this source tree on PYTHONPATH, and build/librtdl_optix.so"
        ) from exc
    if not cuda.is_available():
        raise RuntimeError("Numba CUDA is not available")

    stream = cuda.stream()
    search = _device_columns(
        cuda,
        stream,
        ids=[10, 11, 12],
        x=[0.0, 4.0, 9.0],
        y=[0.0, 0.0, 9.0],
    )
    query = _device_columns(
        cuda,
        stream,
        ids=[1, 2, 3],
        x=[0.0, 4.0, 1.5],
        y=[0.0, 0.0, 1.5],
    )
    outputs = {
        "query_ids": cuda.device_array((3,), dtype=np.uint32, stream=stream),
        "neighbor_counts": cuda.device_array((3,), dtype=np.uint32, stream=stream),
        "threshold_flags": cuda.device_array((3,), dtype=np.uint32, stream=stream),
    }

    result = rtdsl.run_v4_fixed_radius_count_threshold_2d(
        query,
        search,
        radius=1.1,
        threshold=1,
        partner="numba",
        output_columns=outputs,
        stream=stream,
        return_metadata=True,
    )
    stream.synchronize()

    observed = {
        name: [int(value) for value in column.copy_to_host(stream=stream).tolist()]
        for name, column in outputs.items()
    }
    stream.synchronize()
    expected = {
        "query_ids": [1, 2, 3],
        "neighbor_counts": [1, 1, 0],
        "threshold_flags": [1, 1, 0],
    }
    if observed != expected:
        raise AssertionError(f"unexpected V4 Numba output: observed={observed!r} expected={expected!r}")

    metadata = result["metadata"]
    return {
        "status": "pass",
        "framework": "numba",
        "route_id": metadata["v4_route_id"],
        "observed": observed,
        "expected": expected,
        "metadata_subset": {
            "caller_stream_handle_nonzero": int(metadata["caller_stream_handle"]) != 0,
            "caller_stream_matches_numba_stream": int(metadata["caller_stream_handle"]) == _stream_ptr(stream),
            "native_synchronized_before_return": bool(metadata["native_synchronized_before_return"]),
            "native_async_ready": bool(metadata["native_async_ready"]),
        },
        "claim_boundaries": {
            "v4_current_front_door_authorized": True,
            "package_install_claim_authorized": False,
            "full_numba_surface_claim_authorized": False,
            "public_true_zero_copy_claim_authorized": False,
            "async_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
        },
    }


def main() -> int:
    print(json.dumps(run(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
