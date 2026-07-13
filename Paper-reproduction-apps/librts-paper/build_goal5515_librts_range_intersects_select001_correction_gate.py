from __future__ import annotations

import json
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").is_dir())
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
RESULTS = APP / "results"


def main() -> None:
    current = json.loads(
        (RESULTS / "goal5514_exact_range_intersects_select001_resolution_gate.json").read_text(
            encoding="utf-8"
        )
    )
    expected_current = {
        "parks_Europe_select_0.01_10000": 216977211,
        "dtl_cnty_select_0.01_10000": 1570285,
        "lakes_bz2_select_0.01_10000": 1113229623,
        "USACensusBlockGroupBoundaries_select_0.01_10000": 33404355,
        "USADetailedWaterBodies_select_0.01_10000": 55205607,
    }
    current_by_case = {case["case_id"]: case for case in current["cases"]}
    for case_id, expected_count in expected_current.items():
        case = current_by_case[case_id]
        if not case.get("matched"):
            raise ValueError(f"current case is not matched: {case_id}")
        if case["author"]["result_count"] != expected_count or case["rtdl"]["result_count"] != expected_count:
            raise ValueError(f"current count changed: {case_id}")

    historical = {
        "source_report": "history/internal_docs/goal5500_librts_exact_range_intersects_six_geometry_batch_result_2026-07-12.md",
        "cases": [
            {
                "case_id": "parks_Europe_select_0.01_10000",
                "author_count": 216977211,
                "historical_rtdl_count": 216981002,
                "historical_delta": 3791,
                "current_rtdl_count": 216977211,
                "current_delta": 0,
            },
            {
                "case_id": "lakes_bz2_select_0.01_10000",
                "author_count": 1113229623,
                "historical_rtdl_count": 1113284318,
                "historical_delta": 54695,
                "current_rtdl_count": 1113229623,
                "current_delta": 0,
            },
        ],
        "interpretation": "The two historical count disagreements do not reproduce on the same official query family after the generic indexed-AABB validity correction. This closes the observed mismatch at the evidence level; it does not claim that every possible range-intersects discrepancy has a single proven cause.",
    }
    payload = {
        "schema": "rtdl.paper_reproduction.librts.goal5515_range_intersects_select001_correction.v1",
        "status": "historical_select001_count_mismatches_no_longer_reproduced",
        "operation": "range_intersects",
        "query_family": "range-intersects_select_0.01_queries_10000",
        "current_gate": "Paper-reproduction-apps/librts-paper/results/goal5514_exact_range_intersects_select001_resolution_gate.json",
        "current_case_count": 6,
        "current_match_count": 5,
        "current_author_capacity_failure_count": 1,
        "historical_mismatch_recheck": historical,
        "generic_fix_evidence": {
            "source_gate": "Paper-reproduction-apps/librts-paper/results/goal5508_generic_float32_degenerate_aabb_validity_fix_gate.json",
            "contract": "indexed AABBs that are not strictly valid after float32 packing are non-matchable in the generic OptiX intersection kernel",
            "app_specific_behavior_added": False,
        },
        "claim_boundary": {
            "historical_mismatch_resolution_evidence_only": True,
            "complete_range_intersects_matrix_claimed": False,
            "pointwise_intersection_equivalence_claimed": False,
            "complete_paper_reproduction_claimed": False,
            "figure6_reproduced": False,
            "performance_ratio_authorized": False,
            "author_performance_parity_claimed": False,
            "device_zero_copy_claimed": False,
            "author_specific_rtdl_core_behavior_authorized": False,
            "embree_in_scope": False,
        },
        "not_closed": [
            "the full 42-pair range-intersects inventory",
            "pair-row equality because the author binary exposes counts only",
            "the parks.bz2 author CUDA capacity boundary",
            "Figure 6 and performance comparison",
        ],
    }
    output = RESULTS / "goal5515_range_intersects_select001_correction_gate.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
