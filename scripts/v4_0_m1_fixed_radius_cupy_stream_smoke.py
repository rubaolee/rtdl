#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def _cuda_ptr(array) -> int:
    cuda_array = getattr(array, "__cuda_array_interface__", {})
    data = cuda_array.get("data")
    if isinstance(data, tuple) and data:
        return int(data[0])
    raise RuntimeError("array does not expose a CUDA data pointer")


def _source_audit() -> dict[str, bool]:
    workloads = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
    source = workloads.read_text(encoding="utf-8")
    symbol = "write_prepared_fixed_radius_count_threshold_2d_device_query_columns_on_stream_optix"
    start = source.index(symbol)
    end = source.index("static void count_prepared_fixed_radius_threshold_reached_2d_optix", start)
    body = source[start:end]
    return {
        "on_stream_symbol_present": symbol in source,
        "uses_caller_stream_launch": "optixLaunch(g_frn_count_rt.pipe->pipeline, stream" in body,
        "uses_async_param_upload": "upload_async(d_params.ptr, &lp, 1, stream)" in body,
        "uses_device_to_device_empty_copy": "cuMemcpyDtoDAsync" in body,
        "does_not_download_outputs": "download(" not in body and "cuMemcpyDtoH" not in body,
        "synchronizes_caller_stream_before_return": "cuStreamSynchronize(stream)" in body,
    }


def run_smoke() -> dict[str, object]:
    import cupy as cp
    import rtdsl

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
    input_ptrs = {
        f"search.{name}": _cuda_ptr(column) for name, column in search.items()
    }
    input_ptrs.update({f"query.{name}": _cuda_ptr(column) for name, column in query.items()})
    output_ptrs = {f"output.{name}": _cuda_ptr(column) for name, column in outputs.items()}

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

    observed = {name: outputs[name].get().tolist() for name in outputs}
    expected = {
        "query_ids": [1, 2, 3],
        "neighbor_counts": [1, 1, 0],
        "threshold_flags": [1, 1, 0],
    }
    if observed != expected:
        raise AssertionError(f"unexpected V4 fixed-radius output: {observed!r}")

    metadata = result["metadata"]
    plan_ptrs = metadata["v4_plan"]["borrowed_device_pointers"]
    pointer_identity = {
        "search.x": plan_ptrs["search.x"] == input_ptrs["search.x"],
        "search.y": plan_ptrs["search.y"] == input_ptrs["search.y"],
        "search.ids": plan_ptrs["search.ids"] == input_ptrs["search.ids"],
        "query.x": plan_ptrs["query.x"] == input_ptrs["query.x"],
        "query.y": plan_ptrs["query.y"] == input_ptrs["query.y"],
        "query.ids": plan_ptrs["query.ids"] == input_ptrs["query.ids"],
        "output.query_ids": plan_ptrs["output.query_ids"] == output_ptrs["output.query_ids"],
        "output.neighbor_counts": plan_ptrs["output.neighbor_counts"] == output_ptrs["output.neighbor_counts"],
        "output.threshold_flags": plan_ptrs["output.threshold_flags"] == output_ptrs["output.threshold_flags"],
    }
    if not all(pointer_identity.values()):
        raise AssertionError(f"pointer identity failed: {pointer_identity!r}")
    if metadata["caller_stream_handle"] != int(stream.ptr):
        raise AssertionError("metadata did not preserve the caller stream handle")
    if not metadata["native_synchronized_before_return"]:
        raise AssertionError("native route must document stream synchronization before return")
    if metadata["native_async_ready"]:
        raise AssertionError("M1 caller-stream route must not claim async readiness")

    return {
        "status": "pass-with-boundary",
        "route_id": metadata["v4_route_id"],
        "observed": observed,
        "expected": expected,
        "caller_stream_handle_nonzero": int(stream.ptr) != 0,
        "metadata_subset": {
            "caller_stream_handle": int(metadata["caller_stream_handle"]),
            "caller_stream_native_propagation_ready": bool(metadata["caller_stream_native_propagation_ready"]),
            "native_synchronized_before_return": bool(metadata["native_synchronized_before_return"]),
            "native_async_ready": bool(metadata["native_async_ready"]),
            "native_true_zero_copy_authorized": bool(metadata["native_true_zero_copy_authorized"]),
            "v4_true_zero_copy_claim_authorized": bool(metadata["v4_true_zero_copy_claim_authorized"]),
        },
        "pointer_identity": pointer_identity,
        "source_audit": _source_audit(),
        "claim_boundaries": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "v4_true_zero_copy_claim_authorized": False,
            "async_claim_authorized": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the V4 M1 CuPy caller-stream smoke.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    args = parser.parse_args()

    result = run_smoke()
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
