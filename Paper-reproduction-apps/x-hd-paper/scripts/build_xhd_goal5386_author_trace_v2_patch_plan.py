from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"

LAUNCH_REL = Path("src/rt/launch_parameters.h")
SHADER_REL = Path("src/rt/shaders/shaders_nn_uniform_grid.cu")
RT_REL = Path("src/hd_impl/hausdorff_distance_rt.h")

MARKER = "RTDL_GOAL5385_LB_STATUS_TRACE_V2"
SCHEMA = "rtdl.paper_reproduction.xhd.goal5386.author_trace_v2_patch_plan.v1"


def _default_author_root() -> Path:
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        return Path(local_appdata) / "Temp" / "xhd-author-src"
    return Path.home() / "AppData" / "Local" / "Temp" / "xhd-author-src"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _line_for_anchor(text: str, anchor: str) -> int | None:
    index = text.find(anchor)
    if index < 0:
        return None
    return text.count("\n", 0, index) + 1


HOOKS: list[dict[str, Any]] = [
    {
        "name": "launch_parameter_trace_fields",
        "target": str(LAUNCH_REL).replace("\\", "/"),
        "anchor": "dev::Queue<uint32_t> offloading_point_ids;",
        "fields": [
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
        ],
        "patch_intent": "extend author launch parameters with v2 trace counters and optional hash/sample buffers",
    },
    {
        "name": "outer_iteration_scope",
        "target": str(RT_REL).replace("\\", "/"),
        "anchor": "while (in_size > 0) {",
        "fields": [
            "iteration_index",
            "radius",
            "cmax2_before_ray",
            "cmax2_after_ray",
            "cmax2_after_load_balance",
        ],
        "patch_intent": "open per-iteration trace object and capture cmax2 before/after ray and load-balance",
    },
    {
        "name": "batch_scope_and_active_queue",
        "target": str(RT_REL).replace("\\", "/"),
        "anchor": "auto valid_batch_size = batch_end - batch_begin;",
        "fields": [
            "batch_index",
            "active_in_queue_size",
            "cmin2_sample_indices",
        ],
        "patch_intent": "record batch index, active input queue window, and deterministic cmin2 sample indices",
    },
    {
        "name": "cmin2_initial_state",
        "target": str(RT_REL).replace("\\", "/"),
        "anchor": "thrust::fill(rmm::exec_policy_nosync(stream), cmin2.begin(), cmin2.end(),",
        "fields": [
            "cmin2_initial_hash",
            "cmin2_initial_samples",
        ],
        "patch_intent": "hash/sample cmin2 after initialization and before the ray launch mutates payload state",
    },
    {
        "name": "shader_cmax2_abort_status",
        "target": str(SHADER_REL).replace("\\", "/"),
        "anchor": "update_status(ShaderStatus::kAborted);",
        "fields": [
            "status_count_aborted",
            "cmax2_mbr_abort_count",
            "point_loop_early_break_count",
        ],
        "patch_intent": "count shader abort branches separately for MBR cmax2 abort and point-loop early break",
    },
    {
        "name": "shader_offload_append_stream",
        "target": str(SHADER_REL).replace("\\", "/"),
        "anchor": "auto tail = params.offloading_point_ids.Append(in_q_idx);",
        "fields": [
            "raw_offload_rows_before_sort_reduce",
            "raw_offload_row_hash",
            "raw_offload_row_sample_point_ids",
            "raw_offload_row_sample_cell_ids",
            "status_count_offloading",
        ],
        "patch_intent": "hash/sample raw offload point/cell stream at append time before sort/reduce",
    },
    {
        "name": "after_ray_launch_state",
        "target": str(RT_REL).replace("\\", "/"),
        "anchor": "auto offloading_size = offloading_point_ids_.size(stream);",
        "fields": [
            "cmin2_after_ray_hash",
            "cmin2_after_ray_samples",
            "raw_offload_rows_before_sort_reduce",
            "cmax2_after_ray",
        ],
        "patch_intent": "sample cmin2 and offload row stream after OptiX launch before loadBalanceProcessing",
    },
    {
        "name": "load_balance_processing_call",
        "target": str(RT_REL).replace("\\", "/"),
        "anchor": "loadBalanceProcessing(",
        "fields": [
            "load_balance_input_row_count",
            "load_balance_group_count",
            "load_balance_feedback_update_count",
        ],
        "patch_intent": "record input rows and grouped feedback counts around author loadBalanceProcessing",
    },
    {
        "name": "load_balance_cmin2_feedback",
        "target": str(RT_REL).replace("\\", "/"),
        "anchor": "curr_cmin2 = std::min(curr_cmin2, agg_min);",
        "fields": [
            "load_balance_feedback_update_count",
            "cmin2_after_load_balance_hash",
            "cmin2_after_load_balance_samples",
        ],
        "patch_intent": "count cmin2 feedback updates and hash/sample post-load-balance state",
    },
    {
        "name": "miss_and_completed_status_after_raygen",
        "target": str(SHADER_REL).replace("\\", "/"),
        "anchor": "params.miss_queue.Append(point_id_a);",
        "fields": [
            "status_count_miss",
            "status_count_completed",
        ],
        "patch_intent": "count terminal miss/completed statuses in the author raygen result branch",
    },
    {
        "name": "json_iteration_emit",
        "target": str(RT_REL).replace("\\", "/"),
        "anchor": 'json_iter["OffloadingSize"] = total_offloading_size;',
        "fields": [
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
        "patch_intent": "emit the complete v2 trace payload alongside author iteration JSON",
    },
]


def _target_paths(author_root: Path) -> dict[str, Path]:
    return {
        str(LAUNCH_REL).replace("\\", "/"): author_root / LAUNCH_REL,
        str(SHADER_REL).replace("\\", "/"): author_root / SHADER_REL,
        str(RT_REL).replace("\\", "/"): author_root / RT_REL,
    }


def build(*, output: Path, author_root: Path) -> dict[str, Any]:
    goal5385 = _load_json(RESULTS_DIR / "xhd_goal5385_author_trace_v2_spec.json")
    required_fields = list(goal5385["author_trace_v2_schema"]["required_batch_fields"])

    targets = _target_paths(author_root)
    source_texts: dict[str, str] = {}
    missing_files: list[str] = []
    for rel, path in targets.items():
        if path.exists():
            source_texts[rel] = path.read_text(encoding="utf-8")
        else:
            missing_files.append(rel)

    resolved_hooks: list[dict[str, Any]] = []
    covered_fields: set[str] = set()
    missing_hooks: list[str] = []
    for hook in HOOKS:
        rel = hook["target"]
        text = source_texts.get(rel, "")
        line = _line_for_anchor(text, hook["anchor"])
        hook_record = dict(hook)
        hook_record["anchor_line"] = line
        hook_record["anchor_found"] = line is not None
        hook_record["would_patch_author_only"] = True
        resolved_hooks.append(hook_record)
        if line is None:
            missing_hooks.append(hook["name"])
        else:
            covered_fields.update(hook["fields"])

    field_coverage = {
        field: sorted(hook["name"] for hook in resolved_hooks if field in hook["fields"] and hook["anchor_found"])
        for field in required_fields
    }
    uncovered_fields = [field for field, hooks in field_coverage.items() if not hooks]
    all_hooks_found = not missing_files and not missing_hooks

    artifact = {
        "goal": "Goal5386",
        "date": "2026-07-10",
        "schema": SCHEMA,
        "status": "implemented_review_pending",
        "exit_label": (
            "author_trace_v2_patch_plan_ready__implementation_next"
            if all_hooks_found and not uncovered_fields
            else "author_trace_v2_hook_gap_found__revise_spec_or_fail_closed"
        ),
        "purpose": (
            "Validate fail-closed source hook anchors for the Goal5385 author "
            "trace v2 schema before applying a live author patch."
        ),
        "author_root": str(author_root),
        "goal5385_schema": goal5385["author_trace_v2_schema"]["name"],
        "patch_plan": {
            "instrumentation_marker": MARKER,
            "targets": [
                {
                    "path": rel,
                    "exists": rel not in missing_files,
                    "owner": "paper_app_author_instrumentation",
                }
                for rel in sorted(targets)
            ],
            "hooks": resolved_hooks,
            "all_hooks_found": all_hooks_found,
            "missing_files": missing_files,
            "missing_hooks": missing_hooks,
        },
        "field_coverage": {
            "required_batch_fields": required_fields,
            "coverage_by_field": field_coverage,
            "uncovered_fields": uncovered_fields,
            "all_required_fields_covered": not uncovered_fields,
        },
        "implementation_status": {
            "dry_run_patch_plan_ready": all_hooks_found and not uncovered_fields,
            "author_v2_trace_implemented": False,
            "author_v2_trace_executed_on_pod": False,
            "patch_applied_to_author_tree": False,
            "rtdl_core_patched": False,
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
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--author-root", type=Path, default=_default_author_root())
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS_DIR / "xhd_goal5386_author_trace_v2_patch_plan.json",
    )
    args = parser.parse_args()
    artifact = build(output=args.output, author_root=args.author_root)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "exit_label": artifact["exit_label"],
                "all_hooks_found": artifact["patch_plan"]["all_hooks_found"],
                "all_required_fields_covered": artifact["field_coverage"]["all_required_fields_covered"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
