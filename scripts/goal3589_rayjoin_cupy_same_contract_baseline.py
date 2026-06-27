#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from examples.benchmark_apps.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    _load_rayjoin_case,
)
from examples.benchmark_apps.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    run_rayjoin_prepared_optix_cupy_refined_pip,
)
from examples.benchmark_apps.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    run_rayjoin_prepared_optix_left_id_dense_count_workload,
)
from examples.benchmark_apps.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    run_rayjoin_prepared_optix_shape_pair_active_count_workload,
)


SCHEMA = "rtdl.goal3589.rayjoin_cupy_same_contract_baseline.v1"
DEFAULT_ARTIFACT = ROOT / "docs" / "reports" / "goal3589_rayjoin_cupy_same_contract_baseline_a5000" / "summary.json"
TIER_SUFFIX = {"smoke": "x64", "standard": "x512", "stress": "x2048"}
WORKLOADS = ("pip", "lsi", "overlay_seed")


PIP_COUNT_KERNEL = r"""
extern "C" __global__
void rtdl_goal3589_pip_count_flags(
    const double* px,
    const double* py,
    const long long point_count,
    const int* shape_offsets,
    const int* shape_counts,
    const double* bounds,
    const double* vx,
    const double* vy,
    const long long shape_count,
    unsigned char* flags)
{
    const long long idx = (long long)blockDim.x * (long long)blockIdx.x + (long long)threadIdx.x;
    const long long total = point_count * shape_count;
    if (idx >= total) return;
    const long long pi = idx / shape_count;
    const long long si = idx - pi * shape_count;
    const double x = px[pi];
    const double y = py[pi];
    const double min_x = bounds[si * 4 + 0];
    const double min_y = bounds[si * 4 + 1];
    const double max_x = bounds[si * 4 + 2];
    const double max_y = bounds[si * 4 + 3];
    if (x < min_x || x > max_x || y < min_y || y > max_y) return;

    const int off = shape_offsets[si];
    const int n = shape_counts[si];
    for (int i = 0; i < n; ++i) {
        const int j = (i + 1) % n;
        const double ax = vx[off + i];
        const double ay = vy[off + i];
        const double bx = vx[off + j];
        const double by = vy[off + j];
        const double dx = bx - ax;
        const double dy = by - ay;
        const double cross = (x - ax) * dy - (y - ay) * dx;
        const double dot = (x - ax) * dx + (y - ay) * dy;
        const double len2 = dx * dx + dy * dy;
        if (fabs(cross) <= 1.0e-9 * sqrt(len2) && dot >= -1.0e-9 && dot <= len2 + 1.0e-9) {
            flags[idx] = 1;
            return;
        }
    }

    bool inside = false;
    for (int i = 0, j = n - 1; i < n; j = i++) {
        const double xi = vx[off + i];
        const double yi = vy[off + i];
        const double xj = vx[off + j];
        const double yj = vy[off + j];
        if ((yi > y) != (yj > y)) {
            const double denom = (yj - yi) != 0.0 ? (yj - yi) : 1.0e-20;
            const double x_cross = (xj - xi) * (y - yi) / denom + xi;
            if (x <= x_cross) {
                inside = !inside;
            }
        }
    }
    if (inside) flags[idx] = 1;
}
"""


LSI_COUNT_KERNEL = r"""
static __device__ bool seg_intersect(
    double ax0, double ay0, double ax1, double ay1,
    double bx0, double by0, double bx1, double by1)
{
    const double rx = ax1 - ax0;
    const double ry = ay1 - ay0;
    const double sx = bx1 - bx0;
    const double sy = by1 - by0;
    const double denom = rx * sy - ry * sx;
    if (fabs(denom) < 1.0e-7) return false;
    const double qpx = bx0 - ax0;
    const double qpy = by0 - ay0;
    const double t = (qpx * sy - qpy * sx) / denom;
    const double u = (qpx * ry - qpy * rx) / denom;
    return t >= 0.0 && t <= 1.0 && u >= 0.0 && u <= 1.0;
}

extern "C" __global__
void rtdl_goal3589_lsi_count_flags(
    const double* left,
    const double* right,
    const long long left_count,
    const long long right_count,
    unsigned char* flags)
{
    const long long idx = (long long)blockDim.x * (long long)blockIdx.x + (long long)threadIdx.x;
    const long long total = left_count * right_count;
    if (idx >= total) return;
    const long long li = idx / right_count;
    const long long ri = idx - li * right_count;
    const double ax0 = left[li * 4 + 0];
    const double ay0 = left[li * 4 + 1];
    const double ax1 = left[li * 4 + 2];
    const double ay1 = left[li * 4 + 3];
    const double bx0 = right[ri * 4 + 0];
    const double by0 = right[ri * 4 + 1];
    const double bx1 = right[ri * 4 + 2];
    const double by1 = right[ri * 4 + 3];
    if (seg_intersect(ax0, ay0, ax1, ay1, bx0, by0, bx1, by1)) flags[idx] = 1;
}
"""


OVERLAY_ACTIVE_COUNT_KERNEL = r"""
static __device__ bool seg_intersect_overlay(
    double ax0, double ay0, double ax1, double ay1,
    double bx0, double by0, double bx1, double by1)
{
    const double rx = ax1 - ax0;
    const double ry = ay1 - ay0;
    const double sx = bx1 - bx0;
    const double sy = by1 - by0;
    const double denom = rx * sy - ry * sx;
    if (fabs(denom) < 1.0e-7) return false;
    const double qpx = bx0 - ax0;
    const double qpy = by0 - ay0;
    const double t = (qpx * sy - qpy * sx) / denom;
    const double u = (qpx * ry - qpy * rx) / denom;
    return t >= 0.0 && t <= 1.0 && u >= 0.0 && u <= 1.0;
}

static __device__ bool point_on_segment_overlay(
    double px, double py,
    double ax, double ay,
    double bx, double by)
{
    const double dx = bx - ax;
    const double dy = by - ay;
    const double cross = (px - ax) * dy - (py - ay) * dx;
    if (fabs(cross) > 1.0e-5) return false;
    const double min_x = ax < bx ? ax : bx;
    const double max_x = ax > bx ? ax : bx;
    const double min_y = ay < by ? ay : by;
    const double max_y = ay > by ? ay : by;
    return px >= min_x - 1.0e-5 && px <= max_x + 1.0e-5 &&
           py >= min_y - 1.0e-5 && py <= max_y + 1.0e-5;
}

static __device__ bool point_in_polygon_overlay(
    double px,
    double py,
    int off,
    int n,
    const double* vx,
    const double* vy)
{
    for (int i = 0, j = n - 1; i < n; j = i++) {
        if (point_on_segment_overlay(px, py, vx[off + j], vy[off + j], vx[off + i], vy[off + i])) {
            return true;
        }
    }
    bool inside = false;
    for (int i = 0, j = n - 1; i < n; j = i++) {
        const double xi = vx[off + i];
        const double yi = vy[off + i];
        const double xj = vx[off + j];
        const double yj = vy[off + j];
        if ((yi > py) != (yj > py)) {
            const double denom = (yj - yi) != 0.0 ? (yj - yi) : 1.0e-20;
            const double x_cross = (xj - xi) * (py - yi) / denom + xi;
            if (px <= x_cross) inside = !inside;
        }
    }
    return inside;
}

extern "C" __global__
void rtdl_goal3589_overlay_active_count_flags(
    const int* left_offsets,
    const int* left_counts,
    const double* left_bounds,
    const double* left_vx,
    const double* left_vy,
    const long long left_count,
    const int* right_offsets,
    const int* right_counts,
    const double* right_bounds,
    const double* right_vx,
    const double* right_vy,
    const long long right_count,
    unsigned char* flags)
{
    const long long idx = (long long)blockDim.x * (long long)blockIdx.x + (long long)threadIdx.x;
    const long long total = left_count * right_count;
    if (idx >= total) return;
    const long long li = idx / right_count;
    const long long ri = idx - li * right_count;
    if (left_bounds[li * 4 + 2] < right_bounds[ri * 4 + 0] ||
        right_bounds[ri * 4 + 2] < left_bounds[li * 4 + 0] ||
        left_bounds[li * 4 + 3] < right_bounds[ri * 4 + 1] ||
        right_bounds[ri * 4 + 3] < left_bounds[li * 4 + 1]) {
        return;
    }

    const int loff = left_offsets[li];
    const int lcnt = left_counts[li];
    const int roff = right_offsets[ri];
    const int rcnt = right_counts[ri];
    for (int le = 0; le < lcnt; ++le) {
        const int le_next = (le + 1) % lcnt;
        const double ax0 = left_vx[loff + le];
        const double ay0 = left_vy[loff + le];
        const double ax1 = left_vx[loff + le_next];
        const double ay1 = left_vy[loff + le_next];
        for (int re = 0; re < rcnt; ++re) {
            const int re_next = (re + 1) % rcnt;
            if (seg_intersect_overlay(
                    ax0, ay0, ax1, ay1,
                    right_vx[roff + re], right_vy[roff + re],
                    right_vx[roff + re_next], right_vy[roff + re_next])) {
                flags[idx] = 1;
                return;
            }
        }
    }

    const double lx0 = left_vx[loff];
    const double ly0 = left_vy[loff];
    if (point_in_polygon_overlay(lx0, ly0, roff, rcnt, right_vx, right_vy)) {
        flags[idx] = 1;
        return;
    }
    const double rx0 = right_vx[roff];
    const double ry0 = right_vy[roff];
    if (point_in_polygon_overlay(rx0, ry0, loff, lcnt, left_vx, left_vy)) {
        flags[idx] = 1;
    }
}
"""


def _claim_boundary() -> dict[str, bool]:
    return {
        "internal_results_only": True,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
    }


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _dataset_for(workload: str, tier: str) -> str:
    suffix = TIER_SUFFIX[tier]
    if workload == "pip":
        return f"derived/authored_pip_square_tiled_{suffix}"
    if workload == "lsi":
        return f"derived/authored_lsi_crossing_tiled_{suffix}"
    if workload == "overlay_seed":
        return f"derived/authored_overlay_squares_tiled_{suffix}"
    raise ValueError(f"unknown workload: {workload}")


def _workload_list(value: str) -> tuple[str, ...]:
    if value == "all":
        return WORKLOADS
    requested = tuple(part.strip() for part in value.split(",") if part.strip())
    if not requested:
        raise ValueError("workload list is empty")
    for workload in requested:
        if workload not in WORKLOADS:
            raise ValueError(f"unsupported workload: {workload}")
    return requested


def _median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def _record_value(record: object, field: str) -> Any:
    if isinstance(record, dict):
        return record[field]
    return getattr(record, field)


def _segment_array(segments, np):
    if all(hasattr(segments, name) for name in ("x0", "y0", "x1", "y1", "count")):
        return np.column_stack(
            (
                np.asarray(segments.x0, dtype=np.float64),
                np.asarray(segments.y0, dtype=np.float64),
                np.asarray(segments.x1, dtype=np.float64),
                np.asarray(segments.y1, dtype=np.float64),
            )
        )
    return np.asarray(
        [
            [
                float(_record_value(segment, "x0")),
                float(_record_value(segment, "y0")),
                float(_record_value(segment, "x1")),
                float(_record_value(segment, "y1")),
            ]
            for segment in segments
        ],
        dtype=np.float64,
    )


def _point_arrays(points, np):
    return (
        np.asarray([float(_record_value(point, "x")) for point in points], dtype=np.float64),
        np.asarray([float(_record_value(point, "y")) for point in points], dtype=np.float64),
    )


def _polygon_arrays(polygons, np):
    offsets: list[int] = []
    counts: list[int] = []
    bounds: list[tuple[float, float, float, float]] = []
    vx: list[float] = []
    vy: list[float] = []
    for polygon in polygons:
        vertices = tuple(_record_value(polygon, "vertices"))
        offsets.append(len(vx))
        counts.append(len(vertices))
        xs = [float(x) for x, _ in vertices]
        ys = [float(y) for _, y in vertices]
        bounds.append((min(xs), min(ys), max(xs), max(ys)))
        vx.extend(xs)
        vy.extend(ys)
    return (
        np.asarray(offsets, dtype=np.int32),
        np.asarray(counts, dtype=np.int32),
        np.asarray(bounds, dtype=np.float64),
        np.asarray(vx, dtype=np.float64),
        np.asarray(vy, dtype=np.float64),
    )


def _time_cupy_flags(*, cp, flags, repeat: int, warmup: int, launch, stability_label: str) -> dict[str, object]:
    measured: list[float] = []
    counts: list[int] = []
    runs: list[dict[str, object]] = []
    for iteration in range(warmup + repeat):
        flags.fill(0)
        cp.cuda.Stream.null.synchronize()
        start = time.perf_counter()
        launch()
        count = int(cp.count_nonzero(flags).get())
        cp.cuda.Stream.null.synchronize()
        elapsed = time.perf_counter() - start
        is_warmup = iteration < warmup
        runs.append(
            {
                "iteration": iteration,
                "is_warmup": is_warmup,
                "elapsed_sec": elapsed,
                "count": count,
            }
        )
        print(
            f"[goal3589] {stability_label} {'warmup' if is_warmup else 'repeat'} "
            f"{iteration + 1}/{warmup + repeat} elapsed={elapsed:.6f}s count={count}",
            flush=True,
        )
        if not is_warmup:
            measured.append(elapsed)
            counts.append(count)
    if len(set(counts)) != 1:
        raise RuntimeError(f"{stability_label} changed count across repeats: {counts}")
    return {
        "hot_median_sec": _median(measured),
        "hot_total_sec": float(sum(measured)),
        "hot_repeat_secs": measured,
        "count": counts[-1] if counts else 0,
        "runs": runs,
    }


def run_cupy_baseline(workload: str, dataset: str, *, repeat: int, warmup: int) -> dict[str, object]:
    import numpy as np
    import cupy as cp

    case = _load_rayjoin_case(workload, dataset, segment_column_inputs=workload == "lsi")
    prepare_start = time.perf_counter()
    threads = 256
    if workload == "pip":
        points = tuple(case.inputs["points"])
        shapes = tuple(case.inputs["polygons"])
        point_x, point_y = _point_arrays(points, np)
        shape_offsets, shape_counts, bounds, vx, vy = _polygon_arrays(shapes, np)
        px_gpu = cp.asarray(point_x)
        py_gpu = cp.asarray(point_y)
        shape_offsets_gpu = cp.asarray(shape_offsets)
        shape_counts_gpu = cp.asarray(shape_counts)
        bounds_gpu = cp.asarray(bounds)
        vx_gpu = cp.asarray(vx)
        vy_gpu = cp.asarray(vy)
        candidate_pair_count = int(len(points) * len(shapes))
        flags = cp.zeros((candidate_pair_count,), dtype=cp.uint8)
        kernel = cp.RawKernel(PIP_COUNT_KERNEL, "rtdl_goal3589_pip_count_flags")
        blocks = (candidate_pair_count + threads - 1) // threads
        prepare_sec = time.perf_counter() - prepare_start
        timed = _time_cupy_flags(
            cp=cp,
            flags=flags,
            repeat=repeat,
            warmup=warmup,
            stability_label="pip/cupy_dense_all_pairs",
            launch=lambda: kernel(
                (blocks,),
                (threads,),
                (
                    px_gpu,
                    py_gpu,
                    len(points),
                    shape_offsets_gpu,
                    shape_counts_gpu,
                    bounds_gpu,
                    vx_gpu,
                    vy_gpu,
                    len(shapes),
                    flags,
                ),
            ),
        )
        input_counts = {"point_count": len(points), "shape_count": len(shapes)}
        output_contract = "point_to_shape_positive_hit_count"
        baseline_kind = "cupy_rawkernel_cuda_core_dense_pip_count"
    elif workload == "lsi":
        left_array = _segment_array(case.inputs["left"], np)
        right_array = _segment_array(case.inputs["right"], np)
        left_count = int(left_array.shape[0])
        right_count = int(right_array.shape[0])
        left_gpu = cp.asarray(left_array)
        right_gpu = cp.asarray(right_array)
        candidate_pair_count = int(left_count * right_count)
        flags = cp.zeros((candidate_pair_count,), dtype=cp.uint8)
        kernel = cp.RawKernel(LSI_COUNT_KERNEL, "rtdl_goal3589_lsi_count_flags")
        blocks = (candidate_pair_count + threads - 1) // threads
        prepare_sec = time.perf_counter() - prepare_start
        timed = _time_cupy_flags(
            cp=cp,
            flags=flags,
            repeat=repeat,
            warmup=warmup,
            stability_label="lsi/cupy_dense_all_pairs",
            launch=lambda: kernel(
                (blocks,),
                (threads,),
                (
                    left_gpu,
                    right_gpu,
                    left_count,
                    right_count,
                    flags,
                ),
            ),
        )
        input_counts = {"left_segment_count": left_count, "right_segment_count": right_count}
        output_contract = "segment_segment_intersection_count"
        baseline_kind = "cupy_rawkernel_cuda_core_dense_lsi_count"
    else:
        left = tuple(case.inputs["left"])
        right = tuple(case.inputs["right"])
        left_offsets, left_counts, left_bounds, left_vx, left_vy = _polygon_arrays(left, np)
        right_offsets, right_counts, right_bounds, right_vx, right_vy = _polygon_arrays(right, np)
        left_offsets_gpu = cp.asarray(left_offsets)
        left_counts_gpu = cp.asarray(left_counts)
        left_bounds_gpu = cp.asarray(left_bounds)
        left_vx_gpu = cp.asarray(left_vx)
        left_vy_gpu = cp.asarray(left_vy)
        right_offsets_gpu = cp.asarray(right_offsets)
        right_counts_gpu = cp.asarray(right_counts)
        right_bounds_gpu = cp.asarray(right_bounds)
        right_vx_gpu = cp.asarray(right_vx)
        right_vy_gpu = cp.asarray(right_vy)
        candidate_pair_count = int(len(left) * len(right))
        flags = cp.zeros((candidate_pair_count,), dtype=cp.uint8)
        kernel = cp.RawKernel(OVERLAY_ACTIVE_COUNT_KERNEL, "rtdl_goal3589_overlay_active_count_flags")
        blocks = (candidate_pair_count + threads - 1) // threads
        prepare_sec = time.perf_counter() - prepare_start
        timed = _time_cupy_flags(
            cp=cp,
            flags=flags,
            repeat=repeat,
            warmup=warmup,
            stability_label="overlay_seed/cupy_dense_all_pairs",
            launch=lambda: kernel(
                (blocks,),
                (threads,),
                (
                    left_offsets_gpu,
                    left_counts_gpu,
                    left_bounds_gpu,
                    left_vx_gpu,
                    left_vy_gpu,
                    len(left),
                    right_offsets_gpu,
                    right_counts_gpu,
                    right_bounds_gpu,
                    right_vx_gpu,
                    right_vy_gpu,
                    len(right),
                    flags,
                ),
            ),
        )
        input_counts = {"left_shape_count": len(left), "right_shape_count": len(right)}
        output_contract = "overlay_active_pair_dependency_count"
        baseline_kind = "cupy_rawkernel_cuda_core_dense_shape_pair_active_count"

    return {
        "backend": "cupy",
        "partner": "cupy",
        "rt_core_accelerated": False,
        "partner_accelerated": True,
        "baseline_kind": baseline_kind,
        "dataset": dataset,
        "dataset_note": case.note,
        "output_contract": output_contract,
        "prepare_sec": prepare_sec,
        "hot_median_sec": timed["hot_median_sec"],
        "hot_total_sec": timed["hot_total_sec"],
        "hot_repeat_secs": timed["hot_repeat_secs"],
        "row_count": timed["count"],
        "candidate_pair_count": candidate_pair_count,
        "input_counts": input_counts,
        "same_contract_baseline": True,
        "claim_boundary": _claim_boundary(),
    }


def run_rtdl_optix(workload: str, dataset: str, *, repeat: int, warmup: int) -> dict[str, object]:
    if workload == "pip":
        payload = run_rayjoin_prepared_optix_cupy_refined_pip(
            dataset=dataset,
            result_mode="count",
            include_rows=False,
            query_repeat=repeat,
            warmup=warmup,
        )
        route = "prepared_optix_cupy_refined_pip"
    elif workload == "lsi":
        payload = run_rayjoin_prepared_optix_left_id_dense_count_workload(
            "lsi",
            dataset=dataset,
            include_rows=False,
            query_repeat=repeat,
            warmup=warmup,
        )
        route = "prepared_optix_left_id_dense_count"
    else:
        payload = run_rayjoin_prepared_optix_shape_pair_active_count_workload(
            "overlay_seed",
            dataset=dataset,
            query_repeat=repeat,
            warmup=warmup,
        )
        route = "prepared_optix_shape_pair_active_count"
    phases = payload["phases_sec"]
    return {
        "backend": payload.get("backend", "optix"),
        "execution_route": route,
        "rt_core_accelerated": True,
        "partner_accelerated": workload == "pip",
        "dataset": dataset,
        "output_contract": payload["summary"]["output_contract"],
        "prepare_sec": {
            key: value
            for key, value in phases.items()
            if key.startswith("prepare_") or key.endswith("_pack_sec") or key.endswith("_refiner_sec")
        },
        "hot_median_sec": float(phases["prepared_query_sec"]),
        "hot_total_sec": float(phases["prepared_query_sec_total_sec"]),
        "hot_repeat": int(phases["prepared_query_sec_repeat"]),
        "hot_warmup": int(phases["prepared_query_sec_warmup"]),
        "row_count": int(payload["row_count"]),
        "device_resident_continuation_status": payload.get("device_resident_continuation_status"),
        "claim_boundary": payload.get("claim_boundary", _claim_boundary()),
    }


def build_dry_run(*, tier: str, workloads: tuple[str, ...], repeat: int, warmup: int) -> dict[str, object]:
    rows = []
    for workload in workloads:
        dataset = _dataset_for(workload, tier)
        case = _load_rayjoin_case(workload, dataset, segment_column_inputs=workload == "lsi")
        if workload == "pip":
            input_counts = {
                "point_count": len(case.inputs["points"]),
                "shape_count": len(case.inputs["polygons"]),
            }
            candidate_pair_count = input_counts["point_count"] * input_counts["shape_count"]
        elif workload == "lsi":
            input_counts = {
                "left_segment_count": len(case.inputs["left"]),
                "right_segment_count": len(case.inputs["right"]),
            }
            candidate_pair_count = input_counts["left_segment_count"] * input_counts["right_segment_count"]
        else:
            input_counts = {
                "left_shape_count": len(case.inputs["left"]),
                "right_shape_count": len(case.inputs["right"]),
            }
            candidate_pair_count = input_counts["left_shape_count"] * input_counts["right_shape_count"]
        rows.append(
            {
                "workload": workload,
                "dataset": dataset,
                "dataset_note": case.note,
                "input_counts": input_counts,
                "candidate_pair_count": candidate_pair_count,
                "planned_cupy_baseline": "dense CUDA-core all-pairs count over the same authored contract",
                "planned_rtdl_optix": "hot prepared-query promoted route",
            }
        )
    return {
        "schema": SCHEMA,
        "dry_run": True,
        "tier": tier,
        "repeat": repeat,
        "warmup": warmup,
        "rows": rows,
        "claim_boundary": _claim_boundary(),
    }


def run_packet(*, tier: str, workloads: tuple[str, ...], repeat: int, warmup: int, skip_optix: bool) -> dict[str, object]:
    rows = []
    for workload in workloads:
        dataset = _dataset_for(workload, tier)
        print(f"[goal3589] workload={workload} dataset={dataset} CuPy baseline start", flush=True)
        cupy = run_cupy_baseline(workload, dataset, repeat=repeat, warmup=warmup)
        rtdl_optix = None
        if not skip_optix:
            print(f"[goal3589] workload={workload} dataset={dataset} RTDL/OptiX route start", flush=True)
            rtdl_optix = run_rtdl_optix(workload, dataset, repeat=repeat, warmup=warmup)
            if int(rtdl_optix["row_count"]) != int(cupy["row_count"]):
                raise RuntimeError(
                    f"{workload} count mismatch: RTDL/OptiX={rtdl_optix['row_count']} CuPy={cupy['row_count']}"
                )
        speedup = None
        if rtdl_optix is not None and float(rtdl_optix["hot_median_sec"]) > 0.0:
            speedup = float(cupy["hot_median_sec"]) / float(rtdl_optix["hot_median_sec"])
        rows.append(
            {
                "workload": workload,
                "dataset": dataset,
                "cupy_cuda_core_baseline": cupy,
                "rtdl_optix": rtdl_optix,
                "counts_match": (
                    None
                    if rtdl_optix is None
                    else int(rtdl_optix["row_count"]) == int(cupy["row_count"])
                ),
                "rtdl_optix_speedup_vs_cupy_cuda_core": speedup,
                "interpretation": (
                    "RTDL/OptiX faster than this dense CuPy CUDA-core baseline"
                    if speedup is not None and speedup > 1.0
                    else (
                        "CuPy CUDA-core baseline faster or tied; use as optimization pressure"
                        if speedup is not None
                        else "CuPy-only run"
                    )
                ),
                "claim_boundary": _claim_boundary(),
            }
        )
    ratios = [
        float(row["rtdl_optix_speedup_vs_cupy_cuda_core"])
        for row in rows
        if isinstance(row.get("rtdl_optix_speedup_vs_cupy_cuda_core"), (int, float))
    ]
    return {
        "schema": SCHEMA,
        "dry_run": False,
        "generated_at_unix": time.time(),
        "git_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "git_status_short": _command_output(["git", "status", "--short"]),
        "tier": tier,
        "repeat": repeat,
        "warmup": warmup,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "all_counts_match": all(row["counts_match"] is not False for row in rows),
            "min_rtdl_optix_speedup_vs_cupy_cuda_core": min(ratios) if ratios else None,
            "geomean_rtdl_optix_speedup_vs_cupy_cuda_core": (
                pow(__import__("math").prod(ratios), 1.0 / len(ratios)) if ratios else None
            ),
            "same_contract_cuda_core_baseline_complete": not skip_optix and len(rows) == len(workloads),
        },
        "boundary": (
            "This packet compares hot prepared RTDL/OptiX routes against dense CuPy CUDA-core "
            "same-contract baselines on derived authored tiled fixtures. It is not a RayJoin paper "
            "reproduction and does not authorize public speedup wording."
        ),
        "claim_boundary": _claim_boundary(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal3589 RayJoin same-contract CuPy baseline.")
    parser.add_argument("--tier", choices=tuple(TIER_SUFFIX), default="standard")
    parser.add_argument("--workloads", default="all", help="Comma-separated subset or 'all'.")
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--skip-optix", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_ARTIFACT)
    args = parser.parse_args(argv)
    if args.repeat <= 0:
        raise ValueError("--repeat must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")
    workloads = _workload_list(args.workloads)
    payload = (
        build_dry_run(tier=args.tier, workloads=workloads, repeat=args.repeat, warmup=args.warmup)
        if args.dry_run
        else run_packet(
            tier=args.tier,
            workloads=workloads,
            repeat=args.repeat,
            warmup=args.warmup,
            skip_optix=args.skip_optix,
        )
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3589] wrote {args.output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
