#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_sales_risk_screening as sales_app
from examples import rtdl_v0_7_db_app_demo as regional_app
from scripts import goal756_db_prepared_session_perf as goal756
from scripts.goal839_baseline_artifact_schema import (
    build_baseline_artifact,
    load_goal835_row,
    write_baseline_artifact,
)

import rtdsl as rt


GOAL = "Goal842 PostgreSQL prepared DB baseline collector"
DATE = "2026-04-23"
SCENARIOS = ("sales_risk", "regional_dashboard")


def _sort_rows(rows: tuple[dict[str, Any], ...]) -> list[dict[str, Any]]:
    def key(row: dict[str, Any]) -> tuple[Any, ...]:
        if "row_id" in row:
            return (int(row["row_id"]),)
        if "region" in row:
            return (str(row["region"]),)
        return tuple((name, row[name]) for name in sorted(row))

    return sorted((dict(row) for row in rows), key=key)


def _summary_fingerprint(section: dict[str, Any]) -> dict[str, Any]:
    summary = dict(section.get("summary") or {})
    summary.pop("risky_order_id_sample", None)
    return {
        "summary": summary,
        "row_counts": section.get("row_counts"),
        "output_mode": section.get("output_mode"),
    }


def _connect(dsn: str):
    connection = rt.connect_postgresql(dsn)
    close = getattr(connection, "close", None)
    return connection, close


def _run_sales_risk(connection, *, copies: int) -> tuple[dict[str, Any], dict[str, float]]:
    table_start = time.perf_counter()
    scan_case, grouped_case = sales_app.make_sales_case(copies)
    table = scan_case["table"]
    predicates = scan_case["predicates"]
    grouped_query = grouped_case["query"]
    count_query = {
        "predicates": grouped_query["predicates"],
        "group_keys": grouped_query["group_keys"],
    }
    input_construction_sec = time.perf_counter() - table_start

    prepare_start = time.perf_counter()
    rt.prepare_postgresql_denorm_table(connection, table, predicates)
    backend_prepare_sec = time.perf_counter() - prepare_start

    query_scan_start = time.perf_counter()
    risky_rows = tuple(rt.query_postgresql_conjunctive_scan(connection, predicates))
    query_scan_sec = time.perf_counter() - query_scan_start

    query_count_start = time.perf_counter()
    if hasattr(connection, "_rtdl_fake_db"):
        connection._rtdl_fake_grouped_query = rt.normalize_grouped_query(count_query)
    count_rows = tuple(rt.query_postgresql_grouped_count(connection, count_query))
    query_count_sec = time.perf_counter() - query_count_start

    query_sum_start = time.perf_counter()
    if hasattr(connection, "_rtdl_fake_db"):
        connection._rtdl_fake_grouped_query = rt.normalize_grouped_query(grouped_query)
    sum_rows = tuple(rt.query_postgresql_grouped_sum(connection, grouped_query))
    query_sum_sec = time.perf_counter() - query_sum_start

    postprocess_start = time.perf_counter()
    region_counts = {str(row["region"]): int(row["count"]) for row in count_rows}
    region_revenue = {
        str(row["region"]): int(row["sum"]) if float(row["sum"]).is_integer() else float(row["sum"])
        for row in sum_rows
    }
    risky_order_ids = [int(row["row_id"]) for row in risky_rows]
    highest_risk_region = max(region_counts.items(), key=lambda item: (item[1], item[0]))[0]
    python_summary_postprocess_sec = time.perf_counter() - postprocess_start

    total_query_sec = query_scan_sec + query_count_sec + query_sum_sec
    section = {
        "app": "sales_risk_screening",
        "backend": "postgresql",
        "copies": copies,
        "output_mode": "compact_summary",
        "execution_mode": "prepared_session_semantics",
        "session": {
            "input_construction_sec": input_construction_sec,
            "prepare_sec": backend_prepare_sec,
        },
        "run_phases": {
            "query_conjunctive_scan_and_materialize_sec": query_scan_sec,
            "query_grouped_count_and_materialize_sec": query_count_sec,
            "query_grouped_sum_and_materialize_sec": query_sum_sec,
            "python_summary_postprocess_sec": python_summary_postprocess_sec,
        },
        "summary": {
            "risky_order_count": len(risky_rows),
            "risky_order_count_by_region": region_counts,
            "risky_revenue_by_region": region_revenue,
            "highest_risk_region": highest_risk_region,
        },
        "row_counts": {
            "scan": len(risky_rows),
            "grouped_count": len(count_rows),
            "grouped_sum": len(sum_rows),
        },
        "rows": {},
    }
    return section, {
        "input_pack_or_table_build": input_construction_sec,
        "backend_prepare": backend_prepare_sec,
        "native_query": total_query_sec,
        "copyback_or_materialization": total_query_sec,
        "python_summary_postprocess": python_summary_postprocess_sec,
    }


def _run_regional_dashboard(connection, *, copies: int) -> tuple[dict[str, Any], dict[str, float]]:
    table_start = time.perf_counter()
    table = regional_app.make_orders(copies)
    input_construction_sec = time.perf_counter() - table_start

    prepare_start = time.perf_counter()
    rt.prepare_postgresql_denorm_table(connection, table, regional_app.PROMO_SCAN)
    backend_prepare_sec = time.perf_counter() - prepare_start

    query_scan_start = time.perf_counter()
    promo_order_ids = _sort_rows(tuple(rt.query_postgresql_conjunctive_scan(connection, regional_app.PROMO_SCAN)))
    query_scan_sec = time.perf_counter() - query_scan_start

    query_count_start = time.perf_counter()
    if hasattr(connection, "_rtdl_fake_db"):
        connection._rtdl_fake_grouped_query = rt.normalize_grouped_query(regional_app.REGION_WORKLOAD)
    open_order_count_by_region = _sort_rows(
        tuple(rt.query_postgresql_grouped_count(connection, regional_app.REGION_WORKLOAD))
    )
    query_count_sec = time.perf_counter() - query_count_start

    query_sum_start = time.perf_counter()
    if hasattr(connection, "_rtdl_fake_db"):
        connection._rtdl_fake_grouped_query = rt.normalize_grouped_query(regional_app.REGION_REVENUE)
    web_revenue_by_region = _sort_rows(
        tuple(rt.query_postgresql_grouped_sum(connection, regional_app.REGION_REVENUE))
    )
    query_sum_sec = time.perf_counter() - query_sum_start

    postprocess_start = time.perf_counter()
    summary = regional_app._summarize_results(
        {
            "promo_order_ids": promo_order_ids,
            "open_order_count_by_region": open_order_count_by_region,
            "web_revenue_by_region": web_revenue_by_region,
        }
    )
    python_summary_postprocess_sec = time.perf_counter() - postprocess_start

    total_query_sec = query_scan_sec + query_count_sec + query_sum_sec
    section = {
        "app": "regional_order_dashboard",
        "requested_backend": "postgresql",
        "backend": "postgresql",
        "copies": copies,
        "output_mode": "compact_summary",
        "execution_mode": "prepared_session_semantics",
        "fallback_note": None,
        "session": {
            "table_construction_sec": input_construction_sec,
            "backend_selection_sec": 0.0,
            "prepare_sec": backend_prepare_sec,
        },
        "run_phases": {
            "query_conjunctive_scan_and_materialize_sec": query_scan_sec,
            "query_grouped_count_and_materialize_sec": query_count_sec,
            "query_grouped_sum_and_materialize_sec": query_sum_sec,
            "python_summary_postprocess_sec": python_summary_postprocess_sec,
        },
        "summary": summary,
        "row_counts": None,
        "results": {},
    }
    return section, {
        "input_pack_or_table_build": input_construction_sec,
        "backend_prepare": backend_prepare_sec,
        "native_query": total_query_sec,
        "copyback_or_materialization": total_query_sec,
        "python_summary_postprocess": python_summary_postprocess_sec,
    }


def _collect_postgresql_section(*, scenario: str, copies: int, dsn: str) -> tuple[dict[str, Any], dict[str, float]]:
    connection, close = _connect(dsn)
    try:
        if scenario == "sales_risk":
            return _run_sales_risk(connection, copies=copies)
        if scenario == "regional_dashboard":
            return _run_regional_dashboard(connection, copies=copies)
        raise ValueError(f"unsupported scenario: {scenario}")
    finally:
        if close is not None:
            close()


def build_postgresql_db_baseline_artifact(*, scenario: str, copies: int, iterations: int, dsn: str) -> dict[str, Any]:
    if scenario not in SCENARIOS:
        raise ValueError(f"unsupported scenario: {scenario}")
    if copies <= 0:
        raise ValueError("--copies must be positive")
    if iterations <= 0:
        raise ValueError("--iterations must be positive")

    baseline_name = "postgresql_same_semantics_on_linux_when_available"
    row = load_goal835_row(
        app="database_analytics",
        path_name=f"prepared_db_session_{scenario}",
        baseline_name=baseline_name,
    )
    section, phase_seconds = _collect_postgresql_section(scenario=scenario, copies=copies, dsn=dsn)
    reference_payload = goal756.run_suite(
        backends=("cpu",),
        scenario=scenario,
        copies=copies,
        iterations=iterations,
        output_mode="compact_summary",
        strict=True,
    )
    reference_result = next(result for result in reference_payload["results"] if result["backend"] == "cpu")
    reference_section = dict(reference_result["prepared_session_output"]["sections"][scenario])
    correctness_parity = _summary_fingerprint(section) == _summary_fingerprint(reference_section)

    return build_baseline_artifact(
        row=row,
        baseline_name=baseline_name,
        source_backend="postgresql",
        benchmark_scale={"copies": copies, "iterations": iterations},
        repeated_runs=iterations,
        correctness_parity=correctness_parity,
        phase_seconds=phase_seconds,
        summary={"scenario": scenario, "prepared_session_section": section},
        notes=[
            "This PostgreSQL artifact is same-semantics compact-summary baseline evidence for Linux hosts with live PostgreSQL available.",
            "The unified database analytics app does not expose PostgreSQL as a public backend; this collector validates equivalent bounded DB semantics against the CPU prepared compact-summary path.",
            "The current collector measures PostgreSQL query plus row materialization as one aggregate query total, so native_query and copyback_or_materialization share that total.",
            "This artifact does not authorize any public speedup claim.",
        ],
        validation={
            "goal": GOAL,
            "date": DATE,
            "scenario": scenario,
            "target_backend": "postgresql",
            "reference_backend": "cpu",
            "target_summary": _summary_fingerprint(section),
            "reference_summary": _summary_fingerprint(reference_section),
        },
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write a Goal836-valid PostgreSQL prepared DB baseline artifact.")
    parser.add_argument("--scenario", choices=SCENARIOS, required=True)
    parser.add_argument("--copies", type=int, default=20000)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--dsn", default="dbname=postgres")
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args(argv)

    artifact = build_postgresql_db_baseline_artifact(
        scenario=args.scenario,
        copies=args.copies,
        iterations=args.iterations,
        dsn=args.dsn,
    )
    write_baseline_artifact(args.output_json, artifact)
    print(Path(args.output_json).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
