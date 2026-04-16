from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from rtdsl.db_perf import db_perf_conjunctive_scan_reference
from rtdsl.db_perf import db_perf_grouped_count_reference
from rtdsl.db_perf import db_perf_grouped_sum_reference
from rtdsl.db_perf import make_conjunctive_scan_case
from rtdsl.db_perf import make_grouped_count_case
from rtdsl.db_perf import make_grouped_sum_case
from rtdsl.db_perf import measure_backend_family
from rtdsl.db_perf import measure_postgresql_conjunctive_scan
from rtdsl.db_perf import measure_postgresql_grouped_count
from rtdsl.db_perf import measure_postgresql_grouped_sum


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row-count", type=int, default=100000)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--dsn", type=str, default=os.environ.get("RTDL_POSTGRESQL_DSN", ""))
    args = parser.parse_args()

    scan_case = make_conjunctive_scan_case(args.row_count)
    grouped_count_case = make_grouped_count_case(args.row_count)
    grouped_sum_case = make_grouped_sum_case(args.row_count)

    result = {
        "row_count": args.row_count,
        "repeats": args.repeats,
        "conjunctive_scan": measure_backend_family(
            db_perf_conjunctive_scan_reference,
            scan_case,
            repeats=args.repeats,
        ),
        "grouped_count": measure_backend_family(
            db_perf_grouped_count_reference,
            grouped_count_case,
            repeats=args.repeats,
        ),
        "grouped_sum": measure_backend_family(
            db_perf_grouped_sum_reference,
            grouped_sum_case,
            repeats=args.repeats,
        ),
    }

    if args.dsn:
        result["conjunctive_scan"].update(
            measure_postgresql_conjunctive_scan(
                scan_case["table"],
                scan_case["predicates"],
                dsn=args.dsn,
                repeats=args.repeats,
            )
        )
        result["grouped_count"].update(
            measure_postgresql_grouped_count(
                grouped_count_case["table"],
                grouped_count_case["query"],
                dsn=args.dsn,
                repeats=args.repeats,
            )
        )
        result["grouped_sum"].update(
            measure_postgresql_grouped_sum(
                grouped_sum_case["table"],
                grouped_sum_case["query"],
                dsn=args.dsn,
                repeats=args.repeats,
            )
        )

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
