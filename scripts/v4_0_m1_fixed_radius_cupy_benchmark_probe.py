#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


def _hardware() -> dict[str, object]:
    command = [
        "nvidia-smi",
        "--query-gpu=name,driver_version,memory.total,compute_cap",
        "--format=csv,noheader",
    ]
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return {"nvidia_smi_available": False}
    line = (completed.stdout or "").strip().splitlines()
    if not line:
        return {"nvidia_smi_available": False, "stderr": completed.stderr}
    parts = [part.strip() for part in line[0].split(",")]
    return {
        "nvidia_smi_available": True,
        "gpu": parts[0] if len(parts) > 0 else "unknown",
        "driver": parts[1] if len(parts) > 1 else "unknown",
        "memory": parts[2] if len(parts) > 2 else "unknown",
        "compute_capability": parts[3] if len(parts) > 3 else "unknown",
    }


def _columns_from_xy(cp, ids: np.ndarray, xy: np.ndarray) -> dict[str, object]:
    return {
        "ids": cp.asarray(ids.astype(np.uint32, copy=False)),
        "x": cp.asarray(xy[:, 0].astype(np.float64, copy=False)),
        "y": cp.asarray(xy[:, 1].astype(np.float64, copy=False)),
    }


def _outputs(cp, count: int) -> dict[str, object]:
    return {
        "query_ids": cp.empty((count,), dtype=cp.uint32),
        "neighbor_counts": cp.empty((count,), dtype=cp.uint32),
        "threshold_flags": cp.empty((count,), dtype=cp.uint32),
    }


def _make_case(count: int, *, seed: int, radius: float) -> tuple[dict[str, object], dict[str, object]]:
    import cupy as cp

    rng = np.random.default_rng(seed)
    search_xy = rng.uniform(-1.0, 1.0, size=(count, 2))
    jitter = rng.normal(0.0, radius * 0.35, size=(count, 2))
    query_xy = search_xy + jitter
    ids = np.arange(count, dtype=np.uint32)
    return (
        _columns_from_xy(cp, ids + np.uint32(1), query_xy),
        _columns_from_xy(cp, ids + np.uint32(10), search_xy),
    )


def _cupy_bruteforce_count_threshold(
    cp,
    query: dict[str, object],
    search: dict[str, object],
    outputs: dict[str, object],
    *,
    radius: float,
    threshold: int,
    block_size: int,
) -> None:
    radius_sq = cp.asarray(float(radius) * float(radius), dtype=cp.float64)
    threshold_u32 = cp.asarray(int(threshold), dtype=cp.uint32)
    outputs["query_ids"][:] = query["ids"]
    query_count = int(query["ids"].shape[0])
    for start in range(0, query_count, int(block_size)):
        end = min(start + int(block_size), query_count)
        dx = query["x"][start:end, None] - search["x"][None, :]
        dy = query["y"][start:end, None] - search["y"][None, :]
        counts = cp.count_nonzero((dx * dx + dy * dy) <= radius_sq, axis=1).astype(cp.uint32)
        if int(threshold) > 0:
            outputs["threshold_flags"][start:end] = (counts >= threshold_u32).astype(cp.uint32)
            outputs["neighbor_counts"][start:end] = cp.minimum(counts, threshold_u32)
        else:
            outputs["threshold_flags"][start:end] = cp.zeros((end - start,), dtype=cp.uint32)
            outputs["neighbor_counts"][start:end] = counts


def _time_call(callable_obj, *, synchronize) -> float:
    started = time.perf_counter()
    callable_obj()
    synchronize()
    return time.perf_counter() - started


def _median(values: list[float]) -> float:
    ordered = sorted(float(value) for value in values)
    return ordered[len(ordered) // 2]


def _materialize(outputs: dict[str, object]) -> dict[str, list[int]]:
    return {name: [int(value) for value in column.get().tolist()] for name, column in outputs.items()}


def run_probe(
    *,
    count: int,
    radius: float,
    threshold: int,
    repeats: int,
    warmups: int,
    block_size: int,
    seed: int,
) -> dict[str, object]:
    import cupy as cp
    import rtdsl

    count = int(count)
    repeats = int(repeats)
    warmups = int(warmups)
    if count <= 0:
        raise ValueError("count must be positive")
    if repeats <= 0 or warmups < 0:
        raise ValueError("repeats must be positive and warmups must be non-negative")
    query, search = _make_case(count, seed=int(seed), radius=float(radius))
    stream = cp.cuda.Stream(non_blocking=True)

    baseline_outputs = _outputs(cp, count)
    v4_outputs = _outputs(cp, count)
    with stream:
        _cupy_bruteforce_count_threshold(
            cp,
            query,
            search,
            baseline_outputs,
            radius=radius,
            threshold=threshold,
            block_size=block_size,
        )
        rtdsl.run_v4_fixed_radius_count_threshold_2d(
            query,
            search,
            radius=radius,
            threshold=threshold,
            partner="cupy",
            output_columns=v4_outputs,
            stream=stream.ptr,
            return_metadata=True,
        )
    stream.synchronize()
    expected = _materialize(baseline_outputs)
    observed = _materialize(v4_outputs)
    if observed != expected:
        raise AssertionError(f"V4 benchmark validation mismatch: observed={observed!r} expected={expected!r}")

    for _ in range(warmups):
        outputs = _outputs(cp, count)
        with stream:
            rtdsl.run_v4_fixed_radius_count_threshold_2d(
                query,
                search,
                radius=radius,
                threshold=threshold,
                partner="cupy",
                output_columns=outputs,
                stream=stream.ptr,
                return_metadata=True,
            )
        stream.synchronize()
        outputs = _outputs(cp, count)
        with stream:
            _cupy_bruteforce_count_threshold(
                cp,
                query,
                search,
                outputs,
                radius=radius,
                threshold=threshold,
                block_size=block_size,
            )
        stream.synchronize()

    one_shot_samples = []
    for _ in range(repeats):
        outputs = _outputs(cp, count)
        one_shot_samples.append(
            _time_call(
                lambda outputs=outputs: rtdsl.run_v4_fixed_radius_count_threshold_2d(
                    query,
                    search,
                    radius=radius,
                    threshold=threshold,
                    partner="cupy",
                    output_columns=outputs,
                    stream=stream.ptr,
                    return_metadata=True,
                ),
                synchronize=stream.synchronize,
            )
        )

    prepared_samples = []
    with stream:
        operator = rtdsl.prepare_v4_fixed_radius_count_threshold_2d(
            search,
            max_radius=radius,
            partner="cupy",
            stream=stream.ptr,
        )
    stream.synchronize()
    try:
        for _ in range(repeats):
            outputs = _outputs(cp, count)
            prepared_samples.append(
                _time_call(
                    lambda outputs=outputs: operator.run(
                        query,
                        radius=radius,
                        threshold=threshold,
                        output_columns=outputs,
                        stream=stream.ptr,
                        return_metadata=True,
                    ),
                    synchronize=stream.synchronize,
                )
            )
    finally:
        operator.close()

    baseline_samples = []
    for _ in range(repeats):
        outputs = _outputs(cp, count)
        with stream:
            baseline_samples.append(
                _time_call(
                    lambda outputs=outputs: _cupy_bruteforce_count_threshold(
                        cp,
                        query,
                        search,
                        outputs,
                        radius=radius,
                        threshold=threshold,
                        block_size=block_size,
                    ),
                    synchronize=stream.synchronize,
                )
            )

    baseline_median = _median(baseline_samples)
    one_shot_median = _median(one_shot_samples)
    prepared_median = _median(prepared_samples)
    return {
        "status": "pass-with-boundary",
        "route_id": "fixed_radius_count_threshold_2d",
        "hardware": _hardware(),
        "parameters": {
            "count": count,
            "radius": float(radius),
            "threshold": int(threshold),
            "repeats": repeats,
            "warmups": warmups,
            "cupy_baseline_block_size": int(block_size),
            "seed": int(seed),
        },
        "validation": {
            "output_match": True,
            "observed_subset": {name: values[:8] for name, values in observed.items()},
        },
        "samples_seconds": {
            "v4_one_shot_prepare_plus_query": one_shot_samples,
            "v4_prepared_query_only": prepared_samples,
            "cupy_bruteforce_cuda_core_baseline": baseline_samples,
        },
        "median_seconds": {
            "v4_one_shot_prepare_plus_query": one_shot_median,
            "v4_prepared_query_only": prepared_median,
            "cupy_bruteforce_cuda_core_baseline": baseline_median,
        },
        "raw_ratios": {
            "baseline_over_v4_one_shot": baseline_median / one_shot_median if one_shot_median > 0 else None,
            "baseline_over_v4_prepared_query": baseline_median / prepared_median if prepared_median > 0 else None,
        },
        "claim_boundaries": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "v4_true_zero_copy_claim_authorized": False,
            "async_claim_authorized": False,
            "reason": (
                "This is a route-scoped benchmark probe against a simple CuPy brute-force CUDA-core "
                "baseline. It records raw timings only and does not authorize public speedup wording."
            ),
            "baseline_limitations": (
                "The CuPy baseline is an intentionally simple blocked all-pairs implementation, not a "
                "best-known tuned fixed-radius library baseline."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the V4 M1 fixed-radius CuPy benchmark probe.")
    parser.add_argument("--count", type=int, default=2048)
    parser.add_argument("--radius", type=float, default=0.05)
    parser.add_argument("--threshold", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--block-size", type=int, default=256)
    parser.add_argument("--seed", type=int, default=404)
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    args = parser.parse_args()

    result = run_probe(
        count=args.count,
        radius=args.radius,
        threshold=args.threshold,
        repeats=args.repeats,
        warmups=args.warmups,
        block_size=args.block_size,
        seed=args.seed,
    )
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
