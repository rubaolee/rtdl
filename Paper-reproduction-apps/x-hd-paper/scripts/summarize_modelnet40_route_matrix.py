from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


def _load_cases(path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise ValueError(f"{path} does not contain a cases array")
    by_name: dict[str, dict[str, Any]] = {}
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("case_name"), str):
            raise ValueError(f"{path} contains a malformed case entry")
        name = str(case["case_name"])
        if name in by_name:
            raise ValueError(f"duplicate case_name {name!r} in {path}")
        by_name[name] = case
    return by_name


def _stat(values: list[float]) -> dict[str, float | int]:
    if not values:
        raise ValueError("cannot summarize empty values")
    return {
        "count": len(values),
        "min": float(min(values)),
        "median": float(statistics.median(values)),
        "p90": float(statistics.quantiles(values, n=10)[8]) if len(values) >= 10 else float(max(values)),
        "p95": float(statistics.quantiles(values, n=20)[18]) if len(values) >= 20 else float(max(values)),
        "max": float(max(values)),
        "sum": float(sum(values)),
    }


def _route(case: dict[str, Any]) -> dict[str, Any]:
    route = case.get("rtdl_normalized_route")
    if not isinstance(route, dict):
        raise ValueError(f"case {case.get('case_name')} lacks rtdl_normalized_route")
    return route


def _author(case: dict[str, Any]) -> dict[str, Any]:
    author = case.get("author_normalized")
    if not isinstance(author, dict):
        raise ValueError(f"case {case.get('case_name')} lacks author_normalized")
    return author


def _num(mapping: dict[str, Any], key: str) -> float:
    value = mapping.get(key)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"expected numeric {key}, got {value!r}")
    return float(value)


def _ratio(num: float, den: float) -> float:
    if den <= 0.0:
        raise ValueError("ratio denominator must be positive")
    return num / den


def build_matrix(scalar_summary: Path, exact_summary: Path) -> dict[str, Any]:
    scalar = _load_cases(scalar_summary)
    exact = _load_cases(exact_summary)
    if set(scalar) != set(exact):
        missing_exact = sorted(set(scalar) - set(exact))
        missing_scalar = sorted(set(exact) - set(scalar))
        raise ValueError(
            "case sets differ: "
            f"missing_exact={missing_exact[:5]} missing_scalar={missing_scalar[:5]}"
        )

    rows: list[dict[str, Any]] = []
    for name in sorted(scalar):
        s = scalar[name]
        e = exact[name]
        sr = _route(s)
        er = _route(e)
        author = _author(s)
        row = {
            "case_name": name,
            "category": s.get("category"),
            "total_points": int(s.get("total_points")),
            "scalar_route_sec": _num(sr, "route_wall_sec"),
            "scalar_total_sec": _num(sr, "total_sec"),
            "exact_route_sec": _num(er, "route_wall_sec"),
            "exact_total_sec": _num(er, "total_sec"),
            "author_process_sec": _num(author, "process_wall_sec"),
            "author_avg_time_ms": _num(author, "running_avg_time_ms"),
            "author_abs_diff": _num(sr, "author_abs_diff"),
        }
        row["exact_route_vs_scalar_route"] = _ratio(row["exact_route_sec"], row["scalar_route_sec"])
        row["exact_total_vs_scalar_total"] = _ratio(row["exact_total_sec"], row["scalar_total_sec"])
        row["scalar_route_vs_author_process"] = _ratio(row["scalar_route_sec"], row["author_process_sec"])
        row["exact_route_vs_author_process"] = _ratio(row["exact_route_sec"], row["author_process_sec"])
        row["scalar_total_vs_author_process"] = _ratio(row["scalar_total_sec"], row["author_process_sec"])
        row["exact_total_vs_author_process"] = _ratio(row["exact_total_sec"], row["author_process_sec"])
        row["scalar_route_vs_author_avg_time"] = _ratio(
            row["scalar_route_sec"],
            row["author_avg_time_ms"] / 1000.0,
        )
        row["exact_route_vs_author_avg_time"] = _ratio(
            row["exact_route_sec"],
            row["author_avg_time_ms"] / 1000.0,
        )
        rows.append(row)

    metrics: dict[str, dict[str, float | int]] = {}
    numeric_keys = [
        "total_points",
        "author_abs_diff",
        "scalar_route_sec",
        "scalar_total_sec",
        "exact_route_sec",
        "exact_total_sec",
        "author_process_sec",
        "author_avg_time_ms",
        "exact_route_vs_scalar_route",
        "exact_total_vs_scalar_total",
        "scalar_route_vs_author_process",
        "exact_route_vs_author_process",
        "scalar_total_vs_author_process",
        "exact_total_vs_author_process",
        "scalar_route_vs_author_avg_time",
        "exact_route_vs_author_avg_time",
    ]
    for key in numeric_keys:
        metrics[key] = _stat([float(row[key]) for row in rows])

    category_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        category_rows[str(row["category"])].append(row)
    category_summary = []
    for category, group in sorted(category_rows.items()):
        category_summary.append(
            {
                "category": category,
                "case_count": len(group),
                "scalar_route_sum_sec": float(sum(row["scalar_route_sec"] for row in group)),
                "exact_route_sum_sec": float(sum(row["exact_route_sec"] for row in group)),
                "scalar_route_median_sec": float(statistics.median(row["scalar_route_sec"] for row in group)),
                "exact_route_median_sec": float(statistics.median(row["exact_route_sec"] for row in group)),
            }
        )

    return {
        "schema": "rtdl.paper_reproduction.xhd.modelnet40_route_label_matrix.v1",
        "scalar_summary": str(scalar_summary),
        "exact_summary": str(exact_summary),
        "case_count": len(rows),
        "case_sets_identical": True,
        "claim_boundary": {
            "scalar_route_label": "fast scalar HDResult route; per-source witnesses may be approximate",
            "exact_route_label": "slower exact per-source witness route",
            "not_claimed": [
                "full X-HD paper reproduction complete",
                "author internal Running.AvgTime parity",
                "author RT-core algorithm equivalence",
                "exact paper byte-input identity",
            ],
        },
        "metrics": metrics,
        "sum_ratios": {
            "scalar_route_sum_vs_author_process_sum": _ratio(
                metrics["scalar_route_sec"]["sum"],
                metrics["author_process_sec"]["sum"],
            ),
            "scalar_total_sum_vs_author_process_sum": _ratio(
                metrics["scalar_total_sec"]["sum"],
                metrics["author_process_sec"]["sum"],
            ),
            "exact_route_sum_vs_author_process_sum": _ratio(
                metrics["exact_route_sec"]["sum"],
                metrics["author_process_sec"]["sum"],
            ),
            "exact_total_sum_vs_author_process_sum": _ratio(
                metrics["exact_total_sec"]["sum"],
                metrics["author_process_sec"]["sum"],
            ),
            "scalar_route_sum_vs_author_avgtime_sum": _ratio(
                metrics["scalar_route_sec"]["sum"],
                metrics["author_avg_time_ms"]["sum"] / 1000.0,
            ),
            "exact_route_sum_vs_author_avgtime_sum": _ratio(
                metrics["exact_route_sec"]["sum"],
                metrics["author_avg_time_ms"]["sum"] / 1000.0,
            ),
        },
        "top_outliers": {
            "scalar_route_sec": sorted(rows, key=lambda row: row["scalar_route_sec"], reverse=True)[:10],
            "exact_route_sec": sorted(rows, key=lambda row: row["exact_route_sec"], reverse=True)[:10],
            "total_points": sorted(rows, key=lambda row: row["total_points"], reverse=True)[:10],
        },
        "category_summary": category_summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scalar-summary", required=True, type=Path)
    parser.add_argument("--exact-summary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    matrix = build_matrix(args.scalar_summary, args.exact_summary)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.output} cases={matrix['case_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
