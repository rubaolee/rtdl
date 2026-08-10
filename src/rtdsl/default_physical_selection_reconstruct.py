"""Independent reconstruction of a Goal5695 DEFAULT selection receipt.

This module intentionally imports neither :mod:`default_physical_selection`
nor any compiler/planner module.  It uses only the canonical receipt bytes and
the frozen public algorithm constants duplicated here.  A disagreement is a
hard verification failure, not a reason to trust the producer.
"""

from __future__ import annotations

import hashlib
import json
from typing import Mapping


_SUPPORTED_CONTRACTS = {
    (
        "rtdl.default_physical_selection.receipt.v2",
        "rtdl.default_physical_selection.goal5695_a1.v2",
    ): False,
    (
        "rtdl.default_physical_selection.receipt.v3",
        "rtdl.default_physical_selection.goal5695_a2.v3",
    ): True,
    (
        "rtdl.default_physical_selection.receipt.v4",
        "rtdl.default_physical_selection.goal5698_a4.v4",
    ): True,
    (
        "rtdl.default_physical_selection.receipt.v5",
        "rtdl.default_physical_selection.goal5699.v5",
    ): True,
    (
        "rtdl.default_physical_selection.receipt.v6",
        "rtdl.default_physical_selection.goal5699_a2.v6",
    ): True,
}
_SOURCE_BOUND_MEMORY_CONTRACTS = {
    (
        "rtdl.default_physical_selection.receipt.v4",
        "rtdl.default_physical_selection.goal5698_a4.v4",
    ),
    (
        "rtdl.default_physical_selection.receipt.v5",
        "rtdl.default_physical_selection.goal5699.v5",
    ),
    (
        "rtdl.default_physical_selection.receipt.v6",
        "rtdl.default_physical_selection.goal5699_a2.v6",
    ),
}
_NORMAL = "NORMAL"
_VALIDATION = "VALIDATION"
_ANNOTATION_NONE = "NONE"
_ANNOTATION_COMPLETE = "COMPLETE"
_MAX_CANDIDATES = 64
_UINT64_MAX = (1 << 64) - 1
_MAX_WORK_POLYNOMIAL_DEGREE = 8
_MAX_WORK_LOGARITHMIC_DEGREE = 4
_ROLE_TIER = {"DEPLOYABLE_LOWERING": 0, "REFERENCE_FALLBACK": 1}
_DEVICE_EXECUTION_CLASSES = {"cuda", "optix", "mixed_optix_numba"}


class ReceiptReconstructionError(RuntimeError):
    pass


def _fail(code: str, detail: str = "") -> None:
    raise ReceiptReconstructionError(f"{code}: {detail}" if detail else code)


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


def _u64(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0 or value > _UINT64_MAX:
        _fail("INVALID_UNSIGNED_FIELD", field)
    return value


def _mul(left: int, right: int, field: str) -> int:
    if left and right > _UINT64_MAX // left:
        _fail("RESOURCE_BOUND_OVERFLOW", field)
    return left * right


def _add(left: int, right: int, field: str) -> int:
    result = left + right
    if result > _UINT64_MAX:
        _fail("RESOURCE_BOUND_OVERFLOW", field)
    return result


def _require_mapping(value: object, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        _fail("EXPECTED_MAPPING", field)
    return value


def _require_list(value: object, field: str) -> list[object]:
    if not isinstance(value, list):
        _fail("EXPECTED_LIST", field)
    return value


def _memory(declaration: Mapping[str, object], action: Mapping[str, object]) -> int:
    model = _require_mapping(declaration.get("memory_bound"), "memory_bound")
    total = _u64(model.get("base_bytes"), "memory_bound.base_bytes")
    for extent_name, multiplier_name in (
        ("input_bytes", "input_bytes_multiplier"),
        ("output_bytes", "output_bytes_multiplier"),
        ("prepared_bytes", "prepared_bytes_multiplier"),
    ):
        extent = _u64(action.get(extent_name), f"action.{extent_name}")
        multiplier = _u64(model.get(multiplier_name), f"memory_bound.{multiplier_name}")
        total = _add(total, _mul(extent, multiplier, extent_name), "memory_bound.total")
    for cardinality_name, item_bytes_name, multiplier_name in (
        (
            "logical_cardinality_bound",
            "logical_item_bytes_bound",
            "logical_item_multiplicity",
        ),
        (
            "pair_cardinality_bound",
            "pair_item_bytes_bound",
            "pair_item_multiplicity",
        ),
    ):
        cardinality = _u64(action.get(cardinality_name), f"action.{cardinality_name}")
        item_bytes = _u64(action.get(item_bytes_name), f"action.{item_bytes_name}")
        multiplier = _u64(model.get(multiplier_name), f"memory_bound.{multiplier_name}")
        relation_bytes = _mul(cardinality, item_bytes, cardinality_name)
        total = _add(
            total,
            _mul(relation_bytes, multiplier, multiplier_name),
            "memory_bound.total",
        )
    return total


def _resource_bound_digest(
    declaration: Mapping[str, object], *, source_bound_memory: bool
) -> str:
    payload = {
        "stable_id": declaration.get("stable_id"),
        "scope": "one_complete_action_no_amortization",
        "work": declaration.get("work_order"),
        "host_round_trips": declaration.get("host_round_trips"),
        "materializations": declaration.get("materializations"),
        "device_synchronizations": declaration.get("device_synchronizations"),
        "launches": declaration.get("launches"),
        "memory_bound": declaration.get("memory_bound"),
        "memory_proof_kind": declaration.get("memory_proof_kind"),
        "resource_bound_verified": declaration.get("resource_bound_verified"),
        "max_logical_cardinality": declaration.get("max_logical_cardinality"),
        "max_pair_cardinality": declaration.get("max_pair_cardinality"),
        "source_path": declaration.get("source_path"),
        "source_sha256": declaration.get("source_sha256"),
        "source_anchor": declaration.get("source_anchor"),
    }
    if source_bound_memory:
        payload.update(
            {
                "memory_source_path": declaration.get("memory_source_path"),
                "memory_source_sha256": declaration.get("memory_source_sha256"),
                "memory_source_anchor": declaration.get("memory_source_anchor"),
            }
        )
    return _digest(payload)


def _proof_digest(candidate: Mapping[str, object]) -> str:
    capabilities = _require_list(
        candidate.get("physical_capabilities"), "physical_capabilities"
    )
    payload = {
        "stable_id": candidate.get("stable_id"),
        "exactness_verified": True,
        "determinism_verified": True,
        "ordering_verified": True,
        "physical_capabilities": sorted(set(capabilities)),
        "source_path": candidate.get("source_path"),
        "source_sha256": candidate.get("source_sha256"),
        "source_anchor": candidate.get("source_anchor"),
    }
    return _digest(payload)


def _instantiate(
    declaration: Mapping[str, object], action: Mapping[str, object]
) -> dict[str, object]:
    candidate = dict(declaration)
    candidate.update(
        {
            "action_digest": action.get("action_digest"),
            "output_contract_digest": action.get("output_contract_digest"),
            "work_domain_digest": action.get("work_domain_digest"),
            "conservative_memory_bytes": _memory(declaration, action),
        }
    )
    return candidate


def _reasons(
    candidate: Mapping[str, object],
    action: Mapping[str, object],
    target: Mapping[str, object],
    *,
    normalized: bool,
    source_bound_memory: bool,
) -> list[str]:
    reasons: list[str] = []
    work = _require_list(candidate.get("work_order"), "work_order")
    if len(work) != 2:
        _fail("WORK_ORDER_OUT_OF_GRAMMAR", "work.arity")
    polynomial = _u64(work[0], "work.p")
    logarithmic = _u64(work[1], "work.q")
    if polynomial > _MAX_WORK_POLYNOMIAL_DEGREE:
        _fail("WORK_ORDER_OUT_OF_GRAMMAR", "work.p")
    if logarithmic > _MAX_WORK_LOGARITHMIC_DEGREE:
        _fail("WORK_ORDER_OUT_OF_GRAMMAR", "work.q")
    role = candidate.get("selection_role")
    if role not in _ROLE_TIER:
        reasons.append("SELECTION_ROLE_UNVERIFIED")
    accepted_contracts = set(
        _require_list(
            candidate.get("accepted_action_contract_classes"),
            "accepted_action_contract_classes",
        )
    )
    if action.get("action_contract_class") not in accepted_contracts:
        reasons.append("ACTION_CONTRACT_CLASS_NOT_ACCEPTED")
    if not all(
        candidate.get(field) is True
        for field in ("exactness_verified", "determinism_verified", "ordering_verified")
    ):
        reasons.append("MANDATORY_PROOF_OBLIGATION_UNVERIFIED")
    if normalized and _proof_digest(candidate) != candidate.get("proof_digest"):
        reasons.append("PROOF_DIGEST_MISMATCH")
    if candidate.get("resource_bound_verified") is not True:
        reasons.append("RESOURCE_BOUND_UNPROVED")
    if _resource_bound_digest(
        candidate, source_bound_memory=source_bound_memory
    ) != candidate.get("resource_bound_digest"):
        reasons.append("RESOURCE_BOUND_DIGEST_MISMATCH")
    admission_checks = (
        ("proof_digest", "admitted_proof_digests", "ACTION_PROOF_NOT_ADMITTED"),
        (
            "resource_bound_digest",
            "admitted_resource_bound_digests",
            "ACTION_RESOURCE_BOUND_NOT_ADMITTED",
        ),
        (
            "reuse_contract_digest",
            "admitted_reuse_contract_digests",
            "ACTION_REUSE_CONTRACT_NOT_ADMITTED",
        ),
        ("template_digest", "admitted_template_digests", "ACTION_TEMPLATE_NOT_ADMITTED"),
    )
    for candidate_field, action_field, code in admission_checks:
        admitted = set(_require_list(action.get(action_field), action_field))
        if candidate.get(candidate_field) not in admitted:
            reasons.append(code)
    for field, code in (
        ("action_digest", "ACTION_DIGEST_MISMATCH"),
        ("output_contract_digest", "OUTPUT_CONTRACT_MISMATCH"),
        ("work_domain_digest", "WORK_DOMAIN_MISMATCH"),
    ):
        if candidate.get(field) != action.get(field):
            reasons.append(code)
    available = set(_require_list(target.get("available_providers"), "available_providers"))
    required = set(_require_list(candidate.get("required_providers"), "required_providers"))
    if not required.issubset(available):
        reasons.append("REQUIRED_PROVIDER_UNAVAILABLE")
    available_abis = set(
        _require_list(
            target.get("available_provider_abi_requirement_digests"),
            "available_provider_abi_requirement_digests",
        )
    )
    if candidate.get("provider_abi_requirement_digest") not in available_abis:
        reasons.append("PROVIDER_ABI_REQUIREMENT_UNAVAILABLE")
    allowed = set(_require_list(target.get("allowed_execution_classes"), "allowed_execution_classes"))
    if allowed and candidate.get("execution_class") not in allowed:
        reasons.append("EXECUTION_CLASS_NOT_ALLOWED")
    required_capabilities_raw = target.get("required_physical_capabilities", [])
    candidate_capabilities_raw = candidate.get("physical_capabilities", [])
    required_capabilities = _require_list(
        required_capabilities_raw, "required_physical_capabilities"
    )
    candidate_capabilities = _require_list(
        candidate_capabilities_raw, "physical_capabilities"
    )
    if required_capabilities != sorted(set(required_capabilities)):
        _fail("NONCANONICAL_REQUIRED_CAPABILITY_SET")
    if candidate_capabilities and candidate_capabilities != sorted(
        set(candidate_capabilities)
    ):
        _fail("NONCANONICAL_PHYSICAL_CAPABILITY_SET")
    if not set(required_capabilities).issubset(set(candidate_capabilities)):
        reasons.append("REQUIRED_PHYSICAL_CAPABILITY_MISSING")
    profile = target.get("profile")
    if profile not in (_NORMAL, _VALIDATION):
        _fail("UNKNOWN_TARGET_PROFILE", str(profile))
    if profile == _NORMAL and candidate.get("normal_default_eligible") is not True:
        reasons.append("NORMAL_DEFAULT_NOT_AUTHORIZED")
    max_logical = candidate.get("max_logical_cardinality")
    if max_logical is not None and _u64(
        action.get("logical_cardinality_bound"), "action.logical_cardinality_bound"
    ) > _u64(max_logical, "candidate.max_logical_cardinality"):
        reasons.append("LOGICAL_CARDINALITY_BOUND_EXCEEDED")
    max_pair = candidate.get("max_pair_cardinality")
    if max_pair is not None and _u64(
        action.get("pair_cardinality_bound"), "action.pair_cardinality_bound"
    ) > _u64(max_pair, "candidate.max_pair_cardinality"):
        reasons.append("PAIR_CARDINALITY_BOUND_EXCEEDED")
    if _u64(candidate.get("conservative_memory_bytes"), "candidate.memory") > _u64(
        target.get("memory_limit_bytes"), "target.memory_limit_bytes"
    ):
        reasons.append("CONSERVATIVE_MEMORY_BOUND_EXCEEDED")
    return reasons


def _avoidable_device_synchronizations(
    candidate: Mapping[str, object],
    action: Mapping[str, object],
    *,
    normalized: bool,
) -> int:
    total = _u64(candidate.get("device_synchronizations"), "device_synchronizations")
    if not normalized:
        return total
    host_visible = action.get("host_visible_canonical_output_required")
    if not isinstance(host_visible, bool):
        _fail("INVALID_ENDPOINT_COMPLETION_CONTRACT")
    mandatory = int(
        host_visible and candidate.get("execution_class") in _DEVICE_EXECUTION_CLASSES
    )
    if total < mandatory:
        _fail(
            "DEVICE_SYNCHRONIZATION_BELOW_MANDATORY_ENDPOINT",
            str(candidate.get("stable_id")),
        )
    return total - mandatory


def _avoidable_device_launches(
    candidate: Mapping[str, object],
    *,
    normalized: bool,
) -> int:
    total = _u64(candidate.get("launches"), "launches")
    if not normalized:
        return total
    mandatory = int(candidate.get("execution_class") in _DEVICE_EXECUTION_CLASSES)
    if total < mandatory:
        _fail(
            "DEVICE_LAUNCHES_BELOW_MANDATORY_EXECUTION",
            str(candidate.get("stable_id")),
        )
    return total - mandatory


def _key(
    candidate: Mapping[str, object],
    action: Mapping[str, object],
    *,
    normalized: bool,
) -> tuple[object, ...]:
    role = candidate.get("selection_role")
    if role not in _ROLE_TIER:
        _fail("SELECTION_ROLE_UNVERIFIED", str(candidate.get("stable_id")))
    work = _require_list(candidate.get("work_order"), "work_order")
    if len(work) != 2:
        _fail("INVALID_WORK_ORDER")
    work_pair = (_u64(work[0], "work.p"), _u64(work[1], "work.q"))
    if work_pair[0] > _MAX_WORK_POLYNOMIAL_DEGREE:
        _fail("WORK_ORDER_OUT_OF_GRAMMAR", "work.p")
    if work_pair[1] > _MAX_WORK_LOGARITHMIC_DEGREE:
        _fail("WORK_ORDER_OUT_OF_GRAMMAR", "work.q")
    return (
        _ROLE_TIER[str(role)],
        work_pair,
        _u64(candidate.get("host_round_trips"), "host_round_trips"),
        _u64(candidate.get("materializations"), "materializations"),
        _u64(candidate.get("conservative_memory_bytes"), "conservative_memory_bytes"),
        _avoidable_device_synchronizations(candidate, action, normalized=normalized),
        _avoidable_device_launches(candidate, normalized=normalized),
        str(candidate.get("stable_id")),
    )


def _dominates(
    left: Mapping[str, object],
    right: Mapping[str, object],
    action: Mapping[str, object],
    *,
    normalized: bool,
) -> bool:
    left_work = _require_list(left.get("work_order"), "left.work_order")
    right_work = _require_list(right.get("work_order"), "right.work_order")
    left_pair = (_u64(left_work[0], "left.work.p"), _u64(left_work[1], "left.work.q"))
    right_pair = (
        _u64(right_work[0], "right.work.p"),
        _u64(right_work[1], "right.work.q"),
    )
    if left_pair[0] > _MAX_WORK_POLYNOMIAL_DEGREE or right_pair[0] > _MAX_WORK_POLYNOMIAL_DEGREE:
        _fail("WORK_ORDER_OUT_OF_GRAMMAR", "work.p")
    if left_pair[1] > _MAX_WORK_LOGARITHMIC_DEGREE or right_pair[1] > _MAX_WORK_LOGARITHMIC_DEGREE:
        _fail("WORK_ORDER_OUT_OF_GRAMMAR", "work.q")
    lvalues: tuple[object, ...] = (
        left_pair,
        _u64(left.get("host_round_trips"), "left.h"),
        _u64(left.get("materializations"), "left.m"),
        _u64(left.get("conservative_memory_bytes"), "left.b"),
        _avoidable_device_synchronizations(left, action, normalized=normalized),
        _avoidable_device_launches(left, normalized=normalized),
    )
    rvalues: tuple[object, ...] = (
        right_pair,
        _u64(right.get("host_round_trips"), "right.h"),
        _u64(right.get("materializations"), "right.m"),
        _u64(right.get("conservative_memory_bytes"), "right.b"),
        _avoidable_device_synchronizations(right, action, normalized=normalized),
        _avoidable_device_launches(right, normalized=normalized),
    )
    return all(a <= b for a, b in zip(lvalues, rvalues)) and any(
        a < b for a, b in zip(lvalues, rvalues)
    )


def reconstruct_default_receipt(receipt: Mapping[str, object]) -> dict[str, object]:
    """Rebuild every decision-bearing field and return a verification summary."""

    body = dict(receipt)
    claimed_receipt_digest = body.pop("receipt_sha256", None)
    if claimed_receipt_digest != _digest(body):
        _fail("RECEIPT_SHA256_MISMATCH")
    contract = (receipt.get("schema"), receipt.get("policy_version"))
    if contract not in _SUPPORTED_CONTRACTS:
        _fail("UNSUPPORTED_RECEIPT_CONTRACT")
    normalized = _SUPPORTED_CONTRACTS[contract]
    source_bound_memory = contract in _SOURCE_BOUND_MEMORY_CONTRACTS
    status = receipt.get("status")
    if status not in ("SELECTED", "FAIL_CLOSED"):
        _fail("UNKNOWN_RECEIPT_STATUS")

    action = _require_mapping(receipt.get("action"), "action")
    target = _require_mapping(receipt.get("target"), "target")
    registry = _require_mapping(receipt.get("registry"), "registry")
    if receipt.get("action_descriptor_sha256") != _digest(action):
        _fail("ACTION_DESCRIPTOR_SHA256_MISMATCH")
    if receipt.get("target_descriptor_sha256") != _digest(target):
        _fail("TARGET_DESCRIPTOR_SHA256_MISMATCH")
    if receipt.get("registry_sha256") != _digest(registry):
        _fail("REGISTRY_SHA256_MISMATCH")

    declarations = _require_list(registry.get("declarations"), "registry.declarations")
    ids = [str(_require_mapping(row, "declaration").get("stable_id")) for row in declarations]
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        _fail("NONCANONICAL_OR_DUPLICATE_REGISTRY")
    expected_declarations = [
        _require_mapping(row, "declaration")
        for row in declarations
        if _require_mapping(row, "declaration").get("semantic_kind") == action.get("semantic_kind")
        and action.get("action_contract_class")
        in _require_list(
            _require_mapping(row, "declaration").get("accepted_action_contract_classes"),
            "accepted_action_contract_classes",
        )
    ]
    candidates = _require_list(receipt.get("candidates"), "candidates")

    if status == "FAIL_CLOSED":
        error_code = receipt.get("error_code")
        if not isinstance(error_code, str) or not error_code:
            _fail("MISSING_FAILURE_CODE")
        condition_verified = False
        if error_code == "ACTION_KIND_NOT_IN_REGISTRY":
            condition_verified = not expected_declarations
        elif error_code == "CANDIDATE_CAP_EXCEEDED_BEFORE_COMPARISON":
            condition_verified = len(expected_declarations) > _MAX_CANDIDATES
        elif error_code == "UNKNOWN_ANNOTATION_MODE":
            condition_verified = receipt.get("annotation_mode") not in (
                _ANNOTATION_NONE,
                _ANNOTATION_COMPLETE,
            )
        elif error_code in {"RESOURCE_BOUND_OVERFLOW", "UNSIGNED_FIELD_OUT_OF_RANGE"}:
            try:
                [_instantiate(row, action) for row in expected_declarations]
            except ReceiptReconstructionError as exc:
                condition_verified = error_code in str(exc)
        reconstructed_evaluations: list[dict[str, object]] = []
        comparison_started = False
        else_candidates: list[dict[str, object]] | None = None
        if error_code not in {
            "ACTION_KIND_NOT_IN_REGISTRY",
            "CANDIDATE_CAP_EXCEEDED_BEFORE_COMPARISON",
            "UNKNOWN_ANNOTATION_MODE",
            "RESOURCE_BOUND_OVERFLOW",
            "UNSIGNED_FIELD_OUT_OF_RANGE",
        }:
            if len(expected_declarations) <= _MAX_CANDIDATES:
                expected_candidates = [_instantiate(row, action) for row in expected_declarations]
                if error_code == "INCOMPLETE_OR_REBOUND_CANDIDATE_SET":
                    condition_verified = _canonical_bytes(candidates) != _canonical_bytes(
                        expected_candidates
                    )
                elif error_code == "NO_LEGAL_CANDIDATE":
                    else_candidates = expected_candidates
                    for candidate in expected_candidates:
                        reasons = _reasons(
                            candidate,
                            action,
                            target,
                            normalized=normalized,
                            source_bound_memory=source_bound_memory,
                        )
                        reconstructed_evaluations.append(
                            {
                                "stable_id": candidate.get("stable_id"),
                                "candidate_digest": _digest(candidate),
                                "legal": not reasons,
                                "rejection_reasons": reasons,
                                "selection_key": (
                                    list(
                                        _key(
                                            candidate,
                                            action,
                                            normalized=normalized,
                                        )
                                    )
                                    if not reasons
                                    else None
                                ),
                            }
                        )
                    condition_verified = all(
                        row["rejection_reasons"] for row in reconstructed_evaluations
                    )
                    if source_bound_memory:
                        condition_verified = condition_verified and (
                            _canonical_bytes(candidates)
                            == _canonical_bytes(expected_candidates)
                        )
                        comparison_started = True
        if not condition_verified:
            _fail("FAILURE_CONDITION_NOT_RECONSTRUCTED", error_code)
        if receipt.get("candidate_set_sha256") != _digest(candidates):
            _fail("CANDIDATE_SET_SHA256_MISMATCH")
        if error_code == "NO_LEGAL_CANDIDATE":
            if else_candidates is None:
                _fail("NO_LEGAL_CANDIDATE_SET_NOT_RECONSTRUCTED")
            if source_bound_memory:
                if _canonical_bytes(receipt.get("evaluations")) != _canonical_bytes(
                    reconstructed_evaluations
                ):
                    _fail("FAILURE_LEGALITY_RECONSTRUCTION_MISMATCH")
                expected_detail = ";".join(
                    f"{row['stable_id']}:{','.join(row['rejection_reasons'])}"
                    for row in reconstructed_evaluations
                )
                if receipt.get("error_detail") != expected_detail:
                    _fail("FAILURE_DETAIL_RECONSTRUCTION_MISMATCH")
            elif receipt.get("evaluations") is not None:
                _fail("UNEXPECTED_LEGACY_FAILURE_EVALUATIONS")
        elif receipt.get("evaluations") not in (None, []):
            _fail("UNEXPECTED_FAILURE_EVALUATIONS")
        if receipt.get("candidate_comparison_started") is not comparison_started:
            _fail("FAILURE_COMPARISON_STATE_MISMATCH")
        for field in (
            "sort_started",
            "candidate_executed",
            "timing_or_learned_input_used",
            "application_identity_used",
            "production_default_changed",
        ):
            if receipt.get(field) is not False:
                _fail("FAILURE_RECEIPT_SIDE_EFFECT_OR_CLAIM", field)
        return {
            "schema": "rtdl.default_physical_selection.reconstruction.v1",
            "status": "PASS",
            "receipt_sha256": claimed_receipt_digest,
            "registry_sha256": receipt.get("registry_sha256"),
            "reconstructed_status": "FAIL_CLOSED",
            "verified_error_code": error_code,
            "candidate_comparison_started": comparison_started,
            "sort_started": False,
            "imports_selector_or_compiler": False,
        }

    if not expected_declarations:
        _fail("ACTION_KIND_NOT_IN_REGISTRY")
    if len(expected_declarations) > _MAX_CANDIDATES:
        _fail("CANDIDATE_CAP_EXCEEDED_BEFORE_COMPARISON")

    expected_candidates = [_instantiate(row, action) for row in expected_declarations]
    if _canonical_bytes(candidates) != _canonical_bytes(expected_candidates):
        _fail("INCOMPLETE_OR_REBOUND_CANDIDATE_SET")
    if receipt.get("candidate_set_sha256") != _digest(candidates):
        _fail("CANDIDATE_SET_SHA256_MISMATCH")

    evaluations: list[dict[str, object]] = []
    legal: list[Mapping[str, object]] = []
    for raw in candidates:
        candidate = _require_mapping(raw, "candidate")
        reasons = _reasons(
            candidate,
            action,
            target,
            normalized=normalized,
            source_bound_memory=source_bound_memory,
        )
        is_legal = not reasons
        if is_legal:
            legal.append(candidate)
        evaluations.append(
            {
                "stable_id": candidate.get("stable_id"),
                "candidate_digest": _digest(candidate),
                "legal": is_legal,
                "rejection_reasons": reasons,
                "selection_key": (
                    list(_key(candidate, action, normalized=normalized))
                    if is_legal
                    else None
                ),
            }
        )
    if not legal:
        _fail("NO_LEGAL_CANDIDATE")
    if _canonical_bytes(receipt.get("evaluations")) != _canonical_bytes(evaluations):
        _fail("LEGALITY_OR_KEY_RECONSTRUCTION_MISMATCH")

    ordered = sorted(
        legal,
        key=lambda item: _key(item, action, normalized=normalized),
    )
    order_ids = [str(row.get("stable_id")) for row in ordered]
    winner = ordered[0]
    if receipt.get("complete_legal_order") != order_ids:
        _fail("COMPLETE_LEGAL_ORDER_MISMATCH")
    if receipt.get("winner_stable_id") != winner.get("stable_id"):
        _fail("WINNER_MISMATCH")
    if receipt.get("winner_candidate_sha256") != _digest(winner):
        _fail("WINNER_DIGEST_MISMATCH")
    if receipt.get("selected_reference_fallback") != (
        winner.get("selection_role") == "REFERENCE_FALLBACK"
    ):
        _fail("FALLBACK_STATUS_MISMATCH")

    annotation_mode = receipt.get("annotation_mode")
    edges: list[list[str]] = []
    comparison_count = 0
    if annotation_mode == _ANNOTATION_COMPLETE:
        for left in legal:
            for right in legal:
                if left is right:
                    continue
                comparison_count += 6
                if _dominates(left, right, action, normalized=normalized):
                    edges.append([str(left.get("stable_id")), str(right.get("stable_id"))])
        edges.sort()
    elif annotation_mode != _ANNOTATION_NONE:
        _fail("UNKNOWN_ANNOTATION_MODE", str(annotation_mode))
    if receipt.get("dominance_edges") != edges:
        _fail("DOMINANCE_ANNOTATION_MISMATCH")
    if receipt.get("dominance_dimension_comparisons") != comparison_count:
        _fail("DOMINANCE_COMPARISON_COUNT_MISMATCH")
    if receipt.get("legal_candidate_count") != len(legal):
        _fail("LEGAL_CANDIDATE_COUNT_MISMATCH")
    for forbidden_true in (
        "timing_or_learned_input_used",
        "application_identity_used",
        "candidate_executed",
        "production_default_changed",
    ):
        if receipt.get(forbidden_true) is not False:
            _fail("FORBIDDEN_CLAIM_OR_INPUT", forbidden_true)

    return {
        "schema": "rtdl.default_physical_selection.reconstruction.v1",
        "status": "PASS",
        "receipt_sha256": claimed_receipt_digest,
        "registry_sha256": receipt.get("registry_sha256"),
        "candidate_count": len(candidates),
        "legal_candidate_count": len(legal),
        "winner_stable_id": winner.get("stable_id"),
        "complete_legal_order": order_ids,
        "annotation_mode": annotation_mode,
        "dominance_edge_count": len(edges),
        "dominance_dimension_comparisons": comparison_count,
        "imports_selector_or_compiler": False,
    }


__all__ = ["ReceiptReconstructionError", "reconstruct_default_receipt"]
