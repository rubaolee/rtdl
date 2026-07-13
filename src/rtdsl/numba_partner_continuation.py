from __future__ import annotations

from time import perf_counter
from typing import Any

from .partner_continuation_protocol import V2_5_PARTNER_CONTINUATION_VERSION
from .partner_continuation_protocol import V2_5_STATUS_PREVIEW_NOT_PROMOTED
from .partner_column_contracts import make_equal_contiguous_group_id_contract
from .partner_column_contracts import make_dense_zero_based_group_id_contract
from .partner_column_contracts import require_group_id_contract
from .partner_protocol import V2_4_PARTNER_PROTOCOL_VERSION
from .partner_protocol import v2_4_phase_timing_metadata


NUMBA_SEGMENTED_COUNT_I64_OPERATION = "segmented_count_i64"
NUMBA_LABEL_COUNT_AND_FLAG_COUNT_I64_OPERATION = "label_count_and_flag_count_i64"
NUMBA_SEGMENTED_SUM_F64_OPERATION = "segmented_sum_f64"
NUMBA_GROUPED_VECTOR_SUM_F64X2_OPERATION = "grouped_vector_sum_f64x2"
NUMBA_SEGMENTED_MIN_F64_OPERATION = "segmented_min_f64"
NUMBA_SEGMENTED_MAX_F64_OPERATION = "segmented_max_f64"
NUMBA_COMPACT_MASK_I64_OPERATION = "compact_mask_i64"
NUMBA_ADJACENT_MIDPOINT_CANDIDATES_I64X2_BY_KEY_OPERATION = (
    "adjacent_midpoint_candidates_i64x2_by_key"
)
NUMBA_CONSECUTIVE_DEDUPE_MASK_F64X2_OPERATION = "consecutive_dedupe_mask_f64x2"
NUMBA_RANGE_HAS_SORTED_VALUES_I64_OPERATION = "range_has_sorted_values_i64"
NUMBA_UINT32_EQUAL_MASK_OPERATION = "uint32_equal_mask"
NUMBA_GROUPED_ARGMIN_F64_OPERATION = "grouped_argmin_f64"
NUMBA_GROUPED_ARGMAX_F64_OPERATION = "grouped_argmax_f64"
NUMBA_GROUPED_TOPK_F64_OPERATION = "grouped_topk_f64"
NUMBA_GROUPED_TOPK_F64_MAX_K = 16
NUMBA_GLOBAL_ARGMAX_U32_F64_OPERATION = "global_argmax_u32_f64"
NUMBA_PAIRWISE_L2_SQ_SCORE_ROWS_2D_OPERATION = "pairwise_l2_sq_score_rows_2d"
NUMBA_PAIRWISE_L2_SQ_BLOCK_NEAREST_ROWS_2D_OPERATION = "pairwise_l2_sq_block_nearest_rows_2d"
NUMBA_SQRT_F64_OPERATION = "sqrt_f64"
NUMBA_PARTNER_CONTINUATION_STATUS = V2_5_STATUS_PREVIEW_NOT_PROMOTED
NUMBA_GROUP_ID_VALIDATION_MODE = "device_resident_error_flag"
NUMBA_GROUPED_VECTOR_SUM_OFFSETS_SESSION_VERSION = "rtdl.v2_9.numba_grouped_vector_sum_offsets_session.v1"
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


def describe_numba_label_count_and_flag_count_i64() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_LABEL_COUNT_AND_FLAG_COUNT_I64_OPERATION)
    descriptor["input_columns"] = ("labels:int64", "flags:uint32")
    descriptor["output_columns"] = ("label_counts:int64", "flag_true_count:int64", "negative_label_count:int64")
    descriptor["negative_label_policy"] = "counted_separately_not_used_as_label_index"
    descriptor["host_column_materialization_used"] = False
    return descriptor


def describe_numba_segmented_sum_f64() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_SEGMENTED_SUM_F64_OPERATION)
    descriptor["input_columns"] = ("group_ids:int64", "values:float64")
    descriptor["output_columns"] = ("sums:float64",)
    return descriptor


def describe_numba_grouped_vector_sum_f64x2() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_GROUPED_VECTOR_SUM_F64X2_OPERATION)
    descriptor["input_columns"] = ("group_ids:int64", "values_x:float64", "values_y:float64")
    descriptor["optional_input_columns"] = ("row_offsets:int64",)
    descriptor["output_columns"] = ("sum_x:float64", "sum_y:float64")
    descriptor["component_count"] = 2
    descriptor["componentwise_reduction"] = "independent_float64_sum_per_group"
    descriptor["presegmented_row_offsets_supported"] = True
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


def describe_numba_adjacent_midpoint_candidates_i64x2_by_key() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_ADJACENT_MIDPOINT_CANDIDATES_I64X2_BY_KEY_OPERATION)
    descriptor["input_columns"] = ("keys:int64", "values_x:int64", "values_y:int64")
    descriptor["output_columns"] = (
        "mid_x:int64",
        "mid_y:int64",
        "left_indices:int64",
        "valid_mask:bool",
    )
    descriptor["requires_sorted_by_key"] = True
    descriptor["same_key_pair_policy"] = "adjacent_rows_only"
    descriptor["midpoint_policy"] = "integer_truncating_divide_by_two"
    descriptor["app_specific_semantics_allowed"] = False
    descriptor["host_column_materialization_used"] = False
    return descriptor


def describe_numba_consecutive_dedupe_mask_f64x2() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_CONSECUTIVE_DEDUPE_MASK_F64X2_OPERATION)
    descriptor["input_columns"] = ("values_x:float64", "values_y:float64")
    descriptor["output_columns"] = ("keep_mask:bool",)
    descriptor["comparison_policy"] = "exact_float64_pair_equality_against_previous_row"
    descriptor["stable_input_order"] = True
    descriptor["app_specific_semantics_allowed"] = False
    descriptor["host_column_materialization_used"] = False
    return descriptor


def describe_numba_range_has_sorted_values_i64() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_RANGE_HAS_SORTED_VALUES_I64_OPERATION)
    descriptor["input_columns"] = ("range_starts:int64", "range_lengths:int64", "sorted_values:int64")
    descriptor["output_columns"] = ("has_value:bool",)
    descriptor["range_contract"] = "half_open_start_start_plus_length"
    descriptor["requires_sorted_values"] = True
    descriptor["app_specific_semantics_allowed"] = False
    descriptor["host_column_materialization_used"] = False
    return descriptor


def describe_numba_uint32_equal_mask() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_UINT32_EQUAL_MASK_OPERATION)
    descriptor["input_columns"] = ("values:uint32",)
    descriptor["scalar_inputs"] = ("target:uint32",)
    descriptor["output_columns"] = ("mask:bool",)
    descriptor["comparison_policy"] = "exact_uint32_equality_against_scalar_target"
    descriptor["app_specific_semantics_allowed"] = False
    descriptor["host_column_materialization_used"] = False
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


def describe_numba_grouped_topk_f64() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_GROUPED_TOPK_F64_OPERATION)
    descriptor["input_columns"] = ("group_ids:int64", "item_ids:int64", "scores:float64")
    descriptor["output_columns"] = (
        "group_ids:int64",
        "item_ids:int64",
        "scores:float64",
        "ranks:int64",
        "row_offsets:int64",
        "missing_group_ids:int64",
    )
    descriptor["tie_break"] = "lowest_score_then_lowest_item_id"
    descriptor["duplicate_item_policy"] = "lowest_score_per_group_item"
    descriptor["layout_precondition"] = "equal_contiguous_group_segments"
    descriptor["max_k"] = NUMBA_GROUPED_TOPK_F64_MAX_K
    descriptor["host_rank_materialization_used"] = False
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


def describe_numba_sqrt_f64() -> dict[str, object]:
    descriptor = _base_numba_descriptor(NUMBA_SQRT_F64_OPERATION)
    descriptor["input_columns"] = ("values:float64",)
    descriptor["output_columns"] = ("sqrt_values:float64",)
    descriptor["elementwise_transform"] = True
    descriptor["host_column_materialization_used"] = False
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
    group_ids = _as_numba_cuda_vector(group_ids, name="group_ids", dtype=np.int64, cuda=cuda, np=np)
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


def run_numba_label_count_and_flag_count_i64(
    labels: Any,
    flags: Any,
    *,
    label_count: int,
    block_size: int = 256,
    validate_labels: bool = False,
) -> dict[str, object]:
    """Count signed int64 labels and uint32 true flags in one Numba CUDA pass."""

    cuda, np = _import_numba_stack()
    labels = _as_numba_cuda_vector(labels, name="labels", dtype=np.int64, cuda=cuda, np=np)
    flags = _as_numba_cuda_vector(flags, name="flags", dtype=np.uint32, cuda=cuda, np=np)
    if tuple(labels.shape) != tuple(flags.shape):
        raise ValueError("labels and flags must have the same shape")
    label_count, block_size, row_count = _validate_label_count_run_shape(
        labels,
        label_count=label_count,
        block_size=block_size,
        validate_labels=validate_labels,
        cuda=cuda,
        np=np,
    )

    cuda.synchronize()
    started = perf_counter()
    label_counts = cuda.device_array((label_count,), dtype=np.int64)
    flag_true_count = cuda.device_array((1,), dtype=np.int64)
    negative_label_count = cuda.device_array((1,), dtype=np.int64)
    label_counts.copy_to_device(np.zeros((label_count,), dtype=np.int64))
    flag_true_count.copy_to_device(np.zeros((1,), dtype=np.int64))
    negative_label_count.copy_to_device(np.zeros((1,), dtype=np.int64))
    if row_count:
        grid = ((row_count + block_size - 1) // block_size,)
        _cached_numba_kernel(cuda, _numba_label_count_and_flag_count_i64_kernel)[grid, block_size](
            labels,
            flags,
            label_counts,
            flag_true_count,
            negative_label_count,
            row_count,
            label_count,
        )
    cuda.synchronize()
    elapsed = perf_counter() - started

    return _numba_run_result(
        operation=NUMBA_LABEL_COUNT_AND_FLAG_COUNT_I64_OPERATION,
        outputs={
            "label_counts": label_counts,
            "flag_true_count": flag_true_count,
            "negative_label_count": negative_label_count,
        },
        elapsed=elapsed,
        source="run_numba_label_count_and_flag_count_i64",
        extra_metadata={
            "label_count": label_count,
            "row_count": row_count,
            "label_validation_host_sync_used": validate_labels,
            "host_column_materialization_used": False,
        },
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


def run_numba_grouped_vector_sum_f64x2(
    group_ids: Any,
    values_x: Any,
    values_y: Any,
    *,
    group_count: int,
    block_size: int = 256,
    validate_group_ids: bool = True,
) -> dict[str, object]:
    """Run grouped two-component vector sum over Numba CUDA arrays."""

    cuda, np = _import_numba_stack()
    group_ids = _as_numba_cuda_vector(group_ids, name="group_ids", dtype=np.int64, cuda=cuda, np=np)
    values_x = _as_numba_cuda_vector(values_x, name="values_x", dtype=np.float64, cuda=cuda, np=np)
    values_y = _as_numba_cuda_vector(values_y, name="values_y", dtype=np.float64, cuda=cuda, np=np)
    if tuple(group_ids.shape) != tuple(values_x.shape) or tuple(group_ids.shape) != tuple(values_y.shape):
        raise ValueError("group_ids, values_x, and values_y must have the same shape")
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
    sum_x = cuda.device_array((group_count,), dtype=np.float64)
    sum_y = cuda.device_array((group_count,), dtype=np.float64)
    zeros = np.zeros((group_count,), dtype=np.float64)
    sum_x.copy_to_device(zeros)
    sum_y.copy_to_device(zeros)
    if row_count:
        grid = ((row_count + block_size - 1) // block_size,)
        _cached_numba_kernel(cuda, _numba_grouped_vector_sum_f64x2_kernel)[grid, block_size](
            group_ids,
            values_x,
            values_y,
            sum_x,
            sum_y,
            row_count,
            group_count,
        )
    cuda.synchronize()
    elapsed = perf_counter() - started

    return _numba_run_result(
        operation=NUMBA_GROUPED_VECTOR_SUM_F64X2_OPERATION,
        outputs={"sum_x": sum_x, "sum_y": sum_y},
        elapsed=elapsed,
        source="run_numba_grouped_vector_sum_f64x2",
        extra_metadata={
            "group_count": group_count,
            "row_count": row_count,
            "component_count": 2,
            "componentwise_reduction": "independent_float64_sum_per_group",
        },
    )


def run_numba_grouped_vector_sum_f64x2_by_offsets(
    row_offsets: Any,
    values_x: Any,
    values_y: Any,
    *,
    block_size: int = 256,
    validate_row_offsets: bool = True,
) -> dict[str, object]:
    """Run grouped vector sum for presegmented rows over Numba CUDA arrays."""

    cuda, np = _import_numba_stack()
    row_offsets = _as_numba_cuda_vector(row_offsets, name="row_offsets", dtype=np.int64, cuda=cuda, np=np)
    values_x = _as_numba_cuda_vector(values_x, name="values_x", dtype=np.float64, cuda=cuda, np=np)
    values_y = _as_numba_cuda_vector(values_y, name="values_y", dtype=np.float64, cuda=cuda, np=np)
    group_count, block_size, row_count = _validate_numba_grouped_vector_offsets_shape(
        row_offsets,
        values_x,
        values_y,
        block_size=block_size,
        validate_row_offsets=validate_row_offsets,
        cuda=cuda,
        np=np,
    )

    cuda.synchronize()
    started = perf_counter()
    sum_x = cuda.device_array((group_count,), dtype=np.float64)
    sum_y = cuda.device_array((group_count,), dtype=np.float64)
    if group_count:
        grid = ((group_count + block_size - 1) // block_size,)
        _cached_numba_kernel(cuda, _numba_grouped_vector_sum_f64x2_offsets_kernel)[grid, block_size](
            row_offsets,
            values_x,
            values_y,
            sum_x,
            sum_y,
            group_count,
        )
    cuda.synchronize()
    elapsed = perf_counter() - started

    return _numba_run_result(
        operation=NUMBA_GROUPED_VECTOR_SUM_F64X2_OPERATION,
        outputs={"sum_x": sum_x, "sum_y": sum_y},
        elapsed=elapsed,
        source="run_numba_grouped_vector_sum_f64x2_by_offsets",
        extra_metadata={
            "group_count": group_count,
            "row_count": row_count,
            "component_count": 2,
            "componentwise_reduction": "independent_float64_sum_per_group_by_offsets",
            "presegmented_row_offsets": True,
            "adapter_kernel": "numba_grouped_vector_sum_offsets_f64x2_kernel",
            "program_count": (group_count + block_size - 1) // block_size if group_count else 0,
            "threads_per_block": block_size,
            "global_atomic_add_used": False,
            "row_offset_validation_host_sync_used": validate_row_offsets,
        },
    )


def prepare_numba_grouped_vector_sum_f64x2_offsets_session(
    row_offsets: Any,
    values_x: Any,
    values_y: Any,
    *,
    block_size: int = 256,
    validate_row_offsets: bool = True,
) -> dict[str, object]:
    """Prepare reusable output buffers for presegmented grouped vector sums."""

    cuda, np = _import_numba_stack()
    row_offsets = _as_numba_cuda_vector(row_offsets, name="row_offsets", dtype=np.int64, cuda=cuda, np=np)
    values_x = _as_numba_cuda_vector(values_x, name="values_x", dtype=np.float64, cuda=cuda, np=np)
    values_y = _as_numba_cuda_vector(values_y, name="values_y", dtype=np.float64, cuda=cuda, np=np)
    group_count, block_size, row_count = _validate_numba_grouped_vector_offsets_shape(
        row_offsets,
        values_x,
        values_y,
        block_size=block_size,
        validate_row_offsets=validate_row_offsets,
        cuda=cuda,
        np=np,
    )
    sum_x = cuda.device_array((group_count,), dtype=np.float64)
    sum_y = cuda.device_array((group_count,), dtype=np.float64)
    return {
        "session_version": NUMBA_GROUPED_VECTOR_SUM_OFFSETS_SESSION_VERSION,
        "contract_version": V2_5_PARTNER_CONTINUATION_VERSION,
        "operation": NUMBA_GROUPED_VECTOR_SUM_F64X2_OPERATION,
        "partner": "numba",
        "status": NUMBA_PARTNER_CONTINUATION_STATUS,
        "row_offsets": row_offsets,
        "values_x": values_x,
        "values_y": values_y,
        "outputs": {"sum_x": sum_x, "sum_y": sum_y},
        "group_count": group_count,
        "row_count": row_count,
        "block_size": block_size,
        "presegmented_row_offsets": True,
        "row_offset_validation_performed_at_prepare": bool(validate_row_offsets),
        "output_columns_reused": True,
        "global_atomic_add_used": False,
        "raw_kernel_required": False,
        "replaces_rt_traversal": False,
        "promoted_performance_path": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "release_authorized": False,
    }


def run_numba_prepared_grouped_vector_sum_f64x2_by_offsets(
    session: dict[str, object],
) -> dict[str, object]:
    """Replay a prepared presegmented grouped vector-sum session."""

    if session.get("session_version") != NUMBA_GROUPED_VECTOR_SUM_OFFSETS_SESSION_VERSION:
        raise ValueError("unexpected Numba grouped-vector offset session version")
    cuda, _np = _import_numba_stack()
    row_offsets = session["row_offsets"]
    values_x = session["values_x"]
    values_y = session["values_y"]
    outputs = session["outputs"]
    sum_x = outputs["sum_x"]
    sum_y = outputs["sum_y"]
    group_count = int(session["group_count"])
    block_size = int(session["block_size"])
    cuda.synchronize()
    started = perf_counter()
    if group_count:
        grid = ((group_count + block_size - 1) // block_size,)
        _cached_numba_kernel(cuda, _numba_grouped_vector_sum_f64x2_offsets_kernel)[grid, block_size](
            row_offsets,
            values_x,
            values_y,
            sum_x,
            sum_y,
            group_count,
        )
    cuda.synchronize()
    elapsed = perf_counter() - started
    return _numba_run_result(
        operation=NUMBA_GROUPED_VECTOR_SUM_F64X2_OPERATION,
        outputs={"sum_x": sum_x, "sum_y": sum_y},
        elapsed=elapsed,
        source="run_numba_prepared_grouped_vector_sum_f64x2_by_offsets",
        extra_metadata={
            "session_version": NUMBA_GROUPED_VECTOR_SUM_OFFSETS_SESSION_VERSION,
            "group_count": group_count,
            "row_count": int(session["row_count"]),
            "component_count": 2,
            "componentwise_reduction": "independent_float64_sum_per_group_by_offsets",
            "presegmented_row_offsets": True,
            "adapter_kernel": "numba_grouped_vector_sum_offsets_f64x2_kernel",
            "program_count": (group_count + block_size - 1) // block_size if group_count else 0,
            "threads_per_block": block_size,
            "global_atomic_add_used": False,
            "prepared_session_reused": True,
            "output_columns_reused": True,
            "row_offset_validation_performed_at_prepare": bool(
                session["row_offset_validation_performed_at_prepare"]
            ),
            "row_offset_validation_host_sync_used": False,
        },
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


def run_numba_grouped_topk_f64(
    group_ids: Any,
    item_ids: Any,
    scores: Any,
    *,
    group_count: int,
    k: int,
    rows_per_group: int | None = None,
    block_size: int = 128,
    validate_group_ids: bool = True,
    validate_nan_scores: bool = True,
) -> dict[str, object]:
    """Run grouped top-k over equal contiguous score-row segments.

    This is a generic ranked-summary continuation for score rows already laid
    out as one contiguous segment per dense group. The v2.11 point top-k
    adapter's pairwise score-row producer emits exactly this layout.
    """

    cuda, np = _import_numba_stack()
    _validate_numba_cuda_vector(group_ids, name="group_ids", dtype=np.int64)
    _validate_numba_cuda_vector(item_ids, name="item_ids", dtype=np.int64)
    _validate_numba_cuda_vector(scores, name="scores", dtype=np.float64)
    if not (tuple(group_ids.shape) == tuple(item_ids.shape) == tuple(scores.shape)):
        raise ValueError("group_ids, item_ids, and scores must have the same shape")
    if validate_nan_scores and int(scores.shape[0]) and bool(np.isnan(scores.copy_to_host()).any()):
        raise ValueError("grouped top-k rejects NaN scores")
    group_count = int(group_count)
    k = int(k)
    block_size = int(block_size)
    row_count = int(group_ids.shape[0])
    if group_count < 0:
        raise ValueError("group_count must be non-negative")
    if group_count == 0:
        raise ValueError("grouped top-k requires at least one group")
    if k <= 0:
        raise ValueError("k must be positive")
    if k > NUMBA_GROUPED_TOPK_F64_MAX_K:
        raise ValueError(f"k must be <= {NUMBA_GROUPED_TOPK_F64_MAX_K} for numba grouped_topk_f64")
    if block_size not in {32, 64, 128, 256}:
        raise ValueError("block_size must be one of 32, 64, 128, or 256")
    if rows_per_group is None:
        if row_count % group_count != 0:
            raise ValueError("row_count must be divisible by group_count when rows_per_group is omitted")
        rows_per_group = row_count // group_count
    rows_per_group = int(rows_per_group)
    if rows_per_group < k:
        raise ValueError("rows_per_group must be >= k")
    if rows_per_group * group_count != row_count:
        raise ValueError("rows_per_group * group_count must equal row_count")
    group_contract_metadata = require_group_id_contract(
        make_equal_contiguous_group_id_contract(
            operation=NUMBA_GROUPED_TOPK_F64_OPERATION,
            group_count=group_count,
            row_count=row_count,
            rows_per_group=rows_per_group,
        )
    )
    if validate_group_ids:
        group_count, block_size, _ = _validate_group_run_shape(
            group_ids,
            group_count=group_count,
            block_size=block_size,
            validate_group_ids=True,
            cuda=cuda,
            np=np,
        )

    cuda.synchronize()
    started = perf_counter()
    output_count = group_count * k
    out_group_ids = cuda.device_array((output_count,), dtype=np.int64)
    out_item_ids = cuda.device_array((output_count,), dtype=np.int64)
    out_scores = cuda.device_array((output_count,), dtype=np.float64)
    out_ranks = cuda.device_array((output_count,), dtype=np.int64)
    row_offsets = cuda.device_array((group_count + 1,), dtype=np.int64)
    counts = cuda.device_array((group_count,), dtype=np.int64)
    missing_group_ids = cuda.device_array((0,), dtype=np.int64)
    error_flag = cuda.device_array((1,), dtype=np.int64)
    error_flag.copy_to_device(np.zeros((1,), dtype=np.int64))
    _cached_numba_kernel(cuda, _numba_grouped_topk_f64_equal_segments_kernel)[
        (group_count,), block_size
    ](
        group_ids,
        item_ids,
        scores,
        out_group_ids,
        out_item_ids,
        out_scores,
        out_ranks,
        row_offsets,
        counts,
        error_flag,
        group_count,
        rows_per_group,
        k,
    )
    cuda.synchronize()
    error_code = int(error_flag.copy_to_host()[0])
    if error_code:
        raise ValueError(
            "grouped_topk_f64 equal-segment validation failed; "
            f"error_code={error_code}; expected contiguous dense group segments and finite scores"
        )
    elapsed = perf_counter() - started

    return _numba_run_result(
        operation=NUMBA_GROUPED_TOPK_F64_OPERATION,
        outputs={
            "group_ids": out_group_ids,
            "item_ids": out_item_ids,
            "scores": out_scores,
            "ranks": out_ranks,
            "row_offsets": row_offsets,
            "missing_group_ids": missing_group_ids,
            "dense_item_ids": out_item_ids,
            "dense_scores": out_scores,
            "counts": counts,
        },
        elapsed=elapsed,
        source="run_numba_grouped_topk_f64",
        extra_metadata={
            "tie_break": "lowest_score_then_lowest_item_id",
            "duplicate_item_policy": "lowest_score_per_group_item",
            "layout_precondition": "equal_contiguous_group_segments",
            "rows_per_group": rows_per_group,
            "k": k,
            "max_k": NUMBA_GROUPED_TOPK_F64_MAX_K,
            "host_rank_materialization_used": False,
            "host_score_row_materialization_used": False,
            "nan_validation_host_sync_used": validate_nan_scores,
            "device_validation_error_flag_used": True,
            **group_contract_metadata,
        },
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


def run_numba_sqrt_f64(
    values: Any,
    *,
    block_size: int = 256,
) -> dict[str, object]:
    """Run a generic elementwise sqrt over a float64 CUDA column."""

    cuda, np = _import_numba_stack()
    _validate_numba_cuda_vector(values, name="values", dtype=np.float64)
    row_count = int(values.shape[0])
    block_size = int(block_size)
    if block_size <= 0:
        raise ValueError("block_size must be positive")

    cuda.synchronize()
    started = perf_counter()
    output = cuda.device_array((row_count,), dtype=np.float64)
    if row_count:
        grid = ((row_count + block_size - 1) // block_size,)
        _cached_numba_kernel(cuda, _numba_sqrt_f64_kernel)[grid, block_size](values, output, row_count)
    cuda.synchronize()
    elapsed = perf_counter() - started

    return _numba_run_result(
        operation=NUMBA_SQRT_F64_OPERATION,
        outputs={"sqrt_values": output},
        elapsed=elapsed,
        source="run_numba_sqrt_f64",
        extra_metadata={
            "row_count": row_count,
            "elementwise_transform": True,
            "host_column_materialization_used": False,
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


def run_numba_adjacent_midpoint_candidates_i64x2_by_key(
    keys: Any,
    values_x: Any,
    values_y: Any,
    *,
    block_size: int = 256,
) -> dict[str, object]:
    """Emit same-key adjacent integer midpoint candidates over CUDA columns.

    This is a generic Layer-2 numeric continuation. It assumes callers have
    already sorted rows by key and any app-specific tie keys. The output keeps a
    candidate row for every adjacent pair position and uses ``valid_mask`` to
    mark positions where ``keys[i] == keys[i + 1]``.
    """

    cuda, np = _import_numba_stack()
    keys = _as_numba_cuda_vector(keys, name="keys", dtype=np.int64, cuda=cuda, np=np)
    values_x = _as_numba_cuda_vector(values_x, name="values_x", dtype=np.int64, cuda=cuda, np=np)
    values_y = _as_numba_cuda_vector(values_y, name="values_y", dtype=np.int64, cuda=cuda, np=np)
    if not (tuple(keys.shape) == tuple(values_x.shape) == tuple(values_y.shape)):
        raise ValueError("keys, values_x, and values_y must have the same shape")
    block_size = int(block_size)
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    row_count = int(keys.shape[0])
    candidate_count = max(0, row_count - 1)

    cuda.synchronize()
    started = perf_counter()
    mid_x = cuda.device_array((candidate_count,), dtype=np.int64)
    mid_y = cuda.device_array((candidate_count,), dtype=np.int64)
    left_indices = cuda.device_array((candidate_count,), dtype=np.int64)
    valid_mask = cuda.device_array((candidate_count,), dtype=np.bool_)
    if candidate_count:
        grid = ((candidate_count + block_size - 1) // block_size,)
        _cached_numba_kernel(cuda, _numba_adjacent_midpoint_candidates_i64x2_by_key_kernel)[
            grid,
            block_size,
        ](
            keys,
            values_x,
            values_y,
            mid_x,
            mid_y,
            left_indices,
            valid_mask,
            candidate_count,
        )
    cuda.synchronize()
    elapsed = perf_counter() - started
    return _numba_run_result(
        operation=NUMBA_ADJACENT_MIDPOINT_CANDIDATES_I64X2_BY_KEY_OPERATION,
        outputs={
            "mid_x": mid_x,
            "mid_y": mid_y,
            "left_indices": left_indices,
            "valid_mask": valid_mask,
        },
        elapsed=elapsed,
        source="run_numba_adjacent_midpoint_candidates_i64x2_by_key",
        extra_metadata={
            "row_count": row_count,
            "candidate_count": candidate_count,
            "requires_sorted_by_key": True,
            "same_key_pair_policy": "adjacent_rows_only",
            "midpoint_policy": "integer_truncating_divide_by_two",
            "host_column_materialization_used": False,
            "app_specific_semantics_allowed": False,
        },
    )


def run_numba_consecutive_dedupe_mask_f64x2(
    values_x: Any,
    values_y: Any,
    *,
    block_size: int = 256,
) -> dict[str, object]:
    """Mark exact consecutive duplicate float64 x/y rows over CUDA columns."""

    cuda, np = _import_numba_stack()
    values_x = _as_numba_cuda_vector(values_x, name="values_x", dtype=np.float64, cuda=cuda, np=np)
    values_y = _as_numba_cuda_vector(values_y, name="values_y", dtype=np.float64, cuda=cuda, np=np)
    if tuple(values_x.shape) != tuple(values_y.shape):
        raise ValueError("values_x and values_y must have the same shape")
    block_size = int(block_size)
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    row_count = int(values_x.shape[0])

    cuda.synchronize()
    started = perf_counter()
    keep_mask = cuda.device_array((row_count,), dtype=np.bool_)
    if row_count:
        grid = ((row_count + block_size - 1) // block_size,)
        _cached_numba_kernel(cuda, _numba_consecutive_dedupe_mask_f64x2_kernel)[grid, block_size](
            values_x,
            values_y,
            keep_mask,
            row_count,
        )
    cuda.synchronize()
    elapsed = perf_counter() - started
    return _numba_run_result(
        operation=NUMBA_CONSECUTIVE_DEDUPE_MASK_F64X2_OPERATION,
        outputs={"keep_mask": keep_mask},
        elapsed=elapsed,
        source="run_numba_consecutive_dedupe_mask_f64x2",
        extra_metadata={
            "row_count": row_count,
            "comparison_policy": "exact_float64_pair_equality_against_previous_row",
            "stable_input_order": True,
            "host_column_materialization_used": False,
            "app_specific_semantics_allowed": False,
        },
    )


def run_numba_range_has_sorted_values_i64(
    range_starts: Any,
    range_lengths: Any,
    sorted_values: Any,
    *,
    block_size: int = 256,
    validate_inputs: bool = True,
) -> dict[str, object]:
    """Report whether sorted int64 values intersect each half-open range."""

    cuda, np = _import_numba_stack()
    range_starts = _as_numba_cuda_vector(
        range_starts,
        name="range_starts",
        dtype=np.int64,
        cuda=cuda,
        np=np,
    )
    range_lengths = _as_numba_cuda_vector(
        range_lengths,
        name="range_lengths",
        dtype=np.int64,
        cuda=cuda,
        np=np,
    )
    sorted_values = _as_numba_cuda_vector(
        sorted_values,
        name="sorted_values",
        dtype=np.int64,
        cuda=cuda,
        np=np,
    )
    if tuple(range_starts.shape) != tuple(range_lengths.shape):
        raise ValueError("range_starts and range_lengths must have the same shape")
    if validate_inputs:
        host_lengths = range_lengths.copy_to_host()
        if bool((host_lengths < 0).any()):
            raise ValueError("range_lengths must be non-negative")
        host_values = sorted_values.copy_to_host()
        if int(host_values.size) > 1 and bool((host_values[1:] < host_values[:-1]).any()):
            raise ValueError("sorted_values must be sorted in nondecreasing order")
    block_size = int(block_size)
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    range_count = int(range_starts.shape[0])
    value_count = int(sorted_values.shape[0])

    cuda.synchronize()
    started = perf_counter()
    has_value = cuda.device_array((range_count,), dtype=np.bool_)
    if range_count:
        grid = ((range_count + block_size - 1) // block_size,)
        _cached_numba_kernel(cuda, _numba_range_has_sorted_values_i64_kernel)[grid, block_size](
            range_starts,
            range_lengths,
            sorted_values,
            has_value,
            range_count,
            value_count,
        )
    cuda.synchronize()
    elapsed = perf_counter() - started
    return _numba_run_result(
        operation=NUMBA_RANGE_HAS_SORTED_VALUES_I64_OPERATION,
        outputs={"has_value": has_value},
        elapsed=elapsed,
        source="run_numba_range_has_sorted_values_i64",
        extra_metadata={
            "range_count": range_count,
            "value_count": value_count,
            "range_contract": "half_open_start_start_plus_length",
            "requires_sorted_values": True,
            "input_validation_host_sync_used": bool(validate_inputs),
            "host_column_materialization_used": False,
            "app_specific_semantics_allowed": False,
        },
    )


def run_numba_uint32_equal_mask(
    values: Any,
    *,
    target: int,
    block_size: int = 256,
) -> dict[str, object]:
    """Mark uint32 device rows equal to a scalar target."""

    cuda, np = _import_numba_stack()
    values = _as_numba_cuda_vector(values, name="values", dtype=np.uint32, cuda=cuda, np=np)
    target = int(target)
    if target < 0 or target > 0xFFFFFFFF:
        raise ValueError("target must fit uint32")
    block_size = int(block_size)
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    row_count = int(values.shape[0])

    cuda.synchronize()
    started = perf_counter()
    mask = cuda.device_array((row_count,), dtype=np.bool_)
    if row_count:
        grid = ((row_count + block_size - 1) // block_size,)
        _cached_numba_kernel(cuda, _numba_uint32_equal_mask_kernel)[grid, block_size](
            values,
            target,
            mask,
            row_count,
        )
    cuda.synchronize()
    elapsed = perf_counter() - started
    return _numba_run_result(
        operation=NUMBA_UINT32_EQUAL_MASK_OPERATION,
        outputs={"mask": mask},
        elapsed=elapsed,
        source="run_numba_uint32_equal_mask",
        extra_metadata={
            "row_count": row_count,
            "target": target,
            "comparison_policy": "exact_uint32_equality_against_scalar_target",
            "host_column_materialization_used": False,
            "app_specific_semantics_allowed": False,
        },
    )


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
    group_contract_metadata = require_group_id_contract(
        make_dense_zero_based_group_id_contract(
            operation=operation,
            group_count=group_count,
            row_count=row_count,
            validation_mode=(
                "device_resident_error_flag"
                if validate_group_ids
                else "caller_declared_unchecked"
            ),
        )
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
            **group_contract_metadata,
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


def _numba_label_count_and_flag_count_i64_kernel(cuda: Any):
    @cuda.jit
    def kernel(labels, flags, label_counts, flag_true_count, negative_label_count, row_count, label_count):
        index = cuda.grid(1)
        if index < row_count:
            label = labels[index]
            if 0 <= label < label_count:
                cuda.atomic.add(label_counts, label, 1)
            elif label < 0:
                cuda.atomic.add(negative_label_count, 0, 1)
            if flags[index] != 0:
                cuda.atomic.add(flag_true_count, 0, 1)

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


def _numba_grouped_vector_sum_f64x2_kernel(cuda: Any):
    @cuda.jit
    def kernel(group_ids, values_x, values_y, output_x, output_y, row_count, group_count):
        index = cuda.grid(1)
        if index < row_count:
            group = group_ids[index]
            if 0 <= group < group_count:
                cuda.atomic.add(output_x, group, values_x[index])
                cuda.atomic.add(output_y, group, values_y[index])

    return kernel


def _numba_grouped_vector_sum_f64x2_offsets_kernel(cuda: Any):
    @cuda.jit
    def kernel(row_offsets, values_x, values_y, output_x, output_y, group_count):
        group = cuda.grid(1)
        local_x = 0.0
        local_y = 0.0
        if group < group_count:
            start = row_offsets[group]
            end = row_offsets[group + 1]
            index = start
            while index < end:
                local_x += values_x[index]
                local_y += values_y[index]
                index += 1
            output_x[group] = local_x
            output_y[group] = local_y

    return kernel


def _validate_numba_grouped_vector_offsets_shape(
    row_offsets: Any,
    values_x: Any,
    values_y: Any,
    *,
    block_size: int,
    validate_row_offsets: bool,
    cuda: Any,
    np: Any,
) -> tuple[int, int, int]:
    if tuple(values_x.shape) != tuple(values_y.shape):
        raise ValueError("values_x and values_y must have the same shape")
    group_count = int(row_offsets.shape[0]) - 1
    row_count = int(values_x.shape[0])
    if group_count < 0:
        raise ValueError("row_offsets must contain at least one element")
    block_size = int(block_size)
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    if validate_row_offsets and int(row_offsets.shape[0]):
        host_offsets = row_offsets.copy_to_host()
        if int(host_offsets[0]) != 0 or int(host_offsets[-1]) != row_count:
            raise ValueError("row_offsets must start at 0 and end at the row count")
        if bool(np.any(host_offsets[1:] < host_offsets[:-1])):
            raise ValueError("row_offsets must be monotonically nondecreasing")
    return group_count, block_size, row_count


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


def _numba_grouped_topk_f64_equal_segments_kernel(cuda: Any):
    from numba import float64, int64

    @cuda.jit
    def kernel(
        group_ids,
        item_ids,
        scores,
        out_group_ids,
        out_item_ids,
        out_scores,
        out_ranks,
        row_offsets,
        counts,
        error_flag,
        group_count,
        rows_per_group,
        k,
    ):
        shared_scores = cuda.shared.array(256, dtype=float64)
        shared_items = cuda.shared.array(256, dtype=int64)

        group = cuda.blockIdx.x
        thread = cuda.threadIdx.x
        block_size = cuda.blockDim.x
        start = group * rows_per_group
        out_start = group * k
        max_i64 = 9223372036854775807

        if group < group_count and thread == 0:
            row_offsets[group] = out_start
            if group == group_count - 1:
                row_offsets[group_count] = out_start + k
            counts[group] = k
        cuda.syncthreads()

        for rank_index in range(k):
            best_score = float("inf")
            best_item = max_i64
            local = thread
            while local < rows_per_group:
                row = start + local
                if group_ids[row] != group:
                    cuda.atomic.max(error_flag, 0, 1)
                score = scores[row]
                item = item_ids[row]
                if score != score:
                    cuda.atomic.max(error_flag, 0, 2)
                already_selected = False
                prior = 0
                while prior < rank_index:
                    if out_item_ids[out_start + prior] == item:
                        already_selected = True
                    prior += 1
                if not already_selected and score == score:
                    if score < best_score or (score == best_score and item < best_item):
                        best_score = score
                        best_item = item
                local += block_size
            shared_scores[thread] = best_score
            shared_items[thread] = best_item
            cuda.syncthreads()

            stride = block_size // 2
            while stride > 0:
                if thread < stride:
                    other_score = shared_scores[thread + stride]
                    other_item = shared_items[thread + stride]
                    current_score = shared_scores[thread]
                    current_item = shared_items[thread]
                    if other_score < current_score or (other_score == current_score and other_item < current_item):
                        shared_scores[thread] = other_score
                        shared_items[thread] = other_item
                cuda.syncthreads()
                stride //= 2

            if thread == 0:
                if shared_items[0] == max_i64:
                    cuda.atomic.max(error_flag, 0, 3)
                out_group_ids[out_start + rank_index] = group
                out_item_ids[out_start + rank_index] = shared_items[0]
                out_scores[out_start + rank_index] = shared_scores[0]
                out_ranks[out_start + rank_index] = rank_index + 1
            cuda.syncthreads()

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


def _numba_sqrt_f64_kernel(cuda: Any):
    import math

    @cuda.jit
    def kernel(values, output, row_count):
        index = cuda.grid(1)
        if index < row_count:
            output[index] = math.sqrt(values[index])

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


def _numba_adjacent_midpoint_candidates_i64x2_by_key_kernel(cuda: Any):
    @cuda.jit(device=True)
    def trunc_div2(value):
        if value >= 0:
            return value // 2
        return -((-value) // 2)

    @cuda.jit
    def kernel(keys, values_x, values_y, mid_x, mid_y, left_indices, valid_mask, candidate_count):
        index = cuda.grid(1)
        if index < candidate_count:
            left_indices[index] = index
            same_key = keys[index] == keys[index + 1]
            valid_mask[index] = same_key
            if same_key:
                mid_x[index] = trunc_div2(int(values_x[index]) + int(values_x[index + 1]))
                mid_y[index] = trunc_div2(int(values_y[index]) + int(values_y[index + 1]))
            else:
                mid_x[index] = 0
                mid_y[index] = 0

    return kernel


def _numba_consecutive_dedupe_mask_f64x2_kernel(cuda: Any):
    @cuda.jit
    def kernel(values_x, values_y, keep_mask, row_count):
        index = cuda.grid(1)
        if index < row_count:
            if index == 0:
                keep_mask[index] = True
            else:
                keep_mask[index] = (
                    values_x[index] != values_x[index - 1]
                    or values_y[index] != values_y[index - 1]
                )

    return kernel


def _numba_range_has_sorted_values_i64_kernel(cuda: Any):
    @cuda.jit
    def kernel(range_starts, range_lengths, sorted_values, has_value, range_count, value_count):
        index = cuda.grid(1)
        if index >= range_count:
            return
        start = range_starts[index]
        stop = start + range_lengths[index]
        lo = 0
        hi = value_count
        while lo < hi:
            mid = (lo + hi) // 2
            if sorted_values[mid] < start:
                lo = mid + 1
            else:
                hi = mid
        has_value[index] = lo < value_count and sorted_values[lo] < stop

    return kernel


def _numba_uint32_equal_mask_kernel(cuda: Any):
    @cuda.jit
    def kernel(values, target, mask, row_count):
        index = cuda.grid(1)
        if index < row_count:
            mask[index] = values[index] == target

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


def _numba_label_validation_kernel(cuda: Any):
    @cuda.jit
    def kernel(labels, error_flag, row_count, label_count):
        index = cuda.grid(1)
        if index < row_count:
            label = labels[index]
            if label >= label_count:
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


def _validate_label_count_run_shape(
    labels: Any,
    *,
    label_count: int,
    block_size: int,
    validate_labels: bool,
    cuda: Any,
    np: Any,
) -> tuple[int, int, int]:
    label_count = int(label_count)
    if label_count < 0:
        raise ValueError("label_count must be non-negative")
    block_size = int(block_size)
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    row_count = int(labels.shape[0])
    if validate_labels and row_count:
        error_flag = cuda.to_device(np.zeros((1,), dtype=np.int32))
        grid = ((row_count + block_size - 1) // block_size,)
        _cached_numba_kernel(cuda, _numba_label_validation_kernel)[grid, block_size](
            labels,
            error_flag,
            row_count,
            label_count,
        )
        cuda.synchronize()
        if int(error_flag.copy_to_host()[0]) != 0:
            raise ValueError("labels must be negative or in [0, label_count)")
    return label_count, block_size, row_count


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
