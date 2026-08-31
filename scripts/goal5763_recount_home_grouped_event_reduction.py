#!/usr/bin/env python3
"""Independent raw recount for Goal5763.

This verifier intentionally imports no RTDL product, compiler, application,
or submitted statistics module.  It rebuilds the two producer row sets from
the frozen M2/M4 inputs, reapplies the closed projections, recomputes the
grouped COUNT/SUM oracle, and checks the behavioral traversal receipts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


I64_MIN = -(1 << 63)
I64_MAX = (1 << 63) - 1


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _lane(result: dict[str, object], name: str) -> dict[str, object]:
    rows = [row for row in result["lanes"] if row["lane"] == name]
    if len(rows) != 1:
        raise AssertionError(f"expected exactly one lane {name!r}")
    return rows[0]


def _verify_receipt(lane: dict[str, object]) -> None:
    receipt = lane["traversal_receipt"]
    body = dict(receipt)
    claimed = body.pop("receipt_sha256")
    if claimed != _digest(body) or claimed != lane["traversal_receipt_sha256"]:
        raise AssertionError("traversal receipt digest mismatch")
    snapshot = receipt["native_snapshot"]
    successful = snapshot["successful_launch_count"]
    if not (
        receipt["physical_executor_classification"]
        == "optix_traversal_observed"
        and successful > 0
        and snapshot["complete_context_launch_count"] == successful
        and snapshot["failed_launch_count"] == 0
        and snapshot["incomplete_context_launch_count"] == 0
        and snapshot["pending_context_at_finish"] == 0
        and snapshot["session_error"] == 0
        and snapshot["first_traversable"]
        and snapshot["last_traversable"]
        and receipt["expected_program_observed_at_receipt_edge"] is True
    ):
        raise AssertionError("behavioral true-OptiX receipt did not close")
    if receipt["provider_library_sha256"] != lane["native_library_sha256"]:
        raise AssertionError("native identity differs from producer receipt")


def _projection(
    spec: dict[str, object], source_id: int, item_id: int,
    lookups: dict[str, dict[int, int]],
) -> int:
    source = spec["source"]
    if source == "source_id_i64":
        return source_id
    if source == "item_id_i64":
        return item_id
    if source == "constant_i64":
        return int(spec["constant_i64"])
    table = lookups[spec["lookup_sha256"]]
    identity = source_id if source == "source_lookup_i64" else item_id
    if identity not in table:
        raise AssertionError("projection lookup is incomplete")
    return table[identity]


def _recount_lane(
    lane: dict[str, object], expected_semantic_rows: list[list[int]],
) -> dict[str, object]:
    _verify_receipt(lane)
    semantic_rows = lane["producer_semantic_rows"]
    if semantic_rows != expected_semantic_rows:
        raise AssertionError(f"{lane['lane']}: frozen producer rows differ")
    if _digest(semantic_rows) != lane["producer_semantic_rows_sha256"]:
        raise AssertionError("producer semantic-row digest mismatch")
    if lane["producer_completion_kind"] == "direct_canonical_relation_v1":
        if not (
            lane["producer_semantic_rows_sha256"]
            == lane["producer_output_sha256"]
            == lane["traversal_receipt"]["output_digest"]
        ):
            raise AssertionError("direct producer rows are not receipt-bound")
    else:
        authority = lane["semantic_completion_authority_sha256"]
        if not isinstance(authority, str) or len(authority) != 64:
            raise AssertionError("exact-partner completion authority is absent")

    schema = dict(lane["grouped_schema"])
    schema_sha = schema.pop("schema_sha256")
    if _digest(schema) != schema_sha:
        raise AssertionError("grouped schema digest mismatch")
    if schema["producer_contract_sha256"] != lane["producer_contract_sha256"]:
        raise AssertionError("schema/producer contract mismatch")
    if len(semantic_rows) > schema["maximum_event_rows"]:
        raise AssertionError("producer capacity exceeded")

    lookups: dict[str, dict[int, int]] = {}
    for table in lane["projection_lookup_tables"]:
        rows = table["rows"]
        if _digest(rows) != table["table_sha256"]:
            raise AssertionError("lookup digest mismatch")
        keys = [int(row[0]) for row in rows]
        if keys != sorted(keys) or len(keys) != len(set(keys)):
            raise AssertionError("lookup keys are not canonical and unique")
        lookups[table["table_sha256"]] = {
            int(row[0]): int(row[1]) for row in rows
        }

    projected: list[tuple[int, int, int, int]] = []
    for event_id, row in enumerate(semantic_rows):
        source_id, item_id = map(int, row)
        projected.append((
            event_id,
            _projection(schema["key0"], source_id, item_id, lookups),
            _projection(schema["key1"], source_id, item_id, lookups),
            _projection(schema["signed_value"], source_id, item_id, lookups),
        ))
    projected.sort(key=lambda row: (row[1], row[2], row[0]))
    columns = {
        "event_id": [row[0] for row in projected],
        "key0": [row[1] for row in projected],
        "key1": [row[2] for row in projected],
        "signed_value": [row[3] for row in projected],
    }
    if columns != lane["event_columns"]:
        raise AssertionError("compiler-owned event projection mismatch")
    ordered_columns = [
        columns["event_id"], columns["key0"], columns["key1"],
        columns["signed_value"],
    ]
    if _digest(ordered_columns) != lane["event_batch_sha256"]:
        raise AssertionError("event batch digest mismatch")

    grouped: dict[tuple[int, int], tuple[int, int]] = {}
    for _, key0, key1, value in projected:
        count, total = grouped.get((key0, key1), (0, 0))
        total += value
        if not I64_MIN <= total <= I64_MAX:
            raise AssertionError("unexpected signed overflow in successful lane")
        grouped[(key0, key1)] = (count + 1, total)
    rows = [
        [key[0], key[1], grouped[key][0], grouped[key][1]]
        for key in sorted(grouped)
    ]
    if not (
        rows == lane["expected_rows"]
        == lane["oracle_rows"]
        == lane["actual_rows"]
        and _digest(rows) == lane["output_sha256"]
        and lane["exact_output_matched"] is True
        and lane["input_order_verified_on_device"] is True
    ):
        raise AssertionError("grouped device output did not match independent oracle")
    return {
        "lane": lane["lane"],
        "event_rows": len(projected),
        "group_rows": len(rows),
        "output_sha256": _digest(rows),
        "behavioral_true_optix": True,
        "device_checked_grouped_reducer": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", required=True, type=Path)
    parser.add_argument("--m2-result", required=True, type=Path)
    parser.add_argument("--m4-result", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result, m2, m4 = map(_load, (args.result, args.m2_result, args.m4_result))
    if result["m2_result_sha256"] != _file_sha(args.m2_result) \
            or result["m4_result_sha256"] != _file_sha(args.m4_result):
        raise AssertionError("frozen predecessor result identity mismatch")

    point = _lane(m4, "rayjoin.planar_map.directed_segment_point_location_2d.v1")
    rayjoin_rows = [
        [int(row[0]), int(row[2])] for row in point["actual"]["rows"]
        if int(row[2]) != 0xFFFFFFFF
    ]
    polygon = _lane(m2, "polygon_set_jaccard.aabb_candidate_stage.v1")
    polygon_rows = [[int(a), int(b)] for a, b in polygon["observed_rows"]]
    recounted = [
        _recount_lane(_lane(
            result, "rayjoin.logical_events.grouped_i64x2_count_sum.v1"),
            rayjoin_rows),
        _recount_lane(_lane(
            result, "polygon_set_jaccard.grouped_overlap_incidence.v1"),
            polygon_rows),
    ]
    if not (
        result["one_product_contract_for_both_consumers"] is True
        and result["per_producer_semantic_identity_is_intentionally_distinct"] is True
        and len({lane["compiled"]["template_contract_sha256"]
                 for lane in result["lanes"]}) == 1
        and len({lane["compiled"]["action_semantic_digest"]
                 for lane in result["lanes"]}) == 2
        and all(attack["passed"] for attack in result["attacks"].values())
        and result["registered_performance_timing_count"] == 0
    ):
        raise AssertionError("result-level contract or attack gate failed")
    output = {
        "schema": "rtdl.goal5763.independent_recount.v1",
        "result_sha256": _file_sha(args.result),
        "m2_result_sha256": _file_sha(args.m2_result),
        "m4_result_sha256": _file_sha(args.m4_result),
        "lane_count": 2,
        "exact_output_count": 2,
        "behavioral_true_optix_count": 2,
        "device_checked_grouped_reducer_count": 2,
        "one_app_neutral_template_count": 1,
        "attack_count": 3,
        "registered_performance_timing_count": 0,
        "lanes": recounted,
        "imports_product_or_application_module": False,
    }
    args.output.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
