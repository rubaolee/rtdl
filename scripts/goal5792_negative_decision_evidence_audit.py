#!/usr/bin/env python3
"""Rebuild the bounded Goal5790-A1 negative-decision evidence for Goal5792."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


PINS: dict[str, tuple[str, str]] = {
    "work_authority": (
        "history/internal_docs/goal5792_unknown_lane_classification_work_authority_20260819.json",
        "465cd43d1fa93a567ac85c53dc210165aa33f95c9a55d6e4064795d4804df9c3",
    ),
    "a1_plan": (
        "history/internal_docs/goal5790_a1_rejected_program_suite_plan_20260816.md",
        "66123ebf1d1b3a6c61b77ac89c2ada61dcb730c6291cd195d5fc2ed11b57ce37",
    ),
    "a1_result": (
        "history/internal_docs/goal5790_a1_home_rejected_program_suite_result_20260816.json",
        "800707087dcabfd677eff41062215cde22eca94f0d5102ab637eece815160dcf",
    ),
    "controller_result": (
        "history/internal_docs/goal5790_a1_home_s3_independent_audit_staging_v2_20260816/controller/RESULT.json",
        "eb1828cf0303661064f9dd03a07efb8f373045bd8e70f3e21f85fc0e7e621f67",
    ),
    "evidence": (
        "history/internal_docs/goal5790_a1_home_postrun_validation_a2_20260816/GOAL5790_A1_EVIDENCE.tar.gz",
        "006842c86db89c4974fe308534f2ba137921615dd7df2b4ea07fecb2173bd0ac",
    ),
    "evidence_twin": (
        "history/internal_docs/goal5790_a1_home_postrun_validation_a2_20260816/GOAL5790_A1_EVIDENCE_TWIN.tar.gz",
        "006842c86db89c4974fe308534f2ba137921615dd7df2b4ea07fecb2173bd0ac",
    ),
    "independent_recount": (
        "history/internal_docs/goal5790_a1_home_postrun_validation_a2_20260816/INDEPENDENT_RECOUNT.json",
        "70264aa110f5b780e88ca125d89be0f8138c49796aa5202303b97aef0cc2e522",
    ),
    "external_review": (
        "history/internal_docs/review_goal5790_a1_home_rejected_program_suite_20260816.md",
        "778c996516c85ab185c8e3be23132794348827ad13f54d774e402fc42f09e9d9",
    ),
    "review_absorption": (
        "history/internal_docs/goal5790_a1_owner_returned_external_review_absorption_20260817.json",
        "e830a626689cc362c8223c70544e28bf97d0aa00086727b901cdcb54677f91eb",
    ),
    "postreview_clarification": (
        "history/internal_docs/goal5790_a1_postreview_claim_clarification_20260817.md",
        "9fc25d0b5bb0bf81551a119066b6c0913178d0c56da54747212677354a92cbff",
    ),
    "delivery_manifest": (
        "history/internal_docs/goal5790_a1_delivery_manifest_20260816.json",
        "cc309514aa7e6d96a1431c1ab8e848b89efd143ef82971e798dc6758809041e0",
    ),
}

CASE_IDS = (
    "builtin_triangle.discrete_interval_boundary.v1",
    "builtin_triangle.deterministic_tie_rank.v1",
    "builtin_triangle.checked_u64_overflow.v1",
    "builtin_triangle.weighted_multiplicity.v1",
    "builtin_triangle.front_back_orientation.v1",
    "custom_aabb.closed_boundary.v1",
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_sha(value: Any) -> str:
    return _sha256(json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8"))


def _read_pins(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, bytes]]:
    rows: dict[str, dict[str, Any]] = {}
    blobs: dict[str, bytes] = {}
    for role, (relative, expected) in PINS.items():
        path = root / relative
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f"missing or non-regular pin: {role}")
        data = path.read_bytes()
        actual = _sha256(data)
        if actual != expected:
            raise RuntimeError(f"pin drift: {role}: {actual}")
        blobs[role] = data
        rows[role] = {"path": relative, "sha256": actual, "bytes": len(data)}
    return rows, blobs


def _strict_json(data: bytes, role: str) -> dict[str, Any]:
    try:
        value = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid JSON: {role}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"non-object JSON: {role}")
    return value


def _validate_cases(
    result: dict[str, Any],
    controller: dict[str, Any],
    recount: dict[str, Any],
) -> list[dict[str, Any]]:
    if tuple(case.get("case_id") for case in result.get("cases", [])) != CASE_IDS:
        raise RuntimeError("controlling result case order drifted")
    if tuple(case.get("case_id") for case in controller.get("cases", [])) != CASE_IDS:
        raise RuntimeError("controller case order drifted")
    if tuple(case.get("case_id") for case in recount.get("cases", [])) != CASE_IDS:
        raise RuntimeError("recount case order drifted")

    rows: list[dict[str, Any]] = []
    facade_count = 0
    tps_count = 0
    for result_case, controller_case, recount_case in zip(
        result["cases"], controller["cases"], recount["cases"], strict=True,
    ):
        case_id = result_case["case_id"]
        if controller_case.get("case_sha256") != result_case.get("case_sha256"):
            raise RuntimeError(f"case digest mismatch: {case_id}")
        if recount_case.get("case_sha256") != result_case.get("case_sha256"):
            raise RuntimeError(f"recount case digest mismatch: {case_id}")
        if recount_case.get("raw_sha256") != result_case.get("raw_case_sha256"):
            raise RuntimeError(f"raw case digest mismatch: {case_id}")

        arms = controller_case.get("arms")
        if not isinstance(arms, dict) or set(arms) != {
            "accepted_control", "diagnostic_counterfactual", "product_admission_reject",
        }:
            raise RuntimeError(f"arm set mismatch: {case_id}")
        accepted = arms["accepted_control"]
        diagnostic = arms["diagnostic_counterfactual"]
        rejected = arms["product_admission_reject"]
        if any(arm.get("status") != "PASS" for arm in (accepted, diagnostic, rejected)):
            raise RuntimeError(f"non-PASS arm: {case_id}")
        accepted_result = accepted.get("arm_result", {})
        diagnostic_result = diagnostic.get("arm_result", {})
        reject_result = rejected.get("arm_result", {})
        if accepted_result.get("matches_own_oracle") is not True \
                or accepted_result.get("matches_requested_semantics") is not True:
            raise RuntimeError(f"accepted control oracle mismatch: {case_id}")
        if diagnostic_result.get("matches_own_oracle") is not True \
                or diagnostic_result.get("matches_requested_semantics") is not False \
                or diagnostic_result.get("counterexample_observed") is not True \
                or diagnostic_result.get("behaviorally_true_optix") is not True:
            raise RuntimeError(f"diagnostic is not a legal silent-wrong counterexample: {case_id}")
        if diagnostic_result.get("output") != result_case.get("diagnostic_output"):
            raise RuntimeError(f"diagnostic output mismatch: {case_id}")
        receipts = diagnostic_result.get("traversal_receipts")
        if not isinstance(receipts, list) or not receipts:
            raise RuntimeError(f"diagnostic traversal receipt missing: {case_id}")
        successful_launch_count = 0
        raygen_invocation_count = 0
        receipt_sha256s: list[str] = []
        for receipt in receipts:
            snapshot = receipt.get("native_snapshot", {})
            if receipt.get("physical_executor_classification") != "optix_traversal_observed" \
                    or receipt.get("expected_program_observed_at_receipt_edge") is not True:
                raise RuntimeError(f"diagnostic is not behavioral OptiX: {case_id}")
            successful = snapshot.get("successful_launch_count")
            raygen = snapshot.get("raygen_invocation_count")
            if type(successful) is not int or successful <= 0 \
                    or type(raygen) is not int or raygen <= 0 \
                    or snapshot.get("complete_context_launch_count") != successful \
                    or snapshot.get("attempted_launch_count") != successful:
                raise RuntimeError(f"diagnostic launch accounting drifted: {case_id}")
            for zero_field in (
                "failed_launch_count", "incomplete_context_launch_count",
                "incomplete_callsite_record_count", "pending_context_at_finish", "session_error",
            ):
                if type(snapshot.get(zero_field)) is not int or snapshot[zero_field] != 0:
                    raise RuntimeError(f"diagnostic launch did not complete: {case_id}:{zero_field}")
            receipt_sha = receipt.get("receipt_sha256")
            if not isinstance(receipt_sha, str) or len(receipt_sha) != 64:
                raise RuntimeError(f"diagnostic receipt digest malformed: {case_id}")
            receipt_sha256s.append(receipt_sha)
            successful_launch_count += successful
            raygen_invocation_count += raygen
        if reject_result.get("verdict") != "INCOMPATIBLE" \
                or reject_result.get("named_case_rule_id") != controller_case.get("expected_rule_id") \
                or reject_result.get("execution_authorized") is not False \
                or reject_result.get("executable_issued") is not False:
            raise RuntimeError(f"product admission did not fail closed: {case_id}")
        for field in (
            "compiler_call_count", "low_level_compiler_call_count", "native_prepare_call_count",
            "native_execute_call_count", "traversal_launch_count",
        ):
            if type(reject_result.get(field)) is not int or reject_result[field] != 0:
                raise RuntimeError(f"reject arm executed work: {case_id}:{field}")
        if reject_result.get("production_facade_called") is True:
            facade_count += 1
        elif reject_result.get("product_rejection_gate") == "verify_typed_physical_schema":
            tps_count += 1
        else:
            raise RuntimeError(f"unexpected rejection gate: {case_id}")

        rows.append({
            "case_id": case_id,
            "application_family": result_case["application_family"],
            "geometry_family": result_case["geometry_family"],
            "requested_output": result_case.get("requested_output",
                                                result_case.get("requested_mathematical_output")),
            "accepted_output_or_disposition": result_case.get(
                "accepted_output", result_case.get("accepted_disposition")),
            "diagnostic_output": result_case["diagnostic_output"],
            "matches_own_oracle": True,
            "matches_requested_semantics": False,
            "behaviorally_true_optix": True,
            "traversal_receipt_sha256s": receipt_sha256s,
            "successful_complete_launch_count": successful_launch_count,
            "raygen_invocation_count": raygen_invocation_count,
            "admission_verdict": "INCOMPATIBLE",
            "rejection_gate": result_case["gate"],
            "rule_id": result_case["rule_id"],
            "case_sha256": result_case["case_sha256"],
            "raw_case_sha256": result_case["raw_case_sha256"],
            "negative_decision_disposition": (
                "REJECT_ASSOCIATION__PREVENTS_LEGAL_SELF_CONSISTENT_SILENT_WRONG_EXECUTION"
            ),
        })
    if (facade_count, tps_count) != (5, 1):
        raise RuntimeError("five-plus-one rejection split drifted")
    return rows


def build_result(root: Path) -> dict[str, Any]:
    root = root.resolve()
    pins, blobs = _read_pins(root)
    authority = _strict_json(blobs["work_authority"], "work_authority")
    if authority.get("goal5792_required_output", {}).get(
        "goal5790_a1_rejected_programs_must_be_presented_as_negative_decision_evidence"
    ) is not True:
        raise RuntimeError("Goal5792 negative-evidence requirement absent")
    result = _strict_json(blobs["a1_result"], "a1_result")
    controller = _strict_json(blobs["controller_result"], "controller_result")
    recount = _strict_json(blobs["independent_recount"], "independent_recount")
    absorption = _strict_json(blobs["review_absorption"], "review_absorption")

    expected_counts = {
        "case_count": 6,
        "arm_count": 18,
        "product_reject_count": 6,
        "public_admitted_facade_reject_count": 5,
        "typed_physical_schema_reject_count": 1,
        "diagnostic_wrong_answer_count": 6,
        "accepted_control_count": 6,
        "behavioral_true_optix_receipt_count": 11,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    for key, expected in expected_counts.items():
        if type(result.get("counts", {}).get(key)) is not int \
                or result["counts"][key] != expected:
            raise RuntimeError(f"controlling count drift: {key}")
    if result.get("counts", {}).get("pod_used") is not False \
            or result.get("counts", {}).get("performance_claimed") is not False:
        raise RuntimeError("controlling result expanded scope")
    if result.get("home_execution", {}).get("controller", {}).get(
        "result_file_sha256") != PINS["controller_result"][1]:
        raise RuntimeError("controller result is not bound by the controlling result")
    if recount.get("status") != "PASS" or recount.get("case_count") != 6 \
            or recount.get("diagnostic_wrong_answer_count") != 6 \
            or recount.get("product_reject_count") != 6:
        raise RuntimeError("independent recount summary drifted")
    if absorption.get("external_review", {}).get("sha256") != PINS["external_review"][1] \
            or absorption.get("external_review", {}).get("verdict") \
            != "APPROVE_AT_BOUNDED_HOME_SEMANTIC_PHYSICAL_REJECTION_SCOPE":
        raise RuntimeError("external review absorption drifted")

    cases = _validate_cases(result, controller, recount)
    if (
        sum(len(row["traversal_receipt_sha256s"]) for row in cases),
        sum(row["successful_complete_launch_count"] for row in cases),
        sum(row["raygen_invocation_count"] for row in cases),
    ) != (6, 7, 9):
        raise RuntimeError("diagnostic traversal totals drifted")
    output: dict[str, Any] = {
        "schema": "rtdl.goal5792.negative_decision_evidence_audit.v1",
        "goal": 5792,
        "status": "PASS__SIX_LEGAL_SILENT_WRONG_ENCODINGS_REJECTED_FAIL_CLOSED",
        "pins": pins,
        "summary": {
            "case_count": 6,
            "application_family_count": 4,
            "geometry_family_count": 2,
            "arm_count": 18,
            "diagnostic_legally_executes_and_matches_own_oracle_count": 6,
            "diagnostic_matches_requested_semantics_count": 0,
            "product_admission_fail_closed_count": 6,
            "public_facade_reject_count": 5,
            "typed_physical_schema_reject_count": 1,
            "behaviorally_true_optix_receipt_count": 11,
            "diagnostic_traversal_receipt_count": sum(
                len(row["traversal_receipt_sha256s"]) for row in cases),
            "diagnostic_successful_complete_launch_count": sum(
                row["successful_complete_launch_count"] for row in cases),
            "diagnostic_raygen_invocation_count": sum(
                row["raygen_invocation_count"] for row in cases),
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "pod_used": False,
        },
        "cases": cases,
        "decision_evidence_interpretation": {
            "legal_execution_implies_requested_semantics": False,
            "own_oracle_and_requested_semantics_are_distinct": True,
            "unknown_may_be_silently_upgraded_to_compatible": False,
            "suite_is_bounded_negative_decision_evidence": True,
            "arbitrary_python_semantics_inferred": False,
            "universal_soundness_or_completeness_proved": False,
            "compile_admission_certifies_concrete_runtime_arrays": False,
            "five_facade_plus_one_earlier_typed_schema_split_preserved": True,
        },
        "authorization": {
            "authorizes_gpu_or_pod": False,
            "authorizes_registered_timing": False,
            "authorizes_product_or_native_changes": False,
            "authorizes_publication_or_submission": False,
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
    print(json.dumps({
        "status": result["status"],
        "case_count": result["summary"]["case_count"],
        "silent_wrong_count": result["summary"][
            "diagnostic_legally_executes_and_matches_own_oracle_count"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
