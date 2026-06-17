from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.internal_completion_packet.goal4536.v1"
OUT_JSON = Path("docs/reports/goal4536_v3_0_m138_v3_internal_completion_packet_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4536_v3_0_m138_v3_internal_completion_packet_2026-06-17.md")


def _app_rows() -> tuple[dict[str, Any], ...]:
    queue = rt.v3_benchmark_implementation_queue()
    routes = {row["app"]: row for row in rt.current_benchmark_route_decisions()}
    adequacy = {row["app"]: row for row in rt.current_benchmark_adequacy()}
    rows = []
    for row in queue["rows"]:
        app = row["app"]
        route = routes[app]
        adequate = adequacy[app]
        rows.append(
            {
                "app": app,
                "queue_class": row["work_class"],
                "current_route_status": row["current_route_status"],
                "route_decision_kind": route["decision_kind"],
                "partner_policy": route["partner_policy"],
                "adequacy": adequate["adequacy"],
                "current_recommended_path": adequate["current_recommended_path"],
                "remaining_gap": row["remaining_gap"],
                "next_or_future_target": row["next_build_target"],
                "evidence_refs": row["evidence_refs"],
                "public_speedup_claim_authorized": row["public_speedup_claim_authorized"],
                "broad_rt_core_claim_authorized": row["broad_rt_core_claim_authorized"],
                "paper_reproduction_claim_authorized": row["paper_reproduction_claim_authorized"],
                "automatic_partner_selection_authorized": row[
                    "automatic_partner_selection_authorized"
                ],
                "app_specific_native_engine_logic_allowed": row[
                    "app_specific_native_engine_logic_allowed"
                ],
            }
        )
    return tuple(rows)


def build_packet() -> dict[str, Any]:
    queue = rt.v3_benchmark_implementation_queue()
    validation = rt.validate_v3_benchmark_implementation_queue(queue)
    rows = _app_rows()
    apps = {row["app"] for row in rows}
    summary = queue["summary"]
    checks = {
        "queue_validates": validation["status"] == "accept",
        "all_ten_apps_present": len(apps) == 10,
        "runtime_queue_empty": tuple(summary["runtime_build_queue"]) == (),
        "claim_queue_empty": tuple(summary["claim_or_evidence_queue"]) == (),
        "design_blocker_queue_empty": tuple(summary["design_blocker_queue"]) == (),
        "future_design_queue_empty_after_goal4541": tuple(
            summary["future_design_target_queue"]
        )
        == (),
        "closed_current_target_count_is_ten": len(summary["closed_current_targets"]) == 10,
        "all_routes_have_adequacy": all(row["adequacy"] for row in rows),
        "all_public_speedup_claims_blocked": not any(
            row["public_speedup_claim_authorized"] for row in rows
        ),
        "all_broad_rt_core_claims_blocked": not any(
            row["broad_rt_core_claim_authorized"] for row in rows
        ),
        "all_paper_reproduction_claims_blocked": not any(
            row["paper_reproduction_claim_authorized"] for row in rows
        ),
        "all_automatic_partner_selection_blocked": not any(
            row["automatic_partner_selection_authorized"] for row in rows
        ),
        "all_app_specific_native_engine_logic_blocked": not any(
            row["app_specific_native_engine_logic_allowed"] for row in rows
        ),
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4536 / V3 M138",
        "status": "internal_completion_packet_checked",
        "date": "2026-06-17",
        "queue_version": queue["version"],
        "queue_status": queue["status"],
        "checks": checks,
        "failed_checks": failed,
        "summary": summary,
        "app_rows": rows,
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
            "Goal4536 packages the V3.0 current benchmark-app implementation state. "
            "All ten apps are accounted for. Runtime, claim/evidence, and current "
            "design-blocker queues are empty. After Goal4540 accepts Triangle's "
            "non-graph stream continuation contract and Goal4541 closes Barnes-Hut "
            "as a current mixed-explicit route target, all ten apps are closed "
            "current targets and the future-design queue is empty. The packet "
            "does not authorize release or public performance claims: broad RT-core, "
            "paper-reproduction, automatic partner-selection, and app-specific "
            "native-engine claims remain blocked."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    summary = packet["summary"]
    lines = [
        "# Goal4536 / V3 M138 Internal Completion Packet",
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
        "## App Matrix",
        "",
        "| App | Class | Route kind | Partner policy | Adequacy | Next/future target |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in packet["app_rows"]:
        lines.append(
            f"| `{row['app']}` | `{row['queue_class']}` | "
            f"`{row['route_decision_kind']}` | `{row['partner_policy']}` | "
            f"`{row['adequacy']}` | {row['next_or_future_target']} |"
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
