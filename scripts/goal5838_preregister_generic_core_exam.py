#!/usr/bin/env python3
"""Build and verify the Goal5838 pre-mutation preregistration authority."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / (
    "history/internal_docs/goal5838_generic_core_exam_20260902/"
    "GOAL5838_PREREGISTRATION.json"
)
PREREGISTRATION = ROOT / (
    "history/internal_docs/goal5838_generic_core_exam_20260902/"
    "PREREGISTRATION.md"
)
ROADMAP = ROOT / (
    "history/internal_docs/"
    "goal5838_goal5843_cgo_reviewer_attack_remediation_plan_20260902.md"
)
GOAL5837 = ROOT / (
    "history/internal_docs/goal5837_owner_grouped_classification_20260902/"
    "GOAL5837_AUTHORITY.json"
)

BASELINE_COMMIT = "0f5c9d4297f73e412732e5a8ab133423fe4cfd21"
BASELINE_BLOBS = {
    "src/rtdsl/v4_callback_lifecycle.py":
        "76e35a2b246f125b51136bd6f8354a3133b8c207474f9e9aea31fda9c6b240bd",
    "src/rtdsl/v4_curve_owner_grouped_any_hit_public.py":
        "e6934833d596e6190a85f6af4e5769ee9f9ce29c350558a80759c805bd9db8eb",
    "src/rtdsl/v4_family_schema.py":
        "829fed3594dd3cb618edcf5ebbdfc1000d22e024e50c5f6a1973d35e3a5e4eef",
    "tests/goal5833_family_schema_compilation_plan_test.py":
        "53d0624d33ad5f6a973113233bc14712192d2e5e680a988ecbf23b95f2752c73",
}
ROADMAP_SHA256 = "bf02dfe3833d524c14586d4459adfe7b5063f88cc498a137562f55e087e0b664"
GOAL5837_SHA256 = "962fe108326b51fe9ca1c31e5192aab2699d941a7ea0f733d39e718d15bae271"


class Goal5838PreregistrationError(ValueError):
    pass


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _read_json(path: Path) -> dict[str, Any]:
    def reject_duplicate(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise Goal5838PreregistrationError(
                    f"G5838P001_DUPLICATE_KEY:{path}:{key}"
                )
            result[key] = value
        return result

    value = json.loads(path.read_text("utf-8"), object_pairs_hook=reject_duplicate)
    if not isinstance(value, dict):
        raise Goal5838PreregistrationError(f"G5838P002_OBJECT_REQUIRED:{path}")
    return value


def _git_blob(path: str) -> bytes:
    try:
        return subprocess.run(
            ["git", "show", f"{BASELINE_COMMIT}:{path}"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
    except subprocess.CalledProcessError as exc:
        raise Goal5838PreregistrationError(
            f"G5838P003_BASELINE_BLOB_UNAVAILABLE:{path}"
        ) from exc


def build_authority() -> dict[str, Any]:
    if _sha256(ROADMAP.read_bytes()) != ROADMAP_SHA256:
        raise Goal5838PreregistrationError("G5838P004_ROADMAP_DRIFT")
    if _sha256(GOAL5837.read_bytes()) != GOAL5837_SHA256:
        raise Goal5838PreregistrationError("G5838P005_GOAL5837_DRIFT")
    for path, expected in BASELINE_BLOBS.items():
        if _sha256(_git_blob(path)) != expected:
            raise Goal5838PreregistrationError(
                f"G5838P006_BASELINE_BLOB_DRIFT:{path}"
            )

    goal5837 = _read_json(GOAL5837)
    classification = goal5837.get("classification")
    if not isinstance(classification, dict) or any((
        classification.get("stable_v4_fixed_constructor_count_after_goal5837") != 2,
        classification.get("root_exported_closed_successor_route_count") != 1,
        classification.get("prospective_frozen_core_new_shape_exam_count") != 0,
    )):
        raise Goal5838PreregistrationError("G5838P007_BASELINE_COUNTS")

    body: dict[str, Any] = {
        "schema": "rtdl.goal5838.generic_core_exam_preregistration.v1",
        "goal": 5838,
        "date": "2026-09-02",
        "status": "PREREGISTERED_BEFORE_GENERIC_CORE_MUTATION",
        "scientific_question": (
            "schema_driven_frozen_core_executes_independently_selected_"
            "new_topology_without_core_change"
        ),
        "baseline": {
            "git_commit": BASELINE_COMMIT,
            "stable_v4_fixed_constructor_count": 2,
            "root_exported_closed_successor_route_count": 1,
            "prospective_frozen_core_new_shape_success_count": 0,
            "goal5837_authority_sha256": GOAL5837_SHA256,
            "roadmap_sha256": ROADMAP_SHA256,
            "git_blob_sha256": dict(sorted(BASELINE_BLOBS.items())),
            "family_schema_prototype_status": "INERT_NONCONTROLLING",
        },
        "stage_order": [
            "A_PREREGISTER",
            "B_IMPLEMENT_MIGRATE_AND_FREEZE_GENERIC_CORE",
            "C_INDEPENDENTLY_SELECT_CHALLENGE",
            "D_IMPLEMENT_ONLY_THROUGH_FROZEN_EXTENSION_SURFACES",
            "E_ORACLE_LIFECYCLE_TRUE_GPU_AND_HOSTILE_REVIEW",
        ],
        "before_core_seal": {
            "ordinary_defects_are_engineering_repairs": True,
            "deadline_can_trigger_scientific_failure": False,
            "attempt_count_can_trigger_scientific_failure": False,
            "core_may_be_changed": True,
        },
        "core_requirements": [
            "schema_driven_admission",
            "canonical_compilation_plan",
            "provider_binding_without_concrete_family_dispatch",
            "generic_public_lifecycle",
            "no_application_name_dispatch",
            "two_stable_routes_migrated_without_reclassification",
            "owner_grouped_successor_migrated_without_reclassification",
            "package_external_provider_conformance",
            "exact_core_inventory_and_sha256_seal_before_selection",
        ],
        "challenge_selection": {
            "occurs_after_core_seal": True,
            "project_author_selects_convenient_challenge": False,
            "preferred_selector": "external_reviewer_from_precommitted_table",
            "temporary_selector_unavailability": "PENDING_NOT_FAILURE",
            "goal5837_can_be_reused": False,
        },
        "post_selection_mutable_layers": [
            "protocol_instance_and_restricted_callback_ir",
            "package_external_or_provider_specific_modules",
            "application_input_and_independent_oracle",
            "tests_runners_reports_and_evidence_tools",
            "build_and_environment_repairs_without_core_semantic_change",
        ],
        "only_scientific_failure_condition": {
            "core_sealed_before_selection": True,
            "challenge_independently_selected_and_admissible": True,
            "allowed_extension_layers_exhausted": True,
            "frozen_core_change_semantically_required": True,
            "minimal_witness_and_hostile_review_required": True,
        },
        "success_condition": {
            "frozen_core_byte_changes_after_selection": 0,
            "schema_admission": "PASS",
            "callback_ir_verification": "PASS",
            "provider_binding": "PASS",
            "public_lifecycle": "compile_materialize_prepare_execute_close",
            "independent_oracle": "EXACT_MATCH",
            "hostile_cases": "PASS",
            "true_gpu_receipt": "REQUIRED",
        },
        "claim_ceiling_after_one_success": [
            "one_bounded_prospective_frozen_core_topology_result",
            "not_arbitrary_callback_ir_gpu_execution",
            "not_universal_provider_portability",
            "not_usability_superiority",
            "not_application_correctness_proof",
        ],
        "preregistration_markdown_sha256": _sha256(PREREGISTRATION.read_bytes()),
    }
    return {**body, "authority_sha256": _sha256(_canonical(body))}


def verify_authority(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise Goal5838PreregistrationError("G5838P008_AUTHORITY_OBJECT")
    expected = build_authority()
    if _canonical(value) != _canonical(expected):
        raise Goal5838PreregistrationError("G5838P009_AUTHORITY_MISMATCH")
    return expected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    if args.write == args.verify_stored:
        parser.error("choose exactly one of --write or --verify-stored")
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(_canonical(build_authority()) + b"\n")
    else:
        verify_authority(_read_json(OUTPUT))
    print("GOAL5838_PREREGISTRATION_PASS")


if __name__ == "__main__":
    main()

