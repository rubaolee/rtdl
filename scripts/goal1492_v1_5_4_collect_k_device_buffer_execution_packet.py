#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


REPORT_STEM = "goal1492_v1_5_4_collect_k_device_buffer_execution_packet_2026-05-08"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


def candidate_rows() -> tuple[tuple[int, int], ...]:
    return (
        (2, 20),
        (1, 10),
        (2, 20),
        (3, 30),
    )


def build_packet(*, capacity: int = 3) -> dict[str, Any]:
    expected = rt.collect_k_bounded_rows(candidate_rows(), k=capacity, row_width=2)
    expected = rt.validate_collect_k_bounded_result(expected, row_width=2)
    return {
        "goal": "Goal1492",
        "scope": "v1.5.4 COLLECT_K_BOUNDED RTDL-owned device-buffer execution packet",
        "first_target_primitive": "COLLECT_K_BOUNDED",
        "native_symbols": {
            "embree_reference": "rtdl_embree_collect_k_bounded_i64",
            "optix_target": "rtdl_optix_collect_k_bounded_i64",
        },
        "candidate_rows": candidate_rows(),
        "row_width": 2,
        "capacity": capacity,
        "expected_reference": {
            "backend": expected.get("backend", "python_reference"),
            "valid_count": expected["valid_count"],
            "overflowed": expected["overflowed"],
            "candidate_id_rows": expected["candidate_id_rows"],
            "ordering_policy": expected["ordering_policy"],
            "overflow_policy": expected["overflow_policy"],
            "failure_mode": expected["failure_mode"],
        },
        "device_buffer_execution_required": {
            "input_descriptor": "rtdl_owned_device_resident_i64_candidate_rows",
            "output_descriptor": "bounded_rtdl_owned_result_buffer",
            "required_backend": "optix",
            "required_symbol": "rtdl_optix_collect_k_bounded_i64",
            "must_run_on_real_nvidia": True,
            "must_pass_goal1489_preflight": True,
        },
        "required_parity": (
            "same_valid_count",
            "same_overflowed_flag",
            "same_candidate_id_rows",
            "same_fail_closed_overflow_behavior",
        ),
        "required_transfer_accounting": {
            "host_to_device_transfers_before_backend_execution": "must_be_recorded",
            "device_to_host_transfers_after_backend_execution": "must_be_recorded",
            "internal_device_transfers_if_any": "must_be_recorded",
            "allocation_only_transfers_distinguished_from_content_transfers": True,
        },
        "result_placeholders": {
            "optix_device_buffer_result_json": None,
            "same_contract_parity_json": None,
            "transfer_accounting_summary": None,
        },
        "ready_to_run_on_current_pod": False,
        "blocked_by": (
            "goal1489_current_pod_missing_optix_headers",
            "goal1489_current_pod_missing_librtdl_optix",
        ),
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "partner_tensor_handoff_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "Goal1492 prepares a replayable COLLECT_K_BOUNDED device-buffer "
            "execution packet only. It does not run OptiX, does not prove "
            "true zero-copy, and does not authorize public speedup wording, "
            "whole-app claims, partner tensor handoff, or release action."
        ),
    }


def validate_packet(packet: dict[str, Any]) -> dict[str, Any]:
    if packet.get("goal") != "Goal1492":
        raise ValueError("invalid Goal1492 packet goal")
    if packet.get("first_target_primitive") != "COLLECT_K_BOUNDED":
        raise ValueError("Goal1492 must target COLLECT_K_BOUNDED")
    expected = packet.get("expected_reference", {})
    if expected.get("valid_count") != 3:
        raise ValueError("Goal1492 expected valid_count must be 3")
    if expected.get("overflowed") is not False:
        raise ValueError("Goal1492 expected result must not overflow")
    if tuple(tuple(row) for row in expected.get("candidate_id_rows", ())) != ((1, 10), (2, 20), (3, 30)):
        raise ValueError("Goal1492 expected candidate rows mismatch")
    if packet.get("ready_to_run_on_current_pod") is not False:
        raise ValueError("Goal1492 must remain blocked on the current pod")
    for flag in (
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "partner_tensor_handoff_authorized",
        "release_action_authorized",
    ):
        if packet.get(flag) is not False:
            raise ValueError(f"Goal1492 packet must keep {flag}=False")
    for phrase in (
        "device-buffer execution packet only",
        "does not run OptiX",
        "does not prove true zero-copy",
        "public speedup wording",
        "partner tensor handoff",
        "release action",
    ):
        if phrase not in packet.get("claim_boundary", ""):
            raise ValueError("Goal1492 packet claim boundary is incomplete")
    return packet


def to_markdown(packet: dict[str, Any]) -> str:
    expected = packet["expected_reference"]
    lines = [
        "# Goal 1492: COLLECT_K_BOUNDED Device-Buffer Execution Packet",
        "",
        "## Verdict",
        "",
        "Prepared as a replayable packet. It is blocked on the current pod until Goal 1489 preflight is green.",
        "",
        "## Fixture",
        "",
        f"- Candidate rows: `{packet['candidate_rows']}`",
        f"- Row width: `{packet['row_width']}`",
        f"- Capacity: `{packet['capacity']}`",
        "",
        "## Expected Reference",
        "",
        f"- Valid count: `{expected['valid_count']}`",
        f"- Overflowed: `{expected['overflowed']}`",
        f"- Candidate rows: `{expected['candidate_id_rows']}`",
        "",
        "## Required Device-Buffer Execution",
        "",
        f"- Backend: `{packet['device_buffer_execution_required']['required_backend']}`",
        f"- Symbol: `{packet['device_buffer_execution_required']['required_symbol']}`",
        "- Must run on real NVIDIA hardware after Goal 1489 preflight is green.",
        "",
        "## Claim Boundary",
        "",
        packet["claim_boundary"],
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Goal1492 COLLECT_K_BOUNDED device-buffer packet.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packet = validate_packet(build_packet())
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(packet), encoding="utf-8")
    print(json.dumps({"ready_to_run_on_current_pod": packet["ready_to_run_on_current_pod"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
