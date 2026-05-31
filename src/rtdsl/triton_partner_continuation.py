from __future__ import annotations

from time import perf_counter
from typing import Any, Mapping, Sequence

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
TRITON_GROUPED_VECTOR_SUM_F64X2_OPERATION = "grouped_vector_sum_f64x2"
TRITON_GROUPED_VECTOR_SUM_F64X2_OFFSETS_KERNEL = "grouped_vector_sum_f64x2_offsets_kernel"
TRITON_GROUPED_VECTOR_SUM_F64X2_OFFSETS_BATCHED_KERNEL = "grouped_vector_sum_f64x2_offsets_batched_kernel"
TRITON_SEGMENTED_COUNT_I64_OPERATION = "segmented_count_i64"
TRITON_SEGMENTED_MIN_F64_OPERATION = "segmented_min_f64"
TRITON_SEGMENTED_MAX_F64_OPERATION = "segmented_max_f64"
TRITON_COMPACT_MASK_I64_OPERATION = "compact_mask_i64"
TRITON_EDGE_LIST_COMPONENTS_I64_OPERATION = "edge_list_components_i64"
TRITON_GROUPED_ARGMIN_F64_OPERATION = "grouped_argmin_f64"
TRITON_GROUPED_ARGMAX_F64_OPERATION = "grouped_argmax_f64"
TRITON_GROUPED_TOPK_F64_OPERATION = "grouped_topk_f64"
TRITON_DENSE_POINT_TOPK_2D_ADAPTER_KERNEL = "dense_point_topk_2d_adapter_kernel"
TRITON_DENSE_POINT_NEAREST_2D_ADAPTER_KERNEL = "dense_point_nearest_2d_adapter_kernel"
TRITON_DENSE_POINT_NEAREST_2D_TILED_ADAPTER_KERNEL = "dense_point_nearest_2d_tiled_adapter_kernel"
TRITON_BOUNDED_COLLECT_FINALIZE_I64_OPERATION = "bounded_collect_finalize_i64"
TRITON_PARTNER_CONTINUATION_STATUS = V2_5_STATUS_PREVIEW_NOT_PROMOTED
TRITON_TENSOR_CARRIER = "torch_cuda_tensor_for_triton_launch"
TRITON_GROUPED_TOPK_F64_MAX_K = 64
TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_I64_OPERATION = "group_id_bounds_device_flag_i64"
TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE = "torch_cuda_precheck_host_scalar_sync"
TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_MODE = "triton_device_error_flag_no_host_read"
TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_HOST_RAISE_MODE = "triton_device_error_flag_host_scalar_raise"
TRITON_GROUP_ID_BOUNDS_NOT_APPLICABLE = "not_applicable_no_group_ids"
TRITON_GROUP_ID_BOUNDS_DEVICE_ERROR_FLAG_AVAILABLE = True


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


def describe_triton_grouped_vector_sum_f64x2() -> dict[str, object]:
    descriptor = _base_triton_descriptor(TRITON_GROUPED_VECTOR_SUM_F64X2_OPERATION)
    descriptor["input_columns"] = ("group_ids:int64", "values_x:float64", "values_y:float64")
    descriptor["output_columns"] = ("sum_x:float64", "sum_y:float64")
    descriptor["vector_width"] = 2
    descriptor["component_contract"] = "paired_float64_components"
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


def describe_triton_edge_list_components_i64() -> dict[str, object]:
    descriptor = _base_triton_descriptor(TRITON_EDGE_LIST_COMPONENTS_I64_OPERATION)
    descriptor["input_columns"] = ("source_ids:int64", "target_ids:int64")
    descriptor["output_columns"] = ("component_ids:int64",)
    descriptor["algorithm"] = "fixed_iteration_min_label_propagation"
    descriptor["component_label"] = "smallest_node_id_in_component"
    descriptor["convergence_contract"] = "caller_supplied_max_iterations_must_cover_component_diameter"
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


def describe_triton_grouped_argmax_f64() -> dict[str, object]:
    descriptor = _base_triton_descriptor(TRITON_GROUPED_ARGMAX_F64_OPERATION)
    descriptor["input_columns"] = ("group_ids:int64", "item_ids:int64", "scores:float64")
    descriptor["output_columns"] = (
        "group_ids:int64",
        "item_ids:int64",
        "scores:float64",
        "missing_group_ids:int64",
    )
    descriptor["tie_break"] = "highest_score_then_lowest_item_id"
    descriptor["tensor_carrier_compaction_used"] = True
    return descriptor


def describe_triton_grouped_topk_f64() -> dict[str, object]:
    descriptor = _base_triton_descriptor(TRITON_GROUPED_TOPK_F64_OPERATION)
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
    descriptor["max_k"] = TRITON_GROUPED_TOPK_F64_MAX_K
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


def describe_triton_group_id_bounds_device_flag_i64() -> dict[str, object]:
    """Describe the optional device-resident group-id validation helper."""

    return {
        "contract_version": V2_5_PARTNER_CONTINUATION_VERSION,
        "operation": TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_I64_OPERATION,
        "partner": "triton",
        "status": TRITON_PARTNER_CONTINUATION_STATUS,
        "phase": "partner_validation",
        "requires_cuda": True,
        "tensor_carrier": TRITON_TENSOR_CARRIER,
        "tensor_carrier_is_partner": False,
        "requires_torch_tensor_inputs": True,
        "input_columns": ("group_ids:int64",),
        "output_columns": ("invalid_count:int64[1]",),
        "triton_kernel_available": True,
        "raw_kernel_required": False,
        "replaces_rt_traversal": False,
        "promoted_performance_path": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "device_error_flag_available": True,
        "group_id_bounds_validation": _triton_group_id_bounds_validation_metadata(
            TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_I64_OPERATION,
            mode=TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_MODE,
        ),
        "claim_boundary": (
            "This helper writes an invalid-group counter on device for future "
            "device-resident continuation planning. Raising a Python exception "
            "from that counter still requires an explicit host scalar read."
        ),
    }


def describe_triton_partner_continuation(operation: str) -> dict[str, object]:
    """Describe the Triton-owned v2.5 continuation for any generic operation."""

    if operation == TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_I64_OPERATION:
        return describe_triton_group_id_bounds_device_flag_i64()
    if operation == TRITON_SEGMENTED_COUNT_I64_OPERATION:
        return describe_triton_segmented_count_i64()
    if operation == TRITON_SEGMENTED_SUM_F64_OPERATION:
        return describe_triton_segmented_sum_f64()
    if operation == TRITON_GROUPED_VECTOR_SUM_F64X2_OPERATION:
        return describe_triton_grouped_vector_sum_f64x2()
    if operation == TRITON_SEGMENTED_MIN_F64_OPERATION:
        return describe_triton_segmented_min_f64()
    if operation == TRITON_SEGMENTED_MAX_F64_OPERATION:
        return describe_triton_segmented_max_f64()
    if operation == TRITON_COMPACT_MASK_I64_OPERATION:
        return describe_triton_compact_mask_i64()
    if operation == TRITON_EDGE_LIST_COMPONENTS_I64_OPERATION:
        return describe_triton_edge_list_components_i64()
    if operation == TRITON_GROUPED_ARGMIN_F64_OPERATION:
        return describe_triton_grouped_argmin_f64()
    if operation == TRITON_GROUPED_ARGMAX_F64_OPERATION:
        return describe_triton_grouped_argmax_f64()
    if operation == TRITON_GROUPED_TOPK_F64_OPERATION:
        return describe_triton_grouped_topk_f64()
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
    group_id_bounds_validation_mode: str = TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE,
    allow_reference_fallback: bool = False,
    primitive_payload_descriptors: Sequence[Mapping[str, Any]] = (),
) -> dict[str, object]:
    """Run a Triton v2.5 continuation when a preview kernel exists.

    Unsupported operations can explicitly fall back to the Python reference for
    conformance. The fallback is labeled as `python_reference`; it is not a
    Triton performance path.
    """

    if operation not in V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
        raise ValueError(f"unsupported v2.5 partner continuation operation: {operation}")

    def with_payload_plan(result: dict[str, object], execution_status: str = "completed") -> dict[str, object]:
        if not primitive_payload_descriptors:
            return result
        from .hit_stream_handoff import attach_primitive_payload_partner_continuation_metadata

        return attach_primitive_payload_partner_continuation_metadata(
            result,
            operation=operation,
            partner="triton",
            descriptors=primitive_payload_descriptors,
            entrypoint="run_triton_partner_continuation",
            execution_status=execution_status,
        )

    if operation == TRITON_SEGMENTED_COUNT_I64_OPERATION:
        try:
            return with_payload_plan(run_triton_segmented_count_i64(
                inputs["group_ids"],
                group_count=int(inputs["group_count"]),
                block_size=block_size,
                group_id_bounds_validation_mode=group_id_bounds_validation_mode,
            ))
        except (ModuleNotFoundError, RuntimeError) as exc:
            if allow_reference_fallback and _is_triton_environment_error(exc):
                return with_payload_plan(_triton_reference_fallback(operation, inputs, str(exc)), "reference_fallback")
            raise
    if operation == TRITON_SEGMENTED_SUM_F64_OPERATION:
        try:
            return with_payload_plan(run_triton_segmented_sum_f64(
                inputs["group_ids"],
                inputs["values"],
                group_count=int(inputs["group_count"]),
                block_size=block_size,
                group_id_bounds_validation_mode=group_id_bounds_validation_mode,
            ))
        except (ModuleNotFoundError, RuntimeError) as exc:
            if allow_reference_fallback and _is_triton_environment_error(exc):
                return with_payload_plan(_triton_reference_fallback(operation, inputs, str(exc)), "reference_fallback")
            raise
    if operation == TRITON_GROUPED_VECTOR_SUM_F64X2_OPERATION:
        try:
            return with_payload_plan(run_triton_grouped_vector_sum_f64x2(
                inputs["group_ids"],
                inputs["values_x"],
                inputs["values_y"],
                group_count=int(inputs["group_count"]),
                block_size=block_size,
                group_id_bounds_validation_mode=group_id_bounds_validation_mode,
            ))
        except (ModuleNotFoundError, RuntimeError) as exc:
            if allow_reference_fallback and _is_triton_environment_error(exc):
                return with_payload_plan(_triton_reference_fallback(operation, inputs, str(exc)), "reference_fallback")
            raise
    if operation == TRITON_SEGMENTED_MIN_F64_OPERATION:
        try:
            return with_payload_plan(run_triton_segmented_min_f64(
                inputs["group_ids"],
                inputs["values"],
                group_count=int(inputs["group_count"]),
                block_size=block_size,
                group_id_bounds_validation_mode=group_id_bounds_validation_mode,
            ))
        except (ModuleNotFoundError, RuntimeError) as exc:
            if allow_reference_fallback and _is_triton_environment_error(exc):
                return with_payload_plan(_triton_reference_fallback(operation, inputs, str(exc)), "reference_fallback")
            raise
    if operation == TRITON_SEGMENTED_MAX_F64_OPERATION:
        try:
            return with_payload_plan(run_triton_segmented_max_f64(
                inputs["group_ids"],
                inputs["values"],
                group_count=int(inputs["group_count"]),
                block_size=block_size,
                group_id_bounds_validation_mode=group_id_bounds_validation_mode,
            ))
        except (ModuleNotFoundError, RuntimeError) as exc:
            if allow_reference_fallback and _is_triton_environment_error(exc):
                return with_payload_plan(_triton_reference_fallback(operation, inputs, str(exc)), "reference_fallback")
            raise
    if operation == TRITON_COMPACT_MASK_I64_OPERATION:
        try:
            return with_payload_plan(run_triton_compact_mask_i64(
                inputs["values"],
                inputs["mask"],
                block_size=block_size,
            ))
        except (ModuleNotFoundError, RuntimeError) as exc:
            if allow_reference_fallback and _is_triton_environment_error(exc):
                return with_payload_plan(_triton_reference_fallback(operation, inputs, str(exc)), "reference_fallback")
            raise
    if operation == TRITON_EDGE_LIST_COMPONENTS_I64_OPERATION:
        try:
            return with_payload_plan(run_triton_edge_list_components_i64(
                inputs["source_ids"],
                inputs["target_ids"],
                node_count=int(inputs["node_count"]),
                max_iterations=int(inputs["max_iterations"]),
                block_size=block_size,
            ))
        except (ModuleNotFoundError, RuntimeError) as exc:
            if allow_reference_fallback and _is_triton_environment_error(exc):
                return with_payload_plan(_triton_reference_fallback(operation, inputs, str(exc)), "reference_fallback")
            raise
    if operation == TRITON_GROUPED_ARGMIN_F64_OPERATION:
        try:
            return with_payload_plan(run_triton_grouped_argmin_f64(
                inputs["group_ids"],
                inputs["item_ids"],
                inputs["scores"],
                group_count=int(inputs["group_count"]),
                block_size=block_size,
                group_id_bounds_validation_mode=group_id_bounds_validation_mode,
            ))
        except (ModuleNotFoundError, RuntimeError) as exc:
            if allow_reference_fallback and _is_triton_environment_error(exc):
                return with_payload_plan(_triton_reference_fallback(operation, inputs, str(exc)), "reference_fallback")
            raise
    if operation == TRITON_GROUPED_ARGMAX_F64_OPERATION:
        try:
            return with_payload_plan(run_triton_grouped_argmax_f64(
                inputs["group_ids"],
                inputs["item_ids"],
                inputs["scores"],
                group_count=int(inputs["group_count"]),
                block_size=block_size,
                group_id_bounds_validation_mode=group_id_bounds_validation_mode,
            ))
        except (ModuleNotFoundError, RuntimeError) as exc:
            if allow_reference_fallback and _is_triton_environment_error(exc):
                return with_payload_plan(_triton_reference_fallback(operation, inputs, str(exc)), "reference_fallback")
            raise
    if operation == TRITON_GROUPED_TOPK_F64_OPERATION:
        try:
            return with_payload_plan(run_triton_grouped_topk_f64(
                inputs["group_ids"],
                inputs["item_ids"],
                inputs["scores"],
                group_count=int(inputs["group_count"]),
                k=int(inputs["k"]),
                block_size=block_size,
                group_id_bounds_validation_mode=group_id_bounds_validation_mode,
            ))
        except (ModuleNotFoundError, RuntimeError) as exc:
            if allow_reference_fallback and _is_triton_environment_error(exc):
                return with_payload_plan(_triton_reference_fallback(operation, inputs, str(exc)), "reference_fallback")
            raise
    if operation == TRITON_BOUNDED_COLLECT_FINALIZE_I64_OPERATION:
        try:
            return with_payload_plan(run_triton_bounded_collect_finalize_i64(
                inputs["group_ids"],
                inputs["item_ids"],
                group_count=int(inputs["group_count"]),
                k=int(inputs["k"]),
                total_row_capacity=inputs.get("total_row_capacity"),
                block_size=block_size,
                group_id_bounds_validation_mode=group_id_bounds_validation_mode,
            ))
        except (ModuleNotFoundError, RuntimeError) as exc:
            if allow_reference_fallback and _is_triton_environment_error(exc):
                return with_payload_plan(_triton_reference_fallback(operation, inputs, str(exc)), "reference_fallback")
            raise
    if not allow_reference_fallback:
        raise ValueError(
            f"Triton continuation `{operation}` is descriptor-only; "
            "pass allow_reference_fallback=True for conformance-only execution"
        )
    return with_payload_plan(
        _triton_reference_fallback(operation, inputs, "triton_descriptor_only_operation"),
        "reference_fallback",
    )


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
        "group_id_bounds_validation": _triton_group_id_bounds_validation_metadata(operation),
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
    group_id_bounds_validation_mode: str = TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE,
) -> dict[str, object]:
    """Run the v2.5 Triton segmented-count continuation pilot."""

    triton, torch, tl = _import_triton_stack()
    _validate_torch_cuda_vector(group_ids, name="group_ids", dtype=torch.int64)
    group_count, block_size, row_count = _validate_group_run_shape(
        group_ids,
        group_count=group_count,
        block_size=block_size,
        torch=torch,
        validation_mode=group_id_bounds_validation_mode,
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
        group_id_bounds_validation_mode=group_id_bounds_validation_mode,
    )


def run_triton_segmented_sum_f64(
    group_ids: Any,
    values: Any,
    *,
    group_count: int,
    block_size: int = 256,
    group_id_bounds_validation_mode: str = TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE,
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
        validation_mode=group_id_bounds_validation_mode,
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
        group_id_bounds_validation_mode=group_id_bounds_validation_mode,
    )


def run_triton_grouped_vector_sum_f64x2(
    group_ids: Any,
    values_x: Any,
    values_y: Any,
    *,
    group_count: int,
    block_size: int = 256,
    group_id_bounds_validation_mode: str = TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE,
) -> dict[str, object]:
    """Run the v2.5 Triton grouped two-component vector-sum preview."""

    triton, torch, tl = _import_triton_stack()
    _validate_torch_cuda_vector(group_ids, name="group_ids", dtype=torch.int64)
    _validate_torch_cuda_vector(values_x, name="values_x", dtype=torch.float64)
    _validate_torch_cuda_vector(values_y, name="values_y", dtype=torch.float64)
    if not (tuple(group_ids.shape) == tuple(values_x.shape) == tuple(values_y.shape)):
        raise ValueError("group_ids, values_x, and values_y must have the same shape")
    group_count, block_size, row_count = _validate_group_run_shape(
        group_ids,
        group_count=group_count,
        block_size=block_size,
        torch=torch,
        validation_mode=group_id_bounds_validation_mode,
    )

    torch.cuda.synchronize(group_ids.device)
    started = perf_counter()
    sum_x = torch.zeros((group_count,), dtype=torch.float64, device=values_x.device)
    sum_y = torch.zeros((group_count,), dtype=torch.float64, device=values_y.device)
    if row_count:
        grid = (triton.cdiv(row_count, block_size),)
        _triton_grouped_vector_sum_f64x2_kernel(tl)[grid](
            group_ids,
            values_x,
            values_y,
            sum_x,
            sum_y,
            row_count,
            group_count,
            BLOCK_SIZE=block_size,
        )
    torch.cuda.synchronize(group_ids.device)
    elapsed = perf_counter() - started

    return _triton_run_result(
        operation=TRITON_GROUPED_VECTOR_SUM_F64X2_OPERATION,
        outputs={"sum_x": sum_x, "sum_y": sum_y},
        elapsed=elapsed,
        source="run_triton_grouped_vector_sum_f64x2",
        group_id_bounds_validation_mode=group_id_bounds_validation_mode,
        extra_metadata={
            "vector_width": 2,
            "component_contract": "paired_float64_components",
        },
    )


def run_triton_grouped_vector_sum_f64x2_by_offsets(
    row_offsets: Any,
    values_x: Any,
    values_y: Any,
    *,
    max_group_block_size: int = 2048,
    groups_per_program: int = 1,
) -> dict[str, object]:
    """Run grouped vector sum for presegmented rows using row offsets."""

    triton, torch, tl = _import_triton_stack()
    _validate_torch_cuda_vector(row_offsets, name="row_offsets", dtype=torch.int64)
    _validate_torch_cuda_vector(values_x, name="values_x", dtype=torch.float64)
    _validate_torch_cuda_vector(values_y, name="values_y", dtype=torch.float64)
    if tuple(values_x.shape) != tuple(values_y.shape):
        raise ValueError("values_x and values_y must have the same shape")
    groups_per_program = int(groups_per_program)
    if groups_per_program < 1:
        raise ValueError("groups_per_program must be positive")
    group_count = int(row_offsets.numel()) - 1
    row_count = int(values_x.numel())
    if group_count < 0:
        raise ValueError("row_offsets must contain at least one element")
    if group_count == 0:
        sum_x = torch.empty((0,), dtype=torch.float64, device=values_x.device)
        sum_y = torch.empty((0,), dtype=torch.float64, device=values_y.device)
        return _triton_run_result(
            operation=TRITON_GROUPED_VECTOR_SUM_F64X2_OPERATION,
            outputs={"sum_x": sum_x, "sum_y": sum_y},
            elapsed=0.0,
            source="run_triton_grouped_vector_sum_f64x2_by_offsets",
            group_id_bounds_validation_mode=TRITON_GROUP_ID_BOUNDS_NOT_APPLICABLE,
            extra_metadata={
                "presegmented_row_offsets": True,
                "adapter_kernel": TRITON_GROUPED_VECTOR_SUM_F64X2_OFFSETS_KERNEL,
                "groups_per_program": groups_per_program,
                "program_count": 0,
                "global_atomic_add_used": False,
            },
        )
    if bool(torch.any(row_offsets[1:] < row_offsets[:-1]).item()):
        raise ValueError("row_offsets must be monotonically nondecreasing")
    if int(row_offsets[0].item()) != 0 or int(row_offsets[-1].item()) != row_count:
        raise ValueError("row_offsets must start at 0 and end at the row count")
    group_lengths = row_offsets[1:] - row_offsets[:-1]
    max_group_size = int(torch.max(group_lengths).item())
    block_size = max(1, int(triton.next_power_of_2(max_group_size)))
    if block_size > int(max_group_block_size):
        raise ValueError("presegmented vector-sum group length exceeds max_group_block_size")

    torch.cuda.synchronize(values_x.device)
    started = perf_counter()
    sum_x = torch.empty((group_count,), dtype=torch.float64, device=values_x.device)
    sum_y = torch.empty((group_count,), dtype=torch.float64, device=values_y.device)
    if groups_per_program == 1:
        adapter_kernel = TRITON_GROUPED_VECTOR_SUM_F64X2_OFFSETS_KERNEL
        program_count = group_count
        _triton_grouped_vector_sum_f64x2_offsets_kernel(tl)[(program_count,)](
            row_offsets,
            values_x,
            values_y,
            sum_x,
            sum_y,
            BLOCK_SIZE=block_size,
        )
    else:
        adapter_kernel = TRITON_GROUPED_VECTOR_SUM_F64X2_OFFSETS_BATCHED_KERNEL
        program_count = int(triton.cdiv(group_count, groups_per_program))
        _triton_grouped_vector_sum_f64x2_offsets_batched_kernel(tl)[(program_count,)](
            row_offsets,
            values_x,
            values_y,
            sum_x,
            sum_y,
            group_count,
            BLOCK_SIZE=block_size,
            GROUPS_PER_PROGRAM=groups_per_program,
        )
    torch.cuda.synchronize(values_x.device)
    elapsed = perf_counter() - started

    return _triton_run_result(
        operation=TRITON_GROUPED_VECTOR_SUM_F64X2_OPERATION,
        outputs={"sum_x": sum_x, "sum_y": sum_y},
        elapsed=elapsed,
        source="run_triton_grouped_vector_sum_f64x2_by_offsets",
        group_id_bounds_validation_mode=TRITON_GROUP_ID_BOUNDS_NOT_APPLICABLE,
        extra_metadata={
            "vector_width": 2,
            "component_contract": "paired_float64_components",
            "presegmented_row_offsets": True,
            "adapter_kernel": adapter_kernel,
            "max_group_size": max_group_size,
            "max_group_block_size": int(max_group_block_size),
            "groups_per_program": groups_per_program,
            "program_count": program_count,
            "global_atomic_add_used": False,
        },
    )


def run_triton_segmented_min_f64(
    group_ids: Any,
    values: Any,
    *,
    group_count: int,
    block_size: int = 256,
    group_id_bounds_validation_mode: str = TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE,
) -> dict[str, object]:
    """Run the v2.5 Triton segmented-min continuation preview."""

    return _run_triton_segmented_minmax_f64(
        group_ids,
        values,
        group_count=group_count,
        block_size=block_size,
        group_id_bounds_validation_mode=group_id_bounds_validation_mode,
        reduce="min",
    )


def run_triton_segmented_max_f64(
    group_ids: Any,
    values: Any,
    *,
    group_count: int,
    block_size: int = 256,
    group_id_bounds_validation_mode: str = TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE,
) -> dict[str, object]:
    """Run the v2.5 Triton segmented-max continuation preview."""

    return _run_triton_segmented_minmax_f64(
        group_ids,
        values,
        group_count=group_count,
        block_size=block_size,
        group_id_bounds_validation_mode=group_id_bounds_validation_mode,
        reduce="max",
    )


def _run_triton_segmented_minmax_f64(
    group_ids: Any,
    values: Any,
    *,
    group_count: int,
    block_size: int,
    group_id_bounds_validation_mode: str,
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
        validation_mode=group_id_bounds_validation_mode,
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
        group_id_bounds_validation_mode=group_id_bounds_validation_mode,
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


def run_triton_edge_list_components_i64(
    source_ids: Any,
    target_ids: Any,
    *,
    node_count: int,
    max_iterations: int,
    block_size: int = 256,
) -> dict[str, object]:
    """Run the v2.5 Triton edge-list component-labeling preview."""

    triton, torch, tl = _import_triton_stack()
    _validate_torch_cuda_vector(source_ids, name="source_ids", dtype=torch.int64)
    _validate_torch_cuda_vector(target_ids, name="target_ids", dtype=torch.int64)
    if tuple(source_ids.shape) != tuple(target_ids.shape):
        raise ValueError("source_ids and target_ids must have the same shape")
    if source_ids.device != target_ids.device:
        raise ValueError("source_ids and target_ids must be on the same CUDA device")
    node_count = int(node_count)
    max_iterations = int(max_iterations)
    block_size = int(block_size)
    if node_count < 0:
        raise ValueError("node_count must be non-negative")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    edge_count = int(source_ids.numel())
    if edge_count and bool(
        torch.any((source_ids < 0) | (source_ids >= node_count) | (target_ids < 0) | (target_ids >= node_count)).item()
    ):
        raise ValueError("source_ids and target_ids must be in [0, node_count)")

    torch.cuda.synchronize(source_ids.device)
    started = perf_counter()
    component_ids = torch.arange(node_count, dtype=torch.int64, device=source_ids.device)
    if edge_count and node_count:
        edge_grid = (triton.cdiv(edge_count, block_size),)
        node_grid = (triton.cdiv(node_count, block_size),)
        for _ in range(max_iterations):
            _triton_edge_list_component_relax_i64_kernel(tl)[edge_grid](
                source_ids,
                target_ids,
                component_ids,
                edge_count,
                node_count,
                BLOCK_SIZE=block_size,
            )
            _triton_edge_list_component_compress_i64_kernel(tl)[node_grid](
                component_ids,
                node_count,
                BLOCK_SIZE=block_size,
            )
    torch.cuda.synchronize(source_ids.device)
    elapsed = perf_counter() - started

    return _triton_run_result(
        operation=TRITON_EDGE_LIST_COMPONENTS_I64_OPERATION,
        outputs={"component_ids": component_ids},
        elapsed=elapsed,
        source="run_triton_edge_list_components_i64",
        extra_metadata={
            "algorithm": "fixed_iteration_min_label_propagation",
            "component_label": "smallest_node_id_in_component",
            "max_iterations": max_iterations,
            "convergence_contract": "caller_supplied_max_iterations_must_cover_component_diameter",
        },
    )


def run_triton_grouped_argmin_f64(
    group_ids: Any,
    item_ids: Any,
    scores: Any,
    *,
    group_count: int,
    block_size: int = 256,
    group_id_bounds_validation_mode: str = TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE,
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
        validation_mode=group_id_bounds_validation_mode,
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
        group_id_bounds_validation_mode=group_id_bounds_validation_mode,
        extra_metadata={
            "tie_break": "lowest_score_then_lowest_item_id",
            "tensor_carrier_compaction_used": True,
        },
    )


def run_triton_grouped_argmax_f64(
    group_ids: Any,
    item_ids: Any,
    scores: Any,
    *,
    group_count: int,
    block_size: int = 256,
    group_id_bounds_validation_mode: str = TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE,
) -> dict[str, object]:
    """Run the v2.5 Triton grouped-argmax continuation preview."""

    triton, torch, tl = _import_triton_stack()
    _validate_torch_cuda_vector(group_ids, name="group_ids", dtype=torch.int64)
    _validate_torch_cuda_vector(item_ids, name="item_ids", dtype=torch.int64)
    _validate_torch_cuda_vector(scores, name="scores", dtype=torch.float64)
    if not (tuple(group_ids.shape) == tuple(item_ids.shape) == tuple(scores.shape)):
        raise ValueError("group_ids, item_ids, and scores must have the same shape")
    if int(scores.numel()) and bool(torch.any(torch.isnan(scores)).item()):
        raise ValueError("grouped argmax rejects NaN scores")
    group_count, block_size, row_count = _validate_group_run_shape(
        group_ids,
        group_count=group_count,
        block_size=block_size,
        torch=torch,
        validation_mode=group_id_bounds_validation_mode,
    )

    torch.cuda.synchronize(group_ids.device)
    started = perf_counter()
    dense_scores = torch.full((group_count,), -float("inf"), dtype=torch.float64, device=scores.device)
    dense_item_ids = torch.full(
        (group_count,),
        torch.iinfo(torch.int64).max,
        dtype=torch.int64,
        device=item_ids.device,
    )
    counts = torch.zeros((group_count,), dtype=torch.int64, device=group_ids.device)
    if row_count:
        grid = (triton.cdiv(row_count, block_size),)
        _triton_grouped_argmax_score_f64_kernel(tl)[grid](
            group_ids,
            scores,
            dense_scores,
            counts,
            row_count,
            group_count,
            BLOCK_SIZE=block_size,
        )
        _triton_grouped_argmax_item_i64_kernel(tl)[grid](
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
        operation=TRITON_GROUPED_ARGMAX_F64_OPERATION,
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
        source="run_triton_grouped_argmax_f64",
        group_id_bounds_validation_mode=group_id_bounds_validation_mode,
        extra_metadata={
            "tie_break": "highest_score_then_lowest_item_id",
            "tensor_carrier_compaction_used": True,
        },
    )


def run_triton_grouped_topk_f64(
    group_ids: Any,
    item_ids: Any,
    scores: Any,
    *,
    group_count: int,
    k: int,
    block_size: int = 256,
    group_id_bounds_validation_mode: str = TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE,
) -> dict[str, object]:
    """Run the v2.5 Triton grouped top-k ranked-summary continuation preview."""

    triton, torch, tl = _import_triton_stack()
    _validate_torch_cuda_vector(group_ids, name="group_ids", dtype=torch.int64)
    _validate_torch_cuda_vector(item_ids, name="item_ids", dtype=torch.int64)
    _validate_torch_cuda_vector(scores, name="scores", dtype=torch.float64)
    if not (tuple(group_ids.shape) == tuple(item_ids.shape) == tuple(scores.shape)):
        raise ValueError("group_ids, item_ids, and scores must have the same shape")
    k = int(k)
    if k <= 0:
        raise ValueError("k must be positive")
    if k > TRITON_GROUPED_TOPK_F64_MAX_K:
        raise ValueError(f"grouped_topk_f64 preview supports k <= {TRITON_GROUPED_TOPK_F64_MAX_K}")
    if int(scores.numel()) and bool(torch.any(torch.isnan(scores)).item()):
        raise ValueError("grouped top-k rejects NaN scores")
    group_count, block_size, row_count = _validate_group_run_shape(
        group_ids,
        group_count=group_count,
        block_size=block_size,
        torch=torch,
        validation_mode=group_id_bounds_validation_mode,
    )

    torch.cuda.synchronize(group_ids.device)
    started = perf_counter()
    counts = torch.zeros((group_count,), dtype=torch.int64, device=group_ids.device)
    dense_scores = torch.full((group_count, k), float("inf"), dtype=torch.float64, device=scores.device)
    dense_item_ids = torch.full(
        (group_count, k),
        torch.iinfo(torch.int64).max,
        dtype=torch.int64,
        device=item_ids.device,
    )
    if row_count:
        grid = (triton.cdiv(row_count, block_size),)
        _triton_segmented_count_i64_kernel(tl)[grid](
            group_ids,
            counts,
            row_count,
            group_count,
            BLOCK_SIZE=block_size,
        )
        for rank in range(k):
            rank_scores = torch.full((group_count,), float("inf"), dtype=torch.float64, device=scores.device)
            rank_item_ids = torch.full(
                (group_count,),
                torch.iinfo(torch.int64).max,
                dtype=torch.int64,
                device=item_ids.device,
            )
            _triton_grouped_topk_score_f64_kernel(tl)[grid](
                group_ids,
                item_ids,
                scores,
                dense_item_ids,
                rank_scores,
                row_count,
                group_count,
                RANK=rank,
                K=k,
                BLOCK_SIZE=block_size,
            )
            _triton_grouped_topk_item_i64_kernel(tl)[grid](
                group_ids,
                item_ids,
                scores,
                dense_item_ids,
                rank_scores,
                rank_item_ids,
                row_count,
                group_count,
                RANK=rank,
                K=k,
                BLOCK_SIZE=block_size,
            )
            store_grid = (triton.cdiv(group_count, block_size),)
            _triton_grouped_topk_store_rank_kernel(tl)[store_grid](
                counts,
                rank_scores,
                rank_item_ids,
                dense_scores,
                dense_item_ids,
                group_count,
                RANK=rank,
                K=k,
                BLOCK_SIZE=block_size,
            )

    compact_counts = torch.clamp(counts, max=k)
    row_offsets = torch.empty((group_count + 1,), dtype=torch.int64, device=group_ids.device)
    row_offsets[0] = 0
    if group_count:
        row_offsets[1:] = torch.cumsum(compact_counts, dim=0)
    rank_values = torch.arange(1, k + 1, dtype=torch.int64, device=group_ids.device)
    rank_matrix = rank_values.reshape(1, k).expand(group_count, k)
    valid_mask = rank_matrix <= compact_counts.reshape(group_count, 1)
    repeated_group_ids = torch.arange(group_count, dtype=torch.int64, device=group_ids.device).reshape(group_count, 1).expand(group_count, k)
    compact_group_ids = repeated_group_ids[valid_mask]
    compact_item_ids = dense_item_ids[valid_mask]
    compact_scores = dense_scores[valid_mask]
    compact_ranks = rank_matrix[valid_mask]
    missing_group_ids = torch.nonzero(counts == 0, as_tuple=False).reshape(-1).to(torch.int64)
    torch.cuda.synchronize(group_ids.device)
    elapsed = perf_counter() - started

    return _triton_run_result(
        operation=TRITON_GROUPED_TOPK_F64_OPERATION,
        outputs={
            "group_ids": compact_group_ids,
            "item_ids": compact_item_ids,
            "scores": compact_scores,
            "ranks": compact_ranks,
            "row_offsets": row_offsets,
            "missing_group_ids": missing_group_ids,
            "dense_item_ids": dense_item_ids,
            "dense_scores": dense_scores,
            "counts": counts,
        },
        elapsed=elapsed,
        source="run_triton_grouped_topk_f64",
        group_id_bounds_validation_mode=group_id_bounds_validation_mode,
        extra_metadata={
            "tie_break": "lowest_score_then_lowest_item_id",
            "duplicate_item_policy": "lowest_score_per_group_item",
            "max_k": TRITON_GROUPED_TOPK_F64_MAX_K,
            "tensor_carrier_compaction_used": True,
        },
    )


def run_triton_dense_point_topk_2d(
    query_ids: Any,
    query_x: Any,
    query_y: Any,
    candidate_ids: Any,
    candidate_x: Any,
    candidate_y: Any,
    *,
    k: int,
    max_candidate_block_size: int = 4096,
) -> dict[str, object]:
    """Run a direct dense 2D point top-k adapter kernel without score materialization."""

    triton, torch, tl = _import_triton_stack()
    _validate_torch_cuda_vector(query_ids, name="query_ids", dtype=torch.int64)
    _validate_torch_cuda_vector(query_x, name="query_x", dtype=torch.float64)
    _validate_torch_cuda_vector(query_y, name="query_y", dtype=torch.float64)
    _validate_torch_cuda_vector(candidate_ids, name="candidate_ids", dtype=torch.int64)
    _validate_torch_cuda_vector(candidate_x, name="candidate_x", dtype=torch.float64)
    _validate_torch_cuda_vector(candidate_y, name="candidate_y", dtype=torch.float64)
    if not (tuple(query_ids.shape) == tuple(query_x.shape) == tuple(query_y.shape)):
        raise ValueError("query ids/x/y must have the same shape")
    if not (tuple(candidate_ids.shape) == tuple(candidate_x.shape) == tuple(candidate_y.shape)):
        raise ValueError("candidate ids/x/y must have the same shape")
    query_count = int(query_ids.numel())
    candidate_count = int(candidate_ids.numel())
    k = int(k)
    if query_count <= 0 or candidate_count <= 0:
        raise ValueError("dense point top-k requires non-empty query and candidate columns")
    if k <= 0:
        raise ValueError("k must be positive")
    if k > candidate_count:
        raise ValueError("k must be <= candidate point count")
    if k > TRITON_GROUPED_TOPK_F64_MAX_K:
        raise ValueError(f"dense point top-k adapter supports k <= {TRITON_GROUPED_TOPK_F64_MAX_K}")
    block_size = int(triton.next_power_of_2(candidate_count))
    if block_size > int(max_candidate_block_size):
        raise ValueError("dense point top-k adapter candidate count exceeds max_candidate_block_size")

    output_shape = (query_count * k,)
    output_query_ids = torch.empty(output_shape, dtype=torch.int64, device=query_ids.device)
    output_neighbor_ids = torch.empty(output_shape, dtype=torch.int64, device=candidate_ids.device)
    output_scores = torch.empty(output_shape, dtype=torch.float64, device=query_x.device)
    output_ranks = torch.empty(output_shape, dtype=torch.int64, device=query_ids.device)

    torch.cuda.synchronize(query_ids.device)
    started = perf_counter()
    _triton_dense_point_topk_2d_kernel(tl)[(query_count,)](
        query_ids,
        query_x,
        query_y,
        candidate_ids,
        candidate_x,
        candidate_y,
        output_query_ids,
        output_neighbor_ids,
        output_scores,
        output_ranks,
        candidate_count,
        K=k,
        BLOCK_SIZE=block_size,
    )
    torch.cuda.synchronize(query_ids.device)
    elapsed = perf_counter() - started

    return _triton_run_result(
        operation=TRITON_GROUPED_TOPK_F64_OPERATION,
        outputs={
            "query_ids": output_query_ids,
            "neighbor_ids": output_neighbor_ids,
            "scores": output_scores,
            "ranks": output_ranks,
        },
        elapsed=elapsed,
        source="run_triton_dense_point_topk_2d",
        group_id_bounds_validation_mode=TRITON_GROUP_ID_BOUNDS_NOT_APPLICABLE,
        extra_metadata={
            "adapter_kernel": TRITON_DENSE_POINT_TOPK_2D_ADAPTER_KERNEL,
            "logical_operation": TRITON_GROUPED_TOPK_F64_OPERATION,
            "tie_break": "lowest_score_then_lowest_candidate_id",
            "duplicate_item_policy": "lowest_score_per_candidate_id",
            "score_materialization": "none",
            "max_candidate_block_size": int(max_candidate_block_size),
        },
    )


def run_triton_dense_point_nearest_2d(
    query_ids: Any,
    query_x: Any,
    query_y: Any,
    candidate_ids: Any,
    candidate_x: Any,
    candidate_y: Any,
    *,
    max_candidate_block_size: int = 4096,
) -> dict[str, object]:
    """Run a direct dense 2D point nearest-witness adapter kernel."""

    triton, torch, tl = _import_triton_stack()
    _validate_torch_cuda_vector(query_ids, name="query_ids", dtype=torch.int64)
    _validate_torch_cuda_vector(query_x, name="query_x", dtype=torch.float64)
    _validate_torch_cuda_vector(query_y, name="query_y", dtype=torch.float64)
    _validate_torch_cuda_vector(candidate_ids, name="candidate_ids", dtype=torch.int64)
    _validate_torch_cuda_vector(candidate_x, name="candidate_x", dtype=torch.float64)
    _validate_torch_cuda_vector(candidate_y, name="candidate_y", dtype=torch.float64)
    if not (tuple(query_ids.shape) == tuple(query_x.shape) == tuple(query_y.shape)):
        raise ValueError("query ids/x/y must have the same shape")
    if not (tuple(candidate_ids.shape) == tuple(candidate_x.shape) == tuple(candidate_y.shape)):
        raise ValueError("candidate ids/x/y must have the same shape")
    query_count = int(query_ids.numel())
    candidate_count = int(candidate_ids.numel())
    if query_count <= 0 or candidate_count <= 0:
        raise ValueError("dense point nearest requires non-empty query and candidate columns")
    block_size = int(triton.next_power_of_2(candidate_count))
    if block_size > int(max_candidate_block_size):
        raise ValueError("dense point nearest adapter candidate count exceeds max_candidate_block_size")

    output_query_indices = torch.empty((query_count,), dtype=torch.int64, device=query_ids.device)
    output_query_ids = torch.empty((query_count,), dtype=torch.int64, device=query_ids.device)
    output_neighbor_ids = torch.empty((query_count,), dtype=torch.int64, device=candidate_ids.device)
    output_scores = torch.empty((query_count,), dtype=torch.float64, device=query_x.device)

    torch.cuda.synchronize(query_ids.device)
    started = perf_counter()
    _triton_dense_point_nearest_2d_kernel(tl)[(query_count,)](
        query_ids,
        query_x,
        query_y,
        candidate_ids,
        candidate_x,
        candidate_y,
        output_query_indices,
        output_query_ids,
        output_neighbor_ids,
        output_scores,
        candidate_count,
        BLOCK_SIZE=block_size,
    )
    torch.cuda.synchronize(query_ids.device)
    elapsed = perf_counter() - started

    return _triton_run_result(
        operation=TRITON_GROUPED_ARGMIN_F64_OPERATION,
        outputs={
            "query_indices": output_query_indices,
            "query_ids": output_query_ids,
            "neighbor_ids": output_neighbor_ids,
            "scores": output_scores,
        },
        elapsed=elapsed,
        source="run_triton_dense_point_nearest_2d",
        group_id_bounds_validation_mode=TRITON_GROUP_ID_BOUNDS_NOT_APPLICABLE,
        extra_metadata={
            "adapter_kernel": TRITON_DENSE_POINT_NEAREST_2D_ADAPTER_KERNEL,
            "logical_operation": TRITON_GROUPED_ARGMIN_F64_OPERATION,
            "tie_break": "lowest_score_then_lowest_candidate_id",
            "score_materialization": "none",
            "max_candidate_block_size": int(max_candidate_block_size),
        },
    )


def run_triton_dense_point_nearest_2d_tiled(
    query_ids: Any,
    query_x: Any,
    query_y: Any,
    candidate_ids: Any,
    candidate_x: Any,
    candidate_y: Any,
    *,
    candidate_block_size: int = 1024,
) -> dict[str, object]:
    """Run tiled dense 2D point nearest-witness without score-row materialization."""

    triton, torch, tl = _import_triton_stack()
    _validate_torch_cuda_vector(query_ids, name="query_ids", dtype=torch.int64)
    _validate_torch_cuda_vector(query_x, name="query_x", dtype=torch.float64)
    _validate_torch_cuda_vector(query_y, name="query_y", dtype=torch.float64)
    _validate_torch_cuda_vector(candidate_ids, name="candidate_ids", dtype=torch.int64)
    _validate_torch_cuda_vector(candidate_x, name="candidate_x", dtype=torch.float64)
    _validate_torch_cuda_vector(candidate_y, name="candidate_y", dtype=torch.float64)
    if not (tuple(query_ids.shape) == tuple(query_x.shape) == tuple(query_y.shape)):
        raise ValueError("query ids/x/y must have the same shape")
    if not (tuple(candidate_ids.shape) == tuple(candidate_x.shape) == tuple(candidate_y.shape)):
        raise ValueError("candidate ids/x/y must have the same shape")
    query_count = int(query_ids.numel())
    candidate_count = int(candidate_ids.numel())
    if query_count <= 0 or candidate_count <= 0:
        raise ValueError("dense point nearest tiled requires non-empty query and candidate columns")
    candidate_block_size = int(candidate_block_size)
    if candidate_block_size <= 0:
        raise ValueError("candidate_block_size must be positive")
    block_size = int(triton.next_power_of_2(candidate_block_size))
    tile_count = (candidate_count + candidate_block_size - 1) // candidate_block_size
    tile_rows = query_count * tile_count
    tile_query_indices = torch.empty((tile_rows,), dtype=torch.int64, device=query_ids.device)
    tile_neighbor_ids = torch.empty((tile_rows,), dtype=torch.int64, device=candidate_ids.device)
    tile_scores = torch.empty((tile_rows,), dtype=torch.float64, device=query_x.device)

    torch.cuda.synchronize(query_ids.device)
    started = perf_counter()
    _triton_dense_point_nearest_2d_tile_kernel(tl)[(query_count, tile_count)](
        query_ids,
        query_x,
        query_y,
        candidate_ids,
        candidate_x,
        candidate_y,
        tile_query_indices,
        tile_neighbor_ids,
        tile_scores,
        candidate_count,
        CANDIDATE_BLOCK_SIZE=candidate_block_size,
        BLOCK_SIZE=block_size,
    )
    torch.cuda.synchronize(query_ids.device)
    tile_elapsed = perf_counter() - started

    reduce_started = perf_counter()
    argmin_result = run_triton_grouped_argmin_f64(
        tile_query_indices,
        tile_neighbor_ids,
        tile_scores,
        group_count=query_count,
    )
    reduce_elapsed = perf_counter() - reduce_started
    query_indices = torch.arange(query_count, dtype=torch.int64, device=query_ids.device)
    outputs = {
        "query_indices": query_indices,
        "query_ids": query_ids,
        "neighbor_ids": argmin_result["outputs"]["dense_item_ids"],
        "scores": argmin_result["outputs"]["dense_scores"],
        "tile_query_indices": tile_query_indices,
        "tile_neighbor_ids": tile_neighbor_ids,
        "tile_scores": tile_scores,
    }
    elapsed = tile_elapsed + reduce_elapsed

    return _triton_run_result(
        operation=TRITON_GROUPED_ARGMIN_F64_OPERATION,
        outputs=outputs,
        elapsed=elapsed,
        source="run_triton_dense_point_nearest_2d_tiled",
        group_id_bounds_validation_mode=TRITON_GROUP_ID_BOUNDS_NOT_APPLICABLE,
        extra_metadata={
            "adapter_kernel": TRITON_DENSE_POINT_NEAREST_2D_TILED_ADAPTER_KERNEL,
            "logical_operation": TRITON_GROUPED_ARGMIN_F64_OPERATION,
            "tie_break": "lowest_score_then_lowest_candidate_id",
            "score_materialization": "tile_witness_rows_only",
            "candidate_block_size": candidate_block_size,
            "candidate_tile_count": tile_count,
            "tile_witness_row_count": tile_rows,
            "tile_kernel_elapsed_seconds": float(tile_elapsed),
            "tile_argmin_reduce_elapsed_seconds": float(reduce_elapsed),
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
    group_id_bounds_validation_mode: str = TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE,
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
        validation_mode=group_id_bounds_validation_mode,
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
        group_id_bounds_validation_mode=group_id_bounds_validation_mode,
        extra_metadata={
            "failure_mode": "fail_closed_overflow",
            "within_group_order": "unspecified_nonsemantic",
            "tensor_carrier_prefix_sum_used": True,
        },
    )


def run_triton_group_id_bounds_device_flag_i64(
    group_ids: Any,
    *,
    group_count: int,
    block_size: int = 256,
) -> dict[str, object]:
    """Write a device-resident invalid-group counter for v2.5 Triton previews."""

    triton, torch, tl = _import_triton_stack()
    _validate_torch_cuda_vector(group_ids, name="group_ids", dtype=torch.int64)
    group_count, block_size, row_count = _validate_group_run_shape(
        group_ids,
        group_count=group_count,
        block_size=block_size,
        torch=torch,
        validation_mode=TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_MODE,
    )

    torch.cuda.synchronize(group_ids.device)
    started = perf_counter()
    invalid_count = torch.zeros((1,), dtype=torch.int64, device=group_ids.device)
    if row_count:
        grid = (triton.cdiv(row_count, block_size),)
        _triton_group_id_bounds_device_flag_i64_kernel(tl)[grid](
            group_ids,
            invalid_count,
            row_count,
            group_count,
            BLOCK_SIZE=block_size,
        )
    torch.cuda.synchronize(group_ids.device)
    elapsed = perf_counter() - started

    return _triton_run_result(
        operation=TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_I64_OPERATION,
        outputs={"invalid_count": invalid_count},
        elapsed=elapsed,
        source="run_triton_group_id_bounds_device_flag_i64",
        group_id_bounds_validation_mode=TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_MODE,
        extra_metadata={
            "phase": "partner_validation",
            "device_error_flag_available": True,
            "host_scalar_sync_for_exception": False,
            "strict_exception_requires_host_read": True,
        },
    )


def assert_triton_group_ids_in_bounds_device_flag_i64(
    group_ids: Any,
    *,
    group_count: int,
    block_size: int = 256,
) -> dict[str, object]:
    """Enforce group-id bounds through the device flag, then a host exception read."""

    result = run_triton_group_id_bounds_device_flag_i64(
        group_ids,
        group_count=group_count,
        block_size=block_size,
    )
    invalid_count = int(result["outputs"]["invalid_count"].item())
    result["group_id_bounds_validation"] = _triton_group_id_bounds_validation_metadata(
        TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_I64_OPERATION,
        mode=TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_HOST_RAISE_MODE,
    )
    result["host_scalar_sync_for_exception"] = True
    if invalid_count:
        raise ValueError(
            "group_ids must be in [0, group_count); "
            f"device_error_flag invalid_count={invalid_count}"
        )
    return result


def _triton_run_result(
    *,
    operation: str,
    outputs: dict[str, object],
    elapsed: float,
    source: str,
    group_id_bounds_validation_mode: str = TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE,
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
        "group_id_bounds_validation": _triton_group_id_bounds_validation_metadata(
            operation,
            mode=group_id_bounds_validation_mode,
        ),
    }
    if extra_metadata:
        result.update(dict(extra_metadata))
    return result


def _triton_group_id_bounds_validation_metadata(
    operation: str,
    *,
    mode: str = TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE,
) -> dict[str, object]:
    if operation == TRITON_COMPACT_MASK_I64_OPERATION:
        return {
            "mode": TRITON_GROUP_ID_BOUNDS_NOT_APPLICABLE,
            "checked_before_kernel_launch": False,
            "uses_host_scalar_sync": False,
            "device_error_flag_available": False,
            "claim_boundary": "compact_mask_i64 has no group-id bounds contract",
        }
    if operation == TRITON_EDGE_LIST_COMPONENTS_I64_OPERATION:
        return {
            "mode": "edge_endpoint_bounds_host_scalar_sync",
            "checked_before_kernel_launch": True,
            "uses_host_scalar_sync": True,
            "device_error_flag_available": False,
            "true_zero_copy_claim_authorized": False,
            "claim_boundary": (
                "edge_list_components_i64 checks source/target endpoint bounds "
                "before launch through a Torch CUDA predicate and host scalar sync. "
                "This is not a zero-copy validation path."
            ),
        }
    if mode == TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_MODE:
        return {
            "mode": TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_MODE,
            "checked_before_kernel_launch": True,
            "uses_host_scalar_sync": False,
            "device_error_flag_available": True,
            "host_scalar_sync_required_for_python_exception": True,
            "true_zero_copy_claim_authorized": False,
            "claim_boundary": (
                "The Triton helper writes an invalid-group counter on device "
                "without reading it on the host. Treating that counter as a "
                "Python exception still requires a separate host scalar read."
            ),
        }
    if mode == TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_HOST_RAISE_MODE:
        return {
            "mode": TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_HOST_RAISE_MODE,
            "checked_before_kernel_launch": True,
            "uses_host_scalar_sync": True,
            "device_error_flag_available": True,
            "device_error_flag_used": True,
            "true_zero_copy_claim_authorized": False,
            "claim_boundary": (
                "Bounds are detected by a Triton device counter, then read "
                "back as a host scalar to preserve Python fail-closed errors. "
                "This is not a zero-copy validation path."
            ),
        }
    return {
        "mode": TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE,
        "checked_before_kernel_launch": True,
        "uses_host_scalar_sync": True,
        "device_error_flag_available": TRITON_GROUP_ID_BOUNDS_DEVICE_ERROR_FLAG_AVAILABLE,
        "device_error_flag_mode": TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_MODE,
        "device_error_flag_used_by_default": False,
        "true_zero_copy_claim_authorized": False,
        "claim_boundary": (
            "v2.5 Triton preview kernels reject out-of-range group ids before "
            "launch via a Torch CUDA predicate and host scalar sync. A "
            "separate device-error-flag helper is available, but the default "
            "strict Python exception path still reads a host scalar."
        ),
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


def _triton_grouped_vector_sum_f64x2_kernel(tl):
    @__import__("triton").jit
    def kernel(group_ids, values_x, values_y, output_x, output_y, row_count: tl.constexpr, group_count: tl.constexpr, BLOCK_SIZE: tl.constexpr):
        program_id = tl.program_id(0)
        offsets = program_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offsets < row_count
        groups = tl.load(group_ids + offsets, mask=mask, other=-1)
        vals_x = tl.load(values_x + offsets, mask=mask, other=0.0)
        vals_y = tl.load(values_y + offsets, mask=mask, other=0.0)
        valid = mask & (groups >= 0) & (groups < group_count)
        tl.atomic_add(output_x + groups, vals_x, sem="relaxed", mask=valid)
        tl.atomic_add(output_y + groups, vals_y, sem="relaxed", mask=valid)

    return kernel


def _triton_grouped_vector_sum_f64x2_offsets_kernel(tl):
    @__import__("triton").jit
    def kernel(row_offsets, values_x, values_y, output_x, output_y, BLOCK_SIZE: tl.constexpr):
        group = tl.program_id(0)
        start = tl.load(row_offsets + group)
        end = tl.load(row_offsets + group + 1)
        offsets = start + tl.arange(0, BLOCK_SIZE)
        valid = offsets < end
        vals_x = tl.load(values_x + offsets, mask=valid, other=0.0)
        vals_y = tl.load(values_y + offsets, mask=valid, other=0.0)
        tl.store(output_x + group, tl.sum(vals_x, axis=0))
        tl.store(output_y + group, tl.sum(vals_y, axis=0))

    return kernel


def _triton_grouped_vector_sum_f64x2_offsets_batched_kernel(tl):
    @__import__("triton").jit
    def kernel(
        row_offsets,
        values_x,
        values_y,
        output_x,
        output_y,
        group_count: tl.constexpr,
        BLOCK_SIZE: tl.constexpr,
        GROUPS_PER_PROGRAM: tl.constexpr,
    ):
        program_id = tl.program_id(0)
        offsets_in_group = tl.arange(0, BLOCK_SIZE)
        for slot in tl.static_range(0, GROUPS_PER_PROGRAM):
            group = program_id * GROUPS_PER_PROGRAM + slot
            active_group = group < group_count
            start = tl.load(row_offsets + group, mask=active_group, other=0)
            end = tl.load(row_offsets + group + 1, mask=active_group, other=0)
            offsets = start + offsets_in_group
            valid = active_group & (offsets < end)
            vals_x = tl.load(values_x + offsets, mask=valid, other=0.0)
            vals_y = tl.load(values_y + offsets, mask=valid, other=0.0)
            tl.store(output_x + group, tl.sum(vals_x, axis=0), mask=active_group)
            tl.store(output_y + group, tl.sum(vals_y, axis=0), mask=active_group)

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


def _triton_edge_list_component_relax_i64_kernel(tl):
    @__import__("triton").jit
    def kernel(source_ids, target_ids, component_ids, edge_count: tl.constexpr, node_count: tl.constexpr, BLOCK_SIZE: tl.constexpr):
        program_id = tl.program_id(0)
        offsets = program_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offsets < edge_count
        sources = tl.load(source_ids + offsets, mask=mask, other=0)
        targets = tl.load(target_ids + offsets, mask=mask, other=0)
        valid = mask & (sources >= 0) & (sources < node_count) & (targets >= 0) & (targets < node_count)
        source_labels = tl.load(component_ids + sources, mask=valid, other=0)
        target_labels = tl.load(component_ids + targets, mask=valid, other=0)
        low = tl.minimum(source_labels, target_labels)
        tl.atomic_min(component_ids + sources, low, sem="relaxed", mask=valid)
        tl.atomic_min(component_ids + targets, low, sem="relaxed", mask=valid)

    return kernel


def _triton_edge_list_component_compress_i64_kernel(tl):
    @__import__("triton").jit
    def kernel(component_ids, node_count: tl.constexpr, BLOCK_SIZE: tl.constexpr):
        program_id = tl.program_id(0)
        nodes = program_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        valid = nodes < node_count
        parents = tl.load(component_ids + nodes, mask=valid, other=0)
        grandparents = tl.load(component_ids + parents, mask=valid, other=0)
        new_parent = tl.minimum(parents, grandparents)
        tl.store(component_ids + nodes, new_parent, mask=valid)

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


def _triton_grouped_argmax_score_f64_kernel(tl):
    @__import__("triton").jit
    def kernel(group_ids, scores, dense_scores, counts, row_count: tl.constexpr, group_count: tl.constexpr, BLOCK_SIZE: tl.constexpr):
        program_id = tl.program_id(0)
        offsets = program_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offsets < row_count
        groups = tl.load(group_ids + offsets, mask=mask, other=-1)
        vals = tl.load(scores + offsets, mask=mask, other=-float("inf"))
        valid = mask & (groups >= 0) & (groups < group_count)
        tl.atomic_max(dense_scores + groups, vals, sem="relaxed", mask=valid)
        ones = tl.full((BLOCK_SIZE,), 1, tl.int64)
        tl.atomic_add(counts + groups, ones, sem="relaxed", mask=valid)

    return kernel


def _triton_grouped_argmax_item_i64_kernel(tl):
    @__import__("triton").jit
    def kernel(group_ids, item_ids, scores, dense_scores, dense_item_ids, row_count: tl.constexpr, group_count: tl.constexpr, BLOCK_SIZE: tl.constexpr):
        program_id = tl.program_id(0)
        offsets = program_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offsets < row_count
        groups = tl.load(group_ids + offsets, mask=mask, other=-1)
        items = tl.load(item_ids + offsets, mask=mask, other=0)
        vals = tl.load(scores + offsets, mask=mask, other=-float("inf"))
        valid = mask & (groups >= 0) & (groups < group_count)
        best_scores = tl.load(dense_scores + groups, mask=valid, other=-float("inf"))
        is_best = valid & (vals == best_scores)
        tl.atomic_min(dense_item_ids + groups, items, sem="relaxed", mask=is_best)

    return kernel


def _triton_grouped_topk_score_f64_kernel(tl):
    @__import__("triton").jit
    def kernel(group_ids, item_ids, scores, selected_item_ids, rank_scores, row_count: tl.constexpr, group_count: tl.constexpr, RANK: tl.constexpr, K: tl.constexpr, BLOCK_SIZE: tl.constexpr):
        program_id = tl.program_id(0)
        offsets = program_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offsets < row_count
        groups = tl.load(group_ids + offsets, mask=mask, other=-1)
        items = tl.load(item_ids + offsets, mask=mask, other=0)
        vals = tl.load(scores + offsets, mask=mask, other=float("inf"))
        valid = mask & (groups >= 0) & (groups < group_count)
        already_selected = tl.full((BLOCK_SIZE,), False, tl.int1)
        for previous_rank in tl.static_range(0, RANK):
            previous_items = tl.load(selected_item_ids + groups * K + previous_rank, mask=valid, other=-1)
            already_selected = already_selected | (previous_items == items)
        candidate = valid & (~already_selected)
        tl.atomic_min(rank_scores + groups, vals, sem="relaxed", mask=candidate)

    return kernel


def _triton_grouped_topk_item_i64_kernel(tl):
    @__import__("triton").jit
    def kernel(group_ids, item_ids, scores, selected_item_ids, rank_scores, rank_item_ids, row_count: tl.constexpr, group_count: tl.constexpr, RANK: tl.constexpr, K: tl.constexpr, BLOCK_SIZE: tl.constexpr):
        program_id = tl.program_id(0)
        offsets = program_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offsets < row_count
        groups = tl.load(group_ids + offsets, mask=mask, other=-1)
        items = tl.load(item_ids + offsets, mask=mask, other=0)
        vals = tl.load(scores + offsets, mask=mask, other=float("inf"))
        valid = mask & (groups >= 0) & (groups < group_count)
        already_selected = tl.full((BLOCK_SIZE,), False, tl.int1)
        for previous_rank in tl.static_range(0, RANK):
            previous_items = tl.load(selected_item_ids + groups * K + previous_rank, mask=valid, other=-1)
            already_selected = already_selected | (previous_items == items)
        best_scores = tl.load(rank_scores + groups, mask=valid, other=float("inf"))
        is_best = valid & (~already_selected) & (vals == best_scores)
        tl.atomic_min(rank_item_ids + groups, items, sem="relaxed", mask=is_best)

    return kernel


def _triton_grouped_topk_store_rank_kernel(tl):
    @__import__("triton").jit
    def kernel(counts, rank_scores, rank_item_ids, dense_scores, dense_item_ids, group_count: tl.constexpr, RANK: tl.constexpr, K: tl.constexpr, BLOCK_SIZE: tl.constexpr):
        program_id = tl.program_id(0)
        groups = program_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        valid = groups < group_count
        counts_for_group = tl.load(counts + groups, mask=valid, other=0)
        items = tl.load(rank_item_ids + groups, mask=valid, other=9223372036854775807)
        scores = tl.load(rank_scores + groups, mask=valid, other=float("inf"))
        has_rank = valid & (RANK < counts_for_group) & (items != 9223372036854775807)
        offsets = groups * K + RANK
        tl.store(dense_item_ids + offsets, items, mask=has_rank)
        tl.store(dense_scores + offsets, scores, mask=has_rank)

    return kernel


def _triton_dense_point_topk_2d_kernel(tl):
    @__import__("triton").jit
    def kernel(
        query_ids,
        query_x,
        query_y,
        candidate_ids,
        candidate_x,
        candidate_y,
        output_query_ids,
        output_neighbor_ids,
        output_scores,
        output_ranks,
        candidate_count: tl.constexpr,
        K: tl.constexpr,
        BLOCK_SIZE: tl.constexpr,
    ):
        query_index = tl.program_id(0)
        offsets = tl.arange(0, BLOCK_SIZE)
        valid = offsets < candidate_count

        qid = tl.load(query_ids + query_index)
        qx = tl.load(query_x + query_index)
        qy = tl.load(query_y + query_index)
        cids = tl.load(candidate_ids + offsets, mask=valid, other=9223372036854775807)
        cx = tl.load(candidate_x + offsets, mask=valid, other=0.0)
        cy = tl.load(candidate_y + offsets, mask=valid, other=0.0)
        dx = qx - cx
        dy = qy - cy
        scores = tl.where(valid, dx * dx + dy * dy, float("inf"))
        selected = tl.full((BLOCK_SIZE,), False, tl.int1)

        for rank in tl.static_range(0, K):
            candidate_scores = tl.where(selected, float("inf"), scores)
            best_score = tl.min(candidate_scores, axis=0)
            best_score_mask = (~selected) & valid & (scores == best_score)
            best_id = tl.min(tl.where(best_score_mask, cids, 9223372036854775807), axis=0)
            out_offset = query_index * K + rank
            tl.store(output_query_ids + out_offset, qid)
            tl.store(output_neighbor_ids + out_offset, best_id)
            tl.store(output_scores + out_offset, best_score)
            tl.store(output_ranks + out_offset, rank + 1)
            selected = selected | (cids == best_id)

    return kernel


def _triton_dense_point_nearest_2d_kernel(tl):
    @__import__("triton").jit
    def kernel(
        query_ids,
        query_x,
        query_y,
        candidate_ids,
        candidate_x,
        candidate_y,
        output_query_indices,
        output_query_ids,
        output_neighbor_ids,
        output_scores,
        candidate_count: tl.constexpr,
        BLOCK_SIZE: tl.constexpr,
    ):
        query_index = tl.program_id(0)
        offsets = tl.arange(0, BLOCK_SIZE)
        valid = offsets < candidate_count

        qid = tl.load(query_ids + query_index)
        qx = tl.load(query_x + query_index)
        qy = tl.load(query_y + query_index)
        cids = tl.load(candidate_ids + offsets, mask=valid, other=9223372036854775807)
        cx = tl.load(candidate_x + offsets, mask=valid, other=0.0)
        cy = tl.load(candidate_y + offsets, mask=valid, other=0.0)
        dx = qx - cx
        dy = qy - cy
        scores = tl.where(valid, dx * dx + dy * dy, float("inf"))
        best_score = tl.min(scores, axis=0)
        best_score_mask = valid & (scores == best_score)
        best_id = tl.min(tl.where(best_score_mask, cids, 9223372036854775807), axis=0)
        tl.store(output_query_indices + query_index, query_index)
        tl.store(output_query_ids + query_index, qid)
        tl.store(output_neighbor_ids + query_index, best_id)
        tl.store(output_scores + query_index, best_score)

    return kernel


def _triton_dense_point_nearest_2d_tile_kernel(tl):
    @__import__("triton").jit
    def kernel(
        query_ids,
        query_x,
        query_y,
        candidate_ids,
        candidate_x,
        candidate_y,
        tile_query_indices,
        tile_neighbor_ids,
        tile_scores,
        candidate_count: tl.constexpr,
        CANDIDATE_BLOCK_SIZE: tl.constexpr,
        BLOCK_SIZE: tl.constexpr,
    ):
        query_index = tl.program_id(0)
        tile_index = tl.program_id(1)
        offsets = tl.arange(0, BLOCK_SIZE)
        candidate_offset = tile_index * CANDIDATE_BLOCK_SIZE + offsets
        valid = candidate_offset < candidate_count

        qx = tl.load(query_x + query_index)
        qy = tl.load(query_y + query_index)
        cids = tl.load(candidate_ids + candidate_offset, mask=valid, other=9223372036854775807)
        cx = tl.load(candidate_x + candidate_offset, mask=valid, other=0.0)
        cy = tl.load(candidate_y + candidate_offset, mask=valid, other=0.0)
        dx = qx - cx
        dy = qy - cy
        scores = tl.where(valid, dx * dx + dy * dy, float("inf"))
        best_score = tl.min(scores, axis=0)
        best_score_mask = valid & (scores == best_score)
        best_id = tl.min(tl.where(best_score_mask, cids, 9223372036854775807), axis=0)
        out_offset = query_index * tl.num_programs(1) + tile_index
        tl.store(tile_query_indices + out_offset, query_index)
        tl.store(tile_neighbor_ids + out_offset, best_id)
        tl.store(tile_scores + out_offset, best_score)

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


def _triton_group_id_bounds_device_flag_i64_kernel(tl):
    @__import__("triton").jit
    def kernel(group_ids, invalid_count, row_count: tl.constexpr, group_count: tl.constexpr, BLOCK_SIZE: tl.constexpr):
        program_id = tl.program_id(0)
        offsets = program_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offsets < row_count
        groups = tl.load(group_ids + offsets, mask=mask, other=0)
        invalid = mask & ((groups < 0) | (groups >= group_count))
        local_count = tl.sum(tl.where(invalid, 1, 0), axis=0)
        tl.atomic_add(invalid_count, local_count, sem="relaxed", mask=local_count != 0)

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
    validation_mode: str = TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE,
) -> tuple[int, int, int]:
    group_count = int(group_count)
    if group_count < 0:
        raise ValueError("group_count must be non-negative")
    block_size = int(block_size)
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    row_count = int(group_ids.numel())
    if validation_mode == TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_MODE:
        return group_count, block_size, row_count
    if validation_mode == TRITON_GROUP_ID_BOUNDS_DEVICE_FLAG_HOST_RAISE_MODE:
        if row_count:
            assert_triton_group_ids_in_bounds_device_flag_i64(
                group_ids,
                group_count=group_count,
                block_size=block_size,
            )
        return group_count, block_size, row_count
    if validation_mode != TRITON_GROUP_ID_BOUNDS_VALIDATION_MODE:
        raise ValueError(f"unsupported group_id_bounds_validation_mode: {validation_mode}")
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
