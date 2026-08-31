#!/usr/bin/env python3
"""Build the source- and execution-backed Goal5800 three-arm table."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history" / "internal_docs"
BASE = HISTORY / "goal5796_source_backed_responsibility_tables_v2_20260823.json"
GOAL5797 = HISTORY / "goal5797_five_mechanism_liveness_and_necessity_result_20260823.json"
PYOPTIX = HISTORY / "goal5797_gpu_evidence_20260823" / "GOAL5797_PYOPTIX_CONTROLS.json"
OWL = HISTORY / "goal5800_owl_v5_lx1_untimed_result_20260824" / "goal5800_owl_untimed_result.json"
PYOPTIX_IDIOMATIC = ROOT / "experiments" / "goal5800_pyoptix_owl" / "pyoptix_idiomatic_arm.py"
PYOPTIX_IDIOMATIC_RESULT = HISTORY / (
    "goal5800_pyoptix_idiomatic_untimed_evidence_20260824"
    "/idiomatic_pyoptix_untimed.json")
PYOPTIX_IDIOMATIC_EVIDENCE = HISTORY / (
    "goal5800_pyoptix_idiomatic_untimed_evidence_20260824"
    "/goal5800_pyoptix_idiomatic_untimed_evidence.tar.gz")
PYOPTIX_SOURCE_CAPSULE = HISTORY / (
    "goal5800_nvidia_otk_pyoptix_source_capsule_v2_20260824.tar.gz")
MIGRATION = HISTORY / "goal5796_r590_non_timed_migration_bundle_20260823.tar.gz"
OWL_BUNDLE = HISTORY / "goal5800_owl_untimed_functional_bundle_v5_20260824.tar.gz"
OUTPUT = HISTORY / "goal5800_three_arm_responsibility_and_executable_residual_result_v6_20260824.json"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def pin(path: Path) -> dict[str, object]:
    value = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(value),
        "sha256": sha256_bytes(value),
    }


def tar_files(path: Path) -> dict[str, bytes]:
    rows: dict[str, bytes] = {}
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError(f"could not read archive member: {member.name}")
            rows[member.name] = stream.read()
    return rows


def immutable_ref(ref: dict[str, object], *, migration: dict[str, bytes],
                   public_source: dict[str, bytes],
                   owl_bundle: dict[str, bytes],
                   pyoptix_source: dict[str, bytes]) -> dict[str, object]:
    result = dict(ref)
    path = str(ref["path"])
    if path.startswith("experiments/goal5796_matched/"):
        member = "overlay/" + path
        value = migration[member]
        result["path"] = (
            "history/internal_docs/goal5796_r590_non_timed_migration_bundle_"
            f"20260823.tar.gz::{member}")
    elif path.startswith("src/rtdsl/"):
        value = public_source[path]
        result["path"] = (
            "history/internal_docs/goal5796_r590_non_timed_migration_bundle_"
            "20260823.tar.gz::payload/goal5795_public_source.tar.gz::" + path)
    elif path.startswith(".tmp_goal5796_upstream_20260823/OWL/"):
        relative = path.removeprefix(
            ".tmp_goal5796_upstream_20260823/OWL/")
        member = "goal5800_owl_source/" + relative
        value = owl_bundle[member]
        result["path"] = (
            "history/internal_docs/goal5800_owl_untimed_functional_bundle_"
            f"v5_20260824.tar.gz::{member}")
    elif path.startswith(
            ".tmp_goal5796_upstream_20260823/otk-pyoptix/"):
        relative = path.removeprefix(
            ".tmp_goal5796_upstream_20260823/otk-pyoptix/")
        member = "goal5800_pyoptix_source/clean_checkout/" + relative
        value = pyoptix_source[member]
        result["path"] = (
            "history/internal_docs/goal5800_nvidia_otk_pyoptix_source_"
            f"capsule_v2_20260824.tar.gz::{member}")
    else:
        value = (ROOT / path).read_bytes()
    if sha256_bytes(value) != ref["sha256"]:
        raise RuntimeError(f"source reference bytes are stale: {path}")
    literal = str(ref["literal"])
    if literal.encode("utf-8") not in value:
        raise RuntimeError(f"source reference literal missing: {path}/{literal}")
    lines = value.decode("utf-8").splitlines()
    for line_number in ref["line_numbers"]:
        if not 1 <= line_number <= len(lines):
            raise RuntimeError(
                f"source reference line out of range: {path}/{line_number}")
        if literal not in lines[line_number - 1]:
            raise RuntimeError(
                f"source reference literal not on declared line: "
                f"{path}/{line_number}/{literal}")
    result["bytes_reverified"] = len(value)
    result["archive_or_live_bytes_reverified"] = True
    result["line_numbers_reverified"] = True
    return result


def freeze_owner(owner: dict[str, object], **kwargs: object) -> dict[str, object]:
    result = dict(owner)
    result["sources"] = [
        immutable_ref(row, **kwargs) for row in owner.get("sources", [])
    ]
    return result


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    base = json.loads(BASE.read_bytes())
    rtdl = json.loads(GOAL5797.read_bytes())
    pyoptix = json.loads(PYOPTIX.read_bytes())
    owl = json.loads(OWL.read_bytes())
    pyoptix_idiomatic = json.loads(PYOPTIX_IDIOMATIC_RESULT.read_bytes())
    migration = tar_files(MIGRATION)
    with tarfile.open(
            fileobj=io.BytesIO(migration["payload/goal5795_public_source.tar.gz"]),
            mode="r:gz") as archive:
        public_source = {}
        for member in archive.getmembers():
            if not member.isfile():
                continue
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError(f"could not read public source: {member.name}")
            public_source[member.name] = stream.read()
    owl_bundle = tar_files(OWL_BUNDLE)
    pyoptix_source = tar_files(PYOPTIX_SOURCE_CAPSULE)
    ref_kwargs = {
        "migration": migration, "public_source": public_source,
        "owl_bundle": owl_bundle, "pyoptix_source": pyoptix_source,
    }
    if base["status"] != "PASS":
        raise RuntimeError("Goal5796 source responsibility authority failed")
    if rtdl["status"] != "PASS" or pyoptix["status"] != "PASS":
        raise RuntimeError("Goal5797 evidence failed")
    if not owl["minimum_met"] or owl["executed_residual_mechanism_count"] != 5:
        raise RuntimeError("Goal5800 OWL executable residual is incomplete")
    if pyoptix_idiomatic["status"] != "PASS__UNTIMED_FUNCTIONAL" \
            or pyoptix_idiomatic["registered_performance_timing_count"] != 0 \
            or pyoptix_idiomatic["optix_validation"] != "PASS" \
            or pyoptix_idiomatic["relation"]["launch_count"] != 2 \
            or pyoptix_idiomatic["triangle"]["launch_count"] != 1:
        raise RuntimeError("Goal5800 idiomatic PyOptiX execution is incomplete")
    if owl["runtime_capture"][
            "optix_validation_error_or_fatal_message_count"] != 0:
        raise RuntimeError("OWL validation emitted an error/fatal diagnostic")

    rtdl_rows = {row["mechanism"]: row for row in rtdl["rows"]}
    pyoptix_rows = pyoptix["behavioral_controls"]
    owl_rows = owl["behavioral_controls"]
    mechanisms = (
        "role_effect_closure",
        "payload_attribute_abi_ownership",
        "physical_geometry_binding",
        "device_status_continuation",
        "checked_program_executable_identity",
    )
    base_names = {
        "role_effect_closure": "role_effect_closure",
        "payload_attribute_abi_ownership": "payload_attribute_semantic_ownership",
        "physical_geometry_binding": "physical_geometry_binding",
        "device_status_continuation": "device_status_before_consume",
        "checked_program_executable_identity": "checked_program_executable_identity",
    }
    exact_reasons = {
        "role_effect_closure": "CP001_ROLE_EFFECT_MISMATCH",
        "payload_attribute_abi_ownership": (
            "CP002_ATTRIBUTE_ABI_OWNERSHIP_MISMATCH"),
        "physical_geometry_binding": "CP003_PHYSICAL_BINDING_MISMATCH",
        "device_status_continuation": "CP004_CONTINUATION_STATUS_MISMATCH",
        "checked_program_executable_identity": (
            "CP005_EXECUTABLE_IDENTITY_MISMATCH"),
    }
    protocol_authority = {
        row["responsibility"]: row
        for row in base["protocol_contract_ownership"]
    }
    if set(rtdl_rows) != set(mechanisms) or set(pyoptix_rows) != set(mechanisms) \
            or set(owl_rows) != set(mechanisms):
        raise RuntimeError("three-arm mechanism sets differ")

    protocol_rows = []
    for mechanism in mechanisms:
        rtdl_row = rtdl_rows[mechanism]
        decision = rtdl_row["semantic_necessity"]["full_decision"]
        if decision["verdict"] != "REJECT" \
                or len(decision["findings"]) != 1 \
                or decision["findings"][0]["reason_id"] != exact_reasons[mechanism] \
                or decision["executable_capability_issued"]:
            raise RuntimeError(
                f"RTDL exact reject contract failed: {mechanism}")
        py_row = pyoptix_rows[mechanism]
        owl_row = owl_rows[mechanism]
        boundary = protocol_authority[base_names[mechanism]]
        if mechanism == "device_status_continuation":
            baseline_evidence = (
                "EXECUTED_PROTOCOL_VIOLATION__OVERFLOW_EXPOSED__PARTIAL_COUNT_SEVEN")
        else:
            baseline_evidence = "EXECUTED_ACCEPTED_INVALID__EXACT_WRONG_OUTPUT"
        protocol_rows.append({
            "mechanism": mechanism,
            "raw_pyoptix": {
                "owner": "application_convention",
                "evidence": baseline_evidence,
                "optix_validation": "PASS",
                "process_exit_code": 0,
                "observation": py_row,
                "observation_sha256": sha256_bytes(canonical(py_row)),
                "source_boundary": freeze_owner(
                    boundary["B_pyoptix"], **ref_kwargs),
            },
            "nvidia_owl": {
                "executed_arm": (
                    "PINNED_NVIDIA_OWL_PLUS_DIAGNOSTIC_ONLY_VALIDATION_OVERLAY"),
                "owner": "application_convention_after_owl_composition",
                "evidence": baseline_evidence,
                "optix_validation_mode": "ALL",
                "optix_validation_error_or_fatal_message_count": 0,
                "process_exit_code": 0,
                "observation": owl_row,
                "observation_sha256": sha256_bytes(canonical(owl_row)),
                "source_boundary": freeze_owner(
                    boundary["C_owl"], **ref_kwargs),
            },
            "rtdl": {
                "owner": "compiler_or_public_runtime",
                "evidence": "LAUNCH_PREVENTED__EXACT_SINGLE_FINDING",
                "verdict": decision["verdict"],
                "reason_id": decision["findings"][0]["reason_id"],
                "finding_count": len(decision["findings"]),
                "executable_capability_issued": decision[
                    "executable_capability_issued"],
                "decision_sha256": decision["decision_sha256"],
                "source_boundary": freeze_owner(
                    boundary["D_rtdl"], **ref_kwargs),
            },
            "residual_novelty_supported_against_owl": True,
        })

    composition = []
    for row in base["composition_ownership"]:
        composition.append({
            "responsibility": row["responsibility"],
            "raw_pyoptix": freeze_owner(row["B_pyoptix"], **ref_kwargs),
            "nvidia_owl": {
                **freeze_owner(row["C_owl"], **ref_kwargs),
                "executed_arm": (
                    "PINNED_NVIDIA_OWL_PLUS_DIAGNOSTIC_ONLY_VALIDATION_OVERLAY"),
            },
            "rtdl": freeze_owner(row["D_rtdl"], **ref_kwargs),
            "novelty_score_allowed": False,
        })

    device_language = []
    for row in base["device_language_path"]:
        device_language.append({
            "task": row["task"],
            "raw_pyoptix": row["B_pyoptix"],
            "nvidia_owl": (
                "CPP_HOST_PLUS_CUDA_CPP_DEVICE__EXECUTED_PINNED_OWL_PLUS_"
                "DIAGNOSTIC_ONLY_VALIDATION_OVERLAY"),
            "rtdl": row["D_rtdl"],
            "language_change_is_not_a_protocol_novelty_claim": True,
        })

    result = {
        "schema": "rtdl.goal5800.three_arm_responsibility_and_executable_residual.v3",
        "status": (
            "PASS__OWL_COMPOSITION_CREDITED__FOUR_EXACT_SILENT_WRONG_OUTPUTS__"
            "ONE_STATUS_BEFORE_CONSUME_ENFORCEMENT_VIOLATION"),
        "inputs": [pin(BASE), pin(GOAL5797), pin(PYOPTIX), pin(OWL),
                   pin(PYOPTIX_IDIOMATIC), pin(PYOPTIX_IDIOMATIC_RESULT),
                   pin(PYOPTIX_IDIOMATIC_EVIDENCE), pin(PYOPTIX_SOURCE_CAPSULE),
                   pin(MIGRATION), pin(OWL_BUNDLE)],
        "immutable_source_authorities": {
            "goal5796_migration_bundle": pin(MIGRATION),
            "nested_public_source_member_sha256": sha256_bytes(
                migration["payload/goal5795_public_source.tar.gz"]),
            "goal5800_owl_bundle": pin(OWL_BUNDLE),
            "nvidia_otk_pyoptix_complete_tree_capsule": pin(
                PYOPTIX_SOURCE_CAPSULE),
            "nvidia_otk_pyoptix_commit": (
                "3144f224c0fd18733925faf3d8fb82c7376b8dcf"),
            "nvidia_otk_pyoptix_tree": (
                "0bf0ec24efb4a43f129aee25dd265aa8149374e3"),
            "all_emitted_source_references_rehashed": True,
            "all_emitted_line_references_verified": True,
        },
        "source_pins": base["source_pins"],
        "arm_definition": {
            "raw_pyoptix": (
                "Current NVIDIA PyOptiX-compatible Python binding arm; "
                "application owns OptiX construction and CUDA/C++ device code."),
            "nvidia_owl": (
                "Pinned OWL + diagnostic-only validation overlay; OWL owns "
                "mature host composition while the application supplies "
                "device programs."),
            "rtdl": (
                "RTDL restricted callback program plus compiler/runtime whole-"
                "protocol admission and public lifecycle."),
            "pyoptix_plus_owl_combined_stack_claimed": False,
            "reason_no_combined_stack": (
                "PyOptiX and OWL are alternative host abstractions, not a "
                "documented combined product stack; fabricating that arm would "
                "confound language and composition ownership."),
        },
        "composition_ownership": composition,
        "protocol_residual_ownership": protocol_rows,
        "device_language_path": device_language,
        "idiomatic_pyoptix_successor": {
            "status": "PASS__UNTIMED_GPU_EXECUTED__IDENTITY_CLOSED",
            "purpose": (
                "Remove Goal5798's per-element Python output materialization "
                "before any future symmetric timing design."),
            "bulk_relation_materialization": "reshape.tolist_then_set_map",
            "bulk_triangle_materialization": "ndarray.tolist",
            "actual_installed_distribution_identity_required_before_future_execution": True,
            "result": pin(PYOPTIX_IDIOMATIC_RESULT),
            "evidence": pin(PYOPTIX_IDIOMATIC_EVIDENCE),
            "installed_distribution_version": pyoptix_idiomatic[
                "pyoptix_distribution_version"],
            "loaded_distribution_files_sha256": pyoptix_idiomatic[
                "pyoptix_loaded_distribution_manifest"]["files_sha256"],
            "loaded_optix_module_sha256": pyoptix_idiomatic[
                "loaded_optix_module_sha256"],
            "pinned_source_commit": pyoptix_idiomatic["pyoptix_commit"],
            "pinned_source_tree": pyoptix_idiomatic["pyoptix_tree"],
            "relation_output_sha256": pyoptix_idiomatic[
                "relation"]["output_sha256"],
            "triangle_per_ray_sha256": pyoptix_idiomatic[
                "triangle"]["per_ray_sha256"],
            "registered_performance_timing_count": 0,
            "independent_idiomaticity_judgment_status": (
                "PENDING_EXTERNAL_REVIEW_OF_EXACT_EXECUTED_SOURCE"),
        },
        "executed_summary": {
            "raw_pyoptix_executed_protocol_invalid_count": 5,
            "raw_pyoptix_exact_silent_wrong_output_count": 4,
            "raw_pyoptix_status_before_consume_violation_count": 1,
            "owl_executed_protocol_invalid_count": 5,
            "owl_exact_silent_wrong_output_count": 4,
            "owl_status_before_consume_violation_count": 1,
            "rtdl_launch_prevented_count": 5,
            "owl_goal5799_minimum_required": 3,
            "owl_minimum_met": True,
            "owl_nearby_valid_control_exact": True,
        },
        "claim_boundary": {
            "owl_composition_advantage_fully_credited": True,
            "rtdl_composition_novelty_over_owl_claimed": False,
            "residual_protocol_novelty_over_owl_supported": True,
            "owl_performance_claimed": False,
            "pyoptix_performance_claimed": False,
            "rtdl_performance_claimed": False,
            "modern_rt_core_execution_claimed": False,
            "generalization_claimed": False,
            "usability_or_productivity_claimed": False,
            "task_oracle_would_catch_all_five_on_exercised_inputs": True,
            "static_protocol_value_is_prelaunch_and_input_coverage_independent": True,
        },
        "scope": {
            "registered_performance_timing_count": 0,
            "new_app_generalization_exam_count": 0,
            "third_party_user_count": 0,
            "owl_execution_host": "lx1 GTX1070 CC6.1 Pascal",
            "owl_execution_interpretation": "OptiX_semantics_not_RT_core_performance",
        },
    }
    OUTPUT.write_bytes(
        json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": result["status"],
        "output": OUTPUT.relative_to(ROOT).as_posix(),
        "bytes": OUTPUT.stat().st_size,
        "sha256": sha256_bytes(OUTPUT.read_bytes()),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
