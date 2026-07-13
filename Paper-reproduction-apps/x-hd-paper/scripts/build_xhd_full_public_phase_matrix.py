#!/usr/bin/env python3
"""Build a phase-boundary matrix for the X-HD full public Level-B candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _author_iterations(author_json: dict[str, object]) -> list[dict[str, object]]:
    running = author_json.get("Running")
    if not isinstance(running, dict):
        return []
    repeats = running.get("Repeats")
    if not isinstance(repeats, list) or not repeats:
        return []
    first = repeats[0]
    if not isinstance(first, dict):
        return []
    iterations = first.get("Iterations")
    if not isinstance(iterations, list):
        return []
    return [item for item in iterations if isinstance(item, dict)]


def _author_repeat(author_json: dict[str, object]) -> dict[str, object]:
    running = author_json.get("Running")
    if not isinstance(running, dict):
        return {}
    repeats = running.get("Repeats")
    if not isinstance(repeats, list) or not repeats or not isinstance(repeats[0], dict):
        return {}
    return repeats[0]


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    author_summary = _load(Path(args.author_summary))
    author_json = _load(Path(args.author_json))
    rtdl_summary = _load(Path(args.rtdl_route_summary))
    rtdl_case = rtdl_summary["cases"][0]  # type: ignore[index]
    rtdl_route = rtdl_case["rtdl_route"]  # type: ignore[index]

    author_run = author_summary.get("author_run")
    author_wall_sec = None
    if isinstance(author_run, dict) and author_run.get("wall_sec") is not None:
        author_wall_sec = float(author_run["wall_sec"])

    author_repeat = _author_repeat(author_json)
    iterations = _author_iterations(author_json)
    author_internal_ms = author_summary.get("author_running_avg_time_ms")
    rtdl_route_wall_sec = float(rtdl_summary["summary_statistics"]["median_route_wall_sec"])  # type: ignore[index]
    rtdl_total_sec = float(rtdl_summary["phase_timings_sec"]["total"])  # type: ignore[index]

    return {
        "schema": "rtdl.paper_reproduction.xhd.full_public_phase_matrix.v1",
        "goal": args.run_goal,
        "status": "full_public_level_b_phase_boundary_matrix_ready",
        "target": rtdl_summary["target"],
        "level": "level_b_same_source_candidate_only",
        "inputs": {
            "source_points": rtdl_summary["full_point_counts"]["source"],  # type: ignore[index]
            "target_points": rtdl_summary["full_point_counts"]["target"],  # type: ignore[index]
            "input1": rtdl_summary["input1"],
            "input2": rtdl_summary["input2"],
        },
        "correctness_anchor": {
            "author_hd_result": author_summary["author_hd_result"],
            "rtdl_route_distance": rtdl_route["distance"],
            "author_abs_diff": rtdl_case["author_abs_diff"],  # type: ignore[index]
            "author_tolerance": rtdl_summary["author_tolerance"],
            "matched": bool(author_summary["matched"]) and bool(rtdl_summary["summary_statistics"]["all_matched"]),  # type: ignore[index]
            "exact_oracle_used": bool(rtdl_case["exact_oracle_used"]),  # type: ignore[index]
        },
        "author_phase_evidence": {
            "source": str(args.author_json),
            "summary": str(args.author_summary),
            "running_avg_time_ms": None if author_internal_ms is None else float(author_internal_ms),
            "process_wall_sec": author_wall_sec,
            "reported_time_ms": None if not author_repeat else author_repeat.get("ReportedTime"),
            "bvh_build_time_ms": None if not author_repeat else author_repeat.get("BVHBuildTime"),
            "grid_resolution": None if not author_repeat else author_repeat.get("GridResolution"),
            "large_cells": None if not author_repeat else author_repeat.get("LargeCells"),
            "iterations": [
                {
                    "iteration": item.get("Iteration"),
                    "num_input_points": item.get("NumInputPoints"),
                    "num_output_points": item.get("NumOutputPoints"),
                    "rt_time_ms": item.get("RTTime"),
                    "cuda_time_ms": item.get("CUDATime"),
                    "offloading_size": item.get("OffloadingSize"),
                    "radius": item.get("Radius"),
                }
                for item in iterations
            ],
        },
        "rtdl_phase_evidence": {
            "source": str(args.rtdl_route_summary),
            "route_wall_sec": rtdl_route_wall_sec,
            "total_sec": rtdl_total_sec,
            "load_full_inputs_sec": rtdl_summary["phase_timings_sec"]["load_full_inputs"],  # type: ignore[index]
            "case_total_sec": rtdl_case["phase_timings_sec"]["case_total"],  # type: ignore[index]
            "select_source_subset_sec": rtdl_case["phase_timings_sec"]["select_source_subset"],  # type: ignore[index]
            "subphases_sec": rtdl_route["phase_timings_sec"],  # type: ignore[index]
            "frontier_row_count": rtdl_route["frontier_row_count"],
            "frontier_row_capacity": rtdl_route["frontier_row_capacity"],
            "frontier_native_symbol": rtdl_route["frontier_native_symbol"],
            "initial_cell_mbr_tests": rtdl_route["initial_cell_mbr_tests"],
            "total_candidate_distance_evaluations": rtdl_route["total_candidate_distance_evaluations"],
        },
        "comparison_policy": {
            "ratio_reported": False,
            "ratio_forbidden_reason": (
                "Author Running.AvgTime is an internal author algorithm phase; "
                "RTDL route_wall_sec and total_sec include different Python/RTDL "
                "phase boundaries. A ratio requires a separate denominator review."
            ),
            "author_running_avg_vs_rtdl_route_ratio_computed": False,
            "author_process_wall_vs_rtdl_total_ratio_computed": False,
        },
        "claim_boundary": {
            "level_b_same_source_candidate_claimed": True,
            "full_public_author_run_claimed": True,
            "full_public_rtdl_all_source_route_claimed": True,
            "phase_matrix_claimed": True,
            "performance_ratio_claimed": False,
            "author_parity_claimed": False,
            "exact_oracle_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
            "figure_reproduction_claimed": False,
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--author-summary", required=True, type=Path)
    parser.add_argument("--author-json", required=True, type=Path)
    parser.add_argument("--rtdl-route-summary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--run-goal", default="Goal5188")
    args = parser.parse_args(list(argv) if argv is not None else None)

    summary = build_summary(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "wrote",
        args.output,
        "matched=",
        summary["correctness_anchor"]["matched"],
        "ratio_reported=",
        summary["comparison_policy"]["ratio_reported"],
    )
    return 0 if summary["correctness_anchor"]["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
