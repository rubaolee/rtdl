from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.major_performance_target_refresh.goal4543.v1"
OUT_JSON = Path(
    "docs/reports/goal4543_v3_0_m144_major_performance_target_refresh_2026-06-17.json"
)
OUT_REPORT = Path(
    "docs/reports/goal4543_v3_0_m144_major_performance_target_refresh_2026-06-17.md"
)


def build_packet() -> dict[str, Any]:
    rows = rt.current_major_performance_targets()
    validation = rt.validate_current_major_performance_targets(rows)
    summary = rt.summarize_current_major_performance_targets(rows)
    by_id = {row["target_id"]: row for row in rows}
    app_queue = rt.v3_benchmark_implementation_queue()
    app_summary = app_queue["summary"]
    checks = {
        "target_map_validates": validation["status"] == "accept",
        "target_map_version_is_goal4543": summary["version"]
        == "rtdl.v3_0.current_major_performance_targets.goal4543.v1",
        "app_queue_validates": rt.validate_v3_benchmark_implementation_queue(app_queue)[
            "status"
        ]
        == "accept",
        "app_queue_all_ten_closed": len(app_summary["closed_current_targets"]) == 10,
        "app_queue_future_design_empty": tuple(app_summary["future_design_target_queue"]) == (),
        "ten_app_health_cites_goal4542": (
            "Goal4542" in by_id["ten_app_current_route_health"]["evidence_refs"]
            and "post-closure" in by_id["ten_app_current_route_health"]["next_action"]
        ),
        "release_grade_is_conditional_not_immediate_pod": (
            by_id["release_grade_long_run_packet"]["target_status"] == "needs_broader_evidence"
            and "Goal4542" in by_id["release_grade_long_run_packet"]["evidence_refs"]
            and not by_id["release_grade_long_run_packet"]["pod_needed_next"]
        ),
        "amd_hardware_blocked_not_immediate_pod": (
            by_id["amd_hiprt_functional_parity"]["target_status"] == "blocked_pending_hardware"
            and by_id["amd_hiprt_functional_parity"]["amd_hardware_needed"]
            and not by_id["amd_hiprt_functional_parity"]["pod_needed_next"]
        ),
        "major_release_pending_user_decision": (
            by_id["major_release_candidate_packet"]["target_status"]
            == "pending_user_release_decision"
            and "Goal4542" in by_id["major_release_candidate_packet"]["evidence_refs"]
        ),
        "no_immediate_pod_targets": tuple(summary["pod_needed_next_targets"]) == (),
        "release_and_public_claims_blocked": not any(
            summary[name]
            for name in (
                "release_authorized",
                "public_speedup_claim_authorized",
                "whole_app_speedup_claim_authorized",
                "broad_rt_core_claim_authorized",
                "paper_reproduction_claim_authorized",
                "rtdl_beats_rayjoin_claim_authorized",
                "true_zero_copy_claim_authorized",
                "automatic_partner_selection_authorized",
                "app_specific_native_engine_logic_allowed",
            )
        ),
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4543 / V3 M144",
        "status": "major_performance_target_refresh_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "target_summary": summary,
        "target_rows": rows,
        "app_queue_summary": app_summary,
        "claim_boundary": {
            "runtime_executed": False,
            "current_route_changed": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        },
        "conclusion": (
            "Goal4543 refreshes the major performance target map after Goal4542. "
            "The V3 app surface is internally closed, and the target map no longer "
            "lists any immediate pod-needed targets. Release-grade validation, "
            "public performance tables, AMD/HIPRT parity, and future RT-native "
            "Barnes-Hut traversal remain conditional future gates, not current "
            "pod work and not authorized claims."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    summary = packet["target_summary"]
    lines = [
        "# Goal4543 / V3 M144 Major Performance Target Refresh",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Target Summary",
        "",
        f"- Target count: `{summary['target_count']}`",
        f"- Immediate pod-needed targets: `{', '.join(summary['pod_needed_next_targets'])}`",
        f"- AMD hardware-needed targets: `{', '.join(summary['amd_hardware_needed_targets'])}`",
        f"- Needs broader evidence count: `{summary['needs_broader_evidence_count']}`",
        f"- Blocked pending hardware count: `{summary['blocked_pending_hardware_count']}`",
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
            "- No release, public speedup, broad RT-core, paper-reproduction, automatic partner-selection, true-zero-copy, RTDL-beats-RayJoin, or app-specific native-engine wording is authorized.",
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
