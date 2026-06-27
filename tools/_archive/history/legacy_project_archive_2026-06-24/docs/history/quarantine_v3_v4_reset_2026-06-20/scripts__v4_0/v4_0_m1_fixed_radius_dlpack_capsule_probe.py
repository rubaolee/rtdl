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


class DLPackCapsuleOnlyColumn:
    """Expose a CuPy-owned column only through legacy DLPack capsules."""

    def __init__(self, array) -> None:
        self.array = array
        self.dtype = array.dtype
        self.shape = array.shape
        self.strides = tuple(int(stride // array.dtype.itemsize) for stride in array.strides)
        self.requested_streams: list[int | str] = []
        self.stream_argument_accepted: list[bool] = []

    def __dlpack__(self, stream=None):
        if stream is None:
            self.requested_streams.append("none")
            self.stream_argument_accepted.append(True)
            return self.array.__dlpack__()
        requested = int(stream)
        self.requested_streams.append(requested)
        try:
            capsule = self.array.__dlpack__(stream=requested)
        except TypeError:
            self.stream_argument_accepted.append(False)
            return self.array.__dlpack__()
        self.stream_argument_accepted.append(True)
        return capsule

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
        "rt_core_hardware": False,
        "hardware_note": (
            "This host validates CUDA/OptiX execution and DLPack capsule routing; "
            "it is not RTX/RT-core speed evidence."
        ),
    }


def _git_value(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _wrap(columns: dict[str, object]) -> dict[str, DLPackCapsuleOnlyColumn]:
    wrapped = {name: DLPackCapsuleOnlyColumn(column) for name, column in columns.items()}
    for name, column in wrapped.items():
        if hasattr(column, "__cuda_array_interface__"):
            raise AssertionError(f"DLPack capsule column {name!r} unexpectedly exposes CUDA Array Interface")
        if callable(getattr(column, "data_ptr", None)):
            raise AssertionError(f"DLPack capsule column {name!r} unexpectedly exposes data_ptr()")
    return wrapped


def _ptrs(prefix: str, arrays: dict[str, object]) -> dict[str, int]:
    return {f"{prefix}.{name}": int(column.data.ptr) for name, column in arrays.items()}


def _requested_streams(columns: dict[str, DLPackCapsuleOnlyColumn]) -> dict[str, list[int | str]]:
    return {name: list(column.requested_streams) for name, column in columns.items()}


def _stream_acceptance(columns: dict[str, DLPackCapsuleOnlyColumn]) -> dict[str, list[bool]]:
    return {name: list(column.stream_argument_accepted) for name, column in columns.items()}


def run_probe() -> dict[str, object]:
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

    search = _wrap(search_arrays)
    query = _wrap(query_arrays)
    outputs = _wrap(output_arrays)

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

    observed = {name: output_arrays[name].get().tolist() for name in output_arrays}
    expected = {
        "query_ids": [1, 2, 3],
        "neighbor_counts": [1, 1, 0],
        "threshold_flags": [1, 1, 0],
    }
    if observed != expected:
        raise AssertionError(f"unexpected DLPack capsule output: observed={observed!r} expected={expected!r}")

    metadata = result["metadata"]
    plan = metadata["v4_plan"]
    source_protocols = list(plan["source_protocols"])
    if source_protocols != ["dlpack"]:
        raise AssertionError(f"unexpected source protocols for DLPack capsule probe: {source_protocols!r}")

    plan_ptrs = plan["borrowed_device_pointers"]
    pointer_identity = {name: int(plan_ptrs[name]) == int(ptr) for name, ptr in expected_ptrs.items()}
    if not all(pointer_identity.values()):
        raise AssertionError(f"DLPack capsule pointer identity failed: {pointer_identity!r}")

    native_pointer_echo = metadata["native_call_device_pointer_echo"]
    pointer_echo_identity = {
        name: int(native_pointer_echo.get(name, 0)) == int(ptr) for name, ptr in expected_ptrs.items()
    }
    if not metadata["native_call_device_pointer_echo_complete"]:
        raise AssertionError("native pointer echo is incomplete")
    if not all(pointer_echo_identity.values()):
        raise AssertionError(f"DLPack capsule pointer echo failed: {pointer_echo_identity!r}")
    if int(metadata["caller_stream_handle"]) != int(stream.ptr):
        raise AssertionError("metadata did not preserve DLPack capsule caller stream")
    if int(metadata["prepare_stream_handle"]) != int(stream.ptr):
        raise AssertionError("metadata did not preserve DLPack capsule prepare stream")
    if metadata["native_async_ready"]:
        raise AssertionError("DLPack capsule probe must not authorize async")
    if metadata["v4_true_zero_copy_claim_authorized"]:
        raise AssertionError("DLPack capsule probe must not authorize public true-zero-copy")

    stream_groups = {
        "search": _requested_streams(search),
        "query": _requested_streams(query),
        "output": _requested_streams(outputs),
    }
    stream_acceptance = {
        "search": _stream_acceptance(search),
        "query": _stream_acceptance(query),
        "output": _stream_acceptance(outputs),
    }
    all_streams = [
        int(value)
        for group in stream_groups.values()
        for values in group.values()
        for value in values
        if value != "none"
    ]
    if not all_streams or any(value != int(stream.ptr) for value in all_streams):
        raise AssertionError(f"DLPack capsule stream requests did not match caller stream: {stream_groups!r}")
    if not all(
        all(values)
        for group in stream_acceptance.values()
        for values in group.values()
    ):
        raise AssertionError(f"DLPack producer did not accept every stream argument: {stream_acceptance!r}")

    return {
        "status": "pass-with-boundary",
        "report_id": "v4_0_m1_fixed_radius_dlpack_capsule_probe_2026-06-19",
        "route_id": "fixed_radius_count_threshold_2d",
        "framework": "cupy_backed_dlpack_capsule_only_wrapper",
        "protocol": "legacy_dlpack_capsule",
        "evidence_code_commit": _git_value("rev-parse", "HEAD"),
        "evidence_code_tree": _git_value("rev-parse", "HEAD^{tree}"),
        "hardware": _hardware(),
        "validation": {
            "output_match": True,
            "observed": observed,
            "expected": expected,
            "all_wrappers_hide_cuda_array_interface": True,
            "all_wrappers_hide_data_ptr": True,
            "real_dlpack_capsule_intake": True,
            "legacy_dltensor_capsule_policy": True,
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
        "dlpack_stream_contract": {
            "caller_stream_ptr": int(stream.ptr),
            "requested_streams": stream_groups,
            "producer_accepted_stream_argument": stream_acceptance,
            "all_requested_streams_match_caller_stream": True,
            "synchronous_return": True,
            "async_completion_authorized": False,
        },
        "lifetime_contract": {
            "capsule_policy": "legacy_dltensor_only",
            "consume_policy": "RTDL renames each consumed capsule to used_dltensor",
            "deleter_policy": "RTDL-held leases call the DLManagedTensor deleter exactly once",
            "producer_retained_by_wrapper": True,
            "full_framework_neutral_lifetime_matrix_complete": False,
        },
        "claim_boundaries": {
            "fixed_radius_m1_dlpack_capsule_route_claim_authorized": True,
            "full_dlpack_capsule_route_claim_authorized": False,
            "framework_neutral_dlpack_route_claim_authorized": False,
            "dlpack_route_claim_authorized": False,
            "pytorch_route_claim_authorized": False,
            "async_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "v4_true_zero_copy_claim_authorized": False,
            "reason": (
                "This probe validates real legacy DLPack capsule intake for the CuPy-backed "
                "fixed-radius M1 route, including stream argument propagation, pointer identity, "
                "native pointer echo, and output correctness. It does not validate arbitrary "
                "framework-neutral DLPack, PyTorch, async, true-zero-copy, or speedup wording."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V4 M1 DLPack capsule route probe.")
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
