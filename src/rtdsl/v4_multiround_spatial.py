"""Compiler-owned bounded multi-round spatial composition for V4.

This module intentionally has no user-supplied controller, reducer, ranking
function, or application identity.  One verified Callback-IR traversal emits
typed candidate rows.  Two closed partner algebras consume those rows:

* exact float32 ranked-distance-window top-K; and
* exact float32 radius graph plus deterministic predicate-aware components.

The executable runtime is separate.  The functions below are the reference
semantics and fail-closed admission contract used to check device results.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
import re
from typing import Sequence

import numpy as np

from .component_partition import canonical_partition_labels
from .predicate_aware_boundary_union import (
    predicate_aware_boundary_union_reference,
)
from .v4_bounded_relation import (
    CompiledBoundedRelationContract,
    VerifiedBoundedRelationAuthority,
    verify_bounded_relation_schema,
)
from .v4_callback_abi import CompiledCallbackAbi, verify_compiled_callback_abi
from .v4_typed_physical_schema import GasUpdatePolicy


MULTIROUND_SPATIAL_SCHEMA_ID = (
    "https://rtdl.dev/schemas/v4-multiround-spatial-composition-v1.json"
)
MULTIROUND_SPATIAL_SCHEMA_VERSION = "v1"
U32_MAX = (1 << 32) - 1


class MultiRoundSpatialError(ValueError):
    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"V4 multi-round spatial rejected: {code}@{path}: {message}")


def _fail(code: str, path: str, message: str) -> None:
    raise MultiRoundSpatialError(code, path, message)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


class SpatialPartnerAlgebra(str, Enum):
    RANKED_DISTANCE_WINDOW_F32 = "ranked_distance_window_f32_v1"
    RADIUS_GRAPH_COMPONENTS_F32 = "radius_graph_components_f32_v1"


class DistanceWindowBoundaryPolicy(str, Enum):
    """Closed vocabulary; never a user predicate or callback."""

    OPEN = "open_min_open_max_v1"
    CLOSED = "closed_min_closed_max_v1"


@dataclass(frozen=True)
class MultiRoundSpatialSchema:
    relation_schema_sha256: str
    callback_ir_sha256: str
    effect_digest: str
    physical_schema_sha256: str
    maximum_rounds: int
    maximum_event_capacity: int
    partner_algebras: tuple[SpatialPartnerAlgebra, ...] = (
        SpatialPartnerAlgebra.RANKED_DISTANCE_WINDOW_F32,
        SpatialPartnerAlgebra.RADIUS_GRAPH_COMPONENTS_F32,
    )
    schema_id: str = MULTIROUND_SPATIAL_SCHEMA_ID
    schema_version: str = MULTIROUND_SPATIAL_SCHEMA_VERSION

    def semantic_dict(self) -> dict[str, object]:
        return {
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "relation_schema_sha256": self.relation_schema_sha256,
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "physical_schema_sha256": self.physical_schema_sha256,
            "maximum_rounds": self.maximum_rounds,
            "maximum_event_capacity": self.maximum_event_capacity,
            "partner_algebras": [item.value for item in self.partner_algebras],
            "controller_owner": "compiler",
            "persistent_gas_required": True,
            "gas_build_count": 1,
            "refit_between_changed_radii": True,
            "raw_device_order_is_semantic": False,
            "overflow_policy": "fail_closed_reject_complete_result",
            "user_controller_or_reducer_allowed": False,
        }

    @property
    def schema_sha256(self) -> str:
        return _digest(self.semantic_dict())

    def to_dict(self) -> dict[str, object]:
        return {**self.semantic_dict(), "schema_sha256": self.schema_sha256}


@dataclass(frozen=True)
class VerifiedMultiRoundSpatialAuthority:
    relation: VerifiedBoundedRelationAuthority
    relation_contract: CompiledBoundedRelationContract
    abi: CompiledCallbackAbi
    schema: MultiRoundSpatialSchema
    authority_nonce: str


@dataclass(frozen=True)
class RankedDistanceWindowRequest:
    k: int
    minimum_distance: float
    maximum_distance: float
    initial_radius: float
    maximum_rounds: int
    boundary_policy: DistanceWindowBoundaryPolicy = DistanceWindowBoundaryPolicy.OPEN


@dataclass(frozen=True)
class RadiusGraphComponentsRequest:
    epsilon: float
    min_points: int
    maximum_rounds: int = 1


@dataclass(frozen=True)
class MultiRoundTelemetry:
    prepared_token: int
    gas_build_count: int
    gas_refit_count: int
    launch_count: int
    traversable_handle_first: int
    traversable_handle_last: int
    radii: tuple[float, ...]


def verify_multiround_spatial_schema(
    relation: VerifiedBoundedRelationAuthority,
    relation_contract: CompiledBoundedRelationContract,
    abi: CompiledCallbackAbi,
    schema: MultiRoundSpatialSchema,
    *,
    any_hit_proof_authority,
) -> VerifiedMultiRoundSpatialAuthority:
    fresh = verify_bounded_relation_schema(relation.physical, relation.schema)
    if fresh != relation:
        _fail("relation_authority_drift", "relation", "authority did not rederive")
    canonical_abi = verify_compiled_callback_abi(
        abi,
        fresh.physical.callback,
        any_hit_proof_authority=any_hit_proof_authority,
        physical_schema_authority=fresh.physical,
    )
    if canonical_abi != abi:
        _fail("abi_drift", "abi", "exact callback ABI is required")
    if relation_contract.relation_schema_sha256 != fresh.schema.schema_sha256 \
            or relation_contract.abi_sha256 != abi.abi_sha256 \
            or relation_contract.executable:
        _fail("relation_contract", "relation_contract", "exact inert contract required")
    if fresh.physical.schema.gas.update_policy is not GasUpdatePolicy.DECLARED_REFIT:
        _fail("gas_update_policy", "physical.gas", "declared_refit is required")
    if schema.schema_id != MULTIROUND_SPATIAL_SCHEMA_ID \
            or schema.schema_version != MULTIROUND_SPATIAL_SCHEMA_VERSION:
        _fail("schema_identity", "schema", "unsupported schema")
    if schema.relation_schema_sha256 != fresh.schema.schema_sha256 \
            or schema.callback_ir_sha256 != fresh.physical.callback.ir_sha256 \
            or schema.effect_digest != fresh.physical.callback.effect_digest \
            or schema.physical_schema_sha256 != fresh.physical.schema.schema_sha256:
        _fail("identity_binding", "schema", "exact relation/callback/physical binding required")
    if not isinstance(schema.maximum_rounds, int) or isinstance(schema.maximum_rounds, bool) \
            or not 1 <= schema.maximum_rounds <= 64:
        _fail("maximum_rounds", "schema.maximum_rounds", "integer in [1,64] required")
    if not isinstance(schema.maximum_event_capacity, int) \
            or isinstance(schema.maximum_event_capacity, bool) \
            or not 1 <= schema.maximum_event_capacity <= U32_MAX:
        _fail("maximum_event_capacity", "schema", "positive u32 required")
    if schema.maximum_event_capacity > fresh.schema.capacity:
        _fail("capacity_binding", "schema", "cannot exceed verified relation capacity")
    if schema.partner_algebras != (
            SpatialPartnerAlgebra.RANKED_DISTANCE_WINDOW_F32,
            SpatialPartnerAlgebra.RADIUS_GRAPH_COMPONENTS_F32):
        _fail("partner_algebras", "schema", "the two closed typed algebras are required")
    nonce = _digest({
        "relation": fresh.authority_nonce,
        "relation_contract": relation_contract.contract_sha256,
        "abi": abi.abi_sha256,
        "schema": schema.schema_sha256,
        "kind": "verified_multiround_spatial_authority_v1",
    })
    return VerifiedMultiRoundSpatialAuthority(
        fresh, relation_contract, abi, schema, nonce)


def _points_f32(points: Sequence[Sequence[float]], label: str) -> np.ndarray:
    values = np.asarray(points, dtype=np.float32)
    if values.ndim != 2 or values.shape[0] == 0 or values.shape[1] not in (2, 3):
        _fail("point_shape", label, "nonempty Nx2 or Nx3 rows required")
    if not np.isfinite(values).all():
        _fail("point_finite", label, "finite float32 coordinates required")
    if values.shape[1] == 2:
        values = np.column_stack((values, np.zeros(values.shape[0], dtype=np.float32)))
    return np.ascontiguousarray(values, dtype=np.float32)


def _candidate_set(
    candidates: Sequence[Sequence[int]],
    *, query_count: int,
    item_count: int,
) -> tuple[tuple[int, int], ...]:
    rows: set[tuple[int, int]] = set()
    for index, row in enumerate(candidates):
        if len(row) != 2:
            _fail("candidate_shape", f"candidates[{index}]", "u32 pair required")
        query_id, item_id = int(row[0]), int(row[1])
        if not 0 <= query_id < query_count or not 0 <= item_id < item_count:
            _fail("candidate_domain", f"candidates[{index}]", "pair outside input domains")
        rows.add((query_id, item_id))
    return tuple(sorted(rows))


def _distance_sq_f32(left: np.ndarray, right: np.ndarray) -> np.float32:
    delta = np.subtract(left, right, dtype=np.float32)
    squared = np.multiply(delta, delta, dtype=np.float32)
    value = np.add(squared[0], squared[1], dtype=np.float32)
    return np.add(value, squared[2], dtype=np.float32)


def ranked_distance_window_partner(
    search_points: Sequence[Sequence[float]],
    query_points: Sequence[Sequence[float]],
    candidates: Sequence[Sequence[int]],
    *,
    k: int,
    minimum_distance: float,
    maximum_distance: float,
    boundary_policy: DistanceWindowBoundaryPolicy = DistanceWindowBoundaryPolicy.OPEN,
) -> tuple[tuple[int, int, int, float], ...]:
    search = _points_f32(search_points, "search_points")
    queries = _points_f32(query_points, "query_points")
    if not isinstance(k, int) or isinstance(k, bool) or not 1 <= k <= 64:
        _fail("k", "request.k", "integer in [1,64] required")
    if not math.isfinite(minimum_distance) or not math.isfinite(maximum_distance) \
            or minimum_distance < 0.0 or not minimum_distance < maximum_distance:
        _fail("distance_window", "request", "finite 0<=min<max required")
    if not isinstance(boundary_policy, DistanceWindowBoundaryPolicy):
        _fail("boundary_policy", "request", "closed boundary-policy enum required")
    rows = _candidate_set(candidates, query_count=len(queries), item_count=len(search))
    by_query: list[list[tuple[np.float32, int]]] = [[] for _ in range(len(queries))]
    for query_id, item_id in rows:
        distance_sq = _distance_sq_f32(queries[query_id], search[item_id])
        distance = np.sqrt(distance_sq, dtype=np.float32)
        inside = (
            float(minimum_distance) < float(distance) < float(maximum_distance)
            if boundary_policy is DistanceWindowBoundaryPolicy.OPEN
            else float(minimum_distance) <= float(distance) <= float(maximum_distance)
        )
        if inside:
            by_query[query_id].append((distance, item_id))
    output: list[tuple[int, int, int, float]] = []
    for query_id, values in enumerate(by_query):
        selected = sorted(values, key=lambda item: (float(item[0]), item[1]))[:k]
        for rank, (distance, item_id) in enumerate(selected, start=1):
            distance_sq_out = np.multiply(distance, distance, dtype=np.float32)
            output.append((query_id, item_id, rank, float(distance_sq_out)))
    return tuple(output)


def radius_graph_components_partner(
    points: Sequence[Sequence[float]],
    candidates: Sequence[Sequence[int]],
    *,
    epsilon: float,
    min_points: int,
) -> dict[str, object]:
    values = _points_f32(points, "points")
    if not math.isfinite(epsilon) or epsilon < 0.0:
        _fail("epsilon", "request.epsilon", "finite nonnegative radius required")
    if not isinstance(min_points, int) or isinstance(min_points, bool) or min_points <= 0:
        _fail("min_points", "request.min_points", "positive integer required")
    rows = _candidate_set(candidates, query_count=len(values), item_count=len(values))
    radius = np.float32(epsilon)
    radius_sq = np.multiply(radius, radius, dtype=np.float32)
    exact_edges = tuple(
        (source, target)
        for source, target in rows
        if _distance_sq_f32(values[source], values[target]) <= radius_sq
    )
    neighbor_counts = [0] * len(values)
    for source, _ in exact_edges:
        neighbor_counts[source] += 1
    core_flags = tuple(count >= min_points for count in neighbor_counts)
    partition = predicate_aware_boundary_union_reference(
        point_count=len(values),
        candidate_pairs=exact_edges,
        predicate_flags=core_flags,
    )
    labels = canonical_partition_labels(partition["component_labels"])
    return {
        "edge_count": len(exact_edges),
        "edge_rows": exact_edges,
        "neighbor_counts": tuple(neighbor_counts),
        "core_flags": core_flags,
        "canonical_component_labels": labels,
        "partition_metadata": partition,
    }


def bounded_radius_schedule(
    *, initial_radius: float, maximum_radius: float, maximum_rounds: int,
) -> tuple[float, ...]:
    if not math.isfinite(initial_radius) or not math.isfinite(maximum_radius) \
            or initial_radius <= 0.0 or initial_radius > maximum_radius:
        _fail("radius_schedule", "request", "finite 0<initial<=maximum required")
    if not isinstance(maximum_rounds, int) or isinstance(maximum_rounds, bool) \
            or not 1 <= maximum_rounds <= 64:
        _fail("round_bound", "request.maximum_rounds", "integer in [1,64] required")
    radii: list[float] = []
    radius = float(np.float32(initial_radius))
    maximum = float(np.float32(maximum_radius))
    for _ in range(maximum_rounds):
        radii.append(min(radius, maximum))
        if radii[-1] == maximum:
            break
        doubled = float(np.float32(radius * 2.0))
        radius = maximum if not math.isfinite(doubled) or doubled >= maximum else doubled
    if radii[-1] != maximum:
        _fail("round_bound_exhausted", "request.maximum_rounds", "maximum radius was not reached")
    return tuple(radii)


def expected_radius_candidates(
    search_points: Sequence[Sequence[float]],
    query_points: Sequence[Sequence[float]],
    radius: float,
) -> tuple[tuple[int, int], ...]:
    """Route-independent conservative candidate reference used by tests."""
    search = _points_f32(search_points, "search_points")
    queries = _points_f32(query_points, "query_points")
    radius_f32 = np.float32(radius)
    radius_sq = np.multiply(radius_f32, radius_f32, dtype=np.float32)
    return tuple(
        (query_id, item_id)
        for query_id, query in enumerate(queries)
        for item_id, item in enumerate(search)
        if _distance_sq_f32(query, item) <= radius_sq
    )


def validate_multiround_telemetry(
    telemetry: MultiRoundTelemetry,
    *, expected_rounds: int,
    expected_refits: int | None = None,
) -> None:
    if telemetry.prepared_token <= 0:
        _fail("prepared_token", "telemetry", "positive live owner token required")
    if telemetry.gas_build_count != 1:
        _fail("gas_build_count", "telemetry", "exactly one GAS build required")
    if expected_refits is None:
        expected_refits = max(0, expected_rounds - 1)
    if not isinstance(expected_refits, int) or expected_refits < 0 \
            or expected_refits > expected_rounds:
        _fail("expected_refits", "telemetry", "bounded refit count required")
    if telemetry.launch_count != expected_rounds \
            or telemetry.gas_refit_count != expected_refits:
        _fail("lifecycle_counts", "telemetry", "launch/refit counts do not match rounds")
    if telemetry.traversable_handle_first <= 0 \
            or telemetry.traversable_handle_last <= 0:
        _fail("traversable_handle", "telemetry", "nonzero observed handles required")
    if len(telemetry.radii) != expected_rounds:
        _fail("radius_count", "telemetry", "one radius per round required")


def product_source_has_forbidden_identity_dispatch(source: str) -> bool:
    lowered = source.lower()
    return bool(re.search(
        r"\b(rtnn|dbscan|paper|application_id|app_id)\b\s*(?:==|in\s*\{|in\s*\[)",
        lowered,
    ))


__all__ = [
    "DistanceWindowBoundaryPolicy",
    "MultiRoundSpatialError", "MultiRoundSpatialSchema",
    "MultiRoundTelemetry", "RadiusGraphComponentsRequest",
    "RankedDistanceWindowRequest", "SpatialPartnerAlgebra",
    "VerifiedMultiRoundSpatialAuthority", "bounded_radius_schedule",
    "expected_radius_candidates", "product_source_has_forbidden_identity_dispatch",
    "radius_graph_components_partner", "ranked_distance_window_partner",
    "validate_multiround_telemetry", "verify_multiround_spatial_schema",
]
