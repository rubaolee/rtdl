#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def _hardware() -> dict[str, object]:
    command = [
        "nvidia-smi",
        "--query-gpu=name,driver_version,memory.total,compute_cap",
        "--format=csv,noheader",
    ]
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return {"nvidia_smi_available": False}
    line = (completed.stdout or "").strip().splitlines()
    if not line:
        return {"nvidia_smi_available": False, "stderr": completed.stderr}
    parts = [part.strip() for part in line[0].split(",")]
    return {
        "nvidia_smi_available": True,
        "gpu": parts[0] if len(parts) > 0 else "unknown",
        "driver": parts[1] if len(parts) > 1 else "unknown",
        "memory": parts[2] if len(parts) > 2 else "unknown",
        "compute_capability": parts[3] if len(parts) > 3 else "unknown",
    }


def _stream_ptr(stream) -> int:
    handle = getattr(stream, "handle", None)
    value = getattr(handle, "value", handle)
    return int(value or 0)


def _to_device_columns(cuda, stream, ids, x, y) -> dict[str, object]:
    return {
        "ids": cuda.to_device(np.asarray(ids, dtype=np.uint32), stream=stream),
        "x": cuda.to_device(np.asarray(x, dtype=np.float64), stream=stream),
        "y": cuda.to_device(np.asarray(y, dtype=np.float64), stream=stream),
    }


def _outputs(cuda, stream, count: int) -> dict[str, object]:
    return {
        "query_ids": cuda.device_array((count,), dtype=np.uint32, stream=stream),
        "neighbor_counts": cuda.device_array((count,), dtype=np.uint32, stream=stream),
        "threshold_flags": cuda.device_array((count,), dtype=np.uint32, stream=stream),
    }


def _host_outputs(outputs: dict[str, object], stream) -> dict[str, list[int]]:
    return {
        name: [int(value) for value in column.copy_to_host(stream=stream).tolist()]
        for name, column in outputs.items()
    }


def run_smoke() -> dict[str, object]:
    from numba import cuda
    import rtdsl

    if not cuda.is_available():
        raise RuntimeError("Numba CUDA is not available")
    stream = cuda.stream()
    search = _to_device_columns(
        cuda,
        stream,
        ids=[10, 11, 12],
        x=[0.0, 4.0, 9.0],
        y=[0.0, 0.0, 9.0],
    )
    query = _to_device_columns(
        cuda,
        stream,
        ids=[1, 2, 3],
        x=[0.0, 4.0, 1.5],
        y=[0.0, 0.0, 1.5],
    )
    outputs = _outputs(cuda, stream, 3)

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

    observed = _host_outputs(outputs, stream)
    stream.synchronize()
    expected = {
        "query_ids": [1, 2, 3],
        "neighbor_counts": [1, 1, 0],
        "threshold_flags": [1, 1, 0],
    }
    if observed != expected:
        raise AssertionError(f"unexpected Numba V4 output: observed={observed!r} expected={expected!r}")
    metadata = result["metadata"]
    source_protocols = list(metadata["v4_plan"]["source_protocols"])
    if source_protocols != ["cuda_array_interface"]:
        raise AssertionError(f"unexpected source protocols for Numba smoke: {source_protocols!r}")
    if int(metadata["caller_stream_handle"]) != _stream_ptr(stream):
        raise AssertionError("metadata did not preserve Numba caller stream handle")
    if int(metadata["prepare_stream_handle"]) != _stream_ptr(stream):
        raise AssertionError("metadata did not preserve Numba prepare stream handle")
    if metadata["native_async_ready"]:
        raise AssertionError("Numba smoke must not authorize async")
    if metadata["v4_true_zero_copy_claim_authorized"]:
        raise AssertionError("Numba smoke must not authorize public true-zero-copy")

    return {
        "status": "pass-with-boundary",
        "route_id": "fixed_radius_count_threshold_2d",
        "framework": "numba",
        "protocol": "cuda_array_interface",
        "hardware": _hardware(),
        "validation": {
            "output_match": True,
            "observed": observed,
            "expected": expected,
        },
        "metadata_subset": {
            "source_protocols": source_protocols,
            "caller_stream_handle_nonzero": int(metadata["caller_stream_handle"]) != 0,
            "prepare_stream_handle_nonzero": int(metadata["prepare_stream_handle"]) != 0,
            "caller_stream_native_propagation_ready": bool(metadata["caller_stream_native_propagation_ready"]),
            "native_prepare_stream_propagation_ready": bool(metadata["native_prepare_stream_propagation_ready"]),
            "native_synchronized_before_return": bool(metadata["native_synchronized_before_return"]),
            "native_async_ready": bool(metadata["native_async_ready"]),
            "named_cuda_columns_no_host_stage_authorized": bool(
                metadata["named_cuda_columns_no_host_stage_authorized"]
            ),
            "v4_true_zero_copy_claim_authorized": bool(metadata["v4_true_zero_copy_claim_authorized"]),
        },
        "claim_boundaries": {
            "numba_device_array_route_claim_authorized": True,
            "numba_cuda_array_interface_claim_authorized": True,
            "numba_full_partner_surface_claim_authorized": False,
            "pytorch_route_claim_authorized": False,
            "dlpack_route_claim_authorized": False,
            "async_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "v4_true_zero_copy_claim_authorized": False,
            "reason": (
                "This smoke validates the V4 M1 route with Numba DeviceNDArray columns through "
                "__cuda_array_interface__. It does not validate a full Numba partner surface, "
                "PyTorch, DLPack, async, true-zero-copy, or speedup wording."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V4 M1 Numba CUDA Array Interface smoke.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    args = parser.parse_args()

    result = run_smoke()
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
