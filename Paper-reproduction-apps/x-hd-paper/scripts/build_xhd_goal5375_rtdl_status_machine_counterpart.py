from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5375_rtdl_status_machine_counterpart_assessment.json"

AUTHOR_ORACLE = RESULTS / "xhd_goal5374_author_lb_status_trace_oracle.json"
GOAL5371 = RESULTS / "xhd_goal5371_inline_global_bound_lb_probe.json"
GOAL5368 = RESULTS / "xhd_goal5368_cell_mbr_raw_kind_count_telemetry.json"
GOAL5365 = RESULTS / "xhd_goal5365_rtdl_lb_counterpart_gate.json"
GOAL5373 = RESULTS / "xhd_goal5373_rtdl_status_machine_telemetry_surface.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _candidate(
    *,
    name: str,
    row_count: int,
    active_in_queue_size: int,
    status_init_count: int,
    status_offloading_count: int,
    status_aborted_count: int | None,
    cmax2_mbr_abort_count: int | None,
    point_loop_early_break_count: int | None,
    miss_queue_count: int | None,
    current_best_state_source: str,
    source_artifact: Path,
    author_rows: int,
    author_width_bytes: int,
) -> dict[str, Any]:
    author_width = row_count * 2 * 4
    return {
        "name": name,
        "source_artifact": str(source_artifact),
        "active_in_queue_size": int(active_in_queue_size),
        "raw_offload_rows_before_sort_reduce": int(row_count),
        "raw_offload_rows_author_width_bytes": int(author_width),
        "status_count_init": int(status_init_count),
        "status_count_offloading": int(status_offloading_count),
        "status_count_aborted": status_aborted_count,
        "miss_queue_count": miss_queue_count,
        "cmax2_mbr_abort_count": cmax2_mbr_abort_count,
        "point_loop_early_break_count": point_loop_early_break_count,
        "current_best_state_source": current_best_state_source,
        "row_delta_author_minus_rtdl": int(author_rows - row_count),
        "row_ratio_rtdl_div_author": float(row_count / author_rows),
        "author_width_byte_delta_author_minus_rtdl": int(author_width_bytes - author_width),
        "row_count_parity": bool(row_count == author_rows),
        "author_width_byte_parity": bool(author_width == author_width_bytes),
        "required_field_gaps": [
            key
            for key, value in {
                "status_count_aborted": status_aborted_count,
                "miss_queue_count": miss_queue_count,
                "cmax2_mbr_abort_count": cmax2_mbr_abort_count,
                "point_loop_early_break_count": point_loop_early_break_count,
            }.items()
            if value is None
        ],
    }


def build_artifact() -> dict[str, Any]:
    oracle = _read_json(AUTHOR_ORACLE)
    goal5371 = _read_json(GOAL5371)
    goal5368 = _read_json(GOAL5368)
    goal5365 = _read_json(GOAL5365)
    goal5373 = _read_json(GOAL5373)

    author_trace = oracle["author_lb_trace"]
    author_rows = int(author_trace["raw_offload_rows_before_sort_reduce"])
    author_width = int(author_trace["raw_offload_rows_author_width_bytes"])
    active = int(author_trace["active_in_queue_size"])
    status_init = int(author_trace["status_count_init"])

    inline_rows = int(goal5371["comparison"]["rtdl_author_radius_inline_count_only_kind2_rows"])
    inline_global_rows = int(goal5371["comparison"]["rtdl_author_radius_inline_global_bound_kind2_rows"])
    noinline_rows = int(goal5371["comparison"]["rtdl_author_radius_noinline_raw_kind2_rows_from_goal5368"])
    old_lb256_rows = int(
        goal5365["rtdl_counterparts"]["lb256_heavy_offload"]["heavy_offload_peak_rows"]
    )

    candidates = [
        _candidate(
            name="author_radius_inline_kind2_current_surface",
            row_count=inline_rows,
            active_in_queue_size=active,
            status_init_count=status_init,
            status_offloading_count=inline_rows,
            status_aborted_count=None,
            cmax2_mbr_abort_count=None,
            point_loop_early_break_count=0,
            miss_queue_count=None,
            current_best_state_source="rtdl_inline_nearest_payload_not_author_cmin2_restore",
            source_artifact=GOAL5371,
            author_rows=author_rows,
            author_width_bytes=author_width,
        ),
        _candidate(
            name="author_radius_inline_global_bound_kind2_current_surface",
            row_count=inline_global_rows,
            active_in_queue_size=active,
            status_init_count=status_init,
            status_offloading_count=inline_global_rows,
            status_aborted_count=int(
                goal5371["probe_results"]["inline_global_bound_count_only"][
                    "global_bound_early_break_count"
                ]
            ),
            cmax2_mbr_abort_count=None,
            point_loop_early_break_count=int(
                goal5371["probe_results"]["inline_global_bound_count_only"][
                    "global_bound_early_break_count"
                ]
            ),
            miss_queue_count=None,
            current_best_state_source="rtdl_global_bound_not_author_cmax2_status_machine",
            source_artifact=GOAL5371,
            author_rows=author_rows,
            author_width_bytes=author_width,
        ),
        _candidate(
            name="author_radius_noinline_raw_kind2_current_surface",
            row_count=noinline_rows,
            active_in_queue_size=active,
            status_init_count=status_init,
            status_offloading_count=noinline_rows,
            status_aborted_count=None,
            cmax2_mbr_abort_count=None,
            point_loop_early_break_count=None,
            miss_queue_count=None,
            current_best_state_source="none_no_inline_nearest_payload",
            source_artifact=GOAL5368,
            author_rows=author_rows,
            author_width_bytes=author_width,
        ),
        _candidate(
            name="goal5365_full_cover_lb256_behavior_gate_surface",
            row_count=old_lb256_rows,
            active_in_queue_size=active,
            status_init_count=status_init,
            status_offloading_count=old_lb256_rows,
            status_aborted_count=None,
            cmax2_mbr_abort_count=None,
            point_loop_early_break_count=None,
            miss_queue_count=None,
            current_best_state_source="single_pass_full_cover_not_author_iteration_radius",
            source_artifact=GOAL5365,
            author_rows=author_rows,
            author_width_bytes=author_width,
        ),
    ]

    best_by_abs_delta = min(candidates, key=lambda item: abs(int(item["row_delta_author_minus_rtdl"])))
    required_fields = [
        "active_in_queue_size",
        "raw_offload_rows_before_sort_reduce",
        "raw_offload_rows_author_width_bytes",
        "status_count_init",
        "status_count_offloading",
        "status_count_aborted",
        "miss_queue_count",
        "cmax2_mbr_abort_count",
        "point_loop_early_break_count",
        "current_best_state_source",
        "row_count_parity_against_author_offloading_size",
    ]
    return {
        "goal": "Goal5375",
        "date": "2026-07-10",
        "schema": "rtdl.paper_reproduction.xhd.goal5375.rtdl_status_machine_counterpart_assessment.v1",
        "status": "rtdl_status_machine_counterpart_assessed__row_parity_not_established",
        "exit_label": "current_rtdl_surface_fails_author_lb_oracle__need_status_machine_implementation",
        "purpose": (
            "Assess current RTDL lb/offload telemetry surfaces against the Goal5374 "
            "author status-machine oracle before claiming explicit -lb support."
        ),
        "input_artifacts": {
            "author_oracle": str(AUTHOR_ORACLE),
            "goal5371_inline_global_bound_probe": str(GOAL5371),
            "goal5368_raw_kind_count_probe": str(GOAL5368),
            "goal5365_behavior_gate": str(GOAL5365),
            "goal5373_surface_audit": str(GOAL5373),
        },
        "author_oracle": {
            "offloading_size_rows": author_rows,
            "raw_offload_rows_before_sort_reduce": author_rows,
            "raw_offload_rows_author_width_bytes": author_width,
            "active_in_queue_size": active,
            "status_count_init": status_init,
            "status_count_offloading": int(author_trace["status_count_offloading_append"]),
            "status_count_cmax2_mbr_abort": int(author_trace["status_count_cmax2_mbr_abort"]),
            "status_count_point_loop_early_break": int(
                author_trace["status_count_point_loop_early_break"]
            ),
        },
        "required_fields": required_fields,
        "candidate_counterparts": candidates,
        "best_current_candidate": {
            "name": best_by_abs_delta["name"],
            "absolute_row_delta": abs(int(best_by_abs_delta["row_delta_author_minus_rtdl"])),
            "row_ratio_rtdl_div_author": best_by_abs_delta["row_ratio_rtdl_div_author"],
            "row_count_parity": bool(best_by_abs_delta["row_count_parity"]),
        },
        "assessment": {
            "any_candidate_row_count_parity": any(bool(item["row_count_parity"]) for item in candidates),
            "any_candidate_author_width_parity": any(
                bool(item["author_width_byte_parity"]) for item in candidates
            ),
            "rtdl_surface_ready_from_goal5373": bool(
                goal5373["coverage_summary"]["ready_for_author_shader_status_machine_lb_trace"]
            ),
            "minimum_gate_passed": False,
            "missing_or_unproven_semantics": [
                "author cmin2/current-best restoration by in_q_idx",
                "author cmax2 MBR abort status counter",
                "author miss_queue append/count semantics",
                "author loadBalanceProcessing sort/reduce feedback into later state",
                "row-count parity against Goal5374 OffloadingSize",
            ],
        },
        "decision": {
            "explicit_lb_support_authorized": False,
            "next_goal": "implement_or_probe_rtdl_status_machine_mode_against_goal5374_oracle",
            "why": (
                "Current RTDL surfaces can mimic some field shapes, but no current "
                "candidate matches the author raw offload row denominator, and key "
                "author status-machine fields remain missing or only analogs."
            ),
        },
        "claim_boundary": {
            "rtdl_counterpart_assessment_claimed": True,
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
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    payload = build_artifact()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
