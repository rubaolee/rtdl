#!/usr/bin/env python3
"""Build the create-only Goal5792 local completion checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


PINS: dict[str, tuple[str, str]] = {
    "work_authority": ("history/internal_docs/goal5792_unknown_lane_classification_work_authority_20260819.json", "465cd43d1fa93a567ac85c53dc210165aa33f95c9a55d6e4064795d4804df9c3"),
    "unknown_result": ("history/internal_docs/goal5792_preliminary_source_backed_unknown_lane_classification_20260820.json", "2f1030b93fc69834f093090bb513cccc701938590327f85c0c424d51bc7738c3"),
    "unknown_report": ("history/internal_docs/goal5792_preliminary_source_backed_unknown_lane_classification_20260820.md", "601bc148bbd2612e78d2d7dcdd0dda323bb355c33359d2add5d06057ca692307"),
    "responsibility_result_v3": ("history/internal_docs/goal5792_source_backed_responsibility_audit_result_v3_20260820.json", "f4958306576ac3a6a0d182796c067cbd693018cb45318af3b6f77520f982682b"),
    "responsibility_report_v3": ("history/internal_docs/goal5792_source_backed_responsibility_audit_report_v3_20260820.md", "57d9c4ce3b4639c02c3bbafe752f2f487e4b80a21233079bdd0f82ce9168e8cc"),
    "responsibility_script": ("scripts/goal5792_source_backed_responsibility_audit.py", "2a50d597fd25370dcfb8d2b0acda7535c73884899bbfcb81f1e9927ecca0a376"),
    "responsibility_tests": ("tests/goal5792_source_backed_responsibility_audit_test.py", "708da915ad961b702ad48c3a5d5801a0826aa28e37357b11afed25e061ea9d54"),
    "clean_linux_result": ("history/internal_docs/goal5792_clean_linux_rc_v6_rehearsal_result_20260820.json", "1db0a9fb5c3122875a342aaf6d5476f26449740c8ecdc2c08aa0b038788dd16b"),
    "clean_linux_report": ("history/internal_docs/goal5792_clean_linux_rc_v6_rehearsal_report_20260820.md", "46fab8d31f90d7db00a9d23dd0c4e5d5ed900a7a5080034427ae39860fae1a0e"),
    "clean_linux_raw": ("history/internal_docs/goal5792_clean_linux_rc_v6_rehearsal_20260820/CANONICAL_VALIDATION.json", "69d78bba3f935414e337c94856480f79d8a38c8ebcf0b2e47645bcdf3676e12e"),
    "clean_linux_wheel": ("history/internal_docs/goal5792_clean_linux_rc_v6_rehearsal_20260820/rtdl_source_tree-4.0.0rc1-py3-none-any.whl", "cdc93fd10dc7ff409ab6cdc12946a7d7f367ac861495623f96c4f4e02d1c547d"),
    "hygiene_result_v2": ("history/internal_docs/goal5792_artifact_identity_hygiene_audit_result_v2_20260820.json", "e6480512081f97fb84c74c4abeb0cc73aec73c2f4011981d78bfbc2802964131"),
    "hygiene_report_v2": ("history/internal_docs/goal5792_artifact_identity_hygiene_audit_report_v2_20260820.md", "52a41b5f24d9fb51212571094faf43e89ec20aac5b0dd326e9bb5d6075d526ec"),
    "hygiene_script": ("scripts/goal5792_artifact_identity_hygiene_audit.py", "490c039886d51492526bb7f57a3d072a29677154ab63946ab07877f5f205ae91"),
    "hygiene_tests": ("tests/goal5792_artifact_identity_hygiene_audit_test.py", "c44cb3584090ff9c2194f4288bf956b759931a4d7bc6291bb09ffb340b169eac"),
    "negative_result": ("history/internal_docs/goal5792_negative_decision_evidence_audit_result_20260820.json", "cd3e01a71c6540c9584f4e6c1d812906f4ba744a843db8f1980eb8ede5dfecdf"),
    "negative_report": ("history/internal_docs/goal5792_negative_decision_evidence_audit_report_20260820.md", "4f0bfe712c6a44f98f8ebfc88b3d58b4a8ee22850299a29b50d4c77f8605c6fe"),
    "negative_script": ("scripts/goal5792_negative_decision_evidence_audit.py", "f457210753d1bd49e0ab2be4a2267770085e9c2eead4b8661bfee4f1965864e9"),
    "negative_tests": ("tests/goal5792_negative_decision_evidence_audit_test.py", "dccfbbf5db6b8a9045f0dba556f05cff072c268920759cd69b7a2debbcc307f4"),
    "design_doc": ("docs/v4/restricted_python_optix_callbacks_design.md", "fa00ecbb582a185f4767470e386c9e1b3d7995c5bc3c4945dcba883be61ddc9c"),
    "historical_plan_doc": ("docs/v4/v4_system_design_and_execution_plan.md", "9a05c07060d97c59f1829975096cfaf4d77595733409f66fcd422434a56cf6d3"),
    "reproduction_doc": ("docs/v4/cgo_artifact_reproduction.md", "514e290b61c6df19ae6148524c7c8ff8edea03261f9458a5053dd4ca81226341"),
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_sha(value: Any) -> str:
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=True, allow_nan=False).encode("utf-8"))


def _load_pins(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, bytes]]:
    rows: dict[str, dict[str, Any]] = {}
    blobs: dict[str, bytes] = {}
    for role, (relative, expected) in PINS.items():
        path = root / relative
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f"missing or non-regular local completion pin: {role}")
        data = path.read_bytes()
        actual = _sha(data)
        if actual != expected:
            raise RuntimeError(f"local completion pin drift: {role}: {actual}")
        rows[role] = {"path": relative, "sha256": actual, "bytes": len(data)}
        blobs[role] = data
    return rows, blobs


def _json(blobs: dict[str, bytes], role: str) -> dict[str, Any]:
    value = json.loads(blobs[role])
    if not isinstance(value, dict):
        raise RuntimeError(f"non-object JSON component: {role}")
    return value


def _verify_seal(value: dict[str, Any], field: str, role: str) -> str:
    copied = dict(value)
    stored = copied.pop(field, None)
    if not isinstance(stored, str) or _canonical_sha(copied) != stored:
        raise RuntimeError(f"component self-seal mismatch: {role}")
    return stored


def build_result(root: Path) -> dict[str, Any]:
    root = root.resolve()
    pins, blobs = _load_pins(root)
    authority = _json(blobs, "work_authority")
    unknown = _json(blobs, "unknown_result")
    responsibility = _json(blobs, "responsibility_result_v3")
    clean = _json(blobs, "clean_linux_result")
    clean_raw = _json(blobs, "clean_linux_raw")
    hygiene = _json(blobs, "hygiene_result_v2")
    negative = _json(blobs, "negative_result")

    authority_seal = _verify_seal(authority, "authority_sha256", "work_authority")
    unknown_seal = _verify_seal(unknown, "artifact_sha256", "unknown_result")
    responsibility_seal = _verify_seal(responsibility, "result_sha256", "responsibility_result_v3")
    clean_seal = _verify_seal(clean, "result_sha256", "clean_linux_result")
    hygiene_seal = _verify_seal(hygiene, "result_sha256", "hygiene_result_v2")
    negative_seal = _verify_seal(negative, "result_sha256", "negative_result")

    if authority.get("goal5792_required_output", {}).get("clean_linux_artifact_rehearsal_required") is not True:
        raise RuntimeError("clean-Linux requirement drifted")
    unknown_recount = unknown.get("frozen_lane_recount", {})
    unknown_rows = unknown.get("unknown_lane_classifications", [])
    unknown_policy = unknown.get("classification_policy", {})
    if unknown_recount.get("registered_lane_count") != 15 \
            or unknown_recount.get("semantic_unknown_count") != 9 \
            or unknown_recount.get("semantic_compatible_count") != 6 \
            or unknown_recount.get("semantic_incompatible_count") != 0:
        raise RuntimeError("semantic classification counts drifted")
    if len(unknown_rows) != 9 or any(
        row.get("primary_class")
        != "DECLARATION_OR_AUTHORITY_MISSING__ENGINEERING_DEBT"
        for row in unknown_rows
    ):
        raise RuntimeError("UNKNOWN primary classification drifted")
    if unknown_policy.get("primary_class_for_all_unknown_lanes") \
            != "DECLARATION_OR_AUTHORITY_MISSING__ENGINEERING_DEBT" \
            or unknown_policy.get("principled_semantic_limitation_count") != 0 \
            or unknown_policy.get("incompatible_count") != 0:
        raise RuntimeError("UNKNOWN classification policy drifted")
    if responsibility.get("summary", {}).get("application_count") != 9 \
            or responsibility.get("summary", {}).get(
                "native_runtime_loading_behind_registered_v4_interface_count") != 8:
        raise RuntimeError("responsibility summary drifted")
    if responsibility.get("summary", {}).get("native_runtime_loading_exception_applications") != ["raydb"]:
        raise RuntimeError("RayDB exception drifted")
    if clean_raw.get("schema") != "rtdl.goal5767.clean_usability_result.v1" \
            or clean_raw.get("unit_tests") != "186/186 PASS" \
            or clean_raw.get("v4_test_module_count") != 20 \
            or clean_raw.get("gpu_or_pod_used") is not False \
            or clean_raw.get("performance_timing_registered") is not False:
        raise RuntimeError("clean-Linux raw result drifted")
    if hygiene.get("outer_performance_authority", {}).get(
        "evidence_embeds_exact_standalone_execution_source") is not True:
        raise RuntimeError("artifact identity cross-binding incomplete")
    if negative.get("summary", {}).get(
        "diagnostic_legally_executes_and_matches_own_oracle_count") != 6 \
            or negative.get("summary", {}).get("product_admission_fail_closed_count") != 6:
        raise RuntimeError("negative-decision summary drifted")

    output: dict[str, Any] = {
        "schema": "rtdl.goal5792.local_completion_checkpoint.v1",
        "goal": 5792,
        "date": "2026-08-20",
        "status": "LOCAL_EVIDENCE_COMPLETE__OWNER_REVIEW_REQUIRED__NO_EXECUTION_AUTHORITY",
        "pins": pins,
        "component_internal_seals": {
            "work_authority": authority_seal,
            "unknown_classification": unknown_seal,
            "responsibility_v3": responsibility_seal,
            "clean_linux": clean_seal,
            "identity_hygiene_v2": hygiene_seal,
            "negative_decision": negative_seal,
        },
        "semantic_decision_evidence": {
            "registered_lane_count": 15,
            "semantic_compatible_count": 6,
            "semantic_unknown_fail_closed_count": 9,
            "semantic_incompatible_count_in_bounded_inventory": 0,
            "unknown_primary_class": "DECLARATION_OR_AUTHORITY_MISSING__ENGINEERING_DEBT",
            "unknown_primary_class_count": 9,
            "unknown_secondary_physical_or_composition_gaps_source_backed": True,
            "raydb_placeholder_family_mismatch_disclosed": True,
            "all_registered_lanes_target_capable_and_instance_admissible": True,
            "unknown_is_principled_undecidability_count": 0,
            "unknown_silently_upgraded_count": 0,
        },
        "negative_decision_evidence": {
            "bounded_counterexample_count": 6,
            "legal_behavioral_optix_and_matches_own_oracle_count": 6,
            "matches_requested_semantics_count": 0,
            "product_admission_fail_closed_count": 6,
            "rejection_split": "5 admitted-facade + 1 earlier Typed Physical Schema",
            "successful_complete_diagnostic_launch_count": 7,
            "diagnostic_raygen_invocation_count": 9,
        },
        "responsibility_evidence": {
            "application_count": 9,
            "structural_shift_count": 9,
            "native_runtime_loading_behind_registered_interface_count": 8,
            "native_runtime_loading_exception_applications": ["raydb"],
            "legacy_six_obligations_fully_source_backed": 0,
            "legacy_six_obligations_partially_source_backed": 2,
            "legacy_six_obligations_not_established": 4,
            "developer_task_or_time_measurement_count": 0,
            "productivity_multiplier_claimed": False,
        },
        "artifact_evidence": {
            "clean_linux_canonical_validator_pass": True,
            "clean_linux_test_count": 186,
            "clean_linux_test_module_count": 20,
            "offline_wheel_build_and_install_pass": True,
            "functional_rc_source_pre_post_identity_pass": True,
            "functional_rc_is_goal5785_performance_source": False,
            "goal5785_outer_authority_source_evidence_embedded_source_crossbound": True,
            "goal5776_historical_schema_occurrence_count": 1175,
            "goal5776_historical_schema_json_member_count": 603,
        },
        "theory_and_claim_boundary": {
            "formal_positioning": "registered-family assume-guarantee interface compatibility with identity binding and fail-closed UNKNOWN",
            "proof_carrying_code_or_translation_validation_guarantee_claimed": False,
            "abstract_interpretation_soundness_theorem_claimed": False,
            "data_refinement_proof_claimed": False,
            "arbitrary_python_semantics_inferred": False,
            "universal_soundness_or_completeness_claimed": False,
            "developer_productivity_claimed": False,
            "public_release_or_submission_ready_claimed": False,
        },
        "completion": {
            "goal5792_local_required_work_complete": True,
            "owner_returned_external_review_complete": False,
            "current_bytes_approved_for_publication_or_submission": False,
            "remaining_local_scientific_or_artifact_execution_required": False,
            "next_action": "owner-controlled exact-byte review of this local checkpoint",
        },
        "authorization": {
            "authorizes_gpu_or_pod": False,
            "authorizes_registered_timing": False,
            "authorizes_product_or_native_changes": False,
            "authorizes_publication_or_submission": False,
            "authorizes_goal5791_stage_a_or_stage_b": False,
        },
    }
    output["result_sha256"] = _canonical_sha(output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    result = build_result(Path(args.root))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps({"status": result["status"], "pins": len(result["pins"])}, sort_keys=True))


if __name__ == "__main__":
    main()
