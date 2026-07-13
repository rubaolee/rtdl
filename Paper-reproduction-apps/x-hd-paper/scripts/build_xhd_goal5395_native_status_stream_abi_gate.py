from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt  # noqa: E402


RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5395_native_status_stream_abi_gate.json"
GOAL5394 = RESULTS / "xhd_goal5394_full_cover_delta_status_probe.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _source_contains(path: Path, needle: str) -> bool:
    return needle in path.read_text(encoding="utf-8", errors="ignore")


def build(output: Path = OUT) -> dict[str, Any]:
    goal5394 = _read_json(GOAL5394)
    validation = rt.validate_active_query_status_stream_native_abi_contract()
    contract = validation["contract"]

    prelude = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
    optix_api = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
    optix_runtime = ROOT / "src" / "rtdsl" / "optix_runtime.py"

    v6_symbol = "rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v6"
    v7_symbol = "rtdl_optix_collect_active_query_status_stream_3d_v1"

    existing_v6_present = all(
        _source_contains(path, v6_symbol)
        for path in (prelude, optix_api, optix_runtime)
    )
    future_symbol_present = any(
        _source_contains(path, v7_symbol)
        for path in (prelude, optix_api, optix_runtime)
    )

    required_output_columns = tuple(contract["output_row_schema"])
    v6_available_columns = (
        "frontier_kind_code",
        "query_row_id",
        "query_point_id",
        "cell_id",
        "point_begin_offset",
        "point_count",
        "min_distance",
        "max_distance",
        "nearest_distance",
        "nearest_item_id",
    )
    missing_required_columns = [
        column for column in required_output_columns if column not in v6_available_columns
    ]

    target = goal5394["selected_surface"]
    author = goal5394["author_target"]

    return {
        "goal": "Goal5395",
        "date": "2026-07-10",
        "schema": "rtdl.paper_reproduction.xhd.goal5395.native_status_stream_abi_gate.v1",
        "status": "native_status_stream_abi_contract_ready__native_backend_not_implemented",
        "exit_label": "native_status_stream_abi_gate_ready__implement_v7_or_fail_closed_next",
        "purpose": (
            "Turn the Goal5394 native probe requirements into a public generic "
            "RTDL ABI contract and audit whether the current native surface can "
            "satisfy it before writing backend code."
        ),
        "input_artifacts": {
            "goal5394_full_cover_delta_status_probe": str(GOAL5394),
        },
        "generic_native_abi_contract": {
            "validation_status": validation["status"],
            "contract": contract["contract"],
            "status": contract["status"],
            "executable": contract["executable"],
            "app_generic": contract["app_generic"],
            "reference_contract": contract["reference_contract"],
            "output_row_schema": list(contract["output_row_schema"]),
            "telemetry_schema": list(contract["telemetry_schema"]),
            "overflow_policy": contract["overflow_policy"],
            "explicit_app_option_support_claimed": contract[
                "explicit_app_option_support_claimed"
            ],
        },
        "goal5394_target": {
            "author_rows": int(author["raw_offload_rows_before_sort_reduce"]),
            "author_rows_per_active": int(author["rows_per_active"]),
            "full_cover_rows": int(target["row_count"]),
            "full_cover_rows_per_active": int(target["rows_per_active"]),
            "missing_rows": int(target["missing_rows_to_author"]),
            "missing_rows_per_active": int(target["missing_rows_per_active"]),
            "full_cover_is_correctness_claim": bool(target["full_cover_is_correctness_claim"]),
        },
        "current_native_surface_audit": {
            "latest_cell_mbr_status_probe_symbol": v6_symbol,
            "latest_symbol_present_in_python_and_native_sources": bool(existing_v6_present),
            "future_multiround_status_symbol": v7_symbol,
            "future_symbol_already_present": bool(future_symbol_present),
            "supported_probe_modes": [
                "default",
                "heavy-before-inline-prune",
                "active-initial-best-prune",
            ],
            "current_surface_is_single_launch_frontier_probe": True,
            "current_surface_satisfies_goal5394_native_probe": False,
            "v6_available_columns": list(v6_available_columns),
            "missing_required_output_columns": missing_required_columns,
            "missing_required_semantics": [
                "multi-round feedback state",
                "transition_phase_code",
                "current_best_before_sq per status row",
                "current_best_after_sq per status row",
                "miss/completed/aborted row counts from the same native status stream",
                "feedback update count or explicit not-applicable evidence from the native stream",
            ],
        },
        "decision": {
            "native_code_implemented_by_goal5395": False,
            "generic_native_abi_contract_added": True,
            "existing_native_v6_is_sufficient": False,
            "explicit_lb_support_remains_unsupported": True,
            "recommended_next_goal": "Goal5396",
            "recommended_next_action": (
                "Implement a new generic native active-query status-stream "
                "backend matching the ABI contract, or fail-close explicit "
                "load-balance support if that requires app-specific constants."
            ),
            "next_gate_requires_pod": True,
        },
        "claim_boundary": {
            "generic_native_abi_contract_claimed": True,
            "native_backend_completion_claimed": False,
            "existing_native_v6_parity_claimed": False,
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "hash_sample_parity_claimed": False,
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
