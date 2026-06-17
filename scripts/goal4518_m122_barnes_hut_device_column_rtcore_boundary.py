from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.barnes_hut_device_column_rtcore_boundary.goal4518.v1"
OUT_JSON = Path("docs/reports/goal4518_v3_0_m122_barnes_hut_device_column_rtcore_boundary_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4518_v3_0_m122_barnes_hut_device_column_rtcore_boundary_2026-06-17.md")
OPTIX_SOURCE = Path("src/native/optix/rtdl_optix_api.cpp")
ROUTE_SOURCE = Path("src/rtdsl/current_benchmark_route_decisions.py")
ADEQUACY_SOURCE = Path("src/rtdsl/current_benchmark_adequacy.py")


def _source_block(root: Path) -> str:
    text = (root / OPTIX_SOURCE).read_text(encoding="utf-8")
    start = text.index("static const char* kAggregateFrontierDeviceColumns2DKernelSrc")
    end = text.index('extern "C" void rtdl_optix_destroy_aggregate_frontier_device_columns_2d')
    return text[start:end]


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    block = _source_block(root)
    route_text = _text(root / ROUTE_SOURCE)
    adequacy_text = _text(root / ADEQUACY_SOURCE)
    contract = rt.validate_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract()
    audit = {
        "source_path": OPTIX_SOURCE.as_posix(),
        "symbols_audited": (
            "rtdl_optix_prepare_aggregate_frontier_device_columns_2d",
            "rtdl_optix_run_aggregate_frontier_device_columns_2d",
            "rtdl_optix_destroy_aggregate_frontier_device_columns_2d",
        ),
        "contains_runtime_cuda_kernel_source": "static const char* kAggregateFrontierDeviceColumns2DKernelSrc" in block,
        "contains_cu_module_load": "cuModuleLoadData" in block,
        "contains_cu_launch_kernel": "cuLaunchKernel" in block,
        "contains_optix_launch": "optixLaunch" in block,
        "contains_optix_trace": "optixTrace" in block,
        "contains_optix_report_intersection": "optixReportIntersection" in block,
        "implementation_vehicle": "cuda_driver_runtime_compiled_cubin_inside_optix_backend",
        "device_resident_claim_authorized": True,
        "optix_library_backend_claim_authorized": True,
        "rt_core_traversal_claim_authorized": False,
    }
    live_guidance = {
        "route_guidance_uses_cuda_device_column_wording": (
            "OptiX-library CUDA device-column evidence" in route_text
        ),
        "adequacy_uses_cuda_device_column_wording": (
            "OptiX-library CUDA device-column evidence" in adequacy_text
        ),
        "route_guidance_stale_rtcore_device_column_wording": (
            "RT-core device-column evidence" in route_text
            or "RT-core aggregate-frontier device-column" in route_text
        ),
        "adequacy_stale_rtcore_device_column_wording": (
            "RT-core device-column evidence" in adequacy_text
            or "RT-core aggregate-frontier device-column" in adequacy_text
        ),
    }
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4518 / V3 M122",
        "status": "device_column_rtcore_boundary_repaired",
        "date": "2026-06-17",
        "aggregate_frontier_device_column_audit": audit,
        "fused_contract_rt_core_requirements": tuple(contract["rt_core_claim_requirements"]),
        "live_guidance": live_guidance,
        "claim_boundary": {
            "prepared_aggregate_frontier_device_columns_are_device_resident": True,
            "prepared_aggregate_frontier_device_columns_are_rt_core_traversal_evidence": False,
            "barnes_hut_rt_core_speedup_claim_authorized": False,
            "future_fused_primitive_implemented": False,
            "cuda_only_fused_kernel_sufficient_for_rt_core_claim": False,
        },
        "conclusion": (
            "M122 repairs Barnes-Hut wording: the current prepared aggregate-frontier "
            "device-column route is useful device-resident work inside the OptiX "
            "backend, implemented with CUDA driver kernels, but it is not current "
            "RT-core traversal evidence. Barnes-Hut RT-core wording now requires the "
            "future fused aggregate-tree primitive plus an OptiX launch/trace proof."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    audit = packet["aggregate_frontier_device_column_audit"]
    guidance = packet["live_guidance"]
    lines = [
        "# Goal4518 / V3 M122 Barnes-Hut Device-Column RT-Core Boundary",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Source Audit",
        "",
        "| Check | Value |",
        "| --- | --- |",
        f"| Source | `{audit['source_path']}` |",
        f"| Runtime CUDA kernel source | `{audit['contains_runtime_cuda_kernel_source']}` |",
        f"| `cuModuleLoadData` | `{audit['contains_cu_module_load']}` |",
        f"| `cuLaunchKernel` | `{audit['contains_cu_launch_kernel']}` |",
        f"| `optixLaunch` | `{audit['contains_optix_launch']}` |",
        f"| `optixTrace` | `{audit['contains_optix_trace']}` |",
        f"| RT-core traversal claim authorized | `{audit['rt_core_traversal_claim_authorized']}` |",
        "",
        "## Live Guidance Check",
        "",
        "| Check | Value |",
        "| --- | --- |",
    ]
    for key, value in guidance.items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Future Gate",
            "",
            "- A CUDA-only fused implementation can be useful device evidence.",
            "- A Barnes-Hut RT-core claim requires an OptiX pipeline launch and device traversal proof.",
            "- Timing must separate build, traversal, continuation, and copy phases.",
            "- Current public wording remains blocked.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["aggregate_frontier_device_column_audit"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
