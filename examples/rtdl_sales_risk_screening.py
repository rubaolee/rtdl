from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def risky_order_scan():
    predicates = rt.input("predicates", rt.PredicateSet, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
    matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
    return rt.emit(matches, fields=["row_id"])


@rt.kernel(backend="rtdl", precision="float_approx")
def risky_order_count_by_region():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(candidates, predicate=rt.grouped_count(group_keys=("region",)))
    return rt.emit(groups, fields=["region", "count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def risky_order_revenue_by_region():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(
        candidates,
        predicate=rt.grouped_sum(group_keys=("region",), value_field="revenue"),
    )
    return rt.emit(groups, fields=["region", "sum"])


def make_sales_case() -> tuple[dict[str, object], dict[str, object]]:
    table = (
        {"row_id": 1, "region": "east", "ship_date": 10, "discount": 4, "quantity": 8, "revenue": 120},
        {"row_id": 2, "region": "east", "ship_date": 12, "discount": 7, "quantity": 18, "revenue": 310},
        {"row_id": 3, "region": "west", "ship_date": 12, "discount": 6, "quantity": 12, "revenue": 280},
        {"row_id": 4, "region": "west", "ship_date": 13, "discount": 6, "quantity": 9, "revenue": 150},
        {"row_id": 5, "region": "central", "ship_date": 13, "discount": 2, "quantity": 40, "revenue": 500},
        {"row_id": 6, "region": "central", "ship_date": 11, "discount": 6, "quantity": 14, "revenue": 260},
    )
    risky_predicates = (
        ("ship_date", "between", 11, 13),
        ("discount", "ge", 6),
        ("quantity", "lt", 20),
    )
    grouped_query = {
        "predicates": risky_predicates,
        "group_keys": ("region",),
        "value_field": "revenue",
    }
    return {"table": table, "predicates": risky_predicates}, {"table": table, "query": grouped_query}


def _run_scan_rows(backend: str, case: dict[str, object]) -> tuple[dict[str, object], ...]:
    if backend == "cpu_python_reference":
        return tuple(rt.run_cpu_python_reference(risky_order_scan, **case))
    if backend == "cpu":
        return tuple(rt.run_cpu(risky_order_scan, **case))
    if backend == "embree":
        return tuple(rt.run_embree(risky_order_scan, **case))
    if backend == "optix":
        return tuple(rt.run_optix(risky_order_scan, **case))
    if backend == "vulkan":
        return tuple(rt.run_vulkan(risky_order_scan, **case))
    raise ValueError(f"unsupported backend: {backend}")


def _run_grouped_count_rows(backend: str, case: dict[str, object]) -> tuple[dict[str, object], ...]:
    adjusted = dict(case)
    adjusted["query"] = {
        "predicates": case["query"]["predicates"],
        "group_keys": case["query"]["group_keys"],
    }
    if backend == "cpu_python_reference":
        return tuple(rt.run_cpu_python_reference(risky_order_count_by_region, **adjusted))
    if backend == "cpu":
        return tuple(rt.run_cpu(risky_order_count_by_region, **adjusted))
    if backend == "embree":
        return tuple(rt.run_embree(risky_order_count_by_region, **adjusted))
    if backend == "optix":
        return tuple(rt.run_optix(risky_order_count_by_region, **adjusted))
    if backend == "vulkan":
        return tuple(rt.run_vulkan(risky_order_count_by_region, **adjusted))
    raise ValueError(f"unsupported backend: {backend}")


def _run_grouped_sum_rows(backend: str, case: dict[str, object]) -> tuple[dict[str, object], ...]:
    if backend == "cpu_python_reference":
        return tuple(rt.run_cpu_python_reference(risky_order_revenue_by_region, **case))
    if backend == "cpu":
        return tuple(rt.run_cpu(risky_order_revenue_by_region, **case))
    if backend == "embree":
        return tuple(rt.run_embree(risky_order_revenue_by_region, **case))
    if backend == "optix":
        return tuple(rt.run_optix(risky_order_revenue_by_region, **case))
    if backend == "vulkan":
        return tuple(rt.run_vulkan(risky_order_revenue_by_region, **case))
    raise ValueError(f"unsupported backend: {backend}")


def run_case(backend: str) -> dict[str, object]:
    scan_case, grouped_case = make_sales_case()
    risky_rows = _run_scan_rows(backend, scan_case)
    count_rows = _run_grouped_count_rows(backend, grouped_case)
    sum_rows = _run_grouped_sum_rows(backend, grouped_case)
    region_counts = {str(row["region"]): int(row["count"]) for row in count_rows}
    region_revenue = {
        str(row["region"]): int(row["sum"]) if float(row["sum"]).is_integer() else float(row["sum"])
        for row in sum_rows
    }
    return {
        "app": "sales_risk_screening",
        "backend": backend,
        "summary": {
            "risky_order_ids": [int(row["row_id"]) for row in risky_rows],
            "risky_order_count_by_region": region_counts,
            "risky_revenue_by_region": region_revenue,
            "highest_risk_region": max(region_counts.items(), key=lambda item: (item[1], item[0]))[0],
        },
        "rows": {
            "scan": list(risky_rows),
            "grouped_count": list(count_rows),
            "grouped_sum": list(sum_rows),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="App-style RTDL v0.7 demo: scan risky orders and summarize counts and revenue by region."
    )
    parser.add_argument(
        "--backend",
        default="cpu_python_reference",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
    )
    args = parser.parse_args(argv)
    print(json.dumps(run_case(args.backend), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
