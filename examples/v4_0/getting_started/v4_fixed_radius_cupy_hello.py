#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def run() -> dict[str, object]:
    try:
        import cupy as cp
        import rtdsl
    except Exception as exc:  # pragma: no cover - depends on local GPU env
        raise RuntimeError(
            "V4 CuPy hello requires CuPy, this source tree on PYTHONPATH, and build/librtdl_optix.so"
        ) from exc

    search = {
        "ids": cp.asarray([10, 11, 12], dtype=cp.uint32),
        "x": cp.asarray([0.0, 3.0, 0.0], dtype=cp.float64),
        "y": cp.asarray([0.0, 0.0, 4.0], dtype=cp.float64),
    }
    query = {
        "ids": cp.asarray([1, 2, 3], dtype=cp.uint32),
        "x": cp.asarray([0.0, 3.0, 9.0], dtype=cp.float64),
        "y": cp.asarray([0.0, 0.0, 9.0], dtype=cp.float64),
    }
    outputs = {
        "query_ids": cp.zeros((3,), dtype=cp.uint32),
        "neighbor_counts": cp.zeros((3,), dtype=cp.uint32),
        "threshold_flags": cp.zeros((3,), dtype=cp.uint32),
    }

    stream = cp.cuda.Stream(non_blocking=True)
    with stream:
        result = rtdsl.run_v4_fixed_radius_count_threshold_2d(
            query,
            search,
            radius=1.1,
            threshold=1,
            partner="cupy",
            output_columns=outputs,
            stream=stream.ptr,
            return_metadata=True,
        )
    stream.synchronize()

    observed = {name: [int(value) for value in outputs[name].get().tolist()] for name in outputs}
    expected = {
        "query_ids": [1, 2, 3],
        "neighbor_counts": [1, 1, 0],
        "threshold_flags": [1, 1, 0],
    }
    if observed != expected:
        raise AssertionError(f"unexpected V4 CuPy output: observed={observed!r} expected={expected!r}")

    metadata = result["metadata"]
    return {
        "status": "pass",
        "framework": "cupy",
        "route_id": metadata["v4_route_id"],
        "observed": observed,
        "expected": expected,
        "metadata_subset": {
            "caller_stream_handle_nonzero": int(metadata["caller_stream_handle"]) != 0,
            "native_synchronized_before_return": bool(metadata["native_synchronized_before_return"]),
            "native_async_ready": bool(metadata["native_async_ready"]),
            "named_cuda_columns_no_host_stage_authorized": bool(
                metadata["named_cuda_columns_no_host_stage_authorized"]
            ),
        },
        "claim_boundaries": {
            "v4_current_front_door_authorized": True,
            "package_install_claim_authorized": False,
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
