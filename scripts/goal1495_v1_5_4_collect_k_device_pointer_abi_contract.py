#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_STEM = "goal1495_v1_5_4_collect_k_device_pointer_abi_contract_2026-05-08"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


def build_contract() -> dict[str, Any]:
    return {
        "goal": "Goal1495",
        "status": "goal1495_collect_k_device_pointer_abi_contract_defined",
        "track": "python_rtdl",
        "primitive": "COLLECT_K_BOUNDED",
        "current_host_symbol": "rtdl_optix_collect_k_bounded_i64",
        "proposed_device_symbol": "rtdl_optix_collect_k_bounded_i64_device",
        "proposed_c_abi": (
            "int rtdl_optix_collect_k_bounded_i64_device("
            "uint64_t candidate_rows_device_ptr, size_t candidate_count, "
            "size_t row_width, uint64_t rows_out_device_ptr, size_t row_capacity, "
            "size_t* emitted_count_out, uint32_t* overflowed_out, "
            "uint64_t* h2d_transfers_out, uint64_t* d2h_transfers_out, "
            "uint64_t* internal_device_transfers_out, "
            "char* error_out, size_t error_size)"
        ),
        "pointer_semantics": {
            "candidate_rows_device_ptr": "CUDA device pointer to contiguous int64 candidate rows",
            "rows_out_device_ptr": "CUDA device pointer to bounded contiguous int64 output rows",
            "row_width": "positive explicit int64 cell count per row",
            "row_capacity": "bounded row capacity, not cell capacity",
            "emitted_count_out": "host pointer metadata output",
            "overflowed_out": "host pointer fail-closed overflow flag",
        },
        "required_runtime_behavior": (
            "validate_nonzero_device_pointers_when_counts_are_nonzero",
            "fail_closed_on_output_overflow_before_partial_success_claim",
            "preserve_goal1492_deduplicated_lexicographic_reference_rows",
            "record_transfer_accounting_even_when_zero",
            "do_not_allocate_hidden_host_content_buffers_for_candidate_rows",
        ),
        "required_transfer_accounting": {
            "host_to_device_transfers_before_backend_execution": "counter_output_required",
            "device_to_host_transfers_after_backend_execution": "counter_output_required",
            "internal_device_transfers_if_any": "counter_output_required",
            "allocation_only_transfers_distinguished_from_content_transfers": True,
        },
        "minimum_acceptance_tests": (
            "goal1492_fixture_same_rows_no_overflow",
            "goal1492_fixture_capacity_two_overflow_fail_closed",
            "wrong_row_width_rejected",
            "null_device_input_rejected_when_candidate_count_nonzero",
            "null_device_output_rejected_when_row_capacity_nonzero",
            "goal1493_intake_accepts_measured_result_only_after_green_preflight",
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
            "Goal1495 defines a proposed device-pointer ABI contract for future "
            "OptiX COLLECT_K_BOUNDED work. It does not implement the native "
            "symbol, does not run OptiX, does not prove true zero-copy, and does "
            "not authorize public speedup wording, whole-app claims, partner "
            "tensor handoff, stable primitive promotion, or release action."
        ),
    }


def validate_contract(contract: dict[str, Any]) -> dict[str, Any]:
    if contract.get("goal") != "Goal1495":
        raise ValueError("invalid Goal1495 contract goal")
    if contract.get("track") != "python_rtdl":
        raise ValueError("Goal1495 must stay on Python+RTDL track")
    if contract.get("primitive") != "COLLECT_K_BOUNDED":
        raise ValueError("Goal1495 must target COLLECT_K_BOUNDED")
    if contract.get("current_host_symbol") == contract.get("proposed_device_symbol"):
        raise ValueError("Goal1495 device ABI must not reuse the host-pointer symbol name")
    proposed = contract.get("proposed_c_abi", "")
    for required in (
        "uint64_t candidate_rows_device_ptr",
        "uint64_t rows_out_device_ptr",
        "uint64_t* h2d_transfers_out",
        "uint64_t* d2h_transfers_out",
        "uint64_t* internal_device_transfers_out",
    ):
        if required not in proposed:
            raise ValueError("Goal1495 proposed ABI is missing required device-pointer or accounting fields")
    for behavior in (
        "preserve_goal1492_deduplicated_lexicographic_reference_rows",
        "record_transfer_accounting_even_when_zero",
        "do_not_allocate_hidden_host_content_buffers_for_candidate_rows",
    ):
        if behavior not in contract.get("required_runtime_behavior", ()):
            raise ValueError("Goal1495 runtime behavior contract is incomplete")
    for test_name in (
        "goal1492_fixture_same_rows_no_overflow",
        "goal1492_fixture_capacity_two_overflow_fail_closed",
        "goal1493_intake_accepts_measured_result_only_after_green_preflight",
    ):
        if test_name not in contract.get("minimum_acceptance_tests", ()):
            raise ValueError("Goal1495 minimum acceptance tests are incomplete")
    for flag, value in contract.get("claim_flags", {}).items():
        if value is not False:
            raise ValueError(f"Goal1495 must keep {flag}=False")
    for phrase in (
        "device-pointer ABI contract",
        "does not implement the native symbol",
        "does not run OptiX",
        "does not prove true zero-copy",
        "public speedup wording",
        "partner tensor handoff",
        "release action",
    ):
        if phrase not in contract.get("claim_boundary", ""):
            raise ValueError("Goal1495 claim boundary is incomplete")
    return contract


def to_markdown(contract: dict[str, Any]) -> str:
    lines = [
        "# Goal 1495: COLLECT_K_BOUNDED Device-Pointer ABI Contract",
        "",
        "## Verdict",
        "",
        "`goal1495_collect_k_device_pointer_abi_contract_defined`",
        "",
        "## Proposed ABI",
        "",
        "```c",
        contract["proposed_c_abi"],
        "```",
        "",
        "## Required Behavior",
        "",
        *[f"- `{behavior}`" for behavior in contract["required_runtime_behavior"]],
        "",
        "## Minimum Acceptance Tests",
        "",
        *[f"- `{test}`" for test in contract["minimum_acceptance_tests"]],
        "",
        "## Claim Boundary",
        "",
        contract["claim_boundary"],
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Define Goal1495 collect_k device-pointer ABI contract.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract = validate_contract(build_contract())
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(contract), encoding="utf-8")
    print(json.dumps({"status": contract["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
