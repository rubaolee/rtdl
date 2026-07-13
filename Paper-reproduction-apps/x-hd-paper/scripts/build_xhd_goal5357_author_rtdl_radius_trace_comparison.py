#!/usr/bin/env python3
"""Build Goal5357 author-vs-RTDL radius trace comparison evidence.

This goal consumes the existing Goal5355 author trace mapping artifact and the
Goal5356 RTDL route trace metadata artifact.  It intentionally treats the
current RTDL single-pass route as a negative/control row: matching HDResult is
not the same as matching the author's adaptive radius queue semantics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _first_repeat_iterations(author_payload: dict[str, Any]) -> list[dict[str, Any]]:
    repeat = author_payload["Running"]["Repeats"][0]
    return [dict(row) for row in repeat.get("Iterations", [])]


def _find_case(mapping: dict[str, Any], case_id: str) -> dict[str, Any]:
    for case in mapping.get("cases", []):
        if case.get("case_id") == case_id:
            return dict(case)
    raise KeyError(f"author mapping case not found: {case_id}")


def _bounded3d_comparison(author_mapping: dict[str, Any], rtdl_route_trace: dict[str, Any]) -> dict[str, Any]:
    author_case = _find_case(author_mapping, "bounded3d_author_gate")
    author_json = Path(str(author_case["author_json"]))
    author_payload = _load_json(author_json)
    author_iterations = _first_repeat_iterations(author_payload)
    if not author_iterations:
        raise ValueError("bounded3d author trace must contain at least one iteration")
    author_first = author_iterations[0]

    route_probe = dict(rtdl_route_trace["route_probe"])
    trace = dict(rtdl_route_trace["radius_trace_metadata"])
    directions = list(trace.get("directions", []))
    if len(directions) != 1:
        raise ValueError("Goal5356 bounded3d RTDL trace is expected to contain one direction")
    rtdl_first = dict(directions[0])

    author_hd = float(author_payload["HDResult"])
    rtdl_hd = float(route_probe["hd_result"])
    hd_result_abs_diff = abs(author_hd - rtdl_hd)
    hd_result_matched = hd_result_abs_diff <= 1.0e-6

    comparable = bool(trace.get("author_queue_semantics_aligned")) and bool(trace.get("author_trace_comparison_ready"))
    semantic_mismatches = [
        {
            "field": "iteration_model",
            "author": "author_adaptive_radius_queue_loop",
            "rtdl": trace.get("route_iteration_model"),
            "reason": "Current RTDL route emits one single-pass diagnostic row, not the author's radius queue loop.",
        },
        {
            "field": "radius",
            "author": float(author_first["Radius"]),
            "rtdl": float(rtdl_first["radius"]),
            "reason": "Author bounded3d starts from HD lower bound 2.0; current RTDL trace records the route's full-cover fallback radius.",
        },
        {
            "field": "num_output_points",
            "author": int(author_first["NumOutputPoints"]),
            "rtdl": int(rtdl_first["num_output_points"]),
            "reason": "Author NumOutputPoints is unresolved queue size after an iteration; RTDL num_output_points is frontier row count after a single pass.",
        },
        {
            "field": "route_uses_radius_growth_helper",
            "author": True,
            "rtdl": bool(trace.get("route_uses_radius_growth_helper")),
            "reason": "Goal5355 maps author transitions to radius_growth_step, but the current RTDL route does not use that helper to drive iterations.",
        },
    ]

    return {
        "case_id": "bounded3d_author_vs_rtdl_single_pass",
        "input_fixture": "bounded3d_a.wkt -> bounded3d_b.wkt",
        "author": {
            "source_artifact": str(author_json),
            "iteration_model": "author_adaptive_radius_queue_loop",
            "iteration_count": len(author_iterations),
            "hd_result": author_hd,
            "first_iteration": {
                "iteration": int(author_first["Iteration"]),
                "radius": float(author_first["Radius"]),
                "num_input_points": int(author_first["NumInputPoints"]),
                "num_output_points": int(author_first["NumOutputPoints"]),
            },
        },
        "rtdl": {
            "source_artifact": str(RESULTS / "xhd_goal5356_route_radius_trace_metadata.json"),
            "iteration_model": trace.get("route_iteration_model"),
            "direction_count": len(directions),
            "hd_result": rtdl_hd,
            "first_direction": {
                "label": rtdl_first.get("label"),
                "iteration": int(rtdl_first["iteration"]),
                "radius": float(rtdl_first["radius"]),
                "num_input_points": int(rtdl_first["num_input_points"]),
                "num_output_points": int(rtdl_first["num_output_points"]),
                "input_count_semantics": rtdl_first.get("input_count_semantics"),
                "output_count_semantics": rtdl_first.get("output_count_semantics"),
            },
            "author_queue_semantics_aligned": bool(trace.get("author_queue_semantics_aligned")),
            "author_trace_comparison_ready": bool(trace.get("author_trace_comparison_ready")),
            "route_uses_radius_growth_helper": bool(trace.get("route_uses_radius_growth_helper")),
        },
        "value_result": {
            "hd_result_matched": hd_result_matched,
            "abs_diff": hd_result_abs_diff,
            "tolerance": 1.0e-6,
        },
        "trace_result": {
            "comparable_as_author_radius_queue": comparable,
            "matched": False,
            "semantic_mismatches": semantic_mismatches,
        },
        "decision": {
            "explicit_author_tune_radius_must_remain_fail_closed": True,
            "reason": "The current RTDL route matches bounded3d HDResult but does not emit author-like radius/input/output queue iterations.",
        },
    }


def build_artifact() -> dict[str, Any]:
    author_mapping_path = RESULTS / "xhd_goal5355_radius_trace_mapping.json"
    rtdl_trace_path = RESULTS / "xhd_goal5356_route_radius_trace_metadata.json"
    author_mapping = _load_json(author_mapping_path)
    rtdl_trace = _load_json(rtdl_trace_path)
    comparison = _bounded3d_comparison(author_mapping, rtdl_trace)
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5357.author_rtdl_radius_trace_comparison.v1",
        "goal": "Goal5357",
        "date": "2026-07-09",
        "status": "trace_comparison_complete__rtdl_value_matches_but_radius_trace_not_author_queue_aligned",
        "purpose": (
            "Compare existing author hd_exec radius trace evidence with current "
            "RTDL route radius trace metadata, and keep explicit author tune_radius "
            "fail-closed unless the route emits comparable author-like iterations."
        ),
        "inputs": {
            "author_mapping_artifact": str(author_mapping_path),
            "rtdl_route_trace_artifact": str(rtdl_trace_path),
        },
        "comparison": comparison,
        "summary": {
            "hd_result_matched": comparison["value_result"]["hd_result_matched"],
            "trace_matched": comparison["trace_result"]["matched"],
            "trace_comparable_as_author_radius_queue": comparison["trace_result"][
                "comparable_as_author_radius_queue"
            ],
            "semantic_mismatch_count": len(comparison["trace_result"]["semantic_mismatches"]),
            "explicit_author_tune_radius_must_remain_fail_closed": comparison["decision"][
                "explicit_author_tune_radius_must_remain_fail_closed"
            ],
        },
        "claim_boundary": {
            "author_tune_radius_route_mapping_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "figure8_reproduction_claimed": False,
            "performance_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "recommended_next_targets": [
            "decide_whether_to_build_author_like_radius_queue_route_or_stop_tune_radius_line",
            "if_built_emit_author_like_radius_input_output_iterations_using_generic_radius_growth_step",
            "only_after_trace_match_consider_accepting_explicit_author_tune_radius",
        ],
        "exit_label": "current_single_pass_route_not_author_tune_radius_compatible__keep_explicit_tune_radius_fail_closed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS / "xhd_goal5357_author_rtdl_radius_trace_comparison.json",
    )
    args = parser.parse_args()
    payload = build_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "status": payload["status"],
                "hd_result_matched": payload["summary"]["hd_result_matched"],
                "trace_matched": payload["summary"]["trace_matched"],
                "exit_label": payload["exit_label"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
