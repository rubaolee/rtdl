#!/usr/bin/env python3
"""Plan the next X-HD provenance-ingestion step from an intake case.

This app-owned helper reads a case directory produced by
``ingest_xhd_external_response.py`` and emits a fail-closed action plan. It does
not run POD, inspect private artifacts, or change reproduction claims.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any, Dict, List


POD_READY_ACTIONS = {
    "hashes_with_candidate_bytes__verify_hashes_then_pod_gate": {
        "recommended_goal_type": "hash_and_bytes_provenance_ingestion_gate",
        "summary": "Verify candidate bytes against supplied hashes, then run the smallest author/RTDL same-input gate on POD.",
        "required_inputs": [
            "candidate input bytes referenced by the response",
            "hash manifest entries with algorithms and values",
            "author hd_exec or paper-branch contract for the affected workload",
        ],
    },
    "archive_present__record_hashes_extract_then_pod_gate": {
        "recommended_goal_type": "author_archive_provenance_ingestion_gate",
        "summary": "Record archive metadata, extract according to policy outside public repo when needed, then run hash and author/RTDL same-input gates on POD.",
        "required_inputs": [
            "archive filename and sha256",
            "redistribution and extraction policy",
            "file listing or extraction manifest",
        ],
    },
    "regeneration_present__run_regeneration_then_pod_gate": {
        "recommended_goal_type": "byte_identical_regeneration_provenance_gate",
        "summary": "Run the supplied regeneration commands in a controlled workspace, verify expected output hashes, then run author/RTDL same-input gates on POD.",
        "required_inputs": [
            "regeneration script reference and commit/archive hash",
            "source snapshots",
            "commands",
            "expected output hashes",
        ],
    },
    "exact_equivalence_accepted__run_accepted_bounded_matrix": {
        "recommended_goal_type": "accepted_exact_equivalence_bounded_matrix_gate",
        "summary": "Run the externally accepted bounded public reconstruction matrix under the accepted claim denominator.",
        "required_inputs": [
            "accepted claim name",
            "accepted denominator",
            "reviewed reconstruction identifier",
        ],
    },
}


BLOCKED_ACTIONS = {
    "hashes_only__compare_or_request_bytes_before_pod": "Hashes alone are not enough to run a same-input gate. Request bytes or byte-identical regeneration instructions.",
    "acm_listing_inspected_no_actionable_artifact__keep_blocked": "The ACM listing contains no actionable artifact material. Keep exact-input reproduction blocked.",
    "accepted_level_b_only__do_not_claim_exact": "External review accepted only Level-B public reconstruction. Do not claim exact paper dataset reproduction.",
    "equivalence_rejected__keep_level_b": "External review rejected exact equivalence. Keep Level-B status for the affected scope.",
    "non_availability_statement__keep_blocked": "External response states artifacts are unavailable. Keep full-paper reproduction blocked for that scope.",
    "unknown_response__manual_review_keep_blocked": "Unknown response shape needs manual review before any POD or claim update.",
}

INGESTION_READY_NO_POD_ACTIONS = {
    "acm_artifact_instructions_present__ingest_before_pod": {
        "recommended_goal_type": "acm_artifact_instruction_ingestion_gate",
        "summary": "Ingest ACM artifact instructions, classify datasets/hashes/scripts, and only then decide whether a POD gate is justified.",
        "required_inputs": [
            "ACM supplement listing",
            "dataset/hash/script instruction entries",
            "access and redistribution constraints",
        ],
    },
}


def _load_json(path: pathlib.Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _write_json(path: pathlib.Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(path: pathlib.Path, plan: Dict[str, Any]) -> None:
    lines = [
        "# X-HD Provenance Ingestion Action Plan",
        "",
        f"case_id: `{plan['case_id']}`",
        f"plan_status: `{plan['plan_status']}`",
        f"response_type: `{plan['response_type']}`",
        f"next_action: `{plan['next_action']}`",
        f"pod_allowed_next: `{str(plan['pod_allowed_next']).lower()}`",
        "",
        "## Recommendation",
        "",
        plan["recommendation"],
        "",
        "## Required Inputs",
        "",
    ]
    for item in plan["required_inputs"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## POD Rule",
            "",
            "If POD is later used, it must be inside the recommended follow-up",
            "goal and must use `scripts/current_pod_ssh.py`; do not use naked SSH.",
            "",
            "## Not Allowed",
            "",
        ]
    )
    for item in plan["not_allowed"]:
        lines.append(f"- {item}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_plan(case_dir: pathlib.Path) -> Dict[str, Any]:
    case_dir = case_dir.resolve()
    manifest = _load_json(case_dir / "manifest.json")
    validation = _load_json(case_dir / "validation_result.json")

    errors: List[str] = []
    if manifest.get("schema") != "rtdl.paper_reproduction.xhd.external_response_intake.case_manifest.v1":
        errors.append("manifest schema mismatch")
    if validation.get("schema") != "rtdl.paper_reproduction.xhd.external_response_intake.validation_result.v1":
        errors.append("validation_result schema mismatch")
    for key in ["valid", "pod_expected", "next_action"]:
        if manifest.get(key) != validation.get(key):
            errors.append(f"manifest and validation_result disagree on {key}")

    next_action = validation.get("next_action")
    valid = bool(validation.get("valid"))
    pod_expected = bool(validation.get("pod_expected"))
    case_id = str(manifest.get("case_id") or case_dir.name)
    response_type = validation.get("response_type")

    if errors:
        plan_status = "invalid_case_record__repair_before_use"
        recommendation = "The intake case record is internally inconsistent. Do not run POD or change reproduction claims until the case is repaired."
        recommended_goal_type = "repair_intake_case_record"
        pod_allowed_next = False
        required_inputs = ["consistent manifest.json and validation_result.json"]
    elif valid and pod_expected and next_action in POD_READY_ACTIONS:
        action = POD_READY_ACTIONS[str(next_action)]
        plan_status = "ready_for_separate_provenance_ingestion_goal"
        recommendation = action["summary"]
        recommended_goal_type = action["recommended_goal_type"]
        pod_allowed_next = True
        required_inputs = action["required_inputs"]
    elif valid and not pod_expected and next_action in INGESTION_READY_NO_POD_ACTIONS:
        action = INGESTION_READY_NO_POD_ACTIONS[str(next_action)]
        plan_status = "ready_for_separate_artifact_instruction_ingestion_goal"
        recommendation = action["summary"]
        recommended_goal_type = action["recommended_goal_type"]
        pod_allowed_next = False
        required_inputs = action["required_inputs"]
    elif valid and not pod_expected:
        plan_status = "valid_response_but_no_pod_gate__keep_blocked_or_request_missing_material"
        recommendation = BLOCKED_ACTIONS.get(str(next_action), "Valid response does not justify a POD gate; manual review required.")
        recommended_goal_type = "request_missing_material_or_record_blocked_status"
        pod_allowed_next = False
        required_inputs = ["missing concrete artifact/provenance material"]
    else:
        plan_status = "invalid_response__keep_blocked"
        recommendation = "The response did not validate. Request corrected intake fields or keep the affected scope blocked."
        recommended_goal_type = "request_corrected_response"
        pod_allowed_next = False
        required_inputs = ["valid normalized response JSON"]

    return {
        "schema": "rtdl.paper_reproduction.xhd.provenance_ingestion.action_plan.v1",
        "case_id": case_id,
        "case_dir": str(case_dir),
        "response_type": response_type,
        "valid": valid,
        "pod_expected": pod_expected,
        "pod_allowed_next": pod_allowed_next,
        "next_action": next_action,
        "plan_status": plan_status,
        "recommended_goal_type": recommended_goal_type,
        "recommendation": recommendation,
        "required_inputs": required_inputs,
        "case_record_errors": errors,
        "requires_new_goal_before_pod": True,
        "sufficient_to_claim_exact_input": False,
        "claim_boundary": {
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
        },
        "not_allowed": [
            "running POD directly from this plan without a separate provenance-ingestion goal",
            "claiming exact paper dataset reproduction from this plan alone",
            "claiming Figure 5 reproduction from this plan alone",
            "claiming full X-HD paper reproduction from this plan alone",
            "claiming author-vs-RTDL performance ratio from this plan alone",
        ],
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir", type=pathlib.Path)
    parser.add_argument("--write", action="store_true", help="write plan JSON and Markdown into the case directory")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--output", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    try:
        plan = build_plan(args.case_dir)
        if args.write:
            json_path = args.case_dir / "provenance_action_plan.json"
            md_path = args.case_dir / "provenance_action_plan.md"
            if not args.overwrite and (json_path.exists() or md_path.exists()):
                raise FileExistsError("provenance action plan already exists; use --overwrite to replace it")
            _write_json(json_path, plan)
            _write_markdown(md_path, plan)
        text = json.dumps(plan, indent=2, sort_keys=True)
        if args.output:
            args.output.write_text(text + "\n", encoding="utf-8")
        else:
            print(text)
    except Exception as exc:
        print(f"plan failed: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
