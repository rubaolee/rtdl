#!/usr/bin/env python3
"""Build Goal5363 X-HD lb / heavy-cell offload semantics audit evidence."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"

AUTHOR_SOURCE_CANDIDATES = [
    Path(os.environ.get("TEMP", "")) / "xhd-author-src",
    ROOT / ".codex_tmp" / "xhd_author_repo",
]

PRIOR_ARTIFACTS = {
    "rt_core_feature_matrix": RESULTS / "xhd_goal5352_rt_core_feature_parity_matrix.json",
    "figure7_load_balance_audit": RESULTS / "xhd_goal5292_figure7_load_balance_audit_2026-07-09.json",
    "generic_heavy_offload_worklist": RESULTS / "xhd_goal5279_generic_heavy_offload_worklist_reference_2026-07-09.json",
    "native_heavy_offload_telemetry": RESULTS / "xhd_goal5281_native_heavy_offload_telemetry_pod_2026-07-09.json",
    "author_offload_mapping": RESULTS / "xhd_goal5282_author_offload_mapping_2026-07-09.json",
    "figure11_disposition": RESULTS / "xhd_goal5283_figure11_disposition_2026-07-09.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_author_source_root() -> Path:
    for candidate in AUTHOR_SOURCE_CANDIDATES:
        if (candidate / "src" / "hd_impl" / "hausdorff_distance_rt.h").exists():
            return candidate
    searched = [str(path) for path in AUTHOR_SOURCE_CANDIDATES]
    raise FileNotFoundError(f"Could not locate pinned X-HD author source. Searched: {searched}")


def _line_hits(path: Path, patterns: dict[str, str]) -> dict[str, dict[str, Any]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    hits: dict[str, dict[str, Any]] = {}
    for key, pattern in patterns.items():
        regex = re.compile(pattern)
        for number, text in enumerate(lines, start=1):
            if regex.search(text):
                hits[key] = {
                    "file": str(path),
                    "line": number,
                    "text": text.strip(),
                }
                break
        else:
            hits[key] = {
                "file": str(path),
                "line": None,
                "text": None,
            }
    return hits


def _author_lb_semantics(author_root: Path) -> dict[str, Any]:
    rt_h = author_root / "src" / "hd_impl" / "hausdorff_distance_rt.h"
    launch_h = author_root / "src" / "rt" / "launch_parameters.h"
    shader_cu = author_root / "src" / "rt" / "shaders" / "shaders_nn_uniform_grid.cu"
    main_cpp = author_root / "src" / "main.cpp"
    flags_h = author_root / "src" / "flags.h"

    rt_hits = _line_hits(
        rt_h,
        {
            "default_lb": r"int lb = 2 \* MAX_BLOCK_SIZE",
            "wl_formula": r"2 \* n_points_a \* sizeof\(uint32_t\)",
            "processing_threshold_from_config": r"uint32_t processing_threshold = config_\.lb",
            "lb_zero_disabled": r"processing_threshold == 0",
            "lb_zero_sets_uint32_max": r"std::numeric_limits<uint32_t>::max",
            "large_cell_rule": r"return np > processing_threshold",
            "offloading_cap_formula": r"ceil\(n_points_a \* n_large_cells \* 0\.01\)",
            "offloading_bytes_formula": r"offloading_cap \* 2 \* sizeof\(uint32_t\)",
            "set_processing_threshold_param": r"params\.processing_threshold = processing_threshold",
            "read_offloading_size": r"auto offloading_size = offloading_point_ids_\.size",
            "wl_heavy_peak_formula": r"offloading_size \* 2 \*\s*$",
            "total_offloading_size": r"total_offloading_size \+= offloading_size",
            "load_balance_processing_call": r"loadBalanceProcessing",
            "json_rt_time": r'json_iter\["RTTime"\] = rt_time',
            "json_offloading_size": r'json_iter\["OffloadingSize"\] = total_offloading_size',
            "json_cuda_time": r'json_iter\["CUDATime"\] = cuda_time',
            "json_wl_heavy_peak": r'mem\["WL Heavy Peak"\] = wl_heavy_peak_bytes',
            "sort_offload_by_point": r"sort_by_key\(.*offloading_point_ids",
            "reduce_offload_by_point": r"reduce_by_key\(.*offloading_point_ids",
        },
    )
    launch_hits = _line_hits(
        launch_h,
        {
            "in_queue": r"ArrayView<uint32_t> in_queue",
            "miss_queue": r"dev::Queue<uint32_t> miss_queue",
            "processing_threshold_field": r"uint32_t processing_threshold",
            "cmin2_field": r"coord_t\* cmin2",
            "offloading_point_ids": r"dev::Queue<uint32_t> offloading_point_ids",
            "offloading_cell_ids": r"uint32_t\* offloading_cell_ids",
        },
    )
    shader_hits = _line_hits(
        shader_cu,
        {
            "shader_offload_rule": r"np_in_cell > params\.processing_threshold",
            "append_offload_point": r"params\.offloading_point_ids\.Append\(in_q_idx\)",
            "write_offload_cell": r"params\.offloading_cell_ids\[tail\] = mbr_id",
            "offloading_status": r"kOffloading",
            "append_miss_queue": r"params\.miss_queue\.Append\(point_id_a\)",
        },
    )
    main_hits = _line_hits(main_cpp, {"config_lb": r"config\.lb = FLAGS_lb"})
    flag_hits = _line_hits(flags_h, {"declare_lb": r"DECLARE_int32\(lb\)"})

    required = [
        *rt_hits.values(),
        *launch_hits.values(),
        *shader_hits.values(),
        *main_hits.values(),
        *flag_hits.values(),
    ]
    all_found = all(item["line"] is not None for item in required)

    return {
        "source_root": str(author_root),
        "all_required_source_evidence_found": all_found,
        "lb_option_plumbing": {
            "flag_declared": flag_hits["declare_lb"],
            "main_assigns_config_lb": main_hits["config_lb"],
            "processing_threshold_from_config_lb": rt_hits["processing_threshold_from_config"],
        },
        "semantic_rules": {
            "lb_zero_disables_offload_by_uint32_max_threshold": {
                "status": "identified",
                "evidence": [
                    rt_hits["lb_zero_disabled"],
                    rt_hits["lb_zero_sets_uint32_max"],
                ],
                "interpretation": (
                    "Author lb=0 does not mean threshold zero; it is rewritten to "
                    "UINT32_MAX, effectively disabling heavy-cell offload."
                ),
            },
            "lb_n_offloads_cells_with_point_count_greater_than_n": {
                "status": "identified",
                "evidence": [
                    rt_hits["large_cell_rule"],
                    shader_hits["shader_offload_rule"],
                ],
                "interpretation": (
                    "Author lb=N maps to processing_threshold=N; a cell is offloaded "
                    "when its point count is strictly greater than N."
                ),
            },
            "offload_row_shape": {
                "status": "identified",
                "evidence": [
                    launch_hits["offloading_point_ids"],
                    launch_hits["offloading_cell_ids"],
                    shader_hits["append_offload_point"],
                    shader_hits["write_offload_cell"],
                ],
                "interpretation": (
                    "Author offload rows are pairs of in-queue index and cell id. "
                    "CUDA offload processing later groups rows by point."
                ),
            },
        },
        "iteration_and_memory_fields": {
            "iteration_fields": {
                "RTTime": rt_hits["json_rt_time"],
                "OffloadingSize": rt_hits["json_offloading_size"],
                "CUDATime": rt_hits["json_cuda_time"],
            },
            "memory_fields": {
                "WL": rt_hits["wl_formula"],
                "WL Heavy Peak": rt_hits["json_wl_heavy_peak"],
                "WL Heavy Peak formula": rt_hits["wl_heavy_peak_formula"],
            },
            "denominators": {
                "WL": "2 * n_points_a * sizeof(uint32_t)",
                "WL Heavy Peak": "max(OffloadingSize * 2 * sizeof(uint32_t))",
            },
        },
        "cuda_offload_stage": {
            "call": rt_hits["load_balance_processing_call"],
            "sort_by_point": rt_hits["sort_offload_by_point"],
            "reduce_by_point": rt_hits["reduce_offload_by_point"],
            "uses_cmin2_for_offload_pruning": launch_hits["cmin2_field"],
        },
    }


def _prior_status() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, path in PRIOR_ARTIFACTS.items():
        record: dict[str, Any] = {
            "path": str(path),
            "exists": path.exists(),
        }
        if path.exists():
            payload = _load_json(path)
            record["schema"] = payload.get("schema")
            record["status"] = payload.get("status")
            record["exit_label"] = payload.get("exit_label")
            record["matched"] = payload.get("matched")
            if key == "figure7_load_balance_audit":
                record["figure7_reproduced"] = payload.get("figure7_reproduced")
                record["lb_comparison_numeric_matrix_available"] = payload.get(
                    "lb_comparison_numeric_matrix_available"
                )
                record["run_all_lb0_counterpart_available"] = payload.get(
                    "run_all_lb0_counterpart_available"
                )
            if key == "author_offload_mapping":
                mapping = payload.get("author_offload_mapping", {})
                denominator = mapping.get("denominator_alignment", {})
                record["same_denominator_author_figure11"] = denominator.get(
                    "same_denominator_author_figure11"
                )
                record["offloading_size_row_count_shape_available"] = denominator.get(
                    "offloading_size_row_count_shape_available"
                )
            if key == "native_heavy_offload_telemetry":
                for field in ("heavy_offload_peak_rows", "heavy_offload_queue_peak_bytes"):
                    if field in payload:
                        record[field] = payload[field]
                native_memory = payload.get("native_memory", {})
                for field in ("heavy_offload_peak_rows", "heavy_offload_queue_peak_bytes"):
                    if field in native_memory:
                        record[field] = native_memory[field]
        out[key] = record
    return out


def build_artifact() -> dict[str, Any]:
    author_root = _find_author_source_root()
    author = _author_lb_semantics(author_root)
    priors = _prior_status()

    shape_aligned = (
        author["semantic_rules"]["lb_n_offloads_cells_with_point_count_greater_than_n"]["status"]
        == "identified"
    )
    rtdl_generic_threshold_rule = "cell_point_count > max_inline_points"
    author_threshold_rule = "cell_point_count > lb"
    offload_mapping = priors["author_offload_mapping"]
    figure7 = priors["figure7_load_balance_audit"]

    same_denominator = bool(offload_mapping.get("same_denominator_author_figure11") is True)
    figure7_matrix_available = bool(figure7.get("lb_comparison_numeric_matrix_available") is True)

    lb_option_supported_now = False
    next_gate = {
        "name": "bounded_lb_processing_threshold_route_trace_gate",
        "purpose": (
            "Only after this gate may the app-owned hd_exec wrapper accept explicit "
            "-lb for a narrow route. The gate must compare lb=0 versus lb=N behavior "
            "against author trace fields and must preserve denominator labels."
        ),
        "minimum_requirements": [
            "Run or reconstruct an author trace with lb=0 and a matching lb=N trace on the same bounded input.",
            "Show lb=0 disables heavy offload and lb=N creates OffloadingSize rows when heavy cells exist.",
            "Map author processing_threshold to a generic RTDL threshold only when the RTDL route emits equivalent offload row semantics.",
            "Report RTTime, CUDATime, OffloadingSize, WL, and WL Heavy Peak with explicit denominator status.",
            "Keep unsupported author RT options fail-closed; do not claim Figure 7/11 or performance parity.",
        ],
        "candidate_rtdl_control": {
            "name": "max_inline_points",
            "rtdl_rule": rtdl_generic_threshold_rule,
            "author_rule": author_threshold_rule,
            "semantic_shape_aligned": bool(shape_aligned),
            "authorized_as_lb_mapping_now": False,
            "reason_not_authorized": (
                "The threshold rule shape matches, but no author lb=0/lb=N route "
                "trace gate has proven behavior, and Figure 7/11 byte denominators "
                "remain non-aligned."
            ),
        },
    }

    matched = bool(
        author["all_required_source_evidence_found"]
        and shape_aligned
        and not lb_option_supported_now
        and not same_denominator
        and not figure7_matrix_available
    )
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5363.lb_heavy_offload_semantics_audit.v1",
        "goal": "Goal5363",
        "date": "2026-07-09",
        "status": (
            "lb_heavy_offload_semantics_audit_ready__lb_option_still_unsupported"
            if matched
            else "lb_heavy_offload_semantics_audit_incomplete"
        ),
        "purpose": (
            "Audit author X-HD lb / heavy-cell offload semantics and existing "
            "RTDL generic heavy-offload assets before accepting any explicit -lb "
            "author option or making Figure 7/11 claims."
        ),
        "author_lb_semantics": author,
        "existing_rtdl_assets": {
            "prior_artifacts": priors,
            "generic_assets_summary": {
                "nearest_state_frontier_threshold_rule": rtdl_generic_threshold_rule,
                "heavy_offload_worklist_exists": bool(priors["generic_heavy_offload_worklist"]["exists"]),
                "native_heavy_offload_telemetry_exists": bool(
                    priors["native_heavy_offload_telemetry"]["exists"]
                ),
                "author_offload_shape_mapping_exists": bool(priors["author_offload_mapping"]["exists"]),
                "figure7_lb0_lbN_matrix_available": figure7_matrix_available,
                "figure11_same_denominator_available": same_denominator,
            },
        },
        "semantic_mapping_decision": {
            "lb_option_supported_now": lb_option_supported_now,
            "accepted_explicit_author_lb_values": [],
            "candidate_mapping_shape": {
                "author_lb_rule": author_threshold_rule,
                "rtdl_generic_threshold_rule": rtdl_generic_threshold_rule,
                "shape_aligned": bool(shape_aligned),
            },
            "reason": (
                "RTDL has generic offload shape and telemetry, and the threshold "
                "rule shape aligns with author lb. However, explicit -lb changes "
                "author RT execution and author fields; no bounded author lb=0/lb=N "
                "trace gate or same-denominator Figure 7/11 evidence is available."
            ),
            "next_gate": next_gate,
            "exit_label": "lb_heavy_offload_semantics_audit_ready__next_gate_bounded_lb_trace",
        },
        "claim_boundary": {
            "explicit_lb_support_claimed": False,
            "author_rt_option_surface_complete_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "same_denominator_memory_claimed": False,
            "performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "comparison": {
            "matched": matched,
            "author_source_evidence_complete": author["all_required_source_evidence_found"],
            "threshold_rule_shape_aligned": bool(shape_aligned),
            "lb_option_supported_now": lb_option_supported_now,
            "figure7_lb0_lbN_matrix_available": figure7_matrix_available,
            "figure11_same_denominator_available": same_denominator,
        },
        "exit_label": "lb_heavy_offload_semantics_audit_ready__next_gate_bounded_lb_trace",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS / "xhd_goal5363_lb_heavy_offload_semantics_audit.json",
    )
    args = parser.parse_args()
    payload = build_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": payload["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
