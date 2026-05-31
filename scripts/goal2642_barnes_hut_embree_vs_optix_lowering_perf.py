#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gc
import json
import statistics
import time
from pathlib import Path
from typing import Any, Callable

from examples.v2_0.research_benchmarks.barnes_hut import (
    rtdl_barnes_hut_benchmark_app as bench,
)


def _median(values: list[float]) -> float:
    return statistics.median(values)


def _run_once(
    *,
    backend: str,
    body_count: int,
    bucket_size: int,
    theta: float,
    validate: bool,
) -> dict[str, Any]:
    mode = f"aggregate_frontier_expanded_membership_{backend}"
    start = time.perf_counter()
    payload = bench.run_benchmark(
        mode,
        body_count=body_count,
        theta=theta,
        bucket_size=bucket_size,
        skip_validation=not validate,
        require_rt_core=(backend == "optix"),
    )
    external_sec = time.perf_counter() - start
    return {
        "payload": payload,
        "external_sec": external_sec,
    }


def _summarize_samples(samples: list[dict[str, Any]]) -> dict[str, Any]:
    payload = samples[-1]["payload"]
    phases = payload["run_phases"]
    membership = payload["membership_primitive"]
    summary = payload["frontier_collection"]["summary"]
    return {
        "backend": payload["backend"],
        "rt_core_accelerated": bool(membership["rt_core_accelerated"]),
        "native_generic_symbol": membership["native_generic_symbol"],
        "rows_match_reference": payload["baseline_validation"]["matches_collect_aggregate_frontier_2d"],
        "validation_skipped": payload["baseline_validation"]["skipped"],
        "body_count": int(payload["body_count"]),
        "tree_node_count": int(payload["tree_summary"]["tree_node_count"]),
        "frontier_row_count": int(summary["frontier_row_count"]),
        "near_zone_candidate_row_count": int(summary["near_zone_candidate_row_count"]),
        "safe_far_accept_count": int(summary["safe_far_accept_count"]),
        "exact_opening_test_count": int(summary["exact_opening_test_count"]),
        "force_row_count": int(payload["force_summary"]["force_row_count"]),
        "total_sec_median": _median([float(sample["payload"]["run_phases"]["total_sec"]) for sample in samples]),
        "external_sec_median": _median([float(sample["external_sec"]) for sample in samples]),
        "frontier_lowering_sec_median": _median(
            [float(sample["payload"]["run_phases"]["frontier_lowering_sec"]) for sample in samples]
        ),
        "membership_wrapper_sec_median": _median(
            [float(sample["payload"]["run_phases"]["membership_primitive_wrapper_sec"]) for sample in samples]
        ),
        "force_interpretation_sec_median": _median(
            [float(sample["payload"]["run_phases"]["force_interpretation_sec"]) for sample in samples]
        ),
        "tree_build_sec_median": _median(
            [float(sample["payload"]["run_phases"]["tree_build_sec"]) for sample in samples]
        ),
    }


def run_case(
    *,
    body_count: int,
    bucket_size: int,
    theta: float,
    repeats: int,
    validate: bool,
    progress_callback: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    case: dict[str, Any] = {
        "body_count": body_count,
        "bucket_size": bucket_size,
        "theta": theta,
        "repeats": repeats,
        "validate": validate,
        "backends": {},
    }
    for backend in ("embree", "optix"):
        samples: list[dict[str, Any]] = []
        for repeat_index in range(repeats):
            if progress_callback is not None:
                progress_callback(
                    f"backend={backend} repeat={repeat_index + 1}/{repeats} start"
                )
            gc.collect()
            repeat_start = time.perf_counter()
            samples.append(
                _run_once(
                    backend=backend,
                    body_count=body_count,
                    bucket_size=bucket_size,
                    theta=theta,
                    validate=validate,
                )
            )
            if progress_callback is not None:
                progress_callback(
                    f"backend={backend} repeat={repeat_index + 1}/{repeats} "
                    f"done sec={time.perf_counter() - repeat_start:.3f}"
                )
        case["backends"][backend] = _summarize_samples(samples)
    embree = case["backends"]["embree"]
    optix = case["backends"]["optix"]
    case["speedups_optix_vs_embree"] = {
        "total": embree["total_sec_median"] / optix["total_sec_median"],
        "frontier_lowering": embree["frontier_lowering_sec_median"] / optix["frontier_lowering_sec_median"],
        "membership_wrapper": embree["membership_wrapper_sec_median"] / optix["membership_wrapper_sec_median"],
        "force_interpretation": embree["force_interpretation_sec_median"] / optix["force_interpretation_sec_median"]
        if optix["force_interpretation_sec_median"]
        else None,
    }
    case["rows_match_between_backends"] = (
        embree["frontier_row_count"] == optix["frontier_row_count"]
        and embree["near_zone_candidate_row_count"] == optix["near_zone_candidate_row_count"]
        and embree["safe_far_accept_count"] == optix["safe_far_accept_count"]
        and embree["exact_opening_test_count"] == optix["exact_opening_test_count"]
        and embree["force_row_count"] == optix["force_row_count"]
    )
    print(json.dumps(case, indent=2, sort_keys=True))
    return case


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--case",
        action="append",
        default=[],
        help="body_count:bucket_size; may be passed multiple times",
    )
    parser.add_argument("--theta", type=float, default=bench.app.THETA)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument(
        "--validate-first",
        action="store_true",
        help="Run reference validation only on the first case.",
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    raw_cases = args.case or ["128:8", "512:16", "2048:32"]
    results = []
    for index, raw in enumerate(raw_cases):
        body_count, bucket_size = (int(part) for part in raw.split(":", 1))
        results.append(
            run_case(
                body_count=body_count,
                bucket_size=bucket_size,
                theta=args.theta,
                repeats=args.repeats,
                validate=bool(args.validate_first and index == 0),
            )
        )
    payload = {
        "benchmark": "goal2642_barnes_hut_embree_vs_optix_expanded_membership_lowering",
        "cases": results,
    }
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
