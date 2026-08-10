"""Independent reconstruction for Goal5696 DEFAULT front-door evidence.

This module imports neither the front door nor the selector/compiler.  It
rebuilds selection through the already independent Goal5695 receipt
reconstructor and then independently validates plan, source, native-launch,
program, output, and admission bindings.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .default_physical_selection_reconstruct import reconstruct_default_receipt


_PLAN_SCHEMA = "rtdl.default_compiler_frontdoor.plan.v1"
_ADMISSION_SCHEMA = "rtdl.default_compiler_frontdoor.execution_admission.v1"
_TRAVERSAL_SCHEMA = "rtdl.physical_execution.traversal_receipt.v1"
_POLICY = "rtdl.default_compiler_frontdoor.goal5696.v1"
_OPTIX_CAPABILITY = "OPTIX_TRAVERSAL_PROGRAM"


class DefaultFrontdoorReconstructionError(RuntimeError):
    pass


def _fail(code: str, detail: str = "") -> None:
    raise DefaultFrontdoorReconstructionError(
        f"{code}: {detail}" if detail else code
    )


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mapping(value: object, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        _fail("EXPECTED_MAPPING", field)
    return value


def _sha(value: object, field: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or value != value.lower()
        or any(char not in "0123456789abcdef" for char in value)
    ):
        _fail("INVALID_SHA256", field)
    return value


def _program_id(name: str) -> int:
    if not isinstance(name, str) or not name:
        _fail("INVALID_PROGRAM_BUNDLE_NAME")
    value = 1469598103934665603
    for byte in name.encode("utf-8"):
        value ^= byte
        value = (value * 1099511628211) & ((1 << 64) - 1)
    return value


def _count(snapshot: Mapping[str, object], name: str) -> int:
    value = snapshot.get(name)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _fail("INVALID_NATIVE_SNAPSHOT_COUNT", name)
    return value


def reconstruct_default_plan(
    plan: Mapping[str, object], *, repository_root: Path | None = None
) -> dict[str, object]:
    if plan.get("schema") != _PLAN_SCHEMA or plan.get("policy_version") != _POLICY:
        _fail("UNSUPPORTED_PLAN")
    if plan.get("status") != "PLANNED":
        _fail("PLAN_NOT_SUCCESSFUL")
    claimed = _sha(plan.get("plan_sha256"), "plan_sha256")
    body = dict(plan)
    body.pop("plan_sha256", None)
    if _digest(body) != claimed:
        _fail("PLAN_DIGEST_MISMATCH")
    selection = _mapping(plan.get("selection_receipt"), "selection_receipt")
    rebuilt_selection = reconstruct_default_receipt(selection)
    if rebuilt_selection.get("status") != "PASS":
        _fail("SELECTION_RECONSTRUCTION_FAILED")
    if selection.get("receipt_sha256") != plan.get("selection_receipt_sha256"):
        _fail("SELECTION_RECEIPT_BINDING_MISMATCH")
    if rebuilt_selection.get("winner_stable_id") != plan.get(
        "selected_candidate_stable_id"
    ):
        _fail("WINNER_BINDING_MISMATCH")
    if selection.get("winner_candidate_sha256") != plan.get(
        "selected_candidate_sha256"
    ):
        _fail("WINNER_DIGEST_BINDING_MISMATCH")
    candidates = selection.get("candidates")
    if not isinstance(candidates, list):
        _fail("INVALID_SELECTION_CANDIDATES")
    selected_candidates = [
        row
        for row in candidates
        if isinstance(row, Mapping)
        and row.get("stable_id") == plan.get("selected_candidate_stable_id")
    ]
    if len(selected_candidates) != 1:
        _fail("SELECTED_CANDIDATE_CARDINALITY_MISMATCH")
    expected_policy = selected_candidates[0].get("physical_configuration_policy")
    observed_policy = plan.get("selected_physical_configuration_policy")
    if _canonical_bytes(expected_policy) != _canonical_bytes(observed_policy):
        _fail("PHYSICAL_CONFIGURATION_POLICY_BINDING_MISMATCH")
    policy_digest = None
    if observed_policy is not None:
        policy = _mapping(observed_policy, "selected_physical_configuration_policy")
        policy_digest = _sha(
            plan.get("selected_physical_configuration_policy_sha256"),
            "selected_physical_configuration_policy_sha256",
        )
        policy_contract_digest = _sha(
            policy.get("policy_contract_sha256"),
            "physical_configuration_policy.policy_contract_sha256",
        )
        policy_body = dict(policy)
        policy_body.pop("policy_contract_sha256", None)
        if _digest(policy) != policy_digest or _digest(
            policy_body
        ) != policy_contract_digest:
            _fail("PHYSICAL_CONFIGURATION_POLICY_DIGEST_MISMATCH")
        if (
            policy.get("schema")
            != "rtdl.physical_configuration_policy.cell_mbr_inline.v1"
            or policy.get("application_identity_used") is not False
            or policy.get("timing_or_learned_input_used") is not False
            or policy.get("universal_optimality_claimed") is not False
        ):
            _fail("INVALID_PHYSICAL_CONFIGURATION_POLICY")
        floor = policy.get("prior_floor")
        cap = policy.get("reviewed_cap")
        if (
            isinstance(floor, bool)
            or not isinstance(floor, int)
            or floor <= 0
            or isinstance(cap, bool)
            or not isinstance(cap, int)
            or cap < floor
        ):
            _fail("INVALID_PHYSICAL_CONFIGURATION_POLICY_RANGE")
        relative = policy.get("source_path")
        anchor = policy.get("source_anchor")
        if not isinstance(relative, str) or not relative or not isinstance(anchor, str) or not anchor:
            _fail("INVALID_PHYSICAL_CONFIGURATION_POLICY_SOURCE")
        root = (
            Path(__file__).resolve().parents[2]
            if repository_root is None
            else Path(repository_root).resolve()
        )
        path = (root / relative).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            _fail("PHYSICAL_CONFIGURATION_POLICY_SOURCE_OUTSIDE_REPOSITORY")
        if not path.is_file() or _sha256_file(path) != _sha(
            policy.get("source_sha256"), "physical_configuration_policy.source_sha256"
        ):
            _fail("PHYSICAL_CONFIGURATION_POLICY_SOURCE_IDENTITY_MISMATCH")
        if anchor not in path.read_text(encoding="utf-8"):
            _fail("PHYSICAL_CONFIGURATION_POLICY_SOURCE_ANCHOR_MISSING")
    elif plan.get("selected_physical_configuration_policy_sha256") is not None:
        _fail("UNEXPECTED_PHYSICAL_CONFIGURATION_POLICY_DIGEST")
    target = _mapping(plan.get("target"), "target")
    required = target.get("required_physical_capabilities")
    if not isinstance(required, list):
        _fail("INVALID_REQUIRED_CAPABILITIES")
    capabilities = plan.get("selected_physical_capabilities")
    if not isinstance(capabilities, list):
        _fail("INVALID_SELECTED_CAPABILITIES")
    mandatory = _OPTIX_CAPABILITY in required
    selected_optix = _OPTIX_CAPABILITY in capabilities
    if plan.get("mandatory_optix_target") is not mandatory:
        _fail("MANDATORY_OPTIX_FLAG_MISMATCH")
    if mandatory and not selected_optix:
        _fail("MANDATORY_OPTIX_SELECTED_NONTRAVERSAL_CANDIDATE")
    if plan.get("behavioral_optix_receipt_required") is not selected_optix:
        _fail("BEHAVIORAL_RECEIPT_REQUIREMENT_MISMATCH")
    if plan.get("candidate_override_accepted") is not False:
        _fail("CANDIDATE_OVERRIDE_ACCEPTED")
    for field in (
        "application_identity_used",
        "candidate_executed",
        "static_capability_is_behavioral_proof",
        "behavioral_optix_claimed",
        "silicon_rt_core_utilization_claimed",
        "production_default_changed",
    ):
        if plan.get(field) is not False:
            _fail("FORBIDDEN_PLAN_CLAIM_OR_SIDE_EFFECT", field)

    program_digest = None
    if selected_optix:
        program = _mapping(plan.get("optix_program_contract"), "optix_program_contract")
        program_digest = _sha(
            program.get("program_contract_sha256"), "program_contract_sha256"
        )
        program_body = dict(program)
        program_body.pop("program_contract_sha256", None)
        if _digest(program_body) != program_digest:
            _fail("PROGRAM_CONTRACT_DIGEST_MISMATCH")
        if program.get("candidate_stable_id") != plan.get(
            "selected_candidate_stable_id"
        ):
            _fail("PROGRAM_CANDIDATE_BINDING_MISMATCH")
        names = program.get("program_bundles")
        ids = program.get("program_bundle_ids")
        if not isinstance(names, list) or not names:
            _fail("EMPTY_PROGRAM_SET")
        if ids != [_program_id(str(name)) for name in names]:
            _fail("PROGRAM_ID_RECONSTRUCTION_MISMATCH")
        source_rows = program.get("source_evidence")
        if not isinstance(source_rows, list) or not source_rows:
            _fail("EMPTY_SOURCE_EVIDENCE")
        root = (
            Path(__file__).resolve().parents[2]
            if repository_root is None
            else Path(repository_root).resolve()
        )
        for index, raw in enumerate(source_rows):
            row = _mapping(raw, f"source_evidence[{index}]")
            relative = row.get("path")
            if not isinstance(relative, str) or not relative:
                _fail("INVALID_SOURCE_PATH", str(index))
            path = (root / relative).resolve()
            try:
                path.relative_to(root)
            except ValueError:
                _fail("SOURCE_OUTSIDE_REPOSITORY", relative)
            if not path.is_file() or _sha256_file(path) != _sha(
                row.get("sha256"), f"source_evidence[{index}].sha256"
            ):
                _fail("SOURCE_IDENTITY_MISMATCH", relative)
            source = path.read_text(encoding="utf-8")
            role = row.get("source_role")
            if role not in {
                "device_program_and_bound_launch",
                "device_program_with_optix_trace",
                "bound_launch",
            }:
                _fail("INVALID_SOURCE_ROLE", f"{relative}:{role}")
            anchors = row.get("required_anchors")
            if not isinstance(anchors, list) or not anchors:
                _fail("EMPTY_SOURCE_ANCHORS", relative)
            for anchor_index, anchor in enumerate(anchors):
                if not isinstance(anchor, str) or not anchor or anchor not in source:
                    _fail(
                        "SOURCE_ANCHOR_MISSING",
                        f"{relative}:required_anchors[{anchor_index}]",
                    )
        roles = {str(_mapping(raw, "source_evidence").get("source_role")) for raw in source_rows}
        if not roles.intersection(
            {"device_program_and_bound_launch", "device_program_with_optix_trace"}
        ):
            _fail("DEVICE_PROGRAM_SOURCE_MISSING")
        if not roles.intersection({"device_program_and_bound_launch", "bound_launch"}):
            _fail("BOUND_LAUNCH_SOURCE_MISSING")

    route_identity_fields = {
        "selection_receipt_sha256": plan.get("selection_receipt_sha256"),
        "winner_stable_id": plan.get("selected_candidate_stable_id"),
        "program_contract_sha256": program_digest,
    }
    # Plans frozen before Goal5707 did not carry either configuration-policy
    # field.  Reconstruct their original route identity exactly; new plans
    # always carry both fields (including explicit null for non-parameterized
    # candidates), so their identity is unambiguously parameter-complete.
    if (
        "selected_physical_configuration_policy" in plan
        or "selected_physical_configuration_policy_sha256" in plan
    ):
        route_identity_fields["physical_configuration_policy_sha256"] = (
            policy_digest
        )
    expected_route_identity = "rtdl.default/" + _digest(route_identity_fields)
    if plan.get("prescribed_route_identity") != expected_route_identity:
        _fail("PRESCRIBED_ROUTE_IDENTITY_MISMATCH")

    return {
        "schema": "rtdl.default_compiler_frontdoor.plan_reconstruction.v1",
        "status": "PASS",
        "plan_sha256": claimed,
        "selection_receipt_sha256": plan.get("selection_receipt_sha256"),
        "winner_stable_id": plan.get("selected_candidate_stable_id"),
        "program_contract_sha256": program_digest,
        "physical_configuration_policy_sha256": policy_digest,
        "behavioral_receipt_still_required": selected_optix,
        "imports_frontdoor_selector_or_compiler": False,
    }


def reconstruct_default_execution_admission(
    plan: Mapping[str, object],
    traversal_receipt: Mapping[str, object],
    admission: Mapping[str, object],
) -> dict[str, object]:
    plan_recount = reconstruct_default_plan(plan)
    if admission.get("schema") != _ADMISSION_SCHEMA or admission.get(
        "policy_version"
    ) != _POLICY:
        _fail("UNSUPPORTED_ADMISSION")
    if admission.get("status") != "PASS":
        _fail("ADMISSION_NOT_SUCCESSFUL")
    claimed_admission = _sha(
        admission.get("admission_sha256"), "admission_sha256"
    )
    admission_body = dict(admission)
    admission_body.pop("admission_sha256", None)
    if _digest(admission_body) != claimed_admission:
        _fail("ADMISSION_DIGEST_MISMATCH")
    if traversal_receipt.get("schema") != _TRAVERSAL_SCHEMA:
        _fail("UNSUPPORTED_TRAVERSAL_RECEIPT")
    claimed_receipt = _sha(
        traversal_receipt.get("receipt_sha256"), "receipt_sha256"
    )
    receipt_body = dict(traversal_receipt)
    receipt_body.pop("receipt_sha256", None)
    if _digest(receipt_body) != claimed_receipt:
        _fail("TRAVERSAL_RECEIPT_DIGEST_MISMATCH")
    for field, expected in (
        ("plan_sha256", plan_recount["plan_sha256"]),
        ("traversal_receipt_sha256", claimed_receipt),
        ("verified_output_digest", traversal_receipt.get("output_digest")),
        ("provider_library_sha256", traversal_receipt.get("provider_library_sha256")),
    ):
        if admission.get(field) != expected:
            _fail("ADMISSION_BINDING_MISMATCH", field)
    if traversal_receipt.get("physical_executor_classification") != "optix_traversal_observed":
        _fail("OPTIX_TRAVERSAL_NOT_OBSERVED")
    if traversal_receipt.get("route_identity") != plan.get("prescribed_route_identity"):
        _fail("ROUTE_IDENTITY_MISMATCH")
    action = _mapping(plan.get("action"), "action")
    if traversal_receipt.get("semantic_digest") != action.get("action_digest"):
        _fail("SEMANTIC_DIGEST_MISMATCH")
    program = _mapping(plan.get("optix_program_contract"), "optix_program_contract")
    names = program.get("program_bundles")
    ids = program.get("program_bundle_ids")
    if traversal_receipt.get("expected_program_bundles") != names:
        _fail("EXPECTED_PROGRAM_NAMES_MISMATCH")
    if traversal_receipt.get("expected_program_bundle_ids") != ids:
        _fail("EXPECTED_PROGRAM_IDS_MISMATCH")
    if traversal_receipt.get("expected_program_observed_at_receipt_edge") is not True:
        _fail("EXPECTED_PROGRAM_NOT_OBSERVED")
    snapshot = _mapping(traversal_receipt.get("native_snapshot"), "native_snapshot")
    nonce = _mapping(traversal_receipt.get("nonce"), "nonce")
    if snapshot.get("nonce_hi") != nonce.get("hi") or snapshot.get(
        "nonce_lo"
    ) != nonce.get("lo"):
        _fail("NONCE_BINDING_MISMATCH")
    successful = _count(snapshot, "successful_launch_count")
    if (
        successful <= 0
        or _count(snapshot, "attempted_launch_count") != successful
        or _count(snapshot, "failed_launch_count") != 0
        or _count(snapshot, "complete_context_launch_count") != successful
        or _count(snapshot, "incomplete_context_launch_count") != 0
        or _count(snapshot, "context_bind_count") != successful
    ):
        _fail("LAUNCH_OR_CONTEXT_COUNTS_INVALID")
    for field in (
        "pending_context_at_finish",
        "session_error",
        "incomplete_callsite_record_count",
    ):
        if _count(snapshot, field) != 0:
            _fail("AUDIT_SESSION_NOT_CLEAN", field)
    for field in (
        "raygen_invocation_count",
        "first_traversable",
        "last_traversable",
        "program_bundle_mix",
        "traversable_mix",
        "pipeline_mix",
        "sbt_mix",
        "stream_mix",
        "params_mix",
        "callsite_mix",
    ):
        if _count(snapshot, field) <= 0:
            _fail("MISSING_BEHAVIORAL_BINDING", field)
    observed_edges = {
        _count(snapshot, "first_program_bundle_id"),
        _count(snapshot, "last_program_bundle_id"),
    } - {0}
    if not set(ids).issubset(observed_edges):
        _fail("PROGRAM_SET_NOT_BOUND_AT_EDGES")
    for field, expected in (
        ("behavioral_optix_proven", True),
        ("silicon_rt_core_utilization_proven", False),
        ("whole_endpoint_rt_only_proven", False),
        ("partner_stages_rejected", False),
    ):
        if admission.get(field) is not expected:
            _fail("ADMISSION_CLAIM_BOUNDARY_MISMATCH", field)

    return {
        "schema": "rtdl.default_compiler_frontdoor.execution_reconstruction.v1",
        "status": "PASS",
        "plan_sha256": plan_recount["plan_sha256"],
        "traversal_receipt_sha256": claimed_receipt,
        "admission_sha256": claimed_admission,
        "behavioral_optix_proven": True,
        "silicon_rt_core_utilization_proven": False,
        "whole_endpoint_rt_only_proven": False,
        "imports_frontdoor_selector_or_compiler": False,
    }


__all__ = [
    "DefaultFrontdoorReconstructionError",
    "reconstruct_default_execution_admission",
    "reconstruct_default_plan",
]
