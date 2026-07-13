#!/usr/bin/env python3
"""Build Goal5427 consolidation for full-public Water/BG paper-config evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
GOAL5426 = RESULTS / "xhd_goal5426_full_public_water_bg_wkt_resource_gate.json"
GOAL5314 = RESULTS / "xhd_goal5314_water_bg_corrected_comparison_summary.json"
GOAL5311 = RESULTS / "xhd_goal5311_water_bg_full_public_author_ingestion_summary_pod.json"
OUT = RESULTS / "xhd_goal5427_water_bg_paper_config_consolidation.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    goal5426 = _load(GOAL5426)
    goal5314 = _load(GOAL5314)
    goal5311 = _load(GOAL5311)

    paper_author = goal5314["author"]["paper_config_rerun_n_points_cell_8"]
    default_author = goal5314["author"]["default_rerun_n_points_cell_15"]
    rtdl_exact = goal5314["rtdl"]["exact_witness"]
    tolerance = goal5314["tolerance_boundary"]
    diff = float(rtdl_exact["abs_diff_vs_author_paper_config"])
    tolerance_value = 2.0e-6
    matched = bool(goal5426["matched"]) and bool(
        goal5314["decision"]["water_bg_full_public_rtdl_exact_witness_matches_author_float32_with_declared_tolerance"]
    )
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5427.water_bg_paper_config_consolidation.v1",
        "goal": "Goal5427",
        "status": "existing_goal5314_evidence_sufficient__no_rerun",
        "matched": matched,
        "execution": {
            "new_author_execution": False,
            "new_rtdl_execution": False,
            "reason": (
                "Goal5426 verifies the current POD has hash-matching full-public WKT artifacts via symlink, "
                "and Goal5314 already ran RTDL exact-witness on the same Goal5310 WKT hashes against the "
                "paper-config author denominator. Re-running the 873s-class exact route would not change the "
                "evidence boundary."
            ),
        },
        "input_artifact_reuse": {
            "goal5426_reuse_gate_passed": bool(goal5426["resource_decision"]["existing_artifact_reuse_gate_passed"]),
            "goal5426_generation_safety_gate_passed": bool(goal5426["resource_decision"]["generation_safety_gate_passed"]),
            "waterbodies_goal5426_path": goal5426["remote_probe"]["parsed"]["files"]["waterbodies"]["goal5426_path"],
            "blockgroups_goal5426_path": goal5426["remote_probe"]["parsed"]["files"]["blockgroups"]["goal5426_path"],
            "waterbodies_sha256": goal5426["remote_probe"]["parsed"]["files"]["waterbodies"]["actual_sha256"],
            "blockgroups_sha256": goal5426["remote_probe"]["parsed"]["files"]["blockgroups"]["actual_sha256"],
        },
        "author_denominator": {
            "selected": "goal5314_paper_config_n_points_cell_8",
            "hd_result": float(paper_author["hd_result"]),
            "num_points_cell": int(paper_author["num_points_per_cell"]),
            "matches_paper_log": bool(paper_author["matches_paper_log"]),
            "avg_time_ms": float(paper_author["avg_time_ms"]),
            "grid_resolution": paper_author["grid_resolution"],
            "iterations": int(paper_author["iterations"]),
        },
        "default_author_denominator_kept_as_config_sensitivity": {
            "goal5311_default_author_hd_result": float(goal5311["author_result"]["hd_result"]),
            "goal5311_paper_value_matched": bool(goal5311["decision"]["paper_value_matched"]),
            "goal5314_default_author_hd_result": float(default_author["hd_result"]),
            "num_points_cell": int(default_author["num_points_per_cell"]),
            "reason": "Default n_points_cell=15 does not match the paper log and must not be used as the paper denominator.",
        },
        "rtdl_evidence": {
            "route": "existing_goal5314_exact_witness",
            "hd_result_float64": float(rtdl_exact["hd_result_float64"]),
            "abs_diff_vs_author_paper_config": diff,
            "declared_tolerance": tolerance_value,
            "matched_with_declared_tolerance": diff <= tolerance_value,
            "per_source_witness_exact": bool(rtdl_exact["per_source_witness_exact"]),
            "route_sec": float(rtdl_exact["route_sec"]),
            "entrypoint_total_sec": float(rtdl_exact["entrypoint_total_sec"]),
            "same_witness_float32_distance": float(tolerance["same_witness_float32_distance"]),
            "distance_float32_matches_paper_log": bool(tolerance["exact_float32_match"]),
        },
        "decision": {
            "full_public_water_bg_level_b_scalar_match_confirmed": matched,
            "rerun_required_now": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "performance_ratio_claimed": False,
        },
        "claim_boundary": {
            "full_public_level_b_scalar_match_claimed": matched,
            "existing_evidence_consolidation_only": True,
            "new_execution_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "geo_figure5_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "author_rt_core_equivalence_claimed": False,
            "route_micro_optimization_goal_authorized": False,
            "explicit_lb_reopened": False,
        },
        "source_artifacts": {
            "goal5426": str(GOAL5426),
            "goal5314": str(GOAL5314),
            "goal5311": str(GOAL5311),
        },
        "next_recommended_goal": "Goal5428_update_level_b_matrix_with_goal5427_water_bg_paper_config_row",
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"matched": payload["matched"], "status": payload["status"]}, sort_keys=True))
    return 0 if payload["matched"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
