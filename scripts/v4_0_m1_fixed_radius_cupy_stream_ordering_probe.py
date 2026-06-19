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
    if metadata["native_prepare_ready_event_wait_used"]:
        raise AssertionError("same-stream proof should not require a prepare-ready event wait")

    cross_search = _device_column_dict(cp, count)
    cross_query = _device_column_dict(cp, count)
    cross_outputs = _output_dict(cp, count)
    cross_checksum = cp.empty((), dtype=cp.uint64)
    prepare_stream = cp.cuda.Stream(non_blocking=True)
    query_stream = cp.cuda.Stream(non_blocking=True)
    if int(prepare_stream.ptr) == int(query_stream.ptr):
        raise AssertionError("cross-stream probe did not receive distinct CUDA stream handles")
    prepare_input_event = cp.cuda.Event()
    cross_consumer_event = cp.cuda.Event()

    with prepare_stream:
        cross_search["ids"][:] = cp.asarray([10, 11, 12, 13], dtype=cp.uint32)
        cross_search["x"][:] = cp.asarray([0.0, 5.0, 0.0, 9.0], dtype=cp.float64)
        cross_search["y"][:] = cp.asarray([0.0, 0.0, 5.0, 9.0], dtype=cp.float64)
        prepare_input_event.record(prepare_stream)

    with query_stream:
        cross_query["ids"][:] = cp.asarray([1, 2, 3, 4], dtype=cp.uint32)
        cross_query["x"][:] = cp.asarray([0.0, 5.0, 2.5, 9.0], dtype=cp.float64)
        cross_query["y"][:] = cp.asarray([0.0, 0.0, 2.5, 9.0], dtype=cp.float64)
        cross_outputs["query_ids"].fill(cp.uint32(777))
        cross_outputs["neighbor_counts"].fill(cp.uint32(777))
        cross_outputs["threshold_flags"].fill(cp.uint32(777))

    cross_operator = rtdsl.prepare_v4_fixed_radius_count_threshold_2d(
        cross_search,
        max_radius=1.1,
        partner="cupy",
        stream=prepare_stream.ptr,
    )
    try:
        cross_result = cross_operator.run(
            cross_query,
            radius=1.1,
            threshold=1,
            output_columns=cross_outputs,
            stream=query_stream.ptr,
            return_metadata=True,
        )
    finally:
        cross_operator.close()

    with query_stream:
        cross_checksum[...] = cp.sum(
            cross_outputs["query_ids"].astype(cp.uint64) * cp.uint64(100)
            + cross_outputs["neighbor_counts"].astype(cp.uint64) * cp.uint64(10)
            + cross_outputs["threshold_flags"].astype(cp.uint64)
        )
        cross_consumer_event.record(query_stream)

    query_stream.synchronize()
    prepare_stream.synchronize()
    cross_observed = {name: [int(value) for value in cross_outputs[name].get().tolist()] for name in cross_outputs}
    if cross_observed != expected:
        raise AssertionError(
            f"unexpected cross-stream output: observed={cross_observed!r} expected={expected!r}"
        )
    cross_observed_checksum = int(cross_checksum.get().item())
    if cross_observed_checksum != expected_checksum:
        raise AssertionError(
            f"unexpected cross-stream consumer checksum: observed={cross_observed_checksum} "
            f"expected={expected_checksum}"
        )
    cross_metadata = cross_result["metadata"]
    if int(cross_metadata["prepare_stream_handle"]) != int(prepare_stream.ptr):
        raise AssertionError("cross-stream metadata did not preserve the prepare stream")
    if int(cross_metadata["caller_stream_handle"]) != int(query_stream.ptr):
        raise AssertionError("cross-stream metadata did not preserve the query stream")
    if not cross_metadata["prepare_query_streams_differ"]:
        raise AssertionError("cross-stream metadata did not mark distinct streams")
    if not cross_metadata["native_prepare_ready_event_wait_required"]:
        raise AssertionError("cross-stream metadata did not require a prepare-ready event wait")
    if not cross_metadata["native_prepare_ready_event_recorded"]:
        raise AssertionError("cross-stream metadata did not record prepare-ready event ownership")
    if not cross_metadata["native_prepare_ready_event_wait_used"]:
        raise AssertionError("cross-stream metadata did not report native event-wait use")
    if not cross_metadata["native_synchronized_before_return"]:
        raise AssertionError("cross-stream proof requires the documented synchronous return")
    if cross_metadata["native_async_ready"]:
        raise AssertionError("cross-stream proof must not claim async readiness")

    return {
        "status": "pass-with-boundary",
        "route_id": "fixed_radius_count_threshold_2d",
        "hardware": _hardware(),
        "ordering_scope": "same_stream_and_cross_stream_prepare_query_event_wait",
        "same_stream_contract": {
            "ordering_scope": "same_nondefault_cupy_stream_producer_rtdl_consumer",
            "producer_stream_ptr": int(stream.ptr),
            "rtdl_prepare_stream_ptr": int(metadata["prepare_stream_handle"]),
            "rtdl_query_stream_ptr": int(metadata["caller_stream_handle"]),
            "consumer_stream_ptr": int(stream.ptr),
            "producer_event_recorded": True,
            "consumer_event_recorded": True,
            "producer_rtdl_consumer_order_validated": True,
            "native_prepare_ready_event_wait_used": bool(metadata["native_prepare_ready_event_wait_used"]),
            "cross_stream_event_wait_validated": False,
        },
        "cross_stream_prepare_query_contract": {
            "prepare_stream_ptr": int(prepare_stream.ptr),
            "query_stream_ptr": int(query_stream.ptr),
            "streams_distinct": int(prepare_stream.ptr) != int(query_stream.ptr),
            "prepare_input_event_recorded": True,
            "query_stream_consumer_event_recorded": True,
            "prepare_query_streams_differ": bool(cross_metadata["prepare_query_streams_differ"]),
            "native_prepare_ready_event_recorded": bool(cross_metadata["native_prepare_ready_event_recorded"]),
            "native_prepare_ready_event_wait_required": bool(
                cross_metadata["native_prepare_ready_event_wait_required"]
            ),
            "native_prepare_ready_event_wait_used": bool(cross_metadata["native_prepare_ready_event_wait_used"]),
            "native_synchronized_before_return": bool(cross_metadata["native_synchronized_before_return"]),
            "cross_stream_event_wait_validated": True,
        },
        "validation": {
            "output_match": True,
            "device_consumer_checksum_match": True,
            "observed": observed,
            "expected": expected,
            "observed_checksum": observed_checksum,
            "expected_checksum": expected_checksum,
            "cross_stream_output_match": True,
            "cross_stream_device_consumer_checksum_match": True,
            "cross_stream_observed": cross_observed,
            "cross_stream_expected": expected,
            "cross_stream_observed_checksum": cross_observed_checksum,
            "cross_stream_expected_checksum": expected_checksum,
        },
        "metadata_subset": {
            "caller_stream_handle_nonzero": int(metadata["caller_stream_handle"]) != 0,
            "prepare_stream_handle_nonzero": int(metadata["prepare_stream_handle"]) != 0,
            "caller_stream_native_propagation_ready": bool(metadata["caller_stream_native_propagation_ready"]),
            "native_prepare_stream_propagation_ready": bool(metadata["native_prepare_stream_propagation_ready"]),
            "cross_stream_event_wait_ready": bool(cross_metadata["cross_stream_event_wait_ready"]),
            "cross_stream_prepare_query_wait_used": bool(
                cross_metadata["native_prepare_ready_event_wait_used"]
            ),
            "native_synchronized_before_return": bool(metadata["native_synchronized_before_return"]),
            "native_async_ready": bool(metadata["native_async_ready"]),
            "named_cuda_columns_no_host_stage_authorized": bool(
                metadata["named_cuda_columns_no_host_stage_authorized"]
            ),
            "v4_true_zero_copy_claim_authorized": bool(metadata["v4_true_zero_copy_claim_authorized"]),
        },
        "claim_boundaries": {
            "same_stream_ordering_claim_authorized": True,
            "fixed_radius_m1_cross_stream_prepare_query_event_wait_claim_authorized": True,
            "cross_stream_event_wait_claim_authorized": False,
            "general_cross_stream_event_wait_claim_authorized": False,
            "full_external_stream_ownership_claim_authorized": False,
            "async_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "v4_true_zero_copy_claim_authorized": False,
            "reason": (
                "This probe validates same-stream ordering and the narrow fixed-radius M1 "
                "prepare-ready event wait from a prepare stream to a different query stream. It does "
                "not authorize async, full external stream ownership, true-zero-copy, or speedup wording."
            ),
            "forbidden_wording": [
                "async or nonblocking completion",
                "full external stream ownership",
                "general cross-stream event semantics",
                "public true-zero-copy",
                "RT-core speedup",
            ],
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
