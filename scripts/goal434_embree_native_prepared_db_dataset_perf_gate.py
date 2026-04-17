from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from rtdsl import run_cpu_python_reference
from rtdsl import prepare_embree
from rtdsl.db_perf import db_perf_conjunctive_scan_reference
from rtdsl.db_perf import db_perf_grouped_count_reference
from rtdsl.db_perf import db_perf_grouped_sum_reference
from rtdsl.db_perf import hash_rows
from rtdsl.db_perf import make_conjunctive_scan_case
from rtdsl.db_perf import make_grouped_count_case
from rtdsl.db_perf import make_grouped_sum_case
from rtdsl.db_perf import median_seconds
from rtdsl import connect_postgresql
from rtdsl import prepare_postgresql_denorm_table
from rtdsl import query_postgresql_conjunctive_scan
from rtdsl import query_postgresql_grouped_count
from rtdsl import query_postgresql_grouped_sum
from rtdsl.db_reference import normalize_grouped_query


def measure_embree_prepared_dataset(kernel_fn, inputs: dict[str, object], *, repeats: int) -> dict[str, object]:
    reference_rows = run_cpu_python_reference(kernel_fn, **inputs)
    prepare_start = time.perf_counter()
    prepared = prepare_embree(kernel_fn).bind(**inputs)
    prepare_seconds = time.perf_counter() - prepare_start

    query_samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        rows = prepared.run()
        query_samples.append(time.perf_counter() - start)
        if rows != reference_rows:
            raise AssertionError("Embree prepared DB dataset rows do not match Python truth")

    return {
        "row_count": len(reference_rows),
        "row_hash": hash_rows(reference_rows),
        "embree_dataset_prepare_seconds": prepare_seconds,
        "embree_dataset_query_seconds_samples": tuple(query_samples),
        "embree_dataset_query_seconds_median": median_seconds(query_samples),
        "embree_dataset_total_repeated_seconds": prepare_seconds + sum(query_samples),
        "embree_dataset_transfer_note": (
            "Goal 434 reuses a native Embree scene across repeated queries; the initial Python-to-native "
            "table ingestion still uses the existing ctypes compatibility encoding path."
        ),
    }


def measure_postgresql_scan_once(table_rows, predicates, *, dsn: str, repeats: int) -> dict[str, object]:
    table_name = "rtdl_goal434_scan"
    with connect_postgresql(dsn) as connection:
        setup_start = time.perf_counter()
        prepare_postgresql_denorm_table(connection, table_rows, predicates, table_name=table_name)
        setup_seconds = time.perf_counter() - setup_start
        reference_rows = None
        query_samples = []
        for _ in range(repeats):
            start = time.perf_counter()
            rows = query_postgresql_conjunctive_scan(connection, predicates, table_name=table_name)
            query_samples.append(time.perf_counter() - start)
            if reference_rows is None:
                reference_rows = rows
            elif rows != reference_rows:
                raise AssertionError("PostgreSQL conjunctive_scan drifted across repeated queries")
    return {
        "postgresql_row_count": len(reference_rows),
        "postgresql_row_hash": hash_rows(reference_rows),
        "postgresql_setup_seconds": setup_seconds,
        "postgresql_query_seconds_samples": tuple(query_samples),
        "postgresql_query_seconds_median": median_seconds(query_samples),
        "postgresql_total_repeated_seconds": setup_seconds + sum(query_samples),
    }


def measure_postgresql_grouped_count_once(table_rows, query, *, dsn: str, repeats: int) -> dict[str, object]:
    table_name = "rtdl_goal434_gcount"
    normalized_query = normalize_grouped_query(query)
    with connect_postgresql(dsn) as connection:
        setup_start = time.perf_counter()
        prepare_postgresql_denorm_table(connection, table_rows, normalized_query.predicates, table_name=table_name)
        setup_seconds = time.perf_counter() - setup_start
        if hasattr(connection, "_rtdl_fake_db"):
            connection._rtdl_fake_grouped_query = normalized_query
        reference_rows = None
        query_samples = []
        for _ in range(repeats):
            start = time.perf_counter()
            rows = query_postgresql_grouped_count(connection, normalized_query, table_name=table_name)
            query_samples.append(time.perf_counter() - start)
            if reference_rows is None:
                reference_rows = rows
            elif rows != reference_rows:
                raise AssertionError("PostgreSQL grouped_count drifted across repeated queries")
    return {
        "postgresql_row_count": len(reference_rows),
        "postgresql_row_hash": hash_rows(reference_rows),
        "postgresql_setup_seconds": setup_seconds,
        "postgresql_query_seconds_samples": tuple(query_samples),
        "postgresql_query_seconds_median": median_seconds(query_samples),
        "postgresql_total_repeated_seconds": setup_seconds + sum(query_samples),
    }


def measure_postgresql_grouped_sum_once(table_rows, query, *, dsn: str, repeats: int) -> dict[str, object]:
    table_name = "rtdl_goal434_gsum"
    normalized_query = normalize_grouped_query(query)
    with connect_postgresql(dsn) as connection:
        setup_start = time.perf_counter()
        prepare_postgresql_denorm_table(connection, table_rows, normalized_query.predicates, table_name=table_name)
        setup_seconds = time.perf_counter() - setup_start
        if hasattr(connection, "_rtdl_fake_db"):
            connection._rtdl_fake_grouped_query = normalized_query
        reference_rows = None
        query_samples = []
        for _ in range(repeats):
            start = time.perf_counter()
            rows = query_postgresql_grouped_sum(connection, normalized_query, table_name=table_name)
            query_samples.append(time.perf_counter() - start)
            if reference_rows is None:
                reference_rows = rows
            elif rows != reference_rows:
                raise AssertionError("PostgreSQL grouped_sum drifted across repeated queries")
    return {
        "postgresql_row_count": len(reference_rows),
        "postgresql_row_hash": hash_rows(reference_rows),
        "postgresql_setup_seconds": setup_seconds,
        "postgresql_query_seconds_samples": tuple(query_samples),
        "postgresql_query_seconds_median": median_seconds(query_samples),
        "postgresql_total_repeated_seconds": setup_seconds + sum(query_samples),
    }


def _attach_postgresql(report: dict[str, object], pg_report: dict[str, object]) -> None:
    if report["row_count"] != pg_report["postgresql_row_count"] or report["row_hash"] != pg_report["postgresql_row_hash"]:
        raise AssertionError("PostgreSQL rows do not match Embree/Python reference rows")
    report.update(pg_report)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row-count", type=int, default=100000)
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--dsn", type=str, default=os.environ.get("RTDL_POSTGRESQL_DSN", ""))
    args = parser.parse_args()

    scan_case = make_conjunctive_scan_case(args.row_count)
    grouped_count_case = make_grouped_count_case(args.row_count)
    grouped_sum_case = make_grouped_sum_case(args.row_count)

    result = {
        "goal": 434,
        "row_count": args.row_count,
        "repeated_query_count": args.repeats,
        "conjunctive_scan": measure_embree_prepared_dataset(
            db_perf_conjunctive_scan_reference, scan_case, repeats=args.repeats
        ),
        "grouped_count": measure_embree_prepared_dataset(
            db_perf_grouped_count_reference, grouped_count_case, repeats=args.repeats
        ),
        "grouped_sum": measure_embree_prepared_dataset(
            db_perf_grouped_sum_reference, grouped_sum_case, repeats=args.repeats
        ),
    }

    if args.dsn:
        _attach_postgresql(
            result["conjunctive_scan"],
            measure_postgresql_scan_once(scan_case["table"], scan_case["predicates"], dsn=args.dsn, repeats=args.repeats),
        )
        _attach_postgresql(
            result["grouped_count"],
            measure_postgresql_grouped_count_once(
                grouped_count_case["table"], grouped_count_case["query"], dsn=args.dsn, repeats=args.repeats
            ),
        )
        _attach_postgresql(
            result["grouped_sum"],
            measure_postgresql_grouped_sum_once(
                grouped_sum_case["table"], grouped_sum_case["query"], dsn=args.dsn, repeats=args.repeats
            ),
        )

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
