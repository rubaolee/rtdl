from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def promo_scan_kernel():
    predicates = rt.input("predicates", rt.PredicateSet, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(predicates, table, accel="bvh", mode="db_scan")
    matches = rt.refine(candidates, predicate=rt.conjunctive_scan(exact=True))
    return rt.emit(matches, fields=["row_id"])


@rt.kernel(backend="rtdl", precision="float_approx")
def region_count_kernel():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(candidates, predicate=rt.grouped_count(group_keys=("region",)))
    return rt.emit(groups, fields=["region", "count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def region_revenue_kernel():
    query = rt.input("query", rt.GroupedQuery, role="probe")
    table = rt.input("table", rt.DenormTable, role="build")
    candidates = rt.traverse(query, table, accel="bvh", mode="db_group")
    groups = rt.refine(
        candidates,
        predicate=rt.grouped_sum(group_keys=("region",), value_field="revenue"),
    )
    return rt.emit(groups, fields=["region", "sum"])


BACKENDS = ("cpu_python_reference", "cpu", "embree", "optix", "vulkan")


def make_orders() -> tuple[dict[str, object], ...]:
    return (
        {"row_id": 1, "region": "east", "channel": "web", "ship_date": 10, "discount": 5, "quantity": 12, "revenue": 120},
        {"row_id": 2, "region": "west", "channel": "store", "ship_date": 11, "discount": 8, "quantity": 30, "revenue": 300},
        {"row_id": 3, "region": "east", "channel": "web", "ship_date": 12, "discount": 6, "quantity": 18, "revenue": 180},
        {"row_id": 4, "region": "west", "channel": "web", "ship_date": 13, "discount": 6, "quantity": 10, "revenue": 150},
        {"row_id": 5, "region": "west", "channel": "web", "ship_date": 13, "discount": 6, "quantity": 8, "revenue": 90},
        {"row_id": 6, "region": "south", "channel": "store", "ship_date": 14, "discount": 3, "quantity": 6, "revenue": 70},
        {"row_id": 7, "region": "east", "channel": "store", "ship_date": 15, "discount": 6, "quantity": 16, "revenue": 160},
    )


ONE_PREDICATE = (
    ("discount", "eq", 6),
)

TWO_PREDICATES = (
    ("ship_date", "between", 12, 15),
    ("quantity", "lt", 20),
)

THREE_PREDICATES = (
    ("ship_date", "between", 12, 15),
    ("discount", "eq", 6),
    ("quantity", "lt", 20),
)

REGION_WORKLOAD = {
    "predicates": TWO_PREDICATES,
    "group_keys": ("region",),
}

REGION_REVENUE = {
    "predicates": (
        ("ship_date", "ge", 12),
        ("channel", "eq", "web"),
    ),
    "group_keys": ("region",),
    "value_field": "revenue",
}


def _sort_rows(rows) -> list[dict[str, object]]:
    def key(row: dict[str, object]) -> tuple[object, ...]:
        if "row_id" in row:
            return (int(row["row_id"]),)
        if "region" in row:
            return (str(row["region"]),)
        return tuple(str(row[name]) for name in sorted(row))

    return sorted((dict(row) for row in rows), key=key)


def _run_kernel(backend: str, kernel_fn, **inputs):
    if backend == "cpu_python_reference":
        return rt.run_cpu_python_reference(kernel_fn, **inputs)
    if backend == "cpu":
        return rt.run_cpu(kernel_fn, **inputs)
    if backend == "embree":
        return rt.run_embree(kernel_fn, **inputs)
    if backend == "optix":
        return rt.run_optix(kernel_fn, **inputs)
    if backend == "vulkan":
        return rt.run_vulkan(kernel_fn, **inputs)
    raise ValueError(f"unsupported backend: {backend}")


def choose_backend(requested: str, table: tuple[dict[str, object], ...]) -> tuple[str, str | None]:
    if requested != "auto":
        return requested, None
    for backend in ("embree", "optix", "vulkan", "cpu"):
        try:
            _run_kernel(backend, promo_scan_kernel, predicates=THREE_PREDICATES, table=table)
            return backend, None
        except Exception as exc:
            last_error = f"{backend}: {exc}"
    return "cpu_python_reference", f"no native backend ran successfully; using CPU Python reference ({last_error})"


def run_app(backend: str) -> dict[str, Any]:
    table = make_orders()
    selected_backend, fallback_note = choose_backend(backend, table)
    results = {
        "one_predicate_discounted_ids": _sort_rows(
            _run_kernel(selected_backend, promo_scan_kernel, predicates=ONE_PREDICATE, table=table)
        ),
        "two_predicate_campaign_window_ids": _sort_rows(
            _run_kernel(selected_backend, promo_scan_kernel, predicates=TWO_PREDICATES, table=table)
        ),
        "three_predicate_promo_order_ids": _sort_rows(
            _run_kernel(selected_backend, promo_scan_kernel, predicates=THREE_PREDICATES, table=table)
        ),
        "open_order_count_by_region": _sort_rows(
            _run_kernel(selected_backend, region_count_kernel, query=REGION_WORKLOAD, table=table)
        ),
        "web_revenue_by_region": _sort_rows(
            _run_kernel(selected_backend, region_revenue_kernel, query=REGION_REVENUE, table=table)
        ),
    }
    return {
        "app": "regional_order_dashboard_kernel_form",
        "requested_backend": backend,
        "backend": selected_backend,
        "fallback_note": fallback_note,
        "kernel_flow": [
            "rt.input(..., role='probe') receives predicates or grouped query",
            "rt.input(..., role='build') receives application rows",
            "rt.traverse(..., accel='bvh') discovers encoded row candidates",
            "rt.refine(...) applies exact scan or grouped aggregate semantics",
            "rt.emit(...) returns application JSON rows",
        ],
        "predicate_examples": {
            "one_predicate": ONE_PREDICATE,
            "two_predicates": TWO_PREDICATES,
            "three_predicates": THREE_PREDICATES,
        },
        "input_table": {
            "row_count": len(table),
            "fields": sorted(table[0]),
        },
        "kernels": {
            "promo_scan_kernel": "conjunctive_scan",
            "region_count_kernel": "grouped_count",
            "region_revenue_kernel": "grouped_sum",
        },
        "results": results,
        "honesty_boundary": "RTDL kernel demo for bounded DB workloads; not SQL, joins, transactions, or a DBMS.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RTDL v0.7 DB kernel-form app demo.")
    parser.add_argument(
        "--backend",
        default="cpu_python_reference",
        choices=("auto", *BACKENDS),
        help="Run the RTDL kernels on a selected backend, or auto-select an available native backend.",
    )
    args = parser.parse_args(argv)
    print(json.dumps(run_app(args.backend), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
