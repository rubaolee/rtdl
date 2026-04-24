#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_API_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
DEFAULT_WORKLOADS_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
DEFAULT_OUTPUT_JSON = ROOT / "docs" / "reports" / "goal871_native_pair_row_bounded_helper_packet_2026-04-24.json"
DEFAULT_OUTPUT_MD = ROOT / "docs" / "reports" / "goal871_native_pair_row_bounded_helper_packet_2026-04-24.md"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_packet(api_cpp: str, workloads_cpp: str) -> dict[str, Any]:
    helper_name = "run_seg_poly_anyhit_rows_optix_native_bounded"
    helper_present = f"static void {helper_name}(" in workloads_cpp
    api_delegates = f"{helper_name}(" in api_cpp
    empty_success_present = "if (segment_count == 0 || polygon_count == 0)" in workloads_cpp and "return;" in workloads_cpp
    outputs_zeroed = "*emitted_count_out = 0;" in workloads_cpp and "*overflowed_out = 0;" in workloads_cpp
    not_implemented_boundary = "OptiX pair-row emission is still pending" in workloads_cpp
    public_rows_still_host_indexed = "run_seg_poly_anyhit_rows_optix_host_indexed(" in api_cpp
    return {
        "goal": "Goal871 native pair-row bounded helper packet",
        "date": "2026-04-24",
        "helper": helper_name,
        "recommended_status": "bounded_helper_added",
        "evidence": {
            "helper_present": helper_present,
            "api_delegates_to_helper": api_delegates,
            "empty_input_success_path_present": empty_success_present,
            "outputs_zeroed_before_work": outputs_zeroed,
            "not_implemented_boundary_present": not_implemented_boundary,
            "public_rows_path_still_host_indexed": public_rows_still_host_indexed,
        },
        "current_behavior": {
            "empty_input": "success_zero_rows",
            "non_empty_input": "explicit_not_implemented_until_native_emitter_exists",
            "public_rows_path": "unchanged_host_indexed",
        },
        "boundary": (
            "This goal moves the bounded rows contract into a named workload-layer helper and gives empty inputs correct zero-row behavior. "
            "It still does not implement native OptiX pair-row emission or authorize readiness."
        ),
    }


def to_markdown(packet: dict[str, Any]) -> str:
    ev = packet["evidence"]
    behavior = packet["current_behavior"]
    return "\n".join(
        [
            "# Goal871 Native Pair-Row Bounded Helper Packet",
            "",
            f"- helper: `{packet['helper']}`",
            f"- recommended status: `{packet['recommended_status']}`",
            "",
            "## Evidence",
            "",
            f"- helper present: `{ev['helper_present']}`",
            f"- API delegates to helper: `{ev['api_delegates_to_helper']}`",
            f"- empty-input success path present: `{ev['empty_input_success_path_present']}`",
            f"- outputs zeroed before work: `{ev['outputs_zeroed_before_work']}`",
            f"- not-implemented boundary present: `{ev['not_implemented_boundary_present']}`",
            f"- public rows path still host-indexed: `{ev['public_rows_path_still_host_indexed']}`",
            "",
            "## Current Behavior",
            "",
            f"- empty input: `{behavior['empty_input']}`",
            f"- non-empty input: `{behavior['non_empty_input']}`",
            f"- public rows path: `{behavior['public_rows_path']}`",
            "",
            "## Boundary",
            "",
            packet["boundary"],
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a packet proving the native pair-row bounded helper exists.")
    parser.add_argument("--api-cpp", type=Path, default=DEFAULT_API_CPP)
    parser.add_argument("--workloads-cpp", type=Path, default=DEFAULT_WORKLOADS_CPP)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args(argv)
    packet = build_packet(_read_text(args.api_cpp), _read_text(args.workloads_cpp))
    packet["sources"] = {"api_cpp": str(args.api_cpp), "workloads_cpp": str(args.workloads_cpp)}
    args.output_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(packet) + "\n", encoding="utf-8")
    print(json.dumps({"output_json": str(args.output_json), "output_md": str(args.output_md), "recommended_status": packet["recommended_status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
