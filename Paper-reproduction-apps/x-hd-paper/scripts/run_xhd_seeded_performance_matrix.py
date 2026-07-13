from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Iterable


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_xhd_author_json_gate import load_author_hd_result
from run_xhd_author_json_gate import run_author
import run_xhd_cell_mbr_frontier_route_gate as seeded_route


CASE_FILES = {
    "sample256": (
        "stanford_dragon_res4_sample256.ply",
        "stanford_happy_res4_sample256.ply",
    ),
    "sample1024": (
        "stanford_dragon_res4_sample1024.ply",
        "stanford_happy_res4_sample1024.ply",
    ),
    "sample2048": (
        "stanford_dragon_res4_sample2048.ply",
        "stanford_happy_res4_sample2048.ply",
    ),
    "sample4096": (
        "stanford_dragon_res4_sample4096.ply",
        "stanford_happy_res4_sample4096.ply",
    ),
    "res4full": (
        "stanford_dragon_res4_full.ply",
        "stanford_happy_res4_full.ply",
    ),
}


def _author_avg_time_ms(payload: dict[str, object]) -> float | None:
    running = payload.get("Running")
    if not isinstance(running, dict):
        return None
    value = running.get("AvgTime")
    return None if value is None else float(value)


def _author_reported_time_ms(payload: dict[str, object]) -> float | None:
    running = payload.get("Running")
    if not isinstance(running, dict):
        return None
    repeats = running.get("Repeats")
    if not isinstance(repeats, list) or not repeats:
        return None
    first = repeats[0]
    if not isinstance(first, dict):
        return None
    value = first.get("ReportedTime")
    return None if value is None else float(value)


def _author_iteration_summary(payload: dict[str, object]) -> dict[str, object]:
    running = payload.get("Running")
    if not isinstance(running, dict):
        return {}
    repeats = running.get("Repeats")
    if not isinstance(repeats, list) or not repeats or not isinstance(repeats[0], dict):
        return {}
    iterations = repeats[0].get("Iterations")
    if not isinstance(iterations, list):
        return {}
    return {
        "iteration_count": len(iterations),
        "rt_time_ms_sum": sum(float(item.get("RTTime", 0.0)) for item in iterations if isinstance(item, dict)),
        "cuda_time_ms_sum": sum(float(item.get("CUDATime", 0.0)) for item in iterations if isinstance(item, dict)),
        "offloading_size_sum": sum(int(item.get("OffloadingSize", 0)) for item in iterations if isinstance(item, dict)),
    }


def _median(values: list[float]) -> float | None:
    return None if not values else float(statistics.median(values))


def _median_optional(values: list[float | None]) -> float | None:
    real_values = [float(value) for value in values if value is not None]
    return _median(real_values)


def _direction_phase_runs(runs: list[dict[str, object]], direction_key: str) -> dict[str, list[float]]:
    phase_runs: dict[str, list[float]] = {}
    for run in runs:
        direction = run["rtdl_route"].get(direction_key)
        if direction is None:
            continue
        timings = direction["phase_timings_sec"]
        for name, value in timings.items():
            phase_runs.setdefault(str(name), []).append(float(value))
    return phase_runs


def _phase_medians(phase_runs: dict[str, list[float]]) -> dict[str, float | None]:
    return {name: _median(values) for name, values in sorted(phase_runs.items())}


def _run_rtdl_repeats(
    *,
    input1: Path,
    input2: Path,
    author_json: Path,
    backend: str,
    grid_shape: str,
    repeat_count: int,
    tolerance: float,
    validation_mode: str,
    frontier_nearest_executor: str,
    frontier_row_order: str,
    frontier_inline_nearest: bool,
    direction_mode: str,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    runs: list[dict[str, object]] = []
    for _index in range(repeat_count):
        args = argparse.Namespace(
            input1=str(input1),
            input2=str(input2),
            n_dims=3,
            input_type="ply",
            translate_each_input_to_min_bound=True,
            backend=backend,
            grid_shape=grid_shape,
            radius=None,
            max_inline_points=64,
            initial_state="nearest-cell-mbr",
            frontier_nearest_executor=frontier_nearest_executor,
            frontier_row_order=frontier_row_order,
            frontier_inline_nearest=frontier_inline_nearest,
            direction_mode=direction_mode,
            validation_mode=validation_mode,
            author_json=str(author_json),
            summary="",
            tolerance=tolerance,
        )
        runs.append(seeded_route.build_summary(args))
    last = runs[-1]
    return runs, last


def _case_summary(
    *,
    case_name: str,
    fixtures_dir: Path,
    results_dir: Path,
    author_bin: Path,
    backend: str,
    grid_shape: str,
    rtdl_repeat_count: int,
    tolerance: float,
    validation_mode: str,
    frontier_nearest_executor: str,
    frontier_row_order: str,
    frontier_inline_nearest: bool,
    direction_mode: str,
) -> dict[str, object]:
    input_a_name, input_b_name = CASE_FILES[case_name]
    input1 = fixtures_dir / input_a_name
    input2 = fixtures_dir / input_b_name
    if not input1.exists() or not input2.exists():
        raise FileNotFoundError(f"missing fixture for {case_name}: {input1} / {input2}")

    author_json = results_dir / f"perf_{case_name}_author_hd_exec_output_pod.json"
    author_wall_start = time.perf_counter()
    author_run = run_author(
        author_bin=author_bin,
        input1=input1,
        input2=input2,
        n_dims=3,
        author_json=author_json,
        execution="gpu",
        variant="rt",
        input_type="ply",
    )
    author_wall_sec = time.perf_counter() - author_wall_start
    if author_run["returncode"] != 0:
        raise RuntimeError(f"author run failed for {case_name}: {author_run}")
    author_payload = json.loads(author_json.read_text(encoding="utf-8"))

    rtdl_runs, last_rtdl = _run_rtdl_repeats(
        input1=input1,
        input2=input2,
        author_json=author_json,
        backend=backend,
        grid_shape=grid_shape,
        repeat_count=rtdl_repeat_count,
        tolerance=tolerance,
        validation_mode=validation_mode,
        frontier_nearest_executor=frontier_nearest_executor,
        frontier_row_order=frontier_row_order,
        frontier_inline_nearest=frontier_inline_nearest,
        direction_mode=direction_mode,
    )
    rtdl_route_secs = [float(run["run_phases"]["rtdl_route_sec"]) for run in rtdl_runs]
    rtdl_load_secs = [float(run["run_phases"]["load_input_sec"]) for run in rtdl_runs]
    rtdl_exact_secs = [
        None if run["run_phases"]["exact_reference_sec"] is None else float(run["run_phases"]["exact_reference_sec"])
        for run in rtdl_runs
    ]
    rtdl_total_secs = [float(run["run_phases"]["total_sec"]) for run in rtdl_runs]

    author_hd = load_author_hd_result(author_json)
    author_comparison_distance = float(last_rtdl["author_comparison_distance"])
    author_abs_diff = abs(float(author_hd) - author_comparison_distance)
    matched = bool(last_rtdl["matched"] and author_abs_diff <= tolerance)
    directed_ab = last_rtdl["rtdl_route"]["directed_a_to_b"]
    directed_ba = last_rtdl["rtdl_route"]["directed_b_to_a"]
    directed_ab_phase_runs = _direction_phase_runs(rtdl_runs, "directed_a_to_b")
    directed_ba_phase_runs = _direction_phase_runs(rtdl_runs, "directed_b_to_a")
    directed_ba_payload = None
    if directed_ba is not None:
        directed_ba_payload = {
            "distance": float(directed_ba["distance"]),
            "frontier_row_count": int(directed_ba["frontier_row_count"]),
            "initial_candidate_distance_evaluations": int(directed_ba["initial_candidate_distance_evaluations"]),
            "continuation_candidate_distance_evaluations": int(directed_ba["candidate_distance_evaluations"]),
            "total_candidate_distance_evaluations": int(directed_ba["total_candidate_distance_evaluations"]),
            "initial_cell_mbr_tests": int(directed_ba["initial_cell_mbr_tests"]),
            "initial_cell_mbr_selection": directed_ba["initial_cell_mbr_selection"],
            "nearest_executor": directed_ba["nearest_executor"],
            "nearest_executor_requested": directed_ba["nearest_executor_requested"],
            "nearest_reduction_strategy": directed_ba["nearest_reduction_strategy"],
            "frontier_row_order": directed_ba["frontier_row_order"],
            "frontier_row_order_requested": directed_ba["frontier_row_order_requested"],
            "frontier_sort_rows": directed_ba["frontier_sort_rows"],
            "frontier_inline_nearest": directed_ba["frontier_inline_nearest"],
            "frontier_inline_nearest_requested": directed_ba["frontier_inline_nearest_requested"],
            "phase_timings_sec_last_run": directed_ba["phase_timings_sec"],
            "phase_timings_sec_runs": directed_ba_phase_runs,
            "phase_timings_sec_median": _phase_medians(directed_ba_phase_runs),
        }
    return {
        "case": case_name,
        "input1": str(input1),
        "input2": str(input2),
        "point_count_a": int(last_rtdl["point_count_a"]),
        "point_count_b": int(last_rtdl["point_count_b"]),
        "preprocessing": last_rtdl["reference_preprocessing"],
        "matched": matched,
        "author": {
            "hd_result": float(author_hd),
            "json": str(author_json),
            "process_wall_sec": author_wall_sec,
            "running_avg_time_ms": _author_avg_time_ms(author_payload),
            "first_reported_time_ms": _author_reported_time_ms(author_payload),
            "iteration_summary": _author_iteration_summary(author_payload),
            "run": author_run,
        },
        "rtdl": {
            "backend": backend,
            "route": last_rtdl["rtdl_route"]["route"],
            "initial_state": last_rtdl["initial_state"],
            "validation_mode": validation_mode,
            "frontier_nearest_executor": last_rtdl["frontier_nearest_executor"],
            "frontier_row_order": last_rtdl["frontier_row_order"],
            "frontier_inline_nearest": last_rtdl["frontier_inline_nearest"],
            "direction_mode": last_rtdl["direction_mode"],
            "frontier_native_symbol": directed_ab["frontier_native_symbol"],
            "author_comparison_distance": author_comparison_distance,
            "author_abs_diff": author_abs_diff,
            "rtdl_matches_exact_reference": last_rtdl["rtdl_matches_exact_reference"],
            "route_sec_runs": rtdl_route_secs,
            "load_input_sec_runs": rtdl_load_secs,
            "exact_reference_sec_runs": rtdl_exact_secs,
            "total_sec_runs": rtdl_total_secs,
            "route_sec_median": _median(rtdl_route_secs),
            "load_input_sec_median": _median(rtdl_load_secs),
            "exact_reference_sec_median": _median_optional(rtdl_exact_secs),
            "total_sec_median": _median(rtdl_total_secs),
            "directed_a_to_b": {
                "distance": float(directed_ab["distance"]),
                "frontier_row_count": int(directed_ab["frontier_row_count"]),
                "initial_candidate_distance_evaluations": int(directed_ab["initial_candidate_distance_evaluations"]),
                "continuation_candidate_distance_evaluations": int(directed_ab["candidate_distance_evaluations"]),
                "total_candidate_distance_evaluations": int(directed_ab["total_candidate_distance_evaluations"]),
                "initial_cell_mbr_tests": int(directed_ab["initial_cell_mbr_tests"]),
                "initial_cell_mbr_selection": directed_ab["initial_cell_mbr_selection"],
                "nearest_executor": directed_ab["nearest_executor"],
                "nearest_executor_requested": directed_ab["nearest_executor_requested"],
                "nearest_reduction_strategy": directed_ab["nearest_reduction_strategy"],
                "frontier_row_order": directed_ab["frontier_row_order"],
                "frontier_row_order_requested": directed_ab["frontier_row_order_requested"],
                "frontier_sort_rows": directed_ab["frontier_sort_rows"],
                "frontier_inline_nearest": directed_ab["frontier_inline_nearest"],
                "frontier_inline_nearest_requested": directed_ab["frontier_inline_nearest_requested"],
                "phase_timings_sec_last_run": directed_ab["phase_timings_sec"],
                "phase_timings_sec_runs": directed_ab_phase_runs,
                "phase_timings_sec_median": _phase_medians(directed_ab_phase_runs),
            },
            "directed_b_to_a": directed_ba_payload,
        },
        "ratio_policy": {
            "author_avg_vs_rtdl_route_ratio": None,
            "author_wall_vs_rtdl_total_ratio": None,
            "reason": (
                "No speedup/parity ratio is reported because author Running.AvgTime, "
                "author process wall, RTDL route time, and RTDL total time are distinct "
                "phase boundaries."
            ),
        },
    }


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    fixtures_dir = Path(args.fixtures_dir)
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    frontier_nearest_executor = getattr(args, "frontier_nearest_executor", "auto")
    frontier_row_order = getattr(args, "frontier_row_order", "sorted")
    frontier_inline_nearest = bool(getattr(args, "frontier_inline_nearest", False))
    direction_mode = getattr(args, "direction_mode", "symmetric-diagnostic")
    cases = [item.strip() for item in args.cases.split(",") if item.strip()]
    unknown = sorted(set(cases) - set(CASE_FILES))
    if unknown:
        raise ValueError(f"unknown cases: {unknown}")
    case_summaries = [
        _case_summary(
            case_name=case_name,
            fixtures_dir=fixtures_dir,
            results_dir=results_dir,
            author_bin=Path(args.author_bin),
            backend=args.backend,
            grid_shape=args.grid_shape,
            rtdl_repeat_count=args.rtdl_repeat_count,
            tolerance=args.tolerance,
            validation_mode=args.validation_mode,
            frontier_nearest_executor=frontier_nearest_executor,
            frontier_row_order=frontier_row_order,
            frontier_inline_nearest=frontier_inline_nearest,
            direction_mode=direction_mode,
        )
        for case_name in cases
    ]
    return {
        "schema": "rtdl.paper_reproduction.xhd.seeded_performance_matrix.v1",
        "paper_app": "x-hd-paper",
        "cases": case_summaries,
        "phase_policy": {
            "author_running_avg_time_ms": "author hd_exec JSON Running.AvgTime",
            "author_process_wall_sec": "subprocess wall time around hd_exec",
            "rtdl_route_sec": "in-process seeded RTDL route computation",
            "rtdl_total_sec": "route script total after input load and preprocessing",
            "validation_mode": args.validation_mode,
            "frontier_nearest_executor": frontier_nearest_executor,
            "frontier_row_order": frontier_row_order,
            "frontier_inline_nearest": frontier_inline_nearest,
            "direction_mode": direction_mode,
            "ratios_authorized": False,
        },
        "boundary": (
            "Representative same-source performance matrix for the seeded RTDL "
            "cell-MBR frontier route. It separates author and RTDL phase "
            "boundaries and does not claim paper performance parity."
        ),
        "paper_reproduction_claim_authorized": False,
        "performance_claim_authorized": False,
        "author_performance_parity_claimed": False,
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run X-HD seeded route fair performance matrix.")
    parser.add_argument("--author-bin", required=True)
    parser.add_argument(
        "--fixtures-dir",
        default=str(ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "data" / "fixtures"),
    )
    parser.add_argument(
        "--results-dir",
        default=str(ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"),
    )
    parser.add_argument("--cases", default="sample256,sample1024")
    parser.add_argument("--backend", default="optix", choices=("numpy", "optix"))
    parser.add_argument("--grid-shape", default="8,8,8")
    parser.add_argument("--rtdl-repeat-count", type=int, default=3)
    parser.add_argument(
        "--frontier-nearest-executor",
        default="auto",
        choices=("auto", "numpy", "numba", "numba_parallel"),
    )
    parser.add_argument(
        "--frontier-row-order",
        default="sorted",
        choices=("sorted", "native"),
        help=(
            "Forwarded native frontier row ordering policy: sorted keeps the "
            "legacy sorted+unique rows, native leaves rows in backend emission "
            "order for streaming consumers."
        ),
    )
    parser.add_argument(
        "--frontier-inline-nearest",
        action="store_true",
        help=(
            "Ask the native 3-D cell-MBR frontier producer to compute nearest "
            "witnesses for inline rows before the downstream continuation."
        ),
    )
    parser.add_argument(
        "--direction-mode",
        default="symmetric-diagnostic",
        choices=("symmetric-diagnostic", "directed-a-to-b"),
        help=(
            "Forwarded route direction policy. directed-a-to-b matches the "
            "author HDResult contract proven by Goal5126; symmetric-diagnostic "
            "also runs B->A and records a symmetric diagnostic."
        ),
    )
    parser.add_argument(
        "--validation-mode",
        default="exact-and-author",
        choices=("exact-and-author", "author-only", "none"),
        help=(
            "Validation mode forwarded to the RTDL route. Use author-only for "
            "production-style timing that excludes exact-reference validation."
        ),
    )
    parser.add_argument("--tolerance", type=float, default=1e-6)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)

    summary = build_summary(args)
    out = Path(args.summary)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if all(case["matched"] for case in summary["cases"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
