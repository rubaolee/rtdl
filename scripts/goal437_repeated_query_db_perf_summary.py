from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


BACKENDS = {
    "embree": "docs/reports/goal434_embree_native_prepared_db_dataset_linux_2026-04-16.json",
    "optix": "docs/reports/goal435_optix_native_prepared_db_dataset_linux_2026-04-16.json",
    "vulkan": "docs/reports/goal436_vulkan_native_prepared_db_dataset_linux_2026-04-16.json",
}

WORKLOADS = ("conjunctive_scan", "grouped_count", "grouped_sum")


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


def summarize(root: Path) -> dict[str, object]:
    summary: dict[str, object] = {
        "goal": 437,
        "source_files": {},
        "row_count": None,
        "repeated_query_count": None,
        "workloads": {},
    }
    for workload in WORKLOADS:
        summary["workloads"][workload] = {}

    for backend, relative_path in BACKENDS.items():
        path = root / relative_path
        data = json.loads(path.read_text(encoding="utf-8"))
        summary["source_files"][backend] = str(path)
        summary["row_count"] = data["row_count"]
        summary["repeated_query_count"] = data["repeated_query_count"]
        for workload in WORKLOADS:
            row = data[workload]
            prepare = row[f"{backend}_dataset_prepare_seconds"]
            query = row[f"{backend}_dataset_query_seconds_median"]
            total = row[f"{backend}_dataset_total_repeated_seconds"]
            pg_setup = row["postgresql_setup_seconds"]
            pg_query = row["postgresql_query_seconds_median"]
            pg_total = row["postgresql_total_repeated_seconds"]
            summary["workloads"][workload][backend] = {
                "row_count": row["row_count"],
                "row_hash": row["row_hash"],
                "prepare_seconds": prepare,
                "median_query_seconds": query,
                "total_repeated_seconds": total,
                "postgresql_setup_seconds": pg_setup,
                "postgresql_median_query_seconds": pg_query,
                "postgresql_total_repeated_seconds": pg_total,
                "median_query_speedup_vs_postgresql": _speedup(pg_query, query),
                "total_repeated_speedup_vs_postgresql": _speedup(pg_total, total),
                "break_even_query_count": _break_even_query_count(prepare, query, pg_setup, pg_query),
            }

    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    print(json.dumps(summarize(args.root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
