from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
OUT = RESULTS / "xhd_goal5374_author_lb_status_trace_oracle.json"

AUTHOR_TRACE = RESULTS / "xhd_goal5374_author_lb256_status_trace_pod.json"
PATCH_SUMMARY = RESULTS / "xhd_goal5374_author_instrument_patch_summary_pod.json"
GOAL5364 = RESULTS / "xhd_goal5364_lb_trace_gate_author_pair_contract.json"
GOAL5371 = RESULTS / "xhd_goal5371_inline_global_bound_lb_probe.json"
GOAL5373 = RESULTS / "xhd_goal5373_rtdl_status_machine_telemetry_surface.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _repeat(payload: dict[str, Any]) -> dict[str, Any]:
    return payload["Running"]["Repeats"][0]


def _iterations(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return list(_repeat(payload)["Iterations"])


def build_artifact() -> dict[str, Any]:
    author_trace = _read_json(AUTHOR_TRACE)
    patch = _read_json(PATCH_SUMMARY)
    goal5364 = _read_json(GOAL5364)
    goal5371 = _read_json(GOAL5371)
    goal5373 = _read_json(GOAL5373)

    iterations = _iterations(author_trace)
    if len(iterations) < 3:
        raise RuntimeError("expected at least three author iterations")
    iter3 = iterations[2]
    trace = iter3.get("LBTrace")
    if not isinstance(trace, dict):
        raise RuntimeError("instrumented author iteration 3 is missing LBTrace")

    offloading_size = int(iter3["OffloadingSize"])
    raw_rows = int(trace["RawOffloadRowsBeforeSortReduce"])
    author_width_bytes = int(trace["RawOffloadRowsAuthorWidthBytes"])
    status_offload = int(trace["StatusOffloadingAppendCount"])
    cmax2_abort = int(trace["StatusCmax2MbrAbortCount"])
    point_loop_abort = int(trace["StatusPointLoopEarlyBreakCount"])
    active = int(trace["ActiveInQueueSize"])
    init_count = int(trace["StatusInitCount"])

    expected_author_rows = int(goal5364["author_pair"]["lb_256"]["iteration_3"]["OffloadingSize"])
    expected_author_width = int(goal5364["author_pair"]["lb_256"]["memory"]["WL Heavy Peak"])
    rtdl_inline_rows = int(goal5371["comparison"]["rtdl_author_radius_inline_count_only_kind2_rows"])
    rtdl_noinline_rows = int(goal5371["comparison"]["rtdl_author_radius_noinline_raw_kind2_rows_from_goal5368"])

    row_parity = raw_rows == offloading_size == expected_author_rows == status_offload
    width_parity = author_width_bytes == expected_author_width == raw_rows * 2 * 4
    active_parity = active == init_count == int(iter3["NumInputPoints"])

    return {
        "goal": "Goal5374",
        "date": "2026-07-09",
        "schema": "rtdl.paper_reproduction.xhd.goal5374.author_lb_status_trace_oracle.v1",
        "status": "author_lb_status_trace_oracle_ready__rtdl_status_machine_counterpart_missing",
        "exit_label": "author_oracle_ready__next_rtdl_status_machine_counterpart",
        "purpose": (
            "Instrument the author X-HD RT path to emit raw lb status-machine "
            "trace fields for the Dragon -> AsianDragon lb=256 Level-B diagnostic."
        ),
        "input_artifacts": {
            "author_trace": str(AUTHOR_TRACE),
            "patch_summary": str(PATCH_SUMMARY),
            "goal5364_author_pair_contract": str(GOAL5364),
            "goal5371_rtdl_count_probe": str(GOAL5371),
            "goal5373_rtdl_surface_audit": str(GOAL5373),
        },
        "pod": {
            "host": "213.173.108.24",
            "port": 13502,
            "wrapper": "scripts/current_pod_ssh.py",
            "gpu": author_trace["GPU"]["name"],
        },
        "author_instrumentation": {
            "patch_schema": patch["schema"],
            "marker": patch["marker"],
            "patched": bool(patch["patched"]),
            "changed": patch["changed"],
            "author_root": patch["author_root"],
            "binary": "/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec",
            "source_modified_in_pod_only": True,
            "rtdl_core_modified": False,
        },
        "input_scope": {
            "input1": author_trace["Input"]["Files"][0]["Path"],
            "input2": author_trace["Input"]["Files"][1]["Path"],
            "input1_num_points": int(author_trace["Input"]["Files"][0]["NumPoints"]),
            "input2_num_points": int(author_trace["Input"]["Files"][1]["NumPoints"]),
            "level": "level_b_temporary_input_author_only_diagnostic",
            "exact_paper_dataset_identity_proven": False,
        },
        "author_result": {
            "HDResult": float(author_trace["HDResult"]),
            "AvgTime_ms": float(author_trace["Running"]["AvgTime"]),
            "LB": int(author_trace["Running"]["LB"]),
            "iteration_3": {
                "Radius": float(iter3["Radius"]),
                "NumInputPoints": int(iter3["NumInputPoints"]),
                "NumOutputPoints": int(iter3["NumOutputPoints"]),
                "RTTime_ms": float(iter3["RTTime"]),
                "CUDATime_ms": float(iter3["CUDATime"]),
                "ComparedPoints": int(iter3["ComparedPoints"]),
                "Hits": int(iter3["Hits"]),
                "OffloadingSize": offloading_size,
            },
        },
        "author_lb_trace": {
            "schema": trace["Schema"],
            "active_in_queue_size": active,
            "raw_offload_rows_before_sort_reduce": raw_rows,
            "raw_offload_rows_author_width_bytes": author_width_bytes,
            "status_count_init": init_count,
            "status_count_offloading_append": status_offload,
            "status_count_cmax2_mbr_abort": cmax2_abort,
            "status_count_point_loop_early_break": point_loop_abort,
            "batch_count": len(trace.get("Batches") or []),
            "batches": trace.get("Batches") or [],
        },
        "comparison": {
            "author_trace_row_parity": bool(row_parity),
            "author_width_parity": bool(width_parity),
            "active_in_queue_parity": bool(active_parity),
            "author_offloading_size_rows": expected_author_rows,
            "author_wl_heavy_peak_bytes": expected_author_width,
            "rtdl_inline_kind2_rows_from_goal5371": rtdl_inline_rows,
            "rtdl_noinline_kind2_rows_from_goal5371": rtdl_noinline_rows,
            "rtdl_inline_div_author_trace_rows": rtdl_inline_rows / raw_rows,
            "rtdl_noinline_div_author_trace_rows": rtdl_noinline_rows / raw_rows,
            "rtdl_counterpart_row_parity": False,
            "rtdl_surface_ready_from_goal5373": bool(
                goal5373["coverage_summary"]["ready_for_author_shader_status_machine_lb_trace"]
            ),
        },
        "decision": {
            "author_oracle_ready": bool(row_parity and width_parity and active_parity),
            "explicit_lb_support_authorized": False,
            "next_gate": "rtdl_status_machine_counterpart_against_author_oracle",
            "recommended_next_goal": "Goal5375 rtdl_status_machine_counterpart_against_goal5374_author_oracle",
        },
        "claim_boundary": {
            "author_oracle_claimed": True,
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
    payload = build_artifact()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
