from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.current_app_completion_gate.goal4534.v1"
OUT_JSON = Path("docs/reports/goal4534_v3_0_m136_v3_current_app_completion_gate_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4534_v3_0_m136_v3_current_app_completion_gate_2026-06-17.md")


def build_packet() -> dict[str, Any]:
    queue = rt.v3_benchmark_implementation_queue()
    validation = rt.validate_v3_benchmark_implementation_queue(queue)
    summary = queue["summary"]
    rows = {row["app"]: row for row in queue["rows"]}
    current_accounted = tuple(summary["closed_current_targets"]) + tuple(
        summary["future_design_target_queue"]
    )
    checks = {
        "queue_validates": validation["status"] == "accept",
        "runtime_queue_empty": tuple(summary["runtime_build_queue"]) == (),
        "claim_queue_empty": tuple(summary["claim_or_evidence_queue"]) == (),
        "design_blocker_queue_empty": tuple(summary["design_blocker_queue"]) == (),
        "future_design_queue_exact": tuple(summary["future_design_target_queue"])
        == ("barnes_hut", "triangle_counting"),
        "all_ten_apps_accounted_as_closed_or_future_design": set(current_accounted)
        == {row["app"] for row in queue["rows"]},
        "closed_current_target_count_is_eight": len(summary["closed_current_targets"]) == 8,
        "barnes_hut_future_design_target": (
            rows["barnes_hut"]["work_class"] == "future_design_target"
            and "no current V3 app implementation blocker" in rows["barnes_hut"]["remaining_gap"]
        ),
        "triangle_future_design_target": (
            rows["triangle_counting"]["work_class"] == "future_design_target"
            and "no current V3 app implementation blocker" in rows["triangle_counting"]["remaining_gap"]
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
        "goal": "Goal4534 / V3 M136",
        "status": "current_app_completion_gate_checked",
        "date": "2026-06-17",
        "queue_version": queue["version"],
        "queue_status": queue["status"],
        "checks": checks,
        "failed_checks": failed,
        "summary": summary,
        "future_design_targets": {
            "barnes_hut": rows["barnes_hut"],
            "triangle_counting": rows["triangle_counting"],
        },
        "claim_boundary": {
            "current_route_changed": False,
            "runtime_executed": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        },
        "conclusion": (
            "Goal4534 closes the V3 current app implementation queue: there are no "
            "runtime blockers, no claim/evidence blockers, and no current design "
            "blockers. Eight apps are closed current targets. Barnes-Hut and "
            "Triangle Counting remain explicitly listed as future design targets: "
            "Barnes-Hut needs a reviewed hierarchical traversal lowering before "
            "any RT-native subtree-skip route can replace the current mixed route, "
            "and Triangle Counting needs a capture-compatible OptiX weighted replay "
            "design or an accepted non-graph stream continuation contract before "
            "future M113 graph wording. This completion gate does not authorize "
            "release, public speedup, broad RT-core, paper-reproduction, automatic "
            "partner-selection, or app-specific native-engine claims."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    summary = packet["summary"]
    future = packet["future_design_targets"]
    lines = [
        "# Goal4534 / V3 M136 Current App Completion Gate",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Queue Summary",
        "",
        f"- Runtime queue: `{', '.join(summary['runtime_build_queue'])}`",
        f"- Claim/evidence queue: `{', '.join(summary['claim_or_evidence_queue'])}`",
        f"- Design blocker queue: `{', '.join(summary['design_blocker_queue'])}`",
        f"- Future design target queue: `{', '.join(summary['future_design_target_queue'])}`",
        f"- Closed current targets: `{', '.join(summary['closed_current_targets'])}`",
        "",
        "## Future Design Targets",
        "",
        "| App | Future design target | Boundary |",
        "| --- | --- | --- |",
    ]
    for app in ("barnes_hut", "triangle_counting"):
        row = future[app]
        lines.append(
            f"| `{app}` | {row['next_build_target']} | {row['remaining_gap']} |"
        )
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for name, passed in packet["checks"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No runtime was executed.",
            "- No current route changed.",
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
            {"failed_checks": packet["failed_checks"], "status": "accept" if not packet["failed_checks"] else "reject"},
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not packet["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
