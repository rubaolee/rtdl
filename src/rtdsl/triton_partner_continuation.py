from __future__ import annotations

from time import perf_counter
from typing import Any

from .partner_continuation_protocol import V2_5_PARTNER_CONTINUATION_VERSION
from .partner_continuation_protocol import V2_5_STATUS_PREVIEW_NOT_PROMOTED
from .partner_protocol import V2_4_PARTNER_PROTOCOL_VERSION
from .partner_protocol import v2_4_phase_timing_metadata


TRITON_SEGMENTED_SUM_F64_OPERATION = "segmented_sum_f64"
TRITON_SEGMENTED_COUNT_I64_OPERATION = "segmented_count_i64"
TRITON_PARTNER_CONTINUATION_STATUS = V2_5_STATUS_PREVIEW_NOT_PROMOTED


def triton_partner_available() -> bool:
    try:
        import triton  # noqa: F401
        import torch
    except ImportError:
        return False
    return bool(torch.cuda.is_available())


def describe_triton_segmented_sum_f64() -> dict[str, object]:
    descriptor = _base_triton_descriptor(TRITON_SEGMENTED_SUM_F64_OPERATION)
    descriptor["input_columns"] = ("group_ids:int64", "values:float64")
    descriptor["output_columns"] = ("sums:float64",)
    return descriptor


def describe_triton_segmented_count_i64() -> dict[str, object]:
    descriptor = _base_triton_descriptor(TRITON_SEGMENTED_COUNT_I64_OPERATION)
    descriptor["input_columns"] = ("group_ids:int64",)
    descriptor["output_columns"] = ("counts:int64",)
    return descriptor


def _base_triton_descriptor(operation: str) -> dict[str, object]:
    return {
        "contract_version": V2_5_PARTNER_CONTINUATION_VERSION,
        "operation": operation,
        "partner": "triton",
        "status": TRITON_PARTNER_CONTINUATION_STATUS,
        "phase": "partner_continuation",
        "requires_cuda": True,
        "requires_torch_tensor_inputs": True,
        "raw_kernel_required": False,
        "replaces_rt_traversal": False,
        "promoted_performance_path": False,
        "rt_traversal_contract_version": V2_4_PARTNER_PROTOCOL_VERSION,
        "claim_boundary": (
            "Triton executes only generic segmented-sum continuation over "
            "partner-owned tensors; RTDL/OptiX traversal remains separate"
        ),
    }


def run_triton_segmented_count_i64(
    group_ids: Any,
    *,
    group_count: int,
    block_size: int = 256,
) -> dict[str, object]:
    """Run the v2.5 Triton segmented-count continuation pilot."""

    triton, torch, tl = _import_triton_stack()
    _validate_torch_cuda_vector(group_ids, name="group_ids", dtype=torch.int64)
    group_count, block_size, row_count = _validate_group_run_shape(
        group_ids,
        group_count=group_count,
        block_size=block_size,
        torch=torch,
    )

    torch.cuda.synchronize(group_ids.device)
    started = perf_counter()
    output = torch.zeros((group_count,), dtype=torch.int64, device=group_ids.device)
    grid = (triton.cdiv(row_count, block_size),)
    _triton_segmented_count_i64_kernel(tl)[grid](
        group_ids,
        output,
        row_count,
        group_count,
        BLOCK_SIZE=block_size,
    )
    torch.cuda.synchronize(group_ids.device)
    elapsed = perf_counter() - started

    return _triton_run_result(
        operation=TRITON_SEGMENTED_COUNT_I64_OPERATION,
        outputs={"counts": output},
        elapsed=elapsed,
        source="run_triton_segmented_count_i64",
    )


def run_triton_segmented_sum_f64(
    group_ids: Any,
    values: Any,
    *,
    group_count: int,
    block_size: int = 256,
) -> dict[str, object]:
    """Run the first v2.5 Triton continuation kernel.

    Inputs must be CUDA torch tensors:

    - ``group_ids``: int64, shape ``(row_count,)``
    - ``values``: float64, shape ``(row_count,)``

    This function is intentionally not a promoted performance path. It is the
    first executable Triton pilot for the generic v2.5 continuation contract.
    """

    triton, torch, tl = _import_triton_stack()
    _validate_torch_cuda_vector(group_ids, name="group_ids", dtype=torch.int64)
    _validate_torch_cuda_vector(values, name="values", dtype=torch.float64)
    if tuple(group_ids.shape) != tuple(values.shape):
        raise ValueError("group_ids and values must have the same shape")
    group_count, block_size, row_count = _validate_group_run_shape(
        group_ids,
        group_count=group_count,
        block_size=block_size,
        torch=torch,
    )

    torch.cuda.synchronize(group_ids.device)
    started = perf_counter()
    output = torch.zeros((group_count,), dtype=torch.float64, device=values.device)
    grid = (triton.cdiv(row_count, block_size),)
    _triton_segmented_sum_f64_kernel(tl)[grid](
        group_ids,
        values,
        output,
        row_count,
        group_count,
        BLOCK_SIZE=block_size,
    )
    torch.cuda.synchronize(group_ids.device)
    elapsed = perf_counter() - started

    return _triton_run_result(
        operation=TRITON_SEGMENTED_SUM_F64_OPERATION,
        outputs={"sums": output},
        elapsed=elapsed,
        source="run_triton_segmented_sum_f64",
    )


def _triton_run_result(
    *,
    operation: str,
    outputs: dict[str, object],
    elapsed: float,
    source: str,
) -> dict[str, object]:
    return {
        "contract_version": V2_5_PARTNER_CONTINUATION_VERSION,
        "operation": operation,
        "partner": "triton",
        "status": TRITON_PARTNER_CONTINUATION_STATUS,
        "outputs": outputs,
        "phase_timing": v2_4_phase_timing_metadata(
            {"partner_continuation": elapsed},
            promoted_performance_path=False,
            same_phase_contract_as_basis=False,
            source=source,
        ),
        "raw_kernel_required": False,
        "replaces_rt_traversal": False,
        "promoted_performance_path": False,
        "rt_core_speedup_claim_authorized": False,
    }


def _triton_segmented_count_i64_kernel(tl):
    @__import__("triton").jit
    def kernel(group_ids, output, row_count: tl.constexpr, group_count: tl.constexpr, BLOCK_SIZE: tl.constexpr):
        program_id = tl.program_id(0)
        offsets = program_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offsets < row_count
        groups = tl.load(group_ids + offsets, mask=mask, other=-1)
        valid = mask & (groups >= 0) & (groups < group_count)
        ones = tl.full((BLOCK_SIZE,), 1, tl.int64)
        tl.atomic_add(output + groups, ones, sem="relaxed", mask=valid)

    return kernel


def _triton_segmented_sum_f64_kernel(tl):
    @__import__("triton").jit
    def kernel(group_ids, values, output, row_count: tl.constexpr, group_count: tl.constexpr, BLOCK_SIZE: tl.constexpr):
        program_id = tl.program_id(0)
        offsets = program_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offsets < row_count
        groups = tl.load(group_ids + offsets, mask=mask, other=-1)
        vals = tl.load(values + offsets, mask=mask, other=0.0)
        valid = mask & (groups >= 0) & (groups < group_count)
        tl.atomic_add(output + groups, vals, sem="relaxed", mask=valid)

    return kernel


def _import_triton_stack():
    try:
        import triton
        import triton.language as tl
        import torch
    except ImportError as exc:
        raise ModuleNotFoundError(
            "run_triton_segmented_sum_f64 requires triton and torch with CUDA; "
            "use an NVIDIA pod for execution validation"
        ) from exc
    if not torch.cuda.is_available():
        raise RuntimeError("run_triton_segmented_sum_f64 requires CUDA; use an NVIDIA pod")
    return triton, torch, tl


def _validate_group_run_shape(
    group_ids: Any,
    *,
    group_count: int,
    block_size: int,
    torch: Any,
) -> tuple[int, int, int]:
    group_count = int(group_count)
    if group_count < 0:
        raise ValueError("group_count must be non-negative")
    block_size = int(block_size)
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    row_count = int(group_ids.numel())
    if row_count and bool(torch.any((group_ids < 0) | (group_ids >= group_count)).item()):
        raise ValueError("group_ids must be in [0, group_count)")
    return group_count, block_size, row_count


def _validate_torch_cuda_vector(tensor: Any, *, name: str, dtype: Any) -> None:
    if getattr(tensor, "device", None) is None or getattr(tensor.device, "type", None) != "cuda":
        raise ValueError(f"{name} must be a CUDA torch tensor")
    if getattr(tensor, "dtype", None) != dtype:
        raise ValueError(f"{name} has wrong dtype")
    if int(getattr(tensor, "dim")()) != 1:
        raise ValueError(f"{name} must be a 1-D tensor")
