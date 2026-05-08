#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.goal1500_v1_5_4_optix_device_collect_k_measurement import CudaDriver, _cuda_check
from scripts.goal1503_v1_5_4_optix_collect_k_scaling_probe import _expected_native_path


REPORT_STEM = "goal1508_v1_5_4_optix_collect_k_tiled_preflight_2026-05-08"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"
DEFAULT_COUNTS = (4097, 65537, 131072)
CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK_OPTIN = 97
ROW_WIDTH2_TILE_SIZE = 4096
ROW_WIDTH2_TILE_SHARED_BYTES = ctypes.sizeof(ctypes.c_int64) * ROW_WIDTH2_TILE_SIZE * 2 + ROW_WIDTH2_TILE_SIZE


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


def _device_attribute(cuda: CudaDriver, attribute: int) -> int:
    cuda.cuda.cuDeviceGetAttribute.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int]
    cuda.cuda.cuDeviceGetAttribute.restype = ctypes.c_int
    value = ctypes.c_int()
    _cuda_check(
        cuda.cuda.cuDeviceGetAttribute(ctypes.byref(value), int(attribute), cuda.device.value),
        "cuDeviceGetAttribute",
    )
    return int(value.value)


def _case_for_count(candidate_count: int, max_optin_shared_bytes: int) -> dict[str, Any]:
    expected_path = _expected_native_path(candidate_count, 2)
    requires_tiled_shared_memory = expected_path in (
        "row_width2_parallel_bitonic_sort",
        "row_width2_bounded_multi_tile_sort_merge",
    )
    shared_memory_sufficient = (
        not requires_tiled_shared_memory
        or max_optin_shared_bytes >= ROW_WIDTH2_TILE_SHARED_BYTES
    )
    predicted_profile_native_path = expected_path if shared_memory_sufficient else "dynamic_row_width_single_thread_fallback"
    return {
        "candidate_count": candidate_count,
        "row_width": 2,
        "expected_native_path": expected_path,
        "required_shared_memory_bytes": ROW_WIDTH2_TILE_SHARED_BYTES if requires_tiled_shared_memory else 0,
        "max_optin_shared_memory_per_block_bytes": max_optin_shared_bytes,
        "shared_memory_sufficient_for_expected_path": shared_memory_sufficient,
        "predicted_profile_native_path": predicted_profile_native_path,
        "accepted_goal1506_profile_candidate": (
            expected_path == "row_width2_bounded_multi_tile_sort_merge"
            and predicted_profile_native_path == expected_path
        ),
    }


def run_preflight(counts: tuple[int, ...]) -> dict[str, Any]:
    cuda = CudaDriver()
    try:
        max_optin_shared_bytes = _device_attribute(
            cuda,
            CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK_OPTIN,
        )
        cases = [_case_for_count(count, max_optin_shared_bytes) for count in counts]
        return {
            "goal": "Goal1508",
            "status": "goal1508_optix_collect_k_tiled_preflight_recorded",
            "git_commit": _git_head(),
            "platform": platform.platform(),
            "device_name": cuda.device_name(),
            "cuda_driver_version": cuda.driver_version(),
            "cuda_attribute": {
                "name": "CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK_OPTIN",
                "value": CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK_OPTIN,
                "max_optin_shared_memory_per_block_bytes": max_optin_shared_bytes,
            },
            "row_width2_tile_shared_memory_bytes": ROW_WIDTH2_TILE_SHARED_BYTES,
            "cases": cases,
            "all_requested_counts_are_goal1506_profile_candidates": all(
                case["accepted_goal1506_profile_candidate"] for case in cases
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
                "Goal1508 is a CUDA shared-memory preflight for the experimental "
                "OptiX COLLECT_K_BOUNDED stage-profile path only. It does not "
                "authorize public speedup wording, true zero-copy wording, whole-app "
                "claims, partner tensor handoff, stable primitive promotion, or release action."
            ),
        }
    finally:
        cuda.close()


def validate_preflight(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("goal") != "Goal1508":
        raise ValueError("invalid Goal1508 preflight goal")
    if payload.get("row_width2_tile_shared_memory_bytes") != ROW_WIDTH2_TILE_SHARED_BYTES:
        raise ValueError("Goal1508 row_width2 tile shared-memory requirement drifted")
    cases = payload.get("cases", [])
    if not cases:
        raise ValueError("Goal1508 requires at least one preflight case")
    for case in cases:
        if case.get("row_width") != 2:
            raise ValueError("Goal1508 currently preflights row_width=2 only")
        sufficient = (
            int(case.get("max_optin_shared_memory_per_block_bytes", 0))
            >= int(case.get("required_shared_memory_bytes", 0))
        )
        if case.get("required_shared_memory_bytes", 0) and case.get("shared_memory_sufficient_for_expected_path") is not sufficient:
            raise ValueError("Goal1508 shared-memory sufficiency flag mismatch")
        expected_candidate = (
            case.get("expected_native_path") == "row_width2_bounded_multi_tile_sort_merge"
            and case.get("predicted_profile_native_path") == case.get("expected_native_path")
        )
        if case.get("accepted_goal1506_profile_candidate") is not expected_candidate:
            raise ValueError("Goal1508 accepted profile candidate flag mismatch")
    expected_all = all(case["accepted_goal1506_profile_candidate"] for case in cases)
    if payload.get("all_requested_counts_are_goal1506_profile_candidates") is not expected_all:
        raise ValueError("Goal1508 aggregate profile candidate flag mismatch")
    for flag, value in payload.get("claim_flags", {}).items():
        if value is not False:
            raise ValueError(f"Goal1508 must keep {flag}=False")
    return payload


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal 1508: OptiX COLLECT_K_BOUNDED Tiled Preflight",
        "",
        "## Verdict",
        "",
        f"`{payload['status']}`",
        "",
        "## Scope",
        "",
        f"- Device: `{payload['device_name']}`",
        f"- Git commit: `{payload['git_commit']}`",
        f"- Max opt-in shared memory per block: `{payload['cuda_attribute']['max_optin_shared_memory_per_block_bytes']}` bytes",
        f"- Row_width=2 tile shared-memory requirement: `{payload['row_width2_tile_shared_memory_bytes']}` bytes",
        f"- All requested counts are Goal1506 profile candidates: `{payload['all_requested_counts_are_goal1506_profile_candidates']}`",
        "",
        "## Cases",
        "",
    ]
    for case in payload["cases"]:
        lines.append(
            "- candidates=`{candidate_count}`, expected_path=`{expected_native_path}`, "
            "predicted_profile_native_path=`{predicted_profile_native_path}`, "
            "shared_memory_sufficient=`{shared_memory_sufficient_for_expected_path}`, "
            "accepted_goal1506_profile_candidate=`{accepted_goal1506_profile_candidate}`".format(**case)
        )
    lines.extend(["", "## Claim Boundary", "", payload["claim_boundary"], ""])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preflight OptiX collect-k tiled shared-memory support.")
    parser.add_argument("--counts", nargs="+", type=int, default=list(DEFAULT_COUNTS))
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = validate_preflight(run_preflight(tuple(args.counts)))
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
