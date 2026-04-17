from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from rtdsl import prepare_optix
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
from scripts.goal434_embree_native_prepared_db_dataset_perf_gate import _attach_postgresql


def measure_optix_prepared_dataset(kernel_fn, inputs: dict[str, object], *, repeats: int) -> dict[str, object]:
    reference_rows = run_cpu_python_reference(kernel_fn, **inputs)
    prepare_start = time.perf_counter()
    prepared = prepare_optix(kernel_fn).bind(**inputs)
    prepare_seconds = time.perf_counter() - prepare_start

    query_samples = []
    try:
        for _ in range(repeats):
            start = time.perf_counter()
            rows = prepared.run()
            query_samples.append(time.perf_counter() - start)
            if rows != reference_rows:
                raise AssertionError("OptiX prepared DB dataset rows do not match Python truth")
    finally:
        prepared.dataset.close()

    return {
        "row_count": len(reference_rows),
        "row_hash": hash_rows(reference_rows),
        "optix_dataset_prepare_seconds": prepare_seconds,
        "optix_dataset_query_seconds_samples": tuple(query_samples),
        "optix_dataset_query_seconds_median": median_seconds(query_samples),
        "optix_dataset_total_repeated_seconds": prepare_seconds + sum(query_samples),
        "optix_dataset_transfer_note": (
            "Goal 435 reuses a native OptiX GAS/traversable across repeated queries; the initial Python-to-native "
            "table ingestion still uses the existing ctypes compatibility encoding path."
        ),
    }


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
        "goal": 435,
        "row_count": args.row_count,
        "repeated_query_count": args.repeats,
        "conjunctive_scan": measure_optix_prepared_dataset(
            db_perf_conjunctive_scan_reference, scan_case, repeats=args.repeats
        ),
        "grouped_count": measure_optix_prepared_dataset(
            db_perf_grouped_count_reference, grouped_count_case, repeats=args.repeats
        ),
        "grouped_sum": measure_optix_prepared_dataset(
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
