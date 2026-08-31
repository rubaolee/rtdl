"""Build Goal5797's append-only oracle and source-provenance correction.

This is a post-review evidence reconstruction.  It performs no GPU execution,
does not import RTDL or PyOptiX, and emits no timing observation.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history" / "internal_docs"
REVIEW = HISTORY / (
    "review_goal5797_five_mechanism_liveness_and_semantic_necessity_"
    "20260823.md")
PRIMARY = HISTORY / (
    "goal5797_five_mechanism_liveness_and_necessity_result_20260823.json")
GPU = HISTORY / "goal5797_gpu_evidence_20260823" / (
    "GOAL5797_PYOPTIX_CONTROLS.json")
GPU_HARNESS = HISTORY / "goal5797_gpu_evidence_20260823" / (
    "pyoptix_controls_v2_executed.py")
LEAF = HISTORY / (
    "goal5797_a1_exhaustive_populated_leaf_liveness_result_20260823.json")
LEAF_VERIFY = HISTORY / (
    "goal5797_a1_exhaustive_populated_leaf_liveness_independent_"
    "verification_20260823.json")
RESPONSIBILITY = HISTORY / (
    "goal5796_source_backed_responsibility_tables_v2_20260823.json")
GOAL5796 = HISTORY / (
    "goal5796_pyoptix90_compatibility_successor_result_20260823.json")
TRANSACTION = HISTORY / "goal5796_home_pyoptix90_compatibility_evidence_20260823" / (
    "results/TRANSACTION_RESULT.json")
ORACLE_RESULT = HISTORY / "goal5796_home_pyoptix90_compatibility_evidence_20260823" / (
    "results/PYOPTIX_ORACLE.json")
ORACLE_SOURCE = ROOT / "experiments" / "goal5796_matched" / (
    "independent_oracle.py")
BASE_DEVICE = ROOT / "experiments" / "goal5796_matched" / "matched_device.cu"
PYOPTIX_ARM = ROOT / "experiments" / "goal5796_matched" / "pyoptix_baseline.py"
DIRECT_ARM = ROOT / "experiments" / "goal5796_matched" / "direct_optix.cpp"
OUTPUT = HISTORY / (
    "goal5797_a1_oracle_counterfactual_and_source_provenance_result_"
    "20260823.json")


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def pin(path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha_file(path),
    }


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def row(
    *, mechanism: str, expected: object, observed: object,
    gate_reason: str, sampling_limit: str,
) -> dict[str, object]:
    differs = canonical(expected) != canonical(observed)
    if not differs:
        raise RuntimeError(f"oracle would not detect {mechanism}")
    return {
        "mechanism": mechanism,
        "registered_attack_exposing_expected": expected,
        "observed_invalid_program_result": observed,
        "developer_end_to_end_oracle_on_this_registered_input": (
            "DETECTS_MISMATCH"),
        "oracle_detects": True,
        "platform_automatic_diagnostic": "NO_DIAGNOSTIC",
        "optix_validation": "PASS",
        "optix_validation_error_message_count": 0,
        "cuda_last_error": "SUCCESS",
        "process_exit_code": 0,
        "rtdl_prelaunch_gate": "REJECT",
        "sole_gate_reason": gate_reason,
        "sampling_limit": sampling_limit,
    }


def main() -> None:
    primary = load(PRIMARY)
    gpu = load(GPU)
    leaf = load(LEAF)
    leaf_verify = load(LEAF_VERIFY)
    responsibility = load(RESPONSIBILITY)
    goal5796 = load(GOAL5796)
    transaction = load(TRANSACTION)
    oracle = load(ORACLE_RESULT)

    if sha_file(REVIEW) != (
            "ff82ef925b00f1173495bcae4b9048d3c3d40581fe04c5d36d01f1e1f6abe856"):
        raise RuntimeError("external review identity drift")
    if primary.get("status") != "PASS" or gpu.get("status") != "PASS":
        raise RuntimeError("Goal5797 evidence not PASS")
    if leaf.get("status") != "PASS" or leaf_verify.get("status") != "PASS":
        raise RuntimeError("exhaustive leaf evidence not PASS")
    if leaf.get("decision_bearing_count") != 19:
        raise RuntimeError("exhaustive populated-leaf count is not 19")
    if responsibility.get("status") != "PASS":
        raise RuntimeError("responsibility table not PASS")
    if transaction.get("status") != "PASS" or not transaction.get(
            "all_three_outputs_exact_and_identical"):
        raise RuntimeError("Goal5796 A/B/D accounting not exact")
    if oracle.get("status") != "PASS":
        raise RuntimeError("independent oracle not PASS")
    if sha_file(BASE_DEVICE) != gpu["identities"]["valid_a"][
            "device_source_sha256"]:
        raise RuntimeError("Goal5797 valid-A source is not matched_device.cu")

    primary_rows = {item["mechanism"]: item for item in primary["rows"]}
    controls = gpu["behavioral_controls"]
    expected = oracle["expected"]
    triangle_expected = expected["triangle"]
    relation_expected = expected["bounded_relation"]["diagnostic_cross"]
    broad_expected = expected["bounded_relation"]["librts_tiny_broad"]

    rows = [
        row(
            mechanism="role_effect_closure",
            expected=triangle_expected,
            observed=controls["role_effect_closure"]["output"],
            gate_reason="CP001_ROLE_EFFECT_MISMATCH",
            sampling_limit=(
                "Only inputs whose hit multiplicity exposes terminate-versus-continue "
                "distinguish this error."),
        ),
        row(
            mechanism="payload_attribute_abi_ownership",
            expected=relation_expected,
            observed=controls["payload_attribute_abi_ownership"]["output"],
            gate_reason="CP002_ATTRIBUTE_ABI_OWNERSHIP_MISMATCH",
            sampling_limit=(
                "Only inputs whose application ids differ from primitive indices "
                "expose this slot-meaning error."),
        ),
        row(
            mechanism="physical_geometry_binding",
            expected=relation_expected,
            observed=controls["physical_geometry_binding"]["output"],
            gate_reason="CP003_PHYSICAL_BINDING_MISMATCH",
            sampling_limit=(
                "Only asymmetric geometry/query coordinates expose the x/y binding "
                "swap."),
        ),
        row(
            mechanism="device_status_continuation",
            expected={
                "rows": broad_expected,
                "status": "COMPLETE",
                "row_count": len(broad_expected),
            },
            observed={
                "rows": controls["device_status_continuation"]["returned_rows"],
                "status": controls["device_status_continuation"]["status"],
                "row_count": controls["device_status_continuation"][
                    "returned_row_count"],
            },
            gate_reason="CP004_CONTINUATION_STATUS_MISMATCH",
            sampling_limit=(
                "The registered capacity-7-of-8 input exposes the violation; an "
                "otherwise identical below-capacity input would not expose overflow."),
        ),
        row(
            mechanism="checked_program_executable_identity",
            expected=triangle_expected,
            observed=controls["checked_program_executable_identity"]["output"],
            gate_reason="CP005_EXECUTABLE_IDENTITY_MISMATCH",
            sampling_limit=(
                "Only a launch whose loaded program identity differs from the checked "
                "identity exposes this substitution."),
        ),
    ]

    for item in rows:
        source = primary_rows[item["mechanism"]]["semantic_necessity"]
        reasons = [finding["reason_id"] for finding in source[
            "full_decision"]["findings"]]
        if source["full_decision"]["verdict"] != "REJECT":
            raise RuntimeError("primary gate verdict drift")
        if reasons != [item["sole_gate_reason"]]:
            raise RuntimeError("primary sole reason drift")
        if source["optix_validation"] != "PASS" or source[
                "process_exit_code"] != 0:
            raise RuntimeError("platform diagnostic reconstruction drift")

    require_status_rows = [item for item in leaf["rows"] if item.get("path") == (
        "role_effects.finalize[1]")]
    if len(require_status_rows) != 1 or not require_status_rows[0].get(
            "decision_bearing"):
        raise RuntimeError("require_status_ok leaf liveness not established")

    result: dict[str, object] = {
        "schema": "rtdl.goal5797_a1.oracle_and_source_provenance.v1",
        "date": "2026-08-23",
        "status": "PASS",
        "evidence_kind": (
            "POSTREVIEW_RECONSTRUCTION__NO_NEW_GPU_EXECUTION__NO_TIMING"),
        "review": pin(REVIEW),
        "p1_closure": {
            "P1_1_every_populated_contract_leaf": {
                "status": "CLOSED",
                "populated_leaf_count": 19,
                "decision_bearing_count": 19,
                "explicit_non_decision_bearing_count": 0,
                "require_status_ok_leaf": {
                    "path": "role_effects.finalize[1]",
                    "mutation": "require_status_ok -> allow_status_error",
                    "verdict_delta": "ACCEPT_TO_REJECT",
                    "sole_reason": "CP001_ROLE_EFFECT_MISMATCH",
                },
                "primary": pin(LEAF),
                "independent_verification": pin(LEAF_VERIFY),
            },
            "P1_2_oracle_counterfactual": {
                "status": "CLOSED",
                "conditional_answer": (
                    "YES: a developer end-to-end test comparing against the exact "
                    "independent oracle on each registered attack-exposing input "
                    "detects all five wrong outcomes."),
                "platform_automatic_check_detection_count": 0,
                "developer_oracle_detection_count_on_registered_inputs": 5,
                "rtdl_prelaunch_gate_rejection_count": 5,
                "rows": rows,
            },
        },
        "oracle_scope": {
            "source": pin(ORACLE_SOURCE),
            "executed_result": pin(ORACLE_RESULT),
            "implementation_independence": (
                "The stdlib-only oracle imports none of Direct OptiX, PyOptiX, OWL, "
                "or RTDL."),
            "why_oracle_does_not_make_the_gate_redundant": [
                "An oracle checks only inputs that are actually sampled.",
                "The CP004 overflow is invisible below the registered capacity boundary.",
                "Repurposed acceleration is most valuable when no fast trusted answer "
                "is available for every production input.",
                "The RTDL gate rejects the declared/projected protocol mismatch before "
                "launch; it is not a substitute for end-to-end correctness tests.",
            ],
            "claim_ceiling": (
                "This evidence proves diagnostic complementarity on two designed tasks; "
                "it does not prove oracle-free correctness or new-app generalization."),
        },
        "device_source_provenance": {
            "base": pin(BASE_DEVICE),
            "classification": (
                "HAND_WRITTEN_MATCHED_EXPERIMENT_CUDA_SOURCE__SHARED_BY_DIRECT_AND_"
                "PYOPTIX_ARMS__NOT_RTDL_GENERATED"),
            "direct_host_arm": pin(DIRECT_ARM),
            "pyoptix_host_arm": pin(PYOPTIX_ARM),
            "goal5797_mutation_harness": pin(GPU_HARNESS),
            "goal5797_valid_a_device_sha256_matches_base": True,
            "variant_construction": (
                "Goal5797 derives five CUDA variants by exact textual edits to the "
                "hand-written matched_device.cu base, then NVRTC-compiles and executes "
                "them through the current-source PyOptiX compatibility arm."),
            "schema_field_correction": {
                "field": "actual_projection.generated_device_source_sha256",
                "meaning_in_goal5797": (
                    "SHA-256 of the executed variant CUDA source supplied to NVRTC; "
                    "the inherited field name is not evidence that RTDL generated it."),
                "immutable_historical_result_edited": False,
            },
        },
        "goal5796_accounting": {
            "successor_result": pin(GOAL5796),
            "source_backed_responsibility_tables_v2": pin(RESPONSIBILITY),
            "same_host_transaction": pin(TRANSACTION),
            "A_direct_B_pyoptix_D_rtdl_outputs_exact_and_identical": True,
            "B_scope": (
                "current PyOptiX source adapted for OptiX 9.0 compatibility; stock "
                "PyOptiX 9.1 was not executed"),
            "C_owl_scope": "ANALYSED_NOT_IMPLEMENTED",
            "composition_novelty_claimed": False,
        },
        "p2_p3_dispositions": {
            "P2_pascal": (
                "The five GPU controls ran under OptiX on GTX 1070/Pascal and therefore "
                "do not establish RT-core hardware execution.  An Ada confirmation is "
                "a separate functional replication, not a timing prerequisite."),
            "P2_CP004": (
                "The executed CP004 control establishes continuation/completeness under "
                "capacity overflow.  The exhaustive require_status_ok leaf establishes "
                "declaration liveness, not a real injected nonzero device-status event. "
                "The paper row must be named continuation/completeness unless such an "
                "event is separately executed."),
            "P3_physical_mutation": (
                "The original semantic-necessity attack coherently swapped all four "
                "lower/upper x/y bindings.  Goal5797-A1 additionally mutates all four "
                "populated physical leaves one at a time, each ACCEPT_TO_REJECT."),
            "P3_triangle_B_B": (
                "The reject-all guard pairs the already executed identity-arm B output "
                "with a separately rebuilt B contract/projection ACCEPT decision; it is "
                "not claimed as a second GPU launch under B authority."),
        },
        "claims": {
            "new_application_generalization_exam_count": 0,
            "usability_study_count": 0,
            "performance_claimed": False,
            "rt_core_execution_claimed_for_goal5797": False,
            "registered_performance_timing_count": 0,
            "lx1_performance_host_authorized": False,
            "goal5798_timing_authorized": False,
        },
    }
    result["result_sha256"] = sha_bytes(canonical(result))
    OUTPUT.write_bytes(json.dumps(
        result, indent=2, sort_keys=True, ensure_ascii=False,
    ).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": result["status"],
        "output": OUTPUT.relative_to(ROOT).as_posix(),
        "file_sha256": sha_file(OUTPUT),
        "result_sha256": result["result_sha256"],
        "oracle_detection_count": 5,
        "platform_detection_count": 0,
        "populated_leaf_count": 19,
        "registered_performance_timing_count": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
