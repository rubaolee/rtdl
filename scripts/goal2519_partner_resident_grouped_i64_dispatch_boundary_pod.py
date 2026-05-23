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


def _canonical(rows) -> list[tuple[tuple[str, object], ...]]:
    return sorted(tuple(sorted(row.items())) for row in rows)


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo / "src"))
    sys.path.insert(0, str(repo))

    import rtdsl as rt
    from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app

    output_path = repo / "docs/reports/goal2519_partner_resident_grouped_i64_dispatch_boundary_pod_2026-05-23.json"
    app_source = (repo / "examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py").read_text(
        encoding="utf-8"
    )
    low_level_names = (
        "run_optix_partner_resident_columnar_grouped_count_i64(",
        "run_optix_partner_resident_columnar_grouped_sum_i64(",
        "run_optix_partner_resident_columnar_grouped_min_i64(",
        "run_optix_partner_resident_columnar_grouped_max_i64(",
        "run_optix_partner_resident_columnar_grouped_sum_count_i64(",
    )
    native_text = "\n".join(
        (repo / relpath).read_text(encoding="utf-8")
        for relpath in (
            "src/native/optix/rtdl_optix_api.cpp",
            "src/native/optix/rtdl_optix_prelude.h",
            "src/native/optix/rtdl_optix_workloads.cpp",
        )
    ).lower()
    payload: dict[str, object] = {
        "goal": "Goal2519 partner-resident grouped i64 dispatch boundary",
        "python": sys.version,
        "platform": platform.platform(),
        "git_head": _run_text(["git", "-C", str(repo), "rev-parse", "HEAD"]),
        "rtdl_optix_lib": os.environ.get("RTDL_OPTIX_LIB", ""),
        "ld_library_path": os.environ.get("LD_LIBRARY_PATH", ""),
        "dispatcher_exported": hasattr(rt, "run_optix_partner_resident_columnar_grouped_i64_reduction"),
        "dispatcher_reductions": list(rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_GROUPED_I64_REDUCTIONS),
        "app_uses_dispatcher": "run_optix_partner_resident_columnar_grouped_i64_reduction(" in app_source,
        "app_direct_low_level_symbols_absent": all(name not in app_source for name in low_level_names),
        "native_avg_symbol_absent": (
            "rtdl_optix_columnar_device_payload_grouped_avg" not in native_text
            and "run_device_column_grouped_avg" not in native_text
        ),
        "claim_boundary": (
            "Experimental dispatcher-boundary evidence only. The app asks for generic grouped i64 "
            "reductions; the runtime selects native symbols. No SQL, DBMS, whole-app, true zero-copy, "
            "or public performance claim is authorized."
        ),
    }
    try:
        torch = app.require_optix_partner_resident_experimental_backend()
    except Exception as exc:
        payload.update({"status": "blocked", "blocked_reason": str(exc)})
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

    direct_cases: dict[str, object] = {}
    for mode in app.OPTIX_PARTNER_RESIDENT_RESULT_MODES:
        plan = app.make_plan(mode)
        group_capacity = app._infer_dense_group_capacity(fixture, plan)
        query = rt.columnar_plan_to_grouped_query(plan)
        reduction = mode
        composite_lowering: tuple[str, ...] = ()
        if mode == "avg_as_sum_count":
            decomposed_plans = rt.decompose_columnar_aggregate_plan(plan)
            composite_lowering = tuple(item.aggregate for item in decomposed_plans)
            query = rt.columnar_plan_to_grouped_query(decomposed_plans[0])
            reduction = "sum_count"
        dispatch_result = rt.run_optix_partner_resident_columnar_grouped_i64_reduction(
            descriptor,
            query,
            reduction=reduction,
            allow_experimental_native=True,
            group_capacity=group_capacity,
            semantic_aggregate=mode,
        )
        rows = tuple(dispatch_result["rows"])
        cpu_rows = tuple(app.run_result_mode(mode, backend="cpu_python_reference")["rows"])
        direct_cases[mode] = {
            "reduction": reduction,
            "rows": list(rows),
            "cpu_rows": list(cpu_rows),
            "matches_cpu_reference": _canonical(rows) == _canonical(cpu_rows),
            "metadata": dispatch_result["metadata"],
            "composite_lowering": list(composite_lowering),
        }

    suite = app.run_suite(backend=app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND)
    avg_metadata = suite["modes"]["avg_as_sum_count"]["metadata"]
    payload.update(
        {
            "status": "ok",
            "cuda_available": bool(torch.cuda.is_available()),
            "torch_version": getattr(torch, "__version__", "unknown"),
            "optix_version": list(rt.optix_version()),
            "descriptor": descriptor.to_metadata(),
            "direct_cases": direct_cases,
            "direct_dispatch_all_match_cpu_reference": all(
                bool(case["matches_cpu_reference"]) for case in direct_cases.values()
            ),
            "app_suite_modes": list(suite["modes"]),
            "app_suite_all_match_cpu_reference": bool(suite["all_match_cpu_reference"]),
            "avg_metadata": avg_metadata,
        }
    )
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    ok = (
        payload["dispatcher_reductions"] == ["count", "sum", "min", "max", "sum_count"]
        and payload["app_uses_dispatcher"]
        and payload["app_direct_low_level_symbols_absent"]
        and payload["native_avg_symbol_absent"]
        and payload["direct_dispatch_all_match_cpu_reference"]
        and payload["app_suite_all_match_cpu_reference"]
        and avg_metadata["partner_resident_grouped_i64_dispatcher"] is True
        and avg_metadata["semantic_aggregate"] == "avg_as_sum_count"
        and avg_metadata["reduction"] == "sum_count"
        and avg_metadata["native_launch_count"] == 1
        and avg_metadata["generic_sum_count_abi_used"] is True
        and avg_metadata["native_avg_abi_added"] is False
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
