from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.aggregate_tree_fused_rt_native_contract.goal4517.v1"
OUT_JSON = Path("docs/reports/goal4517_v3_0_m121_aggregate_tree_fused_rt_native_contract_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4517_v3_0_m121_aggregate_tree_fused_rt_native_contract_2026-06-17.md")
GOAL4497 = Path("docs/reports/goal4497_v3_0_m101_barnes_hut_rt_native_fused_feasibility_2026-06-17.json")
GOAL4516 = Path("docs/reports/goal4516_v3_0_m120_prepared_graph_chunk_adoption_gate_2026-06-17.json")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _goal4497_candidate(root: Path) -> dict[str, Any]:
    path = root / GOAL4497
    if not path.exists():
        return {}
    packet = _load_json(path)
    candidate = packet.get("candidate_contract", {})
    if isinstance(candidate, dict):
        return candidate
    return {}


def _goal4516_barnes_hut_row(root: Path) -> dict[str, Any]:
    path = root / GOAL4516
    if not path.exists():
        return {}
    packet = _load_json(path)
    for row in packet.get("rows", []):
        if not isinstance(row, dict):
            continue
        assessment = row.get("assessment", {})
        if isinstance(assessment, dict) and assessment.get("app_id") == "barnes_hut":
            return row
    return {}


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    contract = rt.validate_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract()
    candidate = _goal4497_candidate(root)
    adoption_row = _goal4516_barnes_hut_row(root)
    proposed = candidate.get("proposed_contract")
    assessment = adoption_row.get("assessment", {}) if isinstance(adoption_row, dict) else {}
    blockers = assessment.get("blockers", ()) if isinstance(assessment, dict) else ()

    implementation_gates = (
        {
            "gate": "native_abi_symbols",
            "status": "blocked",
            "required": tuple(contract["required_native_symbols"]),
            "acceptance": "OptiX prepare/run/destroy symbols exist and expose the declared device output columns.",
        },
        {
            "gate": "equivalence_oracles",
            "status": "blocked",
            "required": (
                contract["cpu_reference_api"],
                contract["partner_reference_api"],
            ),
            "acceptance": "RT-native output columns match CPU and Numba CUDA references by source id.",
        },
        {
            "gate": "hot_path_materialization",
            "status": "blocked",
            "required": tuple(contract["hot_path_forbidden_outputs"]),
            "acceptance": "No user-visible frontier or contribution rows are emitted on the hot path.",
        },
        {
            "gate": "measured_route_rerank",
            "status": "blocked",
            "required": (
                "Goal4458 small-row fused CPU/Numba baseline",
                "Goal4483 large-row fused Numba CUDA baseline",
                "new RT-native fused route",
            ),
            "acceptance": "Rerank uses the same source-id keyed vector-summary contract.",
        },
    )

    return {
        "version": PACKET_VERSION,
        "goal": "Goal4517 / V3 M121",
        "status": "contract_specified_runtime_not_implemented",
        "date": "2026-06-17",
        "contract": contract,
        "source_evidence": {
            "goal4497_candidate_matches": proposed == contract["contract"],
            "goal4497_candidate_contract": proposed,
            "goal4516_barnes_hut_m113_blockers": tuple(blockers),
        },
        "implementation_gates": implementation_gates,
        "claim_boundary": {
            "runtime_implemented": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        },
        "conclusion": (
            "M121 turns the Goal4497 Barnes-Hut finding into an app-agnostic RTDL "
            "runtime target: a fused aggregate-tree weighted-vector primitive that "
            "would accumulate directly into device vector/count columns. The current "
            "status is contract-only; the existing frontier device-column route remains "
            "valid RT-core evidence but not the final accelerated shape for this workload."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    contract = packet["contract"]
    lines = [
        "# Goal4517 / V3 M121 Aggregate-Tree Fused RT-Native Contract",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Contract",
        "",
        f"- Primitive: `{contract['primitive']}`",
        f"- Contract: `{contract['contract']}`",
        f"- Status: `{contract['status']}`",
        f"- Executable today: `{contract['executable']}`",
        f"- First backend target: `{contract['required_first_backend']}`",
        f"- CPU oracle: `{contract['cpu_reference_api']}`",
        f"- Partner oracle: `{contract['partner_reference_api']}`",
        "",
        "## Output Columns",
        "",
    ]
    for column in contract["output_device_columns"]:
        lines.append(f"- `{column}`")
    lines.extend(
        [
            "",
            "## Implementation Gates",
            "",
            "| Gate | Status | Acceptance |",
            "| --- | --- | --- |",
        ]
    )
    for gate in packet["implementation_gates"]:
        lines.append(f"| `{gate['gate']}` | `{gate['status']}` | {gate['acceptance']} |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- The runtime is not implemented by this packet.",
            "- No RT-core speedup, whole-app speedup, public speedup, or paper-reproduction claim is authorized.",
            "- No automatic partner selection or app-specific native engine logic is authorized.",
            "- The next real engineering step is an OptiX backend prototype that satisfies the contract and matches both oracles.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["claim_boundary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
