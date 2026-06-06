from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable


SEGMENT_PAIR_CONTRACT_VERSION = "rtdl.segment_pair_contract.v0.candidate"
SEGMENT_PAIR_STRICT_DENOMINATOR_EPSILON = 1.0e-7


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
