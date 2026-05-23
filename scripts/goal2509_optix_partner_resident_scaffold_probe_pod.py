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
    text = (result.stdout + result.stderr).strip()
    return text


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    if str(repo / "src") not in sys.path:
        sys.path.insert(0, str(repo / "src"))
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))

    import torch
    import rtdsl as rt

    output_path = repo / "docs/reports/goal2509_optix_partner_resident_scaffold_probe_pod_2026-05-22.json"
    result: dict[str, object] = {
        "goal": "Goal2509 OptiX partner-resident scaffold pod probe",
        "python": sys.version,
        "platform": platform.platform(),
        "git_head": _run_text(["git", "-C", str(repo), "rev-parse", "HEAD"]),
        "cuda_available": bool(torch.cuda.is_available()),
        "torch_version": getattr(torch, "__version__", "unknown"),
        "rtdl_optix_lib": os.environ.get("RTDL_OPTIX_LIB", ""),
        "native_symbol": rt.OPTIX_PARTNER_RESIDENT_COLUMNAR_DEVICE_SYMBOL,
    }
    if not torch.cuda.is_available():
        result["probe_status"] = "blocked_no_cuda"
        output_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        return 2

    row_ids = torch.arange(4, dtype=torch.int64, device="cuda")
    columns = {
        "region_id": torch.tensor([1, 1, 2, 2], dtype=torch.int64, device="cuda"),
        "ship_year": torch.tensor([1995, 1996, 1997, 1998], dtype=torch.int64, device="cuda"),
        "revenue": torch.tensor([10.0, 20.0, 30.0, 40.0], dtype=torch.float64, device="cuda"),
    }
    descriptor = rt.prepare_partner_resident_columnar_record_set(
        {"row_ids": row_ids, "columns": columns},
        backend="optix",
    )
    result["descriptor"] = descriptor.to_metadata()

    try:
        rt.prepare_optix_partner_resident_columnar_record_set(
            descriptor,
            primary_fields=("region_id", "ship_year"),
            allow_scaffold_probe=True,
        )
    except Exception as exc:  # noqa: BLE001 - this script records the exact fail-closed path.
        message = str(exc)
        result["error"] = message
        if "fail-closed ABI scaffold" in message and "native execution is not implemented" in message:
            result["probe_status"] = "expected_fail_closed"
            output_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            return 0
        result["probe_status"] = "unexpected_error"
        output_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        return 1

    result["probe_status"] = "unexpected_success"
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
