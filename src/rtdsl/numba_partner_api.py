from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from .device_column_row_buffer import DeviceColumnBuffer
from . import numba_partner_continuation as _numba_ops


NUMBA_PARTNER_CONTINUATION_CONTRACT_VERSION = (
    "rtdl.numba_partner_continuation.v2_14_4.public.v1"
)
NUMBA_PARTNER_CONTINUATION_API_MATURITY = (
    "public_contract_device_columnar_prepared_pipeline"
)
NUMBA_PARTNER_CONTINUATION_CLAIM_BOUNDARY = (
    "NumbaPartnerContinuation is the public RTDL contract for running approved "
    "Numba CUDA continuations over DeviceColumnBuffer inputs. It records device "
    "residency, stream-ordering, explicit host fallback, and output metadata. It "
    "does not replace RT traversal, does not authorize public speedup wording, "
    "does not authorize true-zero-copy wording, and does not permit app-specific "
    "semantics."
)

_DESCRIBERS: dict[str, Callable[[], dict[str, object]]] = {
    _numba_ops.NUMBA_LABEL_COUNT_AND_FLAG_COUNT_I64_OPERATION:
        _numba_ops.describe_numba_label_count_and_flag_count_i64,
    _numba_ops.NUMBA_ADJACENT_MIDPOINT_CANDIDATES_I64X2_BY_KEY_OPERATION:
        _numba_ops.describe_numba_adjacent_midpoint_candidates_i64x2_by_key,
    _numba_ops.NUMBA_CONSECUTIVE_DEDUPE_MASK_F64X2_OPERATION:
        _numba_ops.describe_numba_consecutive_dedupe_mask_f64x2,
    _numba_ops.NUMBA_RANGE_HAS_SORTED_VALUES_I64_OPERATION:
        _numba_ops.describe_numba_range_has_sorted_values_i64,
    _numba_ops.NUMBA_UINT32_EQUAL_MASK_OPERATION:
        _numba_ops.describe_numba_uint32_equal_mask,
    _numba_ops.NUMBA_PAIRWISE_L2_SQ_SCORE_ROWS_2D_OPERATION:
        _numba_ops.describe_numba_pairwise_l2_sq_score_rows_2d,
    _numba_ops.NUMBA_PAIRWISE_L2_SQ_BLOCK_NEAREST_ROWS_2D_OPERATION:
        _numba_ops.describe_numba_pairwise_l2_sq_block_nearest_rows_2d,
    _numba_ops.NUMBA_SQRT_F64_OPERATION:
        _numba_ops.describe_numba_sqrt_f64,
}

_RUNNERS: dict[str, Callable[..., dict[str, object]]] = {
    _numba_ops.NUMBA_LABEL_COUNT_AND_FLAG_COUNT_I64_OPERATION:
        _numba_ops.run_numba_label_count_and_flag_count_i64,
    _numba_ops.NUMBA_ADJACENT_MIDPOINT_CANDIDATES_I64X2_BY_KEY_OPERATION:
        _numba_ops.run_numba_adjacent_midpoint_candidates_i64x2_by_key,
    _numba_ops.NUMBA_CONSECUTIVE_DEDUPE_MASK_F64X2_OPERATION:
        _numba_ops.run_numba_consecutive_dedupe_mask_f64x2,
    _numba_ops.NUMBA_RANGE_HAS_SORTED_VALUES_I64_OPERATION:
        _numba_ops.run_numba_range_has_sorted_values_i64,
    _numba_ops.NUMBA_UINT32_EQUAL_MASK_OPERATION:
        _numba_ops.run_numba_uint32_equal_mask,
    _numba_ops.NUMBA_PAIRWISE_L2_SQ_SCORE_ROWS_2D_OPERATION:
        _numba_ops.run_numba_pairwise_l2_sq_score_rows_2d,
    _numba_ops.NUMBA_PAIRWISE_L2_SQ_BLOCK_NEAREST_ROWS_2D_OPERATION:
        _numba_ops.run_numba_pairwise_l2_sq_block_nearest_rows_2d,
    _numba_ops.NUMBA_SQRT_F64_OPERATION:
        _numba_ops.run_numba_sqrt_f64,
}

NUMBA_PARTNER_CONTINUATION_PUBLIC_OPERATIONS = tuple(_DESCRIBERS.keys())


@dataclass(frozen=True)
class NumbaPartnerContinuationPlan:
    operation: str
    input_buffer: DeviceColumnBuffer
    input_bindings: Mapping[str, str]
    scalar_inputs: Mapping[str, Any] = field(default_factory=dict)
    options: Mapping[str, Any] = field(default_factory=dict)
    allow_host_fallback: bool = False

    def __post_init__(self) -> None:
        if self.operation not in NUMBA_PARTNER_CONTINUATION_PUBLIC_OPERATIONS:
            raise ValueError("unsupported public Numba partner continuation operation")
        if not isinstance(self.input_buffer, DeviceColumnBuffer):
            raise ValueError("NumbaPartnerContinuation requires a DeviceColumnBuffer input")
        bindings = {str(name): str(column) for name, column in dict(self.input_bindings).items()}
        if not bindings:
            raise ValueError("NumbaPartnerContinuation requires explicit input bindings")
        descriptor = _DESCRIBERS[self.operation]()
        required = _required_input_names(descriptor)
        missing = tuple(name for name in required if name not in bindings)
        if missing:
            raise ValueError(f"missing Numba input bindings: {missing}")
        for logical_name, column_name in bindings.items():
            if column_name not in self.input_buffer.columns:
                raise ValueError(f"bound column {column_name!r} for {logical_name!r} is missing")
        if self.input_buffer.materializes_host_rows_for_bridge and not self.allow_host_fallback:
            raise ValueError("host-materialized buffers require allow_host_fallback=True")
        object.__setattr__(self, "input_bindings", bindings)
        object.__setattr__(self, "scalar_inputs", dict(self.scalar_inputs or {}))
        object.__setattr__(self, "options", dict(self.options or {}))

    @property
    def descriptor(self) -> dict[str, object]:
        return _DESCRIBERS[self.operation]()

    @property
    def host_fallback_used(self) -> bool:
        return bool(self.input_buffer.materializes_host_rows_for_bridge)

    def to_metadata(self) -> dict[str, Any]:
        descriptor = self.descriptor
        return {
            "contract_version": NUMBA_PARTNER_CONTINUATION_CONTRACT_VERSION,
            "api_maturity": NUMBA_PARTNER_CONTINUATION_API_MATURITY,
            "operation": self.operation,
            "partner": "numba",
            "input_bindings": dict(self.input_bindings),
            "scalar_inputs": tuple(sorted(self.scalar_inputs.keys())),
            "options": dict(self.options),
            "input_buffer": self.input_buffer.to_metadata(),
            "stream_ordering": self.input_buffer.producer_consumer_stream_ordering,
            "stream_synchronization_proven": (
                self.input_buffer.producer_consumer_stream_ordering != "not_proven"
            ),
            "device_resident_candidate": self.input_buffer.device_resident_candidate,
            "materializes_host_rows_for_bridge": self.input_buffer.materializes_host_rows_for_bridge,
            "allow_host_fallback": bool(self.allow_host_fallback),
            "host_fallback_used": self.host_fallback_used,
            "descriptor": descriptor,
            "replaces_rt_traversal": False,
            "raw_kernel_required": False,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "app_specific_semantics_allowed": False,
            "claim_boundary": NUMBA_PARTNER_CONTINUATION_CLAIM_BOUNDARY,
        }


@dataclass(frozen=True)
class NumbaPartnerContinuationResult:
    plan: NumbaPartnerContinuationPlan
    status: str
    outputs: Mapping[str, Any] = field(default_factory=dict, compare=False)
    metadata: Mapping[str, Any] = field(default_factory=dict, compare=False)

    def to_metadata(self) -> dict[str, Any]:
        return {
            "contract_version": NUMBA_PARTNER_CONTINUATION_CONTRACT_VERSION,
            "api_maturity": NUMBA_PARTNER_CONTINUATION_API_MATURITY,
            "status": self.status,
            "operation": self.plan.operation,
            "plan": self.plan.to_metadata(),
            "outputs": tuple(self.outputs.keys()),
            "metadata": dict(self.metadata),
            "host_fallback_used": self.plan.host_fallback_used,
            "public_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "app_specific_semantics_allowed": False,
            "claim_boundary": NUMBA_PARTNER_CONTINUATION_CLAIM_BOUNDARY,
        }


def describe_numba_partner_continuation_contract() -> dict[str, Any]:
    return {
        "contract_version": NUMBA_PARTNER_CONTINUATION_CONTRACT_VERSION,
        "api_maturity": NUMBA_PARTNER_CONTINUATION_API_MATURITY,
        "partner": "numba",
        "public_operations": NUMBA_PARTNER_CONTINUATION_PUBLIC_OPERATIONS,
        "operation_descriptors": tuple(_DESCRIBERS[name]() for name in NUMBA_PARTNER_CONTINUATION_PUBLIC_OPERATIONS),
        "input_surface": "DeviceColumnBuffer",
        "host_fallback_requires_explicit_opt_in": True,
        "local_cuda_unavailable_status": "skipped_cuda_unavailable",
        "replaces_rt_traversal": False,
        "raw_kernel_required": False,
        "public_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "app_specific_semantics_allowed": False,
        "claim_boundary": NUMBA_PARTNER_CONTINUATION_CLAIM_BOUNDARY,
    }


def validate_numba_partner_continuation_contract(
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = dict(contract or describe_numba_partner_continuation_contract())
    errors: list[str] = []
    if metadata.get("contract_version") != NUMBA_PARTNER_CONTINUATION_CONTRACT_VERSION:
        errors.append("unexpected Numba partner continuation contract version")
    if tuple(metadata.get("public_operations", ())) != NUMBA_PARTNER_CONTINUATION_PUBLIC_OPERATIONS:
        errors.append("Numba public operation set changed")
    if metadata.get("input_surface") != "DeviceColumnBuffer":
        errors.append("Numba partner continuation must use DeviceColumnBuffer input")
    if metadata.get("host_fallback_requires_explicit_opt_in") is not True:
        errors.append("host fallback must require explicit opt-in")
    for flag in (
        "replaces_rt_traversal",
        "raw_kernel_required",
        "public_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "app_specific_semantics_allowed",
    ):
        if metadata.get(flag):
            errors.append(f"{flag} must remain false")
    return {
        "contract_version": NUMBA_PARTNER_CONTINUATION_CONTRACT_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "claim_boundary": NUMBA_PARTNER_CONTINUATION_CLAIM_BOUNDARY,
    }


def numba_partner_continuation(
    *,
    operation: str,
    input_buffer: DeviceColumnBuffer,
    input_bindings: Mapping[str, str],
    scalar_inputs: Mapping[str, Any] | None = None,
    options: Mapping[str, Any] | None = None,
    allow_host_fallback: bool = False,
) -> NumbaPartnerContinuationPlan:
    return NumbaPartnerContinuationPlan(
        operation=operation,
        input_buffer=input_buffer,
        input_bindings=input_bindings,
        scalar_inputs=dict(scalar_inputs or {}),
        options=dict(options or {}),
        allow_host_fallback=allow_host_fallback,
    )


def run_numba_partner_continuation(
    plan: NumbaPartnerContinuationPlan,
    *,
    skip_if_cuda_unavailable: bool = True,
) -> NumbaPartnerContinuationResult:
    if not isinstance(plan, NumbaPartnerContinuationPlan):
        raise ValueError("run_numba_partner_continuation requires a NumbaPartnerContinuationPlan")
    if not _numba_ops.numba_partner_available():
        if skip_if_cuda_unavailable:
            return NumbaPartnerContinuationResult(
                plan=plan,
                status="skipped_cuda_unavailable",
                metadata={
                    "cuda_available": False,
                    "host_fallback_used": plan.host_fallback_used,
                },
            )
        raise RuntimeError("Numba CUDA is unavailable")
    runner = _RUNNERS[plan.operation]
    inputs = {
        logical_name: plan.input_buffer.columns[column_name]
        for logical_name, column_name in plan.input_bindings.items()
    }
    kwargs = dict(plan.scalar_inputs)
    kwargs.update(plan.options)
    result = runner(**inputs, **kwargs)
    return NumbaPartnerContinuationResult(
        plan=plan,
        status="completed",
        outputs=dict(result.get("outputs", {})),
        metadata=dict(result),
    )


def _required_input_names(descriptor: Mapping[str, object]) -> tuple[str, ...]:
    names: list[str] = []
    for entry in descriptor.get("input_columns", ()):
        name = str(entry).split(":", 1)[0]
        if name:
            names.append(name)
    return tuple(names)


__all__ = [
    "NUMBA_PARTNER_CONTINUATION_API_MATURITY",
    "NUMBA_PARTNER_CONTINUATION_CLAIM_BOUNDARY",
    "NUMBA_PARTNER_CONTINUATION_CONTRACT_VERSION",
    "NUMBA_PARTNER_CONTINUATION_PUBLIC_OPERATIONS",
    "NumbaPartnerContinuationPlan",
    "NumbaPartnerContinuationResult",
    "describe_numba_partner_continuation_contract",
    "numba_partner_continuation",
    "run_numba_partner_continuation",
    "validate_numba_partner_continuation_contract",
]
