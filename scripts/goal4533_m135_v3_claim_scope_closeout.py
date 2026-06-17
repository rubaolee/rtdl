from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.claim_scope_closeout.goal4533.v1"
OUT_JSON = Path("docs/reports/goal4533_v3_0_m135_v3_claim_scope_closeout_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4533_v3_0_m135_v3_claim_scope_closeout_2026-06-17.md")


def build_packet() -> dict[str, Any]:
    queue = rt.v3_benchmark_implementation_queue()
    validation = rt.validate_v3_benchmark_implementation_queue(queue)
    rows = {row["app"]: row for row in queue["rows"]}
    summary = queue["summary"]
    checks = {
        "queue_validates": validation["status"] == "accept",
        "runtime_queue_empty": tuple(summary["runtime_build_queue"]) == (),
        "claim_queue_empty": tuple(summary["claim_or_evidence_queue"]) == (),
        "design_queue_exact": tuple(summary["design_blocker_queue"])
        == ("barnes_hut", "triangle_counting"),
        "closed_count_is_eight": len(summary["closed_current_targets"]) == 8,
        "rtnn_closed_claim_scoped": (
            rows["rtnn"]["work_class"] == "closed_current_target"
            and not rows["rtnn"]["paper_reproduction_claim_authorized"]
            and not rows["rtnn"]["public_speedup_claim_authorized"]
            and "future optional claim-expansion" in rows["rtnn"]["remaining_gap"]
        ),
        "spatial_rayjoin_closed_claim_scoped": (
            rows["spatial_rayjoin"]["work_class"] == "closed_current_target"
            and not rows["spatial_rayjoin"]["paper_reproduction_claim_authorized"]
            and not rows["spatial_rayjoin"]["public_speedup_claim_authorized"]
            and "future optional claim-expansion" in rows["spatial_rayjoin"]["remaining_gap"]
        ),
        "all_public_speedup_claims_blocked": summary["all_public_speedup_claims_blocked"],
        "all_broad_rt_core_claims_blocked": summary["all_broad_rt_core_claims_blocked"],
        "all_paper_reproduction_claims_blocked": summary["all_paper_reproduction_claims_blocked"],
        "all_automatic_partner_selection_blocked": summary[
            "all_automatic_partner_selection_blocked"
        ],
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4533 / V3 M135",
        "status": "claim_scope_closeout_checked",
        "date": "2026-06-17",
        "queue_version": queue["version"],
        "queue_status": queue["status"],
        "checks": checks,
        "failed_checks": failed,
        "summary": summary,
        "closed_claim_scoped_apps": {
            "rtnn": rows["rtnn"],
            "spatial_rayjoin": rows["spatial_rayjoin"],
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
            "Goal4533 closes RTNN and Spatial RayJoin as V3 current app targets "
            "without expanding claims. RTNN exact paper reproduction and same-output "
            "author comparison remain future optional claim-expansion work; Spatial "
            "RayJoin full RayJoin paper reproduction and Section 5.7 8/8 overlay "
            "wording remain future optional claim-expansion work. The V3 implementation "
            "queue now has no runtime blocker and no claim/evidence blocker; only "
            "Barnes-Hut and Triangle Counting remain design blockers, and none of "
            "the public speedup, broad RT-core, paper-reproduction, or automatic "
            "partner-selection claims are authorized."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    summary = packet["summary"]
    rows = packet["closed_claim_scoped_apps"]
    lines = [
        "# Goal4533 / V3 M135 Claim-Scope Closeout",
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
        f"- Closed current targets: `{', '.join(summary['closed_current_targets'])}`",
        "",
        "## Closed Claim-Scoped Apps",
        "",
        "| App | Current route status | Remaining claim boundary |",
        "| --- | --- | --- |",
    ]
    for app in ("rtnn", "spatial_rayjoin"):
        row = rows[app]
        lines.append(
            f"| `{app}` | {row['current_route_status']} | {row['remaining_gap']} |"
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
