#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKLOADS_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
DEFAULT_API_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
DEFAULT_APP = ROOT / "examples" / "rtdl_graph_analytics_app.py"
DEFAULT_MATRIX = ROOT / "src" / "rtdsl" / "app_support_matrix.py"
DEFAULT_OUTPUT_JSON = ROOT / "docs" / "reports" / "goal868_graph_redesign_decision_packet_2026-04-23.json"
DEFAULT_OUTPUT_MD = ROOT / "docs" / "reports" / "goal868_graph_redesign_decision_packet_2026-04-23.md"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_packet(workloads_cpp: str, api_cpp: str, app_py: str, matrix_py: str) -> dict[str, Any]:
    bfs_host_indexed = "run_bfs_expand_optix_host_indexed(" in workloads_cpp and "run_bfs_expand_optix_host_indexed(" in api_cpp
    triangle_host_indexed = "run_triangle_probe_optix_host_indexed(" in workloads_cpp and "run_triangle_probe_optix_host_indexed(" in api_cpp
    bfs_native_graph_ray = "run_bfs_expand_optix_graph_ray(" in workloads_cpp and "run_bfs_expand_optix_graph_ray(" in api_cpp
    triangle_native_graph_ray = "run_triangle_probe_optix_graph_ray(" in workloads_cpp and "run_triangle_probe_optix_graph_ray(" in api_cpp
    require_rt_core_rejects = (
        "limited to --scenario visibility_edges" in app_py
        and "native graph-ray mode remain RTX-gated" in app_py
    ) or "graph_analytics OptiX path is host-indexed fallback today, not NVIDIA RT-core traversal" in app_py
    matrix_host_indexed = '"graph_analytics"' in matrix_py and "performance_class=HOST_INDEXED_FALLBACK" in matrix_py
    matrix_redesign_note = "Replace host-indexed CSR helpers with a real graph-to-RT lowering or explicitly remove graph from NVIDIA RT-core app targets." in matrix_py
    matrix_native_note = "explicit native graph-ray mode" in matrix_py and "needs_real_rtx_artifact" in matrix_py
    native_packaged = bfs_native_graph_ray and triangle_native_graph_ray and require_rt_core_rejects and matrix_native_note

    if native_packaged:
        recommended_status = "native_graph_ray_packaged_needs_rtx_artifact"
        blocker = "needs_real_rtx_artifact"
        bfs_truth = "explicit_native_graph_ray_rtx_gated"
        triangle_truth = "explicit_native_graph_ray_rtx_gated"
        local_recommendation = "run_combined_graph_rtx_gate"
        fallback_option = "keep default host-indexed path until strict RTX artifact passes review"
        required_work = [
            "Run the combined Goal889/905 RTX graph gate for visibility, native BFS graph-ray, and native triangle graph-ray.",
            "Keep --require-rt-core rejected for BFS/triangle until the strict RTX artifact passes independent review.",
            "Keep shortest-path, graph database, distributed analytics, and whole-app graph-system claims excluded.",
        ]
        boundary = (
            "This packet does not authorize graph_analytics for RT-core claims. "
            "It records that native OptiX graph-ray candidate generation is now packaged "
            "but remains RTX-gated before promotion."
        )
    else:
        recommended_status = "needs_graph_rt_redesign_or_exclusion"
        blocker = "host_indexed_graph_paths_not_rt_core"
        bfs_truth = "host_indexed_correctness_path" if bfs_host_indexed else "unknown_or_native"
        triangle_truth = "host_indexed_correctness_path" if triangle_host_indexed else "unknown_or_native"
        local_recommendation = "redesign_first"
        fallback_option = "remove graph_analytics from NVIDIA RT-core targets if no real graph-to-RT lowering is accepted"
        required_work = [
            "Design a real graph-to-RT lowering for BFS and triangle expansion instead of host-indexed CSR helpers inside the OptiX module.",
            "Add a local correctness gate that proves the redesigned graph path matches the bounded graph semantics.",
            "Keep graph_analytics out of active RTX app benchmarking until the redesigned path exists and passes a real OptiX artifact gate.",
        ]
        boundary = (
            "This packet does not authorize graph_analytics for RT-core claims. "
            "It records that the current OptiX-facing graph paths are host-indexed correctness paths and therefore require redesign or explicit exclusion."
        )

    return {
        "goal": "Goal868 graph redesign decision packet",
        "date": "2026-04-23",
        "app": "graph_analytics",
        "recommended_status": recommended_status,
        "blocker": blocker,
        "evidence": {
            "bfs_host_indexed_helper_present": bfs_host_indexed,
            "triangle_host_indexed_helper_present": triangle_host_indexed,
            "bfs_native_graph_ray_present": bfs_native_graph_ray,
            "triangle_native_graph_ray_present": triangle_native_graph_ray,
            "public_app_require_rt_core_rejects": require_rt_core_rejects,
            "support_matrix_marks_host_indexed_fallback": matrix_host_indexed,
            "support_matrix_calls_for_redesign_or_exclusion": matrix_redesign_note,
            "support_matrix_records_native_graph_ray_gate": matrix_native_note,
        },
        "current_truth": {
            "bfs_optix_path": bfs_truth,
            "triangle_optix_path": triangle_truth,
            "public_app_rt_core_status": "rejected" if require_rt_core_rejects else "not_proven",
        },
        "decision": {
            "nvidia_rt_core_claim_today": "not_allowed",
            "local_recommendation": local_recommendation,
            "fallback_option": fallback_option,
        },
        "required_work": required_work,
        "boundary": boundary,
    }


def to_markdown(packet: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Goal868 Graph Redesign Decision Packet",
            "",
            f"- app: `{packet['app']}`",
            f"- recommended status: `{packet['recommended_status']}`",
            f"- blocker: `{packet['blocker']}`",
            "",
            "## Current Truth",
            "",
            f"- BFS OptiX path: `{packet['current_truth']['bfs_optix_path']}`",
            f"- triangle OptiX path: `{packet['current_truth']['triangle_optix_path']}`",
            f"- public app RT-core status: `{packet['current_truth']['public_app_rt_core_status']}`",
            "",
            "## Evidence",
            "",
            f"- BFS host-indexed helper present: `{packet['evidence']['bfs_host_indexed_helper_present']}`",
            f"- triangle host-indexed helper present: `{packet['evidence']['triangle_host_indexed_helper_present']}`",
            f"- public app require-rt-core rejects: `{packet['evidence']['public_app_require_rt_core_rejects']}`",
            f"- support matrix marks host-indexed fallback: `{packet['evidence']['support_matrix_marks_host_indexed_fallback']}`",
            f"- support matrix calls for redesign or exclusion: `{packet['evidence']['support_matrix_calls_for_redesign_or_exclusion']}`",
            "",
            "## Required Work",
            "",
            *[f"- {item}" for item in packet["required_work"]],
            "",
            "## Boundary",
            "",
            packet["boundary"],
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a source-backed decision packet for graph_analytics RT-core redesign vs exclusion.")
    parser.add_argument("--workloads-cpp", type=Path, default=DEFAULT_WORKLOADS_CPP)
    parser.add_argument("--api-cpp", type=Path, default=DEFAULT_API_CPP)
    parser.add_argument("--app-py", type=Path, default=DEFAULT_APP)
    parser.add_argument("--matrix-py", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args(argv)

    packet = build_packet(
        _read_text(args.workloads_cpp),
        _read_text(args.api_cpp),
        _read_text(args.app_py),
        _read_text(args.matrix_py),
    )
    packet["sources"] = {
        "workloads_cpp": str(args.workloads_cpp),
        "api_cpp": str(args.api_cpp),
        "app_py": str(args.app_py),
        "matrix_py": str(args.matrix_py),
    }
    args.output_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(packet) + "\n", encoding="utf-8")
    print(json.dumps({"output_json": str(args.output_json), "output_md": str(args.output_md), "recommended_status": packet["recommended_status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
