from __future__ import annotations

from typing import Any


REQUIRED_PRIMITIVE_CONTRACT_FIELDS = (
    "app_row",
    "primitive",
    "backend",
    "backend_scope",
    "active_v1_4_backend",
    "backend_contract_role",
    "same_contract_baseline_required",
    "mode",
    "build_layout",
    "probe_layout",
    "result_layout",
    "phase_counters",
    "claim_boundary",
    "migration_status",
)

VALID_BACKEND_CONTRACT_ROLES = (
    "cpu_rt_baseline_and_fallback",
    "nvidia_rt_target",
    "compatibility_or_inactive",
)

VALID_MIGRATION_STATUSES = (
    "compatibility_wrapper_metadata_only",
    "diagnostic_metadata_only",
)

ACTIVE_V1_4_BACKENDS = ("embree", "optix")


def primitive_contract_schema_errors(contract: dict[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    for field in REQUIRED_PRIMITIVE_CONTRACT_FIELDS:
        if field not in contract:
            errors.append(f"missing required primitive_contract field: {field}")

    backend = str(contract.get("backend", ""))
    backend_scope = tuple(contract.get("backend_scope", ()))
    role = contract.get("backend_contract_role")
    migration_status = contract.get("migration_status")

    if role not in VALID_BACKEND_CONTRACT_ROLES:
        errors.append(f"invalid backend_contract_role: {role}")
    if migration_status not in VALID_MIGRATION_STATUSES:
        errors.append(f"invalid migration_status: {migration_status}")
    if backend_scope != ACTIVE_V1_4_BACKENDS:
        errors.append(f"backend_scope must be {ACTIVE_V1_4_BACKENDS!r}, got {backend_scope!r}")

    expected_active = backend in ACTIVE_V1_4_BACKENDS
    if bool(contract.get("active_v1_4_backend")) != expected_active:
        errors.append("active_v1_4_backend does not match backend/backend_scope")
    if bool(contract.get("same_contract_baseline_required")) != expected_active:
        errors.append("same_contract_baseline_required does not match backend/backend_scope")

    if expected_active and role == "compatibility_or_inactive":
        errors.append("active backend cannot use compatibility_or_inactive role")
    if not expected_active and role != "compatibility_or_inactive":
        errors.append("inactive backend must use compatibility_or_inactive role")
    if backend == "embree" and role != "cpu_rt_baseline_and_fallback":
        errors.append("Embree must be cpu_rt_baseline_and_fallback")
    if backend == "optix" and role != "nvidia_rt_target":
        errors.append("OptiX must be nvidia_rt_target")

    phase_counters = contract.get("phase_counters")
    if not isinstance(phase_counters, tuple) or not phase_counters:
        errors.append("phase_counters must be a non-empty tuple")
    if not str(contract.get("claim_boundary", "")).strip():
        errors.append("claim_boundary must be non-empty")

    if contract.get("app_row") == "polygon_set_jaccard":
        if contract.get("status") != "optix_still_slower_with_reason":
            errors.append("Jaccard status must remain optix_still_slower_with_reason")
        if contract.get("public_wording_allowed") is not False:
            errors.append("Jaccard public_wording_allowed must be false")
        if contract.get("migration_status") != "diagnostic_metadata_only":
            errors.append("Jaccard must remain diagnostic_metadata_only")
        if contract.get("future_score_primitive_status") != "blocked_by_native_score_reduction":
            errors.append("Jaccard score primitive must remain blocked by native score reduction")
        bounded_collection_policy = contract.get("bounded_collection_policy")
        if not isinstance(bounded_collection_policy, dict):
            errors.append("Jaccard must declare bounded_collection_policy")
        else:
            if bounded_collection_policy.get("collection_primitive") != "COLLECT_K_BOUNDED":
                errors.append("Jaccard bounded collection primitive must be COLLECT_K_BOUNDED")
            if bounded_collection_policy.get("status") != "experimental_diagnostic_only":
                errors.append("Jaccard bounded collection must remain experimental_diagnostic_only")
            if bounded_collection_policy.get("overflow_policy") != "no_silent_truncation":
                errors.append("Jaccard bounded collection must reject silent truncation")
            if bounded_collection_policy.get("failure_mode") != "fail_closed_overflow":
                errors.append("Jaccard bounded collection must fail closed on overflow")
            if bounded_collection_policy.get("truncation_allowed") is not False:
                errors.append("Jaccard bounded collection truncation_allowed must be false")
            if bounded_collection_policy.get("complete_candidate_coverage_required") is not True:
                errors.append("Jaccard bounded collection requires complete candidate coverage")
            if bounded_collection_policy.get("score_reduction_allowed_on_overflow") is not False:
                errors.append("Jaccard score reduction must not run after overflow")

    return tuple(errors)


def validate_primitive_contract(contract: dict[str, Any]) -> None:
    errors = primitive_contract_schema_errors(contract)
    if errors:
        raise ValueError("; ".join(errors))
