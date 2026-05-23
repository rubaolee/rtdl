#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from pathlib import Path


def _run_text(command: list[str]) -> str:
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    return (result.stdout + result.stderr).strip()


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo / "src"))
    sys.path.insert(0, str(repo))

    import torch
    import rtdsl as rt
    from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app

    output_path = repo / "docs/reports/goal2513_partner_resident_group_capacity_pod_2026-05-22.json"
    payload: dict[str, object] = {
        "goal": "Goal2513 partner-resident group_capacity contract",
        "python": sys.version,
        "platform": platform.platform(),
        "git_head": _run_text(["git", "-C", str(repo), "rev-parse", "HEAD"]),
        "rtdl_optix_lib": os.environ.get("RTDL_OPTIX_LIB", ""),
        "cuda_available": bool(torch.cuda.is_available()),
        "torch_version": getattr(torch, "__version__", "unknown"),
        "with_capacity_symbols": {
            "count": rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_WITH_CAPACITY_SYMBOL,
            "sum": rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_I64_WITH_CAPACITY_SYMBOL,
        },
    }
    if not torch.cuda.is_available():
        payload["status"] = "blocked_no_cuda"
        output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return 2

    fixture = app.make_fixture()
    count_plan = app.make_plan("count")
    sum_plan = app.make_plan("sum")
    group_capacity = app._infer_dense_group_capacity(fixture, count_plan)
    record_set = {
        "row_ids": torch.tensor(fixture["row_ids"], dtype=torch.int64, device="cuda"),
        "columns": {
            name: torch.tensor(values, dtype=torch.int64, device="cuda")
            for name, values in fixture["columns"].items()
        },
    }
    descriptor = rt.prepare_partner_resident_columnar_record_set(record_set, backend="optix")
    count_query = rt.columnar_plan_to_grouped_query(count_plan)
    sum_query = rt.columnar_plan_to_grouped_query(sum_plan)
    count_rows = rt.run_optix_partner_resident_columnar_grouped_count_i64(
        descriptor,
        count_query,
        allow_experimental_native=True,
        group_capacity=group_capacity,
    )
    sum_rows = rt.run_optix_partner_resident_columnar_grouped_sum_i64(
        descriptor,
        sum_query,
        allow_experimental_native=True,
        group_capacity=group_capacity,
    )
    expected_count = tuple(app.run_result_mode("count")["rows"])
    expected_sum = tuple(app.run_result_mode("sum")["rows"])

    expected_capacity_error = ""
    try:
        rt.run_optix_partner_resident_columnar_grouped_count_i64(
            descriptor,
            count_query,
            allow_experimental_native=True,
            group_capacity=2,
        )
    except RuntimeError as exc:
        expected_capacity_error = str(exc)

    app_suite = app.run_suite(backend=app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND)
    payload.update(
        {
            "status": "ok",
            "group_capacity": group_capacity,
            "legacy_default_capacity": 65536,
            "capacity_is_explicit": True,
            "descriptor": descriptor.to_metadata(),
            "count_rows": list(count_rows),
            "sum_rows": list(sum_rows),
            "count_matches_cpu": tuple(count_rows) == expected_count,
            "sum_matches_cpu": tuple(sum_rows) == expected_sum,
            "expected_capacity_error": expected_capacity_error,
            "capacity_error_matched": "below group_capacity" in expected_capacity_error,
            "app_suite_group_capacity": app_suite["modes"]["count"]["metadata"]["group_capacity"],
            "app_suite_all_match_cpu_reference": bool(app_suite["all_match_cpu_reference"]),
            "claim_boundary": (
                "Experimental explicit group_capacity evidence only. No arbitrary sparse group-key, "
                "true zero-copy, whole-app, SQL/DBMS, or public speedup claim is authorized."
            ),
        }
    )
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return 0 if (
        payload["count_matches_cpu"]
        and payload["sum_matches_cpu"]
        and payload["capacity_error_matched"]
        and payload["app_suite_group_capacity"] == group_capacity
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
