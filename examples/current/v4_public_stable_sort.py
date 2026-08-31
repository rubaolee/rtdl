#!/usr/bin/env python3
"""Stable integer sorting as a public RTDL V4 bounded-relation application.

This is deliberately application code, not a new RTDL core family.  It maps a
stable total order onto the existing custom-AABB relation protocol:

* record ``j`` precedes record ``i`` iff the query box for ``i`` overlaps the
  indexed suffix box for ``j``;
* the RT result is the complete predecessor relation;
* removing the self row by *application item id* gives each record's rank;
* scattering by those ranks produces the stable order.

RTDL admits and executes the callback protocol.  It does not prove that this
application mapping implements sorting, so the returned relation and final
order are checked against independent application oracles after execution.
No performance claim is made.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import struct
from typing import Iterable, Sequence

from rtdsl.v4 import (
    AnyHitProtocolProof,
    BoundedRelationBatch,
    BoundedRelationProtocol,
    BoundedRelationStaticInput,
    V4Target,
    V4Toolchain,
    compile_protocol_program,
    standard_protocol_physical_plan,
)


_QUARTER = 0.25
_UINT32_MAX = (1 << 32) - 1


class StableSortMappingError(ValueError):
    """The application mapping or returned relation cannot define a sort."""


@dataclass(frozen=True)
class StableSortEncoding:
    values: tuple[int, ...]
    order_codes: tuple[int, ...]
    indexed_order: tuple[int, ...]
    source_order: tuple[int, ...]
    indexed_boxes: tuple[tuple[float, float, float, float, int], ...]
    source_boxes: tuple[tuple[float, float, float, float, int], ...]
    capacity: int
    minimum_overlap_f32: float = _QUARTER


@dataclass(frozen=True)
class StableSortOutcome:
    ranks_by_item_id: tuple[int, ...]
    sorted_records: tuple[tuple[int, int], ...]

    @property
    def sorted_values(self) -> tuple[int, ...]:
        return tuple(value for value, _item_id in self.sorted_records)


def _f32(value: float | int) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def _permutation(value: Sequence[int] | None, count: int, name: str) -> tuple[int, ...]:
    if value is None:
        return tuple(range(count))
    raw = tuple(value)
    if any(not isinstance(item, int) or isinstance(item, bool) for item in raw):
        raise StableSortMappingError(f"{name} must contain integer item ids")
    result = tuple(int(item) for item in raw)
    if len(result) != count or set(result) != set(range(count)):
        raise StableSortMappingError(f"{name} must be a permutation of 0..{count - 1}")
    return result


def encode_stable_sort(
    values: Sequence[int],
    *,
    indexed_order: Sequence[int] | None = None,
    source_order: Sequence[int] | None = None,
) -> StableSortEncoding:
    """Map stable integer ordering to an exact binary32 AABB relation.

    For record ``i``, ``u_i = (key_i - min_key) * (n + 1) + i``.  The original
    index is therefore the stable tie break without sorting or coordinate
    compression on the host.  Quarter-wide query boxes require every endpoint
    to survive an exact binary32 round trip; inputs outside that envelope are
    rejected before RTDL sees them.
    """

    normalized = tuple(values)
    if not normalized:
        raise StableSortMappingError("the RT sorting demo requires at least one record")
    if any(not isinstance(value, int) or isinstance(value, bool) for value in normalized):
        raise StableSortMappingError("stable-sort keys must be integers, not booleans")
    count = len(normalized)
    if count - 1 > _UINT32_MAX:
        raise StableSortMappingError("record item ids exceed the U32 protocol domain")
    capacity = count * (count + 1) // 2
    if capacity <= 0 or capacity > _UINT32_MAX:
        raise StableSortMappingError("complete predecessor relation exceeds U32 capacity")

    base = min(normalized)
    stride = count + 1
    order_codes = tuple(
        (int(value) - int(base)) * stride + item_id
        for item_id, value in enumerate(normalized)
    )
    upper = max(order_codes) + 1
    exact_endpoints: Iterable[float | int] = (
        endpoint
        for code in order_codes
        for endpoint in (code, code + _QUARTER, upper)
    )
    try:
        endpoints_are_exact = all(
            _f32(endpoint) == float(endpoint) for endpoint in exact_endpoints)
    except (OverflowError, ValueError, struct.error) as error:
        raise StableSortMappingError(
            "stable-sort coordinates exceed the binary32 domain") from error
    if not endpoints_are_exact:
        raise StableSortMappingError(
            "stable-sort coordinates exceed the exact binary32 quarter grid"
        )

    indexed_ids = _permutation(indexed_order, count, "indexed_order")
    source_ids = _permutation(source_order, count, "source_order")
    indexed_boxes = tuple(
        (float(order_codes[item_id]), 0.0, float(upper), 1.0, item_id)
        for item_id in indexed_ids
    )
    source_boxes = tuple(
        (
            float(order_codes[item_id]), 0.0,
            float(order_codes[item_id]) + _QUARTER, 1.0,
            item_id,
        )
        for item_id in source_ids
    )
    return StableSortEncoding(
        values=tuple(int(value) for value in normalized),
        order_codes=order_codes,
        indexed_order=indexed_ids,
        source_order=source_ids,
        indexed_boxes=indexed_boxes,
        source_boxes=source_boxes,
        capacity=capacity,
    )


def predecessor_relation_oracle(values: Sequence[int]) -> tuple[tuple[int, int], ...]:
    """Independent pairwise oracle; it does not call a sorting routine."""

    normalized = tuple(int(value) for value in values)
    return tuple(
        (source_id, predecessor_id)
        for source_id in range(len(normalized))
        for predecessor_id in range(len(normalized))
        if (normalized[predecessor_id], predecessor_id)
        <= (normalized[source_id], source_id)
    )


def geometry_relation_reference(
    encoding: StableSortEncoding,
) -> tuple[tuple[int, int], ...]:
    """Application-side closed-overlap model, independent of RTDL."""

    rows: set[tuple[int, int]] = set()
    threshold = encoding.minimum_overlap_f32
    for source in encoding.source_boxes:
        for indexed in encoding.indexed_boxes:
            overlap_x = max(0.0, min(source[2], indexed[2]) - max(source[0], indexed[0]))
            overlap_y = max(0.0, min(source[3], indexed[3]) - max(source[1], indexed[1]))
            closed = (
                indexed[0] <= source[2] and indexed[2] >= source[0]
                and indexed[1] <= source[3] and indexed[3] >= source[1]
            )
            if closed and overlap_x * overlap_y >= threshold:
                rows.add((int(source[4]), int(indexed[4])))
    return tuple(sorted(rows))


def stable_sort_from_relation(
    values: Sequence[int], rows: Sequence[Sequence[int]],
) -> StableSortOutcome:
    """Remove self by nominal item id, derive ranks, and scatter records."""

    normalized = tuple(int(value) for value in values)
    count = len(normalized)
    canonical = tuple((int(row[0]), int(row[1])) for row in rows)
    if len(set(canonical)) != len(canonical):
        raise StableSortMappingError("relation contains duplicate logical rows")
    if any(
        source < 0 or source >= count or predecessor < 0 or predecessor >= count
        for source, predecessor in canonical
    ):
        raise StableSortMappingError("relation contains an unknown application item id")

    by_source: list[list[int]] = [[] for _ in range(count)]
    for source_id, predecessor_id in canonical:
        by_source[source_id].append(predecessor_id)
    ranks: list[int] = []
    for item_id, predecessors in enumerate(by_source):
        if predecessors.count(item_id) != 1:
            raise StableSortMappingError(
                f"item {item_id} must have exactly one self relation"
            )
        ranks.append(sum(predecessor_id != item_id for predecessor_id in predecessors))
    if set(ranks) != set(range(count)):
        raise StableSortMappingError("predecessor relation does not define unique ranks")

    scattered: list[tuple[int, int] | None] = [None] * count
    for item_id, rank in enumerate(ranks):
        scattered[rank] = (normalized[item_id], item_id)
    if any(record is None for record in scattered):
        raise StableSortMappingError("rank scatter is incomplete")
    return StableSortOutcome(
        ranks_by_item_id=tuple(ranks),
        sorted_records=tuple(record for record in scattered if record is not None),
    )


def stable_sort_oracle(values: Sequence[int]) -> tuple[tuple[int, int], ...]:
    """Independent final-result oracle using Python's specified stable sort."""

    return tuple(sorted(
        ((int(value), item_id) for item_id, value in enumerate(values)),
        key=lambda record: (record[0], record[1]),
    ))


def primitive_index_attack_rows(
    logical_rows: Sequence[Sequence[int]], indexed_order: Sequence[int],
) -> tuple[tuple[int, int], ...]:
    """Model the silent CP002 bug: report primitive position, not item id."""

    physical_position = {
        int(item_id): position for position, item_id in enumerate(indexed_order)
    }
    return tuple(sorted(
        (int(source_id), physical_position[int(predecessor_id)])
        for source_id, predecessor_id in logical_rows
    ))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute_stable_sort(
    values: Sequence[int],
    *,
    native: str | Path,
    optix_include: str | Path,
    cuda_include: str | Path,
    optix_sdk: str,
    compute_capability: str,
    any_hit_proof: str | Path | None = None,
    any_hit_proof_sha256: str | None = None,
    proof_kind: str = "external_machine_checked_order_independence_v1",
    indexed_order: Sequence[int] | None = None,
    source_order: Sequence[int] | None = None,
    capacity_override: int | None = None,
) -> dict[str, object]:
    """Execute one untimed public V4 stable-sort instance on OptiX."""

    encoding = encode_stable_sort(
        values, indexed_order=indexed_order, source_order=source_order)
    capacity = encoding.capacity if capacity_override is None else int(capacity_override)
    protocol = BoundedRelationProtocol(
        capacity=capacity,
        minimum_overlap_f32=encoding.minimum_overlap_f32,
    )
    physical_plan = standard_protocol_physical_plan(protocol)
    if (any_hit_proof is None) == (any_hit_proof_sha256 is None):
        raise StableSortMappingError(
            "supply exactly one of any_hit_proof or any_hit_proof_sha256"
        )
    if any_hit_proof is not None:
        proof_digest = _sha256(Path(any_hit_proof).expanduser().resolve())
    else:
        proof_digest = str(any_hit_proof_sha256).lower()
        if len(proof_digest) != 64 or any(
            character not in "0123456789abcdef" for character in proof_digest
        ):
            raise StableSortMappingError("any_hit_proof_sha256 must be SHA-256 hex")
    proof = AnyHitProtocolProof(
        callback_ir_sha256=physical_plan.callback_ir_sha256,
        effect_digest=physical_plan.effect_digest,
        proof_sha256=proof_digest,
        proof_kind=proof_kind,
    )
    target = V4Target.from_native(
        native,
        optix_sdk=optix_sdk,
        compute_capability=compute_capability,
    )
    capability = tuple(int(item) for item in compute_capability.split("."))
    toolchain = V4Toolchain.current(
        compute_capability=capability,
        optix_include=optix_include,
        cuda_include=cuda_include,
    )

    verified = compile_protocol_program(
        protocol,
        physical_plan=physical_plan,
        any_hit_proof=proof,
    )
    materialized = verified.materialize(target=target, toolchain=toolchain)
    prepared = materialized.prepare(
        BoundedRelationStaticInput(encoding.indexed_boxes))
    try:
        # The application oracle is deliberately not passed into execution.
        result = prepared.execute(BoundedRelationBatch(encoding.source_boxes))
        lifecycle = prepared.lifecycle_receipt
    finally:
        prepared.close()
        prepared.close()

    expected_rows = predecessor_relation_oracle(encoding.values)
    geometry_rows = geometry_relation_reference(encoding)
    if result.output != expected_rows or geometry_rows != expected_rows:
        raise StableSortMappingError(
            "RT relation, geometry model, and pairwise order oracle disagree"
        )
    outcome = stable_sort_from_relation(encoding.values, result.output)
    oracle = stable_sort_oracle(encoding.values)
    if outcome.sorted_records != oracle:
        raise StableSortMappingError("RT-derived stable order disagrees with oracle")

    attack_rows = primitive_index_attack_rows(result.output, encoding.indexed_order)
    try:
        attack_outcome = stable_sort_from_relation(encoding.values, attack_rows)
        attack_observation: dict[str, object] = {
            "postcheck": "RETURNED",
            "sorted_records": attack_outcome.sorted_records,
            "matches_oracle": attack_outcome.sorted_records == oracle,
        }
    except StableSortMappingError as error:
        attack_observation = {
            "postcheck": "REJECTED",
            "reason": str(error),
            "matches_oracle": False,
        }

    return {
        "schema": "rtdl.v4.public_stable_sort_demo.v1",
        "input_records": tuple(
            (value, item_id) for item_id, value in enumerate(encoding.values)),
        "order_codes": encoding.order_codes,
        "indexed_physical_order": encoding.indexed_order,
        "source_launch_order": encoding.source_order,
        "relation_rows": result.output,
        "ranks_by_item_id": outcome.ranks_by_item_id,
        "sorted_records": outcome.sorted_records,
        "python_stable_oracle": oracle,
        "primitive_index_attack": {
            "rows": attack_rows,
            **attack_observation,
        },
        "program_identity_sha256": verified.identity.identity_sha256,
        "executable_identity_sha256": result.executable_identity.identity_sha256,
        "physical_executor_classification": result.traversal_receipt[
            "physical_executor_classification"],
        "lifecycle": lifecycle,
        "expected_rows_passed_into_execution": False,
        "sorting_algorithm_proved": False,
        "arbitrary_sorting_supported": False,
        "application_mapping_verified_by_rtdl": False,
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
    }


def _csv_ints(value: str) -> tuple[int, ...]:
    if not value.strip():
        return ()
    return tuple(int(item.strip()) for item in value.split(","))


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--values", default="2,1,2,0")
    parser.add_argument("--indexed-order", default="2,0,3,1")
    parser.add_argument("--source-order", default="3,2,1,0")
    parser.add_argument("--capacity", type=int)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    proof_group = parser.add_mutually_exclusive_group(required=True)
    proof_group.add_argument("--any-hit-proof", type=Path)
    proof_group.add_argument("--any-hit-proof-sha256")
    parser.add_argument(
        "--proof-kind",
        default="external_machine_checked_order_independence_v1",
    )
    return parser.parse_args()


def main() -> None:
    args = _arguments()
    result = execute_stable_sort(
        _csv_ints(args.values),
        native=args.native,
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
        any_hit_proof=args.any_hit_proof,
        any_hit_proof_sha256=args.any_hit_proof_sha256,
        proof_kind=args.proof_kind,
        indexed_order=_csv_ints(args.indexed_order),
        source_order=_csv_ints(args.source_order),
        capacity_override=args.capacity,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
