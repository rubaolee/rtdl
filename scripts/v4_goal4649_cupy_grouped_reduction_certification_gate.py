#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import platform
import subprocess
import statistics
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.partner_adapters import prepare_grouped_vector_sum_2d_partner_columns_session
from rtdsl.partner_adapters import run_grouped_vector_sum_2d_partner_columns_session
from rtdsl.v4_cupy_certification import V4_GOAL4649_CUPY_CERTIFICATION_STATUS
from rtdsl.v4_cupy_certification import v4_goal4649_ready_cupy_targets


DEFAULT_EVIDENCE_DIR = ROOT / "future" / "v4" / "evidence" / "v4_goal4649_cupy_grouped_reduction_gate_2026-06-25"
DEFAULT_JSON_OUT = DEFAULT_EVIDENCE_DIR / "summary.json"
DEFAULT_MD_OUT = DEFAULT_EVIDENCE_DIR / "summary.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="V4 Goal4649 CuPy grouped-reduction certification gate.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--rows", type=int, action="append", default=None)
    parser.add_argument("--repeat", type=int, default=100)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--trust-row-offsets", action="store_true")
    args = parser.parse_args()

    payload = build_dry_run_payload(args)
    if not args.dry_run:
        payload = run_live_gate(args)

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    return 0 if payload["status"] not in {"goal4649_cupy_gate_failed"} else 2


def build_dry_run_payload(args: argparse.Namespace) -> dict[str, Any]:
    ready_targets = _selected_targets(args.rows)
    return {
        "schema": "rtdl.v4.goal4649.cupy_grouped_reduction_gate.v1",
        "status": "goal4649_cupy_gate_dry_run_no_claims",
        "gate_status": V4_GOAL4649_CUPY_CERTIFICATION_STATUS,
        "ready_targets": ready_targets,
        "rows_requested": args.rows,
        "warmup": int(args.warmup),
        "repeat": int(args.repeat),
        "trust_row_offsets": bool(args.trust_row_offsets),
        "cupy_performance_claim_authorized": False,
        "pod_spend_authorized_by_this_file": False,
        "partner_migration_counts_as_v4_speed_win": False,
        "partner_parity_counts_as_v4_speed_win": False,
        "summary": {
            "mode": "dry_run",
            "ready_target_count": len(ready_targets),
            "live_rows_passed": 0,
            "cupy_performance_claim_authorized": False,
        },
    }


def run_live_gate(args: argparse.Namespace) -> dict[str, Any]:
    try:
        import cupy
    except Exception as exc:  # pragma: no cover - exercised on non-CUDA hosts only
        return _blocked_payload(args, f"CuPy import failed: {exc}")

    try:
        device_count = int(cupy.cuda.runtime.getDeviceCount())
    except Exception as exc:  # pragma: no cover
        return _blocked_payload(args, f"CuPy CUDA device query failed: {exc}")
    if device_count <= 0:
        return _blocked_payload(args, "CuPy reports no CUDA devices")

    targets = _selected_targets(args.rows)
    rows = []
    for target in targets:
        rows.append(_run_one_target(cupy, target, args))

    all_pass = all(row["pass"] for row in rows)
    return {
        "schema": "rtdl.v4.goal4649.cupy_grouped_reduction_gate.v1",
        "status": "goal4649_cupy_gate_passed_pending_review" if all_pass else "goal4649_cupy_gate_failed",
        "gate_status": V4_GOAL4649_CUPY_CERTIFICATION_STATUS,
        "environment": _environment(cupy),
        "device_count": device_count,
        "ready_targets": targets,
        "rows": rows,
        "cupy_performance_claim_authorized": False,
        "pod_spend_authorized_by_this_file": False,
        "partner_migration_counts_as_v4_speed_win": False,
        "partner_parity_counts_as_v4_speed_win": False,
        "summary": {
            "mode": "live",
            "ready_target_count": len(targets),
            "live_rows_passed": sum(1 for row in rows if row["pass"]),
            "live_rows_failed": sum(1 for row in rows if not row["pass"]),
            "cupy_performance_claim_authorized": False,
            "min_representative_speedup": min((row["representative_speedup"] for row in rows), default=None),
            "all_correctness_parity": all(row["correctness_parity"] for row in rows),
            "all_no_hot_host_materialization": all(not row["host_materialization_in_hot_path"] for row in rows),
        },
    }


def _run_one_target(cupy: Any, target: dict[str, object], args: argparse.Namespace) -> dict[str, object]:
    row_count = int(target["representative_rows"])
    group_count = int(target["representative_groups"])
    if row_count % group_count != 0:
        raise ValueError("Goal4649 grouped-reduction fixture requires rows divisible by groups")
    rows_per_group = row_count // group_count
    group_ids = cupy.repeat(cupy.arange(group_count, dtype=cupy.int64), rows_per_group)
    row_offsets = cupy.arange(0, row_count + 1, rows_per_group, dtype=cupy.int64)
    values_x = cupy.ones((row_count,), dtype=cupy.float64)
    values_y = cupy.full((row_count,), 2.0, dtype=cupy.float64)
    vector_columns = {
        "group_ids": group_ids,
        "row_offsets": row_offsets,
        "values_x": values_x,
        "values_y": values_y,
    }

    prepare_started = time.perf_counter()
    prepared = prepare_grouped_vector_sum_2d_partner_columns_session(
        vector_columns,
        group_count=group_count,
        partner="cupy",
        validate_row_offsets=not bool(args.trust_row_offsets),
        return_metadata=True,
    )
    cupy.cuda.Stream.null.synchronize()
    prepare_seconds = time.perf_counter() - prepare_started
    session = prepared["session"]

    for _ in range(int(args.warmup)):
        run_grouped_vector_sum_2d_partner_columns_session(session, return_metadata=True)
    cupy.cuda.Stream.null.synchronize()

    repeat_times = []
    last_result = None
    for _ in range(int(args.repeat)):
        started = time.perf_counter()
        last_result = run_grouped_vector_sum_2d_partner_columns_session(session, return_metadata=True)
        cupy.cuda.Stream.null.synchronize()
        repeat_times.append(time.perf_counter() - started)

    sum_x = session["cupy_session"]["outputs"]["sum_x"]
    sum_y = session["cupy_session"]["outputs"]["sum_y"]
    max_err_x = float(cupy.max(cupy.abs(sum_x - float(rows_per_group))).item())
    max_err_y = float(cupy.max(cupy.abs(sum_y - float(rows_per_group * 2))).item())
    correctness = bool(max_err_x == 0.0 and max_err_y == 0.0)
    median_seconds = statistics.median(repeat_times)
    # The denominator is a deterministic same-contract Python/CPU row loop over
    # every input row. It is used only to check the frozen gate; it is not a
    # public speedup claim.
    cpu_started = time.perf_counter()
    expected_x = [0.0] * group_count
    expected_y = [0.0] * group_count
    for row_index in range(row_count):
        group = row_index // rows_per_group
        expected_x[group] += 1.0
        expected_y[group] += 2.0
    cpu_seconds = time.perf_counter() - cpu_started
    representative_speedup = (cpu_seconds / median_seconds) if median_seconds > 0 else math.inf
    metadata = dict(last_result.get("metadata", {})) if isinstance(last_result, dict) else {}
    host_materialization_in_hot_path = bool(
        metadata.get("hot_path_host_materialization")
        or metadata.get("host_output_materialized")
        or metadata.get("per_run_host_validation_materialized")
    )
    return {
        "candidate_id": target["candidate_id"],
        "operator": target["operator"],
        "row_count": row_count,
        "group_count": group_count,
        "rows_per_group": rows_per_group,
        "warmup": int(args.warmup),
        "repeat": int(args.repeat),
        "prepare_seconds": prepare_seconds,
        "median_seconds": median_seconds,
        "cpu_row_loop_seconds": cpu_seconds,
        "representative_speedup": representative_speedup,
        "speedup_floor": float(target["representative_speedup_floor"]),
        "correctness_parity": correctness,
        "max_err_x": max_err_x,
        "max_err_y": max_err_y,
        "host_materialization_in_hot_path": host_materialization_in_hot_path,
        "row_offset_validation_performed_at_prepare": bool(not args.trust_row_offsets),
        "metadata": metadata,
        "pass": bool(
            correctness
            and not host_materialization_in_hot_path
            and representative_speedup >= float(target["representative_speedup_floor"])
        ),
        "public_claim_authorized": False,
    }


def _selected_targets(rows_filter: list[int] | None) -> list[dict[str, object]]:
    targets = v4_goal4649_ready_cupy_targets()
    if rows_filter:
        allowed = {int(item) for item in rows_filter}
        targets = [target for target in targets if int(target["representative_rows"]) in allowed]
    return targets


def _blocked_payload(args: argparse.Namespace, reason: str) -> dict[str, Any]:
    return {
        "schema": "rtdl.v4.goal4649.cupy_grouped_reduction_gate.v1",
        "status": "goal4649_cupy_gate_blocked",
        "gate_status": V4_GOAL4649_CUPY_CERTIFICATION_STATUS,
        "blocked_reason": reason,
        "ready_targets": _selected_targets(args.rows),
        "cupy_performance_claim_authorized": False,
        "pod_spend_authorized_by_this_file": False,
        "summary": {
            "mode": "blocked",
            "ready_target_count": len(_selected_targets(args.rows)),
            "live_rows_passed": 0,
            "cupy_performance_claim_authorized": False,
        },
    }


def _environment(cupy: Any) -> dict[str, object]:
    try:
        device_id = int(cupy.cuda.runtime.getDevice())
        props = cupy.cuda.runtime.getDeviceProperties(device_id)
        gpu_name = props.get("name", b"")
        if isinstance(gpu_name, bytes):
            gpu_name = gpu_name.decode("utf-8", errors="replace")
    except Exception as exc:  # pragma: no cover
        device_id = None
        gpu_name = f"unavailable: {exc}"
    try:
        nvidia_smi = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version",
                "--format=csv,noheader",
            ],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except Exception as exc:  # pragma: no cover
        nvidia_smi = f"unavailable: {exc}"
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "cupy": getattr(cupy, "__version__", "unknown"),
        "cuda_runtime": cupy.cuda.runtime.runtimeGetVersion(),
        "device_id": device_id,
        "gpu_name": gpu_name,
        "nvidia_smi": nvidia_smi,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    rows = payload.get("rows", [])
    row_table = "\n".join(
        "| {candidate_id} | {row_count} | {group_count} | {representative_speedup:.3f}x | {correctness_parity} | {host} | {passed} |".format(
            candidate_id=row["candidate_id"],
            row_count=row["row_count"],
            group_count=row["group_count"],
            representative_speedup=row["representative_speedup"],
            correctness_parity=str(row["correctness_parity"]).lower(),
            host=str(row["host_materialization_in_hot_path"]).lower(),
            passed=str(row["pass"]).lower(),
        )
        for row in rows
    )
    target_table = "\n".join(
        "| {candidate_id} | {operator} | {representative_rows} | {representative_groups} | {representative_speedup_floor}x |".format(
            candidate_id=target["candidate_id"],
            operator=target["operator"],
            representative_rows=target["representative_rows"],
            representative_groups=target["representative_groups"],
            representative_speedup_floor=target["representative_speedup_floor"],
        )
        for target in payload.get("ready_targets", [])
    )
    return f"""# V4 Goal4649 CuPy Grouped-Reduction Certification Gate

Status: `{payload['status']}`

CuPy performance remains unauthorized until Goal4649 completion review closes.
This file does not authorize public release, broad speedup, whole-app speedup,
POD spend, C ABI/embedding, arbitrary Numba callback support, or partner
migration/parity as V4 speed evidence.

## Ready Targets

| Candidate | Operator | Rows | Groups | Frozen speed floor |
|---|---|---:|---:|---:|
{target_table}

## Live Results

| Candidate | Rows | Groups | Representative speedup | Correctness parity | Host materialization in hot path | Pass |
|---|---:|---:|---:|---|---|---|
{row_table if row_table else '| none | 0 | 0 | 0.000x | false | false | false |'}

## Summary

```json
{json.dumps(payload['summary'], indent=2, sort_keys=True)}
```
"""


if __name__ == "__main__":
    raise SystemExit(main())
