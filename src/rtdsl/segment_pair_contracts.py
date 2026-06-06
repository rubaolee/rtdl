from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable


SEGMENT_PAIR_CONTRACT_VERSION = "rtdl.segment_pair_contract.v0.candidate"
SEGMENT_PAIR_STRICT_DENOMINATOR_EPSILON = 1.0e-7
SEGMENT_PAIR_TYPED_OUTPUT_RESIDENCY_VERSION = "rtdl.segment_pair_output_residency.v0.candidate"


@dataclass(frozen=True)
class Segment2DContractInput:
    """Generic finite 2-D segment input for contract fixtures."""

    x0: float
    y0: float
    x1: float
    y1: float


@dataclass(frozen=True)
class SegmentPairIntersectionDecision:
    hit: bool
    ambiguous: bool
    reason: str
    t: float | None = None
    u: float | None = None
    x: float | None = None
    y: float | None = None


@dataclass(frozen=True)
class SegmentPairContractCase:
    name: str
    left: Segment2DContractInput
    right: Segment2DContractInput
    expected_hit: bool
    expected_ambiguous: bool
    category: str
    note: str


SEGMENT_PAIR_ALLOWED_DECISION_REASONS = (
    "non_collinear_endpoint_inclusive_hit",
    "outside_parametric_bounds",
    "denominator_degenerate_or_collinear",
    "non_finite_input",
)


def segment_pair_intersection_strict_v0(
    left: Segment2DContractInput,
    right: Segment2DContractInput,
    *,
    denominator_epsilon: float = SEGMENT_PAIR_STRICT_DENOMINATOR_EPSILON,
) -> SegmentPairIntersectionDecision:
    """Evaluate the candidate strict segment-pair intersection contract.

    This is a contract reference for the current fast RayJoin LSI count route,
    not a public API. It deliberately matches the non-collinear,
    endpoint-inclusive, absolute-denominator predicate used in the current
    CuPy baseline and repaired OptiX fast count path.
    """

    values = (left.x0, left.y0, left.x1, left.y1, right.x0, right.y0, right.x1, right.y1)
    if any(not isfinite(value) for value in values):
        return SegmentPairIntersectionDecision(False, True, "non_finite_input")

    rx = left.x1 - left.x0
    ry = left.y1 - left.y0
    sx = right.x1 - right.x0
    sy = right.y1 - right.y0
    denom = rx * sy - ry * sx
    if abs(denom) < denominator_epsilon:
        return SegmentPairIntersectionDecision(False, True, "denominator_degenerate_or_collinear")

    qpx = right.x0 - left.x0
    qpy = right.y0 - left.y0
    t = (qpx * sy - qpy * sx) / denom
    u = (qpx * ry - qpy * rx) / denom
    if t < 0.0 or t > 1.0 or u < 0.0 or u > 1.0:
        return SegmentPairIntersectionDecision(False, False, "outside_parametric_bounds", t=t, u=u)

    return SegmentPairIntersectionDecision(
        True,
        False,
        "non_collinear_endpoint_inclusive_hit",
        t=t,
        u=u,
        x=left.x0 + t * rx,
        y=left.y0 + t * ry,
    )


def segment_pair_contract_adversarial_cases() -> tuple[SegmentPairContractCase, ...]:
    """Return app-free adversarial fixtures for the candidate v0 contract."""

    return (
        SegmentPairContractCase(
            name="proper_crossing",
            left=Segment2DContractInput(0.0, 0.0, 1.0, 1.0),
            right=Segment2DContractInput(0.0, 1.0, 1.0, 0.0),
            expected_hit=True,
            expected_ambiguous=False,
            category="proper",
            note="Interior crossing must be counted.",
        ),
        SegmentPairContractCase(
            name="endpoint_touch",
            left=Segment2DContractInput(0.0, 0.0, 1.0, 0.0),
            right=Segment2DContractInput(1.0, 0.0, 1.0, 1.0),
            expected_hit=True,
            expected_ambiguous=False,
            category="endpoint",
            note="Endpoint-inclusive t/u bounds count this hit.",
        ),
        SegmentPairContractCase(
            name="outside_bounds_same_lines",
            left=Segment2DContractInput(0.0, 0.0, 1.0, 1.0),
            right=Segment2DContractInput(2.0, 0.0, 3.0, -1.0),
            expected_hit=False,
            expected_ambiguous=False,
            category="outside",
            note="The infinite lines cross outside the finite segment intervals.",
        ),
        SegmentPairContractCase(
            name="parallel_disjoint",
            left=Segment2DContractInput(0.0, 0.0, 1.0, 0.0),
            right=Segment2DContractInput(0.0, 1.0, 1.0, 1.0),
            expected_hit=False,
            expected_ambiguous=True,
            category="parallel",
            note="Parallel pairs are excluded from the v0 fast count contract.",
        ),
        SegmentPairContractCase(
            name="collinear_overlap",
            left=Segment2DContractInput(0.0, 0.0, 2.0, 0.0),
            right=Segment2DContractInput(1.0, 0.0, 3.0, 0.0),
            expected_hit=False,
            expected_ambiguous=True,
            category="collinear",
            note="Collinear overlap is not counted by the current v0 contract.",
        ),
        SegmentPairContractCase(
            name="near_parallel_below_abs_epsilon",
            left=Segment2DContractInput(0.0, 0.0, 1.0, 0.0),
            right=Segment2DContractInput(0.0, 1.0e-8, 1.0, 2.0e-8),
            expected_hit=False,
            expected_ambiguous=True,
            category="near_parallel",
            note="Absolute denominator policy excludes near-parallel pairs below 1e-7.",
        ),
        SegmentPairContractCase(
            name="tiny_degenerate_left",
            left=Segment2DContractInput(0.0, 0.0, 0.0, 0.0),
            right=Segment2DContractInput(0.0, -1.0, 0.0, 1.0),
            expected_hit=False,
            expected_ambiguous=True,
            category="degenerate",
            note="Zero-length segments fall into the excluded denominator-degenerate bucket.",
        ),
    )


def validate_segment_pair_contract_cases(
    cases: Iterable[SegmentPairContractCase] | None = None,
) -> dict[str, object]:
    """Validate the executable adversarial fixture set for the v0 contract."""

    selected_cases = tuple(cases or segment_pair_contract_adversarial_cases())
    failures: list[dict[str, object]] = []
    categories: set[str] = set()
    reasons: set[str] = set()
    for case in selected_cases:
        categories.add(case.category)
        decision = segment_pair_intersection_strict_v0(case.left, case.right)
        reasons.add(decision.reason)
        if decision.reason not in SEGMENT_PAIR_ALLOWED_DECISION_REASONS:
            failures.append({"case": case.name, "error": f"unexpected reason {decision.reason}"})
        if decision.hit != case.expected_hit or decision.ambiguous != case.expected_ambiguous:
            failures.append(
                {
                    "case": case.name,
                    "expected_hit": case.expected_hit,
                    "actual_hit": decision.hit,
                    "expected_ambiguous": case.expected_ambiguous,
                    "actual_ambiguous": decision.ambiguous,
                    "reason": decision.reason,
                }
            )

    required_categories = {"proper", "endpoint", "outside", "parallel", "collinear", "near_parallel", "degenerate"}
    missing_categories = tuple(sorted(required_categories - categories))
    if missing_categories:
        failures.append({"case": "fixture_set", "missing_categories": missing_categories})

    return {
        "version": SEGMENT_PAIR_CONTRACT_VERSION,
        "valid": not failures,
        "case_count": len(selected_cases),
        "categories": tuple(sorted(categories)),
        "decision_reasons": tuple(sorted(reasons)),
        "failures": tuple(failures),
        "public_api_specification": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "claim_boundary": (
            "candidate executable primitive contract only; not a public API specification, "
            "not release evidence, not RayJoin paper reproduction, and not public speedup wording"
        ),
    }


def segment_pair_left_id_dense_count_output_residency_contract(
    *,
    group_capacity: int,
    counts_device_ptr: int | None = None,
    overflow_device_ptr: int | None = None,
    ambiguous_count_device_ptr: int | None = None,
    stream_ordering: str = "not_proven",
    device_id: int = 0,
    owner: object | None = None,
) -> dict[str, object]:
    """Describe the candidate typed output columns for left-id dense counts.

    This helper intentionally reuses the generic primitive payload descriptor
    and neutral-buffer seam machinery. It does not allocate buffers and does not
    authorize zero-copy. It only makes the segment-pair contract's residency
    target executable and testable.
    """

    if int(group_capacity) <= 0:
        raise ValueError("group_capacity must be positive")
    from .hit_stream_handoff import describe_primitive_payload_column_descriptor

    columns = (
        _segment_pair_output_column_descriptor(
            describe_primitive_payload_column_descriptor,
            name="segment_pair_left_id_counts",
            dtype="int64",
            shape=(int(group_capacity),),
            semantic_role="partner_output",
            data_ptr=counts_device_ptr,
            stream_ordering=stream_ordering,
            device_id=device_id,
            owner=owner,
        ),
        _segment_pair_output_column_descriptor(
            describe_primitive_payload_column_descriptor,
            name="segment_pair_overflow_status",
            dtype="uint32",
            shape=(1,),
            semantic_role="status_counter",
            data_ptr=overflow_device_ptr,
            stream_ordering=stream_ordering,
            device_id=device_id,
            owner=owner,
        ),
        _segment_pair_output_column_descriptor(
            describe_primitive_payload_column_descriptor,
            name="segment_pair_ambiguous_count",
            dtype="uint64",
            shape=(1,),
            semantic_role="status_counter",
            data_ptr=ambiguous_count_device_ptr,
            stream_ordering=stream_ordering,
            device_id=device_id,
            owner=owner,
        ),
    )
    device_resident_columns = sum(1 for column in columns if column["data_ptr_observed"])
    any_fallback = any(bool(column["fallback_required"]) for column in columns)
    return {
        "version": SEGMENT_PAIR_TYPED_OUTPUT_RESIDENCY_VERSION,
        "primitive_contract_version": SEGMENT_PAIR_CONTRACT_VERSION,
        "primitive": "segment_pair_left_id_dense_count",
        "schema": "dense_grouped_count_i64_plus_status_columns",
        "group_capacity": int(group_capacity),
        "columns": columns,
        "device_resident_column_count": device_resident_columns,
        "all_columns_device_resident": device_resident_columns == len(columns),
        "fallback_required": any_fallback,
        "ambiguous_count_required": True,
        "overflow_status_required": True,
        "stream_ordering": stream_ordering,
        "true_zero_copy_authorized": False,
        "public_speedup_claim_authorized": False,
        "release_authorized": False,
        "claim_boundary": (
            "candidate typed output residency contract only; descriptors may record "
            "device-resident pointers, but this does not authorize true-zero-copy, "
            "public speedup wording, release readiness, or automatic partner selection"
        ),
    }


def validate_segment_pair_output_residency_contract(contract: dict[str, object]) -> dict[str, object]:
    errors: list[str] = []
    if contract.get("version") != SEGMENT_PAIR_TYPED_OUTPUT_RESIDENCY_VERSION:
        errors.append("unexpected segment-pair output residency version")
    if contract.get("primitive_contract_version") != SEGMENT_PAIR_CONTRACT_VERSION:
        errors.append("unexpected segment-pair primitive contract version")
    if contract.get("primitive") != "segment_pair_left_id_dense_count":
        errors.append("unexpected segment-pair output primitive")
    if int(contract.get("group_capacity", 0)) <= 0:
        errors.append("group_capacity must be positive")
    columns = tuple(contract.get("columns", ()))
    if len(columns) != 3:
        errors.append("segment-pair output contract must expose exactly three columns")
    required_names = {
        "segment_pair_left_id_counts",
        "segment_pair_overflow_status",
        "segment_pair_ambiguous_count",
    }
    names = {str(column.get("name", "")) for column in columns if isinstance(column, dict)}
    if names != required_names:
        errors.append("segment-pair output column set changed")
    for column in columns:
        if not isinstance(column, dict):
            errors.append("segment-pair output columns must be descriptor metadata dictionaries")
            continue
        if column.get("true_zero_copy_authorized") is not False:
            errors.append(f"{column.get('name')} must not authorize true zero-copy")
        if column.get("public_speedup_claim_authorized") is not False:
            errors.append(f"{column.get('name')} must not authorize public speedup")
        seam = column.get("neutral_buffer_seam")
        if not isinstance(seam, dict):
            errors.append(f"{column.get('name')} must include neutral_buffer_seam metadata")
        elif seam.get("zero_copy_claim_authorized") is not False:
            errors.append(f"{column.get('name')} neutral seam must not authorize zero-copy")
    for false_flag in ("true_zero_copy_authorized", "public_speedup_claim_authorized", "release_authorized"):
        if contract.get(false_flag) is not False:
            errors.append(f"{false_flag} must remain false")
    if "not authorize true-zero-copy" not in str(contract.get("claim_boundary", "")):
        errors.append("claim boundary must block true-zero-copy wording")
    return {
        "version": SEGMENT_PAIR_TYPED_OUTPUT_RESIDENCY_VERSION,
        "valid": not errors,
        "errors": tuple(errors),
        "column_count": len(columns),
        "all_columns_device_resident": bool(contract.get("all_columns_device_resident")),
        "fallback_required": bool(contract.get("fallback_required")),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "true_zero_copy_authorized": False,
    }


def _segment_pair_output_column_descriptor(
    describe_column,
    *,
    name: str,
    dtype: str,
    shape: tuple[int, ...],
    semantic_role: str,
    data_ptr: int | None,
    stream_ordering: str,
    device_id: int,
    owner: object | None,
) -> dict[str, object]:
    has_device_ptr = data_ptr is not None and int(data_ptr) > 0
    return describe_column(
        name=name,
        dtype=dtype,
        shape=shape,
        semantic_role=semantic_role,
        producer="segment_pair_intersection_rows_2d",
        consumer="caller_selected_partner_or_native_reduction",
        device_type="cuda" if has_device_ptr else "cpu",
        device_id=int(device_id),
        data_ptr=int(data_ptr) if has_device_ptr else None,
        source_protocol="native_cuda_device_pointer" if has_device_ptr else "host_reference",
        access_mode="read",
        mutability="mutable" if has_device_ptr else "immutable",
        stream_ordering=stream_ordering,
        lifetime_state="producer_retained" if has_device_ptr else "caller_retained",
        transfer_status="borrowed_device_pointer_unmeasured" if has_device_ptr else "host_reference",
        fallback_reason="none" if has_device_ptr else "host_reference",
        capacity_elements=int(shape[0]),
        owner=owner,
        host_materialized_before_handoff=not has_device_ptr,
        native_producer=has_device_ptr,
        measured_same_pointer=False,
        measured_no_host_stage=False,
    )
