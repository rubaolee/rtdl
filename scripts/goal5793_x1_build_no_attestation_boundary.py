"""Build/validate the conservative Goal5793 X1 no-memory-attestation boundary."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


SCHEMA = "rtdl.goal5793.x1.no_owner_memory_attestation_boundary.v1"
STATUS = "NO_OWNER_MEMORY_ATTESTATION__NOT_USED_AS_ELIGIBILITY_EVIDENCE__EXTERNAL_REVIEW_REQUIRED"
EXPECTED_RULES = {
    "owner_memory_attestation_requested": False,
    "owner_memory_attestation_provided": False,
    "absence_from_repository_or_declared_registry_proves_unseen": False,
    "unseen_blind_or_held_out_claim_authorized": False,
    "future_claim_term": "not present in the frozen declared exposure registry",
    "all_pre_x1_repository_git_s0_and_pinned_survey_identities_permanently_ineligible": True,
    "later_recalled_or_discovered_pre_x1_exposure_terminates_single_expansion": True,
    "replacement_after_late_exposure_discovery": False,
    "manual_owner_memory_filtering_of_future_candidates": False,
    "x2_requires_external_review_acceptance_and_append_only_owner_closure": True,
}
EXPECTED_BOUNDARY = {
    "complete_human_memory_claimed": False,
    "complete_project_exposure_claimed": False,
    "complete_literature_universe_claimed": False,
    "no_attestation_is_not_evidence_of_no_exposure": True,
    "search_defined_existing_family_bounded_experiment_only": True,
    "generality_exam_count": 0,
    "usability_evidence_count": 0,
}
EXPECTED_AUTHORIZATION = {
    "x1_complete": False,
    "x2_search": False,
    "entropy": False,
    "selection": False,
    "candidate_implementation": False,
    "candidate_execution": False,
    "gpu_home_pod_ssh": False,
    "registered_or_performance_timing": False,
    "external_reviewer_contact": False,
    "public_release_publication_or_submission": False,
}
ROOT_KEYS = {
    "schema", "date", "goal", "status", "reason", "substitution_rules",
    "claim_boundary", "authorization", "boundary_sha256",
}


class BoundaryError(ValueError):
    pass


def build() -> dict[str, Any]:
    document: dict[str, Any] = {
        "schema": SCHEMA,
        "date": "2026-08-22",
        "goal": 5793,
        "status": STATUS,
        "reason": (
            "An unverifiable human-memory completeness statement is not requested, inferred, or fabricated. "
            "The experiment instead adopts stricter late-exposure termination and no-replacement rules."
        ),
        "substitution_rules": deepcopy(EXPECTED_RULES),
        "claim_boundary": deepcopy(EXPECTED_BOUNDARY),
        "authorization": deepcopy(EXPECTED_AUTHORIZATION),
        "boundary_sha256": "",
    }
    document["boundary_sha256"] = seal_document(
        document,
        seal_field="boundary_sha256",
        domain="rtdl.goal5793.x1.no_owner_memory_attestation_boundary",
        version=1,
    )
    return document


def validate(value: object) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != ROOT_KEYS:
        raise BoundaryError("boundary_keyset_mismatch")
    if value.get("schema") != SCHEMA or value.get("date") != "2026-08-22" or value.get("goal") != 5793:
        raise BoundaryError("boundary_identity_mismatch")
    if value.get("status") != STATUS:
        raise BoundaryError("boundary_status_mismatch")
    if canonical_json_bytes(value.get("substitution_rules")) != canonical_json_bytes(EXPECTED_RULES):
        raise BoundaryError("substitution_rules_mismatch")
    if canonical_json_bytes(value.get("claim_boundary")) != canonical_json_bytes(EXPECTED_BOUNDARY):
        raise BoundaryError("claim_boundary_mismatch")
    if canonical_json_bytes(value.get("authorization")) != canonical_json_bytes(EXPECTED_AUTHORIZATION):
        raise BoundaryError("authorization_mismatch")
    expected = seal_document(
        value,
        seal_field="boundary_sha256",
        domain="rtdl.goal5793.x1.no_owner_memory_attestation_boundary",
        version=1,
    )
    if value.get("boundary_sha256") != expected:
        raise BoundaryError("boundary_seal_mismatch")
    return dict(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise BoundaryError("create_only_output_exists")
    document = build()
    validate(document)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as handle:
        handle.write(canonical_json_bytes(document) + b"\n")
    print(document["status"], document["boundary_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
