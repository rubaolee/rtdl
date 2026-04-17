#!/usr/bin/env python3
"""Rebase RTDL DB perf comparisons against best-tested PostgreSQL modes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _speedup(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else float("inf")


def _backend_metric(entry: dict[str, Any], backend: str, suffix: str) -> float:
    return float(entry[f"{backend}_dataset_{suffix}"])


def build_rebase(rtdl: dict[str, Any], pg: dict[str, Any]) -> dict[str, Any]:
    if rtdl["row_count"] != pg["row_count"]:
        raise AssertionError("row_count mismatch")
    if rtdl["repeated_query_count"] != pg["repeated_query_count"]:
        raise AssertionError("repeated query count mismatch")
    if rtdl["postgresql_dsn"] != pg["postgresql_dsn"]:
        raise AssertionError("PostgreSQL DSN mismatch")

    workloads: dict[str, Any] = {}
    for workload_name, rtdl_workload in rtdl["workloads"].items():
        pg_workload = pg["workloads"][workload_name]
        if rtdl_workload["reference_row_hash"] != pg_workload["row_hash"]:
            raise AssertionError(f"row hash mismatch for {workload_name}")

        pg_modes = pg_workload["modes"]
        best_query_mode = min(pg_modes, key=lambda mode: pg_modes[mode]["query_seconds_median"])
        best_total_mode = min(pg_modes, key=lambda mode: pg_modes[mode]["total_repeated_seconds"])
        historical_mode = "single_column"

        pg_best_query = pg_modes[best_query_mode]
        pg_best_total = pg_modes[best_total_mode]
        pg_historical = pg_modes[historical_mode]

        backend_rows: dict[str, Any] = {}
        for backend, backend_entry in rtdl_workload["backends"].items():
            rtdl_query = _backend_metric(backend_entry, backend, "query_seconds_median")
            rtdl_total = _backend_metric(backend_entry, backend, "total_repeated_seconds")
            rtdl_prepare = _backend_metric(backend_entry, backend, "prepare_seconds")
            backend_rows[backend] = {
                "rtdl_prepare_seconds": rtdl_prepare,
                "rtdl_median_query_seconds": rtdl_query,
                "rtdl_total_repeated_seconds": rtdl_total,
                "postgresql_best_query_mode": best_query_mode,
                "postgresql_best_query_seconds_median": pg_best_query["query_seconds_median"],
                "query_speedup_vs_best_tested_postgresql": _speedup(
                    pg_best_query["query_seconds_median"], rtdl_query
                ),
                "postgresql_best_total_mode": best_total_mode,
                "postgresql_best_total_repeated_seconds": pg_best_total["total_repeated_seconds"],
                "total_speedup_vs_best_tested_postgresql": _speedup(
                    pg_best_total["total_repeated_seconds"], rtdl_total
                ),
                "postgresql_historical_single_column_query_seconds_median": pg_historical[
                    "query_seconds_median"
                ],
                "postgresql_historical_single_column_total_repeated_seconds": pg_historical[
                    "total_repeated_seconds"
                ],
                "query_speedup_vs_historical_single_column_postgresql": _speedup(
                    pg_historical["query_seconds_median"], rtdl_query
                ),
                "total_speedup_vs_historical_single_column_postgresql": _speedup(
                    pg_historical["total_repeated_seconds"], rtdl_total
                ),
                "row_hash": backend_entry["row_hash"],
                "postgresql_row_hash": pg_workload["row_hash"],
                "hash_match": backend_entry["row_hash"] == pg_workload["row_hash"],
            }
        workloads[workload_name] = {
            "row_count": pg_workload["row_count"],
            "row_hash": pg_workload["row_hash"],
            "postgresql_best_query_mode": best_query_mode,
            "postgresql_best_total_mode": best_total_mode,
            "postgresql_historical_mode": historical_mode,
            "backends": backend_rows,
        }

    return {
        "goal": 452,
        "row_count": rtdl["row_count"],
        "repeated_query_count": rtdl["repeated_query_count"],
        "postgresql_dsn": rtdl["postgresql_dsn"],
        "rtdl_transfer": rtdl["transfer"],
        "source_evidence": {
            "rtdl_goal450": "docs/reports/goal450_columnar_repeated_query_perf_linux_2026-04-16.json",
            "postgresql_goal451": "docs/reports/goal451_postgresql_baseline_index_audit_linux_2026-04-16.json",
        },
        "claim_boundary": (
            "Compares bounded v0.7 RTDL DB workloads against the best PostgreSQL "
            "index modes tested in Goal 451, not exhaustive PostgreSQL tuning."
        ),
        "workloads": workloads,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rtdl-json",
        default="docs/reports/goal450_columnar_repeated_query_perf_linux_2026-04-16.json",
    )
    parser.add_argument(
        "--postgresql-json",
        default="docs/reports/goal451_postgresql_baseline_index_audit_linux_2026-04-16.json",
    )
    parser.add_argument("--json-out", required=True)
    args = parser.parse_args()

    rtdl = json.loads(Path(args.rtdl_json).read_text())
    pg = json.loads(Path(args.postgresql_json).read_text())
    result = build_rebase(rtdl, pg)
    out = Path(args.json_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
