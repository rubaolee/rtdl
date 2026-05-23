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

    output_path = repo / "docs/reports/goal2511_optix_partner_resident_device_grouped_i64_pod_2026-05-22.json"
    payload: dict[str, object] = {
        "goal": "Goal2511 OptiX partner-resident device grouped i64 execution",
        "python": sys.version,
        "platform": platform.platform(),
        "git_head": _run_text(["git", "-C", str(repo), "rev-parse", "HEAD"]),
        "cuda_available": bool(torch.cuda.is_available()),
        "torch_version": getattr(torch, "__version__", "unknown"),
        "rtdl_optix_lib": os.environ.get("RTDL_OPTIX_LIB", ""),
        "native_symbols": {
            "count": rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_COUNT_I64_SYMBOL,
            "sum": rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_SUM_I64_SYMBOL,
        },
    }
    if not torch.cuda.is_available():
        payload["status"] = "blocked_no_cuda"
        output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return 2

    fixture = app.make_fixture()
    record_set = {
        "row_ids": torch.tensor(fixture["row_ids"], dtype=torch.int64, device="cuda"),
        "columns": {
            name: torch.tensor(values, dtype=torch.int64, device="cuda")
            for name, values in fixture["columns"].items()
        },
    }
    descriptor = rt.prepare_partner_resident_columnar_record_set(record_set, backend="optix")
    count_query = rt.columnar_plan_to_grouped_query(app.make_plan("count"))
    sum_query = rt.columnar_plan_to_grouped_query(app.make_plan("sum"))
    count_rows = rt.run_optix_partner_resident_columnar_grouped_count_i64(
        descriptor,
        count_query,
        allow_experimental_native=True,
    )
    sum_rows = rt.run_optix_partner_resident_columnar_grouped_sum_i64(
        descriptor,
        sum_query,
        allow_experimental_native=True,
    )
    expected_count = tuple(app.run_result_mode("count")["rows"])
    expected_sum = tuple(app.run_result_mode("sum")["rows"])
    payload.update(
        {
            "status": "ok",
            "descriptor": descriptor.to_metadata(),
            "count_rows": list(count_rows),
            "sum_rows": list(sum_rows),
            "expected_count_rows": list(expected_count),
            "expected_sum_rows": list(expected_sum),
            "count_matches_cpu": tuple(count_rows) == expected_count,
            "sum_matches_cpu": tuple(sum_rows) == expected_sum,
            "claim_boundary": (
                "Experimental partner-resident CUDA grouped count/sum slice only. "
                "No public speedup, true zero-copy, SQL, DBMS, or complete RayDB claim."
            ),
        }
    )
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return 0 if payload["count_matches_cpu"] and payload["sum_matches_cpu"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
