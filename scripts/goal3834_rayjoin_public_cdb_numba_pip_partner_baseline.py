#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
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
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import _point_arrays  # noqa: E402
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import _polygon_arrays  # noqa: E402
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import run_cupy_baseline  # noqa: E402
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import run_rtdl_optix  # noqa: E402


SCHEMA = "rtdl.goal3834.rayjoin_public_cdb_numba_pip_partner_baseline.v1"
DEFAULT_ARTIFACT = (
    ROOT / "docs" / "reports" / "goal3834_rayjoin_public_cdb_numba_pip_partner_a5000" / "summary.json"
)
CASE_ID = "pip_county512"
_NUMBA_PIP_COUNT_KERNEL: Any | None = None


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _case_dataset(data_dir: Path) -> str:
    return str(data_dir / "br_county_start256_count512.cdb")


def _median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def _activate_numba_cuda_redirector() -> None:
    try:
        import _numba_cuda_redirector  # noqa: F401
    except ImportError:
        pass


def _numba_pip_count_kernel(cuda: Any) -> Any:
    global _NUMBA_PIP_COUNT_KERNEL
    if _NUMBA_PIP_COUNT_KERNEL is not None:
        return _NUMBA_PIP_COUNT_KERNEL

    @cuda.jit
    def pip_count(
        px,
        py,
        point_count,
        shape_offsets,
        shape_counts,
        bounds,
        vx,
        vy,
        shape_count,
        count_out,
    ):
        idx = cuda.grid(1)
        total = point_count * shape_count
        if idx >= total:
            return
        pi = idx // shape_count
        si = idx - pi * shape_count
        x = px[pi]
        y = py[pi]
        min_x = bounds[si * 4 + 0]
        min_y = bounds[si * 4 + 1]
        max_x = bounds[si * 4 + 2]
        max_y = bounds[si * 4 + 3]
        if x < min_x or x > max_x or y < min_y or y > max_y:
            return

        off = shape_offsets[si]
        n = shape_counts[si]
        for i in range(n):
            j = i + 1
            if j == n:
                j = 0
            ax = vx[off + i]
            ay = vy[off + i]
            bx = vx[off + j]
            by = vy[off + j]
            dx = bx - ax
            dy = by - ay
            cross = (x - ax) * dy - (y - ay) * dx
            dot = (x - ax) * dx + (y - ay) * dy
            len2 = dx * dx + dy * dy
            if abs(cross) <= 1.0e-9 * math.sqrt(len2) and dot >= -1.0e-9 and dot <= len2 + 1.0e-9:
                cuda.atomic.add(count_out, 0, 1)
                return

        inside = False
        j = n - 1
        for i in range(n):
            xi = vx[off + i]
            yi = vy[off + i]
            xj = vx[off + j]
            yj = vy[off + j]
            if (yi > y) != (yj > y):
                denom = yj - yi
                if denom == 0.0:
                    denom = 1.0e-20
                x_cross = (xj - xi) * (y - yi) / denom + xi
                if x <= x_cross:
                    inside = not inside
            j = i
        if inside:
            cuda.atomic.add(count_out, 0, 1)

    _NUMBA_PIP_COUNT_KERNEL = pip_count
    return pip_count


def run_numba_pip_baseline(
    dataset: str,
    *,
    repeat: int,
    warmup: int,
    block_size: int = 256,
) -> dict[str, object]:
    _activate_numba_cuda_redirector()
    import numpy as np
    import numba
    from numba import cuda

    if not cuda.is_available():
        raise RuntimeError("Numba CUDA is unavailable")
    if repeat <= 0:
        raise ValueError("repeat must be positive")
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    if block_size <= 0:
        raise ValueError("block_size must be positive")

    case = _load_rayjoin_case("pip", dataset)
    prepare_start = time.perf_counter()
    points = tuple(case.inputs["points"])
    shapes = tuple(case.inputs["polygons"])
    point_x, point_y = _point_arrays(points, np)
    shape_offsets, shape_counts, bounds, vx, vy = _polygon_arrays(shapes, np)
    bounds_flat = np.asarray(bounds, dtype=np.float64).reshape(-1)

    px_gpu = cuda.to_device(point_x)
    py_gpu = cuda.to_device(point_y)
    shape_offsets_gpu = cuda.to_device(shape_offsets)
    shape_counts_gpu = cuda.to_device(shape_counts)
    bounds_gpu = cuda.to_device(bounds_flat)
    vx_gpu = cuda.to_device(vx)
    vy_gpu = cuda.to_device(vy)
    count_gpu = cuda.device_array((1,), dtype=np.int64)
    zero = np.zeros((1,), dtype=np.int64)
    candidate_pair_count = int(len(points) * len(shapes))
    blocks = (candidate_pair_count + block_size - 1) // block_size
    kernel = _numba_pip_count_kernel(cuda)
    prepare_sec = time.perf_counter() - prepare_start

    measured: list[float] = []
    counts: list[int] = []
    runs: list[dict[str, object]] = []
    for iteration in range(warmup + repeat):
        count_gpu.copy_to_device(zero)
        cuda.synchronize()
        start = time.perf_counter()
        kernel[blocks, block_size](
            px_gpu,
            py_gpu,
            len(points),
            shape_offsets_gpu,
            shape_counts_gpu,
            bounds_gpu,
            vx_gpu,
            vy_gpu,
            len(shapes),
            count_gpu,
        )
        count = int(count_gpu.copy_to_host()[0])
        cuda.synchronize()
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
            f"[goal3834] pip/numba_dense_all_pairs_scalar_count "
            f"{'warmup' if is_warmup else 'repeat'} {iteration + 1}/{warmup + repeat} "
            f"elapsed={elapsed:.6f}s count={count}",
            flush=True,
        )
        if not is_warmup:
            measured.append(elapsed)
            counts.append(count)
    if len(set(counts)) != 1:
        raise RuntimeError(f"Numba PIP count changed across repeats: {counts}")

    return {
        "backend": "numba_cuda",
        "partner": "numba",
        "rt_core_accelerated": False,
        "partner_accelerated": True,
        "raw_kernel_required": False,
        "baseline_kind": "numba_cuda_jit_dense_pip_scalar_count",
        "dataset": dataset,
        "dataset_note": case.note,
        "output_contract": "point_to_shape_positive_hit_count",
        "prepare_sec": prepare_sec,
        "hot_median_sec": _median(measured),
        "hot_total_sec": float(sum(measured)),
        "hot_repeat_secs": measured,
        "row_count": counts[-1] if counts else 0,
        "candidate_pair_count": candidate_pair_count,
        "input_counts": {"point_count": len(points), "shape_count": len(shapes)},
        "same_contract_baseline": True,
        "same_contract_with_goal3589_cupy_pip": True,
        "block_size": int(block_size),
        "numba_version": numba.__version__,
        "numba_cuda_module": str(getattr(cuda, "__file__", "")),
        "runs": runs,
        "claim_boundary": _claim_boundary(),
    }


def build_dry_run(*, data_dir: Path, repeat: int, warmup: int, block_size: int) -> dict[str, object]:
    dataset = _case_dataset(data_dir)
    return {
        "schema": SCHEMA,
        "dry_run": True,
        "case_id": CASE_ID,
        "workload": "pip",
        "dataset": dataset,
        "repeat": repeat,
        "warmup": warmup,
        "block_size": block_size,
        "planned_numba_baseline": "Numba CUDA JIT dense all-pairs scalar count; no CuPy RawKernel required",
        "planned_cupy_baseline": "Goal3589 CuPy RawKernel dense same-contract scalar count",
        "planned_rtdl_optix": "Goal3589 hot prepared RTDL/OptiX PIP route for context",
        "claim_boundary": _claim_boundary(),
    }


def run_probe(
    *,
    data_dir: Path,
    repeat: int,
    warmup: int,
    block_size: int,
    skip_cupy: bool,
    skip_optix: bool,
) -> dict[str, object]:
    dataset = _case_dataset(data_dir)
    if not Path(dataset).exists():
        raise FileNotFoundError(dataset)
    print("[goal3834] Numba PIP baseline start", flush=True)
    numba_row = run_numba_pip_baseline(dataset, repeat=repeat, warmup=warmup, block_size=block_size)

    cupy_row = None
    if not skip_cupy:
        print("[goal3834] CuPy PIP baseline start", flush=True)
        cupy_row = run_cupy_baseline("pip", dataset, repeat=repeat, warmup=warmup)
        if int(cupy_row["row_count"]) != int(numba_row["row_count"]):
            raise RuntimeError(
                f"Numba/CuPy PIP count mismatch: Numba={numba_row['row_count']} CuPy={cupy_row['row_count']}"
            )

    rtdl_optix = None
    if not skip_optix:
        print("[goal3834] RTDL/OptiX PIP route start", flush=True)
        rtdl_optix = run_rtdl_optix("pip", dataset, repeat=repeat, warmup=warmup)
        if int(rtdl_optix["row_count"]) != int(numba_row["row_count"]):
            raise RuntimeError(
                f"Numba/RTDL PIP count mismatch: Numba={numba_row['row_count']} RTDL={rtdl_optix['row_count']}"
            )

    cupy_vs_numba = None
    if cupy_row is not None and float(numba_row["hot_median_sec"]) > 0.0:
        cupy_vs_numba = float(cupy_row["hot_median_sec"]) / float(numba_row["hot_median_sec"])
    rtdl_vs_numba = None
    if rtdl_optix is not None and float(rtdl_optix["hot_median_sec"]) > 0.0:
        rtdl_vs_numba = float(numba_row["hot_median_sec"]) / float(rtdl_optix["hot_median_sec"])

    counts_match = (
        (cupy_row is None or int(cupy_row["row_count"]) == int(numba_row["row_count"]))
        and (rtdl_optix is None or int(rtdl_optix["row_count"]) == int(numba_row["row_count"]))
    )
    return {
        "schema": SCHEMA,
        "dry_run": False,
        "generated_at_unix": time.time(),
        "git_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "git_status_short": _command_output(["git", "status", "--short"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "case_id": CASE_ID,
        "workload": "pip",
        "dataset": dataset,
        "repeat": repeat,
        "warmup": warmup,
        "block_size": block_size,
        "numba_cuda_jit_baseline": numba_row,
        "cupy_cuda_core_baseline": cupy_row,
        "rtdl_optix": rtdl_optix,
        "counts_match": counts_match,
        "cupy_speedup_vs_numba": cupy_vs_numba,
        "numba_speedup_vs_rtdl_optix": rtdl_vs_numba,
        "summary": {
            "all_counts_match": counts_match,
            "numba_no_rawkernel_route_available": True,
            "numba_row_count": int(numba_row["row_count"]),
            "cupy_row_count": None if cupy_row is None else int(cupy_row["row_count"]),
            "rtdl_optix_row_count": None if rtdl_optix is None else int(rtdl_optix["row_count"]),
        },
        "boundary": (
            "This is a RayJoin PIP partner-coverage probe. It validates a Numba CUDA JIT "
            "same-contract scalar-count route so users are not forced to write CuPy RawKernel "
            "for this custom logic. It is not automatic dispatch, not a RayJoin paper "
            "reproduction, and not release evidence."
        ),
        "claim_boundary": _claim_boundary(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal3834 RayJoin public-CDB Numba PIP partner baseline.")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--repeat", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--block-size", type=int, default=256)
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

    payload = (
        build_dry_run(data_dir=args.data_dir, repeat=args.repeat, warmup=args.warmup, block_size=args.block_size)
        if args.dry_run
        else run_probe(
            data_dir=args.data_dir,
            repeat=args.repeat,
            warmup=args.warmup,
            block_size=args.block_size,
            skip_cupy=args.skip_cupy,
            skip_optix=args.skip_optix,
        )
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3834] wrote {args.output}", flush=True)
    if not args.dry_run:
        print(json.dumps(payload["summary"], indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
