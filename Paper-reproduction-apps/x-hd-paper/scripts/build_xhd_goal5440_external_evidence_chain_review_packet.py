#!/usr/bin/env python3
"""Build the Goal5440 X-HD external evidence-chain review packet.

This consolidates Goals5433-5439 into one machine-readable status for external
review. It does not send requests, read private correspondence, run POD, run
author code, run RTDL routes, or upgrade reproduction claims.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP / "results"
HISTORY = ROOT / "history" / "internal_docs"
OUT = RESULTS / "xhd_goal5440_external_evidence_chain_review_packet.json"
REVIEW_MD = HISTORY / "call_for_review_goals5433_5439_xhd_external_evidence_chain_2026-07-10.md"


GOAL_RESULTS = {
    "Goal5433": RESULTS / "xhd_goal5433_water_bg_external_response_classifier_contract.json",
    "Goal5434": RESULTS / "xhd_goal5434_water_bg_external_action_packet.json",
    "Goal5435": RESULTS / "xhd_goal5435_external_response_inbox_gate.json",
    "Goal5436": RESULTS / "xhd_goal5436_full_reproduction_readiness_matrix.json",
    "Goal5437": RESULTS / "xhd_goal5437_external_response_next_gate_plan.json",
    "Goal5438": RESULTS / "xhd_goal5438_external_request_send_manifest.json",
    "Goal5439": RESULTS / "xhd_goal5439_external_request_sent_receipt_gate.json",
}


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} JSON root is not an object")
    return payload


def _claim_false(payload: dict[str, Any], key: str) -> bool:
    return payload.get("claim_boundary", {}).get(key) is False


def _collect_goal_statuses(results: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for goal, path in GOAL_RESULTS.items():
        payload = results[goal]
        rows.append(
            {
                "goal": goal,
                "path": _rel(path),
                "status": payload.get("status"),
                "pod_used": payload.get("pod_usage", {}).get("used"),
                "pod_expected_next": payload.get("pod_usage", {}).get("expected_next"),
                "claim_boundary": payload.get("claim_boundary", {}),
                "stop_loss_gate": payload.get("stop_loss_gate", {}),
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    results = {goal: _load_json(path) for goal, path in GOAL_RESULTS.items()}
    goal_statuses = _collect_goal_statuses(results)

    readiness = results["Goal5436"]
    inbox = results["Goal5435"]
    next_gate = results["Goal5437"]
    send_manifest = results["Goal5438"]
    sent_receipt = results["Goal5439"]

    response_count = int(inbox.get("response_count", 0))
    receipt_count = int(sent_receipt.get("receipt_count", 0))
    planned_gate_count = int(next_gate.get("planned_gate_count", 0))
    ready_external_request_count = len(send_manifest.get("ready_external_request_ids", []))

    all_no_pod = all(row["pod_used"] is False for row in goal_statuses)
    all_no_claims = all(
        _claim_false(results[goal], key)
        for goal in results
        for key in [
            "exact_paper_dataset_reproduction_claimed",
            "figure5_reproduction_claimed",
            "performance_ratio_claimed",
            "pod_execution_claimed",
        ]
        if key in results[goal].get("claim_boundary", {})
    )
    full_ready = readiness.get("full_xhd_paper_reproduction_ready") is True

    if response_count:
        status = "external_evidence_chain_has_responses__review_classifier_before_gate"
        next_action = "strictly_review_goal5435_and_goal5437_outputs_before_any_pod_or_claim"
    elif receipt_count:
        status = "external_evidence_chain_has_sent_receipts__await_response_intake"
        next_action = "normalize_any_external_response_then_run_goal5435_and_goal5437"
    else:
        status = "external_evidence_chain_prepared_not_sent__await_owner_or_external_action"
        next_action = "owner_send_selected_requests_record_receipts_then_run_goal5439"

    payload = {
        "schema": "rtdl.paper_reproduction.xhd.goal5440.external_evidence_chain_review_packet.v1",
        "goal": "Goal5440",
        "date": "2026-07-10",
        "status": status,
        "goals_covered": list(GOAL_RESULTS.keys()),
        "goal_statuses": goal_statuses,
        "summary": {
            "ready_external_request_count": ready_external_request_count,
            "sent_receipt_count": receipt_count,
            "external_response_count": response_count,
            "positive_classifier_outcome_count": inbox.get("positive_classifier_outcome_count", 0),
            "planned_gate_count": planned_gate_count,
            "full_xhd_paper_reproduction_ready": full_ready,
            "pod_expected_next": False,
            "pod_used_anywhere_in_chain": not all_no_pod,
            "claim_boundaries_preserved": all_no_claims,
        },
        "chain_state": {
            "classifier_ready": results["Goal5433"].get("status"),
            "action_packet_ready": results["Goal5434"].get("status"),
            "inbox_status": inbox.get("status"),
            "readiness_status": readiness.get("status"),
            "next_gate_plan_status": next_gate.get("status"),
            "send_manifest_status": send_manifest.get("status"),
            "sent_receipt_status": sent_receipt.get("status"),
        },
        "review_focus": [
            "Verify that a prepared request is not treated as a sent request.",
            "Verify that a sent receipt is not treated as an external response.",
            "Verify that a positive classifier outcome would require strict review before POD.",
            "Verify that no exact/full/performance claim is made anywhere in the chain.",
            "Verify that route micro-optimization and explicit -lb remain closed while exact input evidence is absent.",
        ],
        "next_action": next_action,
        "pod_usage": {
            "used": False,
            "expected_next": False,
            "reason": "Review packet only. POD is opened only after a positive classified response and strict next-gate review.",
        },
        "claim_boundary": {
            "external_evidence_chain_review_packet_claimed": True,
            "request_send_manifest_claimed": True,
            "request_sent_claimed": sent_receipt.get("claim_boundary", {}).get("request_sent_claimed") is True,
            "external_response_received": response_count > 0,
            "external_artifacts_acquired": False,
            "exact_equivalence_accepted": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "pod_execution_claimed": False,
            "new_rtdl_route_code_added": False,
            "explicit_lb_reopened": False,
            "route_micro_optimization_goal_authorized": False,
        },
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": "external evidence-chain review packet / provenance governance workflow",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: review governance, not app-artifact parity implementation.",
        },
        "not_allowed": [
            "claiming a request was sent from a prepared manifest alone",
            "claiming a response arrived from a sent receipt alone",
            "claiming exact-equivalence accepted without external response classification and strict review",
            "claiming exact paper dataset reproduction",
            "claiming Figure 5 or full X-HD paper reproduction",
            "claiming author-vs-RTDL performance ratio",
            "running POD or route work from this review packet",
            "reopening route micro-optimization or explicit -lb while exact input evidence is absent",
        ],
    }
    return payload


def _write_review_md(payload: dict[str, Any]) -> None:
    lines = [
        "# Call For Review - Goals5433-5439 X-HD External Evidence Chain",
        "",
        "Please strictly review the X-HD external evidence chain from Goals5433-5439.",
        "",
        "## Files Under Review",
        "",
        "```text",
    ]
    for row in payload["goal_statuses"]:
        lines.append(row["path"])
    lines.extend(
        [
            "Paper-reproduction-apps/x-hd-paper/results/xhd_goal5440_external_evidence_chain_review_packet.json",
            "```",
            "",
            "## Current Consolidated State",
            "",
            "```text",
            f"status = {payload['status']}",
            f"ready_external_request_count = {payload['summary']['ready_external_request_count']}",
            f"sent_receipt_count = {payload['summary']['sent_receipt_count']}",
            f"external_response_count = {payload['summary']['external_response_count']}",
            f"positive_classifier_outcome_count = {payload['summary']['positive_classifier_outcome_count']}",
            f"planned_gate_count = {payload['summary']['planned_gate_count']}",
            f"full_xhd_paper_reproduction_ready = {str(payload['summary']['full_xhd_paper_reproduction_ready']).lower()}",
            f"pod_expected_next = {str(payload['summary']['pod_expected_next']).lower()}",
            "```",
            "",
            "## Claim Boundary",
            "",
            "```text",
            "request_sent_claimed = false",
            "external_response_received = false",
            "external_artifacts_acquired = false",
            "exact_equivalence_accepted = false",
            "exact_paper_dataset_reproduction_claimed = false",
            "figure5_reproduction_claimed = false",
            "full_xhd_paper_reproduction_claimed = false",
            "performance_ratio_claimed = false",
            "pod_execution_claimed = false",
            "explicit_lb_reopened = false",
            "route_micro_optimization_goal_authorized = false",
            "```",
            "",
            "## Review Questions",
            "",
            "1. Does the chain correctly distinguish prepared requests, sent receipts, incoming responses, classifier outcomes, next-gate plans, and POD execution?",
            "2. Does it correctly forbid treating a prepared request as sent, or a sent receipt as a response?",
            "3. Does a positive classifier outcome, if one later appears, require strict review before POD or claim changes?",
            "4. Does the readiness matrix correctly keep full X-HD reproduction false until exact/accepted inputs and same-input gates exist?",
            "5. Are all exact/full/Figure/performance/POD claims false in the current state?",
            "6. Does the packet keep route micro-optimization and explicit -lb closed while exact input evidence is absent?",
            "7. Does the stop-loss gate pass as governance infrastructure rather than app-artifact parity work?",
            "8. Is the next action correct: owner sends selected requests, records sent receipts, then any reply is normalized into requests/incoming before Goal5435/5437?",
            "",
            "## Requested Verdict Labels",
            "",
            "Approve:",
            "",
            "```text",
            "approve_goals5433_5439_external_evidence_chain_fail_closed",
            "```",
            "",
            "Revise:",
            "",
            "```text",
            "revise_goals5433_5439_external_evidence_chain_before_dispatch_or_response_gate",
            "```",
            "",
            "Block:",
            "",
            "```text",
            "block_goals5433_5439_external_evidence_chain_overclaims_or_skips_gate",
            "```",
            "",
            "## Expected Answer Shape",
            "",
            "```text",
            "Verdict:",
            "",
            "Blocking findings:",
            "",
            "Required amendments:",
            "",
            "Non-blocking notes:",
            "",
            "Answers to review questions:",
            "```",
        ]
    )
    REVIEW_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_review_md(payload)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "ready_external_request_count": payload["summary"]["ready_external_request_count"],
                "sent_receipt_count": payload["summary"]["sent_receipt_count"],
                "external_response_count": payload["summary"]["external_response_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
