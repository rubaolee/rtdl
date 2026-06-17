from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.barnes_hut_rt_native_traversal_semantic_gate.goal4527.v2"
OUT_JSON = Path(
    "docs/reports/goal4527_v3_0_m131_barnes_hut_rt_native_traversal_semantic_gate_2026-06-17.json"
)
OUT_REPORT = Path(
    "docs/reports/goal4527_v3_0_m131_barnes_hut_rt_native_traversal_semantic_gate_2026-06-17.md"
)
API = Path("src/native/optix/rtdl_optix_api.cpp")
QUEUE = Path("src/rtdsl/v3_0_benchmark_implementation_queue.py")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    queue = rt.v3_benchmark_implementation_queue()
    validation = rt.validate_v3_benchmark_implementation_queue(queue)
    barnes_row = next(row for row in queue["rows"] if row["app"] == "barnes_hut")
    api = _read(root / API)
    queue_src = _read(root / QUEUE)
    fail_closed_fragments = (
        "not implemented yet",
        "ABI is exported fail-closed",
        "until optixTrace traversal",
    )
    semantic_constraints = {
        "parent_acceptance_suppresses_descendants": True,
        "single_custom_primitive_gas_reports_nodes_independently": True,
        "single_trace_parent_subtree_skip_proof_exists": False,
        "direct_all_node_anyhit_route_accepted": False,
    }
    queue_checks = {
        "barnes_hut_is_future_design_target": barnes_row["work_class"] == "future_design_target",
        "barnes_hut_not_next_runtime_target": (
            queue["summary"]["next_runtime_build_target"] != "barnes_hut"
        ),
        "runtime_queue_empty": tuple(queue["summary"]["runtime_build_queue"]) == (),
        "goal4527_recorded": "Goal4527" in barnes_row["evidence_refs"],
        "future_design_queue_recorded": tuple(queue["summary"]["future_design_target_queue"])
        == ("barnes_hut", "triangle_counting"),
    }
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4527 / V3 M131",
        "status": "barnes_hut_rt_native_semantic_gate_safe_to_advance_runtime_queue",
        "date": "2026-06-17",
        "semantic_constraints": semantic_constraints,
        "source_audit": {
            "api": API.as_posix(),
            "queue": QUEUE.as_posix(),
            "fail_closed_fragments": {
                fragment: fragment in api for fragment in fail_closed_fragments
            },
            "queue_mentions_subtree_skip_semantics": "subtree-skip semantics" in queue_src,
            "queue_rejects_direct_anyhit_route": "direct all-node any-hit route" in queue_src,
        },
        "queue_alignment": {
            "validation": validation,
            "barnes_hut_work_class": barnes_row["work_class"],
            "barnes_hut_priority": barnes_row["priority"],
            "barnes_hut_remaining_gap": barnes_row["remaining_gap"],
            "barnes_hut_next_build_target": barnes_row["next_build_target"],
            "next_runtime_build_target": queue["summary"]["next_runtime_build_target"],
            "runtime_build_queue": queue["summary"]["runtime_build_queue"],
            "design_blocker_queue": queue["summary"]["design_blocker_queue"],
            "future_design_target_queue": queue["summary"]["future_design_target_queue"],
            "queue_checks": queue_checks,
        },
        "implementation_decision": {
            "replace_fail_closed_abi_now": False,
            "implement_naive_all_node_optix_anyhit": False,
            "current_runtime_queue_remains_empty": True,
            "future_barnes_hut_requirements": (
                "A future Barnes-Hut RT-native route must use a reviewed generic "
                "hierarchical traversal lowering that proves accepted aggregate "
                "subtrees are not double counted, keeps force-law code outside "
                "app-specific native engine callbacks, and beats fused CPU/Numba "
                "and fused Numba CUDA under the same force-summary contract."
            ),
        },
        "claim_boundary": {
            "runtime_executed": False,
            "current_route_changed": False,
            "rt_core_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        },
        "conclusion": (
            "M131 prevents an incorrect Barnes-Hut RT-native implementation from "
            "landing. A direct OptiX GAS containing every aggregate-tree node "
            "cannot, by itself, express the Barnes-Hut rule that accepting a "
            "parent aggregate suppresses all descendants; reporting nodes "
            "independently would double count unless a separate reviewed "
            "hierarchical traversal/skip design exists. The fail-closed ABI "
            "therefore stays in place, and Barnes-Hut remains a future design "
            "target rather than a current V3 app implementation blocker."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    queue = packet["queue_alignment"]
    decision = packet["implementation_decision"]
    lines = [
        "# Goal4527 / V3 M131 Barnes-Hut RT-Native Traversal Semantic Gate",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Decision",
        "",
        f"- Replace fail-closed ABI now: `{decision['replace_fail_closed_abi_now']}`",
        f"- Implement naive all-node OptiX any-hit: `{decision['implement_naive_all_node_optix_anyhit']}`",
        f"- Current runtime queue remains empty: `{decision['current_runtime_queue_remains_empty']}`",
        "",
        "## Queue",
        "",
        f"- Barnes-Hut class: `{queue['barnes_hut_work_class']}`",
        f"- Runtime queue: `{', '.join(queue['runtime_build_queue'])}`",
        f"- Design blocker queue: `{', '.join(queue['design_blocker_queue'])}`",
        f"- Future design target queue: `{', '.join(queue['future_design_target_queue'])}`",
        f"- Next runtime build target: `{queue['next_runtime_build_target']}`",
        "",
        "## Future Barnes-Hut Requirement",
        "",
        decision["future_barnes_hut_requirements"],
        "",
        "## Boundary",
        "",
        "- No runtime was executed.",
        "- No current Barnes-Hut route changed.",
        "- No RT-core speedup, public speedup, automatic partner-selection, or app-specific native-engine wording is authorized.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["queue_alignment"]["queue_checks"], indent=2, sort_keys=True))
    checks = packet["queue_alignment"]["queue_checks"]
    fail_closed = packet["source_audit"]["fail_closed_fragments"]
    return 0 if all(checks.values()) and all(fail_closed.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
