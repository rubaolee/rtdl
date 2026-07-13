from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build(output: Path) -> dict[str, Any]:
    results_dir = output.parent
    author_oracle = _load_json(results_dir / "xhd_goal5374_author_lb_status_trace_oracle.json")
    goal5384 = _load_json(results_dir / "xhd_goal5384_multiround_status_requirements.json")

    author_rows = (
        None
        if author_oracle is None
        else author_oracle.get("author_lb_trace", {}).get("raw_offload_rows_before_sort_reduce")
    )
    author_width_bytes = (
        None
        if author_oracle is None
        else author_oracle.get("author_lb_trace", {}).get("raw_offload_rows_author_width_bytes")
    )

    artifact = {
        "goal": "Goal5385",
        "date": "2026-07-10",
        "schema": "rtdl.paper_reproduction.xhd.goal5385.author_trace_v2_spec.v1",
        "status": "implemented_review_pending",
        "exit_label": "author_trace_v2_spec_ready__next_patch_author_or_native_stream",
        "purpose": (
            "Define the stronger author-side lb status trace needed to compare "
            "RTDL's multi-round active-query status stream against the author's "
            "load-balance/offload denominator."
        ),
        "current_author_oracle": {
            "source": "Goal5374",
            "available": author_oracle is not None,
            "schema": None if author_oracle is None else author_oracle.get("author_lb_trace", {}).get("schema"),
            "active_in_queue_size": (
                None if author_oracle is None else author_oracle.get("author_lb_trace", {}).get("active_in_queue_size")
            ),
            "raw_offload_rows_before_sort_reduce": author_rows,
            "raw_offload_rows_author_width_bytes": author_width_bytes,
            "limitation": "counts_only_no_row_identity_no_cmin2_vectors_no_load_balance_feedback",
        },
        "goal5384_multiround_requirement": {
            "available": goal5384 is not None,
            "contract": (
                None
                if goal5384 is None
                else goal5384.get("generic_system_addition", {}).get("contract")
            ),
            "required_fields": (
                []
                if goal5384 is None
                else goal5384.get("requirements_for_next_native_or_author_gate", {}).get("required_fields", [])
            ),
        },
        "author_trace_v2_schema": {
            "name": "rtdl.goal5385.author.lb_status_trace.v2",
            "owner": "paper_app_author_instrumentation",
            "app_semantics": "xhd_author_oracle_only",
            "required_batch_fields": [
                "batch_index",
                "iteration_index",
                "radius",
                "active_in_queue_size",
                "cmax2_before_ray",
                "cmax2_after_ray",
                "cmax2_after_load_balance",
                "cmin2_initial_hash",
                "cmin2_after_ray_hash",
                "cmin2_after_load_balance_hash",
                "cmin2_sample_indices",
                "cmin2_initial_samples",
                "cmin2_after_ray_samples",
                "cmin2_after_load_balance_samples",
                "raw_offload_rows_before_sort_reduce",
                "raw_offload_row_hash",
                "raw_offload_row_sample_point_ids",
                "raw_offload_row_sample_cell_ids",
                "status_count_init",
                "status_count_offloading",
                "status_count_aborted",
                "status_count_miss",
                "status_count_completed",
                "cmax2_mbr_abort_count",
                "point_loop_early_break_count",
                "load_balance_input_row_count",
                "load_balance_group_count",
                "load_balance_feedback_update_count",
            ],
            "optional_large_fields": [
                "raw_offload_point_ids_full",
                "raw_offload_cell_ids_full",
                "cmin2_initial_full",
                "cmin2_after_ray_full",
                "cmin2_after_load_balance_full",
            ],
            "dump_policy": {
                "full_raw_rows_required_for_default_gate": False,
                "hash_and_sample_required": True,
                "full_dump_allowed_under_explicit_flag": True,
                "reason": (
                    "Dragon->Asian lb256 has 27133990 raw offload rows; a full "
                    "uint32 pair dump is about 217071920 bytes before container "
                    "format overhead."
                ),
            },
        },
        "patch_targets": {
            "author_files": [
                "src/rt/launch_parameters.h",
                "src/rt/shaders/shaders_nn_uniform_grid.cu",
                "src/hd_impl/hausdorff_distance_rt.h",
            ],
            "must_not_patch_rtdl_core": True,
            "instrumentation_marker": "RTDL_GOAL5385_LB_STATUS_TRACE_V2",
            "expected_hook_points": [
                "before ray launch: hash/sample initial cmin2 and record cmax2",
                "inside shader offload append: preserve raw point_id/cell_id stream for hash/sample",
                "after ray launch before loadBalanceProcessing: hash/sample cmin2 and queue rows",
                "inside/after loadBalanceProcessing: record group count and feedback update count",
                "after loadBalanceProcessing: hash/sample cmin2 and cmax2",
            ],
        },
        "comparison_gate_requirements": {
            "must_compare_same_input_pair": "Dragon -> AsianDragon Level-B lb=256 diagnostic",
            "must_report": [
                "active_in_queue_parity",
                "raw_offload_row_count_parity",
                "raw_offload_row_hash_parity_if_full_or_hash_available",
                "cmin2_state_hash_comparison",
                "load_balance_feedback_count_comparison",
                "row_count_parity_against_goal5374",
            ],
            "minimum_success_for_native_counterpart": [
                "active_in_queue_parity=true",
                "raw_offload_row_count_parity=true",
                "status_count_offloading_parity=true",
                "explicit_lb_support_claimed=false_until_review",
            ],
        },
        "claim_boundary": {
            "author_v2_trace_implemented": False,
            "author_v2_trace_executed_on_pod": False,
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "rtdl_author_performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
    }
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT
        / "Paper-reproduction-apps"
        / "x-hd-paper"
        / "results"
        / "xhd_goal5385_author_trace_v2_spec.json",
    )
    args = parser.parse_args()
    artifact = build(args.output)
    print(json.dumps({"output": str(args.output), "status": artifact["status"]}, indent=2))


if __name__ == "__main__":
    main()
