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


def _device_column_dict(cp, count: int) -> dict[str, object]:
    return {
        "ids": cp.empty((count,), dtype=cp.uint32),
        "x": cp.empty((count,), dtype=cp.float64),
        "y": cp.empty((count,), dtype=cp.float64),
    }


def _output_dict(cp, count: int) -> dict[str, object]:
    return {
        "query_ids": cp.empty((count,), dtype=cp.uint32),
        "neighbor_counts": cp.empty((count,), dtype=cp.uint32),
        "threshold_flags": cp.empty((count,), dtype=cp.uint32),
    }


def run_probe() -> dict[str, object]:
    import cupy as cp
    import rtdsl

    count = 4
    search = _device_column_dict(cp, count)
    query = _device_column_dict(cp, count)
    outputs = _output_dict(cp, count)
    checksum = cp.empty((), dtype=cp.uint64)
    stream = cp.cuda.Stream(non_blocking=True)
    producer_event = cp.cuda.Event()
    consumer_event = cp.cuda.Event()

    with stream:
        search["ids"][:] = cp.asarray([10, 11, 12, 13], dtype=cp.uint32)
        search["x"][:] = cp.asarray([0.0, 5.0, 0.0, 9.0], dtype=cp.float64)
        search["y"][:] = cp.asarray([0.0, 0.0, 5.0, 9.0], dtype=cp.float64)
        query["ids"][:] = cp.asarray([1, 2, 3, 4], dtype=cp.uint32)
        query["x"][:] = cp.asarray([0.0, 5.0, 2.5, 9.0], dtype=cp.float64)
        query["y"][:] = cp.asarray([0.0, 0.0, 2.5, 9.0], dtype=cp.float64)
        outputs["query_ids"].fill(cp.uint32(777))
        outputs["neighbor_counts"].fill(cp.uint32(777))
        outputs["threshold_flags"].fill(cp.uint32(777))
        producer_event.record(stream)

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

        checksum[...] = cp.sum(
            outputs["query_ids"].astype(cp.uint64) * cp.uint64(100)
            + outputs["neighbor_counts"].astype(cp.uint64) * cp.uint64(10)
            + outputs["threshold_flags"].astype(cp.uint64)
        )
        consumer_event.record(stream)

    stream.synchronize()
    observed = {name: [int(value) for value in outputs[name].get().tolist()] for name in outputs}
    expected = {
        "query_ids": [1, 2, 3, 4],
        "neighbor_counts": [1, 1, 0, 1],
        "threshold_flags": [1, 1, 0, 1],
    }
    if observed != expected:
        raise AssertionError(f"unexpected stream-ordering output: observed={observed!r} expected={expected!r}")
    expected_checksum = 111 + 211 + 300 + 411
    observed_checksum = int(checksum.get().item())
    if observed_checksum != expected_checksum:
        raise AssertionError(
            f"unexpected stream-ordering consumer checksum: observed={observed_checksum} "
            f"expected={expected_checksum}"
        )
    metadata = result["metadata"]
    if int(metadata["caller_stream_handle"]) != int(stream.ptr):
        raise AssertionError("metadata did not preserve the caller stream")
    if int(metadata["prepare_stream_handle"]) != int(stream.ptr):
        raise AssertionError("metadata did not preserve the prepare stream")
    if not metadata["native_synchronized_before_return"]:
        raise AssertionError("M1 stream-ordering proof requires the documented synchronous return")
    if metadata["native_async_ready"]:
        raise AssertionError("M1 stream-ordering proof must not claim async readiness")

    return {
        "status": "pass-with-boundary",
        "route_id": "fixed_radius_count_threshold_2d",
        "hardware": _hardware(),
        "ordering_scope": "same_nondefault_cupy_stream_producer_rtdl_consumer",
        "same_stream_contract": {
            "producer_stream_ptr": int(stream.ptr),
            "rtdl_prepare_stream_ptr": int(metadata["prepare_stream_handle"]),
            "rtdl_query_stream_ptr": int(metadata["caller_stream_handle"]),
            "consumer_stream_ptr": int(stream.ptr),
            "producer_event_recorded": True,
            "consumer_event_recorded": True,
            "producer_rtdl_consumer_order_validated": True,
            "cross_stream_event_wait_validated": False,
        },
        "validation": {
            "output_match": True,
            "device_consumer_checksum_match": True,
            "observed": observed,
            "expected": expected,
            "observed_checksum": observed_checksum,
            "expected_checksum": expected_checksum,
        },
        "metadata_subset": {
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
            "same_stream_ordering_claim_authorized": True,
            "cross_stream_event_wait_claim_authorized": False,
            "async_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "v4_true_zero_copy_claim_authorized": False,
            "reason": (
                "This probe validates producer -> RTDL prepare/query -> consumer ordering on one "
                "nondefault CuPy CUDA stream. It does not validate cross-stream event waits and does "
                "not authorize async, true-zero-copy, or speedup wording."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V4 M1 same-stream ordering probe.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    args = parser.parse_args()

    result = run_probe()
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
