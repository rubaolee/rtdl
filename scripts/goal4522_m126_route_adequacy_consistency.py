from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.route_adequacy_consistency.goal4522.v3"
OUT_JSON = Path("docs/reports/goal4522_v3_0_m126_route_adequacy_consistency_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4522_v3_0_m126_route_adequacy_consistency_2026-06-17.md")


def _contains_all(text: str, fragments: tuple[str, ...]) -> bool:
    return all(fragment in text for fragment in fragments)


def build_packet() -> dict[str, Any]:
    routes = {row["app"]: row for row in rt.current_benchmark_route_decisions()}
    adequacy = {row["app"]: row for row in rt.current_benchmark_adequacy()}
    checks = {
        "rt_dbscan_route_refs": all(
            ref in routes["rt_dbscan"]["evidence_refs"]
            for ref in ("Goal4519", "Goal4520", "Goal4528")
        ),
        "rt_dbscan_route_wording": _contains_all(
            routes["rt_dbscan"]["current_reader_decision"],
            ("Goal4528", "prepared graph capture/replay", "current route does not change"),
        ),
        "rt_dbscan_adequacy_refs": all(
            ref in adequacy["rt_dbscan"]["evidence_refs"]
            for ref in ("Goal4519", "Goal4520", "Goal4528")
        ),
        "rt_dbscan_adequacy_wording": _contains_all(
            adequacy["rt_dbscan"]["next_generic_runtime_action"],
            ("Goal4528", "prepared graph capture/replay", "current route"),
        ),
        "triangle_route_ref": all(
            ref in routes["triangle_counting"]["evidence_refs"]
            for ref in ("Goal4521", "Goal4530", "Goal4531", "Goal4539", "Goal4540")
        ),
        "triangle_route_wording": _contains_all(
            routes["triangle_counting"]["next_runtime_action"],
            ("Goal4539", "Goal4540", "device-output stream", "future graph wording"),
        ),
        "triangle_adequacy_ref": all(
            ref in adequacy["triangle_counting"]["evidence_refs"]
            for ref in ("Goal4521", "Goal4530", "Goal4531", "Goal4539", "Goal4540")
        ),
        "triangle_adequacy_wording": _contains_all(
            adequacy["triangle_counting"]["next_generic_runtime_action"],
            ("Goal4539", "Goal4540", "device-output stream", "future graph wording"),
        ),
        "barnes_hut_route_refs": all(
            ref in routes["barnes_hut"]["evidence_refs"]
            for ref in ("Goal4497", "Goal4527", "Goal4541")
        ),
        "barnes_hut_route_wording": _contains_all(
            routes["barnes_hut"]["next_runtime_action"],
            ("no immediate V3 build target", "subtree-skip semantics", "future RT-core research"),
        ),
        "barnes_hut_adequacy_refs": all(
            ref in adequacy["barnes_hut"]["evidence_refs"]
            for ref in ("Goal4497", "Goal4527", "Goal4541")
        ),
        "barnes_hut_adequacy_wording": _contains_all(
            adequacy["barnes_hut"]["next_generic_runtime_action"],
            ("no immediate V3 build target", "subtree-skip semantics", "Optional future"),
        ),
        "barnes_hut_no_next_pod": (
            not routes["barnes_hut"]["pod_needed_next"]
            and not adequacy["barnes_hut"]["pod_needed_next"]
        ),
        "route_registry_valid": rt.validate_current_benchmark_route_decisions()["status"] == "accept",
        "adequacy_registry_valid": rt.validate_current_benchmark_adequacy()["status"] == "accept",
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4522 / V3 M126",
        "status": "route_adequacy_consistency_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "route_summary": {
            "rt_dbscan_reader_len": len(routes["rt_dbscan"]["current_reader_decision"]),
            "rt_dbscan_user_guidance_len": len(routes["rt_dbscan"]["user_choice_guidance"]),
            "triangle_refs_tail": routes["triangle_counting"]["evidence_refs"][-6:],
            "barnes_hut_refs_tail": routes["barnes_hut"]["evidence_refs"][-6:],
        },
        "adequacy_summary": {
            "rt_dbscan_refs_tail": adequacy["rt_dbscan"]["evidence_refs"][-6:],
            "triangle_refs_tail": adequacy["triangle_counting"]["evidence_refs"][-6:],
            "barnes_hut_refs_tail": adequacy["barnes_hut"]["evidence_refs"][-6:],
        },
        "claim_boundary": {
            "runtime_executed": False,
            "current_route_changed": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
        "conclusion": (
            "M126 synchronizes the programmatic route-decision and adequacy registries "
            "with the later M132/M133/M134 blocker refinements. RT-DBSCAN now "
            "records Goal4528 fixed-iteration prepared graph capture/replay as "
            "validated for the future M113 shape without changing the current "
            "compact-signature route. Triangle now records Goal4530 key/count "
            "payload merge as validated and Goal4531 weighted replay device-output "
            "stream as valid; Goal4539 records capture-mode-independent graph "
            "failure; and Goal4540 accepts the non-graph stream continuation "
            "contract for current closure while future graph wording remains "
            "blocked. Barnes-Hut now records Goal4541 as a current mixed-explicit "
            "route closure while preserving Goal4527's RT-native subtree-skip "
            "semantic blocker as future optional research/claim expansion."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4522 / V3 M126 Route-Adequacy Consistency",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
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
            "- No public speedup, RT-core speedup, or automatic partner-selection wording is authorized.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps({"failed_checks": packet["failed_checks"], "status": "accept" if not packet["failed_checks"] else "reject"}, indent=2, sort_keys=True))
    return 0 if not packet["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
