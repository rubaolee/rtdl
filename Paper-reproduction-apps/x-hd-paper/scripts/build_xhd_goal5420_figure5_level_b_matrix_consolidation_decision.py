#!/usr/bin/env python3
"""Build the Goal5420 X-HD Figure-5 Level-B matrix consolidation decision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
DEFAULT_GOAL5419 = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5419_figure5_level_b_same_pod_graphics_matrix.json"
)
DEFAULT_GOAL5417 = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5417_figure5_level_b_same_pod_matrix_plan.json"
)
DEFAULT_SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5420_figure5_level_b_matrix_consolidation_decision.json"
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _graphics_summary(goal5419: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in goal5419["rows"]:
        route_rows = []
        for route in row["rtdl_routes"]:
            route_rows.append(
                {
                    "route_label": route["route_label"],
                    "matched_author_rerun": route["matched_author_rerun"],
                    "abs_diff_vs_author_rerun": route["abs_diff_vs_author_rerun"],
                    "rtdl_route_wall_sec": route["rtdl"]["rtdl_route_wall_sec"],
                    "rtdl_process_wall_sec": route["process_wall_sec"],
                    "rtdl_input_load_sec": route["rtdl"]["rtdl_input_load_sec"],
                    "per_source_witness_exact": route["rtdl"]["per_source_witness_exact"],
                    "ratio_authorized": route["ratio_authorized"],
                }
            )
        rows.append(
            {
                "case_id": row["case_id"],
                "input_identity_level": row["input_identity_level"],
                "author_hd_result": row["author"]["hd_result"],
                "author_running_avg_time_ms": row["author"]["running_avg_time_ms"],
                "author_process_wall_sec": row["author_process_wall_sec"],
                "author_rerun_matches_paper_log": row["author_rerun_matches_paper_log"],
                "required_rtdl_preprocessing": row["required_rtdl_preprocessing"],
                "rtdl_routes": route_rows,
                "ratio_authorized": row["ratio_authorized"],
            }
        )
    return rows


def build_decision(args: argparse.Namespace) -> dict[str, Any]:
    goal5419 = _read_json(Path(args.goal5419))
    goal5417 = _read_json(Path(args.goal5417))

    if goal5419.get("schema") != "rtdl.paper_reproduction.xhd.goal5419.figure5_level_b_same_pod_graphics_matrix.v1":
        raise ValueError("Goal5420 requires the Goal5419 graphics matrix artifact")
    if not bool(goal5419.get("matched")):
        raise ValueError("Goal5419 matrix must be matched before consolidation")

    secondary_geo = goal5417["secondary_bounded_geo_candidates"]
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5420.figure5_level_b_matrix_consolidation_decision.v1",
        "goal": "Goal5420",
        "status": "figure5_level_b_graphics_matrix_consolidated__bounded_geo_packet_next__no_ratio",
        "matched": True,
        "source_artifacts": {
            "goal5419": str(args.goal5419),
            "goal5417": str(args.goal5417),
        },
        "graphics_matrix": {
            "same_pod_execution_claimed": goal5419["same_pod_execution_claimed"],
            "graphics_case_count": goal5419["graphics_case_count"],
            "route_result_count": goal5419["route_result_count"],
            "matched": goal5419["matched"],
            "rows": _graphics_summary(goal5419),
        },
        "decision": {
            "graphics_matrix_ready_for_strict_review": True,
            "continue_route_micro_optimization_by_default": False,
            "bounded_geo_matrix_packet_authorized_next": True,
            "bounded_geo_matrix_execution_authorized_now": False,
            "return_to_exact_dataset_work_without_geo_packet": False,
            "recommended_next_goal": "Goal5421_bounded_geo_same_pod_packet_plan",
        },
        "decision_rationale": [
            "Goal5419 already provides the same-POD graphics matrix for the three value-matched Level-B graphics cases.",
            "The two bounded geo rows were intentionally deferred because they use a partner/Triton runner family rather than the graphics hd_exec-compatible packet.",
            "A separate bounded-geo packet can expand Figure-5-like Level-B coverage without claiming exact paper datasets or mixing runner families.",
            "Route micro-optimization is not the default next step because the current blocker is coverage/provenance/denominator alignment, not a missing graphics-route timing column.",
            "The explicit -lb row-identity line remains stopped and must not be restarted from this decision.",
        ],
        "secondary_bounded_geo_candidates": [
            {
                "case_id": case["case_id"],
                "input_identity_level": "level_b_bounded_geo_fixture",
                "point_counts": case["point_counts"],
                "prior_author_hd_result": case["author_hd_result"],
                "prior_rtdl_hd_result": case["prior_rtdl_hd_result"],
                "prior_abs_diff": case["prior_abs_diff"],
                "tolerance": case["tolerance"],
                "planned_rtdl_routes": case["planned_rtdl_routes"],
                "packet_status": "authorize_separate_packet_plan_not_execution",
            }
            for case in secondary_geo
        ],
        "claim_boundary": {
            "figure5_reproduction_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "bounded_geo_execution_claimed": False,
            "route_micro_optimization_goal_authorized": False,
            "explicit_lb_reopened": False,
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--goal5419", type=Path, default=DEFAULT_GOAL5419)
    parser.add_argument("--goal5417", type=Path, default=DEFAULT_GOAL5417)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args(list(argv) if argv is not None else None)
    payload = build_decision(args)
    _write_json(Path(args.summary), payload)
    print(json.dumps({"matched": payload["matched"], "status": payload["status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
