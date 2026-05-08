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

from rtdsl import optix_runtime


REPORT_STEM = "goal1497_v1_5_4_optix_device_pointer_runtime_refusal_2026-05-08"
DEFAULT_JSON_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.json"
DEFAULT_MD_PATH = ROOT / "docs" / "reports" / f"{REPORT_STEM}.md"


def build_report() -> dict[str, Any]:
    refused = False
    refusal = ""
    try:
        optix_runtime.collect_k_bounded_i64_device_optix(
            candidate_rows_device_ptr=1,
            candidate_count=1,
            row_width=2,
            rows_out_device_ptr=2,
            row_capacity=1,
        )
    except RuntimeError as exc:
        refused = True
        refusal = str(exc)
    return {
        "goal": "Goal1497",
        "status": "goal1497_optix_device_pointer_runtime_refuses_unimplemented_execution",
        "device_symbol": optix_runtime.OPTIX_COLLECT_K_BOUNDED_I64_DEVICE_SYMBOL,
        "host_symbol": optix_runtime.OPTIX_COLLECT_K_BOUNDED_I64_HOST_SYMBOL,
        "runtime_refused_execution": refused,
        "runtime_refusal_message": refusal,
        "accepted_for_goal1493_device_buffer_execution": False,
        "claim_flags": {
            "true_zero_copy_authorized": False,
            "public_speedup_wording_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "stable_public_primitive_authorized": False,
            "partner_tensor_handoff_authorized": False,
            "release_action_authorized": False,
        },
        "claim_boundary": (
            "Goal1497 wires Python runtime awareness of the reserved OptiX "
            "COLLECT_K_BOUNDED device-pointer symbol, but refuses execution "
            "until a measured native implementation exists. It does not run "
            "OptiX, does not prove true zero-copy, and does not authorize public "
            "speedup wording, whole-app claims, partner tensor handoff, stable "
            "primitive promotion, or release action."
        ),
    }


def validate_report(report: dict[str, Any]) -> dict[str, Any]:
    if report.get("goal") != "Goal1497":
        raise ValueError("invalid Goal1497 report goal")
    if report.get("device_symbol") != "rtdl_optix_collect_k_bounded_i64_device":
        raise ValueError("Goal1497 must name the reserved device symbol")
    if report.get("host_symbol") != "rtdl_optix_collect_k_bounded_i64":
        raise ValueError("Goal1497 must preserve the current host symbol name")
    if report.get("runtime_refused_execution") is not True:
        raise ValueError("Goal1497 runtime must refuse unimplemented device execution")
    if "reserved but not implemented" not in report.get("runtime_refusal_message", ""):
        raise ValueError("Goal1497 refusal message must identify reserved unimplemented status")
    if report.get("accepted_for_goal1493_device_buffer_execution") is not False:
        raise ValueError("Goal1497 must not be accepted as Goal1493 evidence")
    for flag, value in report.get("claim_flags", {}).items():
        if value is not False:
            raise ValueError(f"Goal1497 must keep {flag}=False")
    for phrase in (
        "runtime awareness",
        "refuses execution",
        "does not run OptiX",
        "does not prove true zero-copy",
        "public speedup wording",
        "partner tensor handoff",
        "release action",
    ):
        if phrase not in report.get("claim_boundary", ""):
            raise ValueError("Goal1497 claim boundary is incomplete")
    return report


def to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Goal 1497: OptiX Device-Pointer Runtime Refusal",
        "",
        "## Verdict",
        "",
        "`goal1497_optix_device_pointer_runtime_refuses_unimplemented_execution`",
        "",
        "## Runtime Surface",
        "",
        f"- Device symbol: `{report['device_symbol']}`",
        f"- Host symbol: `{report['host_symbol']}`",
        f"- Runtime refused execution: `{report['runtime_refused_execution']}`",
        f"- Accepted for Goal1493 evidence: `{report['accepted_for_goal1493_device_buffer_execution']}`",
        "",
        "## Claim Boundary",
        "",
        report["claim_boundary"],
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record Goal1497 OptiX device-pointer runtime refusal.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = validate_report(build_report())
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(to_markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
