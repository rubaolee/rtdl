#!/usr/bin/env python3
"""Build Goal5444 post-ACM exact-input blocker review packet.

Goal5444 consolidates the current full-objective gap matrix, external evidence
chain, public provenance rescan, and ACM access gate into one current-state
packet.  It is a decision/review packet only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP / "results"
OUT = RESULTS / "xhd_goal5444_post_acm_exact_input_blocker_packet.json"

SOURCES = {
    "external_chain": RESULTS / "xhd_goal5440_external_evidence_chain_review_packet.json",
    "full_objective_gap": RESULTS / "xhd_goal5441_full_objective_functional_gap_matrix.json",
    "public_provenance_rescan": RESULTS / "xhd_goal5442_public_provenance_rescan.json",
    "acm_access_gate": RESULTS / "xhd_goal5443_acm_supplement_access_gate.json",
}


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} JSON root is not an object")
    return payload


def build_payload() -> dict[str, Any]:
    data = {name: _load_json(path) for name, path in SOURCES.items()}
    external = data["external_chain"]
    gap = data["full_objective_gap"]
    public = data["public_provenance_rescan"]
    acm = data["acm_access_gate"]

    exact_blocker_removed = bool(
        public["classification"]["exact_input_blocker_removed"]
        or acm["classification"]["exact_input_blocker_removed"]
        or external["claim_boundary"]["exact_equivalence_accepted"]
        or external["claim_boundary"]["external_artifacts_acquired"]
    )
    request_sent = bool(external["claim_boundary"]["request_sent_claimed"])
    response_received = bool(external["claim_boundary"]["external_response_received"])
    planned_gate_count = int(external["summary"]["planned_gate_count"])

    if exact_blocker_removed:
        status = "post_acm_exact_input_blocker_possible_change__strict_next_gate_required"
        next_action = "strictly_review_positive_evidence_then_open_command_ready_same_input_gate"
    elif request_sent or response_received or planned_gate_count:
        status = "post_acm_exact_input_blocker_waiting_on_external_chain_progress"
        next_action = "run_external_response_inbox_and_next_gate_planner_before_pod"
    else:
        status = "post_acm_exact_input_blocker_unchanged__owner_external_action_needed"
        next_action = "owner_send_selected_requests_or_obtain_authorized_acm_access_then_record_receipt_or_intake"

    blockers = [
        {
            "blocker": "exact input artifacts or accepted exact-equivalence evidence",
            "current_state": "not satisfied",
            "evidence": [
                _rel(SOURCES["full_objective_gap"]),
                _rel(SOURCES["public_provenance_rescan"]),
                _rel(SOURCES["acm_access_gate"]),
                _rel(SOURCES["external_chain"]),
            ],
        },
        {
            "blocker": "ACM supplement contents",
            "current_state": "visible but forbidden; not inspected",
            "evidence": [_rel(SOURCES["acm_access_gate"])],
        },
        {
            "blocker": "external request/response chain",
            "current_state": "prepared but not sent; no response; no planned gate",
            "evidence": [_rel(SOURCES["external_chain"])],
        },
        {
            "blocker": "full user objective",
            "current_state": "1 of 14 requirements achieved; full objective incomplete",
            "evidence": [_rel(SOURCES["full_objective_gap"])],
        },
    ]

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5444.post_acm_exact_input_blocker_packet.v1",
        "goal": "Goal5444",
        "date": "2026-07-10",
        "purpose": "Consolidate Goals5440-5443 into the current exact-input blocker node after public and ACM access checks.",
        "status": status,
        "source_artifacts": {name: _rel(path) for name, path in SOURCES.items()},
        "summary": {
            "full_objective_complete": bool(gap["summary"]["full_objective_complete"]),
            "achieved_requirement_count": int(gap["summary"]["achieved_count"]),
            "requirement_count": int(gap["summary"]["requirement_count"]),
            "exact_input_blocker_removed": exact_blocker_removed,
            "new_public_exact_input_artifact_found": bool(public["classification"]["new_public_exact_input_artifact_found"]),
            "acm_current_environment_can_download_zip": bool(acm["classification"]["current_environment_can_download_zip"]),
            "acm_supplement_inspected": bool(acm["classification"]["acm_supplement_inspected"]),
            "ready_external_request_count": int(external["summary"]["ready_external_request_count"]),
            "sent_receipt_count": int(external["summary"]["sent_receipt_count"]),
            "external_response_count": int(external["summary"]["external_response_count"]),
            "planned_gate_count": planned_gate_count,
            "pod_expected_next": False,
        },
        "blocker_rows": blockers,
        "recommended_next_actions": [
            {
                "action": "send_or_review_selected_external_requests_and_record_receipts",
                "when": "owner chooses an external request path",
                "expected_artifact": "valid sent receipt under Paper-reproduction-apps/x-hd-paper/requests/sent",
            },
            {
                "action": "obtain_authorized_acm_access_or_local_zip_then_inspect",
                "when": "ACM access/cookie or ics26-106.zip becomes available",
                "expected_artifact": "normalized ACM supplement intake JSON via inspect_xhd_acm_supplement_zip.py",
            },
            {
                "action": "normalize_external_response_then_run_goal5435_and_goal5437",
                "when": "author/reviewer/ACM response arrives",
                "expected_artifact": "classified response and strict next-gate plan",
            },
        ],
        "not_recommended_next_actions": [
            "POD execution without exact artifact/hash/equivalence response",
            "route micro-optimization",
            "explicit -lb or row/hash parity work",
            "performance ratio work",
            "promoting Level-B scalar evidence to exact paper reproduction",
        ],
        "next_action": next_action,
        "claim_boundary": {
            "post_acm_blocker_packet_claimed": True,
            "exact_input_blocker_removed": exact_blocker_removed,
            "request_sent_claimed": request_sent,
            "external_response_received": response_received,
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
            "gate_non_app_consumer": "post-ACM exact-input blocker packet / reproduction-governance workflow",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: blocker governance, not app-artifact parity implementation.",
        },
        "allowed_summary": (
            "After Goals5440-5443, the X-HD exact-input blocker is unchanged: public/ACM checks "
            "do not provide exact input artifacts, no request is recorded sent, no response exists, "
            "and POD is not the next step."
        ),
        "not_allowed": [
            "claiming exact paper dataset reproduction",
            "claiming Figure 5 or full X-HD reproduction",
            "claiming author-vs-RTDL performance ratio",
            "claiming ACM supplement inspection from forbidden HTML",
            "running POD or route work from this packet",
            "reopening explicit -lb or route micro-optimization as paper-reproduction progress",
        ],
        "exit_label": status,
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "exact_input_blocker_removed": payload["summary"]["exact_input_blocker_removed"],
        "pod_expected_next": payload["summary"]["pod_expected_next"],
        "next_action": payload["next_action"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
