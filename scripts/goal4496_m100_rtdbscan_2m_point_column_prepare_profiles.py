from __future__ import annotations

import gc
import json
import os
from pathlib import Path
import subprocess
import time

from examples.benchmark_apps.rt_dbscan import rtdl_rt_dbscan_benchmark_app as app

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.rtdbscan_2m_point_column_prepare_profiles.goal4496.v1"
OUT_JSON = Path("docs/reports/goal4496_v3_0_m100_rtdbscan_2m_point_column_prepare_profiles_2026-06-17.json")
OUT_JSONL = Path("docs/reports/goal4496_v3_0_m100_rtdbscan_2m_point_column_prepare_profiles_2026-06-17.jsonl")
DATASETS = ("clustered3d", "ngsim_dense")
POINT_COUNT = 2_097_152
PARTITION_CELL_FACTOR = 0.25
SEED = 20260519
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


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0.0:
        return None
    return float(numerator) / float(denominator)


def _cleanup_gpu() -> None:
    gc.collect()
    try:
        import cupy

        cupy.cuda.get_current_stream().synchronize()
        cupy.get_default_memory_pool().free_all_blocks()
    except Exception:
        pass


def _phase_total(metadata: dict[str, object]) -> float | None:
    total = metadata.get("prepare_phase_timing_total_observed_sec")
    return None if total is None else float(total)


def _prepare_metadata(handle) -> dict[str, object]:
    return dict(handle.to_metadata()["prepare_metadata"])


def _signature(prepared) -> tuple[int, ...]:
    result = rt.run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_direct_status_union_preview_3d(
        prepared,
        convergence_mode="single_pass_candidate",
    )
    return tuple(int(value) for value in result["columns"]["component_size_signature"])


def _case(dataset: str) -> dict[str, object]:
    points = app.make_rt_dbscan_points(dataset, point_count=POINT_COUNT, seed=SEED)
    radius = app.DEFAULT_DATASET_CONFIG[dataset]["radius"]

    point_column_build_start = time.perf_counter()
    point_columns = rt.point_rows_to_partner_coordinate_columns_3d(points, partner="cupy")
    import cupy

    cupy.cuda.get_current_stream().synchronize()
    point_column_build_sec = time.perf_counter() - point_column_build_start

    previous = os.environ.get(DIAGNOSTIC_ENV_VAR)
    os.environ[DIAGNOSTIC_ENV_VAR] = "1"
    try:
        row_prepare_start = time.perf_counter()
        row_prepared = rt.prepare_v2_8_fixed_radius_partition_convergence_direct_status_union_cupy_preview_3d(
            points,
            radius=radius,
            cell_factor=PARTITION_CELL_FACTOR,
        )
        row_prepare_sec = time.perf_counter() - row_prepare_start
        row_meta = _prepare_metadata(row_prepared)
        with row_prepared:
            row_run_start = time.perf_counter()
            row_signature = _signature(row_prepared)
            row_run_sec = time.perf_counter() - row_run_start
        _cleanup_gpu()

        column_prepare_start = time.perf_counter()
        column_prepared = rt.prepare_v2_8_fixed_radius_partition_convergence_direct_status_union_cupy_point_columns_preview_3d(
            point_columns,
            radius=radius,
            cell_factor=PARTITION_CELL_FACTOR,
        )
        column_prepare_sec = time.perf_counter() - column_prepare_start
        column_meta = _prepare_metadata(column_prepared)
        with column_prepared:
            column_run_start = time.perf_counter()
            column_signature = _signature(column_prepared)
            column_run_sec = time.perf_counter() - column_run_start
    finally:
        if previous is None:
            os.environ.pop(DIAGNOSTIC_ENV_VAR, None)
        else:
            os.environ[DIAGNOSTIC_ENV_VAR] = previous

    row_phase_total = _phase_total(row_meta)
    column_phase_total = _phase_total(column_meta)
    return {
        "status": "ok",
        "dataset": dataset,
        "point_count": POINT_COUNT,
        "radius": radius,
        "partition_cell_factor": PARTITION_CELL_FACTOR,
        "point_column_build_sec": point_column_build_sec,
        "row_prepare_sec": row_prepare_sec,
        "row_prepare_phase_total_sec": row_phase_total,
        "row_prepare_metadata": {
            "point_coordinate_host_extraction": row_meta.get("point_coordinate_host_extraction"),
            "point_coordinate_upload_avoided": row_meta.get("point_coordinate_upload_avoided"),
            "prepare_phase_timing_sec": row_meta.get("prepare_phase_timing_sec"),
        },
        "row_run_sec": row_run_sec,
        "column_prepare_sec": column_prepare_sec,
        "column_prepare_phase_total_sec": column_phase_total,
        "column_prepare_metadata": {
            "point_coordinate_host_extraction": column_meta.get("point_coordinate_host_extraction"),
            "point_coordinate_upload_avoided": column_meta.get("point_coordinate_upload_avoided"),
            "prepare_phase_timing_sec": column_meta.get("prepare_phase_timing_sec"),
        },
        "column_run_sec": column_run_sec,
        "prepare_speedup_if_columns_already_owned": _ratio(row_prepare_sec, column_prepare_sec),
        "prepare_phase_speedup_if_columns_already_owned": _ratio(row_phase_total, column_phase_total),
        "signatures_match": row_signature == column_signature,
        "signature": {
            "component_count": len(column_signature),
            "point_count": sum(column_signature),
            "first_sizes": column_signature[:10],
            "last_sizes": column_signature[-10:],
        },
        "claim_boundary": {
            "isolates_direct_status_coordinate_handoff": True,
            "counts_point_column_build_separately": True,
            "not_full_rtdbscan_total": True,
            "not_count_threshold_app_route": True,
            "route_promotion_authorized": False,
        },
    }


def run_matrix() -> dict[str, object]:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSONL.write_text("", encoding="utf-8")
    rows: list[dict[str, object]] = []
    for dataset in DATASETS:
        started = time.perf_counter()
        try:
            row = _case(dataset)
            row["wall_sec"] = time.perf_counter() - started
        except Exception as exc:  # pragma: no cover - pod evidence helper
            row = {
                "status": "error",
                "dataset": dataset,
                "point_count": POINT_COUNT,
                "error": repr(exc),
                "wall_sec": time.perf_counter() - started,
            }
        rows.append(row)
        with OUT_JSONL.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        print(
            json.dumps(
                {
                    "dataset": dataset,
                    "status": row["status"],
                    "prepare_speedup_if_columns_already_owned": row.get(
                        "prepare_speedup_if_columns_already_owned"
                    ),
                    "wall_sec": row["wall_sec"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
        _cleanup_gpu()

    ok_rows = [row for row in rows if row["status"] == "ok"]
    packet = {
        "version": PACKET_VERSION,
        "goal": "Goal4496 / V3 M100",
        "datasets": DATASETS,
        "point_count": POINT_COUNT,
        "partition_cell_factor": PARTITION_CELL_FACTOR,
        "case_count": len(rows),
        "ok_count": len(ok_rows),
        "error_count": len(rows) - len(ok_rows),
        "hardware": _gpu_info(),
        "claim_boundary": {
            "caller_owned_column_speedup_requires_existing_device_columns": True,
            "point_column_build_reported_separately": True,
            "isolated_direct_status_prepare_only": True,
            "not_count_threshold_app_route": True,
            "route_promotion_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
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
