from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import time

from examples.current.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    make_rt_dbscan_points,
)

import rtdsl as rt


POINT_COUNT = 1_048_576
OUT_JSON = Path("docs/reports/goal4489_v3_0_m93_direct_status_point_columns_2026-06-17.json")
OUT_JSONL = Path("docs/reports/goal4489_v3_0_m93_direct_status_point_columns_2026-06-17.jsonl")
DIAGNOSTIC_ENV_VAR = "RTDL_DIRECT_STATUS_PREPARE_DIAGNOSTICS"


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


def _phase_total(metadata: dict[str, object]) -> float | None:
    total = metadata.get("prepare_phase_timing_total_observed_sec")
    return None if total is None else float(total)


def _prepare_metadata(handle) -> dict[str, object]:
    return dict(handle.to_metadata()["prepare_metadata"])


def _signature(prepared) -> tuple[int, ...]:
    result = rt.run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_direct_status_union_preview_3d(
        prepared
    )
    return tuple(int(value) for value in result["columns"]["component_size_signature"])


def _point_columns(cupy, points: tuple[rt.Point3D, ...]) -> tuple[dict[str, object], float]:
    start = time.perf_counter()
    columns = {
        "x": cupy.asarray([point.x for point in points], dtype=cupy.float64),
        "y": cupy.asarray([point.y for point in points], dtype=cupy.float64),
        "z": cupy.asarray([point.z for point in points], dtype=cupy.float64),
    }
    cupy.cuda.get_current_stream().synchronize()
    return columns, time.perf_counter() - start


def _case(dataset: str) -> dict[str, object]:
    import cupy

    points = make_rt_dbscan_points(dataset, point_count=POINT_COUNT, seed=20260519)
    point_columns, point_column_build_sec = _point_columns(cupy, points)

    previous = os.environ.get(DIAGNOSTIC_ENV_VAR)
    os.environ[DIAGNOSTIC_ENV_VAR] = "1"
    try:
        row_prepare_start = time.perf_counter()
        row_prepared = rt.prepare_v2_8_fixed_radius_partition_convergence_direct_status_union_cupy_preview_3d(
            points,
            radius={
                "clustered3d": 0.055,
                "road3d": 0.030,
                "ngsim_dense": 0.012,
            }[dataset],
            cell_factor=0.125,
        )
        row_prepare_sec = time.perf_counter() - row_prepare_start
        row_meta = _prepare_metadata(row_prepared)
        row_run_start = time.perf_counter()
        row_signature = _signature(row_prepared)
        row_run_sec = time.perf_counter() - row_run_start

        column_prepare_start = time.perf_counter()
        column_prepared = (
            rt.prepare_v2_8_fixed_radius_partition_convergence_direct_status_union_cupy_point_columns_preview_3d(
                point_columns,
                radius={
                    "clustered3d": 0.055,
                    "road3d": 0.030,
                    "ngsim_dense": 0.012,
                }[dataset],
                cell_factor=0.125,
            )
        )
        column_prepare_sec = time.perf_counter() - column_prepare_start
        column_meta = _prepare_metadata(column_prepared)
        column_run_start = time.perf_counter()
        column_signature = _signature(column_prepared)
        column_run_sec = time.perf_counter() - column_run_start
    finally:
        if previous is None:
            os.environ.pop(DIAGNOSTIC_ENV_VAR, None)
        else:
            os.environ[DIAGNOSTIC_ENV_VAR] = previous

    return {
        "status": "ok",
        "dataset": dataset,
        "point_count": POINT_COUNT,
        "point_column_build_sec": point_column_build_sec,
        "row_prepare_sec": row_prepare_sec,
        "row_prepare_phase_total_sec": _phase_total(row_meta),
        "row_prepare_metadata": {
            "point_coordinate_host_extraction": row_meta.get("point_coordinate_host_extraction"),
            "point_coordinate_upload_avoided": row_meta.get("point_coordinate_upload_avoided"),
            "prepare_phase_timing_sec": row_meta.get("prepare_phase_timing_sec"),
        },
        "row_run_sec": row_run_sec,
        "column_prepare_sec": column_prepare_sec,
        "column_prepare_phase_total_sec": _phase_total(column_meta),
        "column_prepare_metadata": {
            "point_coordinate_host_extraction": column_meta.get("point_coordinate_host_extraction"),
            "point_coordinate_upload_avoided": column_meta.get("point_coordinate_upload_avoided"),
            "prepare_phase_timing_sec": column_meta.get("prepare_phase_timing_sec"),
        },
        "column_run_sec": column_run_sec,
        "prepare_speedup_if_columns_already_owned": (
            row_prepare_sec / column_prepare_sec if column_prepare_sec > 0.0 else None
        ),
        "prepare_phase_speedup_if_columns_already_owned": (
            _phase_total(row_meta) / _phase_total(column_meta)
            if _phase_total(row_meta) and _phase_total(column_meta)
            else None
        ),
        "signatures_match": row_signature == column_signature,
        "signature": {
            "component_count": len(column_signature),
            "point_count": sum(column_signature),
            "first_sizes": column_signature[:10],
            "last_sizes": column_signature[-10:],
        },
    }


def run_matrix() -> dict[str, object]:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSONL.write_text("", encoding="utf-8")
    rows: list[dict[str, object]] = []
    for dataset in ("clustered3d", "road3d", "ngsim_dense"):
        start = time.perf_counter()
        try:
            row = _case(dataset)
            row["wall_sec"] = time.perf_counter() - start
        except Exception as exc:  # pragma: no cover - pod evidence helper
            row = {
                "status": "error",
                "dataset": dataset,
                "point_count": POINT_COUNT,
                "error": repr(exc),
                "wall_sec": time.perf_counter() - start,
            }
        rows.append(row)
        with OUT_JSONL.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        print(
            json.dumps(
                {
                    "dataset": dataset,
                    "status": row["status"],
                    "row_prepare": row.get("row_prepare_sec"),
                    "column_prepare": row.get("column_prepare_sec"),
                    "speedup": row.get("prepare_speedup_if_columns_already_owned"),
                },
                sort_keys=True,
            ),
            flush=True,
        )
    ok_rows = [row for row in rows if row["status"] == "ok"]
    packet = {
        "version": "rtdl.v3_0.direct_status_point_columns.goal4489.v1",
        "point_count": POINT_COUNT,
        "case_count": len(rows),
        "ok_count": len(ok_rows),
        "error_count": len(rows) - len(ok_rows),
        "hardware": _gpu_info(),
        "claim_boundary": (
            "Column-based direct-status prepare speedups apply only when the caller already "
            "owns CuPy float64 x/y/z device columns. Point-column construction is reported "
            "separately and is not hidden."
        ),
        "summary": {
            "all_signatures_match": all(bool(row.get("signatures_match")) for row in ok_rows),
            "prepare_speedups_if_columns_already_owned": {
                row["dataset"]: row["prepare_speedup_if_columns_already_owned"]
                for row in ok_rows
            },
            "prepare_phase_speedups_if_columns_already_owned": {
                row["dataset"]: row["prepare_phase_speedup_if_columns_already_owned"]
                for row in ok_rows
            },
        },
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(packet["summary"], indent=2, sort_keys=True), flush=True)
    return packet


if __name__ == "__main__":
    run_matrix()
