#!/usr/bin/env python3
"""Freeze and verify the pre-execution Goal5836 same-input authority."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / (
    "history/internal_docs/"
    "goal5836_sui_same_input_preaction_authority_20260901.json"
)
DOMAIN = b"rtdl.goal5836.sui_same_input_preaction_authority.v1\0"
PREDECESSOR_COMMIT = "56ba0219c4cf58f27c78da978257caad39ebbf18"
MINIMUM_CHECKPOINT = "d0bb938170cd227a33a5237cf5b7e48102cb5c7e"
BRANCH = "codex/cgo-goal5836-handoff"

STATIC_PINS = {
    "history/internal_docs/self_review_pre_goal5836_macbook_handoff_a1_20260831.md": (
        18733,
        "e3b988a1dcdd94db0101221af841103b9c397a304cfc4504d53443dd7ef39ea2",
    ),
    "history/internal_docs/goal5834_b1_fixture_preaction_20260830/FIXTURE_AUTHORITY.json": (
        64132,
        "0f13ab8a7408c253114c56a51645c015d0e5e36ca96a4290c9dd1a2ba700adad",
    ),
    "history/internal_docs/goal5834_b1_fixture_preaction_20260830/WORKER_INPUTS.json": (
        16434,
        "55eeff377c93c32fed8cc326ad975cb9d2437df85812e30b9d916b3e7cc581a4",
    ),
    "history/internal_docs/goal5834_b3_home_result_20260830/RAW_GPU_RECEIPT_B3.json": (
        115663,
        "b50043e81713aacf6a70986a6e334789cbfeef17342ae97a8ae401ab1507f513",
    ),
    "history/internal_docs/goal5834_b3_home_result_20260830/INDEPENDENT_EVALUATION_B3.json": (
        5285,
        "786ebd4970dadf842c57aa6c08539694d0cdbe8a6b2f6672932029b5f19be02a",
    ),
    "history/internal_docs/goal5835_sui_derived_edge_crossing_mapping_result_20260830.json": (
        15642,
        "ae370da1ca5ac96562d0956438e7c6c8eee39fddf2d9894953db8e956c47ccff",
    ),
}

IMPLEMENTATION_PATHS = (
    "history/internal_docs/goal5836_sui_same_input_preaction_technical_plan_20260901.md",
    "scripts/goal5836_build_sui_same_input_preaction.py",
    "tests/goal5836_sui_same_input_preaction_test.py",
)

AUTHORIZATION = {
    "preaction_document_creation_authorized": True,
    "source_acquisition_authorized": False,
    "paper_download_authorized": False,
    "author_repository_fetch_authorized": False,
    "author_code_execution_authorized": False,
    "goal5836_execution_authorized": False,
    "product_source_mutation_authorized": False,
    "case_study_source_mutation_authorized": False,
    "pod_or_gpu_authorized": False,
    "modern_rtx_worker_authorized": False,
    "performance_measurement_authorized": False,
    "paper_app_promotion_authorized": False,
    "external_review_authorized": False,
    "public_claim_authorized": False,
}

STAGE_ORDER = (
    "A0_EXACT_SOURCE_ACQUISITION_AND_HASHING",
    "A1_AUTHOR_SOURCE_FIDELITY_CLASSIFICATION",
    "A2_SAME_INPUT_AND_OUTPUT_CONTRACT_FREEZE",
    "A3_LOCAL_THREE_ROUTE_MATERIALIZATION",
    "A4_MODERN_RTX_FUNCTIONAL_EXECUTION",
    "A5_PAPER_APP_PROMOTION_DECISION",
)

TERMINAL_OUTCOMES = {
    "all_three_routes_match": "FUNCTIONAL_MATCH__PAPER_APP_GATE_MAY_BE_EVALUATED",
    "functional_mismatch": "TERMINAL_SCIENTIFIC_MISMATCH__PRESERVE_INPUT_AND_OUTPUTS",
    "author_build_or_run_failure": "AUTHOR_EXECUTION_UNAVAILABLE__NO_PAPER_APP_PROMOTION",
    "source_fidelity_material_difference": "TERMINAL_MAPPING_REFUSAL__KEEP_GOAL5835_SCOPE",
    "source_fidelity_unresolved": "TERMINAL_UNRESOLVED_SOURCE_RELATION__STOP",
    "mapping_failure": "TERMINAL_MAPPING_FAILURE__NO_INPUT_REPLACEMENT",
    "unsupported_capability": "TERMINAL_UNSUPPORTED_CAPABILITY__NO_SCOPE_REWRITE",
    "infrastructure_invalid": "INVALID_EVIDENCE__NO_SCIENTIFIC_INFERENCE",
}


class PreactionError(RuntimeError):
    """Raised when the frozen Goal5836 preaction contract is violated."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _seal(document: dict[str, Any]) -> str:
    payload = dict(document)
    payload["preaction_authority_sha256"] = ""
    return hashlib.sha256(DOMAIN + canonical_json_bytes(payload)).hexdigest()


def _identity(relative: str) -> dict[str, Any]:
    logical = PurePosixPath(relative)
    if logical.is_absolute() or ".." in logical.parts:
        raise PreactionError(f"NON_PORTABLE_IDENTITY_PATH:{relative}")
    path = ROOT / logical
    data = path.read_bytes()
    return {
        "path": logical.as_posix(),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _verify_static_pins() -> None:
    for relative, (expected_bytes, expected_sha256) in STATIC_PINS.items():
        observed = _identity(relative)
        if (
            observed["bytes"] != expected_bytes
            or observed["sha256"] != expected_sha256
        ):
            raise PreactionError(f"STATIC_PREDECESSOR_PIN_MISMATCH:{relative}")


def _stage(
    stage_id: str,
    *,
    gate: str,
    authorized_now: bool,
    required_inputs: list[str],
    required_outputs: list[str],
    pass_condition: str,
    fail_condition: str,
) -> dict[str, Any]:
    return {
        "stage_id": stage_id,
        "entry_gate": gate,
        "authorized_now": authorized_now,
        "required_inputs": required_inputs,
        "required_outputs": required_outputs,
        "pass_condition": pass_condition,
        "fail_condition": fail_condition,
        "result_observed_at_preaction_freeze": False,
    }


def build_authority() -> dict[str, Any]:
    _verify_static_pins()
    document: dict[str, Any] = {
        "schema": "rtdl.goal5836.sui_same_input_preaction_authority.v1",
        "date": "2026-09-01",
        "goal": "5836",
        "status": (
            "READY_FOR_OWNER_GATE__SOURCE_ACQUISITION_ONLY__"
            "NO_GOAL5836_EXECUTION"
        ),
        "preaction_scope": "PLAN_AND_GATE_FREEZE_ONLY",
        "repository_binding": {
            "repository": "https://github.com/rubaolee/rtdl",
            "branch": BRANCH,
            "predecessor_commit": PREDECESSOR_COMMIT,
            "minimum_checkpoint": MINIMUM_CHECKPOINT,
            "identity_paths_are_repository_relative": True,
            "absolute_execution_paths_are_identity_bearing": False,
        },
        "predecessors": [_identity(path) for path in STATIC_PINS],
        "implementation_and_tests": [
            _identity(path) for path in IMPLEMENTATION_PATHS
        ],
        "current_scientific_state": {
            "paper_app_status": "NOT_A_PAPER_APP",
            "source_relation": "SUI_DERIVED_MAPPING__AUTHOR_DESIGNED_FIXTURES",
            "generalization_exam_count": 0,
            "registered_performance_timing_count": 0,
            "new_goal5835_gpu_launch_count": 0,
            "inherited_b3_true_optix_launch_count": 33,
            "goal5836_functional_execution_count": 0,
            "author_source_byte_count_observed": 0,
            "author_output_count_observed": 0,
        },
        "planned_source": {
            "observation_status": "PLANNING_CLAIMS_ONLY__NO_BYTES_ACQUIRED",
            "paper": {
                "authors": ["Sizhe Sui", "Luis Sentis", "Andrew Bylard"],
                "title": (
                    "Hardware-Accelerated Ray Tracing for Discrete and "
                    "Continuous Collision Detection on GPUs"
                ),
                "venue": "ICRA 2025",
                "pages": "16133--16139",
                "planning_claim_only": True,
                "local_bytes_present": False,
                "sha256": None,
            },
            "author_repository": {
                "url": "https://github.com/Ssz990220/RTCollisionDetection",
                "planned_commit": "bacbf77a612bba3e6e8f7a464fa0fa2c67298ac7",
                "planned_license": "MIT",
                "planning_claim_only": True,
                "git_object_observed": False,
                "license_bytes_observed": False,
                "tree_sha256": None,
                "license_sha256": None,
            },
            "pin_rewrite_to_match_returned_bytes_allowed": False,
            "source_selection_after_result_inspection_allowed": False,
        },
        "authorization": dict(AUTHORIZATION),
        "next_owner_gate": {
            "requested_decision": (
                "AUTHORIZE_STAGE_A0_SOURCE_ACQUISITION_AND_HASHING_ONLY"
            ),
            "authorization_if_approved": [
                "download_and_hash_exact_paper_pdf",
                "fetch_and_verify_exact_planned_git_commit",
                "capture_and_hash_license_bytes",
                "capture_fetch_receipts_and_full_source_tree_identity",
            ],
            "still_forbidden_after_approval": [
                "author_code_build_or_execution",
                "goal5836_functional_execution",
                "product_or_case_study_source_mutation",
                "pod_or_gpu_use",
                "timing_or_performance_collection",
                "paper_app_promotion",
                "external_review",
                "public_claim",
            ],
        },
        "stages": [
            _stage(
                STAGE_ORDER[0],
                gate="SEPARATE_OWNER_APPROVAL_FOR_A0_ONLY",
                authorized_now=False,
                required_inputs=[
                    "planned paper identity",
                    "planned repository URL and commit",
                    "planned license label",
                ],
                required_outputs=[
                    "exact paper PDF bytes and SHA-256",
                    "exact Git commit object and complete tree identity",
                    "exact license bytes and SHA-256",
                    "network and fetch receipts",
                ],
                pass_condition=(
                    "all planned identities are available and exact; no pin changed"
                ),
                fail_condition=(
                    "missing commit, source drift, license mismatch, incomplete "
                    "receipt, or hash ambiguity stops the transaction"
                ),
            ),
            _stage(
                STAGE_ORDER[1],
                gate="A0_PASS_PLUS_SEPARATE_OWNER_APPROVAL",
                authorized_now=False,
                required_inputs=[
                    "A0 exact source authority",
                    "selected author source files chosen without output inspection",
                ],
                required_outputs=[
                    "source-backed edge direction semantics",
                    "source-backed trajectory and width/radius semantics",
                    "source-backed Boolean and discrete endpoint/pose semantics",
                    "one of MATCH_SELECTED_EDGE_PREDICATE, "
                    "MATERIAL_PREDICATE_DIFFERENCE, or UNRESOLVED",
                ],
                pass_condition="MATCH_SELECTED_EDGE_PREDICATE",
                fail_condition=(
                    "MATERIAL_PREDICATE_DIFFERENCE or UNRESOLVED stops promotion"
                ),
            ),
            _stage(
                STAGE_ORDER[2],
                gate="A1_MATCH_PLUS_SEPARATE_OWNER_APPROVAL",
                authorized_now=False,
                required_inputs=[
                    "source-backed predicate statement",
                    "source-derived candidate geometry independent of outputs",
                ],
                required_outputs=[
                    "one complete mesh-derived robust positive edge crossing",
                    "retained face-interior-only negative boundary",
                    "exact common input bytes and Boolean output contract",
                    "deterministic global u32 path IDs and unique triangle IDs",
                    "finite nondegenerate mesh validation",
                    "no-replacement and no-threshold-change rules",
                ],
                pass_condition=(
                    "input and identities freeze before author, RTDL, or oracle output"
                ),
                fail_condition=(
                    "invalid mesh, ambiguous identity, unavailable positive case, or "
                    "post-output selection stops the transaction"
                ),
            ),
            _stage(
                STAGE_ORDER[3],
                gate="A2_FREEZE_PLUS_SEPARATE_OWNER_APPROVAL",
                authorized_now=False,
                required_inputs=[
                    "A2 exact common input",
                    "A1 source-backed semantic mapping",
                ],
                required_outputs=[
                    "author adapter materializer without expected output",
                    "RTDL public-lifecycle adapter without expected output",
                    "stdlib-only oracle isolated from both workers",
                    "raw-output sealing and post-seal evaluator",
                    "CPU-only schema, hostile, and materializer tests",
                ],
                pass_condition=(
                    "three separately implemented routes reproduce exact input identity"
                ),
                fail_condition=(
                    "expected-output leakage, identity drift, route coupling, or "
                    "materializer mismatch stops the transaction"
                ),
            ),
            _stage(
                STAGE_ORDER[4],
                gate="FROZEN_A3_BUNDLE_PLUS_SEPARATE_MODERN_RTX_OWNER_GATE",
                authorized_now=False,
                required_inputs=[
                    "sealed A3 execution bundle",
                    "zero-worker preflight",
                    "exact GPU, driver, CUDA, OptiX, source, binary, and input hashes",
                ],
                required_outputs=[
                    "author raw functional output",
                    "RTDL public-route raw functional output",
                    "independent oracle output",
                    "true-OptiX built-in sphere/curve receipts",
                    "post-seal same-input evaluation",
                ],
                pass_condition="frozen routes complete with valid custody",
                fail_condition=(
                    "build failure, mismatch, unsupported capability, or invalid "
                    "infrastructure is reported without replacement"
                ),
            ),
            _stage(
                STAGE_ORDER[5],
                gate="A4_VALID_RESULT_PLUS_SEPARATE_OWNER_PROMOTION_DECISION",
                authorized_now=False,
                required_inputs=[
                    "exact provenance",
                    "faithful same-input mapping",
                    "author, RTDL, and oracle functional records",
                    "independently recountable custody",
                ],
                required_outputs=[
                    "bounded Paper App decision or strongest lower status",
                ],
                pass_condition="all eight controlling Paper App gates pass",
                fail_condition="retain strongest lower status without wording repair",
            ),
        ],
        "same_input_contract": {
            "application_scope": (
                "ONE_PAPER_SOURCE_DERIVED_PIECEWISE_LINEAR_EDGE_CROSSING_CORE"
            ),
            "output_contract": "PER_EDGE_BOOLEAN_THEN_HOST_OR_COLLISION_BOOLEAN",
            "edge_result_remains_separately_observable": True,
            "complete_sphere_triangle_ccd_claimed": False,
            "complete_robot_collision_detection_claimed": False,
            "required_routes": [
                "AUTHOR_SOURCE_ADAPTER",
                "RTDL_PUBLIC_LIFECYCLE_ADAPTER",
                "STDLIB_ONLY_CPU_ORACLE",
            ],
            "same_exact_input_for_all_routes": True,
            "author_and_rtdl_workers_receive_expected_output": False,
            "oracle_imports_rtdl_or_author_runtime": False,
            "raw_outputs_sealed_before_evaluation": True,
            "input_replacement_after_output_allowed": False,
            "threshold_or_margin_change_after_output_allowed": False,
            "output_predicate_change_after_output_allowed": False,
        },
        "custody_contract": {
            "identity_paths": "REPOSITORY_RELATIVE_POSIX_PLUS_CONTENT_HASH",
            "absolute_paths": "OPTIONAL_NON_IDENTITY_DIAGNOSTICS_ONLY",
            "workers_contain_expected_output": False,
            "workers_contain_cpu_geometry_oracle": False,
            "raw_output_evaluated_before_seal": False,
            "source_and_input_hashes_verified_before_worker_zero": True,
            "modern_rtx_preflight_worker_count": 0,
        },
        "unconditional_outcomes": dict(TERMINAL_OUTCOMES),
        "paper_app_gate": {
            "required_all": [
                "exact paper and author-source provenance",
                "faithful frozen same-input mapping",
                "successful author execution",
                "RTDL public-lifecycle execution",
                "author, RTDL, and oracle agreement or scientifically resolved difference",
                "independently recountable identity and custody",
                "visible limitations and negative cases",
                "zero performance inference",
            ],
            "promotion_on_partial_gate_allowed": False,
        },
        "claim_boundary": {
            "goal5835_claim_preserved": True,
            "goal5836_result_claimed": False,
            "paper_app_claimed": False,
            "generalization_claimed": False,
            "modern_rtx_claimed": False,
            "performance_claimed": False,
            "public_release_claimed": False,
        },
        "preaction_authority_sha256": "",
    }
    document["preaction_authority_sha256"] = _seal(document)
    validate_policy(document)
    return document


def _walk_paths(value: Any, key: str = "") -> None:
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            _walk_paths(child_value, child_key)
        return
    if isinstance(value, list):
        for child in value:
            _walk_paths(child, key)
        return
    if not isinstance(value, str):
        return
    if key == "path" or key.endswith("_path"):
        if value.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:[\\/]", value):
            raise PreactionError(f"ABSOLUTE_IDENTITY_PATH:{value}")
        logical = PurePosixPath(value)
        if ".." in logical.parts:
            raise PreactionError(f"PARENT_TRAVERSAL_IDENTITY_PATH:{value}")


def validate_policy(document: dict[str, Any]) -> None:
    if document.get("schema") != "rtdl.goal5836.sui_same_input_preaction_authority.v1":
        raise PreactionError("SCHEMA_MISMATCH")
    if document.get("status") != (
        "READY_FOR_OWNER_GATE__SOURCE_ACQUISITION_ONLY__NO_GOAL5836_EXECUTION"
    ):
        raise PreactionError("STATUS_MISMATCH")
    if document.get("authorization") != AUTHORIZATION:
        raise PreactionError("AUTHORIZATION_MISMATCH")
    true_authorizations = [
        key for key, value in document["authorization"].items() if value
    ]
    if true_authorizations != ["preaction_document_creation_authorized"]:
        raise PreactionError("UNEXPECTED_AUTHORIZATION")
    if [row.get("stage_id") for row in document.get("stages", [])] != list(STAGE_ORDER):
        raise PreactionError("STAGE_ORDER_MISMATCH")
    if any(row.get("authorized_now") for row in document["stages"]):
        raise PreactionError("STAGE_PREAUTHORIZED")
    if document.get("unconditional_outcomes") != TERMINAL_OUTCOMES:
        raise PreactionError("OUTCOME_POLICY_MISMATCH")
    state = document.get("current_scientific_state", {})
    expected_state = {
        "paper_app_status": "NOT_A_PAPER_APP",
        "source_relation": "SUI_DERIVED_MAPPING__AUTHOR_DESIGNED_FIXTURES",
        "generalization_exam_count": 0,
        "registered_performance_timing_count": 0,
        "new_goal5835_gpu_launch_count": 0,
        "inherited_b3_true_optix_launch_count": 33,
        "goal5836_functional_execution_count": 0,
        "author_source_byte_count_observed": 0,
        "author_output_count_observed": 0,
    }
    if state != expected_state:
        raise PreactionError("SCIENTIFIC_STATE_MISMATCH")
    planned = document.get("planned_source", {})
    if planned.get("observation_status") != "PLANNING_CLAIMS_ONLY__NO_BYTES_ACQUIRED":
        raise PreactionError("SOURCE_OBSERVATION_STATUS_MISMATCH")
    if not planned.get("paper", {}).get("planning_claim_only"):
        raise PreactionError("PAPER_PLANNING_BOUNDARY_MISSING")
    if not planned.get("author_repository", {}).get("planning_claim_only"):
        raise PreactionError("REPOSITORY_PLANNING_BOUNDARY_MISSING")
    if planned["paper"].get("sha256") is not None:
        raise PreactionError("UNAUTHORIZED_PAPER_HASH_OBSERVED")
    if planned["author_repository"].get("tree_sha256") is not None:
        raise PreactionError("UNAUTHORIZED_SOURCE_HASH_OBSERVED")
    if planned["author_repository"].get("license_sha256") is not None:
        raise PreactionError("UNAUTHORIZED_LICENSE_HASH_OBSERVED")
    same_input = document.get("same_input_contract", {})
    if same_input.get("author_and_rtdl_workers_receive_expected_output") is not False:
        raise PreactionError("EXPECTED_OUTPUT_LEAKAGE")
    if same_input.get("raw_outputs_sealed_before_evaluation") is not True:
        raise PreactionError("RAW_OUTPUT_SEAL_POLICY_MISMATCH")
    if same_input.get("input_replacement_after_output_allowed") is not False:
        raise PreactionError("INPUT_REPLACEMENT_ALLOWED")
    if document.get("custody_contract", {}).get("modern_rtx_preflight_worker_count") != 0:
        raise PreactionError("NONZERO_PREACTION_WORKER_COUNT")
    if any(document.get("claim_boundary", {}).values()) is not True:
        # The only true claim-boundary value is preservation of Goal5835.
        raise PreactionError("CLAIM_BOUNDARY_SHAPE_MISMATCH")
    if [
        key for key, value in document["claim_boundary"].items() if value
    ] != ["goal5835_claim_preserved"]:
        raise PreactionError("UNAUTHORIZED_CLAIM")
    _walk_paths(document)
    seal = document.get("preaction_authority_sha256")
    if not isinstance(seal, str) or not re.fullmatch(r"[0-9a-f]{64}", seal):
        raise PreactionError("INVALID_AUTHORITY_SEAL")
    if seal != _seal(document):
        raise PreactionError("AUTHORITY_SEAL_MISMATCH")


def verify_stored(path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise PreactionError("STORED_AUTHORITY_NOT_REGULAR_FILE")
    stored = json.loads(path.read_text(encoding="ascii"))
    validate_policy(stored)
    expected = build_authority()
    if stored != expected:
        raise PreactionError("STORED_AUTHORITY_EXACT_DOCUMENT_MISMATCH")
    return stored


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write-create-only", action="store_true")
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    if args.write_create_only and args.verify_stored:
        parser.error("write and verify are mutually exclusive")

    document = build_authority()
    payload = json.dumps(
        document, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False
    ).encode("ascii") + b"\n"
    if args.write_create_only:
        if args.output.exists() or args.output.is_symlink():
            raise SystemExit("CREATE_ONLY_OUTPUT_EXISTS")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("xb") as stream:
            stream.write(payload)
        status = "CREATE_ONLY_GOAL5836_PREACTION_FREEZE_PASS"
    elif args.verify_stored:
        verify_stored(args.output)
        status = "POSTWRITE_GOAL5836_PREACTION_VERIFY_PASS"
    else:
        status = "DRY_RUN_GOAL5836_PREACTION_PASS__NO_NETWORK__NO_EXECUTION"
    print(
        json.dumps(
            {
                "status": status,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "preaction_authority_sha256": document[
                    "preaction_authority_sha256"
                ],
                "authorized_stage_count": sum(
                    row["authorized_now"] for row in document["stages"]
                ),
                "source_bytes_observed": 0,
                "worker_count": 0,
                "timing_count": 0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
