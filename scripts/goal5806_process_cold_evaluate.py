#!/usr/bin/env python3
"""Frozen primary evaluator for Goal5806 formal process-cold rows."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import re
import statistics


ROW = re.compile(
    r"^(relation|triangle)_b([0-9]{2})_p([01])_(rtdl|pyoptix)\.json$")


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bootstrap(values: list[float], *, seed: int, draws: int,
               indices: tuple[int, int]) -> tuple[float, float]:
    generator = random.Random(seed)
    samples = sorted(
        statistics.median(generator.choices(values, k=len(values)))
        for _ in range(draws))
    return samples[indices[0]], samples[indices[1]]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    contract_path = args.contract.resolve(strict=True)
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    contract_sha = _sha(contract_path)
    rows_dir = args.matrix.resolve(strict=True) / "rows"
    expected_keys = {
        (task, block, position, arm)
        for task in contract["matrix"]["tasks"]
        for block in range(contract["matrix"]["blocks_per_task"])
        for position, arm in enumerate(
            ("rtdl", "pyoptix") if block % 2 == 0
            else ("pyoptix", "rtdl"))
    }
    rows: dict[tuple[str, int, int, str], dict[str, object]] = {}
    pids: set[int] = set()
    findings: list[str] = []
    for path in sorted(rows_dir.glob("*.json")):
        match = ROW.fullmatch(path.name)
        if not match:
            findings.append(f"unexpected_row_name:{path.name}")
            continue
        task, block_text, position_text, arm = match.groups()
        key = (task, int(block_text), int(position_text), arm)
        row = json.loads(path.read_text(encoding="utf-8"))
        child = row.get("child")
        valid = (
            key not in rows
            and row.get("schema") == "rtdl.goal5806.process_cold_formal_row.v1"
            and row.get("contract_sha256") == contract_sha
            and row.get("task") == key[0]
            and row.get("block") == key[1]
            and row.get("position") == key[2]
            and row.get("arm") == key[3]
            and row.get("status") == "PASS"
            and row.get("registered_performance_timing_count") == 1
            and row.get("returncode") == 0
            and row.get("stderr") == ""
            and row.get("boundary_marker") == "GOAL5806_BOUNDARY"
            and type(row.get("worker_pid")) is int
            and row["worker_pid"] not in pids
            and type(row.get("primary_process_cold_ns")) is int
            and row["primary_process_cold_ns"] > 0
            and isinstance(child, dict)
            and child.get("task") == task
            and child.get("arm") == arm
            and child.get("status_ok") is True
            and child.get("output_sha256")
                == contract["expected_output_sha256"][task]
        )
        if not valid:
            findings.append(f"invalid_row:{path.name}")
            continue
        rows[key] = row
        pids.add(row["worker_pid"])
    if set(rows) != expected_keys:
        findings.append("formal_row_universe_mismatch")
    statistics_spec = contract["statistics"]
    results: dict[str, object] = {}
    if not findings:
        for task_index, task in enumerate(contract["matrix"]["tasks"]):
            block_ratios: list[float] = []
            rtdl_values: list[int] = []
            pyoptix_values: list[int] = []
            for block in range(contract["matrix"]["blocks_per_task"]):
                arm_rows = {
                    arm: row for (row_task, row_block, _position, arm), row
                    in rows.items() if row_task == task and row_block == block}
                rtdl_ns = int(arm_rows["rtdl"]["primary_process_cold_ns"])
                pyoptix_ns = int(arm_rows["pyoptix"]["primary_process_cold_ns"])
                rtdl_values.append(rtdl_ns)
                pyoptix_values.append(pyoptix_ns)
                block_ratios.append(rtdl_ns / pyoptix_ns)
            median_ratio = statistics.median(block_ratios)
            seed = statistics_spec[
                "relation_seed" if task == "relation" else "triangle_seed"]
            ci_low, ci_high = _bootstrap(
                block_ratios, seed=seed,
                draws=statistics_spec["bootstrap_draw_count"],
                indices=tuple(statistics_spec["ci_indices"]))
            threshold = 1.05
            results[task] = {
                "block_count": len(block_ratios),
                "block_ratios_rtdl_over_pyoptix": block_ratios,
                "median_block_ratio_rtdl_over_pyoptix": median_ratio,
                "bootstrap_ci_low": ci_low,
                "bootstrap_ci_high": ci_high,
                "rtdl_median_ns": int(statistics.median(rtdl_values)),
                "pyoptix_median_ns": int(statistics.median(pyoptix_values)),
                "ratio_of_arm_medians": (
                    statistics.median(rtdl_values)
                    / statistics.median(pyoptix_values)),
                "pass": median_ratio <= threshold and ci_high <= threshold,
            }
    overall_pass = not findings and all(
        bool(result["pass"]) for result in results.values())
    evaluation = {
        "schema": "rtdl.goal5806.process_cold_formal_evaluation.v1",
        "contract_sha256": contract_sha,
        "controller_sha256": _sha(args.matrix.resolve() / "controller.json"),
        "registered_performance_timing_count": len(rows),
        "worker_count": len(rows),
        "unique_worker_pid_count": len(pids),
        "finding_count": len(findings),
        "findings": findings,
        "results": results,
        "overall_pass": overall_pass,
        "claim_boundary": contract["claim_boundary"],
        "status": "PASS" if overall_pass else "FAIL",
    }
    with args.output.resolve().open("xb") as stream:
        stream.write(_canonical(evaluation) + b"\n")
    print(_canonical(evaluation).decode("ascii"))
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
