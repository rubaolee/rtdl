from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.barnes_hut_rt_native_fail_closed_abi.goal4526.v1"
OUT_JSON = Path("docs/reports/goal4526_v3_0_m130_barnes_hut_rt_native_fail_closed_abi_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4526_v3_0_m130_barnes_hut_rt_native_fail_closed_abi_2026-06-17.md")
PRELUDE = Path("src/native/optix/rtdl_optix_prelude.h")
API = Path("src/native/optix/rtdl_optix_api.cpp")
RUNTIME = Path("src/rtdsl/optix_runtime.py")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    contract = rt.validate_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract()
    required_symbols = tuple(contract["required_native_symbols"])
    prelude = _read(root / PRELUDE)
    api = _read(root / API)
    runtime = _read(root / RUNTIME)
    export_checks = {
        symbol: {
            "declared_in_prelude": symbol in prelude,
            "defined_in_api": f'extern "C" int {symbol}' in api
            or f'extern "C" void {symbol}' in api,
            "python_wrapper_looks_up_symbol": symbol in runtime,
        }
        for symbol in required_symbols
    }
    fail_closed_fragments = (
        "not implemented yet",
        "ABI is exported fail-closed",
        "optixLaunch/optixTrace implementation",
    )
    fail_closed_checks = {fragment: fragment in api for fragment in fail_closed_fragments}
    queue = rt.v3_benchmark_implementation_queue()
    barnes_queue = next(row for row in queue["rows"] if row["app"] == "barnes_hut")
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4526 / V3 M130",
        "status": "native_abi_symbols_exported_fail_closed",
        "date": "2026-06-17",
        "contract": {
            "contract_key": contract["contract"],
            "primitive": contract["primitive"],
            "required_native_symbols": required_symbols,
        },
        "source_audit": {
            "prelude": PRELUDE.as_posix(),
            "api": API.as_posix(),
            "runtime": RUNTIME.as_posix(),
            "export_checks": export_checks,
            "all_symbols_declared_defined_and_wrapped": all(
                all(check.values()) for check in export_checks.values()
            ),
            "output_struct_declared": "RtdlAggregateTreeFusedWeightedVectorSum2DOutput" in prelude,
            "fail_closed_checks": fail_closed_checks,
            "fail_closed_ready": all(fail_closed_checks.values()),
        },
        "implementation_gate": {
            "status": "blocked_fail_closed_native_scaffold",
            "python_wrapper_ready": True,
            "native_abi_symbols_exported": all(
                all(check.values()) for check in export_checks.values()
            ),
            "native_execution_ready": False,
            "optix_traversal_proof_ready": False,
            "equivalence_oracle_ready": False,
            "timing_split_ready": False,
        },
        "queue_alignment": {
            "barnes_hut_work_class": barnes_queue["work_class"],
            "barnes_hut_priority": barnes_queue["priority"],
            "barnes_hut_evidence_refs": barnes_queue["evidence_refs"],
            "barnes_hut_next_build_target": barnes_queue["next_build_target"],
        },
        "claim_boundary": {
            "runtime_executed": False,
            "current_route_changed": False,
            "rt_core_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
        "conclusion": (
            "M130 removes the missing-symbol cliff for the Barnes-Hut RT-native "
            "path by adding the app-agnostic native prepare/run/destroy ABI and "
            "matching Python bindings. The symbols intentionally fail closed: "
            "native execution, OptiX traversal proof, equivalence, timing split, "
            "and RT-core wording remain blocked until the scaffold is replaced "
            "with a real optixLaunch/optixTrace implementation."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    gate = packet["implementation_gate"]
    lines = [
        "# Goal4526 / V3 M130 Barnes-Hut RT-Native Fail-Closed ABI",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Gate",
        "",
        f"- Native ABI symbols exported: `{gate['native_abi_symbols_exported']}`",
        f"- Native execution ready: `{gate['native_execution_ready']}`",
        f"- OptiX traversal proof ready: `{gate['optix_traversal_proof_ready']}`",
        f"- Equivalence oracle ready: `{gate['equivalence_oracle_ready']}`",
        f"- Timing split ready: `{gate['timing_split_ready']}`",
        "",
        "## Symbols",
        "",
        "| Symbol | Declared | Defined | Python wrapper |",
        "| --- | --- | --- | --- |",
    ]
    for symbol, check in packet["source_audit"]["export_checks"].items():
        lines.append(
            f"| `{symbol}` | `{check['declared_in_prelude']}` | "
            f"`{check['defined_in_api']}` | `{check['python_wrapper_looks_up_symbol']}` |"
        )
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
    return 0 if packet["implementation_gate"]["native_abi_symbols_exported"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
