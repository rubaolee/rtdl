#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


class DLPackOnlyColumn:
    """Expose a CuPy-backed column through DLPack metadata only."""

    def __init__(self, array) -> None:
        self.array = array
        self.dtype = array.dtype
        self.shape = array.shape
        self.strides = array.strides

    def data_ptr(self) -> int:
        return int(self.array.data.ptr)

    def __dlpack__(self, stream=None):
        if stream is None:
            return self.array.__dlpack__()
        try:
            return self.array.__dlpack__(stream=stream)
        except TypeError:
            return self.array.__dlpack__()

    def __dlpack_device__(self):
        return self.array.__dlpack_device__()


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


def _wrap(columns: dict[str, object]) -> dict[str, DLPackOnlyColumn]:
    wrapped = {name: DLPackOnlyColumn(column) for name, column in columns.items()}
    for name, column in wrapped.items():
        if hasattr(column, "__cuda_array_interface__"):
            raise AssertionError(f"DLPack bridge column {name!r} unexpectedly exposes CUDA Array Interface")
    return wrapped


def _ptrs(prefix: str, columns: dict[str, object]) -> dict[str, int]:
    return {f"{prefix}.{name}": int(column.data.ptr) for name, column in columns.items()}


def run_smoke() -> dict[str, object]:
    import cupy as cp
    import rtdsl

    search_arrays = {
        "ids": cp.asarray([10, 11, 12], dtype=cp.uint32),
        "x": cp.asarray([0.0, 4.0, 9.0], dtype=cp.float64),
        "y": cp.asarray([0.0, 0.0, 9.0], dtype=cp.float64),
    }
    query_arrays = {
        "ids": cp.asarray([1, 2, 3], dtype=cp.uint32),
        "x": cp.asarray([0.0, 4.0, 1.5], dtype=cp.float64),
        "y": cp.asarray([0.0, 0.0, 1.5], dtype=cp.float64),
    }
    output_arrays = {
        "query_ids": cp.zeros((3,), dtype=cp.uint32),
        "neighbor_counts": cp.zeros((3,), dtype=cp.uint32),
        "threshold_flags": cp.zeros((3,), dtype=cp.uint32),
    }
    expected_ptrs = {}
    expected_ptrs.update(_ptrs("search", search_arrays))
    expected_ptrs.update(_ptrs("query", query_arrays))
    expected_ptrs.update(_ptrs("output", output_arrays))

    stream = cp.cuda.Stream(non_blocking=True)
    with stream:
        result = rtdsl.run_v4_fixed_radius_count_threshold_2d(
            _wrap(query_arrays),
            _wrap(search_arrays),
            radius=1.1,
            threshold=1,
            partner="cupy",
            output_columns=_wrap(output_arrays),
            stream=stream.ptr,
            return_metadata=True,
        )
    stream.synchronize()

    observed = {name: output_arrays[name].get().tolist() for name in output_arrays}
    expected = {
        "query_ids": [1, 2, 3],
        "neighbor_counts": [1, 1, 0],
        "threshold_flags": [1, 1, 0],
    }
    if observed != expected:
        raise AssertionError(f"unexpected DLPack bridge output: observed={observed!r} expected={expected!r}")

    metadata = result["metadata"]
    plan = metadata["v4_plan"]
    source_protocols = list(plan["source_protocols"])
    if source_protocols != ["dlpack"]:
        raise AssertionError(f"unexpected source protocols for DLPack bridge smoke: {source_protocols!r}")

    plan_ptrs = plan["borrowed_device_pointers"]
    pointer_identity = {name: int(plan_ptrs[name]) == int(ptr) for name, ptr in expected_ptrs.items()}
    if not all(pointer_identity.values()):
        raise AssertionError(f"DLPack bridge pointer identity failed: {pointer_identity!r}")

    native_pointer_echo = metadata["native_call_device_pointer_echo"]
    echo_expected = {name: ptr for name, ptr in expected_ptrs.items() if not name.startswith("search.")}
    pointer_echo_identity = {
        name: int(native_pointer_echo.get(name, 0)) == int(ptr) for name, ptr in echo_expected.items()
    }
    if not metadata["native_call_device_pointer_echo_complete"]:
        raise AssertionError("native pointer echo is incomplete")
    if not all(pointer_echo_identity.values()):
        raise AssertionError(f"DLPack bridge pointer echo failed: {pointer_echo_identity!r}")
    if int(metadata["caller_stream_handle"]) != int(stream.ptr):
        raise AssertionError("metadata did not preserve DLPack bridge caller stream")
    if metadata["native_async_ready"]:
        raise AssertionError("DLPack bridge smoke must not authorize async")
    if metadata["v4_true_zero_copy_claim_authorized"]:
        raise AssertionError("DLPack bridge smoke must not authorize public true-zero-copy")

    return {
        "status": "pass-with-boundary",
        "route_id": "fixed_radius_count_threshold_2d",
        "framework": "cupy_backed_dlpack_only_wrapper",
        "protocol": "dlpack_bridge_wrapper",
        "hardware": _hardware(),
        "validation": {
            "output_match": True,
            "observed": observed,
            "expected": expected,
            "all_wrappers_hide_cuda_array_interface": True,
        },
        "metadata_subset": {
            "source_protocols": source_protocols,
            "caller_stream_handle_nonzero": int(metadata["caller_stream_handle"]) != 0,
            "prepare_stream_handle_nonzero": int(metadata["prepare_stream_handle"]) != 0,
            "caller_stream_native_propagation_ready": bool(metadata["caller_stream_native_propagation_ready"]),
            "native_prepare_stream_propagation_ready": bool(metadata["native_prepare_stream_propagation_ready"]),
            "native_synchronized_before_return": bool(metadata["native_synchronized_before_return"]),
            "native_async_ready": bool(metadata["native_async_ready"]),
            "native_call_device_pointer_echo_complete": bool(metadata["native_call_device_pointer_echo_complete"]),
            "named_cuda_columns_no_host_stage_authorized": bool(
                metadata["named_cuda_columns_no_host_stage_authorized"]
            ),
            "v4_true_zero_copy_claim_authorized": bool(metadata["v4_true_zero_copy_claim_authorized"]),
        },
        "pointer_identity": pointer_identity,
        "pointer_echo_identity": pointer_echo_identity,
        "claim_boundaries": {
            "dlpack_bridge_wrapper_claim_authorized": True,
            "full_dlpack_capsule_route_claim_authorized": False,
            "dlpack_route_claim_authorized": False,
            "pytorch_route_claim_authorized": False,
            "async_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "v4_true_zero_copy_claim_authorized": False,
            "reason": (
                "This smoke validates a CuPy-backed DLPack-only wrapper through the generic DLPack "
                "adapter on the V4 M1 route. It does not validate arbitrary DLPack capsule "
                "ownership/deleter semantics, PyTorch, async, true-zero-copy, or speedup wording."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V4 M1 DLPack bridge wrapper smoke.")
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
