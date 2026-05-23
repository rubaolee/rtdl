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
    from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app

    output_path = repo / "docs/reports/goal2514_partner_resident_compact_output_pod_2026-05-22.json"
    source = (repo / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
    compact_output_source_check = all(
        marker in source
        for marker in (
            "device_column_grouped_i64_compact_count_kernel",
            "device_column_grouped_i64_compact_sum_kernel",
            "download(count_rows.data(), d_rows.ptr, compact_row_count)",
            "download(sum_rows.data(), d_rows.ptr, compact_row_count)",
        )
    ) and "download(group_counts.data()" not in source and "download(group_sums.data()" not in source

    payload: dict[str, object] = {
        "goal": "Goal2514 partner-resident compact grouped output",
        "python": sys.version,
        "platform": platform.platform(),
        "git_head": _run_text(["git", "-C", str(repo), "rev-parse", "HEAD"]),
        "rtdl_optix_lib": os.environ.get("RTDL_OPTIX_LIB", ""),
        "cuda_available": bool(torch.cuda.is_available()),
        "torch_version": getattr(torch, "__version__", "unknown"),
        "compact_output_source_check": compact_output_source_check,
    }
    if not torch.cuda.is_available():
        payload["status"] = "blocked_no_cuda"
        output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return 2

    suite = app.run_suite(backend=app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND)
    count_rows = suite["modes"]["count"]["rows"]
    sum_rows = suite["modes"]["sum"]["rows"]
    payload.update(
        {
            "status": "ok",
            "group_capacity": suite["modes"]["count"]["metadata"]["group_capacity"],
            "count_rows_downloaded": len(count_rows),
            "sum_rows_downloaded": len(sum_rows),
            "count_rows": count_rows,
            "sum_rows": sum_rows,
            "all_match_cpu_reference": bool(suite["all_match_cpu_reference"]),
            "claim_boundary": (
                "Experimental compact grouped-output evidence only. Host downloads compact result "
                "rows rather than capacity-sized count/sum workspaces; no true zero-copy, sparse "
                "group-key, SQL/DBMS, whole-app, or public speedup claim is authorized."
            ),
        }
    )
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return 0 if (
        compact_output_source_check
        and payload["all_match_cpu_reference"]
        and payload["count_rows_downloaded"] == 3
        and payload["sum_rows_downloaded"] == 3
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
