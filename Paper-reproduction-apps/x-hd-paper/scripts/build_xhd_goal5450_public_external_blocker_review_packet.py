#!/usr/bin/env python3
"""Goal5450 consolidated public/external blocker review packet for X-HD."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP / "results"
OUT = RESULTS / "xhd_goal5450_public_external_blocker_review_packet.json"


def _load(name: str) -> dict[str, Any]:
    path = RESULTS / name
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def build_payload() -> dict[str, Any]:
    goal5442 = _load("xhd_goal5442_public_provenance_rescan.json")
    goal5448 = _load("xhd_goal5448_external_path_readiness_audit.json")
    goal5449 = _load("xhd_goal5449_deep_public_mirror_probe.json")

    exact_removed = any(
        bool(payload.get("classification", {}).get("exact_input_blocker_removed"))
        for payload in (goal5442, goal5449)
    )
    new_public_artifact = any(
        bool(payload.get("classification", {}).get("new_public_exact_input_artifact_found"))
        for payload in (goal5442, goal5449)
    )
    ready_paths = int(goal5448.get("ready_path_count", 0))
    path_count = int(goal5448.get("path_count", 0))
    all_paths_ready = ready_paths == path_count and path_count > 0

    status = (
        "public_external_blocker_packet_ready__external_event_required"
        if all_paths_ready and not exact_removed and not new_public_artifact
        else "public_external_blocker_packet_requires_review_before_action"
    )

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5450.public_external_blocker_review_packet.v1",
        "goal": "Goal5450",
        "date": "2026-07-10",
        "purpose": (
            "Consolidate the current public-provenance and external-action state after Goal5449 so it can be "
            "strictly reviewed as one blocker node."
        ),
        "status": status,
        "source_artifacts": {
            "goal5442_public_provenance_rescan": _rel(RESULTS / "xhd_goal5442_public_provenance_rescan.json"),
            "goal5448_external_path_readiness": _rel(RESULTS / "xhd_goal5448_external_path_readiness_audit.json"),
            "goal5449_deep_public_mirror_probe": _rel(RESULTS / "xhd_goal5449_deep_public_mirror_probe.json"),
        },
        "public_provenance_summary": {
            "goal5442_status": goal5442["status"],
            "goal5442_new_public_exact_input_artifact_found": goal5442["classification"][
                "new_public_exact_input_artifact_found"
            ],
            "goal5449_status": goal5449["status"],
            "goal5449_new_public_exact_input_artifact_found": goal5449["classification"][
                "new_public_exact_input_artifact_found"
            ],
            "deep_surface_classes_checked": list(goal5449["deep_surfaces"].keys()),
            "exact_input_blocker_removed": exact_removed,
        },
        "external_path_summary": {
            "goal5448_status": goal5448["status"],
            "path_count": path_count,
            "ready_path_count": ready_paths,
            "missing_required_file_count": goal5448["missing_required_file_count"],
            "all_paths_ready": all_paths_ready,
            "path_ids": [row["path_id"] for row in goal5448["paths"]],
            "all_paths_disallow_direct_pod": all(not row["pod_direct_allowed"] for row in goal5448["paths"]),
            "all_paths_disallow_direct_exact_claim": all(
                not row["exact_claim_direct_allowed"] for row in goal5448["paths"]
            ),
        },
        "current_blocker": {
            "exact_input_blocker_removed": False,
            "full_objective_complete": False,
            "new_public_exact_input_artifact_found": new_public_artifact,
            "external_paths_ready": all_paths_ready,
            "pod_expected_next": False,
            "why_not_pod": (
                "No exact artifact, accepted exact-equivalence verdict, hash manifest, byte-identical regeneration, "
                "or inspected ACM supplement is present. POD would only rerun Level-B routes."
            ),
        },
        "next_external_events": [
            {
                "event": "real sent receipt",
                "first_local_gate": "run_xhd_goal5439_external_request_sent_receipt_gate.py",
            },
            {
                "event": "normalized external response JSON",
                "first_local_gate": "validate_xhd_external_response_intake.py",
            },
            {
                "event": "authorized artifact in requests/artifacts",
                "first_local_gate": "run_xhd_goal5446_external_artifact_dropbox_gate.py",
            },
            {
                "event": "authorized ACM supplement zip",
                "first_local_gate": "inspect_xhd_acm_supplement_zip.py",
            },
            {
                "event": "accepted exact-equivalence verdict",
                "first_local_gate": "validate_xhd_external_response_intake.py",
            },
        ],
        "claim_boundary": {
            "consolidated_blocker_packet_claimed": True,
            "external_artifacts_acquired": False,
            "external_response_received": False,
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
            "gate_non_app_consumer": "public/external blocker review packet / reproduction-governance workflow",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: consolidated governance packet, not app-artifact parity implementation.",
        },
        "allowed_summary": (
            "Goal5450 consolidates Goals5442, 5448, and 5449: public surfaces have been checked to the current "
            "depth, external paths are ready, and exact/full reproduction still requires a real external event."
        ),
        "not_allowed": [
            "claiming exact input recovery",
            "claiming full X-HD paper reproduction",
            "claiming Figure 5 reproduction",
            "claiming author-vs-RTDL performance ratio",
            "running POD from this packet",
            "adding route tuning, explicit -lb, row/hash parity, or another local wrapper as paper-reproduction progress",
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
                "exact_input_blocker_removed": payload["current_blocker"]["exact_input_blocker_removed"],
                "external_paths_ready": payload["current_blocker"]["external_paths_ready"],
                "pod_expected_next": payload["current_blocker"]["pod_expected_next"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
