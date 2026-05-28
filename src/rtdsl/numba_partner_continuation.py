from __future__ import annotations

from time import perf_counter
from typing import Any

from .partner_continuation_protocol import V2_5_PARTNER_CONTINUATION_VERSION
from .partner_continuation_protocol import V2_5_STATUS_PREVIEW_NOT_PROMOTED
from .partner_protocol import V2_4_PARTNER_PROTOCOL_VERSION
from .partner_protocol import v2_4_phase_timing_metadata


NUMBA_SEGMENTED_COUNT_I64_OPERATION = "segmented_count_i64"
NUMBA_SEGMENTED_SUM_F64_OPERATION = "segmented_sum_f64"
NUMBA_PARTNER_CONTINUATION_STATUS = V2_5_STATUS_PREVIEW_NOT_PROMOTED
NUMBA_GROUP_ID_VALIDATION_MODE = "device_resident_error_flag"


def numba_partner_available() -> bool:
    try:
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
        _numba_segmented_count_i64_kernel(cuda)[grid, block_size](group_ids, output, row_count, group_count)
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
        _numba_segmented_sum_f64_kernel(cuda)[grid, block_size](group_ids, values, output, row_count, group_count)
    cuda.synchronize()
    elapsed = perf_counter() - started

    return _numba_run_result(
        operation=NUMBA_SEGMENTED_SUM_F64_OPERATION,
        outputs={"sums": output},
        elapsed=elapsed,
        source="run_numba_segmented_sum_f64",
    )


def _numba_run_result(
    *,
    operation: str,
    outputs: dict[str, object],
    elapsed: float,
    source: str,
) -> dict[str, object]:
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
        from numba import cuda
    except ImportError as exc:
        raise ModuleNotFoundError(
            "Numba continuation execution requires numba, numpy, and CUDA; "
            "use an NVIDIA pod for validation"
        ) from exc
    if not cuda.is_available():
        raise RuntimeError("Numba continuation execution requires CUDA; use an NVIDIA pod")
    return cuda, np


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
        _numba_group_id_validation_kernel(cuda)[grid, block_size](
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
