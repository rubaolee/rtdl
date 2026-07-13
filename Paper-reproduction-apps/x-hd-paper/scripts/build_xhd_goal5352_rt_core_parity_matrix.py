#!/usr/bin/env python3
"""Build the Goal5352 X-HD RT-core feature parity matrix.

This is an app-owned paper-reproduction artifact.  It does not implement a new
route.  Its job is to turn the author-RT semantics exposed by prior goals into
a concrete same-functionality gap matrix so the next implementation goal targets
the actual X-HD algorithm surface rather than CLI spelling or value-only parity.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"
WRAPPER = APP_ROOT / "scripts" / "run_xhd_rtdl_hd_exec.py"


INPUT_ARTIFACTS = {
    "goal5351_variant_semantics": RESULTS / "xhd_goal5351_author_variant_semantics_audit.json",
    "goal5350_functional_matrix": RESULTS / "xhd_goal5350_functional_parity_matrix_amendment.json",
    "goal5282_offload_mapping": RESULTS / "xhd_goal5282_author_offload_mapping_2026-07-09.json",
    "goal5284_auto_tune_matrix": RESULTS / "xhd_goal5284_figure9_auto_tune_semantics_matrix_2026-07-09.json",
    "goal5292_figure7_load_balance": RESULTS / "xhd_goal5292_figure7_load_balance_audit_2026-07-09.json",
    "goal5288_figure5_timing": RESULTS / "xhd_goal5288_figure5_timing_denominator_audit_2026-07-09.json",
}


AUTHOR_RT_FLAG_PATTERNS = {
    "fast_build_bvh": ("-fast_build_bvh", "--fast-build-bvh", "--fast_build_bvh"),
    "rebuild_bvh": ("-rebuild_bvh", "--rebuild-bvh", "--rebuild_bvh"),
    "eb": ("-eb", "--eb"),
    "prune": ("-prune", "--prune"),
    "lb": ("-lb", "--lb"),
    "n_points_cell": ("-n_points_cell", "--n-points-cell", "--n_points_cell"),
    "tune_grid": ("-tune_grid", "--tune-grid", "--tune_grid"),
    "tune_radius": ("-tune_radius", "--tune-radius", "--tune_radius"),
}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _artifact_summary() -> dict[str, Any]:
    artifacts: dict[str, Any] = {}
    for name, path in INPUT_ARTIFACTS.items():
        payload = _load_json(path)
        artifacts[name] = {
            "path": str(path.relative_to(ROOT)),
            "schema": payload.get("schema"),
            "goal": payload.get("goal"),
            "status": payload.get("status"),
            "exit_label": payload.get("exit_label"),
        }
    return artifacts


def _wrapper_surface() -> dict[str, Any]:
    text = WRAPPER.read_text(encoding="utf-8")
    author_rt_flags = {
        flag: any(pattern in text for pattern in patterns)
        for flag, patterns in AUTHOR_RT_FLAG_PATTERNS.items()
    }
    return {
        "path": str(WRAPPER.relative_to(ROOT)),
        "author_variant_names_supported": ["eb", "nn", "itk", "clover", "rt"],
        "rtdl_route_labels": [
            "auto",
            "public-columnar",
            "cell-mbr-fast-scalar",
            "cell-mbr-exact-witness",
        ],
        "author_rt_option_surface_observed": author_rt_flags,
        "all_author_rt_options_observed": all(author_rt_flags.values()),
        "interpretation": (
            "The wrapper accepts author variant names and RTDL route controls, "
            "but it does not yet expose the author RT option surface for BVH "
            "build/update policy, early-break, prune, load-balance, n_points_cell, "
            "tune_grid, or tune_radius."
        ),
    }


def _feature(
    *,
    key: str,
    author_semantics: str,
    current_rtdl: str,
    same_functionality_status: str,
    blocking_for_full_functionality: bool,
    evidence: list[str],
    next_action: str,
) -> dict[str, Any]:
    return {
        "key": key,
        "author_semantics": author_semantics,
        "current_rtdl": current_rtdl,
        "same_functionality_status": same_functionality_status,
        "blocking_for_full_functionality": blocking_for_full_functionality,
        "evidence": evidence,
        "next_action": next_action,
    }


def build_matrix() -> dict[str, Any]:
    artifacts = _artifact_summary()
    wrapper_surface = _wrapper_surface()
    goal5351 = _load_json(INPUT_ARTIFACTS["goal5351_variant_semantics"])
    rt_row = next(row for row in goal5351["variant_semantics"] if row["author_flag"] == "rt")

    feature_matrix = [
        _feature(
            key="rt_variant_value_surface",
            author_semantics="Author -variant rt selects the X-HD RT implementation.",
            current_rtdl=(
                "RTDL accepts -variant rt and returns directed HDResult through "
                "a selected RTDL route."
            ),
            same_functionality_status="partial_value_route_only",
            blocking_for_full_functionality=True,
            evidence=["Goal5349", "Goal5351", "run_xhd_rtdl_hd_exec.py"],
            next_action=(
                "Keep value compatibility, but do not treat this as author RT-core "
                "algorithm identity."
            ),
        ),
        _feature(
            key="author_rt_option_surface",
            author_semantics=(
                "Author RT supports RT-specific controls such as radius, eb/prune, "
                "lb, n_points_cell, and tune_radius."
            ),
            current_rtdl=wrapper_surface["interpretation"],
            same_functionality_status="not_reproduced",
            blocking_for_full_functionality=True,
            evidence=["Goal5351", "run_xhd_rtdl_hd_exec.py"],
            next_action=(
                "Add an app-owned author RT option-surface gate: either implement "
                "semantics for each flag, map it to a generic RTDL control with "
                "evidence, or fail closed with an explicit unsupported status."
            ),
        ),
        _feature(
            key="uniform_grid_and_cell_mbr_target_structure",
            author_semantics=(
                "Author RT organizes target points into a uniform grid and tight "
                "cell MBRs used as OptiX custom primitives."
            ),
            current_rtdl=(
                "Generic grid/cell descriptors and native cell-MBR traversal exist "
                "and are used by the Level-B route, but exact author grid sizing and "
                "kernel/SBT identity are not claimed."
            ),
            same_functionality_status="partial_generic_route",
            blocking_for_full_functionality=True,
            evidence=["Goals5138-5150", "Goal5216", "Goal5350"],
            next_action=(
                "Keep the generic cell-MBR substrate; compare author grid sizing and "
                "n_points_cell semantics before claiming RT-core equivalence."
            ),
        ),
        _feature(
            key="radius_growth_and_tune_radius",
            author_semantics=(
                "Author RT uses radius-growing iterations and tune_radius / "
                "n_points_cell decisions in the X-HD route."
            ),
            current_rtdl=(
                "RTDL has grid-shape and seed controls, but no proven author-equivalent "
                "radius growth or tune-radius policy."
            ),
            same_functionality_status="not_reproduced",
            blocking_for_full_functionality=True,
            evidence=["Goal5284", "Goal5351"],
            next_action=(
                "Open a focused radius-growth semantics goal: extract author iteration "
                "inputs/counters and decide whether a generic radius schedule API is needed."
            ),
        ),
        _feature(
            key="early_break_prune_scalar_contract",
            author_semantics=(
                "Author EB/prune controls point-level culling and RT pruning behavior."
            ),
            current_rtdl=(
                "RTDL has a generic global-bound early break that preserves exact "
                "directed-HD scalar values but may make per-source witnesses approximate."
            ),
            same_functionality_status="partial_scalar_value_only",
            blocking_for_full_functionality=True,
            evidence=["Goal5211", "Goal5350"],
            next_action=(
                "Separate exact-scalar and exact-witness contracts. Do not use the "
                "fast scalar route as witness parity evidence."
            ),
        ),
        _feature(
            key="load_balance_and_heavy_cell_offload",
            author_semantics=(
                "Author RT uses lb-controlled load balancing and heavy-cell CUDA offload, "
                "with OffloadingSize / RTTime / CUDATime iteration fields."
            ),
            current_rtdl=(
                "RTDL has generic heavy-offload row shape and telemetry, but the "
                "author queue byte denominator and Figure 7 matrix are not aligned."
            ),
            same_functionality_status="partial_shape_and_telemetry_only",
            blocking_for_full_functionality=True,
            evidence=["Goal5279", "Goal5281", "Goal5282", "Goal5292"],
            next_action=(
                "Target a denominator-aligned load-balance/offload gate before any "
                "Figure 7 or heavy-offload performance claim."
            ),
        ),
        _feature(
            key="figure11_memory_fields",
            author_semantics=(
                "Author reports Grid, BVH, MBRs, WL, and WL Heavy Peak memory fields."
            ),
            current_rtdl=(
                "RTDL status-bearing memory accounting exists for selected routes, "
                "but Goal5282 shows WL and WL Heavy Peak denominators are not fully aligned."
            ),
            same_functionality_status="partial_not_same_denominator",
            blocking_for_full_functionality=True,
            evidence=["Goal5273", "Goal5275", "Goal5282"],
            next_action=(
                "Do not claim Figure 11 reproduction until byte denominators and "
                "field semantics are matched or explicitly accepted as different."
            ),
        ),
        _feature(
            key="figure5_author_variant_performance_matrix",
            author_semantics=(
                "Figure 5 compares X-HD with EB, NN-KD, NN-Clover, ITK, and RT-HDIST "
                "baselines over paper workload families."
            ),
            current_rtdl=(
                "RTDL accepts variant names as value requests only; non-rt algorithms "
                "and RT-HDIST external baseline are not reproduced."
            ),
            same_functionality_status="not_reproduced",
            blocking_for_full_functionality=True,
            evidence=["Goal5288", "Goal5351"],
            next_action=(
                "Decide which Figure 5 baselines are external comparisons and which, "
                "if any, RTDL intentionally implements as generic algorithms."
            ),
        ),
        _feature(
            key="exact_paper_input_identity",
            author_semantics=(
                "Full paper reproduction requires exact paper input bytes or accepted "
                "exact-equivalence provenance."
            ),
            current_rtdl=(
                "Current best evidence is Level-B same-source representative; exact "
                "paper input identity remains blocked."
            ),
            same_functionality_status="blocking_gap",
            blocking_for_full_functionality=True,
            evidence=["Goal5345", "Goal5346", "Goal5350"],
            next_action=(
                "Resume exact-input execution only if Goal5345 readiness changes and "
                "a command-ready real artifact packet exists."
            ),
        ),
    ]

    closed = [
        row["key"]
        for row in feature_matrix
        if row["same_functionality_status"] in {"closed", "implemented_and_reviewed"}
    ]
    not_closed = [
        row["key"]
        for row in feature_matrix
        if row["same_functionality_status"] not in {"closed", "implemented_and_reviewed"}
    ]

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5352.rt_core_feature_parity_matrix.v1",
        "goal": "Goal5352",
        "date": "2026-07-09",
        "status": "rt_core_feature_parity_matrix_ready__author_rt_algorithm_parity_not_closed",
        "purpose": (
            "Convert the author X-HD RT-core semantics and existing RTDL evidence "
            "into a concrete same-functionality gap matrix."
        ),
        "input_artifacts": artifacts,
        "author_rt_summary": {
            "author_flag": rt_row["author_flag"],
            "author_impl": rt_row["author_impl"],
            "author_reported_algorithm": rt_row["author_reported_algorithm"],
            "author_algorithm_semantics": rt_row["author_algorithm_semantics"],
            "current_rtdl_status_from_goal5351": rt_row["current_rtdl_status"],
            "algorithm_equivalence_claimed": False,
            "performance_equivalence_claimed": False,
        },
        "current_wrapper_surface": wrapper_surface,
        "feature_matrix": feature_matrix,
        "same_functionality_rollup": {
            "author_rt_core_algorithm_parity_ready": False,
            "full_xhd_paper_reproduction_ready": False,
            "closed_features": closed,
            "not_closed_features": not_closed,
            "blocking_feature_count": sum(
                1 for row in feature_matrix if row["blocking_for_full_functionality"]
            ),
        },
        "recommended_next_targets": [
            {
                "priority": 1,
                "target": "author_rt_option_surface_gate",
                "reason": (
                    "The user-facing author RT flag surface is not reproduced. "
                    "A gate should classify each option as implemented, mapped, "
                    "or fail-closed unsupported."
                ),
            },
            {
                "priority": 2,
                "target": "radius_growth_and_tune_radius_semantics",
                "reason": (
                    "This is central to the author X-HD RT algorithm and Figure 8/9 "
                    "behavior; current RTDL has grid/seed controls but no proven "
                    "author-equivalent policy."
                ),
            },
            {
                "priority": 3,
                "target": "load_balance_heavy_offload_denominator_gate",
                "reason": (
                    "RTDL has generic offload shape and telemetry, but Figure 7/11 "
                    "denominators remain non-aligned."
                ),
            },
        ],
        "claim_boundary": {
            "author_rt_core_algorithm_parity_claimed": False,
            "author_rt_option_surface_complete_claimed": False,
            "figure5_reproduction_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure8_reproduction_claimed": False,
            "figure9_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
        },
        "exit_label": "rt_core_feature_parity_matrix_ready__next_target_author_rt_option_surface",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS / "xhd_goal5352_rt_core_feature_parity_matrix.json",
    )
    args = parser.parse_args()
    payload = build_matrix()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": payload["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
