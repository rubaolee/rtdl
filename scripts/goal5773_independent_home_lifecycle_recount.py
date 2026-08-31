#!/usr/bin/env python3
"""Independent JSON/byte recount of Goal5773 Home lifecycle evidence.

This verifier deliberately imports no RTDL module and no Paper-App route.
It checks the preserved native bytes, exact outputs, traversal failure fields,
session reuse and the grouped eager-specialization boundary directly from the
four result files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"non-object result: {path}")
    return value


def _equivalent(left: object, right: object) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return left is right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isfinite(float(left)) and math.isfinite(float(right)) \
            and abs(float(left) - float(right)) <= 1.0e-9
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(
            _equivalent(a, b) for a, b in zip(left, right, strict=True))
    if isinstance(left, dict) and isinstance(right, dict):
        return set(left) == set(right) and all(
            _equivalent(left[key], right[key]) for key in left)
    return left == right


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    native = args.evidence / "librtdl_optix.so"
    native_sha = _sha(native)
    names = ("MULTIROUND", "HIERARCHY", "TRIANGLE", "PARTICLE_RELATION")
    result_by_name = {
        name: _load(args.evidence / f"{name}.json") for name in names
    }
    records: list[tuple[str, dict[str, object]]] = []
    for group, result in result_by_name.items():
        if result.get("native_library_sha256") != native_sha:
            raise RuntimeError(f"{group}: native identity mismatch")
        if result.get("formal_performance_row_created") is not False \
                or result.get("cold_result_replaced") is not False \
                or result.get("speed_or_no_slower_claimed") is not False:
            raise RuntimeError(f"{group}: claim boundary changed")
        for row in result.get("records", ()):  # type: ignore[assignment]
            if not isinstance(row, dict):
                raise RuntimeError(f"{group}: malformed record")
            records.append((group, row))

    paper_lanes: dict[str, list[dict[str, object]]] = {}
    nonpaper_lanes: dict[str, list[dict[str, object]]] = {}
    for group, row in records:
        lane = str(row.get("application") or row.get("consumer"))
        target = (
            nonpaper_lanes
            if lane == "nonpaper_hierarchical_field_intensity"
            else paper_lanes
        )
        target.setdefault(f"{group}:{lane}", []).append(row)
        if row.get("matched") is not True or not _equivalent(
                row.get("output"), row.get("expected")):
            raise RuntimeError(f"{group}:{lane}: output mismatch")
        if row.get("physical_executor_classification") != "optix_traversal_observed":
            raise RuntimeError(f"{group}:{lane}: traversal not observed")
        successful = row.get("successful_launch_count")
        if not isinstance(successful, int) or successful <= 0 \
                or row.get("complete_context_launch_count") != successful:
            raise RuntimeError(f"{group}:{lane}: incomplete launch binding")
        for field in (
            "failed_launch_count", "incomplete_context_launch_count",
            "pending_context_at_finish", "session_error",
        ):
            if row.get(field) != 0:
                raise RuntimeError(f"{group}:{lane}: {field} is nonzero")
        if not row.get("first_traversable") or not row.get("last_traversable"):
            raise RuntimeError(f"{group}:{lane}: missing traversable")
        if row.get("provider_library_sha256") != native_sha:
            raise RuntimeError(f"{group}:{lane}: provider identity mismatch")
        seconds = row.get("registered_prepared_execution_seconds")
        prepare = row.get("reported_total_prepare_seconds")
        if not isinstance(seconds, (float, int)) or not math.isfinite(seconds) \
                or seconds <= 0.0 or not isinstance(prepare, (float, int)) \
                or not math.isfinite(prepare) or prepare <= 0.0:
            raise RuntimeError(f"{group}:{lane}: invalid lifecycle observations")

    if len(paper_lanes) != 13 or len(nonpaper_lanes) != 1:
        raise RuntimeError(
            f"lane shape mismatch: paper={len(paper_lanes)}, "
            f"nonpaper={len(nonpaper_lanes)}")
    for lane, rows in {**paper_lanes, **nonpaper_lanes}.items():
        rows.sort(key=lambda row: int(row["call_index"]))
        if len(rows) != 2 or [row.get("execution_count") for row in rows] != [1, 2] \
                or len({row.get("session_identity") for row in rows}) != 1:
            raise RuntimeError(f"{lane}: cross-call ownership not proved")

    grouped = paper_lanes.get(
        "PARTICLE_RELATION:rayjoin_logical_events.grouped_i64x2_count_sum.v1")
    if grouped is None:
        raise RuntimeError("grouped lifecycle lane is absent")
    for row in grouped:
        receipt = row.get("grouped_lifecycle_receipt")
        if not isinstance(receipt, dict) \
                or receipt.get("first_execute_may_trigger_numba_jit") is not False:
            raise RuntimeError("grouped first execute still permits lazy JIT")
        specialization = receipt.get("eager_specialization")
        if not isinstance(specialization, dict) \
                or specialization.get("complete_physical_route_executed") is not True \
                or specialization.get("synthetic_row_count") != 1 \
                or specialization.get("registered_query_count") != 0 \
                or specialization.get("kernel_launch_delta", 0) < 1 \
                or specialization.get("runtime_speedup_claimed") is not False:
            raise RuntimeError("grouped eager-specialization receipt is invalid")

    output = {
        "schema": "rtdl.goal5773.independent_home_lifecycle_recount.v1",
        "native_library_sha256": native_sha,
        "input_result_sha256": {
            name: _sha(args.evidence / f"{name}.json") for name in names
        },
        "paper_application_count": 9,
        "paper_lane_count": len(paper_lanes),
        "paper_call_count": sum(map(len, paper_lanes.values())),
        "nonpaper_second_consumer_lane_count": len(nonpaper_lanes),
        "total_call_count": len(records),
        "exact_output_count": len(records),
        "behavioral_true_optix_count": len(records),
        "failed_or_unbound_count": 0,
        "grouped_eager_specialization_verified": True,
        "paper_app_route_imported": False,
        "rtdl_product_module_imported": False,
        "formal_performance_row_created": False,
        "speed_or_no_slower_claimed": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
