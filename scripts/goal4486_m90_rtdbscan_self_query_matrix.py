from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import time

from examples.current.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    run_rt_dbscan_benchmark,
)


POINT_COUNT = 1_048_576
OUT_JSON = Path("docs/reports/goal4486_v3_0_m90_rtdbscan_self_query_count_threshold_1m_2026-06-17.json")
OUT_JSONL = Path("docs/reports/goal4486_v3_0_m90_rtdbscan_self_query_count_threshold_1m_2026-06-17.jsonl")
BASELINE_PACKET = Path("docs/reports/goal4485_v3_0_m89_rtdbscan_1m_compact_signature_matrix_2026-06-16.json")


def _gpu_info() -> str:
    try:
        return subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total,pci.bus_id",
                "--format=csv,noheader",
            ],
            text=True,
        ).strip()
    except Exception as exc:  # pragma: no cover - pod evidence helper
        return f"unavailable: {exc}"


def _load_m89_predicate_rows() -> dict[tuple[str, str], dict[str, object]]:
    packet = json.loads(BASELINE_PACKET.read_text(encoding="utf-8"))
    rows: dict[tuple[str, str], dict[str, object]] = {}
    for row in packet["rows"]:
        case = row.get("case", {})
        if row.get("status") == "ok" and case.get("mode_key") == "predicate_direct_status":
            rows[(case.get("dataset"), case.get("protocol"))] = row
    return rows


def _cases() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for dataset in ("clustered3d", "road3d", "ngsim_dense"):
        rows.append({"dataset": dataset, "protocol": "one_shot_no_warmup", "repeat": 1, "warmup": 0})
        rows.append({"dataset": dataset, "protocol": "warmed_replay", "repeat": 3, "warmup": 1})
    return rows


def _metric_for_protocol(row: dict[str, object], protocol: str, *, source: str) -> float:
    if protocol == "one_shot_no_warmup":
        if source == "payload_metadata":
            return float(row["metadata"]["prepare_plus_replay_median_sec"])
        return float(row["prepare_plus_replay_sec"])
    return float(row["elapsed_sec"])


def run_matrix() -> dict[str, object]:
    old_by_key = _load_m89_predicate_rows()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSONL.write_text("", encoding="utf-8")

    rows: list[dict[str, object]] = []
    for case in _cases():
        start = time.perf_counter()
        try:
            payload = run_rt_dbscan_benchmark(
                mode="optix_rt_core_flags_cupy_predicate_direct_status_column_signature_3d",
                dataset=str(case["dataset"]),
                point_count=POINT_COUNT,
                radius=None,
                min_neighbors=None,
                seed=20260519,
                partner="cupy",
                repeat=int(case["repeat"]),
                warmup=int(case["warmup"]),
                validate=False,
                include_rows=False,
            )
            metadata = payload["metadata"]
            threshold = dict(metadata.get("threshold_metadata") or {})
            native = dict(threshold.get("native_metadata") or {})
            old = old_by_key[(str(case["dataset"]), str(case["protocol"]))]
            old_metric = _metric_for_protocol(old, str(case["protocol"]), source="m89_packet")
            new_metric = _metric_for_protocol(payload, str(case["protocol"]), source="payload_metadata")
            signature_match_m89 = json.dumps(payload["signature"], sort_keys=True) == json.dumps(
                old["signature"],
                sort_keys=True,
            )
            row = {
                "status": "ok",
                "case": {
                    **case,
                    "mode_key": "predicate_direct_status_self_query",
                    "point_count": POINT_COUNT,
                },
                "elapsed_sec": float(payload["elapsed_sec"]),
                "prepare_plus_replay_sec": float(metadata["prepare_plus_replay_median_sec"]),
                "prepare_sec": float(metadata["prepared_predicate_direct_status_plus_count_prepare_sec"]),
                "rt_native_current_run_sec": float(
                    (metadata.get("timing_breakdown_sec") or {}).get("optix_rt_count_threshold_sec", 0.0)
                ),
                "signature": payload["signature"],
                "signature_matches_m89": signature_match_m89,
                "m89_metric_sec": old_metric,
                "m90_metric_sec": new_metric,
                "m90_vs_m89_speedup": old_metric / new_metric if new_metric > 0 else None,
                "m90_minus_m89_sec": new_metric - old_metric,
                "metadata_focus": {
                    "path": metadata.get("path"),
                    "native_engine_summary_contract": metadata.get("native_engine_summary_contract"),
                    "native_execution_path": metadata.get("native_execution_path"),
                    "prepared_optix_count_threshold_sec": metadata.get("prepared_optix_count_threshold_sec"),
                    "prepared_predicate_direct_status_sec": metadata.get("prepared_predicate_direct_status_sec"),
                    "prepared_predicate_direct_status_plus_count_prepare_sec": metadata.get(
                        "prepared_predicate_direct_status_plus_count_prepare_sec"
                    ),
                    "prepare_plus_replay_median_sec": metadata.get("prepare_plus_replay_median_sec"),
                    "timing_breakdown_sec": metadata.get("timing_breakdown_sec"),
                    "threshold_adapter": threshold.get("adapter"),
                    "threshold_input_contract": threshold.get("input_contract"),
                    "threshold_native_contract": threshold.get("native_engine_row_contract"),
                    "threshold_transfer_mode": native.get("transfer_mode"),
                    "threshold_query_source": native.get("query_source"),
                    "threshold_host_query_point_repack_avoided": native.get("host_query_point_repack_avoided"),
                    "threshold_host_query_point_upload_avoided": native.get("host_query_point_upload_avoided"),
                    "threshold_native_elapsed_sec": native.get("native_elapsed_sec"),
                    "rt_core_accelerated": metadata.get("rt_core_accelerated"),
                    "materializes_python_rows": metadata.get("materializes_python_rows"),
                },
                "wall_sec": time.perf_counter() - start,
            }
        except Exception as exc:  # pragma: no cover - pod evidence helper
            row = {
                "status": "error",
                "case": case,
                "error": repr(exc),
                "wall_sec": time.perf_counter() - start,
            }
        rows.append(row)
        with OUT_JSONL.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        print(
            json.dumps(
                {
                    "case": case,
                    "status": row["status"],
                    "elapsed_sec": row.get("elapsed_sec"),
                    "prepare_plus": row.get("prepare_plus_replay_sec"),
                    "speedup": row.get("m90_vs_m89_speedup"),
                },
                sort_keys=True,
            ),
            flush=True,
        )

    ok_rows = [row for row in rows if row["status"] == "ok"]
    packet = {
        "version": "rtdl.v3_0.rtdbscan_self_query_count_threshold_1m.goal4486.v1",
        "point_count": POINT_COUNT,
        "case_count": len(rows),
        "ok_count": sum(1 for row in rows if row["status"] == "ok"),
        "error_count": sum(1 for row in rows if row["status"] != "ok"),
        "hardware": _gpu_info(),
        "env": {
            name: os.environ.get(name)
            for name in ("RTDL_OPTIX_LIBRARY", "CUDA_HOME", "NUMBA_CUDA_PREFIX")
        },
        "baseline_packet": str(BASELINE_PACKET),
        "change": (
            "generic prepared OptiX 3D fixed-radius count-threshold self-query "
            "device-output primitive; RT-DBSCAN predicate route uses it for "
            "self-query workloads"
        ),
        "summary": {
            "all_signatures_match_m89": all(bool(row.get("signature_matches_m89")) for row in ok_rows),
            "speedups_vs_m89": {
                f"{row['case']['dataset']}:{row['case']['protocol']}": row.get("m90_vs_m89_speedup")
                for row in ok_rows
            },
            "transfer_modes": sorted({row["metadata_focus"]["threshold_transfer_mode"] for row in ok_rows}),
            "query_sources": sorted({row["metadata_focus"]["threshold_query_source"] for row in ok_rows}),
            "host_query_upload_avoided_all": all(
                bool(row["metadata_focus"]["threshold_host_query_point_upload_avoided"])
                for row in ok_rows
            ),
        },
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(packet["summary"], indent=2, sort_keys=True), flush=True)
    return packet


if __name__ == "__main__":
    run_matrix()
