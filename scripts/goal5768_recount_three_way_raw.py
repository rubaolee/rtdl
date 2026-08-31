#!/usr/bin/env python3
"""Independent raw recount; imports no controller, evaluator, or frontdoor."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import statistics


V2_NAME = "v2_direct_true_optix_backport"
V3_NAME = "v3_compiler_true_optix"
V4_NAME = "v4_restricted_callback_true_optix"


def canonical_hash(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def percentile_pair(samples, seed):
    generator = random.Random(seed)
    estimates = []
    sample_count = len(samples)
    for _ in range(10_000):
        resample = generator.choices(samples, k=sample_count)
        estimates.append(statistics.median(resample))
    estimates.sort()
    return estimates[249], estimates[9749]


def recount(plan_path: Path, raw_root: Path, primary_path: Path | None = None):
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan_body = dict(plan)
    claimed_plan_hash = plan_body.pop("plan_sha256", None)
    if claimed_plan_hash != canonical_hash(plan_body):
        raise RuntimeError("independent recount rejected plan digest")
    units = {str(row["unit_id"]): row for row in plan["units"]}
    raw_files = sorted(raw_root.glob("*/RESULT.json"))
    if len(raw_files) != 312:
        raise RuntimeError("independent recount requires exactly 312 raw files")
    records = {}
    pids = set()
    payload_manifest = []
    for path in raw_files:
        payload_manifest.append({
            "path": str(path.relative_to(raw_root)).replace("\\", "/"),
            "sha256": file_hash(path),
            "bytes": path.stat().st_size,
        })
        record = json.loads(path.read_text(encoding="utf-8"))
        unit = record.get("unit")
        if not isinstance(unit, dict):
            raise RuntimeError("raw unit is not a mapping")
        unit_id = str(unit.get("unit_id"))
        if unit_id not in units or unit != units[unit_id] or unit_id in records:
            raise RuntimeError("raw unit is unknown, drifted, or duplicated")
        if record.get("plan_sha256") != claimed_plan_hash \
                or record.get("formal_identity_sha256") != plan["formal_identity_sha256"]:
            raise RuntimeError("raw formal identity drift")
        pid = record.get("parent_pid")
        if type(pid) is not int or pid <= 0 or pid in pids:
            raise RuntimeError("raw process freshness failed")
        pids.add(pid)
        endpoint = record.get("endpoint")
        if not isinstance(endpoint, dict) or endpoint.get("matched") is not True:
            raise RuntimeError("raw correctness failed")
        if endpoint.get("lane_id") != unit["lane_id"] \
                or endpoint.get("method") != unit["method"]:
            raise RuntimeError("raw endpoint lane/method label drift")
        if endpoint.get("stock_v2_or_v3_claimed") is not False \
                or endpoint.get("default_selected_between_application_algorithms") is not False:
            raise RuntimeError("raw endpoint provenance/selection drift")
        elapsed = endpoint.get("registered_complete_seconds")
        if type(elapsed) not in (int, float) or not math.isfinite(elapsed) \
                or elapsed <= 0:
            raise RuntimeError("raw registered timer invalid")
        if endpoint.get("comparator_inside_registered_timer") is not False:
            raise RuntimeError("raw comparator timing boundary drift")
        if endpoint.get("native_library_sha256") != plan["native_library_sha256"]:
            raise RuntimeError("raw native identity drift")
        receipt = endpoint.get("traversal_receipt")
        if not isinstance(receipt, dict):
            raise RuntimeError("raw traversal receipt absent")
        receipt_body = dict(receipt)
        receipt_hash = receipt_body.pop("receipt_sha256", None)
        if receipt_hash != canonical_hash(receipt_body):
            raise RuntimeError("raw traversal receipt hash mismatch")
        snapshot = receipt.get("native_snapshot")
        if receipt.get("physical_executor_classification") \
                != "optix_traversal_observed" or not isinstance(snapshot, dict):
            raise RuntimeError("raw behavioral OptiX classification failed")
        launches = snapshot.get("successful_launch_count")
        if type(launches) is not int or launches <= 0 \
                or snapshot.get("complete_context_launch_count") != launches:
            raise RuntimeError("raw launch binding incomplete")
        if any(snapshot.get(name) != 0 for name in (
            "failed_launch_count", "incomplete_context_launch_count",
            "pending_context_at_finish", "session_error",
        )):
            raise RuntimeError("raw traversal session failed closed")
        if any(snapshot.get(name) in (None, 0) for name in (
            "first_traversable", "last_traversable",
            "first_program_bundle_id", "last_program_bundle_id",
        )):
            raise RuntimeError("raw traversal edge binding absent")
        records[unit_id] = record
    if set(records) != set(units):
        raise RuntimeError("raw unit set is incomplete")

    comparison_rows = []
    ordinal = 0
    for lane_id in plan["lane_ids"]:
        cohort = [item for item in records.values()
                  if item["unit"]["lane_id"] == lane_id]
        if len(cohort) != 24:
            raise RuntimeError("lane does not contain 24 workers")
        input_hashes = {item["endpoint"]["input_sha256"] for item in cohort}
        output_hashes = {item["endpoint"]["output_sha256"] for item in cohort}
        oracle_hashes = {item["endpoint"]["expected_sha256"] for item in cohort}
        if len(input_hashes) != 1 or len(output_hashes) != 1 \
                or output_hashes != oracle_hashes:
            raise RuntimeError("lane input/output identity mismatch")
        contract = plan["lane_contracts"][lane_id]
        if input_hashes != {contract["input_sha256"]} \
                or output_hashes != {contract["output_sha256"]} \
                or oracle_hashes != {contract["expected_sha256"]}:
            raise RuntimeError("lane differs from prepared input/output contract")
        cell = {
            (int(item["unit"]["block_index"]), item["unit"]["method"]): item
            for item in cohort
        }
        for predecessor in (V2_NAME, V3_NAME):
            values = tuple(
                float(cell[(block, predecessor)]["endpoint"][
                    "registered_complete_seconds"])
                / float(cell[(block, V4_NAME)]["endpoint"][
                    "registered_complete_seconds"])
                for block in range(8)
            )
            middle = float(statistics.median(values))
            low, high = percentile_pair(values, 57_680_000 + ordinal)
            comparison_rows.append({
                "row_index": ordinal,
                "lane_id": lane_id,
                "baseline": predecessor,
                "candidate": V4_NAME,
                "pair_ratios": values,
                "pair_count": 8,
                "paired_ratio_median": middle,
                "bootstrap_ci95": (low, high),
                "row_local_no_slower_pass": middle >= 1.0,
                "independent_comparison_row": True,
            })
            ordinal += 1
    passed = sum(row["row_local_no_slower_pass"] for row in comparison_rows)
    result = {
        "schema": "rtdl.goal5768.independent_three_way_raw_recount.v1",
        "plan_sha256": claimed_plan_hash,
        "formal_identity_sha256": plan["formal_identity_sha256"],
        "worker_count": len(records),
        "unique_parent_pid_count": len(pids),
        "payload_manifest": payload_manifest,
        "payload_count": len(payload_manifest),
        "payload_bytes": sum(row["bytes"] for row in payload_manifest),
        "independent_row_count": len(comparison_rows),
        "pass_count": passed,
        "fail_count": len(comparison_rows) - passed,
        "all_row_no_slower": passed == len(comparison_rows),
        "rows": comparison_rows,
        "imports_controller_evaluator_or_frontdoors": False,
        "cross_row_aggregate_or_compensation_used": False,
    }
    if primary_path is not None:
        primary = json.loads(primary_path.read_text(encoding="utf-8"))
        primary_core = tuple((
            row["lane_id"], row["baseline"], tuple(row["pair_ratios"]),
            row["paired_ratio_median"], tuple(row["bootstrap_ci95"]),
            row["row_local_no_slower_pass"],
        ) for row in primary["rows"])
        recount_core = tuple((
            row["lane_id"], row["baseline"], tuple(row["pair_ratios"]),
            row["paired_ratio_median"], tuple(row["bootstrap_ci95"]),
            row["row_local_no_slower_pass"],
        ) for row in comparison_rows)
        result["primary_core_exact_match"] = primary_core == recount_core
        if not result["primary_core_exact_match"]:
            raise RuntimeError("independent recount differs from primary evaluation")
    result["recount_sha256"] = canonical_hash(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--primary", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = recount(args.plan, args.raw_root, args.primary)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")


if __name__ == "__main__":
    main()
