#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
API_PATH = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
CORE_PATH = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
PRELUDE_PATH = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
REPORT_STEM = "goal1496_v1_5_4_collect_k_device_pointer_stub_gate_2026-05-08"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_gate() -> dict[str, Any]:
    api = _read(API_PATH)
    core = _read(CORE_PATH)
    implementation_text = api + "\n" + core
    prelude = _read(PRELUDE_PATH)
    symbol = "rtdl_optix_collect_k_bounded_i64_device"
    signature_requirements = (
        "uint64_t candidate_rows_device_ptr",
        "uint64_t rows_out_device_ptr",
        "uint64_t* h2d_transfers_out",
        "uint64_t* d2h_transfers_out",
        "uint64_t* internal_device_transfers_out",
    )
    signature_present = symbol in prelude and all(required in prelude for required in signature_requirements)
    implementation_present = symbol in api and all(required in api for required in signature_requirements)
    implementation_markers = (
        "collect_k_bounded_i64",
        "collect_k_bounded_i64_row_width2_sort",
        "padded_count",
        "collect_k_compare_rows",
        "&row_width",
        "cuLaunchKernel",
        "download(emitted_count_out",
        "unique_count > row_capacity",
        "*overflowed_out = 1u",
        "*h2d_transfers_out = 0",
        "*d2h_transfers_out = 0",
        "*d2h_transfers_out += 2",
        "*internal_device_transfers_out = 0",
    )
    implementation_markers_present = all(marker in implementation_text for marker in implementation_markers)
    hidden_host_content_buffer_absent = "std::vector<std::vector<int64_t>> rows" not in api.split(symbol, 1)[1]
    return {
        "goal": "Goal1496",
        "status": "goal1496_collect_k_device_pointer_dynamic_row_width_guarded",
        "symbol": symbol,
        "api_path": str(API_PATH.relative_to(ROOT)),
        "prelude_path": str(PRELUDE_PATH.relative_to(ROOT)),
        "signature_present": signature_present,
        "implementation_present": implementation_present,
        "implementation_markers_present": implementation_markers_present,
        "hidden_host_content_buffer_absent": hidden_host_content_buffer_absent,
        "accepted_for_goal1493_device_buffer_execution": False,
        "native_symbol_implemented_for_dynamic_row_width": implementation_markers_present,
        "transfer_counters_initialized": implementation_markers_present,
        "claim_flags": {
            "true_zero_copy_authorized": False,
            "public_speedup_wording_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "stable_public_primitive_authorized": False,
            "partner_tensor_handoff_authorized": False,
            "release_action_authorized": False,
        },
        "claim_boundary": (
            "Goal1496 guards the OptiX COLLECT_K_BOUNDED "
            "device-pointer implementation shape. It is not accepted as Goal1493 "
            "device-buffer execution evidence until measured on an OptiX-ready "
            "NVIDIA pod and passed through Goal1493 intake. It does not prove "
            "true zero-copy and does not authorize public speedup wording, "
            "whole-app claims, partner tensor handoff, stable primitive promotion, "
            "or release action."
        ),
    }


def validate_gate(gate: dict[str, Any]) -> dict[str, Any]:
    if gate.get("goal") != "Goal1496":
        raise ValueError("invalid Goal1496 gate goal")
    if gate.get("symbol") != "rtdl_optix_collect_k_bounded_i64_device":
        raise ValueError("Goal1496 must reserve the device collect-k symbol")
    if gate.get("signature_present") is not True:
        raise ValueError("Goal1496 device-pointer signature is missing")
    if gate.get("implementation_present") is not True:
        raise ValueError("Goal1496 device-pointer implementation is missing")
    if gate.get("implementation_markers_present") is not True:
        raise ValueError("Goal1496 device-pointer implementation markers are missing")
    if gate.get("hidden_host_content_buffer_absent") is not True:
        raise ValueError("Goal1496 device-pointer implementation must not allocate hidden host content buffers")
    if gate.get("accepted_for_goal1493_device_buffer_execution") is not False:
        raise ValueError("Goal1496 implementation must not be accepted as Goal1493 device-buffer evidence")
    if gate.get("native_symbol_implemented_for_dynamic_row_width") is not True:
        raise ValueError("Goal1496 must identify the dynamic row_width native implementation")
    for flag, value in gate.get("claim_flags", {}).items():
        if value is not False:
            raise ValueError(f"Goal1496 must keep {flag}=False")
    for phrase in (
        "COLLECT_K_BOUNDED",
        "not accepted as Goal1493 device-buffer execution evidence",
        "measured on an OptiX-ready NVIDIA pod",
        "does not prove true zero-copy",
        "public speedup wording",
        "partner tensor handoff",
        "release action",
    ):
        if phrase not in gate.get("claim_boundary", ""):
            raise ValueError("Goal1496 claim boundary is incomplete")
    return gate


def to_markdown(gate: dict[str, Any]) -> str:
    lines = [
        "# Goal 1496: COLLECT_K_BOUNDED Device-Pointer Stub Gate",
        "",
        "## Verdict",
        "",
        "`goal1496_collect_k_device_pointer_dynamic_row_width_guarded`",
        "",
        "## Implementation Guard",
        "",
        f"- Symbol: `{gate['symbol']}`",
        f"- Signature present: `{gate['signature_present']}`",
        f"- Implementation present: `{gate['implementation_present']}`",
        f"- Implementation markers present: `{gate['implementation_markers_present']}`",
        f"- Hidden host content buffer absent: `{gate['hidden_host_content_buffer_absent']}`",
        f"- Accepted for Goal1493 device-buffer execution: `{gate['accepted_for_goal1493_device_buffer_execution']}`",
        "",
        "## Claim Boundary",
        "",
        gate["claim_boundary"],
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the Goal1496 device-pointer ABI stub gate.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    gate = validate_gate(build_gate())
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(gate), encoding="utf-8")
    print(json.dumps({"status": gate["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
