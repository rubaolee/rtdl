#!/usr/bin/env python3
"""Validate mapping of hashed X-HD candidate files to paper workloads.

This app-owned helper follows ``map_xhd_acm_candidate_bytes_hashes.py``. It
checks that candidate files with verified hashes are explicitly mapped to paper
workload roles (input1/input2), known paper dataset names, direction, dimension,
and input type. It does not run POD, author binaries, or RTDL.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any, Dict, Iterable, List, Set


ROOT = pathlib.Path(__file__).resolve().parents[3]
DEFAULT_TARGET_MATRIX = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_paper_target_matrix_2026-07-08.json"
)

VALID_DIRECTIONS = {"input1_to_input2"}
VALID_INPUT_TYPES = {"image", "wkt", "ply", "off"}
VALID_DIMS = {2, 3}
MATCHED_STATUSES = {"matched_by_path_and_sha256", "matched_by_sha256_only"}


def _load_json(path: pathlib.Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _candidate_index(candidate_mapping: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    for record in candidate_mapping.get("candidate_mappings", []):
        if isinstance(record, dict) and "path" in record:
            index[str(record["path"]).replace("\\", "/")] = record
    return index


def _target_dataset_names(target_matrix: Dict[str, Any]) -> Set[str]:
    names: Set[str] = set()
    for record in target_matrix.get("dataset_table_targets", []):
        if isinstance(record, dict) and record.get("name"):
            names.add(str(record["name"]))
    return names


def _validate_input_role(
    role: str,
    payload: Any,
    candidate_by_path: Dict[str, Dict[str, Any]],
    dataset_names: Set[str],
    errors: List[str],
) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        errors.append(f"{role} must be an object")
        return {}
    candidate_path = str(payload.get("candidate_path", "")).replace("\\", "/")
    dataset_name = str(payload.get("paper_dataset_name", ""))
    if not candidate_path:
        errors.append(f"{role}.candidate_path missing")
    elif candidate_path not in candidate_by_path:
        errors.append(f"{role}.candidate_path is not present in candidate hash mapping: {candidate_path}")
    else:
        status = str(candidate_by_path[candidate_path].get("status", ""))
        if status not in MATCHED_STATUSES:
            errors.append(f"{role}.candidate_path does not have a matched hash status: {candidate_path} -> {status}")
    if not dataset_name:
        errors.append(f"{role}.paper_dataset_name missing")
    elif dataset_name not in dataset_names:
        errors.append(f"{role}.paper_dataset_name not in paper target matrix: {dataset_name}")
    return {
        "role": role,
        "candidate_path": candidate_path,
        "paper_dataset_name": dataset_name,
        "hash_status": str(candidate_by_path.get(candidate_path, {}).get("status", "")),
    }


def _validate_workload(
    workload: Any,
    candidate_by_path: Dict[str, Dict[str, Any]],
    dataset_names: Set[str],
) -> Dict[str, Any]:
    errors: List[str] = []
    if not isinstance(workload, dict):
        return {"valid": False, "errors": ["workload mapping must be an object"]}

    workload_id = str(workload.get("workload_id", ""))
    if not workload_id:
        errors.append("workload_id missing")
    figure = str(workload.get("figure", ""))
    direction = str(workload.get("direction", ""))
    input_type = str(workload.get("input_type", ""))
    try:
        n_dims = int(workload.get("n_dims"))
    except Exception:
        n_dims = -1
    if direction not in VALID_DIRECTIONS:
        errors.append(f"direction must be one of {sorted(VALID_DIRECTIONS)}")
    if input_type not in VALID_INPUT_TYPES:
        errors.append(f"input_type must be one of {sorted(VALID_INPUT_TYPES)}")
    if n_dims not in VALID_DIMS:
        errors.append("n_dims must be 2 or 3")

    input1 = _validate_input_role("input1", workload.get("input1"), candidate_by_path, dataset_names, errors)
    input2 = _validate_input_role("input2", workload.get("input2"), candidate_by_path, dataset_names, errors)
    if input1.get("candidate_path") and input1.get("candidate_path") == input2.get("candidate_path"):
        errors.append("input1 and input2 candidate paths must differ")

    evidence = workload.get("mapping_evidence", [])
    if not isinstance(evidence, list) or not evidence:
        errors.append("mapping_evidence must be a non-empty list")

    return {
        "workload_id": workload_id,
        "figure": figure,
        "direction": direction,
        "input_type": input_type,
        "n_dims": n_dims,
        "input1": input1,
        "input2": input2,
        "mapping_evidence_count": len(evidence) if isinstance(evidence, list) else 0,
        "valid": not errors,
        "errors": errors,
    }


def build_review(candidate_mapping_path: pathlib.Path, mapping_spec_path: pathlib.Path, target_matrix_path: pathlib.Path) -> Dict[str, Any]:
    candidate_mapping = _load_json(candidate_mapping_path)
    mapping_spec = _load_json(mapping_spec_path)
    target_matrix = _load_json(target_matrix_path)

    errors: List[str] = []
    if candidate_mapping.get("schema") != "rtdl.paper_reproduction.xhd.acm_candidate_bytes_hash_mapping.v1":
        errors.append("candidate mapping schema mismatch")
    if mapping_spec.get("schema") != "rtdl.paper_reproduction.xhd.candidate_workload_mapping_spec.v1":
        errors.append("mapping spec schema mismatch")

    candidate_classification = str(candidate_mapping.get("classification", ""))
    if candidate_classification != "all_candidate_hashes_matched__workload_mapping_required":
        errors.append(f"candidate mapping is not clean: {candidate_classification}")

    dataset_names = _target_dataset_names(target_matrix)
    if not dataset_names:
        errors.append("target matrix has no dataset_table_targets names")

    review_status = str(mapping_spec.get("external_mapping_review_status", ""))
    if review_status not in {"proposed", "accepted"}:
        errors.append("external_mapping_review_status must be proposed or accepted")

    candidate_by_path = _candidate_index(candidate_mapping)
    workload_reviews = [
        _validate_workload(workload, candidate_by_path, dataset_names)
        for workload in mapping_spec.get("workload_mappings", [])
    ]
    if not workload_reviews:
        errors.append("workload_mappings must contain at least one mapping")

    invalid_count = sum(1 for record in workload_reviews if not record.get("valid"))
    all_valid = not errors and invalid_count == 0
    if all_valid and review_status == "accepted":
        classification = "accepted_workload_mapping_ready_for_same_input_gate"
        recommended_goal_type = "mapped_candidate_same_input_author_rtdl_gate"
        pod_allowed_next = True
    elif all_valid:
        classification = "proposed_workload_mapping_requires_external_acceptance"
        recommended_goal_type = "external_workload_mapping_acceptance_review"
        pod_allowed_next = False
    else:
        classification = "workload_mapping_invalid_or_incomplete"
        recommended_goal_type = "repair_candidate_workload_mapping"
        pod_allowed_next = False

    return {
        "schema": "rtdl.paper_reproduction.xhd.candidate_workload_mapping_review.v1",
        "candidate_mapping_path": str(candidate_mapping_path),
        "mapping_spec_path": str(mapping_spec_path),
        "target_matrix_path": str(target_matrix_path),
        "external_mapping_review_status": review_status,
        "classification": classification,
        "recommended_goal_type": recommended_goal_type,
        "pod_allowed_next": pod_allowed_next,
        "requires_separate_pod_goal": True,
        "sufficient_to_claim_exact_input": False,
        "workload_review_count": len(workload_reviews),
        "invalid_workload_review_count": invalid_count,
        "workload_reviews": workload_reviews,
        "errors": errors,
        "claim_boundary": {
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
        },
        "not_allowed": [
            "claiming exact paper input reproduction from workload mapping alone",
            "claiming Figure 5 reproduction from workload mapping alone",
            "claiming full X-HD paper reproduction from workload mapping alone",
            "claiming author-vs-RTDL performance ratio from workload mapping alone",
            "running POD outside the recommended separate same-input gate",
        ],
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate_mapping_json", type=pathlib.Path)
    parser.add_argument("mapping_spec_json", type=pathlib.Path)
    parser.add_argument("--target-matrix", type=pathlib.Path, default=DEFAULT_TARGET_MATRIX)
    parser.add_argument("--output", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    try:
        review = build_review(args.candidate_mapping_json, args.mapping_spec_json, args.target_matrix)
    except Exception as exc:
        print(f"workload mapping review failed: {exc}", file=sys.stderr)
        return 2

    text = json.dumps(review, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
