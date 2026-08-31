"""Verified capacity-bounded relation emission for V4 Callback IR.

This module is the app-neutral M2 successor to the fixed-record V4 targets.
It does not accept a reducer, serializer, callback provider, or application
identity.  A verified custom-AABB callback may expose accepted any-hit events
as a two-column U32 relation under one closed contract:

* capacity is declared before launch;
* overflow rejects the complete result (partial rows are never authoritative);
* raw device order is never semantic;
* canonical order is unsigned lexicographic ``(source_id, item_id)``; and
* duplicate handling is explicit and verified.

The CPU materializer is executable reference semantics.  Device execution is
authorized separately by the target compiler/runtime and must bind the exact
callback, typed physical schema, target native, ABI, and relation contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
import re
import struct
from typing import Iterable, Sequence

from .v4_callback_ir import (
    CallbackRole,
    EffectKind,
    IfStatement,
    ReturnEffectStatement,
    StaticForStatement,
)
from .v4_typed_physical_schema import (
    GeometryFamily,
    VerifiedPhysicalSchemaAuthority,
    verify_typed_physical_schema,
)


BOUNDED_RELATION_SCHEMA_ID = (
    "https://rtdl.dev/schemas/v4-bounded-relation-emission-v1.json"
)
BOUNDED_RELATION_SCHEMA_VERSION = "v1"
BOUNDED_RELATION_TEMPLATE = "custom_aabb_bounded_relation_emission_v1"
U32_MAX = (1 << 32) - 1


class BoundedRelationError(ValueError):
    """Stable fail-closed diagnostic for relation admission/materialization."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(
            f"V4 bounded relation rejected: {code}@{path}: {message}")


def _fail(code: str, path: str, message: str) -> None:
    raise BoundedRelationError(code, path, message)


def _sha(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


class RelationRowSource(str, Enum):
    LAUNCH_SOURCE_ID = "launch_source_id"
    VERIFIED_INTERSECTION_ATTRIBUTE0_ITEM_ID = (
        "verified_intersection_attribute0_item_id")


class RelationOrdering(str, Enum):
    LEXICOGRAPHIC_U32_PAIR = "lexicographic_u32_pair"


class RelationDuplicatePolicy(str, Enum):
    REJECT = "reject"
    KEYED_IDENTICAL_DEDUP = "keyed_identical_dedup"


@dataclass(frozen=True)
class BoundedRelationEmissionSchema:
    callback_ir_sha256: str
    effect_digest: str
    physical_schema_sha256: str
    capacity: int
    minimum_overlap_f32: float = 0.0
    row_sources: tuple[RelationRowSource, RelationRowSource] = (
        RelationRowSource.LAUNCH_SOURCE_ID,
        RelationRowSource.VERIFIED_INTERSECTION_ATTRIBUTE0_ITEM_ID,
    )
    ordering: RelationOrdering = RelationOrdering.LEXICOGRAPHIC_U32_PAIR
    duplicate_policy: RelationDuplicatePolicy = (
        RelationDuplicatePolicy.KEYED_IDENTICAL_DEDUP
    )
    schema_id: str = BOUNDED_RELATION_SCHEMA_ID
    schema_version: str = BOUNDED_RELATION_SCHEMA_VERSION

    def semantic_dict(self) -> dict[str, object]:
        return {
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "physical_schema_sha256": self.physical_schema_sha256,
            "capacity": self.capacity,
            "minimum_overlap_f32": self.minimum_overlap_f32,
            "minimum_overlap_boundary": "inclusive",
            "row_sources": [item.value for item in self.row_sources],
            "ordering": self.ordering.value,
            "duplicate_policy": self.duplicate_policy.value,
            "overflow_policy": "fail_closed_reject_complete_result",
            "raw_device_order_is_semantic": False,
            "row_type": ["u32", "u32"],
        }

    @property
    def schema_sha256(self) -> str:
        return _sha(self.semantic_dict())

    def to_dict(self) -> dict[str, object]:
        return {**self.semantic_dict(), "schema_sha256": self.schema_sha256}


@dataclass(frozen=True)
class VerifiedBoundedRelationAuthority:
    physical: VerifiedPhysicalSchemaAuthority
    schema: BoundedRelationEmissionSchema
    authority_nonce: str


@dataclass(frozen=True)
class CompiledBoundedRelationContract:
    callback_ir_sha256: str
    effect_digest: str
    physical_schema_sha256: str
    relation_schema_sha256: str
    target_sha256: str
    abi_sha256: str
    capacity: int
    minimum_overlap_f32: float
    row_sources: tuple[str, str]
    ordering: str
    duplicate_policy: str
    authority_nonce: str
    template_id: str = BOUNDED_RELATION_TEMPLATE
    executable: bool = False

    def semantic_dict(self) -> dict[str, object]:
        return {
            "callback_ir_sha256": self.callback_ir_sha256,
            "effect_digest": self.effect_digest,
            "physical_schema_sha256": self.physical_schema_sha256,
            "relation_schema_sha256": self.relation_schema_sha256,
            "target_sha256": self.target_sha256,
            "abi_sha256": self.abi_sha256,
            "capacity": self.capacity,
            "minimum_overlap_f32": self.minimum_overlap_f32,
            "minimum_overlap_boundary": "inclusive",
            "row_sources": list(self.row_sources),
            "ordering": self.ordering,
            "duplicate_policy": self.duplicate_policy,
            "overflow_policy": "fail_closed_reject_complete_result",
            "raw_device_order_is_semantic": False,
            "authority_nonce": self.authority_nonce,
            "template_id": self.template_id,
            "executable": self.executable,
            "target_execution_receipt_required": True,
        }

    @property
    def contract_sha256(self) -> str:
        return _sha(self.semantic_dict())

    def to_dict(self) -> dict[str, object]:
        return {**self.semantic_dict(), "contract_sha256": self.contract_sha256}


def verify_bounded_relation_schema(
    physical: VerifiedPhysicalSchemaAuthority,
    schema: BoundedRelationEmissionSchema,
) -> VerifiedBoundedRelationAuthority:
    """Reverify exact callback/schema/target identity before minting authority."""

    if not isinstance(physical, VerifiedPhysicalSchemaAuthority):
        _fail("physical_authority_required", "physical", type(physical).__name__)
    fresh = verify_typed_physical_schema(
        physical.callback,
        physical.schema,
        target=physical.target,
        orientation_authorities={},
    )
    if fresh != physical:
        _fail("physical_authority_drift", "physical", "authority did not rederive")
    callback = physical.callback
    if physical.schema.geometry_family is not GeometryFamily.CUSTOM_AABB:
        _fail("geometry_family", "physical.schema", "custom_aabb is required")
    if schema.schema_id != BOUNDED_RELATION_SCHEMA_ID \
            or schema.schema_version != BOUNDED_RELATION_SCHEMA_VERSION:
        _fail("schema_identity", "schema", "unsupported relation schema")
    if schema.callback_ir_sha256 != callback.ir_sha256 \
            or schema.effect_digest != callback.effect_digest:
        _fail("callback_binding", "schema", "exact callback identity required")
    if schema.physical_schema_sha256 != physical.schema.schema_sha256:
        _fail("physical_schema_binding", "schema", "exact physical schema required")
    if not isinstance(schema.capacity, int) or isinstance(schema.capacity, bool) \
            or schema.capacity <= 0 or schema.capacity > U32_MAX:
        _fail("capacity", "schema.capacity", "positive u32 capacity required")
    if not math.isfinite(float(schema.minimum_overlap_f32)) \
            or float(schema.minimum_overlap_f32) < 0.0:
        _fail(
            "minimum_overlap",
            "schema.minimum_overlap_f32",
            "finite nonnegative closed-boundary threshold required",
        )
    f32_threshold = struct.unpack(
        "<f", struct.pack("<f", float(schema.minimum_overlap_f32)))[0]
    if f32_threshold != float(schema.minimum_overlap_f32):
        _fail(
            "minimum_overlap_f32_exactness",
            "schema.minimum_overlap_f32",
            "threshold must be exactly representable by the device f32 contract",
        )
    if schema.row_sources != (
            RelationRowSource.LAUNCH_SOURCE_ID,
            RelationRowSource.VERIFIED_INTERSECTION_ATTRIBUTE0_ITEM_ID):
        _fail("row_sources", "schema.row_sources", "closed two-column source required")
    if schema.ordering is not RelationOrdering.LEXICOGRAPHIC_U32_PAIR:
        _fail("ordering", "schema.ordering", "canonical u32 pair ordering required")
    if schema.duplicate_policy not in {
            RelationDuplicatePolicy.REJECT,
            RelationDuplicatePolicy.KEYED_IDENTICAL_DEDUP}:
        _fail("duplicate_policy", "schema.duplicate_policy", "unsupported policy")
    any_hit = callback.program.function_for_role(CallbackRole.ANY_HIT)

    def returned_effects(statements) -> set[EffectKind]:
        result: set[EffectKind] = set()
        for statement in statements:
            if isinstance(statement, ReturnEffectStatement):
                result.add(statement.effect.kind)
            elif isinstance(statement, IfStatement):
                result.update(returned_effects(statement.then_body))
                result.update(returned_effects(statement.else_body))
            elif isinstance(statement, StaticForStatement):
                result.update(returned_effects(statement.body))
        return result

    effect_kinds = returned_effects(any_hit.body)
    # The current target materializes accepted events.  It cannot soundly
    # invent semantics for terminate/ignore/payload-only any-hit outcomes.
    if not effect_kinds or effect_kinds != {EffectKind.ACCEPT_CONTINUE}:
        _fail(
            "any_hit_effect",
            "callback.any_hit",
            "every return path must be accept_continue for relation emission",
        )
    nonce = _sha({
        "kind": "verified_bounded_relation_authority_v1",
        "callback": callback.ir_sha256,
        "effect": callback.effect_digest,
        "physical_schema": physical.schema.schema_sha256,
        "target": physical.target.target_sha256,
        "relation_schema": schema.schema_sha256,
    })
    return VerifiedBoundedRelationAuthority(physical, schema, nonce)


def compile_bounded_relation_contract(
    authority: VerifiedBoundedRelationAuthority,
    *,
    abi_sha256: str,
) -> CompiledBoundedRelationContract:
    fresh = verify_bounded_relation_schema(authority.physical, authority.schema)
    if fresh != authority:
        _fail("authority_reverification", "authority", "live authority did not rederive")
    if re.fullmatch(r"[0-9a-f]{64}", abi_sha256) is None:
        _fail("abi_identity", "abi_sha256", abi_sha256)
    schema = authority.schema
    return CompiledBoundedRelationContract(
        callback_ir_sha256=authority.physical.callback.ir_sha256,
        effect_digest=authority.physical.callback.effect_digest,
        physical_schema_sha256=authority.physical.schema.schema_sha256,
        relation_schema_sha256=schema.schema_sha256,
        target_sha256=authority.physical.target.target_sha256,
        abi_sha256=abi_sha256,
        capacity=schema.capacity,
        minimum_overlap_f32=float(schema.minimum_overlap_f32),
        row_sources=tuple(item.value for item in schema.row_sources),
        ordering=schema.ordering.value,
        duplicate_policy=schema.duplicate_policy.value,
        authority_nonce=authority.authority_nonce,
    )


def materialize_bounded_relation(
    rows: Iterable[Sequence[int]],
    *,
    capacity: int,
    duplicate_policy: RelationDuplicatePolicy,
    observed_raw_count: int | None = None,
    overflowed: bool = False,
) -> tuple[tuple[int, int], ...]:
    """Canonical executable reference; never accepts a partial overflow."""

    if not isinstance(capacity, int) or isinstance(capacity, bool) \
            or capacity <= 0 or capacity > U32_MAX:
        _fail("capacity", "capacity", "positive u32 capacity required")
    materialized: list[tuple[int, int]] = []
    for index, row in enumerate(rows):
        if len(row) != 2:
            _fail("row_shape", f"rows[{index}]", repr(tuple(row)))
        left, right = int(row[0]), int(row[1])
        if not 0 <= left <= U32_MAX or not 0 <= right <= U32_MAX:
            _fail("row_domain", f"rows[{index}]", repr((left, right)))
        materialized.append((left, right))
    raw_count = len(materialized) if observed_raw_count is None else observed_raw_count
    if not isinstance(raw_count, int) or isinstance(raw_count, bool) or raw_count < 0:
        _fail("raw_count", "observed_raw_count", repr(raw_count))
    if overflowed or raw_count > capacity or len(materialized) > capacity:
        _fail(
            "capacity_overflow",
            "rows",
            f"raw_count={raw_count}, materialized={len(materialized)}, capacity={capacity}",
        )
    ordered = sorted(materialized)
    duplicate = next(
        (ordered[index] for index in range(1, len(ordered))
         if ordered[index] == ordered[index - 1]),
        None,
    )
    if duplicate is not None and duplicate_policy is RelationDuplicatePolicy.REJECT:
        _fail("duplicate_row", "rows", repr(duplicate))
    if duplicate_policy is RelationDuplicatePolicy.KEYED_IDENTICAL_DEDUP:
        ordered = list(dict.fromkeys(ordered))
    return tuple(ordered)


def verify_precanonical_bounded_relation(
    rows: Iterable[Sequence[int]],
    *,
    capacity: int,
    observed_unique_count: int,
    overflowed: bool = False,
) -> tuple[tuple[int, int], ...]:
    """Verify, without resorting, a native sorted/unique result projection."""

    if not isinstance(capacity, int) or isinstance(capacity, bool) \
            or capacity <= 0 or capacity > U32_MAX:
        _fail("capacity", "capacity", "positive u32 capacity required")
    if not isinstance(observed_unique_count, int) \
            or isinstance(observed_unique_count, bool) \
            or observed_unique_count < 0:
        _fail("raw_count", "observed_unique_count", repr(observed_unique_count))
    materialized: list[tuple[int, int]] = []
    previous: tuple[int, int] | None = None
    for index, row in enumerate(rows):
        if len(row) != 2:
            _fail("row_shape", f"rows[{index}]", repr(tuple(row)))
        current = int(row[0]), int(row[1])
        if not 0 <= current[0] <= U32_MAX \
                or not 0 <= current[1] <= U32_MAX:
            _fail("row_domain", f"rows[{index}]", repr(current))
        if previous is not None and current <= previous:
            _fail(
                "precanonical_order",
                f"rows[{index}]",
                f"previous={previous!r}, current={current!r}",
            )
        materialized.append(current)
        previous = current
    if overflowed or observed_unique_count > capacity \
            or len(materialized) > capacity \
            or len(materialized) != observed_unique_count:
        _fail(
            "capacity_overflow" if overflowed \
                or observed_unique_count > capacity \
                or len(materialized) > capacity else "unique_count",
            "rows",
            f"observed_unique_count={observed_unique_count}, "
            f"materialized={len(materialized)}, capacity={capacity}",
        )
    return tuple(materialized)


__all__ = [
    "BOUNDED_RELATION_SCHEMA_ID",
    "BOUNDED_RELATION_SCHEMA_VERSION",
    "BOUNDED_RELATION_TEMPLATE",
    "BoundedRelationEmissionSchema",
    "BoundedRelationError",
    "CompiledBoundedRelationContract",
    "RelationDuplicatePolicy",
    "RelationOrdering",
    "RelationRowSource",
    "VerifiedBoundedRelationAuthority",
    "compile_bounded_relation_contract",
    "materialize_bounded_relation",
    "verify_precanonical_bounded_relation",
    "verify_bounded_relation_schema",
]
