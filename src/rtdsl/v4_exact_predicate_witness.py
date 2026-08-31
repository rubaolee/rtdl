"""Closed exact-predicate and witness composition for V4.

The physical producer remains a verified OptiX traversal.  This module owns
the deterministic semantic completion that a local floating-point hit cannot
prove:

* per-query nearest rows to one global directed-Hausdorff witness;
* RayJoin's scaled-integer simulation-of-simplicity point location; and
* RayJoin's scaled-integer segment-pair predicate plus grouped counts.

There is no user reducer, comparator, predicate callback, application name, or
publication identity in the executable contract.  The closed algebras below
are trusted language partners.  They recompute exact predicates from bounded
integer inputs and never treat the OptiX broad phase as final authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
import re
from typing import Iterable, Mapping, Sequence

import numpy as np


EXACT_COMPOSITION_SCHEMA_ID = (
    "https://rtdl.dev/schemas/v4-exact-predicate-witness-composition-v1.json"
)
EXACT_COMPOSITION_SCHEMA_VERSION = "v1"
U32_MAX = (1 << 32) - 1
U64_MAX = (1 << 64) - 1
RAYJOIN_COORDINATE_BITS = 46
RAYJOIN_COORDINATE_MIN = -(1 << RAYJOIN_COORDINATE_BITS)
RAYJOIN_COORDINATE_MAX = (1 << RAYJOIN_COORDINATE_BITS) - 1


class ExactCompositionError(ValueError):
    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(
            f"V4 exact-predicate/witness rejected: {code}@{path}: {message}")


def _fail(code: str, path: str, message: str) -> None:
    raise ExactCompositionError(code, path, message)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


class ExactPartnerAlgebra(str, Enum):
    GLOBAL_MAX_NEAREST_WITNESS_F32 = "global_max_nearest_witness_f32_v1"
    DIRECTED_POINT_LOCATION_SOS_I46 = "directed_point_location_sos_i46_v1"
    SEGMENT_PAIR_GROUPED_COUNT_SOS_I46 = (
        "segment_pair_grouped_count_sos_i46_v1"
    )


class CandidateProducerKind(str, Enum):
    SPHERE_NEAREST = "verified_sphere_nearest_candidate_relation_v1"
    CLOSED_AABB_RELATION = "verified_closed_aabb_candidate_relation_v1"


@dataclass(frozen=True)
class ExactPredicateWitnessSchema:
    callback_ir_sha256: str
    effect_digest: str
    physical_schema_sha256: str
    source_authority_nonce: str
    producer_kind: CandidateProducerKind
    partner_algebras: tuple[ExactPartnerAlgebra, ...]
    maximum_candidate_capacity: int
    coordinate_bits: int = RAYJOIN_COORDINATE_BITS
    schema_id: str = EXACT_COMPOSITION_SCHEMA_ID
    schema_version: str = EXACT_COMPOSITION_SCHEMA_VERSION

    def semantic_dict(self) -> dict[str, object]:
        return {
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "physical_schema_sha256": self.physical_schema_sha256,
            "source_authority_nonce": self.source_authority_nonce,
            "producer_kind": self.producer_kind.value,
            "partner_algebras": [item.value for item in self.partner_algebras],
            "maximum_candidate_capacity": self.maximum_candidate_capacity,
            "coordinate_bits": self.coordinate_bits,
            "candidate_rows_are_final_authority": False,
            "exact_predicates_recomputed_after_traversal": True,
            "raw_device_order_is_semantic": False,
            "overflow_policy": "fail_closed_reject_complete_result",
            "arbitrary_user_predicate_reducer_or_comparator_allowed": False,
        }

    @property
    def schema_sha256(self) -> str:
        return _digest(self.semantic_dict())

    def to_dict(self) -> dict[str, object]:
        return {**self.semantic_dict(), "schema_sha256": self.schema_sha256}


@dataclass(frozen=True)
class VerifiedExactPredicateWitnessAuthority:
    schema: ExactPredicateWitnessSchema
    authority_nonce: str


def verify_exact_predicate_witness_schema(
    *,
    callback_ir_sha256: str,
    effect_digest: str,
    physical_schema_sha256: str,
    source_authority_nonce: str,
    schema: ExactPredicateWitnessSchema,
) -> VerifiedExactPredicateWitnessAuthority:
    for label, value in (
        ("callback_ir_sha256", callback_ir_sha256),
        ("effect_digest", effect_digest),
        ("physical_schema_sha256", physical_schema_sha256),
        ("source_authority_nonce", source_authority_nonce),
    ):
        if re.fullmatch(r"[0-9a-f]{64}", value) is None:
            _fail("identity", label, "lower-case sha256 identity required")
    if schema.schema_id != EXACT_COMPOSITION_SCHEMA_ID \
            or schema.schema_version != EXACT_COMPOSITION_SCHEMA_VERSION:
        _fail("schema_identity", "schema", "unsupported schema")
    if (
        schema.callback_ir_sha256 != callback_ir_sha256
        or schema.effect_digest != effect_digest
        or schema.physical_schema_sha256 != physical_schema_sha256
        or schema.source_authority_nonce != source_authority_nonce
    ):
        _fail("identity_binding", "schema", "exact producer authority required")
    if not isinstance(schema.producer_kind, CandidateProducerKind):
        _fail("producer_kind", "schema", "closed producer enum required")
    if not isinstance(schema.maximum_candidate_capacity, int) \
            or isinstance(schema.maximum_candidate_capacity, bool) \
            or not 1 <= schema.maximum_candidate_capacity <= U32_MAX:
        _fail("capacity", "schema", "positive u32 capacity required")
    if schema.coordinate_bits != RAYJOIN_COORDINATE_BITS:
        _fail("coordinate_bits", "schema", "exact signed 46-bit domain required")
    if not schema.partner_algebras \
            or len(set(schema.partner_algebras)) != len(schema.partner_algebras) \
            or not all(isinstance(item, ExactPartnerAlgebra)
                       for item in schema.partner_algebras):
        _fail("partner_algebras", "schema", "nonempty unique closed algebras required")
    allowed = (
        (ExactPartnerAlgebra.GLOBAL_MAX_NEAREST_WITNESS_F32,)
        if schema.producer_kind is CandidateProducerKind.SPHERE_NEAREST
        else (
            ExactPartnerAlgebra.DIRECTED_POINT_LOCATION_SOS_I46,
            ExactPartnerAlgebra.SEGMENT_PAIR_GROUPED_COUNT_SOS_I46,
        )
    )
    if schema.partner_algebras != allowed:
        _fail(
            "producer_algebra_binding", "schema",
            f"{schema.producer_kind.value} requires {[item.value for item in allowed]}",
        )
    nonce = _digest({
        "kind": "verified_exact_predicate_witness_authority_v1",
        "schema": schema.schema_sha256,
        "source_authority": source_authority_nonce,
    })
    return VerifiedExactPredicateWitnessAuthority(schema, nonce)


@dataclass(frozen=True)
class NearestStateRow:
    query_id: int
    item_id: int
    rank: int
    distance_squared: float


def global_max_nearest_witness_f32(
    rows: Iterable[Sequence[object]],
    *,
    expected_query_ids: Sequence[int],
    source_ids: Sequence[int] | None = None,
) -> dict[str, object]:
    """Reduce exact one-nearest rows to a deterministic global witness.

    Ties are distance descending, then source ID ascending, then item ID
    ascending.  Every expected query must contribute exactly one rank-1 row.
    """

    queries = tuple(int(value) for value in expected_query_ids)
    if not queries or len(set(queries)) != len(queries) \
            or any(value < 0 or value > U32_MAX for value in queries):
        _fail("query_domain", "expected_query_ids", "unique nonempty u32 IDs required")
    sources = queries if source_ids is None else tuple(int(value) for value in source_ids)
    if len(sources) != len(queries) or len(set(sources)) != len(sources) \
            or any(value < 0 or value > U32_MAX for value in sources):
        _fail("source_domain", "source_ids", "one unique u32 source ID per query required")
    source_by_query = dict(zip(queries, sources))
    nearest: dict[int, NearestStateRow] = {}
    for index, raw in enumerate(rows):
        if len(raw) != 4:
            _fail("row_shape", f"rows[{index}]", "query,item,rank,distance_squared required")
        query_id, item_id, rank = int(raw[0]), int(raw[1]), int(raw[2])
        distance_squared = float(raw[3])
        if query_id not in source_by_query or not 0 <= item_id <= U32_MAX:
            _fail("row_domain", f"rows[{index}]", "row identity outside verified domain")
        if rank != 1:
            _fail("rank", f"rows[{index}]", "exactly one rank-1 row is required")
        if not math.isfinite(distance_squared) or distance_squared < 0.0:
            _fail("distance", f"rows[{index}]", "finite nonnegative distance squared required")
        if query_id in nearest:
            _fail("duplicate_query", f"rows[{index}]", "one nearest row per query required")
        nearest[query_id] = NearestStateRow(
            query_id, item_id, rank, distance_squared)
    missing = tuple(query for query in queries if query not in nearest)
    if missing:
        _fail("incomplete_query_coverage", "rows", repr(missing))
    winner = min(
        nearest.values(),
        key=lambda row: (
            -row.distance_squared,
            source_by_query[row.query_id],
            row.item_id,
        ),
    )
    value = math.sqrt(winner.distance_squared)
    return {
        "source_index": queries.index(winner.query_id),
        "source_id": source_by_query[winner.query_id],
        "item_id": winner.item_id,
        "value": value,
        "distance_squared": winner.distance_squared,
        "per_query_nearest": tuple(
            (row.query_id, source_by_query[row.query_id], row.item_id,
             row.distance_squared)
            for row in (nearest[query] for query in queries)
        ),
        "contract": ExactPartnerAlgebra.GLOBAL_MAX_NEAREST_WITNESS_F32.value,
    }


def _u32(value: object, path: str) -> int:
    result = int(value)
    if not 0 <= result <= U32_MAX:
        _fail("u32_domain", path, repr(result))
    return result


def _coord(value: object, path: str) -> int:
    if isinstance(value, bool):
        _fail("coordinate_domain", path, "boolean is not a coordinate")
    result = int(value)
    if result != value or not RAYJOIN_COORDINATE_MIN <= result <= RAYJOIN_COORDINATE_MAX:
        _fail(
            "coordinate_domain", path,
            f"signed {RAYJOIN_COORDINATE_BITS}-bit integer required",
        )
    return result


@dataclass(frozen=True)
class ExactPoint2D:
    point_id: int
    x: int
    y: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "point_id", _u32(self.point_id, "point.point_id"))
        object.__setattr__(self, "x", _coord(self.x, "point.x"))
        object.__setattr__(self, "y", _coord(self.y, "point.y"))


@dataclass(frozen=True)
class ExactSegment2D:
    segment_id: int
    x0: int
    y0: int
    x1: int
    y1: int
    left_face_id: int = 0
    right_face_id: int = 0
    group_id: int = 0

    def __post_init__(self) -> None:
        for field in ("segment_id", "left_face_id", "right_face_id", "group_id"):
            object.__setattr__(self, field, _u32(getattr(self, field), f"segment.{field}"))
        for field in ("x0", "y0", "x1", "y1"):
            object.__setattr__(self, field, _coord(getattr(self, field), f"segment.{field}"))
        if self.x0 == self.x1 and self.y0 == self.y1:
            _fail("degenerate_segment", "segment", "zero-length segment is not admissible")


def _outward_f32(value: int, direction: float) -> float:
    rounded = np.float32(value)
    target = np.float32(-math.inf if direction < 0.0 else math.inf)
    return float(np.nextafter(rounded, target, dtype=np.float32))


def exact_segment_aabb_projection(
    segments: Sequence[ExactSegment2D],
) -> tuple[tuple[float, float, float, float, int], ...]:
    """Compiler-owned conservative AABBs for exact integer segments."""

    _unique_by_id(segments, "segment_id", "segments")
    return tuple(
        (
            _outward_f32(min(row.x0, row.x1), -1.0),
            _outward_f32(min(row.y0, row.y1), -1.0),
            _outward_f32(max(row.x0, row.x1), 1.0),
            _outward_f32(max(row.y0, row.y1), 1.0),
            row.segment_id,
        )
        for row in segments
    )


def exact_vertical_ray_aabb_projection(
    points: Sequence[ExactPoint2D],
    segments: Sequence[ExactSegment2D],
) -> tuple[tuple[float, float, float, float, int], ...]:
    """Compiler-owned conservative upward-ray boxes for point location."""

    _unique_by_id(points, "point_id", "points")
    _unique_by_id(segments, "segment_id", "segments")
    if not segments:
        _fail("empty_index", "segments", "nonempty segment index required")
    maximum_y = max(max(row.y0, row.y1) for row in segments)
    return tuple(
        (
            _outward_f32(row.x, -1.0),
            _outward_f32(row.y, -1.0),
            _outward_f32(row.x, 1.0),
            _outward_f32(max(row.y, maximum_y), 1.0),
            row.point_id,
        )
        for row in points
    )


@dataclass(frozen=True)
class _Line:
    a: int
    b: int
    c: int


def _line(segment: ExactSegment2D) -> _Line:
    a = segment.y0 - segment.y1
    b = segment.x1 - segment.x0
    c = -segment.x0 * a - segment.y0 * b
    if b < 0:
        a, b, c = -a, -b, -c
    return _Line(a, b, c)


def _eval(line: _Line, x: int, y: int) -> int:
    return x * line.a + y * line.b + line.c


def rayjoin_sos_segment_pair_intersects(
    left: ExactSegment2D,
    right: ExactSegment2D,
) -> bool:
    """Exact integer transcription of RayJoin's asymmetric LSI SoS rule."""

    e1, e2 = _line(left), _line(right)
    if (e1.a == 0 and e1.b == 0) or (e2.a == 0 and e2.b == 0):
        return False
    e2p1_e1 = _eval(e1, right.x0, right.y0)
    e2p2_e1 = _eval(e1, right.x1, right.y1)
    e1p1_e2 = _eval(e2, left.x0, left.y0)
    e1p2_e2 = _eval(e2, left.x1, left.y1)

    if e1p1_e2 == 0:
        e1p1_e2 = -e2.a
    if e1p1_e2 == 0:
        e1p1_e2 = -e2.b
    if e1p1_e2 == 0:
        return False
    if e1p2_e2 == 0:
        e1p2_e2 = -e2.a
    if e1p2_e2 == 0:
        e1p2_e2 = -e2.b
    if e1p2_e2 == 0:
        return False
    if (e1p1_e2 > 0) == (e1p2_e2 > 0):
        return False

    if e2p1_e1 == 0:
        e2p1_e1 = e1.a
    if e2p1_e1 == 0:
        e2p1_e1 = e1.b
    if e2p1_e1 == 0:
        return False
    if e2p2_e1 == 0:
        e2p2_e1 = e1.a
    if e2p2_e1 == 0:
        e2p2_e1 = e1.b
    if e2p2_e1 == 0:
        return False
    if (e2p1_e1 > 0) == (e2p2_e1 > 0):
        return False

    same = (
        (left.x0, left.y0, left.x1, left.y1)
        == (right.x0, right.y0, right.x1, right.y1)
        or (left.x0, left.y0, left.x1, left.y1)
        == (right.x1, right.y1, right.x0, right.y0)
    )
    return not same


def _unique_by_id(rows: Sequence[object], field: str, label: str) -> dict[int, object]:
    result: dict[int, object] = {}
    for index, row in enumerate(rows):
        identity = int(getattr(row, field))
        if identity in result:
            _fail("duplicate_identity", f"{label}[{index}]", repr(identity))
        result[identity] = row
    return result


def _candidate_pairs(
    candidates: Iterable[Sequence[int]],
    *,
    left: Mapping[int, object],
    right: Mapping[int, object],
    capacity: int,
) -> tuple[tuple[int, int], ...]:
    if not isinstance(capacity, int) or isinstance(capacity, bool) \
            or not 1 <= capacity <= U32_MAX:
        _fail("capacity", "capacity", "positive u32 capacity required")
    rows: set[tuple[int, int]] = set()
    raw_count = 0
    for index, row in enumerate(candidates):
        raw_count += 1
        if raw_count > capacity:
            _fail("capacity_overflow", "candidates", f"capacity={capacity}")
        if len(row) != 2:
            _fail("candidate_shape", f"candidates[{index}]", "u32 pair required")
        pair = (_u32(row[0], f"candidates[{index}][0]"),
                _u32(row[1], f"candidates[{index}][1]"))
        if pair[0] not in left or pair[1] not in right:
            _fail("candidate_domain", f"candidates[{index}]", repr(pair))
        if pair in rows:
            _fail("duplicate_candidate", f"candidates[{index}]", repr(pair))
        rows.add(pair)
    return tuple(sorted(rows))


def grouped_exact_segment_pair_counts(
    left_segments: Sequence[ExactSegment2D],
    right_segments: Sequence[ExactSegment2D],
    candidates: Iterable[Sequence[int]],
    *,
    capacity: int,
) -> dict[str, object]:
    left = _unique_by_id(left_segments, "segment_id", "left_segments")
    right = _unique_by_id(right_segments, "segment_id", "right_segments")
    pairs = _candidate_pairs(candidates, left=left, right=right, capacity=capacity)
    exact = tuple(
        pair for pair in pairs
        if rayjoin_sos_segment_pair_intersects(left[pair[0]], right[pair[1]])
    )
    counts: dict[tuple[int, int], int] = {}
    for left_id, right_id in exact:
        key = (left[left_id].group_id, right[right_id].group_id)
        value = counts.get(key, 0) + 1
        if value > U64_MAX:
            _fail("count_overflow", "grouped_counts", repr(key))
        counts[key] = value
    return {
        "candidate_pairs": pairs,
        "exact_pairs": exact,
        "grouped_counts": tuple(
            (left_group, right_group, count)
            for (left_group, right_group), count in sorted(counts.items())
        ),
        "candidate_count": len(pairs),
        "exact_count": len(exact),
        "contract": ExactPartnerAlgebra.SEGMENT_PAIR_GROUPED_COUNT_SOS_I46.value,
    }


def _rational_lt(an: int, ad: int, bn: int, bd: int) -> bool:
    return an * bd < bn * ad


def _rational_eq(an: int, ad: int, bn: int, bd: int) -> bool:
    return an * bd == bn * ad


def _point_location_candidate(
    point: ExactPoint2D,
    segment: ExactSegment2D,
    query_map_id: int,
) -> tuple[int, int, int] | None:
    x_min, x_max = sorted((segment.x0, segment.x1))
    excluded = x_min if query_map_id == 0 else x_max
    if point.x < x_min or point.x > x_max or point.x == excluded:
        return None
    line = _line(segment)
    if line.b == 0:
        return None
    numerator = -(line.a * point.x) - line.c
    diff = point.y * line.b - numerator
    if diff == 0:
        diff = -line.a if query_map_id == 0 else line.a
    if diff == 0:
        diff = -line.b if query_map_id == 0 else line.b
    if diff > 0:
        return None
    return numerator, line.b, line.a


def directed_point_location_sos(
    points: Sequence[ExactPoint2D],
    segments: Sequence[ExactSegment2D],
    candidates: Iterable[Sequence[int]],
    *,
    query_map_id: int,
    capacity: int,
) -> dict[str, object]:
    if query_map_id not in (0, 1):
        _fail("query_map_id", "query_map_id", "closed enum {0,1} required")
    point_by_id = _unique_by_id(points, "point_id", "points")
    segment_by_id = _unique_by_id(segments, "segment_id", "segments")
    pairs = _candidate_pairs(
        candidates, left=point_by_id, right=segment_by_id, capacity=capacity)
    by_point: dict[int, list[int]] = {point.point_id: [] for point in points}
    for point_id, segment_id in pairs:
        by_point[point_id].append(segment_id)
    order = {segment.segment_id: index for index, segment in enumerate(segments)}
    output: list[tuple[int, int, int]] = []
    exact_hit_count = 0
    for point in points:
        best: tuple[int, int, int, ExactSegment2D] | None = None
        for segment_id in sorted(by_point[point.point_id], key=order.__getitem__):
            segment = segment_by_id[segment_id]
            candidate = _point_location_candidate(point, segment, query_map_id)
            if candidate is None:
                continue
            exact_hit_count += 1
            numerator, denominator, slope_numerator = candidate
            if best is None:
                best = numerator, denominator, slope_numerator, segment
                continue
            best_n, best_d, best_slope_n, best_segment = best
            better_height = _rational_lt(
                numerator, denominator, best_n, best_d)
            equal_height = _rational_eq(
                numerator, denominator, best_n, best_d)
            better_slope = (
                slope_numerator * best_d > best_slope_n * denominator
                if query_map_id == 0
                else slope_numerator * best_d <= best_slope_n * denominator
            )
            if better_height or (equal_height and better_slope):
                best = numerator, denominator, slope_numerator, segment
        if best is None:
            output.append((point.point_id, 0, U32_MAX))
        else:
            segment = best[3]
            face = (
                segment.right_face_id
                if segment.x0 < segment.x1
                else segment.left_face_id
            )
            output.append((point.point_id, face, segment.segment_id))
    return {
        "rows": tuple(output),
        "candidate_pairs": pairs,
        "candidate_count": len(pairs),
        "exact_hit_count": exact_hit_count,
        "query_map_id": query_map_id,
        "canonical_segment_order": tuple(segment.segment_id for segment in segments),
        "contract": ExactPartnerAlgebra.DIRECTED_POINT_LOCATION_SOS_I46.value,
    }


def product_source_has_forbidden_identity_dispatch(source: str) -> bool:
    return bool(re.search(
        r"\b(x_hd|rayjoin|paper|publication|application_id|app_id)\b\s*(?:==|in\s*[\{\[])",
        source.lower(),
    ))


__all__ = [
    "CandidateProducerKind", "EXACT_COMPOSITION_SCHEMA_ID",
    "EXACT_COMPOSITION_SCHEMA_VERSION", "ExactCompositionError",
    "ExactPartnerAlgebra", "ExactPoint2D", "ExactPredicateWitnessSchema",
    "ExactSegment2D", "NearestStateRow", "RAYJOIN_COORDINATE_BITS",
    "VerifiedExactPredicateWitnessAuthority", "directed_point_location_sos",
    "exact_segment_aabb_projection", "exact_vertical_ray_aabb_projection",
    "global_max_nearest_witness_f32", "grouped_exact_segment_pair_counts",
    "product_source_has_forbidden_identity_dispatch",
    "rayjoin_sos_segment_pair_intersects",
    "verify_exact_predicate_witness_schema",
]
