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

    from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app

    output_path = repo / "docs/reports/goal2516_partner_resident_composite_avg_sum_count_pod_2026-05-22.json"
    native_text = "\n".join(
        (repo / relpath).read_text(encoding="utf-8")
        for relpath in (
            "src/native/optix/rtdl_optix_api.cpp",
            "src/native/optix/rtdl_optix_prelude.h",
            "src/native/optix/rtdl_optix_workloads.cpp",
        )
    ).lower()
    native_avg_symbol_absent = (
        "rtdl_optix_columnar_device_payload_grouped_avg" not in native_text
        and "run_device_column_grouped_avg" not in native_text
    )
    payload: dict[str, object] = {
        "goal": "Goal2516 partner-resident composite avg_as_sum_count",
        "python": sys.version,
        "platform": platform.platform(),
        "git_head": _run_text(["git", "-C", str(repo), "rev-parse", "HEAD"]),
        "rtdl_optix_lib": os.environ.get("RTDL_OPTIX_LIB", ""),
        "native_avg_symbol_absent": native_avg_symbol_absent,
    }
    try:
        torch = app.require_optix_partner_resident_experimental_backend()
    except Exception as exc:
        payload.update(
            {
                "status": "blocked",
                "blocked_reason": str(exc),
                "claim_boundary": (
                    "Pod did not provide the required PyTorch CUDA plus OptiX runtime for the "
                    "experimental partner-resident composite aggregate path."
                ),
            }
        )
        output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return 2

    avg_payload = app.run_result_mode(
        "avg_as_sum_count",
        backend=app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND,
    )
    cpu_avg_payload = app.run_result_mode("avg_as_sum_count", backend="cpu_python_reference")
    suite = app.run_suite(backend=app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND)
    payload.update(
        {
            "status": "ok",
            "cuda_available": bool(torch.cuda.is_available()),
            "torch_version": getattr(torch, "__version__", "unknown"),
            "avg_rows": avg_payload["rows"],
            "cpu_avg_rows": cpu_avg_payload["rows"],
            "avg_matches_cpu": tuple(avg_payload["rows"]) == tuple(cpu_avg_payload["rows"]),
            "avg_metadata": avg_payload["metadata"],
            "app_suite_modes": list(suite["modes"]),
            "app_suite_all_match_cpu_reference": bool(suite["all_match_cpu_reference"]),
            "claim_boundary": (
                "Experimental partner-resident composite aggregate evidence only. "
                "avg_as_sum_count lowers to generic sum+count reductions; no native average ABI exists. "
                "No public speedup, true zero-copy, SQL, DBMS, or complete RayDB claim."
            ),
        }
    )
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return 0 if (
        payload["native_avg_symbol_absent"]
        and payload["avg_matches_cpu"]
        and payload["app_suite_all_match_cpu_reference"]
        and payload["app_suite_modes"] == ["count", "sum", "min", "max", "avg_as_sum_count"]
        and payload["avg_metadata"]["composite_lowering"] == ["sum", "count"]
        and payload["avg_metadata"]["native_launch_count"] == 2
        and payload["avg_metadata"]["native_avg_abi_added"] is False
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
