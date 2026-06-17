from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.rtnn_chunked_runtime.goal4506.v1"
RAW_EVIDENCE = Path("docs/reports/goal4506_rtnn_chunked_uniform_1048576q1048576_w1r3_2026-06-17.json")
OUT_JSON = Path("docs/reports/goal4506_v3_0_m110_rtnn_chunked_runtime_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4506_v3_0_m110_rtnn_chunked_runtime_2026-06-17.md")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    raw = _read_json(root / RAW_EVIDENCE)
    validation = rt.validate_v3_m19_ranked_summary_bridge_chunked_payload(raw["runner_payload"])
    compact = raw["compact_summary"]
    cupy = compact["partner_rows"]["cupy"]
    numba = compact["partner_rows"]["numba"]
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4506 / V3 M110",
        "raw_evidence": RAW_EVIDENCE.as_posix(),
        "mode": compact["mode"],
        "input": {
            "point_count": int(compact["point_count"]),
            "query_count": int(compact["query_count"]),
            "distribution": compact["distribution"],
            "warmups": int(compact["warmups"]),
            "repeats": int(compact["repeats"]),
            "chunk_count": int(compact["chunk_count"]),
            "max_query_count": int(compact["max_query_count"]),
        },
        "validation": validation,
        "runtime": {
            "chunked_runtime_executed": True,
            "prepared_scene_reused_across_chunks": bool(compact["prepared_scene_reused_across_chunks"]),
            "signature_match": bool(compact["signature_match"]),
            "hot_no_hidden_column_copy_ready": bool(compact["hot_no_hidden_column_copy_ready"]),
            "device_result_materialization_after_hot_window": bool(
                compact["device_result_materialization_after_hot_window"]
            ),
            "cupy_hot_device_run_seconds_median_sum": float(cupy["hot_device_run_seconds_median_sum"]),
            "numba_hot_device_run_seconds_median_sum": float(numba["hot_device_run_seconds_median_sum"]),
            "cupy_materialize_seconds_median_sum": float(cupy["materialize_seconds_median_sum"]),
            "numba_materialize_seconds_median_sum": float(numba["materialize_seconds_median_sum"]),
            "cupy_chunk_hot_medians": tuple(float(value) for value in cupy["chunk_hot_device_run_seconds_medians"]),
            "numba_chunk_hot_medians": tuple(float(value) for value in numba["chunk_hot_device_run_seconds_medians"]),
        },
        "toolchain": {
            "numba_toolchain": raw["runner_numba_cuda_home"],
            "transfer_counter_bootstrap": raw["runner_transfer_counter_bootstrap"],
        },
        "claim_boundary": {
            "large_chunked_runtime_evidence": True,
            "planner_only": False,
            "same_stream_partner_continuation_evidence": True,
            "aggregate_only_full_batch_direct_comparison_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
        "conclusion": (
            "The M19 RTNN partner-continuation route now has measured chunked runtime evidence "
            "on a 1,048,576-query uniform workload. The route executed 16 explicit 65,536-query "
            "chunks, reused the prepared scene across chunks, prepared query points and CUDA graph "
            "state per chunk, ran both CuPy and Numba same-stream device reductions, matched "
            "combined signatures, and kept result materialization after the hot window. This does "
            "not authorize public speedup wording or comparison against the aggregate-only "
            "full-batch direct route because the output contracts differ."
        ),
    }


def _fmt(value: float) -> str:
    return f"{value:.6f}s"


def write_report(packet: dict[str, Any], path: Path) -> None:
    runtime = packet["runtime"]
    input_row = packet["input"]
    lines = [
        "# Goal4506 / V3 M110 RTNN Chunked Runtime",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Measured Row",
        "",
        "| Field | Value |",
        "| --- | ---: |",
        f"| raw evidence | `{packet['raw_evidence']}` |",
        f"| point/query count | {input_row['query_count']:,} |",
        f"| chunk count | {input_row['chunk_count']} |",
        f"| max query count per chunk | {input_row['max_query_count']:,} |",
        f"| warmups / repeats | {input_row['warmups']} / {input_row['repeats']} |",
        f"| CuPy hot median-sum | {_fmt(runtime['cupy_hot_device_run_seconds_median_sum'])} |",
        f"| Numba hot median-sum | {_fmt(runtime['numba_hot_device_run_seconds_median_sum'])} |",
        f"| signature match | `{runtime['signature_match']}` |",
        f"| no-hidden-column-copy hot gate | `{runtime['hot_no_hidden_column_copy_ready']}` |",
        f"| materialization after hot window | `{runtime['device_result_materialization_after_hot_window']}` |",
        "",
        "## Boundary",
        "",
        "- This is large chunked runtime evidence for the same-stream partner-continuation route.",
        "- It is not aggregate-only full-batch direct evidence and must not be compared as the same output contract.",
        "- Public speedup, RT-core speedup, whole-app speedup, true-zero-copy, and automatic partner-selection claims remain blocked.",
        "- The Numba toolchain is auto-configured through `configure_numba_cuda_toolchain_environment()` so the pod uses CUDA 12.4 ptxas/NVVM instead of emitting unsupported PTX 8.7.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["runtime"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
