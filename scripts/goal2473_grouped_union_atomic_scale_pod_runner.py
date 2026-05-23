from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import subprocess
import sys
import time
from typing import Any


ROOT = next(parent for parent in pathlib.Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402
from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (  # noqa: E402
    DEFAULT_DATASET_CONFIG,
    make_rt_dbscan_points,
)


def _check_output(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _sync(cp: Any) -> None:
    cp.cuda.Stream.null.synchronize()


def _timed(cp: Any, fn) -> tuple[float, dict[str, object]]:
    _sync(cp)
    start = time.perf_counter()
    result = fn()
    _sync(cp)
    return time.perf_counter() - start, result


def _run_native_grouped_union(
    prepared,
    *,
    use_telemetry: bool,
) -> tuple[float, dict[str, object], list[int] | None]:
    cp = prepared.cupy
    prepared.parent_workspace[...] = prepared.parent_initial
    telemetry = cp.zeros((4,), dtype=cp.uint64) if use_telemetry else None
    if bool(prepared._cached_all_core_flags_true):
        elapsed, result = _timed(
            cp,
            lambda: prepared.prepared_native.apply_device_grouped_union_all_self(
                radius=prepared.radius,
                parent_out=prepared.parent_workspace,
                telemetry_out=telemetry,
            ),
        )
    else:
        prepared.border_core_candidate_workspace.fill(prepared.point_count)
        elapsed, result = _timed(
            cp,
            lambda: prepared.prepared_native.apply_device_grouped_union_self(
                radius=prepared.radius,
                predicate_flags=prepared._cached_core_flags,
                parent_out=prepared.parent_workspace,
                fallback_candidate_out=prepared.border_core_candidate_workspace,
                telemetry_out=telemetry,
            ),
        )
    telemetry_host = None
    if telemetry is not None:
        telemetry_host = [int(value) for value in telemetry.get().tolist()]
    return elapsed, result["metadata"], telemetry_host


def _median(values: list[float]) -> float:
    return float(statistics.median(values))


def run_point_count(*, point_count: int, repeat_count: int) -> dict[str, object]:
    dataset = "clustered3d"
    config = DEFAULT_DATASET_CONFIG[dataset]
    radius = float(config["radius"])
    min_neighbors = int(config["min_neighbors"])
    points = make_rt_dbscan_points(dataset, point_count=point_count, seed=20260519)

    prepare_start = time.perf_counter()
    prepared = rt.prepare_optix_cupy_radius_graph_grouped_stream_continuation_3d(
        points,
        radius=radius,
        partner="cupy",
    )
    prepare_sec = time.perf_counter() - prepare_start

    rows: list[dict[str, object]] = []
    with prepared:
        warm = prepared.run(min_neighbors=min_neighbors, return_metadata=True)
        warm_metadata = warm["metadata"]
        for repeat in range(1, repeat_count + 1):
            baseline_sec, baseline_metadata, _ = _run_native_grouped_union(
                prepared,
                use_telemetry=False,
            )
            telemetry_sec, telemetry_metadata, telemetry = _run_native_grouped_union(
                prepared,
                use_telemetry=True,
            )
            assert telemetry is not None
            rows.append(
                {
                    "repeat": repeat,
                    "baseline_elapsed_sec": baseline_sec,
                    "baseline_native_elapsed_sec": baseline_metadata.get("native_elapsed_sec"),
                    "telemetry_elapsed_sec": telemetry_sec,
                    "telemetry_native_elapsed_sec": telemetry_metadata.get("native_elapsed_sec"),
                    "native_execution_path": telemetry_metadata.get("native_execution_path"),
                    "predicate_mode": telemetry_metadata.get("predicate_mode"),
                    "all_core_flags_true": bool(prepared._cached_all_core_flags_true),
                    "telemetry": telemetry,
                    "parent_atomic_attempts": telemetry[0],
                    "parent_atomic_successes": telemetry[1],
                    "fallback_atomic_attempts": telemetry[2],
                    "fallback_atomic_successes": telemetry[3],
                }
            )

    tail = rows[1:] if len(rows) > 1 else rows
    parent_attempts = [int(row["parent_atomic_attempts"]) for row in tail]
    parent_successes = [int(row["parent_atomic_successes"]) for row in tail]
    fallback_attempts = [int(row["fallback_atomic_attempts"]) for row in tail]
    fallback_successes = [int(row["fallback_atomic_successes"]) for row in tail]
    baseline_native = [float(row["baseline_native_elapsed_sec"]) for row in tail]
    telemetry_native = [float(row["telemetry_native_elapsed_sec"]) for row in tail]
    return {
        "dataset": dataset,
        "point_count": point_count,
        "radius": radius,
        "min_neighbors": min_neighbors,
        "prepare_sec": prepare_sec,
        "warm_metadata": warm_metadata,
        "repeat_rows": rows,
        "tail_median_parent_atomic_attempts": _median(parent_attempts),
        "tail_median_parent_atomic_successes": _median(parent_successes),
        "tail_median_fallback_atomic_attempts": _median(fallback_attempts),
        "tail_median_fallback_atomic_successes": _median(fallback_successes),
        "tail_median_baseline_native_sec": _median(baseline_native),
        "tail_median_telemetry_native_sec": _median(telemetry_native),
        "tail_median_parent_attempts_per_point": _median(parent_attempts) / max(1, point_count),
        "tail_median_parent_success_rate": _median(parent_successes) / max(1.0, _median(parent_attempts)),
        "tail_median_fallback_success_rate": _median(fallback_successes) / max(1.0, _median(fallback_attempts)),
        "performance_claim_authorized": False,
    }


def run(*, output: pathlib.Path, point_counts: tuple[int, ...], repeat_count: int) -> dict[str, object]:
    summary = {
        "goal": "Goal2473",
        "purpose": "grouped_union_atomic_scale_telemetry_for_next_segmented_proposal_reduction",
        "source_commit": _check_output(["git", "rev-parse", "HEAD"]),
        "source_dirty": (_check_output(["git", "status", "--short"]) or "").splitlines(),
        "gpu": _check_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "cuda_nvcc": _check_output(["nvcc", "--version"]),
        "repeat_count": repeat_count,
        "summaries": [run_point_count(point_count=point_count, repeat_count=repeat_count) for point_count in point_counts],
        "claim_boundary": {
            "telemetry_only": True,
            "performance_claim_authorized": False,
            "dbscan_native_abi_added": False,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect grouped-union atomic telemetry at benchmark scale.")
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("docs/reports/goal2473_grouped_union_atomic_scale_pod.json"))
    parser.add_argument("--point-count", action="append", type=int, dest="point_counts")
    parser.add_argument("--repeat-count", type=int, default=3)
    args = parser.parse_args(argv)
    point_counts = tuple(args.point_counts) if args.point_counts else (32768, 65536)
    if args.repeat_count < 1:
        raise ValueError("repeat-count must be positive")
    summary = run(output=args.output, point_counts=point_counts, repeat_count=args.repeat_count)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
