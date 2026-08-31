#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Callable


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SCHEMA = "rtdl.goal3872.prepared_session_amortization_probe.v1"
DEFAULT_OUTPUT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3872_prepared_session_amortization_a5000"
    / "summary.json"
)

FORBIDDEN_TRUE_FLAGS = (
    "release_authorized",
    "public_speedup_claim_authorized",
    "whole_app_speedup_claim_authorized",
    "broad_rt_core_claim_authorized",
    "broad_rt_core_speedup_claim_authorized",
    "paper_reproduction_claim_authorized",
    "true_zero_copy_claim_authorized",
    "true_zero_copy_authorized",
    "automatic_partner_selection_authorized",
    "app_specific_native_engine_logic_allowed",
    "amd_performance_claim_authorized",
)


def _claim_boundary() -> dict[str, bool]:
    return {
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "app_specific_native_engine_logic_allowed": False,
        "amd_performance_claim_authorized": False,
    }


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _find_forbidden_true_flags(value: Any, *, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_TRUE_FLAGS and child is True:
                hits.append(child_path)
            hits.extend(_find_forbidden_true_flags(child, path=child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(_find_forbidden_true_flags(child, path=f"{path}[{index}]"))
    return hits


def _run_json_command(command: list[str], *, timeout_sec: int) -> tuple[dict[str, Any], dict[str, Any]]:
    start = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_sec,
        check=False,
    )
    elapsed = time.perf_counter() - start
    parse_error = None
    payload: dict[str, Any] = {}
    if completed.returncode == 0:
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            parse_error = str(exc)
    return payload, {
        "command": command,
        "returncode": completed.returncode,
        "elapsed_sec": elapsed,
        "stdout_bytes": len(completed.stdout.encode("utf-8")),
        "stderr_bytes": len(completed.stderr.encode("utf-8")),
        "stderr_tail": completed.stderr[-4000:],
        "stdout_json_parse_error": parse_error,
    }


def _ratio(numerator: float, denominator: float) -> float | None:
    if denominator == 0.0:
        return None
    return float(numerator) / float(denominator)


def _hausdorff_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    repeat = int(payload["repeat_protocol"]["repeat"])
    query_total = float(payload["repeat_protocol"]["measured_query_total_sec"])
    query_per_request = query_total / repeat
    prepare = float(payload["run_phases"]["scene_prepare_sec"])
    return {
        "prepared_family": "fixed_radius_threshold_2d",
        "repeat": repeat,
        "prepare_sec": prepare,
        "hot_query_total_sec": query_total,
        "hot_query_per_request_sec": query_per_request,
        "prepare_to_single_query_ratio": _ratio(prepare, query_per_request),
        "rt_core_accelerated": bool(payload.get("rt_core_accelerated")),
    }


def _librts_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    repeat = int(payload["repeat_protocol"]["repeat"])
    query_total = float(payload["run_phases"]["query_total_sec"])
    query_median = float(payload["run_phases"]["query_median_sec"])
    prepare = float(payload["run_phases"]["scene_prepare_sec"])
    return {
        "prepared_family": "aabb_index_query_2d",
        "repeat": repeat,
        "prepare_sec": prepare,
        "hot_query_total_sec": query_total,
        "hot_query_per_request_sec": query_median,
        "prepare_to_single_query_ratio": _ratio(prepare, query_median),
        "rt_core_accelerated": bool(payload.get("rt_core_accelerated")),
    }


def _rtnn_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    runner = payload["runner_payload"]
    repeat = int(runner["repeat"])
    query_median = float(runner["elapsed_median_sec"])
    query_total = float(sum(runner["elapsed_runs_sec"]))
    prepare = float(runner["execution_prepare_sec"])
    return {
        "prepared_family": "fixed_radius_neighbors_3d_ranked_summary",
        "repeat": repeat,
        "prepare_sec": prepare,
        "hot_query_total_sec": query_total,
        "hot_query_per_request_sec": query_median,
        "prepare_to_single_query_ratio": _ratio(prepare, query_median),
        "rt_core_accelerated": True,
    }


def _triangle_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    timing = payload["timing_ms"]
    repeat = int(timing["query_repeat"])
    query_median = float(timing["query_median_ms"]) / 1000.0
    query_total = query_median * repeat
    prepare = float(timing["prepare_scene_ms"]) / 1000.0
    return {
        "prepared_family": "ray_triangle_weighted_any_hit_sum_3d",
        "repeat": repeat,
        "prepare_sec": prepare,
        "hot_query_total_sec": query_total,
        "hot_query_per_request_sec": query_median,
        "prepare_to_single_query_ratio": _ratio(prepare, query_median),
        "rt_core_accelerated": bool(payload.get("rt_core_accelerated")),
    }


def _case_definitions(repeat: int, warmup: int) -> tuple[dict[str, Any], ...]:
    py = sys.executable
    return (
        {
            "app": "hausdorff_xhd",
            "timeout_sec": 240,
            "command": [
                py,
                "examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py",
                "--backend",
                "optix",
                "--require-rt-core",
                "--optix-summary-mode",
                "directed_threshold_prepared",
                "--hausdorff-threshold",
                "0.25",
                "--copies",
                "1024",
                "--repeat",
                str(repeat),
                "--warmup",
                str(warmup),
            ],
            "extract": _hausdorff_metrics,
        },
        {
            "app": "librts_spatial_index",
            "timeout_sec": 240,
            "command": [
                py,
                "examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py",
                "--mode",
                "optix_aabb_index",
                "--dataset",
                "uniform",
                "--box-count",
                "32768",
                "--query-count",
                "32768",
                "--operation",
                "all",
                "--repeat",
                str(repeat),
                "--warmup",
                str(warmup),
            ],
            "extract": _librts_metrics,
        },
        {
            "app": "rtnn",
            "timeout_sec": 240,
            "command": [
                py,
                "examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py",
                "--mode",
                "prepared_optix_ranked_summary",
                "--point-count",
                "65536",
                "--radius",
                "0.02",
                "--k",
                "50",
                "--repeat",
                str(repeat),
                "--query-batch-size",
                "65536",
                "--distribution",
                "uniform",
            ],
            "extract": _rtnn_metrics,
        },
        {
            "app": "triangle_counting",
            "timeout_sec": 240,
            "command": [
                py,
                "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py",
                "--mode",
                "rt_graph_2a1_generic_rt",
                "--backend",
                "optix",
                "--fixture",
                "degree_oriented_two_triangles",
                "--rt-graph-copies",
                "2048",
                "--detail",
                "summary",
                "--repeat",
                str(repeat),
                "--warmup",
                str(warmup),
            ],
            "extract": _triangle_metrics,
        },
    )


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for case in _case_definitions(args.repeat, args.warmup):
        app_name = str(case["app"])
        print(f"[goal3872] start {app_name}", flush=True)
        payload, process = _run_json_command(case["command"], timeout_sec=int(case["timeout_sec"]))
        ok = process["returncode"] == 0 and process["stdout_json_parse_error"] is None
        metrics: dict[str, Any] = {}
        if ok:
            metrics = case["extract"](payload)
        claim_violations = _find_forbidden_true_flags(payload) if payload else []
        row = {
            "app": app_name,
            "status": "pass" if ok and not claim_violations else "fail",
            "process": process,
            "metrics": metrics,
            "claim_flag_violations": claim_violations,
            "payload_git_status_short": payload.get("git_status_short") if isinstance(payload, dict) else None,
            "claim_boundary": _claim_boundary(),
        }
        rows.append(row)
        print(
            f"[goal3872] done {app_name} status={row['status']} "
            f"elapsed={process['elapsed_sec']:.3f}s",
            flush=True,
        )

    prepare_ratios = [
        float(row["metrics"]["prepare_to_single_query_ratio"])
        for row in rows
        if row["status"] == "pass" and row["metrics"].get("prepare_to_single_query_ratio") is not None
    ]
    return {
        "schema": SCHEMA,
        "generated_at_unix": time.time(),
        "source_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "source_commit_short": _command_output(["git", "rev-parse", "--short", "HEAD"]),
        "git_status_short": _command_output(["git", "status", "--short"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "repeat": int(args.repeat),
        "warmup": int(args.warmup),
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "all_pass": all(row["status"] == "pass" for row in rows),
            "all_claim_boundaries_clean": all(not row["claim_flag_violations"] for row in rows),
            "max_prepare_to_single_query_ratio": max(prepare_ratios) if prepare_ratios else None,
            "geomean_prepare_to_single_query_ratio": (
                math.prod(prepare_ratios) ** (1.0 / len(prepare_ratios)) if prepare_ratios else None
            ),
        },
        "interpretation": (
            "Prepared-session amortization probe for scene-heavy benchmark rows. "
            "It measures how much one-time scene/prepared setup dominates the "
            "file-backed CLI row versus warmed repeated query work. This is not "
            "release evidence and not a public speedup claim."
        ),
        "claim_boundary": _claim_boundary(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Goal3872 prepared-session amortization probe.")
    parser.add_argument("--repeat", type=int, default=50)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.repeat <= 0:
        raise ValueError("--repeat must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3872] wrote {args.output}", flush=True)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
