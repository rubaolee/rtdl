from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5376_status_machine_candidate_contract.json"

AUTHOR_ORACLE = RESULTS / "xhd_goal5374_author_lb_status_trace_oracle.json"
GOAL5375 = RESULTS / "xhd_goal5375_rtdl_status_machine_counterpart_assessment.json"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
PARTNER_CONTINUATIONS = ROOT / "src" / "rtdsl" / "partner_continuations.py"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _source_window(path: Path, start_token: str, end_token: str | None = None) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.index(start_token)
    end = text.index(end_token, start) if end_token else len(text)
    return text[start:end]


def build_artifact() -> dict[str, Any]:
    author = _read_json(AUTHOR_ORACLE)
    goal5375 = _read_json(GOAL5375)
    runtime_window = _source_window(
        OPTIX_RUNTIME,
        "def collect_cell_mbr_nearest_frontier_3d_optix",
        "@dataclass(frozen=True)",
    )
    partner_window = _source_window(
        PARTNER_CONTINUATIONS,
        "def cell_mbr_nearest_frontier_native_3d_optix_columns",
        "def nearest_witness_from_cell_mbr_frontier_numpy_columns",
    )
    required_runtime_tokens = [
        "status_machine_candidate_telemetry.v1",
        "generic_cell_mbr_frontier_status_machine_candidate",
        "raw_offload_rows_author_width_bytes",
        "explicit_lb_support_claimed",
        "same_denominator_memory_claimed",
        "author cmin2/current-best restoration by in_q_idx",
        "author loadBalanceProcessing sort/reduce feedback into later state",
    ]
    required_partner_tokens = [
        '"status_machine_telemetry_collected"',
        '"status_machine_telemetry"',
    ]
    runtime_contract_present = all(token in runtime_window for token in required_runtime_tokens)
    partner_passthrough_present = all(token in partner_window for token in required_partner_tokens)

    author_trace = author["author_lb_trace"]
    best = goal5375["best_current_candidate"]
    implemented_fields = {
        "active_in_queue_size": "generic query_count for the current launch",
        "raw_offload_rows_before_sort_reduce": "native raw_frontier_kind2_rows",
        "raw_offload_rows_author_width_bytes": "raw kind2 rows * 2 uint32 fields",
        "status_count_init": "generic query_count for the current launch",
        "status_count_offloading": "native raw_frontier_kind2_rows",
        "point_loop_early_break_count": "RTDL global-bound early-break analog when enabled",
        "current_best_state_source": "RTDL current_best arrays / inline payload provenance label",
    }
    still_missing_or_analog = [
        "author cmin2/current-best restoration by in_q_idx",
        "author cmax2 MBR abort status counter",
        "author miss_queue append/count semantics",
        "author loadBalanceProcessing sort/reduce feedback into later state",
        "row-count parity against Goal5374 OffloadingSize",
    ]
    return {
        "goal": "Goal5376",
        "date": "2026-07-10",
        "schema": "rtdl.paper_reproduction.xhd.goal5376.status_machine_candidate_contract.v1",
        "status": (
            "rtdl_status_machine_candidate_contract_implemented__"
            "author_lb_row_parity_not_established"
        ),
        "exit_label": "status_machine_candidate_surface_ready__real_author_lb_mode_still_required",
        "purpose": (
            "Expose current RTDL cell-MBR frontier status-shaped telemetry as a "
            "generic, app-neutral contract so X-HD can compare it against the "
            "Goal5374 author -lb oracle without claiming explicit -lb support."
        ),
        "source_contract": {
            "runtime_contract_present": runtime_contract_present,
            "partner_passthrough_present": partner_passthrough_present,
            "required_runtime_tokens": required_runtime_tokens,
            "required_partner_tokens": required_partner_tokens,
            "optix_runtime": str(OPTIX_RUNTIME),
            "partner_continuations": str(PARTNER_CONTINUATIONS),
        },
        "implemented_status_candidate_fields": implemented_fields,
        "author_oracle": {
            "active_in_queue_size": int(author_trace["active_in_queue_size"]),
            "offloading_size_rows": int(author_trace["raw_offload_rows_before_sort_reduce"]),
            "raw_offload_rows_author_width_bytes": int(
                author_trace["raw_offload_rows_author_width_bytes"]
            ),
            "status_count_init": int(author_trace["status_count_init"]),
            "status_count_offloading": int(author_trace["status_count_offloading_append"]),
            "status_count_cmax2_mbr_abort": int(author_trace["status_count_cmax2_mbr_abort"]),
            "status_count_point_loop_early_break": int(
                author_trace["status_count_point_loop_early_break"]
            ),
        },
        "comparison_to_goal5375_best_existing_candidate": {
            "best_candidate_name": best["name"],
            "best_candidate_absolute_row_delta": int(best["absolute_row_delta"]),
            "best_candidate_row_ratio_rtdl_div_author": float(best["row_ratio_rtdl_div_author"]),
            "best_candidate_row_count_parity": bool(best["row_count_parity"]),
        },
        "assessment": {
            "status_candidate_contract_ready": bool(
                runtime_contract_present and partner_passthrough_present
            ),
            "author_lb_row_parity_established": False,
            "explicit_lb_support_authorized": False,
            "still_missing_or_analog_semantics": still_missing_or_analog,
            "next_required_work": (
                "Implement or experimentally probe a real RTDL status-machine "
                "mode that restores current-best state by active queue index, "
                "tracks author-like abort/miss/offload states, and validates "
                "row parity against the Goal5374 oracle."
            ),
        },
        "verification": {
            "focused_tests": [
                "tests.goal5376_status_machine_candidate_telemetry_test",
                "tests.goal5211_global_bound_early_break_contract_test",
                "tests.goal5172_native_inline_nearest_frontier_test",
            ],
            "pod_preflight_observed": True,
            "pod_runtime_probe_completed": False,
            "pod_runtime_probe_reason": (
                "This goal adds and locally verifies the generic telemetry contract; "
                "a full POD route probe requires syncing/rebuilding the remote "
                "workspace and remains the next implementation step."
            ),
        },
        "claim_boundary": {
            "status_candidate_contract_claimed": True,
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
    payload = build_artifact()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
