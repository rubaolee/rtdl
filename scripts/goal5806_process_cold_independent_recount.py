#!/usr/bin/env python3
"""Independent byte-level recount of Goal5806 formal process-cold rows."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random


def _bytes_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _median(values: list[float | int]) -> float:
    ordered = sorted(values)
    count = len(ordered)
    if count == 0:
        raise ValueError("median of empty values")
    midpoint = count // 2
    if count % 2:
        return float(ordered[midpoint])
    return (float(ordered[midpoint - 1]) + float(ordered[midpoint])) / 2.0


def _ci(values: list[float], seed: int, draws: int,
        low_index: int, high_index: int) -> tuple[float, float]:
    generator = random.Random(seed)
    distribution: list[float] = []
    for _ in range(draws):
        resample = generator.choices(values, k=len(values))
        distribution.append(_median(resample))
    distribution.sort()
    return distribution[low_index], distribution[high_index]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    contract_path = args.contract.resolve(strict=True)
    matrix = args.matrix.resolve(strict=True)
    evaluation_path = args.evaluation.resolve(strict=True)
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    controller = json.loads(
        (matrix / "controller.json").read_text(encoding="utf-8"))
    published = json.loads(evaluation_path.read_text(encoding="utf-8"))
    findings: list[str] = []
    contract_sha = _bytes_sha(contract_path)
    if controller.get("contract_sha256") != contract_sha:
        findings.append("controller_contract_identity_mismatch")
    rows_by_task_block: dict[tuple[str, int], dict[str, int]] = {}
    pids: set[int] = set()
    output_digests: dict[str, set[str]] = {
        task: set() for task in contract["matrix"]["tasks"]}
    observed_hashes: dict[str, str] = {}
    phase_values: dict[tuple[str, str], dict[str, list[int]]] = {}
    for path in sorted((matrix / "rows").glob("*.json")):
        observed_hashes[path.name] = _bytes_sha(path)
        row = json.loads(path.read_text(encoding="utf-8"))
        task = row.get("task")
        arm = row.get("arm")
        block = row.get("block")
        child = row.get("child")
        if task not in contract["matrix"]["tasks"] \
                or arm not in contract["matrix"]["arms"] \
                or type(block) is not int \
                or not isinstance(child, dict):
            findings.append(f"row_shape:{path.name}")
            continue
        key = (task, block)
        if arm in rows_by_task_block.setdefault(key, {}):
            findings.append(f"duplicate_block_arm:{path.name}")
        rows_by_task_block[key][arm] = int(row["primary_process_cold_ns"])
        pid = row.get("worker_pid")
        if type(pid) is not int or pid in pids:
            findings.append(f"pid_invalid_or_reused:{path.name}")
        else:
            pids.add(pid)
        valid = (
            row.get("schema") == "rtdl.goal5806.process_cold_formal_row.v1"
            and row.get("contract_sha256") == contract_sha
            and row.get("status") == "PASS"
            and row.get("registered_performance_timing_count") == 1
            and row.get("boundary_marker") == "GOAL5806_BOUNDARY"
            and row.get("returncode") == 0
            and row.get("stderr") == ""
            and child.get("schema") == "rtdl.goal5806.process_cold_child.v2"
            and child.get("task") == task
            and child.get("arm") == arm
            and child.get("status_ok") is True
            and child.get("output_sha256")
                == contract["expected_output_sha256"][task]
            and child.get("output_count") == (4096 if task == "relation" else 1)
            and int(row["primary_process_cold_ns"])
                >= int(child["child_measured_total_ns"])
        )
        if not valid:
            findings.append(f"row_contract:{path.name}")
        output_digests[task].add(str(child.get("output_sha256")))
        phases = phase_values.setdefault((task, arm), {})
        for name in (
                "preload_ns", "load_ns", "prepare_ns", "execute_ns",
                "close_ns", "child_measured_total_ns"):
            phases.setdefault(name, []).append(int(child[name]))
        phases.setdefault("parent_minus_child_ns", []).append(
            int(row["primary_process_cold_ns"])
            - int(child["child_measured_total_ns"]))
    if observed_hashes != controller.get("row_sha256"):
        findings.append("controller_row_hash_manifest_mismatch")
    expected_block_keys = {
        (task, block)
        for task in contract["matrix"]["tasks"]
        for block in range(contract["matrix"]["blocks_per_task"])}
    if set(rows_by_task_block) != expected_block_keys \
            or any(set(arms) != set(contract["matrix"]["arms"])
                   for arms in rows_by_task_block.values()):
        findings.append("block_arm_universe_mismatch")
    results: dict[str, object] = {}
    spec = contract["statistics"]
    for task in contract["matrix"]["tasks"]:
        ratios = [
            rows_by_task_block[(task, block)]["rtdl"]
            / rows_by_task_block[(task, block)]["pyoptix"]
            for block in range(contract["matrix"]["blocks_per_task"])]
        median_ratio = _median(ratios)
        seed = spec["relation_seed" if task == "relation" else "triangle_seed"]
        low, high = _ci(
            ratios, seed, spec["bootstrap_draw_count"],
            spec["ci_indices"][0], spec["ci_indices"][1])
        rtdl_values = [
            rows_by_task_block[(task, block)]["rtdl"]
            for block in range(contract["matrix"]["blocks_per_task"])]
        pyoptix_values = [
            rows_by_task_block[(task, block)]["pyoptix"]
            for block in range(contract["matrix"]["blocks_per_task"])]
        results[task] = {
            "median_block_ratio_rtdl_over_pyoptix": median_ratio,
            "bootstrap_ci_low": low,
            "bootstrap_ci_high": high,
            "rtdl_median_ns": int(_median(rtdl_values)),
            "pyoptix_median_ns": int(_median(pyoptix_values)),
            "ratio_of_arm_medians": _median(rtdl_values) / _median(pyoptix_values),
            "pass": median_ratio <= 1.05 and high <= 1.05,
        }
        primary = published["results"][task]
        for name, value in results[task].items():
            if primary.get(name) != value:
                findings.append(f"primary_numeric_mismatch:{task}:{name}")
    compact_phases = {
        f"{task}:{arm}": {name: int(_median(values)) for name, values in phases.items()}
        for (task, arm), phases in sorted(phase_values.items())}
    recount = {
        "schema": "rtdl.goal5806.process_cold_independent_recount.v1",
        "contract_sha256": contract_sha,
        "controller_sha256": _bytes_sha(matrix / "controller.json"),
        "evaluation_sha256": _bytes_sha(evaluation_path),
        "row_count": len(observed_hashes),
        "unique_worker_pid_count": len(pids),
        "registered_performance_timing_count": len(observed_hashes),
        "output_digests": {
            task: sorted(values) for task, values in output_digests.items()},
        "results": results,
        "phase_medians": compact_phases,
        "finding_count": len(findings),
        "findings": findings,
        "status": "PASS" if not findings else "FAIL",
    }
    with args.output.resolve().open("xb") as stream:
        stream.write(json.dumps(
            recount, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n")
    print(json.dumps(recount, sort_keys=True, separators=(",", ":")))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
