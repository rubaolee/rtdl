from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5369_lb_queue_state_requirements.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_artifact() -> dict[str, Any]:
    goal5361 = _read_json(RESULTS / "xhd_goal5361_res4full_nonterminal_author_queue_gate.json")
    goal5364 = _read_json(RESULTS / "xhd_goal5364_lb_trace_gate_author_pair_contract.json")
    goal5365 = _read_json(RESULTS / "xhd_goal5365_rtdl_lb_counterpart_gate.json")
    goal5366 = _read_json(RESULTS / "xhd_goal5366_lb_denominator_reconciliation.json")
    goal5367 = _read_json(RESULTS / "xhd_goal5367_lb_author_radius_probe.json")
    goal5368 = _read_json(RESULTS / "xhd_goal5368_cell_mbr_raw_kind_count_telemetry.json")

    author_rows = int(goal5368["comparison"]["author_offloading_size_rows"])
    noinline_kind2 = int(goal5368["comparison"]["rtdl_noinline_raw_kind2_rows"])
    inline_rows = int(goal5367["comparison"]["author_radius_row_count"])
    full_cover_rows = int(goal5367["comparison"]["full_cover_row_count"])
    author_radius = float(goal5367["author_reference"]["iteration_radius"])
    raw_kind2_ratio = noinline_kind2 / author_rows
    inline_ratio = inline_rows / author_rows
    full_cover_ratio = full_cover_rows / author_rows

    return {
        "goal": "Goal5369",
        "date": "2026-07-09",
        "schema": "rtdl.paper_reproduction.xhd.goal5369.lb_queue_state_requirements.v1",
        "status": "lb_queue_state_requirements_ready__implementation_requires_queue_state_reconstruction_or_author_instrumentation",
        "exit_label": "lb_queue_state_requirements_ready__no_explicit_lb_support_yet",
        "purpose": (
            "Convert the Goal5364-5368 load-balance evidence into an executable "
            "requirements gate for the next author-queue-aligned RTDL lb trace. "
            "This goal does not implement explicit -lb support."
        ),
        "input_scope": {
            "level": "level_b_temporary_input_dragon_to_asian_dragon",
            "input1": goal5367["author_reference"]["input_scope"]["input1"],
            "input1_num_points": int(goal5367["author_reference"]["input_scope"]["input1_num_points"]),
            "input2": goal5367["author_reference"]["input_scope"]["input2"],
            "input2_num_points": int(goal5367["author_reference"]["input_scope"]["input2_num_points"]),
            "preprocessing": ["translate_each_input_to_min_bound"],
            "exact_paper_dataset_identity_proven": False,
        },
        "evidence_summary": {
            "author_like_queue_rows_available_from_goal5361": {
                "status": goal5361["status"],
                "matched": bool(goal5361["comparison"]["matched"]),
                "row_mismatch_count": int(goal5361["comparison"]["row_comparison"]["mismatch_count"]),
                "route_iteration_model": goal5361["route"]["route_iteration_model"],
                "covers_fields": [
                    "Iteration",
                    "NumInputPoints",
                    "NumOutputPoints",
                    "Radius",
                    "CMax2",
                ],
                "does_not_cover_fields": [
                    "OffloadingSize",
                    "raw offloading queue rows",
                    "per-source current-best/cmin2 vector",
                ],
            },
            "author_lb256_reference": {
                "hd_result": float(goal5367["author_reference"]["hd_result"]),
                "lb": int(goal5367["author_reference"]["lb"]),
                "radius": author_radius,
                "offloading_size_rows": author_rows,
                "wl_heavy_peak_bytes": int(goal5367["author_reference"]["wl_heavy_peak_bytes"]),
                "num_input_points": int(goal5367["author_reference"]["iteration_num_input_points"]),
            },
            "rtdl_lb_behavior_from_goal5365": {
                "matched_behavior_gate": bool(goal5365["comparison"]["matched"]),
                "lb0_zero_offload": bool(goal5365["comparison"]["lb0_behavior_zero_offload"]),
                "lb256_positive_offload": bool(goal5365["comparison"]["lb256_behavior_positive_offload"]),
                "row_count_or_byte_parity_claimed": bool(goal5365["comparison"]["row_count_or_byte_parity_claimed"]),
            },
            "denominator_shape_from_goal5366": {
                "author_denominator": goal5366["denominator_interpretation"]["author_denominator"],
                "rtdl_denominator": goal5366["denominator_interpretation"]["rtdl_denominator"],
                "formula_denominator_aligned": bool(
                    goal5366["quantitative_reconciliation"]["formula_denominator_aligned"]
                ),
                "route_regime_aligned": bool(goal5366["quantitative_reconciliation"]["route_regime_aligned"]),
                "row_count_parity": bool(goal5366["quantitative_reconciliation"]["row_count_parity"]),
            },
            "scalar_radius_probe_from_goal5367": {
                "radius_aligned": bool(goal5367["comparison"]["radius_aligned"]),
                "explicit_radius_matches_author_value": bool(
                    goal5367["comparison"]["explicit_radius_matches_author_value"]
                ),
                "author_radius_closes_denominator_gap": bool(
                    goal5367["comparison"]["author_radius_closes_denominator_gap"]
                ),
                "author_radius_rtdl_rows": inline_rows,
                "author_radius_rtdl_div_author": inline_ratio,
                "full_cover_rtdl_rows": full_cover_rows,
                "full_cover_rtdl_div_author": full_cover_ratio,
            },
            "raw_kind_count_from_goal5368": {
                "raw_kind2_rows": noinline_kind2,
                "raw_kind2_div_author": raw_kind2_ratio,
                "raw_kind2_greater_than_author": bool(
                    goal5368["comparison"]["noinline_raw_kind2_greater_than_author"]
                ),
                "overflow_telemetry_only": bool(goal5368["telemetry"]["overflow_telemetry_only"]),
                "frontier_row_capacity": int(goal5368["telemetry"]["frontier_row_capacity"]),
            },
        },
        "rejected_hypotheses": [
            {
                "hypothesis": "byte formula mismatch explains the memory gap",
                "rejected_by": "Goal5366 shows the author-width formula shape is aligned.",
            },
            {
                "hypothesis": "scalar radius mismatch alone explains OffloadingSize",
                "rejected_by": "Goal5367 matches author radius but gets 21,006,960 rows, not 27,133,990.",
            },
            {
                "hypothesis": "author OffloadingSize equals all materialized RTDL heavy/offload rows",
                "rejected_by": "Goal5365/5367 materialized rows are 24,508,120 / 21,006,960, not 27,133,990.",
            },
            {
                "hypothesis": "author OffloadingSize equals all raw same-radius kind2 rows",
                "rejected_by": "Goal5368 raw no-inline kind2 rows are 304,981,889, about 11.24x author.",
            },
        ],
        "required_runtime_state_for_next_gate": [
            {
                "name": "active_in_queue_indices",
                "required": True,
                "current_status": "missing_for_lb_trace",
                "why": "Author offload rows append in_q_idx, so RTDL must know the same active queue index space.",
            },
            {
                "name": "per_source_current_best_or_cmin2",
                "required": True,
                "current_status": "missing_for_lb_trace",
                "why": "The author shader prunes against current best state; raw kind2 rows without this state overcount by ~11.24x.",
            },
            {
                "name": "per_iteration_radius_schedule",
                "required": True,
                "current_status": "partially_available",
                "why": "Goal5361 shows radius queue rows can be reproduced for tune-radius fields, but lb OffloadingSize still needs the same queue state.",
            },
            {
                "name": "raw_offload_row_shape",
                "required": True,
                "current_status": "source_semantics_available_runtime_rows_missing",
                "why": "Goal5366 identifies author rows as (in_queue_idx, cell_id); RTDL must emit or count that denominator directly.",
            },
            {
                "name": "author_width_memory_view",
                "required": True,
                "current_status": "formula_available",
                "why": "Figure 11 style memory comparison must use OffloadingSize * 2 * sizeof(uint32_t), not RTDL generic uint64 rows.",
            },
        ],
        "missing_author_runtime_state": [
            "per-source cmin2/current-best vector for iteration 3",
            "active in_queue_idx vector for iteration 3",
            "raw author offloading rows before sort/reduce",
            "per-batch offloading_size contributions inside iteration 3",
        ],
        "next_gate_contract": {
            "name": "author_queue_aligned_lb_trace",
            "implementation_options": [
                "Reconstruct the RTDL queue/current-best state through prior iterations, then run count-only raw offload telemetry under that state.",
                "Instrument/regenerate author to expose the missing runtime queue/current-best arrays and raw offload rows, then compare RTDL against them.",
            ],
            "minimum_acceptance_criteria": {
                "same_input_pair": True,
                "same_preprocessing": True,
                "same_lb_threshold": 256,
                "same_iteration_radius": author_radius,
                "active_queue_size_matches_author_num_input_points": int(
                    goal5364["author_pair"]["lb_256"]["iteration_3"]["NumInputPoints"]
                ),
                "author_offloading_size_rows": author_rows,
                "must_report": [
                    "active_in_queue_size",
                    "current_best_state_source",
                    "raw_offload_rows_before_sort_reduce",
                    "author_width_bytes",
                    "row_count_parity",
                ],
            },
            "success_exit_label": "author_queue_aligned_lb_trace_denominator_compared",
            "failure_exit_label": "lb_trace_blocked_until_queue_state_or_author_instrumentation_available",
        },
        "claim_boundary": {
            "requirements_gate_claimed": True,
            "generic_system_requirement_claimed": True,
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
        "input_artifacts": {
            "goal5361": str(RESULTS / "xhd_goal5361_res4full_nonterminal_author_queue_gate.json"),
            "goal5364": str(RESULTS / "xhd_goal5364_lb_trace_gate_author_pair_contract.json"),
            "goal5365": str(RESULTS / "xhd_goal5365_rtdl_lb_counterpart_gate.json"),
            "goal5366": str(RESULTS / "xhd_goal5366_lb_denominator_reconciliation.json"),
            "goal5367": str(RESULTS / "xhd_goal5367_lb_author_radius_probe.json"),
            "goal5368": str(RESULTS / "xhd_goal5368_cell_mbr_raw_kind_count_telemetry.json"),
        },
    }


def main() -> None:
    artifact = build_artifact()
    OUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, sort_keys=True))


if __name__ == "__main__":
    main()
