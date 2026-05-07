from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable


V1_5_1_COLLECT_K_BOUNDED_PRIMITIVE = "COLLECT_K_BOUNDED"
V1_5_1_COLLECT_K_BOUNDED_STATUS = "promotion_candidate_python_rtdl_track"
V1_5_1_COLLECT_K_BOUNDED_RESULT_LAYOUT = "dense_candidate_id_rows_with_valid_count"
V1_5_1_COLLECT_K_BOUNDED_OVERFLOW_POLICY = "fail_closed_before_result_materialization"
V1_5_1_COLLECT_K_BOUNDED_ORDERING_POLICY = "stable_lexicographic_by_candidate_id_row"
V1_5_1_COLLECT_K_BOUNDED_DUPLICATE_POLICY = "deduplicate_before_capacity_check"
V1_5_1_COLLECT_K_BOUNDED_BACKENDS = ("embree", "optix")
V1_5_1_COLLECT_K_BOUNDED_READINESS_REQUIRED_GATES = (
    "contract_foundation",
    "bounds_tests",
    "native_embree_optix_parity",
    "same_contract_benchmarks",
    "external_3_ai_parity_consensus",
    "external_3_ai_benchmark_consensus",
)
V1_5_1_COLLECT_K_BOUNDED_READINESS_EVIDENCE = (
    ("contract_foundation", "docs/reports/v1_5_1_collect_k_bounded_contract_foundation_2026-05-06.md"),
    ("native_embree_optix_parity", "docs/reports/three_ai_goal1416_v1_5_1_collect_k_native_parity_consensus_2026-05-06.md"),
    ("same_contract_benchmarks", "docs/reports/three_ai_goal1417_v1_5_1_collect_k_benchmark_consensus_2026-05-06.md"),
)
V1_5_1_COLLECT_K_BOUNDED_READINESS_BLOCKED_ACTIONS = (
    "public_collect_k_bounded_promotion",
    "public_speedup_wording",
    "zero_copy_wording",
    "release_tag_action",
    "whole_app_speedup_claim",
)
V1_5_1_COLLECT_K_BOUNDED_READINESS_ALLOWED_NEXT_ACTIONS = (
    "prepare_v1_5_1_release_surface_proposal",
    "request_explicit_release_gate_review",
    "continue_python_rtdl_track_hardening",
)
V1_5_1_COLLECT_K_BOUNDED_RELEASE_SURFACE_PROPOSAL_STATUS = (
    "proposal_ready_for_external_release_surface_review"
)
V1_5_1_COLLECT_K_BOUNDED_RELEASE_SURFACE_PROPOSED_CLASSIFICATION = (
    "documented_experimental_public_candidate"
)
V1_5_1_COLLECT_K_BOUNDED_RELEASE_SURFACE_REQUIRED_REVIEW = "3-AI release-surface review"
V1_5_1_COLLECT_K_BOUNDED_RELEASE_SURFACE_FORBIDDEN_WORDING = (
    "stable primitive",
    "public speedup",
    "zero-copy",
    "whole-app speedup",
    "release tag action",
)
V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_STATUS = (
    "candidate_docs_publicly_discoverable_pending_explicit_release_action"
)
V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_REQUIRED_DOCS = (
    "docs/release_reports/v1_5_1/README.md",
    "docs/release_reports/v1_5_1/collect_k_bounded.md",
    "docs/release_reports/v1_5_1/release_surface_gate.md",
)
V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_REQUIRED_PHRASES = (
    "documented experimental public-candidate",
    "COLLECT_K_BOUNDED",
    "Python+RTDL",
    "Embree and OptiX",
    "fail-closed",
    "candidate-id rows",
    "not stable primitive promotion",
    "no public speedup wording",
    "no zero-copy wording",
    "no whole-app claims",
    "no release tag action",
    "PYTHONPATH=src:. python",
)
V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_FORBIDDEN_PHRASES = (
    "COLLECT_K_BOUNDED is stable",
    "stable COLLECT_K_BOUNDED primitive",
    "public speedup is authorized",
    "zero-copy is authorized",
    "whole-app speedup is authorized",
    "pip install -e .",
    "release tag action is authorized",
)
V1_5_1_COLLECT_K_BOUNDED_NATIVE_APP_GENERIC_AUDIT_STATUS = (
    "blocked_for_stable_promotion_native_abi_still_polygon_pair_specific"
)
V1_5_1_COLLECT_K_BOUNDED_NATIVE_APP_GENERIC_AUDIT_SYMBOLS = (
    (
        "embree",
        "src/native/embree/rtdl_embree_api.cpp",
        "rtdl_embree_collect_polygon_pair_candidates_bounded",
    ),
    (
        "optix",
        "src/native/optix/rtdl_optix_api.cpp",
        "rtdl_optix_collect_polygon_pair_candidates_bounded",
    ),
)
V1_5_1_COLLECT_K_BOUNDED_NATIVE_APP_GENERIC_REQUIRED_NEXT_STEPS = (
    "add_embree_optix_generic_abi_parity_tests",
    "validate_generic_native_symbols_in_built_libraries",
    "rerun_3_ai_stable_promotion_review",
)
V1_5_1_COLLECT_K_BOUNDED_NATIVE_GENERIC_ABI_STATUS = (
    "source_symbols_present_python_adapter_routed_embree_optix_adapter_parity_ok_binary_validation_pending"
)
V1_5_1_COLLECT_K_BOUNDED_NATIVE_GENERIC_ABI_SYMBOLS = (
    "rtdl_embree_collect_k_bounded_i64",
    "rtdl_optix_collect_k_bounded_i64",
)
V1_5_1_COLLECT_K_BOUNDED_NATIVE_GENERIC_ABI_PROTOTYPE = (
    "int {symbol}(const int64_t* candidate_rows, size_t candidate_count, "
    "size_t row_width, int64_t* rows_out, size_t row_capacity, "
    "size_t* emitted_count_out, uint32_t* overflowed_out, "
    "char* error_out, size_t error_size)"
)


def v1_5_1_collect_k_bounded_contract() -> dict[str, Any]:
    """Return the app-generic v1.5.1 bounded collection promotion contract."""
    return {
        "primitive": V1_5_1_COLLECT_K_BOUNDED_PRIMITIVE,
        "status": V1_5_1_COLLECT_K_BOUNDED_STATUS,
        "track": "python_rtdl",
        "app_generic": True,
        "stable_promotion_authorized": False,
        "active_backend_scope": V1_5_1_COLLECT_K_BOUNDED_BACKENDS,
        "result_layout": V1_5_1_COLLECT_K_BOUNDED_RESULT_LAYOUT,
        "row_dtype": "int64",
        "capacity_parameter": "k",
        "capacity_unit": "candidate_id_rows",
        "valid_count_field": "valid_count",
        "overflow_field": "overflowed",
        "ordering_policy": V1_5_1_COLLECT_K_BOUNDED_ORDERING_POLICY,
        "duplicate_policy": V1_5_1_COLLECT_K_BOUNDED_DUPLICATE_POLICY,
        "overflow_policy": V1_5_1_COLLECT_K_BOUNDED_OVERFLOW_POLICY,
        "failure_mode": "fail_closed_overflow",
        "truncation_allowed": False,
        "partial_result_on_overflow_allowed": False,
        "score_or_reduction_after_overflow_allowed": False,
        "complete_candidate_coverage_required": True,
        "bounds_tests_required": (
            "k_zero_with_zero_results",
            "k_zero_overflow_with_positive_results",
            "exact_k_full_buffer",
            "k_plus_one_overflow",
            "deterministic_ordering",
            "duplicate_rows_deduplicated_before_capacity_check",
            "row_width_mismatch_rejected",
            "negative_k_rejected",
        ),
        "claim_boundary": (
            "v1.5.1 app-generic COLLECT_K_BOUNDED promotion candidate contract only; "
            "not yet public promotion, not a Jaccard-specific or polygon-specific engine path, "
            "and not a performance or zero-copy claim."
        ),
    }


def validate_v1_5_1_collect_k_bounded_contract() -> dict[str, Any]:
    contract = v1_5_1_collect_k_bounded_contract()
    required = (
        "primitive",
        "status",
        "track",
        "app_generic",
        "stable_promotion_authorized",
        "active_backend_scope",
        "result_layout",
        "row_dtype",
        "capacity_parameter",
        "capacity_unit",
        "valid_count_field",
        "overflow_field",
        "ordering_policy",
        "duplicate_policy",
        "overflow_policy",
        "failure_mode",
        "truncation_allowed",
        "partial_result_on_overflow_allowed",
        "score_or_reduction_after_overflow_allowed",
        "complete_candidate_coverage_required",
        "bounds_tests_required",
        "claim_boundary",
    )
    for field in required:
        if field not in contract:
            raise ValueError(f"missing v1.5.1 collect-k contract field: {field}")
        if field not in {
            "stable_promotion_authorized",
            "truncation_allowed",
            "partial_result_on_overflow_allowed",
            "score_or_reduction_after_overflow_allowed",
        } and not contract[field]:
            raise ValueError(f"empty v1.5.1 collect-k contract field: {field}")
    if contract["primitive"] != V1_5_1_COLLECT_K_BOUNDED_PRIMITIVE:
        raise ValueError("v1.5.1 collect-k contract must target COLLECT_K_BOUNDED")
    if contract["app_generic"] is not True:
        raise ValueError("v1.5.1 collect-k contract must be app-generic")
    if contract["stable_promotion_authorized"] is not False:
        raise ValueError("v1.5.1 collect-k contract is a candidate, not final promotion")
    if tuple(contract["active_backend_scope"]) != V1_5_1_COLLECT_K_BOUNDED_BACKENDS:
        raise ValueError("v1.5.1 collect-k backend scope must remain Embree+OptiX")
    for false_flag in (
        "truncation_allowed",
        "partial_result_on_overflow_allowed",
        "score_or_reduction_after_overflow_allowed",
    ):
        if contract[false_flag] is not False:
            raise ValueError(f"v1.5.1 collect-k must keep {false_flag}=False")
    if contract["complete_candidate_coverage_required"] is not True:
        raise ValueError("v1.5.1 collect-k must require complete candidate coverage")
    required_bounds = {
        "k_zero_with_zero_results",
        "k_zero_overflow_with_positive_results",
        "exact_k_full_buffer",
        "k_plus_one_overflow",
        "deterministic_ordering",
        "duplicate_rows_deduplicated_before_capacity_check",
        "row_width_mismatch_rejected",
        "negative_k_rejected",
    }
    if set(contract["bounds_tests_required"]) != required_bounds:
        raise ValueError("v1.5.1 collect-k bounds test set mismatch")
    boundary = str(contract["claim_boundary"])
    for phrase in (
        "app-generic",
        "not yet public promotion",
        "not a Jaccard-specific",
        "not a performance or zero-copy claim",
    ):
        if phrase not in boundary:
            raise ValueError("v1.5.1 collect-k claim boundary is too broad")
    return contract


def v1_5_1_collect_k_bounded_readiness_gate() -> dict[str, Any]:
    """Return the current v1.5.1 readiness gate for bounded collection.

    This gate records that parity and benchmark evidence is now accepted for the
    measured package, while intentionally keeping all public promotion and claim
    flags closed until a separate release-surface decision authorizes them.
    """
    contract = validate_v1_5_1_collect_k_bounded_contract()
    gate_results = {
        "contract_foundation": True,
        "bounds_tests": True,
        "native_embree_optix_parity": True,
        "same_contract_benchmarks": True,
        "external_3_ai_parity_consensus": True,
        "external_3_ai_benchmark_consensus": True,
    }
    passed_gates = tuple(
        gate for gate in V1_5_1_COLLECT_K_BOUNDED_READINESS_REQUIRED_GATES if gate_results[gate]
    )
    failed_gates = tuple(
        gate for gate in V1_5_1_COLLECT_K_BOUNDED_READINESS_REQUIRED_GATES if not gate_results[gate]
    )
    evidence_files = dict(V1_5_1_COLLECT_K_BOUNDED_READINESS_EVIDENCE)
    return {
        "status": "promotion_track_evidence_ready_pending_release_surface_decision",
        "primitive": contract["primitive"],
        "track": contract["track"],
        "app_generic": contract["app_generic"],
        "backend_scope": contract["active_backend_scope"],
        "required_gates": V1_5_1_COLLECT_K_BOUNDED_READINESS_REQUIRED_GATES,
        "gate_results": gate_results,
        "passed_gates": passed_gates,
        "failed_gates": failed_gates,
        "evidence_files": V1_5_1_COLLECT_K_BOUNDED_READINESS_EVIDENCE,
        "contract_foundation_evidence": evidence_files["contract_foundation"],
        "parity_consensus_evidence": evidence_files["native_embree_optix_parity"],
        "benchmark_consensus_evidence": evidence_files["same_contract_benchmarks"],
        "external_review_partners": ("claude", "gemini"),
        "external_3_ai_consensus_ready": True,
        "parity_scope": (
            "Windows Embree optional run",
            "Linux Embree required-backend run",
            "NVIDIA pod OptiX required-backend run",
        ),
        "benchmark_scope": (
            "Windows Embree plus Python reference",
            "Linux Embree required-backend timing",
            "NVIDIA pod OptiX required-backend timing",
        ),
        "stable_promotion_authorized": False,
        "public_wording_authorized": False,
        "public_speedup_wording_authorized": False,
        "zero_copy_wording_authorized": False,
        "release_tag_action_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "blocked_actions": V1_5_1_COLLECT_K_BOUNDED_READINESS_BLOCKED_ACTIONS,
        "allowed_next_actions": V1_5_1_COLLECT_K_BOUNDED_READINESS_ALLOWED_NEXT_ACTIONS,
        "remaining_release_surface_decisions": (
            "decide whether v1.5.1 exposes COLLECT_K_BOUNDED as public stable or documented experimental",
            "write user-facing docs only after explicit release-gate approval",
            "keep speedup and zero-copy wording blocked unless separately reviewed",
        ),
        "claim_boundary": (
            "v1.5.1 COLLECT_K_BOUNDED evidence gates are satisfied for the measured "
            "Python+RTDL Embree/OptiX package; this does not authorize public primitive "
            "promotion, speedup wording, zero-copy wording, release tag action, or whole-app claims."
        ),
    }


def validate_v1_5_1_collect_k_bounded_readiness_gate() -> dict[str, Any]:
    gate = v1_5_1_collect_k_bounded_readiness_gate()
    required_fields = (
        "status",
        "primitive",
        "track",
        "app_generic",
        "backend_scope",
        "required_gates",
        "gate_results",
        "passed_gates",
        "failed_gates",
        "evidence_files",
        "external_review_partners",
        "external_3_ai_consensus_ready",
        "stable_promotion_authorized",
        "public_wording_authorized",
        "public_speedup_wording_authorized",
        "zero_copy_wording_authorized",
        "release_tag_action_authorized",
        "whole_app_speedup_claim_authorized",
        "blocked_actions",
        "allowed_next_actions",
        "remaining_release_surface_decisions",
        "claim_boundary",
    )
    for field in required_fields:
        if field not in gate:
            raise ValueError(f"missing v1.5.1 collect-k readiness field: {field}")
    if gate["primitive"] != V1_5_1_COLLECT_K_BOUNDED_PRIMITIVE:
        raise ValueError("readiness gate must target COLLECT_K_BOUNDED")
    if tuple(gate["backend_scope"]) != V1_5_1_COLLECT_K_BOUNDED_BACKENDS:
        raise ValueError("readiness backend scope must remain Embree+OptiX")
    if tuple(gate["required_gates"]) != V1_5_1_COLLECT_K_BOUNDED_READINESS_REQUIRED_GATES:
        raise ValueError("readiness required gate set mismatch")
    if tuple(gate["passed_gates"]) != V1_5_1_COLLECT_K_BOUNDED_READINESS_REQUIRED_GATES:
        raise ValueError("all measured v1.5.1 collect-k evidence gates must pass")
    if tuple(gate["failed_gates"]) != ():
        raise ValueError("v1.5.1 collect-k readiness gate must have no failed evidence gates")
    if gate["external_review_partners"] != ("claude", "gemini"):
        raise ValueError("v1.5.1 collect-k readiness requires Claude and Gemini reviews")
    if gate["external_3_ai_consensus_ready"] is not True:
        raise ValueError("v1.5.1 collect-k readiness requires 3-AI consensus")
    false_flags = (
        "stable_promotion_authorized",
        "public_wording_authorized",
        "public_speedup_wording_authorized",
        "zero_copy_wording_authorized",
        "release_tag_action_authorized",
        "whole_app_speedup_claim_authorized",
    )
    for flag in false_flags:
        if gate[flag] is not False:
            raise ValueError(f"v1.5.1 collect-k readiness must keep {flag}=False")
    boundary = str(gate["claim_boundary"])
    for phrase in (
        "evidence gates are satisfied",
        "does not authorize public primitive promotion",
        "speedup wording",
        "zero-copy wording",
        "whole-app claims",
    ):
        if phrase not in boundary:
            raise ValueError("v1.5.1 collect-k readiness claim boundary is incomplete")
    return gate


def v1_5_1_collect_k_bounded_release_surface_proposal() -> dict[str, Any]:
    """Return the proposed v1.5.1 release surface for bounded collection.

    The proposal is intentionally not an authorization. It recommends a cautious
    documented experimental surface after the readiness gate, while keeping
    stable promotion and public claims closed until release-surface review.
    """
    readiness = validate_v1_5_1_collect_k_bounded_readiness_gate()
    return {
        "status": V1_5_1_COLLECT_K_BOUNDED_RELEASE_SURFACE_PROPOSAL_STATUS,
        "primitive": readiness["primitive"],
        "track": readiness["track"],
        "proposed_classification": V1_5_1_COLLECT_K_BOUNDED_RELEASE_SURFACE_PROPOSED_CLASSIFICATION,
        "proposed_public_surface": (
            "document COLLECT_K_BOUNDED as a v1.5.1 experimental Python+RTDL candidate "
            "for bounded candidate-id row collection over Embree and OptiX"
        ),
        "not_proposed": (
            "stable primitive promotion",
            "whole-app speedup wording",
            "public speedup wording",
            "zero-copy wording",
            "release tag action",
            "new backend expansion",
        ),
        "evidence_ready": readiness["failed_gates"] == (),
        "readiness_status": readiness["status"],
        "readiness_consensus": (
            "docs/reports/three_ai_goal1418_v1_5_1_collect_k_readiness_gate_consensus_2026-05-06.md"
        ),
        "parity_consensus": readiness["parity_consensus_evidence"],
        "benchmark_consensus": readiness["benchmark_consensus_evidence"],
        "required_review": V1_5_1_COLLECT_K_BOUNDED_RELEASE_SURFACE_REQUIRED_REVIEW,
        "required_review_partners": ("claude", "gemini"),
        "public_docs_change_authorized_by_this_proposal": False,
        "stable_promotion_authorized_by_this_proposal": False,
        "public_speedup_wording_authorized_by_this_proposal": False,
        "zero_copy_wording_authorized_by_this_proposal": False,
        "release_tag_action_authorized_by_this_proposal": False,
        "allowed_next_actions": (
            "request_external_release_surface_review",
            "draft_user_docs_after_release_surface_review_accepts",
            "keep_v1_5_public_docs_unchanged_until_authorized",
        ),
        "forbidden_wording": V1_5_1_COLLECT_K_BOUNDED_RELEASE_SURFACE_FORBIDDEN_WORDING,
        "claim_boundary": (
            "This is a v1.5.1 release-surface proposal only: evidence-ready "
            "COLLECT_K_BOUNDED may be considered for documented experimental public-candidate "
            "status after 3-AI release-surface review, but this proposal itself does not "
            "authorize public docs changes, stable promotion, speedup wording, zero-copy wording, "
            "release tag action, or whole-app claims."
        ),
    }


def validate_v1_5_1_collect_k_bounded_release_surface_proposal() -> dict[str, Any]:
    proposal = v1_5_1_collect_k_bounded_release_surface_proposal()
    if proposal["status"] != V1_5_1_COLLECT_K_BOUNDED_RELEASE_SURFACE_PROPOSAL_STATUS:
        raise ValueError("invalid v1.5.1 collect-k release-surface proposal status")
    if proposal["primitive"] != V1_5_1_COLLECT_K_BOUNDED_PRIMITIVE:
        raise ValueError("release-surface proposal must target COLLECT_K_BOUNDED")
    if proposal["proposed_classification"] != V1_5_1_COLLECT_K_BOUNDED_RELEASE_SURFACE_PROPOSED_CLASSIFICATION:
        raise ValueError("release-surface proposal classification mismatch")
    if proposal["evidence_ready"] is not True:
        raise ValueError("release-surface proposal requires readiness evidence")
    if proposal["required_review"] != V1_5_1_COLLECT_K_BOUNDED_RELEASE_SURFACE_REQUIRED_REVIEW:
        raise ValueError("release-surface proposal must require 3-AI review")
    if proposal["required_review_partners"] != ("claude", "gemini"):
        raise ValueError("release-surface proposal must require Claude and Gemini")
    false_flags = (
        "public_docs_change_authorized_by_this_proposal",
        "stable_promotion_authorized_by_this_proposal",
        "public_speedup_wording_authorized_by_this_proposal",
        "zero_copy_wording_authorized_by_this_proposal",
        "release_tag_action_authorized_by_this_proposal",
    )
    for flag in false_flags:
        if proposal[flag] is not False:
            raise ValueError(f"release-surface proposal must keep {flag}=False")
    for forbidden in V1_5_1_COLLECT_K_BOUNDED_RELEASE_SURFACE_FORBIDDEN_WORDING:
        if forbidden not in proposal["forbidden_wording"]:
            raise ValueError(f"missing forbidden wording: {forbidden}")
    boundary = str(proposal["claim_boundary"])
    for phrase in (
        "proposal only",
        "documented experimental public-candidate",
        "does not authorize public docs changes",
        "stable promotion",
        "speedup wording",
        "zero-copy wording",
        "release tag action",
        "whole-app claims",
    ):
        if phrase not in boundary:
            raise ValueError("release-surface proposal claim boundary is incomplete")
    return proposal


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_release_gate_doc(relative_path: str) -> str:
    path = _repo_root() / relative_path
    if not path.exists():
        raise ValueError(f"missing v1.5.1 collect-k release-surface doc: {relative_path}")
    return path.read_text(encoding="utf-8")


def v1_5_1_collect_k_bounded_release_surface_gate() -> dict[str, Any]:
    """Return the v1.5.1 release-surface doc gate for bounded collection."""
    proposal = validate_v1_5_1_collect_k_bounded_release_surface_proposal()
    docs = {
        relative_path: _read_release_gate_doc(relative_path)
        for relative_path in V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_REQUIRED_DOCS
    }
    combined = "\n".join(docs.values())
    missing_required_phrases = tuple(
        phrase
        for phrase in V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_REQUIRED_PHRASES
        if phrase not in combined
    )
    present_forbidden_phrases = tuple(
        phrase
        for phrase in V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_FORBIDDEN_PHRASES
        if phrase in combined
    )
    return {
        "status": V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_STATUS,
        "primitive": proposal["primitive"],
        "classification": proposal["proposed_classification"],
        "required_docs": V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_REQUIRED_DOCS,
        "required_phrases": V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_REQUIRED_PHRASES,
        "forbidden_phrases": V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_FORBIDDEN_PHRASES,
        "missing_required_phrases": missing_required_phrases,
        "present_forbidden_phrases": present_forbidden_phrases,
        "release_surface_docs_ready": not missing_required_phrases and not present_forbidden_phrases,
        "proposal_consensus": (
            "docs/reports/three_ai_goal1419_v1_5_1_collect_k_release_surface_proposal_consensus_2026-05-06.md"
        ),
        "release_surface_gate_consensus": (
            "docs/reports/three_ai_goal1420_v1_5_1_collect_k_release_surface_gate_consensus_2026-05-06.md"
        ),
        "public_doc_link_consensus": (
            "docs/reports/three_ai_goal1421_v1_5_1_collect_k_public_doc_link_consensus_2026-05-06.md"
        ),
        "readiness_consensus": proposal["readiness_consensus"],
        "public_docs_change_authorized_by_this_gate": False,
        "stable_promotion_authorized_by_this_gate": False,
        "public_speedup_wording_authorized_by_this_gate": False,
        "zero_copy_wording_authorized_by_this_gate": False,
        "whole_app_speedup_claim_authorized_by_this_gate": False,
        "release_tag_action_authorized_by_this_gate": False,
        "explicit_release_approval_required": True,
        "allowed_next_actions": (
            "keep_candidate_docs_discoverable_without_broader_claims",
            "continue_python_rtdl_track_hardening",
            "request_explicit_v1_5_1_release_action_if_user_wants_release",
        ),
        "claim_boundary": (
            "The v1.5.1 COLLECT_K_BOUNDED candidate docs are publicly discoverable "
            "as documented experimental public-candidate material only after "
            "Goal1421 3-AI public-doc-link consensus. This gate does not authorize "
            "public docs changes beyond that discoverability link, stable promotion, "
            "speedup wording, zero-copy wording, whole-app claims, or release tag action."
        ),
    }


def validate_v1_5_1_collect_k_bounded_release_surface_gate() -> dict[str, Any]:
    gate = v1_5_1_collect_k_bounded_release_surface_gate()
    if gate["status"] != V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_STATUS:
        raise ValueError("invalid v1.5.1 collect-k release-surface gate status")
    if gate["classification"] != V1_5_1_COLLECT_K_BOUNDED_RELEASE_SURFACE_PROPOSED_CLASSIFICATION:
        raise ValueError("v1.5.1 collect-k release-surface gate classification mismatch")
    if tuple(gate["required_docs"]) != V1_5_1_COLLECT_K_BOUNDED_RELEASE_GATE_REQUIRED_DOCS:
        raise ValueError("v1.5.1 collect-k release-surface required docs mismatch")
    if tuple(gate["missing_required_phrases"]) != ():
        raise ValueError(
            "v1.5.1 collect-k release-surface docs are missing required phrases: "
            + ", ".join(gate["missing_required_phrases"])
        )
    if tuple(gate["present_forbidden_phrases"]) != ():
        raise ValueError(
            "v1.5.1 collect-k release-surface docs contain forbidden phrases: "
            + ", ".join(gate["present_forbidden_phrases"])
        )
    if gate["release_surface_docs_ready"] is not True:
        raise ValueError("v1.5.1 collect-k release-surface docs must be ready")
    false_flags = (
        "public_docs_change_authorized_by_this_gate",
        "stable_promotion_authorized_by_this_gate",
        "public_speedup_wording_authorized_by_this_gate",
        "zero_copy_wording_authorized_by_this_gate",
        "whole_app_speedup_claim_authorized_by_this_gate",
        "release_tag_action_authorized_by_this_gate",
    )
    for flag in false_flags:
        if gate[flag] is not False:
            raise ValueError(f"release-surface gate must keep {flag}=False")
    if gate["explicit_release_approval_required"] is not True:
        raise ValueError("v1.5.1 collect-k release-surface gate requires explicit release approval")
    boundary = str(gate["claim_boundary"])
    for phrase in (
        "candidate docs are publicly discoverable",
        "documented experimental public-candidate",
        "does not authorize public docs changes",
        "Goal1421 3-AI public-doc-link consensus",
        "stable promotion",
        "speedup wording",
        "zero-copy wording",
        "whole-app claims",
        "release tag action",
    ):
        if phrase not in boundary:
            raise ValueError("v1.5.1 collect-k release-surface gate claim boundary is incomplete")
    return gate


def v1_5_1_collect_k_bounded_native_app_generic_audit() -> dict[str, Any]:
    """Return the native app-genericity audit for stable-promotion readiness."""
    observed_symbols = []
    missing_symbols = []
    for backend, relative_path, symbol in V1_5_1_COLLECT_K_BOUNDED_NATIVE_APP_GENERIC_AUDIT_SYMBOLS:
        path = _repo_root() / relative_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        record = {
            "backend": backend,
            "path": relative_path,
            "symbol": symbol,
            "path_exists": path.exists(),
            "symbol_present": symbol in text,
            "app_specific_reason": "polygon_pair_specific_native_entrypoint",
        }
        observed_symbols.append(record)
        if not record["path_exists"] or not record["symbol_present"]:
            missing_symbols.append(record)

    return {
        "primitive": V1_5_1_COLLECT_K_BOUNDED_PRIMITIVE,
        "status": V1_5_1_COLLECT_K_BOUNDED_NATIVE_APP_GENERIC_AUDIT_STATUS,
        "contract_layer_app_generic": True,
        "python_reference_app_generic": True,
        "result_validator_app_generic": True,
        "native_engine_fully_app_agnostic": False,
        "stable_promotion_blocked": True,
        "public_docs_candidate_status_remains": "documented_experimental_public_candidate",
        "observed_native_symbols": tuple(observed_symbols),
        "missing_expected_symbols": tuple(missing_symbols),
        "required_next_steps": V1_5_1_COLLECT_K_BOUNDED_NATIVE_APP_GENERIC_REQUIRED_NEXT_STEPS,
        "claim_boundary": (
            "COLLECT_K_BOUNDED is app-generic at the contract, Python reference, "
            "and result-validation layers, but the current Embree/OptiX native "
            "collection entrypoints are still polygon-pair-specific. Stable "
            "primitive promotion is blocked until an app-name-free native "
            "COLLECT_K_BOUNDED ABI and parity tests exist."
        ),
    }


def validate_v1_5_1_collect_k_bounded_native_app_generic_audit() -> dict[str, Any]:
    audit = v1_5_1_collect_k_bounded_native_app_generic_audit()
    if audit["status"] != V1_5_1_COLLECT_K_BOUNDED_NATIVE_APP_GENERIC_AUDIT_STATUS:
        raise ValueError("invalid v1.5.1 collect-k native app-generic audit status")
    for flag in (
        "contract_layer_app_generic",
        "python_reference_app_generic",
        "result_validator_app_generic",
    ):
        if audit[flag] is not True:
            raise ValueError(f"collect-k audit expected {flag}=True")
    if audit["native_engine_fully_app_agnostic"] is not False:
        raise ValueError("collect-k native engine must not be marked fully app-agnostic yet")
    if audit["stable_promotion_blocked"] is not True:
        raise ValueError("collect-k stable promotion must remain blocked by native ABI audit")
    if tuple(audit["missing_expected_symbols"]) != ():
        raise ValueError("collect-k native app-generic audit lost expected native evidence")
    boundary = str(audit["claim_boundary"])
    for phrase in (
        "app-generic at the contract",
        "polygon-pair-specific",
        "Stable primitive promotion is blocked",
        "app-name-free native COLLECT_K_BOUNDED ABI",
    ):
        if phrase not in boundary:
            raise ValueError("collect-k native app-generic audit claim boundary is incomplete")
    return audit


def v1_5_1_collect_k_bounded_native_generic_abi_contract() -> dict[str, Any]:
    """Return the app-name-free native ABI contract needed for stable promotion."""
    prototypes = tuple(
        V1_5_1_COLLECT_K_BOUNDED_NATIVE_GENERIC_ABI_PROTOTYPE.format(symbol=symbol)
        for symbol in V1_5_1_COLLECT_K_BOUNDED_NATIVE_GENERIC_ABI_SYMBOLS
    )
    return {
        "primitive": V1_5_1_COLLECT_K_BOUNDED_PRIMITIVE,
        "status": V1_5_1_COLLECT_K_BOUNDED_NATIVE_GENERIC_ABI_STATUS,
        "native_source_symbols_present": True,
        "native_binary_validation_present": False,
        "stable_promotion_authorized": False,
        "backend_symbols": V1_5_1_COLLECT_K_BOUNDED_NATIVE_GENERIC_ABI_SYMBOLS,
        "prototype_template": V1_5_1_COLLECT_K_BOUNDED_NATIVE_GENERIC_ABI_PROTOTYPE,
        "prototypes": prototypes,
        "input_layout": "row_major_int64_candidate_id_rows",
        "output_layout": V1_5_1_COLLECT_K_BOUNDED_RESULT_LAYOUT,
        "row_width_parameter": "row_width",
        "capacity_parameter": "row_capacity",
        "capacity_unit": "candidate_id_rows",
        "ordering_policy": V1_5_1_COLLECT_K_BOUNDED_ORDERING_POLICY,
        "duplicate_policy": V1_5_1_COLLECT_K_BOUNDED_DUPLICATE_POLICY,
        "overflow_policy": V1_5_1_COLLECT_K_BOUNDED_OVERFLOW_POLICY,
        "failure_mode": "fail_closed_overflow",
        "partial_result_on_overflow_allowed": False,
        "app_name_free": True,
        "forbidden_symbol_substrings": ("polygon", "jaccard", "segment", "graph", "app"),
        "required_adapter_work": (
            "add_embree_optix_generic_abi_parity_tests",
            "validate_embree_optix_generic_i64_symbols_in_built_libraries",
        ),
        "post_adapter_parity_evidence": {
            "windows_optional": (
                "docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_windows_optional_2026-05-06.md"
            ),
            "linux_embree_required": (
                "docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_linux_embree_2026-05-06.md"
            ),
            "linux_optix_required_not_accepted_superseded": (
                "docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_linux_optix_2026-05-06.md"
            ),
            "pod_optix_required": (
                "docs/reports/goal1429_v1_5_1_collect_k_adapter_parity_pod_optix_required_2026-05-06.md"
            ),
            "summary": (
                "docs/reports/goal1429_v1_5_1_collect_k_adapter_parity_optix_closure_2026-05-06.md"
            ),
        },
        "claim_boundary": (
            "This is a native source-level ABI implementation step only. It defines "
            "the app-name-free COLLECT_K_BOUNDED row collector shape and source "
            "symbols required before stable promotion, but it does not claim built "
            "Embree or OptiX library validation. Existing polygon-pair collection "
            "is routed through the Python generic i64 adapter. Post-adapter Embree "
            "and OptiX polygon-pair parity are accepted for the recorded Windows, "
            "Linux, and RTX A5000 pod evidence, but the route is not through "
            "validated built native generic symbols yet. "
            "This does not authorize "
            "speedup, zero-copy, whole-app, release-tag, or stable primitive wording."
        ),
    }


def validate_v1_5_1_collect_k_bounded_native_generic_abi_contract() -> dict[str, Any]:
    contract = v1_5_1_collect_k_bounded_native_generic_abi_contract()
    if contract["status"] != V1_5_1_COLLECT_K_BOUNDED_NATIVE_GENERIC_ABI_STATUS:
        raise ValueError("invalid collect-k native generic ABI contract status")
    if contract["native_source_symbols_present"] is not True:
        raise ValueError("generic collect-k native ABI source symbols must be present")
    if contract["native_binary_validation_present"] is not False:
        raise ValueError("generic collect-k native ABI binary validation must remain pending")
    if contract["stable_promotion_authorized"] is not False:
        raise ValueError("generic collect-k native ABI contract must not authorize stable promotion")
    if contract["app_name_free"] is not True:
        raise ValueError("generic collect-k native ABI contract must be app-name-free")
    for symbol in contract["backend_symbols"]:
        lowered = str(symbol).lower()
        for forbidden in contract["forbidden_symbol_substrings"]:
            if forbidden in lowered:
                raise ValueError(f"generic collect-k native ABI symbol is app-specific: {symbol}")
    for prototype in contract["prototypes"]:
        for required in (
            "const int64_t* candidate_rows",
            "size_t candidate_count",
            "size_t row_width",
            "int64_t* rows_out",
            "size_t row_capacity",
            "size_t* emitted_count_out",
            "uint32_t* overflowed_out",
            "char* error_out",
            "size_t error_size",
        ):
            if required not in prototype:
                raise ValueError("generic collect-k native ABI prototype is incomplete")
    boundary = str(contract["claim_boundary"])
    for phrase in (
        "native source-level ABI implementation step only",
        "app-name-free COLLECT_K_BOUNDED row collector",
        "source symbols required before stable promotion",
        "does not claim built Embree or OptiX library validation",
        "Python generic i64 adapter",
        "Post-adapter Embree and OptiX polygon-pair parity are accepted",
        "not through validated built native generic symbols yet",
        "does not authorize speedup",
        "stable primitive wording",
    ):
        if phrase not in boundary:
            raise ValueError("generic collect-k native ABI claim boundary is incomplete")
    return contract


def _normalize_candidate_rows(
    candidate_rows: Iterable[Any],
    *,
    row_width: int,
) -> tuple[tuple[int, ...], ...]:
    if row_width <= 0:
        raise ValueError("COLLECT_K_BOUNDED row_width must be positive")
    normalized: set[tuple[int, ...]] = set()
    for row in candidate_rows:
        if isinstance(row, int):
            values = (row,)
        else:
            values = tuple(row)
        if len(values) != row_width:
            raise ValueError(
                "COLLECT_K_BOUNDED candidate row width mismatch: "
                f"expected {row_width}, got {len(values)}"
            )
        normalized.add(tuple(int(value) for value in values))
    return tuple(sorted(normalized))


def collect_k_bounded_rows(
    candidate_rows: Iterable[Any],
    *,
    k: int,
    row_width: int = 1,
) -> dict[str, Any]:
    """Materialize an app-generic bounded candidate-id row buffer.

    Overflow fails before returning partial rows. This function is the Python
    reference shape that v1.5.1 native Embree/OptiX collection paths must match.
    """
    capacity = int(k)
    if capacity < 0:
        raise ValueError("COLLECT_K_BOUNDED capacity k must be non-negative")
    contract = validate_v1_5_1_collect_k_bounded_contract()
    rows = _normalize_candidate_rows(candidate_rows, row_width=int(row_width))
    emitted_count = len(rows)
    if emitted_count > capacity:
        raise RuntimeError(
            "COLLECT_K_BOUNDED overflowed capacity "
            f"{capacity}; emitted {emitted_count}; "
            f"failure_mode={contract['failure_mode']}; partial_result_returned=False"
        )
    return {
        "primitive": contract["primitive"],
        "status": contract["status"],
        "app_generic": True,
        "result_layout": contract["result_layout"],
        "row_dtype": contract["row_dtype"],
        "row_width": int(row_width),
        "capacity": capacity,
        "valid_count": emitted_count,
        "emitted_count": emitted_count,
        "overflowed": False,
        "complete_candidate_coverage": True,
        "ordering_policy": contract["ordering_policy"],
        "duplicate_policy": contract["duplicate_policy"],
        "overflow_policy": contract["overflow_policy"],
        "failure_mode": contract["failure_mode"],
        "truncation_allowed": contract["truncation_allowed"],
        "partial_result_on_overflow_allowed": contract[
            "partial_result_on_overflow_allowed"
        ],
        "score_or_reduction_after_overflow_allowed": contract[
            "score_or_reduction_after_overflow_allowed"
        ],
        "candidate_id_rows": rows,
        "claim_boundary": contract["claim_boundary"],
    }


def adapt_native_i64_rows_to_collect_k_bounded_result(
    candidate_rows: Iterable[Any],
    *,
    capacity: int,
    row_width: int,
    backend: str,
    source_symbol: str,
) -> dict[str, Any]:
    """Adapt native row-major i64 candidates to the generic collect-k result.

    This is the Python-side ABI seam used while built Embree/OptiX generic
    collector symbol validation remains pending.
    """
    row_buffer = collect_k_bounded_rows(
        candidate_rows,
        k=int(capacity),
        row_width=int(row_width),
    )
    return {
        **row_buffer,
        "backend": str(backend),
        "native_i64_adapter": True,
        "native_source_symbol": str(source_symbol),
        "source_rows_are_row_major_i64": True,
        "binary_symbol_validation_present": False,
        "claim_boundary": (
            "Python generic i64 adapter over native candidate rows only; "
            "built Embree/OptiX generic symbol validation and stable promotion remain pending."
        ),
    }


def validate_collect_k_bounded_result(
    result: dict[str, Any],
    *,
    row_width: int,
    backend: str | None = None,
) -> dict[str, Any]:
    """Validate and normalize a completed app-generic bounded collection result."""
    if result.get("primitive") != V1_5_1_COLLECT_K_BOUNDED_PRIMITIVE:
        raise ValueError("bounded collection result must use primitive COLLECT_K_BOUNDED")
    if backend is not None and result.get("backend") != backend:
        raise ValueError("bounded collection backend does not match requested backend")
    if result.get("overflowed"):
        raise RuntimeError(
            "COLLECT_K_BOUNDED result reported overflow; "
            f"failure_mode={result.get('failure_mode', 'fail_closed_overflow')}"
        )
    if result.get("complete_candidate_coverage") is not True:
        raise RuntimeError("COLLECT_K_BOUNDED result must report complete candidate coverage")
    if "candidate_id_rows" not in result:
        raise ValueError("bounded collection result must include candidate_id_rows")
    capacity = int(result.get("capacity", result.get("valid_count", 0)))
    normalized = collect_k_bounded_rows(
        result["candidate_id_rows"],
        k=capacity,
        row_width=int(row_width),
    )
    if int(result.get("row_width", row_width)) != int(row_width):
        raise ValueError("COLLECT_K_BOUNDED row_width metadata mismatch")
    if int(result.get("valid_count", normalized["valid_count"])) != normalized["valid_count"]:
        raise ValueError("COLLECT_K_BOUNDED valid_count metadata mismatch")
    if int(result.get("emitted_count", normalized["emitted_count"])) != normalized["emitted_count"]:
        raise ValueError("COLLECT_K_BOUNDED emitted_count metadata mismatch")
    if tuple(result.get("candidate_id_rows", ())) != normalized["candidate_id_rows"]:
        raise ValueError("COLLECT_K_BOUNDED candidate_id_rows must be canonicalized")
    return {
        **result,
        "app_generic": True,
        "result_layout": result.get("result_layout", normalized["result_layout"]),
        "generic_result_layout": result.get(
            "generic_result_layout",
            normalized["result_layout"],
        ),
        "row_dtype": result.get("row_dtype", normalized["row_dtype"]),
        "row_width": int(row_width),
        "capacity": capacity,
        "valid_count": normalized["valid_count"],
        "emitted_count": normalized["emitted_count"],
        "overflowed": False,
        "complete_candidate_coverage": True,
        "ordering_policy": normalized["ordering_policy"],
        "duplicate_policy": normalized["duplicate_policy"],
        "candidate_id_rows": normalized["candidate_id_rows"],
    }
