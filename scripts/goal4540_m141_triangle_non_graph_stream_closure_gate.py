from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.triangle_non_graph_stream_closure_gate.goal4540.v1"
OUT_JSON = Path("docs/reports/goal4540_v3_0_m141_triangle_non_graph_stream_closure_gate_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4540_v3_0_m141_triangle_non_graph_stream_closure_gate_2026-06-17.md")
GOAL4539_PACKET = Path("docs/reports/goal4539_v3_0_m140_triangle_capture_mode_audit_2026-06-17.json")


def _read_goal4539(root: Path) -> dict[str, Any]:
    return json.loads((root / GOAL4539_PACKET).read_text(encoding="utf-8"))


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    queue = rt.v3_benchmark_implementation_queue()
    validation = rt.validate_v3_benchmark_implementation_queue(queue)
    rows = {row["app"]: row for row in queue["rows"]}
    triangle = rows["triangle_counting"]
    barnes = rows["barnes_hut"]
    summary = queue["summary"]
    goal4539 = _read_goal4539(root)
    goal4539_runtime = goal4539["runtime"]
    goal4539_acceptance = goal4539["acceptance"]
    checks = {
        "queue_validates": validation["status"] == "accept",
        "runtime_queue_empty": tuple(summary["runtime_build_queue"]) == (),
        "claim_queue_empty": tuple(summary["claim_or_evidence_queue"]) == (),
        "design_blocker_queue_empty": tuple(summary["design_blocker_queue"]) == (),
        "future_design_queue_empty_after_goal4541": tuple(summary["future_design_target_queue"])
        == (),
        "closed_current_target_count_is_ten_after_goal4541": (
            len(summary["closed_current_targets"]) == 10
        ),
        "triangle_closed_current_target": triangle["work_class"] == "closed_current_target",
        "triangle_has_goal4540_evidence": "Goal4540" in triangle["evidence_refs"],
        "triangle_non_graph_stream_contract_accepted": (
            "non-graph stream" in triangle["remaining_gap"]
            and goal4539_acceptance["non_graph_stream_continuation_evidence_accepted"]
        ),
        "triangle_m113_graph_still_blocked": (
            goal4539_acceptance["m113_graph_capture_still_blocked"]
            and "M113 graph" in triangle["next_build_target"]
        ),
        "barnes_hut_closed_by_goal4541_successor": (
            barnes["work_class"] == "closed_current_target"
            and "Goal4541" in barnes["evidence_refs"]
        ),
        "goal4539_stream_prelaunch_validated": goal4539_runtime[
            "device_output_stream_prelaunch_validated"
        ],
        "goal4539_graph_capture_modes_all_reject": (
            tuple(goal4539_runtime["graph_capture_validated_modes"]) == ()
            and goal4539_runtime["graph_capture_mode_independent_reject"]
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
        "goal": "Goal4540 / V3 M141",
        "status": "triangle_non_graph_stream_closure_gate_checked",
        "date": "2026-06-17",
        "queue_version": queue["version"],
        "queue_status": queue["status"],
        "source_packets": {
            "goal4539": goal4539["version"],
        },
        "checks": checks,
        "failed_checks": failed,
        "summary": summary,
        "triangle_row": triangle,
        "barnes_hut_row": barnes,
        "goal4539_runtime": goal4539_runtime,
        "goal4539_acceptance": goal4539_acceptance,
        "review_intake": {
            "singer_verdict": "request_changes_for_goal4539_direct_flip",
            "singer_resolution": (
                "addressed by adding this explicit successor gate instead of "
                "using Goal4539 itself to authorize queue reclassification"
            ),
            "ramanujan_verdict": "approve_with_caveats",
            "shared_caveat": (
                "closure is only non-graph device-output stream continuation; "
                "M113 graph readiness and public/broad/native claims remain blocked"
            ),
        },
        "claim_boundary": {
            "current_route_changed": False,
            "runtime_executed": False,
            "queue_reclassification_authorized": True,
            "queue_reclassification_scope": (
                "triangle_counting future_design_target to closed_current_target "
                "only through non-graph stream continuation evidence"
            ),
            "prepared_weighted_replay_device_output_stream_validated": True,
            "prepared_weighted_replay_graph_capture_validated": False,
            "m113_promotion_authorized_for_future_triangle_shape": False,
            "m113_replaces_current_triangle_route": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        },
        "conclusion": (
            "Goal4540 explicitly supersedes Goal4539's no-reclassification boundary "
            "for exactly one purpose: Triangle Counting is moved from future design "
            "target to closed current target because Goal4539 validates the "
            "non-graph device-output stream continuation evidence and confirms "
            "CUDA graph capture remains invalid across capture modes. Goal4541 "
            "later closes Barnes-Hut only as a current mixed-explicit route "
            "classification, so the current future-design queue is empty. This "
            "does not authorize M113 graph readiness, RT-native Barnes-Hut "
            "traversal, release, public speedup, broad RT-core, automatic "
            "partner-selection, paper-reproduction, or app-specific native-engine "
            "wording."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    summary = packet["summary"]
    runtime = packet["goal4539_runtime"]
    lines = [
        "# Goal4540 / V3 M141 Triangle Non-Graph Stream Closure Gate",
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
        "## Goal4539 Evidence",
        "",
        f"- Device-output stream prelaunch validated: `{runtime['device_output_stream_prelaunch_validated']}`",
        f"- Graph capture validated modes: `{', '.join(runtime['graph_capture_validated_modes'])}`",
        f"- Graph capture mode-independent reject: `{runtime['graph_capture_mode_independent_reject']}`",
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
            "- Triangle queue reclassification is authorized only for non-graph stream continuation closure.",
            "- No current Triangle route changed.",
            "- No M113 graph promotion, release, public speedup, broad RT-core, automatic partner-selection, paper-reproduction, or app-specific native-engine wording is authorized.",
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
