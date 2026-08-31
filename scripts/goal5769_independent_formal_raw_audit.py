#!/usr/bin/env python3
"""Independent postrun audit for the frozen Goal5769 V2/V3/V4 matrix.

This verifier intentionally imports no controller, worker, application
frontdoor, evaluator, or packaged recount.  It reconstructs the 312-worker
cohort and all 26 statistical rows directly from the immutable raw JSON files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import statistics


BASELINES = (
    "v2_direct_true_optix_backport",
    "v3_compiler_true_optix",
)
V4 = "v4_restricted_callback_true_optix"


def _canonical(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _bootstrap(values: tuple[float, ...], seed: int) -> tuple[float, float]:
    generator = random.Random(seed)
    medians = sorted(
        statistics.median(generator.choices(values, k=len(values)))
        for _ in range(10_000)
    )
    return medians[249], medians[9749]


def audit(plan_path: Path, raw_root: Path) -> dict[str, object]:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    body = dict(plan)
    plan_sha = body.pop("plan_sha256", None)
    if plan_sha != _canonical(body):
        raise RuntimeError("plan digest mismatch")
    expected = {row["unit_id"]: row for row in plan["units"]}
    paths = sorted(raw_root.glob("*/RESULT.json"))
    if len(paths) != 312 or len(expected) != 312:
        raise RuntimeError("audit requires exactly 312 planned and raw workers")
    records: dict[str, dict[str, object]] = {}
    pids: set[int] = set()
    payloads: list[dict[str, object]] = []
    for path in paths:
        payloads.append({
            "path": path.relative_to(raw_root).as_posix(),
            "sha256": _file_sha(path),
            "bytes": path.stat().st_size,
        })
        row = json.loads(path.read_text(encoding="utf-8"))
        unit = row.get("unit")
        if not isinstance(unit, dict):
            raise RuntimeError("worker unit is malformed")
        unit_id = unit.get("unit_id")
        if unit_id not in expected or unit != expected[unit_id] or unit_id in records:
            raise RuntimeError("worker unit unknown, drifted, or duplicated")
        if row.get("plan_sha256") != plan_sha \
                or row.get("formal_identity_sha256") != plan["formal_identity_sha256"]:
            raise RuntimeError("worker formal identity drift")
        pid = row.get("parent_pid")
        if type(pid) is not int or pid <= 0 or pid in pids:
            raise RuntimeError("fresh parent PID contract failed")
        pids.add(pid)
        endpoint = row.get("endpoint")
        if not isinstance(endpoint, dict) or endpoint.get("matched") is not True:
            raise RuntimeError("worker correctness failed")
        if endpoint.get("lane_id") != unit["lane_id"] \
                or endpoint.get("method") != unit["method"]:
            raise RuntimeError("endpoint label drift")
        if endpoint.get("native_library_sha256") != plan["native_library_sha256"]:
            raise RuntimeError("native identity drift")
        if endpoint.get("output_sha256") != endpoint.get("expected_sha256"):
            raise RuntimeError("output and oracle digests differ")
        if endpoint.get("stock_v2_or_v3_claimed") is not False \
                or endpoint.get("default_selected_between_application_algorithms") is not False:
            raise RuntimeError("method provenance or DEFAULT claim drift")
        if endpoint.get("comparator_inside_registered_timer") is not False:
            raise RuntimeError("comparator entered the registered timer")
        seconds = endpoint.get("registered_complete_seconds")
        if type(seconds) not in (int, float) or not math.isfinite(seconds) or seconds <= 0:
            raise RuntimeError("registered endpoint timer invalid")
        receipt = endpoint.get("traversal_receipt")
        if not isinstance(receipt, dict):
            raise RuntimeError("traversal receipt absent")
        receipt_body = dict(receipt)
        receipt_sha = receipt_body.pop("receipt_sha256", None)
        if receipt_sha != _canonical(receipt_body) \
                or receipt.get("physical_executor_classification") \
                != "optix_traversal_observed":
            raise RuntimeError("behavioral OptiX receipt invalid")
        snapshot = receipt.get("native_snapshot")
        if not isinstance(snapshot, dict):
            raise RuntimeError("native traversal snapshot absent")
        launches = snapshot.get("successful_launch_count")
        if type(launches) is not int or launches <= 0 \
                or snapshot.get("complete_context_launch_count") != launches:
            raise RuntimeError("traversal launch binding incomplete")
        if any(snapshot.get(name) != 0 for name in (
            "failed_launch_count", "incomplete_context_launch_count",
            "pending_context_at_finish", "session_error",
        )):
            raise RuntimeError("traversal receipt contains a failed state")
        if any(snapshot.get(name) in (None, 0) for name in (
            "first_traversable", "last_traversable",
            "first_program_bundle_id", "last_program_bundle_id",
        )):
            raise RuntimeError("traversal receipt edge binding absent")
        records[str(unit_id)] = row
    if set(records) != set(expected):
        raise RuntimeError("raw cohort is incomplete")

    rows: list[dict[str, object]] = []
    row_index = 0
    for lane_id in plan["lane_ids"]:
        cohort = [row for row in records.values()
                  if row["unit"]["lane_id"] == lane_id]
        if len(cohort) != 24:
            raise RuntimeError("lane is not balanced at 24 workers")
        inputs = {row["endpoint"]["input_sha256"] for row in cohort}
        outputs = {row["endpoint"]["output_sha256"] for row in cohort}
        expected_outputs = {row["endpoint"]["expected_sha256"] for row in cohort}
        contract = plan["lane_contracts"][lane_id]
        if inputs != {contract["input_sha256"]} \
                or outputs != {contract["output_sha256"]} \
                or expected_outputs != {contract["expected_sha256"]}:
            raise RuntimeError("lane input/output contract drift")
        cells = {
            (row["unit"]["block_index"], row["unit"]["method"]): row
            for row in cohort
        }
        for baseline in BASELINES:
            ratios = tuple(
                float(cells[(block, baseline)]["endpoint"][
                    "registered_complete_seconds"])
                / float(cells[(block, V4)]["endpoint"][
                    "registered_complete_seconds"])
                for block in range(8)
            )
            median = float(statistics.median(ratios))
            low, high = _bootstrap(ratios, 57_680_000 + row_index)
            rows.append({
                "row_index": row_index,
                "lane_id": lane_id,
                "baseline": baseline,
                "candidate": V4,
                "pair_ratios": ratios,
                "paired_ratio_median": median,
                "bootstrap_ci95": (low, high),
                "row_local_no_slower_pass": median >= 1.0,
                "ci_interpretation": (
                    "wholly_above_one" if low > 1.0
                    else "wholly_below_one" if high < 1.0
                    else "crosses_one"
                ),
            })
            row_index += 1
    passed = sum(row["row_local_no_slower_pass"] for row in rows)
    result: dict[str, object] = {
        "schema": "rtdl.goal5769.independent_formal_raw_audit.v1",
        "plan_sha256": plan_sha,
        "formal_identity_sha256": plan["formal_identity_sha256"],
        "worker_count": len(records),
        "unique_parent_pid_count": len(pids),
        "correctness_pass_count": len(records),
        "behavioral_true_optix_count": len(records),
        "payload_count": len(payloads),
        "payload_bytes": sum(row["bytes"] for row in payloads),
        "payloads": payloads,
        "independent_row_count": len(rows),
        "pass_count": passed,
        "fail_count": len(rows) - passed,
        "all_row_no_slower": passed == len(rows),
        "rows": rows,
        "imports_controller_worker_frontdoor_evaluator_or_recount": False,
        "cross_row_aggregate_or_compensation_used": False,
    }
    result["audit_sha256"] = _canonical(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = audit(args.plan, args.raw_root)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
