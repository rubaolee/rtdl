from __future__ import annotations

from pathlib import Path
from typing import Any


V1_6_PYTHON_RTDL_STATUS = "planning_boundary_accepted_not_release_ready"
V1_6_PYTHON_RTDL_TRACK = "python_rtdl"
V1_6_PYTHON_RTDL_HISTORICAL_DEFINITION = (
    "first_historical_python_rtdl_closure_milestone"
)
V1_6_PYTHON_RTDL_SUPPORTED_BACKENDS = ("embree", "optix")
V1_6_PYTHON_RTDL_STABLE_PRIMITIVES = (
    "ANY_HIT",
    "COUNT_HITS",
    "REDUCE_FLOAT(MIN)",
    "REDUCE_FLOAT(MAX)",
    "REDUCE_FLOAT(SUM)",
    "REDUCE_INT(COUNT)",
    "REDUCE_INT(SUM)",
)
V1_6_PYTHON_RTDL_PENDING_PRIMITIVES = ("COLLECT_K_BOUNDED",)
V1_6_PYTHON_RTDL_OUT_OF_SCOPE = (
    "arbitrary_user_python_optimization",
    "whole_application_speedup",
    "sql_engine_behavior",
    "graph_system_analytics",
    "partner_tensor_handoff",
    "true_zero_copy_without_measured_device_path",
    "package_install_support_without_packaging_metadata",
)
V1_6_PYTHON_RTDL_BLOCKED_CLAIMS = (
    "v1_6_release",
    "stable_collect_k_bounded_promotion",
    "public_speedup_wording",
    "whole_app_speedup",
    "broad_rtx_or_gpu_acceleration",
    "true_zero_copy",
    "partner_tensor_handoff",
    "package_install_support",
    "release_tag_action",
)
V1_6_PYTHON_RTDL_REQUIRED_CLOSURE_GATES = (
    "formal_v1_6_release_surface_proposal",
    "public_docs_overclaim_audit",
    "stable_native_path_app_leakage_audit",
    "blocked_claim_regression_tests",
    "windows_linux_source_tree_validation",
    "real_nvidia_optix_validation_for_claimed_surface",
    "three_ai_consensus",
)
V1_6_PYTHON_RTDL_ACCEPTED_READINESS_ARTIFACTS = (
    "docs/reports/goal1599_v1_6_python_rtdl_historical_milestone_readiness_2026-05-09.md",
    "docs/reviews/goal1599_v1_6_readiness_claude_review_2026-05-09.md",
    "docs/reviews/goal1599_v1_6_readiness_gemini_review_2026-05-09.md",
    "docs/reviews/goal1599_v1_6_readiness_3ai_consensus_2026-05-09.md",
)
V1_6_PYTHON_RTDL_ALLOWED_NEXT_ACTIONS = (
    "write_formal_v1_6_release_surface_proposal",
    "audit_public_docs_for_overclaims",
    "audit_native_stable_paths_for_app_leakage",
    "prepare_batched_pod_runbook_after_local_gates",
)


def v1_6_python_rtdl_readiness_gate(*, repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the non-release v1.6 Python+RTDL readiness boundary.

    Passing this gate means the planning boundary is recorded and consensus
    reviewed. It intentionally does not authorize release, public speedup
    wording, true zero-copy wording, partner support, or package-install
    claims.
    """
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    artifact_presence = {
        artifact: (root / artifact).exists()
        for artifact in V1_6_PYTHON_RTDL_ACCEPTED_READINESS_ARTIFACTS
    }
    missing_artifacts = tuple(
        artifact for artifact, present in artifact_presence.items() if not present
    )
    return {
        "status": V1_6_PYTHON_RTDL_STATUS,
        "track": V1_6_PYTHON_RTDL_TRACK,
        "historical_definition": V1_6_PYTHON_RTDL_HISTORICAL_DEFINITION,
        "supported_backends": V1_6_PYTHON_RTDL_SUPPORTED_BACKENDS,
        "stable_primitives": V1_6_PYTHON_RTDL_STABLE_PRIMITIVES,
        "pending_primitives": V1_6_PYTHON_RTDL_PENDING_PRIMITIVES,
        "out_of_scope": V1_6_PYTHON_RTDL_OUT_OF_SCOPE,
        "required_closure_gates": V1_6_PYTHON_RTDL_REQUIRED_CLOSURE_GATES,
        "accepted_readiness_artifacts": V1_6_PYTHON_RTDL_ACCEPTED_READINESS_ARTIFACTS,
        "artifact_presence": artifact_presence,
        "missing_artifacts": missing_artifacts,
        "allowed_next_actions": V1_6_PYTHON_RTDL_ALLOWED_NEXT_ACTIONS,
        "release_ready": False,
        "public_release_authorized": False,
        "release_tag_action_authorized": False,
        "stable_collect_k_bounded_promotion_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rtx_or_gpu_acceleration_claim_authorized": False,
        "true_zero_copy_wording_authorized": False,
        "partner_tensor_handoff_authorized": False,
        "package_install_support_authorized": False,
        "blocked_claims": V1_6_PYTHON_RTDL_BLOCKED_CLAIMS,
        "claim_boundary": (
            "v1.6 is the planned first historical Python+RTDL closure "
            "milestone. Current main is not release-ready. The accepted "
            "boundary is RTDL-managed RT primitives and the Python/native "
            "bridge only; arbitrary user Python optimization, whole-app "
            "speedup, broad RTX/GPU acceleration, true zero-copy, partner "
            "tensor handoff, package-install support, and release action "
            "remain blocked until separate reviewed gates close."
        ),
    }


def validate_v1_6_python_rtdl_readiness_gate(
    *, repo_root: str | Path | None = None
) -> dict[str, Any]:
    gate = v1_6_python_rtdl_readiness_gate(repo_root=repo_root)
    if gate["status"] != V1_6_PYTHON_RTDL_STATUS:
        raise ValueError("invalid v1.6 Python+RTDL readiness status")
    if gate["track"] != V1_6_PYTHON_RTDL_TRACK:
        raise ValueError("v1.6 readiness gate must stay on Python+RTDL track")
    if tuple(gate["supported_backends"]) != V1_6_PYTHON_RTDL_SUPPORTED_BACKENDS:
        raise ValueError("v1.6 readiness gate must stay scoped to Embree and OptiX")
    if tuple(gate["stable_primitives"]) != V1_6_PYTHON_RTDL_STABLE_PRIMITIVES:
        raise ValueError("v1.6 stable primitive boundary changed")
    if tuple(gate["pending_primitives"]) != V1_6_PYTHON_RTDL_PENDING_PRIMITIVES:
        raise ValueError("v1.6 pending primitive boundary changed")
    if "COLLECT_K_BOUNDED" in tuple(gate["stable_primitives"]):
        raise ValueError("COLLECT_K_BOUNDED must not be stable in this readiness gate")
    if tuple(gate["out_of_scope"]) != V1_6_PYTHON_RTDL_OUT_OF_SCOPE:
        raise ValueError("v1.6 out-of-scope list changed")
    if tuple(gate["blocked_claims"]) != V1_6_PYTHON_RTDL_BLOCKED_CLAIMS:
        raise ValueError("v1.6 blocked claims changed")
    if tuple(gate["required_closure_gates"]) != V1_6_PYTHON_RTDL_REQUIRED_CLOSURE_GATES:
        raise ValueError("v1.6 required closure gates changed")
    if tuple(gate["allowed_next_actions"]) != V1_6_PYTHON_RTDL_ALLOWED_NEXT_ACTIONS:
        raise ValueError("v1.6 allowed next actions changed")
    if tuple(gate["missing_artifacts"]) != ():
        raise ValueError("v1.6 readiness artifacts are missing")
    for flag in (
        "release_ready",
        "public_release_authorized",
        "release_tag_action_authorized",
        "stable_collect_k_bounded_promotion_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "broad_rtx_or_gpu_acceleration_claim_authorized",
        "true_zero_copy_wording_authorized",
        "partner_tensor_handoff_authorized",
        "package_install_support_authorized",
    ):
        if gate[flag] is not False:
            raise ValueError(f"v1.6 readiness gate must keep {flag}=False")
    boundary = str(gate["claim_boundary"])
    for phrase in (
        "not release-ready",
        "RTDL-managed RT primitives",
        "arbitrary user Python optimization",
        "whole-app speedup",
        "broad RTX/GPU acceleration",
        "true zero-copy",
        "partner tensor handoff",
        "package-install support",
        "release action",
        "separate reviewed gates",
    ):
        if phrase not in boundary:
            raise ValueError("v1.6 readiness claim boundary is incomplete")
    return gate
