from __future__ import annotations

import hashlib
import json
from typing import Any

from .bounded_collection_contracts import validate_v1_5_collect_k_bounded_contracts
from .bounded_collection_contracts import validate_v1_5_collect_k_bounded_resolution
from .float_reduction_contracts import validate_v1_5_float_sum_reduction_contracts
from .generic_db_primitives import validate_v1_5_db_compact_summary_contracts
from .grouped_reduction_contracts import validate_v1_5_grouped_reduction_contracts
from .reduction_runtime import V1_5_GENERIC_SCALAR_REDUCTION_PRIMITIVES
from .v1_5_migration_inventory import (
    ACTIVE_V1_5_BACKENDS,
    FROZEN_BEFORE_V2_1_BACKENDS,
    validate_v1_5_generic_migration_inventory,
    v1_5_generic_migration_blockers,
)
from .v1_5_standalone_app_classification import (
    validate_v1_5_standalone_app_classification_matrix,
)
from .v1_5_standalone_correctness import (
    validate_v1_5_standalone_correctness_summary,
)


V1_5_INTERNAL_READINESS_STATUS = "internal_v1_5_contract_gate_passing_non_public"
V1_5_INTERNAL_READINESS_CLAIM_BOUNDARY = (
    "internal v1.5 contract readiness only; not public v1.5 release wording; "
    "not public speedup wording; v1.0 tag remains unchanged; public claims require 3-AI consensus"
)
V1_5_INTERNAL_READINESS_STABLE_SUMMARY_PRIMITIVES = (
    "COUNT_HITS",
    "REDUCE_FLOAT(MIN)",
    "REDUCE_FLOAT(MAX)",
    "REDUCE_FLOAT(SUM)",
    "REDUCE_INT(COUNT)",
    "REDUCE_INT(SUM)",
)
V1_5_INTERNAL_READINESS_ALLOWED_INVENTORY_STATUSES = ("pod_verified_generic",)
V1_5_INTERNAL_READINESS_ALLOWED_EXPERIMENTAL_CONTRACT_STATUSES = (
    "experimental_diagnostic_only",
)
V1_5_INTERNAL_READINESS_REQUIRED_BLOCKER_PHRASES = (
    "app-level continuations remain outside v1.5 generic subpath scope",
    "whole-app speedup wording remains blocked",
    "public NVIDIA wording remains blocked",
    "3-AI consensus",
)
V1_5_INTERNAL_READINESS_ALLOWED_NEXT_ACTIONS = (
    "continue_internal_contract_hardening",
    "collect_pod_validation_from_git",
    "request_external_review_before_public_claims",
)
V1_5_INTERNAL_READINESS_BLOCKED_NEXT_ACTIONS = (
    "public_v1_5_release_wording",
    "public_speedup_wording",
    "release_tag_action",
    "stable_collect_k_bounded_promotion",
    "new_pre_v2_1_backend_implementation",
)
V1_5_INTERNAL_READINESS_PUBLIC_CLAIM_PRECONDITIONS = (
    "exact_subpath_evidence",
    "fresh_git_pod_validation",
    "external_3_ai_consensus",
    "public_wording_review",
)
V1_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PARTNERS = ("claude", "gemini")
V1_5_INTERNAL_READINESS_ACCEPTED_EXTERNAL_REVIEW_PARTNERS = ("claude",)
V1_5_INTERNAL_READINESS_SOURCE_USAGE_MODE = "source_tree_pythonpath"
V1_5_INTERNAL_READINESS_SOURCE_USAGE_COMMAND = "PYTHONPATH=src:. python ..."
V1_5_INTERNAL_READINESS_CURRENT_PUBLIC_RELEASE_TAG = "v1.0"
V1_5_INTERNAL_READINESS_SCOPE_KIND = "generic_traversal_plus_reduction_subpaths"
V1_5_INTERNAL_READINESS_EXCLUDED_APP_SCOPE = (
    "app_level_continuations",
    "whole_app_speedup",
    "public_nvidia_speedup",
)
V1_5_INTERNAL_READINESS_EVIDENCE_STATE = "internal_pod_validated_non_claim_grade"
V1_5_INTERNAL_READINESS_REQUIRED_PUBLIC_EVIDENCE = (
    "claim_grade_exact_subpath_evidence",
    "same_contract_baseline",
    "reviewed_public_wording_packet",
)
V1_5_INTERNAL_READINESS_FALSE_AUTHORIZATION_FLAGS = (
    "public_claims_ready",
    "external_3_ai_consensus_ready",
    "editable_install_claim_authorized",
    "package_release_artifact_authorized",
    "new_backend_implementation_authorized",
    "pre_v2_1_frozen_backend_work_authorized",
    "stable_collect_k_bounded_promotion_authorized",
    "current_public_release_tag_move_authorized",
    "new_public_release_tag_authorized",
    "app_level_continuations_authorized_as_generic",
    "whole_app_speedup_claim_authorized",
    "public_nvidia_speedup_claim_authorized",
    "claim_grade_exact_subpath_evidence_ready",
    "same_contract_baseline_ready",
    "reviewed_public_wording_packet_ready",
    "public_release_authorized",
    "public_speedup_wording_authorized",
    "release_tag_action_authorized",
)
V1_5_INTERNAL_READINESS_BROAD_LOCAL_SUITE_STATE = "passed_internal_regression"
V1_5_INTERNAL_READINESS_BROAD_LOCAL_SUITE_TESTS = 2656
V1_5_INTERNAL_READINESS_BROAD_LOCAL_SUITE_SKIPPED = 197
V1_5_INTERNAL_READINESS_DECISION_FINGERPRINT_ALGORITHM = "sha256"
V1_5_INTERNAL_READINESS_DECISION_FINGERPRINT_FIELDS = (
    "decision",
    "gate_status",
    "allowed_next_actions",
    "blocked_next_actions",
    "public_claim_preconditions",
    "required_external_review_partners",
    "accepted_external_review_partners",
    "missing_external_review_partners",
    "source_usage_mode",
    "active_backend_scope",
    "frozen_before_v2_1_backends",
    "stable_summary_primitives",
    "experimental_primitives",
    "current_public_release_tag",
    "scope_kind",
    "excluded_app_scope",
    "evidence_state",
    "required_public_evidence",
    "false_authorization_flags",
    "broad_local_suite_state",
    "broad_local_suite_tests",
    "broad_local_suite_skipped",
)
V1_5_STANDALONE_RELEASE_STATUS = "blocked_pending_standalone_language_completion"
V1_5_STANDALONE_RELEASE_SCOPE_KIND = "standalone_embree_optix_language_runtime"
V1_5_STANDALONE_RELEASE_REQUIRED_GATES = (
    "primitive_packet_prerequisite",
    "roadmap_consensus",
    "collect_k_bounded_resolution",
    "app_migration_classification",
    "same_contract_per_app_correctness",
    "same_contract_per_app_benchmarks",
    "test_backed_support_maturity_matrix",
    "release_docs_and_public_wording",
)
V1_5_STANDALONE_RELEASE_BLOCKERS = (
    "same-contract per-app Embree/OptiX benchmark evidence is not yet complete",
    "test-backed support/maturity matrix is not yet complete",
    "v1.5 release docs and public wording must be refreshed after standalone gates pass",
)
V1_5_STANDALONE_RELEASE_ALLOWED_NEXT_ACTIONS = (
    "run_same_contract_per_app_benchmarks",
    "build_test_backed_support_maturity_matrix",
    "refresh_release_docs_and_public_wording",
)
V1_5_1_COLLECT_K_BOUNDED_TRACK = (
    ("v1.5.1", "collect_k_bounded_fail_closed_semantics"),
    ("v1.5.1", "native_embree_optix_collection_parity"),
    ("v1.5.1", "same_contract_collection_benchmarks"),
    ("v1.5.1", "external_review_before_collect_k_promotion"),
)
V1_5_STANDALONE_PARTNER_TRACK = (
    ("v1.6", "partner_api_design"),
    ("v1.7", "first_partner_prototype"),
    ("v1.8", "partner_conformance_suite"),
    ("v1.9", "partner_ecosystem_hardening"),
    ("v2.0", "public_partner_ready_rtdl"),
)


def _count_inventory_statuses(inventory: tuple[dict[str, Any], ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in inventory:
        status = str(row["status"])
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def _count_contract_statuses(contracts: tuple[dict[str, Any], ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for contract in contracts:
        status = str(contract["status"])
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def _contract_surface_counts(
    *,
    inventory_rows: int,
    grouped_contracts: int,
    db_contracts: int,
    float_sum_contracts: int,
    bounded_collection_contracts: int,
) -> dict[str, int]:
    return {
        "inventory_rows": inventory_rows,
        "grouped_contracts": grouped_contracts,
        "db_contracts": db_contracts,
        "float_sum_contracts": float_sum_contracts,
        "bounded_collection_contracts": bounded_collection_contracts,
    }


def _decision_fingerprint(decision: dict[str, Any]) -> str:
    payload = {
        field: decision[field]
        for field in V1_5_INTERNAL_READINESS_DECISION_FINGERPRINT_FIELDS
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _require_tuple_field(
    decision: dict[str, Any],
    field: str,
    expected: tuple[Any, ...],
    message: str,
) -> None:
    if tuple(decision[field]) != expected:
        raise ValueError(message)


def _require_false_field(decision: dict[str, Any], field: str, message: str) -> None:
    if decision[field] is not False:
        raise ValueError(message)


def _missing_external_review_partners(decision: dict[str, Any]) -> tuple[str, ...]:
    accepted = tuple(decision["accepted_external_review_partners"])
    return tuple(
        partner
        for partner in decision["required_external_review_partners"]
        if partner not in accepted
    )


def _validate_decision_next_actions(decision: dict[str, Any]) -> None:
    _require_tuple_field(
        decision,
        "allowed_next_actions",
        V1_5_INTERNAL_READINESS_ALLOWED_NEXT_ACTIONS,
        "v1.5 internal readiness decision must preserve allowed next actions",
    )
    for required_action in V1_5_INTERNAL_READINESS_ALLOWED_NEXT_ACTIONS:
        if required_action not in tuple(decision["allowed_next_actions"]):
            raise ValueError(f"missing allowed internal next action: {required_action}")
    _require_tuple_field(
        decision,
        "blocked_next_actions",
        V1_5_INTERNAL_READINESS_BLOCKED_NEXT_ACTIONS,
        "v1.5 internal readiness decision must preserve blocked next actions",
    )
    for blocked_action in V1_5_INTERNAL_READINESS_BLOCKED_NEXT_ACTIONS:
        if blocked_action not in tuple(decision["blocked_next_actions"]):
            raise ValueError(f"missing blocked public/broad next action: {blocked_action}")


def _validate_decision_public_claim_preconditions(decision: dict[str, Any]) -> None:
    _require_tuple_field(
        decision,
        "public_claim_preconditions",
        V1_5_INTERNAL_READINESS_PUBLIC_CLAIM_PRECONDITIONS,
        "v1.5 internal readiness decision must preserve public claim preconditions",
    )
    for precondition in V1_5_INTERNAL_READINESS_PUBLIC_CLAIM_PRECONDITIONS:
        if precondition not in tuple(decision["public_claim_preconditions"]):
            raise ValueError(f"missing public claim precondition: {precondition}")
    _require_false_field(
        decision,
        "public_claims_ready",
        "v1.5 internal readiness decision must not mark public claims ready",
    )


def _validate_decision_external_review_state(decision: dict[str, Any]) -> None:
    _require_tuple_field(
        decision,
        "required_external_review_partners",
        V1_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PARTNERS,
        "v1.5 internal readiness decision must preserve required external reviewers",
    )
    _require_tuple_field(
        decision,
        "accepted_external_review_partners",
        V1_5_INTERNAL_READINESS_ACCEPTED_EXTERNAL_REVIEW_PARTNERS,
        "v1.5 internal readiness decision must preserve accepted external reviewers",
    )
    missing_external_review_partners = _missing_external_review_partners(decision)
    if tuple(decision["missing_external_review_partners"]) != missing_external_review_partners:
        raise ValueError("v1.5 internal readiness decision must report missing external reviewers")
    if not decision["missing_external_review_partners"]:
        raise ValueError("v1.5 internal readiness decision must not imply 3-AI consensus is complete")
    _require_false_field(
        decision,
        "external_3_ai_consensus_ready",
        "v1.5 internal readiness decision must not mark 3-AI consensus ready",
    )


def _validate_decision_source_usage(decision: dict[str, Any]) -> None:
    if decision["source_usage_mode"] != V1_5_INTERNAL_READINESS_SOURCE_USAGE_MODE:
        raise ValueError("v1.5 internal readiness decision must preserve source-tree usage mode")
    if decision["source_usage_command"] != V1_5_INTERNAL_READINESS_SOURCE_USAGE_COMMAND:
        raise ValueError("v1.5 internal readiness decision must preserve source-tree usage command")


def _validate_decision_backend_boundary(decision: dict[str, Any]) -> None:
    if tuple(decision["active_backend_scope"]) != ("embree", "optix"):
        raise ValueError("v1.5 internal readiness decision must stay scoped to Embree and OptiX")
    if tuple(decision["frozen_before_v2_1_backends"]) != ("vulkan", "hiprt", "apple_rt"):
        raise ValueError("v1.5 internal readiness decision must preserve frozen-before-v2.1 backends")
    if set(decision["active_backend_scope"]) & set(decision["frozen_before_v2_1_backends"]):
        raise ValueError("v1.5 internal readiness decision backend scopes must not overlap")


def _validate_decision_primitive_boundary(decision: dict[str, Any]) -> None:
    _require_tuple_field(
        decision,
        "stable_summary_primitives",
        V1_5_INTERNAL_READINESS_STABLE_SUMMARY_PRIMITIVES,
        "v1.5 internal readiness decision must preserve stable summary primitives",
    )
    if "COLLECT_K_BOUNDED" not in tuple(decision["experimental_primitives"]):
        raise ValueError("v1.5 internal readiness decision must keep COLLECT_K_BOUNDED experimental")
    if "COLLECT_K_BOUNDED" in tuple(decision["stable_summary_primitives"]):
        raise ValueError("v1.5 internal readiness decision must not mark COLLECT_K_BOUNDED stable")
    if decision["experimental_contract_status_counts"] != {"experimental_diagnostic_only": 1}:
        raise ValueError("v1.5 internal readiness decision must preserve experimental status counts")


def _validate_decision_release_and_scope_boundary(decision: dict[str, Any]) -> None:
    if decision["current_public_release_tag"] != V1_5_INTERNAL_READINESS_CURRENT_PUBLIC_RELEASE_TAG:
        raise ValueError("v1.5 internal readiness decision must preserve the current public release tag")
    if decision["scope_kind"] != V1_5_INTERNAL_READINESS_SCOPE_KIND:
        raise ValueError("v1.5 internal readiness decision must preserve generic subpath scope")
    _require_tuple_field(
        decision,
        "excluded_app_scope",
        V1_5_INTERNAL_READINESS_EXCLUDED_APP_SCOPE,
        "v1.5 internal readiness decision must preserve excluded app scope",
    )


def _validate_decision_evidence_boundary(decision: dict[str, Any]) -> None:
    if decision["evidence_state"] != V1_5_INTERNAL_READINESS_EVIDENCE_STATE:
        raise ValueError("v1.5 internal readiness decision must preserve evidence state")
    _require_tuple_field(
        decision,
        "required_public_evidence",
        V1_5_INTERNAL_READINESS_REQUIRED_PUBLIC_EVIDENCE,
        "v1.5 internal readiness decision must preserve required public evidence",
    )
    _require_tuple_field(
        decision,
        "false_authorization_flags",
        V1_5_INTERNAL_READINESS_FALSE_AUTHORIZATION_FLAGS,
        "v1.5 internal readiness decision must preserve false authorization flags",
    )
    for flag in V1_5_INTERNAL_READINESS_FALSE_AUTHORIZATION_FLAGS:
        if decision[flag] is not False:
            raise ValueError(f"v1.5 internal readiness decision must not authorize {flag}")


def _validate_decision_broad_suite_state(decision: dict[str, Any]) -> None:
    if decision["broad_local_suite_state"] != V1_5_INTERNAL_READINESS_BROAD_LOCAL_SUITE_STATE:
        raise ValueError("v1.5 internal readiness decision must preserve broad local suite state")
    if int(decision["broad_local_suite_tests"]) != V1_5_INTERNAL_READINESS_BROAD_LOCAL_SUITE_TESTS:
        raise ValueError("v1.5 internal readiness decision must preserve broad local test count")
    if int(decision["broad_local_suite_skipped"]) != V1_5_INTERNAL_READINESS_BROAD_LOCAL_SUITE_SKIPPED:
        raise ValueError("v1.5 internal readiness decision must preserve broad local skipped count")
    _require_false_field(
        decision,
        "broad_local_suite_claim_grade_evidence",
        "v1.5 internal readiness decision must not treat broad suite as claim-grade",
    )


def _validate_decision_fingerprint_state(decision: dict[str, Any]) -> None:
    if (
        decision["decision_fingerprint_algorithm"]
        != V1_5_INTERNAL_READINESS_DECISION_FINGERPRINT_ALGORITHM
    ):
        raise ValueError("v1.5 internal readiness decision must preserve fingerprint algorithm")
    _require_tuple_field(
        decision,
        "decision_fingerprint_fields",
        V1_5_INTERNAL_READINESS_DECISION_FINGERPRINT_FIELDS,
        "v1.5 internal readiness decision must preserve fingerprint fields",
    )
    if decision["decision_fingerprint"] != _decision_fingerprint(decision):
        raise ValueError("v1.5 internal readiness decision fingerprint mismatch")


def _validate_decision_claim_boundary(decision: dict[str, Any]) -> None:
    if "not public v1.5 release wording" not in decision["claim_boundary"]:
        raise ValueError("v1.5 internal readiness decision must preserve non-public boundary")


def v1_5_internal_readiness_gate() -> dict[str, Any]:
    """Return the aggregate internal v1.5 contract-readiness gate.

    The gate composes existing validators and summarizes counts for the
    currently verified contract surfaces. It is intentionally non-public:
    passing this gate does not authorize release tags, public v1.5 wording, or
    speedup language.
    """
    inventory = validate_v1_5_generic_migration_inventory()
    grouped_contracts = validate_v1_5_grouped_reduction_contracts()
    db_contracts = validate_v1_5_db_compact_summary_contracts()
    float_sum_contracts = validate_v1_5_float_sum_reduction_contracts()
    bounded_collection_contracts = validate_v1_5_collect_k_bounded_contracts()
    blockers = v1_5_generic_migration_blockers()
    contract_surface_counts = _contract_surface_counts(
        inventory_rows=len(inventory),
        grouped_contracts=len(grouped_contracts),
        db_contracts=len(db_contracts),
        float_sum_contracts=len(float_sum_contracts),
        bounded_collection_contracts=len(bounded_collection_contracts),
    )

    return {
        "status": V1_5_INTERNAL_READINESS_STATUS,
        **contract_surface_counts,
        "contract_surface_counts": contract_surface_counts,
        "total_contract_surfaces": sum(contract_surface_counts.values()),
        "stable_summary_primitives": V1_5_GENERIC_SCALAR_REDUCTION_PRIMITIVES,
        "active_backend_scope": ACTIVE_V1_5_BACKENDS,
        "frozen_before_v2_1_backends": FROZEN_BEFORE_V2_1_BACKENDS,
        "inventory_status_counts": _count_inventory_statuses(inventory),
        "allowed_inventory_statuses": V1_5_INTERNAL_READINESS_ALLOWED_INVENTORY_STATUSES,
        "experimental_contract_status_counts": _count_contract_statuses(
            bounded_collection_contracts
        ),
        "allowed_experimental_contract_statuses": (
            V1_5_INTERNAL_READINESS_ALLOWED_EXPERIMENTAL_CONTRACT_STATUSES
        ),
        "validators": (
            "validate_v1_5_generic_migration_inventory",
            "validate_v1_5_grouped_reduction_contracts",
            "validate_v1_5_db_compact_summary_contracts",
            "validate_v1_5_float_sum_reduction_contracts",
            "validate_v1_5_collect_k_bounded_contracts",
        ),
        "blockers": blockers,
        "required_blocker_phrases": V1_5_INTERNAL_READINESS_REQUIRED_BLOCKER_PHRASES,
        "public_release_authorized": False,
        "public_speedup_wording_authorized": False,
        "release_tag_action_authorized": False,
        "requires_external_consensus_for_public_claims": "3-AI",
        "experimental_primitives": ("COLLECT_K_BOUNDED",),
        "claim_boundary": V1_5_INTERNAL_READINESS_CLAIM_BOUNDARY,
    }


def validate_v1_5_internal_readiness_gate() -> dict[str, Any]:
    gate = v1_5_internal_readiness_gate()
    if gate["status"] != V1_5_INTERNAL_READINESS_STATUS:
        raise ValueError("invalid v1.5 internal readiness gate status")
    for flag in (
        "public_release_authorized",
        "public_speedup_wording_authorized",
        "release_tag_action_authorized",
    ):
        if gate[flag] is not False:
            raise ValueError(f"v1.5 internal readiness gate must not authorize {flag}")
    if gate["requires_external_consensus_for_public_claims"] != "3-AI":
        raise ValueError("public v1.5 claims must remain behind 3-AI consensus")
    if tuple(gate["stable_summary_primitives"]) != V1_5_INTERNAL_READINESS_STABLE_SUMMARY_PRIMITIVES:
        raise ValueError("v1.5 internal readiness gate must preserve stable summary primitives")
    if tuple(gate["active_backend_scope"]) != ("embree", "optix"):
        raise ValueError("v1.5 internal readiness gate must stay scoped to Embree and OptiX")
    if tuple(gate["frozen_before_v2_1_backends"]) != ("vulkan", "hiprt", "apple_rt"):
        raise ValueError("v1.5 internal readiness gate must preserve frozen-before-v2.1 backends")
    if set(gate["active_backend_scope"]) & set(gate["frozen_before_v2_1_backends"]):
        raise ValueError("active and frozen v1.5 backend scopes must not overlap")
    invalid_statuses = sorted(
        set(gate["inventory_status_counts"]) - set(gate["allowed_inventory_statuses"])
    )
    if invalid_statuses:
        raise ValueError(
            "v1.5 internal readiness gate cannot pass with non-verified inventory statuses: "
            f"{', '.join(invalid_statuses)}"
        )
    if sum(int(count) for count in gate["inventory_status_counts"].values()) != int(
        gate["inventory_rows"]
    ):
        raise ValueError("v1.5 internal readiness inventory status counts must match row count")
    invalid_experimental_statuses = sorted(
        set(gate["experimental_contract_status_counts"])
        - set(gate["allowed_experimental_contract_statuses"])
    )
    if invalid_experimental_statuses:
        raise ValueError(
            "v1.5 internal readiness gate cannot pass with promoted experimental statuses: "
            f"{', '.join(invalid_experimental_statuses)}"
        )
    if sum(int(count) for count in gate["experimental_contract_status_counts"].values()) != int(
        gate["bounded_collection_contracts"]
    ):
        raise ValueError(
            "v1.5 internal readiness experimental status counts must match bounded collection count"
        )
    blockers = tuple(gate["blockers"])
    if not blockers:
        raise ValueError("v1.5 internal readiness gate must expose blockers")
    missing_blockers = [
        phrase
        for phrase in gate["required_blocker_phrases"]
        if not any(phrase in blocker for blocker in blockers)
    ]
    if missing_blockers:
        raise ValueError(
            "v1.5 internal readiness blockers are missing required phrases: "
            f"{', '.join(missing_blockers)}"
        )
    boundary = str(gate["claim_boundary"])
    for required_boundary in (
        "internal v1.5 contract readiness only",
        "not public v1.5 release wording",
        "not public speedup wording",
        "v1.0 tag remains unchanged",
        "public claims require 3-AI consensus",
    ):
        if required_boundary not in boundary:
            raise ValueError("v1.5 internal readiness claim boundary is too broad")
    if "COLLECT_K_BOUNDED" not in tuple(gate["experimental_primitives"]):
        raise ValueError("COLLECT_K_BOUNDED must remain represented as experimental")
    for count_field in (
        "inventory_rows",
        "grouped_contracts",
        "db_contracts",
        "float_sum_contracts",
        "bounded_collection_contracts",
    ):
        if int(gate[count_field]) <= 0:
            raise ValueError(f"v1.5 internal readiness count must be positive: {count_field}")
    expected_surface_total = sum(int(count) for count in gate["contract_surface_counts"].values())
    if int(gate["total_contract_surfaces"]) != expected_surface_total:
        raise ValueError("v1.5 internal readiness total contract surfaces must match component counts")
    for count_field, count in gate["contract_surface_counts"].items():
        if gate[count_field] != count:
            raise ValueError(
                f"v1.5 internal readiness surface count mismatch for {count_field}"
            )
    return gate


def v1_5_internal_readiness_decision() -> dict[str, Any]:
    """Return a compact non-public decision summary for the v1.5 gate."""
    gate = validate_v1_5_internal_readiness_gate()
    decision = {
        "decision": "continue_internal_non_public_v1_5_hardening",
        "gate_status": gate["status"],
        "total_contract_surfaces": gate["total_contract_surfaces"],
        "allowed_next_actions": V1_5_INTERNAL_READINESS_ALLOWED_NEXT_ACTIONS,
        "blocked_next_actions": V1_5_INTERNAL_READINESS_BLOCKED_NEXT_ACTIONS,
        "public_claim_preconditions": V1_5_INTERNAL_READINESS_PUBLIC_CLAIM_PRECONDITIONS,
        "public_claims_ready": False,
        "required_external_review_partners": (
            V1_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PARTNERS
        ),
        "accepted_external_review_partners": (
            V1_5_INTERNAL_READINESS_ACCEPTED_EXTERNAL_REVIEW_PARTNERS
        ),
        "missing_external_review_partners": tuple(
            partner
            for partner in V1_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PARTNERS
            if partner not in V1_5_INTERNAL_READINESS_ACCEPTED_EXTERNAL_REVIEW_PARTNERS
        ),
        "external_3_ai_consensus_ready": False,
        "source_usage_mode": V1_5_INTERNAL_READINESS_SOURCE_USAGE_MODE,
        "source_usage_command": V1_5_INTERNAL_READINESS_SOURCE_USAGE_COMMAND,
        "editable_install_claim_authorized": False,
        "package_release_artifact_authorized": False,
        "active_backend_scope": gate["active_backend_scope"],
        "frozen_before_v2_1_backends": gate["frozen_before_v2_1_backends"],
        "new_backend_implementation_authorized": False,
        "pre_v2_1_frozen_backend_work_authorized": False,
        "stable_summary_primitives": gate["stable_summary_primitives"],
        "experimental_primitives": gate["experimental_primitives"],
        "experimental_contract_status_counts": gate["experimental_contract_status_counts"],
        "stable_collect_k_bounded_promotion_authorized": False,
        "current_public_release_tag": V1_5_INTERNAL_READINESS_CURRENT_PUBLIC_RELEASE_TAG,
        "current_public_release_tag_move_authorized": False,
        "new_public_release_tag_authorized": False,
        "scope_kind": V1_5_INTERNAL_READINESS_SCOPE_KIND,
        "excluded_app_scope": V1_5_INTERNAL_READINESS_EXCLUDED_APP_SCOPE,
        "app_level_continuations_authorized_as_generic": False,
        "whole_app_speedup_claim_authorized": False,
        "public_nvidia_speedup_claim_authorized": False,
        "evidence_state": V1_5_INTERNAL_READINESS_EVIDENCE_STATE,
        "required_public_evidence": V1_5_INTERNAL_READINESS_REQUIRED_PUBLIC_EVIDENCE,
        "claim_grade_exact_subpath_evidence_ready": False,
        "same_contract_baseline_ready": False,
        "reviewed_public_wording_packet_ready": False,
        "false_authorization_flags": V1_5_INTERNAL_READINESS_FALSE_AUTHORIZATION_FLAGS,
        "broad_local_suite_state": V1_5_INTERNAL_READINESS_BROAD_LOCAL_SUITE_STATE,
        "broad_local_suite_tests": V1_5_INTERNAL_READINESS_BROAD_LOCAL_SUITE_TESTS,
        "broad_local_suite_skipped": V1_5_INTERNAL_READINESS_BROAD_LOCAL_SUITE_SKIPPED,
        "broad_local_suite_claim_grade_evidence": False,
        "public_release_authorized": gate["public_release_authorized"],
        "public_speedup_wording_authorized": gate["public_speedup_wording_authorized"],
        "release_tag_action_authorized": gate["release_tag_action_authorized"],
        "claim_boundary": gate["claim_boundary"],
    }
    decision["decision_fingerprint_algorithm"] = (
        V1_5_INTERNAL_READINESS_DECISION_FINGERPRINT_ALGORITHM
    )
    decision["decision_fingerprint_fields"] = V1_5_INTERNAL_READINESS_DECISION_FINGERPRINT_FIELDS
    decision["decision_fingerprint"] = _decision_fingerprint(decision)
    return decision


def validate_v1_5_internal_readiness_decision() -> dict[str, Any]:
    decision = v1_5_internal_readiness_decision()
    if decision["decision"] != "continue_internal_non_public_v1_5_hardening":
        raise ValueError("invalid v1.5 internal readiness decision")
    _validate_decision_next_actions(decision)
    _validate_decision_public_claim_preconditions(decision)
    _validate_decision_external_review_state(decision)
    _validate_decision_source_usage(decision)
    _validate_decision_backend_boundary(decision)
    _validate_decision_primitive_boundary(decision)
    _validate_decision_release_and_scope_boundary(decision)
    _validate_decision_evidence_boundary(decision)
    _validate_decision_broad_suite_state(decision)
    _validate_decision_fingerprint_state(decision)
    _validate_decision_claim_boundary(decision)
    return decision


def v1_5_standalone_release_gate() -> dict[str, Any]:
    """Return the expanded v1.5 release gate after Goal1397 consensus.

    This is intentionally separate from the internal primitive readiness gate:
    the primitive packet is prerequisite evidence, while standalone v1.5
    release requires collection, app migration, benchmark, and support-maturity
    gates that are not complete yet.
    """
    internal_decision = validate_v1_5_internal_readiness_decision()
    bounded_collection_contracts = validate_v1_5_collect_k_bounded_contracts()
    bounded_collection_resolution = validate_v1_5_collect_k_bounded_resolution()
    app_classification = validate_v1_5_standalone_app_classification_matrix()
    correctness_summary = validate_v1_5_standalone_correctness_summary()
    collect_k_statuses = tuple(
        sorted({str(contract["status"]) for contract in bounded_collection_contracts})
    )
    gate_results = {
        "primitive_packet_prerequisite": True,
        "roadmap_consensus": True,
        "collect_k_bounded_resolution": bounded_collection_resolution[
            "standalone_v1_5_resolution_complete"
        ],
        "app_migration_classification": True,
        "same_contract_per_app_correctness": correctness_summary["release_gate_complete"],
        "same_contract_per_app_benchmarks": False,
        "test_backed_support_maturity_matrix": False,
        "release_docs_and_public_wording": False,
    }
    return {
        "status": V1_5_STANDALONE_RELEASE_STATUS,
        "scope_kind": V1_5_STANDALONE_RELEASE_SCOPE_KIND,
        "current_public_release_tag": V1_5_INTERNAL_READINESS_CURRENT_PUBLIC_RELEASE_TAG,
        "current_public_release_tag_move_authorized": False,
        "new_public_release_tag_authorized": False,
        "public_release_authorized": False,
        "release_tag_action_authorized": False,
        "public_speedup_wording_authorized": False,
        "primitive_packet_status": internal_decision["gate_status"],
        "primitive_packet_is_prerequisite_only": True,
        "primitive_packet_sufficient_for_release": False,
        "required_gates": V1_5_STANDALONE_RELEASE_REQUIRED_GATES,
        "gate_results": gate_results,
        "passed_gates": tuple(gate for gate, passed in gate_results.items() if passed),
        "failed_gates": tuple(gate for gate, passed in gate_results.items() if not passed),
        "blockers": V1_5_STANDALONE_RELEASE_BLOCKERS,
        "allowed_next_actions": V1_5_STANDALONE_RELEASE_ALLOWED_NEXT_ACTIONS,
        "active_backend_scope": internal_decision["active_backend_scope"],
        "frozen_before_v2_1_backends": internal_decision["frozen_before_v2_1_backends"],
        "source_usage_mode": internal_decision["source_usage_mode"],
        "source_usage_command": internal_decision["source_usage_command"],
        "collect_k_bounded_statuses": collect_k_statuses,
        "collect_k_bounded_resolution_plan_status": bounded_collection_resolution["status"],
        "collect_k_bounded_resolution_strategy": bounded_collection_resolution[
            "resolution_strategy"
        ],
        "collect_k_bounded_resolution_fallback": bounded_collection_resolution[
            "fallback_strategy"
        ],
        "collect_k_bounded_resolution_failed_gates": bounded_collection_resolution[
            "failed_gates"
        ],
        "collect_k_bounded_resolution_complete": bounded_collection_resolution[
            "standalone_v1_5_resolution_complete"
        ],
        "collect_k_bounded_standalone_decision": bounded_collection_resolution[
            "standalone_v1_5_decision"
        ],
        "collect_k_bounded_excluded_row_returning_apps": bounded_collection_resolution[
            "excluded_row_returning_apps"
        ],
        "app_classification_counts": _count_inventory_statuses(
            tuple(
                {"status": row["classification"]}
                for row in app_classification.values()
            )
        ),
        "standalone_included_app_count": sum(
            1 for row in app_classification.values() if row["standalone_included"]
        ),
        "standalone_excluded_app_count": sum(
            1 for row in app_classification.values() if not row["standalone_included"]
        ),
        "same_contract_correctness_status_counts": correctness_summary["status_counts"],
        "same_contract_correctness_covered_app_count": correctness_summary["covered_app_count"],
        "same_contract_correctness_pending_app_count": correctness_summary["pending_app_count"],
        "same_contract_correctness_excluded_app_count": correctness_summary["excluded_app_count"],
        "same_contract_correctness_pending_apps": correctness_summary["pending_apps"],
        "same_contract_correctness_command": correctness_summary["command"],
        "collect_k_bounded_resolution": "resolved_by_explicit_row_returning_app_exclusion",
        "collect_k_bounded_followup_track": V1_5_1_COLLECT_K_BOUNDED_TRACK,
        "partner_track": V1_5_STANDALONE_PARTNER_TRACK,
        "claim_boundary": (
            "standalone v1.5 release is blocked until all standalone gates pass; "
            "do not tag v1.5 from primitive-only readiness; v1.5.1 is the collect-k track; "
            "v1.6-v2.0 are partner-track milestones"
        ),
    }


def validate_v1_5_standalone_release_gate() -> dict[str, Any]:
    gate = v1_5_standalone_release_gate()
    if gate["status"] != V1_5_STANDALONE_RELEASE_STATUS:
        raise ValueError("invalid v1.5 standalone release gate status")
    if gate["scope_kind"] != V1_5_STANDALONE_RELEASE_SCOPE_KIND:
        raise ValueError("v1.5 standalone release gate must use standalone scope")
    if tuple(gate["required_gates"]) != V1_5_STANDALONE_RELEASE_REQUIRED_GATES:
        raise ValueError("v1.5 standalone release gate must preserve required gates")
    gate_results = dict(gate["gate_results"])
    if tuple(gate_results) != V1_5_STANDALONE_RELEASE_REQUIRED_GATES:
        raise ValueError("v1.5 standalone release gate results must match required gates")
    if not gate_results["primitive_packet_prerequisite"]:
        raise ValueError("primitive packet must remain a prerequisite for standalone v1.5")
    if not gate_results["roadmap_consensus"]:
        raise ValueError("Goal1397 roadmap consensus must be represented")
    if gate["primitive_packet_sufficient_for_release"] is not False:
        raise ValueError("primitive-only readiness must not be sufficient for standalone release")
    if tuple(gate["passed_gates"]) != (
        "primitive_packet_prerequisite",
        "roadmap_consensus",
        "collect_k_bounded_resolution",
        "app_migration_classification",
        "same_contract_per_app_correctness",
    ):
        raise ValueError(
            "only prerequisite, roadmap consensus, collect-k, classification, and correctness gates should pass now"
        )
    expected_failed = tuple(
        required
        for required in V1_5_STANDALONE_RELEASE_REQUIRED_GATES
        if required not in gate["passed_gates"]
    )
    if tuple(gate["failed_gates"]) != expected_failed:
        raise ValueError("v1.5 standalone failed gate list mismatch")
    for flag in (
        "current_public_release_tag_move_authorized",
        "new_public_release_tag_authorized",
        "public_release_authorized",
        "release_tag_action_authorized",
        "public_speedup_wording_authorized",
    ):
        if gate[flag] is not False:
            raise ValueError(f"v1.5 standalone release gate must not authorize {flag}")
    if tuple(gate["active_backend_scope"]) != ("embree", "optix"):
        raise ValueError("v1.5 standalone release gate must stay scoped to Embree and OptiX")
    if tuple(gate["frozen_before_v2_1_backends"]) != ("vulkan", "hiprt", "apple_rt"):
        raise ValueError("v1.5 standalone release gate must preserve frozen backends")
    if gate["source_usage_command"] != V1_5_INTERNAL_READINESS_SOURCE_USAGE_COMMAND:
        raise ValueError("v1.5 standalone release gate must preserve source-tree usage")
    if gate["collect_k_bounded_statuses"] != ("experimental_diagnostic_only",):
        raise ValueError("COLLECT_K_BOUNDED must still be represented as unresolved")
    if gate["collect_k_bounded_resolution_plan_status"] != "resolved_by_exclusion_for_standalone_v1_5":
        raise ValueError("COLLECT_K_BOUNDED resolution must be explicit exclusion for v1.5")
    if "exclude_row_returning_apps" not in gate["collect_k_bounded_resolution_strategy"]:
        raise ValueError("COLLECT_K_BOUNDED strategy must exclude row-returning apps")
    if "promote_later" not in gate["collect_k_bounded_resolution_fallback"]:
        raise ValueError("COLLECT_K_BOUNDED fallback must preserve future promotion")
    if not tuple(gate["collect_k_bounded_resolution_failed_gates"]):
        raise ValueError("COLLECT_K_BOUNDED future promotion must still expose failed gates")
    if gate["gate_results"]["collect_k_bounded_resolution"] is not True:
        raise ValueError("COLLECT_K_BOUNDED standalone resolution must pass by exclusion")
    if gate["collect_k_bounded_resolution_complete"] is not True:
        raise ValueError("COLLECT_K_BOUNDED standalone resolution complete flag mismatch")
    if gate["collect_k_bounded_standalone_decision"] != (
        "exclude_row_returning_apps_keep_primitive_experimental"
    ):
        raise ValueError("COLLECT_K_BOUNDED standalone decision mismatch")
    if tuple(gate["collect_k_bounded_excluded_row_returning_apps"]) != (
        "polygon_set_jaccard",
        "segment_polygon_anyhit_rows",
    ):
        raise ValueError("COLLECT_K_BOUNDED excluded row app list mismatch")
    if gate["gate_results"]["app_migration_classification"] is not True:
        raise ValueError("app migration/classification gate must pass after classification matrix")
    if int(gate["standalone_included_app_count"]) <= 0:
        raise ValueError("standalone app classification must include at least one app")
    if int(gate["standalone_excluded_app_count"]) <= 0:
        raise ValueError("standalone app classification must exclude frozen/collection-dependent apps")
    if gate["gate_results"]["same_contract_per_app_correctness"] is not True:
        raise ValueError("same-contract correctness must pass after Goal1402 closure tests")
    if int(gate["same_contract_correctness_covered_app_count"]) != 14:
        raise ValueError("same-contract correctness covered app count mismatch")
    if int(gate["same_contract_correctness_pending_app_count"]) != 0:
        raise ValueError("same-contract correctness pending app count mismatch")
    if int(gate["same_contract_correctness_excluded_app_count"]) != 4:
        raise ValueError("same-contract correctness excluded app count mismatch")
    if tuple(gate["same_contract_correctness_pending_apps"]) != ():
        raise ValueError("same-contract correctness pending apps mismatch")
    for required_classification in (
        "fully_generic",
        "wrapper_backed",
        "scalar_only",
        "collection_dependent",
        "frozen",
        "demo_only",
    ):
        if required_classification not in gate["app_classification_counts"]:
            raise ValueError(f"missing app classification: {required_classification}")
    if "resolved_by_explicit" not in gate["collect_k_bounded_resolution"]:
        raise ValueError("COLLECT_K_BOUNDED resolution must be explicit exclusion")
    if tuple(gate["collect_k_bounded_followup_track"]) != V1_5_1_COLLECT_K_BOUNDED_TRACK:
        raise ValueError("v1.5.1 collect-k follow-up track must be preserved")
    if tuple(gate["partner_track"]) != V1_5_STANDALONE_PARTNER_TRACK:
        raise ValueError("v1.6-v2.0 partner track must be preserved")
    boundary = str(gate["claim_boundary"])
    for required_boundary in (
        "standalone v1.5 release is blocked",
        "do not tag v1.5 from primitive-only readiness",
        "v1.5.1 is the collect-k track",
        "v1.6-v2.0 are partner-track milestones",
    ):
        if required_boundary not in boundary:
            raise ValueError("v1.5 standalone release gate boundary is too broad")
    for blocker in V1_5_STANDALONE_RELEASE_BLOCKERS:
        if blocker not in tuple(gate["blockers"]):
            raise ValueError(f"missing v1.5 standalone blocker: {blocker}")
    return gate
