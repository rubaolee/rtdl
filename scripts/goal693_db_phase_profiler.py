#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples import rtdl_sales_risk_screening as sales
from examples import rtdl_v0_7_db_app_demo as regional


def _time_call(fn: Callable[[], Any]) -> tuple[Any, float]:
    start = time.perf_counter()
    value = fn()
    return value, time.perf_counter() - start


def _stats(samples: list[float]) -> dict[str, float]:
    if not samples:
        return {"min_sec": 0.0, "median_sec": 0.0, "max_sec": 0.0}
    return {
        "min_sec": min(samples),
        "median_sec": statistics.median(samples),
        "max_sec": max(samples),
    }


def _append(samples: dict[str, list[float]], phase: str, elapsed: float) -> None:
    samples.setdefault(phase, []).append(elapsed)


def _profile_regional_once(backend: str) -> tuple[dict[str, float], dict[str, object]]:
    phases: dict[str, float] = {}
    total_start = time.perf_counter()
    table, elapsed = _time_call(regional.make_orders)
    phases["python_input_construction"] = elapsed
    selected_backend, elapsed = _time_call(lambda: regional.choose_backend(backend, table))
    phases["backend_selection"] = elapsed
    backend_name, fallback_note = selected_backend

    if backend_name == "cpu_reference":
        results, elapsed = _time_call(lambda: regional._run_cpu_reference(table))
        phases["cpu_reference_execute_and_postprocess"] = elapsed
        prepared_summary = None
    else:
        dataset, elapsed = _time_call(lambda: regional._prepare_dataset(backend_name, table))
        phases["native_prepare_dataset"] = elapsed
        try:
            promo_order_ids, elapsed = _time_call(lambda: regional._sort_rows(dataset.conjunctive_scan(regional.PROMO_SCAN)))
            phases["query_conjunctive_scan_and_materialize"] = elapsed
            open_order_count_by_region, elapsed = _time_call(
                lambda: regional._sort_rows(dataset.grouped_count(regional.REGION_WORKLOAD))
            )
            phases["query_grouped_count_and_materialize"] = elapsed
            web_revenue_by_region, elapsed = _time_call(lambda: regional._sort_rows(dataset.grouped_sum(regional.REGION_REVENUE)))
            phases["query_grouped_sum_and_materialize"] = elapsed
            results = {
                "promo_order_ids": promo_order_ids,
                "open_order_count_by_region": open_order_count_by_region,
                "web_revenue_by_region": web_revenue_by_region,
            }
            prepared_summary = {"transfer": dataset._dataset.transfer, "row_count": dataset.row_count}
        finally:
            _, close_elapsed = _time_call(dataset.close)
            phases["native_close_dataset"] = close_elapsed

    phases["total"] = time.perf_counter() - total_start
    return phases, {
        "app": "regional_order_dashboard",
        "requested_backend": backend,
        "backend": backend_name,
        "fallback_note": fallback_note,
        "prepared_dataset": prepared_summary,
        "results": results,
    }


def _profile_sales_once(backend: str) -> tuple[dict[str, float], dict[str, object]]:
    phases: dict[str, float] = {}
    total_start = time.perf_counter()
    cases, elapsed = _time_call(sales.make_sales_case)
    phases["python_input_construction"] = elapsed
    scan_case, grouped_case = cases
    risky_rows, elapsed = _time_call(lambda: sales._run_scan_rows(backend, scan_case))
    phases["query_conjunctive_scan_and_materialize"] = elapsed
    count_rows, elapsed = _time_call(lambda: sales._run_grouped_count_rows(backend, grouped_case))
    phases["query_grouped_count_and_materialize"] = elapsed
    sum_rows, elapsed = _time_call(lambda: sales._run_grouped_sum_rows(backend, grouped_case))
    phases["query_grouped_sum_and_materialize"] = elapsed

    def postprocess() -> dict[str, object]:
        region_counts = {str(row["region"]): int(row["count"]) for row in count_rows}
        region_revenue = {
            str(row["region"]): int(row["sum"]) if float(row["sum"]).is_integer() else float(row["sum"])
            for row in sum_rows
        }
        return {
            "risky_order_ids": [int(row["row_id"]) for row in risky_rows],
            "risky_order_count_by_region": region_counts,
            "risky_revenue_by_region": region_revenue,
            "highest_risk_region": max(region_counts.items(), key=lambda item: (item[1], item[0]))[0],
        }

    summary, elapsed = _time_call(postprocess)
    phases["python_postprocess"] = elapsed
    phases["total"] = time.perf_counter() - total_start
    return phases, {
        "app": "sales_risk_screening",
        "backend": backend,
        "summary": summary,
        "row_counts": {
            "scan": len(risky_rows),
            "grouped_count": len(count_rows),
            "grouped_sum": len(sum_rows),
        },
    }


def _profile(iterations: int, scenario: str, backend: str) -> dict[str, object]:
    phase_samples: dict[str, list[float]] = {}
    outputs: list[dict[str, object]] = []
    profile_fns: tuple[tuple[str, Callable[[str], tuple[dict[str, float], dict[str, object]]]], ...]
    if scenario == "regional_dashboard":
        profile_fns = (("regional_dashboard", _profile_regional_once),)
    elif scenario == "sales_risk":
        profile_fns = (("sales_risk", _profile_sales_once),)
    else:
        profile_fns = (("regional_dashboard", _profile_regional_once), ("sales_risk", _profile_sales_once))

    for _ in range(iterations):
        iteration_output: dict[str, object] = {}
        for label, fn in profile_fns:
            scenario_backend = backend
            if label == "regional_dashboard" and backend in {"cpu", "cpu_python_reference"}:
                scenario_backend = "cpu_reference"
            if label == "sales_risk" and backend == "cpu_reference":
                scenario_backend = "cpu_python_reference"
            phases, output = fn(scenario_backend)
            iteration_output[label] = output
            for phase, elapsed in phases.items():
                _append(phase_samples, f"{label}.{phase}", elapsed)
        outputs.append(iteration_output)

    return {
        "app": "database_analytics",
        "scenario": scenario,
        "backend": backend,
        "iterations": iterations,
        "optix_performance_class": rt.optix_app_performance_support("database_analytics").performance_class,
        "phase_stats": {phase: _stats(samples) for phase, samples in sorted(phase_samples.items())},
        "last_output": outputs[-1] if outputs else {},
        "boundary": "This profiler exposes DB app phases. It does not make an OptiX RT-core performance claim; RTX-class hardware and backend-specific validation are still required.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal693 DB app phase-split profiler.")
    parser.add_argument("--backend", choices=("cpu_python_reference", "cpu_reference", "cpu", "embree", "optix", "vulkan"), default="cpu_python_reference")
    parser.add_argument("--scenario", choices=("regional_dashboard", "sales_risk", "all"), default="all")
    parser.add_argument("--iterations", type=int, default=3)
    args = parser.parse_args(argv)
    if args.iterations < 1:
        raise ValueError("--iterations must be positive")
    print(json.dumps(_profile(args.iterations, args.scenario, args.backend), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
