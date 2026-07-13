from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"

GOAL5387_AUTHOR_TRACE = RESULTS / "xhd_goal5387_author_trace_v2_execution.json"
GOAL5398_NATIVE_V7 = RESULTS / "xhd_goal5398_native_v7_status_stream_parity_gate_pod.json"
GOAL5402_NATIVE_SMOKE = RESULTS / "xhd_goal5402_status_state_machine_native_smoke_pod.json"
OUT = RESULTS / "xhd_goal5403_status_state_next_gate_decision.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _author_trace_summary(payload: dict[str, Any]) -> dict[str, Any]:
    trace = payload["author_lb_trace_v2"]
    batch = trace["batch_0"]
    return {
        "artifact": str(GOAL5387_AUTHOR_TRACE),
        "schema": trace.get("schema"),
        "active_in_queue_size": int(trace["active_in_queue_size"]),
        "raw_offload_rows_before_sort_reduce": int(trace["raw_offload_rows_before_sort_reduce"]),
        "status_count_offloading": int(trace["status_count_offloading_append"]),
        "feedback_update_count": int(trace["load_balance_feedback_update_count"]),
        "raw_offload_row_hash": int(batch["raw_offload_row_hash"]),
        "raw_offload_row_sample_point_ids": [int(value) for value in batch.get("raw_offload_row_sample_point_ids", [])],
        "raw_offload_row_sample_cell_ids": [int(value) for value in batch.get("raw_offload_row_sample_cell_ids", [])],
        "author_trace_v2_oracle_ready": bool(payload["claim_boundary"]["author_v2_trace_oracle_claimed"]),
    }


def _native_v7_summary(payload: dict[str, Any]) -> dict[str, Any]:
    comparison = payload["native_v7_status_stream"]["comparison_to_author"]
    metadata = payload["native_v7_status_stream"]["native_result_metadata"]
    return {
        "artifact": str(GOAL5398_NATIVE_V7),
        "native_generic_symbol": metadata["native_generic_symbol"],
        "contract": metadata["contract"],
        "active_query_count_parity": bool(comparison["active_query_count_parity"]),
        "row_count_parity": bool(comparison["row_count_parity"]),
        "hash_parity": bool(comparison["hash_parity"]),
        "status_count_offloading_parity": bool(comparison["status_count_offloading_parity"]),
        "feedback_update_count_parity": comparison["feedback_update_count_parity"],
        "author_raw_offload_rows_before_sort_reduce": int(comparison["author_raw_offload_rows_before_sort_reduce"]),
        "rtdl_v7_offload_rows": int(comparison["rtdl_v7_offload_rows"]),
        "row_delta_author_minus_rtdl_v7": int(comparison["row_delta_author_minus_rtdl_v7"]),
        "row_ratio_rtdl_v7_div_author": float(comparison["row_ratio_rtdl_v7_div_author"]),
        "author_raw_offload_row_hash": int(comparison["author_raw_offload_row_hash"]),
        "rtdl_raw_offload_row_hash": int(comparison["rtdl_raw_offload_row_hash"]),
        "author_raw_offload_row_sample_point_ids": [
            int(value) for value in comparison.get("author_raw_offload_row_sample_point_ids", [])
        ],
        "author_raw_offload_row_sample_cell_ids": [
            int(value) for value in comparison.get("author_raw_offload_row_sample_cell_ids", [])
        ],
        "rtdl_sample_source_ids": [int(value) for value in comparison.get("rtdl_sample_source_ids", [])],
        "rtdl_sample_cell_ids": [int(value) for value in comparison.get("rtdl_sample_cell_ids", [])],
        "explicit_lb_support_remains_unsupported": bool(
            payload["decision"]["explicit_lb_support_remains_unsupported"]
        ),
    }


def _native_smoke_summary(payload: dict[str, Any]) -> dict[str, Any]:
    metadata = payload["native_result_metadata"]
    telemetry = payload["observed"]["telemetry"]
    return {
        "artifact": str(GOAL5402_NATIVE_SMOKE),
        "matched": bool(payload["matched"]),
        "status": payload["status"],
        "fixture": payload["fixture"],
        "native_generic_symbol": metadata["native_generic_symbol"],
        "contract": metadata["contract"],
        "synthetic_active_query_count": int(telemetry["active_query_count"]),
        "synthetic_candidate_row_count": int(telemetry["candidate_row_count"]),
        "synthetic_raw_offload_row_count": int(telemetry["raw_offload_row_count"]),
        "synthetic_status_count_offloading": int(telemetry["status_count_offloading"]),
        "synthetic_feedback_update_count": int(telemetry["feedback_update_count"]),
        "generic_native_status_state_smoke_claimed": bool(
            payload["claim_boundary"]["generic_native_status_state_smoke_claimed"]
        ),
    }


def build(
    *,
    author_trace_path: Path = GOAL5387_AUTHOR_TRACE,
    native_v7_path: Path = GOAL5398_NATIVE_V7,
    native_smoke_path: Path = GOAL5402_NATIVE_SMOKE,
) -> dict[str, Any]:
    author_payload = _read_json(author_trace_path)
    native_v7_payload = _read_json(native_v7_path)
    smoke_payload = _read_json(native_smoke_path)

    author = _author_trace_summary(author_payload)
    native_v7 = _native_v7_summary(native_v7_payload)
    smoke = _native_smoke_summary(smoke_payload)

    full_gate_blockers = [
        "current native v7 status stream has row_count_parity=false",
        "current native v7 status stream has hash_parity=false",
        "current native v7 feedback_update_count_parity is null/unmeasured",
        "Goal5402 is synthetic and does not consume the real Goal5387 candidate/frontier stream",
        "Goal5402 active/query/row scale is 3 active queries and 2 rows, not 437645 active queries and 27133990 rows",
    ]

    bounded_oracle_requirements = [
        "deterministic small app-shaped fixture",
        "raw offload rows before continuation/reduce",
        "row_count and deterministic row hash or sample comparison",
        "status_count_offloading comparison",
        "feedback_update_count comparison",
        "overflow fail-closed behavior",
        "no X-HD-specific constants or option names in RTDL core/native",
    ]

    return {
        "goal": "Goal5403",
        "date": "2026-07-10",
        "schema": "rtdl.paper_reproduction.xhd.goal5403.status_state_next_gate_decision.v1",
        "status": "bounded_status_state_oracle_gate_authorized__direct_full_trace_gate_not_ready",
        "exit_label": "authorize_goal5404_bounded_status_state_oracle_gate__direct_goal5387_gate_not_ready",
        "purpose": (
            "Reconcile the Goal5387 author trace oracle, Goal5398 native v7 "
            "mismatch, Goal5400 knob exhaustion, and Goal5402 native synthetic "
            "smoke before choosing the next explicit-lb status-state gate."
        ),
        "input_artifacts": {
            "goal5387_author_trace_v2": str(author_trace_path),
            "goal5398_native_v7_status_stream_parity_gate": str(native_v7_path),
            "goal5402_native_status_state_smoke": str(native_smoke_path),
        },
        "author_trace_v2_target": author,
        "current_rtdl_native_v7": native_v7,
        "goal5402_native_smoke": smoke,
        "scale_gap": {
            "author_active_queries": author["active_in_queue_size"],
            "smoke_active_queries": smoke["synthetic_active_query_count"],
            "author_raw_rows": author["raw_offload_rows_before_sort_reduce"],
            "smoke_raw_rows": smoke["synthetic_raw_offload_row_count"],
            "native_v7_raw_rows": native_v7["rtdl_v7_offload_rows"],
            "native_v7_row_ratio_to_author": native_v7["row_ratio_rtdl_v7_div_author"],
        },
        "readiness_assessment": {
            "author_trace_v2_oracle_ready": author["author_trace_v2_oracle_ready"],
            "native_v7_gap_confirmed": not (
                native_v7["row_count_parity"]
                and native_v7["hash_parity"]
                and native_v7["status_count_offloading_parity"]
            ),
            "synthetic_native_smoke_ready": bool(smoke["matched"]),
            "bounded_app_oracle_gate_ready_to_design": bool(smoke["matched"]),
            "direct_full_goal5387_gate_ready": False,
            "direct_full_goal5387_gate_blockers": full_gate_blockers,
        },
        "next_gate_requirements": {
            "recommended_goal": "Goal5404_bounded_status_state_oracle_gate",
            "requirements": bounded_oracle_requirements,
            "success_exit_label": "bounded_status_state_oracle_matches_rows_status_feedback__full_gate_next",
            "fail_exit_label": "bounded_status_state_oracle_no_go__explicit_lb_remains_fail_closed",
        },
        "decision": {
            "direct_full_goal5387_gate_authorized": False,
            "bounded_status_state_oracle_gate_authorized": True,
            "explicit_lb_support_remains_unsupported": True,
            "do_not_claim_goal5387_row_hash_parity": True,
            "do_not_claim_figure7_or_figure11": True,
            "next_goal": "Goal5404",
        },
        "claim_boundary": {
            "status_state_next_gate_decision_claimed": True,
            "author_trace_v2_oracle_referenced": True,
            "native_v7_gap_referenced": True,
            "native_smoke_referenced": True,
            "bounded_oracle_authorized": True,
            "direct_full_trace_gate_claimed_ready": False,
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "hash_sample_parity_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "same_denominator_memory_claimed": False,
            "performance_ratio_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    payload = build()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
