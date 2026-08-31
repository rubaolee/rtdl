"""App-neutral checked U64 reduction over device-resident partner columns.

The weighted path deliberately produces the maximum value, maximum weight,
weight sum and weighted value sum in one device pass and one host
synchronization.  The host then applies the same conservative no-overflow
proof as the former sequence of independent CuPy reductions.  A wrapped
provisional sum is never used when any proof obligation fails.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import re

from .v4_operation_evidence import OperationKind, OperationTrace


U64_MAX = (1 << 64) - 1
_SHA256 = re.compile(r"[0-9a-f]{64}")

_WEIGHTED_REDUCTION_SOURCE = r"""
extern "C" __global__ void rtdl_v4_checked_u64_weighted_reduce(
    const unsigned long long* values,
    const unsigned long long* weights,
    const unsigned long long count,
    unsigned long long* summary) {
  __shared__ unsigned long long maximum_values[256];
  __shared__ unsigned long long maximum_weights[256];
  __shared__ unsigned long long weight_sums[256];
  __shared__ unsigned long long weighted_sums[256];
  const unsigned int lane = threadIdx.x;
  const unsigned long long index =
      (unsigned long long)blockIdx.x * blockDim.x + lane;
  const unsigned long long value = index < count ? values[index] : 0ULL;
  const unsigned long long weight = index < count ? weights[index] : 0ULL;
  maximum_values[lane] = value;
  maximum_weights[lane] = weight;
  weight_sums[lane] = weight;
  weighted_sums[lane] = value * weight;
  __syncthreads();
  for (unsigned int stride = blockDim.x / 2; stride; stride >>= 1) {
    if (lane < stride) {
      maximum_values[lane] = (
          maximum_values[lane] > maximum_values[lane + stride]
              ? maximum_values[lane] : maximum_values[lane + stride]);
      maximum_weights[lane] = (
          maximum_weights[lane] > maximum_weights[lane + stride]
              ? maximum_weights[lane] : maximum_weights[lane + stride]);
      weight_sums[lane] += weight_sums[lane + stride];
      weighted_sums[lane] += weighted_sums[lane + stride];
    }
    __syncthreads();
  }
  if (lane == 0) {
    atomicMax(summary + 0, maximum_values[0]);
    atomicMax(summary + 1, maximum_weights[0]);
    atomicAdd(summary + 2, weight_sums[0]);
    atomicAdd(summary + 3, weighted_sums[0]);
  }
}
"""


def checked_u64_downstream_operation_identity(
    variant: str, *, target_identity_sha256: str, cupy_version: str,
) -> dict[str, object]:
    """Return the canonical target-local reducer recipe identity payload.

    The fused recipe includes the exact compiler-owned CUDA source and options.
    The legal-unfused recipe binds the exact ordered CuPy operation graph.  The
    latter deliberately does *not* claim that CuPy's opaque internal kernel
    count or binary was independently introspected; the enclosing exact source
    tree, target and dependency identities remain required separately.
    """

    if variant not in {"fusion_on", "fusion_off"}:
        raise ValueError("unknown checked-U64 downstream variant")
    if not isinstance(target_identity_sha256, str) or \
            _SHA256.fullmatch(target_identity_sha256) is None:
        raise ValueError("target_identity_sha256 must be a SHA-256 digest")
    if not isinstance(cupy_version, str) or not cupy_version:
        raise ValueError("cupy_version must be nonempty")
    implementation = (
        {
            "kind": "compiler_owned_rawkernel_recipe",
            "entry": "rtdl_v4_checked_u64_weighted_reduce",
            "source_sha256": hashlib.sha256(
                _WEIGHTED_REDUCTION_SOURCE.encode("utf-8")).hexdigest(),
            "options": ["-std=c++11"],
            "opaque_partner_kernel_binary_claimed": False,
        }
        if variant == "fusion_on"
        else {
            "kind": "trusted_cupy_operation_graph",
            "operations": [
                "cp.max(weights)",
                "maximum_weight.item()",
                "cp.sum(weights,dtype=cp.uint64)",
                "weight_sum.item()",
                "values*weights",
                "cp.sum(weighted_product,dtype=cp.uint64)",
                "weighted_sum.item()",
            ],
            "opaque_partner_kernel_binary_claimed": False,
        }
    )
    return {
        "schema": "rtdl.v4.checked_u64_downstream_operation_identity.v1",
        "variant": variant,
        "target_identity_sha256": target_identity_sha256,
        "cupy_version": cupy_version,
        "implementation": implementation,
    }


def checked_u64_downstream_operation_sha256(
    variant: str, *, target_identity_sha256: str, cupy_version: str,
) -> str:
    """Digest one structured recipe without claiming opaque kernel bytes."""

    payload = checked_u64_downstream_operation_identity(
        variant,
        target_identity_sha256=target_identity_sha256,
        cupy_version=cupy_version,
    )
    return hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CheckedU64WeightedReduction:
    value: int
    maximum_value: int
    maximum_weight: int
    weight_sum: int
    value_count: int
    value_upper_bound: int
    device_kernel_launch_count: int
    host_synchronization_count: int
    logical_reduction_count: int
    device_materialization_count: int
    operation_counts_event_derived: bool
    maximum_value_is_device_observed: bool


def validate_weighted_reduction_summary(
    *, value_count: int, value_upper_bound: int,
    maximum_value: int, maximum_weight: int, weight_sum: int,
) -> None:
    """Validate the exact conservative U64 bounds used by the device path."""

    for name, value in (
        ("value_count", value_count),
        ("value_upper_bound", value_upper_bound),
        ("maximum_value", maximum_value),
        ("maximum_weight", maximum_weight),
        ("weight_sum", weight_sum),
    ):
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= U64_MAX:
            raise ValueError(f"{name} must be a U64 integer")
    if value_count <= 0:
        raise ValueError("value_count must be positive")
    if maximum_value > value_upper_bound:
        raise ValueError("device values exceed declared upper bound")
    if maximum_weight and value_count > U64_MAX // maximum_weight:
        raise OverflowError("query-weight domain cannot be summed exactly")
    if weight_sum and value_upper_bound > U64_MAX // weight_sum:
        raise OverflowError("weighted hit-count U64 domain is unsafe")


@lru_cache(maxsize=1)
def _weighted_reduction_kernel():
    import cupy as cp

    return cp.RawKernel(
        _WEIGHTED_REDUCTION_SOURCE,
        "rtdl_v4_checked_u64_weighted_reduce",
        options=("-std=c++11",),
    )


def checked_u64_weighted_sum_device(
    values, weights, *, value_upper_bound: int,
    operation_trace: OperationTrace | None = None,
) -> CheckedU64WeightedReduction:
    """Return an exact weighted U64 sum for two resident contiguous columns.

    ``values`` and ``weights`` remain device-resident.  The four scalar
    summary values cross to the host once, where the conservative overflow
    proof is checked before the provisional weighted sum is trusted.
    """

    import cupy as cp

    for name, column in (("values", values), ("weights", weights)):
        if not isinstance(column, cp.ndarray) or column.dtype != cp.uint64 \
                or column.ndim != 1 or not column.flags.c_contiguous:
            raise TypeError(f"{name} must be a contiguous CuPy u64 vector")
    if int(values.size) != int(weights.size) or int(values.device.id) != int(weights.device.id):
        raise ValueError("values and weights must have matching size and device")
    if int(values.device.id) != int(cp.cuda.Device().id):
        raise ValueError("weighted reduction columns must belong to the current device")
    count = int(values.size)
    if count <= 0:
        raise ValueError("weighted reduction columns must be nonempty")
    if not isinstance(value_upper_bound, int) or isinstance(value_upper_bound, bool) \
            or not 0 <= value_upper_bound <= U64_MAX:
        raise ValueError("value_upper_bound must be a U64 integer")

    summary = cp.zeros(4, dtype=cp.uint64)
    threads = 256
    blocks = (count + threads - 1) // threads
    def launch_checked_summary_kernel() -> None:
        _weighted_reduction_kernel()(
            (blocks,), (threads,),
            (values, weights, cp.uint64(count), summary),
        )

    try:
        if operation_trace is None:
            launch_checked_summary_kernel()
            copied_summary = summary.get()
        else:
            operation_trace.execute(
                "checked_summary.kernel_launch", launch_checked_summary_kernel)
            copied_summary = operation_trace.execute(
                "checked_summary.summary_copy_sync", summary.get)
        maximum_value, maximum_weight, weight_sum, weighted_sum = (
            int(value) for value in copied_summary.tolist()
        )
        validate_weighted_reduction_summary(
            value_count=count,
            value_upper_bound=value_upper_bound,
            maximum_value=maximum_value,
            maximum_weight=maximum_weight,
            weight_sum=weight_sum,
        )
    except BaseException:
        if operation_trace is not None:
            operation_trace.abort()
        raise
    if operation_trace is None:
        event_counts = {
            OperationKind.COMPILER_KERNEL_INVOCATION.value: 1,
            OperationKind.HOST_COPY_SYNCHRONIZATION.value: 1,
            OperationKind.LOGICAL_REDUCTION.value: 0,
            OperationKind.DEVICE_MATERIALIZATION.value: 0,
        }
    else:
        event_counts = operation_trace.successful_event_counts()
    return CheckedU64WeightedReduction(
        value=weighted_sum,
        maximum_value=maximum_value,
        maximum_weight=maximum_weight,
        weight_sum=weight_sum,
        value_count=count,
        value_upper_bound=value_upper_bound,
        device_kernel_launch_count=event_counts[
            OperationKind.COMPILER_KERNEL_INVOCATION.value],
        host_synchronization_count=event_counts[
            OperationKind.HOST_COPY_SYNCHRONIZATION.value],
        logical_reduction_count=event_counts[
            OperationKind.LOGICAL_REDUCTION.value],
        device_materialization_count=event_counts[
            OperationKind.DEVICE_MATERIALIZATION.value],
        operation_counts_event_derived=operation_trace is not None,
        maximum_value_is_device_observed=True,
    )


def checked_u64_weighted_sum_unfused_device(
    values, weights, *, value_upper_bound: int,
    operation_trace: OperationTrace,
) -> CheckedU64WeightedReduction:
    """Execute the legal unfused checked-U64 product-sum lowering.

    This is intentionally the exact pre-Goal5778 V4 operation graph: reduce
    maximum weight, reduce weight sum, materialize ``values * weights``, and
    reduce the product.  Each host-visible scalar copy is a separate ordered
    event.  It is an experiment-only physical lowering of the same checked-U64
    semantic contract, not a V2 call and not an application-specific branch.
    """

    import cupy as cp

    if not isinstance(operation_trace, OperationTrace):
        raise TypeError("unfused checked reduction requires an OperationTrace")
    for name, column in (("values", values), ("weights", weights)):
        if not isinstance(column, cp.ndarray) or column.dtype != cp.uint64 \
                or column.ndim != 1 or not column.flags.c_contiguous:
            raise TypeError(f"{name} must be a contiguous CuPy u64 vector")
    if int(values.size) != int(weights.size) or \
            int(values.device.id) != int(weights.device.id):
        raise ValueError("values and weights must have matching size and device")
    if int(values.device.id) != int(cp.cuda.Device().id):
        raise ValueError("weighted reduction columns must belong to the current device")
    count = int(values.size)
    if count <= 0:
        raise ValueError("weighted reduction columns must be nonempty")
    if not isinstance(value_upper_bound, int) or isinstance(value_upper_bound, bool) \
            or not 0 <= value_upper_bound <= U64_MAX:
        raise ValueError("value_upper_bound must be a U64 integer")

    try:
        maximum_weight_device = operation_trace.execute(
            "maximum_weight.logical_reduce", lambda: cp.max(weights))
        maximum_weight = int(operation_trace.execute(
            "maximum_weight.scalar_copy_sync", maximum_weight_device.item))
        if maximum_weight and count > U64_MAX // maximum_weight:
            raise OverflowError("query-weight domain cannot be summed exactly")

        weight_sum_device = operation_trace.execute(
            "weight_sum.logical_reduce",
            lambda: cp.sum(weights, dtype=cp.uint64),
        )
        weight_sum = int(operation_trace.execute(
            "weight_sum.scalar_copy_sync", weight_sum_device.item))
        if weight_sum and value_upper_bound > U64_MAX // weight_sum:
            raise OverflowError("weighted hit-count U64 domain is unsafe")

        weighted_product = operation_trace.execute(
            "weighted_product.materialize", lambda: values * weights)
        weighted_sum_device = operation_trace.execute(
            "weighted_product_sum.logical_reduce",
            lambda: cp.sum(weighted_product, dtype=cp.uint64),
        )
        weighted_sum = int(operation_trace.execute(
            "weighted_product_sum.scalar_copy_sync", weighted_sum_device.item))

        # The OptiX producer contract proves every per-ray count is bounded by
        # the primitive count.  The unfused reference graph never performs an
        # extra max(values) reduction, so record the declared bound rather than
        # pretending it observed a fourth reduction.
        validate_weighted_reduction_summary(
            value_count=count,
            value_upper_bound=value_upper_bound,
            maximum_value=value_upper_bound,
            maximum_weight=maximum_weight,
            weight_sum=weight_sum,
        )
    except BaseException:
        operation_trace.abort()
        raise
    event_counts = operation_trace.successful_event_counts()
    return CheckedU64WeightedReduction(
        value=weighted_sum,
        maximum_value=value_upper_bound,
        maximum_weight=maximum_weight,
        weight_sum=weight_sum,
        value_count=count,
        value_upper_bound=value_upper_bound,
        device_kernel_launch_count=event_counts[
            OperationKind.COMPILER_KERNEL_INVOCATION.value],
        host_synchronization_count=event_counts[
            OperationKind.HOST_COPY_SYNCHRONIZATION.value],
        logical_reduction_count=event_counts[
            OperationKind.LOGICAL_REDUCTION.value],
        device_materialization_count=event_counts[
            OperationKind.DEVICE_MATERIALIZATION.value],
        operation_counts_event_derived=True,
        maximum_value_is_device_observed=False,
    )


__all__ = (
    "CheckedU64WeightedReduction",
    "checked_u64_downstream_operation_identity",
    "checked_u64_downstream_operation_sha256",
    "checked_u64_weighted_sum_device",
    "checked_u64_weighted_sum_unfused_device",
    "validate_weighted_reduction_summary",
)
