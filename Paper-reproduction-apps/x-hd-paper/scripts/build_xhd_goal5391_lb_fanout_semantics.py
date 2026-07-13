from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5391_lb_fanout_semantics.json"

GOAL5387 = RESULTS / "xhd_goal5387_author_trace_v2_execution.json"
GOAL5390 = RESULTS / "xhd_goal5390_full_trace_summary_gate.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _division_summary(row_count: int, active_count: int) -> dict[str, Any]:
    quotient, remainder = divmod(row_count, active_count)
    return {
        "row_count": row_count,
        "active_query_count": active_count,
        "integer_multiple": remainder == 0,
        "rows_per_active_average": row_count / active_count,
        "rows_per_active_integer_if_exact": quotient if remainder == 0 else None,
        "remainder": remainder,
    }


def build(output: Path = OUT) -> dict[str, Any]:
    author = _read_json(GOAL5387)
    full_gate = _read_json(GOAL5390)

    author_trace = author["author_lb_trace_v2"]
    author_batch = author_trace["batch_0"]
    comparison = full_gate["comparison_to_author"]

    active_count = int(author_trace["active_in_queue_size"])
    rtdl_active_count = int(full_gate["rtdl_trace_summary"]["active_query_count"])
    author_rows = int(author_trace["raw_offload_rows_before_sort_reduce"])
    rtdl_rows = int(full_gate["rtdl_trace_summary"]["row_count"])

    author_division = _division_summary(author_rows, active_count)
    rtdl_division = _division_summary(rtdl_rows, rtdl_active_count)
    row_delta = author_rows - rtdl_rows
    per_active_delta = (
        author_division["rows_per_active_average"] - rtdl_division["rows_per_active_average"]
    )

    denominator_mismatch = (
        active_count == rtdl_active_count
        and author_rows != rtdl_rows
        and bool(comparison["active_query_count_parity"])
        and not bool(comparison["row_count_parity"])
    )

    return {
        "goal": "Goal5391",
        "date": "2026-07-10",
        "schema": "rtdl.paper_reproduction.xhd.goal5391.lb_fanout_semantics.v1",
        "status": "fanout_denominator_mismatch_classified__native_multiround_required",
        "exit_label": "lb_fanout_semantics_mismatch__bridge_runtime_not_next_target",
        "purpose": (
            "Classify the Goal5390 full-source -lb trace mismatch as a "
            "status-stream fanout / transition semantics problem using the "
            "Goal5387 author trace v2 oracle and the Goal5390 RTDL trace summary."
        ),
        "input_artifacts": {
            "goal5387_author_trace_v2": str(GOAL5387),
            "goal5390_full_trace_summary_gate": str(GOAL5390),
        },
        "scope": {
            "level": "level_b_public_dragon_asian_lb256_diagnostic",
            "source_limit_applied": bool(full_gate["run_scope"]["source_limit_applied"]),
            "point_count_a": int(full_gate["run_scope"]["point_count_a"]),
            "point_count_b": int(full_gate["run_scope"]["point_count_b"]),
            "explicit_lb_support_before_goal5391": False,
        },
        "author_denominator": {
            "active_in_queue_size": active_count,
            "raw_offload_rows_before_sort_reduce": author_rows,
            "status_count_offloading_append": int(author_trace["status_count_offloading_append"]),
            "raw_offload_row_hash": int(author_batch["raw_offload_row_hash"]),
            "division": author_division,
        },
        "rtdl_denominator": {
            "active_query_count": rtdl_active_count,
            "raw_offload_rows": rtdl_rows,
            "status_count_offloading": int(full_gate["rtdl_trace_summary"]["status_count_offloading"]),
            "raw_offload_row_hash": int(full_gate["rtdl_trace_summary"]["raw_offload_row_hash"]),
            "division": rtdl_division,
        },
        "comparison": {
            "active_query_count_parity": bool(comparison["active_query_count_parity"]),
            "row_count_parity": bool(comparison["row_count_parity"]),
            "hash_parity": bool(comparison["hash_parity"]),
            "author_rows_minus_rtdl_rows": row_delta,
            "rtdl_rows_div_author_rows": rtdl_rows / author_rows,
            "author_rows_per_active_minus_rtdl_rows_per_active": per_active_delta,
            "author_and_rtdl_row_counts_are_exact_active_multiples": (
                author_division["integer_multiple"] and rtdl_division["integer_multiple"]
            ),
            "aggregate_rows_per_active_author": author_division["rows_per_active_average"],
            "aggregate_rows_per_active_rtdl": rtdl_division["rows_per_active_average"],
            "denominator_mismatch_confirmed": denominator_mismatch,
        },
        "classification": {
            "primary_mismatch": "status_stream_fanout_or_transition_semantics",
            "why": (
                "The active query count matches, but author raw offload rows are "
                "an exact 62x the active count while the current RTDL trace rows "
                "are an exact 5x the active count. This aggregate denominator "
                "gap is much larger than a bridge formatting issue and cannot be "
                "fixed by source-limited smoke or bridge runtime optimization."
            ),
            "not_proven": [
                "per-query uniform fanout distribution",
                "author-compatible row identity",
                "explicit -lb support",
                "Figure 7 or Figure 11 reproduction",
            ],
        },
        "next_native_status_stream_requirements": {
            "required_contract_kind": "generic_native_multi_round_active_query_status_stream",
            "must_change_denominator": True,
            "must_compare_to_author_trace_v2": True,
            "minimum_comparison_fields": [
                "active_query_count",
                "raw_offload_row_count",
                "raw_offload_row_hash",
                "sampled query/source ids",
                "sampled cell ids",
                "status_count_offloading",
                "miss/completed/aborted counters or explicit not-applicable evidence",
                "load-balance feedback count or explicit not-applicable evidence",
            ],
            "forbidden_implementation_shortcuts": [
                "hard-code 62 rows per active query",
                "X-HD-specific native primitive names or paper semantics in RTDL core",
                "bridge vectorization as the main fix while row/hash parity is false",
                "source-limited smoke as a substitute for full-source parity",
            ],
        },
        "decision": {
            "explicit_lb_support_remains_unsupported": True,
            "bridge_runtime_optimization_rejected_as_next_main_path": True,
            "source_limited_smoke_rejected_as_next_main_path": True,
            "next_gate": "generic_native_multiround_status_stream_or_fail_closed_lb_closeout",
        },
        "claim_boundary": {
            "fanout_diagnostic_claimed": True,
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "hash_sample_parity_claimed": False,
            "per_query_distribution_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "same_denominator_memory_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "performance_ratio_claimed": False,
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
