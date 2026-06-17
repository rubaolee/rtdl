from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rtdsl as rt


OUT_JSON = Path("docs/reports/goal4524_v3_0_m128_benchmark_implementation_queue_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4524_v3_0_m128_benchmark_implementation_queue_2026-06-17.md")


def build_packet() -> dict[str, Any]:
    queue = rt.v3_benchmark_implementation_queue()
    validation = rt.validate_v3_benchmark_implementation_queue(queue)
    return {
        "version": queue["version"],
        "goal": "Goal4524 / V3 M128",
        "status": "benchmark_implementation_queue_checked",
        "date": "2026-06-17",
        "queue_status": queue["status"],
        "summary": queue["summary"],
        "rows": queue["rows"],
        "validation": validation,
        "claim_boundary": {
            "current_route_changed": False,
            "runtime_executed": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
        "conclusion": (
            "M128 turns the post-clean-target app status into a concrete "
            "implementation queue. Goal4527 later fail-closes the naive "
            "Barnes-Hut all-node OptiX any-hit mapping because it cannot "
            "preserve aggregate-subtree skip semantics. Goal4528 then "
            "validates the RT-DBSCAN prepared graph capture gate without changing "
            "the current direct-status component-signature route. Goal4530 "
            "validates Triangle Counting's device key/count payload merge, and "
            "Goal4531 validates device-output weighted replay while fail-closing "
            "CUDA graph capture for that OptiX launch. Goal4539 confirms the "
            "graph capture failure is capture-mode independent, and Goal4540 "
            "accepts the non-graph stream continuation contract for current "
            "Triangle closure while keeping graph/public wording blocked. There is now no runtime "
            "build target in this queue. Goal4533 closes RTNN and Spatial RayJoin as claim-scoped "
            "current targets: their full paper/author wording remains blocked, "
            "but that wording is future optional claim expansion rather than a "
            "current V3 app implementation blocker. Barnes-Hut is the only "
            "remaining future design target rather than a current app "
            "implementation blocker. The other nine apps also have no "
            "immediate V3 runtime blocker."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    summary = packet["summary"]
    rows = packet["rows"]
    lines = [
        "# Goal4524 / V3 M128 Benchmark Implementation Queue",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Summary",
        "",
        f"- Next runtime build target: `{summary['next_runtime_build_target']}`",
        f"- Runtime queue: `{', '.join(summary['runtime_build_queue'])}`",
        f"- Design blocker queue: `{', '.join(summary['design_blocker_queue'])}`",
        f"- Future design target queue: `{', '.join(summary['future_design_target_queue'])}`",
        f"- Claim/evidence queue: `{', '.join(summary['claim_or_evidence_queue'])}`",
        f"- Closed current targets: `{', '.join(summary['closed_current_targets'])}`",
        "",
        "## Queue",
        "",
        "| App | Class | Priority | Remaining gap | Next build target |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in rows:
        priority = "" if row["priority"] is None else str(row["priority"])
        lines.append(
            f"| `{row['app']}` | `{row['work_class']}` | {priority} | "
            f"{row['remaining_gap']} | {row['next_build_target']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No runtime was executed.",
            "- No current route changed.",
            "- No release, public speedup, broad RT-core, paper-reproduction, or automatic partner-selection wording is authorized.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["validation"], indent=2, sort_keys=True))
    return 0 if packet["validation"]["status"] == "accept" else 1


if __name__ == "__main__":
    raise SystemExit(main())
