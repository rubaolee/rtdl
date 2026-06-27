from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

M70_REVIEW = ROOT / "docs" / "reviews" / "claude_phoenix_v3_m70_rtnn_focused_protocol_recorded_review_2026-06-23.md"
M71_REVIEW = ROOT / "docs" / "reviews" / "claude_phoenix_v3_m71_rtnn_local_harness_dry_run_gate_recorded_review_2026-06-23.md"

M70_RECOGNIZED_VERDICTS = (
    "accept_m70_protocol_draft_continue_m71_local_harness_no_execution_no_pod",
    "accept_m70_protocol_shape_but_revise_before_harness",
    "blocked_m70_missing_same_contract_or_phase_boundaries",
    "reject_m70_protocol_repeats_leaf_first_or_overclaims",
)

M70_ACCEPT_VERDICTS = (
    "accept_m70_protocol_draft_continue_m71_local_harness_no_execution_no_pod",
)

M71_RECOGNIZED_VERDICTS = (
    "accept_m71_local_dry_run_gate_continue_no_execution_no_pod",
    "revise_m71_dry_run_gate_before_any_harness_work",
    "reject_m71_dry_run_gate_oversteps_no_execution_boundary",
)

M71_ACCEPT_VERDICTS = (
    "accept_m71_local_dry_run_gate_continue_no_execution_no_pod",
)

NON_AUTHORIZATION_PHRASES = (
    "no V3 release",
    "no all-app benchmark run",
    "no POD spend",
    "no paid POD spend",
    "no focused POD spend",
    "no runbook execution",
    "no benchmark execution",
    "no public speedup wording",
    "no broad V3-over-V2 wording",
    "no whole-app speedup wording",
    "no paper reproduction wording",
    "no RT-core speedup wording",
    "no V4 work",
    "no embedding",
    "no C ABI",
    "no true-zero-copy claim",
    "no automatic partner selection",
    "no route-specific RTNN app tuning",
    "no watch-row closure",
)

M70_REQUIRED_TERMS = (
    "frozen",
    "same-contract",
    "uniform",
    "per-distribution",
    "full-batch self-query",
    "0.988781x",
)

M71_REQUIRED_TERMS = (
    "dry-run",
    "input_load",
    "input_pack",
    "hot_query_median",
    "signature_match_status",
    "7",
    "14",
)


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("/", "\\")
    except ValueError:
        return str(path)


def _missing_terms(text: str, terms: tuple[str, ...]) -> list[str]:
    folded = text.lower()
    return [term for term in terms if term.lower() not in folded]


def classify_review(
    milestone: str,
    path: Path,
    recognized_verdicts: tuple[str, ...],
    accept_verdicts: tuple[str, ...],
    required_terms: tuple[str, ...],
) -> dict[str, Any]:
    if not path.exists():
        return {
            "milestone": milestone,
            "path": _rel(path),
            "accepted": False,
            "status": "missing_review_file",
            "verdict": None,
            "reasons": ["missing_review_file"],
        }

    text = path.read_text(encoding="utf-8")
    folded = text.lower()
    verdicts_present = [label for label in recognized_verdicts if label in text]
    missing_non_authorization = _missing_terms(text, NON_AUTHORIZATION_PHRASES)
    missing_required_terms = _missing_terms(text, required_terms)
    reasons: list[str] = []

    if "claude" not in folded:
        reasons.append("missing_claude_reviewer_provenance")
    if len(verdicts_present) != 1:
        reasons.append("missing_or_ambiguous_verdict_label")
    elif verdicts_present[0] not in accept_verdicts:
        reasons.append("non_accept_verdict_requires_revision_or_blocks")
    if missing_non_authorization:
        reasons.append("missing_non_authorization_boundary")
    if missing_required_terms:
        reasons.append("missing_required_answer_terms")
    if "release_ready" in folded:
        reasons.append("contains_release_ready_label")

    return {
        "milestone": milestone,
        "path": _rel(path),
        "accepted": not reasons,
        "status": "accepted" if not reasons else "blocked_or_revise",
        "verdict": verdicts_present[0] if len(verdicts_present) == 1 else None,
        "reasons": reasons,
        "missing_non_authorization": missing_non_authorization,
        "missing_required_terms": missing_required_terms,
    }


def build_payload(m70_review: Path = M70_REVIEW, m71_review: Path = M71_REVIEW) -> dict[str, Any]:
    reviews = [
        classify_review("M70", m70_review, M70_RECOGNIZED_VERDICTS, M70_ACCEPT_VERDICTS, M70_REQUIRED_TERMS),
        classify_review("M71", m71_review, M71_RECOGNIZED_VERDICTS, M71_ACCEPT_VERDICTS, M71_REQUIRED_TERMS),
    ]
    missing = [item for item in reviews if item["status"] == "missing_review_file"]
    accepted = [item for item in reviews if item["accepted"]]

    if missing:
        status = "pending_claude_backfill"
    elif len(accepted) == len(reviews):
        status = "claude_backfill_intake_accept_no_authorization"
    else:
        status = "claude_backfill_intake_blocked_or_revise"

    return {
        "tool": "v3_phoenix_m70_m71_claude_backfill_intake",
        "status": status,
        "review_count": len(reviews),
        "accepted_review_count": len(accepted),
        "missing_review_count": len(missing),
        "reviews": reviews,
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
        "goal_completion_authorized_by_intake_alone": False,
        "next_action": (
            "run_claude_backfill_helper"
            if missing
            else "draft_3ai_consensus_if_all_reviews_accepted"
            if len(accepted) == len(reviews)
            else "revise_or_re-request_claude_backfill"
        ),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Phoenix V3 M70/M71 Claude Backfill Intake",
        "",
        "Date: 2026-06-24",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This intake validates the recorded Claude M70/M71 backfill reviews. It",
        "does not authorize release, all-app runs, POD spend, benchmark execution,",
        "public speedup wording, broad V3-over-V2 wording, or goal completion by",
        "itself.",
        "",
        "## Reviews",
        "",
    ]
    for item in payload["reviews"]:
        lines.extend(
            [
                f"### {item['milestone']}",
                "",
                f"- Path: `{item['path']}`",
                f"- Status: `{item['status']}`",
                f"- Verdict: `{item['verdict']}`",
                f"- Accepted: `{str(item['accepted']).lower()}`",
                f"- Reasons: `{', '.join(item.get('reasons', [])) or 'none'}`",
                "",
            ]
        )
    lines.extend(
        [
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
            "- goal_completion_authorized_by_intake_alone: false",
            "",
            "## Next Action",
            "",
            f"`{payload['next_action']}`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--m70-review", default=str(M70_REVIEW))
    parser.add_argument("--m71-review", default=str(M71_REVIEW))
    parser.add_argument("--json-out")
    parser.add_argument("--md-out")
    parser.add_argument(
        "--allow-non-accepted",
        action="store_true",
        help="Permit pending or blocked intake statuses to exit 0 after writing outputs.",
    )
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
    if payload["status"] != "claude_backfill_intake_accept_no_authorization" and not args.allow_non_accepted:
        sys.exit(1)


if __name__ == "__main__":
    main()
