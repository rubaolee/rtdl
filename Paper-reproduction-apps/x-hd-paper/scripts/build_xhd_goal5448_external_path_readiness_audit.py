#!/usr/bin/env python3
"""Build Goal5448 X-HD external-path readiness audit.

Goal5448 audits whether every owner/external action named by the current
Goal5447 blocker node has an executable, fail-closed next path.

It does not send requests, inspect real artifacts, run POD, run author code,
run RTDL routes, or upgrade any reproduction claim.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP / "results"
SCRIPTS = APP / "scripts"
REQUESTS = APP / "requests"
TESTS = ROOT / "tests"
OUT = RESULTS / "xhd_goal5448_external_path_readiness_audit.json"

CURRENT_STATE = RESULTS / "xhd_goal5447_current_external_blocker_state.json"


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def _file(path: Path) -> dict[str, Any]:
    return {
        "path": _rel(path),
        "exists": path.exists(),
    }


def _path_row(
    *,
    path_id: str,
    trigger: str,
    status_now: str,
    required_files: list[Path],
    command_templates: list[str],
    expected_output: str,
    pod_direct_allowed: bool = False,
    exact_claim_direct_allowed: bool = False,
) -> dict[str, Any]:
    missing = [_rel(path) for path in required_files if not path.exists()]
    return {
        "path_id": path_id,
        "trigger": trigger,
        "status_now": status_now,
        "required_files": [_file(path) for path in required_files],
        "missing_required_files": missing,
        "ready": not missing,
        "command_templates": command_templates,
        "expected_output": expected_output,
        "pod_direct_allowed": pod_direct_allowed,
        "exact_claim_direct_allowed": exact_claim_direct_allowed,
    }


def build_payload() -> dict[str, Any]:
    current = json.loads(CURRENT_STATE.read_text(encoding="utf-8"))

    rows = [
        _path_row(
            path_id="sent_receipt_path",
            trigger="owner sends a prepared request outside the repository and records a real sent receipt",
            status_now="not_triggered__request_sent_claimed_false",
            required_files=[
                SCRIPTS / "run_xhd_goal5439_external_request_sent_receipt_gate.py",
                SCRIPTS / "build_xhd_goal5440_external_evidence_chain_review_packet.py",
                SCRIPTS / "build_xhd_goal5447_current_external_blocker_state.py",
                TESTS / "goal5439_external_request_sent_receipt_gate_test.py",
                TESTS / "goal5447_current_external_blocker_state_test.py",
            ],
            command_templates=[
                "py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5439_external_request_sent_receipt_gate.py",
                "py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5440_external_evidence_chain_review_packet.py",
                "py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5447_current_external_blocker_state.py",
            ],
            expected_output="valid sent receipt updates request_sent_claimed but still does not imply response/artifact/exact input",
        ),
        _path_row(
            path_id="incoming_response_json_path",
            trigger="author/reviewer/ACM response is normalized as external_response_intake.v1 JSON",
            status_now="not_triggered__external_response_received_false",
            required_files=[
                SCRIPTS / "validate_xhd_external_response_intake.py",
                SCRIPTS / "ingest_xhd_external_response.py",
                SCRIPTS / "run_xhd_goal5435_external_response_inbox_gate.py",
                SCRIPTS / "build_xhd_goal5437_external_response_next_gate_plan.py",
                TESTS / "goal5330_xhd_external_response_intake_validator_test.py",
                TESTS / "goal5435_external_response_inbox_gate_test.py",
                TESTS / "goal5437_external_response_next_gate_plan_test.py",
            ],
            command_templates=[
                "py Paper-reproduction-apps/x-hd-paper/scripts/validate_xhd_external_response_intake.py <response.json>",
                "py Paper-reproduction-apps/x-hd-paper/scripts/ingest_xhd_external_response.py <response.json> --case-id <case>",
                "py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5435_external_response_inbox_gate.py",
                "py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5437_external_response_next_gate_plan.py",
            ],
            expected_output="classified response and explicit not-executed next-gate plan",
        ),
        _path_row(
            path_id="artifact_dropbox_path",
            trigger="owner places authorized ACM zip, author archive, hash file, or response JSON in requests/artifacts",
            status_now="not_triggered__artifact_candidate_count_zero",
            required_files=[
                SCRIPTS / "run_xhd_goal5446_external_artifact_dropbox_gate.py",
                TESTS / "goal5446_external_artifact_dropbox_gate_test.py",
                REQUESTS / "artifacts" / "README.md",
            ],
            command_templates=[
                "py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5446_external_artifact_dropbox_gate.py",
            ],
            expected_output="hash-and-route record with file-specific intake recommendation; no direct POD",
        ),
        _path_row(
            path_id="acm_supplement_zip_path",
            trigger="authorized local ACM supplement zip is available",
            status_now="not_triggered__dropbox_empty",
            required_files=[
                SCRIPTS / "inspect_xhd_acm_supplement_zip.py",
                SCRIPTS / "ingest_xhd_external_response.py",
                SCRIPTS / "plan_xhd_provenance_ingestion_from_case.py",
                TESTS / "goal5335_xhd_acm_supplement_zip_inspector_test.py",
            ],
            command_templates=[
                "py Paper-reproduction-apps/x-hd-paper/scripts/inspect_xhd_acm_supplement_zip.py <ics26-106.zip> --output <response.json>",
                "py Paper-reproduction-apps/x-hd-paper/scripts/ingest_xhd_external_response.py <response.json> --case-id <case>",
                "py Paper-reproduction-apps/x-hd-paper/scripts/plan_xhd_provenance_ingestion_from_case.py <case-dir>",
            ],
            expected_output="ACM listing response classified before any artifact mapping or POD",
        ),
        _path_row(
            path_id="acm_artifact_pipeline_path",
            trigger="ACM zip contains artifact-like material and a mapping spec has been accepted",
            status_now="not_triggered__requires_prior_zip_inspection_and_mapping_review",
            required_files=[
                SCRIPTS / "ingest_xhd_acm_artifact_instructions.py",
                SCRIPTS / "map_xhd_acm_candidate_bytes_hashes.py",
                SCRIPTS / "review_xhd_candidate_workload_mapping.py",
                SCRIPTS / "build_xhd_mapped_candidate_same_input_gate_packet.py",
                SCRIPTS / "run_xhd_acm_artifact_to_packet_pipeline.py",
                TESTS / "goal5337_xhd_acm_candidate_hash_mapping_test.py",
                TESTS / "goal5338_xhd_candidate_workload_mapping_review_test.py",
                TESTS / "goal5339_xhd_mapped_candidate_same_input_packet_test.py",
                TESTS / "goal5342_xhd_acm_artifact_to_packet_pipeline_test.py",
            ],
            command_templates=[
                "py Paper-reproduction-apps/x-hd-paper/scripts/ingest_xhd_acm_artifact_instructions.py <ics26-106.zip> --output <manifest.json>",
                "py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_acm_artifact_to_packet_pipeline.py <zip> <accepted_mapping_spec.json> --output-root <out> --output <summary.json>",
            ],
            expected_output="mapped same-input command packet; POD remains separate and reviewed",
        ),
        _path_row(
            path_id="exact_equivalence_verdict_path",
            trigger="external reviewer accepts a named exact-equivalence boundary",
            status_now="not_triggered__exact_equivalence_accepted_false",
            required_files=[
                SCRIPTS / "validate_xhd_external_response_intake.py",
                SCRIPTS / "build_xhd_goal5437_external_response_next_gate_plan.py",
                TESTS / "goal5330_xhd_external_response_intake_validator_test.py",
                TESTS / "goal5437_external_response_next_gate_plan_test.py",
            ],
            command_templates=[
                "py Paper-reproduction-apps/x-hd-paper/scripts/validate_xhd_external_response_intake.py <exact_equivalence_verdict_response.json>",
                "py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5437_external_response_next_gate_plan.py",
            ],
            expected_output="accepted-equivalence next-gate label; still requires accepted matrix gate before exact wording",
        ),
    ]

    missing = [path for row in rows for path in row["missing_required_files"]]
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5448.external_path_readiness_audit.v1",
        "goal": "Goal5448",
        "date": "2026-07-10",
        "source_current_state": _rel(CURRENT_STATE),
        "current_state_status": current["status"],
        "path_count": len(rows),
        "ready_path_count": sum(1 for row in rows if row["ready"]),
        "missing_required_file_count": len(missing),
        "missing_required_files": missing,
        "status": "external_path_readiness_complete__all_paths_have_fail_closed_gates" if not missing else "external_path_readiness_incomplete__missing_bridge_files",
        "paths": rows,
        "exact_input_blocker_removed": False,
        "pod_expected_next": False,
        "claim_boundary": {
            "external_path_readiness_audit_claimed": True,
            "request_sent_claimed": False,
            "external_response_received": False,
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
            "gate_non_app_consumer": "external path readiness audit / reproduction-governance workflow",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: external-action routing audit, not app-artifact parity implementation.",
        },
        "not_allowed": [
            "claiming any external action happened from this audit alone",
            "claiming exact paper dataset reproduction",
            "claiming Figure 5 or full X-HD reproduction",
            "claiming author-vs-RTDL performance ratio",
            "running POD or route work from this audit alone",
        ],
        "next_action": "owner_or_external_action_required; after trigger, run the corresponding ready path",
    }


def main() -> int:
    payload = build_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "path_count": payload["path_count"],
                "ready_path_count": payload["ready_path_count"],
                "missing_required_file_count": payload["missing_required_file_count"],
                "pod_expected_next": payload["pod_expected_next"],
            },
            sort_keys=True,
        )
    )
    return 0 if payload["missing_required_file_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
