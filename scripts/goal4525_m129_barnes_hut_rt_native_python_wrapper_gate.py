from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.barnes_hut_rt_native_python_wrapper_gate.goal4525.v1"
OUT_JSON = Path("docs/reports/goal4525_v3_0_m129_barnes_hut_rt_native_python_wrapper_gate_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4525_v3_0_m129_barnes_hut_rt_native_python_wrapper_gate_2026-06-17.md")
OPTIX_RUNTIME = Path("src/rtdsl/optix_runtime.py")
INIT = Path("src/rtdsl/__init__.py")
NATIVE_PATHS = (
    Path("src/native/optix/rtdl_optix_api.cpp"),
    Path("src/native/optix/rtdl_optix_workloads.cpp"),
    Path("src/native/optix/rtdl_optix_core.cpp"),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    contract = rt.validate_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract()
    required_symbols = tuple(contract["required_native_symbols"])
    runtime_source = _read(root / OPTIX_RUNTIME)
    init_source = _read(root / INIT)
    native_sources = {path.as_posix(): _read(root / path) for path in NATIVE_PATHS}
    native_combined = "\n".join(native_sources.values())
    wrapper_tokens = (
        "OptixAggregateTreeFusedWeightedVectorSum2DOutput",
        "PreparedOptixAggregateTreeFusedWeightedVectorSum2D",
        "prepare_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_optix",
        "_RtdlAggregateTreeFusedWeightedVectorSum2DOutput",
        "OPTIX_AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE_PREPARE_SYMBOL",
        "OPTIX_AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE_RUN_SYMBOL",
        "OPTIX_AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE_DESTROY_SYMBOL",
    )
    wrapper_checks = {token: token in runtime_source for token in wrapper_tokens}
    export_checks = {
        "prepare_exported": "prepare_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_optix" in init_source,
        "prepared_class_exported": "PreparedOptixAggregateTreeFusedWeightedVectorSum2D" in init_source,
        "output_class_exported": "OptixAggregateTreeFusedWeightedVectorSum2DOutput" in init_source,
    }
    native_symbol_checks = {
        symbol: {
            "native_present_anywhere": symbol in native_combined,
            "python_constant_or_lookup_present": symbol in runtime_source,
        }
        for symbol in required_symbols
    }
    missing_native_symbols = tuple(
        symbol for symbol, check in native_symbol_checks.items() if not check["native_present_anywhere"]
    )
    queue = rt.v3_benchmark_implementation_queue()
    barnes_queue = next(row for row in queue["rows"] if row["app"] == "barnes_hut")
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4525 / V3 M129",
        "status": "python_wrapper_ready_native_execution_blocked",
        "date": "2026-06-17",
        "contract": {
            "contract_key": contract["contract"],
            "primitive": contract["primitive"],
            "required_native_symbols": required_symbols,
        },
        "wrapper_audit": {
            "runtime_path": OPTIX_RUNTIME.as_posix(),
            "init_path": INIT.as_posix(),
            "wrapper_checks": wrapper_checks,
            "export_checks": export_checks,
            "python_wrapper_ready": all(wrapper_checks.values()) and all(export_checks.values()),
        },
        "native_audit": {
            "native_paths": tuple(native_sources),
            "native_symbol_checks": native_symbol_checks,
            "missing_native_symbols": missing_native_symbols,
            "native_abi_symbols_exported": not missing_native_symbols,
        },
        "implementation_gate": {
            "status": (
                "blocked_missing_native_symbols"
                if missing_native_symbols
                else "blocked_fail_closed_native_scaffold"
            ),
            "python_wrapper_ready": all(wrapper_checks.values()) and all(export_checks.values()),
            "native_abi_symbols_exported": not missing_native_symbols,
            "native_abi_symbols_ready": False,
            "native_execution_ready": False,
            "optix_traversal_proof_ready": False,
            "equivalence_oracle_ready": False,
            "timing_split_ready": False,
            "current_route_changed": False,
        },
        "queue_alignment": {
            "barnes_hut_work_class": barnes_queue["work_class"],
            "barnes_hut_priority": barnes_queue["priority"],
            "barnes_hut_evidence_refs": barnes_queue["evidence_refs"],
            "barnes_hut_remaining_gap": barnes_queue["remaining_gap"],
        },
        "claim_boundary": {
            "runtime_executed": False,
            "current_route_changed": False,
            "rt_core_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
        "conclusion": (
            "M129 removes the Python-wrapper part of the Barnes-Hut RT-native "
            "blocker: RTDL now exposes an app-agnostic OptiX prepared-handle "
            "wrapper for fused aggregate-tree weighted-vector outputs. Native "
            "execution and RT-core wording remain blocked until the C++/OptiX "
            "path launches an OptiX pipeline with optixTrace and passes "
            "equivalence/timing gates."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    gate = packet["implementation_gate"]
    lines = [
        "# Goal4525 / V3 M129 Barnes-Hut RT-Native Python Wrapper Gate",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Gate",
        "",
        f"- Python wrapper ready: `{gate['python_wrapper_ready']}`",
        f"- Native ABI symbols exported: `{gate['native_abi_symbols_exported']}`",
        f"- Native execution ready: `{gate['native_execution_ready']}`",
        f"- OptiX traversal proof ready: `{gate['optix_traversal_proof_ready']}`",
        f"- Equivalence oracle ready: `{gate['equivalence_oracle_ready']}`",
        f"- Timing split ready: `{gate['timing_split_ready']}`",
        "",
        "## Missing Native Symbols",
        "",
    ]
    for symbol in packet["native_audit"]["missing_native_symbols"]:
        lines.append(f"- `{symbol}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No runtime was executed.",
            "- No current Barnes-Hut route changed.",
            "- No RT-core speedup, public speedup, or automatic partner-selection wording is authorized.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["implementation_gate"], indent=2, sort_keys=True))
    return 0 if packet["implementation_gate"]["python_wrapper_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
