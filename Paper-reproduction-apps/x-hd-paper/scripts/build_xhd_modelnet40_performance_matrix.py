#!/usr/bin/env python3
"""Build a denominator-explicit ModelNet40 performance matrix.

The matrix is intentionally conservative: it reports author internal timing,
author process wall timing, RTDL route timing, and RTDL full per-case timing as
separate scopes. Ratios are diagnostic and explicitly not a parity claim unless
a later review accepts the denominator.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Iterable


def _percentile(sorted_values: list[float], q: float) -> float | None:
    if not sorted_values:
        return None
    if q <= 0:
        return sorted_values[0]
    if q >= 1:
        return sorted_values[-1]
    index = int(q * (len(sorted_values) - 1))
    return sorted_values[index]


def _stats(values: Iterable[float]) -> dict[str, float | int | None]:
    cleaned = [float(value) for value in values if math.isfinite(float(value))]
    cleaned.sort()
    if not cleaned:
        return {
            "count": 0,
            "sum": 0.0,
            "min": None,
            "median": None,
            "mean": None,
            "p90": None,
            "p95": None,
            "p99": None,
            "max": None,
        }
    return {
        "count": len(cleaned),
        "sum": float(sum(cleaned)),
        "min": cleaned[0],
        "median": float(statistics.median(cleaned)),
        "mean": float(statistics.mean(cleaned)),
        "p90": _percentile(cleaned, 0.90),
        "p95": _percentile(cleaned, 0.95),
        "p99": _percentile(cleaned, 0.99),
        "max": cleaned[-1],
    }


def _safe_ratio(numerator: float, denominator: float) -> float | None:
    if denominator == 0.0:
        return None
    return float(numerator / denominator)


def _case_metric_rows(unique_summary: dict[str, object]) -> list[dict[str, object]]:
    cases = unique_summary.get("cases", [])
    if not isinstance(cases, list):
        raise ValueError("unique summary does not contain cases")
    rows: list[dict[str, object]] = []
    for case in cases:
        if not isinstance(case, dict):
            continue
        if case.get("case_matched") is not True:
            raise ValueError(f"performance matrix requires matched cases, got {case.get('case_name')}")
        author = case.get("author_normalized", {})
        route = case.get("rtdl_normalized_route", {})
        if not isinstance(author, dict) or not isinstance(route, dict):
            raise ValueError(f"case lacks author/RTDL timing payload: {case.get('case_name')}")
        rows.append(
            {
                "case_index": int(case["case_index"]),
                "case_name": str(case["case_name"]),
                "category": str(case["category"]),
                "total_points": int(case["total_points"]),
                "author_internal_avg_time_sec": float(author["running_avg_time_ms"]) / 1000.0,
                "author_process_wall_sec": float(author["process_wall_sec"]),
                "rtdl_route_wall_sec": float(route["route_wall_sec"]),
                "rtdl_full_total_sec": float(route["total_sec"]),
                "rtdl_author_abs_diff": float(route["author_abs_diff"]),
            }
        )
    return rows


def _group_by_category(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["category"])].append(row)
    by_category: dict[str, dict[str, object]] = {}
    for category, items in sorted(grouped.items()):
        by_category[category] = {
            "case_count": len(items),
            "total_points": _stats(row["total_points"] for row in items),
            "author_internal_avg_time_sec": _stats(row["author_internal_avg_time_sec"] for row in items),
            "author_process_wall_sec": _stats(row["author_process_wall_sec"] for row in items),
            "rtdl_route_wall_sec": _stats(row["rtdl_route_wall_sec"] for row in items),
            "rtdl_full_total_sec": _stats(row["rtdl_full_total_sec"] for row in items),
            "rtdl_author_abs_diff": _stats(row["rtdl_author_abs_diff"] for row in items),
        }
    return by_category


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    unique_summary = json.loads(Path(args.unique_summary).read_text(encoding="utf-8"))
    record_coverage = (
        json.loads(Path(args.record_coverage).read_text(encoding="utf-8"))
        if args.record_coverage
        else None
    )
    rows = _case_metric_rows(unique_summary)
    author_internal_sum = sum(float(row["author_internal_avg_time_sec"]) for row in rows)
    author_process_sum = sum(float(row["author_process_wall_sec"]) for row in rows)
    rtdl_route_sum = sum(float(row["rtdl_route_wall_sec"]) for row in rows)
    rtdl_total_sum = sum(float(row["rtdl_full_total_sec"]) for row in rows)

    return {
        "schema": "rtdl.paper_reproduction.xhd.modelnet40_performance_matrix.v1",
        "goal": str(args.goal_label),
        "status": "modelnet40_denominator_explicit_performance_matrix",
        "unique_summary": str(Path(args.unique_summary)),
        "record_coverage": None if args.record_coverage is None else str(Path(args.record_coverage)),
        "case_count": len(rows),
        "record_coverage_summary": None
        if record_coverage is None
        else {
            "record_count": record_coverage.get("record_count"),
            "covered_record_count": record_coverage.get("covered_record_count"),
            "all_records_covered": record_coverage.get("all_records_covered"),
            "algorithm_distribution": record_coverage.get("algorithm_distribution"),
        },
        "timing_scopes": {
            "author_internal_avg_time_sec": {
                "description": "author JSON Running.AvgTime converted from ms; internal reported algorithm time",
                "stats": _stats(row["author_internal_avg_time_sec"] for row in rows),
            },
            "author_process_wall_sec": {
                "description": "wall time to invoke author hd_exec once for each case",
                "stats": _stats(row["author_process_wall_sec"] for row in rows),
            },
            "rtdl_route_wall_sec": {
                "description": "RTDL route phase from the app runner, excluding input loading and author invocation",
                "stats": _stats(row["rtdl_route_wall_sec"] for row in rows),
            },
            "rtdl_full_total_sec": {
                "description": "RTDL app gate per-case total including input load/normalization and route",
                "stats": _stats(row["rtdl_full_total_sec"] for row in rows),
            },
            "total_points": {
                "description": "sum of input point counts for the pair",
                "stats": _stats(row["total_points"] for row in rows),
            },
            "rtdl_author_abs_diff": {
                "description": "absolute HDResult difference between RTDL route and author rerun",
                "stats": _stats(row["rtdl_author_abs_diff"] for row in rows),
            },
        },
        "diagnostic_ratios": {
            "rtdl_route_sum_over_author_internal_sum": _safe_ratio(rtdl_route_sum, author_internal_sum),
            "rtdl_full_total_sum_over_author_process_wall_sum": _safe_ratio(rtdl_total_sum, author_process_sum),
            "rtdl_route_sum_over_author_process_wall_sum": _safe_ratio(rtdl_route_sum, author_process_sum),
            "rtdl_full_total_sum_over_author_internal_sum": _safe_ratio(rtdl_total_sum, author_internal_sum),
            "ratios_are_authorized_performance_claims": False,
            "why_not_authorized": (
                "The scopes are reported to expose the performance envelope, but author internal AvgTime, "
                "author process wall, RTDL route wall, and RTDL full app total are different denominators."
            ),
        },
        "by_category": _group_by_category(rows),
        "claim_boundary": {
            "modelnet40_all400_performance_matrix_published": True,
            "modelnet40_all2000_value_coverage_referenced": bool(
                record_coverage and record_coverage.get("all_records_covered") is True
            ),
            "author_vs_rtdl_speedup_claimed": False,
            "author_vs_rtdl_parity_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unique-summary", required=True, type=Path)
    parser.add_argument("--record-coverage", type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--goal-label", default="Goal5231")
    args = parser.parse_args(list(argv) if argv is not None else None)

    summary = build_summary(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", args.summary, "cases=", summary["case_count"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
