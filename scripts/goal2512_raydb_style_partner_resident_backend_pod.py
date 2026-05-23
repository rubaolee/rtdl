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
    from scripts import goal2500_raydb_style_backend_matrix as matrix

    output_path = repo / "docs/reports/goal2512_raydb_style_partner_resident_backend_pod_2026-05-22.json"
    payload: dict[str, object] = {
        "goal": "Goal2512 RayDB-style partner-resident experimental backend",
        "python": sys.version,
        "platform": platform.platform(),
        "git_head": _run_text(["git", "-C", str(repo), "rev-parse", "HEAD"]),
        "rtdl_optix_lib": os.environ.get("RTDL_OPTIX_LIB", ""),
        "backend": app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND,
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
                    "experimental partner-resident RayDB-style backend."
                ),
            }
        )
        output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return 2

    suite = app.run_suite(backend=app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND)
    backend_matrix = matrix.run_matrix(
        backends=(app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND,),
        repeats=3,
    )
    payload.update(
        {
            "status": "ok",
            "cuda_available": bool(torch.cuda.is_available()),
            "torch_version": getattr(torch, "__version__", "unknown"),
            "suite": suite,
            "matrix": backend_matrix,
            "all_match_cpu_reference": bool(suite["all_match_cpu_reference"])
            and bool(
                backend_matrix["cases"][app.OPTIX_PARTNER_RESIDENT_EXPERIMENTAL_BACKEND][
                    "all_match_cpu_reference"
                ]
            ),
            "claim_boundary": (
                "Experimental synthetic RayDB-style partner-resident backend evidence only. "
                "No RayDB reproduction, SQL/DBMS, true zero-copy, whole-app, authors-code, "
                "or public speedup claim is authorized."
            ),
        }
    )
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return 0 if payload["all_match_cpu_reference"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
