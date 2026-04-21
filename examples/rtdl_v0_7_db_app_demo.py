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
from rtdsl.db_reference import conjunctive_scan_cpu
from rtdsl.db_reference import grouped_count_cpu
from rtdsl.db_reference import grouped_sum_cpu
from rtdsl.db_reference import normalize_denorm_table
from rtdsl.db_reference import normalize_grouped_query
from rtdsl.db_reference import normalize_predicate_bundle


BACKENDS = ("cpu_python_reference", "cpu_reference", "embree", "optix", "vulkan")


def make_orders() -> tuple[dict[str, object], ...]:
    """Small denormalized app table; a real app would load this from its own store."""
    return (
        {"row_id": 1, "region": "east", "channel": "web", "ship_date": 10, "discount": 5, "quantity": 12, "revenue": 120},
        {"row_id": 2, "region": "west", "channel": "store", "ship_date": 11, "discount": 8, "quantity": 30, "revenue": 300},
        {"row_id": 3, "region": "east", "channel": "web", "ship_date": 12, "discount": 6, "quantity": 18, "revenue": 180},
        {"row_id": 4, "region": "west", "channel": "web", "ship_date": 13, "discount": 6, "quantity": 10, "revenue": 150},
        {"row_id": 5, "region": "west", "channel": "web", "ship_date": 13, "discount": 6, "quantity": 8, "revenue": 90},
        {"row_id": 6, "region": "south", "channel": "store", "ship_date": 14, "discount": 3, "quantity": 6, "revenue": 70},
        {"row_id": 7, "region": "east", "channel": "store", "ship_date": 15, "discount": 6, "quantity": 16, "revenue": 160},
    )


PROMO_SCAN = (
    ("ship_date", "between", 12, 15),
    ("discount", "eq", 6),
    ("quantity", "lt", 20),
)

REGION_WORKLOAD = {
    "predicates": (
        ("ship_date", "ge", 12),
        ("quantity", "lt", 20),
    ),
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


def _sort_rows(rows: tuple[dict[str, object], ...]) -> list[dict[str, object]]:
    def key(row: dict[str, object]) -> tuple[object, ...]:
        if "row_id" in row:
            return (int(row["row_id"]),)
        if "region" in row:
            return (str(row["region"]),)
        return tuple(str(row[name]) for name in sorted(row))

    return sorted((dict(row) for row in rows), key=key)


def _run_cpu_reference(table: tuple[dict[str, object], ...]) -> dict[str, Any]:
    normalized = normalize_denorm_table(table)
    return {
        "promo_order_ids": _sort_rows(conjunctive_scan_cpu(normalized, normalize_predicate_bundle(PROMO_SCAN))),
        "open_order_count_by_region": _sort_rows(grouped_count_cpu(normalized, normalize_grouped_query(REGION_WORKLOAD))),
        "web_revenue_by_region": _sort_rows(grouped_sum_cpu(normalized, normalize_grouped_query(REGION_REVENUE))),
    }


def _prepare_dataset(backend: str, table: tuple[dict[str, object], ...]):
    kwargs = {
        "primary_fields": ("ship_date", "discount", "quantity"),
        "transfer": "columnar",
    }
    if backend == "embree":
        return rt.prepare_embree_db_dataset(table, **kwargs)
    if backend == "optix":
        return rt.prepare_optix_db_dataset(table, **kwargs)
    if backend == "vulkan":
        return rt.prepare_vulkan_db_dataset(table, **kwargs)
    raise ValueError(f"unsupported prepared backend: {backend}")


def _run_prepared_backend(backend: str, table: tuple[dict[str, object], ...]) -> dict[str, Any]:
    dataset = _prepare_dataset(backend, table)
    try:
        return {
            "prepared_transfer": dataset._dataset.transfer,
            "prepared_row_count": dataset.row_count,
            "promo_order_ids": _sort_rows(dataset.conjunctive_scan(PROMO_SCAN)),
            "open_order_count_by_region": _sort_rows(dataset.grouped_count(REGION_WORKLOAD)),
            "web_revenue_by_region": _sort_rows(dataset.grouped_sum(REGION_REVENUE)),
        }
    finally:
        dataset.close()


def _canonical_backend(backend: str) -> str:
    if backend == "cpu_python_reference":
        return "cpu_reference"
    return backend


def choose_backend(requested: str, table: tuple[dict[str, object], ...]) -> tuple[str, str | None]:
    if requested != "auto":
        return _canonical_backend(requested), None
    for backend in ("embree", "optix", "vulkan"):
        try:
            dataset = _prepare_dataset(backend, table)
            dataset.close()
            return backend, None
        except Exception as exc:
            last_error = f"{backend}: {exc}"
    return "cpu_reference", f"no RT backend prepared successfully; using CPU reference ({last_error})"


def run_app(backend: str) -> dict[str, Any]:
    table = make_orders()
    selected_backend, fallback_note = choose_backend(backend, table)
    if selected_backend == "cpu_reference":
        results = _run_cpu_reference(table)
        prepared_summary = None
    else:
        results = _run_prepared_backend(selected_backend, table)
        prepared_summary = {
            "transfer": results.pop("prepared_transfer"),
            "row_count": results.pop("prepared_row_count"),
        }

    return {
        "app": "regional_order_dashboard",
        "requested_backend": backend,
        "backend": selected_backend,
        "fallback_note": fallback_note,
        "data_flow": [
            "app order rows",
            "RTDL v0.7 bounded DB workload",
            "prepared RT dataset over encoded row boxes" if selected_backend != "cpu_reference" else "CPU reference evaluator",
            "application-ready JSON rows",
        ],
        "input_table": {
            "row_count": len(table),
            "fields": sorted(table[0]),
        },
        "queries": {
            "promo_order_ids": {
                "operation": "conjunctive_scan",
                "predicates": PROMO_SCAN,
                "meaning": "Which discounted small-quantity orders shipped during the campaign window?",
            },
            "open_order_count_by_region": {
                "operation": "grouped_count",
                "query": REGION_WORKLOAD,
                "meaning": "How many small post-window orders remain by region?",
            },
            "web_revenue_by_region": {
                "operation": "grouped_sum",
                "query": REGION_REVENUE,
                "meaning": "How much web-channel revenue is covered by region?",
            },
        },
        "prepared_dataset": prepared_summary,
        "results": results,
        "honesty_boundary": "Demo of bounded v0.7 DB kernels; not a SQL engine, optimizer, transaction system, or DBMS.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RTDL v0.7 app demo for bounded DB workloads.")
    parser.add_argument(
        "--backend",
        default="cpu_python_reference",
        choices=("auto", *BACKENDS),
        help="Use the CPU reference everywhere, or run a prepared RT backend when available.",
    )
    args = parser.parse_args(argv)
    print(json.dumps(run_app(args.backend), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
