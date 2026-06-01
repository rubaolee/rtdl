from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402


CLAIM_BOUNDARY = {
    "public_speedup_claim_authorized": False,
    "broad_rt_core_speedup_claim_authorized": False,
    "whole_app_speedup_claim_authorized": False,
    "true_zero_copy_claim_authorized": False,
    "v2_5_release_authorized": False,
    "triton_preview_auto_selection_authorized": False,
    "native_engine_customization": False,
}


def _check_output(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _median(values: list[float]) -> float:
    return float(statistics.median(values))


def _time_call(label: str, repeats: int, warmups: int, sync, fn) -> tuple[list[float], Any]:
    result = None
    for index in range(warmups):
        print(f"[goal2932] warmup {label} {index + 1}/{warmups}", flush=True)
        result = fn()
        sync()
    times: list[float] = []
    for index in range(repeats):
        print(f"[goal2932] repeat {label} {index + 1}/{repeats}", flush=True)
        sync()
        start = time.perf_counter()
        result = fn()
        sync()
        times.append(time.perf_counter() - start)
    return times, result


def run_goal2932(
    *,
    group_count: int,
    rows_per_group: int,
    repeats: int,
    warmups: int,
    output: Path,
) -> dict[str, Any]:
    import cupy
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("Torch CUDA is required for Goal2932 comparison")
    if int(cupy.cuda.runtime.getDeviceCount()) <= 0:
        raise RuntimeError("CuPy CUDA is required for Goal2932 comparison")

    group_count = int(group_count)
    rows_per_group = int(rows_per_group)
    row_count = group_count * rows_per_group
    if group_count <= 0 or rows_per_group <= 0:
        raise ValueError("group_count and rows_per_group must be positive")
    print(
        f"[goal2932] start groups={group_count} rows_per_group={rows_per_group} "
        f"row_count={row_count} repeats={repeats} warmups={warmups}",
        flush=True,
    )

    torch_base = torch.arange(row_count, dtype=torch.float64, device="cuda")
    torch_group_ids = torch.arange(group_count, dtype=torch.int64, device="cuda").repeat_interleave(rows_per_group)
    torch_offsets = torch.arange(0, row_count + 1, rows_per_group, dtype=torch.int64, device="cuda")
    torch_values_x = torch.sin(torch_base * 0.001) + 0.25 * torch.cos(torch_base * 0.0003)
    torch_values_y = torch.cos(torch_base * 0.0007) - 0.125 * torch.sin(torch_base * 0.0002)

    cupy_group_ids = cupy.arange(group_count, dtype=cupy.int64).repeat(rows_per_group)
    cupy_offsets = cupy.arange(0, row_count + 1, rows_per_group, dtype=cupy.int64)
    cupy_base = cupy.arange(row_count, dtype=cupy.float64)
    cupy_values_x = cupy.sin(cupy_base * 0.001) + 0.25 * cupy.cos(cupy_base * 0.0003)
    cupy_values_y = cupy.cos(cupy_base * 0.0007) - 0.125 * cupy.sin(cupy_base * 0.0002)

    torch_columns = {
        "group_ids": torch_group_ids,
        "row_offsets": torch_offsets,
        "values_x": torch_values_x,
        "values_y": torch_values_y,
    }
    cupy_columns = {
        "group_ids": cupy_group_ids,
        "row_offsets": cupy_offsets,
        "values_x": cupy_values_x,
        "values_y": cupy_values_y,
    }
    cupy_columns_no_offsets = {
        "group_ids": cupy_group_ids,
        "values_x": cupy_values_x,
        "values_y": cupy_values_y,
    }

    torch_times, torch_result = _time_call(
        "torch_scatter_add",
        repeats,
        warmups,
        torch.cuda.synchronize,
        lambda: rt.grouped_vector_sum_2d_partner_columns(
            torch_columns,
            group_count=group_count,
            partner="torch",
            return_metadata=True,
        ),
    )
    triton_times, triton_result = _time_call(
        "triton_offsets",
        repeats,
        warmups,
        torch.cuda.synchronize,
        lambda: rt.grouped_vector_sum_2d_partner_columns(
            torch_columns,
            group_count=group_count,
            partner="triton",
            return_metadata=True,
        ),
    )
    cupy_offsets_times, cupy_offsets_result = _time_call(
        "cupy_offsets_rawkernel",
        repeats,
        warmups,
        cupy.cuda.runtime.deviceSynchronize,
        lambda: rt.grouped_vector_sum_2d_partner_columns(
            cupy_columns,
            group_count=group_count,
            partner="cupy",
            return_metadata=True,
        ),
    )
    cupy_add_at_times, cupy_add_at_result = _time_call(
        "cupy_add_at",
        repeats,
        warmups,
        cupy.cuda.runtime.deviceSynchronize,
        lambda: rt.grouped_vector_sum_2d_partner_columns(
            cupy_columns_no_offsets,
            group_count=group_count,
            partner="cupy",
            return_metadata=True,
        ),
    )

    torch_x = torch_result["columns"]["sum_x"].detach().cpu().numpy()
    torch_y = torch_result["columns"]["sum_y"].detach().cpu().numpy()
    cupy_offsets_x = cupy.asnumpy(cupy_offsets_result["columns"]["sum_x"])
    cupy_offsets_y = cupy.asnumpy(cupy_offsets_result["columns"]["sum_y"])
    cupy_add_at_x = cupy.asnumpy(cupy_add_at_result["columns"]["sum_x"])
    cupy_add_at_y = cupy.asnumpy(cupy_add_at_result["columns"]["sum_y"])
    triton_x = triton_result["columns"]["sum_x"].detach().cpu().numpy()
    triton_y = triton_result["columns"]["sum_y"].detach().cpu().numpy()

    import numpy as np

    matches = {
        "triton_matches_torch": bool(np.allclose(triton_x, torch_x, rtol=1e-9, atol=1e-9) and np.allclose(triton_y, torch_y, rtol=1e-9, atol=1e-9)),
        "cupy_offsets_matches_torch": bool(np.allclose(cupy_offsets_x, torch_x, rtol=1e-9, atol=1e-9) and np.allclose(cupy_offsets_y, torch_y, rtol=1e-9, atol=1e-9)),
        "cupy_add_at_matches_torch": bool(np.allclose(cupy_add_at_x, torch_x, rtol=1e-9, atol=1e-9) and np.allclose(cupy_add_at_y, torch_y, rtol=1e-9, atol=1e-9)),
    }
    torch_median = _median(torch_times)
    triton_median = _median(triton_times)
    cupy_offsets_median = _median(cupy_offsets_times)
    cupy_add_at_median = _median(cupy_add_at_times)
    winner = min(
        (
            ("torch", torch_median),
            ("triton_offsets", triton_median),
            ("cupy_offsets_rawkernel", cupy_offsets_median),
            ("cupy_add_at", cupy_add_at_median),
        ),
        key=lambda item: item[1],
    )
    payload = {
        "goal": "Goal2932",
        "status": "pass" if all(matches.values()) else "mismatch",
        "app_pressure": "barnes_hut_generic_grouped_vector_sum_continuation",
        "operation": "grouped_vector_sum_f64x2",
        "group_count": group_count,
        "rows_per_group": rows_per_group,
        "row_count": row_count,
        "repeats": int(repeats),
        "warmups": int(warmups),
        "source_commit": _check_output(["git", "rev-parse", "HEAD"]),
        "source_dirty": (_check_output(["git", "status", "--short"]) or "").splitlines(),
        "gpu": _check_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "timings": {
            "torch_scatter_add": {"times_sec": torch_times, "median_sec": torch_median},
            "triton_offsets": {"times_sec": triton_times, "median_sec": triton_median},
            "cupy_offsets_rawkernel": {"times_sec": cupy_offsets_times, "median_sec": cupy_offsets_median},
            "cupy_add_at": {"times_sec": cupy_add_at_times, "median_sec": cupy_add_at_median},
        },
        "ratios": {
            "triton_over_torch": triton_median / torch_median,
            "cupy_offsets_over_torch": cupy_offsets_median / torch_median,
            "cupy_offsets_over_triton": cupy_offsets_median / triton_median,
            "cupy_offsets_over_cupy_add_at": cupy_offsets_median / cupy_add_at_median,
        },
        "winner": {"partner": winner[0], "median_sec": winner[1]},
        "matches": matches,
        "metadata": {
            "torch": torch_result["metadata"],
            "triton_offsets": triton_result["metadata"],
            "cupy_offsets_rawkernel": cupy_offsets_result["metadata"],
            "cupy_add_at": cupy_add_at_result["metadata"],
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal2932 CuPy presegmented grouped-vector-sum tuning.")
    parser.add_argument("--group-count", type=int, default=8192)
    parser.add_argument("--rows-per-group", type=int, default=16)
    parser.add_argument("--repeats", type=int, default=9)
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = run_goal2932(
        group_count=args.group_count,
        rows_per_group=args.rows_per_group,
        repeats=args.repeats,
        warmups=args.warmups,
        output=args.output,
    )
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
