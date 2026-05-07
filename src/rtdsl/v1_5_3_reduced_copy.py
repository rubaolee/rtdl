from __future__ import annotations

from typing import Any


V1_5_3_REDUCED_COPY_STATUS = "contract_defined_implementation_pending"
V1_5_3_REDUCED_COPY_TRACK = "python_rtdl"
V1_5_3_REDUCED_COPY_SCOPE = (
    "typed_contiguous_host_buffers",
    "preallocated_result_buffers",
    "prepared_host_buffer_reuse",
    "prepared_device_or_staging_buffer_reuse",
)
V1_5_3_REDUCED_COPY_REQUIRED_EVIDENCE = (
    "python_materialized_rows_baseline",
    "typed_contiguous_host_buffer_path",
    "preallocated_result_buffer_reuse_path",
    "copy_count_or_transfer_count_measurement",
    "embree_optix_same_contract_parity_where_claimed",
    "external_ai_review_before_public_claims",
)
V1_5_3_REDUCED_COPY_SATISFIED_EVIDENCE = (
    "python_materialized_rows_baseline",
    "preallocated_result_buffer_reuse_path",
)
V1_5_3_REDUCED_COPY_MISSING_EVIDENCE = tuple(
    item
    for item in V1_5_3_REDUCED_COPY_REQUIRED_EVIDENCE
    if item not in V1_5_3_REDUCED_COPY_SATISFIED_EVIDENCE
)
V1_5_3_REDUCED_COPY_BLOCKED_CLAIMS = (
    "true_zero_copy",
    "public_speedup",
    "whole_app_speedup",
    "stable_public_primitive",
    "release_action",
)
V1_5_3_REDUCED_COPY_ALLOWED_WORDING = (
    "reduced-copy candidate",
    "reduced-transfer candidate",
    "prepared host-buffer reuse",
    "typed contiguous host-buffer path",
)
V1_5_3_REDUCED_COPY_FORBIDDEN_WORDING = (
    "true zero-copy",
    "zero-copy speedup",
    "whole-app acceleration",
    "public speedup",
    "release-ready",
)


def v1_5_3_reduced_copy_contract() -> dict[str, Any]:
    """Return the v1.5.3 reduced-copy contract for Python+RTDL buffers."""
    return {
        "status": V1_5_3_REDUCED_COPY_STATUS,
        "track": V1_5_3_REDUCED_COPY_TRACK,
        "scope": V1_5_3_REDUCED_COPY_SCOPE,
        "required_evidence": V1_5_3_REDUCED_COPY_REQUIRED_EVIDENCE,
        "satisfied_evidence": V1_5_3_REDUCED_COPY_SATISFIED_EVIDENCE,
        "missing_evidence": V1_5_3_REDUCED_COPY_MISSING_EVIDENCE,
        "blocked_claims": V1_5_3_REDUCED_COPY_BLOCKED_CLAIMS,
        "allowed_wording": V1_5_3_REDUCED_COPY_ALLOWED_WORDING,
        "forbidden_wording": V1_5_3_REDUCED_COPY_FORBIDDEN_WORDING,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "next_implementation_lanes": (
            "add typed contiguous host input/output adapters for collect rows",
            "measure copy count against python materialized row baselines",
            "separate host reduced-copy wording from device zero-copy wording",
            "only add OptiX device/staging reuse claims after measured RTX evidence",
        ),
        "claim_boundary": (
            "v1.5.3 begins the reduced-copy lane for Python+RTDL buffer "
            "plumbing. It may describe reduced-copy or reduced-transfer "
            "candidates only after measured copy-count evidence. It does not "
            "authorize true zero-copy, public speedup wording, whole-app "
            "claims, stable primitive promotion, partner tensor handoff, or "
            "release action."
        ),
    }


def validate_v1_5_3_reduced_copy_contract() -> dict[str, Any]:
    contract = v1_5_3_reduced_copy_contract()
    if contract["status"] != V1_5_3_REDUCED_COPY_STATUS:
        raise ValueError("invalid v1.5.3 reduced-copy status")
    if contract["track"] != V1_5_3_REDUCED_COPY_TRACK:
        raise ValueError("invalid v1.5.3 reduced-copy track")
    if tuple(contract["required_evidence"]) != V1_5_3_REDUCED_COPY_REQUIRED_EVIDENCE:
        raise ValueError("v1.5.3 reduced-copy required evidence changed")
    if tuple(contract["satisfied_evidence"]) != V1_5_3_REDUCED_COPY_SATISFIED_EVIDENCE:
        raise ValueError("v1.5.3 reduced-copy satisfied evidence changed")
    if tuple(contract["missing_evidence"]) != V1_5_3_REDUCED_COPY_MISSING_EVIDENCE:
        raise ValueError("v1.5.3 reduced-copy missing evidence changed")
    for flag in (
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "release_action_authorized",
    ):
        if contract[flag] is not False:
            raise ValueError(f"v1.5.3 reduced-copy contract must keep {flag}=False")
    for phrase in (
        "reduced-copy lane",
        "measured copy-count evidence",
        "does not authorize true zero-copy",
        "public speedup wording",
        "whole-app claims",
        "release action",
    ):
        if phrase not in contract["claim_boundary"]:
            raise ValueError("v1.5.3 reduced-copy claim boundary is incomplete")
    return contract
