#!/usr/bin/env python3
"""Build Goal5428 Level-B matrix including Water/BG full-public paper-config row."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
GOAL5423 = RESULTS / "xhd_goal5423_level_b_matrix_consolidation_after_geo.json"
GOAL5427 = RESULTS / "xhd_goal5427_water_bg_paper_config_consolidation.json"
OUT = RESULTS / "xhd_goal5428_level_b_matrix_with_water_bg_full_public.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _full_public_geo_row(goal5427: dict[str, Any]) -> dict[str, Any]:
    author = goal5427["author_denominator"]
    rtdl = goal5427["rtdl_evidence"]
    return {
        "case_id": "geo_water_bg_full_public_paper_config",
        "category": "geo_full_public",
        "input_identity_level": "level_b_full_public_same_source_geo_not_exact_file_hash",
        "paper_pair": "USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt",
        "point_counts": [22824823, 52271467],
        "author_denominator": author["selected"],
        "author_hd_result": author["hd_result"],
        "author_running_avg_time_ms": author["avg_time_ms"],
        "author_matches_paper_log": author["matches_paper_log"],
        "rtdl_hd_result_float64": rtdl["hd_result_float64"],
        "abs_diff_vs_author": rtdl["abs_diff_vs_author_paper_config"],
        "tolerance": rtdl["declared_tolerance"],
        "matched_author": rtdl["matched_with_declared_tolerance"],
        "per_source_witness_exact": rtdl["per_source_witness_exact"],
        "rtdl_route_sec": rtdl["route_sec"],
        "rtdl_total_sec": rtdl["entrypoint_total_sec"],
        "same_witness_float32_distance": rtdl["same_witness_float32_distance"],
        "distance_float32_matches_paper_log": rtdl["distance_float32_matches_paper_log"],
        "ratio_authorized": False,
        "figure5_reproduction_claimed": False,
        "exact_paper_dataset_reproduction_claimed": False,
        "new_execution_claimed": False,
    }


def build_payload() -> dict[str, Any]:
    goal5423 = _load(GOAL5423)
    goal5427 = _load(GOAL5427)
    full_geo = [_full_public_geo_row(goal5427)]
    matched = (
        bool(goal5423["matched"])
        and bool(goal5427["matched"])
        and all(row["matched_author"] for row in full_geo)
    )
    coverage = {
        "graphics_case_count": int(goal5423["coverage"]["graphics_case_count"]),
        "graphics_route_result_count": int(goal5423["coverage"]["graphics_route_result_count"]),
        "bounded_geo_case_count": int(goal5423["coverage"]["bounded_geo_case_count"]),
        "bounded_geo_route_result_count": int(goal5423["coverage"]["bounded_geo_route_result_count"]),
        "full_public_geo_case_count": len(full_geo),
        "full_public_geo_route_result_count": len(full_geo),
    }
    coverage["total_case_count"] = (
        coverage["graphics_case_count"]
        + coverage["bounded_geo_case_count"]
        + coverage["full_public_geo_case_count"]
    )
    coverage["total_route_result_count"] = (
        coverage["graphics_route_result_count"]
        + coverage["bounded_geo_route_result_count"]
        + coverage["full_public_geo_route_result_count"]
    )
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5428.level_b_matrix_with_water_bg_full_public.v1",
        "goal": "Goal5428",
        "status": "level_b_matrix_updated_with_water_bg_full_public_paper_config__review_node__no_ratio",
        "matched": matched,
        "coverage": coverage,
        "graphics_rows": goal5423["graphics_rows"],
        "bounded_geo_rows": goal5423["bounded_geo_rows"],
        "full_public_geo_rows": full_geo,
        "claim_boundary": {
            "level_b_same_pod_scalar_matrix_claimed": True,
            "full_public_geo_scalar_row_claimed": True,
            "figure5_reproduction_claimed": False,
            "full_figure5_matrix_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "explicit_lb_reopened": False,
            "route_micro_optimization_goal_authorized": False,
        },
        "remaining_blockers": [
            {
                "blocker": "exact_paper_dataset_files_or_hashes_missing",
                "impact": "WaterBodies/BG is full-public and close to paper logs, but lacks exact file/hash provenance.",
            },
            {
                "blocker": "figures_5_to_11_denominators_not_aligned",
                "impact": "No author-vs-RTDL performance ratio is authorized.",
            },
            {
                "blocker": "fast_scalar_routes_are_scalar_only_when_per_source_witness_exact_false",
                "impact": "Fast-scalar rows cannot claim exact per-source witnesses.",
            },
            {
                "blocker": "explicit_lb_row_identity_fail_closed",
                "impact": "Figure 7 implementation-artifact parity remains stopped.",
            },
        ],
        "next_recommendation": {
            "strict_review_packet": True,
            "route_micro_optimization": False,
            "explicit_lb": False,
            "preferred_next_goal": "strict_review_goals5424_5428_or_exact_dataset_provenance",
        },
        "source_artifacts": {
            "goal5423": str(GOAL5423),
            "goal5427": str(GOAL5427),
        },
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"matched": payload["matched"], "status": payload["status"]}, sort_keys=True))
    return 0 if payload["matched"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
