#!/usr/bin/env python3
"""Standard-library-only independent Goal5798 raw-evidence recount."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import statistics
from typing import Any


DIRECT_ARM = "A_DIRECT_CUDA_OPTIX"
RTDL_ARM = "D_RTDL_PUBLIC"
MEMORY_MODE = "MEMORY_SEPARATE_NON_TIMED"


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def sha(path: Path) -> str:
    block = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            block.update(chunk)
    return block.hexdigest()


def load_sealed(path: Path, seal_key: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    seal = value.get(seal_key)
    unsealed = dict(value)
    unsealed.pop(seal_key, None)
    if not isinstance(seal, str) or digest(unsealed) != seal:
        raise ValueError(f"seal mismatch: {path}")
    return value


def integer_median(values: list[int]) -> int:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("empty integer median")
    middle = len(ordered) // 2
    return ordered[middle] if len(ordered) % 2 else (
        ordered[middle - 1] + ordered[middle]) // 2


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    freeze = load_sealed(args.freeze.resolve(), "freeze_sha256")
    schedule_arms = {row["arm"] for row in (
        freeze["memory_schedule"] + freeze["performance_schedule"])}
    pyoptix_arms = sorted(arm for arm in schedule_arms if arm.startswith("B_"))
    if DIRECT_ARM not in schedule_arms or RTDL_ARM not in schedule_arms \
            or len(pyoptix_arms) != 1 or len(schedule_arms) != 3:
        raise ValueError("freeze does not contain exactly one A/B/D arm set")
    arms = (DIRECT_ARM, pyoptix_arms[0], RTDL_ARM)
    root = args.result_root.resolve()
    controller = load_sealed(root / "controller_result.json", "result_sha256")
    schedule = freeze["memory_schedule"] + freeze["performance_schedule"]
    if controller["worker_count"] != len(schedule):
        raise ValueError("controller worker count mismatch")
    planned = {row["worker_id"]: row for row in schedule}
    records: dict[str, dict[str, Any]] = {}
    receipts: dict[str, dict[str, Any]] = {}
    record_paths = sorted(root.glob("*_/controller_record.json"))
    if not record_paths:
        record_paths = sorted(root.glob("*/controller_record.json"))
    for path in record_paths:
        record = load_sealed(path, "record_sha256")
        worker_id = record["worker_id"]
        if worker_id in records or worker_id not in planned:
            raise ValueError(f"unexpected/duplicate record: {worker_id}")
        worker_dir = path.parent
        receipt_path = worker_dir / "final_receipt.json"
        if sha(receipt_path) != record["final_receipt_sha256"]:
            raise ValueError(f"final receipt file identity mismatch: {worker_id}")
        receipt = load_sealed(receipt_path, "receipt_sha256")
        payload_path = worker_dir / "worker_receipt.json"
        if sha(payload_path) != record["worker_payload_receipt_sha256"] \
                or sha(payload_path) != receipt["worker_payload_receipt_file_sha256"]:
            raise ValueError(f"worker payload identity mismatch: {worker_id}")
        row = planned[worker_id]
        if receipt.get("schema") != "rtdl.goal5798.formal_worker_receipt.v1" \
                or not set(freeze["future_worker_receipt_required_fields"]).issubset(receipt):
            raise ValueError(f"final receipt schema/fields mismatch: {worker_id}")
        for key in ("worker_id", "arm", "task", "mode", "row_sample_index"):
            if receipt.get(key) != row.get(key) or record.get(key) != row.get(key):
                raise ValueError(f"schedule mismatch {worker_id}:{key}")
        if receipt.get("correctness", {}).get("oracle_exact") is not True \
                or record.get("correctness_oracle_exact") is not True:
            raise ValueError(f"non-exact worker: {worker_id}")
        if receipt.get("correctness", {}).get("raw_output_sha256") \
                != receipt.get("raw_output_sha256"):
            raise ValueError(f"raw output identity mismatch: {worker_id}")
        if set(receipt.get("durations_ns", {})) != set(freeze["required_phase_keys"]):
            raise ValueError(f"phase denominator mismatch: {worker_id}")
        durations = receipt["durations_ns"]["complete_execute_ns"]
        if receipt["durations_ns"]["controller_process_wall_ns"] != record["process_wall_ns"]:
            raise ValueError(f"controller wall mismatch: {worker_id}")
        if row["mode"] == "PREPARED_EXECUTION":
            if len(durations) != 64 or integer_median(durations) != record["registered_primary_sample_ns"]:
                raise ValueError(f"prepared primary mismatch: {worker_id}")
        elif row["mode"] == "COLD_FRESH_PROCESS":
            if len(durations) != 1 or record["registered_primary_sample_ns"] != record["process_wall_ns"]:
                raise ValueError(f"cold primary mismatch: {worker_id}")
        else:
            if record["registered_primary_sample_ns"] is not None or record["timing_eligible"] is not False:
                raise ValueError(f"memory timing contamination: {worker_id}")
            if receipt["memory"] != record["memory"]:
                raise ValueError(f"memory receipt/record mismatch: {worker_id}")
            for metric in freeze["measurement_modes"][MEMORY_MODE]["primary_metrics"]:
                if type(receipt["memory"].get(metric)) is not int \
                        or receipt["memory"][metric] <= 0:
                    raise ValueError(f"invalid memory metric {worker_id}:{metric}")
        records[worker_id] = record
        receipts[worker_id] = receipt
    if set(records) != set(planned):
        missing = sorted(set(planned) - set(records))
        raise ValueError(f"missing worker records: {missing[:3]} ({len(missing)} total)")
    ordered_record_seals = [records[row["worker_id"]]["record_sha256"] for row in schedule]
    if ordered_record_seals != controller["record_sha256s"]:
        raise ValueError("controller record ordering mismatch")

    primary: dict[tuple[str, str, int, str], int] = {}
    for row in freeze["performance_schedule"]:
        record = records[row["worker_id"]]
        key = (row["task"], row["mode"], row["superblock"], row["arm"])
        if key in primary:
            raise ValueError(f"duplicate paired sample: {key}")
        value = record["registered_primary_sample_ns"]
        if type(value) is not int or value <= 0:
            raise ValueError(f"invalid primary sample: {row['worker_id']}")
        primary[key] = value

    comparison_rows = []
    row_order = freeze["statistics"]["row_index_order"]
    for row_index, row_id in enumerate(row_order):
        comparison = "A" if row_id.endswith("A_OVER_D") else "B"
        baseline = arms[0] if comparison == "A" else arms[1]
        body = row_id.removesuffix(f"__{comparison}_OVER_D")
        mode = "COLD_FRESH_PROCESS" if body.endswith("__COLD_FRESH_PROCESS") else "PREPARED_EXECUTION"
        task = body.removesuffix(f"__{mode}")
        ratios = [
            primary[(task, mode, block, baseline)]
            / primary[(task, mode, block, arms[2])]
            for block in range(24)
        ]
        estimate = statistics.median(ratios)
        rng = random.Random(freeze["statistics"]["bootstrap_seed_base"] + row_index)
        draws = sorted(statistics.median(rng.choices(ratios, k=len(ratios)))
                       for _ in range(freeze["statistics"]["bootstrap_draw_count"]))
        low, high = freeze["statistics"]["bootstrap_indices"]
        comparison_rows.append({
            "row_id": row_id, "row_index": row_index,
            "baseline_arm": baseline, "rtdl_arm": arms[2],
            "paired_sample_count": len(ratios),
            "paired_ratios_baseline_over_rtdl": ratios,
            "median_ratio": estimate,
            "bootstrap_ci": [draws[low], draws[high]],
            "ratio_greater_than_one_favors_rtdl": True,
            "success_threshold": None,
        })

    memory_rows = []
    metrics = (
        "host_peak_rss_bytes", "gpu_process_sampled_peak_bytes",
        "gpu_process_steady_prepared_bytes",
    )
    for task in freeze["tasks"]:
        for arm in arms:
            group = [records[row["worker_id"]]["memory"]
                     for row in freeze["memory_schedule"]
                     if row["task"] == task and row["arm"] == arm]
            if len(group) != 5 or any(value is None for value in group):
                raise ValueError(f"memory denominator mismatch: {task}/{arm}")
            memory_rows.append({
                "task": task, "arm": arm, "sample_count": 5,
                "medians": {metric: statistics.median([row[metric] for row in group])
                            for metric in metrics},
                "raw_samples": {metric: [row[metric] for row in group] for metric in metrics},
                "timing_eligible": False,
            })

    result = {
        "schema": "rtdl.goal5798.independent_recount.v1",
        "status": "PASS",
        "imports_controller_worker_or_project_statistics": False,
        "standard_library_only": True,
        "freeze_file_sha256": sha(args.freeze.resolve()),
        "controller_result_sha256": sha(root / "controller_result.json"),
        "worker_count": len(records),
        "correct_worker_count": sum(
            receipt["correctness"]["oracle_exact"] is True for receipt in receipts.values()),
        "comparison_rows": comparison_rows,
        "memory_rows": memory_rows,
        "retry_count": controller["retry_count"],
        "resume_count": controller["resume_count"],
        "replacement_count": controller["replacement_count"],
        "dropped_row_count": controller["dropped_row_count"],
    }
    result["recount_sha256"] = digest(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(json.dumps(
        result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": "PASS", "worker_count": len(records),
        "comparison_medians": {row["row_id"]: row["median_ratio"] for row in comparison_rows},
        "recount_sha256": result["recount_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
