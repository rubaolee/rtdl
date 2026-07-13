#!/usr/bin/env python3
"""Validate and classify X-HD external response intake JSON.

This script is intentionally app-owned. It validates the X-HD paper
reproduction response-intake shape created by Goal5329 and emits a
fail-closed decision record. It does not send requests, download artifacts, or
run author/RTDL gates.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any, Dict, Iterable, List, Tuple


SUPPORTED_RESPONSE_TYPES = {
    "author_hash_manifest",
    "author_input_archive",
    "byte_identical_regeneration_script",
    "acm_supplement_artifact_instructions",
    "exact_equivalence_verdict",
    "explicit_non_availability_statement",
    "other",
}


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _require_path(root: Dict[str, Any], path: Iterable[str], errors: List[str]) -> Any:
    cur: Any = root
    parts = list(path)
    for part in parts:
        if not isinstance(cur, dict) or part not in cur:
            errors.append("missing field: " + ".".join(parts))
            return None
        cur = cur[part]
    return cur


def _require_nonempty_path(root: Dict[str, Any], path: Iterable[str], errors: List[str]) -> Any:
    value = _require_path(root, path, errors)
    if value is not None and not _is_nonempty_string(value):
        errors.append("empty field: " + ".".join(path))
    return value


def _default_claim_boundary() -> Dict[str, bool]:
    return {
        "external_response_received": False,
        "external_artifacts_acquired": False,
        "acm_supplement_inspected": False,
        "exact_equivalence_accepted": False,
        "exact_paper_dataset_reproduction_claimed": False,
        "figure5_reproduction_claimed": False,
        "full_paper_reproduction_claimed": False,
        "performance_ratio_claimed": False,
    }


def _validate_hash_manifest(artifacts: Dict[str, Any], errors: List[str]) -> Tuple[bool, str]:
    entries = _as_list(artifacts.get("hash_manifest_entries"))
    if not entries:
        errors.append("author_hash_manifest requires artifacts.hash_manifest_entries")
        return False, "missing_hash_entries"
    has_bytes = False
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"hash_manifest_entries[{idx}] must be an object")
            continue
        if not (_is_nonempty_string(entry.get("paper_input_path")) or _is_nonempty_string(entry.get("logical_workload_row"))):
            errors.append(f"hash_manifest_entries[{idx}] requires paper_input_path or logical_workload_row")
        if not _is_nonempty_string(entry.get("hash_algorithm")):
            errors.append(f"hash_manifest_entries[{idx}] requires hash_algorithm")
        if not _is_nonempty_string(entry.get("hash_value")):
            errors.append(f"hash_manifest_entries[{idx}] requires hash_value")
        has_bytes = has_bytes or bool(entry.get("input_bytes_available")) or _is_nonempty_string(entry.get("local_path"))
    if has_bytes:
        return True, "hashes_with_candidate_bytes__verify_hashes_then_pod_gate"
    return False, "hashes_only__compare_or_request_bytes_before_pod"


def _validate_archive(artifacts: Dict[str, Any], errors: List[str]) -> Tuple[bool, str]:
    archive = _as_dict(artifacts.get("archive"))
    if not archive:
        errors.append("author_input_archive requires artifacts.archive")
        return False, "missing_archive"
    for key in ["filename", "sha256", "redistribution_boundary", "extraction_policy"]:
        if not _is_nonempty_string(archive.get(key)):
            errors.append(f"archive requires {key}")
    if not _as_list(archive.get("file_listing")):
        errors.append("archive requires non-empty file_listing")
    return True, "archive_present__record_hashes_extract_then_pod_gate"


def _validate_regeneration(artifacts: Dict[str, Any], errors: List[str]) -> Tuple[bool, str]:
    script = _as_dict(artifacts.get("regeneration_script"))
    if not script:
        errors.append("byte_identical_regeneration_script requires artifacts.regeneration_script")
        return False, "missing_regeneration_script"
    for key in ["reference", "commit_or_archive_hash"]:
        if not _is_nonempty_string(script.get(key)):
            errors.append(f"regeneration_script requires {key}")
    if not _as_list(script.get("source_snapshots")):
        errors.append("regeneration_script requires source_snapshots")
    if not _as_list(script.get("commands")):
        errors.append("regeneration_script requires commands")
    if not _as_list(script.get("expected_output_hashes")):
        errors.append("regeneration_script requires expected_output_hashes")
    return True, "regeneration_present__run_regeneration_then_pod_gate"


def _validate_acm_listing(artifacts: Dict[str, Any], errors: List[str]) -> Tuple[bool, str, bool]:
    listing = _as_dict(artifacts.get("acm_supplement_listing"))
    if not listing:
        errors.append("acm_supplement_artifact_instructions requires artifacts.acm_supplement_listing")
        return False, "missing_acm_listing", False
    if not _as_list(listing.get("top_level_files")):
        errors.append("acm_supplement_listing requires top_level_files")
    has_artifact = bool(listing.get("contains_artifact_material"))
    if has_artifact and not (
        _as_list(listing.get("dataset_or_hash_entries"))
        or _as_list(listing.get("script_or_instruction_entries"))
    ):
        errors.append("artifact-bearing ACM listing requires dataset/hash or script/instruction entries")
    if has_artifact:
        return False, "acm_artifact_instructions_present__ingest_before_pod", True
    return False, "acm_listing_inspected_no_actionable_artifact__keep_blocked", True


def _validate_equivalence(artifacts: Dict[str, Any], errors: List[str]) -> Tuple[bool, str, bool]:
    verdict = _as_dict(artifacts.get("exact_equivalence_verdict"))
    if not verdict:
        errors.append("exact_equivalence_verdict requires artifacts.exact_equivalence_verdict")
        return False, "missing_equivalence_verdict", False
    decision = verdict.get("decision")
    allowed = {
        "accepted_as_exact_equivalent_with_named_boundary",
        "accepted_only_as_level_b_public_reconstruction",
        "rejected_keep_level_b",
    }
    if decision not in allowed:
        errors.append("exact_equivalence_verdict.decision must be one of: " + ", ".join(sorted(allowed)))
        return False, "invalid_equivalence_decision", False
    if not _is_nonempty_string(verdict.get("reviewed_reconstruction")):
        errors.append("exact_equivalence_verdict requires reviewed_reconstruction")
    if decision == "accepted_as_exact_equivalent_with_named_boundary":
        if not _is_nonempty_string(verdict.get("accepted_claim_name")):
            errors.append("accepted exact-equivalence requires accepted_claim_name")
        if not _is_nonempty_string(verdict.get("accepted_denominator")):
            errors.append("accepted exact-equivalence requires accepted_denominator")
        return True, "exact_equivalence_accepted__run_accepted_bounded_matrix", True
    if decision == "accepted_only_as_level_b_public_reconstruction":
        return False, "accepted_level_b_only__do_not_claim_exact", False
    return False, "equivalence_rejected__keep_level_b", False


def _validate_nonavailability(artifacts: Dict[str, Any], errors: List[str]) -> Tuple[bool, str]:
    notes = artifacts.get("freeform_notes")
    if not _is_nonempty_string(notes):
        errors.append("explicit_non_availability_statement requires artifacts.freeform_notes")
    return False, "non_availability_statement__keep_blocked"


def classify_intake(payload: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    schema = payload.get("schema")
    if schema != "rtdl.paper_reproduction.xhd.external_response_intake.v1":
        errors.append("schema must be rtdl.paper_reproduction.xhd.external_response_intake.v1")
    if payload.get("status") == "template_not_filled":
        errors.append("template_not_filled is not a usable response")

    _require_nonempty_path(payload, ["received_from", "actor_type"], errors)
    _require_nonempty_path(payload, ["received_from", "name_or_role"], errors)
    _require_nonempty_path(payload, ["received_from", "received_date"], errors)

    response_type = payload.get("response_type")
    if response_type not in SUPPORTED_RESPONSE_TYPES:
        errors.append("unsupported response_type")

    scope = _as_dict(payload.get("scope"))
    if scope.get("paper") != "X-HD":
        errors.append("scope.paper must be X-HD")

    artifacts = _as_dict(payload.get("artifacts"))
    pod_expected = False
    exact_equivalence_accepted = False
    acm_supplement_inspected = False
    next_action = "classify_response_before_action"

    if response_type == "author_hash_manifest":
        pod_expected, next_action = _validate_hash_manifest(artifacts, errors)
    elif response_type == "author_input_archive":
        pod_expected, next_action = _validate_archive(artifacts, errors)
    elif response_type == "byte_identical_regeneration_script":
        pod_expected, next_action = _validate_regeneration(artifacts, errors)
    elif response_type == "acm_supplement_artifact_instructions":
        pod_expected, next_action, acm_supplement_inspected = _validate_acm_listing(artifacts, errors)
    elif response_type == "exact_equivalence_verdict":
        pod_expected, next_action, exact_equivalence_accepted = _validate_equivalence(artifacts, errors)
    elif response_type == "explicit_non_availability_statement":
        pod_expected, next_action = _validate_nonavailability(artifacts, errors)
    elif response_type == "other":
        if not _is_nonempty_string(artifacts.get("freeform_notes")):
            warnings.append("other response has no freeform_notes")
        pod_expected = False
        next_action = "unknown_response__manual_review_keep_blocked"

    valid = not errors
    claim_boundary = _default_claim_boundary()
    claim_boundary["external_response_received"] = valid
    claim_boundary["acm_supplement_inspected"] = valid and acm_supplement_inspected
    claim_boundary["exact_equivalence_accepted"] = valid and exact_equivalence_accepted
    claim_boundary["external_artifacts_acquired"] = valid and response_type == "author_input_archive"

    return {
        "schema": "rtdl.paper_reproduction.xhd.external_response_intake.validation_result.v1",
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
        "response_type": response_type,
        "next_action": next_action,
        "pod_expected": bool(valid and pod_expected),
        "sufficient_to_claim_exact_input": False,
        "requires_review_before_claim": True,
        "claim_boundary": claim_boundary,
        "not_allowed": [
            "claiming exact paper dataset reproduction from this validation result alone",
            "claiming Figure 5 reproduction from this validation result alone",
            "claiming full X-HD paper reproduction from this validation result alone",
            "claiming author-vs-RTDL performance ratio from this validation result alone",
        ],
    }


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("top-level JSON must be an object")
    return data


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("response_json", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    result = classify_intake(load_json(args.response_json))
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
