from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5387_author_trace_v2_execution.json"

AUTHOR_TRACE_V2 = RESULTS / "xhd_goal5387_author_lb256_status_trace_v2_pod.json"
PATCH_SUMMARY_V2 = RESULTS / "xhd_goal5387_author_trace_v2_patch_summary_pod.json"
GOAL5374_ORACLE = RESULTS / "xhd_goal5374_author_lb_status_trace_oracle.json"
GOAL5385_SPEC = RESULTS / "xhd_goal5385_author_trace_v2_spec.json"
GOAL5386_PLAN = RESULTS / "xhd_goal5386_author_trace_v2_patch_plan.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _repeat(payload: dict[str, Any]) -> dict[str, Any]:
    return payload["Running"]["Repeats"][0]


def _iterations(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return list(_repeat(payload)["Iterations"])


def _iteration(payload: dict[str, Any], iteration_index: int) -> dict[str, Any]:
    for item in _iterations(payload):
        if int(item["Iteration"]) == iteration_index:
            return item
    raise RuntimeError(f"missing author iteration {iteration_index}")


def _trace_v2(iteration: dict[str, Any]) -> dict[str, Any]:
    trace = iteration.get("LBTraceV2")
    if not isinstance(trace, dict):
        raise RuntimeError("author iteration is missing LBTraceV2")
    return trace


def _batch(trace: dict[str, Any]) -> dict[str, Any]:
    batches = trace.get("Batches") or []
    if len(batches) != 1:
        raise RuntimeError(f"expected exactly one LBTraceV2 batch, got {len(batches)}")
    return dict(batches[0])


def build(output: Path = OUT) -> dict[str, Any]:
    author_trace = _read_json(AUTHOR_TRACE_V2)
    patch_summary = _read_json(PATCH_SUMMARY_V2)
    goal5374 = _read_json(GOAL5374_ORACLE)
    goal5385 = _read_json(GOAL5385_SPEC)
    goal5386 = _read_json(GOAL5386_PLAN)

    iter3 = _iteration(author_trace, 3)
    trace = _trace_v2(iter3)
    batch = _batch(trace)

    active = int(trace["ActiveInQueueSize"])
    raw_rows = int(trace["RawOffloadRowsBeforeSortReduce"])
    status_offload = int(trace["StatusOffloadingAppendCount"])
    status_init = int(trace["StatusInitCount"])
    offloading_size = int(iter3["OffloadingSize"])

    goal5374_trace = goal5374["author_lb_trace"]
    old_raw_rows = int(goal5374_trace["raw_offload_rows_before_sort_reduce"])
    old_active = int(goal5374_trace["active_in_queue_size"])
    old_status_offload = int(goal5374_trace["status_count_offloading_append"])
    old_offloading_size = int(goal5374["author_result"]["iteration_3"]["OffloadingSize"])

    required_batch_fields = list(goal5385["author_trace_v2_schema"]["required_batch_fields"])
    batch_field_presence = {field: field in batch for field in required_batch_fields}
    all_required_batch_fields_present = all(batch_field_presence.values())

    sample_fields_present = all(
        bool(batch.get(name))
        for name in (
            "cmin2_initial_samples",
            "cmin2_after_ray_samples",
            "cmin2_after_load_balance_samples",
            "raw_offload_row_sample_point_ids",
            "raw_offload_row_sample_cell_ids",
        )
    )
    hash_fields_present = all(
        isinstance(batch.get(name), int)
        for name in (
            "cmin2_initial_hash",
            "cmin2_after_ray_hash",
            "cmin2_after_load_balance_hash",
            "raw_offload_row_hash",
        )
    )

    count_parity = {
        "active_matches_goal5374": active == old_active == 437645,
        "offloading_size_matches_goal5374": offloading_size == old_offloading_size == 27133990,
        "raw_rows_matches_goal5374": raw_rows == old_raw_rows == 27133990,
        "status_offload_matches_raw_rows": status_offload == raw_rows == 27133990,
        "status_init_matches_active": status_init == active == 437645,
    }

    return {
        "goal": "Goal5387",
        "date": "2026-07-10",
        "schema": "rtdl.paper_reproduction.xhd.goal5387.author_trace_v2_execution.v1",
        "status": "author_trace_v2_executed_on_pod__rtdl_counterpart_next",
        "exit_label": "author_trace_v2_oracle_ready__native_counterpart_next",
        "purpose": (
            "Execute the app-owned author trace v2 instrumentation on the "
            "Dragon -> AsianDragon lb=256 Level-B diagnostic, producing a "
            "stronger status-machine oracle for the next RTDL counterpart."
        ),
        "input_artifacts": {
            "author_trace_v2_pod": str(AUTHOR_TRACE_V2),
            "patch_summary_v2_pod": str(PATCH_SUMMARY_V2),
            "goal5374_author_oracle": str(GOAL5374_ORACLE),
            "goal5385_trace_v2_spec": str(GOAL5385_SPEC),
            "goal5386_patch_plan": str(GOAL5386_PLAN),
        },
        "pod": {
            "host": "213.173.108.24",
            "port": 13502,
            "wrapper": "scripts/current_pod_ssh.py",
            "hostname": "45c502cfccb5",
            "gpu": author_trace["GPU"]["name"],
        },
        "author_instrumentation": {
            "patch_schema": patch_summary["schema"],
            "trace_schema": patch_summary["trace_schema"],
            "marker": patch_summary["marker"],
            "changed": patch_summary["changed"],
            "author_root": patch_summary["author_root"],
            "binary": "/tmp/xhd-goal5387/build-gcc11-optix77-fast/bin/hd_exec",
            "source_copy": "/tmp/xhd-goal5387/author",
            "source_modified_in_pod_only": True,
            "rtdl_core_modified": False,
            "goal5386_all_hooks_found": bool(goal5386["patch_plan"]["all_hooks_found"]),
            "goal5386_all_required_fields_covered": bool(
                goal5386["field_coverage"]["all_required_fields_covered"]
            ),
        },
        "input_scope": {
            "input1": author_trace["Input"]["Files"][0]["Path"],
            "input2": author_trace["Input"]["Files"][1]["Path"],
            "input1_num_points": int(author_trace["Input"]["Files"][0]["NumPoints"]),
            "input2_num_points": int(author_trace["Input"]["Files"][1]["NumPoints"]),
            "level": "level_b_public_dragon_asian_author_only_diagnostic",
            "exact_paper_dataset_identity_proven": False,
        },
        "author_result": {
            "HDResult": float(author_trace["HDResult"]),
            "AvgTime_ms": float(author_trace["Running"]["AvgTime"]),
            "LB": int(author_trace["Running"]["LB"]),
            "iteration_count": len(_iterations(author_trace)),
            "iteration_3": {
                "Radius": float(iter3["Radius"]),
                "RTTime_ms": float(iter3["RTTime"]),
                "CUDATime_ms": float(iter3["CUDATime"]),
                "ComparedPoints": int(iter3["ComparedPoints"]),
                "Hits": int(iter3["Hits"]),
                "OffloadingSize": offloading_size,
            },
        },
        "author_lb_trace_v2": {
            "schema": trace["Schema"],
            "active_in_queue_size": active,
            "raw_offload_rows_before_sort_reduce": raw_rows,
            "status_count_init": status_init,
            "status_count_offloading_append": status_offload,
            "status_count_miss": int(trace["StatusMissCount"]),
            "status_count_completed": int(trace["StatusCompletedCount"]),
            "status_count_aborted": int(trace["StatusAbortedCount"]),
            "status_count_cmax2_mbr_abort": int(trace["StatusCmax2MbrAbortCount"]),
            "status_count_point_loop_early_break": int(trace["StatusPointLoopEarlyBreakCount"]),
            "load_balance_feedback_update_count": int(trace["LoadBalanceFeedbackUpdateCount"]),
            "batch_count": len(trace.get("Batches") or []),
            "batch_0": batch,
        },
        "field_validation": {
            "required_batch_fields": required_batch_fields,
            "batch_field_presence": batch_field_presence,
            "all_required_batch_fields_present": bool(all_required_batch_fields_present),
            "hash_fields_present": bool(hash_fields_present),
            "sample_fields_present": bool(sample_fields_present),
        },
        "comparison_to_goal5374": {
            "count_parity": count_parity,
            "all_core_counts_match_goal5374": bool(all(count_parity.values())),
            "goal5374_raw_rows": old_raw_rows,
            "goal5374_active_in_queue_size": old_active,
            "goal5374_status_offload": old_status_offload,
            "goal5374_offloading_size": old_offloading_size,
        },
        "decision": {
            "author_trace_v2_oracle_ready": bool(
                all(count_parity.values())
                and all_required_batch_fields_present
                and hash_fields_present
                and sample_fields_present
            ),
            "next_gate": "rtdl_native_multi_round_status_stream_against_author_trace_v2",
            "recommended_next_goal": "Goal5388 or successor: RTDL native counterpart against Goal5387 oracle",
        },
        "claim_boundary": {
            "author_v2_trace_implemented": True,
            "author_v2_trace_executed_on_pod": True,
            "author_v2_trace_oracle_claimed": True,
            "explicit_lb_support_claimed": False,
            "rtdl_row_count_parity_claimed": False,
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
    payload = build()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
