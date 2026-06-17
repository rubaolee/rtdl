from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.completion_review_consensus.goal4538.v1"
OUT_JSON = Path("docs/reports/goal4538_v3_0_m139_v3_completion_review_consensus_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4538_v3_0_m139_v3_completion_review_consensus_2026-06-17.md")

REVIEWERS = (
    {
        "reviewer": "codex_local_self_review",
        "role": "primary_integrator",
        "verdict": "approve_with_caveats",
        "blocking_findings": (),
        "caveat": (
            "Preserve the narrow wording: V3 current benchmark-app implementation "
            "queue complete. This does not authorize release, public performance, "
            "broad RT-core, paper-reproduction, automatic partner-selection, or "
            "app-specific native-engine claims."
        ),
    },
    {
        "reviewer": "harvey_external_review",
        "role": "independent_reviewer",
        "verdict": "approve",
        "blocking_findings": (),
        "caveat": (
            "Barnes-Hut and Triangle are bounded as future design targets rather "
            "than hidden current blockers; RTNN and Spatial RayJoin claim-scope "
            "closure is honest."
        ),
    },
    {
        "reviewer": "pascal_external_review",
        "role": "independent_reviewer",
        "verdict": "approve_with_caveats",
        "blocking_findings": (),
        "caveat": (
            "Do not shorten the claim to generic V3 implementation complete: "
            "Barnes-Hut still needs reviewed hierarchical traversal lowering and "
            "Triangle still needs capture-compatible weighted replay or an "
            "accepted non-graph continuation contract."
        ),
    },
)


def _prior_packet(module_name: str) -> dict[str, Any]:
    module = importlib.import_module(module_name)
    return module.build_packet()


def build_packet() -> dict[str, Any]:
    goal4534 = _prior_packet("scripts.goal4534_m136_v3_current_app_completion_gate")
    goal4535 = _prior_packet("scripts.goal4535_m137_v3_completion_readiness_audit")
    goal4536 = _prior_packet("scripts.goal4536_m138_v3_internal_completion_packet")
    reviewers = tuple(dict(row) for row in REVIEWERS)
    verdicts = tuple(row["verdict"] for row in reviewers)
    blocking_findings = tuple(
        (row["reviewer"], finding)
        for row in reviewers
        for finding in row["blocking_findings"]
    )
    summary = goal4536["summary"]
    checks = {
        "goal4534_current_app_gate_accepts": tuple(goal4534["failed_checks"]) == (),
        "goal4535_readiness_audit_accepts": tuple(goal4535["failed_checks"]) == (),
        "goal4536_completion_packet_accepts": tuple(goal4536["failed_checks"]) == (),
        "three_ai_reviewers_recorded": len(reviewers) == 3,
        "no_blocking_review_findings": not blocking_findings,
        "no_review_requests_changes": "request_changes" not in verdicts,
        "external_reviews_present": {
            row["reviewer"] for row in reviewers if row["role"] == "independent_reviewer"
        }
        == {"harvey_external_review", "pascal_external_review"},
        "consensus_verdict_is_caveated_approve": all(
            verdict in {"approve", "approve_with_caveats"} for verdict in verdicts
        )
        and "approve_with_caveats" in verdicts,
        "runtime_claim_design_queues_empty": tuple(summary["runtime_build_queue"]) == ()
        and tuple(summary["claim_or_evidence_queue"]) == ()
        and tuple(summary["design_blocker_queue"]) == (),
        "goal4540_successor_future_design_targets_preserved": tuple(
            summary["future_design_target_queue"]
        )
        == ("barnes_hut",),
        "goal4540_successor_closed_current_target_count_preserved": len(
            summary["closed_current_targets"]
        )
        == 9,
        "goal4540_successor_triangle_closed_without_graph_claim": (
            "triangle_counting" in summary["closed_current_targets"]
            and not goal4536["claim_boundary"]["paper_reproduction_claim_authorized"]
            and not goal4536["claim_boundary"]["broad_rt_core_claim_authorized"]
        ),
        "release_and_public_claims_still_blocked": not any(
            goal4536["claim_boundary"][name]
            for name in (
                "release_authorized",
                "public_speedup_claim_authorized",
                "broad_rt_core_claim_authorized",
                "paper_reproduction_claim_authorized",
                "automatic_partner_selection_authorized",
                "app_specific_native_engine_logic_allowed",
            )
        ),
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4538 / V3 M139",
        "status": "completion_review_consensus_checked",
        "date": "2026-06-17",
        "source_packets": {
            "goal4534": goal4534["version"],
            "goal4535": goal4535["version"],
            "goal4536": goal4536["version"],
        },
        "reviewers": reviewers,
        "consensus_verdict": "approve_with_caveats",
        "checks": checks,
        "failed_checks": failed,
        "summary": summary,
        "claim_boundary": goal4536["claim_boundary"],
        "conclusion": (
            "The 3-AI review consensus accepts the narrow Goal4536 conclusion: "
            "the V3 current benchmark-app implementation queue is complete. "
            "Goal4540 later supersedes the Triangle future-design classification "
            "by explicitly accepting the non-graph stream device-output "
            "continuation contract, so the current queue has empty runtime, "
            "claim/evidence, and current design-blocker queues; nine apps are "
            "closed current targets; and Barnes-Hut is the only remaining future "
            "design target. "
            "The consensus does not authorize release, public speedup, broad "
            "RT-core, paper-reproduction, automatic partner-selection, or "
            "app-specific native-engine claims."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4538 / V3 M139 Completion Review Consensus",
        "",
        f"Status: `{packet['status']}`",
        f"Consensus verdict: `{packet['consensus_verdict']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Reviewer Verdicts",
        "",
        "| Reviewer | Role | Verdict | Blocking findings | Caveat |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in packet["reviewers"]:
        findings = ", ".join(row["blocking_findings"]) or "none"
        lines.append(
            f"| `{row['reviewer']}` | `{row['role']}` | `{row['verdict']}` | "
            f"{findings} | {row['caveat']} |"
        )
    summary = packet["summary"]
    lines.extend(
        [
            "",
            "## Queue State Preserved",
            "",
            f"- Runtime queue: `{', '.join(summary['runtime_build_queue'])}`",
            f"- Claim/evidence queue: `{', '.join(summary['claim_or_evidence_queue'])}`",
            f"- Design blocker queue: `{', '.join(summary['design_blocker_queue'])}`",
            f"- Future design targets: `{', '.join(summary['future_design_target_queue'])}`",
            f"- Closed current targets: `{', '.join(summary['closed_current_targets'])}`",
            "- Goal4540 successor note: `triangle_counting` is closed only through the non-graph stream continuation contract; M113 graph wording remains blocked.",
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
            "- The accepted wording is exactly scoped to V3 current benchmark-app implementation queue complete.",
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
