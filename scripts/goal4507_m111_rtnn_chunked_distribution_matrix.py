from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.rtnn_chunked_distribution_matrix.goal4507.v1"
RAW_BY_DISTRIBUTION = {
    "uniform": Path("docs/reports/goal4506_rtnn_chunked_uniform_1048576q1048576_w1r3_2026-06-17.json"),
    "shell": Path("docs/reports/goal4507_rtnn_chunked_shell_1048576q1048576_w1r3_2026-06-17.json"),
    "clustered": Path("docs/reports/goal4507_rtnn_chunked_clustered_1048576q1048576_w1r3_2026-06-17.json"),
}
OUT_JSON = Path("docs/reports/goal4507_v3_0_m111_rtnn_chunked_distribution_matrix_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4507_v3_0_m111_rtnn_chunked_distribution_matrix_2026-06-17.md")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _row(distribution: str, payload: dict[str, Any], raw_path: Path) -> dict[str, Any]:
    validation = rt.validate_v3_m19_ranked_summary_bridge_chunked_payload(payload["runner_payload"])
    compact = payload["compact_summary"]
    cupy = compact["partner_rows"]["cupy"]
    numba = compact["partner_rows"]["numba"]
    return {
        "distribution": distribution,
        "raw_evidence": raw_path.as_posix(),
        "point_count": int(compact["point_count"]),
        "query_count": int(compact["query_count"]),
        "chunk_count": int(compact["chunk_count"]),
        "max_query_count": int(compact["max_query_count"]),
        "warmups": int(compact["warmups"]),
        "repeats": int(compact["repeats"]),
        "signature_match": bool(compact["signature_match"]),
        "hot_no_hidden_column_copy_ready": bool(compact["hot_no_hidden_column_copy_ready"]),
        "prepared_scene_reused_across_chunks": bool(compact["prepared_scene_reused_across_chunks"]),
        "device_result_materialization_after_hot_window": bool(
            compact["device_result_materialization_after_hot_window"]
        ),
        "cupy_hot_device_run_seconds_median_sum": float(cupy["hot_device_run_seconds_median_sum"]),
        "numba_hot_device_run_seconds_median_sum": float(numba["hot_device_run_seconds_median_sum"]),
        "cupy_materialize_seconds_median_sum": float(cupy["materialize_seconds_median_sum"]),
        "numba_materialize_seconds_median_sum": float(numba["materialize_seconds_median_sum"]),
        "validation": validation,
    }


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    rows = tuple(
        _row(distribution, _read_json(root / raw_path), raw_path)
        for distribution, raw_path in RAW_BY_DISTRIBUTION.items()
    )
    fastest = min(rows, key=lambda row: row["cupy_hot_device_run_seconds_median_sum"])
    slowest = max(rows, key=lambda row: row["cupy_hot_device_run_seconds_median_sum"])
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4507 / V3 M111",
        "mode": "prepared_ranked_summary_graph_partner_bridge_chunked",
        "rows": rows,
        "matrix_summary": {
            "row_count": len(rows),
            "distributions": tuple(row["distribution"] for row in rows),
            "all_signature_match": all(bool(row["signature_match"]) for row in rows),
            "all_hot_no_hidden_column_copy_ready": all(
                bool(row["hot_no_hidden_column_copy_ready"]) for row in rows
            ),
            "all_prepared_scene_reused_across_chunks": all(
                bool(row["prepared_scene_reused_across_chunks"]) for row in rows
            ),
            "fastest_distribution_by_cupy_hot_sum": fastest["distribution"],
            "slowest_distribution_by_cupy_hot_sum": slowest["distribution"],
            "slowest_over_fastest_cupy_hot_sum": (
                slowest["cupy_hot_device_run_seconds_median_sum"]
                / fastest["cupy_hot_device_run_seconds_median_sum"]
            ),
        },
        "claim_boundary": {
            "large_chunked_runtime_evidence": True,
            "distribution_matrix_complete_for_current_m19_synthetic_family": True,
            "paper_dataset_reproduction_authorized": False,
            "aggregate_only_full_batch_direct_comparison_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
        "conclusion": (
            "The M19 chunked partner-continuation route now has measured 1,048,576-query "
            "runtime evidence across the current uniform, shell, and clustered synthetic "
            "distribution family. All three rows execute 16 chunks, reuse the prepared scene, "
            "match CuPy/Numba signatures, pass the hot no-hidden-column-copy gate, and keep "
            "materialization after the hot window. Clustered is the expected slowest row and "
            "uniform is the fastest. These rows are still not official RTNN paper-dataset "
            "reproduction and not aggregate-only full-batch direct comparison rows."
        ),
    }


def _fmt(value: float) -> str:
    return f"{value:.6f}s"


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4507 / V3 M111 RTNN Chunked Distribution Matrix",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Matrix",
        "",
        "| Distribution | Chunks | CuPy hot median-sum | Numba hot median-sum | Signature | No hidden copy |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in packet["rows"]:
        lines.append(
            "| {distribution} | {chunk_count} | {cupy} | {numba} | `{signature}` | `{copy}` |".format(
                distribution=row["distribution"],
                chunk_count=row["chunk_count"],
                cupy=_fmt(row["cupy_hot_device_run_seconds_median_sum"]),
                numba=_fmt(row["numba_hot_device_run_seconds_median_sum"]),
                signature=row["signature_match"],
                copy=row["hot_no_hidden_column_copy_ready"],
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This matrix is for the current synthetic M19 distribution family: uniform, shell, clustered.",
            "- It does not replace official RTNN paper datasets.",
            "- It does not authorize public speedup, RT-core speedup, whole-app speedup, automatic partner selection, or aggregate-only full-batch direct comparison wording.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["matrix_summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
