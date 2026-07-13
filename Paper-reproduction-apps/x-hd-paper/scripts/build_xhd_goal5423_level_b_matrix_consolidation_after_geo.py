#!/usr/bin/env python3
"""Build Goal5423 consolidation after the bounded-geo packet execution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
GOAL5419 = RESULTS / "xhd_goal5419_figure5_level_b_same_pod_graphics_matrix.json"
GOAL5422 = RESULTS / "xhd_goal5422_bounded_geo_same_pod_packet_execution.json"
OUT = RESULTS / "xhd_goal5423_level_b_matrix_consolidation_after_geo.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _graphics_rows(goal5419: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in goal5419["rows"]:
        best_exact = [
            route for route in row["rtdl_routes"] if route["rtdl"]["per_source_witness_exact"]
        ]
        best_scalar = [
            route for route in row["rtdl_routes"] if not route["rtdl"]["per_source_witness_exact"]
        ]
        rows.append(
            {
                "case_id": row["case_id"],
                "category": "graphics",
                "input_identity_level": row["input_identity_level"],
                "author_hd_result": row["author"]["hd_result"],
                "author_running_avg_time_ms": row["author"]["running_avg_time_ms"],
                "author_process_wall_sec": row["author_process_wall_sec"],
                "author_rerun_matches_paper_log": row["author_rerun_matches_paper_log"],
                "route_count": len(row["rtdl_routes"]),
                "all_routes_match_author": all(route["matched_author_rerun"] for route in row["rtdl_routes"]),
                "exact_witness_route_labels": [route["route_label"] for route in best_exact],
                "scalar_only_route_labels": [route["route_label"] for route in best_scalar],
                "ratio_authorized": False,
                "figure5_reproduction_claimed": False,
            }
        )
    return rows


def _geo_rows(goal5422: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in goal5422["rows"]:
        rows.append(
            {
                "case_id": row["case_id"],
                "category": "geo_bounded",
                "input_identity_level": row["input_identity_level"],
                "paper_pair": row["paper_pair"],
                "point_counts": row["point_counts"],
                "author_hd_result": row["author"]["HDResult"],
                "author_running_avg_time_ms": row["author"]["Running_AvgTime_ms"],
                "author_process_wall_sec": row["author"]["remote_process_wall_sec"],
                "rtdl_hd_result": row["rtdl"]["HDResult"],
                "rtdl_route_sec": row["rtdl"]["run_phases"]["rtdl_route_sec"],
                "rtdl_total_sec": row["rtdl"]["run_phases"]["total_sec"],
                "abs_diff_vs_author": row["comparison"]["abs_diff"],
                "tolerance": row["comparison"]["tolerance"],
                "matched_author": row["comparison"]["matched"],
                "route": row["rtdl"]["route"],
                "partner": row["rtdl"]["partner"],
                "triton_strategy": row["rtdl"]["triton_strategy"],
                "per_source_witness_exact": row["rtdl"]["per_source_witness_exact"],
                "ratio_authorized": False,
                "figure5_reproduction_claimed": False,
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    goal5419 = _load(GOAL5419)
    goal5422 = _load(GOAL5422)
    graphics = _graphics_rows(goal5419)
    geo = _geo_rows(goal5422)
    all_match = (
        bool(goal5419["matched"])
        and bool(goal5422["matched"])
        and all(row["all_routes_match_author"] for row in graphics)
        and all(row["matched_author"] for row in geo)
    )
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5423.level_b_matrix_consolidation_after_geo.v1",
        "goal": "Goal5423",
        "status": "level_b_same_pod_matrix_consolidated_after_geo__review_node__no_ratio",
        "matched": all_match,
        "coverage": {
            "graphics_case_count": len(graphics),
            "graphics_route_result_count": sum(row["route_count"] for row in graphics),
            "bounded_geo_case_count": len(geo),
            "bounded_geo_route_result_count": len(geo),
            "total_case_count": len(graphics) + len(geo),
        },
        "graphics_rows": graphics,
        "bounded_geo_rows": geo,
        "claim_boundary": {
            "level_b_same_pod_scalar_matrix_claimed": True,
            "figure5_reproduction_claimed": False,
            "full_figure5_matrix_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "explicit_lb_reopened": False,
            "route_micro_optimization_goal_authorized": False,
        },
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": (
                "generic_directed_max_of_nearest_distance_2d / "
                "Goal5128 facility-service-radius consumer family"
            ),
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "pass_no_app_artifact_parity_work_authorized",
        },
        "remaining_blockers": [
            {
                "blocker": "exact_paper_dataset_files_or_hashes_missing",
                "impact": "prevents exact paper dataset and full Figure 5 reproduction claims",
            },
            {
                "blocker": "figures_5_to_11_denominators_not_aligned",
                "impact": "prevents author-vs-RTDL performance ratios",
            },
            {
                "blocker": "explicit_lb_row_identity_fail_closed",
                "impact": "prevents Figure 7 load-balance implementation-artifact parity line",
            },
            {
                "blocker": "fast_scalar_routes_are_scalar_only_when_per_source_witness_exact_false",
                "impact": "prevents exact per-source witness claims for fast-scalar rows",
            },
        ],
        "next_recommendation": {
            "strict_review_packet": True,
            "route_micro_optimization": False,
            "explicit_lb": False,
            "preferred_next_goal": "Goal5424_strict_review_packet_for_5419_5423_or_return_to_exact_dataset_acquisition",
        },
        "source_artifacts": {
            "goal5419": str(GOAL5419),
            "goal5422": str(GOAL5422),
        },
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"matched": payload["matched"], "status": payload["status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
