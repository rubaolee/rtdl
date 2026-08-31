#!/usr/bin/env python3
"""Reconstruct the bounded CGO claim from frozen Goal5800 OWL evidence.

This verifier deliberately separates an executed consequence from academic
claim weight.  All five invalid protocols reached an OWL-composed launch, but
the defensible novelty summary is three primary semantic residuals, one partial
status-enforcement residual, and one executable-binding support result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history" / "internal_docs"
TABLE = HISTORY / (
    "goal5800_three_arm_responsibility_and_executable_residual_result_"
    "v6_20260824.json"
)
CORRECTION = HISTORY / (
    "goal5800_owl_repository_locator_correction_result_20260824.json"
)
OWL_RESULT = HISTORY / (
    "goal5800_owl_v5_lx1_untimed_result_20260824"
    "/goal5800_owl_untimed_result.json"
)

PINS = {
    "table": "32b48e335e788320395fd8727c94f7b6636f11c3d95ea6f976e7a9608b3523c0",
    "correction": "29e174b77a4b6c47692baae8b7f8175462f77a97266a99ec5e9c575431a69f4d",
    "owl_result": "2d5404f7d7b73d22ab5e4d7592ff169877c33b023af8575d882adb146d8bf7ec",
}

CLASSIFICATION = {
    "role_effect_closure": "PRIMARY_SEMANTIC_RESIDUAL",
    "payload_attribute_abi_ownership": "PRIMARY_SEMANTIC_RESIDUAL",
    "physical_geometry_binding": "PRIMARY_SEMANTIC_RESIDUAL",
    "device_status_continuation": "PARTIAL_ENFORCEMENT_RESIDUAL",
    "checked_program_executable_identity": "EXECUTABLE_BINDING_SUPPORT",
}

EXPECTED_REASON = {
    "role_effect_closure": "CP001_ROLE_EFFECT_MISMATCH",
    "payload_attribute_abi_ownership":
        "CP002_ATTRIBUTE_ABI_OWNERSHIP_MISMATCH",
    "physical_geometry_binding": "CP003_PHYSICAL_BINDING_MISMATCH",
    "device_status_continuation": "CP004_CONTINUATION_STATUS_MISMATCH",
    "checked_program_executable_identity":
        "CP005_EXECUTABLE_IDENTITY_MISMATCH",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_exact(path: Path, expected_sha256: str) -> dict[str, Any]:
    actual = _sha256(path)
    if actual != expected_sha256:
        raise RuntimeError(
            f"frozen authority digest mismatch: {path.name}: "
            f"expected {expected_sha256}, observed {actual}"
        )
    return json.loads(path.read_bytes())


def build_claim(
    *,
    table_path: Path = TABLE,
    correction_path: Path = CORRECTION,
    owl_result_path: Path = OWL_RESULT,
) -> dict[str, Any]:
    table = _load_exact(table_path, PINS["table"])
    correction = _load_exact(correction_path, PINS["correction"])
    owl_result = _load_exact(owl_result_path, PINS["owl_result"])

    bridge = correction["official_source_bridge"]
    if correction["status"] != (
        "PASS__P1_REPOSITORY_LOCATOR_CORRECTED_APPEND_ONLY__EXECUTION_PRESERVED"
    ):
        raise RuntimeError("official OWL repository correction did not pass")
    if bridge["origin"] != "https://github.com/NVIDIA/OWL.git":
        raise RuntimeError("effective OWL source is not the official repository")
    if bridge["undeclared_mismatch_count_excluding_overlay"] != 0:
        raise RuntimeError("official OWL source bridge has undeclared mismatches")
    if bridge["declared_overlay_path"] != "owl/DeviceContext.cpp":
        raise RuntimeError("validation overlay path changed")

    expected_valid = {
        "relation": [[100, 10], [101, 20]],
        "triangle_per_ray": [3, 2, 0, 1],
        "triangle_weighted_sum": 16,
    }
    if owl_result["nearby_valid"] != expected_valid:
        raise RuntimeError("nearby valid OWL control is not exact")
    if owl_result["runtime_capture"][
            "optix_validation_error_or_fatal_message_count"] != 0:
        raise RuntimeError("OptiX validation reported an error or fatal record")
    if owl_result["executable"]["process_exit_code"] != 0:
        raise RuntimeError("OWL residual executable failed")

    rows_by_mechanism = {
        row["mechanism"]: row for row in table["protocol_residual_ownership"]
    }
    if set(rows_by_mechanism) != set(CLASSIFICATION):
        raise RuntimeError("OWL/RTDL residual mechanism set changed")

    rows: list[dict[str, Any]] = []
    for mechanism, claim_class in CLASSIFICATION.items():
        row = rows_by_mechanism[mechanism]
        owl = row["nvidia_owl"]
        rtdl = row["rtdl"]
        if owl["executed_arm"] != (
            "PINNED_NVIDIA_OWL_PLUS_DIAGNOSTIC_ONLY_VALIDATION_OVERLAY"
        ):
            raise RuntimeError(f"OWL arm changed: {mechanism}")
        if owl["observation"]["owl_accepted_and_executed"] is not True:
            raise RuntimeError(f"OWL did not execute control: {mechanism}")
        if rtdl["verdict"] != "REJECT" or rtdl["finding_count"] != 1:
            raise RuntimeError(f"RTDL did not reject exactly once: {mechanism}")
        if rtdl["executable_capability_issued"] is not False:
            raise RuntimeError(f"RTDL issued executable capability: {mechanism}")
        if rtdl["reason_id"] != EXPECTED_REASON[mechanism]:
            raise RuntimeError(f"RTDL reason changed: {mechanism}")

        wrong_output = owl["evidence"] == (
            "EXECUTED_ACCEPTED_INVALID__EXACT_WRONG_OUTPUT"
        )
        partial_status = owl["evidence"] == (
            "EXECUTED_PROTOCOL_VIOLATION__OVERFLOW_EXPOSED__PARTIAL_COUNT_SEVEN"
        )
        if mechanism == "device_status_continuation" and not partial_status:
            raise RuntimeError("CP004 narrow status result changed")
        if mechanism != "device_status_continuation" and not wrong_output:
            raise RuntimeError(f"wrong-output witness changed: {mechanism}")
        rows.append({
            "mechanism": mechanism,
            "claim_class": claim_class,
            "owl_composition_completed": True,
            "reached_launch": True,
            "exact_frozen_wrong_output": wrong_output,
            "overflow_exposed_but_status_before_consume_not_enforced":
                partial_status,
            "nearby_valid_control_exact": True,
            "optix_validation_error_or_fatal_count": 0,
            "rtdl_prelaunch_reject": True,
            "rtdl_single_reason_id": rtdl["reason_id"],
        })

    counts = {
        "primary_semantic_residual": sum(
            row["claim_class"] == "PRIMARY_SEMANTIC_RESIDUAL" for row in rows
        ),
        "partial_enforcement_residual": sum(
            row["claim_class"] == "PARTIAL_ENFORCEMENT_RESIDUAL"
            for row in rows
        ),
        "executable_binding_support": sum(
            row["claim_class"] == "EXECUTABLE_BINDING_SUPPORT" for row in rows
        ),
        "all_invalid_controls_reached_launch": sum(
            row["reached_launch"] for row in rows
        ),
        "all_rtdl_controls_rejected_prelaunch": sum(
            row["rtdl_prelaunch_reject"] for row in rows
        ),
    }
    if counts != {
        "primary_semantic_residual": 3,
        "partial_enforcement_residual": 1,
        "executable_binding_support": 1,
        "all_invalid_controls_reached_launch": 5,
        "all_rtdl_controls_rejected_prelaunch": 5,
    }:
        raise RuntimeError("CGO residual classification changed")

    return {
        "schema": "rtdl.goal5808.owl_cgo_residual_claim.v1",
        "status": "PASS__BOUNDED_OWL_RESIDUAL_CGO_CLAIM_RECONSTRUCTED",
        "answer_to_owl_plus_type_checker_objection": (
            "OWL owns mature OptiX composition; RTDL adds pre-launch admission "
            "for cross-role application-semantic protocol obligations that the "
            "executed OWL arm leaves to application convention."
        ),
        "effective_owl_source": {
            "repository": bridge["origin"],
            "commit": bridge["commit"],
            "tree": bridge["tree"],
            "diagnostic_only_overlay": bridge["declared_overlay_path"],
            "undeclared_mismatch_count_excluding_overlay": 0,
        },
        "counts": counts,
        "mechanisms": rows,
        "claim_boundary": {
            "owl_composition_novelty_claimed": False,
            "five_equally_independent_novel_mechanisms_claimed": False,
            "natural_defect_incidence_claimed": False,
            "new_application_generalization_claimed": False,
            "third_party_usability_claimed": False,
            "performance_claimed": False,
            "modern_rtx_or_rt_core_claimed": False,
            "task_oracle_can_catch_exercised_failures": True,
            "prelaunch_admission_is_input_coverage_independent": True,
        },
        "frozen_authorities": {
            "three_arm_table_sha256": PINS["table"],
            "official_repository_correction_sha256": PINS["correction"],
            "owl_execution_result_sha256": PINS["owl_result"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    result = build_claim()
    print(json.dumps(
        result,
        indent=2 if args.pretty else None,
        sort_keys=True,
        separators=None if args.pretty else (",", ":"),
    ))


if __name__ == "__main__":
    main()
