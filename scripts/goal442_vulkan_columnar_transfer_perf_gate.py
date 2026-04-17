from __future__ import annotations

import argparse
import json
import sys
import time

sys.path.insert(0, "src")
sys.path.insert(0, ".")

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


def _measure_prepare(table, *, primary_fields, transfer: str, repeats: int) -> dict[str, object]:
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        dataset = prepare_vulkan_db_dataset(table, primary_fields=primary_fields, transfer=transfer)
        samples.append(time.perf_counter() - start)
        dataset.close()
    return {
        f"{transfer}_prepare_seconds_samples": tuple(samples),
        f"{transfer}_prepare_seconds_median": median_seconds(samples),
    }


def _measure_case(kernel_fn, case, *, primary_fields, query_kind: str, repeats: int) -> dict[str, object]:
    reference_rows = run_cpu_python_reference(kernel_fn, **case)
    row_report = _measure_prepare(case["table"], primary_fields=primary_fields, transfer="row", repeats=repeats)
    columnar_report = _measure_prepare(case["table"], primary_fields=primary_fields, transfer="columnar", repeats=repeats)

    row_dataset = prepare_vulkan_db_dataset(case["table"], primary_fields=primary_fields, transfer="row")
    columnar_dataset = prepare_vulkan_db_dataset(case["table"], primary_fields=primary_fields, transfer="columnar")
    try:
        if query_kind == "scan":
            row_rows = row_dataset.conjunctive_scan(case["predicates"])
            columnar_rows = columnar_dataset.conjunctive_scan(case["predicates"])
        elif query_kind == "grouped_count":
            row_rows = row_dataset.grouped_count(case["query"])
            columnar_rows = columnar_dataset.grouped_count(case["query"])
        else:
            row_rows = row_dataset.grouped_sum(case["query"])
            columnar_rows = columnar_dataset.grouped_sum(case["query"])
    finally:
        row_dataset.close()
        columnar_dataset.close()

    if row_rows != reference_rows or columnar_rows != reference_rows:
        raise AssertionError("Vulkan row/columnar transfer parity failed")

    row_median = row_report["row_prepare_seconds_median"]
    columnar_median = columnar_report["columnar_prepare_seconds_median"]
    return {
        "row_count": len(reference_rows),
        "row_hash": hash_rows(reference_rows),
        **row_report,
        **columnar_report,
        "columnar_prepare_speedup_vs_row": row_median / columnar_median if columnar_median else float("inf"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row-count", type=int, default=100000)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()

    result = {
        "goal": 442,
        "input_row_count": args.row_count,
        "prepare_repeats": args.repeats,
        "conjunctive_scan": _measure_case(
            db_perf_conjunctive_scan_reference,
            make_conjunctive_scan_case(args.row_count),
            primary_fields=("ship_date", "discount", "quantity"),
            query_kind="scan",
            repeats=args.repeats,
        ),
        "grouped_count": _measure_case(
            db_perf_grouped_count_reference,
            make_grouped_count_case(args.row_count),
            primary_fields=("ship_date", "quantity"),
            query_kind="grouped_count",
            repeats=args.repeats,
        ),
        "grouped_sum": _measure_case(
            db_perf_grouped_sum_reference,
            make_grouped_sum_case(args.row_count),
            primary_fields=("ship_date", "discount"),
            query_kind="grouped_sum",
            repeats=args.repeats,
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
