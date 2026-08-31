#!/usr/bin/env python3
"""Absorb the returned X3 review and close Goal5793 at terminal scope."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history/internal_docs"
DATE = "2026-08-23"

ABSORPTION_NAME = "goal5793_x3_owner_returned_external_review_absorption_20260823.json"
AMENDMENT_NAME = "goal5793_x3_governance_ordering_and_terminal_attribution_amendment_20260823.json"
CLOSURE_NAME = "goal5793_x3_terminal_owner_closure_and_a1_entry_20260823.json"

ABSORPTION_DOMAIN = "rtdl.goal5793.x3.owner_returned_external_review_absorption"
AMENDMENT_DOMAIN = "rtdl.goal5793.x3.governance_ordering_and_terminal_attribution_amendment"
CLOSURE_DOMAIN = "rtdl.goal5793.x3.terminal_owner_closure_and_a1_entry"

PINNED = {
    "history/internal_docs/call_for_review_goal5793_x3_provider_search_terminal_failure_v2_20260822.md": (
        10482070,
        "5f58ef8756a4d2b0ef8c33228efc8224ef4a05a13ee163b794efd22a651da1d5",
    ),
    "history/internal_docs/review_goal5793_x3_provider_search_terminal_failure_20260822.md": (
        34071,
        "dc9e070b00fecf27211a363462f4872a4e3649c09c0d7f3b9c6bcb288ea1b17a",
    ),
    "history/internal_docs/self_review_goal5793_x3_provider_search_terminal_lineage_20260823.md": (
        18646,
        "2d535a8b672d2afd460a0a592dae65446d81f2f0293ce35a9b7126de685da878",
    ),
    "history/internal_docs/goal5793_x3_provider_search_journal_20260822.jsonl": (
        9326661,
        "94ab0fc951c728569c0d57f649de918feeb547a8f4dac0ea48ec43f176b7e4c5",
    ),
    "history/internal_docs/goal5793_x3_provider_search_terminal_failure_20260822.json": (
        587,
        "6a9f7228ff918c7c4a91c956f5ff5d12f09361c7e71eaf6e65a20054d330e2fd",
    ),
    "history/internal_docs/goal5793_x3_provider_search_terminal_audit_v2_20260822.json": (
        9629,
        "a6d7540544ca3b67ab4741a6b06cb610854816bb9983ff2d0c206c869f6620ec",
    ),
    "history/internal_docs/goal5793_x3_provider_search_terminal_report_v2_20260822.md": (
        1770,
        "f6c26a04e4252b6e37e496fb510c3ff990c56a9f5657729d4f06e185049f8f87",
    ),
    "history/internal_docs/goal5793_x3_provider_search_preaction_authority_20260822.json": (
        4069,
        "e43bd6fdbaddf35e80485113b79224403839d17f4225baad974c8aed404346a7",
    ),
    "history/internal_docs/goal5793_x2_postreview_owner_closure_and_x3_provider_search_entry_20260822.json": (
        4130,
        "ce3f83ef318085646cefdbbfbcc4290b66e745aa9ee88f4b041f84661997e659",
    ),
    "history/internal_docs/goal5793_s0_protocol_and_stage_authority_20260822.json": (
        56110,
        "126ee3c1dfe930a7bb25b2f19df8a6c4889c7ef8b619abe3cc69da54efa8b7c2",
    ),
}


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _identity(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"PINNED_ROOT_MISSING_OR_UNSAFE:{relative}")
    payload = path.read_bytes()
    return {"path": relative, "bytes": len(payload), "sha256": _sha(payload)}


def _verify_pins() -> None:
    for relative, (expected_bytes, expected_sha) in PINNED.items():
        actual = _identity(relative)
        if actual["bytes"] != expected_bytes or actual["sha256"] != expected_sha:
            raise RuntimeError(f"PINNED_IDENTITY_MISMATCH:{relative}")


def _sealed(document: dict[str, Any], field: str, domain: str) -> dict[str, Any]:
    document[field] = seal_document(document, seal_field=field, domain=domain, version=1)
    return document


def _json_bytes(document: dict[str, Any]) -> bytes:
    return canonical_json_bytes(document) + b"\n"


def _generated_identity(name: str, payload: bytes) -> dict[str, Any]:
    return {
        "path": f"history/internal_docs/{name}",
        "bytes": len(payload),
        "sha256": _sha(payload),
    }


def build_documents() -> dict[str, bytes]:
    _verify_pins()
    roots = {relative: _identity(relative) for relative in PINNED}

    absorption = _sealed(
        {
            "schema": "rtdl.goal5793.x3.owner_returned_external_review_absorption.v1",
            "goal": 5793,
            "stage": "X3_TERMINAL_POSTREVIEW_ABSORPTION",
            "date": DATE,
            "status": "RETURNED_REVIEW_ABSORBED_EXACTLY__P1_DOES_NOT_BLOCK_TERMINAL_CLOSURE__P1_BLOCKS_SUCCESSOR_PREREGISTRATION",
            "bound_files": list(roots.values()),
            "external_review_verdict": {
                "p0": 0,
                "p1": 1,
                "p2": 3,
                "p3": 2,
                "verdict_rewritten_by_internal_review": False,
                "p1_blocks_terminal_marking": False,
                "p1_blocks_successor_prospective_generalization_preregistration": True,
            },
            "externally_reproduced_facts": {
                "response_body_bytes": 6991761,
                "response_body_sha256": "453fbab3bf25b84986fa593b80e6e12451619ed24b2c189dc717e643253d874d",
                "result_count": 200,
                "meta_count": 48998,
                "next_cursor_nonnull": True,
                "invalid_url_field_occurrence_count": 217,
                "invalid_http_occurrence_count": 214,
                "invalid_malformed_https_occurrence_count": 3,
                "affected_work_count": 99,
                "selection_bearing_invalid_occurrence_count": 13,
                "selection_bearing_affected_work_count": 7,
                "first_failure": {
                    "result_index": 3,
                    "openalex": "W2973457155",
                    "location": "locations[5].landing_page_url",
                    "parser_reason": "SOURCE_URL_INVALID",
                },
                "all_invalid_values_sha256": "b51c6397d4615955b4a5bf72f587a65b334983185fb10c21a14ff7bcd5a9edd2",
                "canonical_recorded_http_attempt_count": 1,
                "completed_query_count": 0,
                "candidate_count": None,
                "candidate_count_semantics": "UNDEFINED__NO_COMPLETE_POPULATION_EXISTS",
            },
            "review_findings": {
                "p1_observed_work_exposure": "OPEN__DOES_NOT_BLOCK_STOPPING__BLOCKS_ANY_SUCCESSOR_PREREGISTRATION_UNTIL_EXACT_200_ROW_REGISTRY_IS_SEALED_AND_EXTERNALLY_REVIEWED",
                "p2_terminal_reason_attribution": "ACCEPTED__IMMUTABLE_REASON_ID_RETAINED__APPEND_ONLY_INTERNAL_FAULT_ATTRIBUTION_REQUIRED",
                "p2_live_validity_methodology": "ACCEPTED_WITH_INFERENCE_CEILING__FAILED_TO_PREDICT_THIS_LIVE_URL_COMPATIBILITY_BOUNDARY__NOT_A_UNIVERSAL_CLAIM_THAT_OFFLINE_TESTS_HAVE_ZERO_VALUE",
                "p2_sole_cfr_newline_loss": "ACCEPTED__18_OF_18_RECOVERABLE_WITH_DECLARED_LENGTH_AND_HASH__NOT_TURNKEY__FUTURE_BASE64_EXACT_EMBEDDING_REQUIRED",
                "p3_predicate_difference": "ACCEPTED__NO_EMPTY_STRING_URL_ON_CAPTURED_PAGE__COUNTS_UNCHANGED",
                "p3_failure_receipt_self_seal": "ACCEPTED__OUTWARD_INTEGRITY_CHAIN_HOLDS__SUCCESSOR_SCHEMA_MUST_SELF_SEAL",
            },
            "claim_boundary": {
                "goal5793_generalization_exam_count": 0,
                "goal5793_usability_study_count": 0,
                "functionally_matched_direct_cuda_optix_baseline_count": 0,
                "x3_is_generalization_evidence": False,
                "x3_is_scientific_zero_of_three": False,
                "x3_is_zero_candidates": False,
                "publication_or_submission_authorized": False,
            },
            "authorization": {
                "terminal_closure_authoring": True,
                "successor_preregistration": False,
                "parser_repair_or_rerun": False,
                "partial_universe_use": False,
                "science_entropy_selection_candidate_work": False,
                "gpu_ssh_pod_timing": False,
                "product_change": False,
                "publication_submission": False,
            },
            "absorption_sha256": "",
        },
        "absorption_sha256",
        ABSORPTION_DOMAIN,
    )
    absorption_bytes = _json_bytes(absorption)

    amendment = _sealed(
        {
            "schema": "rtdl.goal5793.x3.governance_ordering_and_terminal_attribution_amendment.v1",
            "goal": 5793,
            "stage": "X3_APPEND_ONLY_HISTORICAL_AND_CAUSAL_CORRECTION",
            "date": DATE,
            "status": "HISTORICAL_CONFORMANCE_VIOLATION_AND_INTERNAL_FAULT_RECORDED__NO_REEXECUTION__NO_RELABELLING",
            "predecessors": {
                "external_review": roots["history/internal_docs/review_goal5793_x3_provider_search_terminal_failure_20260822.md"],
                "strict_self_review": roots["history/internal_docs/self_review_goal5793_x3_provider_search_terminal_lineage_20260823.md"],
                "s0_protocol": roots["history/internal_docs/goal5793_s0_protocol_and_stage_authority_20260822.json"],
                "x2_owner_closure": roots["history/internal_docs/goal5793_x2_postreview_owner_closure_and_x3_provider_search_entry_20260822.json"],
                "journal": roots["history/internal_docs/goal5793_x3_provider_search_journal_20260822.jsonl"],
                "review_absorption": _generated_identity(ABSORPTION_NAME, absorption_bytes),
            },
            "deduplicated_finding_register": {
                "p0": 0,
                "p1": 4,
                "p2": 6,
                "p3": 4,
                "external_verdict_remains_exactly_p0_0_p1_1_p2_3_p3_2": True,
                "purpose": "UNION_OF_EXTERNAL_AND_INTERNAL_FINDINGS__NOT_A_REGRADING_OF_THE_EXTERNAL_REVIEW",
            },
            "historical_transition_conformance": {
                "owner_and_reviewer_intended_x3_provider_search_scope_approval": True,
                "literal_s0_x2_to_x3_gate_required_returned_review_p1_zero": True,
                "actual_returned_x2_review_p1": 1,
                "literal_s0_transition_receipt_required": True,
                "exact_transition_receipt_present": False,
                "required_transition_receipt_key_count": 9,
                "missing_required_transition_receipt_key_count": 8,
                "disposition": "GOVERNANCE_ORDERING_AND_PROTOCOL_CONFORMANCE_VIOLATION__NOT_RETROACTIVE_PREAUTHORIZATION__SCIENTIFIC_RAW_FACTS_UNCHANGED",
            },
            "one_attempt_boundary": {
                "canonical_recorded_transaction_http_attempt_count": 1,
                "provider_rate_limit_headers_corroborate_one_billable_request": True,
                "evidence_of_any_second_live_attempt_found": False,
                "global_exactly_once_mechanically_enforced": False,
                "fresh_output_paths_can_reenter_fetch_loop": True,
                "controlling_wording": "EXACTLY_ONE_HTTP_ATTEMPT_IN_THE_CANONICAL_RECORDED_TRANSACTION__NO_EVIDENCE_OF_ANOTHER_ATTEMPT__NOT_A_GLOBAL_MECHANICAL_ATTESTATION",
            },
            "terminal_attribution": {
                "immutable_historical_reason_id": "OPENALEX_SCHEMA_OR_IDENTITY_INVALID__NO_PARTIAL_UNIVERSE",
                "immutable_reason_id_edited": False,
                "controlling_causal_attribution": "RTDL_REVIEWED_PARSER_HTTPS_ONLY_CONSTRAINT_APPLIED_AS_FATAL_RAW_RECORD_RULE__PROVIDER_RESPONSE_WAS_VALID",
                "provider_data_was_invalid": False,
                "fault_is_internal": True,
                "parser_repair_or_rerun_authorized": False,
            },
            "controlling_alias_implementation_gap": {
                "alias_v2_identity_verified": True,
                "alias_v2_rows_operationally_consumed": False,
                "runtime_rebuilt_rows_from_x1_registry": True,
                "different_operational_projection_row_count": 8,
                "different_citation_keys": [
                    "Markidis2018NVIDIATC",
                    "Martin2014PostDennardSA",
                    "bedorf2012sparse",
                    "bedorf2019bonsai",
                    "bhm2020spacefilling",
                    "el2018techniques",
                    "jarzabek2017a",
                    "jarząbek2017b",
                ],
                "affected_this_terminal_prepopulation_result": False,
                "current_runtime_alias_implementation_approved_for_reuse": False,
            },
            "branch_label_resolution": {
                "external_review_literal": "GOAL5793_PROSPECTIVE_GENERALIZATION_BRANCH__TERMINAL_NEGATIVE__UNDISCHARGED",
                "controlling_scientific_execution_disposition": "TERMINAL_SEARCH_INFRASTRUCTURE_FAILURE__NO_COMPLETE_POPULATION__NO_SCIENTIFIC_RESULT",
                "terminal_negative_means_only_no_further_prospective_generalization_work_inside_goal5793": True,
                "terminal_negative_means_zero_candidates_or_scientific_zero_of_three": False,
                "goal5793_generality_objective_discharged": False,
            },
            "historical_actions": {
                "reviewed_byte_edited": False,
                "network_reexecution_count": 0,
                "parser_or_product_change_count": 0,
                "partial_population_use_count": 0,
                "retroactive_preauthorization_claimed": False,
            },
            "authorization": {
                "terminal_owner_closure": True,
                "parser_repair_or_rerun": False,
                "successor_preregistration": False,
                "science_entropy_selection_candidate_work": False,
                "gpu_ssh_pod_timing": False,
                "product_change": False,
                "publication_submission": False,
            },
            "amendment_sha256": "",
        },
        "amendment_sha256",
        AMENDMENT_DOMAIN,
    )
    amendment_bytes = _json_bytes(amendment)

    closure = _sealed(
        {
            "schema": "rtdl.goal5793.x3.terminal_owner_closure_and_a1_entry.v1",
            "goal": 5793,
            "stage": "X3_TERMINAL_OWNER_CLOSURE",
            "date": DATE,
            "status": "GOAL5793_TERMINAL_REVIEWED__GENERALITY_OBJECTIVE_PERMANENTLY_UNDISCHARGED_WITHIN_GOAL5793__A1_OBSERVED_EXPOSURE_CORRECTION_ONLY_AUTHORIZED",
            "bindings": {
                "external_review": roots["history/internal_docs/review_goal5793_x3_provider_search_terminal_failure_20260822.md"],
                "strict_self_review": roots["history/internal_docs/self_review_goal5793_x3_provider_search_terminal_lineage_20260823.md"],
                "review_absorption": _generated_identity(ABSORPTION_NAME, absorption_bytes),
                "governance_and_attribution_amendment": _generated_identity(AMENDMENT_NAME, amendment_bytes),
                "journal": roots["history/internal_docs/goal5793_x3_provider_search_journal_20260822.jsonl"],
            },
            "terminal_disposition": {
                "x3_search_completed": False,
                "candidate_population_constructed": False,
                "candidate_count": None,
                "candidate_count_semantics": "UNDEFINED__NO_COMPLETE_POPULATION_EXISTS",
                "generalization_exam_count": 0,
                "usability_study_count": 0,
                "matched_cuda_optix_baseline_count": 0,
                "goal5793_may_be_reopened": False,
                "goal5793_prospective_generalization_objective_undischarged_forever": True,
                "scientific_result": "TERMINAL_SEARCH_INFRASTRUCTURE_FAILURE__NOT_ZERO_CANDIDATES__NOT_ZERO_OF_THREE",
            },
            "open_review_findings": {
                "external_p1_observed_200_work_exposure_registry": True,
                "successor_preregistration_blocked_until_registry_external_review": True,
                "additional_internal_findings_silently_closed": False,
                "current_runtime_alias_implementation_reuse_allowed": False,
            },
            "a1_scope": {
                "name": "GOAL5793_X3_A1_OBSERVED_EXPOSURE_AND_TERMINAL_RECORD_CORRECTION_ONLY",
                "local_cpu_and_offline_only": True,
                "derive_exactly_200_observed_work_rows_from_frozen_journal": True,
                "every_observed_row_selection_eligible": False,
                "freeze_no_reuse_of_observed_rows": True,
                "freeze_internal_terminal_attribution_and_bounded_methodology_finding": True,
                "deterministic_hostile_tests_required": True,
                "lossless_base64_single_cfr_required": True,
                "external_review_required_before_external_p1_can_close": True,
                "successful_a1_review_automatically_authorizes_successor_preregistration": False,
                "allowed_create_only_roots": [
                    "scripts/goal5793_x3_a1_*",
                    "tests/goal5793_x3_a1_*",
                    "history/internal_docs/goal5793_x3_a1_*",
                    "history/internal_docs/call_for_review_goal5793_x3_a1_*",
                ],
            },
            "authorization": {
                "goal5793_x3_a1_observed_exposure_and_terminal_record_correction": True,
                "successor_preregistration": False,
                "http_or_provider_call": False,
                "parser_runtime_core_native_product_application_change": False,
                "partial_page_population_or_candidate_use": False,
                "full_text_science_taxonomy_triplet_work": False,
                "live_beacon_entropy_selection_candidate_execution": False,
                "gpu_home_pod_ssh_worker_timing": False,
                "generalization_usability_productivity_or_performance_claim": False,
                "public_release_publication_submission": False,
            },
            "required_next_action": "COMPLETE_BOUNDED_OFFLINE_A1__SEND_EXACTLY_ONE_SELF_CONTAINED_CFR_FOR_EXTERNAL_REVIEW__DO_NOT_REOPEN_GOAL5793_OR_ENTER_A_SUCCESSOR_PROTOCOL",
            "closure_sha256": "",
        },
        "closure_sha256",
        CLOSURE_DOMAIN,
    )
    closure_bytes = _json_bytes(closure)

    return {
        ABSORPTION_NAME: absorption_bytes,
        AMENDMENT_NAME: amendment_bytes,
        CLOSURE_NAME: closure_bytes,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=HISTORY)
    parser.add_argument("--write-create-only", action="store_true")
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    if args.write_create_only and args.verify_stored:
        parser.error("write and verify are mutually exclusive")
    documents = build_documents()
    if args.write_create_only:
        targets = [args.output_dir / name for name in documents]
        if any(path.exists() or path.is_symlink() for path in targets):
            raise SystemExit("CREATE_ONLY_OUTPUT_EXISTS")
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, payload in documents.items():
            with (args.output_dir / name).open("xb") as stream:
                stream.write(payload)
        status = "CREATE_ONLY_X3_TERMINAL_CLOSURE_WRITE_PASS"
    elif args.verify_stored:
        for name, payload in documents.items():
            path = args.output_dir / name
            if not path.is_file() or path.is_symlink() or path.read_bytes() != payload:
                raise SystemExit(f"STORED_OUTPUT_MISMATCH:{name}")
        status = "X3_TERMINAL_CLOSURE_STORED_VERIFY_PASS"
    else:
        status = "X3_TERMINAL_CLOSURE_DRY_RUN_PASS"
    print(
        json.dumps(
            {
                "status": status,
                "documents": [
                    {"path": name, "bytes": len(payload), "sha256": _sha(payload)}
                    for name, payload in documents.items()
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
