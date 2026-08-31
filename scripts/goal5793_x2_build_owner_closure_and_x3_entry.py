#!/usr/bin/env python3
"""Build the append-only X2 owner closure that conditionally unlocks X3 search."""

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
DEFAULT_OUTPUT = ROOT / "history/internal_docs/goal5793_x2_postreview_owner_closure_and_x3_provider_search_entry_20260822.json"
DOMAIN = "rtdl.goal5793.x2.postreview_owner_closure_and_x3_provider_search_entry"

PINNED = {
    "history/internal_docs/call_for_review_goal5793_x2_postreview_amendment_and_x3_search_entry_20260822.md": (536328, "ee81ee833d3d74d49a53686dff5285b6051c5d805299db781bc56ca0efe42a76"),
    "history/internal_docs/goal5793_x2_postreview_amendment_authority_20260822.json": (8833, "0606a663b02b2744ab9d1f4ef7c89b53eae7f95deb822fe610ac573a8d5fc929"),
    "history/internal_docs/goal5793_x2_postreview_amendment_report_20260822.md": (2224, "9414de6544be7aacebabb23460c3e4b13c9c035c3511e4b204dc081ab586044b"),
    "history/internal_docs/review_goal5793_x2_postreview_amendment_and_x3_search_entry_20260822.md": (38691, "f5b80f97f25baacace78a78e10a182da9a1d42a5bb3418b18a035ef6f914114b"),
    "scripts/goal5793_x2_preentropy_enumerator_v2.py": (9646, "e4c882d2bcf75b1f18d12023c6706b02c75b4c9e0d15ecb898a9ccd879368d24"),
    "scripts/goal5793_x2_structural_friction_v2.py": (10650, "320f81dd4aa1c21b6f3f83ced88379102b62673c7076b16998e306dea0f7518b"),
    "history/internal_docs/goal5793_x2_exposure_alias_authority_v2_20260822.json": (461251, "72a30e8b2a8998507ca2f27517346006f62ef6b370f9777a54bddf9dd8edae8b"),
}


def _identity(relative: str) -> dict[str, Any]:
    data = (ROOT / relative).read_bytes()
    return {"path": relative, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _verify_pins() -> None:
    for relative, (size, digest) in PINNED.items():
        identity = _identity(relative)
        if identity["bytes"] != size or identity["sha256"] != digest:
            raise RuntimeError(f"PINNED_ROOT_IDENTITY_MISMATCH:{relative}")


def build_closure() -> dict[str, Any]:
    _verify_pins()
    document: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.postreview_owner_closure_and_x3_provider_search_entry.v1",
        "date": "2026-08-22",
        "status": "X2_OWNER_CLOSED__P1_CLOSED_BY_CONTROLLING_BINDING__X3_PROVIDER_SEARCH_ONLY_AUTHORIZED",
        "returned_external_review": _identity(
            "history/internal_docs/review_goal5793_x2_postreview_amendment_and_x3_search_entry_20260822.md"
        ),
        "review_verdict_absorbed": {
            "P0": 0,
            "P1": 1,
            "P1_disposition": "CLOSED_BY_THIS_OWNER_CLOSURE_CONTROLLING_IMPLEMENTATIONS_BINDING",
            "P2": 4,
            "P3": 2,
            "review_permits_same_closure_to_close_P1_and_authorize_x3_provider_search_only": True,
        },
        "reviewed_amendment_roots": [
            _identity("history/internal_docs/call_for_review_goal5793_x2_postreview_amendment_and_x3_search_entry_20260822.md"),
            _identity("history/internal_docs/goal5793_x2_postreview_amendment_authority_20260822.json"),
            _identity("history/internal_docs/goal5793_x2_postreview_amendment_report_20260822.md"),
        ],
        "controlling_implementations": {
            "preentropy_enumerator": _identity("scripts/goal5793_x2_preentropy_enumerator_v2.py"),
            "structural_friction": _identity("scripts/goal5793_x2_structural_friction_v2.py"),
            "exposure_alias_authority": _identity(
                "history/internal_docs/goal5793_x2_exposure_alias_authority_v2_20260822.json"
            ),
            "v1_predecessors_may_produce_a_stage_of_record_output": False,
            "v1_predecessors_retained_for": "IMMUTABLE_REVIEWED_HISTORY_AND_SUCCESSOR_DELEGATION_ONLY",
            "any_future_enumeration_or_friction_output_not_produced_by_the_named_successors":
                "INVALID__NOT_A_STAGE_OF_RECORD",
        },
        "p2_p3_absorption": {
            "friction_v2_device_language_and_CU_lowercase_coverage_complete": False,
            "friction_v2_C_CPP_literal_masker_sound_for_digit_separators_and_unterminated_literals": False,
            "friction_number_may_appear_in_any_written_claim": False,
            "required_before_any_friction_claim": "APPEND_ONLY_V3_REPAIR_TEST_FREEZE_AND_CONTROLLING_SUCCESSOR_BINDING",
            "science_row_set_digest_bound_to_harvested_components": False,
            "required_before_science_row_construction": "EXACT_SOURCE_COMPONENT_AUTHORITY_AND_SET_EQUALITY_GATE",
            "sampling_frame_funnel_ledger_complete": False,
            "required_before_selection": "SEALED_FULL_FUNNEL_LEDGER_FROM_QUERY_RESPONSES_THROUGH_TRIPLETS",
            "friction_second_read_reverified": False,
            "crypto_cross_platform_comparison_projection_corrected": False,
            "required_before_live_beacon": "LINUX_TCB_FREEZE_AND_VERIFICATION_OUTCOME_PROJECTION_REVIEW",
        },
        "x3_provider_search_scope": {
            "single_expansion_only": True,
            "query_terms_or_providers_may_change": False,
            "must_follow_frozen_S0_X2_provider_order_terms_pagination_retry_and_failure_policy": True,
            "all_raw_requests_attempts_headers_bodies_errors_and_UTC_times_preserved": True,
            "partial_universe_allowed": False,
            "postsearch_manual_row_deletion_or_vocabulary_extension_allowed": False,
            "provider_search_output_is_generalization_evidence": False,
            "provider_search_output_is_usability_evidence": False,
        },
        "authorization": {
            "x3_provider_search": True,
            "x3_science_row_construction": False,
            "full_text_source_resolution": False,
            "candidate_implementation": False,
            "candidate_execution": False,
            "live_nist_beacon": False,
            "entropy": False,
            "selection": False,
            "gpu": False,
            "ssh": False,
            "pod": False,
            "timing": False,
            "product_change": False,
            "publication": False,
            "submission": False,
        },
        "claim_boundary": {
            "generality_exam_count": 0,
            "usability_study_count": 0,
            "functionally_matched_direct_cuda_optix_baseline_count": 0,
            "generalization_claim_earned": False,
            "usability_or_productivity_claim_earned": False,
            "selection_measure_unit": "IDENTITY_COMPONENTS_NOT_PROVEN_UNDERLYING_WORKS",
        },
        "closure_sha256": "",
    }
    document["closure_sha256"] = seal_document(
        document, seal_field="closure_sha256", domain=DOMAIN, version=1
    )
    return document


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write-create-only", action="store_true")
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    if args.write_create_only and args.verify_stored:
        parser.error("write and verify are mutually exclusive")
    payload = canonical_json_bytes(build_closure()) + b"\n"
    if args.write_create_only:
        if args.output.exists() or args.output.is_symlink():
            raise SystemExit("CREATE_ONLY_OUTPUT_ALREADY_EXISTS")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
        status = "CREATE_ONLY_WRITE_PASS__X3_PROVIDER_SEARCH_ONLY_AUTHORIZED"
    elif args.verify_stored:
        if not args.output.is_file() or args.output.is_symlink() or args.output.read_bytes() != payload:
            raise SystemExit("STORED_CLOSURE_MISMATCH")
        status = "POSTWRITE_VERIFY_PASS__X3_PROVIDER_SEARCH_ONLY_AUTHORIZED"
    else:
        status = "DRY_RUN_PASS__X3_PROVIDER_SEARCH_ONLY_AUTHORIZED"
    print(json.dumps({
        "status": status,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "closure_sha256": json.loads(payload)["closure_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
