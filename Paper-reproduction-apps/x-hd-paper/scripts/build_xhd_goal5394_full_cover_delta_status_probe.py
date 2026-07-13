from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt  # noqa: E402


RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5394_full_cover_delta_status_probe.json"

GOAL5393 = RESULTS / "xhd_goal5393_lb_status_stream_target_design.json"
GOAL5387 = RESULTS / "xhd_goal5387_author_trace_v2_execution.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _repeat_candidates(
    query_row_ids: list[int],
    *,
    rows_per_query: int,
    first_cell_id: int,
    work_count: int = 9,
) -> dict[str, list[float | int]]:
    candidate_query_row_ids: list[int] = []
    candidate_cell_ids: list[int] = []
    candidate_min_sq: list[float] = []
    candidate_max_sq: list[float] = []
    candidate_work_counts: list[int] = []
    for query in query_row_ids:
        for local_index in range(rows_per_query):
            candidate_query_row_ids.append(int(query))
            candidate_cell_ids.append(first_cell_id + query * 1000 + local_index)
            candidate_min_sq.append(float(local_index + 1))
            candidate_max_sq.append(float(local_index + 2))
            candidate_work_counts.append(int(work_count))
    return {
        "candidate_query_row_ids": candidate_query_row_ids,
        "candidate_cell_ids": candidate_cell_ids,
        "candidate_min_sq": candidate_min_sq,
        "candidate_max_sq": candidate_max_sq,
        "candidate_work_counts": candidate_work_counts,
    }


def _build_synthetic_multiround_demo(*, base_rows_per_active: int, delta_rows_per_active: int) -> dict[str, Any]:
    query_row_ids = [0, 1]
    active_queue_indices = [10, 11]
    source_ids = [100, 101]
    result = rt.active_query_status_multiround_reference_numpy_columns(
        query_row_ids=query_row_ids,
        active_queue_indices=active_queue_indices,
        source_ids=source_ids,
        current_best_sq=[np.inf, np.inf],
        current_best_item_ids=[-1, -1],
        round_candidate_tables=[
            _repeat_candidates(
                query_row_ids,
                rows_per_query=base_rows_per_active,
                first_cell_id=1000,
            ),
            _repeat_candidates(
                query_row_ids,
                rows_per_query=delta_rows_per_active,
                first_cell_id=9000,
            ),
        ],
        heavy_threshold=5,
        return_metadata=True,
    )
    telemetry = result["telemetry"]
    rounds = telemetry["rounds"]
    return {
        "purpose": (
            "Synthetic app-neutral demonstration that the existing generic "
            "multi-round active-query status reference can represent a base "
            "offload surface plus a later generic delta surface. It is not an "
            "author parity proof."
        ),
        "contract": result["metadata"]["contract"],
        "app_semantics": result["metadata"]["app_semantics"],
        "author_semantics_claimed": False,
        "hardcoded_author_fanout_claimed": False,
        "synthetic_active_query_count": len(query_row_ids),
        "base_rows_per_active": base_rows_per_active,
        "delta_rows_per_active": delta_rows_per_active,
        "target_rows_per_active": base_rows_per_active + delta_rows_per_active,
        "base_round_offload_rows": rounds[0]["offload_row_count"],
        "delta_round_offload_rows": rounds[1]["offload_row_count"],
        "raw_offload_rows_before_sort_reduce": telemetry["raw_offload_rows_before_sort_reduce"],
        "final_active_query_count": telemetry["final_active_query_count"],
        "rounds": rounds,
        "sample_offload_cell_ids": result["offload_rows"]["cell_ids"][:5].astype(np.int64).tolist(),
    }


def build(output: Path = OUT) -> dict[str, Any]:
    goal5393 = _read_json(GOAL5393)
    author = _read_json(GOAL5387)
    target = goal5393["target_selection"]

    author_rows = int(author["author_lb_trace_v2"]["raw_offload_rows_before_sort_reduce"])
    active_count = int(author["author_lb_trace_v2"]["active_in_queue_size"])
    selected_rows = int(target["selected_surface_rows"])
    missing_rows = int(target["missing_rows_to_author"])
    missing_per_active = int(target["missing_rows_per_active_if_exact"])
    selected_per_active = int(target["selected_rows_per_active"])
    target_per_active = int(target["author_rows_per_active"])

    synthetic = _build_synthetic_multiround_demo(
        base_rows_per_active=selected_per_active,
        delta_rows_per_active=missing_per_active,
    )

    synthetic_matches_shape = (
        synthetic["base_rows_per_active"] == selected_per_active
        and synthetic["delta_rows_per_active"] == missing_per_active
        and synthetic["target_rows_per_active"] == target_per_active
    )

    return {
        "goal": "Goal5394",
        "date": "2026-07-10",
        "schema": "rtdl.paper_reproduction.xhd.goal5394.full_cover_delta_status_probe.v1",
        "status": "generic_full_cover_delta_probe_spec_ready__native_probe_next",
        "exit_label": "generic_full_cover_delta_probe_ready__native_or_fail_closed_next",
        "purpose": (
            "Convert Goal5393's selected full-cover delta target into a concrete "
            "generic probe specification and synthetic capability demo before "
            "native implementation."
        ),
        "input_artifacts": {
            "goal5393_status_stream_target_design": str(GOAL5393),
            "goal5387_author_trace_v2": str(GOAL5387),
        },
        "author_target": {
            "active_in_queue_size": active_count,
            "raw_offload_rows_before_sort_reduce": author_rows,
            "rows_per_active": target_per_active,
            "raw_offload_row_hash": int(author["author_lb_trace_v2"]["batch_0"]["raw_offload_row_hash"]),
        },
        "selected_surface": {
            "name": target["selected_starting_surface"],
            "row_count": selected_rows,
            "rows_per_active": selected_per_active,
            "missing_rows_to_author": missing_rows,
            "missing_rows_per_active": missing_per_active,
            "missing_rows_per_active_remainder": int(target["missing_rows_per_active_remainder"]),
            "full_cover_is_correctness_claim": False,
        },
        "synthetic_generic_probe": synthetic,
        "synthetic_probe_assessment": {
            "shape_matches_selected_target": synthetic_matches_shape,
            "proves_author_parity": False,
            "proves_native_backend_completion": False,
            "why_useful": (
                "It verifies that the generic multi-round status reference can "
                "represent the exact base+delta row-shape required by the next "
                "native probe without app-specific terminology or hard-coded "
                "author constants in RTDL core."
            ),
        },
        "native_probe_spec": {
            "name": "generic_full_cover_delta_status_probe",
            "recommended_goal": "Goal5395",
            "contract_kind": "generic_native_multi_round_active_query_status_stream",
            "start_surface": target["selected_starting_surface"],
            "must_not_hardcode": [
                "6 missing rows per active",
                "62 author rows per active",
                "X-HD option or figure names in RTDL core/native code",
            ],
            "required_output_columns": [
                "active_queue_index or query_row_id",
                "source_id",
                "cell_id",
                "status_code",
                "transition_phase_code",
                "current_best_before_sq",
                "current_best_after_sq or explicit not-applicable value",
            ],
            "required_telemetry": [
                "raw_offload_rows_before_sort_reduce",
                "raw_offload_row_hash or deterministic sample rows",
                "status_count_offloading",
                "feedback_update_count or explicit not-applicable evidence",
                "miss_count",
                "completed_count",
                "aborted_count",
            ],
            "must_compare_against_author": [
                "row_count",
                "hash_or_samples",
                "status_count_offloading",
                "load_balance_feedback_update_count or explicit not-applicable evidence",
            ],
            "success_exit_label": "generic_full_cover_delta_probe_moves_rows_toward_author",
            "fail_exit_label": "generic_full_cover_delta_probe_no_go__explicit_lb_fail_closed_candidate",
        },
        "decision": {
            "native_code_implemented_by_goal5394": False,
            "native_probe_ready_for_implementation": True,
            "explicit_lb_support_remains_unsupported": True,
            "next_gate_requires_pod_if_native_code_is_changed": True,
        },
        "claim_boundary": {
            "generic_full_cover_delta_probe_spec_claimed": True,
            "synthetic_generic_multiround_demo_claimed": True,
            "author_parity_claimed": False,
            "native_backend_completion_claimed": False,
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
