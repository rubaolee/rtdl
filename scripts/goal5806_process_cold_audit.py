#!/usr/bin/env python3
"""Independent raw-row audit for the Goal5806 process-cold diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import statistics


ROW = re.compile(
    r"^(relation|triangle)_b([0-9]+)_p([01])_(rtdl|pyoptix)\.json$")


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.matrix.resolve(strict=True)
    summary_path = root / "summary.json"
    published = json.loads(summary_path.read_text(encoding="utf-8"))
    blocks = int(published["blocks"])
    rows: list[dict[str, object]] = []
    findings: list[str] = []
    seen: set[tuple[str, int, int, str]] = set()
    row_hashes: dict[str, str] = {}
    for path in sorted(root.glob("*.json")):
        match = ROW.fullmatch(path.name)
        if not match:
            if path.name != "summary.json" \
                    and not path.name.startswith("independent_audit"):
                findings.append(f"unexpected_json:{path.name}")
            continue
        task, block_text, position_text, arm = match.groups()
        block = int(block_text)
        position = int(position_text)
        key = (task, block, position, arm)
        if key in seen:
            findings.append(f"duplicate_key:{key}")
        seen.add(key)
        row = json.loads(path.read_text(encoding="utf-8"))
        row_hashes[path.name] = _sha(path)
        expected_arm = (
            ("rtdl", "pyoptix") if block % 2 == 0
            else ("pyoptix", "rtdl"))[position]
        checks = {
            "top_schema": row.get("schema")
                == "rtdl.goal5806.process_cold_parent_row.v2",
            "top_task": row.get("task") == task,
            "top_block": row.get("block") == block,
            "top_position": row.get("position") == position,
            "top_arm": row.get("arm") == arm == expected_arm,
            "marker": row.get("boundary_marker") == "GOAL5806_BOUNDARY",
            "returncode": row.get("returncode") == 0,
            "stderr": row.get("stderr") == "",
            "top_unregistered": row.get("registered_performance_timing_count") == 0,
            "top_unclaimed": row.get("scientific_claim_authorized") is False,
        }
        child = row.get("child")
        if not isinstance(child, dict):
            findings.append(f"missing_child:{path.name}")
            continue
        checks.update({
            "child_schema": child.get("schema")
                == "rtdl.goal5806.process_cold_child.v2",
            "child_arm": child.get("arm") == arm,
            "child_task": child.get("task") == task,
            "child_unregistered": child.get("registered_performance_timing_count") == 0,
            "child_unclaimed": child.get("scientific_claim_authorized") is False,
            "status_ok": child.get("status_ok") is True,
            "output_count": child.get("output_count")
                == (4096 if task == "relation" else 1),
            "output_digest_shape": bool(re.fullmatch(
                r"[0-9a-f]{64}", str(child.get("output_sha256", "")))),
            "first_input": child.get("lifecycle", {}).get(
                "prepared_input_reused") is False,
            "input_generation": child.get("lifecycle", {}).get(
                "dynamic_input_generation") == 1,
            "no_blocking_upload": child.get("lifecycle", {}).get(
                "dynamic_blocking_upload_call_count") == 0,
        })
        phase_names = (
            "preload_ns", "load_ns", "prepare_ns", "execute_ns", "close_ns",
            "child_measured_total_ns")
        for name in phase_names:
            value = child.get(name)
            checks[f"positive_{name}"] = type(value) is int and value > 0
        checks["parent_contains_child"] = (
            type(row.get("parent_boundary_ns")) is int
            and row["parent_boundary_ns"] >= child.get("child_measured_total_ns", 10**30))
        for name, passed in checks.items():
            if not passed:
                findings.append(f"{name}:{path.name}")
        row["_path"] = path.name
        rows.append(row)

    expected_keys = {
        (task, block, position, arm)
        for task in ("relation", "triangle")
        for block in range(blocks)
        for position, arm in enumerate(
            ("rtdl", "pyoptix") if block % 2 == 0
            else ("pyoptix", "rtdl"))
    }
    if seen != expected_keys:
        findings.append("row_key_universe_mismatch")
    output_digests: dict[str, list[str]] = {}
    recomputed_groups: dict[str, object] = {}
    phase_medians: dict[str, object] = {}
    for task in ("relation", "triangle"):
        output_digests[task] = sorted({
            str(row["child"]["output_sha256"])
            for row in rows if row["task"] == task})
        if len(output_digests[task]) != 1:
            findings.append(f"cross_arm_output_digest_mismatch:{task}")
        recomputed_groups[task] = {}
        phase_medians[task] = {}
        for arm in ("rtdl", "pyoptix"):
            selected = [
                row for row in rows
                if row["task"] == task and row["arm"] == arm]
            boundaries = [int(row["parent_boundary_ns"]) for row in selected]
            recomputed_groups[task][arm] = {
                "count": len(selected),
                "parent_boundary_median_ns": int(statistics.median(boundaries)),
                "parent_boundary_min_ns": min(boundaries),
                "parent_boundary_max_ns": max(boundaries),
            }
            phase_medians[task][arm] = {
                name: int(statistics.median(
                    int(row["child"][name]) for row in selected))
                for name in (
                    "preload_ns", "load_ns", "prepare_ns", "execute_ns",
                    "close_ns", "child_measured_total_ns")
            }
            phase_medians[task][arm]["parent_minus_child_median_ns"] = int(
                statistics.median(
                    int(row["parent_boundary_ns"])
                    - int(row["child"]["child_measured_total_ns"])
                    for row in selected))
        recomputed_groups[task]["rtdl_over_pyoptix"] = (
            recomputed_groups[task]["rtdl"]["parent_boundary_median_ns"]
            / recomputed_groups[task]["pyoptix"]["parent_boundary_median_ns"])
    if recomputed_groups != published.get("groups"):
        findings.append("published_summary_mismatch")
    audit = {
        "schema": "rtdl.goal5806.process_cold_independent_audit.v1",
        "matrix_summary_sha256": _sha(summary_path),
        "registered_performance_timing_count": 0,
        "scientific_claim_authorized": False,
        "row_count": len(rows),
        "unique_key_count": len(seen),
        "row_hashes": row_hashes,
        "output_digests": output_digests,
        "recomputed_groups": recomputed_groups,
        "phase_medians": phase_medians,
        "finding_count": len(findings),
        "findings": findings,
        "status": "PASS" if not findings else "FAIL",
    }
    args.output.resolve().write_bytes(_canonical(audit) + b"\n")
    print(_canonical(audit).decode("ascii"))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
