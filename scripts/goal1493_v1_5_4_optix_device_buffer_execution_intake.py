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


REPORT_STEM = "goal1493_v1_5_4_optix_device_buffer_execution_intake_2026-05-08"
DEFAULT_PACKET_PATH = (
    ROOT / "docs" / "reports" / "goal1492_v1_5_4_collect_k_device_buffer_execution_packet_2026-05-08.json"
)
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"
GOAL1493_REQUIRED_DEVICE_SYMBOL = "rtdl_optix_collect_k_bounded_i64_device"
GOAL1493_LEGACY_HOST_SYMBOL = "rtdl_optix_collect_k_bounded_i64"


def _rows(value: Any) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(int(cell) for cell in row) for row in value)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_packet_basis(packet: dict[str, Any]) -> dict[str, Any]:
    if packet.get("goal") != "Goal1492":
        raise ValueError("Goal1493 intake must be based on the Goal1492 packet")
    if packet.get("first_target_primitive") != "COLLECT_K_BOUNDED":
        raise ValueError("Goal1493 intake must target COLLECT_K_BOUNDED")
    if packet.get("device_buffer_execution_required", {}).get("required_backend") != "optix":
        raise ValueError("Goal1493 intake requires the Goal1492 OptiX backend contract")
    if packet.get("ready_to_run_on_current_pod") is not False:
        raise ValueError("Goal1493 packet basis must preserve the current-pod blocked state")
    return packet


def pending_intake(packet: dict[str, Any]) -> dict[str, Any]:
    packet = validate_packet_basis(packet)
    return {
        "goal": "Goal1493",
        "status": "goal1493_pending_measured_optix_execution",
        "source_packet_goal": packet["goal"],
        "primitive": packet["first_target_primitive"],
        "required_backend": "optix",
        "required_symbol": GOAL1493_REQUIRED_DEVICE_SYMBOL,
        "legacy_packet_symbol_rejected_for_device_execution": packet["device_buffer_execution_required"]["required_symbol"],
        "expected_reference": packet["expected_reference"],
        "blocked_by": packet["blocked_by"],
        "acceptance_requirements": (
            "measured_on_real_nvidia_true",
            "goal1489_preflight_green",
            "same_candidate_rows",
            "same_valid_count",
            "same_overflowed_flag",
            "transfer_accounting_present",
            "claim_flags_false_until_external_review",
        ),
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "partner_tensor_handoff_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "Goal1493 is an intake validator for a future measured OptiX "
            "device-buffer execution result. Pending intake does not run OptiX, "
            "does not prove true zero-copy, and does not authorize public speedup "
            "wording, whole-app claims, partner tensor handoff, or release action."
        ),
    }


def validate_execution_intake(packet: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
    packet = validate_packet_basis(packet)
    expected = packet["expected_reference"]
    required = packet["device_buffer_execution_required"]

    if execution.get("goal") != "Goal1493":
        raise ValueError("Goal1493 execution evidence must identify goal=Goal1493")
    if execution.get("source_packet_goal") != "Goal1492":
        raise ValueError("Goal1493 execution evidence must reference Goal1492")
    if execution.get("primitive") != "COLLECT_K_BOUNDED":
        raise ValueError("Goal1493 execution evidence must target COLLECT_K_BOUNDED")
    if execution.get("backend") != "optix":
        raise ValueError("Goal1493 execution evidence must use backend=optix")
    if required["required_symbol"] != GOAL1493_LEGACY_HOST_SYMBOL:
        raise ValueError("Goal1493 packet basis no longer matches the expected legacy host symbol")
    if execution.get("native_symbol") == GOAL1493_LEGACY_HOST_SYMBOL:
        raise ValueError("Goal1493 execution evidence must not use the legacy host-pointer symbol")
    if execution.get("native_symbol") != GOAL1493_REQUIRED_DEVICE_SYMBOL:
        raise ValueError("Goal1493 execution evidence used the wrong device native symbol")
    if execution.get("measured_on_real_nvidia") is not True:
        raise ValueError("Goal1493 execution evidence must be measured on real NVIDIA hardware")
    if execution.get("goal1489_preflight_green") is not True:
        raise ValueError("Goal1493 execution evidence requires green Goal1489 preflight")
    if execution.get("row_width") != packet["row_width"]:
        raise ValueError("Goal1493 execution evidence row_width mismatch")
    if execution.get("capacity") != packet["capacity"]:
        raise ValueError("Goal1493 execution evidence capacity mismatch")
    if _rows(execution.get("candidate_rows", ())) != _rows(packet["candidate_rows"]):
        raise ValueError("Goal1493 execution evidence candidate input mismatch")

    result = execution.get("result", {})
    if result.get("valid_count") != expected["valid_count"]:
        raise ValueError("Goal1493 execution evidence valid_count parity failed")
    if result.get("overflowed") != expected["overflowed"]:
        raise ValueError("Goal1493 execution evidence overflow parity failed")
    if _rows(result.get("candidate_id_rows", ())) != _rows(expected["candidate_id_rows"]):
        raise ValueError("Goal1493 execution evidence candidate row parity failed")

    parity = execution.get("parity", {})
    for key in ("same_candidate_rows", "same_valid_count", "same_overflowed_flag"):
        if parity.get(key) is not True:
            raise ValueError(f"Goal1493 execution evidence parity missing {key}=True")

    transfer = execution.get("transfer_accounting", {})
    for key in (
        "host_to_device_transfers_before_backend_execution",
        "device_to_host_transfers_after_backend_execution",
        "internal_device_transfers_if_any",
    ):
        if not isinstance(transfer.get(key), int) or transfer[key] < 0:
            raise ValueError(f"Goal1493 execution evidence transfer accounting missing nonnegative {key}")
    if transfer.get("allocation_only_transfers_distinguished_from_content_transfers") is not True:
        raise ValueError("Goal1493 execution evidence must distinguish allocation from content transfers")

    for flag in (
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "partner_tensor_handoff_authorized",
        "release_action_authorized",
    ):
        if execution.get(flag) is not False:
            raise ValueError(f"Goal1493 execution evidence must keep {flag}=False")

    accepted = dict(execution)
    accepted["status"] = "goal1493_measured_optix_execution_intake_accepted"
    accepted["claim_boundary"] = (
        "Goal1493 accepts measured OptiX device-buffer execution parity and "
        "transfer-accounting evidence only. It still does not authorize true "
        "zero-copy wording, public speedup wording, whole-app claims, partner "
        "tensor handoff, stable primitive promotion, or release action."
    )
    return accepted


def to_markdown(intake: dict[str, Any]) -> str:
    lines = [
        "# Goal 1493: OptiX Device-Buffer Execution Intake",
        "",
        "## Verdict",
        "",
        f"`{intake['status']}`",
        "",
        "## Scope",
        "",
        f"- Primitive: `{intake['primitive']}`",
        f"- Backend: `{intake.get('backend', intake.get('required_backend'))}`",
        f"- Symbol: `{intake.get('native_symbol', intake.get('required_symbol'))}`",
        "",
        "## Claim Boundary",
        "",
        intake["claim_boundary"],
        "",
    ]
    if intake["status"] == "goal1493_pending_measured_optix_execution":
        lines.extend(
            [
                "## Blocked By",
                "",
                *[f"- `{blocker}`" for blocker in intake["blocked_by"]],
                "",
            ]
        )
    else:
        transfer = intake["transfer_accounting"]
        lines.extend(
            [
                "## Accepted Evidence",
                "",
                f"- Valid count parity: `{intake['parity']['same_valid_count']}`",
                f"- Overflow parity: `{intake['parity']['same_overflowed_flag']}`",
                f"- Candidate row parity: `{intake['parity']['same_candidate_rows']}`",
                f"- H2D transfers before backend execution: `{transfer['host_to_device_transfers_before_backend_execution']}`",
                f"- D2H transfers after backend execution: `{transfer['device_to_host_transfers_after_backend_execution']}`",
                "",
            ]
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate future Goal1493 OptiX device-buffer execution evidence.")
    parser.add_argument("--packet-json", type=Path, default=DEFAULT_PACKET_PATH)
    parser.add_argument("--execution-json", type=Path)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packet = load_json(args.packet_json)
    if args.execution_json:
        intake = validate_execution_intake(packet, load_json(args.execution_json))
    else:
        intake = pending_intake(packet)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(intake, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(intake), encoding="utf-8")
    print(json.dumps({"status": intake["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
