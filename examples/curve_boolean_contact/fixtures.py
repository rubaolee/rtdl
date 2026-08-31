"""Frozen Goal5834-B1 fixtures and canonical scene normalization.

This file is evaluation support.  It imports no RTDL module and performs no
GPU work.  The public worker receives only the canonical static/query bytes
emitted here; it never receives the expected Boolean or pairwise geometry.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct

from .independent_oracle import evaluate_scene, f32, f32_bits, f64_bits


EVALUATION_MARGIN = 2.0 ** -10
DIRECTION_CROSS_RATIO_MARGIN = 2.0 ** -12
ENTRY_ENDPOINT_MARGIN = 2.0 ** -12
CANONICAL_QUERY_ENVELOPE = 2.0 ** 20


def _f32_from_bits(value: int) -> float:
    return struct.unpack("<f", struct.pack("<I", int(value)))[0]


def _capsule(start, end, radius, identity):
    return (tuple(start), tuple(end), float(radius), int(identity))


def _fixture(family_id, capsules, queries, *, note, execution_id=None):
    return {
        "family_id": family_id,
        "execution_id": execution_id or family_id,
        "capsules": tuple(capsules),
        "queries": tuple((tuple(start), tuple(end)) for start, end in queries),
        "note": note,
    }


BASE_LARGE_TRANSLATION = _fixture(
    "large_translation_metamorphic_pair",
    (_capsule((0.0, -1.0, 0.0), (0.0, 1.0, 0.0), 0.125, 4),),
    (((-4.0, 0.0, 0.0), (4.0, 0.0, 0.0)),),
    note="base member of the normalization metamorphic pair",
    execution_id="large_translation_base",
)


def _translate_scale_fixture(fixture, *, scale, translation, execution_id):
    def point(value):
        return tuple(translation[index] + scale * value[index]
                     for index in range(3))
    return _fixture(
        fixture["family_id"],
        tuple(_capsule(
            point(start), point(end), scale * radius, identity)
            for start, end, radius, identity in fixture["capsules"]),
        tuple((point(start), point(end)) for start, end in fixture["queries"]),
        note="power-of-two scaled and translated member of the metamorphic pair",
        execution_id=execution_id,
    )


EXECUTABLE_FIXTURES = (
    _fixture(
        "single_crossing_hit",
        (_capsule((0, -1, 0), (0, 1, 0), 0.25, 1),),
        (((-1, 0, 0), (1, 0, 0)),),
        note="one edge crosses one swept capsule",
    ),
    _fixture(
        "clear_miss",
        (_capsule((0, -1, 0), (0, 1, 0), 0.25, 2),),
        (((-1, 0, 1), (1, 0, 1)),),
        note="one edge has robust clearance",
    ),
    _fixture(
        "round_endcap_hit",
        (_capsule((0, 0, 0), (0, 1, 0), 0.25, 3),),
        (((-1, -0.20, 0), (1, -0.20, 0)),),
        note="contact is through the rounded start cap, not the cylindrical side",
    ),
    _fixture(
        "piecewise_linear_or",
        (
            _capsule((0, -1, 0), (0, 0, 0), 0.20, 10),
            _capsule((0, 0, 0), (1, 0, 0), 0.20, 11),
        ),
        (
            ((-1, 0, 1), (1, 0, 1)),
            ((0.5, -1, 0), (0.5, 1, 0)),
            ((-1, -1, 1), (-1, 1, 1)),
        ),
        note="two swept path segments and three edges; exactly one edge hits",
    ),
    _fixture(
        "multiple_robust_hits",
        (
            _capsule((0, -1, 0), (0, 1, 0), 0.20, 20),
            _capsule((0.5, -1, 0), (0.5, 1, 0), 0.20, 21),
        ),
        (((-1, 0, 0), (1, 0, 0)),),
        note="one edge robustly intersects two capsules; output remains Boolean",
    ),
    BASE_LARGE_TRANSLATION,
    _translate_scale_fixture(
        BASE_LARGE_TRANSLATION,
        scale=2.0 ** 20,
        translation=(2.0 ** 40, -(2.0 ** 39), 2.0 ** 38),
        execution_id="large_translation_transformed",
    ),
    _fixture(
        "face_interior_only_boundary",
        (_capsule((0, 0, -1), (0, 0, 1), 0.10, 30),),
        (
            ((-2, -2, 0), (2, -2, 0)),
            ((2, -2, 0), (0, 2, 0)),
            ((0, 2, 0), (-2, -2, 0)),
        ),
        note=("the swept capsule crosses the triangle face interior, but no "
              "registered triangle edge; the implemented edge predicate is MISS"),
    ),
    _fixture(
        "ordinary_provider_t_disagreement_regression",
        (_capsule((-2, -1, 1), (-1, 1, 2), 0.2, 555),),
        (((
            -0.9590878702997561, 1.1931053085886383, 1.9541103637013393,
        ), (
            2.4671945820539714, -2.85371731402841, -1.7223614664107387,
        )),),
        note="Goal5834 exact-t counterexample retained as a Boolean HIT",
    ),
    _fixture(
        "near_coincident_id_disagreement_regression",
        (
            _capsule(
                (-2, -1, 1), (-1, 1, 2), _f32_from_bits(0x3E4CCCCE), 1000),
            _capsule(
                (-2, -1, 1), (-1, 1, 2), _f32_from_bits(0x3E4CCCCD), 1),
        ),
        (((
            -2.391265976033713, -1.1123559085756902, 0.9287584731586094,
        ), (
            1.7186848663858152, -1.1347605412858597, 0.9746184002928722,
        )),),
        note="Goal5834 unstable-winner counterexample retained as a Boolean HIT",
    ),
    _fixture(
        "float32_tie_id_disagreement_regression",
        (
            _capsule((0, -1, 0), (0, 1, 0), 0.25, 100),
            _capsule((0.01, -1, 0), (0.01, 1, 0), 0.25, 1),
        ),
        (((-1.0e6, 0, 0), (1.0e6, 0, 0)),),
        note="Goal5834 float32 tie-order case retained as a Boolean HIT",
    ),
)


BOUNDARY_FIXTURES = (
    _fixture(
        "start_inside_ineligible",
        (_capsule((0, -1, 0), (0, 1, 0), 0.25, 90),),
        (((0, 0, 0), (1, 0, 0)),),
        note="query starts inside the swept capsule",
    ),
    _fixture(
        "near_tangent_parallel_ineligible",
        (_capsule((0, -1, 0), (0, 1, 0), 0.25, 91),),
        (((0.25001, -2, 0), (0.25002, 2, 0)),),
        note="near-tangent and near-parallel input lies outside the frozen margin",
    ),
)


def _canonical_bytes(value) -> bytes:
    return (json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def _sha(value) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _float64_input_projection(fixture):
    return {
        "capsules": [[
            [f64_bits(value) for value in start],
            [f64_bits(value) for value in end],
            f64_bits(radius), identity,
        ] for start, end, radius, identity in fixture["capsules"]],
        "queries": [[
            [f64_bits(value) for value in start],
            [f64_bits(value) for value in end],
        ] for start, end in fixture["queries"]],
    }


def _float32_input_projection(capsules, queries):
    return {
        "capsules": [[
            [f32_bits(value) for value in start],
            [f32_bits(value) for value in end],
            f32_bits(radius), identity,
        ] for start, end, radius, identity in capsules],
        "queries": [[
            [f32_bits(value) for value in start],
            [f32_bits(value) for value in end],
        ] for start, end in queries],
    }


def _power_of_two_ceiling(value: float) -> float:
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError("positive finite normalization extent required")
    mantissa, exponent = math.frexp(value)
    return math.ldexp(1.0, exponent - 1 if mantissa == 0.5 else exponent)


def normalize_fixture(fixture):
    capsules = fixture["capsules"]
    if not capsules:
        raise ValueError("at least one capsule is required")
    lower = [math.inf, math.inf, math.inf]
    upper = [-math.inf, -math.inf, -math.inf]
    for start, end, radius, _identity in capsules:
        if not math.isfinite(radius) or radius <= 0.0:
            raise ValueError("positive finite capsule radius required")
        for point in (start, end):
            if len(point) != 3 or not all(math.isfinite(value) for value in point):
                raise ValueError("finite vec3 capsule endpoints required")
            for axis in range(3):
                lower[axis] = min(lower[axis], point[axis] - radius)
                upper[axis] = max(upper[axis], point[axis] + radius)
    origin = tuple(
        lower[axis] + (upper[axis] - lower[axis]) / 2.0
        for axis in range(3))
    largest = max(
        [abs(point[axis] - origin[axis])
         for start, end, _radius, _identity in capsules
         for point in (start, end) for axis in range(3)]
        + [radius for _start, _end, radius, _identity in capsules])
    scale = _power_of_two_ceiling(largest)

    def point(value):
        if len(value) != 3 or not all(math.isfinite(item) for item in value):
            raise ValueError("finite vec3 query endpoints required")
        transformed = tuple(f32((value[axis] - origin[axis]) / scale)
                            for axis in range(3))
        if not all(math.isfinite(item) for item in transformed) \
                or max(abs(item) for item in transformed) > CANONICAL_QUERY_ENVELOPE:
            raise ValueError("query lies outside the frozen canonical envelope")
        return transformed

    canonical_capsules = []
    for start, end, radius, identity in capsules:
        normalized_radius = f32(radius / scale)
        if not math.isfinite(normalized_radius) or normalized_radius <= 0.0:
            raise ValueError("normalized radius underflowed or is nonpositive")
        canonical_capsules.append(
            (point(start), point(end), normalized_radius, identity))
    canonical_queries = tuple(
        (point(start), point(end)) for start, end in fixture["queries"])
    if any(start == end for start, end in canonical_queries):
        raise ValueError("canonical query segment must be nonzero")
    return {
        "origin": origin,
        "origin_f64_bits": tuple(f64_bits(value) for value in origin),
        "scale": scale,
        "scale_f64_bits": f64_bits(scale),
        "capsules": tuple(canonical_capsules),
        "queries": canonical_queries,
        "original_input_sha256": _sha(_float64_input_projection(fixture)),
        "normalized_input_sha256": _sha(_float32_input_projection(
            canonical_capsules, canonical_queries)),
    }


def _qualify(canonical_result):
    reasons = []
    for row in canonical_result["pair_rows"]:
        if row["decision_separation"] < EVALUATION_MARGIN:
            reasons.append("DECISION_SEPARATION_BELOW_2^-10")
        if not row["both_query_endpoints_outside"]:
            reasons.append("QUERY_ENDPOINT_INSIDE_CAPSULE")
        if row["hit"]:
            if row["direction_cross_ratio"] < DIRECTION_CROSS_RATIO_MARGIN:
                reasons.append("CONTACT_DIRECTION_CROSS_RATIO_BELOW_2^-12")
            entry = row["entry_parameter"]
            if entry is None or entry < ENTRY_ENDPOINT_MARGIN \
                    or entry > 1.0 - ENTRY_ENDPOINT_MARGIN:
                reasons.append("CONTACT_ENTRY_OUTSIDE_ENDPOINT_MARGIN")
    return tuple(sorted(set(reasons)))


def evaluate_fixture(fixture):
    normalized = normalize_fixture(fixture)
    original = evaluate_scene(fixture["capsules"], fixture["queries"])
    canonical = evaluate_scene(normalized["capsules"], normalized["queries"])
    reasons = _qualify(canonical)
    return {
        "family_id": fixture["family_id"],
        "execution_id": fixture["execution_id"],
        "note": fixture["note"],
        "original_input": {
            "capsules": fixture["capsules"],
            "queries": fixture["queries"],
        },
        "normalization": normalized,
        "original_oracle": original,
        "canonical_oracle": canonical,
        "oracle_boolean_equal": original["collision"] == canonical["collision"],
        "eligibility": "ELIGIBLE" if not reasons else "INELIGIBLE",
        "ineligibility_reasons": reasons,
    }


def runtime_static_input(evaluation):
    capsules = evaluation["normalization"]["capsules"]
    control_points = []
    widths = []
    segment_indices = []
    application_ids = []
    for start, end, radius, identity in capsules:
        segment_indices.append(len(control_points))
        control_points.extend((start, end))
        widths.extend((radius, radius))
        application_ids.append(identity)
    return {
        "control_points": tuple(control_points),
        "widths": tuple(widths),
        "segment_indices": tuple(segment_indices),
        "application_ids": tuple(application_ids),
    }


def build_evaluation_manifest():
    executable = tuple(evaluate_fixture(item) for item in EXECUTABLE_FIXTURES)
    boundary = tuple(evaluate_fixture(item) for item in BOUNDARY_FIXTURES)
    if len({row["family_id"] for row in executable}) != 10:
        raise RuntimeError("exactly ten executable fixture families required")
    if len(executable) != 11:
        raise RuntimeError("large-translation pair must yield eleven executions")
    if any(row["eligibility"] != "ELIGIBLE" for row in executable):
        failed = [(row["execution_id"], row["ineligibility_reasons"])
                  for row in executable if row["eligibility"] != "ELIGIBLE"]
        raise RuntimeError(f"intended executable fixture is ineligible: {failed!r}")
    if any(not row["oracle_boolean_equal"] for row in executable):
        raise RuntimeError("original and canonical fixture oracles differ")
    if any(row["eligibility"] != "INELIGIBLE" for row in boundary):
        raise RuntimeError("boundary fixture unexpectedly became eligible")
    first, second = executable[5], executable[6]
    if first["normalization"]["normalized_input_sha256"] != \
            second["normalization"]["normalized_input_sha256"]:
        raise RuntimeError("large-translation normalized bytes are not identical")
    return {
        "schema": "rtdl.goal5834_b1.frozen_boolean_fixture_manifest.v1",
        "evaluation_margin_exact": "2^-10",
        "direction_cross_ratio_margin_exact": "2^-12",
        "entry_endpoint_margin_exact": "2^-12",
        "fixture_family_count": 10,
        "concrete_gpu_execution_count": 11,
        "evaluator_ineligible_execution_count": 2,
        "malformed_prelaunch_rejection_count": 1,
        "generalization_exam_count": 0,
        "corpus_kind": "AUTHOR_DESIGNED_CONVENIENCE_AND_ADVERSARIAL",
        "executable": executable,
        "boundary": boundary,
    }


__all__ = [
    "BOUNDARY_FIXTURES", "CANONICAL_QUERY_ENVELOPE",
    "DIRECTION_CROSS_RATIO_MARGIN", "ENTRY_ENDPOINT_MARGIN",
    "EVALUATION_MARGIN", "EXECUTABLE_FIXTURES", "build_evaluation_manifest",
    "evaluate_fixture", "normalize_fixture", "runtime_static_input",
]
