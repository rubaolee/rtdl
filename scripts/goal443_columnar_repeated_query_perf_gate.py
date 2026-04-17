from __future__ import annotations

import argparse
import json
import sys
import time

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from rtdsl import prepare_embree_db_dataset
from rtdsl import prepare_optix_db_dataset
from rtdsl import prepare_vulkan_db_dataset
from rtdsl import run_cpu_python_reference
from rtdsl.db_perf import db_perf_conjunctive_scan_reference
from rtdsl.db_perf import db_perf_grouped_count_reference
from rtdsl.db_perf import db_perf_grouped_sum_reference
from rtdsl.db_perf import hash_rows
from rtdsl.db_perf import make_conjunctive_scan_case
from rtdsl.db_perf import make_grouped_count_case
from rtdsl.db_perf import make_grouped_sum_case
from rtdsl.db_perf import median_seconds
from scripts.goal434_embree_native_prepared_db_dataset_perf_gate import measure_postgresql_grouped_count_once
from scripts.goal434_embree_native_prepared_db_dataset_perf_gate import measure_postgresql_grouped_sum_once
from scripts.goal434_embree_native_prepared_db_dataset_perf_gate import measure_postgresql_scan_once


BACKENDS = {
    "embree": prepare_embree_db_dataset,
    "optix": prepare_optix_db_dataset,
    "vulkan": prepare_vulkan_db_dataset,
}


def _speedup(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else float("inf")


def _break_even_query_count(prepare: float, query: float, pg_setup: float, pg_query: float) -> str:
    if prepare <= pg_setup and query <= pg_query:
        return "wins_from_first_query"
    denominator = pg_query - query
    if denominator <= 0:
        return "no_break_even_with_median_query"
    n = (prepare - pg_setup) / denominator
    if n <= 1:
        return "wins_from_first_query"
    return f"{n:.2f}"


def _measure_backend(
    backend: str,
    prepare_fn,
    case: dict[str, object],
    reference_rows: tuple[dict[str, object], ...],
    *,
    primary_fields: tuple[str, ...],
    query_kind: str,
    repeats: int,
) -> dict[str, object]:
    prepare_start = time.perf_counter()
    dataset = prepare_fn(case["table"], primary_fields=primary_fields, transfer="columnar")
    prepare_seconds = time.perf_counter() - prepare_start

    query_samples = []
    try:
        for _ in range(repeats):
            start = time.perf_counter()
            if query_kind == "scan":
                rows = dataset.conjunctive_scan(case["predicates"])
            elif query_kind == "grouped_count":
                rows = dataset.grouped_count(case["query"])
            else:
                rows = dataset.grouped_sum(case["query"])
            query_samples.append(time.perf_counter() - start)
            if rows != reference_rows:
                raise AssertionError(f"{backend} columnar prepared rows do not match Python truth")
    finally:
        dataset.close()

    return {
        "row_count": len(reference_rows),
        "row_hash": hash_rows(reference_rows),
        f"{backend}_dataset_prepare_seconds": prepare_seconds,
        f"{backend}_dataset_query_seconds_samples": tuple(query_samples),
        f"{backend}_dataset_query_seconds_median": median_seconds(query_samples),
        f"{backend}_dataset_total_repeated_seconds": prepare_seconds + sum(query_samples),
        f"{backend}_dataset_transfer": "columnar",
    }


def _attach_postgresql(report: dict[str, object], pg_report: dict[str, object], *, backend: str) -> None:
    if report["row_count"] != pg_report["postgresql_row_count"] or report["row_hash"] != pg_report["postgresql_row_hash"]:
        raise AssertionError(f"PostgreSQL rows do not match {backend}/Python reference rows")
    report.update(pg_report)
    prepare = report[f"{backend}_dataset_prepare_seconds"]
    query = report[f"{backend}_dataset_query_seconds_median"]
    total = report[f"{backend}_dataset_total_repeated_seconds"]
    pg_setup = report["postgresql_setup_seconds"]
    pg_query = report["postgresql_query_seconds_median"]
    pg_total = report["postgresql_total_repeated_seconds"]
    report["median_query_speedup_vs_postgresql"] = _speedup(pg_query, query)
    report["total_repeated_speedup_vs_postgresql"] = _speedup(pg_total, total)
    report["break_even_query_count"] = _break_even_query_count(prepare, query, pg_setup, pg_query)


def _measure_workload(
    name: str,
    kernel_fn,
    case: dict[str, object],
    *,
    primary_fields: tuple[str, ...],
    query_kind: str,
    dsn: str,
    repeats: int,
) -> dict[str, object]:
    reference_rows = run_cpu_python_reference(kernel_fn, **case)
    if query_kind == "scan":
        pg_report = measure_postgresql_scan_once(case["table"], case["predicates"], dsn=dsn, repeats=repeats)
    elif query_kind == "grouped_count":
        pg_report = measure_postgresql_grouped_count_once(case["table"], case["query"], dsn=dsn, repeats=repeats)
    else:
        pg_report = measure_postgresql_grouped_sum_once(case["table"], case["query"], dsn=dsn, repeats=repeats)

    workload_report = {
        "reference_row_count": len(reference_rows),
        "reference_row_hash": hash_rows(reference_rows),
        "postgresql": pg_report,
        "backends": {},
    }
    if pg_report["postgresql_row_count"] != len(reference_rows) or pg_report["postgresql_row_hash"] != hash_rows(reference_rows):
        raise AssertionError(f"PostgreSQL rows do not match Python truth for {name}")

    for backend, prepare_fn in BACKENDS.items():
        backend_report = _measure_backend(
            backend,
            prepare_fn,
            case,
            reference_rows,
            primary_fields=primary_fields,
            query_kind=query_kind,
            repeats=repeats,
        )
        _attach_postgresql(backend_report, pg_report, backend=backend)
        workload_report["backends"][backend] = backend_report

    return workload_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row-count", type=int, default=100000)
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--dsn", type=str, default="dbname=postgres")
    args = parser.parse_args()

    result = {
        "goal": 443,
        "row_count": args.row_count,
        "repeated_query_count": args.repeats,
        "transfer": "columnar",
        "postgresql_dsn": args.dsn,
        "workloads": {
            "conjunctive_scan": _measure_workload(
                "conjunctive_scan",
                db_perf_conjunctive_scan_reference,
                make_conjunctive_scan_case(args.row_count),
                primary_fields=("ship_date", "discount", "quantity"),
                query_kind="scan",
                dsn=args.dsn,
                repeats=args.repeats,
            ),
            "grouped_count": _measure_workload(
                "grouped_count",
                db_perf_grouped_count_reference,
                make_grouped_count_case(args.row_count),
                primary_fields=("ship_date", "quantity"),
                query_kind="grouped_count",
                dsn=args.dsn,
                repeats=args.repeats,
            ),
            "grouped_sum": _measure_workload(
                "grouped_sum",
                db_perf_grouped_sum_reference,
                make_grouped_sum_case(args.row_count),
                primary_fields=("ship_date", "discount"),
                query_kind="grouped_sum",
                dsn=args.dsn,
                repeats=args.repeats,
            ),
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
