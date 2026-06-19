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


def run_probe() -> dict[str, object]:
    import torch
    import rtdsl

    if not torch.cuda.is_available():
        raise RuntimeError("PyTorch CUDA is not available")

    stream = torch.cuda.Stream()
    stream_ptr = _torch_stream_ptr(stream)
    if stream_ptr == 0:
        raise AssertionError("PyTorch probe requires a nonzero CUDA stream")

    with torch.cuda.stream(stream):
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
        outputs = _torch_outputs(torch, 3)
        expected_ptrs = {}
        expected_ptrs.update(_ptrs("search", search))
        expected_ptrs.update(_ptrs("query", query))
        expected_ptrs.update(_ptrs("output", outputs))

        grad_search = dict(search)
        grad_search["x"] = torch.tensor([0.0, 1.0, 2.0], dtype=torch.float64, device="cuda", requires_grad=True)
        grad_enabled_rejected = False
        try:
            rtdsl.plan_v4_fixed_radius_count_threshold_2d(
                query,
                grad_search,
                output_columns=outputs,
                stream=stream_ptr,
                prepare_stream=stream_ptr,
            )
        except ValueError as exc:
            grad_enabled_rejected = "detached" in str(exc)
        if not grad_enabled_rejected:
            raise AssertionError("PyTorch grad-enabled tensors must be rejected before RTDL export")

        result = rtdsl.run_v4_fixed_radius_count_threshold_2d(
            query,
            search,
            radius=1.1,
            threshold=1,
            partner="torch",
            output_columns=outputs,
            stream=stream_ptr,
            return_metadata=True,
        )
        checksum = (
            outputs["query_ids"].to(torch.int64) * 100
            + outputs["neighbor_counts"].to(torch.int64) * 10
            + outputs["threshold_flags"].to(torch.int64)
        ).sum()
    stream.synchronize()

    observed = {name: [int(value) for value in column.detach().cpu().tolist()] for name, column in outputs.items()}
    expected = {
        "query_ids": [1, 2, 3],
        "neighbor_counts": [1, 1, 0],
        "threshold_flags": [1, 1, 0],
    }
    if observed != expected:
        raise AssertionError(f"unexpected PyTorch output: observed={observed!r} expected={expected!r}")
    expected_checksum = 111 + 211 + 300
    observed_checksum = int(checksum.detach().cpu().item())
    if observed_checksum != expected_checksum:
        raise AssertionError(
            f"unexpected PyTorch same-stream checksum: observed={observed_checksum} "
            f"expected={expected_checksum}"
        )

    metadata = result["metadata"]
    plan = metadata["v4_plan"]
    source_protocols = list(plan["source_protocols"])
    if source_protocols != ["torch"]:
        raise AssertionError(f"unexpected source protocols for PyTorch probe: {source_protocols!r}")

    plan_ptrs = plan["borrowed_device_pointers"]
    pointer_identity = {name: int(plan_ptrs[name]) == int(ptr) for name, ptr in expected_ptrs.items()}
    if not all(pointer_identity.values()):
        raise AssertionError(f"PyTorch plan pointer identity failed: {pointer_identity!r}")
    native_pointer_echo = metadata["native_call_device_pointer_echo"]
    pointer_echo_identity = {
        name: int(native_pointer_echo.get(name, 0)) == int(ptr) for name, ptr in expected_ptrs.items()
    }
    if not metadata["native_call_device_pointer_echo_complete"]:
        raise AssertionError("native pointer echo is incomplete")
    if not all(pointer_echo_identity.values()):
        raise AssertionError(f"PyTorch native pointer echo failed: {pointer_echo_identity!r}")
    if int(metadata["caller_stream_handle"]) != stream_ptr:
        raise AssertionError("metadata did not preserve the PyTorch caller stream")
    if int(metadata["prepare_stream_handle"]) != stream_ptr:
        raise AssertionError("metadata did not preserve the PyTorch prepare stream")
    if metadata["native_async_ready"]:
        raise AssertionError("PyTorch probe must not authorize async")
    if metadata["v4_true_zero_copy_claim_authorized"]:
        raise AssertionError("PyTorch probe must not authorize public true-zero-copy")

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
            "observed": observed,
            "expected": expected,
            "same_stream_consumer_checksum_match": True,
            "observed_checksum": observed_checksum,
            "expected_checksum": expected_checksum,
            "grad_enabled_tensor_rejected": grad_enabled_rejected,
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
        "stream_contract": {
            "torch_stream_ptr": stream_ptr,
            "rtdl_prepare_stream_ptr": int(metadata["prepare_stream_handle"]),
            "rtdl_query_stream_ptr": int(metadata["caller_stream_handle"]),
            "same_stream_consumer_checksum_validated": True,
            "cross_stream_event_wait_validated": False,
            "async_completion_authorized": False,
        },
        "lifetime_contract": {
            "caller_owned_tensors_retained_until_stream_synchronized": True,
            "grad_enabled_tensors_must_be_detached": True,
            "full_pytorch_partner_surface_complete": False,
        },
        "claim_boundaries": {
            "pytorch_fixed_radius_m1_cuda_tensor_route_claim_authorized": True,
            "pytorch_route_claim_authorized": True,
            "pytorch_full_partner_surface_claim_authorized": False,
            "framework_neutral_dlpack_route_claim_authorized": False,
            "async_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "v4_true_zero_copy_claim_authorized": False,
            "reason": (
                "This probe validates the exact fixed-radius M1 route for PyTorch CUDA tensors "
                "with pointer identity, native pointer echo, same-stream checksum, caller-owned "
                "outputs, and grad-enabled tensor rejection. It does not validate a full PyTorch "
                "partner surface, framework-neutral DLPack, async, true-zero-copy, or speedup wording."
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
