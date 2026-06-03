from __future__ import annotations

from time import perf_counter
from typing import Any

from .partner_continuation_protocol import V2_5_PARTNER_CONTINUATION_VERSION
from .partner_continuation_protocol import V2_5_STATUS_PREVIEW_NOT_PROMOTED
from .partner_protocol import V2_4_PARTNER_PROTOCOL_VERSION
from .partner_protocol import v2_4_phase_timing_metadata


NUMBA_SEGMENTED_COUNT_I64_OPERATION = "segmented_count_i64"
NUMBA_SEGMENTED_SUM_F64_OPERATION = "segmented_sum_f64"
NUMBA_SEGMENTED_MIN_F64_OPERATION = "segmented_min_f64"
NUMBA_SEGMENTED_MAX_F64_OPERATION = "segmented_max_f64"
NUMBA_COMPACT_MASK_I64_OPERATION = "compact_mask_i64"
NUMBA_GROUPED_ARGMIN_F64_OPERATION = "grouped_argmin_f64"
NUMBA_GROUPED_ARGMAX_F64_OPERATION = "grouped_argmax_f64"
NUMBA_GLOBAL_ARGMAX_U32_F64_OPERATION = "global_argmax_u32_f64"
NUMBA_PAIRWISE_L2_SQ_SCORE_ROWS_2D_OPERATION = "pairwise_l2_sq_score_rows_2d"
NUMBA_PAIRWISE_L2_SQ_BLOCK_NEAREST_ROWS_2D_OPERATION = "pairwise_l2_sq_block_nearest_rows_2d"
NUMBA_PARTNER_CONTINUATION_STATUS = V2_5_STATUS_PREVIEW_NOT_PROMOTED
NUMBA_GROUP_ID_VALIDATION_MODE = "device_resident_error_flag"
_NUMBA_KERNEL_CACHE: dict[tuple[int, str], Any] = {}


def numba_partner_available() -> bool:
    try:
        _activate_numba_cuda_redirector()
        from numba import cuda
    except ImportError:
        return False
    return bool(cuda.is_available())


def describe_numba_segmented_count_i64() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_SEGMENTED_COUNT_I64_OPERATION)
    descriptor["input_columns"] = ("group_ids:int64",)
    descriptor["output_columns"] = ("counts:int64",)
    return descriptor


def describe_numba_segmented_sum_f64() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_SEGMENTED_SUM_F64_OPERATION)
    descriptor["input_columns"] = ("group_ids:int64", "values:float64")
    descriptor["output_columns"] = ("sums:float64",)
    return descriptor


def describe_numba_segmented_min_f64() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_SEGMENTED_MIN_F64_OPERATION)
    descriptor["input_columns"] = ("group_ids:int64", "values:float64")
    descriptor["output_columns"] = ("mins:float64",)
    descriptor["empty_group_fill"] = "initial"
    return descriptor


def describe_numba_segmented_max_f64() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_SEGMENTED_MAX_F64_OPERATION)
    descriptor["input_columns"] = ("group_ids:int64", "values:float64")
    descriptor["output_columns"] = ("maxes:float64",)
    descriptor["empty_group_fill"] = "initial"
    return descriptor


def describe_numba_compact_mask_i64() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_COMPACT_MASK_I64_OPERATION)
    descriptor["input_columns"] = ("values:int64", "mask:bool")
    descriptor["output_columns"] = ("values:int64", "original_indices:int64")
    descriptor["stable_input_order"] = True
    descriptor["host_prefix_sum_used"] = True
    return descriptor


def describe_numba_grouped_argmin_f64() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_GROUPED_ARGMIN_F64_OPERATION)
    descriptor["input_columns"] = ("group_ids:int64", "item_ids:int64", "scores:float64")
    descriptor["output_columns"] = (
        "group_ids:int64",
        "item_ids:int64",
        "scores:float64",
        "missing_group_ids:int64",
    )
    descriptor["tie_break"] = "lowest_score_then_lowest_item_id"
    descriptor["host_present_group_compaction_used"] = True
    return descriptor


def describe_numba_grouped_argmax_f64() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_GROUPED_ARGMAX_F64_OPERATION)
    descriptor["input_columns"] = ("group_ids:int64", "item_ids:int64", "scores:float64")
    descriptor["output_columns"] = (
        "group_ids:int64",
        "item_ids:int64",
        "scores:float64",
        "missing_group_ids:int64",
    )
    descriptor["tie_break"] = "highest_score_then_lowest_item_id"
    descriptor["host_present_group_compaction_used"] = True
    return descriptor


def describe_numba_global_argmax_u32_f64() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_GLOBAL_ARGMAX_U32_F64_OPERATION)
    descriptor["input_columns"] = ("item_ids:uint32", "scores:float64")
    descriptor["output_columns"] = ("item_ids:uint32", "scores:float64", "row_indices:int64")
    descriptor["tie_break"] = "highest_score_then_lowest_item_id_then_lowest_row_index"
    descriptor["invalid_item_id_default"] = 0xFFFFFFFF
    return descriptor


def describe_numba_pairwise_l2_sq_score_rows_2d() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_PAIRWISE_L2_SQ_SCORE_ROWS_2D_OPERATION)
    descriptor["input_columns"] = (
        "source_x:float64",
        "source_y:float64",
        "target_ids:int64",
        "target_x:float64",
        "target_y:float64",
    )
    descriptor["output_columns"] = ("group_ids:int64", "item_ids:int64", "scores:float64")
    descriptor["group_id_semantics"] = "dense_source_row_index"
    descriptor["item_id_semantics"] = "caller_supplied_target_id"
    descriptor["score_semantics"] = "squared_l2_distance"
    descriptor["host_score_row_materialization_used"] = False
    return descriptor


def describe_numba_pairwise_l2_sq_block_nearest_rows_2d() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_PAIRWISE_L2_SQ_BLOCK_NEAREST_ROWS_2D_OPERATION)
    descriptor["input_columns"] = (
        "source_x:float64",
        "source_y:float64",
        "target_ids:int64",
        "target_x:float64",
        "target_y:float64",
    )
    descriptor["output_columns"] = ("group_ids:int64", "item_ids:int64", "scores:float64")
    descriptor["group_id_semantics"] = "dense_source_row_index"
    descriptor["item_id_semantics"] = "caller_supplied_target_id"
    descriptor["score_semantics"] = "per_source_tile_nearest_squared_l2_distance"
    descriptor["tie_break"] = "lowest_score_then_lowest_item_id_per_source_tile"
    descriptor["host_score_row_materialization_used"] = False
    descriptor["bounded_tile_summary_rows"] = True
    return descriptor


def _base_numba_descriptor(operation: str) -> dict[str, object]:
    return {
        "contract_version": V2_5_PARTNER_CONTINUATION_VERSION,
        "operation": operation,
        "partner": "numba",
        "status": NUMBA_PARTNER_CONTINUATION_STATUS,
        "phase": "partner_continuation",
        "requires_cuda": True,
        "requires_numba_cuda_device_arrays": True,
        "group_id_validation_mode": NUMBA_GROUP_ID_VALIDATION_MODE,
        "raw_kernel_required": False,
        "replaces_rt_traversal": False,
        "promoted_performance_path": False,
        "rt_traversal_contract_version": V2_4_PARTNER_PROTOCOL_VERSION,
        "claim_boundary": (
            "Numba executes only generic grouped continuation over device arrays; "
            "RTDL/OptiX traversal remains separate"
        ),
    }


def run_numba_segmented_count_i64(
    group_ids: Any,
    *,
    group_count: int,
    block_size: int = 256,
    validate_group_ids: bool = True,
) -> dict[str, object]:
    """Run the v2.5 Numba segmented-count continuation pilot."""

    cuda, np = _import_numba_stack()
    _validate_numba_cuda_vector(group_ids, name="group_ids", dtype=np.int64)
    group_count, block_size, row_count = _validate_group_run_shape(
        group_ids,
        group_count=group_count,
        block_size=block_size,
        validate_group_ids=validate_group_ids,
        cuda=cuda,
        np=np,
    )

    cuda.synchronize()
    started = perf_counter()
    output = cuda.device_array((group_count,), dtype=np.int64)
    output.copy_to_device(np.zeros((group_count,), dtype=np.int64))
    if row_count:
        grid = ((row_count + block_size - 1) // block_size,)
        _cached_numba_kernel(cuda, _numba_segmented_count_i64_kernel)[grid, block_size](
            group_ids,
            output,
            row_count,
            group_count,
        )
    cuda.synchronize()
    elapsed = perf_counter() - started

    return _numba_run_result(
        operation=NUMBA_SEGMENTED_COUNT_I64_OPERATION,
        outputs={"counts": output},
        elapsed=elapsed,
        source="run_numba_segmented_count_i64",
    )


def run_numba_segmented_sum_f64(
    group_ids: Any,
    values: Any,
    *,
    group_count: int,
    block_size: int = 256,
    validate_group_ids: bool = True,
) -> dict[str, object]:
    """Run the v2.5 Numba segmented-sum continuation pilot."""

    cuda, np = _import_numba_stack()
    _validate_numba_cuda_vector(group_ids, name="group_ids", dtype=np.int64)
    _validate_numba_cuda_vector(values, name="values", dtype=np.float64)
    if tuple(group_ids.shape) != tuple(values.shape):
        raise ValueError("group_ids and values must have the same shape")
    group_count, block_size, row_count = _validate_group_run_shape(
        group_ids,
        group_count=group_count,
        block_size=block_size,
        validate_group_ids=validate_group_ids,
        cuda=cuda,
        np=np,
    )

    cuda.synchronize()
    started = perf_counter()
    output = cuda.device_array((group_count,), dtype=np.float64)
    output.copy_to_device(np.zeros((group_count,), dtype=np.float64))
    if row_count:
        grid = ((row_count + block_size - 1) // block_size,)
        _cached_numba_kernel(cuda, _numba_segmented_sum_f64_kernel)[grid, block_size](
            group_ids,
            values,
            output,
            row_count,
            group_count,
        )
    cuda.synchronize()
    elapsed = perf_counter() - started

    return _numba_run_result(
        operation=NUMBA_SEGMENTED_SUM_F64_OPERATION,
        outputs={"sums": output},
        elapsed=elapsed,
        source="run_numba_segmented_sum_f64",
    )


def run_numba_segmented_min_f64(
    group_ids: Any,
    values: Any,
    *,
    group_count: int,
    initial: float,
    block_size: int = 256,
    validate_group_ids: bool = True,
) -> dict[str, object]:
    """Run the v2.6 Numba segmented-min continuation over CUDA arrays."""

    return _run_numba_segmented_extreme_f64(
        group_ids,
        values,
        group_count=group_count,
        initial=initial,
        block_size=block_size,
        validate_group_ids=validate_group_ids,
        operation=NUMBA_SEGMENTED_MIN_F64_OPERATION,
        output_name="mins",
        source="run_numba_segmented_min_f64",
        kernel_factory=_numba_segmented_min_f64_kernel,
    )


def run_numba_segmented_max_f64(
    group_ids: Any,
    values: Any,
    *,
    group_count: int,
    initial: float,
    block_size: int = 256,
    validate_group_ids: bool = True,
) -> dict[str, object]:
    """Run the v2.6 Numba segmented-max continuation over CUDA arrays."""

    return _run_numba_segmented_extreme_f64(
        group_ids,
        values,
        group_count=group_count,
        initial=initial,
        block_size=block_size,
        validate_group_ids=validate_group_ids,
        operation=NUMBA_SEGMENTED_MAX_F64_OPERATION,
        output_name="maxes",
        source="run_numba_segmented_max_f64",
        kernel_factory=_numba_segmented_max_f64_kernel,
    )


def run_numba_grouped_argmin_f64(
    group_ids: Any,
    item_ids: Any,
    scores: Any,
    *,
    group_count: int,
    block_size: int = 256,
    validate_group_ids: bool = True,
    validate_nan_scores: bool = True,
    compact_present_groups: bool = True,
) -> dict[str, object]:
    """Run grouped argmin over Numba CUDA arrays with a stable item-id tie-break."""

    return _run_numba_grouped_arg_reduce_f64(
        group_ids,
        item_ids,
        scores,
        group_count=group_count,
        block_size=block_size,
        validate_group_ids=validate_group_ids,
        validate_nan_scores=validate_nan_scores,
        compact_present_groups=compact_present_groups,
        operation=NUMBA_GROUPED_ARGMIN_F64_OPERATION,
        source="run_numba_grouped_argmin_f64",
        score_initial=float("inf"),
        score_kernel_factory=_numba_grouped_argmin_score_f64_kernel,
        tie_break="lowest_score_then_lowest_item_id",
    )


def run_numba_grouped_argmax_f64(
    group_ids: Any,
    item_ids: Any,
    scores: Any,
    *,
    group_count: int,
    block_size: int = 256,
    validate_group_ids: bool = True,
    validate_nan_scores: bool = True,
    compact_present_groups: bool = True,
) -> dict[str, object]:
    """Run grouped argmax over Numba CUDA arrays with a stable item-id tie-break."""

    return _run_numba_grouped_arg_reduce_f64(
        group_ids,
        item_ids,
        scores,
        group_count=group_count,
        block_size=block_size,
        validate_group_ids=validate_group_ids,
        validate_nan_scores=validate_nan_scores,
        compact_present_groups=compact_present_groups,
        operation=NUMBA_GROUPED_ARGMAX_F64_OPERATION,
        source="run_numba_grouped_argmax_f64",
        score_initial=-float("inf"),
        score_kernel_factory=_numba_grouped_argmax_score_f64_kernel,
        tie_break="highest_score_then_lowest_item_id",
    )


def run_numba_global_argmax_u32_f64(
    item_ids: Any,
    scores: Any,
    *,
    invalid_item_id: int = 0xFFFFFFFF,
    block_size: int = 256,
) -> dict[str, object]:
    """Run a generic global argmax over CUDA columns with a stable uint32 item tie-break."""

    cuda, np = _import_numba_stack()
    item_ids = _as_numba_cuda_vector(item_ids, name="item_ids", dtype=np.uint32, cuda=cuda, np=np)
    scores = _as_numba_cuda_vector(scores, name="scores", dtype=np.float64, cuda=cuda, np=np)
    if tuple(item_ids.shape) != tuple(scores.shape):
        raise ValueError("item_ids and scores must have the same shape")
    row_count = int(item_ids.shape[0])
    block_size = int(block_size)
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    invalid_u32 = int(invalid_item_id) & 0xFFFFFFFF

    if block_size > 256:
        raise ValueError("block_size must be <= 256 for global_argmax_u32_f64")
    if row_count == 0:
        raise ValueError("global_argmax_u32_f64 requires at least one valid item row")

    cuda.synchronize()
    started = perf_counter()
    current_count = row_count
    block_count = (current_count + block_size - 1) // block_size
    current_item_ids = cuda.device_array((block_count,), dtype=np.uint32)
    current_scores = cuda.device_array((block_count,), dtype=np.float64)
    current_row_indices = cuda.device_array((block_count,), dtype=np.int64)
    current_valid_counts = cuda.device_array((block_count,), dtype=np.int64)
    _cached_numba_kernel(cuda, _numba_global_argmax_initial_block_reduce_u32_f64_kernel)[(block_count,), block_size](
        item_ids,
        scores,
        current_item_ids,
        current_scores,
        current_row_indices,
        current_valid_counts,
        row_count,
        invalid_u32,
    )
    cuda.synchronize()
    valid_count = cuda.device_array((1,), dtype=np.int64)
    valid_total = int(np.asarray(current_valid_counts.copy_to_host(), dtype=np.int64).sum())
    valid_count.copy_to_device(np.asarray([valid_total], dtype=np.int64))
    if valid_total == 0:
        raise ValueError("global_argmax_u32_f64 requires at least one valid item row")

    current_count = block_count
    while current_count > 1:
        block_count = (current_count + block_size - 1) // block_size
        next_item_ids = cuda.device_array((block_count,), dtype=np.uint32)
        next_scores = cuda.device_array((block_count,), dtype=np.float64)
        next_row_indices = cuda.device_array((block_count,), dtype=np.int64)
        next_valid_counts = cuda.device_array((block_count,), dtype=np.int64)
        _cached_numba_kernel(cuda, _numba_global_argmax_block_reduce_u32_f64_kernel)[(block_count,), block_size](
            current_item_ids,
            current_scores,
            current_row_indices,
            current_valid_counts,
            next_item_ids,
            next_scores,
            next_row_indices,
            next_valid_counts,
            current_count,
            invalid_u32,
        )
        cuda.synchronize()
        current_item_ids = next_item_ids
        current_scores = next_scores
        current_row_indices = next_row_indices
        current_valid_counts = next_valid_counts
        current_count = block_count

    elapsed = perf_counter() - started

    return _numba_run_result(
        operation=NUMBA_GLOBAL_ARGMAX_U32_F64_OPERATION,
        outputs={
            "item_ids": current_item_ids,
            "scores": current_scores,
            "row_indices": current_row_indices,
            "valid_count": valid_count,
        },
        elapsed=elapsed,
        source="run_numba_global_argmax_u32_f64",
        extra_metadata={
            "row_count": row_count,
            "invalid_item_id": invalid_u32,
            "tie_break": "highest_score_then_lowest_item_id_then_lowest_row_index",
            "reduction_strategy": "multi_stage_block_reduce_no_global_atomics",
            "host_row_materialization_used": False,
        },
    )


def run_numba_pairwise_l2_sq_score_rows_2d(
    source_x: Any,
    source_y: Any,
    target_ids: Any,
    target_x: Any,
    target_y: Any,
    *,
    block_size: int = 256,
) -> dict[str, object]:
    """Generate generic pairwise 2D squared-L2 score rows on a Numba CUDA device."""

    cuda, np = _import_numba_stack()
    _validate_numba_cuda_vector(source_x, name="source_x", dtype=np.float64)
    _validate_numba_cuda_vector(source_y, name="source_y", dtype=np.float64)
    _validate_numba_cuda_vector(target_ids, name="target_ids", dtype=np.int64)
    _validate_numba_cuda_vector(target_x, name="target_x", dtype=np.float64)
    _validate_numba_cuda_vector(target_y, name="target_y", dtype=np.float64)
    if tuple(source_x.shape) != tuple(source_y.shape):
        raise ValueError("source_x and source_y must have the same shape")
    if not (tuple(target_ids.shape) == tuple(target_x.shape) == tuple(target_y.shape)):
        raise ValueError("target_ids, target_x, and target_y must have the same shape")
    source_count = int(source_x.shape[0])
    target_count = int(target_ids.shape[0])
    block_size = int(block_size)
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    row_count = source_count * target_count

    cuda.synchronize()
    started = perf_counter()
    group_ids = cuda.device_array((row_count,), dtype=np.int64)
    item_ids = cuda.device_array((row_count,), dtype=np.int64)
    scores = cuda.device_array((row_count,), dtype=np.float64)
    if row_count:
        grid = ((row_count + block_size - 1) // block_size,)
        _cached_numba_kernel(cuda, _numba_pairwise_l2_sq_score_rows_2d_kernel)[grid, block_size](
            source_x,
            source_y,
            target_ids,
            target_x,
            target_y,
            group_ids,
            item_ids,
            scores,
            source_count,
            target_count,
            row_count,
        )
    cuda.synchronize()
    elapsed = perf_counter() - started

    return _numba_run_result(
        operation=NUMBA_PAIRWISE_L2_SQ_SCORE_ROWS_2D_OPERATION,
        outputs={"group_ids": group_ids, "item_ids": item_ids, "scores": scores},
        elapsed=elapsed,
        source="run_numba_pairwise_l2_sq_score_rows_2d",
        extra_metadata={
            "source_count": source_count,
            "target_count": target_count,
            "row_count": row_count,
            "group_id_semantics": "dense_source_row_index",
            "item_id_semantics": "caller_supplied_target_id",
            "score_semantics": "squared_l2_distance",
            "host_score_row_materialization_used": False,
            "score_rows_generated_on_partner_device": True,
        },
    )


def run_numba_pairwise_l2_sq_block_nearest_rows_2d(
    source_x: Any,
    source_y: Any,
    target_ids: Any,
    target_x: Any,
    target_y: Any,
    *,
    block_size: int = 256,
) -> dict[str, object]:
    """Emit one nearest squared-L2 score row per source point and target tile."""

    cuda, np = _import_numba_stack()
    _validate_numba_cuda_vector(source_x, name="source_x", dtype=np.float64)
    _validate_numba_cuda_vector(source_y, name="source_y", dtype=np.float64)
    _validate_numba_cuda_vector(target_ids, name="target_ids", dtype=np.int64)
    _validate_numba_cuda_vector(target_x, name="target_x", dtype=np.float64)
    _validate_numba_cuda_vector(target_y, name="target_y", dtype=np.float64)
    if tuple(source_x.shape) != tuple(source_y.shape):
        raise ValueError("source_x and source_y must have the same shape")
    if not (tuple(target_ids.shape) == tuple(target_x.shape) == tuple(target_y.shape)):
        raise ValueError("target_ids, target_x, and target_y must have the same shape")
    source_count = int(source_x.shape[0])
    target_count = int(target_ids.shape[0])
    block_size = int(block_size)
    if block_size not in {32, 64, 128, 256}:
        raise ValueError("block_size must be one of 32, 64, 128, or 256")
    target_tile_count = (target_count + block_size - 1) // block_size if target_count else 0
    row_count = source_count * target_tile_count

    cuda.synchronize()
    started = perf_counter()
    group_ids = cuda.device_array((row_count,), dtype=np.int64)
    item_ids = cuda.device_array((row_count,), dtype=np.int64)
    scores = cuda.device_array((row_count,), dtype=np.float64)
    if row_count:
        grid = (source_count, target_tile_count)
        _cached_numba_kernel(cuda, _numba_pairwise_l2_sq_block_nearest_rows_2d_kernel)[grid, block_size](
            source_x,
            source_y,
            target_ids,
            target_x,
            target_y,
            group_ids,
            item_ids,
            scores,
            target_count,
            target_tile_count,
        )
    cuda.synchronize()
    elapsed = perf_counter() - started

    return _numba_run_result(
        operation=NUMBA_PAIRWISE_L2_SQ_BLOCK_NEAREST_ROWS_2D_OPERATION,
        outputs={"group_ids": group_ids, "item_ids": item_ids, "scores": scores},
        elapsed=elapsed,
        source="run_numba_pairwise_l2_sq_block_nearest_rows_2d",
        extra_metadata={
            "source_count": source_count,
            "target_count": target_count,
            "target_tile_count": target_tile_count,
            "row_count": row_count,
            "logical_pair_count": source_count * target_count,
            "group_id_semantics": "dense_source_row_index",
            "item_id_semantics": "caller_supplied_target_id",
            "score_semantics": "per_source_tile_nearest_squared_l2_distance",
            "tie_break": "lowest_score_then_lowest_item_id_per_source_tile",
            "host_score_row_materialization_used": False,
            "score_rows_generated_on_partner_device": True,
            "bounded_tile_summary_rows": True,
        },
    )


def run_numba_compact_mask_i64(
    values: Any,
    mask: Any,
    *,
    block_size: int = 256,
) -> dict[str, object]:
    """Run a stable Numba compact-by-mask continuation over CUDA arrays."""

    cuda, np = _import_numba_stack()
    _validate_numba_cuda_vector(values, name="values", dtype=np.int64)
    _validate_numba_cuda_vector(mask, name="mask", dtype=np.bool_)
    if tuple(values.shape) != tuple(mask.shape):
        raise ValueError("values and mask must have the same shape")
    block_size = int(block_size)
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    row_count = int(values.shape[0])

    cuda.synchronize()
    started = perf_counter()
    if row_count == 0:
        compact_values = cuda.device_array((0,), dtype=np.int64)
        original_indices = cuda.device_array((0,), dtype=np.int64)
        elapsed = perf_counter() - started
        return _numba_run_result(
            operation=NUMBA_COMPACT_MASK_I64_OPERATION,
            outputs={"values": compact_values, "original_indices": original_indices},
            elapsed=elapsed,
            source="run_numba_compact_mask_i64",
            extra_metadata={"stable_input_order": True, "host_prefix_sum_used": True},
        )

    block_count = (row_count + block_size - 1) // block_size
    block_counts = cuda.device_array((block_count,), dtype=np.int64)
    _cached_numba_kernel(cuda, _numba_compact_count_blocks_i64_kernel)[(block_count,), 1](
        mask,
        block_counts,
        row_count,
        block_size,
    )
    cuda.synchronize()
    host_counts = block_counts.copy_to_host()
    host_offsets = np.empty((block_count,), dtype=np.int64)
    total_count = 0
    for index, count in enumerate(host_counts):
        host_offsets[index] = total_count
        total_count += int(count)
    block_offsets = cuda.to_device(host_offsets)
    compact_values = cuda.device_array((total_count,), dtype=np.int64)
    original_indices = cuda.device_array((total_count,), dtype=np.int64)
    if total_count:
        _cached_numba_kernel(cuda, _numba_compact_scatter_i64_kernel)[(block_count,), block_size](
            values,
            mask,
            block_offsets,
            compact_values,
            original_indices,
            row_count,
            block_size,
        )
    cuda.synchronize()
    elapsed = perf_counter() - started
    return _numba_run_result(
        operation=NUMBA_COMPACT_MASK_I64_OPERATION,
        outputs={
            "values": compact_values,
            "original_indices": original_indices,
            "block_counts": block_counts,
        },
        elapsed=elapsed,
        source="run_numba_compact_mask_i64",
        extra_metadata={"stable_input_order": True, "host_prefix_sum_used": True},
    )


def run_numba_mask_indices_i64(
    mask: Any,
    *,
    block_size: int = 256,
) -> dict[str, object]:
    """Return stable original indices where a Numba CUDA boolean mask is true."""

    cuda, np = _import_numba_stack()
    _validate_numba_cuda_vector(mask, name="mask", dtype=np.bool_)
    row_count = int(mask.shape[0])
    values = cuda.device_array((row_count,), dtype=np.int64)
    if row_count:
        block_size = int(block_size)
        if block_size <= 0:
            raise ValueError("block_size must be positive")
        grid = ((row_count + block_size - 1) // block_size,)
        _cached_numba_kernel(cuda, _numba_iota_i64_kernel)[grid, block_size](values, row_count)
    return run_numba_compact_mask_i64(values, mask, block_size=block_size)


def _run_numba_segmented_extreme_f64(
    group_ids: Any,
    values: Any,
    *,
    group_count: int,
    initial: float,
    block_size: int,
    validate_group_ids: bool,
    operation: str,
    output_name: str,
    source: str,
    kernel_factory: Any,
) -> dict[str, object]:
    cuda, np = _import_numba_stack()
    _validate_numba_cuda_vector(group_ids, name="group_ids", dtype=np.int64)
    _validate_numba_cuda_vector(values, name="values", dtype=np.float64)
    if tuple(group_ids.shape) != tuple(values.shape):
        raise ValueError("group_ids and values must have the same shape")
    group_count, block_size, row_count = _validate_group_run_shape(
        group_ids,
        group_count=group_count,
        block_size=block_size,
        validate_group_ids=validate_group_ids,
        cuda=cuda,
        np=np,
    )

    cuda.synchronize()
    started = perf_counter()
    output = cuda.device_array((group_count,), dtype=np.float64)
    output.copy_to_device(np.full((group_count,), float(initial), dtype=np.float64))
    if row_count:
        grid = ((row_count + block_size - 1) // block_size,)
        _cached_numba_kernel(cuda, kernel_factory)[grid, block_size](group_ids, values, output, row_count, group_count)
    cuda.synchronize()
    elapsed = perf_counter() - started

    return _numba_run_result(
        operation=operation,
        outputs={output_name: output},
        elapsed=elapsed,
        source=source,
    )


def _run_numba_grouped_arg_reduce_f64(
    group_ids: Any,
    item_ids: Any,
    scores: Any,
    *,
    group_count: int,
    block_size: int,
    validate_group_ids: bool,
    validate_nan_scores: bool,
    compact_present_groups: bool,
    operation: str,
    source: str,
    score_initial: float,
    score_kernel_factory: Any,
    tie_break: str,
) -> dict[str, object]:
    cuda, np = _import_numba_stack()
    _validate_numba_cuda_vector(group_ids, name="group_ids", dtype=np.int64)
    _validate_numba_cuda_vector(item_ids, name="item_ids", dtype=np.int64)
    _validate_numba_cuda_vector(scores, name="scores", dtype=np.float64)
    if not (tuple(group_ids.shape) == tuple(item_ids.shape) == tuple(scores.shape)):
        raise ValueError("group_ids, item_ids, and scores must have the same shape")
    if validate_nan_scores and int(scores.shape[0]) and bool(np.isnan(scores.copy_to_host()).any()):
        raise ValueError("grouped arg reductions reject NaN scores")
    group_count, block_size, row_count = _validate_group_run_shape(
        group_ids,
        group_count=group_count,
        block_size=block_size,
        validate_group_ids=validate_group_ids,
        cuda=cuda,
        np=np,
    )

    cuda.synchronize()
    started = perf_counter()
    dense_scores = cuda.device_array((group_count,), dtype=np.float64)
    dense_scores.copy_to_device(np.full((group_count,), float(score_initial), dtype=np.float64))
    dense_item_ids = cuda.device_array((group_count,), dtype=np.int64)
    dense_item_ids.copy_to_device(
        np.full((group_count,), np.iinfo(np.int64).max, dtype=np.int64)
    )
    counts = cuda.device_array((group_count,), dtype=np.int64)
    counts.copy_to_device(np.zeros((group_count,), dtype=np.int64))
    if row_count:
        grid = ((row_count + block_size - 1) // block_size,)
        _cached_numba_kernel(cuda, score_kernel_factory)[grid, block_size](
            group_ids,
            scores,
            dense_scores,
            counts,
            row_count,
            group_count,
        )
        _cached_numba_kernel(cuda, _numba_grouped_arg_item_i64_kernel)[grid, block_size](
            group_ids,
            item_ids,
            scores,
            dense_scores,
            dense_item_ids,
            row_count,
            group_count,
        )
    cuda.synchronize()

    if compact_present_groups:
        host_counts = counts.copy_to_host()
        present_host = np.nonzero(host_counts > 0)[0].astype(np.int64)
        missing_host = np.nonzero(host_counts == 0)[0].astype(np.int64)
        present_group_ids = cuda.to_device(present_host)
        missing_group_ids = cuda.to_device(missing_host)
        compact_item_ids = cuda.device_array((int(present_host.size),), dtype=np.int64)
        compact_scores = cuda.device_array((int(present_host.size),), dtype=np.float64)
        compact_count = int(present_host.size)
    else:
        present_group_ids = cuda.device_array((group_count,), dtype=np.int64)
        if group_count:
            iota_block = min(block_size, 256)
            iota_grid = ((group_count + iota_block - 1) // iota_block,)
            _cached_numba_kernel(cuda, _numba_iota_i64_kernel)[iota_grid, iota_block](present_group_ids, group_count)
        missing_group_ids = cuda.device_array((0,), dtype=np.int64)
        compact_item_ids = dense_item_ids
        compact_scores = dense_scores
        compact_count = group_count
    if compact_present_groups and compact_count:
        compact_block = min(block_size, 256)
        compact_grid = ((compact_count + compact_block - 1) // compact_block,)
        _cached_numba_kernel(cuda, _numba_gather_group_arg_outputs_kernel)[compact_grid, compact_block](
            present_group_ids,
            dense_item_ids,
            dense_scores,
            compact_item_ids,
            compact_scores,
            compact_count,
        )
    cuda.synchronize()
    elapsed = perf_counter() - started

    return _numba_run_result(
        operation=operation,
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
        source=source,
        extra_metadata={
            "tie_break": tie_break,
            "host_present_group_compaction_used": compact_present_groups,
            "nan_validation_host_sync_used": validate_nan_scores,
        },
    )


def _numba_run_result(
    *,
    operation: str,
    outputs: dict[str, object],
    elapsed: float,
    source: str,
    extra_metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    metadata = {} if extra_metadata is None else dict(extra_metadata)
    return {
        "contract_version": V2_5_PARTNER_CONTINUATION_VERSION,
        "operation": operation,
        "partner": "numba",
        "status": NUMBA_PARTNER_CONTINUATION_STATUS,
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
        **metadata,
    }


def _numba_segmented_count_i64_kernel(cuda: Any):
    @cuda.jit
    def kernel(group_ids, output, row_count, group_count):
        index = cuda.grid(1)
        if index < row_count:
            group = group_ids[index]
            if 0 <= group < group_count:
                cuda.atomic.add(output, group, 1)

    return kernel


def _numba_segmented_sum_f64_kernel(cuda: Any):
    @cuda.jit
    def kernel(group_ids, values, output, row_count, group_count):
        index = cuda.grid(1)
        if index < row_count:
            group = group_ids[index]
            if 0 <= group < group_count:
                cuda.atomic.add(output, group, values[index])

    return kernel


def _numba_segmented_min_f64_kernel(cuda: Any):
    @cuda.jit
    def kernel(group_ids, values, output, row_count, group_count):
        index = cuda.grid(1)
        if index < row_count:
            group = group_ids[index]
            if 0 <= group < group_count:
                cuda.atomic.min(output, group, values[index])

    return kernel


def _numba_segmented_max_f64_kernel(cuda: Any):
    @cuda.jit
    def kernel(group_ids, values, output, row_count, group_count):
        index = cuda.grid(1)
        if index < row_count:
            group = group_ids[index]
            if 0 <= group < group_count:
                cuda.atomic.max(output, group, values[index])

    return kernel


def _numba_grouped_argmin_score_f64_kernel(cuda: Any):
    @cuda.jit
    def kernel(group_ids, scores, dense_scores, counts, row_count, group_count):
        index = cuda.grid(1)
        if index < row_count:
            group = group_ids[index]
            if 0 <= group < group_count:
                cuda.atomic.add(counts, group, 1)
                cuda.atomic.min(dense_scores, group, scores[index])

    return kernel


def _numba_grouped_argmax_score_f64_kernel(cuda: Any):
    @cuda.jit
    def kernel(group_ids, scores, dense_scores, counts, row_count, group_count):
        index = cuda.grid(1)
        if index < row_count:
            group = group_ids[index]
            if 0 <= group < group_count:
                cuda.atomic.add(counts, group, 1)
                cuda.atomic.max(dense_scores, group, scores[index])

    return kernel


def _numba_grouped_arg_item_i64_kernel(cuda: Any):
    @cuda.jit
    def kernel(group_ids, item_ids, scores, dense_scores, dense_item_ids, row_count, group_count):
        index = cuda.grid(1)
        if index < row_count:
            group = group_ids[index]
            if 0 <= group < group_count and scores[index] == dense_scores[group]:
                cuda.atomic.min(dense_item_ids, group, item_ids[index])

    return kernel


def _numba_global_argmax_initial_block_reduce_u32_f64_kernel(cuda: Any):
    from numba import float64, int64, uint32

    @cuda.jit
    def kernel(item_ids, scores, out_item_ids, out_scores, out_row_indices, out_valid_counts, row_count, invalid_item_id):
        shared_scores = cuda.shared.array(256, dtype=float64)
        shared_item_ids = cuda.shared.array(256, dtype=uint32)
        shared_row_indices = cuda.shared.array(256, dtype=int64)
        shared_valid_counts = cuda.shared.array(256, dtype=int64)

        thread = cuda.threadIdx.x
        index = cuda.blockIdx.x * cuda.blockDim.x + thread
        best_score = -float("inf")
        best_item = invalid_item_id
        best_row = 9223372036854775807
        valid = 0
        if index < row_count:
            item = item_ids[index]
            score = scores[index]
            if item != invalid_item_id and score == score:
                best_score = score
                best_item = item
                best_row = index
                valid = 1
        shared_scores[thread] = best_score
        shared_item_ids[thread] = best_item
        shared_row_indices[thread] = best_row
        shared_valid_counts[thread] = valid
        cuda.syncthreads()

        stride = cuda.blockDim.x // 2
        while stride > 0:
            if thread < stride:
                other_valid = shared_valid_counts[thread + stride]
                current_valid = shared_valid_counts[thread]
                if other_valid > 0:
                    other_score = shared_scores[thread + stride]
                    other_item = shared_item_ids[thread + stride]
                    other_row = shared_row_indices[thread + stride]
                    current_score = shared_scores[thread]
                    current_item = shared_item_ids[thread]
                    current_row = shared_row_indices[thread]
                    if current_valid == 0 or other_score > current_score or (
                        other_score == current_score
                        and (
                            other_item < current_item
                            or (other_item == current_item and other_row < current_row)
                        )
                    ):
                        shared_scores[thread] = other_score
                        shared_item_ids[thread] = other_item
                        shared_row_indices[thread] = other_row
                    shared_valid_counts[thread] = current_valid + other_valid
            cuda.syncthreads()
            stride //= 2

        if thread == 0:
            block = cuda.blockIdx.x
            out_item_ids[block] = shared_item_ids[0]
            out_scores[block] = shared_scores[0]
            out_row_indices[block] = shared_row_indices[0]
            out_valid_counts[block] = shared_valid_counts[0]

    return kernel


def _numba_global_argmax_block_reduce_u32_f64_kernel(cuda: Any):
    from numba import float64, int64, uint32

    @cuda.jit
    def kernel(item_ids, scores, row_indices, valid_counts, out_item_ids, out_scores, out_row_indices, out_valid_counts, row_count, invalid_item_id):
        shared_scores = cuda.shared.array(256, dtype=float64)
        shared_item_ids = cuda.shared.array(256, dtype=uint32)
        shared_row_indices = cuda.shared.array(256, dtype=int64)
        shared_valid_counts = cuda.shared.array(256, dtype=int64)

        thread = cuda.threadIdx.x
        index = cuda.blockIdx.x * cuda.blockDim.x + thread
        best_score = -float("inf")
        best_item = invalid_item_id
        best_row = 9223372036854775807
        valid = 0
        if index < row_count and valid_counts[index] > 0:
            item = item_ids[index]
            score = scores[index]
            if item != invalid_item_id and score == score:
                best_score = score
                best_item = item
                best_row = row_indices[index]
                valid = valid_counts[index]
        shared_scores[thread] = best_score
        shared_item_ids[thread] = best_item
        shared_row_indices[thread] = best_row
        shared_valid_counts[thread] = valid
        cuda.syncthreads()

        stride = cuda.blockDim.x // 2
        while stride > 0:
            if thread < stride:
                other_valid = shared_valid_counts[thread + stride]
                current_valid = shared_valid_counts[thread]
                if other_valid > 0:
                    other_score = shared_scores[thread + stride]
                    other_item = shared_item_ids[thread + stride]
                    other_row = shared_row_indices[thread + stride]
                    current_score = shared_scores[thread]
                    current_item = shared_item_ids[thread]
                    current_row = shared_row_indices[thread]
                    if current_valid == 0 or other_score > current_score or (
                        other_score == current_score
                        and (
                            other_item < current_item
                            or (other_item == current_item and other_row < current_row)
                        )
                    ):
                        shared_scores[thread] = other_score
                        shared_item_ids[thread] = other_item
                        shared_row_indices[thread] = other_row
                    shared_valid_counts[thread] = current_valid + other_valid
            cuda.syncthreads()
            stride //= 2

        if thread == 0:
            block = cuda.blockIdx.x
            out_item_ids[block] = shared_item_ids[0]
            out_scores[block] = shared_scores[0]
            out_row_indices[block] = shared_row_indices[0]
            out_valid_counts[block] = shared_valid_counts[0]

    return kernel


def _numba_gather_group_arg_outputs_kernel(cuda: Any):
    @cuda.jit
    def kernel(present_group_ids, dense_item_ids, dense_scores, compact_item_ids, compact_scores, group_count):
        index = cuda.grid(1)
        if index < group_count:
            group = present_group_ids[index]
            compact_item_ids[index] = dense_item_ids[group]
            compact_scores[index] = dense_scores[group]

    return kernel


def _numba_pairwise_l2_sq_score_rows_2d_kernel(cuda: Any):
    @cuda.jit
    def kernel(
        source_x,
        source_y,
        target_ids,
        target_x,
        target_y,
        group_ids,
        item_ids,
        scores,
        source_count,
        target_count,
        row_count,
    ):
        index = cuda.grid(1)
        if index < row_count:
            source_index = index // target_count
            target_index = index - source_index * target_count
            dx = source_x[source_index] - target_x[target_index]
            dy = source_y[source_index] - target_y[target_index]
            group_ids[index] = source_index
            item_ids[index] = target_ids[target_index]
            scores[index] = dx * dx + dy * dy

    return kernel


def _numba_pairwise_l2_sq_block_nearest_rows_2d_kernel(cuda: Any):
    from numba import float64, int64

    @cuda.jit
    def kernel(
        source_x,
        source_y,
        target_ids,
        target_x,
        target_y,
        group_ids,
        item_ids,
        scores,
        target_count,
        target_tile_count,
    ):
        shared_scores = cuda.shared.array(256, dtype=float64)
        shared_item_ids = cuda.shared.array(256, dtype=int64)
        source_index = cuda.blockIdx.x
        tile_index = cuda.blockIdx.y
        thread = cuda.threadIdx.x
        target_index = tile_index * cuda.blockDim.x + thread
        best_score = float("inf")
        best_item = 9223372036854775807
        if target_index < target_count:
            dx = source_x[source_index] - target_x[target_index]
            dy = source_y[source_index] - target_y[target_index]
            best_score = dx * dx + dy * dy
            best_item = target_ids[target_index]
        shared_scores[thread] = best_score
        shared_item_ids[thread] = best_item
        cuda.syncthreads()

        stride = cuda.blockDim.x // 2
        while stride > 0:
            if thread < stride:
                other_score = shared_scores[thread + stride]
                other_item = shared_item_ids[thread + stride]
                current_score = shared_scores[thread]
                current_item = shared_item_ids[thread]
                if other_score < current_score or (
                    other_score == current_score and other_item < current_item
                ):
                    shared_scores[thread] = other_score
                    shared_item_ids[thread] = other_item
            cuda.syncthreads()
            stride //= 2

        if thread == 0:
            output_index = source_index * target_tile_count + tile_index
            group_ids[output_index] = source_index
            item_ids[output_index] = shared_item_ids[0]
            scores[output_index] = shared_scores[0]

    return kernel


def _numba_compact_count_blocks_i64_kernel(cuda: Any):
    @cuda.jit
    def kernel(mask, block_counts, row_count, block_size):
        block = cuda.blockIdx.x
        start = block * block_size
        end = start + block_size
        if end > row_count:
            end = row_count
        count = 0
        for index in range(start, end):
            if mask[index]:
                count += 1
        block_counts[block] = count

    return kernel


def _numba_iota_i64_kernel(cuda: Any):
    @cuda.jit
    def kernel(values, row_count):
        index = cuda.grid(1)
        if index < row_count:
            values[index] = index

    return kernel


def _numba_compact_scatter_i64_kernel(cuda: Any):
    @cuda.jit
    def kernel(values, mask, block_offsets, compact_values, original_indices, row_count, block_size):
        block = cuda.blockIdx.x
        thread = cuda.threadIdx.x
        index = block * block_size + thread
        if index >= row_count or not mask[index]:
            return
        start = block * block_size
        local_rank = 0
        for previous in range(start, index):
            if mask[previous]:
                local_rank += 1
        output_index = block_offsets[block] + local_rank
        compact_values[output_index] = values[index]
        original_indices[output_index] = index

    return kernel


def _numba_group_id_validation_kernel(cuda: Any):
    @cuda.jit
    def kernel(group_ids, error_flag, row_count, group_count):
        index = cuda.grid(1)
        if index < row_count:
            group = group_ids[index]
            if group < 0 or group >= group_count:
                cuda.atomic.max(error_flag, 0, 1)

    return kernel


def _import_numba_stack() -> tuple[Any, Any]:
    try:
        import numpy as np
        _activate_numba_cuda_redirector()
        from numba import cuda
    except ImportError as exc:
        raise ModuleNotFoundError(
            "Numba continuation execution requires numba, numpy, and CUDA; "
            "use an NVIDIA pod for validation"
        ) from exc
    if not cuda.is_available():
        raise RuntimeError("Numba continuation execution requires CUDA; use an NVIDIA pod")
    return cuda, np


def _activate_numba_cuda_redirector() -> None:
    """Activate numba-cuda's redirector when installed via --target/PYTHONPATH."""

    try:
        import _numba_cuda_redirector  # noqa: F401
    except ImportError:
        pass


def _as_numba_cuda_vector(array: Any, *, name: str, dtype: Any, cuda: Any, np: Any) -> Any:
    if not hasattr(array, "copy_to_host") and hasattr(array, "__cuda_array_interface__"):
        array = cuda.as_cuda_array(array)
    _validate_numba_cuda_vector(array, name=name, dtype=dtype)
    return array


def _validate_group_run_shape(
    group_ids: Any,
    *,
    group_count: int,
    block_size: int,
    validate_group_ids: bool,
    cuda: Any,
    np: Any,
) -> tuple[int, int, int]:
    group_count = int(group_count)
    if group_count < 0:
        raise ValueError("group_count must be non-negative")
    block_size = int(block_size)
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    row_count = int(group_ids.shape[0])
    if validate_group_ids and row_count:
        error_flag = cuda.to_device(np.zeros((1,), dtype=np.int32))
        grid = ((row_count + block_size - 1) // block_size,)
        _cached_numba_kernel(cuda, _numba_group_id_validation_kernel)[grid, block_size](
            group_ids,
            error_flag,
            row_count,
            group_count,
        )
        cuda.synchronize()
        if int(error_flag.copy_to_host()[0]) != 0:
            raise ValueError("group_ids must be in [0, group_count)")
    return group_count, block_size, row_count


def _validate_numba_cuda_vector(array: Any, *, name: str, dtype: Any) -> None:
    if not hasattr(array, "copy_to_host"):
        raise ValueError(f"{name} must be a Numba CUDA device array")
    if tuple(getattr(array, "shape", ())) == ():
        raise ValueError(f"{name} must be a 1-D array")
    if len(tuple(array.shape)) != 1:
        raise ValueError(f"{name} must be a 1-D array")
    if getattr(array, "dtype", None) != dtype:
        raise ValueError(f"{name} has wrong dtype")


def _cached_numba_kernel(cuda: Any, factory: Any) -> Any:
    factory_name = getattr(factory, "__name__", repr(factory))
    key = (id(cuda), str(factory_name))
    kernel = _NUMBA_KERNEL_CACHE.get(key)
    if kernel is None:
        kernel = factory(cuda)
        _NUMBA_KERNEL_CACHE[key] = kernel
    return kernel
