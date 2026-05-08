#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from rtdsl import optix_runtime
from scripts.goal1500_v1_5_4_optix_device_collect_k_measurement import CudaDriver


REPORT_STEM = "goal1503_v1_5_4_optix_collect_k_scaling_probe_2026-05-08"
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


def _make_rows(candidate_count: int, row_width: int) -> list[tuple[int, ...]]:
    if candidate_count <= 0:
        raise ValueError("candidate_count must be positive")
    rows: list[tuple[int, ...]] = []
    unique_mod = max(1, candidate_count // 2)
    for index in range(candidate_count):
        key = (index * 37) % unique_mod
        rows.append(tuple(key + column * 1_000 for column in range(row_width)))
    return rows


def _expected_rows(rows: list[tuple[int, ...]]) -> list[list[int]]:
    return [list(row) for row in sorted(set(rows))]


def _rows_from_flat(values: ctypes.Array, row_width: int, row_count: int) -> list[list[int]]:
    return [
        [int(values[row_index * row_width + column]) for column in range(row_width)]
        for row_index in range(row_count)
    ]


def _run_case(
    cuda: CudaDriver,
    *,
    candidate_count: int,
    row_width: int,
    repeats: int,
) -> dict[str, Any]:
    rows = _make_rows(candidate_count, row_width)
    expected = _expected_rows(rows)
    capacity = len(expected)
    flat_rows = [int(cell) for row in rows for cell in row]
    input_array_type = ctypes.c_int64 * len(flat_rows)
    input_array = input_array_type(*flat_rows)
    output_array_type = ctypes.c_int64 * max(1, capacity * row_width)
    output_array = output_array_type()

    candidate_ptr = ctypes.c_ulonglong()
    output_ptr = ctypes.c_ulonglong()
    try:
        candidate_ptr = cuda.alloc(ctypes.sizeof(input_array))
        output_ptr = cuda.alloc(ctypes.sizeof(output_array))
        cuda.h2d(candidate_ptr, input_array, ctypes.sizeof(input_array))

        warmup = optix_runtime.collect_k_bounded_i64_device_optix(
            candidate_rows_device_ptr=candidate_ptr.value,
            candidate_count=candidate_count,
            row_width=row_width,
            rows_out_device_ptr=output_ptr.value,
            row_capacity=capacity,
            allow_experimental=True,
        )
        if int(warmup["valid_count"]) != capacity or bool(warmup["overflowed"]):
            raise RuntimeError("warmup collect-k parity failed before timing")

        elapsed_ms: list[float] = []
        last_result: dict[str, Any] | None = None
        for _ in range(repeats):
            start = time.perf_counter()
            last_result = optix_runtime.collect_k_bounded_i64_device_optix(
                candidate_rows_device_ptr=candidate_ptr.value,
                candidate_count=candidate_count,
                row_width=row_width,
                rows_out_device_ptr=output_ptr.value,
                row_capacity=capacity,
                allow_experimental=True,
            )
            elapsed_ms.append((time.perf_counter() - start) * 1000.0)

        cuda.d2h(output_array, output_ptr, ctypes.sizeof(output_array))
        actual = _rows_from_flat(output_array, row_width, capacity)
        if last_result is None:
            raise RuntimeError("timing loop did not execute")
        return {
            "candidate_count": candidate_count,
            "row_width": row_width,
            "unique_count": capacity,
            "expected_native_path": _expected_native_path(candidate_count, row_width),
            "repeats": repeats,
            "median_ms": statistics.median(elapsed_ms),
            "min_ms": min(elapsed_ms),
            "max_ms": max(elapsed_ms),
            "all_ms": elapsed_ms,
            "same_candidate_rows": actual == expected,
            "same_valid_count": int(last_result["valid_count"]) == capacity,
            "same_overflowed_flag": bool(last_result["overflowed"]) is False,
            "transfer_accounting": last_result["transfer_accounting"],
        }
    finally:
        if output_ptr.value:
            cuda.free(output_ptr)
        if candidate_ptr.value:
            cuda.free(candidate_ptr)


def run_probe(library_path: Path, repeats: int, counts: tuple[int, ...]) -> dict[str, Any]:
    os.environ["RTDL_OPTIX_LIB"] = str(library_path)
    cuda = CudaDriver()
    try:
        cases = [
            _run_case(cuda, candidate_count=count, row_width=2, repeats=repeats)
            for count in counts
        ]
        return {
            "goal": "Goal1503",
            "status": "goal1503_optix_collect_k_scaling_probe_recorded",
            "git_commit": _git_head(),
            "platform": platform.platform(),
            "device_name": cuda.device_name(),
            "cuda_driver_version": cuda.driver_version(),
            "library_path": str(library_path),
            "measured_on_real_nvidia": True,
            "python_entry_point": "rtdsl.optix_runtime.collect_k_bounded_i64_device_optix",
            "native_symbol": optix_runtime.OPTIX_COLLECT_K_BOUNDED_I64_DEVICE_SYMBOL,
            "algorithm_classification": (
                "row_width2_parallel_bitonic_sort_with_bounded_multi_tile_merge_and_dynamic_row_width_o_n2_fallback"
            ),
            "timing_scope": (
                "Python wrapper call around native OptiX/CUDA device-pointer execution, "
                "including launch and metadata copy overhead, excluding input setup H2D "
                "and output verification D2H."
            ),
            "cases": cases,
            "all_parity_passed": all(
                case["same_candidate_rows"] and case["same_valid_count"] and case["same_overflowed_flag"]
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
                "Goal1503 records scaling observations for the experimental Python OptiX "
                "COLLECT_K_BOUNDED device-pointer bridge only. It is not a speedup claim, "
                "does not prove true zero-copy, and does not authorize whole-app claims, "
                "partner tensor handoff, stable primitive promotion, or release action."
            ),
        }
    finally:
        cuda.close()


def validate_probe(probe: dict[str, Any]) -> dict[str, Any]:
    if probe.get("goal") != "Goal1503":
        raise ValueError("invalid Goal1503 report goal")
    if probe.get("measured_on_real_nvidia") is not True:
        raise ValueError("Goal1503 must be measured on real NVIDIA hardware")
    if probe.get("all_parity_passed") is not True:
        raise ValueError("Goal1503 requires parity for every timing case")
    for case in probe.get("cases", []):
        if case.get("candidate_count", 0) <= 0:
            raise ValueError("Goal1503 case candidate_count must be positive")
        if case.get("median_ms", 0.0) <= 0.0:
            raise ValueError("Goal1503 case median_ms must be positive")
    for flag, value in probe.get("claim_flags", {}).items():
        if value is not False:
            raise ValueError(f"Goal1503 must keep {flag}=False")
    return probe


def _expected_native_path(candidate_count: int, row_width: int) -> str:
    if row_width == 2 and candidate_count <= 4096:
        return "row_width2_parallel_bitonic_sort"
    if row_width == 2 and candidate_count <= 65536:
        return "row_width2_bounded_multi_tile_sort_merge"
    return "dynamic_row_width_single_thread_fallback"


def to_markdown(probe: dict[str, Any]) -> str:
    lines = [
        "# Goal 1503: OptiX COLLECT_K_BOUNDED Scaling Probe",
        "",
        "## Verdict",
        "",
        f"`{probe['status']}`",
        "",
        "## Scope",
        "",
        f"- Device: `{probe['device_name']}`",
        f"- Git commit: `{probe['git_commit']}`",
        f"- Algorithm classification: `{probe['algorithm_classification']}`",
        f"- Timing scope: {probe['timing_scope']}",
        "",
        "## Cases",
        "",
    ]
    for case in probe["cases"]:
        lines.append(
            f"- candidates=`{case['candidate_count']}`, unique=`{case['unique_count']}`, "
            f"row_width=`{case['row_width']}`, path=`{case['expected_native_path']}`, "
            f"median_ms=`{case['median_ms']:.6f}`, "
            f"parity=`{case['same_candidate_rows'] and case['same_valid_count'] and case['same_overflowed_flag']}`"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            probe["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record OptiX collect-k scaling observations.")
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY_PATH)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument(
        "--counts",
        nargs="+",
        type=int,
        default=[
            8,
            32,
            128,
            512,
            1024,
            1025,
            2048,
            2049,
            4096,
            4097,
            8192,
            8193,
            16384,
            16385,
            32768,
            32769,
            65536,
        ],
    )
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.repeats <= 0:
        raise ValueError("repeats must be positive")
    if any(count <= 0 for count in args.counts):
        raise ValueError("counts must all be positive")
    probe = validate_probe(run_probe(args.library, args.repeats, tuple(args.counts)))
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(probe, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(probe), encoding="utf-8")
    print(json.dumps({"status": probe["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
