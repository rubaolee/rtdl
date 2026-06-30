from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.reference.rtdl_fixed_radius_neighbors_reference import fixed_radius_neighbors_reference
from examples.reference.rtdl_fixed_radius_neighbors_reference import make_fixture_fixed_radius_neighbors_case
from examples.reference.rtdl_knn_rows_reference import knn_rows_reference
from examples.reference.rtdl_knn_rows_reference import make_fixture_knn_rows_case
from rtdsl.baseline_contracts import BASELINE_WORKLOADS
from rtdsl.baseline_contracts import compare_baseline_rows
from rtdsl.external_baselines import scipy_available
from rtdsl.reference import Point


def tile_points(
    points: tuple[Point, ...],
    *,
    copies: int,
    step_x: float,
    step_y: float,
) -> tuple[Point, ...]:
    tiled: list[Point] = []
    next_id = 1
    for copy_index in range(copies):
        dx = step_x * copy_index
        dy = step_y * copy_index
        for point in points:
            tiled.append(
                Point(
                    id=next_id,
                    x=point.x + dx,
                    y=point.y + dy,
                )
            )
            next_id += 1
    return tuple(tiled)


def make_scaled_case(
    base_case: dict[str, tuple[Point, ...]],
    *,
    copies: int,
) -> dict[str, tuple[Point, ...]]:
    query_points = tile_points(
        base_case["query_points"],
        copies=copies,
        step_x=1000.0,
        step_y=500.0,
    )
    search_points = tile_points(
        base_case["search_points"],
        copies=copies,
        step_x=1000.0,
        step_y=500.0,
    )
    return {
        "query_points": query_points,
        "search_points": search_points,
    }


def build_benchmark_cases() -> dict[str, dict[str, tuple[Point, ...]]]:
    fixed_fixture = make_fixture_fixed_radius_neighbors_case()
    knn_fixture = make_fixture_knn_rows_case()
    return {
        "fixture": {
            "fixed_radius_neighbors": fixed_fixture,
            "knn_rows": knn_fixture,
        },
        "fixture_tiled_x8": {
            "fixed_radius_neighbors": make_scaled_case(fixed_fixture, copies=8),
            "knn_rows": make_scaled_case(knn_fixture, copies=8),
        },
        "fixture_tiled_x32": {
            "fixed_radius_neighbors": make_scaled_case(fixed_fixture, copies=32),
            "knn_rows": make_scaled_case(knn_fixture, copies=32),
        },
    }


def workload_kernel(workload: str):
    if workload == "fixed_radius_neighbors":
        return fixed_radius_neighbors_reference
    if workload == "knn_rows":
        return knn_rows_reference
    raise ValueError(f"unsupported workload `{workload}`")


def run_backend(workload: str, backend: str, case: dict[str, tuple[Point, ...]]):
    kernel = workload_kernel(workload)
    if backend == "cpu_python_reference":
        return rt.run_cpu_python_reference(kernel, **case)
    if backend == "cpu":
        return rt.run_cpu(kernel, **case)
    if backend == "embree":
        return rt.run_embree(kernel, **case)
    if backend == "scipy":
        if workload == "fixed_radius_neighbors":
            return rt.run_scipy_fixed_radius_neighbors(
                case["query_points"],
                case["search_points"],
                radius=0.5,
                k_max=3,
            )
        return rt.run_scipy_knn_rows(
            case["query_points"],
            case["search_points"],
            k=3,
        )
    raise ValueError(f"unsupported backend `{backend}`")


def time_backend(
    workload: str,
    backend: str,
    case: dict[str, tuple[Point, ...]],
    *,
    repeats: int,
    reference_rows: tuple[dict[str, object], ...],
) -> dict[str, object]:
    run_backend(workload, backend, case)
    durations_ms: list[float] = []
    rows = ()
    for _ in range(repeats):
        start = time.perf_counter()
        rows = run_backend(workload, backend, case)
        durations_ms.append((time.perf_counter() - start) * 1000.0)
    parity = compare_baseline_rows(workload, reference_rows, rows)
    return {
        "backend": backend,
        "rows": len(rows),
        "median_ms": round(statistics.median(durations_ms), 6),
        "min_ms": round(min(durations_ms), 6),
        "max_ms": round(max(durations_ms), 6),
        "parity_ok": bool(parity),
        "parity_mode": BASELINE_WORKLOADS[workload].comparison_mode,
    }


def benchmark_workload(
    workload: str,
    case_name: str,
    case: dict[str, tuple[Point, ...]],
    *,
    repeats: int,
) -> dict[str, object]:
    reference_rows = run_backend(workload, "cpu_python_reference", case)
    backends = ["cpu_python_reference", "cpu", "embree"]
    if scipy_available():
        backends.append("scipy")
    return {
        "workload": workload,
        "case": case_name,
        "query_count": len(case["query_points"]),
        "search_count": len(case["search_points"]),
        "results": [
            time_backend(
                workload,
                backend,
                case,
                repeats=repeats,
                reference_rows=reference_rows,
            )
            for backend in backends
        ],
    }


def run_scaling_note(
    *,
    repeats: int = 5,
    case_names: tuple[str, ...] | None = None,
) -> dict[str, object]:
    all_cases = build_benchmark_cases()
    selected = case_names or tuple(all_cases.keys())
    workloads = ("fixed_radius_neighbors", "knn_rows")
    return {
        "note": "Bounded nearest-neighbor scaling note for v0.4 on the local macOS development host.",
        "repeats": repeats,
        "scipy_available": scipy_available(),
        "cases": [
            benchmark_workload(workload, case_name, all_cases[case_name][workload], repeats=repeats)
            for case_name in selected
            for workload in workloads
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a bounded nearest-neighbor scaling note for the active v0.4 line."
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=5,
        help="Number of timed repeats per backend.",
    )
    parser.add_argument(
        "--case",
        action="append",
        choices=("fixture", "fixture_tiled_x8", "fixture_tiled_x32"),
        default=None,
        help="Optional case filter. May be supplied multiple times.",
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "build" / "goal209_nearest_neighbor_scaling_note.json"),
        help="JSON output path.",
    )
    args = parser.parse_args(argv)

    payload = run_scaling_note(
        repeats=args.repeats,
        case_names=tuple(args.case) if args.case else None,
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
