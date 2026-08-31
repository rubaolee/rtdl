#!/usr/bin/env python3
"""Run a small paired Home/Pascal phase-diagnostic matrix.

The matrix is deliberately non-formal and has no threshold.  It alternates
arm and application order, gives every child a fresh process and cache root,
and keeps every structurally valid result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys
from typing import Any, Mapping


SCHEMA = "rtdl.goal5810.home_two_app_diagnostic_matrix.v1"
STATUS = "COMPLETE__HOME_PASCAL_NONFORMAL_PAIRED_DIAGNOSTIC_MATRIX"
PHASES = (
    "input_admission", "runtime_preload", "workload_materialization",
    "load_relation", "load_triangle", "first_session_admission",
    "first_app_prepare", "first_app_first_exact_execute",
    "second_app_prepare", "second_app_first_exact_execute", "close",
)
ARMS = ("rtdl", "pyoptix")
FIRST_APPS = ("relation", "triangle")


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def _file_row(path: Path) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    return {
        "path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": _sha(resolved),
    }


def _read_result(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Goal5810 worker result is not an object")
    unsigned = dict(value)
    seal = unsigned.pop("diagnostic_sha256", None)
    if seal != _digest(unsigned):
        raise RuntimeError("Goal5810 worker seal differs")
    if value.get("status") \
            != "COMPLETE__HOME_PASCAL_NONFORMAL_TWO_APP_PHASE_DIAGNOSTIC" \
            or value.get("formal_worker_count") != 0 \
            or value.get("registered_performance_timing_count") != 0 \
            or value.get("cuda", {}).get("gpu_name") \
            != "NVIDIA GeForce GTX 1070" \
            or value.get("cuda", {}).get("compute_capability") != [6, 1]:
        raise RuntimeError("Goal5810 worker scope or Home identity differs")
    for task in FIRST_APPS:
        app = value.get("applications", {}).get(task)
        if not isinstance(app, Mapping) \
                or app.get("exact_oracle_passed") is not True \
                or app.get("device_status_ok") is not True:
            raise RuntimeError(f"Goal5810 {task} exact/status evidence differs")
    phase_rows = value.get("phase_times_absolute", {}).get("phases")
    if not isinstance(phase_rows, Mapping) or tuple(
            value["phase_times_absolute"].get("phase_order", ())) != PHASES:
        raise RuntimeError("Goal5810 phase ledger differs")
    return value


def _duration(result: Mapping[str, Any], phase: str) -> int:
    value = result["phase_times_absolute"]["phases"][phase]["duration_ns"]
    if type(value) is not int or value <= 0:
        raise RuntimeError(f"Goal5810 invalid phase duration: {phase}")
    return value


def _edge(result: Mapping[str, Any], phase: str, edge: str) -> int:
    value = result["phase_times_absolute"]["phases"][phase][
        f"{edge}_perf_counter_ns"]
    if type(value) is not int or value < 0:
        raise RuntimeError(f"Goal5810 invalid phase edge: {phase}.{edge}")
    return value


def _condition_summary(rows: list[dict[str, Any]]) -> dict[str, object]:
    phases = {
        phase: statistics.median(_duration(row, phase) for row in rows)
        for phase in PHASES
    }
    continuous = {
        "session_start_to_second_exact_output": statistics.median(
            _edge(row, "second_app_first_exact_execute", "end")
            - _edge(row, "first_session_admission", "start")
            for row in rows),
        "first_prepare_start_to_second_exact_output": statistics.median(
            _edge(row, "second_app_first_exact_execute", "end")
            - _edge(row, "first_app_prepare", "start")
            for row in rows),
    }
    return {
        "sample_count": len(rows),
        "phase_median_ns": phases,
        "phase_median_ms": {
            key: value / 1_000_000.0 for key, value in phases.items()
        },
        "continuous_median_ns": continuous,
        "continuous_median_ms": {
            key: value / 1_000_000.0 for key, value in continuous.items()
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--expected-target-manifest-sha256", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--blocks", type=int, default=4)
    args = parser.parse_args()
    if args.blocks <= 0 or args.blocks > 16:
        raise RuntimeError("Goal5810 block count is outside 1..16")
    if args.output_root.exists() or args.output.exists():
        raise RuntimeError("Goal5810 controller output already exists")
    args.output_root.mkdir(parents=True)
    worker = args.worker.resolve(strict=True)
    target = args.target_manifest.resolve(strict=True)
    if _sha(target) != args.expected_target_manifest_sha256:
        raise RuntimeError("Goal5810 controller target SHA-256 differs")

    journal: list[dict[str, Any]] = []
    results: dict[tuple[str, str], list[dict[str, Any]]] = {
        (first, arm): [] for first in FIRST_APPS for arm in ARMS
    }
    worker_index = 0
    for block in range(args.blocks):
        first_apps = FIRST_APPS if block % 2 == 0 else tuple(reversed(FIRST_APPS))
        arm_order = (
            ("rtdl", "pyoptix", "pyoptix", "rtdl")
            if block % 2 == 0 else
            ("pyoptix", "rtdl", "rtdl", "pyoptix")
        )
        for first_app in first_apps:
            for slot, arm in enumerate(arm_order):
                stem = (
                    f"worker_{worker_index:03d}_block_{block:02d}_"
                    f"{first_app}_first_{arm}_slot_{slot}")
                output = args.output_root / f"{stem}.json"
                cache = args.output_root / f"{stem}_cache"
                stdout_path = args.output_root / f"{stem}.stdout"
                stderr_path = args.output_root / f"{stem}.stderr"
                command = [
                    sys.executable, "-B", str(worker),
                    "--arm", arm,
                    "--target-manifest", str(target),
                    "--expected-target-manifest-sha256",
                    args.expected_target_manifest_sha256,
                    "--first-app", first_app,
                    "--cache-root", str(cache),
                    "--output", str(output),
                ]
                process = subprocess.run(
                    command, text=True, capture_output=True, check=False)
                stdout_path.write_text(process.stdout, encoding="utf-8")
                stderr_path.write_text(process.stderr, encoding="utf-8")
                row = {
                    "worker_index": worker_index,
                    "block": block,
                    "first_app": first_app,
                    "arm": arm,
                    "slot": slot,
                    "returncode": process.returncode,
                    "output_path": str(output),
                    "stdout": _file_row(stdout_path),
                    "stderr": _file_row(stderr_path),
                }
                journal.append(row)
                if process.returncode != 0:
                    raise RuntimeError({"Goal5810_worker_failed": row})
                result = _read_result(output)
                if result.get("app_order", [None])[0] != first_app \
                        or result.get("scope", {}).get("arm") != {
                            "rtdl": "RTDL_SHARED_RUNTIME_SESSION",
                            "pyoptix": "PYOPTIX_SHARED_DEVICE_CONTEXT",
                        }[arm]:
                    raise RuntimeError("Goal5810 worker condition differs")
                row["output"] = _file_row(output)
                row["process_pid"] = result["process_pid"]
                results[(first_app, arm)].append(result)
                worker_index += 1

    conditions = {
        f"{first_app}_first/{arm}": _condition_summary(
            results[(first_app, arm)])
        for first_app in FIRST_APPS for arm in ARMS
    }
    comparisons: dict[str, Any] = {}
    for first_app in FIRST_APPS:
        rtdl = conditions[f"{first_app}_first/rtdl"]
        pyoptix = conditions[f"{first_app}_first/pyoptix"]
        comparisons[first_app] = {
            "phase_ratio_of_medians_rtdl_over_pyoptix": {
                phase: (
                    rtdl["phase_median_ns"][phase]
                    / pyoptix["phase_median_ns"][phase])
                for phase in PHASES
            },
            "continuous_ratio_of_medians_rtdl_over_pyoptix": {
                name: (
                    rtdl["continuous_median_ns"][name]
                    / pyoptix["continuous_median_ns"][name])
                for name in rtdl["continuous_median_ns"]
            },
        }
    position_effects = {
        arm: {
            "relation_first_prepare_median_ns": conditions[
                f"relation_first/{arm}"]["phase_median_ns"][
                    "first_app_prepare"],
            "relation_second_prepare_median_ns": conditions[
                f"triangle_first/{arm}"]["phase_median_ns"][
                    "second_app_prepare"],
            "triangle_first_prepare_median_ns": conditions[
                f"triangle_first/{arm}"]["phase_median_ns"][
                    "first_app_prepare"],
            "triangle_second_prepare_median_ns": conditions[
                f"relation_first/{arm}"]["phase_median_ns"][
                    "second_app_prepare"],
        }
        for arm in ARMS
    }
    body = {
        "schema": SCHEMA,
        "status": STATUS,
        "scope": {
            "diagnostic_only": True,
            "home_pascal_only": True,
            "rt_core_evidence": False,
            "formal_evidence": False,
            "paper_evidence": False,
            "claim_authorized": False,
            "threshold_or_pass_fail_gate_present": False,
            "all_structurally_valid_results_accepted": True,
            "retry_count": 0,
            "replacement_count": 0,
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0,
            "descriptive_phase_duration_count": worker_index * len(PHASES),
        },
        "matrix": {
            "block_count": args.blocks,
            "worker_count": worker_index,
            "unique_process_pid_count": len({
                row["process_pid"] for row in journal
            }),
            "fresh_process_per_worker": True,
            "fresh_cache_root_per_worker": True,
            "arm_order_alternated_by_block": True,
            "first_app_order_alternated_by_block": True,
            "condition_sample_count": args.blocks * 2,
        },
        "inputs": {
            "controller": _file_row(Path(__file__)),
            "worker": _file_row(worker),
            "target_manifest": _file_row(target),
            "python_executable": _file_row(Path(sys.executable)),
        },
        "conditions": conditions,
        "descriptive_comparisons": comparisons,
        "task_position_effects": position_effects,
        "journal": journal,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    result = {**body, "matrix_sha256": _digest(body)}
    with args.output.open("xb") as handle:
        handle.write(_canonical(result) + b"\n")
    print(json.dumps({
        "status": STATUS,
        "worker_count": worker_index,
        "unique_process_pid_count": result["matrix"][
            "unique_process_pid_count"],
        "matrix_sha256": result["matrix_sha256"],
        "output": str(args.output.resolve(strict=True)),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
