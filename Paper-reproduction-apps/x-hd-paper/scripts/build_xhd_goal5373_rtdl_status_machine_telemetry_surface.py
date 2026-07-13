from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5373_rtdl_status_machine_telemetry_surface.json"

GOAL5372 = RESULTS / "xhd_goal5372_author_shader_status_machine_gap.json"
NATIVE_WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
NATIVE_PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
PARTNER_CONTINUATIONS = ROOT / "src" / "rtdsl" / "partner_continuations.py"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _has_all(text: str, needles: tuple[str, ...]) -> bool:
    return all(needle in text for needle in needles)


def _coverage(status: str, evidence: str, missing: str = "") -> dict[str, object]:
    if status not in {"available", "partial", "missing"}:
        raise ValueError(f"unexpected coverage status: {status}")
    return {
        "status": status,
        "evidence": evidence,
        "missing": missing,
    }


def build_artifact() -> dict[str, Any]:
    goal5372 = _read_json(GOAL5372)
    workloads = _read_text(NATIVE_WORKLOADS)
    prelude = _read_text(NATIVE_PRELUDE)
    runtime = _read_text(OPTIX_RUNTIME)
    partner = _read_text(PARTNER_CONTINUATIONS)

    surface_checks = {
        "native_v3_memory_telemetry_symbol": "rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry_v3"
        in prelude
        and "rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry_v3" in workloads,
        "raw_frontier_kind_counts": _has_all(
            workloads,
            (
                "raw_frontier_kind_counts",
                "g_optix_last_cell_mbr_frontier_raw_kind1_rows",
                "g_optix_last_cell_mbr_frontier_raw_kind2_rows",
                "g_optix_last_cell_mbr_frontier_raw_kind3_rows",
            ),
        ),
        "inline_stats": _has_all(
            workloads,
            ("inline_cell_hit_count", "inline_point_eval_count", "collect_inline_stats"),
        ),
        "global_bound_early_break": _has_all(
            workloads,
            (
                "global_bound_early_break_count",
                "global_bound_distance_bits",
                "can_global_bound_abort",
            ),
        ),
        "python_exposes_raw_kind_counts": _has_all(
            runtime,
            (
                "raw_frontier_kind_counts",
                "raw_frontier_kind2_rows",
                "raw_frontier_kind_counts_semantics",
            ),
        ),
        "python_exposes_global_bound": _has_all(
            partner,
            (
                "global_bound_early_break_count",
                "global_bound_distance",
                "global_bound_contract",
            ),
        ),
    }
    if not all(surface_checks.values()):
        missing = [name for name, ok in surface_checks.items() if not ok]
        raise RuntimeError(f"Expected current telemetry surface checks failed: {missing}")

    forbidden_status_machine_symbols = {
        "author_like_status_count_init": "status_count_init",
        "author_like_status_count_offloading": "status_count_offloading",
        "author_like_status_count_aborted": "status_count_aborted",
        "author_like_miss_queue_count": "miss_queue_count",
        "author_like_cmax2_abort_count": "cmax2_mbr_abort_count",
        "author_like_raw_offload_author_width": "raw_offload_rows_author_width_bytes",
        "author_like_active_in_queue_size": "active_in_queue_size",
    }
    missing_status_machine_tokens = {
        name: token not in workloads and token not in runtime and token not in partner
        for name, token in forbidden_status_machine_symbols.items()
    }

    required_gate_fields = list(goal5372["next_gate_contract"]["minimum_fields"])
    field_coverage = {
        "active_in_queue_size": _coverage(
            "missing",
            "generic query_count exists, but current rows are indexed by query_row_id, not the author's active in_queue namespace",
            "active queue indices and active queue size under author iteration state",
        ),
        "raw_offload_rows_before_sort_reduce": _coverage(
            "partial",
            "raw_frontier_kind2_rows counts generic offload-kind rows before Python materialization",
            "author status-machine pruning/abort and in_q_idx namespace before sort/reduce",
        ),
        "raw_offload_rows_author_width_bytes": _coverage(
            "missing",
            "Goal5282 can compute shape-level candidate bytes after the fact, but the current frontier API does not emit this field",
            "author-width byte field tied to status-machine raw rows",
        ),
        "status_count_init": _coverage(
            "missing",
            "no native or Python telemetry surface exposes author ShaderStatus::kInit counts",
            "status payload accounting",
        ),
        "status_count_offloading": _coverage(
            "missing",
            "kind2/offload rows are not equivalent to kOffloading status after author abort/prune semantics",
            "author kOffloading status count",
        ),
        "status_count_aborted": _coverage(
            "missing",
            "existing global_bound_early_break_count is not author kAborted and was zero in Goal5371",
            "author kAborted status count",
        ),
        "miss_queue_count": _coverage(
            "missing",
            "current generic frontier collector does not model author miss_queue append semantics",
            "source count appended to author miss_queue",
        ),
        "cmax2_mbr_abort_count": _coverage(
            "missing",
            "current generic global-bound flag is max-nearest early break, not author max_dist2 <= cmax2 MBR abort",
            "separate cmax2 MBR abort counter",
        ),
        "point_loop_early_break_count": _coverage(
            "partial",
            "global_bound_early_break_count can count RTDL inline point-loop early termination for the generic max-nearest flag",
            "author point-loop early-break count tied to ShaderStatus::kAborted and cmax2",
        ),
        "current_best_state_source": _coverage(
            "partial",
            "front door accepts current_best_distances/current_best_item_ids and inline nearest updates them",
            "author cmin2 state source, restoration by in_q_idx, and load-balance propagation",
        ),
        "row_count_parity_against_author_offloading_size": _coverage(
            "missing",
            "Goal5371 records 21,006,960 RTDL inline kind2 rows vs 27,133,990 author OffloadingSize rows",
            "row parity or reviewed denominator explanation",
        ),
    }
    missing_required = [
        field for field in required_gate_fields if field_coverage[field]["status"] == "missing"
    ]
    partial_required = [
        field for field in required_gate_fields if field_coverage[field]["status"] == "partial"
    ]

    return {
        "goal": "Goal5373",
        "date": "2026-07-09",
        "schema": "rtdl.paper_reproduction.xhd.goal5373.rtdl_status_machine_telemetry_surface.v1",
        "status": "rtdl_status_machine_telemetry_surface_audited__author_lb_trace_fields_missing",
        "exit_label": "current_surface_insufficient__native_status_probe_or_author_instrumentation_required",
        "purpose": (
            "Audit the current generic RTDL cell-MBR frontier telemetry surface against "
            "Goal5372's author_shader_status_machine_lb_trace minimum fields before "
            "attempting explicit -lb support."
        ),
        "input_artifacts": {
            "goal5372": str(GOAL5372),
        },
        "source_evidence": {
            "native_workloads": str(NATIVE_WORKLOADS),
            "native_prelude": str(NATIVE_PRELUDE),
            "optix_runtime": str(OPTIX_RUNTIME),
            "partner_continuations": str(PARTNER_CONTINUATIONS),
            "surface_checks": surface_checks,
            "missing_status_machine_tokens": missing_status_machine_tokens,
        },
        "current_available_surface": {
            "raw_frontier_kind_counts": True,
            "raw_frontier_kind2_rows": True,
            "inline_cell_hit_count": True,
            "inline_point_evaluation_count": True,
            "global_bound_early_break_count": True,
            "global_bound_distance": True,
            "native_phase_timings": True,
            "native_memory_telemetry": True,
        },
        "required_gate_fields": required_gate_fields,
        "field_coverage": field_coverage,
        "coverage_summary": {
            "available_count": sum(1 for item in field_coverage.values() if item["status"] == "available"),
            "partial_count": len(partial_required),
            "missing_count": len(missing_required),
            "partial_fields": partial_required,
            "missing_fields": missing_required,
            "ready_for_author_shader_status_machine_lb_trace": False,
        },
        "decision": {
            "explicit_lb_support_authorized": False,
            "why": (
                "The current RTDL surface can report generic kind counts and generic "
                "global-bound diagnostics, but it cannot report the author active "
                "queue/status/cmin2/miss/load-balance denominator required by Goal5372."
            ),
            "next_options": [
                "add a generic experimental native status-machine probe that emits the missing fields",
                "instrument the author code to dump raw queue/status/cmin2 oracle rows",
            ],
            "recommended_next_goal": "Goal5374 author_shader_status_machine_lb_trace implementation_or_author_instrumentation",
        },
        "claim_boundary": {
            "telemetry_surface_audit_claimed": True,
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
