#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORE_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
DEFAULT_WORKLOADS_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
DEFAULT_API_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
DEFAULT_OUTPUT_JSON = ROOT / "docs" / "reports" / "goal872_native_pair_row_device_emitter_packet_2026-04-24.json"
DEFAULT_OUTPUT_MD = ROOT / "docs" / "reports" / "goal872_native_pair_row_device_emitter_packet_2026-04-24.md"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_packet(core_cpp: str, workloads_cpp: str, api_cpp: str) -> dict[str, Any]:
    kernel_present = "kSegPolyAnyhitRowsKernelSrc" in core_cpp
    anyhit_appends = "atomicAdd(params.output_count, 1u)" in core_cpp
    overflow_flag_present = "atomicExch(params.overflowed, 1u)" in core_cpp
    pair_payload_present = "params.output[slot] = {params.segments[sidx].id, params.polygons[prim].id}" in core_cpp
    pipeline_present = "g_segpoly_rows.pipe = build_pipeline" in workloads_cpp
    launch_present = "optixLaunch(g_segpoly_rows.pipe->pipeline" in workloads_cpp
    bounded_copy_present = "std::min<size_t>(emitted, output_capacity)" in workloads_cpp
    public_rows_still_host_indexed = "run_seg_poly_anyhit_rows_optix_host_indexed(" in api_cpp

    return {
        "goal": "Goal872 native pair-row device emitter packet",
        "date": "2026-04-24",
        "app": "segment_polygon_anyhit_rows",
        "mode": "native_bounded_rows",
        "recommended_status": "device_emitter_implemented_pending_real_optix_gate",
        "evidence": {
            "kernel_present": kernel_present,
            "anyhit_atomic_append_present": anyhit_appends,
            "overflow_flag_present": overflow_flag_present,
            "pair_payload_present": pair_payload_present,
            "pipeline_present": pipeline_present,
            "launch_present": launch_present,
            "bounded_copy_present": bounded_copy_present,
            "public_rows_path_still_host_indexed": public_rows_still_host_indexed,
        },
        "current_behavior": {
            "native_bounded_symbol": "attempts_device_emission",
            "overflow_semantics": "emitted_count_reports_total_hits; rows_out_receives_prefix_up_to_output_capacity; overflowed_out marks truncation",
            "public_rows_path": "unchanged_host_indexed_until_gate",
        },
        "remaining_gate": (
            "A Linux/RTX build must compile and run the new native bounded symbol, compare row digests against CPU reference, "
            "and then decide whether to promote the public rows path or keep it separate."
        ),
        "boundary": (
            "This goal implements the first native bounded device-emission path, but it does not promote the public rows app path. "
            "No RT-core readiness claim is authorized until a real OptiX artifact passes the strict gate."
        ),
    }


def to_markdown(packet: dict[str, Any]) -> str:
    ev = packet["evidence"]
    behavior = packet["current_behavior"]
    return "\n".join(
        [
            "# Goal872 Native Pair-Row Device Emitter Packet",
            "",
            f"- app: `{packet['app']}`",
            f"- mode: `{packet['mode']}`",
            f"- recommended status: `{packet['recommended_status']}`",
            "",
            "## Evidence",
            "",
            f"- kernel present: `{ev['kernel_present']}`",
            f"- any-hit atomic append present: `{ev['anyhit_atomic_append_present']}`",
            f"- overflow flag present: `{ev['overflow_flag_present']}`",
            f"- pair payload present: `{ev['pair_payload_present']}`",
            f"- pipeline present: `{ev['pipeline_present']}`",
            f"- launch present: `{ev['launch_present']}`",
            f"- bounded copy present: `{ev['bounded_copy_present']}`",
            f"- public rows path still host-indexed: `{ev['public_rows_path_still_host_indexed']}`",
            "",
            "## Current Behavior",
            "",
            f"- native bounded symbol: `{behavior['native_bounded_symbol']}`",
            f"- overflow semantics: `{behavior['overflow_semantics']}`",
            f"- public rows path: `{behavior['public_rows_path']}`",
            "",
            "## Remaining Gate",
            "",
            packet["remaining_gate"],
            "",
            "## Boundary",
            "",
            packet["boundary"],
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a packet for the native bounded OptiX pair-row device emitter.")
    parser.add_argument("--core-cpp", type=Path, default=DEFAULT_CORE_CPP)
    parser.add_argument("--workloads-cpp", type=Path, default=DEFAULT_WORKLOADS_CPP)
    parser.add_argument("--api-cpp", type=Path, default=DEFAULT_API_CPP)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args(argv)
    packet = build_packet(
        _read_text(args.core_cpp),
        _read_text(args.workloads_cpp),
        _read_text(args.api_cpp),
    )
    packet["sources"] = {
        "core_cpp": str(args.core_cpp),
        "workloads_cpp": str(args.workloads_cpp),
        "api_cpp": str(args.api_cpp),
    }
    args.output_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(packet) + "\n", encoding="utf-8")
    print(json.dumps({"output_json": str(args.output_json), "output_md": str(args.output_md), "recommended_status": packet["recommended_status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
