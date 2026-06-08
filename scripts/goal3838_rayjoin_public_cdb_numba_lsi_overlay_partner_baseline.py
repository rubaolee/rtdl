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

from examples.v2_0.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    _load_rayjoin_case,
)
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import _claim_boundary  # noqa: E402
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import _polygon_arrays  # noqa: E402
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import _segment_array  # noqa: E402
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import run_cupy_baseline  # noqa: E402
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import run_rtdl_optix  # noqa: E402


SCHEMA = "rtdl.goal3838.rayjoin_public_cdb_numba_lsi_overlay_partner_baseline.v1"
DEFAULT_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_a5000"
    / "summary.json"
)
CASE_ORDER = ("lsi_county512_soil512", "overlay_county512_soil512")
WORKLOAD_BY_CASE = {
    "lsi_county512_soil512": "lsi",
    "overlay_county512_soil512": "overlay_seed",
}

_NUMBA_LSI_COUNT_KERNEL: Any | None = None
_NUMBA_OVERLAY_ACTIVE_COUNT_KERNEL: Any | None = None


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def _activate_numba_cuda_redirector() -> None:
    try:
        import _numba_cuda_redirector  # noqa: F401
    except ImportError:
        pass


def _case_dataset(case_id: str, data_dir: Path) -> str:
    county = data_dir / "br_county_start256_count512.cdb"
    soil = data_dir / "br_soil_start256_count512.cdb"
    if case_id in CASE_ORDER:
        return f"{county} + {soil}"
    raise ValueError(f"unknown case id: {case_id}")


def _selected_cases(value: str) -> tuple[str, ...]:
    if value == "all":
        return CASE_ORDER
    selected = tuple(part.strip() for part in value.split(",") if part.strip())
    if not selected:
        raise ValueError("case list is empty")
    for case_id in selected:
        if case_id not in CASE_ORDER:
            raise ValueError(f"unknown case id: {case_id}")
    return selected


def _numba_lsi_count_kernel(cuda: Any) -> Any:
    global _NUMBA_LSI_COUNT_KERNEL
    if _NUMBA_LSI_COUNT_KERNEL is not None:
        return _NUMBA_LSI_COUNT_KERNEL

    @cuda.jit
    def lsi_count(left, right, left_count, right_count, count_out):
        idx = cuda.grid(1)
        total = left_count * right_count
        if idx >= total:
            return
        li = idx // right_count
        ri = idx - li * right_count
        ax0 = left[li, 0]
        ay0 = left[li, 1]
        ax1 = left[li, 2]
        ay1 = left[li, 3]
        bx0 = right[ri, 0]
        by0 = right[ri, 1]
        bx1 = right[ri, 2]
        by1 = right[ri, 3]
        rx = ax1 - ax0
        ry = ay1 - ay0
        sx = bx1 - bx0
        sy = by1 - by0
        denom = rx * sy - ry * sx
        if abs(denom) < 1.0e-7:
            return
        qpx = bx0 - ax0
        qpy = by0 - ay0
        t = (qpx * sy - qpy * sx) / denom
        u = (qpx * ry - qpy * rx) / denom
        if t >= 0.0 and t <= 1.0 and u >= 0.0 and u <= 1.0:
            cuda.atomic.add(count_out, 0, 1)

    _NUMBA_LSI_COUNT_KERNEL = lsi_count
    return lsi_count


def _numba_overlay_active_count_kernel(cuda: Any) -> Any:
    global _NUMBA_OVERLAY_ACTIVE_COUNT_KERNEL
    if _NUMBA_OVERLAY_ACTIVE_COUNT_KERNEL is not None:
        return _NUMBA_OVERLAY_ACTIVE_COUNT_KERNEL

    @cuda.jit
    def overlay_active_count(
        left_offsets,
        left_counts,
        left_bounds,
        left_vx,
        left_vy,
        left_count,
        right_offsets,
        right_counts,
        right_bounds,
        right_vx,
        right_vy,
        right_count,
        count_out,
    ):
        idx = cuda.grid(1)
        total = left_count * right_count
        if idx >= total:
            return
        li = idx // right_count
        ri = idx - li * right_count
        if (
            left_bounds[li * 4 + 2] < right_bounds[ri * 4 + 0]
            or right_bounds[ri * 4 + 2] < left_bounds[li * 4 + 0]
            or left_bounds[li * 4 + 3] < right_bounds[ri * 4 + 1]
            or right_bounds[ri * 4 + 3] < left_bounds[li * 4 + 1]
        ):
            return

        loff = left_offsets[li]
        lcnt = left_counts[li]
        roff = right_offsets[ri]
        rcnt = right_counts[ri]

        for le in range(lcnt):
            le_next = le + 1
            if le_next == lcnt:
                le_next = 0
            ax0 = left_vx[loff + le]
            ay0 = left_vy[loff + le]
            ax1 = left_vx[loff + le_next]
            ay1 = left_vy[loff + le_next]
            rx = ax1 - ax0
            ry = ay1 - ay0
            for re in range(rcnt):
                re_next = re + 1
                if re_next == rcnt:
                    re_next = 0
                bx0 = right_vx[roff + re]
                by0 = right_vy[roff + re]
                bx1 = right_vx[roff + re_next]
                by1 = right_vy[roff + re_next]
                sx = bx1 - bx0
                sy = by1 - by0
                denom = rx * sy - ry * sx
                if abs(denom) < 1.0e-7:
                    continue
                qpx = bx0 - ax0
                qpy = by0 - ay0
                t = (qpx * sy - qpy * sx) / denom
                u = (qpx * ry - qpy * rx) / denom
                if t >= 0.0 and t <= 1.0 and u >= 0.0 and u <= 1.0:
                    cuda.atomic.add(count_out, 0, 1)
                    return

        lx0 = left_vx[loff]
        ly0 = left_vy[loff]
        on_segment = False
        j = rcnt - 1
        for i in range(rcnt):
            ax = right_vx[roff + j]
            ay = right_vy[roff + j]
            bx = right_vx[roff + i]
            by = right_vy[roff + i]
            dx = bx - ax
            dy = by - ay
            cross = (lx0 - ax) * dy - (ly0 - ay) * dx
            min_x = ax if ax < bx else bx
            max_x = ax if ax > bx else bx
            min_y = ay if ay < by else by
            max_y = ay if ay > by else by
            if (
                abs(cross) <= 1.0e-5
                and lx0 >= min_x - 1.0e-5
                and lx0 <= max_x + 1.0e-5
                and ly0 >= min_y - 1.0e-5
                and ly0 <= max_y + 1.0e-5
            ):
                on_segment = True
                break
            j = i
        if on_segment:
            cuda.atomic.add(count_out, 0, 1)
            return
        inside = False
        j = rcnt - 1
        for i in range(rcnt):
            xi = right_vx[roff + i]
            yi = right_vy[roff + i]
            xj = right_vx[roff + j]
            yj = right_vy[roff + j]
            if (yi > ly0) != (yj > ly0):
                denom = yj - yi
                if denom == 0.0:
                    denom = 1.0e-20
                x_cross = (xj - xi) * (ly0 - yi) / denom + xi
                if lx0 <= x_cross:
                    inside = not inside
            j = i
        if inside:
            cuda.atomic.add(count_out, 0, 1)
            return

        rx0 = right_vx[roff]
        ry0 = right_vy[roff]
        on_segment = False
        j = lcnt - 1
        for i in range(lcnt):
            ax = left_vx[loff + j]
            ay = left_vy[loff + j]
            bx = left_vx[loff + i]
            by = left_vy[loff + i]
            dx = bx - ax
            dy = by - ay
            cross = (rx0 - ax) * dy - (ry0 - ay) * dx
            min_x = ax if ax < bx else bx
            max_x = ax if ax > bx else bx
            min_y = ay if ay < by else by
            max_y = ay if ay > by else by
            if (
                abs(cross) <= 1.0e-5
                and rx0 >= min_x - 1.0e-5
                and rx0 <= max_x + 1.0e-5
                and ry0 >= min_y - 1.0e-5
                and ry0 <= max_y + 1.0e-5
            ):
                on_segment = True
                break
            j = i
        if on_segment:
            cuda.atomic.add(count_out, 0, 1)
            return
        inside = False
        j = lcnt - 1
        for i in range(lcnt):
            xi = left_vx[loff + i]
            yi = left_vy[loff + i]
            xj = left_vx[loff + j]
            yj = left_vy[loff + j]
            if (yi > ry0) != (yj > ry0):
                denom = yj - yi
                if denom == 0.0:
                    denom = 1.0e-20
                x_cross = (xj - xi) * (ry0 - yi) / denom + xi
                if rx0 <= x_cross:
                    inside = not inside
            j = i
        if inside:
            cuda.atomic.add(count_out, 0, 1)

    _NUMBA_OVERLAY_ACTIVE_COUNT_KERNEL = overlay_active_count
    return overlay_active_count


def _time_numba_count(
    *,
    cuda: Any,
    count_gpu: Any,
    zero: Any,
    repeat: int,
    warmup: int,
    launch,
    stability_label: str,
) -> dict[str, object]:
    measured: list[float] = []
    counts: list[int] = []
    runs: list[dict[str, object]] = []
    for iteration in range(warmup + repeat):
        count_gpu.copy_to_device(zero)
        cuda.synchronize()
        start = time.perf_counter()
        launch()
        count = int(count_gpu.copy_to_host()[0])
        cuda.synchronize()
        elapsed = time.perf_counter() - start
        is_warmup = iteration < warmup
        print(
            f"[goal3838] {stability_label} {'warmup' if is_warmup else 'repeat'} "
            f"{iteration + 1}/{warmup + repeat} elapsed={elapsed:.6f}s count={count}",
            flush=True,
        )
        runs.append({"iteration": iteration, "is_warmup": is_warmup, "elapsed_sec": elapsed, "count": count})
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


def run_numba_baseline(
    workload: str,
    dataset: str,
    *,
    repeat: int,
    warmup: int,
    block_size: int = 128,
) -> dict[str, object]:
    _activate_numba_cuda_redirector()
    import numpy as np
    import numba
    from numba import cuda

    if not cuda.is_available():
        raise RuntimeError("Numba CUDA is unavailable")
    if workload not in {"lsi", "overlay_seed"}:
        raise ValueError("Goal3838 supports only lsi and overlay_seed")
    if repeat <= 0:
        raise ValueError("repeat must be positive")
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    if block_size <= 0:
        raise ValueError("block_size must be positive")

    case = _load_rayjoin_case(workload, dataset, segment_column_inputs=workload == "lsi")
    prepare_start = time.perf_counter()
    count_gpu = cuda.device_array((1,), dtype=np.int64)
    zero = np.zeros((1,), dtype=np.int64)

    if workload == "lsi":
        left_array = _segment_array(case.inputs["left"], np)
        right_array = _segment_array(case.inputs["right"], np)
        left_count = int(left_array.shape[0])
        right_count = int(right_array.shape[0])
        left_gpu = cuda.to_device(left_array)
        right_gpu = cuda.to_device(right_array)
        candidate_pair_count = int(left_count * right_count)
        blocks = (candidate_pair_count + block_size - 1) // block_size
        kernel = _numba_lsi_count_kernel(cuda)
        prepare_sec = time.perf_counter() - prepare_start
        timed = _time_numba_count(
            cuda=cuda,
            count_gpu=count_gpu,
            zero=zero,
            repeat=repeat,
            warmup=warmup,
            stability_label="lsi/numba_dense_all_pairs_scalar_count",
            launch=lambda: kernel[blocks, block_size](left_gpu, right_gpu, left_count, right_count, count_gpu),
        )
        input_counts = {"left_segment_count": left_count, "right_segment_count": right_count}
        output_contract = "segment_segment_intersection_count"
        baseline_kind = "numba_cuda_jit_dense_lsi_scalar_count"
    else:
        left = tuple(case.inputs["left"])
        right = tuple(case.inputs["right"])
        left_offsets, left_counts, left_bounds, left_vx, left_vy = _polygon_arrays(left, np)
        right_offsets, right_counts, right_bounds, right_vx, right_vy = _polygon_arrays(right, np)
        left_offsets_gpu = cuda.to_device(left_offsets)
        left_counts_gpu = cuda.to_device(left_counts)
        left_bounds_gpu = cuda.to_device(np.asarray(left_bounds, dtype=np.float64).reshape(-1))
        left_vx_gpu = cuda.to_device(left_vx)
        left_vy_gpu = cuda.to_device(left_vy)
        right_offsets_gpu = cuda.to_device(right_offsets)
        right_counts_gpu = cuda.to_device(right_counts)
        right_bounds_gpu = cuda.to_device(np.asarray(right_bounds, dtype=np.float64).reshape(-1))
        right_vx_gpu = cuda.to_device(right_vx)
        right_vy_gpu = cuda.to_device(right_vy)
        left_count = len(left)
        right_count = len(right)
        candidate_pair_count = int(left_count * right_count)
        blocks = (candidate_pair_count + block_size - 1) // block_size
        kernel = _numba_overlay_active_count_kernel(cuda)
        prepare_sec = time.perf_counter() - prepare_start
        timed = _time_numba_count(
            cuda=cuda,
            count_gpu=count_gpu,
            zero=zero,
            repeat=repeat,
            warmup=warmup,
            stability_label="overlay_seed/numba_dense_all_pairs_scalar_count",
            launch=lambda: kernel[blocks, block_size](
                left_offsets_gpu,
                left_counts_gpu,
                left_bounds_gpu,
                left_vx_gpu,
                left_vy_gpu,
                left_count,
                right_offsets_gpu,
                right_counts_gpu,
                right_bounds_gpu,
                right_vx_gpu,
                right_vy_gpu,
                right_count,
                count_gpu,
            ),
        )
        input_counts = {"left_shape_count": left_count, "right_shape_count": right_count}
        output_contract = "overlay_active_pair_dependency_count"
        baseline_kind = "numba_cuda_jit_dense_shape_pair_active_scalar_count"

    return {
        "backend": "numba_cuda",
        "partner": "numba",
        "rt_core_accelerated": False,
        "partner_accelerated": True,
        "raw_kernel_required": False,
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
        "block_size": int(block_size),
        "numba_version": numba.__version__,
        "numba_cuda_module": str(getattr(cuda, "__file__", "")),
        "runs": timed["runs"],
        "claim_boundary": _claim_boundary(),
    }


def build_dry_run(*, data_dir: Path, cases: tuple[str, ...], repeat: int, warmup: int, block_size: int) -> dict[str, object]:
    rows = []
    for case_id in cases:
        rows.append(
            {
                "case_id": case_id,
                "workload": WORKLOAD_BY_CASE[case_id],
                "dataset": _case_dataset(case_id, data_dir),
                "planned_numba_baseline": "Numba CUDA JIT dense all-pairs scalar count; no CuPy RawKernel required",
                "planned_cupy_baseline": "Goal3589 CuPy RawKernel dense same-contract scalar count",
                "planned_rtdl_optix": "Goal3589 hot prepared RTDL/OptiX route for context",
            }
        )
    return {
        "schema": SCHEMA,
        "dry_run": True,
        "cases": list(cases),
        "repeat": repeat,
        "warmup": warmup,
        "block_size": block_size,
        "rows": rows,
        "claim_boundary": _claim_boundary(),
    }


def run_probe(
    *,
    data_dir: Path,
    cases: tuple[str, ...],
    repeat: int,
    warmup: int,
    block_size: int,
    skip_cupy: bool,
    skip_optix: bool,
) -> dict[str, object]:
    rows = []
    for case_id in cases:
        workload = WORKLOAD_BY_CASE[case_id]
        dataset = _case_dataset(case_id, data_dir)
        for part in (piece.strip() for piece in dataset.split("+")):
            if part and not Path(part).exists():
                raise FileNotFoundError(part)
        print(f"[goal3838] {case_id} Numba baseline start", flush=True)
        numba_row = run_numba_baseline(workload, dataset, repeat=repeat, warmup=warmup, block_size=block_size)

        cupy_row = None
        if not skip_cupy:
            print(f"[goal3838] {case_id} CuPy baseline start", flush=True)
            cupy_row = run_cupy_baseline(workload, dataset, repeat=repeat, warmup=warmup)
            if int(cupy_row["row_count"]) != int(numba_row["row_count"]):
                raise RuntimeError(
                    f"Numba/CuPy {workload} count mismatch: "
                    f"Numba={numba_row['row_count']} CuPy={cupy_row['row_count']}"
                )

        rtdl_optix = None
        if not skip_optix:
            print(f"[goal3838] {case_id} RTDL/OptiX route start", flush=True)
            rtdl_optix = run_rtdl_optix(workload, dataset, repeat=repeat, warmup=warmup)
            if int(rtdl_optix["row_count"]) != int(numba_row["row_count"]):
                raise RuntimeError(
                    f"Numba/RTDL {workload} count mismatch: "
                    f"Numba={numba_row['row_count']} RTDL={rtdl_optix['row_count']}"
                )

        cupy_speedup_vs_numba = None
        if cupy_row is not None and float(numba_row["hot_median_sec"]) > 0.0:
            cupy_speedup_vs_numba = float(cupy_row["hot_median_sec"]) / float(numba_row["hot_median_sec"])
        numba_speedup_vs_rtdl_optix = None
        if rtdl_optix is not None and float(rtdl_optix["hot_median_sec"]) > 0.0:
            numba_speedup_vs_rtdl_optix = float(rtdl_optix["hot_median_sec"]) / float(numba_row["hot_median_sec"])

        rows.append(
            {
                "case_id": case_id,
                "workload": workload,
                "dataset": dataset,
                "numba_cuda_jit_baseline": numba_row,
                "cupy_cuda_core_baseline": cupy_row,
                "rtdl_optix": rtdl_optix,
                "counts_match": (
                    (cupy_row is None or int(cupy_row["row_count"]) == int(numba_row["row_count"]))
                    and (rtdl_optix is None or int(rtdl_optix["row_count"]) == int(numba_row["row_count"]))
                ),
                "cupy_speedup_vs_numba": cupy_speedup_vs_numba,
                "numba_speedup_vs_rtdl_optix": numba_speedup_vs_rtdl_optix,
                "claim_boundary": _claim_boundary(),
            }
        )

    return {
        "schema": SCHEMA,
        "dry_run": False,
        "generated_at_unix": time.time(),
        "git_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "git_status_short": _command_output(["git", "status", "--short"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "data_dir": str(data_dir),
        "cases": list(cases),
        "repeat": repeat,
        "warmup": warmup,
        "block_size": block_size,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "all_counts_match": all(bool(row["counts_match"]) for row in rows),
            "numba_no_rawkernel_route_available_for_all_cases": True,
        },
        "boundary": (
            "This is a RayJoin LSI/overlay partner-coverage probe. It validates "
            "Numba CUDA JIT same-contract scalar-count routes so users are not "
            "forced to write CuPy RawKernel for these custom continuations. It is "
            "not automatic dispatch, not a RayJoin paper reproduction, and not "
            "release evidence."
        ),
        "claim_boundary": _claim_boundary(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal3838 RayJoin public-CDB Numba LSI/overlay partner baseline.")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--cases", default="all")
    parser.add_argument("--repeat", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--block-size", type=int, default=128)
    parser.add_argument("--skip-cupy", action="store_true")
    parser.add_argument("--skip-optix", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_ARTIFACT)
    args = parser.parse_args(argv)
    if args.repeat <= 0:
        raise ValueError("--repeat must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")
    if args.block_size <= 0:
        raise ValueError("--block-size must be positive")
    cases = _selected_cases(args.cases)
    payload = (
        build_dry_run(data_dir=args.data_dir, cases=cases, repeat=args.repeat, warmup=args.warmup, block_size=args.block_size)
        if args.dry_run
        else run_probe(
            data_dir=args.data_dir,
            cases=cases,
            repeat=args.repeat,
            warmup=args.warmup,
            block_size=args.block_size,
            skip_cupy=args.skip_cupy,
            skip_optix=args.skip_optix,
        )
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3838] wrote {args.output}", flush=True)
    if not args.dry_run:
        print(json.dumps(payload["summary"], indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
