from __future__ import annotations

import gc
import json
import os
from pathlib import Path
import subprocess
import time

from examples.current.research_benchmarks.rt_dbscan import rtdl_rt_dbscan_benchmark_app as app

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.rtdbscan_2m_point_column_reuse.goal4495.v1"
OUT_JSON = Path("docs/reports/goal4495_v3_0_m99_rtdbscan_2m_point_column_reuse_2026-06-17.json")
OUT_JSONL = Path("docs/reports/goal4495_v3_0_m99_rtdbscan_2m_point_column_reuse_2026-06-17.jsonl")
DATASET = "road3d"
POINT_COUNT = 2_097_152
PARTITION_CELL_FACTOR = 0.25
SEED = 20260519
PROTOCOLS = (
    {"name": "one_shot", "repeat": 1, "warmup": 0},
    {"name": "warm_replay", "repeat": 3, "warmup": 1},
)
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


def _direct_status_prepare_pair() -> dict[str, object]:
    points = app.make_rt_dbscan_points(DATASET, point_count=POINT_COUNT, seed=SEED)
    radius = app.DEFAULT_DATASET_CONFIG[DATASET]["radius"]

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
    row_signature_payload = {
        "component_count": len(row_signature),
        "point_count": sum(row_signature),
        "first_sizes": row_signature[:10],
        "last_sizes": row_signature[-10:],
    }
    return {
        "status": "ok",
        "dataset": DATASET,
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
        "signature": row_signature_payload,
        "claim_boundary": {
            "isolates_direct_status_coordinate_handoff": True,
            "counts_point_column_build_separately": True,
            "not_full_rtdbscan_total": True,
            "route_promotion_authorized": False,
        },
    }


def _app_case(mode: str, *, protocol: dict[str, object]) -> dict[str, object]:
    repeat = int(protocol["repeat"])
    warmup = int(protocol["warmup"])
    start = time.perf_counter()
    payload = app.run_rt_dbscan_benchmark(
        mode=mode,
        dataset=DATASET,
        point_count=POINT_COUNT,
        radius=None,
        min_neighbors=None,
        seed=SEED,
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
    row = {
        "status": "ok",
        "dataset": DATASET,
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
            "point_coordinate_column_build_charged_in_total": metadata.get(
                "point_coordinate_column_build_charged_in_total"
            ),
            "point_coordinate_column_build_hidden": metadata.get("point_coordinate_column_build_hidden"),
            "prepared_predicate_direct_status_sec": metadata.get("prepared_predicate_direct_status_sec"),
            "charged_predicate_direct_status_prepare_sec": metadata.get(
                "charged_predicate_direct_status_prepare_sec"
            ),
            "prepared_optix_count_threshold_sec": metadata.get("prepared_optix_count_threshold_sec"),
            "prepared_predicate_direct_status_plus_count_prepare_total_sec": metadata.get(
                "prepared_predicate_direct_status_plus_count_prepare_total_sec"
            ),
            "prepare_plus_replay_median_sec": metadata.get("prepare_plus_replay_median_sec"),
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
    _cleanup_gpu()
    return row


def _compare_app_rows(row_mode: dict[str, object], column_mode: dict[str, object]) -> dict[str, object]:
    row_meta = row_mode["metadata"]
    column_meta = column_mode["metadata"]
    return {
        "dataset": DATASET,
        "protocol": row_mode["protocol"],
        "signatures_match": row_mode["signature"] == column_mode["signature"],
        "row_elapsed_sec": row_mode["elapsed_sec"],
        "column_elapsed_sec": column_mode["elapsed_sec"],
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
        "row_prepare_plus_count_total_sec": row_meta[
            "prepared_predicate_direct_status_plus_count_prepare_total_sec"
        ],
        "column_prepare_plus_count_total_sec": column_meta[
            "prepared_predicate_direct_status_plus_count_prepare_total_sec"
        ],
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
        "decision": "reuse_columns_only" if (
            _ratio(
                row_meta["prepared_predicate_direct_status_plus_count_prepare_total_sec"],
                column_meta["prepared_predicate_direct_status_plus_count_prepare_total_sec"],
            )
            or 0.0
        ) < 1.05 else "charged_columns_candidate",
    }


def run_matrix() -> dict[str, object]:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSONL.write_text("", encoding="utf-8")
    rows: list[dict[str, object]] = []
    comparisons: list[dict[str, object]] = []

    primitive_started = time.perf_counter()
    try:
        primitive = _direct_status_prepare_pair()
        primitive["wall_sec"] = time.perf_counter() - primitive_started
    except Exception as exc:  # pragma: no cover - pod evidence helper
        primitive = {
            "status": "error",
            "dataset": DATASET,
            "point_count": POINT_COUNT,
            "error": repr(exc),
            "wall_sec": time.perf_counter() - primitive_started,
        }
    rows.append({"row_type": "primitive_prepare_pair", **primitive})
    with OUT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(rows[-1], sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "row_type": "primitive_prepare_pair",
                "status": primitive["status"],
                "prepare_speedup_if_columns_already_owned": primitive.get(
                    "prepare_speedup_if_columns_already_owned"
                ),
            },
            sort_keys=True,
        ),
        flush=True,
    )

    for protocol in PROTOCOLS:
        pair: list[dict[str, object]] = []
        for mode in (
            app.RT_DBSCAN_PREDICATE_DIRECT_STATUS_APP_MODE,
            app.RT_DBSCAN_PREDICATE_DIRECT_STATUS_POINT_COLUMNS_APP_MODE,
        ):
            started = time.perf_counter()
            try:
                row = _app_case(mode, protocol=protocol)
            except Exception as exc:  # pragma: no cover - pod evidence helper
                row = {
                    "status": "error",
                    "dataset": DATASET,
                    "mode": mode,
                    "protocol": protocol["name"],
                    "point_count": POINT_COUNT,
                    "repeat": protocol["repeat"],
                    "warmup": protocol["warmup"],
                    "error": repr(exc),
                    "wall_sec": time.perf_counter() - started,
                }
            rows.append({"row_type": "app_mode", **row})
            pair.append(row)
            with OUT_JSONL.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(rows[-1], sort_keys=True) + "\n")
            print(
                json.dumps(
                    {
                        "row_type": "app_mode",
                        "protocol": protocol["name"],
                        "mode": mode,
                        "status": row["status"],
                        "elapsed_sec": row.get("elapsed_sec"),
                        "wall_sec": row.get("wall_sec"),
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
        if len(pair) == 2 and pair[0]["status"] == "ok" and pair[1]["status"] == "ok":
            comparisons.append(_compare_app_rows(pair[0], pair[1]))

    ok_rows = [row for row in rows if row["status"] == "ok"]
    packet = {
        "version": PACKET_VERSION,
        "goal": "Goal4495 / V3 M99",
        "dataset": DATASET,
        "point_count": POINT_COUNT,
        "partition_cell_factor": PARTITION_CELL_FACTOR,
        "protocols": PROTOCOLS,
        "case_count": len(rows),
        "ok_count": len(ok_rows),
        "error_count": len(rows) - len(ok_rows),
        "hardware": _gpu_info(),
        "claim_boundary": {
            "caller_owned_column_speedup_requires_existing_device_columns": True,
            "point_column_build_charged_when_app_constructs_columns": True,
            "route_promotion_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
        "summary": {
            "primitive_signatures_match": bool(primitive.get("signatures_match")),
            "primitive_prepare_speedup_if_columns_already_owned": primitive.get(
                "prepare_speedup_if_columns_already_owned"
            ),
            "primitive_prepare_phase_speedup_if_columns_already_owned": primitive.get(
                "prepare_phase_speedup_if_columns_already_owned"
            ),
            "all_app_signatures_match": all(row["signatures_match"] for row in comparisons),
            "app_prepare_speedup_if_columns_already_owned": {
                row["protocol"]: row["row_prepare_speedup_if_columns_already_owned"]
                for row in comparisons
            },
            "app_prepare_speedup_vs_charged_columns": {
                row["protocol"]: row["row_prepare_speedup_vs_charged_columns"] for row in comparisons
            },
            "app_prepare_plus_count_total_speedup_vs_charged_columns": {
                row["protocol"]: row["prepare_plus_count_total_speedup_vs_charged_columns"]
                for row in comparisons
            },
            "app_prepare_plus_replay_speedup_vs_charged_columns": {
                row["protocol"]: row["prepare_plus_replay_speedup_vs_charged_columns"]
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
