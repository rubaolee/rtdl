#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_API_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
DEFAULT_WORKLOADS_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
DEFAULT_CODEGEN_PY = ROOT / "src" / "rtdsl" / "codegen.py"
DEFAULT_OUTPUT_JSON = ROOT / "docs" / "reports" / "goal867_native_pair_row_emitter_design_packet_2026-04-23.json"
DEFAULT_OUTPUT_MD = ROOT / "docs" / "reports" / "goal867_native_pair_row_emitter_design_packet_2026-04-23.md"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_packet(api_cpp: str, workloads_cpp: str, codegen_py: str) -> dict[str, Any]:
    api_symbol_present = "rtdl_optix_run_segment_polygon_anyhit_rows(" in api_cpp
    api_calls_host_indexed = "run_seg_poly_anyhit_rows_optix_host_indexed(" in api_cpp
    host_indexed_impl_present = "static void run_seg_poly_anyhit_rows_optix_host_indexed(" in workloads_cpp
    native_pair_row_impl_present = "static void run_seg_poly_anyhit_rows_optix_native(" in workloads_cpp
    placeholder_raygen_present = "__raygen__rtdl_segment_polygon_anyhit_rows_probe" in codegen_py and "placeholder" in codegen_py
    placeholder_closesthit_present = "__closesthit__rtdl_segment_polygon_anyhit_rows_refine" in codegen_py and "Materialize one (segment_id, polygon_id) row" in codegen_py

    recommended_status = "needs_native_pair_row_emitter_implementation"
    if native_pair_row_impl_present and not api_calls_host_indexed and not placeholder_raygen_present:
        recommended_status = "ready_for_native_pair_row_gate"

    return {
        "goal": "Goal867 native pair-row emitter design packet",
        "date": "2026-04-23",
        "app": "segment_polygon_anyhit_rows",
        "mode": "rows",
        "recommended_status": recommended_status,
        "blocker": "native_pair_row_emitter_missing" if recommended_status != "ready_for_native_pair_row_gate" else "none",
        "evidence": {
            "api_symbol_present": api_symbol_present,
            "api_calls_host_indexed_helper": api_calls_host_indexed,
            "host_indexed_helper_present": host_indexed_impl_present,
            "native_pair_row_impl_present": native_pair_row_impl_present,
            "generated_raygen_placeholder_present": placeholder_raygen_present,
            "generated_closesthit_stub_present": placeholder_closesthit_present,
        },
        "current_truth": {
            "abi_surface": "present" if api_symbol_present else "missing",
            "runtime_execution": (
                "host_indexed_exact_cpu_loop"
                if api_calls_host_indexed and host_indexed_impl_present
                else "unknown_or_native"
            ),
            "device_codegen": (
                "placeholder_only"
                if placeholder_raygen_present
                else "non_placeholder"
            ),
        },
        "required_work": [
            "Add a true native OptiX pair-row emitter instead of calling the host-indexed helper from the public C ABI.",
            "Define bounded native output memory semantics for pair-row emission, including count discovery and overflow policy.",
            "Replace the generated segment_polygon_anyhit_rows OptiX device placeholder with an implementation-backed contract.",
            "Add a strict correctness/performance gate with CPU reference digest and real OptiX artifact evidence before promotion.",
        ],
        "promotion_boundary": (
            "Do not promote segment_polygon_anyhit_rows rows mode into any RT-core-ready or active RTX claim set until "
            "the public OptiX row path stops using the host-indexed helper and the generated device path is no longer placeholder-only."
        ),
    }


def to_markdown(packet: dict[str, Any]) -> str:
    evidence = packet["evidence"]
    current = packet["current_truth"]
    required_work = packet["required_work"]
    return "\n".join(
        [
            "# Goal867 Native Pair-Row Emitter Design Packet",
            "",
            f"- app: `{packet['app']}`",
            f"- mode: `{packet['mode']}`",
            f"- recommended status: `{packet['recommended_status']}`",
            f"- blocker: `{packet['blocker']}`",
            "",
            "## Current Truth",
            "",
            f"- ABI surface: `{current['abi_surface']}`",
            f"- runtime execution: `{current['runtime_execution']}`",
            f"- device codegen: `{current['device_codegen']}`",
            "",
            "## Evidence",
            "",
            f"- api symbol present: `{evidence['api_symbol_present']}`",
            f"- api calls host-indexed helper: `{evidence['api_calls_host_indexed_helper']}`",
            f"- host-indexed helper present: `{evidence['host_indexed_helper_present']}`",
            f"- native pair-row impl present: `{evidence['native_pair_row_impl_present']}`",
            f"- generated raygen placeholder present: `{evidence['generated_raygen_placeholder_present']}`",
            f"- generated closesthit stub present: `{evidence['generated_closesthit_stub_present']}`",
            "",
            "## Required Work",
            "",
            *[f"- {item}" for item in required_work],
            "",
            "## Boundary",
            "",
            packet["promotion_boundary"],
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a source-backed design packet for the segment_polygon_anyhit_rows native pair-row emitter gap.")
    parser.add_argument("--api-cpp", type=Path, default=DEFAULT_API_CPP)
    parser.add_argument("--workloads-cpp", type=Path, default=DEFAULT_WORKLOADS_CPP)
    parser.add_argument("--codegen-py", type=Path, default=DEFAULT_CODEGEN_PY)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args(argv)

    packet = build_packet(
        _read_text(args.api_cpp),
        _read_text(args.workloads_cpp),
        _read_text(args.codegen_py),
    )
    packet["sources"] = {
        "api_cpp": str(args.api_cpp),
        "workloads_cpp": str(args.workloads_cpp),
        "codegen_py": str(args.codegen_py),
    }
    args.output_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(packet) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output_json": str(args.output_json),
                "output_md": str(args.output_md),
                "recommended_status": packet["recommended_status"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
