from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.apps.trajectory import rtdl_continuous_frechet_distance_app as app


def _median(values: list[float]) -> float:
    return float(statistics.median(values))


def _point_arrays(curve: tuple[object, ...]) -> tuple[list[float], list[float]]:
    return ([float(point.x) for point in curve], [float(point.y) for point in curve])


def _torch_free_interval(torch, ax, ay, bx, by, px, py, radius: float):
    vx = bx - ax
    vy = by - ay
    wx = ax - px
    wy = ay - py
    qa = vx * vx + vy * vy
    qb = 2.0 * (vx * wx + vy * wy)
    qc = wx * wx + wy * wy - radius * radius
    disc = qb * qb - 4.0 * qa * qc
    valid = disc >= -1.0e-12
    disc = torch.clamp(disc, min=0.0)
    root = torch.sqrt(disc)
    denom = 2.0 * qa
    lo = (-qb - root) / denom
    hi = (-qb + root) / denom
    lo = torch.clamp(lo, min=0.0)
    hi = torch.clamp(hi, max=1.0)
    valid = valid & (qa > 0.0) & (lo <= hi + 1.0e-12)
    return valid, lo, hi


def _torch_union(torch, a_valid, a_lo, a_hi, b_valid, b_lo, b_hi):
    inf = torch.full_like(a_lo, float("inf"))
    ninf = torch.full_like(a_lo, float("-inf"))
    lo = torch.minimum(torch.where(a_valid, a_lo, inf), torch.where(b_valid, b_lo, inf))
    hi = torch.maximum(torch.where(a_valid, a_hi, ninf), torch.where(b_valid, b_hi, ninf))
    valid = a_valid | b_valid
    return valid, lo, hi


def torch_cuda_continuous_frechet_decision(
    curve_p: tuple[object, ...],
    curve_q: tuple[object, ...],
    radius: float,
    *,
    device: str = "cuda",
) -> bool:
    import torch

    if len(curve_p) < 2 or len(curve_q) < 2:
        raise ValueError("continuous Frechet distance requires two curves with at least two points each")
    if radius < 0.0:
        return False
    px, py = _point_arrays(curve_p)
    qx, qy = _point_arrays(curve_q)
    p = torch.tensor(list(zip(px, py)), dtype=torch.float64, device=device)
    q = torch.tensor(list(zip(qx, qy)), dtype=torch.float64, device=device)
    if torch.linalg.vector_norm(p[0] - q[0]).item() > radius + 1.0e-12:
        return False
    if torch.linalg.vector_norm(p[-1] - q[-1]).item() > radius + 1.0e-12:
        return False

    p0 = p[:-1]
    p1 = p[1:]
    q0 = q[:-1]
    q1 = q[1:]
    n = int(p0.shape[0])
    m = int(q0.shape[0])

    # Precompute all cell-side free intervals on CUDA. The reachability DP
    # itself is still wavefront ordered because each cell depends on left and
    # bottom neighbors.
    bottom_valid, bottom_lo, bottom_hi = _torch_free_interval(
        torch,
        p0[:, 0:1],
        p0[:, 1:2],
        p1[:, 0:1],
        p1[:, 1:2],
        q0[:, 0].unsqueeze(0),
        q0[:, 1].unsqueeze(0),
        radius,
    )
    top_valid, top_lo, top_hi = _torch_free_interval(
        torch,
        p0[:, 0:1],
        p0[:, 1:2],
        p1[:, 0:1],
        p1[:, 1:2],
        q1[:, 0].unsqueeze(0),
        q1[:, 1].unsqueeze(0),
        radius,
    )
    left_valid, left_lo, left_hi = _torch_free_interval(
        torch,
        q0[:, 0].unsqueeze(0),
        q0[:, 1].unsqueeze(0),
        q1[:, 0].unsqueeze(0),
        q1[:, 1].unsqueeze(0),
        p0[:, 0:1],
        p0[:, 1:2],
        radius,
    )
    right_valid, right_lo, right_hi = _torch_free_interval(
        torch,
        q0[:, 0].unsqueeze(0),
        q0[:, 1].unsqueeze(0),
        q1[:, 0].unsqueeze(0),
        q1[:, 1].unsqueeze(0),
        p1[:, 0:1],
        p1[:, 1:2],
        radius,
    )

    reach_top_valid = torch.zeros((n, m), dtype=torch.bool, device=device)
    reach_top_lo = torch.zeros((n, m), dtype=torch.float64, device=device)
    reach_top_hi = torch.zeros((n, m), dtype=torch.float64, device=device)
    reach_right_valid = torch.zeros((n, m), dtype=torch.bool, device=device)
    reach_right_lo = torch.zeros((n, m), dtype=torch.float64, device=device)
    reach_right_hi = torch.zeros((n, m), dtype=torch.float64, device=device)

    for diag in range(n + m - 1):
        i0 = max(0, diag - (m - 1))
        i1 = min(n - 1, diag)
        ii = torch.arange(i0, i1 + 1, device=device, dtype=torch.long)
        jj = diag - ii
        size = int(ii.numel())

        b_valid = torch.zeros(size, dtype=torch.bool, device=device)
        b_lo = torch.zeros(size, dtype=torch.float64, device=device)
        b_hi = torch.zeros(size, dtype=torch.float64, device=device)

        from_left_cell = jj > 0
        if bool(from_left_cell.any()):
            b_valid[from_left_cell] = reach_top_valid[ii[from_left_cell], jj[from_left_cell] - 1]
            b_lo[from_left_cell] = reach_top_lo[ii[from_left_cell], jj[from_left_cell] - 1]
            b_hi[from_left_cell] = reach_top_hi[ii[from_left_cell], jj[from_left_cell] - 1]

        start_cell = (jj == 0) & (ii == 0)
        if bool(start_cell.any()):
            bv = bottom_valid[ii[start_cell], jj[start_cell]]
            b_valid[start_cell] = bv & (bottom_lo[ii[start_cell], jj[start_cell]] <= 0.0) & (
                bottom_hi[ii[start_cell], jj[start_cell]] >= 0.0
            )
            b_lo[start_cell] = torch.clamp(bottom_lo[ii[start_cell], jj[start_cell]], min=0.0)
            b_hi[start_cell] = bottom_hi[ii[start_cell], jj[start_cell]]

        from_previous_row_on_first_column = (jj == 0) & (ii > 0)
        if bool(from_previous_row_on_first_column.any()):
            prev_i = ii[from_previous_row_on_first_column] - 1
            prev_j = jj[from_previous_row_on_first_column]
            contains_zero = (
                reach_right_valid[prev_i, prev_j]
                & (reach_right_lo[prev_i, prev_j] <= 0.0)
                & (reach_right_hi[prev_i, prev_j] >= 0.0)
            )
            bv = bottom_valid[ii[from_previous_row_on_first_column], jj[from_previous_row_on_first_column]]
            b_valid[from_previous_row_on_first_column] = contains_zero & bv
            b_lo[from_previous_row_on_first_column] = torch.clamp(
                bottom_lo[ii[from_previous_row_on_first_column], jj[from_previous_row_on_first_column]],
                min=0.0,
            )
            b_hi[from_previous_row_on_first_column] = bottom_hi[
                ii[from_previous_row_on_first_column],
                jj[from_previous_row_on_first_column],
            ]

        l_valid = torch.zeros(size, dtype=torch.bool, device=device)
        l_lo = torch.zeros(size, dtype=torch.float64, device=device)
        l_hi = torch.zeros(size, dtype=torch.float64, device=device)

        from_previous_row = ii > 0
        if bool(from_previous_row.any()):
            l_valid[from_previous_row] = reach_right_valid[ii[from_previous_row] - 1, jj[from_previous_row]]
            l_lo[from_previous_row] = reach_right_lo[ii[from_previous_row] - 1, jj[from_previous_row]]
            l_hi[from_previous_row] = reach_right_hi[ii[from_previous_row] - 1, jj[from_previous_row]]

        start_cell_left = (ii == 0) & (jj == 0)
        if bool(start_cell_left.any()):
            lv = left_valid[ii[start_cell_left], jj[start_cell_left]]
            l_valid[start_cell_left] = lv & (left_lo[ii[start_cell_left], jj[start_cell_left]] <= 0.0) & (
                left_hi[ii[start_cell_left], jj[start_cell_left]] >= 0.0
            )
            l_lo[start_cell_left] = torch.clamp(left_lo[ii[start_cell_left], jj[start_cell_left]], min=0.0)
            l_hi[start_cell_left] = left_hi[ii[start_cell_left], jj[start_cell_left]]

        from_previous_column_on_first_row = (ii == 0) & (jj > 0)
        if bool(from_previous_column_on_first_row.any()):
            prev_i = ii[from_previous_column_on_first_row]
            prev_j = jj[from_previous_column_on_first_row] - 1
            contains_zero = (
                reach_top_valid[prev_i, prev_j]
                & (reach_top_lo[prev_i, prev_j] <= 0.0)
                & (reach_top_hi[prev_i, prev_j] >= 0.0)
            )
            lv = left_valid[ii[from_previous_column_on_first_row], jj[from_previous_column_on_first_row]]
            l_valid[from_previous_column_on_first_row] = contains_zero & lv
            l_lo[from_previous_column_on_first_row] = torch.clamp(
                left_lo[ii[from_previous_column_on_first_row], jj[from_previous_column_on_first_row]],
                min=0.0,
            )
            l_hi[from_previous_column_on_first_row] = left_hi[
                ii[from_previous_column_on_first_row],
                jj[from_previous_column_on_first_row],
            ]

        tfb_valid = b_valid & top_valid[ii, jj] & (torch.maximum(top_lo[ii, jj], b_lo) <= top_hi[ii, jj] + 1.0e-12)
        tfb_lo = torch.maximum(top_lo[ii, jj], b_lo)
        tfb_hi = top_hi[ii, jj]
        tfl_valid = l_valid & top_valid[ii, jj]
        tfl_lo = top_lo[ii, jj]
        tfl_hi = top_hi[ii, jj]
        tv, tl, th = _torch_union(torch, tfb_valid, tfb_lo, tfb_hi, tfl_valid, tfl_lo, tfl_hi)
        reach_top_valid[ii, jj] = tv
        reach_top_lo[ii, jj] = tl
        reach_top_hi[ii, jj] = th

        rfb_valid = b_valid & right_valid[ii, jj]
        rfb_lo = right_lo[ii, jj]
        rfb_hi = right_hi[ii, jj]
        rfl_valid = l_valid & right_valid[ii, jj] & (
            torch.maximum(right_lo[ii, jj], l_lo) <= right_hi[ii, jj] + 1.0e-12
        )
        rfl_lo = torch.maximum(right_lo[ii, jj], l_lo)
        rfl_hi = right_hi[ii, jj]
        rv, rl, rh = _torch_union(torch, rfb_valid, rfb_lo, rfb_hi, rfl_valid, rfl_lo, rfl_hi)
        reach_right_valid[ii, jj] = rv
        reach_right_lo[ii, jj] = rl
        reach_right_hi[ii, jj] = rh

    top_ok = bool(
        (
            reach_top_valid[n - 1, m - 1]
            & (reach_top_lo[n - 1, m - 1] <= 1.0)
            & (reach_top_hi[n - 1, m - 1] >= 1.0)
        ).item()
    )
    right_ok = bool(
        (
            reach_right_valid[n - 1, m - 1]
            & (reach_right_lo[n - 1, m - 1] <= 1.0)
            & (reach_right_hi[n - 1, m - 1] >= 1.0)
        ).item()
    )
    return top_ok or right_ok


def torch_cuda_continuous_frechet_distance(
    curve_p: tuple[object, ...],
    curve_q: tuple[object, ...],
    *,
    iterations: int,
    device: str = "cuda",
) -> dict[str, object]:
    import torch

    px, py = _point_arrays(curve_p)
    qx, qy = _point_arrays(curve_q)
    hi = max(math.hypot(ax - bx, ay - by) for ax, ay in zip(px, py) for bx, by in zip(qx, qy)) + 1.0
    lo = 0.0
    torch.cuda.synchronize()
    start = time.perf_counter()
    for _ in range(iterations):
        mid = (lo + hi) * 0.5
        if torch_cuda_continuous_frechet_decision(curve_p, curve_q, mid, device=device):
            hi = mid
        else:
            lo = mid
    torch.cuda.synchronize()
    return {
        "distance_estimate": hi,
        "lower_bound": lo,
        "upper_bound": hi,
        "iterations": iterations,
        "wall_sec": time.perf_counter() - start,
        "baseline": "torch_cuda_wavefront_all_cells",
    }


def _run_cpu_cpp(curve_p, curve_q, *, iterations: int) -> dict[str, Any]:
    start = time.perf_counter()
    payload = app.run_curves_app(
        curve_p,
        curve_q,
        "cpu_python_reference",
        candidate_mode="all_cells",
        continuation="cpp",
        iterations=iterations,
        verify_oracle=False,
    )
    payload["outer_wall_sec"] = time.perf_counter() - start
    return payload


def _run_rtdl_optix(curve_p, curve_q, *, iterations: int, output_capacity: int) -> dict[str, Any]:
    start = time.perf_counter()
    payload = app.run_curves_app(
        curve_p,
        curve_q,
        "optix",
        candidate_mode="rtdl_broadphase",
        continuation="cpp",
        iterations=iterations,
        require_rt_core=True,
        output_capacity=output_capacity,
        verify_oracle=False,
    )
    payload["outer_wall_sec"] = time.perf_counter() - start
    return payload


def _measure(label: str, fn, repeats: int, warmups: int) -> tuple[list[dict[str, Any]], list[float]]:
    for _ in range(warmups):
        fn()
    payloads = []
    times = []
    for _ in range(repeats):
        payload = fn()
        payloads.append(payload)
        if label == "torch_cuda":
            times.append(float(payload["wall_sec"]))
        else:
            times.append(float(payload["run_phases"]["distance_search_sec"]))
    return payloads, times


def run_suite(
    *,
    copies_list: list[int],
    iterations: int,
    repeats: int,
    warmups: int,
    include_optix: bool,
    output_capacity: int,
) -> dict[str, Any]:
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("Torch CUDA is required for the GPU baseline")

    rows: list[dict[str, Any]] = []
    for copies in copies_list:
        case = app.make_authored_curves(copies=copies)
        curve_p = case["curve_p"]
        curve_q = case["curve_q"]

        cpu_payloads, cpu_times = _measure(
            "cpu_cpp",
            lambda: _run_cpu_cpp(curve_p, curve_q, iterations=iterations),
            repeats,
            warmups,
        )
        gpu_payloads, gpu_times = _measure(
            "torch_cuda",
            lambda: torch_cuda_continuous_frechet_distance(curve_p, curve_q, iterations=iterations),
            repeats,
            warmups,
        )
        optix_payloads: list[dict[str, Any]] = []
        optix_times: list[float] = []
        optix_error = None
        if include_optix:
            try:
                optix_payloads, optix_times = _measure(
                    "rtdl_optix",
                    lambda: _run_rtdl_optix(curve_p, curve_q, iterations=iterations, output_capacity=output_capacity),
                    repeats,
                    warmups,
                )
            except Exception as exc:  # noqa: BLE001 - keep benchmark evidence machine-readable.
                optix_error = repr(exc)

        cpu_distance = float(cpu_payloads[-1]["distance_estimate"])
        gpu_distance = float(gpu_payloads[-1]["distance_estimate"])
        optix_distance = float(optix_payloads[-1]["distance_estimate"]) if optix_payloads else None
        rows.append(
            {
                "copies": copies,
                "point_count_per_curve": len(curve_p),
                "free_space_cell_count": (len(curve_p) - 1) * (len(curve_q) - 1),
                "iterations": iterations,
                "repeats": repeats,
                "cpu_cpp_all_cells_median_sec": _median(cpu_times),
                "torch_cuda_wavefront_all_cells_median_sec": _median(gpu_times),
                "rtdl_optix_broadphase_cpp_median_sec": _median(optix_times) if optix_times else None,
                "torch_cuda_over_cpu_cpp_speed": _median(cpu_times) / _median(gpu_times),
                "rtdl_optix_over_cpu_cpp_speed": (_median(cpu_times) / _median(optix_times)) if optix_times else None,
                "rtdl_optix_over_torch_cuda_speed": (_median(gpu_times) / _median(optix_times)) if optix_times else None,
                "cpu_distance_estimate": cpu_distance,
                "torch_cuda_distance_estimate": gpu_distance,
                "rtdl_optix_distance_estimate": optix_distance,
                "torch_cuda_matches_cpu_cpp": math.isclose(gpu_distance, cpu_distance, rel_tol=1.0e-5, abs_tol=1.0e-5),
                "rtdl_optix_matches_cpu_cpp": (
                    math.isclose(optix_distance, cpu_distance, rel_tol=1.0e-5, abs_tol=1.0e-5)
                    if optix_distance is not None
                    else None
                ),
                "rtdl_optix_broadphase_stats": optix_payloads[-1].get("broadphase_stats") if optix_payloads else None,
                "rtdl_optix_error": optix_error,
            }
        )
    return {
        "app": "continuous_frechet_distance",
        "benchmark": "goal2584_continuous_frechet_gpu_cpu_baselines",
        "claim_boundary": (
            "Internal same-contract benchmark evidence only. The Torch CUDA path "
            "is a locally written GPU baseline because no usable same-contract "
            "external continuous Frechet GPU implementation was available in this "
            "environment. The C++ path is the learner-owned exact all-cells CPU "
            "reference from the RTDL app."
        ),
        "environment": {
            "python": sys.version,
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "cuda_available": torch.cuda.is_available(),
            "gpu": torch.cuda.get_device_name(0),
            "rtdl_optix_library": os.environ.get("RTDL_OPTIX_LIBRARY") or os.environ.get("RTDL_OPTIX_LIB"),
        },
        "rows": rows,
    }


def _parse_copies(text: str) -> list[int]:
    values = [int(part) for part in text.split(",") if part.strip()]
    if not values or any(value <= 0 for value in values):
        raise argparse.ArgumentTypeError("copies list must contain positive integers")
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Continuous Frechet CPU/GPU same-contract baselines.")
    parser.add_argument("--copies-list", type=_parse_copies, default=[8, 16, 32])
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--skip-optix", action="store_true")
    parser.add_argument("--output-capacity", type=int, default=1_000_000)
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args(argv)
    payload = run_suite(
        copies_list=args.copies_list,
        iterations=args.iterations,
        repeats=args.repeats,
        warmups=args.warmups,
        include_optix=not args.skip_optix,
        output_capacity=args.output_capacity,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
