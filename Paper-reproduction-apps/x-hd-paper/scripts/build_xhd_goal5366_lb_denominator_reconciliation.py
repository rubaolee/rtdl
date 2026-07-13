#!/usr/bin/env python3
"""Build Goal5366 lb/offload denominator reconciliation evidence."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"

GOAL5363 = RESULTS / "xhd_goal5363_lb_heavy_offload_semantics_audit.json"
GOAL5365 = RESULTS / "xhd_goal5365_rtdl_lb_counterpart_gate.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _candidate_author_roots() -> list[Path]:
    roots: list[Path] = []
    env_root = os.environ.get("XHD_AUTHOR_SRC")
    if env_root:
        roots.append(Path(env_root))
    roots.append(Path(os.environ.get("TEMP", "")) / "xhd-author-src")
    roots.append(Path("/tmp/xhd-author-src"))
    return roots


def _resolve_author_root() -> Path | None:
    for root in _candidate_author_roots():
        if (root / "src" / "hd_impl" / "hausdorff_distance_rt.h").exists():
            return root
    return None


def _line_evidence(path: Path, needle: str) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for idx, line in enumerate(lines, start=1):
        if needle in line:
            return {"file": str(path), "line": idx, "text": line.strip()}
    raise RuntimeError(f"missing source evidence {needle!r} in {path}")


def _rtdl_line_evidence(needle: str) -> dict[str, Any]:
    path = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
    return _line_evidence(path, needle)


def build_artifact() -> dict[str, Any]:
    goal5363 = _load_json(GOAL5363)
    goal5365 = _load_json(GOAL5365)
    author_lb256 = goal5365["author_pair"]["lb_256"]
    rtdl_lb256 = goal5365["rtdl_counterparts"]["lb256_heavy_offload"]
    rtdl_phase = rtdl_lb256["frontier_native_phase_timings"]

    author_rows = int(author_lb256["iteration_3"]["OffloadingSize"])
    author_bytes = int(author_lb256["memory"]["WL Heavy Peak"])
    rtdl_rows = int(rtdl_lb256["heavy_offload_peak_rows"])
    rtdl_author_width_bytes = int(rtdl_lb256["heavy_offload_queue_peak_bytes_author_u32_equivalent"])
    rtdl_generic_bytes = int(rtdl_lb256["heavy_offload_queue_peak_bytes_generic_u64"])
    row_delta = author_rows - rtdl_rows
    author_width_byte_delta = author_bytes - rtdl_author_width_bytes

    author_root = _resolve_author_root()
    author_source_available = author_root is not None
    author_evidence: dict[str, Any] = {}
    if author_root is not None:
        rt_h = author_root / "src" / "hd_impl" / "hausdorff_distance_rt.h"
        shader = author_root / "src" / "rt" / "shaders" / "shaders_nn_uniform_grid.cu"
        author_evidence = {
            "offload_append_point_id": _line_evidence(shader, "params.offloading_point_ids.Append(in_q_idx)"),
            "offload_append_cell_id": _line_evidence(shader, "params.offloading_cell_ids[tail] = mbr_id"),
            "offload_size_read": _line_evidence(rt_h, "auto offloading_size = offloading_point_ids_.size(stream);"),
            "wl_heavy_peak_formula": _line_evidence(rt_h, "offloading_size * 2 *"),
            "total_offloading_size_accumulates_batches": _line_evidence(rt_h, "total_offloading_size += offloading_size;"),
            "json_offloading_size": _line_evidence(rt_h, 'json_iter["OffloadingSize"] = total_offloading_size;'),
            "load_balance_sort_by_point": _line_evidence(rt_h, "thrust::sort_by_key"),
            "load_balance_reduce_by_point": _line_evidence(rt_h, "thrust::reduce_by_key"),
            "author_radius_field": _line_evidence(rt_h, 'json_iter["Radius"] = radius;'),
        }

    rtdl_evidence = {
        "kind_threshold": _rtdl_line_evidence("cell.point_count > params.max_inline_points"),
        "kind_two_payload": _rtdl_line_evidence("optixSetPayload_6(2u);"),
        "row_sort": _rtdl_line_evidence(
            "std::sort(rows.begin(), rows.end(), [](const RtdlCellMbrFrontierRow& a"
        ),
        "row_unique": _rtdl_line_evidence(
            "rows.erase(std::unique(rows.begin(), rows.end(), [](const RtdlCellMbrFrontierRow& a"
        ),
        "offload_row_counter": _rtdl_line_evidence("if (row.frontier_kind_code == 2)"),
        "generic_uint64_byte_formula": _rtdl_line_evidence("offload_row_count * 2ULL * static_cast<uint64_t>(sizeof(uint64_t))"),
    }

    attempted = int(rtdl_phase["attempted_count"])
    emitted = int(rtdl_phase["emitted_count"])
    raw_equals_emitted = attempted == emitted == rtdl_rows
    author_byte_formula_holds = author_bytes == author_rows * 2 * 4
    rtdl_author_width_formula_holds = rtdl_author_width_bytes == rtdl_rows * 2 * 4
    rtdl_generic_formula_holds = rtdl_generic_bytes == rtdl_rows * 2 * 8
    denominator_formula_aligned = (
        author_byte_formula_holds and rtdl_author_width_formula_holds
    )
    row_count_parity = author_rows == rtdl_rows
    byte_parity_author_width = author_bytes == rtdl_author_width_bytes

    author_radius = float(author_lb256["iteration_3"]["Radius"])
    rtdl_radius = float(rtdl_lb256["frontier_native_phase_timings"]["mode_bits"] * 0 + goal5365["rtdl_counterparts"]["lb256_heavy_offload"].get("radius", 0.0))
    # Goal5365's summarized lb256 payload does not retain radius; recover it from the raw artifact.
    raw_lb256_path = Path(goal5365["input_artifacts"]["rtdl_lb256"])
    raw_lb256 = _load_json(raw_lb256_path)
    directed = raw_lb256["rtdl_route"]["directed_a_to_b"]
    rtdl_radius = float(directed["radius"])

    regime_aligned = False
    status = (
        "lb_denominator_reconciliation_ready__row_count_parity_not_established"
        if not row_count_parity
        else "lb_denominator_reconciliation_ready__row_count_parity_observed"
    )

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5366.lb_denominator_reconciliation.v1",
        "goal": "Goal5366",
        "date": "2026-07-09",
        "status": status,
        "purpose": (
            "Reconcile the author OffloadingSize / WL Heavy Peak denominator "
            "with RTDL generic heavy-offload telemetry before accepting explicit "
            "-lb support or making Figure 7/11 claims."
        ),
        "input_artifacts": {
            "goal5363_lb_semantics_audit": str(GOAL5363),
            "goal5365_rtdl_lb_counterpart_gate": str(GOAL5365),
            "rtdl_lb256_raw_summary": str(raw_lb256_path),
        },
        "source_evidence": {
            "author_source_available": author_source_available,
            "author_root": None if author_root is None else str(author_root),
            "author": author_evidence,
            "rtdl": rtdl_evidence,
        },
        "quantitative_reconciliation": {
            "author": {
                "lb": int(author_lb256["lb"]),
                "offloading_size_rows": author_rows,
                "wl_heavy_peak_bytes": author_bytes,
                "bytes_formula": "OffloadingSize * 2 * sizeof(uint32_t)",
                "bytes_formula_holds": author_byte_formula_holds,
                "radius": author_radius,
                "num_input_points": int(author_lb256["iteration_3"]["NumInputPoints"]),
                "iteration_field": "iteration_3",
            },
            "rtdl": {
                "max_inline_points": int(rtdl_lb256["max_inline_points"]),
                "heavy_offload_peak_rows": rtdl_rows,
                "author_width_candidate_bytes": rtdl_author_width_bytes,
                "generic_uint64_queue_peak_bytes": rtdl_generic_bytes,
                "author_width_formula": "heavy_offload_peak_rows * 2 * sizeof(uint32_t)",
                "generic_formula": "heavy_offload_peak_rows * 2 * sizeof(uint64_t)",
                "author_width_formula_holds": rtdl_author_width_formula_holds,
                "generic_formula_holds": rtdl_generic_formula_holds,
                "raw_attempted_count": attempted,
                "emitted_count_after_native_sort_unique": emitted,
                "raw_attempted_equals_emitted_equals_offload_rows": raw_equals_emitted,
                "radius": rtdl_radius,
            },
            "deltas": {
                "row_delta_author_minus_rtdl": row_delta,
                "row_ratio_rtdl_div_author": rtdl_rows / author_rows,
                "author_width_byte_delta_author_minus_rtdl": author_width_byte_delta,
                "author_width_byte_ratio_rtdl_div_author": rtdl_author_width_bytes / author_bytes,
            },
            "formula_denominator_aligned": denominator_formula_aligned,
            "row_count_parity": row_count_parity,
            "byte_parity_author_width": byte_parity_author_width,
            "route_regime_aligned": regime_aligned,
        },
        "denominator_interpretation": {
            "author_denominator": (
                "Raw offloading queue rows appended by the author shader as "
                "(in_queue_idx, cell_id), accumulated across batches within the "
                "reported iteration. The CUDA load-balance stage later sorts and "
                "reduces rows by point, but OffloadingSize records the queue size "
                "before that grouped processing."
            ),
            "rtdl_denominator": (
                "Generic cell-MBR frontier rows with frontier_kind_code=2 after "
                "the native collector's row download / sort / unique path. In the "
                "Goal5365 artifact raw attempted_count equals emitted_count and "
                "equals heavy_offload_peak_rows, so the observed delta is not "
                "explained by an RTDL duplicate-collapse delta in that run."
            ),
            "current_mismatch_reason": (
                "The byte formula is shape-aligned under an author-width uint32 "
                "view, but row-count parity is not established because the current "
                "RTDL run is a single-pass full-cover cell-MBR frontier route "
                "while the author field is an iterative radius/in_queue offload "
                "counter. The author iteration radius and RTDL route radius are "
                "different, and RTDL is not yet emitting an author-iteration "
                "offload queue denominator."
            ),
            "support_level": "behavior_level_only",
        },
        "decision": {
            "explicit_lb_support_authorized_now": False,
            "row_count_or_byte_parity_authorized_now": False,
            "reason": (
                "Goal5365 proves value preservation and offload sign behavior, "
                "and Goal5366 shows the byte formulas are compatible. It does "
                "not prove that RTDL and author count the same offload rows."
            ),
            "next_gate": (
                "Build an author-iteration-aligned RTDL lb trace or add raw "
                "author-denominator telemetry to the native collector before "
                "claiming -lb row-count / memory parity."
            ),
        },
        "claim_boundary": {
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "same_denominator_memory_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "rtdl_author_performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "prior_context": {
            "goal5363_threshold_rule_shape_aligned": bool(
                goal5363["comparison"]["threshold_rule_shape_aligned"]
            ),
            "goal5365_behavior_gate_passed": bool(
                goal5365["decision"]["bounded_lb_behavior_gate_passed"]
            ),
        },
        "exit_label": "lb_denominator_reconciled_shape_aligned__row_count_parity_not_established",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS / "xhd_goal5366_lb_denominator_reconciliation.json",
    )
    args = parser.parse_args()
    payload = build_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": payload["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
