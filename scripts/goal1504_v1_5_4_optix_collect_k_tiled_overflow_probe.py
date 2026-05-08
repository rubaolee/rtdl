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
from scripts.goal1503_v1_5_4_optix_collect_k_scaling_probe import _expected_native_path


REPORT_STEM = "goal1504_v1_5_4_optix_collect_k_tiled_overflow_probe_2026-05-08"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"
DEFAULT_LIBRARY_PATH = ROOT / "build" / "librtdl_optix.so"
DEFAULT_COUNTS = (4097, 65537, 131072)
OUTPUT_SENTINEL = -909090


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


def _make_rows(candidate_count: int) -> list[tuple[int, int]]:
    if candidate_count <= 0:
        raise ValueError("candidate_count must be positive")
    unique_mod = max(1, candidate_count // 2)
    return [((index * 37) % unique_mod, ((index * 37) % unique_mod) + 1_000) for index in range(candidate_count)]


def _unique_count(rows: list[tuple[int, int]]) -> int:
    return len(set(rows))


def _run_overflow_case(cuda: CudaDriver, *, candidate_count: int) -> dict[str, Any]:
    rows = _make_rows(candidate_count)
    unique_count = _unique_count(rows)
    capacity = unique_count - 1
    flat_rows = [cell for row in rows for cell in row]
    input_array_type = ctypes.c_int64 * len(flat_rows)
    input_array = input_array_type(*flat_rows)
    output_elements = max(1, capacity * 2)
    output_array_type = ctypes.c_int64 * output_elements
    sentinel_array = output_array_type(*([OUTPUT_SENTINEL] * output_elements))
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
            candidate_count=candidate_count,
            row_width=2,
            rows_out_device_ptr=output_ptr.value,
            row_capacity=capacity,
            allow_experimental=True,
        )
        cuda.d2h(output_array, output_ptr, ctypes.sizeof(output_array))
        output_flat = [int(value) for value in output_array]
        return {
            "candidate_count": candidate_count,
            "row_width": 2,
            "unique_count": unique_count,
            "capacity": capacity,
            "expected_native_path": _expected_native_path(candidate_count, 2),
            "valid_count": int(result["valid_count"]),
            "overflowed": bool(result["overflowed"]),
            "output_sentinel": OUTPUT_SENTINEL,
            "output_flat_sample": output_flat[: min(16, len(output_flat))],
            "fail_closed_output_preserved": all(value == OUTPUT_SENTINEL for value in output_flat),
            "same_valid_count": int(result["valid_count"]) == unique_count,
            "same_overflowed_flag": bool(result["overflowed"]) is True,
            "transfer_accounting": result["transfer_accounting"],
        }
    finally:
        if output_ptr.value:
            cuda.free(output_ptr)
        if candidate_ptr.value:
            cuda.free(candidate_ptr)


def run_probe(library_path: Path, counts: tuple[int, ...]) -> dict[str, Any]:
    os.environ["RTDL_OPTIX_LIB"] = str(library_path)
    cuda = CudaDriver()
    try:
        cases = [_run_overflow_case(cuda, candidate_count=count) for count in counts]
        return {
            "goal": "Goal1504",
            "status": "goal1504_optix_collect_k_tiled_overflow_probe_recorded",
            "git_commit": _git_head(),
            "platform": platform.platform(),
            "device_name": cuda.device_name(),
            "cuda_driver_version": cuda.driver_version(),
            "library_path": str(library_path),
            "measured_on_real_nvidia": True,
            "python_entry_point": "rtdsl.optix_runtime.collect_k_bounded_i64_device_optix",
            "native_symbol": optix_runtime.OPTIX_COLLECT_K_BOUNDED_I64_DEVICE_SYMBOL,
            "cases": cases,
            "all_fail_closed_passed": all(
                case["same_valid_count"] and case["same_overflowed_flag"] and case["fail_closed_output_preserved"]
                for case in cases
            ),
            "claim_flags": {
                "true_zero_copy_authorized": False,
                "public_speedup_wording_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "stable_public_primitive_authorized": False,
                "partner_tensor_handoff_authorized": False,
                "release_action_authorized": False,
            },
            "claim_boundary": (
                "Goal1504 records overflow/fail-closed behavior for the experimental Python "
                "OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize "
                "true zero-copy wording, public speedup wording, whole-app claims, partner "
                "tensor handoff, stable primitive promotion, or release action."
            ),
        }
    finally:
        cuda.close()


def validate_probe(probe: dict[str, Any]) -> dict[str, Any]:
    if probe.get("goal") != "Goal1504":
        raise ValueError("invalid Goal1504 report goal")
    if probe.get("measured_on_real_nvidia") is not True:
        raise ValueError("Goal1504 must be measured on real NVIDIA hardware")
    if probe.get("all_fail_closed_passed") is not True:
        raise ValueError("Goal1504 requires every overflow case to fail closed")
    cases = probe.get("cases", [])
    if not cases:
        raise ValueError("Goal1504 requires at least one overflow case")
    for case in cases:
        if case.get("row_width") != 2:
            raise ValueError("Goal1504 currently targets row_width=2 tiled path only")
        if case.get("capacity", 0) >= case.get("unique_count", 0):
            raise ValueError("Goal1504 overflow case capacity must be below unique_count")
        if case.get("valid_count") != case.get("unique_count"):
            raise ValueError("Goal1504 overflow case must report full unique valid_count")
        if case.get("overflowed") is not True:
            raise ValueError("Goal1504 overflow case must set overflowed=True")
        if case.get("fail_closed_output_preserved") is not True:
            raise ValueError("Goal1504 overflow case must preserve output buffer sentinel")
        transfer = case.get("transfer_accounting", {})
        if transfer.get("host_to_device_transfers_before_backend_execution") != 0:
            raise ValueError("Goal1504 device-pointer path must not report backend H2D content transfer")
    for flag, value in probe.get("claim_flags", {}).items():
        if value is not False:
            raise ValueError(f"Goal1504 must keep {flag}=False")
    return probe


def to_markdown(probe: dict[str, Any]) -> str:
    lines = [
        "# Goal 1504: OptiX COLLECT_K_BOUNDED Tiled Overflow Probe",
        "",
        "## Verdict",
        "",
        f"`{probe['status']}`",
        "",
        "## Scope",
        "",
        f"- Device: `{probe['device_name']}`",
        f"- Git commit: `{probe['git_commit']}`",
        f"- Python entry point: `{probe['python_entry_point']}`",
        f"- Native symbol: `{probe['native_symbol']}`",
        "",
        "## Cases",
        "",
    ]
    for case in probe["cases"]:
        lines.append(
            "- candidates=`{candidate_count}`, unique=`{unique_count}`, capacity=`{capacity}`, "
            "path=`{expected_native_path}`, valid_count=`{valid_count}`, overflowed=`{overflowed}`, "
            "fail_closed_output_preserved=`{fail_closed_output_preserved}`".format(**case)
        )
    lines.extend(["", "## Claim Boundary", "", probe["claim_boundary"], ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe OptiX collect-k tiled overflow fail-closed behavior.")
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY_PATH)
    parser.add_argument("--counts", nargs="+", type=int, default=list(DEFAULT_COUNTS))
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    probe = validate_probe(run_probe(args.library, tuple(args.counts)))
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(probe, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(probe), encoding="utf-8")
    print(json.dumps({"status": probe["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
