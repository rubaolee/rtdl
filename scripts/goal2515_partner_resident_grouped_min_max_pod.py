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


def _sort_rows(rows: tuple[dict[str, object], ...] | list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted((dict(row) for row in rows), key=lambda row: int(row["region_id"]))


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo / "src"))
    sys.path.insert(0, str(repo))

    import torch
    import rtdsl as rt
    from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app

    output_path = repo / "docs/reports/goal2515_partner_resident_grouped_min_max_pod_2026-05-22.json"
    payload: dict[str, object] = {
        "goal": "Goal2515 partner-resident grouped min/max i64",
        "python": sys.version,
        "platform": platform.platform(),
        "git_head": _run_text(["git", "-C", str(repo), "rev-parse", "HEAD"]),
        "rtdl_optix_lib": os.environ.get("RTDL_OPTIX_LIB", ""),
        "cuda_available": bool(torch.cuda.is_available()),
        "torch_version": getattr(torch, "__version__", "unknown"),
        "symbols": {
            "min": rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_MIN_I64_WITH_CAPACITY_SYMBOL,
            "max": rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_MAX_I64_WITH_CAPACITY_SYMBOL,
        },
    }
    if not torch.cuda.is_available():
        payload["status"] = "blocked_no_cuda"
        output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return 2

    fixture = app.make_fixture()
    min_plan = app.make_plan("min")
    max_plan = app.make_plan("max")
    group_capacity = app._infer_dense_group_capacity(fixture, min_plan)
    record_set = {
        "row_ids": torch.tensor(fixture["row_ids"], dtype=torch.int64, device="cuda"),
        "columns": {
            name: torch.tensor(values, dtype=torch.int64, device="cuda")
            for name, values in fixture["columns"].items()
        },
    }
    descriptor = rt.prepare_partner_resident_columnar_record_set(record_set, backend="optix")
    min_rows = rt.run_optix_partner_resident_columnar_grouped_min_i64(
        descriptor,
        rt.columnar_plan_to_grouped_query(min_plan),
        allow_experimental_native=True,
        group_capacity=group_capacity,
    )
    max_rows = rt.run_optix_partner_resident_columnar_grouped_max_i64(
        descriptor,
        rt.columnar_plan_to_grouped_query(max_plan),
        allow_experimental_native=True,
        group_capacity=group_capacity,
    )
    expected_min = tuple(app.run_result_mode("min")["rows"])
    expected_max = tuple(app.run_result_mode("max")["rows"])

    signed_fixture = {
        "row_ids": torch.arange(1, 6, dtype=torch.int64, device="cuda"),
        "columns": {
            "region_id": torch.tensor((0, 0, 1, 1, 2), dtype=torch.int64, device="cuda"),
            "revenue": torch.tensor((10, -5, -20, 7, 3), dtype=torch.int64, device="cuda"),
        },
    }
    signed_descriptor = rt.prepare_partner_resident_columnar_record_set(signed_fixture, backend="optix")
    signed_query = {"predicates": (), "group_keys": ("region_id",), "value_field": "revenue"}
    signed_min_rows = _sort_rows(
        rt.run_optix_partner_resident_columnar_grouped_min_i64(
            signed_descriptor,
            signed_query,
            allow_experimental_native=True,
            group_capacity=3,
        )
    )
    signed_max_rows = _sort_rows(
        rt.run_optix_partner_resident_columnar_grouped_max_i64(
            signed_descriptor,
            signed_query,
            allow_experimental_native=True,
            group_capacity=3,
        )
    )
    expected_signed_min = [
        {"region_id": 0, "min": -5},
        {"region_id": 1, "min": -20},
        {"region_id": 2, "min": 3},
    ]
    expected_signed_max = [
        {"region_id": 0, "max": 10},
        {"region_id": 1, "max": 7},
        {"region_id": 2, "max": 3},
    ]

    app_suite = app.run_suite(backend=app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND)
    payload.update(
        {
            "status": "ok",
            "group_capacity": group_capacity,
            "descriptor": descriptor.to_metadata(),
            "min_rows": list(min_rows),
            "max_rows": list(max_rows),
            "min_matches_cpu": tuple(min_rows) == expected_min,
            "max_matches_cpu": tuple(max_rows) == expected_max,
            "signed_min_rows": signed_min_rows,
            "signed_max_rows": signed_max_rows,
            "signed_min_matches_expected": signed_min_rows == expected_signed_min,
            "signed_max_matches_expected": signed_max_rows == expected_signed_max,
            "app_suite_modes": list(app_suite["modes"]),
            "app_suite_all_match_cpu_reference": bool(app_suite["all_match_cpu_reference"]),
            "claim_boundary": (
                "Experimental partner-resident CUDA grouped count/sum/min/max slice only. "
                "No public speedup, true zero-copy, SQL, DBMS, or complete RayDB claim."
            ),
        }
    )
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return 0 if (
        payload["min_matches_cpu"]
        and payload["max_matches_cpu"]
        and payload["signed_min_matches_expected"]
        and payload["signed_max_matches_expected"]
        and payload["app_suite_all_match_cpu_reference"]
        and payload["app_suite_modes"] == ["count", "sum", "min", "max"]
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
