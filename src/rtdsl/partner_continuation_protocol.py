from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from .partner_protocol import RtdlBufferDescriptor
from .partner_protocol import V2_4_FORBIDDEN_NATIVE_APP_TOKENS
from .partner_protocol import V2_4_PARTNER_PROTOCOL_VERSION
from .partner_protocol import validate_phase_timing_record


V2_5_PARTNER_CONTINUATION_VERSION = "rtdl.partner_continuation.v2.5"
V2_5_PRIMARY_PARTNER = "triton"
V2_5_FALLBACK_PARTNER = "numba"
V2_5_REFERENCE_PARTNER = "python_reference"
V2_5_CONFORMANCE_PARTNER = "cupy_conformance"
V2_5_ALLOWED_PARTNERS = (
    V2_5_REFERENCE_PARTNER,
    V2_5_PRIMARY_PARTNER,
    V2_5_FALLBACK_PARTNER,
    V2_5_CONFORMANCE_PARTNER,
)
V2_5_PARTNER_ROLES = (
    "preparation",
    "partner_continuation",
    "reduction",
    "compaction",
    "finalization",
)
V2_5_STATUS_REFERENCE_CONTRACT = "reference_contract"
V2_5_STATUS_PARTNER_DESCRIPTOR_ONLY = "partner_descriptor_only"
V2_5_STATUS_PREVIEW_NOT_PROMOTED = "preview_not_promoted"
V2_5_ALLOWED_STATUSES = (
    V2_5_STATUS_REFERENCE_CONTRACT,
    V2_5_STATUS_PARTNER_DESCRIPTOR_ONLY,
    V2_5_STATUS_PREVIEW_NOT_PROMOTED,
)
V2_5_PERFORMANCE_PATH_AUTHORIZED = False
V2_5_RT_TRAVERSAL_REPLACEMENT_ALLOWED = False
V2_5_RAWKERNEL_REQUIRED_ALLOWED = False


class PartnerContinuationOverflowError(RuntimeError):
    """Raised when a bounded continuation would silently drop exact rows."""


@dataclass(frozen=True)
class RtdlPartnerContinuationOperation:
    name: str
    category: str
    input_names: tuple[str, ...]
    output_names: tuple[str, ...]
    behavior: str
    deterministic: bool = True
    app_specific_semantics_allowed: bool = False

    def to_metadata(self) -> dict[str, object]:
        return {
            "name": self.name,
            "category": self.category,
            "input_names": self.input_names,
            "output_names": self.output_names,
            "behavior": self.behavior,
            "deterministic": self.deterministic,
            "app_specific_semantics_allowed": self.app_specific_semantics_allowed,
        }


V2_5_PARTNER_CONTINUATION_OPERATIONS: tuple[RtdlPartnerContinuationOperation, ...] = (
    RtdlPartnerContinuationOperation(
        name="segmented_count_i64",
        category="segmented_reduction",
        input_names=("group_ids", "group_count"),
        output_names=("counts",),
        behavior="count int64 rows per integer group id",
    ),
    RtdlPartnerContinuationOperation(
        name="segmented_sum_f64",
        category="segmented_reduction",
        input_names=("group_ids", "values", "group_count"),
        output_names=("sums",),
        behavior="sum float64 values per integer group id",
    ),
    RtdlPartnerContinuationOperation(
        name="compact_mask_i64",
        category="compaction",
        input_names=("values", "mask"),
        output_names=("values", "original_indices"),
        behavior="compact int64 values by a boolean mask while preserving source indices",
    ),
    RtdlPartnerContinuationOperation(
        name="bounded_collect_finalize_i64",
        category="bounded_finalization",
        input_names=("group_ids", "item_ids", "group_count", "k"),
        output_names=("group_ids", "item_ids", "row_offsets"),
        behavior="finalize bounded int64 rows per group with fail-closed overflow",
    ),
    RtdlPartnerContinuationOperation(
        name="grouped_argmin_f64",
        category="ranked_summary",
        input_names=("group_ids", "item_ids", "scores", "group_count"),
        output_names=("group_ids", "item_ids", "scores", "missing_group_ids"),
        behavior="select the lowest-score item per group with deterministic item-id tie-break",
    ),
)

V2_5_PARTNER_CONTINUATION_OPERATION_NAMES = tuple(
    operation.name for operation in V2_5_PARTNER_CONTINUATION_OPERATIONS
)


@dataclass(frozen=True)
class RtdlPartnerContinuationSpec:
    operation: str
    partner: str = V2_5_REFERENCE_PARTNER
    input_buffers: tuple[RtdlBufferDescriptor, ...] = ()
    output_buffers: tuple[RtdlBufferDescriptor, ...] = ()
    status: str = V2_5_STATUS_REFERENCE_CONTRACT
    phase: str = "partner_continuation"
    replaces_rt_traversal: bool = False
    raw_kernel_required: bool = False
    promoted_performance_path: bool = False
    app_specific_semantics_allowed: bool = False

    def __post_init__(self) -> None:
        _validate_operation_name(self.operation)
        normalized_partner = _normalize_partner(self.partner)
        _validate_partner(normalized_partner)
        _validate_status(self.status)
        if self.phase not in V2_5_PARTNER_ROLES:
            raise ValueError("partner continuation phase is not a v2.5 partner-owned role")
        if self.replaces_rt_traversal:
            raise ValueError("v2.5 partners must not replace RTDL/OptiX RT traversal")
        if self.raw_kernel_required:
            raise ValueError("v2.5 Triton/Numba path must not require CuPy RawKernel-style user code")
        if self.promoted_performance_path:
            raise ValueError("v2.5 first slice does not authorize promoted performance paths")
        if self.app_specific_semantics_allowed:
            raise ValueError("partner continuation specs must remain app-agnostic")
        if normalized_partner != V2_5_REFERENCE_PARTNER and self.status == V2_5_STATUS_REFERENCE_CONTRACT:
            raise ValueError("non-reference partners are descriptor-only until implementation evidence exists")
        object.__setattr__(self, "partner", normalized_partner)
        _validate_buffer_names(self.input_buffers, self.output_buffers)

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract_version": V2_5_PARTNER_CONTINUATION_VERSION,
            "operation": self.operation,
            "operation_category": _operation_by_name(self.operation).category,
            "partner": self.partner,
            "input_buffers": tuple(buffer.to_metadata() for buffer in self.input_buffers),
            "output_buffers": tuple(buffer.to_metadata() for buffer in self.output_buffers),
            "status": self.status,
            "phase": self.phase,
            "partner_roles": V2_5_PARTNER_ROLES,
            "replaces_rt_traversal": self.replaces_rt_traversal,
            "raw_kernel_required": self.raw_kernel_required,
            "promoted_performance_path": self.promoted_performance_path,
            "app_specific_semantics_allowed": self.app_specific_semantics_allowed,
            "rt_traversal_contract_version": V2_4_PARTNER_PROTOCOL_VERSION,
            "claim_boundary": (
                "v2.5 partner continuations own preparation/reduction/compaction/"
                "finalization around RTDL primitives; they do not replace RTDL/OptiX traversal"
            ),
        }


def v2_5_partner_continuation_contract() -> dict[str, object]:
    return {
        "contract_version": V2_5_PARTNER_CONTINUATION_VERSION,
        "primary_partner": V2_5_PRIMARY_PARTNER,
        "fallback_partner": V2_5_FALLBACK_PARTNER,
        "reference_partner": V2_5_REFERENCE_PARTNER,
        "conformance_partner": V2_5_CONFORMANCE_PARTNER,
        "allowed_partners": V2_5_ALLOWED_PARTNERS,
        "partner_roles": V2_5_PARTNER_ROLES,
        "operations": tuple(operation.to_metadata() for operation in V2_5_PARTNER_CONTINUATION_OPERATIONS),
        "performance_path_authorized": V2_5_PERFORMANCE_PATH_AUTHORIZED,
        "rt_traversal_replacement_allowed": V2_5_RT_TRAVERSAL_REPLACEMENT_ALLOWED,
        "rawkernel_required_allowed": V2_5_RAWKERNEL_REQUIRED_ALLOWED,
        "native_engine_app_specific_vocab_allowed": False,
        "phase_timing_required": True,
    }


def validate_v2_5_partner_continuation_contract(
    contract: Mapping[str, object] | None = None,
) -> dict[str, object]:
    contract = v2_5_partner_continuation_contract() if contract is None else contract
    errors: list[str] = []
    if contract.get("contract_version") != V2_5_PARTNER_CONTINUATION_VERSION:
        errors.append("unexpected v2.5 partner-continuation contract version")
    if contract.get("primary_partner") != V2_5_PRIMARY_PARTNER:
        errors.append("v2.5 must remain Triton-first")
    if contract.get("fallback_partner") != V2_5_FALLBACK_PARTNER:
        errors.append("v2.5 must retain Numba fallback")
    if tuple(contract.get("allowed_partners", ())) != V2_5_ALLOWED_PARTNERS:
        errors.append("v2.5 allowed partner order changed unexpectedly")
    if tuple(contract.get("partner_roles", ())) != V2_5_PARTNER_ROLES:
        errors.append("v2.5 partner roles changed unexpectedly")
    operation_names = tuple(
        str(operation.get("name"))
        for operation in contract.get("operations", ())
        if isinstance(operation, Mapping)
    )
    if operation_names != V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
        errors.append("v2.5 operation set changed unexpectedly")
    for operation in contract.get("operations", ()):
        if not isinstance(operation, Mapping):
            errors.append("v2.5 operations must be metadata mappings")
            continue
        name = str(operation.get("name", ""))
        for token in V2_4_FORBIDDEN_NATIVE_APP_TOKENS:
            if token in name.lower():
                errors.append(f"operation contains app-specific token `{token}`")
        if operation.get("app_specific_semantics_allowed") is not False:
            errors.append(f"operation {name} must reject app-specific semantics")
    if contract.get("performance_path_authorized") is not False:
        errors.append("first v2.5 slice must not authorize a promoted performance path")
    if contract.get("rt_traversal_replacement_allowed") is not False:
        errors.append("Triton/Numba must not replace RT traversal for RT-core claims")
    if contract.get("rawkernel_required_allowed") is not False:
        errors.append("v2.5 ease-of-use path must not require CuPy RawKernel-style code")
    if contract.get("native_engine_app_specific_vocab_allowed") is not False:
        errors.append("native app-specific vocabulary must remain rejected")
    if contract.get("phase_timing_required") is not True:
        errors.append("v2.5 partner continuation paths require phase timing")
    return {
        "status": "accept" if not errors else "reject",
        "contract_version": contract.get("contract_version"),
        "primary_partner": contract.get("primary_partner"),
        "fallback_partner": contract.get("fallback_partner"),
        "operation_names": operation_names,
        "errors": tuple(errors),
    }


def plan_v2_5_partner_continuation(
    operation: str,
    *,
    available_partners: Iterable[str] = (),
    preferred_partner: str = V2_5_PRIMARY_PARTNER,
    fallback_partner: str = V2_5_FALLBACK_PARTNER,
) -> RtdlPartnerContinuationSpec:
    """Select the v2.5 partner shape without claiming executable GPU evidence."""

    _validate_operation_name(operation)
    preferred = _normalize_partner(preferred_partner)
    fallback = _normalize_partner(fallback_partner)
    _validate_partner(preferred)
    _validate_partner(fallback)
    available = tuple(_normalize_partner(partner) for partner in available_partners)
    if preferred in available:
        partner = preferred
    elif fallback in available:
        partner = fallback
    elif V2_5_CONFORMANCE_PARTNER in available:
        partner = V2_5_CONFORMANCE_PARTNER
    else:
        partner = V2_5_REFERENCE_PARTNER
    status = (
        V2_5_STATUS_REFERENCE_CONTRACT
        if partner == V2_5_REFERENCE_PARTNER
        else V2_5_STATUS_PARTNER_DESCRIPTOR_ONLY
    )
    return RtdlPartnerContinuationSpec(
        operation=operation,
        partner=partner,
        status=status,
    )


def execute_v2_5_partner_continuation_reference(
    operation: str,
    inputs: Mapping[str, object],
) -> dict[str, object]:
    """CPU/Python reference semantics for v2.5 generic continuation ops."""

    _validate_operation_name(operation)
    if operation == "segmented_count_i64":
        group_count = _required_int(inputs, "group_count")
        group_ids = _required_i64_sequence(inputs, "group_ids")
        counts = _segmented_count(group_ids, group_count)
        outputs = {"counts": counts}
    elif operation == "segmented_sum_f64":
        group_count = _required_int(inputs, "group_count")
        group_ids = _required_i64_sequence(inputs, "group_ids")
        values = _required_f64_sequence(inputs, "values")
        if len(group_ids) != len(values):
            raise ValueError("group_ids and values must have the same length")
        outputs = {"sums": _segmented_sum(group_ids, values, group_count)}
    elif operation == "compact_mask_i64":
        values = _required_i64_sequence(inputs, "values")
        mask = _required_bool_sequence(inputs, "mask")
        if len(values) != len(mask):
            raise ValueError("values and mask must have the same length")
        compact_values = [value for value, keep in zip(values, mask) if keep]
        original_indices = [index for index, keep in enumerate(mask) if keep]
        outputs = {"values": compact_values, "original_indices": original_indices}
    elif operation == "bounded_collect_finalize_i64":
        group_count = _required_int(inputs, "group_count")
        k = _required_int(inputs, "k")
        total_row_capacity = inputs.get("total_row_capacity")
        group_ids = _required_i64_sequence(inputs, "group_ids")
        item_ids = _required_i64_sequence(inputs, "item_ids")
        outputs = _bounded_collect(group_ids, item_ids, group_count, k, total_row_capacity)
    elif operation == "grouped_argmin_f64":
        group_count = _required_int(inputs, "group_count")
        group_ids = _required_i64_sequence(inputs, "group_ids")
        item_ids = _required_i64_sequence(inputs, "item_ids")
        scores = _required_f64_sequence(inputs, "scores")
        if not (len(group_ids) == len(item_ids) == len(scores)):
            raise ValueError("group_ids, item_ids, and scores must have the same length")
        outputs = _grouped_argmin(group_ids, item_ids, scores, group_count)
    else:  # pragma: no cover - guarded by _validate_operation_name
        raise ValueError(f"unsupported v2.5 partner continuation operation: {operation}")

    timing = {
        "phases_sec": {"partner_continuation": 0.0},
        "promoted_performance_path": False,
        "same_phase_contract_as_basis": False,
    }
    return {
        "contract_version": V2_5_PARTNER_CONTINUATION_VERSION,
        "operation": operation,
        "partner": V2_5_REFERENCE_PARTNER,
        "outputs": outputs,
        "phase_timing_validation": validate_phase_timing_record(timing),
        "promoted_performance_path": False,
        "rt_core_speedup_claim_authorized": False,
    }


def _bounded_collect(
    group_ids: Sequence[int],
    item_ids: Sequence[int],
    group_count: int,
    k: int,
    total_row_capacity: object,
) -> dict[str, list[int]]:
    if k <= 0:
        raise ValueError("k must be positive")
    if len(group_ids) != len(item_ids):
        raise ValueError("group_ids and item_ids must have the same length")
    buckets: list[list[int]] = [[] for _ in range(group_count)]
    for group, item in zip(group_ids, item_ids):
        _validate_group_id(group, group_count)
        bucket = buckets[group]
        if len(bucket) >= k:
            raise PartnerContinuationOverflowError(
                "bounded_collect_finalize_i64 overflowed per-group capacity; "
                "failure_mode=fail_closed_overflow; partial_result_returned=False"
            )
        bucket.append(int(item))
    total_rows = sum(len(bucket) for bucket in buckets)
    if total_row_capacity is not None and total_rows > int(total_row_capacity):
        raise PartnerContinuationOverflowError(
            "bounded_collect_finalize_i64 overflowed total row capacity; "
            "failure_mode=fail_closed_overflow; partial_result_returned=False"
        )
    out_groups: list[int] = []
    out_items: list[int] = []
    offsets = [0]
    for group, bucket in enumerate(buckets):
        for item in bucket:
            out_groups.append(group)
            out_items.append(item)
        offsets.append(len(out_items))
    return {"group_ids": out_groups, "item_ids": out_items, "row_offsets": offsets}


def _grouped_argmin(
    group_ids: Sequence[int],
    item_ids: Sequence[int],
    scores: Sequence[float],
    group_count: int,
) -> dict[str, list[int] | list[float]]:
    best: list[tuple[float, int] | None] = [None] * group_count
    for group, item, score in zip(group_ids, item_ids, scores):
        _validate_group_id(group, group_count)
        candidate = (float(score), int(item))
        current = best[group]
        if current is None or candidate < current:
            best[group] = candidate
    out_groups: list[int] = []
    out_items: list[int] = []
    out_scores: list[float] = []
    missing: list[int] = []
    for group, candidate in enumerate(best):
        if candidate is None:
            missing.append(group)
            continue
        score, item = candidate
        out_groups.append(group)
        out_items.append(item)
        out_scores.append(score)
    return {
        "group_ids": out_groups,
        "item_ids": out_items,
        "scores": out_scores,
        "missing_group_ids": missing,
    }


def _segmented_count(group_ids: Sequence[int], group_count: int) -> list[int]:
    counts = [0] * group_count
    for group in group_ids:
        _validate_group_id(group, group_count)
        counts[group] += 1
    return counts


def _segmented_sum(group_ids: Sequence[int], values: Sequence[float], group_count: int) -> list[float]:
    sums = [0.0] * group_count
    for group, value in zip(group_ids, values):
        _validate_group_id(group, group_count)
        sums[group] += float(value)
    return sums


def _required_i64_sequence(inputs: Mapping[str, object], name: str) -> list[int]:
    if name not in inputs:
        raise ValueError(f"missing required input `{name}`")
    value = inputs[name]
    if isinstance(value, (str, bytes)):
        raise ValueError(f"{name} must be a sequence of integers")
    return [int(item) for item in value]  # type: ignore[arg-type]


def _required_f64_sequence(inputs: Mapping[str, object], name: str) -> list[float]:
    if name not in inputs:
        raise ValueError(f"missing required input `{name}`")
    value = inputs[name]
    if isinstance(value, (str, bytes)):
        raise ValueError(f"{name} must be a sequence of floats")
    return [float(item) for item in value]  # type: ignore[arg-type]


def _required_bool_sequence(inputs: Mapping[str, object], name: str) -> list[bool]:
    if name not in inputs:
        raise ValueError(f"missing required input `{name}`")
    value = inputs[name]
    if isinstance(value, (str, bytes)):
        raise ValueError(f"{name} must be a sequence of booleans")
    return [bool(item) for item in value]  # type: ignore[arg-type]


def _required_int(inputs: Mapping[str, object], name: str) -> int:
    if name not in inputs:
        raise ValueError(f"missing required input `{name}`")
    value = int(inputs[name])  # type: ignore[arg-type]
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
    return value


def _validate_group_id(group: int, group_count: int) -> None:
    if group < 0 or group >= group_count:
        raise ValueError("group ids must be in [0, group_count)")


def _validate_operation_name(name: str) -> None:
    normalized = str(name)
    if normalized not in V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
        raise ValueError(f"unsupported v2.5 partner continuation operation: {name}")
    for token in V2_4_FORBIDDEN_NATIVE_APP_TOKENS:
        if token in normalized.lower():
            raise ValueError(f"operation contains app-specific token `{token}`")


def _operation_by_name(name: str) -> RtdlPartnerContinuationOperation:
    for operation in V2_5_PARTNER_CONTINUATION_OPERATIONS:
        if operation.name == name:
            return operation
    raise ValueError(f"unsupported v2.5 partner continuation operation: {name}")


def _normalize_partner(partner: str) -> str:
    return str(partner).strip().lower().replace("-", "_")


def _validate_partner(partner: str) -> None:
    if _normalize_partner(partner) not in V2_5_ALLOWED_PARTNERS:
        raise ValueError(f"unsupported v2.5 partner: {partner}")


def _validate_status(status: str) -> None:
    if status not in V2_5_ALLOWED_STATUSES:
        raise ValueError(f"unsupported v2.5 partner continuation status: {status}")


def _validate_buffer_names(
    input_buffers: tuple[RtdlBufferDescriptor, ...],
    output_buffers: tuple[RtdlBufferDescriptor, ...],
) -> None:
    names = [buffer.name for buffer in (*input_buffers, *output_buffers)]
    if len(names) != len(set(names)):
        raise ValueError("partner continuation buffer names must be unique")
