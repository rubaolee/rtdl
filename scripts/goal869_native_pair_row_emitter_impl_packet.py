#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKLOADS_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
DEFAULT_API_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
DEFAULT_PRELUDE_H = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
DEFAULT_OUTPUT_JSON = ROOT / "docs" / "reports" / "goal869_native_pair_row_emitter_impl_packet_2026-04-23.json"
DEFAULT_OUTPUT_MD = ROOT / "docs" / "reports" / "goal869_native_pair_row_emitter_impl_packet_2026-04-23.md"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_packet(workloads_cpp: str, api_cpp: str, prelude_h: str) -> dict[str, Any]:
    has_native_hitcount_pipeline = "kSegPolyHitcountKernelSrc" in workloads_cpp and "__raygen__segpoly_probe" in workloads_cpp
    has_fixed_size_hitcount_output = "GpuSegPolyRecord* output;" in workloads_cpp and "sizeof(GpuSegPolyRecord) * segment_count" in workloads_cpp
    has_public_rows_abi = "rtdl_optix_run_segment_polygon_anyhit_rows(" in api_cpp and "rtdl_optix_run_segment_polygon_anyhit_rows(" in prelude_h
    rows_abi_calls_host_indexed = "run_seg_poly_anyhit_rows_optix_host_indexed(" in api_cpp
    has_native_rows_impl = "run_seg_poly_anyhit_rows_optix_native(" in workloads_cpp

    return {
        "goal": "Goal869 native pair-row emitter implementation packet",
        "date": "2026-04-23",
        "app": "segment_polygon_anyhit_rows",
        "mode": "rows",
        "recommended_status": "implementation_packet_ready",
        "current_blocker": "variable_length_native_pair_output_missing",
        "source_evidence": {
            "native_hitcount_pipeline_present": has_native_hitcount_pipeline,
            "fixed_size_hitcount_output_present": has_fixed_size_hitcount_output,
            "public_rows_abi_present": has_public_rows_abi,
            "rows_abi_calls_host_indexed": rows_abi_calls_host_indexed,
            "native_rows_impl_present": has_native_rows_impl,
        },
        "current_truth": {
            "native_hitcount_foundation": "present" if has_native_hitcount_pipeline else "missing",
            "rows_output_shape": "variable_length_pair_rows",
            "existing_native_output_shape": "fixed_one_row_per_segment" if has_fixed_size_hitcount_output else "unknown",
            "public_rows_execution": "host_indexed" if rows_abi_calls_host_indexed else "unknown_or_native",
        },
        "implementation_plan": [
            "Reuse the existing native segment-polygon custom-AABB traversal foundation rather than creating a second unrelated geometry encoding.",
            "Add a bounded native pair-row emission contract for variable-length output instead of the current fixed one-row-per-segment output buffer.",
            "Choose and document an overflow-safe strategy before promotion: either a two-pass count-then-emit contract or an explicit bounded-capacity plus overflow-status contract.",
            "Only after the native rows ABI exists should the public rows path stop calling the host-indexed helper and move into a strict correctness/performance gate.",
        ],
        "acceptance_conditions": [
            "A public OptiX rows ABI exists that no longer dispatches to the host-indexed helper.",
            "The native rows implementation is backed by the custom-AABB traversal foundation, not a disguised CPU loop.",
            "A local gate proves exact row-digest parity against the CPU reference.",
            "A real OptiX artifact exists before any RT-core readiness or RTX claim review.",
        ],
        "boundary": (
            "This packet is implementation-facing only. It does not authorize promotion of rows mode. "
            "Its purpose is to turn the current blocker into a concrete engineering plan tied to the existing native hit-count foundation."
        ),
    }


def to_markdown(packet: dict[str, Any]) -> str:
    evidence = packet["source_evidence"]
    truth = packet["current_truth"]
    return "\n".join(
        [
            "# Goal869 Native Pair-Row Emitter Implementation Packet",
            "",
            f"- app: `{packet['app']}`",
            f"- mode: `{packet['mode']}`",
            f"- current blocker: `{packet['current_blocker']}`",
            f"- recommended status: `{packet['recommended_status']}`",
            "",
            "## Current Truth",
            "",
            f"- native hitcount foundation: `{truth['native_hitcount_foundation']}`",
            f"- rows output shape: `{truth['rows_output_shape']}`",
            f"- existing native output shape: `{truth['existing_native_output_shape']}`",
            f"- public rows execution: `{truth['public_rows_execution']}`",
            "",
            "## Source Evidence",
            "",
            f"- native hitcount pipeline present: `{evidence['native_hitcount_pipeline_present']}`",
            f"- fixed-size hitcount output present: `{evidence['fixed_size_hitcount_output_present']}`",
            f"- public rows ABI present: `{evidence['public_rows_abi_present']}`",
            f"- rows ABI calls host-indexed: `{evidence['rows_abi_calls_host_indexed']}`",
            f"- native rows impl present: `{evidence['native_rows_impl_present']}`",
            "",
            "## Implementation Plan",
            "",
            *[f"- {item}" for item in packet["implementation_plan"]],
            "",
            "## Acceptance Conditions",
            "",
            *[f"- {item}" for item in packet["acceptance_conditions"]],
            "",
            "## Boundary",
            "",
            packet["boundary"],
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build an implementation-facing packet for the native OptiX pair-row emitter gap.")
    parser.add_argument("--workloads-cpp", type=Path, default=DEFAULT_WORKLOADS_CPP)
    parser.add_argument("--api-cpp", type=Path, default=DEFAULT_API_CPP)
    parser.add_argument("--prelude-h", type=Path, default=DEFAULT_PRELUDE_H)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args(argv)

    packet = build_packet(
        _read_text(args.workloads_cpp),
        _read_text(args.api_cpp),
        _read_text(args.prelude_h),
    )
    packet["sources"] = {
        "workloads_cpp": str(args.workloads_cpp),
        "api_cpp": str(args.api_cpp),
        "prelude_h": str(args.prelude_h),
    }
    args.output_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(packet) + "\n", encoding="utf-8")
    print(json.dumps({"output_json": str(args.output_json), "output_md": str(args.output_md), "recommended_status": packet["recommended_status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
