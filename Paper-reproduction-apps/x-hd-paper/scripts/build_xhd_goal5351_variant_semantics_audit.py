#!/usr/bin/env python3
"""Build the Goal5351 X-HD author variant semantics audit.

This is an app-owned paper-reproduction audit.  It maps the author's hd_exec
variant flags and Figure-5 script labels to the current RTDL support surface.
It intentionally does not execute author code or RTDL code, and it does not
claim author algorithm or performance equivalence for non-rt variants.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


DEFAULT_OUTPUT = Path(
    "Paper-reproduction-apps/x-hd-paper/results/"
    "xhd_goal5351_author_variant_semantics_audit.json"
)

AUTHOR_COMMIT = "7bf41c8442d059c94f4178355c6d5a10571d9658"
PAPER_BRANCH_COMMIT = "8c3846866052e1e8755210021f23fac2cbe8c3d6"


SOURCE_EXPECTATIONS = {
    "src/main.cpp": [
        'variant == "eb"',
        "Variant::kEarlyBreak",
        'variant == "rt"',
        "Variant::kRT",
        'variant == "nn"',
        "Variant::kNearestNeighborSearch",
        'variant == "clover"',
        "Variant::kClover",
        'variant == "itk"',
        "Variant::kITK",
        'variant == "compare-methods"',
        "Variant::kCompareMethods",
    ],
    "src/run_hausdorff_distance.cu": [
        "case Variant::kEarlyBreak",
        "HausdorffDistanceEarlyBreak",
        "case Variant::kRT",
        "HausdorffDistanceRT",
        "case Variant::kITK",
        "HausdorffDistanceITK",
        "case Variant::kNearestNeighborSearch",
        "HausdorffDistanceNearestNeighborSearch",
        "case Variant::kClover",
        "HausdorffDistanceClover",
    ],
    "src/hd_impl/hausdorff_distance_early_break.h": [
        'stats["Algorithm"] = "Early Break"',
        "ComparedPairs",
    ],
    "src/hd_impl/hausdorff_distance_nearest_neighbor_search.h": [
        'stats["Algorithm"] = "Nearest Neighbor Search"',
        "cukd::buildTree",
        "cukd::cct::fcp",
    ],
    "src/hd_impl/hausdorff_distance_clover.h": [
        'stats["Algorithm"] = "Clover"',
        "bitonic_hubs::C_and_Q",
    ],
    "src/hd_impl/hausdorff_distance_itk.h": [
        'stats["Algorithm"] = "ITK"',
        "itk::DirectedHausdorffDistanceImageFilter",
    ],
    "src/hd_impl/hausdorff_distance_rt.h": [
        'stats["Algorithm"] = "XHD"',
        "LargeCells",
        "OffloadingSize",
        "config_.prune",
        "config_.eb",
        "processing_threshold",
    ],
    "expr/run_fig5.sh": [
        "for variant in eb nn clover rt",
        '"itk" "cpu"',
    ],
    "expr/draw_end2end.py": [
        "MRI_VARIANTS",
        "GEO_VARIANTS",
        "GRAPHICS_VARIANTS",
        "RT-HDIST",
        "X-HD",
        "NN-KD",
        "NN-Clover",
    ],
}


def _verify_source_root(author_source_root: Path | None) -> dict[str, Any]:
    if author_source_root is None:
        return {
            "checked": False,
            "status": "not_checked__no_author_source_root_supplied",
            "missing_files": [],
            "missing_snippets": {},
        }

    missing_files: list[str] = []
    missing_snippets: dict[str, list[str]] = {}
    for rel_path, snippets in SOURCE_EXPECTATIONS.items():
        path = author_source_root / rel_path
        if not path.exists():
            missing_files.append(rel_path)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        missing = [snippet for snippet in snippets if snippet not in text]
        if missing:
            missing_snippets[rel_path] = missing

    ok = not missing_files and not missing_snippets
    return {
        "checked": True,
        "status": "source_expectations_matched" if ok else "source_expectations_failed",
        "author_source_root": str(author_source_root),
        "missing_files": missing_files,
        "missing_snippets": missing_snippets,
    }


def _variant_rows() -> list[dict[str, Any]]:
    return [
        {
            "author_flag": "eb",
            "author_enum": "Variant::kEarlyBreak",
            "author_impl": "HausdorffDistanceEarlyBreak",
            "author_reported_algorithm": "Early Break",
            "author_algorithm_semantics": [
                "Directed Hausdorff value by brute-force nearest search with global cmax early break.",
                "CPU path shuffles both input point arrays and uses host threads.",
                "GPU path shuffles device arrays and uses a block-reduce kernel with early termination when local min <= global cmax.",
            ],
            "figure5_label": "EB",
            "paper_role": "Figure 5 baseline and pruning/early-break comparison component.",
            "current_rtdl_status": "value_compatible_only",
            "rtdl_current_behavior": "RTDL accepts -variant eb and returns directed HDResult through the selected generic RTDL route.",
            "algorithm_equivalence_claimed": False,
            "performance_equivalence_claimed": False,
            "gap_to_close_for_full_parity": [
                "Reproduce author EB execution semantics, including shuffle/seed behavior, early-break update contract, and CPU/GPU denominator fields.",
                "Or explicitly classify EB as an external baseline that RTDL reports but does not reproduce algorithmically.",
            ],
        },
        {
            "author_flag": "nn",
            "author_enum": "Variant::kNearestNeighborSearch",
            "author_impl": "HausdorffDistanceNearestNeighborSearch",
            "author_reported_algorithm": "Nearest Neighbor Search",
            "author_algorithm_semantics": [
                "Directed Hausdorff value by building a nearest-neighbor index over input2 and reducing max nearest distance over input1.",
                "CPU path uses the author's KDTree wrapper.",
                "GPU path uses cuKD buildTree and fcp nearest point query.",
            ],
            "figure5_label": "NN-KD",
            "paper_role": "Figure 5 baseline; Figure 11 memory baseline.",
            "current_rtdl_status": "value_compatible_only",
            "rtdl_current_behavior": "RTDL accepts -variant nn and returns directed HDResult through the selected generic RTDL route.",
            "algorithm_equivalence_claimed": False,
            "performance_equivalence_claimed": False,
            "gap_to_close_for_full_parity": [
                "Implement or map an RTDL generic KD-tree / cuKD-equivalent nearest-neighbor route with matched timing fields.",
                "Or carry NN-KD as an external author baseline, not a reproduced RTDL algorithm.",
            ],
        },
        {
            "author_flag": "clover",
            "author_enum": "Variant::kClover",
            "author_impl": "HausdorffDistanceClover",
            "author_reported_algorithm": "Clover",
            "author_algorithm_semantics": [
                "Directed Hausdorff value through the included Clover bitonic-hubs C_and_Q k=1 query.",
                "2-D inputs are lifted to 3-D with z=0 before Clover execution.",
                "The implementation is GPU-oriented and records Clover memory/time fields.",
            ],
            "figure5_label": "NN-Clover",
            "paper_role": "Figure 5 and Figure 11 baseline.",
            "current_rtdl_status": "value_compatible_only",
            "rtdl_current_behavior": "RTDL accepts -variant clover and returns directed HDResult through the selected generic RTDL route.",
            "algorithm_equivalence_claimed": False,
            "performance_equivalence_claimed": False,
            "gap_to_close_for_full_parity": [
                "Implement or wrap an equivalent generic Clover/bitonic-hubs nearest-neighbor baseline.",
                "Or carry NN-Clover as an external author baseline, not a reproduced RTDL algorithm.",
            ],
        },
        {
            "author_flag": "itk",
            "author_enum": "Variant::kITK",
            "author_impl": "HausdorffDistanceITK",
            "author_reported_algorithm": "ITK",
            "author_algorithm_semantics": [
                "Directed Hausdorff value via itk::DirectedHausdorffDistanceImageFilter.",
                "Meaningful for image inputs with known ITK image sizes.",
                "CPU path records ITK ReportedTime; it is not the X-HD RT algorithm.",
            ],
            "figure5_label": "ITK",
            "paper_role": "MRI / image baseline in Figure 5.",
            "current_rtdl_status": "value_compatible_only",
            "rtdl_current_behavior": "RTDL accepts -variant itk and returns directed HDResult through the selected generic RTDL route, but does not reproduce ITK image-filter semantics.",
            "algorithm_equivalence_claimed": False,
            "performance_equivalence_claimed": False,
            "gap_to_close_for_full_parity": [
                "Either implement/wrap an ITK-directed Hausdorff baseline for image inputs, or classify ITK as an external baseline.",
                "Clarify image voxelization/index semantics before any MRI Figure 5 reproduction claim.",
            ],
        },
        {
            "author_flag": "rt",
            "author_enum": "Variant::kRT",
            "author_impl": "HausdorffDistanceRT",
            "author_reported_algorithm": "XHD",
            "author_algorithm_semantics": [
                "X-HD ray-tracing route over uniform-grid tight cell MBRs.",
                "Uses radius-growing iterations, OptiX custom primitives, early-break and prune flags, load-balance threshold lb, and heavy-cell offload queues.",
                "Records Grid/BVH/MBRs/WL/WL Heavy Peak memory and iteration RTTime/CUDATime/OffloadingSize.",
            ],
            "figure5_label": "X-HD",
            "paper_role": "Main paper algorithm.",
            "current_rtdl_status": "partial_level_b_value_route",
            "rtdl_current_behavior": "RTDL has generic cell-MBR / native OptiX routes that match Level-B directed HD values and an hd_exec-compatible exact-witness route on reviewed representative artifacts, but it does not claim author RT-core algorithm identity.",
            "algorithm_equivalence_claimed": False,
            "performance_equivalence_claimed": False,
            "gap_to_close_for_full_parity": [
                "Align or explicitly differ from author radius-growth / tune-radius policy.",
                "Align or explicitly differ from author LB / heavy-cell offload behavior.",
                "Align memory and iteration counters if Figure 7/11 are in scope.",
                "Acquire exact inputs or accepted exact-equivalence before full-paper claims.",
            ],
        },
    ]


def build_audit(*, author_source_root: Path | None = None, date: str = "2026-07-09") -> dict[str, Any]:
    source_verification = _verify_source_root(author_source_root)
    variant_rows = _variant_rows()
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5351.author_variant_semantics_audit.v1",
        "goal": "Goal5351",
        "date": date,
        "status": "author_variant_semantics_audit_ready__algorithm_parity_not_closed",
        "purpose": (
            "Map author hd_exec variants and Figure-5 labels to implementation semantics and "
            "current RTDL support, so variant-name acceptance cannot be mistaken for "
            "author algorithm or performance reproduction."
        ),
        "author_provenance": {
            "repository": "https://github.com/pwrliang/X-HD.git",
            "main_commit": AUTHOR_COMMIT,
            "paper_branch_commit": PAPER_BRANCH_COMMIT,
            "source_verification": source_verification,
        },
        "author_cli_surface": {
            "documented_readme_variants": ["eb", "nn", "itk", "rt"],
            "flags_help_variants": ["eb", "rt", "nn", "itk"],
            "main_cpp_variants": ["compare-methods", "eb", "rt", "nn", "clover", "itk"],
            "supported_goal5349_rtdl_value_surface": ["eb", "nn", "itk", "clover", "rt"],
            "compare_methods_status": (
                "Parser maps compare-methods to Variant::kCompareMethods, but "
                "RunHausdorffDistanceImpl has no switch case for it; not treated as a "
                "supported hd_exec paper variant surface."
            ),
        },
        "figure5_script_surface": {
            "mri_variants": ["itk_cpu", "rt_hdist", "nn_gpu", "clover_gpu", "eb_gpu", "rt_gpu"],
            "mri_labels": ["ITK", "RT-HDIST", "NN-KD", "NN-Clover", "EB", "X-HD"],
            "geo_variants": ["nn_gpu", "clover_gpu", "eb_gpu", "rt_gpu"],
            "geo_labels": ["NN-KD", "NN-Clover", "EB", "X-HD"],
            "graphics_variants": ["rt_hdist", "nn_gpu", "clover_gpu", "eb_gpu", "rt_gpu"],
            "graphics_labels": ["RT-HDIST", "NN-KD", "NN-Clover", "EB", "X-HD"],
            "external_baselines_not_hd_exec_variants": [
                {
                    "label": "RT-HDIST",
                    "status": "external_script_baseline_not_reproduced_by_rtdl",
                    "note": "Figure scripts load RT-HDIST timing from separate logs rather than from hd_exec -variant rt/eb/nn/clover/itk.",
                }
            ],
        },
        "variant_semantics": variant_rows,
        "current_rtdl_parity_summary": {
            "value_surface": {
                "status": "all_author_variant_names_accepted_for_directed_hdresult_value_output",
                "source": "Goal5349",
                "scope": "bounded / supported inputs through app-owned RTDL hd_exec-compatible runner",
            },
            "algorithm_surface": {
                "full_author_variant_algorithm_parity_ready": False,
                "closed": [],
                "partial": ["rt value route on Level-B representative artifacts"],
                "not_closed": ["eb", "nn", "clover", "itk", "RT-HDIST external baseline"],
            },
            "performance_surface": {
                "author_variant_performance_parity_ready": False,
                "reason": "RTDL does not reproduce non-rt algorithm denominators, and author/RTDL timing denominators are not aligned.",
            },
        },
        "recommended_next_actions": [
            {
                "action": "decide_external_baseline_policy",
                "details": "Classify ITK, NN-KD, NN-Clover, EB, and RT-HDIST as external baselines unless RTDL intentionally implements algorithm-equivalent routes.",
            },
            {
                "action": "target_rt_algorithm_gap",
                "details": "For the main X-HD algorithm, focus on radius-growth, LB/heavy-cell offload, and Figure 7/11 counters rather than variant flag plumbing.",
            },
            {
                "action": "avoid_false_figure5_completion",
                "details": "Do not claim Figure 5 baseline reproduction from Goal5349 value-compatible variant acceptance.",
            },
        ],
        "claim_boundary": {
            "full_xhd_paper_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "author_variant_algorithm_equivalence_claimed": False,
            "author_variant_performance_parity_claimed": False,
            "rtdl_accepts_all_author_variant_names_as_algorithm_equivalent": False,
            "rt_hdist_reproduced": False,
        },
        "exit_label": "author_variant_semantics_audit_ready__non_rt_algorithm_parity_not_closed",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build X-HD Goal5351 author variant semantics audit.")
    parser.add_argument("--author-source-root", default=None)
    parser.add_argument("--date", default="2026-07-09")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    root = Path(args.author_source_root) if args.author_source_root else None
    artifact = build_audit(author_source_root=root, date=args.date)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(out),
                "status": artifact["status"],
                "source_verification_status": artifact["author_provenance"]["source_verification"]["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
