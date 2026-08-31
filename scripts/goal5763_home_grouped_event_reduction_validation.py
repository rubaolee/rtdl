#!/usr/bin/env python3
"""Home functional closure for V4 M5 grouped-event reduction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from rtdsl.action_numba_continuation import (
    execute_numba_grouped_i64x2_count_sum,
    prepare_numba_grouped_i64x2_count_sum_columns,
)
from rtdsl.v4_grouped_event_reduction import (
    EventFieldProjection,
    EventFieldSource,
    EventProducerCompletionKind,
    GroupedEventReductionSchema,
    I64LookupTable,
    compile_grouped_event_reduction,
    execute_grouped_event_reduction,
    materialize_verified_grouped_event_batch,
    reference_grouped_i64x2_count_sum,
    verify_event_producer_evidence,
)


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _lane(result: dict[str, object], name: str) -> dict[str, object]:
    return next(row for row in result["lanes"] if row["lane"] == name)


def _run(
    *,
    lane_name: str,
    producer,
    schema,
    lookups,
    expected,
    traversal_receipt,
) -> dict[str, object]:
    batch = materialize_verified_grouped_event_batch(
        schema, producer, lookup_tables=lookups)
    compiled = compile_grouped_event_reduction(
        schema, producer, lookup_tables=lookups)
    oracle = reference_grouped_i64x2_count_sum(batch)
    if oracle != expected:
        raise RuntimeError(f"{lane_name}: independent oracle mismatch: {oracle!r}")
    actual = execute_grouped_event_reduction(compiled, batch)
    if actual.rows != oracle:
        raise RuntimeError(f"{lane_name}: device grouped result mismatch")
    metadata = actual.device_metadata
    certificate = metadata.get("device_column_certificate") or {}
    return {
        "schema": "rtdl.goal5763.home_grouped_event_lane.v1",
        "lane": lane_name,
        "producer_contract_sha256": producer.producer_contract_sha256,
        "producer_authority_nonce": producer.authority_nonce,
        "producer_completion_kind": producer.completion_kind.value,
        "semantic_completion_authority_sha256": (
            producer.semantic_completion_authority_sha256),
        "producer_output_sha256": producer.producer_output_sha256,
        "producer_semantic_rows": producer.producer_semantic_rows,
        "producer_semantic_rows_sha256": _digest(
            producer.producer_semantic_rows),
        "traversal_receipt_sha256": producer.traversal_receipt_sha256,
        "traversal_receipt": traversal_receipt,
        "native_library_sha256": producer.native_library_sha256,
        "grouped_schema": schema.to_dict(),
        "projection_lookup_tables": tuple({
            "table_sha256": table.table_sha256,
            "rows": table.rows,
        } for table in lookups),
        "compiled": compiled.to_dict(),
        "event_batch_sha256": batch.content_sha256,
        "event_row_count": batch.row_count,
        "event_columns": {
            "event_id": batch.event_id,
            "key0": batch.key0,
            "key1": batch.key1,
            "signed_value": batch.signed_value,
        },
        "expected_rows": expected,
        "oracle_rows": oracle,
        "actual_rows": actual.rows,
        "output_sha256": actual.output_sha256,
        "exact_output_matched": True,
        "behavioral_true_optix_producer": True,
        "numba_cuda_checked_grouped_reducer_executed": True,
        "input_order_verified_on_device": bool(
            metadata.get("input_order_verified_on_device")),
        "device_signed_overflow_policy": "fail_closed",
        "device_metadata": metadata,
        "device_certificate_metadata": certificate,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--m2-result", required=True, type=Path)
    parser.add_argument("--m4-result", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    m2 = _load(args.m2_result)
    m4 = _load(args.m4_result)

    # RayJoin: exact point-location rows are the verified logical events.
    # The closed projection uses the exact face and segment-group metadata;
    # a value of one counts point rows without app-owned grouping code.
    point = _lane(
        m4, "rayjoin.planar_map.directed_segment_point_location_2d.v1")
    semantic_rows = tuple(
        (int(row[0]), int(row[2]))
        for row in point["actual"]["rows"]
        if int(row[2]) != 0xFFFFFFFF
    )
    rayjoin_producer = verify_event_producer_evidence(
        semantic_rows,
        producer_contract_sha256=point["exact_authority_nonce"],
        maximum_event_rows=int(point["input"]["candidate_capacity"]),
        traversal_receipt=point["traversal_receipt"],
        completion_kind=(
            EventProducerCompletionKind.VERIFIED_EXACT_PARTNER_COMPLETION),
        semantic_completion_authority_sha256=point["exact_authority_nonce"],
    )
    face_table = I64LookupTable.from_rows(
        (int(row[0]), int(row[1])) for row in point["actual"]["rows"]
        if int(row[2]) != 0xFFFFFFFF)
    segment_group_table = I64LookupTable.from_rows(
        (int(row["segment_id"]), int(row["group_id"]))
        for row in point["input"]["segments"])
    rayjoin_schema = GroupedEventReductionSchema(
        point["exact_authority_nonce"],
        int(point["input"]["candidate_capacity"]),
        EventFieldProjection(
            EventFieldSource.SOURCE_LOOKUP, face_table.table_sha256),
        EventFieldProjection(
            EventFieldSource.ITEM_LOOKUP, segment_group_table.table_sha256),
        EventFieldProjection(EventFieldSource.CONSTANT, constant_i64=1),
    )
    rayjoin = _run(
        lane_name="rayjoin.logical_events.grouped_i64x2_count_sum.v1",
        producer=rayjoin_producer,
        schema=rayjoin_schema,
        lookups=(face_table, segment_group_table),
        expected=((10, 1, 3, 3), (30, 3, 1, 1)),
        traversal_receipt=point["traversal_receipt"],
    )

    # A real non-RayJoin consumer: group the existing authored polygon-set
    # Jaccard broad-phase relation by left/right polygon family and accumulate
    # signed source weights.  It executes the exact same product contract.
    polygon = _lane(m2, "polygon_set_jaccard.aabb_candidate_stage.v1")
    polygon_producer = verify_event_producer_evidence(
        polygon["observed_rows"],
        producer_contract_sha256=polygon["contract_sha256"],
        maximum_event_rows=int(polygon["capacity"]),
        traversal_receipt=polygon["traversal_receipt"],
    )
    source_ids = tuple(sorted({int(row[0]) for row in polygon["observed_rows"]}))
    item_ids = tuple(sorted({int(row[1]) for row in polygon["observed_rows"]}))
    source_family = I64LookupTable.from_rows((value, 0) for value in source_ids)
    item_family = I64LookupTable.from_rows((value, 0) for value in item_ids)
    source_weight = I64LookupTable.from_rows(
        (value, 5 if index == 0 else -2)
        for index, value in enumerate(source_ids))
    polygon_schema = GroupedEventReductionSchema(
        polygon["contract_sha256"], int(polygon["capacity"]),
        EventFieldProjection(
            EventFieldSource.SOURCE_LOOKUP, source_family.table_sha256),
        EventFieldProjection(
            EventFieldSource.ITEM_LOOKUP, item_family.table_sha256),
        EventFieldProjection(
            EventFieldSource.SOURCE_LOOKUP, source_weight.table_sha256),
    )
    expected_polygon = {}
    weights = source_weight.as_mapping()
    for source_id, _ in polygon["observed_rows"]:
        count, total = expected_polygon.get((0, 0), (0, 0))
        expected_polygon[(0, 0)] = (count + 1, total + weights[int(source_id)])
    polygon_expected = tuple(
        (key[0], key[1], value[0], value[1])
        for key, value in sorted(expected_polygon.items()))
    polygon_lane = _run(
        lane_name="polygon_set_jaccard.grouped_overlap_incidence.v1",
        producer=polygon_producer,
        schema=polygon_schema,
        lookups=(source_family, item_family, source_weight),
        expected=polygon_expected,
        traversal_receipt=polygon["traversal_receipt"],
    )

    # Device attack 1: a noncanonical batch must be rejected by the reducer's
    # device order certificate.  This deliberately invokes the reused partner
    # below the sealed V4 materializer, which always canonicalizes.
    attack_program = compile_grouped_event_reduction(
        polygon_schema, polygon_producer,
        lookup_tables=(source_family, item_family, source_weight),
    ).action_program
    unsorted = {
        "event_id": np.asarray([0, 1], dtype=np.int64),
        "key0": np.asarray([2, 1], dtype=np.int64),
        "key1": np.asarray([0, 0], dtype=np.int64),
        "signed_value": np.asarray([1, 1], dtype=np.int64),
    }
    prepared = prepare_numba_grouped_i64x2_count_sum_columns(
        attack_program, unsorted)
    device = execute_numba_grouped_i64x2_count_sum(prepared)
    try:
        try:
            device.to_host_reductions()
        except Exception as exc:
            if "group_key_order_certificate_violated" not in str(exc):
                raise
            order_attack = {
                "passed": True,
                "observed_code": "group_key_order_certificate_violated",
                "failure_was_device_status_derived": True,
            }
        else:
            raise RuntimeError("noncanonical grouped keys escaped device check")
    finally:
        device.close()
        prepared.close()

    # Device attack 2: checked signed-I64 overflow must fail from the device
    # status word rather than wrapping or relying on Python arithmetic.
    overflow_rows = tuple(polygon["observed_rows"][:2])
    overflow_receipt = dict(polygon["traversal_receipt"])
    overflow_producer = verify_event_producer_evidence(
        overflow_rows,
        producer_contract_sha256=polygon["contract_sha256"],
        maximum_event_rows=int(polygon["capacity"]),
        traversal_receipt=overflow_receipt,
        completion_kind=(
            EventProducerCompletionKind.VERIFIED_EXACT_PARTNER_COMPLETION),
        semantic_completion_authority_sha256=_digest({
            "kind": "goal5763_overflow_attack_subset_v1",
            "source_output": polygon["output_sha256"],
            "rows": overflow_rows,
        }),
    )
    overflow_source_ids = tuple(sorted({int(row[0]) for row in overflow_rows}))
    overflow_item_ids = tuple(sorted({int(row[1]) for row in overflow_rows}))
    overflow_source_key = I64LookupTable.from_rows(
        (value, 0) for value in overflow_source_ids)
    overflow_item_key = I64LookupTable.from_rows(
        (value, 0) for value in overflow_item_ids)
    overflow_values = I64LookupTable.from_rows(
        (value, (1 << 63) - 1) for value in overflow_source_ids)
    overflow_schema = GroupedEventReductionSchema(
        polygon["contract_sha256"], int(polygon["capacity"]),
        EventFieldProjection(
            EventFieldSource.SOURCE_LOOKUP, overflow_source_key.table_sha256),
        EventFieldProjection(
            EventFieldSource.ITEM_LOOKUP, overflow_item_key.table_sha256),
        EventFieldProjection(
            EventFieldSource.SOURCE_LOOKUP, overflow_values.table_sha256),
    )
    overflow_tables = (
        overflow_source_key, overflow_item_key, overflow_values)
    overflow_batch = materialize_verified_grouped_event_batch(
        overflow_schema, overflow_producer, lookup_tables=overflow_tables)
    overflow_compiled = compile_grouped_event_reduction(
        overflow_schema, overflow_producer, lookup_tables=overflow_tables)
    try:
        execute_grouped_event_reduction(overflow_compiled, overflow_batch)
    except Exception as exc:
        if "signed_reduction_overflow" not in str(exc):
            raise
        overflow_attack = {
            "passed": True,
            "observed_code": "signed_reduction_overflow",
            "failure_was_device_status_derived": True,
        }
    else:
        raise RuntimeError("signed-I64 device overflow did not fail closed")

    result = {
        "schema": "rtdl.goal5763.home_grouped_event_reduction_result.v1",
        "goal": 5763,
        "scope": "functional_only_no_registered_performance_timing",
        "m2_result_sha256": hashlib.sha256(args.m2_result.read_bytes()).hexdigest(),
        "m4_result_sha256": hashlib.sha256(args.m4_result.read_bytes()).hexdigest(),
        "lane_count": 2,
        "exact_output_count": 2,
        "behavioral_true_optix_producer_count": 2,
        "numba_cuda_checked_grouped_reducer_count": 2,
        "registered_performance_timing_count": 0,
        "one_product_contract_for_both_consumers": (
            rayjoin["compiled"]["template_contract_sha256"]
            == polygon_lane["compiled"]["template_contract_sha256"]),
        "per_producer_semantic_identity_is_intentionally_distinct": (
            rayjoin["compiled"]["action_semantic_digest"]
            != polygon_lane["compiled"]["action_semantic_digest"]),
        "attacks": {
            "device_key_order": order_attack,
            "device_signed_i64_overflow": overflow_attack,
            "producer_capacity": m2["overflow_attack"],
        },
        "lanes": (rayjoin, polygon_lane),
    }
    (args.output / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "exact": 2,
        "behavioral_optix_producers": 2,
        "device_grouped_reducers": 2,
        "attacks": 3,
        "result": str(args.output / "RESULT.json"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
