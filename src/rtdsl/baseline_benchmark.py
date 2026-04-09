from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from .baseline_contracts import BASELINE_WORKLOADS
from .baseline_runner import representative_dataset_names
from .baseline_runner import run_baseline_case

ROOT = Path(__file__).resolve().parents[2]


def benchmark_workload(
    workload: str,
    dataset: str,
    *,
    backend: str,
    iterations: int,
    warmup: int,
) -> dict[str, object]:
    kernel = _kernel_for_workload(workload)
    warmup_timings = []
    timings = []
    sample_payload = None

    for _ in range(warmup):
        start = time.perf_counter()
        sample_payload = run_baseline_case(kernel, dataset, backend=backend)
        warmup_timings.append(time.perf_counter() - start)

    for _ in range(iterations):
        start = time.perf_counter()
        sample_payload = run_baseline_case(kernel, dataset, backend=backend)
        timings.append(time.perf_counter() - start)

    return {
        "workload": workload,
        "dataset": dataset,
        "backend": backend,
        "warmup_iterations": warmup,
        "iterations": iterations,
        "warmup_timings_sec": warmup_timings,
        "timings_sec": timings,
        "mean_sec": statistics.mean(timings) if timings else 0.0,
        "median_sec": statistics.median(timings) if timings else 0.0,
        "min_sec": min(timings) if timings else 0.0,
        "max_sec": max(timings) if timings else 0.0,
        "parity": sample_payload.get("parity"),
        "note": sample_payload["note"],
    }


def run_benchmark(
    *,
    workloads: tuple[str, ...],
    backends: tuple[str, ...],
    iterations: int,
    warmup: int,
) -> dict[str, object]:
    records = []
    for workload in workloads:
        for dataset in representative_dataset_names(workload):
            for backend in backends:
                records.append(
                    benchmark_workload(
                        workload,
                        dataset,
                        backend=backend,
                        iterations=iterations,
                        warmup=warmup,
                    )
                )
    return {
        "suite": "rtdl_embree_baseline",
        "iterations": iterations,
        "warmup": warmup,
        "records": records,
    }


def write_benchmark_json(payload: dict[str, object], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return output_path


def _kernel_for_workload(workload: str):
    if workload == "lsi":
        from examples.reference.rtdl_language_reference import county_zip_join_reference as kernel
        return kernel
    if workload == "pip":
        from examples.reference.rtdl_language_reference import point_in_counties_reference as kernel
        return kernel
    if workload == "overlay":
        from examples.reference.rtdl_language_reference import county_soil_overlay_reference as kernel
        return kernel
    if workload == "ray_tri_hitcount":
        from examples.reference.rtdl_ray_tri_hitcount import ray_triangle_hitcount_reference as kernel
        return kernel
    if workload == "segment_polygon_hitcount":
        from examples.reference.rtdl_goal10_reference import segment_polygon_hitcount_reference as kernel
        return kernel
    if workload == "segment_polygon_anyhit_rows":
        from examples.reference.rtdl_goal10_reference import segment_polygon_anyhit_rows_reference as kernel
        return kernel
    if workload == "point_nearest_segment":
        from examples.reference.rtdl_goal10_reference import point_nearest_segment_reference as kernel
        return kernel
    raise ValueError(f"unknown baseline workload `{workload}`")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark the RTDL Embree baseline.")
    parser.add_argument("--workload", choices=BASELINE_WORKLOADS.keys(), action="append")
    parser.add_argument("--backend", choices=("cpu", "embree", "both"), default="both")
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--output", default=str(ROOT / "build" / "embree_baseline_benchmark.json"))
    args = parser.parse_args(argv)

    workloads = tuple(args.workload or BASELINE_WORKLOADS.keys())
    backends = ("cpu", "embree") if args.backend == "both" else (args.backend,)
    payload = run_benchmark(
        workloads=workloads,
        backends=backends,
        iterations=args.iterations,
        warmup=args.warmup,
    )
    output_path = write_benchmark_json(payload, Path(args.output))
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
