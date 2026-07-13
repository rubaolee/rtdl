#!/usr/bin/env python3
"""Build Goal5429 exact-input / exact-equivalence decision refresh."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
GOAL5428 = RESULTS / "xhd_goal5428_level_b_matrix_with_water_bg_full_public.json"
GOAL5324 = RESULTS / "xhd_goal5324_exact_input_acquisition_and_equivalence_decision_packet.json"
OUT = RESULTS / "xhd_goal5429_exact_input_or_equivalence_decision_refresh.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    goal5428 = _load(GOAL5428)
    goal5324 = _load(GOAL5324)
    coverage = goal5428["coverage"]
    source_best = goal5324["current_best_candidate_for_exact_equivalence_review"]
    protocol = goal5324["public_exact_equivalence_review_protocol"]

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5429.exact_input_or_equivalence_decision_refresh.v1",
        "goal": "Goal5429",
        "date": "2026-07-10",
        "status": "exact_input_or_equivalence_decision_refreshed_after_goal5428__no_route_work",
        "purpose": (
            "Refresh the full-paper blocker after the expanded Goal5428 Level-B matrix. "
            "The goal is to decide what can legally move the X-HD line beyond Level-B."
        ),
        "level_b_matrix_status": {
            "source_goal": "Goal5428",
            "matched": bool(goal5428["matched"]),
            "graphics_case_count": int(coverage["graphics_case_count"]),
            "graphics_route_result_count": int(coverage["graphics_route_result_count"]),
            "bounded_geo_case_count": int(coverage["bounded_geo_case_count"]),
            "bounded_geo_route_result_count": int(coverage["bounded_geo_route_result_count"]),
            "full_public_geo_case_count": int(coverage["full_public_geo_case_count"]),
            "full_public_geo_route_result_count": int(coverage["full_public_geo_route_result_count"]),
            "total_case_count": int(coverage["total_case_count"]),
            "total_route_result_count": int(coverage["total_route_result_count"]),
            "strongest_new_row": "geo_water_bg_full_public_paper_config",
        },
        "full_reproduction_decision": {
            "full_reproduction_next_blocker": goal5324["global_decision"]["full_reproduction_next_blocker"],
            "more_route_performance_work_is_next": False,
            "route_micro_optimization_authorized": False,
            "explicit_lb_authorized": False,
            "reason": (
                "Goal5428 makes Level-B scalar evidence broader, but it does not change "
                "the exact-input identity blocker. Full paper progress now requires "
                "author files/hashes, byte-identical regeneration, or an externally "
                "accepted exact-equivalence claim."
            ),
        },
        "current_best_exact_equivalence_candidate": {
            "row_id": source_best["row_id"],
            "why_best": source_best["why_best"],
            "why_not_exact_yet": source_best["why_not_exact_yet"],
            "recommended_decision": source_best["recommended_decision"],
            "goal5428_row_id": "geo_water_bg_full_public_paper_config",
            "evidence_level": "level_b_full_public_same_source_geo_not_exact_file_hash",
        },
        "exact_or_equivalence_requirements": {
            "valid_next_paths": goal5324["global_decision"]["valid_next_paths"],
            "required_before_exact_equivalence_can_be_considered": protocol[
                "required_before_exact_equivalence_can_be_considered"
            ],
            "not_sufficient": protocol["not_sufficient"],
            "allowed_outcomes": protocol["allowed_outcomes"],
        },
        "branch_ranking": [
            {
                "rank": 1,
                "branch": "strict_review_goals5424_5428_packet",
                "requires_pod": False,
                "reason": "The expanded Level-B matrix should be reviewed before using it as a public status baseline.",
            },
            {
                "rank": 2,
                "branch": "author_artifact_or_hash_acquisition",
                "requires_pod": False,
                "reason": "Exact paper status requires input files, hashes, or byte-identical regeneration evidence.",
            },
            {
                "rank": 3,
                "branch": "water_bg_public_reconstruction_exact_equivalence_review_packet",
                "requires_pod": False,
                "reason": "WaterBodies->BlockGroups is the strongest public candidate, but only an explicit external decision can promote the claim beyond Level-B.",
            },
            {
                "rank": 4,
                "branch": "same_input_author_rtdl_gate_after_new_artifacts",
                "requires_pod": True,
                "reason": "POD becomes useful only after new exact artifacts or an accepted reconstruction require verification.",
            },
        ],
        "blocked_or_rejected_paths": [
            {
                "path": "route_micro_optimization",
                "allowed": False,
                "reason": "Goal5428 already has broad Level-B scalar evidence; the blocker is input identity, not route timing.",
            },
            {
                "path": "explicit_lb_or_row_identity_work",
                "allowed": False,
                "reason": "The implementation-artifact parity line remains fail-closed under the stop-loss rule.",
            },
            {
                "path": "water_bg_exact_promotion_by_statistics_only",
                "allowed": False,
                "reason": "Matching point counts, MBRs, and HDResult are not sufficient without file/hash or accepted exact-equivalence evidence.",
            },
            {
                "path": "performance_ratio_from_goal5428",
                "allowed": False,
                "reason": "Author AvgTime, process wall, RTDL route wall, and RTDL total are separate denominators.",
            },
        ],
        "claim_boundary": {
            "decision_refresh_claimed": True,
            "level_b_matrix_current_claimed": True,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "new_pod_execution_claimed": False,
            "new_rtdl_route_code_added": False,
            "explicit_lb_reopened": False,
            "route_micro_optimization_goal_authorized": False,
        },
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": "exact-input / exact-equivalence decision packet; no app-artifact parity implementation",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: this goal keeps app-artifact parity fail-closed and redirects to provenance/equivalence.",
        },
        "pod_usage": {
            "used": False,
            "expected_next": False,
            "reason": "No new input artifact or accepted exact-equivalence claim exists yet; POD execution would not advance the blocker.",
        },
        "recommended_next_goal": "Goal5430_water_bg_exact_equivalence_review_packet_or_author_artifact_request",
        "allowed_summary": (
            "Goal5429 refreshes the post-Level-B decision: after Goal5428 the X-HD matrix has "
            "6 cases and 9 route results, but full paper reproduction is still blocked on exact "
            "input artifacts or explicit exact-equivalence acceptance. The next useful work is "
            "review/provenance/equivalence, not route tuning."
        ),
        "not_allowed": [
            "claiming exact paper dataset recovery",
            "claiming Figure 5 reproduction",
            "claiming full X-HD paper reproduction",
            "claiming author-vs-RTDL performance ratio",
            "claiming public reconstruction is exact from point counts, MBRs, or HDResult alone",
            "reopening explicit -lb or row identity work",
            "starting route micro-optimization as paper-reproduction progress",
        ],
        "source_artifacts": {
            "goal5428": str(GOAL5428),
            "goal5324": str(GOAL5324),
        },
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "recommended_next_goal": payload["recommended_next_goal"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
