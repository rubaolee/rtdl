"""Close Goal5793 X1 after the conditional returned review, append-only."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history/internal_docs"
DATE = "2026-08-22"
REVIEW = "history/internal_docs/review_goal5793_x1_examiner_exposure_boundary_and_exact_environment_20260822.md"
CFR = "history/internal_docs/call_for_review_goal5793_x1_generic_examiner_exposure_and_environment_single_cfr_20260822.md"
RESULT = "history/internal_docs/goal5793_x1_external_review_result_v2_single_cfr_20260822.json"
DELIVERY_CORRECTION = "history/internal_docs/goal5793_x1_single_cfr_delivery_correction_20260822.json"
S0_CLOSURE = "history/internal_docs/goal5793_s0_postreview_closure_and_x1_entry_20260822.json"
OWNER_DIRECTIVE = "history/internal_docs/goal5793_x1_owner_local_linux_directive_record_20260822.json"
EXACT_ENV = "history/internal_docs/goal5793_x1_exact_environment_capture_20260822.json"
ENV_CAPSULE = "history/internal_docs/goal5793_x1_exact_environment_capsule_20260822.tar.gz"
NATIVE_TRACE = "history/internal_docs/goal5793_x1_native_trace_authority_20260822.json"
AMENDMENT_NAME = "goal5793_x1_governance_ordering_amendment_20260822.json"
ABSORPTION_NAME = "goal5793_x1_owner_returned_external_review_absorption_20260822.json"
CLOSURE_NAME = "goal5793_x1_postreview_closure_and_x2_offline_entry_20260822.json"

EXPECTED = {
    REVIEW: (None, "2a94062fed53ad9daa52aef447c03c1d70ece46ce15fb6e1cf623fee136ddc7e"),
    CFR: (9094, "496d9cd9be32c362b1e413d10c137efabf0328b48800e6e143a33c6fb8ce0c4c"),
    RESULT: (7228, "a83eac15d7c8bedb93966d884c3c20e86fc3e78ab0ef99daaf09b630349d9b4d"),
    DELIVERY_CORRECTION: (1840, "5cee9a16957280dd0733c8179b2d2a91884de5825bab0249b54080d0a44f7f41"),
    S0_CLOSURE: (9317, "4d6e37bc19c0f541537e2f9fc36a31b4d35a20bc0fb080ba495629c0d9fd1f41"),
    OWNER_DIRECTIVE: (1338, "e5761628d84a72bded1647be9cc616a6eda65b54e11eadfa6423c9f105c31969"),
    EXACT_ENV: (717243, "010f92a84d4f956fc186bd1594dbee4dbabefe7cfe87c94d2edd4a3596c93240"),
    ENV_CAPSULE: (434441467, "90ff09e084c4b9e9ba0262dfe9dc2ef028b2777b98ce4c16a5a8f4e3b1fe41d9"),
    NATIVE_TRACE: (629556, "3454f73dce43dd39928f71516ff434dcb555c7a841dc5715b3b7cfd2d87080f7"),
}


class ClosureError(ValueError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _identity(relative: str) -> dict[str, object]:
    path = ROOT / relative
    if not path.is_file() or path.is_symlink():
        raise ClosureError(f"root_absent_or_nonregular:{relative}")
    observed = (path.stat().st_size, _sha256(path))
    expected_bytes, expected_sha = EXPECTED[relative]
    if (expected_bytes is not None and observed[0] != expected_bytes) or observed[1] != expected_sha:
        raise ClosureError(f"root_identity_mismatch:{relative}")
    return {"path": relative, "bytes": observed[0], "sha256": observed[1]}


def _bytes_identity(path: str, payload: bytes) -> dict[str, object]:
    return {"path": path, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}


def build_documents() -> dict[str, bytes]:
    roots = {key: _identity(key) for key in EXPECTED}
    review_text = (ROOT / REVIEW).read_text(encoding="utf-8")
    required_review_literals = [
        "| **P0** | **0** |",
        "| **P1** | **1** |",
        "| **P2** | **2** |",
        "| **P3** | **2** |",
        "| **X1 accepted** | **Not yet**",
        "| **Conservative no-memory-attestation boundary accepted** | **Yes** |",
        "| **Owner-directed SSH-to-local-Linux successor scope accepted** | **Yes**",
        "| **X2 offline implementation only, after owner closure** | **Yes, conditional**",
        "One append-only amendment, no re-execution, unblocks it.",
        "Close P1-1 with one append-only amendment and X1 is accepted",
    ]
    if not all(literal in review_text for literal in required_review_literals):
        raise ClosureError("returned_review_required_ruling_missing")

    amendment: dict[str, Any] = {
        "schema": "rtdl.goal5793.x1.governance_ordering_amendment.v1",
        "date": DATE,
        "status": "ONE_TIME_REVIEWED_HISTORICAL_TRANSPORT_EXCEPTION__ORDERING_VIOLATION_PRESERVED__NO_FUTURE_SSH_OR_POD_PRECEDENT",
        "predecessors": {
            "s0_closure": roots[S0_CLOSURE], "owner_directive": roots[OWNER_DIRECTIVE],
            "returned_x1_review": roots[REVIEW], "exact_environment": roots[EXACT_ENV],
            "environment_capsule": roots[ENV_CAPSULE], "native_trace": roots[NATIVE_TRACE],
        },
        "admitted_facts": {
            "s0_closure_x1_scope_pod_or_ssh_allowed_was_false": True,
            "s0_protocol_permanent_goal5793_pod_or_ssh_allowed_ever_was_false": True,
            "ssh_to_192_168_1_20_occurred_before_this_sealed_amendment": True,
            "chat_directive_was_not_a_protocol_compliant_pre_action_sealed_transition": True,
            "governance_ordering_violation_occurred": True,
            "action_was_pre_authorized_by_s0_artifact": False,
            "external_review_accepted_scientific_scope": True,
            "external_review_required_this_append_only_amendment": True,
        },
        "one_time_disposition": {
            "classification": "OWNER_DIRECTED_BUT_NOT_PRESEALED__EXTERNALLY_REVIEWED_AFTER_ACTION",
            "retroactively_relabelled_as_pre_authorized": False,
            "exact_completed_action_may_enter_x1_evidence_after_this_amendment_and_owner_closure": True,
            "host": "192.168.1.20", "transport": "SSH", "wsl_used": False,
            "purpose": "X1 exact non-GPU environment/native materialization only",
            "gpu_call_count": 0, "gpu_marker_hit_count": 0, "candidate_work_count": 0,
            "registered_or_performance_timing_count": 0, "reexecution_required": False,
        },
        "permanent_future_invariants": {
            "goal5793_pod_or_ssh_allowed_ever": False,
            "future_chat_message_alone_can_authorize_protocol_transition": False,
            "future_action_requires_pre_action_exact_sealed_authority": True,
            "this_exception_is_precedent_for_gpu_execution_or_timing": False,
            "this_exception_is_precedent_for_future_ssh_or_pod": False,
            "product_src_native_family_role_opcode_rule_facade_change_allowed": False,
            "registered_or_performance_timing_count_required": 0,
        },
        "authorization": {
            "authorizes_inclusion_of_exact_already_completed_non_gpu_x1_materialization_after_owner_closure": True,
            "authorizes_x1_owner_closure_authoring": True,
            "authorizes_future_ssh_or_pod": False, "authorizes_gpu": False,
            "authorizes_x2_before_owner_closure": False, "authorizes_live_search": False,
            "authorizes_entropy_selection_candidate_work": False, "authorizes_timing": False,
            "authorizes_publication_or_submission": False,
        },
        "amendment_sha256": "",
    }
    amendment["amendment_sha256"] = seal_document(
        amendment, seal_field="amendment_sha256", domain="rtdl.goal5793.x1.governance_ordering_amendment", version=1,
    )
    amendment_bytes = canonical_json_bytes(amendment) + b"\n"

    absorption: dict[str, Any] = {
        "schema": "rtdl.goal5793.x1.owner_returned_external_review_absorption.v1",
        "date": DATE,
        "status": "RETURNED_REVIEW_ABSORBED__P1_CONDITION_SATISFIED_BY_APPEND_ONLY_AMENDMENT__X1_READY_FOR_OWNER_CLOSURE",
        "review": roots[REVIEW], "single_cfr": roots[CFR], "result_v2": roots[RESULT],
        "delivery_correction": roots[DELIVERY_CORRECTION],
        "governance_amendment": _bytes_identity(f"history/internal_docs/{AMENDMENT_NAME}", amendment_bytes),
        "review_verdict": {"P0": 0, "P1": 1, "P2": 2, "P3": 2, "x1_accepted_before_condition": False},
        "finding_disposition": {
            "P1_1_governance_ordering": "CLOSED_BY_EXACT_APPEND_ONLY_AMENDMENT__HISTORICAL_VIOLATION_NOT_ERASED__NO_REEXECUTION",
            "P2_1_single_self_contained_delivery": "OPEN_NONBLOCKING__SINGLE_CFR_OWNER_REQUIREMENT_CONTROLS__COMPACT_SELF_CONTAINED_REVIEWABILITY_REPAIR_REQUIRED_IN_X2_BEFORE_NEXT_EXTERNAL_REVIEW",
            "P2_2_missing_strong_identifiers_179_of_186": "OPEN_NONBLOCKING__X2_MATCHING_RISK__NO_LIVE_LOOKUP_BEFORE_X2_REVIEW_AND_CLOSURE",
            "P3_findings": "ACCEPTED_AS_NONBLOCKING_DISCLOSURES",
        },
        "accepted_boundaries": {
            "ssh_successor_scientific_scope": True, "no_memory_attestation_boundary": True,
            "x2_offline_only_after_condition_and_owner_closure": True,
        },
        "claim_boundary": {"prospective_generality_exam_count": 0, "usability_evidence_count": 0},
        "authorization": {"x1_owner_closure_authoring": True, "x2": False, "live_search": False,
                          "entropy_selection_candidate_work": False, "gpu_pod_ssh": False,
                          "timing": False, "publication_submission": False},
        "absorption_sha256": "",
    }
    absorption["absorption_sha256"] = seal_document(
        absorption, seal_field="absorption_sha256", domain="rtdl.goal5793.x1.owner_returned_external_review_absorption", version=1,
    )
    absorption_bytes = canonical_json_bytes(absorption) + b"\n"

    closure: dict[str, Any] = {
        "schema": "rtdl.goal5793.x1.postreview_closure_and_x2_offline_entry.v1",
        "date": DATE,
        "status": "X1_CLOSED_ACCEPTED_AFTER_CONDITIONAL_P1_AMENDMENT__X2_OFFLINE_IMPLEMENTATION_ONLY_AUTHORIZED__ALL_LIVE_AND_SCIENTIFIC_ACTIONS_BLOCKED",
        "predecessors": {
            "s0_closure": roots[S0_CLOSURE], "single_cfr": roots[CFR], "returned_review": roots[REVIEW],
            "result_v2": roots[RESULT], "delivery_correction": roots[DELIVERY_CORRECTION],
            "governance_amendment": _bytes_identity(f"history/internal_docs/{AMENDMENT_NAME}", amendment_bytes),
            "review_absorption": _bytes_identity(f"history/internal_docs/{ABSORPTION_NAME}", absorption_bytes),
        },
        "closure_findings": {
            "external_review_p0": 0, "conditional_p1_count_before_amendment": 1,
            "conditional_p1_remaining_after_exact_amendment": 0,
            "historical_ordering_violation_preserved": True, "reexecution_performed_or_required": False,
            "p2_open_nonblocking_count": 2, "p3_open_nonblocking_count": 2,
        },
        "x1_result": {
            "x1_complete": True, "examiner_registry_environment_freeze_accepted": True,
            "prospective_generality_exam_count": 0, "usability_evidence_count": 0,
            "generalization_or_usability_claim_authorized": False,
        },
        "x2_entry_scope": {
            "offline_implementation_only": True,
            "allowed": [
                "offline harvester implementation against synthetic fixtures",
                "taxonomy and deterministic alias enumerator implementation",
                "NIST verifier and selection-client implementation against synthetic fixtures",
                "compact self-contained reviewability repair",
                "offline strong-identifier matching policy hardening without live lookup",
                "local CPU tests, manifests, reports and one CFR authoring",
            ],
            "first_live_provider_call_allowed": False, "systematic_search_execution_allowed": False,
            "entropy_anchor_or_draw_allowed": False, "candidate_selection_allowed": False,
            "candidate_implementation_or_execution_allowed": False,
        },
        "permanent_invariants": {
            "goal5793_pod_or_ssh_allowed_ever": False, "gpu_allowed": False,
            "registered_or_performance_timing_count_required": 0,
            "product_src_native_family_role_opcode_rule_facade_change_allowed": False,
            "valid_scientific_rejection_unknown_or_zero_of_three_can_trigger_rescue": False,
        },
        "authorization": {
            "authorizes_x2_offline_implementation": True,
            "authorizes_live_provider_call_or_systematic_search": False,
            "authorizes_entropy_anchor_or_draw": False, "authorizes_candidate_selection": False,
            "authorizes_candidate_implementation_or_execution": False,
            "authorizes_gpu_home_pod_or_ssh": False, "authorizes_registered_or_performance_timing": False,
            "authorizes_product_or_src_native_change": False, "authorizes_publication_or_submission": False,
            "authorizes_external_reviewer_contact": False,
        },
        "required_next_action": "IMPLEMENT_AND_FREEZE_X2_OFFLINE_TOOLING_ONLY__THEN_SINGLE_CFR_EXTERNAL_REVIEW_AND_OWNER_CLOSURE_BEFORE_ANY_LIVE_SEARCH",
        "closure_sha256": "",
    }
    closure["closure_sha256"] = seal_document(
        closure, seal_field="closure_sha256", domain="rtdl.goal5793.x1.postreview_closure_and_x2_offline_entry", version=1,
    )
    return {
        AMENDMENT_NAME: amendment_bytes,
        ABSORPTION_NAME: absorption_bytes,
        CLOSURE_NAME: canonical_json_bytes(closure) + b"\n",
    }


def write_create_only(output_root: Path) -> dict[str, dict[str, object]]:
    documents = build_documents()
    paths = {name: output_root / name for name in documents}
    if any(path.exists() or path.is_symlink() for path in paths.values()):
        raise ClosureError("create_only_output_exists")
    output_root.mkdir(parents=True, exist_ok=True)
    for name, payload in documents.items():
        with paths[name].open("xb") as handle:
            handle.write(payload)
    return {name: {"bytes": path.stat().st_size, "sha256": _sha256(path)} for name, path in paths.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-create-only", action="store_true")
    args = parser.parse_args()
    if args.write_create_only:
        print(json.dumps(write_create_only(HISTORY), sort_keys=True))
    else:
        with tempfile.TemporaryDirectory(prefix="goal5793_x1_postreview_dry_") as raw:
            print("DRY_RUN_NO_HISTORY_WRITE", json.dumps(write_create_only(Path(raw)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
