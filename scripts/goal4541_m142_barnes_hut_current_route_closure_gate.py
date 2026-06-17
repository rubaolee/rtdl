from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.barnes_hut_current_route_closure_gate.goal4541.v1"
OUT_JSON = Path(
    "docs/reports/goal4541_v3_0_m142_barnes_hut_current_route_closure_gate_2026-06-17.json"
)
OUT_REPORT = Path(
    "docs/reports/goal4541_v3_0_m142_barnes_hut_current_route_closure_gate_2026-06-17.md"
)


def build_packet() -> dict[str, Any]:
    queue = rt.v3_benchmark_implementation_queue()
    validation = rt.validate_v3_benchmark_implementation_queue(queue)
    rows = {row["app"]: row for row in queue["rows"]}
    routes = {row["app"]: row for row in rt.current_benchmark_route_decisions()}
    adequacy = {row["app"]: row for row in rt.current_benchmark_adequacy()}
    summary = queue["summary"]
    barnes = rows["barnes_hut"]
    barnes_route = routes["barnes_hut"]
    barnes_adequacy = adequacy["barnes_hut"]
    checks = {
        "queue_validates": validation["status"] == "accept",
        "runtime_queue_empty": tuple(summary["runtime_build_queue"]) == (),
        "claim_queue_empty": tuple(summary["claim_or_evidence_queue"]) == (),
        "design_blocker_queue_empty": tuple(summary["design_blocker_queue"]) == (),
        "future_design_queue_empty": tuple(summary["future_design_target_queue"]) == (),
        "all_ten_apps_closed_current_targets": len(summary["closed_current_targets"]) == 10,
        "barnes_hut_closed_current_target": barnes["work_class"] == "closed_current_target",
        "barnes_hut_priority_none": barnes["priority"] is None,
        "barnes_hut_goal4541_recorded": "Goal4541" in barnes["evidence_refs"],
        "barnes_hut_goal4512_and_goal4527_preserved": (
            "Goal4512" in barnes["evidence_refs"]
            and "Goal4527" in barnes["evidence_refs"]
        ),
        "barnes_hut_pod_not_needed_next": not barnes["pod_needed_next"],
        "barnes_hut_future_rt_native_boundary_preserved": (
            "RT-native" in barnes["remaining_gap"]
            and "hierarchical traversal" in barnes["remaining_gap"]
            and "Future optional RT-native research" in barnes["next_build_target"]
        ),
        "barnes_route_and_adequacy_updated": (
            "Goal4541" in barnes_route["evidence_refs"]
            and not barnes_route["pod_needed_next"]
            and "Goal4541" in barnes_adequacy["evidence_refs"]
            and not barnes_adequacy["pod_needed_next"]
        ),
        "all_public_speedup_claims_blocked": summary["all_public_speedup_claims_blocked"],
        "all_broad_rt_core_claims_blocked": summary["all_broad_rt_core_claims_blocked"],
        "all_paper_reproduction_claims_blocked": summary["all_paper_reproduction_claims_blocked"],
        "all_automatic_partner_selection_blocked": summary[
            "all_automatic_partner_selection_blocked"
        ],
        "all_app_specific_native_engine_logic_blocked": summary[
            "all_app_specific_native_engine_logic_blocked"
        ],
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4541 / V3 M142",
        "status": "barnes_hut_current_route_closure_gate_checked",
        "date": "2026-06-17",
        "queue_version": queue["version"],
        "queue_status": queue["status"],
        "checks": checks,
        "failed_checks": failed,
        "summary": summary,
        "barnes_hut_row": barnes,
        "barnes_hut_route_decision": barnes_route,
        "barnes_hut_adequacy": barnes_adequacy,
        "review_intake": {
            "leibniz_verdict": "approve_with_caveats",
            "russell_verdict": "approve_with_caveats",
            "shared_caveat": (
                "Close only the current mixed-explicit route classification; do not "
                "claim RT-native Barnes-Hut traversal, RT-core speedup, release, "
                "paper reproduction, automatic partner selection, or app-specific "
                "native engine logic."
            ),
        },
        "claim_boundary": {
            "current_route_changed": False,
            "runtime_executed": False,
            "queue_reclassification_authorized": True,
            "queue_reclassification_scope": (
                "barnes_hut future_design_target to closed_current_target only as "
                "current mixed-explicit route classification"
            ),
            "rt_native_hierarchical_traversal_implemented": False,
            "rt_core_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4541 closes Barnes-Hut only as a current V3 mixed-explicit "
            "route-classification target. The current route remains "
            "scale-dependent fused CPU/Numba or fused Numba CUDA, with "
            "prepared RTDL/OptiX+Numba retained as OptiX-library CUDA "
            "device-column evidence. The future design queue is now empty and "
            "all ten benchmark apps are closed current targets. This does not "
            "implement RT-native Barnes-Hut hierarchical traversal and does not "
            "authorize release, public speedup, broad RT-core, paper-reproduction, "
            "automatic partner-selection, or app-specific native-engine wording."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    summary = packet["summary"]
    barnes = packet["barnes_hut_row"]
    lines = [
        "# Goal4541 / V3 M142 Barnes-Hut Current Route Closure Gate",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Queue State",
        "",
        f"- Runtime queue: `{', '.join(summary['runtime_build_queue'])}`",
        f"- Claim/evidence queue: `{', '.join(summary['claim_or_evidence_queue'])}`",
        f"- Design blocker queue: `{', '.join(summary['design_blocker_queue'])}`",
        f"- Future design targets: `{', '.join(summary['future_design_target_queue'])}`",
        f"- Closed current targets: `{', '.join(summary['closed_current_targets'])}`",
        "",
        "## Barnes-Hut Boundary",
        "",
        f"- Work class: `{barnes['work_class']}`",
        f"- Priority: `{barnes['priority']}`",
        f"- Pod needed next: `{barnes['pod_needed_next']}`",
        f"- Remaining gap: {barnes['remaining_gap']}",
        f"- Next/future target: {barnes['next_build_target']}",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for name, passed in packet["checks"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No runtime was executed.",
            "- No current route changed.",
            "- RT-native Barnes-Hut hierarchical traversal remains unimplemented future optional research/claim expansion.",
            "- No release, public speedup, broad RT-core, paper-reproduction, automatic partner-selection, or app-specific native-engine wording is authorized.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(
        json.dumps(
            {
                "failed_checks": packet["failed_checks"],
                "status": "accept" if not packet["failed_checks"] else "reject",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not packet["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
