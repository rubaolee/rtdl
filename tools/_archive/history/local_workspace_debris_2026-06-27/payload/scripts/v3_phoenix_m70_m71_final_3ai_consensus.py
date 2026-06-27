from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts import v3_phoenix_m70_m71_claude_backfill_intake as intake
from scripts import v3_phoenix_m70_m71_goal_completion_audit as audit


ROOT = Path(__file__).resolve().parents[1]

ANTIGRAVITY_REVIEWS = (
    ROOT / "docs" / "reviews" / "antigravity_phoenix_v3_m70_rtnn_focused_protocol_review_2026-06-23.md",
    ROOT / "docs" / "reviews" / "antigravity_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_review_2026-06-23.md",
    ROOT / "docs" / "reviews" / "antigravity_phoenix_v3_m70_m71_backfill_packet_intake_review_2026-06-24.md",
)


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("/", "\\")
    except ValueError:
        return str(path)


def build_payload(
    m70_review: Path = intake.M70_REVIEW,
    m71_review: Path = intake.M71_REVIEW,
) -> dict[str, Any]:
    intake_payload = intake.build_payload(m70_review, m71_review)
    audit_payload = audit.build_payload(m70_review, m71_review)
    antigravity = [{"path": _rel(path), "exists": path.exists()} for path in ANTIGRAVITY_REVIEWS]
    antigravity_ready = all(item["exists"] for item in antigravity)
    claude_ready = intake_payload["status"] == "claude_backfill_intake_accept_no_authorization"
    audit_ready = audit_payload["goal_completion_ready_for_final_3ai_consensus"]

    if claude_ready and audit_ready and antigravity_ready:
        status = "m70_m71_final_3ai_consensus_ready_to_record_no_authorization"
    else:
        status = "m70_m71_final_3ai_consensus_pending"

    return {
        "tool": "v3_phoenix_m70_m71_final_3ai_consensus",
        "status": status,
        "claude_ready": claude_ready,
        "antigravity_ready": antigravity_ready,
        "audit_ready": audit_ready,
        "reviewers": ["codex", "claude", "antigravity"],
        "required_claude_reviews": [_rel(m70_review), _rel(m71_review)],
        "antigravity_reviews": antigravity,
        "intake_status": intake_payload["status"],
        "audit_status": audit_payload["status"],
        "release_authorized": False,
        "all_app_authorized": False,
        "pod_spend_authorized": False,
        "paid_pod_spend_authorized": False,
        "focused_pod_spend_authorized": False,
        "runbook_execution_authorized": False,
        "benchmark_execution_authorized": False,
        "public_speedup_wording_authorized": False,
        "broad_v3_over_v2_wording_authorized": False,
        "whole_app_speedup_wording_authorized": False,
        "paper_reproduction_wording_authorized": False,
        "rt_core_speedup_wording_authorized": False,
        "v4_work_authorized": False,
        "embedding_authorized": False,
        "c_abi_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "route_specific_rtnn_app_tuning_authorized": False,
        "watch_row_closure_authorized": False,
        "goal_completion_authorized_by_builder": False,
        "goal_completion_ready_for_human_record": status.endswith("ready_to_record_no_authorization"),
        "decision_audit": {
            "was_i_foolish": "No. This builder records readiness only after the three review seats exist.",
            "if_yes_actions": "Not applicable.",
            "other_path": "Manually write the final consensus, but that is easier to overclaim.",
            "different_path": "Use this builder after Claude accepts, then write the final consensus record.",
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Phoenix V3 M70/M71 Final 3AI Consensus Builder",
        "",
        "Date: 2026-06-24",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This is a fail-closed readiness builder. It does not by itself complete",
        "M70/M71 and does not authorize release, all-app runs, POD spend,",
        "benchmark execution, public speedup wording, or broad V3-over-V2 wording.",
        "",
        "## Readiness",
        "",
        f"- claude_ready: `{str(payload['claude_ready']).lower()}`",
        f"- antigravity_ready: `{str(payload['antigravity_ready']).lower()}`",
        f"- audit_ready: `{str(payload['audit_ready']).lower()}`",
        f"- goal_completion_ready_for_human_record: `{str(payload['goal_completion_ready_for_human_record']).lower()}`",
        "",
        "## Authorization Flags",
        "",
        "- release_authorized: false",
        "- all_app_authorized: false",
        "- pod_spend_authorized: false",
        "- paid_pod_spend_authorized: false",
        "- focused_pod_spend_authorized: false",
        "- runbook_execution_authorized: false",
        "- benchmark_execution_authorized: false",
        "- public_speedup_wording_authorized: false",
        "- broad_v3_over_v2_wording_authorized: false",
        "- whole_app_speedup_wording_authorized: false",
        "- paper_reproduction_wording_authorized: false",
        "- rt_core_speedup_wording_authorized: false",
        "- v4_work_authorized: false",
        "- embedding_authorized: false",
        "- c_abi_authorized: false",
        "- true_zero_copy_claim_authorized: false",
        "- automatic_partner_selection_authorized: false",
        "- route_specific_rtnn_app_tuning_authorized: false",
        "- watch_row_closure_authorized: false",
        "- goal_completion_authorized_by_builder: false",
        "",
        "## Goal-Level Decision Audit",
        "",
        f"1. Was I foolish? {payload['decision_audit']['was_i_foolish']}",
        f"2. If yes, what actions made it foolish? {payload['decision_audit']['if_yes_actions']}",
        f"3. Was there another path? {payload['decision_audit']['other_path']}",
        f"4. Can I now try a different path? {payload['decision_audit']['different_path']}",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--m70-review", default=str(intake.M70_REVIEW))
    parser.add_argument("--m71-review", default=str(intake.M71_REVIEW))
    parser.add_argument("--json-out")
    parser.add_argument("--md-out")
    args = parser.parse_args()

    payload = build_payload(Path(args.m70_review), Path(args.m71_review))
    print(json.dumps(payload, indent=2, sort_keys=True))
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.md_out:
        out = Path(args.md_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_markdown(payload), encoding="utf-8")


if __name__ == "__main__":
    main()
