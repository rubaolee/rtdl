#!/usr/bin/env python3
"""Build Goal5447 current X-HD external blocker state.

Goal5447 supersedes the older Goal5444 current-state packet by also including
the Goal5445 dispatch bundle and Goal5446 artifact dropbox gate.

It is a review/decision packet only. It does not send requests, inspect
responses, inspect archives, run POD, run author code, run RTDL routes, or
upgrade any reproduction claim.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP / "results"
OUT = RESULTS / "xhd_goal5447_current_external_blocker_state.json"

SOURCES = {
    "post_acm_blocker_packet": RESULTS / "xhd_goal5444_post_acm_exact_input_blocker_packet.json",
    "external_action_dispatch_bundle": RESULTS / "xhd_goal5445_external_action_dispatch_bundle.json",
    "external_artifact_dropbox_gate": RESULTS / "xhd_goal5446_external_artifact_dropbox_gate.json",
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
    blocker = data["post_acm_blocker_packet"]
    dispatch = data["external_action_dispatch_bundle"]
    dropbox = data["external_artifact_dropbox_gate"]

    exact_input_blocker_removed = bool(
        blocker["summary"]["exact_input_blocker_removed"]
        or dispatch["exact_input_blocker_removed"]
        or dropbox["exact_input_blocker_removed"]
    )
    request_sent = bool(
        blocker["claim_boundary"]["request_sent_claimed"]
        or dispatch["request_sent_claimed"]
    )
    response_received = bool(
        blocker["claim_boundary"]["external_response_received"]
        or dispatch["external_response_received"]
    )
    artifact_candidates = int(dropbox["artifact_candidate_count"])
    artifacts_acquired = bool(dropbox["external_artifacts_acquired"])

    if exact_input_blocker_removed:
        status = "current_external_blocker_possible_change__strict_next_gate_required"
        next_action = "strictly_review_positive_exact_input_or_equivalence_evidence_before_pod"
    elif artifact_candidates:
        status = "current_external_blocker_artifact_candidates_present__run_intake_gate"
        next_action = "run_dropbox_record_specific_intake_gate_before_any_pod"
    elif request_sent or response_received:
        status = "current_external_blocker_external_chain_progress__run_receipt_or_response_gate"
        next_action = "run_sent_receipt_or_external_response_gate_before_any_pod"
    else:
        status = "current_external_blocker_waiting_on_owner_or_external_action"
        next_action = "owner_send_request_or_place_authorized_artifact_or_wait_for_response"

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5447.current_external_blocker_state.v1",
        "goal": "Goal5447",
        "date": "2026-07-10",
        "purpose": "Consolidate the post-ACM blocker, external dispatch bundle, and artifact dropbox gate into the current X-HD external blocker node.",
        "status": status,
        "source_artifacts": {name: _rel(path) for name, path in SOURCES.items()},
        "summary": {
            "full_objective_complete": False,
            "exact_input_blocker_removed": exact_input_blocker_removed,
            "ready_external_request_count": int(dispatch["ready_external_request_count"]),
            "receipt_stub_count": int(dispatch["receipt_stub_count"]),
            "request_sent_claimed": request_sent,
            "external_response_received": response_received,
            "external_artifact_candidate_count": artifact_candidates,
            "external_artifacts_acquired": artifacts_acquired,
            "pod_expected_next": False,
        },
        "current_interfaces": [
            {
                "interface": "sendable external request bundle",
                "path": dispatch["bundle_dir"],
                "status": dispatch["status"],
                "ready_count": int(dispatch["ready_external_request_count"]),
                "claim_boundary": "prepared_not_sent; request_sent_claimed=false",
            },
            {
                "interface": "external artifact dropbox",
                "path": dropbox["dropbox_dir"],
                "status": dropbox["status"],
                "artifact_candidate_count": artifact_candidates,
                "claim_boundary": "hash-and-route only; pod_expected_next=false",
            },
        ],
        "recommended_next_actions": [
            "owner sends selected request and records a real receipt",
            "owner places authorized ACM zip / author archive / response JSON in the artifact dropbox and reruns Goal5446",
            "authorized ACM access or local zip is inspected with the ACM zip inspector",
            "real external response is normalized and classified with Goal5435/Goal5437",
        ],
        "not_recommended_next_actions": [
            "POD execution from the current state",
            "route micro-optimization",
            "explicit -lb or row/hash parity work",
            "performance ratio work",
            "promoting Level-B scalar evidence to exact paper reproduction",
        ],
        "next_action": next_action,
        "claim_boundary": {
            "current_external_blocker_state_claimed": True,
            "exact_input_blocker_removed": exact_input_blocker_removed,
            "request_sent_claimed": request_sent,
            "external_response_received": response_received,
            "external_artifacts_acquired": artifacts_acquired,
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
        "pod_usage": {
            "used": False,
            "expected_next": False,
            "reason": "Current state has no sent request, no incoming response, no artifact candidate, and no exact-equivalence evidence.",
        },
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": "current external blocker state packet / reproduction-governance workflow",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: blocker governance, not app-artifact parity implementation.",
        },
        "allowed_summary": (
            "The X-HD external chain is ready for owner action: requests can be sent "
            "and artifacts can be dropped into a fixed gate, but no request is sent, "
            "no artifact/response is present, exact input remains blocked, and POD is not next."
        ),
        "not_allowed": [
            "claiming request_sent from prepared requests or stubs",
            "claiming external artifact acquisition from an empty dropbox",
            "claiming ACM supplement inspection from file presence alone",
            "claiming exact paper dataset reproduction",
            "claiming Figure 5 or full X-HD reproduction",
            "claiming author-vs-RTDL performance ratio",
            "running POD or route work from this state",
            "reopening explicit -lb or route micro-optimization as paper-reproduction progress",
        ],
        "exit_label": status,
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "exact_input_blocker_removed": payload["summary"]["exact_input_blocker_removed"],
                "request_sent_claimed": payload["summary"]["request_sent_claimed"],
                "external_artifact_candidate_count": payload["summary"]["external_artifact_candidate_count"],
                "pod_expected_next": payload["summary"]["pod_expected_next"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
