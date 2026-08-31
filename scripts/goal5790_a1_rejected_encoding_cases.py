"""CPU contract tranche for the Goal5790-A1 rejected-encoding suite.

This module intentionally does *not* compile or execute GPU code.  It freezes
six small, application-neutral counterexamples and independently binds:

* the source bytes inspected for the case;
* the semantic contract and its oracle source;
* the counterfactual physical guarantee; and
* the stable rule that must reject the semantic/physical pairing.

The CPU evaluators recompute both the required answer and the answer produced
by the unsafe transform.  The JSON reader is deliberately strict: duplicate
keys, non-finite numbers, schema drift, stale digests, authority substitution,
and even internally re-signed substitutions fail closed.

No record emitted here is executable authority.  A later GPU tranche must use
an isolated, non-registrable test bypass and must independently demonstrate a
real OptiX receipt before making the three-column rejected-program claim.
"""

from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "rtdl.goal5790_a1.rejected_encoding_cases.cpu_contract.v1"
U64_MODULUS = 1 << 64

POLICY_KEYS = (
    "exactness",
    "multiplicity",
    "numeric_precision",
    "order_policy",
    "overflow_policy",
    "tie_policy",
)

CASE_IDS = (
    "builtin_triangle.discrete_interval_boundary.v1",
    "builtin_triangle.deterministic_tie_rank.v1",
    "builtin_triangle.checked_u64_overflow.v1",
    "builtin_triangle.weighted_multiplicity.v1",
    "builtin_triangle.front_back_orientation.v1",
    "custom_aabb.closed_boundary.v1",
)


class RejectedEncodingContractError(ValueError):
    """Fail-closed error for malformed or unauthorised suite evidence."""


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _file_sha256(path: str) -> str:
    resolved = ROOT / path
    if not resolved.is_file():
        raise RejectedEncodingContractError(f"source authority path is absent: {path}")
    return hashlib.sha256(resolved.read_bytes()).hexdigest()


def _sealed(payload: Mapping[str, object], field: str = "authority_sha256") -> dict[str, object]:
    result = copy.deepcopy(dict(payload))
    result[field] = canonical_sha256(result)
    return result


def _source_authority(*rows: tuple[str, str]) -> dict[str, object]:
    sources = [
        {"role": role, "path": path, "sha256": _file_sha256(path)}
        for role, path in rows
    ]
    return _sealed({
        "authority_kind": "exact_source_bytes_v1",
        "sources": sources,
    })


def _policy(**updates: str) -> dict[str, str]:
    base = {
        "exactness": "declared_domain_exact",
        "multiplicity": "one_output_per_semantic_request",
        "numeric_precision": "declared_integer_and_binary32_domain",
        "order_policy": "semantic_request_order",
        "overflow_policy": "fail_closed_before_integer_wraparound",
        "tie_policy": "deterministic_declared_tie_rule",
    }
    base.update(updates)
    if tuple(sorted(base)) != tuple(sorted(POLICY_KEYS)):
        raise AssertionError("internal policy construction drift")
    return base


def _semantic_authority(
    contract_id: str,
    *,
    oracle_path: str,
    policy: Mapping[str, str],
) -> dict[str, object]:
    return _sealed({
        "authority_kind": "independent_semantic_contract_v1",
        "contract_id": contract_id,
        "oracle_source_path": oracle_path,
        "oracle_source_sha256": _file_sha256(oracle_path),
        "policy": dict(policy),
    })


def _physical_authority(
    encoding_id: str,
    *,
    source_authority_sha256: str,
    guarantees: Mapping[str, str],
    orientation_mapping: Mapping[str, str] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "authority_kind": "counterfactual_physical_guarantee_v1",
        "encoding_id": encoding_id,
        "source_authority_sha256": source_authority_sha256,
        "guarantees": dict(guarantees),
        "orientation_mapping": (
            None if orientation_mapping is None else dict(orientation_mapping)
        ),
    }
    return _sealed(payload)


def _case(
    *,
    case_id: str,
    geometry_family: str,
    sources: Sequence[tuple[str, str]],
    semantic_contract_id: str,
    oracle_path: str,
    semantic_policy: Mapping[str, str],
    physical_encoding_id: str,
    physical_guarantees: Mapping[str, str],
    expected_rule_id: str,
    minimal_witness: Mapping[str, object],
    oracle_kind: str,
    unsafe_transform: Mapping[str, object],
    orientation_mapping: Mapping[str, str] | None = None,
) -> dict[str, object]:
    source_authority = _source_authority(*sources)
    semantic = _semantic_authority(
        semantic_contract_id,
        oracle_path=oracle_path,
        policy=semantic_policy,
    )
    physical = _physical_authority(
        physical_encoding_id,
        source_authority_sha256=str(source_authority["authority_sha256"]),
        guarantees=physical_guarantees,
        orientation_mapping=orientation_mapping,
    )
    expected, counterfactual = evaluate_case(case_id, minimal_witness)
    payload: dict[str, object] = {
        "case_id": case_id,
        "geometry_family": geometry_family,
        "source_authority": source_authority,
        "semantic_authority": semantic,
        "physical_authority": physical,
        "expected_rule_id": expected_rule_id,
        "minimal_witness": copy.deepcopy(dict(minimal_witness)),
        "independent_oracle": {
            "oracle_kind": oracle_kind,
            "oracle_source_sha256": semantic["oracle_source_sha256"],
            "expected_output": expected,
        },
        "unsafe_transform": {
            **copy.deepcopy(dict(unsafe_transform)),
            "scope": "test_only_nonregistrable_counterfactual",
            "production_authority_minted": False,
        },
        "counterfactual_execution": {
            "execution_scope": "cpu_recomputation_only__gpu_not_executed",
            "counterfactual_output": counterfactual,
            "oracle_mismatch": counterfactual != expected,
            "valid_optix_receipt_claimed": False,
        },
    }
    payload["case_sha256"] = canonical_sha256(payload)
    return payload


def _leftmost_range_minimum(values: Sequence[int], left: int, right: int) -> int:
    if not values or left < 0 or right < left or right >= len(values):
        raise RejectedEncodingContractError("invalid closed interval witness")
    return min(range(left, right + 1), key=lambda index: (values[index], index))


def _orientation(a: tuple[Fraction, Fraction], b: tuple[Fraction, Fraction],
                 p: tuple[Fraction, Fraction]) -> Fraction:
    return (b[0] - a[0]) * (p[1] - a[1]) \
        - (b[1] - a[1]) * (p[0] - a[0])


def _point_in_closed_triangle(
    point: tuple[Fraction, Fraction],
    vertices: tuple[
        tuple[Fraction, Fraction],
        tuple[Fraction, Fraction],
        tuple[Fraction, Fraction],
    ],
) -> bool:
    signs = tuple(
        _orientation(vertices[index], vertices[(index + 1) % 3], point)
        for index in range(3)
    )
    return not (any(value < 0 for value in signs) and any(value > 0 for value in signs))


def _discrete_interval_physical(
    values: Sequence[int],
    left: int,
    right: int,
    *,
    boundary_coordinates: bool,
    reverse_equal_value_ties: bool,
) -> int:
    count = len(values)
    if count == 0 or left < 0 or right < left or right >= count:
        raise RejectedEncodingContractError("invalid discrete interval physical witness")
    order = sorted(
        range(count),
        key=lambda index: (
            values[index], -index if reverse_equal_value_ties else index),
    )
    rank = {index: position + 1 for position, index in enumerate(order)}
    if boundary_coordinates:
        point = (Fraction(left, count), Fraction(right, count))
    else:
        point = (
            Fraction(2 * left + 1, 2 * count),
            Fraction(2 * right - 1, 2 * count),
        )
    candidates: list[int] = []
    for index in range(count):
        lower = Fraction(index - 1, count)
        upper = Fraction(index + 1, count)
        triangle = ((upper, lower), (upper, Fraction(2)), (Fraction(-1), lower))
        if _point_in_closed_triangle(point, triangle):
            candidates.append(index)
    if not candidates:
        raise RejectedEncodingContractError("counterfactual interval ray missed every triangle")
    return min(candidates, key=lambda index: rank[index])


def _vector_sub(left: Sequence[Fraction], right: Sequence[Fraction]) -> tuple[Fraction, ...]:
    return tuple(a - b for a, b in zip(left, right))


def _cross(left: Sequence[Fraction], right: Sequence[Fraction]) -> tuple[Fraction, Fraction, Fraction]:
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def _dot(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def _orientation_projection(witness: Mapping[str, object], *, swapped: bool) -> list[int]:
    vertices = tuple(
        tuple(Fraction(value) for value in row)
        for row in _sequence(witness.get("vertices"), "vertices")
    )
    triangle_raw = _sequence(witness.get("triangle"), "triangle")
    if len(vertices) != 3 or len(triangle_raw) != 3:
        raise RejectedEncodingContractError("orientation witness requires one triangle")
    triangle = tuple(_strict_int(value, "triangle index") for value in triangle_raw)
    if sorted(triangle) != [0, 1, 2]:
        raise RejectedEncodingContractError("orientation triangle indices are invalid")
    origin = tuple(Fraction(value) for value in _sequence(witness.get("ray_origin"), "ray_origin"))
    direction = tuple(Fraction(value) for value in _sequence(witness.get("ray_direction"), "ray_direction"))
    if len(origin) != 3 or len(direction) != 3:
        raise RejectedEncodingContractError("orientation ray must be three-dimensional")
    a, b, c = (vertices[index] for index in triangle)
    normal = _cross(_vector_sub(b, a), _vector_sub(c, a))
    denominator = _dot(normal, direction)
    if denominator == 0:
        raise RejectedEncodingContractError("orientation witness ray is parallel")
    distance = _dot(normal, _vector_sub(a, origin)) / denominator
    if distance < 0:
        raise RejectedEncodingContractError("orientation witness hit is behind the ray")
    front_value = _strict_int(witness.get("front_value"), "front_value")
    back_value = _strict_int(witness.get("back_value"), "back_value")
    if swapped:
        front_value, back_value = back_value, front_value
    is_front = denominator < 0
    selected = front_value if is_front else back_value
    neighbor = back_value if is_front else front_value
    return [selected, neighbor, 0]


def _closed_aabb_overlap(left: Sequence[int], right: Sequence[int], *, strict: bool) -> bool:
    if len(left) != 5 or len(right) != 5:
        raise RejectedEncodingContractError("AABB witness rows must have four bounds and one ID")
    if strict:
        return left[0] < right[2] and left[2] > right[0] \
            and left[1] < right[3] and left[3] > right[1]
    return left[0] <= right[2] and left[2] >= right[0] \
        and left[1] <= right[3] and left[3] >= right[1]


def _sequence(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise RejectedEncodingContractError(f"{label} must be a JSON array")
    return value


def _strict_int(value: object, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise RejectedEncodingContractError(f"{label} must be an integer")
    return value


def evaluate_case(case_id: str, witness: Mapping[str, object]) -> tuple[object, object]:
    """Independently recompute semantic and unsafe-counterfactual outputs."""

    if case_id == CASE_IDS[0]:
        values = [_strict_int(value, "values[]") for value in _sequence(witness.get("values"), "values")]
        interval = _sequence(witness.get("interval"), "interval")
        if len(interval) != 2:
            raise RejectedEncodingContractError("interval must contain left and right")
        left, right = (_strict_int(value, "interval[]") for value in interval)
        expected = _leftmost_range_minimum(values, left, right)
        observed = _discrete_interval_physical(
            values, left, right,
            boundary_coordinates=True,
            reverse_equal_value_ties=False,
        )
        return expected, observed
    if case_id == CASE_IDS[1]:
        values = [_strict_int(value, "values[]") for value in _sequence(witness.get("values"), "values")]
        interval = _sequence(witness.get("interval"), "interval")
        if len(interval) != 2:
            raise RejectedEncodingContractError("interval must contain left and right")
        left, right = (_strict_int(value, "interval[]") for value in interval)
        expected = _leftmost_range_minimum(values, left, right)
        observed = _discrete_interval_physical(
            values, left, right,
            boundary_coordinates=False,
            reverse_equal_value_ties=True,
        )
        return expected, observed
    if case_id == CASE_IDS[2]:
        values = [_strict_int(value, "values[]") for value in _sequence(witness.get("values"), "values")]
        weights = [_strict_int(value, "weights[]") for value in _sequence(witness.get("weights"), "weights")]
        if len(values) != len(weights) or not values:
            raise RejectedEncodingContractError("overflow vectors must be nonempty and equal length")
        exact = sum(value * weight for value, weight in zip(values, weights))
        return exact, exact % U64_MODULUS
    if case_id == CASE_IDS[3]:
        values = [_strict_int(value, "values[]") for value in _sequence(witness.get("values"), "values")]
        weights = [_strict_int(value, "weights[]") for value in _sequence(witness.get("weights"), "weights")]
        if len(values) != len(weights) or not values:
            raise RejectedEncodingContractError("multiplicity vectors must be nonempty and equal length")
        return sum(value * weight for value, weight in zip(values, weights)), sum(values)
    if case_id == CASE_IDS[4]:
        return (
            _orientation_projection(witness, swapped=False),
            _orientation_projection(witness, swapped=True),
        )
    if case_id == CASE_IDS[5]:
        source = [_strict_int(value, "source[]") for value in _sequence(witness.get("source"), "source")]
        indexed = [_strict_int(value, "indexed[]") for value in _sequence(witness.get("indexed"), "indexed")]
        expected = [[source[4], indexed[4]]] if _closed_aabb_overlap(source, indexed, strict=False) else []
        observed = [[source[4], indexed[4]]] if _closed_aabb_overlap(source, indexed, strict=True) else []
        return expected, observed
    raise RejectedEncodingContractError(f"unknown rejected-encoding case: {case_id!r}")


def _case_specs() -> tuple[dict[str, object], ...]:
    rmq_oracle = "Paper-reproduction-apps/goal5783-held-out-rtxrmq/independent_oracle.py"
    rmq_physical = "Paper-reproduction-apps/goal5783-held-out-rtxrmq/v4_whole_app.py"
    triangle_semantic = "scripts/goal5776_real_scale_frontdoors.py"
    particle_oracle = "Paper-reproduction-apps/goal5753-held-out-particle-tracking/independent_oracle.py"
    relation_oracle = "scripts/goal5760_m2_consumer_fixtures.py"

    rmq_policy = _policy(
        exactness="exact_for_registered_interior_cell_encoding_domain",
        tie_policy="leftmost_minimum_index",
        numeric_precision="integer_rank_geometry_with_binary32_interior_coordinates",
    )
    weighted_policy = _policy(
        exactness="exact_checked_integer_reduction",
        multiplicity="paper_owned_weighted_hit_multiplicity",
        numeric_precision="u32_inputs_checked_u64_accumulator",
        order_policy="commutative_checked_reduction",
        overflow_policy="fail_closed_before_u64_wraparound",
        tie_policy="not_applicable_scalar",
    )
    orientation_policy = _policy(
        exactness="exact_for_declared_mesh_and_ray_domain",
        multiplicity="one_hit_or_miss_per_query",
        numeric_precision="binary32_triangle_with_pinned_orientation",
        order_policy="query_index_ascending",
        tie_policy="nearest_t_then_min_u32_primitive",
    )
    relation_policy = _policy(
        exactness="inclusive_overlap_exact_for_declared_binary32_domain",
        multiplicity="deduplicated_set",
        numeric_precision="binary32_geometry_with_exact_u32_identity",
        order_policy="lexicographic_u32_pair",
        overflow_policy="fail_closed_capacity_or_counter_overflow",
        tie_policy="ascending_u32_pair",
    )

    return (
        {
            "case_id": CASE_IDS[0],
            "geometry_family": "builtin_triangle",
            "sources": (
                ("semantic_oracle", rmq_oracle),
                ("physical_encoder", rmq_physical),
                ("runtime", "src/rtdsl/v4_triangle_optix_runtime.py"),
            ),
            "semantic_contract_id": "discrete_interval.leftmost_minimum.v1",
            "oracle_path": rmq_oracle,
            "semantic_policy": rmq_policy,
            "physical_encoding_id": "triangle_rank_geometry.boundary_coordinates.v1",
            "physical_guarantees": {
                **rmq_policy,
                "exactness": "not_exact_when_query_coordinates_lie_on_cell_boundaries",
            },
            "expected_rule_id": "semantic_guarantee_mismatch:exactness",
            "minimal_witness": {"values": [0, 2, 1], "interval": [1, 1]},
            "oracle_kind": "closed_interval_leftmost_integer_argmin",
            "unsafe_transform": {
                "transform_id": "replace_interior_half_cell_coordinates_with_exact_cell_boundaries",
                "description": "Use left/n and right/n instead of the two interior half-cell coordinates.",
            },
        },
        {
            "case_id": CASE_IDS[1],
            "geometry_family": "builtin_triangle",
            "sources": (
                ("semantic_oracle", rmq_oracle),
                ("physical_encoder", rmq_physical),
                ("runtime", "src/rtdsl/v4_triangle_optix_runtime.py"),
            ),
            "semantic_contract_id": "discrete_interval.leftmost_minimum.v1",
            "oracle_path": rmq_oracle,
            "semantic_policy": rmq_policy,
            "physical_encoding_id": "triangle_rank_geometry.reverse_equal_value_rank.v1",
            "physical_guarantees": {
                **rmq_policy,
                "tie_policy": "rightmost_minimum_index",
            },
            "expected_rule_id": "semantic_guarantee_mismatch:tie_policy",
            "minimal_witness": {"values": [1, 1], "interval": [0, 1]},
            "oracle_kind": "closed_interval_leftmost_integer_argmin",
            "unsafe_transform": {
                "transform_id": "reverse_index_component_of_equal_value_rank",
                "description": "Rank equal values by descending index while retaining unique, legal triangle distances.",
            },
        },
        {
            "case_id": CASE_IDS[2],
            "geometry_family": "builtin_triangle",
            "sources": (
                ("semantic_contract", triangle_semantic),
                ("physical_continuation", "src/rtdsl/v4_checked_u64_device_reduction.py"),
                ("runtime", "src/rtdsl/v4_triangle_reduction_device_runtime.py"),
            ),
            "semantic_contract_id": "checked_weighted_u64_scalar.v1",
            "oracle_path": triangle_semantic,
            "semantic_policy": weighted_policy,
            "physical_encoding_id": "triangle_weighted_reduction.unchecked_modulo_u64.v1",
            "physical_guarantees": {
                **weighted_policy,
                "overflow_policy": "unchecked_modulo_u64",
            },
            "expected_rule_id": "semantic_guarantee_mismatch:overflow_policy",
            "minimal_witness": {
                "values": [1, 1],
                "weights": [1 << 63, 1 << 63],
            },
            "oracle_kind": "python_unbounded_integer_weighted_sum",
            "unsafe_transform": {
                "transform_id": "trust_provisional_u64_kernel_sum_without_bound_validation",
                "description": "Read the device U64 accumulator without validate_weighted_reduction_summary.",
            },
        },
        {
            "case_id": CASE_IDS[3],
            "geometry_family": "builtin_triangle",
            "sources": (
                ("semantic_contract", triangle_semantic),
                ("physical_schema", "src/rtdsl/v4_triangle_standard_library.py"),
                ("runtime", "src/rtdsl/v4_triangle_reduction_device_runtime.py"),
            ),
            "semantic_contract_id": "weighted_hit_multiplicity.v1",
            "oracle_path": triangle_semantic,
            "semantic_policy": weighted_policy,
            "physical_encoding_id": "triangle_reduction.unweighted_continuation.v1",
            "physical_guarantees": {
                **weighted_policy,
                "multiplicity": "unweighted_hit_multiplicity",
            },
            "expected_rule_id": "semantic_guarantee_mismatch:multiplicity",
            "minimal_witness": {"values": [1, 1], "weights": [2, 3]},
            "oracle_kind": "python_unbounded_integer_weighted_sum",
            "unsafe_transform": {
                "transform_id": "replace_checked_product_sum_with_unweighted_sum",
                "description": "Ignore the declared per-query multiplicands after the same physical hit collection.",
            },
        },
        {
            "case_id": CASE_IDS[4],
            "geometry_family": "builtin_triangle",
            "sources": (
                ("semantic_oracle", particle_oracle),
                ("orientation_authority", "src/rtdsl/v4_typed_physical_schema.py"),
                ("physical_encoder", "Paper-reproduction-apps/goal5753-held-out-particle-tracking/v4_whole_app.py"),
            ),
            "semantic_contract_id": "oriented_face_adjacency_projection.v1",
            "oracle_path": particle_oracle,
            "semantic_policy": orientation_policy,
            "physical_encoding_id": "triangle_adjacency.swapped_front_back.v1",
            "physical_guarantees": orientation_policy,
            "orientation_mapping": {
                "front_hit_selects": "back",
                "back_hit_selects": "front",
            },
            "expected_rule_id": "triangle_orientation_mapping",
            "minimal_witness": {
                # Integer-scaled geometry keeps the ray strictly inside the
                # face, so this case tests orientation rather than edge ties.
                "vertices": [[0, 0, 0], [4, 0, 0], [0, 4, 0]],
                "triangle": [0, 1, 2],
                "ray_origin": [1, 1, 1],
                "ray_direction": [0, 0, -1],
                "front_value": 7,
                "back_value": 9,
            },
            "oracle_kind": "exact_rational_winding_and_front_back_projection",
            "unsafe_transform": {
                "transform_id": "swap_front_and_back_adjacency_buffers",
                "description": "Bind each primitive's back adjacency as front and front adjacency as back.",
            },
        },
        {
            "case_id": CASE_IDS[5],
            "geometry_family": "custom_aabb",
            "sources": (
                ("semantic_oracle", relation_oracle),
                ("physical_callback", "src/rtdsl/v4_box_relation_callback.py"),
                ("runtime", "src/rtdsl/v4_bounded_relation_optix_runtime.py"),
            ),
            "semantic_contract_id": "closed_aabb_relation.v1",
            "oracle_path": relation_oracle,
            "semantic_policy": relation_policy,
            "physical_encoding_id": "custom_aabb.strict_overlap_predicate.v1",
            "physical_guarantees": {
                **relation_policy,
                "exactness": "strict_positive_width_overlap_only",
            },
            "expected_rule_id": "semantic_guarantee_mismatch:exactness",
            "minimal_witness": {
                "source": [0, 0, 1, 1, 0],
                "indexed": [1, 0, 2, 1, 1],
            },
            "oracle_kind": "closed_integer_aabb_intersection",
            "unsafe_transform": {
                "transform_id": "replace_inclusive_comparators_with_strict_comparators",
                "description": "Replace <=/>= edge tests with </>, excluding a legal edge-touch relation.",
            },
        },
    )


def expected_rejection_reasons(case: Mapping[str, object]) -> tuple[str, ...]:
    """Replay the bounded app-neutral rejection rules used by this tranche."""

    semantic = _mapping(case.get("semantic_authority"), "semantic_authority")
    physical = _mapping(case.get("physical_authority"), "physical_authority")
    semantic_policy = _mapping(semantic.get("policy"), "semantic_authority.policy")
    physical_policy = _mapping(physical.get("guarantees"), "physical_authority.guarantees")
    reasons = [
        f"semantic_guarantee_mismatch:{key}"
        for key in POLICY_KEYS
        if semantic_policy.get(key) != physical_policy.get(key)
    ]
    orientation = physical.get("orientation_mapping")
    if orientation is not None:
        mapping = _mapping(orientation, "physical_authority.orientation_mapping")
        if mapping != {
            "front_hit_selects": "front",
            "back_hit_selects": "back",
        }:
            reasons.append("triangle_orientation_mapping")
    return tuple(sorted(reasons))


def build_suite() -> dict[str, object]:
    cases = tuple(_case(**spec) for spec in _case_specs())
    if tuple(case["case_id"] for case in cases) != CASE_IDS:
        raise AssertionError("internal rejected-encoding case order drift")
    for case in cases:
        reasons = expected_rejection_reasons(case)
        if reasons != (case["expected_rule_id"],):
            raise AssertionError(
                f"{case['case_id']} does not have one stable rejection: {reasons!r}"
            )
        if case["counterfactual_execution"]["oracle_mismatch"] is not True:
            raise AssertionError(f"{case['case_id']} is not a real counterexample")
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "cases": list(cases),
    }
    payload["suite_sha256"] = canonical_sha256(payload)
    return payload


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise RejectedEncodingContractError(f"{label} must be a JSON object")
    return value


def _exact_keys(value: Mapping[str, object], expected: set[str], label: str) -> None:
    observed = set(value)
    if observed != expected:
        raise RejectedEncodingContractError(
            f"{label} key mismatch: missing={sorted(expected-observed)!r}, "
            f"extra={sorted(observed-expected)!r}"
        )


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 \
        and all(character in "0123456789abcdef" for character in value)


def _verify_seal(value: Mapping[str, object], field: str, label: str) -> None:
    claimed = value.get(field)
    if not _is_sha256(claimed):
        raise RejectedEncodingContractError(f"{label}.{field} is not a SHA-256")
    unsigned = dict(value)
    del unsigned[field]
    if claimed != canonical_sha256(unsigned):
        raise RejectedEncodingContractError(f"{label} digest mismatch")


def _duplicate_rejecting_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise RejectedEncodingContractError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def strict_json_loads(text: str) -> object:
    def reject_constant(token: str) -> object:
        raise RejectedEncodingContractError(f"non-finite JSON constant: {token}")

    try:
        return json.loads(
            text,
            object_pairs_hook=_duplicate_rejecting_object,
            parse_constant=reject_constant,
        )
    except RejectedEncodingContractError:
        raise
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        raise RejectedEncodingContractError(f"invalid JSON: {error}") from error


def validate_suite(payload: object) -> dict[str, object]:
    root = _mapping(payload, "suite")
    _exact_keys(root, {"schema", "cases", "suite_sha256"}, "suite")
    if root.get("schema") != SCHEMA:
        raise RejectedEncodingContractError("suite schema mismatch")
    _verify_seal(root, "suite_sha256", "suite")
    raw_cases = root.get("cases")
    if not isinstance(raw_cases, list):
        raise RejectedEncodingContractError("suite.cases must be a JSON array")
    if len(raw_cases) != len(CASE_IDS):
        raise RejectedEncodingContractError("suite must contain exactly six cases")

    expected = build_suite()
    expected_by_id = {case["case_id"]: case for case in expected["cases"]}
    observed_ids: list[str] = []
    case_keys = {
        "case_id", "geometry_family", "source_authority",
        "semantic_authority", "physical_authority", "expected_rule_id",
        "minimal_witness", "independent_oracle", "unsafe_transform",
        "counterfactual_execution", "case_sha256",
    }
    for index, raw_case in enumerate(raw_cases):
        case = _mapping(raw_case, f"cases[{index}]")
        _exact_keys(case, case_keys, f"cases[{index}]")
        _verify_seal(case, "case_sha256", f"cases[{index}]")
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or case_id not in expected_by_id:
            raise RejectedEncodingContractError(f"unknown case ID: {case_id!r}")
        if case_id in observed_ids:
            raise RejectedEncodingContractError(f"duplicate case ID: {case_id}")
        observed_ids.append(case_id)
        reference = expected_by_id[case_id]

        for authority_name in (
            "source_authority", "semantic_authority", "physical_authority"):
            authority = _mapping(case.get(authority_name), authority_name)
            _verify_seal(authority, "authority_sha256", authority_name)
            if authority != reference[authority_name]:
                raise RejectedEncodingContractError(
                    f"{case_id} {authority_name} independent pin mismatch"
                )
        for immutable_name in (
            "geometry_family", "expected_rule_id", "minimal_witness",
            "unsafe_transform"):
            if case.get(immutable_name) != reference[immutable_name]:
                raise RejectedEncodingContractError(
                    f"{case_id} {immutable_name} authority mismatch"
                )
        reasons = expected_rejection_reasons(case)
        if reasons != (case["expected_rule_id"],):
            raise RejectedEncodingContractError(
                f"{case_id} rejection rule mismatch: {reasons!r}"
            )
        witness = _mapping(case.get("minimal_witness"), "minimal_witness")
        expected_output, counterfactual_output = evaluate_case(case_id, witness)
        oracle = _mapping(case.get("independent_oracle"), "independent_oracle")
        execution = _mapping(case.get("counterfactual_execution"), "counterfactual_execution")
        if oracle != reference["independent_oracle"] \
                or oracle.get("expected_output") != expected_output:
            raise RejectedEncodingContractError(f"{case_id} oracle recomputation mismatch")
        if execution != reference["counterfactual_execution"] \
                or execution.get("counterfactual_output") != counterfactual_output \
                or execution.get("oracle_mismatch") is not True:
            raise RejectedEncodingContractError(
                f"{case_id} counterfactual recomputation mismatch")

    if tuple(observed_ids) != CASE_IDS:
        raise RejectedEncodingContractError("case order/coverage mismatch")
    return copy.deepcopy(dict(root))


def parse_suite_json(text: str) -> dict[str, object]:
    return validate_suite(strict_json_loads(text))


def resign_suite_for_test(payload: Mapping[str, object]) -> dict[str, object]:
    """Mechanically re-sign a mutated suite for adversarial tests only.

    This helper deliberately has no authority: :func:`validate_suite` compares
    the result against independently reconstructed pins and CPU oracles.
    """

    result = copy.deepcopy(dict(payload))
    raw_cases = result.get("cases")
    if not isinstance(raw_cases, list):
        raise RejectedEncodingContractError("cannot re-sign a suite without cases")
    for raw_case in raw_cases:
        case = _mapping(raw_case, "resign.case")
        for name in ("source_authority", "semantic_authority", "physical_authority"):
            authority = _mapping(case.get(name), f"resign.{name}")
            authority.pop("authority_sha256", None)
            authority["authority_sha256"] = canonical_sha256(authority)
        case.pop("case_sha256", None)
        case["case_sha256"] = canonical_sha256(case)
    result.pop("suite_sha256", None)
    result["suite_sha256"] = canonical_sha256(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    suite = build_suite()
    rendered = json.dumps(suite, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
