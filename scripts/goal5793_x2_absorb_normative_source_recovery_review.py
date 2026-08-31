#!/usr/bin/env python3
"""Append-only absorption and owner closure for the reviewed X2 source recovery."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts import goal5793_x2_recover_pinned_normative_sources as recovery


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-08-22"
SEND_NAME = "goal5793_x2_normative_source_recovery_owner_send_receipt_20260822.json"
V3_NAME = "goal5793_x2_normative_source_recovery_preaction_governance_authority_v3_20260822.json"
ABSORPTION_NAME = "goal5793_x2_normative_source_recovery_review_absorption_20260822.json"
CLOSURE_NAME = "goal5793_x2_normative_source_recovery_owner_closure_20260822.json"
V2_AUTHORITY = "history/internal_docs/goal5793_x2_normative_source_recovery_preaction_work_authority_v2_20260822.json"
V2_CFR = "history/internal_docs/call_for_review_goal5793_x2_normative_source_recovery_preaction_amendment_v2_20260822.md"
RETURNED_REVIEW = "history/internal_docs/review_goal5793_x2_normative_source_recovery_preaction_amendment_v2_20260822.md"
TOOL = "scripts/goal5793_x2_recover_pinned_normative_sources.py"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _rel_identity(rel: str) -> dict[str, Any]:
    data = (ROOT / rel).read_bytes()
    return {"path": rel, "bytes": len(data), "sha256": _sha(data)}


def _abs_identity(path: Path) -> dict[str, Any]:
    path = path.resolve(); data = path.read_bytes()
    return {"path": path.as_posix(), "bytes": len(data), "sha256": _sha(data)}


def _json_bytes(value: Any) -> bytes:
    return canonical_json_bytes(value) + b"\n"


def _sealed(value: dict[str, Any], field: str, domain: str) -> dict[str, Any]:
    value[field] = seal_document(value, seal_field=field, domain=domain, version=1)
    return value


def build_outputs() -> dict[str, bytes]:
    v2_authority = _rel_identity(V2_AUTHORITY)
    cfr = _rel_identity(V2_CFR)
    review = _rel_identity(RETURNED_REVIEW)
    tool = _rel_identity(TOOL)

    send = _sealed(
        {
            "schema": "rtdl.goal5793.x2.normative_source_recovery.owner_send_receipt.v1",
            "goal": 5793,
            "stage": "X2_NORMATIVE_SOURCE_RECOVERY_PREACTION_EXTERNAL_REVIEW_SEND",
            "date": DATE,
            "status": "OWNER_ASSERTED_SENT_EXACT_SINGLE_CFR__RETURNED_REVIEW_REHASHES_ENTRYPOINT__TIME_OF_DAY_UNAVAILABLE",
            "cfr": cfr,
            "send_time": {
                "owner_reported_literal": "已经送审",
                "owner_reported_date_crosschecked_from_review": DATE,
                "time_of_day_known": False,
                "exact_rfc3339_timestamp_claimed": False,
                "review_file_creation_time_used_as_send_time": False,
                "review_file_creation_time_observation_local": "2026-08-22T18:55:46-04:00",
                "review_file_creation_time_observation_role": "upper-bound context only; not owner send time",
            },
            "recipient_selected_by_owner": "Claude (claude-opus-5)",
            "recipient_crosschecked_from_returned_review": True,
            "sent_file_count": 1,
            "sent_paths": [V2_CFR],
            "separate_packet_or_authority_sent": False,
            "owner_attests_exact_cfr_sent": True,
            "returned_review_crosscheck": {**review, "reviewer_rehashed_cfr_bytes": 25145, "reviewer_rehashed_cfr_sha256": cfr["sha256"]},
            "authorization": {"owner_absorption_and_closure": True, "network_source_recovery": False, "live_search": False, "beacon": False, "entropy": False, "selection": False, "candidate_work": False, "gpu_ssh_pod": False, "timing": False},
            "receipt_sha256": "",
        },
        "receipt_sha256",
        "rtdl.goal5793.x2.normative_source_recovery.owner_send_receipt",
    )
    send_bytes = _json_bytes(send)

    v3 = _sealed(
        {
            "schema": "rtdl.goal5793.x2.normative_source_recovery.preaction_governance_authority.v3",
            "goal": 5793,
            "date": DATE,
            "status": "P1_PIN_PROVENANCE_BOUNDARY_CLOSED__TECHNICAL_EXECUTION_REMAINS_EXACT_REVIEWED_V2",
            "technical_execution_authority": v2_authority,
            "exact_reviewed_recovery_tool": tool,
            "returned_review": review,
            "pin_provenance": {
                "provenance_unrecorded": True,
                "historical_observation_location": "history/internal_docs/goal5793_s0_protocol_and_stage_authority_20260822.json deferred_entropy.normative_source_authority",
                "historical_label": "*_observed_2026_08_22",
                "prior_fetch_receipt_found": False,
                "prior_attempt_log_found": False,
                "prior_preserved_response_found": False,
                "prior_environment_copy_found": False,
                "prior_citing_document_that_recomputes_pin_found": False,
                "how_bytes_were_obtained_known": False,
                "pin_correctness_independently_proven_before_recovery": False,
                "pins_edited_after_review_or_in_response_to_recovery": False,
            },
            "exact_pins_unchanged": [
                {"source_id": source["source_id"], "bytes": source["bytes"], "sha256": source["sha256"]}
                for source in recovery.SOURCES
            ],
            "mismatch_taxonomy": {
                "raw_reviewed_tool_fail_id": "RECOVERY_SOURCE_DRIFT__NO_ALTERNATE_OR_RETRY",
                "raw_fail_id_is_a_legacy_implementation_token_not_a_third_party_causal_finding": True,
                "controlling_governance_disposition": "TERMINAL_PIN_PROVENANCE_UNVERIFIED__NO_CAUSAL_ATTRIBUTION_TO_NIST__NO_RETRY__NO_ALTERNATE__NO_PIN_EDIT",
                "terminal_source_drift_may_be_claimed_from_this_transaction": False,
                "nist_changed_the_file_claimed": False,
                "pin_was_wrong_claimed": False,
                "cause_identified": False,
                "possible_causes_remain_unranked": ["historical pin did not correspond to the URL bytes", "official bytes changed after an unrecorded observation", "retrieval path or transport returned different bytes"],
                "classification_rules": {
                    "mismatch_with_historical_fetch_provenance_unrecorded": "TERMINAL_PIN_PROVENANCE_UNVERIFIED",
                    "terminal_source_drift_requires": "preserved prior official response bytes and fetch receipt that independently reproduce the frozen pin, plus a preserved current official response at the same URL that differs",
                    "terminal_source_drift_preconditions_satisfied_here": False,
                    "cause_is_never_selected_after_observing_which_label_is_convenient": True,
                },
            },
            "exact_match_taxonomy": {
                "disposition": "EXACT_CURRENT_URL_RESPONSE_MATCHES_FROZEN_PIN__BYTES_RECOVERED__HISTORICAL_FETCH_PROVENANCE_REMAINS_UNRECORDED",
                "historical_provenance_retroactively_fabricated": False,
            },
            "p2_absorption": {
                "inline_canonical_sha_seal_reimplementation_present": True,
                "review_grade": "P2_NONBLOCKING",
                "reviewed_exact_tool_changed_for_this_transaction": False,
                "reviewed_tool_remains_fail_closed": True,
                "final_x2_normative_verifier_and_future_successor_tools_must_import_goal5793_x1_canonical": True,
                "same_defect_class_may_be_waived_in_final_x2": False,
            },
            "claim_boundary": {"x2_accepted": False, "normative_verifier_complete": False, "generalization_evidence_count": 0, "usability_evidence_count": 0, "third_party_source_drift_claimed": False},
            "authorization": {"network": False, "live_search": False, "beacon": False, "entropy": False, "selection": False, "candidate_work": False, "gpu_ssh_pod": False, "timing": False, "x2_closure": False, "publication": False},
            "governance_authority_sha256": "",
        },
        "governance_authority_sha256",
        "rtdl.goal5793.x2.normative_source_recovery.preaction_governance_authority",
    )
    v3_bytes = _json_bytes(v3)

    send_id = {"path": f"history/internal_docs/{SEND_NAME}", "bytes": len(send_bytes), "sha256": _sha(send_bytes)}
    v3_id = {"path": f"history/internal_docs/{V3_NAME}", "bytes": len(v3_bytes), "sha256": _sha(v3_bytes)}
    absorption = _sealed(
        {
            "schema": "rtdl.goal5793.x2.normative_source_recovery.review_absorption.v1",
            "goal": 5793,
            "date": DATE,
            "status": "RETURNED_REVIEW_ABSORBED__P1_CLOSED_BY_APPEND_ONLY_V3__P2_ACCEPTED_NONBLOCKING__OWNER_CLOSURE_ALLOWED",
            "predecessors": {"v2_authority": v2_authority, "single_cfr": cfr, "owner_send_receipt": send_id, "returned_review": review, "v3_governance_authority": v3_id, "reviewed_tool": tool},
            "review_verdict": {"p0": 0, "p1": 1, "p2": 1, "p3": 2, "may_owner_closure_authorize_only_two_source_recovery_after_p1": True},
            "finding_disposition": {
                "p1_pin_provenance": "CLOSED__PROVENANCE_UNRECORDED_TRUE__MISMATCH_CAUSE_UNASSIGNED__NO_PIN_EDIT",
                "p2_inline_canonical_helper": "ACCEPTED_NONBLOCKING_FOR_EXACT_REVIEWED_FAIL_CLOSED_RECOVERY_TOOL__MANDATORY_REPAIR_FOR_FINAL_X2_TOOLS",
                "delivery_reconstructability": "CLOSED__REVIEWER_RECONSTRUCTED_AUTHORITY_AND_TOOL_BYTE_EXACTLY_FROM_SINGLE_CFR",
            },
            "authorization": {"owner_closure_authoring": True, "network_source_recovery": False, "live_search": False, "beacon": False, "entropy": False, "selection": False, "candidate_work": False, "gpu_ssh_pod": False, "timing": False, "x2_closure": False},
            "absorption_sha256": "",
        },
        "absorption_sha256",
        "rtdl.goal5793.x2.normative_source_recovery.review_absorption",
    )
    absorption_bytes = _json_bytes(absorption)
    absorption_id = {"path": f"history/internal_docs/{ABSORPTION_NAME}", "bytes": len(absorption_bytes), "sha256": _sha(absorption_bytes)}

    closure: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.normative_source_recovery_owner_closure.v1",
        "goal": 5793,
        "date": DATE,
        "status": "P1_CLOSED__ONLY_EXACT_TWO_SOURCE_RECOVERY_AUTHORIZED__X2_AND_ALL_SCIENTIFIC_ACTIONS_STILL_BLOCKED",
        "bindings": {
            "work_authority": _abs_identity(ROOT / V2_AUTHORITY),
            "returned_review": _abs_identity(ROOT / RETURNED_REVIEW),
            "recovery_tool": _abs_identity(ROOT / TOOL),
        },
        "controlling_governance_amendment": v3_id,
        "review_absorption": absorption_id,
        "owner_send_receipt": send_id,
        "mismatch_controlling_disposition": v3["mismatch_taxonomy"]["controlling_governance_disposition"],
        "raw_tool_source_drift_token_is_not_an_authorized_claim_about_nist": True,
        "authorization": {
            "authorizes_exact_pinned_source_recovery": True,
            "live_search": False,
            "beacon": False,
            "entropy": False,
            "selection": False,
            "candidate_work": False,
            "normative_verifier_result_claim": False,
            "x2_closure": False,
            "x3": False,
            "gpu": False,
            "ssh": False,
            "pod": False,
            "timing": False,
            "product_change": False,
            "publication": False,
        },
        "closure_sha256": "",
    }
    closure["closure_sha256"] = recovery._seal(closure, "closure_sha256", recovery.CLOSURE_DOMAIN)
    closure_bytes = recovery._canonical(closure) + b"\n"
    return {SEND_NAME: send_bytes, V3_NAME: v3_bytes, ABSORPTION_NAME: absorption_bytes, CLOSURE_NAME: closure_bytes}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output-dir", type=Path); parser.add_argument("--write-create-only", action="store_true"); args = parser.parse_args()
    if args.write_create_only != (args.output_dir is not None):
        parser.error("formal write requires --output-dir and --write-create-only together")
    outputs = build_outputs()
    if args.output_dir is not None:
        paths = [args.output_dir / name for name in outputs]
        if any(path.exists() or path.is_symlink() for path in paths):
            raise SystemExit("CREATE_ONLY_OUTPUT_EXISTS")
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, data in outputs.items():
            (args.output_dir / name).write_bytes(data)
    print(json.dumps({"status": "WRITE_PASS" if args.output_dir else "DRY_RUN_PASS", "outputs": [{"path": name, "bytes": len(data), "sha256": _sha(data)} for name, data in outputs.items()]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
