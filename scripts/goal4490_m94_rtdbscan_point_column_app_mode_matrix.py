from __future__ import annotations

import json
from pathlib import Path
import subprocess
import time

from examples.benchmark_apps.rt_dbscan import rtdl_rt_dbscan_benchmark_app as app


POINT_COUNT = 1_048_576
PARTITION_CELL_FACTOR = 0.25
PROTOCOLS = (
    {"name": "one_shot", "repeat": 1, "warmup": 0},
    {"name": "warm_replay", "repeat": 3, "warmup": 1},
)
OUT_JSON = Path("docs/reports/goal4490_v3_0_m94_rtdbscan_point_column_app_mode_2026-06-17.json")
OUT_JSONL = Path("docs/reports/goal4490_v3_0_m94_rtdbscan_point_column_app_mode_2026-06-17.jsonl")


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


def _case(dataset: str, mode: str, *, protocol: dict[str, object]) -> dict[str, object]:
    repeat = int(protocol["repeat"])
    warmup = int(protocol["warmup"])
    start = time.perf_counter()
    payload = app.run_rt_dbscan_benchmark(
        mode=mode,
        dataset=dataset,
        point_count=POINT_COUNT,
        radius=None,
        min_neighbors=None,
        seed=20260519,
        partner="cupy",
        include_rows=False,
        validate=False,
        partition_cell_factor=PARTITION_CELL_FACTOR,
        direct_status_convergence_mode="single_pass_candidate",
        repeat=repeat,
        warmup=warmup,
    )
    wall_sec = time.perf_counter() - start
    metadata = dict(payload["metadata"])
    timing = dict(metadata.get("timing_breakdown_sec", {}))
    protocol_summary = dict(metadata.get("prepared_query_repeat_protocol", {}))
    return {
        "status": "ok",
        "dataset": dataset,
        "mode": mode,
        "protocol": protocol["name"],
        "point_count": POINT_COUNT,
        "partition_cell_factor": PARTITION_CELL_FACTOR,
        "repeat": repeat,
        "warmup": warmup,
        "wall_sec": wall_sec,
        "elapsed_sec": payload["elapsed_sec"],
        "signature": payload["signature"],
        "metadata": {
            "path": metadata.get("path"),
            "native_execution_path": metadata.get("native_execution_path"),
            "point_coordinate_columns_source": metadata.get("point_coordinate_columns_source"),
            "point_coordinate_column_helper": metadata.get("point_coordinate_column_helper"),
            "point_coordinate_column_build_sec": metadata.get("point_coordinate_column_build_sec"),
            "point_coordinate_column_build_charged_in_total": metadata.get("point_coordinate_column_build_charged_in_total"),
            "prepared_predicate_direct_status_sec": metadata.get("prepared_predicate_direct_status_sec"),
            "charged_predicate_direct_status_prepare_sec": metadata.get("charged_predicate_direct_status_prepare_sec"),
            "prepared_optix_count_threshold_sec": metadata.get("prepared_optix_count_threshold_sec"),
            "prepare_plus_replay_median_sec": metadata.get("prepare_plus_replay_median_sec"),
            "prepared_predicate_direct_status_plus_count_prepare_total_sec": metadata.get(
                "prepared_predicate_direct_status_plus_count_prepare_total_sec"
            ),
            "predicate_direct_status_signature_sec": metadata.get("predicate_direct_status_signature_sec"),
            "optix_rt_count_threshold_sec": timing.get("optix_rt_count_threshold_sec"),
            "timing_breakdown_sec": timing,
            "prepared_query_repeat_protocol": protocol_summary,
            "caller_owned_column_speedup_claim_authorized": metadata.get(
                "caller_owned_column_speedup_claim_authorized"
            ),
            "column_prepare_speedup_claim_authorized": metadata.get("column_prepare_speedup_claim_authorized"),
            "route_promotion_authorized": metadata.get("route_promotion_authorized"),
            "whole_app_speedup_claim_authorized": metadata.get("whole_app_speedup_claim_authorized"),
        },
    }


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None:
        return None
    if denominator <= 0.0:
        return None
    return float(numerator) / float(denominator)


def _compare_rows(row_mode: dict[str, object], column_mode: dict[str, object]) -> dict[str, object]:
    row_meta = row_mode["metadata"]
    column_meta = column_mode["metadata"]
    return {
        "dataset": row_mode["dataset"],
        "protocol": row_mode["protocol"],
        "signatures_match": row_mode["signature"] == column_mode["signature"],
        "row_prepare_sec": row_meta["charged_predicate_direct_status_prepare_sec"],
        "column_charged_prepare_sec": column_meta["charged_predicate_direct_status_prepare_sec"],
        "column_handle_prepare_sec": column_meta["prepared_predicate_direct_status_sec"],
        "column_coordinate_build_sec": column_meta["point_coordinate_column_build_sec"],
        "row_prepare_speedup_vs_charged_columns": _ratio(
            row_meta["charged_predicate_direct_status_prepare_sec"],
            column_meta["charged_predicate_direct_status_prepare_sec"],
        ),
        "row_prepare_speedup_if_columns_already_owned": _ratio(
            row_meta["charged_predicate_direct_status_prepare_sec"],
            column_meta["prepared_predicate_direct_status_sec"],
        ),
        "row_prepare_plus_count_total_sec": row_meta["prepared_predicate_direct_status_plus_count_prepare_total_sec"],
        "column_prepare_plus_count_total_sec": column_meta["prepared_predicate_direct_status_plus_count_prepare_total_sec"],
        "prepare_plus_count_total_speedup_vs_charged_columns": _ratio(
            row_meta["prepared_predicate_direct_status_plus_count_prepare_total_sec"],
            column_meta["prepared_predicate_direct_status_plus_count_prepare_total_sec"],
        ),
        "row_prepare_plus_replay_sec": row_meta["prepare_plus_replay_median_sec"],
        "column_prepare_plus_replay_sec": column_meta["prepare_plus_replay_median_sec"],
        "prepare_plus_replay_speedup_vs_charged_columns": _ratio(
            row_meta["prepare_plus_replay_median_sec"],
            column_meta["prepare_plus_replay_median_sec"],
        ),
    }


def run_matrix() -> dict[str, object]:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSONL.write_text("", encoding="utf-8")
    rows: list[dict[str, object]] = []
    comparisons: list[dict[str, object]] = []
    for protocol in PROTOCOLS:
        for dataset in ("clustered3d", "road3d", "ngsim_dense"):
            pair: list[dict[str, object]] = []
            for mode in (
                app.RT_DBSCAN_PREDICATE_DIRECT_STATUS_APP_MODE,
                app.RT_DBSCAN_PREDICATE_DIRECT_STATUS_POINT_COLUMNS_APP_MODE,
            ):
                start = time.perf_counter()
                try:
                    row = _case(dataset, mode, protocol=protocol)
                except Exception as exc:  # pragma: no cover - pod evidence helper
                    row = {
                        "status": "error",
                        "dataset": dataset,
                        "mode": mode,
                        "protocol": protocol["name"],
                        "point_count": POINT_COUNT,
                        "repeat": protocol["repeat"],
                        "warmup": protocol["warmup"],
                        "error": repr(exc),
                        "wall_sec": time.perf_counter() - start,
                    }
                rows.append(row)
                pair.append(row)
                with OUT_JSONL.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(row, sort_keys=True) + "\n")
                print(
                    json.dumps(
                        {
                            "dataset": dataset,
                            "mode": mode,
                            "protocol": protocol["name"],
                            "status": row["status"],
                            "elapsed_sec": row.get("elapsed_sec"),
                            "wall_sec": row.get("wall_sec"),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
            if len(pair) == 2 and pair[0]["status"] == "ok" and pair[1]["status"] == "ok":
                comparisons.append(_compare_rows(pair[0], pair[1]))
    ok_rows = [row for row in rows if row["status"] == "ok"]
    packet = {
        "version": "rtdl.v3_0.rtdbscan_point_column_app_mode.goal4490.v1",
        "goal": "Goal4490 / V3 M94",
        "point_count": POINT_COUNT,
        "partition_cell_factor": PARTITION_CELL_FACTOR,
        "protocols": PROTOCOLS,
        "case_count": len(rows),
        "ok_count": len(ok_rows),
        "error_count": len(rows) - len(ok_rows),
        "hardware": _gpu_info(),
        "claim_boundary": (
            "This matrix charges app-constructed coordinate-column build time. "
            "The larger caller-owned-column prepare speedup is valid only when "
            "the application already naturally owns CuPy x/y/z device columns."
        ),
        "summary": {
            "all_signatures_match": all(row["signatures_match"] for row in comparisons),
            "prepare_speedup_vs_charged_columns": {
                f"{row['protocol']}:{row['dataset']}": row["row_prepare_speedup_vs_charged_columns"]
                for row in comparisons
            },
            "prepare_speedup_if_columns_already_owned": {
                f"{row['protocol']}:{row['dataset']}": row["row_prepare_speedup_if_columns_already_owned"]
                for row in comparisons
            },
            "prepare_plus_replay_speedup_vs_charged_columns": {
                f"{row['protocol']}:{row['dataset']}": row["prepare_plus_replay_speedup_vs_charged_columns"]
                for row in comparisons
            },
        },
        "comparisons": comparisons,
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(packet["summary"], indent=2, sort_keys=True), flush=True)
    return packet


if __name__ == "__main__":
    run_matrix()
