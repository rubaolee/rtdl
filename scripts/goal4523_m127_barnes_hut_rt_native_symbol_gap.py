from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.barnes_hut_rt_native_symbol_gap.goal4523.v1"
OUT_JSON = Path("docs/reports/goal4523_v3_0_m127_barnes_hut_rt_native_symbol_gap_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4523_v3_0_m127_barnes_hut_rt_native_symbol_gap_2026-06-17.md")
NATIVE_PATHS = (
    Path("src/native/optix/rtdl_optix_api.cpp"),
    Path("src/native/optix/rtdl_optix_workloads.cpp"),
    Path("src/native/optix/rtdl_optix_core.cpp"),
)
PYTHON_WRAPPER_PATH = Path("src/rtdsl/optix_runtime.py")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    contract = rt.validate_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract()
    required_symbols = tuple(contract["required_native_symbols"])
    native_text_by_path = {path.as_posix(): _read(root / path) for path in NATIVE_PATHS}
    native_combined = "\n".join(native_text_by_path.values())
    wrapper_text = _read(root / PYTHON_WRAPPER_PATH)
    symbol_checks = {
        symbol: {
            "native_occurrences": {
                path: symbol in text for path, text in native_text_by_path.items()
            },
            "native_present_anywhere": symbol in native_combined,
            "python_wrapper_present": symbol in wrapper_text,
        }
        for symbol in required_symbols
    }
    missing_symbols = tuple(
        symbol for symbol, check in symbol_checks.items() if not check["native_present_anywhere"]
    )
    wrapper_missing_symbols = tuple(
        symbol for symbol, check in symbol_checks.items() if not check["python_wrapper_present"]
    )
    generic_optix_traversal_available_elsewhere = (
        "optixTrace" in native_combined and "optixLaunch" in native_combined
    )
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4523 / V3 M127",
        "status": "barnes_hut_rt_native_symbols_missing",
        "date": "2026-06-17",
        "contract": {
            "contract_key": contract["contract"],
            "primitive": contract["primitive"],
            "status": contract["status"],
            "required_native_symbols": required_symbols,
        },
        "source_audit": {
            "native_paths": tuple(native_text_by_path),
            "python_wrapper_path": PYTHON_WRAPPER_PATH.as_posix(),
            "symbol_checks": symbol_checks,
            "missing_native_symbols": missing_symbols,
            "missing_python_wrappers": wrapper_missing_symbols,
            "generic_optix_traversal_available_elsewhere": generic_optix_traversal_available_elsewhere,
            "fused_rt_native_block_present": not missing_symbols,
        },
        "implementation_gate": {
            "status": "blocked_missing_native_symbols",
            "native_abi_symbols_ready": not missing_symbols,
            "python_wrapper_ready": not wrapper_missing_symbols,
            "optix_traversal_proof_ready": False,
            "equivalence_oracle_ready": False,
            "timing_split_ready": False,
        },
        "next_implementation_surfaces": (
            "src/rtdsl/optix_runtime.py ctypes symbols and prepared-handle wrapper",
            "src/native/optix/rtdl_optix_api.cpp extern C prepare/run/destroy ABI",
            "src/native/optix/rtdl_optix_workloads.cpp launch/timing path with optixLaunch",
            "src/native/optix/rtdl_optix_core.cpp device program with optixTrace or equivalent traversal",
            "pod equivalence packet versus CPU/Numba fused weighted-vector references",
        ),
        "claim_boundary": {
            "runtime_executed": False,
            "current_route_changed": False,
            "rt_core_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
        "conclusion": (
            "M127 converts the Barnes-Hut RT-native future work into an auditable "
            "native-symbol gap. The generic fused weighted-vector RT-native contract "
            "exists, and the OptiX backend has traversal machinery elsewhere, but the "
            "required aggregate-tree fused prepare/run/destroy symbols and Python "
            "wrappers are still absent. Barnes-Hut RT-core wording remains blocked."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    gate = packet["implementation_gate"]
    lines = [
        "# Goal4523 / V3 M127 Barnes-Hut RT-Native Symbol Gap",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Gate",
        "",
        f"- Native ABI symbols ready: `{gate['native_abi_symbols_ready']}`",
        f"- Python wrapper ready: `{gate['python_wrapper_ready']}`",
        f"- OptiX traversal proof ready: `{gate['optix_traversal_proof_ready']}`",
        f"- Equivalence oracle ready: `{gate['equivalence_oracle_ready']}`",
        f"- Timing split ready: `{gate['timing_split_ready']}`",
        "",
        "## Missing Symbols",
        "",
    ]
    for symbol in packet["source_audit"]["missing_native_symbols"]:
        lines.append(f"- `{symbol}`")
    lines.extend(
        [
            "",
            "## Next Surfaces",
            "",
        ]
    )
    for surface in packet["next_implementation_surfaces"]:
        lines.append(f"- {surface}")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
