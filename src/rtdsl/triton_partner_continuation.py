from __future__ import annotations

from time import perf_counter
from typing import Any, Mapping

from .partner_continuation_protocol import RtdlPartnerContinuationSpec
from .partner_continuation_protocol import PartnerContinuationOverflowError
from .partner_continuation_protocol import V2_5_PARTNER_CONTINUATION_OPERATION_NAMES
from .partner_continuation_protocol import V2_5_PARTNER_CONTINUATION_VERSION
from .partner_continuation_protocol import V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS
from .partner_continuation_protocol import V2_5_STATUS_PREVIEW_NOT_PROMOTED
from .partner_continuation_protocol import V2_5_STATUS_REFERENCE_CONTRACT
from .partner_continuation_protocol import execute_v2_5_partner_continuation_reference
from .partner_protocol import V2_4_PARTNER_PROTOCOL_VERSION
from .partner_protocol import v2_4_phase_timing_metadata


TRITON_SEGMENTED_SUM_F64_OPERATION = "segmented_sum_f64"
TRITON_SEGMENTED_COUNT_I64_OPERATION = "segmented_count_i64"
TRITON_SEGMENTED_MIN_F64_OPERATION = "segmented_min_f64"
TRITON_SEGMENTED_MAX_F64_OPERATION = "segmented_max_f64"
TRITON_COMPACT_MASK_I64_OPERATION = "compact_mask_i64"
TRITON_GROUPED_ARGMIN_F64_OPERATION = "grouped_argmin_f64"
TRITON_BOUNDED_COLLECT_FINALIZE_I64_OPERATION = "bounded_collect_finalize_i64"
TRITON_PARTNER_CONTINUATION_STATUS = V2_5_STATUS_PREVIEW_NOT_PROMOTED
TRITON_TENSOR_CARRIER = "torch_cuda_tensor_for_triton_launch"


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


def describe_triton_segmented_min_f64() -> dict[str, object]:
    descriptor = _base_triton_descriptor(TRITON_SEGMENTED_MIN_F64_OPERATION)
    descriptor["input_columns"] = ("group_ids:int64", "values:float64")
    descriptor["output_columns"] = ("group_ids:int64", "mins:float64", "missing_group_ids:int64")
    descriptor["tensor_carrier_compaction_used"] = True
    return descriptor


def describe_triton_segmented_max_f64() -> dict[str, object]:
    descriptor = _base_triton_descriptor(TRITON_SEGMENTED_MAX_F64_OPERATION)
    descriptor["input_columns"] = ("group_ids:int64", "values:float64")
    descriptor["output_columns"] = ("group_ids:int64", "maxes:float64", "missing_group_ids:int64")
    descriptor["tensor_carrier_compaction_used"] = True
    return descriptor


def describe_triton_compact_mask_i64() -> dict[str, object]:
    descriptor = _base_triton_descriptor(TRITON_COMPACT_MASK_I64_OPERATION)
    descriptor["input_columns"] = ("values:int64", "mask:bool")
    descriptor["output_columns"] = ("values:int64", "original_indices:int64")
    descriptor["tensor_carrier_prefix_sum_used"] = True
    return descriptor


def describe_triton_grouped_argmin_f64() -> dict[str, object]:
    descriptor = _base_triton_descriptor(TRITON_GROUPED_ARGMIN_F64_OPERATION)
    descriptor["input_columns"] = ("group_ids:int64", "item_ids:int64", "scores:float64")
    descriptor["output_columns"] = (
        "group_ids:int64",
        "item_ids:int64",
        "scores:float64",
        "missing_group_ids:int64",
    )
    descriptor["tie_break"] = "lowest_score_then_lowest_item_id"
    descriptor["tensor_carrier_compaction_used"] = True
    return descriptor


def describe_triton_bounded_collect_finalize_i64() -> dict[str, object]:
    descriptor = _base_triton_descriptor(TRITON_BOUNDED_COLLECT_FINALIZE_I64_OPERATION)
    descriptor["input_columns"] = ("group_ids:int64", "item_ids:int64")
    descriptor["output_columns"] = ("group_ids:int64", "item_ids:int64", "row_offsets:int64")
    descriptor["failure_mode"] = "fail_closed_overflow"
    descriptor["within_group_order"] = "unspecified_nonsemantic"
    descriptor["tensor_carrier_prefix_sum_used"] = True
    return descriptor


def describe_triton_partner_continuation(operation: str) -> dict[str, object]:
    """Describe the Triton-owned v2.5 continuation for any generic operation."""

    if operation == TRITON_SEGMENTED_COUNT_I64_OPERATION:
        return describe_triton_segmented_count_i64()
    if operation == TRITON_SEGMENTED_SUM_F64_OPERATION:
        return describe_triton_segmented_sum_f64()
    if operation == TRITON_SEGMENTED_MIN_F64_OPERATION:
        return describe_triton_segmented_min_f64()
    if operation == TRITON_SEGMENTED_MAX_F64_OPERATION:
        return describe_triton_segmented_max_f64()
    if operation == TRITON_COMPACT_MASK_I64_OPERATION:
        return describe_triton_compact_mask_i64()
    if operation == TRITON_GROUPED_ARGMIN_F64_OPERATION:
        return describe_triton_grouped_argmin_f64()
    if operation == TRITON_BOUNDED_COLLECT_FINALIZE_I64_OPERATION:
        return describe_triton_bounded_collect_finalize_i64()
    spec = RtdlPartnerContinuationSpec(
        operation=operation,
        partner="triton",
        status="partner_descriptor_only",
    )
    metadata = spec.to_metadata()
    metadata.update(
        {
            "requires_cuda": True,
            "tensor_carrier": TRITON_TENSOR_CARRIER,
            "tensor_carrier_is_partner": False,
            "cupy_required": False,
            "pytorch_partner_required": False,
            "triton_kernel_available": False,
            "preview_kernel_operations": V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS,
            "claim_boundary": (
                "Triton is the v2.5 primary continuation partner, but this "
                "operation is descriptor-only until a generic Triton kernel and "
                "app-integration evidence exist. RTDL/OptiX traversal remains separate."
            ),
        }
    )
    return metadata


def run_triton_partner_continuation(
    operation: str,
    inputs: Mapping[str, object],
    *,
    block_size: int = 256,
    allow_reference_fallback: bool = False,
) -> dict[str, object]:
    """Run a Triton v2.5 continuation when a preview kernel exists.

    Unsupported operations can explicitly fall back to the Python reference for
    conformance. The fallback is labeled as `python_reference`; it is not a
    Triton performance path.
    """

    if operation not in V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
        raise ValueError(f"unsupported v2.5 partner continuation operation: {operation}")
    if operation == TRITON_SEGMENTED_COUNT_I64_OPERATION:
        try:
            return run_triton_segmented_count_i64(
                inputs["group_ids"],
                group_count=int(inputs["group_count"]),
                block_size=block_size,
            )
        except (ModuleNotFoundError, RuntimeError) as exc:
            if allow_reference_fallback and _is_triton_environment_error(exc):
                return _triton_reference_fallback(operation, inputs, str(exc))
            raise
    if operation == TRITON_SEGMENTED_SUM_F64_OPERATION:
        try:
            return run_triton_segmented_sum_f64(
                inputs["group_ids"],
                inputs["values"],
                group_count=int(inputs["group_count"]),
                block_size=block_size,
            )
        except (ModuleNotFoundError, RuntimeError) as exc:
            if allow_reference_fallback and _is_triton_environment_error(exc):
                return _triton_reference_fallback(operation, inputs, str(exc))
            raise
    if operation == TRITON_SEGMENTED_MIN_F64_OPERATION:
        try:
            return run_triton_segmented_min_f64(
                inputs["group_ids"],
                inputs["values"],
                group_count=int(inputs["group_count"]),
                block_size=block_size,
            )
        except (ModuleNotFoundError, RuntimeError) as exc:
            if allow_reference_fallback and _is_triton_environment_error(exc):
                return _triton_reference_fallback(operation, inputs, str(exc))
            raise
    if operation == TRITON_SEGMENTED_MAX_F64_OPERATION:
        try:
            return run_triton_segmented_max_f64(
                inputs["group_ids"],
                inputs["values"],
                group_count=int(inputs["group_count"]),
                block_size=block_size,
            )
        except (ModuleNotFoundError, RuntimeError) as exc:
            if allow_reference_fallback and _is_triton_environment_error(exc):
                return _triton_reference_fallback(operation, inputs, str(exc))
            raise
    if operation == TRITON_COMPACT_MASK_I64_OPERATION:
        try:
            return run_triton_compact_mask_i64(
                inputs["values"],
                inputs["mask"],
                block_size=block_size,
            )
        except (ModuleNotFoundError, RuntimeError) as exc:
            if allow_reference_fallback and _is_triton_environment_error(exc):
                return _triton_reference_fallback(operation, inputs, str(exc))
            raise
    if operation == TRITON_GROUPED_ARGMIN_F64_OPERATION:
        try:
            return run_triton_grouped_argmin_f64(
                inputs["group_ids"],
                inputs["item_ids"],
                inputs["scores"],
                group_count=int(inputs["group_count"]),
                block_size=block_size,
            )
        except (ModuleNotFoundError, RuntimeError) as exc:
            if allow_reference_fallback and _is_triton_environment_error(exc):
                return _triton_reference_fallback(operation, inputs, str(exc))
            raise
    if operation == TRITON_BOUNDED_COLLECT_FINALIZE_I64_OPERATION:
        try:
            return run_triton_bounded_collect_finalize_i64(
                inputs["group_ids"],
                inputs["item_ids"],
                group_count=int(inputs["group_count"]),
                k=int(inputs["k"]),
                total_row_capacity=inputs.get("total_row_capacity"),
                block_size=block_size,
            )
        except (ModuleNotFoundError, RuntimeError) as exc:
            if allow_reference_fallback and _is_triton_environment_error(exc):
                return _triton_reference_fallback(operation, inputs, str(exc))
            raise
    if not allow_reference_fallback:
        raise ValueError(
            f"Triton continuation `{operation}` is descriptor-only; "
            "pass allow_reference_fallback=True for conformance-only execution"
        )
    return _triton_reference_fallback(operation, inputs, "triton_descriptor_only_operation")


def _triton_reference_fallback(
    operation: str,
    inputs: Mapping[str, object],
    reason: str,
) -> dict[str, object]:
    result = execute_v2_5_partner_continuation_reference(operation, inputs)
    result["requested_partner"] = "triton"
    result["fallback_reason"] = reason
    result["status"] = V2_5_STATUS_REFERENCE_CONTRACT
    result["promoted_performance_path"] = False
    result["rt_core_speedup_claim_authorized"] = False
    return result


def _is_triton_environment_error(exc: BaseException) -> bool:
    message = str(exc).lower()
    return "requires cuda" in message or "unavailable" in message or isinstance(exc, ModuleNotFoundError)


def _base_triton_descriptor(operation: str) -> dict[str, object]:
    return {
        "contract_version": V2_5_PARTNER_CONTINUATION_VERSION,
        "operation": operation,
        "partner": "triton",
        "status": TRITON_PARTNER_CONTINUATION_STATUS,
        "phase": "partner_continuation",
        "requires_cuda": True,
        "tensor_carrier": TRITON_TENSOR_CARRIER,
        "tensor_carrier_is_partner": False,
        "requires_torch_tensor_inputs": True,
        "cupy_required": False,
        "pytorch_partner_required": False,
        "triton_kernel_available": True,
        "raw_kernel_required": False,
        "replaces_rt_traversal": False,
        "promoted_performance_path": False,
        "rt_traversal_contract_version": V2_4_PARTNER_PROTOCOL_VERSION,
        "claim_boundary": (
            "Triton executes only a generic post-RT continuation over tensor "
            "carriers used for launch; Torch is a carrier here, not the v2.5 "
            "partner. RTDL/OptiX traversal remains separate."
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
    if row_count:
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
    if row_count:
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


def run_triton_segmented_min_f64(
    group_ids: Any,
    values: Any,
    *,
    group_count: int,
    block_size: int = 256,
) -> dict[str, object]:
    """Run the v2.5 Triton segmented-min continuation preview."""

    return _run_triton_segmented_minmax_f64(
        group_ids,
        values,
        group_count=group_count,
        block_size=block_size,
        reduce="min",
    )


def run_triton_segmented_max_f64(
    group_ids: Any,
    values: Any,
    *,
    group_count: int,
    block_size: int = 256,
) -> dict[str, object]:
    """Run the v2.5 Triton segmented-max continuation preview."""

    return _run_triton_segmented_minmax_f64(
        group_ids,
        values,
        group_count=group_count,
        block_size=block_size,
        reduce="max",
    )


def _run_triton_segmented_minmax_f64(
    group_ids: Any,
    values: Any,
    *,
    group_count: int,
    block_size: int,
    reduce: str,
) -> dict[str, object]:
    triton, torch, tl = _import_triton_stack()
    _validate_torch_cuda_vector(group_ids, name="group_ids", dtype=torch.int64)
    _validate_torch_cuda_vector(values, name="values", dtype=torch.float64)
    if tuple(group_ids.shape) != tuple(values.shape):
        raise ValueError("group_ids and values must have the same shape")
    if int(values.numel()) and bool(torch.any(torch.isnan(values)).item()):
        raise ValueError("segmented min/max reject NaN values")
    group_count, block_size, row_count = _validate_group_run_shape(
        group_ids,
        group_count=group_count,
        block_size=block_size,
        torch=torch,
    )

    operation = TRITON_SEGMENTED_MIN_F64_OPERATION if reduce == "min" else TRITON_SEGMENTED_MAX_F64_OPERATION
    output_key = "mins" if reduce == "min" else "maxes"
    fill_value = float("inf") if reduce == "min" else float("-inf")

    torch.cuda.synchronize(group_ids.device)
    started = perf_counter()
    dense_values = torch.full((group_count,), fill_value, dtype=torch.float64, device=values.device)
    counts = torch.zeros((group_count,), dtype=torch.int64, device=group_ids.device)
    if row_count:
        grid = (triton.cdiv(row_count, block_size),)
        _triton_segmented_minmax_f64_kernel(tl, reduce)[grid](
            group_ids,
            values,
            dense_values,
            counts,
            row_count,
            group_count,
            BLOCK_SIZE=block_size,
        )
    present_mask = counts > 0
    present_group_ids = torch.nonzero(present_mask, as_tuple=False).reshape(-1).to(torch.int64)
    missing_group_ids = torch.nonzero(~present_mask, as_tuple=False).reshape(-1).to(torch.int64)
    compact_values = dense_values[present_mask]
    torch.cuda.synchronize(group_ids.device)
    elapsed = perf_counter() - started

    return _triton_run_result(
        operation=operation,
        outputs={
            "group_ids": present_group_ids,
            output_key: compact_values,
            "missing_group_ids": missing_group_ids,
            f"dense_{output_key}": dense_values,
            "present_counts": counts,
        },
        elapsed=elapsed,
        source=f"run_triton_segmented_{reduce}_f64",
        extra_metadata={"tensor_carrier_compaction_used": True},
    )


def run_triton_compact_mask_i64(
    values: Any,
    mask: Any,
    *,
    block_size: int = 256,
) -> dict[str, object]:
    """Run the v2.5 Triton compact-by-mask continuation preview."""

    triton, torch, tl = _import_triton_stack()
    _validate_torch_cuda_vector(values, name="values", dtype=torch.int64)
    _validate_torch_cuda_vector(mask, name="mask", dtype=torch.bool)
    if tuple(values.shape) != tuple(mask.shape):
        raise ValueError("values and mask must have the same shape")
    block_size = int(block_size)
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    row_count = int(values.numel())

    torch.cuda.synchronize(values.device)
    started = perf_counter()
    if row_count == 0:
        compact_values = torch.empty((0,), dtype=torch.int64, device=values.device)
        original_indices = torch.empty((0,), dtype=torch.int64, device=values.device)
        elapsed = perf_counter() - started
        return _triton_run_result(
            operation=TRITON_COMPACT_MASK_I64_OPERATION,
            outputs={"values": compact_values, "original_indices": original_indices},
            elapsed=elapsed,
            source="run_triton_compact_mask_i64",
            extra_metadata={"tensor_carrier_prefix_sum_used": True},
        )

    block_count = triton.cdiv(row_count, block_size)
    block_counts = torch.empty((block_count,), dtype=torch.int64, device=values.device)
    _triton_compact_count_blocks_i64_kernel(tl)[(block_count,)](
        mask,
        block_counts,
        row_count,
        BLOCK_SIZE=block_size,
    )
    block_prefix = torch.cumsum(block_counts, dim=0)
    total_count = int(block_prefix[-1].item()) if block_count else 0
    block_offsets = block_prefix - block_counts
    compact_values = torch.empty((total_count,), dtype=torch.int64, device=values.device)
    original_indices = torch.empty((total_count,), dtype=torch.int64, device=values.device)
    if total_count:
        _triton_compact_scatter_i64_kernel(tl)[(block_count,)](
            values,
            mask,
            block_offsets,
            compact_values,
            original_indices,
            row_count,
            BLOCK_SIZE=block_size,
        )
    torch.cuda.synchronize(values.device)
    elapsed = perf_counter() - started

    return _triton_run_result(
        operation=TRITON_COMPACT_MASK_I64_OPERATION,
        outputs={
            "values": compact_values,
            "original_indices": original_indices,
            "block_counts": block_counts,
        },
        elapsed=elapsed,
        source="run_triton_compact_mask_i64",
        extra_metadata={"tensor_carrier_prefix_sum_used": True},
    )


def run_triton_grouped_argmin_f64(
    group_ids: Any,
    item_ids: Any,
    scores: Any,
    *,
    group_count: int,
    block_size: int = 256,
) -> dict[str, object]:
    """Run the v2.5 Triton grouped-argmin continuation preview."""

    triton, torch, tl = _import_triton_stack()
    _validate_torch_cuda_vector(group_ids, name="group_ids", dtype=torch.int64)
    _validate_torch_cuda_vector(item_ids, name="item_ids", dtype=torch.int64)
    _validate_torch_cuda_vector(scores, name="scores", dtype=torch.float64)
    if not (tuple(group_ids.shape) == tuple(item_ids.shape) == tuple(scores.shape)):
        raise ValueError("group_ids, item_ids, and scores must have the same shape")
    if int(scores.numel()) and bool(torch.any(torch.isnan(scores)).item()):
        raise ValueError("grouped argmin rejects NaN scores")
    group_count, block_size, row_count = _validate_group_run_shape(
        group_ids,
        group_count=group_count,
        block_size=block_size,
        torch=torch,
    )

    torch.cuda.synchronize(group_ids.device)
    started = perf_counter()
    dense_scores = torch.full((group_count,), float("inf"), dtype=torch.float64, device=scores.device)
    dense_item_ids = torch.full(
        (group_count,),
        torch.iinfo(torch.int64).max,
        dtype=torch.int64,
        device=item_ids.device,
    )
    counts = torch.zeros((group_count,), dtype=torch.int64, device=group_ids.device)
    if row_count:
        grid = (triton.cdiv(row_count, block_size),)
        _triton_grouped_argmin_score_f64_kernel(tl)[grid](
            group_ids,
            scores,
            dense_scores,
            counts,
            row_count,
            group_count,
            BLOCK_SIZE=block_size,
        )
        # The second pass implements the documented lowest-item-id tie-break
        # after the best score is fixed. Keep the equal-score CUDA test in
        # goal2679 before promoting this beyond preview status.
        _triton_grouped_argmin_item_i64_kernel(tl)[grid](
            group_ids,
            item_ids,
            scores,
            dense_scores,
            dense_item_ids,
            row_count,
            group_count,
            BLOCK_SIZE=block_size,
        )
    present_mask = counts > 0
    present_group_ids = torch.nonzero(present_mask, as_tuple=False).reshape(-1).to(torch.int64)
    missing_group_ids = torch.nonzero(~present_mask, as_tuple=False).reshape(-1).to(torch.int64)
    compact_item_ids = dense_item_ids[present_mask]
    compact_scores = dense_scores[present_mask]
    torch.cuda.synchronize(group_ids.device)
    elapsed = perf_counter() - started

    return _triton_run_result(
        operation=TRITON_GROUPED_ARGMIN_F64_OPERATION,
        outputs={
            "group_ids": present_group_ids,
            "item_ids": compact_item_ids,
            "scores": compact_scores,
            "missing_group_ids": missing_group_ids,
            "dense_item_ids": dense_item_ids,
            "dense_scores": dense_scores,
            "present_counts": counts,
        },
        elapsed=elapsed,
        source="run_triton_grouped_argmin_f64",
        extra_metadata={
            "tie_break": "lowest_score_then_lowest_item_id",
            "tensor_carrier_compaction_used": True,
        },
    )


def run_triton_bounded_collect_finalize_i64(
    group_ids: Any,
    item_ids: Any,
    *,
    group_count: int,
    k: int,
    total_row_capacity: int | None = None,
    block_size: int = 256,
) -> dict[str, object]:
    """Run the v2.5 Triton bounded collect/finalize continuation preview.

    The preview is fail-closed: it checks all per-group and total capacities
    before materializing output rows. Within-group row order is not semantic.
    """

    triton, torch, tl = _import_triton_stack()
    _validate_torch_cuda_vector(group_ids, name="group_ids", dtype=torch.int64)
    _validate_torch_cuda_vector(item_ids, name="item_ids", dtype=torch.int64)
    if tuple(group_ids.shape) != tuple(item_ids.shape):
        raise ValueError("group_ids and item_ids must have the same shape")
    k = int(k)
    if k <= 0:
        raise ValueError("k must be positive")
    group_count, block_size, row_count = _validate_group_run_shape(
        group_ids,
        group_count=group_count,
        block_size=block_size,
        torch=torch,
    )
    if total_row_capacity is not None and row_count > int(total_row_capacity):
        raise PartnerContinuationOverflowError(
            "bounded_collect_finalize_i64 overflowed total row capacity; "
            "failure_mode=fail_closed_overflow; partial_result_returned=False"
        )

    torch.cuda.synchronize(group_ids.device)
    started = perf_counter()
    counts = torch.zeros((group_count,), dtype=torch.int64, device=group_ids.device)
    if row_count:
        grid = (triton.cdiv(row_count, block_size),)
        _triton_segmented_count_i64_kernel(tl)[grid](
            group_ids,
            counts,
            row_count,
            group_count,
            BLOCK_SIZE=block_size,
        )
    if group_count and bool(torch.any(counts > k).item()):
        raise PartnerContinuationOverflowError(
            "bounded_collect_finalize_i64 overflowed per-group capacity; "
            "failure_mode=fail_closed_overflow; partial_result_returned=False"
        )

    row_offsets = torch.empty((group_count + 1,), dtype=torch.int64, device=group_ids.device)
    row_offsets[0] = 0
    if group_count:
        row_offsets[1:] = torch.cumsum(counts, dim=0)
    out_group_ids = torch.empty((row_count,), dtype=torch.int64, device=group_ids.device)
    out_item_ids = torch.empty((row_count,), dtype=torch.int64, device=item_ids.device)
    write_counts = torch.zeros((group_count,), dtype=torch.int64, device=group_ids.device)
    if row_count:
        grid = (triton.cdiv(row_count, block_size),)
        _triton_bounded_collect_scatter_i64_kernel(tl)[grid](
            group_ids,
            item_ids,
            row_offsets,
            write_counts,
            out_group_ids,
            out_item_ids,
            row_count,
            group_count,
            BLOCK_SIZE=block_size,
        )
    torch.cuda.synchronize(group_ids.device)
    elapsed = perf_counter() - started

    return _triton_run_result(
        operation=TRITON_BOUNDED_COLLECT_FINALIZE_I64_OPERATION,
        outputs={
            "group_ids": out_group_ids,
            "item_ids": out_item_ids,
            "row_offsets": row_offsets,
            "counts": counts,
        },
        elapsed=elapsed,
        source="run_triton_bounded_collect_finalize_i64",
        extra_metadata={
            "failure_mode": "fail_closed_overflow",
            "within_group_order": "unspecified_nonsemantic",
            "tensor_carrier_prefix_sum_used": True,
        },
    )


def _triton_run_result(
    *,
    operation: str,
    outputs: dict[str, object],
    elapsed: float,
    source: str,
    extra_metadata: Mapping[str, object] | None = None,
) -> dict[str, object]:
    result = {
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
        "tensor_carrier": TRITON_TENSOR_CARRIER,
        "tensor_carrier_is_partner": False,
        "cupy_required": False,
        "pytorch_partner_required": False,
    }
    if extra_metadata:
        result.update(dict(extra_metadata))
    return result


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


def _triton_segmented_minmax_f64_kernel(tl, reduce: str):
    if reduce == "min":
        @__import__("triton").jit
        def min_kernel(group_ids, values, output, counts, row_count: tl.constexpr, group_count: tl.constexpr, BLOCK_SIZE: tl.constexpr):
            program_id = tl.program_id(0)
            offsets = program_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
            mask = offsets < row_count
            groups = tl.load(group_ids + offsets, mask=mask, other=-1)
            vals = tl.load(values + offsets, mask=mask, other=0.0)
            valid = mask & (groups >= 0) & (groups < group_count)
            tl.atomic_min(output + groups, vals, sem="relaxed", mask=valid)
            ones = tl.full((BLOCK_SIZE,), 1, tl.int64)
            tl.atomic_add(counts + groups, ones, sem="relaxed", mask=valid)

        return min_kernel
    elif reduce == "max":
        @__import__("triton").jit
        def max_kernel(group_ids, values, output, counts, row_count: tl.constexpr, group_count: tl.constexpr, BLOCK_SIZE: tl.constexpr):
            program_id = tl.program_id(0)
            offsets = program_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
            mask = offsets < row_count
            groups = tl.load(group_ids + offsets, mask=mask, other=-1)
            vals = tl.load(values + offsets, mask=mask, other=0.0)
            valid = mask & (groups >= 0) & (groups < group_count)
            tl.atomic_max(output + groups, vals, sem="relaxed", mask=valid)
            ones = tl.full((BLOCK_SIZE,), 1, tl.int64)
            tl.atomic_add(counts + groups, ones, sem="relaxed", mask=valid)

        return max_kernel
    raise ValueError("reduce must be min or max")


def _triton_compact_count_blocks_i64_kernel(tl):
    @__import__("triton").jit
    def kernel(mask, block_counts, row_count: tl.constexpr, BLOCK_SIZE: tl.constexpr):
        program_id = tl.program_id(0)
        offsets = program_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        valid = offsets < row_count
        keep = tl.load(mask + offsets, mask=valid, other=0)
        counts = tl.sum(tl.where(valid & keep, 1, 0), axis=0)
        tl.store(block_counts + program_id, counts)

    return kernel


def _triton_compact_scatter_i64_kernel(tl):
    @__import__("triton").jit
    def kernel(values, mask, block_offsets, compact_values, original_indices, row_count: tl.constexpr, BLOCK_SIZE: tl.constexpr):
        program_id = tl.program_id(0)
        offsets = program_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        valid = offsets < row_count
        keep = tl.load(mask + offsets, mask=valid, other=0)
        keep_i64 = tl.where(valid & keep, 1, 0)
        local_rank = tl.cumsum(keep_i64, axis=0) - 1
        base = tl.load(block_offsets + program_id)
        out_offsets = base + local_rank
        vals = tl.load(values + offsets, mask=valid, other=0)
        write_mask = valid & keep
        tl.store(compact_values + out_offsets, vals, mask=write_mask)
        tl.store(original_indices + out_offsets, offsets, mask=write_mask)

    return kernel


def _triton_grouped_argmin_score_f64_kernel(tl):
    @__import__("triton").jit
    def kernel(group_ids, scores, dense_scores, counts, row_count: tl.constexpr, group_count: tl.constexpr, BLOCK_SIZE: tl.constexpr):
        program_id = tl.program_id(0)
        offsets = program_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offsets < row_count
        groups = tl.load(group_ids + offsets, mask=mask, other=-1)
        vals = tl.load(scores + offsets, mask=mask, other=float("inf"))
        valid = mask & (groups >= 0) & (groups < group_count)
        tl.atomic_min(dense_scores + groups, vals, sem="relaxed", mask=valid)
        ones = tl.full((BLOCK_SIZE,), 1, tl.int64)
        tl.atomic_add(counts + groups, ones, sem="relaxed", mask=valid)

    return kernel


def _triton_grouped_argmin_item_i64_kernel(tl):
    @__import__("triton").jit
    def kernel(group_ids, item_ids, scores, dense_scores, dense_item_ids, row_count: tl.constexpr, group_count: tl.constexpr, BLOCK_SIZE: tl.constexpr):
        program_id = tl.program_id(0)
        offsets = program_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offsets < row_count
        groups = tl.load(group_ids + offsets, mask=mask, other=-1)
        items = tl.load(item_ids + offsets, mask=mask, other=0)
        vals = tl.load(scores + offsets, mask=mask, other=float("inf"))
        valid = mask & (groups >= 0) & (groups < group_count)
        best_scores = tl.load(dense_scores + groups, mask=valid, other=float("inf"))
        is_best = valid & (vals == best_scores)
        tl.atomic_min(dense_item_ids + groups, items, sem="relaxed", mask=is_best)

    return kernel


def _triton_bounded_collect_scatter_i64_kernel(tl):
    @__import__("triton").jit
    def kernel(group_ids, item_ids, row_offsets, write_counts, out_group_ids, out_item_ids, row_count: tl.constexpr, group_count: tl.constexpr, BLOCK_SIZE: tl.constexpr):
        program_id = tl.program_id(0)
        offsets = program_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offsets < row_count
        groups = tl.load(group_ids + offsets, mask=mask, other=-1)
        items = tl.load(item_ids + offsets, mask=mask, other=0)
        valid = mask & (groups >= 0) & (groups < group_count)
        ones = tl.full((BLOCK_SIZE,), 1, tl.int64)
        slots = tl.atomic_add(write_counts + groups, ones, sem="relaxed", mask=valid)
        bases = tl.load(row_offsets + groups, mask=valid, other=0)
        out_offsets = bases + slots
        tl.store(out_group_ids + out_offsets, groups, mask=valid)
        tl.store(out_item_ids + out_offsets, items, mask=valid)

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
    globals()["triton"] = triton
    globals()["tl"] = tl
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
