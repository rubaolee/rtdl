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
        "rt_core_hardware": False,
        "hardware_note": (
            "This host validates CUDA/OptiX execution and PyTorch tensor routing; "
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


def _ptrs(prefix: str, columns: dict[str, object]) -> dict[str, int]:
    return {f"{prefix}.{name}": int(column.data_ptr()) for name, column in columns.items()}


def _torch_stream_ptr(stream) -> int:
    return int(getattr(stream, "cuda_stream", 0) or 0)


def _torch_columns(torch, *, ids, x, y) -> dict[str, object]:
    return {
        "ids": torch.tensor(ids, dtype=torch.uint32, device="cuda"),
        "x": torch.tensor(x, dtype=torch.float64, device="cuda"),
        "y": torch.tensor(y, dtype=torch.float64, device="cuda"),
    }


def _torch_outputs(torch, count: int) -> dict[str, object]:
    return {
        "query_ids": torch.empty((count,), dtype=torch.uint32, device="cuda"),
        "neighbor_counts": torch.empty((count,), dtype=torch.uint32, device="cuda"),
        "threshold_flags": torch.empty((count,), dtype=torch.uint32, device="cuda"),
    }


def _expected_output() -> dict[str, list[int]]:
    return {
        "query_ids": [1, 2, 3],
        "neighbor_counts": [1, 1, 0],
        "threshold_flags": [1, 1, 0],
    }


def _expected_checksum() -> int:
    return 111 + 211 + 300


def _read_outputs(outputs: dict[str, object]) -> dict[str, list[int]]:
    return {name: [int(value) for value in column.detach().cpu().tolist()] for name, column in outputs.items()}


def _output_checksum(torch, outputs: dict[str, object]):
    return (
        outputs["query_ids"].to(torch.int64) * 100
        + outputs["neighbor_counts"].to(torch.int64) * 10
        + outputs["threshold_flags"].to(torch.int64)
    ).sum()


def _standard_route_columns(torch) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    search = _torch_columns(
        torch,
        ids=[10, 11, 12],
        x=[0.0, 4.0, 9.0],
        y=[0.0, 0.0, 9.0],
    )
    query = _torch_columns(
        torch,
        ids=[1, 2, 3],
        x=[0.0, 4.0, 1.5],
        y=[0.0, 0.0, 1.5],
    )
    return search, query, _torch_outputs(torch, 3)


def _validate_route_result(
    *,
    case_id: str,
    outputs: dict[str, object],
    result: dict[str, object],
    expected_ptrs: dict[str, int],
    observed_checksum: int,
    expected_stream_ptr: int,
    expected_prepare_stream_ptr: int,
    require_prepare_query_wait: bool = False,
) -> dict[str, object]:
    observed = _read_outputs(outputs)
    expected = _expected_output()
    if observed != expected:
        raise AssertionError(f"{case_id}: unexpected PyTorch output: observed={observed!r} expected={expected!r}")
    expected_checksum = _expected_checksum()
    if int(observed_checksum) != expected_checksum:
        raise AssertionError(
            f"{case_id}: unexpected PyTorch same-stream checksum: observed={observed_checksum} "
            f"expected={expected_checksum}"
        )

    metadata = result["metadata"]
    plan = metadata["v4_plan"]
    source_protocols = list(plan["source_protocols"])
    if source_protocols != ["torch"]:
        raise AssertionError(f"{case_id}: unexpected source protocols: {source_protocols!r}")

    plan_ptrs = plan["borrowed_device_pointers"]
    pointer_identity = {name: int(plan_ptrs[name]) == int(ptr) for name, ptr in expected_ptrs.items()}
    if not all(pointer_identity.values()):
        raise AssertionError(f"{case_id}: PyTorch plan pointer identity failed: {pointer_identity!r}")
    native_pointer_echo = metadata["native_call_device_pointer_echo"]
    pointer_echo_identity = {
        name: int(native_pointer_echo.get(name, 0)) == int(ptr) for name, ptr in expected_ptrs.items()
    }
    if not metadata["native_call_device_pointer_echo_complete"]:
        raise AssertionError(f"{case_id}: native pointer echo is incomplete")
    if not all(pointer_echo_identity.values()):
        raise AssertionError(f"{case_id}: PyTorch native pointer echo failed: {pointer_echo_identity!r}")
    if int(metadata["caller_stream_handle"]) != int(expected_stream_ptr):
        raise AssertionError(f"{case_id}: metadata did not preserve the PyTorch caller stream")
    if int(metadata["prepare_stream_handle"]) != int(expected_prepare_stream_ptr):
        raise AssertionError(f"{case_id}: metadata did not preserve the PyTorch prepare stream")
    if metadata["native_async_ready"]:
        raise AssertionError(f"{case_id}: PyTorch probe must not authorize async")
    if metadata["v4_true_zero_copy_claim_authorized"]:
        raise AssertionError(f"{case_id}: PyTorch probe must not authorize public true-zero-copy")
    if require_prepare_query_wait and not metadata["native_prepare_ready_event_wait_used"]:
        raise AssertionError(f"{case_id}: distinct prepare/query streams must use the native prepare-ready wait")

    return {
        "case_id": case_id,
        "passed": True,
        "observed": observed,
        "expected": expected,
        "observed_checksum": int(observed_checksum),
        "expected_checksum": expected_checksum,
        "source_protocols": source_protocols,
        "caller_stream_handle": int(metadata["caller_stream_handle"]),
        "prepare_stream_handle": int(metadata["prepare_stream_handle"]),
        "prepare_query_streams_differ": bool(metadata["prepare_query_streams_differ"]),
        "native_prepare_ready_event_wait_used": bool(metadata["native_prepare_ready_event_wait_used"]),
        "native_synchronized_before_return": bool(metadata["native_synchronized_before_return"]),
        "native_async_ready": bool(metadata["native_async_ready"]),
        "pointer_identity": pointer_identity,
        "pointer_echo_identity": pointer_echo_identity,
        "pointer_identity_complete": all(pointer_identity.values()),
        "native_pointer_echo_match_complete": all(pointer_echo_identity.values()),
        "metadata_subset": {
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
    }


def _expect_rejection(case_id: str, action, expected_message: str) -> dict[str, object]:
    try:
        action()
    except (TypeError, ValueError, RuntimeError) as exc:
        message = str(exc)
        if expected_message not in message:
            raise AssertionError(
                f"{case_id}: expected error containing {expected_message!r}, got {message!r}"
            ) from exc
        return {
            "case_id": case_id,
            "passed": True,
            "error_type": exc.__class__.__name__,
            "message_contains": expected_message,
            "observed_message": message,
        }
    raise AssertionError(f"{case_id}: expected rejection containing {expected_message!r}")


def run_probe() -> dict[str, object]:
    import torch
    import rtdsl

    if not torch.cuda.is_available():
        raise RuntimeError("PyTorch CUDA is not available")

    stream = torch.cuda.Stream()
    stream_ptr = _torch_stream_ptr(stream)
    if stream_ptr == 0:
        raise AssertionError("PyTorch probe requires a nonzero CUDA stream")

    accepted_cases: list[dict[str, object]] = []
    rejected_cases: list[dict[str, object]] = []

    with torch.cuda.stream(stream):
        search, query, outputs = _standard_route_columns(torch)
        expected_ptrs = {}
        expected_ptrs.update(_ptrs("search", search))
        expected_ptrs.update(_ptrs("query", query))
        expected_ptrs.update(_ptrs("output", outputs))

        result = rtdsl.run_v4_fixed_radius_count_threshold_2d(
            query,
            search,
            radius=1.1,
            threshold=1,
            partner="torch",
            output_columns=outputs,
            stream=stream,
            return_metadata=True,
        )
        checksum = _output_checksum(torch, outputs)
    stream.synchronize()

    primary_case = _validate_route_result(
        case_id="contiguous_detached_cuda_same_stream_object",
        outputs=outputs,
        result=result,
        expected_ptrs=expected_ptrs,
        observed_checksum=int(checksum.detach().cpu().item()),
        expected_stream_ptr=stream_ptr,
        expected_prepare_stream_ptr=stream_ptr,
    )
    accepted_cases.append(primary_case)

    detached_stream = torch.cuda.Stream()
    detached_stream_ptr = _torch_stream_ptr(detached_stream)
    with torch.cuda.stream(detached_stream):
        detached_search, detached_query, detached_outputs = _standard_route_columns(torch)
        detached_query["x"] = torch.tensor(
            [0.0, 4.0, 1.5],
            dtype=torch.float64,
            device="cuda",
            requires_grad=True,
        ).detach()
        detached_ptrs = {}
        detached_ptrs.update(_ptrs("search", detached_search))
        detached_ptrs.update(_ptrs("query", detached_query))
        detached_ptrs.update(_ptrs("output", detached_outputs))
        detached_result = rtdsl.run_v4_fixed_radius_count_threshold_2d(
            detached_query,
            detached_search,
            radius=1.1,
            threshold=1,
            partner="torch",
            output_columns=detached_outputs,
            stream=detached_stream,
            return_metadata=True,
        )
        detached_checksum = _output_checksum(torch, detached_outputs)
    detached_stream.synchronize()
    accepted_cases.append(
        _validate_route_result(
            case_id="detached_from_grad_cuda_tensor",
            outputs=detached_outputs,
            result=detached_result,
            expected_ptrs=detached_ptrs,
            observed_checksum=int(detached_checksum.detach().cpu().item()),
            expected_stream_ptr=detached_stream_ptr,
            expected_prepare_stream_ptr=detached_stream_ptr,
        )
    )

    prepare_stream = torch.cuda.Stream()
    query_stream = torch.cuda.Stream()
    prepare_stream_ptr = _torch_stream_ptr(prepare_stream)
    query_stream_ptr = _torch_stream_ptr(query_stream)
    cross_search, cross_query, cross_outputs = _standard_route_columns(torch)
    torch.cuda.synchronize()
    cross_ptrs = {}
    cross_ptrs.update(_ptrs("search", cross_search))
    cross_ptrs.update(_ptrs("query", cross_query))
    cross_ptrs.update(_ptrs("output", cross_outputs))
    with torch.cuda.stream(prepare_stream):
        operator = rtdsl.prepare_v4_fixed_radius_count_threshold_2d(
            cross_search,
            max_radius=1.1,
            partner="torch",
            stream=prepare_stream,
        )
    try:
        with torch.cuda.stream(query_stream):
            cross_result = operator.run(
                cross_query,
                radius=1.1,
                threshold=1,
                output_columns=cross_outputs,
                stream=query_stream,
                return_metadata=True,
            )
            cross_checksum = _output_checksum(torch, cross_outputs)
        query_stream.synchronize()
    finally:
        operator.close()
    accepted_cases.append(
        _validate_route_result(
            case_id="distinct_prepare_query_torch_stream_objects",
            outputs=cross_outputs,
            result=cross_result,
            expected_ptrs=cross_ptrs,
            observed_checksum=int(cross_checksum.detach().cpu().item()),
            expected_stream_ptr=query_stream_ptr,
            expected_prepare_stream_ptr=prepare_stream_ptr,
            require_prepare_query_wait=True,
        )
    )

    reject_search, reject_query, reject_outputs = _standard_route_columns(torch)
    grad_search = dict(reject_search)
    grad_search["x"] = torch.tensor([0.0, 1.0, 2.0], dtype=torch.float64, device="cuda", requires_grad=True)
    rejected_cases.append(
        _expect_rejection(
            "grad_enabled_input_rejected",
            lambda: rtdsl.plan_v4_fixed_radius_count_threshold_2d(
                reject_query,
                grad_search,
                output_columns=reject_outputs,
                stream=stream,
                prepare_stream=stream,
            ),
            "detached",
        )
    )

    grad_output = dict(reject_outputs)
    grad_output["threshold_flags"] = torch.empty((3,), dtype=torch.float64, device="cuda", requires_grad=True)
    rejected_cases.append(
        _expect_rejection(
            "grad_enabled_output_rejected",
            lambda: rtdsl.plan_v4_fixed_radius_count_threshold_2d(
                reject_query,
                reject_search,
                output_columns=grad_output,
                stream=stream,
                prepare_stream=stream,
            ),
            "detached",
        )
    )

    cpu_query = dict(reject_query)
    cpu_query["x"] = torch.tensor([0.0, 4.0, 1.5], dtype=torch.float64, device="cpu")
    rejected_cases.append(
        _expect_rejection(
            "cpu_tensor_rejected",
            lambda: rtdsl.plan_v4_fixed_radius_count_threshold_2d(
                cpu_query,
                reject_search,
                output_columns=reject_outputs,
                stream=stream,
                prepare_stream=stream,
            ),
            "requires a CUDA",
        )
    )

    wrong_dtype_query = dict(reject_query)
    wrong_dtype_query["x"] = torch.tensor([0.0, 4.0, 1.5], dtype=torch.float32, device="cuda")
    rejected_cases.append(
        _expect_rejection(
            "wrong_dtype_rejected",
            lambda: rtdsl.plan_v4_fixed_radius_count_threshold_2d(
                wrong_dtype_query,
                reject_search,
                output_columns=reject_outputs,
                stream=stream,
                prepare_stream=stream,
            ),
            "must use dtype",
        )
    )

    bad_rank_query = dict(reject_query)
    bad_rank_query["x"] = torch.zeros((3, 1), dtype=torch.float64, device="cuda")
    rejected_cases.append(
        _expect_rejection(
            "bad_rank_rejected",
            lambda: rtdsl.plan_v4_fixed_radius_count_threshold_2d(
                bad_rank_query,
                reject_search,
                output_columns=reject_outputs,
                stream=stream,
                prepare_stream=stream,
            ),
            "one-dimensional",
        )
    )

    noncontiguous_query = dict(reject_query)
    noncontiguous_query["x"] = torch.arange(6, dtype=torch.float64, device="cuda")[::2]
    rejected_cases.append(
        _expect_rejection(
            "noncontiguous_view_rejected",
            lambda: rtdsl.plan_v4_fixed_radius_count_threshold_2d(
                noncontiguous_query,
                reject_search,
                output_columns=reject_outputs,
                stream=stream,
                prepare_stream=stream,
            ),
            "must be contiguous",
        )
    )

    mismatched_query = dict(reject_query)
    mismatched_query["ids"] = torch.tensor([1, 2], dtype=torch.uint32, device="cuda")
    rejected_cases.append(
        _expect_rejection(
            "mismatched_lengths_rejected",
            lambda: rtdsl.plan_v4_fixed_radius_count_threshold_2d(
                mismatched_query,
                reject_search,
                output_columns=reject_outputs,
                stream=stream,
                prepare_stream=stream,
            ),
            "matching lengths",
        )
    )

    short_outputs = _torch_outputs(torch, 2)
    rejected_cases.append(
        _expect_rejection(
            "bad_output_length_rejected",
            lambda: rtdsl.plan_v4_fixed_radius_count_threshold_2d(
                reject_query,
                reject_search,
                output_columns=short_outputs,
                stream=stream,
                prepare_stream=stream,
            ),
            "matching lengths",
        )
    )

    missing_query = dict(reject_query)
    del missing_query["x"]
    rejected_cases.append(
        _expect_rejection(
            "missing_column_rejected",
            lambda: rtdsl.plan_v4_fixed_radius_count_threshold_2d(
                missing_query,
                reject_search,
                output_columns=reject_outputs,
                stream=stream,
                prepare_stream=stream,
            ),
            "missing V4 query columns",
        )
    )

    extra_query = dict(reject_query)
    extra_query["z"] = torch.zeros((3,), dtype=torch.float64, device="cuda")
    rejected_cases.append(
        _expect_rejection(
            "extra_column_rejected",
            lambda: rtdsl.plan_v4_fixed_radius_count_threshold_2d(
                extra_query,
                reject_search,
                output_columns=reject_outputs,
                stream=stream,
                prepare_stream=stream,
            ),
            "unexpected V4 query columns",
        )
    )

    matrix_all_expected = all(case["passed"] for case in accepted_cases) and all(
        case["passed"] for case in rejected_cases
    )
    if not matrix_all_expected:
        raise AssertionError("PyTorch compatibility matrix did not pass")

    return {
        "status": "pass-with-boundary",
        "report_id": "v4_0_m1_fixed_radius_pytorch_cuda_tensor_probe_2026-06-19",
        "route_id": "fixed_radius_count_threshold_2d",
        "framework": "pytorch",
        "protocol": "torch_cuda_tensor_data_ptr",
        "torch": {
            "version": torch.__version__,
            "cuda_version": torch.version.cuda,
            "cuda_available": bool(torch.cuda.is_available()),
            "device_name": torch.cuda.get_device_name(0),
        },
        "evidence_code_commit": _git_value("rev-parse", "HEAD"),
        "evidence_code_tree": _git_value("rev-parse", "HEAD^{tree}"),
        "hardware": _hardware(),
        "validation": {
            "output_match": True,
            "observed": primary_case["observed"],
            "expected": primary_case["expected"],
            "same_stream_consumer_checksum_match": True,
            "observed_checksum": primary_case["observed_checksum"],
            "expected_checksum": primary_case["expected_checksum"],
            "grad_enabled_tensor_rejected": True,
            "compatibility_matrix_all_expected": matrix_all_expected,
            "accepted_case_count": len(accepted_cases),
            "rejected_case_count": len(rejected_cases),
        },
        "metadata_subset": {"source_protocols": primary_case["source_protocols"], **primary_case["metadata_subset"]},
        "pointer_identity": primary_case["pointer_identity"],
        "pointer_echo_identity": primary_case["pointer_echo_identity"],
        "compatibility_matrix": {
            "scope": "fixed_radius_m1_pytorch_cuda_tensor_compatibility",
            "accepted": accepted_cases,
            "rejected": rejected_cases,
            "accepted_case_count": len(accepted_cases),
            "rejected_case_count": len(rejected_cases),
            "all_expected": matrix_all_expected,
            "full_pytorch_partner_surface_complete": False,
        },
        "stream_contract": {
            "torch_stream_ptr": stream_ptr,
            "rtdl_prepare_stream_ptr": primary_case["prepare_stream_handle"],
            "rtdl_query_stream_ptr": primary_case["caller_stream_handle"],
            "direct_torch_stream_object_validated": True,
            "distinct_prepare_query_streams_validated": True,
            "same_stream_consumer_checksum_validated": True,
            "cross_stream_event_wait_validated": True,
            "async_completion_authorized": False,
        },
        "lifetime_contract": {
            "caller_owned_tensors_retained_until_stream_synchronized": True,
            "grad_enabled_tensors_must_be_detached": True,
            "detached_tensors_accepted": True,
            "full_pytorch_partner_surface_complete": False,
        },
        "claim_boundaries": {
            "pytorch_fixed_radius_m1_cuda_tensor_route_claim_authorized": True,
            "pytorch_fixed_radius_m1_cuda_tensor_compatibility_matrix_claim_authorized": True,
            "pytorch_route_claim_authorized": True,
            "pytorch_full_partner_surface_claim_authorized": False,
            "framework_neutral_dlpack_route_claim_authorized": False,
            "async_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "v4_true_zero_copy_claim_authorized": False,
            "reason": (
                "This probe validates the exact fixed-radius M1 route for PyTorch CUDA tensors "
                "with pointer identity, native pointer echo, same-stream checksum, direct "
                "torch.cuda.Stream objects, distinct prepare/query stream ordering, caller-owned "
                "outputs, detached tensor acceptance, and fail-closed compatibility cases. It does "
                "not validate a full PyTorch partner surface, framework-neutral DLPack, async, "
                "true-zero-copy, or speedup wording."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V4 M1 PyTorch CUDA tensor route probe.")
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
