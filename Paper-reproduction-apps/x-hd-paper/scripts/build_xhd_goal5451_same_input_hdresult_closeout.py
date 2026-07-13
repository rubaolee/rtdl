#!/usr/bin/env python3
"""Build the Goal5451 X-HD same-input directed-HDResult closeout packet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP / "results"
OUT = RESULTS / "xhd_goal5451_same_input_hdresult_closeout.json"
REVIEW = (
    ROOT
    / "history"
    / "internal_docs"
    / "review_goal5451_xhd_same_input_hdresult_closeout_verified_2026-07-10.md"
)


def _load(name: str) -> dict[str, Any]:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def _rel(name: str) -> str:
    return str((RESULTS / name).relative_to(ROOT)).replace("\\", "/")


def _graphics_rows(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    primary: list[dict[str, Any]] = []
    scalar_only: list[dict[str, Any]] = []
    for row in payload["rows"]:
        exact = next(route for route in row["rtdl_routes"] if route["route_label"] == "cell-mbr-exact-witness")
        fast = next(route for route in row["rtdl_routes"] if route["route_label"] == "cell-mbr-fast-scalar")
        primary.append(
            {
                "case_id": row["case_id"],
                "category": "graphics_3d",
                "same_input_author_and_rtdl": True,
                "input_identity_level": row["input_identity_level"],
                "point_counts": row["point_counts"],
                "author_hd_result": row["author"]["hd_result"],
                "rtdl_hd_result": exact["rtdl"]["hd_result"],
                "abs_diff": exact["abs_diff_vs_author_rerun"],
                "tolerance": payload["tolerance"],
                "matched": exact["matched_author_rerun"],
                "route": exact["route_label"],
                "directed_contract": "input1_to_input2",
                "per_source_witness_exact": exact["rtdl"]["per_source_witness_exact"],
            }
        )
        scalar_only.append(
            {
                "case_id": row["case_id"],
                "route": fast["route_label"],
                "author_hd_result": row["author"]["hd_result"],
                "rtdl_hd_result": fast["rtdl"]["hd_result"],
                "abs_diff": fast["abs_diff_vs_author_rerun"],
                "tolerance": payload["tolerance"],
                "matched": fast["matched_author_rerun"],
                "per_source_witness_exact": fast["rtdl"]["per_source_witness_exact"],
                "claim": "directed scalar HDResult only",
            }
        )
    return primary, scalar_only


def build_payload() -> dict[str, Any]:
    directed_author = _load("directed2d_asymmetric_author_gate_summary_pod.json")
    directed_rtdl = _load("directed2d_asymmetric_rtdl_route_gate_summary.json")
    graphics = _load("xhd_goal5419_figure5_level_b_same_pod_graphics_matrix.json")
    bounded_geo = _load("xhd_goal5422_bounded_geo_same_pod_packet_execution.json")
    full_public_geo = _load("xhd_goal5427_water_bg_paper_config_consolidation.json")
    performance = _load("xhd_goal5217_level_b_same_pod_performance_matrix_2026-07-09.json")

    if directed_author["author_comparison_reference"] != "directed_a_to_b":
        raise ValueError("author directed contract is not input1-to-input2")
    if directed_author["author_hd_result"] == directed_author["rtdl_reference"]["hausdorff"]:
        raise ValueError("directed discriminator no longer distinguishes directed from symmetric Hausdorff")
    if not (directed_author["matched"] and directed_rtdl["matched"]):
        raise ValueError("directed discriminator gate is not matched")

    graphics_primary, graphics_scalar_only = _graphics_rows(graphics)
    geo_primary = []
    for row in bounded_geo["rows"]:
        geo_primary.append(
            {
                "case_id": row["case_id"],
                "category": "geo_2d_bounded",
                "same_input_author_and_rtdl": True,
                "input_identity_level": row["input_identity_level"],
                "point_counts": row["point_counts"],
                "author_hd_result": row["author"]["HDResult"],
                "rtdl_hd_result": row["rtdl"]["HDResult"],
                "abs_diff": row["comparison"]["abs_diff"],
                "tolerance": row["comparison"]["tolerance"],
                "matched": row["comparison"]["matched"],
                "route": row["rtdl"]["route"],
                "directed_contract": row["comparison"]["comparison_reference"],
                "per_source_witness_exact": row["rtdl"]["per_source_witness_exact"],
            }
        )

    full_geo = {
        "case_id": "water_bg_full_public_paper_config",
        "category": "geo_2d_full_public",
        "same_input_author_and_rtdl": True,
        "input_identity_level": "level_b_full_public_same_source_geo_not_exact_file_hash",
        "point_counts": [22824823, 52271467],
        "author_hd_result": full_public_geo["author_denominator"]["hd_result"],
        "rtdl_hd_result": full_public_geo["rtdl_evidence"]["hd_result_float64"],
        "abs_diff": full_public_geo["rtdl_evidence"]["abs_diff_vs_author_paper_config"],
        "tolerance": full_public_geo["rtdl_evidence"]["declared_tolerance"],
        "matched": full_public_geo["rtdl_evidence"]["matched_with_declared_tolerance"],
        "route": full_public_geo["rtdl_evidence"]["route"],
        "directed_contract": "input1_to_input2",
        "per_source_witness_exact": full_public_geo["rtdl_evidence"]["per_source_witness_exact"],
    }

    directed_case = {
        "case_id": "directed2d_asymmetric",
        "category": "definition_discriminator_2d",
        "same_input_author_and_rtdl": True,
        "input_identity_level": "bounded_checked_in_fixture",
        "point_counts": [directed_author["point_count_a"], directed_author["point_count_b"]],
        "author_hd_result": directed_author["author_hd_result"],
        "rtdl_hd_result": directed_rtdl["rtdl_route"]["directed_a_to_b"]["distance"],
        "abs_diff": directed_rtdl["author_abs_diff"],
        "tolerance": directed_rtdl["tolerance"],
        "matched": directed_rtdl["matched"],
        "route": directed_rtdl["rtdl_route"]["route"],
        "directed_contract": "input1_to_input2",
        "reverse_directed_hd_result": directed_author["rtdl_reference"]["directed_b_to_a"],
        "symmetric_hd_result": directed_author["rtdl_reference"]["hausdorff"],
        "per_source_witness_exact": True,
    }

    cases = [directed_case, *graphics_primary, *geo_primary, full_geo]
    if not all(row["same_input_author_and_rtdl"] and row["matched"] for row in cases):
        raise ValueError("same-input HDResult closeout contains an unmatched primary case")
    if not all(row["abs_diff"] <= row["tolerance"] for row in cases):
        raise ValueError("same-input HDResult closeout contains an out-of-tolerance primary case")

    author_perf = performance["author_repeats"]
    rtdl_fresh = performance["rtdl_fresh_repeats"]
    rtdl_warm = performance["rtdl_explicit_warm_repeats"]
    review_text = REVIEW.read_text(encoding="utf-8") if REVIEW.is_file() else ""
    review_approved = "approve_goal5451_xhd_same_input_directed_hdresult_closeout" in review_text
    status = (
        "xhd_same_input_directed_hdresult_reproduction_complete__externally_reviewed_and_approved"
        if review_approved
        else "xhd_same_input_directed_hdresult_reproduction_complete__review_pending"
    )

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5451.same_input_hdresult_closeout.v1",
        "goal": "Goal5451",
        "date": "2026-07-10",
        "status": status,
        "owner_acceptance_criterion": (
            "For the same input files, RTDL/Python/partner and author C++/CUDA/OptiX hd_exec produce the "
            "same directed input1-to-input2 HDResult within the declared tolerance."
        ),
        "directed_definition_gate": {
            "author_comparison_reference": directed_author["author_comparison_reference"],
            "author_hd_result": directed_author["author_hd_result"],
            "rtdl_hd_result": directed_rtdl["rtdl_route"]["directed_a_to_b"]["distance"],
            "reverse_directed_hd_result": directed_author["rtdl_reference"]["directed_b_to_a"],
            "symmetric_hd_result": directed_author["rtdl_reference"]["hausdorff"],
            "distinguishes_directed_from_symmetric": True,
            "matched": True,
        },
        "evidence_matrix": {
            "primary_case_count": len(cases),
            "primary_matched_case_count": sum(bool(row["matched"]) for row in cases),
            "additional_scalar_only_route_count": len(graphics_scalar_only),
            "additional_scalar_only_matched_count": sum(bool(row["matched"]) for row in graphics_scalar_only),
            "categories": sorted({row["category"] for row in cases}),
            "primary_cases": cases,
            "additional_fast_scalar_routes": graphics_scalar_only,
        },
        "performance_appendix": {
            "workload": "public Stanford Dragon to HappyBuddha, same POD, same input pair",
            "author_process_wall_sec_median": author_perf["process_wall_sec"]["median"],
            "author_internal_running_avg_time_ms_median": author_perf["running_avg_time_ms"]["median"],
            "rtdl_fresh_route_wall_sec_median": rtdl_fresh["route_wall_sec"]["median"],
            "rtdl_fresh_total_including_load_sec_median": rtdl_fresh["full_total_including_load_sec"]["median"],
            "rtdl_explicit_warm_route_sec_median": rtdl_warm["measured_route_wall_sec"]["median"],
            "rtdl_explicit_warm_full_total_including_load_warmup_and_measured_sec_median": rtdl_warm[
                "full_total_including_load_warmup_and_measured_sec"
            ]["median"],
            "fresh_scalar_hdresult_matched": rtdl_fresh["all_matched"],
            "fresh_per_source_witness_exact": all(rtdl_fresh["per_source_witness_exact_values"]),
            "performance_ratio_authorized": False,
            "why_no_ratio": performance["denominator_alignment"]["reason"],
            "warm_is_diagnostic_only": True,
        },
        "system_value": {
            "hausdorff_is_an_app_composition": True,
            "generic_rtdl_assets": [
                "pairwise L2 candidate rows",
                "nearest witness reduction",
                "max-nearest scalar reduction",
                "generic grid/cell-MBR descriptors and nearest frontier execution",
                "partner-facing 2D directed max-of-nearest route",
            ],
            "non_xhd_consumer_proof": "Goal5128 facility-service-radius / worst-served-demand consumer",
            "xhd_specific_core_primitive_added": False,
        },
        "claim_boundary": {
            "same_input_directed_hdresult_reproduction_complete": True,
            "exact_original_paper_artifacts_recovered": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "all_paper_figures_reproduced": False,
            "author_internal_worklist_or_row_hash_parity_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "performance_parity_or_speedup_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "new_route_optimization_authorized": False,
            "new_public_artifact_search_authorized": False,
        },
        "source_artifacts": {
            "directed_author_gate": _rel("directed2d_asymmetric_author_gate_summary_pod.json"),
            "directed_rtdl_gate": _rel("directed2d_asymmetric_rtdl_route_gate_summary.json"),
            "graphics_same_pod_matrix": _rel("xhd_goal5419_figure5_level_b_same_pod_graphics_matrix.json"),
            "bounded_geo_same_pod_matrix": _rel("xhd_goal5422_bounded_geo_same_pod_packet_execution.json"),
            "full_public_geo_consolidation": _rel("xhd_goal5427_water_bg_paper_config_consolidation.json"),
            "performance_regime_matrix": _rel("xhd_goal5217_level_b_same_pod_performance_matrix_2026-07-09.json"),
            "external_review": str(REVIEW.relative_to(ROOT)).replace("\\", "/") if review_approved else None,
        },
        "review_status": {
            "external_review_present": REVIEW.is_file(),
            "external_review_approved": review_approved,
            "verdict_label": (
                "approve_goal5451_xhd_same_input_directed_hdresult_closeout" if review_approved else None
            ),
        },
        "allowed_summary": (
            "X-HD same-input directed-HDResult reproduction is complete for the current owner-approved scope: "
            "the tested author hd_exec and RTDL routes agree on directed input1-to-input2 HDResult within tolerance."
        ),
        "forbidden_summaries": [
            "the original paper datasets were recovered",
            "all X-HD paper figures were reproduced",
            "RTDL reproduces the author's internal RT-core algorithm or worklists",
            "RTDL performance parity or speedup against the author is proven",
            "fast-scalar per-source witnesses are exact",
        ],
        "next_action": (
            "stop the current X-HD implementation line; no more route tuning or artifact search is required"
            if review_approved
            else "strict external review of this scoped closeout; no more X-HD route tuning is required"
        ),
        "exit_label": status,
    }


def main() -> int:
    payload = build_payload()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "primary_case_count": payload["evidence_matrix"]["primary_case_count"],
                "primary_matched_case_count": payload["evidence_matrix"]["primary_matched_case_count"],
                "performance_ratio_authorized": payload["performance_appendix"]["performance_ratio_authorized"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
