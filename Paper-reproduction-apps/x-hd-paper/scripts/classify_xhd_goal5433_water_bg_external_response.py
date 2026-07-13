#!/usr/bin/env python3
"""Classify Water/BG external responses for X-HD exact-input/equivalence gates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP / "results"
REQUESTS = APP / "requests"
GOAL5430 = RESULTS / "xhd_goal5430_water_bg_exact_equivalence_packet.json"
OUT = RESULTS / "xhd_goal5433_water_bg_external_response_classifier_contract.json"

REQUIRED_PAPER_PATHS = {
    "USADetailedWaterBodies.wkt": "waterbodies",
    "USACensusBlockGroupBoundaries.wkt": "blockgroups",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _norm_path(value: str) -> str:
    return str(value).replace("\\", "/").split("/")[-1]


def _hash_entries(response: dict[str, Any]) -> list[dict[str, Any]]:
    entries = response.get("artifacts", {}).get("hash_manifest_entries", [])
    return entries if isinstance(entries, list) else []


def _exact_verdict(response: dict[str, Any]) -> dict[str, Any] | None:
    verdict = response.get("artifacts", {}).get("exact_equivalence_verdict")
    return verdict if isinstance(verdict, dict) else None


def _archive(response: dict[str, Any]) -> dict[str, Any] | None:
    archive = response.get("artifacts", {}).get("archive")
    return archive if isinstance(archive, dict) else None


def _regen(response: dict[str, Any]) -> dict[str, Any] | None:
    script = response.get("artifacts", {}).get("regeneration_script")
    return script if isinstance(script, dict) else None


def _acm_listing(response: dict[str, Any]) -> dict[str, Any] | None:
    listing = response.get("artifacts", {}).get("acm_supplement_listing")
    return listing if isinstance(listing, dict) else None


def _current_hashes(goal5430: dict[str, Any]) -> dict[str, str]:
    evidence = goal5430["public_reconstruction_evidence"]
    return {
        "USADetailedWaterBodies.wkt": evidence["waterbodies"]["generated_wkt_sha256"],
        "USACensusBlockGroupBoundaries.wkt": evidence["blockgroups"]["generated_wkt_sha256"],
    }


def classify_response(response: dict[str, Any], *, goal5430: dict[str, Any] | None = None) -> dict[str, Any]:
    """Classify one normalized external response without upgrading claims."""

    goal5430 = goal5430 or _load(GOAL5430)
    current_hashes = _current_hashes(goal5430)
    response_type = response.get("response_type", "other")
    failures: list[str] = []
    evidence: dict[str, Any] = {}
    sufficient_to_run_pod_gate = False
    sufficient_to_claim_exact_input = False
    exact_equivalence_accepted = False
    recommended_next_action = "keep_level_b__insufficient_or_unknown_response"
    classification = "fail_closed"

    if response_type == "author_hash_manifest":
        found: dict[str, dict[str, Any]] = {}
        for entry in _hash_entries(response):
            path = _norm_path(entry.get("paper_input_path") or entry.get("path") or "")
            if path in REQUIRED_PAPER_PATHS:
                found[path] = entry
        missing = sorted(set(REQUIRED_PAPER_PATHS) - set(found))
        if missing:
            failures.append("missing_required_hash_entries: " + ", ".join(missing))
        matches_current: dict[str, bool] = {}
        algorithms_ok: dict[str, bool] = {}
        for path, entry in found.items():
            algorithm = str(entry.get("hash_algorithm", "")).lower()
            value = str(entry.get("hash_value", "")).lower()
            algorithms_ok[path] = algorithm == "sha256"
            matches_current[path] = value == current_hashes[path].lower()
            if not algorithms_ok[path]:
                failures.append(f"{path}: hash_algorithm_not_sha256")
        evidence = {
            "required_paths": sorted(REQUIRED_PAPER_PATHS),
            "found_paths": sorted(found),
            "current_public_hashes": current_hashes,
            "hashes_match_current_public_reconstruction": matches_current,
            "hash_algorithms_sha256": algorithms_ok,
        }
        if not missing and all(algorithms_ok.values()) and all(matches_current.values()):
            classification = "author_hashes_match_current_public_reconstruction__run_same_input_gate_before_claim"
            sufficient_to_run_pod_gate = True
            sufficient_to_claim_exact_input = False
            recommended_next_action = "run_same_input_author_rtdl_gate_on_current_public_wkt_then_external_review_exact_wording"
        elif not missing and all(algorithms_ok.values()):
            classification = "author_hashes_do_not_match_current_public_reconstruction__need_author_bytes_or_regeneration"
            recommended_next_action = "request_author_bytes_or_byte_identical_regeneration_for_mismatched_hashes"
        else:
            classification = "author_hash_manifest_incomplete__keep_level_b"

    elif response_type == "author_input_archive":
        archive = _archive(response)
        if not archive:
            failures.append("archive_metadata_missing")
            evidence = {}
        else:
            listing = archive.get("contained_files", []) or archive.get("file_listing", [])
            listing_names = {_norm_path(row.get("path", row) if isinstance(row, dict) else row) for row in listing}
            missing = sorted(set(REQUIRED_PAPER_PATHS) - listing_names)
            if missing:
                failures.append("archive_missing_required_files: " + ", ".join(missing))
            if not archive.get("archive_sha256"):
                failures.append("archive_sha256_missing")
            evidence = {
                "archive_name": archive.get("filename") or archive.get("name"),
                "archive_sha256_present": bool(archive.get("archive_sha256")),
                "required_paths": sorted(REQUIRED_PAPER_PATHS),
                "contained_required_paths": sorted(set(REQUIRED_PAPER_PATHS) & listing_names),
            }
            if not missing and archive.get("archive_sha256"):
                classification = "author_input_archive_contains_required_paths__extract_hash_then_run_pod_gate"
                sufficient_to_run_pod_gate = True
                recommended_next_action = "extract_archive_record_file_hashes_then_run_same_input_author_rtdl_gate"
            else:
                classification = "author_input_archive_incomplete__keep_level_b"

    elif response_type == "byte_identical_regeneration_script":
        regen = _regen(response)
        if not regen:
            failures.append("regeneration_script_metadata_missing")
            evidence = {}
        else:
            expected = regen.get("expected_output_hashes", {})
            missing = sorted(path for path in REQUIRED_PAPER_PATHS if path not in expected)
            if missing:
                failures.append("missing_expected_output_hashes: " + ", ".join(missing))
            for path, row in expected.items():
                if _norm_path(path) in REQUIRED_PAPER_PATHS:
                    algorithm = str(row.get("hash_algorithm", "") if isinstance(row, dict) else "").lower()
                    if algorithm and algorithm != "sha256":
                        failures.append(f"{_norm_path(path)}: expected hash algorithm not sha256")
            evidence = {
                "script_or_repository": regen.get("script") or regen.get("repository") or regen.get("path"),
                "commit_or_archive_hash": regen.get("commit") or regen.get("archive_sha256"),
                "expected_output_hash_paths": sorted(expected),
                "required_paths": sorted(REQUIRED_PAPER_PATHS),
            }
            if not missing:
                classification = "byte_identical_regeneration_available__run_regeneration_then_hash_gate"
                sufficient_to_run_pod_gate = True
                recommended_next_action = "run_regeneration_record_hashes_then_same_input_author_rtdl_gate"
            else:
                classification = "byte_identical_regeneration_incomplete__keep_level_b"

    elif response_type == "acm_supplement_artifact_instructions":
        listing = _acm_listing(response)
        if not listing:
            failures.append("acm_supplement_listing_missing")
            evidence = {}
        else:
            files = listing.get("files", [])
            names = [_norm_path(row.get("path", row) if isinstance(row, dict) else row) for row in files]
            has_hash_like = bool(listing.get("hash_manifest_entries")) or any("hash" in name.lower() for name in names)
            has_required = bool(set(names) & set(REQUIRED_PAPER_PATHS))
            has_regen = any("readme" in name.lower() or "script" in name.lower() or name.endswith((".sh", ".py")) for name in names)
            evidence = {
                "zip_sha256_present": bool(listing.get("zip_sha256")),
                "file_count": len(names),
                "required_wkt_present": has_required,
                "hash_like_material_present": has_hash_like,
                "regeneration_like_material_present": has_regen,
            }
            if has_required or has_hash_like or has_regen:
                classification = "acm_supplement_contains_possible_provenance__map_before_route"
                recommended_next_action = "ingest_supplement_listing_map_to_workloads_before_any_pod_route"
            else:
                classification = "acm_supplement_inspected_no_relevant_provenance__keep_level_b"
                recommended_next_action = "record_acm_no_relevant_artifacts_keep_level_b"

    elif response_type == "exact_equivalence_verdict":
        verdict = _exact_verdict(response)
        if not verdict:
            failures.append("exact_equivalence_verdict_missing")
            evidence = {}
        else:
            outcome = str(verdict.get("outcome", ""))
            reviewed = str(verdict.get("reviewed_reconstruction", "")).lower()
            accepted_claim = str(verdict.get("accepted_claim_name", ""))
            water_bg_scope = "water" in reviewed and ("block" in reviewed or "bg" in reviewed)
            evidence = {
                "outcome": outcome,
                "reviewed_reconstruction": verdict.get("reviewed_reconstruction"),
                "accepted_claim_name": accepted_claim,
                "limitations": verdict.get("limitations", []),
                "water_bg_scope_detected": water_bg_scope,
            }
            if outcome == "exact_equivalent_accepted_with_renamed_bounded_public_reconstruction_claim" and water_bg_scope and accepted_claim:
                classification = "exact_equivalence_accepted_for_bounded_public_reconstruction__run_accepted_matrix"
                exact_equivalence_accepted = True
                sufficient_to_run_pod_gate = True
                sufficient_to_claim_exact_input = False
                recommended_next_action = "run_bounded_public_reconstruction_matrix_using_accepted_claim_name"
            elif outcome in {"bounded_public_reconstruction_only_keep_level_b", "not_accepted_keep_level_b"}:
                classification = "exact_equivalence_not_accepted__keep_level_b"
                recommended_next_action = "keep_level_b_no_exact_or_figure_claim"
            else:
                classification = "exact_equivalence_verdict_incomplete_or_wrong_scope__keep_level_b"
                if not water_bg_scope:
                    failures.append("verdict_scope_not_water_bg")
                if not accepted_claim and "accepted" in outcome:
                    failures.append("accepted_claim_name_missing")

    elif response_type == "explicit_non_availability_statement":
        classification = "external_non_availability_statement__keep_level_b_and_record_blocker"
        recommended_next_action = "record_non_availability_keep_level_b"
        evidence = {
            "scope": response.get("scope", {}),
            "notes": response.get("artifacts", {}).get("freeform_notes", ""),
        }

    else:
        classification = "unsupported_or_other_response__manual_review_keep_level_b"
        recommended_next_action = "manual_review_before_action"
        failures.append("unsupported_response_type_or_no_positive_evidence")
        evidence = {"response_type": response_type}

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5433.water_bg_external_response_classification.v1",
        "classification": classification,
        "response_type": response_type,
        "recommended_next_action": recommended_next_action,
        "evidence": evidence,
        "failure_or_missing_items": failures,
        "validation_status": {
            "validated_by_codex": True,
            "sufficient_to_run_pod_gate": sufficient_to_run_pod_gate,
            "sufficient_to_claim_exact_input": sufficient_to_claim_exact_input,
            "requires_external_review_before_use": not exact_equivalence_accepted and not sufficient_to_run_pod_gate,
            "exact_equivalence_accepted": exact_equivalence_accepted,
        },
        "claim_boundary": {
            "external_response_classified": True,
            "external_artifacts_acquired": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "pod_execution_claimed": False,
        },
    }


def build_contract_payload() -> dict[str, Any]:
    goal5430 = _load(GOAL5430)
    current_hashes = _current_hashes(goal5430)
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5433.water_bg_external_response_classifier_contract.v1",
        "goal": "Goal5433",
        "date": "2026-07-10",
        "status": "water_bg_external_response_classifier_ready__await_response",
        "purpose": "Make WaterBodies/BG external response intake fail-closed and machine-classified before any exact/full-paper claim or POD gate.",
        "current_required_paths": sorted(REQUIRED_PAPER_PATHS),
        "current_public_hashes": current_hashes,
        "supported_response_types": [
            "author_hash_manifest",
            "author_input_archive",
            "byte_identical_regeneration_script",
            "acm_supplement_artifact_instructions",
            "exact_equivalence_verdict",
            "explicit_non_availability_statement",
            "other",
        ],
        "allowed_positive_classifications": [
            "author_hashes_match_current_public_reconstruction__run_same_input_gate_before_claim",
            "author_input_archive_contains_required_paths__extract_hash_then_run_pod_gate",
            "byte_identical_regeneration_available__run_regeneration_then_hash_gate",
            "acm_supplement_contains_possible_provenance__map_before_route",
            "exact_equivalence_accepted_for_bounded_public_reconstruction__run_accepted_matrix",
        ],
        "default_classification": "fail_closed_keep_level_b",
        "claim_boundary": {
            "classifier_contract_claimed": True,
            "external_response_received": False,
            "external_artifacts_acquired": False,
            "exact_equivalence_accepted": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "pod_execution_claimed": False,
            "new_rtdl_route_code_added": False,
            "explicit_lb_reopened": False,
            "route_micro_optimization_goal_authorized": False,
        },
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": "external response classifier / provenance intake decision gate",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "PASS: intake governance, not app-artifact parity implementation.",
        },
        "pod_usage": {
            "used": False,
            "expected_next": False,
            "reason": "Classifier contract only. POD becomes useful only for positive classifications that require same-input gates.",
        },
        "next_action": "await_external_response_then_classify_before_action",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, help="Normalized external response JSON to classify.")
    parser.add_argument("--output", type=Path, default=OUT, help="Output JSON path.")
    args = parser.parse_args(argv)

    if args.input:
        payload = classify_response(_load(args.input))
    else:
        payload = build_contract_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"classification": payload.get("classification"), "status": payload.get("status")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
