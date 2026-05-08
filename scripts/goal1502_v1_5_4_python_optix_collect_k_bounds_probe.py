#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from rtdsl import optix_runtime
from scripts.goal1500_v1_5_4_optix_device_collect_k_measurement import CudaDriver


REPORT_STEM = "goal1502_v1_5_4_python_optix_collect_k_bounds_probe_2026-05-08"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"
DEFAULT_LIBRARY_PATH = ROOT / "build" / "librtdl_optix.so"


def _run_command(command: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError as exc:
        return {"command": command, "returncode": 127, "stdout": "", "stderr": f"{type(exc).__name__}: {exc}"}
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _git_head() -> str:
    result = _run_command(["git", "rev-parse", "HEAD"])
    return result["stdout"] if result["returncode"] == 0 else "unknown"


def _rows_from_flat(values: ctypes.Array, row_width: int, row_count: int) -> list[list[int]]:
    return [
        [int(values[row_index * row_width + column]) for column in range(row_width)]
        for row_index in range(row_count)
    ]


def _run_collect(
    cuda: CudaDriver,
    rows: list[tuple[int, ...]],
    *,
    row_width: int,
    capacity: int,
    output_sentinel: int = -777,
) -> dict[str, Any]:
    flat_rows = [int(cell) for row in rows for cell in row]
    input_array_type = ctypes.c_int64 * len(flat_rows)
    input_array = input_array_type(*flat_rows)
    output_elements = max(1, row_width * max(1, capacity))
    output_array_type = ctypes.c_int64 * output_elements
    sentinel_array = output_array_type(*([output_sentinel] * output_elements))
    output_array = output_array_type()

    candidate_ptr = ctypes.c_ulonglong()
    output_ptr = ctypes.c_ulonglong()
    try:
        candidate_ptr = cuda.alloc(ctypes.sizeof(input_array))
        output_ptr = cuda.alloc(ctypes.sizeof(sentinel_array))
        cuda.h2d(candidate_ptr, input_array, ctypes.sizeof(input_array))
        cuda.h2d(output_ptr, sentinel_array, ctypes.sizeof(sentinel_array))
        result = optix_runtime.collect_k_bounded_i64_device_optix(
            candidate_rows_device_ptr=candidate_ptr.value,
            candidate_count=len(rows),
            row_width=row_width,
            rows_out_device_ptr=output_ptr.value,
            row_capacity=capacity,
            allow_experimental=True,
        )
        cuda.d2h(output_array, output_ptr, ctypes.sizeof(output_array))
        return {
            "status": "ok",
            "result": result,
            "output_flat": [int(value) for value in output_array],
            "output_rows": _rows_from_flat(output_array, row_width, min(capacity, int(result["valid_count"]))),
        }
    finally:
        if output_ptr.value:
            cuda.free(output_ptr)
        if candidate_ptr.value:
            cuda.free(candidate_ptr)


def run_probe(library_path: Path) -> dict[str, Any]:
    os.environ["RTDL_OPTIX_LIB"] = str(library_path)
    cuda = CudaDriver()
    try:
        overflow_case = _run_collect(
            cuda,
            [(2, 20), (1, 10), (2, 20), (3, 30)],
            row_width=2,
            capacity=2,
        )
        row_width3_case = _run_collect(
            cuda,
            [(2, 20, 200), (1, 10, 100), (2, 20, 200), (3, 30, 300)],
            row_width=3,
            capacity=3,
        )

        overflow_result = overflow_case["result"]
        overflow_output_flat = overflow_case["output_flat"]
        fail_closed_output_preserved = all(value == -777 for value in overflow_output_flat)
        row_width3_result = row_width3_case["result"]
        row_width3_expected = [[1, 10, 100], [2, 20, 200], [3, 30, 300]]
        return {
            "goal": "Goal1502",
            "status": "goal1502_python_optix_collect_k_bounds_and_dynamic_width_probe_passed",
            "git_commit": _git_head(),
            "platform": platform.platform(),
            "device_name": cuda.device_name(),
            "cuda_driver_version": cuda.driver_version(),
            "library_path": str(library_path),
            "measured_on_real_nvidia": True,
            "python_entry_point": "rtdsl.optix_runtime.collect_k_bounded_i64_device_optix",
            "native_symbol": optix_runtime.OPTIX_COLLECT_K_BOUNDED_I64_DEVICE_SYMBOL,
            "overflow_case": {
                "candidate_rows": [[2, 20], [1, 10], [2, 20], [3, 30]],
                "row_width": 2,
                "capacity": 2,
                "valid_count": int(overflow_result["valid_count"]),
                "overflowed": bool(overflow_result["overflowed"]),
                "output_flat_after_call": overflow_output_flat,
                "fail_closed_output_preserved": fail_closed_output_preserved,
                "transfer_accounting": overflow_result["transfer_accounting"],
            },
            "dynamic_row_width_case": {
                "row_width": 3,
                "capacity": 3,
                "candidate_rows": [[2, 20, 200], [1, 10, 100], [2, 20, 200], [3, 30, 300]],
                "expected_rows": row_width3_expected,
                "candidate_id_rows": row_width3_case["output_rows"],
                "valid_count": int(row_width3_result["valid_count"]),
                "overflowed": bool(row_width3_result["overflowed"]),
                "same_candidate_rows": row_width3_case["output_rows"] == row_width3_expected,
                "same_valid_count": int(row_width3_result["valid_count"]) == 3,
                "same_overflowed_flag": bool(row_width3_result["overflowed"]) is False,
                "transfer_accounting": row_width3_result["transfer_accounting"],
            },
            "claim_flags": {
                "true_zero_copy_authorized": False,
                "public_speedup_wording_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "stable_public_primitive_authorized": False,
                "partner_tensor_handoff_authorized": False,
                "release_action_authorized": False,
            },
            "claim_boundary": (
                "Goal1502 validates bounds behavior and dynamic row-width behavior for "
                "the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. "
                "It does not authorize "
                "true zero-copy wording, public speedup wording, whole-app claims, "
                "partner tensor handoff, stable primitive promotion, or release action."
            ),
        }
    finally:
        cuda.close()


def validate_probe(probe: dict[str, Any]) -> dict[str, Any]:
    if probe.get("goal") != "Goal1502":
        raise ValueError("invalid Goal1502 report goal")
    if probe.get("measured_on_real_nvidia") is not True:
        raise ValueError("Goal1502 must be measured on real NVIDIA hardware")
    overflow = probe.get("overflow_case", {})
    if overflow.get("valid_count") != 3:
        raise ValueError("Goal1502 overflow case must report full unique valid_count")
    if overflow.get("overflowed") is not True:
        raise ValueError("Goal1502 overflow case must set overflowed=True")
    if overflow.get("fail_closed_output_preserved") is not True:
        raise ValueError("Goal1502 overflow case must preserve the output sentinel")
    dynamic = probe.get("dynamic_row_width_case", {})
    if dynamic.get("same_candidate_rows") is not True:
        raise ValueError("Goal1502 dynamic row_width case candidate rows failed")
    if dynamic.get("same_valid_count") is not True:
        raise ValueError("Goal1502 dynamic row_width case valid_count failed")
    if dynamic.get("same_overflowed_flag") is not True:
        raise ValueError("Goal1502 dynamic row_width case overflow flag failed")
    for flag, value in probe.get("claim_flags", {}).items():
        if value is not False:
            raise ValueError(f"Goal1502 must keep {flag}=False")
    return probe


def to_markdown(probe: dict[str, Any]) -> str:
    overflow = probe["overflow_case"]
    dynamic = probe["dynamic_row_width_case"]
    return "\n".join(
        [
            "# Goal 1502: Python OptiX COLLECT_K_BOUNDED Bounds Probe",
            "",
            "## Verdict",
            "",
            f"`{probe['status']}`",
            "",
            "## Scope",
            "",
            f"- Python entry point: `{probe['python_entry_point']}`",
            f"- Native symbol: `{probe['native_symbol']}`",
            f"- Device: `{probe['device_name']}`",
            f"- Git commit: `{probe['git_commit']}`",
            "",
            "## Bounds",
            "",
            f"- Overflow valid count: `{overflow['valid_count']}`",
            f"- Overflow flag: `{overflow['overflowed']}`",
            f"- Output sentinel preserved on overflow: `{overflow['fail_closed_output_preserved']}`",
            f"- Dynamic row_width=3 row parity: `{dynamic['same_candidate_rows']}`",
            f"- Dynamic row_width=3 valid count parity: `{dynamic['same_valid_count']}`",
            f"- Dynamic row_width=3 overflow parity: `{dynamic['same_overflowed_flag']}`",
            "",
            "## Claim Boundary",
            "",
            probe["claim_boundary"],
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe Python OptiX collect-k bounds behavior.")
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY_PATH)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    probe = validate_probe(run_probe(args.library))
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(probe, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(probe), encoding="utf-8")
    print(json.dumps({"status": probe["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
