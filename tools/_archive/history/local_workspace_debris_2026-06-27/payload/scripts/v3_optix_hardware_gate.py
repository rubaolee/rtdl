#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
from typing import Any


RT_HARDWARE_NAME_PATTERNS = (
    re.compile(r"\bRTX\b", re.IGNORECASE),
    re.compile(r"\bA10\b", re.IGNORECASE),
    re.compile(r"\bA16\b", re.IGNORECASE),
    re.compile(r"\bA2\b", re.IGNORECASE),
    re.compile(r"\bA30\b", re.IGNORECASE),
    re.compile(r"\bA40\b", re.IGNORECASE),
    re.compile(r"\bL4\b", re.IGNORECASE),
    re.compile(r"\bL40S?\b", re.IGNORECASE),
)


def parse_nvidia_smi_rows(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split(",")]
        rows.append(
            {
                "name": parts[0] if len(parts) > 0 else "",
                "driver_version": parts[1] if len(parts) > 1 else "",
                "compute_cap": parts[2] if len(parts) > 2 else "",
            }
        )
    return rows


def row_has_rt_hardware(row: dict[str, str]) -> bool:
    name = row.get("name", "")
    return any(pattern.search(name) for pattern in RT_HARDWARE_NAME_PATTERNS)


def query_nvidia_smi() -> tuple[list[dict[str, str]], str | None]:
    command = [
        "nvidia-smi",
        "--query-gpu=name,driver_version,compute_cap",
        "--format=csv,noheader",
    ]
    try:
        completed = subprocess.run(command, check=True, text=True, capture_output=True)
    except Exception as exc:  # pragma: no cover - requires NVIDIA host
        return [], repr(exc)
    return parse_nvidia_smi_rows(completed.stdout), None


def build_payload(*, require_rt_hardware: bool, sample_nvidia_smi: str | None) -> dict[str, Any]:
    if sample_nvidia_smi is None:
        rows, query_error = query_nvidia_smi()
    else:
        rows = parse_nvidia_smi_rows(sample_nvidia_smi)
        query_error = None
    optix_capable = bool(rows)
    rt_hardware_ready = any(row_has_rt_hardware(row) for row in rows)
    checks = {
        "nvidia_smi_query": query_error is None,
        "has_nvidia_gpu": bool(rows),
        "optix_capable_gpu_present": optix_capable,
        "rt_hardware_name_present": rt_hardware_ready,
    }
    status = "pass" if checks["nvidia_smi_query"] and optix_capable and (rt_hardware_ready or not require_rt_hardware) else "fail"
    return {
        "tool": "v3_optix_hardware_gate",
        "status": status,
        "require_rt_hardware": require_rt_hardware,
        "gpus": rows,
        "checks": checks,
        "query_error": query_error,
        "fail_closed_reason": None
        if status == "pass"
        else "No NVIDIA GPU satisfying the V3 OptiX/RT hardware precondition was detected.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fail-closed V3 OptiX/RT hardware precondition gate.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--require-rt-hardware", action="store_true")
    parser.add_argument(
        "--sample-nvidia-smi",
        help="Testing hook: parse this noheader nvidia-smi CSV output instead of executing nvidia-smi.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(
        require_rt_hardware=bool(args.require_rt_hardware),
        sample_nvidia_smi=args.sample_nvidia_smi,
    )
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
